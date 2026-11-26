"""repro_cuts.py OUT.jsonl: the binding referee's cut construction rebuilt (the 30-knot start with the three middle
knots of the detours joined pairwise and holding one loose distinction each), grown under the ordinary count and both
forbidding cuts; carriers are each ring's ten original loose distinctions.  BUILT-BINDING-20261126-001; README.md."""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import repro as RP
S, rings, loose = RP.rings_start(link_middles=True)
with open(sys.argv[1], 'w') as f:
    for arm in ('ordinary', 'one_fewer', 'arity_floor'):
        rec = {'arm': arm, 'knots': len(S), 'rounds': [dict(RP.analyse(S, S, loose), round=0)]}
        st = S
        for t in range(1, 4):
            nxt, status, births = RP.forbid.grown(st, 'parity', arm)
            if status != 'funded': rec['rounds'].append({'round': t, 'end': status}); break
            st = nxt; r = RP.analyse(S, st, loose); r['round'] = t
            r['births with no fresh distinction'] = [[b['parents'], b['p']] for b in births if b['f'] == 0]
            rec['rounds'].append(r)
        f.write(json.dumps(rec) + '\n'); print(json.dumps(rec)[:2500], flush=True)
