#!/usr/bin/env python3
"""Check SOS-SIZE-20261020-001B-P001: tangles give Sherali-Adams and sum-of-squares pseudo-expectations for Tseitin.

For each declared graph G with an odd charge, the check computes the carving width cvw(G) exactly and finds, by
exhaustive search, a tangle of order cvw(G) of the cut function. At degree D = cvw(G) - 1 it builds the functional of
proof.md, in the coordinates y = 1 - 2x:
    E[y_F] = s_X  if F = delta(X) and X is the tangle's small side,   E[y_F] = 0  if F is not a cut.
It then verifies, exactly and over every monomial up to the stated degrees:
  1. E[1] = 1;
  2. the ideal constraints of three encodings: the standard binomial y_{E(v)} - s_v, the balanced binomial
     y_{A_v} - s_v y_{B_v}, and the clause encoding (the indicators of the violating assignments of E(v));
  3. Sherali-Adams nonnegativity: on every edge set S with |S| <= D, the Walsh-Hadamard transform of T -> E[y_T]
     is nonnegative, so every junta of degree <= D has nonnegative value;
  4. sum-of-squares positivity: the moment matrix on the monomials of degree <= floor(D/2) is positive semidefinite,
     by exact symmetric elimination over the rationals.
Instances include restricted grids: the four edges of one non-corner face are set at random, as in the cell
restriction of CELL-SIZE-20261020-001B-P001, and the charges absorb the assigned values. Balanced constraints at
vertices of degree above D lie outside the theorem's hypothesis and are reported separately. Controls: flipping the
orientation of one small set (one with at least two vertices where there is one) breaks some check; and on a hub
joined to two copies of K4 (maximum degree = cvw) the tangle breaks a balanced constraint at the hub only.

The Graph class, carving() and find_tangle() are copied from PC-DEGREE-20261020-001B-P001's check.py.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import random
import sys
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent


def popcount(x: int) -> int:
    return bin(x).count("1")


class Graph:
    def __init__(self, edges):
        self.edges = [tuple(e) for e in edges]
        self.n = 1 + max(max(e) for e in self.edges)
        self.m = len(self.edges)
        self.star = [0] * self.n
        self.nbr = [0] * self.n
        for i, (a, b) in enumerate(self.edges):
            self.star[a] |= 1 << i
            self.star[b] |= 1 << i
            self.nbr[a] |= 1 << b
            self.nbr[b] |= 1 << a
        self.deg = [popcount(s) for s in self.star]
        self.maxdeg = max(self.deg)
        self.full = (1 << self.n) - 1

    def cut(self, U: int) -> int:
        return sum(1 << i for i, (a, b) in enumerate(self.edges) if (U >> a & 1) != (U >> b & 1))

    def balanced(self, v: int) -> tuple[int, int]:
        bits = [i for i in range(self.m) if self.star[v] >> i & 1]
        A = sum(1 << i for i in bits[:(len(bits) + 1) // 2])
        return A, self.star[v] ^ A


def carving(g: Graph):
    """Return (cvw, tree) with tree a nested tuple of vertex sets: leaves are ints (vertex bitmasks)."""
    cut = [0] * (1 << g.n)
    for S in range(1, 1 << g.n):
        v = (S & -S).bit_length() - 1
        R = S ^ (1 << v)
        cut[S] = cut[R] + g.deg[v] - 2 * popcount(g.nbr[v] & R)
    big = 10 ** 9
    best, split = [big] * (1 << g.n), [0] * (1 << g.n)
    for v in range(g.n):
        best[1 << v] = cut[1 << v]
    for S in sorted(range(1, g.full + 1), key=popcount):
        if popcount(S) < 2:
            continue
        low = S & -S
        b, arg = big, 0
        sub = (S - 1) & S
        while sub:
            if sub & low:
                val = max(best[sub], best[S ^ sub])
                if val < b:
                    b, arg = val, sub
            sub = (sub - 1) & S
        best[S], split[S] = max(cut[S], b), arg
    root = min((S for S in range(1, g.full) if S & 1), key=lambda S: max(best[S], best[g.full ^ S]))
    width = max(best[root], best[g.full ^ root])

    def tree(S):
        return S if popcount(S) == 1 else (S, tree(split[S]), tree(S ^ split[S]))

    return width, tree(root), tree(g.full ^ root)


def find_tangle(g: Graph, k: int, drop_t2=False):
    """A tangle of order k+1 of the cut function: small sides for every X with |cut(X)| <= k, no three small
    sides covering V (T2), and V minus a vertex never small (T3). Exhaustive backtracking; None if none."""
    full = g.full
    pairs = []
    for X in range(full + 1):
        Y = full ^ X
        if X < Y and popcount(g.cut(X)) <= k:
            pairs.append((X, Y))
    pairs.sort(key=lambda xy: min(popcount(xy[0]), popcount(xy[1])))
    small = []

    def ok(S):
        if S == full:
            return False
        if popcount(S) == g.n - 1:                                    # T3
            return False
        if drop_t2:
            return True
        members = small + [S]
        for Y in members:
            if (S | Y) == full:
                return False
            for Z in members:
                if (S | Y | Z) == full:
                    return False
        return True

    def search(i):
        if i == len(pairs):
            return True
        X, Y = pairs[i]
        first, second = (X, Y) if popcount(X) <= popcount(Y) else (Y, X)
        for S in (first, second):
            if ok(S):
                small.append(S)
                if search(i + 1):
                    return True
                small.pop()
        return False

    return set(small) if search(0) else None


# ---------------------------------------------------------------- instances

def grid(a, b):
    E = []
    for r in range(a):
        for c in range(b):
            if c + 1 < b:
                E.append((r * b + c, r * b + c + 1))
            if r + 1 < a:
                E.append((r * b + c, (r + 1) * b + c))
    return E


def grid3d(a, b, c):
    idx = {(i, j, k): (i * b + j) * c + k for i in range(a) for j in range(b) for k in range(c)}
    E = []
    for (i, j, k), u in idx.items():
        for di, dj, dk in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            w = idx.get((i + di, j + dj, k + dk))
            if w is not None:
                E.append((u, w))
    return E


def restricted_grid(a, b, face, rng):
    """Remove the four edges of the unit face with top-left corner `face`; return (edges, odd vertex mask) where the
    charge starts odd at vertex 0 and absorbs uniformly random values on the removed edges."""
    r, c = face
    corners = [r * b + c, r * b + c + 1, (r + 1) * b + c, (r + 1) * b + c + 1]
    removed = {tuple(sorted(e)) for e in [(corners[0], corners[1]), (corners[2], corners[3]), (corners[0], corners[2]),
                                         (corners[1], corners[3])]}
    edges = [e for e in grid(a, b) if tuple(sorted(e)) not in removed]
    odd = 1
    for u, v in sorted(removed):
        if rng.randrange(2):
            odd ^= (1 << u) | (1 << v)
    return edges, odd


CUBIC = {
    "K33": [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 4), (2, 5), (3, 4), (3, 5)],
    "prism": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 5), (3, 4), (3, 5), (4, 5)],
    "cube": [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 4), (2, 6), (3, 5), (3, 6), (4, 7), (5, 7), (6, 7)],
    "wagner": [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 4), (2, 6), (3, 5), (3, 7), (4, 7), (5, 6), (6, 7)],
    "petersen": [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4), (0, 5), (1, 6), (2, 7), (3, 8), (4, 9), (5, 7), (7, 9),
                 (6, 9), (6, 8), (5, 8)],
}


# ---------------------------------------------------------------- the pseudo-expectation and its checks

class PseudoExpectation:
    def __init__(self, g: Graph, small, odd: int, D: int):
        self.g, self.D, self.odd = g, D, odd
        self.side = {}
        for X in small:
            F = g.cut(X)
            if popcount(F) <= D:
                assert F not in self.side
                self.side[F] = X

    def s(self, X: int) -> int:
        return -1 if popcount(X & self.odd) % 2 else 1

    def E(self, F: int) -> int:
        assert popcount(F) <= self.D
        X = self.side.get(F)
        return 0 if X is None else self.s(X)


def subsets(indices, r):
    for j in range(r + 1):
        for comb in combinations(indices, j):
            yield sum(1 << i for i in comb)


def check_ideal(pe: PseudoExpectation):
    """Ideal constraints. Balanced constraints at a vertex of degree above D are outside Theorem 1's hypothesis and are
    counted separately ("balanced_beyond_hypothesis")."""
    g, D = pe.g, pe.D
    counts = {"standard": 0, "balanced": 0, "clause": 0, "balanced_beyond_hypothesis": 0}
    bad = {"standard": 0, "balanced": 0, "clause": 0, "balanced_beyond_hypothesis": 0}
    every = list(range(g.m))
    for v in range(g.n):
        sv = -1 if pe.odd >> v & 1 else 1
        star, d = g.star[v], g.deg[v]
        if d <= D:
            for C in subsets(every, D - d):
                counts["standard"] += 1
                if pe.E(C ^ star) != sv * pe.E(C):
                    bad["standard"] += 1
        A, B = g.balanced(v)
        h = popcount(A)
        key = "balanced" if d <= D else "balanced_beyond_hypothesis"
        if h <= D:
            for C in subsets(every, D - h):
                counts[key] += 1
                if pe.E(C ^ A) != sv * pe.E(C ^ B):
                    bad[key] += 1
        if d <= D:
            bits = [i for i in range(g.m) if star >> i & 1]
            others = [i for i in range(g.m) if not star >> i & 1]
            violating = [a for a in product((1, -1), repeat=d) if (-1 if a.count(-1) % 2 else 1) == -sv]
            parts = []
            for T in subsets(bits, d):
                parts.append((T, [i for i, e in enumerate(bits) if T >> e & 1]))
            for C in subsets(others, D - d):
                values = {T: pe.E(C ^ T) for T, _ in parts}
                for a in violating:
                    counts["clause"] += 1
                    total = 0
                    for T, pos in parts:
                        sign = 1
                        for p in pos:
                            sign *= a[p]
                        total += sign * values[T]
                    if total != 0:
                        bad["clause"] += 1
    return counts, bad


def walsh_nonnegative(pe: PseudoExpectation, S_bits):
    k = len(S_bits)
    f = []
    for local in range(1 << k):
        F = 0
        for j in range(k):
            if local >> j & 1:
                F |= 1 << S_bits[j]
        f.append(pe.E(F))
    h = 1
    while h < (1 << k):
        for i in range(0, 1 << k, 2 * h):
            for j in range(i, i + h):
                x, y = f[j], f[j + h]
                f[j], f[j + h] = x + y, x - y
        h *= 2
    return min(f) >= 0


def check_sherali_adams(pe: PseudoExpectation):
    g, D = pe.g, pe.D
    count, bad = 0, 0
    for j in range(D + 1):
        for S in combinations(range(g.m), j):
            count += 1
            if not walsh_nonnegative(pe, list(S)):
                bad += 1
    return count, bad


def psd_exact(M):
    n = len(M)
    A = [[Fraction(x) for x in row] for row in M]
    rank = 0
    for i in range(n):
        p = A[i][i]
        if p < 0:
            return False, rank
        if p == 0:
            if any(A[i][j] != 0 for j in range(i + 1, n)):
                return False, rank
            continue
        rank += 1
        row_i = A[i]
        for j in range(i + 1, n):
            if A[j][i] != 0:
                f = A[j][i] / p
                row_j = A[j]
                for l in range(i, n):
                    if row_i[l] != 0:
                        row_j[l] -= f * row_i[l]
    return True, rank


def rank_one_blocks(pe: PseudoExpectation, monomials):
    """Certify M = sum over classes of sigma sigma^T entrywise, where A ~ B iff E[y_{A xor B}] != 0 and sigma(A) =
    E[y_{A xor R}] for the class representative R. Such an identity proves M positive semidefinite exactly."""
    parent = list(range(len(monomials)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, a in enumerate(monomials):
        for j in range(i + 1, len(monomials)):
            if pe.E(a ^ monomials[j]) != 0:
                parent[find(i)] = find(j)
    rep = {}
    for i in range(len(monomials)):
        rep.setdefault(find(i), i)
    sigma = [pe.E(monomials[i] ^ monomials[rep[find(i)]]) for i in range(len(monomials))]
    for i, a in enumerate(monomials):
        for j, b in enumerate(monomials):
            want = sigma[i] * sigma[j] if find(i) == find(j) else 0
            if pe.E(a ^ b) != want:
                return False, len(rep)
    return True, len(rep)


def check_sos(pe: PseudoExpectation, ldl_cap=150):
    half = pe.D // 2
    monomials = list(subsets(range(pe.g.m), half))
    certified, classes = rank_one_blocks(pe, monomials)
    row = {"monomials": len(monomials), "rank_one_certificate": certified, "classes": classes}
    ok = certified
    if len(monomials) <= ldl_cap:
        M = [[pe.E(a ^ b) for b in monomials] for a in monomials]
        ldl_ok, rank = psd_exact(M)
        row.update({"exact_ldl_psd": ldl_ok, "exact_ldl_rank": rank})
        ok = ok and ldl_ok and rank == classes
    row["psd"] = ok
    return row


def evaluate(pe: PseudoExpectation):
    counts, bad = check_ideal(pe)
    sa_count, sa_bad = check_sherali_adams(pe)
    sos = check_sos(pe)
    return {
        "E_of_1": pe.E(0),
        "ideal_checks": counts,
        "ideal_failures": bad,
        "sherali_adams_sets": sa_count,
        "sherali_adams_failures": sa_bad,
        "sos": sos,
        "all_hold": pe.E(0) == 1 and not any(v for k, v in bad.items() if k != "balanced_beyond_hypothesis")
                    and sa_bad == 0 and sos["psd"],
    }


def run():
    rng = random.Random(20261020)
    instances = [(name, edges, 1) for name, edges in CUBIC.items()]
    instances += [("K44", [(a, 4 + b) for a in range(4) for b in range(4)], 1),
                  ("K6", [(a, b) for a, b in combinations(range(6), 2)], 1),
                  ("heawood", sorted(tuple(sorted(e)) for e in [(i, (i + 1) % 14) for i in range(14)] +
                                     [(i, (i + 5) % 14) for i in range(0, 14, 2)]), 1),
                  ("grid3x3", grid(3, 3), 1), ("grid2x5", grid(2, 5), 1), ("grid3x4", grid(3, 4), 1),
                  ("grid2x2x3", grid3d(2, 2, 3), 1)]
    for a, b, face in ((3, 4, (0, 1)), (3, 4, (1, 1)), (3, 5, (1, 2))):
        edges, odd = restricted_grid(a, b, face, rng)
        instances.append((f"grid{a}x{b}-minus-face{face[0]}{face[1]}", edges, odd))
    checks, failures, controls = {}, [], {}
    for name, edges, odd in instances:
        g = Graph(edges)
        assert popcount(odd) % 2 == 1
        cvw = carving(g)[0]
        D = cvw - 1
        small = find_tangle(g, D)
        row = {"n": g.n, "m": g.m, "maxdeg": g.maxdeg, "cvw": cvw, "degree_checked": D,
               "tangle_found": small is not None}
        if small is None:
            failures.append(f"{name}: no tangle of order cvw found")
            checks[name] = row
            continue
        row["small_sets"] = len(small)
        pe = PseudoExpectation(g, small, odd, D)
        row.update(evaluate(pe))
        if not row["all_hold"]:
            failures.append(f"{name}: pseudo-expectation check failed")
        if g.n <= 9:
            row["no_tangle_of_order_cvw_plus_1"] = find_tangle(g, cvw) is None
            if not row["no_tangle_of_order_cvw_plus_1"]:
                failures.append(f"{name}: tangle of order cvw+1 found (duality)")
        checks[name] = row
        if name in ("cube", "grid3x3", "petersen"):
            nonempty = [S for S in small if popcount(S) >= 1 and popcount(g.cut(S)) <= D]
            X = min(nonempty, key=lambda S: (popcount(S) < 2, popcount(S), S))
            flipped = (small - {X}) | {g.full ^ X}
            bad = evaluate(PseudoExpectation(g, flipped, odd, D))
            controls[name] = {"flipped_set_size": popcount(X), "all_hold": bad["all_hold"],
                              "ideal_failures": bad["ideal_failures"], "sherali_adams_failures": bad["sherali_adams_failures"],
                              "psd": bad["sos"]["psd"]}
            if bad["all_hold"]:
                failures.append(f"control {name}: flipped orientation passed every check")
    # control: the balanced encoding needs every degree below the tangle order (a hub joined to two copies of K4)
    hub = [(a, b) for a, b in combinations(range(4), 2)] + [(a, b) for a, b in combinations(range(4, 8), 2)] + \
        [(a, 8) for a in range(8)]
    g = Graph(hub)
    cvw = carving(g)[0]
    small = find_tangle(g, cvw - 1)
    counts, bad = check_ideal(PseudoExpectation(g, small, 1, cvw - 1))
    controls["hub_of_two_K4"] = {"maxdeg": g.maxdeg, "cvw": cvw, "both_K4_small": {0b1111, 0b11110000} <= small,
                                 "ideal_failures": bad}
    if not (bad["balanced_beyond_hypothesis"] > 0 and bad["standard"] == bad["clause"] == bad["balanced"] == 0):
        failures.append("control hub_of_two_K4: expected failures only beyond the balanced hypothesis")
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
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if write:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: failures {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
