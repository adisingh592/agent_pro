"""
Centralized Filesystem Safety and Path Validation Layer for Personal Agent.
Prevents path traversal, blocks system-critical directories, and validates safe access.
"""
import os
import sys
from pathlib import Path
from typing import Tuple, Optional, Set, List


class FilesystemSafetyError(Exception):
    """Raised when a path safety check fails."""
    pass


class FilesystemSafety:
    """
    Enforces path boundaries and restricts access to sensitive operating system folders.
    """

    # System directory names / prefixes that must never be accessed or modified automatically
    RESTRICTED_DIR_NAMES = {
        "windows",
        "system32",
        "syswow64",
        "program files",
        "program files (x86)",
        "programdata",
        "recovery",
        "$recycle.bin",
        "system volume information",
        "boot",
        "efi"
    }

    # Supported text file extensions for safe reading
    SUPPORTED_TEXT_EXTENSIONS = {
        ".txt", ".py", ".java", ".c", ".cpp", ".h", ".cs",
        ".js", ".ts", ".html", ".css", ".json", ".xml", ".yaml",
        ".yml", ".md", ".sql", ".log", ".bat", ".ps1", ".ini",
        ".cfg", ".toml", ".csv", ".tsv", ".sh", ".rst"
    }

    @classmethod
    def get_user_home_dir(cls) -> Path:
        """Returns the current user home directory."""
        return Path.home().resolve()

    @classmethod
    def get_common_user_dirs(cls) -> List[Path]:
        """Returns standard safe user directory paths (Desktop, Documents, Downloads, Pictures)."""
        home = cls.get_user_home_dir()
        common = [
            home,
            home / "Desktop",
            home / "Documents",
            home / "Downloads",
            home / "Pictures",
            home / "Videos",
            home / "Music"
        ]
        return [p for p in common if p.exists()]

    @classmethod
    def normalize_and_resolve(cls, path_str: str) -> Path:
        """
        Normalizes and resolves a path string into a canonical absolute Path object,
        resolving symlinks and eliminating relative navigation segments (..).
        """
        if not path_str or not isinstance(path_str, str):
            raise FilesystemSafetyError("Path must be a non-empty string.")

        # Strip surrounding quotes if present
        clean_str = path_str.strip().strip("'\"")
        if not clean_str:
            raise FilesystemSafetyError("Path cannot be empty or whitespace.")

        # Expand user ~ if present
        expanded = os.path.expanduser(clean_str)
        # Normalize and resolve real path
        resolved = Path(expanded).resolve()
        return resolved

    @classmethod
    def is_path_restricted(cls, target_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Checks if the resolved path points to or inside a restricted system directory.
        Returns: (is_restricted, reason)
        """
        resolved = target_path.resolve()
        parts = [p.lower() for p in resolved.parts]

        # Check for system partition root directories
        for part in parts:
            if part in cls.RESTRICTED_DIR_NAMES:
                return True, f"Access to system folder '{part}' is restricted for safety."

        # Check Windows directory specifically on Windows
        if os.name == "nt":
            win_dir = os.environ.get("WINDIR") or os.environ.get("SYSTEMROOT")
            if win_dir:
                win_path = Path(win_dir).resolve()
                if resolved == win_path or win_path in resolved.parents:
                    return True, "Access to Windows installation directory is blocked."

            prog_files = os.environ.get("PROGRAMFILES")
            if prog_files:
                pf_path = Path(prog_files).resolve()
                if resolved == pf_path or pf_path in resolved.parents:
                    return True, "Access to Program Files directory is blocked."

            prog_files_x86 = os.environ.get("PROGRAMFILES(X86)")
            if prog_files_x86:
                pfx86_path = Path(prog_files_x86).resolve()
                if resolved == pfx86_path or pfx86_path in resolved.parents:
                    return True, "Access to Program Files (x86) directory is blocked."

            prog_data = os.environ.get("PROGRAMDATA")
            if prog_data:
                pd_path = Path(prog_data).resolve()
                if resolved == pd_path or pd_path in resolved.parents:
                    return True, "Access to ProgramData directory is blocked."

        return False, None

    @classmethod
    def validate_read_path(cls, path_str: str, check_exists: bool = True) -> Path:
        """
        Validates a path intended for reading:
        1. Resolves canonical path.
        2. Ensures it is not within restricted system folders.
        3. If check_exists=True, ensures path exists on disk.
        """
        resolved = cls.normalize_and_resolve(path_str)

        is_restricted, reason = cls.is_path_restricted(resolved)
        if is_restricted:
            raise FilesystemSafetyError(f"Security restriction: {reason}")

        if check_exists and not resolved.exists():
            raise FilesystemSafetyError(f"Path does not exist: '{resolved}'")

        return resolved

    @classmethod
    def validate_write_path(cls, path_str: str, allow_existing: bool = True) -> Path:
        """
        Validates a path intended for writing/creation:
        1. Resolves canonical path.
        2. Ensures it is not within restricted system folders.
        3. Ensures parent directory exists or is valid.
        """
        resolved = cls.normalize_and_resolve(path_str)

        is_restricted, reason = cls.is_path_restricted(resolved)
        if is_restricted:
            raise FilesystemSafetyError(f"Security restriction: {reason}")

        # Ensure parent exists
        parent = resolved.parent
        if not parent.exists():
            raise FilesystemSafetyError(f"Parent directory does not exist: '{parent}'")

        # Check if destination already exists when not allowed
        if not allow_existing and resolved.exists():
            raise FilesystemSafetyError(f"Destination already exists: '{resolved}'")

        return resolved

    @classmethod
    def is_text_file(cls, path: Path) -> bool:
        """Checks if a file extension is in the supported text files list."""
        return path.suffix.lower() in cls.SUPPORTED_TEXT_EXTENSIONS
