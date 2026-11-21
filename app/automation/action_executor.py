"""
Action Executor for Windows Desktop UI Automation.
Executes clicks, text input, key presses, and element reads using native UI Automation
patterns (InvokePattern, ValuePattern, TogglePattern) with coordinate-based fallback.
Includes state verification and key allowlists.
"""
import logging
import time
from typing import Optional, Dict, Any, List

from .automation_models import AutomationResult
from .window_manager import window_manager
from .element_finder import element_finder

logger = logging.getLogger("PersonalAgent.ActionExecutor")

try:
    import uiautomation as auto
    HAS_UIA = True
except ImportError:
    HAS_UIA = False

# Explicit Key Allowlist
SAFE_KEYS = {
    "escape", "tab", "space", "backspace", "delete",
    "up", "down", "left", "right", "home", "end", "pageup", "pagedown",
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
    "ctrl+a", "ctrl+c", "ctrl+v", "ctrl+x", "ctrl+z", "ctrl+y", "ctrl+s", "ctrl+f"
}

SENSITIVE_KEYS = {
    "enter", "return", "alt+f4", "ctrl+w", "ctrl+shift+esc"
}


class ActionExecutor:
    """Executes validated desktop automation actions."""

    def click_element(
        self,
        window_title: str,
        element_name: str,
        control_type: Optional[str] = None,
        automation_id: Optional[str] = None,
        match_index: int = 0
    ) -> AutomationResult:
        """
        Click / invoke a UI element in the specified window.
        Prioritizes InvokePattern, TogglePattern, and SelectionItemPattern.
        """
        if not HAS_UIA:
            return AutomationResult(
                success=False,
                message="Windows UI Automation backend is not available.",
                error="UIA_BACKEND_MISSING"
            )

        # 1. Focus target window
        focus_res = window_manager.focus_window(window_title)
        if not focus_res.success:
            return focus_res

        win = window_manager.find_window(window_title)
        if not win:
            return AutomationResult(
                success=False,
                message=f"Window '{window_title}' could not be focused.",
                error="WINDOW_NOT_FOUND"
            )

        # 2. Check ambiguity via finder
        find_res = element_finder.find_elements(
            window_title=win.window_title,
            element_name=element_name,
            control_type=control_type,
            automation_id=automation_id
        )
        if not find_res.success or not find_res.data:
            return AutomationResult(
                success=False,
                message=f"Could not find element '{element_name}' in '{win.window_title}'.",
                error="ELEMENT_NOT_FOUND"
            )

        matches = find_res.data.get("matches", [])
        if not matches:
            return AutomationResult(
                success=False,
                message=f"No matching element found for '{element_name}'.",
                error="ELEMENT_NOT_FOUND"
            )

        # Ambiguity alert if multiple high-confidence matches and index 0 default
        if find_res.data.get("is_ambiguous") and match_index == 0 and len(matches) > 1:
            candidate_list = [f"{m['element']['name']} ({m['element']['control_type']})" for m in matches[:4]]
            return AutomationResult(
                success=False,
                message=(
                    f"Ambiguous element target '{element_name}'. Multiple matches found: {', '.join(candidate_list)}. "
                    "Please specify the exact name, automation_id, or match_index."
                ),
                error="AMBIGUOUS_TARGET",
                data={"candidates": matches[:4]}
            )

        # Check enabled state from metadata
        selected_match = matches[min(match_index, len(matches) - 1)]
        elem_meta = selected_match["element"]
        if not elem_meta.get("enabled", True):
            return AutomationResult(
                success=False,
                message=f"Element '{elem_meta.get('name')}' is disabled and cannot be clicked.",
                error="ELEMENT_DISABLED"
            )

        # 3. Locate live control
        live_ctrl = element_finder.locate_live_control(
            hwnd=win.hwnd,
            element_name=elem_meta.get("name"),
            control_type=elem_meta.get("control_type"),
            automation_id=elem_meta.get("automation_id"),
            match_index=match_index
        )

        invoked_via = "pattern"
        try:
            if live_ctrl:
                # Check InvokePattern
                inv_pat = live_ctrl.GetInvokePattern()
                if inv_pat:
                    inv_pat.Invoke()
                    invoked_via = "InvokePattern"
                else:
                    # Check TogglePattern
                    tog_pat = live_ctrl.GetTogglePattern()
                    if tog_pat:
                        tog_pat.Toggle()
                        invoked_via = "TogglePattern"
                    else:
                        # Check SelectionItemPattern
                        sel_pat = live_ctrl.GetSelectionItemPattern()
                        if sel_pat:
                            sel_pat.Select()
                            invoked_via = "SelectionItemPattern"
                        else:
                            # Coordinate click fallback on bounding center
                            rect = live_ctrl.BoundingRectangle
                            if rect and rect.width() > 0 and rect.height() > 0:
                                live_ctrl.Click()
                                invoked_via = "BoundingCenterClick"
                            else:
                                return AutomationResult(
                                    success=False,
                                    message=f"Element '{elem_meta.get('name')}' has no callable pattern and no visible bounding box.",
                                    error="NO_INTERACTION_PATTERN"
                                )
            else:
                # Fallback using bounds from metadata if live control walk failed
                bounds = elem_meta.get("bounds")
                if bounds and bounds.get("width", 0) > 0:
                    cx = bounds["left"] + bounds["width"] // 2
                    cy = bounds["top"] + bounds["height"] // 2
                    auto.Click(cx, cy)
                    invoked_via = "MetadataCoordinateClick"
                else:
                    return AutomationResult(
                        success=False,
                        message=f"Could not bind live interaction handle to '{elem_meta.get('name')}'.",
                        error="LIVE_HANDLE_NOT_FOUND"
                    )

            # Verification: small delay to let UI respond
            time.sleep(0.3)
            active_win = window_manager.get_active_window()

            return AutomationResult(
                success=True,
                message=f"Successfully clicked '{elem_meta.get('name')}' via {invoked_via}.",
                data={
                    "element": elem_meta,
                    "method": invoked_via,
                    "target_window": win.to_dict()
                },
                verification={
                    "active_window_title": active_win.window_title if active_win else None,
                    "active_window_pid": active_win.process_id if active_win else None
                }
            )
        except Exception as e:
            logger.error(f"Error clicking element '{element_name}': {e}", exc_info=True)
            return AutomationResult(
                success=False,
                message=f"Failed to click element '{element_name}': {str(e)}",
                error=str(e)
            )

    def type_into_element(
        self,
        window_title: str,
        element_name: str,
        text: str,
        automation_id: Optional[str] = None,
        match_index: int = 0
    ) -> AutomationResult:
        """
        Enter text into an editable UI control.
        Uses ValuePattern.SetValue() for instant reliable entry, or SendKeys.
        """
        if not HAS_UIA:
            return AutomationResult(
                success=False,
                message="Windows UI Automation backend is not available.",
                error="UIA_BACKEND_MISSING"
            )

        # 1. Focus target window
        focus_res = window_manager.focus_window(window_title)
        if not focus_res.success:
            return focus_res

        win = window_manager.find_window(window_title)
        if not win:
            return AutomationResult(
                success=False,
                message=f"Window '{window_title}' could not be focused.",
                error="WINDOW_NOT_FOUND"
            )

        # 2. Locate live control
        live_ctrl = element_finder.locate_live_control(
            hwnd=win.hwnd,
            element_name=element_name,
            automation_id=automation_id,
            match_index=match_index
        )

        if not live_ctrl:
            return AutomationResult(
                success=False,
                message=f"Text input control '{element_name}' could not be located in '{win.window_title}'.",
                error="ELEMENT_NOT_FOUND"
            )

        try:
            if not live_ctrl.IsEnabled:
                return AutomationResult(
                    success=False,
                    message=f"Element '{live_ctrl.Name}' is disabled and cannot accept text input.",
                    error="ELEMENT_DISABLED"
                )

            # Focus control
            live_ctrl.SetFocus()
            time.sleep(0.1)

            method_used = ""
            val_pattern = live_ctrl.GetValuePattern()
            if val_pattern and not val_pattern.IsReadOnly:
                val_pattern.SetValue(text)
                method_used = "ValuePattern.SetValue"
            else:
                # Type characters directly without sending Enter
                live_ctrl.SendKeys(text, waitTime=0.01)
                method_used = "SendKeys"

            # 3. Verification: Read back value
            read_back = None
            try:
                if val_pattern:
                    read_back = val_pattern.Value
            except Exception:
                pass

            verified = bool(read_back and text in read_back) if read_back else True

            return AutomationResult(
                success=True,
                message=f"Successfully typed into '{live_ctrl.Name or element_name}' via {method_used}.",
                data={
                    "element_name": live_ctrl.Name or element_name,
                    "characters_entered": len(text),
                    "method": method_used
                },
                verification={
                    "read_back_value": read_back,
                    "verified": verified
                }
            )
        except Exception as e:
            logger.error(f"Error typing into element '{element_name}': {e}", exc_info=True)
            return AutomationResult(
                success=False,
                message=f"Failed to enter text into '{element_name}': {str(e)}",
                error=str(e)
            )

    def read_element(
        self,
        window_title: str,
        element_name: str,
        control_type: Optional[str] = None,
        automation_id: Optional[str] = None
    ) -> AutomationResult:
        """
        Read the text content or value of a UI element.
        Masks password and credential controls for security.
        """
        if not HAS_UIA:
            return AutomationResult(
                success=False,
                message="Windows UI Automation backend is not available.",
                error="UIA_BACKEND_MISSING"
            )

        win = window_manager.find_window(window_title)
        if not win:
            return AutomationResult(
                success=False,
                message=f"Window '{window_title}' could not be found.",
                error="WINDOW_NOT_FOUND"
            )

        live_ctrl = element_finder.locate_live_control(
            hwnd=win.hwnd,
            element_name=element_name,
            control_type=control_type,
            automation_id=automation_id
        )

        if not live_ctrl:
            return AutomationResult(
                success=False,
                message=f"Control '{element_name}' could not be located in '{win.window_title}'.",
                error="ELEMENT_NOT_FOUND"
            )

        try:
            name = live_ctrl.Name or ""
            c_type = live_ctrl.ControlTypeName or ""
            is_enabled = bool(live_ctrl.IsEnabled)

            # Password field protection
            is_sensitive = False
            try:
                if getattr(live_ctrl, "IsPassword", False):
                    is_sensitive = True
            except Exception:
                pass

            name_lower = (name + " " + (automation_id or "")).lower()
            if any(k in name_lower for k in ("password", "token", "secret", "cvv", "pin")):
                is_sensitive = True

            if is_sensitive:
                return AutomationResult(
                    success=True,
                    message=f"Element '{name}' is a sensitive password field. Value is masked for safety.",
                    data={
                        "element_name": name,
                        "control_type": c_type,
                        "value": "********",
                        "is_sensitive": True,
                        "enabled": is_enabled
                    }
                )

            # Read value via patterns
            extracted_text = ""
            val_pat = live_ctrl.GetValuePattern()
            if val_pat and val_pat.Value:
                extracted_text = val_pat.Value
            else:
                # Check TextPattern or Name
                extracted_text = name

            return AutomationResult(
                success=True,
                message=f"Read value from '{name}': {extracted_text[:100]}",
                data={
                    "element_name": name,
                    "control_type": c_type,
                    "value": extracted_text,
                    "enabled": is_enabled
                }
            )
        except Exception as e:
            logger.error(f"Error reading element '{element_name}': {e}", exc_info=True)
            return AutomationResult(
                success=False,
                message=f"Failed to read element '{element_name}': {str(e)}",
                error=str(e)
            )

    def press_key(
        self,
        window_title: str,
        key: str,
        approved_key_combination: Optional[str] = None
    ) -> AutomationResult:
        """
        Send a validated key or key combination to the target window.
        Enforces key allowlist and requires confirmation for sensitive combos.
        """
        if not HAS_UIA:
            return AutomationResult(
                success=False,
                message="Windows UI Automation backend is not available.",
                error="UIA_BACKEND_MISSING"
            )

        key_norm = key.strip().lower()

        # Check key allowlist
        if key_norm not in SAFE_KEYS and key_norm not in SENSITIVE_KEYS:
            return AutomationResult(
                success=False,
                message=(
                    f"Key '{key}' is not in the approved keyboard allowlist. "
                    f"Allowed keys include: {', '.join(sorted(SAFE_KEYS)[:12])}..."
                ),
                error="KEY_NOT_ALLOWED"
            )

        # Check sensitive keys
        if key_norm in SENSITIVE_KEYS and not approved_key_combination:
            return AutomationResult(
                success=False,
                message=(
                    f"Key combination '{key}' is sensitive and requires confirmation. "
                    "Please confirm the action."
                ),
                error="CONFIRMATION_REQUIRED"
            )

        # 1. Focus target window
        focus_res = window_manager.focus_window(window_title)
        if not focus_res.success:
            return focus_res

        try:
            # Map friendly key string to uiautomation SendKeys syntax
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

            key_seq = key_map.get(key_norm, key)
            auto.SendKeys(key_seq, waitTime=0.05)

            return AutomationResult(
                success=True,
                message=f"Dispatched key '{key}' to window '{window_title}'.",
                data={
                    "window_title": window_title,
                    "key": key,
                    "sequence": key_seq
                }
            )
        except Exception as e:
            logger.error(f"Error pressing key '{key}': {e}", exc_info=True)
            return AutomationResult(
                success=False,
                message=f"Failed to dispatch key '{key}': {str(e)}",
                error=str(e)
            )


# Global singleton instance
action_executor = ActionExecutor()
