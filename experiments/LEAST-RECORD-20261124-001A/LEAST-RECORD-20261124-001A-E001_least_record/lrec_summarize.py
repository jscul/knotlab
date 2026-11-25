"""Verdicts of LEAST-RECORD-20261124-001A: summary.json and summary.md (one row per prediction, the table of costs).

    python -B lrec_summarize.py

Reads the outputs of runs 1-7 and, for P4, P5 and P6, the class tables that lrec_run.py left in the session scratchpad.
"""
from __future__ import annotations

import gzip
import json
import pickle
from array import array
from collections import defaultdict

import pfh_common as PC
from pfh_struct import STAMP_TABLE

LAWS = ('F1O', 'F1R', 'R3W', 'ORD')
TWO_VALUED = ('NOT-MEMBER', 'HAS-CHILD', 'JOIN', 'START-KNOT', 'GENERATION-MOD-2')


def load(name):
    p = PC.OUT / name
    return json.loads(p.read_text()) if p.exists() else None


def classes(law, stamp):
    p = PC.SCRATCH / ('classes_%s_%s.pkl.gz' % (law, stamp))
    if not p.exists():
        return None
    meta = pickle.load(gzip.open(p))
    kinds = array('b')
    kinds.frombytes(meta['kinds'])
    sid = array('i')
    sid.frombytes(meta['sid_of'])
    cls = {}
    for d in range(1, 7):
        c = array('i')
        c.frombytes(meta['cls']['%d' % d])
        cls[d] = c
    return {'labels': meta['labels'], 'kinds': kinds, 'sid_of': sid, 'cls': cls}


def same_partition(a, b, items):
    m1 = {}
    m2 = {}
    for i in items:
        if m1.setdefault(a[i], b[i]) != b[i] or m2.setdefault(b[i], a[i]) != a[i]:
            return False
    return True


def table(stamp, law, pop):
    return load('%s_%s_%s.json' % (stamp, law, pop))


def least(stamp, law, sub, key='least_distance_rule_counted'):
    for pop in ('P1', 'P2', 'P1P2', 'P3'):
        t = table(stamp, law, pop)
        if t and sub in t[key]:
            return t[key][sub]
    return 'not run'


def row_at(stamp, law, sub, d):
    for pop in ('P1', 'P2', 'P1P2', 'P3'):
        t = table(stamp, law, pop)
        if t and sub in t['tables']['d=%d' % d]:
            return t['tables']['d=%d' % d][sub]
    return None


def by_round(stamp, law, prefix, key='least_distance_rule_counted'):
    pop = 'P2' if prefix.startswith('P2') else ('P3' if prefix.startswith('P3') else 'P1')
    t = table(stamp, law, pop)
    if not t:
        return None
    out = {}
    for p, v in t[key].items():
        if p.startswith(prefix + ' round ') and p.endswith(' | holds'):
            out[int(p.split(' round ')[1].split(' |')[0])] = v
    return dict(sorted(out.items()))


def mixed_by_d(stamp, law, sub):
    out = []
    for d in range(1, 7):
        r = row_at(stamp, law, sub, d)
        out.append(None if r is None else r['mixed_classes'])
    return out


def guards_at(stamp, law, sub, d):
    r = row_at(stamp, law, sub, d) if d else None
    return None if r is None else [r['guard_count'], r['guard_count_2'], r['guard_count_2_variant']]


