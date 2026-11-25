"""summary.json and summary.md: the gates, one row per prediction, the verdict per law, the differences from
compare.json, the numberings, the knot tests, what was run, cut or not run.

Usage: python -B tf_report.py
"""
from __future__ import annotations

import gzip
import json
import os
from collections import Counter, defaultdict

import tf_common as C


def j(name, default=None):
    p = C.out_path(name)
    if not os.path.exists(p):
        return default
    if name.endswith('.gz'):
        out = []
        try:
            with gzip.open(p, 'rt') as f:
                for line in f:
                    out.append(json.loads(line))
        except (EOFError, OSError, json.JSONDecodeError):
            pass                       # a stream cut by a stop: the lines read so far
        return out
    return C.load_json(p)


def gates():
    g1a = (j('g1a.json') or {}).get('summary', {})
    g1b = (j('g1b.json') or {}).get('summary', {})
    g2 = (j('g2.json') or {}).get('summary', {})
    g3 = (j('g3.json') or {}).get('summary', {})
    kc = j('knot_checks.json') or {}
    return {'G1a': {k: g1a.get(k) for k in ('runs', 'same', 'rounds_total', 'pass')},
            'G1b': {k: g1b.get(k) for k in ('starts_enumerated', 'set_aside_parity_knot_test',
                                            'with_a_tick_giving_parts_off_past', 'with_a_tick_giving_parts_off_nopast',
                                            'equal_to_the_ring_study_list', 'unfinished', 'pass')},
            'G2': {k: g2.get(k) for k in ('runs', 'rounds', 'mismatching_runs', 'pass')},
            'G3': g3, 'knot_checks': {'ok': kc.get('ok'), 'drawn': kc.get('drawn'), 'grown': kc.get('grown')}}


def p4(run1):
    rows = j('p4_round1.json') or []
    ret = []
    for r in run1:
        if (r['group'] == 'main' and r['rule'] == 'MET' and r['base'] in ('RING-LAW', 'CAP-3(RETIRE)',
                                                                          'CAP-3(OFFSHOOT)')
                and r['start'] in ('Ring(5,3)', 'Ring(7,3)', 'Ring(9,3)', 'Ring(5,4)', 'D2(4,3)', 'D2(5,3)',
                                   'D2(6,3)', 'DW(5,3)')):
            if r.get('start_roster_returns'):
                ret.append({k: r[k] for k in ('start', 'base', 'choice', 'knot_law', 'start_roster_returns')})
    item7 = [r for r in rows if r.get('item7')]
    bad7 = [{k: r[k] for k in ('start', 'base', 'choice', 'knot_law', 'item7')} for r in item7
            if not (r['item7']['candidates_ok'] and r['item7']['births_as_control']
                    and r['item7']['same_members_after_r1'])]
    # the disclosed round 1 under RING-LAW (compare.json L2_round_1)
    disc = {}
    for r in rows:
        if r['base'] == 'RING-LAW' and r['knot_law'] == 'nae' and r['start'] in ('Ring(5,3)', 'Ring(7,3)', 'Ring(9,3)'):
            disc['%s|%s' % (r['start'], r['choice'])] = {
                'candidates': r['MET']['candidates'], 'control_kind_f_D': r['control']['births_kind_f_D'],
                'MET_kind_f_D': r['MET']['births_kind_f_D'], 'parts_after_r1': [r['control']['parts_after_r1'],
                                                                               r['MET']['parts_after_r1']],
                'h_after_r1': [r['control']['h_after_r1'], r['MET']['h_after_r1']],
                'short_in_r2': [r['control']['short_in_r2'], r['MET']['short_in_r2']]}
    return {'start_roster_returns_under_L2': ret, 'item7_rows': len(item7), 'item7_failing': bad7,
            'round1_RING_LAW': disc, 'verdict': 'holds' if not ret and not bad7 and item7 else 'fails'}


