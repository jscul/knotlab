#!/usr/bin/env python3
"""Checks for DISTANCE-20261108-001B: distance across time is native as a cone.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Needs numpy and networkx (the repository's .venv). 16 worker processes, a few minutes. Readings at the cell level follow rows of M^T
(net_lib) to a stated lag, or until the next row lies in the span of the earlier ones (exact); walk-count readings follow rows of A^k
until the next row lies in the span of the earlier ones (lattice_lib.reach, exact). Checks 9 to 11 are computations, not theorems."""
import hashlib
import heapq
import itertools
import json
import random
import sys
import time
from collections import Counter, defaultdict, deque
from math import comb
from multiprocessing import Pool
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A_DIR = ROOT / "experiments/DISTANCE-20261108-001A/DISTANCE-20261108-001A-E001_isolated_routes"
sys.path.insert(0, str(A_DIR))
import distance_lib as D  # noqa: E402

LN, T, N, Gl = D.LN, D.T, D.N, D.Gl
T0 = time.time()
OUT = {}
SEED = 20261108


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:400], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


DEPS = {
    "experiments/DISTANCE-20261108-001A/DISTANCE-20261108-001A-E001_isolated_routes/contract.json":
        "c7818ce53ded426b0d79a11940e93bc1e8842f7dbf2a823dbfc26feb8e3ecaae",
    "experiments/DISTANCE-20261108-001A/DISTANCE-20261108-001A-E001_isolated_routes/run.py":
        "7e109b3b76c426e27173e1b97795d996e553cd7ffe386f0d59054bd6c9530960",
    "experiments/DISTANCE-20261108-001A/DISTANCE-20261108-001A-E001_isolated_routes/distance_lib.py":
        "ad7c26626e04edfe80cb6872fd2be92f2ae9d5b25e462c85872a5f7ab4bbe1dd",
    "proofs/GENUS-CUT-20261108-001A/GENUS-CUT-20261108-001A-P001_two_rings_of_cuts_per_handle/manifest.json":
        "1a4e62c47587f50eb1de77e7371ca1b4d5a5224536724de5993452683310444f",
    "proofs/LATTICE-NET-20261108-001A/LATTICE-NET-20261108-001A-P001_odd_tori_compose_rings_of_cuts_separate/manifest.json":
        "9ba1f3e50d4015eed6677f40bf3dc74c93024d7cb6b69c4ab49656176704643a",
    "proofs/LOOP-NET-20261108-001A/LOOP-NET-20261108-001A-P001_symmetry_cancels_returns/manifest.json":
        "ea82b4fbe792a325ce481430b65203894505095f86c54798973cb5a58d1134e5",
}


# ---------- networks and readings
def net(name):
    if name.startswith("square torus "):
        return LN.square_torus(int(name.split()[-1]))
    if name.startswith("triangular torus "):
        return LN.triangular_torus(int(name.split()[-1]))
    if name.startswith("honeycomb torus "):
        return LN.honeycomb_torus(int(name.split()[-1]))
    if name in ("tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"):
        return LN.platonic(name)
    return D.substrates()[name]


G2 = "genus 2, 16 rings of three contacts (GL(2,3))"
G2D = "genus 2, 6 rings of eight contacts (GL(2,3))"
G3 = "genus 3, 56 rings of three contacts (Klein quartic, PSL(2,7))"
G3D = "genus 3, 24 rings of seven contacts (PSL(2,7))"
PLATONIC = ["tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"]


