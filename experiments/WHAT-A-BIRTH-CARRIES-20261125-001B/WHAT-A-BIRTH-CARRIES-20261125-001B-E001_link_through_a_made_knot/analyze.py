"""Verdicts, predictions and the reported readings from the raw records: writes summary.json.

  python -B analyze.py
"""
import sys

sys.dont_write_bytecode = True

import glob
import json
import os
from collections import Counter, defaultdict

import common
from common import log
import verdicts

RUNS = ('1a', 'P1', '1b', '1c', 'U1', 'M2')
CORE_STARTS = ('Ring(5,3)', 'D2(5,3)', 'Ring(7,3)')
RINGS = ('Ring(5,3)', 'Ring(5,3)+1', 'D2(5,3)', 'Ring(7,3)')


def load(run):
    return list(common.read_jsonl('run%s.jsonl.gz' % run))


def gate():
    rows = []
    for p in sorted(glob.glob(common.out_path('G_engine_*_of_5.jsonl'))):
        rows += [json.loads(l) for l in open(p)]
    rest = json.load(open(common.out_path('G_rest.json')))
    return {'engine_runs': len(rows), 'engine_equal': sum(r['equal'] for r in rows),
            'distinct_cases': len({r['case'] for r in rows}),
            'gate_listing_equal': rest['gate_listing']['equal'],
            'gate_listing_lines': rest['gate_listing']['lines_compared'],
            'attribution_records': [(r['name'], r['got']['class'], r['equal']) for r in rest['attribution_records']],
            'passed': len(rows) == 648 and all(r['equal'] for r in rows) and rest['gate_listing']['equal']
            and all(r['equal'] for r in rest['attribution_records'])}


def c0():
    recs = load('C0')
    neg = [r for r in recs if r['id'].startswith('C0-neg')]
    pos = [r for r in recs if r['id'].startswith('C0-pos')]
    pl = [r for r in recs if r['id'].startswith('C0-planted')]
    cn, cp = Counter(), Counter()
    for r in neg:
        cn.update(verdicts.item_summary(r))
    for r in pos:
        cp.update(verdicts.item_summary(r))
    Vp = verdicts.law_verdicts(pos)
    return {'negative': {'items': len(neg), 'meeting_pairs': cn['meeting'], 'no_meeting_pairs': cn['no meeting'],
                         'knot_fail_items': sum(1 for r in neg if verdicts.ktA_fails(r))},
            'positive': {'items': len(pos), 'counts': dict(cp),
                         'laws_link_found': sorted('%s|%s' % k for k, o in Vp.items() if o['B1-link'] == 'found'),
                         'laws_dependence_found': sorted('%s|%s' % k for k, o in Vp.items()
                                                         if o['B1-dependence'] == 'found'),
                         'knot_fail_items': sum(1 for r in pos if verdicts.ktA_fails(r))},
            'planted': [{'id': r['id'], 'class_a4': r['class_a4'], 'class_a1': r['class_a1'],
                         'meeting_a4': r['runs']['a=4']['meeting'],
                         'linking_a4': [(x['knot'], x['made'], x['class']) for x in r['runs']['a=4']['linking']],
                         'passes': r['passes']} for r in pl],
            'passed': cn['meeting'] == 0 and cp['strict'] > 0 and cp['dep: differs through the meeting'] > 0
            and all(r['passes'] for r in pl)}


def knot_totals(recs_by_run):
    out = {}
    for run, recs in recs_by_run.items():
        c = Counter()
        where = Counter()
        for r in recs:
            kt = r.get('knot_test_A')
            if kt:
                c['run A verdicts'] += kt['verdicts']
                c['run A fails'] += kt['n_fail']
                c['run A disagree'] += kt['n_disagree']
                c['run A untested'] += kt['n_untested']
                if kt['n_fail']:
                    where['%s|%s' % (r['law_id'], r['start']) + '|' + r['law']['knot_law']] += kt['n_fail']
            c['undecided: knot test not run'] += r.get('untested_differing_pairs', 0)
            for p in r.get('pairs', []):
                kb = p.get('knot_test_barred')
                if isinstance(kb, dict):
                    c['barred runs tested'] += 1
                    c['barred verdicts'] += kb['verdicts']
                    c['barred fails'] += kb['n_fail']
                    if kb['n_fail']:
                        where['barred|%s|%s|%s' % (r['law_id'], r['start'], r['law']['knot_law'])] += kb['n_fail']
                for kl in p.get('knot_test_lasting') or []:
                    c['lasting reruns tested'] += 1
                    c['lasting verdicts'] += kl['verdicts']
                    c['lasting fails'] += kl['n_fail']
                    if kl['n_fail']:
                        where['lasting|%s|%s|%s' % (r['law_id'], r['start'], r['law']['knot_law'])] += kl['n_fail']
        out[run] = {'counts': dict(c), 'fails_where': dict(where)}
    return out


