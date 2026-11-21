"""
Agent core orchestrator with background worker for non-blocking local LLM streaming.
Manages conversation history, system prompt, execution states, and SQLite persistence.
"""
import json
import time
import logging
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Any
from PySide6.QtCore import QObject, QThread, Signal

from .model_manager import ModelManager
from ..database.db import db_manager

logger = logging.getLogger("PersonalAgent.AgentCore")

SYSTEM_PROMPT = (
    "You are Personal Agent, a capable and professional desktop AI assistant running locally on the user's computer.\n"
    "Your capabilities:\n"
    "- Understand natural-language commands and assist with computer tasks.\n"
    "- Assist with programming, coding analysis, debugging, and scripts.\n"
    "- Help organize, review, and manage local files and workspaces.\n"
    "- Help structure, plan, and automate multi-step desktop workflows.\n\n"
    "Guidelines:\n"
    "- Be concise, direct, and practical.\n"
    "- If a request is ambiguous or lacks essential details, ask clarifying questions.\n"
    "- Never pretend to have executed actions, changed files, launched apps, or accessed websites that you have not actually performed.\n"
    "- Clearly distinguish between planning a task and executing a task.\n"
    "- In Phase 2.1, external tool execution (such as browser control, direct file modification, or voice recognition) is staged; do not claim those actions have taken place."
)


class OllamaChatWorker(QThread):
    """
    Worker thread that streams responses from Ollama /api/chat.
    Ensures the main Qt GUI remains completely responsive during model inference.
    """
    chunk_received = Signal(str)            # token string
    finished = Signal(str, dict)            # full_text, stats dict
    error = Signal(str)                     # error message
    cancelled = Signal()

    def __init__(self, endpoint: str, model: str, messages: List[Dict[str, str]], options: Dict[str, Any]):
        super().__init__()
        self.endpoint = endpoint
        self.model = model
        self.messages = messages
        self.options = options
        self._is_cancelled = False
        self._response_handle = None

    def cancel(self):
        """Request immediate abort of the streaming request."""
        self._is_cancelled = True
        if self._response_handle:
            try:
                self._response_handle.close()
            except Exception:
                pass

    def run(self):
        url = f"{self.endpoint}/api/chat"
        payload = {
            "model": self.model,
            "messages": self.messages,
            "stream": True,
            "options": self.options
        }

        full_text = ""
        start_time = time.time()
        eval_count = 0
        eval_duration_ns = 0

        is_thinking = False
        try:
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={"Content-Type": "application/json", "User-Agent": "PersonalAgent/1.0"}
            )

            # Use generous timeout for prompt evaluation & first token
            response = urllib.request.urlopen(req, timeout=60)
            self._response_handle = response

            while not self._is_cancelled:
                try:
                    raw_line = response.readline()
                except Exception as read_err:
                    if not self._is_cancelled:
                        logger.warning("Socket read ended: %s", read_err)
                    break

                if not raw_line:
                    break

                line_str = raw_line.decode("utf-8").strip()
                if not line_str:
                    continue

                try:
                    chunk = json.loads(line_str)
                except Exception:
                    continue

                msg = chunk.get("message", {})
                thinking_token = msg.get("thinking", "")
                content_token = msg.get("content", "")

                if thinking_token:
                    if not is_thinking:
                        is_thinking = True
                        self.chunk_received.emit("<think>\n")
                        full_text += "<think>\n"
                    self.chunk_received.emit(thinking_token)
                    full_text += thinking_token
                elif content_token:
                    if is_thinking:
                        is_thinking = False
                        self.chunk_received.emit("\n</think>\n\n")
                        full_text += "\n</think>\n\n"
                    self.chunk_received.emit(content_token)
                    full_text += content_token

                if chunk.get("done"):
                    if is_thinking:
                        is_thinking = False
                        self.chunk_received.emit("\n</think>\n\n")
                        full_text += "\n</think>\n\n"
                    eval_count = chunk.get("eval_count", 0)
                    eval_duration_ns = chunk.get("eval_duration", 0)
                    break

            try:
                response.close()
            except Exception:
                pass

            if self._is_cancelled:
                self.cancelled.emit()
                return

            total_duration = time.time() - start_time
            eval_duration_sec = eval_duration_ns / 1e9 if eval_duration_ns else total_duration
            tokens_per_sec = (eval_count / eval_duration_sec) if eval_duration_sec > 0 else 0.0

            stats = {
                "eval_count": eval_count,
                "total_duration": total_duration,
                "tokens_per_sec": tokens_per_sec,
                "model": self.model
            }
            self.finished.emit(full_text, stats)

        except urllib.error.URLError as url_err:
            if not self._is_cancelled:
                msg = f"Cannot connect to Ollama at {self.endpoint}. Please verify the Ollama service is running."
                logger.error("Ollama connection error: %s", url_err)
                self.error.emit(msg)
        except Exception as exc:
            if not self._is_cancelled:
                logger.exception("Inference streaming error: %s", exc)
                self.error.emit(f"Inference error: {exc}")


