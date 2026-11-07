"""Flat (label) states on the whole octahedral knot sphere K_k, for FLAT-STATES-20261107-001A.

Frames. A frame at a point is a sublattice index in Z3 and a sign gauge in Z2. Moving from a to b inside a line l shifts the sublattice by
+1 or -1 (b after or before a in the line's cyclic order in the plane embedding) and the gauge by the relative sign of a and b in l.
In a common frame the line is plain not-all-equal on three distinct sublattices, so a constant label colours it not-all-equal.

Holonomy. Going once around a face of the incidence graph composes these moves. Around a three-point face nothing changes; around each
of the six two-point faces (the octahedron's corners) the composite is a sublattice turn plus a complement, which acts on labels as a
shift by -1 (label 5).

Flat states. Cut the sphere along six disjoint paths of the line-face graph from the six triangles around a point z to the six corner
faces, develop one frame over what remains (z excluded), and colour every point by the label-0 pattern in its frame. Every line then
sees labels within two consecutive values except the lines at z, whose neighbours carry the six labels in cyclic order: z is a vortex.
"""
import random
import sys
from collections import deque
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "proofs/TWO-ROUND-BRIDGE-20261106-001B/TWO-ROUND-BRIDGE-20261106-001B-P001_three_fold_spaces_are_an_euler_count"))
import count_lib as C  # noqa: E402

PATTERNS = [(0, 1, 1), (0, 0, 1), (1, 0, 1), (1, 0, 0), (1, 1, 0), (0, 1, 0)]   # S0..S5 on sublattices (0, 1, 2)


def build(k):
    """K_k with its plane embedding: lines, signs, the cyclic order of each line's points, corners (l, a, b, face) and face point sets"""
    lines, signs, n = C.signed_space(C.octa_dual(k))
    g = nx.Graph()
    for i, L in enumerate(lines):
        for p in L:
            g.add_edge(("p", p), ("l", i))
    ok, emb = nx.check_planarity(g)
    assert ok
    rot = {i: [v[1] for v in emb.neighbors_cw_order(("l", i))] for i in range(len(lines))}
    cs, fpts = C.corners(lines, n)
    sgn = [{p: s for p, s in zip(L, S)} for L, S in zip(lines, signs)]
    return dict(k=k, lines=lines, signs=signs, n=n, rot=rot, corners=cs, fpts=fpts, sgn=sgn)


def step(K, l, a, b):
    """frame move a -> b inside line l: (sublattice shift, gauge flip)"""
    r = K["rot"][l]
    i = r.index(a)
    return (1 if r[(i + 1) % 3] == b else -1), K["sgn"][l][a] ^ K["sgn"][l][b]


def face_holonomy(K, fi):
    """composite move once around face fi along its traversal: (sublattice shift mod 3, gauge flip, label shift mod 6)"""
    cs = [(l, a, b) for (l, a, b, f) in K["corners"] if f == fi]
    d = sum(step(K, l, a, b)[0] for l, a, b in cs) % 3
    e = sum(step(K, l, a, b)[1] for l, a, b in cs) % 2
    return d, e, (2 * d + 3 * e) % 6


def corner_faces(K):
    return [fi for fi, P in enumerate(K["fpts"]) if len(P) == 2]


def gamma(K):
    """the line-face graph: one vertex per line ('l', i) and face ('f', j), one edge per corner, keyed by its point pair"""
    G = nx.Graph()
    for (l, a, b, f) in K["corners"]:
        G.add_edge(("l", l), ("f", f), pair=frozenset((a, b)))
    return G


def triangles_at(K, G, z):
    return [v for v in G if (v[0] == "l" and z in K["lines"][v[1]]) or (v[0] == "f" and z in K["fpts"][v[1]])]


