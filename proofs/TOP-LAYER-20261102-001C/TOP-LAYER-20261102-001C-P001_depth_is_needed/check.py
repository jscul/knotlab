#!/usr/bin/env python3
"""Checks for TOP-LAYER-20261102-001C: depth is needed (simple abelian sections force rigid selection).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy). About ten minutes."""
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

V = 4
TR = list(itertools.product(range(V), repeat=3))


# ------------------------------------------------------------------------------------------------ algebras on four values with one Mal'tsev operation
def partitions(s):
    s = list(s)
    if not s:
        yield []
        return
    first, rest = s[0], s[1:]
    for p in partitions(rest):
        for i in range(len(p)):
            yield p[:i] + [[first] + p[i]] + p[i + 1:]
        yield [[first]] + p


class Alg:
    def __init__(self, m):
        self.m = m
        self.subs = [frozenset(S) for r in range(1, V + 1) for S in itertools.combinations(range(V), r)
                     if all(m[(x, y, z)] in S for x in S for y in S for z in S)]
        self.cons = {S: self.congruences(S) for S in self.subs}
        self._ab, self._der = {}, {}

    def congruences(self, S):
        out = []
        for p in partitions(sorted(S)):
            cls = {x: i for i, b in enumerate(p) for x in b}
            if all(cls[self.m[(a, y, z)]] == cls[self.m[(b, y, z)]] and cls[self.m[(y, a, z)]] == cls[self.m[(y, b, z)]]
                   and cls[self.m[(y, z, a)]] == cls[self.m[(y, z, b)]]
                   for a in S for b in S if cls[a] == cls[b] and a != b for y in S for z in S):
                out.append(cls)
        return out

    def abelian_quotient(self, S, cls):
        """is S/cls abelian? for an algebra whose only operation is a Mal'tsev operation, iff the operation is medial on the quotient"""
        key = (S, tuple(sorted({frozenset(x for x in S if cls[x] == cls[y]) for y in S}, key=sorted)))
        if key not in self._ab:
            self._ab[key] = self._abelian(S, cls)
        return self._ab[key]

    def _abelian(self, S, cls):
        reps = {}
        for x in S:
            reps.setdefault(cls[x], x)
        R = list(reps.values())
        k = len(R)
        lab = {cls[r]: i for i, r in enumerate(R)}
        Q = np.zeros((k, k, k), dtype=np.int64)          # the quotient operation on class indices
        for i, a in enumerate(R):
            for j, b in enumerate(R):
                for l, c in enumerate(R):
                    Q[i, j, l] = lab[cls[self.m[(a, b, c)]]]
        g = np.array(list(itertools.product(range(k), repeat=9)), dtype=np.int64).T
        lhs = Q[Q[g[0], g[1], g[2]], Q[g[3], g[4], g[5]], Q[g[6], g[7], g[8]]]
        rhs = Q[Q[g[0], g[3], g[6]], Q[g[1], g[4], g[7]], Q[g[2], g[5], g[8]]]
        return bool((lhs == rhs).all())

    def derived(self, S):
        """[1,1] of S: the meet of the congruences with an abelian quotient"""
        if S not in self._der:
            ab = [c for c in self.cons[S] if self.abelian_quotient(S, c)]
            self._der[S] = {x: tuple(c[x] for c in ab) for x in S}
        return self._der[S]

    def sections_simple(self):
        """is every abelian section S/alpha simple, i.e. alpha = 1 or alpha a maximal congruence of S?"""
        for S in self.subs:
            cons = self.cons[S]
            for c in cons:
                k = len(set(c.values()))
                if k <= 1 or not self.abelian_quotient(S, c):
                    continue
                coarser = [d for d in cons if len(set(d.values())) < k and all(d[a] == d[b] for a in S for b in S if c[a] == c[b])]
                if any(len(set(d.values())) > 1 for d in coarser):
                    return False
        return True

    def cube_subuniverses(self):
        els = TR
        ei = {t: i for i, t in enumerate(els)}
        M = len(els)
        T = np.zeros((M, M, M), dtype=np.int16)
        for a in range(M):
            for b in range(M):
                for c in range(M):
                    T[a, b, c] = ei[tuple(self.m[(els[a][j], els[b][j], els[c][j])] for j in range(3))]

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