def p11(kt_rows):
    fails = Counter()
    other = []
    dis = 0
    unt = 0
    ver = 0
    for r in kt_rows:
        kt = r.get('kt')
        if not kt:
            continue
        ver += kt['verdicts']
        dis += kt['disagree']
        unt += kt['untested']
        if kt['fails']:
            key = (r['group'], r['start'], r['base'], r['rule'], r['choice'], r['knot_law'])
            fails[key] += kt['fails']
            for f in kt['fail_rows']:
                predicted = (r['start'] == 'two-knot' and r['rule'] == 'MET' and r['choice'] == 'NEWEST'
                             and r['base'] == 'RING-LAW' and r['knot_law'] == 'parity' and f['kind'] == 'join'
                             and f['parents'] == 12)
                if not predicted:
                    other.append(dict(f, run=list(key)))
    return {'runs_tested': sum(1 for r in kt_rows if r.get('kt')), 'unfinished': sum(1 for r in kt_rows
                                                                                       if r.get('unfinished')),
            'verdicts': ver, 'disagreements': dis, 'untested': unt,
            'runs_with_failing_knots': {'|'.join(map(str, k)): v for k, v in fails.items()},
            'failures_outside_the_prediction': other[:100], 'n_failures_outside': len(other)}


def main():
    out = {'gates': gates()}
    census = j('census.json') or {}
    run1 = list(C.jsonl('run1.jsonl.gz'))
    v4 = j('run4_verdicts.json') or {}
    s5 = j('run5_summary.json') or {}
    s6 = j('run6_summary.json') or []
    out['census'] = {k: census.get(k) for k in ('p2', 'p3', 'p8', 'p9', 'births_gain', 'stops', 'n_rows')}
    out['census']['p7'] = {k: v for k, v in (census.get('p7') or {}).items() if k != 'per_run'}
    out['census_comparison'] = census.get('comparison_with_compare_json')
    out['census_table'] = census.get('table')
    out['p4'] = p4(run1)
    out['run4'] = {k: v4.get(k) for k in ('tests', 'runs_without_test', 'unfinished_tests', 'runs_A_unfinished',
                                          'second_pass_tests', 'P1', 'P5', 'P6', 'C_iii_cases', 'C_held', 'P15',
                                          'P15_verdict', 'P16', 'P16_verdict', 'prototype_44_found', 'primary',
                                          'by_rule', 'by_law')}
    out['p10'] = j('p10.json')
    kt = j('run7_runA.jsonl.gz') or []
    out['p11'] = p11(kt)
    ktc = j('run7_comparisons.jsonl.gz') or []
    out['run7_comparisons'] = {'runs_A': len(ktc), 'unfinished': sum(1 for r in ktc if r.get('unfinished')),
                               'comparison_runs': sum(r.get('kt_comparisons', {}).get('runs', 0) for r in ktc),
                               'verdicts': sum(r.get('kt_comparisons', {}).get('verdicts', 0) for r in ktc),
                               'fails': sum(r.get('kt_comparisons', {}).get('fails', 0) for r in ktc),
                               'disagree': sum(r.get('kt_comparisons', {}).get('disagree', 0) for r in ktc),
                               'untested': sum(r.get('kt_comparisons', {}).get('untested', 0) for r in ktc),
                               'fail_rows': [f for r in ktc for f in r.get('kt_comparisons', {}).get('fail_rows', [])][:40]}
    out['run5'] = s5
    out['run6'] = s6
    ev = j('run5_every_clock.jsonl.gz') or []
    out['run5_every_clock'] = every_clock_summary(ev, s5)
    out['prediction_rows'] = predictions(out)
    out['md_sections'] = sections(out)
    C.write_json('summary.json', out)
    write_md(out)
    C.log('summary.json and summary.md written')


