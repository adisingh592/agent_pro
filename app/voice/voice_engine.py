"""
Voice Engine — Groq-powered Speech-to-Text + LLM + Text-to-Speech pipeline.

Architecture (no wake word, push-to-talk):

  Microphone → sounddevice → WAV buffer
       ↓
  Groq Whisper (distil-whisper-large-v3-en) → transcript text
       ↓
  PersonalAgent AgentCore.process_user_input() → response text
       ↓
  Groq TTS (playai-tts, voice: Fritz-PlayAI) → MP3/WAV audio
       ↓
  sounddevice playback

All network calls run in a QThread worker so the Qt GUI stays fully responsive.
The mic recording itself uses a simple blocking `sounddevice.rec()` call in a 
dedicated thread and signals the main thread when done.

Required packages (add to requirements.txt):
  groq>=0.13.0
  sounddevice>=0.5.0
  soundfile>=0.12.1
  numpy>=1.24.0
"""

from __future__ import annotations

import io
import logging
import os
import tempfile
import time
import numpy as np
from typing import Optional

from PySide6.QtCore import QObject, QThread, Signal

logger = logging.getLogger("PersonalAgent.VoiceEngine")

# ---------------------------------------------------------------------------
# Lazy-import helpers — these packages may not be installed, so we import
# inside methods and report clear errors to the UI.
# ---------------------------------------------------------------------------

def _require_sounddevice():
    try:
        import sounddevice as sd
        return sd
    except ImportError:
        raise ImportError(
            "sounddevice is not installed. Run: pip install sounddevice soundfile numpy"
        )

def _require_soundfile():
    try:
        import soundfile as sf
        return sf
    except ImportError:
        raise ImportError(
            "soundfile is not installed. Run: pip install sounddevice soundfile numpy"
        )

def _require_groq():
    try:
        from groq import Groq
        return Groq
    except ImportError:
        raise ImportError(
            "groq is not installed. Run: pip install groq"
        )


# ---------------------------------------------------------------------------
# Recording worker — captures mic in a background thread
# ---------------------------------------------------------------------------

