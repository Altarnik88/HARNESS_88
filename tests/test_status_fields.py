from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from llm_wiki.status_fields import (  # noqa: E402
    missing_required_fields,
    normalize,
    parse_fields,
    parse_status,
    value_is_unknown,
)


class StatusFieldsTests(unittest.TestCase):
    def test_parse_status_returns_casefolded_status_or_missing(self) -> None:
        self.assertEqual(parse_status("# Doc\n\nStatus: Needs-Review\n"), "needs-review")
        self.assertEqual(parse_status("# Doc\n\nNo status here\n"), "missing")

    def test_parse_fields_normalizes_keys_and_optionally_values(self) -> None:
        text = """# Doc

Status: approved
site-type: Ecommerce Store
frontend_preview_approval: Approved
notes: Keep Original Spacing
"""

        self.assertEqual(
            parse_fields(text),
            {
                "site_type": "Ecommerce Store",
                "frontend_preview_approval": "Approved",
                "notes": "Keep Original Spacing",
            },
        )
        self.assertEqual(
            parse_fields(text, normalize_values=True),
            {
                "site_type": "ecommerce-store",
                "frontend_preview_approval": "approved",
                "notes": "keep-original-spacing",
            },
        )

    def test_unknown_and_required_field_helpers_are_shared(self) -> None:
        unknown_values = {"", "unknown", "TBD", "todo", "not selected", "unselected", "pending"}
        for value in unknown_values:
            self.assertTrue(value_is_unknown(value, unknown_values=unknown_values))

        fields = {"goal": "Launch", "audience": "unknown", "country": "Poland"}
        self.assertEqual(
            missing_required_fields(fields, ["goal", "audience", "country", "language"], unknown_values=unknown_values),
            ["audience", "language"],
        )
        self.assertEqual(normalize("Needs Review"), "needs-review")


if __name__ == "__main__":
    unittest.main()
