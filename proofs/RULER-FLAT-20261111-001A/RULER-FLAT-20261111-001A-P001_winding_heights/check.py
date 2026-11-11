#!/usr/bin/env python3
"""Finite checks for RULER-FLAT-20261111-001A-P001: the ruler on tori, by winding heights.

The proof (proof.md) covers every torus. These checks support it:
  C1. The torus criterion (Lemma T2: a pattern extends exactly when some admissible tilt leaves its weighted digraph without a negative
      cycle) agrees with brute force over all states, for every pattern on every set of at most 3 distinctions of every torus with
      12 to 18 distinctions, and on 100 random sets of 4 per torus; admissibility is tested exactly (the slope inequalities).
  C2. Margin facts: M is a multiple of 3 and at most 3/2 the edge-width, for every torus with 12 to 96 distinctions.
  C3. T4: every torus with 12 to 96 distinctions and M > 3 is read faithfully (12 to 48 read here; 49 to 96 from LONG-LOOP's census and
      stress test, by lattice).
  C4. T2 and T3 on every faithful torus with 12 to 48 distinctions (read here) and 49 to 96 (LONG-LOOP): at distance 2, a bond of 4
      exists whenever M >= 9 (T3); at distance 3, a bond of 4 exists only when M <= 6 (T2) and is absent with a bond of 5 present when
      M >= 12 (T3).
  C5. T1: every torus with M >= 0 has an NAE state (12 to 48 read here).
  C6. Mutation: the criterion with the tilt forced to 0 disagrees with brute force on some torus (so C1 can fail).
  Klein bottles with an edge glide (the glide's reflection permutes the forward steps):
  C7. The criterion with the glide terms agrees with brute force for every pattern on every set of at most 3 distinctions, and on 100
      random sets of 4, of every such Klein bottle with 12 to 20 distinctions (raw presentations); states exist exactly when M >= 0.
  C8. On every such Klein bottle with 12 to 48 distinctions up to isomorphism: M is the same on every presentation, a multiple of 3
      and at most 3/2 the edge-width; states exist exactly when M >= 0 (T1); M > 3 implies faithful (T4).
  C9. T2 and T3 at distances 2 and 3 from distinction 0 on those that are faithful (as C4).
  C10. Mutation: the criterion without the glide terms disagrees with brute force (so C7 can fail).
  C11. Lemma K0: on every raw one-sided world (Klein bottle) with 12 to 48 distinctions, the glide is an edge glide exactly when the
       pairs can be directed so that every knot is a directed cycle; every torus read (12 to 96) can be.
  C12. Mutation: the Klein criterion with the mod-4 condition on tau(As + s) dropped disagrees with brute force (so it is needed).

Margins are exact (every lattice vector that can reach the least value is enumerated; see Torus).

Usage: check.py [--write]   (the workspace .venv)
"""
from __future__ import annotations

import itertools
import json
import os
import random
import sys
from fractions import Fraction
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "KNOTS-ALONE-20261111-001A" / "KNOTS-ALONE-20261111-001A-E001_knots_alone_census"))
sys.path.insert(0, str(ROOT / "experiments" / "LONG-LOOP-20261111-001A" / "LONG-LOOP-20261111-001A-E001_long_loops"))
import knots_alone as ka  # noqa: E402
import flat_worlds as fw  # noqa: E402
import numpy as np  # noqa: E402


def D(d1, d2):
    return d1 + d2 + 3 * max(0, -d1, -d2)


def hexn(x, y):
    return max(abs(x), abs(y)) if x * y >= 0 else abs(x) + abs(y)


def even_class_ok(t, v):
    return t % 2 == 0 and (t - (v[0] + v[1])) % 3 == 0


def admissible(a, b, c, t1, t2):
    """Exact: the tilt's linear extension (alpha, beta) satisfies tau <= D on all of R^2, i.e. on the three rays where D is 1:
    alpha <= 1, beta <= 1, -alpha - beta <= 1 (D is linear on the three sectors between the forward steps)."""
    beta = Fraction(t2, c)
    alpha = (Fraction(t1) - b * beta) / a
    return alpha <= 1 and beta <= 1 and -alpha - beta <= 1


