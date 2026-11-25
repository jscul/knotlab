"""summary.json and summary.md from the parts' raw files (no recomputation)."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from fractions import Fraction as Fr

import tc

A = tc.ART + '/'


def J(name):
    try:
        return json.load(open(A + name))
    except FileNotFoundError:
        return None


p1, p8e, p2, p3, p4, p5, p6, p7, p8, p9 = (J('part1_gates.json'), J('part8_early_knots.json'), J('part2_lemma.json'),
                                           J('part3_signs.json'), J('part4_examples.json'), J('part5_p9.json'),
                                           J('part6_orders.json'), J('part7_grow_again.json'), J('part8_knots.json'),
                                           J('part9_engine_check.json'))
table = json.load(open(tc.REPO + '/research/TWO-COUNTINGS-20261125-001/table.json'))
md = []


def w(s=''):
    md.append(s)


def F(x):
    return Fr(x) if x is not None else None


# ---------------------------------------------------------------------------------------------- knot lookups
by_label = {}
if p8:
    for s in p8['structures']:
        for lab in s['labels']:
            by_label[lab] = s


def fails_of(s):
    return ['%s (%s)' % (k['knot'], ', '.join(x for x in ('K1', 'K2', 'K3') if not k[x])) for k in s['knots']
            if not k['whole']]


def canon_status(s):
    st = set()
    for k in s['knots']:
        c = k.get('canonical')
        if isinstance(c, dict):
            st.add('canonical: agrees' if c.get('agrees with projection') else 'canonical: DISAGREES')
        else:
            st.add(str(c))
    return '; '.join(sorted(st))


def knots_col(labels):
    """'all', 'fails (...)', or 'not tested' over the structures with these labels."""
    ss = [by_label[l] for l in labels if l in by_label]
    if not ss:
        return 'not tested'
    f = sorted({x for s in ss for x in fails_of(s)})
    meth = sorted({canon_status(s) for s in ss})
    return ('all' if not f else 'fails: ' + '; '.join(f)) + ' [' + ' | '.join(meth) + ']'


# ---------------------------------------------------------------------------------------------- part 2 lookups
items = defaultdict(list)
for it in p2['items']:
    items[it['item']].append(it)


def rows_of(name):
    for it in p2['items']:
        if it['result']['name'] == name:
            return it['result']
    return None


def fin_labels(res):
    out = []
    for v in res['variants']:
        for ab in v['finished']:
            out.append('part 2: %s | %s | %s' % (res['name'], v['label'], ab))
    return out


summary = {'study': 'TWO-COUNTINGS-20261125-001A-E001', 'referee': 'pending', 'parts': {}}

# ---------------------------------------------------------------------------------------------- predictions
pred = []
# P1
p1_ok = []
k = p1['known']
p1_ok.append(('Known 1-3 (part 1 gates)', not p1['failed']))
recs = p2['records']
p1_ok.append(('894 records of part 2 (ONE-PARENT-REREAD 680, rule R 214): the recorded finish value',
              all(r['P1']['reproduced'] for r in recs)))
ten_ok = all(rows_of(n)['variants'][0]['rows']['from the finish']['score_all'] == '55/27'
             for n in ('ten A x2-x3/y3-t', 'ten B x2-x3/y2-t')) and all(
    v['rows']['from the finish']['score_all'] == '55/27' for n in ('ten A x2-x3/y3-t', 'ten B x2-x3/y2-t')
    for v in rows_of(n)['variants'])
p1_ok.append(('the 10-knot 55/27 per history (and 109/54 for the pairs with c)', ten_ok))
e18 = rows_of('eighteen')['variants'][0]
p1_ok.append(('the 18-knot 20/9 hidden, 1,152 allowed states per finished structure, 512 start states',
              e18['rows']['from the finish']['score_all'] == '20/9' and e18['rows']['from the finish']['hidden']
              and set(e18['info']['allowed at the finish'].values()) == {1152} and p2['eighteen start states']['equal']
              and p2['eighteen start states']['engine'] == 512))
e83 = rows_of('eight-thirds case')['variants'][0]['rows']['from the finish']
p1_ok.append(('the 8/3 case: 8/3, not hidden, largest record change 1/6', e83['score_all'] == '8/3'
              and not e83['hidden'] and max(F(e83['change_first']), F(e83['change_second'])) == Fr(1, 6)))
kd = {x['structure']: x for x in p2['keyed']}
k18 = kd['eighteen']['results']
p1_ok.append(('the 18-knot keyed setting: 2/9 between two keyings, 1/9 against a fixed setting (finish, pooled)',
              all(v['from the finish (pooled): largest change of the second record between two g'] == '2/9'
                  and v['from the finish (pooled): largest change against a constant function'] == '1/9'
                  for v in k18.values())))
p1_ok.append(('Known 4: 128 of 512 sign assignments at 20/9 hidden (finish)', p3['summary']['finish: hidden at 20/9'] == 128))
k11 = kd['eleven']['results']
p1_ok.append(('Known 5: the 11-knot keyed setting, up to 2/9 from the finish (pooled), 0 from the start',
              all(v['from the finish (pooled): largest change of the second record between two g'] == '2/9'
                  and v['from the start: largest change of the second record between two g'] == '0'
                  for v in k11.values())))
P1 = all(ok for _, ok in p1_ok)
pred.append(('P1', 'Counting from the finish reproduces every recorded number of parts 2 and 3', 'held' if P1 else 'FAILED',
             '; '.join('%s: %s' % (a, 'yes' if b else 'NO') for a, b in p1_ok)))
# P2
verd = Counter()
p2_rows = []
for it in p2['items']:
    r = it['result']
    for v in r['variants']:
        for cname, row in v['rows'].items():
            if 'verdict' in row:
                verd[row['verdict'].split(',')[0] if row['verdict'].startswith('a hypothesis') else row['verdict']] += 1
                p2_rows.append((r['name'], v['label'], cname, row))
for rec in recs:
    v = rec['variants'][0]
    for cname, row in v['rows'].items():
        if 'verdict' in row:
            verd[row['verdict']] += 1
            p2_rows.append((rec['name'], 'only', cname, row))
p2_fail = [x for x in p2_rows if x[3]['verdict'].startswith('hypotheses met and a score above 2')]
p2_hyp = [x for x in p2_rows if x[3]['verdict'].startswith('a hypothesis fails')]
pooled_ok = all(x['score_all'] == '2' and x['hidden'] for it in p2['items'] if 'pooled' in it['result']
                for kk, x in it['result']['pooled'].items() if 'from the start' in kk)
pred.append(('P2', 'Every structure of parts 2 and 3 that meets the hypotheses scores at most 2 for both outcome classes '
             '(exactly 2 over all two-valued functions) with both records hidden; the unmeasured structures meet them',
             'held' if not p2_fail and not p2_hyp and all(F(r['from the start']['score_all']) == 2 and
                                                           r['from the start']['hidden'] for r in p3['rows'])
             else ('FAILED' if p2_fail else 'held where met; a hypothesis fails on some'),
             '%d lemma verdicts in part 2 (every counting from a common stage before the settings, every structure, '
             'variant and record): %s; part 3: all 512 at exactly 2, hidden, from the start; pooled 10-knot rows from '
             'the start at 2, hidden: %s' % (len(p2_rows), dict(verd), pooled_ok)))
# P3
ex = {x['example']: x for x in p4['examples']}
pred.append(('P3', 'Each example E1-E7 gives a score above 2 or a record changed by the other’s setting',
             'held' if p4['P3 holds'] else 'FAILED',
             '; '.join('%s %s (changes %s, %s)' % (e, ex[e]['score_all'], ex[e]['change_first'], ex[e]['change_second'])
                       for e in ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7'])))
# P4
s6 = p6['summary']
pred.append(('P4', 'Every order in C5’s class scores 2 and is hidden', 'held' if p6['P4 holds'] else 'FAILED',
             '; '.join('%s: %d in the class, %d at 2 hidden' % (l, v['in the class'], v['in the class: at 2 and hidden'])
                       for l, v in s6.items())))
# P6a, P6b
pred.append(('P6a', 'Under Q-OLDEST or Q-NEWEST some renumbered start grows a different finished structure',
             'held' if p7['P6a holds (some renumbering grows a different finished structure)'] else 'FAILED',
             '; '.join('%s: %s' % (s, ', '.join('%s %d of %d different' % (l, v['different finished structures'],
                                                                           sum(v[x] for x in ('different finished structures',
                                                                                              'weighting same',
                                                                                              'weighting by renaming only',
                                                                                              'weighting not decided',
                                                                                              'weighting DIFFERENT'))
                                                                           ) for l, v in c.items()))
                       for s, c in p7['counts'].items())))
p6b_n = p7['P6b: weightings that differ on the same structure']
same_num = sum(v['weighting same'] for c in p7['counts'].values() for v in c.values())
same_ren = sum(v['weighting by renaming only'] for c in p7['counts'].values() for v in c.values())
undec = sum(v['weighting not decided'] + v.get('structure comparison not decided', 0) for c in p7['counts'].values()
            for v in c.values())
pred.append(('P6b', 'Where the finished structures are the same, counting from the start gives the same weighting '
             'carried back; where they differ, "no comparison"', 'held' if p6b_n == 0 else 'FAILED',
             '%d weightings differ on the same structure; %d same by enumeration, %d same by the renaming of the whole '
             'history (too large to enumerate), %d not decided' % (p6b_n, same_num, same_ren, undec)))
# P7
t5 = {}
for n in ('ten A x2-x3/y3-t', 'ten B x2-x3/y2-t'):
    r = rows_of(n)
    t5[n] = {'per history, from the start': [v['rows']['from the start']['score_all'] for v in r['variants']],
             'per history, hidden': [v['rows']['from the start']['hidden'] for v in r['variants']],
             'pooled, from the start': r['pooled']['from the start, pooled (nu uniform over histories)']['score_all'],
             'per history, from the finish': [v['rows']['from the finish']['score_all'] for v in r['variants']],
             'pooled from the finish (TD 3.5)': r['pooled']['from the finish, pooled (each history and state once, TD 3.5)']['score_all'],
             'pooled from the finish (nu uniform)': r['pooled']['from the finish, nu uniform over histories']['score_all']}
p7ok = all(all(x == '2' for x in v['per history, from the start']) and v['pooled, from the start'] == '2'
           for v in t5.values())
pred.append(('P7', 'The 10-knot 55/27 becomes 2 counted from the start, per history and pooled',
             'held' if p7ok else 'FAILED', json.dumps(t5)))
# P8
s3 = p3['summary']
p8ok = (s3['P8: both four-place rules fail K2 in all 512 (start and every finished structure)']
        and s3['P8: the 128 at 20/9 are exactly those with both ties inequalities'])
pred.append(('P8', 'The two four-place rules of the 11-knot structure fail K2 in all 512 sign assignments, and the 128 '
             'at 20/9 are exactly those whose ties are inequalities', 'held' if p8ok else 'FAILED',
             'K2 fails for both in all 512 (start and the four finished structures each): %s; 128 at 20/9 = the 128 with '
             'both ties inequalities: %s; no other rule fails in any of the 512: %s; finish values %s' % (
                 s3['P8: both four-place rules fail K2 in all 512 (start and every finished structure)'],
                 s3['P8: the 128 at 20/9 are exactly those with both ties inequalities'],
                 not s3['other rules failing in the whole (index, structure, rule)'],
                 s3['finish: score values (all two-valued functions, hidden or not)'])))
# P9
pred.append(('P9', 'The counting-from-the-start pair tables decide the next birth count on all 194 not-all-equal types',
             'held' if p5['P9 holds (the tables decide the next birth count)'] else 'FAILED',
             '%d types (%d connected, %d disconnected); %d distinct tables under renaming; groups sharing a table: '
             'named %d, under renaming %d; gates (finish pair counts and totals equal the archive; start tables equal '
             'enumeration up to width 20): %s' % (p5['types'], p5['connected'], p5['disconnected'],
                                                 p5['distinct tables under renaming'],
                                                 len(p5['named: groups of types sharing one table']),
                                                 len(p5['under renaming: groups of types sharing one table']),
                                                 p5['gates pass'])))
summary['predictions'] = [{'id': a, 'prediction': b, 'verdict': c, 'numbers': d} for a, b, c, d in pred]

# ---------------------------------------------------------------------------------------------- write md
w('# Two countings of a structure’s allowed states, side by side: results of TWO-COUNTINGS-20261125-001A-E001')
w()
w('Computed by an engine written from the frozen texts, independent of the drafter’s prototype. Referee pending. '
  'Every weighting here is supplied. "Counting from the finish": each allowed state of the finished structure counts '
  'once. "Counting from the start": each allowed state of the start counts once, and at each birth an old state’s '
  'weight is divided equally among its completions. A rule is called a knot only once it has passed the knot test in '
  'the whole structure. Readings taken: `deviations.md` of the experiment folder. No claim is made about physics, '
  'physical space or time, living things or minds.')
w()
w('**Notes added after an independent check** (the checker\'s report is in the study\'s folder under `checks/`; the result note of the ticket carries the checked numbers). '
  'Names such as "11-knot", "10-knot" and "8-knot" below are the earlier studies\' names for their structures and count rules: some of those rules are not knots in the whole structure (the section on the knot test says which). '
  'In the table, T07\'s knot column applies to 280 of its 680 histories; in the other 400 every rule passes. '
  'T10\'s structures were all checked by the canonical command; the "not run" in its column belongs to the 18-knot structures. '
  'The canonical command ran on 7,406 rules in all, 171 of them in the early run, failing rules among them. '
  'One of the 133 class orders of the smallest gain loses no weight (132 lose some). '
  'In the examples\' table the column headed "Weight kept" gives the weight lost. '
  'The four-correlation score is the literature\'s CHSH form of a Bell inequality, named here once.')
w()
w('## Gates (part 1)')
w()
w('%d checks, %d failed. Brute force equals the engine on the 11-knot and smallest-gain structures (allowed states, '
  'completions, counting from the start); the score’s merged method equals the unmerged one and an enumeration of '
  'both sides’ functions; the parity score equals a direct enumeration; Known 1–3 reproduced.' % (
      len(p1['checks']), len(p1['failed'])))
w()
w('## Predictions')
w()
w('| # | Prediction | Verdict | Numbers |')
w('| --- | --- | --- | --- |')
for a, b, c, d in pred:
    w('| %s | %s | %s | %s |' % (a, b, c, d.replace('|', '/')))
w()
# lemma table
w('## The lemma (C2): each registered structure and example')
w()
w('Scores over all two-valued functions; "par" the signed parity score, "|par|" its absolute form (R 16). Hidden: both '
  'records unchanged by the other’s setting. Verdict for counting from a common stage before the settings.')
w()
w('| Structure | Variant | Counting | Score | par | abs par | Hidden (changes) | Hypotheses failing | Verdict |')
w('| --- | --- | --- | --- | --- | --- | --- | --- | --- |')
for it in p2['items']:
    r = it['result']
    for v in r['variants']:
        for cname, row in v['rows'].items():
            hy = row.get('hypotheses')
            w('| %s | %s | %s | %s | %s | %s | %s (%s, %s) | %s | %s |' % (
                r['name'], v['label'], cname, row['score_all'], row['score_parity'], row['score_parity_abs'],
                'yes' if row['hidden'] else 'no', row['change_first'], row['change_second'],
                ', '.join(hy['fails']) if hy else '', row.get('verdict', '(no verdict: %s)' % (
                    'the finish breaks the premise' if 'finish' in cname else 'the mixed stage is not common'))))
    if 'pooled' in r:
        for kk, x in r['pooled'].items():
            w('| %s | pooled | %s | %s | %s | %s | %s (%s, %s) |  |  |' % (r['name'], kk, x['score_all'], x['score_parity'],
                                                                       x['score_parity_abs'], 'yes' if x['hidden'] else 'no',
                                                                       x['change_first'], x['change_second']))
w()
w('**The records of part 2** (each one history; counting from the part, from after the round, from the finish, and the '
  'two mixed stages):')
w()
w('| Source | Records | From the start | From stage 1 | From the finish (= the record’s number in every record) | '
  'Mixed stages | Verdicts |')
w('| --- | ---: | --- | --- | --- | --- | --- |')
for src in ['ONE-PARENT-REREAD uniform', 'ONE-PARENT-REREAD mixed', 'REREAD-BIRTHS rule R']:
    rs = [r for r in recs if r['record']['source'] == src]

    def cnt(cn):
        return ', '.join('%s%s ×%d' % (a, '' if b else ' not hidden', n) for (a, b), n in Counter(
            (r['variants'][0]['rows'][cn]['score_all'], r['variants'][0]['rows'][cn]['hidden']) for r in rs).most_common())
    w('| %s | %d | %s | %s | %s | %s; %s | %s |' % (
        src, len(rs), cnt('from the start'), cnt('from stage 1'), cnt('from the finish'),
        cnt('mixed stage (the first observer first)'), cnt('mixed stage (the second observer first)'),
        dict(Counter(r['variants'][0]['rows'][c]['verdict'][:45] for r in rs for c in ('from the start', 'from stage 1')))))
w()
w('**The examples (part 4)**, counted from the start (E1 from the finish; E2 from nothing, renormalised):')
w()
w('| Example | Breaks (TD 8.2) | Score | par | Change of the first / second record | Weight kept per setting pair | '
  'Hypotheses found failing | P3 |')
w('| --- | --- | --- | --- | --- | --- | --- | --- |')
for x in p4['examples']:
    hy = x.get('hypotheses (counting from the start)')
    kept = x.get('kept') or x.get('weight lost')
    w('| %s | %s | %s | %s | %s / %s | %s | %s | %s |' % (
        x['example'], x['breaks (TD 8.2)'], x['score_all'], x['score_parity'], x['change_first'], x['change_second'],
        json.dumps(x['kept']) if 'kept' in x else 'lost: ' + json.dumps(x.get('weight lost')),
        (', '.join(hy['fails']) or 'none') if hy else 'not computed (R 25)',
        'above 2 or changed' if x['P3: a score above 2 or a record changed'] else '2 and hidden'))
for x in p4['beside']:
    w('| %s | (beside) | %s |  | %s / %s | %s | %s |  |' % (x['example'], x['score_all'], x.get('change_first', ''),
                                                          x.get('change_second', ''), json.dumps(x.get('kept', x.get('weight lost'))),
                                                          ', '.join(x['hypotheses']['fails']) if 'hypotheses' in x else ''))
w()
w('**Keyed settings** (the first observer keyed, TD 4.5): the largest change of the second record between two functions g '
  '(and against a constant function):')
w()
w('| Structure | Second observer fixed at | From the start | From the finish, pooled | Against a constant (start / finish) |')
w('| --- | --- | --- | --- | --- |')
for x in p2['keyed']:
    for kk, v in x['results'].items():
        w('| %s (%d functions g) | %s | %s | %s | %s / %s |' % (
            x['structure'], v['functions g'], kk[-1], v['from the start: largest change of the second record between two g'],
            v['from the finish (pooled): largest change of the second record between two g'],
            v['from the start: largest change against a constant function'],
            v['from the finish (pooled): largest change against a constant function']))
w()
# orders
w('## Construction orders (part 6)')
w()
w('| List | Orders | In C5’s class | In the class: at 2, hidden | Outside: at 2, hidden | Outside: above 2, hidden | '
  'Outside: above 2, not hidden | Largest hidden outside |')
w('| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |')
for l, v in s6.items():
    rows = [r for r in p6['rows'] if r['list'] == l and not r['in class'] and r['hidden'] and Fr(r['score_all']) > 2]
    mx = max((Fr(r['score_all']) for r in rows), default=None)
    at = [r['index'] for r in rows if Fr(r['score_all']) == mx]
    w('| %s | %d | %d | %d | %d | %d | %d | %s (orders %s) |' % (l, v['orders'], v['in the class'],
                                                              v['in the class: at 2 and hidden'], v['outside: at 2, hidden'],
                                                              v['outside: above 2, hidden'], v['outside: above 2, not hidden'],
                                                              tc.fstr(mx), at))
w()
w('Every order in the class loses weight at some knot and loses it equally across the four setting pairs (%s).' % (
    ', '.join('%s %d of %d' % (l, v['in the class: losing weight equally across the setting pairs'], v['in the class'])
              for l, v in s6.items())))
w()
# grow again
w('## Grow again (part 7)')
w()
w('| Start | Law | Renumberings | Different finished structure | Same: weighting compared by enumeration (same) | '
  'Same: by the renaming of the whole history | Weighting differs |')
w('| --- | --- | ---: | ---: | ---: | ---: | ---: |')
for r in p7['rows']:
    for l, v in r['laws'].items():
        w('| %s | %s | %d | %d | %d | %d | %d |' % (r['start'], l, r['renumberings'], v['different finished structures'],
                                                 v['weighting same'], v['weighting by renaming only'],
                                                 v['weighting DIFFERENT']))
w()
# P9 and the engine check
w('## P9 (part 5) and the engine check (part 9)')
w()
w('P9: %d types, %d distinct counting-from-the-start pair tables under renaming, so no two types share a table and the '
  'tables decide the next birth count (and status) on all %d. Gates: the finish pair counts and totals equal the '
  'archive’s on every type; the start tables equal enumeration on every type of at most 20 names.' % (
      p5['types'], p5['distinct tables under renaming'], p5['types']))
w()
if p9:
    w('Engine check (TD 7.3 on the 100 census starts, 3 rounds): first round whose product varies, by law and knot law.')
    w()
    w('| Law / knot law | Growths | Made a birth | First parting at round | Not parted | Undecided | Rounds checked directly | '
      'Rule against direct: mismatches |')
    w('| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |')
    for kk, v in p9['counts'].items():
        w('| %s | %d | %d | %s | %d | %d | %d | %d |' % (kk, v['growths'], v['made a birth'], v['first parting at round'],
                                                       v['not parted through the rounds done'], v['undecided'],
                                                       v['rounds checked directly'], v['rule against direct: mismatches']))
    w()
else:
    w('Engine check: not run.')
    w()
# table of statements
w('## The table of the record’s statements (C1)')
w()
TAB = {}
r11 = rows_of('eleven x2-x3/y2-y3')['variants'][0]
others = [rows_of('eleven %s/%s' % ('-'.join(a), '-'.join(b)))['variants'][0] for a in
          [('x2', 'x3'), ('x2', 'c'), ('x3', 'c')] for b in [('y2', 'y3'), ('y2', 't'), ('y3', 't')]][1:]
mg = r11['info']['marginals']
eleven_labels = ['structures.json: eleven (start)'] + ['structures.json: eleven + settings %d%d' % (a, b)
                                                       for a in (0, 1) for b in (0, 1)]
TAB['T01'] = (r11['rows']['from the finish']['score_all'] + ' hidden', r11['rows']['from the start']['score_all'] + ' hidden',
              'changed by ' + tc.fstr(F(r11['rows']['from the finish']['score_all']) - 2), knots_col(eleven_labels))
of = sorted({o['rows']['from the finish']['score_all'] for o in others})
TAB['T02'] = (' or '.join(of) + (' hidden' if all(o['rows']['from the finish']['hidden'] for o in others) else ''),
              '2 hidden (all eight)' if all(o['rows']['from the start']['score_all'] == '2' and o['rows']['from the start']['hidden']
                                            for o in others) else 'see part 2',
              'changed by ' + ' or '.join(tc.fstr(F(x) - 2) for x in of),
              knots_col([l for a in [('x2', 'x3'), ('x2', 'c'), ('x3', 'c')] for b in [('y2', 'y3'), ('y2', 't'), ('y3', 't')]
                         if (a, b) != (('x2', 'x3'), ('y2', 'y3'))
                         for l in fin_labels(rows_of('eleven %s/%s' % ('-'.join(a), '-'.join(b))))]))
TAB['T03'] = ('TV ' + tc.fstr(mg['(s1,s2) from the finish']["change under the second observer's setting"]),
              tc.fstr(mg['(s1,s2) from the start']["change under the second observer's setting"]),
              'changed by ' + tc.fstr(mg['(s1,s2) from the finish']["change under the second observer's setting"]),
              knots_col(eleven_labels))
TAB['T04'] = ('%d of 512 at 20/9 (hidden)' % s3['finish: hidden at 20/9'],
              '%d of 512 above 2; %d at 2, hidden' % (len(s3['start: above 2']), 512 - len(s3['start: not exactly 2'])),
              'changed: %d to %d' % (s3['finish: hidden at 20/9'], len(s3['start: above 2'])),
              'fails (the two four-place rules, K2, in all 512; projection)' if p8ok else 'see part 3')
ten_labels = fin_labels(rows_of('ten A x2-x3/y3-t')) + fin_labels(rows_of('ten B x2-x3/y2-t'))
TAB['T05'] = ('55/27 hidden per history; pooled %s (TD 3.5) and %s (nu uniform)' % (
    t5['ten A x2-x3/y3-t']['pooled from the finish (TD 3.5)'], t5['ten A x2-x3/y3-t']['pooled from the finish (nu uniform)']),
              '2 hidden, per history and pooled' if p7ok else 'see part 2', 'changed by 1/27 (per history)',
              knots_col(ten_labels) + '; the starts: ' + knots_col(['structures.json: ten A: eleven less even(y2,k1,k2) (start)',
                                                                    'structures.json: ten B: eleven less odd(y3,k1,k2) (start)']))
sg = rows_of('smallest gain')['variants'][0]['rows']
sg_labels = ['structures.json: smallest gain finished %d%d' % (a, b) for a in (0, 1) for b in (0, 1)]
TAB['T06'] = (sg['from the finish']['score_all'] + ' hidden', '%s hidden (from the part), %s hidden (after round 1)' % (
    sg['from the start']['score_all'], sg['from stage 1']['score_all']),
              'changed by ' + tc.fstr(F(sg['from the finish']['score_all']) - 2), knots_col(sg_labels))
op = [r for r in recs if r['record']['source'].startswith('ONE-PARENT')]
opv = sorted({r['variants'][0]['rows']['from the finish']['score_all'] for r in op}, key=Fr)
op_labels = ['part 2: %s | %s' % (r['name'], ab) for r in op for ab in r['variants'][0]['finished']]
TAB['T07'] = (', '.join(opv) + ' hidden (680 records reproduced)', '2 hidden in all 680 (from the part and after the round)'
              if all(r['variants'][0]['rows']['from the start']['score_all'] == '2' and
                     r['variants'][0]['rows']['from stage 1']['score_all'] == '2' for r in op) else 'see part 2',
              'changed by ' + ', '.join(tc.fstr(F(x) - 2) for x in opv), knots_col(op_labels))
for tid, name, lab in [('T09', 'seven', 'seven'), ('T10', 'eight', 'eight'), ('T11', 'nine', 'nine')]:
    rr = rows_of(name)['variants'][0]['rows']
    labs = ['structures.json: %s' % k for k in tc.load_structures() if k.startswith(lab)]
    TAB[tid] = (rr['from the finish']['score_all'] + ' hidden', rr['from the start']['score_all'] + ' hidden',
                'changed by ' + tc.fstr(F(rr['from the finish']['score_all']) - 2), knots_col(labs))
rr = e18['rows']
TAB['T13'] = (rr['from the finish']['score_all'] + ' hidden', rr['from the start']['score_all'] + ' hidden (recomputed)',
              'changed by ' + tc.fstr(F(rr['from the finish']['score_all']) - 2),
              knots_col(['structures.json: %s' % k for k in tc.load_structures() if k.startswith('eighteen')]))
TAB['T15'] = ('2/9 between keyings (pooled), 18-knot and 11-knot', '0 (both structures)', 'changed by 2/9',
              knots_col(['structures.json: %s' % k for k in tc.load_structures() if k.startswith('eighteen')])
              + '; 11-knot: ' + knots_col(eleven_labels))
e83r = rows_of('eight-thirds case')['variants'][0]['rows']
TAB['T17'] = ('the 8/3 case: %s, not hidden (change %s)' % (e83r['from the finish']['score_all'],
                                                           max(F(e83r['from the finish']['change_first']),
                                                               F(e83r['from the finish']['change_second']))),
              'the 8/3 case: %s, %s' % (e83r['from the start']['score_all'], 'hidden' if e83r['from the start']['hidden'] else 'not hidden'),
              'changed: 8/3 not hidden to 2 hidden (the census rows not recomputed)',
              knots_col(fin_labels(rows_of('eight-thirds case'))))
rrr = [r for r in recs if r['record']['source'].startswith('REREAD')]
rv = sorted({r['variants'][0]['rows']['from the finish']['score_all'] for r in rrr}, key=Fr)
TAB['T18'] = (', '.join(rv) + ' hidden (214 records reproduced)', '2 hidden in all 214 (from the start and after the round)'
              if all(r['variants'][0]['rows']['from the start']['score_all'] == '2' and
                     r['variants'][0]['rows']['from stage 1']['score_all'] == '2' for r in rrr) else 'see part 2',
              'changed by ' + ', '.join(tc.fstr(F(x) - 2) for x in rv),
              knots_col(['part 2: %s | %s' % (r['name'], ab) for r in rrr for ab in r['variants'][0]['finished']]))
TAB['T36'] = ('194 of 194 (the record)', '194 of 194: no two types share a table' if p5['P9 holds (the tables decide the next birth count)'] else 'see part 5',
              'unchanged', 'not applicable (no settings-line structure)')
w('| Row | Statement | From the finish | From the start | Verdict here | Verdict in table.json | Knots in the whole (here) | Source |')
w('| --- | --- | --- | --- | --- | --- | --- | --- |')
trows = []
for row in table['rows']:
    tid = row['id']
    if tid in TAB:
        fin, st, vd, kn = TAB[tid]
        src = 'recomputed here'
    else:
        fin, st, vd, kn = row['from the finish'], row['from the start'], row['verdict'], row['knots in the whole']
        src = 'from table.json (not recomputed here)'
    trows.append({'id': tid, 'statement': row['statement'], 'from the finish': fin, 'from the start': st,
                  'verdict here': vd, 'verdict in table.json': row['verdict'], 'knots in the whole': kn, 'source': src,
                  'record': row['record']})
    w('| %s | %s | %s | %s | %s | %s | %s | %s |' % (tid, row['statement'].replace('|', '/'), fin, st, vd, row['verdict'],
                                                     kn.replace('|', '/'), src))
summary['table'] = trows
w()
# knot table of the 33
w('## The knot test in the whole: the 33 registered structures')
w()
S = tc.load_structures()
if p8:
    w('Projection on %d distinct structures; the canonical command on %d knots of this run and %d of the early run '
      '(agreement with projection: %s; disagreements %d; errors %d); %d structures cut from the canonical check (R 38).' % (
          p8['unique structures'], p8['canonical knots checked (this run)'], p8['canonical knots checked early'],
          'every knot' if not p8['canonical disagreements with projection'] else 'NOT every knot',
          len(p8['canonical disagreements with projection']), len(p8['canonical errors']), p8['canonical structures cut']))
    w()
    w('| Structure | Knots | Distinctions | Rule | Relation induced in the whole | K1 | K2 | K3 | In the whole | On its own | Canonical |')
    w('| --- | ---: | ---: | --- | --- | --- | --- | --- | --- | --- | --- |')
    knot33 = []
    for name in S:
        s = by_label.get('structures.json: ' + name)
        if s is None:
            continue
        for k in s['knots']:
            c = k.get('canonical')
            cs = ('agrees' if c.get('agrees with projection') else 'DISAGREES') if isinstance(c, dict) and 'knot' in c else str(c)
            knot33.append({'structure': name, 'rule': k['knot'], 'induced': k['induced'], 'K1': k['K1'], 'K2': k['K2'],
                           'K3': k['K3'], 'whole': k['whole'], 'own': k['own'], 'canonical': cs})
            w('| %s | %d | %d | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                name, s['n_knots'], s['n_distinctions'], k['knot'], ' '.join(k['induced']) if len(k['induced']) <= 8
                else '%d rows (all of the rule’s own)' % len(k['induced']) if k['whole'] else ' '.join(k['induced']),
                k['K1'], k['K2'], k['K3'], 'passes' if k['whole'] else 'fails', 'passes' if k['own'] else 'fails', cs))
    summary['knot table (33)'] = knot33
    w()
    # beyond the finding's structures: part 2's records
    w('**Beyond the 33: part 2’s histories.** Rules that fail in the whole in the finished structures of part 2’s '
      'records (projection; the canonical check where run agreed on every knot):')
    w()
    w('| Source | Histories | With a rule failing in some finished structure | Rules failing (finished structures) | '
      'Scores from the finish of the histories whose every rule passes | Canonical |')
    w('| --- | ---: | ---: | --- | --- | --- |')
    beyond = []
    for src_ in ['ONE-PARENT-REREAD uniform', 'ONE-PARENT-REREAD mixed', 'REREAD-BIRTHS rule R']:
        rs = [r for r in recs if r['record']['source'] == src_]
        nf = 0
        cf = Counter()
        passing = Counter()
        cst = Counter()
        for r in rs:
            anyf = False
            for ab in r['variants'][0]['finished']:
                s = by_label.get('part 2: %s | %s' % (r['name'], ab))
                if s is None:
                    continue
                cst[canon_status(s)] += 1
                for k in s['knots']:
                    if not k['whole']:
                        anyf = True
                        cf['%s at %s' % (k['knot'], ab)] += 1
            nf += anyf
            if not anyf:
                passing[r['variants'][0]['rows']['from the finish']['score_all']] += 1
        beyond.append({'source': src_, 'histories': len(rs), 'with a failing rule': nf, 'rules': dict(cf),
                       'finish scores of the histories whose every rule passes': dict(passing), 'canonical': dict(cst)})
        w('| %s | %d | %d | %s | %s | %s |' % (src_, len(rs), nf, '; '.join('%s ×%d' % x for x in sorted(cf.items())),
                                               ', '.join('%s ×%d' % x for x in passing.most_common()),
                                               '; '.join('%s ×%d' % x for x in cst.most_common())))
    summary['beyond the 33'] = beyond
    w()
    allk = [k for s in p8['structures'] for k in s['knots']]
    w('All %d distinct structures of parts 2–4 and structures.json: %d knot verdicts, %d fail in the whole, %d fail '
      'on their own. Part 3’s 2,560 structures: the two four-place rules fail K2 in every one, no other rule fails.' % (
          len(p8['structures']), len(allk), sum(1 for k in allk if not k['whole']), sum(1 for k in allk if not k['own'])))
    w()
    fail_by = Counter()
    for s in p8['structures']:
        for k in s['knots']:
            if not k['whole']:
                fail_by[(s['labels'][0].split(':')[0], k['knot'])] += 1
    w('Failing rules by source and rule (structures counted): ' + '; '.join('%s %s ×%d' % (a, b, n) for (a, b), n in
                                                                        fail_by.most_common()))
    w()
else:
    w('Part 8 remainder: not run.')
w()
summary['walls'] = {'part 1': p1['wall_s'], 'part 8 early': p8e['wall_s'], 'part 2': p2['wall_s'], 'part 3': p3['wall_s'],
                    'part 4': p4['wall_s'], 'part 5': p5['wall_s'], 'part 6': p6['wall_s'], 'part 7': p7['wall_s'],
                    'part 8 remainder': p8['wall_s'] if p8 else None, 'part 9': p9['wall_s'] if p9 else None}
w('## Wall times (s)')
w()
w(json.dumps(summary['walls']))
open(A + 'summary.md', 'w').write('\n'.join(md) + '\n')
tc.dump('summary.json', summary)
print('\n'.join(md[:40]))
