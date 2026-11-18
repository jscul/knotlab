"""Referee R1 for CUMULANT-DIST-20261118-001 (own code; the study's cumlib.py, run.py and score.py are not imported).

  ../../../.venv/bin/python -B referee_cumulant.py <part> [args] > referee_cumulant_<part>.json      (from this directory)

The distance, from the note: delta(x, y) = min over sets S of distinctions holding x and y, with kappa_S != 0, of
(|S| - 2) + max(0, -log_3 |kappa_S|); spins s = (-1)^value under the uniform weighting of the allowed states (or a given weighting);
kappa_S the joint cumulant, here by the partition formula kappa_S = sum over set partitions pi of S of (-1)^(|pi| - 1) (|pi| - 1)!
prod_B m_B (not the study's recursion).  A search over sets of size s may stop once s - 2 >= the best value found.

Parts:
  linear     300 random parity bases (6 to 9 distinctions, 2 to 6 knots; the referee's seed): delta against the least circuit
             through the pair minus 2 (circuits by the referee's own dual-code enumeration); and the triangle inequality.
  trees      every knot tree (each new knot shares one distinction with the earlier ones) to five knots under every assignment of
             parity and not-all-equal, and to six under one law: delta against steps apart, every pair; sets searched to the
             proved upper bound (steps apart: a set of size s can improve it only when s <= steps + 1).
  trees7     one size past: every knot tree of seven knots under pure parity and pure not-all-equal.
  weave      the weave patch of radius 2 (the study's) and of radius 3: correlations and delta (sets to six at radius 2, to four
             at radius 3, exact below delta 4) on the pairs two steps apart along the rows through the centre.
  weave3 <i> <m>  shard i of m: on the radius-3 patch, every pair with tau > 2 (the only ones a set of four can shortcut),
             searched over every set of four (exact where delta < 4); the pair's radius from the centre is recorded.
  chain      the chain grid on a 4 x 4 patch with its loose distinctions kept (one not-all-equal knot per neighbouring pair):
             delta between grid distinctions with sets of up to four drawn from all 40 distinctions, against tau.
  split      the split line of eight: delta on every pair, and the switching rotation.
"""
import functools
import itertools
import json
import math
import random
import sys
from multiprocessing import Pool

import networkx as nx
import numpy as np


# ---------------- states, moments, cumulants ----------------

def states(n, knots):
    """Allowed states of knots (law, (a, b, c)): P parity (sum even), N not-all-equal, B betweenness (b between a and c).
    Built distinction by distinction, each knot checked once all three of its distinctions are set."""
    by_last = {}
    for law, k in knots:
        by_last.setdefault(max(k), []).append((law, k))
    P = np.zeros(1, dtype=np.int64)
    for v in range(n):
        P = np.concatenate([P, P | (1 << v)])
        for law, (a, b, c) in by_last.get(v, []):
            x, y, z = (P >> a) & 1, (P >> b) & 1, (P >> c) & 1
            if law == "P":
                ok = (x + y + z) % 2 == 0
            elif law == "N":
                ok = ~((x == y) & (y == z))
            else:
                ok = ~((x == z) & (x != y))
            P = P[ok]
    return P


@functools.lru_cache(maxsize=None)
def set_partitions(m):
    def rec(items):
        if not items:
            yield []
            return
        f, rest = items[0], items[1:]
        for p in rec(rest):
            yield [(f,)] + p
            for i in range(len(p)):
                yield p[:i] + [(f,) + p[i]] + p[i + 1:]
    out = []
    for p in rec(tuple(range(m))):
        b = len(p)
        out.append(((-1) ** (b - 1) * math.factorial(b - 1), [tuple(sorted(x)) for x in p]))
    return out


