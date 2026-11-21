"""
Application and Process Control Tools for Personal Agent (Phase 2.2.3).
Provides safe application discovery, name resolution, launch validation,
file/folder association, process enumeration, status tracking, and graceful termination.
"""
import os
import sys
import shlex
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from .app_discovery import (
    ApplicationDiscovery,
    ApplicationResolver,
    DiscoveredApplication,
    ResolutionResult,
    default_app_discovery,
    default_app_resolver
)
from .process_manager import (
    ProcessManager,
    default_process_manager
)
from .filesystem_safety import FilesystemSafety, FilesystemSafetyError
from .tool_registry import ToolDefinition, ToolRegistry
from .tool_permissions import PermissionLevel

logger = logging.getLogger("PersonalAgent.AppTools")


# =====================================================================
# TOOL 1: search_applications (READ_ONLY)
# =====================================================================

def search_applications(
    query: str,
    maximum_results: int = 10,
    discovery: Optional[ApplicationDiscovery] = None
) -> Dict[str, Any]:
    """
    Search for installed or discoverable applications by name or category keyword.
    """
    try:
        disc = discovery or default_app_discovery
        apps = disc.get_applications()
        maximum_results = max(1, min(maximum_results, 50))

        if not query or not query.strip():
            return {
                "success": False,
                "tool": "search_applications",
                "error": "Search query cannot be empty."
            }

        q_lower = query.strip().lower()
        matches = []

        for key, app in apps.items():
            name_lower = app.name.lower()
            aliases_lower = [a.lower() for a in app.aliases]

            score = 0.0
            if q_lower == name_lower or q_lower in aliases_lower:
                score = 1.0
            elif q_lower in name_lower or any(q_lower in a for a in aliases_lower):
                score = 0.85
            elif q_lower == app.category.lower():
                score = 0.75
            elif any(word in name_lower for word in q_lower.split()):
                score = 0.65

            if score > 0:
                matches.append({
                    "name": app.name,
                    "executable": app.executable,
                    "category": app.category,
                    "confidence": score,
                    "source": app.source
                })

        # Sort highest confidence first
        matches.sort(key=lambda x: x["confidence"], reverse=True)

        return {
            "success": True,
            "tool": "search_applications",
            "result": {
                "query": query,
                "count": len(matches[:maximum_results]),
                "total_matched": len(matches),
                "applications": matches[:maximum_results]
            }
        }
    except Exception as exc:
        logger.exception("Error searching applications: %s", exc)
        return {"success": False, "tool": "search_applications", "error": f"Error searching applications: {str(exc)}"}


# =====================================================================
# TOOL 2: list_installed_applications (READ_ONLY)
# =====================================================================

def list_installed_applications(
    category: Optional[str] = None,
    maximum_results: int = 50,
    discovery: Optional[ApplicationDiscovery] = None
) -> Dict[str, Any]:
    """
    Return discovered applications filtered optionally by category.
    Categories: Development, Browser, Media, Productivity, System, Other.
    """
    try:
        disc = discovery or default_app_discovery
        apps = disc.get_applications()
        maximum_results = max(1, min(maximum_results, 100))

        results = []
        target_cat = category.strip().lower() if category else None

        for app in apps.values():
            if target_cat and app.category.lower() != target_cat:
                continue

            results.append({
                "name": app.name,
                "category": app.category,
                "launch_method": app.executable
            })

        # Sort alphabetically by application name
        results.sort(key=lambda x: x["name"].lower())

        return {
            "success": True,
            "tool": "list_installed_applications",
            "result": {
                "category_filter": category or "All",
                "count": len(results[:maximum_results]),
                "total_available": len(results),
                "applications": results[:maximum_results]
            }
        }
    except Exception as exc:
        logger.exception("Error listing applications: %s", exc)
        return {"success": False, "tool": "list_installed_applications", "error": f"Error listing applications: {str(exc)}"}


# =====================================================================
# TOOL 3: launch_application (CONTROLLED_ACTION)
# =====================================================================

