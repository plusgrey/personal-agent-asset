"""Scheduled task implementations."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

from automations.config import Config
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


def run_task(task: str, config: Config, provider: Provider, notifier: Notifier) -> dict[str, Any]:
    if task not in TASKS:
        raise ValueError(f"unknown task: {task}")
    state = StateStore(config.state_dir, task)
    context = ""
    prompts = {
        "research-radar": "Identify 5 timely quantitative-finance or agent-engineering research topics. Return concise bullet points with why each matters and a concrete follow-up.",
        "quant-interview": "Create 5 varied quant interview questions across probability, statistics, markets, coding, and modeling. Return a JSON array of question strings only.",
        "backtest-auditor": "Produce a practical daily backtest-audit checklist emphasizing leakage, survivorship bias, costs, execution assumptions, multiple testing, and reproducibility.",
    }
    system = "You are a rigorous proactive personal agent. Be concrete, verify assumptions, and never invent completed external actions."
    output = provider.generate(system, prompts[task])
    items = _parse_list(output) if task == "quant-interview" else [output]
    new_items = state.unseen(items)
    if new_items:
        notifier.send(task, "\n".join(new_items))
        if not config.dry_run:
            state.mark_seen(new_items)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": config.dry_run,
        "items": len(items),
        "new_items": len(new_items),
    }
    if not config.dry_run:
        state.add_run(record)
        state.save()
    return record
