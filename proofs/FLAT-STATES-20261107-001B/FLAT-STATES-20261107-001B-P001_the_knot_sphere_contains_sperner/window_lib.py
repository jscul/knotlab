"""When pebbled colours admit a Sperner state with the full triangle at a given place, for FLAT-STATES-20261107-001B.

A Sperner state with exactly one fully labelled triangle T (positively oriented) is the same thing as an integer height h on the plane
cut along a ray from T, with |h(v) - h(u) + tau(u, v)| <= 1 on every edge, where tau = +-3 on edges crossing the ray and 0 elsewhere,
read mod 3 as colours. Pebbled colours fix h mod 3 at the pebbles. Writing h(p) = c_p + 3 s_p, the state exists iff the integer
difference system s_q - s_p <= floor((d(p, q) - c_q + c_p) / 3) on the pebbles has no negative cycle, where d is the shortest-path
distance for the edge weights 1 - tau (the most h can rise along a path). This module computes that criterion and, for comparison,
decides the same question with a solver.
"""
import itertools
import math

from pysat.formula import IDPool
from pysat.solvers import Solver


def grid(m):
    V = [(a, b) for a in range(m + 1) for b in range(m + 1 - a)]
    up = [((a, b), (a + 1, b), (a, b + 1)) for a in range(m) for b in range(m - a)]
    dn = [((a + 1, b), (a + 1, b + 1), (a, b + 1)) for a in range(m) for b in range(m - a - 1)]
    E = set()
    for t in up + dn:
        for u, v in itertools.combinations(t, 2):
            E.add(tuple(sorted((u, v))))
    return V, up + dn, sorted(E)   # triangles listed counterclockwise


def boundary_colours(m):
    """corners 0, 1, 2; each side takes the colour of its far corner except at its start: winding +1 counterclockwise"""
    col = {}
    for a in range(m + 1):
        col[(a, 0)] = 0 if a == 0 else 1
    for b in range(1, m + 1):
        col[(m - b, b)] = 2
    for b in range(1, m):
        col[(0, m - b)] = 0
    return col


def pos(v):
    return (v[0] + v[1] / 2.0, v[1] * math.sqrt(3) / 2.0)


def tau(T, u, v):
    """+3, -3 or 0: the signed crossing of edge u -> v with the ray straight down from just right of T's centre"""
    ox = sum(pos(w)[0] for w in T) / 3.0 + 0.1
    oy = sum(pos(w)[1] for w in T) / 3.0
    (ux, uy), (vx, vy) = pos(u), pos(v)
    if (ux - ox) * (vx - ox) >= 0:
        return 0
    y = uy + (vy - uy) * (ox - ux) / (vx - ux)
    if y >= oy:
        return 0
    return 3 if ux < ox else -3


def feasible_by_window(m, T, peb):
    """the difference-system criterion; peb = {vertex: colour}, boundary included"""
    V, _, E = grid(m)
    w = {}
    for u, v in E:
        t = tau(T, u, v)
        w[(u, v)] = 1 - t      # the colour step u -> v is h(v) - h(u) + tau(u, v), in [-1, 1]
        w[(v, u)] = 1 + t
    # loop around T counterclockwise must carry +3 (a positively oriented full triangle)
    assert sum(tau(T, T[i], T[(i + 1) % 3]) for i in range(3)) == 3
    P = sorted(peb)
    INF = 10 ** 9
    dist = {}
    for p in P:
        d = {v: INF for v in V}
        d[p] = 0
        for _ in range(len(V)):
            ch = False
            for (u, v), wt in w.items():
                if d[u] + wt < d[v]:
                    d[v] = d[u] + wt
                    ch = True
            if not ch:
                break
        dist[p] = d
    # sheets: s_q - s_p <= b(p, q); feasible iff no negative cycle (Bellman-Ford from a virtual source)
    b = {(p, q): (dist[p][q] - peb[q] + peb[p]) // 3 for p in P for q in P if p != q}
    s = {p: 0 for p in P}
    for _ in range(len(P) + 1):
        ch = False
        for (p, q), bb in b.items():
            if s[p] + bb < s[q]:
                s[q] = s[p] + bb
                ch = True
        if not ch:
            return True
    return False


def feasible_by_solver(m, T, peb):
    V, tris, _ = grid(m)
    pool = IDPool()
    var = lambda v, c: pool.id((v, c))  # noqa: E731
    cl = []
    for v in V:
        cl.append([var(v, c) for c in range(3)])
        cl += [[-var(v, a), -var(v, c)] for a, c in itertools.combinations(range(3), 2)]
        if v in peb:
            cl.append([var(v, peb[v])])
    rots = [tuple((r + i) % 3 for i in range(3)) for r in range(3)]
    sel = [pool.id(("rot", r)) for r in range(3)]
    cl.append(sel)
    for r, s_ in zip(rots, sel):
        for w, c in zip(T, r):
            cl.append([-s_, var(w, c)])
    for t in tris:
        if set(t) == set(T):
            continue
        for perm in itertools.permutations(range(3)):
            cl.append([-var(w, c) for w, c in zip(t, perm)])
    with Solver(name="cadical153", bootstrap_with=cl) as S:
        return S.solve()


def random_state(m, rng):
    """a random Sperner colouring with exactly one fully labelled triangle (positive), and that triangle"""
    V, tris, _ = grid(m)
    T = rng.choice([t for t in tris if not any(v[0] == 0 or v[1] == 0 or v[0] + v[1] == m for v in t)])
    pool = IDPool()
    var = lambda v, c: pool.id((v, c))  # noqa: E731
    bc = boundary_colours(m)
    cl = []
    for v in V:
        cl.append([var(v, c) for c in range(3)])
        cl += [[-var(v, a), -var(v, c)] for a, c in itertools.combinations(range(3), 2)]
        if v in bc:
            cl.append([var(v, bc[v])])
    for t in tris:
        if set(t) == set(T):
            continue
        for perm in itertools.permutations(range(3)):
            cl.append([-var(w, c) for w, c in zip(t, perm)])
    with Solver(name="cadical153", bootstrap_with=cl) as S:
        S.set_phases([var(v, c) * rng.choice((1, -1)) for v in V for c in range(3)])
        assert S.solve()
        mod = set(S.get_model())
    return T, {v: next(c for c in range(3) if var(v, c) in mod) for v in V}