def main():
    chk = load('checks.json')
    gens = load('generations.json')
    rules = load('rules.json')
    stamps = [s[0] for s in STAMP_TABLE]
    mod_m = ['GENERATION-MOD-%d' % m for m in sorted(set(gens['moduli_for_run_6'].values()))]
    preds = []
    notes = {}

    preds.append({'id': 'Checks', 'prediction': 'The four checks of run 1 hold.',
                  'verdict': 'holds' if chk['pass'] else 'fails',
                  'numbers': '(a) earlier checks with NONE: %d pairs, %d disagreements, thresholds %s, %d plants pass; '
                             'stamped addition %d pairs, %d disagreements. (b) constant stamp: same partition as NONE at '
                             'every d on %s; NONE reproduces the earlier tables: %s. (c) generations %s; kinds as stated: %s. '
                             '(d) %d planted stamps, all pass: %s' % (
                      chk['check_a']['earlier_check_a']['pairs_compared'],
                      len(chk['check_a']['earlier_check_a']['disagreements']),
                      [r['threshold_found'] for r in chk['check_a']['earlier_check_b']['rows']],
                      chk['check_a']['earlier_check_c']['n_plants'],
                      chk['check_a_addition_stamped']['pairs_compared'],
                      len(chk['check_a_addition_stamped']['disagreements']),
                      list(chk['check_b']['laws']), {k: v['earlier_tables_reproduced'] for k, v in chk['check_b']['laws'].items()},
                      chk['check_c']['generations'], chk['check_c']['kinds_as_stated'], chk['check_d']['n_plants'],
                      chk['check_d']['pass'])})

    # P1
    eq = all(r['births_with_unequal_parents'] == 0 for r in gens['P1_P2'] if r['condition_holds'])
    nb = sum(r['births'] for r in gens['P1_P2'] if r['condition_holds'])
    rr = {}
    ok_rule = True
    for law in LAWS:
        q = rules['by_law'][law]['GENERATION-MOD-3']['populations']
        for p in ('P1 | holds', 'P2 | holds'):
            if p in q:
                rr['%s %s' % (law, p)] = '%d/%d' % (q[p]['reproduced'], q[p]['places'])
                ok_rule &= q[p]['all_reproduced']
    preds.append({'id': 'P1', 'prediction': 'Where the condition holds, every birth\'s parents have equal generations in every '
                  'structure of P1 and P2, and with GENERATION-MOD-3 the rule "the other holder is a parent exactly when its '
                  'stamp is one less, modulo 3" recovers the parents at distance 1.',
                  'verdict': 'holds' if (eq and ok_rule) else 'fails',
                  'numbers': 'births with unequal parents where the condition holds: %d of %d; places reproduced by the '
                             'rule: %s' % (sum(r['births_with_unequal_parents'] for r in gens['P1_P2'] if r['condition_holds']),
                                           nb, rr)})
    # P2
    fails_on = gens['condition_fails_on']
    scc = [r for r in gens['P1_P2'] if r['start'] == 'SCC'][0]
    r2 = [b for b in scc['unequal_births'] if b['round'] == 2 and 0 in b['parent_generations'] and 1 in b['parent_generations']]
    q = rules['by_law']['R3W']['GENERATION-MOD-3']['populations']
    wrong = q.get('P2 | fails', {}).get('failures', [])
    wrong_start = [f for f in wrong if f['generation_of_knot'] == 2 and f['generation_of_other_holder'] == 0
                   or f['generation_of_knot'] == 0 and f['generation_of_other_holder'] == 2]
    v = fails_on == [['R3W', 'SCC']] and bool(r2) and bool(wrong_start)
    preds.append({'id': 'P2', 'prediction': 'The condition fails on the start-clause counterexample and on no other registered '
                  'start; there a birth of round 2 has parents of generations 0 and 1, and the modulo-3 rule gets its place '
                  'to the start knot wrong.', 'verdict': 'holds' if v else 'fails',
                  'numbers': 'condition fails on %s (round, waiting start knot, acting start knot: %s); births with unequal '
                             'parents there: %s; places the modulo-3 rule gets wrong on P2 there: %s of %s, by kind %s, e.g. %s' % (
                      fails_on, [(w['round'], w['waiting_start_knot'], w['acting_start_knot']) for w in scc['condition_fails_at']],
                      [(b['knot'], b['round'], b['parents'], b['parent_generations'], b['generation']) for b in scc['unequal_births']],
                      q.get('P2 | fails', {}).get('places', 0) - q.get('P2 | fails', {}).get('reproduced', 0),
                      q.get('P2 | fails', {}).get('places'), q.get('P2 | fails', {}).get('failures_by_kind'),
                      [(f['structure'], f['knot'], f['other_holder'], f['kind'], f['stamp_of_knot'], f['stamp_of_other_holder'])
                       for f in wrong[:4]])})
    # P3
    allok = {}
    for law, rs in rules['by_law'].items():
        for p, qq in rs['GENERATION']['populations'].items():
            if ' | ' not in p:
                allok['%s %s' % (law, p)] = (qq['reproduced'], qq['places'])
    v = all(a == b for a, b in allok.values())
    preds.append({'id': 'P3', 'prediction': 'With GENERATION shown the parents are recovered at distance 1 everywhere, P3 '
                  'included.', 'verdict': 'holds' if v else 'fails', 'numbers': 'places reproduced: %s' % allok})
    # P4
    p4 = {}
    v = True
    for law in LAWS:
        a = classes(law, 'NONE')
        b = classes(law, 'NOT-MEMBER')
        if a is None or b is None:
            p4[law] = 'not run'
            v = False
            continue
        items = range(len(a['kinds']))
        p4[law] = {d: same_partition(a['cls'][d], b['cls'][d], items) for d in range(1, 7)}
        v &= all(p4[law].values())
    preds.append({'id': 'P4', 'prediction': 'NOT-MEMBER changes no class of looks at any distance.',
                  'verdict': 'holds' if v else 'fails', 'numbers': 'same partition as NONE, by law and distance: %s' % p4})
    # P5
    p5 = {}
    ok_pair = True
    for law in ('F1O', 'F1R', 'ORD'):
        c = classes(law, 'HAS-CHILD')
        if c is None:
            continue
        found = _three_knot_pairs(law, c)
        p5[law] = found
        ok_pair &= bool(found) and all(f['alike_at'] == [1, 2, 3, 4, 5, 6] for f in found)
    sep = {}
    for st in ('START-KNOT', 'GENERATION-MOD-2', 'NONE'):
        for law in ('F1O', 'F1R', 'ORD'):
            c = classes(law, st)
            if c is not None:
                sep['%s %s' % (law, st)] = [f['alike_at'] for f in _three_knot_pairs(law, c)][:1]
    a = classes('F1O', 'NONE')
    b = classes('F1O', 'HAS-CHILD')
    same2 = None
    if a and b:
        items = [i for i in range(len(a['kinds'])) if a['labels'][a['sid_of'][i]].startswith('TWO-KNOT F1O round')]
        same2 = {d: same_partition(a['cls'][d], b['cls'][d], items) for d in range(1, 7)}
    v = ok_pair and same2 is not None and all(same2.values())
    preds.append({'id': 'P5', 'prediction': 'HAS-CHILD leaves a confusable pair at every distance in the three-knot structure, '
                  'and changes no class of looks on the complete rounds of the two-knot start under (FLOOR1, '
                  'CANCEL-OFFSHOOT).', 'verdict': 'holds' if v else 'fails',
                  'numbers': 'the pair (B\'s place to A, the offshoot\'s place to A), distances at which alike under '
                             'HAS-CHILD: %s; the same pair under other stamps: %s; HAS-CHILD and NONE give the same partition of '
                             'the two-knot start\'s rounds under (FLOOR1, CANCEL-OFFSHOOT) at d = 1..6: %s' % (
                      {k: [(f['structure'], f['alike_at']) for f in vv] for k, vv in p5.items()}, sep, same2)})
    # P6
    c = classes('ORD', 'GENERATION-MOD-2')
    hyper = None
    if c:
        sids = [i for i, l in enumerate(c['labels']) if l == 'LONE-FOUR ORD round 4']
        hyper = {}
        for d in range(1, 7):
            P = set()
            Q = set()
            for i in range(len(c['kinds'])):
                if c['sid_of'][i] in sids:
                    (P if c['kinds'][i] == 0 else Q).add(c['cls'][d][i])
            hyper[d] = len(P & Q)
    t = table('GENERATION-MOD-2', 'F1O', 'P2')
    r12 = None
    if t:
        r12 = [t['tables']['d=%d' % d].get('P2 round 12', {}).get('mixed_classes') for d in range(1, 7)]
    v = hyper is not None and all(hyper[d] > 0 for d in range(1, 7)) and r12 is not None and all(
        (m or 0) > 0 for m in r12[:4])
    preds.append({'id': 'P6', 'prediction': 'GENERATION-MOD-2 leaves a confusable pair at every distance from 1 to 6 in the '
                  'finished structure of 16 knots under ordinary growth, and under (FLOOR1, CANCEL-OFFSHOOT) on the grown '
                  'structures of twelve rounds at distances up to 4 at least.', 'verdict': 'holds' if v else 'fails',
                  'numbers': 'mixed classes within the finished LONE-FOUR structure (the 4-dimensional hypercube, the '
                             'literature\'s name) by d: %s; mixed classes in P2 round 12 under (FLOOR1, CANCEL-OFFSHOOT) by d: '
                             '%s' % (hyper, r12)})
    # P7
    p7 = {}
    for st in ('START-KNOT', 'JOIN', 'PARENT-COUNT', 'HAS-CHILD+START-KNOT'):
        p7[st] = {}
        for law in LAWS:
            ld = least(st, law, 'P1P2 | holds')
            p7[st][law] = {'least_rule_P1P2_holds': ld,
                           'least_no_pair_P1P2_holds': least(st, law, 'P1P2 | holds', 'least_distance_no_confusable_pair'),
                           'least_rule_P1_holds': least(st, law, 'P1 | holds'),
                           'least_rule_P2_holds': least(st, law, 'P2 | holds'),
                           'guards_at_least': guards_at(st, law, 'P1P2 | holds', ld) if isinstance(ld, int) else None,
                           'by_P2_round': by_round(st, law, 'P2'), 'mixed_P1P2_holds_by_d': mixed_by_d(st, law, 'P1P2 | holds')}
    preds.append({'id': 'P7', 'prediction': 'START-KNOT, JOIN, PARENT-COUNT and HAS-CHILD with START-KNOT: the least distance '
                  'with a rule, by law and population, with both guard counts and by round (open).', 'verdict': 'reported',
                  'numbers': p7})
    # P8
    p8 = {}
    for st in TWO_VALUED:
        p8[st] = {law: least(st, law, 'P1P2 | holds') for law in LAWS}
    every = [st for st, v in p8.items() if all(isinstance(x, int) for x in v.values())]
    preds.append({'id': 'P8', 'prediction': 'Whether any stamp of two values in the table recovers the parents, with a guard '
                  'count that is not zero, on every structure of every start where the condition holds (open; the thread and '
                  'the advisor expect none).', 'verdict': ('yes: %s' % every) if every else
                  'no two-valued stamp does under every law', 'numbers': 'least distance with a rule that counts on P1 and P2 '
                  'where the condition holds, by stamp and law: %s' % p8})
    # P9
    unequal = [(r['law_short'], r['start'], r['births_with_unequal_parents']) for r in gens['P3']]
    anyu = any(u[2] for u in unequal)
    mod3_p3 = {law: (rules['by_law'][law]['GENERATION-MOD-3']['populations']['P3']['reproduced'],
                     rules['by_law'][law]['GENERATION-MOD-3']['populations']['P3']['places']) for law in PC.HOLD_LAWS}
    preds.append({'id': 'P9', 'prediction': 'Under holding (P3) some birth has parents whose generations differ, and the '
                  'modulo-3 rule fails there.', 'verdict': 'holds' if anyu else 'fails',
                  'numbers': 'births with unequal parents by law and start: %s; places the modulo-3 rule reproduces on P3: %s'
                             % (unequal, mod3_p3)})

    # the table of costs
    costs = []
    for key, values, what, needs, rewrite in STAMP_TABLE + [(m, m.split('-')[-1], 'generation modulo %s (run 6)' %
                                                            m.split('-')[-1], "its parents' stamps", 'no') for m in mod_m]:
        row = {'stamp': key, 'values': values, 'what_is_written': what, 'writer_needs': needs,
               'old_knot_rewritten': rewrite, 'by_law': {}}
        for law in LAWS:
            ld = least(key, law, 'P1P2 | holds')
            row['by_law'][law] = {
                'least_distance_rule_P1P2_holds': ld,
                'least_distance_no_pair_P1P2_holds': least(key, law, 'P1P2 | holds', 'least_distance_no_confusable_pair'),
                'least_distance_rule_P1_holds': least(key, law, 'P1 | holds'),
                'least_distance_rule_P2_holds': least(key, law, 'P2 | holds'),
                'least_distance_rule_by_P2_round_holds': by_round(key, law, 'P2'),
                'least_distance_rule_by_P1_reference_round_holds': by_round(key, law, 'P1 reference'),
                'guards_at_least_distance_P1P2_holds': guards_at(key, law, 'P1P2 | holds', ld) if isinstance(ld, int) else None,
                'mixed_classes_P1P2_holds_by_d': mixed_by_d(key, law, 'P1P2 | holds'),
            }
            if law == 'R3W':
                row['by_law'][law]['where_the_condition_fails'] = {
                    'least_distance_no_pair_P1P2_fails': least(key, law, 'P1P2 | fails',
                                                               'least_distance_no_confusable_pair'),
                    'least_distance_rule_P1P2_fails': least(key, law, 'P1P2 | fails'),
                    'mixed_classes_P1P2_fails_by_d': mixed_by_d(key, law, 'P1P2 | fails')}
        row['P3'] = {law: {'least_distance_rule': least(key, law, 'P3'),
                           'least_distance_no_pair': least(key, law, 'P3', 'least_distance_no_confusable_pair'),
                           'mixed_by_d': mixed_by_d(key, law, 'P3'),
                           'by_round': by_round(key, law, 'P3')} for law in PC.HOLD_LAWS}
        pr = {}
        for law in LAWS + PC.HOLD_LAWS:
            pf = load('pairs_%s_%s.json' % (key, law))
            if pf:
                pr[law] = {p: (None if v is None else {
                    'distance': v['distance'], 'group': v['group'],
                    'structure_knots': [v['parent_place']['structure_knots'], v['other_place']['structure_knots']],
                    'look_knots': v['look_at_d']['knots'],
                    'parent_place': [v['parent_place']['structure'], v['parent_place']['knot'], v['parent_place']['distinction']],
                    'other_place': [v['other_place']['structure'], v['other_place']['knot'], v['other_place']['distinction'],
                                    v['other_place']['kind']],
                    'whole_structure': v.get('exchanged_by_a_renaming_of_the_whole_structure')})
                    for p, v in pf['smallest_pairs'].items()}
        row['smallest_pairs'] = pr
        rr = None
        if rules and key in rules['rules']:
            rr = {'rule': rules['rules'][key],
                  'reproduced': {law: {p: '%d/%d' % (q['reproduced'], q['places'])
                                       for p, q in rules['by_law'][law][key]['populations'].items()
                                       if p in ('P1 | holds', 'P2 | holds', 'P1 | fails', 'P2 | fails', 'P3')}
                                 for law in rules['by_law'] if key in rules['by_law'][law]}}
        row['rule'] = rr
        costs.append(row)
    out = {'predictions': preds, 'costs': costs, 'generations': {k: gens[k] for k in (
        'condition_fails_on', 'moduli_for_run_6', 'equal_generations_wherever_the_condition_holds')},
        'run3': [{k: r[k] for k in ('law_short', 'start', 'condition_holds', 'births', 'births_with_unequal_parents',
                                     'greatest_difference')} for r in gens['P1_P2'] + gens['P3']],
        'mismatch_births': len(gens['mismatch_births']), 'checks_pass': chk['pass']}
    PC.write_json(PC.OUT / 'summary.json', out)
    (PC.OUT / 'summary.md').write_text(markdown(out))
    print('summary written')


