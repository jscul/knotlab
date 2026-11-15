"""Closed forks (CYCLE-RULER #1, one step at the coordinator's go-ahead): a cross-level knot K with its upper member p at a level n in
3..6 and its two lower members c0, c1 at n + 1 is a closed fork when c0 and c1 are joined by knots other than K lying wholly in levels
n + 1 .. 7 (the branches below K rejoin within the levels read). Count per cyclic census description, against the outcome."""
import sys, gzip, json, collections
sys.path.insert(0, 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex')
from pattern import pattern
src = open('research/CYCLE-RULER-20261115-001/exploratory/discriminator.py').read()
exec("def outcome(a):" + src.split("def outcome(a):")[1].split("N = int")[0])
recs = [json.loads(l) for l in gzip.open('artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt')]
TOP, LAST = 3, 7
def lvl(i): return (int(i) + 1).bit_length() - 1
def forks(key):
    P = [tuple(int(x) for x in k) for k in pattern(key, LAST)]
    L = [sorted({lvl(x) for x in k}) for k in P]
    # cycle check on the whole read region
    par = {}
    def find(x):
        while par.setdefault(x, x) != x: par[x] = par[par[x]]; x = par[x]
        return x
    cyc = False
    for j, k in enumerate(P):
        for x in k:
            a, b = find(('v', x)), find(('k', j))
            if a == b: cyc = True
            else: par[a] = b
    count = 0
    for j, k in enumerate(P):
        ls = L[j]
        if len(ls) != 2 or not (TOP <= ls[0] <= LAST - 1): continue
        n = ls[0]; top = [x for x in k if lvl(x) == n]; kids = [x for x in k if lvl(x) == n + 1]
        if len(top) != 1 or len(kids) != 2: continue
        p2 = {}
        def f2(x):
            while p2.setdefault(x, x) != x: p2[x] = p2[p2[x]]; x = p2[x]
            return x
        for i, kk in enumerate(P):
            if i == j or L[i][0] < n + 1: continue
            for x in kk[1:]: p2[f2(x)] = f2(kk[0])
        if f2(kids[0]) == f2(kids[1]): count += 1
    return cyc, count
tab = collections.defaultdict(collections.Counter)
for a in recs:
    if 'key' not in a: continue
    o = outcome(a)
    if o not in ('chained', 'direct', 'other'): continue
    cyc, c = forks(a['key'])
    if not cyc: continue
    tab[o]['no closed fork' if c == 0 else 'closed forks'] += 1
for o, c in sorted(tab.items()): print(o, dict(c))
