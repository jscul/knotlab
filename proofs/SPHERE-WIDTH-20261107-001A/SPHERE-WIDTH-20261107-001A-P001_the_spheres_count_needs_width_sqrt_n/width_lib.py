"""Label states under pebbles on the octahedral knot sphere, for SPHERE-WIDTH-20261107-001A.

Trivialization. For a vortex z, cut the sphere along a cut star from z to the six corners and develop frames over the rest
(FLAT-STATES-20261107-001A). For each line l and points a, b of l (neither z), t(a, b) in {-1, 0, 1} is the label shift between b's
developed frame and b's frame seen from a through l: it is 0 off the cut and the corner holonomy (+-1) across it. A label state with
vortex z is an integer L on the points other than z with |L(b) + t(a, b) - L(a)| <= 1 for every such (l, a, b), lines through z
included for their two other points; its colours are
S_{L mod 6}[sigma] xor g. Around z the shifts add up to 6, so z's neighbours read 0..5 and z is a vortex.

Pebbles. A pebbled colour at p allows the labels a_p, a_p + 1, a_p + 2 (mod 6). Writing L(p) in [a_p + 6 s_p, a_p + 6 s_p + 2], a state
exists iff the integer system s_q - s_p <= floor((d(p, q) + a_p + 2 - a_q) / 6) has no negative cycle, where d is the shortest-path
distance for the weights 1 - t(a, b) on a -> b (the most L can rise). This is the window criterion of FLAT-STATES-20261107-001B with
windows of three labels instead of one colour.
"""
import heapq
import itertools
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "proofs/FLAT-STATES-20261107-001A/FLAT-STATES-20261107-001A-P001_flat_states_exist_on_the_whole_sphere"))
import flat_lib as F  # noqa: E402

from pysat.formula import IDPool  # noqa: E402
from pysat.solvers import Solver  # noqa: E402


def sphere(k):
    K = F.index_lines(F.build(k))
    K["G"] = F.gamma(K)
    K["adj"] = F.point_graph(K)
    K["corner_pts"] = {p for fi in F.corner_faces(K) for p in K["fpts"][fi]}
    return K


def trivialize(K, z, rng=None):
    """frames and edge shifts for a vortex at z: {(a, b): [shifts]} over ordered pairs inside lines, z excluded"""
    star = F.cut_star(K, K["G"], z, rng)
    base = next(p for p in range(K["n"]) if p != z)
    fr = F.develop(K, z, star, base)
    shift = {}
    for l, L in enumerate(K["lines"]):
        # a line through z still binds its other two points: z's six neighbours must read 0..5 in order
        for a, b in itertools.permutations([p for p in L if p != z], 2):
            o, e = F.step(K, l, a, b)
            d = (fr[a][0] + o - fr[b][0]) % 3
            t = (2 * d + 3 * (fr[a][1] ^ e ^ fr[b][1])) % 6
            assert t in (0, 1, 5), ("shift out of range", l, a, b, t)
            shift.setdefault((a, b), []).append({0: 0, 1: 1, 5: -1}[t])
    return dict(z=z, star=star, fr=fr, shift=shift)


def arc_start(fr_p, colour):
    s, g = fr_p
    ok = [lab for lab in range(6) if F.PATTERNS[lab][s] ^ g == colour]
    a = next(x for x in ok if (x + 1) % 6 in ok and (x + 2) % 6 in ok)
    return a


def weights(T):
    """max rise of L along each directed edge (the tightest over parallel lines)"""
    w = {}
    for (a, b), ts in T["shift"].items():
        for t in ts:
            w[(a, b)] = min(w.get((a, b), 9), 1 - t)
            w[(b, a)] = min(w.get((b, a), 9), 1 + t)
    out = {}
    for (a, b), c in w.items():
        out.setdefault(a, []).append((b, c))
    return out


def dists(W, src, n):
    d = [None] * n
    d[src] = 0
    h = [(0, src)]
    while h:
        du, u = heapq.heappop(h)
        if du > d[u]:
            continue
        for v, c in W.get(u, ()):
            if d[v] is None or du + c < d[v]:
                d[v] = du + c
                heapq.heappush(h, (d[v], v))
    return d