class Net:
    def __init__(self, name, g=2, gaps_seed=None):
        self.name = name
        self.rot, self.edges = net(name)
        if gaps_seed is None:
            self.sizes, self.contacts = LN.network(self.rot, self.edges, g)
        else:
            self.sizes, self.contacts = D.network_gaps(self.rot, self.edges, random.Random(gaps_seed), 2, 9)
        self.g = g
        self.out, self.inn, self.rc = D.graph(self.sizes, self.contacts)
        self.n = len(self.contacts)
        self.ring = Gl.ring_index(self.rot)
        self.ends = [(ra, rb) for (ra, pa, rb, pb, law) in self.contacts]

    def dist_to(self, c):
        """directed distance in arcs from every contact to c, and the number of shortest walks (arcs counted with multiplicity)"""
        dist, cnt = [None] * self.n, [0] * self.n
        dist[c], cnt[c] = 0, 1
        order, q = [c], deque([c])
        while q:
            x = q.popleft()
            for y, ring, l in self.inn[x]:
                if dist[y] is None:
                    dist[y] = dist[x] + 1
                    q.append(y)
                    order.append(y)
        for y in order[1:]:
            cnt[y] = sum(cnt[z] for z, ring, l in self.out[y] if dist[z] is not None and dist[z] == dist[y] - 1)
        return dist, cnt

    def first_odd(self, cut=()):
        """{c: {d: least k with an odd number of k-arc walks d -> c avoiding the cut}}"""
        ins = T.in_sets(self.sizes, self.contacts, cut)
        return {c: T.reach(ins, c)[1] for c in range(self.n) if c not in set(cut)}

    def ring_graph(self):
        G = nx.MultiGraph()
        G.add_nodes_from(range(len(self.rc)))
        for (ra, rb) in self.ends:
            G.add_edge(ra, rb)
        return G

    def cells_dist_to(self, c):
        """least cells (own cells + 1 per arc) of a walk from every contact to c, and the least arcs among such walks"""
        best = [None] * self.n
        best[c] = (0, 0)
        pq = [(0, 0, c)]
        while pq:
            w, a, x = heapq.heappop(pq)
            if (w, a) > best[x]:
                continue
            for y, ring, l in self.inn[x]:
                cand = (w + l + 1, a + 1)
                if best[y] is None or cand < best[y]:
                    best[y] = cand
                    heapq.heappush(pq, (cand[0], cand[1], y))
        return best


def cell_union(rows, start):
    """every first-row cell a value ever depends on: rows of M^T at lags 1, 2, ... until the next lies in the span of the earlier
    ones (GENUS-CUT-20261108-001A's check), exact"""
    row, union, basis = start, 0, {}
    while True:
        row = LN.step(rows, row)
        x = row
        while x:
            top = x.bit_length() - 1
            if top not in basis:
                break
            x ^= basis[top]
        if not x:
            return union
        basis[x.bit_length() - 1] = x
        union |= row


def need_lags(sizes, contacts, target, X, H, cut=()):
    rows, Nb, blocks = N.matrix(sizes, (60,) * len(sizes), contacts, cut=tuple(cut))
    mask = N.mask(blocks, X)
    row, out = 1 << target, []
    for t in range(1, H + 1):
        row = LN.step(rows, row)
        if row & mask:
            out.append(t)
    return out


# ---------- check 1: isolated induced routes, the need set by Lucas, every route contact binding at every lag
def induced(out, route):
    on = {c: i for i, c in enumerate(route)}
    return all(not (y in on and on[y] != i + 1) for i, c in enumerate(route) for y, ring, l in out[c])


def corner_into(contacts, out, inn, X, c0):
    """own cells of X's corner ending at c0"""
    return next(l for d, ring, l in inn[c0] if ring == X)


