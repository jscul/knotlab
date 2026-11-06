#!/usr/bin/env python3
"""Replay for "The Nullstellensatz degree of Tseitin formulas".

Standalone: Python 3.8 or later, standard library only. For each declared
connected graph G and the Tseitin CNF T(G, c) with c = 1 at vertex 0 (odd total
charge), encoded as polynomials in the usual way (one degree-3 polynomial per
falsifying assignment of a vertex, plus the Boolean axioms x^2 = x):

  1. widths: cutwidth cw(G), toggle width tgw(G) and its monotone version;
  2. upper bound, over every field: the sweep refutation, an explicit
     Nullstellensatz refutation of degree tgw(G) with integer coefficients,
     checked as a polynomial identity over the integers;
  3. lower bound, over F3, F5 and Q: the closed-form design of degree
     tgw(G) - 1, checked against every axiom multiple of that degree;
  4. characteristic 2: the charge-sum refutation of degree 3, checked over F2;
  5. an independent cross-check: the least degree d at which 1 lies in the span
     of the degree-d axiom multiples, by Gaussian elimination over F2 and F3;
  6. the graph lemmas: peak elimination and uncrossing turn random toggle paths
     of cost k into vertex orderings of cutwidth at most k - 1;
  7. the +-1 encoding (one binomial y_E(v) = (-1)^c(v) per vertex): its degree
     is exactly cw(G) when products are measured after reduction modulo
     y^2 = 1, and lies between tgw(G) and cw(G) + 3 when they are measured
     before reduction;
  8. the treewidth of G and of its line graph, for the Sherali-Adams remark.

Usage: python3 replay.py            (all graphs)
       python3 replay.py --quick    (graphs with at most 12 edges)
Exit status 0 when every check passes. Prints one line per graph and a JSON
summary on the last line.
"""

from __future__ import annotations

import heapq
import json
import random
import sys
from fractions import Fraction
from itertools import combinations

GRAPHS = {
    "K4": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)],
    "prism": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 5), (3, 4), (3, 5), (4, 5)],
    "K33": [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 4), (2, 5), (3, 4), (3, 5)],
    "cubic8-a": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 4), (3, 5), (4, 6), (4, 7), (5, 6), (5, 7), (6, 7)],
    "cubic8-b": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 5), (3, 4), (3, 6), (4, 7), (5, 6), (5, 7), (6, 7)],
    "cubic8-c": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 5), (3, 6), (3, 7), (4, 6), (4, 7), (5, 6), (5, 7)],
    "cube": [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 4), (2, 6), (3, 5), (3, 6), (4, 7), (5, 7), (6, 7)],
    "wagner": [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 4), (2, 6), (3, 5), (3, 7), (4, 7), (5, 6), (6, 7)],
    "cubic10": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 5), (3, 6), (3, 7), (4, 6), (4, 8), (5, 7), (5, 9),
                (6, 8), (7, 9), (8, 9)],
    "petersen": [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4), (0, 5), (1, 6), (2, 7), (3, 8), (4, 9),
                 (5, 7), (7, 9), (6, 9), (6, 8), (5, 8)],
}


class Tseitin:
    def __init__(self, edges, charge=None):
        self.edges = list(edges)
        self.n = 1 + max(max(e) for e in edges)
        self.m = len(edges)
        self.stars = [[i for i, e in enumerate(edges) if v in e] for v in range(self.n)]
        self.star_mask = [sum(1 << i for i in s) for s in self.stars]
        self.charge = charge if charge is not None else [1] + [0] * (self.n - 1)
        self.violating = []                       # per vertex: list of (ones_mask, zeros_mask) on its star
        for v in range(self.n):
            star = self.stars[v]
            out = []
            for bits in range(1 << len(star)):
                values = [(bits >> j) & 1 for j in range(len(star))]
                if sum(values) % 2 != self.charge[v]:
                    ones = sum(1 << e for e, x in zip(star, values) if x)
                    zeros = sum(1 << e for e, x in zip(star, values) if not x)
                    out.append((ones, zeros))
            self.violating.append(out)

    def cut(self, members):
        return sum(1 << i for i, (a, b) in enumerate(self.edges) if ((members >> a) & 1) != ((members >> b) & 1))

    def generator(self, v, beta, T):
        """The polynomial x_T * chi_beta as {monomial mask: integer coefficient}."""
        ones, zeros = beta
        poly = {}
        sub = zeros
        while True:
            mono = T | ones | sub
            poly[mono] = poly.get(mono, 0) + (-1) ** bin(sub).count("1")
            if sub == 0:
                break
            sub = (sub - 1) & zeros
        return poly


