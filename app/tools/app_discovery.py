"""
Application Discovery and Name Resolution System for Personal Agent (Phase 2.2.3).
Discovers installed Windows applications from App Paths, Start Menu, Uninstall Registry,
known system utilities, and PATH. Resolves natural-language names with alias matching,
fuzzy scoring, and strict ambiguity guards.
"""
import os
import sys
import time
import shutil
import logging
import difflib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any

logger = logging.getLogger("PersonalAgent.AppDiscovery")

# Windows Registry module (available on Windows)
try:
    import winreg
except ImportError:
    winreg = None


@dataclass
class DiscoveredApplication:
    """Represents a discovered Windows desktop application."""
    name: str                           # Primary standardized display name
    display_name: str                   # Human-readable title
    executable: str                     # Validated path to executable or launch target
    launch_command: str                 # Command or path used to launch
    category: str = "Other"             # Development, Browser, Media, Productivity, System, Other
    source: str = "Unknown"             # App Paths, Start Menu, Registry, Known Builtin, PATH
    aliases: List[str] = field(default_factory=list)
    discovered_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "executable": self.executable,
            "launch_command": self.launch_command,
            "category": self.category,
            "source": self.source,
            "aliases": self.aliases
        }


class ApplicationDiscovery:
    """
    Discovers installed and system applications on Windows with caching.
    Avoids aggressive full-drive scans by inspecting verified registration paths.
    """
    CACHE_TTL_SECONDS = 3600.0  # 1 hour cache TTL

    def __init__(self):
        self._cache: Dict[str, DiscoveredApplication] = {}
        self._last_scan_time: float = 0.0

    def get_applications(self, force_refresh: bool = False) -> Dict[str, DiscoveredApplication]:
        """
        Returns all discovered applications, using cache if still valid.
        """
        now = time.time()
        if not force_refresh and self._cache and (now - self._last_scan_time < self.CACHE_TTL_SECONDS):
            return dict(self._cache)

        self._cache = self._scan_all()
        self._last_scan_time = now
        logger.info("Application discovery completed: %d applications cached.", len(self._cache))
        return dict(self._cache)

    def clear_cache(self) -> None:
        """Invalidates the application cache."""
        self._cache.clear()
        self._last_scan_time = 0.0

    def _scan_all(self) -> Dict[str, DiscoveredApplication]:
        """Scan all discovery sources and aggregate results."""
        apps: Dict[str, DiscoveredApplication] = {}

        # 1. Known built-in Windows applications
        self._scan_known_system_apps(apps)

        # 2. Windows App Paths registry keys
        self._scan_registry_app_paths(apps)

        # 3. Start Menu shortcuts
        self._scan_start_menu_shortcuts(apps)

        # 4. Uninstall registry keys
        self._scan_registry_uninstall(apps)

        # 5. Common development & CLI tools from PATH
        self._scan_path_executables(apps)

        return apps

    def _classify_category(self, name: str, exe_path: str) -> str:
        """Classify application category based on name and executable keywords."""
        text = f"{name} {exe_path}".lower()

        dev_kw = ["code", "visual studio", "studio", "ide", "git", "python", "terminal",
                  "powershell", "cmd", "compiler", "debug", "pycharm", "intellij", "docker",
                  "ollama", "sublime", "neovim", "vim", "android studio", "arduino", "morph"]
        for kw in dev_kw:
            if kw in text:
                return "Development"

        browser_kw = ["chrome", "edge", "firefox", "brave", "opera", "safari", "browser", "vivaldi", "tor"]
        for kw in browser_kw:
            if kw in text:
                return "Browser"

        media_kw = ["player", "vlc", "spotify", "music", "video", "photo", "image", "paint",
                    "sound", "audio", "camera", "obs", "blender", "stream", "tv", "movie",
                    "gimp", "photoshop", "camo"]
        for kw in media_kw:
            if kw in text:
                return "Media"

        prod_kw = ["office", "word", "excel", "powerpoint", "outlook", "onenote", "acrobat",
                   "reader", "pdf", "docs", "sheets", "notion", "slack", "teams", "zoom",
                   "calculator", "calc", "notepad", "obsidian", "evernote", "canva", "figma"]
        for kw in prod_kw:
            if kw in text:
                return "Productivity"

        sys_kw = ["explorer", "taskmgr", "settings", "control", "regedit", "cleanmgr", "task manager"]
        for kw in sys_kw:
            if kw in text:
                return "System"

        return "Other"

    def _scan_known_system_apps(self, apps: Dict[str, DiscoveredApplication]) -> None:
        """Register standard Windows system utilities."""
        system_root = os.environ.get("SystemRoot", r"C:\Windows")
        system32 = os.path.join(system_root, "System32")

        known = [
            ("Notepad", os.path.join(system32, "notepad.exe"), "notepad.exe", "Productivity", ["editor", "text editor"]),
            ("Calculator", os.path.join(system32, "calc.exe"), "calc.exe", "Productivity", ["calc", "math"]),
            ("Paint", os.path.join(system32, "mspaint.exe"), "mspaint.exe", "Media", ["mspaint", "draw"]),
            ("File Explorer", os.path.join(system_root, "explorer.exe"), "explorer.exe", "System", ["explorer", "files", "windows explorer"]),
            ("Command Prompt", os.path.join(system32, "cmd.exe"), "cmd.exe", "Development", ["cmd", "dos"]),
            ("PowerShell", os.path.join(system32, "WindowsPowerShell", "v1.0", "powershell.exe"), "powershell.exe", "Development", ["powershell", "ps", "pwsh"]),
            ("Task Manager", os.path.join(system32, "taskmgr.exe"), "taskmgr.exe", "System", ["taskmgr", "tasks"]),
            ("Registry Editor", os.path.join(system_root, "regedit.exe"), "regedit.exe", "System", ["regedit"]),
        ]

        for name, exe, cmd, cat, aliases in known:
            key = name.lower()
            if os.path.exists(exe):
                apps[key] = DiscoveredApplication(
                    name=name,
                    display_name=name,
                    executable=exe,
                    launch_command=cmd,
                    category=cat,
                    source="Known Builtin",
                    aliases=aliases
                )

    def _scan_registry_app_paths(self, apps: Dict[str, DiscoveredApplication]) -> None:
        """Scan HKLM and HKCU App Paths for registered executables."""
        if not winreg:
            return

        hives = [
            (winreg.HKEY_LOCAL_MACHINE, "HKLM App Paths"),
            (winreg.HKEY_CURRENT_USER, "HKCU App Paths")
        ]

        for hive, source_name in hives:
            try:
                with winreg.OpenKey(hive, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths") as key:
                    count = winreg.QueryInfoKey(key)[0]
                    for i in range(count):
                        try:
                            sub_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, sub_name) as subkey:
                                raw_path, _ = winreg.QueryValueEx(subkey, "")
                                if raw_path:
                                    clean_path = raw_path.strip('\"')
                                    if clean_path and os.path.exists(clean_path):
                                        stem = Path(clean_path).stem
                                        # Use stem or subkey without .exe
                                        app_name = sub_name.replace(".exe", "").replace(".EXE", "")
                                        # Normalize special names
                                        display = stem.replace("-", " ").title()
                                        if "code" in app_name.lower():
                                            display = "Visual Studio Code"
                                        elif "chrome" in app_name.lower():
                                            display = "Google Chrome"
                                        elif "brave" in app_name.lower():
                                            display = "Brave"
                                        elif "firefox" in app_name.lower():
                                            display = "Mozilla Firefox"
                                        elif "blender" in app_name.lower():
                                            display = "Blender"

                                        key_id = display.lower()
                                        if key_id not in apps:
                                            apps[key_id] = DiscoveredApplication(
                                                name=display,
                                                display_name=display,
                                                executable=clean_path,
                                                launch_command=clean_path,
                                                category=self._classify_category(display, clean_path),
                                                source=source_name,
                                                aliases=[app_name.lower(), stem.lower()]
                                            )
                        except Exception:
                            continue
            except Exception:
                continue

    def _scan_start_menu_shortcuts(self, apps: Dict[str, DiscoveredApplication]) -> None:
        """Scan User and System Start Menu directories for shortcuts."""
        appdata = os.environ.get("APPDATA", "")
        progdata = os.environ.get("PROGRAMDATA", "")

        start_dirs = []
        if appdata:
            start_dirs.append(os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs"))
        if progdata:
            start_dirs.append(os.path.join(progdata, r"Microsoft\Windows\Start Menu\Programs"))

        ignored_keywords = ["uninstall", "help", "documentation", "readme", "website", "support", "license"]

        for sdir in start_dirs:
            if not os.path.exists(sdir):
                continue

            for root, dirs, files in os.walk(sdir):
                for f in files:
                    if f.lower().endswith(".lnk"):
                        name_without_ext = f[:-4].strip()
                        # Skip uninstallers and documentation links
                        if any(kw in name_without_ext.lower() for kw in ignored_keywords):
                            continue

                        full_path = os.path.join(root, f)
                        key_id = name_without_ext.lower()

                        if key_id not in apps:
                            apps[key_id] = DiscoveredApplication(
                                name=name_without_ext,
                                display_name=name_without_ext,
                                executable=full_path,
                                launch_command=full_path,
                                category=self._classify_category(name_without_ext, full_path),
                                source="Start Menu",
                                aliases=[name_without_ext.lower()]
                            )

    def _scan_registry_uninstall(self, apps: Dict[str, DiscoveredApplication]) -> None:
        """Scan registry uninstall keys to discover installed programs."""
        if not winreg:
            return

        targets = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]

        for hive, reg_path in targets:
            try:
                with winreg.OpenKey(hive, reg_path) as root_key:
                    count = winreg.QueryInfoKey(root_key)[0]
                    for i in range(count):
                        try:
                            sub_key_name = winreg.EnumKey(root_key, i)
                            with winreg.OpenKey(root_key, sub_key_name) as subkey:
                                try:
                                    display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                                except Exception:
                                    continue

                                if not display_name or not isinstance(display_name, str):
                                    continue

                                # Skip drivers, updates, redistributables
                                d_lower = display_name.lower()
                                if any(x in d_lower for x in ["redistributable", "update", "driver", "security intelligence", "kb", "sdk"]):
                                    continue

                                exe_target = None
                                # Check DisplayIcon
                                try:
                                    display_icon, _ = winreg.QueryValueEx(subkey, "DisplayIcon")
                                    if display_icon:
                                        icon_path = display_icon.split(",")[0].strip('\"')
                                        if icon_path.lower().endswith(".exe") and os.path.exists(icon_path):
                                            exe_target = icon_path
                                except Exception:
                                    pass

                                # Check InstallLocation
                                if not exe_target:
                                    try:
                                        inst_loc, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                                        if inst_loc and os.path.isdir(inst_loc):
                                            # Look for exe matching display name
                                            for item in os.listdir(inst_loc):
                                                if item.lower().endswith(".exe"):
                                                    candidate = os.path.join(inst_loc, item)
                                                    if os.path.isfile(candidate):
                                                        exe_target = candidate
                                                        break
                                    except Exception:
                                        pass

                                if exe_target:
                                    key_id = display_name.lower()
                                    if key_id not in apps:
                                        apps[key_id] = DiscoveredApplication(
                                            name=display_name,
                                            display_name=display_name,
                                            executable=exe_target,
                                            launch_command=exe_target,
                                            category=self._classify_category(display_name, exe_target),
                                            source="Uninstall Registry",
                                            aliases=[display_name.lower()]
                                        )
                        except Exception:
                            continue
            except Exception:
                continue

    def _scan_path_executables(self, apps: Dict[str, DiscoveredApplication]) -> None:
        """Find common CLI and developer applications via PATH."""
        common_bins = [
            ("Ollama", "ollama", "Development", ["ollama runner", "ollama service"]),
            ("Windows Terminal", "wt", "Development", ["wt", "terminal"]),
            ("Visual Studio Code", "code", "Development", ["vscode", "code"]),
            ("Google Chrome", "chrome", "Browser", ["chrome"]),
            ("Microsoft Edge", "msedge", "Browser", ["edge"]),
            ("Git", "git", "Development", ["git bash"])
        ]

        for display, bin_name, cat, aliases in common_bins:
            p = shutil.which(bin_name)
            if p and os.path.exists(p):
                key_id = display.lower()
                if key_id not in apps:
                    apps[key_id] = DiscoveredApplication(
                        name=display,
                        display_name=display,
                        executable=p,
                        launch_command=p,
                        category=cat,
                        source="PATH",
                        aliases=aliases
                    )


