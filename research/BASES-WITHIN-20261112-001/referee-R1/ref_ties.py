#!/usr/bin/env python3
"""Referee BASES-WITHIN-R1, E3 (levels of finite seeds), E4 (the three-copy nesting) and the control, with the referee's own code.

    python3 -B ref_ties.py --part seeds|gasket|control

The full tie relation (every pair forced equal or forced unequal), not only the origin's: many varied states (random phases) rule
out most pairs, and every pair left is decided by two SAT calls. Solver: Glucose 4 (the author used CaDiCaL). The gasket is built
from integer points (x, y), x + y <= 2^n, its knots the upward cells {(x, y), (x+1, y), (x, y+1)} with x AND y = 0 (Pascal's
triangle mod 2), not by copying.
"""
import itertools
import json
import random
import sys
import time
from collections import deque
from pathlib import Path

import numpy as np
from pysat.solvers import Glucose4

import ref_lib as R

HERE = Path(__file__).resolve().parent


def cnf(knots, law="NAE"):
    cl = []
    for a, b, c in knots:
        if law == "NAE":
            cl += [[a, b, c], [-a, -b, -c]]
        else:  # exactly one
            cl += [[a, b, c], [-a, -b], [-a, -c], [-b, -c]]
    return cl


def tie_relation(knots, nv, seed=0, rounds=64):
    """None if no state; else (tied, rel): tied[u] = sorted list of v tied to u, and rel[(u, v)] = the forced value of x_u xor x_v"""
    rng = random.Random(seed)
    with Glucose4(bootstrap_with=cnf(knots)) as s:
        if not s.solve():
            return None
        sols = []
        for _ in range(rounds):
            s.set_phases([v if rng.random() < 0.5 else -v for v in range(1, nv + 1)])
            assert s.solve()
            m = s.get_model()
            sols.append([1 if m[v - 1] > 0 else 0 for v in range(1, nv + 1)])
        X = np.array(sols, dtype=np.uint8)                   # rounds x nv
        # u, v survive when x_u xor x_v is the same in every state found
        same = np.ones((nv, nv), dtype=bool)
        for r in range(1, len(sols)):
            d = X[r] ^ X[0]
            same &= ~(d[:, None] ^ d[None, :]).astype(bool)
        cand = [(int(u), int(v)) for u, v in np.argwhere(np.triu(same, 1))]
        rel = {}
        for u, v in cand:
            x = int(X[0, u] ^ X[0, v])
            # forced iff no state has x_u xor x_v = 1 - x: try x_u = 1, x_v = x and x_u = 0, x_v = 1 - x
            a = s.solve(assumptions=[u + 1, v + 1 if x == 1 else -(v + 1)])
            b = s.solve(assumptions=[-(u + 1), -(v + 1) if x == 1 else (v + 1)])
            if not a and not b:
                rel[(u, v)] = x
    tied = {u: [u] for u in range(nv)}
    for (u, v) in rel:
        tied[u].append(v)
        tied[v].append(u)
    return {u: sorted(t) for u, t in tied.items()}, rel


def distances(knots, nv, root):
    adj = [set() for _ in range(nv)]
    for t in knots:
        for a in t:
            adj[a - 1] |= {b - 1 for b in t if b != a}
    d = [-1] * nv
    d[root] = 0
    q = deque([root])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if d[w] < 0:
                d[w] = d[u] + 1
                q.append(w)
    return d


# ---------------------------------------------------------------- E3

SEEDS = {
    "one knot": (3, [(0, 1, 2)]),
    "two knots sharing one": (5, [(0, 1, 2), (2, 3, 4)]),
    "two knots sharing two": (4, [(0, 1, 2), (0, 1, 3)]),
    "closed chain of three": (6, [(0, 1, 2), (2, 3, 4), (4, 5, 0)]),
    "Fano less one knot": (7, list(R.FANO[:-1])),
}


def power(m, E, k):
    """the k-fold Cartesian product: addresses {0..m-1}^k; for each coordinate t, each knot of the seed along every line"""
    addrs = list(itertools.product(range(m), repeat=k))
    idx = {a: i + 1 for i, a in enumerate(addrs)}
    knots = []
    for t in range(k):
        for rest in itertools.product(range(m), repeat=k - 1):
            for (a, b, c) in E:
                knots.append(tuple(idx[rest[:t] + (x,) + rest[t:]] for x in (a, b, c)))
    return addrs, idx, knots


