"""Environment-backed configuration with no embedded credentials."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MODEL = "claude-opus-5-5"


@dataclass(frozen=True)
class Config:
    provider: str = "anthropic"
    model: str = DEFAULT_MODEL
    state_dir: Path = Path(__file__).resolve().parent / "state"
    dry_run: bool = False
    locale: str = "en"

    @classmethod
    def from_env(cls, dry_run: bool = False, locale: str | None = None) -> "Config":
        return cls(
            provider=os.getenv("AGENT_PROVIDER", "anthropic"),
            model=os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL),
            state_dir=Path(os.getenv("AUTOMATION_STATE_DIR", str(Path(__file__).resolve().parent / "state"))),
            dry_run=dry_run,
            locale=locale or os.getenv("AGENT_LOCALE", "en"),
        )
