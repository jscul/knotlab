"""Checks that THEORY.md keeps its form: every claim has one label and its evidence, and every link resolves.

Run from the repository root: python3 -m unittest tests.test_theory
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEORY = ROOT / "THEORY.md"

LABELS = ("Premise", "Proved", "Proved (Lean)", "Proved (note)", "Checked", "Conjecture", "Reading", "Open")
STATUS = re.compile(r"^\*\*(?P<label>[^*]+)\*\*(?: · (?P<date>\d{4}-\d{2}-\d{2}))?(?: · (?P<note>reopenable))?$")
PENDING = ("Qualification pending:", "Interpretation pending:", "Erratum pending:")
LINK = re.compile(r"\[[^\]]+\]\(([^)\s]+)\)")


def slug(heading):
    """GitHub's anchor for a heading."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def anchors(path):
    return {slug(m.group(1)) for m in re.finditer(r"^#{1,6} (.+)$", path.read_text(), re.M)}


def parse(text):
    sections = []
    for block in re.split(r"^## ", text, flags=re.M)[1:]:
        heading, _, body = block.partition("\n")
        match = re.match(r"(\d+)\. (.+)$", heading)
        if not match:
            continue
        claims = []
        for part in re.split(r"^### ", body, flags=re.M)[1:]:
            title, _, rest = part.partition("\n")
            paragraphs = [p.strip() for p in rest.strip().split("\n\n") if p.strip()]
            claims.append((title.strip(), paragraphs))
        sections.append((int(match.group(1)), match.group(2), claims))
    return sections


class TheoryTest(unittest.TestCase):
    def setUp(self):
        self.text = THEORY.read_text()
        self.sections = parse(self.text)

    def test_sections_are_numbered_in_order(self):
        self.assertEqual([n for n, _, _ in self.sections], list(range(1, len(self.sections) + 1)))
        self.assertGreaterEqual(len(self.sections), 9)

    def test_every_claim_has_a_label_a_statement_and_evidence(self):
        for _, section, claims in self.sections:
            self.assertTrue(claims, section)
            for title, paragraphs in claims:
                status = STATUS.match(paragraphs[0])
                self.assertIsNotNone(status, f"{title}: status line {paragraphs[0]!r}")
                self.assertIn(status.group("label"), LABELS, title)
                self.assertTrue(paragraphs[-1].startswith("Evidence: "), f"{title}: last paragraph must list evidence")
                statements = [p for p in paragraphs[1:-1] if not p.lstrip("*").startswith(PENDING)]
                self.assertTrue(statements, f"{title}: no statement")
                if status.group("label") in ("Proved", "Proved (Lean)", "Proved (note)", "Checked", "Conjecture"):
                    self.assertTrue(status.group("date"), f"{title}: a result needs its date")

    def test_pending_qualifications_are_carried(self):
        for record in ("KNOT-COMPOSE-20261101-001-D001", "FACE-CLAIM-20261103-001-D003", "STRIP-RELAY-20261103-001-D001"):
            self.assertIn(record, self.text)
        self.assertIn("*Interpretation pending: whether counted length is a native magnitude", self.text)
        self.assertIn("*Erratum pending: abstract item 5, Section 6 and Theorem 12", self.text)
        self.assertIn("proofs/PHASE-HALO-20261103-001A/", self.text)

    def test_every_link_resolves(self):
        own = anchors(THEORY)
        for target in LINK.findall(self.text):
            if target.startswith(("http://", "https://")):
                continue
            path, _, anchor = target.partition("#")
            if not path:
                self.assertIn(anchor, own, f"in-page anchor {target}")
                continue
            resolved = ROOT / path
            self.assertTrue(resolved.exists(), f"missing {path}")
            if path.endswith("/"):
                self.assertTrue(resolved.is_dir(), f"not a folder: {path}")
            if anchor:
                self.assertIn(anchor, anchors(resolved), f"missing anchor {target}")


if __name__ == "__main__":
    unittest.main()
