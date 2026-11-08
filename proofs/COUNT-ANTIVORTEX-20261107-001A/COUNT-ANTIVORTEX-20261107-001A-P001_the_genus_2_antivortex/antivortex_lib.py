"""The genus-2 antivortex, for COUNT-ANTIVORTEX-20261107-001A.

The surface. T = Z^2 / 3aZ^2 is the triangular lattice torus of COUNT-SURFACES-20261107-001A (points are up triangles, lines down
triangles). Remove the hexagon of side h around a vertex and glue the torus to a second copy of itself along the hexagon's boundary;
the copy's colours are swapped so that neighbours across the seam still differ. The result is a closed orientable surface of genus 2.
Its vertices have degree 6 except the hexagon's six corners, which have degree 8 (two 240-degree wedges): faces of the incidence graph
with four corners, the negative-curvature mirror of the knot sphere's six two-corner faces.

Frames (FLAT-STATES-20261107-001A). A frame is a sublattice in Z3 and a gauge bit; a step a -> b inside a line shifts the sublattice by
+1 or -1 (by the surface's orientation) and the gauge by the relative sign. Label lambda in frame (s, g) means colour S_lambda[s] xor g.

Signs. The count (COUNT-SURFACES-20261107-001A) needs every face odd; this holds for exactly one Kasteleyn class with the handles' loops
flat, found by trying the 16 classes. Cutting along six disjoint paths from a point z to the six degree-8 faces and developing one frame
leaves an assignment with no violated line and one over-agreeing face at z: an antivortex.

The reduction. The region R and the Sperner map are those of FLAT-STATES-20261107-001B, placed in the first sheet; the outside state's
cut star leaves R through the three crossing pairs, so R's boundary carries a Sperner boundary of the reversed orientation."""
import itertools
import math
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/COUNT-SURFACES-20261107-001A/COUNT-SURFACES-20261107-001A-P001_the_count_reads_the_euler_characteristic"))
sys.path.insert(0, str(ROOT / "proofs/FLAT-STATES-20261107-001A/FLAT-STATES-20261107-001A-P001_flat_states_exist_on_the_whole_sphere"))
sys.path.insert(0, str(ROOT / "proofs/FLAT-STATES-20261107-001B/FLAT-STATES-20261107-001B-P001_the_knot_sphere_contains_sperner"))
import surface_lib as L  # noqa: E402
import flat_lib as F  # noqa: E402
import sperner_lib as SP  # noqa: E402


def hexnorm(a, b):
    return max(abs(a), abs(b), abs(a + b))


