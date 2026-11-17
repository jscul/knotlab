"""Every-depth orbit-and-block bonds from level 3 (CARRIER-20261117-001, the thread's own code): for the 25 open patterns of KEEP-REACH
and the four census parents, every_depth_block with bonds searched up to cap members. Writes block_25.json."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from two_block import WindowTree, every_depth_block  # noqa: E402

cap = int(sys.argv[1]) if len(sys.argv) > 1 else 8
third = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/third_class.json'))['third']

ids = [i for i, r in third.items() if not r['kind'].startswith('forget')]
jobs = [(i, third[i]['key'], third[i]['kind']) for i in ids]
out = {}
for idx, key, kind in jobs:
    t = time.time()
    e = every_depth_block(WindowTree(key), 3, cap=cap)
    seqs = e['sequences']
    every_s = all(x is not None for seq in seqs.values() for x in seq)
    out[idx] = dict(key=key, kind=kind, cap=cap, block_every_s=every_s,
                    block_max=max((x for seq in seqs.values() for x in seq if x is not None), default=None) if every_s else None,
                    seconds=round(time.time() - t, 1), **e)
    print(idx, kind[:24], every_s, out[idx]['block_max'], {k: v[:10] for k, v in seqs.items()}, out[idx]['seconds'], flush=True)
    json.dump(out, open(HERE / 'block_25.json', 'w'), indent=1)
