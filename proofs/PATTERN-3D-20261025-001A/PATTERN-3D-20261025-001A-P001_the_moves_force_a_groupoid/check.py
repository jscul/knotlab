#!/usr/bin/env python3
"""Check for PATTERN-3D-20261025-001A-P001 (the moves force a groupoid). Standard library only.

A pure counting law has a triangle rule R, a set of triples (x_ab, x_bc, x_ac) for a < b < c; a tetrahedron is allowed when its four
faces are in R. Ordered identities, with constants lam, mu:
- 1-4: every allowed tetrahedron extends in exactly mu ways at each of the five positions of a new vertex;
- 2-3: for every labelling of the nine boundary edges with the six boundary triangles in R, the number of labels on the new edge
  putting the three interior triangles in R is lam * [shared triangle in R].
The law survives when both hold with lam, mu >= 1. R is deterministic when it is the graph of a partial operation.

Parts:
1. every partial operation on one, two or three labels (4^9 + 3^4 + 2^1 tables): survival by a fast path-based test, confirmed by the
   generic test for every table passing the 1-4 identity and for a random sample; every survivor's reduced triangles form a groupoid
   with equal component values (objects x group order = mu) and lam = 1 (Theorem 2), and every reduced survivor is a groupoid;
2. groupoids with up to eight arrows: those with equal component values survive with lam = 1, mu = objects x group order; unequal
   values fail;
3. controls: merged arrows, a non-group monoid, the projection table, an unequal union and a wrong count formula must all fail;
4. the count formula (Corollary 3) on sampled ordered triangulations, for abelian vertex groups, against homology;
5. the reduction lemma (Lemma 1): deleting triangles in no allowed tetrahedron never changes the verdict or the constants.
"""
from __future__ import annotations

import itertools
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRIS5 = list(itertools.combinations(range(5), 3))
EDGES4 = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
FACES4 = [tuple(v for v in range(4) if v != i) for i in range(4)]


# ---------------------------------------------------------------------------------------------------------------- generic law test
class Law:
    """Exact identity test for any pure law (deterministic or not), by constraint propagation over edge labels."""

    def __init__(self, R):
        self.R = set(R)
        self.labels = sorted({l for t in self.R for l in t})
        self.by01, self.by02, self.by12 = defaultdict(set), defaultdict(set), defaultdict(set)
        for x, y, z in self.R:
            self.by01[(x, y)].add(z)
            self.by02[(x, z)].add(y)
            self.by12[(y, z)].add(x)

    def solutions(self, edges, tris, fixed):
        """all labellings of `edges` extending `fixed` with every triangle of `tris` in R"""
        out = []

        def cands(x, e):
            c = None
            for u, v, w in tris:
                ab, bc, ac = (u, v), (v, w), (u, w)
                if e == ac and ab in x and bc in x:
                    s = self.by01.get((x[ab], x[bc]), set())
                elif e == bc and ab in x and ac in x:
                    s = self.by02.get((x[ab], x[ac]), set())
                elif e == ab and bc in x and ac in x:
                    s = self.by12.get((x[bc], x[ac]), set())
                else:
                    continue
                c = set(s) if c is None else c & s
            return c

        def rec(x, rest):
            if not rest:
                out.append(dict(x))
                return
            best = None
            for e in rest:
                c = cands(x, e)
                if c is not None and (best is None or len(c) < len(best[1])):
                    best = (e, c)
            e, c = best if best is not None else (rest[0], set(self.labels))
            nrest = [f for f in rest if f != e]
            for v in sorted(c):
                x[e] = v
                if all(not ((u, w) in x and (w, z) in x and (u, z) in x) or (x[(u, w)], x[(w, z)], x[(u, z)]) in self.R
                       for u, w, z in tris):
                    rec(x, nrest)
                del x[e]

        rec(dict(fixed), list(edges))
        return out

    def tetrahedra(self):
        return self.solutions(EDGES4, list(itertools.combinations(range(4), 3)), {})

    def check14(self, tets):
        mu = None
        for t in tets:
            for r in range(5):
                old = [v for v in range(5) if v != r]
                fixed = {(old[i], old[j]): t[(i, j)] for i, j in t}
                newe = [(min(r, v), max(r, v)) for v in range(5) if v != r]
                c = len(self.solutions(newe, [tr for tr in TRIS5 if r in tr], fixed))
                if mu is None:
                    mu = c
                elif c != mu:
                    return None
        return mu

    def check23(self):
        lam = None
        for p, q in itertools.combinations(range(5), 2):
            others = tuple(v for v in range(5) if v not in (p, q))
            bedges = [e for e in itertools.combinations(range(5), 2) if e != (p, q)]
            btris = [t for t in TRIS5 if not ({p, q} <= set(t)) and t != others]
            itris = [t for t in TRIS5 if {p, q} <= set(t)]
            for x in self.solutions(bedges, btris, {}):
                sh = (x[(others[0], others[1])], x[(others[1], others[2])], x[(others[0], others[2])]) in self.R
                c = len(self.solutions([(p, q)], itris, x))
                if sh:
                    if lam is None:
                        lam = c
                    elif c != lam:
                        return None
                elif c:
                    return None
        return lam

    def verdict(self):
        tets = self.tetrahedra()
        if not tets:
            return ("empty", None, None)
        mu = self.check14(tets)
        if mu is None:
            return ("fails 1-4", None, None)
        if mu == 0:
            return ("mu = 0", None, None)
        lam = self.check23()
        if lam is None or lam < 1:
            return ("fails 2-3", None, None)
        return ("survives", lam, mu)