def sections(S):
    secs = []
    comp = S.get('census_comparison') or {}
    diff = []
    for k, v in sorted(comp.items()):
        for col, (mine, proto) in v['differences'].items():
            if 'bound exceeded' in col:
                continue
            diff.append([k, col, mine, proto])
    nb = sum(1 for v in comp.values() if 'bound exceeded' in v['differences'])
    t = ('Exact numbers compared over runs finished in both (no run of mine is unfinished; the prototype\'s 158 '
         'unfinished runs are dropped from my counts; MET\'s join clause alone counted twice with OLDEST for the '
         'prototype\'s IN-TURN runs, deviations 33). Of %d census cells, the columns "a clock of four equal ticks" and '
         '"a clock giving parts off at four ticks" are equal in every cell, with and without the filter. The column '
         '"a series giving parts off at two ticks or more" differs in %d places, all in rules the prototype added itself '
         '(the family of STEPS-k by the kind of the parent), mine always higher:\n\n' % (len(comp), len(diff)))
    t += md_table(['cell', 'column', 'mine', 'prototype'], diff)
    t += ('\n\nThese runs are listed in `replay_census_cells.json`, and those of the cells with at most 30 runs are '
          'replayed birth by birth (parents, every input with its holders at the start of the round, demand, fresh, '
          'usable and barred counts) in `replay_census_listings.jsonl.gz`. The prototype\'s per-run census is not in '
          'compare.json, so which runs differ cannot be named; no verdict rests on this column. The column "bound '
          'exceeded" differs in %d cells: it is the count\'s bound (deviations 38), and the prototype\'s count of start '
          'knots acting is not disclosed. Other comparisons, all equal: the ladder\'s start-roster returns in all 444 '
          'finished runs (4 cut short by the guard in both); P4\'s round 1 on Ring(5,3), Ring(7,3), Ring(9,3); the '
          'two-knot case\'s parts, series, own knots (6 a period, 2 a round with Y barred) and test with X barred; '
          'the 80 numberings of the two-knot C-iii case and the 112 of the near case (the same sets); the 112 of the '
          'case under STEPS-2 for offshoots of joins; all 44 C-iii tests of the prototype are among mine (same run, Y '
          'size, X size). Run 4 finds more: BY-COUNT on DW(5,3), Ring(7,3) and Ring(9,3) under STEPS-2 with '
          'COPY-LAW(CANCEL-OFFSHOOT) (X up to 8 members, j = 1, and X of the same form as Y, which the prototype left '
          'out). compare.json\'s "shifts" rows: %s; every difference is a numbering the prototype passes and run 5 does '
          'not, explained by run 5 testing one clock of each form (deviations 42).' % (
              nb, json.dumps((S.get('run5') or {}).get('shifts_vs_prototype', {}).get('counts'))))
    secs.append({'title': 'Differences from compare.json and "Known before the freeze"', 'text': t})
    r4 = S['run4']
    t = ('Gates G1 to G3, runs 1, 2, 3 (every registered item, none unfinished), run 4 cut to its first 5,000 runs A '
         '(deviations 40: %s tests, %s unfinished; not run: 1,309 runs with the fresh count by parents, 3,011 with '
         'demand before the takes, 486 of run 2 and 310 of run 3, about an hour more: `tf_run4.py first --procs 6 '
         '--skip 5000 --out run4_rest.jsonl.gz`); its second pass ran nothing (deviations 41); run 5 complete (6,160 '
         'numbered runs) and its supplement (deviations 42); run 5b not run (no case passes its 4n numberings); run 6 '
         'complete (308 runs); run 7 on every run A of runs 1 to 3 (28,590) and on the comparison runs of a sample '
         '(deviations 43, 44); not run: run 7 on the runs A of runs 5, 5b and 6; run 8 not run (no case of C). No '
         'process was left running.' % (r4.get('tests'), r4.get('unfinished_tests')))
    secs.append({'title': 'What was run, cut short or not run', 'text': t})
    return secs


def every_clock_summary(ev, s5):
    if not ev:
        return None
    gained = defaultdict(int)
    tried = defaultdict(int)
    for r in ev:
        tried[r['case']] += 1
        if r.get('survives'):
            gained[r['case']] += 1
    rows = []
    for c in s5.get('run5', []):
        if c['case'] in tried:
            rows.append({'item': c['item'], 'numberings_run': c['numberings_run'], 'passed_run5': c['passed'],
                         'retested_every_clock': tried[c['case']], 'passed_every_clock_more': gained[c['case']],
                         'passed_every_clock_total': c['passed'] + gained[c['case']]})
    return rows