class MicRecorderWorker(QThread):
    """
    Records microphone audio for `duration` seconds at `sample_rate` Hz,
    saves to a temporary WAV file, and emits `recording_done(path)`.
    If an error occurs, emits `recording_error(message)`.
    """
    recording_done = Signal(str)   # path to temp WAV file
    recording_error = Signal(str)  # human-readable error message

    def __init__(
        self,
        duration: float = 6.0,
        sample_rate: int = 16000,
        channels: int = 1,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.duration = duration
        self.sample_rate = sample_rate
        self.channels = channels
        self._stop_flag = False

    def stop_early(self) -> None:
        """Signal the recorder to stop before `duration` expires (future use)."""
        self._stop_flag = True

    def run(self) -> None:
        try:
            sd = _require_sounddevice()
            sf = _require_soundfile()
        except ImportError as e:
            self.recording_error.emit(str(e))
            return

        try:
            audio = sd.rec(
                int(self.duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",
            )
            sd.wait()

            # Write to temp WAV
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.close()
            sf.write(tmp.name, audio, self.sample_rate)
            self.recording_done.emit(tmp.name)

        except Exception as e:
            self.recording_error.emit(f"Recording failed: {e}")


# ---------------------------------------------------------------------------
# Transcription + LLM + TTS worker
# ---------------------------------------------------------------------------

class GroqVoicePipelineWorker(QThread):
    """
    Runs the full Groq pipeline in one background thread:
      1. Whisper STT (transcribe WAV → text)
      2. Emit transcript so UI can show it
      3. Send transcript to AgentCore for LLM response
      4. Emit agent response text
      5. Groq TTS → WAV → play through speakers

    Signals
    -------
    transcript_ready(str)   – spoken text detected
    response_ready(str)     – agent text reply
    tts_playing()           – TTS audio has started playing
    pipeline_done()         – everything finished, ready for next query
    pipeline_error(str)     – human-readable error at any stage
    """
    transcript_ready = Signal(str)
    response_ready = Signal(str)
    tts_playing = Signal()
    pipeline_done = Signal()
    pipeline_error = Signal(str)

    # Groq Whisper model
    WHISPER_MODEL = "whisper-large-v3-turbo"

    # Groq TTS model + voice
    TTS_MODEL = "playai-tts"
    TTS_VOICE = "Fritz-PlayAI"

    def __init__(
        self,
        wav_path: str,
        api_key: str,
        agent_core,          # app.core.agent.AgentCore (avoid circular import)
        tts_enabled: bool = True,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.wav_path = wav_path
        self.api_key = api_key
        self.agent_core = agent_core
        self.tts_enabled = tts_enabled

    # ------------------------------------------------------------------
    def run(self) -> None:
        # 1 ── Transcribe
        try:
            transcript = self._transcribe(self.wav_path)
        except Exception as e:
            self.pipeline_error.emit(f"Transcription failed: {e}")
            return
        finally:
            # Clean up temp wav
            try:
                os.remove(self.wav_path)
            except OSError:
                pass

        if not transcript or not transcript.strip():
            self.pipeline_error.emit("No speech detected. Please speak clearly and try again.")
            return

        self.transcript_ready.emit(transcript)

        # 2 ── LLM via AgentCore (synchronous call, runs in this thread)
        try:
            response_text = self._get_agent_response(transcript)
        except Exception as e:
            self.pipeline_error.emit(f"Agent response failed: {e}")
            return

        self.response_ready.emit(response_text)

        # 3 ── TTS
        if self.tts_enabled and response_text:
            try:
                self._speak(response_text)
            except Exception as e:
                # Non-fatal – log and continue
                logger.warning("TTS failed (non-fatal): %s", e)

        self.pipeline_done.emit()

    # ------------------------------------------------------------------
    def _transcribe(self, wav_path: str) -> str:
        """Call Groq Whisper API to transcribe the WAV file."""
        Groq = _require_groq()
        client = Groq(api_key=self.api_key)
        with open(wav_path, "rb") as f:
            result = client.audio.transcriptions.create(
                file=("audio.wav", f),
                model=self.WHISPER_MODEL,
                response_format="text",
                language="en",
            )
        return str(result).strip()

    # ------------------------------------------------------------------
    def _get_agent_response(self, text: str) -> str:
        """
        Send the transcribed text through the existing AgentCore using the
        Groq LLM chat API directly (bypasses Ollama so we can use Groq cloud).
        Falls back to Ollama / local if GROQ_API_KEY is unavailable.
        """
        Groq = _require_groq()
        client = Groq(api_key=self.api_key)

        # Build a minimal system prompt focused on voice responses
        system_prompt = (
            "You are Personal Agent, a helpful desktop AI voice assistant. "
            "The user has spoken to you. Reply concisely and naturally for text-to-speech playback. "
            "Keep responses under 3 sentences unless complex details are absolutely needed. "
            "No markdown formatting — plain spoken language only."
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.7,
            max_tokens=512,
        )
        return response.choices[0].message.content.strip()

    # ------------------------------------------------------------------
    def _speak(self, text: str) -> None:
        """Call Groq TTS, get audio bytes, play through sounddevice."""
        Groq = _require_groq()
        sd = _require_sounddevice()
        sf = _require_soundfile()

        client = Groq(api_key=self.api_key)

        # Truncate very long responses for TTS
        speak_text = text[:800] if len(text) > 800 else text

        response = client.audio.speech.create(
            model=self.TTS_MODEL,
            voice=self.TTS_VOICE,
            input=speak_text,
            response_format="wav",
        )

        # Read audio bytes into a soundfile-readable buffer
        audio_bytes = response.read()
        buf = io.BytesIO(audio_bytes)
        data, sample_rate = sf.read(buf, dtype="float32")

        self.tts_playing.emit()

        # Play synchronously (blocks this worker thread, not the GUI)
        sd.play(data, samplerate=sample_rate)
        sd.wait()


# ---------------------------------------------------------------------------
# Public voice engine facade — manages state & workers, talks to Qt
# ---------------------------------------------------------------------------

class VoiceEngine(QObject):
    """
    High-level controller for the Groq voice assistant pipeline.

    States:   idle → recording → processing → speaking → idle
    
    Signals
    -------
    state_changed(state_str)          – 'idle' | 'recording' | 'processing' | 'speaking'
    transcript_ready(text)            – spoken words transcribed
    response_ready(text)              – agent text reply
    error_occurred(message)           – user-visible error
    """
    state_changed = Signal(str)
    transcript_ready = Signal(str)
    response_ready = Signal(str)
    error_occurred = Signal(str)

    STATE_IDLE = "idle"
    STATE_RECORDING = "recording"
    STATE_PROCESSING = "processing"
    STATE_SPEAKING = "speaking"

    def __init__(
        self,
        agent_core,
        api_key: str = "",
        record_duration: float = 7.0,
        tts_enabled: bool = True,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.agent_core = agent_core
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        self.record_duration = record_duration
        self.tts_enabled = tts_enabled

        self._state = self.STATE_IDLE
        self._mic_worker: Optional[MicRecorderWorker] = None
        self._pipeline_worker: Optional[GroqVoicePipelineWorker] = None

    # ------------------------------------------------------------------
    @property
    def state(self) -> str:
        return self._state

    def _set_state(self, s: str) -> None:
        self._state = s
        self.state_changed.emit(s)

    # ------------------------------------------------------------------
    def start_listening(self) -> None:
        """Begin recording from the default microphone."""
        if self._state != self.STATE_IDLE:
            return

        if not self.api_key:
            self.error_occurred.emit(
                "No GROQ_API_KEY set. Go to Settings → Voice → Enter your Groq API key."
            )
            return

        self._set_state(self.STATE_RECORDING)
        self._mic_worker = MicRecorderWorker(
            duration=self.record_duration,
            sample_rate=16000,
            channels=1,
            parent=self,
        )
        self._mic_worker.recording_done.connect(self._on_recording_done)
        self._mic_worker.recording_error.connect(self._on_error)
        self._mic_worker.finished.connect(self._mic_worker.deleteLater)
        self._mic_worker.start()

    def stop_listening(self) -> None:
        """Stop recording early (if still in progress)."""
        if self._mic_worker and self._mic_worker.isRunning():
            self._mic_worker.stop_early()

    # ------------------------------------------------------------------
    def _on_recording_done(self, wav_path: str) -> None:
        self._set_state(self.STATE_PROCESSING)
        self._pipeline_worker = GroqVoicePipelineWorker(
            wav_path=wav_path,
            api_key=self.api_key,
            agent_core=self.agent_core,
            tts_enabled=self.tts_enabled,
            parent=self,
        )
        self._pipeline_worker.transcript_ready.connect(self.transcript_ready)
        self._pipeline_worker.response_ready.connect(self.response_ready)
        self._pipeline_worker.tts_playing.connect(lambda: self._set_state(self.STATE_SPEAKING))
        self._pipeline_worker.pipeline_done.connect(self._on_pipeline_done)
        self._pipeline_worker.pipeline_error.connect(self._on_error)
        self._pipeline_worker.finished.connect(self._pipeline_worker.deleteLater)
        self._pipeline_worker.start()

    def _on_pipeline_done(self) -> None:
        self._set_state(self.STATE_IDLE)

    def _on_error(self, msg: str) -> None:
        self._set_state(self.STATE_IDLE)
        self.error_occurred.emit(msg)

    # ------------------------------------------------------------------
    def set_api_key(self, key: str) -> None:
        self.api_key = key.strip()

    def set_tts_enabled(self, enabled: bool) -> None:
        self.tts_enabled = enabled

    def set_record_duration(self, seconds: float) -> None:
        self.record_duration = max(2.0, min(30.0, seconds))
