"""Referee R1 for VARIABLE-OUTPUT-READER-20261118-001D (own code; none of the study's checkers or libraries are imported; the width-32
presentation's junction supports are copied from its certificate, active_part.json, as data).

  ../../../.venv/bin/python -B referee_reader.py <part> > referee_reader_<part>.json      (from this directory)

The serial law as the study states it: seed one even-parity junction on three distinctions; a new junction takes one loose
distinction from each of one, two or three distinct junctions and two or three fresh ones; two parents need a common ordinary
neighbour (a junction sharing a distinction with each), three parents pairwise so and no neighbour common to all three.  The dual space
is the GF(2) span of the junction supports; bonds are its inclusion-minimal nonzero words; D(x, y) is the least bond size through the
pair minus one.  A legal triple is three loose distinctions at three distinct junctions that could be the parents of a three-parent
join.  The scalar separator test at t links x, y when D(x, y) != D(x, t) + D(t, y) - 1.

Parts:
  w32      the study's width-32 presentation: the history's legality, all 496 entries, the transposition (13 14), the six-place
           equation and its image, the table's automorphism group, the legal triples and whether every automorphism keeps them, the
           separator test at every t.
  random   random reachable presentations, widths 21 to 34, 6,000 uniform over legal moves and 6,000 biased towards joins: the separator test at every t
           against physical deletion; every table automorphism (capped) against the legal-triple set; the automorphisms that lose a
           parity equation (like (13 14)), and whether any of them moves a legal triple to a forbidden one.
  cont     4,000 random continuations (biased to joins) of the study's width-20 source with the (13 14) symmetry, widths 22 to 34:
           the same checks, aimed at the open case (an equation-losing table symmetry in a presentation with legal triples).
  cont32   800 random one- and two-join continuations of the width-32 presentation (widths 34 to 38), which starts with both.
"""
import itertools
import json
import random
import sys
from collections import Counter

import numpy as np


class Pres:
    def __init__(self, supports=None):
        self.J = [list(s) for s in (supports or [[0, 1, 2]])]
        self.owner = {}
        for k, S in enumerate(self.J):
            for b in S:
                self.owner.setdefault(b, []).append(k)
        self.nb = 1 + max(self.owner)

    def nbrs(self, k):
        return {o for b in self.J[k] for o in self.owner[b] if o != k}

    def loose(self, k):
        return [b for b in self.J[k] if len(self.owner[b]) == 1]

    def legal_parents(self, P):
        if len(set(P)) != len(P) or not all(self.loose(k) for k in P):
            return False
        if len(P) == 1:
            return True
        N = [self.nbrs(k) for k in P]
        if any(not (N[i] & N[j]) for i, j in itertools.combinations(range(len(P)), 2)):
            return False
        return len(P) == 2 or not set.intersection(*N)

    def moves(self):
        live = [k for k in range(len(self.J)) if self.loose(k)]
        out = []
        for r in (1, 2, 3):
            for P in itertools.combinations(live, r):
                if self.legal_parents(P):
                    out.append(P)
        return out

    def add(self, P, fresh):
        bits = [self.loose(k)[0] for k in P] + list(range(self.nb, self.nb + fresh))
        self.nb += fresh
        jid = len(self.J)
        self.J.append(bits)
        for b in bits:
            self.owner.setdefault(b, []).append(jid)

    def width(self):
        return self.nb

    def legal_triples(self):
        loose = [(b, js[0]) for b, js in self.owner.items() if len(js) == 1]
        out = set()
        for (x, a), (y, b), (z, c) in itertools.combinations(loose, 3):
            if len({a, b, c}) == 3 and self.legal_parents((a, b, c)):
                out.add(frozenset((x, y, z)))
        return out

    def physical_parts(self, t):
        """Components of the ordinary incidence after deleting distinction t, as sets of distinctions."""
        parent = {}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        bits = [b for b in range(self.nb) if b != t]
        for b in bits:
            parent[b] = b
        for S in self.J:
            S2 = [b for b in S if b != t]
            for b in S2[1:]:
                parent[find(b)] = find(S2[0])
        groups = {}
        for b in bits:
            groups.setdefault(find(b), set()).add(b)
        return sorted(map(frozenset, groups.values()), key=min)


