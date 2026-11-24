"""Verdicts for the Gate and P1-P12, the holding table, and the reports of run 6.

    python -B gch_summarize.py      # reads gate.json, knot_test.json and runs/*.json; writes summary.json,
                                    # summary.md and listings/*.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gch_configs as K  # noqa: E402
from gch_run import OUT as RUNS, slug  # noqa: E402

ART = RUNS.parent
LIST = ART / 'listings'


def load(cid):
    p = RUNS / (slug(cid) + '.json')
    return json.loads(p.read_text()) if p.exists() else None


def rid(fam, start, r, g):
    return '%s-%s__r%d__%s' % (K.FAMILY_NAMES[fam], start, r, g.replace("'", 'P'))


def facts(x):
    if x is None:
        return None
    eo = x['every_order']
    o = eo.get('orders', {})
    sm, xl = x['sampled']['counts'], x['xlast']['counts']
    f = {'every_finished': eo.get('finished'), 'every_least': eo.get('least_n'), 'keys': eo.get('keys'),
         'depth': eo.get('searched_to_births'), 'every_match': int(o.get('match', '0')),
         'every_mismatch': int(o.get('mismatch', '0')), 'every_underbuild': int(o.get('underbuild', '0')),
         'sampled': sm, 'xlast': xl, 'births_within_r': x['reference']['births_within_r'], 'R': x['reference']['R']}
    f['any_mismatch'] = f['every_least'] is not None or sm['mismatch'] > 0 or xl['mismatch'] > 0
    f['any_underbuild'] = f['every_underbuild'] > 0 or sm['underbuild'] > 0 or xl['underbuild'] > 0
    f['any_match'] = f['every_match'] > 0 or sm['match'] > 0 or xl['match'] > 0
    ld = x.get('least_differing_order')
    f['least'] = ld['births'] if ld else None
    f['least_exact'] = bool(ld and ld.get('exact'))
    if f['any_mismatch']:
        f['outcome'] = 'mismatch'
    elif f['any_underbuild'] and not f['any_match']:
        f['outcome'] = 'underbuild'
    elif f['any_underbuild']:
        f['outcome'] = 'match and underbuild'
    else:
        f['outcome'] = 'match'
    return f


def line(x):
    f = facts(x)
    if f is None:
        return 'not run'
    s = f['outcome']
    if f['least'] is not None:
        s += ', least %d%s' % (f['least'], '' if f['least_exact'] else ' found')
    if f['every_finished']:
        s += '; every order finished (%s keys, %d births)' % (format(f['keys'], ','), f['depth'])
    else:
        s += '; every order to %d births (cap, %s keys)' % (f['depth'], format(f['keys'], ','))
    s += '; sampled %d/%d/%d, x-last %d/%d/%d (match/mismatch/underbuild)' % (
        f['sampled']['match'], f['sampled']['mismatch'], f['sampled']['underbuild'],
        f['xlast']['match'], f['xlast']['mismatch'], f['xlast']['underbuild'])
    return s


def first_never_made(x):
    """The first reference knot never made, and why, over every underbuilding order of a run."""
    if x is None:
        return None
    out = {}
    for k, n in x['every_order'].get('underbuild_reasons', {}).items():
        out[k] = out.get(k, 0) + n
    for kind in ('sampled', 'xlast'):
        for k, n in x[kind].get('underbuild_reasons', {}).items():
            out['%s (%s orders)' % (k, kind)] = n
    ex = x.get('underbuild_example')
    return {'reasons': out, 'example': ex}


def write_listing(name, x, extra=None):
    name = name.replace("'", 'P')          # R3' is written R3P in file names
    LIST.mkdir(parents=True, exist_ok=True)
    rec = {'run': x['id'] if x else None, 'least_differing_order': x.get('least_differing_order') if x else None}
    if extra:
        rec.update(extra)
    (LIST / (slug(name) + '.json')).write_text(json.dumps(rec, indent=1, default=str) + '\n')
    return 'listings/%s.json' % slug(name)


# ============================================================================== verdicts

def verdicts():
    V = {}
    gate = json.loads((ART / 'gate.json').read_text())
    V['Gate'] = {
        'verdict': ('holds' if gate['pass'] else
                    'fails on D under (RATION-3, CANCEL-WAIT, HOLD), as GCH section 1 foresees under holding; holds in '
                    'every other respect (structure, f, usable and barred counts, stayers) and under every other law'
                    if gate['pass_without_D'] and gate['D_differences_explained'] else 'fails'),
        'pairs': gate['n_pairs'], 'rounds_compared': gate['n_rounds_compared'],
        'pass_with_D': gate['pass'], 'pass_without_D': gate['pass_without_D'],
        'pairs_where_D_differs': gate['pairs_where_D_differs'],
        'D_differences_explained_by_groups_with_an_old_member': gate['D_differences_explained'],
        'controls': gate['controls'],
        'start_clause_violations': [s for s in gate['start_clause'] if s['violations']],
        'start_clause_checked': len(gate['start_clause'])}

    # P1, P5: R3 under the cap (with and without fillers)
    for P, fam in (('P1', K.CAP3W), ('P5', K.CAP3WF)):
        rows, bad, unf = {}, [], []
        for start in K.CAP_STARTS:
            x1, x3 = load(rid(fam, start, 1, 'R3')), load(rid(fam, start, 3, 'R3'))
            f1, f3 = facts(x1), facts(x3)
            rows['%s r1' % start] = line(x1)
            rows['%s r3' % start] = line(x3)
            if f1 is None or f1['any_mismatch'] or f1['any_underbuild']:
                bad.append('%s r1' % start)
            if f1 and not f1['every_finished']:
                unf.append('%s r1' % start)
            if f3 is None or f3['sampled']['mismatch'] + f3['sampled']['underbuild'] + f3['xlast']['mismatch'] + \
                    f3['xlast']['underbuild'] > 0:
                bad.append('%s r3 sampled/x-last' % start)
            if f3 and (f3['every_least'] is not None or f3['every_underbuild']):
                bad.append('%s r3 every order' % start)
        V[P] = {'verdict': 'fails' if bad else 'holds', 'fails_on': bad,
                'every_order_unfinished_at_round_1': unf, 'numbers': rows}

    # P2: R1 under the cap
    rows, bad = {}, []
    for start in ('D2(4,3)', 'D2(5,3)', 'Ring(5,3)'):
        x = load(rid(K.CAP3W, start, 1, 'R1'))
        f = facts(x)
        ws = x.get('least_mismatches_waiter_surplus', []) if x else []
        rows[start] = {'least': f['least'] if f else None, 'exact': f['least_exact'] if f else None,
                       'all_least_mismatches_waiter_surplus': bool(ws) and all(ws), 'line': line(x),
                       'r3': line(load(rid(K.CAP3W, start, 3, 'R1')))}
        if not f or f['least'] != 7 or not f['least_exact'] or not (ws and all(ws)):
            bad.append(start)
    for start in ('TWO-KNOT', 'THREE-KNOT'):
        for r in (1, 3):
            x = load(rid(K.CAP3W, start, r, 'R1'))
            f = facts(x)
            rows['%s r%d' % (start, r)] = line(x)
            if f is None or f['any_mismatch'] or f['any_underbuild']:
                bad.append('%s r%d' % (start, r))
    V['P2'] = {'verdict': 'fails' if bad else 'holds', 'fails_on': bad, 'numbers': rows}

    # P3: R2 under the cap
    rows, bad = {}, []
    for start in ('D2(4,3)', 'D2(5,3)', 'Ring(5,3)'):
        x = load(rid(K.CAP3W, start, 1, 'R2'))
        f = facts(x)
        rows[start] = line(x)
        if f is None or f['any_mismatch'] or f['any_underbuild']:
            bad.append(start)
    x = load(rid(K.CAP3W, 'C8X3', 1, 'R2'))
    f = facts(x)
    rows['C8X3'] = line(x)
    rows['C8X3 r3'] = line(load(rid(K.CAP3W, 'C8X3', 3, 'R2')))
    if f is None or not f['any_mismatch']:
        bad.append('C8X3 (matches)')
    V['P3'] = {'verdict': 'fails' if bad else 'holds', 'fails_on': bad, 'numbers': rows,
               'least_on_C8X3': f['least'] if f else None, 'least_exact': f['least_exact'] if f else None}
    if x and x.get('least_differing_order'):
        V['P3']['C8X3_listing'] = write_listing('P3 C8X3 R2 under the cap, least differing order', x)

    # P4: T(d)
    td = {}
    for start in K.TD_STARTS:
        per, least = {}, {'every': None, 'sampled': None, 'xlast': None, 'all kinds': None}
        for d in K.TD_DS:
            x = load('TD-%s__r1__T(%d)' % (start, d))
            f = facts(x)
            per[d] = line(x)
            if f is None:
                continue
            nomm = {'every': f['every_least'] is None, 'sampled': f['sampled']['mismatch'] == 0,
                    'xlast': f['xlast']['mismatch'] == 0}
            nomm['all kinds'] = all(nomm.values()) and not f['any_underbuild']
            for k, v in nomm.items():
                if v and least[k] is None:
                    least[k] = d
        td[start] = {'least_d_with_no_mismatch': least, 'per_d': per}
    V['P4'] = {'verdict': 'holds' if td['D2(6,3)']['least_d_with_no_mismatch']['all kinds'] == 4 else 'fails',
               'D2(4,3)_check': td['D2(4,3)']['least_d_with_no_mismatch']['all kinds'] == 4, 'numbers': td}

    # P6: R1, R2, R3 under (RATION-3, CANCEL-WAIT, HOLD) on D2(4,3), Ring(5,3)
    rows, bad = {}, []
    for start in ('D2(4,3)', 'Ring(5,3)'):
        for g in ('R1', 'R2', 'R3'):
            x1, x2 = load(rid(K.R3H, start, 1, g)), load(rid(K.R3H, start, 2, g))
            f1, f2 = facts(x1), facts(x2)
            fn = first_never_made(x2)
            rows['%s %s' % (start, g)] = {'r1': line(x1), 'r2': line(x2), 'r2_first_never_made': fn}
            if f1 is None or f1['any_mismatch'] or f1['any_underbuild']:
                bad.append('%s %s r1' % (start, g))
            if f2 is None or f2['any_match'] or f2['any_mismatch'] or not f2['any_underbuild']:
                bad.append('%s %s r2' % (start, g))
    V['P6'] = {'verdict': 'fails' if bad else 'holds (a check)', 'fails_on': bad, 'numbers': rows}

    # P7: R3' under (RATION-3, CANCEL-WAIT, HOLD)
    rows, bad = {}, []
    for start, want in (('D2(4,3)', 13), ('Ring(5,3)', 15)):
        xs = {r: load(rid(K.R3H, start, r, "R3'")) for r in (1, 2, 3)}
        fs = {r: facts(v) for r, v in xs.items()}
        rows[start] = {'r%d' % r: line(v) for r, v in xs.items()}
        for r in (1, 2):
            if fs[r] is None or fs[r]['any_mismatch'] or fs[r]['any_underbuild']:
                bad.append('%s r%d differs' % (start, r))
        f3 = fs[3]
        if f3 is None or not f3['any_mismatch']:
            bad.append('%s r3 matches' % start)
        elif f3['least'] != want or not f3['least_exact']:
            bad.append('%s r3 least %s (exact %s), predicted %d' % (start, f3['least'], f3['least_exact'], want))
        if xs[3] is not None:
            rows[start]['r3_listing'] = write_listing("P7 R3' %s through round 3" % start, xs[3])
    V['P7'] = {'verdict': 'fails' if bad else 'holds', 'fails_on': bad, 'numbers': rows}

    # P8: the cap with holding
    rows, bad = {}, []
    for start in ('D2(4,3)', 'Ring(5,3)'):
        for g in ('R1', 'R2', 'R3', "R3'"):
            for r in (1, 2, 3):
                x = load(rid(K.CAP3H, start, r, g))
                f = facts(x)
                rows['%s %s r%d' % (start, g, r)] = line(x)
                if f is None or f['any_mismatch'] or f['any_underbuild']:
                    bad.append('%s %s r%d' % (start, g, r))
    eq = {}
    for start in ('TWO-KNOT', 'THREE-KNOT'):
        for g in ('R1', 'R2', 'R3', 'CONTROL'):
            for r in (1, 3):
                a, b = load(rid(K.CAP3H, start, r, g)), load(rid(K.CAP3W, start, r, g))
                fa, fb = facts(a), facts(b)
                same = fa is not None and fb is not None and all(
                    fa[k] == fb[k] for k in ('keys', 'every_match', 'every_mismatch', 'every_underbuild', 'sampled',
                                             'xlast', 'every_least'))
                eq['%s %s r%d' % (start, g, r)] = same
                if not same:
                    bad.append('%s %s r%d differs from RELEASE' % (start, g, r))
        for r in (2, 4):
            for g in ('R1', 'R2', 'R3', "R3'"):
                x = load(rid(K.CAP3H, start, r, g))
                f = facts(x)
                rows['%s %s r%d' % (start, g, r)] = line(x)
                if f is None or f['any_mismatch'] or f['any_underbuild']:
                    bad.append('%s %s r%d' % (start, g, r))
    V['P8'] = {'verdict': 'fails' if bad else 'holds (a check)', 'fails_on': bad, 'numbers': rows,
               'small_starts_equal_to_RELEASE': eq}

    # P9: two-knot under (FLOOR1, CANCEL-RETIRE, HOLD) and (FLOOR1, CANCEL-OFFSHOOT, HOLD)
    rows, bad = {}, []
    for fam in (K.F1RH, K.F1OH):
        fn = K.FAMILY_NAMES[fam]
        for g in ('R1', 'R2', 'R3', "R3'"):
            for r in (1, 2, 3, 4):
                x = load(rid(fam, 'TWO-KNOT', r, g))
                rows['%s %s r%d' % (fn, g, r)] = {'line': line(x), 'first_never_made': first_never_made(x)
                                                  if facts(x) and facts(x)['any_underbuild'] else None}
        f3 = facts(load(rid(fam, 'TWO-KNOT', 3, 'R3')))
        if f3 is None or (not f3['any_mismatch'] and not f3['any_underbuild']):
            bad.append('%s: R3 matches through round 3' % fn)
        f4 = facts(load(rid(fam, 'TWO-KNOT', 4, "R3'")))
        if f4 is None or not f4['any_mismatch']:
            bad.append("%s: R3' matches through round 4" % fn)
        x4 = load(rid(fam, 'TWO-KNOT', 4, "R3'"))
        if x4 is not None:
            rows['%s R3P r4 listing' % fn] = write_listing("P9 R3' two-knot %s through round 4" % fn, x4)
        # the other parts of the hand prediction, reported
        parts = {}
        for g in ('R1', 'R2', 'R3'):
            for r in (1, 2):
                f = facts(load(rid(fam, 'TWO-KNOT', r, g)))
                parts['%s r%d matches' % (g, r)] = bool(f) and f['outcome'] == 'match'
            f = facts(load(rid(fam, 'TWO-KNOT', 3, g)))
            parts['%s r3 underbuilds' % g] = bool(f) and f['outcome'] == 'underbuild'
        rows['%s parts of the hand prediction' % fn] = parts
    V['P9'] = {'verdict': 'fails' if bad else 'holds', 'fails_on': bad, 'numbers': rows}

    # P10: D2(4,3) under (FLOOR1, CANCEL-OFFSHOOT, HOLD)
    rows, bad = {}, []
    for g in ('R3', "R3'"):
        for r in (1, 2, 3):
            x = load(rid(K.F1OH, 'D2(4,3)', r, g))
            f = facts(x)
            rows['%s r%d' % (g, r)] = line(x)
            if f is None or f['any_mismatch'] or f['any_underbuild']:
                bad.append('%s r%d' % (g, r))
                if x is not None:
                    rows['%s r%d listing' % (g, r)] = write_listing('P10 %s D2(4,3) F1OH r%d' % (g, r), x,
                                                                    {'underbuild_example': x.get('underbuild_example')})
    V['P10'] = {'verdict': 'fails' if bad else 'holds', 'fails_on': bad, 'numbers': rows}

    # P11 and P12: reported
    p11 = {}
    for fam in K.HOLD_LAWS:
        for start, cuts in K.HOLD_STARTS.items():
            for g in ('R1', 'R2', 'R3', "R3'"):
                for r in cuts:
                    p11['%s %s %s r%d' % (K.FAMILY_NAMES[fam], start, g, r)] = line(load(rid(fam, start, r, g)))
    V['P11'] = {'verdict': 'open (reported)', 'numbers': p11}
    p12 = {}
    for cid, start, fam, r, g in K.configs():
        if g == 'CONTROL':
            p12[cid] = line(load(cid))
    V['P12'] = {'verdict': 'open (reported)', 'numbers': p12}
    return V


def holding_table():
    """For each holding law, start and cutoff: R1, R2, R3, R3' and the control."""
    out = []
    for fam in K.HOLD_LAWS:
        for start, cuts in K.HOLD_STARTS.items():
            for r in cuts:
                row = {'law': K.FAMILY_NAMES[fam], 'start': start, 'cutoff': r}
                for g in K.HOLD_GUARDS:
                    x = load(rid(fam, start, r, g))
                    f = facts(x)
                    cell = {'outcome': f['outcome'] if f else 'not run', 'least': f['least'] if f else None,
                            'least_exact': f['least_exact'] if f else None, 'line': line(x)}
                    if f and f['any_mismatch']:
                        cell['listing'] = write_listing('hold %s %s r%d %s' % (row['law'], start, r, g), x)
                    if f and f['any_underbuild']:
                        fn = first_never_made(x)
                        cell['first_never_made'] = fn['reasons']
                    row[g] = cell
                out.append(row)
    return out


