"""Pilot: on NAE-GROWTH's part-B stages, does the minimal-NAE core equal the junctions where no junction is redundant?"""
import json, sys
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
R = load_results(str(ROOT / 'runs/nae-growth'))
tab = Counter(); ex = []
k = 0
for c, r in sorted(R.items()):
    if not c.startswith('B-'):
        continue
    for a in r['result']['arrangements']:
        for s in a['stages']:
            stars = s['stars']
            n = s['bits']
            st = B.states(n, stars, 'nae')
            core = S.nae_core(n, st, kmax=max(len(x) for x in stars) + 1)
            js = sorted(tuple(sorted(x)) for x in stars)
            same = sorted(set(js)) == sorted(core)
            red = s['nae']['redundant'] > 0
            mult = S.multiplicity(n, core)
            tab[('redundant' if red else 'irredundant', 'core = junctions' if same else 'core differs', 'max mult ' + str(max(mult) if mult else 0))] += 1
            if not same and not red and len(ex) < 5:
                ex.append((a['key'], s['round'], js, core))
            k += 1
    if k > 1500:
        break
print(k, dict(sorted(tab.items())))
for e in ex: print(e)
