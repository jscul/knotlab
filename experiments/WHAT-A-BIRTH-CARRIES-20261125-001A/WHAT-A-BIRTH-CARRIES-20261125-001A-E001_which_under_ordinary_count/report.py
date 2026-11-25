"""summary.json and summary.md of WHAT-A-BIRTH-CARRIES-20261125-001A-E001, from summary_raw.json (analyze.py)."""
import sys

sys.dont_write_bytecode = True

import json
from collections import Counter

import common
import wbc

TAKE = {'OLDEST': 'take-the-oldest', 'NEWEST': 'take-the-newest'}
KL = {'nae': 'not-all-equal', 'parity': 'parity'}
LAWS = (('OLDEST', 'nae'), ('OLDEST', 'parity'), ('NEWEST', 'nae'), ('NEWEST', 'parity'))


def load():
    with open(common.out_path('summary_raw.json')) as f:
        return json.load(f)


def cell(r1, ch, kl, h, a, b):
    for c in r1['cells']:
        if (c['take'], c['knot_law'], c['h'], c['a'], c['b']) == (ch, kl, h, a, b):
            return c
    return None


def disj_text(cmp_):
    if cmp_['verdict'] == 'undecided':
        return 'undecided (%d runs read fewer than 2 rounds after s)' % cmp_['undecided_runs']
    by = cmp_['by_prefix']
    parts = ['%s%s' % (R, 'd' if v['disjoint'] else 'n') for R, v in sorted(by.items())]
    return '%s through round %d (by prefix: %s)' % (cmp_['verdict'], cmp_['prefix'], ', '.join(parts))


def meet_text(ps):
    c = ps['counts']
    n = c.get('pairs', 0)
    s = '%d pairs: both meet %d, same round %d, same meeting %d' % (n, c.get('both_meet', 0), c.get('same_round', 0),
                                                                     c.get('same_meeting', 0))
    if c.get('no_meeting_in_one'):
        s += ', no meeting in one run %d' % c['no_meeting_in_one']
    if ps['meeting_gaps']:
        s += ', gaps %s' % ps['meeting_gaps']
    return s


def attr_text(ps):
    c = ps['counts']
    a = ps['attribution']
    s = 'courses differ on %d; ' % c.get('courses_differ', 0)
    s += ', '.join('%s %d' % (k, v) for k, v in sorted(a.items())) if a else 'no attribution'
    if ps['first_entry']:
        fe = Counter()
        for k, v in ps['first_entry'].items():
            fe[k] += v
        s += '; first entry: ' + ', '.join('%s %d' % (k.replace("'", ''), v) for k, v in sorted(fe.items()))
    if c.get('values_differ_courses_equal'):
        s += '; values differ with courses equal on %d' % c['values_differ_courses_equal']
    return s


def nu_note(c):
    if c.get('numberings_run', 0) < c.get('numberings', 0):
        return ' [among %d numberings run, %d not run]' % (c['numberings_run'], c['numberings'] - c['numberings_run'])
    return ''


