"""PICK-TWO-20261118-001B-E001: who picks the number of orders.

The moves are fills (one to three betweenness knots on any old pairs, no state added) and subdivisions (one knot B(u, p, v) on a
pair differing in exactly two states), as in NEVER-NEST-20261118-001's NNF; nnlib.py is pinned in the contract.  A step reads the
states only.  The rules:

- CAP(d): the fills after which lambda <= d (and, for d = 2, a bipartite crossing graph: NNF); else a subdivision.
- PRICE(f): the moves minimising (states added) + f(lambda after); f(l) = w * l (linear) or w * l^2 (convex).
- KEEP: the fills that leave lambda unchanged; else a subdivision (fewest orders first, then fewest states).
- CC: corner fills across two crossing splits; else a subdivision (NEVER-NEST's CC).
- ODD: the fills after which the crossing graph has no odd cycle (k <= 2); else a subdivision.
- FRESH (the advisor's b'): the fills whose new crossings all join two splits that crossed nothing before; else a subdivision.
- NEWCROSS (b): the fills that make no new crossing between two splits that both crossed something before; else a subdivision.
- SEED (the advisor's g, seed and copy): while no two splits cross, any fill; after that, the fills that make no new crossing
  between two splits that already crossed something, and under which every split that crossed nothing and gains crossings ends
  with exactly the crossers of a split that already crossed something; else a subdivision.
Ties are uniform over distinct extensions.  No rule but CAP and PRICE names a number of orders; FRESH, NEWCROSS and SEED name only
"crosses nothing".
"""
import itertools
import os
import random
import sys

import networkx as nx
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.append(os.path.join(ROOT, "experiments", "NEVER-NEST-20261118-001B", "NEVER-NEST-20261118-001B-E001_nest"))
import nnlib as L  # noqa: E402

M = L.M
pc = M.pc


def splits(S, n):
    full = (1 << n) - 1
    return sorted({min(s, full ^ s) for s in S if s not in (0, full)}), full


def cross(a, b, full):
    return bool(a & b and a & (full ^ b) and (full ^ a) & b and (full ^ a) & (full ^ b))


def kl(S, n):
    """(k, lambda): k is 1, 2 or 3 (3 meaning not bipartite), as melib.measure."""
    m = M.measure(S, n)
    return m["k"], m["lam"]


def grid(S, n):
    """Whether the crossing graph is complete multipartite with parts s_1, ..., s_d (all >= 1, d >= 2) and n = prod(s_i + 1):
    a full d-grid.  Returns (d, sorted part sizes) for a full grid, else None."""
    sp, full = splits(S, n)
    G = nx.Graph()
    G.add_nodes_from(range(len(sp)))
    G.add_edges_from((i, j) for i, j in itertools.combinations(range(len(sp)), 2) if cross(sp[i], sp[j], full))
    if G.number_of_edges() == 0:
        return None
    parts = list(nx.connected_components(nx.complement(G)))
    for P in parts:
        if any(G.has_edge(a, b) for a, b in itertools.combinations(P, 2)):
            return None
    if G.number_of_edges() != (len(sp) ** 2 - sum(len(P) ** 2 for P in parts)) // 2:
        return None
    sizes = sorted((len(P) for P in parts), reverse=True)
    prod = 1
    for s in sizes:
        prod *= s + 1
    return (len(sizes), sizes) if prod == n and len(sizes) >= 2 else None


def crossing_graph(S, n):
    sp, full = splits(S, n)
    G = nx.Graph()
    G.add_nodes_from(range(len(sp)))
    G.add_edges_from((i, j) for i, j in itertools.combinations(range(len(sp)), 2) if cross(sp[i], sp[j], full))
    return sp, G


def reading(S, n):
    k, lam = kl(S, n)
    g = grid(S, n)
    sp, G = crossing_graph(S, n)
    omega = max((len(c) for c in nx.find_cliques(G)), default=1) if G.number_of_edges() else 1
    return {"n": n, "N": len(S), "k": k, "lam": lam, "full_grid": g is not None, "grid": g[1] if g else None,
            "omega": omega, "isolated": sum(1 for v in G if G.degree(v) == 0),
            "components": sum(1 for c in nx.connected_components(G) if len(c) > 1)}


def new_crossings(S, n, a1):
    """For a fill whose new distinction takes value 1 on the states in a1: the old split pairs (as indices into splits(S, n)) that
    come to cross, and the crossing graph before.  A pair comes to cross exactly when the new distinction lands in its one empty
    quadrant."""
    sp, G = crossing_graph(S, n)
    full = (1 << n) - 1
    idx = {x: i for i, x in enumerate(S)}
    val = lambda X: (a1 >> idx[X]) & 1
    new = []
    for i, j in itertools.combinations(range(len(sp)), 2):
        if G.has_edge(i, j):
            continue
        a, b = sp[i], sp[j]
        for X in (a, full ^ a):
            for Y in (b, full ^ b):
                if X & Y == 0 and val(X) and val(Y):
                    new.append((i, j))
    return new, G


