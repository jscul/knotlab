"""Part 7: the knot test (DH 7; P10) on the last structure of every run of parts 4 and 6 (each run grown again; the
engine is deterministic).  Parity: knots.parity_test (ranks and kernel, which must agree).  Not-all-equal:
knots.nae_decomposed on every knot; knots.nae_direct as a check of the code on knots of at most 7 places in structures
of at most 150 knots.  Writes part7.json.

python -B part7.py
"""
from __future__ import annotations

import time

from dh_common import STARTS_JSON, knots, write, log, n_procs, load_avg
import dh_engine as E
import part6

STARS = {k: v['stars'] for k, v in STARTS_JSON['starts'].items()}
NAMED = list(STARTS_JSON['starts'].keys())


def test_structure(S, kl):
    KS = E.KS(S)
    out = {'knots': KS.n_knots}
    if kl == 'parity':
        pt = knots.parity_test(KS)
        out.update({'fail': pt['fail'][:50], 'n_fail': len(pt['fail']), 'disagree': pt['disagree'][:50],
                    'n_disagree': len(pt['disagree'])})
        return out
    fails, untested = [], []
    dec = {}
    for u in range(KS.n_knots):
        v = knots.nae_decomposed(KS, u)
        dec[u] = v
        if v is None:
            untested.append(u)
        elif not v:
            fails.append(u)
    out.update({'n_fail': len(fails), 'fail': fails[:50], 'n_untested': len(untested), 'untested': untested[:50]})
    if KS.n_knots <= 150:
        small = [u for u in range(KS.n_knots) if len(KS.places[u]) <= 7 and dec[u] is not None]
        dr = knots.nae_direct(KS, small)
        dis = [u for u in small if dr[u] != dec[u]]
        out.update({'direct_checked': len(small), 'n_disagree': len(dis), 'disagree': dis[:50]})
    else:
        out.update({'direct_checked': 0, 'n_disagree': 0, 'disagree': []})
    return out


def job(args):
    kind, start, ln, form, kl = args
    t = time.time()
    if kind == 'part4':
        S, recs, end = E.grow(STARS[start], E.LAW[ln], form, kl, R=8, N=3000)
    else:
        S, recs, end = E.grow(STARS[start], E.LAW[ln], form, 'parity', R=part6.R6, N=10 ** 9)
    r = test_structure(S, kl)
    r.update({'from': kind, 'start': start, 'law': ln, 'form': E.FORM_NAMES[form], 'knot_law': kl,
              'seconds': round(time.time() - t, 2)})
    return r


LIMIT = 30 * 60


def main():
    import multiprocessing as mp
    procs = n_procs()
    log('part 7, load %.1f, %d processes' % (load_avg(), procs))
    t0 = time.time()
    jobs = [('part4', s, L.name, f, kl) for s in NAMED for L in E.BASES for f in (None,) + E.FORMS
            for kl in ('parity', 'nae')]
    jobs += [('part6', s, ln, f, 'parity') for s in part6.RINGS for ln in part6.RLAWS for f in (None, 'PB', 'BB')]
    done = {}
    pool = mp.Pool(procs)
    try:
        handles = [pool.apply_async(job, (j,)) for j in jobs]
        last_log = time.time()
        while len(done) < len(jobs) and time.time() - t0 < LIMIT:
            for i, h in enumerate(handles):
                if i not in done and h.ready():
                    r = h.get()
                    r['finished_after_s'] = round(time.time() - t0, 1)
                    done[i] = r
            if time.time() - last_log > 60:
                pre = next((i for i in range(len(jobs)) if i not in done), len(jobs))
                log('part 7: %d of %d finished, prefix %d, load %.1f' % (len(done), len(jobs), pre, load_avg()))
                last_log = time.time()
            time.sleep(0.5)
    finally:
        pool.terminate()
        pool.join()
    prefix_n = next((i for i in range(len(jobs)) if i not in done), len(jobs))
    res = [done[i] for i in range(prefix_n)]
    beyond = [done[i] for i in sorted(done) if i >= prefix_n]
    not_run = [list(map(str, jobs[i])) for i in range(len(jobs)) if i not in done]
    par = [r for r in res if r['knot_law'] == 'parity']
    nae = [r for r in res if r['knot_law'] == 'nae']
    out = {'part': 7, 'load_at_start': load_avg(), 'processes': procs, 'jobs': len(jobs),
           'cut': prefix_n < len(jobs), 'prefix_jobs': prefix_n,
           'finished_beyond_prefix (run past the registered order of the cut, reported separately)': beyond,
           'beyond_prefix_totals': {
               'parity': {'runs': sum(1 for r in beyond if r['knot_law'] == 'parity'),
                          'fail': sum(r['n_fail'] for r in beyond if r['knot_law'] == 'parity'),
                          'disagree': sum(r['n_disagree'] for r in beyond if r['knot_law'] == 'parity')},
               'nae': {'runs': sum(1 for r in beyond if r['knot_law'] == 'nae'),
                       'knots': sum(r['knots'] for r in beyond if r['knot_law'] == 'nae'),
                       'fail': sum(r['n_fail'] for r in beyond if r['knot_law'] == 'nae'),
                       'untested': sum(r['n_untested'] for r in beyond if r['knot_law'] == 'nae'),
                       'disagree': sum(r['n_disagree'] for r in beyond if r['knot_law'] == 'nae')}},
           'not_run': not_run, 'runs': res, 'n': len(res),
           'parity': {'runs': len(par), 'knots': sum(r['knots'] for r in par), 'fail': sum(r['n_fail'] for r in par),
                      'disagree': sum(r['n_disagree'] for r in par)},
           'nae': {'runs': len(nae), 'knots': sum(r['knots'] for r in nae), 'fail': sum(r['n_fail'] for r in nae),
                   'untested': sum(r['n_untested'] for r in nae), 'direct_checked': sum(r['direct_checked'] for r in nae),
                   'disagree': sum(r['n_disagree'] for r in nae)},
           'max_seconds': max([r['seconds'] for r in res] + [0]), 'seconds': round(time.time() - t0, 1)}
    out['P10'] = (out['parity']['fail'] == 0 and out['parity']['disagree'] == 0 and out['nae']['fail'] == 0
                  and out['nae']['disagree'] == 0 and out['nae']['untested'] == 0)
    write('part7.json', out)
    log('part 7 written', out['P10'], out['parity'], out['nae'], out['seconds'])


if __name__ == '__main__':
    main()
