"""Theorem A** coverage in the registered LEVEL-REACH census at depth 9: is the knot pattern Berge-acyclic (no cycle of knots), and
does a chain of s knots, each one level down, join level 3 to level 3 + s (s = 1..4)? Then L(s) = s + 2 by RANDOM-FATES-001B's T1.
Also: how many descriptions have Theorem A's form (one distinct placement, of tree type)."""
import sys, gzip, json, collections
from collections import deque
sys.path.insert(0, 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex')
from pattern import pattern
recs = [json.loads(l) for l in gzip.open('artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt')]
exec(open('research/RULER-LEVEL-20261114-001/exploratory/census_tree_iso.py').read().split('N = 9')[0].split('def outcome')[1].join(['def outcome', '']) if False else '')
def outcome(a):
    fl = a['flags']; un = a['union']; Ls = [l['L_N'] for l in a['levels']]
    if fl['no_join']: return 'no join'
    if un == 'dead': return 'dead'
    if un != 'alive': return 'undecided'
    if any(x == 'none' for x in Ls): return 'no bond'
    if any(x == 'undecided' for x in Ls): return 'undecided'
    if all(isinstance(x, int) for x in Ls) and len(set(Ls)) == 1: return 'direct'
    if all(isinstance(x, int) for x in Ls) and all(Ls[i] == i + 3 for i in range(4)): return 'chained'
    return 'other'
N = 9; NV = (1 << (N + 1)) - 1
def lvl(i): return (int(i) + 1).bit_length() - 1
def analyse(key):
    P = [tuple(int(x) for x in k) for k in pattern(key, N)]
    parent = list(range(NV + len(P)))
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    acyclic = True
    for j, k in enumerate(P):
        for x in k:
            a, b = find(x), find(NV + j)
            if a == b: acyclic = False
            else: parent[a] = b
    if not acyclic: return 'cyclic', None
    occ = collections.defaultdict(list)
    for j, k in enumerate(P):
        for x in k: occ[x].append(j)
    dist = {x: 0 for x in range(NV) if lvl(x) == 3}; dq = deque(dist)
    while dq:
        x = dq.popleft()
        for j in occ[x]:
            for y in P[j]:
                if y not in dist: dist[y] = dist[x] + 1; dq.append(y)
    ok = all(min((d for y, d in dist.items() if lvl(y) == 3 + s), default=None) == s for s in range(1, 5))
    return 'forest', ok
tab = collections.defaultdict(collections.Counter); formA = collections.Counter()
for a in recs:
    if 'key' not in a: continue
    o = outcome(a); kind, ok = analyse(a['key'])
    tab[o][kind if kind == 'cyclic' else ('forest, chains at every s' if ok else 'forest, some s without a chain')] += 1
    pls = sorted(set(tuple(p) for p in a['key'][4]))
    if len(pls) == 1 and sorted(t % 3 for t in pls[0]) == [0, 1, 2]: formA[o] += 1
for o, c in sorted(tab.items()): print(o, dict(c))
print('Theorem A form by outcome:', dict(formA))
