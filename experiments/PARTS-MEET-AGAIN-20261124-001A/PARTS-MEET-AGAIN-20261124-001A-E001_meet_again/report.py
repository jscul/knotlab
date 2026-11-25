"""summary.json and summary.md from summary_core.json (written by analyze.py).  usage: python -B report.py"""
import json
import os
from collections import Counter

import common as C


def load():
    with open(os.path.join(C.OUT, 'summary_core.json')) as f:
        return json.load(f)


def j(x, n=400):
    s = json.dumps(x, sort_keys=True)
    return s if len(s) <= n else s[:n] + ' ...'


def rows(S):
    V = S['verdicts']
    g = S['gate']
    R = []
    b, bb = g['brute'], g['birth']
    R.append(('P0', V['P0']['verdict'],
              'ring engine: %d registered + %d extra runs of G, %d rounds compared, %d mismatches; IMPLIED = LITERAL on '
              '%d parity runs (%d differ); rule R / rule Q engines: %d runs, %d rounds compared, %d mismatches; brute '
              'force: %d structures, %d knot verdicts (%d failing), ranks/kernel/NAE mismatches %d/%d/%d; birth method: '
              '%d grown structures, %d knots (%d failing), against direct %d and brute %d mismatches; birth vs direct on '
              'run G: %d knots compared, 0 disagree' % (
                  g['ring_runs_registered'], g['ring_runs_extra'], g['ring_rounds_compared'], g['ring_mismatches'],
                  g['implied_vs_literal_runs'], g['implied_vs_literal_mismatch'], g['rq_runs'],
                  g['rq_rounds_compared'], g['rq_mismatches'], b['structures'], b['knot_verdicts'], b['failing'],
                  b['mismatch_ranks'], b['mismatch_kernel'], b['mismatch_nae'], bb['structures'], bb['knots'],
                  bb['failing'], bb['mismatch_direct'], bb['mismatch_brute'], g['G_birth_vs_direct'])))
    n = V['P1']['numbers']
    R.append(('P1', V['P1']['verdict'], '%d runs (run 1 arm A, CARRY both readings): no wholly-apart pair one part '
              'again, no joint birth, every pair checked; run 2: %d enumerations, %d histories, no violation' % (
                  n['runs checked (run 1 arm A, CARRY of run 3, CARRY other reading)'], n['run 2 enumerations checked'],
                  n['run 2 histories'])))
    n = V['P2']['numbers']
    R.append(('P2', V['P2']['verdict'], 'arm A pairs at s >= 1: %d under not-all-equal, none differs; %d under '
              'parity, %d differ (none by another way). The two-knot start\'s own pair at s = 0 (an addition, not '
              'wholly apart) differs under Q by a group or owing / fresh: outside argument 4' % (
                  n['pairs at s >= 1, not-all-equal'], n['pairs at s >= 1, parity'],
                  n['parity marks (all by a round-wide trigger if holds)'])))
    n = V['P3']['numbers']
    R.append(('P3', V['P3']['verdict'], 'ring returns under arm A from round 1: %d (control without a taking rule: '
              'RING-LAW returns at rounds 2, 4, 6, 8 on all three ring starts); two-knot parts after round 1 besides '
              'the exception: %d; exception N(1) = 2 on the two-knot start under SHORT-TAKES (every COPY-LAW, both '
              'knot laws)' % (len(n['ring returns under arm A from round 1']),
                              len(n['two-knot parts after round 1 other than the exception']))))
    R.append(('P4', V['P4']['verdict'], 'three-knot start, COPY-LAW(t), both knot laws: Q(OLDEST/NEWEST) round 2 has '
              'the group {3, 4, 5} and one part at every round; SHORT-TAKES: knot 3 short in round 2, its second join '
              'takes a shared distinction, one part through round 8 (%d of %d runs)' % (
                  sum(1 for x in V['P4']['numbers'] if x['ok']), len(V['P4']['numbers']))))
    n = V['P5']['numbers']
    R.append(('P5', V['P5']['verdict'], '; '.join('%s: %d pairs that came apart, %d one part again' % (
        k, v['pairs that came apart'], v['one part again']) for k, v in sorted(n.items()))))
    n = V['P6']['numbers']
    R.append(('P6', V['P6']['verdict'], 'RECORD-2: %d pairs that came apart, %d one part again; RECORD-3: %d, %d; '
              'ALL-JOINABLE, CARRY (both readings): at most one class at every round' % (
                  n['RECORD-2']['pairs that came apart'], n['RECORD-2']['one part again'],
                  n['RECORD-3']['pairs that came apart'], n['RECORD-3']['one part again'])))
    n = V['P7']['numbers']
    R.append(('P7', V['P7']['verdict'], 'round 1: %s; round 2 under RETIRE: groups %s, retired %s, %d knots at the end; '
              'under WAIT jammed in round 2: %s' % (n['CANCEL-RETIRE']['round1'], n['CANCEL-RETIRE']['round2']['groups'],
                                                     n['CANCEL-RETIRE']['round2']['retired'],
                                                     n['CANCEL-RETIRE']['final_knots'],
                                                     n['CANCEL-WAIT']['round2']['jammed'])))
    n = V['P8']['numbers']['nae']
    R.append(('P8', V['P8']['verdict'], 'one part again %s (through start knot 0, no recorded ancestor of both); course '
              'differs %s in B(i), %s in B(ii); demand line %s; way %s; %s; joint birth %s; verdict %s; 12-15 take '
              '%s; %d knots after round 5; knot failures through round 8: %d (not-all-equal), %d (parity)' % (
                  n['one part again'], n['course differs B(i)'], n['course differs B(ii)'], n['demand line'],
                  n['way'], n['confirmed'], n['joint birth'], n['verdict'], n['round 3 takes of 12..15'],
                  n['knots after round 5'], n['knot fails through round 8'],
                  V['P8']['numbers']['parity']['knot fails through round 8'])))
    n = V['P9']['numbers']
    R.append(('P9', V['P9']['verdict'], '; '.join('%s: %s' % (k, 'stands' if v['stands'] else 'vanishes')
                                                 for k, v in n.items() if isinstance(v, dict) and 'stands' in v) +
              '; names reversed through %s' % n['names reversed']['verdicts']))
    n = V['P10']['numbers']
    R.append(('P10', V['P10']['verdict'], 'one part again %s through %s; course differs %s; verdict %s; ' % (
        n['case']['one part again'], n['case']['link classes'], n['case']['course differs'], n['case']['verdict']) +
        '; '.join('%s: %s' % (k, ('stands ' + str(v['verdicts'])) if v['stands'] else 'vanishes')
                  for k, v in n.items() if isinstance(v, dict) and 'stands' in v)))
    n = V['P11']['numbers']
    R.append(('P11', V['P11']['verdict'],
              'pairs that came apart, minimal (three components): base laws %s, CAP-3 swap %s; four components: base '
              '%s, CAP-3 %s. Halves (first time): base %s, CAP-3 %s. No law of arm A, RECORD-k, ALL-JOINABLE or CARRY '
              'has the mark' % (
                  n['came apart']['base laws']['minimal, three components (holder, record, whole roster)'],
                  n['came apart']['CAP-3 swap']['minimal, three components (holder, record, whole roster)'],
                  n['came apart']['base laws']['minimal, four components (choice supplier compared by equality)'],
                  n['came apart']['CAP-3 swap']['minimal, four components (choice supplier compared by equality)'],
                  n['first time']['base laws']['minimal, three components (holder, record, whole roster)'],
                  n['first time']['CAP-3 swap']['minimal, three components (holder, record, whole roster)'])))
    n = V['P12']['numbers']
    R.append(('P12', V['P12']['verdict'], 'came apart: %d cases; vanish under %s; survive the ration swap: %d; STEPS-2 '
              'surviving UP-TO-2: %d; vanish under the knot law: %d. Halves: %d cases; vanish under %s; survive every '
              'swap: %s' % (n['came apart']['cases'], n['came apart']['vanish under'],
                            len(n['came apart']['survive the ration swap']),
                            len(n['came apart']['STEPS-2 cases surviving UP-TO-2']),
                            len(n['came apart']['vanish under the knot law']), n['first time']['cases'],
                            n['first time']['vanish under'], n['first time']['survive every swap'])))
    n = V['P13']['numbers']
    R.append(('P13', V['P13']['verdict'], 'smallest case, first copy only: %s; Ring(5,3), X a given-off part, Y the '
              'ring part: %s' % (n['smallest case, first copy only'], j(n[
                  'Ring(5,3) RING-LAW STEPS-2(OLDEST), X a given-off part, Y the ring part'], 300))))
    sp = V['P14']['supplement (every three-knot pair with a course-differs mark in runs 1 and 3)']
    R.append(('P14', V['P14']['verdict'], 'run 4: ' + j([(x['case'], x['knot_law'], 'differs' if x['course differs']
                                                          else 'same', x['rounds compared'])
                                                         for x in V['P14']['numbers']], 300) +
              '; supplement: %d three-knot pairs with a mark, %d applicable (six laws: %s), differing: %s' % (
                  sp['pairs'], sp['applicable (Y from knot 2 only, X not from knot 2)'],
                  sp['laws of the applicable pairs'],
                  sp['applicable pairs whose course differs with what the other is'] or 'none')))
    R.append(('P15', V['P15']['verdict'], j([(x['base'], x['start'], x['knot_law'], 'one part at s with the placed '
                                             'knot: %s' % x['one_part_at_round_s_with_placed_knot'],
                                             'vs Y barred: %s' % x['course_differs_against_Y_barred']['round'],
                                             'vs no placed knot: %s' % x['course_differs_against_no_placed_knot'][
                                                 'round']) for x in V['P15']['numbers']], 700)))
    n = V['P16']['numbers']
    R.append(('P16', V['P16']['verdict'], 'COPY-LAW(WAIT)+HOLD: %d pairs not wholly apart, %d one part again, course '
              'differs: %d; Q with HOLD, runs with parts that come apart: %s' % (
                  n['COPY-LAW(WAIT)+HOLD: pairs not wholly apart'], n['of them one part again'],
                  len(n['COPY-LAW(WAIT)+HOLD: course differs']), n['Q with HOLD: parts that come apart (runs)'])))
    R.append(('P17', V['P17']['verdict'], j(V['P17']['numbers'], 900)))
    n = V['P18']['numbers']
    R.append(('P18', V['P18']['verdict'], 'run A verdicts %d, comparison-run verdicts %d, run 2 verdicts %d; method '
              'disagreements %d; untested %d; birth vs direct compared %d. Not-all-equal failures outside CARRY: %d; '
              'parity failures not at a join of 3+ parents (FLOOR0/ONE-FEWER excepted): %d' % (
                  n['verdicts'], n['comparison-run verdicts'], n.get('run 2 verdicts', 0), n['disagreements'],
                  n['untested'], n['birth vs direct compared'],
                  len(V['P18']['not-all-equal failures outside CARRY']),
                  len(V['P18']['parity failures not at joins of 3+ parents']))))
    return R


