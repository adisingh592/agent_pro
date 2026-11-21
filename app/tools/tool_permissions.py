"""
Tool Permissions and Security Categorization for Personal Agent.
Determines whether tools execute automatically or require explicit user approval.
"""
from enum import Enum
from typing import Dict, Any, Optional


class PermissionLevel(str, Enum):
    """Permission levels for tool execution safety."""
    SAFE_READ_ONLY = "safe_read_only"              # Read-only information (time, system stats); always auto-approved
    SAFE_ACTION = "safe_action"                    # Safe non-destructive operations (file reading, search)
    SENSITIVE_READ = "sensitive_read"              # Sensitive reads (private files, process lists)
    MODERATE_WRITE = "moderate_write"              # Modifying files, creating folders (requires user confirmation)
    CONTROLLED_ACTION = "controlled_action"        # Launching apps, opening files/folders (requires user confirmation)
    PROCESS_MODIFICATION = "process_modification"  # Graceful process termination (requires user confirmation)
    DESTRUCTIVE = "destructive"                    # Deleting files, killing processes, system modifications (requires user approval)


class ToolPermissionPolicy:
    """Policy rules governing tool execution permissions."""

    def __init__(self, allow_auto_execution: bool = True):
        self.allow_auto_execution = allow_auto_execution
        # Tools explicitly permitted to run without prompt
        self._auto_approved_tools = {
            "get_current_time",
            "get_system_info",
            "get_gpu_info",
            "search_applications",
            "list_installed_applications",
            "list_running_processes",
            "check_application_status",
            "get_process_info",
            # Windows UI Automation Read-Only Tools
            "list_windows",
            "get_active_window",
            "inspect_window",
            "find_ui_element",
            "read_ui_element",
            "focus_window"
        }

    def is_tool_allowed(
        self,
        tool_name: str,
        permission_level: PermissionLevel,
        is_confirmed: bool = False
    ) -> tuple[bool, str]:
        """
        Check if a tool is permitted to execute.
        Returns: (is_allowed, reason)
        """
        if not self.allow_auto_execution:
            return False, "Automated tool execution is disabled in settings."

        if permission_level in (PermissionLevel.SAFE_READ_ONLY, PermissionLevel.SAFE_ACTION):
            return True, "Safe tool auto-approved."

        if tool_name in self._auto_approved_tools:
            return True, f"Tool '{tool_name}' is in auto-approved safe list."

        if permission_level == PermissionLevel.MODERATE_WRITE:
            if is_confirmed:
                return True, "Moderate write operation approved by user confirmation."
            return False, f"Tool '{tool_name}' requires explicit user confirmation (moderate write level)."

        if permission_level == PermissionLevel.CONTROLLED_ACTION:
            if is_confirmed:
                return True, "Controlled application action approved by user confirmation."
            return False, f"Tool '{tool_name}' requires explicit user confirmation (controlled action level)."

        if permission_level == PermissionLevel.PROCESS_MODIFICATION:
            if is_confirmed:
                return True, "Process modification approved by user confirmation."
            return False, f"Tool '{tool_name}' requires explicit user confirmation (process modification level)."

        if permission_level == PermissionLevel.DESTRUCTIVE:
            if is_confirmed:
                return True, "Destructive operation explicitly approved by user."
            return False, f"Tool '{tool_name}' requires explicit user confirmation (destructive level)."

        return True, "Tool approved under current security policy."

    def add_auto_approved_tool(self, tool_name: str) -> None:
        self._auto_approved_tools.add(tool_name)

    def remove_auto_approved_tool(self, tool_name: str) -> None:
        self._auto_approved_tools.discard(tool_name)


# Global default permission policy
default_permission_policy = ToolPermissionPolicy()
