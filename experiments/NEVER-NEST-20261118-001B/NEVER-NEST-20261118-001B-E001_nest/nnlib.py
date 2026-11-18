"""NEVER-NEST-20261118-001B-E001: rules that never nest their fills (B197).

The moves are KF3's (MEET-ORDERS-20261118-001B's melib.py, pinned in the contract): a new distinction p = n with an irredundant set
of one to three betweenness knots, each on p and two old distinctions that already share a knot; every old state extends; p
constrained, no copy.  A step that adds no state is a fill.  The rules:

- KF3: the fewest resulting states, uniform over knot sets.
- NN (never nest): the fills after which the base still has two orders (k = lambda = 2), uniform over knot sets; if there is
  none, a subdivision: one knot B(u, p, v) on a co-knotted pair u, v that differ in exactly two states (one split), uniform over
  the pairs.  On a base that is a line with fills of triples this is Lemma C's rule (MEET-ORDERS-20261118-001A): a fill keeps two
  orders exactly when no middle lies strictly between the ends of a fill with another middle.
- NN2: the fewest resulting states among the options after which the base has two orders, uniform over knot sets.
- SUB: subdivisions only (the baseline: it keeps the number of orders and never fills).
- NNF (never nest, free): NN with every pair of old distinctions allowed (A99's moves without the knot-sharing condition), uniform
  over distinct extensions, as in STATE-RULES-20261117-001's rules.

Every rule reads only the states and, for the knot-sharing rules, the pairs that share a knot: (S, G) is an exact Markov state.
"""
import itertools
import os
import random
import sys
from collections import Counter, defaultdict
from fractions import Fraction

import networkx as nx
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.append(os.path.join(ROOT, "experiments", "MEET-ORDERS-20261118-001B", "MEET-ORDERS-20261118-001B-E001_census"))
import melib as M  # noqa: E402

pc = M.pc
RULES = ("KF3", "NN", "NN2", "SUB")


def two(S, n):
    """Two orders (k = lambda = 2); the crossing graph's bipartiteness is checked first, since it is cheap and necessary."""
    full = (1 << n) - 1
    sp = sorted({min(s, full ^ s) for s in S if s not in (0, full)})
    adj = [[] for _ in sp]
    any_cross = False
    for i, j in itertools.combinations(range(len(sp)), 2):
        a, b = sp[i], sp[j]
        if a & b and a & (full ^ b) and (full ^ a) & b and (full ^ a) & (full ^ b):
            adj[i].append(j)
            adj[j].append(i)
            any_cross = True
    if not any_cross:
        return False
    col = [-1] * len(sp)
    for s0 in range(len(sp)):
        if col[s0] >= 0:
            continue
        col[s0] = 0
        stack = [s0]
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if col[y] < 0:
                    col[y] = 1 - col[x]
                    stack.append(y)
                elif col[y] == col[x]:
                    return False
    return M.measure(S, n)["lam"] == 2


def moves(S, n, G, wide=False):
    """melib.moves, which holds masks over the states in 64-bit integers, so it is used up to 62 states; beyond (or with wide),
    the same enumeration with the masks split into 64-bit words (equal to melib.moves wherever both run: checks.py)."""
    if len(S) <= 62 and not wide:
        return M.moves(S, n, G)
    cands, O, Z, full = M.candidates(S, n, G)
    N = len(S)
    ties = {(Z[u], O[u]) for u in range(n)}
    m = len(cands)
    W = (N + 63) // 64
    word = (1 << 64) - 1

    def arr(xs):
        return np.array([[(x >> (64 * w)) & word for w in range(W)] for x in xs], dtype=np.uint64).reshape(len(xs), W)
    P0 = arr([c[1] for c in cands])
    P1 = arr([c[2] for c in cands])
    clash = ((P0[:, None, :] & P1[None, :, :]) != 0).any(-1) | ((P1[:, None, :] & P0[None, :, :]) != 0).any(-1)
    comp = ~clash
    out = []

    def finish(idx):                  # as in melib.moves
        pin0 = 0
        pin1 = 0
        for i in idx:
            pin0 |= cands[i][1]
            pin1 |= cands[i][2]
        if len(idx) >= 2:
            for d in idx:
                q0 = 0
                q1 = 0
                for i in idx:
                    if i != d:
                        q0 |= cands[i][1]
                        q1 |= cands[i][2]
                if q0 == pin0 and q1 == pin1:
                    return None
        a0 = full ^ pin1
        a1 = full ^ pin0
        if pc(a0) + pc(a1) >= 2 * N:
            return None
        if (a0, a1) in ties:
            return None
        return (a0, a1, tuple(cands[i][0] for i in idx))

    for i in range(m):
        r = finish((i,))
        if r:
            out.append(r)
    ii, jj = np.nonzero(np.triu(comp, 1))
    for i, j in zip(ii.tolist(), jj.tolist()):
        r = finish((i, j))
        if r:
            out.append(r)
        ks = np.nonzero(comp[i, j + 1:] & comp[j, j + 1:])[0] + j + 1
        for k in ks.tolist():
            r = finish((i, j, k))
            if r:
                out.append(r)
    return out


