"""Straight cut systems on the octahedral knot sphere, for COUNT-NOTE-20261107-001A.

Geometry. The points and lines of K_k are the two colour classes of the 8k^2 triangles of the k-frequency octahedron
|x| + |y| + |z| = k; the faces of the point graph are the lines and the subdivision vertices (two-point faces at the six corners).
Unfold the positive face F and its three neighbours N1 (x <= 0), N2 (y <= 0), N3 (z <= 0) into the plane of F. They form a triangle
of side 2k whose vertices are the far corners -e_i and whose side midpoints are F's corners e_i. Point centroids form a unit triangular
lattice there, and the point graph's edges are straight unit segments.

Straight cut systems. For a vortex z near F's centre, the six arcs follow the segments from z's centroid to the six corners: each arc is
the sequence of faces its segment crosses, starting in the face of z's six whose angle contains the segment. Within distance R of its
corner an arc is completed by a shortest path of faces to the corner's two-point face. The frames, shifts t and label states are those
of SPHERE-WIDTH-20261107-001A's width_lib, built on this cut system instead of an arbitrary one."""
import itertools
import math
import sys
from collections import deque
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/SPHERE-WIDTH-20261107-001A/SPHERE-WIDTH-20261107-001A-P001_the_spheres_count_needs_width_sqrt_n"))
import width_lib as W  # noqa: E402

F = W.F
C = F.C
S2, S6 = math.sqrt(2), math.sqrt(6)


def unfold(v):
    """a 3D point of F, N1, N2 or N3 in F's plane, then in planar coordinates (unit edge length)"""
    x, y, z = v
    if x < 0:
        x, y, z = x, y - x, z - x
    elif y < 0:
        x, y, z = x - y, y, z - y
    elif z < 0:
        x, y, z = x - z, y - z, z
    return ((y - z) / S2, (2 * x - y - z) / S6)


def in_big(c):
    """the triangle's centroid lies in F or one of its three neighbours"""
    return sum(1 for t in c if t < 0) <= 1


def geometry(k):
    K = W.sphere(k)
    g = C.octa_dual(k)
    tris = set()
    for sx, sy, sz in itertools.product((1, -1), repeat=3):
        P = lambda i, j, l: (sx * i, sy * j, sz * l)  # noqa: E731
        for i in range(k):
            for j in range(k - i):
                tris.add(frozenset([P(i + 1, j, k - 1 - i - j), P(i, j + 1, k - 1 - i - j), P(i, j, k - i - j)]))
        for i in range(k - 1):
            for j in range(k - 1 - i):
                l = k - 2 - i - j
                tris.add(frozenset([P(i + 1, j + 1, l), P(i + 1, j, l + 1), P(i, j + 1, l + 1)]))
    tris = sorted(tris, key=lambda t: sorted(t))
    col = nx.bipartite.color(g)
    pts = sorted(v for v in g if col[v] == 0)
    lns = sorted(v for v in g if col[v] == 1)
    cen = lambda t: tuple(sum(v[i] for v in t) / 3 for i in range(3))  # noqa: E731
    K["ptri"] = [tris[v] for v in pts]
    K["ltri"] = [tris[v] for v in lns]
    # consistency with count_lib's lines: a line's points are the point-triangles sharing a side with it
    for l, L in enumerate(K["lines"]):
        assert all(len(K["ltri"][l] & K["ptri"][p]) == 2 for p in L)
    K["c3"] = [cen(t) for t in K["ptri"]]
    K["pos"] = [unfold(c) if in_big(c) else None for c in K["c3"]]
    K["face_vertex"] = []
    for fi, P in enumerate(K["fpts"]):
        common = set.intersection(*[set(K["ptri"][p]) for p in P])
        assert len(common) == 1
        K["face_vertex"].append(next(iter(common)))
    K["corner_face"] = {}
    for fi in F.corner_faces(K):
        K["corner_face"][K["face_vertex"][fi]] = fi
    K["node_corners"] = {}
    for c in K["corners"]:
        l, a, b, f = c
        K["node_corners"].setdefault(("l", l), []).append(c)
        K["node_corners"].setdefault(("f", f), []).append(c)
    centre = min((p for p in range(K["n"]) if all(t > 0 for t in K["c3"][p])),
                 key=lambda p: sum((t - k / 3) ** 2 for t in K["c3"][p]))
    K["centre"] = centre
    K["dist_centre"] = F.dist_from(K["adj"], [centre])
    K["dist_corner"] = {v: F.dist_from(K["adj"], K["fpts"][fi]) for v, fi in K["corner_face"].items()}
    return K


