"""Checks for GROW-FACE-20261110-001A: accretion needs a named face.

Frozen in the pre-registration (commit 9df96cd7f):
P1. The spiral law (G2), run to 40 full turns, has after turn k exactly the (2k + 1) x (2k + 1) block of the square grid, with every
    grid edge between its places, and exactly one enabled action at every step checked.
P2. For r = 3, 4 and 6, the slit order of the square-closing law SQ_r (G3) leaves two places created at one grid position, and the
    place created at the slit's base, once every place within distance 4 of it has four neighbours, has a radius-3 ball that is not
    the square grid's.
P3. A control: for the same radii, SQ_r filled from the slit's base upward leaves no two places at one grid position.

Added after the review, not pre-registered:
P4. SQ_r with a fixed priority of the four offsets (one action per view, as the frozen setting reads it), for all 24 priorities and
    r = 2, 3, 4, 6: the order of G3 leaves two places at exactly the heights y with 2y + 2 > r (y >= 2, or y >= 1 when r = 2), and at
    v = (1, y0 - 1) the neighbours u (west) and w (north) share only v, at the end of the slit and after a further stretch of
    growth. The order-choosing version of P2 is checked the same way, with r = 2 added.
P5. The spiral without its arrow (G2'): values are coordinates mod 3 only, and a site is enabled when its radius-2 view is one the
    spiral's head has. Run to 40 rings: exactly one enabled site at every step, the head, whose action (read at radius 1) grows the
    spiral; no new kind of view appears after a few rings, and the kinds repeat with period 3 in the ring. At radius 1 the head's
    views clash with other places' views.

Usage: check.py
"""
import itertools
import json
import os
import time
from collections import deque

import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'result.json')

UNITS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def neg(d):
    return (-d[0], -d[1])


def left(d):
    return (-d[1], d[0])


def right(d):
    return (d[1], -d[0])


def mod3(p):
    return (p[0] % 3, p[1] % 3)


def offset(ca, cb):
    """The unit vector from coordinate ca to cb (mod 3), or None."""
    for u in UNITS:
        if mod3(add(ca, u)) == cb:
            return u
    return None


class Board:
    """Places with coordinates mod 3 as values (and, for the spiral, an arrow); every edge a unit offset."""

    def __init__(self):
        self.val, self.nb, self.pos = [], [], []

    def new(self, val, pos):
        self.val.append(val)
        self.nb.append({})
        self.pos.append(pos)
        return len(self.val) - 1

    def join(self, a, b):
        d = offset(self.val[a][0], self.val[b][0])
        assert d is not None and d not in self.nb[a] and neg(d) not in self.nb[b]
        self.nb[a][d] = b
        self.nb[b][neg(d)] = a

    def graph(self):
        return nx.Graph([(a, b) for a in range(len(self.nb)) for b in self.nb[a].values()])


# --- G2: the spiral law ---------------------------------------------------------------------------------------------------------

def spiral_cells(rings):
    """The square spiral's cells in order, by the ring formula: ring m starts at (m, 1 - m) and runs north, west, south and east."""
    cells = [(0, 0)]
    for m in range(1, rings + 1):
        x, y = m, 1 - m
        cells.append((x, y))
        for d, n in (((0, 1), 2 * m - 1), ((-1, 0), 2 * m), ((0, -1), 2 * m), ((1, 0), 2 * m)):
            for _ in range(n):
                x, y = x + d[0], y + d[1]
                cells.append((x, y))
    return cells


def spiral(turns):
    """Values (coordinate mod 3, arrow). A site is enabled exactly when it has no neighbour at the offset of its arrow. Its action adds
    a place there, joined to the site and to the site's left neighbour's neighbour at the arrow's offset when that exists (closing a
    square); the new place keeps the arrow if it got that inner neighbour, and turns left otherwise."""
    B = Board()
    B.new(((0, 0), (1, 0)), (0, 0))
    ok, one_enabled = True, True
    target = 1
    for k in range(1, turns + 1):
        target = (2 * k + 1) ** 2
        while len(B.val) < target:
            h = len(B.val) - 1
            c, a = B.val[h]
            assert a not in B.nb[h]
            q = None
            l = left(a)
            if l in B.nb[h] and a in B.nb[B.nb[h][l]]:
                q = B.nb[B.nb[h][l]][a]
            p = B.new((mod3(add(c, a)), a if q is not None else l), add(B.pos[h], a))
            B.join(h, p)
            if q is not None:
                B.join(p, q)
        en = [v for v in range(len(B.val)) if B.val[v][1] not in B.nb[v]]
        one_enabled = one_enabled and en == [len(B.val) - 1]
        block = {(x, y) for x in range(-k, k + 1) for y in range(-k, k + 1)}
        pos = set(B.pos)
        edges = {frozenset((B.pos[a], B.pos[b])) for a in range(len(B.nb)) for b in B.nb[a].values()}
        grid_edges = {frozenset((p, add(p, u))) for p in block for u in UNITS if add(p, u) in block}
        ok = ok and pos == block and len(pos) == len(B.pos) and edges == grid_edges
    same_order = B.pos == spiral_cells(turns)
    return {'turns': turns, 'places': len(B.val), 'blocks_exact': ok, 'one_enabled_action': one_enabled,
            'order_is_the_ring_formula': same_order}


