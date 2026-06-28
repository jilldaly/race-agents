"""The LLM control plane: a raw OpenAI-compatible client pointed at Gemini.

The router only routes — it sees tool schemas and compact JSON observations, never
raw DataFrames or PII. Swapping the provider is a config change (ADR 0003).
"""
from __future__ import annotations

from backend import config


class Router:
    def __init__(self, model: str | None = None) -> None:
        from openai import OpenAI  # imported lazily so tests can stub the router

        self.model = model or config.MODEL
        self._client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)

    def chat(self, messages: list[dict], tools: list[dict]):
        return self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            temperature=config.TEMPERATURE,
        )