def subsets_of_size_at_most(mask, k):
    bits = [i for i in range(mask.bit_length()) if (mask >> i) & 1]
    for size in range(k + 1):
        for chosen in combinations(bits, size):
            yield sum(1 << i for i in chosen)


# ---------------------------------------------------------------- widths

def popcount(x):
    return bin(x).count("1")


def cutwidth(t):
    width = {0: 0}
    for members in range(1, 1 << t.n):
        best = min(width[members ^ (1 << v)] for v in range(t.n) if (members >> v) & 1)
        width[members] = max(popcount(t.cut(members)), best)
    return width[(1 << t.n) - 1]


def treewidth(n, edges):
    """Exact treewidth by dynamic programming over elimination prefixes."""
    adjacency = [0] * n
    for a, b in edges:
        adjacency[a] |= 1 << b
        adjacency[b] |= 1 << a

    def neighbours(mask):
        out = 0
        while mask:
            low = mask & -mask
            out |= adjacency[low.bit_length() - 1]
            mask ^= low
        return out

    def q(S, v):
        """Vertices outside S + v adjacent to the component of v in G[S + v]."""
        component = frontier = 1 << v
        while frontier:
            frontier = neighbours(frontier) & S & ~component
            component |= frontier
        return popcount(neighbours(component) & ~S & ~(1 << v))

    tw = {0: -1}
    for S in sorted(range(1, 1 << n), key=popcount):
        tw[S] = min(max(tw[S ^ (1 << v)], q(S ^ (1 << v), v)) for v in range(n) if (S >> v) & 1)
    return tw[(1 << n) - 1]


def line_graph(edges):
    return [(i, j) for i, j in combinations(range(len(edges)), 2) if set(edges[i]) & set(edges[j])]


def toggle_width(t, monotone=False):
    full = (1 << t.n) - 1
    best, heap = {0: 0}, [(0, 0)]
    while heap:
        cost, members = heapq.heappop(heap)
        if members == full:
            return cost
        if cost > best[members]:
            continue
        cut = t.cut(members)
        for v in range(t.n):
            if monotone and (members >> v) & 1:
                continue
            nxt, step = members ^ (1 << v), max(cost, popcount(cut | t.star_mask[v]))
            if step < best.get(nxt, 1 << 30):
                best[nxt] = step
                heapq.heappush(heap, (step, nxt))
    raise ValueError("graph must be connected")


def toggle_path(t, k):
    start, goal = 0, (1 << t.n) - 1
    previous, queue = {start: None}, [start]
    while queue:
        members = queue.pop(0)
        if members == goal:
            path = [members]
            while previous[path[-1]] is not None:
                path.append(previous[path[-1]])
            return path[::-1]
        cut = t.cut(members)
        for v in range(t.n):
            nxt = members ^ (1 << v)
            if nxt not in previous and popcount(cut | t.star_mask[v]) <= k:
                previous[nxt] = members
                queue.append(nxt)
    return None


# ---------------------------------------------------------------- 2. the sweep refutation (integer coefficients)

def parity_indicator(cut_mask, t_value):
    """Integer multilinear polynomial of [sum of the cut's variables = t_value mod 2]."""
    bits = [i for i in range(cut_mask.bit_length()) if (cut_mask >> i) & 1]
    poly = {}
    for size in range(len(bits) + 1):
        for chosen in combinations(bits, size):
            mono = sum(1 << i for i in chosen)
            # (1 + (-1)^t prod(1 - 2x)) / 2: coefficient of x_A is (-1)^t (-2)^|A| / 2 for A nonempty
            if size == 0:
                coef = 1 if t_value == 0 else 0
            else:
                coef = ((-1) ** t_value) * ((-2) ** size) // 2
            if coef:
                poly[mono] = coef
    return poly


def evaluate(poly, assignment_mask):
    return sum(c for mono, c in poly.items() if mono & assignment_mask == mono)