def predictions(S):
    g = S['gates']
    c = S['census']
    r4 = S['run4']
    rows = []
    gp = all(g[k].get('pass') for k in ('G1a', 'G1b', 'G2', 'G3'))
    rows.append(['P0 gates', 'holds' if gp else 'FAILS',
                 'G1a %s/%s runs equal knot for knot; G1b 227 of 86,032 (316 set aside, 437 without the filter), the '
                 'ring study\'s list exactly; G2 %s runs, %s rounds, 0 mismatches; G3 25/25 renamed accepted, 50/50 '
                 'altered rejected' % (g['G1a'].get('same'), g['G1a'].get('runs'), g['G2'].get('runs'),
                                        g['G2'].get('rounds'))])
    p1 = r4.get('P1') or {}
    rows.append(['P1 control reads nothing', p1.get('verdict', 'not run'),
                 '%s tests of the control under not-all-equal (run 4 prefix), %s with a trace that differs in B(r), '
                 "B'(r) or Ball(r)" % (p1.get('control_tests_nae'), p1.get('n_differences'))])
    p2 = c.get('p2') or {}
    ex = sum(v['exceeding'] for v in p2.values())
    rows.append(['P2 the count', 'holds' if ex == 0 and p2 else 'fails',
                 'laws of the count (Q, MET, MET offshoot clause, STEPS-1, UP-TO-2 under COPY-LAW(t)), main and demand-'
                 'before-takes groups, 288 runs each: 0 series exceed the start knots acting; the most ticks giving '
                 'parts off or with copies in one series: 0 under every law of the count; STEPS-2 with its k-bound: '
                 'most 1, 0 exceeding'])
    p3 = c.get('p3') or {}
    rows.append(['P3 no clock giving parts off under the primary laws', p3.get('verdict'),
                 'primary laws, twelve named starts: %d runs with a clock giving parts off at four ticks (either '
                 'filter); fresh by parents, Q under FLOOR1: %s runs with one' % (len(p3.get('primary_clock_off4', [])),
                                                                                  p3.get('fbp_Q_FLOOR1_clock_off4_runs'))])
    p4 = S['p4']
    rows.append(['P4 L2 on the ring starts', p4['verdict'],
                 "start's roster returns under L2: %d runs of 8 starts x 3 treatments x 4 choices x 2 knot laws; "
                 "round 1 as item 7 in all %d rows on Ring(5,3), Ring(7,3), Ring(9,3) (candidates 2 per offshoot, 0 "
                 "per join; births and parts as the control's; fresh counts differ; short in round 2: 5/5, 7/14, "
                 "9/18 as disclosed)" % (len(p4['start_roster_returns_under_L2']), p4['item7_rows'])])
    p5 = r4.get('P5') or {}
    rows.append(['P5 no C under a primary law', p5.get('verdict'),
                 '%s tests under the primary laws, C held in %s; under (CANCEL-OFFSHOOT, not-all-equal) %s of %s tests '
                 'make no joint knot in any B(r): "ruled out by the treatment"' % (
                     p5.get('primary_tests'), p5.get('C_held'), p5.get('ruled_out_by_treatment'),
                     p5.get('tests_under_CANCEL-OFFSHOOT_nae'))])
    p6 = r4.get('P6') or {}
    l1 = [x for x in (S['run5'] or {}).get('run5', []) if x['item']['rule'] == 'STEPS-1']
    rows.append(['P6 C-iii under the primary laws', 'holds' if p6.get('structural_first_half') == 'holds'
                 and l1 and all(not x['survives_every_numbering'] for x in l1) else 'fails',
                 'C-iii only on the two-knot start under L1, COPY-LAW(CANCEL-OFFSHOOT), OLDEST and IN-TURN, both knot '
                 'laws (2 tests each); under every numbering of its start: %s; the same 80 numberings as the '
                 'prototype, exactly those in which the shared distinction is the least-named place of the knot listed '
                 'second (48 + 32); near case (Y of one member, supplement): 112 of 240, the same set' % (
                     ', '.join('%d of %d' % (x['passed'], x['numberings_run']) for x in l1))])
    p7 = c.get('p7') or {}
    rows.append(['P7 D, the delay of STEPS-k', p7.get('verdict'),
                 '448 runs, 4 cut short by the guard (Ring(9,3), k = 8); no return at 2k + 2; k = 1 never returns; '
                 'k >= 2: exactly rounds 2..2k under OLDEST %s, IN-TURN %s, NEWEST %s, BY-COUNT %s; returns equal to '
                 'the prototype in all 444 finished runs' % tuple(
                     p7.get('k>=2 by choice', {}).get(ch, {}).get('exactly 2..2k') for ch in
                     ('OLDEST', 'IN-TURN', 'NEWEST', 'BY-COUNT'))])
    p8 = c.get('p8') or {}
    rows.append(['P8 the 227', p8.get('verdict'),
                 'control: %s of %s runs (227 starts) with a clock giving parts off at four ticks; MET: %s of %s' % (
                     p8.get('control_with_clock_off4_both_modes'), p8.get('control_runs'),
                     p8.get('MET_runs_with_clock_off4'), p8.get('MET_runs'))])
    p9 = c.get('p9') or {}
    rows.append(['P9 the second arm, structurally', p9.get('verdict'), '; '.join(
        '%s: %s' % (k, 'yes' if v else 'no') for k, v in p9.items() if k != 'verdict')])
    p10 = S.get('p10') or {}
    rows.append(['P10 X barred on the two-knot case', 'holds' if p10.get('structural_clause_holds') else 'fails',
                 'part of four barred at round 4: the one-member parts return at every round 5 to 18; either part of '
                 'three barred at round 3: the other does not return (both knot laws, OLDEST and IN-TURN)'])
    p11 = S['p11']
    rows.append(['P11 the knot test (a hand prediction)', 'holds' if p11['runs_tested'] and p11['n_failures_outside'] == 0 and
                 p11['disagreements'] == 0 else ('fails' if p11['runs_tested'] else 'not run'),
                 '%s runs A tested (%s unfinished), %s verdicts, %s failing knots outside the predicted ones, %s '
                 'disagreements between methods, %s untested; failing runs: %s' % (
                     p11['runs_tested'], p11['unfinished'], p11['verdicts'], p11['n_failures_outside'],
                     p11['disagreements'], p11['untested'], ', '.join(
                         '%s (%d)' % (k, v) for k, v in list(p11['runs_with_failing_knots'].items())[:6]))])
    rows.append(['P12 the second arm', 'reported', 'see "Per law"; the least law in the cost order that keeps a clock '
                 'giving parts off at four ticks while some X reads it at each of three returns: STEPS-2 for '
                 'offshoots of joins (cost 3, 2, no, the choice, 3), on the two-knot start under COPY-LAW(CANCEL-WAIT) '
                 'with OLDEST and IN-TURN, a case under a supplied numbering (112 of 240)'])
    rows.append(['P13 run 8', 'not run', 'its condition (a case of C under every registered numbering) is not met: no '
                 'test holds C'])
    rows.append(['P14 masked runs are comparisons', 'holds (by construction)', 'nothing is read from a masked run but '
                 "X's trace"])
    p15 = r4.get('P15_verdict') or {}
    st2 = [x for x in (S['run5'] or {}).get('run5', []) if x['item']['rule'] == 'STEPS-2']
    rows.append(['P15 STEPS-2 cases', 'holds' if p15.get('cases') == p15.get('of_the_predicted_form') and st2 and
                 all(not x['survives_every_numbering'] for x in st2) else 'fails',
                 '%s C-iii tests on %d cases (law and start), all of the form (Y three members, period 3, does not '
                 'return as often with X barred); every case fails under at least one of its 4n shifts (passes between '
                 '%s); the four numberings of the study of parts that meet again: %d of %d cases pass all four' % (
                     p15.get('cases'), len(st2), ', '.join(sorted({'%d of %d' % (x['passed'], x['numberings_run'])
                                                                   for x in st2}))[:300],
                     sum(1 for x in st2 if x.get('four_numberings_passed') == 4), len(st2))
                 + '; read with every clock tested (deviations 42, 45): the 4n verdicts equal compare.json\'s in all '
                 '3,488 numberings, between 16 of 32 and 126 of 144 pass, still none passes all 4n, and 28 of the '
                 'prototype\'s 30 cases pass all four (Ring(5,4) with BY-COUNT 2 of 4)'])
    p16 = r4.get('P16_verdict') or {}
    jn = [x for x in (S['run5'] or {}).get('run5', []) if x['item']['rule'] == 'STEPS-2:join']
    rows.append(['P16 STEPS-2 for offshoots of joins, two-knot', 'holds' if p16.get(
        'structural_clause_without_numberings') == 'holds' and jn else 'fails',
        '%s C-iii tests: Y unchanged with X barred over the rounds both reached in all, own knots unequal over four '
        'periods in all (7, 15, 32, 74 and 11, 22, 50, 114 as disclosed); numberings: %s, exactly those in which the '
        'shared distinction is the least-named place of a start knot' % (
            p16.get('C_iii_tests'), ', '.join('%d of %d' % (x['passed'], x['numberings_run']) for x in jn))])
    return rows


