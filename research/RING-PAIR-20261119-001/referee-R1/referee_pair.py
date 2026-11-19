"""Referee R1 for RING-PAIR-20261119-001 (own code; covermodel.py, fresh.py and the study's growth are not imported).

  ../../../.venv/bin/python -B referee_pair.py <part> [args] > referee_pair_<part>.json      (from this directory)

The model as the study states it: the candidate complex of a start has a vertex per knot and, for every knot w with two or more
neighbours, a block (full simplex) on the neighbours N(w); every listed surplus distinction at knot r adds a vertex joined to r
alone.  Its universal cover is a tree of blocks.  Rule: the junctions of round t are the deck orbits of the connected vertex sets
of t + 1 vertices of the cover that contain a knot.

Three independent counts of those orbits:
  rooted     the referee's rooted series, from U(B, z) = y prod over the other blocks B' at z of prod over w in B' - z of
             (1 + U(B', w)) and R_x = y prod over blocks at x of prod over w in B - x of (1 + U(B, w)), then the orbit count
             c(t) = [y^(t+1)] sum_x R_x / (t + 1) (the deck group acts freely on finite sets of a tree, so each orbit of sets of
             size s is met s times);
  dissym     the dissymmetry count (vertices less vertex-block incidences plus blocks, which is 1 on a finite subtree), written
             here from that identity: c(t) = [y^(t+1)] (sum_x R_x - sum_B sum_{S in B, |S| >= 2} (|S| - 1) prod_{v in S} U(B, v));
  brute      an explicit enumeration (Redelmeier) of connected vertex sets containing a root, in the cover built lazily as
             non-backtracking walks of the vertex-block incidence graph, to a given size: the rooted counts.

Parts:
  check NAME N        the three counts against one another (brute to size N) and against the growth's counts: the referee's own
                      growth where it has one (JOIN-GROWTH-R1's C-5-9-D to round 17) and the recorded counts.
  exponent NAME T     T terms of the orbit count: the rate, and the local exponent alpha(t) from three consecutive terms.
  fresh               the study's 17 fresh starts and 3 out-of-scope starts: the scope conditions computed by the referee, and the
                      referee's model against the study's grown counts.
"""
import itertools
import json
import math
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def ring(n, off=0):
    return [(off + i, off + (i + 1) % n) for i in range(n)]


def start(name):
    """Two-ring starts as JOIN-GROWTH's job.two_rings builds them (written here from its description)."""
    if name == "C-5-9-D":
        return 14, ring(5) + ring(9, 5) + [(0, 5)], {}
    if name == "C-5-7-D":
        return 12, ring(5) + ring(7, 5) + [(0, 5)], {}
    if name == "C-7-7-D":
        return 14, ring(7) + ring(7, 7) + [(0, 7)], {}
    if name == "C-5-5-P1":
        return 11, ring(5) + ring(5, 5) + [(0, 10), (10, 5)], {}
    if name == "C-5-5-K":   # a shared knot: the second ring's knot 0 is the first ring's knot 0
        return 9, ring(5) + [(0, 5), (5, 6), (6, 7), (7, 8), (8, 0)], {}
    raise KeyError(name)


def blocks(n, edges, surplus):
    nb = defaultdict(set)
    for a, b in edges:
        nb[a].add(b)
        nb[b].add(a)
    B = [tuple(sorted(nb[w])) for w in range(n) if len(nb[w]) >= 2]
    k = n
    for r, v in sorted(surplus.items()):
        for _ in range(v):
            B.append((r, k))
            k += 1
    return k, B


def mul(a, b, N):
    out = [0] * (N + 1)
    for i, x in enumerate(a):
        if x:
            bi = b[:N + 1 - i]
            for j, y in enumerate(bi):
                if y:
                    out[i + j] += x * y
    return out


def rooted_system(nv, B, N):
    at = defaultdict(list)
    for i, blk in enumerate(B):
        for z in blk:
            at[z].append(i)
    one = [1] + [0] * N
    U = {(i, z): [0] * (N + 1) for i, blk in enumerate(B) for z in blk}
    for _ in range(N + 2):
        new = {}
        for (i, z) in U:
            r = one
            for j in at[z]:
                if j == i:
                    continue
                for w in B[j]:
                    if w != z:
                        r = mul(r, [1 + U[(j, w)][0]] + U[(j, w)][1:], N)
            new[(i, z)] = [0] + r[:N]
        if new == U:
            break
        U = new
    R = {}
    for x in range(nv):
        r = one
        for j in at[x]:
            for w in B[j]:
                if w != x:
                    r = mul(r, [1 + U[(j, w)][0]] + U[(j, w)][1:], N)
        R[x] = [0] + r[:N]
    return U, R


