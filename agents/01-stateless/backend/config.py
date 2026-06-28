"""Config — all env-overridable; default control plane is Gemini (free tier).

The transport is OpenAI-compatible, so swapping providers (Gemini ↔ Ollama ↔ any
hosted endpoint) is a base_url + key + model change, nothing else (ADR 0003).
Cost defaults to $0 on the Gemini free tier.
"""
from __future__ import annotations

import os
from pathlib import Path

# Load the agent's local .env (gitignored) so GEMINI_API_KEY and any overrides are
# picked up without exporting them by hand. Optional dep — keyless tests/eval still
# run if python-dotenv isn't installed.
try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ModuleNotFoundError:
    pass

# Google's OpenAI-compatible endpoint for Gemini.
BASE_URL = os.environ.get(
    "LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"
)
MODEL = os.environ.get("LLM_MODEL", "gemini-2.0-flash")
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0"))
MAX_STEPS = int(os.environ.get("AGENT_MAX_STEPS", "6"))
