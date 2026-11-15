"""Which registered LEVEL-REACH descriptions have, at depth 9, a knot pattern that is exactly a full binary tree across levels (no
knot within a level; every joining knot one address above and two below; every address of levels 0..8 above in exactly one knot,
every address of levels 1..9 below in exactly one)? Those are rulers by Theorem A*; cross-tabulate with the census outcome."""
import sys, gzip, json, collections
sys.path.insert(0, 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex')
from pattern import pattern
recs = [json.loads(l) for l in gzip.open('artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt')]
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
N = 9
def lvl(i): return (int(i) + 1).bit_length() - 1
def kind(key):
    P = [tuple(int(x) for x in k) for k in pattern(key, N)]
    up = collections.Counter(); down = collections.Counter(); within = 0; bad = 0
    for k in P:
        ls = [lvl(x) for x in k]
        if len(set(ls)) == 1: within += 1; continue
        lo = min(ls); top = [x for x in k if lvl(x) == lo]; kids = [x for x in k if lvl(x) != lo]
        if len(top) == 1 and len(kids) == 2:
            up[top[0]] += 1
            for c in kids: down[c] += 1
        else: bad += 1
    allx = range((1 << (N + 1)) - 1)
    tree = (within == 0 and bad == 0 and all(up[x] == 1 for x in allx if lvl(x) < N) and all(down[x] == 1 for x in allx if lvl(x) >= 1))
    if tree: return 'tree-isomorphic'
    if within == 0 and bad == 0: return 'joining 1-over-2 only, not a tree'
    if within == 0: return 'joining only, some 2-over-1'
    return 'with within-level knots'
tab = collections.defaultdict(collections.Counter)
for a in recs:
    if 'key' not in a: continue
    tab[outcome(a)][kind(a['key'])] += 1
for o, c in sorted(tab.items()): print(o, dict(c))

# by weight (W_R draws with index < 2000)
wt = collections.defaultdict(collections.Counter)
for a in recs:
    if 'key' not in a: continue
    w = sum(1 for m in a['memberships'] if m['family'] == 'W_R' and m['index'] < 2000)
    if w: wt[outcome(a)][kind(a['key'])] += w
print('--- by weight')
for o, c in sorted(wt.items()): print(o, dict(c))
