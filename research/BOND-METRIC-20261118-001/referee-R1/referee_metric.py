"""Referee R1 for BOND-METRIC-20261118-001 (own code; the study's metriclib.py, job.py and merge.py are not imported).

  ../../../.venv/bin/python -B referee_metric.py <part> > referee_metric_<part>.json      (from this directory)

A law is a set of allowed patterns on three places (bit i of a pattern = the value at place i); a knot places a law on an ordered
triple of distinctions.  Free, bond and bond distance b as in the note; b is infinite when no bond holds the pair, and the triangle
inequality fails when b(x, z) > b(x, y) + b(y, z), an infinite left side against a finite right side included.

Parts:
  laws      the three-place laws passing K1 and K2; their classes under reordering places and the global flip (the note's languages),
            and under reordering and every switch.
  bases     the proofs' bases written out (T2, T3, T4 and its twist, T5 and its twist, two R5 knots sharing two distinctions) and
            P6's pair: b on the pairs named, the triangle failure, and P6's joint counts.
  smallest  for each language, every base of 2 and 3 knots on 4 and 5 distinctions (every placement): how many fail, b and b - 1.
  parity    1,500 random parity bases (either constant; 4 to 11 distinctions, 1 to 7 knots): failures of b and of b - 1.
  r5        R5 one size past the census: every base of five to eight R5 knots on six distinctions and of five and six on seven
            (the census went to four knots), with a failing example.
  nae8      not-all-equal knots meeting at most once on eight distinctions, every system of 4 to 6 knots that allows a state and
            covers the eight: failures by number of knots.
"""
import itertools
import json
import math
import random
import sys
from collections import Counter
from multiprocessing import Pool

import numpy as np


def permute(R, perm):
    return frozenset(sum(((p >> perm[i]) & 1) << i for i in range(3)) for p in R)


def switch(R, sw):
    return frozenset(p ^ sw for p in R)


def k2_laws():
    out = []
    for mask in range(1, 255):
        R = frozenset(p for p in range(8) if (mask >> p) & 1)
        if all(len({((p >> i) & 1, (p >> j) & 1) for p in R}) == 4 for i, j in ((0, 1), (0, 2), (1, 2))):
            out.append(R)
    return out


def canon(R, switches):
    return min(tuple(sorted(switch(permute(R, perm), sw))) for perm in itertools.permutations(range(3)) for sw in switches)


P0 = frozenset([0b000, 0b011, 0b101, 0b110])
NAE = frozenset(range(1, 7))
CLAUSE = frozenset(range(7))
R5 = frozenset([0b000, 0b001, 0b010, 0b100, 0b111])
R6 = frozenset(range(8)) - {0b101, 0b110}
LANG = {"parity": P0, "NAE": NAE, "betweenness": switch(NAE, 2), "clause": CLAUSE, "clause-twisted": switch(CLAUSE, 1),
        "R5": R5, "R5-twisted": switch(R5, 1), "R6": R6, "R6-twisted": switch(R6, 1)}


def states(n, knots):
    s = np.arange(1 << n, dtype=np.int64)
    ok = np.ones(1 << n, dtype=bool)
    for R, (a, b, c) in knots:
        pat = ((s >> a) & 1) | (((s >> b) & 1) << 1) | (((s >> c) & 1) << 2)
        allowed = np.zeros(8, dtype=bool)
        allowed[list(R)] = True
        ok &= allowed[pat]
    return s[ok]


def bmatrix(n, st):
    """Least bond holding each pair, minus one; inf when none.  Freedom of every set by the number of distinct projections."""
    free = np.zeros(1 << n, dtype=bool)
    for m in range(1 << n):
        free[m] = len(np.unique(st & m)) == (1 << bin(m).count("1"))
    D = [[math.inf] * n for _ in range(n)]
    for m in range(1, 1 << n):
        if free[m] or not all(free[m & ~(1 << i)] for i in range(n) if (m >> i) & 1):
            continue
        vs = [i for i in range(n) if (m >> i) & 1]
        for x, y in itertools.combinations(vs, 2):
            D[x][y] = D[y][x] = min(D[x][y], len(vs) - 1)
    return D


