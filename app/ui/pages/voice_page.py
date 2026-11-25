"""
Voice Assistant Page — Groq-powered push-to-talk voice interface.

Pipeline:
  [🎙 Hold to Speak] → sounddevice mic → Groq Whisper STT → Groq LLaMA-3 LLM
                     → Groq PlayAI TTS → sounddevice speaker output

No wake word needed. Push-to-talk only.
"""
from __future__ import annotations

import os
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QCheckBox, QScrollArea, QSizePolicy,
    QSlider, QSpinBox,
)

from ...voice.voice_engine import VoiceEngine
from ...core.agent import AgentCore


# ---------------------------------------------------------------------------
# Animated waveform label (ASCII bars cycling while recording)
# ---------------------------------------------------------------------------
_WAVE_IDLE    = "  ▂  ▂  ▂  ▂  ▂  ▂  ▂  ▂  ▂  ▂  "
_WAVE_FRAMES = [
    "  ▂ ▃ ▅ ▇ █ ▇ ▅ ▃ ▂ ▂ ▃ ▅ ▇ █  ",
    "  ▅ ▇ █ ▇ ▅ ▃ ▂ ▃ ▅ ▇ █ ▇ ▅ ▃  ",
    "  █ ▇ ▅ ▃ ▂ ▃ ▅ ▇ █ ▇ ▅ ▃ ▂ ▃  ",
    "  ▇ ▅ ▃ ▂ ▃ ▅ ▇ █ ▇ ▅ ▃ ▂ ▃ ▅  ",
    "  ▅ ▃ ▂ ▃ ▅ ▇ █ ▇ ▅ ▃ ▂ ▃ ▅ ▇  ",
    "  ▃ ▂ ▃ ▅ ▇ █ ▇ ▅ ▃ ▂ ▃ ▅ ▇ █  ",
]
_WAVE_PROC = "  ⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏  processing..."
_WAVE_SPEAK = "  ◈ ◈ ◈  speaking  ◈ ◈ ◈  "


class ConversationBubble(QFrame):
    """A single voice conversation turn (user transcript or agent reply)."""

    def __init__(self, speaker: str, text: str, is_user: bool = True):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        if is_user:
            self.setStyleSheet("""
                ConversationBubble {
                    background: transparent;
                    border: none;
                }
            """)
            speaker_lbl = QLabel(f"🎙 {speaker}")
            speaker_lbl.setStyleSheet("color: #e59840; font-size: 12px; font-weight: 700;")
        else:
            self.setStyleSheet("""
                ConversationBubble {
                    background-color: #22242a;
                    border: 1px solid #2c2f38;
                    border-radius: 8px;
                }
            """)
            speaker_lbl = QLabel(f"🤖 {speaker}")
            speaker_lbl.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: 700;")

        text_lbl = QLabel(text)
        text_lbl.setWordWrap(True)
        text_lbl.setStyleSheet("color: #d1d5db; font-size: 13px; line-height: 1.5;")

        layout.addWidget(speaker_lbl)
        layout.addWidget(text_lbl)


