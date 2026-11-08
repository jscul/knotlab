"""Distance across time (DISTANCE-20261108-001), on GENUS-CUT-20261108-001A's genus_lib and the libraries under it.

A network is (sizes, contacts) in SEPARATE-20261108-001A's net_lib format: rule-60 rings joined by contacts with law (12, 12), each
reading its left neighbour on both of its rings. The contact graph has an arc d -> e for every corner, the own cells on a ring between
a contact d and the next contact e (loopnet_lib.corners). A route is a directed path c_0 -> c_1 -> ... -> c_L of the contact graph,
from a ring X holding c_0 and no other contact of the route; it is chordless when no arc c_i -> c_j with j > i + 1 joins two of its
contacts. Isolating a route freezes every contact off it (A38: c <- c). The cell-level reading follows rows of M^T (net_lib): the row
of a contact after T steps is the set of first-row cells its value at lag T depends on, mod 2, and the contact needs ring X at lag T
when that set meets X's own cells."""
from __future__ import annotations

import collections
import itertools
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/GENUS-CUT-20261108-001A/GENUS-CUT-20261108-001A-P001_two_rings_of_cuts_per_handle"))
import genus_lib as Gl  # noqa: E402

LN, T, N = Gl.LN, Gl.T, Gl.N
LAW = LN.LAW


# ---------- networks
def regular_map(G, mul, one, x, y):
    """the orientably regular map of a group with x (vertex rotation) and y (an involution): darts are the elements, a vertex is a
    coset g<x>, an edge {g, gy}, and the rotation at a vertex follows h -> hx (as genus_lib.gl23_maps)"""
    vert = {}
    for g in G:
        if g not in vert:
            h = g
            while True:
                vert[h] = g
                h = mul(h, x)
                if h == g:
                    break
    edge_of, edges = {}, []
    for g in G:
        if g not in edge_of:
            gy = mul(g, y)
            edge_of[g] = edge_of[gy] = len(edges)
            edges.append((vert[g], vert[gy]))
    rot = {}
    for g in G:
        if vert[g] not in rot:
            cyc, h = [], g
            while True:
                cyc.append(edge_of[h])
                h = mul(h, x)
                if h == g:
                    break
            rot[vert[g]] = cyc
    return rot, edges


def psl27_maps():
    """orientably regular maps from PSL(2,7) (2 x 2 matrices over GF(7) of determinant 1, up to sign), keyed (vertex degree, face
    degree): (3, 7) is the Klein quartic map {7,3} of genus 3 (56 rings of three contacts), (7, 3) its dual (24 rings of seven)"""
    def norm(m):
        for v in m:
            if v:
                return m if v <= 3 else tuple((-u) % 7 for u in m)
        return m
    G = sorted({norm(m) for m in itertools.product(range(7), repeat=4) if (m[0] * m[3] - m[1] * m[2]) % 7 == 1})
    one = (1, 0, 0, 1)

    def mul(a, b):
        return norm(((a[0] * b[0] + a[1] * b[2]) % 7, (a[0] * b[1] + a[1] * b[3]) % 7,
                     (a[2] * b[0] + a[3] * b[2]) % 7, (a[2] * b[1] + a[3] * b[3]) % 7))

    def order(m):
        k, p = 1, m
        while p != one:
            p, k = mul(p, m), k + 1
        return k

    def generated(gens):
        S, todo = {one}, [one]
        while todo:
            a = todo.pop()
            for g in gens:
                b = mul(a, g)
                if b not in S:
                    S.add(b)
                    todo.append(b)
        return S
    assert len(G) == 168
    out = {}
    for key in ((3, 7), (7, 3)):
        found = next((x, y) for x in G if order(x) == key[0] for y in G
                     if order(y) == 2 and order(mul(x, y)) == key[1] and len(generated([x, y])) == 168)
        out[key] = regular_map(G, mul, one, *found)
    return out


def substrates():
    """the frozen roster of DISTANCE-20261108-001A-E001: name -> (rot, edges)"""
    out = {}
    for n in (5, 6, 7):
        out["square torus %d" % n] = LN.square_torus(n)
    for n in (4, 5):
        out["triangular torus %d" % n] = LN.triangular_torus(n)
    for n in (3, 4, 5):
        out["honeycomb torus %d" % n] = LN.honeycomb_torus(n)
    gl = Gl.gl23_maps()
    out["genus 2, 16 rings of three contacts (GL(2,3))"] = gl[(3, 8)]
    out["genus 2, 6 rings of eight contacts (GL(2,3))"] = gl[(8, 3)]
    ps = psl27_maps()
    out["genus 3, 56 rings of three contacts (Klein quartic, PSL(2,7))"] = ps[(3, 7)]
    out["genus 3, 24 rings of seven contacts (PSL(2,7))"] = ps[(7, 3)]
    for name in ("tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"):
        out[name] = LN.platonic(name)
    return out


