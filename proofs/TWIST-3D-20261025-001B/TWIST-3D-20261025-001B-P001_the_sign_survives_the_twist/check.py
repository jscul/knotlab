#!/usr/bin/env python3
"""Check of TWIST-3D-20261025-001B-P001 (standard library only, seed 20261025).

Turaev-Viro form on ordered triangulations: weights d[x] on edge labels, t[y] on ordered triangle labellings y = (x_ab, x_bc, x_ac)
in the triangle rule R, W[s][z] on R-compatible labellings z of an ordered tetrahedron with orientation sign s, and v on vertices.
2-3 move (apex pair {p, q}, global orientation eps): t(shared face) W(F_p) W(F_q) = sum over x_pq of d[x_pq] t t t W W W; 1-4 move (new
vertex r, eps): W(F_r) = v * sum over the four new edges of their d's, the six new triangles' t's and the four new tetrahedra's W's;
signs of facets as in ticket A. For each of the eight non-windable knots (the knots excluding three tuples) the check confirms:
- (full support) some identity has monomials on one side only when every weight is positive;
- (supports) exhaustive enumeration of the supports for which every identity has a fully supported monomial on one side exactly when
  it has one on the other, with v and some tetrahedron weight positive: the tetrahedron part of every such support consists of constant
  labellings, of the parity class contained in R, or (for the no-lone knots) of the union of the even class with the all-ones or all-zero
  labelling;
- (parity class) restricted to the parity class, each 2-3 identity is one monomial on each side; in logarithms these form a homogeneous
  linear system whose solution space equals the span of the gauge directions (per triangle labelling of the class, an antisymmetric face
  gauge entering each tetrahedron with the sign of its face and a symmetric one rescaling the triangle weight against the square root
  in its two tetrahedra; and the global direction W * a, d / a); so every positive weighting there is a
  gauge transform of the constant weighting d = t = W = 1, v = 1/2, whose state sum is |Z^1| / 2^V = |H^1(M; Z2)| / 2.
Controls: the odd parity knot itself has no one-sided identity under full support; changing one tetrahedron weight alone violates the
2-3 system; the constant weighting evaluated on sampled ordered triangulations gives |H^1(M; Z2)| / 2 exactly.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import random
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_spec = importlib.util.spec_from_file_location(
    "census", ROOT / "proofs/TWIST-3D-20261025-001A/TWIST-3D-20261025-001A-P001_twists_add_nothing_to_counting/check.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)
CUBE, E5, EDGES4 = A.CUBE, A.E5, A.EDGES4


def tri_lab(x, t):
    a, b, c = sorted(t)
    return (x[(a, b)], x[(b, c)], x[(a, c)])


def tv_identities(R):
    comp = set(A.compatible(R))
    eqs = []
    for eps in (1, -1):
        for p, q in itertools.combinations(range(5), 2):
            others = [v for v in range(5) if v not in (p, q)]
            bnd_edges = [e for e in E5 if e != (p, q)]
            bnd_tris = [t for t in itertools.combinations(range(5), 3) if not ({p, q} <= set(t)) and set(t) != set(others)]
            itris = [t for t in itertools.combinations(range(5), 3) if {p, q} <= set(t)]
            for lab in itertools.product((0, 1), repeat=9):
                x = dict(zip(bnd_edges, lab))
                if not all(tri_lab(x, t) in R for t in bnd_tris):
                    continue
                lhs = []
                if tri_lab(x, tuple(others)) in R and all(A.tet_lab(x, A.facet(i)) in comp for i in (p, q)):
                    lhs.append((("t", tri_lab(x, tuple(others))),) +
                               tuple(("W", -eps * (-1) ** i, A.tet_lab(x, A.facet(i))) for i in (p, q)))
                rhs = []
                for e in (0, 1):
                    y = dict(x)
                    y[(p, q)] = e
                    if all(tri_lab(y, t) in R for t in itris) and all(A.tet_lab(y, A.facet(r)) in comp for r in others):
                        rhs.append((("d", e),) + tuple(("t", tri_lab(y, t)) for t in itris) +
                                   tuple(("W", eps * (-1) ** r, A.tet_lab(y, A.facet(r))) for r in others))
                eqs.append(("23", lhs, rhs))
        for r in range(5):
            F = A.facet(r)
            bnd_edges = [e for e in E5 if r not in e]
            new_edges = [e for e in E5 if r in e]
            itris = [t for t in itertools.combinations(range(5), 3) if r in t]
            for lab in itertools.product((0, 1), repeat=6):
                x = dict(zip(bnd_edges, lab))
                if not all(tri_lab(x, t) in R for t in itertools.combinations(F, 3)):
                    continue
                lhs = [(("W", -eps * (-1) ** r, A.tet_lab(x, F)),)] if A.tet_lab(x, F) in comp else []
                rhs = []
                for nl in itertools.product((0, 1), repeat=4):
                    y = dict(x)
                    y.update(zip(new_edges, nl))
                    if all(tri_lab(y, t) in R for t in itris) and all(A.tet_lab(y, A.facet(s)) in comp for s in range(5) if s != r):
                        rhs.append((("v",),) + tuple(("d", y[e]) for e in new_edges) + tuple(("t", tri_lab(y, t)) for t in itris) +
                                   tuple(("W", eps * (-1) ** s, A.tet_lab(y, A.facet(s))) for s in range(5) if s != r))
                eqs.append(("14", lhs, rhs))
    keys = sorted({k for _, l, r in eqs for m in l + r for k in m}, key=str)
    return eqs, keys


def consistent_supports(eqs, keys):
    """all supports (sets of positive keys) with v and some W positive, such that every identity has a fully supported monomial on one
    side exactly when it has one on the other; exhaustive search with checking of decided identities"""
    idx = {k: i for i, k in enumerate(keys)}
    cons = [([sum(1 << idx[k] for k in set(m)) for m in l], [sum(1 << idx[k] for k in set(m)) for m in r]) for _, l, r in eqs]
    n = len(keys)
    var_cons = [[] for _ in range(n)]
    for ci, (l, r) in enumerate(cons):
        allm = 0
        for m in l + r:
            allm |= m
        for i in range(n):
            if allm >> i & 1:
                var_cons[i].append(ci)
    order = sorted(range(n), key=lambda i: -len(var_cons[i]))

    def status(ms, on, off):
        """1 if some monomial is fully on, 0 if every monomial has an off key, None otherwise"""
        undecided = False
        for m in ms:
            if m & off:
                continue
            if m & ~on == 0:
                return 1
            undecided = True
        return None if undecided else 0

    def ok(on, off):
        for l, r in cons:
            a, b = status(l, on, off), status(r, on, off)
            if a is not None and b is not None and a != b:
                return False
        return True
    vbit = 1 << idx[("v",)]
    wmask = sum(1 << idx[k] for k in keys if k[0] == "W")
    sols = []
    stack = [(vbit, 0, 0)]
    while stack:
        on, off, depth = stack.pop()
        if not ok(on, off):
            continue
        while depth < n and ((on | off) >> order[depth] & 1):
            depth += 1
        if depth == n:
            if on & wmask:
                sols.append(frozenset(keys[i] for i in range(n) if on >> i & 1))
            continue
        i = order[depth]
        stack.append((on, off | (1 << i), depth + 1))
        stack.append((on | (1 << i), off, depth + 1))
    return sols


def parities(z):
    x = dict(zip(EDGES4, z))
    return tuple((x[(a, b)] + x[(b, c)] + x[(a, c)]) % 2 for a, b, c in itertools.combinations(range(4), 3))


def rank_and_nullspace_dim(rows, ncols):
    M = [[Fraction(v) for v in row] for row in rows]
    rank, col = 0, 0
    for col in range(ncols):
        piv = next((i for i in range(rank, len(M)) if M[i][col] != 0), None)
        if piv is None:
            continue
        M[rank], M[piv] = M[piv], M[rank]
        pv = M[rank][col]
        M[rank] = [v / pv for v in M[rank]]
        for i in range(len(M)):
            if i != rank and M[i][col] != 0:
                f = M[i][col]
                M[i] = [a - f * b for a, b in zip(M[i], M[rank])]
        rank += 1
    return rank, ncols - rank


def parity_gauge(R, eqs):
    """on the parity class of R: is the solution space of the log-linear 2-3 system equal to the span of gauge directions?"""
    even = {t for t in CUBE if sum(t) % 2 == 0}
    odd = {t for t in CUBE if sum(t) % 2 == 1}
    P = even if even <= R else odd
    par = (0, 0, 0, 0) if P == even else (1, 1, 1, 1)
    in_sector = lambda k: (k[0] == "d") or (k[0] == "t" and k[1] in P) or (k[0] == "W" and parities(k[2]) == par) or k[0] == "v"
    rows, keys = [], set()
    two_sided = 0
    for kind, l, r in eqs:
        if kind != "23":
            continue
        l2 = [m for m in l if all(in_sector(k) for k in m)]
        r2 = [m for m in r if all(in_sector(k) for k in m)]
        if not l2 and not r2:
            continue
        if len(l2) != 1 or len(r2) != 1:
            return {"single monomial on each side": False}
        two_sided += 1
        rows.append((l2[0], r2[0]))
        keys |= set(l2[0]) | set(r2[0])
    keys = sorted(keys, key=str)
    col = {k: i for i, k in enumerate(keys)}
    def vec(m1, m2):
        v = [0] * len(keys)
        for k in m1:
            v[col[k]] += 1
        for k in m2:
            v[col[k]] -= 1
        return v
    system = [vec(a, b) for a, b in rows]
    rank_sys, null_dim = rank_and_nullspace_dim(system, len(keys))
    gauges = []
    for y in sorted(P):
        g = [0] * len(keys)
        for k in keys:
            if k[0] == "W":
                s, z = k[1], k[2]
                x = dict(zip(EDGES4, z))
                for i in range(4):
                    a, b, c = [v for v in range(4) if v != i]
                    if (x[(a, b)], x[(b, c)], x[(a, c)]) == y:
                        g[col[k]] += s * (-1) ** i
        gauges.append(g)
    for y in sorted(P):
        # symmetric triangle gauge: t_y times beta, every tetrahedron times beta^(-1/2) per face of type y (scaled by 2)
        g = [0] * len(keys)
        if ("t", y) in col:
            g[col[("t", y)]] = 2
        for k in keys:
            if k[0] == "W":
                x = dict(zip(EDGES4, k[2]))
                for i in range(4):
                    a, b, c = [v for v in range(4) if v != i]
                    if (x[(a, b)], x[(b, c)], x[(a, c)]) == y:
                        g[col[k]] -= 1
        gauges.append(g)
    glob = [0] * len(keys)
    for k in keys:
        if k[0] == "W":
            glob[col[k]] = 1
        if k[0] == "d":
            glob[col[k]] = -1
    gauges.append(glob)
    in_null = all(all(sum(r_[i] * g[i] for i in range(len(keys))) == 0 for r_ in system) for g in gauges)
    rank_g, _ = rank_and_nullspace_dim(gauges, len(keys))
    # control: a single tetrahedron weight changed alone is not a solution direction
    single = [0] * len(keys)
    single[next(i for i, k in enumerate(keys) if k[0] == "W")] = 1
    single_breaks = any(sum(r_[i] * single[i] for i in range(len(keys))) != 0 for r_ in system)
    return {"parity class": "even" if P == even else "odd", "single monomial on each side": True, "two-sided 2-3 identities": two_sided,
            "unknowns": len(keys), "solution space dimension": null_dim, "gauge directions are solutions": in_null,
            "gauge rank": rank_g, "solutions are exactly the gauge span": in_null and rank_g == null_dim,
            "single change breaks the system": single_breaks}


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    knots = [R for R in (frozenset(CUBE[i] for i in range(8) if m >> i & 1) for m in range(256))
             if len(R) == 5 and all(len({(t[i], t[j]) for t in R}) == 4 for i, j in ((0, 1), (0, 2), (1, 2)))]
    out, ok = {}, len(knots) == 8
    ZERO, ONE = (0,) * 6, (1,) * 6
    for R in knots:
        label = ",".join("".join(map(str, t)) for t in CUBE if t not in R)
        eqs, keys = tv_identities(R)
        one_sided = sum(1 for _, l, r in eqs if bool(l) != bool(r))
        sups = consistent_supports(eqs, keys)
        even = {t for t in CUBE if sum(t) % 2 == 0}
        P = even if even <= R else {t for t in CUBE if sum(t) % 2 == 1}
        par = (0, 0, 0, 0) if P == even else (1, 1, 1, 1)
        families = set()
        bad = 0
        sector_W = {(sg, z) for sg in (1, -1) for z in A.LABS if parities(z) == par}
        sector_full = True
        for s in sups:
            W = {(k[1], k[2]) for k in s if k[0] == "W"}
            labs = {z for _, z in W}
            if labs <= {ZERO, ONE}:
                families.add("constant")
            elif all(parities(z) == par for z in labs):
                families.add("parity class")
                sector_full &= W == sector_W and {("d", 0), ("d", 1)} <= s and all(("t", y) in s for y in P)
            elif {z for z in labs if parities(z) != par} <= {ZERO, ONE} and any(parities(z) == par for z in labs):
                families.add("parity class with a constant")
            else:
                bad += 1
        gauge = parity_gauge(R, eqs)
        no_lone = R in (frozenset(t for t in CUBE if sum(t) != 1), frozenset(t for t in CUBE if sum(t) != 2))
        out[label] = {"identities": len(eqs), "one-sided under full support": one_sided, "consistent supports": len(sups),
                      "families": sorted(families), "supports outside the families": bad,
                      "parity supports cover the whole sector": sector_full, "parity class": gauge}
        ok &= one_sided > 0 and bad == 0 and sector_full and gauge["solutions are exactly the gauge span"]
        ok &= gauge["single change breaks the system"] and gauge["unknowns"] == 22
        ok &= ("parity class with a constant" in families) == no_lone

    # controls
    oddR = frozenset(t for t in CUBE if sum(t) % 2 == 1)
    eqs_odd, _ = tv_identities(oddR)
    odd_two_sided = all(bool(l) == bool(r) for _, l, r in eqs_odd)
    rng = random.Random(20261025)
    samples, per = [], {}
    while len(samples) < 24:
        T = rng.randint(1, 4)
        faces = [(t, i) for t in range(T) for i in range(4)]
        rng.shuffle(faces)
        pairing = [(faces[k], faces[k + 1]) for k in range(0, 4 * T, 2)]
        if not A.is_manifold(T, pairing):
            continue
        free, tors, V, E = A.homology(T, pairing)
        if E > 11:
            continue
        key = (free, tuple(tors))
        if per.get(key, 0) >= 4:
            continue
        per[key] = per.get(key, 0) + 1
        samples.append((T, pairing, free, tors, V, E))
    const_ok = True
    for T, pairing, free, tors, V, E in samples:
        h1 = 2 ** (free + sum(1 for d in tors if d % 2 == 0))
        z = A.count(T, pairing, A.ZODD)                # constant weighting: each odd cocycle has weight 1, times v^V with v = 1/2
        const_ok &= Fraction(z, 2 ** V) == Fraction(h1, 2)
    controls = {"the odd parity knot has no one-sided identity under full support": odd_two_sided,
                "changing one tetrahedron weight alone breaks the 2-3 system (every knot)": all(v["parity class"]["single change breaks the system"] for v in out.values()),
                "the constant weighting gives |H1(M; Z2)|/2 on sampled triangulations": const_ok and len(samples) == 24}
    ok &= all(controls.values())
    result["checks"] = {"the eight non-windable knots": out}
    result["controls"] = controls
    result["status"] = "passed" if ok else "failed"
    result["failures"] = [] if ok else ["a check or control did not come out as stated in proof.md"]
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    else:
        old = (HERE / "result.json").read_text() if (HERE / "result.json").exists() else None
        print("result.json matches" if old == text else "result.json differs from a fresh run")
        ok = ok and old == text
    print(json.dumps({"status": result["status"], "checks": result["checks"], "controls": controls}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