# ---------------------------------------------------------------------------------------------------- fast test for partial operations
def fast14(op, labels):
    """For a partial operation (dict), a 4-simplex is determined by its path; returns ('empty'|'fails 1-4'|'mu = 0'|'passes', mu)."""
    def m(x, y):
        return op.get((x, y))

    def allowed(a, b, c):
        ab, bc = m(a, b), m(b, c)
        if ab is None or bc is None:
            return False
        l, r = m(ab, c), m(a, bc)
        return l is not None and l == r

    tets = [t for t in itertools.product(labels, repeat=3) if allowed(*t)]
    if not tets:
        return "empty", None
    N = [defaultdict(int) for _ in range(5)]
    tset = set(tets)
    for a, b, c in tets:
        for d in labels:
            if (b, c, d) not in tset:
                continue
            ab, bc, cd = m(a, b), m(b, c), m(c, d)
            if (ab, c, d) in tset and (a, bc, d) in tset and (a, b, cd) in tset:
                N[4][(a, b, c)] += 1
                N[0][(b, c, d)] += 1
                N[1][(ab, c, d)] += 1
                N[2][(a, bc, d)] += 1
                N[3][(a, b, cd)] += 1
    vals = {N[r][t] for t in tets for r in range(5)}
    if len(vals) > 1:
        return "fails 1-4", None
    mu = vals.pop()
    return ("mu = 0", None) if mu == 0 else ("passes", mu)


def reduced(R):
    """triangles lying in some allowed tetrahedron"""
    law = Law(R)
    out = set()
    for x in law.tetrahedra():
        for a, b, c in itertools.combinations(range(4), 3):
            out.add((x[(a, b)], x[(b, c)], x[(a, c)]))
    return out


def groupoid_structure(R):
    """If the deterministic rule R is the composition of a groupoid, return its components [(objects, group order)], else None."""
    comp = {}
    for x, y, z in R:
        if comp.setdefault((x, y), z) != z:
            return None
    labels = sorted({l for t in R for l in t})
    idem = [e for e in labels if comp.get((e, e)) == e]
    s, t = {}, {}
    for x in labels:
        L = [e for e in idem if comp.get((e, x)) == x]
        Rt = [e for e in idem if comp.get((x, e)) == x]
        if len(L) != 1 or len(Rt) != 1:
            return None
        s[x], t[x] = L[0], Rt[0]
    for x in labels:
        for y in labels:
            if ((x, y) in comp) != (t[x] == s[y]):
                return None
            if (x, y) in comp:
                z = comp[(x, y)]
                if s[z] != s[x] or t[z] != t[y]:
                    return None
    for x, y, z in itertools.product(labels, repeat=3):
        if (x, y) in comp and (y, z) in comp and comp[(comp[(x, y)], z)] != comp[(x, comp[(y, z)])]:
            return None
    for x in labels:
        if not any(comp.get((x, y)) == s[x] and comp.get((y, x)) == t[x] for y in labels):
            return None
    # components: objects connected by arrows
    parent = {o: o for o in idem}

    def find(o):
        while parent[o] != o:
            parent[o] = parent[parent[o]]
            o = parent[o]
        return o

    for x in labels:
        parent[find(s[x])] = find(t[x])
    comps = defaultdict(list)
    for o in idem:
        comps[find(o)].append(o)
    out = []
    for objs in comps.values():
        o = objs[0]
        group = [x for x in labels if s[x] == o and t[x] == o]
        out.append((len(objs), len(group)))
    return sorted(out)


