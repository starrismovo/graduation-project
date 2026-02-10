import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from prompts.hr_agent_llm import safe_load_json, extract_followup_question


class TestDeepSeekParsing(unittest.TestCase):
    def test_invalid_json(self):
        raw = '{invalid json'
        resp = safe_load_json(raw)
        self.assertEqual(resp.get("_error"), "invalid_json")

    def test_error_field(self):
        resp = {"error": {"message": "Invalid API key"}}
        parsed = extract_followup_question(resp)
        self.assertIsNone(parsed.get("question"))
        self.assertEqual(parsed.get("error"), "Invalid API key")

    def test_empty_choices(self):
        resp = {"choices": []}
        parsed = extract_followup_question(resp)
        self.assertIsNone(parsed.get("question"))
        self.assertEqual(parsed.get("error"), "empty_choices")


if __name__ == '__main__':
    unittest.main()
