"""Environment-backed configuration with no embedded credentials."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_NOTION_PAGE_ID = "38889a37c8408030b9bdcdbd13c618d9"
DEFAULT_NOTION_VERSION = "2026-03-11"
DEFAULT_MODEL = "claude-opus-5-5"


@dataclass(frozen=True)
class Config:
    provider: str = "anthropic"
    model: str = DEFAULT_MODEL
    notion_page_id: str = DEFAULT_NOTION_PAGE_ID
    notion_version: str = DEFAULT_NOTION_VERSION
    state_dir: Path = Path(__file__).resolve().parent / "state"
    dry_run: bool = False
    locale: str = "en"
    allow_private_context: bool = False

    @classmethod
    def from_env(cls, dry_run: bool = False, locale: str | None = None) -> "Config":
        return cls(
            provider=os.getenv("AGENT_PROVIDER", "anthropic"),
            model=os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL),
            notion_page_id=os.getenv("NOTION_PAGE_ID", DEFAULT_NOTION_PAGE_ID).replace("-", ""),
            notion_version=os.getenv("NOTION_VERSION", DEFAULT_NOTION_VERSION),
            state_dir=Path(os.getenv("AUTOMATION_STATE_DIR", str(Path(__file__).resolve().parent / "state"))),
            dry_run=dry_run,
            locale=locale or os.getenv("AGENT_LOCALE", "en"),
            allow_private_context=os.getenv("ALLOW_PRIVATE_CONTEXT", "").lower() in {"1", "true", "yes"},
        )
