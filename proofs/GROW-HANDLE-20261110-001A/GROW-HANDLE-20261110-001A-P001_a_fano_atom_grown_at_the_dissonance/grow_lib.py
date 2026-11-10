"""Learning that grows a handle, for GROW-HANDLE-20261110-001A.

A knot space is read off a two-coloured triangulation (surface_lib, COUNT-SURFACES-20261107-001A). Dually it is a map of a cubic graph B
whose vertices are the triangles (points of colour 0, lines of colour 1) and whose edges are the sides. This module goes both ways:
- `rotation_of(S)` reads an oriented surface as a rotation system: for each triangle the cyclic order of its three darts (dart (t, k) is
  side k of triangle t), with each dart's partner across its side;
- `build(name, colour, rot, partner)` turns a rotation system back into a surface_lib.Surface. Side j of the triangle of v is the j-th dart
  of rot[v]; tracing faces (a dart d is followed by rot(partner(d))) puts corner j + 1 of v (between sides j + 2 and j) in the face of corner
  j' + 2 of the triangle across side j, which is side j' there, and corner j + 2 in the face of corner j' + 1.
- `splice(A, x, R, y, sigma)` removes vertex x of map A and vertex y of map R and joins x's neighbours to y's (the 3-edge splice of
  THREEFOLD-SURFACES-20261030-001): the dart of A that pointed at x, from x's i-th dart, is joined to the dart of R that pointed at y from
  y's sigma(i)-th dart. Rotations are kept, so the result is a map of the spliced graph.
- `GrownTorus` wraps a knot space on any torus for handles_lib (LEARN-HANDLES-20261109-001A), with sign classes labelled by two linear
  functionals that vanish on gauge and read the class of a flat change."""
import itertools
import sys
from collections import deque
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/LEARN-HANDLES-20261109-001A/LEARN-HANDLES-20261109-001A-P001_learning_resolves_a_class_forced_pair_only_by_winding"))
import handles_lib as H  # noqa: E402

SL = H.SL


# ---------------------------------------------------------------------------------------------------- maps and surfaces
def orientation(S):
    o = [None] * S.nt
    o[0], stack = 0, [0]
    while stack:
        t = stack.pop()
        for k in range(3):
            t2, k2 = S.side[t][k]
            rev = int(S.cmap[t][k][(k + 1) % 3] == (k2 + 1) % 3)
            want = o[t] ^ rev
            if o[t2] is None:
                o[t2] = want
                stack.append(t2)
            assert o[t2] == want, "not orientable"
    return o


def rotation_of(S, tag=""):
    """(colour, rot, partner) with darts named (tag, t, k)"""
    o = orientation(S)
    colour = {(tag, t): S.colour[t] for t in range(S.nt)}
    rot = {(tag, t): [(tag, t, k) for k in ((0, 1, 2) if o[t] == 0 else (0, 2, 1))] for t in range(S.nt)}
    partner = {(tag, t, k): (tag,) + tuple(S.side[t][k]) for t in range(S.nt) for k in range(3)}
    return colour, rot, partner


def mirror(m):
    colour, rot, partner = m
    return colour, {v: [r[0], r[2], r[1]] for v, r in rot.items()}, partner


def build(name, colour, rot, partner):
    verts = sorted(rot)
    vid = {v: i for i, v in enumerate(verts)}
    where = {}
    for v in verts:
        for j, d in enumerate(rot[v]):
            where[d] = (vid[v], j)
    side, cmap = [], []
    for v in verts:
        sv, cv = [], []
        for j, d in enumerate(rot[v]):
            w, j2 = where[partner[d]]
            sv.append((w, j2))
            cv.append({(j + 1) % 3: (j2 + 2) % 3, (j + 2) % 3: (j2 + 1) % 3})
        side.append(sv)
        cmap.append(cv)
    S = SL.Surface(name, [colour[v] for v in verts], side, cmap)
    S.verts, S.where = verts, where
    return S


