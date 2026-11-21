"""
Desktop Physical Actions & Coordinate Tools for Personal Agent.
Provides tool definitions and handlers for physical mouse movements, clicks,
dragging, scrolling, typing, key combinations, and emergency stop.
"""
import logging
from typing import Dict, Any, Optional

from .tool_registry import ToolRegistry, ToolDefinition
from .tool_permissions import PermissionLevel
from ..automation.actions import (
    coordinate_mapper,
    input_simulator,
    emergency_stop
)

logger = logging.getLogger("PersonalAgent.DesktopActionTools")


# ---------------------------------------------------------------------------
# Tool Handlers
# ---------------------------------------------------------------------------

def handle_get_screen_metrics() -> Dict[str, Any]:
    """Retrieve screen resolution, multi-monitor virtual bounds, DPI scaling, and cursor position."""
    metrics = coordinate_mapper.get_screen_metrics()
    return {
        "success": True,
        "message": f"Screen Resolution: {metrics.primary_width}x{metrics.primary_height} (DPI scale: {metrics.dpi_scale:.2f})",
        "result": metrics.to_dict(),
        "data": metrics.to_dict()
    }


def handle_move_mouse(
    x: int,
    y: int,
    normalized: bool = True,
    window_title: Optional[str] = None,
    confirmed: bool = False
) -> Dict[str, Any]:
    """Move mouse cursor to designated coordinates (normalized 0-1000 by default)."""
    if not confirmed:
        coord_type = "normalized [0-1000]" if normalized else "pixels"
        target_str = f" in window '{window_title}'" if window_title else " on desktop"
        return {
            "success": False,
            "requires_confirmation": True,
            "tool": "move_mouse",
            "title": "Mouse Movement Approval Required",
            "action": "Move Mouse Cursor",
            "coordinates": f"({x}, {y}) ({coord_type})",
            "window": window_title or "Full Desktop",
            "risk": f"Will physically move mouse cursor to ({x}, {y}){target_str}.",
            "message": f"User confirmation required to move mouse to ({x}, {y}){target_str}."
        }

    res = input_simulator.move_mouse(x=x, y=y, normalized=normalized, window_title=window_title)
    d = res.to_dict()
    d["result"] = d
    return d


def handle_click_at(
    x: int,
    y: int,
    button: str = "left",
    normalized: bool = True,
    window_title: Optional[str] = None,
    confirmed: bool = False
) -> Dict[str, Any]:
    """Click at specified screen coordinates (normalized 0-1000 or actual pixels)."""
    if not confirmed:
        coord_type = "normalized [0-1000]" if normalized else "pixels"
        target_str = f" in window '{window_title}'" if window_title else " on desktop"
        return {
            "success": False,
            "requires_confirmation": True,
            "tool": "click_at",
            "title": "Mouse Click Approval Required",
            "action": f"{button.capitalize()}-Click at Coordinates",
            "coordinates": f"({x}, {y}) ({coord_type})",
            "window": window_title or "Full Desktop",
            "risk": f"Will physically dispatch a {button}-click at ({x}, {y}){target_str}.",
            "message": f"User confirmation required to click at ({x}, {y}){target_str}."
        }

    res = input_simulator.click(x=x, y=y, button=button, normalized=normalized, window_title=window_title)
    d = res.to_dict()
    d["result"] = d
    return d


def handle_double_click_at(
    x: int,
    y: int,
    normalized: bool = True,
    window_title: Optional[str] = None,
    confirmed: bool = False
) -> Dict[str, Any]:
    """Double-click at specified screen coordinates."""
    if not confirmed:
        coord_type = "normalized [0-1000]" if normalized else "pixels"
        target_str = f" in window '{window_title}'" if window_title else " on desktop"
        return {
            "success": False,
            "requires_confirmation": True,
            "tool": "double_click_at",
            "title": "Mouse Double-Click Approval Required",
            "action": "Double-Click at Coordinates",
            "coordinates": f"({x}, {y}) ({coord_type})",
            "window": window_title or "Full Desktop",
            "risk": f"Will physically dispatch a double-click at ({x}, {y}){target_str}.",
            "message": f"User confirmation required to double-click at ({x}, {y}){target_str}."
        }

    res = input_simulator.double_click(x=x, y=y, normalized=normalized, window_title=window_title)
    d = res.to_dict()
    d["result"] = d
    return d


