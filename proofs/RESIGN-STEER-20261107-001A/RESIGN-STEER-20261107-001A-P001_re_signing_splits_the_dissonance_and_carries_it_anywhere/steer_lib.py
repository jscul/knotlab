"""Re-signing the knot sphere, for RESIGN-STEER-20261107-001A.

A knot sphere is a two-coloured triangulation T of the sphere read as in COUNT-SURFACES-20261107-001A: points are the triangles of
colour 0, lines those of colour 1, and a signing puts a bit on every side. The faces of the incidence graph are T's vertices, called
faces here. Under a signing s and an assignment x a line's corner at a face agrees when the line's two literals there are equal; the
even faces D(s) are the faces whose number of agreeing corners is even, whatever x is; a Kasteleyn signing has none.

The line-face graph H joins each line to its three faces (one edge per corner). An assignment satisfies every line of a law with
|D| = 2 exactly when its agreeing corners form a perfect matching of the lines with the faces off D (COUNT-SURFACES-20261107-001A
theorem 4; on the sphere one sign class accepts every matching, and each matching gives two complementary assignments).

What proof.md proves, and this module computes:
- `pm(D)` finds a perfect matching of H - D (Hopcroft-Karp); `count_pm(D)` counts them with a Kasteleyn determinant whose signs are
  solved on the faces of the plane graph H - D;
- `allplus_minor(u, v)` is |det| of the 0/1 line-face matrix with columns u, v deleted, and `three_colouring()` T's vertex colouring;
- `flat_state(l)` builds a state of the Kasteleyn law whose only violated line is l and which over-agrees nowhere;
- `steer(l0, t)` splits the dissonance at line l0 by one re-signing, carries the two even faces by single re-signings along
  alternating paths (each at an even face, along a line that agrees at the destination) to two faces of line t, and rejoins them
  there, with the state held fixed; it returns every intermediate tally and the signing's change, which `gauge_region` writes as the
  boundary of a set of triangles."""
import itertools
import sys
from collections import deque
from pathlib import Path

import networkx as nx
import numpy as np
from networkx.algorithms import bipartite

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/COUNT-SURFACES-20261107-001A/COUNT-SURFACES-20261107-001A-P001_the_count_reads_the_euler_characteristic"))
sys.path.insert(0, str(ROOT / "proofs/SPHERE-GROWTH-20261107-001A/SPHERE-GROWTH-20261107-001A-P001_round_spheres_need_one_hidden_bit"))
import surface_lib as SL  # noqa: E402
import seam_lib as SM  # noqa: E402


