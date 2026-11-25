"""R3, the confirmations (DC 4.4; PC "Runs", order 11): every case of a claimed reading (form, from both, values both
from X) that passes at 100 in the main runs read (R1a to R1d and R2), all counted before any confirmation (m), read on
1,000 further continuations of each of the five kinds (i = 100 to 1,099) and confirmed when q1 is above q0, qY and qT,
each at 0.01/m; its way by qM.  The reported readings (one from both, both from both, ticket A's values reading) form a
family of their own (m', each at 0.01/m').  Writes R3.json."""
import argparse
import multiprocessing as mp
import os
import sys
import time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mcc  # noqa: E402
import study  # noqa: E402
from study import log  # noqa: E402

MAIN = ('R1a', 'R1b', 'R1c', 'R1d', 'R2')
CHUNK = 100


def passing_cases(runs=MAIN):
    out = []
    read = {}
    for run in runs:
        rows = study.read_jsonl('%s.jsonl.gz' % run)
        read[run] = len(rows)
        for r in rows:
            for c in r.get('cases', []):
                if c.get('first_stage', {}).get('passes_at_100'):
                    out.append({'run': run, 'start': r['start'], 'index': r['index'], 'law': r['law'], 'i': r['i'],
                                'seed': r['seed'], 's': c['s'], 'X': c['X'], 'Y': c['Y'], 'reading': c['reading'],
                                'rates100': c['rates100'], 'first_stage': c['first_stage'],
                                'made_questions': c.get('made_questions'), 'growth_has_failing_knot':
                                    bool(r.get('knot_test', {}).get('n_fails'))})
    return out, read


def job(args):
    key, readings, kind, lo, hi = args
    run, idx, law, i, s, X, Y = key
    st = mcc.census()[idx]
    spec = mcc.Spec.from_name(law)
    g = mcc.Growth(st['stars'], spec, st['id'], i)
    cnt = study.stage(g, s, {(tuple(X), tuple(Y)): readings}, (kind,), range(lo, hi))
    c = cnt[(tuple(X), tuple(Y))][kind]
    return key, kind, {k: (dict(v) if isinstance(v, Counter) else v) for k, v in c.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--procs', type=int, default=6)
    ap.add_argument('--runs', default=','.join(MAIN))
    ap.add_argument('--out', default='R3.json', help="R3.json (main family) or Rcond.json (the conditional family)")
    a = ap.parse_args()
    runs = a.runs.split(',')
    cases, read = passing_cases(runs)
    claimed = [c for c in cases if c['reading'] in mcc.CLAIMED]
    reported = [c for c in cases if c['reading'] in mcc.REPORTED]
    m, m2 = len(claimed), len(reported)
    log('R3: runs read', read, 'claimed cases passing at 100: m =', m, "reported: m' =", m2)
    out = {'runs read': read, 'm': m, "m'": m2, 'level_claimed': (0.01 / m) if m else None,
           'level_reported': (0.01 / m2) if m2 else None, 'cases': []}
    groups = defaultdict(list)
    for c in cases:
        key = (c['run'], c['index'], c['law'], c['i'], c['s'], tuple(c['X']), tuple(c['Y']))
        groups[key].append(c['reading'])
    jobs = [(key, sorted(set(rs)), kind, lo, lo + CHUNK) for key, rs in groups.items() for kind in mcc.KINDS
            for lo in range(100, 1100, CHUNK)]
    acc = defaultdict(list)
    if jobs:
        ctx = mp.get_context('fork')
        t0 = time.time()
        with ctx.Pool(a.procs, initializer=study.cap_memory) as pool:
            for k, (key, kind, c) in enumerate(pool.imap_unordered(job, jobs, chunksize=1), 1):
                acc[(key, kind)].append(c)
                if k % 50 == 0:
                    log('R3 %d/%d jobs, %.0f s' % (k, len(jobs), time.time() - t0))
    from controls import merge
    for c in cases:
        key = (c['run'], c['index'], c['law'], c['i'], c['s'], tuple(c['X']), tuple(c['Y']))
        cnt = {kind: merge(acc[(key, kind)]) for kind in mcc.KINDS}
        rt = study.rates_of(cnt, c['reading'])
        level = (0.01 / m) if c['reading'] in mcc.CLAIMED else (0.01 / m2)
        cv = study.confirm_verdict(rt, level)
        row = dict(c, rates1000=rt, confirmation=cv,
                   family='claimed' if c['reading'] in mcc.CLAIMED else 'reported')
        out['cases'].append(row)
        log(c['run'], c['start'], c['law'], c['reading'], 's', c['s'], (rt['q1'], rt['q0'], rt['qY'], rt['qM'],
                                                                          rt['qT']), cv['confirmed'], cv.get('way'))
    out['confirmed_claimed'] = [c for c in out['cases'] if c['family'] == 'claimed' and c['confirmation']['confirmed']]
    out['confirmed_reported'] = [c for c in out['cases'] if c['family'] == 'reported' and c['confirmation']['confirmed']]
    out['family of'] = runs
    study.write_json(a.out, out)
    log('R3 done: confirmed claimed', len(out['confirmed_claimed']), 'reported', len(out['confirmed_reported']))


if __name__ == '__main__':
    main()