def _three_knot_pairs(law, c):
    """The three-knot structures of the two-knot start (B - A - a1, a1 an offshoot of A) among P1's serial states, and
    the distances at which the pair (B's place to A, a1's place to A) is alike."""
    import pfh_pop as PP
    out = []
    seen = set()
    first = {}
    for k, sd in enumerate(c['sid_of']):
        if sd not in first:
            first[sd] = k
    lab_index = {l: i for i, l in enumerate(c['labels'])}
    for cid, start, fam, r in PP.serial_configs():
        if start != 'TWO-KNOT' or PC.LAW_SHORT[fam] != law:
            continue
        SR = PP.SerialRun(cid, start, fam, r)
        for i, st in enumerate(SR.states):
            T = SR.struct(i)
            if T.n != 3 or st['extra'] is not None:
                continue
            c3 = [x for x in range(3) if T.parents[x]]
            if len(c3) != 1 or T.parents[c3[0]] != (0,):
                continue
            label = '%s state %d' % (cid, i)
            if label not in lab_index:
                continue
            sid = lab_index[label]
            a1 = c3[0]
            off = first[sid]
            items = T.items
            iB = [k for k, (x, e) in enumerate(items) if x == 1 and T.other(x, e) == 0][0]
            ia = [k for k, (x, e) in enumerate(items) if x == a1 and T.other(x, e) == 0][0]
            alike = [d for d in range(1, 7) if c['cls'][d][off + iB] == c['cls'][d][off + ia]]
            key = (T.n, tuple(alike))
            if key in seen:
                continue
            seen.add(key)
            out.append({'structure': label, 'alike_at': alike, 'B_place_kind': T.kinds[iB], 'a1_place_kind': T.kinds[ia]})
    return out