class AgentCore(QObject):
    """
    Central Agent coordinator for the desktop application.
    Orchestrates Ollama interaction, streaming worker threads, and UI signals.
    """
    status_changed = Signal(str)           # "Ready", "Thinking...", "Streaming...", "Idle"
    current_task_changed = Signal(str, str) # title, detail
    execution_state_changed = Signal(str)  # "Idle", "Executing", "Waiting"
    activity_logged = Signal(str)          # Single line activity summary
    message_received = Signal(str, str)    # sender ("You" or "Agent"), content
    stream_started = Signal(str)           # sender ("Agent")
    stream_chunk = Signal(str)             # token chunk
    stream_finished = Signal(str, dict)    # full_text, stats
    stream_error = Signal(str)             # error message

    def __init__(self, model_manager: Optional[ModelManager] = None):
        super().__init__()
        self.model_manager = model_manager or ModelManager()
        self._status = "Ready"
        self._current_task_title = "No task running"
        self._current_task_detail = "Waiting for instruction"
        self._execution_state = "Idle"
        self._recent_activities: List[str] = [
            "Application started",
            "Workspace initialized",
            "Ollama integration active"
        ]

        # Multi-turn conversation context for LLM
        self._conversation_history: List[Dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

        self._current_worker: Optional[OllamaChatWorker] = None

        # Load persisted messages from database into memory
        self._load_persisted_chat_history()

    @property
    def status(self) -> str:
        return self._status

    @property
    def current_task(self) -> tuple[str, str]:
        return self._current_task_title, self._current_task_detail

    @property
    def execution_state(self) -> str:
        return self._execution_state

    @property
    def recent_activities(self) -> List[str]:
        return list(self._recent_activities)

    @property
    def is_generating(self) -> bool:
        return self._current_worker is not None and self._current_worker.isRunning()

    def set_status(self, status: str) -> None:
        self._status = status
        self.status_changed.emit(status)

    def set_current_task(self, title: str, detail: str = "") -> None:
        self._current_task_title = title
        self._current_task_detail = detail
        self.current_task_changed.emit(title, detail)

    def set_execution_state(self, state: str) -> None:
        self._execution_state = state
        self.execution_state_changed.emit(state)

    def log_activity(self, activity: str) -> None:
        self._recent_activities.insert(0, activity)
        if len(self._recent_activities) > 20:
            self._recent_activities.pop()
        self.activity_logged.emit(activity)

    def _load_persisted_chat_history(self) -> None:
        """Load messages from SQLite to hydrate multi-turn context."""
        try:
            records = db_manager.get_messages(limit=50)
            for rec in records:
                role = rec.get("role", "user")
                content = rec.get("content", "")
                if content:
                    self._conversation_history.append({"role": role, "content": content})
        except Exception as e:
            logger.warning("Failed to load conversation history from db: %s", e)

    def process_user_input(self, text: str) -> None:
        """Handle incoming user message from chat or home command bar."""
        cleaned = text.strip()
        if not cleaned:
            return

        if self.is_generating:
            logger.warning("Generation already in progress. Ignoring duplicate request.")
            return

        # 1. Save user message to database
        db_manager.save_message(role="user", content=cleaned, model=self.model_manager.active_model)

        # 2. Add to in-memory conversation context
        self._conversation_history.append({"role": "user", "content": cleaned})

        # 3. Emit user message signal for UI display
        self.message_received.emit("You", cleaned)
        self.log_activity(f"User: '{cleaned[:28]}...'")

        # 4. Check if Ollama is connected
        if not self.model_manager.is_connected:
            # Try a quick reconnection check
            self.model_manager.check_connection()

        if not self.model_manager.is_connected:
            err_msg = (
                f"Ollama is not running or unreachable at {self.model_manager.endpoint}.\n"
                f"Please ensure Ollama is started (`ollama serve`) and try again."
            )
            self.stream_error.emit(err_msg)
            self.set_status("Ready")
            self.set_execution_state("Idle")
            return

        # 5. Update agent execution state
        self.set_status("Working")
        self.set_execution_state("Generating response")
        self.set_current_task("Inference with " + self.model_manager.active_model, cleaned[:40])

        # 6. Signal UI that a streaming response has started
        self.stream_started.emit("Agent")

        # 7. Start worker thread for non-blocking Ollama generation
        options = {
            "temperature": self.model_manager.temperature,
            "num_ctx": self.model_manager.num_ctx,
            "num_gpu": self.model_manager.num_gpu
        }

        self._current_worker = OllamaChatWorker(
            endpoint=self.model_manager.endpoint,
            model=self.model_manager.active_model,
            messages=list(self._conversation_history),
            options=options
        )
        self._current_worker.chunk_received.connect(self._on_worker_chunk)
        self._current_worker.finished.connect(self._on_worker_finished)
        self._current_worker.error.connect(self._on_worker_error)
        self._current_worker.cancelled.connect(self._on_worker_cancelled)
        self._current_worker.start()

    def _on_worker_chunk(self, chunk: str) -> None:
        self.stream_chunk.emit(chunk)

    def _on_worker_finished(self, full_text: str, stats: dict) -> None:
        # Save assistant message to DB
        db_manager.save_message(
            role="assistant",
            content=full_text,
            model=self.model_manager.active_model
        )
        self._conversation_history.append({"role": "assistant", "content": full_text})

        # Update model manager's processor status
        self.model_manager.query_running_processor()

        speed = stats.get("tokens_per_sec", 0.0)
        self.log_activity(f"Generated {stats.get('eval_count', 0)} tokens ({speed:.1f} tok/s)")

        self.stream_finished.emit(full_text, stats)
        self.set_status("Ready")
        self.set_execution_state("Idle")
        self.set_current_task("No task running", "Waiting for instruction")

    def _on_worker_error(self, err_msg: str) -> None:
        self.log_activity(f"Inference error: {err_msg[:30]}")
        self.stream_error.emit(err_msg)
        self.set_status("Ready")
        self.set_execution_state("Idle")
        self.set_current_task("No task running", "Waiting for instruction")

    def _on_worker_cancelled(self) -> None:
        self.log_activity("Generation stopped by user")
        self.set_status("Ready")
        self.set_execution_state("Idle")
        self.set_current_task("No task running", "Waiting for instruction")

    def stop_generation(self) -> None:
        """Interrupt and stop active model generation."""
        worker = self._current_worker
        self._current_worker = None
        if worker and worker.isRunning():
            worker.cancel()
            worker.wait(1000)
            if worker.isRunning():
                worker.terminate()
                worker.wait(500)
        self.set_status("Ready")
        self.set_execution_state("Idle")
        self.set_current_task("No task running", "Generation stopped")

    def clear_conversation(self) -> None:
        """Clear conversation history both in memory and SQLite."""
        self.stop_generation()
        self._conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        db_manager.clear_messages()
        self.log_activity("Chat conversation cleared")