def sweep_refutation(t, path, skip=None):
    """Coefficients {(v, beta_index, T): integer} of an NS refutation along a toggle path."""
    refutation = {}
    parity = 0
    for number, (before, after) in enumerate(zip(path, path[1:])):
        (v,) = [u for u in range(t.n) if ((before ^ after) >> u) & 1]
        nxt = (parity + t.charge[v]) % 2
        if number == skip:
            parity = nxt
            continue
        bag = t.cut(before) | t.star_mask[v]
        step = {}
        for mono, c in parity_indicator(t.cut(after), nxt).items():
            step[mono] = step.get(mono, 0) + c
        for mono, c in parity_indicator(t.cut(before), parity).items():
            step[mono] = step.get(mono, 0) - c
        rest = bag & ~t.star_mask[v]
        rest_bits = [i for i in range(rest.bit_length()) if (rest >> i) & 1]
        for index, (ones, zeros) in enumerate(t.violating[v]):
            for size in range(len(rest_bits) + 1):
                for chosen in combinations(rest_bits, size):
                    f_rest = sum(1 << i for i in chosen)          # the ones of the assignment on the rest of the bag
                    value = evaluate(step, ones | f_rest)
                    if value == 0:
                        continue
                    zeros_rest = rest & ~f_rest
                    sub = zeros_rest
                    while True:
                        key = (v, index, f_rest | sub)
                        # the refutation is minus the sum of the step polynomials
                        refutation[key] = refutation.get(key, 0) - value * (-1) ** popcount(sub)
                        if sub == 0:
                            break
                        sub = (sub - 1) & zeros_rest
        parity = nxt
    return {k: c for k, c in refutation.items() if c}


def combine(t, coefficients, modulus=None):
    total = {}
    for (v, index, T), c in coefficients.items():
        for mono, a in t.generator(v, t.violating[v][index], T).items():
            total[mono] = total.get(mono, 0) + c * a
    if modulus:
        return {m: c % modulus for m, c in total.items() if c % modulus}
    return {m: c for m, c in total.items() if c}


def refutation_degree(t, coefficients):
    return max(popcount(T) + 3 for (v, index, T) in coefficients)


# ---------------------------------------------------------------- 3. the closed-form design

def design_check(t, k, field):
    """Build the design of degree k from toggle reachability; check it against every axiom multiple of degree <= k."""
    full = (1 << t.n) - 1
    reach, queue = {0}, [0]
    while queue:
        members = queue.pop()
        cut = t.cut(members)
        for v in range(t.n):
            nxt = members ^ (1 << v)
            if nxt not in reach and popcount(cut | t.star_mask[v]) <= k:
                reach.add(nxt)
                queue.append(nxt)
    if full in reach:
        return False, "toggle relations inconsistent: V reachable"
    sign = {}
    for members in reach:
        sign[t.cut(members)] = -1 if sum(t.charge[v] for v in range(t.n) if (members >> v) & 1) % 2 else 1
    cuts = sorted({t.cut(members) for members in range(1 << (t.n - 1))})
    p = {"F3": 3, "F5": 5, "Q": None}[field]
    cache = {}

    def design(W):
        """D(x_W) = z[W, all ones] when the all-ones assignment satisfies every star inside W, else 0."""
        if W in cache:
            return cache[W]
        inside_ok = all(t.charge[v] == len(t.stars[v]) % 2 for v in range(t.n) if t.star_mask[v] & ~W == 0)
        if not inside_ok:
            cache[W] = 0
            return 0
        total = 0
        for gamma in cuts:
            if gamma & ~W == 0 and gamma in sign:
                total += sign[gamma] * (-1) ** popcount(gamma)          # <1_W, gamma> = |gamma|
        size = popcount(W)
        value = Fraction(total, 2 ** size) if p is None else total * pow(2, -size, p) % p
        cache[W] = value
        return value

    if design(0) != 1:
        return False, "D(1) != 1"
    checked = 0
    for v in range(t.n):
        others = ((1 << t.m) - 1) & ~t.star_mask[v]
        for beta in t.violating[v]:
            for T in subsets_of_size_at_most(others, k - 3):
                value = sum(c * design(mono) for mono, c in t.generator(v, beta, T).items())
                if (value % p if p else value) != 0:
                    return False, f"D(x_T chi) != 0 at vertex {v}"
                checked += 1
    return True, checked


# ---------------------------------------------------------------- 4. characteristic 2

def charge_sum_refutation(t):
    return {(v, index, 0): 1 for v in range(t.n) for index in range(len(t.violating[v]))}


# ---------------------------------------------------------------- 5. direct degree by elimination