def predictions(D):
    S = D['S']
    r1 = S['run1']
    rows = []
    g = S['gate']
    rows.append(('Q0', 'check', 'Gate: 648 runs equal to the fold engine; the listing; the 4 records; 100 symmetric pairs',
                 'holds' if D['q0'] else 'FAILS',
                 '%d/%d runs equal; listing %s (%d lines); records %s; symmetric %d/%d identical' % (
                     g['engine_equal'], g['engine_runs'], 'reproduced' if g['listing_equal'] else 'differs',
                     g['listing_lines'], '4/4 as written' if all(x[1] for x in g['records']) else 'differ',
                     g['symmetric_identical'], g['symmetric_pairs'])))
    # Q1
    ch1 = r1['checks']
    sh = ch1['short']
    nae_short = sum(v for k, v in sh.items() if "'nae'" in k)
    par_bad = sum(v for k, v in sh.items() if "'parity'" in k and 'False' in k)
    par_ok = sum(v for k, v in sh.items() if "'parity'" in k and 'True' in k)
    b1 = S.get('run1b', {})
    eq = b1.get('equal_to_run1', {})
    nae_eq = sum(v for k, v in eq.items() if "'nae', True" in k)
    nae_ne = sum(v for k, v in eq.items() if "'nae', False" in k)
    par_ne = sum(v for k, v in eq.items() if "'parity', False" in k)
    b_short_nae = 0
    b_short_par_bad = 0
    for tr in ('CANCEL-OFFSHOOT', 'CANCEL-WAIT'):
        if tr in b1:
            for k, v in b1[tr]['checks']['short'].items():
                if "'nae'" in k:
                    b_short_nae += v
                elif 'False' in k:
                    b_short_par_bad += v
    r2short = sum(len(x['short']) for x in S.get('run2', {}).get('runs', []))
    q1 = nae_short == 0 and par_bad == 0 and b_short_nae == 0 and b_short_par_bad == 0 and nae_ne == 0 and \
        r2short == 0 and bool(eq)
    rows.append(('Q1', '(b; S1)', 'No member short after round 1 under not-all-equal (runs 1, 1b, 2); under parity '
                 'only after an implied birth; run 1b equals run 1 under not-all-equal',
                 'holds' if q1 else ('not run' if not eq else 'FAILS'),
                 'run 1: short after round 1 under not-all-equal %d, under parity %d after an implied birth and %d '
                 'not; run 1b: under not-all-equal %d, under parity not after an implied birth %d; run 2: %d; '
                 'run 1b equal to run 1 under not-all-equal %d, differing %d (under parity, where run 1 was run, '
                 'differing %d)' % (nae_short, par_ok, par_bad, b_short_nae, b_short_par_bad, r2short, nae_eq, nae_ne,
                                    par_ne)))
    # Q2
    s3reg = [x for x in S['registered']['S3'] if x['take'] == 'OLDEST']
    q2 = (not ch1['q2_fail']) and ch1['meet2_a_ge_1'] == ch1['a_ge_1'] and all(x['x_births_D_ok'] for x in s3reg)
    rows.append(('Q2', '(b; S3, S4)', 'J takes e, D = f = 2 + M, 5 + M places, every run with a ≥ 1; registered '
                 'numbering and OLDEST: every round-2 birth from X only has D = 2 + M; meeting round 2 for a ≥ 1',
                 'holds' if q2 else 'FAILS',
                 'run 1: S4 as registered on %d of %d runs (a = 0 included); J values on %d runs with a ≥ 1, %d '
                 'failing; meeting round 2 on %d of %d; registered OLDEST round-2 X births D = 2 + M on %d of %d' % (
                     ch1['s4_ok'], ch1['runs'], ch1['a_ge_1'], len(ch1['q2_fail']), ch1['meet2_a_ge_1'],
                     ch1['a_ge_1'], sum(x['x_births_D_ok'] for x in s3reg), len(s3reg))))
    # Q3
    bad = []
    n_cells = 0
    n_pairs = 0
    n_j = 0
    for c in r1['cells']:
        h, a, b = c['h'], c['a'], c['b']
        if c['M_a'] == c['M_b']:
            continue
        n_cells += 1
        ps = c['pairs']
        npair = ps['counts'].get('pairs', 0)
        n_pairs += npair
        alld = c['compare']['verdict'] == 'disjoint' and all(v['disjoint'] for v in c['compare']['by_prefix'].values())
        jj = sum(v for k, v in ps['first_entry'].items() if "'J'" in k)
        tm = ps['attribution'].get('through the meeting', 0)
        n_j += min(jj, tm)
        if not alld or jj != npair or tm != npair:
            bad.append('%s/%s h=%d (%d,%d): %s; J first %d/%d, through the meeting %d' % (
                c['take'], c['knot_law'], h, a, b, c['compare']['verdict'], jj, npair, tm))
    pn = r1.get('per_nu', [])
    top = [x for x in pn if x['verdict'] != 'not read' and x['top_equal']]
    top_ok = [x for x in top if x['verdict'] == 'handed in one value' and x['J_demand_r2_induces'] and
              x['first_inducing'] and x['first_inducing'].get('is_J') and x['first_inducing']['step'] == 6 and
              x['first_inducing']['round'] == 2]
    q3 = not bad and len(top_ok) == len(top)
    rows.append(('Q3', '(b; S4)', 'Pairs with M(h, a) ≠ M(h, b): disjoint on every prefix from round 2; first '
                 'differing entry J\'s demand at round 2, through the meeting; J\'s demand induces P wherever '
                 '(h − 1, h) has equal courses (handed in one value, a count)',
                 'holds' if q3 else 'FAILS',
                 '%d cells, %d pairs; failing cells %d%s; J\'s round-2 demand first and through the meeting on %d '
                 'pairs; numberings with (h − 1, h) equal: %d, J\'s demand induces P on %d' % (
                     n_cells, n_pairs, len(bad), (' (' + '; '.join(bad[:6]) + ')') if bad else '', n_j, len(top),
                     len(top_ok))))
    # Q3' and Q3''
    qp = []
    okp = True
    for kl in ('nae', 'parity'):
        for h in (3, 4):
            c = cell(r1, 'OLDEST', kl, h, h - 1, h)
            by = c['compare'].get('by_prefix', {})
            for R, v in sorted(by.items()):
                if int(R) <= 3 and v['disjoint']:
                    okp = False
            qp.append('%s h=%d: %s' % (KL[kl], h, disj_text(c['compare'])))
    rows.append(("Q3'", '(b; S5)', '(h − 1, h) under OLDEST: not disjoint on prefixes up to round 3 (round 4: c)',
                 'holds' if okp else 'FAILS', '; '.join(qp)))
    qn = []
    for kl in ('nae', 'parity'):
        for h in (3, 4):
            c = cell(r1, 'NEWEST', kl, h, h - 1, h)
            if c is None:
                qn.append('%s h=%d: not run' % (KL[kl], h))
                continue
            qn.append('%s h=%d: %s%s' % (KL[kl], h, disj_text(c['compare']), nu_note(c)))
    rows.append(("Q3''", '(c)', '(h − 1, h) under NEWEST: no prediction', 'reported', '; '.join(qn)))
    # Q4
    fh = r1['follows_h']
    fh_b = [x for x in fh if x['a'] >= 1]
    fh_ok = all(x['compare']['verdict'] == 'disjoint' for x in fh_b)
    nu_ok = True
    nu_txt = []
    for c in r1['cells']:
        if c['a'] == 0 and c['b'] >= 1:
            if c['compare']['verdict'] != 'disjoint':
                nu_ok = False
                nu_txt.append('%s/%s h=%d b=%d %s' % (c['take'], c['knot_law'], c['h'], c['b'], c['compare']['verdict']))
    fh0 = ['%s/%s %s' % (x['take'], x['knot_law'], x['compare']['verdict']) for x in fh if x['a'] == 0]
    dc = ['%s/%s h=%d: %d' % (x['take'], x['knot_law'], x['h'], x['distinct']) for x in r1['distinct_courses']]
    rows.append(('Q4', '(b) and (c)', 'Follows h at a = 1 … 3 (b); needs the second pattern\'s members usable for '
                 'every a ≥ 1 (b); follows h at a = 0 and the number of distinct courses (c)',
                 'holds' if fh_ok and nu_ok else 'FAILS',
                 'follows h at a = 1 … 3: %d of %d disjoint; needs usable: %s; (c) follows h at a = 0: %s; (c) distinct '
                 'courses over the class: %s' % (
                     sum(x['compare']['verdict'] == 'disjoint' for x in fh_b), len(fh_b),
                     'disjoint in every cell' if nu_ok else '; '.join(nu_txt), ', '.join(fh0), ', '.join(dc))))
    N = S['N']
    rows.append(('Q5', '(b)', 'Negative control: one course from X only over every cell and entry',
                 'holds' if D['q5'] else 'FAILS',
                 '; '.join('%s: %d runs, courses by prefix %s, meetings %d, knot failures %d' % (
                     KL[k], v['runs'], v['courses_by_prefix'], v['meetings'], v['knot_fail']) for k, v in N.items())))
    P = S['P']
    rows.append(('Q6', '(a)', 'Planted control: first difference at round 3, in the round-3 joins\' candidates, '
                 'supplied by Y\'s start knot, a third part (a start knot)', 'holds' if D['q6'] else 'FAILS',
                 '; '.join('%s: course differs first at round %s, entry %s, class %s, X\'s round-3 joins take %s '
                           'against %s' % (c['law'].split('/')[-1], c['criterion']['first_course_difference_round'],
                                           'round-3 join candidates' if c['criterion'][
                                               'entry_is_round3_join_candidates'] else 'other',
                                           c['criterion']['class'], c['criterion'].get('x_round3_joins_takes_made-5'),
                                           c['criterion'].get('x_round3_joins_takes_made-6'))
                           for c in P['comparisons'])))
    kt = r1['knot_test']
    r2f = sum(x['knot_fail'] for x in S.get('run2', {}).get('runs', []))
    rows.append(('Q7', '(a)', 'Every knot passes under both knot laws in runs 1 and 2',
                 'holds' if kt['fails'] == 0 and r2f == 0 and kt['disagree'] == 0 else 'FAILS',
                 'run 1: %d verdicts, %d failing, %d method disagreements, %d untested; run 2: %d failing' % (
                     kt['verdicts'], kt['fails'], kt['disagree'], kt['untested'], r2f)))
    return rows


