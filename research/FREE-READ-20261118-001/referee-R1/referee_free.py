"""Referee R1 for FREE-READ-20261118-001 (own code; the study's freelib.py, job.py and posthoc.py are not imported).

  ../../../.venv/bin/python -B referee_free.py <part> > referee_free_<part>.json      (from this directory)

A set S of distinctions is free when the allowed states take all 2^|S| joint values on it; a bond when it is not free and every
set of |S| - 1 of its distinctions is free; bond distance b(x, y) = (size of the least bond holding x and y) - 1, undefined (None)
when none.  Allowed states come from the referee's own builder (CUMULANT-DIST-R1 `states`: P parity, N not-all-equal, B
betweenness with the middle in second place); cumulants and delta_K from its CUMULANT-DIST-R1 and TREE-STEPS-R1 code.

Parts:
  trees      every knot tree of five knots under every assignment of P, N and B (the middle of each B knot at a seeded random place),
             every six-knot tree under every P/N assignment, and 200 random seven-knot trees under random P/N/B: b = steps + 1?
  grids      the split line of six and the split grids 3 x 3 and 3 x 4: b on every pair, and the triples that are free.
  cycles     the mixed cycles (a not-all-equal path of k knots from x to y closed by a parity knot (x, y, z)), k = 2 to 5: b, delta_K
             and delta_KB = min(delta_K, min over bonds S holding the pair of (|S| - 2) + tau(kappa_S)) on every pair, against steps.
  triangle   400 random bases that are not trees (6 to 8 distinctions, 3 to 7 knots of mixed laws), and every ring of three to six
             knots under P, N, B and alternating laws: the triangle inequality for b and for b - 1, a pair that no bond holds
             counting as infinitely far (corrected: the first version skipped such triples).
  hub        the hub set {x, y, one child of each of N not-all-equal knots hung on x} is free for N = 1 to 8 (so freedom gating keeps it).
"""
import itertools
import json
import math
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/CUMULANT-DIST-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/TREE-STEPS-20261118-001/referee-R1"))
import referee_cumulant as RC  # noqa: E402
import referee_steps as RS  # noqa: E402


class Sup:
    def __init__(self, st, n):
        self.st = np.asarray(st, dtype=np.int64)
        self.n = n
        self.c = {}

    def free(self, S):
        S = tuple(sorted(S))
        if S not in self.c:
            code = np.zeros(len(self.st), dtype=np.int64)
            for i, v in enumerate(S):
                code |= ((self.st >> v) & 1) << i
            self.c[S] = len(np.unique(code)) == (1 << len(S))
        return self.c[S]

    def bond(self, S):
        return not self.free(S) and all(self.free(T) for T in itertools.combinations(S, len(S) - 1))

    def b(self, x, y, smax=None):
        others = [z for z in range(self.n) if z not in (x, y)]
        smax = self.n if smax is None else smax
        for s in range(2, smax + 1):
            for extra in itertools.combinations(others, s - 2):
                if self.bond((x, y) + extra):
                    return s - 1
        return None


def orient(knots, laws, rng):
    out = []
    for law, (a, b, c) in zip(laws, knots):
        if law == "B":
            t = [a, b, c]
            m = rng.randrange(3)
            t[1], t[m] = t[m], t[1]
            out.append(("B", tuple(t)))
        else:
            out.append((law, (a, b, c)))
    return out


