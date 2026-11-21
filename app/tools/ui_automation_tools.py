"""
Windows UI Automation Tools for Personal Agent.
Provides tool definitions and handlers for desktop window management, UI element inspection,
and accessibility-based interaction (clicking, typing, reading, and key pressing).
"""
import logging
from typing import Dict, Any, Optional

from .tool_registry import ToolRegistry, ToolDefinition
from .tool_permissions import PermissionLevel
from ..automation import windows_automation

logger = logging.getLogger("PersonalAgent.UIAutomationTools")


# ---------------------------------------------------------------------------
# Tool Handlers
# ---------------------------------------------------------------------------

def handle_list_windows(
    visible_only: bool = True,
    maximum_results: int = 50
) -> Dict[str, Any]:
    """List open desktop windows with title, PID, and visibility."""
    res = windows_automation.list_windows(
        visible_only=visible_only,
        maximum_results=maximum_results
    )
    return res.to_dict()


def handle_get_active_window() -> Dict[str, Any]:
    """Retrieve details about the currently active foreground window."""
    res = windows_automation.get_active_window()
    return res.to_dict()


def handle_inspect_window(
    window_title: str,
    process_name: Optional[str] = None,
    process_id: Optional[int] = None,
    maximum_depth: int = 3,
    maximum_elements: int = 40
) -> Dict[str, Any]:
    """Inspect UI controls of a target window and return a compact observation."""
    res = windows_automation.inspect_window(
        window_title=window_title,
        process_name=process_name,
        process_id=process_id,
        maximum_depth=maximum_depth,
        maximum_elements=maximum_elements
    )
    return res.to_dict()


def handle_find_ui_element(
    window_title: str,
    element_name: str,
    control_type: Optional[str] = None,
    automation_id: Optional[str] = None,
    maximum_results: int = 10
) -> Dict[str, Any]:
    """Search for specific UI elements within a target window."""
    res = windows_automation.find_ui_element(
        window_title=window_title,
        element_name=element_name,
        control_type=control_type,
        automation_id=automation_id,
        maximum_results=maximum_results
    )
    return res.to_dict()


def handle_click_ui_element(
    window_title: str,
    element_name: str,
    control_type: Optional[str] = None,
    automation_id: Optional[str] = None,
    match_index: int = 0,
    confirmed: bool = False
) -> Dict[str, Any]:
    """Click or invoke a UI element in the specified window."""
    if not confirmed:
        return {
            "success": False,
            "requires_confirmation": True,
            "tool": "click_ui_element",
            "title": "UI Action Confirmation Required",
            "action": "Click UI Element",
            "window": window_title,
            "element": element_name,
            "risk": "Will click/invoke interactive control in target window.",
            "message": f"User confirmation required to click '{element_name}' in window '{window_title}'."
        }

    res = windows_automation.click_ui_element(
        window_title=window_title,
        element_name=element_name,
        control_type=control_type,
        automation_id=automation_id,
        match_index=match_index
    )
    return res.to_dict()


def handle_type_into_ui_element(
    window_title: str,
    element_name: str,
    text: str,
    automation_id: Optional[str] = None,
    match_index: int = 0,
    confirmed: bool = False
) -> Dict[str, Any]:
    """Enter text into an editable UI control."""
    if not confirmed:
        return {
            "success": False,
            "requires_confirmation": True,
            "tool": "type_into_ui_element",
            "title": "Text Input Confirmation Required",
            "action": "Type into Element",
            "window": window_title,
            "element": element_name,
            "text": text,
            "risk": "Will input text into selected desktop control.",
            "message": f"User confirmation required to enter text into '{element_name}' in '{window_title}'."
        }

    res = windows_automation.type_into_ui_element(
        window_title=window_title,
        element_name=element_name,
        text=text,
        automation_id=automation_id,
        match_index=match_index
    )
    return res.to_dict()


def handle_read_ui_element(
    window_title: str,
    element_name: str,
    control_type: Optional[str] = None,
    automation_id: Optional[str] = None
) -> Dict[str, Any]:
    """Read the text content or value of a UI element (masks sensitive fields)."""
    res = windows_automation.read_ui_element(
        window_title=window_title,
        element_name=element_name,
        control_type=control_type,
        automation_id=automation_id
    )
    return res.to_dict()


def handle_focus_window(
    window_title: str,
    process_name: Optional[str] = None,
    process_id: Optional[int] = None
) -> Dict[str, Any]:
    """Bring the target window to the foreground and activate it."""
    res = windows_automation.focus_window(
        window_title=window_title,
        process_name=process_name,
        process_id=process_id
    )
    return res.to_dict()