@dataclass
class ResolutionResult:
    """Outcome of resolving an application name."""
    resolved: bool
    ambiguous: bool
    app: Optional[DiscoveredApplication] = None
    candidates: List[DiscoveredApplication] = field(default_factory=list)
    confidence: float = 0.0
    message: str = ""


class ApplicationResolver:
    """
    Resolves natural-language application requests to discovered applications.
    Handles common aliases, exact matches, fuzzy matches, and detects ambiguity.
    """
    COMMON_ALIASES: Dict[str, str] = {
        "vs code": "Visual Studio Code",
        "vscode": "Visual Studio Code",
        "code": "Visual Studio Code",
        "visual studio code": "Visual Studio Code",
        "chrome": "Google Chrome",
        "google chrome": "Google Chrome",
        "edge": "Microsoft Edge",
        "microsoft edge": "Microsoft Edge",
        "msedge": "Microsoft Edge",
        "firefox": "Mozilla Firefox",
        "mozilla firefox": "Mozilla Firefox",
        "brave": "Brave",
        "brave browser": "Brave",
        "notepad": "Notepad",
        "notepad++": "Notepad++",
        "notepadplusplus": "Notepad++",
        "calc": "Calculator",
        "calculator": "Calculator",
        "windows calculator": "Calculator",
        "explorer": "File Explorer",
        "file explorer": "File Explorer",
        "windows explorer": "File Explorer",
        "terminal": "Windows Terminal",
        "windows terminal": "Windows Terminal",
        "wt": "Windows Terminal",
        "powershell": "PowerShell",
        "pwsh": "PowerShell",
        "ps": "PowerShell",
        "cmd": "Command Prompt",
        "command prompt": "Command Prompt",
        "spotify": "Spotify",
        "discord": "Discord",
        "steam": "Steam",
        "blender": "Blender",
        "android studio": "Android Studio",
        "pycharm": "PyCharm",
        "ollama": "Ollama",
        "task manager": "Task Manager",
        "taskmgr": "Task Manager",
        "paint": "Paint",
        "mspaint": "Paint"
    }

    def __init__(self, discovery: Optional[ApplicationDiscovery] = None):
        self.discovery = discovery or default_app_discovery

    @staticmethod
    def normalize_name(text: str) -> str:
        """Clean and normalize an application query."""
        if not text:
            return ""
        cleaned = text.strip().lower()
        if cleaned.endswith(".exe"):
            cleaned = cleaned[:-4]
        # Remove common extraneous words
        for prefix in ["open ", "launch ", "start ", "run "]:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        return cleaned

    def resolve(self, query: str) -> ResolutionResult:
        """
        Resolve an application name against discovered applications.
        Follows a strict hierarchy:
        1. Normalization
        2. Alias lookup
        3. Exact match
        4. Substring containment
        5. Fuzzy matching with ambiguity check
        """
        normalized = self.normalize_name(query)
        if not normalized:
            return ResolutionResult(
                resolved=False,
                ambiguous=False,
                message="Application name cannot be empty."
            )

        apps = self.discovery.get_applications()
        if not apps:
            return ResolutionResult(
                resolved=False,
                ambiguous=False,
                message="No applications discovered on the system."
            )

        # 1. Alias dictionary check
        target_alias = self.COMMON_ALIASES.get(normalized)
        if target_alias:
            # Look for matching app in discovered list
            for key, app in apps.items():
                if app.name.lower() == target_alias.lower() or target_alias.lower() in [a.lower() for a in app.aliases]:
                    return ResolutionResult(
                        resolved=True,
                        ambiguous=False,
                        app=app,
                        confidence=1.0,
                        message=f"Matched '{query}' via alias to '{app.name}'."
                    )
            # If alias mapped but exact display name search in apps
            for key, app in apps.items():
                if target_alias.lower() in key:
                    return ResolutionResult(
                        resolved=True,
                        ambiguous=False,
                        app=app,
                        confidence=0.95,
                        message=f"Matched '{query}' via alias to '{app.name}'."
                    )

        # 2. Exact match against application key or name
        if normalized in apps:
            return ResolutionResult(
                resolved=True,
                ambiguous=False,
                app=apps[normalized],
                confidence=1.0,
                message=f"Exact match found for '{apps[normalized].name}'."
            )

        for key, app in apps.items():
            if app.name.lower() == normalized or normalized in [a.lower() for a in app.aliases]:
                return ResolutionResult(
                    resolved=True,
                    ambiguous=False,
                    app=app,
                    confidence=1.0,
                    message=f"Exact match found for '{app.name}'."
                )

        # 3. Substring matching & collect candidates
        substring_matches = []
        for key, app in apps.items():
            app_lower = app.name.lower()
            if normalized in app_lower or any(normalized in a.lower() for a in app.aliases):
                substring_matches.append(app)

        # Ambiguity check for substring matches (e.g. "visual studio" matching VS Code and VS Community)
        if len(substring_matches) == 1:
            return ResolutionResult(
                resolved=True,
                ambiguous=False,
                app=substring_matches[0],
                confidence=0.9,
                message=f"Substring match found for '{substring_matches[0].name}'."
            )
        elif len(substring_matches) > 1:
            # Check if one is an exact match for one of the primary words
            candidate_names = [a.name for a in substring_matches[:5]]
            return ResolutionResult(
                resolved=False,
                ambiguous=True,
                candidates=substring_matches[:5],
                confidence=0.5,
                message=f"Multiple applications match '{query}': {', '.join(candidate_names)}. Please specify which one you would like to use."
            )

        # 4. Fuzzy matching with difflib
        scored_candidates: List[Tuple[float, DiscoveredApplication]] = []
        for key, app in apps.items():
            score1 = difflib.SequenceMatcher(None, normalized, app.name.lower()).ratio()
            score2 = max([difflib.SequenceMatcher(None, normalized, a.lower()).ratio() for a in app.aliases], default=0.0)
            score = max(score1, score2)
            if score >= 0.65:
                scored_candidates.append((score, app))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        if not scored_candidates:
            return ResolutionResult(
                resolved=False,
                ambiguous=False,
                message=f"Could not find an installed application matching '{query}'."
            )

        best_score, best_app = scored_candidates[0]

        # Check if top candidate is ambiguous with second candidate
        if len(scored_candidates) > 1:
            second_score, second_app = scored_candidates[1]
            if (best_score - second_score) < 0.08 and best_app.name != second_app.name:
                cand_list = [c[1] for c in scored_candidates[:4]]
                cand_names = [a.name for a in cand_list]
                return ResolutionResult(
                    resolved=False,
                    ambiguous=True,
                    candidates=cand_list,
                    confidence=best_score,
                    message=f"Ambiguous match for '{query}'. Found: {', '.join(cand_names)}. Please clarify which application you mean."
                )

        return ResolutionResult(
            resolved=True,
            ambiguous=False,
            app=best_app,
            confidence=round(best_score, 2),
            message=f"Fuzzy match found for '{best_app.name}' with confidence {best_score:.2f}."
        )


# Global default instances
default_app_discovery = ApplicationDiscovery()
default_app_resolver = ApplicationResolver(default_app_discovery)
