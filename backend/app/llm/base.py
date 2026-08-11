"""ForgeHub AI — Abstract LLM provider interface."""
from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Provider-independent LLM interface. All providers must implement generate()."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Send a prompt and return the model's text response."""
        ...

    @property
    def name(self) -> str:
        return self.__class__.__name__
