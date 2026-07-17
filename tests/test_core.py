import json
import tempfile
import unittest
from pathlib import Path

from app.analysis import mock_analysis
from app.ledger import build_ledger
from app.report import render_report


class CoreTests(unittest.TestCase):
    def test_lossless_grouping_and_report(self):
        results = [
            {"status": 3, "code": "bad_value", "message": "Value is invalid", "location": "line 4"},
            {"status": 3, "code": "bad_value", "message": "Value is invalid", "location": "line 9"},
            {"status": 0, "code": "document_validity", "message": "Checked", "location": "document"},
        ]
        ledger = build_ledger(results)
        self.assertEqual(ledger["occurrenceCount"], 3)
        self.assertEqual(ledger["findingGroups"][0]["occurrenceCount"], 2)
        analysis = mock_analysis(ledger)
        template = Path(__file__).resolve().parents[1] / "templates" / "report.html"
        output = render_report("example.xml", "example.xml.validation.json", ledger,
                               analysis, {}, template)
        self.assertIn("example.xml", output)
        self.assertIn("bad_value", output)
        self.assertIn("line 4", output)
        self.assertIn("line 9", output)
        self.assertNotIn("{{REPORT_TITLE}}", output)


if __name__ == "__main__":
    unittest.main()