# --- G2': the spiral without its arrow -------------------------------------------------------------------------------------------

def ball(c, board, R):
    """A place's radius-R view on a board of grid cells with every grid edge: its value (coordinate mod 3) and the shape of its ball."""
    seen = {c: 0}
    dq = deque([c])
    while dq:
        x = dq.popleft()
        if seen[x] == R:
            continue
        for d in UNITS:
            y = add(x, d)
            if y in board and y not in seen:
                seen[y] = seen[x] + 1
                dq.append(y)
    return (mod3(c), frozenset((y[0] - c[0], y[1] - c[1]) for y in seen))


def head_arrow(nbrs):
    """The arrow read from the head's radius-1 view: no neighbour gives e1; one neighbour at f gives right(f); two neighbours at f and
    right(f) give -f."""
    if not nbrs:
        return (1, 0)
    if len(nbrs) == 1:
        (f,) = nbrs
        return right(f)
    f, g = sorted(nbrs)
    if g == right(f):
        return neg(f)
    assert f == right(g)
    return neg(g)


def near(c, R):
    return [(c[0] + dx, c[1] + dy) for dx in range(-R, R + 1) for dy in range(abs(dx) - R, R - abs(dx) + 1)]


def arrow_free(rings, R):
    cells = spiral_cells(rings)
    ringof = lambda c: max(abs(c[0]), abs(c[1]))
    # 1. The views along the spiral: the head's (with its arrow, the step to the next cell) and every other place's, at every step.
    #    A place's view changes only when a cell within grid distance R is placed, so these are all the views that occur.
    board, head, other, first, by_ring = set(), {}, set(), {}, {}
    radius1_reads_arrow = True
    for n, c in enumerate(cells[:-1]):
        board.add(c)
        a = (cells[n + 1][0] - c[0], cells[n + 1][1] - c[1])
        k = ringof(c)
        seen = by_ring.setdefault(k, set())
        for y in near(c, R):
            if y in board:
                t = ball(y, board, R)
                kind = ('head', t) if y == c else ('other', t)
                if y == c:
                    head.setdefault(t, set()).add(a)
                    radius1_reads_arrow = radius1_reads_arrow and head_arrow({d for d in UNITS if add(c, d) in board}) == a
                else:
                    other.add(t)
                seen.add(kind)
                first.setdefault(kind, k)
    clashes = len(set(head) & other)
    consistent = all(len(v) == 1 for v in head.values())
    out = {'rings': rings, 'radius': R, 'head_views': len(head), 'other_views': len(other), 'clashes': clashes,
           'one_arrow_per_head_view': consistent, 'radius_1_reads_the_arrow': radius1_reads_arrow,
           'last_ring_with_a_new_view': max(first.values())}
    top = rings - 1
    period = [k for k in range(4, top + 1) if by_ring[k] == by_ring[k - 3]]
    start = next((k for k in range(4, top + 1) if all(j in period for j in range(k, top + 1))), None)
    out['views_repeat_every_3_rings_from'] = start
    if clashes or not consistent:
        return out
    # 2. Run the law itself: values are coordinates mod 3 only; a site is enabled when its view is one of the head's views, and its
    #    action adds a place at the arrow read from the view, joined to the site and to the place q at the arrow's offset from the
    #    site's left neighbour, when that is in the view.
    table = {t: next(iter(v)) for t, v in head.items()}
    board = {(0, 0)}
    views = {(0, 0): ball((0, 0), board, R)}
    enabled = {c for c, t in views.items() if t in table}
    last, ok = (0, 0), True
    for n in range(1, len(cells)):
        ok = ok and enabled == {last}
        if not ok:
            break
        a = table[views[last]]
        new = add(last, a)
        inner = add(last, left(a))
        q = add(new, left(a))
        joins = {last} | ({q} if q in board and inner in board else set())
        ok = ok and new == cells[n] and new not in board and {add(new, d) for d in UNITS if add(new, d) in board} == joins
        board.add(new)
        last = new
        for y in near(new, R):
            if y in board:
                views[y] = ball(y, board, R)
                if views[y] in table:
                    enabled.add(y)
                else:
                    enabled.discard(y)
    out['run_one_enabled_site_and_the_spiral'] = ok
    out['run_places'] = len(board)
    # the law's table: each head view as (value mod 3, the offsets of its ball) with the arrow its radius-1 view gives
    out['head_view_list'] = sorted([list(t[0]), sorted(list(d) for d in t[1]), list(a)] for t, a in table.items())
    return out


