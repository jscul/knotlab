"""Diagnosis after the frozen run (not a prediction): at each stage of R1, which true junctions are missed and why.
Run: .venv/bin/python -B diagnose.py 15"""
import sys
from collections import Counter
from itertools import combinations
sys.path.insert(0, '.')
import ringread as R
B = R.B
T = int(sys.argv[1])
P = R.grow(T); st = R.stars_of(P); K = max(map(len, st)); truth = set(st)
tab, _ = R.bond_table(st, 6, K)
own = R.owners(st); idx = {s: j for j, s in enumerate(st)}
labels = B.table_labels(tab); stars = set()
for support in range(3, K + 1):
    raw = {p for p, d in tab.items() if d < support}
    pr = B.prune(raw, stars, support)
    new = B.clique_stars(labels, pr)
    miss = truth - new; spur = new - truth
    print('stage', support, 'missed', len(miss), 'spurious', len(spur), 'removed by prune', len(raw - pr))
    for s in list(miss)[:3]:
        j = idx[s]
        pairs = list(combinations(sorted(s), 2))
        print('   missed junction', j, 'size', len(s), 'round', P.round_of[j], 'parents', P.parents[j],
              'pair distances', Counter(tab[p] for p in pairs), 'pairs removed by prune', sum(1 for p in pairs if p in raw and p not in pr),
              'pairs not short', sum(1 for p in pairs if p not in raw))
    rs = Counter(P.round_of[j] for s in spur for b in s for j in own[b])
    if spur: print('   spurious touch rounds', dict(sorted(rs.items())))
    stars = new
