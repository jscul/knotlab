#!/usr/bin/env python3
"""Check PC-DEGREE-20261020-001B-P001: polynomial calculus degree of Tseitin formulas is half the carving width.

Executable checks of each step of proof.md on declared instances:

1. Geometry (Lemma 3), exhaustively on ground sets of up to 7 elements and d <= 3: positions of a relation
   with |gamma| <= 2d - 1 form a nonempty connected set; at |gamma| = 2d no position can move; any three sets
   with pairwise differences at most 2d have a common point within d (and the median construction finds it).
2. The closure model (Lemma 1): the label-tracking closure (relations labelled by vertex sets, composing by
   symmetric difference, refutation = a relation labelled V) agrees with plain linear algebra over F3 on
   every connected graph with at most 6 vertices and at most 9 edges, for every degree up to its refutation.
3. The lower bound (Lemma 2) and the cited duality: on every connected graph with at most 6 vertices, every
   cubic graph with at most 8 vertices, K44, Petersen, K6, K45 and K55, for each d with
   ceil(maxdeg/2) <= d <= floor(cvw/2) + 1:
   a tangle of order 2d+1 of the cut function exists (found by exhaustive search) exactly when cvw >= 2d+1;
   when it exists, every label of every relation in the degree-d closure lies on its small side, and the
   closure does not refute.
4. The upper bound (Theorem, part 3): along an optimal carving, an explicit derivation with balanced axioms is
   built and replayed line by line as reduced PC steps (axiom, multiplication by a variable, linear
   combination); every line has degree at most floor(cvw/2) + 1, and it ends in a nonzero constant.
5. The encodings (part 4): for d >= maxdeg the reduced closures of the balanced, standard and clause axioms
   refute at the same degrees; the standard convention needs at most one more.

Controls: a derivation replay with one sign flipped must fail; a tangle search with T2 dropped must find
"tangles" where cvw <= 2d; the closure without translations must not refute K4 at degree 3.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import sys
from collections import deque
from itertools import combinations, permutations
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


# ---------------------------------------------------------------- graphs

def connected(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    seen, todo = {0}, [0]
    while todo:
        for y in adj[todo.pop()] - seen:
            seen.add(y)
            todo.append(y)
    return len(seen) == n


def canonical(n, edges):
    return min(tuple(sorted(tuple(sorted((p[a], p[b]))) for a, b in edges)) for p in permutations(range(n)))


def small_graphs(max_n=6):
    out = []
    for n in range(2, max_n + 1):
        seen = set()
        pairs = list(combinations(range(n), 2))
        for mask in range(1, 1 << len(pairs)):
            edges = [pairs[i] for i in range(len(pairs)) if mask >> i & 1]
            if len(edges) < n - 1 or not connected(n, edges) or 1 + max(max(e) for e in edges) != n:
                continue
            key = canonical(n, edges)
            if key not in seen:
                seen.add(key)
                out.append(list(key))
    return out


CUBIC = {
    "K4": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)],
    "prism": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 5), (3, 4), (3, 5), (4, 5)],
    "K33": [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 4), (2, 5), (3, 4), (3, 5)],
    "cubic8-a": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 4), (3, 5), (4, 6), (4, 7), (5, 6), (5, 7), (6, 7)],
    "cubic8-b": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 5), (3, 4), (3, 6), (4, 7), (5, 6), (5, 7), (6, 7)],
    "cubic8-c": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 5), (3, 6), (3, 7), (4, 6), (4, 7), (5, 6), (5, 7)],
    "cube": [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 4), (2, 6), (3, 5), (3, 6), (4, 7), (5, 7), (6, 7)],
    "wagner": [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 4), (2, 6), (3, 5), (3, 7), (4, 7), (5, 6), (6, 7)],
}
LARGER = {
    "petersen": [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4), (0, 5), (1, 6), (2, 7), (3, 8), (4, 9), (5, 7), (7, 9),
                 (6, 9), (6, 8), (5, 8)],
    "K44": [(a, 4 + b) for a in range(4) for b in range(4)],
    "K45": [(a, 4 + b) for a in range(4) for b in range(5)],
    "K55": [(a, 5 + b) for a in range(5) for b in range(5)],
    "K6": [(a, b) for a, b in combinations(range(6), 2)],
    "heawood": sorted(tuple(sorted(e)) for e in [(i, (i + 1) % 14) for i in range(14)] +
                      [(i, (i + 5) % 14) for i in range(0, 14, 2)]),
}


# ---------------------------------------------------------------- carving width with an optimal carving

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


# ---------------------------------------------------------------- 1. geometry

def positions(m, gamma, d):
    return [A for A in range(1 << m) if popcount(A) <= d and popcount(A ^ gamma) <= d]


def geometry_checks():
    report = {"connected_below_2d": True, "frozen_at_2d": True, "three_point_center": True, "median_center": True,
              "cases": 0}
    for m in range(1, 8):
        for d in range(1, 4):
            for gamma in range(1 << m):
                k = popcount(gamma)
                if k > 2 * d:
                    continue
                P = set(positions(m, gamma, d))
                if k <= 2 * d - 1:
                    start = next(iter(P), None)
                    seen = {start} if start is not None else set()
                    queue = deque(seen)
                    while queue:
                        A = queue.popleft()
                        for e in range(m):
                            B = A ^ (1 << e)
                            if B in P and B not in seen:
                                seen.add(B)
                                queue.append(B)
                    if not P or seen != P:
                        report["connected_below_2d"] = False
                else:
                    if any((A ^ (1 << e)) in P for A in P for e in range(m)):
                        report["frozen_at_2d"] = False
                report["cases"] += 1
    for m in range(1, 7):
        for d in range(1, 4):
            for X1 in range(1 << m):
                for X2 in range(1 << m):
                    if max(popcount(X1), popcount(X2), popcount(X1 ^ X2)) > 2 * d:
                        continue
                    if not any(popcount(P) <= d and popcount(P ^ X1) <= d and popcount(P ^ X2) <= d
                               for P in range(1 << m)):
                        report["three_point_center"] = False
                    if not median_center_ok(X1, X2, d):
                        report["median_center"] = False
    return report


def median_center(X0, X1, X2, d):
    """The construction of proof.md, Lemma 3(b): from the median, step toward the farthest point."""
    M = (X0 & X1) | (X0 & X2) | (X1 & X2)
    legs = sorted(((popcount(X ^ M), i, X) for i, X in enumerate((X0, X1, X2))), reverse=True)
    far, X = legs[0][0], legs[0][2]
    t = max(0, far - d)
    diff = X ^ M
    bits = [i for i in range(diff.bit_length()) if diff >> i & 1][:t]
    return M ^ sum(1 << i for i in bits)


def median_center_ok(X1, X2, d):
    P = median_center(0, X1, X2, d)
    return popcount(P) <= d and popcount(P ^ X1) <= d and popcount(P ^ X2) <= d


# ---------------------------------------------------------------- 2. closures

class LabelClosure:
    """Reduced (or standard) PC closure of a binomial Tseitin system, tracking labels.

    Each relation y_A ~ sign * y_B carries the vertex set U with A xor B = cut(U) and sign (-1)^c(U); labels
    compose by symmetric difference, and a relation labelled V (all vertices) is a contradiction."""

    def __init__(self, g: Graph, d: int, axioms="balanced", convention="R", translate=True):
        self.g, self.d = g, d
        self.parent, self.pot, self.members, self.bad = {}, {}, {}, set()
        need = {"balanced": max((x + 1) // 2 for x in g.deg), "standard": g.maxdeg, "clause": g.maxdeg}[axioms]
        self.writable = need <= d
        if not self.writable:
            return
        for v in range(g.n):
            E, U = g.star[v], 1 << v
            if axioms == "balanced":
                A, B = g.balanced(v)
                self.relate(A, B, U)
            elif axioms == "standard":
                self.relate(0, E, U)
            else:
                sub = E
                while True:
                    self.relate(sub, E ^ sub, U)
                    if sub == 0:
                        break
                    sub = (sub - 1) & E
        if translate:
            self.close(convention)

    def find(self, a):
        path = []
        while self.parent.get(a, a) != a:
            path.append(a)
            a = self.parent[a]
        acc = 0
        for node in reversed(path):
            acc ^= self.pot[node]
            self.pot[node], self.parent[node] = acc, a
        return a, (self.pot[path[0]] if path else 0)

    def relate(self, a, b, U):
        ra, la = self.find(a)
        rb, lb = self.find(b)
        if ra == rb:
            diff = la ^ lb ^ U
            if diff and ra not in self.bad:
                assert diff == self.g.full, "two labels of one pair differ by a proper subset"
                self.bad.add(ra)
                self.members.setdefault(ra, [ra])
                return True
            return False
        ma, mb = self.members.get(ra, [ra]), self.members.get(rb, [rb])
        if len(ma) < len(mb):
            ra, rb, la, lb, ma, mb = rb, ra, lb, la, mb, ma
        self.parent[rb], self.pot[rb] = ra, la ^ lb ^ U
        self.members[ra] = ma + mb
        self.members.pop(rb, None)
        if rb in self.bad:
            self.bad.discard(rb)
            self.bad.add(ra)
        return True

    def mark_bad(self, a):
        ra, _ = self.find(a)
        if ra in self.bad:
            return False
        self.bad.add(ra)
        self.members.setdefault(ra, [ra])
        return True

    def close(self, convention):
        d, m = self.d, self.g.m
        changed = True
        while changed:
            changed = False
            for r in list(self.members):
                if r not in self.members:
                    continue
                M = list(self.members[r])
                isbad = r in self.bad
                if not isbad and len(M) < 2:
                    continue
                lab = None if isbad else {A: self.find(A)[1] for A in M}
                low = [A for A in M if popcount(A) <= d - 1]
                top = [A for A in M if popcount(A) == d] if convention == "R" else []
                for e in range(m):
                    bit = 1 << e
                    elig = low + [A for A in top if A & bit] if top else low
                    if not elig:
                        continue
                    if isbad:
                        for A in elig:
                            changed |= self.mark_bad(A ^ bit)
                    elif len(elig) >= 2:
                        A0 = elig[0]
                        for A in elig[1:]:
                            changed |= self.relate(A0 ^ bit, A ^ bit, lab[A0] ^ lab[A])

    def refuted(self):
        return self.writable and self.find(0)[0] in self.bad

    def labels(self):
        """All labels of relations between members of one class (pairwise), for consistent classes."""
        out = set()
        for r, M in self.members.items():
            if r in self.bad:
                continue
            labs = [self.find(A)[1] for A in M]
            for i in range(len(labs)):
                for j in range(i + 1, len(labs)):
                    out.add(labs[i] ^ labs[j])
        return out


def least(g, axioms, convention, cap):
    for d in range(1, cap + 1):
        if LabelClosure(g, d, axioms, convention).refuted():
            return d
    return None


def linear_algebra_refutes(g: Graph, d: int, p=3) -> bool:
    """Plain PC closure over F_p in the reduced convention with balanced axioms (no binomial structure used)."""
    if max((x + 1) // 2 for x in g.deg) > d:
        return False
    rows = {}                                     # pivot monomial -> row {monomial: coefficient}, echelon form

    def reduce(vec):
        vec = dict(vec)
        while vec:
            top = max(vec)
            if top not in rows:
                return vec
            f = vec[top]
            for mono, c in rows[top].items():
                val = (vec.get(mono, 0) - f * c) % p
                if val:
                    vec[mono] = val
                else:
                    vec.pop(mono, None)
        return vec

    def insert(vec):
        vec = reduce({k: v % p for k, v in vec.items() if v % p})
        if not vec:
            return False
        top = max(vec)
        inv = pow(vec[top], p - 2, p)
        rows[top] = {k: v * inv % p for k, v in vec.items()}
        return True

    for v in range(g.n):
        A, B = g.balanced(v)
        insert({A: 1, B: -(-1) ** (1 if v == 0 else 0)})
    while True:
        grown = False
        basis = list(rows.values())
        for e in range(g.m):
            bit = 1 << e
            eligible = lambda mono: popcount(mono ^ bit) <= d
            # intersect span(basis) with the coordinate subspace of eligible monomials:
            # echelonize with ineligible monomials first, keep rows with no ineligible monomial
            order = lambda mono: (0 if eligible(mono) else 1, mono)
            local = {}

            def lreduce(vec):
                vec = dict(vec)
                while vec:
                    top = max(vec, key=order)
                    if top not in local:
                        return vec
                    f = vec[top]
                    for mono, c in local[top].items():
                        val = (vec.get(mono, 0) - f * c) % p
                        if val:
                            vec[mono] = val
                        else:
                            vec.pop(mono, None)
                return vec

            for row in basis:
                vec = lreduce(row)
                if vec:
                    top = max(vec, key=order)
                    inv = pow(vec[top], p - 2, p)
                    local[top] = {k: c * inv % p for k, c in vec.items()}
            for top, row in list(local.items()):
                if eligible(top):
                    if insert({mono ^ bit: c for mono, c in row.items()}):
                        grown = True
        if 0 in rows and len(rows[0]) == 1:
            return True
        if reduce({0: 1}) == {}:
            return True
        if not grown:
            return False


# ---------------------------------------------------------------- 3. tangles

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


# ---------------------------------------------------------------- 4. explicit carving derivations

class Replay:
    """Lines as {monomial: integer coefficient}; every step is a reduced PC step whose degree is checked."""

    def __init__(self, g: Graph, d: int):
        self.g, self.d, self.max_degree, self.steps, self.ok = g, d, 0, 0, True

    def check(self, line):
        deg = max((popcount(mono) for mono, c in line.items() if c), default=0)
        self.max_degree = max(self.max_degree, deg)
        self.steps += 1
        if deg > self.d:
            self.ok = False
        return line

    def axiom(self, v, flip=False):
        A, B = self.g.balanced(v)
        s = (-1) ** (1 if v == 0 else 0)
        if flip:
            s = -s
        return self.check({A: 1, B: -s})

    def times(self, line, e):
        out = {}
        for mono, c in line.items():
            out[mono ^ (1 << e)] = out.get(mono ^ (1 << e), 0) + c
        return self.check({k: v for k, v in out.items() if v})

    def combine(self, a, x, b, y):
        out = dict((k, a * v) for k, v in x.items())
        for k, v in y.items():
            out[k] = out.get(k, 0) + b * v
        return self.check({k: v for k, v in out.items() if v})


def move(replay, line, source, target, gamma):
    """Translate a binomial relation from position source to position target within S_d(gamma)."""
    d = replay.d
    A = source
    path = []
    for e in range(replay.g.m):                       # leave the elements outside gamma
        if A >> e & 1 and not gamma >> e & 1:
            A ^= 1 << e
            path.append(e)
    tail = []
    T = target
    for e in range(replay.g.m):
        if T >> e & 1 and not gamma >> e & 1:
            T ^= 1 << e
            tail.append(e)
    while A != T:
        if (A & ~T) and popcount(A) - 1 >= popcount(gamma) - d:
            e = ((A & ~T) & -(A & ~T)).bit_length() - 1
        elif (T & ~A) and popcount(A) + 1 <= d:
            e = ((T & ~A) & -(T & ~A)).bit_length() - 1
        else:
            raise AssertionError("stuck: |gamma| = 2d")
        A ^= 1 << e
        path.append(e)
    for e in reversed(tail):
        path.append(e)
    for e in path:
        line = replay.times(line, e)
    return line


def derive(replay, node, flip_leaf=None):
    """Return (line, position P, label U) with line = y_P - sign y_(P xor cut(U))."""
    g = replay.g
    if isinstance(node, int):
        v = node.bit_length() - 1
        line = replay.axiom(v, flip=(v == flip_leaf))
        A, _ = g.balanced(v)
        return line, A, node
    U, left, right = node
    l1, p1, U1 = derive(replay, left, flip_leaf)
    l2, p2, U2 = derive(replay, right, flip_leaf)
    c1, cU = g.cut(U1), g.cut(U)
    P = median_center(0, c1, cU, replay.d)
    l1 = move(replay, l1, p1, P, c1)
    c2 = g.cut(U2)
    l2 = move(replay, l2, p2, P ^ c1, c2)
    # l1 = y_P - s1 y_(P^c1); l2 = y_(P^c1) - s2 y_(P^cU): l1 + s1 l2 = y_P - s1 s2 y_(P^cU)
    s1 = -l1[P ^ c1] if P ^ c1 in l1 else None
    if l1.get(P) != 1:
        l1 = {k: -v for k, v in l1.items()}
        s1 = -l1[P ^ c1]
    if l2.get(P ^ c1) != 1:
        l2 = {k: -v for k, v in l2.items()}
    line = replay.combine(1, l1, s1, l2)
    return line, P, U


def replay_carving(g: Graph, flip_leaf=None):
    cvw, left, right = carving(g)
    d = cvw // 2 + 1
    replay = Replay(g, d)
    l1, p1, U1 = derive(replay, left, flip_leaf)
    l2, p2, U2 = derive(replay, right, flip_leaf)
    gamma = g.cut(U1)
    P = p1
    l2 = move(replay, l2, p2, P, gamma)
    if l1.get(P) != 1:
        l1 = {k: -v for k, v in l1.items()}
    if l2.get(P) != 1:
        l2 = {k: -v for k, v in l2.items()}
    line = replay.combine(1, l1, -1, l2)               # (y_P - s y_Q) - (y_P - s' y_Q) = (s' - s) y_Q
    rest = [mono for mono in line]
    if len(rest) != 1:
        return {"cvw": cvw, "degree_bound": d, "ok": False, "reason": "no single monomial at the root"}
    (Q,) = rest
    for e in range(g.m):
        if Q >> e & 1:
            line = replay.times(line, e)
    constant = line.get(0, 0)
    ends_in_constant = set(line) == {0} and constant % 3 != 0
    return {"cvw": cvw, "degree_bound": d, "max_degree": replay.max_degree, "steps": replay.steps,
            "ok": replay.ok and ends_in_constant and replay.max_degree <= d}


# ---------------------------------------------------------------- run

def run():
    checks, controls = {}, {}
    checks["geometry"] = geometry_checks()

    smalls = small_graphs(6)
    agree, cases = True, 0
    for edges in smalls:
        g = Graph(edges)
        if g.m > 9:
            continue
        top = least(g, "balanced", "R", g.m + 1)
        for d in range(1, (top or g.m) + 1):
            if LabelClosure(g, d).refuted() != linear_algebra_refutes(g, d):
                agree = False
            cases += 1
    checks["closure_matches_linear_algebra"] = {"agree": agree, "graph_degree_cases": cases}

    tangle_rows, tangle_ok, duality_ok = [], True, True
    pool = [("small", e) for e in smalls] + [(name, e) for name, e in CUBIC.items()] + \
        [(name, LARGER[name]) for name in ("K44", "petersen", "K6", "K45", "K55")]
    for name, edges in pool:
        g = Graph(edges)
        if g.n < 3:
            continue
        cvw = carving(g)[0]
        for d in range(max(1, (g.maxdeg + 1) // 2), cvw // 2 + 2):
            T = find_tangle(g, 2 * d)
            exists = T is not None
            if exists != (cvw >= 2 * d + 1):
                duality_ok = False
            if exists:
                closure = LabelClosure(g, d)
                labels = closure.labels()
                if closure.refuted() or not labels <= T:
                    tangle_ok = False
                tangle_rows.append(1)
    checks["tangle_lower_bound"] = {"labels_on_small_side_and_no_refutation": tangle_ok, "tangles_checked": len(tangle_rows)}
    checks["duality_on_small_instances"] = duality_ok

    replays, replay_ok = {}, True
    pool = [("small:" + str(i), e) for i, e in enumerate(smalls) if len(e) >= 2] + list(CUBIC.items()) + \
           list(LARGER.items())
    for name, edges in pool:
        g = Graph(edges)
        if g.n < 2:
            continue
        r = replay_carving(g)
        replay_ok &= r["ok"]
        if not name.startswith("small"):
            replays[name] = r
    checks["carving_derivations"] = {"all_replay": replay_ok, "named": replays,
                                     "graphs": len(pool)}

    enc_ok, conv_ok, rows = True, True, {}
    for name, edges in list(CUBIC.items()) + [("petersen", LARGER["petersen"]), ("K45", LARGER["K45"]),
                                             ("K6", LARGER["K6"])]:
        g = Graph(edges)
        bal = least(g, "balanced", "R", 12)
        std = least(g, "standard", "R", 12)
        cla = least(g, "clause", "R", 12)
        sc = least(g, "clause", "S", 12)
        enc_ok &= std == cla == max(g.maxdeg, bal)
        conv_ok &= max(g.maxdeg, bal) <= sc <= max(g.maxdeg, bal) + 1
        rows[name] = {"PC_bal": bal, "PC_Rstd": std, "PC_Rclause": cla, "PC_SC": sc, "maxdeg": g.maxdeg}
    checks["encodings"] = {"reduced_closures_agree_above_maxdeg": enc_ok, "standard_within_one": conv_ok,
                           "values": rows}

    g = Graph(CUBIC["K4"])
    controls["flipped_sign_replay_fails"] = not replay_carving(g, flip_leaf=1)["ok"]
    controls["tangle_without_T2_found_where_cvw_small"] = find_tangle(g, 2 * 2, drop_t2=True) is not None and \
        find_tangle(g, 2 * 2) is None
    controls["no_translation_no_refutation_K4_d3"] = not LabelClosure(g, 3, translate=False).refuted()

    expected = [checks["geometry"]["connected_below_2d"], checks["geometry"]["frozen_at_2d"],
                checks["geometry"]["three_point_center"], checks["geometry"]["median_center"],
                checks["closure_matches_linear_algebra"]["agree"],
                checks["tangle_lower_bound"]["labels_on_small_side_and_no_refutation"],
                checks["duality_on_small_instances"], checks["carving_derivations"]["all_replay"],
                checks["encodings"]["reduced_closures_agree_above_maxdeg"], checks["encodings"]["standard_within_one"]]
    failures = [i for i, ok in enumerate(expected) if not ok] + [k for k, ok in controls.items() if not ok]
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
        "safe_conclusions": manifest["safe_to_conclude"], "checks": checks, "controls": controls,
        "failures": failures,
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
