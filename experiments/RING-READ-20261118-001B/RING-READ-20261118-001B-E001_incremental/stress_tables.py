"""Stress test one size past (after the frozen runs, not pre-registered): do the tables with sides of up to 6 and 7 junctions
still agree at round 25, where the first ten-distinction junction appears?  Run: .venv/bin/python -B stress_tables.py 25"""
import json
import sys
import time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reader3 as R3  # noqa: E402
R = R3.R
T = int(sys.argv[1])
P = R.grow(T)
st = R.stars_of(P)
K = max(map(len, st))
out = {'T': T, 'junctions': len(st), 'largest_junction': K}
tabs = {}
for m in (6, 7):
    t = time.time()
    tabs[m], _ = R.bond_table(st, m, K)
    out[f'm{m}_seconds'] = round(time.time() - t, 1)
out['entries'] = len(tabs[6])
out['entries_differing_m6_m7'] = sum(1 for p in tabs[6] if tabs[6][p] != tabs[7][p])
dest = HERE.parents[2] / f'artifacts/RING-READ-20261118-001B/RING-READ-20261118-001B-E001_incremental/stress_tables_{T}.json'
dest.write_text(json.dumps(out, indent=1))
print(json.dumps(out))
