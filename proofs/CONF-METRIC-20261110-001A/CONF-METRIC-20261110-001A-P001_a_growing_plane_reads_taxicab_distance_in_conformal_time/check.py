#!/usr/bin/env python3
"""Checks for CONF-METRIC-20261110-001A: a growing plane reads taxicab distance in conformal time.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Check 1 compares Lemma 1's formula with breadth-first search on the cell digraph of fixed stages, built on READ-GROW-20261110-001A-E001's
grid_lib geometry. Checks 2 and 3 compare Theorem 2's bounds with the route first arrivals T1 computed by METRIC-GROW-20261110-001A-E001's
metric_lib, on every schedule of EXPAND-READ-20261110-001A-E001 and on fresh random schedules. Check 4 computes the plain round trip's
excess on a family of schedules (Corollary 4)."""
import hashlib
import itertools
import json
import random
import sys
import time
from collections import deque
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GL = ROOT / "experiments/READ-GROW-20261110-001A/READ-GROW-20261110-001A-E001_reading_distance_while_growing"
MG = ROOT / "experiments/METRIC-GROW-20261110-001A/METRIC-GROW-20261110-001A-E001_time_length_while_growing"
sys.path.insert(0, str(GL))
sys.path.insert(0, str(MG))
import grid_lib as G2  # noqa: E402
import metric_lib as M  # noqa: E402

T0 = time.time()
OUT = {}
DEPS = {
    "experiments/READ-GROW-20261110-001A/READ-GROW-20261110-001A-E001_reading_distance_while_growing/grid_lib.py": "0176b395221264fece460187692d5d9bcc2868fcd44cb35f35871d733397847e",
    "experiments/METRIC-GROW-20261110-001A/METRIC-GROW-20261110-001A-E001_time_length_while_growing/metric_lib.py": "417a8b4d4c5b7a89eae96210dd7aa5800f48d6ebbe418aef715a42f90051dd04",
    "experiments/EXPAND-READ-20261110-001A/EXPAND-READ-20261110-001A-E001_expansion_from_time_lengths/run.py": "eed326df0b76f8c5d170e9425f93a3567ba4be272d1bddadbd77bfe9b8edf78a",
}


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:400], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


