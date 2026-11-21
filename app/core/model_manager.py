"""
Model and Provider Manager for local and cloud models.
"""
from typing import Dict, List, Any
from PySide6.QtCore import QObject, Signal


class ModelManager(QObject):
    """
    Manages active AI models, providers, and connection health.
    """
    connection_changed = Signal(str, bool) # model_name, is_connected

    def __init__(self):
        super().__init__()
        self._active_provider = "Local (Ollama)"
        self._active_model = "Qwen 2.5 7B"
        self._is_connected = False
        self._available_models = [
            {"provider": "Local (Ollama)", "name": "Qwen 2.5 7B", "connected": False},
            {"provider": "Local (Ollama)", "name": "Llama 3.2 3B", "connected": False},
            {"provider": "Local (LM Studio)", "name": "DeepSeek R1 Distill", "connected": False},
            {"provider": "Google Gemini", "name": "Gemini 1.5 Pro", "connected": True},
            {"provider": "Anthropic", "name": "Claude 3.5 Sonnet", "connected": False},
            {"provider": "OpenAI", "name": "GPT-4o", "connected": False},
        ]

    @property
    def active_model_display(self) -> str:
        return f"{self._active_provider}: {self._active_model}"

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def available_models(self) -> List[Dict[str, Any]]:
        return list(self._available_models)

    def set_active_model(self, model_name: str, provider: str = "Local") -> None:
        self._active_model = model_name
        self._active_provider = provider
        self.connection_changed.emit(self.active_model_display, self._is_connected)

    def test_connection(self) -> bool:
        # Placeholder for real health check
        return self._is_connected
