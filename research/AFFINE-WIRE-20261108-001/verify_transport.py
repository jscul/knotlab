#!/usr/bin/env python3
"""Verification added after the search (AFFINE-WIRE-20261108-001B): the twelve smallest persistently composing chains whose contacts
are at least two cells apart on the middle ring, so that the middle ring carries c1's past across at least one of its own cells,
checked on their full state spaces; with the row periods and the eventual supports of the contacts.

    .venv/bin/python3 -B research/AFFINE-WIRE-20261108-001/verify_transport.py   writes verify_transport.json"""
import json
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/AFFINE-WIRE-20261108-001B/AFFINE-WIRE-20261108-001B-E001_affine_search"))
import run as B  # noqa: E402

W, C = B.W, B.C
T0 = time.time()
rows = json.loads((ROOT / "artifacts/AFFINE-WIRE-20261108-001B/AFFINE-WIRE-20261108-001B-E001_affine_search/run/positives.json").read_text())["rows"]
found = [r for r in rows if r[5]]
far = sorted([r for r in found if r[8] >= 2], key=lambda r: (sum(r[1]), r[1], r[2], r[0]))
out = {"persistently composing chains with d >= 2": len(far),
       "row periods among them": {f"{a}/{b}": n for (a, b), n in Counter(tuple(r[7]) for r in far).items()},
       "both contacts compose among them": sum(1 for r in far if r[6]),
       "verified": []}
for r in far[:12]:
    rules, sizes, k, law1, law2 = tuple(r[0]), tuple(r[1]), r[2], tuple(r[3]), tuple(r[4])
    b = B.brute(rules, sizes, k, law1, law2)
    mrows, N, blocks = W.linear_matrix(rules, sizes, k, law1, law2)
    s2, T1, p2 = W.row_orbit(mrows, 1 << 1)
    support = s2[-1]
    cells = {x: bin(support & W.block_mask(blocks, x)).count("1") for x in "ABC"}
    out["verified"].append({"chain": r, "full state space (c1 persists, c2 persists, c2 composes, T1, period)": b,
                            "agrees": b is not None and b[:3] == (True, True, True),
                            "c2's eventual support: cells of A, B and C": cells, "c2 holds c2(0) eventually": bool(support & 2)})
out["all verified"] = all(v["agrees"] for v in out["verified"])
out["seconds"] = round(time.time() - T0, 1)
(HERE / "verify_transport.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({k: v for k, v in out.items() if k != "verified"}, indent=1))
for v in out["verified"][:6]:
    print(v["chain"][:5], v["agrees"], v["c2's eventual support: cells of A, B and C"])
