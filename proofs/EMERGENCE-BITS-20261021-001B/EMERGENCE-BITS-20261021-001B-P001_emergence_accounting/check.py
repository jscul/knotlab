#!/usr/bin/env python3
"""Checks for EMERGENCE-BITS-20261021-001B-P001. The statements are in proof.md.

E(R) = log2|pc(R)| - log2|R| is the logical emergence of a relation R on bits (pc: points whose every pair projection
occurs in R). A link is a three-variable knot read as L(h, x, h'): joints h, h' and one spoke x; its transfer for the
spoke value x is the 2x2 table M(x)[h][h'].

Checks:
- Theorem 1 (visible joins). For all 10,404 placements of two three-variable knots sharing one visible distinction,
  every pair of the join is free and E(join) = E(R) + E(S) - log2(1 + bR bS), bR and bS the leanings (mean of +1/-1)
  of the shared distinction. Visible chains of parity knots hold exactly one bit per knot.
- Theorem 2 (forgetting). Forgetting any coordinate of any of the 4,169 majority-closed relations on four bits leaves
  E = 0, as does forgetting witnesses of 300 random systems of two-literal relations. The cyclic gadget of
  {000, 011, 101} (E = log2(4/3), a least set of a pairwise energy, so I = 0) is a least set on all six variables and
  becomes parity on the three visible ones (E = I = 1).
- Theorem 3 (chains and rings). For all 34 knots and all 6 placements of joints (204 links): rings of 2-7 links match
  the formula E = -log2(1 - ((a+b)^m - (a-b)^m)/2) (a, b the shares of identity and swap transfers); a link's
  transfers are all permutations exactly when it is parity; parity chains and rings hold exactly one bit at lengths
  1-12; every other link's chain falls below 0.06 bits by length 12, with consecutive ratio at most 0.81. For all 742
  four-variable knots with joints at the ends, all-permutation transfers occur exactly for parity.
- Theorem 4 (long knots in a law). The conjunction-closed knots on three and four bits exclude either the all-ones
  point alone or only points with one zero, and reach -log2(1 - N/2^N); dually for disjunction. Even parity on four
  and six bits is preserved by minority, both constants and negation, and is a one-bit knot.
- Theorem 5 (networks). For all 204 links on nine small graphs (the cycles of length 3-5, theta(1,2,2), the bowtie,
  K4, the prism, K33 and the cube), and for seven links on the Petersen graph: visible pairs are free on K4; E <= b1,
  with equality exactly for parity; links with a common vacuum hold 0; not-all-equal holds 0 on bipartite graphs;
  emergence is superadditive over edge-disjoint pieces. On 5x7 and 3x5 tori, the recoloured not-all-equal network
  (random implications plus monotone seam clauses) is consistent exactly when the original is, sample by sample.

Controls, each of which must be rejected:
- 'visible joins always add emergence exactly';
- 'forgetting never creates emergence';
- 'every knot link holds one bit per independent cycle';
- 'some link other than parity reaches the cycle rank';
- 'a conjunction-closed knot can exclude two points with two zeros each';
- 'the consistency test accepts an odd parity ring' (the checker on a wrong input).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import math
import random
import sys
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent


# ------------------------------------------------------------------ relations

def cube(n):
    return list(product((0, 1), repeat=n))


def pair_closure_size(R, n):
    pairs = {(i, j): {(t[i], t[j]) for t in R} for i, j in combinations(range(n), 2)}
    return sum(1 for t in cube(n) if all((t[i], t[j]) in s for (i, j), s in pairs.items()))


def emergence(R, n):
    return math.log2(pair_closure_size(R, n)) - math.log2(len(R))


def is_knot(R, n):
    if n < 3 or not R or len(R) == 2 ** n:
        return False
    return all(len({t[:d] + t[d + 1:] for t in R}) == 2 ** (n - 1) for d in range(n))


def knots(n):
    pts = cube(n)
    out = []
    for mask in range(1, 1 << (1 << n)):
        R = frozenset(pts[k] for k in range(1 << n) if mask >> k & 1)
        if is_knot(R, n):
            out.append(R)
    return out


def leaning(R, i):
    return (sum(1 if t[i] else -1 for t in R)) / len(R)


# ------------------------------------------------------------------ exact least-set test (as in the A proof)

def simplex_feasible(A, b):
    m, n = len(A), len(A[0])
    rows = []
    for i in range(m):
        sgn = -1 if b[i] < 0 else 1
        rows.append([F(sgn * v) for v in A[i]] + [F(1) if j == i else F(0) for j in range(m)] + [F(sgn * b[i])])
    basis = [n + i for i in range(m)]
    cost = [F(0)] * n + [F(1)] * m
    while True:
        enter = None
        for j in range(n + m):
            if cost[j] - sum(cost[basis[i]] * rows[i][j] for i in range(m)) < 0:
                enter = j
                break
        if enter is None:
            break
        ratios = [(rows[i][-1] / rows[i][enter], basis[i], i) for i in range(m) if rows[i][enter] > 0]
        r = min(ratios)[2]
        pv = rows[r][enter]
        rows[r] = [v / pv for v in rows[r]]
        for i in range(m):
            if i != r and rows[i][enter] != 0:
                f = rows[i][enter]
                rows[i] = [x - f * y for x, y in zip(rows[i], rows[r])]
        basis[r] = enter
    return sum(rows[i][-1] for i in range(m) if basis[i] >= n) == 0


def least_set_of_pairwise_energy(R, n):
    keys = [(i, j, a, b) for i, j in combinations(range(n), 2) for a in (0, 1) for b in (0, 1)]
    idx = {k: q for q, k in enumerate(keys)}
    out = [t for t in cube(n) if t not in R]
    nk = len(keys)
    width = 2 * nk + 2 + len(out)
    A, b = [], []
    for t in cube(n):
        row = [0] * width
        for i, j in combinations(range(n), 2):
            q = idx[(i, j, t[i], t[j])]
            row[q] += 1
            row[nk + q] -= 1
        row[2 * nk] -= 1
        row[2 * nk + 1] += 1
        if t in R:
            b.append(0)
        else:
            row[2 * nk + 2 + out.index(t)] = -1
            b.append(1)
        A.append(row)
    return simplex_feasible(A, b)


def maxent_entropy(R, n, iters=2000):
    pts = cube(n)
    targets = []
    for i, j in combinations(range(n), 2):
        m = {}
        for t in R:
            m[(t[i], t[j])] = m.get((t[i], t[j]), 0) + 1 / len(R)
        targets.append((i, j, m))
    p = [1 / len(pts)] * len(pts)
    for _ in range(iters):
        for i, j, m in targets:
            cur = {}
            for t, x in zip(pts, p):
                cur[(t[i], t[j])] = cur.get((t[i], t[j]), 0) + x
            p = [x * m.get((t[i], t[j]), 0) / cur[(t[i], t[j])] if cur[(t[i], t[j])] > 0 else 0 for t, x in zip(pts, p)]
    return -sum(x * math.log2(x) for x in p if x > 0)


# ------------------------------------------------------------------ links, chains, rings

I2 = ((1, 0), (0, 1))
S2 = ((0, 1), (1, 0))
J2 = ((1, 1), (1, 1))


def transfers(R, a, b):
    sp = [k for k in range(len(next(iter(R)))) if k not in (a, b)]
    out = []
    for xs in product((0, 1), repeat=len(sp)):
        M = [[0, 0], [0, 0]]
        for t in R:
            if tuple(t[k] for k in sp) == xs:
                M[t[a]][t[b]] = 1
        out.append(tuple(map(tuple, M)))
    return out


def bmul(A, B):
    return tuple(tuple(int(any(A[i][k] and B[k][j] for k in range(2))) for j in range(2)) for i in range(2))


def ring_bruteforce(Ms, m):
    good = 0
    for xs in product(range(len(Ms)), repeat=m):
        P = I2
        for x in xs:
            P = bmul(P, Ms[x])
        good += bool(P[0][0] or P[1][1])
    return m * math.log2(len(Ms)) - math.log2(good)


def ring_formula(Ms, m):
    a = sum(M == I2 for M in Ms) / len(Ms)
    b = sum(M == S2 for M in Ms) / len(Ms)
    return -math.log2(1 - ((a + b) ** m - (a - b) ** m) / 2)


def chain_emergence(Ms, m):
    """Ends visible, inner joints forgotten: a distribution over products, exact."""
    dist = {I2: 1.0}
    for _ in range(m):
        nxt = {}
        for P, w in dist.items():
            for M in Ms:
                Q = bmul(P, M)
                nxt[Q] = nxt.get(Q, 0) + w / len(Ms)
        dist = nxt
    zeros = sum(w * sum(1 for i in range(2) for j in range(2) if P[i][j] == 0) for P, w in dist.items())
    return -math.log2(1 - zeros / 4)


# ------------------------------------------------------------------ networks

def consistent(nv, edges, mats):
    """Limited-backtracking satisfiability for binary relations on bits (Even, Itai and Shamir)."""
    adj = [[] for _ in range(nv)]
    for k, (u, v) in enumerate(edges):
        adj[u].append((v, k, 0))
        adj[v].append((u, k, 1))
    val = [None] * nv

    def propagate(start, a, val):
        val[start] = a
        stack = [start]
        while stack:
            u = stack.pop()
            for w, k, side in adj[u]:
                M = mats[k]
                allowed = [c for c in (0, 1) if (M[val[u]][c] if side == 0 else M[c][val[u]])]
                if val[w] is None:
                    if not allowed:
                        return False
                    if len(allowed) == 1:
                        val[w] = allowed[0]
                        stack.append(w)
                elif val[w] not in allowed:
                    return False
        return True

    for v in range(nv):
        if val[v] is not None:
            continue
        for a in (0, 1):
            trial = list(val)
            if propagate(v, a, trial):
                val = trial
                break
        else:
            return False
    return all(mats[k][val[u]][val[v]] for k, (u, v) in enumerate(edges))


def network_emergence(nv, edges, Ms):
    good = 0
    for xs in product(range(len(Ms)), repeat=len(edges)):
        good += consistent(nv, edges, [Ms[x] for x in xs])
    return len(edges) * math.log2(len(Ms)) - math.log2(good)


def visible_relation(nv, edges, Ms):
    return {xs for xs in product(range(len(Ms)), repeat=len(edges)) if consistent(nv, edges, [Ms[x] for x in xs])}


def cycle(k):
    return k, [(i, (i + 1) % k) for i in range(k)]


def theta(a, b, c):
    edges, nv = [], 2
    for L in (a, b, c):
        prev = 0
        for _ in range(L - 1):
            edges.append((prev, nv))
            prev = nv
            nv += 1
        edges.append((prev, 1))
    return nv, edges


GRAPHS = {
    "C3": cycle(3), "C4": cycle(4), "C5": cycle(5), "theta(1,2,2)": theta(1, 2, 2),
    "bowtie": (5, [(0, 1), (1, 2), (0, 2), (0, 3), (3, 4), (0, 4)]),
    "K4": (4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]),
    "prism": (6, [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5), (0, 3), (1, 4), (2, 5)]),
    "K33": (6, [(i, 3 + j) for i in range(3) for j in range(3)]),
    "cube": (8, [(a, a ^ (1 << i)) for a in range(8) for i in range(3) if a < a ^ (1 << i)]),
}
PETERSEN = (10, [(i, (i + 1) % 5) for i in range(5)] + [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
            + [(i, 5 + i) for i in range(5)])


def bipartite(nv, edges):
    adj = [[] for _ in range(nv)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    col = [None] * nv
    for s in range(nv):
        if col[s] is None:
            col[s] = 0
            stack = [s]
            while stack:
                u = stack.pop()
                for w in adj[u]:
                    if col[w] is None:
                        col[w] = 1 - col[u]
                        stack.append(w)
                    elif col[w] == col[u]:
                        return False
    return True


def cycle_rank(nv, edges):
    parent = list(range(nv))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    comps = nv
    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            comps -= 1
    return len(edges) - nv + comps


def torus(a, b):
    idx = lambda i, j: (i % a) * b + (j % b)
    return a * b, [(idx(i, j), idx(i + 1, j)) for i in range(a) for j in range(b)] + \
        [(idx(i, j), idx(i, j + 1)) for i in range(a) for j in range(b)]


# ------------------------------------------------------------------ the checks

def run():
    checks, controls, failures = {}, {}, []
    rng = random.Random("emergence-bits-accounting")
    K3 = knots(3)
    pts3 = cube(3)
    parity3 = {frozenset(t for t in pts3 if sum(t) % 2 == s) for s in (0, 1)}

    # Theorem 1: visible joins
    placements = formula_ok = pairs_free = nonzero_correction = 0
    for R in K3:
        for S in K3:
            for i in range(3):
                for j in range(3):
                    T = set()
                    for r in R:
                        for s in S:
                            if r[i] == s[j]:
                                T.add(tuple(r[k] for k in range(3) if k != i) + (r[i],) + tuple(s[k] for k in range(3) if k != j))
                    corr = math.log2(1 + leaning(R, i) * leaning(S, j))
                    placements += 1
                    pairs_free += pair_closure_size(T, 5) == 32
                    formula_ok += abs(emergence(T, 5) - (emergence(R, 3) + emergence(S, 3) - corr)) < 1e-9
                    nonzero_correction += abs(corr) > 1e-9
    par = next(iter(parity3))
    chain_bits = []
    for k in range(1, 5):
        n = 1
        Rk = [t for t in cube(1)]
        for _ in range(k):
            Rk = [r + s[1:] for r in Rk for s in par if s[0] == r[-1]]
            n += 2
        chain_bits.append(emergence(set(Rk), n))
    checks["theorem_1_visible_joins"] = {"placements": placements, "pairs_free": pairs_free, "formula_holds": formula_ok,
                                         "placements_with_nonzero_correction": nonzero_correction,
                                         "visible_parity_chains_bits": chain_bits}
    if not (placements == 10404 and pairs_free == placements and formula_ok == placements
            and all(abs(v - (k + 1)) < 1e-12 for k, v in enumerate(chain_bits))):
        failures.append("Theorem 1")

    # Theorem 2: forgetting
    pts4 = cube(4)
    ints = range(16)
    maj = lambda a, b, c: (a & b) | (b & c) | (a & c)
    bits4 = [tuple((v >> (3 - k)) & 1 for k in range(4)) for v in ints]
    closed_count = forget_zero = 0
    for mask in range(1, 1 << 16):
        members = [v for v in ints if mask >> v & 1]
        if all(mask >> maj(a, b, c) & 1 for a in members for b in members for c in members):
            closed_count += 1
            R = [bits4[v] for v in members]
            forget_zero += all(abs(emergence({t[:d] + t[d + 1:] for t in R}, 3)) < 1e-12 for d in range(4))
    binary = [frozenset(s) for s in ({(0, 0), (0, 1), (1, 1)}, {(0, 1), (1, 0)}, {(0, 0), (1, 1)},
                                     {(0, 1), (1, 0), (1, 1)}, {(0, 0), (0, 1), (1, 0)}, {(1, 0), (1, 1)})]
    random_zero = random_tried = 0
    for _ in range(300):
        cons = [(rng.choice(binary), tuple(rng.sample(range(6), 2))) for _ in range(rng.randint(2, 7))]
        sols = [t for t in cube(6) if all((t[u], t[v]) in rel for rel, (u, v) in cons)]
        if not sols:
            continue
        random_tried += 1
        random_zero += abs(emergence({t[3:] for t in sols}, 3)) < 1e-12
    R0 = frozenset({(0, 0, 0), (0, 1, 1), (1, 0, 1)})
    gadget = [t for t in cube(6) if (t[0], t[1], t[3]) in R0 and (t[1], t[2], t[4]) in R0 and (t[2], t[0], t[5]) in R0]
    visible = {t[3:] for t in gadget}
    gad = {"E_of_triple": emergence(R0, 3), "triple_is_least_set": least_set_of_pairwise_energy(R0, 3),
           "whole_system_is_least_set": least_set_of_pairwise_energy(frozenset(gadget), 6),
           "visible_relation": sorted(visible), "visible_is_parity": frozenset(visible) in parity3,
           "visible_E": emergence(visible, 3), "visible_I": maxent_entropy(visible, 3) - math.log2(len(visible))}
    checks["theorem_2_forgetting"] = {"majority_closed_on_four_bits": closed_count, "every_forgetting_has_zero_E": forget_zero,
                                      "random_pairwise_systems": random_tried, "random_projections_with_zero_E": random_zero,
                                      "gadget": gad}
    if not (closed_count == 4169 and forget_zero == closed_count and random_zero == random_tried and random_tried > 200
            and gad["triple_is_least_set"] and gad["whole_system_is_least_set"] and gad["visible_is_parity"]
            and abs(gad["E_of_triple"] - math.log2(4 / 3)) < 1e-12 and abs(gad["visible_E"] - 1) < 1e-12
            and abs(gad["visible_I"] - 1) < 1e-6):
        failures.append("Theorem 2")

    # Theorem 3: chains and rings
    orders = [(0, 1), (0, 2), (1, 2), (1, 0), (2, 0), (2, 1)]
    links = []
    for R in K3:
        for a, b in orders:
            links.append((R, (a, b), transfers(R, a, b)))
    ring_match = ring_cases = perm_iff_parity = 0
    parity_constant = True
    worst_tail, worst_ratio, worst_link = 0.0, 0.0, None
    for R, ab, Ms in links:
        for m in range(2, 8):
            ring_cases += 1
            ring_match += abs(ring_bruteforce(Ms, m) - ring_formula(Ms, m)) < 1e-9
        allperm = all(M in (I2, S2) for M in Ms)
        perm_iff_parity += allperm == (R in parity3)
        chain = [chain_emergence(Ms, m) for m in range(1, 13)]
        rings = [ring_formula(Ms, m) for m in range(1, 13)]
        if R in parity3:
            parity_constant &= all(abs(v - 1) < 1e-12 for v in chain + rings)
        else:
            if chain[-1] > worst_tail:
                worst_tail, worst_link = chain[-1], [list(map(list, M)) for M in Ms]
            if chain[-2] > 0:
                worst_ratio = max(worst_ratio, chain[-1] / chain[-2])
            worst_tail = max(worst_tail, rings[-1])
    # visible pairs of rings of three and four links are free; a ring of two parity links ties its spokes
    ring_pairs_free = True
    for R, ab, Ms in links:
        for m in (3, 4):
            nv, edges = cycle(m)
            V = visible_relation(nv, edges, Ms)
            ring_pairs_free &= all(len({(xs[i], xs[j]) for xs in V}) == 4 for i, j in combinations(range(m), 2))
    par_link = next(l for l in links if l[0] in parity3)[2]
    two_ring = {(x1, x2) for x1 in range(2) for x2 in range(2)
                if any(par_link[x1][h0][h1] and par_link[x2][h1][h0] for h0 in (0, 1) for h1 in (0, 1))}
    two_ring_is_tie = len(two_ring) == 2 and len({x1 for x1, _ in two_ring}) == 2
    # the subsemigroups of the seven no-zero-row-or-column tables that avoid the all-ones table
    tables = [M for M in (tuple(tuple(v[2 * i:2 * i + 2]) for i in range(2)) for v in product((0, 1), repeat=4))
              if all(any(r) for r in M) and all(any(M[i][j] for i in range(2)) for j in range(2))]
    U2, L2 = ((1, 1), (0, 1)), ((1, 0), (1, 1))
    j_free_ok = True
    for mask in range(1, 1 << len(tables)):
        gens = [tables[k] for k in range(len(tables)) if mask >> k & 1]
        sg = set(gens)
        while True:
            new = {bmul(A, B) for A in sg for B in sg} - sg
            if not new:
                break
            sg |= new
        if J2 not in sg:
            j_free_ok &= sg <= {I2, S2} or sg <= {I2, U2} or sg <= {I2, L2}
    K4 = knots(4)
    perm4 = sum(all(M in (I2, S2) for M in transfers(R, 0, 3)) == (len(R) == 8 and all(sum(t) % 2 == sum(next(iter(R))) % 2 for t in R))
                for R in K4)
    checks["theorem_3_chains_rings"] = {"links": len(links), "ring_cases": ring_cases, "ring_formula_matches": ring_match,
                                        "all_permutation_iff_parity": perm_iff_parity, "parity_holds_one_bit_1_to_12": parity_constant,
                                        "largest_non_parity_emergence_at_12": worst_tail, "largest_tail_ratio": worst_ratio,
                                        "slowest_link_transfers": worst_link, "four_variable_knots": len(K4),
                                        "ring_pairs_free_lengths_3_4": ring_pairs_free, "two_link_parity_ring_is_a_tie": two_ring_is_tie,
                                        "tables_without_zero_rows_or_columns": len(tables), "all_ones_free_semigroups_in_three_families": j_free_ok,
                                        "four_variable_all_permutation_iff_parity": perm4}
    if not (ring_match == ring_cases == 1224 and perm_iff_parity == len(links) and parity_constant
            and worst_tail < 0.06 and worst_ratio <= 0.81 and perm4 == 742 and ring_pairs_free and two_ring_is_tie
            and len(tables) == 7 and j_free_ok):
        failures.append("Theorem 3")

    # Theorem 4: long knots in a law
    long = {}
    for n, Kn in ((3, K3), (4, K4)):
        ones = tuple([1] * n)
        near = {tuple(1 - (k == i) for k in range(n)) for i in range(n)}
        zeros = tuple([0] * n)
        near0 = {tuple(int(k == i) for k in range(n)) for i in range(n)}
        def closed(R, op):
            return all(tuple(op(x, y) for x, y in zip(r, s)) in R for r in R for s in R)
        conj = [R for R in Kn if closed(R, lambda x, y: x & y)]
        disj = [R for R in Kn if closed(R, lambda x, y: x | y)]
        conj_shape = all((set(cube(n)) - R) == {ones} or (set(cube(n)) - R) <= near for R in conj)
        disj_shape = all((set(cube(n)) - R) == {zeros} or (set(cube(n)) - R) <= near0 for R in disj)
        bound = -math.log2(1 - n / 2 ** n)
        long[n] = {"conjunction_closed_knots": len(conj), "disjunction_closed_knots": len(disj),
                   "conjunction_shape": conj_shape, "disjunction_shape": disj_shape,
                   "max_E": max(emergence(R, n) for R in conj + disj), "bound": bound}
    even = {}
    for n in (4, 6):
        P = frozenset(t for t in cube(n) if sum(t) % 2 == 0)
        minority = all(tuple(x ^ y ^ z for x, y, z in zip(r, s, u)) in P for r in P for s in P for u in P)
        consts = (tuple([0] * n) in P) and (tuple([1] * n) in P)
        negation = all(tuple(1 - x for x in r) in P for r in P)
        even[n] = {"preserved_by_minority": minority, "contains_both_constants": consts, "closed_under_negation": negation,
                   "knot": is_knot(P, n), "E": emergence(P, n)}
    checks["theorem_4_long_knots"] = {"by_size": {str(k): v for k, v in long.items()},
                                      "even_parity": {str(k): v for k, v in even.items()}}
    if not (all(v["conjunction_shape"] and v["disjunction_shape"] and abs(v["max_E"] - v["bound"]) < 1e-12 for v in long.values())
            and all(all(v[k] for k in ("preserved_by_minority", "contains_both_constants", "closed_under_negation", "knot"))
                    and abs(v["E"] - 1) < 1e-12 for v in even.values())):
        failures.append("Theorem 4")

    # Theorem 5: networks with hidden joints
    rows = {}
    bound_ok = equality_iff_parity = vacuum_zero = nae_bip_zero = 0
    cases = vacuum_cases = nae_bip_cases = 0
    NAE = frozenset(t for t in pts3 if len(set(t)) == 2)
    for name, (nv, edges) in GRAPHS.items():
        b1 = cycle_rank(nv, edges)
        for R, ab, Ms in links:
            e = network_emergence(nv, edges, Ms)
            cases += 1
            bound_ok += e <= b1 + 1e-9
            equality_iff_parity += (abs(e - b1) < 1e-9) == (R in parity3)
            vac = any(all(M[c][c] for M in Ms) for c in (0, 1))
            if vac:
                vacuum_cases += 1
                vacuum_zero += abs(e) < 1e-12
            if R == NAE and bipartite(nv, edges):
                nae_bip_cases += 1
                nae_bip_zero += abs(e) < 1e-12
            if ab == (0, 2) and (R in parity3 or R == NAE):
                rows.setdefault(name, {})["parity" if R in parity3 else "not-all-equal"] = round(e, 4)
        rows.setdefault(name, {})["b1"] = b1
    non_vacuum_links = sum(1 for R, ab, Ms in links if not any(all(M[c][c] for M in Ms) for c in (0, 1)))
    reps = {"parity": next(l for l in links if l[0] in parity3 and l[1] == (0, 2)),
            "not-all-equal": next(l for l in links if l[0] == NAE and l[1] == (0, 2)),
            "swap or order": next(l for l in links if set(l[2]) == {S2, ((1, 1), (0, 1))})}
    pet = {k: round(network_emergence(*PETERSEN, l[2]), 4) for k, l in reps.items()}
    pet_b1 = cycle_rank(*PETERSEN)
    # visible pairs free on K4 for every link
    nvk, ek = GRAPHS["K4"]
    pairs_free_K4 = all(all(len({(xs[i], xs[j]) for xs in visible_relation(nvk, ek, Ms)}) == 4 for i, j in combinations(range(6), 2))
                        for R, ab, Ms in links)
    # superadditivity over edge-disjoint pieces
    so = reps["swap or order"][2]
    nae = reps["not-all-equal"][2]
    two_bowties = (9, [(0, 1), (1, 2), (0, 2), (0, 3), (3, 4), (0, 4), (0, 5), (5, 6), (0, 6), (0, 7), (7, 8), (0, 8)])
    sup = {"bowtie_vs_two_triangles_swap_or_order": (network_emergence(*GRAPHS["bowtie"], so), 2 * network_emergence(*GRAPHS["C3"], so)),
           "two_bowties_vs_bowtie_not_all_equal": (network_emergence(*two_bowties, nae), 2 * network_emergence(*GRAPHS["bowtie"], nae))}
    sup_ok = all(a >= b - 1e-9 for a, b in sup.values())
    # recolouring on tori
    gauge = {}
    for a, b, samples in ((5, 7, 300), (3, 5, 300)):
        nv, edges = torus(a, b)
        g = [((v // b) + (v % b)) % 2 for v in range(nv)]
        agree = 0
        forms_ok = True
        for _ in range(samples):
            x = [rng.randrange(2) for _ in edges]
            direct = consistent(nv, edges, [nae[xe] for xe in x])
            mats = []
            for (u, v), xe in zip(edges, x):
                M = tuple(tuple(int(not ((tu ^ g[u]) == (tv ^ g[v]) == xe)) for tv in (0, 1)) for tu in (0, 1))
                seam = g[u] == g[v]
                if seam:
                    forms_ok &= M in (((0, 1), (1, 1)), ((1, 1), (1, 0)))
                else:
                    forms_ok &= M in (((1, 0), (1, 1)), ((1, 1), (0, 1)))
                mats.append(M)
            agree += direct == consistent(nv, edges, mats)
        gauge[f"{a}x{b}"] = {"samples": samples, "agree": agree, "every_edge_has_the_stated_form": forms_ok}
    checks["theorem_5_networks"] = {
        "cases": cases, "bound_holds": bound_ok, "equality_exactly_for_parity": equality_iff_parity,
        "vacuum_cases": vacuum_cases, "vacuum_zero": vacuum_zero, "non_vacuum_links": non_vacuum_links,
        "not_all_equal_bipartite_cases": nae_bip_cases, "not_all_equal_bipartite_zero": nae_bip_zero,
        "table": rows, "petersen": pet, "petersen_b1": pet_b1, "visible_pairs_free_on_K4_all_links": pairs_free_K4,
        "superadditivity": {k: [round(v[0], 6), round(v[1], 6)] for k, v in sup.items()}, "torus_recolouring": gauge}
    if not (bound_ok == cases and equality_iff_parity == cases and vacuum_zero == vacuum_cases and nae_bip_zero == nae_bip_cases
            and nae_bip_cases > 0 and abs(pet["parity"] - pet_b1) < 1e-9 and pet["swap or order"] < pet_b1 and pairs_free_K4
            and sup_ok and all(v["agree"] == v["samples"] and v["every_edge_has_the_stated_form"] for v in gauge.values())):
        failures.append("Theorem 5")

    # Controls
    controls["visible_joins_always_add_exactly"] = "rejected" if nonzero_correction > 0 else "accepted"
    controls["forgetting_never_creates_emergence"] = "rejected" if gad["visible_E"] > gad["E_of_triple"] else "accepted"
    nae_c3 = network_emergence(*GRAPHS["C3"], nae)
    controls["every_knot_link_holds_one_bit_per_cycle"] = "rejected" if nae_c3 < 1 - 1e-9 else "accepted"
    controls["some_non_parity_link_reaches_the_cycle_rank"] = "rejected" if equality_iff_parity == cases else "accepted"
    two_zero_points = frozenset(t for t in cube(4) if t not in {(0, 0, 1, 1), (1, 1, 0, 0)})
    conj_ok = all(tuple(x & y for x, y in zip(r, s)) in two_zero_points for r in two_zero_points for s in two_zero_points)
    controls["conjunction_closed_knot_excluding_two_points_with_two_zeros"] = (
        "accepted" if conj_ok and is_knot(two_zero_points, 4) else "rejected")
    odd_ring = consistent(3, [(0, 1), (1, 2), (2, 0)], [S2, S2, S2])
    controls["consistency_test_accepts_an_odd_parity_ring"] = "accepted" if odd_ring else "rejected"
    if any(v != "rejected" for v in controls.values()):
        failures.append("controls")
    return checks, controls, failures


def main() -> int:
    write = "--write" in sys.argv[1:]
    checks, controls, failures = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not failures else "failed", "claim": manifest["claim"],
        "foundation_contract": manifest["foundation_contract"], "semantic_domains": manifest["semantic_domains"],
        "evidence_modes": manifest["evidence_modes"], "thesis_alignment": manifest["thesis_alignment"],
        "safe_conclusions": manifest["safe_to_conclude"], "checks": checks, "controls": controls, "failures": failures,
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n"
    if write:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: failures {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
