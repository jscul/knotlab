"""Run 7: the knot test (TD 7) of every run A of runs 1 to 3 (and of runs 5, 6 where given), and of comparison runs.

Every run A is regrown (deterministic) and tested: parity by ranks and kernel, not-all-equal by the birth method and the
direct test (dev 17, 18); runs A of at most 300 knots also by the literal test at every round.  Each run's knot test has
its own limit of 600 seconds of process time.
Usage: python -B tf_run7.py runA [--inputs run1.jsonl.gz,...] [--procs 6] [--time-sample N] [--order-file F]
       python -B tf_run7.py comparisons [--procs 6] [--time-sample N]
"""
from __future__ import annotations

import argparse
import gzip
import json
import multiprocessing as mp
import random
import time

import tf_common as C
import tf_engine as E
import tf_knots as K
import tf_run4 as R4
import tf_runs as RN
import tf_series as Se
import tf_tests as Tt

LITERAL_MAX = 300


def brief(kt):
    return {'verdicts': kt['verdicts'], 'fails': len(kt['fails']), 'fail_rows': kt['fails'][:20],
            'disagree': len(kt['disagree']), 'disagree_rows': kt['disagree'][:10], 'untested': len(kt['untested']),
            'untested_rows': kt['untested'][:10], 'compared': kt['compared'], 'extension_bad': kt['extension_bad'],
            'cuts': kt.get('cuts', [])}


def runA_job(it):
    t0 = time.process_time()
    out = dict(it)
    try:
        A, law = RN.grow(it, clock=E.Clock(600))
        if A.stop == 'limit':
            out['unfinished'] = 'growth'
            return out
        out['rounds'] = A.rounds_done
        out['knots'] = A.S.n_knots
        clock = E.Clock(600)
        kt = K.test_run(A.S, A.records, law, direct_rounds='last', clock=clock)
        out['kt'] = brief(kt)
        if A.S.n_knots <= LITERAL_MAX:
            lit = K.literal_every_round(A.S, law, clock=clock)
            # compare: a knot failing literally at some round must be a knot failing in kt, and the reverse
            fl = {f['knot'] for f in lit['fails']}
            fk = {f['knot'] for f in kt['fails']}
            out['literal'] = {'rounds': lit['rounds'], 'verdicts': lit['verdicts'], 'fails': len(lit['fails']),
                              'disagree_methods': len(lit['disagree']), 'same_failing_knots': fl == fk}
    except E.LimitReached:
        out['unfinished'] = 'knot test: limit'
    except MemoryError:
        out['unfinished'] = 'memory cap'
    out['sec'] = round(time.process_time() - t0, 2)
    return out


def _init():
    C.cap_memory()


def items_from(inputs):
    out = []
    for fn in inputs:
        for r in C.jsonl(fn):
            if r.get('unfinished'):
                continue
            out.append(R4.item_of(r))
    return out


def run(items, procs, out_name):
    path = C.out_path(out_name)
    t0 = time.time()
    sec = 0.0
    with gzip.open(path, 'wt') as f, mp.Pool(procs, initializer=_init, maxtasksperchild=20) as pool:
        for i, r in enumerate(pool.imap_unordered(runA_job, items)):
            f.write(json.dumps(r, sort_keys=True, default=C._default) + '\n')
            sec += r.get('sec', 0)
            if (i + 1) % 200 == 0 or i + 1 == len(items):
                C.log('%s: %d/%d, %.0f s process, %.0f s wall' % (out_name, i + 1, len(items), sec, time.time() - t0))
                f.flush()
    return path


def comparisons_job(arg):
    """Knot tests of the comparison runs of one run A's tests (B(r), B'(r), Ball(r), M(r), X barred): knots made after
    the round each run leaves run A, at every round under parity (by extension, dev 17) and at the last round under
    not-all-equal."""
    it = arg
    t0 = time.process_time()
    out = dict(it)
    try:
        A, law = RN.grow(it, clock=E.Clock(600))
        ser, _ = Se.build_series(A, False)
        Se.describe(ser)
        rounds, kb = RN.bounds_of(it)
        comps = Tt.Comparisons(A, law, rounds, kb)
        for s in R4.chosen_clocks(ser):
            for j in (0, 1):
                Tt.run_tests(A, law, s, j, comps)
        tot = {'runs': 0, 'verdicts': 0, 'fails': 0, 'disagree': 0, 'untested': 0, 'fail_rows': []}
        clock = E.Clock(600)
        for key, (R, sec) in comps.cache.items():
            if R.stop == 'limit':
                continue
            t_left = key[1]
            kt = K.test_run(R.S, R.records[t_left:], law, only_after=t_left, direct_rounds='last', clock=clock)
            tot['runs'] += 1
            tot['verdicts'] += kt['verdicts']
            tot['fails'] += len(kt['fails'])
            tot['disagree'] += len(kt['disagree'])
            tot['untested'] += len(kt['untested'])
            tot['fail_rows'] += [dict(f, run=list(map(str, key))) for f in kt['fails'][:5]]
        out['kt_comparisons'] = tot
    except E.LimitReached:
        out['unfinished'] = 'limit'
    out['sec'] = round(time.process_time() - t0, 2)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('what')
    ap.add_argument('--inputs', default='run1.jsonl.gz,run2.jsonl.gz,run3.jsonl.gz')
    ap.add_argument('--procs', type=int, default=6)
    ap.add_argument('--time-sample', type=int, default=0)
    ap.add_argument('--prefix', type=int, default=0)
    ap.add_argument('--out', default=None)
    ap.add_argument('--prefix-pool', type=int, default=0)
    a = ap.parse_args()
    C.cap_memory()
    if a.what == 'runA':
        items = items_from(a.inputs.split(','))
        if a.time_sample:
            items = random.Random(2026112507).sample(items, a.time_sample)
        elif a.prefix:
            items = items[:a.prefix]
        run(items, a.procs, a.out or ('run7_runA.jsonl.gz' if not a.time_sample else 'run7_timing.jsonl.gz'))
    elif a.what == 'comparisons':
        items = R4.select(a.inputs.split(','))
        if a.prefix_pool:
            items = items[:a.prefix_pool]          # run 4's prefix (deviations 40)
        if a.time_sample:
            items = random.Random(2026112508).sample(items, min(a.time_sample, len(items)))
        elif a.prefix:
            items = items[:a.prefix]
        path = C.out_path(a.out or 'run7_comparisons.jsonl.gz')
        with gzip.open(path, 'wt') as f, mp.Pool(a.procs, initializer=_init, maxtasksperchild=10) as pool:
            for i, r in enumerate(pool.imap_unordered(comparisons_job, items)):
                f.write(json.dumps(r, sort_keys=True, default=C._default) + '\n')
                if (i + 1) % 50 == 0 or i + 1 == len(items):
                    C.log('run 7 comparisons: %d/%d' % (i + 1, len(items)))
                    f.flush()


if __name__ == '__main__':
    main()
