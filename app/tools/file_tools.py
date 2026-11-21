"""
File Intelligence and Safe File Operations for Personal Agent Phase 2.2.2.
Implements read-only file queries and controlled, verified file modifications.
"""
import os
import shutil
import time
import fnmatch
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from .filesystem_safety import FilesystemSafety, FilesystemSafetyError
from .tool_registry import ToolDefinition, ToolRegistry
from .tool_permissions import PermissionLevel


# File extension categorization mapping for intelligent file organization
CATEGORY_EXTENSIONS = {
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".ppt", ".pptx", ".xls", ".xlsx", ".csv"},
    "Images": {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Installers": {".exe", ".msi"},
    "Code": {".py", ".java", ".c", ".cpp", ".h", ".cs", ".js", ".ts", ".html", ".css", ".json", ".sql", ".sh", ".bat", ".ps1"}
}


def _format_size(size_bytes: int) -> str:
    """Format bytes into readable units."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


# =====================================================================
# READ-ONLY FILE TOOLS
# =====================================================================

def search_files(directory: str, pattern: str = "*", recursive: bool = True) -> Dict[str, Any]:
    """
    Search for files matching a wildcard pattern inside a directory.
    Limits output to 500 files to prevent unbounded memory growth.
    """
    try:
        dir_path = FilesystemSafety.validate_read_path(directory, check_exists=True)
        if not dir_path.is_dir():
            return {"success": False, "tool": "search_files", "error": f"Path is not a directory: '{directory}'"}

        matched_files = []
        truncated = False
        max_results = 500

        if recursive:
            for root, dirs, files in os.walk(dir_path):
                # Filter out hidden or restricted folders
                dirs[:] = [d for d in dirs if not d.startswith(".") and d.lower() not in FilesystemSafety.RESTRICTED_DIR_NAMES]
                for file_name in files:
                    if fnmatch.fnmatch(file_name, pattern):
                        full_p = os.path.join(root, file_name)
                        matched_files.append(full_p)
                        if len(matched_files) >= max_results:
                            truncated = True
                            break
                if truncated:
                    break
        else:
            for item in dir_path.iterdir():
                if item.is_file() and fnmatch.fnmatch(item.name, pattern):
                    matched_files.append(str(item))
                    if len(matched_files) >= max_results:
                        truncated = True
                        break

        return {
            "success": True,
            "tool": "search_files",
            "result": {
                "directory": str(dir_path),
                "pattern": pattern,
                "count": len(matched_files),
                "truncated": truncated,
                "files": matched_files
            }
        }
    except FilesystemSafetyError as safety_err:
        return {"success": False, "tool": "search_files", "error": str(safety_err)}
    except Exception as exc:
        return {"success": False, "tool": "search_files", "error": f"Error searching files: {str(exc)}"}


def list_directory(directory: str, include_hidden: bool = False) -> Dict[str, Any]:
    """
    List files and folders inside a given directory with size and modification timestamp.
    """
    try:
        dir_path = FilesystemSafety.validate_read_path(directory, check_exists=True)
        if not dir_path.is_dir():
            return {"success": False, "tool": "list_directory", "error": f"Path is not a directory: '{directory}'"}

        entries = []
        for item in dir_path.iterdir():
            if not include_hidden and item.name.startswith("."):
                continue

            try:
                stat = item.stat()
                mtime_str = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                is_dir = item.is_dir()
                size_bytes = stat.st_size if not is_dir else 0

                entries.append({
                    "name": item.name,
                    "type": "directory" if is_dir else "file",
                    "size_bytes": size_bytes,
                    "size_readable": _format_size(size_bytes) if not is_dir else "-",
                    "modified": mtime_str
                })
            except (PermissionError, OSError):
                continue

        # Sort folders first, then files alphabetically
        entries.sort(key=lambda x: (0 if x["type"] == "directory" else 1, x["name"].lower()))

        return {
            "success": True,
            "tool": "list_directory",
            "result": {
                "directory": str(dir_path),
                "total_items": len(entries),
                "items": entries
            }
        }
    except FilesystemSafetyError as safety_err:
        return {"success": False, "tool": "list_directory", "error": str(safety_err)}
    except Exception as exc:
        return {"success": False, "tool": "list_directory", "error": f"Error listing directory: {str(exc)}"}


def get_file_info(path: str) -> Dict[str, Any]:
    """
    Retrieve detailed metadata for a file or folder.
    """
    try:
        target_path = FilesystemSafety.validate_read_path(path, check_exists=True)
        stat = target_path.stat()
        is_dir = target_path.is_dir()
        size_bytes = stat.st_size if not is_dir else 0

        ctime_str = datetime.datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
        mtime_str = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

        ext = target_path.suffix.lower() if not is_dir else ""
        file_type = "Folder" if is_dir else (ext.replace(".", "").upper() + " File" if ext else "File")

        return {
            "success": True,
            "tool": "get_file_info",
            "result": {
                "name": target_path.name,
                "full_path": str(target_path),
                "extension": ext,
                "file_type": file_type,
                "is_directory": is_dir,
                "size_bytes": size_bytes,
                "size_readable": _format_size(size_bytes),
                "created": ctime_str,
                "modified": mtime_str
            }
        }
    except FilesystemSafetyError as safety_err:
        return {"success": False, "tool": "get_file_info", "error": str(safety_err)}
    except Exception as exc:
        return {"success": False, "tool": "get_file_info", "error": f"Error getting file metadata: {str(exc)}"}


def read_text_file(path: str, max_characters: int = 20000) -> Dict[str, Any]:
    """
    Safely read text files up to a specified character limit.
    Enforces text extension check, UTF-8/fallback decoding, and size boundaries.
    """
    try:
        target_path = FilesystemSafety.validate_read_path(path, check_exists=True)
        if target_path.is_dir():
            return {"success": False, "tool": "read_text_file", "error": f"Cannot read directory as text: '{path}'"}

        # Validate file type
        if not FilesystemSafety.is_text_file(target_path):
            return {
                "success": False,
                "tool": "read_text_file",
                "error": f"File '{target_path.name}' has extension '{target_path.suffix}', which is not an approved text file format. Binary file reading is blocked."
            }

        file_size = target_path.stat().st_size
        # Block files larger than 10 MB to prevent memory exhaustion
        if file_size > 10 * 1024 * 1024:
            return {
                "success": False,
                "tool": "read_text_file",
                "error": f"File is too large ({_format_size(file_size)}). Text reading is capped at 10 MB."
            }

        # Attempt UTF-8 with Latin-1 fallback
        content = ""
        encoding_used = "utf-8"
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read(max_characters + 1)
        except UnicodeDecodeError:
            encoding_used = "latin-1"
            with open(target_path, "r", encoding="latin-1") as f:
                content = f.read(max_characters + 1)

        truncated = len(content) > max_characters
        final_text = content[:max_characters]

        return {
            "success": True,
            "tool": "read_text_file",
            "result": {
                "file_path": str(target_path),
                "encoding": encoding_used,
                "character_count": len(final_text),
                "truncated": truncated,
                "content": final_text
            }
        }
    except FilesystemSafetyError as safety_err:
        return {"success": False, "tool": "read_text_file", "error": str(safety_err)}
    except Exception as exc:
        return {"success": False, "tool": "read_text_file", "error": f"Error reading file: {str(exc)}"}


def find_recent_files(directory: str, days: int = 3, recursive: bool = True) -> Dict[str, Any]:
    """
    Find files modified within the past N days inside a specified directory.
    """
    try:
        dir_path = FilesystemSafety.validate_read_path(directory, check_exists=True)
        if not dir_path.is_dir():
            return {"success": False, "tool": "find_recent_files", "error": f"Path is not a directory: '{directory}'"}

        cutoff_timestamp = time.time() - (days * 86400)
        recent_files = []

        if recursive:
            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [d for d in dirs if not d.startswith(".") and d.lower() not in FilesystemSafety.RESTRICTED_DIR_NAMES]
                for f in files:
                    full_p = Path(root) / f
                    try:
                        stat = full_p.stat()
                        if stat.st_mtime >= cutoff_timestamp:
                            recent_files.append({
                                "name": f,
                                "path": str(full_p),
                                "size_bytes": stat.st_size,
                                "size_readable": _format_size(stat.st_size),
                                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                                "_mtime": stat.st_mtime
                            })
                    except (PermissionError, OSError):
                        continue
        else:
            for item in dir_path.iterdir():
                if item.is_file():
                    try:
                        stat = item.stat()
                        if stat.st_mtime >= cutoff_timestamp:
                            recent_files.append({
                                "name": item.name,
                                "path": str(item),
                                "size_bytes": stat.st_size,
                                "size_readable": _format_size(stat.st_size),
                                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                                "_mtime": stat.st_mtime
                            })
                    except (PermissionError, OSError):
                        continue

        # Sort newest first
        recent_files.sort(key=lambda x: x["_mtime"], reverse=True)
        for item in recent_files:
            item.pop("_mtime", None)

        return {
            "success": True,
            "tool": "find_recent_files",
            "result": {
                "directory": str(dir_path),
                "days_threshold": days,
                "count": len(recent_files),
                "files": recent_files[:200]
            }
        }
    except FilesystemSafetyError as safety_err:
        return {"success": False, "tool": "find_recent_files", "error": str(safety_err)}
    except Exception as exc:
        return {"success": False, "tool": "find_recent_files", "error": f"Error finding recent files: {str(exc)}"}


def find_large_files(directory: str, minimum_size_mb: float = 10.0, recursive: bool = True) -> Dict[str, Any]:
    """
    Find files larger than a minimum size threshold (in MB) inside a directory.
    Sorted from largest to smallest.
    """
    try:
        dir_path = FilesystemSafety.validate_read_path(directory, check_exists=True)
        if not dir_path.is_dir():
            return {"success": False, "tool": "find_large_files", "error": f"Path is not a directory: '{directory}'"}

        min_bytes = int(minimum_size_mb * 1024 * 1024)
        large_files = []

        if recursive:
            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [d for d in dirs if not d.startswith(".") and d.lower() not in FilesystemSafety.RESTRICTED_DIR_NAMES]
                for f in files:
                    full_p = Path(root) / f
                    try:
                        stat = full_p.stat()
                        if stat.st_size >= min_bytes:
                            large_files.append({
                                "name": f,
                                "path": str(full_p),
                                "size_bytes": stat.st_size,
                                "size_readable": _format_size(stat.st_size),
                                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                            })
                    except (PermissionError, OSError):
                        continue
        else:
            for item in dir_path.iterdir():
                if item.is_file():
                    try:
                        stat = item.stat()
                        if stat.st_size >= min_bytes:
                            large_files.append({
                                "name": item.name,
                                "path": str(item),
                                "size_bytes": stat.st_size,
                                "size_readable": _format_size(stat.st_size),
                                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                            })
                    except (PermissionError, OSError):
                        continue

        # Sort largest first
        large_files.sort(key=lambda x: x["size_bytes"], reverse=True)

        return {
            "success": True,
            "tool": "find_large_files",
            "result": {
                "directory": str(dir_path),
                "threshold_mb": minimum_size_mb,
                "count": len(large_files),
                "files": large_files[:100]
            }
        }
    except FilesystemSafetyError as safety_err:
        return {"success": False, "tool": "find_large_files", "error": str(safety_err)}
    except Exception as exc:
        return {"success": False, "tool": "find_large_files", "error": f"Error finding large files: {str(exc)}"}


# =====================================================================
# CONTROLLED FILE MODIFICATION TOOLS (MODERATE_WRITE)
# =====================================================================

def copy_file(source: str, destination: str, confirmed: bool = False) -> Dict[str, Any]:
    """
    Copy a file from source to destination.
    Requires user confirmation. Performs post-copy size and existence verification.
    """
    try:
        src_path = FilesystemSafety.validate_read_path(source, check_exists=True)
        if src_path.is_dir():
            return {"success": False, "tool": "copy_file", "error": "Source must be a file, not a directory."}

        dest_candidate = FilesystemSafety.normalize_and_resolve(destination)
        # If destination is an existing directory, copy into it with same filename
        if dest_candidate.is_dir():
            dest_path = dest_candidate / src_path.name
        else:
            dest_path = dest_candidate

        dest_path = FilesystemSafety.validate_write_path(str(dest_path), allow_existing=True)

        # Detect overwrite conflict
        overwrite_warning = dest_path.exists()

        if not confirmed:
            return {
                "success": False,
                "requires_confirmation": True,
                "tool": "copy_file",
                "action": "Copy File",
                "source": str(src_path),
                "destination": str(dest_path),
                "risk": f"File will be duplicated to destination.{' WARNING: Destination file already exists and will be overwritten!' if overwrite_warning else ''}",
                "message": f"User confirmation required to copy '{src_path.name}' to '{dest_path}'."
            }

        # Execute copy operation
        shutil.copy2(src_path, dest_path)

        # POST-OPERATION VERIFICATION
        if not dest_path.exists():
            return {"success": False, "tool": "copy_file", "error": "Verification failed: Destination file was not created."}

        src_size = src_path.stat().st_size
        dest_size = dest_path.stat().st_size
        if src_size != dest_size:
            return {
                "success": False,
                "tool": "copy_file",
                "error": f"Verification failed: Size mismatch. Source ({src_size} bytes) != Destination ({dest_size} bytes)."
            }

        return {
            "success": True,
            "tool": "copy_file",
            "result": {
                "source": str(src_path),
                "destination": str(dest_path),
                "size_copied": _format_size(dest_size),
                "verified": True,
                "status": "Copied and verified successfully."
            }
        }
    except FilesystemSafetyError as safety_err:
        return {"success": False, "tool": "copy_file", "error": str(safety_err)}
    except Exception as exc:
        return {"success": False, "tool": "copy_file", "error": f"Copy failed: {str(exc)}"}


def move_file(source: str, destination: str, confirmed: bool = False) -> Dict[str, Any]:
    """
    Move a file from source to destination.
    Requires user confirmation. Performs post-move verification.
    """
    try:
        src_path = FilesystemSafety.validate_read_path(source, check_exists=True)
        dest_candidate = FilesystemSafety.normalize_and_resolve(destination)

        if dest_candidate.is_dir():
            dest_path = dest_candidate / src_path.name
        else:
            dest_path = dest_candidate

        dest_path = FilesystemSafety.validate_write_path(str(dest_path), allow_existing=True)

        if src_path == dest_path:
            return {"success": False, "tool": "move_file", "error": "Source and destination paths are identical."}

        overwrite_warning = dest_path.exists()

        if not confirmed:
            return {
                "success": False,
                "requires_confirmation": True,
                "tool": "move_file",
                "action": "Move File",
                "source": str(src_path),
                "destination": str(dest_path),
                "risk": f"Source file will be relocated to destination.{' WARNING: Destination file already exists and will be replaced!' if overwrite_warning else ''}",
                "message": f"User confirmation required to move '{src_path.name}' to '{dest_path}'."
            }

        src_size = src_path.stat().st_size if src_path.is_file() else 0

        # Execute move operation
        shutil.move(str(src_path), str(dest_path))

        # POST-OPERATION VERIFICATION
        if not dest_path.exists():
            return {"success": False, "tool": "move_file", "error": "Verification failed: Destination path does not exist."}

        if src_path.exists():
            return {"success": False, "tool": "move_file", "error": "Verification failed: Source file still exists after move."}

        return {
            "success": True,
            "tool": "move_file",
            "result": {
                "source": str(src_path),
                "destination": str(dest_path),
                "size_moved": _format_size(src_size),
                "verified": True,
                "status": "Moved and verified successfully."
            }
        }
    except FilesystemSafetyError as safety_err:
        return {"success": False, "tool": "move_file", "error": str(safety_err)}
    except Exception as exc:
        return {"success": False, "tool": "move_file", "error": f"Move failed: {str(exc)}"}


def rename_file(path: str, new_name: str, confirmed: bool = False) -> Dict[str, Any]:
    """
    Rename a file or directory.
    Requires user confirmation. Blocks directory traversal in new_name.
    """
    try:
        target_path = FilesystemSafety.validate_read_path(path, check_exists=True)

        # Validate that new_name is strictly a single filename, not a path
        clean_new_name = new_name.strip().strip("'\"")
        if not clean_new_name:
            return {"success": False, "tool": "rename_file", "error": "New name cannot be empty."}

        if "/" in clean_new_name or "\\" in clean_new_name or ".." in clean_new_name:
            return {
                "success": False,
                "tool": "rename_file",
                "error": "New name must be a simple filename without path separators or directory traversal."
            }

        dest_path = target_path.parent / clean_new_name

        if dest_path.exists():
            return {"success": False, "tool": "rename_file", "error": f"A file or folder named '{clean_new_name}' already exists in this folder."}

        if not confirmed:
            return {
                "success": False,
                "requires_confirmation": True,
                "tool": "rename_file",
                "action": "Rename File",
                "source": str(target_path),
                "destination": str(dest_path),
                "risk": f"File '{target_path.name}' will be renamed to '{clean_new_name}'.",
                "message": f"User confirmation required to rename '{target_path.name}' to '{clean_new_name}'."
            }

        # Execute rename
        target_path.rename(dest_path)

        # POST-OPERATION VERIFICATION
        if not dest_path.exists():
            return {"success": False, "tool": "rename_file", "error": "Verification failed: Renamed file does not exist."}
        if target_path.exists():
            return {"success": False, "tool": "rename_file", "error": "Verification failed: Original path still exists."}

        return {
            "success": True,
            "tool": "rename_file",
            "result": {
                "old_name": target_path.name,
                "new_name": clean_new_name,
                "full_path": str(dest_path),
                "verified": True,
                "status": "Renamed and verified successfully."
            }
        }
    except FilesystemSafetyError as safety_err:
        return {"success": False, "tool": "rename_file", "error": str(safety_err)}
    except Exception as exc:
        return {"success": False, "tool": "rename_file", "error": f"Rename failed: {str(exc)}"}


def create_directory(path: str, confirmed: bool = False) -> Dict[str, Any]:
    """
    Create a new directory on the filesystem.
    Requires user confirmation if outside default user spaces.
    """
    try:
        resolved = FilesystemSafety.normalize_and_resolve(path)
        is_restricted, reason = FilesystemSafety.is_path_restricted(resolved)
        if is_restricted:
            return {"success": False, "tool": "create_directory", "error": f"Security restriction: {reason}"}

        if resolved.exists():
            return {"success": True, "tool": "create_directory", "result": {"path": str(resolved), "status": "Directory already exists."}}

        if not confirmed:
            return {
                "success": False,
                "requires_confirmation": True,
                "tool": "create_directory",
                "action": "Create Directory",
                "source": "None",
                "destination": str(resolved),
                "risk": f"A new directory will be created at: {resolved}",
                "message": f"User confirmation required to create folder '{resolved.name}'."
            }

        # Execute folder creation
        resolved.mkdir(parents=True, exist_ok=True)

        # POST-OPERATION VERIFICATION
        if not resolved.exists() or not resolved.is_dir():
            return {"success": False, "tool": "create_directory", "error": "Verification failed: Directory was not created."}

        return {
            "success": True,
            "tool": "create_directory",
            "result": {
                "directory_created": str(resolved),
                "verified": True,
                "status": "Directory created and verified successfully."
            }
        }
    except FilesystemSafetyError as safety_err:
        return {"success": False, "tool": "create_directory", "error": str(safety_err)}
    except Exception as exc:
        return {"success": False, "tool": "create_directory", "error": f"Directory creation failed: {str(exc)}"}


# =====================================================================
# SMART FILE ORGANIZATION (PREVIEW & EXECUTION)
# =====================================================================

def organize_files_preview(directory: str) -> Dict[str, Any]:
    """
    Analyzes a directory and generates a proposed organization plan categorized by file type.
    Non-destructive preview only. Does not alter files.
    """
    try:
        dir_path = FilesystemSafety.validate_read_path(directory, check_exists=True)
        if not dir_path.is_dir():
            return {"success": False, "tool": "organize_files_preview", "error": f"Path is not a directory: '{directory}'"}

        plan = {}
        category_counts = {}

        for item in dir_path.iterdir():
            if not item.is_file() or item.name.startswith("."):
                continue

            ext = item.suffix.lower()
            matched_cat = "Other"
            for cat_name, ext_set in CATEGORY_EXTENSIONS.items():
                if ext in ext_set:
                    matched_cat = cat_name
                    break

            if matched_cat not in plan:
                plan[matched_cat] = []
                category_counts[matched_cat] = 0

            plan[matched_cat].append({
                "file_name": item.name,
                "source": str(item),
                "target_folder": matched_cat,
                "target_path": str(dir_path / matched_cat / item.name),
                "size_readable": _format_size(item.stat().st_size)
            })
            category_counts[matched_cat] += 1

        total_files = sum(category_counts.values())

        return {
            "success": True,
            "tool": "organize_files_preview",
            "result": {
                "directory": str(dir_path),
                "total_files": total_files,
                "category_summary": category_counts,
                "plan": plan
            }
        }
    except FilesystemSafetyError as safety_err:
        return {"success": False, "tool": "organize_files_preview", "error": str(safety_err)}
    except Exception as exc:
        return {"success": False, "tool": "organize_files_preview", "error": f"Preview failed: {str(exc)}"}


def organize_files(directory: str, confirmed: bool = False) -> Dict[str, Any]:
    """
    Executes intelligent file organization inside a directory according to extension categories.
    Requires user confirmation before moving files.
    """
    try:
        dir_path = FilesystemSafety.validate_read_path(directory, check_exists=True)
        preview_res = organize_files_preview(directory)
        if not preview_res.get("success"):
            return preview_res

        preview_data = preview_res["result"]
        plan = preview_data["plan"]
        total_files = preview_data["total_files"]

        if total_files == 0:
            return {
                "success": True,
                "tool": "organize_files",
                "result": {"status": "No files found to organize."}
            }

        if not confirmed:
            return {
                "success": False,
                "requires_confirmation": True,
                "tool": "organize_files",
                "action": f"Organize {total_files} Files",
                "source": str(dir_path),
                "destination": f"Subfolders in {dir_path.name} (Documents, Images, etc.)",
                "risk": f"{total_files} files will be categorized and moved into typed subfolders.",
                "message": f"User confirmation required to organize {total_files} files in '{dir_path.name}'."
            }

        # Execute the plan safely
        moved_count = 0
        errors = []

        for category, items in plan.items():
            cat_folder = dir_path / category
            cat_folder.mkdir(exist_ok=True)

            for item in items:
                src = Path(item["source"])
                dest = cat_folder / item["file_name"]

                # Prevent overwriting
                if dest.exists() and dest != src:
                    errors.append(f"Skipped '{item['file_name']}': Destination already exists in '{category}'.")
                    continue

                try:
                    shutil.move(str(src), str(dest))
                    moved_count += 1
                except Exception as m_err:
                    errors.append(f"Failed to move '{item['file_name']}': {str(m_err)}")

        return {
            "success": True,
            "tool": "organize_files",
            "result": {
                "directory": str(dir_path),
                "total_organized": moved_count,
                "warnings": errors,
                "status": f"Successfully organized {moved_count} of {total_files} files into categorized folders."
            }
        }
    except FilesystemSafetyError as safety_err:
        return {"success": False, "tool": "organize_files", "error": str(safety_err)}
    except Exception as exc:
        return {"success": False, "tool": "organize_files", "error": f"Organization failed: {str(exc)}"}


# =====================================================================
# TOOL REGISTRATION HELPER
# =====================================================================

def register_file_tools(registry: ToolRegistry) -> None:
    """Registers all Phase 2.2.2 file intelligence and safe operation tools."""

    # 1. search_files
    registry.register(ToolDefinition(
        name="search_files",
        description="Search for files matching a wildcard pattern (e.g. '*.py' or '*report*') in a directory. Supports recursive search.",
        parameters={
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Starting directory path to search within."},
                "pattern": {"type": "string", "description": "Wildcard pattern such as '*.py', '*notes*', '*.pdf'."},
                "recursive": {"type": "boolean", "description": "Whether to search recursively in subdirectories (default: true)."}
            },
            "required": ["directory"]
        },
        handler=search_files,
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="filesystem"
    ))

    # 2. list_directory
    registry.register(ToolDefinition(
        name="list_directory",
        description="List files and folders inside a directory with their names, types, sizes, and modification timestamps.",
        parameters={
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory path to list."},
                "include_hidden": {"type": "boolean", "description": "Whether to include hidden files (default: false)."}
            },
            "required": ["directory"]
        },
        handler=list_directory,
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="filesystem"
    ))

    # 3. get_file_info
    registry.register(ToolDefinition(
        name="get_file_info",
        description="Retrieve detailed metadata for a file or folder (full path, size, extension, created and modified dates).",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file or folder."}
            },
            "required": ["path"]
        },
        handler=get_file_info,
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="filesystem"
    ))

    # 4. read_text_file
    registry.register(ToolDefinition(
        name="read_text_file",
        description="Safely read the text contents of a code or text file (TXT, PY, JS, TS, HTML, CSS, JSON, MD, SQL, LOG, etc.).",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the text file."},
                "max_characters": {"type": "integer", "description": "Maximum characters to read (default: 20000)."}
            },
            "required": ["path"]
        },
        handler=read_text_file,
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="filesystem"
    ))

    # 5. find_recent_files
    registry.register(ToolDefinition(
        name="find_recent_files",
        description="Find files modified recently (within the last N days) inside a directory.",
        parameters={
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory path to search."},
                "days": {"type": "integer", "description": "Number of days threshold (default: 3)."},
                "recursive": {"type": "boolean", "description": "Search recursively (default: true)."}
            },
            "required": ["directory"]
        },
        handler=find_recent_files,
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="filesystem"
    ))

    # 6. find_large_files
    registry.register(ToolDefinition(
        name="find_large_files",
        description="Find large files exceeding a minimum size (in MB) inside a directory, sorted largest to smallest.",
        parameters={
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory path to search."},
                "minimum_size_mb": {"type": "number", "description": "Minimum file size in megabytes (default: 10.0)."},
                "recursive": {"type": "boolean", "description": "Search recursively (default: true)."}
            },
            "required": ["directory"]
        },
        handler=find_large_files,
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="filesystem"
    ))

    # 7. copy_file
    registry.register(ToolDefinition(
        name="copy_file",
        description="Copy a file to a new destination path. Requires user confirmation. Verifies existence and size after copy.",
        parameters={
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Source file path."},
                "destination": {"type": "string", "description": "Destination file or folder path."},
                "confirmed": {"type": "boolean", "description": "Internal flag indicating user approval."}
            },
            "required": ["source", "destination"]
        },
        handler=copy_file,
        permission_level=PermissionLevel.MODERATE_WRITE,
        category="filesystem"
    ))

    # 8. move_file
    registry.register(ToolDefinition(
        name="move_file",
        description="Move a file from source to destination path. Requires user confirmation. Verifies move operation.",
        parameters={
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Source file path to move."},
                "destination": {"type": "string", "description": "Destination directory or file path."},
                "confirmed": {"type": "boolean", "description": "Internal flag indicating user approval."}
            },
            "required": ["source", "destination"]
        },
        handler=move_file,
        permission_level=PermissionLevel.MODERATE_WRITE,
        category="filesystem"
    ))

    # 9. rename_file
    registry.register(ToolDefinition(
        name="rename_file",
        description="Rename a file or folder in-place. Requires user confirmation. Validates that new_name is not a path injection.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the existing file or folder."},
                "new_name": {"type": "string", "description": "New filename (just the name, not a path)."},
                "confirmed": {"type": "boolean", "description": "Internal flag indicating user approval."}
            },
            "required": ["path", "new_name"]
        },
        handler=rename_file,
        permission_level=PermissionLevel.MODERATE_WRITE,
        category="filesystem"
    ))

    # 10. create_directory
    registry.register(ToolDefinition(
        name="create_directory",
        description="Create a new folder on the filesystem. Requires user confirmation for non-standard locations.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path to create."},
                "confirmed": {"type": "boolean", "description": "Internal flag indicating user approval."}
            },
            "required": ["path"]
        },
        handler=create_directory,
        permission_level=PermissionLevel.MODERATE_WRITE,
        category="filesystem"
    ))

    # 11. organize_files_preview
    registry.register(ToolDefinition(
        name="organize_files_preview",
        description="Generate a preview of how files in a directory will be sorted into typed folders (Documents, Images, Code, etc.). Non-destructive.",
        parameters={
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory path to preview organization for."}
            },
            "required": ["directory"]
        },
        handler=organize_files_preview,
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="filesystem"
    ))

    # 12. organize_files
    registry.register(ToolDefinition(
        name="organize_files",
        description="Sort files in a directory into categorized subfolders (Documents, Images, Videos, Code, etc.). Requires user confirmation.",
        parameters={
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory path to organize."},
                "confirmed": {"type": "boolean", "description": "Internal flag indicating user approval."}
            },
            "required": ["directory"]
        },
        handler=organize_files,
        permission_level=PermissionLevel.MODERATE_WRITE,
        category="filesystem"
    ))