# --- G3: the square-closing law SQ_r ---------------------------------------------------------------------------------------------

def view(B, s, r):
    """The radius-r view of s, read without names: breadth first, each place's neighbours taken in the fixed order of UNITS, with the
    grid displacement along the breadth-first tree. Places come in the order (distance, offsets along the least shortest path)."""
    disp = {s: (0, 0)}
    order = [s]
    dq = deque([(s, 0)])
    while dq:
        v, dist = dq.popleft()
        if dist == r:
            continue
        for u in UNITS:
            w = B.nb[v].get(u)
            if w is not None and w not in disp:
                disp[w] = add(disp[v], u)
                order.append(w)
                dq.append((w, dist + 1))
    return order, disp


def act(B, s, d, r):
    """SQ_r's action at site s for its missing offset d: join a visible place at displacement d that lacks the opposite neighbour;
    otherwise add a new place there, joined to s and to the first visible place at each grid position next to it."""
    assert d not in B.nb[s]
    order, disp = view(B, s, r)
    md = neg(d)
    for t in order:
        if t != s and disp[t] == d and md not in B.nb[t]:
            B.join(s, t)
            return t
    p = B.new((mod3(add(B.val[s][0], d)),), add(B.pos[s], d))
    B.join(s, p)
    for e in UNITS:
        if e == md:
            continue
        want = add(d, e)
        me = neg(e)
        for t in order:
            if t != s and disp[t] == want and me not in B.nb[t] and e not in B.nb[p]:
                B.join(p, t)
                break
    return p


def predicted_heights(r, H):
    return [y for y in range(1, H + 1) if (y >= 2 and 2 * y + 2 > r) or (y == 1 and r <= 2)]


def doubled(B, X, frame=None):
    """Heights of the slit column holding two places."""
    created = {}
    for v, p in enumerate(B.pos):
        created.setdefault(p, []).append(v)
    out = []
    for p, vs in created.items():
        q = frame(p) if frame else p
        if q[0] == X and len(vs) > 1:
            out.append(q[1])
    return sorted(out)


def shares_only(B, u, w, v):
    return set(B.nb[u].values()) & set(B.nb[w].values()) == {v}


def pairs_sharing_two(B, v):
    """How many pairs of v's neighbours share a second common neighbour."""
    ns = list(B.nb[v].values())
    return sum(1 for a, b in itertools.combinations(ns, 2) if len(set(B.nb[a].values()) & set(B.nb[b].values())) >= 2)