def network_gaps(rot, edges, rng, lo=2, hi=5):
    """rings with unequal corners: consecutive contacts on a ring lo .. hi cells apart (lo >= 2 keeps every left neighbour an own
    cell), positions in the rotation's order"""
    verts = sorted(rot, key=repr)
    idx = {v: i for i, v in enumerate(verts)}
    pos, sizes = {}, []
    for v in verts:
        p = 0
        for e in rot[v]:
            pos[(v, e)] = p
            p += rng.randint(lo, hi)
        sizes.append(p)
    return tuple(sizes), [(idx[u], pos[(u, e)], idx[w], pos[(w, e)], LAW) for e, (u, w) in enumerate(edges)]


# ---------- the contact graph
def graph(sizes, contacts):
    """out-arcs {d: [(e, ring, l)]}, in-arcs {e: [(d, ring, l)]}, and each ring's contacts"""
    out, inn = collections.defaultdict(list), collections.defaultdict(list)
    for d, e, ring, l in LN.corners(sizes, contacts):
        out[d].append((e, ring, l))
        inn[e].append((d, ring, l))
    rc = collections.defaultdict(set)
    for c, (ra, pa, rb, pb, law) in enumerate(contacts):
        rc[ra].add(c)
        rc[rb].add(c)
    return out, inn, rc


def dist_from(out, sources, n):
    """directed distance (in arcs) from a set of contacts to every contact"""
    dist = [None] * n
    q = collections.deque()
    for s in sources:
        dist[s] = 0
        q.append(s)
    while q:
        x = q.popleft()
        for y, ring, l in out[x]:
            if dist[y] is None:
                dist[y] = dist[x] + 1
                q.append(y)
    return dist


def rings_of(contacts, c):
    ra, pa, rb, pb, law = contacts[c]
    return ra, rb


def chordless(out, route):
    """no arc c_i -> c_j with j > i + 1"""
    at = {c: i for i, c in enumerate(route)}
    return all(not (y in at and at[y] > i + 1) for i, c in enumerate(route) for y, ring, l in out[c])


def valid_route(out, rc, contacts, route, X):
    """distinct contacts, c_0 the only one on X, each hop along exactly one corner, and chordless"""
    if len(set(route)) != len(route) or route[0] not in rc[X] or any(c in rc[X] for c in route[1:]):
        return False
    if any(sum(y == b for y, ring, l in out[a]) != 1 for a, b in zip(route, route[1:])):
        return False
    return chordless(out, route)


def parallel_arcs(out):
    """pairs of contacts joined by two or more corners"""
    return sum(1 for d in out for e in {y for y, ring, l in out[d]} if sum(y == e for y, ring, l in out[d]) > 1)


def hop_ring(out, a, b):
    return next(ring for y, ring, l in out[a] if y == b)


def shortest_route(rng, out, inn, rc, n, X, L):
    """a random shortest route of L arcs from ring X, or None: a contact at distance L, traced back through random predecessors"""
    dist = dist_from(out, rc[X], n)
    ends = [c for c in range(n) if dist[c] == L]
    if not ends:
        return None
    route = [rng.choice(ends)]
    while dist[route[-1]] > 0:
        route.append(rng.choice(sorted({d for d, ring, l in inn[route[-1]] if dist[d] == dist[route[-1]] - 1})))
    return route[::-1]


def random_route(rng, out, rc, n, X, L, tries=200):
    """a random chordless route of L arcs from ring X (not necessarily shortest), or None"""
    for _ in range(tries):
        route = [rng.choice(sorted(rc[X]))]
        while len(route) <= L:
            on = set(route)
            cand = sorted({y for y, ring, l in out[route[-1]]
                           if y not in on and y not in rc[X]
                           and not any(z == y for c in route[:-1] for z, r2, l2 in out[c])})
            if not cand:
                break
            route.append(rng.choice(cand))
        if len(route) == L + 1:
            return route
    return None


def hop_cells(out, route):
    """the cells each hop carries influence through: its corner's own cells plus the contact it reaches"""
    return [next(l for y, ring, l in out[a] if y == b) + 1 for a, b in zip(route, route[1:])]


# ---------- the cell-level reading
def first_need(sizes, contacts, target, X, horizon, cut=()):
    """the first lag <= horizon at which the target contact's value depends on ring X's own first-row cells, or None; read from
    rows of M^T with the cut contacts frozen"""
    rows, Nb, blocks = N.matrix(sizes, (60,) * len(sizes), contacts, cut=tuple(cut))
    mask = N.mask(blocks, X)
    row = 1 << target
    for t in range(1, horizon + 1):
        row = LN.step(rows, row)
        if row & mask:
            return t
    return None


def isolated_first_need(sizes, contacts, route, X, horizon):
    on = set(route)
    return first_need(sizes, contacts, route[-1], X, horizon, cut=[c for c in range(len(contacts)) if c not in on])
