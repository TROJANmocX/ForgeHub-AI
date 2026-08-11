"""ForgeHub AI — Google Gemini LLM Provider."""
from __future__ import annotations

from app.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro") -> None:
        self._api_key = api_key
        self._model = model

    def generate(self, prompt: str) -> str:
        try:
            import google.generativeai as genai  # type: ignore
        except ImportError as e:
            raise RuntimeError(
                "google-generativeai package not installed. Run: pip install google-generativeai"
            ) from e

        genai.configure(api_key=self._api_key)
        model = genai.GenerativeModel(self._model)
        response = model.generate_content(prompt)
        return response.text

    @property
    def name(self) -> str:
        return "gemini"
