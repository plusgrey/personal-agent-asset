"""Atomic durable state and content-hash deduplication."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


class StateStore:
    def __init__(self, directory: Path, namespace: str):
        self.directory = directory
        self.path = directory / f"{namespace}.json"
        self.data: dict[str, Any] = {"seen": [], "runs": []}
        if self.path.exists():
            self.data.update(json.loads(self.path.read_text(encoding="utf-8")))

    @staticmethod
    def fingerprint(value: str) -> str:
        return hashlib.sha256(value.strip().encode("utf-8")).hexdigest()

    def unseen(self, values: list[str]) -> list[str]:
        seen = set(self.data.get("seen", []))
        return [value for value in values if self.fingerprint(value) not in seen]

    def mark_seen(self, values: list[str]) -> None:
        known = set(self.data.get("seen", []))
        known.update(self.fingerprint(value) for value in values)
        self.data["seen"] = sorted(known)

    def add_run(self, record: dict[str, Any]) -> None:
        runs = list(self.data.get("runs", []))
        runs.append(record)
        self.data["runs"] = runs[-100:]

    def save(self) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(f".tmp.{os.getpid()}")
        temp.write_text(json.dumps(self.data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temp, self.path)
