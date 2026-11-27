"""rest/nae_rest.py LO HI OUT.jsonl: the rest of part (d) under not-all-equal (census starts LO to HI - 1), with
nae_pres.presentations unchanged; run in parallel ranges after the frozen run stopped at its time limit."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nae_pres as NP
lo, hi, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
cen = NP.forbid.census()
with open(out, 'w') as f:
    for i in range(lo, min(hi, len(cen))):
        S = NP.forbid.supports_of(cen[i]); pres, capped = NP.presentations(S, 'nae')
        trees = {NP.PR.tree_of(P) for P in pres}
        rec = {'start': 'census %d' % i, 'presentations': len(pres), 'capped': capped, 'family partitions': len({t[0] for t in trees}),
               'trees': len(trees), 'own tree among them': NP.PR.tree_of(S) in trees}
        if len(pres) > 1: rec['presentations found'] = [list(map(list, P)) for P in pres[:3]]
        f.write(json.dumps(rec) + '\n'); f.flush()