def core(K, radius):
    return [p for p in range(K["n"]) if K["dist_centre"][p] <= radius and all(t > 0 for t in K["c3"][p])]


def node_points(K, v):
    return F.vertex_points(K, v)


def _cross(p, r, a, b):
    """parameter s in (0, 1] where segment p->r crosses segment a-b, or None"""
    dx, dy = r[0] - p[0], r[1] - p[1]
    ex, ey = b[0] - a[0], b[1] - a[1]
    den = dx * ey - dy * ex
    if abs(den) < 1e-12:
        return None
    s = ((a[0] - p[0]) * ey - (a[1] - p[1]) * ex) / den
    u = ((a[0] - p[0]) * dy - (a[1] - p[1]) * dx) / den
    if 1e-9 < s <= 1 + 1e-9 and -1e-9 <= u <= 1 + 1e-9:
        if min(u, 1 - u) < 1e-9:
            raise ValueError("segment passes through a point centroid")
        return s
    return None


def _sgn(c):
    return tuple(1 if t > 0 else -1 for t in c)


def _vertices(s, k):
    return [tuple(s[i] * k if j == i else 0 for j in range(3)) for i in range(3)]


def _reflect(P, A, B):
    ax, ay = B[0] - A[0], B[1] - A[1]
    t = ((P[0] - A[0]) * ax + (P[1] - A[1]) * ay) / (ax * ax + ay * ay)
    fx, fy = A[0] + t * ax, A[1] + t * ay
    return (2 * fx - P[0], 2 * fy - P[1])


def chart_pos(K, p, via):
    """p's centroid drawn in the chart of its face unfolded across the side it shares with the T-face 'via' (a sign pattern)"""
    c3, k = K["c3"][p], K["k"]
    s = _sgn(c3)
    if sum(1 for t in s if t < 0) <= 1:
        return K["pos"][p]
    diff = [i for i in range(3) if s[i] != via[i]]
    assert len(diff) == 1, ("faces not adjacent", s, via)
    V = _vertices(s, k)
    Vv = _vertices(via, k)
    shared = [v for v in V if v in Vv]
    third_via = next(v for v in Vv if v not in V)
    A, B = unfold(shared[0]), unfold(shared[1])
    img = {shared[0]: A, shared[1]: B, next(v for v in V if v not in Vv): _reflect(unfold(third_via), A, B)}
    lam = [abs(t) / k for t in c3]
    x = sum(lam[i] * img[V[i]][0] for i in range(3))
    y = sum(lam[i] * img[V[i]][1] for i in range(3))
    return (x, y)


def edge_segment(K, l, a, b):
    if K["pos"][a] is not None and K["pos"][b] is not None:
        return K["pos"][a], K["pos"][b]
    lc = tuple(sum(v[i] for v in K["ltri"][l]) / 3 for i in range(3))
    if in_big(lc):
        via = _sgn(lc)
    elif K["pos"][a] is None and K["pos"][b] is None:
        return None                     # wholly outside the unfolded triangle: no arc meets it
    else:
        inside = a if K["pos"][a] is not None else b
        via = _sgn(K["c3"][inside])
    return chart_pos(K, a, via), chart_pos(K, b, via)


