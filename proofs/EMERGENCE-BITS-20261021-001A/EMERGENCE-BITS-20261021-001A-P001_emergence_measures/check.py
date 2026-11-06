#!/usr/bin/env python3
"""Checks for EMERGENCE-BITS-20261021-001A-P001. The statements are in proof.md.

Notation: R is a nonempty set of points of {0,1}^n. Its pair closure pc(R) is the set of points whose every
two-coordinate projection appears in R. E(R) = log2|pc(R)| - log2|R| (logical emergence). I(R) = H(p*) - log2|R|,
where p* is the maximum-entropy distribution with the two-coordinate marginals of the uniform distribution on R
(statistical emergence).

Checks:
- Theorem 1 (zero set of E). For every relation on n <= 4 bits (15 + 255 + 65,535): E = 0 exactly when R is
  closed under majority.
- Theorem 2 (knots). For n = 3, 4 the knots found from the definition (constrained, every one-coordinate-forgotten
  projection full) are exactly the complements of nonempty independent sets of the n-cube (34 and 742); the
  independent sets of the 5-cube number 254,475. E of a knot is -log2(1 - |Z|/2^n), at most 1, and equal to 1 only
  for the two parity relations; one clause holds log2(8/7).
- Theorem 3 (statistical emergence). For all 255 relations on three bits: the facial closure (the points some
  distribution with R's pair marginals can charge) is computed by exact rational linear programming; I = 0 exactly
  when R is the least set of a pairwise energy (exact feasibility), which happens for 225 relations, 60 of them with
  E > 0; 0 <= I <= E throughout; the Rauh-Kahle-Ay circuit criterion agrees. The knots with I = 0 are the four
  not-all-equal relations, and I of the other knots depends only on |Z| (0.0785, 0.2516, 0.5364, 1). The one-clause
  value is recomputed from its symmetric equation. A sample of 4-bit knots is not facial.
- Theorem 4 (logical capacity). max E is 0, 1 and 4 - log2 5 on 2, 3 and 4 bits, the 4-bit maximizers being the 16
  five-row covering arrays; on 5 bits no relation with at most 5 points exceeds 5 - log2 6, and a 6-row covering
  array of 10 columns reaches n - log2 6 for n = 5..10. The covering numbers CAN(n) follow Kleitman-Spencer and
  Katona, and the inequality used in the proof holds for 6 <= n <= 5000 and every matching size.
- Theorem 5 (statistical capacity). On three bits I <= min(n, |R| - 1) - log2|R| for all relations, and on a random
  sample of 4-bit relations; the 4-bit maximum among relations with all pairs free is below 4 - log2 5. On seven
  bits the sets of 8 points with every pair of coordinates uniform are exactly the 480 cosets of the 30 Fano simplex
  codes, all affine, each with I = E = 4 = 7 - log2 8.
- Theorem 6 (affine relations). For n <= 6 every subspace of F_2^n is enumerated: with all pairs free the largest
  codimension is n - ceil(log2(n+1)); punctured simplex constructions reach it for n <= 15.
- Additivity: E and I add over products of relations on disjoint coordinates (random pairs).

Controls, each of which must be rejected:
- 'every knot hides one bit' (the clause);
- 'statistical emergence vanishes only on two-literal relations';
- 'four rows cover all pairs of four binary columns';
- 'some 8-point set of 7 bits with uniform pairs is not affine';
- 'parity is the least set of a pairwise energy' (the exact feasibility test run on a wrong input).

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


def pair_closure(R, n):
    pairs = {(i, j): {(t[i], t[j]) for t in R} for i, j in combinations(range(n), 2)}
    return [t for t in cube(n) if all((t[i], t[j]) in s for (i, j), s in pairs.items())]


def emergence(R, n):
    return math.log2(len(pair_closure(R, n))) - math.log2(len(R))


def is_knot(R, n):
    if n < 3 or not R or len(R) == 2 ** n:
        return False
    return all(len({t[:d] + t[d + 1:] for t in R}) == 2 ** (n - 1) for d in range(n))


def independent_set_complements(n):
    pts = cube(n)
    out = []
    def rec(k, chosen):
        if k == len(pts):
            if chosen:
                out.append(frozenset(p for p in pts if p not in chosen))
            return
        rec(k + 1, chosen)
        if all(sum(a != b for a, b in zip(pts[k], q)) != 1 for q in chosen):
            rec(k + 1, chosen + [pts[k]])
    rec(0, [])
    return out


def count_independent_sets(n):
    N = 1 << n
    lower = [[v ^ (1 << i) for i in range(n) if v ^ (1 << i) < v] for v in range(N)]
    count = 0
    def rec(v, chosen):
        nonlocal count
        if v == N:
            count += 1
            return
        rec(v + 1, chosen)
        if not any(chosen >> u & 1 for u in lower[v]):
            rec(v + 1, chosen | (1 << v))
    rec(0, 0)
    return count


# ------------------------------------------------------------------ exact linear programming

def simplex(A, b, c=None):
    """Exact two-phase simplex with Bland's rule. Feasibility of A x = b, x >= 0, then maximize c.x if c is given.
    Returns (status, value): status is 'infeasible', 'unbounded' or 'optimal'."""
    m, n = len(A), len(A[0])
    rows = []
    for i in range(m):
        sgn = -1 if b[i] < 0 else 1
        rows.append([F(sgn * v) for v in A[i]] + [F(1) if j == i else F(0) for j in range(m)] + [F(sgn * b[i])])
    basis = [n + i for i in range(m)]
    width = n + m

    def pivot(r, col):
        pv = rows[r][col]
        rows[r] = [v / pv for v in rows[r]]
        for i in range(m):
            if i != r and rows[i][col] != 0:
                f = rows[i][col]
                rows[i] = [x - f * y for x, y in zip(rows[i], rows[r])]
        basis[r] = col

    def optimize(cost, allowed):          # minimize cost.x
        while True:
            enter = None
            for j in allowed:
                red = cost[j] - sum(cost[basis[i]] * rows[i][j] for i in range(m))
                if red < 0:
                    enter = j
                    break
            if enter is None:
                return "optimal"
            ratios = [(rows[i][-1] / rows[i][enter], basis[i], i) for i in range(m) if rows[i][enter] > 0]
            if not ratios:
                return "unbounded"
            pivot(min(ratios)[2], enter)

    optimize([F(0)] * n + [F(1)] * m, list(range(width)))
    if sum(rows[i][-1] for i in range(m) if basis[i] >= n) > 0:
        return "infeasible", None
    for i in range(m):
        if basis[i] >= n:
            col = next((j for j in range(n) if rows[i][j] != 0), None)
            if col is not None:
                pivot(i, col)
    if c is None:
        return "optimal", F(0)
    cost = [-F(v) for v in c] + [F(0)] * m
    status = optimize(cost, list(range(n)))
    if status == "unbounded":
        return "unbounded", None
    x = [F(0)] * n
    for i in range(m):
        if basis[i] < n:
            x[basis[i]] = rows[i][-1]
    return "optimal", sum(F(v) * xi for v, xi in zip(c, x))


def pair_features(t, n):
    return [(i, j, a, b) for i, j in combinations(range(n), 2) for a in (0, 1) for b in (0, 1) if (t[i], t[j]) == (a, b)]


def least_set_of_pairwise_energy(R, n):
    """Is R exactly the set of minimizers of a sum of functions of two coordinates? Exact feasibility of
    E(t) = m on R and E(t) >= m + 1 off R, with E = sum of free pair terms."""
    keys = [(i, j, a, b) for i, j in combinations(range(n), 2) for a in (0, 1) for b in (0, 1)]
    idx = {k: q for q, k in enumerate(keys)}
    out = [t for t in cube(n) if t not in R]
    nk = len(keys)
    width = 2 * nk + 2 + len(out)
    A, b = [], []
    for t in cube(n):
        row = [0] * width
        for k in pair_features(t, n):
            row[idx[k]] += 1
            row[nk + idx[k]] -= 1
        row[2 * nk] -= 1
        row[2 * nk + 1] += 1
        if t in R:
            A.append(row)
            b.append(0)
        else:
            row[2 * nk + 2 + out.index(t)] = -1
            A.append(row)
            b.append(1)
    return simplex(A, b)[0] == "optimal"


def facial_closure(R, n):
    """Points that some distribution with the pair marginals of the uniform distribution on R can charge."""
    pts = cube(n)
    A, b = [], []
    for i, j in combinations(range(n), 2):
        for a in (0, 1):
            for bb in (0, 1):
                A.append([1 if (t[i], t[j]) == (a, bb) else 0 for t in pts])
                b.append(F(sum(1 for t in R if (t[i], t[j]) == (a, bb)), len(R)))
    closure = set(R)
    for k, t in enumerate(pts):
        if t in closure:
            continue
        c = [0] * len(pts)
        c[k] = 1
        status, value = simplex(A, b, c)
        if status == "optimal" and value > 0:
            closure.add(t)
    return closure


def maxent_entropy(R, n, support, iters=3000):
    pts = [t for t in cube(n) if t in support]
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


def statistical_emergence(R, n, iters=3000):
    closure = facial_closure(R, n)
    if closure == set(R):
        return 0.0, closure
    return maxent_entropy(R, n, closure, iters) - math.log2(len(R)), closure


def ipf_full(R, n, iters):
    return maxent_entropy(R, n, set(cube(n)), iters)


# ------------------------------------------------------------------ covering arrays

def can(n):
    """Least number of rows of a binary covering array of strength 2 with n columns (Kleitman-Spencer, Katona)."""
    if n <= 1:
        return 2
    k = 2
    while math.comb(k - 1, (k + 1) // 2) < n:
        k += 1
    return k


def covers_all_pairs(R, n):
    return all(len({(t[i], t[j]) for t in R}) == 4 for i, j in combinations(range(n), 2))


# ------------------------------------------------------------------ the checks

def run():
    checks, controls, failures = {}, {}, []
    rng = random.Random("emergence-bits-measures")

    # Theorem 1: the zero set of E
    zero = {}
    for n in (2, 3, 4):
        pts = cube(n)
        ints = list(range(1 << n))
        maj = [[[(a & b) | (b & c) | (a & c) for c in ints] for b in ints] for a in ints]
        bits = [tuple((v >> (n - 1 - k)) & 1 for k in range(n)) for v in ints]
        agree = total = zeros = 0
        for mask in range(1, 1 << (1 << n)):
            members = [v for v in ints if mask >> v & 1]
            R = {bits[v] for v in members}
            closed = all(mask >> maj[a][b][c] & 1 for a in members for b in members for c in members)
            e0 = len(pair_closure(R, n)) == len(R)
            agree += closed == e0
            zeros += e0
            total += 1
        zero[n] = {"relations": total, "zero_emergence": zeros, "agrees_with_majority_closure": agree}
    checks["theorem_1_zero_set"] = zero
    if not all(v["agrees_with_majority_closure"] == v["relations"] for v in zero.values()):
        failures.append("Theorem 1")

    # Theorem 2: knots as complements of independent sets
    knots = {}
    for n in (3, 4):
        by_def = [frozenset(R) for R in (frozenset(p for k, p in enumerate(cube(n)) if mask >> k & 1)
                                         for mask in range(1, 1 << (1 << n))) if is_knot(R, n)]
        by_ind = independent_set_complements(n)
        ems = {R: emergence(R, n) for R in by_def}
        formula_ok = all(abs(ems[R] + math.log2(1 - (2 ** n - len(R)) / 2 ** n)) < 1e-12 for R in by_def)
        top = [R for R in by_def if abs(ems[R] - 1) < 1e-12]
        parity = [frozenset(t for t in cube(n) if sum(t) % 2 == s) for s in (0, 1)]
        knots[n] = {"knots_by_definition": len(by_def), "complements_of_independent_sets": len(by_ind),
                    "same_sets": set(by_def) == set(by_ind), "formula_holds": formula_ok,
                    "max_emergence": max(ems.values()), "one_bit_knots_are_parity": sorted(map(sorted, top)) == sorted(map(sorted, parity))}
    clause = frozenset(t for t in cube(3) if t != (0, 0, 0))
    checks["theorem_2_knots"] = {"by_size": {str(k): v for k, v in knots.items()},
                                 "independent_sets_of_5_cube": count_independent_sets(5),
                                 "one_clause_emergence": emergence(clause, 3)}
    if not (all(v["same_sets"] and v["formula_holds"] and v["one_bit_knots_are_parity"] for v in knots.values())
            and knots[3]["knots_by_definition"] == 34 and knots[4]["knots_by_definition"] == 742
            and checks["theorem_2_knots"]["independent_sets_of_5_cube"] == 254475
            and abs(emergence(clause, 3) - math.log2(8 / 7)) < 1e-12):
        failures.append("Theorem 2")

    # Theorem 3: statistical emergence on three bits
    pts3 = cube(3)
    evens = {t for t in pts3 if sum(t) % 2 == 0}
    odds = set(pts3) - evens
    rows = []
    for mask in range(1, 256):
        R = frozenset(pts3[k] for k in range(8) if mask >> k & 1)
        I, closure = statistical_emergence(R, 3)
        rows.append({"R": R, "E": emergence(R, 3), "I": I, "least_set": least_set_of_pairwise_energy(R, 3),
                     "closure": closure, "circuit_criterion": (evens <= R) == (odds <= R), "knot": is_knot(R, 3)})
    stat = {
        "relations": len(rows),
        "zero_I_equals_least_set": sum((abs(r["I"]) < 1e-12) == r["least_set"] for r in rows),
        "least_sets": sum(r["least_set"] for r in rows),
        "least_sets_with_positive_E": sum(1 for r in rows if r["least_set"] and r["E"] > 1e-12),
        "circuit_criterion_agrees": sum(r["circuit_criterion"] == r["least_set"] for r in rows),
        "I_between_0_and_E": sum(-1e-12 <= r["I"] <= r["E"] + 1e-9 for r in rows),
        "closure_is_R_or_cube": sum(r["closure"] in (set(r["R"]), set(pts3)) for r in rows),
    }
    silent = sorted(sorted(set(pts3) - r["R"]) for r in rows if r["knot"] and abs(r["I"]) < 1e-12)
    by_z = {}
    for r in rows:
        if r["knot"] and r["I"] > 1e-12:
            z = 8 - len(r["R"])
            by_z.setdefault(z, set()).add(round(r["I"], 6))
    one_parity = all(r["I"] > 1e-12 for r in rows if r["knot"] and (set(pts3) - r["R"] <= evens or set(pts3) - r["R"] <= odds))
    # the clause from its symmetric equation: p*(000)=1/7-b, weight one b, weight two 2/7-b, weight three b,
    # with (1/7-b)(2/7-b)^3 = b^4 (vanishing third difference of log p*)
    lo, hi = 0.0, 1 / 7
    for _ in range(200):
        mid = (lo + hi) / 2
        if (1 / 7 - mid) * (2 / 7 - mid) ** 3 - mid ** 4 > 0:
            lo = mid
        else:
            hi = mid
    b = (lo + hi) / 2
    probs = [1 / 7 - b] + [b] * 3 + [2 / 7 - b] * 3 + [b]
    clause_exact = -sum(p * math.log2(p) for p in probs) - math.log2(7)
    clause_row = next(r for r in rows if r["R"] == clause)
    sample4 = []
    knots4 = independent_set_complements(4)
    for R in rng.sample(knots4, 40):
        sample4.append(least_set_of_pairwise_energy(R, 4))
    stat.update({"silent_knots_excluded_points": [list(map(list, z)) for z in silent],
                 "I_of_other_knots_by_excluded_count": {str(z): sorted(v) for z, v in sorted(by_z.items())},
                 "one_parity_knots_have_positive_I": one_parity,
                 "clause_I_from_equation": clause_exact, "clause_I_from_fitting": clause_row["I"],
                 "sampled_4_bit_knots_that_are_least_sets": sum(sample4), "sampled_4_bit_knots": len(sample4)})
    checks["theorem_3_statistical"] = stat
    nae = sorted(sorted(z) for z in ([(0, 0, 0), (1, 1, 1)], [(0, 0, 1), (1, 1, 0)], [(0, 1, 0), (1, 0, 1)], [(0, 1, 1), (1, 0, 0)]))
    if not (stat["zero_I_equals_least_set"] == 255 and stat["least_sets"] == 225 and stat["least_sets_with_positive_E"] == 60
            and stat["circuit_criterion_agrees"] == 255 and stat["I_between_0_and_E"] == 255
            and stat["closure_is_R_or_cube"] == 255 and silent == nae and one_parity
            and all(len(v) == 1 for v in by_z.values()) and sorted(by_z) == [1, 2, 3, 4]
            and abs(clause_exact - clause_row["I"]) < 1e-6 and sum(sample4) == 0):
        failures.append("Theorem 3")

    # Theorem 4: logical capacity
    cap = {}
    for n in (2, 3, 4):
        pts = cube(n)
        best, maxi = -1.0, []
        for mask in range(1, 1 << (1 << n)):
            R = [pts[k] for k in range(1 << n) if mask >> k & 1]
            e = emergence(R, n)
            if e > best + 1e-12:
                best, maxi = e, [R]
            elif abs(e - best) < 1e-12:
                maxi.append(R)
        cap[n] = {"max_E": best, "formula": n - math.log2(can(n)), "maximizers": len(maxi),
                  "maximizers_are_minimum_covering_arrays": all(len(R) == can(n) and covers_all_pairs(R, n) for R in maxi)}
    pts5 = cube(5)
    pattern_mask = {}
    for i, j in combinations(range(5), 2):
        for a in (0, 1):
            for c in (0, 1):
                pattern_mask[(i, j, a, c)] = sum(1 << k for k, t in enumerate(pts5) if (t[i], t[j]) == (a, c))
    small_best = 0.0
    for k in range(1, 6):
        for R in combinations(pts5, k):
            closure = (1 << 32) - 1
            for i, j in combinations(range(5), 2):
                allowed = 0
                for (a, c) in {(t[i], t[j]) for t in R}:
                    allowed |= pattern_mask[(i, j, a, c)]
                closure &= allowed
            small_best = max(small_best, math.log2(bin(closure).count("1")) - math.log2(k))
    # Kleitman-Spencer columns: the 3-subsets of rows 1..5, each column zero in row 0
    columns = [tuple(1 if r in cols else 0 for r in range(6)) for cols in combinations(range(1, 6), 3)]
    rows6 = [tuple(col[r] for col in columns) for r in range(6)]
    ca_ok = all(covers_all_pairs([row[:n] for row in rows6], n) and len({row[:n] for row in rows6}) == 6
                and abs(emergence({row[:n] for row in rows6}, n) - (n - math.log2(6))) < 1e-12 for n in range(5, 11))
    cans = [can(n) for n in range(5001)]
    bad = [(n, nu) for n in range(6, 5001) for nu in range(1, n // 2 + 1)
           if (0.75 ** nu) * cans[n] > max(cans[max(n - 2 * nu, 1)], 3) + 1e-12]
    growth = all(math.comb(j + 1, (j + 3) // 2) >= 2 * math.comb(j - 1, (j + 1) // 2) for j in range(3, 400))
    cap5 = {"max_E_over_at_most_5_points": small_best, "bound": 5 - math.log2(6)}
    checks["theorem_4_logical_capacity"] = {"exhaustive": {str(k): v for k, v in cap.items()}, "five_bits": cap5,
                                            "six_row_array_reaches_bound_for_5_to_10": ca_ok,
                                            "CAN_values": {str(n): can(n) for n in (2, 3, 4, 5, 10, 11, 15, 16, 35, 36)},
                                            "inequality_failures_6_to_5000": bad, "central_binomial_growth": growth}
    if not (all(abs(v["max_E"] - v["formula"]) < 1e-12 for v in cap.values())
            and cap[3]["maximizers_are_minimum_covering_arrays"] and cap[4]["maximizers_are_minimum_covering_arrays"]
            and cap[4]["maximizers"] == 16 and small_best < cap5["bound"] - 1e-9 and ca_ok and not bad and growth):
        failures.append("Theorem 4")

    # Theorem 5: statistical capacity
    bound_ok3 = all(r["I"] <= min(3, len(r["R"]) - 1) - math.log2(len(r["R"])) + 1e-9 for r in rows)
    pts4 = cube(4)
    sample = []
    for _ in range(60):
        k = rng.randint(2, 12)
        R = frozenset(rng.sample(pts4, k))
        I, _ = statistical_emergence(R, 4, iters=1500)
        sample.append(I <= min(4, k - 1) - math.log2(k) + 1e-6)
    best4 = 0.0
    for k in (5, 6, 7):
        for R in combinations(pts4, k):
            if covers_all_pairs(R, 4):
                h = ipf_full(R, 4, 200) - math.log2(k)
                if h > best4 - 0.02:
                    best4 = max(best4, ipf_full(R, 4, 2500) - math.log2(k))
    w4 = [v for v in product((0, 1), repeat=7) if sum(v) == 4]
    adj = {v: {u for u in w4 if sum(a & c for a, c in zip(u, v)) == 2} for v in w4}
    cliques = []
    def grow(cl, cand):
        if len(cl) == 7:
            cliques.append(cl)
            return
        for u in sorted(cand):
            if cl and u <= cl[-1]:
                continue
            grow(cl + [u], cand & adj[u])
    grow([], set(w4))
    codes = [frozenset([(0,) * 7] + cl) for cl in cliques]
    def uniform_pairs(R):
        for i, j in combinations(range(7), 2):
            counts = {}
            for t in R:
                counts[(t[i], t[j])] = counts.get((t[i], t[j]), 0) + 1
            if sorted(counts.values()) != [2, 2, 2, 2]:
                return False
        return True
    linear = all(all(tuple(a ^ c for a, c in zip(u, v)) in C for u in C for v in C) for C in codes)
    cosets = {frozenset(tuple(a ^ c for a, c in zip(t, s)) for t in C) for C in codes for s in product((0, 1), repeat=7)}
    seven = {"distance_4_cliques": len(cliques), "all_uniform_on_pairs": all(uniform_pairs(C) for C in codes),
             "all_linear": linear, "cosets": len(cosets),
             "E_of_simplex_code": emergence(codes[0], 7), "I_of_simplex_code_from_uniform_pairs": 7 - math.log2(8)}
    checks["theorem_5_statistical_capacity"] = {
        "three_bit_bound_holds": bound_ok3, "four_bit_sample_bound_holds": sum(sample), "four_bit_sample": len(sample),
        "four_bit_max_I_all_pairs_free": best4, "four_bit_bound": 4 - math.log2(5), "seven_bits": seven}
    if not (bound_ok3 and all(sample) and best4 < 4 - math.log2(5) - 0.1 and len(cliques) == 30 and seven["all_uniform_on_pairs"]
            and linear and len(cosets) == 480 and abs(seven["E_of_simplex_code"] - 4) < 1e-12):
        failures.append("Theorem 5")

    # Theorem 6: affine relations
    affine = {}
    for n in range(2, 7):
        vecs = list(product((0, 1), repeat=n))
        seen = {frozenset([(0,) * n])}
        frontier = list(seen)
        while frontier:
            nxt = []
            for L in frontier:
                for v in vecs:
                    if v in L:
                        continue
                    M = frozenset(L | {tuple(a ^ c for a, c in zip(u, v)) for u in L})
                    if M not in seen:
                        seen.add(M)
                        nxt.append(M)
            frontier = nxt
        best = max(n - round(math.log2(len(L))) for L in seen if covers_all_pairs(L, n))
        affine[n] = {"subspaces": len(seen), "max_codimension_with_pairs_free": best,
                     "formula": n - math.ceil(math.log2(n + 1))}
    constructed = {}
    for n in range(3, 16):
        m = math.ceil(math.log2(n + 1))
        columns = [tuple((c >> k) & 1 for k in range(m)) for c in range(1, 2 ** m)][:n]
        rowspace = {tuple(sum(a[k] * col[k] for k in range(m)) % 2 for col in columns) for a in product((0, 1), repeat=m)}
        constructed[n] = covers_all_pairs(rowspace, n) and abs(emergence(rowspace, n) - (n - m)) < 1e-12 if n <= 9 else \
            covers_all_pairs(rowspace, n) and len(rowspace) == 2 ** m
    checks["theorem_6_affine_capacity"] = {"exhaustive": {str(k): v for k, v in affine.items()},
                                           "punctured_simplex_reaches_it": {str(k): v for k, v in constructed.items()}}
    if not (all(v["max_codimension_with_pairs_free"] == v["formula"] for v in affine.values())
            and affine[6]["subspaces"] == 2825 and all(constructed.values())):
        failures.append("Theorem 6")

    # Additivity over products
    add_ok = 0
    trials = 25
    for _ in range(trials):
        R1 = frozenset(rng.sample(cube(2), rng.randint(1, 4)))
        R2 = frozenset(rng.sample(pts3, rng.randint(1, 8)))
        P = frozenset(a + c for a in R1 for c in R2)
        e_ok = abs(emergence(P, 5) - emergence(R1, 2) - emergence(R2, 3)) < 1e-12
        I1, cl1 = statistical_emergence(R1, 2, 500)
        I2, cl2 = statistical_emergence(R2, 3, 2000)
        support = {a + c for a in cl1 for c in cl2}
        IP = maxent_entropy(P, 5, support, 1500) - math.log2(len(P))
        add_ok += e_ok and abs(IP - I1 - I2) < 1e-4
    checks["additivity"] = {"trials": trials, "passed": add_ok}
    if add_ok != trials:
        failures.append("additivity")

    # Controls
    controls["every_knot_hides_one_bit"] = "rejected" if abs(emergence(clause, 3) - 1) > 1e-9 else "accepted"
    controls["statistical_zero_only_on_two_literal_relations"] = (
        "rejected" if stat["least_sets_with_positive_E"] > 0 else "accepted")
    four_rows = any(covers_all_pairs(R, 4) for R in combinations(pts4, 4))
    controls["four_rows_cover_all_pairs_of_four_columns"] = "accepted" if four_rows else "rejected"
    controls["a_non_affine_uniform_8_set_on_7_bits"] = "rejected" if linear and len(cosets) == 480 else "accepted"
    parity3 = frozenset(t for t in pts3 if sum(t) % 2 == 0)
    controls["parity_is_a_least_set_of_a_pairwise_energy"] = (
        "accepted" if least_set_of_pairwise_energy(parity3, 3) else "rejected")
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
