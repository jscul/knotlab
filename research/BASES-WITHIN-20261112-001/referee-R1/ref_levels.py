#!/usr/bin/env python3
"""Referee BASES-WITHIN-R1: the E1 follow-up after the run (descriptive), recounted with the referee's own code.

    python3 -B ref_levels.py

Level 2 of a harmony on Z_P^2: arrays whose every row and column is a state. Counted by backtracking over rows with every column
kept a prefix of some state (no SAT), capped at 20,000 as in the follow-up, and written after each harmony. Also: that the cyclic words
of length P allowed by the kinds are exactly the states (so Z_P^k is exact); the linear states u(m.c + a) and mirror lifts; the
tie class of the origin at level 2 (SAT, the referee's tie code) against the product of the line ties; level 3 of 0011."""
import itertools
import json
import sys
import time
from pathlib import Path

import ref_lib as R
import ref_ties as T

HERE = Path(__file__).resolve().parent


def count_level2(W, cap):
    P = len(W[0])
    pre = [set() for _ in range(P + 1)]
    for w in W:
        for l in range(P + 1):
            pre[l].add(w[:l])
    n = 0
    cols = [()] * P

    def go(r):
        nonlocal n
        if r == P:
            n += 1
            return n <= cap
        for w in W:
            new = [cols[c] + (w[c],) for c in range(P)]
            if all(x in pre[r + 1] for x in new):
                old = cols[:]
                cols[:] = new
                ok = go(r + 1)
                cols[:] = old
                if not ok:
                    return False
        return True
    finished = go(0)
    return n if finished else None


def count_level3_0011():
    """level 3 of 0011 on Z_4^3 by backtracking: a state of 0011 along c at each (a, b), every line along a and b kept a prefix"""
    W = [(0, 0, 1, 1), (0, 1, 1, 0), (1, 1, 0, 0), (1, 0, 0, 1)]
    pre = [{w[:l] for w in W} for l in range(5)]
    x = {}
    n = 0

    def go(q):
        nonlocal n
        if q == 16:
            n += 1
            return
        a, b = divmod(q, 4)
        for w in W:
            if all(tuple(x[(a, bb)][c] for bb in range(b)) + (w[c],) in pre[b + 1] and
                   tuple(x[(aa, b)][c] for aa in range(a)) + (w[c],) in pre[a + 1] for c in range(4)):
                x[(a, b)] = w
                go(q + 1)
                del x[(a, b)]
    go(0)
    return n


def kinds_cyclic(h):
    P = h["P"]
    words = [w for w in itertools.product((0, 1), repeat=P)
             if all(R.nae(w[i], w[(i + a) % P], w[(i + b) % P]) for a, b in h["kinds"] for i in range(P))]
    return sorted(words) == R.states(h)


def known(W):
    P = len(W[0])
    Ws = set(W)
    good = [m for m in range(P) if all(tuple(u[(m * i) % P] for i in range(P)) in Ws for u in W)]
    coords = list(itertools.product(range(P), repeat=2))
    lin = {tuple(u[(m1 * c1 + m2 * c2) % P] for (c1, c2) in coords) for u in W for m1 in good for m2 in good}
    xor = {tuple(u1[c1] ^ u2[c2] for (c1, c2) in coords) for u1 in W for u2 in W}
    return len(lin), len(xor), len(lin | xor)


def ties_level2(h):
    P = h["P"]
    idx = {c: i + 1 for i, c in enumerate(itertools.product(range(P), repeat=2))}
    knots = []
    for a, b in h["kinds"]:
        for i in range(P):
            for j in range(P):
                knots.append((idx[(i, j)], idx[((i + a) % P, j)], idx[((i + b) % P, j)]))
                knots.append((idx[(i, j)], idx[(i, (j + a) % P)], idx[(i, (j + b) % P)]))
    tied, rel = T.tie_relation(knots, P * P, seed=7, rounds=48)
    inv = {i - 1: c for c, i in idx.items()}
    got = {inv[v] for v in tied[idx[(0, 0)] - 1]}
    W = R.states(h)
    line = {i for i in range(P) if len({u[0] ^ u[i] for u in W}) == 1}
    return sorted(line), got == {(i, j) for i in line for j in line}, len(got)


if __name__ == "__main__":
    t0 = time.time()
    rows = []
    for i, h in enumerate(R.harmonies()):
        W = R.states(h)
        t = time.time()
        c20 = count_level2(W, 20000)
        lin, xor, union = known(W)
        line, prod, ntied = ties_level2(h)
        rows.append({"i": i, "orbits": h["orbits"], "P": h["P"], "states": len(W), "kinds give exactly the states on Z_P": kinds_cyclic(h),
                     "level 2 (cap 20,000)": c20, "linear": lin, "mirror lifts": xor,
                     "known union": union, "rigid": None if c20 is None else c20 == lin,
                     "not below the known states": c20 is None or c20 >= union,
                     "line ties of place 0": line, "level-2 ties of the origin = product": prod, "seconds": round(time.time() - t, 1)})
        print(i, h["orbits"][:3], c20, lin, union, prod, round(time.time() - t, 1), flush=True)
        (HERE / "result_levels.json").write_text(json.dumps({"rows": rows, "partial": True}, indent=1) + "\n")
    res = {"rows": rows, "level 3 of 0011": count_level3_0011(), "seconds": round(time.time() - t0, 1)}
    (HERE / "result_levels.json").write_text(json.dumps(res, indent=1) + "\n")
    print("wrote levels", res["seconds"], "s")
