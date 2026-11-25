"""Part 8: the swaps (P16).  (i) the rule for a birth whose parents differ (DH 3.2 step 3, swap: c and c+1 give c+2);
(ii) the closing reading (DH 3.2 step 5, swap: F_B and s); on the named starts, 14 x 11 bases x 3 forms x 2 knot laws;
(iii) the stopping reading (DH 1.1, swap: end at the first round with no birth) on the named starts under arm R (14 laws
x 14 starts x 2 knot laws); and (i) on the census under the seven RELEASE bases and three forms, parity.  The census
counts of P11 under the other stopping reading are derived from part 1's runs (deviations 6) by the summary.
Writes part8.json.

python -B part8.py
"""
from __future__ import annotations

import sys
import time

from dh_common import STARTS_JSON, knots, write, log, n_procs, load_avg
import dh_engine as E
import dh_analysis as A
from dh_census import census, kept_parity

STARS = {k: v['stars'] for k, v in STARTS_JSON['starts'].items()}
NAMED = list(STARTS_JSON['starts'].keys())
LIMIT = 30 * 60
sys.setrecursionlimit(100000)       # deviations 35: lr_core's Bron-Kerbosch recursion on cliques over 1,000 members
KEEP = ('a', 'bprime', 'c', 'd', 'place_rule_last_by_kind', 'wrong_last', 'right_on_every_structure', 'P3', 'P4',
        'knots', 'rounds', 'end', 'counted_step3', 'closing_births', 'births')


def named_job(args):
    start, ln, form, kl = args
    L = E.LAW[ln]
    out = {'start': start, 'law': ln, 'form': form, 'knot_law': kl}
    S0, r0, e0 = E.grow(STARS[start], L, form, kl, R=8, N=3000)
    reg = A.analyze_armw(S0, r0, e0, form, kl, L, keep_wrong=0)
    out['registered'] = {k: reg[k] for k in KEEP}
    S1, r1, e1 = E.grow(STARS[start], L, form, kl, R=8, N=3000, pd_swap=True)
    sw = A.analyze_armw(S1, r1, e1, form, kl, L, keep_wrong=0)
    out['parents_differ_swap'] = {k: sw[k] for k in KEEP}
    S2, r2, e2 = E.grow(STARS[start], L, form, kl, R=8, N=3000, closing_swap=True)
    cl = {'closing_births': sum(1 for x in range(len(S2.places)) if S2.closing[x]), 'rounds': len(r2),
          'knots': len(S2.places), 'end': e2, 'identical_to_registered': S2.places == S0.places}
    if cl['closing_births'] and kl == 'parity':
        xs = [x for x in range(len(S2.places)) if S2.closing[x]]
        tc = S2.born[xs[0]]
        pt = knots.parity_test(E.KS(S2, tc))
        ck = []
        dis = list(pt['disagree'])
        for x in xs:
            ptx = knots.parity_test(E.KS(S2, S2.born[x]))
            dis += ptx['disagree']
            ck.append({'knot': x, 'round': S2.born[x], 'F': S2.F[x], 's': S2.s[x],
                       'fails_parity_after_its_round': x in ptx['fail']})
        cl['closing_knots'] = ck
        cl['parity_fail_after_closing_round'] = pt['fail'][:20]
        cl['parity_disagree'] = dis
        cl['place_rule_after_closing_round'] = E.place_rule(S2, form, t=tc, keep_wrong=0)['by_kind']
        cl['grows_after_closing'] = any(r['births'] for r in r2[tc:])
    out['closing_swap'] = cl
    return out


