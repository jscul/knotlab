"""Route (b): closed-manifold counts from link counts.

For a framed link (L, f) with c components, let L^(k) = every component replaced by k
parallel copies with pairwise linking f_i.  Then
    H(L^(k)) = sum_{a+b+c'=c} N_{a,b,c'} (6^a 2^b 3^c')^(k-1),
where N_{a,b,c'} counts rho in Hom(pi_L, S3) whose framed longitudes rho(lambda_i mu_i^f_i)
are a identities, b transpositions and c' 3-cycles.  The nodes 6^a 2^b 3^c' = 2^(a+b) 3^(a+c')
are distinct, so k = 1..(c+1)(c+2)/2 determine every N; N_{c,0,0} = |Hom(pi_1(S^3_f(L)), S3)|.
Here the left side is computed DIRECTLY on the cabled braids (sector method) for c <= 2,
and compared with the direct count of rho with all framed longitudes trivial and with
known values.
"""
import sys
from fractions import Fraction
sys.path.insert(0, '.')
from braidlab import *
from test_cable import seifert_long


def solve(nodes, rhs):
    K = len(nodes)
    A = [[Fraction(x) ** k for x in nodes] + [Fraction(r)] for k, r in enumerate(rhs)]
    for i in range(K):
        piv = next(j for j in range(i, K) if A[j][i] != 0)
        A[i], A[piv] = A[piv], A[i]
        for j in range(K):
            if j != i and A[j][i] != 0:
                fac = A[j][i] / A[i][i]
                A[j] = [x - fac * y for x, y in zip(A[j], A[i])]
    return [A[i][K] / A[i][i] for i in range(K)]


def closed_direct(word, n, framing):
    tot = 0
    for fp in fixed_points(word, n):
        labels = [ELTS[x] for x in fp]
        if all(mul(lam, power(m, framing[k])) == E for k, (m, lam) in enumerate(seifert_long(word, n, labels, 1))):
            tot += 1
    return tot


def histogram_formula(word, n, framing, k):
    tot = 0
    for fp in fixed_points(word, n):
        labels = [ELTS[x] for x in fp]
        w = 1
        for kk, (m, lam) in enumerate(seifert_long(word, n, labels, 1)):
            w *= CENT[mul(lam, power(m, framing[kk]))] ** (k - 1)
        tot += w
    return tot


def recover_closed(word, n, framing, direct_links=True):
    c = len(components(word, n))
    profiles = [(a, b, c - a - b) for a in range(c + 1) for b in range(c + 1 - a)]
    nodes = [6 ** a * 2 ** b * 3 ** cc for a, b, cc in profiles]
    assert len(set(nodes)) == len(nodes)
    rhs = []
    for k in range(1, len(nodes) + 1):
        if direct_links:
            cw, cn = cable(word, n, [k] * c, framing)
            rhs.append(count_psi(cw, cn))
        else:
            rhs.append(histogram_formula(word, n, framing, k))
    sol = solve(nodes, rhs)
    return sol[profiles.index((c, 0, 0))], rhs


if __name__ == '__main__':
    cases = [
        ('unknot f=0  (S1xS2, 6)', [], 1, [0], 6),
        ('unknot f=2  (L(2,1), 4)', [], 1, [2], 4),
        ('unknot f=3  (L(3,1), 3)', [], 1, [3], 3),
        ('unknot f=6  (L(6,1), 6)', [], 1, [6], 6),
        ('unknot f=1  (S3, 1)', [], 1, [1], 1),
        ('trefoil f=0 (12)', [1, 1, 1], 2, [0], 12),
        ('trefoil f=1 (homology sphere, 1)', [1, 1, 1], 2, [1], 1),
        ('trefoil f=-1 (homology sphere, 1)', [1, 1, 1], 2, [-1], 1),
        ('trefoil f=6', [1, 1, 1], 2, [6], None),
        ('trefoil f=-6', [1, 1, 1], 2, [-6], None),
        ('Hopf f=(0,0) (S3, 1)', [1, 1], 2, [0, 0], 1),
        ('Hopf f=(2,2) (L(3,.), 3)', [1, 1], 2, [2, 2], 3),
        ('Hopf f=(3,3) (L(8,.), 4)', [1, 1], 2, [3, 3], 4),
        ('Hopf f=(1,1) (S1xS2: |H1| infinite, 6)', [1, 1], 2, [1, 1], 6),
        ('Hopf f=(4,1) (L(3,.), 3)', [1, 1], 2, [4, 1], 3),
        ('Hopf f=(7,1) (L(6,.), 6)', [1, 1], 2, [7, 1], 6),
        ('T(2,4) f=(0,0)', [1, 1, 1, 1], 2, [0, 0], None),
        ('T(2,4) f=(1,-1)', [1, 1, 1, 1], 2, [1, -1], None),
        ('trefoil+meridian f=(0,0)', [1, 1, 1, 2, 2], 3, [0, 0], None),
        ('trefoil+meridian f=(6,1)', [1, 1, 1, 2, 2], 3, [6, 1], None),
    ]
    allok = True
    for name, w, n, fr, known in cases:
        rec, rhs = recover_closed(w, n, fr, direct_links=True)
        d = closed_direct(w, n, fr)
        ok = (rec == d) and (known is None or known == d)
        allok &= ok
        print(f'{name:42s} interpolated={rec} direct={d} known={known} H(L^(k)),k=1..={rhs[:4]}... {"OK" if ok else "FAIL"}')
    # three components: Borromean rings with 0-framings = T^3 (48 commuting triples);
    # the 10 cable levels are evaluated with the (verified) cabling formula.
    for name, w, n, fr, known in [('Borromean f=(0,0,0) = T^3 (48)', [1, -2] * 3, 3, [0, 0, 0], 48),
                                   ('chain3 f=(0,0,0)', [1, 1, 2, 2], 3, [0, 0, 0], None),
                                   ('Borromean f=(1,1,1)', [1, -2] * 3, 3, [1, 1, 1], None)]:
        rec, rhs = recover_closed(w, n, fr, direct_links=False)
        d = closed_direct(w, n, fr)
        # spot-check the first two levels directly on the cabled links
        spot = [count_psi(*cable(w, n, [k] * 3, fr)) for k in (1, 2)]
        ok = rec == d and (known is None or known == d) and spot == rhs[:2]
        allok &= ok
        print(f'{name:42s} interpolated={rec} direct={d} known={known} levels 1-2 direct={spot} formula={rhs[:2]} {"OK" if ok else "FAIL"}')
    print('ALL OK' if allok else 'SOME FAILED')
