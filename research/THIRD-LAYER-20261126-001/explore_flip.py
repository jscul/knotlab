import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research' / 'BUILT-BINDING-20261126-001')); sys.path.insert(0, str(HERE))
import repro as RP, minflip as MF
S, rings, loose = RP.rings_start(link='double')     # split attachments, double links (21 knots)
conn = list(range(15, len(S)))
st = S
for t in range(0, 5):
    if t: st, status, b = RP.forbid.grown(st, 'parity', 'ordinary')
    z = [MF.least(st, g) for g in loose]
    e = []
    for L in conn:
        h = RP.forbid.holders(st); att = [x for x in S[L] if any(k < 15 for k in h[x] if k != L)]
        e.append(MF.least(st, att))
    print('round', t, 'distinctions', len({x for r in st for x in r}), 'ring facts', z, 'attachment parities', e, flush=True)