# ------------------------------------------------------------------------------------------------------------------- groupoids
def groupoid_rule(components):
    """components: list of (objects, elements, multiplication); arrows are (component, o1, g, o2)."""
    R = set()
    for ci, (objs, els, mul) in enumerate(components):
        for o1, o2, o3 in itertools.product(objs, repeat=3):
            for g in els:
                for h in els:
                    R.add(((ci, o1, g, o2), (ci, o2, h, o3), (ci, o1, mul(g, h), o3)))
    return R


def relabel(R):
    names = {}
    return {tuple(names.setdefault(m, len(names)) for m in t) for t in R}


def cyclic(n):
    return (list(range(n)), lambda g, h: (g + h) % n)


def product(*ns):
    els = list(itertools.product(*[range(n) for n in ns]))
    return (els, lambda g, h: tuple((a + b) % n for a, b, n in zip(g, h, ns)))


def perm_group(gens, n):
    els = {tuple(range(n))}
    frontier = list(els)
    while frontier:
        new = []
        for p in frontier:
            for g in gens:
                q = tuple(p[g[i]] for i in range(n))
                if q not in els:
                    els.add(q)
                    new.append(q)
        frontier = new
    return (sorted(els), lambda g, h: tuple(g[h[i]] for i in range(n)))


TRIV = ([0], lambda g, h: 0)
S3 = perm_group([(1, 0, 2), (1, 2, 0)], 3)
D4 = perm_group([(1, 2, 3, 0), (3, 2, 1, 0)], 4)
Q8_ELS = [(s, k) for s in (1, -1) for k in "1ijk"]
_QT = {("1", x): (1, x) for x in "1ijk"}
_QT.update({(x, "1"): (1, x) for x in "1ijk"})
_QT.update({("i", "i"): (-1, "1"), ("j", "j"): (-1, "1"), ("k", "k"): (-1, "1"), ("i", "j"): (1, "k"), ("j", "k"): (1, "i"),
            ("k", "i"): (1, "j"), ("j", "i"): (-1, "k"), ("k", "j"): (-1, "i"), ("i", "k"): (-1, "j")})
Q8 = (Q8_ELS, lambda g, h: (g[0] * h[0] * _QT[(g[1], h[1])][0], _QT[(g[1], h[1])][1]))


def groupoid_cases():
    """(name, components, expected mu or None when the component values differ)"""
    cases = []
    groups = {"1": TRIV, "Z2": cyclic(2), "Z3": cyclic(3), "Z4": cyclic(4), "Z2xZ2": product(2, 2), "Z5": cyclic(5),
              "Z6": cyclic(6), "S3": S3, "Z7": cyclic(7), "Z8": cyclic(8), "Z4xZ2": product(4, 2), "Z2^3": product(2, 2, 2),
              "D4": D4, "Q8": Q8}
    for name, G in groups.items():
        cases.append((name, [(["o"],) + G], len(G[0])))
    for k in (2, 3):
        for name in ("1", "Z2"):
            G = groups[name]
            if k * k * len(G[0]) <= 8:
                cases.append((f"{k} objects x {name}", [([f"o{i}" for i in range(k)],) + G], k * len(G[0])))
    cases += [
        ("two constants", [(["X"],) + TRIV, (["Y"],) + TRIV], 1),
        ("four constants", [([o],) + TRIV for o in "WXYZ"], 1),
        ("Z2 + Z2", [(["X"],) + cyclic(2), (["Y"],) + cyclic(2)], 2),
        ("Z3 + Z3", [(["X"],) + cyclic(3), (["Y"],) + cyclic(3)], 3),
        ("Z4 + Z2xZ2", [(["X"],) + cyclic(4), (["Y"],) + product(2, 2)], 4),
        ("Z2 + 2 objects x 1", [(["X"],) + cyclic(2), (["Y", "W"],) + TRIV], 2),
        ("2 objects x 1 + 2 objects x 1", [(["X", "Y"],) + TRIV, (["U", "W"],) + TRIV], 2),
        ("Z2 + 1 (unequal)", [(["X"],) + cyclic(2), (["Y"],) + TRIV], None),
        ("Z3 + Z2 (unequal)", [(["X"],) + cyclic(3), (["Y"],) + cyclic(2)], None),
        ("2 objects x 1 + 1 (unequal)", [(["X", "Y"],) + TRIV, (["W"],) + TRIV], None),
    ]
    return cases


