"""check3.py: the advisor's third check (README.md, part A). On the ten sampled closers whose knots all commute under
rule R (EVENTUAL-R-20261126-001, part B: census starts 33, 2502, 3030, 4911, 6171, 6313, 6391, 6407, 6483, 6585), for
each knot, the distinctions whose values fail to commute with its law: is that set an allowed change (every knot holds
an even number of its distinctions), as the advisor's general form says?"""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'EVENTUAL-R-20261126-001')); sys.path.insert(0, str(HERE.parent / 'FORBID-EDITS-20261126-001'))
import ops, forbid, part_b            # noqa: E402

STARTS = (33, 2502, 3030, 4911, 6171, 6313, 6391, 6407, 6483, 6585)
if __name__ == '__main__':
    S = forbid.census(); total = {'knots': 0, 'lists that are allowed changes': 0, 'empty lists': 0}
    for i in STARTS:
        stages, births, end = part_b.grow(forbid.supports_of(S[i]), 4)
        F = [list(k) for k in stages[-1]]; m = 1 + max(d for k in F for d in k)
        vals = ops.realise(m, ops.rule_R(F, m)); K = ops.knot_ops(F, vals)
        assert end == 'closed' and ops.r1(K)
        ok = 0; empty = 0
        for u in range(len(F)):
            N = {d for d in range(m) if not ops.commute(vals[d], K[u])}
            ok += all(len(N & set(k)) % 2 == 0 for k in F); empty += not N
        total['knots'] += len(F); total['lists that are allowed changes'] += ok; total['empty lists'] += empty
        print(json.dumps({'start': i, 'knots': len(F), 'lists that are allowed changes': ok, 'empty lists': empty}))
    print(json.dumps(total))
