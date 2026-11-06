"""Independent replay of the UT3(F4) x| C3 surgery-count claims (claims 1-5).

Run:  python3 run_replay.py            (writes results.json and prints a log)

Everything here is written from scratch with the standard library; no code
from the repository is imported.  See f4.py, group.py, braids.py,
homcount.py, cohomology.py, gadget.py.
"""
import json
import random
import sys
import time

import f4
import group
from braids import ClosedBraid, figure_eight_sum, borromean_insertions
from homcount import count_homs, check_longitude
from cohomology import (TwistedData, leaf_functionals, predicted_tensor,
                        compare_pair_conditions, linear_identification)
import gadget

RESULTS = {}


def log(*args):
    print(*args, flush=True)


def la_count(knot, p=3):
    """1 + sum over both nontrivial characters of |B1|^2 N |Z1(centre)|."""
    total, per = 1, []
    for k_mu in (1, 2):
        D = TwistedData(knot, k_mu, p)
        N = D.count_pairs()
        total += D.hom_count_term(N)
        per.append({'k_mu': k_mu, 'd': D.d, 'N': N, 'dim_ker_delta': D.ker_delta_dim,
                    'surgery_relator_free_on_cocycles': D.surgery_free_on_cocycles})
    return total, per


# ------------------------------------------------------------------ claim 1
CLAIM1 = [('3_1', 2, [1, 1, 1], 3585),
          ('4_1', 3, [1, -2, 1, -2], 8193),
          ('5_2', 3, [1, 1, 1, 2, -1, 2], 129),
          ('8_18', 3, [1, -2] * 4, 229377),
          ('3_1#3_1', 3, [1, 1, 1, 2, 2, 2], 100353)]


def claim1():
    out = []
    for name, n, word, claimed in CLAIM1:
        row = {'knot': name, 'braid': word, 'claimed': claimed, 'runs': []}
        for chi in (1, -1):
            K = ClosedBraid(n, word, chi)
            knot_group_homs = check_longitude(K)
            for p in (3, -3):
                literal, split = count_homs(K, p, literal=True)
                weighted, _ = count_homs(K, p, literal=False)
                la, per = la_count(K, p)
                d, N = per[0]['d'], per[0]['N']
                row['runs'].append({'chirality': chi, 'surgery': p,
                                    'brute_force_all_x0': literal,
                                    'brute_force_class_weighted': weighted,
                                    'split_by_coset_h^0,h^1,h^2': split,
                                    'linear_algebra_count': la, 'd': d, 'N': N,
                                    'formula_1+128*4^d*N': 1 + 128 * 4 ** d * N,
                                    'per_character': per,
                                    'knot_group_homs_longitude_checked': knot_group_homs})
        r0 = row['runs'][0]
        row['all_runs_agree_with_claim'] = all(
            r['brute_force_all_x0'] == r['brute_force_class_weighted'] == r['linear_algebra_count']
            == r['formula_1+128*4^d*N'] == claimed for r in row['runs'])
        log('claim1 %-8s brute=%d  d=%d N=%d  claimed=%d  agree(all chiralities, +-3)=%s'
            % (name, r0['brute_force_all_x0'], r0['d'], r0['N'], claimed,
               row['all_runs_agree_with_claim']))
        out.append(row)
    return out


# ------------------------------------------------------------------ claim 2
def claim2(kmax=10, brute_kmax=3):
    out = []
    for k in range(1, kmax + 1):
        n, word = figure_eight_sum(k)
        K = ClosedBraid(n, word)
        D1, D2 = TwistedData(K, 1), TwistedData(K, 2)
        rec = {'k': k, 'strands': n, 'd': D1.d, 'd_conjugate_character': D2.d,
               'obstruction_identically_zero': D1.is_identically_zero() and D2.is_identically_zero()}
        if k <= 6:
            rec['N_counted'] = D1.count_pairs()
        if k <= brute_kmax:
            rec['brute_force_count'] = count_homs(K, 3)[0]
            rec['formula_with_N=16^k'] = 1 + 128 * 4 ** k * 16 ** k
        rec['ok'] = (D1.d == D2.d == k and rec['obstruction_identically_zero']
                     and rec.get('N_counted', 16 ** k) == 16 ** k
                     and rec.get('brute_force_count', 0) == rec.get('formula_with_N=16^k', 0))
        log('claim2 k=%2d d=%d T==0:%s %s %s ok=%s' % (
            k, D1.d, rec['obstruction_identically_zero'],
            ('N=%d' % rec['N_counted']) if 'N_counted' in rec else '',
            ('brute=%d' % rec['brute_force_count']) if 'brute_force_count' in rec else '',
            rec['ok']))
        out.append(rec)
    return out


