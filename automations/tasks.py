"""Scheduled task implementations."""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automations.config import Config
from automations.notion import NotionClient, blocks_to_text, load_fixture
from automations.notifications import Notifier
from automations.providers import Provider
from automations.state_store import StateStore

TASKS = ("research-radar", "quant-interview", "backtest-auditor")


def _parse_list(text: str) -> list[str]:
    try:
        value = json.loads(text)
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
    except json.JSONDecodeError:
        pass
    return [re.sub(r"^[-*\d.)\s]+", "", line).strip() for line in text.splitlines() if line.strip()]


def _context(config: Config, fixture: Path | None) -> str:
    if fixture:
        return blocks_to_text(load_fixture(fixture))
    token = os.getenv("NOTION_TOKEN", "")
    return blocks_to_text(NotionClient(token, config.notion_version).read_page_recursive(config.notion_page_id))


def run_task(task: str, config: Config, provider: Provider, notifier: Notifier, fixture: Path | None = None) -> dict[str, Any]:
    if task not in TASKS:
        raise ValueError(f"unknown task: {task}")
    state = StateStore(config.state_dir, task)
    if task == "quant-interview" and not fixture and not config.allow_private_context:
        raise RuntimeError(
            "quant-interview sends private Notion content to the configured provider; "
            "set ALLOW_PRIVATE_CONTEXT=true only after explicitly approving that data flow"
        )
    context = _context(config, fixture) if task == "quant-interview" else ""
    prompts = {
        "research-radar": "Identify 5 timely quantitative-finance or agent-engineering research topics. Return concise bullet points with why each matters and a concrete follow-up.",
        "quant-interview": f"Using the existing private notes below, create 5 novel quant interview questions without duplicating them. Return a JSON array of question strings only.\n\nExisting notes:\n{context}",
        "backtest-auditor": "Produce a practical daily backtest-audit checklist emphasizing leakage, survivorship bias, costs, execution assumptions, multiple testing, and reproducibility.",
    }
    system = "You are a rigorous proactive personal agent. Be concrete, verify assumptions, and never invent completed external actions."
    output = provider.generate(system, prompts[task])
    items = _parse_list(output) if task == "quant-interview" else [output]
    new_items = state.unseen(items)
    if task == "quant-interview":
        existing = {line.strip().casefold() for line in context.splitlines() if line.strip()}
        new_items = [item for item in new_items if item.strip().casefold() not in existing]
    appended = False
    if task == "quant-interview" and new_items and not config.dry_run and not fixture:
        NotionClient(os.getenv("NOTION_TOKEN", ""), config.notion_version).append_questions(config.notion_page_id, new_items)
        appended = True
    if new_items:
        notifier.send(task, "\n".join(new_items))
        if not config.dry_run:
            state.mark_seen(new_items)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": config.dry_run,
        "items": len(items),
        "new_items": len(new_items),
        "notion_appended": appended,
    }
    if not config.dry_run:
        state.add_run(record)
        state.save()
    return record
