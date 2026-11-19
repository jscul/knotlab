"""Validation of exact_table.py against the RING-READ referee's finding: at ring round 25 the side-6 table and the exact table
differ in exactly six entries, all at D = 10.  Run: .venv/bin/python -B validate_exact.py 25"""
import json
import sys
import time
from collections import Counter
from pathlib import Path
sys.setrecursionlimit(100000)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job  # noqa: E402
import exact_table as X  # noqa: E402
R = job.R
T = int(sys.argv[1])
P = R.grow(T)
st = R.stars_of(P)
K = max(map(len, st))
t = time.time()
ex = X.exact_table(st, K)
te = time.time() - t
s6, _ = R.bond_table(st, 6, K)
diff = Counter(ex[p] for p in ex if s6[p] != ex[p])
out = {'T': T, 'largest': K, 'exact_seconds': round(te, 1), 'differing_entries_by_exact_D': dict(diff),
       'matches_referee': T != 25 or diff == Counter({10: 6})}
dest = HERE.parents[2] / 'artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census'
dest.mkdir(parents=True, exist_ok=True)
(dest / f'validate_exact_{T}.json').write_text(json.dumps(out, indent=1))
print(json.dumps(out))
