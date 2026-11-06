#!/usr/bin/env python3
"""Check of TWIST-3D-20261025-001A-P001 (standard library only, seed 20261025).

Ordered triangulations: every tetrahedron has vertices 0 < 1 < 2 < 3 and faces are glued by the order-preserving maps. A law has one
bit per edge, a triangle rule R read on (x_ab, x_bc, x_ac) for a triangle a < b < c, and tetrahedron rules Q+ and Q- (sets of
R-compatible labellings of the six ordered edges) for the two orientations of an ordered tetrahedron in an oriented manifold.
Ordered moves live on the 4-simplex [01234] with facets F_i (vertex i removed): a 2-3 move with apex pair {p, q} replaces F_p, F_q by
the other three facets, and a 1-4 move with new vertex r replaces F_r by the other four. With global orientation eps, the
M-orientation of F_i is eps (-1)^i on the new side and -eps (-1)^i on the old side. The identities: for every labelling of the move's
boundary edges whose boundary triangles lie in R, the new side summed over the new edges equals lambda (2-3) or mu (1-4) times the old
side.
Checks:
- the census, by a complete search with unit propagation over the tetrahedron rules, for all 255 triangle rules and all (lambda, mu)
  with lambda in {1, 2} and mu in {1, ..., 16}: once with one rule for both orientations and once with two;
- every solution is one of the seven symmetric laws, the two orientations always agree, and the solutions are exactly the seven laws
  contained in the compatible labellings (354 in all); each of these satisfies every identity by direct evaluation;
- on 60 sampled ordered triangulations of closed orientable manifolds (homology computed by Smith normal form), the counts are 1 for
  all 0 and all 1, 2 for all equal, |Z^1| = |H^1(M; Z2)| 2^(V-1) for even and odd cocycles, twice that for even or odd, and 2^E for
  free.
Controls: the twisted law with triangle rule excluding 000, 011, 101 and all its 12 compatible tetrahedra fails some identity; with the
1-4 identities dropped, the search admits rules outside the seven for the full triangle rule; a sampled triangulation with H_1 of even order has |H^1(M; Z2)| = 2
and doubles the cocycle count of the sphere.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CUBE = list(itertools.product((0, 1), repeat=3))
E5 = [(a, b) for a in range(5) for b in range(a + 1, 5)]
EDGES4 = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
FACES4 = [tuple(v for v in range(4) if v != i) for i in range(4)]
LABS = list(itertools.product((0, 1), repeat=6))


def tri_ok(R, x, a, b, c):
    return (x[(a, b)], x[(b, c)], x[(a, c)]) in R


def tet_lab(x, verts):
    v = sorted(verts)
    return tuple(x[(v[i], v[j])] for i, j in EDGES4)


def facet(i):
    return tuple(v for v in range(5) if v != i)


def compatible(R):
    out = []
    for lab in LABS:
        x = dict(zip(EDGES4, lab))
        if all(tri_ok(R, x, *f) for f in itertools.combinations(range(4), 3)):
            out.append(lab)
    return out


def face_parities(lab):
    x = dict(zip(EDGES4, lab))
    return tuple((x[(a, b)] + x[(b, c)] + x[(a, c)]) % 2 for a, b, c in itertools.combinations(range(4), 3))


ZEVEN = frozenset(l for l in LABS if face_parities(l) == (0, 0, 0, 0))
ZODD = frozenset(l for l in LABS if face_parities(l) == (1, 1, 1, 1))
ZERO, ONE = (0,) * 6, (1,) * 6
SEVEN = {"all 0": (frozenset([ZERO]), 1, 1), "all 1": (frozenset([ONE]), 1, 1), "all equal": (frozenset([ZERO, ONE]), 1, 1),
         "even cocycles": (ZEVEN, 1, 2), "odd cocycles": (ZODD, 1, 2), "even or odd": (ZEVEN | ZODD, 1, 2),
         "free": (frozenset(LABS), 2, 16)}


def identities(R, oriented):
    """list of (kind, old items, list of new item tuples); an item is (sign, labelling); sign is 1 when not oriented"""
    sg = (lambda s: s) if oriented else (lambda s: 1)
    out = []
    for eps in ((1, -1) if oriented else (1,)):
        for p, q in itertools.combinations(range(5), 2):
            others = [v for v in range(5) if v not in (p, q)]
            bnd_edges = [e for e in E5 if e != (p, q)]
            bnd_tris = [t for t in itertools.combinations(range(5), 3) if not ({p, q} <= set(t)) and set(t) != set(others)]
            for lab in itertools.product((0, 1), repeat=9):
                x = dict(zip(bnd_edges, lab))
                if not all(tri_ok(R, x, *t) for t in bnd_tris):
                    continue
                old = tuple((sg(-eps * (-1) ** i), tet_lab(x, facet(i))) for i in (p, q))
                new = []
                for e in (0, 1):
                    y = dict(x)
                    y[(p, q)] = e
                    new.append(tuple((sg(eps * (-1) ** r), tet_lab(y, facet(r))) for r in others))
                out.append((0, old, new))
        for r in range(5):
            F = facet(r)
            bnd_edges = [e for e in E5 if r not in e]
            new_edges = [e for e in E5 if r in e]
            for lab in itertools.product((0, 1), repeat=6):
                x = dict(zip(bnd_edges, lab))
                if not all(tri_ok(R, x, *t) for t in itertools.combinations(F, 3)):
                    continue
                old = ((sg(-eps * (-1) ** r), tet_lab(x, F)),)
                new = []
                for nl in itertools.product((0, 1), repeat=4):
                    y = dict(x)
                    y.update(zip(new_edges, nl))
                    new.append(tuple((sg(eps * (-1) ** s), tet_lab(y, facet(s))) for s in range(5) if s != r))
                out.append((1, old, new))
    return out


def to_masks(ids, index):
    def mask(items):
        m = 0
        for it in items:
            if it not in index:
                return None
            m |= 1 << index[it]
        return m
    seen, out = set(), []
    for kind, old, new in ids:
        o = mask(old)
        terms = sorted(t for t in (mask(n) for n in new) if t is not None)
        key = (kind, o, tuple(terms))
        if key not in seen:
            seen.add(key)
            out.append((kind, o, terms))
    return out


def propagate(cons, ones, zeros, k, var_cons):
    queue = list(range(len(cons)))
    inq = set(queue)
    while queue:
        ci = queue.pop()
        inq.discard(ci)
        kind, old, terms = cons[ci]
        kk = k[kind]
        if old is None or old & zeros:
            rv = (0,)
        elif old & ~ones == 0:
            rv = (kk,)
        else:
            rv = (0, kk)
        lo = hi = 0
        open_terms = []
        for t in terms:
            if t & zeros:
                continue
            hi += 1
            if t & ~ones == 0:
                lo += 1
            else:
                open_terms.append(t)
        feas = [v for v in rv if lo <= v <= hi]
        if not feas:
            return None
        new1 = new0 = 0
        if feas == [0]:
            for t in open_terms:
                un = t & ~ones & ~zeros
                if un and un & (un - 1) == 0:
                    new0 |= un
            if old is not None and not (old & zeros) and len(rv) == 2:
                un = old & ~ones & ~zeros
                if un and un & (un - 1) == 0:
                    new0 |= un
        if len(feas) == 1 and feas[0] == hi and hi > lo:
            for t in open_terms:
                new1 |= t & ~ones & ~zeros
        if len(feas) == 1 and feas[0] > 0 and old is not None:
            new1 |= old & ~ones & ~zeros
        if new1 & new0 or new1 & zeros or new0 & ones:
            return None
        if new1 or new0:
            ones |= new1
            zeros |= new0
            changed = new1 | new0
            while changed:
                b = changed & -changed
                changed ^= b
                for cj in var_cons[b.bit_length() - 1]:
                    if cj not in inq:
                        inq.add(cj)
                        queue.append(cj)
    return ones, zeros


def search(cons, m, items, lams=(1, 2), mus=range(1, 17)):
    var_cons = [[] for _ in range(m)]
    for ci, (kind, old, terms) in enumerate(cons):
        allm = old or 0
        for t in terms:
            allm |= t
        for i in range(m):
            if allm >> i & 1:
                var_cons[i].append(ci)
    order = sorted(range(m), key=lambda i: -len(var_cons[i]))
    full = (1 << m) - 1
    sols = []
    for lam in lams:
        for mu in mus:
            stack = [(0, 0)]
            while stack:
                ones, zeros = stack.pop()
                r = propagate(cons, ones, zeros, (lam, mu), var_cons)
                if r is None:
                    continue
                ones, zeros = r
                if ones | zeros == full:
                    if ones:
                        sols.append((lam, mu, frozenset(items[i] for i in range(m) if ones >> i & 1)))
                    continue
                i = next(i for i in order if not ((ones | zeros) >> i & 1))
                stack.append((ones, zeros | (1 << i)))
                stack.append((ones | (1 << i), zeros))
    return sols


def direct_ok(ids, Q, lam, mu):
    """evaluate every identity directly for an orientation-independent rule Q"""
    for kind, old, new in ids:
        lhs = sum(all(l in Q for _, l in n) for n in new)
        rhs = (lam if kind == 0 else mu) * all(l in Q for _, l in old)
        if lhs != rhs:
            return False
    return True


# ---------------------------------------------------------------- ordered triangulations

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


def snf_rank_and_torsion(M):
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
    d2, d1 = snf_rank_and_torsion(D2), snf_rank_and_torsion(D1)
    free = len(edges) - len(d1) - len(d2)
    torsion = sorted(d for d in d2 if d > 1)
    return free, torsion, len(verts), len(edges)


def count(T, pairing, Q):
    vd, ed, fd, verts, edges, faces = build(T, pairing)
    ei = {e: k for k, e in enumerate(edges)}
    tet = [[ei[ed.find((t, a, b))] for a, b in EDGES4] for t in range(T)]
    return sum(all(tuple(lab[k] for k in tet[t]) in Q for t in range(T)) for lab in itertools.product((0, 1), repeat=len(edges)))


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    # census
    expected, found_q, found_pm = set(), set(), set()
    named_ok, symmetric_ok, direct = True, True, True
    by_type = {}
    for mask in range(1, 256):
        R = frozenset(CUBE[i] for i in range(8) if mask >> i & 1)
        comp = compatible(R)
        cs = set(comp)
        for name, (Q, lam, mu) in SEVEN.items():
            if Q <= cs:
                expected.add((mask, name, lam, mu))
        if not comp:
            continue
        ids_q = identities(R, oriented=False)
        index = {(1, l): k for k, l in enumerate(comp)}
        for lam, mu, S in search(to_masks(ids_q, index), len(comp), [(1, l) for l in comp]):
            Q = frozenset(l for _, l in S)
            name = next((n for n, (QQ, la, m) in SEVEN.items() if QQ == Q and (la, m) == (lam, mu)), None)
            named_ok &= name is not None
            found_q.add((mask, name, lam, mu))
            by_type[name] = by_type.get(name, 0) + 1
            direct &= direct_ok(ids_q, Q, lam, mu)
        ids_pm = identities(R, oriented=True)
        items = [(s, l) for s in (1, -1) for l in comp]
        index = {it: k for k, it in enumerate(items)}
        for lam, mu, S in search(to_masks(ids_pm, index), len(items), items):
            Qp = frozenset(l for s, l in S if s == 1)
            Qm = frozenset(l for s, l in S if s == -1)
            symmetric_ok &= Qp == Qm
            name = next((n for n, (QQ, la, m) in SEVEN.items() if QQ == Qp and (la, m) == (lam, mu)), None)
            found_pm.add((mask, name, lam, mu))
    census = {"solutions, one rule for both orientations": len(found_q), "solutions, two rules": len(found_pm),
              "expected (seven laws within the compatible labellings)": len(expected),
              "every solution is one of the seven": named_ok, "the two orientations always agree": symmetric_ok,
              "solutions equal the expected laws": found_q == expected and found_pm == expected,
              "each expected law passes every identity by direct evaluation": direct,
              "solutions by type": dict(sorted(by_type.items()))}

    # sampled ordered triangulations
    rng = random.Random(20261025)
    samples, per = [], {}
    while len(samples) < 60:
        T = rng.randint(1, 4)
        faces = [(t, i) for t in range(T) for i in range(4)]
        rng.shuffle(faces)
        pairing = [(faces[k], faces[k + 1]) for k in range(0, 4 * T, 2)]
        if not is_manifold(T, pairing):
            continue
        free, tors, V, E = homology(T, pairing)
        if E > 12:
            continue
        key = (free, tuple(tors))
        if per.get(key, 0) >= 8:
            continue
        per[key] = per.get(key, 0) + 1
        samples.append((T, pairing, free, tors, V, E))
    counts_ok = True
    for T, pairing, free, tors, V, E in samples:
        h1 = 2 ** (free + sum(1 for d in tors if d % 2 == 0))
        z1 = h1 * 2 ** (V - 1)
        want = {"all 0": 1, "all 1": 1, "all equal": 2, "even cocycles": z1, "odd cocycles": z1, "even or odd": 2 * z1, "free": 2 ** E}
        for name, (Q, lam, mu) in SEVEN.items():
            counts_ok &= count(T, pairing, Q) == want[name]
    tri = {"sampled triangulations": len(samples), "homology types": sorted([list(k[:1]) + [list(k[1])] for k in per]),
           "counts equal the cocycle formulas": counts_ok}

    # controls
    S_open = frozenset(t for t in CUBE if t not in {(0, 0, 0), (0, 1, 1), (1, 0, 1)})
    comp_s = compatible(S_open)
    ids_s = identities(S_open, oriented=False)
    twisted_fails = not any(direct_ok(ids_s, frozenset(comp_s), lam, mu) for lam in (1, 2) for mu in range(1, 17))
    full = frozenset(CUBE)
    comp_f = compatible(full)
    index = {(1, l): k for k, l in enumerate(comp_f)}
    only23 = [c for c in to_masks(identities(full, oriented=False), index) if c[0] == 0]
    extra = [S for lam, mu, S in search(only23, len(comp_f), [(1, l) for l in comp_f], mus=(1,))
             if frozenset(l for _, l in S) not in {Q for Q, _, _ in SEVEN.values()}]
    even_sample = next(((free, tors, V) for T, p, free, tors, V, E in samples if free == 0 and tors and tors[0] % 2 == 0), None)
    controls = {"the full twisted rule fails some identity": twisted_fails,
                "without the 1-4 identities the search admits rules outside the seven": len(extra) > 0,
                "a sample with H_1 of even order has |H^1(M; Z2)| = 2": even_sample is not None}
    ok = (census["every solution is one of the seven"] and census["the two orientations always agree"]
          and census["solutions equal the expected laws"] and census["each expected law passes every identity by direct evaluation"]
          and len(found_q) == 354 and counts_ok and all(controls.values()))
    result["checks"] = {"census": census, "sampled triangulations": tri}
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