def dis(S, u, v):
    return sum(((s >> u) ^ (s >> v)) & 1 for s in S)


def is_sub(ks, n, S):
    """A subdivision: one knot with the new distinction in the middle, on a pair that differs in exactly two states."""
    return len(ks) == 1 and ks[0][1] == n and dis(S, ks[0][0], ks[0][2]) == 2


def options(S, n, G, rule):
    """The rule's options at (S, G): a list of (a0, a1, knots), all equally likely, or [] if it stalls; and a diagnostic dict."""
    mv = moves(S, n, G)
    N = len(S)
    info = {"moves": len(mv)}
    if not mv:
        return [], info
    cost = {i: pc(a0) + pc(a1) - N for i, (a0, a1, _) in enumerate(mv)}
    zero = [i for i in cost if cost[i] == 0]
    info["zero"] = len(zero)
    memo = {}

    def keeps(i):                      # two orders after the option, computed once per distinct extension
        key = mv[i][:2]
        if key not in memo:
            memo[key] = two(M.apply(S, n, *key), n + 1)
        return memo[key]
    if rule == "KF3":
        low = min(cost.values())
        return [mv[i] for i in cost if cost[i] == low], info
    if rule in ("NN", "SUB"):
        keep = []
        if rule == "NN":
            keep = [i for i in zero if keeps(i)]
            info["zero_two"] = len(keep)
            info["zero_two_ext"] = len({mv[i][:2] for i in keep})
        if not keep:
            keep = [i for i in cost if is_sub(mv[i][2], n, S)]
        return [mv[i] for i in keep], info
    if rule == "NN2":
        for level in sorted(set(cost.values())):  # the cheapest level holding an option that keeps two orders
            good = [i for i in cost if cost[i] == level and keeps(i)]
            if level == 0:
                info["zero_two"] = len(good)
            if good:
                info["level"] = level
                return [mv[i] for i in good], info
        return [], info
    raise ValueError(rule)


def step_dist(S, n, G, rule):
    ops, _ = options(S, n, G, rule)
    if not ops:
        return None
    out = defaultdict(Fraction)
    for a0, a1, ks in ops:
        out[(M.apply(S, n, a0, a1), G | M.pairs_of(ks))] += Fraction(1, len(ops))
    return out


# ---------------------------------------------------------------- readings

def crossing(S, n):
    """Splits, their crossing graph's bipartition sizes (or None if not bipartite) and whether it is complete bipartite."""
    full = (1 << n) - 1
    sp = sorted({min(s, full ^ s) for s in S if s not in (0, full)})

    def cr(a, b):
        return all(x for x in (a & b, a & (full ^ b), (full ^ a) & b, (full ^ a) & (full ^ b)))
    Gc = nx.Graph()
    Gc.add_nodes_from(range(len(sp)))
    Gc.add_edges_from((i, j) for i, j in itertools.combinations(range(len(sp)), 2) if cr(sp[i], sp[j]))
    ncross = Gc.number_of_edges()
    if not nx.is_bipartite(Gc):
        return {"splits": len(sp), "crossings": ncross, "parts": None, "complete": False}
    if ncross == 0:
        return {"splits": len(sp), "crossings": 0, "parts": [len(sp), 0], "complete": False}
    comps = list(nx.connected_components(Gc))
    if len(comps) == 1:
        X, Y = nx.bipartite.sets(Gc)
        a, b = sorted((len(X), len(Y)), reverse=True)
        complete = ncross == a * b
        return {"splits": len(sp), "crossings": ncross, "parts": [a, b], "complete": complete}
    return {"splits": len(sp), "crossings": ncross, "parts": None, "complete": False, "components": len(comps)}


