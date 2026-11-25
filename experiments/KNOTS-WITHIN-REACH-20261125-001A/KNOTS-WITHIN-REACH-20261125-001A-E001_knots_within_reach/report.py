"""Verdicts from the raw records: summary.json and summary.md (one row per prediction), and the listings.
usage: python -B report.py"""
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from fractions import Fraction

import kwr
import readings as RD

OUT = {}
ROWS = []          # (prediction, verdict, numbers)


def row(p, verdict, numbers):
    ROWS.append((p, verdict, numbers))


def load(name):
    return kwr.read_jsonl(kwr.out_path(name))


# ----------------------------------------------------------------------------------------------------------- run 2
def run2():
    R = load('run2.jsonl.gz')
    reg = [r for r in R if r['kind'] in ('named', 'bare ring', 'census')]
    out = {'registered_items': len(reg), 'all_items': len(R)}
    ans = Counter(r['verdict']['answer'] for r in reg)
    out['answers'] = dict(ans)
    table = []
    for r in sorted(reg, key=lambda r: r['item']):
        A, B = r.get('at_T', {}), r.get('at_2T', {})
        ent = {'item': r['item'], 'start': r['start'], 'law': r['law'], 'T_rounds': r['T'], 'kind': r['kind'],
               'answer': r['verdict']['answer'], 'why': r['verdict'].get('why'), 'rounds_done': r['rounds_done'],
               'stop': r['stop'], 'ended': r['ended'], 'knots': r['knots_final'],
               'parity_closing_round': r['parity_closing_round'],
               'births': RD.label(r['births_reading']) if r.get('births_reading') else None}
        for nm, X in (('T', A), ('2T', B)):
            if not X or X.get('not_reached'):
                ent[nm] = None
                continue
            g = X['gate']
            ent[nm] = {'round': X['round'], 'holds': g.get('holds'), 'j': g.get('j'), 'range': g.get('range'),
                       'k': g.get('k'), 'K': g.get('K'), 'least_l': g.get('least_l'), 'zmax': g.get('zmax'),
                       'k_by_j_on_widest': g.get('k_by_j_on_widest'), 'spread': g.get('spread'),
                       'k_by_class': g.get('k_by_class'), 'earlier': g.get('earlier'),
                       'class_sizes': {c: len(v) for c, v in X['classes'].items()},
                       'readings_by_class': _readings_by_class(X),
                       'swap_thresholds': _g(X.get('gate_swap_thresholds')),
                       'swap_parent_steps': _g(X.get('gate_parent_steps')),
                       'parent_steps_differ': len(X.get('H_parent_steps_differs', [])),
                       'swap_retired': _g(X.get('gate_retired_not_stepped')),
                       'P': _P(X.get('P')), 'P_live': _P(X.get('P_live_swap')),
                       'check_F_bad': X.get('check_F', {}).get('n_bad')}
        ent['check_E'] = len(r.get('check_E', []))
        ent['check_R'] = len(r.get('check_R', []))
        table.append(ent)
    out['table'] = table
    # checks
    out['checks'] = {'E_bad_runs': sum(1 for e in table if e['check_E']), 'R_bad_runs': sum(1 for e in table if e['check_R']),
                     'F_bad_knots': sum((e[t] or {}).get('check_F_bad') or 0 for e in table for t in ('T', '2T')),
                     'F_runs': sum(1 for e in table for t in ('T', '2T') if e[t] is not None)}
    # P5
    both_j2 = [e for e in table if e['answer'] == 'both' and (e['T'] or {}).get('j', 0) >= 2]
    decided = sum(1 for e in table if e['answer'] in ('both', 'gate only', 'no gate'))
    v5 = 'holds' if not both_j2 and 2 * decided >= len(table) else 'fails'
    row('P5', v5, 'runs passing the gate with the scaling condition at j >= 2: %d; decided %d of %d (both %d, gate only '
        '%d, no gate %d, undecided %d)' % (len(both_j2), decided, len(table), ans.get('both', 0), ans.get('gate only', 0),
                                            ans.get('no gate', 0), ans.get('undecided', 0)))
    out['P5'] = {'both_j_ge_2': [(e['start'], e['law']) for e in both_j2], 'decided': decided, 'of': len(table)}
    # P6
    out['P6'] = p6(R)
    # P7
    l67 = [e for e in table if e['law'] in ('L6', 'L7') and e['T'] and e['T']['holds']]
    js = Counter(e['T']['j'] for e in l67)
    l67_2 = [e for e in table if e['law'] in ('L6', 'L7') and e['2T'] and e['2T']['holds']]
    js2 = Counter(e['2T']['j'] for e in l67_2)
    v7 = 'holds' if l67 and set(js) == {2} else 'fails'
    row('P7', v7, 'L6 and L7 runs of run 2 holding the gate at T: %d, j: %s (at 2T: %d, j: %s)'
        % (len(l67), dict(js), len(l67_2), dict(js2)))
    out['P7'] = {'at_T': [(e['start'], e['law'], e['T']['j'], e['T']['range']) for e in l67],
                 'at_2T': [(e['start'], e['law'], e['2T']['j'], e['2T']['range']) for e in l67_2]}
    # P9
    out['P9'] = p9(R)
    # the swaps
    sw = defaultdict(Counter)
    for r in R:
        if r['kind'].startswith('swap'):
            sw[r['kind'] + ' ' + r['law']][r['verdict']['answer']] += 1
    out['swaps'] = {k: dict(v) for k, v in sw.items()}
    for nm, key in (('thresholds', 'swap_thresholds'), ('parent steps', 'swap_parent_steps'),
                    ('retired not stepped', 'swap_retired')):
        c = Counter()
        for e in table:
            for t in ('T',):
                x = e[t]
                if x and x.get(key):
                    c['holds j=%s' % x[key].get('j') if x[key].get('holds') else 'no gate'] += 1
        out['swaps']['gate under ' + nm + ' (at T)'] = dict(c)
    # the swap of the gate's thresholds (z >= 4a, C/c <= 3) with the scaling factor 1.5
    sw_ans = Counter()
    sw_both = []
    for r in reg:
        A, B = r.get('at_T') or {}, r.get('at_2T') or {}
        ga, gb = A.get('gate_swap_thresholds'), B.get('gate_swap_thresholds')
        if not ga:
            sw_ans['undecided'] += 1
            continue
        if not ga.get('holds'):
            sw_ans['undecided' if 'below' in str(ga.get('reason')) else 'no gate'] += 1
            continue
        if not gb:
            sw_ans['undecided'] += 1
            continue
        if gb.get('holds') and gb['j'] == ga['j'] and gb['range'][1] >= 1.5 * ga['range'][1]:
            sw_ans['both j=%d' % ga['j']] += 1
            sw_both.append((r['start'], r['law'], ga['j'], ga['range'], gb['range']))
        else:
            sw_ans['gate only'] += 1
    out['swap_thresholds_answers'] = dict(sw_ans)
    out['swap_thresholds_both'] = sw_both
    # the gates that hold at 2T only (no gate at T)
    out['gate_at_2T_only'] = [(e['start'], e['law'], e['2T']['j'], e['2T']['range']) for e in table
                              if e['answer'] == 'no gate' and e['2T'] and e['2T']['holds']]
    # listings: bare-ring made knots outside a factor 2 of r^2 on [4, n - 1] (KD 8.8's upper end; PR Known 2)
    lst = []
    for r in R:
        if r['start'].startswith('Ring(') and r['start'].endswith(',2)') and r['law'] == 'L0' and \
                r['kind'] in ('named', 'bare ring'):
            n = int(r['start'][5:-3])
            for nm in ('at_T', 'at_2T'):
                X = r.get(nm) or {}
                if not X or X.get('not_reached'):
                    continue
                for c in ('b', 'c'):
                    for u in X['classes'][c]:
                        ok, C, cc = RD.ratio_ok(X['H'][str(u)], 0, 4, n - 1, 2)
                        if not ok:
                            lst.append({'start': r['start'], 'rounds': X['round'], 'class': c, 'knot': u,
                                        'C_over_c_on_4_to_n-1': float(C / cc), 'H_0_to_n': X['H'][str(u)][:n + 1]})
    kwr.write_json(kwr.out_path('listing_run2_bare_ring_made_knots.json'), lst)
    out['listing_bare_ring_made_knots'] = Counter('%s at %d' % (x['start'], x['rounds']) for x in lst)
    OUT['run2'] = out
    return out


def _g(g):
    if not g:
        return None
    return {k: g.get(k) for k in ('holds', 'j', 'range', 'k', 'K', 'spread')}


def _P(P):
    if not P:
        return None
    return {'members': P.get('members'), 'parts': P.get('parts'), 'part_sizes': P.get('part_sizes', [])[:10],
            'labels': [c['label'] for c in P.get('counted_from', [])],
            'greatest_ws': [c['greatest_ws'] for c in P.get('counted_from', [])]}


