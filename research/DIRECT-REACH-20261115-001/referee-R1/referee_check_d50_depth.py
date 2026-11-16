"""Referee R1, item (d) follow-up: d50c90fa37ed... ties from level 3 to each deeper level at depths 9..12 (my oracle), with two
spot pairs re-decided by a second solver (Glucose 4) on my own clauses. Writes referee_d50_depth.json."""
import json
import sys
import time

import numpy as np
from pysat.solvers import Glucose4

sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/research/DIRECT-REACH-20261115-001/referee-R1')
from referee_pattern import Oracle, hid, load_population  # noqa: E402

pop = {d['case'][:12]: d for d in load_population()}
key = pop['d50c90fa37ed']['key']
out = {}
for N in (9, 10, 11, 12):
    t = time.time()
    O = Oracle(key, N, seed=5)
    X = O.samples(128)
    others = np.array([v for v in range(O.nv) if (v + 1).bit_length() - 1 > 3])
    by_level = {}
    for u in range(8):
        for v, sg in O.tie_partners(hid(u, 3), others, X).items():
            lv = (v + 1).bit_length() - 1
            by_level[lv] = by_level.get(lv, 0) + 1
    # second solver: is level-3 address 0 tied to level-8 address 0, and to level-(N-1) address 0?
    g = Glucose4()
    for a, b, c in O.K.tolist():
        g.add_clause([a + 1, b + 1, c + 1])
        g.add_clause([-a - 1, -b - 1, -c - 1])
    spot = {}
    for lv in sorted({8, N - 1}):
        x, y = hid(0, 3) + 1, hid(0, lv) + 1
        spot['level3[0]~level%d[0]' % lv] = dict(both_parities=[g.solve(assumptions=[-x, -y]), g.solve(assumptions=[-x, y])])
    g.delete()
    O.close()
    out[N] = dict(tied_pairs_from_level3_by_level={str(k): v for k, v in sorted(by_level.items())},
                  level_sizes={str(l): 1 << l for l in range(4, N + 1)}, glucose_spot=spot, seconds=time.time() - t)
    print(N, out[N], flush=True)
json.dump(out, open('/home/jscul/p-vs-np-contact-first/research/DIRECT-REACH-20261115-001/referee-R1/referee_d50_depth.json', 'w'), indent=1)