def slit(r, H, top_down):
    """The order-choosing SQ_r (a site may act at any missing offset): the order of the first draft."""
    B = Board()
    o = B.new(((0, 0),), (0, 0))
    w = act(B, o, (-1, 0), r)
    e = act(B, o, (1, 0), r)
    L, R = [w], [e]
    for y in range(1, H + 1):
        L.append(act(B, L[-1], (0, 1), r))
        R.append(act(B, R[-1], (0, 1), r))
    rows = range(H, 0, -1) if top_down else range(1, H + 1)
    base, mid = None, {0: o}
    for y in rows:
        if (1, 0) not in B.nb[L[y]]:
            p = act(B, L[y], (1, 0), r)
            mid[y] = p
            if y == 1:
                base = p
        if (-1, 0) not in B.nb[R[y]]:
            act(B, R[y], (-1, 0), r)
    dup = doubled(B, 0)
    out = {'r': r, 'H': H, 'order': 'top-down' if top_down else 'bottom-up', 'positions_with_two_places': len(dup)}
    if not top_down:
        return out
    pred = predicted_heights(r, H)
    out['heights_as_predicted'] = dup == pred
    y0 = pred[0]
    u, v, wv = mid[y0 - 1], R[y0 - 1], R[y0]
    inv0 = B.nb[u].get((1, 0)) == v and B.nb[wv].get((0, -1)) == v and shares_only(B, u, wv, v) and \
        B.nb[u].get((0, 1)) is not None and B.nb[wv].get((-1, 0)) is not None and B.nb[u][(0, 1)] != B.nb[wv][(-1, 0)]
    if base is None:
        base = mid[1] if 1 in mid else o
    # complete the neighbourhood of the base, in order of creation, until every place within distance 4 has four neighbours
    for _ in range(200):
        G = B.graph()
        near_ = [v_ for v_, dist in nx.single_source_shortest_path_length(G, base, cutoff=6).items()]
        todo = [(v_, d) for v_ in sorted(near_) for d in UNITS if d not in B.nb[v_]]
        if not todo:
            break
        ball4 = nx.single_source_shortest_path_length(G, base, cutoff=4)
        if all(len(B.nb[v_]) == 4 for v_ in ball4):
            break
        for v_, d in todo:
            if d not in B.nb[v_]:
                act(B, v_, d, r)
    G = B.graph()
    ball4 = nx.single_source_shortest_path_length(G, base, cutoff=4)
    saturated = all(len(B.nb[v_]) == 4 for v_ in ball4)
    bl = G.subgraph(nx.single_source_shortest_path_length(G, base, cutoff=3).keys()).copy()
    grid = nx.grid_2d_graph(7, 7)
    gball = grid.subgraph(nx.single_source_shortest_path_length(grid, (3, 3), cutoff=3).keys()).copy()
    nx.set_node_attributes(bl, {v_: v_ == base for v_ in bl}, 'root')
    nx.set_node_attributes(gball, {v_: v_ == (3, 3) for v_ in gball}, 'root')
    iso = nx.is_isomorphic(bl, gball, node_match=lambda a, b: a['root'] == b['root'])
    inv1 = shares_only(B, u, wv, v) and pairs_sharing_two(B, v) <= 3
    out.update({'base_neighbourhood_saturated': saturated, 'base_ball_is_the_grids': iso, 'places': len(B.val),
                'y0': y0, 'u_w_share_only_v_at_end_of_slit': inv0, 'u_w_share_only_v_after_growth': inv1})
    return out


def first_missing(B, s, P):
    for d in P:
        if d not in B.nb[s]:
            return d
    return None


def fire(B, s, P, r):
    """One step of SQ_r with priority P at site s: its action at the first offset of P where it has no neighbour."""
    return act(B, s, first_missing(B, s, P), r)


def fire_until(B, s, P, r, d):
    while d not in B.nb[s]:
        fire(B, s, P, r)
    return B.nb[s][d]


def slit_priority(r, H, P):
    """SQ_r with priority P, one action per view. In the frame where P's first offset points up: the seed at (-1, 0) grows up, east
    (the slit's base m) and down; the row below is grown east and turned up to give (1, 0), joined to m; two arms rise from (-1, 0)
    and (1, 0); the slit is filled from the top, each side acting until it has its slit-side neighbour. Every step is the law's."""
    up = P[0]
    east = right(up)
    west, down = neg(east), neg(up)

    def at(X, Y):
        return (X * east[0] + Y * up[0], X * east[1] + Y * up[1])

    def frame(p):
        # inverse of at: X = p . east, Y = p . up
        return (p[0] * east[0] + p[1] * east[1], p[0] * up[0] + p[1] * up[1])

    B = Board()
    s0 = B.new((mod3(at(-1, 0)),), at(-1, 0))
    fire_until(B, s0, P, r, up)
    m = fire_until(B, s0, P, r, east)
    b = fire_until(B, s0, P, r, down)
    c = fire_until(B, b, P, r, east)
    d1 = fire_until(B, c, P, r, east)
    e = fire_until(B, d1, P, r, up)
    base_ok = B.nb[c].get(up) == m and B.nb[e].get(west) == m and up not in B.nb[m]
    L, R = [s0], [e]
    for _ in range(H + 1):
        L.append(fire_until(B, L[-1], P, r, up))
        R.append(fire_until(B, R[-1], P, r, up))
    mid = {0: m}
    for y in range(H, 0, -1):
        mid[y] = fire_until(B, L[y], P, r, east)
        fire_until(B, R[y], P, r, west)
    dup = doubled(B, 0, frame)
    pred = predicted_heights(r, H)
    y0 = pred[0]
    u, v, w = mid[y0 - 1], R[y0 - 1], R[y0]
    inv0 = B.nb[u].get(east) == v and B.nb[w].get(down) == v and shares_only(B, u, w, v) and \
        B.nb[u].get(up) is not None and B.nb[w].get(west) is not None and B.nb[u][up] != B.nb[w][west]
    # a further stretch of growth: four rounds in which every place within distance 5 of u acts until it has four neighbours
    for _ in range(4):
        G = B.graph()
        for s in sorted(nx.single_source_shortest_path_length(G, u, cutoff=5)):
            while first_missing(B, s, P) is not None:
                fire(B, s, P, r)
    inv1 = shares_only(B, u, w, v) and pairs_sharing_two(B, v) <= 3 and len(B.nb[v]) == 4
    return {'P': [list(d) for d in P], 'r': r, 'H': H, 'base_built': base_ok, 'heights_as_predicted': dup == pred,
            'positions_with_two_places': len(dup), 'y0': y0, 'u_w_share_only_v_at_end_of_slit': inv0,
            'u_w_share_only_v_after_growth': inv1, 'places': len(B.val)}