rng = random.Random(20261102)
BLK = [0, 0, 1, 1]


def random_layered():
    """Mal'tsev, with the congruence {0,1}|{2,3} and an affine quotient; other entries random"""
    m = {}
    for (x, y, z) in TR:
        if x == y:
            m[(x, y, z)] = z
        elif y == z:
            m[(x, y, z)] = x
        else:
            b = (BLK[x] + BLK[y] + BLK[z]) % 2
            m[(x, y, z)] = rng.choice([v for v in range(V) if BLK[v] == b])
    return m


def random_free():
    return {(x, y, z): (z if x == y else x if y == z else rng.randrange(V)) for (x, y, z) in TR}


# ------------------------------------------------------------------------------------------------ 1. the lemmas on random algebras
ALGS = [("layered", random_layered()) for _ in range(20)] + [("free", random_free()) for _ in range(6)]
info1, ok1 = collections.Counter(), True
KNOTS = {}
for i, (kind, m) in enumerate(ALGS):
    A = Alg(m)
    knots = [R for R in A.cube_subuniverses() if is_knot(R, 3)]
    KNOTS[i] = (A, knots)
    info1["algebras"] += 1
    info1["knots"] += len(knots)
    for R in knots:
        for i_ in range(3):
            Ri = sorted({t[i_] for t in R})
            others = [j for j in range(3) if j != i_]
            fibres = collections.defaultdict(set)
            for t in R:
                fibres[tuple(t[j] for j in others)].add(t[i_])
            rho = {}                                  # the fork relation: two values related if they share a fibre
            for f in fibres.values():
                for a in f:
                    for b in f:
                        rho.setdefault(a, set()).add(b)
            cls = {}
            for a in Ri:
                cls[a] = min(rho[a])
            is_cong = any(c == {a: cls[a] for a in Ri} or all((c[a] == c[b]) == (cls[a] == cls[b]) for a in Ri for b in Ri)
                          for c in A.cons[frozenset(Ri)])
            ab = A.abelian_quotient(frozenset(Ri), cls)
            sat = all(tuple(b if j == i_ else t[j] for j in range(3)) in R for t in R for b in Ri if cls[b] == cls[t[i_]])
            ok1 &= is_cong and ab and sat
            info1["forks checked"] += 1
check("1 on 26 random Mal'tsev algebras on four values (20 with a congruence {0,1}|{2,3} and an affine quotient, 6 unrestricted), "
      "every three-place knot (all subuniverses of A^3 enumerated): each fork relation is a congruence of the range, its quotient "
      "is abelian, and the knot is a union of fork classes", ok1 and info1["knots"] > 0, dict(info1))

# ------------------------------------------------------------------------------------------------ 2. the theorem: simple sections force rigidity
CENSUS = json.loads((ROOT / "research/MUTUAL-SELECTION-20261031-001C/census.json").read_text())
CUBIC = [(int(n), [tuple(L) for L in row["lines"]]) for n, v in CENSUS.items() if int(n) <= 7 for row in v["rows"]]
CUBIC += [(n, [tuple(i for i, L in enumerate(lines) if p in L) for p in range(n)]) for n, lines in CUBIC]


def random_regular(n, k, tries=4000):
    for _ in range(tries):
        pts = [p for p in range(n) for _ in range(k)]
        rng.shuffle(pts)
        lines = [tuple(pts[i * k:(i + 1) * k]) for i in range(n)]
        if all(len(set(L)) == k for L in lines) and len({frozenset(L) for L in lines}) == n:
            return lines
    return None


XS = {n: np.array(list(itertools.product(range(V), repeat=n)), dtype=np.int64) for n in range(3, 8)}