def _readings_by_class(X):
    out = {}
    for c, ks in X['classes'].items():
        out[c] = dict(Counter(RD.label(X['reading'][str(u)]) for u in ks))
    return out


def p6(R):
    """P6, both readings of "on [4, n - 1] the made knots alone read j = 2 and the start knots do not":
    (A) each knot within a factor 2 of c r^2 on [4, n - 1]; (B) the full gate (z >= 8a) on [4, n - 1]."""
    out = {}
    allok_gate = True
    okA = okB = True
    lines = []
    for r in R:
        if r['kind'] != 'bare ring':
            continue
        n = int(r['start'][5:-3])
        ent = {'answer': r['verdict']['answer'], 'j': r['verdict'].get('j'), 'range_264': r['verdict'].get('range_T'),
               'range_528': r['verdict'].get('range_2T')}
        gate_ok = r['verdict']['answer'] == 'both' and r['verdict'].get('j') == 1
        allok_gate &= gate_ok
        for nm in ('at_T', 'at_2T'):
            X = r[nm]
            made = [u for c in ('b', 'c') for u in X['classes'][c]]
            start = X['classes']['a']
            z = n - 1
            A_made = sum(1 for u in made if RD.ratio_ok(X['H'][str(u)], 0, 4, z, 2)[0])
            A_start = sum(1 for u in start if RD.ratio_ok(X['H'][str(u)], 0, 4, z, 2)[0])
            gm = RD.gate({u: X['H'][str(u)][:z + 1] for u in made})
            gs = RD.gate({u: X['H'][str(u)][:z + 1] for u in start})
            ent[nm] = {'A_made_within_2': [A_made, len(made)], 'A_start_within_2': [A_start, len(start)],
                       'B_made_gate': {'holds': gm['holds'], 'j': gm.get('j'), 'reason': gm.get('reason')},
                       'B_start_gate': {'holds': gs['holds'], 'j': gs.get('j'), 'reason': gs.get('reason')}}
            a_ok = A_made == len(made) and A_start < len(start)
            b_ok = gm['holds'] and gm.get('j') == 2 and not (gs['holds'] and gs.get('j') == 2)
            ent[nm]['A_holds'] = a_ok
            ent[nm]['B_holds'] = b_ok
            okA &= a_ok
            okB &= b_ok
        out['n=%d' % n] = ent
        lines.append('n=%d: gate %s j=%s [264: %s, 528: %s]; (A) made %s start %s; (B) made gate %s start gate %s'
                     % (n, ent['answer'], ent['j'], ent['range_264'], ent['range_528'],
                        ent['at_T']['A_made_within_2'], ent['at_T']['A_start_within_2'],
                        ent['at_T']['B_made_gate']['holds'], ent['at_T']['B_start_gate']['holds']))
    vA = 'holds' if allok_gate and okA else 'fails'
    vB = 'holds' if allok_gate and okB else 'fails'
    row('P6 (reading A: each knot within a factor 2 on [4, n-1])', vA, '; '.join(lines))
    row('P6 (reading B: the full gate, z >= 8a, on [4, n-1])', vB, 'gate and scaling at 264/528 with j = 1 for every n: '
        '%s; see the reading A row for the per-n numbers' % allok_gate)
    out['verdict_A'] = vA
    out['verdict_B'] = vB
    out['gate_and_scaling_all_n'] = allok_gate
    return out


def p9(R):
    out = {}
    fails = []
    labs = Counter()
    labs_with = Counter()
    for r in R:
        if r['law'] not in ('L1', 'L6', 'L7'):
            continue
        if r['kind'] not in ('named', 'bare ring', 'census', 'P only'):
            continue
        Ps = []
        if r['kind'] == 'P only':
            Ps = [r.get('P_%d' % r['T']), r.get('P_%d' % (2 * r['T']))]
        else:
            Ps = [(r.get('at_T') or {}).get('P'), (r.get('at_2T') or {}).get('P')]
        for P in Ps:
            if not P:
                continue
            for c in P.get('counted_from', []):
                lab = c['label']
                target = labs_with
                target[lab] += 1
                if r['kind'] != 'P only':
                    labs[lab] += 1
                if lab.startswith('POWER(') and lab[6] in '23':
                    fails.append((r['start'], r['law'], r['kind'], c['member'], lab))
    f_wo = [f for f in fails if f[2] != 'P only']
    row('P9 (L6, L7 of run 2, as registered)', 'holds' if not f_wo else 'fails',
        'readings of P from every member counted from: %s; POWER(j >= 2): %d' % (dict(labs), len(f_wo)))
    row('P9 (with L1 grown on run 2\'s starts, supplement added after the freeze)', 'holds' if not fails else 'fails',
        'readings: %s; POWER(j >= 2): %d' % (dict(labs_with), len(fails)))
    out['fails'] = fails[:50]
    out['labels_L6_L7'] = dict(labs)
    out['labels_with_L1'] = dict(labs_with)
    return out


# ----------------------------------------------------------------------------------------------------------- run 5
LEVELS = ('i-1', 'i-2', 'i-3')


def stage_key(rec, st):
    return (st['knots'], st['distinctions'], st['round'], rec['index'])


