"""Verdicts of COPYING-PARTS-20261123-001A-E001: one line for the gate, for each of P1 to P10 and for the Reported items,
with the numbers behind each.  Reads gate.json, run1.json ... run6.json; writes summary.json."""
from cpcommon import load, write

V = {True: 'PASS', False: 'FAIL', None: 'n/a'}


def main():
    S = {}
    gate = load('gate.json')
    r1 = load('run1.json')
    r2 = load('run2.json')
    r3 = load('run3.json')
    r4 = load('run4.json')
    r5 = load('run5.json')
    r6 = load('run6.json')
    chk = load('run5_census_check.json')
    p = print

    # ------------------------------------------------------------------ gate
    p('GATE  %s  counts %s, trace (FLOOR0) %s, trace under FLOOR1 and ONE-FEWER %s' % (
        V[gate['gate_pass']], V[gate['counts_ok']], V[gate['trace_ok_floor0']], V[gate['trace_ok_all_rations']]))
    for tr, c in gate['counts'].items():
        p('      %-16s N(2..10) = %s  disclosed %s' % (tr, c['rounds_2_to_10'], c['disclosed']))
    for k, c in gate['trace_checks'].items():
        bad = [x for x, ok in c.items() if not ok]
        p('      trace %-26s %d checks, %s' % (k, len(c), 'all pass' if not bad else 'FAILED: %s' % bad))
    S['gate'] = gate['gate_pass']

    # ------------------------------------------------------------------ N(t) in full
    p('N(t) from round 0, the three starts under FLOOR0 (run 1; the last value is the round that passes 20,000 knots):')
    for key, v in r1['runs'].items():
        if v['law']['ration'] == 'FLOOR0':
            p('      %-32s rounds %d (<= 20,000 knots through %d)  N = %s' % (
                key.replace('/RELEASE', ''), v['rounds_done'], v['last_round_under_cap'], v['N']))

    # ------------------------------------------------------------------ P1-P3
    for P in ('P1', 'P2', 'P3'):
        ok = all(r1[P][s]['C2-a']['ok'] for s in r1[P]) and all(r1[P][s]['C2-b']['ok'] for s in r1[P])
        if P == 'P1':
            ok = ok and all(r1[P][s]['returns'][k]['p1_pattern_ok'] for s in r1[P] for k in r1[P][s]['returns'])
        S[P] = ok
        p('%-5s %s' % (P, V[ok]))
        for s, v in r1[P].items():
            a, b = v['C2-a'], v['C2-b']
            line = '      %-11s recurrence t = %d..%d (%d values) %s; to the last round under the cap t <= %d: %s' % (
                s, a['t_range'][0], a['t_range'][1], a['n_checked'], V[a['ok']], b['t_range'][1], V[b['ok']])
            if P == 'P1':
                ra = v['returns']['C2-a']
                line += ('; returns: %d two-knot parts, %d with s <= R-2 all return at s+2 with exactly one part off, '
                         'the same as it: %s (%d failures, %d unreturned)' % (
                             ra['n_two_knot_parts'], ra['n_checkable_s_le_R_minus_2'], V[ra['p1_pattern_ok']],
                             ra['n_p1_pattern_failures'], ra['n_unreturned_checkable']))
            if a['failures']:
                line += ' failures %s' % a['failures'][:3]
            p(line)

    # ------------------------------------------------------------------ P4
    v4 = r2['P4_verdict']
    S['P4'] = v4['pass']
    p('P4    %s  same roster FLOOR1 / ONE-FEWER as FLOOR0 at rounds 0-12: %s; every birth f >= 1: %s; every knot '
      'passes both parity methods: %s; every round extends: %s; closing exception never: %s' % (
          V[v4['pass']], v4['same_roster'], v4['every_birth_fresh'], v4['all_knots_pass_both_methods'],
          v4['every_round_extends'], v4['closing_never']))
    nb = sum(v['n_births'] for v in r2['runs'].values())
    nk = sum(sum(row['n_knots'] for row in v['parity_rows']) for v in r2['runs'].values())
    p('      18 runs; %d births; %d knot verdicts (knots x rounds); max parents of a birth %d, max demand %d; '
      'identical full round records too: %s' % (
          nb, nk, max(v['max_parents'] for v in r2['runs'].values()), max(v['max_D'] for v in r2['runs'].values()),
          all(x['records_identical'] for x in r2['P4'].values())))

    # ------------------------------------------------------------------ P5
    v5 = r2['P5_verdict']
    S['P5'] = v5['pass']
    last = {}
    for k, v in r2['runs'].items():
        last.setdefault(v['nae']['rounds_tested'][-1], []).append(k.replace('/RELEASE', ''))
    p('P5    %s  births under not-all-equal equal those under parity, rounds 1-12, all 18 runs: %s; not-all-equal '
      'test: every knot passes: %s (%d knot verdicts, %d SAT calls); tested from round 0 to round %s' % (
          V[v5['pass']], v5['births_equal'], v5['nae_all_pass'], v5['nae_knots_checked'], v5['nae_sat_calls'],
          '; to round '.join('%d (%d runs%s)' % (r, len(ks), '' if r == 10 else ': %s, round %d past 600 knots' % (
              ', '.join(ks), r + 1)) for r, ks in sorted(last.items()))))

    # ------------------------------------------------------------------ P6
    S['P6'] = r3['P6_pass']
    p('P6    %s' % V[r3['P6_pass']])
    for k, ok in r3['P6'].items():
        p('      %-80s %s' % (k, V[ok]))
    for key, v in r3['runs'].items():
        if v['n_failing_knots'] or v['n_zero_fresh_births'] or not v['all_rounds_extend']:
            p('      %s: births with f = 0: %s; failing knots: %s; first non-extending round %s' % (
                key, [(z['round'], z['parents'], z['D']) for z in v['zero_fresh_births']],
                [(f['id'], f['kind'], 'made %d' % f['made'], 'first fails %d' % f['first_fail'])
                 for f in v['failing_knots']], v['first_non_extending_round']))
    p('      every other law on Ring(5, 3): no birth with f = 0, no failing knot, every round extends')

    # ------------------------------------------------------------------ P7
    s7 = r4['P7']
    S['P7'] = s7['pass_C8a'] and s7['pass_C8b']
    p('P7    %s  reading C8-a (%d runs): %s; reading C8-b, with NO-OFFSHOOT + CANCEL-OFFSHOOT (%d runs): %s; '
      'copying runs: %s' % (V[S['P7']], s7['n_runs_C8a'], V[s7['pass_C8a']], s7['n_runs_C8b'], V[s7['pass_C8b']],
                            s7['rations_copying'] + s7['no_offshoot_copying_C8b']))
    kinds = {}
    for k, v in r4['runs'].items():
        if v['group'] in ('a', 'b') and v['law']['ration'] != 'RATION-3':
            kinds.setdefault(v['kind'], 0)
            kinds[v['kind']] += 1
    p('      kinds of those runs: %s' % kinds)

    # ------------------------------------------------------------------ P8
    S['P8'] = r4['P8_pass']
    p('P8    %s  %s' % (V[r4['P8_pass']], r4['P8']))
    for k, v in r4['runs'].items():
        if 'P8' in v and v['P8']['first']:
            f = v['P8']['first']
            p('      %-36s first after round %d, returns at %d: members (id,h,k) %s; met sets %s; exactly two sets of '
              'three sharing one member: %s; parts off %d (%d the same); %d such returns' % (
                  k.replace('/RELEASE', ''), f['round'], f['t'], f['members'],
                  ['%s via %s' % (m['members'], m['common_knots']) for m in f['met_sets']],
                  f['exactly_two_sets_of_three_sharing_one'], f['n_off'], f['n_same_off'], v['P8']['n_found']))

    # ------------------------------------------------------------------ P9
    fw = all(x['recurrence_ok'] for x in r4['P9'].values())
    full = all(x['copies'] and x['recurrence_ok'] for x in r4['P9'].values())
    S['P9'] = {'fails_when_column': fw, 'full_statement': full}
    p('P9    by its "Fails when" column (a recurrence fails from round 8 on): %s; full statement (the two-knot part '
      'still copies itself, and the recurrences): %s  (deviations.md C16)' % (V[fw], V[full]))
    for k, v in r4['runs'].items():
        if 'P9' in v:
            q = v['P9']
            p('      %-34s kind %-26s two-knot part copies itself: %-5s (%d returns, period %s); %s at n = 8..16: %s '
              '(holds from n = %s); N = %s' % (
                  k.replace('/HOLD', ''), v['kind'], q['two_knot_part_copies_itself'], q['n_two_knot_copies'],
                  q['two_knot_copy_periods'], q['recurrence'], V[q['ok']], q['holds_from_n'], v['N']))

    # ------------------------------------------------------------------ P10
    S['P10'] = r4['P10_pass']
    p('P10   %s  every FILLERS run has no member after round 4 (to 16); stopped at round: %s' % (
        V[r4['P10_pass']], sorted({(k.split('|')[0], x['stopped_round']) for k, x in r4['P10'].items()})))

    # ------------------------------------------------------------------ Reported: run 5
    p('REPORTED run 5: census check %s (19 / 200 / 3,157 starts, identities and order as the earlier census; set '
      'aside %s, the same starts); %d starts run under 6 laws, 10 rounds, cut off past 1,500 knots' % (
          V[chk['ok']], r5['set_aside_by_n'], r5['n_run']))
    p('      %-24s %6s %6s %8s %6s   by dead knots 0/1/2/3: starts; copy; knot fails' % (
        'law', 'starts', 'copy', 'kt-fail', 'cut'))
    for law, T in r5['tables'].items():
        a = T['all']
        dd = ' | '.join('%d: %d; %d; %d' % (d, T['dead=%d' % d]['starts'], T['dead=%d' % d]['copy'],
                                            T['dead=%d' % d]['kt_fail']) for d in range(4) if 'dead=%d' % d in T)
        p('      %-24s %6d %6d %8d %6d   %s' % (law, a['starts'], a['copy'], a['kt_fail'], a['cut_off'], dd))
    for law, T in r5['tables'].items():
        p('      %-24s by knots: %s' % (law, ' | '.join('n=%d: %d starts, %d copy, %d fail' % (
            n, T['n=%d' % n]['starts'], T['n=%d' % n]['copy'], T['n=%d' % n]['kt_fail']) for n in (3, 4, 5))))
    for law, x in r5['extra'].items():
        p('      %-24s kinds %s; smallest copying part %s; first failing round %s; failing runs with an f = 0 birth in '
          'that round %d/%d; mixed parts %d; method disagreements %d' % (
              law, x['kinds'], x['smallest_copy_size'], x['first_fail_round'],
              x['failing_runs_with_zero_fresh_birth_in_first_fail_round'], x['failing_runs'], x['mixed_parts_runs'],
              x['methods_disagree_runs']))
    p('      (rounds read only while the structure has <= 1,500 knots give the same counts: %s)' % all(
        T['all']['copy'] == T['all']['copy_b'] and T['all']['kt_fail'] == T['all']['kt_fail_b']
        for T in r5['tables'].values()))

    # ------------------------------------------------------------------ Reported: run 6
    for law, v in r6['runs'].items():
        p('REPORTED run 6 %s: %d rounds (cut off past 20,000 knots: %s), returns by part size %s' % (
            law, v['rounds_done'], v['cut_off'], v['return_sizes']))
        for c in v['classes']:
            f = c['first']
            p('      %s: %d returns, period %s, parts off per return %s, copies itself in %d; first after round %d: '
              'members %s, met sets %s; parts off over all returns %s' % (
                  c['shape_key'], c['count'], c['periods'], c['n_off'], c['copies'], f['s'],
                  [m[0] for m in f['detail']['members']],
                  ['%s via %s' % (m['members'], m['common_knots']) for m in f['detail']['met_sets']], c['off_shapes']))
    write('summary.json', {'verdicts': S})


if __name__ == '__main__':
    main()
