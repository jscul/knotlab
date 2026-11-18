"""The cumulant distance of a base (sub-goal B200).

A base is a list of allowed states (bitmasks over n distinctions), weighted uniformly; spins s = (-1)^x. For a set S of
distinctions, the moment is E[prod_S s] and the joint cumulant kappa_S = sum over partitions pi of S of
(-1)^(|pi|-1) (|pi|-1)! prod_B E[prod_B s]. The cumulant distance is

    delta(x, y) = min over S containing x and y of (|S| - 2) + tau(kappa_S),   tau(k) = max(0, -log_3 |k|),

with sets of zero cumulant skipped (infinite). It is invariant under renaming distinctions and under switching values (flipping a
distinction's values multiplies kappa_S by -1 when it is in S). Since tau >= 0, only sets with |S| - 2 below the best value so far
can improve it, so the search stops."""
import functools
import itertools
import math

import numpy as np

LAWS = {
    "P": lambda v: sum(v) % 2 == 0,                       # parity
    "N": lambda v: len(set(v)) > 1,                       # not-all-equal
    "B": lambda v: not (v[0] == v[2] != v[1]),            # betweenness: v[1] between v[0] and v[2]
}


def states_from_knots(n, knots, chunk=1 << 22):
    out = []
    for start in range(0, 1 << n, chunk):
        s = np.arange(start, min(start + chunk, 1 << n), dtype=np.int64)
        ok = np.ones(len(s), dtype=bool)
        for law, k in knots:
            a, b, c = [(s >> i) & 1 for i in k]
            if law == "P":
                ok &= (a + b + c) % 2 == 0
            elif law == "N":
                ok &= ~((a == b) & (b == c))
            elif law == "B":
                ok &= ~((a == c) & (a != b))
        out.extend(int(v) for v in s[ok])
    return out


def _partitions(seq):
    if not seq:
        yield []
        return
    first, rest = seq[0], seq[1:]
    for p in _partitions(rest):
        yield [(first,)] + p
        for i in range(len(p)):
            yield p[:i] + [(first,) + p[i]] + p[i + 1:]


@functools.lru_cache(maxsize=None)
def partitions_of_size(m):
    return [[tuple(sorted(b)) for b in p] for p in _partitions(tuple(range(m)))]


class Base:
    """Uniform over the given states, or weighted (weights[i] for states[i])."""

    def __init__(self, states, n, weights=None):
        self.n = n
        a = np.array(states, dtype=np.int64)
        self.bits = np.stack([(a >> i) & 1 for i in range(n)], axis=1).astype(np.int8)
        w = np.ones(len(states)) if weights is None else np.asarray(weights, dtype=float)
        self.w = w / w.sum()
        self.N = len(states)
        self._mom = {}
        self._cum = {}

    def moment(self, S):
        S = tuple(sorted(S))
        v = self._mom.get(S)
        if v is None:
            if not S:
                v = 1.0
            else:
                par = self.bits[:, list(S)].sum(axis=1) % 2
                v = float(np.dot(self.w, 1.0 - 2.0 * par))
                if abs(v) < 1e-13:
                    v = 0.0
            self._mom[S] = v
        return v

    def cumulant(self, S):
        """kappa_S by the moment-cumulant recursion m_S = sum over B containing min(S) of kappa_B m_(S minus B)."""
        S = tuple(sorted(S))
        v = self._cum.get(S)
        if v is not None:
            return v
        if len(S) == 1:
            v = self.moment(S)
        else:
            s0, rest = S[0], S[1:]
            v = self.moment(S)
            for r in range(0, len(rest)):
                for sub in itertools.combinations(rest, r):
                    B = (s0,) + sub
                    comp = tuple(z for z in rest if z not in sub)
                    mc = self.moment(comp)
                    if mc == 0.0:
                        continue
                    kb = self.cumulant(B)
                    if kb != 0.0:
                        v -= kb * mc
            if abs(v) < 1e-12:
                v = 0.0
        self._cum[S] = v
        return v

    def delta(self, x, y, smax=None, among=None):
        """(value, argmin set, cumulant); sets drawn from `among` (default every distinction); exact when smax >= best + 2."""
        best, arg, kap = math.inf, None, 0.0
        pool = [z for z in (range(self.n) if among is None else among) if z not in (x, y)]
        smax = len(pool) + 2 if smax is None else smax
        m = 2
        while m <= smax and m - 2 < best:
            for extra in itertools.combinations(pool, m - 2):
                S = tuple(sorted((x, y) + extra))
                k = self.cumulant(S)
                if k == 0.0:
                    continue
                v = (m - 2) + max(0.0, -math.log(abs(k), 3))
                if v < best - 1e-12:
                    best, arg, kap = v, S, k
            m += 1
        return best, arg, kap

    def correlation(self, x, y):
        return self.moment((x, y))


def tau(c):
    return math.inf if abs(c) < 1e-15 else max(0.0, -math.log(abs(c), 3))


# ---------- knot trees ----------

def _incidence(knots):
    import networkx as nx
    G = nx.Graph()
    for i, kn in enumerate(knots):
        for v in kn:
            G.add_edge(("k", i), ("v", v))
    for nd in G.nodes:
        G.nodes[nd]["t"] = nd[0]
    return G


def tree_shapes(k):
    """Every knot tree with k three-place knots up to isomorphism: knot i (i >= 1) shares one distinction with the earlier ones
    and adds two fresh ones; distinctions numbered in order of appearance. Isomorphism of the knot-distinction incidence trees."""
    import networkx as nx
    levels = [[([(0, 1, 2)], 3)]]
    for _ in range(k - 1):
        nxt, graphs = [], []
        for knots, n in levels[-1]:
            for v in range(n):
                cand = (knots + [(v, n, n + 1)], n + 2)
                G = _incidence(cand[0])
                if not any(nx.is_isomorphic(G, H, node_match=lambda a, b: a["t"] == b["t"]) for H in graphs):
                    graphs.append(G)
                    nxt.append(cand)
        levels.append(nxt)
    return levels[k - 1]


def steps_apart(knots, n):
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for kn in knots:
        for a, b in itertools.combinations(kn, 2):
            G.add_edge(a, b)
    return dict(nx.all_pairs_shortest_path_length(G))


# ---------- linear bases ----------

def gf2_rank_basis(vecs, n):
    basis = []
    for v in vecs:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return basis


def dual_codewords(knots, n):
    """Every sum of parity checks (as bitmasks): the dual code."""
    checks = gf2_rank_basis([sum(1 << i for i in k) for law, k in knots if law == "P"], n)
    words = {0}
    for c in checks:
        words |= {w ^ c for w in words}
    return words - {0}


def min_circuit_through(words, x, y):
    """Least size of a circuit (inclusion-minimal nonzero dual codeword) containing x and y; inf if none."""
    circuits = [w for w in words if not any((u & w) == u and u != w for u in words)]
    best = math.inf
    for w in circuits:
        if (w >> x) & 1 and (w >> y) & 1:
            best = min(best, bin(w).count("1"))
    return best
