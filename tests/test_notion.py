from __future__ import annotations

import json
import unittest
from pathlib import Path

from automations.notion import NotionClient, blocks_to_text, load_fixture


class NotionClientTests(unittest.TestCase):
    def test_recursive_read_and_headers(self) -> None:
        requests = []

        def transport(request):
            requests.append(request)
            if "root" in request.full_url:
                return {"results": [{"id": "child", "type": "paragraph", "has_children": True, "paragraph": {"rich_text": [{"plain_text": "parent"}]}}], "has_more": False}
            return {"results": [{"id": "leaf", "type": "paragraph", "has_children": False, "paragraph": {"rich_text": [{"plain_text": "leaf"}]}}], "has_more": False}

        client = NotionClient("test-token", transport=transport)
        blocks = client.read_page_recursive("root")
        self.assertEqual("parent\nleaf", blocks_to_text(blocks))
        self.assertEqual("2026-03-11", requests[0].headers["Notion-version"])
        self.assertEqual("Bearer test-token", requests[0].headers["Authorization"])

    def test_append_question_payload(self) -> None:
        captured = []

        def transport(request):
            captured.append(json.loads(request.data))
            return {"results": []}

        NotionClient("test-token", transport=transport).append_questions("page", ["Question?"])
        self.assertEqual("Question?", captured[0]["children"][0]["bulleted_list_item"]["rich_text"][0]["text"]["content"])
        self.assertEqual({"type": "end"}, captured[0]["position"])
        self.assertEqual({"mode": "silent"}, captured[0]["notifications"])

    def test_append_questions_chunks_at_api_limit(self) -> None:
        sizes = []

        def transport(request):
            sizes.append(len(json.loads(request.data)["children"]))
            return {"results": []}

        NotionClient("test-token", transport=transport).append_questions("page", [f"Q{i}" for i in range(205)])
        self.assertEqual([100, 100, 5], sizes)

    def test_fixture_text(self) -> None:
        fixture = Path(__file__).parent / "fixtures" / "notion_blocks.json"
        self.assertIn("Expected tosses", blocks_to_text(load_fixture(fixture)))


if __name__ == "__main__":
    unittest.main()