def four_place_knots(knots, count):
    out = set()
    for _ in range(400):
        if len(out) >= count:
            break
        K1, K2 = rng.choice(knots), rng.choice(knots)
        p1, p2 = list(rng.sample(range(3), 3)), list(rng.sample(range(3), 3))
        R = set()
        for t1 in K1:
            a = [t1[p] for p in p1]
            for t2 in K2:
                b = [t2[p] for p in p2]
                if a[2] == b[0]:
                    R.add((a[0], a[1], b[1], b[2]))
        R = frozenset(R)
        if is_knot(R, 4):
            out.add(R)
    return sorted(out, key=sorted)


def run(A, n, lines, rels):
    X = XS[n]
    sat = np.zeros((len(X), n), dtype=bool)
    for i, (L, R) in enumerate(zip(lines, rels)):
        tab = np.zeros((V,) * len(L), dtype=bool)
        for t in R:
            tab[t] = True
        sat[:, i] = tab[tuple(X[:, p] for p in L)]
    if sat.all(axis=1).any():
        return None
    keep = [np.delete(sat, L, axis=1).all(axis=1) for L in range(n)]
    if not all(k.any() for k in keep):
        return None
    rigid, saturated = True, True
    for L in range(n):
        S = [tuple(int(v) for v in x) for x in X[keep[L]]]
        Sset = set(S)
        rigid &= all(len(C) <= 2 for C in circuits(S, n))
        for v in range(n):
            amb = set(range(V))
            for Lp, (Lline, R) in enumerate(zip(lines, rels)):
                if Lp != L and v in Lline:
                    amb &= {t[Lline.index(v)] for t in R}
            amb = frozenset(amb)
            if amb not in A.cons:
                continue
            der = A.derived(amb)
            for x in S[:40]:
                for y in amb:
                    if der[y] == der[x[v]]:
                        z = list(x)
                        z[v] = y
                        saturated &= tuple(z) in Sset
    return rigid, saturated


info2, ok2 = collections.Counter(), True
for i, (A, knots) in KNOTS.items():
    simple = A.sections_simple()
    info2["algebras with every abelian section simple" if simple else "algebras with a non-simple abelian section"] += 1
    if not knots:
        continue
    k4 = four_place_knots(knots, 20)
    for _ in range(60):
        if rng.random() < 0.5 or not k4:
            n, lines = rng.choice(CUBIC)
            rels = [rng.choice(knots) for _ in lines]
        else:
            n = rng.choice((5, 6))
            lines = random_regular(n, 4)
            if not lines:
                continue
            rels = [rng.choice(k4) for _ in lines]
        lines = [tuple(rng.sample(L, len(L))) for L in lines]
        r = run(A, n, lines, rels)
        if r is None:
            continue
        rigid, saturated = r
        ok2 &= saturated
        key = "simple sections" if simple else "non-simple sections"
        info2["global failures, " + key] += 1
        info2["rigid, " + key] += rigid
        if simple:
            ok2 &= rigid
check("2 random systems of three-place knots on cubic substrates (up to 7 points, both readings) and four-place knots on 4-regular "
      "substrates (5 and 6 points) for every algebra of check 1: every global failure leaves solutions saturated by the derived "
      "congruences of the ambient ranges, and where every abelian section is simple every global failure is rigid", ok2 and
      info2["global failures, simple sections"] > 0, dict(info2))

# ------------------------------------------------------------------------------------------------ 2b. declared domains, the case the proof covers
info2b, ok2b = collections.Counter(), True
for i, (A, knots) in KNOTS.items():
    if not knots or not A.sections_simple():
        continue
    by_ranges = collections.defaultdict(list)
    for R in knots:
        for perm in itertools.permutations(range(3)):
            Rp = frozenset(tuple(t[j] for j in perm) for t in R)
            by_ranges[tuple(frozenset(t[j] for t in Rp) for j in range(3))].append(Rp)
    by_ranges4 = collections.defaultdict(list)
    for R in four_place_knots(knots, 40):
        for perm in itertools.permutations(range(4)):
            Rp = frozenset(tuple(t[j] for j in perm) for t in R)
            by_ranges4[tuple(frozenset(t[j] for t in Rp) for j in range(4))].append(Rp)
    domains = sorted({d for key in by_ranges for d in key}, key=sorted)
    domains4 = sorted({d for key in by_ranges4 for d in key}, key=sorted)
    for _ in range(160):
        if rng.random() < 0.3 or not domains4:
            n, lines, table, doms = *rng.choice(CUBIC), by_ranges, domains
        else:
            n = rng.choice((5, 6))
            lines, table, doms = random_regular(n, 4), by_ranges4, domains4
            if not lines:
                continue
        dom = [rng.choice(doms) for _ in range(n)] if rng.random() < 0.5 else [rng.choice(doms)] * n
        options = [table.get(tuple(dom[v] for v in L), []) for L in lines]
        if not all(options):
            continue
        rels = [rng.choice(o) for o in options]
        info2b["systems"] += 1
        r = run(A, n, lines, rels)
        if r is None:
            continue
        info2b["global failures"] += 1
        info2b["rigid"] += r[0]
        ok2b &= r[0] and r[1]