def handle_press_key(
    window_title: str,
    key: str,
    approved_key_combination: Optional[str] = None,
    confirmed: bool = False
) -> Dict[str, Any]:
    """Send an approved key or shortcut combination to the target window."""
    key_norm = key.strip().lower()
    from ..automation.action_executor import SENSITIVE_KEYS
    if key_norm in SENSITIVE_KEYS and not confirmed and not approved_key_combination:
        return {
            "success": False,
            "requires_confirmation": True,
            "tool": "press_key",
            "title": "Key Combination Confirmation Required",
            "action": "Press Key",
            "window": window_title,
            "key": key,
            "risk": f"Will dispatch sensitive key shortcut '{key}' to active window.",
            "message": f"User confirmation required to dispatch key '{key}' to '{window_title}'."
        }

    res = windows_automation.press_key(
        window_title=window_title,
        key=key,
        approved_key_combination=approved_key_combination or ("confirmed" if confirmed else None)
    )
    return res.to_dict()


# ---------------------------------------------------------------------------
# Tool Registration
# ---------------------------------------------------------------------------

def register_ui_automation_tools(registry: ToolRegistry) -> None:
    """Register all Windows UI Automation tools into the tool registry."""

    # 1. list_windows
    registry.register(ToolDefinition(
        name="list_windows",
        description="List open desktop windows with title, PID, visibility, and minimized/maximized state.",
        parameters={
            "type": "object",
            "properties": {
                "visible_only": {
                    "type": "boolean",
                    "description": "Whether to return only visible, non-empty desktop windows (default: true)."
                },
                "maximum_results": {
                    "type": "integer",
                    "description": "Maximum number of windows to return (default: 50)."
                }
            }
        },
        handler=handle_list_windows,
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="ui_automation"
    ))

    # 2. get_active_window
    registry.register(ToolDefinition(
        name="get_active_window",
        description="Return information about the currently active foreground window.",
        parameters={
            "type": "object",
            "properties": {}
        },
        handler=handle_get_active_window,
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="ui_automation"
    ))

    # 3. inspect_window
    registry.register(ToolDefinition(
        name="inspect_window",
        description="Inspect a window's UI Automation tree and return detected controls and a compact summary.",
        parameters={
            "type": "object",
            "properties": {
                "window_title": {
                    "type": "string",
                    "description": "The title or partial title of the window to inspect (e.g. 'Notepad', 'Calculator')."
                },
                "process_name": {
                    "type": "string",
                    "description": "Optional process name filter (e.g. 'notepad.exe')."
                },
                "process_id": {
                    "type": "integer",
                    "description": "Optional process ID filter."
                },
                "maximum_depth": {
                    "type": "integer",
                    "description": "Maximum tree traversal depth (default: 3)."
                },
                "maximum_elements": {
                    "type": "integer",
                    "description": "Maximum number of elements to inspect (default: 40)."
                }
            },
            "required": ["window_title"]
        },
        handler=handle_inspect_window,
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="ui_automation"
    ))

    # 4. find_ui_element
    registry.register(ToolDefinition(
        name="find_ui_element",
        description="Search for UI elements (buttons, inputs, menus) in a selected window by name or ID.",
        parameters={
            "type": "object",
            "properties": {
                "window_title": {
                    "type": "string",
                    "description": "Title of the window containing the element."
                },
                "element_name": {
                    "type": "string",
                    "description": "Name or label of the target UI element (e.g. 'Save', 'File', 'Search')."
                },
                "control_type": {
                    "type": "string",
                    "description": "Optional control type filter (e.g. 'Button', 'Edit', 'MenuItem', 'CheckBox')."
                },
                "automation_id": {
                    "type": "string",
                    "description": "Optional AutomationId of the control."
                },
                "maximum_results": {
                    "type": "integer",
                    "description": "Maximum number of matching elements to return (default: 10)."
                }
            },
            "required": ["window_title", "element_name"]
        },
        handler=handle_find_ui_element,
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="ui_automation"
    ))

    # 5. click_ui_element
    registry.register(ToolDefinition(
        name="click_ui_element",
        description="Click or invoke an interactive UI element (Button, Tab, MenuItem) in a window using native UI patterns.",
        parameters={
            "type": "object",
            "properties": {
                "window_title": {
                    "type": "string",
                    "description": "Title of the window containing the element."
                },
                "element_name": {
                    "type": "string",
                    "description": "Name or label of the element to click (e.g. 'Save', 'Close', 'Next')."
                },
                "control_type": {
                    "type": "string",
                    "description": "Optional control type (e.g. 'Button', 'MenuItem')."
                },
                "automation_id": {
                    "type": "string",
                    "description": "Optional AutomationId of the control."
                },
                "match_index": {
                    "type": "integer",
                    "description": "Zero-based match index if multiple elements share the same name (default: 0)."
                },
                "confirmed": {
                    "type": "boolean",
                    "description": "User approval confirmation flag."
                }
            },
            "required": ["window_title", "element_name"]
        },
        handler=handle_click_ui_element,
        permission_level=PermissionLevel.CONTROLLED_ACTION,
        category="ui_automation"
    ))

    # 6. type_into_ui_element
    registry.register(ToolDefinition(
        name="type_into_ui_element",
        description="Enter text into an editable UI control (text box, search input, document area) in a window.",
        parameters={
            "type": "object",
            "properties": {
                "window_title": {
                    "type": "string",
                    "description": "Title of the window containing the text control."
                },
                "element_name": {
                    "type": "string",
                    "description": "Name or label of the text input (e.g. 'Search', 'Text Editor', 'File name:')."
                },
                "text": {
                    "type": "string",
                    "description": "The exact text to enter into the control."
                },
                "automation_id": {
                    "type": "string",
                    "description": "Optional AutomationId of the control."
                },
                "match_index": {
                    "type": "integer",
                    "description": "Zero-based match index if multiple text fields match (default: 0)."
                },
                "confirmed": {
                    "type": "boolean",
                    "description": "User approval confirmation flag."
                }
            },
            "required": ["window_title", "element_name", "text"]
        },
        handler=handle_type_into_ui_element,
        permission_level=PermissionLevel.CONTROLLED_ACTION,
        category="ui_automation"
    ))

    # 7. read_ui_element
    registry.register(ToolDefinition(
        name="read_ui_element",
        description="Read the text content or value of a UI element (e.g. status bar, search box, dialog text).",
        parameters={
            "type": "object",
            "properties": {
                "window_title": {
                    "type": "string",
                    "description": "Title of the window containing the element."
                },
                "element_name": {
                    "type": "string",
                    "description": "Name or label of the element to read."
                },
                "control_type": {
                    "type": "string",
                    "description": "Optional control type (e.g. 'Text', 'Edit', 'StatusBar')."
                },
                "automation_id": {
                    "type": "string",
                    "description": "Optional AutomationId of the control."
                }
            },
            "required": ["window_title", "element_name"]
        },
        handler=handle_read_ui_element,
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="ui_automation"
    ))

    # 8. focus_window
    registry.register(ToolDefinition(
        name="focus_window",
        description="Bring target window to the foreground, restore if minimized, and set keyboard focus.",
        parameters={
            "type": "object",
            "properties": {
                "window_title": {
                    "type": "string",
                    "description": "Title or partial title of the window to focus."
                },
                "process_name": {
                    "type": "string",
                    "description": "Optional process name filter (e.g. 'chrome.exe', 'code.exe')."
                },
                "process_id": {
                    "type": "integer",
                    "description": "Optional process ID filter."
                }
            },
            "required": ["window_title"]
        },
        handler=handle_focus_window,
        permission_level=PermissionLevel.CONTROLLED_ACTION,
        category="ui_automation"
    ))

    # 9. press_key
    registry.register(ToolDefinition(
        name="press_key",
        description="Send an approved key or shortcut (Escape, Tab, Enter, Ctrl+S, Ctrl+A, F5) to the target window.",
        parameters={
            "type": "object",
            "properties": {
                "window_title": {
                    "type": "string",
                    "description": "Title of the window to receive the keystroke."
                },
                "key": {
                    "type": "string",
                    "description": "The key or key combination to press (e.g. 'Escape', 'Tab', 'Ctrl+S', 'Enter')."
                },
                "approved_key_combination": {
                    "type": "string",
                    "description": "Confirmation indicator for sensitive keys like 'Alt+F4' or 'Ctrl+W'."
                },
                "confirmed": {
                    "type": "boolean",
                    "description": "User approval confirmation flag."
                }
            },
            "required": ["window_title", "key"]
        },
        handler=handle_press_key,
        permission_level=PermissionLevel.CONTROLLED_ACTION,
        category="ui_automation"
    ))
