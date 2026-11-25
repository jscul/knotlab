"""R9, the knot test at every round (D 8's swap of DC 8; PC "Runs", order 6) on R1a's and R1b's growths of the starts of
three and four knots (those in R1b's prefix; dev 29), grown again from their seeds: every knot at every round read by
the fold engine's parity test on the whole structure (dev 43 for structures past 50,000 distinctions), against the
last-round test of the runs (dev 39).  Writes R9.jsonl.gz and R9.json."""
import argparse
import multiprocessing as mp
import os
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mcc  # noqa: E402
import study  # noqa: E402
from mcc import K  # noqa: E402
from study import log  # noqa: E402

WHOLE_LIMIT = 50000


def job(args):
    run, idx, law = args
    st = mcc.census()[idx]
    spec = mcc.Spec.from_name(law)
    t0 = time.time()
    try:
        g = mcc.Growth(st['stars'], spec, st['id'], 0)
    except MemoryError:
        return {'run': run, 'index': idx, 'law': law, 'error': 'memory'}
    G = g.G
    first = {}
    verdicts = dis = 0
    reduced_rounds = []
    for t in range(G.R + 1):
        S = G.snaps[t]
        if S.n_distinctions <= WHOLE_LIMIT:
            pt = K.parity_test(S)
        else:
            pt = mcc.parity_verdicts(S)
            reduced_rounds.append(t)
        verdicts += pt['n']
        dis += len(pt['disagree'])
        for u in pt['fail']:
            first.setdefault(u, t)
    last = mcc.knot_test(G)
    last_fails = {f['knot'] for f in last['fails']}
    every_fails = set(first)
    rows = []
    for u in sorted(every_fails):
        b = mcc.parent_birth(G.records, u, G.S.made[u])
        rows.append({'knot': u, 'made': G.S.made[u], 'first_failing_round': first[u], 'kind': G.S.kind[u],
                     'parents': len(G.S.parents[u]), 'took': bool(b and b['rule_takes']),
                     'implied': bool(b and b['implied'])})
    return {'run': run, 'index': idx, 'start': st['id'], 'law': law, 'rounds': G.R, 'verdicts': verdicts,
            'disagree': dis, 'every_round_fails': rows, 'last_round_fails': sorted(last_fails),
            'missed_by_last_round': sorted(every_fails - last_fails),
            'only_at_last_round': sorted(last_fails - every_fails),
            'failing_after_its_round': [r['knot'] for r in rows if r['first_failing_round'] != r['made']],
            'reduced_rounds': reduced_rounds, 'sec': round(time.time() - t0, 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--procs', type=int, default=6)
    ap.add_argument('--r1a', type=int, default=3344, help="R1a's size run (starts of the parity list)")
    ap.add_argument('--r1b', type=int, default=2000, help="R1b's registered prefix (dev 44)")
    a = ap.parse_args()
    C = mcc.census()
    order = mcc.run_order('parity')
    jobs = []
    for run, take, n in (('R1a', 'MET', a.r1a), ('R1b', 'STEPS-1', a.r1b)):
        for idx in order[:n]:
            if C[idx]['n'] in (3, 4):
                for sp in mcc.family(take, 'parity'):
                    jobs.append((run, idx, sp.name()))
    log('R9', len(jobs), 'growths')
    w = study.JsonLines('R9.jsonl.gz')
    t0 = time.time()
    tot = Counter()
    kinds = Counter()
    missed = []
    ctx = mp.get_context('fork')
    with ctx.Pool(a.procs, initializer=study.cap_memory) as pool:
        for k, r in enumerate(pool.imap_unordered(job, jobs, chunksize=2), 1):
            w.write(r)
            if 'error' in r:
                tot['errors'] += 1
                continue
            tot['growths'] += 1
            tot['verdicts'] += r['verdicts']
            tot['disagree'] += r['disagree']
            tot['growths_with_a_failing_knot'] += int(bool(r['every_round_fails']))
            tot['failing_knots'] += len(r['every_round_fails'])
            tot['missed_by_last_round'] += len(r['missed_by_last_round'])
            tot['only_at_last_round'] += len(r['only_at_last_round'])
            tot['failing_after_its_round'] += len(r['failing_after_its_round'])
            tot['growths_with_reduced_rounds'] += int(bool(r['reduced_rounds']))
            for f in r['every_round_fails']:
                kinds[(r['run'], f['kind'], min(f['parents'], 3), f['took'], f['implied'])] += 1
            if r['missed_by_last_round']:
                missed.append(r)
            if k % 1000 == 0:
                w.flush()
                log('R9 %d/%d %.0f s' % (k, len(jobs), time.time() - t0))
    w.close()
    out = {'totals': dict(tot), 'classes': [{'run': k[0], 'kind': k[1], 'parents (3 = three or more)': k[2],
                                             'took': k[3], 'implied': k[4], 'n': v} for k, v in sorted(kinds.items())],
           'missed': missed[:20], 'sec': round(time.time() - t0, 1)}
    study.write_json('R9.json', out)
    log('R9 done', dict(tot))


if __name__ == '__main__':
    main()
