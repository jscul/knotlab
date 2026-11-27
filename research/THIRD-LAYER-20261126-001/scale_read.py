"""scale_read.py OUT.jsonl: the read of README.md "Frozen": on the 16 three-ring built families at round 4 (where at
most 300 distinctions), at the scale k one below the families' least flipping change, which families' facts are class
facts held by no part (scale.held_by_no_part)."""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import twokinds as TK, scale as SC, minflip as MF, repro as RP
import families as FA
with open(sys.argv[1], 'w') as f:
    for label, kw in FA.members():
        if kw['R'] != 3: continue
        S, rings, loose = RP.rings_start(**kw); fams, ls = TK.families(S); st = S
        for t in range(1, 5):
            st, status, b = RP.forbid.grown(st, 'parity', 'ordinary')
        nd = len({x for r in st for x in r})
        if nd > 300: f.write(json.dumps({'family': label, 'end': 'not read: %d distinctions' % nd}) + '\n'); continue
        flips = [MF.least(st, l, kmax=40) for l in ls]; k = min(x for x in flips if isinstance(x, int)) - 1
        res, nloc = SC.held_by_no_part(st, ls, k)
        rec = {'family': label, 'round': 4, 'families': len(ls), 'least flips': flips, 'scale': k, 'single-knot facts at k': nloc, 'facts': res}
        f.write(json.dumps(rec) + '\n'); f.flush(); print(json.dumps(rec)[:300], flush=True)
