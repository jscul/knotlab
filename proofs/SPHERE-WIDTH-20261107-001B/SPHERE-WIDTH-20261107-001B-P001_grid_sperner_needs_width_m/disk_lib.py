"""Obstruction certificates for Sperner states on the disk, for SPHERE-WIDTH-20261107-001B.

FLAT-STATES-20261107-001B's window criterion: with the boundary's colours fixed and h(p) = c_p + 3 s_p at the pebbles, a state whose
only full triangle is T (counterclockwise) exists iff s_q - s_p <= floor((d(p, q) - c_q + c_p) / 3) has no negative cycle, where d is
the shortest-path distance for the weights 1 - tau (tau = +-3 across a ray from T, 0 elsewhere). This module extracts a negative cycle
and the closed walk through its shortest paths, and records what the boundary lemma needs: each segment's distance d and term b, and
where the walk goes.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "proofs/FLAT-STATES-20261107-001B/FLAT-STATES-20261107-001B-P001_the_knot_sphere_contains_sperner"))
import window_lib as W  # noqa: E402


def graph(m, T):
    V, _, E = W.grid(m)
    w = {}
    for u, v in E:
        t = W.tau(T, u, v)
        w[(u, v)] = 1 - t
        w[(v, u)] = 1 + t
    adj = {v: [] for v in V}
    for (u, v), c in w.items():
        adj[u].append((v, c))
    return V, adj


def bellman_ford(V, adj, src):
    d = {v: None for v in V}
    pred = {v: None for v in V}
    d[src] = 0
    for _ in range(len(V)):
        changed = False
        for u in V:
            if d[u] is None:
                continue
            for v, c in adj[u]:
                if d[v] is None or d[u] + c < d[v]:
                    d[v], pred[v] = d[u] + c, u
                    changed = True
        if not changed:
            break
    return d, pred


def certificate(m, T, peb):
    """None if T is feasible; else (cycle of pebbles, segments [(p, q, path, d, b)], walk)"""
    V, adj = graph(m, T)
    P = sorted(peb)
    DP = {p: bellman_ford(V, adj, p) for p in P}
    b = {(p, q): (DP[p][0][q] - peb[q] + peb[p]) // 3 for p in P for q in P if p != q}
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
    cyc.reverse()
    segs, walk = [], [cyc[0]]
    for p, q in zip(cyc, cyc[1:] + cyc[:1]):
        path, v = [q], q
        while v != p:
            v = DP[p][1][v]
            path.append(v)
        path.reverse()
        segs.append((p, q, path, DP[p][0][q], b[(p, q)]))
        walk += path[1:]
    return cyc, segs, walk


def depth(m, v):
    """lattice distance from v to the boundary of the side-m triangle"""
    return min(v[0], v[1], m - v[0] - v[1])


def winding3(T, walk):
    """3 x the winding of a closed walk around T (signed ray crossings)"""
    return sum(W.tau(T, u, v) for u, v in zip(walk, walk[1:]))