def handle_right_click_at(
    x: int,
    y: int,
    normalized: bool = True,
    window_title: Optional[str] = None,
    confirmed: bool = False
) -> Dict[str, Any]:
    """Right-click at specified screen coordinates to open context menus."""
    if not confirmed:
        coord_type = "normalized [0-1000]" if normalized else "pixels"
        target_str = f" in window '{window_title}'" if window_title else " on desktop"
        return {
            "success": False,
            "requires_confirmation": True,
            "tool": "right_click_at",
            "title": "Mouse Right-Click Approval Required",
            "action": "Right-Click at Coordinates",
            "coordinates": f"({x}, {y}) ({coord_type})",
            "window": window_title or "Full Desktop",
            "risk": f"Will dispatch a right-click at ({x}, {y}){target_str}.",
            "message": f"User confirmation required to right-click at ({x}, {y}){target_str}."
        }

    res = input_simulator.click(x=x, y=y, button="right", normalized=normalized, window_title=window_title)
    d = res.to_dict()
    d["result"] = d
    return d


def handle_drag_mouse(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration_seconds: float = 0.5,
    normalized: bool = True,
    window_title: Optional[str] = None,
    confirmed: bool = False
) -> Dict[str, Any]:
    """Drag mouse smoothly from start coordinates to end coordinates."""
    if not confirmed:
        coord_type = "normalized [0-1000]" if normalized else "pixels"
        target_str = f" in window '{window_title}'" if window_title else ""
        return {
            "success": False,
            "requires_confirmation": True,
            "tool": "drag_mouse",
            "title": "Mouse Drag Approval Required",
            "action": "Drag Mouse Cursor",
            "start": f"({start_x}, {start_y})",
            "end": f"({end_x}, {end_y}) ({coord_type})",
            "window": window_title or "Full Desktop",
            "duration": f"{duration_seconds}s",
            "risk": f"Will drag from ({start_x}, {start_y}) to ({end_x}, {end_y}){target_str}.",
            "message": f"User confirmation required to drag from ({start_x}, {start_y}) to ({end_x}, {end_y})."
        }

    res = input_simulator.drag(
        start_x=start_x,
        start_y=start_y,
        end_x=end_x,
        end_y=end_y,
        duration=duration_seconds,
        normalized=normalized,
        window_title=window_title
    )
    d = res.to_dict()
    d["result"] = d
    return d


def handle_scroll_at(
    wheel_units: int,
    horizontal: bool = False,
    x: Optional[int] = None,
    y: Optional[int] = None,
    normalized: bool = True,
    window_title: Optional[str] = None,
    confirmed: bool = False
) -> Dict[str, Any]:
    """Scroll mouse wheel (vertical or horizontal) at designated position."""
    if not confirmed:
        direction = "horizontal" if horizontal else "vertical"
        pos_str = f" at ({x}, {y})" if (x is not None and y is not None) else " at current position"
        target_str = f" in '{window_title}'" if window_title else ""
        return {
            "success": False,
            "requires_confirmation": True,
            "tool": "scroll_at",
            "title": "Mouse Scroll Approval Required",
            "action": f"Scroll Wheel ({direction})",
            "units": f"{wheel_units} ticks",
            "position": pos_str,
            "window": window_title or "Active Window",
            "risk": f"Will scroll {direction} by {wheel_units} ticks{pos_str}{target_str}.",
            "message": f"User confirmation required to scroll {wheel_units} ticks{pos_str}."
        }

    res = input_simulator.scroll(
        wheel_units=wheel_units,
        horizontal=horizontal,
        x=x,
        y=y,
        normalized=normalized,
        window_title=window_title
    )
    d = res.to_dict()
    d["result"] = d
    return d


def handle_type_desktop_text(
    text: str,
    window_title: Optional[str] = None,
    confirmed: bool = False
) -> Dict[str, Any]:
    """Type text into active or target window without sending auto-Enter."""
    if not confirmed:
        preview = text[:12] + "..." if len(text) > 12 else text
        target_str = f" into window '{window_title}'" if window_title else " into active window"
        return {
            "success": False,
            "requires_confirmation": True,
            "tool": "type_desktop_text",
            "title": "Keyboard Typing Approval Required",
            "action": "Type Desktop Text",
            "preview": preview,
            "characters": len(text),
            "window": window_title or "Active Window",
            "risk": f"Will physically type {len(text)} characters{target_str}.",
            "message": f"User confirmation required to type text (Preview: '{preview}'){target_str}."
        }

    res = input_simulator.type_text(text=text, window_title=window_title)
    d = res.to_dict()
    d["result"] = d
    return d


def handle_press_desktop_key(
    key: str,
    window_title: Optional[str] = None,
    approved_key_combination: Optional[str] = None,
    confirmed: bool = False
) -> Dict[str, Any]:
    """Send an approved keyboard key to target or active window."""
    key_norm = key.strip().lower()
    from ..automation.actions.input_simulator import SENSITIVE_KEYS
    if (key_norm in SENSITIVE_KEYS or not confirmed) and not approved_key_combination:
        target_str = f" to window '{window_title}'" if window_title else " to active window"
        return {
            "success": False,
            "requires_confirmation": True,
            "tool": "press_desktop_key",
            "title": "Keyboard Key Approval Required",
            "action": f"Press Key '{key}'",
            "key": key,
            "window": window_title or "Active Window",
            "risk": f"Will physically press key '{key}'{target_str}.",
            "message": f"User confirmation required to press key '{key}'{target_str}."
        }

    res = input_simulator.press_key(key=key, window_title=window_title, approved=True)
    d = res.to_dict()
    d["result"] = d
    return d


