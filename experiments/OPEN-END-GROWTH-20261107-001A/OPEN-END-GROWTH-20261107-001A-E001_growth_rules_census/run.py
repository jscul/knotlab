#!/usr/bin/env python3
"""OPEN-END-GROWTH-20261107-001A-E001 (exploratory): growth rules that act only at open ends.

    .venv/bin/python -B experiments/OPEN-END-GROWTH-20261107-001A/OPEN-END-GROWTH-20261107-001A-E001_growth_rules_census/run.py

Writes artifacts/OPEN-END-GROWTH-20261107-001A/OPEN-END-GROWTH-20261107-001A-E001_growth_rules_census/run/result.json.

Model (hub-free parity laws as knot graphs). Each knot is a vertex holding three distinctions. A distinction
shared by two knots is an edge; a distinction held by one knot is an open end, an edge to an outside vertex
INF that carries no constraint. Implied checks are the cuts of sets of knots, so the K1-K3 knots are the
bonds of size >= 3. Exact bond distance between two distinctions: the least bond containing both, minus one,
computed as a minimum cut whose inside contains a path between the two distinctions' chosen endpoints and
whose outside (with INF) is connected; infinite when no bond of size >= 3 contains both.
"""

from __future__ import annotations

import collections
import json
import math
import random
import sys
import time
from pathlib import Path

import networkx as nx
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "OPEN-END-GROWTH-20261107-001A" / "OPEN-END-GROWTH-20261107-001A-E001_growth_rules_census" / "run"
LOCAL = 6           # local rules see connected regions of at most this many knots
FLAT = 6            # the flat face size of three-place knots, as a bond distance
INF = "INF"


class KG:
    """Knot graph: adjacency multiset between knots, and open ends per knot."""

    def __init__(self):
        self.adj: dict[int, list[int]] = {0: []}
        self.opens: dict[int, int] = {0: 3}
        self.n = 1

    def sprout(self, v: int) -> int:
        w = self.n
        self.n += 1
        self.adj[w] = [v]
        self.adj[v].append(w)
        self.opens[v] -= 1
        self.opens[w] = 2
        return w

    def close(self, v: int, u: int) -> int:
        w = self.n
        self.n += 1
        self.adj[w] = [v, u]
        self.adj[v].append(w)
        self.adj[u].append(w)
        self.opens[v] -= 1
        self.opens[u] -= 1
        self.opens[w] = 1
        return w

    def undo_close(self, v: int, u: int, w: int) -> None:
        self.adj[v].remove(w)
        self.adj[u].remove(w)
        del self.adj[w]
        del self.opens[w]
        self.opens[v] += 1
        self.opens[u] += 1
        self.n -= 1

    def open_ends(self) -> list[int]:
        return [v for v, k in self.opens.items() for _ in range(k)]

    def cut(self, U) -> int:
        return sum(self.opens[v] + sum(1 for w in self.adj[v] if w not in U) for v in U)

    def cycle_rank(self) -> int:
        return sum(len(a) for a in self.adj.values()) // 2 - (self.n - 1)

    def local_pairs(self) -> dict[tuple[int, int], int]:
        """Local bond distance between open ends on distinct knots: least |cut(U)| - 1 over connected U of at
        most LOCAL knots containing both knots."""
        holders = {v for v, k in self.opens.items() if k > 0}
        best: dict[tuple[int, int], int] = {}
        for v in holders:
            frontier = [frozenset([v])]
            seen = set(frontier)
            for size in range(1, LOCAL + 1):
                nxt = []
                for U in frontier:
                    c = self.cut(U) - 1
                    for u in U:
                        if u != v and u in holders:
                            key = (min(u, v), max(u, v))
                            if key not in best or c < best[key]:
                                best[key] = c
                    if size == LOCAL:
                        continue
                    for x in U:
                        for y in self.adj[x]:
                            if y not in U:
                                W = U | {y}
                                if W not in seen:
                                    seen.add(W)
                                    nxt.append(W)
                frontier = nxt
        return best

    # --- the parity law ------------------------------------------------------------------------------
    def edges(self):
        """Distinctions: (id, endpoint, endpoint) with INF for open ends; parallel edges kept distinct."""
        out, eid = [], 0
        mult = collections.Counter()
        for v, nb in self.adj.items():
            for w in nb:
                if v < w:
                    mult[(v, w)] += 1
        for (v, w), k in sorted(mult.items()):
            for _ in range(k):
                out.append((eid, v, w))
                eid += 1
        for v in sorted(self.opens):
            for _ in range(self.opens[v]):
                out.append((eid, v, INF))
                eid += 1
        return out

    def pins_and_ties(self, ties: bool = True) -> tuple[int, int]:
        """Pinned distinctions (bridges of the graph with INF) and tied pairs (two-edge cuts)."""
        H = nx.MultiGraph()
        for eid, a, b in self.edges():
            H.add_edge(a, b, key=eid)
        def single_bridges(G):
            mult = collections.Counter(frozenset((a, b)) for a, b, _ in G.edges(keys=True))
            S = nx.Graph([tuple(e) for e in mult if len(e) == 2])
            return [b for b in nx.bridges(S) if mult[frozenset(b)] == 1]
        pins = len(single_bridges(H))
        tie_count = 0
        if ties:
            for a, b, k in list(H.edges(keys=True)):
                H.remove_edge(a, b, key=k)
                if nx.is_connected(H):
                    tie_count += len(single_bridges(H))
                H.add_edge(a, b, key=k)
            tie_count //= 2
        return pins, tie_count

    def has_pin_or_tie(self) -> bool:
        """Same answer as pins_and_ties(), returning at the first pin or tie found."""
        H = nx.MultiGraph()
        for eid, a, b in self.edges():
            H.add_edge(a, b, key=eid)
        def single_bridges(G):
            mult = collections.Counter(frozenset((a, b)) for a, b, _ in G.edges(keys=True))
            S = nx.Graph([tuple(e) for e in mult if len(e) == 2])
            return [b for b in nx.bridges(S) if mult[frozenset(b)] == 1]
        if single_bridges(H):
            return True
        for a, b, k in list(H.edges(keys=True)):
            H.remove_edge(a, b, key=k)
            found = nx.is_connected(H) and bool(single_bridges(H))
            H.add_edge(a, b, key=k)
            if found:
                return True
        return False