def stop_points(table):
    """Where the owner's stop rule falls for each law family (pre-registration, 'Runs and stop rule')."""
    out = {}
    for fam in (K.CAP3W, K.CAP3WF):
        out[K.FAMILY_NAMES[fam]] = 'R3 verdict: %s' % {
            s: (facts(load(rid(fam, s, 1, 'R3'))) or {}).get('outcome', 'not run') for s in K.CAP_STARTS}
    for fam in K.HOLD_LAWS:
        fn = K.FAMILY_NAMES[fam]
        stops = {}
        for start, cuts in K.HOLD_STARTS.items():
            where = 'a match through the last cutoff (round %d)' % cuts[-1]
            for r in cuts:
                for g in ('R3', "R3'"):
                    f = facts(load(rid(fam, start, r, g)))
                    if f and f['any_mismatch']:
                        where = 'the first mismatch: %s through round %d (least %s)' % (g, r, f['least'])
                        break
                else:
                    continue
                break
            stops[start] = where
        out[fn] = stops
    return out


def run_table():
    out = []
    for cid, start, fam, r, g in K.configs():
        x = load(cid)
        if x is None:
            out.append({'id': cid, 'status': 'not run'})
            continue
        e = x['every_order']
        out.append({'id': cid, 'command': x.get('command'), 'seconds_total': x['seconds'],
                    'every_seconds': e.get('seconds'), 'peak_rss_mb': x['peak_rss_mb'],
                    'every_finished': e.get('finished'), 'stopped': e.get('stopped'), 'keys': e.get('keys'),
                    'searched_to_births': e.get('searched_to_births'), 'births_within_r':
                        x['reference']['births_within_r'], 'R': x['reference']['R'], 'line': line(x),
                    'groups_of_three': x['group_of_three_or_more']})
    return out