def reading(S, n):
    """The number of orders; the crossing graph; a full grid; and, when the crossing graph is connected and bipartite, the
    two chains' sizes and the empty cells of their grid."""
    m = M.measure(S, n)
    c = crossing(S, n)
    full_grid = bool(c["complete"] and n == (c["parts"][0] + 1) * (c["parts"][1] + 1))
    ch = chains_of(S, n)
    chains = sorted((len(ch[0]), len(ch[1])), reverse=True) if ch else None
    empty = (chains[0] + 1) * (chains[1] + 1) - n if ch else None
    return {"n": n, "N": len(S), "k": m["k"], "lam": m["lam"], "two": m["k"] == 2 and m["lam"] == 2,
            "splits": c["splits"], "crossings": c["crossings"], "parts": c["parts"], "complete": c["complete"],
            "full_grid": full_grid, "chains": chains, "empty": empty, "isolated": isolated(S, n)}


def isolated(S, n):
    """Splits that cross no other split."""
    full = (1 << n) - 1
    sp = sorted({min(s, full ^ s) for s in S if s not in (0, full)})

    def cr(a, b):
        return bool(a & b and a & (full ^ b) and (full ^ a) & b and (full ^ a) & (full ^ b))
    return sum(1 for a in sp if not any(cr(a, b) for b in sp if b != a))


# ---------------------------------------------------------------- the line and odd sets (labelled runs of NN)

def odd_sets_line(S, n, line):
    """If the states, read on the line distinctions (in the given order), are exactly the line's 2L cuts, each once, the odd set of
    every other distinction as positions on the line (its value changes between the prefix of i and of i + 1 line distinctions at
    position i); else None."""
    L = len(line)
    by_line = {}
    for s in S:
        key = tuple((s >> u) & 1 for u in line)
        k = sum(key)
        if key != tuple([1] * k + [0] * (L - k)) and key != tuple([0] * (L - k) + [1] * k):
            return None
        if key in by_line:
            return None
        by_line[key] = s
    prefixes = [tuple([1] * k + [0] * (L - k)) for k in range(L + 1)]
    if len(by_line) != 2 * L or any(p not in by_line for p in prefixes):
        return None
    out = {}
    for u in range(n):
        if u not in line:
            f = [(by_line[p] >> u) & 1 for p in prefixes]
            out[u] = tuple(i for i in range(L) if f[i] != f[i + 1])
    return out


def lemma_c(odd):
    """Lemma C's verdict on a base of line + fills with odd sets: 1, 2 or 3 (three or more) orders; None if some odd set is not a
    triple."""
    tri = list(odd.values())
    if any(len(t) != 3 for t in tri):
        return None
    if not tri:
        return 1
    for f, g in itertools.permutations(tri, 2):
        if f[0] < g[1] < f[2] and g[1] != f[1]:
            return 3
    return 2


def middles(odd):
    return sorted({t[1] for t in odd.values() if len(t) == 3})


# ---------------------------------------------------------------- exact distributions

def exact(knots, n0, nmax, rule):
    S = M.base(n0, knots)
    G = M.pairs_of(knots)
    dist = {M.canon(S, n0, G): Fraction(1)}
    n = n0
    levels = []
    stalled = Fraction(0)
    while True:
        two_p = Fraction(0)
        grid_p = Fraction(0)
        Nd = Counter()
        for (S1, G1), p in dist.items():
            r = reading(S1, n)
            Nd[r["N"]] += p
            if r["two"]:
                two_p += p
            if r["full_grid"]:
                grid_p += p
        levels.append({"n": n, "classes": len(dist), "two": two_p, "full_grid": grid_p, "N": dict(Nd), "stalled": stalled})
        if n >= nmax:
            break
        new = defaultdict(Fraction)
        for (S1, G1), p in dist.items():
            sd = step_dist(S1, n, G1, rule)
            if sd is None:
                stalled += p
                continue
            for (S2, G2), q in sd.items():
                new[M.canon(S2, n + 1, G2)] += p * q
        dist = dict(new)
        n += 1
    return levels


