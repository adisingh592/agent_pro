"""
Windows Automation Coordinator for Personal Agent.
Provides a unified, high-level API connecting window management, element inspection,
control searching, and action execution.
"""
import logging
from typing import Optional, Dict, Any, List

from .automation_models import (
    WindowInfo,
    UIElementInfo,
    ElementMatch,
    AutomationResult
)
from .window_manager import window_manager, WindowManager
from .element_inspector import element_inspector, ElementInspector
from .element_finder import element_finder, ElementFinder
from .action_executor import action_executor, ActionExecutor

logger = logging.getLogger("PersonalAgent.WindowsAutomation")


class WindowsAutomationEngine:
    """Unified engine coordinating Windows Desktop UI Automation."""

    def __init__(self):
        self.window_mgr = window_manager
        self.inspector = element_inspector
        self.finder = element_finder
        self.executor = action_executor

    def list_windows(
        self,
        visible_only: bool = True,
        maximum_results: int = 50
    ) -> AutomationResult:
        """List open desktop windows."""
        try:
            wins = self.window_mgr.list_windows(
                visible_only=visible_only,
                maximum_results=maximum_results
            )
            return AutomationResult(
                success=True,
                message=f"Found {len(wins)} desktop window(s).",
                data={
                    "windows": [w.to_dict() for w in wins],
                    "total_count": len(wins)
                }
            )
        except Exception as e:
            logger.error(f"Error listing windows: {e}")
            return AutomationResult(
                success=False,
                message=f"Failed to list desktop windows: {str(e)}",
                error=str(e)
            )

    def get_active_window(self) -> AutomationResult:
        """Get the currently focused foreground window."""
        try:
            win = self.window_mgr.get_active_window()
            if not win:
                return AutomationResult(
                    success=False,
                    message="No active foreground window detected.",
                    error="NO_FOREGROUND_WINDOW"
                )
            return AutomationResult(
                success=True,
                message=f"Active window: '{win.window_title}' (PID: {win.process_id}).",
                data=win.to_dict()
            )
        except Exception as e:
            logger.error(f"Error getting active window: {e}")
            return AutomationResult(
                success=False,
                message=f"Failed to detect active window: {str(e)}",
                error=str(e)
            )

    def inspect_window(
        self,
        window_title: str,
        process_name: Optional[str] = None,
        process_id: Optional[int] = None,
        maximum_depth: int = 3,
        maximum_elements: int = 40
    ) -> AutomationResult:
        """Inspect a window's UI Automation tree."""
        return self.inspector.inspect_window(
            window_title=window_title,
            process_name=process_name,
            process_id=process_id,
            maximum_depth=maximum_depth,
            maximum_elements=maximum_elements
        )

    def find_ui_element(
        self,
        window_title: str,
        element_name: Optional[str] = None,
        control_type: Optional[str] = None,
        automation_id: Optional[str] = None,
        maximum_results: int = 10
    ) -> AutomationResult:
        """Search for controls in a window by name, type, or ID."""
        return self.finder.find_elements(
            window_title=window_title,
            element_name=element_name,
            control_type=control_type,
            automation_id=automation_id,
            maximum_results=maximum_results
        )

    def click_ui_element(
        self,
        window_title: str,
        element_name: str,
        control_type: Optional[str] = None,
        automation_id: Optional[str] = None,
        match_index: int = 0
    ) -> AutomationResult:
        """Click / invoke a UI element in the specified window."""
        return self.executor.click_element(
            window_title=window_title,
            element_name=element_name,
            control_type=control_type,
            automation_id=automation_id,
            match_index=match_index
        )

    def type_into_ui_element(
        self,
        window_title: str,
        element_name: str,
        text: str,
        automation_id: Optional[str] = None,
        match_index: int = 0
    ) -> AutomationResult:
        """Type text into an editable control in the specified window."""
        return self.executor.type_into_element(
            window_title=window_title,
            element_name=element_name,
            text=text,
            automation_id=automation_id,
            match_index=match_index
        )

    def read_ui_element(
        self,
        window_title: str,
        element_name: str,
        control_type: Optional[str] = None,
        automation_id: Optional[str] = None
    ) -> AutomationResult:
        """Read the text content or value of a UI element."""
        return self.executor.read_element(
            window_title=window_title,
            element_name=element_name,
            control_type=control_type,
            automation_id=automation_id
        )

    def focus_window(
        self,
        window_title: str,
        process_name: Optional[str] = None,
        process_id: Optional[int] = None
    ) -> AutomationResult:
        """Bring target window to the foreground."""
        return self.window_mgr.focus_window(
            window_title=window_title,
            process_name=process_name,
            process_id=process_id
        )

    def press_key(
        self,
        window_title: str,
        key: str,
        approved_key_combination: Optional[str] = None
    ) -> AutomationResult:
        """Send a key or key combination to the target window."""
        return self.executor.press_key(
            window_title=window_title,
            key=key,
            approved_key_combination=approved_key_combination
        )


# Global singleton instance
windows_automation = WindowsAutomationEngine()