def handle_trigger_emergency_stop() -> Dict[str, Any]:
    """Immediately halt all desktop automation, release held inputs, and lock actions."""
    status = emergency_stop.trigger_stop("User explicitly triggered emergency stop via tool.")
    return {
        "success": True,
        "message": status["message"],
        "result": status,
        "data": status
    }


def handle_reset_emergency_stop(confirmed: bool = False) -> Dict[str, Any]:
    """Clear the emergency stop state so desktop automation can resume."""
    if not confirmed:
        return {
            "success": False,
            "requires_confirmation": True,
            "tool": "reset_emergency_stop",
            "title": "Reset Emergency Stop Confirmation Required",
            "action": "Reset Automation Emergency Stop",
            "risk": "Will unlock desktop mouse and keyboard automation.",
            "message": "User confirmation required to reset the emergency stop state."
        }

    status = emergency_stop.reset_stop()
    return {
        "success": True,
        "message": status["message"],
        "result": status,
        "data": status
    }


# ---------------------------------------------------------------------------
# Tool Registration
# ---------------------------------------------------------------------------

def register_desktop_action_tools(registry: ToolRegistry) -> None:
    """Register all Milestone C Desktop Action & Coordinate tools."""

    # 1. get_screen_metrics
    registry.register(ToolDefinition(
        name="get_screen_metrics",
        description="Query screen resolution, DPI scaling factor, virtual multi-monitor bounds, and cursor position.",
        parameters={"type": "object", "properties": {}},
        handler=handle_get_screen_metrics,
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="desktop_actions"
    ))

    # 2. move_mouse
    registry.register(ToolDefinition(
        name="move_mouse",
        description="Move the mouse cursor to screen coordinates (normalized 0-1000 by default or pixels).",
        parameters={
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X coordinate (0-1000 normalized by default, or pixel value)."},
                "y": {"type": "integer", "description": "Y coordinate (0-1000 normalized by default, or pixel value)."},
                "normalized": {"type": "boolean", "description": "Whether coordinates are in normalized 0-1000 range (default: true)."},
                "window_title": {"type": "string", "description": "Optional target window to scope coordinates and focus."},
                "confirmed": {"type": "boolean", "description": "User approval confirmation flag."}
            },
            "required": ["x", "y"]
        },
        handler=handle_move_mouse,
        permission_level=PermissionLevel.CONTROLLED_ACTION,
        category="desktop_actions"
    ))

    # 3. click_at
    registry.register(ToolDefinition(
        name="click_at",
        description="Click at screen coordinates (left, right, or middle button). Normalized 0-1000 by default.",
        parameters={
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X coordinate (0-1000 normalized by default)."},
                "y": {"type": "integer", "description": "Y coordinate (0-1000 normalized by default)."},
                "button": {"type": "string", "enum": ["left", "right", "middle"], "description": "Mouse button (default: left)."},
                "normalized": {"type": "boolean", "description": "Whether coordinates are normalized 0-1000 (default: true)."},
                "window_title": {"type": "string", "description": "Optional target window to focus before clicking."},
                "confirmed": {"type": "boolean", "description": "User approval confirmation flag."}
            },
            "required": ["x", "y"]
        },
        handler=handle_click_at,
        permission_level=PermissionLevel.CONTROLLED_ACTION,
        category="desktop_actions"
    ))

    # 4. double_click_at
    registry.register(ToolDefinition(
        name="double_click_at",
        description="Double-click at screen coordinates. Normalized 0-1000 by default.",
        parameters={
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X coordinate."},
                "y": {"type": "integer", "description": "Y coordinate."},
                "normalized": {"type": "boolean", "description": "Whether coordinates are normalized (default: true)."},
                "window_title": {"type": "string", "description": "Optional target window to focus."},
                "confirmed": {"type": "boolean", "description": "User approval confirmation flag."}
            },
            "required": ["x", "y"]
        },
        handler=handle_double_click_at,
        permission_level=PermissionLevel.CONTROLLED_ACTION,
        category="desktop_actions"
    ))

    # 5. right_click_at
    registry.register(ToolDefinition(
        name="right_click_at",
        description="Right-click at screen coordinates to open context menus.",
        parameters={
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X coordinate."},
                "y": {"type": "integer", "description": "Y coordinate."},
                "normalized": {"type": "boolean", "description": "Whether coordinates are normalized (default: true)."},
                "window_title": {"type": "string", "description": "Optional target window to focus."},
                "confirmed": {"type": "boolean", "description": "User approval confirmation flag."}
            },
            "required": ["x", "y"]
        },
        handler=handle_right_click_at,
        permission_level=PermissionLevel.CONTROLLED_ACTION,
        category="desktop_actions"
    ))

    # 6. drag_mouse
    registry.register(ToolDefinition(
        name="drag_mouse",
        description="Drag mouse smoothly from start coordinates to end coordinates.",
        parameters={
            "type": "object",
            "properties": {
                "start_x": {"type": "integer", "description": "Starting X coordinate."},
                "start_y": {"type": "integer", "description": "Starting Y coordinate."},
                "end_x": {"type": "integer", "description": "Ending X coordinate."},
                "end_y": {"type": "integer", "description": "Ending Y coordinate."},
                "duration_seconds": {"type": "number", "description": "Duration of drag motion in seconds (default: 0.5)."},
                "normalized": {"type": "boolean", "description": "Whether coordinates are normalized 0-1000 (default: true)."},
                "window_title": {"type": "string", "description": "Optional target window to focus."},
                "confirmed": {"type": "boolean", "description": "User approval confirmation flag."}
            },
            "required": ["start_x", "start_y", "end_x", "end_y"]
        },
        handler=handle_drag_mouse,
        permission_level=PermissionLevel.CONTROLLED_ACTION,
        category="desktop_actions"
    ))

    # 7. scroll_at
    registry.register(ToolDefinition(
        name="scroll_at",
        description="Scroll the mouse wheel at designated coordinates (positive = up, negative = down).",
        parameters={
            "type": "object",
            "properties": {
                "wheel_units": {"type": "integer", "description": "Wheel scroll ticks (e.g. 3 for up, -3 for down)."},
                "horizontal": {"type": "boolean", "description": "Whether to scroll horizontally instead of vertically (default: false)."},
                "x": {"type": "integer", "description": "Optional X coordinate to hover before scrolling."},
                "y": {"type": "integer", "description": "Optional Y coordinate to hover before scrolling."},
                "normalized": {"type": "boolean", "description": "Whether coordinates are normalized (default: true)."},
                "window_title": {"type": "string", "description": "Optional target window to focus."},
                "confirmed": {"type": "boolean", "description": "User approval confirmation flag."}
            },
            "required": ["wheel_units"]
        },
        handler=handle_scroll_at,
        permission_level=PermissionLevel.CONTROLLED_ACTION,
        category="desktop_actions"
    ))

    # 8. type_desktop_text
    registry.register(ToolDefinition(
        name="type_desktop_text",
        description="Type text directly using simulated physical keystrokes (never sends auto-Enter).",
        parameters={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The exact text to type."},
                "window_title": {"type": "string", "description": "Optional target window to focus before typing."},
                "confirmed": {"type": "boolean", "description": "User approval confirmation flag."}
            },
            "required": ["text"]
        },
        handler=handle_type_desktop_text,
        permission_level=PermissionLevel.CONTROLLED_ACTION,
        category="desktop_actions"
    ))

    # 9. press_desktop_key
    registry.register(ToolDefinition(
        name="press_desktop_key",
        description="Send an approved physical keyboard key or shortcut (Escape, Tab, Enter, Ctrl+S, Ctrl+A, F5).",
        parameters={
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "The key or key combo to press (e.g. 'Escape', 'Tab', 'Ctrl+S')."},
                "window_title": {"type": "string", "description": "Optional target window to focus before keypress."},
                "approved_key_combination": {"type": "string", "description": "Approval flag for sensitive shortcuts."},
                "confirmed": {"type": "boolean", "description": "User approval confirmation flag."}
            },
            "required": ["key"]
        },
        handler=handle_press_desktop_key,
        permission_level=PermissionLevel.CONTROLLED_ACTION,
        category="desktop_actions"
    ))

    # 10. trigger_emergency_stop
    registry.register(ToolDefinition(
        name="trigger_emergency_stop",
        description="Emergency circuit breaker: Immediately halts all desktop automation, releases held keys/buttons, and blocks actions.",
        parameters={"type": "object", "properties": {}},
        handler=handle_trigger_emergency_stop,
        permission_level=PermissionLevel.SAFE_ACTION,
        category="desktop_actions"
    ))

    # 11. reset_emergency_stop
    registry.register(ToolDefinition(
        name="reset_emergency_stop",
        description="Deliberately clear the emergency stop state after an abort to resume automation.",
        parameters={
            "type": "object",
            "properties": {
                "confirmed": {"type": "boolean", "description": "User approval confirmation flag."}
            }
        },
        handler=handle_reset_emergency_stop,
        permission_level=PermissionLevel.CONTROLLED_ACTION,
        category="desktop_actions"
    ))