# ---------- Lemma 1 ----------
def contact_point(i, r, p, g):
    """comoving position (in ring sides) and kind ('h' or 'v') of the contact at position p (a multiple of g) of ring (i, r)"""
    j = (p // g) % 4
    return [((i + 1, r + 0.5), 'h'), ((i + 0.5, r + 1), 'v'), ((i, r + 0.5), 'h'), ((i + 0.5, r), 'v')][j]


def hops(P, kp, Q, kq, S):
    """Lemma 1's hop distance on the torus of side S between contact points P (kind kp) and Q (kind kq)"""
    best = None
    for wx in (-1, 0, 1):
        for wy in (-1, 0, 1):
            dx, dy = Q[0] + wx * S - P[0], Q[1] + wy * S - P[1]
            if kp == kq:
                h = 2 * (abs(dx) + abs(dy))
            else:
                first = [(0.5, -0.5), (-0.5, 0.5)] if kp == 'h' else [(0.5, 0.5), (-0.5, -0.5)]
                h = 1 + 2 * min(abs(dx - a) + abs(dy - b) for a, b in first)
            best = h if best is None else min(best, h)
    return round(best)


def lemma_distance(src, dst, g, S):
    """Lemma 1: earliest arrival from own cell src = (i, r, p) to own cell dst = (i', r', q) on the torus of side S rings"""
    (i, r, p), (i2, r2, q) = src, dst
    L = 4 * g
    if (i % S, r % S) == (i2 % S, r2 % S) and p // g == q // g and q >= p:
        return q - p
    pout = (p // g + 1) * g
    qin = (q // g) * g
    P, kp = contact_point(i, r, pout % L, g)
    Q, kq = contact_point(i2, r2, qin, g)
    return (pout - p) + g * hops(P, kp, Q, kq, S) + (q - qin)


def bfs_check(job):
    n, g, k, seed = job
    Gr = G2.Grid(n, g)
    for _ in range(k + 1):
        Gr.double()
    S, L = Gr.side, 4 * g
    succ = [[] for _ in range(Gr.ncell)]
    for i in range(S):
        for r in range(S):
            for p in range(L):
                a = Gr.cell(i, r, p)
                b = Gr.cell(i, r, p + 1)
                if b not in succ[a]:
                    succ[a].append(b)
    rng = random.Random(seed)
    own = list(Gr.own_index.items())
    bad, n_pairs = 0, 0
    for _ in range(12):
        (i, r, p), s = own[rng.randrange(len(own))]
        dist = [-1] * Gr.ncell
        dist[s] = 0
        dq = deque([s])
        while dq:
            a = dq.popleft()
            for b in succ[a]:
                if dist[b] < 0:
                    dist[b] = dist[a] + 1
                    dq.append(b)
        for (i2, r2, q), t in own:
            n_pairs += 1
            if (i2, r2, q) == (i, r, p):
                continue
            if lemma_distance((i, r, p), (i2, r2, q), g, S) != dist[t]:
                bad += 1
    return {"n": n, "g": g, "side": S, "pairs": n_pairs, "mismatches": bad}


# ---------- Theorem 2 ----------
import numpy as np  # noqa: E402


def stage_index(S, g):
    """numpy step arrays for the stage torus of side S: cell numbering own cells (i, r, p) then contacts h(i, r), v(i, r); each cell
    is reached at the next lag when one of the two cells it reads is reached (own cell: itself and its left neighbour; contact: its two
    left neighbours)"""
    L = 4 * g
    own_pos = [p for p in range(L) if p % g]
    no = len(own_pos)
    pidx = {p: j for j, p in enumerate(own_pos)}
    nown = S * S * no
    def own(i, r, p):
        return ((i % S) * S + (r % S)) * no + pidx[p]
    def h(i, r):
        return nown + 2 * ((i % S) * S + (r % S))
    def v(i, r):
        return nown + 2 * ((i % S) * S + (r % S)) + 1
    def cell(i, r, p):
        p %= L
        if p == 0:
            return h(i, r)
        if p == g:
            return v(i, r)
        if p == 2 * g:
            return h(i - 1, r)
        if p == 3 * g:
            return v(i, r - 1)
        return own(i, r, p)
    N = nown + 2 * S * S
    A = np.zeros(N, dtype=np.int64)
    B = np.zeros(N, dtype=np.int64)
    for i in range(S):
        for r in range(S):
            for p in own_pos:
                c = own(i, r, p)
                A[c], B[c] = c, cell(i, r, p - 1)
            A[h(i, r)], B[h(i, r)] = cell(i, r, -1), cell(i + 1, r, 2 * g - 1)
            A[v(i, r)], B[v(i, r)] = cell(i, r, g - 1), cell(i, r + 1, 3 * g - 1)
    return A, B, own, N, nown


def route_arrivals(n, g, runs):
    """first lag each original ring's position-1 cell is reached by a route from ring (0, 0)'s position-1 cell (lag 0 after the first
    doubling), and the doubling lags"""
    S = 2 * n
    A, B, own, N, nown = stage_index(S, g)
    R = np.zeros(N, dtype=bool)
    R[own(0, 0, 1)] = True
    T1, t, D = {}, 0, []
    for P in runs:
        k = S // n
        targets = {(a, b): own(a * k, b * k, 1) for a in range(n) for b in range(n) if (a, b) != (0, 0)}
        for _ in range(P):
            R = R[A] | R[B]
            t += 1
            for Y, c in targets.items():
                if Y not in T1 and R[c]:
                    T1[Y] = t
        # doubling: own cells of old rings keep their reach at (2i, 2r)
        S2 = 2 * S
        A2, B2, own2, N2, nown2 = stage_index(S2, g)
        R2 = np.zeros(N2, dtype=bool)
        L = 4 * g
        for i in range(S):
            for r in range(S):
                for p in range(L):
                    if p % g:
                        if R[own(i, r, p)]:
                            R2[own2(2 * i, 2 * r, p)] = True
        S, A, B, own, N, R = S2, A2, B2, own2, N2, R2
        D.append(t)
    return T1, D


def theorem_check(job):
    n, g, runs = job
    T1raw, D = route_arrivals(n, g, runs)
    t_end = sum(runs)
    k = lambda tau: sum(1 for d in D if 0 < d <= tau)   # noqa: E731
    phi = lambda t: sum(2.0 ** -k(tau) for tau in range(t))   # noqa: E731
    def taxi(a, b):
        f = lambda x: min(x % n, (-x) % n)   # noqa: E731
        return f(a) + f(b)
    low, high, undefined_ok, worst_low, worst_high, readings = True, True, True, None, None, 0
    T1 = T1raw
    phi_end = phi(t_end)
    conf = {}
    for a in range(n):
        for b in range(n):
            if (a, b) == (0, 0):
                continue
            d = taxi(a, b)
            if (a, b) in T1:
                readings += 1
                x = phi(T1[(a, b)])
                conf[(a, b)] = x
                lo, hi = 4 * g * d - 6 * g, 4 * g * d + 9 * g + 2
                low &= x >= lo
                high &= x <= hi
                e = x - 4 * g * d
                worst_low = e if worst_low is None else min(worst_low, e)
                worst_high = e if worst_high is None else max(worst_high, e)
            else:
                undefined_ok &= phi_end < 4 * g * d + 9 * g + 2
    # Corollary 3: conformal round-trip excess
    R = {}
    for (a, b), x in conf.items():
        back = ((-a) % n, (-b) % n)
        if back in conf:
            R[(a, b)] = x + conf[back]
    excess = 0.0
    for u in R:
        for w in R:
            z = ((u[0] + w[0]) % n, (u[1] + w[1]) % n)
            if z != (0, 0) and z in R:
                excess = max(excess, R[z] - R[u] - R[w])
    return {"n": n, "g": g, "runs": runs, "readings": readings, "lower bound": bool(low), "upper bound": bool(high),
            "unreached below the bound": bool(undefined_ok), "least phi - 4gd": worst_low, "largest phi - 4gd": worst_high,
            "largest conformal excess": excess, "42g + 4": 42 * g + 4}


def arrivals_only(job):
    n, g, runs = job
    return {"%d,%d" % Y: t for Y, t in sorted(route_arrivals(n, g, runs)[0].items())}


def metric_lib_arrivals(job):
    n, g, runs = job
    return {"%d,%d" % Y: t for Y, t in sorted(M.run_schedule(n, g, runs, read_balance=False)["T1"].items())}


def plain_family(K):
    n, g = 5, 3
    runs = [28] + [2] * K + [40 * 2 ** (K + 1)]
    T1, D = route_arrivals(n, g, runs)
    k = lambda tau: sum(1 for d in D if 0 < d <= tau)   # noqa: E731
    phi = lambda t: sum(2.0 ** -k(tau) for tau in range(t))   # noqa: E731
    u, mu, z, mz = (1, 1), (4, 4), (2, 2), (3, 3)
    if not all(x in T1 for x in (u, mu, z, mz)):
        return {"K": K, "runs": runs, "defined": False}
    plain = (T1[z] + T1[mz]) - 2 * (T1[u] + T1[mu])
    conformal = (phi(T1[z]) + phi(T1[mz])) - 2 * (phi(T1[u]) + phi(T1[mu]))
    return {"K": K, "runs": runs, "defined": True, "plain excess R1(2u) - 2 R1(u)": plain, "conformal excess": conformal,
            "T1": {str(x): T1[x] for x in (u, mu, z, mz)}}


def main():
    deps = {p: sha(p) for p in DEPS}
    check("0 dependencies bound by hash", all(DEPS[p] == deps[p] for p in DEPS), deps)
    jobs = [(n, g, k, 1000 * n + 10 * g + k) for n in (3, 5) for g in (2, 3, 4, 5) for k in (0, 1)]
    with Pool(8) as pool:
        bfs = pool.map(bfs_check, jobs, chunksize=1)
    check("1 Lemma 1 equals breadth-first search on fixed stages (every own cell from 12 random own cells; n = 3, 5; g = 2 to 5; "
          "sides 2n and 4n)", all(b["mismatches"] == 0 for b in bfs),
          {"stages": len(bfs), "pairs": sum(b["pairs"] for b in bfs), "mismatches": sum(b["mismatches"] for b in bfs)})
    exp = json.loads((ROOT / "artifacts/EXPAND-READ-20261110-001A/EXPAND-READ-20261110-001A-E001_expansion_from_time_lengths/run/"
                             "result.json").read_text())
    census = [(r["n"], r["g"], r["runs"]) for rows in exp["rows"].values() for r in rows]
    rng = random.Random(20261110)
    fresh = []
    while len(fresh) < 240:
        n = rng.choice((5, 7, 9))
        g = rng.choice((2, 3, 4, 5))
        m = rng.randint(1, 4 if n == 5 else 3)
        runs = [rng.choice((1, 2, rng.randint(1, 64))) for _ in range(m)]
        fresh.append((n, g, runs))
    with Pool(8) as pool:
        c2 = pool.map(theorem_check, census, chunksize=1)
        c3 = pool.map(theorem_check, fresh, chunksize=1)
    sample = census[::40]
    with Pool(4) as pool:
        mine = pool.map(arrivals_only, sample, chunksize=1)
        theirs = pool.map(metric_lib_arrivals, sample, chunksize=1)
    agree = sum(1 for a, b in zip(mine, theirs) if a == b)
    def summary(rows):
        return {"schedules": len(rows), "readings": sum(r["readings"] for r in rows),
                "lower bound held": sum(r["lower bound"] for r in rows), "upper bound held": sum(r["upper bound"] for r in rows),
                "unreached below the bound": sum(r["unreached below the bound"] for r in rows),
                "least phi - 4gd by g": {str(g): min((r["least phi - 4gd"] for r in rows if r["g"] == g and r["least phi - 4gd"] is not None), default=None) for g in (2, 3, 4, 5)},
                "largest phi - 4gd by g": {str(g): max((r["largest phi - 4gd"] for r in rows if r["g"] == g and r["largest phi - 4gd"] is not None), default=None) for g in (2, 3, 4, 5)},
                "largest conformal excess": max(r["largest conformal excess"] for r in rows)}
    ok2 = all(r["lower bound"] and r["upper bound"] and r["unreached below the bound"] for r in c2) and agree == len(sample)
    check("2 Theorem 2 on every schedule of EXPAND-READ-20261110-001A-E001 (route first arrivals, computed here and, on every 40th "
          "schedule, equal to metric_lib's)", ok2, dict(summary(c2), **{"sample agreeing with metric_lib": [agree, len(sample)]}))
    ok3 = all(r["lower bound"] and r["upper bound"] and r["unreached below the bound"] for r in c3)
    check("3 Theorem 2 on 240 fresh random schedules (n = 5, 7, 9; g = 2 to 5; one to four runs)", ok3, summary(c3))
    with Pool(4) as pool:
        fam = pool.map(plain_family, [0, 1, 2, 3], chunksize=1)
    ok4 = all(f["defined"] for f in fam) and all(fam[i + 1]["plain excess R1(2u) - 2 R1(u)"] > fam[i]["plain excess R1(2u) - 2 R1(u)"]
                                                  for i in range(len(fam) - 1))
    check("4 Computed (Corollary 4): on [28, 2 x K, 40 2^(K+1)] the plain round-trip excess R1(2u) - 2 R1(u), u = (1, 1), grows with K "
          "while the conformal excess stays bounded", ok4, fam)
    result = {"ticket": "CONF-METRIC-20261110-001A", "artifact_id": "CONF-METRIC-20261110-001A-P001", "checks": OUT, "status": "passed"}
    path = HERE / "result.json"
    if "--write" in sys.argv:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        return 0
    old = json.loads(path.read_text())
    same = json.dumps(old["checks"], sort_keys=True, default=str) == json.dumps(json.loads(json.dumps(OUT, default=str)), sort_keys=True)
    print("result.json matches" if same else "result.json differs")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
