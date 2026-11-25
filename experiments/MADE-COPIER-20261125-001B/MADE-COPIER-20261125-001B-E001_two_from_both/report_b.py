"""summary.md from summary.json (analyze_b.py).  usage: python -B report_b.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cb  # noqa: E402


def j(o, n=900):
    s = json.dumps(o, sort_keys=True)
    return s if len(s) <= n else s[:n] + ' ...'


def main():
    S = json.load(open(cb.out_path('summary.json')))
    out = []

    def w(x=''):
        out.append(x.replace('Seen: seen', 'Seen'))
    w('# MADE-COPIER-20261125-001B, E001: every prediction\'s verdict')
    w()
    w('Written by the engine\'s author from the frozen text (commit 733d0edaeb): PB, DB, ticket B\'s claim, the data files, '
      'ticket A\'s frozen texts and starts.json, the fold study\'s and the shared definitions. The drafter\'s scratch '
      'folder and the study\'s advisor folder were not read. The growth is the fold study\'s engine and the readings '
      'both tickets use are ticket A\'s engine, both imported unchanged; the fold engine\'s guard limits are multiplied '
      'by ten at import (DB 3.9). Readings taken where the text left a choice are numbered in '
      '`experiments/MADE-COPIER-20261125-001B/MADE-COPIER-20261125-001B-E001_two_from_both/deviations.md` ("dev n"). '
      'COPY-LAW(t) is the fold study\'s name for (FLOOR1, t, RELEASE); it is not a law of copying. "Seen" quotes the '
      'prototype\'s disclosed number. No weighting is used. No claim is made about living things, minds, physics or '
      'time.')
    w()
    N = {k: S[k]['numbers'] for k in S if not k.startswith('_') and isinstance(S[k], dict) and 'numbers' in S[k]}
    p10 = N.get('PB10', {})
    w('## Findings, plainly')
    w()
    w('1. **No case of either reading, in either arm, under any registered law, in what was run** (CB-1 holds in no pair '
      'of patterns of different kinds; CB-2 for no first pattern; PBA: only supported). Arm 1 was run in full; arm 2 '
      'in full on ticket A\'s designs and on a registered-order prefix of the 256 starts in 14 of its 72 jobs (finding '
      '3). Under COPY-LAW(t) with no taking rule, six of the eight second patterns cannot be left from both, by '
      'argument (Settled 4, checked: PB5), and the census agrees.')
    w('2. **Where two parts of the second pattern\'s form are left, each descended from both, the second pattern '
      'alone and with the first barred leaves two as well.** Under COPY-LAW(t) this happens only for Y the two-knot part '
      'or a lone member holding two (%s runs through round 8; %s within 6 rounds, as seen); (a) and (b) fail in '
      'every one, (d) in most. Supplied: the meeting, built into the start (arm 1); made: the parts, by the births of the '
      'one start roster with its members marked first or second.' % (
          p10.get('runs with two parts the same as Y, each from both (X other than Y), through round 8'),
          p10.get('the same within 6 rounds')))
    cut = S.get('_b3 the cut (dev 32): starts of DB 2 read per job', {})
    n_read = sum(v[0] for v in cut.values())
    n_not = sum(v[1] for v in cut.values())
    full = sum(1 for v in cut.values() if not v[1])
    a2 = S.get('_arm2', {})
    w('3. **Under the cap of three with no taking rule (arm 1), and under MET (arm 2), no two parts of the second '
      'pattern\'s form descended from both**, with first and second pattern of different kinds (PB11, PB12), through '
      'the rounds run, by census; nothing is argued there. Under MET not one run, on ticket A\'s twelve designs or on '
      'the starts read, has even two such parts (%s jobs; %s of them read all 256 starts of DB 2, the others a prefix '
      'in the registered order: %s starts read in all, %s not run, deviations 32). Supplied in arm 2: the starts and '
      'the taking rule; made: the meetings, through takes, and in no run two parts of the second pattern\'s form '
      'each descended from both. The starts not run are not negatives.' % (
          a2.get('jobs'), full, n_read, n_not))
    w('4. **With no taking rule, the run from each renamed start was a renaming of the original run at every round**: '
      '%s renamed runs, the renaming built and checked exactly (PB1); under MET %s of the 3,456 '
      'renamed runs of the eight renamings are proven different (seen 1,860).' % (
          N.get('PB1', {}).get('renamed runs, no taking rule (RELEASE and HOLD, six base laws, both knot laws)'),
          N.get('PB1', {}).get('of them differing')))
    w('5. **PB13\'s prediction by hand fails**: under COPY-LAW(t) some forms descended from both appear with one second '
      'pattern and with no other (R2 not empty in %s of %s cases), and under COPY-LAW(CANCEL-WAIT) a fourth form, a lone '
      'member holding one, is left twice from both.' % (N.get('PB13', {}).get('under COPY-LAW: R2 not empty in'),
                                                       N.get('PB13', {}).get('of')))
    w()
    for line in S.get('_disagreements', []):
        w(line)
    w('## Verdicts, in PB\'s numbering')
    w()
    order = ['PB1', 'PB2', 'PB3', 'PB4', 'PB5', 'PB6', 'PB7', 'PB8', 'PB9', 'PB10', 'PB11', 'PB12', 'PB13', 'PB14',
             'PB15', 'PB16', 'PB17', 'PB18', 'PBA']
    for k in order:
        if k not in S:
            w('- **%s: not read.**' % k)
            continue
        v = S[k]
        w('- **%s: %s.** %s%s' % (k, v.get('verdict'), j(v.get('numbers'), 2500),
                                  ('. Seen: %s.' % v['seen']) if v.get('seen') else '.'))
        for extra in ('failing counts', 'unequal where (a) is (b)', 'conflicts (first 10)', 'note'):
            if v.get(extra):
                w('  %s: %s.' % (extra, j(v[extra], 1200)))
    w()
    for k in sorted(x for x in S if x.startswith('_')):
        if k in ('_findings',):
            continue
        w('## %s' % k.strip('_'))
        w()
        w(j(S[k], 6000))
        w()
    open(cb.out_path('summary.md'), 'w').write('\n'.join(out) + '\n')
    cb.log('wrote summary.md', len(out), 'lines')


if __name__ == '__main__':
    main()