def straight_star(K, z, eps=0.01, turn=1e-3):
    """the six arcs of the straight cut system for vortex z, as paths of the line-face graph"""
    P0 = K["pos"][z]
    starts = F.triangles_at(K, K["G"], z)
    used, arcs = set(), []
    for v3, fi in sorted(K["corner_face"].items()):
        E = unfold(v3)
        dx, dy = P0[0] - E[0], P0[1] - E[1]
        r = math.hypot(dx, dy)
        Q = (E[0] + eps * dx / r, E[1] + eps * dy / r)
        # rotate the segment slightly counterclockwise about z's centroid, so that it meets no other centroid
        L = math.hypot(Q[0] - P0[0], Q[1] - P0[1])
        Q = (Q[0] - turn * (Q[1] - P0[1]) / L, Q[1] + turn * (Q[0] - P0[0]) / L)
        d = (Q[0] - P0[0], Q[1] - P0[1])
        node = None
        for X in starts:
            n1, n2 = [p for p in node_points(K, X) if p != z]
            a = (K["pos"][n1][0] - P0[0], K["pos"][n1][1] - P0[1])
            b = (K["pos"][n2][0] - P0[0], K["pos"][n2][1] - P0[1])
            cr = lambda u, w: u[0] * w[1] - u[1] * w[0]  # noqa: E731
            if cr(a, b) < 0:
                a, b = b, a
            if cr(a, d) > 0 and cr(d, b) > 0:
                node = X
        path, s_cur, goal = [node], 0.0, ("f", fi)
        while node != goal:
            best = None
            for c in K["node_corners"][node]:
                l, a, b, f = c
                if z in (a, b):
                    continue
                seg = edge_segment(K, l, a, b)
                if seg is None:
                    continue
                s = _cross(P0, Q, *seg)
                if s is not None and s > s_cur + 1e-12 and (best is None or s < best[0]):
                    best = (s, c)
            if best is None:
                raise ValueError("arc stopped before its corner")
            s_cur, (l, a, b, f) = best
            node = ("f", f) if node[0] == "l" else ("l", l)
            path.append(node)
            if len(path) > 20 * K["k"]:
                raise ValueError("arc too long")
        if len(set(path)) != len(path) or used & set(path):
            raise ValueError("arcs meet")
        used |= set(path)
        arcs.append(path)
    return arcs


def trivialization(K, z, star):
    """frames and shifts for vortex z on a given cut system (as width_lib.trivialize)"""
    base = next(p for p in range(K["n"]) if p != z)
    fr = F.develop(K, z, star, base)
    shift = {}
    for l, L in enumerate(K["lines"]):
        for a, b in itertools.permutations([p for p in L if p != z], 2):
            o, e = F.step(K, l, a, b)
            d = (fr[a][0] + o - fr[b][0]) % 3
            t = (2 * d + 3 * (fr[a][1] ^ e ^ fr[b][1])) % 6
            if t not in (0, 1, 5):
                raise ValueError("shift out of range")
            shift.setdefault((a, b), []).append({0: 0, 1: 1, 5: -1}[t])
    return dict(z=z, star=star, fr=fr, shift=shift)


def zero_heads_tails(T):
    """X0: points that are the head of a weight-0 edge and the tail of another"""
    Wt = W.weights(T)
    heads, tails = set(), set()
    for a, nb in Wt.items():
        for b, c in nb:
            if c == 0:
                tails.add(a)
                heads.add(b)
    return heads & tails, Wt


# ------------------------------------------------------------------------------------------------ the local lemma at the vortex
def _lattice(R):
    pts = {}
    for a in range(-2 * R - 2, 2 * R + 3):
        for b in range(-2 * R - 2, 2 * R + 3):
            p = (a + b / 2.0, b * math.sqrt(3) / 2.0)
            if math.hypot(*p) <= R + 1.01:
                pts[(a, b)] = p
    edges = set()
    tris = []
    for (a, b) in pts:
        for u, v in (((a, b), (a + 1, b)), ((a, b), (a, b + 1)), ((a + 1, b), (a, b + 1))):
            if u in pts and v in pts:
                edges.add((u, v))
        for t in (((a, b), (a + 1, b), (a, b + 1)), ((a + 1, b), (a + 1, b + 1), (a, b + 1))):
            if all(q in pts for q in t):
                tris.append(t)
    return pts, edges, tris