def feasible(K, T, peb):
    """peb = {point: colour}; returns (feasible, sheets, arc starts, distances from pebbles)"""
    W = weights(T)
    P = sorted(peb)
    a = {p: arc_start(T["fr"][p], c) for p, c in peb.items()}
    D = {p: dists(W, p, K["n"]) for p in P}
    b = {(p, q): (D[p][q] + a[p] + 2 - a[q]) // 6 for p in P for q in P if p != q}
    s = {p: 0 for p in P}
    for _ in range(len(P) + 1):
        changed = False
        for (p, q), bb in b.items():
            if s[p] + bb < s[q]:
                s[q] = s[p] + bb
                changed = True
        if not changed:
            return True, s, a, D
    return False, None, a, D


def realize(K, T, peb, s, a, D):
    """the largest label function under the pebbles' upper bounds (McShane), read as colours"""
    n, z = K["n"], T["z"]
    if peb:
        L = [min(a[p] + 6 * s[p] + 2 + D[p][v] for p in peb) if v != z else None for v in range(n)]
    else:
        root = next(v for v in range(n) if v != z)
        d0 = dists(weights(T), root, n)
        L = [d0[v] if v != z else None for v in range(n)]
    x = [None] * n
    for v in range(n):
        if v == z:
            x[v] = 0
        else:
            sg, g = T["fr"][v]
            x[v] = F.PATTERNS[L[v] % 6][sg] ^ g
    return x, L


def solver_feasible(K, T, peb):
    """the same question by a solver over Z6 labels (cyclic Lipschitz with the shifts, pebble arcs)"""
    pool = IDPool()
    var = lambda v, c: pool.id((v, c))  # noqa: E731
    z = T["z"]
    cl = []
    for v in range(K["n"]):
        if v == z:
            continue
        cl.append([var(v, c) for c in range(6)])
        cl += [[-var(v, c), -var(v, d)] for c, d in itertools.combinations(range(6), 2)]
    for (p, col) in peb.items():
        ap = arc_start(T["fr"][p], col)
        cl.append([var(p, (ap + i) % 6) for i in range(3)])
    for (u, v), ts in T["shift"].items():
        for t in ts:
            for lu in range(6):
                for lv in range(6):
                    if min((lv + t - lu) % 6, (lu - lv - t) % 6) > 1:
                        cl.append([-var(u, lu), -var(v, lv)])
    with Solver(name="cadical153", bootstrap_with=cl) as S:
        return S.solve()


def random_label_state(K, z, rng):
    """a random label state with vortex z (solver with random phases), as colours"""
    T = trivialize(K, z, rng)
    pool = IDPool()
    var = lambda v, c: pool.id((v, c))  # noqa: E731
    cl = []
    for v in range(K["n"]):
        if v == z:
            continue
        cl.append([var(v, c) for c in range(6)])
        cl += [[-var(v, c), -var(v, d)] for c, d in itertools.combinations(range(6), 2)]
    for (u, v), ts in T["shift"].items():
        for t in ts:
            for lu in range(6):
                for lv in range(6):
                    if min((lv + t - lu) % 6, (lu - lv - t) % 6) > 1:
                        cl.append([-var(u, lu), -var(v, lv)])
    with Solver(name="cadical153", bootstrap_with=cl) as S:
        S.set_phases([var(v, c) * rng.choice((1, -1)) for v in range(K["n"]) if v != z for c in range(6)])
        assert S.solve()
        mod = set(S.get_model())
    x = [0] * K["n"]
    for v in range(K["n"]):
        if v != z:
            lab = next(c for c in range(6) if var(v, c) in mod)
            sg, g = T["fr"][v]
            x[v] = F.PATTERNS[lab][sg] ^ g
    return x


def dists_pred(W, src, n):
    d, pred = [None] * n, [None] * n
    d[src] = 0
    h = [(0, src)]
    while h:
        du, u = heapq.heappop(h)
        if du > d[u]:
            continue
        for v, c in W.get(u, ()):
            if d[v] is None or du + c < d[v]:
                d[v], pred[v] = du + c, u
                heapq.heappush(h, (d[v], v))
    return d, pred


def obstruction(K, T, peb):
    """None if a state exists; else a negative cycle of the sheet system as (pebbles in order, the closed walk through shortest paths)"""
    W = weights(T)
    P = sorted(peb)
    a = {p: arc_start(T["fr"][p], c) for p, c in peb.items()}
    DP = {p: dists_pred(W, p, K["n"]) for p in P}
    b = {(p, q): (DP[p][0][q] + a[p] + 2 - a[q]) // 6 for p in P for q in P if p != q}
    s = {p: 0 for p in P}
    par = {p: None for p in P}
    last = None
    for _ in range(len(P) + 1):
        last = None
        for (p, q), bb in b.items():
            if s[p] + bb < s[q]:
                s[q], par[q], last = s[p] + bb, p, q
        if last is None:
            return None
    for _ in range(len(P)):
        last = par[last]
    cyc, v = [last], par[last]
    while v != last:
        cyc.append(v)
        v = par[v]
    cyc.reverse()                     # p_1 -> p_2 -> ... (each the parent of the next)
    walk = [cyc[0]]
    for p, q in zip(cyc, cyc[1:] + cyc[:1]):
        seg, v = [], q
        while v != p:
            seg.append(v)
            v = DP[p][1][v]
        walk += seg[::-1]
    bsum = sum(b[(p, q)] for p, q in zip(cyc, cyc[1:] + cyc[:1]))
    return cyc, walk, bsum, a


def holonomy(T, walk):
    """the sum of label shifts along a closed walk of points (the tightest shift where parallel lines differ)"""
    h = 0
    for u, v in zip(walk, walk[1:]):
        ts = T["shift"][(u, v)]
        h += max(ts)                 # the weight used was 1 - max(ts)
    return h


def bfs(adj, srcs, n):
    d = [None] * n
    dq = list(srcs)
    for s in srcs:
        d[s] = 0
    i = 0
    while i < len(dq):
        u = dq[i]
        i += 1
        for v in adj[u]:
            if d[v] is None:
                d[v] = d[u] + 1
                dq.append(v)
    return d


def density(K, P, x):
    """max over radii s of (pebbles within distance s of x) / (s + 1): the density the proof's bad set thresholds"""
    if not P:
        return 0.0
    d = bfs(K["adj"], [x], K["n"])
    ds = sorted(d[p] for p in P)
    return max((j + 1) / (dj + 1) for j, dj in enumerate(ds))


class Duplicator:
    """answers from label states whose vortex is kept where the pebble density is lowest (the proof's strategy, greedy form)"""

    def __init__(self, K, beta, z0):
        self.K, self.beta = K, beta
        self.peb = {}
        self.z = z0
        self.T = trivialize(K, z0)
        self.moves = 0

    def place(self, q):
        K = self.K
        P = list(self.peb) + [q]
        if q != self.z and density(K, P, self.z) < 1.0 / self.beta:
            order = [self.z]
        else:
            free = [x for x in range(K["n"]) if x not in K["corner_pts"] and x not in self.peb and x != q]
            order = sorted(free, key=lambda x: (density(K, P, x), x))[:60]
        for x in order:
            T = self.T if x == self.z else trivialize(K, x)
            f, s, a, D = feasible(K, T, self.peb)
            if f:
                y, _ = realize(K, T, self.peb, s, a, D)
                if x != self.z:
                    self.moves += 1
                self.z, self.T = x, T
                self.peb[q] = y[q]
                return True
        return False

    def remove(self, q):
        self.peb.pop(q, None)


def spoiler_chaser(K, dup, M, steps):
    """pebble the free point nearest the vortex; at capacity drop the pebble farthest from it"""
    for _ in range(steps):
        dz = bfs(K["adj"], [dup.z], K["n"])
        if len(dup.peb) >= M:
            dup.remove(max(dup.peb, key=lambda p: (dz[p], p)))
        q = min((x for x in range(K["n"]) if x not in dup.peb), key=lambda x: (dz[x], x))
        if not dup.place(q):
            return False
    return True


def spoiler_ring(K, dup, M, steps, rng):
    """build a ring of adjacent pebbles (a distance sphere) around the vortex, then fill inward; restart when the vortex leaves"""
    for _ in range(steps):
        z0 = dup.z
        d0 = bfs(K["adj"], [z0], K["n"])
        r = max(1, min(rng.randint(1, max(1, K["k"] // 2)), max(d0) - 1))
        ring = [x for x in range(K["n"]) if d0[x] == r]
        inside = sorted((x for x in range(K["n"]) if d0[x] < r), key=lambda x: -d0[x])
        plan = ring + inside
        for q in plan:
            if dup.z != z0 and d0[dup.z] > r:
                break                                  # the vortex escaped: restart around it
            if q in dup.peb:
                continue
            if len(dup.peb) >= M:
                far = [p for p in dup.peb if d0[p] > r]
                if not far:
                    break
                dup.remove(max(far, key=lambda p: d0[p]))
            if not dup.place(q):
                return False
    return True