# --- exact bond distance ----------------------------------------------------------------------------------
def decoupled(g: KG, e, f) -> bool:
    """True when a pinned seam separates e and f, or one of them is pinned: a bridge of the graph with INF
    has a side without INF, hence without open ends, and no knot crosses it (ticket B, Proposition 2)."""
    H = nx.MultiGraph()
    for eid, a, b in g.edges():
        H.add_edge(a, b, key=eid)
    mult = collections.Counter(frozenset((a, b)) for a, b, _ in H.edges(keys=True))
    S = nx.Graph([tuple(x) for x in mult if len(x) == 2])
    bridges = {frozenset(b) for b in nx.bridges(S) if mult[frozenset(b)] == 1}
    for edge in (e, f):
        if frozenset((edge[1], edge[2])) in bridges:
            return True
    T = nx.Graph(S)
    T.remove_edges_from([tuple(b) for b in bridges])
    comp = {}
    for i, c in enumerate(nx.connected_components(T)):
        for x in c:
            comp[x] = i
    # each non-bridge edge lies inside one two-edge-connected component
    return comp[e[1]] != comp[f[1]]


def bond_distance(g: KG, e, f, outside_connected: bool = True):
    """Least bond (size >= 3) containing distinctions e and f, minus one; None when there is none,
    "unresolved" when the program hits its time limit."""
    if outside_connected and decoupled(g, e, f):
        return None
    edges = g.edges()
    verts = sorted(g.adj)
    vi = {v: i for i, v in enumerate(verts)}
    best = None
    def sides(edge):
        _, a, b = edge
        return [(a, b)] if b == INF else [(a, b), (b, a)]
    for ie, oe in sides(e):
        for if_, of in sides(f):
            try:
                val = _milp(g, edges, verts, vi, ie, oe, if_, of, outside_connected)
            except TimeoutError:
                return "unresolved"
            if val is not None and (best is None or val < best):
                best = val
    if best is None or best < 3:
        return None
    return best - 1


