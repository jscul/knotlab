#!/usr/bin/env python3
"""Check of HUB-DIMENSION-20261024-001A-P001 (standard library only, seed 20261024).

Laws: bits on the edges of a triangulation; a symmetric rule W on the number of 1-edges of each triangle and a symmetric rule Q on the
class of each tetrahedron's edge labelling under the 24 symmetries of the tetrahedron (11 classes). A law is a 15-bit mask (4 bits for
W, 11 for Q); its count on a triangulation is the number of edge labellings satisfying every triangle and every tetrahedron.
Checks:
- local census: for all 32,768 masks, the 2-3 identity (for every labelling of the 9 boundary edges with allowed boundary triangles,
  the 3-tetrahedron side sums to a fixed multiple lambda of the 2-tetrahedron side) and the 1-4 identity (fixed multiple mu); the
  masks passing both with some allowed configuration reduce to seven sets of allowed tetrahedron classes: all 0, all 1, all equal,
  free, even parity, odd parity, even or odd;
- global certificates: random sequences of 2-3 and 1-4 moves on singular triangulations, starting from the one-tetrahedron
  triangulations of the sphere, L(4,1) and L(5,2); every mask passing the local identities keeps one ratio per move kind on every
  sampled move, and every other mask that is ever allowed breaks on some sampled move;
- parity: on every sampled triangulation the even-parity count is 2^(dim H^1(M; Z/2) + V - 1), with H^1 computed by linear algebra
  and H_1 by Smith normal form (the moves keep H_1);
- native networks: the one-tetrahedron triangulations of the sphere and of L(4,1) with face pairing (0,1)(2,3) have the same native
  network (bits on faces, one four-place rule with slots 0,1 and 2,3 sharing a bit), so every face law counts them equally, while the
  edge-parity counts are 1 and 2;
- the Fibonacci rule (no triangle with exactly one 1-edge) fails the 2-3 identity: with every boundary edge 1 the sides are 1 and 2.
Controls: dropping the interior edge's sum from the 2-3 identity rejects parity; comparing the sphere with L(4,1) as if one move related
them breaks parity's ratio; replacing 2^(dim H^1 + V - 1) by 2^V disagrees with the parity counts.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------- singular triangulations


def perm_sign(p):
    p = list(p); s = 1
    for i in range(len(p)):
        while p[i] != i:
            j = p[i]; p[i], p[j] = p[j], p[i]; s = -s
    return s

class UF:
    def __init__(self): self.p = {}
    def find(self, a):
        self.p.setdefault(a, a)
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]; a = self.p[a]
        return a
    def union(self, a, b): self.p[self.find(a)] = self.find(b)

class Tri:
    """n tetrahedra; glue[(t, f)] = (t2, f2, perm) with perm a tuple of length 4 mapping vertices of t to vertices of t2, perm[f] = f2."""
    def __init__(self, n, gluings):
        self.n = n
        self.glue = {}
        for (t, f), (t2, f2, perm) in gluings.items():
            self.glue[(t, f)] = (t2, f2, tuple(perm))
            inv = [0] * 4
            for a, b in enumerate(perm): inv[b] = a
            self.glue[(t2, f2)] = (t, f, tuple(inv))
        assert len(self.glue) == 4 * n, "every face must be glued"
        self.classes()

    def classes(self):
        uv = UF()
        for t in range(self.n):
            for v in range(4): uv.find((t, v))
        for (t, f), (t2, f2, p) in self.glue.items():
            for v in range(4):
                if v != f: uv.union((t, v), (t2, p[v]))
        vroots = sorted({uv.find((t, v)) for t in range(self.n) for v in range(4)})
        self.vid = {(t, v): vroots.index(uv.find((t, v))) for t in range(self.n) for v in range(4)}
        self.V = len(vroots)
        # oriented edges: node (t, a, b) with a < b, identified by gluings with an orientation flag
        nodes = [(t, a, b) for t in range(self.n) for a, b in itertools.combinations(range(4), 2)]
        adj = {x: [] for x in nodes}
        for (t, f), (t2, f2, p) in self.glue.items():
            for a, b in itertools.combinations([v for v in range(4) if v != f], 2):
                c, d = p[a], p[b]
                o = 0
                if c > d: c, d, o = d, c, 1
                adj[(t, a, b)].append(((t2, c, d), o))
        self.eid, self.eor = {}, {}
        self.bad_edge = False
        k = 0
        for x in nodes:
            if x in self.eid: continue
            self.eid[x], self.eor[x] = k, 0
            stack = [x]
            while stack:
                y = stack.pop()
                for z, o in adj[y]:
                    oz = self.eor[y] ^ o
                    if z in self.eid:
                        if self.eor[z] != oz: self.bad_edge = True
                    else:
                        self.eid[z], self.eor[z] = k, oz; stack.append(z)
            k += 1
        self.E = k
        # faces: one class per glued pair
        fset = []
        seen = set()
        for (t, f) in sorted(self.glue):
            if (t, f) in seen: continue
            t2, f2, p = self.glue[(t, f)]
            seen.add((t, f)); seen.add((t2, f2)); fset.append((t, f))
        self.faces = fset
        self.F = len(fset)
        self.T = self.n

    def orientable(self):
        # 2-colour tetrahedra so that every gluing perm has sign -(colour product)
        col = {0: 1}; stack = [0]
        while stack:
            t = stack.pop()
            for f in range(4):
                t2, f2, p = self.glue[(t, f)]
                need = -col[t] * perm_sign(p)
                if t2 in col:
                    if col[t2] != need: return False
                else:
                    col[t2] = need; stack.append(t2)
        return True

    def edge_of(self, t, a, b):
        """(edge class, sign) of the oriented edge a->b in tetrahedron t"""
        lo, hi = min(a, b), max(a, b)
        e, o = self.eid[(t, lo, hi)], self.eor[(t, lo, hi)]
        s = 1 if (a < b) else -1
        return e, s * (1 if o == 0 else -1)

    def vertex_links_spheres(self):
        corners = {}
        for t in range(self.n):
            for v in range(4): corners.setdefault(self.vid[(t, v)], []).append((t, v))
        ends = {i: 0 for i in range(self.V)}
        # edge ends at vertex class: count each edge class end (with multiplicity) once per edge class
        rep = {}
        for t in range(self.n):
            for a, b in itertools.combinations(range(4), 2):
                e = self.eid[(t, a, b)]
                if e not in rep: rep[e] = (t, a, b)
        for e, (t, a, b) in rep.items():
            ends[self.vid[(t, a)]] += 1; ends[self.vid[(t, b)]] += 1
        return all(ends[i] - len(corners[i]) / 2 == 2 for i in range(self.V))

    def is_closed_orientable_manifold(self):
        return (not self.bad_edge) and self.orientable() and self.vertex_links_spheres()

    def face_edges(self, t, f):
        vs = [v for v in range(4) if v != f]
        return [self.edge_of(t, vs[0], vs[1]), self.edge_of(t, vs[1], vs[2]), self.edge_of(t, vs[0], vs[2])]

    def boundary2(self):
        """integer matrix E x F of the boundary of faces (orientation from the face's vertex order)"""
        M = [[0] * self.F for _ in range(self.E)]
        for j, (t, f) in enumerate(self.faces):
            vs = [v for v in range(4) if v != f]
            for (a, b), s in (((vs[0], vs[1]), 1), ((vs[1], vs[2]), 1), ((vs[0], vs[2]), -1)):
                e, o = self.edge_of(t, a, b)
                M[e][j] += s * o
        return M

    def boundary1(self):
        M = [[0] * self.E for _ in range(self.V)]
        done = set()
        for t in range(self.n):
            for a, b in itertools.combinations(range(4), 2):
                e, o = self.edge_of(t, a, b)
                if e in done: continue
                done.add(e)
                tail, head = (a, b) if o == 1 else (b, a)
                M[self.vid[(t, head)]][e] += 1; M[self.vid[(t, tail)]][e] -= 1
        return M

def smith_diagonal(M):
    """invariant factors of an integer matrix (list of lists)"""
    A = [row[:] for row in M]
    m = len(A); n = len(A[0]) if m else 0
    diag = []
    r = 0
    for c in range(n):
        if r >= m: break
        # bring a nonzero pivot of minimal absolute value into (r, c) working on the submatrix A[r:, c:]
        while True:
            piv = None
            for i in range(r, m):
                for j in range(c, n):
                    if A[i][j] != 0 and (piv is None or abs(A[i][j]) < abs(A[piv[0]][piv[1]])):
                        piv = (i, j)
            if piv is None:
                return diag
            i, j = piv
            A[r], A[i] = A[i], A[r]
            for row in A: row[c], row[j] = row[j], row[c]
            done = True
            for i in range(r + 1, m):
                q = A[i][c] // A[r][c]
                if q:
                    A[i] = [x - q * y for x, y in zip(A[i], A[r])]
                if A[i][c] != 0: done = False
            for j in range(c + 1, n):
                q = A[r][j] // A[r][c]
                if q:
                    for row in A: row[j] -= q * row[c]
                if A[r][j] != 0: done = False
            if done:
                # divisibility fix
                bad = None
                for i in range(r + 1, m):
                    for j in range(c + 1, n):
                        if A[i][j] % A[r][c] != 0: bad = (i, j)
                if bad is None:
                    diag.append(abs(A[r][c])); r += 1; break
                A[r] = [x + y for x, y in zip(A[r], A[bad[0]])]
    return diag

def rank_mod2(M):
    rows = [int("".join(str(x % 2) for x in row), 2) if row else 0 for row in M]
    rank = 0
    width = len(M[0]) if M else 0
    for bit in reversed(range(width)):
        piv = next((i for i, r in enumerate(rows) if r >> bit & 1), None)
        if piv is None: continue
        pr = rows.pop(piv); rank += 1
        rows = [r ^ pr if r >> bit & 1 else r for r in rows]
    return rank

def homology1(tri):
    d2 = tri.boundary2(); d1 = tri.boundary1()
    inv = smith_diagonal(d2)
    r1 = len(smith_diagonal(d1))
    free = (tri.E - r1) - len(inv)
    torsion = sorted(x for x in inv if x > 1)
    return free, torsion

def h1_mod2_dim(tri):
    d2 = tri.boundary2(); d1 = tri.boundary1()
    return (tri.E - rank_mod2(d1)) - rank_mod2(d2)

def one_tet_gluings():
    out = []
    for pairing in (((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))):
        maps = []
        for fa, fb in pairing:
            va = [v for v in range(4) if v != fa]; vb = [v for v in range(4) if v != fb]
            opts = []
            for img in itertools.permutations(vb):
                p = [None] * 4; p[fa] = fb
                for a, b in zip(va, img): p[a] = b
                opts.append(tuple(p))
            maps.append(opts)
        for p1 in maps[0]:
            for p2 in maps[1]:
                out.append((pairing, {(0, pairing[0][0]): (0, pairing[0][1], p1), (0, pairing[1][0]): (0, pairing[1][1], p2)}))
    return out

# ---------------------------------------------------------------- Pachner moves on gluing data
def gluing_dict(tri):
    return {k: v for k, v in tri.glue.items()}

def move14(tri, t):
    """replace tetrahedron t by four, around a new vertex. New tets: t (reused as child 0) and n, n+1, n+2."""
    n = tri.n
    child = {0: t, 1: n, 2: n + 1, 3: n + 2}   # child i has the new vertex at position i
    g = {}
    old = tri.glue
    def outer(tt, ff):
        """where face ff of old tet tt now lives: (tet, face)"""
        return (child[ff], ff) if tt == t else (tt, ff)
    for (tt, ff), (t2, f2, p) in old.items():
        a = outer(tt, ff); b = outer(t2, f2)
        g[a] = (b[0], b[1], p)
    for i in range(4):
        for j in range(4):
            if i < j:
                p = [None] * 4
                for k in range(4):
                    p[k] = k
                p[i], p[j] = j, i
                g[(child[i], j)] = (child[j], i, tuple(p))
                inv = list(range(4)); inv[j], inv[i] = i, j
                g[(child[j], i)] = (child[i], j, tuple(inv))
    return Tri(n + 3, g)

def move23(tri, t1, f1):
    """2-3 move across face f1 of tet t1 (glued to a different tet t2). Returns None if t2 == t1."""
    t2, f2, p = tri.glue[(t1, f1)]
    if t2 == t1:
        return None
    face = [v for v in range(4) if v != f1]
    n = tri.n
    # new tets: N_c for c in face; reuse t1 for N_face[0], t2 for N_face[1], new index n for N_face[2]
    idx = {face[0]: t1, face[1]: t2, face[2]: n}
    pos = {}   # pos[c] = dict: label -> position in N_c ; labels: ('A') apex1, ('B') apex2, t1-vertex labels for face vertices
    for c in face:
        x, y = [v for v in face if v != c]
        pos[c] = {"A": 0, "B": 1, x: 2, y: 3}
    # map old faces to new (tet, face, relabel map old-vertex -> new position)
    newface = {}
    for c in face:
        x, y = [v for v in face if v != c]
        # t1's face opposite c: vertices f1 (apex1), x, y -> N_c face opposite position 1
        newface[(t1, c)] = (idx[c], 1, {f1: 0, x: 2, y: 3, c: 1})
        # t2's face opposite p[c]: vertices f2 (apex2), p[x], p[y] -> N_c face opposite position 0
        newface[(t2, p[c])] = (idx[c], 0, {f2: 1, p[x]: 2, p[y]: 3, p[c]: 0})
    g = {}
    for (ta, fa), (tb, fb, q) in tri.glue.items():
        if (ta, fa) in ((t1, f1), (t2, f2)):
            continue
        if (ta, fa) in newface:
            na, nfa, ma = newface[(ta, fa)]
        else:
            na, nfa, ma = ta, fa, {v: v for v in range(4)}
        if (tb, fb) in newface:
            nb, nfb, mb = newface[(tb, fb)]
        else:
            nb, nfb, mb = tb, fb, {v: v for v in range(4)}
        inv_a = {v: k for k, v in ma.items()}
        r = [None] * 4
        for k in range(4):
            r[k] = mb[q[inv_a[k]]]
        g[(na, nfa)] = (nb, nfb, tuple(r))
    for c in face:
        x, y = [v for v in face if v != c]
        for excl, keep in ((x, y), (y, x)):
            # N_c face opposite the position of `excl` (vertices A, B, keep) is shared with N_excl, opposite the position of c there
            other = excl
            r = [None] * 4
            r[0], r[1] = 0, 1
            r[pos[c][keep]] = pos[other][keep]
            r[pos[c][excl]] = pos[other][c]
            g[(idx[c], pos[c][excl])] = (idx[other], pos[other][c], tuple(r))
    return Tri(n + 1, g)

def tet_edges(tri, t):
    """edge classes of the six edges of tet t in the order (01, 02, 03, 12, 13, 23)"""
    return [tri.eid[(t, a, b)] for a, b in itertools.combinations(range(4), 2)]

# ---------------------------------------------------------------- tetrahedron classes and the local identities
E4 = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]