def direct_degree(t, p, start, stop):
    """Least d in [start, stop] with 1 in the F_p-span of the axiom multiples of degree <= d, else None."""
    pivots = {}
    built = set()

    def reduce(poly):
        poly = dict(poly)
        while poly:
            top = max(poly)
            if top not in pivots:
                return poly
            factor = poly[top]
            for mono, c in pivots[top].items():
                value = (poly.get(mono, 0) - factor * c) % p
                if value:
                    poly[mono] = value
                else:
                    poly.pop(mono, None)
        return poly

    for d in range(start, stop + 1):
        for v in range(t.n):
            others = ((1 << t.m) - 1) & ~t.star_mask[v]
            for index, beta in enumerate(t.violating[v]):
                for T in subsets_of_size_at_most(others, d - 3):
                    if (v, index, T) in built:
                        continue
                    built.add((v, index, T))
                    row = reduce({mono: c % p for mono, c in t.generator(v, beta, T).items() if c % p})
                    if row:
                        top = max(row)
                        inv = pow(row[top], p - 2, p)
                        pivots[top] = {mono: c * inv % p for mono, c in row.items()}
        if not reduce({0: 1}):
            return d
    return None


# ---------------------------------------------------------------- 7. the +-1 encoding

def pm1_degree(t, reduced, stop):
    """Least d <= stop at which the +-1 encoding is refuted, else None.

    With y_e = 1 - 2 x_e, vertex v contributes the binomial y_E(v) - s_v, s_v = (-1)^c(v). Modulo y^2 = 1 the
    product y_A (y_E(v) - s_v) is y_(A ^ E(v)) - s_v y_A, and the reduced multiples of one binomial span exactly
    these two-term relations. Measured after reduction the product has degree max(|A|, |A ^ E(v)|); measured
    before, with y^2 - 1 as axioms, it has degree |A| + deg v. A functional with value 1 at y_0 that kills the
    allowed relations is a signed labelling of the monomials, so 1 lies in their span over a field of
    characteristic other than 2 exactly when the class of y_0 contains a contradiction y = -y. Signed
    union-find decides it."""
    parent, sign, bad = {}, {}, set()

    def find(a):
        path = []
        while parent.get(a, a) != a:
            path.append(a)
            a = parent[a]
        acc = 1
        for node in reversed(path):
            acc *= sign[node]
            sign[node], parent[node] = acc, a
        return a, acc

    def relate(a, b, s):
        """Record value(b) = s * value(a)."""
        ra, sa = find(a)
        rb, sb = find(b)
        if ra == rb:
            if sb != s * sa:
                bad.add(ra)
        else:
            parent[rb], sign[rb] = ra, sb * s * sa
            if rb in bad:
                bad.add(ra)

    signs = [(-1) ** t.charge[v] for v in range(t.n)]
    everything = (1 << t.m) - 1
    for d in range(stop + 1):
        for v in range(t.n):
            size = d if reduced else d - len(t.stars[v])
            if size < 0:
                continue
            for A in subsets_of_size_at_most(everything, size):
                if popcount(A) != size:
                    continue
                B = A ^ t.star_mask[v]
                if reduced and popcount(B) > d:
                    continue
                relate(A, B, signs[v])
        if find(0)[0] in bad:
            return d
    return None


# ---------------------------------------------------------------- 6. graph lemmas on random toggle paths

def random_toggle_path(t, k, rng):
    goal = (1 << t.n) - 1
    for _ in range(200):
        path = [0]
        for _ in range(20 * t.n):
            members = path[-1]
            if members == goal:
                return path
            cut = t.cut(members)
            moves = [v for v in range(t.n) if popcount(cut | t.star_mask[v]) <= k]
            if not moves:
                break
            adds = [v for v in moves if not (members >> v) & 1]
            removes = [v for v in moves if (members >> v) & 1]
            v = rng.choice(removes) if removes and (not adds or rng.random() < 0.3) else rng.choice(adds)
            path.append(members ^ (1 << v))
    return None


def peak_elimination(t, path, k):
    path = list(path)
    while True:
        peak = next((i for i in range(1, len(path) - 1) if popcount(t.cut(path[i])) == k), None)
        if peak is None:
            return path
        before, here, after = path[peak - 1], path[peak], path[peak + 1]
        v, w = (before ^ here).bit_length() - 1, (here ^ after).bit_length() - 1
        if v == w:
            path = path[:peak] + path[peak + 2:]
        else:
            path = path[:peak] + [before ^ (1 << w)] + path[peak + 1:]


def uncross(t, sequence):
    seq, rho = list(sequence), (lambda A: popcount(t.cut(A)))
    changed = True
    while changed:
        changed = False
        for i in range(1, len(seq)):
            a, b = seq[i - 1], seq[i]
            if rho(a | b) < rho(b):
                seq[i], changed = a | b, True
            elif a & ~b:
                seq[i - 1], changed = a & b, True
    return seq


