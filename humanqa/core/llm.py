"""LLM abstraction layer for HumanQA.

Supports Anthropic (Claude) and OpenAI. All LLM calls go through this module
so prompts and model selection are explicit and inspectable.
"""

from __future__ import annotations

import json
import os
from typing import Any

import anthropic
import openai


class LLMClient:
    """Unified LLM interface."""

    def __init__(self, provider: str = "anthropic", model: str | None = None):
        self.provider = provider
        if provider == "anthropic":
            self.model = model or "claude-sonnet-4-20250514"
            self._client = anthropic.Anthropic(
                api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            )
        elif provider == "openai":
            self.model = model or "gpt-4o"
            self._client = openai.OpenAI(
                api_key=os.environ.get("OPENAI_API_KEY", ""),
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def complete(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> str:
        """Get a text completion."""
        if self.provider == "anthropic":
            msg = self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or "You are HumanQA, an AI QA evaluation system.",
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text
        else:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return resp.choices[0].message.content or ""

    def complete_json(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.2,
    ) -> Any:
        """Get a JSON-structured completion. Extracts JSON from response."""
        full_system = (system or "You are HumanQA, an AI QA evaluation system.") + (
            "\n\nRespond ONLY with valid JSON. No markdown fences, no preamble, no explanation."
        )
        raw = self.complete(prompt, system=full_system, max_tokens=max_tokens, temperature=temperature)
        # Strip markdown fences if present
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first and last fence lines
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines)
        return json.loads(text)
