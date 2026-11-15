"""Checks for proof.md (RULER-LEVEL-20261114-001A): (1) Theorem A's structure on 2,000 random one-placement tree-type descriptions at
N = 8 (a full binary tree across levels); (2) the ruler L(s) = s + 2 by the reach census's exact search on 20 of them (N = 5, top
level 1, s = 1..3); (3) the census coverage (census_forest.py's table) is recomputed by that script, not here. Writes result.json."""
import sys, os, random, json, shutil, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
from pattern import pattern
import job
HERE = os.path.dirname(os.path.abspath(__file__))
def lvl(i): return (int(i) + 1).bit_length() - 1
def is_full_tree(P, N):
    up = collections.Counter(); down = collections.Counter()
    for k in P:
        ls = [lvl(x) for x in k]
        if len(set(ls)) != 2: return False
        lo = min(ls); top = [x for x in k if lvl(x) == lo]; kids = [x for x in k if lvl(x) != lo]
        if len(top) != 1 or len(kids) != 2: return False
        up[top[0]] += 1
        for c in kids: down[c] += 1
    NV = (1 << (N + 1)) - 1
    return all(up[x] == 1 for x in range(NV) if lvl(x) < N) and all(down[x] == 1 for x in range(NV) if lvl(x) >= 1)
rng = random.Random(20261115); bad = 0; keys = []
for _ in range(2000):
    s = rng.choice([1, 2, 3, 4, 5]); W = 1 + s + s * s
    key = [s, [rng.randrange(2) for _ in range(s)], [rng.randrange(s) for _ in range(s)], [rng.randrange(s) for _ in range(s)],
           [sorted([3 * rng.randrange(W), 3 * rng.randrange(W) + 1, 3 * rng.randrange(W) + 2])]]
    P = [tuple(int(x) for x in k) for k in pattern(key, 8)]
    if not is_full_tree(P, 8): bad += 1
    keys.append(key)
rulers = []
wd = os.path.join(HERE, 'work'); job.BUDGET = 120
for key in keys[:20]:
    shutil.rmtree(wd, ignore_errors=True); os.makedirs(wd)
    r = job.compute(key, wd, N=5, k0=1, S=3, histograms=False)
    rulers.append([l['L_N'] for l in r['levels']])
shutil.rmtree(wd, ignore_errors=True)
ok = bad == 0 and all(L == [3, 4, 5] for L in rulers)
json.dump(dict(status='passed' if ok else 'failed', theorem_A_structure=dict(tested=2000, not_full_tree=bad), ruler_profiles=rulers), open(os.path.join(HERE, 'result.json'), 'w'), indent=1)
print('passed' if ok else 'failed', bad, collections.Counter(map(tuple, rulers)))