def stop_job(args):
    start, ln, kl = args
    L = E.LAW[ln]
    S0, r0, e0 = E.grow(STARS[start], L, None, kl, R=8, N=3000)
    S1, r1, e1 = E.grow(STARS[start], L, None, kl, R=8, N=3000, stop='birth')
    a0 = A.analyze_base(S0, r0, e0, with_place=False)
    a1 = A.analyze_base(S1, r1, e1, with_place=False)
    keys = ('counted', 'bprime_fails', 'greatest', 'rounds', 'knots', 'end')
    return {'start': start, 'law': ln, 'knot_law': kl, 'registered': {k: a0[k] for k in keys},
            'first_round_with_no_birth': {k: a1[k] for k in keys},
            'differ': any(a0[k] != a1[k] for k in keys)}


def census_job(idx):
    sys.setrecursionlimit(100000)
    n, gi, loose, stars = census()[idx]
    if not kept_parity(stars):
        return None
    out = {'idx': idx, 'runs': {}, 'errors': []}
    for L in E.RELEASE_BASES:
        for form in E.FORMS:
            try:
                S, recs, end = E.grow(stars, L, form, 'parity', R=8, N=3000, pd_swap=True)
                row = A.analyze_armw(S, recs, end, form, 'parity', L, keep_wrong=0)
                out['runs'][L.name + '|' + form] = {k: row[k] for k in ('a', 'bprime', 'c', 'd',
                                                                         'place_rule_last_by_kind',
                                                                         'right_on_every_structure', 'P3', 'P4',
                                                                         'knots', 'end')}
            except (RecursionError, MemoryError) as e:
                out['errors'].append([L.name, form, type(e).__name__])
    return out


def main():
    import multiprocessing as mp
    procs = n_procs()
    log('part 8, load %.1f, %d processes' % (load_avg(), procs))
    t0 = time.time()
    out = {'part': 8, 'load_at_start': load_avg(), 'processes': procs}
    with mp.Pool(procs) as pool:
        t = time.time()
        out['named'] = pool.map(named_job, [(s, L.name, f, kl) for s in NAMED for L in E.BASES for f in E.FORMS
                                            for kl in ('parity', 'nae')], chunksize=1)
        out['named_seconds'] = round(time.time() - t, 1)
        log('named swaps', out['named_seconds'])
        t = time.time()
        out['stopping'] = pool.map(stop_job, [(s, L.name, kl) for s in NAMED for L in E.LAWS
                                              for kl in ('parity', 'nae')], chunksize=1)
        out['stopping_seconds'] = round(time.time() - t, 1)
        log('stopping swap', out['stopping_seconds'])
        write('part8.json', dict(out, census_parents_differ_swap='not yet run'))
        t = time.time()
        n = len(census())
        handles = [pool.apply_async(census_job, (i,)) for i in range(n)]
        done = {}
        last = time.time()
        while len(done) < n and time.time() - t0 < LIMIT:
            for i, h in enumerate(handles):
                if i not in done and h.ready():
                    done[i] = (h.get(), round(time.time() - t, 1))
            if time.time() - last > 60:
                pre = next((i for i in range(n) if i not in done), n)
                log('census swap: %d of %d finished, prefix %d, load %.1f' % (len(done), n, pre, load_avg()))
                last = time.time()
            time.sleep(0.5)
        pool.terminate()
        prefix = next((i for i in range(n) if i not in done), n)
        rows = [done[i][0] for i in range(prefix) if done[i][0] is not None]
        beyond = [done[i][0] for i in sorted(done) if i >= prefix and done[i][0] is not None]
        out['census_parents_differ_swap'] = {'starts': n, 'prefix_starts': prefix, 'kept_in_prefix': len(rows),
                                             'cut': prefix < n, 'rows': rows,
                                             'finished_beyond_prefix': beyond,
                                             'not_run': [i for i in range(n) if i not in done],
                                             'errors': [[r['idx']] + e for r in rows + beyond for e in r['errors']],
                                             'seconds': round(time.time() - t, 1)}
    out['seconds'] = round(time.time() - t0, 1)
    write('part8.json', out)
    log('part 8 written', out['seconds'])


if __name__ == '__main__':
    main()
