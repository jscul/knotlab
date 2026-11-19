"""Post hoc (after the frozen run was read): the smallest explosive starts found, grown further (to round 40, 2.5 GB, 120 s per
start), with counts and largest groups per round, and the number of loose distinctions after each round."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job  # noqa: E402

job.T = 40
job.CHILD_SECONDS = 120
res = json.loads((HERE.parents[2] / 'artifacts/EXPLOSIVE-20261119-001B/EXPLOSIVE-20261119-001B-E001_filled/results.json').read_text())
out = []
for x in res['smallest_explosive']:
    g = job.grow_isolated(x['sizes'], [tuple(y) for y in x['edges']], 200000)
    out.append({'sizes': x['sizes'], 'edges': x['edges'], 'outcome': g['outcome'], 'counts': g['counts'], 'groups': g['groups']})
    print(x['sizes'], g['outcome'], g['counts'], g['groups'], flush=True)
    (HERE / 'posthoc_smallest.json').write_text(json.dumps(out, indent=1) + '\n')
