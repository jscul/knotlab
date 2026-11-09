"""Distance on the band-grown torus (GROWN-DISTANCE-20261109-001A), on PLAIN-TIME-20261108-001A's plain_lib and GROW-NET-20261108-001A's
grow_lib.

The band law (BAND-SURFACE-20261108-001A, GROW-NET-20261108-001A) keeps a loop's n rings and adds bands: its stages are the n x 2 ladder,
then the n x m torus for m = 3, 4, .... A torus of the square, triangular or honeycomb lattice is the lattice modulo a sublattice L of
translations, any sublattice, not only the rotation-invariant ones of PLAIN-TIME-20261108-001B; L is given by its Hermite basis
((a, 0), (b, c)) with 0 <= b < a, which lists each sublattice of index a c once. Rings list their contacts counterclockwise (E, N, W, S
on the square lattice), as in plain_lib.lattice_torus, and are read as equally spaced networks of rule-60 rings with law (12, 12)
contacts through loopnet_lib. The plain first need of contact c on ring r is on time when it comes at the directed distance
delta(r -> c): by DISTANCE-20261108-001B, Theorem 4, exactly when an odd number of shortest routes lead to c from one of r's contacts at
distance delta(r -> c) (plain_lib.verdicts reads it, and also the least odd walk length, exactly)."""
from __future__ import annotations

import collections
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/PLAIN-TIME-20261108-001A/PLAIN-TIME-20261108-001A-E001_map_census"))
sys.path.insert(0, str(ROOT / "proofs/GROW-NET-20261108-001A/GROW-NET-20261108-001A-P001_bands_grow_single_rings_do_not"))
import plain_lib as P  # noqa: E402
import grow_lib as G  # noqa: E402

LN, D = P.LN, P.D
SQUARE_DIRS = ((1, 0), (0, 1), (-1, 0), (0, -1))
TRI_DIRS = ((1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1))