def splice(A, x, R, y, sigma):
    """the 3-edge splice of map A at vertex x with map R at vertex y; maps are (colour, rot, partner) with disjoint dart names"""
    ca, ra, pa = A
    cr, rr, pr = R
    assert ca[x] != cr[y]
    colour = {v: c for v, c in list(ca.items()) + list(cr.items()) if v not in (x, y)}
    rot = {v: r for v, r in list(ra.items()) + list(rr.items()) if v not in (x, y)}
    partner = {d: e for d, e in list(pa.items()) + list(pr.items()) if d[:2] not in (x, y) and e[:2] not in (x, y)}
    for i in range(3):
        a = pa[ra[x][i]]
        b = pr[rr[y][sigma[i]]]
        partner[a], partner[b] = b, a
    return colour, rot, partner


def euler_of(m):
    """V - E + F of a map, faces traced by d -> rot(partner(d))"""
    colour, rot, partner = m
    nxt = {}
    for v, r in rot.items():
        for j, d in enumerate(r):
            nxt[d] = r[(j + 1) % 3]
    seen, faces = set(), 0
    for d in partner:
        if d in seen:
            continue
        faces += 1
        e = d
        while e not in seen:
            seen.add(e)
            e = nxt[partner[e]]
    return len(rot) - len(partner) // 2 + faces


# ---------------------------------------------------------------------------------------------------- a knot space on any torus
class GrownTorus(H.Torus):
    def __init__(self, S, name, s_nat):
        K = SL.KnotSpace(S)
        assert K.chi == 0 and S.orientable() and S.validate()
        self.S, self.K, self.n, self.V, self.params, self.name = S, K, K.n, K.V, None, name
        self.fv = [[S.vert[K.lines[i]][c] for c in range(3)] for i in range(self.n)]
        self.simple = K.simple() and all(len(set(f)) == 3 for f in self.fv)
        self.lines_at = [[] for _ in range(self.V)]
        for i in range(self.n):
            for c in range(3):
                self.lines_at[self.fv[i][c]].append(i)
        self.adj = [set() for _ in range(self.V)]
        for t in range(S.nt):
            a, b, c = S.vert[t]
            for u, w in ((a, b), (b, c), (a, c)):
                self.adj[u].add(w)
                self.adj[w].add(u)
        assert K.even_faces(s_nat) == []
        Z = [int("".join(str(b) for b in reversed(z)), 2) for z in K.classes()]
        assert len(Z) == 2
        gauge = K.gauge_vectors()
        m = 3 * self.n
        cs = []
        for j in range(2):
            sol = SL.solve_f2(gauge + Z, [0] * len(gauge) + [int(j == 0), int(j == 1)], m)
            assert sol is not None
            cs.append([(sol >> e) & 1 for e in range(m)])
        self.contrib = [[cs[0][e], cs[1][e]] for e in range(m)]
        zs = [[(z >> e) & 1 for e in range(m)] for z in Z]
        self.classes = {}
        for a in itertools.product((0, 1), repeat=2):
            s = list(s_nat)
            for ai, z in zip(a, zs):
                if ai:
                    s = [u ^ w for u, w in zip(s, z)]
            self.classes[self.label(s)] = s
        assert len(self.classes) == 4
        self.natural = self.label(s_nat)
        self.sat = {lab for lab, s in self.classes.items() if K.sat(s)[0]}
        self.forced = [lab for lab in H.LABELS if lab not in self.sat]
        self._dist = {}


# ---------------------------------------------------------------------------------------------------- growing a Fano atom on a knot sphere
def line_orbits(S):
    """orbits of the line triangles under the colour-preserving automorphisms of the incidence graph (networkx VF2)"""
    G = nx.Graph()
    for t in range(S.nt):
        G.add_node(t, c=S.colour[t])
        for k in range(3):
            G.add_edge(t, S.side[t][k][0])
    GM = nx.algorithms.isomorphism.GraphMatcher(G, G, node_match=lambda a, b: a["c"] == b["c"])
    orbit = {t: t for t in range(S.nt) if S.colour[t] == 1}
    for phi in GM.isomorphisms_iter():
        for t in orbit:
            orbit[t] = min(orbit[t], phi[t])
    reps = sorted(set(orbit.values()))
    return reps, orbit