def run5():
    out = {}
    W = {r['index']: r['w_labelled'] for r in []}
    C = kwr.census()
    for lab in ('L0', 'L1', 'L3', 'L6', 'L7'):
        recs = load('run5_%s.jsonl.gz' % lab)
        if not recs:
            continue
        o = {'runs': len(recs), 'stages': Counter(), 'strata': Counter(), 'orders': defaultdict(lambda: [0, 0, 0]),
             'smallest': {}, 'S': defaultdict(lambda: {'S': 0, 'mean': 0.0, 'var': 0.0, 'pair_var': Fraction(0),
                                                       'stages': 0, 'exact_stages': 0}),
             'LW': Counter(), 'btw': Counter(), 'knot_test': Counter(), 'small': Counter(),
             'history': {'stages': 0, 'disc_stage': Counter(), 'disc_hist': Counter(), 'both': Counter(),
                         'stage_only': Counter(), 'hist_only': Counter()},
             'discordant_stage_share': {}, 'kappa_sign_by_ws': defaultdict(Counter), 'not_run': [],
             'P14': {'untied': 0, 'comparisons': 0}}
        level_stages = {lv: [] for lv in LEVELS}
        other_levels = {(yk, lv): [] for yk in ('ws', 'hs') for lv in LEVELS}
        lw_fail_stages = []
        wsum = {'census': Counter(), 'labelled': Counter()}
        for rec in recs:
            kt = rec.get('knot_test')
            if kt:
                o['knot_test']['tested'] += kt['tested']
                o['knot_test']['fails'] += len(kt['fails'])
                o['knot_test']['untested'] += kt['untested']
                o['knot_test']['direct_compared'] += kt['direct_compared']
                o['knot_test']['disagree'] += kt['disagree']
            wl = C[rec['index']]['w_labelled']
            for st in rec['stages']:
                o['stages'][st['status']] += 1
                if st['status'] != 'computed':
                    if len(o['not_run']) < 2000:
                        o['not_run'].append([rec['start'], st['round'], st['status'], st['members'], st['shared']])
                    continue
                for k, v in st['strata'].items():
                    o['strata'][k] += v
                ords = st.get('orders', {})
                for k, v in ords.items():
                    if k in ('n', 'kappa_sign_by_ws'):
                        continue
                    acc = o['orders'][k]
                    for i in range(3):
                        acc[i] += v[i]
                for w, sg in ords.get('kappa_sign_by_ws', {}).items():
                    for sgn, c in sg.items():
                        o['kappa_sign_by_ws'][w][sgn] += c
                wsum['census']['stages'] += 1
                wsum['labelled']['stages'] += wl
                for yk in ('delta', 'ws', 'hs'):
                    for xw in ('kappa', 'gamma'):
                        d1 = ords.get('%s|%s|i-1' % (xw, yk), [0, 0, 0])[1]
                        d2 = ords.get('%s|%s|i-2' % (xw, yk), [0, 0, 0])[1]
                        d3 = ords.get('%s|%s|i-3' % (xw, yk), [0, 0, 0])[1]
                        key = '%s|%s' % (xw, yk)
                        lv = 'i-3' if d3 else ('i-2' if d2 else ('i-1' if d1 else None))
                        if lv:
                            wsum['census'][key + '|' + lv] += 1
                            wsum['labelled'][key + '|' + lv] += wl
                        if yk == 'delta' and xw == 'kappa':
                            if d2:
                                level_stages['i-2'].append((stage_key(rec, st), rec['start'], st['round'],
                                                            ords.get('kappa|delta|i-1')))
                            if d3:
                                level_stages['i-3'].append((stage_key(rec, st), rec['start'], st['round'],
                                                            ords.get('kappa|delta|i-1')))
                            if d1 and not d2:
                                level_stages['i-1'].append((stage_key(rec, st), rec['start'], st['round'],
                                                            ords.get('kappa|delta|i-1')))
                for yk in ('ws', 'hs'):
                    d1 = ords.get('kappa|%s|i-1' % yk, [0, 0, 0])[1]
                    d2 = ords.get('kappa|%s|i-2' % yk, [0, 0, 0])[1]
                    d3 = ords.get('kappa|%s|i-3' % yk, [0, 0, 0])[1]
                    for lv, cond in (('i-2', d2), ('i-3', d3), ('i-1', d1 and not d2)):
                        if cond:
                            other_levels[(yk, lv)].append((stage_key(rec, st), rec['start'], st['round'],
                                                           ords.get('kappa|%s|i-1' % yk)))
                if st.get('LW', {}).get('tests') and not st['LW']['holds']:
                    lw_fail_stages.append((stage_key(rec, st), rec['start'], st['round']))
                if lab == 'L3' and rec['n'] in (3, 4) and st['round'] <= 3:
                    v = ords.get('kappa|delta|i-1')
                    if v:
                        o['P14']['comparisons'] += sum(v)
                        o['P14']['untied'] += v[0] + v[1]
                sh = st.get('shuffle', {})
                for xw, v in sh.items():
                    a = o['S'][xw]
                    a['S'] += v['S']
                    a['mean'] += v['mean']
                    a['var'] += v['var']
                    a['pair_var'] += Fraction(v['pair_shuffle_var'])
                    a['stages'] += 1
                    a['exact_stages'] += bool(v['exact'])
                lw = st.get('LW', {})
                if lw.get('tests'):
                    o['LW']['tests'] += 1
                    o['LW']['fails'] += (not lw['holds'])
                    o['LW']['fails_strict'] += bool(lw.get('strict_reversals'))
                    if not lw['holds'] and 'smallest_fail' not in o:
                        pass
                b = st.get('betweenness', {})
                if b.get('tested'):
                    o['btw']['triples'] += b['tested']
                    o['btw']['failing'] += b['failing']
                    o['btw']['stages_tested'] += 1
                    o['btw']['stages_failing'] += bool(b['failing'])
                sm = st.get('small')
                if sm:
                    o['small']['stages'] += 1
                    o['small']['Z_bad'] += (not sm['Z_ok'])
                    o['small']['I_bad'] += sm['I_bad']
                    o['small']['N_bad'] += sm['N_bad']
                    o['small']['pairs'] += sm['pairs']
                    ho = sm.get('history_orders')
                    if ho:
                        h = o['history']
                        h['stages'] += 1
                        for lv in LEVELS:
                            ds = ords.get('kappa|delta|%s' % lv, [0, 0, 0])[1] > 0
                            dh = ho[lv][1] > 0
                            h['disc_stage'][lv] += ds
                            h['disc_hist'][lv] += dh
                            h['both'][lv] += ds and dh
                            h['stage_only'][lv] += ds and not dh
                            h['hist_only'][lv] += dh and not ds
        for lv in LEVELS:
            L = sorted(level_stages[lv])
            if L:
                k0 = L[0]
                o['smallest'][lv] = {'knots': k0[0][0], 'distinctions': k0[0][1], 'round': k0[2], 'start': k0[1],
                                     'comparisons_kappa_delta': k0[3], 'S': k0[3][0] - k0[3][1],
                                     'tied_with': sum(1 for x in L if x[0][:3] == k0[0][:3]) - 1,
                                     'stages_at_level': len(L)}
            else:
                o['smallest'][lv] = None
        o['smallest_ws_hs'] = {}
        for (yk, lv), Lst in other_levels.items():
            Lst.sort()
            o['smallest_ws_hs']['%s|%s' % (yk, lv)] = None if not Lst else {
                'knots': Lst[0][0][0], 'distinctions': Lst[0][0][1], 'round': Lst[0][2], 'start': Lst[0][1],
                'S': Lst[0][3][0] - Lst[0][3][1], 'stages_at_level': len(Lst)}
        lw_fail_stages.sort()
        o['LW_smallest_fail'] = None if not lw_fail_stages else {
            'knots': lw_fail_stages[0][0][0], 'distinctions': lw_fail_stages[0][0][1], 'round': lw_fail_stages[0][2],
            'start': lw_fail_stages[0][1]}
        for key in list(wsum['census']):
            if key == 'stages':
                continue
            o['discordant_stage_share'][key] = {'census': wsum['census'][key] / wsum['census']['stages'],
                                                'labelled': wsum['labelled'][key] / wsum['labelled']['stages'],
                                                'stages': wsum['census'][key]}
        o['stages_weighted'] = {'census': wsum['census']['stages'], 'labelled_weight': wsum['labelled']['stages']}
        o['S'] = {k: dict(v, pair_var=float(v['pair_var']), z_member=(v['S'] - v['mean']) / v['var'] ** 0.5
                          if v['var'] > 0 else None, z_pair=v['S'] / float(v['pair_var']) ** 0.5
                          if v['pair_var'] > 0 else None) for k, v in o['S'].items()}
        o['orders'] = dict(o['orders'])
        o['kappa_sign_by_ws'] = {k: dict(v) for k, v in o['kappa_sign_by_ws'].items()}
        for k in ('stages', 'strata', 'LW', 'btw', 'knot_test', 'small'):
            o[k] = dict(o[k])
        o['history'] = {k: (dict(v) if isinstance(v, Counter) else v) for k, v in o['history'].items()}
        out[lab] = o
    OUT['run5'] = out
    if not out:
        return out
    # P12
    sm = {lab: out[lab]['smallest'].get('i-2') for lab in ('L0', 'L1', 'L6') if lab in out}
    ok12 = all(v and v['knots'] == 7 and v['start'] == 'census:157' and v['round'] == 1 and v['S'] == 0
               for v in sm.values()) and len(sm) == 3
    row('P12', 'holds' if ok12 else 'fails', '; '.join('%s: %s' % (lab, ('%d knots, %d distinctions, %s after round %d, '
        'S = %d' % (v['knots'], v['distinctions'], v['start'], v['round'], v['S'])) if v else 'none')
        for lab, v in sm.items()))
    # P13
    s13 = {lab: out[lab]['S'].get('gamma', {}).get('S') for lab in ('L0', 'L1', 'L6') if lab in out}
    ok13 = all(v is not None and v > 0 for v in s13.values()) and len(s13) == 3
    row('P13', 'holds' if ok13 else 'fails', '; '.join('%s: sum S = %s (member shuffle mean %.1f, z %.1f; pair '
        'shuffle z %.1f)' % (lab, s13[lab], out[lab]['S']['gamma']['mean'], out[lab]['S']['gamma']['z_member'] or 0,
                             out[lab]['S']['gamma']['z_pair'] or 0) for lab in s13))
    # P14
    if 'L3' in out:
        p = out['L3']['P14']
        row('P14', 'holds' if p['untied'] == 0 else 'fails', 'L3, rounds 1 to 3 of the three- and four-knot starts: '
            '%d comparisons in stratum (i), %d untied in delta' % (p['comparisons'], p['untied']))
    # P15
    parts = []
    status = []
    for lab in ('L0', 'L1', 'L6', 'L3'):
        if lab not in out:
            continue
        lw, bt = out[lab]['LW'], out[lab]['btw']
        if lw.get('tests', 0) == 0 or bt.get('triples', 0) == 0:
            st = 'untested'          # a clause no stage tests is not run, never a negative
            if lw.get('tests', 0) > 0 and lw.get('fails', 0) == 0:
                st = 'held'
            if bt.get('triples', 0) > 0 and bt.get('failing', 0) == 0:
                st = 'held'
        elif lw.get('fails', 0) > 0 and bt.get('failing', 0) > 0:
            st = 'fails as predicted'
        else:
            st = 'held'
        status.append(st)
        parts.append('%s: L-W fails on %d of %d stages testing it; betweenness fails on %d of %d triples (%d of %d '
                     'stages) [%s]' % (lab, lw.get('fails', 0), lw.get('tests', 0), bt.get('failing', 0),
                                       bt.get('triples', 0), bt.get('stages_failing', 0), bt.get('stages_tested', 0), st))
    if 'held' in status:
        v15 = 'fails'
    elif 'untested' in status:
        v15 = 'undecided (a clause is tested on no stage)'
    else:
        v15 = 'holds'
    row('P15', v15, '; '.join(parts))
    return out


