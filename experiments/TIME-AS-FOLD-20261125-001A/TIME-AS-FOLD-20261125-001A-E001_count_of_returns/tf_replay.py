"""Birth-by-birth listings of runs whose counts differ from compare.json (the pre-registration's rule: "on any
disagreement, replayed birth by birth (parents, inputs with their holders, fresh count)").

Usage: python -B tf_replay.py census   (the runs counted in the census cells that differ, where a cell has at most 30)
"""
from __future__ import annotations

import gzip
import json
import sys

import tf_common as C
import tf_engine as E
import tf_runs as RN
import tf_series as Se


def listing(it):
    law = RN.law_of(it)
    rounds, kb = RN.bounds_of(it)
    S = E.from_stars(RN.stars_of(it['start']))
    out = {'item': it, 'start_places': [list(p) for p in S.places], 'rounds': []}
    for t in range(1, rounds + 1):
        T = S.copy()
        try:
            rec, R = E.round_step(T, law)
        except E.GuardStop as g:
            out['stop'] = 'guard at round %d: %s' % (t, g)
            break
        births = []
        for b in rec['births']:
            births.append({'id': b['id'], 'kind': b['kind'], 'parents': b['parents'],
                           'inputs': [[d, list(S.holders[d])] for d in b['inputs']], 'taken_by_rule': b['rule_takes'],
                           'D': b['D'], 'p': b['p'], 'f': b['f'], 'usable': b['usable'], 'barred': b['barred']})
        out['rounds'].append({'round': t, 'members_before': list(R.members), 'parts_before': [list(P) for P in R.parts],
                              'short': rec['short'], 'waiting': rec['waiting'], 'retired': rec['retired'],
                              'births': births})
        S = T
        if S.n_knots > kb:
            out['stop'] = 'knots after round %d' % t
            break
    A = E.Run(E.from_stars(RN.stars_of(it['start'])), law, rounds=rounds, knot_bound=kb)
    for past in (True, False):
        ser, _ = Se.build_series(A, past)
        Se.describe(ser)
        out['series_' + ('past' if past else 'nopast')] = Se.compact([s for s in ser if s['ticks_off'] >= 2], 50)
    return out


def census():
    d = C.load_json(C.out_path('census.json'))
    rows = list(C.jsonl('run1.jsonl.gz'))
    targets = []
    for key, v in d['comparison_with_compare_json'].items():
        diffs = [k for k in v['differences'] if 'series giving parts off' in k or 'clock' in k]
        if not diffs:
            continue
        g, rule, rat = key.split('|')
        cell = [r for r in rows if r['group'] == g and (r['rule'] or 'none') == rule
                and (('FLOOR1' if r['base'].startswith('COPY-LAW') else 'CAP-3') == rat)]
        for col in diffs:
            mode = 'past' if col.startswith('past') else 'nopast'
            hit = [r for r in cell if r[mode]['series_off2']] if 'series' in col else \
                [r for r in cell if r[mode]['clock_off4']]
            targets.append({'cell': key, 'column': col, 'mine_and_prototype': v['differences'][col],
                            'runs': [{k: r[k] for k in ('group', 'start', 'base', 'rule', 'choice', 'knot_law')}
                                     for r in hit]})
    C.write_json('replay_census_cells.json', targets)
    listed = []
    seen = set()
    with gzip.open(C.out_path('replay_census_listings.jsonl.gz'), 'wt') as f:
        for tg in targets:
            if len(tg['runs']) > 30:
                continue
            for it in tg['runs']:
                key = json.dumps(it, sort_keys=True)
                if key in seen:
                    continue
                seen.add(key)
                f.write(json.dumps(listing(it), default=C._default) + '\n')
                listed.append(it)
    C.log('replay: %d cells, %d runs listed' % (len(targets), len(listed)))


if __name__ == '__main__':
    C.cap_memory()
    {'census': census}[sys.argv[1]]()
