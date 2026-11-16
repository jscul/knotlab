"""Theorem M over the small-orbit census (MARK-RATE-20261116-001, the thread's own code, 2026-11-16): the no-skip check for every alive
description with orbits of at most four addresses and r0 = 0 (marks.py), with its BLOCK-REACH profile, forgetting length and cycle
flag. The pilot sample (exploratory/pilot.json) is marked so the predictions can exclude it. Run only after predictions.md is
committed. Each description has 120 s; one over the limit, or whose families exceed the cap, is recorded as undecided. Writes
census_marks.json."""
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
from marks import check  # noqa: E402

LIMIT = 120          # seconds per description; a description over the limit is recorded as undecided (no_skip None)


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout('over %d s' % LIMIT)


signal.signal(signal.SIGALRM, _alarm)
rows = json.load(open(ROOT / 'research/BLOCK-REACH-20261116-001/census_forget.json'))['rows']
pilot = set(json.load(open(HERE / 'exploratory/pilot.json'))['sample'])
out = {}
for line in gzip.open(ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt'):
    rec = json.loads(line)
    row = rows.get(rec['case'])
    if row is None or row['r0'] != 0:
        continue
    signal.alarm(LIMIT)
    t0 = time.time()
    try:
        res = check(rec['key'])
    except (Timeout, RuntimeError) as e:
        res = dict(no_skip=None, witness=None, error=type(e).__name__ + ': ' + str(e)[:80])
    signal.alarm(0)
    print(rec['case'][:12], row['name'], row['r'], res['no_skip'], round(time.time() - t0, 1), flush=True)
    out[rec['case']] = dict(name=row['name'], cyclic=row['cyclic'], r=row['r'], profile=row['profile'], pilot=rec['case'] in pilot,
                            no_skip=res['no_skip'], witness=res['witness'], error=res.get('error'),
                            seconds=round(time.time() - t0, 2))
tally = collections.Counter((r['name'], r['cyclic'] if r['name'] == 'ruler' else None, r['r'], r['no_skip'], r['pilot'])
                            for r in out.values())
json.dump(dict(rows=out, tally={str(k): v for k, v in sorted(tally.items(), key=str)}), open(HERE / 'census_marks.json', 'w'), indent=1)
for k, v in sorted(tally.items(), key=str):
    print(k, v)
