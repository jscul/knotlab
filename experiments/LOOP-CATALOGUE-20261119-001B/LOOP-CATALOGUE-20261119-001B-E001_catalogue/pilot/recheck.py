import json, sys, glob
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import eddy as E, sampler as S
tab = Counter(); bad = []
for f in sorted(glob.glob(str(HERE / 'random_*_*000000.json'))):
    n = int(f.split('_')[-2])
    for r in json.load(open(f)):
        if not r.get('growth'):
            continue
        sz, e = S.sample(n, r['seed'])
        v = E.eddy(sz, e)
        g = r['growth']
        ge = g.startswith('exp')
        tab[(str(v), 'exp' if ge else g)] += 1
        if (v is True) != ge and v != 'out':
            bad.append((n, r['seed'], v, g, r['counts'][:12]))
print(dict(tab))
for b in bad: print(b)
