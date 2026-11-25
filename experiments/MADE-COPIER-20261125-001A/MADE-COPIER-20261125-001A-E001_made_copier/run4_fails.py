"""P10 on run 4 (deviations 50): the drawn histories of run 4 under COPY-LAW(CANCEL-OFFSHOOT), parity, drawn again with
the same generator and calls, so that they are the same histories; every history with two of a place of Y made by X has
its knots tested at every round as run 4 tests them, and every failing knot is listed with its kind, inputs and fresh
count.

usage: python -B run4_fails.py [--procs 4]
"""
import argparse
import os
import random
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
import mc  # noqa: E402
import run4  # noqa: E402

pm, K, P = mc.pm, mc.K, mc.P


def do(name):
    C.cap_memory(6)
    t0 = time.time()
    d = mc.design(name)
    law = run4.law_every('COPY-LAW(OFFSHOOT)', 'parity')
    label = run4.law_label(law)
    S0 = d.start()
    s = d.s
    end = s + 4
    pre = mc.grow(S0, law, rounds=s) if s > 0 else None
    S_s = pre.snap[s] if pre else S0
    pre_snaps = pre.snap[:] if pre else [S0]
    pre_recs = pre.records[:] if pre else []
    R_s = pm.roster_of(S_s.copy(), law)
    ref = mc.Reference(S_s, R_s, d.Y, s, X=d.X)
    tr = run4.Tracker(S_s, d.X, d.Y, s, 'parity', ref)
    rnd = random.Random('2026112502|%s|%s' % (name, label))
    out = Counter()
    rows = []
    for h in range(run4.N_DRAWN):
        S = S_s
        snaps, recs, tied = list(pre_snaps), list(pre_recs), {}
        for t in range(s, end):
            if (recs and recs[-1]['stopped']) or S.n_knots > mc.KNOT_BOUND:
                break
            try:
                T, rec, pk = run4.random_child(S, law, rnd)
            except pm.GuardStop:
                break
            tied.update(tr.new_ties(S, rec))
            snaps.append(T)
            recs.append(rec)
            S = T
        cases = []
        for i in range(s + 1, len(snaps)):
            cases += run4.read_round(tr, snaps[i], tied, i)
        if any(c['owner'] == 'Y' and c['made_by_X'] for c in cases):
            out['histories with two of a place of Y made by X'] += 1
            kt = K.test_run(snaps, law)
            if kt['fails'] or kt['disagree']:
                out['of them with a failing knot'] += 1
                for f in kt['fails']:
                    u, t = f['knot'], f['round']
                    Sx = snaps[f['made']]
                    rec = recs[f['made'] - 1]
                    b = next((b for b in rec['births'] if b['id'] == u), None)
                    out['failing verdicts, %s' % f['kind']] += 1
                    rows.append({'history': h + 1, 'knot': u, 'round tested': t, 'kind': f['kind'],
                                 'parents': f['parents'], 'inputs': len(b['inputs']) if b else None,
                                 'fresh': b['f'] if b else None, 'taken by the rule': len(b['rule_takes']) if b else None})
                out['disagreements'] += len(kt['disagree'])
    return {'design': name, 'counts': dict(out), 'failing knots (first 40)': rows[:40],
            'kinds of failing knots by (kind, inputs, fresh)': dict(Counter('%s, %s inputs, %s fresh' % (
                r['kind'], r['inputs'], r['fresh']) for r in rows)), 'seconds': round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--procs', type=int, default=4)
    args = ap.parse_args()
    res = []
    with ProcessPoolExecutor(max_workers=args.procs) as ex:
        for f in as_completed([ex.submit(do, n) for n in run4.DESIGNS4]):
            r = f.result()
            res.append(r)
            C.log(r['design'], r['counts'], r['seconds'])
    C.write_json('run4_fails.json', {'rows': sorted(res, key=lambda r: run4.DESIGNS4.index(r['design']))})


if __name__ == '__main__':
    main()