def fails(D, n, shift=0):
    out = 0
    first = None
    for x, z in itertools.combinations(range(n), 2):
        for y in range(n):
            if y in (x, z):
                continue
            if D[x][z] - shift > (D[x][y] - shift) + (D[y][z] - shift):
                out += 1
                first = first or (x, y, z, D[x][y], D[y][z], D[x][z])
    return out, first


def part_laws():
    L = k2_laws()
    lang = Counter(canon(R, (0, 7)) for R in L)
    allsw = Counter(canon(R, range(8)) for R in L)
    named = {name: canon(R, (0, 7)) for name, R in LANG.items()}
    return {"laws": len(L), "languages_reorder_and_global_flip": len(lang), "classes_reorder_and_every_switch": len(allsw),
            "named_languages_distinct": len(set(named.values())), "named_cover_all": set(named.values()) == set(lang),
            "laws_per_language": {n: lang[c] for n, c in named.items()}}


def check(n, knots, pairs):
    st = states(n, knots)
    D = bmatrix(n, st)
    f, first = fails(D, n)
    return {"states": len(st), "b": {f"{x}-{y}": D[x][y] for x, y in pairs}, "triangle_failures": f, "first": first}


def part_bases():
    a, b, c, d = 0, 1, 2, 3
    out = {}
    out["T2 NAE {a,b,c},{a,b,d}"] = check(4, [(NAE, (a, b, c)), (NAE, (a, b, d))], [(c, a), (a, d), (c, d)])
    out["T3 clause, two sharing two"] = check(4, [(CLAUSE, (a, b, c)), (CLAUSE, (a, b, d))], [(c, a), (a, d), (c, d)])
    out["T3 clause, two sharing one"] = check(5, [(CLAUSE, (0, 1, 2)), (CLAUSE, (2, 3, 4))], [(0, 2), (2, 4), (0, 4)])
    # R6(s; u, v): s in place 2, u place 0, v place 1
    out["T4 R6(a;b,c), R6(d;b,c)"] = check(4, [(R6, (b, c, a)), (R6, (b, c, d))], [(a, b), (b, d), (a, d)])
    out["T4 R6(a;b,c), R6(a;d,e) (meet once)"] = check(5, [(R6, (1, 2, 0)), (R6, (3, 4, 0))], [(1, 0), (0, 3), (1, 3)])
    out["T4 twisted (c switched)"] = check(4, [(switch(R6, 2), (b, c, a)), (switch(R6, 2), (b, c, d))], [(a, b), (b, d), (a, d)])
    # T5: a, b, f1, g1, c, f2, g2, d = 0..7
    A, B, F1, G1, C, F2, G2, Dd = range(8)
    T5 = [(A, B, F1), (A, B, G1), (F1, G1, C), (A, B, F2), (A, B, G2), (F2, G2, Dd)]
    out["T5 R5 closure base"] = check(8, [(R5, t) for t in T5], [(C, A), (A, Dd), (C, Dd)])
    sw = {A, C, Dd}
    tw = []
    for t in T5:
        place = [i for i, v in enumerate(t) if v in sw]
        assert len(place) == 1
        tw.append((switch(R5, 1 << place[0]), t))
    out["T5 twisted (a, c, d switched)"] = check(8, tw, [(C, A), (A, Dd), (C, Dd)])
    out["two R5 knots sharing two"] = check(4, [(R5, (a, b, c)), (R5, (a, b, d))], [(c, a), (a, d), (c, d)])
    # P6: NAE {0,1,2},{0,1,3},{0,4,5},{2,4,5}, pair 3, 4
    kn = [(NAE, t) for t in ((0, 1, 2), (0, 1, 3), (0, 4, 5), (2, 4, 5))]
    st = states(6, kn)
    joint = Counter((int((s >> 3) & 1), int((s >> 4) & 1)) for s in st)
    out["P6 NAE four knots"] = {**check(6, kn, [(3, 0), (0, 4), (3, 4)]), "joint_counts_3_4": {f"{k}": v for k, v in sorted(joint.items())}}
    return out


