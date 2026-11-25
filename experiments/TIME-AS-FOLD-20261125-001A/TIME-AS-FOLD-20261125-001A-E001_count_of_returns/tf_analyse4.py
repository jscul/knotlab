"""Verdicts of run 4 (and its second pass): per law the tests, failed, held, undecided, for C and C-iii; the law's
verdict; P1, P5, P6, P12, P15, P16; and the comparison with compare.json's 44 C-iii cases.

Usage: python -B tf_analyse4.py   (writes run4_verdicts.json)
"""
from __future__ import annotations

import gzip
import json
from collections import Counter, defaultdict

import tf_common as C

PRIMARY = {('STEPS-1', 'COPY-LAW(RETIRE)'), ('STEPS-1', 'COPY-LAW(OFFSHOOT)'), ('STEPS-1', 'COPY-LAW(WAIT)'),
           ('MET', 'CAP-3(RETIRE)'), ('MET', 'CAP-3(OFFSHOOT)'), ('MET', 'RING-LAW')}
FULLER = {('STEPS-2', 'FLOOR1', 'BY-COUNT'), ('UP-TO-2', 'FLOOR1', 'BY-COUNT'), ('STEPS-2', 'CAP-3', 'IN-TURN')}
SECOND_ARM = ('MET:offshoot', 'MET:join', 'STEPS-1:join', 'STEPS-2:join', 'STEPS-3:join', 'STEPS-1:offshoot',
              'STEPS-2:offshoot', 'STEPS-3:offshoot')


def load(fn):
    out = []
    try:
        with gzip.open(C.out_path(fn), 'rt') as f:
            for line in f:
                out.append(json.loads(line))
    except FileNotFoundError:
        pass
    return out


def test_key(r):
    return (r['group'], r['start'], r['base'], r['rule'], r['choice'], r['knot_law'], r.get('k'), r['t0'],
            tuple(r['P0']), r['j'], tuple(r['X']))


def merged():
    first = [r for r in load('run4.jsonl.gz') if 'verdict_C' in r or r.get('unfinished')]
    second = {test_key(r): r for r in load('run4_second.jsonl.gz') if 'verdict_C' in r}
    out = []
    for r in first:
        if 'X' in r and test_key(r) in second:
            s = second[test_key(r)]
            s['first_pass'] = {'verdict_C': r.get('verdict_C'), 'verdict_C_iii': r.get('verdict_C_iii')}
            out.append(s)
        else:
            out.append(r)
    return out


def ration(base):
    return 'FLOOR1' if base.startswith('COPY-LAW') else 'CAP-3'


def law_verdict(n_held, n_dec, n_und):
    if n_held:
        return 'found (%d)' % n_held
    if n_und == 0:
        return 'none, every test decided (%d)' % n_dec
    return 'none among %d decided, %d undecided' % (n_dec, n_und)


def tally(rows, key):
    t = defaultdict(lambda: Counter())
    for r in rows:
        if 'X' not in r:
            continue
        k = key(r)
        d = t[k]
        d['tests'] += 1
        if r.get('unfinished'):
            d['unfinished'] += 1
            continue
        for claim, f in (('C', 'verdict_C'), ('C-iii', 'verdict_C_iii')):
            v = r[f]
            if v == 'fails':
                d[claim + ' failed'] += 1
            elif str(v).startswith('holds'):
                d[claim + ' held'] += 1
            else:
                d[claim + ' undecided'] += 1
        if r.get('C_fail_reason'):
            d['C failed: ' + r['C_fail_reason']] += 1
        if r.get('ruled_out_by_treatment'):
            d['ruled out by the treatment'] += 1
    out = {}
    for k, d in t.items():
        d = dict(d)
        for claim in ('C', 'C-iii'):
            h = d.get(claim + ' held', 0)
            fl = d.get(claim + ' failed', 0)
            u = d.get(claim + ' undecided', 0) + d.get('unfinished', 0)
            d['verdict ' + claim] = law_verdict(h, fl + h, u)
        out['|'.join(str(x) for x in k)] = d
    return out


