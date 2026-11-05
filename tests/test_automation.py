from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from automations.config import Config
from automations.state_store import StateStore
from automations.tasks import run_task


class FakeProvider:
    def generate(self, system: str, prompt: str) -> str:
        return '["New probability question?", "Expected tosses until HHT?"]'


class RecordingNotifier:
    def __init__(self):
        self.messages = []

    def send(self, title: str, body: str) -> None:
        self.messages.append((title, body))


class AutomationTests(unittest.TestCase):
    def test_state_deduplicates_and_persists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = StateStore(Path(tmp), "task")
            store.mark_seen(["same"])
            store.save()
            self.assertEqual([], StateStore(Path(tmp), "task").unseen(["same"]))

    def test_live_private_context_requires_explicit_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Config(state_dir=Path(tmp), dry_run=True)
            with self.assertRaisesRegex(RuntimeError, "ALLOW_PRIVATE_CONTEXT"):
                run_task("quant-interview", config, FakeProvider(), RecordingNotifier())

    def test_fixture_implies_no_notion_write_or_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            notifier = RecordingNotifier()
            fixture = Path(__file__).parent / "fixtures" / "notion_blocks.json"
            config = Config(state_dir=Path(tmp), dry_run=True)
            result = run_task("quant-interview", config, FakeProvider(), notifier, fixture)
            self.assertFalse(result["notion_appended"])
            self.assertFalse(list(Path(tmp).glob("*.json")))
            self.assertEqual(1, len(notifier.messages))
            self.assertNotIn("Expected tosses", notifier.messages[0][1])


if __name__ == "__main__":
    unittest.main()
