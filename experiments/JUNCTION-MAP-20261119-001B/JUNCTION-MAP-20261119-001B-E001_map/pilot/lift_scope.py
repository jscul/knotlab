"""Pilot: the cluster rule with its scope cut lifted (a group of three sharing two knots with another block kept as two blocks,
which then form a loop of length two), against the grown counts of BREAK-EDDIES' rational starts."""
import inspect, json, sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/CLUSTER-ALL-20261119-001B/CLUSTER-ALL-20261119-001B-E001_census'))
import clusters as Cl
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results
ns = dict(Cl.__dict__)
src = inspect.getsource(Cl.analyse)
cut = "            return {'scope': False, 'why': 'a round-1 group of three sharing two knots with another block'}\n"
assert src.count(cut) == 1
exec(compile(src.replace(cut, "            pass\n"), Cl.__file__, 'exec'), ns)
for name in ('_series', 'series'):
    exec(compile(inspect.getsource(getattr(Cl, name)), Cl.__file__, 'exec'), ns)
series = ns['series']
R = load_results(str(ROOT / 'runs/break-eddies'))
tab = Counter()
ex = []
for c, r in sorted(R.items()):
    if r.get('status') != 'ok':
        continue
    x = r['result']
    rec = x['recurrence']
    if not rec or 'W' not in rec:
        continue
    W = tuple(rec['W'])
    sz, e = x['start']['sizes'], [tuple(v) for v in x['start']['edges']]
    cnt = x['counts']
    try:
        p = series(sz, e, min(len(cnt), 30))
    except Exception as err:
        p = f'error {type(err).__name__}'
    if isinstance(p, list):
        fd = next((t for t in range(len(p)) if p[t] != cnt[t]), None)
        v = 'equal' if fd is None else f'differs at {fd}'
    else:
        v = str(p)
    key = 'y2(1+y)' if W == (0, 0, 1, 1) else 'other'
    tab[(key, v if v in ('equal',) else ('differs' if v.startswith('differs') else v))] += 1
    if len(ex) < 6 and key == 'y2(1+y)':
        ex.append((c, v, cnt[:10], p[:10] if isinstance(p, list) else p))
print(dict(tab))
for e in ex: print(e)