# --------------------------------------------------------------------------------------- ordered triangulations (from TWIST-3D A)
class DSU:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        self.p[self.find(a)] = self.find(b)


def build(T, pairing):
    vd, ed, fd = DSU(), DSU(), DSU()
    for (t, i), (u, j) in pairing:
        A, B = FACES4[i], FACES4[j]
        for k in range(3):
            vd.union((t, A[k]), (u, B[k]))
        for k, l in itertools.combinations(range(3), 2):
            ed.union((t, A[k], A[l]), (u, B[k], B[l]))
        fd.union((t, i), (u, j))
    verts = sorted({vd.find((t, v)) for t in range(T) for v in range(4)})
    edges = sorted({ed.find((t, a, b)) for t in range(T) for a, b in EDGES4})
    faces = sorted({fd.find((t, i)) for t in range(T) for i in range(4)})
    return vd, ed, fd, verts, edges, faces


def is_manifold(T, pairing):
    vd, ed, fd, verts, edges, faces = build(T, pairing)
    if len(verts) - len(edges) + len(faces) - T != 0:
        return False
    for vc in verts:
        corners = [(t, v) for t in range(T) for v in range(4) if vd.find((t, v)) == vc]
        lv = len({(ed.find((t,) + tuple(sorted((v, w)))), v < w) for (t, v) in corners for w in range(4) if w != v})
        if lv - 3 * len(corners) // 2 + len(corners) != 2:
            return False
    sign = {0: 1}
    adj = {}
    for (t, i), (u, j) in pairing:
        adj.setdefault(t, []).append((u, i, j))
        adj.setdefault(u, []).append((t, j, i))
    stack = [0]
    while stack:
        t = stack.pop()
        for u, i, j in adj.get(t, []):
            want = -sign[t] * (-1) ** i * (-1) ** j
            if u not in sign:
                sign[u] = want
                stack.append(u)
            elif sign[u] != want:
                return False
    return len(sign) == T


def snf_diagonal(M):
    A = [row[:] for row in M]
    rows = len(A)
    cols = len(A[0]) if A else 0
    diag, r = [], 0
    for c in range(cols):
        while True:
            piv = None
            for i in range(r, rows):
                for j in range(c, cols):
                    if A[i][j] and (piv is None or abs(A[i][j]) < abs(A[piv[0]][piv[1]])):
                        piv = (i, j)
            if piv is None:
                return diag
            i, j = piv
            A[r], A[i] = A[i], A[r]
            for row in A:
                row[c], row[j] = row[j], row[c]
            clean = True
            for i in range(r + 1, rows):
                q = A[i][c] // A[r][c]
                if q:
                    A[i] = [x - q * y for x, y in zip(A[i], A[r])]
                if A[i][c]:
                    clean = False
            for j in range(c + 1, cols):
                q = A[r][j] // A[r][c]
                if q:
                    for row in A:
                        row[j] -= q * row[c]
                if A[r][j]:
                    clean = False
            if clean:
                bad = next(((i, j) for i in range(r + 1, rows) for j in range(c + 1, cols) if A[i][j] % A[r][c]), None)
                if bad is None:
                    diag.append(abs(A[r][c]))
                    r += 1
                    break
                A[r] = [x + y for x, y in zip(A[r], A[bad[0]])]
        if r >= rows:
            break
    return diag


def homology(T, pairing):
    """H1 of the glued complex: (free rank, torsion coefficients), with the vertex and edge counts"""
    vd, ed, fd, verts, edges, faces = build(T, pairing)
    vi = {v: k for k, v in enumerate(verts)}
    ei = {e: k for k, e in enumerate(edges)}
    frep, erep = {}, {}
    for t in range(T):
        for i in range(4):
            frep.setdefault(fd.find((t, i)), (t, i))
        for a, b in EDGES4:
            erep.setdefault(ed.find((t, a, b)), (t, a, b))
    D2 = [[0] * len(faces) for _ in edges]
    for fk, f in enumerate(faces):
        t, i = frep[f]
        a, b, c = FACES4[i]
        D2[ei[ed.find((t, b, c))]][fk] += 1
        D2[ei[ed.find((t, a, c))]][fk] -= 1
        D2[ei[ed.find((t, a, b))]][fk] += 1
    D1 = [[0] * len(edges) for _ in verts]
    for ek, e in enumerate(edges):
        t, a, b = erep[e]
        D1[vi[vd.find((t, b))]][ek] += 1
        D1[vi[vd.find((t, a))]][ek] -= 1
    d2, d1 = snf_diagonal(D2), snf_diagonal(D1)
    return len(edges) - len(d1) - len(d2), sorted(d for d in d2 if d > 1), len(verts), len(edges)


