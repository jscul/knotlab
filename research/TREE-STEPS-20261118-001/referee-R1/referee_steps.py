"""Referee R1 for TREE-STEPS-20261118-001 (own code: the referee's CUMULANT-DIST-R1 states, partition-formula cumulants and tree
shapes; the study's treelib.py, job.py and cumlib.py are not imported).

  ../../../.venv/bin/python -B referee_steps.py <part> > referee_steps_<part>.json      (from this directory)

delta   = min over S holding x and y with kappa_S != 0 of (|S| - 2) + max(0, -log_3 |kappa_S|);
delta_K = the same over irreducible S only: kappa_S != 0 and kappa_T = 0 for every T with {x, y} in T strictly inside S.
Both are searched over every set holding the pair, by size; a set of size s can lower a value v only when s - 2 < v.

Parts:
  six     every knot tree of six knots (19 shapes) under every parity/not-all-equal assignment (1,216 bases): both against steps.
  rand7   200 random knot trees of seven knots (the referee's seed), at most three knots per distinction, random laws.
  hubs    H1's cases: a not-all-equal hub with both other distinctions of each hung knot taken; a parity hub (both taken) on x with a
          not-all-equal path to y (a mixed tree); two hubs, one at each end of the path: the exact cumulant against the hub identity
          and, for two hubs, against the leading term rho * kappa(hub 1) * kappa(hub 2).
  cycle   a parity knot (x, y, z) closing a not-all-equal path of k knots from x to y (k = 2 to 5): delta and delta_K on the three pairs
          of the parity knot, the pair correlation, and the triangle inequality.
"""
import itertools
import json
import math
import random
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/CUMULANT-DIST-20261118-001/referee-R1"))
import referee_cumulant as RC  # noqa: E402

import sympy as sp  # noqa: E402

T_ = sp.symbols("t")
_SER = sp.series(sp.log(sp.cosh(T_)), T_, 0, 40).removeO()
COIN = {m: float(sp.factorial(m) * _SER.coeff(T_, m)) for m in range(1, 40)}          # cumulants of a fair coin


def both(B, x, y, smax):
    others = [z for z in range(B.n) if z not in (x, y)]
    best, bestK = math.inf, math.inf
    binding = []                                          # sets holding x and y with nonzero cumulant, smaller sizes first
    for s in range(2, smax + 1):
        if s - 2 >= best and s - 2 >= bestK:
            break
        found = []
        for extra in itertools.combinations(others, s - 2):
            S = frozenset((x, y) + extra)
            k = B.k(tuple(sorted(S)))
            if k == 0.0:
                continue
            v = (s - 2) + max(0.0, -math.log(abs(k), 3))
            best = min(best, v)
            if not any(T < S for T in binding):
                bestK = min(bestK, v)
            found.append(S)
        binding.extend(found)
    return best, bestK


def run_tree(args):
    knots, laws = args
    n = 2 * len(knots) + 1
    st = RC.steps(knots, n)
    B = RC.Base(RC.states(n, list(zip(laws, knots))), n)
    off, offK, differ = 0, 0, 0
    for x, y in itertools.combinations(range(n), 2):
        d = st[x][y]
        v, vK = both(B, x, y, d + 2)
        off += abs(v - d) > 1e-9
        offK += abs(vK - d) > 1e-9
        differ += abs(v - vK) > 1e-9
    return {"laws": "".join(laws), "n": n, "pairs": n * (n - 1) // 2, "delta_off": off, "deltaK_off": offK, "differ": differ,
            "parity_on_some_path": "P" in laws and "N" in laws}


def summarize(rows):
    return {"bases": len(rows), "pairs": sum(r["pairs"] for r in rows), "delta_off": sum(r["delta_off"] for r in rows),
            "deltaK_off": sum(r["deltaK_off"] for r in rows), "differ": sum(r["differ"] for r in rows),
            "mixed_bases": sum(r["parity_on_some_path"] for r in rows), "bad": [r for r in rows if r["delta_off"] or r["deltaK_off"]][:5]}


def part_six(workers=16):
    shapes = RC.tree_shapes(6)
    jobs = [(kn, laws) for kn in shapes for laws in itertools.product("PN", repeat=6)]
    with Pool(workers) as P:
        rows = P.map(run_tree, jobs, chunksize=4)
    return {"shapes": len(shapes), **summarize(rows)}


