"""
Process Management and Inspection System for Personal Agent (Phase 2.2.3).
Provides safe Windows process enumeration, application status verification,
graceful termination with post-verification, and strict protection of critical system services.
"""
import os
import time
import logging
import datetime
from typing import Dict, Any, List, Optional, Set, Tuple

import psutil

logger = logging.getLogger("PersonalAgent.ProcessManager")


class ProcessManager:
    """
    Manages process enumeration, status tracking, and graceful termination.
    Guarantees that critical Windows services and agent core cannot be closed.
    """

    # Critical Windows operating system processes that must NEVER be terminated
    CRITICAL_SYSTEM_PROCESSES: Set[str] = {
        "system",
        "system idle process",
        "registry",
        "smss.exe",
        "csrss.exe",
        "wininit.exe",
        "services.exe",
        "lsass.exe",
        "svchost.exe",
        "fontdrvhost.exe",
        "winlogon.exe",
        "dwm.exe",
        "spoolsv.exe",
        "runtimebroker.exe",
        "searchhost.exe",
        "taskhostw.exe",
        "explorer.exe",
        "sihost.exe",
        "shellexperiencehost.exe",
        "startmenuexperiencehost.exe",
        "ctfmon.exe",
        "securityhealthservice.exe",
        "msmpeng.exe",
        "mpcmdrun.exe",
        "conhost.exe"
    }

    @classmethod
    def get_protected_pids(cls) -> Set[int]:
        """Returns set of PIDs that must never be terminated (including current agent process)."""
        protected = {0, 4}  # Idle, System
        current_pid = os.getpid()
        protected.add(current_pid)

        # Protect parent process if applicable
        try:
            parent = psutil.Process(current_pid).parent()
            if parent:
                protected.add(parent.pid)
        except Exception:
            pass
        return protected

    @classmethod
    def is_critical_process(cls, proc_name: str, pid: Optional[int] = None) -> bool:
        """Determines if a process name or PID belongs to critical Windows infrastructure."""
        if not proc_name:
            return False
        clean_name = proc_name.strip().lower()
        if clean_name in cls.CRITICAL_SYSTEM_PROCESSES:
            return True
        if clean_name.replace(".exe", "") in cls.CRITICAL_SYSTEM_PROCESSES:
            return True

        if pid is not None and pid in cls.get_protected_pids():
            return True

        return False

    @staticmethod
    def _format_memory(size_bytes: int) -> str:
        """Format byte size into human readable string."""
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    def list_processes(
        self,
        filter_str: Optional[str] = None,
        maximum_results: int = 50,
        sort_by: str = "memory"
    ) -> Dict[str, Any]:
        """
        List currently running Windows processes with CPU and memory statistics.
        Does not expose sensitive environment variables or command-line credentials.
        """
        maximum_results = max(1, min(maximum_results, 200))
        results: List[Dict[str, Any]] = []
        filter_lower = filter_str.strip().lower() if filter_str else None

        # Iterate active processes safely
        for proc in psutil.process_iter(['pid', 'name', 'status', 'create_time']):
            try:
                p_info = proc.info
                p_name = p_info.get('name') or "Unknown"

                # Apply filter
                if filter_lower and filter_lower not in p_name.lower():
                    continue

                # Safely query memory & CPU
                try:
                    mem_info = proc.memory_info()
                    rss_bytes = mem_info.rss
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    rss_bytes = 0

                try:
                    # Non-blocking cpu percent
                    cpu_perc = proc.cpu_percent(interval=None)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    cpu_perc = 0.0

                results.append({
                    "pid": p_info['pid'],
                    "name": p_name,
                    "cpu_percent": round(cpu_perc, 1),
                    "memory_mb": round(rss_bytes / (1024 * 1024), 2),
                    "memory_readable": self._format_memory(rss_bytes),
                    "status": p_info.get('status', 'running')
                })

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as exc:
                logger.debug("Error reading process: %s", exc)
                continue

        # Sort results
        if sort_by == "cpu":
            results.sort(key=lambda x: x["cpu_percent"], reverse=True)
        elif sort_by == "name":
            results.sort(key=lambda x: x["name"].lower())
        elif sort_by == "pid":
            results.sort(key=lambda x: x["pid"])
        else:  # memory default
            results.sort(key=lambda x: x["memory_mb"], reverse=True)

        return {
            "success": True,
            "tool": "list_running_processes",
            "result": {
                "count": len(results[:maximum_results]),
                "total_matched": len(results),
                "filter": filter_str or "",
                "sort_by": sort_by,
                "processes": results[:maximum_results]
            }
        }

    def check_application_status(
        self,
        application_name: str,
        alias_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Check if a given application is currently running by inspecting process names and aliases.
        """
        if not application_name or not application_name.strip():
            return {"success": False, "tool": "check_application_status", "error": "Application name cannot be empty."}

        target_names = {application_name.strip().lower()}
        if target_names:
            first = list(target_names)[0]
            if first.endswith(".exe"):
                target_names.add(first[:-4])
            else:
                target_names.add(f"{first}.exe")

        if alias_names:
            for a in alias_names:
                al = a.strip().lower()
                target_names.add(al)
                target_names.add(f"{al}.exe")

        matching_processes = []
        total_rss = 0

        for proc in psutil.process_iter(['pid', 'name', 'status']):
            try:
                p_name = (proc.info.get('name') or "").lower()
                stem = p_name.replace(".exe", "")

                if p_name in target_names or stem in target_names or any(t in p_name for t in target_names if len(t) > 3):
                    try:
                        mem_info = proc.memory_info()
                        rss = mem_info.rss
                    except Exception:
                        rss = 0
                    try:
                        cpu_p = proc.cpu_percent(interval=None)
                    except Exception:
                        cpu_p = 0.0

                    total_rss += rss
                    matching_processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info.get('name', 'Unknown'),
                        "memory_mb": round(rss / (1024 * 1024), 2),
                        "cpu_percent": round(cpu_p, 1),
                        "status": proc.info.get('status', 'running')
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        is_running = len(matching_processes) > 0

        return {
            "success": True,
            "tool": "check_application_status",
            "result": {
                "application_name": application_name,
                "is_running": is_running,
                "process_count": len(matching_processes),
                "total_memory_mb": round(total_rss / (1024 * 1024), 2),
                "total_memory_readable": self._format_memory(total_rss),
                "matching_processes": matching_processes
            }
        }

    def get_process_info(
        self,
        process_name: Optional[str] = None,
        optional_pid: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retrieve comprehensive process details for a specific PID or process name.
        """
        if not process_name and optional_pid is None:
            return {
                "success": False,
                "tool": "get_process_info",
                "error": "Must provide either 'process_name' or 'optional_pid'."
            }

        matched_records = []

        # 1. Lookup by PID directly
        if optional_pid is not None:
            try:
                proc = psutil.Process(optional_pid)
                p_name = proc.name()
                mem = proc.memory_info().rss
                create_dt = datetime.datetime.fromtimestamp(proc.create_time()).strftime("%Y-%m-%d %H:%M:%S")
                matched_records.append({
                    "pid": proc.pid,
                    "name": p_name,
                    "cpu_percent": round(proc.cpu_percent(interval=None), 1),
                    "memory_mb": round(mem / (1024 * 1024), 2),
                    "memory_readable": self._format_memory(mem),
                    "create_time": create_dt,
                    "status": proc.status()
                })
            except psutil.NoSuchProcess:
                return {
                    "success": False,
                    "tool": "get_process_info",
                    "error": f"Process with PID {optional_pid} does not exist."
                }
            except psutil.AccessDenied:
                return {
                    "success": False,
                    "tool": "get_process_info",
                    "error": f"Access denied reading process with PID {optional_pid}."
                }

        # 2. Lookup by process_name
        elif process_name:
            target = process_name.strip().lower()
            for proc in psutil.process_iter(['pid', 'name', 'status', 'create_time']):
                try:
                    p_name = (proc.info.get('name') or "").lower()
                    if target in p_name or target in p_name.replace(".exe", ""):
                        try:
                            mem = proc.memory_info().rss
                        except Exception:
                            mem = 0
                        try:
                            cpu_p = proc.cpu_percent(interval=None)
                        except Exception:
                            cpu_p = 0.0

                        create_ts = proc.info.get('create_time', 0.0)
                        create_dt = datetime.datetime.fromtimestamp(create_ts).strftime("%Y-%m-%d %H:%M:%S") if create_ts else "Unknown"

                        matched_records.append({
                            "pid": proc.info['pid'],
                            "name": proc.info.get('name', 'Unknown'),
                            "cpu_percent": round(cpu_p, 1),
                            "memory_mb": round(mem / (1024 * 1024), 2),
                            "memory_readable": self._format_memory(mem),
                            "create_time": create_dt,
                            "status": proc.info.get('status', 'running')
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

        if not matched_records:
            return {
                "success": False,
                "tool": "get_process_info",
                "error": f"No running processes found matching '{process_name or optional_pid}'."
            }

        return {
            "success": True,
            "tool": "get_process_info",
            "result": {
                "count": len(matched_records),
                "processes": matched_records
            }
        }

    def close_process_gracefully(self, pid: int, timeout: float = 2.5) -> Tuple[bool, str]:
        """
        Attempts graceful shutdown of a process via terminate() (SIGTERM/WM_CLOSE).
        Verifies whether process has exited within timeout. Does NOT force-kill.
        """
        try:
            proc = psutil.Process(pid)
            p_name = proc.name()
        except psutil.NoSuchProcess:
            return True, f"Process {pid} is already closed."
        except psutil.AccessDenied:
            return False, f"Permission denied to access process {pid}."

        # Safety check against critical processes
        if self.is_critical_process(p_name, pid):
            return False, f"Security restriction: Cannot terminate critical Windows process '{p_name}' (PID {pid})."

        try:
            # Send graceful termination signal
            proc.terminate()
            gone, alive = psutil.wait_procs([proc], timeout=timeout)
            if proc in gone or not proc.is_running():
                return True, f"Process '{p_name}' (PID {pid}) closed gracefully."
            else:
                return False, f"Process '{p_name}' (PID {pid}) did not exit within {timeout}s timeout. Forced termination was NOT applied."
        except psutil.NoSuchProcess:
            return True, f"Process '{p_name}' (PID {pid}) closed."
        except psutil.AccessDenied:
            return False, f"Access denied when attempting to terminate process '{p_name}' (PID {pid})."
        except Exception as exc:
            return False, f"Error terminating process '{p_name}' (PID {pid}): {str(exc)}"


# Global default instance
default_process_manager = ProcessManager()
