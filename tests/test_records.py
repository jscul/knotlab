"""Checks that the published record is complete and its generated files are current.

Run from the repository root: python3 -m unittest tests.test_records
"""
import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATED = re.compile(r"-20\d{6}-\d{3}[A-Z]?$")
LINK = re.compile(r"\]\(([^)\s]+)\)")


def build_module():
    spec = importlib.util.spec_from_file_location("build", ROOT / "scripts" / "build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RecordsTest(unittest.TestCase):
    def test_generated_files_are_current(self):
        files, _, _ = build_module().outputs()
        stale = [name for name, text in files.items() if (ROOT / name).read_text() != text]
        self.assertEqual(stale, [], "run python3 scripts/build.py")

    def test_every_link_in_the_lists_resolves(self):
        for name in ("RESULTS.md", "RANKING.md"):
            for target in LINK.findall((ROOT / name).read_text()):
                if target.startswith(("http://", "https://", "#")):
                    continue
                self.assertTrue((ROOT / target.split("#")[0]).exists(), f"{name}: missing {target}")

    def test_every_published_folder_has_its_ticket(self):
        tickets = {p.stem for p in (ROOT / "tickets").glob("*.json")}
        for top in ("proofs", "experiments", "artifacts", "research"):
            for folder in (ROOT / top).iterdir():
                if folder.is_dir() and DATED.search(folder.name):
                    self.assertIn(folder.name, tickets, f"{top}/{folder.name} has no ticket")

    def test_epic_closures_find_their_tickets(self):
        tickets = {p.stem for p in (ROOT / "tickets").glob("*.json")}
        for closure in (ROOT / "proofs").glob("*Z/*/check.py"):
            epic = closure.parent.parent.name[:-1]
            for suffix in re.findall(r'"([A-Z])"', closure.read_text()):
                if f"{epic}{suffix}" in tickets or not (ROOT / "proofs" / f"{epic}{suffix}").exists():
                    continue
                self.fail(f"{closure.parent.name} reads tickets/{epic}{suffix}.json, which is not published")


if __name__ == "__main__":
    unittest.main()
