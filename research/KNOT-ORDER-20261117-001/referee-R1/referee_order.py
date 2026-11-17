"""Referee R1 for KNOT-ORDER-20261117-001 (own code; nothing imported from the study).

  ../../../.venv/bin/python -B referee_order.py > referee_order.json     (from this directory; item 0 runs tools/knotlab)

0. B(a, b, c) (excluding 010 and 101 on a, b, c) under the canonical knot test (knotlab check).
1. R1's counts.
2. Growth to n = 16 under the five rules.  The states rule is run blind: before each read the distinctions are renamed by a fresh
   random permutation, the rule sees only the set of allowed states (as bit patterns under the hidden names), finds the two ends as
   the pair at the largest disagreement count, picks one at random, and adds B(other end, chosen end, new).  The random-earlier rule
   is also rerun with the study's own seed derivation to reproduce its counts.
3. Every three-place constraint (all 255 nonempty excluded sets on (new, a, b), every a < b, which covers every place order), added
   to the line on m = 3..14: which keep the base a line (thresholds along some order), and of which kind.  Counted as distinct
   constraints; the 34 knots marked.
4. K1 exhaustively for constraints on 2, 3 and 4 places at n = 5, 6, 7: any constraint that keeps every threshold and excludes a
   two-change state has a place in each of its three blocks.
5. K2: the strongest window-r base (every window of r consecutive places restricted to its thresholds) at n = r + 1 .. r + 3.
6. K7 on grids 3x3, 3x4, 4x4, 3x5, 4x5: states, d = 2 L1, betweenness = boxes.
7. The line as the implication chain in the gauge of one distinction; its correlation profile.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import random
import subprocess
import sys

import numpy as np

BTW = frozenset({(0, 1, 0), (1, 0, 1)})
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


# ---------- bases as numpy state lists ----------

def states_of(n, knots):
    """knots: list of (places, excluded set of tuples).  Returns the allowed states as an int array."""
    s = np.arange(1 << n, dtype=np.int64)
    ok = np.ones(len(s), bool)
    for pl, ex in knots:
        bits = [(s >> p) & 1 for p in pl]
        for e in ex:
            m = np.ones(len(s), bool)
            for b, v in zip(bits, e):
                m &= b == v
            ok &= ~m
    return s[ok]


def thresholds(order):
    n = len(order)
    out = set()
    for t in range(n + 1):
        a = sum(1 << order[i] for i in range(t, n))
        out |= {a, ((1 << n) - 1) ^ a}
    return out


def dcount(n, sts):
    bits = ((np.asarray(sts)[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int64)
    return (bits[:, :, None] != bits[:, None, :]).sum(axis=0)


def line_order(n, sts):
    """If the states are exactly the thresholds of some order, return it (read from the counts), else None."""
    sts = list(map(int, sts))
    if len(sts) != 2 * n:
        return None
    D = dcount(n, sts)
    u, v = np.unravel_index(np.argmax(D), D.shape)
    order = sorted(range(n), key=lambda w: D[u, w])
    return order if set(sts) == thresholds(order) else None


# ---------- 0, 1 ----------

def knot_test():
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "tools"))
    r = subprocess.run([sys.executable, "-B", "-m", "knotlab", "check", "--cnf", "a ~b c; ~a b ~c", "--loops", "a", "c",
                        "--contact", "b", "--json"], capture_output=True, text=True, env=env, cwd=ROOT, timeout=120)
    j = json.loads(r.stdout)
    return {k: j[k] for k in ("allowed", "variables", "is_knot", "binding", "invisible_in_parts", "loss_on_erasure",
                              "coexistence", "pairwise_definable")}


def r1():
    out = {}
    for n in (4, 5):
        cons = set(map(int, states_of(n, [((i, i + 1, i + 2), BTW) for i in range(n - 2)])))
        allt = set(map(int, states_of(n, [(t, BTW) for t in itertools.combinations(range(n), 3)])))
        out[n] = {"consecutive": len(cons), "all_triples": len(allt),
                  "extra": sorted("".join(str((s >> i) & 1) for i in range(n)) for s in cons - allt)}
    out["B(0,1,2)+B(0,2,3)"] = len(states_of(4, [((0, 1, 2), BTW), ((0, 2, 3), BTW)]))
    return out


# ---------- 2: growth ----------

def fib(k):
    a, b = 0, 1
    for _ in range(k):
        a, b = b, a + b
    return a


def grow(rule, nmax=16, seed=0):
    rng = random.Random(seed)
    knots = [((0, 1, 2), BTW)]
    order = [0, 1, 2]
    last2 = [1, 2]
    rows = []
    for n in range(3, nmax + 1):
        sts = states_of(n, knots)
        lo = line_order(n, sts)
        row = {"n": n, "states": int(len(sts)), "line": lo is not None,
               "line_along_rule_order": lo is not None and set(map(int, sts)) == thresholds(order)}
        if rule == "neighbour":
            row["2F(n+1)"] = 2 * fib(n + 1)
        rows.append(row)
        if n == nmax:
            break
        new = n
        if rule == "start":
            knots.append(((order[0], order[-1], new), BTW)); order.append(new)
        elif rule == "neighbour":
            knots.append(((order[-2], order[-1], new), BTW)); order.append(new)
        elif rule == "random":
            x = rng.choice(order[:-1])
            row["x_is_start"] = x == order[0]
            knots.append(((x, order[-1], new), BTW)); order.append(new)
        elif rule == "spiral":
            a, b = last2
            knots.append(((a, new, b), BTW))
            i, j = sorted((order.index(a), order.index(b)))
            order.insert(j, new)
            last2 = [b, new]
        elif rule == "states":
            perm = list(range(n)); rng.shuffle(perm)          # hidden names: position p is shown as perm[p]
            inv = {perm[p]: p for p in range(n)}
            shown = [sum(((int(s) >> p) & 1) << perm[p] for p in range(n)) for s in sts]
            D = dcount(n, shown)
            top = D.max()
            pairs = [(u, v) for u in range(n) for v in range(u + 1, n) if D[u, v] == top]
            row["ends_unique"] = len(pairs) == 1
            row["ends_at_2(n-1)"] = int(top) == 2 * (n - 1)
            row["neighbour_pairs_at_2"] = int(((D == 2).sum()) // 2)
            u, v = pairs[0]
            near, far = (u, v) if rng.random() < 0.5 else (v, u)
            knots.append(((inv[far], inv[near], new), BTW))
            order = (order if order[-1] == inv[near] else order[::-1]) + [new]
    return rows


def grow_study_seed():
    """The random-earlier rule with the study's seed derivation, to reproduce its counts."""
    rng = random.Random(int.from_bytes(hashlib.sha256(b"KO:random").digest()[:8], "little"))
    knots = [((0, 1, 2), BTW)]
    order = [0, 1, 2]
    out = []
    for n in range(3, 15):
        out.append(int(len(states_of(n, knots))))
        if n == 14:
            break
        x = rng.choice(order[:-1])
        knots.append(((x, order[-1], n), BTW)); order.append(n)
    return out


