"""
Model and Provider Manager for local Ollama and future AI providers.
Supports Ollama API, model discovery, model switching, parameters, and GPU status.
"""
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, List, Any, Optional
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger("PersonalAgent.ModelManager")


class ModelManager(QObject):
    """
    Manages active AI models, Ollama connection health, installed models,
    and GPU execution offloading information.
    """
    connection_changed = Signal(str, bool, str)  # display_name, is_connected, processor_info
    models_updated = Signal(list)                # list of model names
    error_occurred = Signal(str)

    def __init__(self, endpoint: str = "http://localhost:11434"):
        super().__init__()
        self._endpoint = endpoint.rstrip("/")
        self._active_provider = "Local (Ollama)"
        self._active_model = "qwen3:8b"
        self._is_connected = False
        self._processor_info = "Standby"
        self._installed_models: List[Dict[str, Any]] = []

        # Default Generation Options optimized for RTX 3050 6GB
        self.temperature = 0.7
        self.num_ctx = 4096
        self.num_gpu = -1  # -1 = auto-offload all layers possible to GPU

        # Perform initial check
        self.check_connection()

    @property
    def endpoint(self) -> str:
        return self._endpoint

    @endpoint.setter
    def endpoint(self, value: str) -> None:
        self._endpoint = value.rstrip("/")
        self.check_connection()

    @property
    def active_model(self) -> str:
        return self._active_model

    @property
    def active_provider(self) -> str:
        return self._active_provider

    @property
    def active_model_display(self) -> str:
        return f"{self._active_provider}: {self._active_model}"

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def processor_info(self) -> str:
        return self._processor_info

    @property
    def available_models(self) -> List[Dict[str, Any]]:
        if self._installed_models:
            return list(self._installed_models)
        # Fallback list if Ollama is not currently running
        return [{"provider": "Local (Ollama)", "name": self._active_model, "connected": self._is_connected}]

    def check_connection(self) -> bool:
        """Ping Ollama API tags endpoint to check connection and discover models."""
        try:
            req = urllib.request.Request(
                f"{self._endpoint}/api/tags",
                headers={"User-Agent": "PersonalAgent/1.0"}
            )
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    models_raw = data.get("models", [])
                    self._installed_models = []
                    names = []
                    for m in models_raw:
                        name = m.get("name", "")
                        size_gb = m.get("size", 0) / (1024**3)
                        self._installed_models.append({
                            "provider": "Local (Ollama)",
                            "name": name,
                            "size": f"{size_gb:.1f} GB",
                            "connected": True
                        })
                        names.append(name)

                    self._is_connected = True
                    # If active model not in installed models, pick first available
                    if names and self._active_model not in names:
                        self._active_model = names[0]

                    # Query running processor status
                    self.query_running_processor()

                    self.connection_changed.emit(self.active_model_display, True, self._processor_info)
                    self.models_updated.emit(names)
                    logger.info("Ollama connected at %s. Models found: %s", self._endpoint, names)
                    return True
        except Exception as exc:
            self._is_connected = False
            self._processor_info = "Disconnected"
            self.connection_changed.emit(self.active_model_display, False, "Disconnected")
            logger.warning("Ollama connection failed at %s: %s", self._endpoint, exc)
            return False

        self._is_connected = False
        return False

    def query_running_processor(self) -> str:
        """Inspect /api/ps to see if model is currently loaded on GPU or CPU."""
        if not self._is_connected:
            self._processor_info = "Disconnected"
            return self._processor_info

        try:
            req = urllib.request.Request(f"{self._endpoint}/api/ps", headers={"User-Agent": "PersonalAgent/1.0"})
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    models = data.get("models", [])
                    for m in models:
                        if m.get("name") == self._active_model:
                            proc = m.get("processor", "")
                            runner = m.get("runner", "")
                            self._processor_info = f"{proc} ({runner})" if runner else proc
                            return self._processor_info
        except Exception:
            pass

        self._processor_info = "Standby (GPU ready)"
        return self._processor_info

    def set_active_model(self, model_name: str, provider: str = "Local (Ollama)") -> None:
        """Change the active model for inference."""
        self._active_model = model_name
        self._active_provider = provider
        self.query_running_processor()
        self.connection_changed.emit(self.active_model_display, self._is_connected, self._processor_info)
        logger.info("Active model switched to: %s", self.active_model_display)

    def test_connection(self) -> bool:
        return self.check_connection()
