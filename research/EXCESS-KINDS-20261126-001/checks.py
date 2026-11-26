"""checks.py: computed checks for EXCESS-KINDS-20261126-001 (README.md).

    checks.py seven     the seven-knot structure of THIRD-HOLDER-20261123-001B (19/9, both records hidden): its best
                        score over all outcome functions of the records, and the largest change a free sender (a setting
                        that is any function of the sender's own old values) makes in the other reader's complete record,
                        counted from the finish; Theorem K predicts it is above zero
    checks.py random    Theorem K's contrapositive on random product-form models (seeded)"""
import sys, itertools
from fractions import Fraction


def nae(*v): return len(set(v)) > 1
def even(*v): return sum(v) % 2 == 0
def odd(*v): return sum(v) % 2 == 1


def seven():
    names = ['x1', 'x2', 'x3', 's1', 's2', 'h1', 'h2', 'y1', 'y2', 'y3', 'k1', 'k2']
    old = []
    for vals in itertools.product((0, 1), repeat=len(names)):
        d = dict(zip(names, vals))
        if (nae(d['x1'], d['x2'], d['s1']) and nae(d['x1'], d['x3'], d['s2']) and even(d['x2'], d['h1'], d['h2'])
                and odd(d['x3'], d['h1'], d['h2']) and even(d['y2'], d['k1'], d['k2']) and odd(d['s1'], d['k1'], d['k2'])
                and odd(d['y1'], d['y2'], d['y3'], d['s2'])):
            old.append(d)
    assert len(old) == 64, len(old)
    pick = {0: ('x2', 'y2'), 1: ('x3', 'y3')}     # setting 0 takes (x1, x2) / (y1, y2); setting 1 (x1, x3) / (y1, y3)
    def finished(a, b):
        """counted from the finish: every allowed state of the finished structure once; a state is (old, fA, fB)"""
        out = []
        for d in old:
            for fa in (0, 1):
                if not nae(d['x1'], d[pick[a][0]], fa): continue
                for fb in (0, 1):
                    if not nae(d['y1'], d[pick[b][1]], fb): continue
                    out.append((d, fa, fb))
        return out
    recA = lambda d, fa: (d['x1'], d['x2'], d['x3'], fa)
    recB = lambda d, fb: (d['y1'], d['y2'], d['y3'], fb)
    # hidden: each record's distribution does not depend on the other's setting
    def dist(states, side):
        c = {}
        for d, fa, fb in states:
            k = recA(d, fa) if side == 'A' else recB(d, fb)
            c[k] = c.get(k, 0) + 1
        n = sum(c.values()); return {k: Fraction(v, n) for k, v in c.items()}
    F = {(a, b): finished(a, b) for a in (0, 1) for b in (0, 1)}
    hidden = all(dist(F[a, 0], 'A') == dist(F[a, 1], 'A') for a in (0, 1)) and \
             all(dist(F[0, b], 'B') == dist(F[1, b], 'B') for b in (0, 1))
    # best score over outcome functions: outcome of a reader is a function of its record (16 records, setting-wise)
    # exact maximization by brute force over Alice's two functions for each of Bob's, is too large; use the joint
    # record tables and the standard reduction: for fixed Bob functions the best Alice function is pointwise
    recsA = sorted({recA(d, fa) for st in F.values() for d, fa, fb in st})
    recsB = sorted({recB(d, fb) for st in F.values() for d, fa, fb in st})
    def joint(a, b):
        J = {}
        for d, fa, fb in F[a, b]:
            k = (recA(d, fa), recB(d, fb)); J[k] = J.get(k, 0) + 1
        n = len(F[a, b]); return {k: Fraction(v, n) for k, v in J.items()}
    Jt = {(a, b): joint(a, b) for a in (0, 1) for b in (0, 1)}
    # best score over outcome functions (a lower bound by alternating best responses from seeded starts; the record's
    # exact value is 19/9): for fixed Bob functions the best Alice function is pointwise, and the other way round
    import random
    rng = random.Random(20261126)
    coefs = [dict(zip([(0, 0), (0, 1), (1, 0), (1, 1)], sg)) for sg in [(1, 1, 1, -1), (1, 1, -1, 1), (1, -1, 1, 1), (-1, 1, 1, 1)]]
    def score(ga, gb, coef):
        return sum(coef[a, b] * p * ga[a][ra] * gb[b][rb] for a in (0, 1) for b in (0, 1) for (ra, rb), p in Jt[a, b].items())
    best = Fraction(-10)
    for coef in coefs:
        for _ in range(40):
            gb = [{r: rng.choice((1, -1)) for r in recsB} for _ in (0, 1)]
            for _ in range(20):
                ga = []
                for a in (0, 1):
                    acc = {}
                    for b in (0, 1):
                        for (ra, rb), p in Jt[a, b].items(): acc[ra] = acc.get(ra, 0) + coef[a, b] * p * gb[b][rb]
                    ga.append({r: (1 if acc.get(r, 0) >= 0 else -1) for r in recsA})
                gb = []
                for b in (0, 1):
                    acc = {}
                    for a in (0, 1):
                        for (ra, rb), p in Jt[a, b].items(): acc[rb] = acc.get(rb, 0) + coef[a, b] * p * ga[a][ra]
                    gb.append({r: (1 if acc.get(r, 0) >= 0 else -1) for r in recsB})
            best = max(best, score(ga, gb, coef))
    # free sender: Alice's setting any function of her old values (x1, x2, x3); Bob's complete record distribution
    vis = sorted({(d['x1'], d['x2'], d['x3']) for d in old})
    worst = Fraction(0)
    for b in (0, 1):
        ds = []
        for pol in itertools.product((0, 1), repeat=len(vis)):
            pi = dict(zip(vis, pol)); c = {}
            for d in old:
                a = pi[(d['x1'], d['x2'], d['x3'])]
                for fa in (0, 1):
                    if not nae(d['x1'], d[pick[a][0]], fa): continue
                    for fb in (0, 1):
                        if not nae(d['y1'], d[pick[b][1]], fb): continue
                        k = recB(d, fb); c[k] = c.get(k, 0) + 1
            n = sum(c.values()); ds.append({k: Fraction(v, n) for k, v in c.items()})
        for x in ds:
            keys = set(x) | set(ds[0])
            worst = max(worst, sum(abs(x.get(k, 0) - ds[0].get(k, 0)) for k in keys) / 2)
    print(f'seven-knot structure: {len(old)} old states; records hidden at fixed settings: {hidden}; best score found over '
          f'outcome functions of the records (a lower bound): {best}; largest change of the other record under a free sender: {worst}')