def task_routes(args):
    name, g, gaps_seed = args
    W = Net(name, g, gaps_seed)
    rng = random.Random("%d/routes/%s/%d/%s" % (SEED, name, g, gaps_seed))
    rings = sorted(W.rc)
    tested = bad = 0
    for L in range(1, 9):
        for _ in range(4):
            r = None
            for _ in range(80):
                X = rng.choice(rings)
                cand = D.random_route(rng, W.out, W.rc, W.n, X, L)
                if cand and D.valid_route(W.out, W.rc, W.contacts, cand, X) and induced(W.out, cand):
                    r = cand
                    break
            if r is None:
                continue
            lX = corner_into(W.contacts, W.out, W.inn, X, r[0])
            own = sum(c - 1 for c in D.hop_cells(W.out, r))
            H = 2 * (L + 1 + own + lX) + 40
            cut = [c for c in range(W.n) if c not in set(r)]
            got = need_lags(W.sizes, W.contacts, r[-1], X, H, cut)
            want = [t for t in range(1, H + 1) if t >= L + 1 and any(comb(t - L - 1, own + m) % 2 for m in range(lX))]
            # every route contact keeps its two chain-end witnesses at every lag to H (no returns on an induced route)
            rows, Nb, blocks = N.matrix(W.sizes, (60,) * len(W.sizes), W.contacts, cut=tuple(cut))
            rings_layout = N.layout(W.sizes, W.contacts)[0]
            wit = True
            for c in r:
                ra, pa, rb, pb, law = W.contacts[c]
                wa, wb = rings_layout[ra][pa - 1], rings_layout[rb][pb - 1]
                row = 1 << c
                for t in range(1, H + 1):
                    row = LN.step(rows, row)
                    if not (row >> wa & 1 and row >> wb & 1):
                        wit = False
                        break
            tested += 1
            bad += got != want or not wit
    return name, g, gaps_seed, tested, bad


# ---------- check 2: the earliest need over freeze sets
def task_earliest(args):
    name, g, gaps_seed, sample = args
    W = Net(name, g, gaps_seed)
    rng = random.Random("%d/earliest/%s/%d/%s" % (SEED, name, g, gaps_seed))
    pairs = [(X, c) for X in sorted(W.rc) for c in range(W.n) if c not in W.rc[X]]
    if sample and len(pairs) > sample:
        pairs = rng.sample(pairs, sample)
    fo = W.first_odd() if gaps_seed is None else None
    tested = bad = 0
    for X, c in pairs:
        best = W.cells_dist_to(c)
        cands = [(best[e], e) for e in W.rc[X] if best[e] is not None]
        if not cands:
            continue
        (cells, arcs), e0 = min(cands)
        # a cell-shortest route with the fewest arcs, traced forward from e0
        route = [e0]
        while route[-1] != c:
            x = route[-1]
            w, a = best[x]
            route.append(next(y for y, ring, l in sorted(W.out[x]) if best[y] is not None and best[y] == (w - l - 1, a - 1)))
        want = 1 + cells
        cut = [d for d in range(W.n) if d not in set(route)]
        t_iso = D.first_need(W.sizes, W.contacts, c, X, want, cut)
        ok = t_iso == want
        for p in (0.3, 0.6):
            F = [d for d in range(W.n) if d != c and rng.random() < p]
            ok &= D.first_need(W.sizes, W.contacts, c, X, want - 1, F) is None
        if gaps_seed is None:
            ok &= D.first_need(W.sizes, W.contacts, c, X, want - 1) is None
            ks = [fo[c][e] for e in W.rc[X] if e in fo[c]]
            if ks:
                k = min(ks)
                ok &= D.first_need(W.sizes, W.contacts, c, X, g * k + 1) == g * k + 1
        tested += 1
        bad += not ok
    return name, g, gaps_seed, tested, bad