def write_md(V, table, stops, runs, knot):
    L_ = []
    a = L_.append
    a('# GUARD-CAP-AND-HOLD-20261124-001A-E001: summary')
    a('')
    a('Generated by `gch_summarize.py`. "Every order": breadth-first over memo keys, capped at two million keys (checked')
    a('when a level is complete), no time budget. "Sampled": seeds 0 to 199, a uniform choice among the allowed births')
    a('(parents, f, usable) at each step. "x-last": one order per knot that exists by round 1 of the reference, seed 0.')
    a('Counts of sampled orders are counts under that uniform choice only. Readings: `deviations.md`.')
    a('')
    a('## Predictions')
    a('')
    a('| Prediction | Verdict | Numbers |')
    a('| --- | --- | --- |')
    for p in ['Gate'] + ['P%d' % i for i in range(1, 13)]:
        v = V[p]
        if p == 'Gate':
            txt = ('%d start and law pairs, %d rounds compared; D differs only under (RATION-3, CANCEL-WAIT, HOLD), in '
                   'rounds %s, by exactly the groups that hold an old member (%s); controls rejected: %s; start clause '
                   'violations: %d of %d pairs' % (
                       v['pairs'], v['rounds_compared'], v['pairs_where_D_differs'],
                       v['D_differences_explained_by_groups_with_an_old_member'],
                       ['%s (round %s)' % (c['control'], c['rejected_at_round']) for c in v['controls'] if c['rejected']],
                       len(v['start_clause_violations']), v['start_clause_checked']))
        elif p in ('P11', 'P12'):
            txt = 'see the holding table and `summary.json`'
        elif p == 'P4':
            txt = '; '.join('%s: least d with no mismatch %s' % (s, d['least_d_with_no_mismatch'])
                            for s, d in v['numbers'].items())
        else:
            parts = []
            for k, val in v.get('numbers', {}).items():
                parts.append('%s: %s' % (k, json.dumps(val, default=str) if isinstance(val, dict) else val))
            txt = ' · '.join(parts)
        extra = (' [fails on: %s]' % v['fails_on']) if v.get('fails_on') else ''
        a('| %s | %s%s | %s |' % (p, v['verdict'], extra, txt.replace('|', '/')))
    a('')
    a('## Holding: every law, start, cutoff and guard')
    a('')
    a("| Law | Start | r | R1 | R2 | R3 | R3' | Control |")
    a('| --- | --- | --- | --- | --- | --- | --- | --- |')
    for row in table:
        cells = []
        for g in K.HOLD_GUARDS:
            c = row[g]
            s = c['outcome']
            if c['least'] is not None:
                s += ' %d%s' % (c['least'], '' if c['least_exact'] else ' found')
            cells.append(s)
        a('| %s | %s | %d | %s |' % (row['law'], row['start'], row['cutoff'], ' | '.join(cells)))
    a('')
    a('First reference knot never made, and why, in every underbuilding run (aggregated over its orders):')
    a('')
    for row in table:
        for g in K.HOLD_GUARDS:
            c = row[g]
            if c.get('first_never_made'):
                a('- %s %s r%d %s: %s' % (row['law'], row['start'], row['cutoff'], g, json.dumps(c['first_never_made'])))
    a('')
    a('## Where the stop rule falls')
    a('')
    for k, v in stops.items():
        a('- %s: %s' % (k, json.dumps(v)))
    a('')
    a('## The knot test (run 5)')
    a('')
    a('- %s' % json.dumps(knot['summary']) if knot else '- not run')
    a('')
    a('## Every run')
    a('')
    a('| Run | R | births within r | result | every-order s | total s | peak MB |')
    a('| --- | --- | --- | --- | --- | --- | --- |')
    for t in runs:
        if t.get('status') == 'not run':
            a('| %s | | | not run | | | |' % t['id'])
            continue
        a('| %s | %s | %s | %s | %s | %s | %s |' % (t['id'], t['R'], t['births_within_r'], t['line'],
                                                   t['every_seconds'], t['seconds_total'], t['peak_rss_mb']))
    (ART / 'summary.md').write_text('\n'.join(L_) + '\n')


def main():
    V = verdicts()
    table = holding_table()
    stops = stop_points(table)
    runs = run_table()
    kt = ART / 'knot_test.json'
    knot = json.loads(kt.read_text()) if kt.exists() else None
    summ = {'predictions': V, 'holding_table': table, 'stop_points': stops, 'runs': runs,
            'knot_test': knot['summary'] if knot else None,
            'unfinished_every_order': [t['id'] for t in runs if t.get('every_finished') is False],
            'runs_over_600s': [{'id': t['id'], 'seconds': t['seconds_total'], 'command': t['command']}
                               for t in runs if t.get('seconds_total', 0) > 600]}
    (ART / 'summary.json').write_text(json.dumps(summ, indent=1, default=str) + '\n')
    write_md(V, table, stops, runs, knot)
    for p, v in V.items():
        print(p, v['verdict'], v.get('fails_on', ''))


if __name__ == '__main__':
    main()
