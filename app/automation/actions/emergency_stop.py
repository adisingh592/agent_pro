"""
Emergency Stop & Failsafe Controller for Milestone C Desktop Actions.
Provides a global automation circuit breaker that immediately halts input simulation,
releases all held mouse buttons and modifier keys, and blocks new actions until explicitly reset.
"""
import ctypes
import logging
import time
from typing import Optional, Dict, Any

logger = logging.getLogger("PersonalAgent.EmergencyStop")


class EmergencyStopController:
    """Manages the global emergency stop state and failsafe recovery."""

    def __init__(self):
        self._is_stopped: bool = False
        self._stop_reason: Optional[str] = None
        self._stop_timestamp: Optional[float] = None
        self._user32 = ctypes.windll.user32

    @property
    def is_stopped(self) -> bool:
        """Check whether emergency stop is currently active."""
        return self._is_stopped

    @property
    def stop_reason(self) -> Optional[str]:
        return self._stop_reason

    def trigger_stop(self, reason: str = "User initiated emergency stop") -> Dict[str, Any]:
        """
        Immediately activate emergency stop:
        1. Set global stop flag to True.
        2. Release all held mouse buttons.
        3. Release all held modifier keys.
        """
        self._is_stopped = True
        self._stop_reason = reason
        self._stop_timestamp = time.time()
        logger.warning(f"🚨 EMERGENCY STOP TRIGGERED: {reason}")

        # Hardware safety release: synthetic mouse release
        self.release_held_inputs()

        return {
            "emergency_stopped": True,
            "reason": reason,
            "timestamp": self._stop_timestamp,
            "message": "Emergency stop activated. All held keys and buttons released. Automation halted."
        }

    def reset_stop(self) -> Dict[str, Any]:
        """
        Explicitly clear the emergency stop state.
        Must be a deliberate action by the user.
        """
        prev_reason = self._stop_reason
        self._is_stopped = False
        self._stop_reason = None
        self._stop_timestamp = None
        logger.info("Emergency stop has been manually reset by user.")

        return {
            "emergency_stopped": False,
            "previous_reason": prev_reason,
            "message": "Emergency stop successfully reset. Desktop automation is now ready."
        }

    def check_failsafe(self, x: int, y: int) -> bool:
        """
        Failsafe check: If mouse position is at extreme top-left (0,0) or <= 5px,
        triggers emergency stop automatically (PyAutoGUI failsafe standard).
        """
        if x <= 5 and y <= 5:
            self.trigger_stop("Mouse moved to screen corner (0,0) failsafe trigger.")
            return True
        return False

    def release_held_inputs(self) -> None:
        """
        Dispatch Windows API events to release any held mouse buttons and modifier keys.
        Uses SendInput / mouse_event and keybd_event.
        """
        try:
            # Mouse events: MOUSEEVENTF_LEFTUP = 0x0004, RIGHTUP = 0x0010, MIDDLEUP = 0x0040
            self._user32.mouse_event(0x0004, 0, 0, 0, 0)
            self._user32.mouse_event(0x0010, 0, 0, 0, 0)
            self._user32.mouse_event(0x0040, 0, 0, 0, 0)

            # Keyboard events: KEYEVENTF_KEYUP = 0x0002
            # VK_SHIFT = 0x10, VK_CONTROL = 0x11, VK_MENU (Alt) = 0x12, VK_LWIN = 0x5B
            for vk in (0x10, 0x11, 0x12, 0x5B):
                self._user32.keybd_event(vk, 0, 0x0002, 0)
        except Exception as e:
            logger.error(f"Error releasing held inputs during emergency stop: {e}")


# Global singleton instance
emergency_stop = EmergencyStopController()