# ----------------------------------------------------------------------------------------------------------- run 1
def bdeg(v):
    """The degree class of a births reading: 'degree j' for POWER(j) (any phase), 'ended', or the label."""
    if v is None:
        return 'none'
    if v['verdict'] == 'POWER':
        return 'degree %d' % v['j']
    if v['verdict'] == 'ENDED':
        return 'ended'
    if v['verdict'] == 'LINREC':
        return 'LINREC root %.3g' % v['root_modulus']
    return RD.label(v)


def parity_failing_starts():
    """The census starts failing the parity knot test at round 0 (KD 7.5: left out of parity shares)."""
    from knots import parity_test
    C = kwr.census()
    out = set()
    for i, x in enumerate(C):
        if x['n'] < 3:
            continue
        S = kwr.pm.from_stars(x['stars'])
        if parity_test(S)['fail']:
            out.add(i)
    return out


def shares(recs, pred, n_five, scratch, knot_law='nae', pfail=frozenset()):
    """KD 7.5's estimators: census (count among the small starts + (3157/n) x count among the n sampled five-knot
    starts) / 3376 (3344 under parity); labelled (the same with w_labelled); with the effective sample size."""
    C = kwr.census()
    f = 3157.0 / n_five if n_five else 0
    res = {}
    for name, excl in (('all', set()), ('without the 64', scratch)):
        cs = cf = ws = wf = wsa = wfa = 0.0
        w2 = 0.0
        ns = nf = 0
        for r in recs:
            i = r['index']
            if i in excl or (knot_law == 'parity' and i in pfail):
                continue
            w = C[i]['w_labelled']
            hit = bool(pred(r))
            if r['small']:
                ns += 1
                cs += hit
                ws += w * hit
                wsa += w
            else:
                nf += 1
                cf += hit
                wf += w * hit
                wfa += w
                w2 += w * w
        denom = (ns + f * nf)
        res[name] = {'census_share': (cs + f * cf) / denom if denom else None,
                     'labelled_share': (ws + f * wf) / (wsa + f * wfa) if (wsa + f * wfa) else None,
                     'count_small': int(cs), 'n_small': ns, 'count_five': int(cf), 'n_five': nf,
                     'effective_sample_size_labelled': (wfa ** 2 / w2) if w2 else None}
    return res


def run1():
    R = load('run1.jsonl.gz')
    if not R:
        return {}
    out = {'items': len(R)}
    by = defaultdict(dict)
    for r in R:
        by[r['law']][r['index']] = r
    five_done = sorted({r['index'] for r in R if not r['small']})
    order = kwr.five_order()['order'][:1000]
    pos = {i: k for k, i in enumerate(order)}
    # the prefix of the five-knot order present under every law (a cut run leaves a prefix)
    nf = 0
    laws_all = [l for l in ('L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L9', 'L10', 'L11') if l in by]
    for k, i in enumerate(order):
        if all(i in by[l] for l in laws_all):
            nf = k + 1
        else:
            break
    prefix = set(order[:nf])
    out['five_knot_prefix'] = nf
    scratch = kwr.scratch64()
    pfail = parity_failing_starts()
    out['parity_failing_starts_round0'] = len(pfail)
    lawrecs = {l: [r for r in by[l].values() if r['small'] or r['index'] in prefix] for l in by}
    # degree tables
    deg = {l: Counter(bdeg(r['births_reading']) for r in v) for l, v in lawrecs.items()}
    out['births_by_law'] = {l: dict(c) for l, c in deg.items()}
    # parity derived: a run with a closing round has ended there
    def pdeg(r):
        return 'ended' if r['parity_closing_round'] is not None else bdeg(r['births_reading'])
    out['births_by_law_parity'] = {l: dict(Counter(pdeg(r) for r in v if r['index'] not in pfail))
                                   for l, v in lawrecs.items()}
    # P1
    sh1 = shares(lawrecs.get('L6', []), lambda r: bdeg(r['births_reading']) == 'degree 1', nf, scratch)
    sh1p = shares(lawrecs.get('L6', []), lambda r: pdeg(r) == 'degree 1', nf, scratch, 'parity', pfail)
    v1 = sh1['all']['census_share']
    row('P1', 'holds' if v1 is not None and v1 >= 0.75 else 'fails',
        'L6, births of degree 1: census share %.3f (labelled %.3f; without the 64: %.3f); %d of %d small, %d of %d '
        'five-knot (prefix %d); parity derived %.3f' % (v1, sh1['all']['labelled_share'],
                                                        sh1['without the 64']['census_share'],
                                                        sh1['all']['count_small'], sh1['all']['n_small'],
                                                        sh1['all']['count_five'], sh1['all']['n_five'], nf,
                                                        sh1p['all']['census_share']))
    out['P1'] = {'nae': sh1, 'parity': sh1p}
    # P2
    def fast(r):
        v = r['births_reading']
        if v is None:
            return False
        if v['verdict'] == 'POWER' and v['j'] >= 2:
            return True
        if v['verdict'] == 'LINREC' and v['root_modulus'] > 1 + 1e-12:
            return True
        if v['verdict'] == 'RATIO' and v['x'] >= 1.25:
            return True
        return False
    p2 = {l: [(r['start'], bdeg(r['births_reading'])) for r in lawrecs.get(l, []) if fast(r)]
          for l in ('L1', 'L6', 'L7', 'L10', 'L11')}
    row('P2', 'holds' if not any(p2.values()) else 'fails', 'starts with births of degree >= 2, LINREC root > 1 or '
        'RATIO x >= 1.25 under L1, L6, L7, L10, L11: %s' % {l: len(v) for l, v in p2.items()})
    out['P2'] = {l: v[:40] for l, v in p2.items()}
    # P3
    d2 = [r['start'] for r in lawrecs.get('L9', []) if bdeg(r['births_reading']) == 'degree 2']
    sh3 = shares(lawrecs.get('L9', []), lambda r: bdeg(r['births_reading']) == 'degree 1', nf, scratch)
    v3 = sh3['all']['census_share']
    row('P3', 'holds' if d2 and v3 is not None and v3 >= 2 / 3 else 'fails', 'L9: %d starts with births of degree 2 '
        '(%s); births of degree 1: census share %.3f (labelled %.3f; without the 64: %.3f)'
        % (len(d2), ', '.join(d2[:6]), v3, sh3['all']['labelled_share'], sh3['without the 64']['census_share']))
    out['P3'] = {'degree_2': d2, 'shares_degree_1': sh3}
    # P4
    ok = tot = mult = 0
    gains = Counter()
    fail_list = []
    for r in lawrecs.get('L6', []):
        if r['rounds_done'] < 100 or r['stop'] not in (None,):
            if r['rounds_done'] < 100:
                continue
        pp = r['parts_per_round']
        ls = [x[0] if x else 0 for x in r['part_sizes_per_round']]
        if len(pp) <= 100:
            continue
        tot += 1
        same_parts = pp[36] == pp[40] and pp[96] == pp[100]
        g1 = [ls[t + 1] - ls[t] for t in range(36, 40)]
        g2 = [ls[t + 1] - ls[t] for t in range(96, 100)]
        const = len(set(g1)) == 1 and len(set(g2)) == 1
        if pp[100] > pp[40]:
            mult += 1
        if same_parts and const:
            ok += 1
            gains[(g1[0], g2[0])] += 1
        elif len(fail_list) < 30:
            fail_list.append({'start': r['start'], 'parts': [pp[36], pp[40], pp[96], pp[100]], 'gains': [g1, g2]})
    share4 = ok / tot if tot else None
    row('P4', 'holds' if share4 is not None and share4 >= 0.9 and mult == 0 else 'fails',
        'L6 runs to round 100: %d; same parts at 36/40 and 96/100 with a constant gain of the largest part over each '
        'span: %d (%.3f, unweighted runs); runs with more parts at 100 than at 40: %d; gains (36-40, 96-100): %s'
        % (tot, ok, share4 or 0, mult, dict(gains.most_common(6))))
    out['P4'] = {'runs': tot, 'ok': ok, 'parts_multiplying_after_40': mult, 'gains': {str(k): v for k, v in gains.items()},
                 'failing': fail_list}
    # the start-by-start table: births under L0 against L6, L7, L1, L9, L10, L11
    tab = {}
    for l in ('L6', 'L7', 'L1', 'L9', 'L10', 'L11'):
        c = Counter()
        for i, r0 in by.get('L0', {}).items():
            if not (r0['small'] or i in prefix):
                continue
            r = by.get(l, {}).get(i)
            if r is None:
                continue
            c[(bdeg(r0['births_reading']), bdeg(r['births_reading']))] += 1
        tab[l] = {'%s -> %s' % k: v for k, v in sorted(c.items())}
    out['table_L0_against'] = tab
    # H's verdicts and the screen
    hv = {}
    scr = {}
    for l, v in lawrecs.items():
        c = Counter()
        for r in v:
            for cl in ('a', 'b', 'c'):
                for u in r['classes'][cl]:
                    c[(cl, RD.label(r['reading'][str(u)]))] += 1
        hv[l] = {'%s: %s' % k: n for k, n in sorted(c.items())}
        scr[l] = dict(Counter(('holds j=%d' % r['screen']['j']) if r['screen'].get('holds') else
                              ('undecided (range)' if 'below' in str(r['screen'].get('reason')) else 'no j')
                              for r in v))
    out['H_verdicts'] = hv
    out['screen'] = scr
    # the same power 1 from every knot examined other than with constant births (registered question)
    p1runs = [(r['start'], l, bdeg(r['births_reading'])) for l, v in lawrecs.items() for r in v
              if r['screen'].get('holds') and r['screen']['j'] == 1 and bdeg(r['births_reading']) != 'degree 0']
    out['screen_power1_not_constant_births'] = p1runs[:50]
    out['screen_power1_not_constant_births_n'] = len(p1runs)
    out['parent_steps_differ_runs'] = sum(1 for v in lawrecs.values() for r in v if r['parent_steps_differ'])
    out['check_E_bad'] = sum(1 for v in lawrecs.values() for r in v if r['check_E'])
    out['shares_births'] = {l: {d: shares(v, (lambda dd: lambda r: bdeg(r['births_reading']) == dd)(d), nf, scratch)
                                ['all']['census_share'] for d in ('degree 0', 'degree 1', 'degree 2', 'ended')}
                            for l, v in lawrecs.items()}
    OUT['run1'] = out
    return out