check("2b systems with declared domains (every point carries one subalgebra and every line carries a knot whose ranges are its points' "
      "domains), on cubic substrates and on 4-regular substrates with 5 and 6 points, for every algebra of check 1 whose abelian sections "
      "are all simple: every global failure is rigid and saturated", ok2b and info2b["global failures"] > 0, dict(info2b))

# ------------------------------------------------------------------------------------------------ 3. controls: Z4 (two layers, not rigid) and T2(F2) (two layers, rigid)
Z4 = {(x, y, z): (x - y + z) % 4 for (x, y, z) in TR}
AZ = Alg(Z4)
A4 = [[0, 3, 3, 3, 0, 3], [1, 3, 0, 0, 1, 3], [3, 1, 1, 0, 1, 0], [3, 0, 1, 3, 3, 0], [3, 1, 0, 3, 0, 1], [0, 0, 1, 1, 1, 1]]
X6 = np.array(list(itertools.product(range(4), repeat=6)), dtype=np.int64)
satz = (X6 @ np.array(A4).T - np.array([2, 0, 0, 0, 0, 0])) % 4 == 0
kept = sum(any(len(C) >= 3 for C in circuits([tuple(int(v) for v in x) for x in X6[np.delete(satz, L, axis=1).all(axis=1)]], 6))
           for L in range(6))
tally_t2 = collections.Counter()
ok_t2 = True
for _ in range(1500):
    k = rng.choice((3, 4))
    n = rng.randint(k + 1, 7)
    lines = random_regular(n, k)
    if not lines:
        continue
    X = XS[n]
    bot, top = X & 1, X >> 1
    sat = np.zeros((len(X), n), dtype=bool)
    for i, L in enumerate(lines):                       # a T2(F2) knot: top parity, and bottom parity or nothing (V inside U)
        ok = (top[:, list(L)].sum(axis=1) - rng.randrange(2)) % 2 == 0
        if rng.random() < 0.5:
            ok &= (bot[:, list(L)].sum(axis=1) - rng.randrange(2)) % 2 == 0
        sat[:, i] = ok
    if sat.all(axis=1).any():
        continue
    keep = [np.delete(sat, L, axis=1).all(axis=1) for L in range(n)]
    if not all(kk.any() for kk in keep):
        continue
    tally_t2["global failures"] += 1
    tally_t2["of which on cubic substrates"] += k == 3
    rig = all(all(len(C) <= 2 for C in circuits([tuple(int(v) for v in x) for x in X[kk]], n)) for kk in keep)
    tally_t2["rigid"] += rig
    ok_t2 &= rig
check("3 controls. Z4 has a two-layer abelian section (itself), and RIGID-SELECTION B's example keeps knots after every removal, so "
      "the hypothesis is needed. The T2(F2)-module has a two-layer section too, yet every global failure of its knot systems on random "
      "regular substrates is rigid (none on cubic ones): depth is necessary, not sufficient",
      not AZ.sections_simple() and kept == 6 and ok_t2 and tally_t2["global failures"] > 0 and tally_t2["of which on cubic substrates"] == 0,
      {"Z4 has a non-simple abelian section": not AZ.sections_simple(), "Z4 example: removals keeping a knot (of 6)": kept,
       "T2(F2)": dict(tally_t2)})

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
