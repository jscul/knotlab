"""Referee R1 for RING-READ-20261118-001 (own code; the study's ringread.py, reader3.py and check.py are not imported).

  ../../../.venv/bin/python -B referee_ringread.py <part> [rounds] > referee_ringread_<part>.json      (from this directory)

The ring of four four-place knots and one five-place knot is grown under the fewest rule by the referee's own engine (FIRST-KNOT-R1
and FRESH-COUNT-R1 referee code: the complete-round joining rule, GF(2) implied parity).  The junction graph: junctions, one
outside vertex o, a shared distinction joining its two holders, a loose one joining its holder to o.  A bond is a cut delta(J),
o not in J, with J and its complement (with o) connected; K = bond size, D = K - 1.

Parts:
  shape    rounds T: junctions, distinctions, junction sizes per round (against the study's table), 3-connectivity of the junction
           graph with o (networkx node connectivity), and the history-free step: the junction supports alone, regrown one round,
           against the true next round.
  large T  completeness of the table for bonds with two large sides, by an exact search: every bond of at most L distinctions
           (L = largest junction + 1, one past what the table must hold exactly) is found, whatever the size of either side,
           by include/exclude branching over connected J grown from a least root, pruned by a max-flow lower bound (no J'
           containing J and avoiding the excluded vertices has a smaller cut than the max-flow from J to them and o).  Reported:
           the bonds with an inner side of seven or more junctions (the table's enumeration stops at six to eight), the bonds
           by inner side size, and, as a control on the search, its count of bonds with sides of at most six against a direct
           enumeration of connected sides of at most six.
"""
import itertools
import json
import sys
from collections import Counter, defaultdict, deque
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/FIRST-KNOT-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/TOUCH-CENSUS-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/RING-GROWTH-20261118-001/referee-R1"))
import referee_first as RFK  # noqa: E402
import referee_touch as RT  # noqa: E402
import referee_ring as RR  # noqa: E402


def grow(T):
    sizes, M = RR.ring([4, 4, 4, 4, 5])
    G = RFK.Start(RT.stars(sizes, M))
    for _ in range(T):
        assert G.step(RFK.fewest, None, None) == "ok"
    return G


def graph(stars):
    n = len(stars)
    own = defaultdict(list)
    for j, S in enumerate(stars):
        for b in S:
            own[b].append(j)
    cap = defaultdict(int)
    for b, js in own.items():
        u, v = (js[0], js[1]) if len(js) == 2 else (js[0], n)
        cap[(u, v)] += 1
        cap[(v, u)] += 1
    adj = defaultdict(dict)
    for (u, v), c in cap.items():
        adj[u][v] = c
    return n, adj, own


def maxflow_exceeds(adj, n, J, X, L):
    """Is the max flow from the vertex set J to X + {o} more than L?  (Unit-ish capacities; stops at L + 1.)"""
    flow = defaultdict(int)
    sink = X | {n}
    total = 0
    while total <= L:
        prev = {}
        dq = deque()
        for s in J:
            prev[s] = None
            dq.append(s)
        hit = None
        while dq and hit is None:
            u = dq.popleft()
            for v, c in adj[u].items():
                if v in prev or c - flow[(u, v)] <= 0:
                    continue
                prev[v] = u
                if v in sink:
                    hit = v
                    break
                dq.append(v)
        if hit is None:
            return False
        v = hit
        while prev[v] is not None:
            u = prev[v]
            flow[(u, v)] += 1
            flow[(v, u)] -= 1
            v = u
        total += 1
    return True


def cut_size(adj, J):
    return sum(c for u in J for v, c in adj[u].items() if v not in J)


def complement_connected(adj, n, J):
    seen = {n}
    stack = [n]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in J and y not in seen:
                seen.add(y)
                stack.append(y)
    return len(seen) + len(J) == n + 1


def search_root(args):
    adj, n, r, L, minside, Lkeep, masks = args
    keep = []
    found = []
    small = Counter()
    nodes = 0

    def go(J, X):
        nonlocal nodes
        nodes += 1
        if maxflow_exceeds(adj, n, J, X, L):
            return
        front = {v for u in J for v in adj[u] if v != n and v not in J and v not in X}
        if not front:
            c = cut_size(adj, J)
            if c <= L and complement_connected(adj, n, J):
                if len(J) >= minside:
                    found.append((sorted(J), c))
                small[(len(J), c)] += 1
                if c <= Lkeep:
                    w = 0
                    for u in J:
                        w ^= masks[u]
                    keep.append((len(J), w))
            return
        w = max(front, key=lambda v: (sum(1 for u in adj[v] if u in J), -v))
        go(J | {w}, X)
        go(J, X | {w})
    go(frozenset([r]), frozenset(range(r)))
    return found, small, nodes, keep


def direct_small(adj, n, L, m=6):
    """Bonds of at most L distinctions whose inner side has at most m junctions, by direct enumeration of connected sets."""
    out = Counter()
    seen = set()
    for r in range(n):
        stack = [frozenset([r])]
        while stack:
            J = stack.pop()
            if J in seen:
                continue
            seen.add(J)
            c = cut_size(adj, J)
            if c <= L and complement_connected(adj, n, J):
                out[(len(J), c)] += 1
            if len(J) < m:
                for u in J:
                    for v in adj[u]:
                        if v != n and v > r and v not in J:
                            stack.append(J | {v})
    return out


