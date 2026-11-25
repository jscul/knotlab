"""The conditional runs (PC, "Runs"), fired by R3's confirmed cases (dev 60) and run on the coordinator's word.

R5, the swaps of the law (DC 1.3): HOLD for RELEASE (the 42) and STEPS-2 for STEPS-1 (the 21), parity, on the starts
of three and four knots and the first 300 five-knot starts of the order; HOLD with MET under not-all-equal on the starts
of three and four knots.  Registered order (dev 61): part A, the starts of three and four knots in DC 1.5's order, each
under the parity laws (HOLD's 42, then STEPS-2's 21, each in DC 1.3's order) and the not-all-equal laws (HOLD with
MET, 21); then part B, the first 300 five-knot starts of the order, in order, each under the 63 parity laws.

R6, every pair and the first stage at 300 (DC 2.2's and DC 4.4's swaps): R1a's and R1b's growths of the starts of three
and four knots (as R9: R1a's 216 under the 21 MET laws, R1b's 131 of its registered prefix under the 21 STEPS-1 laws),
grown again from their seeds, every pair read, each case's first stage at 300 continuations of kinds BN3, BY3, BX3.

  python -B cond.py R5|R6 --procs 6 [--starts N] [--append] [--limit 600]
"""
import argparse
import multiprocessing as mp
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mcc  # noqa: E402
import study  # noqa: E402
from mcc import mc  # noqa: E402
from study import log  # noqa: E402

LIMIT = 600


def r5_starts():
    C = mcc.census()
    o = mcc.order()
    small = [i for i in o if C[i]['n'] in (3, 4)]
    ids = {e['id']: i for i, e in enumerate(C)}
    five = [ids[x] for x in mcc.STARTS_C['registered_samples']['R5 five-knot starts']]
    return small, five


def r5_jobs():
    C = mcc.census()
    small, five = r5_starts()
    hold = [s.name() for s in mcc.family_both('parity', release='HOLD')]
    steps2 = [s.name() for s in mcc.family('STEPS-2', 'parity')]
    nae_hold = [s.name() for s in mcc.family('MET', 'nae', release='HOLD')]
    jobs = []
    for i in small:
        if not C[i]['set_aside_parity']:
            jobs += [('R5', 'A', i, law) for law in hold + steps2]
        jobs += [('R5', 'A', i, law) for law in nae_hold]
    for i in five:
        if not C[i]['set_aside_parity']:
            jobs += [('R5', 'B', i, law) for law in hold + steps2]
    return jobs


def r6_jobs():
    C = mcc.census()
    o = mcc.run_order('parity')
    r1b = set(o[:2000])
    met = [s.name() for s in mcc.family('MET', 'parity')]
    st1 = [s.name() for s in mcc.family('STEPS-1', 'parity')]
    jobs = []
    for i in o:
        if C[i]['n'] not in (3, 4):
            continue
        jobs += [('R6', 'R1a', i, law) for law in met]
        if i in r1b:
            jobs += [('R6', 'R1b', i, law) for law in st1]
    return jobs


def _grow(run, idx, law):
    st = mcc.census()[idx]
    spec = mcc.Spec.from_name(law)
    if run == 'R5':
        return study.analyse_growth(st['stars'], spec, st['id'], 0, return_growth=True)
    return study.analyse_growth(st['stars'], spec, st['id'], 0, return_growth=True, pair_rule='every', k1=300,
                                first_kinds=('BN3', 'BY3', 'BX3'))


def job(args):
    run, part, idx, law, limit = args
    st = mcc.census()[idx]
    t0 = time.time()
    try:
        row, g = study.with_time_limit(limit, _grow, run, idx, law)
    except study.TimeLimit:
        return {'run': run, 'part': part, 'start': st['id'], 'law': law, 'index': idx,
                'error': 'time limit', 'sec': round(time.time() - t0, 2)}
    except MemoryError:
        return {'run': run, 'part': part, 'start': st['id'], 'law': law, 'index': idx, 'error': 'memory',
                'sec': round(time.time() - t0, 2)}
    row.update({'run': run, 'part': part, 'index': idx})
    if mcc.Spec.from_name(law).knot_law == 'nae':
        T = mc.ties_nae(g.G.S, seed=idx)
        nd0 = g.G.snaps[0].n_distinctions
        row['nae_last_round_ties'] = {'classes': len(T.classes), 'frozen': len(T.frozen), 'unsat': T.unsat,
                                      'classes_with_a_made_distinction': sum(1 for c in T.classes
                                                                             if any(d >= nd0 for d in c))}
    row['sec_total'] = round(time.time() - t0, 3)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run', choices=('R5', 'R6'))
    ap.add_argument('--procs', type=int, default=6)
    ap.add_argument('--starts', type=int, default=None, help='a prefix of the run\'s order of starts (dev 62)')
    ap.add_argument('--sample', type=int, default=None, help='timing: this many jobs drawn with a stated seed')
    ap.add_argument('--append', action='store_true')
    ap.add_argument('--limit', type=int, default=LIMIT)
    ap.add_argument('--scratch', default=None)
    ap.add_argument('--every', type=int, default=500)
    a = ap.parse_args()
    jobs = r5_jobs() if a.run == 'R5' else r6_jobs()
    if a.starts is not None:
        keep, seen = [], []
        for j in jobs:
            if j[2] not in seen:
                seen.append(j[2])
            if len(seen) <= a.starts:
                keep.append(j)
        jobs = keep
    if a.sample is not None:
        import random
        jobs = random.Random('timing %s' % a.run).sample(jobs, a.sample)
    if a.scratch:
        os.makedirs(a.scratch, exist_ok=True)
        mcc.OUT = a.scratch
    name = '%s.jsonl.gz' % a.run
    done = set()
    if a.append:
        for r in study.read_jsonl(name):
            if 'error' not in r:
                done.add((r['index'], r['law']))
    todo = [j + (a.limit,) for j in jobs if (j[2], j[3]) not in done]
    log(a.run, 'growths', len(jobs), 'to do', len(todo), 'starts', len({j[2] for j in jobs}), 'limit', a.limit,
        'engine', mcc.engine_hashes() == mcc.ENGINE_SHA)
    w = study.JsonLines(name, 'a' if a.append else 'w')
    t0 = time.time()
    k = 0
    with mp.get_context('fork').Pool(a.procs, initializer=study.cap_memory) as pool:
        for row in pool.imap_unordered(job, todo, chunksize=1):
            w.write(row)
            k += 1
            if 'error' in row or row.get('sec_total', 0) > 60:
                log('long or not read', row['start'], row['law'], row.get('error'), row.get('sec', row.get('sec_total')))
            if k % a.every == 0 or k == len(todo):
                w.flush()
                el = time.time() - t0
                log('%s %d/%d growths, %.0f s, ETA %.0f s' % (a.run, k, len(todo), el, el / k * (len(todo) - k)))
    w.close()
    log(a.run, 'done', k, 'growths in', round(time.time() - t0, 1), 's')


if __name__ == '__main__':
    main()