def table(P):
    n = P.width()
    rows = np.array([sum(1 << b for b in S) for S in P.J], dtype=np.uint64)
    words = np.zeros(1, dtype=np.uint64)
    for r in rows:
        words = np.concatenate([words, words ^ r])
    words = np.unique(words[words != 0])
    size = np.bitwise_count(words)
    order = np.argsort(size, kind="stable")
    words, size = words[order], size[order]
    minimal = np.zeros(0, dtype=np.uint64)
    D = np.full((n, n), 10 ** 6, dtype=np.int64)
    np.fill_diagonal(D, 0)
    for s in np.unique(size):
        W = words[size == s]
        if len(minimal):
            contains = ((W[:, None] & minimal[None, :]) == minimal[None, :]).any(axis=1)
            W = W[~contains]
        if len(W) == 0:
            continue
        minimal = np.concatenate([minimal, W])
        bitsets = ((W[:, None] >> np.arange(n, dtype=np.uint64)[None, :]) & np.uint64(1)).astype(bool)
        for row in bitsets:
            idx = np.flatnonzero(row)
            sub = D[np.ix_(idx, idx)]
            np.minimum(sub, int(s) - 1, out=sub)
            D[np.ix_(idx, idx)] = sub
            np.fill_diagonal(D, 0)
    return D, rows


def in_span(rows, word):
    basis = {}
    for r in [int(x) for x in rows]:
        while r:
            p = r.bit_length() - 1
            if p not in basis:
                basis[p] = r
                break
            r ^= basis[p]
    w = word
    while w:
        p = w.bit_length() - 1
        if p not in basis:
            return False
        w ^= basis[p]
    return True


def automorphisms(D, cap=200000):
    n = len(D)
    Dl = D.tolist()
    sig = [tuple(sorted(Dl[i])) for i in range(n)]
    # refine by the multiset of (distance, signature) pairs
    for _ in range(3):
        sig = [tuple(sorted((Dl[i][j], sig[j]) for j in range(n))) for i in range(n)]
    cls = {s: k for k, s in enumerate(sorted(set(sig)))}
    col = [cls[s] for s in sig]
    order = sorted(range(n), key=lambda i: (sum(1 for j in range(n) if col[j] == col[i]), i))
    out = []

    def go(img, used):
        if len(out) >= cap:
            return
        k = len(img)
        if k == n:
            g = [0] * n
            for a, b in zip(order, img):
                g[a] = b
            out.append(tuple(g))
            return
        a = order[k]
        for t in range(n):
            if t in used or col[t] != col[a]:
                continue
            if all(Dl[a][order[j]] == Dl[t][img[j]] for j in range(k)):
                used.add(t)
                go(img + [t], used)
                used.discard(t)
    go([], set())
    return out, len(out) >= cap


def scalar_parts(D, t):
    n = len(D)
    others = [x for x in range(n) if x != t]
    parent = {x: x for x in others}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for x, y in itertools.combinations(others, 2):
        if D[x][y] != D[x][t] + D[t][y] - 1:
            parent[find(x)] = find(y)
    groups = {}
    for x in others:
        groups.setdefault(find(x), set()).add(x)
    return sorted(map(frozenset, groups.values()), key=min)


def examine(P, aut_cap=200000):
    D, rows = table(P)
    n = P.width()
    r = Counter()
    for t in range(n):
        r["separator tests"] += 1
        r["separator mismatch"] += scalar_parts(D, t) != P.physical_parts(t)
        r["separating distinctions"] += len(P.physical_parts(t)) > 1
    legal = P.legal_triples()
    r["legal triples"] += len(legal)
    aut, capped = automorphisms(D, aut_cap)
    r["automorphisms"] += len(aut)
    r["automorphism search capped"] += capped
    lose = []
    for g in aut:
        img = {frozenset(g[x] for x in T) for T in legal}
        moves_legal = img != legal
        loses = any(not in_span(rows, sum(1 << g[b] for b in S)) for S in P.J)
        r["automorphisms losing a parity equation"] += loses
        r["automorphisms moving a legal triple to a forbidden one"] += moves_legal
        r["... of which lose a parity equation"] += moves_legal and loses
        if loses and len(lose) < 3:
            lose.append(g)
    return D, rows, legal, aut, dict(r), lose