def part_large(T, extra=4):
    G = grow(T)
    stars = [frozenset(b) for b in G.bits]
    masks = [sum(1 << b for b in S) for S in stars]
    n, adj, own = graph(stars)
    big = max(map(len, stars))
    L = big + 1
    Lmax = L + extra
    adjd = {u: dict(v) for u, v in adj.items()}
    with Pool(20) as pool:
        res = pool.map(search_root, [(adjd, n, r, Lmax, 7, L, masks) for r in range(n)], chunksize=1)
    found = [f for fs, _, _, _ in res for f in fs]
    small = Counter()
    for _, s_, _, _ in res:
        small.update(s_)
    keep = [k for _, _, _, ks in res for k in ks]
    # the exact table through K = L from every bond found, against the tables from inner sides of at most 6 and at most 7

    def table(maxside):
        t = {}
        for side, w in keep:
            if side > maxside:
                continue
            bits = [b for b in range(w.bit_length()) if w >> b & 1]
            c = len(bits)
            for p in itertools.combinations(bits, 2):
                if t.get(p, 99) > c:
                    t[p] = c
        return t
    exact, t6, t7 = table(10 ** 9), table(6), table(7)
    diff6 = Counter(exact[p] for p in exact if t6.get(p, 99) != exact[p])
    diff7 = Counter(exact[p] for p in exact if t7.get(p, 99) != exact[p])
    direct = direct_small(adjd, n, L)
    search6 = Counter({k: v for k, v in small.items() if k[0] <= 6 and k[1] <= L})
    sizes_large = Counter(c for _, c in found)
    return {"T": T, "junctions": n, "distinctions": len(own), "largest junction": big,
            "L = largest junction + 1": L, "searched up to": Lmax, "search nodes": sum(x for _, _, x, _ in res),
            "bonds of at most L distinctions with an inner side of 7 or more junctions": sum(v for c, v in sizes_large.items() if c <= L),
            "bonds of at most Lmax with an inner side of 7 or more, by size": dict(sorted(sizes_large.items())),
            "smallest bond with an inner side of 7 or more (if at most Lmax)": min(sizes_large) if sizes_large else None,
            "largest inner side among bonds of at most L": max((k[0] for k in small if k[1] <= L), default=None),
            "bonds of at most L by inner side size": dict(sorted(Counter(k[0] for k in small.elements() if k[1] <= L).items())),
            "pairs with K <= L (exact)": len(exact),
            "exact D histogram through D = L - 1": dict(sorted(Counter(k - 1 for k in exact.values()).items())),
            "pairs whose K <= L is missed by sides of at most 6, by exact K": dict(sorted(diff6.items())),
            "pairs whose K <= L is missed by sides of at most 7, by exact K": dict(sorted(diff7.items())),
            "control: search's bonds of at most L with sides <= 6 equal direct enumeration": search6 == direct,
            "bonds of at most L with sides <= 6 (direct)": sum(direct.values())}


def part_shape(rounds):
    out = []
    for T in rounds:
        G = grow(T + 1)
        cut = [j for j in range(len(G.bits)) if G.round[j] <= T]
        # the presentation at round T: junctions of rounds <= T with their supports as they stood then
        stars_T = []
        for j in cut:
            stars_T.append([b for b in G.bits[j]])
        own_T = defaultdict(list)
        for j, S in enumerate(stars_T):
            for b in S:
                own_T[b].append(j)
        n = len(stars_T)
        H = nx.Graph()
        H.add_nodes_from(range(n + 1))
        for b, js in own_T.items():
            H.add_edge(js[0], js[1] if len(js) == 2 else n)
        conn = nx.node_connectivity(H)
        # the history-free step: a fresh presentation from the round-T supports alone, one round under the fewest rule
        R = RFK.Start(stars_T)
        assert R.step(RFK.fewest, None, None) == "ok"
        new_read = Counter((tuple(sorted(b for b in R.bits[j] if b in own_T)), sum(1 for b in R.bits[j] if b not in own_T))
                           for j in range(n, len(R.bits)))
        new_true = Counter((tuple(sorted(b for b in G.bits[j] if b in own_T)), sum(1 for b in G.bits[j] if b not in own_T))
                           for j in range(len(G.bits)) if G.round[j] == T + 1)
        out.append({"T": T, "junctions": n, "distinctions": len(own_T),
                    "junction sizes": dict(sorted(Counter(map(len, stars_T)).items())),
                    "vertex connectivity of the junction graph with o": conn,
                    "regrown round from the supports alone equals the true next round": new_read == new_true,
                    "next-round junctions": sum(new_true.values())})
        print(json.dumps(out[-1]), file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    if part == "shape":
        print(json.dumps(part_shape([int(a) for a in sys.argv[2:]]), indent=1))
    else:
        print(json.dumps(part_large(int(sys.argv[2])), indent=1, default=str))