# ---------- checks 3 and 4: cut counts
def pieces_labels(W, cut):
    """GENUS-CUT-20261108-001A's native pieces with their members: rings joined when an uncut contact on one needs the other"""
    ins = T.in_sets(W.sizes, W.contacts, cut)
    rc = {r: set(cs) for r, cs in W.rc.items()}
    parent = list(range(len(rc)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for c in range(W.n):
        if c in cut:
            continue
        ra, rb = W.ends[c]
        for y in T.rings_needed(T.reach(ins, c)[0], rc, cut):
            parent[find(ra)] = find(y)
            parent[find(rb)] = find(y)
    return [find(a) for a in range(len(rc))]


def task_pieces(args):
    name, sample = args
    W = Net(name, 2)
    rng = random.Random("%d/pieces/%s" % (SEED, name))
    dG = dict(nx.all_pairs_shortest_path_length(W.ring_graph()))
    pairs = [(X, Y) for X in sorted(W.rc) for Y in sorted(W.rc) if X < Y]
    if len(pairs) > sample:
        pairs = rng.sample(pairs, sample)
    tested = bad = cuts = 0
    for X, Y in pairs:
        Dxy = dG[X][Y]
        layers = [[c for c in range(W.n) if sorted((dG[X][W.ends[c][0]], dG[X][W.ends[c][1]])) == [i - 1, i]] for i in range(1, Dxy + 1)]
        ok = len(layers) == Dxy and all(set(a).isdisjoint(b) for a, b in itertools.combinations(layers, 2))
        for Lc in layers:
            lab = pieces_labels(W, set(Lc))
            ok &= lab[X] != lab[Y]
            cuts += 1
        tested += 1
        bad += not ok
    return name, tested, cuts, bad


def task_blocking(args):
    name, sample, cell_sample = args
    W = Net(name, 2)
    rng = random.Random("%d/blocking/%s" % (SEED, name))
    pairs = [(X, c) for X in sorted(W.rc) for c in range(W.n) if c not in W.rc[X]]
    if len(pairs) > sample:
        pairs = rng.sample(pairs, sample)
    tested = bad = cells_checked = 0
    for idx, (X, c) in enumerate(pairs):
        dist = D.dist_from(W.out, W.rc[X], W.n)
        d = dist[c]
        layers = [[e for e in range(W.n) if dist[e] == i] for i in range(d)]
        ok = all(c not in Lc for Lc in layers) and all(set(a).isdisjoint(b) for a, b in itertools.combinations(layers, 2))
        for Lc in layers:
            S = set(Lc)
            reach = D.dist_from({x: [t for t in W.out[x] if t[0] not in S] for x in range(W.n)}, [e for e in W.rc[X] if e not in S], W.n)
            ok &= reach[c] is None
            if idx < cell_sample:
                rows, Nb, blocks = N.matrix(W.sizes, (60,) * len(W.sizes), W.contacts, cut=tuple(sorted(S)))
                ok &= not (cell_union(rows, 1 << c) & N.mask(blocks, X))
                cells_checked += 1
        tested += 1
        bad += not ok
    return name, tested, cells_checked, bad


# ---------- check 5: the cone and its parity
def task_cone(name):
    W = Net(name, 2)
    fo = W.first_odd()
    eq = later = never = bad = 0
    for c in range(W.n):
        dist, cnt = W.dist_to(c)
        for X, cs in W.rc.items():
            d = min(dist[e] for e in cs if dist[e] is not None)
            ks = [fo[c][e] for e in cs if e in fo[c]]
            k = min(ks) if ks else None
            odd = any(dist[e] == d and cnt[e] % 2 for e in cs)
            if k is not None and k < d:
                bad += 1
            if (k == d) != odd:
                bad += 1
            if k is None:
                never += 1
            elif k == d:
                eq += 1
            else:
                later += 1
    return name, eq, later, never, bad


# ---------- check 6: the square torus
def sq_positions(n):
    """(u, w) of each contact of LN.square_torus(n) (rings at p, h(p) at p + (1/2, 0), v(p) at p + (0, 1/2)), doubled to integers"""
    rot, edges = LN.square_torus(n)
    pos = []
    for (u, w) in edges:
        if (w[0] - u[0]) % n == 1 and w[1] == u[1]:
            x, y = 2 * u[0] + 1, 2 * u[1]
            kind = "h"
        else:
            x, y = 2 * u[0], 2 * u[1] + 1
            kind = "v"
        pos.append((kind, x, y))
    return pos


def sq_closed(n, a, b):
    """the closed form of the directed distance from contact a to contact b, least over lifts"""
    ka, xa, ya = a
    kb, xb, yb = b
    best = None
    for s in (-1, 0, 1):
        for t in (-1, 0, 1):
            dx, dy = (xb + 2 * n * s - xa) // 1, (yb + 2 * n * t - ya)
            du, dw = (dx + dy) // 2, (dy - dx) // 2
            if ka == kb:
                v = 2 * max(abs(du), abs(dw))
            elif ka == "h":
                v = 2 * max(abs(du), abs(dw) - 1) + 1
            else:
                v = 2 * max(abs(dw), abs(du) - 1) + 1
            best = v if best is None else min(best, v)
    return best


def task_square(n):
    W = Net("square torus %d" % n, 2)
    pos = sq_positions(n)
    dG = dict(nx.all_pairs_shortest_path_length(W.ring_graph()))
    bad_closed = bad_D = 0
    for c in range(W.n):
        dist, cnt = W.dist_to(c)
        for e in range(W.n):
            bad_closed += dist[e] != sq_closed(n, pos[e], pos[c])
        for X, cs in W.rc.items():
            d = min(dist[e] for e in cs)
            Dx = min(dG[X][W.ends[c][0]], dG[X][W.ends[c][1]])
            bad_D += Dx != (d + 1) // 2
    # contacts of one kind: the plain need of a contact on another's first value is on time iff a AND b = 0 (unique least lift)
    fo = W.first_odd()
    lucas_bad = lucas_tested = 0
    for c in range(W.n):
        dist, cnt = W.dist_to(c)
        for e in range(W.n):
            if pos[e][0] != pos[c][0]:
                continue
            a = (pos[c][1] - pos[e][1]) // 2 % n
            b = (pos[c][2] - pos[e][2]) // 2 % n
            a, b = min(a, n - a), min(b, n - b)
            on_time = fo[c].get(e) == dist[e]
            unique = 2 * a != n and 2 * b != n
            lucas_tested += 1
            lucas_bad += on_time != (unique and (a & b) == 0) or dist[e] != 2 * (a + b)
    return n, bad_closed, bad_D, lucas_tested, lucas_bad


# ---------- check 7: the plane, Frobenius
def plane(J=63, R=31):
    size = 2 * J + 1
    P = np.zeros((size, size), dtype=np.uint8)
    P[J, J] = 1
    first = {}
    for j in range(J + 1):
        if j:
            Q = np.zeros_like(P)
            Q[1:, :] ^= P[:-1, :]
            Q[:-1, :] ^= P[1:, :]
            Q[:, 1:] ^= P[:, :-1]
            Q[:, :-1] ^= P[:, 1:]
            P = Q
        for a in range(-R, R + 1):
            for b in range(-R, R + 1):
                if (a, b) not in first and P[J + a, J + b]:
                    first[(a, b)] = j

    def v2(x):
        return 99 if x == 0 else (x & -x).bit_length() - 1
    bad, never, total = 0, 0, 0
    for a in range(-R, R + 1):
        for b in range(-R, R + 1):
            total += 1
            nev = (a, b) != (0, 0) and v2(abs(a)) == v2(abs(b))
            never += nev
            bad += nev == ((a, b) in first)
            if (a, b) in first:
                bad += first[(a, b)] < abs(a) + abs(b)
    doubling = sum(1 for (a, b), j in first.items() if (2 * a, 2 * b) in first and first[(2 * a, 2 * b)] != 2 * j)
    doubled_pairs = sum(1 for (a, b) in first if (2 * a, 2 * b) in first)
    return {"window": "|a|, |b| <= %d, powers of L to %d" % (R, J), "points": total, "never reached": never,
            "share never": round(never / total, 4), "mismatches with v2(a) = v2(b)": bad,
            "doubling k(2a, 2b) = 2 k(a, b) checked on": doubled_pairs, "doubling failures": doubling}


# ---------- check 8: translates
def shift_fn(kind, n):
    if kind == "honeycomb":
        return lambda v, a, b: ((v[0] + a) % n, (v[1] + b) % n, v[2])
    return lambda v, a, b: ((v[0] + a) % n, (v[1] + b) % n)


def task_translates(args):
    kind, n = args
    W = Net("%s torus %d" % (kind, n), 2)
    m = {"square": 4, "triangular": 6, "honeycomb": 3}[kind]
    dG = dict(nx.all_pairs_shortest_path_length(W.ring_graph()))
    shift = shift_fn(kind, n)
    eid = {(u, w): e for e, (u, w) in enumerate(W.edges)}
    bad = tested = 0
    for e, (u, w) in enumerate(W.edges):
        dist = D.dist_from(W.out, [e], W.n)
        for a in range(n):
            for b in range(n):
                f = eid[(shift(u, a, b), shift(w, a, b))]
                Dv = dG[W.ring[u]][W.ring[shift(u, a, b)]]
                tested += 1
                bad += 2 * dist[f] != m * Dv
    return kind, n, tested, bad


# ---------- check 9: the triangular and honeycomb bands, and the other networks (computed)
def task_band(name):
    W = Net(name, 2)
    dG = dict(nx.all_pairs_shortest_path_length(W.ring_graph()))
    tab = Counter()
    for c in range(W.n):
        dist, cnt = W.dist_to(c)
        for X, cs in W.rc.items():
            d = min(dist[e] for e in cs)
            Dx = min(dG[X][W.ends[c][0]], dG[X][W.ends[c][1]])
            tab[(Dx, d)] += 1
    return name, sorted(tab.items())


# ---------- check 10: the plain first need is not a metric (computed)
def task_metric(name):
    W = Net(name, 2)
    fo = W.first_odd()
    n = W.n
    K = [[fo[c].get(e) for c in range(n)] for e in range(n)]  # K[e][c]: contact c's plain need on e's first value, in arcs
    dist = [W.dist_to(c)[0] for c in range(n)]
    Dm = [[dist[c][e] for c in range(n)] for e in range(n)]
    tri = bad = 0
    for a in range(n):
        for b in range(n):
            if K[a][b] is None:
                continue
            for c in range(n):
                if K[b][c] is None:
                    continue
                tri += 1
                bad += K[a][c] is None or K[a][c] > K[a][b] + K[b][c]
    asymK = sum(K[a][b] != K[b][a] for a in range(n) for b in range(n))
    asymD = max(abs(Dm[a][b] - Dm[b][a]) for a in range(n) for b in range(n))
    trid = sum(1 for a in range(n) for b in range(n) for c in range(n) if Dm[a][c] > Dm[a][b] + Dm[b][c])
    rings = sorted(W.rc)
    KR = {(X, Y): min([K[e][c] for e in W.rc[X] for c in W.rc[Y] if K[e][c] is not None], default=None) for X in rings for Y in rings}
    rtri = rbad = 0
    for X in rings:
        for Y in rings:
            if KR[(X, Y)] is None:
                continue
            for Z in rings:
                if KR[(Y, Z)] is None:
                    continue
                rtri += 1
                rbad += KR[(X, Z)] is None or KR[(X, Z)] > KR[(X, Y)] + KR[(Y, Z)]
    rnever = sum(v is None for v in KR.values())
    DR = {(X, Y): min(Dm[e][c] for e in W.rc[X] for c in W.rc[Y]) for X in rings for Y in rings}
    drbad = sum(1 for X in rings for Y in rings for Z in rings if DR[(X, Z)] > DR[(X, Y)] + DR[(Y, Z)])
    cr_never = sum(1 for c in range(n) for X in rings if all(K[e][c] is None for e in W.rc[X]))
    return {"network": name, "contact to contact: triangle violations": "%d of %d" % (bad, tri),
            "contact to contact: ordered pairs with K(a, b) != K(b, a)": asymK,
            "directed distance: triangle violations": trid, "directed distance: largest |d(a, b) - d(b, a)|": asymD,
            "ring to ring: triangle violations": "%d of %d" % (rbad, rtri), "ring to ring: pairs never needed": rnever,
            "directed distance, ring to ring (least over their contacts): triangle violations": "%d of %d" % (drbad, len(rings) ** 3),
            "contact needing ring: pairs never": cr_never}


# ---------- check 11: generic spacing (computed)
def task_generic(args):
    name, rep = args
    W = Net(name, 2, gaps_seed=rep)
    rows, Nb, blocks = N.matrix(W.sizes, (60,) * len(W.sizes), W.contacts)
    eq = later = none = 0
    H = 300
    for c in range(W.n):
        best = W.cells_dist_to(c)
        row, firsts = 1 << c, {}
        for t in range(1, H + 1):
            row = LN.step(rows, row)
            for X in W.rc:
                if X not in firsts and row & N.mask(blocks, X):
                    firsts[X] = t
            if len(firsts) == len(W.rc):
                break
        for X in W.rc:
            want = 1 + min(best[e][0] for e in W.rc[X])
            if X not in firsts:
                none += 1
            elif firsts[X] == want:
                eq += 1
            else:
                later += 1
    rc = LN.read_cells(W.sizes, W.contacts, H)
    return {"network": name, "replicate": rep, "first need at 1 + least cells": eq, "later": later, "none by lag 300": none,
            "contacts losing a witness by lag 300": sum(l is not None for l, m in rc),
            "contacts missing a ring by lag 300": sum(m is not None for l, m in rc), "contacts": W.n}


def main():
    write = "--write" in sys.argv
    bad = {p: h for p, h in DEPS.items() if sha(p) != h}
    check("0 dependencies bound by hash", not bad, {"files": len(DEPS), "mismatched": sorted(bad)})
    with Pool(16) as pool:
        nets1 = ["square torus 5", "triangular torus 4", "honeycomb torus 4", G2, G3, "dodecahedron", G2D]
        r1 = pool.map(task_routes, [(nm, g, None) for nm in nets1 for g in (2, 3, 4)] +
                      [(nm, 2, s) for nm in ("square torus 5", G2) for s in (1, 2)])
        check("1 isolated induced routes: the need set is the Lucas set, every route contact keeps its witnesses",
              all(x[4] == 0 for x in r1), {"routes": sum(x[3] for x in r1), "failures": sum(x[4] for x in r1),
                                           "networks": len({x[0] for x in r1}), "spacings": "2, 3, 4 and unequal (2 to 9)"})
        nets2 = [("square torus 5", None), ("square torus 6", None), ("triangular torus 4", None), ("honeycomb torus 3", None),
                 ("honeycomb torus 4", None), ("cube", None), ("dodecahedron", None), (G2, None), (G3, 600), (G3D, 600)]
        r2 = pool.map(task_earliest, [(nm, g, None, s) for nm, s in nets2 for g in (2, 3)] +
                      [(nm, 2, s, 400) for nm in ("square torus 5", G2) for s in (1, 2)])
        check("2 the earliest need any freeze allows is 1 + the least cells of a route (g d + 1 at equal spacing); unaided at g k + 1",
              all(x[4] == 0 for x in r2), {"pairs": sum(x[3] for x in r2), "failures": sum(x[4] for x in r2)})
        r3 = pool.map(task_pieces, [("square torus 5", 300), ("square torus 6", 300), ("triangular torus 5", 300),
                                    ("honeycomb torus 4", 300), ("cube", 300), ("dodecahedron", 300), (G2, 300), (G3, 200), (G3D, 200)])
        check("3 the most disjoint cuts that leave two rings in different native pieces is the ring graph's distance (layer cuts)",
              all(x[3] == 0 for x in r3), {"ring pairs": sum(x[1] for x in r3), "layer cuts": sum(x[2] for x in r3),
                                           "failures": sum(x[3] for x in r3)})
        r4 = pool.map(task_blocking, [("square torus 5", 400, 60), ("triangular torus 4", 400, 60), ("honeycomb torus 4", 400, 60),
                                      ("cube", 400, 60), ("dodecahedron", 400, 60), (G2, 400, 60), (G3, 300, 30)])
        check("4 the most disjoint sets that block a ring from a contact for good is the directed distance (layers of the contact graph)",
              all(x[3] == 0 for x in r4), {"pairs": sum(x[1] for x in r4), "layer cuts read at the cell level (exact)": sum(x[2] for x in r4),
                                           "failures": sum(x[3] for x in r4)})
        cone_nets = (["square torus %d" % n for n in (5, 6, 7, 8)] + ["triangular torus %d" % n for n in (4, 5, 6, 7)] +
                     ["honeycomb torus %d" % n for n in (3, 4, 5, 6)] + PLATONIC + [G2, G2D, G3, G3D])
        r5 = pool.map(task_cone, cone_nets)
        check("5 cone: the plain first need is never before the directed distance, and on time exactly when an odd number of shortest routes "
              "arrive", all(x[4] == 0 for x in r5),
              {x[0]: {"on time": x[1], "later": x[2], "never": x[3]} for x in r5})
        r6 = pool.map(task_square, range(5, 14))
        check("6 square torus: closed forms of the directed distance, D = ceil(d / 2) for every ring and contact, Lucas for one kind",
              all(x[1] == 0 and x[2] == 0 and x[4] == 0 for x in r6),
              {"sides": [x[0] for x in r6], "closed-form mismatches": sum(x[1] for x in r6), "D mismatches": sum(x[2] for x in r6),
               "same-kind pairs": sum(x[3] for x in r6), "Lucas mismatches": sum(x[4] for x in r6)})
        p7 = plane()
        check("7 the plane: a contact's need on another of its kind at offset (a, b) never comes exactly when v2(a) = v2(b); k(2a, 2b) = 2k(a, b)",
              p7["mismatches with v2(a) = v2(b)"] == 0 and p7["doubling failures"] == 0, p7)
        r8 = pool.map(task_translates, [("square", n) for n in range(5, 11)] + [("triangular", n) for n in range(4, 10)] +
                      [("honeycomb", n) for n in range(3, 9)])
        check("8 translates: the directed distance from a contact to its translate is m/2 times the ring graph's distance",
              all(x[3] == 0 for x in r8), {"pairs": sum(x[2] for x in r8), "failures": sum(x[3] for x in r8),
                                           "tori": ["%s %d" % (x[0], x[1]) for x in r8]})
        r9 = dict(pool.map(task_band, ["triangular torus %d" % n for n in range(4, 11)] + ["honeycomb torus %d" % n for n in range(3, 10)] +
                           [G2, G2D, G3, G3D] + PLATONIC))
        tri_ok = all(D_ == (d + 2) // 3 for nm, tab in r9.items() if nm.startswith("triangular") for (D_, d), k in tab)
        hc_ok = all(-(-3 * D_ // 2) - 1 <= d <= -(-3 * D_ // 2) for nm, tab in r9.items() if nm.startswith("honeycomb") for (D_, d), k in tab)
        check("9 computed: triangular tori D = ceil(d / 3) (sides 4 to 10); honeycomb tori ceil(3D/2) - 1 <= d <= ceil(3D/2) (sides 3 to 9)",
              tri_ok and hc_ok, {nm: [[list(k), v] for k, v in tab] for nm, tab in r9.items() if not nm.startswith(("triangular", "honeycomb"))})
        r10 = pool.map(task_metric, ["square torus %d" % n for n in (5, 6, 7)] + ["triangular torus %d" % n for n in (4, 5)] +
                       ["honeycomb torus %d" % n for n in (3, 4, 5, 7, 9)] + PLATONIC + [G2, G2D, G3])
        check("10 computed: the plain first need is not a metric; the directed distance is a directed metric",
              all(x["directed distance: triangle violations"] == 0 for x in r10) and
              any(not x["contact to contact: triangle violations"].startswith("0 ") for x in r10), r10)
        r11 = pool.map(task_generic, [(nm, rep) for nm in ("square torus 5", G2) for rep in (0, 1, 2)])
        check("11 computed: unequal spacing (2 to 9 cells): the plain first need mostly meets 1 + the least cells, and witnesses lapse", True, r11)
    res = {"ticket": "DISTANCE-20261108-001B", "checks": OUT, "status": "passed"}
    path = HERE / "result.json"
    if write:
        path.write_text(json.dumps(res, indent=1, default=str) + "\n")
        print("wrote", path.relative_to(ROOT))
    else:
        old = json.loads(path.read_text())
        same = json.dumps(old, sort_keys=True, default=str) == json.dumps(json.loads(json.dumps(res, default=str)), sort_keys=True)
        print("result.json", "matches" if same else "DIFFERS")
        if not same:
            sys.exit(1)

if __name__ == "__main__":
    main()