DIFFERENCES = [
    ('Pairs tested in runs 1 and 3 (s >= 1)', '7,039 (5,703 that came apart, 1,336 for the first time)',
     'see summary_core.json run1_pairs/run3_pairs', 'every disclosed per-law count of pairs that came apart is equal '
     '(Q 24/178/22/182, late start 355/387/438/438, RECORD 270/174, UP-TO-2(NEWEST) 244); so are the 302 and 116 '
     'marks, their ways, demand lines, reading (ii) and verdicts. The difference lies in laws whose pair counts were '
     'not disclosed. No verdict differs.', 'summary_core.json'),
    ('CARRY, the round-2 join of ten parents on Ring(5,3)', '21 places (ten given, ten carried, one fresh), failing '
     'under both knot laws', '15 places under reading 10 (a parent whose oldest distinction the birth already takes '
     'adds nothing): fails under parity, passes under not-all-equal. Under the other reading (oldest not already '
     'taken) 21 places, failing under both: the disclosed knot', 'P18 holds under either reading (CARRY is the '
     'permitted place); P1 and P6 hold under either', 'replays.json (carry), carry-alt.jsonl.gz'),
    ('Q with HOLD', 'nothing comes apart', 'under COPY-LAW(OFFSHOOT)+HOLD with Q(NEWEST): on the two-knot start the '
     'round-1 part {2, 3, 4, 5} comes apart at round 2; on Ring(5, 3) the round-0 and round-1 parts come apart at '
     'round 2 (every member is short in round 2, so HOLD keeps nothing and the round is the RELEASE round)',
     'P16 fails on this clause', 'replays.json (hold_q_newest)'),
    ('HOLD arm counts', 'COPY-LAW(WAIT)+HOLD: "6 of 20 and 6 of 6 pairs" not wholly apart one part again; STEPS-2 with '
     'HOLD: 3 pairs one part again', 'per knot law, two-knot start: 12 pairs, 4 not wholly apart, all 4 one part '
     'again; three-knot start: 6 of 6. STEPS-2(OLDEST)+HOLD: pairs not wholly apart one part again: 7 per knot law '
     '(and wholly-apart pairs with marks)', 'P16\'s first clause holds; counts differ; the cap of four pairs per round '
     'was kept (reading 20); without it the two-knot count is 12 of 34', 'run7.jsonl.gz'),
    ('STEPS-2 with HOLD (run 7)', '"under STEPS-2 with HOLD, 3 pairs are one part again, no course differs"',
     'STEPS-2(OLDEST) with HOLD: 14 "course differs" marks per knot law at s >= 1 (COPY-LAW(OFFSHOOT): three-knot 5, '
     'one of them on a pair not wholly apart, two-knot 3; COPY-LAW(RETIRE): three-knot 2, the smallest case under HOLD '
     'as P9 says, two-knot 2; RING-LAW: two-knot 2); none under COPY-LAW(WAIT)', 'P16 judges no course under '
     'COPY-LAW(WAIT) only, and that holds; P9 (the smallest case stands under HOLD) holds', 'run7.jsonl.gz'),
    ('A225 control under COPY-LAW(WAIT)', 'the first copy\'s course differs at round 3', 'with X, Y the two copies '
     '{6, 7}, {8, 9}: round 5 (way: a group or owing; the placed knot is short only while the second copy is there, '
     'so the first copy\'s join 11 makes an offshoot instead of a join with it). Round 3 is what X = the waiting join '
     '{3}, Y = {6, 7} gives (my first run 6, reading 38)', 'P15 fails on this clause (round 5, not 3)',
     'replays.json (a225_wait), run6.jsonl'),
    ('Swap battery, HOLD', 'HOLD removes 27 of 33 cases that came apart', '24; two cases survive only through a pair '
     'not wholly apart, one only through marks confirmed by the mask that are never one part again (verdict '
     'unconfirmed); counting only wholly-apart pairs with a made or start-knot verdict gives 27', 'P12 does not judge '
     'HOLD; no verdict differs', 'run5.jsonl'),
    ('The smallest case under HOLD', 'three pairs show it', 'two confirmed pairs (any pair, wholly apart or not)',
     'P9 holds (it stands)', 'run4.jsonl'),
    ('Q runs with pairs that came apart', '8, 14, 2 and 14 of the 42 runs', 'equal when counting runs in which a part '
     'comes apart (every part); 2, 14, 2, 14 runs with a sampled pair that came apart', 'none', 'summary_core.json'),
]


