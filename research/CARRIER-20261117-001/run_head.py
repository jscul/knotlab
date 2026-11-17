"""Every-depth top-chain bonds from level 3 (CARRIER-20261117-001, the thread's own code): head_bond.every_depth_head for one pattern
of KEEP-REACH's 25 open ones, head depth d, bonds searched up to cap members, without the lower orbit's children. Writes
head/<index>_d<d>.json. Usage: run_head.py <index> <d> [cap]."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from head_bond import WindowTree, every_depth_head  # noqa: E402

index, d = sys.argv[1], int(sys.argv[2])
cap = int(sys.argv[3]) if len(sys.argv) > 3 else 8
third = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/third_class.json'))['third']
t = time.time()
e = every_depth_head(WindowTree(third[index]['key']), 3, d, children=False, cap=cap)
seqs = e['sequences']
every_s = all(x is not None for seq in seqs.values() for x in seq)
out = dict(index=index, key=third[index]['key'], kind=third[index]['kind'], d=d, cap=cap, head_every_s=every_s,
           head_max=max(x for seq in seqs.values() for x in seq) if every_s else None, seconds=round(time.time() - t, 1),
           **{k: v for k, v in e.items() if k not in ('d', 'children')})
(HERE / 'head').mkdir(exist_ok=True)
json.dump(out, open(HERE / 'head' / ('%s_d%d.json' % (index, d)), 'w'), indent=1)
print(index, 'd', d, every_s, out['head_max'], {k: v[:12] for k, v in seqs.items()}, out['seconds'], flush=True)
