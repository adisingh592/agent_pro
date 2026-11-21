"""
Window Manager for Windows Desktop UI Automation.
Handles window enumeration, active window detection, window focus, and state queries.
"""
import ctypes
import difflib
import logging
import psutil
from typing import List, Optional, Tuple, Dict, Any

from .automation_models import WindowInfo, AutomationResult

logger = logging.getLogger("PersonalAgent.WindowManager")

# Try importing win32gui/win32process/win32con
try:
    import win32gui
    import win32process
    import win32con
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    logger.warning("pywin32 not available, falling back to ctypes for window management")


class WindowManager:
    """Manages discovery and manipulation of desktop windows."""

    def __init__(self):
        self._user32 = ctypes.windll.user32

    def list_windows(
        self,
        visible_only: bool = True,
        maximum_results: int = 50
    ) -> List[WindowInfo]:
        """
        Enumerate desktop windows.
        Returns a list of WindowInfo objects sorted with active/visible windows first.
        """
        windows: List[WindowInfo] = []

        if HAS_WIN32:
            def enum_handler(hwnd, _):
                try:
                    # Check visibility
                    is_visible = bool(win32gui.IsWindowVisible(hwnd))
                    if visible_only and not is_visible:
                        return True

                    title = win32gui.GetWindowText(hwnd).strip()
                    # Skip empty titles if visible_only requested
                    if visible_only and not title:
                        return True

                    # Get Process ID and name
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    proc_name = ""
                    try:
                        if pid > 0:
                            proc_name = psutil.Process(pid).name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        proc_name = "unknown"

                    is_minimized = bool(win32gui.IsIconic(hwnd))
                    is_maximized = bool(win32gui.IsZoomed(hwnd))
                    class_name = win32gui.GetClassName(hwnd)

                    try:
                        rect = win32gui.GetWindowRect(hwnd)
                    except Exception:
                        rect = (0, 0, 0, 0)

                    windows.append(WindowInfo(
                        window_title=title,
                        process_name=proc_name,
                        process_id=pid,
                        hwnd=hwnd,
                        visible=is_visible,
                        minimized=is_minimized,
                        maximized=is_maximized,
                        bounds=rect,
                        class_name=class_name
                    ))
                except Exception as ex:
                    logger.debug(f"Error inspecting HWND {hwnd}: {ex}")
                return True

            try:
                ctypes.windll.kernel32.SetLastError(0)
                win32gui.EnumWindows(enum_handler, 0)
            except Exception as e:
                logger.debug(f"win32gui EnumWindows completed with notice: {e}")
        else:
            # ctypes fallback
            windows = self._list_windows_ctypes(visible_only)

        # Filter out tooltips, hidden system helpers if visible_only
        if visible_only:
            filtered = []
            for w in windows:
                # Exclude standard invisible background helpers
                if w.class_name in ("Progman", "Shell_TrayWnd", "Windows.UI.Core.CoreWindow") and not w.window_title:
                    continue
                # Exclude windows with zero width and height
                left, top, right, bottom = w.bounds
                if (right - left) <= 0 and (bottom - top) <= 0 and not w.minimized:
                    continue
                filtered.append(w)
            windows = filtered

        return windows[:maximum_results]

    def _list_windows_ctypes(self, visible_only: bool) -> List[WindowInfo]:
        """Fallback window enumeration using standard ctypes."""
        windows: List[WindowInfo] = []
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def enum_cb(hwnd, _):
            try:
                is_visible = bool(self._user32.IsWindowVisible(hwnd))
                if visible_only and not is_visible:
                    return True

                length = self._user32.GetWindowTextLengthW(hwnd)
                if visible_only and length == 0:
                    return True

                buf = ctypes.create_unicode_buffer(length + 1)
                self._user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value.strip()
                if visible_only and not title:
                    return True

                pid = ctypes.c_ulong()
                self._user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                p_id = pid.value
                proc_name = ""
                try:
                    if p_id > 0:
                        proc_name = psutil.Process(p_id).name()
                except Exception:
                    proc_name = "unknown"

                is_minimized = bool(self._user32.IsIconic(hwnd))
                is_maximized = bool(self._user32.IsZoomed(hwnd))

                windows.append(WindowInfo(
                    window_title=title,
                    process_name=proc_name,
                    process_id=p_id,
                    hwnd=hwnd,
                    visible=is_visible,
                    minimized=is_minimized,
                    maximized=is_maximized
                ))
            except Exception:
                pass
            return True

        self._user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        return windows

    def get_active_window(self) -> Optional[WindowInfo]:
        """Retrieve information about the currently active foreground window."""
        hwnd = 0
        if HAS_WIN32:
            hwnd = win32gui.GetForegroundWindow()
        else:
            self._user32.GetForegroundWindow.restype = ctypes.c_void_p
            hwnd = self._user32.GetForegroundWindow()

        if not hwnd:
            return None

        try:
            if HAS_WIN32:
                title = win32gui.GetWindowText(hwnd).strip()
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                is_visible = bool(win32gui.IsWindowVisible(hwnd))
                is_minimized = bool(win32gui.IsIconic(hwnd))
                is_maximized = bool(win32gui.IsZoomed(hwnd))
                class_name = win32gui.GetClassName(hwnd)
                try:
                    rect = win32gui.GetWindowRect(hwnd)
                except Exception:
                    rect = (0, 0, 0, 0)
            else:
                length = self._user32.GetWindowTextLengthW(hwnd)
                buf = ctypes.create_unicode_buffer(length + 1)
                self._user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value.strip()
                p_val = ctypes.c_ulong()
                self._user32.GetWindowThreadProcessId(hwnd, ctypes.byref(p_val))
                pid = p_val.value
                is_visible = bool(self._user32.IsWindowVisible(hwnd))
                is_minimized = bool(self._user32.IsIconic(hwnd))
                is_maximized = bool(self._user32.IsZoomed(hwnd))
                class_name = ""
                rect = (0, 0, 0, 0)

            proc_name = ""
            try:
                if pid > 0:
                    proc_name = psutil.Process(pid).name()
            except Exception:
                proc_name = "unknown"

            return WindowInfo(
                window_title=title,
                process_name=proc_name,
                process_id=pid,
                hwnd=hwnd,
                visible=is_visible,
                minimized=is_minimized,
                maximized=is_maximized,
                bounds=rect,
                class_name=class_name
            )
        except Exception as e:
            logger.error(f"Error getting active window info: {e}")
            return None

    def find_window(
        self,
        window_title: str,
        process_name: Optional[str] = None,
        process_id: Optional[int] = None
    ) -> Optional[WindowInfo]:
        """
        Find a specific window by title, optional process name, or PID.
        Priority:
        1. Exact PID match + title match
        2. Exact title match
        3. Case-insensitive title match
        4. Substring title match
        5. Fuzzy title match (similarity >= 0.6)
        """
        all_windows = self.list_windows(visible_only=False, maximum_results=200)
        target_title = window_title.strip()

        # Filter by PID if specified
        if process_id:
            pid_matches = [w for w in all_windows if w.process_id == process_id]
            if pid_matches:
                # Pick matching title among PID windows
                for w in pid_matches:
                    if target_title.lower() in w.window_title.lower():
                        return w
                return pid_matches[0]

        # Filter by process_name if specified
        candidates = all_windows
        if process_name:
            p_name = process_name.lower().replace(".exe", "")
            matched_by_proc = [
                w for w in all_windows
                if p_name in w.process_name.lower()
            ]
            if matched_by_proc:
                candidates = matched_by_proc

        # 1. Exact title match
        for w in candidates:
            if w.window_title == target_title:
                return w

        # 2. Case-insensitive exact title match
        target_lower = target_title.lower()
        for w in candidates:
            if w.window_title.lower() == target_lower:
                return w

        # 3. Substring match (visible preferred)
        visible_substrings = [
            w for w in candidates
            if target_lower in w.window_title.lower() and w.visible and w.window_title
        ]
        if visible_substrings:
            # Sort by shortest title (closest match)
            visible_substrings.sort(key=lambda x: len(x.window_title))
            return visible_substrings[0]

        # 4. Fallback: fuzzy match on visible windows
        best_match = None
        highest_ratio = 0.0
        for w in candidates:
            if not w.window_title or not w.visible:
                continue
            ratio = difflib.SequenceMatcher(None, target_lower, w.window_title.lower()).ratio()
            if ratio > highest_ratio and ratio >= 0.55:
                highest_ratio = ratio
                best_match = w

        return best_match

    def focus_window(
        self,
        window_title: str,
        process_name: Optional[str] = None,
        process_id: Optional[int] = None
    ) -> AutomationResult:
        """
        Bring target window to the foreground and focus it.
        Restores window if minimized.
        """
        win = self.find_window(window_title, process_name, process_id)
        if not win:
            return AutomationResult(
                success=False,
                message=f"Window '{window_title}' not found on desktop.",
                error="WINDOW_NOT_FOUND"
            )

        hwnd = win.hwnd
        try:
            # If minimized, restore it
            if win.minimized:
                if HAS_WIN32:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                else:
                    self._user32.ShowWindow(hwnd, 9)  # SW_RESTORE = 9

            # Bring to front & set foreground
            if HAS_WIN32:
                # Workaround Windows foreground lock by attaching thread input if needed
                win32gui.BringWindowToTop(hwnd)
                win32gui.SetForegroundWindow(hwnd)
            else:
                self._user32.BringWindowToTop(hwnd)
                self._user32.SetForegroundWindow(hwnd)

            # Verification: check active window
            active = self.get_active_window()
            is_foreground = (active and active.hwnd == hwnd)

            return AutomationResult(
                success=True,
                message=f"Focused window '{win.window_title}' (PID: {win.process_id}).",
                data=win.to_dict(),
                verification={
                    "is_foreground": is_foreground,
                    "target_hwnd": hwnd,
                    "active_hwnd": active.hwnd if active else None
                }
            )
        except Exception as e:
            logger.error(f"Failed to focus window HWND {hwnd}: {e}")
            return AutomationResult(
                success=False,
                message=f"Failed to bring window '{win.window_title}' to foreground: {str(e)}",
                error=str(e)
            )


# Global singleton instance
window_manager = WindowManager()
