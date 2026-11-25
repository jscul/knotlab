"""Part 1: the census strata (P11, P3-P6 on the census, P14, P15).  Writes part1.json and part1_runs.json.

python -B part1.py [--time-sample K] [--limit SECONDS]
Readings: deviations 6-17.
"""
from __future__ import annotations

import gzip
import json
import os
import sys
import time
from collections import Counter, defaultdict

from dh_common import write, log, n_procs, load_avg, OUT
import dh_engine as E
import dh_analysis as A
from dh_census import census, kept_parity, labelled_weight, six_sample_order

LIMIT = 30 * 60
BASE_KEYS = ('counted', 'counted_first_round', 'bprime_fails', 'bprime_first_round', 'greatest', 'greatest_by_round',
             'max_ps', 'lq_fails_rounds', 'first_no_birth_round', 'fives_right_on', 'fives_first_wrong_round',
             'three_stamp_right_on', 'm2_fail_round_some', 'm2_fail_round_every', 'knots', 'rounds', 'end',
             'closing_births')
W_KEYS = ('a', 'bprime', 'b', 'c', 'd', 'greatest', 'place_rule_last_by_kind', 'right_on_every_structure',
          'first_round_with_a_wrong_place', 'counted_step3', 'bprime_births', 'counted_step3_equals_bprime_births',
          'closing_births', 'closing_hyp_s', 'P3', 'P4', 'P5', 'P6', 'knots', 'rounds', 'end', 's_positive',
          'new_knots', 's_sum', 'bprime_first_round', 'retired_knots')


def census_start(idx):
    n, gi, loose, stars = census()[idx]
    kept = kept_parity(stars)
    out = {'idx': idx, 'n': n, 'kept': kept, 'w': labelled_weight(n, gi, loose),
           'a_places': E.condition_a(E.Struct(stars), 'PU'), 'base': {}, 'armw': {}}
    for L in E.LAWS:
        for kl in ('parity', 'nae'):
            if kl == 'parity' and not kept:
                continue
            S, recs, end = E.grow(stars, L, None, kl, R=8, N=3000)
            row = A.analyze_base(S, recs, end)
            r = {k: row[k] for k in BASE_KEYS}
            r['alt_stop'] = A.alt_stop(row)
            out['base'][L.name + '|' + kl] = r
    if kept:
        for L in E.RELEASE_BASES:
            for form in E.FORMS:
                S, recs, end = E.grow(stars, L, form, 'parity', R=8, N=3000)
                row = A.analyze_armw(S, recs, end, form, 'parity', L, keep_wrong=5)
                r = {k: row[k] for k in W_KEYS}
                if row['P3'] is False or row['P4'] is False or row['P5'] is False or row['P6'] is False:
                    r['wrong_examples'] = row['wrong_examples']
                    r['P6_rows'] = row['P6_rows']
                out['armw'][L.name + '|' + form] = r
    return out


def six_kept_chunk(args):
    lo, hi = args
    c6 = census(6, 6)
    out = []
    for i in range(lo, hi):
        n, gi, loose, stars = c6[i]
        out.append((kept_parity(stars), E.condition_a(E.Struct(stars), 'PU')))
    return out


def six_start(i):
    n, gi, loose, stars = census(6, 6)[i]
    out = {'idx6': i, 'w': labelled_weight(n, gi, loose), 'base': {}}
    for L in E.LAWS:
        S, recs, end = E.grow(stars, L, None, 'parity', R=8, N=3000)
        row = A.analyze_base(S, recs, end, with_place=False)
        out['base'][L.name] = {k: row[k] for k in ('counted', 'bprime_fails', 'greatest', 'lq_fails_rounds', 'knots',
                                                   'rounds', 'end', 'counted_first_round', 'first_no_birth_round',
                                                   'bprime_first_round')}
    return out


def run_ordered(pool, fn, items, limit, label, chunksize=4):
    t0 = time.time()
    res = []
    cut = False
    it = pool.imap(fn, items, chunksize=chunksize)
    for k in range(len(items)):
        res.append(next(it))
        if (k + 1) % 250 == 0:
            log('%s %d / %d, load %.1f' % (label, k + 1, len(items), load_avg()))
        if time.time() - t0 > limit:
            cut = True
            break
    return res, cut, round(time.time() - t0, 1)


def main():
    import multiprocessing as mp
    tsample = None
    if '--time-sample' in sys.argv:
        tsample = int(sys.argv[sys.argv.index('--time-sample') + 1])
    limit = LIMIT
    if '--limit' in sys.argv:
        limit = float(sys.argv[sys.argv.index('--limit') + 1])
    procs = n_procs()
    log('part 1, load %.1f, %d processes' % (load_avg(), procs))
    C = census()
    if tsample:
        step = max(1, len(C) // tsample)
        items = list(range(0, len(C), step))[:tsample]
        t = time.time()
        for i in items:
            census_start(i)
        dt = time.time() - t
        log('time sample: %d census starts in %.1f s single process: %.3f s per start; whole census %.0f s single, '
            '%.0f s on %d' % (len(items), dt, dt / len(items), dt / len(items) * len(C),
                              dt / len(items) * len(C) / procs, procs))
        c6 = census(6, 6)
        order = six_sample_order()
        t = time.time()
        for i in order[:20]:
            six_start(i)
        dt6 = time.time() - t
        log('six-knot: 20 starts in %.1f s: whole sample %.0f s single' % (dt6, dt6 / 20 * 3000))
        return
    out = {'part': 1, 'load_at_start': load_avg(), 'processes': procs}
    t_all = time.time()
    t = time.time()
    c6 = census(6, 6)                  # built before the workers start, so that each inherits it
    log('six-knot census built', len(c6), round(time.time() - t, 1))
    with mp.Pool(procs) as pool:
        # (1) condition (a) on all starts, no growth; kept flags at six knots
        chunks = [(lo, min(lo + 2000, len(c6))) for lo in range(0, len(c6), 2000)]
        six = [x for ch in pool.map(six_kept_chunk, chunks) for x in ch]
        out['six_census'] = {'starts': len(c6), 'kept': sum(k for k, a in six), 'a_on_kept': sum(1 for k, a in six if k and a),
                             'a_on_all': sum(1 for k, a in six if a), 'seconds': round(time.time() - t, 1)}
        log('six-knot census', out['six_census'])
        # (2) the census of up to five knots
        rows, cut, sec = run_ordered(pool, census_start, list(range(len(C))), limit - (time.time() - t_all), 'census')
        out['census_run'] = {'starts_done': len(rows), 'cut': cut, 'seconds': sec}
        log('census done', len(rows), cut, sec)
        # (3) the six-knot sample
        order = six_sample_order()
        sample = [i for i in order if six[i][0]][:3000]
        rows6, cut6, sec6 = run_ordered(pool, six_start, sample, limit - (time.time() - t_all), 'six')
        out['six_sample_run'] = {'starts_done': len(rows6), 'cut': cut6, 'seconds': sec6, 'first_indices': sample[:20]}
        log('six done', len(rows6), cut6, sec6)
    out['seconds'] = round(time.time() - t_all, 1)
    with gzip.open(os.path.join(OUT, 'part1_runs.json.gz'), 'wt') as f:
        json.dump({'census_rows': rows, 'six_rows': rows6, 'six_kept_a': six}, f)
    write('part1_meta.json', out)
    log('part 1 written', out['seconds'])


if __name__ == '__main__':
    main()