def random_models(trials=20000, seed=20261126):
    """Theorem K's contrapositive on random product-form models: alphabets of two or three old values a reader, weights
    0 to 2, completions 0 to 2 with H5 (completed at both settings or neither), outcomes any function of the setting,
    the old value and the fresh value; floats with a 1e-9 margin"""
    import random, numpy as np
    rng = random.Random(seed)
    def tables(mu, g1, g2, o1, o2):
        P = {}
        for a in (0, 1):
            for b in (0, 1):
                T = np.zeros((2, 2))
                for v in range(len(mu)):
                    for u in range(len(mu[0])):
                        for r1 in (0, 1):
                            for r2 in (0, 1):
                                T[o1[a][v][r1], o2[b][u][r2]] += mu[v][u] * g1[a][v][r1] * g2[b][u][r2]
                if T.sum() == 0: return None
                P[a, b] = T / T.sum()
        E = {k: P[k][0, 0] + P[k][1, 1] - P[k][0, 1] - P[k][1, 0] for k in P}
        return max(abs(sum(E.values()) - 2 * E[k]) for k in E)
    def sig(mu, g1, g2):
        V, U = len(mu), len(mu[0]); worst = 0
        for b in (0, 1):
            ds = []
            for pi in itertools.product((0, 1), repeat=V):
                M = np.zeros((U, 2))
                for v in range(V):
                    t = sum(g1[pi[v]][v])
                    for u in range(U):
                        for r2 in (0, 1): M[u, r2] += mu[v][u] * t * g2[b][u][r2]
                if M.sum() == 0: return None
                ds.append(M / M.sum())
            worst = max(worst, max(np.abs(d - ds[0]).sum() / 2 for d in ds))
        return worst
    hits = quiet = 0; best = 0
    for _ in range(trials):
        V = U = rng.choice((2, 3))
        mu = [[rng.randint(0, 2) for _ in range(U)] for _ in range(V)]
        g1 = [[[rng.randint(0, 2) for _ in (0, 1)] for _ in range(V)] for _ in (0, 1)]
        g2 = [[[rng.randint(0, 2) for _ in (0, 1)] for _ in range(U)] for _ in (0, 1)]
        if not (all((sum(g1[0][v]) > 0) == (sum(g1[1][v]) > 0) for v in range(V)) and
                all((sum(g2[0][u]) > 0) == (sum(g2[1][u]) > 0) for u in range(U))): continue
        o1 = [[[rng.randint(0, 1) for _ in (0, 1)] for _ in range(V)] for _ in (0, 1)]
        o2 = [[[rng.randint(0, 1) for _ in (0, 1)] for _ in range(U)] for _ in (0, 1)]
        c = tables(mu, g1, g2, o1, o2)
        if c is None or c <= 2 + 1e-9: continue
        s1, s2 = sig(mu, g1, g2), sig([list(x) for x in zip(*mu)], g2, g1)
        if s1 is None or s2 is None: continue
        hits += 1; best = max(best, c)
        if max(s1, s2) < 1e-12: quiet += 1
    print(f'random product-form models above CHSH 2: {hits} (largest {best:.4f}); with no free signalling: {quiet}')


if __name__ == '__main__':
    {'seven': seven, 'random': random_models}[sys.argv[1]]()
