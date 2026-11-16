"""Gate for Lemma U (BLOCK-REACH-20261116-001, the thread's own code, 2026-11-16): for small-orbit census descriptions, the projection of
the whole pattern onto the members of the census's depth-9 least bond (s = 1..4) is the same at depth 9 and at depths 10 and 11 (SAT,
every assignment of the members), so the bond stays a bond. 40 descriptions drawn with a fixed seed."""
import gzip
import itertools
import json
import random
import sys
from pathlib import Path

from pysat.solvers import Cadical195

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
from pattern import pattern, clauses  # noqa: E402

rows = json.load(open(HERE / 'census_forget.json'))['rows']
recs = {}
for line in gzip.open(ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt'):
    r = json.loads(line)
    if r['case'] in rows and rows[r['case']]['upper_every_depth']:
        recs[r['case']] = r
rng = random.Random(20261116)
sample = rng.sample(sorted(recs), 40)


def projection(K, members):
    out = set()
    with Cadical195(bootstrap_with=clauses(K)) as s:
        for bits in itertools.product((0, 1), repeat=len(members)):
            if s.solve(assumptions=[m + 1 if b else -(m + 1) for m, b in zip(members, bits)]):
                out.add(bits)
    return frozenset(out)


checked = differ = 0
for cid in sample:
    key = recs[cid]['key']
    Ks = {N: pattern(key, N) for N in (9, 10, 11)}
    for lv in recs[cid]['levels']:
        if str(lv['s']) not in rows[cid]['upper_every_depth'] and lv['s'] not in rows[cid]['upper_every_depth']:
            continue
        members = [int(v) for v in lv['bond']]
        P = {N: projection(K, members) for N, K in Ks.items()}
        checked += 1
        if not (P[9] == P[10] == P[11]):
            differ += 1
            print('DIFFER', cid[:12], lv['s'], [len(p) for p in P.values()])
res = dict(descriptions=len(sample), bonds_checked=checked, projections_differing=differ, passed=differ == 0)
json.dump(res, open(HERE / 'gate_upper.json', 'w'), indent=1)
print(res)
