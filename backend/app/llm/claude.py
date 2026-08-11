"""ForgeHub AI — Anthropic Claude LLM Provider."""
from __future__ import annotations

from app.llm.base import LLMProvider


class ClaudeProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022") -> None:
        self._api_key = api_key
        self._model = model

    def generate(self, prompt: str) -> str:
        try:
            import anthropic  # type: ignore
        except ImportError as e:
            raise RuntimeError("anthropic package not installed. Run: pip install anthropic") from e

        client = anthropic.Anthropic(api_key=self._api_key)
        message = client.messages.create(
            model=self._model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    @property
    def name(self) -> str:
        return "anthropic"
