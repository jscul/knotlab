"""Every prediction of FOLLOWS-THE-FORM-20261125-001A judged by its "Fails when" entry; summary.json and summary.md.

  python -B ff_summary.py      (after ff_gate.py summary, ff_read.py for R1 R2 R2u R3 R4, ff_controls.py summary)
"""
import sys

sys.dont_write_bytecode = True

import json
import os
from collections import Counter, OrderedDict

import ff_core as C
import ff_judge as J
import ff_read as FR

ROWS = ['none, CANCEL-RETIRE', 'none, CANCEL-OFFSHOOT', 'none, CANCEL-WAIT', 'sole, CANCEL-RETIRE',
        'sole, CANCEL-OFFSHOOT', 'sole, CANCEL-WAIT']
RO_ROWS = ROWS[:2] + ROWS[3:5]          # retiring or offshoots
NONE_LAWS = ['none, %s, %s' % (r, t) for r in ('ORD', 'CAP-3', 'FLOOR1') for t in C.TREATMENTS]
ALL_LAWS = NONE_LAWS + ['sole, %s, %s' % (r, t) for r in ('ORD', 'CAP-3', 'FLOOR1') for t in C.TREATMENTS]


def pct(a, b):
    return round(100.0 * a / b, 2) if b else None


def study_name(key):
    rs, kl, fam, first, take, ration, treat = key
    return '%s %s, first seed %s, %s, %s/%s/%s' % (rs, kl, first, fam, take, ration, treat)


def pr4(recs_by_rs):
    """Start knots act in round 1 only: R1 (mixed, second) and R2 (fresh), the 12 laws with retiring or offshoots."""
    n = 0
    bad = []
    for rs in ('R1', 'R2'):
        for r in recs_by_rs[rs]:
            if r['family'] not in ('mixed', 'second', 'fresh') or r['treatment'] == 'CANCEL-WAIT':
                continue
            n += 1
            if r['last_member_round'] > 1 or r['start_member_final']:
                bad.append(r)
    extra = Counter()
    for rs in ('R1', 'R3', 'R2u', 'R4', 'R2'):
        for r in recs_by_rs.get(rs) or []:
            grp = '%s %s %s' % (rs, r['family'], 'waiting' if r['treatment'] == 'CANCEL-WAIT' else
                                'retiring or offshoots')
            extra[grp + ': runs'] += 1
            extra[grp + ': a start knot a member after round 1'] += int(r['last_member_round'] > 1 or
                                                                         r['start_member_final'])
    first = None
    if bad:
        b = bad[0]
        first = {'run': C.run_key(dict(b, take=None if b['take'] == 'none' else 'MET-SOLE')),
                 'last round a start knot is a member': b['last_member_round'],
                 'a start knot a member after the last round read': b['start_member_final']}
    return {'id': 'PR4', 'verdict': 'holds' if not bad else 'fails', 'runs': n, 'runs failing': len(bad),
            'first failing': first, 'reported, no prediction': dict(extra)}


def fate_kinds(st):
    v = set(st['fates'].values())
    k = set()
    if v & {'ends, no births', 'ends, taken up'}:
        k.add('ends')
    if 'steady' in v:
        k.add('steady')
    if 'grows' in v:
        k.add('grows')
    return k


