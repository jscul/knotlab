"""Boards of rings, their route digraphs and their polygons (BOARD-READ-20261110-001B-E001).

A board is given by a lattice basis (Euclidean), vertex types with offsets, and domain edges (type a at p, type b at p + delta). Rings
sit at vertices, contacts at edges; ring v has deg(v) g cells with its contacts every g cells in counterclockwise order (angles from the
embedding). The route digraph moves each cell to the next cell on every ring it lies on (rule 60 reads leftward; a contact is read by
the next cell on each of its rings).

polygons(): the exact route polygon conv{disp(C)/len(C)} over the simple cycles C of the contact quotient (hops of g cells) and the
graph polygon over the simple cycles of the ring-graph quotient. bfs_*: breadth-first distances on an L x L torus."""
import math
from collections import deque
from fractions import Fraction

S3 = math.sqrt(3)
BOARDS = {
    "square": {"basis": ((1.0, 0.0), (0.0, 1.0)), "types": {"o": (0.0, 0.0)},
               "edges": [("o", "o", (1, 0)), ("o", "o", (0, 1))]},
    "triangular": {"basis": ((1.0, 0.0), (0.5, S3 / 2)), "types": {"o": (0.0, 0.0)},
                   "edges": [("o", "o", (1, 0)), ("o", "o", (0, 1)), ("o", "o", (-1, 1))]},
    "honeycomb": {"basis": ((1.0, 0.0), (0.5, S3 / 2)), "types": {"A": (0.0, 0.0), "B": (1 / 3, 1 / 3)},
                  "edges": [("A", "B", (0, 0)), ("A", "B", (-1, 0)), ("A", "B", (0, -1))]},
    "kagome": {"basis": ((1.0, 0.0), (0.5, S3 / 2)), "types": {"u": (0.5, 0.0), "v": (0.0, 0.5), "w": (0.5, 0.5)},
               # the line graph of the triangular lattice's edges? no: kagome = corner-sharing triangles; up triangles (u, v, w) at p
               # and down triangles joining u(p), v(p + x - y)... written out below
               "edges": None},
}


def kagome_edges():
    # kagome sites at the midpoints of triangular-lattice edges: u(p) = p + (1/2, 0), v(p) = p + (0, 1/2), w(p) = p + (1/2, 1/2)
    # (lattice coordinates). Up triangle at p: u(p), w(p), v(p). Down triangle: u(p), v(p + x - y)?? found by nearest neighbours below.
    return None


def euclid(board, lat):
    (a1, a2) = BOARDS[board]["basis"]
    return (lat[0] * a1[0] + lat[1] * a2[0], lat[0] * a1[1] + lat[1] * a2[1])


def domain_edges(board):
    B = BOARDS[board]
    if B["edges"] is not None:
        return B["edges"]
    # kagome: connect every pair of sites at lattice-coordinate distance 1/2 along the three triangular directions
    types = B["types"]
    out = []
    dirs = [(Fraction(1, 2), Fraction(0)), (Fraction(0), Fraction(1, 2)), (Fraction(-1, 2), Fraction(1, 2))]
    off = {t: (Fraction(o[0]).limit_denominator(6), Fraction(o[1]).limit_denominator(6)) for t, o in types.items()}
    for ta, oa in off.items():
        for d in dirs:
            q = (oa[0] + d[0], oa[1] + d[1])
            for tb, ob in off.items():
                dx, dy = q[0] - ob[0], q[1] - ob[1]
                if dx.denominator == 1 and dy.denominator == 1:
                    out.append((ta, tb, (int(dx), int(dy))))
    return out


def rotation(board):
    """for each vertex type: its incident domain-edge slots in counterclockwise order, each (edge id, other type, lattice shift of the
    other end, side 'a' or 'b')"""
    B = BOARDS[board]
    edges = domain_edges(board)
    inc = {t: [] for t in B["types"]}
    for k, (ta, tb, d) in enumerate(edges):
        inc[ta].append((k, tb, d, "a"))
        inc[tb].append((k, ta, (-d[0], -d[1]), "b"))
    rot = {}
    for t, lst in inc.items():
        o = B["types"][t]
        def ang(item):
            k, tb, d, side = item
            ob = B["types"][tb]
            x, y = euclid(board, (d[0] + ob[0] - o[0], d[1] + ob[1] - o[1]))
            return math.atan2(y, x) % (2 * math.pi)
        rot[t] = sorted(lst, key=ang)
    return edges, rot


def contact_anchor(edges, k, t, p, side):
    """the lattice position that names contact k seen from its end of type t at p: the position of its 'a' end"""
    ta, tb, d = edges[k]
    return p if side == "a" else (p[0] - d[0], p[1] - d[1])


def polygons(board, g):
    """(route points, graph points): disp/len for the simple cycles of the two quotients, as exact fractions"""
    edges, rot = rotation(board)
    # contact quotient: node = edge id; hop arcs along each ring from slot j to slot j + 1
    arcs = []
    for t, lst in rot.items():
        m = len(lst)
        for j in range(m):
            k1, _, _, s1 = lst[j]
            k2, _, _, s2 = lst[(j + 1) % m]
            a1 = contact_anchor(edges, k1, t, (0, 0), s1)
            a2 = contact_anchor(edges, k2, t, (0, 0), s2)
            arcs.append((k1, k2, (a2[0] - a1[0], a2[1] - a1[1])))
    route = cycle_points(len(edges), arcs, weight=g)
    # ring graph quotient: node = vertex type; each edge both ways
    tl = list(BOARDS[board]["types"])
    garcs = []
    for (ta, tb, d) in edges:
        garcs.append((tl.index(ta), tl.index(tb), d))
        garcs.append((tl.index(tb), tl.index(ta), (-d[0], -d[1])))
    graph = cycle_points(len(tl), garcs, weight=1, undirected=True)
    return route, graph