def coloring_count(T, pairing, R):
    """number of edge labellings of the glued triangulation with every face of every tetrahedron in R"""
    vd, ed, fd, verts, edges, faces = build(T, pairing)
    ei = {e: k for k, e in enumerate(edges)}
    tris = set()
    for t in range(T):
        for i in range(4):
            a, b, c = FACES4[i]
            tris.add((ei[ed.find((t, a, b))], ei[ed.find((t, b, c))], ei[ed.find((t, a, c))]))
    law = Law(R)
    edge_names = list(range(len(edges)))
    # reuse the propagation search with edges named by pairs (k, k) so that triangles are triples of such names
    by01, by02, by12, Rset = law.by01, law.by02, law.by12, law.R
    tris = sorted(tris)
    count = 0

    def cands(x, e):
        c = None
        for ab, bc, ac in tris:
            if e == ac and ab in x and bc in x:
                s = by01.get((x[ab], x[bc]), set())
            elif e == bc and ab in x and ac in x:
                s = by02.get((x[ab], x[ac]), set())
            elif e == ab and bc in x and ac in x:
                s = by12.get((x[bc], x[ac]), set())
            else:
                continue
            c = set(s) if c is None else c & s
        return c

    def rec(x, rest):
        nonlocal count
        if not rest:
            count += 1
            return
        best = None
        for e in rest:
            c = cands(x, e)
            if c is not None and (best is None or len(c) < len(best[1])):
                best = (e, c)
        e, c = best if best is not None else (rest[0], set(law.labels))
        nrest = [f for f in rest if f != e]
        for v in c:
            x[e] = v
            if all(not (ab in x and bc in x and ac in x) or (x[ab], x[bc], x[ac]) in Rset for ab, bc, ac in tris):
                rec(x, nrest)
            del x[e]

    rec({}, edge_names)
    return count


def hom_count_abelian(free, tors, invariants):
    """|Hom(H1, A)| for A = product of cyclic groups Z/n (n in invariants)"""
    out = 1
    for n in invariants:
        from math import gcd
        out *= n ** free
        for d in tors:
            out *= gcd(d, n)
    return out


