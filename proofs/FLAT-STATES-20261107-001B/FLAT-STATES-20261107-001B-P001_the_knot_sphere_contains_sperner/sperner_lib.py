"""The knot sphere contains Sperner's lemma, for FLAT-STATES-20261107-001B.

Sperner instance. The coarse triangular grid of side m: vertices (a, b) with a, b >= 0 and a + b <= m, coloured 0, 1, 2; boundary colours
fixed; a small triangle is fully labelled when it carries all three colours.

Embedding. Inside one octant of K_k the points are the up-triangles, with lattice coordinates (x, y), the lines are U(x, y) and the faces
D(x, y) (TWO-ROUND-BRIDGE / SPHERE-COUNT notation). The region R = {(x0 + X, y0 + Y) : X, Y >= 0, X + Y <= 2m} carries the Sperner grid
at even (X, Y); every other point of R is the midpoint of a coarse edge. A Sperner colouring gives labels in Z6: 2c at a vertex, and at a
midpoint the label halfway between its ends' labels (they differ by 0 or 2). Points of R are coloured by their label in a frame developed
over R (FLAT-STATES-20261107-001A). Points outside R take the colours of one fixed flat state whose vortex lies in R and whose cut star
crosses the boundary of R in three adjacent pairs, so that on the boundary of R its labels are exactly those of a Sperner boundary with
three monochromatic sides.

Then a line can be violated only inside a fully labelled coarse triangle (its labels must span three or more values), so every violated
line of the image names a fully labelled triangle of the Sperner instance. Each point's colour reads at most two Sperner colours.
"""
import itertools
import random
import sys
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "proofs/FLAT-STATES-20261107-001A/FLAT-STATES-20261107-001A-P001_flat_states_exist_on_the_whole_sphere"))
import flat_lib as F  # noqa: E402
C = F.C


def triangles_3d(k):
    """the triangles of the k-frequency octahedron in octa_dual's order"""
    tris = set()
    for sx, sy, sz in itertools.product((1, -1), repeat=3):
        P = lambda i, j, l: (sx * i, sy * j, sz * l)  # noqa: E731
        for i in range(k):
            for j in range(k - i):
                l = k - 1 - i - j
                tris.add(frozenset([P(i + 1, j, l), P(i, j + 1, l), P(i, j, l + 1)]))
        for i in range(k - 1):
            for j in range(k - 1 - i):
                l = k - 2 - i - j
                tris.add(frozenset([P(i + 1, j + 1, l), P(i + 1, j, l + 1), P(i, j + 1, l + 1)]))
    return sorted(tris, key=lambda t: sorted(t))


def octant_lattice(K):
    """an octant whose up-triangles are points; {point: (x, y)} for the points inside it"""
    k = K["k"]
    g = C.octa_dual(k)
    col = nx.bipartite.color(g)
    pts = sorted(v for v in g if col[v] == 0)
    tris = triangles_3d(k)
    ptri = {tris[v]: i for i, v in enumerate(pts)}
    for s in itertools.product((1, -1), repeat=3):
        coords = {}
        for t, i in ptri.items():
            u = [tuple(c * sc for c, sc in zip(v, s)) for v in t]
            if all(c >= 0 for v in u for c in v):
                mins = [min(v[a] for v in u) for a in range(3)]
                if sum(mins) == k - 1:
                    coords[i] = (mins[0], mins[1])
        if len(coords) == k * (k + 1) // 2:
            return s, coords
    raise AssertionError("no octant with up-triangles as points")


def region(K, m, x0=1, y0=1):
    """the region R: {point: (X, Y)} and the inverse map"""
    s, coords = octant_lattice(K)
    R = {p: (x - x0, y - y0) for p, (x, y) in coords.items() if x >= x0 and y >= y0 and (x - x0) + (y - y0) <= 2 * m}
    assert len(R) == (2 * m + 1) * (2 * m + 2) // 2, "region does not fit"
    inv = {XY: p for p, XY in R.items()}
    return R, inv


