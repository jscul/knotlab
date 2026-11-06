#!/usr/bin/env python3
"""Check for HARD-3D-20261025-001A-P001 (with boundary, counting maps into S3 is #P-hard). Standard library only.

The fin handlebody X_G of a connected plane multigraph G has pi1 = < a_u (u in V), t_e (e in E) | [t_e, a_u a_v^-1] >.
Parts:
1. the homomorphism count of that presentation, by brute force over all images of the generators, equals the centralizer formula
   sum_y prod_e |C(y_u y_v^-1)| (S3 and the dihedral group of order 8, small graphs);
2. interpolation: with every edge repeated k times, Z_k = sum_y prod_e |C(y_u y_v^-1)|^k; solving the exponential-polynomial system
   for k = 1..K recovers the configuration counts by edge type, and the all-rotation count equals 2 P(G,3) (S3) on planar
   (multi)graphs; for the dihedral group of order 8 the no-central-edge count equals 2^|V| P(G,4);
3. the interpolation nodes are pairwise distinct (so the linear system is invertible);
4. controls: an abelian group gives counts that do not see colourings (two graphs with equal |V|, |E| and different P(G,3) have equal
   counts for every k); the wrong targets P(G,3) and 2 P(G,4) are rejected for S3; a collision of nodes is detected when the
   centralizer sizes are replaced by values with a multiplicative coincidence.
"""
from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent


def perm_group(gens, n):
    idn = tuple(range(n))
    els, frontier = {idn}, [idn]
    while frontier:
        new = []
        for p in frontier:
            for g in gens:
                q = tuple(p[g[i]] for i in range(n))
                if q not in els:
                    els.add(q)
                    new.append(q)
        frontier = new
    return sorted(els)


class Group:
    def __init__(self, els):
        self.els = els
        self.n = len(els[0])
        self.e = tuple(range(self.n))
        self.cent = {g: [h for h in els if self.mul(g, h) == self.mul(h, g)] for g in els}

    def mul(self, p, q):
        return tuple(p[q[i]] for i in range(self.n))

    def inv(self, p):
        r = [0] * self.n
        for i in range(self.n):
            r[p[i]] = i
        return tuple(r)


S3 = Group(perm_group([(1, 0, 2), (1, 2, 0)], 3))
D8 = Group(perm_group([(1, 2, 3, 0), (3, 2, 1, 0)], 4))          # dihedral group of order 8
Z6 = Group(perm_group([(1, 2, 3, 4, 5, 0)], 6))                    # cyclic group of order 6 (control)


def brute_count(G, n, edges):
    """|Hom(<a_u, t_e | [t_e, a_u a_v^-1]>, G)| by enumerating all images of all generators"""
    tot = 0
    for y in itertools.product(G.els, repeat=n):
        for t in itertools.product(G.els, repeat=len(edges)):
            ok = True
            for (u, v), te in zip(edges, t):
                g = G.mul(y[u], G.inv(y[v]))
                if G.mul(te, g) != G.mul(g, te):
                    ok = False
                    break
            tot += ok
    return tot


def formula(G, n, edges, k=1):
    tot = 0
    for y in itertools.product(G.els, repeat=n):
        w = 1
        for u, v in edges:
            w *= len(G.cent[G.mul(y[u], G.inv(y[v]))]) ** k
        tot += w
    return tot


def colourings(n, edges, q):
    return sum(1 for c in itertools.product(range(q), repeat=n) if all(c[u] != c[v] for u, v in edges))


def solve(rows, rhs):
    K = len(rows)
    A = [list(r) + [b] for r, b in zip(rows, rhs)]
    for i in range(K):
        piv = next(j for j in range(i, K) if A[j][i] != 0)
        A[i], A[piv] = A[piv], A[i]
        for j in range(K):
            if j != i and A[j][i] != 0:
                f = A[j][i] / A[i][i]
                A[j] = [x - f * y for x, y in zip(A[j], A[i])]
    return [A[i][K] / A[i][i] for i in range(K)]


def interpolate(G, n, edges, values):
    """values: sorted distinct centralizer sizes; returns {profile: count} from Z_1..Z_K"""
    m = len(edges)
    r = len(values)
    profiles = [p for p in itertools.product(range(m + 1), repeat=r) if sum(p) == m]
    nodes = [Fraction(1) for _ in profiles]
    for i, p in enumerate(profiles):
        for c, k in zip(values, p):
            nodes[i] *= c ** k
    distinct = len(set(nodes)) == len(nodes)
    K = len(profiles)
    rows = [[x ** k for x in nodes] for k in range(1, K + 1)]
    rhs = [Fraction(formula(G, n, edges, k)) for k in range(1, K + 1)]
    sol = solve(rows, rhs)
    # one more value as an independent consistency test
    extra = sum(s * x ** (K + 1) for s, x in zip(sol, nodes)) == formula(G, n, edges, K + 1)
    return dict(zip(profiles, sol)), distinct, extra