def run5_swaps():
    R = load('run5_swaps.jsonl.gz')
    if not R:
        return {}
    prim = {}
    for lab in ('L0', 'L1', 'L3', 'L6', 'L7'):
        for r in load('run5_%s.jsonl.gz' % lab):
            if r['n'] in (3, 4):
                prim[(r['index'], lab)] = r
    out = {}
    for label in ('swap horizon 10', 'swap cap 40/60'):
        o = defaultdict(lambda: {'strata': Counter(), 'orders': defaultdict(lambda: [0, 0, 0]), 'stages': Counter(),
                                 'primary_strata': Counter(), 'primary_orders': defaultdict(lambda: [0, 0, 0]),
                                 'discordant_stages': Counter()})
        for r in R:
            if r['label'] != label:
                continue
            x = o[r['law']]
            for st in r['stages']:
                x['stages'][st['status']] += 1
                if st['status'] != 'computed':
                    continue
                for k, v in st['strata'].items():
                    x['strata'][k] += v
                for k, v in st.get('orders', {}).items():
                    if k in ('n', 'kappa_sign_by_ws'):
                        continue
                    for i in range(3):
                        x['orders'][k][i] += v[i]
                for lv in LEVELS:
                    if st.get('orders', {}).get('kappa|delta|%s' % lv, [0, 0, 0])[1]:
                        x['discordant_stages'][lv] += 1
            if label == 'swap horizon 10':
                p = prim.get((r['index'], r['law']))
                if p:
                    for st in p['stages']:
                        if st['status'] != 'computed':
                            continue
                        for k, v in st['strata'].items():
                            x['primary_strata'][k] += v
                        for k, v in st.get('orders', {}).items():
                            if k in ('n', 'kappa_sign_by_ws'):
                                continue
                            for i in range(3):
                                x['primary_orders'][k][i] += v[i]
        out[label] = {lab: {'strata': dict(v['strata']), 'stages': dict(v['stages']),
                            'kappa_delta': {lv: v['orders'].get('kappa|delta|%s' % lv) for lv in LEVELS},
                            'gamma_delta': {lv: v['orders'].get('gamma|delta|%s' % lv) for lv in LEVELS},
                            'primary_strata': dict(v['primary_strata']),
                            'primary_kappa_delta': {lv: v['primary_orders'].get('kappa|delta|%s' % lv) for lv in LEVELS},
                            'discordant_stages': dict(v['discordant_stages'])}
                        for lab, v in o.items()}
    OUT['run5_swaps'] = out
    return out


# ----------------------------------------------------------------------------------------------------------- run 4
def hubs_verdict(r):
    """Claim 3: held by hubs / held by hubs only under holder steps (the hubs make it so) / not held / ended."""
    rd = r['reads']
    if '100' not in rd or '50' not in rd:
        if r['ended'] is not None:
            return 'ended', None
        return 'undecided (round 100 not reached: %s)' % r['stop'], None
    k50, k100 = rd['50']['knots'], rd['100']['knots']
    rise = {st: max(b - a for a, b in zip(rd['50']['steps'][st], rd['100']['steps'][st]))
            for st in ('hs', 'ps', 'hs_two_holders', 'weighted')}
    ratio = k100 / k50
    nums = {'knots_50': k50, 'knots_100': k100, 'ratio': round(ratio, 3), 'rise': rise}
    if ratio >= 2 and rise['hs'] <= 2:
        if rise['hs_two_holders'] > 2 or rise['weighted'] > 2:
            return 'held by hubs only under holder steps (the hubs make it so)', nums
        return 'held by hubs', nums
    return 'not held', nums


def run4():
    R = [r for r in load('run4.jsonl.gz')]
    if not R:
        return {}
    out = {'runs': len(R)}
    verd = defaultdict(Counter)
    held = []
    ratios = []
    for r in R:
        v, nums = hubs_verdict(r)
        verd['%s %s' % (r['law'], r['knot_law'])][v] += 1
        if v.startswith('held'):
            held.append((r['start'], r['law'], r['knot_law'], r['seed'], v, nums))
        if nums:
            ratios.append((r['law'], nums['ratio'], nums['rise']['hs']))
    out['claim3'] = {k: dict(v) for k, v in verd.items()}
    out['held'] = held
    t18 = [h for h in held if h[1] in ('T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8')]
    kr = [x[1] for x in ratios if x[0] not in ('T9', 'T10')]
    rr = [x[2] for x in ratios if x[0] not in ('T9', 'T10')]
    row('P10', 'holds' if not t18 else 'fails', 'T1-T8 runs held by hubs: %d (of %d runs; %d reach round 100); knot '
        'ratio 100/50: min %.2f max %.2f; rise of the greatest holder steps 50 to 100: min %s max %s'
        % (len(t18), sum(1 for r in R if r['law'] not in ('T9', 'T10')), len(kr), min(kr) if kr else 0,
           max(kr) if kr else 0, min(rr) if rr else None, max(rr) if rr else None))
    # P11 and claim 4 (parity)
    tied = []
    lam_less = []
    lam_rank = Counter()
    for r in R:
        if r['knot_law'] != 'parity':
            continue
        for t, tr in r['tied'].items():
            if int(t) <= 10:
                for row_ in tr['rows']:
                    if all(row_['pass']):
                        tied.append((r['start'], r['law'], r['seed'], int(t), row_['knots'], row_['hs']))
        for t, L in r['lambda'].items():
            lam_rank[L['rank']] += 1
            if L['least_lt_loose']:
                lam_less.append((r['start'], r['law'], r['seed'], int(t), L['least'], L['rank'], L['loose'],
                                 r['knots_per_round'][int(t)]))
    row('P11', 'holds' if tied else 'fails', 'parity, rounds 1 to 10: tied pairs of loose distinctions at two knots '
        'both passing K1-K3: %d, in %d runs; holder steps between the two knots: %s'
        % (len(tied), len({(t[0], t[1], t[2]) for t in tied}), dict(Counter(t[5] for t in tied))))
    out['P11'] = tied[:100]
    lam_less.sort(key=lambda x: (x[7], x[3]))
    out['claim4'] = {'stages_by_rank': {str(k): v for k, v in sorted(lam_rank.items())},
                     'stages_with_a_rule_on_fewer_than_all_loose': len(lam_less),
                     'smallest': lam_less[:5]}
    cp = Counter()
    for r in R:
        cp['stages'] += r['check_P']['stages']
        cp['small_stages'] += r['check_P']['small_stages']
        cp['bad'] += r['check_P']['bad']
    out['check_P'] = dict(cp)
    kt = defaultdict(Counter)
    fails = []
    for r in R:
        k = r['knot_test']
        kt[r['knot_law']]['tested'] += k['tested']
        kt[r['knot_law']]['fails'] += len(k['fails'])
        kt[r['knot_law']]['untested'] += k['untested']
        kt[r['knot_law']]['disagree'] += k['disagree']
        for f in k['fails'][:3]:
            fails.append((r['start'], r['law'], r['knot_law'], r['seed'], f))
    out['knot_test'] = {k: dict(v) for k, v in kt.items()}
    out['knot_test_fails'] = fails[:200]
    hh = Counter()
    for r in R:
        if '100' in r['reads']:
            for m, c in r['reads']['100']['steps']['holders_hist'].items():
                hh[int(m)] += c
    out['holders_hist_round_100'] = {str(k): v for k, v in sorted(hh.items())}
    OUT['run4'] = out
    return out