# ---------------------------------------------------------------------------------------------------------------------- main
def main() -> int:
    t0 = __import__("time").time()
    results = {}

    # part 1: every partial operation on at most three labels
    part1 = {}
    survivors_all = []
    for n in (1, 2, 3):
        labels = list(range(n))
        pairs = list(itertools.product(labels, repeat=2))
        stats = defaultdict(int)
        nsurv = 0
        for table in itertools.product([None] + labels, repeat=n * n):
            op = {p: v for p, v in zip(pairs, table) if v is not None}
            status, mu = fast14(op, labels)
            if status != "passes":
                stats[status] += 1
                continue
            R = {(x, y, z) for (x, y), z in op.items()}
            v, lam, mu2 = Law(R).verdict()
            assert v != "fails 1-4" and mu2 in (None, mu), (op, v, mu, mu2)
            if v != "survives":
                stats[v] += 1
                continue
            stats["survives"] += 1
            nsurv += 1
            survivors_all.append((n, table, lam, mu))
        part1[n] = dict(stats)
    # classify survivors
    classes = defaultdict(int)
    theorem_ok = True
    for n, table, lam, mu in survivors_all:
        labels = list(range(n))
        op = {p: v for p, v in zip(itertools.product(labels, repeat=2), table) if v is not None}
        R = {(x, y, z) for (x, y), z in op.items()}
        Rr = reduced(R)
        g = groupoid_structure(Rr)
        ok = g is not None and lam == 1 and all(o * k == mu for o, k in g)
        theorem_ok &= ok
        classes[str(g)] += 1
    # every partial operation whose full rule is a groupoid with equal values survives (the converse, on these tables)
    converse_ok = True
    nconv = 0
    for n in (1, 2, 3):
        labels = list(range(n))
        pairs = list(itertools.product(labels, repeat=2))
        for table in itertools.product([None] + labels, repeat=n * n):
            op = {p: v for p, v in zip(pairs, table) if v is not None}
            R = {(x, y, z) for (x, y), z in op.items()}
            if not R:
                continue
            g = groupoid_structure(R)
            if g is None or len({o * k for o, k in g}) != 1 or len({l for t in R for l in t}) != n:
                continue
            nconv += 1
            v, lam, mu = Law(R).verdict()
            converse_ok &= (v, lam, mu) == ("survives", 1, g[0][0] * g[0][1])
    # cross-check the fast 1-4 test against the generic one on a random sample
    rng = random.Random(20261025)
    agree = True
    for _ in range(1500):
        n = rng.choice((2, 3))
        labels = list(range(n))
        op = {p: v for p in itertools.product(labels, repeat=2) if (v := rng.choice([None] + labels)) is not None}
        status, mu = fast14(op, labels)
        R = {(x, y, z) for (x, y), z in op.items()}
        law = Law(R)
        tets = law.tetrahedra()
        if not tets:
            agree &= status == "empty"
            continue
        m = law.check14(tets)
        if m is None:
            agree &= status == "fails 1-4"
        elif m == 0:
            agree &= status == "mu = 0"
        else:
            agree &= status == "passes" and mu == m
    results["part1_partial_operations"] = {
        "tables by label count": {str(n): sum(v for v in part1[n].values()) for n in part1},
        "outcomes": {str(n): part1[n] for n in part1},
        "surviving tables": len(survivors_all),
        "reduced survivors by groupoid components [(objects, group order)]": dict(sorted(classes.items())),
        "every survivor reduces to a groupoid with equal values, lam = 1, mu = objects x group order": theorem_ok,
        "groupoid tables with equal values (all labels used)": nconv,
        "each of them survives with lam = 1 and mu = objects x group order": converse_ok,
        "fast 1-4 test agrees with the generic test on 1,500 random tables": agree,
    }

    # part 2: groupoids with up to eight arrows
    part2 = {}
    p2_ok = True
    for name, comps, want in groupoid_cases():
        R = relabel(groupoid_rule(comps))
        v, lam, mu = Law(R).verdict()
        ok = (v, lam, mu) == ("survives", 1, want) if want is not None else v != "survives"
        p2_ok &= ok
        part2[name] = {"arrows": len({l for t in R for l in t}), "verdict": v, "lam": lam, "mu": mu, "as predicted": ok}
    results["part2_groupoids"] = {"cases": part2, "all as predicted": p2_ok}

    # part 3: controls that must fail
    controls = {}
    R, _ = groupoid_rule([(["X", "Y"],) + TRIV]), None
    merge_id = {tuple("1" if m[1] == m[3] else m for m in t) for t in R}
    controls["pair groupoid with its identities merged"] = Law(relabel(merge_id)).verdict()[0]
    R2 = groupoid_rule([(["X", "Y"],) + TRIV, (["U", "W"],) + TRIV])
    f, f2 = (0, "X", 0, "Y"), (1, "U", 0, "W")
    controls["two pair groupoids with X->Y and U->W merged"] = Law(relabel({tuple("F" if m in (f, f2) else m for m in t)
                                                                          for t in R2})).verdict()[0]
    controls["monoid {0,1} under multiplication"] = Law({(a, b, a * b) for a in (0, 1) for b in (0, 1)}).verdict()[0]
    controls["projection table x*y = x on three labels"] = Law({(a, b, a) for a in range(3) for b in range(3)}).verdict()[0]
    controls["Z2 + one constant (unequal values)"] = Law(relabel(groupoid_rule([(["X"],) + cyclic(2), (["Y"],) + TRIV]))).verdict()[0]
    controls["Z3 table with one entry changed"] = Law({(a, b, (a + b) % 3 if (a, b) != (1, 1) else 0)
                                                       for a in range(3) for b in range(3)}).verdict()[0]
    controls_ok = all(v != "survives" for v in controls.values())

    # part 4: the count formula on sampled ordered triangulations
    rng = random.Random(20261026)
    samples, per = [], {}
    while len(samples) < 40:
        T = rng.randint(1, 4)
        faces = [(t, i) for t in range(T) for i in range(4)]
        rng.shuffle(faces)
        pairing = [(faces[k], faces[k + 1]) for k in range(0, 4 * T, 2)]
        if not is_manifold(T, pairing):
            continue
        free, tors, V, E = homology(T, pairing)
        if E > 10:
            continue
        key = (free, tuple(tors))
        if per.get(key, 0) >= 6:
            continue
        per[key] = per.get(key, 0) + 1
        samples.append((T, pairing, free, tors, V, E))
    laws = {
        "Z3": ([(["o"],) + cyclic(3)], [[3]]),
        "Z4": ([(["o"],) + cyclic(4)], [[4]]),
        "Z2xZ2": ([(["o"],) + product(2, 2)], [[2, 2]]),
        "pair groupoid": ([(["X", "Y"],) + TRIV], [[]]),
        "Z2 + Z2": ([(["X"],) + cyclic(2), (["Y"],) + cyclic(2)], [[2], [2]]),
    }
    formula_ok = True
    distinguishes = {"Z4 vs Z2xZ2": False, "Z3 vs trivial": False}
    rows = []
    for T, pairing, free, tors, V, E in samples:
        row = {"tetrahedra": T, "H1": [free, tors], "V": V, "E": E}
        vals = {}
        for name, (comps, invs) in laws.items():
            R = relabel(groupoid_rule(comps))
            mu = len(comps[0][0]) * len(comps[0][1])
            got = coloring_count(T, pairing, R)
            from fractions import Fraction
            want = mu ** V * sum(Fraction(hom_count_abelian(free, tors, inv), len(c[1])) for c, inv in zip(comps, invs))
            formula_ok &= got == want
            vals[name] = got
            row[name] = got
        distinguishes["Z4 vs Z2xZ2"] |= vals["Z4"] != vals["Z2xZ2"]
        distinguishes["Z3 vs trivial"] |= vals["Z3"] != 3 ** V
        rows.append(row)
    results["part4_count_formula"] = {"sampled triangulations": len(samples),
                                      "H1 types": sorted([[k[0], list(k[1])] for k in per]),
                                      "counts equal mu^V * sum |Hom(H1, G_i)| / |G_i|": formula_ok,
                                      "the formula test can fail (some sample separates)": distinguishes,
                                      "rows": rows}
    formula_nonvacuous = all(distinguishes.values())

    # part 5: the reduction lemma on random rules with junk triangles added to survivors
    rng = random.Random(20261027)
    red_ok = True
    tested = 0
    for n, table, lam, mu in survivors_all[:: max(1, len(survivors_all) // 60)]:
        labels = list(range(n))
        op = {p: v for p, v in zip(itertools.product(labels, repeat=2), table) if v is not None}
        R = {(x, y, z) for (x, y), z in op.items()}
        Rr = reduced(R)
        tested += 1
        red_ok &= Law(Rr).verdict() == ("survives", lam, mu)
    # and on random rules (partial operations and arbitrary relations on three labels) that have allowed tetrahedra
    junk_tested = 0
    while junk_tested < 300:
        if junk_tested % 2:
            op = {p: rng.randrange(3) for p in itertools.product(range(3), repeat=2) if rng.random() < 0.8}
            R = {(x, y, z) for (x, y), z in op.items()}
        else:
            R = {t for t in itertools.product(range(3), repeat=3) if rng.random() < 0.45}
        Rr = reduced(R)
        if not Rr or Rr == R:
            continue
        junk_tested += 1
        red_ok &= Law(R).verdict() == Law(Rr).verdict()
    results["part5_reduction_lemma"] = {"survivors re-tested on their reduced triangles": tested,
                                        "random rules with junk triangles re-tested": junk_tested,
                                        "same verdict and constants": red_ok}

    results["controls"] = {"verdicts": controls, "all fail": controls_ok}
    ok = (theorem_ok and converse_ok and agree and p2_ok and controls_ok and formula_ok and formula_nonvacuous and red_ok)
    results["all_checks_pass"] = ok
    results["seconds"] = round(__import__("time").time() - t0, 1)
    out = {"schema_version": 1, "artifact_id": "PATTERN-3D-20261025-001A-P001", "status": "Proved" if ok else "Partial",
           "checks": results}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps({k: (v if k != "part4_count_formula" else {kk: vv for kk, vv in v.items() if kk != "rows"})
                      for k, v in results.items()}, indent=1, default=str))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
