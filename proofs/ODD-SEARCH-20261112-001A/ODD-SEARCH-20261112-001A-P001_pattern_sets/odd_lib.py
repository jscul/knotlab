"""Search pattern sets for an odd harmony (research/ODD-SEARCH-20261112-001/preregistration.md, ticket A).

p is odd. A pattern is a 3-subset {0, a, b} of Z_p up to translation (its three distinct residues). For a set P of patterns, a word c
on Z_p is compatible when it is non-constant on every translate of every pattern of P; residue 0 of c is flippable when no translate
T through 0 has its two other values equal and different from c[0]. P is a COUNTEREXAMPLE when some word is compatible (SAT1) but no
compatible word has residue 0 flippable (SAT2 fails). By lemma 4 of EVEN-PERIOD-20261112-001 (window argument), the base of all knot
kinds (0, a, b) with b < p whose residue triple is a translate of a pattern of P is then a harmony whose states all have period
dividing p, so an odd period: the first odd harmony. Otherwise every compatible word of P has a flip certificate."""
import itertools
import math

from pysat.solvers import Solver


def canon_pattern(a, b, p):
    """least (a', b') among the three ways to put a 0 in {0, a, b}"""
    forms = [(a, b), (b - a, p - a), (p - b, p - b + a)]
    return min(tuple(sorted(f)) for f in forms)


def patterns(p):
    return sorted({canon_pattern(a, b, p) for a in range(1, p) for b in range(a + 1, p)})


def units(p):
    return [u for u in range(1, p) if math.gcd(u, p) == 1]


def act(u, pat, p):
    a, b = pat
    x, y = sorted(((u * a) % p, (u * b) % p))
    return canon_pattern(x, y, p)


def canon_set(P, p, U):
    return min(tuple(sorted(act(u, q, p) for q in P)) for u in U)


def translates(pat, p):
    a, b = pat
    return [(r, (r + a) % p, (r + b) % p) for r in range(p)]


def nae_clauses(P, p):
    cl = []
    for pat in P:
        for (x, y, z) in translates(pat, p):
            cl.append([x + 1, y + 1, z + 1])
            cl.append([-(x + 1), -(y + 1), -(z + 1)])
    return cl


def flip0_clauses(P, p):
    cl = []
    for pat in P:
        for T in translates(pat, p):
            if 0 in T:
                o = [t for t in T if t != 0]
                x, y = o
                cl.append([-(x + 1), -(y + 1), 1])
                cl.append([x + 1, y + 1, -1])
    return cl


def sat(clauses):
    with Solver(name="cadical153", bootstrap_with=clauses) as s:
        if s.solve():
            m = s.get_model()
            return [int(m[i] > 0) for i in range(len(m))]
        return None


def test_set(P, p):
    """(SAT1 word or None, SAT2 word or None)"""
    base = nae_clauses(P, p)
    w1 = sat(base)
    if w1 is None:
        return None, None
    w2 = sat(base + flip0_clauses(P, p))
    return w1[:p], (w2[:p] if w2 else None)


def satisfiable_sets(p, m_max, start=None, cap=None):
    """every set of at most m_max patterns, grown one pattern at a time in increasing order and pruned when unsatisfiable;
    yields (P, w1, w2); supersets of unsatisfiable sets are skipped"""
    pats = patterns(p)
    n = len(pats)
    count = [0]

    def grow(P, last):
        base = nae_clauses(P, p)
        w1 = sat(base)
        if w1 is None:
            return
        w2 = sat(base + flip0_clauses(P, p))
        count[0] += 1
        yield P, w1[:p], (w2[:p] if w2 else None)
        if cap and count[0] >= cap:
            return
        if len(P) < m_max:
            for j in range(last + 1, n):
                yield from grow(P + [pats[j]], j)

    firsts = range(n) if start is None else start
    for i in firsts:
        yield from grow([pats[i]], i)


