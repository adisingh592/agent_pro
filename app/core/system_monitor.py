"""
System and GPU Resource Monitor.
Tracks CPU & RAM usage via psutil, and NVIDIA GPU metrics via nvidia-smi.
"""
import subprocess
import shutil
import logging
import psutil
from typing import Dict, Any, Tuple
from PySide6.QtCore import QObject, QTimer, Signal

logger = logging.getLogger("PersonalAgent.SystemMonitor")


class SystemMonitor(QObject):
    """
    Periodically measures CPU, RAM, and NVIDIA GPU statistics.
    Emits metrics_updated signal without blocking the main event loop.
    """
    # cpu_percent, ram_percent, gpu_metrics_dict
    metrics_updated = Signal(float, float, dict)

    def __init__(self, interval_ms: int = 2000):
        super().__init__()
        self._last_cpu = 0.0
        self._last_ram = 0.0
        self._last_gpu: Dict[str, Any] = {
            "available": False,
            "name": "N/A",
            "utilization": 0,
            "vram_used_mb": 0,
            "vram_total_mb": 0,
            "temp_c": 0
        }

        # Check if nvidia-smi is available on PATH
        self._has_nvidia_smi = shutil.which("nvidia-smi") is not None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._measure)
        self.timer.start(interval_ms)

    def _measure(self) -> None:
        try:
            self._last_cpu = psutil.cpu_percent(interval=None)
            self._last_ram = psutil.virtual_memory().percent
        except Exception:
            pass

        if self._has_nvidia_smi:
            self._measure_gpu()

        self.metrics_updated.emit(self._last_cpu, self._last_ram, dict(self._last_gpu))

    def _measure_gpu(self) -> None:
        """Query GPU metrics using lightweight nvidia-smi query."""
        try:
            cmd = [
                "nvidia-smi",
                "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
                "--format=csv,noheader,nounits"
            ]
            output = subprocess.check_output(cmd, encoding="utf-8", timeout=1.5, creationflags=0x08000000 if hasattr(subprocess, "CREATE_NO_WINDOW") else 0)
            lines = output.strip().split("\n")
            if lines and lines[0]:
                parts = [p.strip() for p in lines[0].split(",")]
                if len(parts) >= 5:
                    self._last_gpu = {
                        "available": True,
                        "name": parts[0],
                        "utilization": int(parts[1]) if parts[1].isdigit() else 0,
                        "vram_used_mb": int(parts[2]) if parts[2].isdigit() else 0,
                        "vram_total_mb": int(parts[3]) if parts[3].isdigit() else 0,
                        "temp_c": int(parts[4]) if parts[4].isdigit() else 0
                    }
        except Exception:
            # Fallback gracefully if query times out or is busy
            pass

    @property
    def last_metrics(self) -> Tuple[float, float, Dict[str, Any]]:
        return self._last_cpu, self._last_ram, dict(self._last_gpu)