def fr(levels):
    out = []
    for L in levels:
        out.append({"n": L["n"], "classes": L["classes"], "two": str(L["two"]), "full_grid": str(L["full_grid"]),
                    "N": {str(k): str(v) for k, v in sorted(L["N"].items())}, "stalled": str(L["stalled"])})
    return out


# ---------------------------------------------------------------- labelled runs

def grow(knots, n0, nmax, rule, seed_value, track_line=False):
    rng = random.Random(seed_value)
    S = M.base(n0, knots)
    G = M.pairs_of(knots)
    n = n0
    line = list(range(n0)) if track_line else None
    trace = [{**reading(S, n), "kind": "start"}]
    while n < nmax:
        ops, info = options(S, n, G, rule)
        if not ops:
            trace.append({"n": n + 1, "stopped": "no option", **info})
            break
        a0, a1, ks = rng.choice(ops)
        S2 = M.apply(S, n, a0, a1)
        cost = len(S2) - len(S)
        kind = "fill" if cost == 0 else ("sub" if is_sub(ks, n, S) else "other")
        if line is not None and kind == "sub":
            u, _, v = ks[0]
            if u in line and v in line and abs(line.index(u) - line.index(v)) == 1:
                line.insert(max(line.index(u), line.index(v)), n)
            else:
                placed = False
                for i in range(len(line) + 1):
                    trial = line[:i] + [n] + line[i:]
                    if odd_sets_line(S2, n + 1, trial) is not None:
                        line, placed = trial, True
                        break
                if not placed:
                    line = None
        elif line is not None and kind == "other":
            line = None
        G = G | M.pairs_of(ks)
        S, n = S2, n + 1
        row = {**reading(S, n), "kind": kind, "cost": cost, "options": len(ops), **info}
        if line is not None:
            odd = odd_sets_line(S, n, line)
            if odd is None:
                line = None
            else:
                row["lemma_c"] = lemma_c(odd)
                row["middles"] = middles(odd)
                row["line"] = len(line)
                if kind == "fill":
                    row["odd"] = list(odd[n - 1])
        trace.append(row)
    return trace


# ---------------------------------------------------------------- the free rule NNF (no knot-sharing condition)

def free_masks(S, n):
    """Distinct single-knot pins over every old pair: {(pin0, pin1): knot}, pins as masks over the states."""
    O, Z, full = M.cols(S, n)
    seen = {}
    for u, v in itertools.combinations(range(n), 2):
        eq = (O[u] & O[v]) | (Z[u] & Z[v])
        ne = full ^ eq
        for k, p0, p1 in (((u, n, v), Z[u] & Z[v], O[u] & O[v]), ((u, v, n), ne & Z[v], ne & O[v]),
                          ((v, u, n), ne & Z[u], ne & O[u])):
            seen.setdefault((p0, p1), k)
    return seen, O, Z, full


def free_zero(S, n):
    """Every zero-cost extension by one to three knots on any old pairs, as {(a0, a1): fewest knots}; copies excluded.  A zero-cost
    extension is a function of the state that flips with the complement (betweenness is flip-symmetric) and takes the constants'
    values (only middle knots pin them), so the candidates are 2^(N/2 - 1) functions, each checked for a cover by at most three
    consistent knots."""
    seen, O, Z, full = free_masks(S, n)
    N = len(S)
    assert N < 63
    ties = {(Z[u], O[u]) for u in range(n)}
    keys = list(seen)
    P0 = np.array([k[0] for k in keys], dtype=np.int64)
    P1 = np.array([k[1] for k in keys], dtype=np.int64)
    fulln = (1 << n) - 1
    idx = {s: i for i, s in enumerate(S)}
    one = 1 << idx[fulln]
    reps = [i for i, s in enumerate(S) if s not in (0, fulln) and s < (fulln ^ s)]
    pair = [(1 << i, 1 << idx[fulln ^ S[i]]) for i in reps]
    out = {}
    for bits in range(1 << len(reps)):
        F1 = one
        for j, (x, y) in enumerate(pair):
            F1 |= x if (bits >> j) & 1 else y
        F0 = full ^ F1
        if (F0, F1) in ties:
            continue
        ok = ((P0 & F1) == 0) & ((P1 & F0) == 0)
        if not ok.any():
            continue
        Q = np.unique((P0 | P1)[ok])
        if int(np.bitwise_or.reduce(Q)) != full:
            continue
        found = None
        if (Q == full).any():
            found = 1
        else:
            pairs = (Q[:, None] | Q[None, :]) == full
            if pairs.any():
                found = 2
            else:
                for i in range(len(Q)):
                    R = Q[i] | Q[i + 1:]
                    if (((R[:, None] | Q[None, :]) == full)).any():
                        found = 3
                        break
        if found:
            out[(F0, F1)] = found
    return out


