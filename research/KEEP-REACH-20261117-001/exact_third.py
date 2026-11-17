"""Exact reach of the genuine third class (KEEP-REACH-20261117-001, the thread's own wrapper, 2026-11-17): never forget even on the
values states take, and no two-orbit bond at some s. For representatives (8db5da810c00-73, bace53f8f952-58, bace53f8f952-111), the
least bond from level 3 to level 3 + s, by the census's exact search (LEVEL-REACH job.compute, which certifies optimality). One process
per key: `exact_third.py <index> [N S budget]` (defaults N = 11, s = 1..6, 300 s per s; `census:<case prefix>` for a census key);
writes exact_third_<index>_N<N>.json (the first three runs wrote exact_third_<index>.json at N = 11)."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
import job  # noqa: E402

index = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 11
S = int(sys.argv[3]) if len(sys.argv) > 3 else 6
job.BUDGET = int(sys.argv[4]) if len(sys.argv) > 4 else 300
if index.startswith('census:'):
    import gzip
    key = next(json.loads(l)['key'] for l in gzip.open(ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt')
               if json.loads(l)['case'].startswith(index[7:]))
else:
    rows = [json.loads(l) for l in open(HERE / 'mutants_keep.jsonl')]
    key = next(r['key'] for r in rows if str(r['index']) == index)
wd = tempfile.mkdtemp()
try:
    res = job.compute(key, wd, N=N, k0=3, S=S, histograms=False)
finally:
    shutil.rmtree(wd, ignore_errors=True)
out = dict(index=index, key=key, N=N, k0=3, budget=job.BUDGET,
           levels=[dict(s=lv['s'], L_N=lv['L_N'], bond=lv.get('bond') or (lv.get('anywhere') or {}).get('bond'),
                        optimality_proved=lv.get('optimality_proved', (lv.get('anywhere') or {}).get('optimality_proved')),
                        certificate=(lv.get('anywhere') or {}).get('certificate')) for lv in res['levels']])
# (fixed after the referee, 2026-11-17: the first runs read the row's own fields, which are null; the certificate is in row['anywhere'])
json.dump(out, open(HERE / ('exact_third_%s_N%d.json' % (index.replace(':', '_'), N)), 'w'), indent=1)
print(index, [lv['L_N'] for lv in res['levels']])
