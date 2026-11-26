"""controls.py: the checks of sides.py before the census (README.md, 'Controls').

    controls.py      runs C1 to C4 and prints one line each"""
import itertools, random, sys
import numpy as np
from fractions import Fraction
import sides as S


def c1_gauss_matches_enumeration(trials=60, seed=20261126):
    """the exact quadratic sums equal the enumeration on random small parity patterns"""
    rng = random.Random(seed); done = 0
    while done < trials:
        K = rng.randint(2, 6); D = rng.randint(5, 14)
        sup = [sorted(rng.sample(range(D), rng.randint(3, min(5, D)))) for _ in range(K)]
        hold = {}
        for k, row in enumerate(sup):
            for d in row: hold.setdefault(d, []).append(k)
        if any(len(v) > 2 for v in hold.values()) or len(hold) < D: continue
        P = S.Pattern(sup)
        x = S.states(P, 'parity'); X = S.bits(x, list(range(P.D)))
        perm = tuple(range(P.K))
        # a random involution of the distinctions stands in for a swap's lift (the sums do not use the pattern's symmetry)
        ds = list(P.dist); rng.shuffle(ds); sig = {d: d for d in P.dist}
        for a, b in zip(ds[0::2][:3], ds[1::2][:3]): sig[a], sig[b] = b, a
        comps = [[0], [1]] if P.K >= 2 else [[0], [0]]
        ws, _ = S.weightings(P, sig, 'two', comps, x, 'parity')
        for nm in ('U', 'W1', 'W1c', 'W2'):
            Z, m1, M11 = S.pair_tables(X, ws[nm])
            Zg, m1g, M11g = S.parity_quadratic_tables(P, sig, 'two', comps, nm)
            assert Z == Zg and all(int(a) == int(b) for a, b in zip(m1, m1g)), (nm, Z, Zg)
            assert all(int(M11[s, t]) == int(M11g[s, t]) for s in range(P.D) for t in range(P.D)), nm
        done += 1
    return f'C1 exact quadratic sums equal enumeration on {trials} random parity patterns: pass'


def c2_positive_control():
    """a signed weighting known to give the literature's PR box passes every gate with CHSH 4 under R1"""
    # on four bits (a0, a1, b0, b1) with a0 = b1, phase a0 b0 + a0 b1 + a1 b0 + a1 b1 (found by quad4's search)
    xs = [y for y in itertools.product((0, 1), repeat=4) if y[0] == y[3]]
    w = np.array([(-1) ** ((y[0] * y[2] + y[0] * y[3] + y[1] * y[2] + y[1] * y[3]) % 2) for y in xs], dtype=np.int8)
    X = np.array(xs, dtype=np.int8)
    Z, m1, M11 = S.pair_tables(X, w); M = S.four(Z, m1, M11)
    dj = np.ones((4, 4), dtype=bool)
    r = S.best_chsh(Z, M, [0, 1], [2, 3], dj, 'R1')
    assert r['best'] == '4' and len(r['hits']) == 1, r
    return f"C2 positive control (a signed PR weighting on four bits): R1 CHSH {r['best']}, all gates passed: pass"


def c3_unsigned_never_exceeds(stages):
    """the unsigned weighting never exceeds 2 under R1 (Fine's theorem), on the named stages"""
    worst = Fraction(0)
    stages = [(P, law) for P, law in stages if S.states(P, law) is not None]
    for P, law in stages:
        x = S.states(P, law); X = S.bits(x, list(range(P.D)))
        Z, m1, M11 = S.pair_tables(X, np.ones(len(x), dtype=np.int8)); M = S.four(Z, m1, M11)
        r = S.best_chsh(Z, M, list(range(P.D)), list(range(P.D)), S.disjoint_matrix(P), 'R1')
        if r['best'] is not None: worst = max(worst, Fraction(r['best']))
        assert not r['hits']
    return f'C3 unsigned weighting, every placement on {len(stages)} stages: largest R1 CHSH {worst} (bound 2): pass'


def c4_four_bit_census():
    """every quadratic signed weighting on an affine set of four read bits: the largest R1 CHSH, and whether any with an
    affine sign exceeds 2"""
    Y = list(itertools.product((0, 1), repeat=4))
    monos = [()] + [(i,) for i in range(4)] + list(itertools.combinations(range(4), 2))
    def val(coef, y):
        s = 0
        for c, m in zip(coef, monos):
            if c: s ^= int(all(y[i] for i in m))
        return s
    def span(gens):
        out = {(0, 0, 0, 0)}
        for g in gens: out |= {tuple(a ^ b for a, b in zip(s, g)) for s in out}
        return out
    subs = set()
    for k in range(5):
        for gens in itertools.combinations(Y[1:], k):
            L = span(gens)
            for off in Y: subs.add(frozenset(tuple(a ^ b for a, b in zip(l, off)) for l in L))
    best, best_affine, hits = Fraction(0), Fraction(0), 0
    import collections
    where = collections.Counter()
    for V in subs:
        Vs = sorted(V)
        for coef in itertools.product((0, 1), repeat=len(monos)):
            if coef[0]: continue
            affine = not any(coef[5:]) or all(
                (val(coef, u) ^ val(coef, v) ^ val(coef, Vs[0]) ^ val(coef, tuple(a ^ b ^ c for a, b, c in zip(u, v, Vs[0])))) == 0
                for u in Vs for v in Vs)
            w = np.array([(-1) ** val(coef, y) for y in Vs], dtype=np.int8)
            X = np.array(Vs, dtype=np.int8)
            Z, m1, M11 = S.pair_tables(X, w); M = S.four(Z, m1, M11)
            r = S.best_chsh(Z, M, [0, 1], [2, 3], np.ones((4, 4), dtype=bool), 'R1')
            if r['best'] is None: continue
            b = Fraction(r['best']); best = max(best, b)
            if affine: best_affine = max(best_affine, b)
            hits += b > 2
            if b > 2:
                ties = [u for u in Y[1:] if len({sum(p * q for p, q in zip(u, y)) % 2 for y in Vs}) == 1]
                cross = any((u[0] or u[1]) and (u[2] or u[3]) and sum(u) == 2 for u in ties)
                where[(len(Vs), 'one read of each reader tied' if cross else 'no such tie')] += 1
    return (f'C4 four read bits, every quadratic sign on every affine set ({len(subs)} sets): largest R1 CHSH {best}; '
            f'with an affine sign at most {best_affine}; {hits} weightings above 2, by set size and tie: {dict(where)}')


if __name__ == '__main__':
    print(c1_gauss_matches_enumeration(), flush=True)
    print(c2_positive_control(), flush=True)
    F = S.forbid()
    two = S.Pattern([[0, 1, 2], [0, 3, 4]])
    st, _ = S.grow_rounds(two.supports, 'parity', 2)
    st2, _ = S.grow_rounds(two.supports, 'nae', 2)
    print(c3_unsigned_never_exceeds([(S.Pattern(s), 'parity') for s in st] + [(S.Pattern(s), 'nae') for s in st2]), flush=True)
    print(c4_four_bit_census(), flush=True)
