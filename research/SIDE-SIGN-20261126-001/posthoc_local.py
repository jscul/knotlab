"""posthoc_local.py: a control added after the census (post hoc, README.md "Results"): does a weighting that is a product
of single-distinction signs give tables above 2 under R1 and R2 on the same stages?  One distinction's sign (-1)^(x_u)
sums to zero under not-all-equal (complement), so the control takes two: (-1)^(x_u + x_v), for every pair u, v.

    posthoc_local.py START ROUND LAW         every pair u, v of that census stage; readers anywhere, holders not sharing a knot
    posthoc_local.py START ROUND parity --cz  one pairwise sign (-1)^(x_u x_v) on every pair u, v
    posthoc_local.py START ROUND LAW --matchings PERM LIFT   the swap's W1 against 200 random matchings (seed 20261126)"""
import sys, json
import numpy as np
import sides as S


def run_cz(start, rnd, law):
    """under parity a product of single signs is a character (normalizer 0 or a nonnegative weighting), so the parity
    control is one pairwise sign (-1)^(x_u x_v) on an arbitrary pair u, v, not a swap's pair"""
    import itertools
    F = S.forbid()
    st, _ = S.grow_rounds(F.supports_of(S.census_starts()[start]), law, rnd)
    P = S.Pattern(st[rnd]); x = S.states(P, law); X = S.bits(x, list(range(P.D))); dj = S.disjoint_matrix(P)
    allc = list(range(P.D)); out = []
    for u, v in itertools.combinations(range(P.D), 2):
        w = (1 - 2 * (((x >> np.uint64(u)) & (x >> np.uint64(v))) & np.uint64(1)).astype(np.int8)).astype(np.int8)
        Z, m1, M11 = S.pair_tables(X, w); M = S.four(Z, m1, M11)
        r1 = S.best_chsh(Z, M, allc, allc, dj, 'R1'); r2 = S.best_chsh(Z, M, allc, allc, dj, 'R2')
        out.append({'u': u, 'v': v, 'Z': Z, 'R1 best': r1['best'], 'R1 hits': len(r1['hits']), 'R2 best': r2['best'], 'R2 hits': len(r2['hits'])})
    print(json.dumps({'start': start, 'round': rnd, 'law': law, 'K': P.K, 'D': P.D, 'N': len(x), 'one pairwise sign on an arbitrary pair': out}))


def run_matchings(start, rnd, law, perm, lift, samples=200, seed=20261126):
    """the swap's own W1 against W1 built on random matchings of the same number of pairs (seed stated): is the swap's
    pairing special?"""
    import random
    F = S.forbid()
    st, _ = S.grow_rounds(F.supports_of(S.census_starts()[start]), law, rnd)
    P = S.Pattern(st[rnd]); x = S.states(P, law); X = S.bits(x, list(range(P.D))); dj = S.disjoint_matrix(P)
    sig = P.lift(tuple(perm), lift == 'max')
    pairs = sorted({tuple(sorted((P.index[d], P.index[sig[d]]))) for d in P.dist if sig[d] != d})
    def w_of(prs):
        q = np.zeros(len(x), dtype=np.uint64)
        for i, j in prs: q ^= ((x >> np.uint64(i)) & (x >> np.uint64(j))) & np.uint64(1)
        return (1 - 2 * q.astype(np.int8)).astype(np.int8)
    allc = list(range(P.D)); rng = random.Random(seed)
    def score(prs):
        w = w_of(prs); Z, m1, M11 = S.pair_tables(X, w); M = S.four(Z, m1, M11)
        r = S.best_chsh(Z, M, allc, allc, dj, 'R1'); return r['best'], len(r['hits'])
    own = score(pairs); rand = []
    for _ in range(samples):
        ds = list(range(P.D)); rng.shuffle(ds)
        rand.append(score([tuple(sorted(ds[2 * k:2 * k + 2])) for k in range(len(pairs))]))
    print(json.dumps({'start': start, 'round': rnd, 'law': law, 'pairs': len(pairs), 'swap': perm, 'lift': lift,
                      'own W1 (best, hits)': own, 'random matchings with a hit': sum(1 for b, h in rand if h),
                      'samples': samples, 'seed': seed, 'random best': [b for b, h in rand]}))


def run(start, rnd, law):
    F = S.forbid()
    st, _ = S.grow_rounds(F.supports_of(S.census_starts()[start]), law, rnd)
    P = S.Pattern(st[rnd]); x = S.states(P, law); X = S.bits(x, list(range(P.D))); dj = S.disjoint_matrix(P)
    allc = list(range(P.D)); out = []
    import itertools
    for u, v in itertools.combinations(range(P.D), 2):
        w = (1 - 2 * (((x >> np.uint64(u)) ^ (x >> np.uint64(v))) & np.uint64(1)).astype(np.int8)).astype(np.int8)
        Z, m1, M11 = S.pair_tables(X, w); M = S.four(Z, m1, M11)
        r1 = S.best_chsh(Z, M, allc, allc, dj, 'R1'); r2 = S.best_chsh(Z, M, allc, allc, dj, 'R2')
        out.append({'u': u, 'v': v, 'Z': Z, 'R1 best': r1['best'], 'R1 hits': len(r1['hits']), 'R2 best': r2['best'], 'R2 hits': len(r2['hits'])})
    print(json.dumps({'start': start, 'round': rnd, 'law': law, 'K': P.K, 'D': P.D, 'N': len(x), 'two-distinction products of single signs': out}))


if __name__ == '__main__':
    if '--matchings' in sys.argv:
        run_matchings(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], json.loads(sys.argv[sys.argv.index('--matchings') + 1]),
                      sys.argv[sys.argv.index('--matchings') + 2])
    else:
        (run_cz if '--cz' in sys.argv else run)(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
