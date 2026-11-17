"""MODE-BOND-A1 completion (the thread's own code): the decorated test on the two ca1efb37ad88 controls, whose full closure passed its
cap of 500,000 pairs. Here the closure stops at the first gadget at a level-3 type (an existence check). Writes controls_first.json."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from decorated import Decorated, gadgets  # noqa: E402

third = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/third_class.json'))['third']
out = {}
for idx in ['ca1efb37ad88-361', 'ca1efb37ad88-835']:
    t = time.time()
    D = Decorated(third[idx]['key'])
    try:
        g, sizes, _ = gadgets(D, first_only=True, max_pairs=3000000)
        out[idx] = dict(gadget_found=bool(g), example=repr(g[0][:4]) if g else None, seconds=round(time.time() - t, 1))
    except RuntimeError as e:
        out[idx] = dict(gadget_found=None, error=str(e), seconds=round(time.time() - t, 1))
    print(idx, out[idx], flush=True)
    json.dump(out, open(HERE / 'controls_first.json', 'w'), indent=1)
