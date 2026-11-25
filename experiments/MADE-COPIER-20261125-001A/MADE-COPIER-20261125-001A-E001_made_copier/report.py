"""summary.md from summary.json (analyze.py) and the check and replay files.

usage: python -B report.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402


def load(name):
    p = C.out_path(name)
    return json.load(open(p)) if os.path.exists(p) else None


def frac(s):
    return s


def j(o, n=600):
    s = json.dumps(o, sort_keys=True)
    return s if len(s) <= n else s[:n] + ' ...'


def lines_kv(d):
    return '; '.join('%s: %s' % (k, v) for k, v in d.items())


def main():
    S = load('summary.json')
    p20 = load('check_p20.json')
    rp = load('replays.json')
    N = {k: S[k]['numbers'] for k in S if not k.startswith('_')}
    V = {k: S[k]['verdict'] for k in S if not k.startswith('_')}
    out = []

    def w(line):
        out.append(line.replace('Seen: seen: ', 'Seen: ').replace('Seen: seen on', 'Seen on')
                   .replace('copies placed', 'placed by hand'))
    w('# MADE-COPIER-20261125-001A, E001: every prediction\'s verdict')
    w('')
    w('Written by the engine\'s author from the frozen text (commit 5ccb89fd87) and the result files of this folder; '
      'the drafter\'s scratch folder and the study\'s advisor folder were not read. The growth is the fold study\'s '
      'engine, imported unchanged. Readings taken where the text left a choice are numbered in '
      '`experiments/MADE-COPIER-20261125-001A/MADE-COPIER-20261125-001A-E001_made_copier/deviations.md` ("dev n"). '
      'Numbers are counts of runs unless said otherwise; "seen" quotes the prototype\'s disclosed number. The only '
      'weighting used is the take-by-take weighting of run 4 (D 2.7), named where used. COPY-LAW(t) is the fold '
      'study\'s name for (FLOOR1, t, RELEASE); it is not a law of copying. No claim is made about living things, minds, '
      'physics or time.')
    w('')
    c = S['_counts']
    w('**Runs made.** Gate and run R; run 1: %d runs; run 2: %d laws, %d runs A with their comparison runs; '
      'X alone and Y alone of made-2-exchanged: %d laws (dev 44); run 3: %d runs, %d pairs; run 4: %d enumerations and '
      'the 33 replayed take lists; run 5: %d cases of run 2, %d of run 3, %d take lists, %d reading-(iv) jobs, %d laws of '
      'the form arm under six swaps; run 6: %d jobs; run O: %d runs.' % (
          c['run 1 runs'], c['run 2 laws'], c['run 2 design runs'], S['_exchanged_alone']['laws'], c['run 3 runs'],
          c['run 3 pairs'], c['run 4 enumerations'], c['run 5 cases'], c['run 5 run-3 cases'], c['run 5 take lists'],
          c['run 5 (iv) jobs'], c['run 5 form arm laws'], c['run 6 jobs'], c['run O runs']))
    errs = {k: v for k, v in c['errors'].items() if v}
    w('Errors in the result files: %s. The file run5_form.jsonl.gz also keeps the 8 error rows of a first pass beside '
      'their reruns (dev 47).' % (j(errs) if errs else 'none'))
    w('')
    # ------------------------------------------------------------------------------------------------ findings
    f1c, f1n = {}, {}
    for k, v in N['P8b'].items():
        dsg, base, kl = [x.strip() for x in k.split('|')]
        if kl == 'parity':
            f1c.setdefault(base, []).append(dsg) if v['with two of a place of Y made by X'] else None
            f1n.setdefault(base, 0)
            f1n[base] += 1
    cs = N['P6']['the case']
    w('## Findings, plainly')
    w('')
    w('1. **No copier, in any reading, for any registered class, law and rule** (POA (i): %s). In values under parity '
      'there is one case under a stated rule: ystart-three-222 under COPY-LAW(CANCEL-OFFSHOOT), MET(NEWEST), where '
      'two usable loose distinctions made by births descended from X only (%s) are tied to a place of Y (%s, a place '
      'of one of Y\'s members) after round %s. Supplied: X (a start pattern), its link to Y through the start '
      'distinction e, the rule (NEWEST picks by name) and the start\'s naming. Made by the growth: only the births that '
      'carry the value. It is lost under every renaming n1 to n4, under the other three rules, the other eight base '
      'laws, STEPS-1, the order of births reversed and the other knot law; it survives HOLD and demand before the '
      'takes. With Y barred, X\'s births leave two again, tied to another place of Y (B(i)), so the case does not '
      'need Y\'s births; whether it needs Y\'s knots was not run.' % (N['POA']['(i)'], cs['two'], cs['v'], cs['round']))
    w('2. **Not-all-equal ties no made distinction to anything** (P2), in every run and history read, as S2 argues for starts with no tie at round 0 under these laws; so '
      'no made pattern leaves two of a place of Y there. Under parity the knot law allows it and the choice decides it: '
      'with every choice of takes read under the take-by-take weighting, histories with two of a place of Y made by X '
      'are found under %s (designs with one: %s). Supplied in each: the history of takes.' % (
          ', '.join('%s in %d of %d designs' % (b, len(f1c.get(b, [])), n) for b, n in sorted(f1n.items())),
          j(f1c, 800)))
    w('3. **Two parts the same as the second pattern, made by X\'s descendants alone, appear only where the first '
      'pattern makes them on its own course or under one rule and one naming.** Under COPY-LAW(t) the ration gives '
      'every later knot at most one loose distinction, so the part that copies itself stops (P1, P3, P5: the ration\'s '
      'doing). Under the form arm\'s laws, apart from the control with Y the same as X, the only case is made-4 under '
      'FBP(CANCEL-OFFSHOOT): under MET(BY-COUNT) the two are there with this Y and not in X alone, the same two come '
      'with Y\'s members barred, no other member of the class gets two, and the case is lost under n1 and n3; under '
      'STEPS-1, in the registered numbering, X alone makes the same two and X and Y are never one part again, so '
      'there they are X\'s own course. One of them passes the registered renamings (n1, n3, n4) and, added after the '
      'freeze, each of the 28 numberings of the start run (dev 51). The independent check found that in 20 of those '
      '28 numberings X and Y are one part at round 2 and the two parts appear a round before X alone has them; in '
      'none of the 28 is it a copier, since no other member of the class gets two of its own. Supplied: the start, '
      'the rule and the naming. The growth makes the parts.')
    w('4. **Under the registered laws a second pattern changes no place and no relation among the first pattern\'s '
      'distinctions; it changes only the first pattern\'s course** (PO1 in every run; X\'s course differs with Y barred '
      'in %d of %d runs). Reading (ii) holds in %d runs and its reverse in %d, reading (iii) in %d and its reverse in '
      '%d, none of them about a copier. A third pattern removes the one values case when it is named before Y and '
      'gives it back when barred (5 of 5 kinds), and is named after Y in the other five, where the two go to a place of '
      'the third pattern instead: it follows the names, as the case does. Only under the rations FLOOR0 and ONE-FEWER '
      'do births descended from Y only change the relation on X\'s distinctions (%d runs), and in each of them a knot '
      'fails the knot test at that round.' % (
          N['PO3']['all']['X differs'], N['PO3']['all']['runs'], len(N['PO5']), len(N['PO6']), N['PO9']['(iii)'],
          N['PO9']['(iii) reverse'], N['PO2']['by births descended from Y only']))
    w('5. **The engines agree on every disclosed count but three, and the replays name the reading behind each**: '
      'whether the confirmation of a course difference is read at T (D 7.1) or through the confirming runs\' own last '
      'round (2 runs), and which run a class member\'s "Y after round s" is taken from in the census (CAP-3(t) runs '
      'of made-4, made-5 and made-6); and the guard stops of the every-choice run under the cap of three, which the '
      'prototype counted on a trial round with every take set to the oldest candidate and this engine counts on the '
      'history\'s own round (found by the independent check; none here in 20,000 histories each). None changes a '
      'verdict of a claim.')
    w('')
    w('## Verdicts, in P\'s numbering')
    w('')
    n0 = N['P0']
    w('- **P0 (check): %s.** Runs grown through this study\'s wrapper equal the fold engine\'s in %s. Ties against every '
      'assignment on the 600 drawn structures, both knot laws: %s (tie classes found: %d parity, %d not-all-equal; %d '
      'frozen distinctions under parity). Sameness and renamings of Y\'s knots against every one-to-one map: %s, %d '
      'mismatches; placed positives: %s. Unit tests of the readings: %s.' % (
          V['P0'], n0['runs equal to the fold engine'], n0['drawn structures, ties against every assignment'],
          n0['tie classes found (parity, not-all-equal)'][0], n0['tie classes found (parity, not-all-equal)'][1],
          n0['frozen (parity)'], lines_kv(n0['sameness and renamings against brute force']), n0['mismatches'],
          lines_kv(n0['placed positives']), n0['unit tests of the readings']))
    n1 = N['P1']
    w('- **P1 (check; S4): %s.** %d runs under COPY-LAW(t) with MET, STEPS-1 and STEPS-2: %d births with another '
      'fresh count. The exceptions are only those P names: %s.' % (
          V['P1'], n1['runs read (COPY-LAW(t); MET, STEPS-1, STEPS-2; four rules; both knot laws; three starts)'],
          n1['births with another count'], j(n1['the allowed exceptions, births (kind | fresh count)'])))
    n2 = N['P2']
    w('- **P2 (check; S2): %s.** Not-all-equal runs and histories read: %s; with a tie class containing a made '
      'distinction: %d. The 60 third-pattern starts: e has three holders in all %s; no tie and no frozen distinction '
      'at round 0 under either knot law: %s. (Run O\'s tie classes: under PO2.)' % (
          V['P2'], j(n2['not-all-equal runs and histories read']), n2['with a tie class containing a made distinction'],
          n2['the third-pattern starts']['starts'], n2['the third-pattern starts']['no tie or frozen distinction under either knot law']))
    n3 = N['P3']
    w('- **P3 (a): %s.** Parts the same as the two-knot part after a round t >= 3 under Q, MET, STEPS-1, STEPS-2 '
      '(COPY-LAW(t), CAP-3(t)): %d. The parts at rounds 0 to 2 (start | rule | round | count: runs): %s. With no '
      'taking rule, round by round equal to starts.json: parity %s; not-all-equal (reported) %s. Under FBP(t) '
      '(reported): %s.' % (
          V['P3'], n3['parts the same as the two-knot part after a round t >= 3 under a taking rule'],
          j(n3['parts after rounds 0 to 2 under a taking rule (start, rule, round, count: runs)'], 900),
          n3['no taking rule, parity, equal to starts.json'],
          n3['no taking rule, not-all-equal, equal to starts.json (reported)'],
          j(S['_run1']['FBP(t) runs with a part the same as the two-knot part after a round >= 3 (reported)'], 500)))
    n4 = N['P4']
    w('- **P4 (check; the owner\'s step 2): %s.** %s. Parity, two holders: %s. Not-all-equal, two holders: %s.' % (
        V['P4'], lines_kv(n4['checks']), j(n4['parity counts']), j(n4['not-all-equal counts'])))
    n5 = N['P5']
    w('- **P5 (check): %s.** Under COPY-LAW(t) with MET or STEPS-1, %d parts the same as a member of the class '
      'contain a member made after round s (%s), and %d of them have a made member that is not an offshoot of a start '
      'knot; %d runs A read for renamings of Y\'s knots among the made knots, %d with one.' % (
          V['P5'], n5['parts the same as a member of the class with a member made after round s'],
          j(n5['parts by design, member and taking rule']),
          n5['of them with a made member that is not an offshoot of a start knot'],
          n5['runs A under COPY-LAW(t) read for renamings of Y\'s knots'], n5['with a renaming among the made knots']))
    n6 = N['P6']
    cs = n6['the case']
    w('- **P6 (a): %s.** Runs with two usable loose made distinctions tied to one place of Y, made by X, under the '
      'stated rules (of %d runs read): %s. The case: distinctions %s, both descended from X only, tied to place %s '
      '(a place of a member of Y) at round %s; v has %s holders at round 6; every knot passes: %s. B(i): %s. Two users '
      '(8 rounds): %s. made-2-exchanged: %s.' % (
          V['P6'], n6['runs read'], '; '.join(n6['runs with two of a place of Y made by X (stated rules; made-2 to '
                                                  'made-6 and the six designs with Y present from round 0)']),
          cs['two'], cs['v'], cs['round'], cs['holders of v after round 0 and at the round seen'][1],
          cs['every knot passes'], j(cs['B(i)']), j(cs['two users'], 400),
          n6['made-2-exchanged (reported)'] or 'none'))
    for k, label in (('P7a', 'demand before the takes and HOLD'), ('P7b', 'the other three rules'),
                     ('P7c', 'the renamings n1 to n4'), ('P7d', 'the other base laws, FBP(t), STEPS-1')):
        w('- **%s: %s.** P6\'s case under %s (survives, round): %s.' % (k, V[k], label, j(N[k], 900)))
    n8 = N['P8a']
    w('- **P8a (a): %s.** %d lists: %d give the two at their round, %d with every knot passing; the full basis gives '
      'the listed two in %d; the holders of v are as listed in %d; lists whose two appear before the listed round: %s.' % (
          V['P8a'], n8['lists'], n8['give the two'], n8['every knot passing'], n8['found by the full basis as listed'],
          n8['holders of v as listed'], n8['two seen earlier than the listed round'] or 'none'))
    w('- **P8b (c): reported.** Every choice, per design, base law and knot law (mode; histories; with two of a place '
      'of Y made by X; of them every knot passing; stopped by the guard), under the take-by-take weighting where drawn:')
    for k, v in sorted(N['P8b'].items()):
        w('  - %s: %s, %s; %s; %s; guard %s' % (k, v['mode'], v['histories'], v['with two of a place of Y made by X'],
                                                v['of them every knot passing'], v['stopped by the guard']))
    w('  Seen: %s.' % S['P8b']['note'])
    w('- **P9 (c): reported.** COPY-LAW(CANCEL-OFFSHOOT), parity, histories with two by whose place and who made them '
      '(take-by-take weighting): %s; pooled: %s.' % (j(N['P9']['per design'], 2500), j(N['P9']['pooled'])))
    n10 = N['P10']
    w('- **P10 (a): %s.** Knot verdicts read in runs 1 to 3: %d under parity, %d under not-all-equal. Under '
      'not-all-equal, tests with a failing knot: %d. Under parity: %d tests with a failing knot, every failing knot a '
      'join (%s); first of them: %s. Method disagreements: %d. Run 4: replayed lists with a failing knot %d; histories '
      'with two of a place of Y made by X %d, of them every knot passing %d. Run 5: runs read %d, with a failing knot '
      '%d under parity and %d under not-all-equal. Every case counted passes (see the cases below).' % (
          V['P10'], n10['knot tests read in runs 1 to 3 (verdicts, parity / not-all-equal)'][0],
          n10['knot tests read in runs 1 to 3 (verdicts, parity / not-all-equal)'][1],
          n10['tests with a failing knot under not-all-equal'], n10['tests with a failing knot under parity'],
          j(n10['failing knots by kind (parity)']), j(n10['parity failures (first 8)'], 1500),
          n10['method disagreements'], n10['run 4: replayed lists with a failing knot'],
          n10['run 4: histories with two of a place of Y made by X / of them every knot passing'][0],
          n10['run 4: histories with two of a place of Y made by X / of them every knot passing'][1],
          n10['run 5: runs read / with a failing knot (parity, not-all-equal)'][0],
          n10['run 5: runs read / with a failing knot (parity, not-all-equal)'][1],
          n10['run 5: runs read / with a failing knot (parity, not-all-equal)'][2]))
    w('  Run 2\'s runs A with a failing knot (failing verdicts): %s (seen: 4 failing verdicts in one run, made-2, '
      'CAP-3(CANCEL-WAIT), MET(NEWEST), the fold study\'s two joins of twelve parents at round 5; the prototype\'s 1,584 '
      'runs did not include made-2-exchanged). The failures in comparison runs and in run 1 are all joins as well, and '
      'were not in the disclosure, which names run A.' % j(n10.get('run 2, runs A with a failing knot'), 600))
    n11 = N['P11']
    w('- **P11 (a): %s.** C(r, b) read for %d pairs of family, base law and rule (MET, parity). Members with two '
      'before the renamings: %s; after every registered renaming: %s. Seen: %s.' % (
          V['P11'], n11['laws and rules read'], j(n11['with a member before the renamings']),
          j(n11['with a member after the renamings']) if n11['with a member after the renamings'] else 'none',
          S['P11']['note']))
    n12 = N['P12']
    w('- **P12 (a): %s.** CF(r, b) under MET holds for: %s. Laws with two parts the same as Y, every member '
      'descended from X only, under MET: %s; under STEPS-1 (reported): %s.' % (
          V['P12'], n12['CF(r, b) holds for (MET)'] or 'none',
          j(n12['laws with two parts the same as Y made by X only (MET)']), j(n12['under STEPS-1 (reported)'])))
    for cf in n12['the cases']:
        w('  - %s, %s: two at round %s; condition 2: fewer than two of every other member %s, every other member has '
          'two in its own run %s; registered renamings %s; X alone has two of Y (X\'s own course) %s; B(i) has two %s; X\'s course '
          'with Y barred first differs at %s; X\'s course against X alone first differs at %s; in the run with each other '
          'member, the most parts the same as this Y at a round: %s.' % (
              cf['design'], cf['law'], cf['round'], cf['condition 2, fewer than two of every other member'],
              cf['condition 2, every other member has two in its own run'], j(cf['renamings']),
              cf['X alone has two of Y (X\'s own course)'], cf['B(i) has two'],
              cf['X\'s course with Y barred first differs at'], cf['X alone first differs at'],
              j(cf['in the run with each other member, the most parts the same as this Y'])))
    w('  Seen: %s.' % S['P12']['note'])
    n13 = N['P13']
    w('- **P13 (a): %s.** The form classes by this engine\'s census: %s; dropped: %s. Runs with a part the same as the '
      'member\'s Y (any descent / every member descended from X only): made family (%d runs) %s / %s; family with Y '
      'present from round 0 (%d runs) %s / %s. Under not-all-equal every form reading equals the one under parity, run '
      'by run: %s. Seen: %s. **The made family\'s counts differ for made-4, made-5 and made-6: see "Disagreements".**' % (
          V['P13'], j(S['P13']['the form classes']), S['P13']['dropped'], n13['made']['runs'],
          j(n13['made']['members made']), j(n13['made']['by descent from X only']), n13['ystart']['runs'],
          j(n13['ystart']['members made']), j(n13['ystart']['by descent from X only']),
          n13['not-all-equal equal to parity, run by run'], S['P13']['note']))
    n14 = N['P14']
    w('- **P14 (check): %s.** Two-knot start, no taking rule, rounds 2 to 7: %s. Placed by hand: %s.' % (
        V['P14'], j(n14['two-knot start, no taking rule, rounds 2 to 7'], 900), j(n14['placed by hand'], 900)))
    w('- **P16 (check; B3): %s.** Form cases made by X only that meet condition 2: %d, so there is nothing for the '
      'fourth mark to be checked on.' % (V['P16'], N['P16']['form cases made by X only meeting condition 2']))
    w('- **P17 (c): reported.** The fourth mark on the replacement runs, on the renamed trace: %s; on the parts by '
      'descent: %s. Seen: %s.' % (j(N['P17']['on the renamed trace']), j(N['P17']['on the parts by descent']),
                                    S['P17']['note']))
    w('- **P18 (c): reported.** X\'s course against X alone (taking rule | designs: runs differing): %s. Seen: %s.' % (
        j(N['P18']), S['P18']['note']))
    n19 = N['P19']
    w('- **P19 (c): reported.** The second pattern handing on its own value, run A: %d runs (%s); with X barred: %d; '
      'the same runs: %s. Y returning (form): %d runs A, %d with X barred. Seen: %s.' % (
          len(n19['Y handing on its own value, run A']), '; '.join(n19['Y handing on its own value, run A']),
          len(n19['with X barred']), n19['the same runs'], n19['Y returning (form), run A'], n19['with X barred'],
          S['P19']['note']) if isinstance(n19['with X barred'], list) else
      '- **P19 (c): reported.** The second pattern handing on its own value, run A: %d runs (%s); the same with X '
      'barred: %s. Y returning (form): %d runs A, %d with X barred. Seen: %s.' % (
          len(n19['Y handing on its own value, run A']), '; '.join(n19['Y handing on its own value, run A']),
          n19['the same runs'], n19['Y returning (form), run A'], n19['with X barred'], S['P19']['note']))
    if p20:
        one = p20['ystart-one-2']
        w('- **P20 (a): %s.** The smallest second pattern of the class that P6\'s case fails on is one member holding '
          'two (P6 holds for three-222 only). Under the case\'s law on ystart-one-2: in round 3 the takes of births '
          'descended from X only are %s (clause 1: %s); after round 6 the usable loose made distinctions descended from '
          'X only are %s (clause 2: %s). In the case itself (three-222) the three takes of round 3 take %s.' % (
              'holds' if p20['clause 1 (all three takes of round 3 take Y\'s fresh distinction 17)'] and
              p20['clause 2 (three usable loose made distinctions of X, tied to three different start distinctions)']
              else 'fails',
              j([(t['birth'], t['took'], t['maker descent']) for t in one['round 3: takes of births descended from X only']]),
              p20['clause 1 (all three takes of round 3 take Y\'s fresh distinction 17)'],
              j([(r['distinction'], r['tied to start distinctions (names)'], r['their labels']) for r in
                 one['after the last round: usable loose made distinctions descended from X only']]),
              p20['clause 2 (three usable loose made distinctions of X, tied to three different start distinctions)'],
              j([t['took'] for t in p20['ystart-three-222 (the case, beside it)']['round 3: takes of births descended from X only']])))
    no1 = N['PO1']
    w('- **PO1 (check; B1): %s.** Runs A of run 2 read: %d, failing: %d; pairs of run 3 read: %d, failing: %d.' % (
        V['PO1'], no1['runs A read (run 2)'], len(no1['failing']), no1.get('pairs read (run 3)', 0),
        len(no1.get('failing (run 3)', []))))
    no2 = N['PO2']
    w('- **PO2 (a): %s.** Run O: %d runs, %d read (%d errors); the relation on D0 changes under FLOOR0 in %s and under '
      'ONE-FEWER in %s (parity %d, not-all-equal %d); by births descended from Y only in %d (%s; %s; %s); of them with '
      'every knot passing at that round: %d. Not-all-equal runs with a tie class containing a made distinction: %d. '
      'Seen: %s.' % (
          V['PO2'], no2['runs'], no2['read'], no2['errors'], no2['changed under FLOOR0'], no2['changed under ONE-FEWER'],
          no2['changed, parity / not-all-equal'][0], no2['changed, parity / not-all-equal'][1],
          no2['by births descended from Y only'], j(no2['of them by ration']),
          j(no2['of them by knot law and taking rule']), j(no2['of them by design']),
          no2['of them with every knot passing at that round'],
          no2['not-all-equal tie classes with a made distinction (runs with one)'], S['PO2']['note']))
    no3 = N['PO3']
    al = no3['all']
    w('- **PO3 (replication): %s.** X\'s course differs with Y barred in %d of %d runs, %d through a meeting; Y\'s with '
      'X barred in %d, %d through a meeting (seen 652, 560; 457, 357). Per base law without made-2-exchanged: %s (seen '
      '50, 276, 240). Every cell of the owner\'s arm\'s table C.1 is reproduced except one: Y present from round 0, five '
      'members, CAP-3: Y differs through a meeting in 70 here, 68 seen. The ways of X\'s differences: %s, through a '
      'meeting %s (seen: a group or owing 340 (284), the fresh count 312 (276)). T: %s (seen 1,606, 54, 66, 2). '
      'Differences from the disclosure: %s; replayed under "Disagreements".' % (
          V['PO3'], al['X differs'], al['runs'], al['X differs (meeting)'], al['Y differs'], al['Y differs (meeting)'],
          j(no3['X differs per base law, without made-2-exchanged (version 2\'s P15: 50, 276, 240 of 528)']),
          j(no3['ways of X\'s differences']), j(no3['of them through a meeting']), j(no3['T']),
          j(S['PO3']['differences from the disclosure'])))
    w('  The table, row by row (runs; X differs (meeting); Y differs (meeting); X takes from Y; Y takes from X; X ended, '
      'not with Y barred; Y ended, not with X barred; (ii); (ii) reverse; (iii); (iii) reverse; waits):')
    for k, v in no3['table'].items():
        w('  - %s: %d; %d (%d); %d (%d); %d; %d; %d; %d; %d; %d; %d; %d; %d' % (
            k, v.get('runs', 0), v.get('X differs', 0), v.get('X differs (meeting)', 0), v.get('Y differs', 0),
            v.get('Y differs (meeting)', 0), v.get('X takes from Y', 0), v.get('Y takes from X', 0),
            v.get('X ended, not with Y barred', 0), v.get('Y ended, not with X barred', 0), v.get('(ii)', 0),
            v.get('(ii) reverse', 0), v.get('(iii)', 0), v.get('(iii) reverse', 0), v.get('Waits', 0)))
    w('  All: %s.' % j(al))
    no4 = N['PO4']
    w('- **PO4 (replication): %s.** Of X\'s differences through a meeting: %s (seen: no take 370, same round 60, after '
      '126, strictly before 4); without the controls %s (seen 234, 42, 80, 4). Of Y\'s: %s (seen 240, 40, 62, 15). '
      'X\'s unconfirmed differences %d, with a take from the other at or before the differing round %d (seen 92, 32). '
      'Pattern-runs with members left and no birth in round T that do not wait: %d (seen: none). The two runs of PO3\'s '
      'difference are the two "after" more here.' % (
          V['PO4'], j(no4['X\'s differences through a meeting']), j(no4['without the controls']),
          j(no4['Y\'s differences through a meeting']), no4['X\'s unconfirmed differences'],
          no4['of them with a take from the other at or before'],
          no4['pattern-runs with members left and no birth in round T, not waiting']))
    w('- **PO5 (replication): %s.** Reading (ii) holds in %d runs: %s.' % (
        V['PO5'], len(N['PO5']), '; '.join('%s (T = %s; X ends, in A, B(i), M: %s; X\'s course differs at %s by %s, '
                                          'through a meeting %s; Y\'s course differs at %s; takes %s)' % (
                                              x['run'], x['T'], x['X ends (A, B(i), M)'], x['X course']['differs'],
                                              x['X course']['way'], x['through a meeting'], x['Y course']['differs'],
                                              j(x['takes'])) for x in N['PO5'])))
    w('- **PO6 (replication): %s.** The reverse of (ii) holds in %d runs, every one through a meeting: %s.' % (
        V['PO6'], len(N['PO6']), '; '.join('%s (Y ends, in A, B_X, M_Y: %s; takes %s)' % (
            x['run'], x['Y ends (A, B_X, M_Y)'], j(x['takes'])) for x in N['PO6'])))
    no7 = N['PO7']
    w('- **PO7 (a; B2): %s.** X and Y end in the same round: %s. Takes in one direction only: %s (here and not '
      'disclosed: %s; disclosed and not here: %s).' % (
          V['PO7'], j(no7['X and Y end in the same round (design, same: runs)']),
          '; '.join('%s %s %s(%s) %s: %s' % tuple(x) for x in no7['takes in one direction only']),
          no7['here, not disclosed'] or 'none', no7['disclosed, not here'] or 'none'))
    w('- **PO8 (check / replication; B2): %s.** made-2 at round s + 4, (X\'s state / Y\'s state): runs, and whether the '
      'counts are unchanged when X and Y are exchanged:' % V['PO8'])
    for k, v in N['PO8'].items():
        w('  - %s (%s): %s; unchanged: %s' % (k, v['mode'], j(v['counts'], 900), v['unchanged when X and Y are exchanged']))
    no9 = N['PO9']
    w('- **PO9 (c): reported.** Reading (iii) holds in %d runs, its reverse in %d (seen 70 and 8). (iii): %s. Reverse: '
      '%s.' % (no9['(iii)'], no9['(iii) reverse'], '; '.join(no9['(iii) runs']), '; '.join(no9['(iii) reverse runs'])))
    no10 = N['PO10']
    w('- **PO10 (c): reported.** Reading (iv). Under the stated rule:')
    for r in no10['the stated-rule cases']:
        w('  - %s, Z = %s named %s Y: (iv) holds %s; with Z, two of Y at %s, two of Z at %s; Z barred, two of Y at %s, '
          'two of Z at %s; Z %s; failing knots %s' % (
              r['case'], r['Z'], r['where'], r['(iv) holds'], r['with Z: two of Y at'], r['with Z: two of Z at'],
              r['Z barred: two of Y at'], r['Z barred: two of Z at'], (r['Z in round T'] or {}).get('state'),
              r['knot fails']))
    w('  Under the %d take lists of the designs with Y present from round 0: %s. Seen: %s.' % (
        no10['lists read'], j(no10['the take-list cases'], 1200), S['PO10']['note']))
    na = N['POA']
    w('- **POA (the owner\'s, A248): %s.** (i): %s. %s Readings (ii) to (iv) are PO5, PO6, PO9 and PO10 and are not '
      'called support for his second sentence.' % (
          V['POA'], na['(i)'], ('A copier for some members: %s.' % j(na['a copier for some members (law and rule: '
                                                                     'members)'])) if na['a copier for some members '
                                                                                         '(law and rule: members)'] else
          ''))
    w('')
    # ---------------------------------------------------------------------------------------------- built, stop rule
    b = S['_built']
    w('## The built-structure reading')
    w('')
    w('Runs A of run 2 read for renamings of Y\'s knots among the made knots: %d; with one at some round: %d%s; runs '
      'in which the search met its bound of 10,000 sets: %d. Run 3: no pair with two (above).' % (
          b['runs A read'], len(b['with a renaming of Y\'s knots among the made knots at some round']),
          (' (%s)' % '; '.join(b['with a renaming of Y\'s knots among the made knots at some round'])) if
          b['with a renaming of Y\'s knots among the made knots at some round'] else '', b['with the search bound met']))
    w('')
    f1 = {}
    for k, v in N['P8b'].items():
        dsg, base, kl = [x.strip() for x in k.split('|')]
        if kl == 'parity':
            f1.setdefault(base, {})[dsg] = v['with two of a place of Y made by X']
    w('## Where the stop rule stands (P, "Runs and stop rule")')
    w('')
    w('- **Values under not-all-equal**: the reason S2 gives holds in every run and history read (P2): no made '
      'distinction is tied to another. No made pattern leaves two of a place of Y there, under these laws, from these '
      'tie-free starts.')
    w('- **Form and built structure under COPY-LAW(t)**: the reason S4 gives holds (P1, P5): every birth other than an '
      'offshoot of a start knot receives one fresh distinction, so no part with a member holding two is made after the '
      'start\'s own offshoots, and no renaming of Y\'s knots is among the made knots.')
    w('- **Values under parity**: neither a copier nor a reason. The bounded report: the one stated-rule case (P6; '
      'supplied, lost under every renaming); every choice, histories with two of a place of Y made by X, under the '
      'take-by-take weighting, per base law and design: %s. The knot law allows it; the choice decides it; the question '
      'under parity is not decided.' % j(f1, 1500))
    w('- **Form under the form arm\'s laws**: the bounded negative: the census (P13), the controls of the readings '
      '(P14), the cases (P12) and the swaps (run 5). The form arm has no every-choice control.')
    w('')
    # ---------------------------------------------------------------------------------------------- disagreements
    w('## Disagreements with the disclosed prototype numbers, and what the replays show')
    w('')
    if rp:
        k = [x for x in rp if x.startswith('PO3')][0]
        a = rp[k]['parity']
        w('1. **PO3 and PO4: Y\'s course confirmed through a meeting in 359 runs here, 357 seen; the PO4 row for Y gives '
          '"after" 64 here, 62 seen.** Every other count of PO3 and PO4 is reproduced. The two runs are ystart-one-2 '
          'under CAP-3(CANCEL-OFFSHOOT), MET(NEWEST), under both knot laws. Replayed birth by birth (`replays.json`): run '
          'A stops at the fold engine\'s guard in round %d (%s), so it reaches round %d and T = %d; B(i), B_X, M and M\'_Y '
          'reach round %s. Y\'s course in run A differs from B_X at round %s (%s). Y\'s course in M is the same as in B_X '
          'through T (%s), and differs from it at round %s (%s) when the two are compared through the last round both '
          'reached, where M\'_Y differs from B_X too. So the confirmation is "through a meeting" at T, as D 7.1 says '
          '("every comparison is made at T"), and "unconfirmed" through rounds 5 and 6, which no run of the reading '
          'other than M, M\'_Y and the barred runs reached. Comparing M with B_X through their own last round gives '
          'exactly the disclosed 357 and 62, and changes no other run of run 2 (checked on every run with T < 6). The '
          'listing decides for D 7.1\'s reading; the prototype\'s count is reproduced by the other reading. A finding '
          'about the engines, not about the claim.' % (
              a['A stopped']['guard']['round'], '%s %s' % (a['A stopped']['guard']['what'], a['A stopped']['guard']['value']),
              a["rounds reached (A, B(i), B_X, M, M'_Y)"][0], a['T'], a["rounds reached (A, B(i), B_X, M, M'_Y)"][1:],
              a['Y course, A against B_X through T']['differs'], a['Y course, A against B_X through T']['way'],
              'no difference through round %d' % a['T'],
              a['Y course, M against B_X through the last round both reached']['differs'],
              a['Y course, M against B_X through the last round both reached']['way']))
        k = [x for x in rp if x.startswith('P13: the census')][0]
        c13 = rp[k]
        flk = [x for x in rp if x.startswith('P13 with')]
        fl = rp[flk[0]] if flk else {'members made': 'not run', 'by descent from X only': 'not run', 'runs': 0}
        ex = c13['made-6']['rows'][0]
        w('2. **P13: the census of the made family.** Here: made-3 47 (46 from X only), made-4 15 (14), made-5 7 (7), '
          'made-6 34 (18); seen: 47 (46), 13 (13), 6 (6), 11 (11). The family with Y present from round 0 is reproduced '
          'exactly. Broken down by base law, the extra runs are all under CAP-3(t): made-4 2 runs, made-5 1, made-6 23 '
          '(7 of them from X only); under FBP(t) the counts are 13, 6 and 11, the disclosed numbers. Replayed '
          '(`replays.json`, every counted run listed with its part, the part\'s members with h and k, their parents, '
          'kinds and descents, the maximal met sets, and the reference): under CAP-3(t) the ration gives the offshoots '
          'of made-6\'s second start knot three loose distinctions each (the demand of six siblings), so made-6\'s Y '
          'after round 1 is six members with h = 3 in one maximal met set; under FBP(t) and COPY-LAW(t) it is six '
          'members with h = 2. Example: %s, round %s: the part %s, maximal met sets %s, against the reference %s with '
          'maximal met sets %s: the same by SD lines 29–30. The engine compares, as dev 4 takes D 3.1, with each member\'s '
          'Y after round s in run A of that member\'s design under the same law. Comparing instead every law\'s parts '
          'with each member\'s Y after round s under COPY-LAW(t) with the same treatment, taking rule, rule and knot law '
          'gives %s from X only, over %d runs: exactly the disclosed numbers. So the disagreement is which run "Y as it '
          'was after round s" is taken from for a member that is not the run\'s own second pattern; it changes no verdict '
          'of P13 (the same members are made and dropped either way). A finding about the engines.' % (
              ex['design'] + ' under ' + ex['law'], ex['first round'],
              j(ex['the part (knot, h, k, places, parents, kind, descent)'], 500), j(ex['its maximal met sets']),
              j(ex['the reference: made-6\'s Y after round 1 (knot, h, k, places, parents)'], 400),
              j(ex['the reference\'s maximal met sets']),
              '%s, %s' % (j(fl['members made']), j(fl['by descent from X only'])), fl['runs']))
    if rp:
        gk = [x for x in rp if x.startswith('P8b')]
        if gk:
            gl = rp[gk[0]]
            g = {k: N['P8b'].get('%s | CAP-3(CANCEL-OFFSHOOT) | parity' % k, {}) for k in ('made-4', 'made-5', 'made-6')}

            def lastrow(h):
                return h[-1] if h else {}
            w('3. **P8b: the guard under CAP-3(CANCEL-OFFSHOOT).** Seen: the fold engine\'s guard stopped 4,867, 5,000 and '
              '5,000 of 5,000 drawn histories of made-4, made-5 and made-6 before round s + 4, so those were not read. Here, '
              'of 20,000 drawn histories each, stopped by the guard: made-4 %s, made-5 %s, made-6 %s; histories with two of '
              'a place of Y made by X: %s, %s, %s. Replayed (`replays.json`: the first three histories of each, drawn as run '
              '4 draws them, round by round with knots, members, the roster\'s joinable pairs and largest met set against '
              'the guard\'s %s pairs): no round of growth and no roster through round s + 4 meets the guard; made-5 and '
              'made-6 pass 500 knots at round s + 4 (%s and %s knots in the first history), which ends the history after '
              'that round is read, as P\'s bounds say; made-4 ends round s + 4 with %s knots and passes 500 only in round '
              's + 5, which is not read. No roster read at any round of 20 histories per design met the guard either. The '
              'prototype\'s stops are not reproduced by this engine\'s growth or rosters through the registered rounds; '
              'the listing decides, and these three designs are read here. A finding about the engines.' % (
                  g['made-4'].get('stopped by the guard'), g['made-5'].get('stopped by the guard'),
                  g['made-6'].get('stopped by the guard'), g['made-4'].get('with two of a place of Y made by X'),
                  g['made-5'].get('with two of a place of Y made by X'),
                  g['made-6'].get('with two of a place of Y made by X'), gl['guard limits'].get('pairs'),
                  lastrow(gl['made-5'][0]).get('knots'), lastrow(gl['made-6'][0]).get('knots'),
                  lastrow(gl['made-4'][0]).get('knots')))
    for i, d in enumerate(S.get('_disagreements_more', []), 4):
        w('%d. %s' % (i, d))
    w('')
    # ---------------------------------------------------------------------------------------------- the cases
    w('## Every case of two of Y, with its three verdicts (D 5.2)')
    w('')
    for c_ in S['_cases']:
        w('- %s%s: round %s. Who made the two: %s. What fixed the takes: %s (renamings %s). Where X and the linking knot '
          'come from: %s; meeting round %s; linking knots by class %s; X and Y one part through made knots only: %s. '
          '**%s.** Failing knots in run A: %s. B(i): %s. X\'s course against X alone first differs at %s.' % (
              c_['case'], ' (control)' if c_['control'] else '', c_['round'], c_['who made the two'],
              c_['what fixed the takes'], j(c_['renamings']), c_['where X comes from'], c_['meeting round'],
              j(c_['linking knots (FD 5.7 classes: knots)']), c_['X and Y one part through made knots only'],
              'Made' if c_['made'] else 'Supplied', c_['knot fails in run A'], j(c_['B(i)'], 300), c_['X alone']))
    w('')
    if S.get('_post-freeze numberings (dev 51)'):
        w('## Added after the freeze: wider numberings (dev 51)')
        w('')
        w('Every case that passes the registered renamings for its design, run under the 4n numberings of its start (n '
          'shifts of the order of its n distinctions, each as given or reversed, with the start knots as given or '
          'reversed), the same law, rule and reading. Kept apart from the registered runs (`run7_numberings.json`); no '
          'registered verdict changes.')
        w('')
        for x in S['_post-freeze numberings (dev 51)']:
            w('- %s: %d numberings run, %d distinct named starts among them; passes %d of the %d run: %s.' % (
                x['case'], x['numberings run'], x['distinct named starts (distinct up to the start\'s symmetries)'],
                x['passes'], x['numberings run'], x['verdict']))
        w('')
    r5 = S['_run5']
    w('## Run 5: the swaps')
    w('')
    for x in r5['cases of run 2']:
        w('- %s%s: as run %s; passes the registered renamings %s; still there under %s; lost under %s.' % (
            x['case'], ' (control)' if x['control'] else '', x['as run'], x['passes the registered renamings'],
            ', '.join(x['swaps survived']) or 'nothing', ', '.join(x['swaps lost'])))
    w('- Run 3\'s cases: %s.' % (len(r5['cases of run 3']) or 'none (run 3 has no case)'))
    tl = r5['take lists']
    w('- The 33 take lists under the swaps that name no rule (dev 37), by swap (swaps; the list does not apply; two of '
      'Y made by X): %s. The translation applied to a list\'s own start and law gives the list\'s own run in %d of 33.' % (
          j(tl['by swap'], 2500), tl['identity translation gives the list\'s run']))
    fa = r5['form arm']
    w('- The form arm under n1, n3, n4, the order of births reversed, demand before the takes and HOLD: %s; runs with '
      'two parts the same as Y, every member descended from X only: %s; runs A stopped by the fold engine\'s guard: %s.' % (
          j(fa['by swap'], 1500), j(fa['cases'], 2500), fa['runs stopped by the guard']))
    w('')
    r3 = S['_run3']
    w('## Run 3: the arm of parts that came apart')
    w('')
    w('%d runs, %d pairs (%s); pairs with two of Y in a reading: %d; pairs with a made distinction descended from X tied '
      'to a place of Y at some round (any count): %d; not-all-equal runs with a tie class containing a made distinction: '
      '%d.' % (r3['runs'], r3['pairs'], j(r3['pairs by start']), len(r3['cases']),
               r3['pairs with a made distinction of X tied to a place of Y (any)'],
               r3['NAE tie classes with a made distinction (runs)']))
    w('')
    open(C.out_path('summary.md'), 'w').write('\n'.join(out) + '\n')
    C.log('wrote summary.md', len(out), 'lines')


if __name__ == '__main__':
    main()
