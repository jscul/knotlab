"""Referee R1 for VARIABLE-OUTPUT-READER-20261118-001J, ring.md: LABELLED CROSS-CHECK that runs RING-READ's published incremental
reader (experiments/RING-READ-20261118-001B/.../reader3.py, read-only, unmodified) on tables the referee computes itself.

  ../../../.venv/bin/python -B ring_tie.py > referee_j_ring_tie.json      (from this directory)

1. 001J's 27-distinction history (frontier.json, two shrinking joins), its exact table from the referee's own shore enumeration,
   read under the original naming and under the transposition (0 24), at stages pooled above D = 4 and with every exact D.
2. The question that decides what 001J's finding means for RING-READ itself: is the reader's answer on the ring independent of how
   the distinctions are named?  The ring at rounds 10, 12, 14, 15 and 16 (and 20 and 25 with `late`), its table (the referee's
   exact all-sides table), read under the study's naming and under eight random renamings each.
"""
import itertools
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/RING-READ-20261118-001B/RING-READ-20261118-001B-E001_incremental"))
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1"))
sys.path.insert(0, str(ROOT / "research/RING-READ-20261118-001/referee-R1"))
import reader3 as R3  # noqa: E402  (the published reader, read-only)
import referee_f as F  # noqa: E402
import crosscheck_reader as CR  # noqa: E402  (the referee's exact all-sides table)

R = R3.R
FAM = ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001J/VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six"


def renamed(table, perm):
    return {tuple(sorted((perm[a], perm[b]))): d for (a, b), d in table.items()}


def read(table, top, perm, truth):
    inv = {v: k for k, v in perm.items()}
    got = R3.r3(renamed(table, perm), top)
    back = {frozenset(inv[x] for x in s) for s in got}
    return {"missing": sorted(sorted(s) for s in truth - back), "extra": sorted(sorted(s) for s in back - truth)}


def part_27():
    rows = json.load(open(FAM / "frontier.json"))["closure"]["first_histories_by_shrinking_joins"]["2"]
    n = 1 + max(max(r) for r in rows)
    K, _ = F.bond_table(rows, n)
    truth = {frozenset(r) for r in rows}
    top = max(map(len, rows))
    exact = {(a, b): int(K[a][b]) - 1 for a, b in itertools.combinations(range(n), 2)}
    ident = {x: x for x in range(n)}
    swap = dict(ident)
    swap[0], swap[24] = 24, 0
    out = {"width": n, "junctions": len(rows), "largest junction": top, "largest D": max(exact.values()),
           "the five loose distinctions": sorted(x for x in range(n) if sum(x in r for r in rows) == 1)}
    for H in (4, 5, max(exact.values())):
        pooled = {p: min(d, H + 1) for p, d in exact.items()}
        out[f"pooled above D = {H}"] = {"original naming": read(pooled, H + 1 if H < top else top, ident, truth),
                                        "names 0 and 24 exchanged": read(pooled, H + 1 if H < top else top, swap, truth)}
    # eight random renamings at D = 4
    rng = random.Random(27)
    pooled = {p: min(d, 5) for p, d in exact.items()}
    res = []
    for _ in range(8):
        perm = list(range(n))
        rng.shuffle(perm)
        r = read(pooled, 5, dict(enumerate(perm)), truth)
        res.append(not r["missing"] and not r["extra"])
    out["eight random renamings at D = 4: exact"] = sum(res)
    return out


def part_ring(rounds=(10, 12, 14, 15, 16)):
    out = {}
    for T in rounds:
        P = R.grow(T)
        st = R.stars_of(P)
        truth = set(st)
        top = max(map(len, st))
        tab = CR.exact_table(st, top)
        labels = sorted({b for s in st for b in s})
        rng = random.Random(1000 + T)
        rows = []
        ident = {x: x for x in labels}
        r0 = read(tab, top, ident, truth)
        for _ in range(8):
            perm = labels[:]
            rng.shuffle(perm)
            r = read(tab, top, dict(zip(labels, perm)), truth)
            rows.append([len(r["missing"]), len(r["extra"])])
        out[f"round {T}"] = {"junctions": len(st), "largest junction": top, "study's naming: missing, extra": [len(r0["missing"]), len(r0["extra"])],
                             "eight random renamings: missing, extra": rows,
                             "renamings giving every junction exactly": sum(1 for a, b in rows if a == 0 and b == 0)}
        print(T, json.dumps(out[f"round {T}"]), file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    if sys.argv[1:] == ["late"]:          # rounds 20 and 25, run separately
        print(json.dumps({"the ring, later rounds": part_ring((20, 25))}, indent=1, default=str))
    else:
        print(json.dumps({"27-distinction history": part_27(), "the ring": part_ring()}, indent=1, default=str))