def main():
    t0 = time.time()
    res = {'P1_spiral': spiral(40)}
    res['P1_spiral']['pass'] = res['P1_spiral']['blocks_exact'] and res['P1_spiral']['one_enabled_action'] and \
        res['P1_spiral']['order_is_the_ring_formula']
    p2, p3 = [], []
    for r in (3, 4, 6):
        H = 2 * r + 6
        p2.append(slit(r, H, True))
        p3.append(slit(r, H, False))
    res['P2_slit'] = {'runs': p2, 'pass': all(x['positions_with_two_places'] > 0 and x['base_neighbourhood_saturated']
                                              and not x['base_ball_is_the_grids'] for x in p2)}
    res['P3_control'] = {'runs': p3, 'pass': all(x['positions_with_two_places'] == 0 for x in p3)}
    p4 = [slit_priority(r, 2 * r + 6, P) for r in (2, 3, 4, 6) for P in itertools.permutations(UNITS)]
    choose = [slit(r, 2 * r + 6, True) for r in (2, 3, 4, 6)]
    res['P4_priorities'] = {'runs': p4, 'order_choosing_runs': choose,
                            'pass': all(x['base_built'] and x['heights_as_predicted'] and x['u_w_share_only_v_at_end_of_slit']
                                        and x['u_w_share_only_v_after_growth'] for x in p4)
                            and all(x['heights_as_predicted'] and x['u_w_share_only_v_at_end_of_slit']
                                    and x['u_w_share_only_v_after_growth'] for x in choose)}
    a2 = arrow_free(40, 2)
    a1 = arrow_free(40, 1)
    res['P5_arrow_free'] = {'radius_2': a2, 'radius_1': a1,
                            'pass': a2['clashes'] == 0 and a2['one_arrow_per_head_view'] and a2['radius_1_reads_the_arrow']
                            and a2.get('run_one_enabled_site_and_the_spiral', False) and a1['clashes'] > 0
                            and a2['views_repeat_every_3_rings_from'] is not None
                            and a2['views_repeat_every_3_rings_from'] <= 15}
    res['pass'] = all(v['pass'] for v in res.values() if isinstance(v, dict))
    res['status'] = 'passed' if res['pass'] else 'failed'
    res['seconds'] = round(time.time() - t0, 1)
    json.dump(res, open(OUT, 'w'), indent=1, sort_keys=True, default=list)
    summary = {k: (v['pass'] if isinstance(v, dict) else v) for k, v in res.items()}
    print(json.dumps(summary))
    print(json.dumps({'P2': [(x['r'], x['positions_with_two_places'], x['y0'], x['u_w_share_only_v_after_growth']) for x in p2],
                      'P4_fails': [x for x in p4 if not (x['base_built'] and x['heights_as_predicted'] and
                                                         x['u_w_share_only_v_at_end_of_slit'] and
                                                         x['u_w_share_only_v_after_growth'])][:3],
                      'choose': [(x['r'], x['positions_with_two_places'], x['heights_as_predicted'],
                                  x['u_w_share_only_v_after_growth']) for x in choose],
                      'P5': {'r2': {k: v for k, v in a2.items()}, 'r1': {k: v for k, v in a1.items()}}}, default=list)[:4000])


if __name__ == '__main__':
    main()
