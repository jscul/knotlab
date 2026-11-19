"""Post hoc (after the frozen run, disclosed): B2's double count for start-03, rounds 7 and 8.

The frozen job writes a round's parent sum only after the next round's groups are listed, and start-03's round 9 ran out of memory,
so round 8's parent sum was never written. Here the roster engine (frozen rosterlib.py) rebuilds round 8 and sums its parents
directly, without listing round 9."""
import json
import resource
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'proofs/WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered'))
import rosterlib as RL  # noqa: E402
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402

resource.setrlimit(resource.RLIMIT_AS, (8 << 30, 8 << 30))
st = load_results(str(ROOT / 'runs/merge-burst'))['start-03']['result']['start']
opn, blocks = RL.roster_of(st['sizes'], [tuple(x) for x in st['edges']])
out = {}


def on_stage(t, pts, B, par):
    if t == 8:
        out['round8_parent_sum'] = sum(len(par[j]) for j in pts)
        out['round8_junctions'] = len(pts)
        raise StopIteration


try:
    for r in RL.grow(opn, blocks, 8, on_stage=on_stage):
        if 'open_sum' in r and r['t'] == 7:
            out['round7_open_sum'] = r['open_sum']
except (StopIteration, RuntimeError):
    pass
out['equal'] = out.get('round7_open_sum') == out.get('round8_parent_sum')
print(json.dumps(out))
Path(__file__).with_suffix('.json').write_text(json.dumps(out, indent=1) + '\n')