def _milp(g, edges, verts, vi, ie, oe, if_, of, outside_connected):
    n, m = len(verts), len(edges)
    internal = [(eid, a, b) for eid, a, b in edges if b != INF]
    opens = [(eid, a) for eid, a, b in edges if b == INF]
    k = len(internal)
    # variables: x (n) | y (m) | path flow p (2k) | outside flow h (2k + len(opens))
    off_y, off_p, off_h = n, n + m, n + m + 2 * k
    nh = (2 * k + len(opens)) if outside_connected else 0
    nvar = n + m + 2 * k + nh
    A = lil_matrix((2 * m + 4 * k + n + (2 * (2 * k) + len(opens) + n if outside_connected else 0), nvar))
    lo, hi = [], []
    r = 0
    for j, (eid, a, b) in enumerate(edges):
        if b == INF:
            A[r, off_y + j] = 1; A[r, vi[a]] = -1; lo.append(0); hi.append(np.inf); r += 1
        else:
            A[r, off_y + j] = 1; A[r, vi[a]] = -1; A[r, vi[b]] = 1; lo.append(0); hi.append(np.inf); r += 1
            A[r, off_y + j] = 1; A[r, vi[a]] = 1; A[r, vi[b]] = -1; lo.append(0); hi.append(np.inf); r += 1
    pcol = {}
    for q, (eid, a, b) in enumerate(internal):
        pcol[(a, b, q)] = off_p + 2 * q
        pcol[(b, a, q)] = off_p + 2 * q + 1
    for (a, b, q), col in pcol.items():
        for endpoint in (a, b):
            A[r, col] = 1; A[r, vi[endpoint]] = -1; lo.append(-np.inf); hi.append(0); r += 1
    base = r
    for v in verts:
        want = (1 if v == ie else 0) - (1 if v == if_ else 0)
        lo.append(want); hi.append(want)
    for (a, b, q), col in pcol.items():
        A[base + vi[a], col] += 1
        A[base + vi[b], col] -= 1
    r += n
    if outside_connected:
        M = n
        hcol = {}
        for q, (eid, a, b) in enumerate(internal):
            hcol[(a, b, q)] = off_h + 2 * q
            hcol[(b, a, q)] = off_h + 2 * q + 1
        ocol = {}
        for t, (eid, a) in enumerate(opens):
            ocol[(a, t)] = off_h + 2 * k + t
        for (a, b, q), col in hcol.items():
            for endpoint in (a, b):
                A[r, col] = 1; A[r, vi[endpoint]] = M; lo.append(-np.inf); hi.append(M); r += 1
        for (a, t), col in ocol.items():
            A[r, col] = 1; A[r, vi[a]] = M; lo.append(-np.inf); hi.append(M); r += 1
        base = r
        for v in verts:
            # inflow - outflow = 1 - x_v   ->   inflow - outflow + x_v = 1
            A[base + vi[v], vi[v]] = 1
            lo.append(1); hi.append(1)
        for (a, b, q), col in hcol.items():
            A[base + vi[b], col] += 1      # flow a -> b enters b
            A[base + vi[a], col] -= 1
        for (a, t), col in ocol.items():
            A[base + vi[a], col] += 1      # flow from INF enters a
        r += n
    A = A[:r].tocsr()
    c = np.zeros(nvar)
    c[off_y:off_y + m] = 1.0
    lb = np.zeros(nvar)
    ub = np.ones(nvar)
    ub[off_p:off_p + 2 * k] = 1.0
    if outside_connected:
        ub[off_h:] = n
    for v in (ie, if_):
        lb[vi[v]] = 1
    for v in (oe, of):
        if v != INF:
            ub[vi[v]] = 0
    if any(lb[i] > ub[i] for i in range(n)):
        return None
    integ = np.zeros(nvar)
    integ[:n] = 1
    res = milp(c, constraints=LinearConstraint(A, lo, hi), integrality=integ, bounds=Bounds(lb, ub),
               options={"time_limit": 60})
    if res.status == 1:
        raise TimeoutError("time limit")
    if res.status != 0 or res.x is None:
        return None
    return int(round(res.fun))