def canon(bits6):
    best = None
    for p in itertools.permutations(range(4)):
        lab = {frozenset(e): b for e, b in zip(E4, bits6)}
        key = tuple(lab[frozenset((p[a], p[b]))] for a, b in E4)
        best = key if best is None or key < best else best
    return best


CLASSES = sorted({canon(b) for b in itertools.product((0, 1), repeat=6)})
CIDX = {c: i for i, c in enumerate(CLASSES)}
PAT = [CIDX[canon(tuple(b >> k & 1 for k in range(6)))] for b in range(64)]
NB = 4 + len(CLASSES)


def class_faces(c):
    lab = {frozenset(e): b for e, b in zip(E4, c)}
    return [lab[frozenset((a, b))] + lab[frozenset((a, d))] + lab[frozenset((b, d))] for a, b, d in itertools.combinations(range(4), 3)]


def tet_class(lab, verts):
    return PAT[sum(lab[frozenset((verts[a], verts[b]))] << k for k, (a, b) in enumerate(E4))]


def tri_w(lab, a, b, c):
    return lab[frozenset((a, b))] + lab[frozenset((a, c))] + lab[frozenset((b, c))]


def move_cases():
    eq = [1, 2, 3]
    bd = [frozenset(e) for e in [(1, 2), (1, 3), (2, 3), ("a", 1), ("a", 2), ("a", 3), ("b", 1), ("b", 2), ("b", 3)]]
    btri = [("a", 1, 2), ("a", 1, 3), ("a", 2, 3), ("b", 1, 2), ("b", 1, 3), ("b", 2, 3)]
    c23 = []
    for bits in itertools.product((0, 1), repeat=9):
        lab = dict(zip(bd, bits))
        bt = tuple(tri_w(lab, *t) for t in btri)
        lhs = (tri_w(lab, 1, 2, 3), tet_class(lab, ["a", 1, 2, 3]), tet_class(lab, ["b", 1, 2, 3]))
        rhs = []
        for x in (0, 1):
            lab[frozenset(("a", "b"))] = x
            rhs.append((tuple(tri_w(lab, "a", "b", v) for v in eq),
                        tuple(tet_class(lab, ["a", "b", u, v]) for u, v in ((1, 2), (2, 3), (1, 3)))))
        del lab[frozenset(("a", "b"))]
        c23.append((bt, lhs, rhs))
    bd4 = [frozenset(e) for e in itertools.combinations([1, 2, 3, 4], 2)]
    c14 = []
    for bits in itertools.product((0, 1), repeat=6):
        lab = dict(zip(bd4, bits))
        bt = tuple(tri_w(lab, *t) for t in itertools.combinations([1, 2, 3, 4], 3))
        lhs = tet_class(lab, [1, 2, 3, 4])
        rhs = []
        for nb in itertools.product((0, 1), repeat=4):
            for v, x in zip([1, 2, 3, 4], nb):
                lab[frozenset((0, v))] = x
            rhs.append((tuple(tri_w(lab, 0, u, v) for u, v in itertools.combinations([1, 2, 3, 4], 2)),
                        tuple(tet_class(lab, [0] + [w for w in [1, 2, 3, 4] if w != s]) for s in [1, 2, 3, 4])))
        c14.append((bt, lhs, rhs))
    return c23, c14