def lemma_check(t, k, rng, attempts=3):
    done = 0
    for _ in range(attempts):
        path = random_toggle_path(t, k, rng)
        if path is None:
            continue
        flat = peak_elimination(t, path, k)
        if any(popcount(t.cut(U)) > k - 1 for U in flat):
            return False, done
        mono = uncross(t, flat)
        if not all(a & ~b == 0 and popcount(b & ~a) <= 1 for a, b in zip(mono, mono[1:])):
            return False, done
        if any(popcount(t.cut(U)) > k - 1 for U in mono) or mono[0] != 0 or mono[-1] != (1 << t.n) - 1:
            return False, done
        done += 1
    return True, done


# ---------------------------------------------------------------- main

def main(argv):
    quick = "--quick" in argv
    rng = random.Random(20261020)
    summary, ok_all = {}, True
    for name, edges in GRAPHS.items():
        if quick and len(edges) > 12:
            continue
        t = Tseitin(edges)
        cw, tgw, mono = cutwidth(t), toggle_width(t), toggle_width(t, monotone=True)
        row = {"vertices": t.n, "edges": t.m, "treewidth": treewidth(t.n, t.edges),
               "line_graph_treewidth": treewidth(t.m, line_graph(t.edges)), "cutwidth": cw, "toggle_width": tgw,
               "monotone_toggle_width": mono}
        checks = {"tgw = monotone = cw + 1": tgw == mono == cw + 1}
        path = toggle_path(t, tgw)
        refutation = sweep_refutation(t, path)
        checks["sweep refutation is 1 over Z"] = combine(t, refutation) == {0: 1}
        checks["sweep refutation has degree tgw"] = refutation_degree(t, refutation) <= tgw
        row["sweep_refutation_terms"] = len(refutation)
        for field in ("F3", "F5", "Q"):
            if field == "Q" and t.m > 12:
                continue
            ok, detail = design_check(t, tgw - 1, field)
            checks[f"design of degree tgw-1 over {field}"] = ok
            row[f"design_{field}_axiom_multiples_checked"] = detail
        checks["charge sum is 1 over F2"] = combine(t, charge_sum_refutation(t), 2) == {0: 1}
        checks["direct F2 degree is 3"] = direct_degree(t, 2, 2, 3) == 3
        direct3 = direct_degree(t, 3, 3, tgw)
        row["direct_F3_degree"] = direct3
        checks["direct F3 degree is tgw"] = direct3 == tgw
        reduced, unreduced = pm1_degree(t, True, cw + 3), pm1_degree(t, False, cw + 3)
        row["pm1_reduced_degree"], row["pm1_unreduced_degree"] = reduced, unreduced
        checks["+-1 degree after reduction is cw"] = reduced == cw
        checks["+-1 degree before reduction is between tgw and cw + 3"] = unreduced is not None and tgw <= unreduced
        ok, done = lemma_check(t, tgw + 1, rng)
        checks["peak elimination and uncrossing"] = ok
        row["lemma_paths"] = done
        # controls: each must come out negative
        even = Tseitin(edges, [1, 1] + [0] * (t.n - 2))
        checks["control: even charge has no F3 refutation up to tgw + 1"] = direct_degree(even, 3, 3, tgw + 1) is None
        checks["control: even charge has no F2 refutation up to tgw + 1"] = direct_degree(even, 2, 3, tgw + 1) is None
        checks["control: the design breaks down at tgw"] = design_check(t, tgw, "F3")[0] is False
        checks["control: even charge has no +-1 refutation at any degree"] = pm1_degree(even, True, t.m) is None
        checks["control: the sweep without one step is not 1"] = combine(t, sweep_refutation(t, path, skip=len(path) // 2)) != {0: 1}
        row["checks"] = checks
        passed = all(checks.values())
        ok_all &= passed
        summary[name] = row
        print(f"{name:9s} n={t.n:2d} m={t.m:2d} tw={row['treewidth']} twL={row['line_graph_treewidth']} cw={cw} "
              f"tgw={tgw} NS_F3={direct3} NS_F2=3 pm1={reduced}/{unreduced} "
              f"{'ok' if passed else 'FAILED ' + str([k for k, v in checks.items() if not v])}", flush=True)
    print(json.dumps({"passed": ok_all, "graphs": summary}, sort_keys=True))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
