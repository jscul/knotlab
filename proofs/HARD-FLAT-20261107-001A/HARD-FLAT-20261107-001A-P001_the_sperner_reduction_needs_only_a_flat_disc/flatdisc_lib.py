"""The Sperner reduction needs only a flat disc, for HARD-FLAT-20261107-001A.

`build_general(S)` gives any two-kind sphere (co-lines of two or three points) the data model of FLAT-STATES-20261107-001A's
`flat_lib`: lines as point triples, a Kasteleyn signing (no even co-line) per line point, the rotation of each line's points in a
plane embedding of the incidence graph, its corners and faces. Then `flat_lib`'s face holonomy, cut star, development and flat states
run unchanged. `flat_radius(S)` is the largest r for which some ball of radius r in the vertex graph of T is a corner-free embedded
hexagon (3r^2 + 3r + 1 vertices, all of degree 6). `rim_paths` asks for six disjoint cut paths in the line-face graph from faces on
the rim of that ball, in three adjacent pairs, to the six corner faces, avoiding the ball."""
import sys
from collections import deque
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/FLAT-STATES-20261107-001A/FLAT-STATES-20261107-001A-P001_flat_states_exist_on_the_whole_sphere"))
sys.path.insert(0, str(ROOT / "proofs/GROW-COIN-20261107-001A/GROW-COIN-20261107-001A-P001_refinement_shares_its_coin_accretion_must_carry_it"))
import flat_lib as F  # noqa: E402
import growth_lib as GL  # noqa: E402
SM = GL.SM
C = F.C


def build_general(S):
    K = SM.SL.KnotSpace(S)
    s = K.signing(())
    lines = [tuple(K.pt[i]) for i in range(K.n)]
    signs = [tuple(s[3 * i + k] for k in range(3)) for i in range(K.n)]
    g = nx.Graph()
    for i, L in enumerate(lines):
        for p in L:
            g.add_edge(("p", p), ("l", i))
    ok, emb = nx.check_planarity(g)
    assert ok
    rot = {i: [v[1] for v in emb.neighbors_cw_order(("l", i))] for i in range(len(lines))}
    cs, fpts = C.corners(lines, K.n)
    sgn = [{p: x for p, x in zip(L, Sg)} for L, Sg in zip(lines, signs)]
    D = dict(k=None, lines=lines, signs=signs, n=K.n, rot=rot, corners=cs, fpts=fpts, sgn=sgn, K=K, S=S)
    return F.index_lines(D)


def holonomies(D):
    """label shift around each face of the incidence graph, grouped by the face's number of points"""
    out = {}
    for fi, P in enumerate(D["fpts"]):
        out.setdefault(len(P), set()).add(F.face_holonomy(D, fi)[2])
    return {k: sorted(v) for k, v in sorted(out.items())}


def flat_states(D, rng, tries):
    """flat states at random vortex positions: (vortex, violated lines) for each one that has a cut star"""
    G = F.gamma(D)
    out = []
    for _ in range(tries):
        z = rng.randrange(D["n"])
        paths = F.cut_star(D, G, z, rng)
        if paths is None:
            continue
        base = next(p for p in range(D["n"]) if p != z)
        x = F.flat_state(D, z, paths, base)
        out.append((z, F.violated(D, x)))
    return out


def vgraph(S):
    adj = {}
    for t in range(S.nt):
        V = S.vert[t]
        for a in V:
            adj.setdefault(a, set()).update(b for b in V if b != a)
    return adj


def ball(adj, v, r):
    dist = {v: 0}
    dq = deque([v])
    while dq:
        x = dq.popleft()
        if dist[x] == r:
            continue
        for y in adj[x]:
            if y not in dist:
                dist[y] = dist[x] + 1
                dq.append(y)
    return dist


def flat_radius(S):
    adj = vgraph(S)
    deg = {v: len(adj[v]) for v in adj}
    best, arg = 0, None
    for v in sorted(adj):
        r = 0
        while True:
            dist = ball(adj, v, r + 1)
            if len(dist) == 3 * (r + 1) ** 2 + 3 * (r + 1) + 1 and all(deg[u] == 6 for u in dist):
                r += 1
            else:
                break
        if r > best:
            best, arg = r, v
    return best, arg


def rim_paths(D, v, r, rng):
    S, K = D["S"], D["K"]
    adj = vgraph(S)
    dist = ball(adj, v, r)
    inside = {u for u, d in dist.items() if d < r}
    rim = {u for u, d in dist.items() if d == r}
    G = F.gamma(D)
    pts_of_vertex = {}
    for i, t in enumerate(K.points):
        for c in range(3):
            pts_of_vertex.setdefault(S.vert[t][c], set()).add(i)
    vertex_of_points = {frozenset(ps): vtx for vtx, ps in pts_of_vertex.items()}
    face_vertex = {fi: vertex_of_points.get(frozenset(P)) for fi, P in enumerate(D["fpts"])}
    blocked = set()
    for node in G:
        if node[0] == "l" and any(S.vert[K.lines[node[1]]][c] in inside for c in range(3)):
            blocked.add(node)
        if node[0] == "f" and face_vertex.get(node[1]) in inside:
            blocked.add(node)
    allowed = set(G) - blocked
    # rim faces in cyclic order around the ball: walk the rim
    rim_list = [u for u in sorted(rim)]
    order, seen = [], set()
    cur = rim_list[0]
    while cur not in seen:
        seen.add(cur)
        order.append(cur)
        nxt = [y for y in adj[cur] if y in rim and y not in seen]
        if not nxt:
            break
        cur = nxt[0]
    vface = {vtx: fi for fi, vtx in face_vertex.items() if vtx is not None}
    ring = [("f", vface[u]) for u in order if u in vface and ("f", vface[u]) in allowed]
    L = len(ring)
    if L < 6:
        return None
    picks = []
    for j in range(3):
        b = (j * L) // 3
        picks += [ring[b % L], ring[(b + 1) % L]]
    paths = F.disjoint_paths(G, picks, [("f", fi) for fi in F.corner_faces(D)], -1, rng, allowed=allowed)
    return paths is not None