def placements(R, n):
    """Every knot placing R on an ordered triple of n distinctions, up to placements giving the same relation on the same set."""
    seen = set()
    out = []
    for t in itertools.permutations(range(n), 3):
        key = frozenset(frozenset((t[i], (p >> i) & 1) for i in range(3)) for p in R)       # the relation on the triple's set
        if key not in seen:
            seen.add(key)
            out.append((R, t))
    return out


def one_base(args):
    n, knots = args
    st = states(n, knots)
    if len(st) == 0:
        return None
    D = bmatrix(n, st)
    return fails(D, n)[0] > 0, fails(D, n, 1)[0] > 0


def part_smallest(workers=16):
    out = {}
    with Pool(workers) as P:
        for name, R in LANG.items():
            row = {}
            for n, k in ((4, 2), (4, 3), (5, 2), (5, 3)):
                kn = placements(R, n)
                jobs = [(n, list(c)) for c in itertools.combinations(kn, k)
                        if len({v for _, t in c for v in t}) == n]
                res = [r for r in P.map(one_base, jobs, chunksize=64) if r is not None]
                row[f"n={n},knots={k}"] = {"bases": len(res), "b_fails": sum(r[0] for r in res), "b_minus_1_fails": sum(r[1] for r in res)}
            out[name] = row
            print("smallest", name, json.dumps(row), file=sys.stderr, flush=True)
    return out


def part_parity(count=1500, seed=20261118):
    rng = random.Random(seed)
    P1 = switch(P0, 7)
    res = {"bases": 0, "b_fails": 0, "b_minus_1_fails": 0, "distinctions": Counter()}
    while res["bases"] < count:
        n = rng.randint(4, 11)
        m = rng.randint(1, 7)
        kn = [(rng.choice([P0, P1]), tuple(rng.sample(range(n), 3))) for _ in range(m)]
        st = states(n, kn)
        if len(st) == 0:
            continue
        D = bmatrix(n, st)
        res["bases"] += 1
        res["distinctions"][n] += 1
        res["b_fails"] += fails(D, n)[0] > 0
        res["b_minus_1_fails"] += fails(D, n, 1)[0] > 0
    res["distinctions"] = dict(sorted(res["distinctions"].items()))
    return res


def r5_job(args):
    n, trips = args
    st = states(n, [(R5, t) for t in trips])
    if len(st) == 0:
        return None
    D = bmatrix(n, st)
    return fails(D, n)[0] > 0


def part_r5(workers=16):
    out = {}
    with Pool(workers) as P:
        for n, ks in ((6, (5, 6, 7, 8)), (7, (5, 6))):
            trip = list(itertools.combinations(range(n), 3))
            for k in ks:
                jobs = [(n, c) for c in itertools.combinations(trip, k) if len({v for t in c for v in t}) == n]
                res = P.map(r5_job, jobs, chunksize=256)
                fail = [j[1] for j, r in zip(jobs, res) if r]
                out[f"{n} distinctions, {k} R5 knots"] = {"bases": sum(r is not None for r in res), "failing": len(fail),
                                                          "example": fail[0] if fail else None}
                print("r5", n, k, out[f"{n} distinctions, {k} R5 knots"], file=sys.stderr, flush=True)
    return out


def nae_job(args):
    n, trips = args
    st = states(n, [(NAE, t) for t in trips])
    if len(st) == 0:
        return None
    D = bmatrix(n, st)
    return fails(D, n)[0] > 0


def part_nae8(workers=16):
    n = 8
    trip = list(itertools.combinations(range(n), 3))
    out = {}
    with Pool(workers) as P:
        for k in (4, 5, 6):
            jobs = []
            for c in itertools.combinations(trip, k):
                if all(len(set(x) & set(y)) <= 1 for x, y in itertools.combinations(c, 2)) and len({v for t in c for v in t}) == n:
                    jobs.append((n, c))
            res = [r for r in P.map(nae_job, jobs, chunksize=256) if r is not None]
            out[f"{k} knots"] = {"systems_allowing_a_state": len(res), "failing": sum(res)}
            print("nae8", k, out[f"{k} knots"], file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    f = {"laws": part_laws, "bases": part_bases, "smallest": part_smallest, "parity": part_parity, "r5": part_r5,
         "nae8": part_nae8}[part]
    print(json.dumps(f(), indent=1, default=str))
