"""Aside: class-2 nilpotent targets on links.  By Milnor, pi_L / gamma_3 depends only on the
linking numbers, so H_L(G) for G = D4 or Q8 should equal
        4^c * sum_{S subset [c]} 4^{-cutrank(S)},
cutrank(S) = F2-rank of the linking matrix (mod 2) restricted to rows S, columns not in S.
Brute-force check on random braid closures."""
import itertools, random, sys
from fractions import Fraction
import numpy as np
sys.path.insert(0, '.')
from braidlab import components, linking_and_writhe, rank_mod3, A_gen


def perm_group(gens, deg):
    elts = {tuple(range(deg))}
    frontier = list(elts)
    while frontier:
        new = []
        for a in frontier:
            for g in gens:
                b = tuple(a[g[i]] for i in range(deg))
                if b not in elts:
                    elts.add(b)
                    new.append(b)
        frontier = new
    return sorted(elts)


def tables(elts, deg):
    idx = {g: i for i, g in enumerate(elts)}
    mul = np.array([[idx[tuple(a[b[i]] for i in range(deg))] for b in elts] for a in elts])
    inv = np.array([idx[tuple(sorted(range(deg), key=lambda i: a[i]))] for a in elts])
    return mul, inv


D4 = perm_group([(1, 2, 3, 0), (0, 3, 2, 1)], 4)          # symmetries of a square
# Q8 as a permutation group on 8 points (regular representation)
q = {'1': (1, 0, 0, 0)}
def qmul(x, y):
    a1, b1, c1, d1 = x; a2, b2, c2, d2 = y
    return (a1*a2 - b1*b2 - c1*c2 - d1*d2, a1*b2 + b1*a2 + c1*d2 - d1*c2,
            a1*c2 - b1*d2 + c1*a2 + d1*b2, a1*d2 + b1*c2 - c1*b2 + d1*a2)
Qel = [(s*1 if k == 0 else 0, s*1 if k == 1 else 0, s*1 if k == 2 else 0, s*1 if k == 3 else 0)
       for k in range(4) for s in (1, -1)]
Qidx = {x: i for i, x in enumerate(Qel)}
Q8 = perm_group([tuple(Qidx[qmul(g, x)] for x in Qel) for g in Qel], 8)


def count(word, n, mul, inv):
    G = len(mul)
    tup = np.array(list(itertools.product(range(G), repeat=n)), dtype=np.int64)
    cur = tup.copy()
    for g in word:
        i = abs(g) - 1
        a, b = cur[:, i].copy(), cur[:, i + 1].copy()
        if g > 0:
            cur[:, i] = mul[mul[a, b], inv[a]]
            cur[:, i + 1] = a
        else:
            cur[:, i] = b
            cur[:, i + 1] = mul[mul[inv[b], a], b]
    return int(np.all(cur == tup, axis=1).sum())


def rank_mod2(M):
    A = np.array(M, dtype=np.int64) % 2
    r = 0
    rows, cols = A.shape if A.size else (0, 0)
    for c in range(cols):
        piv = next((i for i in range(r, rows) if A[i, c]), None)
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        for i in range(rows):
            if i != r and A[i, c]:
                A[i] ^= A[r]
        r += 1
    return r


def cutrank_formula(lk):
    c = lk.shape[0]
    tot = Fraction(0)
    for S in itertools.product((0, 1), repeat=c):
        rows = [i for i in range(c) if S[i]]
        cols = [i for i in range(c) if not S[i]]
        r = rank_mod2(lk[np.ix_(rows, cols)]) if rows and cols else 0
        tot += Fraction(1, 4 ** r)
    return 4 ** c * tot


if __name__ == '__main__':
    random.seed(11)
    for name, grp in (('D4', D4), ('Q8', Q8)):
        assert len(grp) == 8
        mul, inv = tables(grp, len(grp[0]))
        ok = 0
        for trial in range(60):
            n = random.choice([2, 3, 4, 5])
            if trial % 2:
                w = [random.choice([1, -1]) * random.randint(1, n - 1) for _ in range(random.randint(0, 10))]
            else:
                w = []
                for _ in range(random.randint(1, 5)):
                    i, j = sorted(random.sample(range(n), 2))
                    w += A_gen(i, j) * random.choice([1, 2, 3])
            comps, lk, wr = linking_and_writhe(w, n)
            h = count(w, n, mul, inv)
            f = cutrank_formula(lk)
            assert h == f, (name, w, n, h, f)
            ok += 1
        print(name, ': H_L = 4^c sum_S 4^{-cutrank(S)} verified on', ok, 'random links')