def free_subs(S, n):
    """Distinct subdivisions B(u, p, v) on any pair differing in exactly two states."""
    O, Z, full = M.cols(S, n)
    ties = {(Z[u], O[u]) for u in range(n)}
    out = {}
    for u, v in itertools.combinations(range(n), 2):
        eq = (O[u] & O[v]) | (Z[u] & Z[v])
        if pc(full ^ eq) != 2:
            continue
        a0, a1 = full ^ (O[u] & O[v]), full ^ (Z[u] & Z[v])
        if (a0, a1) not in ties:
            out.setdefault((a0, a1), ((u, n, v),))
    return out


def covered(F0, F1, pins, full):
    """Whether the function (0 on the states of F0, 1 on F1) is forced by at most three of the single-knot pins (pin0, pin1):
    some at most three pins consistent with it cover every state.  Only the largest consistent pins are needed."""
    Q = {p0 | p1 for p0, p1 in pins if not (p0 & F1) and not (p1 & F0)}
    acc = 0
    for q in Q:
        acc |= q
    if acc != full:
        return False
    Q = sorted(Q, key=pc, reverse=True)
    top = []
    for q in Q:
        if not any((q | t) == t for t in top):
            top.append(q)
    for i, q in enumerate(top):
        if q == full:
            return True
        for j in range(i, len(top)):
            r = q | top[j]
            if r == full:
                return True
            need = full ^ r
            if any((t & need) == need for t in top[j:]):
                return True
    return False


def chains_of(S, n):
    """For a base whose crossing graph is connected and bipartite with a crossing: each part's splits with sides chosen nested,
    as lists of 1-sets (masks over the distinctions) from smallest to largest; else None."""
    full = (1 << n) - 1
    sp = sorted({min(s, full ^ s) for s in S if s not in (0, full)})

    def cr(a, b):
        return bool(a & b and a & (full ^ b) and (full ^ a) & b and (full ^ a) & (full ^ b))
    Gc = nx.Graph()
    Gc.add_nodes_from(range(len(sp)))
    Gc.add_edges_from((i, j) for i, j in itertools.combinations(range(len(sp)), 2) if cr(sp[i], sp[j]))
    if Gc.number_of_edges() == 0 or not nx.is_connected(Gc) or not nx.is_bipartite(Gc):
        return None
    X, Y = nx.bipartite.sets(Gc)
    out = []
    for part in (sorted(X), sorted(Y)):
        best = None
        for z in range(n):
            sides = sorted((sp[i] if (sp[i] >> z) & 1 else full ^ sp[i] for i in part), key=pc)
            if all((sides[k] & sides[k + 1]) == sides[k] for k in range(len(sides) - 1)):
                best = sides
                break
        if best is None:
            return None
        out.append(best)
    return out


def free_cells(S, n):
    """The empty cells of the grid of the two chains, as candidate fills (F0, F1) over the states, when the crossing graph is
    connected and bipartite (then every fill that keeps two orders is one: N3 (i)); else None."""
    ch = chains_of(S, n)
    if ch is None:
        return None
    C0, C1 = ch
    full_n = (1 << n) - 1

    def cell(x):
        return (sum(1 for T in C0 if not (T >> x) & 1), sum(1 for T in C1 if not (T >> x) & 1))
    filled = {cell(x) for x in range(n)}
    out = []
    for i in range(len(C0) + 1):
        for j in range(len(C1) + 1):
            if (i, j) in filled:
                continue
            # the new distinction lies in a chosen side T_k (k counted from 1) of a chain exactly when k > its coordinate
            inside = {T: k >= i for k, T in enumerate(C0)}
            inside.update({T: k >= j for k, T in enumerate(C1)})
            F1 = 0
            for idx, s in enumerate(S):
                if s == full_n:
                    val = 1
                elif s == 0:
                    val = 0
                elif s in inside:
                    val = int(inside[s])
                else:
                    val = int(not inside[full_n ^ s])
                F1 |= val << idx
            out.append((F1, (i, j)))
    return out


