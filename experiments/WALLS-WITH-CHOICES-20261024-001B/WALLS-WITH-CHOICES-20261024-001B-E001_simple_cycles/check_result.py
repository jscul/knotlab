#!/usr/bin/env python3
"""Independent checker for WALLS-WITH-CHOICES-20261024-001B-E001.

- Recomputes, from the frozen rows of DIRECTIONAL-RIGIDITY-20261023-001A-E001, the frozen histogram of every row and compares it
  with the producer's simple-cycle histogram; recomputes P1, P2 and the verdict.
- For sampled configurations of every placement, torus and twist (and the certified examples), computes the simple-cycle pattern
  with its own Python wall graph (WALLS-WITH-CHOICES-20261024-001A-P001's check) and compares it with the producer's engine run on
  that single configuration and with the true pattern certified by PySAT (a strip of 30 periods with no assignment, or a cyclic
  cover of at most 24 sheets with one).

    .venv/bin/python -B check_result.py
"""

from __future__ import annotations

import importlib.util
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

from pysat.solvers import Glucose3

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "WALLS-WITH-CHOICES-20261024-001B" / HERE.name
FROZEN = ROOT / "artifacts/DIRECTIONAL-RIGIDITY-20261023-001A/DIRECTIONAL-RIGIDITY-20261023-001A-E001_rigidity/rows.jsonl"
_spec = importlib.util.spec_from_file_location(
    "wall_check", ROOT / "proofs/WALLS-WITH-CHOICES-20261024-001A/WALLS-WITH-CHOICES-20261024-001A-P001_wall_theorem/check.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)
DR = A.DR
BENDING = (54, 62, 109, 110, 111, 125, 147, 151, 155, 159, 203, 215)
SAMPLES = 6
STRIP, COVERS = 30, 24


def solvable(cl):
    with Glucose3(bootstrap_with=cl) as s:
        return s.solve()


def true_pattern(R, L, M, q, x, classes):
    m = und = 0
    for k, c in enumerate(classes):
        n, cl, _ = DR.clauses(R, L, M, q, x, c, STRIP, False)
        if not solvable(cl):
            m |= 1 << k
        elif not any(solvable(DR.clauses(R, L, M, q, x, c, s, True)[1]) for s in range(1, COVERS + 1)):
            und |= 1 << k
    return m, und


def python_pattern(R, L, M, q, x, classes, moves, fit):
    G = A.wall_graph(R, L, M, q, x, moves)
    cyc, capped = A.simple_cycles(G, cap=200000)
    odd = DR.odd_classes(classes, fit, q)
    m = 0
    for k, c in enumerate(classes):
        if c in odd and not any(A.good(c, e, A.overlaps(p)) for p, e in cyc):
            m |= 1 << k
    return m, capped


def main() -> int:
    problems = []
    result = json.loads((OUT / "result.json").read_text())
    rows = [json.loads(l) for l in (OUT / "rows.jsonl").read_text().splitlines() if l.strip()]
    frozen = {(r["R"], r["L"], r["M"]): r for r in (json.loads(l) for l in FROZEN.read_text().splitlines() if l.strip())}
    p = {"P1_3x3_simple_cycles_match": True, "P2_3x4_simple_cycles_match": True}
    seen = set()
    for r in rows:
        key = (r["R"], r["L"], r["M"], r["twist"])
        seen.add(key)
        t = frozen[(r["R"], r["L"], r["M"])]["twists"][r["twist"]]
        obs = {int(m): n for m, n in t["patterns"].items()}
        obs[0] = obs.get(0, 0) + t["sat"]
        if {int(m): n for m, n in r["frozen_histogram"].items()} != obs:
            problems.append(f"frozen histogram misread {key}")
        if r["total"] != t["total"] or sum(r["simple_cycle_histogram"].values()) != t["total"]:
            problems.append(f"total {key}")
        eq = {int(m): n for m, n in r["simple_cycle_histogram"].items()} == obs
        if eq != r["equal"]:
            problems.append(f"equality flag {key}")
        p["P1_3x3_simple_cycles_match" if (r["L"], r["M"]) == (3, 3) else "P2_3x4_simple_cycles_match"] &= eq
    expected = {(R, L, M, q) for R in BENDING for L, M in ((3, 3), (3, 4)) for q in ("00", "01", "10", "11")}
    if seen != expected:
        problems.append("rows missing or extra")
    own_verdict = ("invalid" if result["control_failures"] else
                   "supported" if all(p.values()) else "refuted")
    if own_verdict != result["verdict"]:
        problems.append(f"verdict {result['verdict']} against {own_verdict}")
    # per-configuration comparisons
    build = Path(tempfile.mkdtemp(prefix="walls-check-"))
    binary = str(build / "walls")
    subprocess.run(["gcc", "-O2", "-o", binary, str(HERE / "walls.c")], check=True)
    rng = random.Random(20261024)
    cert = {"configurations": 0, "engine equals own Python": 0, "own Python equals PySAT truth": 0, "undetermined": 0,
            "capped": 0, "selective among them": 0}
    sys.path.insert(0, str(HERE))
    import run as producer
    examples = [(R, 3, 3, (int(q[0]), int(q[1])), x) for R, q, x, _p in producer.CERTIFIED]
    for R in BENDING:
        for L, M in ((3, 3), (3, 4)):
            classes = [tuple(c) for c in frozen[(R, L, M)]["classes"]]
            moves = DR.wall_moves(L, M)
            fit = DR.fitting(R, L, M)
            todo = [(R, L, M, q, rng.randrange(1 << (2 * L * M))) for q in DR.TWISTS if q not in fit for _ in range(SAMPLES)]
            todo += [e for e in examples if e[0] == R and (L, M) == (3, 3)]
            for R_, L_, M_, q, x in todo:
                out = subprocess.run([binary, str(R), str(L), str(M), str(q[0]), str(q[1]), str(x), str(x + 1), "0"]
                                     + [str(v) for c in classes for v in c], capture_output=True, text=True, check=True).stdout.split("\n")
                eng = int(out[1].split()[0])
                own, capped = python_pattern(R, L, M, q, x, classes, moves, fit)
                truth, und = true_pattern(R, L, M, q, x, classes)
                cert["configurations"] += 1
                cert["engine equals own Python"] += eng == own
                cert["capped"] += capped
                if und:
                    cert["undetermined"] += 1
                    continue
                cert["own Python equals PySAT truth"] += own == truth
                odd = DR.odd_classes(classes, fit, q)
                om = sum(1 << k for k, c in enumerate(classes) if c in odd)
                cert["selective among them"] += truth != om and bin(truth).count("1") >= 2
            print("checked", R, f"{L}x{M}", cert, flush=True)
    if cert["engine equals own Python"] != cert["configurations"]:
        problems.append("engine and own Python differ on some configuration")
    if cert["own Python equals PySAT truth"] != cert["configurations"] - cert["undetermined"]:
        problems.append("simple-cycle pattern differs from the certified truth on some configuration")
    report = {"problems": problems, "n_problems": len(problems), "own_verdict": own_verdict, **p, "certificates": cert}
    print(json.dumps(report, indent=1))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