# ------------------------------------------------------------- claims 3, 4
def steering_test(k, specs, k_mu=1, chi=1, order='right_to_left'):
    """Direct obstruction of the modified knot against the leaf prediction."""
    n, base = figure_eight_sum(k)
    word, starts = borromean_insertions(base, specs)
    Kb, Km = ClosedBraid(n, base, chi), ClosedBraid(n, word, chi)
    Db, Dm = TwistedData(Kb, k_mu), TwistedData(Km, k_mu)
    same_cocycles = f4.same_span(Db.Z1, Dm.Z1, n)
    leaves = [leaf_functionals(Kb, Dm.V, k_mu, L, o, order=order) for L, o in specs]
    # the inserted blocks act trivially on cocycle values: leaves read on the
    # modified knot just before / just after each block agree with the base
    blocks_trivial = all(
        leaf_functionals(Km, Dm.V, k_mu, s, o, order=order) == lv
        == leaf_functionals(Km, Dm.V, k_mu, s + 54, o, order=order)
        for s, (L, o), lv in zip(starts, specs, leaves))
    Tp = predicted_tensor(leaves, Dm.d)
    N_direct, N_pred, differ = compare_pair_conditions(Dm.T, Tp, Dm.d)
    exists, dimS, rank_on_S = linear_identification(Dm.T, Tp, Dm.d, Dm.q)
    ok = (same_cocycles and N_direct == N_pred and differ == 0 and exists
          and dimS == rank_on_S)
    return {'k': k, 'specs': specs, 'k_mu': k_mu, 'chirality': chi, 'order': order,
            'd': Dm.d, 'N_direct': N_direct, 'N_predicted': N_pred,
            'lines_a_with_different_solution_spaces': differ,
            'linear_identification_exists': exists, 'dim_span_predicted': dimS,
            'rank_of_identification_on_span': rank_on_S,
            'cocycle_space_unchanged': same_cocycles,
            'inserted_blocks_act_trivially_on_cocycles': blocks_trivial,
            'nontrivial': N_direct != 16 ** Dm.d or N_pred != 16 ** Dm.d, 'ok': ok}


CLAIM3 = [(9, [(6, 1), (14, 5), (22, 9)], 45162496),
          (9, [(13, 1), (21, 5), (29, 9)], 45162496),
          (6, [(6, 1), (10, 3)], 326656)]


def claim3():
    out = []
    for k, specs, claimed in CLAIM3:
        n, base = figure_eight_sum(k)
        word, _ = borromean_insertions(base, specs)
        rec = {'base': '(4_1)^#%d' % k, 'specs': specs, 'claimed_N': claimed,
               'word_length': len(word), 'runs': []}
        for chi in (1, -1):
            K = ClosedBraid(n, word, chi)
            for k_mu in (1, 2):
                D = TwistedData(K, k_mu)
                rec['runs'].append({'chirality': chi, 'k_mu': k_mu, 'd': D.d,
                                    'N': D.count_pairs()})
        rec['steering_prediction'] = steering_test(k, specs)
        rec['ok'] = all(r['N'] == claimed and r['d'] == k for r in rec['runs'])
        log('claim3 %s %s d=%d N=%d claimed=%d ok=%s | steering: N_pred=%d ok=%s'
            % (rec['base'], specs, rec['runs'][0]['d'], rec['runs'][0]['N'], claimed,
               rec['ok'], rec['steering_prediction']['N_predicted'],
               rec['steering_prediction']['ok']))
        out.append(rec)
    return out


