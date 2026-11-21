"""
Agent core orchestrator with background worker for non-blocking local LLM streaming,
multi-turn tool calling engine, and interactive confirmation system (Phase 2.2.2).
Manages conversation history, system prompt, execution states, tools, and SQLite persistence.
"""
import json
import time
import re
import logging
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Any
from PySide6.QtCore import QObject, QThread, Signal

from .model_manager import ModelManager
from ..database.db import db_manager
from ..tools import (
    ToolRegistry,
    ToolExecutor,
    default_tool_registry,
    default_tool_executor
)

logger = logging.getLogger("PersonalAgent.AgentCore")

SYSTEM_PROMPT = (
    "You are Personal Agent, a capable and professional desktop AI assistant running locally on the user's computer.\n\n"
    "Available Tools:\n"
    "1. System Inspection (Read-Only, Auto-Approved):\n"
    "- 'get_current_time': Returns the current system date and time.\n"
    "- 'get_system_info': Returns host OS, Windows version, computer name, CPU info, total/available RAM, and CPU usage.\n"
    "- 'get_gpu_info': Returns NVIDIA GPU name, utilization, VRAM usage/capacity, and temperature.\n\n"
    "2. File & Directory Intelligence (Read-Only, Auto-Approved):\n"
    "- 'search_files(directory, pattern, recursive)': Search for files matching wildcards (*.py, *report*).\n"
    "- 'list_directory(directory, include_hidden)': List files and subfolders with size and modified dates.\n"
    "- 'get_file_info(path)': Inspect file/folder metadata, size, created/modified dates.\n"
    "- 'read_text_file(path, max_characters)': Read code/text files safely (TXT, PY, JS, HTML, JSON, MD, etc.).\n"
    "- 'find_recent_files(directory, days, recursive)': Find files modified in the past N days.\n"
    "- 'find_large_files(directory, minimum_size_mb, recursive)': Find large files sorted largest first.\n"
    "- 'organize_files_preview(directory)': Generate a proposed file organization plan sorted by file type.\n\n"
    "3. File Operations (Requires User Confirmation):\n"
    "- 'copy_file(source, destination)': Copy a file to another location (verified).\n"
    "- 'move_file(source, destination)': Move a file to another location (verified).\n"
    "- 'rename_file(path, new_name)': Rename a file or folder (verified).\n"
    "- 'create_directory(path)': Create a new folder (verified).\n"
    "- 'organize_files(directory)': Move files into categorized subfolders based on extension (verified).\n\n"
    "4. Application & Process Intelligence (Read-Only, Auto-Approved):\n"
    "- 'search_applications(query, maximum_results)': Search for installed or discoverable applications by name or category.\n"
    "- 'list_installed_applications(category, maximum_results)': List discovered desktop applications (categories: Development, Browser, Media, Productivity, System, Other).\n"
    "- 'list_running_processes(filter, maximum_results, sort_by)': Return active processes with CPU %, memory MB, and PID (sort_by: memory, cpu, name, pid).\n"
    "- 'check_application_status(application_name)': Check whether a specific application (e.g. 'Chrome', 'Ollama', 'VS Code') is currently running.\n"
    "- 'get_process_info(process_name, optional_pid)': Retrieve detailed runtime information for a specific process name or PID.\n\n"
    "5. Controlled Application & Process Actions (Requires User Confirmation):\n"
    "- 'launch_application(application_name, optional_arguments)': Launch a registered or verified application (e.g. 'Chrome', 'VS Code', 'Notepad', 'Blender').\n"
    "- 'open_file_with_application(file_path, application_name)': Open a file with a specific application or default Windows handler.\n"
    "- 'open_folder(folder_path)': Open a folder in Windows File Explorer.\n"
    "- 'close_application(application_name, optional_pid)': Gracefully close an application (critical system processes are protected).\n\n"
    "6. Windows UI Automation & Accessibility Tools:\n"
    "- 'list_windows(visible_only, maximum_results)': List open desktop windows with title, PID, and visibility.\n"
    "- 'get_active_window()': Inspect the currently focused foreground window.\n"
    "- 'inspect_window(window_title, maximum_depth, maximum_elements)': Inspect accessible controls (menus, buttons, text inputs) in a window.\n"
    "- 'find_ui_element(window_title, element_name, control_type, automation_id)': Find specific controls in a window by label or ID.\n"
    "- 'click_ui_element(window_title, element_name, control_type, automation_id, match_index)': Click a button or menu in a window.\n"
    "- 'type_into_ui_element(window_title, element_name, text, automation_id, match_index)': Enter text into a text field in a window.\n"
    "- 'read_ui_element(window_title, element_name, control_type, automation_id)': Read text or status from a UI element.\n"
    "- 'focus_window(window_title, process_name, process_id)': Bring target window to the foreground.\n"
    "- 'press_key(window_title, key, approved_key_combination)': Send approved keys or shortcuts (Escape, Tab, Enter, Ctrl+S, F5).\n\n"
    "7. Desktop Physical Actions & Coordinate Grounding (Milestone C):\n"
    "- 'get_screen_metrics()': Retrieve display resolution, virtual multi-monitor bounds, DPI scaling, and cursor position.\n"
    "- 'move_mouse(x, y, normalized, window_title)': Move mouse cursor (default normalized [0-1000] coordinates).\n"
    "- 'click_at(x, y, button, normalized, window_title)': Click at screen coordinates (left, right, middle).\n"
    "- 'double_click_at(x, y, normalized, window_title)': Double-click at screen coordinates.\n"
    "- 'right_click_at(x, y, normalized, window_title)': Right-click at screen coordinates.\n"
    "- 'drag_mouse(start_x, start_y, end_x, end_y, duration_ms, normalized, window_title)': Drag cursor between locations.\n"
    "- 'scroll_at(x, y, clicks, direction, normalized, window_title)': Scroll wheel at screen location (vertical or horizontal).\n"
    "- 'type_desktop_text(text, window_title, delay_ms)': Type text physically using keyboard simulation.\n"
    "- 'press_desktop_key(key, window_title, approved_key_combination)': Send approved physical keyboard shortcut or key.\n"
    "- 'trigger_emergency_stop()': Emergency circuit breaker to instantly abort all desktop actions and release keys.\n"
    "- 'reset_emergency_stop()': Reset emergency stop after abort.\n\n"
    "Tool Usage Rules:\n"
    "- When user asks what windows are open, call 'list_windows'.\n"
    "- When user asks what window is active or currently in use, call 'get_active_window'.\n"
    "- When user asks to inspect an app or see what buttons/controls are available (e.g. 'Inspect Notepad', 'Check which buttons are available'), call 'inspect_window'.\n"
    "- When user asks to find a button, search field, or menu, call 'find_ui_element'.\n"
    "- When user asks to click a button or menu (e.g. 'Click Save', 'Click the New File button'), prefer 'click_ui_element'. If element is not accessible via UI Automation, use coordinate-based 'click_at'.\n"
    "- When user asks to click or move to coordinates or screen locations, use 'click_at' or 'move_mouse'. Use normalized coordinates [0-1000] where (0,0) is top-left and (1000,1000) is bottom-right.\n"
    "- When user asks to type into an app, prefer 'type_into_ui_element'. If not accessible, use 'type_desktop_text'.\n"
    "- When user asks to check screen size, resolution, or DPI, call 'get_screen_metrics'.\n"
    "- When user asks to stop, abort, or freeze desktop automation, call 'trigger_emergency_stop'.\n"
    "- When user asks to type into an app (e.g. 'Type Hello World in Notepad'), call 'type_into_ui_element'.\n"
    "- When user asks to read a dialog or text in an app, call 'read_ui_element'.\n"
    "- When user asks to bring a window to front, call 'focus_window'.\n"
    "- When user asks to open/launch an app (e.g. 'Open Chrome', 'Launch VS Code'), call 'launch_application'.\n"
    "- When user asks if an app or service is running (e.g. 'Is Ollama running?'), call 'check_application_status'.\n"
    "- When user asks what applications or processes are running, call 'list_running_processes'.\n"
    "- When user asks to open a folder, call 'open_folder'.\n"
    "- When user asks to open a file in an editor/tool, call 'open_file_with_application'.\n"
    "- When user asks to close an application, call 'close_application'. The system will prompt the user for confirmation.\n"
    "- When an action is staged for user confirmation (status: 'staged_for_user_approval'), clearly inform the user that you have prepared the action and prompt them to click '[✓ Approve & Execute]' on the confirmation card in chat. NEVER say you cannot open applications, cannot click buttons, or cannot access files.\n"
    "- When user asks file queries or operations, use the appropriate file tool.\n"
    "- For general questions that do not require real-time system metrics, file operations, or process actions, answer directly.\n"
    "- After receiving tool results, provide a clear, concise, and helpful natural-language summary. Do not output raw JSON unless specifically requested.\n\n"
    "General Guidelines:\n"
    "- Be concise, direct, and practical.\n"
    "- If an application request is ambiguous (e.g. 'Open Visual Studio' matches Code and Community), ask clarifying questions.\n"
    "- Never claim an application or process was opened or closed unless verified by tool results.\n"
    "- Clearly distinguish between planning a task and executing a task."
)


