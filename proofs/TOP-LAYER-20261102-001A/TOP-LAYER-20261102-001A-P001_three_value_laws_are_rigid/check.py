#!/usr/bin/env python3
"""Checks for TOP-LAYER-20261102-001A: every law on three values that composes like cycles is rigid.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy). About five minutes."""
import collections
import hashlib
import itertools
import json
import math
import random
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]
          if p.endswith(".json") and p.startswith("proofs/")}
check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
      {"mismatched": bad, "statuses": status})

# ------------------------------------------------------------------------------------------------ 1. the Mal'tsev operations on three values
TRIP = list(itertools.product(range(3), repeat=3))
TIDX = {t: i for i, t in enumerate(TRIP)}
fixed = {}
for (x, y, z) in TRIP:
    if x == y:
        fixed[TIDX[(x, y, z)]] = z
    elif y == z:
        fixed[TIDX[(x, y, z)]] = x
free = [i for i in range(27) if i not in fixed]
NOPS = 3 ** len(free)
OPS = np.zeros((NOPS, 27), dtype=np.int8)
for i, v in fixed.items():
    OPS[:, i] = v
codes = np.arange(NOPS)
for k, i in enumerate(free):
    OPS[:, i] = (codes // (3 ** k)) % 3


def cong_mask(a, b):
    cls = np.array([0 if v in (a, b) else 1 for v in range(3)], dtype=np.int8)
    good = np.ones(NOPS, dtype=bool)
    for pos in range(3):
        for others in itertools.product(range(3), repeat=2):
            t1, t2 = list(others), list(others)
            t1.insert(pos, a)
            t2.insert(pos, b)
            good &= cls[OPS[:, TIDX[tuple(t1)]]] == cls[OPS[:, TIDX[tuple(t2)]]]
    return good


ncong = sum(cong_mask(*p).astype(int) for p in ((0, 1), (0, 2), (1, 2)))
PERMS = list(itertools.permutations(range(3)))


def conj(op, p):
    inv = [p.index(v) for v in range(3)]
    return tuple(p[op[TIDX[(inv[x], inv[y], inv[z])]]] for (x, y, z) in TRIP)


def classes(indices):
    seen = {}
    for i in indices:
        op = tuple(int(v) for v in OPS[i])
        seen.setdefault(min(conj(op, p) for p in PERMS), []).append(int(i))
    return seen


NONSIMPLE = classes(np.where(ncong == 1)[0])
simple_idx = np.where(ncong == 0)[0]
Z3 = tuple((x - y + z) % 3 for (x, y, z) in TRIP)
check("1 of the 531441 Mal'tsev operations on three values, 1020 have exactly one nontrivial congruence (none has two); up to "
      "relabelling they form 185 classes", NOPS == 531441 and int((ncong == 1).sum()) == 1020 and int((ncong >= 2).sum()) == 0
      and len(NONSIMPLE) == 185, {"operations": NOPS, "non-simple": int((ncong == 1).sum()), "classes": len(NONSIMPLE),
                                  "simple": int((ncong == 0).sum())})


# ------------------------------------------------------------------------------------------------ the algebra of one operation
class Algebra:
    def __init__(self, op):
        self.op = op
        self.m = lambda x, y, z: op[TIDX[(x, y, z)]]
        self.subs = [S for r in (2, 3) for S in itertools.combinations(range(3), r)
                     if all(self.m(x, y, z) in S for x in S for y in S for z in S)]
        self.homs = []                                   # (range, q, h) with h: range -> Z_q an onto homomorphism
        for S in self.subs:
            for q in (2, 3):
                for h in itertools.product(range(q), repeat=len(S)):
                    hd = dict(zip(S, h))
                    if len(set(h)) == q and all(hd[self.m(x, y, z)] == (hd[x] - hd[y] + hd[z]) % q
                                                for x in S for y in S for z in S):
                        self.homs.append((S, q, hd))

    def pulled_back_knots(self, k):
        out = set()
        for q in (2, 3):
            hs = [h for h in self.homs if h[1] == q]
            signs = [(1,)] if q == 2 else [(1, 2)]
            for combo in itertools.product(hs, repeat=k):
                for sg in itertools.product(*(signs * k)):
                    for c in range(q):
                        K = frozenset(t for t in itertools.product(*[S for S, _, _ in combo])
                                      if sum(s * hd[v] for s, (_, _, hd), v in zip(sg, combo, t)) % q == c)
                        out.add(K)
        return out

    def subuniverses_cube(self):
        els = TRIP
        M = len(els)
        T = np.zeros((M, M, M), dtype=np.int16)
        for a in range(M):
            for b in range(M):
                for c in range(M):
                    T[a, b, c] = TIDX[tuple(self.m(els[a][j], els[b][j], els[c][j]) for j in range(3))]

        def close(S):
            S = np.array(sorted(S), dtype=np.int64)
            while True:
                U = np.union1d(S, np.unique(T[np.ix_(S, S, S)]))
                if len(U) == len(S):
                    return frozenset(int(x) for x in S)
                S = U
        found, frontier = set(), []
        for t in range(M):
            s = close([t])
            if s not in found:
                found.add(s)
                frontier.append(s)
        while frontier:
            nxt = []
            for s in frontier:
                for t in range(M):
                    if t not in s:
                        u = close(set(s) | {t})
                        if u not in found:
                            found.add(u)
                            nxt.append(u)
            frontier = nxt
        return [frozenset(els[i] for i in s) for s in found]


def is_knot(R, k):
    ranges = [{t[i] for t in R} for i in range(k)]
    if any(len(r) < 2 for r in ranges) or len(R) >= math.prod(len(r) for r in ranges):
        return False
    return all(len({t[:i] + t[i + 1:] for t in R}) == math.prod(len(r) for j, r in enumerate(ranges) if j != i) for i in range(k))


def circuits(sol, n):
    ranges = [len({t[v] for t in sol}) for v in range(n)]
    cons = [frozenset(Y) for r in range(1, n + 1) for Y in itertools.combinations(range(n), r)
            if len({tuple(t[v] for v in Y) for t in sol}) < math.prod(ranges[v] for v in Y)]
    return [C for C in cons if not any(D < C for D in cons)]


# ------------------------------------------------------------------------------------------------ 2. three-place knots, exhaustively
ALG = {}
info2 = collections.Counter()
ok2 = True
for key in sorted(NONSIMPLE):
    A = Algebra(key)
    knots = {R for R in A.subuniverses_cube() if is_knot(R, 3)}
    pulled = {R for R in A.pulled_back_knots(3) if is_knot(R, 3)}
    ok2 &= knots == pulled and all(len({hd[v] for v in S}) == 2 for S, q, hd in A.homs if q == 2) and not [h for h in A.homs if h[1] == 3]
    A.k3 = sorted(knots, key=lambda R: sorted(R))
    ALG[key] = A
    info2["classes"] += 1
    info2["three-place knots"] += len(knots)
    info2["classes with a knot"] += bool(knots)
check("2 for each of the 185 classes, every three-place knot (all subuniverses of A^3 enumerated) is pulled back from a two-element "
      "abelian section, and every such pull-back is a knot: the two sets coincide; no class has a three-element abelian section",
      ok2, dict(info2))

# ------------------------------------------------------------------------------------------------ substrates
CENSUS = json.loads((ROOT / "research/MUTUAL-SELECTION-20261031-001C/census.json").read_text())
GRAPHS = [(int(n), [tuple(L) for L in row["lines"]]) for n, v in sorted(CENSUS.items(), key=lambda kv: int(kv[0])) for row in v["rows"]]


def dual(lines, n):
    return [tuple(i for i, L in enumerate(lines) if p in L) for p in range(n)]


def canon(lines, n):
    return min(tuple(sorted(tuple(sorted(perm[p] for p in L)) for L in lines)) for perm in itertools.permutations(range(n)))


CUBIC = []
for n, lines in GRAPHS:
    CUBIC.append((n, lines))
    if canon(lines, n) != canon(dual(lines, n), n):
        CUBIC.append((n, dual(lines, n)))
rng = random.Random(20261102)


def random_regular(n, k, tries=4000):
    for _ in range(tries):
        pts = [p for p in range(n) for _ in range(k)]
        rng.shuffle(pts)
        lines = [tuple(pts[i * k:(i + 1) * k]) for i in range(n)]
        if all(len(set(L)) == k for L in lines) and len({frozenset(L) for L in lines}) == n:
            return lines
    return None


XS = {n: np.array(list(itertools.product(range(3), repeat=n)), dtype=np.int64) for n in range(3, 10)}


def run_system(n, lines, rels):
    """brute force: (fails, global, rigid at every removal) for the system with relation rels[i] on lines[i] (in its order)"""
    X = XS[n]
    sat = np.zeros((len(X), len(lines)), dtype=bool)
    for i, (L, R) in enumerate(zip(lines, rels)):
        table = np.zeros((3,) * len(L), dtype=bool)
        for t in R:
            table[t] = True
        sat[:, i] = table[tuple(X[:, p] for p in L)]
    if sat.all(axis=1).any():
        return False, False, None
    keep = [np.delete(sat, L, axis=1).all(axis=1) for L in range(len(lines))]
    if not all(k.any() for k in keep):
        return True, False, None
    rigid = all(all(len(C) <= 2 for C in circuits([tuple(int(v) for v in x) for x in X[k]], n)) for k in keep)
    return True, True, rigid


def placed(R, L):
    """the relation R placed on line L with a random assignment of the line's points to R's coordinates"""
    perm = list(range(len(L)))
    rng.shuffle(perm)
    return [L[i] for i in perm], R


# ------------------------------------------------------------------------------------------------ 3. cubic census, three-place knots
tally3 = collections.Counter()
ok3 = True
for key, A in ALG.items():
    if not A.k3:
        continue
    for n, lines in CUBIC:
        for _ in range(4):
            ls, rels = zip(*[placed(rng.choice(A.k3), L) for L in lines])
            fails, glob, rigid = run_system(n, ls, rels)
            tally3["systems"] += 1
            tally3["failing"] += fails
            if glob:
                tally3["failing globally"] += 1
                tally3["global and rigid"] += rigid
                ok3 &= rigid
check("3 random systems of three-place knots of every class on all 73 cubic substrates: global failures occur (a variable confined to "
      "a two-element block shortens the parity of a line that reads its top bit), and every one is rigid", ok3 and
      tally3["failing globally"] > 0, dict(tally3))

# ------------------------------------------------------------------------------------------------ 4. 4-regular substrates, four-place knots
tally4 = collections.Counter()
ok4 = True
for key, A in ALG.items():
    k4 = [R for R in A.pulled_back_knots(4) if is_knot(R, 4)]
    if not k4:
        continue
    tally4["classes with four-place knots"] += 1
    for _ in range(30):
        n = rng.choice((5, 6, 6, 7, 7, 8))
        lines = random_regular(n, 4)
        if not lines:
            continue
        ls, rels = zip(*[placed(rng.choice(k4), L) for L in lines])
        fails, glob, rigid = run_system(n, ls, rels)
        tally4["systems"] += 1
        tally4["failing globally"] += glob
        if glob:
            tally4["global and rigid"] += rigid
            ok4 &= rigid
check("4 random systems of four-place knots (pulled back from two-element sections) of every class on random 4-regular substrates with "
      "5 to 8 points: every global failure is rigid", ok4 and tally4["failing globally"] > 0, dict(tally4))

# ------------------------------------------------------------------------------------------------ 5. Z3 and sampled simple laws
SIMPLE = classes(rng.sample(list(simple_idx), 3000))
sample = rng.sample(sorted(k for k in SIMPLE if k != Z3), 300) + [Z3]
tally5 = collections.Counter()
ok5 = True
for key in sample:
    A = Algebra(key)
    knots = {R for R in A.subuniverses_cube() if is_knot(R, 3)}
    pulled = {R for R in A.pulled_back_knots(3) if is_knot(R, 3)}
    ok5 &= knots == pulled
    tally5["classes"] += 1
    tally5["classes with a knot"] += bool(knots)
    tally5["with a three-element section"] += any(q == 3 for _, q, _ in A.homs)
    if not knots:
        continue
    knots = sorted(knots, key=lambda R: sorted(R))
    for n, lines in CUBIC[::4] if key != Z3 else CUBIC:
        for _ in range(1 if key != Z3 else 30):
            ls, rels = zip(*[placed(rng.choice(knots), L) for L in lines])
            fails, glob, rigid = run_system(n, ls, rels)
            tally5["cubic systems"] += 1
            if glob:
                tally5["cubic global failures"] += 1
                ok5 &= rigid
    k4 = [R for R in A.pulled_back_knots(4) if is_knot(R, 4)]
    for _ in range(6 if key != Z3 else 60):
        n = rng.choice((5, 6, 7))
        lines = random_regular(n, 4)
        if not lines or not k4:
            continue
        ls, rels = zip(*[placed(rng.choice(k4), L) for L in lines])
        fails, glob, rigid = run_system(n, ls, rels)
        tally5["4-regular systems"] += 1
        if glob:
            tally5["4-regular global failures"] += 1
            ok5 &= rigid
check("5 Z3 and 300 sampled classes of simple Mal'tsev laws on three values: every three-place knot is pulled back from a two- or "
      "three-element abelian section (the sets coincide), and every global failure found on cubic and 4-regular substrates is rigid",
      ok5 and tally5["cubic global failures"] > 0 and tally5["4-regular global failures"] > 0, dict(tally5))

OUT["seconds"] = round(time.time() - T0, 1)
print("ALL OK", OUT["seconds"], "s")
result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"], "proof": manifest["proof"],
          "status": "passed", "claim": manifest["claim"], "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
if "--write" in sys.argv:
    (HERE / "result.json").write_text(text)
elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
    print("result.json does not match a fresh run; rerun with --write after review")
    sys.exit(1)