def local_check(mask, c23, c14, drop_interior_sum=False):
    """(lambda, mu) if the law passes both identities with some allowed configuration; 'vacuous' if no configuration is ever
    allowed on either side; None if it fails"""
    Wt = {w for w in range(4) if mask >> w & 1}
    Q = {i for i in range(len(CLASSES)) if mask >> (4 + i) & 1}
    ratios = []
    for cases, kind in ((c23, "23"), (c14, "14")):
        r = None
        for bt, lhs, rhs in cases:
            if not all(w in Wt for w in bt):
                continue
            if kind == "23":
                L = int(lhs[0] in Wt and lhs[1] in Q and lhs[2] in Q)
                terms = rhs[:1] if drop_interior_sum else rhs
            else:
                L = int(lhs in Q)
                terms = rhs
            R = sum(1 for tris, tets in terms if all(w in Wt for w in tris) and all(t in Q for t in tets))
            if L == 0:
                if R:
                    return None
                continue
            if r is None:
                r = Fraction(R, L)
            elif r != Fraction(R, L):
                return None
        ratios.append(r)
    if ratios[0] is None or ratios[1] is None:
        return "vacuous"
    return tuple(ratios)


def law_counts(T):
    faces = [[e for e, _ in T.face_edges(t, f)] for (t, f) in T.faces]
    tets = [tet_edges(T, t) for t in range(T.n)]
    hist = {}
    for bits in range(1 << T.E):
        wm = 0
        for es in faces:
            wm |= 1 << ((bits >> es[0] & 1) + (bits >> es[1] & 1) + (bits >> es[2] & 1))
        qm = 0
        for es in tets:
            qm |= 1 << PAT[sum((bits >> e & 1) << k for k, e in enumerate(es))]
        key = wm | (qm << 4)
        hist[key] = hist.get(key, 0) + 1
    f = [0] * (1 << NB)
    for k, c in hist.items():
        f[k] += c
    for i in range(NB):
        b = 1 << i
        for m in range(1 << NB):
            if m & b:
                f[m] += f[m ^ b]
    return f