def main():
    S = load()
    R = rows(S)
    lines = ['# PARTS-MEET-AGAIN-20261124-001A-E001: summary', '',
             'Engine written from the frozen texts by a helper that did not see the drafter\'s prototype. Every reading '
             'taken is an item of `deviations.md` (experiment folder). Files named below are in this artifact folder.',
             '', '## Predictions', '', '| # | Verdict | The numbers |', '| --- | --- | --- |']
    for k, v, n in R:
        lines.append('| %s | %s | %s |' % (k, v, n.replace('|', '/')))
    lines += ['', '## Differences from the numbers disclosed before the freeze', '',
              '| What | Disclosed | Found here | Verdict | Listing |', '| --- | --- | --- | --- | --- |']
    for a, b, c, d, e in DIFFERENCES:
        lines.append('| %s | %s | %s | %s | %s |' % (a, b, c, d, e))
    V = S['verdicts']
    lines += ['', '## The cost of the laws (definitions 3.3)', '',
              '| Law | Holder steps | Record steps | Whole roster | Choice supplied by |', '| --- | --- | --- | --- | --- |']
    for l, c in sorted(V['P11']['cost table'].items()):
        lines.append('| %s | %s | %s | %s | %s |' % (l, 'any' if c[0] == 99 else c[0], 'any' if c[1] == 99 else c[1],
                                                    'yes' if c[2] else 'no', c[3]))
    lines += ['', '## Minimal laws with a confirmed "course differs" mark', '']
    for kind in ('came apart', 'first time'):
        for grp, d in sorted(V['P11']['numbers'][kind].items()):
            lines.append('- %s, %s: laws with the mark %s; minimal (three components) %s; minimal (four components, '
                         'the choice compared by equality) %s' % (
                             'pairs that came apart' if kind == 'came apart' else "the two-knot start's halves",
                             grp, d['laws with the mark'],
                             d['minimal, three components (holder, record, whole roster)'],
                             d['minimal, four components (choice supplier compared by equality)']))
    lines += ['', '## The swap battery (run 5): which swaps each case survives', '',
              '| Case (law, base law, start, kind) | names rev. | order rev. | demand first | fresh by parents | HOLD | '
              'ration | STEPS/UP-TO | knot law |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    order = ['names reversed', 'order reversed', 'demand before the takes', 'fresh by parents', 'HOLD', 'ration',
             'STEPS-k/UP-TO-k', 'knot law']
    for b in V['P12']['battery']:
        c = b['case']
        cells = []
        for k in order:
            x = b['survives'].get(k)
            cells.append('n/a' if x is None else ('survives' if x else 'vanishes'))
        lines.append('| %s, %s, %s, %s | %s |' % (c['law_name'], c['base'], c['start'], c['kind'], ' | '.join(cells)))
    n = V['P18']
    lines += ['', '## Knot tests', '', '- Numbers: %s' % j(n['numbers'], 600),
              '- Failing knots of the registered runs (distinct rows: run, knot law, law, base, start, kind, parents, '
              'places, round made; run-2 rows give the enumeration): %s'
              % j([f for f in n['failing knots (distinct rows)'] if not f[0].startswith('carry-alt')], 4000),
              '- Run 2 failure examples: %s' % j(n.get('run 2 failure examples', []), 2500),
              '- Supplementary CARRY run (other reading, not registered): %s' % j(
                  n['supplementary CARRY run (other reading), failures (not registered)'], 600)]
    lines += ['', '## The most-held distinction within the run, per law', '', j(S['holders'], 2000)]
    lines += ['', '## Run 2 (every choice)', '']
    for r in S['run2']:
        if 'stats' in r and r['stats']:
            st = r['stats']
            lines.append('- %s: %s, %d histories, pairs wholly apart %d (came apart %d), one part again %d, joint '
                         'births %d, knot verdicts %d, failures %d%s' % (
                             r['id'], r['mode'], st['histories'], st['pairs_wholly_apart'], st['pairs_came_apart'],
                             st['one_part_again'], st['joint_births'], st['knot_verdicts'], st['knot_fails'],
                             '' if r['mode'] != 'drawn' else ', distinct final structures %d' %
                             st.get('distinct_final_structures', 0)))
        elif r.get('error'):
            lines.append('- %s: error %s' % (r['id'], r['error']))
    lines += ['', 'Not finished when this summary was written: %s' % j(S.get('run2_not_finished', []), 3000),
              '', 'Their progress (last progress line): %s' % j(S.get('run2_progress_of_unfinished', {}), 3000)]
    lines += ['', '## Stops', '', j(S['stops'], 800), '', 'Errors: %s' % j(S['errors'], 400)]
    with open(os.path.join(C.OUT, 'summary.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    out = {'predictions': {k: {'verdict': v, 'numbers': n} for k, v, n in R}, 'differences': [
        dict(zip(('what', 'disclosed', 'found', 'verdict', 'listing'), d)) for d in DIFFERENCES],
        'verdict_details': V, 'holders': S['holders'], 'stops': S['stops'], 'run2': S['run2'], 'gate': S['gate']}
    C.write_json('summary.json', out)


if __name__ == '__main__':
    main()
