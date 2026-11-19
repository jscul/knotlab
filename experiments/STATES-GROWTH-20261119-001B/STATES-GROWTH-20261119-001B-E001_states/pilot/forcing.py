import itertools, sys
from collections import Counter, defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import statelib as S
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae'))
from longrun import load_results
import bondlib as B
def forcing(stars):
    own = defaultdict(list)
    for j, s in enumerate(stars):
        for b in s: own[b].append(j)
    loose = {j: any(len(own[b]) == 1 for b in s) for j, s in enumerate(stars)}
    out = []
    for j, s in enumerate(stars):
        if len(s) != 3: continue
        nbrs = []
        ok = True
        for b in s:
            o = [k for k in own[b] if k != j]
            if not o: ok = False; break
            k = o[0]
            if len(stars[k]) != 3 or loose[k]: ok = False; break
            nbrs.append(k)
        if ok: out.append(j)
    return out
R = load_results(str(ROOT / 'runs/nae-growth'))
tab = Counter(); k = 0; ex = []
for c, r in sorted(R.items()):
    if not c.startswith('B-'): continue
    for a in r['result']['arrangements']:
        for s in a['stages']:
            stars = s['stars']; n = s['bits']
            if s['nae']['redundant'] > 0: continue
            st = B.states(n, stars, 'nae')
            core = S.nae_core(n, st, kmax=max(len(x) for x in stars) + 1)
            same = sorted(set(tuple(sorted(x)) for x in stars)) == sorted(core)
            f = forcing(stars)
            tab[('saturated' if same else 'not', 'forcing' if f else 'no forcing')] += 1
            if (not same) and not f and len(ex) < 4: ex.append((stars, [x for x in core if x not in set(tuple(sorted(y)) for y in stars)]))
            k += 1
    if k > 1500: break
print(k, dict(sorted(tab.items())))
for e in ex: print(e)
