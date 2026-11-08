"""Checks that docs/ASSUMPTIONS.md keeps its form: every entry has a status, a kind, its five fields and a dated history, the
summary matches the entries, and every link points at a public file that exists.

jscul.dev renders the register from this form, so a malformed register is stopped here, before it is published.

Run from the repository root: python3 -m unittest tests.test_assumptions
In the research workspace: python3 -B publication/knotlab/tests/test_assumptions.py docs/ASSUMPTIONS.md
"""
import re
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "docs" / "ASSUMPTIONS.md"

STATUSES = ("Assumed", "Under challenge", "Confirmed", "Overturned")
KINDS = ("premise", "reading", "scope", "measure", "working premise", "interpretation")
FIELDS = ("Statement", "Why", "Rests on it", "Challenge", "History")
HEADING = re.compile(r"^### (A(\d+)) · (.+)$")
STATUS = re.compile(r"^\*\*(?P<status>[^*]+)\*\* · (?P<date>\d{4}-\d{2}-\d{2}) · (?P<kind>[a-z ]+)$")
FIELD = re.compile(r"^- \*\*(?P<name>[^*]+)\.\*\*(?P<text>.*)$")
HISTORY = re.compile(r"^  - (\d{4}-\d{2}-\d{2}) · \S")
LINK = re.compile(r"\]\(([^)\s]+)\)")
# Public targets, as seen from docs/: the published documents, dated records, and knotlab's own pages.
PUBLIC_DOCS = {"KNOT_INTUITION.md", "FOUNDATIONAL_THESIS.md", "FOUNDATION_READING.md", "COMMON_VERBIAGE.md", "ASSUMPTIONS.md"}
RECORD = re.compile(r"^\.\./(?:proofs|experiments|artifacts|research)/[A-Z0-9-]+-(\d{8})-\d{3}[A-Z]?/")
KNOTLAB_PAGE = re.compile(r"^\.\./(?:(?:INTUITIONS|THEORY|RESULTS|RANKING|FINDINGS|HISTORY|README)\.md|(?:notes|lean|tools|tests)/)")


