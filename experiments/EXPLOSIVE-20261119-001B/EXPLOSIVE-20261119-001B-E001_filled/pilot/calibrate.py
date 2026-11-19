"""Calibration (disclosed, before the freeze): the frozen class rule on BREAK-EDDIES's reference shapes, to 12,000 junctions."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import job  # noqa: E402

P = json.loads((job.ROOT / 'experiments/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/population_ref.json').read_text())
out = []
t = time.time()
for x in P:
    r = job.read(x['sizes'], [tuple(y) for y in x['edges']], x['shape'], 12000)
    out.append({k: r[k] for k in ('tag', 'sizes', 'tri', 'b1', 'b2', 'overlap_point', 'overlap_block', 'reading', 'measured', 'counts', 'groups')})
    print(x['shape'], x['sizes'], r['tri'], r['b1'], r['b2'], r['overlap_point'], r['overlap_block'], r['reading'], r['measured'],
          r['counts'][-6:], r['groups'][-6:], '%.0fs' % (time.time() - t), flush=True)
(HERE / 'calibration.json').write_text(json.dumps(out, indent=1) + '\n')