def test_pairs(pairs, p):
    """the same two SAT calls for residue pairs (a, b) that may repeat a residue (needed for even p, used only as a control):
    a translate is the triple of positions (r, r + a, r + b); a repeated position counts once in a clause, and a knot through 0 twice
    cannot be made constant by flipping one position of residue 0"""
    base, flip = [], []
    for a, b in pairs:
        for r in range(p):
            T = (r, (r + a) % p, (r + b) % p)
            s = sorted(set(T))
            base.append([x + 1 for x in s])
            base.append([-(x + 1) for x in s])
            if T.count(0) == 1:
                x, y = [t for t in T if t != 0]
                flip.append(sorted({-(x + 1), -(y + 1), 1}))
                flip.append(sorted({x + 1, y + 1, -1}))
    w1 = sat(base)
    if w1 is None:
        return None, None
    w2 = sat(base + flip)
    return w1[:p], (w2[:p] if w2 else None)


def good_pairs_of(word):
    p = len(word)
    return [(a, b) for a in range(p) for b in range(p) if all(len({word[r], word[(r + a) % p], word[(r + b) % p]}) > 1 for r in range(p))]


# ---- the frozen word search by defect number (prime p) ----
import numpy as np  # noqa: E402


def compositions(n, k):
    """compositions of n into k positive parts"""
    if k == 1:
        yield (n,)
        return
    for first in range(1, n - k + 2):
        for rest in compositions(n - first, k - 1):
            yield (first,) + rest


def canonical_gaps(g):
    """keep a gap sequence only when it is its own lexicographically largest rotation (one per necklace)"""
    return all(g >= g[i:] + g[:i] for i in range(1, len(g)))


def word_from_gaps(g):
    """the cyclic word with a doubled letter (c[x] = c[x+1]) at the end of each gap and a change everywhere else"""
    p = sum(g)
    ends = set()
    s = 0
    for x in g:
        s += x
        ends.add((s - 1) % p)
    c = [0] * p
    for x in range(p - 1):
        c[x + 1] = c[x] if x in ends else 1 - c[x]
    return np.array(c, dtype=np.int8)


def diffs(c):
    p = len(c)
    return np.array([0] + [int((c != np.roll(c, -d)).sum()) for d in range(1, p)])


def closed_patterns(c, pats):
    """the patterns c is never constant on, by the difference identity D(a) + D(b) + D(b - a) = 2p"""
    p = len(c)
    D = diffs(c)
    return [(a, b) for (a, b) in pats if D[a] + D[b] + D[(b - a) % p] == 2 * p], D


def flippable_residues(c, P):
    """residues r whose flip keeps c compatible with P (equivalent to flippability, lemma 5)"""
    p = len(c)
    out = []
    for r in range(p):
        c2 = c.copy()
        c2[r] ^= 1
        D = diffs(c2)
        if all(D[a] + D[b] + D[(b - a) % p] == 2 * p for (a, b) in P):
            out.append(r)
    return out


def search_defect(p, k, pats):
    """every word of odd prime period p with exactly k doubled letters, normalised so that the difference 1 changes most often;
    returns counts, the fully blocked words with their certificates, and any counterexample"""
    tally = {"words": 0, "not normalised": 0, "no pattern": 0, "own certificate": 0, "fully blocked": 0}
    blocked, counter = [], []
    for g in compositions(p, k):
        if not canonical_gaps(g):
            continue
        c = word_from_gaps(g)
        tally["words"] += 1
        P, D = closed_patterns(c, pats)
        if D.max() > D[1]:
            tally["not normalised"] += 1
            continue
        if not P:
            tally["no pattern"] += 1
            continue
        if flippable_residues(c, P):
            tally["own certificate"] += 1
            continue
        tally["fully blocked"] += 1
        w1, w2 = test_set(P, p)
        rec = {"gaps": g, "word": "".join(map(str, c)), "patterns": len(P), "certificate": None if w2 is None else "".join(map(str, w2))}
        blocked.append(rec)
        if w2 is None:
            counter.append(rec)
    return tally, blocked, counter


