"""
UI Element Inspector for Windows Desktop UI Automation.
Traverses the Microsoft UI Automation tree of a target window with depth and element count limits.
Produces compact, token-efficient observations suitable for LLM reasoning.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple

from .automation_models import UIElementInfo, AutomationResult
from .window_manager import window_manager, WindowInfo

logger = logging.getLogger("PersonalAgent.ElementInspector")

# Import uiautomation
try:
    import uiautomation as auto
    HAS_UIA = True
except ImportError:
    HAS_UIA = False
    logger.warning("uiautomation library not available")


class ElementInspector:
    """Inspects accessible controls inside desktop windows."""

    def __init__(self):
        # Configure uiautomation search timeout to be responsive
        if HAS_UIA:
            auto.SetGlobalSearchTimeout(1.5)

    def inspect_window(
        self,
        window_title: str,
        process_name: Optional[str] = None,
        process_id: Optional[int] = None,
        maximum_depth: int = 3,
        maximum_elements: int = 40
    ) -> AutomationResult:
        """
        Inspect the UI elements of a specified window.
        Returns a structured hierarchy of UIElementInfo and a compact observation summary.
        """
        if not HAS_UIA:
            return AutomationResult(
                success=False,
                message="Windows UI Automation backend is not available.",
                error="UIA_BACKEND_MISSING"
            )

        win = window_manager.find_window(window_title, process_name, process_id)
        if not win:
            return AutomationResult(
                success=False,
                message=f"Window matching '{window_title}' could not be found.",
                error="WINDOW_NOT_FOUND"
            )

        try:
            # Bind to UIA control via NativeWindowHandle
            root_ctrl = auto.ControlFromHandle(win.hwnd)
            if not root_ctrl or not root_ctrl.Exists(0, 0):
                # Fallback search by Name or ClassName
                root_ctrl = auto.WindowControl(searchDepth=2, Name=win.window_title)
                if not root_ctrl.Exists(0.5, 0):
                    return AutomationResult(
                        success=False,
                        message=f"Could not bind UI Automation to window '{win.window_title}' (HWND: {win.hwnd}).",
                        error="UIA_BIND_FAILED"
                    )

            elements_visited = [0]
            root_info = self._extract_element_info(root_ctrl, depth=0)
            self._traverse_tree(
                root_ctrl,
                root_info,
                current_depth=1,
                max_depth=maximum_depth,
                max_elements=maximum_elements,
                visited_counter=elements_visited
            )

            is_truncated = (elements_visited[0] >= maximum_elements)
            compact_summary = self.generate_compact_observation(win, root_info, is_truncated)

            return AutomationResult(
                success=True,
                message=f"Successfully inspected window '{win.window_title}' ({elements_visited[0]} elements detected).",
                data={
                    "window": win.to_dict(),
                    "element_count": elements_visited[0],
                    "is_truncated": is_truncated,
                    "tree": root_info.to_dict(include_children=True),
                    "compact_observation": compact_summary
                }
            )
        except Exception as e:
            logger.error(f"Error inspecting window '{win.window_title}': {e}", exc_info=True)
            return AutomationResult(
                success=False,
                message=f"Failed to inspect window '{win.window_title}': {str(e)}",
                error=str(e)
            )

    def _extract_element_info(self, ctrl: Any, depth: int) -> UIElementInfo:
        """Extract standard properties from an individual UIA control."""
        name = ""
        control_type = "Unknown"
        automation_id = ""
        class_name = ""
        is_enabled = True
        is_visible = True
        is_focused = False
        bounds_dict = None
        val_str = None

        try:
            name = ctrl.Name or ""
        except Exception:
            pass

        try:
            control_type = ctrl.ControlTypeName or "Control"
        except Exception:
            pass

        try:
            automation_id = ctrl.AutomationId or ""
        except Exception:
            pass

        try:
            class_name = ctrl.ClassName or ""
        except Exception:
            pass

        try:
            is_enabled = bool(ctrl.IsEnabled)
        except Exception:
            pass

        try:
            is_visible = not bool(ctrl.IsOffscreen)
        except Exception:
            pass

        try:
            is_focused = bool(ctrl.HasKeyboardFocus)
        except Exception:
            pass

        try:
            rect = ctrl.BoundingRectangle
            if rect:
                bounds_dict = {
                    "left": rect.left,
                    "top": rect.top,
                    "right": rect.right,
                    "bottom": rect.bottom,
                    "width": rect.width(),
                    "height": rect.height()
                }
        except Exception:
            pass

        # Try extracting value if supported
        try:
            val_pattern = ctrl.GetValuePattern()
            if val_pattern:
                # Mask potential password fields
                if "password" in name.lower() or "password" in automation_id.lower():
                    val_str = "********"
                else:
                    val_str = val_pattern.Value
        except Exception:
            pass

        return UIElementInfo(
            name=name,
            control_type=control_type,
            automation_id=automation_id,
            class_name=class_name,
            enabled=is_enabled,
            visible=is_visible,
            focused=is_focused,
            bounds=bounds_dict,
            value=val_str,
            depth=depth
        )

    def _traverse_tree(
        self,
        ctrl: Any,
        parent_info: UIElementInfo,
        current_depth: int,
        max_depth: int,
        max_elements: int,
        visited_counter: List[int]
    ) -> None:
        """Recursively inspect child controls with depth and count bounds."""
        if current_depth > max_depth or visited_counter[0] >= max_elements:
            return

        try:
            children = ctrl.GetChildren()
        except Exception:
            return

        for child in children:
            if visited_counter[0] >= max_elements:
                break

            try:
                # Skip invisible layout filler panes with no name
                c_name = child.Name or ""
                c_type = child.ControlTypeName or ""
                if not c_name and c_type in ("PaneControl", "CustomControl", "SeparatorControl"):
                    # Check if it has named grandchildren
                    sub_children = child.GetChildren()
                    if not sub_children:
                        continue

                child_info = self._extract_element_info(child, depth=current_depth)
                visited_counter[0] += 1
                parent_info.children.append(child_info)

                # Recurse
                self._traverse_tree(
                    child,
                    child_info,
                    current_depth=current_depth + 1,
                    max_depth=max_depth,
                    max_elements=max_elements,
                    visited_counter=visited_counter
                )
            except Exception:
                continue

    def generate_compact_observation(
        self,
        win: WindowInfo,
        root_info: UIElementInfo,
        is_truncated: bool = False
    ) -> str:
        """
        Generate a token-efficient text summary of the window interface for LLM context.
        Groups controls into categories (Menus, Buttons, Inputs, Content).
        """
        lines = [
            f"ACTIVE WINDOW: {win.window_title} (Process: {win.process_name}, PID: {win.process_id})",
            f"STATE: {'Visible' if win.visible else 'Hidden'}"
            f"{', Minimized' if win.minimized else ''}{', Maximized' if win.maximized else ''}"
        ]

        # Flatten elements
        flat_elements: List[UIElementInfo] = []
        def _flatten(e: UIElementInfo):
            if e != root_info:
                flat_elements.append(e)
            for ch in e.children:
                _flatten(ch)
        _flatten(root_info)

        if not flat_elements:
            lines.append("CONTROLS: No accessible UI elements detected (application may use custom canvas or Direct3D).")
            return "\n".join(lines)

        buttons = []
        inputs = []
        menus = []
        other_items = []

        for e in flat_elements:
            t_name = e.name.strip() if e.name else ""
            ctype = e.control_type.replace("Control", "")
            status_str = " (Disabled)" if not e.enabled else ""
            focus_str = " [FOCUSED]" if e.focused else ""

            if ctype in ("Button", "SplitButton"):
                label = t_name if t_name else e.automation_id or "Unnamed Button"
                buttons.append(f"Button '{label}'{status_str}{focus_str}")
            elif ctype in ("Edit", "Document", "ComboBox"):
                label = t_name if t_name else e.automation_id or "Text Input"
                val_repr = f" (Value: '{e.value}')" if e.value is not None else ""
                inputs.append(f"{ctype} '{label}'{val_repr}{status_str}{focus_str}")
            elif ctype in ("Menu", "MenuBar", "MenuItem"):
                if t_name:
                    menus.append(f"MenuItem '{t_name}'")
            elif t_name and ctype in ("TabItem", "CheckBox", "RadioButton", "Hyperlink", "Text", "ListItem"):
                other_items.append(f"{ctype} '{t_name}'{status_str}{focus_str}")

        lines.append("\nDETECTED UI CONTROLS:")
        if menus:
            lines.append("- Menus: " + ", ".join(menus[:8]))
        if inputs:
            for inp in inputs[:6]:
                lines.append(f"- {inp}")
        if buttons:
            lines.append("- Buttons: " + ", ".join(buttons[:10]))
        if other_items:
            for itm in other_items[:8]:
                lines.append(f"- {itm}")

        if is_truncated:
            lines.append("[Tree truncated: maximum elements limit reached]")

        return "\n".join(lines)


# Global singleton instance
element_inspector = ElementInspector()
