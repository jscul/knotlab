"""One-sided grid Sperner is PPADS-hard, for COUNT-TFNP-20261107-001A.

Grid (FLAT-STATES-20261107-001B's window_lib): vertices (a, b) with a, b >= 0 and a + b <= m; small triangles
((a,b),(a+1,b),(a,b+1)) and ((a+1,b),(a+1,b+1),(a,b+1)), listed counterclockwise. Boundary: corners 0, 1, 2 and each side takes its far
corner's colour after its first vertex, so the colours wind once counterclockwise and the door (the meeting of sides 1 and 2) is at the
corner (m, 0).

SINK instance: successor and predecessor pointers on nodes 0..N-1 (None for none). The edge u -> v is present when succ[u] == v,
pred[v] == u and v != 0; node 0's in-edges are dropped, so 0 is the standard source of the drawn graph G'.

Layout (scale S): node j's port is P_j = (X0, Y0 + 6Sj). The potential edge i -> j runs east from P_i along its row to the column
c(i, j) = X0 + 3S(Ni + j + 1), north or south to the row Y0 + 6Sj + 3S, west back to x = X0 and south to P_j. The standard source's tube
enters from the door: it runs west along the bottom row from (m - 1, 0), north along x = X0 to P_0, and continues as 0's out-edge.

Crossings: wherever a present vertical run crosses a present horizontal run, the incoming arm of each turns into the adjacent outgoing arm
of the other, through opposite quadrants of radius r. In- and out-degrees, hence sources and sinks, are unchanged.

Tubes: lane 1 (colour 1) is the drawn path; lane 2 (colour 2) is its right-hand offset, with the outer corner filled at left turns;
everything else inside is 0. A tube's end at a sink is a positively oriented full triangle (0, 1, 2 counterclockwise), its start at a
non-standard source a negatively oriented one."""
import itertools
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/FLAT-STATES-20261107-001B/FLAT-STATES-20261107-001B-P001_the_knot_sphere_contains_sperner"))
import window_lib as SW  # noqa: E402

E, N_, W_, S_ = (1, 0), (0, 1), (-1, 0), (0, -1)


def right(d):
    return (d[1], -d[0])


def left(d):
    return (-d[1], d[0])


def add(p, d, t=1):
    return (p[0] + t * d[0], p[1] + t * d[1])


def present_edges(succ, pred):
    return {(u, v) for u, v in enumerate(succ) if v is not None and v != 0 and pred[v] == u}


def layout(N, S=4, X0=4, Y0=12, r=4):
    port = {j: (X0, Y0 + 6 * S * j) for j in range(N)}
    col = {(i, j): X0 + 3 * S * (N * i + j + 1) for i in range(N) for j in range(N) if i != j}
    m = X0 + 3 * S * (N * N + 1) + Y0 + 6 * S * N + 3 * S + 8
    return dict(N=N, S=S, X0=X0, Y0=Y0, r=r, port=port, col=col, m=m)


def polyline(L, i, j):
    """the corner points of potential edge i -> j"""
    S, X0 = L["S"], L["X0"]
    yi, yj = L["port"][i][1], L["port"][j][1]
    c = L["col"][(i, j)]
    return [(X0, yi), (c, yi), (c, yj + 3 * S), (X0, yj + 3 * S), (X0, yj)]


def door_polyline(L):
    m, X0, Y0 = L["m"], L["X0"], L["Y0"]
    return [(m - 1, 0), (X0, 0), (X0, Y0)]


def steps(corners):
    """unit points along a rectilinear polyline, with their direction of travel"""
    pts = [corners[0]]
    for p, q in zip(corners, corners[1:]):
        d = ((q[0] > p[0]) - (q[0] < p[0]), (q[1] > p[1]) - (q[1] < p[1]))
        assert d[0] == 0 or d[1] == 0
        while pts[-1] != q:
            pts.append(add(pts[-1], d))
    return pts