def tree_case(args):
    knots, laws, seed = args
    n = 2 * len(knots) + 1
    kn = orient(knots, laws, random.Random(seed))
    sup = Sup(RC.states(n, kn), n)
    st = RC.steps(knots, n)
    off = [(x, y) for x, y in itertools.combinations(range(n), 2) if sup.b(x, y, st[x][y] + 2) != st[x][y] + 1]
    return {"laws": "".join(laws), "pairs": n * (n - 1) // 2, "off": len(off), "example": off[:2]}


def part_trees(workers=16):
    from multiprocessing import Pool
    jobs = []
    for kn in RC.tree_shapes(5):
        for laws in itertools.product("PNB", repeat=5):
            jobs.append((kn, laws, f"{kn}{laws}"))
    for kn in RC.tree_shapes(6):
        for laws in itertools.product("PN", repeat=6):
            jobs.append((kn, laws, f"{kn}{laws}"))
    rng = random.Random("referee-free-read-7")
    for i in range(200):
        kn = RS.random_tree(7, 3, rng)
        jobs.append((kn, tuple(rng.choice("PNB") for _ in kn), f"r7-{i}"))
    with Pool(workers) as P:
        rows = P.map(tree_case, jobs, chunksize=8)
    return {"bases": len(rows), "pairs": sum(r["pairs"] for r in rows), "off": sum(r["off"] for r in rows),
            "with_betweenness": sum("B" in r["laws"] for r in rows), "bad": [r for r in rows if r["off"]][:5]}


def split_base(cells, axes):
    n = len(cells)
    full = (1 << n) - 1
    st = {0, full}
    for ax, size in axes:
        for c in range(size - 1):
            m = sum(1 << k for k, p in enumerate(cells) if p[ax] <= c)
            st |= {m, full ^ m}
    return sorted(st), n


def part_grids():
    out = {}
    for name, W, H in (("line6", 6, 1), ("grid3x3", 3, 3), ("grid3x4", 3, 4)):
        cells = [(i, j) for i in range(W) for j in range(H)]
        axes = [(0, W)] + ([(1, H)] if H > 1 else [])
        st, n = split_base(cells, axes)
        sup = Sup(st, n)
        bs = {sup.b(x, y) for x, y in itertools.combinations(range(n), 2)}
        free_triples = [[cells[v] for v in T] for T in itertools.combinations(range(n), 3) if sup.free(T)]
        out[name] = {"n": n, "bond_distances": sorted(bs), "triples": math.comb(n, 3), "free_triples": len(free_triples),
                     "example_free_triple": free_triples[:1]}
    return out


def part_cycles():
    rows = []
    for k in range(2, 6):
        knots, n = [], 1
        for i in range(k):
            knots.append(("N", (n - 1, n, n + 1)))
            n += 2
        x, y, z = 0, n - 1, n
        knots.append(("P", (x, y, z)))
        n += 1
        st = RC.states(n, knots)
        sup, B = Sup(st, n), RC.Base(st, n)
        sp = RC.steps([kk for _, kk in knots], n)
        res = {"k": k, "pairs": 0, "b_minus_1_off_steps": 0, "deltaK_off_steps": 0, "deltaKB_off_steps": 0, "worst_KB": None}
        worst = 0.0
        for a, c in itertools.combinations(range(n), 2):
            d = sp[a][c]
            bb = sup.b(a, c, d + 3)
            _, dK = RS.both(B, a, c, min(n, d + 3))
            vb = math.inf
            for s in range(2, d + 4):
                for extra in itertools.combinations([v for v in range(n) if v not in (a, c)], s - 2):
                    S = (a, c) + extra
                    if sup.bond(S):
                        kk = B.k(tuple(sorted(S)))
                        if kk != 0.0:
                            vb = min(vb, (s - 2) + max(0.0, -math.log(abs(kk), 3)))
            dKB = min(dK, vb)
            res["pairs"] += 1
            res["b_minus_1_off_steps"] += (bb is None or bb - 1 != d)
            res["deltaK_off_steps"] += abs(dK - d) > 0.11
            res["deltaKB_off_steps"] += abs(dKB - d) > 0.11
            if dKB - d > worst:
                worst = dKB - d
                res["worst_KB"] = {"pair": [a, c], "steps": d, "delta_KB": dKB, "delta_K": dK, "bond_cumulant": vb}
        rows.append(res)
    return rows


def random_base(rng):
    while True:
        n = rng.randint(6, 8)
        m = rng.randint(3, 7)
        knots = [(rng.choice("PNB"), tuple(rng.sample(range(n), 3))) for _ in range(m)]
        inc = {v for _, kk in knots for v in kk}
        if len(inc) < n:
            continue
        import networkx as nx
        G = nx.Graph()
        for i, (_, kk) in enumerate(knots):
            for v in kk:
                G.add_edge(("k", i), ("v", v))
        if not nx.is_connected(G) or nx.is_tree(G):
            continue
        st = RC.states(n, knots)
        if len(st):
            return n, knots, st


def triangle_on(n, st):
    """A pair that no bond holds counts as infinitely far (corrected on 18 November 2026: the first version skipped such triples,
    which hid every failure; the owner's challenge).  Returns triples checked, failures for b (all, and those with every distance
    finite), failures for b - 1, and the first failure of b."""
    sup = Sup(st, n)
    D = {}
    for x, y in itertools.combinations(range(n), 2):
        v = sup.b(x, y)
        D[(x, y)] = D[(y, x)] = math.inf if v is None else v
    v_b = v_bfin = v_b1 = checked = 0
    ex = None
    for x, y, z in itertools.permutations(range(n), 3):
        a, b, c = D[(x, z)], D[(x, y)], D[(y, z)]
        checked += 1
        if a > b + c:
            v_b += 1
            v_bfin += a < math.inf
            ex = ex or {"x": x, "y": y, "z": z, "b_xz": a, "b_xy": b, "b_yz": c}
        if a - 1 > (b - 1) + (c - 1):
            v_b1 += 1
    return checked, v_b, v_bfin, v_b1, ex


def part_triangle():
    rng = random.Random("referee-free-read-triangle")
    out = {"random_bases": 0, "triples": 0, "violations_b": 0, "violations_b_finite": 0, "bases_violating_b": 0,
           "violations_b_minus_1": 0, "bases_violating_b_minus_1": 0, "example": None, "rings": {}}
    for _ in range(400):
        n, knots, st = random_base(rng)
        c, vb, vbf, vb1, ex = triangle_on(n, st)
        out["random_bases"] += 1
        out["triples"] += c
        out["violations_b"] += vb
        out["violations_b_finite"] += vbf
        out["bases_violating_b"] += vb > 0
        out["violations_b_minus_1"] += vb1
        out["bases_violating_b_minus_1"] += vb1 > 0
        if ex and out["example"] is None:
            out["example"] = {"n": n, "knots": knots, **ex}
    for m in range(3, 7):
        for name, laws in (("P", "P" * m), ("N", "N" * m), ("B", "B" * m), ("alt", ("PN" * m)[:m])):
            knots = [(laws[i], (2 * i, 2 * i + 1, (2 * i + 2) % (2 * m))) for i in range(m)]
            st = RC.states(2 * m, knots)
            c, vb, vbf, vb1, _ = triangle_on(2 * m, st)
            out["rings"][f"{m}{name}"] = {"triples": c, "violations_b": vb, "violations_b_finite": vbf, "violations_b_minus_1": vb1}
    st = RC.states(4, [("N", (0, 2, 3)), ("N", (1, 2, 3))])
    sup = Sup(st, 4)
    out["two_knots_sharing_two_distinctions"] = {"b(0,2)": sup.b(0, 2), "b(2,1)": sup.b(2, 1), "b(0,1)": sup.b(0, 1)}
    return out


def part_hub():
    out = []
    for N in range(1, 9):
        B, y, kx, _ = RS.path_with_hubs(1, N, 0)
        sup = Sup(B.st, B.n)
        S = [0, y] + kx[0::2]                     # one child of each hung knot
        out.append({"N": N, "hub_set_free": sup.free(S), "every_proper_subset_free": True if sup.free(S) else None})
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    f = {"trees": part_trees, "grids": part_grids, "cycles": part_cycles, "triangle": part_triangle, "hub": part_hub}[part]
    print(json.dumps(f(), indent=1, default=str))