def coarse_of(XY):
    """the Sperner vertices a point reads: one vertex, or the two ends of the coarse edge it bisects"""
    X, Y = XY
    if X % 2 == 0 and Y % 2 == 0:
        return [(X // 2, Y // 2)]
    if Y % 2 == 0:
        return [((X - 1) // 2, Y // 2), ((X + 1) // 2, Y // 2)]
    if X % 2 == 0:
        return [(X // 2, (Y - 1) // 2), (X // 2, (Y + 1) // 2)]
    return [((X + 1) // 2, (Y - 1) // 2), ((X - 1) // 2, (Y + 1) // 2)]


def label_from(colours):
    """2c at a vertex; halfway (mod 6) between the two ends' labels at a midpoint"""
    if len(colours) == 1:
        return 2 * colours[0] % 6
    a, b = 2 * colours[0] % 6, 2 * colours[1] % 6
    d = (b - a) % 6
    return a if d == 0 else (a + 1) % 6 if d == 2 else (a - 1) % 6


def is_boundary(XY, m):
    X, Y = XY
    return X == 0 or Y == 0 or X + Y == 2 * m


def coarse_triangles(m):
    up = [((a, b), (a + 1, b), (a, b + 1)) for a in range(m) for b in range(m - a)]
    dn = [((a + 1, b), (a, b + 1), (a + 1, b + 1)) for a in range(m) for b in range(m - a - 1)]
    return up + dn


def boundary_cycle(m):
    """the boundary points of R in cyclic order (fine coordinates)"""
    side1 = [(X, 0) for X in range(2 * m)]
    side2 = [(2 * m - Y, Y) for Y in range(2 * m)]
    side3 = [(0, 2 * m - Y) for Y in range(2 * m)]
    return side1 + side2 + side3


def r_frames(K, R, base):
    """frames developed over R from base (R is simply connected and holds no corner)"""
    frame = {base: (0, 0)}
    stack = [base]
    while stack:
        a = stack.pop()
        for l in K["lines_of"][a]:
            if not all(q in R for q in K["lines"][l]):
                continue
            for b in K["lines"][l]:
                if b == a:
                    continue
                o, e = F.step(K, l, a, b)
                fb = ((frame[a][0] + o) % 3, frame[a][1] ^ e)
                if b in frame:
                    assert frame[b] == fb
                else:
                    frame[b] = fb
                    stack.append(b)
    assert len(frame) == len(R)
    return frame


def crossing_pairs(m):
    """three adjacent pairs of boundary edges, one just after each corner of R (fine coordinates)"""
    return [((0, 0), (1, 0)), ((1, 0), (2, 0)),
            ((2 * m, 0), (2 * m - 1, 1)), ((2 * m - 1, 1), (2 * m - 2, 2)),
            ((0, 2 * m), (0, 2 * m - 1)), ((0, 2 * m - 1), (0, 2 * m - 2))]


def gamma_ends(K, a, b):
    l, _, _, f = next(c for c in K["corners"] if {c[1], c[2]} == {a, b})
    return ("l", l), ("f", f)


def outside_state(K, G, R, inv, m, rng=None):
    """a flat state with its vortex in R whose cut star leaves R through the crossing pairs; returns (colours, star, z, flat frames)"""
    inside = {v for v in G if all(p in R for p in F.vertex_points(K, v))}
    ins, outs = [], []
    for e in crossing_pairs(m):
        u, v = gamma_ends(K, inv[e[0]], inv[e[1]])
        ins.append(u if u in inside else v)
        outs.append(v if u in inside else u)
        assert (ins[-1] in inside) and (outs[-1] not in inside)
    z = inv[(2 * m // 3, 2 * m // 3)]
    head = F.disjoint_paths(G, F.triangles_at(K, G, z), ins, z, rng, allowed=inside)
    tail = F.disjoint_paths(G, outs, [("f", fi) for fi in F.corner_faces(K)], -1, rng, allowed=set(G) - inside)
    assert head is not None and tail is not None, "no cut star through the crossing pairs"
    by_in = {h[-1]: h for h in head}
    star = [by_in[i] + t for i, t in zip(ins, tail)]
    base = next(p for p in range(K["n"]) if p not in R)
    frames = F.develop(K, z, star, base)
    x = [None] * K["n"]
    for p, (s, g) in frames.items():
        x[p] = F.PATTERNS[0][s] ^ g
    x[z] = 0
    return x, star, z, frames


def build_reduction(k, m, rng=None):
    """everything the reduction needs: the region, its frames, the fixed outside colours and the Sperner boundary colours"""
    K = F.index_lines(F.build(k))
    G = F.gamma(K)
    R, inv = region(K, m)
    x_out, star, z, ff = outside_state(K, G, R, inv, m, rng)
    fr = r_frames(K, R, inv[(0, 0)])
    lab = {p: (2 * (fr[p][0] - ff[p][0]) + 3 * (fr[p][1] ^ ff[p][1])) % 6 for p in R if p != z and is_boundary(R[p], m)}
    t0 = lab[inv[(0, 0)]] % 2
    bcol = {}
    for XY in boundary_cycle(m):
        if XY[0] % 2 == 0 and XY[1] % 2 == 0:
            assert lab[inv[XY]] % 2 == t0
            bcol[(XY[0] // 2, XY[1] // 2)] = (lab[inv[XY]] - t0) // 2
    for XY in boundary_cycle(m):   # midpoints on the boundary interpolate their ends
        assert lab[inv[XY]] == (label_from([bcol[v] for v in coarse_of(XY)]) + t0) % 6, ("boundary midpoint mismatch", XY)
    return dict(K=K, G=G, R=R, inv=inv, m=m, x_out=x_out, star=star, z=z, fr=fr, t0=t0, bcol=bcol)


def interior_vertices(m):
    return [(a, b) for a in range(1, m) for b in range(1, m - a)]


def image(red, cint):
    """the knot sphere assignment of a Sperner colouring (cint on the interior vertices; the boundary is fixed)"""
    K, R, fr, t0 = red["K"], red["R"], red["fr"], red["t0"]
    col = dict(red["bcol"])
    col.update(cint)
    x = list(red["x_out"])
    for p, XY in R.items():
        lab = (label_from([col[v] for v in coarse_of(XY)]) + t0) % 6
        x[p] = F.PATTERNS[lab][fr[p][0]] ^ fr[p][1]
    return x, col


def full_triangles(col, m):
    return [t for t in coarse_triangles(m) if len({col[v] for v in t}) == 3]


def coarse_triangle_of_line(red, l):
    """the coarse triangle containing line l, or None if l is not inside R"""
    R = red["R"]
    L = red["K"]["lines"][l]
    if not all(p in R for p in L):
        return None
    vs = set()
    for p in L:
        vs.update(coarse_of(R[p]))
    return tuple(sorted(vs))
