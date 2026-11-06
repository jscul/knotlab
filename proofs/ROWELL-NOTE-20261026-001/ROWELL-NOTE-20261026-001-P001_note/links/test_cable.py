"""Check the satellite formulas used in the reduction.

(A) cabling:  H(L with component i replaced by k_i parallel copies, framing f_i)
              = sum_{rho in Hom(pi_L, S3)} prod_i |C(rho(lambda_i mu_i^{f_i}))|^{k_i - 1}
(B) local knots: H(L # T(2,3) on component i) = sum_rho 3^{[rho(mu_i) is a transposition]},
    and the trefoil does not change the image of any longitude.
Left sides are computed directly on the new braid (sector method, checked against brute
force where small); right sides by enumerating fixed points of the original braid.
"""
import sys, random
sys.path.insert(0, '.')
from braidlab import *


def seifert_long(word, n, labels, conv):
    """conv in {+1,-1}: lambda_S = (P mu^{-w})^{conv}."""
    comps, lk, wr = linking_and_writhe(word, n)
    out = []
    for k, (m, P) in enumerate(longitudes(word, n, labels)):
        lam = mul(P, power(m, -wr[k]))
        out.append((m, lam if conv == 1 else inv(lam)))
    return out


def formula_cable(word, n, ncopies, framing, conv):
    tot = 0
    for fp in fixed_points(word, n):
        labels = [ELTS[x] for x in fp]
        w = 1
        for k, (m, lam) in enumerate(seifert_long(word, n, labels, conv)):
            if ncopies[k] > 1:
                w *= CENT[mul(lam, power(m, framing[k]))] ** (ncopies[k] - 1)
        tot += w
    return tot


def formula_trefoil(word, n, comp, j):
    tot = 0
    for fp in fixed_points(word, n):
        labels = [ELTS[x] for x in fp]
        comps = components(word, n)
        m = labels[comps[comp][0]]
        tot += 3 ** (j * m[1])
    return tot


if __name__ == '__main__':
    random.seed(3)
    base = {
        'unknot': ([], 1), 'Hopf': ([1, 1], 2), 'trefoil': ([1, 1, 1], 2), 'fig8': ([1, -2, 1, -2], 3),
        'T(2,4)': ([1] * 4, 2), 'Borromean': ([1, -2] * 3, 3), 'Whitehead?': ([1, 1, -2, 1, 1, -2], 3),
        'T(2,5)': ([1] * 5, 2), '5_2-ish': ([1, 1, 1, 2, -1, 2], 3), 'chain3': ([1, 1, 2, 2], 3),
    }
    res = {1: [0, 0], -1: [0, 0]}
    ncheck = 0
    for name, (w, n) in base.items():
        comps = components(w, n)
        c = len(comps)
        for trial in range(6):
            ncopies = [random.choice([1, 2, 2, 3]) for _ in range(c)]
            if all(k == 1 for k in ncopies):
                ncopies[0] = 2
            framing = [random.choice([0, 0, 1, -1, 2, -2, 3]) for _ in range(c)]
            cw, cn = cable(w, n, ncopies, framing)
            direct = count_psi(cw, cn)
            if cn <= 6:
                assert count_brute(cw, cn) == direct
            # the cable has the predicted number of components and pairwise framings
            cc, clk, cwr = linking_and_writhe(cw, cn)
            assert len(cc) == sum(ncopies)
            for conv in (1, -1):
                f = formula_cable(w, n, ncopies, framing, conv)
                res[conv][0] += 1
                res[conv][1] += (f == direct)
            ncheck += 1
            print(f'{name:10s} copies={ncopies} framing={framing} direct={direct} '
                  f'formula(+)={formula_cable(w, n, ncopies, framing, 1)} formula(-)={formula_cable(w, n, ncopies, framing, -1)}')
    print('cabling formula matches (convention +1):', res[1], ' (convention -1):', res[-1])
    # trefoil formula
    okt = 0
    for name, (w, n) in base.items():
        comps = components(w, n)
        for comp in range(len(comps)):
            for j in (1, 2):
                reps = [comps[k][0] for k in range(len(comps))]
                tw, tn, _ = tie_trefoils(w, n, [reps[comp]], j)
                direct = count_psi(tw, tn)
                if tn <= 6:
                    assert count_brute(tw, tn) == direct
                f = formula_trefoil(w, n, comp, j)
                assert f == direct, (name, comp, j, f, direct)
                okt += 1
    print('trefoil formula verified in', okt, 'cases')
    # trefoil + cable combined (longitude of the knotted component unchanged)
    okc = 0
    for name, (w, n) in base.items():
        comps = components(w, n)
        c = len(comps)
        reps = [comps[k][0] for k in range(c)]
        for comp in range(c):
            tw, tn, newreps = tie_trefoils(w, n, [reps[comp]], 1)
            # identify components of the knotted braid with the original ones
            tcomps = components(tw, tn)
            ncopies = [1] * len(tcomps)
            # cable the knotted component with 2 copies, 0-framing
            target = [k for k, cc in enumerate(tcomps) if newreps[0] in cc][0]
            ncopies[target] = 2
            cw, cn = cable(tw, tn, ncopies, [0] * len(tcomps))
            direct = count_psi(cw, cn)
            # formula on the ORIGINAL link: weight 3^{[mu_comp transposition]} * |C(lambda_comp)|
            tot = 0
            for fp in fixed_points(w, n):
                labels = [ELTS[x] for x in fp]
                sl = seifert_long(w, n, labels, 1)
                m, lam = sl[comp]
                tot += 3 ** m[1] * CENT[lam]
            assert tot == direct, (name, comp, tot, direct)
            okc += 1
    print('trefoil-then-2-cable formula verified in', okc, 'cases')
