"""Symmetric step sets (research/ODD-FAMILY-20261112-001/preregistration.md, ticket A).

n odd. A step set S in Z_n closed under negation forbids words constant on a progression {x, x + s, x + 2s}, s in S: the patterns
{0, s, 2s} (the literature's 2-colourings of Z_n with no monochromatic progression of those steps). S MAKES A HARMONY at n when some
word is compatible with it and no compatible word has a flippable residue (SAT1 and not SAT2 of ODD-SEARCH-20261112-001's
odd_lib.test_set): by lemma 4 of EVEN-PERIOD-20261112-001 (its window argument needs n odd, not prime), the base K_S of all knot kinds
(0, a, b), b < n, whose residues form a translate of {0, s, 2s} with s in S, then has every state repeating with a period dividing n.
The families: (cosets) H a multiplicative subgroup of the units of Z_n containing -1, S a union of one, two or three of its cosets t*H
(t any nonzero residue; for composite n, t may be a non-unit), a union with a unit coset normalised by a multiplier to contain H;
(doubled steps) S = {±1, ±2, ±t} or {±1, ±2, ±t, ±2t} for every t."""
import itertools
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/ODD-SEARCH-20261112-001A/ODD-SEARCH-20261112-001A-P001_pattern_sets"))
import odd_lib as O  # noqa: E402


def units(n):
    return [u for u in range(1, n) if math.gcd(u, n) == 1]


def subgroups_with_minus_one(n):
    """the subgroups <u, -1> of the units, one per distinct set"""
    out = {}
    for u in units(n):
        H = {1, n - 1}
        frontier = [1, n - 1]
        while frontier:
            x = frontier.pop()
            for g in (u, n - 1):
                y = (x * g) % n
                if y not in H:
                    H.add(y)
                    frontier.append(y)
        out[frozenset(H)] = sorted(H)
    return sorted(out.values(), key=lambda h: (len(h), h))


def cosets(n, H):
    seen, out = set(), []
    for t in range(1, n):
        c = frozenset((t * h) % n for h in H)
        if c not in seen:
            seen.add(c)
            out.append(sorted(c))
    return out


def step_sets(n, H, max_cosets=3):
    """unions of up to max_cosets cosets of H; unions with a unit coset normalised to contain H"""
    C = cosets(n, H)
    Hs = sorted(H)
    unit = [c for c in C if math.gcd(c[0], n) == 1]
    others = [c for c in C if c != Hs]
    out = set()
    for m in range(0, max_cosets):
        for extra in itertools.combinations(others, m):
            out.add(tuple(sorted(set(Hs).union(*extra))))
    nonunit = [c for c in C if math.gcd(c[0], n) != 1]
    for m in range(1, max_cosets + 1):
        for chosen in itertools.combinations(nonunit, m):
            out.add(tuple(sorted(set().union(*chosen))))
    return sorted(out, key=lambda s: (len(s), s))


def ap_patterns(S, n):
    return sorted({O.canon_pattern(*sorted((s % n, (2 * s) % n)), n) for s in S})


def test(S, n):
    return O.test_set(ap_patterns(S, n), n)


def minimal_period(word):
    n = len(word)
    return next(d for d in range(1, n + 1) if n % d == 0 and all(word[i] == word[(i + d) % n] for i in range(n)))


def rigidity_check(S, n, cap=10**6):
    """enumerate every colouring; return (count, orbits, Hamming-1 pairs, least distance, minimal periods)"""
    from pysat.solvers import Solver
    P = ap_patterns(S, n)
    sols = []
    with Solver(name="cadical153", bootstrap_with=O.nae_clauses(P, n)) as s:
        while s.solve():
            m = s.get_model()
            x = tuple(int(m[i] > 0) for i in range(n))
            sols.append(x)
            if len(sols) > cap:
                return None
            s.add_clause([-(i + 1) if x[i] else (i + 1) for i in range(n)])
    S_ = set(sols)
    ham1 = sum(1 for x in sols for i in range(n) if x[:i] + (1 - x[i],) + x[i + 1:] in S_) // 2
    orbits = {min(x[r:] + x[:r] for r in range(n)) for x in sols}
    least = min((sum(a != b for a, b in zip(x, y)) for x, y in itertools.combinations(sols, 2)), default=None) if len(sols) <= 3000 else None
    return {"colourings": len(sols), "orbits": len(orbits), "Hamming-1 pairs": ham1, "least distance": least,
            "minimal periods": sorted({minimal_period(x) for x in sols})}


def t_sets(n):
    """the advisor's family: {±1, ±2, ±t} and {±1, ±2, ±t, ±2t} for every t (one per set)"""
    out = set()
    for t in range(1, n):
        for steps in ((1, 2, t), (1, 2, t, 2 * t)):
            S = set()
            for s in steps:
                S.update({s % n, (-s) % n})
            S.discard(0)
            if all((2 * s) % n != 0 for s in S):
                out.add(tuple(sorted(S)))
    return sorted(out, key=lambda s: (len(s), s))


def steps_up_to_sign(S, n):
    return len({min(s, n - s) for s in S})


def has_doubled_pair(S, n):
    """some s in S with 2s in S (the advisor's prediction 2, up to scaling)"""
    Ss = set(S)
    return any((2 * s) % n in Ss for s in Ss)


