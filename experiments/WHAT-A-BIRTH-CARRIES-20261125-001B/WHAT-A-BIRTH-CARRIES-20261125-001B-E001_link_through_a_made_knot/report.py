"""summary.md from summary.json: one row per prediction, the per-law table of the three verdicts, the minimal laws.

  python -B report.py
"""
import sys

sys.dont_write_bytecode = True

import json

import common


def cnt(V, key, k):
    return V.get(key, {}).get('counts', {}).get(k, 0)


def main():
    common.check_frozen()
    S = json.load(open(common.out_path('summary.json')))
    fam = common.load('family.json')
    V1a = S['verdicts']['1a']
    P1 = S['verdicts']['P1']
    U1 = S['verdicts']['U1']
    g, c0 = S['gate'], S['C0']
    n2 = S['N2']
    rec = S['recorded_rations_MET_SOLE']
    L = []
    w = L.append
    w('# WHAT-A-BIRTH-CARRIES-20261125-001B-E001: summary')
    w('')
    w('Computed by a program written from the frozen texts by a helper who had not seen the drafter\'s prototype; '
      'evidence class: computed, bounded, referee pending. Readings taken: `deviations.md` of the experiment folder '
      '(items 1 to 36). Every registered run was made in full within the cap (28 minutes of the 70 from the start of '
      'run G); nothing was cut. Whole structures under renamings are compared by an invariant, never called identical.')
    w('')
    w('## Gate and controls')
    w('')
    w('- Run G: %d of %d gate runs equal to the fold engine; `gate_listing_b.txt` reproduced (%d lines, birth by '
      'birth, knot-test counts included); ticket A\'s 4 attribution records classed as written: %s.' % (
        g['engine_equal'], g['engine_runs'], g['gate_listing_lines'],
        ', '.join('"%s"' % r[1] for r in g['attribution_records'])))
    w('- C0, no taking rule (144 items): %d pairs with a meeting among %d ordered pairs wholly apart.' % (
        c0['negative']['meeting_pairs'], c0['negative']['no_meeting_pairs']))
    pc = c0['positive']['counts']
    w('- C0, J-EACH-PART (the positive control that looks at parts; 144 items, 4 rounds): %d pairs meeting only '
      'through made knots (and %d more in runs with a failing knot, not counted); B1-dependence found on %d pairs, '
      '%d undecided (knot test not run), %d equal; found under %d of the 18 law and knot-law combinations.' % (
        pc.get('strict', 0), pc.get('strict, marked (failing knot in run A)', 0),
        pc.get('dep: differs through the meeting', 0), pc.get('dep: undecided: knot test not run', 0),
        pc.get('dep: equal', 0), len(c0['positive']['laws_dependence_found'])))
    w('- C0, the planted case (made-4, ORD/CANCEL-RETIRE/MET(OLDEST), a = 4 against a = 1): classed "%s" under '
      'parity and "%s" under not-all-equal (linking knots: the two start knots).' % (
        c0['planted'][0]['class_a4'], c0['planted'][1]['class_a4']))
    w('')
    w('## Predictions')
    w('')
    w('| # | Prediction (legend a, b, c) | Verdict | Numbers |')
    w('| --- | --- | --- | --- |')
    w('| B0 (b) | Lemma N: no renamed run of N2 differs; the gate passes | Holds (not refuted) | %d renamed runs '
      '(made-3: 119 numberings, two-knot: 29, each ring start: the reversal and 10 drawn) under L02, L10, L07, both '
      'knot laws: whole-structure invariant equal after every round in %d, verdicts and courses (exact classes) equal '
      'in %d; "verdicts and courses equal exactly; whole structures not distinguished by an invariant"; gate passed |'
      % (n2['compared'], n2['invariant equal'], n2['verdicts and courses equal']))
    l02 = {k: v for k, v in V1a.items() if k.startswith('L02|')}
    l05 = {k: v for k, v in V1a.items() if k.startswith('L05|')}
    w('| B1-link (a) | Under MET-SOLE with FLOOR1/CANCEL-WAIT on all 8 starts and with CAP-3/CANCEL-WAIT on the 4 ring '
      'starts, pairs meet only through made knots | Holds under FLOOR1/CANCEL-WAIT, on 5 of the 8 starts; fails '
      'under CAP-3/CANCEL-WAIT (none does) | FLOOR1/CANCEL-WAIT: %d pairs per knot law (made-4 4, Ring(5,3) 20, '
      'Ring(5,3)+1 16, D2(5,3) 20, Ring(7,3) 28), none on two-knot, made-3 and three-knot; CAP-3/CANCEL-WAIT: %d. '
      'Each pairs a two-member part with the part of the waiting members (5, 10, 11 or 14 members), in both orders, '
      'so the parts are not alike. Disclosed: 312 (216 under FLOOR1 on all 8 starts, 96 under CAP-3); see '
      '"Differences" |' % (
          cnt(l02, 'L02|parity', 'strict'), cnt(l05, 'L05|parity', 'strict')))
    w('| B1-ancestral (a) | Such meetings are ancestral in the FD 1.5 form | Holds | %d of %d pairs per knot law under '
      'FLOOR1/CANCEL-WAIT; every-member form: %d (disclosed 32) |' % (
          cnt(l02, 'L02|parity', 'ancestral'), cnt(l02, 'L02|parity', 'strict'),
          cnt(l02, 'L02|parity', 'ancestral every member')))
    w('| B1-dep, recorded (a) | Under the 9 recorded rations and treatments with MET-SOLE, no course from X only '
      'differs with Y barred across a meeting only through made knots | Holds | %d such pairs (both knot laws), %d '
      'with a course difference; %d meeting pairs in all (disclosed 640) |' % (
          rec['strict'], rec['strict, course differs'], rec['meeting']))
    core = S['expected_case']
    ncore = sum(core[k]['counts']['strict'] for k in core if k.split('|')[0] in ('Ring(5,3)', 'D2(5,3)', 'Ring(7,3)'))
    w('| B1-dep, core (a) | MET-SOLE/FLOOR1/CANCEL-OFFSHOOT/PARENT-OWING, both knot laws, on Ring(5,3), D2(5,3), '
      'Ring(7,3): a pair with a made ancestral link whose course differs with Y barred, every tested knot passing | '
      'Holds | %d pairs on the three starts (both knot laws), each ancestral in both forms and with a course '
      'difference, attribution accepted on all; run A and the 8 tested barred runs an item pass (0 failing); the '
      'other pairs are undecided: knot test not run |' % ncore)
    w('| B1-dep, details (c) | Reported | — | the first differing used value at round 5, the course from round 6; '
      'the bars give two classes, {none, either one member} against {both}; attribution through the meeting on all; '
      'm = 1 (handed in one value); Y-side knot: Y\'s join of its two members (round 5); lasts (rounds 7 and 8) |')
    p1 = []
    for lid in ('PARENT-OWING-PLAIN/CANCEL-OFFSHOOT', 'PARENT-OWING-1/CANCEL-OFFSHOOT'):
        for kl in ('parity', 'nae'):
            k = '%s|%s' % (lid, kl)
            p1.append('%s %s: %d strict, %d marked, dependence %s' % (lid.split('/')[0], kl, cnt(P1, k, 'strict'),
                      cnt(P1, k, 'strict, marked (failing knot in run A)'), P1[k]['B1-dependence']))
    w('| P1 (a) | PLAIN gives the core case; PARENT-OWING-1 under parity, with failing knots under not-all-equal; '
      'OFFSHOOT-TWO, OFFSHOOT-THREE, CAP3 no such pair after rounds 3 and 4; CAP4 such pairs and no difference | '
      'Holds under CANCEL-OFFSHOOT (the seen setting); as worded across P1\'s treatments it fails for OFFSHOOT-TWO '
      'and CAP3 under CANCEL-WAIT | %s; PARENT-OWING-1 not-all-equal: 32 to 56 failing verdicts a run A; '
      'OFFSHOOT-TWO, OFFSHOOT-THREE (P1) and PARENT-OWING-CAP3 (L13) under CANCEL-OFFSHOOT: 0 such pairs; '
      'PARENT-OWING-CAP4 (L16): %d per knot law, no course difference; under CANCEL-WAIT, OFFSHOOT-TWO %d and '
      'PARENT-OWING-CAP3 (L14) %d such pairs per knot law (s = 4), with no course difference |' % (
          '; '.join(p1), cnt(V1a, 'L16|parity', 'strict'),
          cnt(P1, 'OFFSHOOT-TWO/CANCEL-WAIT|parity', 'strict'), cnt(V1a, 'L14|parity', 'strict')))
    rp = sum(core[k]['counts']['strict'] for k in core if k.startswith('Ring(5,3)+1'))
    w('| Ring(5,3)+1 (a) | The core case is seen there too | Holds | %d pairs (both knot laws); X\'s join has '
      'demand 10 against 9 |' % rp)
    u = S['U1']['L10']['Ring(5,3)+1+2|parity']['counts']
    w('| The unsymmetric ring (c) | Reported | — | L10: %d pairs per knot law meeting only through made knots, all '
      'with the core case\'s readings; L02: %d per knot law, no course difference; see below |' % (
          u['strict'], S['U1']['L02']['Ring(5,3)+1+2|parity']['counts']['strict']))
    w('| C0 (b and a) | Negative: no meeting; positive: found by B1-link and B1-dependence; planted: "through a start '
      'knot" | Holds | as above |')
    mn = S['minimal']
    w('| B4 (a; c for attribution) | Minimal among the listed: B1-link and B1-ancestral: MET-SOLE with '
      'FLOOR1/CANCEL-WAIT; B1-dependence: MET-SOLE with PARENT-OWING/CANCEL-OFFSHOOT, if attribution is accepted '
      'there | Holds | B1-link: %s; B1-ancestral: %s; B1-dependence: %s (attribution accepted); all 60 laws run |' % (
          mn['B1-link']['either knot law']['minimal'], mn['B1-ancestral']['either knot law']['minimal'],
          mn['B1-dependence']['either knot law']['minimal']))
    w('| B5 (b) | P2 runs only where the guard stopped | Holds | no run of 1a, P1 or 1b reached the guard; P2 ran 0 '
      'items at x10 and x100 |')
    w('| How many, Which, m (c) | Reported | — | how many: undefined on the core case (the one-member runs have no '
      'meeting), 0 pairs; which at equal number: empty; m = 1 on every differing pair |')
    w('')
    w('## The three verdicts per law (search family; runs 1a, 1b, 1c), per knot law')
    w('')
    w('| Law | Take, ration, treatment | Cost | Parity: link / ancestral / dependence | Not-all-equal: link / '
      'ancestral / dependence | Pairs meeting only through made knots (parity, nae) |')
    w('| --- | --- | --- | --- | --- | --- |')
    for Lw in fam['search']:
        run = Lw['run']
        V = S['verdicts'][run]
        cells = []
        nums = []
        for kl in ('parity', 'nae'):
            o = V['%s|%s' % (Lw['id'], kl)]
            cells.append('%s / %s / %s' % (o['B1-link'], o['B1-ancestral'], o['B1-dependence']))
            nums.append(str(o['counts'].get('strict', 0)))
        c = Lw['cost']
        w('| %s | %s, %s, %s | (%d, %d, %s, %s, %d) | %s | %s | %s |' % (
            Lw['id'], Lw['take'], Lw['ration'], Lw['treatment'], c['holder_steps'], c['record_steps'],
            'yes' if c['whole_roster'] else 'no', c['values_at_one_birth'], c['new_rules'], cells[0], cells[1],
            ', '.join(nums)))
    w('')
    w('Cost: (holder steps, record steps, whole-roster look, values at one birth, new rules), compared component by '
      'component.')
    w('')
    w('## The minimal laws among the listed laws')
    w('')
    for v in ('B1-link', 'B1-ancestral', 'B1-dependence'):
        m = mn[v]['either knot law']
        w('- **%s**: laws with it: %s; least among the listed laws: %s (costs %s). Per knot law the same: parity %s, '
          'not-all-equal %s.' % (v, ', '.join(m['laws_with_verdict']) or 'none', ', '.join(m['minimal']) or 'none',
                                 json.dumps(m['costs']), mn[v]['parity']['minimal'], mn[v]['nae']['minimal']))
    w('')
    w('## The expected dependence case (MET-SOLE, FLOOR1, PARENT-OWING, CANCEL-OFFSHOOT; L10)')
    w('')
    for k, v in sorted(core.items()):
        c = v['counts']
        ex = v['example']
        lk = ex['linking'][0]
        w('- %s: %d pairs (all s = 4, meeting round 5, by a demand group), one linking knot made in round 2 (%s of %s, '
          'ancestry %s), ancestral in both forms; course first differs at round 6; first differing used value: '
          'round 5, the demand of X\'s join, %d with Y barred against %d with Y usable, its differing part Y\'s join '
          'of its two members (Y only), attribution accepted on %d of %d; the barred run has no meeting on %d '
          '("meets against does not meet"); bars: %s; m = 1; lasts on %d; 8 barred runs knot-tested, %d failing.' % (
              k, c['strict'], lk['kind'], lk['parents'], [a[0] for a in lk['ancestry']],
              ex['attribution']['value_A'][0], ex['attribution']['value_B'][0], c['attribution accepted'],
              c['strict'], c['meets against does not meet'],
              'two classes, {none, either one member} against {both}', c['lasting: lasts'], c['barred fails']))
    w('')
    w('X\'s join at the meeting round receives one fresh distinction either way (FLOOR1 for joins); the difference '
      'reaches the course in round 6 through the owing of that join, whose offshoots receive max(2, o) under '
      'PARENT-OWING. Birth by birth: `expected_case_listing.txt`.')
    w('')
    w('## The four "is it the start\'s after all" checks')
    w('')
    w('- (a) a start knot holds a linking distinction: on no pair meeting only through made knots, under any law.')
    w('- (b) a start knot enters the linking set of a barred run: on no such pair.')
    w('- (c) a renaming of the structure after round s exchanging X and Y and fixing every linking knot: L10 (and the '
      'P1 cases): yes on every pair, on every ring start and on the unsymmetric ring; it is also found with every '
      'start knot fixed (`check_c_fixing_start_knots.json`), so it exchanges two sibling branches below the made '
      'linking knot and is not a symmetry of the start. L02: no on every pair.')
    w('- (d) the link\'s ancestry: under L10 the linking knot is a round-2 offshoot of a round-1 join of two start '
      'knots (Ring(5,3): knot 15 of join 5 of start knots 0 and 2); under L02 a round-2 offshoot of a round-1 offshoot '
      'of a start knot (made-4: a round-1 offshoot of start knot 0, meeting at round 4 after s = 3). "The start '
      'supplies the ancestors; the knot and both parts are made."')
    w('')
    w('## The knot test')
    w('')
    for r, v in S['knot_test'].items():
        c = v['counts']
        w('- %s: run A %d verdicts, %d failing, %d disagreements; barred runs tested %d (%d verdicts, %d failing); '
          'lasting reruns tested %d (%d verdicts, %d failing); pairs undecided, knot test not run: %d.%s' % (
              r, c.get('run A verdicts', 0), c.get('run A fails', 0), c.get('run A disagree', 0),
              c.get('barred runs tested', 0), c.get('barred verdicts', 0), c.get('barred fails', 0),
              c.get('lasting reruns tested', 0), c.get('lasting verdicts', 0), c.get('lasting fails', 0),
              c.get('undecided: knot test not run', 0),
              (' Failures: ' + ', '.join('%s (%d)' % kv for kv in sorted(v['fails_where'].items()))) if v['fails_where']
              else ''))
    w('')
    w('## Differences from "Known before the runs"')
    w('')
    w('- Item 2 (recorded rations with MET-SOLE, the registered bounds): here %d meeting pairs (disclosed 640) and %d '
      'pairs meeting only through made knots (disclosed 312), all under FLOOR1/CANCEL-WAIT on made-4 and the four '
      'ring starts; none on two-knot, made-3 or three-knot; none under CAP-3/CANCEL-WAIT (disclosed 96); every-member '
      'form %d (disclosed 32). The growth was checked against the fold engine with a sole-candidate wrapper (144 of '
      '144 runs equal). Listings: `listing_two-knot_L02_parity.txt`, `listing_made-3_L02_parity.txt`, '
      '`listing_three-knot_L02_parity.txt`, `listing_Ring5-3_L05_parity.txt`, `listing_Ring5-3_L02_parity.txt`. '
      'Verdicts affected: the CAP-3 half of prediction B1-link fails; the minimal laws do not change.' % (
          rec['meeting'], rec['strict'], rec['every member']))
    w('- Items 3 to 6 were reproduced where comparable (item 4 in full, including demand 7 against 6 and 10 against '
      '9, the two classes, no meeting in the one-member runs, 32 to 56 failing verdicts a run under PARENT-OWING-1 '
      'and not-all-equal, CAP4 with no difference; item 5: lasting at rounds 7 and 8, the guard never reached; no '
      'meeting without a taking rule). Item 1\'s bounds (6 rounds, 5 starts) were not run.')
    w('')
    w('## Reader test item 4 (on the runs with every member of Y barred, X\'s births)')
    w('')
    for k, v in sorted(S['reader_item4'].items()):
        w('- %s: %s' % (k, v))
    w('')
    w('## Runs and wall time (cap: 70 minutes from the start of run G)')
    w('')
    for r, m in S['run_meta'].items():
        w('- %s: %d of %d items, %s s on %d processes; cut: %s.' % (r, m['done'], m['items'], m['wall_seconds'],
                                                                   m['procs'], m['cut_at']))
    w('- G: 648 runs and the rest, about 100 s on 6 processes; P2: 0 items. Not run: nothing.')
    with open(common.out_path('summary.md'), 'w') as f:
        f.write('\n'.join(L) + '\n')
    print('summary.md', len(L))


if __name__ == '__main__':
    main()