def main():
    rows = merged()
    tests = [r for r in rows if 'X' in r]
    runs_no_test = [r for r in rows if 'X' not in r]
    by_law = tally(tests, lambda r: (r['group'], r['rule'] or 'none', r['base'], r['choice']))
    by_rule = tally(tests, lambda r: (r['group'], r['rule'] or 'none', ration(r['base'])))
    primary = [r for r in tests if r['group'] == 'main' and (r['rule'], r['base']) in PRIMARY]
    prim = tally(primary, lambda r: ('L1' if r['rule'] == 'STEPS-1' else 'L2', r['base'], r['choice']))
    # P1: under the control no X's trace differs between A and B, B', Ball under not-all-equal
    p1 = []
    for r in tests:
        if r['rule'] is None and r['knot_law'] == 'nae' and not r.get('unfinished'):
            for b in r['bars']:
                if b.get('course_differs') is not None:
                    p1.append((r['start'], r['base'], 'B', b['r']))
                bp = b.get("B'")
                if isinstance(bp, dict) and bp.get('course_differs') is not None:
                    p1.append((r['start'], r['base'], "B'", b['r']))
                ba = b.get('Ball')
                if isinstance(ba, dict) and ba.get('course_differs') is not None:
                    p1.append((r['start'], r['base'], 'Ball', b['r']))
    n_ctl = sum(1 for r in tests if r['rule'] is None and r['knot_law'] == 'nae')
    # P5: no C under a primary law
    p5_held = [r for r in primary if str(r.get('verdict_C')).startswith('holds')]
    ruled = [r for r in primary if r.get('ruled_out_by_treatment') is not None]
    # P6: C-iii under the primary laws only on the two-knot start under L1 with OLDEST or IN-TURN and
    # COPY-LAW(CANCEL-OFFSHOOT)
    p6_cases = Counter()
    p6_bad = []
    for r in primary:
        if r.get('verdict_C_iii') == 'holds':
            k = (r['start'], r['rule'], r['base'], r['choice'], r['knot_law'])
            p6_cases[k] += 1
            if not (r['start'] == 'two-knot' and r['rule'] == 'STEPS-1' and r['choice'] in ('OLDEST', 'IN-TURN')
                    and r['base'] == 'COPY-LAW(OFFSHOOT)'):
                p6_bad.append(k)
    # C-iii cases anywhere (every group)
    ciii = Counter()
    ciii_rows = []
    for r in tests:
        if r.get('verdict_C_iii') == 'holds':
            k = (r['group'], r['start'], r['base'], r['rule'], r['choice'], r['knot_law'])
            ciii[k] += 1
            ciii_rows.append({'run': list(k), 't0': r['t0'], 'Y_size': r['Y_size'], 'Y_periods': r['Y_periods'],
                              'j': r['j'], 'X': r['X'], 'X_size': len(r['X']), 'own_A': r['own_A_per_period'],
                              'joint_A': r['joint_A_per_period'],
                              'differs_at': [b.get('course_differs') for b in r['bars']],
                              'own_B_after_bar': [b.get('own_B_after_bar_by_round') for b in r['bars']],
                              'Y_ticks_A': (r['X_barred'] or {}).get('Y_ticks_A') if isinstance(r['X_barred'], dict)
                              else None,
                              'Y_ticks_X_barred': (r['X_barred'] or {}).get('Y_ticks_X_barred')
                              if isinstance(r['X_barred'], dict) else None,
                              'verdict_C': r['verdict_C'], 'C_fail_reason': r.get('C_fail_reason'),
                              'who_made': r.get('who_made'), 'what_made_meeting': r.get('what_made_meeting'),
                              'origin': r.get('origin'), "B'": [b.get("B'") for b in r['bars']],
                              'Ball': [b.get('Ball') for b in r['bars']]})
    c_held = [r for r in tests if str(r.get('verdict_C')).startswith('holds')]
    # P15: STEPS-2 with COPY-LAW(CANCEL-OFFSHOOT) C-iii cases: three-member parts of period 3 rounds, each returning
    # only while the other is there (X barred: Y returns fewer times)
    p15 = []
    for row in ciii_rows:
        g, st, base, rule, ch, kl = row['run']
        if g == 'main' and rule == 'STEPS-2' and base == 'COPY-LAW(OFFSHOOT)':
            ok = (row['Y_size'] == 3 and set(row['Y_periods']) == {3}
                  and row['Y_ticks_X_barred'] is not None and len(row['Y_ticks_X_barred']) < len(row['Y_ticks_A']))
            p15.append({'run': row['run'], 'form_as_predicted': ok, 'Y_size': row['Y_size'],
                        'Y_periods': row['Y_periods'], 'X_size': row['X_size'],
                        'Y_ticks_A': row['Y_ticks_A'], 'Y_ticks_X_barred': row['Y_ticks_X_barred']})
    # P16: STEPS-2 for offshoots of joins with COPY-LAW(CANCEL-WAIT) on the two-knot start
    p16 = []
    for r in tests:
        if (r['group'] == 'main' and r['rule'] == 'STEPS-2:join' and r['base'] == 'COPY-LAW(WAIT)'
                and r['start'] == 'two-knot'):
            xb = r['X_barred'] if isinstance(r['X_barred'], dict) else {}
            both = min(r['run_A']['rounds'], xb.get('rounds', 0))
            ya = [t for t in (xb.get('Y_ticks_A') or []) if t <= both]
            yb = [t for t in (xb.get('Y_ticks_X_barred') or []) if t <= both]
            p16.append({'choice': r['choice'], 'knot_law': r['knot_law'], 't0': r['t0'], 'Y_size': r['Y_size'],
                        'j': r['j'], 'X_size': len(r['X']), 'C_iii': r['verdict_C_iii'], 'C': r['verdict_C'],
                        'own_A': r['own_A_per_period'], 'rounds_both_reached': both,
                        'Y_ticks_A': xb.get('Y_ticks_A'), 'Y_ticks_X_barred': xb.get('Y_ticks_X_barred'),
                        'Y_unchanged_with_X_barred': ya == yb,
                        "B'_differs": [isinstance(b.get("B'"), dict) and b["B'"].get('course_differs') is not None
                                       for b in r['bars']],
                        'Ball_differs': [isinstance(b.get('Ball'), dict) and b['Ball'].get('course_differs')
                                         is not None for b in r['bars']]})
    p16_h = [p for p in p16 if p['C_iii'] == 'holds']
    p16_verdict = {'C_iii_tests': len(p16_h), 'Y_changed_with_X_barred': sum(1 for p in p16_h
                                                                             if not p['Y_unchanged_with_X_barred']),
                   'own_equal_over_four_periods': sum(1 for p in p16_h if len(set(p['own_A'])) == 1),
                   'structural_clause_without_numberings': 'holds' if p16_h and all(
                       p['Y_unchanged_with_X_barred'] and len(set(p['own_A'])) > 1 for p in p16_h) else 'fails'}
    # comparison with the prototype's 44 C-iii cases
    proto = C.compare()['paired']['cases']
    found = []
    for pc in proto:
        run = pc['run']
        rule = run['take'] if not run.get('family') else run['take'] + ':' + run['family'].split(':')[1]
        match = [row for row in ciii_rows if row['run'][0] == run['group'] and row['run'][1] == run['start']
                 and row['run'][2] == run['base'] and row['run'][3] == rule and row['run'][4] == run['choice']
                 and row['run'][5] == run['knot_law'] and row['Y_size'] == pc['Y_size']
                 and row['X_size'] == pc['X_size']]
        found.append({'prototype': pc, 'found_in_mine': len(match),
                      'mine': [{'t0': m['t0'], 'own_A': m['own_A'], 'differs_at': m['differs_at'], 'j': m['j']}
                               for m in match[:3]]})
    out = {'tests': len(tests), 'runs_without_test': len(runs_no_test),
           'unfinished_tests': sum(1 for r in tests if r.get('unfinished')),
           'runs_A_unfinished': sum(1 for r in runs_no_test if r.get('unfinished')),
           'second_pass_tests': sum(1 for r in tests if r.get('second_pass')),
           'by_law': by_law, 'by_rule': by_rule, 'primary': prim,
           'P1': {'control_tests_nae': n_ctl, 'differences': p1[:50], 'n_differences': len(p1),
                  'verdict': 'holds' if not p1 else 'fails'},
           'P5': {'primary_tests': len(primary), 'C_held': len(p5_held),
                  'ruled_out_by_treatment': sum(1 for r in ruled if r['ruled_out_by_treatment']),
                  'tests_under_CANCEL-OFFSHOOT_nae': len(ruled),
                  'verdict': 'holds' if not p5_held else 'fails'},
           'P6': {'cases': {'|'.join(k): v for k, v in p6_cases.items()}, 'outside': p6_bad,
                  'structural_first_half': 'holds' if not p6_bad else 'fails'},
           'C_iii_cases': {'|'.join(k): v for k, v in sorted(ciii.items())}, 'C_iii_rows': ciii_rows,
           'C_held': [{k: r.get(k) for k in ('group', 'start', 'base', 'rule', 'choice', 'knot_law', 't0', 'j', 'X')}
                      for r in c_held],
           'P15': p15, 'P15_verdict': {'cases': len(p15), 'of_the_predicted_form': sum(1 for p in p15
                                                                                      if p['form_as_predicted'])},
           'P16': p16, 'P16_verdict': p16_verdict, 'prototype_44': found,
           'prototype_44_found': sum(1 for f in found if f['found_in_mine'])}
    C.write_json('run4_verdicts.json', out)
    C.log('run 4: %d tests, %d unfinished; C held %d; C-iii cases %d; P1 %s; P5 %s; P6 %s; prototype cases found %d/%d'
          % (len(tests), out['unfinished_tests'], len(c_held), len(ciii), out['P1']['verdict'], out['P5']['verdict'],
             out['P6']['structural_first_half'], out['prototype_44_found'], len(found)))


if __name__ == '__main__':
    main()