def orbit_counts(n, edges, surplus, N):
    nv, B = blocks(n, edges, surplus)
    U, R = rooted_system(nv, B, N)
    tot = [sum(R[x][k] for x in R) for k in range(N + 1)]
    rooted = []
    for k in range(1, N + 1):
        q = Fraction(tot[k], k)
        rooted.append(q)
    d = list(tot)
    for i, blk in enumerate(B):
        for m in range(2, len(blk) + 1):
            for S in itertools.combinations(blk, m):
                pr = [1] + [0] * N
                for v in S:
                    pr = mul(pr, U[(i, v)], N)
                d = [a - (m - 1) * b for a, b in zip(d, pr)]
    dissym = d[1:]
    rooted[0] -= nv - n          # surplus-only singletons are not junctions
    dissym[0] -= nv - n
    return rooted, dissym, tot, nv, B


def brute_rooted(nv, B, Nmax):
    """Rooted counts (sets containing the root lift of x, of size 1..Nmax), summed over x, by Redelmeier enumeration in the cover.
    A cover vertex is a tuple (x, parent cover vertex, block index it was entered through); its neighbours are the other vertices of
    its entry block instance (shared with the parent) and new vertices in each other block at x."""
    at = defaultdict(list)
    for i, blk in enumerate(B):
        for z in blk:
            at[z].append(i)
    total = [0] * (Nmax + 1)
    for x0 in range(nv):
        root = ("r", x0)
        base = {root: x0}
        entry = {root: None}
        parent = {root: None}
        cache = {}

        def nbrs(v):
            if v in cache:
                return cache[v]
            x = base[v]
            out = []
            for j in at[x]:
                if entry[v] == j:
                    # the instance of block j shared with the parent: the parent and its siblings
                    p = parent[v]
                    for w in B[j]:
                        if w == base[p]:
                            out.append(p)
                        elif w != x:
                            u = (p, j, w)
                            base.setdefault(u, w)
                            entry.setdefault(u, j)
                            parent.setdefault(u, p)
                            out.append(u)
                else:
                    for w in B[j]:
                        if w != x:
                            u = (v, j, w)
                            base.setdefault(u, w)
                            entry.setdefault(u, j)
                            parent.setdefault(u, v)
                            out.append(u)
            cache[v] = out
            return out

        def rec(untried, size, seen):
            total[size] += 1
            if size == Nmax:
                return
            untried = list(untried)
            while untried:
                v = untried.pop()
                new = [w for w in nbrs(v) if w not in seen]
                for w in new:
                    seen.add(w)
                rec(untried + new, size + 1, seen)
                for w in new:
                    seen.discard(w)
        seen = {root}
        for w in nbrs(root):
            seen.add(w)
        rec(list(nbrs(root)), 1, seen)
    return total


def part_check(name, N):
    n, edges, surplus = start(name)
    rooted, dissym, tot, nv, B = orbit_counts(n, edges, surplus, 40)
    br = brute_rooted(nv, B, N)
    out = {"start": name, "vertices": nv, "blocks": [list(b) for b in B],
           "rooted count equals dissymmetry count (40 terms)": all(r == d for r, d in zip(rooted, dissym)),
           "rooted count always an integer (40 terms)": all(r.denominator == 1 for r in rooted),
           "brute-force rooted totals equal the rooted series, sizes 1..N": br[1:] == tot[1:N + 1],
           "orbit counts (rounds 0..)": [int(x) for x in rooted[:30]]}
    gj = HERE.parents[1] / "JOIN-GROWTH-20261118-001/referee-R1" / f"referee_join_tworing_{name}.json"
    if gj.exists():
        g = json.load(open(gj))["counts"]
        out["the referee's own growth (rounds 0..)"] = g
        out["model equals the referee's growth on every round grown"] = [int(x) for x in rooted[:len(g)]] == g
    res = json.load(open(ROOT / "artifacts/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins/results.json"))["cases"].get(name)
    if res:
        out["model equals JOIN-GROWTH's recorded counts"] = [int(x) for x in rooted[:len(res["counts"])]] == res["counts"]
    return out


