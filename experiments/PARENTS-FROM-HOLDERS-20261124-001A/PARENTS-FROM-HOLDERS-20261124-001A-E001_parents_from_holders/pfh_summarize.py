"""Verdicts: summary.json and summary.md, one row per prediction (pre-registration, "Predictions (frozen)").

    python -B pfh_summarize.py
"""
from __future__ import annotations

import json

import pfh_common as PC

LAWS = ('F1O', 'F1R', 'R3W', 'ORD')
VARS = ('full', 'c1', 'c2')
POPS = ('P1', 'P1 reference', 'P1 serial', 'P2', 'P1P2')


def load(name):
    p = PC.OUT / name
    if p.exists():
        return json.loads(p.read_text())
    return None


def law_summary(short):
    files = {pop: load('%s_%s.json' % (short, pop)) for pop in ('P1', 'P2', 'P1P2')}
    pairs = load('pairs_%s.json' % short)
    if any(v is None for v in files.values()) or pairs is None:
        return None
    tabs = {}
    for f in files.values():
        for k, t in f['tables'].items():
            tabs.setdefault(k, {}).update(t)
    least = {}
    for f in files.values():
        least.update(f['least_distance_no_confusable_pair'])
    out = {'law': pairs['law'], 'starts': pairs['starts'], 'n_places': pairs['n_places'],
           'n_structures': pairs['n_structures'], 'seconds': pairs['seconds'], 'peak_rss_mb': pairs['peak_rss_mb'],
           'p2_rounds': pairs['p2_rounds'], 'command': pairs['command']}
    out['least_distance'] = {pop: {v: least.get('%s %s' % (v, pop)) for v in VARS} for pop in POPS}
    rows = {}
    for pop in POPS:
        rows[pop] = {}
        for v in VARS:
            rows[pop][v] = [{'d': d, 'classes': tabs['%s d=%d' % (v, d)][pop]['classes'],
                             'mixed': tabs['%s d=%d' % (v, d)][pop]['mixed_classes'],
                             'groups': tabs['%s d=%d' % (v, d)][pop]['mixed_by_group'],
                             'child_and_start_only': tabs['%s d=%d' % (v, d)][pop]['classes_child_and_start_only'],
                             'guard': tabs['%s d=%d' % (v, d)][pop]['guard_count'],
                             'places': tabs['%s d=%d' % (v, d)][pop]['places']} for d in range(1, 7)]
    out['by_distance'] = rows
    rounds = sorted({int(p.split()[-1]) for k in tabs for p in tabs[k] if p.startswith('P2 round')})
    out['p2_by_round'] = {t: {'least_full': least.get('full P2 round %d' % t),
                              'mixed_full': [tabs['full d=%d' % d]['P2 round %d' % t]['mixed_classes'] for d in range(1, 7)],
                              'guard': [tabs['full d=%d' % d]['P2 round %d' % t]['guard_count'] for d in range(1, 7)],
                              'places': tabs['full d=1']['P2 round %d' % t]['places']}
                          for t in rounds}
    out['written_pairs'] = {}
    for d, w in pairs['written_pairs_P2_full'].items():
        if w is None:
            out['written_pairs'][d] = None
            continue
        out['written_pairs'][d] = {'farness': w['farness'], 'group': w['group'],
                                   'parent_place': _brief(w['parent_place']), 'other_place': _brief(w['other_place']),
                                   'least_separating_distance_up_to_10': w['least_separating_distance_up_to_10'],
                                   'look': w['look_at_d']}
    out['followed_pair'] = pairs['followed_pair']
    out['whole_structure_renamings'] = pairs['whole_structure_renamings']
    out['test_stats'] = pairs['test_stats']
    out['in_look'] = {'checked': sum(pairs['in_look_checked'].values()), 'sampled': sum(pairs['in_look_sampled'].values())}
    out['search_stats'] = pairs['search_stats']
    out['whole_structure_links'] = pairs['whole_structure_links']
    return out


