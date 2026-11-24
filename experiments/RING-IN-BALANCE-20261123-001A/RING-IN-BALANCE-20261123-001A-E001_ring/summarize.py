"""Read the result files of ticket A and print a verdict line for G and for each of P1 to P11 with the numbers behind
it.  Also writes summary.json.  Readings are those of deviations.md."""
import json

from common import load, write

V = {}


def verdict(name, ok, numbers):
    word = {True: 'HOLDS', False: 'FAILS', None: 'NOT COMPUTED HERE'}[ok]
    V[name] = {'verdict': word, 'numbers': numbers}
    print('%-4s %-18s %s' % (name, word, numbers))


def main():
    gate = load('gate.json')
    te = load('test_engine.json')
    a1, a2, a3, a4, a5, a6, a7 = (load('a%d.json' % i) for i in range(1, 8))

    # ------------------------------------------------------------------------------------------------------ G
    items = gate['items']
    ordinary_a1 = a1['G_ordinary']
    ord_a1_ok = all(v['ok'] for v in ordinary_a1.values())
    ord_a4 = {k: v for k, v in a4['runs'].items() if v['law']['name'] == 'ORD/STALL/RELEASE'}
    ord_a4_ok = not any(v['has_return_giving_parts_off'] for v in ord_a4.values())
    print('Gate G, item by item:')
    for k, v in items.items():
        print('     %-96s %s' % (k, {True: 'pass', False: 'FAIL', None: 'n/a (thread compares a1_trace.json)'}[v['ok']]))
    print('     %-96s %s' % ('G4 (A1 ordinary runs, Ring(n,3) n=3..16, R=8): no part comes apart',
                             'pass' if ord_a1_ok else 'FAIL'))
    print('     %-96s %s' % ('G4 (A4 ordinary law ORD/STALL on Ring(5,7,9;3), R=16): no return giving parts off',
                             'pass' if ord_a4_ok else 'FAIL'))
    g_ok = gate['all_computed_ok'] and ord_a1_ok and ord_a4_ok and te['_all_ok']
    verdict('G', g_ok, 'all items computed by this engine pass (%d gate items; self-checks %s: %d rounds vs naive '
            'implementation, %d structures vs brute force); the comparison with the pilot programs is left to the '
            'thread (a1_trace.json)' % (
                sum(1 for v in items.values() if v['ok'] is not None), 'pass' if te['_all_ok'] else 'FAIL',
                te['one full round vs naive implementation (random starts, laws)']['rounds_compared']
                + te['one full round vs naive implementation (named small cases)']['rounds_compared'],
                te['knot tests vs brute-force allowed states (parity x3, NAE, ext.)']['structures']))

    # ----------------------------------------------------------------------------------------------------- P1
    rows = [(k, r) for k, v in a1['P1'].items() for r in v]
    bad = [(k, r['t']) for k, r in rows if not r['ok']]
    verdict('P1', not bad, '%d (n, t) pairs checked, n = 5..15 odd, t = 2..12 even; failures: %s' % (len(rows), bad or 'none'))

    # ----------------------------------------------------------------------------------------------------- P2
    rows = [(k, r) for k, v in a1['P2'].items() for r in v if r.get('checked')]
    nc = [(k, r['t']) for k, v in a1['P2'].items() for r in v if not r.get('checked')]
    bad = [(k, r['t']) for k, r in rows if not r['ok']]
    verdict('P2', not bad, '%d (n, t) pairs checked (t = 2..10; t = 12 needs round 14 > R, D8: %d not checkable); '
            'each gave n + 1 parts, one the same as the waited part, n parts of two members h = 2 in one met set; '
            'failures: %s' % (len(rows), len(nc), bad or 'none'))

    # ----------------------------------------------------------------------------------------------------- P3
    bad_a, bad_b, nums = [], [], []
    for k, v in a1['P3'].items():
        for r in v['a']['rows']:
            if not r['ok']:
                bad_a.append((k, r['s'], r['member_counts'], r['all_same']))
        for r in v['b']['rows']:
            if not r['ok']:
                bad_b.append((k, r['s'], r['member_counts'], r['all_same']))
        nums.append('%s: %d parts followed (a), s = %d..%d' % (k.split('|')[0], v['a']['population'],
                                                               v['a']['rows'][0]['s'], v['a']['rows'][-1]['s']))
    verdict('P3', not bad_a, 'reading P3-a (D7): %s; failures: %s' % ('; '.join(nums), bad_a or 'none'))
    first_b = bad_b[0] if bad_b else None
    print('     literal reading P3-b (every part given off by any return): %s; %d failing (n, s); first: %s '
          '(member counts [s+2, s+3] mixed: the odd-round returns give off parts with one more member)'
          % ('FAILS' if bad_b else 'holds', len(bad_b), first_b))
    V['P3']['literal_reading_b'] = {'verdict': 'FAILS' if bad_b else 'HOLDS', 'failures': bad_b}

    # ----------------------------------------------------------------------------------------------------- P4
    bad = []
    nums = []
    for k, v in a1['P4'].items():
        ok = (v['in_balance_from_1_period_2'] and v['births_every_round'] and v['rows_ok']
              and v['ended_formal']['all_ok'] and v['ended_with_round2']['all_ok'])
        if not ok:
            bad.append(k)
        nums.append('%s %d+%d ended parts' % (k.split('|')[0], v['ended_formal']['checked'],
                                              v['ended_with_round2']['checked'] - v['ended_formal']['checked']))
    verdict('P4', not bad, 'in balance from round 1 with period 2 through round 20, 2n members in 1 part after odd '
            'rounds and 3n in n + 1 parts after even rounds, every part that came apart made exactly one knot with no '
            'usable distinction and ended (%s); failures: %s' % ('; '.join(nums), bad or 'none'))

    # ----------------------------------------------------------------------------------------------------- P5
    p5 = a1['P5']
    bad = []
    nums = []
    for k, v in sorted(p5.items(), key=lambda kv: kv[1]['n']):
        n = v['n']
        if n == 3:
            nums.append('Ring(3,3): %s (no prediction)' % v['kind'])
            continue
        if n in (4, 6):
            ok = v['returns_giving_parts_off'] == 0
            nums.append('Ring(%d,3): %d returns giving parts off' % (n, v['returns_giving_parts_off']))
        else:
            ok = v['chain']['n_full_chains'] == 2
            nums.append('Ring(%d,3): %d parts after round 2 return every two rounds through 12 giving %d off'
                        % (n, v['chain']['n_full_chains'], n // 2))
        if not ok:
            bad.append(k)
    verdict('P5', not bad, '; '.join(nums) + '; failures: %s' % (bad or 'none'))

    # ----------------------------------------------------------------------------------------------------- P6
    bad = []
    knots = 0
    for k, v in a2['runs'].items():
        c = v['check']
        knots += c['knots_checked']
        if not (c['all_knots_pass'] and c['methods_agree'] and c['all_rounds_extend']):
            bad.append(k)
    verdict('P6', not bad, '%d runs, %d knot tests by each method (rounds 0..12), %d round extensions; failures: %s'
            % (len(a2['runs']), knots, sum(len(v['rows']) - 1 for v in a2['runs'].values()), bad or 'none'))

    # ----------------------------------------------------------------------------------------------------- P7
    bad = []
    nk = sum(v['nae_knots_checked'] for v in a3['runs'].values())
    sc = sum(v['sat_calls'] for v in a3['runs'].values())
    for k, v in a3['runs'].items():
        if v['closing_ever'] or not v['births_equal_every_round'] or not v['nae_all_pass']:
            bad.append(k)
    verdict('P7', not bad, '%d runs: closing exception never applied; births equal to parity at rounds 1..12; '
            '%d knot tests not-all-equal (rounds 0..6), %d SAT calls, all pass; failures: %s'
            % (len(a3['runs']), nk, sc, bad or 'none'))

    # ----------------------------------------------------------------------------------------------------- P8
    runs = a4['runs']
    a_bad, b_bad, b_rep = [], [], []
    must = {'CAP-3', 'ONE-FEWER', 'RATION-3', 'CAP-4'}
    mustnot = {'ORD', 'FLOOR0', 'FLOOR1', 'RATION-2', 'CAP-2'}
    knot_fail, ext_fail = [], []
    for k, v in sorted(runs.items()):
        law = v['law']
        has = v['has_return_giving_parts_off']
        if law['treatment'] in ('STALL', 'CANCEL-OFFSHOOT', 'CANCEL-RETIRE') or law['no_offshoot']:
            if has:
                a_bad.append((k, v['off_return_part_sizes'], v['first_return_giving_parts_off']))
        elif law['treatment'] == 'CANCEL-WAIT':
            r = law['ration']
            if r in must and not has:
                b_bad.append((k, 'expected a return giving parts off, none'))
            if r in mustnot and has:
                b_bad.append((k, 'expected none', v['off_return_part_sizes'], v['first_return_giving_parts_off']))
            if r == 'RATION-4':
                b_rep.append((k, has, v['off_return_part_sizes']))
        kt = v['knot_test']
        if not kt['all_knots_pass'] or not kt['methods_agree']:
            knot_fail.append((k, kt['first_failing_round'], kt['methods_agree']))
        if not kt['all_rounds_extend']:
            ext_fail.append((k, kt['first_non_extending_round']))
    verdict('P8', not a_bad and not b_bad,
            '(a) %d of %d runs with STALL / CANCEL-OFFSHOOT / CANCEL-RETIRE / NO-OFFSHOOT have a part returning '
            'giving parts off; (b) %d stated CANCEL-WAIT cases come out otherwise' % (
                len(a_bad), sum(1 for v in runs.values() if v['law']['treatment'] != 'CANCEL-WAIT'
                                or v['law']['no_offshoot']), len(b_bad)))
    for x in a_bad:
        print('       (a) counterexample: %s  returning part sizes %s  first %s' % x)
    for x in b_bad:
        print('       (b) counterexample: %s' % (x,))
    for x in b_rep:
        print('       RATION-4 (reported): %s has one: %s, returning part sizes %s' % x)
    print('       knot test (rounds 0..6): %d of %d runs have a failing knot: %s' % (len(knot_fail), len(runs),
                                                                                  knot_fail or 'none'))
    print('       extension test (rounds 1..6): %d runs have a round that does not extend: %s' % (len(ext_fail),
                                                                                           ext_fail or 'none'))
    V['P8'].update({'a_counterexamples': a_bad, 'b_counterexamples': b_bad, 'ration4': b_rep,
                    'knot_fail': knot_fail, 'ext_fail': ext_fail})

    # ----------------------------------------------------------------------------------------------------- P9
    bad = [k for k, v in a5['P9'].items() if not v['ok']]
    others = {k: v['summary']['kind'] for k, v in a5['runs'].items() if '|' in k and not k.split('|')[0].endswith(',2)')}
    verdict('P9', not bad, 'Ring(5,2), Ring(7,2) under both laws: the same roster after every round from 1 on, one '
            'part of n members with h = 2; failures: %s.  Reported: %s' % (bad or 'none', others))

    # ---------------------------------------------------------------------------------------------------- P10
    bad = [k for k, v in a6['runs'].items() if not v['ok']]
    verdict('P10', not bad, '; '.join('%s: %s, waited knots of round 2 short in rounds 3..12: %s, return giving parts '
                                      'off: %s' % (k, v['summary']['kind'], v['waited2_short_every_later_round'],
                                                   v['has_return_giving_parts_off']) for k, v in a6['runs'].items())
            + '; failures: %s' % (bad or 'none'))

    # ---------------------------------------------------------------------------------------------------- P11
    bad = [k for k, v in a7['P11'].items() if not v['ok']]
    nums = []
    for k, v in a7['P11'].items():
        run = a7['runs'][k]
        f = v['first']
        nums.append('%s from s=%s, %d returns, off %s%s' % (k, f['s'] if f else '-', f['chain_length'] if f else 0,
                                                             f['chain'][0]['off_sizes'][:1] if f else '-',
                                                             ' (cut off at round %d of %d)' % (
                                                                 run['summary']['rounds_done'], run['R'])
                                                             if run['summary']['cut_off'] else ''))
    verdict('P11', not bad, '; '.join(nums) + '; failures: %s' % (bad or 'none'))

    # ------------------------------------------------------------------------------------------- resources
    res = {'gate': gate['resources'], 'traces': load('a1_trace.json')['resources'],
           **{'a%d' % i: x['resources'] for i, x in enumerate((a1, a2, a3, a4, a5, a6, a7), 1)}}
    print('resources (seconds, peak RSS MB):', json.dumps(res, sort_keys=True))
    write('summary.json', {'verdicts': V, 'resources': res})


if __name__ == '__main__':
    main()
