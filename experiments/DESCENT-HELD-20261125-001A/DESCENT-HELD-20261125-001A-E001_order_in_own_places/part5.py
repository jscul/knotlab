"""Part 5: M2 on the census (DH 5.3; P2).  The ten recorded laws, parity, the 3,348 kept starts, grown round by round
and stopped at the first failing round (deviations 23: "some parent").  Denominators from part 1.  Writes part5.json.

python -B part5.py
"""
from __future__ import annotations

import gzip
import json
import os
import time
from collections import Counter

from dh_common import write, log, n_procs, load_avg, OUT
import dh_engine as E
from dh_census import census, kept_parity


def m2_run(stars, L):
    S = E.Struct(stars)
    recs = []
    end = None
    while True:
        if S.round >= 8:
            end = 'holds through R'
            break
        rec = E.do_round(S, L, None, 'parity')
        recs.append(rec)
        fail = []
        for x in rec['new']:
            nx_ = len(S.places[x])
            if any((nx_ - len(S.places[y])) % 3 != 1 for y in S.parents[x]):
                fail.append('join' if len(S.parents[x]) > 1 else 'offshoot')
        if fail:
            return {'verdict': 'fails at round %d' % rec['round'], 'round': rec['round'],
                    'failing_births': dict(Counter(fail)), 'max_ps': max(S.ps)}
        if rec['stalled'] or (rec['births'] == 0 and rec['newly_barred'] == 0):
            end = 'holds on a finished structure'
            break
        if len(S.places) > 3000:
            end = 'holds, cut at N knots'
            break
    return {'verdict': end, 'round': None, 'max_ps': max(S.ps)}


def job(idx):
    n, gi, loose, stars = census()[idx]
    if not kept_parity(stars):
        return None
    return {'idx': idx, 'laws': {L.name: m2_run(stars, L) for L in E.RECORDED}}


def main():
    import multiprocessing as mp
    procs = n_procs()
    log('part 5, load %.1f, %d processes' % (load_avg(), procs))
    t0 = time.time()
    C = census()
    with mp.Pool(procs) as pool:
        res = [r for r in pool.map(job, range(len(C)), chunksize=20) if r is not None]
    # denominators from part 1: starts reaching three parent steps in the full runs (parity, kept)
    with gzip.open(os.path.join(OUT, 'part1_runs.json.gz'), 'rt') as f:
        p1 = json.load(f)
    reach = {L.name: set() for L in E.RECORDED}
    for row in p1['census_rows']:
        if not row['kept']:
            continue
        for L in E.RECORDED:
            if row['base'][L.name + '|parity']['max_ps'] >= 3:
                reach[L.name].add(row['idx'])
    by_law = {}
    for L in E.RECORDED:
        fails = {r['idx'] for r in res if r['laws'][L.name]['round'] is not None}
        holds = {r['idx']: r['laws'][L.name] for r in res if r['laws'][L.name]['round'] is None}
        exceptions = sorted(i for i in reach[L.name] if i not in fails)
        holds_reaching_3_here = sorted(i for i, v in holds.items() if v['max_ps'] >= 3)
        by_law[L.name] = {'kept': len(res), 'reach_three_parent_steps (part 1)': len(reach[L.name]),
                          'fail_somewhere': len(fails),
                          'fail_by_round': dict(Counter(r['laws'][L.name]['round'] for r in res
                                                        if r['laws'][L.name]['round'] is not None)),
                          'holds_kinds': dict(Counter(v['verdict'] for v in holds.values())),
                          'reach_three_and_fail': len(reach[L.name] & fails),
                          'exceptions (reach three, no failing birth)': exceptions,
                          'holds_and_reach_three_in_part5': holds_reaching_3_here,
                          'P2': not exceptions and not holds_reaching_3_here}
    out = {'part': 5, 'load_at_start': load_avg(), 'processes': procs, 'by_law': by_law,
           'P2': all(v['P2'] for v in by_law.values()), 'rows': res, 'seconds': round(time.time() - t0, 1)}
    write('part5.json', out)
    log('part 5 written', out['P2'], out['seconds'])


if __name__ == '__main__':
    main()
