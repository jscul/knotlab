"""Checks for SEQUENTIAL-WALL-20261116-001B-P001 (proof.md beside this file).

Exhaustive over every atom pattern on four distinctions (all 2^12 sets of
atoms, all 16 held sets) and random larger patterns:
  T1  phase(v) = rank(v) for every v, with rank by relaxation and forced
      sets checked against all states;
  T2  rank(v) <= log2 fringe(v);
  T3  no distinction reused  =>  fringe(v) <= |H| and rank(v) <= log2 |H|;
  T4a no distinction demanded several ways  =>  the unfolding criterion
      equals forcing;
  T5  the class table of the 34 three-place knots (knots_table.py, rerun
      here: 2 AC0, 2 parity-L, 14 P, 16 NP, each P-hardness by an explicit
      definition of the atom or its dual);
  T5b the not-all-equal propagation gadget equals circuit evaluation
      (the experiment's gates, G4, rerun here);
  T6  the dual law on acyclic patterns (the experiment's gates, G7, rerun).
Each statement is written here a second time, in plain Python with explicit
derivation search, independently of atoms.py's numpy code.
"""

import itertools
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EXP = os.path.join(ROOT, "experiments", "SEQUENTIAL-WALL-20261116-001A",
                   "SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases")
INF = float("inf")


def forced_by_states(n, atoms, held):
    out = None
    for x in itertools.product((0, 1), repeat=n):
        if any(x[h] == 0 for h in held):
            continue
        if all(not (x[a] and x[b]) or x[c] for a, b, c in atoms):
            out = [o and bool(v) for o, v in zip(out, x)] if out is not None else [bool(v) for v in x]
    return out


def phases(n, atoms, held):
    cur = set(held)
    phase = {h: 0 for h in held}
    t = 0
    while True:
        rules = {}
        for a, b, c in atoms:
            if a in cur:
                rules.setdefault(b, set()).add(c)
            if b in cur:
                rules.setdefault(a, set()).add(c)
        seen = set(cur)
        stack = list(cur)
        while stack:
            u = stack.pop()
            for w in rules.get(u, ()):
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        new = seen - cur
        if not new:
            return phase, t
        t += 1
        for v in new:
            phase[v] = t
        cur = seen


def comb(i, j):
    if i == INF or j == INF:
        return INF
    return i + 1 if i == j else max(i, j)


def rank(n, atoms, held):
    r = [0 if v in held else INF for v in range(n)]
    changed = True
    while changed:
        changed = False
        for a, b, c in atoms:
            v = comb(r[a], r[b])
            if v < r[c]:
                r[c] = v
                changed = True
    return r


def fringe(n, atoms, held):
    f = [1 if v in held else INF for v in range(n)]
    changed = True
    while changed:
        changed = False
        for a, b, c in atoms:
            v = f[a] + f[b]
            if v < f[c]:
                f[c] = v
                changed = True
    return f


def unfolding_criterion(n, atoms, held, v):
    """Theorem 4(a): with every distinction demanded by at most one atom."""
    dem = {c: (a, b) for a, b, c in atoms}
    def ok(u, path):
        if u in held:
            return True
        if u in path or u not in dem:
            return False
        a, b = dem[u]
        return ok(a, path | {u}) and ok(b, path | {u})
    return ok(v, frozenset())


def check_pattern(n, atoms, held, stats):
    fs = forced_by_states(n, atoms, held) if n <= 10 else None
    ph, P = phases(n, atoms, held)
    r = rank(n, atoms, held)
    f = fringe(n, atoms, held)
    for v in range(n):
        forced = v in ph
        assert (r[v] < INF) == forced, "T1 forced"
        if fs is not None:
            assert fs[v] == forced, "T1 states"
        if forced:
            assert ph[v] == r[v], "T1 phase != rank"
            assert r[v] <= math.log2(f[v]) + 1e-12, "T2"
    reused = any(sum(1 for a, b, c in atoms if u in (a, b)) >= 2 for u in range(n))
    several = any(sum(1 for a, b, c in atoms if c == u) >= 2 for u in range(n))
    if not reused:
        stats["no_reuse"] += 1
        for v in ph:
            assert f[v] <= len(held), "T3 fringe"
            assert r[v] <= math.log2(len(held)) + 1e-12 if held else True, "T3 rank"
    if not several:
        stats["no_several"] += 1
        for v in range(n):
            assert unfolding_criterion(n, atoms, held, v) == (v in ph), "T4a"
    stats["patterns"] += 1
    stats["max_P"] = max(stats["max_P"], P)


def main():
    stats = {"patterns": 0, "no_reuse": 0, "no_several": 0, "max_P": 0}
    n = 4
    all_atoms = [(a, b, c) for a, b in itertools.combinations(range(n), 2)
                 for c in range(n) if c not in (a, b)]
    assert len(all_atoms) == 12
    for mask in range(1 << len(all_atoms)):
        atoms = [all_atoms[i] for i in range(len(all_atoms)) if mask >> i & 1]
        for hm in range(1 << n):
            held = {v for v in range(n) if hm >> v & 1}
            check_pattern(n, atoms, held, stats)
    exhaustive = dict(stats)
    rnd = random.Random(20261116)
    for _ in range(3000):
        n = rnd.randint(5, 9)
        m = rnd.randint(1, 3 * n)
        atoms = []
        for _ in range(m):
            a, b, c = rnd.sample(range(n), 3)
            atoms.append((a, b, c))
        held = set(rnd.sample(range(n), rnd.randint(1, n - 1)))
        check_pattern(n, atoms, held, stats)
    # sparse patterns where reuse or several-way demand is absent
    for _ in range(3000):
        n = rnd.randint(5, 10)
        held = set(rnd.sample(range(n), rnd.randint(1, n - 1)))
        atoms, used_dem, used_c = [], set(), set()
        mode = rnd.random() < 0.5
        for _ in range(3 * n):
            a, b, c = rnd.sample(range(n), 3)
            if mode:
                if a in used_dem or b in used_dem:
                    continue
                used_dem |= {a, b}
            else:
                if c in used_c:
                    continue
                used_c.add(c)
            atoms.append((a, b, c))
        check_pattern(n, atoms, held, stats)
    sys.path.insert(0, EXP)
    import gates  # noqa: E402
    import numpy as np  # noqa: E402
    import knots_table  # noqa: E402
    rep = {}
    gates.g4(np.random.default_rng(1116), rep)
    gates.g7(np.random.default_rng(1117), rep)
    knots_table.main()
    with open(os.path.join(knots_table.OUT, "knots_table.json")) as fh:
        tab = json.load(fh)
    assert tab["knots"] == 34 and tab["classes"] == {"parity-L-complete": 2, "NP-complete": 16,
                                                   "AC0 (single-sign clause)": 2, "P-complete": 14}, "T5"
    res = {"exhaustive_n4": exhaustive, "all": stats, "T5_classes": tab["classes"], "T5b_gadget": rep["G4"],
           "T6_dual": rep["G7"], "status": "passed"}
    print(json.dumps(res, indent=1, sort_keys=True))
    return res


if __name__ == "__main__":
    main()