# ---------- 3: every single three-place constraint ----------

KNOTS34 = set()
for k in range(1, 5):
    for ex in itertools.combinations(list(itertools.product((0, 1), repeat=3)), k):
        if all(sum(a != b for a, b in zip(x, y)) != 1 for x, y in itertools.combinations(ex, 2)):
            KNOTS34.add(frozenset(ex))


def single_constraints(m):
    old = sorted(thresholds(list(range(m))))
    new = m
    keep = []
    pats = list(itertools.product((0, 1), repeat=3))
    for a, b in itertools.combinations(range(m), 2):
        for k in range(1, 256):
            E = frozenset(p for i, p in enumerate(pats) if (k >> i) & 1)      # patterns on (new, a, b)
            sts = []
            for s in old:
                xa, xb = (s >> a) & 1, (s >> b) & 1
                for v in (0, 1):
                    if (v, xa, xb) not in E:
                        sts.append(s | (v << new))
            if len(sts) != 2 * (m + 1):
                continue
            lo = line_order(m + 1, sts)
            if lo is None:
                continue
            pos = lo.index(new)
            nb = sorted(lo[q] for q in (pos - 1, pos + 1) if 0 <= q <= m)
            kind = ("B(a, new, b), a and b neighbours" if E == frozenset({(1, 0, 0), (0, 1, 1)}) and b == a + 1 else
                    "B(new, a, b): beyond end a" if E == frozenset({(1, 0, 1), (0, 1, 0)}) and (a, b) == (0, m - 1) else
                    "B(new, b, a): beyond end b" if E == frozenset({(0, 0, 1), (1, 1, 0)}) and (a, b) == (0, m - 1) else
                    "other")
            keep.append({"a": a, "b": b, "excluded_on_new_a_b": sorted(E), "is_one_of_34": E in KNOTS34,
                         "kind": kind, "new_neighbours_in_line": nb})
    return {"m": m, "line_keeping": len(keep), "kinds": sorted({k["kind"] for k in keep}),
            "all_in_34": all(k["is_one_of_34"] for k in keep), "constraints": keep if m <= 4 else None}


# ---------- 4, 5: K1 and K2 ----------

def k1(n):
    th = thresholds(list(range(n)))
    bad, tested = 0, 0
    for k in (2, 3, 4):
        for pl in itertools.combinations(range(n), k):
            seen = {tuple((s >> x) & 1 for x in pl) for s in th}
            free = [t for t in itertools.product((0, 1), repeat=k) if t not in seen]
            for r in range(1, len(free) + 1):
                for ex in itertools.combinations(free, r):
                    ex = set(ex)
                    tested += 1
                    for p in range(1, n - 1):
                        for q in range(p + 1, n):
                            for flip in (0, 1):
                                s = sum(1 << i for i in range(p, q)) ^ (((1 << n) - 1) if flip else 0)
                                if tuple((s >> x) & 1 for x in pl) in ex:
                                    blocks = (range(0, p), range(p, q), range(q, n))
                                    if not all(any(x in bl for x in pl) for bl in blocks):
                                        bad += 1
    return {"n": n, "constraints_tested": tested, "violations": bad}