GRAPHS = {
    "triangle": (3, [(0, 1), (1, 2), (2, 0)]),
    "square": (4, [(0, 1), (1, 2), (2, 3), (3, 0)]),
    "K4": (4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]),
    "diamond": (4, [(0, 1), (1, 2), (2, 0), (1, 3), (3, 2)]),
    "wheel W4": (5, [(0, 1), (1, 2), (2, 3), (3, 0), (4, 0), (4, 1), (4, 2), (4, 3)]),
    "triangle with a doubled edge": (3, [(0, 1), (0, 1), (1, 2), (2, 0)]),
    "path P4": (4, [(0, 1), (1, 2), (2, 3)]),
}


def main() -> int:
    out = {}
    # part 1: brute force against the formula
    p1 = {}
    for name in ("triangle", "triangle with a doubled edge", "path P4"):
        n, edges = GRAPHS[name]
        if len(edges) + n > 7:
            continue
        p1[name] = {"S3 brute": brute_count(S3, n, edges), "S3 formula": formula(S3, n, edges)}
    n, edges = GRAPHS["triangle"]
    p1["triangle, order-8 dihedral"] = {"brute": brute_count(D8, n, edges), "formula": formula(D8, n, edges)}
    part1_ok = all(len(set(v.values())) == 1 for v in p1.values())
    out["part1_brute_force_vs_formula"] = {"cases": p1, "all equal": part1_ok}

    # part 2: interpolation for S3 (values 2, 3, 6) and the order-8 dihedral group (values 4, 8)
    p2 = {}
    part2_ok = True
    for name, (n, edges) in GRAPHS.items():
        prof, distinct, extra = interpolate(S3, n, edges, [2, 3, 6])
        m = len(edges)
        rot = prof[(0, m, 0)]
        want = 2 * colourings(n, edges, 3)
        row = {"edges": m, "all-rotation count": str(rot), "2 P(G,3)": want, "nodes distinct": distinct,
               "extra value reproduced": extra, "match": rot == want}
        if name in ("triangle", "square", "diamond", "path P4"):
            profd, distinct_d, extra_d = interpolate(D8, n, edges, [4, 8])
            noncentral = profd[(m, 0)]
            wantd = 2 ** n * colourings(n, edges, 4)
            row.update({"order-8 dihedral: no-central-edge count": str(noncentral), "2^|V| P(G,4)": wantd,
                        "order-8 dihedral match": noncentral == wantd and distinct_d and extra_d})
            part2_ok &= row["order-8 dihedral match"]
        part2_ok &= row["match"] and distinct and extra
        p2[name] = row
    out["part2_interpolation"] = {"cases": p2, "all match": part2_ok}

    # part 4: controls
    c = {}
    # abelian group: counts depend only on |V| and |E| (all centralizers are the whole group)
    a, b = GRAPHS["square"], (4, [(0, 1), (1, 2), (2, 0), (2, 3)])          # square vs a triangle with a pendant edge
    c["abelian Z6 does not see colourings"] = (all(formula(Z6, a[0], a[1], k) == formula(Z6, b[0], b[1], k) for k in (1, 2, 3))
                                               and colourings(*a, 3) != colourings(*b, 3))
    n, edges = GRAPHS["square"]
    prof, _, _ = interpolate(S3, n, edges, [2, 3, 6])
    c["wrong target P(G,3) rejected"] = prof[(0, len(edges), 0)] != colourings(n, edges, 3)
    c["wrong target 2 P(G,4) rejected"] = prof[(0, len(edges), 0)] != 2 * colourings(n, edges, 4)
    # node collision detector: values 2, 4, 8 have 4*4 = 2*8, so profiles collide
    m = 3
    profiles = [p for p in itertools.product(range(m + 1), repeat=3) if sum(p) == m]
    nodes = [2 ** p[0] * 4 ** p[1] * 8 ** p[2] for p in profiles]
    c["collision of nodes detected for values 2, 4, 8"] = len(set(nodes)) < len(nodes)
    controls_ok = all(c.values())
    out["controls"] = {"results": c, "all pass": controls_ok}

    ok = part1_ok and part2_ok and controls_ok
    out["all_checks_pass"] = ok
    result = {"schema_version": 1, "artifact_id": "HARD-3D-20261025-001A-P001", "status": "Proved" if ok else "Partial", "checks": out}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(out, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