class Base:
    def __init__(self, st, n, w=None):
        self.st = np.asarray(st, dtype=np.int64)
        self.n = n
        self.w = None if w is None else np.asarray(w, dtype=float) / np.sum(w)
        self.mom = {(): 1.0}
        self.cum = {}

    def m(self, S):
        S = tuple(sorted(S))
        if S not in self.mom:
            par = np.bitwise_count(self.st & sum(1 << v for v in S)) & 1          # the product of the spins is (-1)^par
            v = float(1.0 - 2.0 * par.mean()) if self.w is None else float(self.w @ (1.0 - 2.0 * par))
            self.mom[S] = 0.0 if abs(v) < 1e-13 else v
        return self.mom[S]

    def k(self, S):
        S = tuple(sorted(S))
        if S not in self.cum:
            tot = 0.0
            for coef, blocks in set_partitions(len(S)):
                p = coef
                for b in blocks:
                    mb = self.m(tuple(S[i] for i in b))
                    if mb == 0.0:
                        p = 0.0
                        break
                    p *= mb
                tot += p
            self.cum[S] = 0.0 if abs(tot) < 1e-12 else tot
        return self.cum[S]

    def delta(self, x, y, pool=None, smax=None, even_only=False):
        pool = [z for z in (range(self.n) if pool is None else pool) if z not in (x, y)]
        best, arg = math.inf, None
        s = 2
        smax = len(pool) + 2 if smax is None else smax
        while s <= smax and s - 2 < best:
            if not (even_only and s % 2):
                for extra in itertools.combinations(pool, s - 2):
                    S = (x, y) + extra
                    kk = self.k(S)
                    if kk == 0.0:
                        continue
                    v = (s - 2) + max(0.0, -math.log(abs(kk), 3))
                    if v < best - 1e-12:
                        best, arg = v, tuple(sorted(S))
            s += 1
        return best, arg


def tau(c):
    return math.inf if abs(c) < 1e-15 else max(0.0, -math.log(abs(c), 3))


# ---------------- parity bases ----------------

def least_circuit(knots, n, x, y):
    rows = [sum(1 << v for v in k) for law, k in knots]
    span = {0}
    for r in rows:
        span |= {s ^ r for s in span}
    words = sorted(span - {0}, key=lambda w: bin(w).count("1"))
    circuits = []
    for w in words:                                      # by size: a word is a circuit when no smaller circuit lies inside it
        if not any((c & w) == c for c in circuits):
            circuits.append(w)
    sizes = [bin(c).count("1") for c in circuits if (c >> x) & 1 and (c >> y) & 1]
    return min(sizes) if sizes else math.inf


def part_linear(nb=300, seed=20261118):
    rng = random.Random(seed)
    out = {"bases": 0, "pairs": 0, "mismatch": 0, "triangle_violations": 0, "triples_checked": 0, "examples": []}
    for _ in range(nb):
        n = rng.randint(6, 9)
        kn = [("P", t) for t in rng.sample(list(itertools.combinations(range(n), 3)), rng.randint(2, 6))]
        B = Base(states(n, kn), n)
        D = {}
        for x, y in itertools.combinations(range(n), 2):
            c = least_circuit(kn, n, x, y)
            d = B.delta(x, y)[0]
            D[(x, y)] = D[(y, x)] = d
            out["pairs"] += 1
            if not ((c == math.inf and d == math.inf) or abs(d - (c - 2)) < 1e-9):
                out["mismatch"] += 1
        for x, y, z in itertools.permutations(range(n), 3):
            if D[(x, z)] < math.inf and D[(x, y)] < math.inf and D[(y, z)] < math.inf:
                out["triples_checked"] += 1
                if D[(x, z)] > D[(x, y)] + D[(y, z)] + 1e-9:
                    out["triangle_violations"] += 1
                    if len(out["examples"]) < 3:
                        out["examples"].append({"n": n, "knots": [k for _, k in kn], "x": x, "y": y, "z": z,
                                                "dxz": D[(x, z)], "dxy": D[(x, y)], "dyz": D[(y, z)]})
        out["bases"] += 1
    return out


# ---------------- knot trees ----------------

def tree_shapes(k):
    """Knot trees of k knots up to isomorphism (knot i shares one distinction with the earlier ones), by WL hash and VF2."""
    level = [[(0, 1, 2)]]
    for _ in range(k - 1):
        seen = {}
        nxt = []
        for knots in level:
            n = 2 * len(knots) + 1
            for v in range(n):
                cand = knots + [(v, n, n + 1)]
                G = nx.Graph()
                for i, kn in enumerate(cand):
                    G.add_node(("k", i), t="k")
                    for u in kn:
                        G.add_node(("v", u), t="v")
                        G.add_edge(("k", i), ("v", u))
                hsh = nx.weisfeiler_lehman_graph_hash(G, node_attr="t")
                if not any(nx.is_isomorphic(G, H, node_match=lambda a, b: a["t"] == b["t"]) for H in seen.get(hsh, [])):
                    seen.setdefault(hsh, []).append(G)
                    nxt.append(cand)
        level = nxt
    return level


def steps(knots, n):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for kn in knots:
        G.add_edges_from(itertools.combinations(kn, 2))
    return dict(nx.all_pairs_shortest_path_length(G))


