"""The census runs R1a to R1d and R2 (PC, "Runs"): every start of a registered prefix of DC 1.5's order, under each law
of the run in DC 1.3's order, sample index 0; one record per sampled growth (start, law, knot law, weighting of takes,
sample index, seed, rounds read, stop, knots, the pairs with their forms and s, the pairs "wholly apart" removed, the
rounds with more than eight pairs, every case with its first-stage rates, the knot test, the counts by form).

  python -B runs.py R1b --procs 6 [--prefix N] [--append] [--scratch DIR]
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

RUNS = {
    # name: (knot law, taking rules, weighting, registered prefix)
    'R1a': ('parity', ('MET',), 'T1', 3344),
    'R1b': ('parity', ('STEPS-1',), 'T1', 2000),
    'R1c': ('nae', ('MET',), 'T1', 1000),
    'R1d': ('nae', ('STEPS-1',), 'T1', 120),
    'R2': ('parity', ('MET', 'STEPS-1'), 'T2', 500),
}


def laws_of(run):
    kl, takes, w, _ = RUNS[run]
    if len(takes) == 2:
        return mcc.family_both(kl, weighting=w)
    return mcc.family(takes[0], kl, weighting=w)


def job(args):
    run, idx, law = args
    st = mcc.census()[idx]
    spec = mcc.Spec.from_name(law)
    t0 = time.time()
    try:
        row, g = study.analyse_growth(st['stars'], spec, st['id'], 0, return_growth=True)
    except MemoryError:
        return {'run': run, 'start': st['id'], 'law': law, 'index': idx, 'error': 'memory',
                'sec': round(time.time() - t0, 2)}
    row['run'] = run
    row['index'] = idx
    if spec.knot_law == 'nae':
        # PC7 (dev 14): the tie classes at the last round read; none means no values reading at any round
        t1 = time.time()
        T = mc.ties_nae(g.G.S, seed=idx)
        nd0 = g.G.snaps[0].n_distinctions
        row['nae_last_round_ties'] = {'classes': len(T.classes), 'frozen': len(T.frozen), 'unsat': T.unsat,
                                      'classes_with_a_made_distinction': sum(1 for c in T.classes
                                                                             if any(d >= nd0 for d in c)),
                                      'sec': round(time.time() - t1, 3)}
    row['sec_total'] = round(time.time() - t0, 3)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run', choices=sorted(RUNS))
    ap.add_argument('--procs', type=int, default=6)
    ap.add_argument('--prefix', type=int, default=None, help='starts of the order read (default: the registered size)')
    ap.add_argument('--append', action='store_true')
    ap.add_argument('--scratch', default=None, help='write to this directory instead of the outputs (timing)')
    ap.add_argument('--every', type=int, default=500)
    a = ap.parse_args()
    kl, takes, w, size = RUNS[a.run]
    n = a.prefix if a.prefix is not None else size
    starts = mcc.run_order(kl)[:n]
    laws = [s.name() for s in laws_of(a.run)]
    jobs = [(a.run, idx, law) for idx in starts for law in laws]
    name = '%s.jsonl.gz' % a.run
    if a.scratch:
        os.makedirs(a.scratch, exist_ok=True)
        mcc.OUT = a.scratch
    done = set()
    if a.append:
        for r in study.read_jsonl(name):
            if 'error' not in r:
                done.add((r['index'], r['law']))
    todo = [j for j in jobs if (j[1], j[2]) not in done]
    log(a.run, 'starts', len(starts), 'laws', len(laws), 'growths', len(jobs), 'to do', len(todo),
        'engine', mcc.engine_hashes() == mcc.ENGINE_SHA)
    w_ = study.JsonLines(name, 'a' if a.append else 'w')
    ctx = mp.get_context('fork')
    t0 = time.time()
    k = 0
    slow = 0
    with ctx.Pool(a.procs, initializer=study.cap_memory) as pool:
        for row in pool.imap_unordered(job, todo, chunksize=1):
            w_.write(row)
            k += 1
            if row.get('sec_total', 0) > 30:
                slow += 1
                log('slow growth', row['start'], row['law'], row.get('sec_total'), row.get('stop'), row.get('guard'))
            if k % a.every == 0 or k == len(todo):
                w_.flush()
                el = time.time() - t0
                log('%s %d/%d growths, %.0f s, %.3f s a growth (wall), ETA %.0f s, slow %d' %
                    (a.run, k, len(todo), el, el / k, el / k * (len(todo) - k), slow))
    w_.close()
    log(a.run, 'done', k, 'growths in', round(time.time() - t0, 1), 's')


if __name__ == '__main__':
    main()