def ray_record(theta, pts, edges, tris, R):
    """faces met, left heads and right tails of the edges a ray from the origin crosses within radius R"""
    u = (math.cos(theta), math.sin(theta))
    cr = lambda w: u[0] * w[1] - u[1] * w[0]  # noqa: E731
    crossed, left, right = set(), set(), set()
    for e in edges:
        a, b = e
        if (0, 0) in e:
            continue
        pa, pb = pts[a], pts[b]
        ca, cb = cr(pa), cr(pb)
        if ca * cb >= 0:
            continue
        s = (pa[0] * cb - pb[0] * ca) / (cb - ca), (pa[1] * cb - pb[1] * ca) / (cb - ca)
        if s[0] * u[0] + s[1] * u[1] <= 0 or math.hypot(*s) > R:
            continue
        crossed.add(e)
        (left if ca > 0 else right).add(a)
        (left if cb > 0 else right).add(b)
    faces = set()
    for t in tris:
        es = {tuple(sorted(x)) for x in itertools.combinations(t, 2)}
        if es & {tuple(sorted(e)) for e in crossed}:
            faces.add(t)
        elif (0, 0) in t:
            # the start face: the ray leaves the origin into it
            (p, q) = [pts[x] for x in t if x != (0, 0)]
            if cr(p) * cr(q) < 0 and (p[0] + q[0]) * u[0] + (p[1] + q[1]) * u[1] > 0:
                faces.add(t)
    return faces, left, right, crossed


def local_lemma(d_near=22.0, d_far=11.0, R=5.0):
    """Six rays from a lattice point at angles 30 + 60 j +- d (d_near for 90, 210, 330; d_far for 30, 150, 270).
    Over every interval between critical angles (rays through lattice points): faces met by different rays are disjoint within
    radius R, and the points that head one ray's crossed edge and tail another's (left of one, right of the other) are listed."""
    pts, edges, tris = _lattice(int(R) + 1)
    crit = sorted({math.degrees(math.atan2(p[1], p[0])) % 360 for q, p in pts.items() if q != (0, 0) and math.hypot(*p) <= R + 1})
    recs = []
    for j in range(6):
        ideal = 30 + 60 * j
        d = d_near if ideal in (90, 210, 330) else d_far
        lo, hi = ideal - d, ideal + d
        cuts = [lo] + [c for c in crit if lo < c < hi] + [c - 360 for c in crit if lo < c - 360 < hi] + [hi]
        cuts = sorted(set(cuts))
        recs.append([ray_record(math.radians((x + y) / 2), pts, edges, tris, R) for x, y in zip(cuts, cuts[1:])])
    shared, x0 = 0, set()
    per_pair = {}
    for i in range(6):
        for j in range(6):
            if i == j:
                continue
            for ri in recs[i]:
                for rj in recs[j]:
                    if i < j and ri[0] & rj[0]:
                        shared += 1
                    both = ri[1] & rj[2]
                    if both:
                        x0 |= both
                        per_pair[(i, j)] = max(per_pair.get((i, j), 0), len(both))
    hexd = lambda q: max(abs(q[0]), abs(q[1]), abs(q[0] + q[1]))  # noqa: E731
    return {"intervals per ray": [len(r) for r in recs], "pairs of intervals sharing a face": shared,
            "points that can head one arc's crossing and tail another's": len(x0),
            "largest lattice distance of such a point": max((hexd(q) for q in x0), default=0),
            "bound on |X0| (sum over ordered pairs of the largest set)": sum(per_pair.values())}