def case_detail(recs, law_id, starts):
    """The registered readings of one law's cases with a meeting only through made knots and a course difference."""
    out = {}
    for r in recs:
        if r['law_id'] != law_id or r['start'] not in starts:
            continue
        key = '%s|%s' % (r['start'], r['law']['knot_law'])
        c = Counter()
        ex = None
        for p in r['pairs']:
            if not p['strict']:
                continue
            c['strict'] += 1
            c['s=%d' % p['s']] += 1
            c['meeting round %d' % p['meeting_round']] += 1
            c['linking knots %d' % len(p['linking'])] += 1
            for x in p['linking']:
                c['linking knot made in round %d' % x['made']] += 1
            c['ancestral'] += p['ancestral']
            c['ancestral every member'] += p['ancestral_every_member']
            c['start knot holds a linking distinction'] += p['start_knot_holds_linking_distinction']
            ch = p.get('checks') or {}
            if ch:
                c['symmetry X<->Y fixing linking knots: %s' % ch['symmetry_exchanging_X_Y_fixing_linking_knots']['answer']] += 1
                c['start knot in a barred run link: %s' % ch['start_knot_in_linking_set_of_a_barred_run']] += 1
            if not p['course_differs']:
                c['course equal'] += 1
                continue
            c['course differs'] += 1
            c['course first differs round %d' % p['course_first_differs_round']] += 1
            a = p['attribution']
            c['attribution %s' % a['class']] += 1
            c['attribution accepted'] += p['attribution_accepted']
            c['first differing value: round %d, %s' % (a['round'], a['kind'])] += 1
            c['meets against does not meet'] += p['meets_against_does_not_meet']
            sb = p.get('subsets') or {}
            if sb:
                c['bar classes: %s' % json.dumps(sb['classes_by_size'])] += 1
                c['no-meeting subsets sizes: %s' % sorted(len(A) for A in sb['no_meeting_subsets'])] += 1
                c['m: %s (%s)' % (sb['m'].get('verdict'), sb['m'].get('m'))] += 1
                c['how many: %d' % len(sb['how_many'])] += 1
                c['which at equal number: %d' % len(sb['which_at_equal_number'])] += 1
            ls = p.get('lasting') or {}
            c['lasting: %s' % ls.get('verdict')] += 1
            kb = p.get('knot_test_barred')
            if isinstance(kb, dict):
                c['barred knot test: %d verdicts, %d failing' % (kb['verdicts'], kb['n_fail'])] += 0
                c['barred runs tested'] += 1
                c['barred fails'] += kb['n_fail']
            ys = p.get('y_side_knots_first_differing_demand')
            if ys:
                for y in ys['y_side']:
                    c['y-side: %s %s of %d parents, round %d (%s)' % (y['descent'], y['kind'], len(y['parents']),
                                                                     y['round'], y['run'])] += 1
            if ex is None:
                ex = {'s': p['s'], 'X': p['X'], 'Y': p['Y'], 'meeting_round': p['meeting_round'],
                      'meeting_how': p['meeting_how'], 'linking': p['linking'], 'attribution': a,
                      'y_side': ys, 'subsets': sb, 'lasting': ls, 'checks': ch,
                      'knot_test_barred': kb, 'course_first_differs_round': p['course_first_differs_round']}
        out[key] = {'counts': dict(c), 'example': ex, 'knot_test_A': r['knot_test_A']}
    return out


def main():
    common.check_frozen()
    fam = common.load('family.json')
    recs = {r: load(r) for r in RUNS}
    V = {r: verdicts.law_verdicts(recs[r]) for r in RUNS}
    S = {'gate': gate(), 'C0': c0()}
    S['verdicts'] = {r: {'%s|%s' % k: v for k, v in V[r].items()} for r in RUNS}
    S['minimal'] = verdicts.minimal_laws([V['1a'], V['1b'], V['1c']], fam)
    S['knot_test'] = knot_totals({**recs, 'C0': load('C0')})
    S['expected_case'] = case_detail(recs['1a'], 'L10', RINGS)
    S['L02_case'] = case_detail(recs['1a'], 'L02', ('made-4',) + RINGS)
    S['P1_cases'] = {lid: case_detail(recs['P1'], lid, RINGS) for lid in
                     ('PARENT-OWING-PLAIN/CANCEL-OFFSHOOT', 'PARENT-OWING-1/CANCEL-OFFSHOOT')}
    S['U1'] = {lid: case_detail(recs['U1'], lid, ('Ring(5,3)+1+2',)) for lid in ('L02', 'L10')}
    S['N2'] = json.load(open(common.out_path('runN2_comparison.json')))['totals']
    S['P2'] = {m: json.load(open(common.out_path('runP2_x%d_index.json' % m)))['items'] for m in (10, 100)}
    S['run_meta'] = {}
    for r in ('C0',) + RUNS + ('N2',):
        m = json.load(open(common.out_path('run%s_index.json' % r)))
        S['run_meta'][r] = {k: m[k] for k in ('items', 'done', 'cut_at', 'wall_seconds', 'procs')}
    reader = defaultdict(Counter)
    for r in ('1a', '1b', '1c'):
        for rec in recs[r]:
            reader[rec['law_id']].update(rec.get('reader_item4', {}))
    S['reader_item4'] = {k: dict(v) for k, v in reader.items() if v}
    rec_counts = Counter()
    for rec in recs['1a']:
        if rec['law_id'] in ('L00', 'L01', 'L02', 'L03', 'L04', 'L05', 'L06', 'L07', 'L08'):
            c = verdicts.item_summary(rec)
            rec_counts['meeting'] += c['meeting']
            rec_counts['strict'] += c['strict']
            rec_counts['ancestral'] += c['ancestral']
            rec_counts['every member'] += c['ancestral every member']
            rec_counts['strict, course differs'] += c['strict, course differs']
            rec_counts['start knot holds a linking distinction'] += c['start knot holds a linking distinction']
    S['recorded_rations_MET_SOLE'] = dict(rec_counts)
    common.write_json('summary.json', S)
    log('wrote summary.json')


if __name__ == '__main__':
    main()