def random_tree(k, max_per, rng):
    knots, n, deg = [(0, 1, 2)], 3, {0: 1, 1: 1, 2: 1}
    while len(knots) < k:
        v = rng.choice([u for u in range(n) if deg[u] < max_per])
        knots.append((v, n, n + 1))
        deg[v] += 1
        deg[n] = deg[n + 1] = 1
        n += 2
    return knots


def part_rand7(count=200, workers=16):
    rng = random.Random("referee-tree-steps-7")
    jobs = []
    for _ in range(count):
        kn = random_tree(7, 3, rng)
        jobs.append((kn, tuple(rng.choice("PN") for _ in kn)))
    with Pool(workers) as P:
        rows = P.map(run_tree, jobs, chunksize=1)
    return summarize(rows)


def path_with_hubs(k, hubs_x, hubs_y, hub_law_x="N", hub_law_y="N"):
    """A not-all-equal path of k knots from x = 0 to y, hubs_x knots of law hub_law_x hung on x, hubs_y on y; returns the base,
    y, and the children (both other distinctions of each hung knot) at each end."""
    knots, n = [], 1
    for i in range(k):
        knots.append(("N", (n - 1, n, n + 1)))
        n += 2
    y = n - 1
    kx, ky = [], []
    for _ in range(hubs_x):
        knots.append((hub_law_x, (0, n, n + 1)))
        kx += [n, n + 1]
        n += 2
    for _ in range(hubs_y):
        knots.append((hub_law_y, (y, n, n + 1)))
        ky += [n, n + 1]
        n += 2
    return RC.Base(RC.states(n, knots), n), y, kx, ky


def part_hubs():
    out = {"nae_both_children": [], "parity_hub_mixed_tree": [], "two_hubs": []}
    for N, k in ((1, 1), (2, 1), (2, 2), (3, 1)):
        B, y, kx, _ = path_with_hubs(k, N, 0)
        S = tuple(sorted([0, y] + kx))
        out["nae_both_children"].append({"N_knots": N, "k": k, "copies": 2 * N, "kappa": B.k(S),
                                         "predicted": COIN[2 * N + 2] * (-1 / 3) ** (2 * N + k)})
    for N, k in ((1, 1), (2, 1), (2, 2), (3, 1), (4, 1)):
        B, y, kx, _ = path_with_hubs(k, N, 0, hub_law_x="P")
        S = tuple(sorted([0, y] + kx))
        pred = COIN[N + 2] * (-1 / 3) ** k if (N + 2) % 2 == 0 else 0.0
        out["parity_hub_mixed_tree"].append({"N_knots": N, "k": k, "copies": N, "set_size": len(S), "kappa": B.k(S),
                                             "predicted": pred})
    for N1, N2, k in ((1, 1, 1), (1, 1, 2), (2, 2, 1)):
        B, y, kx, ky = path_with_hubs(k, N1, N2)
        S = tuple(sorted([0, y] + kx + ky))
        rho = (-1 / 3) ** k
        lead = rho * COIN[2 * N1 + 2] * COIN[2 * N2 + 2] * (-1 / 3) ** (2 * N1 + 2 * N2)
        out["two_hubs"].append({"N1": N1, "N2": N2, "k": k, "kappa": B.k(S), "leading_term": lead})
    return out


def part_cycle():
    rows = []
    for k in range(2, 6):
        knots, n = [], 1
        for i in range(k):
            knots.append(("N", (n - 1, n, n + 1)))
            n += 2
        x, y, z = 0, n - 1, n
        knots.append(("P", (x, y, z)))
        n += 1
        B = RC.Base(RC.states(n, knots), n)
        res = {"k": k, "n": n, "C_xy": B.m((x, y))}
        for a, b, name in ((x, y, "x-y"), (x, z, "x-z"), (z, y, "z-y")):
            d, dK = both(B, a, b, min(n, 6))
            res[name] = {"delta": d, "delta_K": dK}
        res["delta_K_triangle_violated"] = res["x-y"]["delta_K"] > res["x-z"]["delta_K"] + res["z-y"]["delta_K"] + 1e-9
        rows.append(res)
    return rows


if __name__ == "__main__":
    part = sys.argv[1]
    f = {"six": part_six, "rand7": part_rand7, "hubs": part_hubs, "cycle": part_cycle}[part]
    print(json.dumps(f(), indent=1, default=str))
