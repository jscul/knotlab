"""Theorem K and Conjecture C on the census (KEEP-REACH-20261117-001): classify every alive small-orbit description of the
LEVEL-REACH census (classify.py), 120 s each. Run only after predictions.md is committed. Writes census_keep.json."""
import collections
import gzip
import json
import signal
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from classify import classify  # noqa: E402


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


signal.signal(signal.SIGALRM, _alarm)
names = {cid: r['name'] for cid, r in json.load(open(ROOT / 'research/BLOCK-REACH-20261116-001/census_forget.json'))['rows'].items()}
out = {}
for line in gzip.open(ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt'):
    rec = json.loads(line)
    if rec['case'] not in names:
        continue
    t0 = time.time()
    signal.alarm(120)
    try:
        c = classify(rec['key'])
    except Timeout:
        c = dict(small_orbits=True, timeout=True)
    signal.alarm(0)
    c.update(name=names[rec['case']], profile=[x['L_N'] for x in rec['levels']], seconds=round(time.time() - t0, 2))
    out[rec['case']] = c
    print(rec['case'][:12], c.get('name'), c.get('r_all'), c.get('two_orbit_every_s'), c.get('two_orbit_tail_max'), c['seconds'], flush=True)
tally = collections.Counter((c['name'], c.get('r_all') is None, c.get('two_orbit_every_s'), c.get('timeout', False)) for c in out.values())
json.dump(dict(rows=out, tally={str(k): v for k, v in sorted(tally.items(), key=str)}), open(HERE / 'census_keep.json', 'w'), indent=1)
for k, v in sorted(tally.items(), key=str):
    print(k, v)
