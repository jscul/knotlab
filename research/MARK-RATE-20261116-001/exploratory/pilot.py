"""Pilot (MARK-RATE-20261116-001, the thread's own, 2026-11-16, before predictions): Theorem M's check on a held-out sample drawn with
seed 1116: 8 cyclic rulers, 4 acyclic rulers with r = 1 (positive control: their reach is s + 2 at every depth by the hypertree
theorem) and 4 half-rate descriptions (negative control: their least bonds skip levels). The sample is excluded from the frozen
predictions."""
import gzip
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
from marks import check  # noqa: E402

rows = json.load(open(ROOT / 'research/BLOCK-REACH-20261116-001/census_forget.json'))['rows']
keys = {}
for line in gzip.open(ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt'):
    r = json.loads(line)
    if r['case'] in rows:
        keys[r['case']] = r['key']
rng = random.Random(1116)
cyc = sorted(c for c, r in rows.items() if r['name'] == 'ruler' and r['cyclic'])
acy = sorted(c for c, r in rows.items() if r['name'] == 'ruler' and not r['cyclic'] and r['r'] == 1)
half = sorted(c for c, r in rows.items() if r['name'] == 'half-rate')
sample = [('cyclic', c) for c in rng.sample(cyc, 8)] + [('acyclic', c) for c in rng.sample(acy, 4)] + [('half', c) for c in rng.sample(half, 4)]
out = []
for kind, cid in sample:
    t = time.time()
    res = check(keys[cid])
    res.update(kind=kind, case=cid, r=rows[cid]['r'], seconds=round(time.time() - t, 2))
    out.append(res)
    print(kind, cid[:12], 'r', rows[cid]['r'], 'no_skip', res['no_skip'], 'D', res['D_sizes'][:4], 'U', res['U_sizes'][:4], res['seconds'], flush=True)
json.dump(dict(sample=[c for _, c in sample], results=out), open(HERE / 'pilot.json', 'w'), indent=1)