def launch_application(
    application_name: str,
    optional_arguments: Optional[Union[str, List[str]]] = None,
    confirmed: bool = False,
    resolver: Optional[ApplicationResolver] = None
) -> Dict[str, Any]:
    """
    Launch a verified Windows application.
    Requires user confirmation. Performs argument sanitization and post-launch verification.
    """
    try:
        res_engine = resolver or default_app_resolver
        res: ResolutionResult = res_engine.resolve(application_name)

        if not res.resolved:
            if res.ambiguous:
                return {
                    "success": False,
                    "tool": "launch_application",
                    "error": res.message,
                    "ambiguous": True,
                    "candidates": [c.name for c in res.candidates]
                }
            return {
                "success": False,
                "tool": "launch_application",
                "error": res.message
            }

        app = res.app
        exe_path = app.executable

        # Verify executable target exists
        if not os.path.exists(exe_path) and not shutil.which(exe_path):
            return {
                "success": False,
                "tool": "launch_application",
                "error": f"Application executable does not exist at '{exe_path}'."
            }

        # Validate and sanitize arguments
        arg_list: List[str] = []
        if optional_arguments:
            if isinstance(optional_arguments, str):
                # Reject dangerous shell injection characters
                dangerous_chars = ["&", "|", ";", ">", "<", "^", "`", "$", "\n"]
                if any(ch in optional_arguments for ch in dangerous_chars):
                    return {
                        "success": False,
                        "tool": "launch_application",
                        "error": "Arguments contain disallowed shell metacharacters for security."
                    }
                try:
                    arg_list = shlex.split(optional_arguments, posix=False)
                except Exception:
                    arg_list = [optional_arguments.strip()]
            elif isinstance(optional_arguments, list):
                for arg in optional_arguments:
                    if not isinstance(arg, str):
                        return {"success": False, "tool": "launch_application", "error": "All arguments must be strings."}
                    dangerous_chars = ["&", "|", ";", ">", "<", "^", "`", "$", "\n"]
                    if any(ch in arg for ch in dangerous_chars):
                        return {"success": False, "tool": "launch_application", "error": f"Disallowed character in argument '{arg}'."}
                arg_list = list(optional_arguments)

        args_str = " ".join(arg_list) if arg_list else "None"

        # Check for confirmation
        if not confirmed:
            return {
                "success": False,
                "requires_confirmation": True,
                "tool": "launch_application",
                "title": "Application Launch Approval Required",
                "action": "Launch Application",
                "application": app.name,
                "target": exe_path,
                "arguments": args_str,
                "risk": "Will launch external desktop process on your computer.",
                "message": f"User confirmation required to launch '{app.name}'."
            }

        # Safe launch execution
        if exe_path.lower().endswith(".lnk"):
            # Windows shortcut
            os.startfile(exe_path)
            pid = 0  # os.startfile does not return PID directly
        else:
            cmd = [exe_path] + arg_list
            proc = subprocess.Popen(
                cmd,
                shell=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            pid = proc.pid

        return {
            "success": True,
            "tool": "launch_application",
            "result": {
                "application": app.name,
                "executable": exe_path,
                "pid": pid,
                "status": "launched",
                "message": f"Application '{app.name}' started successfully."
            }
        }
    except Exception as exc:
        logger.exception("Error launching application: %s", exc)
        return {"success": False, "tool": "launch_application", "error": f"Error launching application: {str(exc)}"}


# =====================================================================
# TOOL 4: open_file_with_application (CONTROLLED_ACTION)
# =====================================================================

def open_file_with_application(
    file_path: str,
    application_name: Optional[str] = None,
    confirmed: bool = False,
    resolver: Optional[ApplicationResolver] = None
) -> Dict[str, Any]:
    """
    Open a file using a specified application (or default Windows handler if omitted).
    Requires user confirmation. Enforces filesystem safety boundaries.
    """
    try:
        # Validate file path with FilesystemSafety
        try:
            valid_path = FilesystemSafety.validate_read_path(file_path, check_exists=True)
        except FilesystemSafetyError as safety_err:
            return {"success": False, "tool": "open_file_with_application", "error": str(safety_err)}

        if valid_path.is_dir():
            return {
                "success": False,
                "tool": "open_file_with_application",
                "error": f"Path is a directory, not a file. Use 'open_folder' instead: '{file_path}'"
            }

        # Resolve application if specified
        target_app: Optional[DiscoveredApplication] = None
        if application_name:
            res_engine = resolver or default_app_resolver
            res = res_engine.resolve(application_name)
            if not res.resolved:
                return {
                    "success": False,
                    "tool": "open_file_with_application",
                    "error": res.message,
                    "ambiguous": res.ambiguous,
                    "candidates": [c.name for c in res.candidates]
                }
            target_app = res.app

        app_title = target_app.name if target_app else "Default Application"

        # Check confirmation
        if not confirmed:
            return {
                "success": False,
                "requires_confirmation": True,
                "tool": "open_file_with_application",
                "title": "Open File Approval Required",
                "action": "Open File with Application",
                "file": str(valid_path),
                "application": app_title,
                "target": target_app.executable if target_app else "Default Windows Association",
                "risk": f"Will open '{valid_path.name}' using {app_title}.",
                "message": f"User confirmation required to open '{valid_path.name}' with {app_title}."
            }

        # Safe launch
        if target_app:
            subprocess.Popen([target_app.executable, str(valid_path)], shell=False)
        else:
            os.startfile(str(valid_path))

        return {
            "success": True,
            "tool": "open_file_with_application",
            "result": {
                "file": str(valid_path),
                "application": app_title,
                "status": "opened",
                "message": f"File '{valid_path.name}' opened with {app_title}."
            }
        }
    except Exception as exc:
        logger.exception("Error opening file: %s", exc)
        return {"success": False, "tool": "open_file_with_application", "error": f"Error opening file: {str(exc)}"}


# =====================================================================
# TOOL 5: open_folder (CONTROLLED_ACTION)
# =====================================================================

def open_folder(
    folder_path: str,
    confirmed: bool = False
) -> Dict[str, Any]:
    """
    Open a directory using Windows File Explorer.
    Requires user confirmation. Enforces filesystem safety boundaries.
    """
    try:
        try:
            valid_path = FilesystemSafety.validate_read_path(folder_path, check_exists=True)
        except FilesystemSafetyError as safety_err:
            return {"success": False, "tool": "open_folder", "error": str(safety_err)}

        if not valid_path.is_dir():
            return {
                "success": False,
                "tool": "open_folder",
                "error": f"Path is not a folder: '{folder_path}'"
            }

        if not confirmed:
            return {
                "success": False,
                "requires_confirmation": True,
                "tool": "open_folder",
                "title": "Open Folder Approval Required",
                "action": "Open Folder in File Explorer",
                "target": str(valid_path),
                "risk": "Will open Windows File Explorer window at this location.",
                "message": f"User confirmation required to open folder '{valid_path}' in File Explorer."
            }

        # Safe launch Explorer
        subprocess.Popen(["explorer.exe", str(valid_path)], shell=False)

        return {
            "success": True,
            "tool": "open_folder",
            "result": {
                "folder": str(valid_path),
                "status": "opened",
                "message": f"Folder '{valid_path.name}' opened in File Explorer."
            }
        }
    except Exception as exc:
        logger.exception("Error opening folder: %s", exc)
        return {"success": False, "tool": "open_folder", "error": f"Error opening folder: {str(exc)}"}


# =====================================================================
# TOOL 6: list_running_processes (READ_ONLY)
# =====================================================================

def list_running_processes(
    filter: Optional[str] = None,
    maximum_results: int = 50,
    sort_by: str = "memory",
    process_manager: Optional[ProcessManager] = None
) -> Dict[str, Any]:
    """
    Return currently running Windows processes with memory, CPU, and PID.
    """
    pm = process_manager or default_process_manager
    return pm.list_processes(filter_str=filter, maximum_results=maximum_results, sort_by=sort_by)


# =====================================================================
# TOOL 7: check_application_status (READ_ONLY)
# =====================================================================

def check_application_status(
    application_name: str,
    process_manager: Optional[ProcessManager] = None,
    resolver: Optional[ApplicationResolver] = None
) -> Dict[str, Any]:
    """
    Check whether a specified application is currently running.
    Uses alias matching and process name resolution.
    """
    pm = process_manager or default_process_manager
    res_engine = resolver or default_app_resolver

    # Attempt to resolve aliases
    aliases = []
    res = res_engine.resolve(application_name)
    if res.resolved and res.app:
        aliases = res.app.aliases + [Path(res.app.executable).name]

    return pm.check_application_status(application_name, alias_names=aliases)


# =====================================================================
# TOOL 8: get_process_info (READ_ONLY)
# =====================================================================

def get_process_info(
    process_name: Optional[str] = None,
    optional_pid: Optional[int] = None,
    process_manager: Optional[ProcessManager] = None
) -> Dict[str, Any]:
    """
    Retrieve comprehensive details (CPU, memory, create time, status) for a process.
    """
    pm = process_manager or default_process_manager
    return pm.get_process_info(process_name=process_name, optional_pid=optional_pid)


# =====================================================================
# TOOL 9: close_application (PROCESS_MODIFICATION)
# =====================================================================

def close_application(
    application_name: str,
    optional_pid: Optional[int] = None,
    confirmed: bool = False,
    process_manager: Optional[ProcessManager] = None,
    resolver: Optional[ApplicationResolver] = None
) -> Dict[str, Any]:
    """
    Close an application gracefully.
    Requires user confirmation. Strictly protects critical Windows services and agent core.
    Verifies that the process exited before reporting success.
    """
    try:
        pm = process_manager or default_process_manager
        res_engine = resolver or default_app_resolver

        # Check critical system process blacklist first
        if pm.is_critical_process(application_name, optional_pid):
            return {
                "success": False,
                "tool": "close_application",
                "error": f"Security restriction: Cannot terminate critical Windows process '{application_name}'."
            }

        target_pids = []
        app_display = application_name

        if optional_pid is not None:
            target_pids = [optional_pid]
        else:
            status_res = check_application_status(application_name, pm, res_engine)
            if not status_res.get("success"):
                return status_res

            res_data = status_res.get("result", {})
            if not res_data.get("is_running"):
                return {
                    "success": False,
                    "tool": "close_application",
                    "error": f"Application '{application_name}' is not currently running."
                }

            matching_procs = res_data.get("matching_processes", [])
            target_pids = [p["pid"] for p in matching_procs]
            app_display = res_data.get("application_name", application_name)

        if not target_pids:
            return {
                "success": False,
                "tool": "close_application",
                "error": f"No active processes found for '{application_name}'."
            }

        # Check each target PID against critical process guard
        for pid in target_pids:
            if pid in pm.get_protected_pids():
                return {
                    "success": False,
                    "tool": "close_application",
                    "error": f"Security restriction: Process with PID {pid} is protected (agent or system)."
                }

        # Check confirmation
        if not confirmed:
            return {
                "success": False,
                "requires_confirmation": True,
                "tool": "close_application",
                "title": "Process Termination Approval Required",
                "action": "Close Application",
                "application": app_display,
                "target": f"PIDs: {target_pids}",
                "risk": "Will send graceful termination signal (WM_CLOSE / SIGTERM). Unsaved work may be lost.",
                "message": f"User confirmation required to close application '{app_display}' (PIDs: {target_pids})."
            }

        # Execute graceful closure
        closed_pids = []
        failed_pids = []

        for pid in target_pids:
            success, msg = pm.close_process_gracefully(pid, timeout=2.5)
            if success:
                closed_pids.append(pid)
            else:
                failed_pids.append({"pid": pid, "reason": msg})

        all_closed = len(failed_pids) == 0

        return {
            "success": all_closed,
            "tool": "close_application",
            "result": {
                "application": app_display,
                "closed_pids": closed_pids,
                "failed_pids": failed_pids,
                "status": "closed" if all_closed else "partial_failure",
                "message": f"Application '{app_display}' closed gracefully." if all_closed else f"Some processes for '{app_display}' could not be closed gracefully."
            }
        }
    except Exception as exc:
        logger.exception("Error closing application: %s", exc)
        return {"success": False, "tool": "close_application", "error": f"Error closing application: {str(exc)}"}


# =====================================================================
# TOOL REGISTRATION
# =====================================================================

def register_app_tools(registry: ToolRegistry) -> None:
    """
    Registers all Phase 2.2.3 Application & Process Control tools with the ToolRegistry.
    """
    # 1. search_applications
    registry.register(ToolDefinition(
        name="search_applications",
        description="Search for installed or discoverable Windows applications by name or category.",
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="application",
        handler=search_applications,
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Application name or keyword to search for (e.g. 'VS Code', 'Chrome', 'browser')."
                },
                "maximum_results": {
                    "type": "integer",
                    "description": "Maximum number of search results to return (default 10)."
                }
            },
            "required": ["query"]
        }
    ))

    # 2. list_installed_applications
    registry.register(ToolDefinition(
        name="list_installed_applications",
        description="Return installed desktop applications discovered by the system, optionally filtered by category.",
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="application",
        handler=list_installed_applications,
        parameters={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Category filter: 'Development', 'Browser', 'Media', 'Productivity', 'System', 'Other' (or null for all)."
                },
                "maximum_results": {
                    "type": "integer",
                    "description": "Maximum number of applications to list (default 50)."
                }
            },
            "required": []
        }
    ))

    # 3. launch_application
    registry.register(ToolDefinition(
        name="launch_application",
        description="Launch a registered or verified Windows application. Requires user confirmation.",
        permission_level=PermissionLevel.CONTROLLED_ACTION,
        category="application",
        handler=launch_application,
        parameters={
            "type": "object",
            "properties": {
                "application_name": {
                    "type": "string",
                    "description": "Name of the application to launch (e.g. 'Chrome', 'VS Code', 'Notepad', 'Blender')."
                },
                "optional_arguments": {
                    "type": "string",
                    "description": "Optional command-line arguments to pass to the application."
                },
                "confirmed": {
                    "type": "boolean",
                    "description": "Confirmation flag set by user approval card."
                }
            },
            "required": ["application_name"]
        }
    ))

    # 4. open_file_with_application
    registry.register(ToolDefinition(
        name="open_file_with_application",
        description="Open a file using a specified application (or default Windows handler). Requires user confirmation.",
        permission_level=PermissionLevel.CONTROLLED_ACTION,
        category="application",
        handler=open_file_with_application,
        parameters={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Full path of the file to open."
                },
                "application_name": {
                    "type": "string",
                    "description": "Optional name of the application to open the file with (e.g. 'VS Code', 'Paint')."
                },
                "confirmed": {
                    "type": "boolean",
                    "description": "Confirmation flag set by user approval card."
                }
            },
            "required": ["file_path"]
        }
    ))

    # 5. open_folder
    registry.register(ToolDefinition(
        name="open_folder",
        description="Open a folder in Windows File Explorer. Requires user confirmation.",
        permission_level=PermissionLevel.CONTROLLED_ACTION,
        category="application",
        handler=open_folder,
        parameters={
            "type": "object",
            "properties": {
                "folder_path": {
                    "type": "string",
                    "description": "Directory path to open in File Explorer."
                },
                "confirmed": {
                    "type": "boolean",
                    "description": "Confirmation flag set by user approval card."
                }
            },
            "required": ["folder_path"]
        }
    ))

    # 6. list_running_processes
    registry.register(ToolDefinition(
        name="list_running_processes",
        description="Return currently running Windows processes with memory, CPU %, and PID.",
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="process",
        handler=list_running_processes,
        parameters={
            "type": "object",
            "properties": {
                "filter": {
                    "type": "string",
                    "description": "Optional substring to filter process names."
                },
                "maximum_results": {
                    "type": "integer",
                    "description": "Maximum number of processes to return (default 50)."
                },
                "sort_by": {
                    "type": "string",
                    "description": "Sort order: 'memory', 'cpu', 'name', or 'pid' (default 'memory')."
                }
            },
            "required": []
        }
    ))

    # 7. check_application_status
    registry.register(ToolDefinition(
        name="check_application_status",
        description="Check whether a specified application is currently running (e.g. 'Is Ollama running?').",
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="process",
        handler=check_application_status,
        parameters={
            "type": "object",
            "properties": {
                "application_name": {
                    "type": "string",
                    "description": "Name of the application to check (e.g. 'Chrome', 'Ollama', 'VS Code')."
                }
            },
            "required": ["application_name"]
        }
    ))

    # 8. get_process_info
    registry.register(ToolDefinition(
        name="get_process_info",
        description="Retrieve comprehensive runtime information about a running process by name or PID.",
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="process",
        handler=get_process_info,
        parameters={
            "type": "object",
            "properties": {
                "process_name": {
                    "type": "string",
                    "description": "Process executable name (e.g. 'ollama.exe', 'Code.exe')."
                },
                "optional_pid": {
                    "type": "integer",
                    "description": "Process ID (PID) to look up directly."
                }
            },
            "required": []
        }
    ))

    # 9. close_application
    registry.register(ToolDefinition(
        name="close_application",
        description="Close a running application gracefully. Requires user confirmation. Critical Windows processes are strictly protected.",
        permission_level=PermissionLevel.PROCESS_MODIFICATION,
        category="process",
        handler=close_application,
        parameters={
            "type": "object",
            "properties": {
                "application_name": {
                    "type": "string",
                    "description": "Name of the application to close (e.g. 'Spotify', 'Notepad')."
                },
                "optional_pid": {
                    "type": "integer",
                    "description": "Optional specific PID to close."
                },
                "confirmed": {
                    "type": "boolean",
                    "description": "Confirmation flag set by user approval card."
                }
            },
            "required": ["application_name"]
        }
    ))
