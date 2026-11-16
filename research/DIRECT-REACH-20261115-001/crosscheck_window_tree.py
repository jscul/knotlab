"""Cross-check of the every-depth window computation (exploratory/window_tree.py, the thread's own) against the Codex SAT results at
N = 9 (codex/case_results/D, certified): for every bounded-orbit description and top k in {2, 3}, s = 1..(8 - k), the window tree's
tie flag at r = 9 - k - s must equal the Codex spanning tie class, and its two-orbit three-member bond (with no tie) must imply the
Codex threshold L = 3. DIRECT-REACH-20261115-001, 2026-11-16."""
import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CODEX = ROOT / 'experiments/DIRECT-REACH-20261115-001A/DIRECT-REACH-20261115-001A-E001_direct_reach/codex'
wt = json.load(open(HERE / 'exploratory/window_tree_census.json'))['cases']


def at(seqs, r0, r, s, period):
    key = 'r=%d' % r if r < r0 else 'r>=%d' % r0
    P = seqs[key]
    while s > len(P):          # P covers the prefix and two periods; reduce s by whole periods
        s -= period
    return P[s - 1]


tally = collections.Counter()
bad = []
for cid, row in wt.items():
    if 'k3' not in row:
        continue
    d = json.load(open(CODEX / 'case_results/D' / (cid + '.json')))
    span = {(x['k0'], x['s']): x['spanning'] for x in d['ties']['summaries']}
    th = {(t['k0'], lv['s']): lv['L_N'] for t in d['threshold_reach'] for lv in t['levels']}
    for k in (2, 3):
        r0 = int(row['k%d' % k]['r0'])
        seqs = row['k%d' % k]['sequences']
        for s in range(1, 9 - k):
            r = 9 - k - s
            tie, b3 = at(seqs, r0, r, s, int(row['k%d' % k]['period']))
            ct = span[(k, s)]
            L = th[(k, s)]
            if bool(tie) != bool(ct):
                bad.append((cid[:12], k, s, 'tie', tie, ct))
            tally['tie agree'] += 1
            if not tie and b3:
                tally['b3 checked'] += 1
                if L != 3:
                    bad.append((cid[:12], k, s, 'b3', L))
            if not tie and not b3 and L == 3:
                tally['L=3 by a bond outside two orbits'] += 1
            if tie and L != 2:
                bad.append((cid[:12], k, s, 'tie but L', L))
print(dict(tally))
print('disagreements', len(bad), bad[:10])
json.dump(dict(tally=dict(tally), disagreements=bad), open(HERE / 'crosscheck_window_tree.json', 'w'), indent=1)
