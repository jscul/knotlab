"""Part B1 (TWO-ENDS-20261117-001, the thread's own code): the saturated composite automaton (composite.py) on KEEP-REACH's 25 open
patterns, the four census parents, and every small-orbit census description that forgets (census_keep.json, r_stable not None).
Writes composite.json: per pattern the automaton's size, threshold, period, the product length l0 (None: some periodic composite is
not a product), and for the census the forgetting length r (BLOCK-REACH's) for P5 (l0 <= r + 1)."""
import gzip
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from composite import WindowTree, automaton  # noqa: E402

third = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/third_class.json'))['third']
census = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/census_keep.json'))['rows']
keys = {}
for line in gzip.open(ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt'):
    r = json.loads(line)
    if 'key' in r and r.get('case') in census:
        keys[r['case']] = r['key']
jobs = [(i, r['key'], r['kind'], None) for i, r in third.items() if not r['kind'].startswith('forget')]
for cid, row in census.items():
    if row.get('small_orbits') and row.get('alive_every_depth') and cid in keys:
        jobs.append(('census:' + cid[:12], keys[cid], 'census ' + row.get('name', ''), row.get('r_stable')))
out = {}
t0 = time.time()
for idx, key, kind, r in jobs:
    a = automaton(WindowTree(key))
    a.pop('nonproduct_examples')
    out[idx] = dict(kind=kind, r_forget=r, **a)
json.dump(out, open(HERE / 'composite.json', 'w'), indent=1)
open25 = [i for i in out if not i.startswith('census')]
cen = [v for i, v in out.items() if i.startswith('census')]
forget = [v for v in cen if v['r_forget'] is not None]
print('open 25: l0 None in', sum(out[i]['l0'] is None for i in open25), 'of', len(open25), '; max states', max(out[i]['states'] for i in open25))
print('census alive small-orbit', len(cen), 'forgetting', len(forget))
print('forgetting with l0 None', sum(v['l0'] is None for v in forget), '; l0 > r + 1', sum(v['l0'] is not None and v['l0'] > v['r_forget'] + 1 for v in forget))
print('never-forgetting census with l0', sum(v['l0'] is not None for v in cen if v['r_forget'] is None), 'of', sum(v['r_forget'] is None for v in cen))
print('max states', max(v['states'] for v in out.values()), 'seconds', round(time.time() - t0, 1))