def disjoint_paths(G, sources, sinks, banned_pairs_with, rng=None, allowed=None):
    """vertex-disjoint paths in G from the sources to the sinks (min-cost flow; random weights when rng is given); edges whose point pair
    contains banned_pairs_with are not used; allowed restricts the vertices; None when no such system exists"""
    H = nx.DiGraph()
    for u, v, d in G.edges(data=True):
        if banned_pairs_with in d["pair"]:
            continue
        if allowed is not None and (u not in allowed or v not in allowed):
            continue
        w = 1 if rng is None else rng.randint(1, 4)
        H.add_edge((u, "o"), (v, "i"), capacity=1, weight=w)
        H.add_edge((v, "o"), (u, "i"), capacity=1, weight=w)
    for v in G:
        if allowed is None or v in allowed:
            H.add_edge((v, "i"), (v, "o"), capacity=1, weight=0)
    for v in sources:
        H.add_edge("S", (v, "i"), capacity=1, weight=0)
    for v in sinks:
        H.add_edge((v, "o"), "T", capacity=1, weight=0)
    flow = nx.max_flow_min_cost(H, "S", "T")
    if sum(flow["S"].values()) != len(sources):
        return None
    sinks = set(sinks)
    paths = []
    for v in sources:
        p, cur = [v], v
        while cur not in sinks:
            cur = next(y for y, f in flow[(cur, "o")].items() if f > 0 and y != "T")[0]
            p.append(cur)
        paths.append(p)
    return paths


def cut_star(K, G, z, rng=None):
    return disjoint_paths(G, triangles_at(K, G, z), [("f", fi) for fi in corner_faces(K)], z, rng)


def develop(K, z, paths, base):
    """frames developed from base over the sphere cut along the paths, z excluded; {point: (sublattice, gauge)}"""
    cut = {frozenset((u, v)) for p in paths for u, v in zip(p, p[1:])}
    blocked = {(l, frozenset((a, b))) for (l, a, b, f) in K["corners"] if frozenset((("l", l), ("f", f))) in cut}
    frame = {base: (0, 0)}
    dq = deque([base])
    while dq:
        a = dq.popleft()
        for l in K["lines_of"][a]:
            for b in K["lines"][l]:
                if b == a or b == z or (l, frozenset((a, b))) in blocked:
                    continue
                o, e = step(K, l, a, b)
                fb = ((frame[a][0] + o) % 3, frame[a][1] ^ e)
                if b in frame:
                    assert frame[b] == fb, ("frames disagree", a, b)
                else:
                    frame[b] = fb
                    dq.append(b)
    return frame


def index_lines(K):
    K["lines_of"] = [[] for _ in range(K["n"])]
    for l, L in enumerate(K["lines"]):
        for p in L:
            K["lines_of"][p].append(l)
    return K


def flat_state(K, z, paths, base, z_colour=0):
    frame = develop(K, z, paths, base)
    assert len(frame) == K["n"] - 1
    x = [None] * K["n"]
    for p, (s, g) in frame.items():
        x[p] = PATTERNS[0][s] ^ g
    x[z] = z_colour
    return x


def violated(K, x):
    return [l for l, (L, S) in enumerate(zip(K["lines"], K["signs"])) if len({x[p] ^ s for p, s in zip(L, S)}) == 1]


def point_graph(K):
    adj = [set() for _ in range(K["n"])]
    for L in K["lines"]:
        for a in L:
            adj[a].update(b for b in L if b != a)
    return adj


def dist_from(adj, srcs):
    d = {s: 0 for s in srcs}
    dq = deque(srcs)
    while dq:
        u = dq.popleft()
        for v in adj[u]:
            if v not in d:
                d[v] = d[u] + 1
                dq.append(v)
    return d


def vertex_points(K, v):
    return K["lines"][v[1]] if v[0] == "l" else K["fpts"][v[1]]


def vortex_step(K, G, adj, z, paths, z2, r, rng=None):
    """move the vortex from z to the adjacent point z2 by re-routing the star only inside the ball of radius r around z: keep each path
    from its first vertex outside the ball on, and join the six triangles around z2 to those vertices by disjoint paths inside the ball"""
    d = dist_from(adj, [z])
    inside = {v for v in G if max(d.get(p, 99) for p in vertex_points(K, v)) <= r}
    exits, tails = [], []
    for p in paths:
        j = next((t for t, v in enumerate(p) if v not in inside), None)
        if j is None or any(v in inside for v in p[j:]):
            return None          # a path that never leaves the ball, or re-enters it
        exits.append(p[j])
        tails.append(p[j:])
    allowed = inside | set(exits)
    heads = disjoint_paths(G, triangles_at(K, G, z2), exits, z2, rng, allowed=allowed)
    if heads is None:
        return None
    by_exit = {t[0]: t for t in tails}
    return [h[:-1] + by_exit[h[-1]] for h in heads], {p for v in inside for p in vertex_points(K, v)}