def part_w32():
    supports = [[0, 1, 2], [0, 3, 5], [1, 4, 7], [2, 6, 8], [3, 4, 9, 11], [5, 6, 10, 12], [7, 8, 13, 14], [9, 10, 15, 16],
                [11, 12, 13, 17, 18, 19], [17, 20, 21], [18, 22, 23], [19, 24, 25], [20, 22, 26, 27], [21, 24, 28, 29],
                [23, 25, 30, 31]]
    # replay the history under the law (parents = the junctions whose loose distinctions each new junction takes)
    P = Pres([supports[0]])
    legal_history = True
    for S in supports[1:]:
        par = []
        for b in S:
            if b in P.owner:
                par.append(P.owner[b][0])
        if not P.legal_parents(tuple(par)) or any(len(P.owner[b]) != 1 for b in S if b in P.owner):
            legal_history = False
        fresh = [b for b in S if b not in P.owner]
        if len(fresh) not in (2, 3) or len(par) not in (1, 2, 3):
            legal_history = False
        jid = len(P.J)
        P.J.append(list(S))
        for b in S:
            P.owner.setdefault(b, []).append(jid)
        P.nb = max(P.nb, 1 + max(S))
    D, rows, legal, aut, r, lose = examine(P)
    n = P.width()
    swap = list(range(n))
    swap[13], swap[14] = 14, 13
    preserved = all(D[x][y] == D[swap[x]][swap[y]] for x in range(n) for y in range(n))
    six = sum(1 << b for b in (11, 12, 13, 17, 18, 19))
    six_img = sum(1 << b for b in (11, 12, 14, 17, 18, 19))
    hist = Counter(int(D[x][y]) for x, y in itertools.combinations(range(n), 2))
    return {"width": n, "junctions": len(P.J), "history legal under the law": legal_history,
            "pairs": n * (n - 1) // 2, "distance histogram": dict(sorted(hist.items())),
            "transposition (13 14) preserves every entry": preserved,
            "six-place equation {11,12,13,17,18,19} in the dual": in_span(rows, six),
            "its image {11,12,14,17,18,19} in the dual": in_span(rows, six_img),
            "legal triples": sorted(sorted(T) for T in legal), "number of legal triples": len(legal),
            "table automorphism group order": len(aut), "checks": r}


def random_pres(rng, target, bias=None):
    """Uniform over legal moves, or, with bias = (w1, w2, w3), first a parent count by those weights among the counts available."""
    P = Pres()
    while P.width() < target:
        mv = P.moves()
        if not mv:
            return None
        if bias is None:
            par = rng.choice(mv)
        else:
            by = {r: [m for m in mv if len(m) == r] for r in (1, 2, 3)}
            ks = [r for r in (1, 2, 3) if by[r]]
            r = rng.choices(ks, weights=[bias[r - 1] for r in ks])[0]
            par = rng.choice(by[r])
        fresh = rng.choice((2, 3))
        if P.width() + fresh > target + 1:
            fresh = 2
        P.add(par, fresh)
    return P


def one(args):
    seed, target, bias = args
    rng = random.Random(f"referee-reader-{seed}-{bias}")
    P = random_pres(rng, target, bias)
    if P is None or P.width() > 34 or len(P.J) > 16:
        return {"skipped": 1}
    D, rows, legal, aut, r, lose = examine(P, aut_cap=50000)
    r["presentations"] = 1
    r[f"width {P.width()}"] = 1
    r["with a legal triple"] = int(bool(legal))
    r["with a legal triple and an equation-losing automorphism"] = int(bool(legal) and r.get("automorphisms losing a parity equation", 0) > 0)
    return r


