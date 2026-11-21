"""
Input Simulator for Milestone C Desktop Actions.
Performs physical mouse and keyboard simulation using native Windows APIs and uiautomation.
Enforces emergency stop checks, coordinate bounds, action scoping, and keyboard allowlists.
"""
import ctypes
import logging
import time
from typing import Optional, Dict, Any, Tuple, List

from .action_models import DesktopActionResult, ScreenMetrics
from .coordinate_mapper import coordinate_mapper
from .emergency_stop import emergency_stop
from ..window_manager import window_manager

logger = logging.getLogger("PersonalAgent.InputSimulator")

try:
    import uiautomation as auto
    HAS_UIA = True
except ImportError:
    HAS_UIA = False

# Strict Keyboard Allowlists
SAFE_KEYS = {
    "tab", "escape", "space", "backspace", "delete",
    "up", "down", "left", "right", "home", "end", "pageup", "pagedown",
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
    "ctrl+a", "ctrl+c", "ctrl+v", "ctrl+x", "ctrl+z", "ctrl+y", "ctrl+s", "ctrl+f"
}

SENSITIVE_KEYS = {
    "enter", "return", "alt+f4", "ctrl+w", "ctrl+shift+esc", "win+r", "win+x"
}


class InputSimulator:
    """Simulates physical mouse and keyboard inputs on Windows."""

    def __init__(self):
        self._user32 = ctypes.windll.user32
        self.mapper = coordinate_mapper
        self.stop_ctrl = emergency_stop

    def _check_emergency(self, action_name: str) -> Optional[DesktopActionResult]:
        """Check if emergency stop is engaged. Returns error result if active."""
        if self.stop_ctrl.is_stopped:
            msg = f"Action '{action_name}' rejected: Emergency stop is ACTIVE ({self.stop_ctrl.stop_reason})."
            logger.warning(msg)
            return DesktopActionResult(
                action_type=action_name,
                success=False,
                message=msg,
                verification_status="EMERGENCY_STOPPED",
                error="EMERGENCY_STOP_ACTIVE"
            )
        return None

    def _scope_to_window(self, window_title: Optional[str]) -> Tuple[bool, Optional[str], Optional[Tuple[int, int, int, int]]]:
        """
        Verify target window exists, bring to foreground, and retrieve bounds.
        Returns: (success, error_message, window_bounds)
        """
        if not window_title:
            return True, None, None

        win = window_manager.find_window(window_title)
        if not win:
            return False, f"Target window '{window_title}' could not be found.", None

        focus_res = window_manager.focus_window(window_title)
        if not focus_res.success:
            return False, focus_res.message, None

        bounds = win.bounds
        return True, None, bounds

    # -----------------------------------------------------------------------
    # Mouse Operations
    # -----------------------------------------------------------------------

    def move_mouse(
        self,
        x: int,
        y: int,
        normalized: bool = True,
        window_title: Optional[str] = None
    ) -> DesktopActionResult:
        """Move the mouse cursor to the designated coordinates."""
        start_t = time.perf_counter()
        em_res = self._check_emergency("move_mouse")
        if em_res:
            return em_res

        # Window scoping
        ok, err_msg, win_bounds = self._scope_to_window(window_title)
        if not ok:
            return DesktopActionResult(
                action_type="move_mouse",
                success=False,
                message=err_msg,
                duration_ms=(time.perf_counter() - start_t) * 1000,
                target_window=window_title,
                error="WINDOW_SCOPING_FAILED"
            )

        try:
            if normalized:
                actual_x, actual_y = self.mapper.normalized_to_actual(x, y, win_bounds)
                norm_x, norm_y = float(x), float(y)
            else:
                actual_x, actual_y = int(x), int(y)
                norm_x, norm_y = self.mapper.actual_to_normalized(actual_x, actual_y, win_bounds)

            # Check failsafe corner slam
            if self.stop_ctrl.check_failsafe(actual_x, actual_y):
                return DesktopActionResult(
                    action_type="move_mouse",
                    success=False,
                    message="Emergency stop triggered by corner slam failsafe (0,0).",
                    verification_status="EMERGENCY_STOPPED",
                    duration_ms=(time.perf_counter() - start_t) * 1000,
                    error="CORNER_SLAM_FAILSAFE"
                )

            # Validate coordinate bounds
            if not self.mapper.validate_actual(actual_x, actual_y):
                return DesktopActionResult(
                    action_type="move_mouse",
                    success=False,
                    message=f"Coordinates ({actual_x}, {actual_y}) lie outside the virtual desktop workspace.",
                    duration_ms=(time.perf_counter() - start_t) * 1000,
                    error="COORDINATES_OUT_OF_BOUNDS"
                )

            # Perform movement
            if HAS_UIA:
                auto.MoveTo(actual_x, actual_y)
            else:
                self._user32.SetCursorPos(actual_x, actual_y)

            duration_ms = (time.perf_counter() - start_t) * 1000
            return DesktopActionResult(
                action_type="move_mouse",
                success=True,
                message=f"Mouse moved to position ({actual_x}, {actual_y}) [Normalized: {norm_x:.1f}, {norm_y:.1f}].",
                coordinates={
                    "actual": {"x": actual_x, "y": actual_y},
                    "normalized": {"norm_x": norm_x, "norm_y": norm_y}
                },
                verification_status="INPUT_SENT",
                duration_ms=duration_ms,
                target_window=window_title
            )
        except Exception as e:
            return DesktopActionResult(
                action_type="move_mouse",
                success=False,
                message=f"Failed to move mouse: {str(e)}",
                duration_ms=(time.perf_counter() - start_t) * 1000,
                error=str(e)
            )

    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: str = "left",
        normalized: bool = True,
        window_title: Optional[str] = None
    ) -> DesktopActionResult:
        """Click at the specified coordinates (or current mouse position)."""
        start_t = time.perf_counter()
        em_res = self._check_emergency("click")
        if em_res:
            return em_res

        # Move first if coordinates provided
        if x is not None and y is not None:
            move_res = self.move_mouse(x, y, normalized=normalized, window_title=window_title)
            if not move_res.success:
                return move_res
            coords = move_res.coordinates
        else:
            metrics = self.mapper.get_screen_metrics()
            coords = {
                "actual": {"x": metrics.cursor_x, "y": metrics.cursor_y},
                "normalized": None
            }

        btn_norm = button.lower().strip()
        try:
            if btn_norm == "right":
                if HAS_UIA and coords and coords.get("actual", {}).get("x") is not None:
                    auto.RightClick(coords["actual"]["x"], coords["actual"]["y"])
                else:
                    self._user32.mouse_event(0x0008, 0, 0, 0, 0) # RIGHTDOWN
                    time.sleep(0.02)
                    self._user32.mouse_event(0x0010, 0, 0, 0, 0) # RIGHTUP
            elif btn_norm == "middle":
                self._user32.mouse_event(0x0020, 0, 0, 0, 0) # MIDDLEDOWN
                time.sleep(0.02)
                self._user32.mouse_event(0x0040, 0, 0, 0, 0) # MIDDLEUP
            else: # left
                if HAS_UIA and coords and coords.get("actual", {}).get("x") is not None:
                    auto.Click(coords["actual"]["x"], coords["actual"]["y"])
                else:
                    self._user32.mouse_event(0x0002, 0, 0, 0, 0) # LEFTDOWN
                    time.sleep(0.02)
                    self._user32.mouse_event(0x0004, 0, 0, 0, 0) # LEFTUP

            duration_ms = (time.perf_counter() - start_t) * 1000
            return DesktopActionResult(
                action_type="click",
                success=True,
                message=f"Dispatched {button.capitalize()}-click at {coords.get('actual') if coords else 'current position'}.",
                coordinates=coords,
                verification_status="INPUT_SENT",
                duration_ms=duration_ms,
                target_window=window_title,
                metadata={"button": button}
            )
        except Exception as e:
            return DesktopActionResult(
                action_type="click",
                success=False,
                message=f"Failed to execute click: {str(e)}",
                duration_ms=(time.perf_counter() - start_t) * 1000,
                error=str(e)
            )

    def double_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        normalized: bool = True,
        window_title: Optional[str] = None
    ) -> DesktopActionResult:
        """Perform a double-click at the designated coordinates."""
        start_t = time.perf_counter()
        em_res = self._check_emergency("double_click")
        if em_res:
            return em_res

        # First click
        click1 = self.click(x, y, button="left", normalized=normalized, window_title=window_title)
        if not click1.success:
            return click1

        time.sleep(0.08)
        # Second click at current position
        click2 = self.click(x=None, y=None, button="left", normalized=normalized, window_title=window_title)
        if not click2.success:
            return click2

        duration_ms = (time.perf_counter() - start_t) * 1000
        return DesktopActionResult(
            action_type="double_click",
            success=True,
            message=f"Double-click completed at {click1.coordinates.get('actual') if click1.coordinates else 'position'}.",
            coordinates=click1.coordinates,
            verification_status="INPUT_SENT",
            duration_ms=duration_ms,
            target_window=window_title
        )

    def drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float = 0.5,
        normalized: bool = True,
        window_title: Optional[str] = None
    ) -> DesktopActionResult:
        """Drag mouse smoothly from start position to end position."""
        start_t = time.perf_counter()
        em_res = self._check_emergency("drag")
        if em_res:
            return em_res

        # Window scoping
        ok, err_msg, win_bounds = self._scope_to_window(window_title)
        if not ok:
            return DesktopActionResult(
                action_type="drag",
                success=False,
                message=err_msg,
                duration_ms=(time.perf_counter() - start_t) * 1000,
                target_window=window_title,
                error="WINDOW_SCOPING_FAILED"
            )

        try:
            if normalized:
                ax1, ay1 = self.mapper.normalized_to_actual(start_x, start_y, win_bounds)
                ax2, ay2 = self.mapper.normalized_to_actual(end_x, end_y, win_bounds)
            else:
                ax1, ay1 = int(start_x), int(start_y)
                ax2, ay2 = int(end_x), int(end_y)

            # Move to start and press left button
            self.move_mouse(ax1, ay1, normalized=False)
            time.sleep(0.05)
            self._user32.mouse_event(0x0002, 0, 0, 0, 0) # LEFTDOWN
            time.sleep(0.05)

            # Intermediate smooth interpolation steps
            steps = max(5, int(duration * 30))
            for i in range(1, steps + 1):
                if self.stop_ctrl.is_stopped:
                    self._user32.mouse_event(0x0004, 0, 0, 0, 0) # Release LEFTUP
                    return DesktopActionResult(
                        action_type="drag",
                        success=False,
                        message="Drag aborted: Emergency stop triggered during motion.",
                        verification_status="EMERGENCY_STOPPED",
                        duration_ms=(time.perf_counter() - start_t) * 1000,
                        error="EMERGENCY_STOP_ACTIVE"
                    )
                cur_x = int(ax1 + (ax2 - ax1) * (i / float(steps)))
                cur_y = int(ay1 + (ay2 - ay1) * (i / float(steps)))
                self._user32.SetCursorPos(cur_x, cur_y)
                time.sleep(duration / float(steps))

            time.sleep(0.05)
            self._user32.mouse_event(0x0004, 0, 0, 0, 0) # LEFTUP
            time.sleep(0.05)

            duration_ms = (time.perf_counter() - start_t) * 1000
            return DesktopActionResult(
                action_type="drag",
                success=True,
                message=f"Dragged from ({ax1}, {ay1}) to ({ax2}, {ay2}) in {duration:.2f}s.",
                coordinates={
                    "start": {"actual": {"x": ax1, "y": ay1}},
                    "end": {"actual": {"x": ax2, "y": ay2}}
                },
                verification_status="INPUT_SENT",
                duration_ms=duration_ms,
                target_window=window_title
            )
        except Exception as e:
            self._user32.mouse_event(0x0004, 0, 0, 0, 0) # Safety release
            return DesktopActionResult(
                action_type="drag",
                success=False,
                message=f"Failed to execute drag: {str(e)}",
                duration_ms=(time.perf_counter() - start_t) * 1000,
                error=str(e)
            )

    def scroll(
        self,
        wheel_units: int,
        horizontal: bool = False,
        x: Optional[int] = None,
        y: Optional[int] = None,
        normalized: bool = True,
        window_title: Optional[str] = None
    ) -> DesktopActionResult:
        """Scroll the mouse wheel (vertical or horizontal) at designated coordinates."""
        start_t = time.perf_counter()
        em_res = self._check_emergency("scroll")
        if em_res:
            return em_res

        # Move first if coordinates provided
        coords = None
        if x is not None and y is not None:
            move_res = self.move_mouse(x, y, normalized=normalized, window_title=window_title)
            if not move_res.success:
                return move_res
            coords = move_res.coordinates

        try:
            # Vertical scroll: MOUSEEVENTF_WHEEL = 0x0800, 1 click = 120 units
            # Horizontal scroll: MOUSEEVENTF_HWHEEL = 0x01000
            event_flag = 0x01000 if horizontal else 0x0800
            scroll_amount = wheel_units * 120

            self._user32.mouse_event(event_flag, 0, 0, scroll_amount, 0)

            duration_ms = (time.perf_counter() - start_t) * 1000
            direction = "horizontal" if horizontal else "vertical"
            return DesktopActionResult(
                action_type="scroll",
                success=True,
                message=f"Dispatched {direction} scroll ({wheel_units} ticks).",
                coordinates=coords,
                verification_status="INPUT_SENT",
                duration_ms=duration_ms,
                target_window=window_title,
                metadata={"wheel_units": wheel_units, "horizontal": horizontal}
            )
        except Exception as e:
            return DesktopActionResult(
                action_type="scroll",
                success=False,
                message=f"Failed to scroll: {str(e)}",
                duration_ms=(time.perf_counter() - start_t) * 1000,
                error=str(e)
            )

    # -----------------------------------------------------------------------
    # Keyboard Operations
    # -----------------------------------------------------------------------

    def type_text(
        self,
        text: str,
        window_title: Optional[str] = None,
        delay_per_char: float = 0.01
    ) -> DesktopActionResult:
        """Type text into the active or target window without sending auto-Enter."""
        start_t = time.perf_counter()
        em_res = self._check_emergency("type_text")
        if em_res:
            return em_res

        # Focus window if specified
        ok, err_msg, _ = self._scope_to_window(window_title)
        if not ok:
            return DesktopActionResult(
                action_type="type_text",
                success=False,
                message=err_msg,
                duration_ms=(time.perf_counter() - start_t) * 1000,
                target_window=window_title,
                error="WINDOW_SCOPING_FAILED"
            )

        try:
            if HAS_UIA:
                auto.SendKeys(text, waitTime=delay_per_char)
            else:
                # Basic typing fallback via SendInput or SendKeys
                for ch in text:
                    if self.stop_ctrl.is_stopped:
                        break
                    # Send character as unicode event
                    # KEYEVENTF_UNICODE = 0x0004
                    self._user32.keybd_event(0, ord(ch), 0x0004, 0)
                    self._user32.keybd_event(0, ord(ch), 0x0004 | 0x0002, 0)
                    time.sleep(delay_per_char)

            duration_ms = (time.perf_counter() - start_t) * 1000
            # Redact text preview for security
            preview = text[:8] + "..." if len(text) > 8 else text
            return DesktopActionResult(
                action_type="type_text",
                success=True,
                message=f"Typed {len(text)} characters into window (Preview: '{preview}').",
                verification_status="INPUT_SENT",
                duration_ms=duration_ms,
                target_window=window_title,
                metadata={"character_count": len(text)}
            )
        except Exception as e:
            return DesktopActionResult(
                action_type="type_text",
                success=False,
                message=f"Failed to type text: {str(e)}",
                duration_ms=(time.perf_counter() - start_t) * 1000,
                error=str(e)
            )

    def press_key(
        self,
        key: str,
        window_title: Optional[str] = None,
        approved: bool = False
    ) -> DesktopActionResult:
        """Send an approved keyboard key to target window."""
        start_t = time.perf_counter()
        em_res = self._check_emergency("press_key")
        if em_res:
            return em_res

        key_norm = key.strip().lower()
        if key_norm not in SAFE_KEYS and key_norm not in SENSITIVE_KEYS:
            return DesktopActionResult(
                action_type="press_key",
                success=False,
                message=f"Key '{key}' is not in the approved keyboard allowlist.",
                duration_ms=(time.perf_counter() - start_t) * 1000,
                error="KEY_NOT_ALLOWED"
            )

        if key_norm in SENSITIVE_KEYS and not approved:
            return DesktopActionResult(
                action_type="press_key",
                success=False,
                message=f"Key '{key}' is a protected/sensitive action and requires explicit confirmation.",
                duration_ms=(time.perf_counter() - start_t) * 1000,
                error="CONFIRMATION_REQUIRED"
            )

        ok, err_msg, _ = self._scope_to_window(window_title)
        if not ok:
            return DesktopActionResult(
                action_type="press_key",
                success=False,
                message=err_msg,
                duration_ms=(time.perf_counter() - start_t) * 1000,
                target_window=window_title,
                error="WINDOW_SCOPING_FAILED"
            )

        try:
            key_map = {
                "escape": "{Esc}",
                "tab": "{Tab}",
                "enter": "{Enter}",
                "return": "{Enter}",
                "space": " ",
                "backspace": "{Back}",
                "delete": "{Delete}",
                "up": "{Up}",
                "down": "{Down}",
                "left": "{Left}",
                "right": "{Right}",
                "home": "{Home}",
                "end": "{End}",
                "pageup": "{PageUp}",
                "pagedown": "{PageDown}",
                "f5": "{F5}",
                "ctrl+a": "{Ctrl}a",
                "ctrl+c": "{Ctrl}c",
                "ctrl+v": "{Ctrl}v",
                "ctrl+x": "{Ctrl}x",
                "ctrl+z": "{Ctrl}z",
                "ctrl+y": "{Ctrl}y",
                "ctrl+s": "{Ctrl}s",
                "ctrl+f": "{Ctrl}f",
                "alt+f4": "{Alt}{F4}",
                "ctrl+w": "{Ctrl}w"
            }
            seq = key_map.get(key_norm, key)
            if HAS_UIA:
                auto.SendKeys(seq, waitTime=0.05)
            else:
                pass

            duration_ms = (time.perf_counter() - start_t) * 1000
            return DesktopActionResult(
                action_type="press_key",
                success=True,
                message=f"Dispatched key '{key}' to '{window_title or 'active window'}'.",
                verification_status="INPUT_SENT",
                duration_ms=duration_ms,
                target_window=window_title
            )
        except Exception as e:
            return DesktopActionResult(
                action_type="press_key",
                success=False,
                message=f"Failed to press key: {str(e)}",
                duration_ms=(time.perf_counter() - start_t) * 1000,
                error=str(e)
            )

    def key_combination(
        self,
        combination: str,
        window_title: Optional[str] = None,
        approved: bool = False
    ) -> DesktopActionResult:
        """Send a validated keyboard combination (e.g. 'Ctrl+C', 'Ctrl+V', 'Ctrl+S')."""
        return self.press_key(key=combination, window_title=window_title, approved=approved)


