"""
Agent core orchestrator.
Manages agent execution state, communication signals, and interaction pipeline.
"""
from typing import Optional, Callable, List
from PySide6.QtCore import QObject, Signal


class AgentCore(QObject):
    """
    Central Agent coordinator for the desktop application.
    Emits signals for state changes, new messages, and status updates.
    """
    status_changed = Signal(str)           # "Ready", "Running", "Paused", "Idle"
    current_task_changed = Signal(str, str) # title, detail
    execution_state_changed = Signal(str)  # "Idle", "Executing", "Waiting"
    activity_logged = Signal(str)          # Single line activity summary
    message_received = Signal(str, str)    # sender ("You" or "Agent"), content

    def __init__(self):
        super().__init__()
        self._status = "Ready"
        self._current_task_title = "No task running"
        self._current_task_detail = "Waiting for instruction"
        self._execution_state = "Idle"
        self._recent_activities: List[str] = [
            "Application started",
            "Workspace initialized",
            "Model connection pending"
        ]

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

    def process_user_input(self, text: str) -> None:
        """Handle incoming user message from chat or home command bar."""
        cleaned = text.strip()
        if not cleaned:
            return

        # Emit user message
        self.message_received.emit("You", cleaned)
        self.log_activity(f"Command received: '{cleaned[:30]}...'")

        # Simulate agent processing response for Phase 1
        self.set_status("Working")
        self.set_execution_state("Processing instruction")
        self.set_current_task("Processing prompt", cleaned)

        # Generate contextual placeholder response based on keywords
        response = self._generate_phase1_response(cleaned)
        
        # In a real environment or future phases, this connects to streaming AI
        self.message_received.emit("Agent", response)
        self.set_status("Ready")
        self.set_execution_state("Idle")
        self.set_current_task("No task running", "Waiting for instruction")

    def _generate_phase1_response(self, text: str) -> str:
        lower = text.lower()
        if "download" in lower or "organize" in lower:
            return "I'll monitor the folder, wait for active downloads to finish, then organize completed files and verify the destination."
        elif "code" in lower or "test" in lower or "script" in lower:
            return "Prepared workspace for coding task. I can review repository files, generate tests, and run local checks in the terminal."
        elif "browse" in lower or "search" in lower or "web" in lower:
            return "Browser automation interface is staged. In Phase 2, I can navigate, extract DOM content, and submit forms on target sites."
        elif "workflow" in lower or "automate" in lower:
            return "Trigger and action nodes loaded into the Automation Builder. You can customize the pipeline steps on the Workflows page."
        elif "file" in lower or "move" in lower:
            return "File manager indexed the local directory safely. Destructive actions are guarded by Phase 1 safety policies."
        else:
            return f"Received: \"{text}\". I'm ready to assist. In future phases, streaming model responses and local execution tools will take action on this prompt."