def part_random(n=6000, workers=16):
    from multiprocessing import Pool
    rng = random.Random("referee-reader-widths")
    out = {}
    for name, bias in (("uniform over legal moves", None), ("biased to joins (parent counts 1, 2, 3 weighted 1, 3, 6)", (1, 3, 6))):
        jobs = [(s, rng.randint(21, 33), bias) for s in range(n)]
        acc = Counter()
        with Pool(workers) as Pl:
            for r in Pl.imap_unordered(one, jobs, chunksize=4):
                acc.update(r)
        out[name] = dict(sorted(acc.items()))
    return out


SOURCE20 = [[0, 1, 2], [0, 3, 5], [1, 4, 7], [2, 6, 8], [3, 4, 9, 11], [5, 6, 10, 12], [7, 8, 13, 14], [9, 10, 15, 16],
            [11, 12, 13, 17, 18, 19]]


def cont(args):
    """A random biased continuation of the study's width-20 source (the one whose table has the (13 14) symmetry)."""
    seed, target = args
    rng = random.Random(f"referee-reader-cont-{seed}")
    P = Pres(SOURCE20)
    while P.width() < target:
        mv = P.moves()
        if not mv:
            break
        by = {r: [m for m in mv if len(m) == r] for r in (1, 2, 3)}
        ks = [r for r in (1, 2, 3) if by[r]]
        r = rng.choices(ks, weights=[(1, 3, 6)[r - 1] for r in ks])[0]
        P.add(rng.choice(by[r]), rng.choice((2, 3)))
    if P.width() > 36 or len(P.J) > 17:
        return {"skipped": 1}
    D, rows, legal, aut, r, lose = examine(P, aut_cap=50000)
    r["presentations"] = 1
    r["with a legal triple"] = int(bool(legal))
    r["with a legal triple and an equation-losing automorphism"] = int(bool(legal) and r.get("automorphisms losing a parity equation", 0) > 0)
    return r


W32 = [[0, 1, 2], [0, 3, 5], [1, 4, 7], [2, 6, 8], [3, 4, 9, 11], [5, 6, 10, 12], [7, 8, 13, 14], [9, 10, 15, 16],
       [11, 12, 13, 17, 18, 19], [17, 20, 21], [18, 22, 23], [19, 24, 25], [20, 22, 26, 27], [21, 24, 28, 29], [23, 25, 30, 31]]


def cont32(args):
    """A random continuation (one or two joins, biased to joins) of the width-32 presentation: legal triples and an
    equation-losing table symmetry are both present at the start."""
    seed, steps = args
    rng = random.Random(f"referee-reader-cont32-{seed}")
    P = Pres(W32)
    for _ in range(steps):
        mv = P.moves()
        by = {r: [m for m in mv if len(m) == r] for r in (1, 2, 3)}
        ks = [r for r in (1, 2, 3) if by[r]]
        r = rng.choices(ks, weights=[(1, 3, 6)[r - 1] for r in ks])[0]
        P.add(rng.choice(by[r]), rng.choice((2, 3)))
    D, rows, legal, aut, r, lose = examine(P, aut_cap=50000)
    r["presentations"] = 1
    r["with a legal triple"] = int(bool(legal))
    r["with a legal triple and an equation-losing automorphism"] = int(bool(legal) and r.get("automorphisms losing a parity equation", 0) > 0)
    return r


def part_cont32(n=800, workers=16):
    from multiprocessing import Pool
    jobs = [(s, 1 + s % 2) for s in range(n)]
    acc = Counter()
    with Pool(workers) as Pl:
        for r in Pl.imap_unordered(cont32, jobs, chunksize=2):
            acc.update(r)
    return dict(sorted(acc.items()))


def part_cont(n=4000, workers=16):
    from multiprocessing import Pool
    rng = random.Random("referee-reader-cont-widths")
    jobs = [(s, rng.randint(22, 34)) for s in range(n)]
    acc = Counter()
    with Pool(workers) as Pl:
        for r in Pl.imap_unordered(cont, jobs, chunksize=4):
            acc.update(r)
    return dict(sorted(acc.items()))


if __name__ == "__main__":
    part = sys.argv[1]
    print(json.dumps({"w32": part_w32, "random": part_random, "cont": part_cont, "cont32": part_cont32}[part](), indent=1, default=str))