def seed_part():
    out = []
    for name, (m, E) in SEEDS.items():
        sts = R.outer_states(m, E)
        seed_rel = {}
        for a in range(m):
            for b in range(m):
                vals = {s[a] ^ s[b] for s in sts}
                seed_rel[(a, b)] = vals.pop() if len(vals) == 1 else None
        row = {"seed": name, "states": len(sts),
               "tied pairs in the seed": sorted([a, b, seed_rel[(a, b)]] for a in range(m) for b in range(a + 1, m) if seed_rel[(a, b)] is not None),
               "levels": []}
        for k in range(1, 5):
            t0 = time.time()
            addrs, idx, knots = power(m, E, k)
            nv = len(addrs)
            res = tie_relation(knots, nv, seed=k)
            lev = {"level": k, "distinctions": nv, "knots": len(knots)}
            if res is None:
                lev["lives"] = False
                row["levels"].append(lev)
                continue
            tied, rel = res
            # the product rule: tied iff every differing coordinate is tied in the seed; value = sum of the coordinates' values
            pred = {}
            for i, u in enumerate(addrs):
                for j in range(i + 1, nv):
                    v = addrs[j]
                    vals = [seed_rel[(u[t], v[t])] for t in range(k) if u[t] != v[t]]
                    if all(x is not None for x in vals):
                        pred[(i, j)] = sum(vals) % 2
            origins = []
            for a in range(m):
                o = idx[(a,) * k] - 1
                d = distances(knots, nv, o)
                origins.append({"origin": a, "tied": len(tied[o]), "share": len(tied[o]) / nv,
                                "farthest tie": max(d[v] for v in tied[o]), "farthest distinction": max(d)})
            lev.update({"lives": True, "tied pairs": len(rel), "tie relation = product rule (pairs and values)": rel == pred,
                        "origins": origins, "seconds": round(time.time() - t0, 1)})
            row["levels"].append(lev)
        out.append(row)
    return out


# ---------------------------------------------------------------- E4

def gasket(n):
    N = 1 << n
    cells = [(x, y) for x in range(N) for y in range(N - x) if x & y == 0]
    pts = sorted({p for (x, y) in cells for p in ((x, y), (x + 1, y), (x, y + 1))})
    idx = {p: i + 1 for i, p in enumerate(pts)}
    knots = [(idx[(x, y)], idx[(x + 1, y)], idx[(x, y + 1)]) for (x, y) in cells]
    return pts, idx, knots


def gasket_part():
    out = []
    for n in range(8):
        t0 = time.time()
        pts, idx, knots = gasket(n)
        nv = len(pts)
        res = tie_relation(knots, nv, seed=100 + n)
        row = {"level": n, "distinctions": nv, "knots": len(knots)}
        if res is None:
            row["lives"] = False
        else:
            tied, rel = res
            corner = idx[(0, 0)] - 1
            shared = idx[(1, 0)] - 1                 # the meeting corner of the two smallest copies at (0, 0)
            mid = idx[(1 << (n - 1), 0)] - 1 if n >= 1 else None   # the meeting corner of the two largest copies
            d = distances(knots, nv, corner)
            row.update({"lives": True, "tied pairs anywhere": len(rel), "corner tied to": len(tied[corner]) - 1,
                        "smallest shared corner tied to": len(tied[shared]) - 1,
                        "largest shared corner tied to": None if mid is None else len(tied[mid]) - 1,
                        "farthest distinction from the corner": max(d)})
        row["seconds"] = round(time.time() - t0, 1)
        out.append(row)
    return out


# ---------------------------------------------------------------- the control

def control_part():
    """exactly one: inner states the shifts of 001 (period 3), outer (0,1,2), (0,1,3), (2,3,4) on 5 rows; brute force"""
    E = [(0, 1, 2), (0, 1, 3), (2, 3, 4)]
    one = lambda a, b, c: a + b + c == 1
    O = [s for s in itertools.product((0, 1), repeat=5) if all(one(s[a], s[b], s[c]) for a, b, c in E)]
    inner = [(0, 0, 1), (0, 1, 0), (1, 0, 0)]
    # every row must satisfy exactly one on x_i, x_(i+1), x_(i+2) cyclically: check the inner states are exactly these
    rows = [w for w in itertools.product((0, 1), repeat=3) if all(one(w[i], w[(i + 1) % 3], w[(i + 2) % 3]) for i in range(3))]
    lives = [r for r in itertools.product(rows, repeat=5) if all(one(r[a][i], r[b][i], r[c][i]) for a, b, c in E for i in range(3))]
    return {"outer states": len(O), "inner states": rows, "inner states as stated": sorted(rows) == sorted(inner),
            "O[I] states": len(lives)}


if __name__ == "__main__":
    part = sys.argv[sys.argv.index("--part") + 1]
    t0 = time.time()
    res = {"seeds": seed_part, "gasket": gasket_part, "control": control_part}[part]()
    (HERE / f"result_{part}.json").write_text(json.dumps({"rows": res, "seconds": round(time.time() - t0, 1)}, indent=1) + "\n")
    print("wrote", part, round(time.time() - t0, 1), "s")