def mask_of(W, Q):
    return sum(1 << w for w in W) | sum(1 << (4 + i) for i in Q)


def even_parity_mask():
    return mask_of({0, 2}, {i for i, c in enumerate(CLASSES) if all(x % 2 == 0 for x in class_faces(c))})


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    rng = random.Random(20261024)
    c23, c14 = move_cases()
    local = {m: local_check(m, c23, c14) for m in range(1 << NB)}
    invariant = {m for m, r in local.items() if isinstance(r, tuple)}
    vacuous = {m for m, r in local.items() if r == "vacuous"}
    # effective content: allowed tetrahedron classes whose faces obey the triangle rule
    eff = {}
    for m in invariant:
        Wt = {w for w in range(4) if m >> w & 1}
        Q = frozenset(i for i in range(len(CLASSES)) if m >> (4 + i) & 1 and all(f in Wt for f in class_faces(CLASSES[i])))
        eff.setdefault(Q, set()).add(local[m])
    named = {
        "all edges 0": frozenset({CIDX[(0,) * 6]}),
        "all edges 1": frozenset({CIDX[(1,) * 6]}),
        "all edges equal": frozenset({CIDX[(0,) * 6], CIDX[(1,) * 6]}),
        "free": frozenset(range(len(CLASSES))),
        "even parity": frozenset(i for i, c in enumerate(CLASSES) if all(x % 2 == 0 for x in class_faces(c))),
        "odd parity": frozenset(i for i, c in enumerate(CLASSES) if all(x % 2 == 1 for x in class_faces(c))),
        "even or odd": frozenset(i for i, c in enumerate(CLASSES) if len({x % 2 for x in class_faces(c)}) == 1),
    }
    census = {"laws (masks)": 1 << NB, "passing both identities": len(invariant), "never allowed": len(vacuous),
              "failing": (1 << NB) - len(invariant) - len(vacuous),
              "distinct sets of allowed tetrahedron classes among the passing laws": len(eff),
              "they are exactly the seven named laws": set(eff) == set(named.values()),
              "ratios (lambda, mu) per named law": {k: [str(x) for x in sorted(eff[v])[0]] for k, v in named.items()}}
    # global certificates on singular triangulations
    base = {}
    for pairing, g in one_tet_gluings():
        T = Tri(1, g)
        if T.is_closed_orientable_manifold():
            free, tors = homology1(T)
            base.setdefault((free, tuple(tors), T.V), T)
    pairs, parity_ok, h1_stable, parity_checked = [], True, True, 0
    parity_wrong_formula = False
    pm = even_parity_mask()
    for key in sorted(base):
        T0 = base[key]
        for walk in range(4):
            cur, ccur = T0, law_counts(T0)
            for step in range(5):
                if cur.n == 1 or rng.random() < 0.3:
                    nxt, kind = move14(cur, rng.randrange(cur.n)), "14"
                else:
                    opts = [(t, f) for t in range(cur.n) for f in range(4) if cur.glue[(t, f)][0] != t]
                    nxt, kind = move23(cur, *rng.choice(opts)), "23"
                if nxt.E > 13:
                    break
                assert nxt.is_closed_orientable_manifold()
                cn = law_counts(nxt)
                pairs.append((kind, ccur, cn))
                h1_stable &= homology1(nxt) == homology1(T0)
                d = h1_mod2_dim(nxt)
                parity_ok &= cn[pm] == 2 ** (d + nxt.V - 1)
                parity_wrong_formula |= cn[pm] != 2 ** nxt.V
                parity_checked += 1
                cur, ccur = nxt, cn
    def consistent(m, pp):
        rat = {}
        seen = False
        for kind, a, b in pp:
            x, y = a[m], b[m]
            if x == 0 and y == 0:
                continue
            seen = True
            if x == 0 or y == 0:
                return False, seen
            r = Fraction(y, x)
            if rat.setdefault(kind, r) != r:
                return False, seen
        return True, seen
    glob = {m: consistent(m, pairs) for m in range(1 << NB)}
    certificates = {
        "sampled moves": len(pairs),
        "2-3 moves": sum(k == "23" for k, _, _ in pairs), "1-4 moves": sum(k == "14" for k, _, _ in pairs),
        "passing laws keep one ratio per move kind": all(glob[m][0] for m in invariant),
        "failing laws that are ever allowed break on some sampled move":
            all(not glob[m][0] for m in range(1 << NB) if m not in invariant and m not in vacuous and glob[m][1]),
        "failing laws never allowed on the sample": sum(1 for m in range(1 << NB) if m not in invariant and m not in vacuous
                                                        and not glob[m][1]),
        "laws never allowed by the identities are never allowed on the sample": all(not glob[m][1] for m in vacuous),
        "moves keep H_1": h1_stable,
    }
    parity = {"sampled triangulations": parity_checked, "count = 2^(dim H^1 + V - 1) on all": parity_ok}
    # native networks: same face pairing, sphere and L(4,1)
    picks = {}
    for pairing, g in one_tet_gluings():
        if pairing != ((0, 1), (2, 3)):
            continue
        T = Tri(1, g)
        if T.is_closed_orientable_manifold() and T.V == 1:
            picks.setdefault(tuple(homology1(T)[1]), (T, g))
    S3, L41 = picks[()][0], picks[(4,)][0]
    def native_network(T):
        """slots of the one four-place rule paired by face gluings"""
        return sorted(tuple(sorted((f, T.glue[(0, f)][1]))) for f in range(4))
    def face_law_count(T, R):
        pairs_ = native_network(T)
        cnt = 0
        for bits in itertools.product((0, 1), repeat=len(set(pairs_))):
            val = [None] * 4
            for (a, b), x in zip(sorted(set(pairs_)), bits):
                val[a] = val[b] = x
            cnt += tuple(val) in R
        return cnt
    four = list(itertools.product((0, 1), repeat=4))
    face_laws = [frozenset(t for t in four if sum(t) in Ws) for Ws in
                 (set(w for w in range(5) if mm >> w & 1) for mm in range(32))]
    native = {"native networks of the sphere and L(4,1) coincide": native_network(S3) == native_network(L41),
              "every symmetric face law counts them equally": all(face_law_count(S3, R) == face_law_count(L41, R) for R in face_laws),
              "edge-parity counts (sphere, L(4,1))": [law_counts(S3)[pm], law_counts(L41)[pm]],
              "H_1 (sphere, L(4,1))": [str(homology1(S3)), str(homology1(L41))]}
    fib_W = {0, 2, 3}
    fib_Q = {i for i, c in enumerate(CLASSES) if all(f in fib_W for f in class_faces(c))}
    allone = [case for case in c23 if all(w == 3 for w in case[0]) and case[1][0] == 3]
    bt, lhs, rhs = allone[0]
    fib = {"Fibonacci rule fails the identities": local_check(mask_of(fib_W, fib_Q), c23, c14) is None,
           "all-ones boundary: 2-tetrahedron side, 3-tetrahedron side": [
               int(lhs[0] in fib_W and lhs[1] in fib_Q and lhs[2] in fib_Q),
               sum(1 for tris, tets in rhs if all(w in fib_W for w in tris) and all(t in fib_Q for t in tets))],
           "Fibonacci rule breaks on some sampled move": not glob[mask_of(fib_W, fib_Q)][0]}
    controls = {
        "dropping the interior edge's sum rejects parity": local_check(pm, c23, c14, drop_interior_sum=True) is None,
        "comparing the sphere with L(4,1) as one move breaks parity's ratio":
            not consistent(pm, pairs + [("23", law_counts(S3), law_counts(L41))])[0],
        "2^V instead of 2^(dim H^1 + V - 1) disagrees with parity": parity_wrong_formula,
    }
    ok = (census["they are exactly the seven named laws"] and census["passing both identities"] > 0
          and all(v for k, v in certificates.items() if isinstance(v, bool))
          and certificates["failing laws never allowed on the sample"] == 0
          and parity["count = 2^(dim H^1 + V - 1) on all"]
          and native["native networks of the sphere and L(4,1) coincide"] and native["every symmetric face law counts them equally"]
          and native["edge-parity counts (sphere, L(4,1))"] == [1, 2]
          and fib["Fibonacci rule fails the identities"] and fib["all-ones boundary: 2-tetrahedron side, 3-tetrahedron side"] == [1, 2]
          and fib["Fibonacci rule breaks on some sampled move"] and all(controls.values()))
    result["checks"] = {"local census": census, "global certificates": certificates, "parity": parity, "native networks": native,
                        "Fibonacci rule": fib}
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