def local_lemma_disk(d=20.0, R=5.0):
    """Grid Sperner: three rays from a down-triangle's centroid at angles 90, 210, 330 (+- d). Faces met by different rays are
    disjoint within radius R, and the possible heads-and-tails of crossings by different rays are listed (as local_lemma)."""
    pts, edges, tris = _lattice(int(R) + 2)
    off = (1.0, math.sqrt(3) / 3.0)          # centroid of the down-triangle (1,0), (1,1), (0,1)
    sh = {q: (p[0] - off[0], p[1] - off[1]) for q, p in pts.items()}
    crit = sorted({math.degrees(math.atan2(p[1], p[0])) % 360 for p in sh.values()})
    recs = []
    for ideal in (90, 210, 330):
        lo, hi = ideal - d, ideal + d
        cuts = sorted(set([lo, hi] + [c for c in crit if lo < c < hi] + [c - 360 for c in crit if lo < c - 360 < hi]))
        rr = []
        for x, y in zip(cuts, cuts[1:]):
            th = math.radians((x + y) / 2)
            u = (math.cos(th), math.sin(th))
            cr = lambda w: u[0] * w[1] - u[1] * w[0]  # noqa: E731
            left, right, crossed = set(), set(), set()
            for e in edges:
                a, b = e
                pa, pb = sh[a], sh[b]
                ca, cb = cr(pa), cr(pb)
                if ca * cb >= 0:
                    continue
                s = (pa[0] * cb - pb[0] * ca) / (cb - ca), (pa[1] * cb - pb[1] * ca) / (cb - ca)
                if s[0] * u[0] + s[1] * u[1] <= 0 or math.hypot(*s) > R:
                    continue
                crossed.add(tuple(sorted(e)))
                (left if ca > 0 else right).add(a)
                (left if cb > 0 else right).add(b)
            faces = {t for t in tris if {tuple(sorted(x)) for x in itertools.combinations(t, 2)} & crossed}
            rr.append((faces, left, right))
        recs.append(rr)
    shared, x0, per = 0, set(), {}
    for i in range(3):
        for j in range(3):
            if i != j:
                for ri in recs[i]:
                    for rj in recs[j]:
                        both = ri[1] & rj[2]
                        if both:
                            x0 |= both
                            per[(i, j)] = max(per.get((i, j), 0), len(both))
    # faces shared beyond the vortex triangle itself
    vt = None
    for t in tris:
        c = (sum(sh[q][0] for q in t) / 3, sum(sh[q][1] for q in t) / 3)
        if math.hypot(*c) < 1e-9:
            vt = t
    for i in range(3):
        for j in range(i + 1, 3):
            for ri in recs[i]:
                for rj in recs[j]:
                    if (ri[0] & rj[0]) - {vt}:
                        shared += 1
    return {"vortex triangle points down": vt is not None and sum(1 for q in vt if sh[q][1] > 0) == 2,
            "intervals per ray": [len(r) for r in recs], "pairs of intervals sharing a face": shared,
            "points that can head one arc's crossing and tail another's": len(x0),
            "bound on |X0|": sum(per.values())}


# ------------------------------------------------------------------------------------------------ grid Sperner with three straight arcs
sys.path.insert(0, str(ROOT / "proofs/FLAT-STATES-20261107-001B/FLAT-STATES-20261107-001B-P001_the_knot_sphere_contains_sperner"))
import window_lib as SW  # noqa: E402


def sperner(m):
    V, tris, E = SW.grid(m)
    adj = {v: [] for v in V}
    for u, v in E:
        adj[u].append(v)
        adj[v].append(u)
    col = SW.boundary_colours(m)
    doors = [((0, 0), (1, 0)), ((m, 0), (m - 1, 1)), ((0, m), (0, m - 1))]
    centre = (m / 3.0 + m / 6.0, m * math.sqrt(3) / 6.0)
    return dict(m=m, V=V, tris=tris, E=E, adj=adj, bcol=col, doors=doors, centre=centre)


def hexdist(u, v):
    da, db = u[0] - v[0], u[1] - v[1]
    return max(abs(da), abs(db), abs(da + db))


def sperner_core(S, radius):
    """down-triangles whose centroid is within Euclidean distance radius of the grid's centre"""
    out = []
    for t in S["tris"]:
        c = [sum(SW.pos(q)[i] for q in t) / 3 for i in range(2)]
        up = sum(1 for q in t if SW.pos(q)[1] > c[1]) == 1
        if not up and math.hypot(c[0] - S["centre"][0], c[1] - S["centre"][1]) <= radius:
            out.append(t)
    return out


