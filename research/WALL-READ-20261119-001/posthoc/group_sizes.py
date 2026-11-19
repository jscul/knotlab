"""Post hoc (after the frozen run, disclosed): what the unread starts' last listed rounds are made of. For each start, the sizes of
the groups of the last round the roster engine listed (pairs against larger groups), to see whether the jump comes from pairs
inside large blocks (the burst kind) or from large cliques (the partnered kind).

Run on start-03 (round 8), start-06 and start-07 (round 7); output in group_sizes.jsonl. The runs on start-09 (round 6) and start-01
(round 10) were stopped after about ten minutes and give nothing."""
import json
import resource
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'proofs/WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered'))
import rosterlib as RL  # noqa: E402
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402

resource.setrlimit(resource.RLIMIT_AS, (8 << 30, 8 << 30))
name, T = sys.argv[1], int(sys.argv[2])
st = load_results(str(ROOT / 'runs/merge-burst'))[name]['result']['start']
opn, blocks = RL.roster_of(st['sizes'], [tuple(x) for x in st['edges']])
out = {}


def on_stage(t, pts, B, par):
    if t == T:
        sz = Counter(len(par[j]) for j in pts)
        out.update({'start': name, 'round': T, 'junctions': len(pts), 'offshoots': sz.get(1, 0), 'pairs': sz.get(2, 0),
                    'three_or_more': sum(c for s, c in sz.items() if s >= 3), 'largest': max(sz)})
        raise StopIteration


try:
    for r in RL.grow(opn, blocks, T, on_stage=on_stage):
        pass
except (StopIteration, RuntimeError):
    pass
print(json.dumps(out))
