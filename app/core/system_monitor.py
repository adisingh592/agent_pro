"""
System Resource Monitor using psutil.
Provides CPU and RAM metrics to the status bar and agent panels.
"""
import psutil
from PySide6.QtCore import QObject, QTimer, Signal


class SystemMonitor(QObject):
    """Periodically emits CPU and RAM usage percentage."""
    metrics_updated = Signal(float, float) # cpu_percent, ram_percent

    def __init__(self, interval_ms: int = 2000):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._measure)
        self.timer.start(interval_ms)
        self._last_cpu = 0.0
        self._last_ram = 0.0

    def _measure(self) -> None:
        try:
            self._last_cpu = psutil.cpu_percent(interval=None)
            self._last_ram = psutil.virtual_memory().percent
            self.metrics_updated.emit(self._last_cpu, self._last_ram)
        except Exception:
            pass

    @property
    def last_metrics(self) -> tuple[float, float]:
        return self._last_cpu, self._last_ram