def run4c():
    R = load('run4c.jsonl.gz')
    if not R:
        return {}
    groups = defaultdict(list)
    for r in R:
        groups[(r['start'], r['law'], r['choice'], r['knot_law'])].append(r)
    out = {'runs': len(R), 'groups': len(groups)}
    changed = Counter()
    changed_runs = Counter()
    verdicts = Counter()
    examples = []
    for g, rs in groups.items():
        rs.sort(key=lambda r: r['k'])
        base = hubs_verdict(rs[0])[0]
        diff = [r['numbering'] for r in rs[1:] if hubs_verdict(r)[0] != base]
        lab = g[1] if g[1] in ('T9', 'T10') else 'T1-T8 ' + g[2]
        changed[lab] += bool(diff)
        changed_runs[lab] += len(diff)
        for r in rs:
            verdicts[(lab, hubs_verdict(r)[0])] += 1
        if diff and len(examples) < 20:
            examples.append({'group': g, 'own_numbering_verdict': base, 'numberings_changing_it': len(diff),
                             'of': len(rs) - 1})
    out['groups_with_a_changed_verdict'] = dict(changed)
    out['numberings_changing_a_verdict'] = dict(changed_runs)
    out['groups_by_kind'] = dict(Counter(g[1] if g[1] in ('T9', 'T10') else 'T1-T8 ' + g[2] for g in groups))
    out['verdicts'] = {'%s: %s' % k: v for k, v in sorted(verdicts.items())}
    out['examples'] = examples
    out['held_by_hubs_any'] = sum(v for k, v in verdicts.items() if k[1].startswith('held'))
    OUT['run4c'] = out
    return out


# ----------------------------------------------------------------------------------------------------------- run 3
def run3():
    R = load('run3.jsonl.gz')
    if not R:
        return {}
    out = {'runs': len(R)}
    for kl in ('nae', 'parity'):
        c = Counter()
        fails = []
        for r in R:
            k = r[kl]
            c['tested'] += k['tested']
            c['untested'] += k.get('untested', 0)
            c['fails'] += len(k['fails'])
            c['disagree'] += k['disagree']
            c['runs'] += 1
            c['runs_with_fail'] += bool(k['fails'])
            for f in k['fails'][:3]:
                fails.append((r['source'], r['start'], r['law'], f))
        out[kl] = dict(c)
        out[kl + '_fails'] = fails[:200]
    OUT['run3'] = out
    return out


# ------------------------------------------------------------------------------------------------------ summary.md
def fmt_share(x):
    return 'n/a' if x is None else '%.3f' % x


def markdown(extra):
    L = []
    w = L.append
    w('# Knots within reach, and the growing end: summary of KNOTS-WITHIN-REACH-20261125-001A-E001')
    w('')
    w('Computed by an engine written from the frozen texts (SD, FD, KD, the claim and the pre-registration) by a helper '
      'that had not seen the drafter\'s prototype; the fold study\'s engine imported unchanged. Every count is a finite '
      'count of what a supplied law makes from a supplied start, read exactly in integers; nothing here is a claim '
      'about physical space. Readings taken where the texts leave a choice: `deviations.md` of the experiment folder. '
      'Raw records (the counts themselves): the `.jsonl.gz` files beside this summary.')
    w('')
    w('## Run 0: controls and checks')
    w('')
    w('| Control or check | Result |')
    w('| --- | --- |')
    for name, res in extra.get('run0', []):
        w('| %s | %s |' % (name, res))
    w('')
    w('## Predictions')
    w('')
    w('| Prediction | Verdict | The numbers behind it |')
    w('| --- | --- | --- |')
    for p, v, n in sorted(ROWS, key=lambda x: (int(''.join(c for c in x[0].split()[0][1:] if c.isdigit()) or 0), x[0])):
        w('| %s | %s | %s |' % (p, v, n.replace('|', '/')))
    w('')
    for title, body in extra.get('sections', []):
        w('## ' + title)
        w('')
        for line in body:
            w(line)
        w('')
    with open(kwr.out_path('summary.md'), 'w') as f:
        f.write('\n'.join(L) + '\n')


def run0_lines():
    out = []
    for name in ('tests', 'controls', 'checks', 'ktest'):
        pth = kwr.out_path('run0_%s.json' % name)
        if os.path.exists(pth):
            d = kwr.read_json(pth)
            for k, v in d['results'].items():
                if k.startswith('control 8') and 'whole kept range' in k:
                    res = ('reads as registered on [0, min(t, l)] from every made knot and exactly from every start knot; '
                           'the registered formula lacks the upper end r <= t, and beyond it the count is n(t + r + 1) '
                           '(half of the made knots of each ring): %s' % k.split('(')[-1].rstrip(')') + ' as registered')
                    out.append((k.split(':')[0] + ': made knots', res))
                else:
                    out.append((k, 'passed' if v['ok'] else 'FAILED'))
    pth = kwr.out_path('run0_probe.json')
    if os.path.exists(pth):
        d = kwr.read_json(pth)['probe_4b']
        pr = d['probe']
        out.append(('run 4b probe (Ring(5,3) under T1, 3 rounds, one numbering)',
                    '%d histories in %.0f s, not finished (over 10^5); at least %d s for its 80 numberings; all cases at '
                    'least %d s on one process; run 4b not run, Settled 3 "argued, unchecked"'
                    % (pr['histories'], pr['seconds'], pr['estimate_one_case_all_numberings_seconds_at_least'],
                       d['estimate_seconds_one_process_lower_bound'])))
    return out


def gate_cell(x):
    if x is None:
        return 'not reached'
    if x['holds']:
        sp = x['spread']
        return 'j=%d on %s, %d of %d; spread %.2f (start %.2f, made %.2f)' % (
            x['j'], x['range'], x['k'], x['K'], sp['all']['spread'], sp.get('start', {}).get('spread', 0),
            sp.get('made', {}).get('spread', 0))
    if 'below' in str(x.get('zmax')) or (x.get('zmax') is not None and x['zmax'] < 32):
        return 'least kept range %s' % x.get('zmax')
    kb = x.get('k_by_j_on_widest') or {}
    best = max(kb.items(), key=lambda kv: kv[1]) if kb else ('-', 0)
    return 'no gate (best j=%s: %s of %s)' % (best[0], best[1], x['K'])


def questions():
    b = []
    r1, r2, r4, r5 = OUT.get('run1'), OUT.get('run2'), OUT.get('run4'), OUT.get('run5')
    if r1:
        b.append('1. **The verdict of H and the degree of b(t)** (per law, run 1, on the 219 small starts and the first %d '
                 'five-knot starts; every knot counted from is in run1.jsonl.gz with its counts): births by reading %s. '
                 'H by class and reading: summary.json, run1.H_verdicts.' % (r1['five_knot_prefix'], r1['births_by_law']))
    if r2:
        a = r2['answers']
        b.append('2. **Run 2, gate and scaling:** both %d (all with j = 1: the seven bare rings at 264 and 528, '
                 'three-knot-larger, Ring(5, 2), Ring(7, 2), Ring(9, 2) under L0, L6, L7 at 66 and 132, census starts 1110 '
                 'and 3151 under L6; every one with constant births); gate only %d; no gate %d; undecided %d (least kept '
                 'range below 32, or T past the knot bound or guard). No run gives the same power of 2 or more from every '
                 'knot examined on a range that lengthens with the rounds.' % (a.get('both', 0), a.get('gate only', 0),
                                                                             a.get('no gate', 0), a.get('undecided', 0)))
    if r4:
        c = Counter()
        for k, v in r4['claim3'].items():
            for kk, n in v.items():
                c[kk] += n
        b.append('3. **Laws with a taking rule (T1 to T10):** %s; held by hubs in no run, under no step.' % dict(c))
        b.append('4. **Parity, Lambda_t:** yes; %d stages have a rule on fewer distinctions than their loose ones; the '
                 'smallest: %s.' % (r4['claim4']['stages_with_a_rule_on_fewer_than_all_loose'],
                                    r4['claim4']['smallest'][0]))
    if r5:
        lines = []
        for lab, o in r5.items():
            sm = o['smallest']
            f = lambda v: 'none' if not v else '%s r%d (%d knots, S = %d)' % (v['start'], v['round'], v['knots'],
                                                                               v['S'])
            ows = o.get('smallest_ws_hs', {})
            lines.append('%s: against delta, explained by loose counts %s; not loose counts %s; not loose or '
                         'shared-place counts %s; against ws (not loose counts) %s; against hs (not loose counts) %s; '
                         'L-W fails on %s of %s stages testing it (smallest %s); betweenness fails on %s of %s triples'
                         % (lab, f(sm.get('i-1')), f(sm.get('i-2')), f(sm.get('i-3')), f(ows.get('ws|i-2')),
                            f(ows.get('hs|i-2')), o['LW'].get('fails', 0), o['LW'].get('tests', 0),
                            (o.get('LW_smallest_fail') or {}).get('start'), o['btw'].get('failing', 0),
                            o['btw'].get('triples', 0)))
        b.append('5. **Not-all-equal, per law:** ' + '; '.join(lines) + '.')
    return b


