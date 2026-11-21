"""
Coordinate Mapper for Milestone C Desktop Actions.
Provides bidirectional mapping between normalized [0, 1000] coordinates and actual screen pixels.
Supports DPI scaling, multi-monitor virtual screen geometry, and window-relative bounding boxes.
"""
import ctypes
import logging
from typing import Optional, Tuple, Dict, Any

from .action_models import Coordinate, NormalizedCoordinate, ScreenMetrics

logger = logging.getLogger("PersonalAgent.CoordinateMapper")

try:
    import win32api
    import win32con
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False


class CoordinateMapper:
    """Calculates and validates desktop coordinates."""

    def __init__(self):
        self._user32 = ctypes.windll.user32

    def get_screen_metrics(self) -> ScreenMetrics:
        """
        Retrieve primary screen resolution, virtual screen geometry (multi-monitor),
        DPI scaling, and current mouse position.
        """
        # Primary monitor dimensions
        # SM_CXSCREEN = 0, SM_CYSCREEN = 1
        primary_w = self._user32.GetSystemMetrics(0) or 1920
        primary_h = self._user32.GetSystemMetrics(1) or 1080

        # Virtual screen dimensions (covers all monitors combined)
        # SM_XVIRTUALSCREEN = 76, SM_YVIRTUALSCREEN = 77, SM_CXVIRTUALSCREEN = 78, SM_CYVIRTUALSCREEN = 79
        virt_x = self._user32.GetSystemMetrics(76)
        virt_y = self._user32.GetSystemMetrics(77)
        virt_w = self._user32.GetSystemMetrics(78) or primary_w
        virt_h = self._user32.GetSystemMetrics(79) or primary_h

        # DPI scale check
        dpi_scale = 1.0
        try:
            # Query DPI for system or monitor if available
            dpi = self._user32.GetDpiForSystem()
            if dpi > 0:
                dpi_scale = dpi / 96.0
        except Exception:
            pass

        # Cursor position check
        cursor_x, cursor_y = None, None
        try:
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            pt = POINT()
            if self._user32.GetCursorPos(ctypes.byref(pt)):
                cursor_x = pt.x
                cursor_y = pt.y
        except Exception:
            pass

        return ScreenMetrics(
            primary_width=primary_w,
            primary_height=primary_h,
            virtual_x=virt_x,
            virtual_y=virt_y,
            virtual_width=virt_w,
            virtual_height=virt_h,
            dpi_scale=dpi_scale,
            cursor_x=cursor_x,
            cursor_y=cursor_y
        )

    def validate_normalized(self, norm_x: float, norm_y: float) -> None:
        """
        Validate that normalized coordinates lie within the [0, 1000] interval.
        Raises ValueError if out of bounds.
        """
        if not (0.0 <= norm_x <= 1000.0) or not (0.0 <= norm_y <= 1000.0):
            raise ValueError(
                f"Normalized coordinates ({norm_x}, {norm_y}) out of range. "
                "Normalized values must be strictly between 0 and 1000."
            )

    def validate_actual(self, actual_x: int, actual_y: int) -> bool:
        """
        Validate that actual coordinates lie within the virtual desktop workspace bounds.
        Supports multi-monitor setups where coordinates may start at negative offsets.
        """
        metrics = self.get_screen_metrics()
        min_x = metrics.virtual_x
        max_x = metrics.virtual_x + metrics.virtual_width
        min_y = metrics.virtual_y
        max_y = metrics.virtual_y + metrics.virtual_height

        return (min_x <= actual_x <= max_x) and (min_y <= actual_y <= max_y)

    def normalized_to_actual(
        self,
        norm_x: float,
        norm_y: float,
        window_bounds: Optional[Tuple[int, int, int, int]] = None,
        metrics: Optional[ScreenMetrics] = None
    ) -> Coordinate:
        """
        Convert normalized [0, 1000] coordinates to physical desktop pixels.
        If window_bounds is provided as (left, top, right, bottom), maps relative
        to the target window rectangle.
        Otherwise, maps relative to the primary display.
        """
        self.validate_normalized(norm_x, norm_y)

        if window_bounds is not None:
            left, top, right, bottom = window_bounds
            width = max(1, right - left)
            height = max(1, bottom - top)

            actual_x = left + int((norm_x / 1000.0) * width)
            actual_y = top + int((norm_y / 1000.0) * height)
            return Coordinate(actual_x, actual_y)

        if metrics is None:
            metrics = self.get_screen_metrics()
        actual_x = int((norm_x / 1000.0) * metrics.primary_width)
        actual_y = int((norm_y / 1000.0) * metrics.primary_height)
        return Coordinate(actual_x, actual_y)

    def actual_to_normalized(
        self,
        actual_x: int,
        actual_y: int,
        window_bounds: Optional[Tuple[int, int, int, int]] = None,
        metrics: Optional[ScreenMetrics] = None
    ) -> NormalizedCoordinate:
        """
        Convert actual desktop pixel coordinates to normalized [0, 1000] values.
        """
        if window_bounds is not None:
            left, top, right, bottom = window_bounds
            width = max(1, right - left)
            height = max(1, bottom - top)

            norm_x = ((actual_x - left) / float(width)) * 1000.0
            norm_y = ((actual_y - top) / float(height)) * 1000.0
            return NormalizedCoordinate(max(0.0, min(1000.0, norm_x)), max(0.0, min(1000.0, norm_y)))

        if metrics is None:
            metrics = self.get_screen_metrics()
        w = max(1, metrics.primary_width)
        h = max(1, metrics.primary_height)

        norm_x = (actual_x / float(w)) * 1000.0
        norm_y = (actual_y / float(h)) * 1000.0
        return NormalizedCoordinate(max(0.0, min(1000.0, norm_x)), max(0.0, min(1000.0, norm_y)))

    def clamp_to_screen(
        self,
        x: int,
        y: int,
        metrics: Optional[ScreenMetrics] = None
    ) -> Tuple[int, int]:
        """Clamp actual pixel coordinates to the virtual desktop bounding box."""
        if metrics is None:
            metrics = self.get_screen_metrics()
        min_x = metrics.virtual_x
        max_x = metrics.virtual_x + metrics.virtual_width
        min_y = metrics.virtual_y
        max_y = metrics.virtual_y + metrics.virtual_height
        clamped_x = max(min_x, min(max_x, x))
        clamped_y = max(min_y, min(max_y, y))
        return clamped_x, clamped_y


# Global singleton instance
coordinate_mapper = CoordinateMapper()


# Module-level convenience functions
def get_screen_metrics() -> ScreenMetrics:
    return coordinate_mapper.get_screen_metrics()

def normalized_to_actual(
    norm_x: float,
    norm_y: float,
    window_bounds: Optional[Tuple[int, int, int, int]] = None,
    metrics: Optional[ScreenMetrics] = None
) -> Coordinate:
    return coordinate_mapper.normalized_to_actual(norm_x, norm_y, window_bounds=window_bounds, metrics=metrics)

def actual_to_normalized(
    actual_x: int,
    actual_y: int,
    window_bounds: Optional[Tuple[int, int, int, int]] = None,
    metrics: Optional[ScreenMetrics] = None
) -> NormalizedCoordinate:
    return coordinate_mapper.actual_to_normalized(actual_x, actual_y, window_bounds=window_bounds, metrics=metrics)

def clamp_to_screen(
    x: int,
    y: int,
    metrics: Optional[ScreenMetrics] = None
) -> Tuple[int, int]:
    return coordinate_mapper.clamp_to_screen(x, y, metrics=metrics)

