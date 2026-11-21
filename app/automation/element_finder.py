"""
UI Element Finder for Windows Desktop UI Automation.
Searches for specific controls inside a target window using exact, case-insensitive,
substring, and fuzzy matching with ambiguity detection.
"""
import difflib
import logging
from typing import List, Optional, Tuple, Any

from .automation_models import UIElementInfo, ElementMatch, AutomationResult
from .window_manager import window_manager, WindowInfo
from .element_inspector import element_inspector

logger = logging.getLogger("PersonalAgent.ElementFinder")

try:
    import uiautomation as auto
    HAS_UIA = True
except ImportError:
    HAS_UIA = False


class ElementFinder:
    """Finds UI elements in a window matching given query parameters."""

    def find_elements(
        self,
        window_title: str,
        element_name: Optional[str] = None,
        control_type: Optional[str] = None,
        automation_id: Optional[str] = None,
        class_name: Optional[str] = None,
        maximum_results: int = 10
    ) -> AutomationResult:
        """
        Search for UI elements matching the criteria.
        Returns matching elements with confidence scores and ambiguity detection.
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

        # Inspect tree up to depth 4 with up to 100 elements to search broadly
        inspect_res = element_inspector.inspect_window(
            window_title=win.window_title,
            process_id=win.process_id,
            maximum_depth=4,
            maximum_elements=100
        )
        if not inspect_res.success or not inspect_res.data:
            return AutomationResult(
                success=False,
                message=f"Could not inspect controls inside '{win.window_title}': {inspect_res.error}",
                error=inspect_res.error
            )

        # Flatten elements
        root_data = inspect_res.data.get("tree", {})
        flat_elements: List[UIElementInfo] = []

        def _flatten_dict(d: dict):
            # Reconstruct element info
            elem = UIElementInfo(
                name=d.get("name", ""),
                control_type=d.get("control_type", ""),
                automation_id=d.get("automation_id", ""),
                class_name=d.get("class_name", ""),
                enabled=d.get("enabled", True),
                visible=d.get("visible", True),
                focused=d.get("focused", False),
                bounds=d.get("bounds"),
                value=d.get("value"),
                depth=d.get("depth", 0)
            )
            # Skip root window itself
            if elem.name != win.window_title or elem.depth > 0:
                flat_elements.append(elem)
            for ch in d.get("children", []):
                _flatten_dict(ch)

        _flatten_dict(root_data)

        # Perform matching
        matches: List[ElementMatch] = []
        target_name = (element_name or "").strip()
        target_id = (automation_id or "").strip()
        target_type = (control_type or "").strip().lower()
        target_class = (class_name or "").strip().lower()

        # Normalize control type query (e.g. "button" -> "buttoncontrol")
        if target_type and not target_type.endswith("control"):
            target_type_norm = target_type + "control"
        else:
            target_type_norm = target_type

        for elem in flat_elements:
            # Filter by control_type if specified
            elem_type = elem.control_type.lower()
            if target_type and target_type not in elem_type and target_type_norm != elem_type:
                continue

            # Filter by class_name if specified
            if target_class and target_class not in elem.class_name.lower():
                continue

            confidence = 0.0
            match_type = ""

            # Check automation_id match
            if target_id and elem.automation_id:
                if elem.automation_id == target_id:
                    confidence = 1.0
                    match_type = "exact_automation_id"
                elif target_id.lower() in elem.automation_id.lower():
                    confidence = 0.85
                    match_type = "substring_automation_id"

            # Check name match if no ID match yet
            if confidence == 0.0 and target_name and elem.name:
                elem_name = elem.name.strip()
                if elem_name == target_name:
                    confidence = 1.0
                    match_type = "exact_name"
                elif elem_name.lower() == target_name.lower():
                    confidence = 0.95
                    match_type = "case_insensitive_name"
                elif target_name.lower() in elem_name.lower():
                    confidence = 0.80
                    match_type = "substring_name"
                else:
                    # Fuzzy match
                    ratio = difflib.SequenceMatcher(None, target_name.lower(), elem_name.lower()).ratio()
                    if ratio >= 0.55:
                        confidence = round(ratio * 0.9, 2)
                        match_type = "fuzzy_name"

            # If only control_type was searched and matches
            if confidence == 0.0 and not target_name and not target_id and target_type:
                confidence = 0.70
                match_type = "control_type_only"

            if confidence > 0.0:
                matches.append(ElementMatch(element=elem, confidence=confidence, match_type=match_type))

        # Sort matches by confidence descending
        matches.sort(key=lambda m: m.confidence, reverse=True)
        top_matches = matches[:maximum_results]

        if not top_matches:
            return AutomationResult(
                success=True,
                message=f"No UI elements matching '{target_name or target_id or target_type}' were found in '{win.window_title}'.",
                data={
                    "window": win.to_dict(),
                    "matches": [],
                    "match_count": 0,
                    "is_ambiguous": False
                }
            )

        # Ambiguity check: if multiple matches have high/identical confidence
        is_ambiguous = False
        if len(top_matches) > 1:
            first_conf = top_matches[0].confidence
            second_conf = top_matches[1].confidence
            if abs(first_conf - second_conf) <= 0.05 and first_conf >= 0.8:
                is_ambiguous = True

        ambiguity_msg = ""
        if is_ambiguous:
            candidate_names = [f"'{m.element.name}' ({m.element.control_type})" for m in top_matches[:3]]
            ambiguity_msg = f" Ambiguity detected: multiple controls match ({', '.join(candidate_names)})."

        return AutomationResult(
            success=True,
            message=f"Found {len(top_matches)} matching UI element(s) in '{win.window_title}'.{ambiguity_msg}",
            data={
                "window": win.to_dict(),
                "matches": [m.to_dict() for m in top_matches],
                "match_count": len(top_matches),
                "is_ambiguous": is_ambiguous
            }
        )

    def locate_live_control(
        self,
        hwnd: int,
        element_name: Optional[str] = None,
        control_type: Optional[str] = None,
        automation_id: Optional[str] = None,
        match_index: int = 0
    ) -> Optional[Any]:
        """
        Locate the live uiautomation Control object for interaction (clicking/typing).
        Searches within the root window HWND.
        """
        if not HAS_UIA:
            return None

        root = auto.ControlFromHandle(hwnd)
        if not root or not root.Exists(0, 0):
            return None

        # Build search criteria
        kwargs = {"searchDepth": 5}
        if automation_id:
            kwargs["AutomationId"] = automation_id
        if element_name:
            kwargs["Name"] = element_name
        if control_type:
            # Map friendly string to uiautomation class if possible
            c_norm = control_type.replace("Control", "").capitalize() + "Control"
            if hasattr(auto, c_norm):
                ctrl_cls = getattr(auto, c_norm)
                try:
                    candidates = ctrl_cls(searchFromControl=root, **kwargs).GetChildren()
                except Exception:
                    pass

        # Use general walk or find
        try:
            target_name = (element_name or "").strip().lower()
            target_id = (automation_id or "").strip()

            matching_controls = []
            def _find_walk(ctrl, depth):
                if depth > 5:
                    return
                for ch in ctrl.GetChildren():
                    c_name = (ch.Name or "").strip().lower()
                    c_id = ch.AutomationId or ""
                    match = False
                    if target_id and c_id == target_id:
                        match = True
                    elif target_name and (c_name == target_name or target_name in c_name):
                        match = True
                    if match:
                        matching_controls.append(ch)
                    _find_walk(ch, depth + 1)

            _find_walk(root, 1)
            if matching_controls and match_index < len(matching_controls):
                return matching_controls[match_index]
        except Exception as e:
            logger.error(f"Error locating live control in HWND {hwnd}: {e}")

        return None


# Global singleton instance
element_finder = ElementFinder()