# --- rules ------------------------------------------------------------------------------------------------
def grow(rule: str, size: int, rng: random.Random, checkpoints):
    g = KG()
    trace = []
    while g.n < size:
        if rule == "R1":
            g.sprout(rng.choice(g.open_ends()))
        elif rule == "R2":
            holders = [v for v, k in g.opens.items() if k >= 2]
            g.sprout(rng.choice(holders))
        elif rule in ("R3", "R4"):
            pairs = g.local_pairs()
            cand = [(d, p) for p, d in pairs.items() if d <= 6]
            done = False
            if cand:
                dmin = min(d for d, _ in cand)
                choices = [p for d, p in cand if d == dmin]
                if rule == "R3":
                    a, b = rng.choice(choices)
                    g.close(a, b)
                    done = True
                else:
                    order = sorted(cand, key=lambda dp: (dp[0], rng.random()))
                    for d, (a, b) in order:
                        w = g.close(a, b)
                        if g.has_pin_or_tie():
                            g.undo_close(a, b, w)
                            continue
                        done = True
                        break
            if not done:
                g.sprout(rng.choice(g.open_ends()))
        elif rule == "R5":
            g.sprout(rng.choice(g.open_ends()))
            while g.n < size:
                pairs = g.local_pairs()
                cand = [p for p, d in pairs.items() if d == FLAT]
                rng.shuffle(cand)
                done = False
                for a, b in cand:
                    w = g.close(a, b)
                    if g.has_pin_or_tie():
                        g.undo_close(a, b, w)
                        continue
                    done = True
                    break
                if not done:
                    break
        if g.n in checkpoints:
            pins, _ = g.pins_and_ties(ties=False)
            trace.append({"knots": g.n, "open ends": sum(g.opens.values()), "cycle rank": g.cycle_rank(),
                          "pinned": pins})
    return g, trace


def graph_distance_from(g: KG, src: int) -> dict[int, int]:
    dist = {src: 0}
    q = collections.deque([src])
    while q:
        x = q.popleft()
        for y in g.adj[x]:
            if y not in dist:
                dist[y] = dist[x] + 1
                q.append(y)
    return dist


def profile(g: KG, targets_per_shell: int, rng: random.Random, all_targets: bool = False):
    """Exact bond distance from a distinction at the seed knot to distinctions spread over graph distance."""
    edges = g.edges()
    dist = graph_distance_from(g, 0)
    at_seed = [e for e in edges if e[1] == 0 or e[2] == 0]
    src = at_seed[0]
    by_shell = collections.defaultdict(list)
    for e in edges:
        if e is src:
            continue
        d = min(dist[e[1]], dist[e[2]] if e[2] != INF else dist[e[1]])
        by_shell[d].append(e)
    rows = []
    shells = sorted(by_shell)
    for d in shells:
        targets = by_shell[d] if all_targets else rng.sample(by_shell[d], min(targets_per_shell, len(by_shell[d])))
        for f in targets:
            rows.append((d, bond_distance(g, src, f)))
    return src, rows


def classify(rows, ball):
    finite = [b for _, b in rows if isinstance(b, int)]
    infinite = sum(1 for _, b in rows if b is None)
    far = [b for d, b in rows if d >= max(d for d, _ in rows) * 0.6]
    near = [b for d, b in rows if d <= max(d for d, _ in rows) * 0.2]
    out = {"pairs": len(rows), "no knot (infinite)": infinite, "unresolved": sum(1 for _, b in rows if b == "unresolved"),
           "largest finite bond distance": max(finite) if finite else None}
    if infinite > len(rows) * 0.2:
        out["class"] = "decoupled cells"
    elif finite and max(finite) <= 8 and len(set(d for d, _ in rows)) > 8:
        out["class"] = "collapse (bounded bond distance)"
    else:
        out["class"] = "grows (see slope and ball growth)"
    pts = [(d, b) for d, b in rows if isinstance(b, int) and d > 0]
    if len(pts) > 3:
        xs = np.array([p[0] for p in pts], float)
        ys = np.array([p[1] for p in pts], float)
        out["bond distance per graph step (least squares)"] = round(float(np.polyfit(xs, ys, 1)[0]), 3)
    if ball:
        rs = sorted(ball)
        sel = [(r, ball[r]) for r in rs if r >= 4]
        if len(sel) > 3:
            lx = np.log([r for r, _ in sel]); ly = np.log([c for _, c in sel])
            out["ball growth exponent (log count vs log radius, r >= 4)"] = round(float(np.polyfit(lx, ly, 1)[0]), 3)
    return out


