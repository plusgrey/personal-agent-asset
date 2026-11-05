"""Switchable text-generation providers."""
from __future__ import annotations

import os
import shlex
import subprocess
from typing import Protocol


class Provider(Protocol):
    def generate(self, system: str, prompt: str) -> str: ...


class AnthropicProvider:
    """Official Anthropic Python SDK provider."""

    def __init__(self, model: str = "claude-opus-5-5"):
        try:
            import anthropic
        except ImportError as exc:
            raise RuntimeError("Install requirements.txt to use the Anthropic provider") from exc
        self.client = anthropic.Anthropic()
        self.model = model

    def generate(self, system: str, prompt: str) -> str:
        response = self.client.beta.messages.create(
            model=self.model,
            max_tokens=16000,
            thinking={"type": "adaptive"},
            output_config={"effort": "high"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        if response.stop_reason == "refusal":
            raise RuntimeError("Anthropic request was refused")
        return "\n".join(block.text for block in response.content if block.type == "text").strip()


class CommandProvider:
    """Provider adapter for a user-supplied command; prompt is sent on stdin."""

    def __init__(self, command: str):
        if not command.strip():
            raise ValueError("EXTERNAL_AGENT_COMMAND is required for command provider")
        self.command = shlex.split(command)

    def generate(self, system: str, prompt: str) -> str:
        completed = subprocess.run(
            self.command,
            input=f"SYSTEM:\n{system}\n\nUSER:\n{prompt}\n",
            text=True,
            capture_output=True,
            check=False,
            timeout=600,
        )
        if completed.returncode:
            raise RuntimeError(f"external provider failed ({completed.returncode}): {completed.stderr.strip()}")
        return completed.stdout.strip()


def build_provider(name: str, model: str) -> Provider:
    if name == "anthropic":
        return AnthropicProvider(model)
    if name == "command":
        return CommandProvider(os.getenv("EXTERNAL_AGENT_COMMAND", ""))
    raise ValueError(f"unsupported provider: {name}")