def one_tree(args):
    knots, laws = args
    n = 2 * len(knots) + 1
    sp = steps(knots, n)
    B = Base(states(n, list(zip(laws, knots))), n)
    bad, worst = 0, 0.0
    for x, y in itertools.combinations(range(n), 2):
        d = sp[x][y]
        v = B.delta(x, y, smax=d + 1, even_only=set(laws) == {"N"})[0]
        if v == math.inf or abs(v - d) > 1e-9:            # nothing below d found and d itself attained by the path set
            v2 = min(v, B.delta(x, y, smax=d + 2)[0])
            if abs(v2 - d) > 1e-9:
                bad += 1
                worst = max(worst, abs(v2 - d))
    return {"k": len(knots), "laws": "".join(laws), "n": n, "pairs": n * (n - 1) // 2, "mismatch": bad, "worst": worst}


def part_trees(kmixed=5, kpure=6, workers=12):
    jobs = []
    shapes = {}
    for k in range(1, kpure + 1):
        shapes[k] = tree_shapes(k)
        for knots in shapes[k]:
            assigns = itertools.product("PN", repeat=k) if k <= kmixed else [("P",) * k, ("N",) * k]
            jobs.extend((knots, laws) for laws in assigns)
    with Pool(workers) as P:
        rows = P.map(one_tree, jobs, chunksize=4)
    return {"shapes": {k: len(v) for k, v in shapes.items()}, "bases": len(rows), "pairs": sum(r["pairs"] for r in rows),
            "mismatch": sum(r["mismatch"] for r in rows), "bad_rows": [r for r in rows if r["mismatch"]][:10]}


def part_trees7(workers=12):
    shapes = tree_shapes(7)
    jobs = [(kn, laws) for kn in shapes for laws in (("P",) * 7, ("N",) * 7)]
    with Pool(workers) as P:
        rows = P.map(one_tree, jobs, chunksize=1)
    return {"shapes": len(shapes), "bases": len(rows), "pairs": sum(r["pairs"] for r in rows),
            "mismatch": sum(r["mismatch"] for r in rows), "bad_rows": [r for r in rows if r["mismatch"]][:10]}


# ---------------- the weave patch ----------------

def weave(R):
    sites = [(i, j) for i in range(-R, R + 1) for j in range(-R, R + 1) if max(abs(i), abs(j), abs(i + j)) <= R]
    sites.sort(key=lambda p: (p[1], p[0]))
    ix = {p: k for k, p in enumerate(sites)}
    knots = []
    for (i, j) in sites:
        for tri in (((i, j), (i + 1, j), (i, j + 1)), ((i + 1, j), (i, j + 1), (i + 1, j + 1))):
            if all(p in ix for p in tri):
                knots.append(("N", tuple(ix[p] for p in tri)))
    return sites, ix, knots


def part_weave():
    out = {}
    pairs = [((-1, 1), (1, -1)), ((0, 0), (0, 2)), ((0, 0), (2, 0)), ((0, 0), (1, 1)), ((-1, 0), (1, 0)), ((0, -1), (0, 1))]
    for R, smax in ((2, 6), (3, 4)):
        sites, ix, knots = weave(R)
        st = states(len(sites), knots)
        B = Base(st, len(sites))
        res = {"sites": len(sites), "knots": len(knots), "states": int(len(st)), "pairs": {}}
        for a, b in pairs:
            x, y = ix[a], ix[b]
            d, S = B.delta(x, y, smax=smax, even_only=True)
            res["pairs"][f"{a}-{b}"] = {"C": B.m((x, y)), "tau": tau(B.m((x, y))), "delta": d,
                                        "argmin": [sites[v] for v in S] if S else None}
        if R == 2:
            short = 0
            for x, y in itertools.combinations(range(len(sites)), 2):
                if B.delta(x, y, smax=6, even_only=True)[0] < tau(B.m((x, y))) - 1e-9:
                    short += 1
            res["pairs_with_delta_below_tau"] = short
        out[f"R={R}"] = res
        print("weave", R, json.dumps(res), file=sys.stderr, flush=True)
    return out


def part_weave3(i, m):
    sites, ix, knots = weave(3)
    B = Base(states(len(sites), knots), len(sites))
    rad = lambda p: max(abs(p[0]), abs(p[1]), abs(p[0] + p[1]))
    todo = [(x, y) for x, y in itertools.combinations(range(len(sites)), 2) if tau(B.m((x, y))) > 2]
    rows = []
    for x, y in todo[i::m]:
        t = tau(B.m((x, y)))
        d, S = B.delta(x, y, smax=4, even_only=True)
        rows.append({"x": sites[x], "y": sites[y], "radii": [rad(sites[x]), rad(sites[y])], "tau": t, "delta": d,
                     "argmin": [sites[v] for v in S] if S else None})
    return {"shard": i, "of": m, "pairs_with_tau_above_2": len(todo), "rows": rows}


# ---------------- the chain grid with loose distinctions ----------------

def part_chain(W=4, H=4):
    """Grid distinctions 0..15 and one loose distinction per neighbouring pair (24). Moments with loose spins come from
    E[s_p | grid] = -(s_u + s_v)/2, the loose spins independent given the grid (each knot NAE(u, p, v), p in no other knot)."""
    cells = [(i, j) for i in range(W) for j in range(H)]
    ix = {c: k for k, c in enumerate(cells)}
    links = [(ix[(i, j)], ix[(i + 1, j)]) for i in range(W - 1) for j in range(H)] + \
            [(ix[(i, j)], ix[(i, j + 1)]) for i in range(W) for j in range(H - 1)]
    ng = len(cells)
    g = np.arange(1 << ng, dtype=np.int64)
    spin = (1 - 2 * ((g[:, None] >> np.arange(ng)[None, :]) & 1)).astype(np.float64)
    w = np.ones(len(g))
    for a, b in links:
        w *= np.where(spin[:, a] == spin[:, b], 1.0, 2.0)
    w /= w.sum()
    loose = {ng + i: l for i, l in enumerate(links)}

    class ChainBase(Base):
        def __init__(self):
            self.n = ng + len(links)
            self.mom = {(): 1.0}
            self.cum = {}

        def m(self, S):
            S = tuple(sorted(S))
            if S not in self.mom:
                f = np.ones(len(g))
                for v in S:
                    if v < ng:
                        f = f * spin[:, v]
                    else:
                        a, b = loose[v]
                        f = f * (-(spin[:, a] + spin[:, b]) / 2)
                val = float(w @ f)
                self.mom[S] = 0.0 if abs(val) < 1e-13 else val
            return self.mom[S]

    B = ChainBase()
    rows = []
    for x, y in itertools.combinations(range(ng), 2):
        t = tau(B.m((x, y)))
        d, S = B.delta(x, y, smax=4, even_only=True)
        rows.append({"x": cells[x], "y": cells[y], "tau": t, "delta": d, "uses_loose": bool(S and any(v >= ng for v in S))})
    worst = max(rows, key=lambda r: r["tau"] - r["delta"])
    return {"pairs": len(rows), "below_tau": sum(r["delta"] < r["tau"] - 1e-9 for r in rows),
            "max_tau": max(r["tau"] for r in rows), "largest_gap": worst,
            "note": "sets of four can beat tau only where tau > 2; the largest tau on the patch bounds what sets of six could do"}


# ---------------- the split line ----------------

def part_split(m=8):
    full = (1 << m) - 1
    st = {0, full}
    for c in range(m - 1):
        cut = (1 << (c + 1)) - 1
        st |= {cut, full ^ cut}
    st = sorted(st)
    B = Base(st, m)
    rot = sorted({((s << 1) & full) | (((s >> (m - 1)) & 1) ^ 1) for s in st})
    return {"states": len(st), "rotation_maps_states": rot == st,
            "delta_from_0": {y: round(B.delta(0, y, smax=6, even_only=True)[0], 6) for y in range(1, m)}}


def merge_weave3(files):
    from collections import Counter
    rows, tot = [], None
    for f in files:
        d = json.load(open(f))
        rows += d["rows"]
        tot = d["pairs_with_tau_above_2"]
    short = [r for r in rows if r["delta"] < r["tau"] - 1e-9]
    return {"radius": 3, "pairs_with_tau_above_2": tot, "searched": len(rows), "delta_below_tau": len(short),
            "radii_of_shortcut_pairs": {str(k): v for k, v in Counter(tuple(sorted(r["radii"])) for r in short).items()},
            "shortcut_pairs": short, "pairs_with_tau_above_4_not_exact_above_4": [r for r in rows if r["tau"] > 4 and r["delta"] >= 4]}


if __name__ == "__main__" and sys.argv[1] == "weave3_merge":
    print(json.dumps(merge_weave3(sys.argv[2:]), indent=1, default=str))
elif __name__ == "__main__" and sys.argv[1] == "weave3":
    print(json.dumps(part_weave3(int(sys.argv[2]), int(sys.argv[3])), indent=1, default=str))
elif __name__ == "__main__":
    part = sys.argv[1]
    f = {"linear": part_linear, "trees": part_trees, "trees7": part_trees7, "weave": part_weave, "chain": part_chain,
         "split": part_split}[part]
    print(json.dumps(f(), indent=1, default=str))
