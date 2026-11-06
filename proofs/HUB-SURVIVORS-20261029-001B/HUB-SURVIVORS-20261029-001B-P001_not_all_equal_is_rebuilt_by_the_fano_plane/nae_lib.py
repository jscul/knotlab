"""Library for HUB-SURVIVORS-20261029-001B-P001: hub gadgets of not-all-equal copies.

A gadget with m copies is a list of variables, each a tuple of distinct copies: hidden variables lie in at least two copies,
legs in exactly one (a wire's hub end may lie in any number). Every copy holds exactly three variables. Copies are enumerated
in a fixed order so that every multiset of variables appears once per labelling of the copies."""
import itertools
from collections import defaultdict

import numpy as np

NAE = np.ones((2, 2, 2), dtype=np.int64)
NAE[0, 0, 0] = NAE[1, 1, 1] = 0
NAE_SET = {s for s in itertools.product((0, 1), repeat=3) if len(set(s)) > 1}
EQ, NEQ = {(0, 0), (1, 1)}, {(0, 1), (1, 0)}
LETTERS = "abcdefghijklmnopqrstuvwxyz"


def connected(m, variables):
    adj = defaultdict(set)
    for S in variables:
        for x in S:
            for y in S:
                adj[x].add(y)
    seen, stack = {0}, [0]
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == m


def fill(m, deg0, visit):
    """call visit(hidden) for every multiset of hidden variables (subsets of >= 2 copies, in lexicographic order, the
    lowest unfilled copy first) completing every copy to three variables"""
    subsets = sorted(c for r in range(2, m + 1) for c in itertools.combinations(range(m), r))

    def rec(start, chosen, deg):
        if all(d == 3 for d in deg):
            visit(tuple(chosen))
            return
        first = next(c for c in range(m) if deg[c] < 3)
        for j in range(start, len(subsets)):
            S = subsets[j]
            if S[0] != first:
                continue
            if all(deg[c] < 3 for c in S):
                for c in S:
                    deg[c] += 1
                chosen.append(S)
                rec(j, chosen, deg)
                chosen.pop()
                for c in S:
                    deg[c] -= 1

    rec(0, [], list(deg0))


def relation(m, leg_vars, hidden, k):
    """projection onto the k legs (leg_vars: tuples of copies) of m NAE copies"""
    slots = [[] for _ in range(m)]
    for i, S in enumerate(leg_vars):
        for c in S:
            slots[c].append(LETTERS[i])
    for j, S in enumerate(hidden):
        for c in S:
            slots[c].append(LETTERS[k + j])
    spec = ",".join("".join(s) for s in slots) + "->" + LETTERS[:k]
    R = np.einsum(spec, *([NAE] * m), optimize="greedy") > 0
    return {s for s in itertools.product((0, 1), repeat=k) if R[s]}


def rebuilding_gadgets(m):
    """all (legs, hidden) with three legs in one copy each whose relation is NAE; returns (count evaluated, hits)"""
    hits, count = [], [0]
    for legs in itertools.combinations_with_replacement(range(m), 3):
        if legs[0] != 0:
            continue
        deg0 = [0] * m
        for c in legs:
            deg0[c] += 1
        if max(deg0) > 2:
            continue

        def visit(hidden):
            if connected(m, list(hidden) + [(c,) for c in legs]):
                count[0] += 1
                if relation(m, [(c,) for c in legs], hidden, 3) == NAE_SET:
                    hits.append((legs, hidden))
        fill(m, deg0, visit)
    return count[0], hits


def wires_with_hub_end(m):
    """all wires: end a in any number (>= 1) of copies including copy 0, end b in one copy; relation EQ or NEQ"""
    hits, count = [], [0]
    for r in range(1, m + 1):
        for A in itertools.combinations(range(m), r):
            if 0 not in A:
                continue
            for b in range(m):
                deg0 = [0] * m
                for c in A:
                    deg0[c] += 1
                deg0[b] += 1
                if max(deg0) > 3:
                    continue

                def visit(hidden, A=A, b=b):
                    if connected(m, list(hidden) + [A, (b,)]):
                        count[0] += 1
                        R = relation(m, [A, (b,)], hidden, 2)
                        if R in (EQ, NEQ):
                            hits.append((A, b, hidden, sorted(R)))
                fill(m, deg0, visit)
    return count[0], hits


FANO_LINES = [tuple(sorted({i % 7, (i + 1) % 7, (i + 3) % 7})) for i in range(7)]


def two_colourable(lines, points):
    for col in itertools.product((0, 1), repeat=len(points)):
        c = dict(zip(points, col))
        if all(len({c[q] for q in L}) > 1 for L in lines):
            return True
    return False


def punctured_relation(lines, p, rel=NAE_SET):
    """split point p into one leg per line through p (in order) and project; rel is the relation on each line"""
    through = [L for L in lines if p in L]
    others = [L for L in lines if p not in L]
    pts = sorted({q for L in lines for q in L} - {p})
    allowed = set()
    for legs in itertools.product((0, 1), repeat=len(through)):
        for col in itertools.product((0, 1), repeat=len(pts)):
            c = dict(zip(pts, col))
            if all(tuple(legs[i] if q == p else c[q] for q in L) in rel for i, L in enumerate(through)) and \
                    all(tuple(c[q] for q in L) in rel for L in others):
                allowed.add(legs)
                break
    return allowed


def is_fano(edges):
    """seven 3-sets on seven points with every pair of points in exactly one edge"""
    pts = sorted({q for e in edges for q in e})
    if len(edges) != 7 or len(pts) != 7 or any(len(set(e)) != 3 for e in edges):
        return False
    return all(sum(1 for e in edges if x in e and y in e) == 1 for x, y in itertools.combinations(pts, 2))


def merged_edges(m, legs, hidden):
    """identify the three legs into one point (labelled -1); copies become edges over hidden variables and that point"""
    edges = [[] for _ in range(m)]
    for c in legs:
        edges[c].append(-1)
    for j, S in enumerate(hidden):
        for c in S:
            edges[c].append(j)
    return [tuple(e) for e in edges]


def punctured_counts(lines, p):
    """number of 2-colourings of the hidden points extending each leg tuple (NAE on every line)"""
    through = [L for L in lines if p in L]
    others = [L for L in lines if p not in L]
    pts = sorted({q for L in lines for q in L} - {p})
    counts = {}
    for legs in itertools.product((0, 1), repeat=len(through)):
        n = 0
        for col in itertools.product((0, 1), repeat=len(pts)):
            c = dict(zip(pts, col))
            if all(tuple(legs[i] if q == p else c[q] for q in L) in NAE_SET for i, L in enumerate(through)) and \
                    all(tuple(c[q] for q in L) in NAE_SET for L in others):
                n += 1
        counts[legs] = n
    return counts