def main():
    disc = C.load_disclosed()
    with open(C.out_path('gate.json')) as f:
        gate = json.load(f)
    controls = None
    if os.path.exists(C.out_path('controls.json')):
        with open(C.out_path('controls.json')) as f:
            controls = json.load(f)
    S = {rs: J.load_studies(rs) for rs in ('R1', 'R2', 'R2u', 'R3', 'R4')}
    T = {rs: J.load_tables(rs) for rs in ('R1', 'R2', 'R2u', 'R3', 'R4')}
    recs = {rs: FR.load_runs(rs) for rs in ('R1', 'R2', 'R2u', 'R3', 'R4')}
    P = OrderedDict()

    # G
    P['G'] = {'id': 'G', 'verdict': gate['verdict'],
              'numbers': {'starts as written': [s['equal'] for s in gate['starts']['starts']],
                          'sampled runs': gate['sampled_runs'], 'by run set': gate['sample_by_runset'],
                          'second growth (no taking rule)': gate['second_growth'],
                          'takes recomputed (the take)': gate['takes']}}
    # replication
    rep = J.replication()
    for k in ('PR1', 'PR2', 'PR3', 'PR5'):
        v = rep[k]
        P[k] = {'id': k, 'verdict': v['verdict'],
                'numbers': {x: y for x, y in v.items() if x not in ('verdict', 'first differing', 'all differing')},
                'first failing': v.get('first differing') or None}
    P['PR4'] = pr4(recs)

    s2 = S['R2']
    t2 = T['R2']
    # CU
    su = S['R2u']
    bad = [s for s in su if not s['every_form_in_bare_class']]
    P['CU'] = {'id': 'CU', 'verdict': 'holds' if not bad and len(su) == 90 else 'fails',
               'numbers': {'studies': len(su), 'every form in the bare start\'s class': len(su) - len(bad),
                           'forms out of the bare start\'s class (all studies)':
                               sum(s['n_forms'] - s['forms_in_bare_class'] for s in su)},
               'first failing': None if not bad else {'study': study_name(bad[0]['key']),
                                                      'forms in the bare class': bad[0]['forms_in_bare_class']}}
    cu_ok = P['CU']['verdict'] == 'holds'
    # S1, S2
    bad = [s for s in s2 if not s['bare_own_class']]
    P['S1'] = {'id': 'S1', 'verdict': 'holds' if not bad else 'fails',
               'numbers': {'studies': len(s2), 'bare start a class of its own': len(s2) - len(bad)},
               'first failing': None if not bad else study_name(bad[0]['key'])}
    bad = [s for s in s2 if s['n_classes_forms'] < 2]
    P['S2'] = {'id': 'S2', 'verdict': 'holds' if not bad else 'fails',
               'numbers': {'studies': len(s2), 'two or more classes among the forms': len(s2) - len(bad),
                           'fewest classes': min(s['n_classes_forms'] for s in s2)},
               'first failing': None if not bad else study_name(bad[0]['key'])}
    # S3
    dt3 = T['R3']['depth, chains, first seeds K to O together (told apart / pairs)']
    bad = [law for law in ALL_LAWS if dt3[law]['1 against 2 knots'] != [20, 20]]
    P['S3'] = {'id': 'S3', 'verdict': 'holds' if not bad else 'fails',
               'numbers': {law: dt3[law]['1 against 2 knots'] for law in ALL_LAWS},
               'first failing': None if not bad else {'law': bad[0], 'cell': dt3[bad[0]]['1 against 2 knots']}}
    # PN2
    n3 = sum(1 for s in s2 if s['n_classes_forms'] >= 3)
    P['PN2'] = {'id': 'PN2', 'verdict': 'holds' if n3 >= 81 else 'fails',
                'numbers': {'studies with three or more classes among the forms': n3, 'studies': len(s2),
                            'distribution of the number of classes': dict(sorted(Counter(
                                s['n_classes_forms'] for s in s2).items()))},
                'first failing': None if n3 >= 81 else [study_name(s['key']) for s in s2
                                                        if s['n_classes_forms'] < 3][:3]}
    # PN3
    aft = t2['after the first round']['fresh']
    vals = {r: aft[r]['of those, the wider record of round 1 the same'] for r in ROWS}
    bad = [r for r in RO_ROWS if vals[r] < 50]
    P['PN3'] = {'id': 'PN3', 'verdict': 'holds' if not bad else 'fails',
                'numbers': {'told apart after the first round, by row': vals,
                            'pairs a row': {r: aft[r]['pairs'] for r in ROWS}},
                'first failing': None if not bad else {'row': bad[0], 'pairs': vals[bad[0]]}}
    # PN4
    sh = {r: pct(aft[r]['told apart at R*'], aft[r]['pairs']) for r in ROWS}
    bad = [r for r in ROWS if not (45 <= sh[r] <= 95)]
    P['PN4'] = {'id': 'PN4', 'verdict': 'holds' if not bad else 'fails',
                'numbers': {'percent of pairs of forms told apart at R*, by row': sh,
                            'told apart / pairs': {r: [aft[r]['told apart at R*'], aft[r]['pairs']] for r in ROWS}},
                'first failing': None if not bad else {'row': bad[0], 'percent': sh[bad[0]]}}
    # PN5
    n5 = sum(1 for s in s2 if len(fate_kinds(s)) >= 2)
    fat = t2['fates on the window']['fresh']
    ends_split = {r: {'ends, no births': fat[r].get('ends, no births', 0),
                      'ends, taken up': fat[r].get('ends, taken up', 0)} for r in ROWS}
    P['PN5'] = {'id': 'PN5', 'verdict': 'holds' if n5 >= 40 else 'fails',
                'numbers': {'studies whose forms show two or more of ends, steady, grows': n5, 'studies': len(s2),
                            'studies with fates not read (R* < 4)': sum(1 for s in s2 if s['R*'] < 4),
                            'the split of ends, by row (forms)': ends_split},
                'first failing': None if n5 >= 40 else 'fewer than 40 studies'}
    # PN6
    s4 = S['R4']
    n6 = sum(1 for s in s4 if s['n_classes_forms'] >= 3)
    P['PN6'] = {'id': 'PN6', 'verdict': 'holds' if n6 >= 60 else 'fails',
                'numbers': {'studies with three or more classes among the forms (parity)': n6, 'studies': len(s4),
                            'distribution of the number of classes': dict(sorted(Counter(
                                s['n_classes_forms'] for s in s4).items()))},
                'first failing': None if n6 >= 60 else 'fewer than 60 studies'}
    # PN7
    not_held = sum(1 for s in s2 if not s['profile_function']['the held knot'])
    not_both = sum(1 for s in s2 if not s['profile_function']['both'])
    not_births = sum(1 for s in s2 if not s['profile_function']["the second seed's births by round"])
    ok7 = not_held >= 81 and not_both >= 25
    P['PN7'] = {'id': 'PN7', 'verdict': 'holds' if ok7 else 'fails',
                'numbers': {'not a function of the held knot': not_held,
                            'not a function of the held knot with the second seed\'s births by round': not_both,
                            'not a function of the second seed\'s births by round (reported)': not_births,
                            'studies': len(s2)},
                'first failing': None if ok7 else ('held knot: %d < 81' % not_held if not_held < 81 else
                                                   'both: %d < 25' % not_both)}
    # PD1
    cells_d = ['depth 2', 'depth 3', 'depth 4']
    bounds = [(c, 10.0) for c in cells_d] + [('3 against 4 knots', 30.0), ('4 against 5 knots', 15.0)]
    nums = {}
    bad = []
    for law in NONE_LAWS:
        row = {}
        for c, bnd in bounds:
            a, b = dt3[law][c]
            row[c] = [a, b, pct(a, b)]
            if pct(a, b) > bnd:
                bad.append({'law': law, 'cell': c, 'told apart / pairs': [a, b], 'percent': pct(a, b),
                            'bound': bnd})
        nums[law] = row
    P['PD1'] = {'id': 'PD1', 'verdict': 'holds' if not bad else 'fails', 'numbers': nums,
                'first failing': bad[0] if bad else None, 'all failing': bad}
    # PD2
    laws2 = ['sole, ORD, CANCEL-RETIRE', 'sole, ORD, CANCEL-OFFSHOOT', 'sole, ORD, CANCEL-WAIT',
             'sole, CAP-3, CANCEL-WAIT']
    nums = {}
    bad = []
    for law in laws2:
        a, b = dt3[law]['4 against 5 knots']
        nums[law] = [a, b, pct(a, b)]
        if pct(a, b) < 15.0:
            bad.append({'law': law, 'told apart / pairs': [a, b], 'percent': pct(a, b)})
    P['PD2'] = {'id': 'PD2', 'verdict': 'holds' if not bad else 'fails', 'numbers': nums,
                'first failing': bad[0] if bad else None}
    # C1, C2
    if controls is None:
        P['C1'] = {'id': 'C1', 'verdict': 'not run'}
        P['C2'] = {'id': 'C2', 'verdict': 'not run'}
    else:
        rn = controls['renumbering']
        P['C1'] = {'id': 'C1', 'verdict': 'holds' if rn['differing'] == 0 and rn['renumbered runs'] == 900 else
                   'fails', 'numbers': {k: v for k, v in rn.items() if k != 'first differing'},
                   'first failing': (rn['first differing'] or [None])[0]}
        kt = controls['knot test']
        P['C2'] = {'id': 'C2', 'verdict': 'holds' if kt['nae']['failing knots'] == 0 and kt['nae']['runs'] > 0 else
                   'fails', 'numbers': {'not-all-equal': {k: v for k, v in kt['nae'].items() if k != 'first failing'},
                                        'parity (reported, no prediction)': {k: v for k, v in kt['parity'].items()
                                                                              if k != 'first failing'}},
                   'first failing': kt['nae']['first failing'],
                   'parity, first failing (reported)': kt['parity']['first failing']}
        P['C2']['cut'] = controls.get('cut')
        P['C2']['knot tests outside the half (reported apart)'] = controls.get(
            'knot test outside the half (reported apart, not the registered row)')
    if not cu_ok:
        for k in ('S1', 'S2', 'S3', 'PN2', 'PN3', 'PN4', 'PN5', 'PN6', 'PN7', 'PD1', 'PD2'):
            P[k]['note'] = 'CU failed: not read as registered'

    claim = OrderedDict()
    v = lambda *ks: 'holds' if all(P[k]['verdict'] == 'holds' for k in ks) else 'fails'
    claim['claim C1 (by PN2 and PN4 with CU)'] = v('PN2', 'PN4', 'CU')
    claim['claim C2 (by PN3)'] = v('PN3')
    claim['claim C3 (by PN7)'] = v('PN7')
    claim['claim C4 (by PN5)'] = v('PN5')
    claim['claim C5 (by PD1 and PD2)'] = v('PD1', 'PD2')

    reported = OrderedDict()
    for rs in ('R1', 'R2', 'R4'):
        t = T[rs]
        reported[rs] = {'wider record against own descent (studies)': t['wider record against own descent (studies)'],
                        'classes among the forms (studies by number)': t['classes among the forms (studies by number)'],
                        'classes by the wider record (studies by number)':
                            t['classes by the wider record (studies by number)']}
    rstar = OrderedDict()
    for rs in ('R1', 'R2', 'R2u', 'R3', 'R4'):
        rstar[rs] = T[rs]['R*']
    # checks reported with the verdicts (no prediction)
    notes = OrderedDict()
    notes['PN5 reading applied to R1 (disclosed: 58 of 90 on mixed, 62 of 90 on second)'] = {
        fam: sum(1 for s in S['R1'] if s['key'][2] == fam and len(fate_kinds(s)) >= 2)
        for fam in ('mixed', 'second', 'chains')}
    a = {(r['first'], r['take'], r['ration'], r['treatment'], r['second']): r for r in recs['R2']}
    b = {(r['first'], r['take'], r['ration'], r['treatment'], r['second']): r for r in recs['R4']}
    keyf = lambda r: (r['make'], r['wider'], r['sec_only'], r['rounds_read'], r['stop'], r['knots'])
    notes['R4 against R2: runs whose record differs (parity against not-all-equal, same starts and laws)'] = [
        sum(1 for k in a if keyf(a[k]) != keyf(b[k])), len(a)]
    notes['R4: entries of the wider record with f = 0 (implied births of the first)'] = sum(
        1 for r in recs['R4'] for m in r['wider'] for e in m if e[3] == 0)
    notes['studies of R4 whose classes differ from the same study of R2'] = sum(
        1 for x, y in zip(S['R2'], S['R4']) if sorted(map(sorted, x['classes'])) != sorted(map(sorted, y['classes'])))
    wl = []
    p = C.out_path('logs/walltime.log')
    if os.path.exists(p):
        with open(p) as f:
            wl = [ln.rstrip('\n') for ln in f]
    notes['wall time log'] = wl
    summary = {'predictions': list(P.values()), 'claim parts': claim, 'reported': reported, 'notes': notes,
               'R* by row': rstar,
               'tables': {'R2': {k: v for k, v in t2.items()}, 'R2u': T['R2u'], 'R3': T['R3'], 'R4': T['R4']}}
    with open(C.out_path('summary.json'), 'w') as f:
        json.dump(summary, f, indent=1)
    write_md(summary, P, T, gate, controls, disc)
    for p in P.values():
        C.log(p['id'], p['verdict'])