def write_md(D, rows):
    S = D['S']
    r1 = S['run1']
    L = []
    w = L.append
    w('# WHAT-A-BIRTH-CARRIES-20261125-001A-E001: the course from X only under the ordinary count and MET')
    w('')
    w('Ticket `WHAT-A-BIRTH-CARRIES-20261125-001A`. Generated by `report.py` from `summary_raw.json`. Results are '
      'stated "under take-the-oldest (or take-the-newest), whatever the numbering"; "which second pattern" is how many '
      'of Y\'s members a hand-placed bar left usable. Readings taken are in the experiment folder\'s `deviations.md`. '
      'Where a count separates two cells, the law handed a count over; no pattern read anything.')
    w('')
    nr = r1.get('numberings_run', {})
    n_run = sum(v[0] * (8 if '/h=3' in k else 16) for k, v in nr.items())
    n_all = sum(v[1] * (8 if '/h=3' in k else 16) for k, v in nr.items())
    w('**What was run:** run 1, %d of its %d registered runs: every numbering of every cell except take-the-newest '
      'under not-all-equal at h = 4, read on 185 of 210 numberings; its other %d runs (numberings 185 to 209) were not '
      'run, because the registered sizes understated the cost (the knot test under not-all-equal with take-the-newest '
      'took up to 125 s a run against a registered 4.6 s), so run 1 was cut at the hour and only take-the-newest under '
      'parity was resumed (deviations 26, 28, 32). Cells not run are not negatives. Runs G, N, P, 1b and 2 were run in '
      'full.' % (n_run, n_all, n_all - n_run))
    w('')
    w('## What was run')
    w('')
    w('Numberings run per take, knot law and h (run, registered): %s.' % nr)
    w('')
    w('## Predictions')
    w('')
    w('| # | Kind | Prediction | Verdict | Numbers |')
    w('| --- | --- | --- | --- | --- |')
    for r in rows:
        w('| %s | %s | %s | %s | %s |' % r)
    w('')
    w('## The cells (made-h, take, knot law, pair (a, b))')
    w('')
    w('Three verdicts per cell: the set comparison (RD 4.2, "d" disjoint, "n" not, per prefix); the meeting over the '
      'pairs (ν, A, B) (RD 3.4, 3.6); attribution over the pairs whose courses differ through the compared prefix '
      '(RD 4.3). M = a(h − 1) − a(a − 1)/2.')
    w('')
    w('| start | take | knot law | (a, b) | M | sets of courses | meeting | attribution |')
    w('| --- | --- | --- | --- | --- | --- | --- | --- |')
    for c in r1['cells']:
        w('| made-%d | %s | %s | (%d, %d) | %d, %d | %s%s | %s | %s |' % (
            c['h'], TAKE[c['take']], KL[c['knot_law']], c['a'], c['b'], c['M_a'], c['M_b'], disj_text(c['compare']),
            nu_note(c), meet_text(c['pairs']), attr_text(c['pairs'])))
    for x in r1.get('not_run', []):
        w('| made-%d | %s | %s | every pair | | not run | not run | not run |' % (x['h'], TAKE[x['take']],
                                                                               KL[x['knot_law']]))
    w('')
    w('## Handed in one value, composed over several births, or no difference (RD 4.4), over a = 1 … h')
    w('')
    w('| start | take | knot law | prefix | numberings by verdict | first inducing entry | classes of P per numbering |')
    w('| --- | --- | --- | --- | --- | --- | --- |')
    for x in r1['handed']:
        w('| made-%d | %s | %s | %d | %s | %s | %s |' % (x['h'], TAKE[x['take']], KL[x['knot_law']], x['prefix'],
                                                      x['verdicts'], x['first_inducing'] or '-', x['classes_of_P']))
    w('')
    w('First inducing entry: (round, step, kind, whether it is J). Step 6 is the demand, a count: there the law hands a '
      'count over. Extra counts per row: %s.' % '; '.join('made-%d %s %s: %s' % (
          x['h'], TAKE[x['take']], KL[x['knot_law']], x['extra']) for x in r1['handed']))
    w('')
    w('## The two (h − 1, h) cells in full')
    w('')
    for ch in ('NEWEST', 'OLDEST'):
        w('### Under %s%s' % (TAKE[ch], ' (no prediction, Q3″)' if ch == 'NEWEST' else ' (Q3′)'))
        w('')
        for kl in ('nae', 'parity'):
            for h in (3, 4):
                c = cell(r1, ch, kl, h, h - 1, h)
                if c is None:
                    w('- made-%d, %s, (%d, %d): not run.' % (h, KL[kl], h - 1, h))
                    continue
                ps = c['pairs']
                w('- made-%d, %s, (%d, %d)%s: %s. %s. Courses differ on %d pairs; first course difference by round '
                  '%s; first difference of the values used, by round, %s; %s.' % (
                      h, KL[kl], h - 1, h, nu_note(c), disj_text(c['compare']), meet_text(ps),
                      ps['counts'].get('courses_differ', 0),
                      ps['first_course_difference_round'], ps['first_values_difference_round'], attr_text(ps)))
                hv = [x for x in r1['handed'] if x['take'] == ch and x['knot_law'] == kl and x['h'] == h]
                if hv:
                    w('  At fixed h and ν: %s; first inducing entries %s.' % (hv[0]['verdicts'], hv[0]['first_inducing']))
        w('')
    w('## Follows h, needs the second pattern\'s members usable, the number of distinct courses')
    w('')
    for x in r1['follows_h']:
        w('- follows h at a = %d, %s, %s: %s' % (x['a'], TAKE[x['take']], KL[x['knot_law']], disj_text(x['compare'])))
    for x in r1['distinct_courses']:
        w('- distinct courses over the class, made-%d, %s, %s, through round %d: %d' % (
            x['h'], TAKE[x['take']], KL[x['knot_law']], x['prefix'], x['distinct']))
    w('')
    w('## R9-Which (the claim), per take and knot law')
    w('')
    for k, v in r1['r9'].items():
        w('- %s: holds %s; pairs (a, b) meeting every condition: h = 3 %s, h = 4 %s' % (k, v['holds'], v['h3'], v['h4']))
    w('')
    ch1 = r1['checks']
    w('## The linking knots (RD 3.5, verdict 6 of the claim)')
    w('')
    w('- runs of run 1 with a ≥ 1 and a meeting: %d; linking knots exactly Y\'s start knot (holding e) and, where a '
      'birth of Y\'s took e, X\'s start knot, all start knots no recorded ancestor of both: %d; classes seen %s; '
      'exceptions %s' % (ch1['a_ge_1'], ch1.get('link_ok', 0), ch1.get('link_classes'), ch1.get('link_fail')))
    w('- In FD 5.7\'s classes this is "through a start knot"; on D 5.2\'s third question the case is therefore '
      'supplied.')
    w('')
    w('## Checks of S3 and S5 on the registered numbering')
    w('')
    for x in S['registered']['S3']:
        w('- S3 %s %s made-%d usable %s: members hold h − 1 and owe a − 1, none short: %s; a − 1 joins and h − a '
          'offshoots each: %s; every round-2 birth takes e: %s; round-2 X births D %s (2 + M = %d)' % (
              TAKE[x['take']], KL[x['knot_law']], x['h'], x['usable'], x['members_hold_owe_ok'], x['joins_offshoots_ok'],
              x['every_birth_takes_e'], x['x_births_D'], 2 + x['M']))
    for x in S['registered']['S5']:
        w('- S5 %s made-%d: round-2 births %s (3 + M = %d); every round-3 join takes distinction 1: %s; round-3 join '
          'demand %s; courses equal through round 2 %s, through round 3 %s' % (
              KL[x['knot_law']], x['h'], x['births_r2'], x['expected'], x['round3_joins_take_1'], x['round3_join_D'],
              x['course_equal_r2'], x['course_equal_r3']))
    w('')
    w('## The disclosed sweep on the registered numbering (PR, "Known before the runs", item 1)')
    w('')
    for x in S['registered']['sweep']:
        w('- %s %s, a = %s, made-%d against made-%d: first course difference at round %s (%s)' % (
            TAKE[x['take']], KL[x['knot_law']], x['a'], x['hA'], x['hB'], x['first_difference'], x['course_equal']))
    w('')
    w('## Runs 2, 1b, N, P')
    w('')
    for c in S.get('run2', {}).get('comparisons', []):
        fd = c['fd']
        w('- run 2, %s, made-5 against made-6 (a = h): courses equal by prefix %s; first values difference %s' % (
            c['law'], c['course_equal'], fd and '(round %d, %s, %s)' % (fd['round'], fd['kind'], fd['class'])))
    for x in S.get('run2', {}).get('runs', []):
        w('  - made-%d %s: rounds %d, stop %s, meeting round %s, S4 as registered %s, knot failures %d, %.2f s' % (
            x['h'], x['law'], x['rounds_read'], x['stop'], x['meet'], x['s4'] and x['s4']['all_ok'], x['knot_fail'],
            x['seconds']))
    b1 = S.get('run1b', {})
    if b1:
        w('- run 1b equal to run 1 (fingerprints), by (treatment, knot law, equal): %s' % b1['equal_to_run1'])
        for tr in ('CANCEL-OFFSHOOT', 'CANCEL-WAIT'):
            if tr in b1:
                w('  - %s: S4 as registered on %d of %d runs; short after round 1 %s' % (
                    tr, b1[tr]['checks']['s4_ok'], b1[tr]['checks']['runs'], b1[tr]['checks']['short']))
                for c in b1[tr]['cells']:
                    if c['b'] == c['h']:
                        w('    - made-3 %s %s (%d, %d): %s; %s' % (TAKE[c['take']], KL[c['knot_law']], c['a'], c['b'],
                                                              disj_text(c['compare']), attr_text(c['pairs'])))
        w('  - run 1b knot test: %s' % b1['knot_test'])
    for k, v in S['N'].items():
        w('- N, %s: %s' % (KL[k], v))
    for x in S['P']['runs']:
        w('- P made-%d a = %d %s: rounds %d, stop %s, meeting round %s, knot failures %d' % (
            x['h'], x['a'], x['law'], x['rounds_read'], x['stop'], x['meet'], x['knot_fail']))
    w('')
    w('## The knot test')
    w('')
    w('- run 1: %s' % r1['knot_test'])
    w('- stops in run 1 by (take, knot law, guard limit, rounds read): %s' % r1['stops'])
    w('- seconds per run in run 1 (min, median, max, sum) by take and knot law: %s' % r1['seconds_per_run'])
    w('')
    with open(common.out_path('summary.md'), 'w') as f:
        f.write('\n'.join(L) + '\n')


def main():
    D = load()
    rows = predictions(D)
    out = {'predictions': [{'id': r[0], 'kind': r[1], 'prediction': r[2], 'verdict': r[3], 'numbers': r[4]}
                           for r in rows],
           'gate': D['S']['gate'], 'cells': D['S']['run1']['cells'], 'handed': D['S']['run1']['handed'],
           'r9': D['S']['run1']['r9'], 'follows_h': D['S']['run1']['follows_h'],
           'distinct_courses': D['S']['run1']['distinct_courses'], 'registered': D['S']['registered'],
           'N': D['S']['N'], 'P': D['S']['P']['comparisons'], 'run2': D['S'].get('run2', {}).get('comparisons'),
           'run1b_equal_to_run1': D['S'].get('run1b', {}).get('equal_to_run1'),
           'knot_test_run1': D['S']['run1']['knot_test'], 'checks_run1': D['S']['run1']['checks']}
    common.write_json('summary.json', out)
    write_md(D, rows)
    for r in rows:
        print(r[0], r[3], '|', r[4][:400])


if __name__ == '__main__':
    main()