class OllamaChatWorker(QThread):
    """
    Worker thread that streams responses from Ollama /api/chat and coordinates
    the tool execution loop across multiple rounds (up to 5 rounds).
    Ensures the main Qt GUI remains completely responsive during model inference and tool runs.
    """
    chunk_received = Signal(str)                         # token string
    finished = Signal(str, dict)                         # full_text, stats dict
    error = Signal(str)                                  # error message
    cancelled = Signal()
    tool_started = Signal(str, dict)                     # tool_name, arguments
    tool_completed = Signal(str, dict, float, bool)      # tool_name, result_dict, duration_ms, success
    confirmation_requested = Signal(dict)                # confirmation payload for UI

    def __init__(
        self,
        endpoint: str,
        model: str,
        messages: List[Dict[str, Any]],
        options: Dict[str, Any],
        tool_registry: Optional[ToolRegistry] = None,
        tool_executor: Optional[ToolExecutor] = None,
        conversation_id: str = "default"
    ):
        super().__init__()
        self.endpoint = endpoint
        self.model = model
        self.messages = messages
        self.options = options
        self.tool_registry = tool_registry or default_tool_registry
        self.tool_executor = tool_executor or default_tool_executor
        self.conversation_id = conversation_id
        self._is_cancelled = False
        self._response_handle = None

    def cancel(self):
        """Request immediate abort of the streaming request or tool execution."""
        self._is_cancelled = True
        if self._response_handle:
            try:
                self._response_handle.close()
            except Exception:
                pass

    def run(self):
        url = f"{self.endpoint}/api/chat"
        current_messages = list(self.messages)
        tools = self.tool_registry.get_ollama_tools() if self.tool_registry else None

        max_rounds = 5
        round_idx = 0
        total_eval_count = 0
        total_eval_duration_ns = 0
        start_time = time.time()
        final_full_text = ""

        while round_idx < max_rounds and not self._is_cancelled:
            round_idx += 1
            payload = {
                "model": self.model,
                "messages": current_messages,
                "stream": True,
                "options": self.options
            }
            if tools:
                payload["tools"] = tools

            round_content = ""
            round_thinking = ""
            is_thinking = False
            detected_tool_calls: List[Dict[str, Any]] = []

            try:
                data_bytes = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=data_bytes,
                    headers={"Content-Type": "application/json", "User-Agent": "PersonalAgent/1.0"}
                )

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
                    tcs = msg.get("tool_calls")
                    if tcs:
                        detected_tool_calls.extend(tcs)

                    if thinking_token:
                        if not is_thinking:
                            is_thinking = True
                            self.chunk_received.emit("<think>\n")
                        self.chunk_received.emit(thinking_token)
                        round_thinking += thinking_token
                    elif content_token:
                        if is_thinking:
                            is_thinking = False
                            self.chunk_received.emit("\n</think>\n\n")
                        self.chunk_received.emit(content_token)
                        round_content += content_token

                    if chunk.get("done"):
                        if is_thinking:
                            is_thinking = False
                            self.chunk_received.emit("\n</think>\n\n")
                        total_eval_count += chunk.get("eval_count", 0)
                        total_eval_duration_ns += chunk.get("eval_duration", 0)
                        break

                try:
                    response.close()
                except Exception:
                    pass

            except urllib.error.URLError as url_err:
                if not self._is_cancelled:
                    msg = f"Cannot connect to Ollama at {self.endpoint}. Please verify the Ollama service is running."
                    logger.error("Ollama connection error: %s", url_err)
                    self.error.emit(msg)
                return
            except Exception as exc:
                if not self._is_cancelled:
                    logger.exception("Inference streaming error: %s", exc)
                    self.error.emit(f"Inference error: {exc}")
                return

            if self._is_cancelled:
                self.cancelled.emit()
                return

            # Structured fallback check if Ollama didn't return native tool_calls
            if not detected_tool_calls and round_content:
                detected_tool_calls = self._check_structured_tool_fallback(round_content)

            # If tool calls were requested, execute them through the safety pipeline
            if detected_tool_calls:
                # Add assistant message with tool calls to context
                assistant_msg = {
                    "role": "assistant",
                    "content": round_content,
                    "tool_calls": detected_tool_calls
                }
                current_messages.append(assistant_msg)

                for tc in detected_tool_calls:
                    if self._is_cancelled:
                        self.cancelled.emit()
                        return

                    func = tc.get("function", {})
                    tool_name = func.get("name", "")
                    args = func.get("arguments", {})
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            args = {}

                    # Notify tool starting
                    self.tool_started.emit(tool_name, args)

                    # Execute tool via executor (Validation -> Permission -> Safe execution)
                    exec_result = self.tool_executor.execute(tool_name, args)
                    result_dict = exec_result.to_dict()

                    # Check if operation requires user confirmation (e.g. copy, move, rename, delete)
                    if exec_result.requires_confirmation:
                        conf_data = exec_result.confirmation_data or {}
                        conf_data["tool"] = tool_name
                        conf_data["arguments"] = args
                        self.confirmation_requested.emit(conf_data)

                    # Save to database
                    try:
                        status_str = "pending_confirmation" if exec_result.requires_confirmation else ("success" if exec_result.success else "error")
                        db_manager.save_tool_execution(
                            tool_name=tool_name,
                            arguments=args,
                            result=result_dict,
                            status=status_str,
                            duration_ms=exec_result.duration_ms,
                            conversation_id=self.conversation_id
                        )
                    except Exception as db_err:
                        logger.warning("Failed to save tool execution: %s", db_err)

                    # Notify tool completed
                    self.tool_completed.emit(
                        tool_name,
                        result_dict,
                        exec_result.duration_ms,
                        exec_result.success
                    )

                    # Append tool response message to context
                    if exec_result.requires_confirmation:
                        action_name = (exec_result.confirmation_data or {}).get("action", tool_name)
                        target_info = (exec_result.confirmation_data or {}).get("application") or (exec_result.confirmation_data or {}).get("target") or tool_name
                        tool_msg_content = json.dumps({
                            "status": "staged_for_user_approval",
                            "requires_confirmation": True,
                            "action": action_name,
                            "message": f"Action '{action_name}' for '{target_info}' has been prepared and an interactive approval card has been displayed to the user in chat. Please ask the user to click [✓ Approve & Execute] on the confirmation card to proceed."
                        })
                    else:
                        tool_msg_content = json.dumps(result_dict)

                    tool_msg = {
                        "role": "tool",
                        "content": tool_msg_content
                    }
                    if "id" in tc:
                        tool_msg["tool_call_id"] = tc["id"]
                    current_messages.append(tool_msg)

                # Continue next round to allow model to analyze tool results
                continue

            else:
                # No tools requested: this was the final response
                final_full_text = round_content
                break

        if self._is_cancelled:
            self.cancelled.emit()
            return

        total_duration = time.time() - start_time
        eval_duration_sec = total_eval_duration_ns / 1e9 if total_eval_duration_ns else total_duration
        tokens_per_sec = (total_eval_count / eval_duration_sec) if eval_duration_sec > 0 else 0.0

        stats = {
            "eval_count": total_eval_count,
            "total_duration": total_duration,
            "tokens_per_sec": tokens_per_sec,
            "model": self.model,
            "rounds": round_idx
        }
        self.finished.emit(final_full_text, stats)

    def _check_structured_tool_fallback(self, content: str) -> List[Dict[str, Any]]:
        """
        Structured JSON fallback: parses explicit tool calls embedded in model output
        if the model produced structured JSON in text instead of native API tool_calls.
        """
        calls: List[Dict[str, Any]] = []
        registered_names = set(self.tool_registry._tools.keys()) if self.tool_registry else set()

        patterns = [
            r'```(?:json)?\s*(\{\s*"name"\s*:\s*"[^"]+".*?\})\s*```',
            r'(\{\s*"name"\s*:\s*"[a-zA-Z0-9_]+"\s*,\s*"arguments"\s*:\s*\{.*?\}\s*\})',
            r'<tool_call>\s*(\{\s*"name"\s*:\s*"[^"]+".*?\})\s*</tool_call>'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for m in matches:
                try:
                    parsed = json.loads(m.strip())
                    if isinstance(parsed, dict) and "name" in parsed:
                        tname = parsed.get("name")
                        if tname in registered_names:
                            calls.append({
                                "id": f"call_fb_{int(time.time()*1000)}",
                                "function": {
                                    "name": tname,
                                    "arguments": parsed.get("arguments", {})
                                }
                            })
                except Exception:
                    pass
            if calls:
                break
        return calls


class AgentCore(QObject):
    """
    Central Agent coordinator for the desktop application.
    Orchestrates Ollama interaction, streaming worker threads, tool engine, confirmation flow, and UI signals.
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
    tool_call_started = Signal(str, dict)  # tool_name, arguments
    tool_call_finished = Signal(str, dict, float, bool) # tool_name, result, duration_ms, success
    confirmation_requested = Signal(dict)  # confirmation card payload

    def __init__(
        self,
        model_manager: Optional[ModelManager] = None,
        tool_registry: Optional[ToolRegistry] = None,
        tool_executor: Optional[ToolExecutor] = None
    ):
        super().__init__()
        self.model_manager = model_manager or ModelManager()
        self.tool_registry = tool_registry or default_tool_registry
        self.tool_executor = tool_executor or default_tool_executor

        self._status = "Ready"
        self._current_task_title = "No task running"
        self._current_task_detail = "Waiting for instruction"
        self._execution_state = "Idle"
        self._recent_activities: List[str] = [
            "Application started",
            "Workspace initialized",
            "Ollama integration active",
            "File Intelligence & Tool Engine active"
        ]

        # Multi-turn conversation context for LLM
        self._conversation_history: List[Dict[str, Any]] = [
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
        self.set_execution_state("Analyzing request")
        self.set_current_task("Inference with " + self.model_manager.active_model, cleaned[:40])

        # 6. Signal UI that a streaming response has started
        self.stream_started.emit("Agent")

        # 7. Start worker thread for non-blocking Ollama generation and tool execution
        options = {
            "temperature": self.model_manager.temperature,
            "num_ctx": self.model_manager.num_ctx,
            "num_gpu": self.model_manager.num_gpu
        }

        self._current_worker = OllamaChatWorker(
            endpoint=self.model_manager.endpoint,
            model=self.model_manager.active_model,
            messages=list(self._conversation_history),
            options=options,
            tool_registry=self.tool_registry,
            tool_executor=self.tool_executor,
            conversation_id="default"
        )
        self._current_worker.chunk_received.connect(self._on_worker_chunk)
        self._current_worker.finished.connect(self._on_worker_finished)
        self._current_worker.error.connect(self._on_worker_error)
        self._current_worker.cancelled.connect(self._on_worker_cancelled)
        self._current_worker.tool_started.connect(self._on_worker_tool_started)
        self._current_worker.tool_completed.connect(self._on_worker_tool_completed)
        self._current_worker.confirmation_requested.connect(self.confirmation_requested.emit)
        self._current_worker.start()

    def _on_worker_chunk(self, chunk: str) -> None:
        self.stream_chunk.emit(chunk)

    def _on_worker_tool_started(self, tool_name: str, arguments: dict) -> None:
        display_name = tool_name.replace("_", " ").title()
        self.set_status("Working")
        self.set_execution_state(f"Using tool: {display_name}")
        self.set_current_task(f"Tool: {display_name}", "Executing tool")
        self.log_activity(f"🔧 Tool: {display_name}")
        self.tool_call_started.emit(tool_name, arguments)

    def _on_worker_tool_completed(self, tool_name: str, result: dict, duration_ms: float, success: bool) -> None:
        display_name = tool_name.replace("_", " ").title()
        if success:
            self.log_activity(f"✓ {display_name} verified ({duration_ms:.1f}ms)")
        elif result.get("requires_confirmation"):
            self.log_activity(f"⏳ {display_name}: Awaiting confirmation")
        else:
            self.log_activity(f"✗ {display_name} failed: {result.get('error', 'Error')}")
        self.tool_call_finished.emit(tool_name, result, duration_ms, success)

    def execute_confirmed_tool(self, tool_name: str, arguments: dict) -> Dict[str, Any]:
        """
        Executes a user-approved tool operation (with confirmed=True) and audits the verified result.
        """
        args_with_conf = dict(arguments)
        args_with_conf["confirmed"] = True

        display_name = tool_name.replace("_", " ").title()
        self.set_status("Working")
        self.set_execution_state(f"Executing: {display_name}")
        self.log_activity(f"✓ Approved: {display_name}")

        self.tool_call_started.emit(tool_name, args_with_conf)
        res = self.tool_executor.execute(tool_name, args_with_conf)
        res_dict = res.to_dict()

        # Save to database
        db_manager.save_tool_execution(
            tool_name=tool_name,
            arguments=args_with_conf,
            result=res_dict,
            status="confirmed_success" if res.success else "confirmed_error",
            duration_ms=res.duration_ms
        )

        self.tool_call_finished.emit(tool_name, res_dict, res.duration_ms, res.success)
        self.set_status("Ready")
        self.set_execution_state("Idle")
        return res_dict

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
        rounds = stats.get("rounds", 1)
        self.log_activity(f"Completed in {rounds} round(s) ({speed:.1f} tok/s)")

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
        """Interrupt and stop active model generation or tool execution."""
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
