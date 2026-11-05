"""Notification backends."""
from __future__ import annotations

import json
import os
import urllib.request
from typing import Protocol


class Notifier(Protocol):
    def send(self, title: str, body: str) -> None: ...


class StdoutNotifier:
    def send(self, title: str, body: str) -> None:
        print(f"[{title}]\n{body}")


class WebhookNotifier:
    def __init__(self, url: str):
        self.url = url

    def send(self, title: str, body: str) -> None:
        payload = json.dumps({"title": title, "body": body}).encode("utf-8")
        request = urllib.request.Request(self.url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=20) as response:
            if response.status >= 300:
                raise RuntimeError(f"webhook returned HTTP {response.status}")


def build_notifier() -> Notifier:
    url = os.getenv("NOTIFICATION_WEBHOOK_URL")
    return WebhookNotifier(url) if url else StdoutNotifier()