def line_distance(S, l0):
    """distance between line triangles, lines adjacent when they share a point"""
    d, dq = {l0: 0}, deque([l0])
    while dq:
        l = dq.popleft()
        for k in range(3):
            p = S.side[l][k][0]
            for k2 in range(3):
                l2 = S.side[p][k2][0]
                if l2 not in d:
                    d[l2] = d[l] + 1
                    dq.append(l2)
    return d


class Growth:
    """a knot sphere (surface S with a Kasteleyn signing s0 indexed as KnotSpace(S)) grown by a Fano atom spliced at line triangle l"""

    def __init__(self, S, s0, l, fano, P, sigma, chirality):
        KA = SL.KnotSpace(S)
        A = rotation_of(S, "A")
        R = rotation_of(fano, "R")
        if chirality:
            R = mirror(R)
        self.m = splice(A, ("A", l), R, ("R", P), sigma)
        self.chi = euler_of(self.m)
        if self.chi != 0:
            return
        G = build("grown", *self.m)
        KG = SL.KnotSpace(G)
        # the sign of each side of the grown space: old sides from s0, the atom's from 0, the three new ones unknown
        line_of = {}  # dart -> (old tag, old line index, side index) for darts of line triangles
        lidA = {t: i for i, t in enumerate(KA.lines)}
        new_sides, s = [], [None] * (3 * KG.n)
        for gi, gt in enumerate(KG.lines):
            v = G.verts[gt]
            for j, d in enumerate(self.m[1][v]):
                e = self.m[2][d]
                if d[0] == "A" and e[0] == "A":
                    s[3 * gi + j] = s0[3 * lidA[d[1]] + d[2]]
                elif d[0] == "R" and e[0] == "R":
                    s[3 * gi + j] = 0
                else:
                    new_sides.append(3 * gi + j)
        assert len(new_sides) == 3 and all(s[e] is not None for e in range(3 * KG.n) if e not in new_sides)
        self.completions = []
        for bits in itertools.product((0, 1), repeat=3):
            t = list(s)
            for e, b in zip(new_sides, bits):
                t[e] = b
            if KG.even_faces(t) == []:
                self.completions.append(t)
        self.G, self.KG, self.new_sides = G, KG, new_sides
        # points: old point triangle t of S -> grown point index; atom points
        pid = {gt: i for i, gt in enumerate(KG.points)}
        gvid = {v: i for i, v in enumerate(G.verts)}
        self.old_point = {t: pid[gvid[("A", t)]] for t in KA.points}
        self.atom_points = [pid[gvid[v]] for v in G.verts if v[0] == "R" and G.colour[gvid[v]] == 0]
        self.atom_lines = [i for i, gt in enumerate(KG.lines) if G.verts[gt][0] == "R"]
        self.l_points = [self.old_point[S.side[l][k][0]] for k in range(3)]
        self.atom_sides = {3 * i + j for i in self.atom_lines for j in range(3)}

    def extend(self, s, x_old, KA):
        """the old state on the old points and, on the atom's points, the first assignment that violates the fewest lines"""
        n = self.KG.n
        base = [None] * n
        for t, gp in self.old_point.items():
            base[gp] = x_old[KA.points.index(t)]
        best, arg, ties = None, None, 0
        for bits in itertools.product((0, 1), repeat=len(self.atom_points)):
            y = list(base)
            for p, b in zip(self.atom_points, bits):
                y[p] = b
            v = self.KG.tallies(s, y)[0]
            if best is None or v < best:
                best, arg, ties = v, y, 1
            elif v == best:
                ties += 1
        return arg, best, ties

    def atom_relation(self, s):
        """the patterns of the replaced line's three points that some assignment of the atom's points completes on the atom's lines"""
        out = []
        for pat in itertools.product((0, 1), repeat=3):
            ok = False
            for bits in itertools.product((0, 1), repeat=len(self.atom_points)):
                y = {}
                for p, b in zip(self.l_points, pat):
                    y[p] = b
                for p, b in zip(self.atom_points, bits):
                    y[p] = b
                if all(not (y[self.KG.pt[i][0]] ^ s[3 * i] == y[self.KG.pt[i][1]] ^ s[3 * i + 1] == y[self.KG.pt[i][2]] ^ s[3 * i + 2])
                       for i in self.atom_lines):
                    ok = True
                    break
            out.append(pat if ok else None)
        return [p for p in out if p is not None]
