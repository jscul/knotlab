#!/usr/bin/env python3
"""Check for HARD-3D-20261025-001B-P001 (closed manifolds: the doubles count pairs of colourings). Standard library only.

The double M_G of the fin handlebody of a connected plane multigraph G (outer face f0) has
  pi1 = < a_u, abar_u, s_f (bounded faces f), tau_e, kappa_e |
          abar_u = a_u (u a corner of f0);  a_u1^-1 a_ui = s_f abar_u1^-1 abar_ui s_f^-1 (corners u1, ui of a bounded face f);
          [tau_e, lam_e] = [kappa_e, lam_e] = 1,  [tau_e, kappa_e] = s_f'(e) s_f(e)^-1  (lam_e = a_v^-1 a_u, faces f, f' beside e) >
so |Hom(pi1, H)| = sum over (y, sigma, ybar) satisfying the face relations of prod_e W(lam_e, mu_e), with
W(lam, c) = #{(tau, kappa) in C(lam)^2 : [tau, kappa] = c}. With every edge repeated k times, digons collapse to W_lam^{*k}.
Parts:
1. identified manifolds: the single edge (T^3 # S^1xS^2), the path of two edges (T^3 # T^3 # S^1xS^2), the doubled edge
   ((genus-2 surface x S^1) # S^1xS^2) and cycles (graph manifolds: pants x S^1 with punctured-torus Seifert pieces), each counted
   independently, for S3 and the dihedral group of order 8;
2. the count does not depend on the outer face or on mirroring;
3. digon collapse: full counts of 2-thickened graphs equal the collapsed formula;
4. exponential polynomial: closed counts for k = 1..K+2 are fitted exactly by the stated bases (two extra values reproduced), and
   the coefficient of the target base equals the stated colouring identity (S3, the dihedral group of order 8);
5. target identities in exact rationals for S3 (2 P(G,9)/3^V), dihedral groups of orders 8, 10, 12 (P(G,8), 2 P(G,25)/5^V,
   2 (2/3)^V P(G,9)), Q8 (P(G,8)) and A4 (3 P(G,16)/4^V); the dihedral group of order 16 satisfies 2 P(G,16)/2^V but its target
   base collides (256 x 16 = 64^2): on C4 the coefficient of 64^(mk) exceeds the identity (documented obstruction);
6. controls: a genus-1 rotation system breaks the S3 identity; wrong targets are rejected; an abelian group's closed counts do not
   see colourings.
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent


# ------------------------------------------------------------------------------------------------------------------ groups
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
    def __init__(self, name, els):
        self.name = name
        self.els = els
        self.n = len(els[0])
        self.e = tuple(range(self.n))
        self.cent = {g: [h for h in els if self.mul(g, h) == self.mul(h, g)] for g in els}
        self.center = [g for g in els if len(self.cent[g]) == len(els)]
        self.W = {}
        for g in els:
            for c in els:
                self.W[(g, c)] = 0
            for t in self.cent[g]:
                for k in self.cent[g]:
                    self.W[(g, self.comm(t, k))] += 1
        self._conv = {}

    def mul(self, p, q):
        return tuple(p[q[i]] for i in range(self.n))

    def inv(self, p):
        r = [0] * self.n
        for i in range(self.n):
            r[p[i]] = i
        return tuple(r)

    def comm(self, a, b):
        return self.mul(self.mul(a, b), self.mul(self.inv(a), self.inv(b)))

    def Wk(self, lam, k):
        """k-fold convolution power of W(lam, .) over C(lam), as a dict"""
        key = (lam, k)
        if key not in self._conv:
            C = self.cent[lam]
            base = {c: self.W[(lam, c)] for c in C}
            if k == 1:
                self._conv[key] = base
            else:
                prev = self.Wk(lam, k - 1)
                self._conv[key] = {c: sum(base[x] * prev[self.mul(self.inv(x), c)] for x in C) for c in C}
        return self._conv[key]


def dihedral(n):
    return Group(f"dihedral of order {2 * n}", perm_group([tuple((i + 1) % n for i in range(n)), tuple((-i) % n for i in range(n))], n))


S3 = Group("S3", perm_group([(1, 0, 2), (1, 2, 0)], 3))
D8 = dihedral(4)
_U = [(s, k) for s in (1, -1) for k in "1ijk"]
_T = {("1", x): (1, x) for x in "1ijk"}
_T.update({(x, "1"): (1, x) for x in "1ijk"})
_T.update({("i", "i"): (-1, "1"), ("j", "j"): (-1, "1"), ("k", "k"): (-1, "1"), ("i", "j"): (1, "k"), ("j", "k"): (1, "i"),
           ("k", "i"): (1, "j"), ("j", "i"): (-1, "k"), ("k", "j"): (-1, "i"), ("i", "k"): (-1, "j")})
_IDX = {u: i for i, u in enumerate(_U)}


def _qm(a, b):
    s, x = _T[(a[1], b[1])]
    return (a[0] * b[0] * s, x)


Q8 = Group("Q8", perm_group([tuple(_IDX[_qm(g, u)] for u in _U) for g in [(1, "i"), (1, "j")]], 8))
A4 = Group("A4", perm_group([(1, 2, 0, 3), (1, 0, 3, 2)], 4))
Z6 = Group("Z6", perm_group([(1, 2, 3, 4, 5, 0)], 6))


# -------------------------------------------------------------------------------------------------------- plane multigraphs
def faces_of(edges, rot):
    def head(d):
        e, s = d
        return edges[e][1 - s]
    seen, faces = set(), []
    for d0 in [(i, s) for i in range(len(edges)) for s in (0, 1)]:
        if d0 in seen:
            continue
        face, d = [], d0
        while d not in seen:
            seen.add(d)
            v = head(d)
            r = rot[v]
            e2 = r[(r.index(d[0]) + 1) % len(r)]
            s2 = 0 if edges[e2][0] == v else 1
            face.append((v, d))
            d = (e2, s2)
        faces.append(face)
    return faces


def configurations(Gr, n, edges, rot, outer=None):
    """yield (y, sigma by face, side map) for all (y, sigma) admitting the (unique) ybar"""
    F = faces_of(edges, rot)
    if outer is None:
        outer = max(range(len(F)), key=lambda i: len(F[i]))
    side = {}
    for fi, face in enumerate(F):
        for v, d in face:
            side[d] = fi
    bounded = [i for i in range(len(F)) if i != outer]
    corners = {fi: [v for v, d in F[fi]] for fi in range(len(F))}
    mul, inv = Gr.mul, Gr.inv
    for y in itertools.product(Gr.els, repeat=n):
        for sig in itertools.product(Gr.els, repeat=len(bounded)):
            s = {outer: Gr.e}
            s.update(zip(bounded, sig))
            yb = [None] * n
            for u in corners[outer]:
                yb[u] = y[u]
            changed, ok = True, True
            while changed and ok:
                changed = False
                for fi in bounded:
                    cs = corners[fi]
                    known = [u for u in cs if yb[u] is not None]
                    if not known:
                        continue
                    u1 = known[0]
                    sf = s[fi]
                    for u in cs:
                        val = mul(yb[u1], mul(inv(sf), mul(mul(inv(y[u1]), y[u]), sf)))
                        if yb[u] is None:
                            yb[u] = val
                            changed = True
                        elif yb[u] != val:
                            ok = False
                            break
                    if not ok:
                        break
            if ok and all(v is not None for v in yb):
                yield y, s, side


def closed_count(Gr, n, edges, rot, k=1, outer=None):
    tot = 0
    for y, s, side in configurations(Gr, n, edges, rot, outer):
        w = 1
        for e, (u, v) in enumerate(edges):
            lam = Gr.mul(Gr.inv(y[v]), y[u])
            mu = Gr.mul(s[side[(e, 1)]], Gr.inv(s[side[(e, 0)]]))
            w *= Gr.Wk(lam, k).get(mu, 0)
            if not w:
                break
        tot += w
    return tot


def target_coef(Gr, n, edges, rot, f):
    tot = Fraction(0)
    for y, s, side in configurations(Gr, n, edges, rot):
        w = Fraction(1)
        for e, (u, v) in enumerate(edges):
            lam = Gr.mul(Gr.inv(y[v]), y[u])
            mu = Gr.mul(s[side[(e, 1)]], Gr.inv(s[side[(e, 0)]]))
            w *= f(lam, mu)
            if not w:
                break
        tot += w
    return tot


def thicken(n, edges, rot, k):
    ne, idx = [], {}
    for e, (u, v) in enumerate(edges):
        idx[e] = list(range(len(ne), len(ne) + k))
        ne += [(u, v)] * k
    nrot = {u: [] for u in range(n)}
    for u in range(n):
        for e in rot[u]:
            nrot[u].extend(idx[e] if edges[e][0] == u else list(reversed(idx[e])))
    return ne, nrot


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
                fct = A[j][i] / A[i][i]
                A[j] = [x - fct * yv for x, yv in zip(A[j], A[i])]
    return [A[i][K] / A[i][i] for i in range(K)]


# ----------------------------------------------------------------------------------------------------------- target weights
def chi2_S3(x):
    return sum(1 for i in range(3) if x[i] == i) - 1


def f_S3(lam, mu):
    if lam == S3.e:
        return Fraction(chi2_S3(mu), 3)
    if len(S3.cent[lam]) == 3:
        return Fraction(int(mu == S3.e))
    return Fraction(0)


def dihedral_target(Gr, n):
    """central edges: sum of the degree-2 characters times 2/|G|; edges with |C| = n: continuity; others: 0"""
    def rot_k(x):
        k = x[0]
        return k if all((x[i] - i) % n == k for i in range(n)) else None

    def chisum(mu):
        k = rot_k(mu)
        if k is None:
            return 0
        if n % 2:
            return n * (k % n == 0) - 1
        return n * (k % n == 0) - 1 - (-1) ** k

    def f(lam, mu):
        if lam in Gr.center:
            return Fraction(2 * chisum(mu), 2 * n)
        if len(Gr.cent[lam]) == n:
            return Fraction(int(mu == Gr.e))
        return Fraction(0)
    return f


def f_Q8(lam, mu):
    if lam in Q8.center:
        u = _U[mu[_IDX[(1, "1")]]]
        return Fraction({(1, "1"): 2, (-1, "1"): -2}.get(u, 0), 4)
    return Fraction(int(mu == Q8.e))


def f_A4(lam, mu):
    C = A4.cent[lam]
    if len(C) == 12:
        fix = sum(1 for i in range(4) if mu[i] == i)
        return Fraction({4: 3, 0: -1, 1: 0}[fix], 4)
    if len(C) == 4:
        return Fraction(int(mu == A4.e))
    return Fraction(0)


# ---------------------------------------------------------------------------------------------------------------- graphs
def cycle(n):
    return (n, [(i, (i + 1) % n) for i in range(n)], {i: [i, (i - 1) % n] for i in range(n)})


def theta(k):
    return (2, [(0, 1)] * k, {0: list(range(k)), 1: list(reversed(range(k)))})


GRAPHS = {
    "single edge": (2, [(0, 1)], {0: [0], 1: [0]}),
    "path": (3, [(0, 1), (1, 2)], {0: [0], 1: [0, 1], 2: [1]}),
    "C3": cycle(3), "C4": cycle(4), "C5": cycle(5),
    "theta2": theta(2), "theta3": theta(3), "theta4": theta(4),
    "diamond": (4, [(0, 1), (1, 2), (2, 0), (1, 3), (3, 2)], {0: [2, 0], 1: [0, 1, 3], 2: [1, 2, 4], 3: [3, 4]}),
    "K4": (4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)], {0: [0, 1, 2], 1: [3, 0, 4], 2: [5, 1, 3], 3: [4, 2, 5]}),
    "triangle with pendant": (4, [(0, 1), (1, 2), (2, 0), (2, 3)], {0: [0, 2], 1: [1, 0], 2: [2, 1, 3], 3: [3]}),
}


# ---------------------------------------------------------------------------------------------------------------- parts
def commuting_triples(Gr):
    return sum(1 for a in Gr.els for b in Gr.cent[a] for c in Gr.els if c in Gr.cent[a] and c in Gr.cent[b])


def surface_times_circle_genus2(Gr):
    tot = 0
    for h in Gr.els:
        C = Gr.cent[h]
        for a1, b1, a2, b2 in itertools.product(C, repeat=4):
            if Gr.mul(Gr.comm(a1, b1), Gr.comm(a2, b2)) == Gr.e:
                tot += 1
    return tot


def cycle_graph_manifold(Gr, n):
    tot = 0
    for f in Gr.els:
        C = Gr.cent[f]
        for cs in itertools.product(C, repeat=n - 1):
            prod = Gr.e
            for c in cs:
                prod = Gr.mul(prod, c)
            last = Gr.inv(prod)
            if last not in C:
                continue
            w = 1
            for c in list(cs) + [last]:
                w *= Gr.W[(c, f)]
                if not w:
                    break
            tot += w
    return tot * len(Gr.els)


def main() -> int:
    t0 = time.time()
    out = {}

    # part 1: identified manifolds
    p1 = {}
    for Gr in (S3, D8):
        g = len(Gr.els)
        ct = commuting_triples(Gr)
        rows = {
            "single edge = T^3 # S1xS2": (closed_count(Gr, *GRAPHS["single edge"]), ct * g),
            "path = T^3 # T^3 # S1xS2": (closed_count(Gr, *GRAPHS["path"]), ct * ct * g),
            "doubled edge = (genus-2 surface x S1) # S1xS2": (closed_count(Gr, *GRAPHS["theta2"]), surface_times_circle_genus2(Gr) * g),
            "C3 = graph manifold # S1xS2": (closed_count(Gr, *GRAPHS["C3"]), cycle_graph_manifold(Gr, 3)),
            "C4 = graph manifold # S1xS2": (closed_count(Gr, *GRAPHS["C4"]), cycle_graph_manifold(Gr, 4)),
        }
        p1[Gr.name] = {k: {"presentation": a, "independent": b, "equal": a == b} for k, (a, b) in rows.items()}
    part1_ok = all(r["equal"] for v in p1.values() for r in v.values())
    out["part1_identified_manifolds"] = {"cases": p1, "all equal": part1_ok}

    # part 2: outer face and mirror invariance (S3)
    p2 = {}
    for name in ("diamond", "K4", "C4", "triangle with pendant"):
        n, edges, rot = GRAPHS[name]
        F = faces_of(edges, rot)
        vals = {closed_count(S3, n, edges, rot, outer=o) for o in range(len(F))}
        mrot = {u: list(reversed(r)) for u, r in rot.items()}
        vals |= {closed_count(S3, n, edges, mrot, outer=o) for o in range(len(faces_of(edges, mrot)))}
        p2[name] = {"distinct values over outer faces and mirror": sorted(vals), "invariant": len(vals) == 1}
    part2_ok = all(v["invariant"] for v in p2.values())
    out["part2_outer_face_and_mirror"] = {"cases": p2, "all invariant": part2_ok}

    # part 3: digon collapse
    p3 = {}
    for Gr, name in ((S3, "C3"), (S3, "C4"), (D8, "C3")):
        n, edges, rot = GRAPHS[name]
        ne, nr = thicken(n, edges, rot, 2)
        p3[f"{Gr.name} {name}"] = {"full": closed_count(Gr, n, ne, nr), "collapsed": closed_count(Gr, n, edges, rot, k=2)}
    part3_ok = all(v["full"] == v["collapsed"] for v in p3.values())
    out["part3_digon_collapse"] = {"cases": p3, "all equal": part3_ok}

    # part 4: exponential polynomial and end-to-end interpolation
    p4 = {}
    part4_ok = True
    for Gr, name, factors, target, pred in (
            (S3, "C3", (36, 9, 4), 9, lambda n, e: Fraction(2 * colourings(n, e, 9), 3 ** n)),
            (S3, "C4", (36, 9, 4), 9, lambda n, e: Fraction(2 * colourings(n, e, 9), 3 ** n)),
            (D8, "C3", (64, 16), 16, lambda n, e: Fraction(colourings(n, e, 8)))):
        n, edges, rot = GRAPHS[name]
        m = len(edges)
        profiles = [p for p in itertools.product(range(m + 1), repeat=len(factors)) if sum(p) == m]
        nodes = []
        for p in profiles:
            x = 1
            for fct, c in zip(factors, p):
                x *= fct ** c
            nodes.append(x)
        assert len(set(nodes)) == len(nodes)
        K = len(nodes)
        Z = [closed_count(Gr, n, edges, rot, k=k) for k in range(1, K + 3)]
        sol = solve([[Fraction(x) ** k for x in nodes] for k in range(1, K + 1)], [Fraction(z) for z in Z[:K]])
        extra_ok = all(sum(s * Fraction(x) ** k for s, x in zip(sol, nodes)) == Z[k - 1] for k in (K + 1, K + 2))
        coef = dict(zip(nodes, sol)).get(target ** m)
        want = pred(n, edges)
        ok = extra_ok and coef == want
        part4_ok &= ok
        p4[f"{Gr.name} {name}"] = {"bases": len(nodes), "two extra values reproduced": extra_ok,
                                   "coefficient of target^(mk)": str(coef), "identity": str(want), "match": ok}
    # the dihedral group of order 16: the target base collides (256 x 16 = 64^2). On a triangle no contamination can occur (a cycle
    # carries an even number of reflection edges); on C4 the channel-resolved coefficient of 64^(mk) exceeds the identity.
    D16 = dihedral(8)
    N16 = 8

    def rot8(x):
        k = x[0]
        return k if all((x[i] - i) % N16 == k for i in range(N16)) else None

    def lin_sum(mu):
        k = rot8(mu)
        return 2 + 2 * (-1) ** k if k is not None else 0

    def deg2_sum(mu):
        k = rot8(mu)
        return N16 * (k % N16 == 0) - 1 - (-1) ** k if k is not None else 0

    def coef64(n, edges, rot):
        tot = {}
        for y, s, side in configurations(D16, n, edges, rot):
            poly = {0: Fraction(1)}
            for e, (u, v) in enumerate(edges):
                lam = D16.mul(D16.inv(y[v]), y[u])
                mu = D16.mul(s[side[(e, 1)]], D16.inv(s[side[(e, 0)]]))
                size = len(D16.cent[lam])
                if size == 16:
                    terms = {1: Fraction(lin_sum(mu), 16), 0: Fraction(2 * deg2_sum(mu), 16)}
                elif size == 8:
                    terms = {0: Fraction(int(mu == D16.e))}
                else:
                    terms = {-1: Fraction(int(mu == D16.e))}
                new = {}
                for d1, w1 in poly.items():
                    for d2, w2 in terms.items():
                        if w2:
                            new[d1 + d2] = new.get(d1 + d2, 0) + w1 * w2
                poly = new
                if not poly:
                    break
            for d, w in poly.items():
                tot[d] = tot.get(d, 0) + w
        return tot.get(0, Fraction(0))
    rows = {}
    for name in ("C3", "C4"):
        n, edges, rot = GRAPHS[name]
        c64 = coef64(n, edges, rot)
        ident = Fraction(2 * colourings(n, edges, 16), 2 ** n)
        rows[name] = {"coefficient of 64^(mk)": str(c64), "identity 2 P(G,16)/2^V": str(ident), "contamination": str(c64 - ident)}
    collision = 256 * 16 == 64 ** 2
    p4["dihedral of order 16 (collision)"] = {"256*16 == 64^2": collision, "rows": rows,
                                              "triangle uncontaminated (parity)": rows["C3"]["contamination"] == "0",
                                              "C4 contaminated": rows["C4"]["contamination"] != "0"}
    part4_ok &= collision and rows["C3"]["contamination"] == "0" and rows["C4"]["contamination"] != "0"
    out["part4_exponential_polynomial"] = {"cases": p4, "all as stated": part4_ok}

    # part 5: target identities
    p5 = {}
    part5_ok = True
    plan = [
        (S3, f_S3, lambda n, e: Fraction(2 * colourings(n, e, 9), 3 ** n), "2 P(G,9)/3^V",
         ["C3", "C4", "C5", "theta2", "theta3", "theta4", "diamond", "K4", "triangle with pendant"]),
        (D8, dihedral_target(D8, 4), lambda n, e: Fraction(colourings(n, e, 8)), "P(G,8)", ["C3", "C4", "theta3", "diamond", "K4"]),
        (dihedral(5), dihedral_target(dihedral(5), 5), lambda n, e: Fraction(2 * colourings(n, e, 25), 5 ** n), "2 P(G,25)/5^V",
         ["C3", "C4", "theta3"]),
        (dihedral(6), dihedral_target(dihedral(6), 6), lambda n, e: 2 * Fraction(2, 3) ** n * colourings(n, e, 9), "2 (2/3)^V P(G,9)",
         ["C3", "theta3"]),
        (Q8, f_Q8, lambda n, e: Fraction(colourings(n, e, 8)), "P(G,8)", ["C3", "C4", "theta3"]),
        (A4, f_A4, lambda n, e: Fraction(3 * colourings(n, e, 16), 4 ** n), "3 P(G,16)/4^V", ["C3", "C4", "theta3"]),
        (D16, dihedral_target(D16, 8), lambda n, e: Fraction(2 * colourings(n, e, 16), 2 ** n), "2 P(G,16)/2^V", ["C3", "theta3"]),
    ]
    for Gr, f, pred, label, names in plan:
        rows = {}
        for name in names:
            n, edges, rot = GRAPHS[name]
            c = target_coef(Gr, n, edges, rot, f)
            rows[name] = {"coefficient": str(c), label: str(pred(n, edges)), "match": c == pred(n, edges)}
            part5_ok &= c == pred(n, edges)
        p5[Gr.name] = rows
    out["part5_target_identities"] = {"cases": p5, "all match": part5_ok}

    # part 6: controls
    c = {}
    n, edges, _ = GRAPHS["diamond"]
    bad_rot = {0: [2, 0], 1: [1, 3, 0], 2: [2, 1, 4], 3: [4, 3]}     # a genus-1 rotation system (one face)
    c["genus-1 rotation system has one face"] = len(faces_of(edges, bad_rot)) == 1
    c["genus-1 rotation system breaks the S3 identity"] = target_coef(S3, n, edges, bad_rot, f_S3) != Fraction(2 * colourings(n, edges, 9), 3 ** n)
    n, edges, rot = GRAPHS["C4"]
    cs3 = target_coef(S3, n, edges, rot, f_S3)
    c["S3: wrong target 2 P(G,8)/3^V rejected"] = cs3 != Fraction(2 * colourings(n, edges, 8), 3 ** n)
    c["S3: wrong target 2 P(G,3) rejected"] = cs3 != 2 * colourings(n, edges, 3)
    cd8 = target_coef(D8, n, edges, rot, dihedral_target(D8, 4))
    c["order-8 dihedral: wrong target 2 P(G,9)/3^V rejected"] = cd8 != Fraction(2 * colourings(n, edges, 9), 3 ** n)
    a, b = GRAPHS["C4"], GRAPHS["triangle with pendant"]
    c["abelian Z6: equal closed counts on graphs with equal V, E, F and different P(G,3)"] = (
        closed_count(Z6, *a) == closed_count(Z6, *b) and colourings(a[0], a[1], 3) != colourings(b[0], b[1], 3))
    controls_ok = all(c.values())
    out["controls"] = {"results": c, "all pass": controls_ok}

    ok = part1_ok and part2_ok and part3_ok and part4_ok and part5_ok and controls_ok
    out["all_checks_pass"] = ok
    out["seconds"] = round(time.time() - t0, 1)
    result = {"schema_version": 1, "artifact_id": "HARD-3D-20261025-001B-P001", "status": "Proved" if ok else "Partial", "checks": out}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(out, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
