"""Check the submitted entry point, full finite core, law change and omission controls."""
from collections import Counter
from pathlib import Path
import json
import sys
from time import perf_counter
from overlaps import case
from draw import realize
from reading import HERE, alike, core, map_data, predict, observed
from trace import twins

sys.path.insert(0, str(HERE.parent))
import order


def control(name, stars, horizon):
    for law in ('nae','parity'):
        start = perf_counter()
        pred, why = order.predict_nodes(stars, horizon, law, groups=True)
        ours = predict(stars, law, horizon)
        g = alike.grow(stars, horizon, knot_law=law)
        independent = None if pred is None else list(map(observed, pred)) == ours
        our_core = core(stars, law, horizon+1)
        print(json.dumps(dict(name=name, law=law, status=why, first=order.score.compare(pred,g) if pred else None,
                              independent_equal=independent, observed=g['end'], counts=[r['n'] for r in g['rows']],
                              core_per_round=sorted(Counter(b.grade for b in (our_core or {}).values()).items()),
                              twins=sorted(set(w['grade'] for w in twins(our_core or {}))),
                              seconds=round(perf_counter()-start,4))),flush=True)


if __name__ == '__main__':
    n = int(sys.argv[1])
    s, f, o = case(2)
    control('two shared-knot groups with one chain', s, 9)
    if n>1:
        v = o.copy()
        v[2] -= 1
        control('same five live knots with the spare on knot 2 removed', realize(5,f,v), 9)
        control('one finite piece', [[0,1,2,3,4,5],[0,1,2]], 8)
        control('four initial offshoots', [[0,1,2],[0,3,4]], 5)
        control('two finite pieces', [[0,1,2,3],[0,4,5,6]], 6)
        control('five cyclically paired knots', [[(i-1)%5,i,5+2*i,6+2*i] for i in range(5)], 4)
