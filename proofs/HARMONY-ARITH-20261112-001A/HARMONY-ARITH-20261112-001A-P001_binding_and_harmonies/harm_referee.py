#!/usr/bin/env python3
"""Referee (harm_referee.py) for HARMONY-ARITH-20261112-001A, fresh code: it imports nothing from harm_lib and reads only the census
results (result_harmonies.json, result_stitches.json).

R1. Harmonies recomputed at spans 2 to 8 under NAE, odd parity and exactly one, by another method: the window graph as a 0/1 matrix,
    its core by pruning zero rows and columns, a harmony exactly when the core matrix is a permutation matrix, periods from the
    permutation's cycles; every pattern's verdict and periods compared with the census.
R2. Every stitch and overlap recomputed over every shift k = 0 .. q - 1 (not only k mod gcd): the shifts that survive must be a union
    of offsets mod gcd(p, q) (the stitching lemma), and their offsets must equal the census's.
R3. For every surviving stitched state, its period computed directly from the pair sequence must be lcm(p, q)."""
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RULE = {"NAE": lambda t: len(set(t)) > 1, "odd parity": lambda t: sum(t) % 2 == 1, "exactly one": lambda t: sum(t) == 1,
        "clause": lambda t: max(t) == 1}


def matrix(W, kinds, law):
    n = 1 << W
    A = np.zeros((n, n), dtype=np.int8)
    for w in range(n):
        bits = [(w >> j) & 1 for j in range(W)]
        for nb in (0, 1):
            y = bits + [nb]
            if all(RULE[law]((y[k[0]], y[k[1]], y[k[2]])) for k in kinds):
                A[w, (w >> 1) | (nb << (W - 1))] = 1
    return A


def verdict(W, kinds, law):
    A = matrix(W, kinds, law)
    keep = np.ones(len(A), dtype=bool)
    while True:
        sub = A[np.ix_(keep, keep)]
        rows, cols = sub.sum(axis=1), sub.sum(axis=0)
        bad = (rows == 0) | (cols == 0)
        if not bad.any():
            break
        idx = np.nonzero(keep)[0]
        keep[idx[bad]] = False
    if not keep.any():
        return "empty", []
    sub = A[np.ix_(keep, keep)]
    if not ((sub.sum(axis=1) == 1).all() and (sub.sum(axis=0) == 1).all()):
        return "not a harmony", []
    perm = sub.argmax(axis=1)
    seen, lens = set(), []
    for i in range(len(perm)):
        if i in seen:
            continue
        L, j = 0, i
        while j not in seen:
            seen.add(j)
            j = perm[j]
            L += 1
        lens.append(L)
    return "harmony", sorted(lens)


def r1(cells):
    bad, n = [], 0
    for c in cells:
        if c["law"] not in ("NAE", "odd parity", "exactly one") or c["span"] > 8:
            continue
        W = c["span"]
        mine_patterns = [S for k in (1, 2, 3) for S in itertools.combinations(
            [(0, a, b) for a in range(1, W + 1) for b in range(a + 1, W + 1)], k) if max(x[2] for x in S) == W]
        theirs = {tuple(map(tuple, r["kinds"])): ("harmony", r["periods"]) if "periods" in r else (r["class"], []) for r in c["rows"]}
        if len(mine_patterns) != len(theirs):
            bad.append((c["law"], W, "pattern count", len(mine_patterns), len(theirs)))
        for S in mine_patterns:
            n += 1
            v = verdict(W, S, c["law"])
            if theirs.get(S) != (v[0], v[1]):
                bad.append((c["law"], W, S, v, theirs.get(S)))
    return {"patterns compared": n, "disagreements": bad[:20], "number of disagreements": len(bad)}


def r2_r3(B):
    bad2, bad3, n = [], [], 0
    for r in B["pairs"]:
        u, v, law = [int(x) for x in r["u"]], [int(x) for x in r["v"]], r["law"]
        p, q = len(u), len(v)
        g, L = math.gcd(p, q), p * q // math.gcd(p, q)
        for name, theirs in r["surviving"].items():
            kind, off = name.rsplit(" ", 1)
            off = [int(x) for x in off.split(",")]
            ok_shifts = []
            for k in range(q):
                good = True
                for i in range(L):
                    A = lambda j: u[(i + j) % p]
                    Bv = lambda j: v[(i + j + k) % q]
                    if kind == "a a b":
                        t = (A(off[0]), A(off[1]), Bv(off[2]))
                    elif kind == "a b b":
                        t = (A(off[0]), Bv(off[1]), Bv(off[2]))
                    else:
                        t = None  # an overlap
                    good = (A(0) == Bv(off[0])) if t is None else RULE[law](t)
                    if not good:
                        break
                if good:
                    ok_shifts.append(k)
            n += 1
            classes = sorted({k % g for k in ok_shifts})
            union = all(((k % g) in classes) == (k in ok_shifts) for k in range(q))
            if not union or classes != sorted(theirs):
                bad2.append((r["u"], r["v"], name, classes, theirs))
            for k in ok_shifts[:1]:
                seq = [(u[i % p], v[(i + k) % q]) for i in range(2 * L)]
                per = next(d for d in range(1, L + 1) if all(seq[i] == seq[i + d] for i in range(L)))
                if per != L:
                    bad3.append((r["u"], r["v"], name, per, L))
    return ({"stitches compared": n, "disagreements": bad2[:20], "number of disagreements": len(bad2)},
            {"stitched states checked": n, "period not lcm": bad3[:20], "number": len(bad3)})


def main():
    cells = json.loads((HERE / "result_harmonies.json").read_text())["checks"]["result"]["cells"]
    B = json.loads((HERE / "result_stitches.json").read_text())["checks"]["result"]
    out = {"R1 harmonies": r1(cells)}
    out["R2 stitches"], out["R3 stitched periods"] = r2_r3(B)
    out["passed"] = (out["R1 harmonies"]["number of disagreements"] == 0 and out["R2 stitches"]["number of disagreements"] == 0
                     and out["R3 stitched periods"]["number"] == 0)
    (HERE / "referee.json").write_text(json.dumps(out, indent=1) + "\n")
    print("referee passed" if out["passed"] else "referee FAILED")
    sys.exit(0 if out["passed"] else 1)


if __name__ == "__main__":
    main()
