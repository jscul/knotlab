"""Checks that the curated pages keep up with the record.

A claim on THEORY.md whose evidence includes a superseded record, or a record or note with a pending
qualification in data/qualifications.json, must say so in a pending paragraph. When this test fails, the
record has moved on and the card needs a person to update it.

Run from the repository root: python3 -m unittest tests.test_curation
"""
import json
import unittest
from pathlib import Path

from tests.test_theory import LINK, THEORY, parse

ROOT = Path(__file__).resolve().parent.parent


def flagged_evidence():
    """Evidence paths and note folders whose record is superseded or awaits a qualification."""
    qualified = {q["id"] for q in json.loads((ROOT / "data" / "qualifications.json").read_text())["items"]}
    flagged = {}
    for path in ROOT.glob("research/*/discoveries/*.json"):
        record = json.loads(path.read_text())
        reason = "superseded" if record.get("status") == "superseded" else (
            "qualified" if record["id"] in qualified else None)
        if not reason:
            continue
        for evidence in record.get("evidence", []):
            if evidence.get("explanation_path"):
                flagged[evidence["explanation_path"]] = f"{record['id']} is {reason}"
    for note_id in qualified:
        for folder in (ROOT / "proofs" / note_id).glob("*/"):
            flagged[folder.relative_to(ROOT).as_posix() + "/"] = f"{note_id} has an erratum pending"
    return flagged


class CurationTest(unittest.TestCase):
    def test_theory_cards_carry_the_records_status(self):
        flagged = flagged_evidence()
        problems = []
        for _, _, claims in parse(THEORY.read_text()):
            for title, paragraphs in claims:
                pending = any(p.lstrip("*").startswith(("Qualification pending:", "Interpretation pending:",
                                                        "Erratum pending:")) for p in paragraphs)
                for target in LINK.findall("\n\n".join(paragraphs)):
                    if target in flagged and not pending:
                        problems.append(f"{title}: {flagged[target]}")
        self.assertEqual(problems, [], "update these THEORY.md cards")


if __name__ == "__main__":
    unittest.main()
