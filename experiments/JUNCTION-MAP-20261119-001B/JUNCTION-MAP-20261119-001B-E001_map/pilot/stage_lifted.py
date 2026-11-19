import sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import maplib as M
sys.path.insert(0, str(M.ROOT / 'scripts'))
from longrun import load_results
R = load_results(str(M.ROOT / 'runs/break-eddies'))
tab = Counter()
for c, r in sorted(R.items()):
    if r.get('status') != 'ok': continue
    x = r['result']; rec = x['recurrence']
    if not rec or tuple(rec.get('W', ())) != (0, 0, 1, 1): continue
    sz, e = x['start']['sizes'], [tuple(v) for v in x['start']['edges']]
    cnt = x['counts']
    for s in (1, 2):
        p = M.lifted_series(sz, e, s, 8)
        if isinstance(p, list):
            tail = cnt[s + 1: s + 9]
            fd = next((k for k in range(len(tail)) if p[k] != tail[k]), None)
            tab[(s, 'equal' if fd is None else f'differs at +{fd + 1}')] += 1
        else:
            tab[(s, str(p))] += 1
print(dict(sorted(tab.items())))