# ---------- tori of every shape
def torus(kind, B):
    """(rot, edges) of the kind's lattice modulo the sublattice with basis rows B, or None when a contact would join a ring to itself"""
    det = B[0][0] * B[1][1] - B[0][1] * B[1][0]
    if det < 0:
        B, det = (B[1], B[0]), -det
    red = lambda v: P.reduce_mod(v, B)
    pts = sorted({red((i, j)) for i in range(-det, det + 1) for j in range(-det, det + 1)})
    assert len(pts) == det
    if kind in ("square", "triangular"):
        dirs = SQUARE_DIRS if kind == "square" else TRI_DIRS
        edges, eid = [], {}
        for v in pts:
            for d in dirs[:len(dirs) // 2]:
                w = red((v[0] + d[0], v[1] + d[1]))
                if w == v:
                    return None
                eid[(v, d)] = eid[(w, (-d[0], -d[1]))] = len(edges)
                edges.append((v, w))
        return {v: [eid[(v, d)] for d in dirs] for v in pts}, edges
    verts = [(p, s) for p in pts for s in (0, 1)]
    edges, rot = [], {v: [None] * 3 for v in verts}
    for p in pts:
        for k, q in enumerate((p, red((p[0] - 1, p[1])), red((p[0], p[1] - 1)))):
            rot[(p, 0)][k] = rot[(q, 1)][k] = len(edges)
            edges.append(((p, 0), (q, 1)))
    return rot, edges


def hermite_bases(index_max, index_min=3):
    """every sublattice of Z^2 of index index_min to index_max, once: ((a, 0), (b, c)), 0 <= b < a (index 1 and 2 only for the
    honeycomb, where they give the networks of 2 and 4 rings; on the square and triangular lattices they join a ring to itself or
    pair every contact)"""
    for a in range(1, index_max + 1):
        for c in range(1, index_max // a + 1):
            if a * c >= index_min:
                for b in range(a):
                    yield ((a, 0), (b, c))


def norm2(kind, v):
    """squared length: the square lattice in its own basis, the triangular and honeycomb translations in a basis at 120 degrees"""
    return v[0] * v[0] + v[1] * v[1] if kind == "square" else v[0] * v[0] - v[0] * v[1] + v[1] * v[1]


def shortest(kind, B):
    best = None
    for i in range(-6, 7):
        for j in range(-6, 7):
            if (i, j) != (0, 0):
                v = (i * B[0][0] + j * B[1][0], i * B[0][1] + j * B[1][1])
                k = (norm2(kind, v), v)
                if best is None or k < best:
                    best = k
    return best


# ---------- the plain first need
def targets(kind):
    """contacts of the first ring point, one per orbit of the translations (contact ids follow torus()'s edge order)"""
    return (0, 1) if kind == "square" else (0, 1, 2)


def reading(rot, edges, kind):
    """{target: verdicts} for one contact of each translation orbit"""
    sizes, contacts = LN.network(rot, edges, 2)
    n, out, rc = P.network_map(sizes, contacts)
    return {t: P.verdicts(n, out, rc, t) for t in targets(kind)}


def on_time(rot, edges, kind):
    v = reading(rot, edges, kind)
    return all(x["rings late"] == 0 and x["rings never"] == 0 and x["cone mismatches"] == 0 for x in v.values()), v


def routes_to(out, n, target):
    """directed distance and number of shortest routes from every contact to the target"""
    inn = [[] for _ in range(n)]
    for d in range(n):
        for e in out[d]:
            inn[e].append(d)
    dist, cnt = [None] * n, [0] * n
    dist[target], cnt[target] = 0, 1
    order, q = [target], collections.deque([target])
    while q:
        a = q.popleft()
        for b in inn[a]:
            if dist[b] is None:
                dist[b] = dist[a] + 1
                q.append(b)
                order.append(b)
    for b in order[1:]:
        cnt[b] = sum(cnt[e] for e in out[b] if dist[e] == dist[b] - 1)
    return dist, cnt


def first_late(rot, edges, target, radius):
    """the least directed distance <= radius at which a ring is late for the target (route counts), or None"""
    sizes, contacts = LN.network(rot, edges, 2)
    n, out, rc = P.network_map(sizes, contacts)
    dist, cnt = routes_to(out, n, target)
    late = None
    for cs in rc:
        if target in cs:
            continue
        dr = min(dist[e] for e in cs)
        if dr <= radius and not any(dist[e] == dr and cnt[e] % 2 for e in cs) and (late is None or dr < late):
            late = dr
    return late


def cylinder_first_late(n, radius):
    """the first late distance of the cylinder Z_n x Z, read on the n x M torus with M = radius + 6: an arc moves a contact by at most
    1/2 along the cylinder, so lifts of a contact by (0, M) are at least 2M > 2 radius + 4 apart and the torus's distances and route
    counts up to the radius are the cylinder's (PLAIN-TIME-20261108-001B, proof of Theorem 3)"""
    rot, edges = G.rect_torus(n, radius + 6)
    return {kind: first_late(rot, edges, t, radius) for kind, t in (("h", 0), ("v", 1))}


# ---------- the ladder's cover Z x Z_2: closed forms of the proof of Theorem 2
def ladder_cover_forms(target, i, level):
    """(least distance, minimising contact's role) of the ring lift (i, level) of the cover Z x Z_2 for the target h(0, 0) or v(0, 0),
    by Theorem 2's tables; None for a ring holding the target"""
    if target == "h":
        if level == 0:
            return None if i in (0, 1) else ((2 * i - 2, "W") if i >= 1 else (-2 * i, "E"))
        return (2 * i - 1, "S") if i >= 1 else (-2 * i + 1, "N")
    if level == 0:
        return None if i == 0 else ((2 * i - 1, "W") if i >= 1 else (-2 * i, "N"))
    return None if i == 0 else ((2 * i, "S") if i >= 1 else (-2 * i - 1, "E"))


# ---------- balls
def ring_ball_sizes(n, m, rmax):
    """rings within ring-graph distance r of a ring of the n x m torus (m = None: the cylinder Z_n x Z), by the closed form
    sum over rows b of min(n, 2 (r - |b|) + 1), |b| the row's circular distance"""
    out = []
    for r in range(rmax + 1):
        rows = range(-r, r + 1) if m is None else range(m)
        tot = 0
        for b in rows:
            bb = abs(b) if m is None else min(b % m, -b % m)
            if bb <= r:
                tot += min(n, 2 * (r - bb) + 1)
        out.append(tot)
    return out


def ring_ball_bfs(n, m, rmax):
    rot, edges = G.rect_torus(n, m)
    nb = collections.defaultdict(set)
    for u, v in edges:
        nb[u].add(v)
        nb[v].add(u)
    dist = {(0, 0): 0}
    q = collections.deque([(0, 0)])
    while q:
        a = q.popleft()
        for b in nb[a]:
            if b not in dist:
                dist[b] = dist[a] + 1
                q.append(b)
    return [sum(1 for d in dist.values() if d <= r) for r in range(rmax + 1)]


def time_ball_sizes(n, m, target, rmax):
    """rings X with delta(X -> target) <= t, t = 0 .. rmax, read from the contact graph"""
    rot, edges = G.rect_torus(n, m)
    sizes, contacts = LN.network(rot, edges, 2)
    nc, out, rc = P.network_map(sizes, contacts)
    dist, cnt = routes_to(out, nc, target)
    dr = [min(dist[e] for e in cs) for cs in rc]
    return [sum(1 for d in dr if d <= t) for t in range(rmax + 1)]