def free_two_fills(S, n):
    """The fills (by one to three knots on any old pairs) after which the base has two orders, as {(a0, a1): cell or count}."""
    N = len(S)
    full = (1 << N) - 1
    cells = free_cells(S, n)
    if cells is None:
        if N >= 63:
            raise RuntimeError("free fills: crossing graph not connected and too many states for the full enumeration")
        zero = free_zero(S, n)
        return {k: v for k, v in zero.items() if two(M.apply(S, n, *k), n + 1)}
    seen, O, Z, _ = free_masks(S, n)
    ties = {(Z[u], O[u]) for u in range(n)}
    out = {}
    for F1, c in cells:
        F0 = full ^ F1
        if (F0, F1) in ties or not covered(F0, F1, list(seen), full):
            continue
        if two(M.apply(S, n, F0, F1), n + 1):
            out[(F0, F1)] = c
    return out


def free_options(S, n):
    good = free_two_fills(S, n)
    info = {"zero_two_ext": len(good)}
    if good:
        return list(good.items()), info
    return list(free_subs(S, n).items()), info


def cc_fills(S, n):
    """CC's fills: the corner certificate {B(x, r, y), B(c, x, r), B(c, y, r)} on any old distinctions where c differs from x on
    exactly one split, from y on exactly one other, and those two splits cross; r is c with both splits changed.  Distinct
    extensions, copies excluded: {(a0, a1): (c, x, y)}."""
    O, Z, full = M.cols(S, n)
    N = len(S)
    fulln = (1 << n) - 1
    ties = {(Z[u], O[u]) for u in range(n)}
    near = {u: [] for u in range(n)}
    for u, v in itertools.combinations(range(n), 2):
        if pc(O[u] ^ O[v]) == 2:
            near[u].append(v)
            near[v].append(u)

    def side(mask):                    # the split, as the normalised mask over distinctions, of the two states in mask
        i = (mask & -mask).bit_length() - 1
        return min(S[i], fulln ^ S[i])

    def cross(a, b):
        return bool(a & b and a & (fulln ^ b) and (fulln ^ a) & b and (fulln ^ a) & (fulln ^ b))
    out = {}
    for c in range(n):
        for x, y in itertools.combinations(near[c], 2):
            t1, t2 = O[c] ^ O[x], O[c] ^ O[y]
            if t1 == t2 or not cross(side(t1), side(t2)):
                continue
            F1 = (O[x] & ~t2) | (O[y] & t2)        # r = x except on t2's states, where r = y
            F1 &= full
            a0, a1 = full ^ F1, F1
            if (a0, a1) not in ties:
                out.setdefault((a0, a1), (c, x, y))
    return out


def cc_options(S, n):
    good = cc_fills(S, n)
    info = {"zero_two_ext": len(good)}
    if good:
        return list(good.items()), info
    return list(free_subs(S, n).items()), info


def free_grow(S, n, nmax, seed_value, rule="NNF"):
    """A labelled run of NNF or CC (uniform over distinct extensions)."""
    opts = free_options if rule == "NNF" else cc_options
    rng = random.Random(seed_value)
    S = tuple(sorted(S))
    trace = [{**reading(S, n), "kind": "start"}]
    while n < nmax:
        ops, info = opts(S, n)
        if not ops:
            trace.append({"n": n + 1, "stopped": "no option", **info})
            break
        (a0, a1), ks = rng.choice(ops)
        S2 = M.apply(S, n, a0, a1)
        cost = len(S2) - len(S)
        S, n = S2, n + 1
        trace.append({**reading(S, n), "kind": "fill" if cost == 0 else "sub", "cost": cost, "options": len(ops), **info})
    return trace


def line_states(n):
    """The line of n: 0, ..., n - 1, presented by its chain bracketing (every bracketing presents it)."""
    return M.base(n, [(0, c, c + 1) for c in range(1, n - 1)])


def square_states():
    """The 2 x 2 pattern: the line of three with its one knot filled."""
    S = M.base(3, [(0, 1, 2)])
    zero = free_zero(S, 3)
    (a0, a1), = list(zero)
    return M.apply(S, 3, a0, a1)