def rooted_float(nv, B, N, scale):
    """The rooted totals sum_x R_x as floats, for coefficients y^0..y^N of the series in z = y / scale (so they stay O(1))."""
    import numpy as np
    at = defaultdict(list)
    for i, blk in enumerate(B):
        for z in blk:
            at[z].append(i)
    one = np.zeros(N + 1)
    one[0] = 1.0

    def mulf(a, b):
        return np.convolve(a, b)[:N + 1]
    U = {(i, z): np.zeros(N + 1) for i, blk in enumerate(B) for z in blk}
    for it in range(N + 2):
        new = {}
        for (i, z) in U:
            r = one
            for j in at[z]:
                if j == i:
                    continue
                for w in B[j]:
                    if w != z:
                        r = mulf(r, one + U[(j, w)])
            v = np.zeros(N + 1)
            v[1:] = r[:N] * scale
            new[(i, z)] = v
        done = all(np.allclose(new[k], U[k], rtol=0, atol=0) for k in U)
        U = new
        if done:
            break
    tot = np.zeros(N + 1)
    for x in range(nv):
        r = one
        for j in at[x]:
            for w in B[j]:
                if w != x:
                    r = mulf(r, one + U[(j, w)])
        v = np.zeros(N + 1)
        v[1:] = r[:N] * scale
        tot += v
    return tot


def part_exponent(name, T):
    n, edges, surplus = start(name)
    nv, B = blocks(n, edges, surplus)
    rooted, dissym, tot_exact, _, _ = orbit_counts(n, edges, surplus, 30)
    lam0 = rooted[29] / rooted[28]
    scale = float(1 / lam0)                      # coefficients of z^k are counts times scale^k
    tot = rooted_float(nv, B, T + 2, scale)
    # orbit counts in scaled form: c(t) scale^(t+1) = tot[t+1] / (t+1)
    cs = [tot[k + 1] / (k + 1) for k in range(T + 1)]
    check = all(abs(cs[k] / (float(rooted[k] + (nv - n if k == 0 else 0)) * scale ** (k + 1)) - 1) < 1e-9 for k in range(1, 29))
    rows = []
    for t in (10, 12, 14, 16, 17, 20, 25, 30, 40, 50, 75, 100, 150, 200, 300, 400, 600, T - 1):
        if 6 <= t < T:
            r1, r2 = cs[t] / cs[t - 1], cs[t + 1] / cs[t]
            q = math.log((t / (t + 1)) / ((t - 1) / t))
            rows.append({"t": t, "local alpha": round(-math.log(r2 / r1) / q, 4)})
    t = T - 1
    ratio = cs[t + 1] / cs[t] / scale
    return {"start": name, "terms": T + 1, "float series agrees with the exact one on terms 1..28": check,
            "local exponents alpha(t) from terms t - 1, t, t + 1": rows,
            "rate with alpha = -5/2 from the last two terms": round(ratio * ((t + 1) / t) ** 2.5, 6),
            "rate with alpha = -3/2 from the last two terms": round(ratio * ((t + 1) / t) ** 1.5, 6),
            "last ratio": round(ratio, 6)}


# ---------------------------------------------------------------- the 17 fresh starts and the scope

def R(n, off=0):
    return ring(n, off)


