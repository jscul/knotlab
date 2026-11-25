"""Part 1's counts from its raw runs (part1_runs.json.gz): P11 with every split, both weightings, the listings, P3-P6
on the census, P14, P15, and P16's census counts under the other stopping reading.  Writes part1.json.

python -B sum_part1.py
"""
from __future__ import annotations

import gzip
import json
import os
from collections import Counter, defaultdict

from dh_common import OUT, write, read_out, log
import dh_engine as E

# the disclosed numbers (pre-registration, P11's table and bullets; history lines)
DISCLOSED = {
    'counted': {'R3W': 510, 'C3W': 510, 'C3WF': 510, 'F1W': 223, 'ORDW': 155, 'OFW': 351, 'R4W': 400, 'H-C3W': 48,
                'H-R3W': 48, 'H-F1R': 369, 'H-F1O': 462, 'F1O': 0, 'F1R': 0, 'ORD': 0},
    'greatest_2_3': {'R3W': (501, 9), 'C3W': (502, 8), 'C3WF': (502, 8), 'F1W': (222, 1), 'ORDW': (155, 0),
                     'OFW': (346, 5), 'R4W': (377, 23), 'H-C3W': (44, 4), 'H-R3W': (48, 0), 'H-F1O': (417, 45)},
    'fives_right_on_among_counted': {'R3W': 501, 'C3W': 502, 'C3WF': 502, 'F1W': 222},
    'lq_fails': {'R3W': 1474, 'C3W': 1474, 'C3WF': 1474, 'F1W': 1474, 'ORDW': 1474, 'OFW': 1474, 'R4W': 1474,
                 'H-C3W': 1266, 'H-R3W': 1266, 'H-F1R': 0, 'H-F1O': 0},
    'labelled_share_percent': {'R3W': 19.3, 'C3W': 19.3, 'C3WF': 19.3, 'F1W': 7.9, 'ORDW': 5.8, 'OFW': 12.9,
                               'R4W': 15.1, 'H-C3W': 1.5, 'H-R3W': 1.5, 'H-F1R': 12.8, 'H-F1O': 16.4, 'F1O': 0,
                               'F1R': 0, 'ORD': 0},
    'condition_a': {'total': 133, 'by_size': {1: 1, 2: 2, 3: 5, 4: 21, 5: 104}},
    'condition_a_size_population': {1: 1, 2: 3, 3: 19, 4: 197, 5: 3128},
    'six_condition_a': 804, 'six_kept': 82372,
    'six_counted': {'R3W': 493, 'C3W': 493, 'C3WF': 493, 'F1W': 184},
    'joint_PU_PB': {'R3W': (129, 127), 'F1O': (133, 133), 'F1R': (133, 133), 'ORD': (133, 133), 'C3W': (129, 127),
                    'C3WF': (129, 127), 'F1W': (127, 130)},
    'joint_BB': {'R3W': 2838, 'F1O': 3348, 'F1R': 90, 'ORD': 3348, 'C3W': 2838, 'C3WF': 2838, 'F1W': 3125},
    'H-F1R_alt_stop': 368,
    'R3W_by_size': {4: 21, 5: 489},
    'fives_1727_of_1753': (1727, 1753),
}
WAITING_RELEASE = ['R3W', 'C3W', 'C3WF', 'F1W', 'ORDW', 'OFW', 'R4W']


