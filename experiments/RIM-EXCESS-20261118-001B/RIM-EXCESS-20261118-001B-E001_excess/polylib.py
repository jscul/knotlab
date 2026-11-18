"""Bond distance of one pair of a weave disc from the cyclic criterion (RIM-EXCESS-20261118-001B), no state enumeration.

Proposition 3 of WEAVE-HEIGHTS-20261118-001A: a set is constrained exactly when m >= 3 of its members have a cyclic order of D-sum at
most 3(m - 2). Lemma P (ticket A): a bond's tight cyclic order has D-sum exactly 3(m - 2), every member on a D-geodesic between its
neighbours. Lemma C: every member of a least bond holding x, z with excess e lies within detour 3e of one of the arcs."""
import itertools
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/DOUBLE-MEET-20261118-001B/DOUBLE-MEET-20261118-001B-E001_patches"))
import weavelib as W  # noqa: E402

nx = W.nx
def tight_subset_exists(pts, DD, exclude_full=True):
    """Is there a sub-collection R of pts (|R| >= 3, R != pts if exclude_full) with a cyclic order of D-sum <= 3(|R|-2)?"""
    n = len(pts); Wm = [[DD[pts[a]][pts[b]] for b in range(n)] for a in range(n)]
    full = (1 << n) - 1
    for s in range(n):
        dp = {(1 << s, s): 0}
        for mask in range(1 << n):
            if not (mask >> s) & 1 or mask & ((1 << s) - 1): continue
            for last in range(n):
                c = dp.get((mask, last))
                if c is None: continue
                k = bin(mask).count("1")
                if k >= 3 and c + Wm[last][s] <= 3 * (k - 2) and not (exclude_full and mask == full):
                    return True
                for nx_ in range(s + 1, n):
                    if not (mask >> nx_) & 1:
                        key = (mask | (1 << nx_), nx_); v = c + Wm[last][nx_]
                        if v < dp.get(key, 10**9): dp[key] = v
    return False
def is_bond(pts, DD):
    # tight with all points, and no tight proper sub-collection
    n = len(pts)
    # Hamiltonian tight cycle: min over cyclic orders of D-sum <= 3(n-2)
    Wm = [[DD[pts[a]][pts[b]] for b in range(n)] for a in range(n)]
    full = (1 << n) - 1
    dp = {(1, 0): 0}
    best = 10**9
    for mask in range(1, 1 << n, 2):
        for last in range(n):
            c = dp.get((mask, last))
            if c is None: continue
            if mask == full: best = min(best, c + Wm[last][0]); continue
            for nx_ in range(1, n):
                if not (mask >> nx_) & 1:
                    key = (mask | (1 << nx_), nx_); v = c + Wm[last][nx_]
                    if v < dp.get(key, 10**9): dp[key] = v
    if best > 3 * (n - 2): return False
    return not tight_subset_exists(pts, DD, exclude_full=True)
def min_cycle_weight(pts, DD):
    """Least D-sum over cyclic orders of all of pts (Held-Karp)."""
    n = len(pts)
    Wm = [[DD[pts[a]][pts[b]] for b in range(n)] for a in range(n)]
    full = (1 << n) - 1
    dp = {(1, 0): 0}
    best = 10**9
    for mask in range(1, 1 << n, 2):
        for last in range(n):
            c = dp.get((mask, last))
            if c is None:
                continue
            if mask == full:
                best = min(best, c + Wm[last][0])
                continue
            for nx_ in range(1, n):
                if not (mask >> nx_) & 1:
                    key = (mask | (1 << nx_), nx_)
                    v = c + Wm[last][nx_]
                    if v < dp.get(key, 10**9):
                        dp[key] = v
    return best


def pair_b_crit(T, x, z, emax=4):
    V = sorted({v for t in T for v in W.verts(t)})
    DD = W.height_distances(T)
    G = nx.Graph(); G.add_edges_from(tuple(sorted(e)) for t in T for e in itertools.combinations(W.verts(t), 2))
    s = nx.shortest_path_length(G, x, z)
    for e in range(0, emax + 1):
        m = s + 2 + e
        cand = [p for p in V if p not in (x, z) and min(DD[x][p] + DD[p][z] - DD[x][z], DD[z][p] + DD[p][x] - DD[z][x]) <= 3 * e]
        if len(cand) < m - 2: continue
        # enumerate sets; prune by requiring a tight Hamiltonian cycle first
        for extra in itertools.combinations(cand, m - 2):
            pts = [x, z] + list(extra)
            if is_bond(pts, DD):
                return m - 1, s
    return None, s


def pair_b_polygons(T, x, z, emax=4, time_limit=60.0):
    """Least bond through x, z found by enumerating geodesic polygons: cyclic sequences through x and z of m = s + 2 + e distinct
    distinctions with D-sum exactly 3(m - 2) and every member on a D-geodesic between its neighbours (the bond-polygon lemma), then
    keeping those with no tight proper sub-collection."""
    import time as _t
    t0 = _t.time()
    V = sorted({v for t in T for v in W.verts(t)})
    DD = W.height_distances(T)
    G = nx.Graph(); G.add_edges_from(tuple(sorted(e)) for t in T for e in itertools.combinations(W.verts(t), 2))
    s = nx.shortest_path_length(G, x, z)
    for e in range(0, emax + 1):
        m = s + 2 + e
        budget = 3 * (m - 2)
        cand = [p for p in V if p not in (x, z) and min(DD[x][p] + DD[p][z] - DD[x][z], DD[z][p] + DD[p][x] - DD[z][x]) <= 3 * e]
        seen = set()
        found = [None]
        def dfs(seq, w, has_z):
            if found[0] is not None or _t.time() - t0 > time_limit:
                return
            last = seq[-1]
            if len(seq) == m:
                if not has_z: return
                tot = w + DD[last][x]
                if tot != budget: return
                if DD[seq[-2]][last] + DD[last][x] != DD[seq[-2]][x]: return
                if DD[last][x] + DD[x][seq[1]] != DD[last][seq[1]]: return
                key = frozenset(seq)
                if key in seen: return
                seen.add(key)
                if not tight_subset_exists(list(key), DD, exclude_full=True):
                    found[0] = key
                return
            pool = ([z] if not has_z else []) + [p for p in cand if p not in seq]
            for q in pool:
                w2 = w + DD[last][q]
                rest = (DD[q][z] + DD[z][x]) if (not has_z and q != z) else DD[q][x]
                if w2 + rest > budget: continue
                if len(seq) >= 2 and DD[seq[-2]][last] + DD[last][q] != DD[seq[-2]][q]: continue
                dfs(seq + [q], w2, has_z or q == z)
        dfs([x], 0, False)
        if found[0] is not None:
            return m - 1, s, False
        if _t.time() - t0 > time_limit:
            return None, s, True
    return None, s, False