# ------------------------------------------------------------------------------------------------ the surface
def holed_double(a, h, centre, L_vectors=None):
    """T(L) (default L = 3a Z^2) minus the hexagon of side h around the vertex `centre`, glued to a colour-swapped copy along the hole"""
    S = L.torus(3 * a, 0, 3 * a) if L_vectors is None else L.torus(*L_vectors)
    key = {L.centroid(P): t for t, (_, P) in enumerate(S.tris)}
    hole = set()
    ci, cj = centre
    for i in range(ci - h - 1, ci + h + 1):
        for j in range(cj - h - 1, cj + h + 1):
            for P in (L.up(i, j), L.down(i, j)):
                if all(hexnorm(X // 6 - ci, Y // 6 - cj) <= h for X, Y in P):
                    hole.add(key[S.canon(L.centroid(P))[0]])
    assert len(hole) == 6 * h * h
    keep = [t for t in range(S.nt) if t not in hole]
    idx = {}
    for sh in (0, 1):
        for t in keep:
            idx[(sh, t)] = len(idx)
    colour, side, cmap = [None] * len(idx), [None] * len(idx), [None] * len(idx)
    for (sh, t), u in idx.items():
        colour[u] = S.colour[t] ^ sh
        srow, crow = [], []
        for k in range(3):
            t2, k2 = S.side[t][k]
            if t2 in hole:                                  # across the seam: the same triangle in the other sheet
                srow.append((idx[(1 - sh, t)], k))
                crow.append({c: c for c in range(3) if c != k})
            else:
                srow.append((idx[(sh, t2)], k2))
                crow.append(dict(S.cmap[t][k]))
        side[u], cmap[u] = srow, crow
    D = L.Surface(f"double(T(L), hexagon {h} at {centre})", colour, side, cmap)
    D.base, D.hole, D.idx, D.a, D.h, D.centre = S, hole, idx, a, h, centre
    return D


def orientation(S):
    """an orientation bit per triangle (corner order 0, 1, 2 positive iff the bit is 0)"""
    o = [None] * S.nt
    o[0], stack = 0, [0]
    while stack:
        t = stack.pop()
        for k in range(3):
            t2, k2 = S.side[t][k]
            want = o[t] ^ int(S.cmap[t][k][(k + 1) % 3] == (k2 + 1) % 3)
            if o[t2] is None:
                o[t2] = want
                stack.append(t2)
            else:
                assert o[t2] == want, "not orientable"
    return o


def flat_dict(KS, s):
    """the knot space with signing s (per line side) in FLAT-STATES-20261107-001A's format: lines, signs, rotation (cyclic order of a
    line's points in the orientation), corners (line, a, b, face) with a before b around the face, face point sets"""
    S = KS.S
    o = orientation(S)
    lines, signs, rot, corners = [], [], {}, []
    for i, l in enumerate(KS.lines):
        pts = [KS.pt[i][k] for k in range(3)]
        lines.append(tuple(pts))
        signs.append(tuple(s[3 * i + k] for k in range(3)))
        rot[i] = [pts[0], pts[1], pts[2]] if o[l] == 0 else [pts[0], pts[2], pts[1]]
        for c in range(3):
            a, b = KS.pt[i][(c + 2) % 3], KS.pt[i][(c + 1) % 3]
            if o[l]:
                a, b = b, a
            corners.append((i, a, b, S.vert[l][c]))
    fpts = [sorted({p for (l, a, b, f) in corners if f == v for p in (a, b)}) for v in range(S.nv)]
    sgn = [{p: x for p, x in zip(Lp, Sg)} for Lp, Sg in zip(lines, signs)]
    K = dict(k=None, lines=lines, signs=signs, n=KS.n, rot=rot, corners=corners, fpts=fpts, sgn=sgn)
    return F.index_lines(K)


def coords(D, KS):
    """point index -> (sheet, i, j) of its lattice cell in the torus's fundamental domain"""
    p = D.base.params[0]
    inv = {u: key for key, u in D.idx.items()}
    out = {}
    for n_, t in enumerate(KS.points):
        sh, tt = inv[t]
        out[n_] = (sh, (tt // 2) % p, (tt // 2) // p)
    return out


def point_at(D, KS, sheet, i, j):
    """the point in `sheet` at lattice cell (i, j): an up triangle in sheet 0, a down triangle in sheet 1"""
    p, q, r = D.base.params
    t = 2 * ((j % r) * p + (i % p)) + (0 if sheet == 0 else 1)
    return KS.points.index(D.idx[(sheet, t)])


def signings(KS):
    """one signing per class with no even face"""
    s0 = KS.signing(())
    Z = KS.classes()
    for bits in itertools.product((0, 1), repeat=len(Z)):
        s = list(s0)
        for b, z in zip(bits, Z):
            if b:
                s = [u ^ w for u, w in zip(s, z)]
        yield bits, s


def defects(KS, s, x):
    """(violated lines, over-agreeing faces)"""
    viol = [i for i in range(KS.n) if len({x[KS.pt[i][k]] ^ s[3 * i + k] for k in range(3)}) == 1]
    _, agree = KS.tallies(s, x)
    over = [v for v in range(KS.V) if agree[v] // 2 >= 1]
    return viol, over


# ------------------------------------------------------------------------------------------------ the reduction
def build(a, h, centre, m, x0, y0, seed=1, margin=1, classes=None):
    """the reduction for Sperner_m on the double of T(3a): region R at (x0, y0) in sheet 0; the cut star confined to the chart
    margin <= i, j <= 3a - 1 - margin of sheet 0 (plus the seam). Returns None when no class develops consistently."""
    D = holed_double(a, h, centre)
    KS = L.KnotSpace(D)
    N = 3 * a
    crd = coords(D, KS)
    corners = [v for v in range(D.nv) if KS.d[v] == 4]
    R = {}
    for X in range(2 * m + 1):
        for Y in range(2 * m + 1 - X):
            R[point_at(D, KS, 0, x0 + X, y0 + Y)] = (X, Y)
    inv = {XY: p for p, XY in R.items()}

    def in_chart(p):
        sh, i, j = crd[p]
        return sh == 0 and margin <= i <= N - 1 - margin and margin <= j <= N - 1 - margin
    tried = []
    for bits, s in signings(KS):
        if classes is not None and bits not in classes:
            continue
        K = flat_dict(KS, s)
        G = F.gamma(K)
        rng = random.Random(seed)
        inside = {v for v in G if all(p in R for p in F.vertex_points(K, v))}

        def ok_vertex(v):
            s0p = [p for p in F.vertex_points(K, v) if crd[p][0] == 0]
            return bool(s0p) and all(in_chart(p) for p in s0p)
        chart = {v for v in G if ok_vertex(v)} | {("f", c) for c in corners}
        ins, outs = [], []
        for e in SP.crossing_pairs(m):
            u, v = SP.gamma_ends(K, inv[e[0]], inv[e[1]])
            ins.append(u if u in inside else v)
            outs.append(v if u in inside else u)
        z = inv[(2 * m // 3, 2 * m // 3)]
        head = F.disjoint_paths(G, F.triangles_at(K, G, z), ins, z, rng, allowed=inside)
        tail = F.disjoint_paths(G, outs, [("f", c) for c in corners], -1, rng, allowed=chart - inside)
        if head is None or tail is None:
            return None
        by_in = {hh[-1]: hh for hh in head}
        star = [by_in[i] + t for i, t in zip(ins, tail)]
        base = next(p for p in range(KS.n) if p not in R and p != z)
        try:
            ff = F.develop(K, z, star, base)
        except AssertionError:
            tried.append(bits)
            continue
        x_out = [None] * KS.n
        for p, (sub, g) in ff.items():
            x_out[p] = F.PATTERNS[0][sub] ^ g
        x_out[z] = 0
        fr = SP.r_frames(K, R, inv[(0, 0)])
        lab = {p: (2 * (fr[p][0] - ff[p][0]) + 3 * (fr[p][1] ^ ff[p][1])) % 6 for p in R if p != z and SP.is_boundary(R[p], m)}
        t0 = lab[inv[(0, 0)]] % 2
        bcol, ok = {}, True
        for XY in SP.boundary_cycle(m):
            if XY[0] % 2 == 0 and XY[1] % 2 == 0:
                ok &= lab[inv[XY]] % 2 == t0
                bcol[(XY[0] // 2, XY[1] // 2)] = (lab[inv[XY]] - t0) // 2
        if ok:
            for XY in SP.boundary_cycle(m):
                ok &= lab[inv[XY]] == (SP.label_from([bcol[v] for v in SP.coarse_of(XY)]) + t0) % 6
        return dict(D=D, KS=KS, K=K, G=G, R=R, inv=inv, m=m, x_out=x_out, star=star, z=z, ff=ff, fr=fr, t0=t0, bcol=bcol, s=s,
                    boundary_ok=ok, bits=bits, inconsistent=tried, corners=corners)
    return dict(D=D, KS=KS, inconsistent=tried, bits=None)


def image(red, cint):
    """the assignment of a Sperner colouring (interior colours cint; the boundary is red['bcol'])"""
    R, fr, t0 = red["R"], red["fr"], red["t0"]
    col = dict(red["bcol"])
    col.update(cint)
    x = list(red["x_out"])
    for p, XY in R.items():
        lab = (SP.label_from([col[v] for v in SP.coarse_of(XY)]) + t0) % 6
        x[p] = F.PATTERNS[lab][fr[p][0]] ^ fr[p][1]
    return x, col


def orient(col, t):
    """+1 when the triangle's colours read 0, 1, 2 counterclockwise in the coarse chart (a, b) -> (a + b/2, b sqrt3/2), else -1"""
    P = [(u + w / 2, w * math.sqrt(3) / 2) for u, w in t]
    cr = (P[1][0] - P[0][0]) * (P[2][1] - P[0][1]) - (P[1][1] - P[0][1]) * (P[2][0] - P[0][0])
    order = [col[v] for v in t] if cr > 0 else [col[v] for v in t][::-1]
    i0 = order.index(0)
    return 1 if order[i0:] + order[:i0] == [0, 1, 2] else -1


def canonical_boundary(m, corner_colours=(0, 1, 2)):
    """the fixed Sperner boundary: corners (0,0), (m,0), (0,m) coloured c0, c1, c2; each side takes its far corner's colour after its
    first vertex (sides traversed (0,0) -> (m,0) -> (0,m) -> (0,0))"""
    c0, c1, c2 = corner_colours
    b = {}
    for t in range(m + 1):
        b[(t, 0)] = c0 if t == 0 else c1
        b[(m - t, t)] = c1 if t == 0 else c2
        b[(0, m - t)] = c2 if t == 0 else c0
    return b


def local_lemma():
    """in a common frame, a triangle whose three points lie on the three sublattices and carry labels within two consecutive values is
    never monochromatic (so neither a violated line nor an over-agreeing three-corner face)"""
    bad = 0
    for c in range(6):
        for labs in itertools.product((c, (c + 1) % 6), repeat=3):
            vals = {F.PATTERNS[labs[s]][s] for s in range(3)}
            bad += len(vals) == 1
    return bad == 0