def sections():
    S = [('The claim\'s questions', questions())]
    r2 = OUT.get('run2')
    if r2:
        body = ['Answers over the %d registered runs: %s. Checks over run 2: E failed on %d runs, R on %d, F on %d knots '
                '(of %d readings).' % (r2['registered_items'], r2['answers'], r2['checks']['E_bad_runs'],
                                       r2['checks']['R_bad_runs'], r2['checks']['F_bad_knots'], r2['checks']['F_runs']),
                '',
                'Does any run give the same power of 2 or more from every knot examined on a range that lengthens with '
                'the rounds? **No** under the registered thresholds (%d runs). Under the swapped thresholds (z >= 4a, '
                'C/c <= 3, 1.5): %s.' % (len(r2['P5']['both_j_ge_2']), r2['swap_thresholds_answers']),
                'Gates that hold at 2T but not at T (answer "no gate" by the registered rule): %d.' % len(
                    r2['gate_at_2T_only']),
                '', '| Start | Law | Answer | Gate at T | Gate at 2T | P at T (labels) |', '| --- | --- | --- | --- | --- | --- |']
        for e in r2['table']:
            P = (e['T'] or {}).get('P') or {}
            labs = dict(Counter(P.get('labels', [])))
            body.append('| %s | %s (T=%s) | %s | %s | %s | %s |' % (e['start'], e['law'], e['T_rounds'], e['answer'],
                                                                 gate_cell(e['T']), gate_cell(e['2T']), labs))
        S.append(('Run 2: the gate', body))
        b2 = ['P beside the gate (members counted from, at T and 2T; L6, L7 and the L1 supplement): %s; with L1: %s.'
              % (OUT['run2']['P9']['labels_L6_L7'], OUT['run2']['P9']['labels_with_L1']),
              'Swaps of run 2: %s.' % json.dumps(r2['swaps'])]
        S.append(('Run 2: the roster count and the swaps', b2))
    r1 = OUT.get('run1')
    if r1:
        b = ['Cut to a prefix fixed before the run (deviations 29): the 219 three- and four-knot starts under all 12 laws '
             'and the first %d five-knot starts of the registered order under 11 laws; the other %d five-knot starts are '
             'not run. Shares use KD 7.5\'s estimators with 3,157/%d.' % (r1['five_knot_prefix'],
                                                                         1000 - r1['five_knot_prefix'],
                                                                         r1['five_knot_prefix']),
             '', '| Law | Births per round, by reading (starts, unweighted) | Census shares (degree 0, 1, 2, ended) |',
             '| --- | --- | --- |']
        for lab in ('L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8', 'L9', 'L10', 'L11'):
            if lab in r1['births_by_law']:
                shs = r1['shares_births'].get(lab, {})
                b.append('| %s | %s | %s |' % (lab, r1['births_by_law'][lab],
                                               ', '.join(fmt_share(shs.get(d)) for d in ('degree 0', 'degree 1',
                                                                                         'degree 2', 'ended'))))
        b += ['', 'Under parity (derived, Settled 4; the %d starts failing the knot test at round 0 left out): %s.'
              % (r1['parity_failing_starts_round0'], r1['births_by_law_parity']),
              '', 'The start-by-start table (births under L0 -> under the law; L9, L10, L11 separate the cap from the '
              'treatment):', '']
        for lab, t in r1['table_L0_against'].items():
            b.append('- %s: %s' % (lab, t))
        b += ['', 'The screen (the same j from every start knot and 16 made knots at the last round, no scaling): %s.'
              % r1['screen'],
              'Runs whose screen gives the same power 1 from every knot examined with births not constant: %d.'
              % r1['screen_power1_not_constant_births_n'],
              'H from the knots counted from, by class and reading: see summary.json (run1.H_verdicts).',
              'Check E failed on %d runs; parent steps change H on %d runs (only through the start\'s own meetings, '
              'Lemma E).' % (r1['check_E_bad'], r1['parent_steps_differ_runs'])]
        S.append(('Run 1: the screen and the start-by-start table', b))
    r4 = OUT.get('run4')
    if r4:
        b = ['Claim 3 by law and knot law (runs): %s.' % r4['claim3'],
             'Held by hubs: %d runs. Claim 4 (parity): stages by rank of Lambda_t %s; stages with a rule on fewer '
             'distinctions than all loose ones: %d; the smallest: %s (start, law, seed, round, least number of '
             'distinctions in one rule, rank, loose distinctions, knots).' % (len(r4['held']),
                                                                              r4['claim4']['stages_by_rank'],
                                                                              r4['claim4']['stages_with_a_rule_on_fewer_than_all_loose'],
                                                                              r4['claim4']['smallest'][:2]),
             'Check P: %s. Knot test (every knot after round 25 and 100 later knots): %s; failing knots are listed '
             'in summary.json (run4.knot_test_fails): joins of many parents under CARRY among them.'
             % (r4['check_P'], r4['knot_test']),
             'Holder-number distribution at round 100 (all runs reaching it): %s.' % r4['holders_hist_round_100']]
        r4c = OUT.get('run4c')
        if r4c:
            b.append('Run 4c (OLDEST and NEWEST under KD 7.3\'s numberings; T1-T8 with 10 numberings since no run is '
                     'held by hubs, T9 and T10 with all 4n): %d runs in %d groups; groups whose claim-3 verdict changes '
                     'with the numbering: %s (numberings changing it: %s); held by hubs under any numbering: %d.'
                     % (r4c['runs'], r4c['groups'], r4c['groups_with_a_changed_verdict'],
                        r4c['numberings_changing_a_verdict'], r4c['held_by_hubs_any']))
        S.append(('Run 4: laws with a taking rule', b))
    r5 = OUT.get('run5')
    if r5:
        b = ['| Law | Stages computed / not run (cap) | Strata (i, ii, iii, iv, v, vi) | |kappa| vs delta (i-1; i-2; '
             'i-3: conc, disc, tied) | |gamma| vs delta (i-1) | Smallest stage: not loose counts; not loose or '
             'shared-place counts |', '| --- | --- | --- | --- | --- | --- |']
        for lab, o in r5.items():
            st = o['strata']
            sm = o['smallest']

            def sml(v):
                return 'none' if not v else '%s r%d (%d knots, %d distinctions, S = %d)' % (
                    v['start'], v['round'], v['knots'], v['distinctions'], v['S'])
            b.append('| %s | %s / %s | %s | %s; %s; %s | %s | %s; %s |' % (
                lab, o['stages'].get('computed', 0), o['stages'].get('not run (stage cap)', 0),
                ', '.join(str(st.get(k, 0)) for k in ('i', 'ii', 'iii', 'iv', 'v', 'vi')),
                o['orders'].get('kappa|delta|i-1'), o['orders'].get('kappa|delta|i-2'),
                o['orders'].get('kappa|delta|i-3'), o['orders'].get('gamma|delta|i-1'), sml(sm.get('i-2')),
                sml(sm.get('i-3'))))
        b += ['']
        for lab, o in r5.items():
            b.append('- %s: against ws %s, against hs %s (|kappa|, i-1/i-2/i-3); rho vs delta %s; S: %s; L-W %s; '
                     'betweenness %s; history weighting on %d stages of at most 20 distinctions: discordant under the '
                     'stage weighting %s, under the history weighting %s, history only %s, stage only %s; checks on '
                     'those stages %s; knot test %s; sign of kappa at each ws %s; shares of stages with a discordance '
                     '(census, labelled) %s.' % (
                         lab, [o['orders'].get('kappa|ws|%s' % lv) for lv in LEVELS],
                         [o['orders'].get('kappa|hs|%s' % lv) for lv in LEVELS],
                         [o['orders'].get('rho|delta|%s' % lv) for lv in LEVELS],
                         {k: {'S': v['S'], 'member shuffle mean': round(v['mean'], 1),
                              'z member': round(v['z_member'] or 0, 1), 'z pair': round(v['z_pair'] or 0, 1),
                              'stages': v['stages'], 'exact': v['exact_stages']} for k, v in o['S'].items()},
                         o['LW'], o['btw'], o['history']['stages'], o['history']['disc_stage'],
                         o['history']['disc_hist'], o['history']['hist_only'], o['history']['stage_only'], o['small'],
                         o['knot_test'], o['kappa_sign_by_ws'],
                         {k: (round(v['census'], 4), round(v['labelled'], 4)) for k, v in o['discordant_stage_share'].items()
                          if k.startswith('kappa|delta')}))
        sw = OUT.get('run5_swaps')
        if sw:
            b += ['', 'Swaps on the three- and four-knot starts:']
            for label, d in sw.items():
                for lab, x in d.items():
                    b.append('- %s, %s: stages %s; strata %s; |kappa| vs delta %s; discordant stages by level %s.'
                             % (label, lab, x['stages'], x['strata'], x['kappa_delta'], x['discordant_stages']))
        S.append(('Run 5: the growing end (not-all-equal)', b))
    r3 = OUT.get('run3')
    if r3:
        b = ['Cut to a prefix fixed before the run (deviations 33): run 2\'s 235 registered runs and run 1\'s runs of '
             'the first 100 three- and four-knot starts.']
        for kl in ('nae', 'parity'):
            x = r3[kl]
            n = x['tested']
            b.append('- %s: %d of %d knots tested %s; a failing share above %.2g is excluded at 95%% %s; untested '
                     'knots are not tested and rest on the argued statement. Runs: %d; runs with a failing knot: %d; '
                     'methods disagreeing: %d.' % (kl, n - x['fails'], n, 'passed' if not x['fails'] else
                                                   '(%d failed)' % x['fails'], 3.0 / n if n else 0,
                                                   '' if not x['fails'] else '(not applicable: failures found)',
                                                   x['runs'], x['runs_with_fail'], x['disagree']))
        S.append(('Run 3: the knot test of runs 1 and 2', b))
    S.append(('Differences from the numbers disclosed in the pre-registration', DIFFS))
    S.append(('Sizes run against sizes registered, and wall times', SIZES))
    S.append(('Readings and texts found short', [
        'Every reading taken is a numbered item of `deviations.md` in the experiment folder, written before the run it '
        'affects. Frozen texts found short: KD 8.8 lacks the upper end r <= t for made knots (item 17); P6\'s clause on '
        '[4, n - 1] fails by arithmetic for small n under either reading (reported under both); P9 names L1, which run 2 '
        'does not run (supplement, items 20 and 25); KD 5.8 gives no stratum to pairs in different parts of a roster not '
        'past its start (a sixth stratum, item 21); the member shuffle\'s "every permutation" with several parts '
        '(item 16).']))
    return S