FRESH = {   # copied as data from the study's fresh.py (edge lists and surplus counts)
    "F01-5-5-P2": (12, R(5) + R(5, 5) + [(0, 10), (10, 11), (11, 5)], {}),
    "F02-5-7-K": (11, R(5) + [(0, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 0)], {}),
    "F03-5-7-P1": (13, R(5) + R(7, 5) + [(0, 12), (12, 5)], {}),
    "F04-chain3-57": (15, R(5) + R(5, 5) + R(5, 10) + [(0, 5), (7, 10)], {}),
    "F05-chain3-56": (15, R(5) + R(5, 5) + R(5, 10) + [(0, 5), (6, 10)], {}),
    "F06-three-K": (13, R(5) + [(0, 5), (5, 6), (6, 7), (7, 8), (8, 0)] + [(0, 9), (9, 10), (10, 11), (11, 12), (12, 0)], {}),
    "F07-7-7-DD": (14, R(7) + R(7, 7) + [(0, 7), (3, 10)], {}),
    "F08-5-5-D-s2s8": (10, R(5) + R(5, 5) + [(0, 5)], {2: 1, 8: 1}),
    "F09-9-5-K": (13, R(9) + [(0, 9), (9, 10), (10, 11), (11, 12), (12, 0)], {}),
    "F10-theta-P4": (9, R(5) + [(0, 5), (5, 6), (6, 7), (7, 8), (8, 2)], {}),
    "F11-5L-7-D": (13, R(5) + R(7, 5) + [(2, 12), (0, 5)], {12: 2}),
    "F12-7-7-P1": (15, R(7) + R(7, 7) + [(0, 14), (14, 7)], {}),
    "F13-bouquet": (16, R(5) + R(5, 5) + R(5, 10) + [(0, 15), (5, 15), (10, 15)], {}),
    "F14-n9-control": (11, R(9) + [(0, 9), (4, 10)], {9: 2, 10: 3, 6: 1}),
    "F15-5-5-two-paths": (12, R(5) + R(5, 5) + [(0, 10), (10, 5), (2, 11), (11, 7)], {}),
    "F16-ring8-four-lone": (12, R(8) + [(1, 8), (3, 9), (5, 10), (7, 11)], {}),
    "F17-5-5-K-path3": (12, R(5) + [(0, 5), (5, 6), (6, 7), (7, 8), (8, 0)] + [(2, 9), (9, 10), (10, 11), (11, 6)], {}),
    "X01-5-5-DD-0-5-2-7": (10, R(5) + R(5, 5) + [(0, 5), (2, 7)], {}),
    "X02-theta-P2": (7, R(5) + [(0, 5), (5, 6), (6, 2)], {}),
    "X03-ring7-chord-P2": (9, R(7) + [(0, 7), (7, 8), (8, 3)], {}),
}


def scope(n, edges, surplus):
    """The four scope conditions, computed by the referee: round-1 groups from the candidate relation (two knots with a common
    neighbour), valid sets of three or more pairwise candidates with no common neighbour, the rest pairs."""
    nb = defaultdict(set)
    for a, b in edges:
        nb[a].add(b)
        nb[b].add(a)
    cand = {(a, b) for a, b in itertools.combinations(range(n), 2) if nb[a] & nb[b]}
    triples = [T for T in itertools.combinations(range(n), 3) if all(p in cand for p in itertools.combinations(T, 2))
               and not (nb[T[0]] & nb[T[1]] & nb[T[2]])]
    demand = defaultdict(int)
    for a, b in cand:
        demand[a] += 1
        demand[b] += 1
    shared = {k: len([e for e in edges if k in e]) for k in range(n)}
    two_common = [(a, b) for a, b in itertools.combinations(range(n), 2) if len(nb[a] & nb[b]) >= 2]
    return {"a knot with shared + round-1 demand below 3": [k for k in range(n) if shared[k] + demand[k] < 3],
            "surplus at a knot of demand below 2": [k for k in surplus if demand[k] < 2],
            "a group of three or more in round 1": len(triples) > 0,
            "two knots with two common neighbours": two_common,
            "in scope": not any(shared[k] + demand[k] < 3 for k in range(n)) and not any(demand[k] < 2 for k in surplus)
                        and not triples and not two_common}


def part_fresh():
    sys.path.insert(0, str(ROOT / "scripts"))
    from longrun import load_results
    recs = load_results(str(ROOT / "runs/ring-pair"))
    for cid, rec in load_results(str(ROOT / "runs/ring-pair-mem")).items():
        if rec.get("status") == "ok" and (recs.get(cid) or {}).get("status") != "ok":
            recs[cid] = rec
    out = {}
    for name, (n, edges, surplus) in FRESH.items():
        sc = scope(n, edges, surplus)
        r = recs[name]["result"]
        row = {"scope (referee)": sc["in scope"], "scope (study)": r["in_scope"], "rounds grown by the study": r["rounds"]}
        if not sc["in scope"]:
            row["why (referee)"] = {k: v for k, v in sc.items() if v and k != "in scope"}
        if sc["in scope"]:
            rooted, dissym, tot, nv, B = orbit_counts(n, edges, surplus, len(r["counts"]) + 1)
            row["referee's model equals the study's grown counts"] = [int(x) for x in rooted[:len(r["counts"])]] == r["counts"]
            row["rooted equals dissymmetry"] = all(a == b for a, b in zip(rooted, dissym))
        out[name] = row
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    if part == "check":
        print(json.dumps(part_check(sys.argv[2], int(sys.argv[3])), indent=1, default=str))
    elif part == "fresh":
        print(json.dumps(part_fresh(), indent=1, default=str))
    else:
        print(json.dumps(part_exponent(sys.argv[2], int(sys.argv[3])), indent=1, default=str))
