"""summary.json and summary.md: one row per prediction, judged by its "Fails when" entry, from the part files.

python -B summarize.py
"""
from __future__ import annotations

import json
import os
from collections import Counter

from dh_common import OUT, write, read_out, log
import dh_engine as E


def maybe(name):
    p = os.path.join(OUT, name)
    return read_out(name) if os.path.exists(p) or os.path.exists(p + '.gz') else None


def fmt(x):
    return json.dumps(x, separators=(', ', ': '))


def main():
    p0, p1, p2, p3 = maybe('part0.json'), maybe('part1.json'), maybe('part2.json'), maybe('part3.json')
    p4, p5, p6, p7, p8 = maybe('part4.json'), maybe('part5.json'), maybe('part6.json'), maybe('part7.json'), maybe('part8.json')
    preds = []

    def add(pid, mark, verdict, numbers, note=''):
        preds.append({'id': pid, 'mark': mark, 'verdict': verdict, 'numbers': numbers, 'note': note})

    # ---------------------------------------------------------------- C0
    if p0:
        c = p0['c_planted_error']
        nums = {'gate pairs passed': '%d of %d (%d structures, names included)' % (
                    sum(r['pass'] for r in p0['a_gate']['pairs']), p0['a_gate']['n_pairs'], p0['a_gate']['structures_compared']),
                'extra: HOLD against own_round': p0['a_gate']['extra_HOLD_against_own_round']['pass'],
                'H1 (four forms)': p0['b_hand_cases']['H1']['pass'], 'T (registered and swap)': p0['b_hand_cases']['T']['pass'],
                'planted error as worded': '%d of %d runs (%d without a birth in round 2)' % (c['pass_as_worded_on'], c['n'], c['skipped']),
                'planted error where (a), (b′), (c), (d) are met': '%s on %d runs' % (c['pass_where_conditions_hold'], c['runs_where_all_four_conditions_hold']),
                'planted error, place-rule formula (deviations 28)': '%d of %d' % (c['changed_equals_formula_on'], c['n']),
                'sixteen holding runs': '%d of 16 births by round equal; %d of 16 no unequal parents' % (
                    p0['d_holding_runs']['equal'], p0['d_holding_runs']['no_unequal_parents']),
                'witnesses W1, W2, W2b': p0['e_witnesses']['pass'],
                'shortness on usable places': '%s: %d runs, 0 mismatches required; %d member-rounds holding barred places; '
                                              '%d rounds where the all-loose count gives another short set' % (
                    p0['f_shortness']['pass'], p0['f_shortness']['n'], p0['f_shortness']['member_rounds_holding_barred_places'],
                    p0['f_shortness']['rounds_where_all_loose_reading_differs']),
                'numberings (exact isomorphism)': '%d runs, %d differences' % (p0['g_numberings']['runs'], p0['g_numberings']['differences'])}
        v = 'Confirmed' if p0['pass'] else ('Fails as worded (part 0 (c): %d runs, each with a condition failing); '
                                        'every other check is confirmed' % (c['n'] - c['pass_as_worded_on'])
                                        if p0['pass_every_check_but_c_as_worded'] else 'Fails')
        add('C0', 'check', v, nums, 'The planted error\'s "exactly" is right only where the four conditions are met (deviations 28).')
    else:
        add('C0', 'check', 'not run', {})
    # ---------------------------------------------------------------- P1
    if p3:
        add('P1', 'check', 'Confirmed' if p3['P1'] else 'Fails',
            {'cases': p3['cases'], 'renaming exists under the base law': '%d of %d' % (p3['base_exists'], p3['cases']),
             'renaming exists under a count form': '%d of %d' % (p3['forms_exist'], 3 * p3['cases'])})
    else:
        add('P1', 'check', 'not run', {})
    # ---------------------------------------------------------------- P2
    if p5:
        nums = {ln: '%d reach three parent steps; %d of them fail somewhere; exceptions %s' % (
            v['reach_three_parent_steps (part 1)'], v['reach_three_and_fail'], v['exceptions (reach three, no failing birth)'][:10])
            for ln, v in p5['by_law'].items()}
        add('P2', 'replication', 'Confirmed' if p5['P2'] else 'Fails', nums)
    else:
        add('P2', 'replication', 'not run', {})
    # ---------------------------------------------------------------- P3-P6
    for pid, key in (('P3', 'P3'), ('P4', 'P4'), ('P5', 'P5'), ('P6', 'P6')):
        app = 0
        fails = []
        if p1:
            for k, v in p1['armw'].items():
                app += v[key + '_applicable']
                fails += [['part 1', k, i] for i in v[key + '_fail']]
        if p4:
            for r in p4['runs']:
                for f, row in r['forms'].items():
                    if f == 'base':
                        continue
                    if row.get(key) is not None:
                        app += 1
                        if row[key] is False:
                            fails.append(['part 4', r['start'], r['law'], f, r['knot_law']])
        mark = 'check'
        if not p1 and not p4:
            add(pid, mark, 'not run', {})
        else:
            add(pid, mark, ('Confirmed' if not fails else 'Fails') + ('' if (p1 and p4) else ' (on the parts run)'),
                {'runs to which it applies': app, 'runs where it fails': len(fails), 'listing': fails[:20]})
    # ---------------------------------------------------------------- P7
    if p4:
        app = 0
        bad = []
        goes_on = []
        for r in p4['runs']:
            for f in ('PB', 'BB'):
                row = r['forms'][f]
                app += 1
                if not row['P7']:
                    bad.append([r['start'], r['law'], f, r['knot_law']])
                if row.get('goes_on_after_base_closes'):
                    goes_on.append([r['start'], r['law'], f, r['knot_law'], row['base_closes_at']])
        closes = sum(1 for r in p4['runs'] for f in ('PB', 'BB') if r['forms'][f]['base_closes_at'] is not None)
        add('P7', 'check', 'Confirmed' if not bad else 'Fails',
            {'barred-form runs': app, 'with a difference before the round': len(bad), 'listing': bad[:20],
             'runs whose base law closes': closes, 'of them, the barred form goes on growing': len(goes_on),
             'those runs': goes_on})
    else:
        add('P7', 'check', 'not run', {})
    # ---------------------------------------------------------------- P8, P8b
    if p2:
        rc = p2['restart_control']
        hi = p2['handins']
        ok = rc['equal'] == rc['tests'] and hi['as_stated'] == hi['conditions_hold']
        add('P8', 'check', 'Confirmed' if ok else 'Fails',
            {'restart control': '%d of %d equal (by stage %s); %d not applicable (the run ended)' % (
                rc['equal'], rc['tests'], rc['by_stage'], rc['not_applicable']),
             'arm-W hand-ins': '%d applicable; (a), (c), (d) met through round 1 on %d; as stated on %d' % (
                 hi['applicable'], hi['conditions_hold'], hi['as_stated']),
             'otherwise': hi['otherwise']})
        cr = p2['census_restarts']
        a = cr['from_223']
        bl = a['by_law']
        lo = min(v['prefix'] for v in bl.values())
        hi_ = max(v['prefix'] for v in bl.values())
        pos = [v['prefix'] for v in bl.values() if v['prefix']]
        totals = (a['prefix'] == 515 and cr['from_220_kept']['prefix'] == 515 and cr['same_515_from_both'] and
                  a['complete'] == 4 and a['within_only'] == 511 and a['subset'] == 1234)
        ok = totals and (lo, hi_) == (145, 234)
        zero = [k for k, v in bl.items() if not v['prefix']]
        if ok:
            verdict = 'Confirmed'
        elif totals and (min(pos), max(pos)) == (145, 234):
            verdict = ('Fails as worded on one by-law count: %s reaches 0, outside the stated "145 to 234 by law"; '
                       'every total is confirmed and the range is met on the other %d laws' % (', '.join(zero), len(pos)))
        else:
            verdict = 'Fails'
        add('P8b', 'replication', verdict,
            {'reached within round 1 by a prefix (from the 223)': [a['prefix'], 515],
             'from the 220 kept': [cr['from_220_kept']['prefix'], 515], 'the same set': cr['same_515_from_both'],
             'by law (least, greatest)': [[lo, hi_], [145, 234]],
             'by law': {k: v['prefix'] for k, v in bl.items()},
             'after a complete round 1': [a['complete'], 4], 'within round 1 only': [a['within_only'], 511],
             'any subset': [a['subset'], 1234]})
    else:
        add('P8', 'check', 'not run', {})
        add('P8b', 'replication', 'not run', {})
    # ---------------------------------------------------------------- P9
    if p6:
        add('P9', 'replication', 'Confirmed' if p6['P9'] else 'Fails',
            {'rows': [[v['start'], v['law'], v['form'], 'T=%s' % v['T_base'], 'q=%s' % v['q'],
                       'hypotheses met %s' % v['hypotheses_hold'], 'predicted %s' % v['predicted_period'],
                       'observed %s' % v['observed_period']] for v in p6['formula']]})
    else:
        add('P9', 'replication', 'not run', {})
    # ---------------------------------------------------------------- P10
    if p7:
        bt = p7.get('beyond_prefix_totals', {})
        cut = p7.get('cut')
        bad_beyond = (bt.get('parity', {}).get('fail', 0) + bt.get('parity', {}).get('disagree', 0) +
                      bt.get('nae', {}).get('fail', 0) + bt.get('nae', {}).get('disagree', 0))
        v = 'Confirmed' if p7['P10'] else 'Fails'
        if cut:
            v += (' on the prefix of %d of %d runs (cut at 30 minutes); %d more runs finished beyond the prefix '
                  '(%s); %d not run' % (p7['prefix_jobs'], p7['jobs'],
                                        len(p7['finished_beyond_prefix (run past the registered order of the cut, '
                                               'reported separately)']),
                                        'no failing or disputed knot' if bad_beyond == 0 else 'with failing or disputed knots',
                                        len(p7['not_run'])))
        add('P10', 'check (parity); replication (not-all-equal)', v,
            {'prefix: parity': p7['parity'], 'prefix: not-all-equal': p7['nae'],
             'beyond the prefix': bt, 'not run (first 10)': p7.get('not_run', [])[:10]})
    else:
        add('P10', 'check / replication', 'not run', {})
    # ---------------------------------------------------------------- P11
    if p1:
        diffs = []
        for ln, row in p1['compare_with_disclosed'].items():
            for k, (mine, disc) in row.items():
                if k == 'labelled_share_percent':
                    continue
                if disc is not None and mine != disc:
                    diffs.append([ln, k, mine, disc])
        ca = p1['condition_a']
        if ca['kept_with_a'] != 133:
            diffs.append(['condition (a)', 'kept', ca['kept_with_a'], 133])
        six = p1['condition_a']['six_knots']
        if six and six['a_on_kept'] != 804:
            diffs.append(['condition (a) six knots', 'kept', six['a_on_kept'], 804])
        done6 = p1['six_sample']['done']
        if done6 == 3000:
            for ln, disc in (('R3W', 493), ('C3W', 493), ('C3WF', 493), ('F1W', 184)):
                mine = p1['six_sample']['by_law'][ln]['counted']
                if mine != disc:
                    diffs.append(['six-knot sample', ln, mine, disc])
        jc = maybe('part1_joint_closing.json')
        joint = {}
        for key, v in p1['armw'].items():
            row = [v['joint_stratum'], v['joint_disclosed']]
            if jc:
                j = jc['by_law_form'][key]
                row += [j['joint_closing_knot_own_places_left_out'], j['joint_both_places_of_closing_knot_left_out']]
            joint[key] = row
        add('P11', 'replication', ('Confirmed' if not diffs else 'Fails') +
            ('' if done6 == 3000 else ' (the six-knot sample bullet: cut at %d of 3,000, not judged)' % done6),
            {'counts against the disclosed (law: [this run, disclosed])': p1['compare_with_disclosed'],
             'condition (a)': [ca['kept_with_a'], 133], 'condition (a), six knots': [six['a_on_kept'] if six else None, 804],
             'six-knot sample (waiting bases), counted of the prefix run': {
                 ln: '%d of %d (disclosed %d of 3,000)' % (p1['six_sample']['by_law'][ln]['counted'], done6, d)
                 for ln, d in (('R3W', 493), ('C3W', 493), ('C3WF', 493), ('F1W', 184))},
             'joint stratum (reported): [every place (this run), scratch, closing knot own side left out, '
             'both sides left out]': joint,
             'H-F1R counted ending at the first round with no birth': [p1['laws']['H-F1R|parity']['alt_stop']['counted'], 368],
             'differences': diffs})
    else:
        add('P11', 'replication', 'not run', {})
    # ---------------------------------------------------------------- P12, P13
    if p4:
        pu = []
        cost = []
        for r in p4['runs']:
            row = r['forms']['PU']
            pu.append([r['start'], r['law'], r['knot_law'], row['P12_against_base']['births_base'],
                       row['P12_against_base']['births'], row['P12_against_base']['end_base'], row['P12_against_base']['end']])
            for f in ('PB', 'BB'):
                cost.append([r['start'], r['law'], f, r['knot_law'], r['forms'][f]['cost']['share_s_positive'],
                             r['forms'][f]['cost']['mean_s']])
        same = sum(1 for x in pu if x[3] == x[4])
        add('P12', 'reported', 'reported', {'usable-form runs': len(pu), 'births by round equal to the base law': same,
                                            'differ': len(pu) - same})
        sh = [c[4] for c in cost if c[4] is not None]
        add('P13', 'reported', 'reported', {
            'PB share of new knots with s > 0 (pooled over runs)': _pooled(p4, 'PB'),
            'BB share': _pooled(p4, 'BB'),
            'share by run, least and greatest': [min(sh), max(sh)] if sh else None})
    else:
        add('P12', 'reported', 'not run', {})
        add('P13', 'reported', 'not run', {})
    # ---------------------------------------------------------------- P14, P15
    if p1:
        g = {ln: p1['laws'][ln + '|parity']['counted_greatest'] for ln in [L.name for L in E.LAWS]}
        add('P14', 'reported', 'reported', {'greatest difference among counted starts, by law': g,
                                            'greatest over 3 on any run (parity)': sum(p1['laws'][L.name + '|parity']['greatest_over_3'] for L in E.LAWS)})
        add('P15', 'reported', 'reported', {ln: round(100 * p1['laws'][ln + '|parity']['counted_labelled_share'], 2)
                                            for ln in [L.name for L in E.LAWS]})
    else:
        add('P14', 'reported', 'not run', {})
        add('P15', 'reported', 'not run', {})
    # ---------------------------------------------------------------- P16
    if p8 or p1:
        nums = {}
        if p8:
            nm = p8['named']
            wr = Counter()
            ws = Counter()
            for r in nm:
                for k in E.KINDS:
                    wr[k] += r['registered']['place_rule_last_by_kind'][k][1]
                    ws[k] += r['parents_differ_swap']['place_rule_last_by_kind'][k][1]
            nums['parents-differ swap, named: wrong places by kind (registered / swap)'] = {k: [wr[k], ws[k]] for k in E.KINDS}
            cl = [r for r in nm if r['closing_swap'].get('closing_knots')]
            nums['closing swap, named parity runs with a closing birth'] = len(cl)
            nums['closing knots failing the parity test after their round'] = '%d of %d' % (
                sum(k['fails_parity_after_its_round'] for r in cl for k in r['closing_swap']['closing_knots']),
                sum(len(r['closing_swap']['closing_knots']) for r in cl))
            st = p8['stopping']
            nums['stopping swap, named arm R: runs that differ'] = [[r['start'], r['law'], r['knot_law']] for r in st if r['differ']]
            cs = p8['census_parents_differ_swap']
            if isinstance(cs, dict):
                nums['parents-differ swap on the census'] = {
                    'prefix of census starts': cs['prefix_starts'], 'kept starts in the prefix': cs['kept_in_prefix'],
                    'cut': cs['cut'], 'finished beyond the prefix': len(cs['finished_beyond_prefix']),
                    'not run': len(cs['not_run']), 'runs with an error': cs['errors'][:20]}
                if p1:
                    import gzip
                    with gzip.open(os.path.join(OUT, 'part1_runs.json.gz'), 'rt') as f:
                        p1rows = {r['idx']: r for r in json.load(f)['census_rows']}
                    for key in p1['armw']:
                        j = sum(1 for r in cs['rows'] if r['runs'].get(key, {}).get('right_on_every_structure'))
                        jr = sum(1 for r in cs['rows'] if p1rows[r['idx']]['armw'][key]['right_on_every_structure'])
                        nums.setdefault('joint stratum on the prefix [registered rule, swap]', {})[key] = [jr, j]
                        p3f = [r['idx'] for r in cs['rows'] if r['runs'].get(key, {}).get('P3') is False]
                        if p3f:
                            nums.setdefault('swap: runs where (a), (b′), (c), (d) are met and a place is wrong', {})[key] = p3f[:10]
            else:
                nums['parents-differ swap on the census'] = 'not run'
        if p1:
            nums['P11 counted under the other stopping reading'] = {L.name: [p1['laws'][L.name + '|parity']['counted'],
                                                                             p1['laws'][L.name + '|parity']['alt_stop']['counted']]
                                                                    for L in E.LAWS}
        add('P16', 'reported', 'reported', nums)
    else:
        add('P16', 'reported', 'not run', {})

    walls = {}
    for i, p in enumerate((p0, p1, p2, p3, p4, p5, p6, p7, p8)):
        if p is None:
            walls['part %d' % i] = 'not run'
        else:
            walls['part %d' % i] = p.get('seconds', (p.get('meta') or {}).get('seconds'))
    summary = {'predictions': preds, 'wall_seconds': walls}
    write('summary.json', summary)
    lines = ['# DESCENT-HELD-20261125-001A-E001: summary', '',
             'One row per prediction of the pre-registration, judged by its "Fails when" entry. Numbers from the part '
             'files beside this one. Readings: the experiment folder\'s deviations.md.', '',
             '| # | Mark | Verdict | Numbers |', '| --- | --- | --- | --- |']
    for p in preds:
        nums = '; '.join('%s: %s' % (k, v if isinstance(v, (str, int, float, bool)) or v is None else fmt(v))
                         for k, v in p['numbers'].items())
        nums = nums.replace('|', '/')
        if len(nums) > 1600:
            nums = nums[:1600] + ' ... (see summary.json)'
        lines.append('| %s | %s | %s | %s |' % (p['id'], p['mark'], p['verdict'], nums))
    lines += ['', 'Wall time by part (seconds): ' + ', '.join('%s %s' % (k, v) for k, v in walls.items()), '']
    with open(os.path.join(OUT, 'summary.md'), 'w') as f:
        f.write('\n'.join(lines))
    log('summary written')


def _pooled(p4, f):
    pos = sum(r['forms'][f]['s_positive'] for r in p4['runs'])
    tot = sum(r['forms'][f]['new_knots'] for r in p4['runs'])
    return round(pos / tot, 3) if tot else None


if __name__ == '__main__':
    main()