class Fast:
    """the same tests through the autocorrelation R(d) = sum_x s_x s_{x+d} of s = 1 - 2c, with D(d) = (p - R(d)) / 2: c is compatible
    with {0, a, b} iff R(a) + R(b) + R(b - a) = -p, and flipping residue r changes R(d) by -2 s_r (s_{r+d} + s_{r-d})"""

    def __init__(self, p):
        self.p = p
        self.pats = patterns(p)
        self.A = np.array([a for a, b in self.pats])
        self.B = np.array([b for a, b in self.pats])
        self.BA = (self.B - self.A) % p
        x = np.arange(p)
        self.plus = (x[:, None] + x[None, :]) % p      # [r, d] -> r + d
        self.minus = (x[:, None] - x[None, :]) % p     # [r, d] -> r - d

    def analyse(self, c):
        p = self.p
        s = 1 - 2 * c.astype(np.int64)
        R = (s[self.plus] * s[None, :]).sum(axis=1)     # R[d] = sum_r s_{r+d} s_r
        R[0] = p
        tot = R[self.A] + R[self.B] + R[self.BA]
        ok = tot == -p
        Dmax_ok = R[1:].min() == R[1]                  # D(1) is the largest difference count
        if not ok.any():
            return Dmax_ok, [], []
        M = s[self.plus] + s[self.minus]               # [r, d]
        delta = -2 * s[:, None] * M
        dsum = delta[:, self.A[ok]] + delta[:, self.B[ok]] + delta[:, self.BA[ok]]
        flips = list(np.nonzero((dsum == 0).all(axis=1))[0])
        return Dmax_ok, [self.pats[i] for i in np.nonzero(ok)[0]], flips


def search_defect_fast(F, k):
    p = F.p
    tally = {"words": 0, "not normalised": 0, "no pattern": 0, "own certificate": 0, "fully blocked": 0}
    blocked, counter = [], []
    for g in compositions(p, k):
        if not canonical_gaps(g):
            continue
        c = word_from_gaps(g)
        tally["words"] += 1
        norm, P, flips = F.analyse(c)
        if not norm:
            tally["not normalised"] += 1
            continue
        if not P:
            tally["no pattern"] += 1
            continue
        if flips:
            tally["own certificate"] += 1
            continue
        tally["fully blocked"] += 1
        w1, w2 = test_set(P, p)
        rec = {"gaps": list(g), "word": "".join(map(str, c)), "patterns": len(P), "certificate": None if w2 is None else "".join(map(str, w2))}
        blocked.append(rec)
        if w2 is None:
            counter.append(rec)
    return tally, blocked, counter


def ap_sets(p, sizes=(2, 3, 4)):
    """the advisor's family: sets of arithmetic-progression patterns {0, a, 2a}, steps A with 1 in A, up to sign (a and -a give the
    same pattern), one representative per set of steps"""
    steps = list(range(2, (p - 1) // 2 + 1))
    for m in sizes:
        for rest in itertools.combinations(steps, m - 1):
            A = (1,) + rest
            yield A, [canon_pattern(*sorted(((a % p), (2 * a) % p)), p) for a in A]


def connected_to_complement(P, p, word, cap=200000):
    """after the run (descriptive): enumerate the compatible words of P (up to cap) and ask whether word reaches its complement
    through compatible words, each step changing one or two positions"""
    from pysat.solvers import Solver
    sols = []
    with Solver(name="cadical153", bootstrap_with=nae_clauses(P, p)) as s:
        while s.solve():
            m = s.get_model()
            x = tuple(int(m[i] > 0) for i in range(p))
            sols.append(x)
            if len(sols) >= cap:
                return None
            s.add_clause([-(i + 1) if x[i] else (i + 1) for i in range(p)])
    S = set(sols)
    start = tuple(int(c) for c in word)
    goal = tuple(1 - v for v in start)
    seen, todo = {start}, [start]
    while todo:
        x = todo.pop()
        if x == goal:
            return True, len(S)
        for i in range(p):
            y = list(x); y[i] ^= 1
            for j in [None] + list(range(i + 1, p)):
                z = list(y)
                if j is not None:
                    z[j] ^= 1
                z = tuple(z)
                if z in S and z not in seen:
                    seen.add(z); todo.append(z)
    return False, len(S)