def main():
    started = time.time()
    results = {"rules": {}}
    sizes = {"R1": 1000, "R2": 1000, "R3": 300, "R4": 300, "R5": 300}
    for rule in ("R2", "R1", "R3", "R4", "R5"):
        per_seed = []
        for seed in (1, 2, 3):
            rng = random.Random(seed)
            checkpoints = set(range(50, sizes[rule] + 1, 50))
            t0 = time.time()
            g, trace = grow(rule, sizes[rule], rng, checkpoints)
            entry = {"seed": seed, "knots": g.n, "trace": trace, "grow seconds": round(time.time() - t0, 1)}
            if rule in ("R3", "R4", "R5"):
                pins, ties = g.pins_and_ties(ties=True)
                entry["pinned distinctions"] = pins
                entry["tied pairs"] = ties
            if seed == 1:
                prof_graph = g
                if rule in ("R1", "R2"):
                    # a 400-knot copy for exact profiles on trees
                    rng2 = random.Random(seed)
                    prof_graph, _ = grow(rule, 400, rng2, set())
                src, rows = profile(prof_graph, 2, random.Random(11))
                ball = collections.Counter()
                for _, b in rows:
                    if isinstance(b, int):
                        ball[b] += 1
                cum, run_total = {}, 0
                for r in sorted(ball):
                    run_total += ball[r]
                    cum[r] = run_total
                entry["profile (graph distance, exact bond distance) from a seed distinction"] = rows
                entry["classification"] = classify(rows, None)
                if rule == "R2":
                    entry["control: bond distance = graph distance + 2"] = all(
                        b == d + 2 for d, b in rows if isinstance(b, int) and d > 0)
                    entry["control: knot graph is a path"] = max(len(a) for a in prof_graph.adj.values()) <= 2
            per_seed.append(entry)
            print(rule, seed, entry.get("classification", ""), entry["knots"], entry["grow seconds"], flush=True)
        results["rules"][rule] = per_seed
    # exhaustive bond-ball profiles at 200 knots (seed 1), every distinction
    balls = {}
    for rule in ("R1", "R2", "R3", "R4", "R5"):
        g, _ = grow(rule, 200, random.Random(1), set())
        src, rows = profile(g, 0, random.Random(0), all_targets=True)
        counts = collections.Counter(b for _, b in rows if isinstance(b, int))
        cum, total = {}, 0
        for r in sorted(counts):
            total += counts[r]
            cum[r] = total
        balls[rule] = {"distinctions": len(rows), "no knot (infinite)": sum(1 for _, b in rows if b is None),
                       "ball counts by bond radius": cum, "classification": classify(rows, cum)}
        print("ball", rule, balls[rule]["classification"], flush=True)
    results["bond balls at 200 knots, all distinctions"] = balls
    # control: on R3, the bond-distance program without its outside-connectivity constraint
    g, _ = grow("R3", 200, random.Random(1), set())
    src, rows = profile(g, 1, random.Random(5))
    edges = g.edges()
    dist = graph_distance_from(g, 0)
    far = [e for e in edges if min(dist[e[1]], dist.get(e[2], dist[e[1]]) if e[2] != INF else dist[e[1]]) > 20][:5]
    pairs = [(bond_distance(g, src, f), bond_distance(g, src, f, outside_connected=False)) for f in far]
    results["control: R3 at 200 knots, far targets (constrained, unconstrained)"] = {
        "pairs": pairs, "constrained none while unconstrained finite": any(a is None and b is not None for a, b in pairs)}
    results["runtime seconds"] = round(time.time() - started, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(results, indent=1, default=str) + "\n")
    print("done", results["runtime seconds"])


if __name__ == "__main__":
    main()
