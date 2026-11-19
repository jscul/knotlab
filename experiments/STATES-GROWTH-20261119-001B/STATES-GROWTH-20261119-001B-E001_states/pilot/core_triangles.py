import itertools, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import statelib as S
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae'))
from longrun import load_results
import bondlib as B
def has_triangle(stars):
    sets = [set(x) for x in stars]
    for a, b, c in itertools.combinations(range(len(sets)), 3):
        if sets[a] & sets[b] and sets[b] & sets[c] and sets[a] & sets[c]:
            return True
    return False
def has_double(stars):
    sets = [set(x) for x in stars]
    return any(len(sets[a] & sets[b]) >= 2 for a, b in itertools.combinations(range(len(sets)), 2))
R = load_results(str(ROOT / 'runs/nae-growth'))
tab = Counter(); k = 0
for c, r in sorted(R.items()):
    if not c.startswith('B-'): continue
    for a in r['result']['arrangements']:
        for s in a['stages']:
            stars = s['stars']; n = s['bits']
            if s['nae']['redundant'] > 0: continue
            st = B.states(n, stars, 'nae')
            core = S.nae_core(n, st, kmax=max(len(x) for x in stars) + 1)
            same = sorted(set(tuple(sorted(x)) for x in stars)) == sorted(core)
            tab[('core = junctions' if same else 'core differs', 'triangle' if has_triangle(stars) else 'no triangle', 'double' if has_double(stars) else '-')] += 1
            k += 1
    if k > 1500: break
print(k, dict(sorted(tab.items())))
