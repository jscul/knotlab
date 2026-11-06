#!/usr/bin/env python3
"""NATIVE-PATHS-20261101-001R: confirm that every statement listed in records.md is where the record says, quoted exactly, and that no
other tracked file states the withdrawn composition claim.

    python3 -B records_check.py > records_check.txt"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KC, SN = "KNOT-COMPOSE-20261101-001", "SELECTION-NOTE-20261101-001"
KCA = f"proofs/{KC}A/{KC}A-P001_knots_spaces_compose_only_through_hubs"
SNP = f"proofs/{SN}/{SN}-P001_note"
LOCATIONS = [   # (record number, path, exact quoted text)
    (1, f"{KCA}/proof.md", "# Knot's spaces compose only through hubs"),
    (2, f"{KCA}/proof.md", "the point side accepts exactly equality on its three ports"),
    (3, f"{KCA}/proof.md", "Both constant patterns occur, by complementation. So the point side accepts exactly equality."),
    (4, f"{KCA}/proof.md", "Every failing composition of the knot's spaces passes through a hub."),
    (5, f"{KCA}/proof.md", "\"Knot's spaces meet only through hubs; hub-free failure is parity\" was found in no source checked."),
    (6, f"{KCA}/manifest.json", "\"title\": \"Knot's spaces compose only through hubs\""),
    (6, f"{KCA}/manifest.json", "the point side exactly equality on its ports"),
    (6, f"{KCA}/manifest.json", "So a composition of knot's spaces always meets a hub (equality fan-out)"),
    (7, f"{KCA}/result.json", "The knot's spaces (connected non-2-colourable cubic systems) compose only through hubs."),
    (7, f"{KCA}/result.json", "3 at every nontrivial 3-edge cut of a knot's space, the line side accepts exactly not-all-equal on its slots and the point "
                              "side exactly"),
    (8, f"{KCA}/check.py", "Checks for KNOT-COMPOSE-20261101-001A: the knot's spaces compose only through hubs."),
    (9, f"tickets/{KC}A.json", "\"title\": \"Knot's spaces compose only through hubs\""),
    (9, f"tickets/{KC}A.json", "So the knot's spaces compose only through hubs, and a hub-free failing composition is parity."),
    (9, f"tickets/{KC}A.json", "so knot's spaces compose only through hubs and hub-free failure is parity"),
    (10, f"research/{KC}B/reading.md", "Every composition of knot's spaces passes through a hub, an equality on three channels."),
    (11, f"tickets/{KC}B.json", "every composition meets an equality hub"),
    (12, f"research/{KC}/compose.md", "Yes, natively, but always through hubs."),
    (12, f"research/{KC}/compose.md", "That the knot's spaces meet only through hubs was found in no source checked."),
    (12, f"research/{KC}/compose.md", "A direct knot-to-knot relation with nothing between them exists only"),
    (13, f"proofs/{KC}Z/{KC}Z-P001_epic_closure/proof.md",
     "Across every nontrivial 3-edge cut of a knot's space, the line side is exactly the knot and the point side exactly a hub."),
    (14, f"tickets/{KC}.json", "Composition of the knot's spaces: knots meet through hubs"),
    (14, f"tickets/{KC}.json", "the knot's selected spaces compose natively, but only through hubs"),
    (15, f"research/{KC}/discoveries/{KC}-D001.json", "\"title\": \"The knot's spaces meet only through hubs\""),
    (15, f"research/{KC}/discoveries/{KC}-D001.json", "So the knot's spaces compose natively only through hubs"),
    (16, f"{SNP}/note/selection_note.tex", "compose only through hubs: across every small cut a knot meets an equality"),
    (17, f"{SNP}/note/selection_note.tex", "\\section{Composition: knots meet through hubs}"),
    (18, f"{SNP}/note/selection_note.tex", "the line side accepts exactly $\\NAE$ and the point side exactly $\\EQ$"),
    (18, f"{SNP}/note/selection_note.tex", "compose only through hubs, and a hub-free failing composition is a parity one."),
    (19, f"{SNP}/review_package.md", "| Lemma 11, Theorem 12 | Complementarity; the knot's spaces compose only through hubs. |"),
    (20, f"{SNP}/proof.md", "Complementarity, and composition only through hubs"),
    (21, f"{SNP}/manifest.json", "the knot's spaces compose only through hubs, and hub-free failing composition is parity."),
    (21, f"{SNP}/result.json", "the knot's spaces compose only through hubs, and hub-free failing composition is parity."),
    (21, f"tickets/{SN}.json", "the knot's spaces compose only through hubs."),
    (22, "docs/KNOT_INTUITION.md", "So every failing composition of the knot's spaces passes through a hub"),
    (23, "docs/KNOT_INTUITION.md", "and the point side exactly as one point (an"),
    (24, "docs/KNOT_INTUITION.md", "     - the knot's spaces compose only through hubs."),
]
SURVIVING_INSTANCE = (f"{SNP}/independent_result.json",
                      "I8 the 13-point splice has one nontrivial 3-edge cut; its point side accepts exactly equality and its line side "
                      "exactly not-all-equal")
PHRASES = ["compose only through hubs", "meet only through hubs", "meet through hubs", "a knot meets an equality", "always through hubs",
           "passes through a hub", "composition only through hubs", "compose natively only through hubs"]
ALLOWED_PREFIXES = ("proofs/NATIVE-PATHS-20261101-001", "research/NATIVE-PATHS-20261101-001", "tickets/NATIVE-PATHS-20261101-001",
                    "docs/programs/")   # this epic quotes them; docs/programs is a generated view

ok = True
for num, path, text in LOCATIONS:
    found = (ROOT / path).exists() and text in (ROOT / path).read_text()
    ok &= found
    print(f"record {num:2d}  {'found  ' if found else 'MISSING'}  {path}: {text[:100]}")
inst = (ROOT / SURVIVING_INSTANCE[0]).read_text()
ok &= SURVIVING_INSTANCE[1] in inst
print("surviving instance I8 present:", SURVIVING_INSTANCE[1] in inst)

listed = {p for _, p, _ in LOCATIONS}
tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split("\n")
others = []
for rel in tracked:
    if not rel or not rel.endswith((".md", ".json", ".tex", ".py", ".txt")) or rel in listed or rel.startswith(ALLOWED_PREFIXES):
        continue
    p = ROOT / rel
    if not p.is_file():
        continue
    t = p.read_text(errors="ignore")
    hits = [ph for ph in PHRASES if ph in t]
    if hits:
        others.append((rel, hits))
print("tracked files stating the withdrawn claim outside the listed locations:", others if others else "none")
ok &= not others
print("ALL OK" if ok else "MISMATCH")
sys.exit(0 if ok else 1)
