"""Minimal official Notion REST API client for recursive page reads and appends."""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable

Transport = Callable[[urllib.request.Request], dict[str, Any]]


class NotionClient:
    def __init__(self, token: str, version: str = "2026-03-11", transport: Transport | None = None):
        if not token:
            raise ValueError("NOTION_TOKEN is required")
        self.token = token
        self.version = version
        self.transport = transport or self._urlopen
        self.base_url = "https://api.notion.com/v1"

    def _urlopen(self, request: urllib.request.Request) -> dict[str, Any]:
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Notion API HTTP {exc.code}: {detail}") from exc

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(
            self.base_url + path,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": self.version,
                "Content-Type": "application/json",
            },
        )
        return self.transport(request)

    def list_children(self, block_id: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            query = "?page_size=100"
            if cursor:
                query += "&start_cursor=" + urllib.parse.quote(cursor)
            payload = self._request("GET", f"/blocks/{block_id}/children{query}")
            results.extend(payload.get("results", []))
            if not payload.get("has_more"):
                return results
            cursor = payload.get("next_cursor")

    def read_page_recursive(self, page_id: str) -> list[dict[str, Any]]:
        def walk(parent: str) -> list[dict[str, Any]]:
            output: list[dict[str, Any]] = []
            for block in self.list_children(parent):
                copied = dict(block)
                if block.get("has_children"):
                    copied["children"] = walk(block["id"])
                output.append(copied)
            return output

        return walk(page_id)

    def append_questions(self, page_id: str, questions: list[str]) -> dict[str, Any]:
        if not questions:
            return {"results": []}
        responses: list[dict[str, Any]] = []
        for offset in range(0, len(questions), 100):
            children = [
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": question}}]},
                }
                for question in questions[offset : offset + 100]
            ]
            responses.append(
                self._request(
                    "PATCH",
                    f"/blocks/{page_id}/children",
                    {"children": children, "position": {"type": "end"}, "notifications": {"mode": "silent"}},
                )
            )
        return {"results": [item for response in responses for item in response.get("results", [])]}


def load_fixture(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("results", payload)


def blocks_to_text(blocks: list[dict[str, Any]]) -> str:
    lines: list[str] = []

    def collect(items: list[dict[str, Any]]) -> None:
        for block in items:
            kind = block.get("type", "")
            value = block.get(kind, {})
            rich_text = value.get("rich_text", []) if isinstance(value, dict) else []
            text = "".join(item.get("plain_text") or item.get("text", {}).get("content", "") for item in rich_text)
            if text:
                lines.append(text)
            collect(block.get("children", []))

    collect(blocks)
    return "\n".join(lines)