def _pattern(vals):
    """How a least separating distance behaves over the rounds followed."""
    if len(vals) < 2:
        return 'one round only' if vals else 'never told apart up to the distance searched'
    if all(b == a + 1 for a, b in zip(vals, vals[1:])):
        return 'increases by one at every round'
    if all(b > a for a, b in zip(vals, vals[1:])):
        return 'increases at every round'
    k = len(vals) - 1
    while k > 0 and vals[k - 1] == vals[-1]:
        k -= 1
    if all(b > a for a, b in zip(vals[:k + 1], vals[1:k + 1])):
        return 'increases at every round up to the %d-th of %d rounds, then stays %d' % (k + 1, len(vals), vals[-1])
    return 'not increasing: %s' % vals


def _brief(r):
    keys = ('structure', 'knot', 'distinction', 'other_holder', 'kind', 'round_of_birth_of_knot',
            'round_of_birth_of_other_holder', 'distance_to_start', 'distance_to_member')
    return {k: r.get(k) for k in keys}


def main():
    chk = load('checks.json')
    ext = load('checks_extra.json')
    kt = load('knot_tests.json')
    rules = load('rules.json')
    wextra = load('whole_extra.json')
    wpairs = load('whole_pairs.json')
    fextra = load('followed_extra.json')
    laws = {s: law_summary(s) for s in LAWS}
    stop = {}
    for s, l in laws.items():
        if l is None:
            continue
        fol = (l['followed_pair'] or {}).get('rows', [])
        seps = [(r['round'], r['least_separating_distance']) for r in fol]
        vals = [v for _, v in seps if v is not None]
        grows = _pattern(vals)
        stop[s] = {'least_distance_P1_and_P2_pooled': l['least_distance']['P1P2']['full'],
                   'least_distance_P2': l['least_distance']['P2']['full'],
                   'least_distance_P1': l['least_distance']['P1']['full'],
                   'guard_count_P2_at_that_distance': (l['by_distance']['P2']['full'][l['least_distance']['P2']['full'] - 1]['guard']
                                                       if l['least_distance']['P2']['full'] else None),
                   'least_distance_P2_by_round': {t: v['least_full'] for t, v in l['p2_by_round'].items()},
                   'followed_pair_separating_distance_by_round': seps,
                   'followed_pair_separating_distance_grows': grows,
                   'whole_structure_pairs_at_d6': (wpairs or {}).get(s, {}).get('counts')}
        if fextra and s in fextra:
            ex = [(r['round'], r['least_separating_distance']) for r in fextra[s]['rows']]
            stop[s]['addition_followed_pair_by_round'] = ex
            stop[s]['addition_followed_pair_pattern'] = _pattern([v for _, v in ex if v is not None])
    preds = []

    # Checks
    b = chk['check_b']
    preds.append({'id': 'Checks', 'prediction': 'The three checks of the code hold, the second with its exact threshold d <= R - 2.',
                  'verdict': 'holds' if chk['pass'] else 'fails',
                  'numbers': '(a) %d looks, %d pairs, %d alike by every renaming, %d disagreements, hand pairs %s; '
                             '(b) thresholds %s for R = 4..9 (expected R - 2); (c) %d plants, all %s' % (
                      chk['check_a']['n_looks'], chk['check_a']['pairs_compared'],
                      chk['check_a']['pairs_alike_by_every_renaming'], len(chk['check_a']['disagreements']),
                      'pass' if all(h['pass'] for h in chk['check_a']['hand_pairs']) else 'FAIL',
                      [r['threshold_found'] for r in b['rows']], chk['check_c']['n_plants'],
                      'pass' if chk['check_c']['pass'] else 'FAIL')})
    # P1
    have = {s: laws[s] is not None for s in LAWS}
    if all(have.values()):
        d1 = {s: laws[s]['by_distance']['P2']['full'][0]['mixed'] for s in LAWS}
        preds.append({'id': 'P1', 'prediction': 'At distance 1 there is a confusable pair under every law in P2.',
                      'verdict': 'holds' if all(v > 0 for v in d1.values()) else 'fails',
                      'numbers': 'mixed classes at d = 1 on P2 (full look): %s' % d1})
    # P2
    if have['F1O']:
        L = laws['F1O']
        fol = L['followed_pair']['rows']
        thr_ok = all(r['least_separating_distance'] == r['round'] - 1 for r in fol)
        r8 = {t: v['mixed_full'] for t, v in L['p2_by_round'].items() if int(t) >= 8}
        every = all(all(m > 0 for m in v) for v in r8.values())
        preds.append({'id': 'P2', 'prediction': 'Under (FLOOR1, CANCEL-OFFSHOOT, RELEASE) a confusable pair at every distance '
                      'from 1 to 6 once the structure has eight rounds; for the advisor\'s pair the least separating '
                      'distance is R - 1 at round R; no rule of a fixed distance.',
                      'verdict': 'holds' if (thr_ok and every) else 'fails',
                      'numbers': 'advisor\'s pair, least separating distance by round: %s; mixed classes at d = 1..6 in '
                                 'P2 rounds >= 8: %s; least distance with no confusable pair on P2: %s' % (
                          [(r['round'], r['least_separating_distance']) for r in fol], r8,
                          L['least_distance']['P2']['full'])})
    # P3
    if have['F1R']:
        L = laws['F1R']
        m3 = {pop: L['by_distance'][pop]['full'][2]['mixed'] for pop in ('P1', 'P1 reference', 'P1 serial', 'P2')}
        holds = m3['P1'] == 0 and m3['P2'] == 0
        preds.append({'id': 'P3', 'prediction': 'Under (FLOOR1, CANCEL-RETIRE, RELEASE) a rule exists at distance 2 or 3 on '
                      'P1 and P2.', 'verdict': 'holds' if holds else 'fails',
                      'numbers': 'mixed classes at d = 3 (full look): %s; least distance with no confusable pair: P2 %s, '
                                 'P1 reference rounds %s, P1 serial states %s, P1 %s; guard count at d = 2 on P2 %s. '
                                 'It fails on P1\'s serial states only: their mixed classes are small states that a renaming '
                                 'of the whole structure exchanges (at d = 6: %s); on P2 and on P1\'s reference rounds the '
                                 'advisor\'s expectation holds, at distance 2, and the rule of run 6 reproduces every place' % (
                          m3, L['least_distance']['P2']['full'], L['least_distance']['P1 reference']['full'],
                          L['least_distance']['P1 serial']['full'], L['least_distance']['P1']['full'],
                          L['by_distance']['P2']['full'][1]['guard'], (wpairs or {}).get('F1R', {}).get('counts'))})
    # P4
    if have['R3W']:
        L = laws['R3W']
        ld = L['least_distance']['P2']['full']
        preds.append({'id': 'P4', 'prediction': 'Under (RATION-3, CANCEL-WAIT, RELEASE): whether a rule exists at some '
                      'distance up to 6 on P2 (open; the advisor leans toward a rule).',
                      'verdict': (('on P2 no confusable pair from distance %d, but the guard count there is %d: every '
                                   'look at that distance holds a start knot or a member, so this shows nothing about larger '
                                   'structures; by round the least distance grows; P1 has confusable pairs at every distance' % (
                                       ld, L['by_distance']['P2']['full'][ld - 1]['guard'])) if ld else
                                  'no rule at any distance up to 6 on P2'),
                      'numbers': 'mixed classes on P2 by d: %s; guard counts on P2 by d: %s; least distance on P2 by round: '
                                 '%s; followed pair (D2(4,3)), least separating distance by round: %s' % (
                          [r['mixed'] for r in L['by_distance']['P2']['full']],
                          [r['guard'] for r in L['by_distance']['P2']['full']],
                          {t: v['least_full'] for t, v in L['p2_by_round'].items()},
                          [(r['round'], r['least_separating_distance']) for r in L['followed_pair']['rows']])})
    # P5
    if all(have.values()):
        p5 = {s: {'P1': laws[s]['least_distance']['P1']['full'],
                  'P1 reference': laws[s]['least_distance']['P1 reference']['full'],
                  'P1 serial': laws[s]['least_distance']['P1 serial']['full'],
                  'guard P1 d=1..6': [r['guard'] for r in laws[s]['by_distance']['P1']['full']]} for s in LAWS}
        preds.append({'id': 'P5', 'prediction': 'On P1 alone: the least distance with no confusable pair for each law, if '
                      'any, with the guard count (open).', 'verdict': 'reported', 'numbers': p5})
    # P6
    if have['ORD']:
        L = laws['ORD']
        ld = L['least_distance']['P2']['full']
        preds.append({'id': 'P6', 'prediction': 'Under ordinary growth: whether a rule exists at some distance up to 6 on P2 '
                      '(open).', 'verdict': ('a rule exists on P2 at distance %d' % ld) if ld else
                      'no rule at any distance up to 6 on P2',
                      'numbers': 'mixed classes on P2 by d: %s; guard counts on P2 by d: %s; least distance on P2 by round: '
                                 '%s; the class at d = 6 is the stopped LONE-FOUR structure (the hypercube), exchanged by a '
                                 'renaming of the whole structure; the pair added by item 40 (two-knot start), least '
                                 'separating distance by round: %s' % (
                          [r['mixed'] for r in L['by_distance']['P2']['full']],
                          [r['guard'] for r in L['by_distance']['P2']['full']],
                          {t: v['least_full'] for t, v in L['p2_by_round'].items()},
                          [(r['round'], r['least_separating_distance']) for r in (fextra or {}).get('ORD', {}).get('rows', [])])})
    # P7
    if all(have.values()):
        p7 = {}
        changed = []
        for s in LAWS:
            p7[s] = {pop: laws[s]['least_distance'][pop] for pop in POPS}
            for pop in POPS:
                ld = laws[s]['least_distance'][pop]
                if not (ld['full'] == ld['c1'] == ld['c2']):
                    changed.append('%s %s' % (s, pop))
        preds.append({'id': 'P7', 'prediction': 'The two coarser looks: whether they change any least distance (open).',
                      'verdict': ('they change the least distance for: %s' % changed) if changed else
                      'they change no least distance', 'numbers': p7})
    # P8
    if all(have.values()):
        found = []
        tested = []
        for s in LAWS:
            for r in laws[s]['whole_structure_renamings']:
                if r['tested']:
                    tested.append('%s %s round %d (%d knots)' % (s, r['start'], r['round'], r['knots']))
                    if r['exists']:
                        found.append('%s %s' % (s, r['start']))
        preds.append({'id': 'P8', 'prediction': 'No whole structure has a renaming onto itself that carries a parent place to '
                      'a place that is not one.', 'verdict': 'holds' if not found else 'fails',
                      'numbers': 'final P2 structures tested (at most 2,000 knots): %d (%s); with such a renaming: %s' % (
                          len(tested), '; '.join(tested), found or 'none')})
    out = {'checks': {'pass': chk['pass'], 'check_a': {k: chk['check_a'][k] for k in (
        'n_looks', 'pairs_compared', 'pairs_agreeing', 'pairs_alike_by_every_renaming', 'pairs_alike_by_code',
        'looks_by_kind', 'looks_by_knots', 'sources')}, 'check_a_hand_pairs': chk['check_a']['hand_pairs'],
        'check_b': [{k: r[k] for k in ('R', 'knots', 'threshold_found', 'expected_threshold', 'exact',
                                       'alike_at_full', 'alike_at_c1', 'alike_at_c2')} for r in b['rows']],
        'check_c': {'n_plants': chk['check_c']['n_plants'], 'pass': chk['check_c']['pass'],
                    'plants_by_law': chk['check_c']['plants_by_law']}},
           'checks_extra_vf2': {k: ext[k] for k in ('pass', 'pairs', 'agree', 'stats', 'knots_range')} if ext else None,
           'knot_tests': kt, 'rules': rules, 'laws': laws, 'predictions': preds, 'stop_rule': stop,
           'addition_whole_structures_under_2000_knots': wextra, 'addition_whole_structure_pairs': wpairs,
           'addition_followed_pair': fextra, 'checks_extra_vf2_full': ext}
    PC.write_json(PC.OUT / 'summary.json', out)
    (PC.OUT / 'summary.md').write_text(markdown(out))
    print('summary written;', len(preds), 'predictions')