class Sphere:
    def __init__(self, S, name=None):
        K = SL.KnotSpace(S)
        assert K.chi == 2
        self.S, self.K, self.n, self.V = S, K, K.n, K.V
        self.name = name or S.name
        self.fv = [[S.vert[K.lines[i]][c] for c in range(3)] for i in range(self.n)]
        self.pt = K.pt
        self.lines_at = [[] for _ in range(self.V)]
        for i in range(self.n):
            for c in range(3):
                self.lines_at[self.fv[i][c]].append((i, c))
        self.adj = [set() for _ in range(self.V)]
        for t in range(S.nt):
            a, b, c = S.vert[t]
            for u, w in ((a, b), (b, c), (a, c)):
                self.adj[u].add(w)
                self.adj[w].add(u)
        self.s0 = K.signing(())
        assert K.even_faces(self.s0) == []
        self._dist = {}

    # ---------------------------------------------------------------------------------------------- geometry
    def corners(self):
        return [v for v in range(self.V) if len(self.lines_at[v]) == 2]

    def dist(self, t):
        """graph distances from face t in T's 1-skeleton"""
        if t not in self._dist:
            d, dq = {t: 0}, deque([t])
            while dq:
                u = dq.popleft()
                for w in self.adj[u]:
                    if w not in d:
                        d[w] = d[u] + 1
                        dq.append(w)
            self._dist[t] = d
        return self._dist[t]

    def girth_ok(self):
        """no line repeats a face and no two lines share two faces: H has no cycle of length 2 or 4"""
        seen = set()
        for i in range(self.n):
            if len(set(self.fv[i])) < 3:
                return False
            for e in itertools.combinations(sorted(self.fv[i]), 2):
                if e in seen:
                    return False
                seen.add(e)
        return True

    def side_between(self, i, u, w):
        """the side k of line i whose ends are the faces u and w"""
        cs = [c for c in range(3) if self.fv[i][c] in (u, w)]
        assert len(cs) == 2
        return 3 - cs[0] - cs[1]

    def three_colouring(self):
        """T's proper vertex 3-colouring (it exists since every vertex has even degree), by spreading over adjacent triangles"""
        S, col = self.S, [None] * self.V
        for c, v in enumerate(S.vert[0]):
            col[v] = c
        done, dq = {0}, deque([0])
        while dq:
            t = dq.popleft()
            for k in range(3):
                t2 = S.side[t][k][0]
                vs = S.vert[t2]
                free = {0, 1, 2} - {col[v] for v in vs if col[v] is not None}
                for v in vs:
                    if col[v] is None:
                        col[v] = min(free)
                        free.discard(col[v])
                assert sorted(col[v] for v in vs) == [0, 1, 2], "not 3-colourable"
                if t2 not in done:
                    done.add(t2)
                    dq.append(t2)
        return col

    # ---------------------------------------------------------------------------------------------- states and laws
    def agree(self, s, x):
        """A[i][c] = 1 when line i's corner c agrees under signing s and assignment x"""
        out = []
        for i in range(self.n):
            L = [x[self.pt[i][k]] ^ s[3 * i + k] for k in range(3)]
            out.append([int(L[(c + 1) % 3] == L[(c + 2) % 3]) for c in range(3)])
        return out

    def tally(self, s, x):
        """(violated lines, agreeing corners per face, even faces, E = sum of floor(agree / 2))"""
        A = self.agree(s, x)
        viol = [i for i in range(self.n) if sum(A[i]) == 3]
        ag = [0] * self.V
        for i in range(self.n):
            for c in range(3):
                ag[self.fv[i][c]] += A[i][c]
        return viol, ag, self.K.even_faces(s), sum(a // 2 for a in ag)

    # ---------------------------------------------------------------------------------------------- matchings
    def pm(self, D):
        """a perfect matching of H - D as {line: face}, or None (always None unless D leaves exactly n faces)"""
        if self.V - len(set(D)) != self.n:
            return None
        G = nx.Graph()
        tops = [("l", i) for i in range(self.n)]
        G.add_nodes_from(tops)
        for i in range(self.n):
            for v in self.fv[i]:
                if v not in D:
                    G.add_edge(("l", i), ("f", v))
        M = bipartite.hopcroft_karp_matching(G, top_nodes=tops)
        if sum(1 for u in M if u[0] == "l") != self.n:
            return None
        return {i: M[("l", i)][1] for i in range(self.n)}

    def count_pm(self, D):
        """log of the number of perfect matchings of H - D (-inf when there is none): Kasteleyn signs solved over F2 on every face of
        the plane graph H - D but its longest (a face of length 2d gets sign product (-1)^(d+1)), then log |det|"""
        D = set(D)
        G = nx.Graph()
        for i in range(self.n):
            for v in self.fv[i]:
                if v not in D:
                    G.add_edge(("l", i), ("f", v))
        ok, emb = nx.check_planarity(G)
        assert ok
        seen, faces = set(), []
        for u, w in emb.edges():
            if (u, w) not in seen:
                faces.append(emb.traverse_face(u, w, mark_half_edges=seen))
        edges = list(G.edges())
        eidx = {frozenset(e): k for k, e in enumerate(edges)}
        faces.sort(key=len)
        rows, rhs = [], []
        for f in faces[:-1]:
            r = 0
            for j in range(len(f)):
                r ^= 1 << eidx[frozenset((f[j], f[(j + 1) % len(f)]))]
            rows.append(r)
            rhs.append((len(f) // 2 + 1) % 2)
        sol = SL.solve_f2(rows, rhs, len(edges))
        assert sol is not None
        fs = sorted(v for v in range(self.V) if v not in D)
        fi = {v: j for j, v in enumerate(fs)}
        M = np.zeros((self.n, len(fs)))
        for k, (a, b) in enumerate(edges):
            if a[0] != "l":
                a, b = b, a
            M[a[1], fi[b[1]]] = -1.0 if (sol >> k) & 1 else 1.0
        sign, logdet = np.linalg.slogdet(M)
        return float("-inf") if sign == 0 else float(logdet)

    def incidence(self):
        B = np.zeros((self.n, self.V))
        for i in range(self.n):
            for v in self.fv[i]:
                B[i, v] = 1.0
        return B

    def allplus_minor(self, u, v, B=None):
        B = self.incidence() if B is None else B
        keep = [w for w in range(self.V) if w not in (u, v)]
        return abs(np.linalg.det(B[:, keep]))

    def closed_form_logN(self):
        """log N(T) from N(T)^2 = det(B B^T) / e2(n0, n1, n2), the n_i being the sizes of T's three colour classes"""
        B = self.incidence()
        col = self.three_colouring()
        ns = [col.count(c) for c in range(3)]
        e2 = ns[0] * ns[1] + ns[1] * ns[2] + ns[0] * ns[2]
        sign, ld = np.linalg.slogdet(B @ B.T)
        assert sign > 0
        return 0.5 * (ld - np.log(e2)), ns

    # ---------------------------------------------------------------------------------------------- flat states and steering
    def split_signing(self, l):
        """the Kasteleyn signing with one side of line l flipped, and that side's two faces"""
        a, b, _ = self.fv[l]
        s = list(self.s0)
        s[3 * l + self.side_between(l, a, b)] ^= 1
        return s, (a, b)

    def flat_state(self, l, M=None):
        """a state of the Kasteleyn law with exactly one violated line, l, and no over-agreeing face: a perfect matching of H minus two
        faces of l sends l to its third face; read it as the agreeing corners of the law with that side of l flipped, and flip back"""
        s, (a, b) = self.split_signing(l)
        M = self.pm({a, b}) if M is None else M
        assert M is not None and M[l] == self.fv[l][2]
        x = self.K.assignment_from([self.fv[i].index(M[i]) for i in range(self.n)], s)
        assert x is not None
        viol, ag, D, E = self.tally(self.s0, x)
        assert viol == [l] and E == 0 and D == []
        return x

    def matching_of(self, s, x):
        """the face each line agrees at, when every line is satisfied"""
        A = self.agree(s, x)
        out = {}
        for i in range(self.n):
            cs = [c for c in range(3) if A[i][c]]
            if len(cs) != 1:
                return None
            out[i] = self.fv[i][cs[0]]
        return out

    def alternating_path(self, match, h, goal, avoid):
        """a shortest walk of the even face h to goal, each step along a line at the current face that agrees at the next one"""
        prev, dq = {h: None}, deque([h])
        while dq:
            u = dq.popleft()
            if u == goal:
                break
            for (i, _) in self.lines_at[u]:
                w = match[i]
                if w != u and w not in prev and w != avoid:
                    prev[w] = (u, i)
                    dq.append(w)
        if goal not in prev:
            return None
        path, w = [], goal
        while prev[w] is not None:
            u, i = prev[w]
            path.append((u, i, w))
            w = u
        return path[::-1]

    def steer(self, l0, t, x=None):
        """split at l0, carry both even faces to two faces of line t, rejoin there; the state x never changes. Returns (signing,
        state, tallies after each re-signing, number of re-signings, every re-signed side was at a dissonance)"""
        x = self.flat_state(l0) if x is None else x
        s = list(self.s0)
        tallies, local = [], True
        viol, _, D, E = self.tally(s, x)
        assert viol == [l0] and D == [] and E == 0

        def resign(i, k):
            nonlocal local
            ends = [self.fv[i][(k + 1) % 3], self.fv[i][(k + 2) % 3]]
            viol, _, D, _ = self.tally(s, x)
            local &= (i in viol) or any(e in D for e in ends)
            s[3 * i + k] ^= 1
            tallies.append(self.tally(s, x))

        a, b, _ = self.fv[l0]
        resign(l0, self.side_between(l0, a, b))
        holes, tv = [a, b], self.fv[t]
        on = [h for h in holes if h in tv]
        if len(on) == 2:
            goals = holes[:]
        elif len(on) == 1:
            j = holes.index(on[0])
            goals = [None, None]
            goals[j], goals[1 - j] = on[0], next(v for v in tv if v != on[0])
        else:
            goals = [tv[0], tv[1]]
        for j in (0, 1):
            if holes[j] == goals[j]:
                continue
            match = self.matching_of(s, x)
            path = self.alternating_path(match, holes[j], goals[j], holes[1 - j])
            assert path is not None, "unreachable"
            for (u, i, w) in path:
                resign(i, self.side_between(i, u, w))
            holes[j] = goals[j]
        resign(t, self.side_between(t, holes[0], holes[1]))
        return s, x, tallies, len(tallies), local

    def gauge_region(self, s):
        """write s - s0 (a cycle of T's 1-skeleton when D(s) is empty) as the boundary of a set of triangles: returns the points and
        lines of that set, or None"""
        z = [a ^ b for a, b in zip(s, self.s0)]
        # triangle boundaries as bit rows over the 3n sides (B-edges): a point's three sides, a line's three sides
        rows = []
        for p in range(self.n):
            r = 0
            for e in self.K.point_sides[p]:
                r ^= 1 << e
            rows.append(r)
        for i in range(self.n):
            rows.append(0b111 << (3 * i))
        # solve sum_j c_j rows_j = z over F2: one equation per side, one unknown per triangle
        cols = [sum(((rows[j] >> e) & 1) << j for j in range(2 * self.n)) for e in range(3 * self.n)]
        sol = SL.solve_f2(cols, z, 2 * self.n)
        if sol is None:
            return None
        pts = [p for p in range(self.n) if (sol >> p) & 1]
        lns = [i for i in range(self.n) if (sol >> (self.n + i)) & 1]
        return pts, lns


# -------------------------------------------------------------------------------------------------- test spheres
def octahedral(m):
    return Sphere(SL.octahedral_sphere(m), f"K_{m}")


def test_spheres(rng, grown=3, grown_min=60):
    """octahedral K_2..K_4, two tubes, grown spheres and branched double covers of K_2 and K_3 (vertex degrees 8 and 12)"""
    out = [octahedral(m) for m in (2, 3, 4)]
    out += [Sphere(SM.tube(*p), "tube%s" % (p,)) for p in ((2, 5, 1), (3, 7, 2))]
    got = 0
    while got < grown:
        S = SM.random_sphere(rng, 0.2, 120)
        if S is not None and S.nt >= grown_min:
            out.append(Sphere(S, "grown%d" % S.nt))
            got += 1
    for m in (2, 3):
        K = octahedral(m)
        cor = K.corners()
        reg = [v for v in range(K.V) if len(K.lines_at[v]) == 3]
        out.append(Sphere(SL.double_cover(K.S, [cor[0], cor[1]]), f"cover(K_{m}; 2 corners)"))
        out.append(Sphere(SL.double_cover(K.S, [cor[0], reg[0]]), f"cover(K_{m}; corner+regular)"))
    return out
