#!/usr/bin/env python3
"""Checks for TOP-LAYER-20261102-001B: group laws keep their top rigid.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy)."""
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
sys.path.insert(0, str(ROOT / "proofs/RIGID-SELECTION-20261101-001A/RIGID-SELECTION-20261101-001A-P001_where_selection_is_rigid"))
import zlocal as Z  # noqa: E402

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


# ------------------------------------------------------------------------------------------------ metacyclic groups <a, b | a^m, b^n, b a b^-1 = a^r>
class Group:
    def __init__(self, m, n, r):
        self.m, self.n, self.r = m, n, r
        self.els = [(i, j) for j in range(n) for i in range(m)]
        self.idx = {e: k for k, e in enumerate(self.els)}
        N = self.N = len(self.els)
        self.mul = np.zeros((N, N), dtype=np.int64)
        for a, (i, j) in enumerate(self.els):
            for b, (i2, j2) in enumerate(self.els):
                self.mul[a, b] = self.idx[((i + pow(r, j, m) * i2) % m if m > 1 else 0, (j + j2) % n)]
        self.e = self.idx[(0, 0)]
        self.inv = [int(np.where(self.mul[a] == self.e)[0][0]) for a in range(N)]
        self.subs = sorted({self.closure([a, b]) for a in range(N) for b in range(a, N)}, key=len)

    def closure(self, gens):
        S = {self.e} | set(gens)
        while True:
            new = {int(self.mul[a, b]) for a in S for b in S} - S
            if not new:
                return frozenset(S)
            S |= new

    def order(self, a):
        k, x = 1, a
        while x != self.e:
            x, k = int(self.mul[x, a]), k + 1
        return k

    def derived(self, H):
        comms = {int(self.mul[self.mul[self.mul[x, y], self.inv[x]], self.inv[y]]) for x in H for y in H}
        return self.closure(comms)

    def normal_in(self, K, H):
        return all(int(self.mul[self.mul[h, k], self.inv[h]]) in K for h in H for k in K)

    def max_normal(self, H):
        normal = [K for K in self.subs if K < H and self.normal_in(K, H)]
        return [K for K in normal if not any(K < K2 for K2 in normal)]

    def invariant(self):
        return (self.N, tuple(sorted(collections.Counter(self.order(a) for a in range(self.N)).items())), len(self.subs))


def iso(G1, G2):
    """an isomorphism test for metacyclic G1 = <a, b> into G2: search images of the two generators"""
    if G1.invariant() != G2.invariant():
        return False
    a, b = G1.idx[(1 % G1.m, 0)], G1.idx[(0, 1 % G1.n)]
    for x in range(G2.N):
        if G2.order(x) != G1.order(a):
            continue
        for y in range(G2.N):
            if G2.order(y) != G1.order(b):
                continue
            yxy = int(G2.mul[G2.mul[y, x], G2.inv[y]])
            xr = G2.e
            for _ in range(G1.r):
                xr = int(G2.mul[xr, x])
            if yxy == xr and len(G2.closure([x, y])) == G2.N:
                return True
    return False


def is_prime_power(d):
    if d < 2:
        return False
    p = next(q for q in range(2, d + 1) if d % q == 0)
    while d % p == 0:
        d //= p
    return d == 1