def main():
    with gzip.open(os.path.join(OUT, 'part1_runs.json.gz'), 'rt') as f:
        raw = json.load(f)
    meta = read_out('part1_meta.json')
    rows = raw['census_rows']
    out = {'part': 1, 'meta': meta, 'disclosed': {k: (v if not isinstance(v, dict) else {str(a): b for a, b in v.items()})
                                                  for k, v in DISCLOSED.items()}}
    kept = [r for r in rows if r['kept']]
    out['population'] = {'census_done': len(rows), 'kept': len(kept), 'set_aside': len(rows) - len(kept),
                         'set_aside_indices': [r['idx'] for r in rows if not r['kept']]}
    # condition (a)
    bysz = Counter(r['n'] for r in kept)
    a_by = Counter(r['n'] for r in kept if r['a_places'])
    out['condition_a'] = {'kept_with_a': sum(a_by.values()), 'of_kept': len(kept),
                          'by_size': {str(n): [a_by.get(n, 0), bysz[n]] for n in sorted(bysz)},
                          'all_3380_with_a': sum(1 for r in rows if r['a_places']),
                          'six_knots': meta.get('six_census'),
                          'listing': [r['idx'] for r in kept if r['a_places']]}
    Wk = sum(r['w'] for r in kept)
    Wa = sum(r['w'] for r in rows)
    laws = {}
    for L in E.LAWS:
        for kl in ('parity', 'nae'):
            pop = kept if kl == 'parity' else rows
            W = Wk if kl == 'parity' else Wa
            key = L.name + '|' + kl
            br = [(r, r['base'][key]) for r in pop]
            counted = [(r, b) for r, b in br if b['counted']]
            g = Counter(b['greatest'] for r, b in counted)
            lq = [(r, b) for r, b in br if b['lq_fails_rounds']]
            lq_idx = {r['idx'] for r, b in lq}
            bp = [(r, b) for r, b in br if b['bprime_fails']]
            st3_wrong = sum(1 for r, b in br if not b['three_stamp_right_on'])
            alt = [(r, b['alt_stop']) for r, b in br]
            alt_c = [(r, a) for r, a in alt if a['counted']]
            gbr = Counter()
            for r, b in br:
                for rd, v in b['greatest_by_round'].items():
                    gbr[(int(rd), v)] += 1
            gbr_counted = Counter()
            for r, b in counted:
                for rd, v in b['greatest_by_round'].items():
                    gbr_counted[(int(rd), v)] += 1
            d = {
                'population': len(pop),
                'counted': len(counted),
                'counted_labelled_share': sum(r['w'] for r, b in counted) / W,
                'counted_by_size': {str(n): [sum(1 for r, b in counted if r['n'] == n), sum(1 for r in pop if r['n'] == n)]
                                    for n in range(1, 6)},
                'counted_greatest': {str(k): v for k, v in sorted(g.items())},
                'counted_first_round': {str(k): v for k, v in sorted(Counter(b['counted_first_round']
                                                                             for r, b in counted).items())},
                'fives_right_on_among_counted': sum(1 for r, b in counted if b['fives_right_on']),
                'fives_right_on_all': sum(1 for r, b in br if b['fives_right_on']),
                'lq_fails': len(lq), 'lq_fails_labelled_share': sum(r['w'] for r, b in lq) / W,
                'counted_among_lq_failing': sum(1 for r, b in counted if r['idx'] in lq_idx),
                'bprime_fails': len(bp), 'bprime_equals_counted': {r['idx'] for r, b in bp} == {r['idx'] for r, b in counted},
                'three_stamp_wrong': st3_wrong,
                'greatest_over_3': sum(1 for r, b in br if b['greatest'] > 3),
                'greatest_by_round_all_runs': {'%d:%d' % k: v for k, v in sorted(gbr.items())},
                'greatest_by_round_counted_runs': {'%d:%d' % k: v for k, v in sorted(gbr_counted.items())},
                'reach_three_parent_steps': sum(1 for r, b in br if b['max_ps'] >= 3),
                'closing_runs': sum(1 for r, b in br if b['closing_births']),
                'ends': dict(Counter(b['end'] for r, b in br)),
                'listing_counted': [[r['idx'], b['greatest'], b['counted_first_round']] for r, b in counted],
                'alt_stop': {'counted': len(alt_c),
                             'counted_greatest': {str(k): v for k, v in
                                                  sorted(Counter(a['greatest'] for r, a in alt_c).items())},
                             'lq_fails': sum(1 for r, a in alt if a['lq_fails']),
                             'fives_right_on_among_counted': sum(1 for r, a in alt_c if a['fives_right_on']),
                             'differs_from_registered_on': [r['idx'] for (r, a), (r2, b) in zip(alt, br)
                                                            if a['counted'] != b['counted']]},
            }
            laws[key] = d
    out['laws'] = laws
    # parity against not-all-equal on the counts
    out['parity_vs_nae'] = {L.name: {'parity': laws[L.name + '|parity']['counted'], 'nae': laws[L.name + '|nae']['counted'],
                                     'nae_counted_set_aside': sum(1 for x in laws[L.name + '|nae']['listing_counted']
                                                                  if x[0] in set(out['population']['set_aside_indices']))}
                            for L in E.LAWS}
    # comparisons with the disclosed numbers (parity, 3,348)
    cmp_ = {}
    for L in E.LAWS:
        d = laws[L.name + '|parity']
        g2, g3 = d['counted_greatest'].get('2', 0), d['counted_greatest'].get('3', 0)
        row = {'counted': [d['counted'], DISCLOSED['counted'].get(L.name)]}
        if L.name in DISCLOSED['greatest_2_3']:
            row['greatest_2_3'] = [[g2, g3], list(DISCLOSED['greatest_2_3'][L.name])]
        if L.name in DISCLOSED['fives_right_on_among_counted']:
            row['fives_right_on_among_counted'] = [d['fives_right_on_among_counted'],
                                                   DISCLOSED['fives_right_on_among_counted'][L.name]]
        if L.name in DISCLOSED['lq_fails']:
            row['lq_fails'] = [d['lq_fails'], DISCLOSED['lq_fails'][L.name]]
        row['labelled_share_percent'] = [round(100 * d['counted_labelled_share'], 2),
                                         DISCLOSED['labelled_share_percent'].get(L.name)]
        cmp_[L.name] = row
    out['compare_with_disclosed'] = cmp_
    # the six-knot sample
    six = raw['six_rows']
    out['six_sample'] = {'done': len(six), 'by_law': {L.name: {'counted': sum(1 for r in six if r['base'][L.name]['counted']),
                                                              'bprime_fails': sum(1 for r in six if r['base'][L.name]['bprime_fails']),
                                                              'greatest': dict(Counter(r['base'][L.name]['greatest'] for r in six)),
                                                              'lq_fails': sum(1 for r in six if r['base'][L.name]['lq_fails_rounds']),
                                                              'labelled_share_counted':
                                                                  (sum(r['w'] for r in six if r['base'][L.name]['counted']) /
                                                                   sum(r['w'] for r in six)) if six else None}
                                                     for L in E.LAWS},
                         'listing_first_20': [r['idx6'] for r in six[:20]]}
    # arm W on the census
    armw = {}
    for L in E.RELEASE_BASES:
        for form in E.FORMS:
            key = L.name + '|' + form
            rs = [(r, r['armw'][key]) for r in kept]
            tot = {k: [0, 0] for k in E.KINDS}
            for r, w in rs:
                for k in E.KINDS:
                    tot[k][0] += w['place_rule_last_by_kind'][k][0]
                    tot[k][1] += w['place_rule_last_by_kind'][k][1]
            joint = [(r, w) for r, w in rs if w['right_on_every_structure']]
            armw[key] = {
                'runs': len(rs), 'joint_stratum': len(joint),
                'joint_labelled_share': sum(r['w'] for r, w in joint) / Wk,
                'places_by_kind_last_structure [right, wrong]': tot,
                'a': sum(1 for r, w in rs if w['a']), 'bprime': sum(1 for r, w in rs if w['bprime']),
                'c': sum(1 for r, w in rs if w['c']), 'd': sum(1 for r, w in rs if w['d']),
                'all_four': sum(1 for r, w in rs if w['a'] and w['bprime'] and w['c'] and w['d']),
                'P3_applicable': sum(1 for r, w in rs if w['P3'] is not None),
                'P3_fail': [r['idx'] for r, w in rs if w['P3'] is False],
                'P4_applicable': sum(1 for r, w in rs if w['P4'] is not None),
                'P4_fail': [r['idx'] for r, w in rs if w['P4'] is False],
                'P5_applicable': sum(1 for r, w in rs if w['P5'] is not None),
                'P5_fail': [r['idx'] for r, w in rs if w['P5'] is False],
                'P6_applicable': sum(1 for r, w in rs if w['P6'] is not None),
                'P6_fail': [r['idx'] for r, w in rs if w['P6'] is False],
                'counted_step3_equals_bprime_births': sum(1 for r, w in rs if w['counted_step3_equals_bprime_births']),
                'closing_runs': sum(1 for r, w in rs if w['closing_births']),
                'closing_runs_with_d_failing': sum(1 for r, w in rs if not w['d']),
                'joint_listing_if_small': [r['idx'] for r, w in joint] if len(joint) <= 200 else None,
                'not_joint_listing_if_small': ([r['idx'] for r, w in rs if not w['right_on_every_structure']]
                                               if len(rs) - len(joint) <= 400 else None),
                'joint_disclosed': (DISCLOSED['joint_BB'][L.name] if form == 'BB' else
                                    DISCLOSED['joint_PU_PB'][L.name][0 if form == 'PU' else 1]),
            }
    out['armw'] = armw
    write('part1.json', out)
    log('part1.json written')


if __name__ == '__main__':
    main()
