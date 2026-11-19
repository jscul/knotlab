import json, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import eddy as E
sys.path.insert(0, str(E.ROOT / 'experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae'))
for v in json.load(open(HERE / 'cat_7.json')):
    sz, e = v['sizes'], [tuple(x) for x in v['edges']]
    t = time.time()
    g = E.J.grow(sz, e, rounds=40, maxj=30000, tmax=120)
    pred = E.Cl.series(sz, e, len(g['counts']))
    print(sz, g['outcome'], g['counts'][:24], pred == g['counts'], round(time.time() - t, 1), flush=True)