DIFFS = [
    '- **Known 1, L8 from one knot:** POWER(3) on [0, 65], not [0, 64]: the run stops after round 65 with 50,116 knots '
    '(the knot bound read as the fold engine\'s, deviations 2); the verdict is the same.',
    '- **Known 2, Ring(33, 2):** the gate, its ranges [16, 132] and [16, 264], 161 knots, spreads 2.02 and 2.02 and start '
    'knots 1.02 and 1.03 replicate; the made knots\' own spread is 2.00 at 264 rounds and 2.02 at 528 (disclosed 2.02). '
    '"On [4, 32] the made knots alone read j = 2 (spread within 2)" does not hold for every made knot examined: 23 of '
    '128 at 66 rounds, 11 of 128 at 132, 5 of 128 at 264 and 528 lie outside a factor 2, all made knots of early rounds '
    'whose count reaches the start after t holder steps (KD 8.8\'s missing upper end); listing '
    '`listing_run2_bare_ring_made_knots.json`. The start knot\'s own C/c on [4, 32], 2.41, replicates. Two-share under L0: '
    'no gate at 66 or 132, as disclosed; its start knots alone read j = 2 on their own wider ranges [4, 66] and [4, 132].',
    '- **Known 3:** the table on the 64 starts at 40 rounds and its start-by-start statements replicate exactly '
    '(`check_known3.json`; its "census 3103 and 3192" are positions in the 3,376, file indices 3107 and 3196). The '
    'registered run 1 (100 rounds, the 219 small starts and a prefix of 250 five-knot starts) is a different set.',
    '- **Known 6, the growing end:** the disclosed census (208 small starts and 8 named starts, rounds 1 to 3, an '
    'elimination-width cap) is not run 5\'s set. On run 5\'s 219 small starts, rounds 1 to 3: under L0 14,146 '
    'discordant comparisons under |kappa| against delta, 146 of 10,240 untied at equal loose counts (1.4 percent; '
    'disclosed 17,448 and 201 of 13,896, 1.4 percent); under |gamma| 4,224 of 40,206 untied (10.5 percent; disclosed 9.2). '
    'L1: 1,227 under |kappa|, 717 under |gamma|, 329 at equal counts (disclosed 1,570, 963, 443); L6: 923, 516, 133 '
    '(disclosed 1,051, 606, 165). Strata (i) 5,898, 4,839, 4,731, 1,131 and (ii) 1,996, 9,227, 5,680, 10,157 for L0, '
    'L1, L6, L3 (disclosed 6,872, 5,473, 5,092, 1,102 and 2,342, 11,880, 6,684, 10,153). L3\'s 1,224 comparisons, all '
    'tied in delta, replicate exactly (P14).',
    '- **Known 7:** replicates exactly (census start 157 after round 1: 38,178 allowed states, kappa -1/2121, -1/707, '
    '19/19089, S = 0; census start 133 under L1: |kappa| 1/27 at delta 2 against 4/243 at delta 1).',
    '- **Known 10, taking rules at 100 rounds:** not reproduced by the registered seeds. Ring(5, 3) under T2 (MET on '
    'CAP-3(RETIRE)): under parity both seeds stop (rounds 47 and 72, 77 and 81 knots); under not-all-equal 296, 421, 671 '
    'and 66, 91, 141 knots at rounds 25, 50, 100 (disclosed 514, 1,575, 3,389, greatest holder steps 8, 14, 17; mine 7, '
    '9, 11). Ring(7, 3) under T4: 218, 393, 743 knots, steps 10, 13, 22 (seed 1, not-all-equal; disclosed 228, 378, 678, '
    '9, 14, 21). Three-knot under T4, seed 1, not-all-equal: 125, 250, 500 knots, steps 23, 48, 98 (as disclosed). The '
    'drafter\'s seeds and knot law for these runs are not stated; the verdicts (not held by hubs) agree.',
    '- **Known 11:** 3,376 starts, 32 failing the parity knot test at round 0 (3 of four knots, 29 of five) replicate; '
    'the small starts of degree 2 or more under L0 replicate (run2_small_recomputed.json).',
    '- **Known 12:** the golden-ratio eddy (Ring(5, 3) under L0) does not pass 50,000 knots after round 17: the registered '
    'guard (more than 200,000 joinable pairs in the demand roster) stops it after round 15 at 20,895 knots (deviations '
    '27); its run 2 answer is "undecided" either way.',
]

SIZES = [
    '- Run 0: as registered; the run 4b probe over its cap (run 4b not run; Settled 3 "argued, unchecked").',
    '- Run 2: as registered (235 runs, 470 gates) with the swaps and the P9 supplement; 12 min on 4 processes.',
    '- Run 5: as registered (3,376 starts x 5 laws) with both swaps on the small starts; 21 min and 4 min.',
    '- Run 1: cut (deviations 29) to the 219 small starts and the first 250 of the 1,000 five-knot starts; 36 min.',
    '- Run 4: as registered (8,496 runs and 944 base-law runs); 11 min and 6 min.',
    '- Run 3: cut (deviations 33) to run 2\'s 235 runs and run 1\'s runs of the first 100 small starts (1,435 of '
    '2,863 runs); the direct comparison on sampled knots of at most 6 places (deviations 31); 18 min on 4 processes, '
    'stopped and resumed on 6 processes for 17 min more (deviations 34).',
    '- Run 4b: not run (the probe). Run 4c: run with 10 numberings for T1-T8 (no run held by hubs) and all 4n for T9, '
    'T10; 2 min on 2 processes.',
]


def main():
    if os.path.exists(kwr.out_path('run4.jsonl.gz')):
        run4()
    if os.path.exists(kwr.out_path('run4c.jsonl.gz')):
        run4c()
    if os.path.exists(kwr.out_path('run3.jsonl.gz')):
        run3()
    if os.path.exists(kwr.out_path('run1.jsonl.gz')):
        run1()
    if os.path.exists(kwr.out_path('run2.jsonl.gz')):
        run2()
    if os.path.exists(kwr.out_path('run5_L0.jsonl.gz')):
        run5()
    if os.path.exists(kwr.out_path('run5_swaps.jsonl.gz')):
        run5_swaps()
    kwr.write_json(kwr.out_path('summary.json'), {'runs': OUT, 'predictions': [{'prediction': p, 'verdict': v,
                                                                                 'numbers': n} for p, v, n in ROWS]})
    markdown({'run0': run0_lines(), 'sections': sections()})
    for p, v, n in ROWS:
        print('%-40s %-8s %s' % (p, v, n[:400]))


if __name__ == '__main__':
    main()