def k2(r, n):
    pats = set()
    for t in range(r + 1):
        a = tuple([0] * t + [1] * (r - t))
        pats |= {a, tuple(1 - x for x in a)}
    ex = set(itertools.product((0, 1), repeat=r)) - pats
    sts = set(map(int, states_of(n, [(tuple(range(i, i + r)), ex) for i in range(n - r + 1)])))
    s1r = sum(1 << i for i in range(1, r))     # 0 1..1 0..0: changes after position 1 and after position r (1-based)
    return {"r": r, "n": n, "states": len(sts), "(1,r)_state_survives": s1r in sts, "line": len(sts) == 2 * n}


# ---------- 6: grids ----------

def grid(nr, nc):
    pts = [(i, j) for i in range(nr) for j in range(nc)]
    idx = {p: k for k, p in enumerate(pts)}
    inbox = lambda a, b, c: (min(a[0], c[0]) <= b[0] <= max(a[0], c[0]) and min(a[1], c[1]) <= b[1] <= max(a[1], c[1]))
    triples = [(idx[a], idx[b], idx[c]) for a, c in itertools.combinations(pts, 2) for b in pts
               if b not in (a, c) and inbox(a, b, c)]
    n = len(pts)
    s = np.arange(1 << n, dtype=np.int64)
    ok = np.ones(len(s), bool)
    for a, b, c in triples:
        xa, xb, xc = (s >> a) & 1, (s >> b) & 1, (s >> c) & 1
        ok &= ~((xa == xc) & (xa != xb))
    sts = s[ok]
    cuts = set()
    for t in range(1, nr):
        m = sum(1 << idx[p] for p in pts if p[0] >= t); cuts |= {m, ((1 << n) - 1) ^ m}
    for t in range(1, nc):
        m = sum(1 << idx[p] for p in pts if p[1] >= t); cuts |= {m, ((1 << n) - 1) ^ m}
    cuts |= {0, (1 << n) - 1}
    D = dcount(n, sts)
    l1 = all(D[idx[a], idx[b]] == 2 * (abs(a[0] - b[0]) + abs(a[1] - b[1])) for a in pts for b in pts)
    btw = {(u, w, v) for u in range(n) for v in range(u + 1, n) for w in range(n)
           if w not in (u, v) and D[u, w] > 0 and D[w, v] > 0 and D[u, v] == D[u, w] + D[w, v]}
    box = {(min(a, c), b, max(a, c)) for a, b, c in triples}
    return {"grid": f"{nr}x{nc}", "box_triples": len(triples), "states": int(len(sts)), "2(r+c)-2": 2 * (nr + nc) - 2,
            "states_are_row_and_column_cuts": set(map(int, sts)) == cuts, "d_is_2L1": l1, "betweenness_is_box": btw == box}


# ---------- 7: the line in the gauge of one distinction ----------

def gauge(n):
    th = thresholds(list(range(n)))
    y = {s ^ (((1 << n) - 1) if s & 1 else 0) for s in th}           # y = x xor x_0
    upsets = {sum(1 << i for i in range(t, n)) for t in range(1, n + 1)}  # y_0 = 0, y_1 <= y_2 <= ... <= y_(n-1)
    N = len(th)
    corr = []
    for r in range(1, n):
        dd = sum(((s >> 0) ^ (s >> r)) & 1 for s in th)
        corr.append(1 - 2 * dd / N)
    return {"n": n, "gauge_image_is_chain_upsets": y == upsets, "each_twice": len(th) == 2 * len(y),
            "states_per_distinction": (2 * n) ** (1 / n), "correlation_end_to_r": corr}


def main():
    out = {"0_knot_test_B": knot_test(), "1_R1": r1()}
    out["2_growth"] = {rule: grow(rule, seed=7) for rule in ("start", "neighbour", "random", "spiral", "states")}
    out["2_states_rule_more_seeds"] = {sd: all(r["line"] for r in grow("states", seed=sd)) for sd in range(1, 21)}
    out["2_random_study_seed"] = grow_study_seed()
    mism = 0
    for sd in range(1, 41):
        allstart = True
        for r in grow("random", nmax=12, seed=sd):
            mism += r["line"] != allstart
            allstart = allstart and r.get("x_is_start", True)
    out["2_random_line_iff_every_x_was_start_40_seeds_mismatches"] = mism
    out["3_single_constraints"] = [single_constraints(m) for m in range(3, 15)]
    out["4_K1"] = [k1(n) for n in (5, 6, 7)]
    out["5_K2"] = [k2(r, n) for r in (3, 4, 5) for n in range(r + 1, r + 4)]
    out["6_K7"] = [grid(*g) for g in ((3, 3), (3, 4), (4, 4), (3, 5), (4, 5))]
    out["7_gauge"] = [gauge(n) for n in (4, 6, 8, 10)]
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