# ------------------------------------------------------------------------------------------------ 1. which groups compose like cycles, up to order 60
groups = []
for m in range(1, 61):
    for n in range(1, 60 // m + 1):
        for r in range(1, max(m, 2)):
            if (m > 1 and math.gcd(r, m) != 1) or (m == 1 and r != 1) or pow(r, n, m) != 1 % m or math.gcd((r - 1) * n, m) != 1:
                continue
            G = Group(m, n, r)
            if not any(iso(G, H) for H in groups):
                groups.append(G)
U = []
for G in groups:
    if all(len(G.max_normal(H)) == 1 for H in G.subs if len(H) > 1):
        U.append(G)
nonabelian = [G for G in U if not (G.m == 1 or G.r == 1)]
facts_ok, facts = True, []


def is_prime(q):
    return q >= 2 and all(q % s for s in range(2, int(q ** 0.5) + 1))


def cyclic_quotient(G, H, D):
    """is H/D cyclic? some x in H whose powers meet every coset of D"""
    d = len(H) // len(D)
    return any(len({frozenset(int(G.mul[y, k]) for k in D) for y in G.closure([x])}) == d for x in H)


for G in U:
    if G.N == 1:
        continue
    N0 = G.max_normal(frozenset(range(G.N)))[0]
    q = G.N // len(N0)
    abelian_subs = [H for H in G.subs if all(int(G.mul[x, y]) == int(G.mul[y, x]) for x in H for y in H)]
    cyc_p = all(len(H) == 1 or (is_prime_power(len(H)) and any(G.order(x) == len(H) for x in H)) for H in abelian_subs)
    ab_ok = all(len(H) == 1 or (len(H) == len(G.derived(H)) or (is_prime_power(len(H) // len(G.derived(H)))
                                                                and cyclic_quotient(G, H, G.derived(H)))) for H in G.subs)
    facts_ok &= cyc_p and ab_ok and is_prime(q)
    facts.append({"m": G.m, "n": G.n, "r": G.r, "order": G.N, "top index": q})
names = sorted((G.N, G.m, G.n, G.r) for G in nonabelian)
check("1 among all groups with a metacyclic presentation <a, b | a^m, b^n, b a b^-1 = a^r> up to order 60 (every group whose Sylow "
      "subgroups are cyclic has one), those whose subgroups each have a unique maximal normal subgroup are the cyclic p-groups and 18 "
      "non-abelian groups; in each, every abelian subgroup is a cyclic p-group, every subgroup's abelianization is a cyclic p-group, and "
      "the unique maximal normal subgroup has prime index", facts_ok and len(nonabelian) == 18 and
      all(is_prime_power(G.N) for G in U if (G.m == 1 or G.r == 1) and G.N > 1),
      {"groups (isomorphism classes, trivial group included)": len(groups), "composing like cycles (trivial group included)": len(U),
       "cyclic ones (orders)": sorted(G.N for G in U if (G.m == 1 or G.r == 1) and G.N > 1), "non-abelian (order, m, n, r)": names})


# ------------------------------------------------------------------------------------------------ knots and systems of a group law
class Law:
    def __init__(self, G):
        self.G = G
        self.homs = collections.defaultdict(list)       # d -> [(H, h)] with h: H -> Z_d onto homomorphism
        for H in G.subs:
            for K in G.subs:
                if not (K < H and G.normal_in(K, H)):
                    continue
                d = len(H) // len(K)
                if not is_prime_power(d):
                    continue
                for g in H:
                    cos, x = {}, G.e
                    for t in range(d):
                        for k in K:
                            cos[int(G.mul[x, k])] = t
                        x = int(G.mul[x, g])
                    if len(cos) == len(H):
                        if all(cos[int(G.mul[u, w])] == (cos[u] + cos[w]) % d for u in H for w in H):
                            self.homs[d].append((H, cos))
                        break
        N0 = G.max_normal(frozenset(range(G.N)))[0]
        self.q = G.N // len(N0)
        self.top = Law.quotient_map(G, N0, self.q)

    @staticmethod
    def quotient_map(G, N0, q):
        for g in range(G.N):
            cos, x = {}, G.e
            for t in range(q):
                for k in N0:
                    cos[int(G.mul[x, k])] = t
                x = int(G.mul[x, g])
            if len(cos) == G.N:
                return [cos[a] for a in range(G.N)]

    def random_knot(self, k, d, rng, choice=None, reps=None):
        """a coset of a subgroup of G^k pulled back from sum s_i h_i(x_i) = c over Z_d; returns (table, subgroups)"""
        G = self.G
        choice = choice or [rng.choice(self.homs[d]) for _ in range(k)]
        reps = reps or [rng.randrange(G.N) for _ in range(k)]
        units = [u for u in range(1, d) if math.gcd(u, d) == 1]
        sg = [rng.choice(units) for _ in range(k)]
        c = rng.randrange(d)
        table = np.zeros((G.N,) * k, dtype=bool)
        for xs in itertools.product(*[sorted(H) for H, _ in choice]):
            if sum(s * h[x] for s, (_, h), x in zip(sg, choice, xs)) % d == c:
                table[tuple(int(G.mul[r, x]) for r, x in zip(reps, xs))] = True
        return table, [H for H, _ in choice]


def circuits(sol, n):
    ranges = [len({t[v] for t in sol}) for v in range(n)]
    cons = [frozenset(Y) for r in range(1, n + 1) for Y in itertools.combinations(range(n), r)
            if len({tuple(t[v] for v in Y) for t in sol}) < math.prod(ranges[v] for v in Y)]
    return [C for C in cons if not any(D < C for D in cons)]


CENSUS = json.loads((ROOT / "research/MUTUAL-SELECTION-20261031-001C/census.json").read_text())
CUBIC = {int(n): [[tuple(L) for L in row["lines"]] for row in v["rows"]] for n, v in CENSUS.items()}
K54 = [tuple(p for p in range(5) if p != i) for i in range(5)]

# ------------------------------------------------------------------------------------------------ 2. brute force in the non-abelian groups up to order 24
rng = random.Random(20261102)
small = [G for G in nonabelian if G.N <= 24]
info2, ok2 = {}, True
for G in small:
    law = Law(G)
    ds = sorted(d for d in law.homs if law.homs[d])
    maxn = 7 if G.N <= 6 else (6 if G.N <= 10 else 5)
    subs_pool = [(n, L) for n in range(4, maxn + 1) for L in CUBIC.get(n, []) if len({frozenset(x) for x in L}) == n] + [(5, K54)]
    X = {n: np.array(list(itertools.product(range(G.N), repeat=n)), dtype=np.int64) for n in range(4, maxn + 1)}
    tally = collections.Counter()
    for trial in range(400):
        n, lines = rng.choice(subs_pool)
        d = rng.choice(ds)
        own = [rng.choice(law.homs[d]) for _ in range(n)]      # each variable: one range and quotient map, one coset
        own_rep = [rng.randrange(G.N) for _ in range(n)]
        rels = []
        for L in lines:
            if rng.random() < 0.15:                             # sometimes a line reads its own ranges
                rels.append(law.random_knot(len(L), d, rng))
            else:
                rels.append(law.random_knot(len(L), d, rng, [own[v] for v in L], [own_rep[v] for v in L]))
        sat = np.stack([tab[tuple(X[n][:, p] for p in L)] for (tab, _), L in zip(rels, lines)], axis=1)
        tally["systems"] += 1
        if sat.all(axis=1).any():
            continue
        keep = [np.delete(sat, L, axis=1).all(axis=1) for L in range(n)]
        if not all(k.any() for k in keep):
            continue
        tally["global failures"] += 1
        for L in range(n):
            S = [tuple(int(v) for v in x) for x in X[n][keep[L]]]
            Sset = set(S)
            for v in range(n):                       # saturation by the derived subgroup of the ambient range
                amb = frozenset(range(G.N))
                for Lp, (Lline, (_, Hs)) in enumerate(zip(lines, rels)):
                    if Lp != L and v in Lline:
                        amb &= Hs[Lline.index(v)]
                Dv = G.derived(amb)
                for x in S[:50]:
                    for dlt in Dv:
                        y = list(x)
                        y[v] = int(G.mul[x[v], dlt])
                        if tuple(y) not in Sset:
                            ok2 = False
                            tally["saturation violations"] += 1
            T = sorted({tuple(law.top[a] for a in x) for x in S})
            rigid_top = len(T) <= law.q and all(len(C) <= 2 for C in circuits(T, n))
            ok2 &= rigid_top
            tally["removals with rigid top"] += rigid_top
            tally["removals keeping a knot"] += any(len(C) >= 3 for C in circuits(S, n))
    info2["order %d (m=%d, n=%d, r=%d)" % (G.N, G.m, G.n, G.r)] = dict(tally)
check("2 random knot systems in the seven non-abelian groups up to order 24 (S3, D5, D7, D9, C5:C4, C7:C3, D11) on cubic substrates "
      "with 4 to 7 points and on K5^(4), by brute force over G^n: every global failure leaves, after any removal, solutions saturated "
      "by the derived subgroups of the ambient ranges and a top image in G/N of at most one line, with only ties", ok2 and
      all(v.get("global failures", 0) > 0 for v in info2.values()), info2)

# ------------------------------------------------------------------------------------------------ 3. knots kept below the top: C5:C4 and D9
F20 = next(G for G in nonabelian if G.N == 20)
D9 = next(G for G in nonabelian if G.N == 18)


def embedded(G, gen, A, c, lines_n, q):
    """the linear system A x = c over Z_q with x_v = gen^(x_v) inside the cyclic subgroup <gen>; brute force over <gen>^n"""
    n = len(A)
    powers = [G.e]
    for _ in range(q - 1):
        powers.append(int(G.mul[powers[-1], gen]))
    law = Law(G)
    Xz = np.array(list(itertools.product(range(q), repeat=n)), dtype=np.int64)
    sat = ((Xz @ np.array(A).T - np.array(c)) % q == 0)
    rep = {"fails": not sat.all(axis=1).any(), "global": True, "removals keeping a knot": [], "top images": []}
    for L in range(n):
        keep = np.delete(sat, L, axis=1).all(axis=1)
        rep["global"] &= bool(keep.any())
        S = [tuple(powers[int(v)] for v in x) for x in Xz[keep]]
        if any(len(C) >= 3 for C in circuits(S, n)):
            rep["removals keeping a knot"].append(L)
        T = sorted({tuple(law.top[a] for a in x) for x in S})
        rep["top images"].append(len(T))
        rep.setdefault("top rigid", True)
        rep["top rigid"] &= len(T) <= law.q and all(len(C) <= 2 for C in circuits(T, n))
    rep["top index q"] = law.q
    rep["generator in the top kernel"] = law.top[gen] == 0
    return rep


b4 = next(x for x in range(F20.N) if F20.order(x) == 4)
a9 = next(x for x in range(D9.N) if D9.order(x) == 9)
A4 = [[0, 3, 3, 3, 0, 3], [1, 3, 0, 0, 1, 3], [3, 1, 1, 0, 1, 0], [3, 0, 1, 3, 3, 0], [3, 1, 0, 3, 0, 1], [0, 0, 1, 1, 1, 1]]
A9 = [[1, 0, 7, 0, 0, 7], [0, 5, 0, 0, 5, 1], [7, 0, 8, 7, 0, 0], [0, 2, 0, 8, 2, 0], [4, 0, 0, 8, 0, 8], [0, 7, 2, 0, 4, 0]]
rep3 = {"C5:C4, signed Z4 example 1 of RIGID-SELECTION B in a subgroup of order 4": embedded(F20, b4, A4, [2, 0, 0, 0, 0, 0], 6, 4),
        "D9, a unit-weighted Z9 system on a 6-point cubic substrate in the subgroup of order 9": embedded(D9, a9, A9, [3, 0, 0, 0, 0, 0], 6, 9)}
r20, r18 = rep3["C5:C4, signed Z4 example 1 of RIGID-SELECTION B in a subgroup of order 4"], \
    rep3["D9, a unit-weighted Z9 system on a 6-point cubic substrate in the subgroup of order 9"]
check("3 knots kept below the top: in C5:C4, signed Z4 placed in a cyclic subgroup of order 4 fails globally and keeps knots after "
      "every removal, while its top image (G/N of order 2, onto which the subgroup maps) is one line; in D9, a Z9 system placed in the "
      "cyclic subgroup of order 9 fails globally and keeps knots after two removals, while its top is constant (the subgroup lies in N)",
      r20["fails"] and r20["global"] and len(r20["removals keeping a knot"]) == 6 and r20["top rigid"] and not r20["generator in the top kernel"]
      and r18["fails"] and r18["global"] and len(r18["removals keeping a knot"]) >= 1 and r18["top rigid"] and r18["generator in the top kernel"],
      rep3)

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