def scan(n, max_cosets=3):
    """every set of the two families at n: (family, H size or None, S, rigid?)"""
    out = []
    seen = set()
    for H in subgroups_with_minus_one(n):
        for S in step_sets(n, H, max_cosets):
            if S in seen:
                continue
            seen.add(S)
            w1, w2 = test(S, n)
            out.append({"family": "cosets", "H": len(H), "S": list(S), "satisfiable": w1 is not None, "rigid": w1 is not None and w2 is None,
                        "word": "".join(map(str, w1)) if (w1 is not None and w2 is None) else None})
    for S in t_sets(n):
        if S in seen:
            continue
        seen.add(S)
        w1, w2 = test(S, n)
        out.append({"family": "doubled steps", "H": None, "S": list(S), "satisfiable": w1 is not None, "rigid": w1 is not None and w2 is None,
                    "word": "".join(map(str, w1)) if (w1 is not None and w2 is None) else None})
    return out


def stabiliser(S, n):
    """the multipliers u (units) with u*S = S: S is a union of cosets of H exactly when H is inside it"""
    Ss = set(S)
    return [u for u in units(n) if {(u * x) % n for x in Ss} == Ss]


def doubled_shape(S, n):
    """S equals {±s, ±2s, ±t} or {±s, ±2s, ±t, ±2t} for some s, t (the advisor's prediction 2: up to a unit, {±1, ±2, ±t(, ±2t)})"""
    Ss = set(S)
    for s in Ss:
        core = {s, n - s, (2 * s) % n, (n - 2 * s) % n}
        if not core <= Ss:
            continue
        rest = Ss - core
        if len(rest) == 2:
            return True
        if len(rest) == 4 and any({t, n - t, (2 * t) % n, (n - 2 * t) % n} == rest for t in rest):
            return True
    return False


def kinds(S, n):
    """the knot kinds (0, a, b), b < n, whose residues form a translate of {0, s, 2s}, s in S"""
    out = set()
    for s in S:
        R = [0, s % n, (2 * s) % n]
        for c in R:
            out.add(tuple(sorted((r - c) % n for r in R)))
    return sorted(out)


def window_check(S, n, width=3):
    """a state of K_S on width*n distinctions, every knot inside, with x_m != x_(m+n) for some m in [n, 2n)? (None: no such state)"""
    from pysat.solvers import Solver
    W = width * n
    cl = []
    for (_, a, b) in kinds(S, n):
        for j in range(W - b):
            cl.append([j + 1, j + a + 1, j + b + 1])
            cl.append([-(j + 1), -(j + a + 1), -(j + b + 1)])
    ys = []
    for m in range(n, 2 * n):
        y = W + 1 + (m - n)
        ys.append(y)
        cl.append([-y, m + 1, m + n + 1])
        cl.append([-y, -(m + 1), -(m + n + 1)])
    cl.append(ys)
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        return s.get_model() if s.solve() else None


def offsets_gcd(S, n):
    g = n
    for s in S:
        g = math.gcd(g, s)
    return g


def h_and_double(p):
    """H u 2H for H the fourth roots of 1 (p = 1 mod 4 prime)"""
    H = next(h for h in subgroups_with_minus_one(p) if len(h) == 4)
    return tuple(sorted(set(H) | {(2 * h) % p for h in H}))


def count_orbits(S, n, cap=200000):
    """compatible words, each found word blocking its n rotations and their flips (at a prime n a non-constant word's orbit has 2n
    words, since n is odd); returns (words, orbit representatives, flippable orbits) or None over the cap"""
    from pysat.solvers import Solver
    P = ap_patterns(S, n)
    reps, total = [], 0
    with Solver(name="cadical153", bootstrap_with=O.nae_clauses(P, n)) as s:
        while s.solve():
            m = s.get_model()
            x = tuple(int(m[i] > 0) for i in range(n))
            orbit = {x[r:] + x[:r] for r in range(n)}
            orbit |= {tuple(1 - v for v in y) for y in orbit}
            total += len(orbit)
            reps.append(x)
            if total > cap:
                return None
            for y in orbit:
                s.add_clause([-(i + 1) if y[i] else (i + 1) for i in range(n)])
    Sset = set(S)

    def flip_ok(w, i):
        """flipping place i of the compatible word w leaves it compatible: only progressions through i can change"""
        v = 1 - w[i]
        for d in Sset:
            if w[(i + d) % n] == w[(i + 2 * d) % n] == v or w[(i - d) % n] == w[(i + d) % n] == v:
                return False
        return True
    flippable = sum(1 for x in reps if any(flip_ok(x, i) for i in range(n)))
    return {"words": total, "orbits": len(reps), "orbits with a flippable residue": flippable}


def multiplier_invariant(S, n, U, cap=200000):
    """compatible words fixed exactly by every multiplier in U (constant on the orbits of U): their number"""
    from pysat.solvers import Solver
    P = ap_patterns(S, n)
    cl = O.nae_clauses(P, n)
    for u in U:
        for x in range(n):
            y = (u * x) % n
            if y != x:
                cl.append([x + 1, -(y + 1)])
                cl.append([-(x + 1), y + 1])
    c = 0
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        while s.solve():
            m = s.get_model()
            c += 1
            if c > cap:
                return None
            s.add_clause([-(i + 1) if m[i] > 0 else (i + 1) for i in range(n)])
    return c


def difference_set(D, v):
    """the differences of D in Z_v, as a count per nonzero residue"""
    cnt = [0] * v
    for a in D:
        for b in D:
            if a != b:
                cnt[(a - b) % v] += 1
    return cnt[1:]


def discrete_log_cosets(word, p, g, H):
    """the positions log_g(x) mod (p-1)/|H| of the cosets of H on which word is 1 (word constant on H-cosets)"""
    m = (p - 1) // len(H)
    logs, x = {}, 1
    for k in range(p - 1):
        logs[x] = k
        x = (x * g) % p
    ones = sorted({logs[x] % m for x in range(1, p) if word[x] == 1})
    return ones, m
