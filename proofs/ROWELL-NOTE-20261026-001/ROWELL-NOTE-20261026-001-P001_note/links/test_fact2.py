"""Check (1) the sign-sector method against brute force and (2) the topological formula
   |Z^1(pi_L; F3^{psi_S})| = 3 * 3^{d_S + e_S - r_S}   (S nonempty),   3^c for S empty,
where d_S = dim H_1(Sigma_2(L_S); F3) (from Fox 3-colourings of the sublink: 3^{1+d_S}),
e_S = #{j not in S : lk(K_j, L_S) even}, r_S = rank of the holonomy map
{Fox colourings of L_S} -> F3^{even j}, colouring -> rotation part of rho(K_j).
"""
import sys, itertools, random, math
sys.path.insert(0, '.')
from braidlab import *


def fox_basis(sub, ns):
    M = sector_matrix(sub, ns, [1] * ns)
    return nullspace_mod3((M - np.eye(ns, dtype=np.int64)) % 3)


def holonomy_rank(word, n, S_strands, evenK, comps):
    """S_strands: set of strand ids in L_S; evenK: list of component indices (not in S, even lk)."""
    keep = sorted(S_strands)
    sub, ns = sub_braid(word, n, keep)
    basis = fox_basis(sub, ns)
    pos_of = {sid: k for k, sid in enumerate(keep)}  # sub-braid top position of each kept id
    rows = []
    for v in basis:
        lab = {sid: int(v[pos_of[sid]]) for sid in keep}  # Fox colour of each S strand at the top
        under_lists = {p: [] for p in range(n)}
        order = list(range(n))
        for g in word:
            i = abs(g) - 1
            a, b = order[i], order[i + 1]
            over, under = (a, b) if g > 0 else (b, a)
            if over in lab and under in lab:
                lab[under] = (2 * lab[over] - lab[under]) % 3
            elif over in lab and under not in lab:
                under_lists[under].append(lab[over])
            order[i], order[i + 1] = b, a
        # labels must return (closure) -- check consistency
        row = []
        for j in evenK:
            h = E
            for p in comps[j]:
                for a_ in under_lists[p]:
                    h = mul(h, (a_, 1))
            assert h[1] == 0
            row.append(h[0])
        rows.append(row)
    if not rows or not evenK:
        return 0, len(basis)
    return rank_mod3(np.array(rows)), len(basis)


def check_formula(word, n, verbose=False):
    comps, lk, wr = linking_and_writhe(word, n)
    c = len(comps)
    ci = {}
    for k, comp in enumerate(comps):
        for p in comp:
            ci[p] = k
    tot, sectors = count_psi(word, n, return_sectors=True)
    ok = True
    formula_total = 0
    for psi, T in sectors.items():
        S = [k for k in range(c) if psi[k]]
        if not S:
            pred = 3 ** c
        else:
            S_strands = set(p for k in S for p in comps[k])
            evenK = [j for j in range(c) if j not in S and sum(lk[j, i] for i in S) % 2 == 0]
            r, dimfox = holonomy_rank(word, n, S_strands, evenK, comps)
            d = round(math.log(3 ** dimfox, 3)) - 1
            e = len(evenK)
            pred = 3 ** (1 + d + e - r)
            if verbose:
                print('   S=', S, 'd=', d, 'e=', e, 'r=', r, 'T=', T, 'pred=', pred)
        formula_total += pred
        if pred != T:
            ok = False
    return ok, tot, formula_total


if __name__ == '__main__':
    random.seed(1)
    nb = 0
    # brute force vs sector method on random braids
    for trial in range(150):
        n = random.choice([2, 3, 4, 5])
        L = random.randint(0, 9)
        w = [random.choice([1, -1]) * random.randint(1, n - 1) for _ in range(L)] if n > 1 else []
        b, p = count_brute(w, n), count_psi(w, n)
        assert b == p, (w, n, b, p)
        nb += 1
    print('brute force == sector method on', nb, 'random braids (2-5 strands)')
    # topological formula
    named = {
        'Hopf': ([1, 1], 2), '2-unlink': ([], 2), 'T(2,4)': ([1] * 4, 2), 'T(2,6)': ([1] * 6, 2),
        'Borromean': ([1, -2] * 3, 3), 'T(3,3)': ([1, 2] * 3, 3), 'chain3': ([1, 1, 2, 2], 3),
        'trefoil+meridian': ([1, 1, 1, 2, 2], 3),
    }
    for name, (w, n) in named.items():
        ok, t, f = check_formula(w, n)
        print(f'{name:18s} H={t} formula={f} {"OK" if ok else "FAIL"}')
        assert ok
    # random pure braids = random 'graph links' and random general braids
    cnt = 0
    for trial in range(400):
        n = random.choice([3, 4, 5, 6])
        if trial % 2 == 0:
            w = []
            for _ in range(random.randint(1, 6)):
                i, j = sorted(random.sample(range(n), 2))
                e = random.choice([1, -1, 2])
                g = A_gen(i, j)
                w += g * e if e > 0 else [-x for x in reversed(g)]
        else:
            w = [random.choice([1, -1]) * random.randint(1, n - 1) for _ in range(random.randint(2, 12))]
        ok, t, f = check_formula(w, n)
        if not ok:
            print('FAIL', w, n)
            check_formula(w, n, verbose=True)
            raise SystemExit
        cnt += 1
    print('topological formula 3*3^(d+e-r) verified sector-by-sector on', cnt, 'random links (3-6 strands)')