def markdown(o):
    L = ['# LEAST-RECORD-20261124-001A-E001: summary', '',
         'Generated by `lrec_summarize.py` from the run outputs in this folder; readings are in the experiment\'s '
         '`deviations.md`. "Mixed class": a class of alike looks holding a parent place and a place that is not one. '
         '"Holds"/"fails": the condition of the start (no start knot waits while a start knot it meets acts).', '',
         '## Predictions', '', '| # | Prediction | Verdict | Numbers |', '| --- | --- | --- | --- |']
    for p in o['predictions']:
        num = p['numbers'] if isinstance(p['numbers'], str) else json.dumps(p['numbers'])
        L.append('| %s | %s | %s | %s |' % (p['id'], p['prediction'], p['verdict'], num.replace('|', '/')))
    L += ['', '## The table of costs (P1 and P2 pooled where the condition holds; least distance with a rule that counts)',
          '', '| Stamp | Values | Writer needs | Old knot rewritten | F1O | F1R | R3W | ORD | where the condition fails (R3W, SCC): least d with no pair | P3: least d with a rule (H-C3W, H-R3W, H-F1R, H-F1O) |',
          '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in o['costs']:
        cells = []
        for law in LAWS:
            b = r['by_law'][law]
            ld = b['least_distance_rule_P1P2_holds']
            g = b['guards_at_least_distance_P1P2_holds']
            cells.append('%s%s' % (ld if ld is not None else 'none',
                                   (' (guards %d, %d)' % (g[0], g[1])) if g else ''))
        fail = r['by_law']['R3W'].get('where_the_condition_fails', {}).get('least_distance_no_pair_P1P2_fails')
        p3 = ', '.join(str(r['P3'][law]['least_distance_rule']) for law in PC.HOLD_LAWS)
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (r['stamp'], r['values'], r['writer_needs'],
                                                           r['old_knot_rewritten'], ' | '.join(cells), fail, p3))
    L += ['', '## Least distance with a rule that counts, by P2 round (condition holds)', '']
    for r in o['costs']:
        parts = []
        for law in LAWS:
            br = r['by_law'][law]['least_distance_rule_by_P2_round_holds']
            parts.append('%s: %s' % (law, br))
        L.append('- **%s**: %s' % (r['stamp'], '; '.join(parts)))
    L += ['', '## Run 3: generations', '', '| Law | Start | Condition | Births | With unequal parents | Greatest difference |',
          '| --- | --- | --- | --- | --- | --- |']
    for r in o['run3']:
        L.append('| %s | %s | %s | %d | %d | %s |' % (r['law_short'], r['start'], 'holds' if r['condition_holds'] else 'fails',
                                                      r['births'], r['births_with_unequal_parents'], r['greatest_difference']))
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    main()