def claim4(n_random=150, seed=20261026):
    """Steering law on NEW insertions (the claimed configurations excluded):
    (a) every single insertion on (4_1)^#5, #6, #7;
    (b) every pair and triple (distinct levels) of the single insertions that
        are nontrivial in (a), so that several insertions interact;
    (c) random 2- and 3-insertion configurations on (4_1)^#5, #6;
    then a diagnostic of the conventions on a sample from (b)."""
    from itertools import combinations
    claimed = {(k, tuple(s)) for k, s, _ in CLAIM3}
    families = {'a_single': [], 'b_interacting': [], 'c_random': []}
    nontrivial_singles = {}
    for k in (5, 6, 7):
        n, base = figure_eight_sum(k)
        for L in range(len(base)):
            for o in range(n - 8):
                families['a_single'].append((k, [(L, o)]))
    rng = random.Random(seed)
    while len(families['c_random']) < n_random:
        k = rng.choice([5, 6])
        n, base = figure_eight_sum(k)
        m = rng.choice([2, 3])
        specs = [(L, rng.randrange(n - 8)) for L in sorted(rng.sample(range(len(base)), m))]
        if (k, tuple(specs)) not in claimed:
            families['c_random'].append((k, specs))
    stats, histogram, failures, examples = {}, {}, [], []

    def run(family, k, specs):
        r = steering_test(k, specs)                     # the claim's convention
        s = stats.setdefault(family, {'configs': 0, 'nontrivial': 0, 'ok': 0})
        s['configs'] += 1
        s['nontrivial'] += r['nontrivial']
        s['ok'] += r['ok']
        if not (r['ok'] and r['inserted_blocks_act_trivially_on_cocycles']):
            failures.append(r)
        if r['nontrivial']:
            key = '%s k=%d m=%d d=%d N=%d' % (family, k, len(specs), r['d'], r['N_direct'])
            histogram[key] = histogram.get(key, 0) + 1
            if family == 'b_interacting' and len(examples) < 10:
                examples.append({x: r[x] for x in ('k', 'specs', 'd', 'N_direct', 'N_predicted')})
        return r

    for k, specs in families['a_single']:
        if run('a_single', k, specs)['nontrivial']:
            nontrivial_singles.setdefault(k, []).append(specs[0])
    for k, singles in sorted(nontrivial_singles.items()):
        for m in (2, 3):
            for combo in combinations(singles, m):
                if len({L for L, _ in combo}) == m and (k, tuple(sorted(combo))) not in claimed:
                    families['b_interacting'].append((k, sorted(combo)))
    for k, specs in families['b_interacting']:
        run('b_interacting', k, specs)
    for k, specs in families['c_random']:
        run('c_random', k, specs)
    # conventions: other character, mirror reading, reversed product order
    variants = {}
    sample = random.Random(seed + 1).sample(families['b_interacting'], 120)
    for k_mu, chi, order in [(1, 1, 'right_to_left'), (2, 1, 'right_to_left'),
                             (1, 1, 'left_to_right'), (1, -1, 'right_to_left'),
                             (1, -1, 'left_to_right')]:
        v = {'configs': 0, 'nontrivial': 0, 'ok': 0}
        for k, specs in sample:
            r = steering_test(k, specs, k_mu, chi, order)
            v['configs'] += 1
            v['nontrivial'] += r['nontrivial']
            v['ok'] += r['ok']
        variants['k_mu=%d chirality=%+d order=%s' % (k_mu, chi, order)] = v
    log('claim4 nontrivial single insertions:', nontrivial_singles)
    log('claim4 stated convention (chirality +1, w^2, x_{q+2}x_{q+1}x_q):', stats,
        'failures:', len(failures))
    for key in sorted(histogram):
        log('claim4   nontrivial', key, 'x', histogram[key])
    for name, v in variants.items():
        log('claim4 variant (120 configs from b)', name, v)
    for e in examples:
        log('claim4 example', e)
    return {'stated_convention': stats, 'nontrivial_singles': nontrivial_singles,
            'nontrivial_histogram': histogram, 'failures': failures,
            'examples': examples, 'variants_on_120_interacting_configs': variants}


# ------------------------------------------------------------------ claim 5
def claim5(naive=True):
    out = []
    for name, (n, edges) in gadget.GRAPHS.items():
        m = len(edges)
        gadget.check_alternating(n, edges)
        count = gadget.count_by_rank(n, edges)
        Z = gadget.potts_Z_fk(n, edges)
        rec = {'graph': name, 'n': n, 'm': m, 'D': n + 2 * m, 'count': count,
               'Z(64,15)': Z, 'rhs_4^(2m-n)Z': 4 ** (2 * m - n) * Z}
        if n <= 3:
            rec['Z_bruteforce_colourings'] = gadget.potts_Z_bruteforce(n, edges)
        if naive and n + 2 * m <= 7:
            rec['count_naive_all_pairs'] = gadget.count_naive_gray(n, edges)
        rec['ok'] = (count == rec['rhs_4^(2m-n)Z']
                     and rec.get('Z_bruteforce_colourings', Z) == Z
                     and rec.get('count_naive_all_pairs', count) == count)
        log('claim5 %-18s count=%d  4^(2m-n)Z(64,15)=%d  naive=%s ok=%s'
            % (name, count, rec['rhs_4^(2m-n)Z'], rec.get('count_naive_all_pairs'), rec['ok']))
        out.append(rec)
    return out


def main():
    t0 = time.time()
    f4.self_check()
    log('group classes', group.self_check())
    timings = {}
    for name, fn in [('claim1', claim1), ('claim2', claim2), ('claim3', claim3),
                     ('claim4', claim4), ('claim5', claim5)]:
        t = time.time()
        RESULTS[name] = fn()
        timings[name] = round(time.time() - t, 2)
        log('%s done in %.1fs' % (name, timings[name]))
    RESULTS['timings_seconds'] = timings
    RESULTS['total_seconds'] = round(time.time() - t0, 2)
    RESULTS['python'] = sys.version
    with open('results.json', 'w') as fh:
        json.dump(RESULTS, fh, indent=1, default=str)
    log('total %.1fs' % RESULTS['total_seconds'])


if __name__ == '__main__':
    main()
