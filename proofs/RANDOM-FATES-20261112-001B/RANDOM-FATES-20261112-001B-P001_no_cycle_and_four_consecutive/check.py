"""Finite checks of RANDOM-FATES-20261112-001B-P001 (proof.md beside this file).

K1  T1 by brute force on random patterns with no cycle of knots (7 to 11 distinctions, connected and not): every state enumerated,
    no tie, the hollow triples exactly the knots, and the least bond of every pair, searched over all sets, of steps apart + 2
    (and none for pairs in different components).
K2  T2 exhaustively: every set of knots within four consecutive of 8 distinctions allows a state.
K3  T3: the ten knots on five distinctions allow no state; the least number of knots of a contradiction with every knot within
    five consecutive distinctions, on 5 to 8 distinctions (exact minimum hitting set by MaxSAT).

Run from the repository root:
    .venv/bin/python -B proofs/RANDOM-FATES-20261112-001B/RANDOM-FATES-20261112-001B-P001_no_cycle_and_four_consecutive/check.py [--write]
"""

from __future__ import annotations

import itertools
import json
import os
import random
import sys
from collections import deque

import numpy as np
from pysat.examples.rc2 import RC2
from pysat.formula import WCNF

HERE = os.path.dirname(os.path.abspath(__file__))


def states(n, knots):
    s = np.arange(1 << n, dtype=np.int64)
    ok = np.ones(len(s), dtype=bool)
    for t in knots:
        bits = [(s >> v) & 1 for v in t]
        tot = bits[0] + bits[1] + bits[2]
        ok &= (tot != 0) & (tot != 3)
    return s[ok]


def ncodes(st, S):
    code = np.zeros(len(st), dtype=np.int64)
    for i, v in enumerate(S):
        code |= ((st >> v) & 1) << i
    return len(np.unique(code))


def is_bond(st, S):
    if ncodes(st, S) == 1 << len(S):
        return False
    return all(ncodes(st, [x for x in S if x != y]) == 1 << (len(S) - 1) for y in S)


def steps(n, knots, src):
    nbr = [set() for _ in range(n)]
    for t in knots:
        for a, b in itertools.combinations(t, 2):
            nbr[a].add(b)
            nbr[b].add(a)
    d = {src: 0}
    q = deque([src])
    while q:
        x = q.popleft()
        for y in nbr[x]:
            if y not in d:
                d[y] = d[x] + 1
                q.append(y)
    return d


def random_forest(n_target, rng, components):
    """A pattern with no cycle of knots: each component grown by knots with one existing and two new distinctions."""
    knots, n = [], 0
    for _ in range(components):
        knots.append((n, n + 1, n + 2))
        base = n
        n += 3
        size = rng.randrange(3, n_target + 1)
        while n - base + 2 <= size:
            a = rng.randrange(base, n)
            knots.append((a, n, n + 1))
            n += 2
    return n, knots


def k1(rng):
    out = {"patterns": 0, "pairs": 0, "violations": []}
    for trial in range(30):
        comps = 1 if trial < 20 else 2
        n, knots = random_forest(11 if comps == 1 else 5, rng, comps)
        if n > 13:
            continue
        st = states(n, knots)
        out["patterns"] += 1
        kset = {tuple(sorted(t)) for t in knots}
        for a, b in itertools.combinations(range(n), 2):
            if ncodes(st, [a, b]) < 4:
                out["violations"].append(["tie", n, knots, a, b])
        for t in itertools.combinations(range(n), 3):
            if is_bond(st, list(t)) != (t in kset):
                out["violations"].append(["triple", n, knots, t])
        for u, v in itertools.combinations(range(n), 2):
            d = steps(n, knots, u).get(v)
            least = None
            rest = [w for w in range(n) if w not in (u, v)]
            for size in range(2, n + 1):
                if any(is_bond(st, [u, v, *ex]) for ex in itertools.combinations(rest, size - 2)):
                    least = size
                    break
            out["pairs"] += 1
            if (d is None and least is not None) or (d is not None and least != d + 2):
                out["violations"].append(["bond", n, knots, u, v, d, least])
    return out


def k2():
    n = 8
    knots = [t for t in itertools.combinations(range(n), 3) if t[2] - t[0] <= 3]
    s = np.arange(1 << n, dtype=np.int64)
    masks = []
    for t in knots:
        tot = sum((s >> v) & 1 for v in t)
        bad = (tot == 0) | (tot == 3)
        masks.append(int("".join("1" if x else "0" for x in bad[::-1]), 2))
    full = (1 << (1 << n)) - 1
    no_state = 0
    for sub in range(1 << len(knots)):
        m = 0
        for i in range(len(knots)):
            if sub >> i & 1:
                m |= masks[i]
        if m == full:
            no_state += 1
    return {"distinctions": n, "knots within four consecutive": len(knots), "sets": 1 << len(knots), "sets with no state": no_state}


def least_contradiction(n, span):
    knots = [t for t in itertools.combinations(range(n), 3) if t[2] - t[0] <= span]
    w = WCNF()
    for s in range(1 << n):
        viol = [i + 1 for i, t in enumerate(knots) if len({(s >> v) & 1 for v in t}) == 1]
        w.append(viol)
    for i in range(len(knots)):
        w.append([-(i + 1)], weight=1)
    with RC2(w) as rc2:
        m = rc2.compute()
        if m is None:
            return None, None
        chosen = [knots[i] for i in range(len(knots)) if m[i] > 0]
    return len(chosen), chosen


def k3():
    k5 = list(itertools.combinations(range(5), 3))
    res = {"ten knots on five allow a state": len(states(5, k5)) > 0}
    for n in range(5, 9):
        size, chosen = least_contradiction(n, 4)
        res[f"least contradiction within five consecutive on {n}"] = {"knots": size, "example": chosen}
    for n in range(4, 9):
        size, _ = least_contradiction(n, 3)
        res[f"least contradiction within four consecutive on {n}"] = size
    return res


def main():
    rng = random.Random(20261112)
    out = {"K1": k1(rng), "K2": k2(), "K3": k3()}
    ok = (not out["K1"]["violations"] and out["K2"]["sets with no state"] == 0
          and not out["K3"]["ten knots on five allow a state"]
          and all(out["K3"][f"least contradiction within four consecutive on {n}"] is None for n in range(4, 9)))
    out["status"] = "passed" if ok else "failed"
    print(json.dumps(out, indent=1, default=str))
    if "--write" in sys.argv:
        res = {"schema_version": 3, "artifact_id": "RANDOM-FATES-20261112-001B-P001", "kind": "proof",
               "ticket": "RANDOM-FATES-20261112-001B", "proof": "RANDOM-FATES-20261112-001B-P001", **out}
        with open(os.path.join(HERE, "result.json"), "w") as f:
            json.dump(res, f, indent=1, default=str)
            f.write("\n")


if __name__ == "__main__":
    main()
