import sys, json, time
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import scale as SC, repro as RP
S, rings, loose = RP.rings_start(link='double')
st = S
for t in range(0, 5):
    if t: st, status, b = RP.forbid.grown(st, 'parity', 'ordinary')
    if t in (1, 4):
        for k in (5, 12):
            t0 = time.time(); res, nloc = SC.held_by_no_part(st, loose, k)
            print('round', t, 'scale', k, res, 'single-knot facts', nloc, round(time.time() - t0, 1), 's', flush=True)