def cycle_points(nnodes, arcs, weight, undirected=False):
    """disp/(weight len) over the simple cycles of a small multi-digraph with displaced arcs (cycles through distinct nodes; for an
    undirected graph a cycle may not reuse an edge, so a 2-cycle needs two different edges)"""
    pts = set()
    out = {i: [] for i in range(nnodes)}
    for idx, (u, v, d) in enumerate(arcs):
        out[u].append((v, d, idx))
    def dfs(start, node, disp, length, seen, used):
        for v, d, idx in out[node]:
            if undirected and (idx ^ 1) in used:
                continue
            nd = (disp[0] + d[0], disp[1] + d[1])
            if v == start:
                if nd != (0, 0) or True:
                    pts.add((Fraction(nd[0], weight * (length + 1)), Fraction(nd[1], weight * (length + 1))))
            elif v not in seen and v > start:
                dfs(start, v, nd, length + 1, seen | {v}, used | {idx})
    for s in range(nnodes):
        dfs(s, s, (0, 0), 0, {s}, frozenset())
    return sorted(pts)


def gauge(points, v, board):
    """N(v) = min t with v in t conv(points), by linear programming over pairs of points (Caratheodory in the plane): v = a p + b q,
    a, b >= 0, N = a + b, minimised; v in lattice coordinates"""
    best = None
    P = list(points)
    vx, vy = Fraction(v[0]), Fraction(v[1])
    for i in range(len(P)):
        px, py = P[i]
        # one point
        if px * vy == py * vx and (px * vx + py * vy) > 0:
            a = vx / px if px != 0 else vy / py
            best = a if best is None else min(best, a)
        for j in range(i + 1, len(P)):
            qx, qy = P[j]
            det = px * qy - py * qx
            if det == 0:
                continue
            a = (vx * qy - vy * qx) / det
            b = (px * vy - py * vx) / det
            if a >= 0 and b >= 0:
                best = a + b if best is None else min(best, a + b)
    return best


# ---------- breadth-first distances on an L x L torus
def torus(board, g, L):
    edges, rot = rotation(board)
    types = list(BOARDS[board]["types"])
    ring_id = {}
    for t in types:
        for i in range(L):
            for j in range(L):
                ring_id[(t, i, j)] = len(ring_id)
    deg = {t: len(rot[t]) for t in types}
    # cells: ring r has deg g cells; contact cells shared: cell of contact (k, anchor) is the 'a' end's slot cell
    cell = {}
    ncell = 0
    def rc(t, i, j, pos):
        return (t, i % L, j % L, pos % (deg[t] * g))
    # assign contact cells first
    contact_cell = {}
    for t in types:
        for i in range(L):
            for j in range(L):
                for s, (k, tb, d, side) in enumerate(rot[t]):
                    anc = contact_anchor(edges, k, t, (i, j), side)
                    key = (k, anc[0] % L, anc[1] % L)
                    if key not in contact_cell:
                        contact_cell[key] = ncell
                        ncell += 1
                    cell[rc(t, i, j, s * g)] = contact_cell[key]
    for t in types:
        for i in range(L):
            for j in range(L):
                for pos in range(deg[t] * g):
                    if pos % g:
                        cell[rc(t, i, j, pos)] = ncell
                        ncell += 1
    succ = [set() for _ in range(ncell)]
    for (t, i, j, pos), c in cell.items():
        succ[c].add(cell[rc(t, i, j, pos + 1)])
    return {"cell": cell, "succ": [list(s) for s in succ], "ring_id": ring_id, "types": types, "deg": deg, "L": L, "g": g}


def bfs(succ, sources):
    dist = [-1] * len(succ)
    dq = deque()
    for s in sources:
        dist[s] = 0
        dq.append(s)
    while dq:
        a = dq.popleft()
        for b in succ[a]:
            if dist[b] < 0:
                dist[b] = dist[a] + 1
                dq.append(b)
    return dist


def ring_cells(tor, t, i, j):
    L, g = tor["L"], tor["g"]
    return [tor["cell"][(t, i % L, j % L, pos)] for pos in range(tor["deg"][t] * g) if pos % g]


def graph_bfs(board, L, src):
    edges, rot = rotation(board)
    types = list(BOARDS[board]["types"])
    nb = {}
    for t in types:
        for i in range(L):
            for j in range(L):
                lst = []
                for (k, tb, d, side) in rot[t]:
                    lst.append((tb, (i + d[0]) % L, (j + d[1]) % L))
                nb[(t, i, j)] = lst
    dist = {src: 0}
    dq = deque([src])
    while dq:
        a = dq.popleft()
        for b in nb[a]:
            if b not in dist:
                dist[b] = dist[a] + 1
                dq.append(b)
    return dist