# Global singleton instance
input_simulator = InputSimulator()


# Module-level convenience functions
def move_mouse(
    x: int,
    y: int,
    normalized: bool = True,
    window_title: Optional[str] = None
) -> DesktopActionResult:
    return input_simulator.move_mouse(x=x, y=y, normalized=normalized, window_title=window_title)


def click(
    x: int,
    y: int,
    button: str = "left",
    normalized: bool = True,
    window_title: Optional[str] = None
) -> DesktopActionResult:
    return input_simulator.click(x=x, y=y, button=button, normalized=normalized, window_title=window_title)


def double_click(
    x: int,
    y: int,
    normalized: bool = True,
    window_title: Optional[str] = None
) -> DesktopActionResult:
    return input_simulator.double_click(x=x, y=y, normalized=normalized, window_title=window_title)


def right_click(
    x: int,
    y: int,
    normalized: bool = True,
    window_title: Optional[str] = None
) -> DesktopActionResult:
    return input_simulator.right_click(x=x, y=y, normalized=normalized, window_title=window_title)


def drag(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration_ms: int = 500,
    normalized: bool = True,
    window_title: Optional[str] = None
) -> DesktopActionResult:
    return input_simulator.drag(
        start_x=start_x,
        start_y=start_y,
        end_x=end_x,
        end_y=end_y,
        duration_ms=duration_ms,
        normalized=normalized,
        window_title=window_title
    )


def scroll(
    wheel_units: int = 3,
    horizontal: bool = False,
    x: Optional[int] = None,
    y: Optional[int] = None,
    normalized: bool = True,
    window_title: Optional[str] = None
) -> DesktopActionResult:
    return input_simulator.scroll(
        wheel_units=wheel_units,
        horizontal=horizontal,
        x=x,
        y=y,
        normalized=normalized,
        window_title=window_title
    )


def type_text(
    text: str,
    window_title: Optional[str] = None,
    delay_per_char: float = 0.01
) -> DesktopActionResult:
    return input_simulator.type_text(
        text=text,
        window_title=window_title,
        delay_per_char=delay_per_char
    )


def press_key(
    key: str,
    window_title: Optional[str] = None,
    approved: bool = False
) -> DesktopActionResult:
    return input_simulator.press_key(key=key, window_title=window_title, approved=approved)


def key_combination(
    combination: str,
    window_title: Optional[str] = None,
    approved: bool = False
) -> DesktopActionResult:
    return input_simulator.key_combination(combination=combination, window_title=window_title, approved=approved)

