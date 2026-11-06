#!/usr/bin/env python3
"""PARITY-CORRECTION-20261031-001R: confirm that every statement listed in records.md is where the record says, quoted exactly, and
that the unaffected records do not use the withdrawn claim.

    python3 -B records_check.py > records_check.log"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MS, PIN = "MUTUAL-SELECTION-20261031-001", "PINNING-20261031-001"
LOCATIONS = [   # (record number, path, exact quoted text)
    (1, f"research/{MS}B/report.md", "It\n     is a generalized equality, affine and polynomial on every graph."),
    (1, f"research/{MS}B/report.md", "So parity's family is easy everywhere, and its unsolvable spaces select nothing."),
    (1, f"research/{MS}B/report.md", "Parity's failures are recognisable, but its whole family is easy, so the selection is vacuous."),
    (2, f"research/{MS}B/parity_clause.py", "for every lam: a generalized equality, affine, polynomial on every graph."),
    (3, f"research/{MS}B/manifest.json", "its whole coupling family [1, lam, 1, lam] is a generalized equality (affine) for every lam"),
    (4, f"tickets/{MS}B.json", "its whole coupling family [1, lam, 1, lam] is affine, so parity selects nothing beyond the universally easy"),
    (4, f"tickets/{MS}B.json", "signed parity fails recognisably but its whole family is affine (selects nothing)"),
    (5, f"tickets/{MS}.json", "parity fails recognisably but its whole family is affine"),
    (6, f"research/{MS}/decision.md", "but its whole coupling family is affine, so it selects nothing."),
    (7, f"proofs/{MS}Z/{MS}Z-P001_epic_closure/proof.md", "but its whole coupling family is affine, so it selects nothing."),
    (8, f"proofs/{PIN}C/{PIN}C-P001_the_knot_is_the_only_law_with_mutual_selection/result.json",
     "no (affine: its whole family is polynomial everywhere)"),
    (8, f"proofs/{PIN}C/{PIN}C-P001_the_knot_is_the_only_law_with_mutual_selection/check.py",
     "no (affine: its whole family is polynomial everywhere)"),
    (9, f"proofs/{PIN}C/{PIN}C-P001_the_knot_is_the_only_law_with_mutual_selection/proof.md", "Parity's family is affine, and the clause"),
    (10, f"proofs/{PIN}C/{PIN}C-P001_the_knot_is_the_only_law_with_mutual_selection/proof.md",
     "| parity | yes (inconsistent linear systems) | yes (linear algebra) | no: affine, its counts are 2^{nullity} or 0 | no |"),
    (11, f"research/{PIN}/discoveries/{PIN}-D002.json", "parity is affine, the clause never fails"),
    (12, "docs/KNOT_INTUITION.md", "With signs, parity fails recognisably but makes nothing new easy; the clauses never fail."),
    (12, "docs/KNOT_INTUITION.md", "Every other three-place law either never fails, is affine, or can build a value out of relations alone"),
]
UNAFFECTED = ["proofs/KNOT-COUPLING-20261031-001A", "proofs/KNOT-COUPLING-20261031-001B", "proofs/KNOT-COUPLING-20261031-001C",
              "research/KNOT-COUPLING-20261031-001", "proofs/PLAIN-COUNT-20261031-001A", "proofs/PLAIN-COUNT-20261031-001B",
              "proofs/PLAIN-BRACE-20261031-001A", "proofs/PLAIN-BRACE-20261031-001B", f"proofs/{PIN}A", f"proofs/{PIN}B",
              "research/COUNT-NOTE-20261031-001", "proofs/COUNT-NOTE-20261031-001"]
PHRASES = ["generalized equality", "whole family", "whole coupling family", "1, lam, 1, lam", "[1, λ, 1, λ]", "easy everywhere"]
ok = True
for num, path, text in LOCATIONS:
    found = (ROOT / path).exists() and text in (ROOT / path).read_text()
    ok &= found
    print(f"record {num:2d}  {'found  ' if found else 'MISSING'}  {path}: {text.splitlines()[-1].strip()[:90]}")
hits = []
for d in UNAFFECTED:
    base = ROOT / d
    if not base.exists():
        print(f"(absent, skipped) {d}")
        continue
    for p in sorted(base.rglob("*")):
        if p.is_file() and p.suffix in (".md", ".py", ".json", ".tex"):
            t = p.read_text(errors="ignore")
            for ph in PHRASES:
                if ph in t and "parity" in t.lower():
                    hits.append((str(p.relative_to(ROOT)), ph))
print("unaffected records using the withdrawn claim:", hits if hits else "none")
ok &= not hits
print("ALL OK" if ok else "MISMATCH")
sys.exit(0 if ok else 1)