def fills(S, n):
    """Every fill (zero-cost extension by one to three knots on any old pairs), as a list of (a0, a1); copies excluded.

    Every fill has a middle knot B(u, r, v), since only middle knots pin the constant states; it pins r to u on the states where u
    and v agree.  The other one or two knots must agree with that and pin the rest R (where u and v differ).  So for each pair u, v
    the knots consistent with r = u off R are collected, restricted to R, and every one or two that cover R without conflict give a
    fill.  Equal to NEVER-NEST's free_zero (all 2^(N/2 - 1) candidate functions) wherever both run: checks.py."""
    N = len(S)
    if N > 62:
        raise RuntimeError("fills: more than 62 states")
    seen, O, Z, full = L.free_masks(S, n)
    keys = list(seen)
    P0 = np.array([k[0] for k in keys], dtype=np.int64)
    P1 = np.array([k[1] for k in keys], dtype=np.int64)
    ties = {(Z[u], O[u]) for u in range(n)}
    out = set()
    for u, v in itertools.combinations(range(n), 2):
        R = O[u] ^ O[v]
        off = full ^ R
        U1, U0 = O[u] & off, Z[u] & off
        ok = ((P0 & U1) == 0) & ((P1 & U0) == 0)
        q0 = P0[ok] & R
        q1 = P1[ok] & R
        keep = (q0 | q1) != 0
        q0, q1 = q0[keep], q1[keep]
        if len(q0) == 0:
            continue
        pairs = set(zip(q0.tolist(), q1.tolist()))
        q0 = np.array([a for a, b in pairs], dtype=np.int64)
        q1 = np.array([b for a, b in pairs], dtype=np.int64)
        for a, b in pairs:                                   # one more knot
            if (a | b) == R:
                out.add((full ^ (U1 | b), U1 | b))
        cov = ((q0[:, None] | q1[:, None] | q0[None, :] | q1[None, :]) == R)
        clash = ((q0[:, None] & q1[None, :]) != 0) | ((q1[:, None] & q0[None, :]) != 0)
        ii, jj = np.nonzero(np.triu(cov & ~clash, 1))
        for i, j in zip(ii.tolist(), jj.tolist()):        # two more knots
            F1 = U1 | int(q1[i]) | int(q1[j])
            out.add((full ^ F1, F1))
    return sorted(f for f in out if f not in ties)


def subdivisions(S, n):
    return sorted(L.free_subs(S, n))


def options(S, n, rule, param=None):
    """The rule's options (a list of (a0, a1), uniform), and the kind of step: 'fill' or 'sub'."""
    if rule == "CC":
        ops, _ = L.cc_options(S, n)
        ops = [k for k, _ in ops]
        return ops, ("fill" if ops and len(M.apply(S, n, *ops[0])) == len(S) else "sub")
    k0, l0 = kl(S, n)
    F = fills(S, n)
    after = {f: kl(M.apply(S, n, *f), n + 1) for f in F}
    if rule == "CAP":
        d = param
        good = [f for f in F if after[f][1] <= d and (d != 2 or after[f][0] <= 2)]
    elif rule == "KEEP":
        good = [f for f in F if after[f][1] == l0]
    elif rule == "ODD":
        good = [f for f in F if after[f][0] <= 2]
    elif rule in ("FRESH", "NEWCROSS", "SEED"):
        good = []
        for f in F:
            new, G = new_crossings(S, n, f[1])
            active = {v for v in G if G.degree(v) > 0}
            if rule == "FRESH":
                ok = all(i not in active and j not in active for i, j in new)
            elif rule == "NEWCROSS":
                ok = all(not (i in active and j in active) for i, j in new)
            else:
                if not active:
                    ok = True
                else:
                    ok = all(not (i in active and j in active) for i, j in new)
                    if ok and new:
                        H = G.copy()
                        H.add_edges_from(new)
                        gained = {v for e in new for v in e if v not in active}
                        nbrs = {v: frozenset(H[v]) for v in H}
                        old = {nbrs[v] for v in active}
                        ok = all(nbrs[u] in old for u in gained)
            if ok:
                good.append(f)
    elif rule == "PRICE":
        kind, w = param
        price = (lambda l: w * l) if kind == "lin" else (lambda l: w * l * l)
        scored = [(price(after[f][1]), f, "fill") for f in F]
        scored += [(2 + price(l0), s, "sub") for s in subdivisions(S, n)]
        if not scored:
            return [], None
        low = min(x[0] for x in scored)
        top = [x for x in scored if abs(x[0] - low) < 1e-9]
        kinds = {x[2] for x in top}
        return [x[1] for x in top], ("fill" if kinds == {"fill"} else "sub" if kinds == {"sub"} else "tie")
    else:
        raise ValueError(rule)
    if good:
        return good, "fill"
    return subdivisions(S, n), "sub"


def grow(S, n, nmax, rule, seed_value, param=None, stop_N=62):
    """A labelled run to nmax distinctions (or until the states exceed stop_N, the fill enumeration's limit)."""
    rng = random.Random(seed_value)
    S = tuple(sorted(S))
    trace = [{**reading(S, n), "kind": "start"}]
    while n < nmax:
        if len(S) > stop_N - 2:
            trace.append({"n": n + 1, "stopped": "state limit", "N": len(S)})
            break
        ops, kind = options(S, n, rule, param)
        if not ops:
            trace.append({"n": n + 1, "stopped": "no option"})
            break
        a0, a1 = rng.choice(ops)
        S2 = M.apply(S, n, a0, a1)
        cost = len(S2) - len(S)
        S, n = S2, n + 1
        trace.append({**reading(S, n), "kind": "fill" if cost == 0 else "sub", "cost": cost, "options": len(ops),
                      "choice": kind})
    return trace


def cube(d):
    """Q_d: the line of two (one split) taken d times, as states over 2^d distinctions (the cells of {0,1}^d)."""
    n = 1 << d
    S = set()
    for i in range(d):
        s = sum(1 << x for x in range(n) if (x >> i) & 1)
        S.add(s)
        S.add(((1 << n) - 1) ^ s)
    S.add(0)
    S.add((1 << n) - 1)
    return tuple(sorted(S)), n


def start(name):
    if name == "2x2":
        return L.square_states(), 4
    if name.startswith("Q"):
        return cube(int(name[1:]))
    if name.startswith("line"):
        n = int(name[4:])
        return L.line_states(n), n
    raise ValueError(name)