# ----------------------------------------------------------------------------------------------------- markdown
def md_table_rows(tab, cols):
    lines = ['| row | ' + ' | '.join(cols) + ' |', '| --- |' + ' --- |' * len(cols)]
    for r, d in tab.items():
        lines.append('| %s | ' % r + ' | '.join(str(d.get(c, 0)) for c in cols) + ' |')
    return lines


def fta_cols(tab):
    ks = set()
    for d in tab.values():
        ks |= set(d)
    num = sorted((k for k in ks if k.isdigit()), key=int)
    return num + [k for k in ('never', 'not read further') if k in ks]


def fmt(x):
    return json.dumps(x)


def write_md(summary, P, T, gate, controls, disc):
    L = []
    L.append('# FOLLOWS-THE-FORM-20261125-001A-E001: summary')
    L.append('')
    L.append('An independent reading on the shared growth engine (ticket B\'s `eng.py`, unchanged), written from the frozen '
             'texts alone. Every prediction is judged by its "Fails when" entry. Readings chosen where the texts leave '
             'a choice are numbered in `deviations.md` of the experiment folder. No weighting is named.')
    L.append('')
    L.append('## Predictions')
    L.append('')
    L.append('| # | verdict | numbers |')
    L.append('| --- | --- | --- |')
    short = {
        'G': lambda p: 'three starts as written; %d sampled runs: %d/%d with no taking rule identical to the fold engine '
                       'at every round; %d/%d with the take, %d births, %d takes, every take as the rule says' % (
                           p['numbers']['sampled runs'], p['numbers']['second growth (no taking rule)']['exact_equal'],
                           p['numbers']['second growth (no taking rule)']['runs'],
                           p['numbers']['takes recomputed (the take)']['exact_equal'],
                           p['numbers']['takes recomputed (the take)']['runs'],
                           p['numbers']['takes recomputed (the take)']['births'],
                           p['numbers']['takes recomputed (the take)']['takes']),
        'PR1': lambda p: '%d of %d studies with R* and classes equal' % (p['numbers']['same'], p['numbers']['studies']),
        'PR2': lambda p: '%d differing cells of %d' % (p['numbers']['differing cells'],
                                                        p['numbers']['cells compared (disclosed leaves)']),
        'PR3': lambda p: '%d differing cells of %d' % (p['numbers']['differing cells'],
                                                        p['numbers']['cells compared (disclosed leaves)']),
        'PR5': lambda p: '%d differing cells of %d' % (p['numbers']['differing cells'],
                                                        p['numbers']['cells compared (disclosed leaves)']),
        'PR4': lambda p: '%d runs; %d with a start knot a member after round 1' % (p['runs'], p['runs failing']),
        'CU': lambda p: '%d of %d studies with every form in the bare start\'s class' % (
            p['numbers']['every form in the bare start\'s class'], p['numbers']['studies']),
        'S1': lambda p: '%d of %d studies' % (p['numbers']['bare start a class of its own'], p['numbers']['studies']),
        'S2': lambda p: '%d of %d studies; fewest %d' % (p['numbers']['two or more classes among the forms'],
                                                          p['numbers']['studies'], p['numbers']['fewest classes']),
        'S3': lambda p: 'cells: %s' % ', '.join(sorted({'%d/%d' % tuple(v) for v in p['numbers'].values()})),
        'PN2': lambda p: '%d of %d studies (needs 81)' % (p['numbers']['studies with three or more classes among the forms'],
                                                           p['numbers']['studies']),
        'PN3': lambda p: 'by row: %s (needs 50 in each row with retiring or offshoots)' % fmt(
            p['numbers']['told apart after the first round, by row']),
        'PN4': lambda p: 'percent by row: %s' % fmt(p['numbers']['percent of pairs of forms told apart at R*, by row']),
        'PN5': lambda p: '%d of %d studies (needs 40); fates not read in %d' % (
            p['numbers']['studies whose forms show two or more of ends, steady, grows'], p['numbers']['studies'],
            p['numbers']['studies with fates not read (R* < 4)']),
        'PN6': lambda p: '%d of %d studies (needs 60)' % (
            p['numbers']['studies with three or more classes among the forms (parity)'], p['numbers']['studies']),
        'PN7': lambda p: 'not a function of the held knot in %d (needs 81); not of it with the births by round in %d '
                         '(needs 25); not of the births by round alone in %d; of 90' % (
            p['numbers']['not a function of the held knot'],
            p['numbers']['not a function of the held knot with the second seed\'s births by round'],
            p['numbers']['not a function of the second seed\'s births by round (reported)']),
        'PD1': lambda p: 'highest: ' + ', '.join('%s %.1f%%' % (c, max(v[c][2] for v in p['numbers'].values()))
                                                for c in ('depth 2', 'depth 3', 'depth 4', '3 against 4 knots',
                                                          '4 against 5 knots')),
        'PD2': lambda p: ', '.join('%s %d/%d (%.1f%%)' % (k, v[0], v[1], v[2]) for k, v in p['numbers'].items()),
        'C1': lambda p: ('not run' if p['verdict'] == 'not run' else '%d of %d renumbered runs make the same' % (
            p['numbers']['make the same (and rounds read, stop)'], p['numbers']['renumbered runs'])),
        'C2': lambda p: ('not run' if p['verdict'] == 'not run' else
                         'cut to half (deviations 35): not-all-equal %d of 100 runs tested, %d verdicts, %d failing; '
                         'parity %d of 50 runs, %d verdicts, %d failing knots in %d runs (reported); not run: %s. '
                         'Outside the half, reported apart: not-all-equal %d runs, %d verdicts, %d failing; parity %d '
                         'runs, %d failing' % (
                             p['numbers']['not-all-equal']['runs'], p['numbers']['not-all-equal']['verdicts'],
                             p['numbers']['not-all-equal']['failing knots'],
                             p['numbers']['parity (reported, no prediction)']['runs'],
                             p['numbers']['parity (reported, no prediction)']['verdicts'],
                             p['numbers']['parity (reported, no prediction)']['failing knots'],
                             p['numbers']['parity (reported, no prediction)']['runs with a failing knot'],
                             ', '.join('job %d (%s)' % (x['job'], x['run']) for x in
                                       p['cut']['knot tests of the half not run']) or 'none of the half',
                             p['knot tests outside the half (reported apart)']['nae runs'],
                             p['knot tests outside the half (reported apart)']['nae verdicts'],
                             p['knot tests outside the half (reported apart)']['nae failing knots'],
                             p['knot tests outside the half (reported apart)']['parity runs'],
                             p['knot tests outside the half (reported apart)']['parity failing knots'])),
    }
    for p in P.values():
        L.append('| %s | **%s** | %s |' % (p['id'], p['verdict'], short[p['id']](p)))
    L.append('')
    fails = [p for p in P.values() if p['verdict'] == 'fails']
    if fails:
        L.append('First failing case of each failed prediction:')
        L.append('')
        for p in fails:
            L.append('- **%s**: `%s`' % (p['id'], json.dumps(p.get('first failing'))))
        L.append('')
    L.append('Claim parts as the pre-registration judges them: ' + '; '.join(
        '%s: %s' % (k, v) for k, v in summary['claim parts'].items()) + '.')
    L.append('')
    L.append('## Checks reported with the verdicts')
    L.append('')
    for k, v in summary['notes'].items():
        if k == 'wall time log':
            continue
        L.append('- %s: %s' % (k, fmt(v)))
    L.append('')
    L.append('## Wall time')
    L.append('')
    L.append('From `logs/walltime.log` (timing parts and readings are listed in `deviations.md`, entries 28 to 35):')
    L.append('')
    L.append('```')
    L += summary['notes']['wall time log']
    L.append('```')
    L.append('')
    # R2 tables
    for rs, fam, title in (('R2', 'fresh', 'R2, held out (`fresh`, first seeds K to O, not-all-equal)'),
                           ('R4', 'fresh', 'R4, the knot law swapped (`fresh`, K to O, parity)')):
        t = T[rs]
        L.append('## %s' % title)
        L.append('')
        L.append('**First told apart**, pairs of forms (%d a row):' % t['after the first round'][fam][ROWS[0]]['pairs'])
        L.append('')
        tab = t['first told apart, %s' % fam]
        L += md_table_rows(tab, fta_cols(tab))
        L.append('')
        L.append('**After the first round:**')
        L.append('')
        L += md_table_rows(t['after the first round'][fam], ['pairs', 'told apart at R*',
                                                            'first told apart in round 2 or later',
                                                            'of those, the wider record of round 1 the same',
                                                            'in round 3 or later with the wider records the same through round 2'])
        L.append('')
        L.append('**Fates on the window** (forms):')
        L.append('')
        L += md_table_rows(t['fates on the window'][fam], ['grows', 'steady', 'shrinks', 'other', 'ends, taken up',
                                                          'ends, no births', 'not read'])
        L.append('')
        cp = t['the count profile (studies in which the class is a function of it)'][fam]
        L.append('**The count profile** (studies in which the class is a function of it): the held knot %d; the second '
                 'seed\'s births by round %d; both %d; of %d studies.' % (
                     cp['the held knot'], cp["the second seed's births by round"], cp['both'], cp['studies']))
        L.append('')
        L.append('**R\\*** by row: ' + '; '.join('%s: %s' % (r, fmt(v)) for r, v in t['R*'][fam].items()))
        L.append('')
        L.append('**Classes among the forms** (studies by number of classes): %s. **By the wider record**: %s. Wider '
                 'record against own descent: %s.' % (fmt(t['classes among the forms (studies by number)'][fam]),
                                                      fmt(t['classes by the wider record (studies by number)'][fam]),
                                                      fmt(t['wider record against own descent (studies)'][fam])))
        L.append('')
        L.append('Bare start a class of its own: %s studies.' % fmt(t['bare start a class of its own (studies)'][fam]))
        L.append('')
    L.append('## R2u, the unlinked control')
    L.append('')
    t = T['R2u']
    L.append('**Unlinked control, fresh**: studies %d; studies in which every form is in the bare start\'s class %d. '
             'R\\* by row: %s.' % (t['every form in the bare start\'s class (studies)']['fresh'][1],
                                   t['every form in the bare start\'s class (studies)']['fresh'][0],
                                   '; '.join('%s: %s' % (r, fmt(v)) for r, v in t['R*']['fresh'].items())))
    L.append('')
    L.append('## R3, depth on the chains (first seeds K to O together; told apart / pairs)')
    L.append('')
    dt = T['R3']['depth, chains, first seeds K to O together (told apart / pairs)']
    cols = ['depth 0', '1 against 2 knots', 'depth 1', '2 against 3 knots', 'depth 2', '3 against 4 knots', 'depth 3',
            '4 against 5 knots', 'depth 4']
    L.append('| law | ' + ' | '.join(cols) + ' |')
    L.append('| --- |' + ' --- |' * len(cols))
    for law, d in dt.items():
        L.append('| %s | ' % law + ' | '.join('%d/%d' % tuple(d[c]) for c in cols) + ' |')
    L.append('')
    L.append('R\\* by row (R3): ' + '; '.join('%s: %s' % (r, fmt(v)) for r, v in T['R3']['R*']['chains'].items()))
    L.append('')
    L.append('## R\\* by row, every run set')
    L.append('')
    for rs, byfam in summary['R* by row'].items():
        for fam, rows in byfam.items():
            L.append('- %s, `%s`: %s' % (rs, fam, '; '.join('%s: %s' % (r, fmt(v)) for r, v in rows.items())))
    L.append('')
    L.append('## Classes by the wider record (reported, no prediction)')
    L.append('')
    for rs, d in summary['reported'].items():
        for fam in d['wider record against own descent (studies)']:
            L.append('- %s, `%s`: wider record against own descent %s; classes among the forms %s; by the wider record %s'
                     % (rs, fam, fmt(d['wider record against own descent (studies)'][fam]),
                        fmt(d['classes among the forms (studies by number)'][fam]),
                        fmt(d['classes by the wider record (studies by number)'][fam])))
    L.append('')
    L.append('## Start knots in the roster (PR4 and reported)')
    L.append('')
    for k, val in sorted(P['PR4']['reported, no prediction'].items()):
        L.append('- %s: %d' % (k, val))
    L.append('')
    with open(C.out_path('summary.md'), 'w') as f:
        f.write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