def markdown(o):
    L = []
    L.append('# PARENTS-FROM-HOLDERS-20261124-001A-E001: summary')
    L.append('')
    L.append('Generated by `pfh_summarize.py` from the run outputs in this folder. Readings are in the experiment\'s '
             '`deviations.md`. "Mixed class": a class of alike looks holding a parent place and a place that is not one.')
    L.append('')
    L.append('## Predictions')
    L.append('')
    L.append('| # | Prediction | Verdict | Numbers |')
    L.append('| --- | --- | --- | --- |')
    for p in o['predictions']:
        num = p['numbers'] if isinstance(p['numbers'], str) else json.dumps(p['numbers'])
        L.append('| %s | %s | %s | %s |' % (p['id'], p['prediction'], p['verdict'], num.replace('|', '/')))
    L.append('')
    L.append('## Stop rule, by law (full look)')
    L.append('')
    L.append('| Law | least d, P1 and P2 | least d, P2 (guard count there) | least d on P2 by round | followed pair: least separating distance by round | how it behaves | pairs at d = 6 exchanged by a whole structure |')
    L.append('| --- | --- | --- | --- | --- | --- | --- |')
    for s, st in o['stop_rule'].items():
        fol = ', '.join('%s: %s' % kv for kv in st['followed_pair_separating_distance_by_round'])
        beh = st['followed_pair_separating_distance_grows']
        if 'addition_followed_pair_by_round' in st:
            fol += '; added pair (item 40): ' + ', '.join('%s: %s' % kv for kv in st['addition_followed_pair_by_round'])
            beh += '; added pair: ' + st['addition_followed_pair_pattern']
        L.append('| %s | %s | %s (%s) | %s | %s | %s | %s |' % (
            o['laws'][s]['law'], st['least_distance_P1_and_P2_pooled'] or 'none', st['least_distance_P2'] or 'none',
            st['guard_count_P2_at_that_distance'], ', '.join('%s: %s' % kv for kv in st['least_distance_P2_by_round'].items()),
            fol, beh, st['whole_structure_pairs_at_d6']))
    L.append('')
    L.append('## Least distance with no confusable pair (full / C1 / C2)')
    L.append('')
    L.append('| Law | P1 | P1 reference rounds | P1 serial states | P2 | P1 and P2 |')
    L.append('| --- | --- | --- | --- | --- | --- |')
    for s, l in o['laws'].items():
        if l is None:
            L.append('| %s | not run | | | | |' % s)
            continue
        cells = []
        for pop in POPS:
            ld = l['least_distance'][pop]
            cells.append(' / '.join(str(ld[v]) if ld[v] else 'none' for v in VARS))
        L.append('| %s | %s |' % (l['law'], ' | '.join(cells)))
    L.append('')
    L.append('## Mixed classes and guard counts by distance (full look)')
    L.append('')
    for s, l in o['laws'].items():
        if l is None:
            continue
        L.append('### %s' % l['law'])
        L.append('')
        L.append('| Population | d | places P / C / S | classes | mixed | groups of the mixed classes | guard count |')
        L.append('| --- | --- | --- | --- | --- | --- | --- |')
        for pop in ('P1', 'P2', 'P1P2'):
            for r in l['by_distance'][pop]['full']:
                pl = r['places']
                L.append('| %s | %d | %d / %d / %d | %d | %d | %s | %d |' % (
                    pop, r['d'], pl['P'], pl['C'], pl['S'], r['classes'], r['mixed'],
                    ', '.join('%s %d' % (g, n) for g, n in sorted(r['groups'].items())) or '-', r['guard']))
        L.append('')
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    main()
