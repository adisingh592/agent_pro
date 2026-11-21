"""
Built-in Safe Tools for Personal Agent Phase 2.2.1.
Provides initial read-only system inspection tools:
1. get_current_time: System date and time
2. get_system_info: OS, CPU, RAM, and hardware metrics
3. get_gpu_info: NVIDIA GPU utilization, VRAM, and temperature
"""
import os
import platform
import subprocess
import datetime
from typing import Dict, Any
import psutil

from .tool_registry import ToolDefinition, ToolRegistry
from .tool_permissions import PermissionLevel


def get_current_time() -> Dict[str, Any]:
    """
    Returns the current local system date and time.
    """
    now = datetime.datetime.now()
    formatted = now.strftime("%B %d, %Y, %I:%M %p")
    return {
        "success": True,
        "tool": "get_current_time",
        "result": formatted
    }


def get_system_info() -> Dict[str, Any]:
    """
    Returns basic non-sensitive information about the host computer:
    Operating system, Windows version, computer name, CPU information,
    total RAM, available RAM, and CPU usage percentage.
    """
    try:
        mem = psutil.virtual_memory()
        cpu_pct = psutil.cpu_percent(interval=0.1)
        total_ram_gb = round(mem.total / (1024**3), 1)
        available_ram_gb = round(mem.available / (1024**3), 1)

        result_data = {
            "os": f"Windows {platform.release()}",
            "windows_version": platform.version(),
            "computer_name": platform.node(),
            "cpu": platform.processor() or "Intel Core i7-13650HX",
            "cpu_cores": psutil.cpu_count(logical=True),
            "ram_total": f"{total_ram_gb} GB",
            "ram_available": f"{available_ram_gb} GB",
            "cpu_usage": f"{cpu_pct}%"
        }

        return {
            "success": True,
            "tool": "get_system_info",
            "result": result_data
        }
    except Exception as exc:
        return {
            "success": False,
            "tool": "get_system_info",
            "error": f"Failed to retrieve system information: {str(exc)}"
        }


def get_gpu_info() -> Dict[str, Any]:
    """
    Returns information about the available NVIDIA GPU:
    GPU name, GPU utilization, VRAM total, VRAM used, VRAM available, and temperature.
    Handles environments where GPU or nvidia-smi is unavailable safely.
    """
    try:
        cmd = [
            "nvidia-smi",
            "--query-gpu=name,utilization.gpu,memory.total,memory.used,memory.free,temperature.gpu",
            "--format=csv,noheader,nounits"
        ]
        
        # Suppress command prompt window on Windows
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3,
            startupinfo=startupinfo
        )

        if proc.returncode == 0 and proc.stdout.strip():
            line = proc.stdout.strip().split("\n")[0]
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 6:
                name, util_gpu, mem_total, mem_used, mem_free, temp = parts[:6]
                return {
                    "success": True,
                    "tool": "get_gpu_info",
                    "result": {
                        "gpu_name": name,
                        "gpu_utilization": f"{util_gpu}%",
                        "vram_total": f"{mem_total} MB",
                        "vram_used": f"{mem_used} MB",
                        "vram_available": f"{mem_free} MB",
                        "gpu_temperature": f"{temp}°C",
                        "status": "Active"
                    }
                }

        return {
            "success": True,
            "tool": "get_gpu_info",
            "result": {
                "status": "NVIDIA GPU not detected or nvidia-smi returned no data."
            }
        }
    except FileNotFoundError:
        return {
            "success": True,
            "tool": "get_gpu_info",
            "result": {
                "status": "nvidia-smi utility is not installed or not in PATH."
            }
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "tool": "get_gpu_info",
            "error": "Query to nvidia-smi timed out."
        }
    except Exception as exc:
        return {
            "success": False,
            "tool": "get_gpu_info",
            "error": f"Error querying GPU information: {str(exc)}"
        }


def register_built_in_tools(registry: ToolRegistry) -> None:
    """Registers all initial safe tools into the given registry."""
    
    # 1. get_current_time
    registry.register(ToolDefinition(
        name="get_current_time",
        description="Returns the current local system date and time. Use whenever the user asks for the current time, date, day, or timestamp.",
        parameters={
            "type": "object",
            "properties": {},
            "required": []
        },
        handler=get_current_time,
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="system_info"
    ))

    # 2. get_system_info
    registry.register(ToolDefinition(
        name="get_system_info",
        description="Returns basic information about the user's computer including OS, Windows version, computer name, CPU information, RAM capacity, and current CPU usage. Use when the user asks about their system specs or general computer hardware.",
        parameters={
            "type": "object",
            "properties": {},
            "required": []
        },
        handler=get_system_info,
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="system_info"
    ))

    # 3. get_gpu_info
    registry.register(ToolDefinition(
        name="get_gpu_info",
        description="Returns information about the available NVIDIA GPU, including GPU model name, GPU utilization percentage, VRAM total, VRAM used, VRAM available, and temperature. Use when the user asks about their graphics card, GPU, VRAM, or GPU temperature.",
        parameters={
            "type": "object",
            "properties": {},
            "required": []
        },
        handler=get_gpu_info,
        permission_level=PermissionLevel.SAFE_READ_ONLY,
        category="system_info"
    ))
