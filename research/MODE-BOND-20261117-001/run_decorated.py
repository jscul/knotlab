"""Part A (MODE-BOND-20261117-001, the thread's own code): the decorated test on the 5 distinct patterns among the 13 mutants of
8db5da810c00 and the 5 bounded controls of CARRIER. Writes decorated.json: per pattern the families' sizes, the periodic non-product
composites, the conditions, the closure sizes and the gadgets at level-3 types (with one witness each)."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from decorated import Decorated, gadgets, level_types  # noqa: E402

PATTERNS = ['8db5da810c00-73', '8db5da810c00-76', '8db5da810c00-81', '8db5da810c00-89', '8db5da810c00-100']
CONTROLS = ['bace53f8f952-58', 'bace53f8f952-111', 'bace53f8f952-147', 'ca1efb37ad88-361', 'ca1efb37ad88-835']
third = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/third_class.json'))['third']
out = {}
for idx in PATTERNS + CONTROLS:
    t = time.time()
    D = Decorated(third[idx]['key'])
    nonprod, start, period = D.periodic_nonproducts()
    g, sizes, _ = gadgets(D)
    out[idx] = dict(role='control' if idx in CONTROLS else 'pattern', r0=D.r0, f_all=D.f_all, level3_types=level_types(D.tree, 3),
                    fam=[len(f) for f in D.fam], famp=[len(f) for f in D.famp],
                    nonproducts=[(a, b, len(T)) for a, b, T in nonprod], threshold=start, period=period,
                    conditions={str(k): len(v) for k, v in D.conditions().items()},
                    closure={str(k): {str(t): n for t, n in v.items()} for k, v in sizes.items()},
                    gadgets=len(g), gadget_examples=[dict(start=a, top_type=b, M1=m1, M2=m2, witness=repr(w)[:400]) for a, b, m1, m2, w in g[:3]],
                    seconds=round(time.time() - t, 1))
    print(idx, out[idx]['role'], 'gadgets', len(g), 'famp', out[idx]['famp'], 'closure', out[idx]['closure'], out[idx]['seconds'], flush=True)
    json.dump(out, open(HERE / 'decorated.json', 'w'), indent=1)