def draw(L, succ, pred, uncross=True):
    """lane-1 points with in/out directions after uncrossing"""
    edges = present_edges(succ, pred)
    r = L["r"]
    seqs = [steps(door_polyline(L))] + [steps(polyline(L, i, j)) for (i, j) in sorted(edges)]
    # directed step sets
    out_d, in_d = {}, {}
    count = {}
    for seq in seqs:
        for p, q in zip(seq, seq[1:]):
            d = (q[0] - p[0], q[1] - p[1])
            out_d.setdefault(p, []).append(d)
            in_d.setdefault(q, []).append(d)
    # a crossing point has two out-steps (one horizontal, one vertical)
    crossings = [p for p, ds in out_d.items() if len(ds) == 2]
    for p, ds in in_d.items():
        if len(ds) > 2 or len(out_d.get(p, [])) > 2:
            raise ValueError("three runs meet")
    route = {}                  # point -> (d_in, d_out) for lane 1
    for p, ds in out_d.items():
        if len(ds) == 1:
            route[p] = [in_d.get(p, [None])[0] if len(in_d.get(p, [])) <= 1 else None, ds[0]]
    for p, ds in in_d.items():
        if p not in out_d:
            route[p] = [ds[0], None]
    if uncross:
        for X in crossings:
            dh = next(d for d in out_d[X] if d[1] == 0)
            dv = next(d for d in out_d[X] if d[0] == 0)
            # remove the straight runs within radius r of X
            for d in (dh, dv):
                for t in range(-r + 1, r):
                    route.pop(add(X, d, t), None)
            # turn: horizontal-in -> vertical-out through quadrant (-dh, +dv); vertical-in -> horizontal-out through (+dh, -dv)
            for din, dout in ((dh, dv), (dv, dh)):
                a = add(X, din, -r)              # where the incoming arm stops being straight
                pts = [add(a, dout, t) for t in range(0, r + 1)]
                corner = pts[-1]
                pts2 = [add(corner, din, t) for t in range(1, r + 1)]
                path = pts + pts2                # a -> corner -> X + r*dout
                assert path[-1] == add(X, dout, r)
                route[a] = [route[a][0] if a in route else din, dout]
                for p in path[1:r + 1]:
                    route[p] = [dout, dout]
                route[corner] = [dout, din]
                for p in pts2[:-1]:
                    route[p] = [din, din]
                end = path[-1]
                route[end] = [din, route[end][1] if end in route else dout]
    else:
        for X in crossings:
            route[X] = [None, None]
    return route, crossings


def colouring(L, succ, pred, uncross=True):
    m = L["m"]
    route, crossings = draw(L, succ, pred, uncross)
    lane1 = set(route)
    lane2 = set()
    for p, (din, dout) in route.items():
        for d in (din, dout):
            if d is not None:
                lane2.add(add(p, right(d)))
        if din is not None and dout is not None and dout == left(din):
            lane2.add(add(add(p, right(din)), right(dout)))
    lane2 -= lane1
    col = {}
    bcol = SW.boundary_colours(m)
    for v in SW.grid(m)[0]:
        if v in bcol:
            col[v] = bcol[v]
        elif v in lane1:
            col[v] = 1
        elif v in lane2:
            col[v] = 2
        else:
            col[v] = 0
    clash = [v for v in bcol if (v in lane1 and bcol[v] != 1) or (v in lane2 and bcol[v] != 2)]
    return col, route, clash, crossings


def full_triangles(col, m):
    """[(triangle, orientation)] with orientation +1 when the colours read 0, 1, 2 counterclockwise"""
    out = []
    for t in SW.grid(m)[1]:
        cs = tuple(col[v] for v in t)
        if len(set(cs)) == 3:
            i = cs.index(0)
            out.append((t, 1 if cs[(i + 1) % 3] == 1 else -1))
    return out


def leaves(N, succ, pred):
    """sinks and non-standard sources of the drawn graph G' (node 0's in-edges dropped; 0 is joined to the door)"""
    edges = present_edges(succ, pred)
    indeg = {j: 0 for j in range(N)}
    outdeg = {j: 0 for j in range(N)}
    for u, v in edges:
        outdeg[u] += 1
        indeg[v] += 1
    indeg[0] = 1                     # the door feeds node 0
    sinks = [j for j in range(N) if indeg[j] == 1 and outdeg[j] == 0]
    sources = [j for j in range(N) if indeg[j] == 0 and outdeg[j] == 1]
    return sinks, sources


def triangle_node(L, t):
    """the node whose port a full triangle sits at, or None"""
    best = None
    for j, P in L["port"].items():
        if min(max(abs(v[0] - P[0]), abs(v[1] - P[1])) for v in t) <= 2:
            best = j
    return best


def back_map(succ, pred, j):
    """a SINK solution from a full triangle at node j's port: j if it is a sink of G, else 0 (which is then not a source of G)"""
    is_sink_G = (pred[j] is not None and succ[pred[j]] == j) and not (succ[j] is not None and pred[succ[j]] == j)
    return j if (is_sink_G and j != 0) else 0


def is_sink_solution(succ, pred, v):
    """Beame et al.'s SINK: a sink v != 0, or 0 if 0 is not a source"""
    has_out = succ[v] is not None and pred[succ[v]] == v
    has_in = pred[v] is not None and succ[pred[v]] == v
    if v == 0:
        return has_in or not has_out
    return has_in and not has_out