def slug(heading):
    """GitHub's anchor for a heading."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def sections(text):
    """The level-two sections, by title."""
    return {block.partition("\n")[0].strip(): block.partition("\n")[2] for block in re.split(r"^## ", text, flags=re.M)[1:]}


def table(body):
    rows = [line for line in body.splitlines() if line.startswith("|")]
    return [[cell.strip() for cell in row.strip("|").split("|")] for row in rows[2:]]


def parse_entries(body):
    entries = []
    for block in re.split(r"^(?=### )", body, flags=re.M):
        if not block.startswith("### "):
            continue
        heading, _, rest = block.partition("\n")
        match = HEADING.match(heading)
        entries.append({"heading": heading[4:], "match": match, "lines": rest.strip("\n").splitlines()})
    return entries


def problems(path):
    """Every way the register at path breaks its form; an empty list means it is sound."""
    text = path.read_text()
    found = []
    if not text.startswith("# Assumptions\n"):
        found.append("the register must start with '# Assumptions'")
    parts = sections(text)
    for name in ("Statuses", "Kinds", "Summary", "Entries"):
        if name not in parts:
            found.append(f"missing section '## {name}'")
    if found:
        return found

    if [row[0].strip("*") for row in table(parts["Statuses"])] != list(STATUSES):
        found.append(f"the Statuses table must list {', '.join(STATUSES)}, in order")
    if [row[0].strip("*") for row in table(parts["Kinds"])] != list(KINDS):
        found.append(f"the Kinds table must list {', '.join(KINDS)}, in order")

    entries = parse_entries(parts["Entries"])
    if not entries:
        found.append("the register has no entries")
    seen = []
    for number, entry in enumerate(entries, start=1):
        heading, match, lines = entry["heading"], entry["match"], entry["lines"]
        if not match:
            found.append(f"'{heading}': the heading must read 'A<n> · <assumption>'")
            continue
        ident = match.group(1)
        if int(match.group(2)) != number:
            found.append(f"{ident}: IDs must run A1, A2, … in order, without gaps (expected A{number})")
        status = STATUS.match(lines[0]) if lines else None
        if not status:
            found.append(f"{ident}: the first line must read '**<Status>** · YYYY-MM-DD · <kind>'")
            continue
        if status.group("status") not in STATUSES:
            found.append(f"{ident}: unknown status '{status.group('status')}'")
        if status.group("kind") not in KINDS:
            found.append(f"{ident}: unknown kind '{status.group('kind')}'")
        body = lines[1:]
        while body and not body[0].strip():
            body = body[1:]
        names = [m.group("name") for m in map(FIELD.match, body) if m]
        if names != list(FIELDS):
            found.append(f"{ident}: the fields must be {', '.join(FIELDS)}, in order (found {', '.join(names) or 'none'})")
            continue
        loose = [line for line in body if line.strip() and not FIELD.match(line) and not line.startswith("  ")]
        if loose:
            found.append(f"{ident}: continuation lines must be indented by two spaces: {loose[0][:60]!r}")
        start = next(i for i, line in enumerate(body) if line.startswith("- **History.**"))
        history = [line for line in body[start + 1:] if HISTORY.match(line)]
        dates = [HISTORY.match(line).group(1) for line in history]
        if not dates:
            found.append(f"{ident}: the history needs at least one dated line, '  - YYYY-MM-DD · …'")
            continue
        for value in [status.group("date"), *dates]:
            try:
                date.fromisoformat(value)
            except ValueError:
                found.append(f"{ident}: '{value}' is not a date")
        if dates != sorted(dates, reverse=True):
            found.append(f"{ident}: the history must run newest first")
        if status.group("date") not in dates:
            found.append(f"{ident}: the status date {status.group('date')} must be one of the history's dates")
        seen.append((ident, match.group(3), status.group("kind"), status.group("status"), slug(heading)))

    rows = table(parts["Summary"])
    expected = [[f"[{ident}](#{anchor})", title, kind, state] for ident, title, kind, state, anchor in seen]
    if rows != expected:
        found.append("the Summary table must list every entry, in order, as '| [A<n>](#anchor) | title | kind | status |'")
        for row, want in zip(rows, expected):
            if row != want:
                found.append(f"  first difference: {' | '.join(row)!r}, expected {' | '.join(want)!r}")
                break

    anchors = {slug(m.group(1)) for m in re.finditer(r"^#{1,6} (.+)$", text, re.M)}
    for target in LINK.findall(text):
        if target.startswith(("http://", "https://")):
            continue
        rel, _, anchor = target.partition("#")
        if not rel:
            if anchor not in anchors:
                found.append(f"no heading for the in-page link {target}")
            continue
        record = RECORD.match(rel)
        if not (rel in PUBLIC_DOCS or (record and record.group(1) >= "20261019") or KNOTLAB_PAGE.match(rel)):
            found.append(f"{target}: not a public target (published documents, records dated from 2026-10-19, knotlab pages)")
            continue
        resolved = (path.parent / rel).resolve()
        if not resolved.exists():
            # In the research workspace, knotlab's own pages live under publication/knotlab/.
            resolved = (path.parent.parent / "publication" / "knotlab" / rel[3:]).resolve()
        if not resolved.exists():
            found.append(f"{target}: missing")
        elif anchor and resolved.suffix == ".md":
            if anchor not in {slug(m.group(1)) for m in re.finditer(r"^#{1,6} (.+)$", resolved.read_text(), re.M)}:
                found.append(f"{target}: no such heading")
    return found


class AssumptionsTest(unittest.TestCase):
    def test_register_keeps_its_form(self):
        if not REGISTER.exists():
            self.skipTest("docs/ASSUMPTIONS.md is not published yet")
        self.assertEqual(problems(REGISTER), [])

    def test_a_malformed_register_is_caught(self):
        if not REGISTER.exists():
            self.skipTest("docs/ASSUMPTIONS.md is not published yet")
        head, mark, entries = REGISTER.read_text().partition("\n## Entries\n")
        broken = REGISTER.with_name("ASSUMPTIONS.broken.md")
        try:
            for old, new, in_summary in (("**Assumed** · ", "**Presumed** · ", False), ("- **Why.**", "- **Reason.**", False),
                                         ("### A2 · ", "### A3 · ", False), ("| Assumed |", "| Overturned |", True)):
                if in_summary:
                    broken.write_text(head.replace(old, new, 1) + mark + entries)
                else:
                    broken.write_text(head + mark + entries.replace(old, new, 1))
                self.assertTrue(problems(broken), f"not caught: {old!r} -> {new!r}")
        finally:
            broken.unlink(missing_ok=True)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        issues = problems(Path(sys.argv[1]).resolve())
        print("\n".join(issues) if issues else f"{sys.argv[1]}: the register keeps its form")
        sys.exit(1 if issues else 0)
    unittest.main()