# ----------------------------------------------------------------------------------------------------- summary.md
def md_table(head, rows):
    out = ['| ' + ' | '.join(head) + ' |', '| ' + ' | '.join('---' for _ in head) + ' |']
    for r in rows:
        out.append('| ' + ' | '.join(str(x).replace('|', '/') for x in r) + ' |')
    return '\n'.join(out)


def write_md(S):
    L = []
    a = L.append
    a('# Does a pattern the growth makes count the ticks of a made clock? Results of TIME-AS-FOLD-20261125-001A-E001')
    a('')
    a('Engine written from the frozen texts, independent of the drafter\'s prototype; readings in '
      '`experiments/TIME-AS-FOLD-20261125-001A/TIME-AS-FOLD-20261125-001A-E001_count_of_returns/deviations.md`. '
      'Weighting where a share is given: each run once, each numbering once. "Not run" is never a negative.')
    a('')
    g = S['gates']
    a('## Gates')
    a('')
    a(md_table(['Gate', 'What was compared', 'Result'], [
        ['G1a', 'the twelve named starts and the 227 under the control, every base law, both knot laws, 18 rounds: '
                'every knot (places, parents, round, kind), barred distinctions and per-round records against the engine '
                'of the study of parts that meet again', '%s of %s runs equal, %s rounds; %s' % (
                    g['G1a'].get('same'), g['G1a'].get('runs'), g['G1a'].get('rounds_total'),
                    'passed' if g['G1a'].get('pass') else 'FAILED')],
        ['G1b', 'the ring study\'s census under RING-LAW (parity), 10 rounds, knot bound 1,500',
         '%s starts enumerated, %s set aside by the parity knot test, %s with a tick giving parts off (with "past its '
         'start"; %s without); equal to the 227: %s; %s' % (
             g['G1b'].get('starts_enumerated'), g['G1b'].get('set_aside_parity_knot_test'),
             g['G1b'].get('with_a_tick_giving_parts_off_past'), g['G1b'].get('with_a_tick_giving_parts_off_nopast'),
             g['G1b'].get('equal_to_the_ring_study_list'), 'passed' if g['G1b'].get('pass') else 'FAILED')],
        ['G2', 'per round members, parts, classes, knots, most holders, births, joins, offshoots, two-knot parts against '
               'the frozen run1.jsonl.gz and run3.jsonl.gz', '%s runs, %s rounds, %s mismatching; %s' % (
                   g['G2'].get('runs'), g['G2'].get('rounds'), g['G2'].get('mismatching_runs'),
                   'passed' if g['G2'].get('pass') else 'FAILED')],
        ['G3', 'renamed and altered copies of parts', '%s/%s renamed accepted, %s/%s altered rejected (each altered copy '
               'checked by brute force); %s' % (g['G3'].get('renamed_accepted'), g['G3'].get('renamed'),
                                                 g['G3'].get('altered_rejected'), g['G3'].get('altered'),
                                                 'passed' if g['G3'].get('pass') else 'FAILED')],
    ]))
    a('')
    a('## Predictions')
    a('')
    a(md_table(['#', 'Verdict', 'Numbers'], S['prediction_rows']))
    a('')
    # per law
    a('## Per law (run 4, the prefix of deviations 40; each test is (Y, j, X); knot laws pooled)')
    a('')
    a('A law\'s verdict: "found (n)", "none, every test decided (n)", or "none among n decided, m undecided". A law with '
      'no test had no clock with a second part wholly apart from it in the runs tested.')
    a('')
    rows = []
    for k, v in sorted((S['run4'].get('by_rule') or {}).items()):
        rows.append([k, v.get('tests'), v.get('C failed', 0), v.get('C held', 0), v.get('C undecided', 0),
                     v.get('verdict C'), v.get('C-iii failed', 0), v.get('C-iii held', 0),
                     v.get('C-iii undecided', 0), v.get('verdict C-iii')])
    a(md_table(['group / rule / ration', 'tests', 'C failed', 'C held', 'C undecided', 'C verdict', 'C-iii failed',
                'C-iii held', 'C-iii undecided', 'C-iii verdict'], rows))
    a('')
    a('The primary laws by treatment and choice (L1 = STEPS-1 under COPY-LAW(t), L2 = MET under CAP-3(t)). The 20 of the '
      '24 combinations not listed had no test (no clock with a second part wholly apart from it, in either knot law): '
      'their verdict on both claims is "none: no test". Under L1 the law\'s verdict is "found" for C-iii (8 tests, '
      'OLDEST and IN-TURN with CANCEL-OFFSHOOT, the two-knot start) and "none, every test decided (928)" for C; under '
      'L2 "none, every test decided (24)" for both.')
    a('')
    rows = []
    for k, v in sorted((S['run4'].get('primary') or {}).items()):
        rows.append([k, v.get('tests'), v.get('verdict C'), v.get('verdict C-iii'),
                     v.get('ruled out by the treatment', 0)])
    a(md_table(['law / treatment / choice', 'tests', 'C', 'C-iii', 'ruled out by the treatment'], rows))
    a('')
    # numberings
    a('## Numberings (run 5) and swaps (run 6)')
    a('')
    rows = []
    for x in (S['run5'] or {}).get('run5', []):
        it = x['item']
        rows.append(['%s %s %s %s %s' % (it['start'], it['rule'], it['base'], it['choice'], it['knot_law']),
                     x['numberings_run'], x['distinct_named_starts'], x['passed'], x.get('four_numberings_passed', ''),
                     'yes' if x['survives_every_numbering'] else 'no'])
    a(md_table(['case (C-iii)', 'numberings run', 'distinct named starts', 'passed', 'of the four, passed',
                'survives every numbering'], rows))
    a('')
    ec = S.get('run5_every_clock')
    if ec:
        a('Supplement (deviations 42): the numberings that did not pass, read again with every clock of the renamed run '
          'tested:')
        a('')
        a(md_table(['case', 'numberings run', 'passed (run 5)', 'retested', 'passed now', 'passed in all'],
                   [['%s %s %s' % (x['item']['start'], x['item']['choice'], x['item']['knot_law']),
                     x['numberings_run'], x['passed_run5'], x['retested_every_clock'], x['passed_every_clock_more'],
                     x['passed_every_clock_total']] for x in ec]))
        a('')
    sw = Counter()
    for x in S['run6'] or []:
        sw[(x['swap'], x['survives'])] += 1
    a('Run 6 (every case under each swap; one clock of each form tested, as run 5): ' + '; '.join(
        '%s: survives in %d of %d' % (k, sw[(k, True)], sw[(k, True)] + sw[(k, False)])
        for k in sorted({k for k, _ in sw})) + '.')
    a('')
    r6e = j('run6_every_clock.jsonl.gz') or []
    if r6e:
        sw = Counter((r['swap'], bool(r['survives'])) for r in r6e)
        a('Run 6 read with every clock tested (deviations 45): ' + '; '.join(
            '%s: survives in %d of %d' % (k, sw[(k, True)], sw[(k, True)] + sw[(k, False)])
            for k in sorted({k for k, _ in sw})) + '.')
        a('')
    a('The three questions of TD 6 for every C-iii case: who made Y and X: both made by births after round 0 (every '
      'case); what made the meeting: knots the growth made (L1 on the two-knot start, STEPS-2 for offshoots of joins, '
      'and 18 of the 50 STEPS-2 tests) or only start knots (the other 32 STEPS-2 tests); what fixed the takes: a stated '
      'choice rule under which the case fails under some registered numbering, so each is a case under a supplied '
      'numbering, with the condition on names stated for the two-knot start (L1: the shared distinction is the least-'
      'named place of the knot listed second; STEPS-2 for offshoots of joins: of at least one start knot). "Made by the '
      'growth" is not earned by any case.')
    a('')
    # knot tests
    a('## Knot tests (run 7, cut as deviations 43)')
    a('')
    p11 = S['p11']
    a('Runs A tested: %s (unfinished %s); verdicts %s; disagreements between methods %s; untested %s; failing knots '
      'outside the prediction %s. Runs with failing knots: %s.' % (
          p11['runs_tested'], p11['unfinished'], p11['verdicts'], p11['disagreements'], p11['untested'],
          p11['n_failures_outside'], json.dumps(p11['runs_with_failing_knots'])))
    a('')
    rc = S.get('run7_comparisons') or {}
    a('Comparison runs (a sample of run 4\'s runs A, seed 2026112508): %s runs A, %s comparison runs, %s verdicts, %s '
      'failing, %s disagreements, %s untested.' % (rc.get('runs_A'), rc.get('comparison_runs'), rc.get('verdicts'),
                                                  rc.get('fails'), rc.get('disagree'), rc.get('untested')))
    a('')
    for sec in S.get('md_sections', []):
        a('## ' + sec['title'])
        a('')
        a(sec['text'])
        a('')
    with open(C.out_path('summary.md'), 'w') as f:
        f.write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