def sperner_cut(S, T, turn=1e-3):
    """shifts tau on directed edges for the three straight arcs from T's centroid across the three doors, and the frames phi"""
    c = [sum(SW.pos(q)[i] for q in T) / 3 for i in range(2)]
    tau = {}
    for (u, v) in S["doors"]:
        pu, pv = SW.pos(u), SW.pos(v)
        mid = ((pu[0] + pv[0]) / 2, (pu[1] + pv[1]) / 2)
        dx, dy = mid[0] - c[0], mid[1] - c[1]
        L = math.hypot(dx, dy)
        Q = (mid[0] + 0.3 * dx / L - turn * dy / L, mid[1] + 0.3 * dy / L + turn * dx / L)    # just outside the door
        ux, uy = Q[0] - c[0], Q[1] - c[1]
        for a, b in S["E"]:
            pa, pb = SW.pos(a), SW.pos(b)
            ca = ux * (pa[1] - c[1]) - uy * (pa[0] - c[0])
            cb = ux * (pb[1] - c[1]) - uy * (pb[0] - c[0])
            if ca * cb >= 0:
                continue
            s = _cross(c, Q, pa, pb)
            if s is None:
                continue
            # crossing from the arc's right (ca < 0) to its left counts +1 for a -> b
            t = 1 if ca < 0 else -1
            if (a, b) in tau or (b, a) in tau:
                raise ValueError("an edge is crossed twice")
            tau[(a, b)], tau[(b, a)] = t, -t
    phi = {S["V"][0]: 0}
    dq = deque([S["V"][0]])
    while dq:
        u = dq.popleft()
        for v in S["adj"][u]:
            f = (phi[u] + tau.get((u, v), 0)) % 3
            if v in phi:
                if phi[v] != f:
                    raise ValueError("frames disagree")
            else:
                phi[v] = f
                dq.append(v)
    return dict(T=T, tau=tau, phi=phi)


def sperner_weights(S, C):
    W = {v: [] for v in S["V"]}
    for u, v in S["E"]:
        t = C["tau"].get((u, v), 0)
        W[u].append((v, 1 - t))
        W[v].append((u, 1 + t))
    return W


def sperner_flat(S, C):
    """the flat state: label = boundary window start everywhere; its fully labelled triangles"""
    starts = {(b, (col - C["phi"][b]) % 3) for b, col in S["bcol"].items()}
    a0 = next(iter(starts))[1]
    colour = {v: (a0 + C["phi"][v]) % 3 for v in S["V"]}
    full = [t for t in S["tris"] if len({colour[q] for q in t}) == 3]
    return {b for b, s in starts}, {s for b, s in starts}, colour, full


# ------------------------------------------------------------------------------------------------ islands
def packing(K, sep, rng, corner_gap=5):
    """greedy random centres: island balls of radius 1, pairwise at least sep apart, centres at least corner_gap from corner points"""
    dcor = F.dist_from(K["adj"], list(K["corner_pts"]))
    cand = [p for p in range(K["n"]) if dcor[p] >= corner_gap]
    rng.shuffle(cand)
    blocked = [False] * K["n"]
    centres = []
    for c in cand:
        if blocked[c]:
            continue
        centres.append(c)
        dc = F.dist_from(K["adj"], [c])
        for p in range(K["n"]):
            if dc[p] < sep + 2:
                blocked[p] = True
    return centres


def island_colours(K, centres, rng):
    """each island B(c, 1) gets one uniform label in a frame developed inside it; returns {point: colour}, {point: island}"""
    col, isl = {}, {}
    for i, c in enumerate(centres):
        pts = {c} | set(K["adj"][c])
        fr = {c: (0, 0)}
        dq = deque([c])
        while dq:
            a = dq.popleft()
            for l in K["lines_of"][a]:
                for b in K["lines"][l]:
                    if b in pts and b not in fr:
                        o, e = F.step(K, l, a, b)
                        fr[b] = ((fr[a][0] + o) % 3, fr[a][1] ^ e)
                        dq.append(b)
        lab = rng.randrange(6)
        for p in pts:
            col[p] = F.PATTERNS[lab][fr[p][0]] ^ fr[p][1]
            isl[p] = i
    return col, isl


def island_lifts(K, T, col, isl, centres):
    """the islands' lifted labels lambda in the gauge T: lambda_b = lambda_a - t(a, b) inside an island, residue fixed by the colours"""
    lam = {}
    for i, c in enumerate(centres):
        pts = [p for p in isl if isl[p] == i]
        rel = {c: 0}
        dq = deque([c])
        while dq:
            a = dq.popleft()
            for b in pts:
                if b not in rel and (a, b) in T["shift"]:
                    rel[b] = rel[a] - max(T["shift"][(a, b)])
                    dq.append(b)
        fits = [l0 for l0 in range(6) if all(F.PATTERNS[(l0 + rel[p]) % 6][T["fr"][p][0]] ^ T["fr"][p][1] == col[p] for p in pts)]
        if len(fits) != 1:
            raise ValueError("island is not a constant-label state")
        for p in pts:
            lam[p] = fits[0] + rel[p]
    return lam
