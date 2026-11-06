"""Lane A (MUTUAL-SELECTION-20261031-001A): plain systems and the exactly-one law.

1. Symmetric three-place laws are allowed-weight sets W. A law is a knot (K1-K3: full two-place projections, not everything allowed)
   exactly for the seven W printed below. A plain cubic system always satisfies a law that allows a constant colouring (0 in W: all
   zero; 3 in W: all one). So plain unsolvable systems can exist only for W in {{1}, {2}, {1, 2}}, and the only knot among them is
   not-all-equal; random cubic systems confirm that each of the three does fail.
2. Exactly-one on a cubic system H asks for a set S of points meeting every line once; in the dual H* (points = lines of H, lines =
   points of H) S is an exact cover of the points of H* by its lines, every point of H* lying on exactly three lines. That is exact
   cover by 3-sets with every element in exactly three sets, NP-complete (Gonzalez 1985). The script checks the correspondence (equal
   counts) on random cubic systems.
Run: .venv/bin/python -B plain.py [--write]"""
import itertools
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
T0 = time.time()
OUT = {}
rng = random.Random(20261031)


def full_projections(W):
    S = [s for s in itertools.product((0, 1), repeat=3) if sum(s) in W]
    return all({(s[i], s[j]) for s in S} == {(0, 0), (0, 1), (1, 0), (1, 1)} for i, j in ((0, 1), (0, 2), (1, 2)))


laws = {}
for r in range(1, 4):
    for W in itertools.combinations(range(4), r):
        laws[str(set(W))] = {"knot": full_projections(set(W)), "allows a constant colouring": 0 in W or 3 in W}
OUT["1 symmetric laws"] = laws
OUT["1 laws that can fail on plain cubic systems"] = [k for k, v in laws.items() if not v["allows a constant colouring"]]
OUT["1 knots that can fail on plain cubic systems"] = [k for k, v in laws.items() if v["knot"] and not v["allows a constant colouring"]]


def random_cubic(n):
    while True:
        slots = [p for p in range(n) for _ in range(3)]
        rng.shuffle(slots)
        lines = [tuple(slots[3 * i:3 * i + 3]) for i in range(n)]
        if all(len(set(l)) == 3 for l in lines) and len({tuple(sorted(l)) for l in lines}) == n:
            return lines


def solutions(lines, n, W):
    return sum(1 for c in itertools.product((0, 1), repeat=n) if all(sum(c[p] for p in l) in W for l in lines))


fails = {}
for W in ({1}, {2}, {1, 2}):
    for n in (6, 9, 12):
        bad = sum(1 for t in range(60) if solutions(random_cubic(n), n, W) == 0)
        fails[f"W = {W}, n = {n}"] = f"{bad}/60 random plain cubic systems unsolvable"
FANO = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]
fails["W = {1, 2}: the Fano plane (random systems almost never fail: the failing ones are exactly the knot's spaces)"] = \
    f"{solutions(FANO, 7, {1, 2})} colourings"
OUT["1 each of the three fails on some plain cubic systems"] = fails

# 2. exactly-one = exact cover in the dual
agree, total = 0, 0
for n in (6, 9, 12):
    for t in range(40):
        H = random_cubic(n)
        transversals = solutions(H, n, {1})
        dual = [tuple(i for i, l in enumerate(H) if p in l) for p in range(n)]       # one dual line per point of H
        covers = 0
        for k in range(n + 1):
            for S in itertools.combinations(range(n), k):
                covered = [0] * n
                for s in S:
                    for x in dual[s]:
                        covered[x] += 1
                covers += all(c == 1 for c in covered)
        agree += transversals == covers
        total += 1
OUT["2 exact transversals of H = exact covers of the dual H* (each element in exactly three triples)"] = f"{agree}/{total} systems agree"
ok = (OUT["1 knots that can fail on plain cubic systems"] == ["{1, 2}"] and agree == total
      and all(not v.startswith("0/") for k, v in fails.items() if not k.startswith("W = {1, 2}, n"))
      and fails["W = {1, 2}: the Fano plane (random systems almost never fail: the failing ones are exactly the knot's spaces)"] == "0 colourings")
OUT["seconds"] = round(time.time() - T0, 1)
print(json.dumps(OUT, indent=1))
print("ALL OK" if ok else "FAIL")
if "--write" in sys.argv:
    (HERE / "results.json").write_text(json.dumps(OUT, indent=1) + "\n")