class VoicePage(QWidget):
    """
    Full Groq-based voice assistant dashboard.

    Layout:
      ┌─────────────────────────────────────────────────────┐
      │  Header: Voice Assistant (Groq)                     │
      ├─────────────────────────────────────────────────────┤
      │  Status Badge  │  State label                       │
      │             [Animated waveform]                     │
      │                                                     │
      │             [🎙 Hold to Speak  / ⏹ Stop]           │
      ├─────────────────────────────────────────────────────┤
      │  Conversation history (scrollable)                  │
      ├─────────────────────────────────────────────────────┤
      │  Settings: API key · TTS on/off · Duration          │
      └─────────────────────────────────────────────────────┘
    """

    def __init__(self, agent_core: AgentCore):
        super().__init__()
        self.agent_core = agent_core

        # Build voice engine (API key loaded from env or entered in settings)
        self._api_key = os.environ.get("GROQ_API_KEY", "")
        self.voice_engine = VoiceEngine(
            agent_core=self.agent_core,
            api_key=self._api_key,
        )

        # Animation timer
        self._wave_frame = 0
        self._wave_timer = QTimer(self)
        self._wave_timer.timeout.connect(self._animate_wave)

        self._init_ui()
        self._connect_engine()

    # ------------------------------------------------------------------
    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(16)

        # ── Header ──
        header_col = QVBoxLayout()
        header_col.setSpacing(4)
        title = QLabel("Voice Assistant")
        title.setProperty("class", "pageTitle")
        subtitle = QLabel(
            "Groq-powered push-to-talk · Whisper STT · LLaMA-3.3-70B · PlayAI TTS"
        )
        subtitle.setProperty("class", "pageSubtitle")
        header_col.addWidget(title)
        header_col.addWidget(subtitle)
        root.addLayout(header_col)

        # ── Main interaction card ──
        main_card = QFrame()
        main_card.setProperty("class", "surfaceCard")
        mc_layout = QVBoxLayout(main_card)
        mc_layout.setContentsMargins(28, 28, 28, 28)
        mc_layout.setSpacing(18)
        mc_layout.setAlignment(Qt.AlignCenter)

        # Status row: coloured badge + state text
        status_row = QHBoxLayout()
        status_row.setAlignment(Qt.AlignCenter)
        status_row.setSpacing(10)

        self._status_badge = QLabel("● IDLE")
        self._status_badge.setStyleSheet(
            "color: #6b7280; font-size: 11px; font-weight: 700; "
            "letter-spacing: 0.08em; padding: 3px 10px; "
            "border-radius: 10px; background: #1c1e24; border: 1px solid #2c2f38;"
        )

        self._state_label = QLabel("Ready — press the button below to speak")
        self._state_label.setStyleSheet("color: #8e929b; font-size: 13px;")
        self._state_label.setAlignment(Qt.AlignCenter)

        status_row.addWidget(self._status_badge)
        status_row.addWidget(self._state_label)
        mc_layout.addLayout(status_row)

        # Waveform visualiser
        self._wave_label = QLabel(_WAVE_IDLE)
        self._wave_label.setStyleSheet(
            "color: #2c2f38; font-size: 22px; letter-spacing: 2px; font-family: monospace;"
        )
        self._wave_label.setAlignment(Qt.AlignCenter)
        mc_layout.addWidget(self._wave_label)

        # Duration counter label (shows countdown while recording)
        self._timer_label = QLabel("")
        self._timer_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        self._timer_label.setAlignment(Qt.AlignCenter)
        mc_layout.addWidget(self._timer_label)

        # Push-to-talk button
        self._ptt_btn = QPushButton("🎙  Speak to Agent")
        self._ptt_btn.setProperty("class", "primaryButton")
        self._ptt_btn.setMinimumHeight(52)
        self._ptt_btn.setFixedWidth(240)
        self._ptt_btn.setCursor(Qt.PointingHandCursor)
        self._ptt_btn.setStyleSheet("""
            QPushButton {
                background-color: #e59840;
                border: none;
                border-radius: 10px;
                color: #131417;
                font-size: 15px;
                font-weight: 700;
                letter-spacing: 0.03em;
            }
            QPushButton:hover { background-color: #f0a34b; }
            QPushButton:pressed { background-color: #c98030; }
            QPushButton:disabled { background-color: #2c2f38; color: #6b7280; }
        """)
        self._ptt_btn.clicked.connect(self._on_ptt_clicked)
        mc_layout.addWidget(self._ptt_btn, alignment=Qt.AlignCenter)

        root.addWidget(main_card)

        # ── Conversation history ──
        conv_card = QFrame()
        conv_card.setProperty("class", "surfaceCard")
        conv_layout = QVBoxLayout(conv_card)
        conv_layout.setContentsMargins(16, 16, 16, 16)
        conv_layout.setSpacing(8)

        conv_title_row = QHBoxLayout()
        conv_title = QLabel("CONVERSATION")
        conv_title.setStyleSheet(
            "color: #ffffff; font-size: 11px; font-weight: 700; letter-spacing: 0.08em;"
        )
        clear_btn = QPushButton("🗑 Clear")
        clear_btn.setProperty("class", "secondaryButton")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self._clear_history)
        conv_title_row.addWidget(conv_title)
        conv_title_row.addStretch()
        conv_title_row.addWidget(clear_btn)
        conv_layout.addLayout(conv_title_row)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("background: transparent; border: none;")
        self._scroll.setMinimumHeight(140)
        self._scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._conv_container = QWidget()
        self._conv_container.setStyleSheet("background: transparent;")
        self._conv_col = QVBoxLayout(self._conv_container)
        self._conv_col.setContentsMargins(2, 2, 2, 2)
        self._conv_col.setSpacing(10)
        self._conv_col.addStretch()

        self._scroll.setWidget(self._conv_container)
        conv_layout.addWidget(self._scroll, 1)

        root.addWidget(conv_card, 1)

        # ── Settings card ──
        settings_card = QFrame()
        settings_card.setProperty("class", "surfaceCard")
        sc = QVBoxLayout(settings_card)
        sc.setContentsMargins(20, 18, 20, 18)
        sc.setSpacing(12)

        sec_lbl = QLabel("VOICE SETTINGS")
        sec_lbl.setStyleSheet(
            "color: #ffffff; font-size: 11px; font-weight: 700; letter-spacing: 0.08em;"
        )
        sc.addWidget(sec_lbl)

        # Groq API key
        key_row = QHBoxLayout()
        key_lbl = QLabel("Groq API Key:")
        key_lbl.setStyleSheet("color: #8e929b; font-size: 13px; min-width: 120px;")
        self._key_input = QLineEdit()
        self._key_input.setPlaceholderText("gsk_xxxxxxxxxxxxxxxxxxxx")
        self._key_input.setEchoMode(QLineEdit.Password)
        self._key_input.setText(self._api_key)
        self._key_input.setStyleSheet("""
            QLineEdit {
                background-color: #1c1e24;
                border: 1px solid #2c2f38;
                border-radius: 4px;
                color: #ffffff;
                padding: 5px 10px;
                font-size: 12px;
                font-family: monospace;
            }
            QLineEdit:focus { border-color: #e59840; }
        """)
        self._key_input.textChanged.connect(self._on_api_key_changed)
        key_row.addWidget(key_lbl)
        key_row.addWidget(self._key_input, 1)

        # Show/hide toggle
        show_key_btn = QPushButton("👁")
        show_key_btn.setFixedWidth(32)
        show_key_btn.setStyleSheet("background: transparent; border: none; color: #8e929b; font-size: 14px;")
        show_key_btn.clicked.connect(self._toggle_key_echo)
        key_row.addWidget(show_key_btn)
        sc.addLayout(key_row)

        # TTS + Duration row
        opts_row = QHBoxLayout()
        opts_row.setSpacing(24)

        self._tts_check = QCheckBox("Enable Text-to-Speech (PlayAI Fritz)")
        self._tts_check.setChecked(True)
        self._tts_check.setStyleSheet("color: #d1d5db; font-size: 13px;")
        self._tts_check.toggled.connect(self.voice_engine.set_tts_enabled)
        opts_row.addWidget(self._tts_check)

        dur_lbl = QLabel("Recording duration:")
        dur_lbl.setStyleSheet("color: #8e929b; font-size: 13px;")
        self._dur_spin = QSpinBox()
        self._dur_spin.setRange(2, 30)
        self._dur_spin.setValue(7)
        self._dur_spin.setSuffix(" s")
        self._dur_spin.setStyleSheet("""
            QSpinBox {
                background: #1c1e24;
                border: 1px solid #2c2f38;
                border-radius: 4px;
                color: #fff;
                padding: 3px 6px;
                font-size: 12px;
            }
        """)
        self._dur_spin.valueChanged.connect(
            lambda v: self.voice_engine.set_record_duration(float(v))
        )
        opts_row.addWidget(dur_lbl)
        opts_row.addWidget(self._dur_spin)
        opts_row.addStretch()
        sc.addLayout(opts_row)

        # Groq model info line
        info = QLabel(
            "STT: whisper-large-v3-turbo  ·  LLM: llama-3.3-70b-versatile  ·  TTS: playai-tts (Fritz-PlayAI)"
        )
        info.setStyleSheet("color: #4b5563; font-size: 11px; font-family: monospace;")
        sc.addWidget(info)

        root.addWidget(settings_card)

    # ------------------------------------------------------------------
    def _connect_engine(self) -> None:
        self.voice_engine.state_changed.connect(self._on_state_changed)
        self.voice_engine.transcript_ready.connect(self._on_transcript)
        self.voice_engine.response_ready.connect(self._on_response)
        self.voice_engine.error_occurred.connect(self._on_error)

    # ------------------------------------------------------------------
    # UI state machine
    # ------------------------------------------------------------------
    def _on_state_changed(self, state: str) -> None:
        if state == VoiceEngine.STATE_IDLE:
            self._wave_timer.stop()
            self._wave_label.setText(_WAVE_IDLE)
            self._wave_label.setStyleSheet(
                "color: #2c2f38; font-size: 22px; letter-spacing: 2px; font-family: monospace;"
            )
            self._status_badge.setText("● IDLE")
            self._status_badge.setStyleSheet(
                "color: #6b7280; font-size: 11px; font-weight: 700; "
                "letter-spacing: 0.08em; padding: 3px 10px; "
                "border-radius: 10px; background: #1c1e24; border: 1px solid #2c2f38;"
            )
            self._state_label.setText("Ready — press the button below to speak")
            self._ptt_btn.setText("🎙  Speak to Agent")
            self._ptt_btn.setEnabled(True)
            self._timer_label.setText("")

        elif state == VoiceEngine.STATE_RECORDING:
            self._wave_frame = 0
            self._wave_timer.start(120)
            self._wave_label.setStyleSheet(
                "color: #ef4444; font-size: 22px; letter-spacing: 2px; font-family: monospace;"
            )
            self._status_badge.setText("● RECORDING")
            self._status_badge.setStyleSheet(
                "color: #ef4444; font-size: 11px; font-weight: 700; "
                "letter-spacing: 0.08em; padding: 3px 10px; "
                "border-radius: 10px; background: #2b1d1f; border: 1px solid #5a272b;"
            )
            self._state_label.setText("Listening… speak now")
            self._ptt_btn.setText("⏹  Stop Recording")
            # Start countdown
            dur = self._dur_spin.value()
            self._countdown_ms = dur * 1000
            self._countdown_timer = QTimer(self)
            self._countdown_timer.setInterval(200)
            self._countdown_timer.timeout.connect(self._tick_countdown)
            self._countdown_timer.start()

        elif state == VoiceEngine.STATE_PROCESSING:
            self._wave_timer.stop()
            if hasattr(self, "_countdown_timer"):
                self._countdown_timer.stop()
            self._wave_label.setText(_WAVE_PROC)
            self._wave_label.setStyleSheet(
                "color: #e59840; font-size: 18px; letter-spacing: 1px; font-family: monospace;"
            )
            self._status_badge.setText("● PROCESSING")
            self._status_badge.setStyleSheet(
                "color: #e59840; font-size: 11px; font-weight: 700; "
                "letter-spacing: 0.08em; padding: 3px 10px; "
                "border-radius: 10px; background: #1f1d17; border: 1px solid #4a3318;"
            )
            self._state_label.setText("Transcribing + thinking…")
            self._ptt_btn.setText("⌛  Processing…")
            self._ptt_btn.setEnabled(False)
            self._timer_label.setText("")

        elif state == VoiceEngine.STATE_SPEAKING:
            self._wave_label.setText(_WAVE_SPEAK)
            self._wave_label.setStyleSheet(
                "color: #9BE34A; font-size: 20px; letter-spacing: 2px; font-family: monospace;"
            )
            self._status_badge.setText("● SPEAKING")
            self._status_badge.setStyleSheet(
                "color: #9BE34A; font-size: 11px; font-weight: 700; "
                "letter-spacing: 0.08em; padding: 3px 10px; "
                "border-radius: 10px; background: #131f10; border: 1px solid #2c5022;"
            )
            self._state_label.setText("Agent is speaking…")
            self._ptt_btn.setText("🔊  Speaking…")

    def _animate_wave(self) -> None:
        self._wave_label.setText(_WAVE_FRAMES[self._wave_frame % len(_WAVE_FRAMES)])
        self._wave_frame += 1

    def _tick_countdown(self) -> None:
        self._countdown_ms -= 200
        if self._countdown_ms <= 0:
            self._countdown_timer.stop()
            self._timer_label.setText("")
        else:
            secs = self._countdown_ms / 1000
            self._timer_label.setText(f"Recording: {secs:.1f}s remaining")

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def _on_ptt_clicked(self) -> None:
        state = self.voice_engine.state
        if state == VoiceEngine.STATE_IDLE:
            self.voice_engine.start_listening()
        elif state == VoiceEngine.STATE_RECORDING:
            self.voice_engine.stop_listening()

    def _on_transcript(self, text: str) -> None:
        bubble = ConversationBubble("You (voice)", text, is_user=True)
        self._insert_bubble(bubble)

    def _on_response(self, text: str) -> None:
        bubble = ConversationBubble("Personal Agent", text, is_user=False)
        self._insert_bubble(bubble)

    def _on_error(self, msg: str) -> None:
        err_lbl = QLabel(f"⚠ {msg}")
        err_lbl.setWordWrap(True)
        err_lbl.setStyleSheet(
            "color: #fca5a5; font-size: 12px; padding: 8px 12px; "
            "background: #2b1d1f; border-radius: 6px; border: 1px solid #5a272b;"
        )
        self._insert_bubble(err_lbl)
        self._state_label.setText(f"Error: {msg[:80]}")

    def _insert_bubble(self, widget: QWidget) -> None:
        idx = max(0, self._conv_col.count() - 1)
        self._conv_col.insertWidget(idx, widget)
        QTimer.singleShot(40, self._scroll_bottom)

    def _scroll_bottom(self) -> None:
        self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        )

    def _clear_history(self) -> None:
        while self._conv_col.count() > 1:
            item = self._conv_col.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _on_api_key_changed(self, text: str) -> None:
        self.voice_engine.set_api_key(text.strip())

    def _toggle_key_echo(self) -> None:
        if self._key_input.echoMode() == QLineEdit.Password:
            self._key_input.setEchoMode(QLineEdit.Normal)
        else:
            self._key_input.setEchoMode(QLineEdit.Password)
