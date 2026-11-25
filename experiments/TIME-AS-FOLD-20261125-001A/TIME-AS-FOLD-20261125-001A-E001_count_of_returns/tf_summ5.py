"""Summaries of runs 5, 5b, 6 and the near-case supplement, with the comparison against compare.json's numbering rows.

Usage: python -B tf_summ5.py   (writes run5_summary.json, run6_summary.json)
"""
from __future__ import annotations

import gzip
import json
import os
import re
from collections import Counter, defaultdict

import tf_common as C


def load(fn):
    p = C.out_path(fn)
    if not os.path.exists(p):
        return []
    out = []
    with gzip.open(p, 'rt') as f:
        for line in f:
            out.append(json.loads(line))
    return out


def labels_two_knot():
    return sorted({d for s in C.named_stars()['two-knot'] for d in s})


def ranks_of(num):
    """The name of each label (in increasing label order): the prototype's 'distinction_ranks' / 'perm'."""
    labs = sorted(num['dist'])
    return [num['dist'].index(lab) for lab in labs]


def shift_key(kind):
    m = re.match(r'shift (\d+)( distinctions reversed)?( knots reversed)?', kind)
    if not m:
        return None
    return (int(m.group(1)), bool(m.group(2)), bool(m.group(3)))


def proto_shift_key(s):
    m = re.match(r'shift (\d+), (reversed, )?knots (as given|reversed)', s)
    return (int(m.group(1)), bool(m.group(2)), m.group(3) == 'reversed')


def summarise(rows, cases):
    by = defaultdict(list)
    for r in rows:
        by[(r['case'], r['sense'])].append(r)
    out = []
    for (cid, sense), rs in sorted(by.items(), key=lambda kv: str(kv[0])):
        case = next((c for c in cases if c['id'] == cid), None)
        named = Counter(json.dumps(r['named_start']) for r in rs)
        passed = [r for r in rs if r.get('survives')]
        unf = [r for r in rs if r.get('unfinished') or r.get('unfinished_tests')]
        und = [r for r in rs if not r.get('survives') and r.get('undecided_C_iii')]
        row = {'case': cid, 'item': case['item'] if case else rs[0].get('item'), 'sense': sense,
               'numberings_run': len(rs), 'distinct_named_starts': len(named),
               'passed': len(passed), 'not_passed': len(rs) - len(passed),
               'not_passed_with_undecided_tests': len(und), 'with_unfinished': len(unf),
               'survives_every_numbering': len(passed) == len(rs) and not unf,
               'distinct_named_starts_passed': len({json.dumps(r['named_start']) for r in passed})}
        if rs and 'shared_least_in_knot' in rs[0]:
            cond = Counter()
            for r in rs:
                k = 'least in knot 0: %s, least in knot 1: %s' % tuple(r['shared_least_in_knot'])
                cond[k + (' | passes' if r.get('survives') else ' | does not pass')] += 1
            row['condition_on_names'] = dict(sorted(cond.items()))
        # the four numberings of the study of parts that meet again (shift 0, distinctions and knots as given or
        # reversed)
        four = [r for r in rs if (shift_key(r['numbering']['kind']) or (None,))[0] == 0]
        if four:
            row['four_numberings_passed'] = sum(1 for r in four if r.get('survives'))
        out.append(row)
    return out


def compare_two_knot(rows, label):
    """Against compare.json numberings_two_knot (sets of numberings by their distinction ranks and knot order)."""
    c = C.compare()['numberings_two_knot']['per_law']
    res = {}
    for r in rows:
        pass
    groups = defaultdict(list)
    for r in rows:
        it = r['item']
        groups['%s|%s|%s' % (it['base'], it['choice'], it['knot_law'])].append(r)
    for key, rs in groups.items():
        ref = c.get(key, {}).get(label)
        if ref is None:
            continue
        refset = {(tuple(n['distinction_ranks']), tuple(n['knot_order'])) for n in ref['numberings']}
        mine = {(tuple(ranks_of(r['numbering'])), tuple(r['numbering']['knots'])) for r in rs if r.get('survives')}
        res[key] = {'prototype': ref['count'], 'mine': len(mine), 'same_set': mine == refset,
                    'only_mine': sorted(mine - refset)[:10], 'only_prototype': sorted(refset - mine)[:10]}
    return res


def compare_shifts(rows):
    ref = C.compare()['shifts']['rows']
    refd = {}
    for r in ref:
        refd[(r['start'], r['choice'], r['knot_law'], proto_shift_key(r['numbering']))] = r['passes']
    comp = Counter()
    diffs = []
    for r in rows:
        it = r['item']
        if it['rule'] != 'STEPS-2' or it['base'] != 'COPY-LAW(OFFSHOOT)' or it['group'] != 'main':
            continue
        sk = shift_key(r['numbering']['kind'])
        if sk is None:
            continue
        k = (it['start'], it['choice'], it['knot_law'], sk)
        if k not in refd:
            continue
        if r.get('unfinished'):
            continue
        comp['compared'] += 1
        if bool(r.get('survives')) == bool(refd[k]):
            comp['same'] += 1
        else:
            comp['differ'] += 1
            if len(diffs) < 40:
                diffs.append({'start': k[0], 'choice': k[1], 'knot_law': k[2], 'shift': k[3],
                              'mine': bool(r.get('survives')), 'prototype': refd[k]})
    return {'counts': dict(comp), 'differences': diffs}


def main():
    cases = C.load_json(C.out_path('cases.json')) if os.path.exists(C.out_path('cases.json')) else []
    r5 = load('run5.jsonl.gz')
    r5b = load('run5b.jsonl.gz')
    r6 = load('run6.jsonl.gz')
    near = load('run5_near_case.jsonl.gz')
    s5 = {'cases': len(cases), 'run5': summarise(r5, cases), 'run5b': summarise(r5b, cases),
          'near_case_supplement': summarise(near, [])}
    tk = [r for r in r5 if r['item']['start'] == 'two-knot' and r['item']['rule'] == 'STEPS-1'
          and r['item']['group'] == 'main']
    s5['two_knot_L1_vs_prototype'] = compare_two_knot(tk, 'C-iii (Y of two or more members)')
    s5['near_case_vs_prototype'] = compare_two_knot(near, 'near case (Y of one member)')
    s5['shifts_vs_prototype'] = compare_shifts(r5)
    C.write_json('run5_summary.json', s5)
    by = defaultdict(list)
    for r in r6:
        by[(r['case'], r['swap'], r['sense'])].append(r)
    s6 = []
    for (cid, sw, sense), rs in sorted(by.items(), key=lambda kv: str(kv[0])):
        case = next((c for c in cases if c['id'] == cid), None)
        s6.append({'case': cid, 'item': case['item'] if case else None, 'swap': sw, 'sense': sense,
                   'survives': any(r.get('survives') for r in rs),
                   'unfinished': any(r.get('unfinished') for r in rs),
                   'undecided_tests': sum(r.get('undecided_C_iii', 0) for r in rs)})
    C.write_json('run6_summary.json', s6)
    C.log('run 5: %d case-senses; 5b %d; near %d; run 6 %d' % (len(s5['run5']), len(s5['run5b']),
                                                                len(s5['near_case_supplement']), len(s6)))


if __name__ == '__main__':
    main()
