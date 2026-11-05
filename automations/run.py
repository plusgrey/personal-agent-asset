#!/usr/bin/env python3
"""CLI entry point for proactive automations."""
from __future__ import annotations

import argparse
import json

from automations.config import Config
from automations.notifications import build_notifier
from automations.providers import build_provider
from automations.tasks import TASKS, run_task


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=TASKS)
    parser.add_argument("--dry-run", action="store_true", help="do not persist automation state")
    parser.add_argument("--locale", choices=("en", "zh_cn"))
    args = parser.parse_args()
    config = Config.from_env(dry_run=args.dry_run, locale=args.locale)
    provider = build_provider(config.provider, config.model)
    result = run_task(args.task, config, provider, build_notifier())
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