def lattice_ball(a, b, c, R):
    """Every vector (i, j, (x, y)) of the lattice spanned by (a, b) and (0, c) with hexagonal length at most R: x = i a, y = i b + j c."""
    out = []
    for i in range(-(R // a), R // a + 1):
        x = i * a
        for j in range(-((R + abs(i * b)) // c) - 1, (R + abs(i * b)) // c + 2):
            y = i * b + j * c
            if hexn(x, y) <= R:
                out.append((i, j, (x, y)))
    return out


class Torus:
    """Exact margin and criterion. D - tau is linear and nonnegative on each of the three cones between the forward steps, and the
    lattice holds (V, 0), (0, c) and (-V, -V) (V = a c), so subtracting the cone's ray vector never raises it: the least value over a
    coset is reached at hexagonal length at most V (+ the representatives' offset), and the least over nonzero lattice vectors too."""

    def __init__(self, a, b, c):
        self.L = fw.Lattice(a, b, c)
        self._dm = {}
        self.a, self.b, self.c = a, b, c
        V = a * c
        self.reps = [(x, y) for x in range(a) for y in range(c)]
        self.idx = {p: i for i, p in enumerate(self.reps)}
        self.ball = [v for v in lattice_ball(a, b, c, V) if v[:2] != (0, 0)]
        self.vecs = lattice_ball(a, b, c, V + a + c)
        self.w = min(hexn(*v) for i, j, v in self.ball)
        # admissible tilts, exactly (Lemma T0): the slope (alpha, beta) lies in the triangle alpha, beta <= 1 <= ... so both lie in
        # [-2, 1], t2 = c beta and t1 = a alpha + b beta
        self.tilts = []
        for t2 in range(-2 * c, c + 1):
            if not even_class_ok(t2, (0, c)):
                continue
            for t1 in range(-2 * a - 2 * abs(b), a + 2 * abs(b) + 1):
                if even_class_ok(t1, (a, b)) and admissible(a, b, c, t1, t2):
                    self.tilts.append((t1, t2))
        self.M = max((min(D(*v) - (i * t1 + j * t2) for i, j, v in self.ball) for t1, t2 in self.tilts), default=None)

    def dmin(self, t1, t2, p, q):
        """min over l in L of D(p, q + l) - tau(l), for representatives p, q (cached)."""
        key = (t1, t2, p, q)
        if key not in self._dm:
            self._dm[key] = min(D(q[0] + v[0] - p[0], q[1] + v[1] - p[1]) - (ii * t1 + jj * t2) for ii, jj, v in self.vecs)
        return self._dm[key]

    def residue(self, p, s):
        cc = (p[0] + p[1]) % 3
        return next(v for v in range(6) if v % 3 == cc and v % 2 == s)

    def extendable(self, S, spins, tilts=None):
        n = len(S)
        r = [self.residue(S[i], spins[i]) for i in range(n)]
        for t1, t2 in (self.tilts if tilts is None else tilts):
            w = [[(self.dmin(t1, t2, S[i], S[j]) - r[j] + r[i]) // 6 for j in range(n)] for i in range(n)]
            for k in range(n):
                for i in range(n):
                    for j in range(n):
                        if w[i][k] + w[k][j] < w[i][j]:
                            w[i][j] = w[i][k] + w[k][j]
            if all(w[i][i] >= 0 for i in range(n)):
                return True
        return False

    def knots(self):
        V, T, ew = fw.torus(self.L)
        return V, T


FORWARD = {(1, 0), (0, 1), (-1, -1)}
EDGE_REFLECTIONS = [M for M in fw.REFLECTIONS if {fw.apply(M, v) for v in FORWARD} == FORWARD]


class Klein(Torus):
    """Z^2/G, G = L u gL, g(x) = Mx + s with M one of the three reflections that permute the forward steps (an edge glide: its axis
    runs along lattice edges). Heights satisfy h(gamma x) = h(x) + tau(gamma) for a homomorphism tau: G -> Z; tau on L is a torus
    tilt with tau(M l) = tau(l), and tau(g) = tau(Ms + s) / 2 must be an even integer."""

    def __init__(self, a, b, c, M, s):
        super().__init__(a, b, c)
        self.Mg, self.s = M, s
        self.sites = sorted({min(p, self.sigma(p)) for p in self.reps})
        self.ktilts, self.ktilts_mut = [], []
        for t1, t2 in self.tilts:
            if self.tau(t1, t2, fw.apply(M, (a, b))) != t1 or self.tau(t1, t2, fw.apply(M, (0, c))) != t2:
                continue
            ms = fw.apply(M, s)
            two = self.tau(t1, t2, (ms[0] + s[0], ms[1] + s[1]))
            if two % 4 == 0:
                self.ktilts.append((t1, t2, two // 2))
            if two % 2 == 0:
                self.ktilts_mut.append((t1, t2, two // 2))  # mutation C12: the mod-4 condition dropped
        trans = {(t1, t2): min(D(*v) - (i * t1 + j * t2) for i, j, v in self.ball) for t1, t2, _ in self.ktilts}
        self.kM = max((min(trans[(t1, t2)], self.glide_margin(t1, t2, tg)) for t1, t2, tg in self.ktilts), default=None)
        self.kw = min([self.w] + [min(hexn(u0[0] + v[0], u0[1] + v[1]) for _, _, v in self.vecs)
                                  for u0 in {self.L.red(*self.disp(x)) for x in self.reps}])

    def sigma(self, p):
        q = fw.apply(self.Mg, p)
        return self.L.red(q[0] + self.s[0], q[1] + self.s[1])

    def disp(self, x):
        q = fw.apply(self.Mg, x)
        return (q[0] + self.s[0] - x[0], q[1] + self.s[1] - x[1])

    def tau(self, t1, t2, v):
        i = v[0] // self.a
        j = (v[1] - i * self.b) // self.c
        assert (i * self.a, i * self.b + j * self.c) == tuple(v)
        return i * t1 + j * t2

    def dmin_u(self, t1, t2, u):
        """min over l in L of D(u + l) - tau(l)."""
        u0 = self.L.red(*u)
        return self.dmin(t1, t2, (0, 0), u0) + self.tau(t1, t2, (u[0] - u0[0], u[1] - u0[1]))

    def glide_margin(self, t1, t2, tg):
        return min(self.dmin_u(t1, t2, self.disp(x)) - tg for x in self.reps)

    def kextendable(self, S, spins, glides=True, tilts=None):
        n = len(S)
        r = [self.residue(S[i], spins[i]) for i in range(n)]
        for t1, t2, tg in (self.ktilts if tilts is None else tilts):
            w = [[None] * n for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    m = self.dmin(t1, t2, S[i], S[j])
                    if glides:
                        q = fw.apply(self.Mg, S[j])
                        m = min(m, self.dmin_u(t1, t2, (q[0] + self.s[0] - S[i][0], q[1] + self.s[1] - S[i][1])) - tg)
                    w[i][j] = (m - r[j] + r[i]) // 6
            for k in range(n):
                for i in range(n):
                    for j in range(n):
                        if w[i][k] + w[k][j] < w[i][j]:
                            w[i][j] = w[i][k] + w[k][j]
            if all(w[i][i] >= 0 for i in range(n)):
                return True
        return False


def cyclic_direction(V, T):
    """Can every pair in a knot be directed so that each knot is a directed 3-cycle? (Propagates from one pair per component.)"""
    knots_of = {}
    for t in T:
        for a, b in itertools.combinations(t, 2):
            knots_of.setdefault(frozenset((a, b)), []).append(t)
    d = {}
    for start in knots_of:
        if start in d:
            continue
        d[start] = tuple(sorted(start))
        stack = [start]
        while stack:
            e = stack.pop()
            u, v = d[e]
            for t in knots_of[e]:
                w = next(x for x in t if x not in e)
                for p, q in ((v, w), (w, u)):
                    f = frozenset((p, q))
                    if f not in d:
                        d[f] = (p, q)
                        stack.append(f)
                    elif d[f] != (p, q):
                        return False
    return True


def c11_one_sided(V):
    """Every raw one-sided world with V distinctions: (edge glide, cyclically directed) counts."""
    out = {}
    for L in fw.sublattices(2 * V):
        for M in fw.REFLECTIONS:
            if not (L.contains(fw.apply(M, (L.a, L.b))) and L.contains(fw.apply(M, (0, L.c)))):
                continue
            for s in ((x, y) for x in range(L.a) for y in range(L.c)):
                g2 = fw.apply(M, s)
                if L.contains((g2[0] + s[0], g2[1] + s[1])):
                    r = fw.klein(L, M, s)
                    if r is not None and ka.is_surface(r[0], r[1]) and not ka.orientable(r[1]):
                        key = f"{M in EDGE_REFLECTIONS} {cyclic_direction(r[0], r[1])}"
                        out[key] = out.get(key, 0) + 1
    return out


def edge_glides(V):
    """Every edge-glide Klein bottle with V distinctions, raw (isomorphic copies included), as (a, b, c, M, s)."""
    out = []
    for L in fw.sublattices(2 * V):
        for M in EDGE_REFLECTIONS:
            if not (L.contains(fw.apply(M, (L.a, L.b))) and L.contains(fw.apply(M, (0, L.c)))):
                continue
            for s in ((x, y) for x in range(L.a) for y in range(L.c)):
                g2 = fw.apply(M, s)
                if L.contains((g2[0] + s[0], g2[1] + s[1])):
                    r = fw.klein(L, M, s)
                    if r is not None and ka.is_surface(r[0], r[1]) and not ka.orientable(r[1]):
                        out.append((L.a, L.b, L.c, M, s))
    return out


def c7_klein(item):
    a, b, c, M, s = item
    kl = Klein(a, b, c, M, s)
    V, T, ew = fw.klein(kl.L, M, s)
    assert V == len(kl.sites)
    st = brute_states(V, T)
    rng = random.Random(a * 1000 + b * 10 + c + 7 * s[0] + 3 * s[1])
    sets = [S for k in (1, 2, 3) for S in itertools.combinations(range(V), k)]
    sets += [tuple(sorted(rng.sample(range(V), 4))) for _ in range(100)]
    mism = total = mut = mut4 = 0
    for S in sets:
        pts = [kl.sites[i] for i in S]
        seen = {tuple(int((int(x) >> i) & 1) for i in S) for x in st}
        for p in itertools.product((0, 1), repeat=len(S)):
            total += 1
            if (p in seen) != kl.kextendable(pts, p):
                mism += 1
            if (p in seen) != kl.kextendable(pts, p, glides=False):
                mut += 1
            if (p in seen) != kl.kextendable(pts, p, tilts=kl.ktilts_mut):
                mut4 += 1
    return {"klein": [a, b, c, [list(r) for r in M], list(s)], "V": V, "M": kl.kM, "states": int(len(st)), "patterns": total,
            "mismatches": mism, "T1 ok": (kl.kM is not None) == (len(st) > 0), "mutation mismatches": mut,
            "mod-4 mutation mismatches": mut4}


def klein_class(V):
    """Edge-glide Klein bottles with V distinctions up to isomorphism, with M on every raw presentation."""
    classes = {}
    for item in edge_glides(V):
        a, b, c, M, s = item
        r = fw.klein(fw.Lattice(a, b, c), M, s)
        code = min(ka.canon_codes_surface(r[1]))
        kl = Klein(a, b, c, M, s)
        e = classes.setdefault(code, {"item": item, "T": r[1], "Ms": set(), "ws": set()})
        e["Ms"].add(kl.kM)
        e["ws"].add(kl.kw)
    return [{"V": V, "item": e["item"], "T": e["T"], "Ms": sorted(e["Ms"], key=lambda m: -1 if m is None else m),
             "ws": sorted(e["ws"])} for e in classes.values()]


def klein_reading(cl):
    V, T = cl["V"], [tuple(t) for t in cl["T"]]
    res = ka.read_law_sat(V, T, ka.LAWS["NAE"])
    out = {"klein": [cl["item"][0], cl["item"][1], cl["item"][2], [list(r) for r in cl["item"][3]], list(cl["item"][4])], "V": V,
           "M": cl["Ms"][0], "M invariant": len(cl["Ms"]) == 1, "w": cl["ws"][0], "allowed": res["allowed"],
           "faithful": bool(res.get("faithful"))}
    if res.get("faithful"):
        import census
        out["ruler"] = census.ruler(V, T, 20261117 + V)
    return out


def brute_states(V, T):
    x = np.arange(1 << V, dtype=np.int64)
    ok = np.ones(len(x), dtype=bool)
    for a, b, c in T:
        s = ((x >> a) & 1) + ((x >> b) & 1) + ((x >> c) & 1)
        ok &= (s == 1) | (s == 2)
    return x[ok]


def c1_torus(abc):
    a, b, c = abc
    tor = Torus(a, b, c)
    r = fw.torus(tor.L)
    if r is None:
        return None
    V, T, ew = r
    # fw.torus numbers coset (x, y) as x * c + y, the same order as tor.reps
    st = brute_states(V, T)
    have = set()
    mism = total = 0
    rng = random.Random(a * 1000 + b * 10 + c)
    sets = [S for k in (1, 2, 3) for S in itertools.combinations(range(V), k)]
    sets += [tuple(sorted(rng.sample(range(V), 4))) for _ in range(100)]
    for S in sets:
        pts = [tor.reps[i] for i in S]
        seen = {tuple(int((int(s) >> i) & 1) for i in S) for s in st}
        for p in itertools.product((0, 1), repeat=len(S)):
            total += 1
            if (p in seen) != tor.extendable(pts, p):
                mism += 1
    mut = 0
    for S in itertools.combinations(range(V), 2):
        pts = [tor.reps[i] for i in S]
        seen = {tuple(int((int(s) >> i) & 1) for i in S) for s in st}
        for p in itertools.product((0, 1), repeat=2):
            if (p in seen) != tor.extendable(pts, p, tilts=[(0, 0)] if (0, 0) in tor.tilts else []):
                mut += 1
    return {"torus": [a, b, c], "V": V, "M": tor.M, "patterns": total, "mismatches": mism, "mutation mismatches": mut, "states": int(len(st))}


def reading(abc):
    a, b, c = abc
    tor = Torus(a, b, c)
    r = fw.torus(tor.L)
    if r is None:
        return None
    V, T, ew = r
    if not ka.is_surface(V, T):
        return None
    res = ka.read_law_sat(V, T, ka.LAWS["NAE"])
    out = {"torus": [a, b, c], "V": V, "w": tor.w, "M": tor.M, "allowed": res["allowed"], "faithful": bool(res.get("faithful"))}
    if res.get("faithful"):
        import census  # LONG-LOOP's frozen code (its ruler and oracle)
        out["ruler"] = census.ruler(V, T, 20261116 + a * 997 + b * 31 + c)
    return out


def bond_checks(records, key):
    """T2 and T3 at distances 2 and 3 on LONG-LOOP's ruler rows (bond distance from distinction 0)."""
    bad = []
    counted = {"d2 with M>=9": 0, "d3 with M<=6 and a 4-bond": 0, "d3 with M>=12": 0}
    for r in records:
        if not r.get("ruler"):
            continue
        M = r["M"]
        for row in r["ruler"]:
            if row["delta"] == 2 and M is not None and M >= 9:
                counted["d2 with M>=9"] += 1
                if not row["bond4_local"]:
                    bad.append([r[key], row])
            if row["delta"] == 3:
                if row["bond4_global"]:
                    if M is not None and M > 6:
                        bad.append([r[key], row])
                    else:
                        counted["d3 with M<=6 and a 4-bond"] += 1
                if M is not None and M >= 12:
                    counted["d3 with M>=12"] += 1
                    if row["bond4_global"] or not row["bond5_local"]:
                        bad.append([r[key], row])
    return {"failures": bad[:10], "counted": counted, "pass": not bad}


def main():
    out = {}
    small = [(L.a, L.b, L.c) for V in range(12, 19) for L in fw.sublattices(V)]
    with Pool(12) as pool:
        c1 = [r for r in pool.map(c1_torus, small, chunksize=1) if r]
    out["C1"] = {"tori": len(c1), "patterns": sum(r["patterns"] for r in c1), "mismatches": sum(r["mismatches"] for r in c1),
                 "pass": sum(r["mismatches"] for r in c1) == 0}
    out["C6"] = {"mutation mismatches": sum(r["mutation mismatches"] for r in c1), "pass": sum(r["mutation mismatches"] for r in c1) > 0}
    mid = [(L.a, L.b, L.c) for V in range(12, 49) for L in fw.sublattices(V)]
    with Pool(12) as pool:
        reads = [r for r in pool.map(reading, mid, chunksize=1) if r]
    # LONG-LOOP's census and stress test, 49 to 96, by lattice
    ll = []
    for path in ("artifacts/LONG-LOOP-20261111-001A/LONG-LOOP-20261111-001A-E001_long_loops/census.json",
                 "research/LONG-LOOP-20261111-001/stress/census.json"):
        for r in json.load(open(ROOT / path))["results"]:
            if r["kind"] == "torus":
                tor = Torus(*r["lattice"])
                ll.append({"torus": r["lattice"], "V": r["V"], "w": tor.w, "M": tor.M, "allowed": r["NAE"]["allowed"],
                           "faithful": bool(r["NAE"].get("faithful")), "ruler": r.get("ruler")})
    allr = reads + ll
    out["C2"] = {"tori": len(allr), "pass": all(r["M"] is None or (r["M"] % 3 == 0 and 2 * r["M"] <= 3 * r["w"]) for r in allr)}
    t4 = [r for r in allr if r["M"] is not None and r["M"] > 3 and not r["faithful"]]
    out["C3"] = {"tori with M > 3": sum(1 for r in allr if r["M"] is not None and r["M"] > 3), "failures": [r["torus"] for r in t4],
                 "pass": not t4}
    out["C4"] = bond_checks(allr, "torus")
    out["C5"] = {"pass": all(r["allowed"] for r in reads if r["M"] is not None and r["M"] >= 0),
                 "tori with no state": [[r["torus"], r["M"]] for r in reads if not r["allowed"]]}
    out["M by edge-width"] = sorted({(r["w"], r["M"]) for r in allr}, key=lambda t: (t[0], -1 if t[1] is None else t[1]))
    # Klein bottles with an edge glide
    smallk = [it for V in range(12, 21) for it in edge_glides(V)]
    with Pool(12) as pool:
        c7 = pool.map(c7_klein, smallk, chunksize=1)
    out["C7"] = {"bottles": len(c7), "patterns": sum(r["patterns"] for r in c7), "mismatches": sum(r["mismatches"] for r in c7),
                 "T1 both ways": all(r["T1 ok"] for r in c7),
                 "pass": sum(r["mismatches"] for r in c7) == 0 and all(r["T1 ok"] for r in c7)}
    out["C10"] = {"mutation mismatches": sum(r["mutation mismatches"] for r in c7), "pass": sum(r["mutation mismatches"] for r in c7) > 0}
    out["C12"] = {"mutation mismatches": sum(r["mod-4 mutation mismatches"] for r in c7),
                  "pass": sum(r["mod-4 mutation mismatches"] for r in c7) > 0}
    with Pool(12) as pool:
        classes = [cl for cls in pool.map(klein_class, range(12, 49), chunksize=1) for cl in cls]
        kreads = pool.map(klein_reading, classes, chunksize=1)
    out["C8"] = {"classes": len(kreads), "M invariant": all(r["M invariant"] for r in kreads),
                 "margin facts": all(r["M"] is None or (r["M"] % 3 == 0 and 2 * r["M"] <= 3 * r["w"]) for r in kreads),
                 "T1": all(r["allowed"] == (r["M"] is not None) for r in kreads),
                 "with M > 3": sum(1 for r in kreads if r["M"] is not None and r["M"] > 3),
                 "T4 failures": [r["klein"] for r in kreads if r["M"] is not None and r["M"] > 3 and not r["faithful"]]}
    out["C8"]["pass"] = out["C8"]["M invariant"] and out["C8"]["margin facts"] and out["C8"]["T1"] and not out["C8"]["T4 failures"]
    out["C9"] = bond_checks(kreads, "klein")
    with Pool(12) as pool:
        parts = pool.map(c11_one_sided, range(12, 49), chunksize=1)
    c11 = {}
    for part in parts:
        for k, v in part.items():
            c11[k] = c11.get(k, 0) + v
    tor_dir = [cyclic_direction(*fw.torus(fw.Lattice(*r["torus"]))[:2]) for r in allr]
    out["C11"] = {"one-sided (edge glide, cyclically directed)": c11, "tori cyclically directed": sum(tor_dir), "tori": len(tor_dir),
                  "pass": set(c11) <= {"True True", "False False"} and all(tor_dir)}
    out["Klein M by edge-width"] = sorted({(r["w"], r["M"]) for r in kreads}, key=lambda t: (t[0], -1 if t[1] is None else t[1]))
    out["failures"] = [k for k in ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11", "C12") if not out[k]["pass"]]
    print(json.dumps(out, indent=1, default=str))
    if "--write" in sys.argv:
        manifest = json.loads((HERE / "manifest.json").read_text())
        result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
                  "proof": manifest["proof"], "status": "passed" if not out["failures"] else "failed", "claim": manifest["claim"], **out}
        (HERE / "result.json").write_text(json.dumps(result, indent=1, default=str) + "\n")
    return 0 if not out["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
