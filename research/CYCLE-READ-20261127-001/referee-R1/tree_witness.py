"""Use the second ordinary stage of the nine-knot witness as a fresh tree-class start."""
import json
import time
from collections import Counter
from pathlib import Path
from core import build_core
from reader import predict_core
from witness import nine_knots
from alike import eng, grow

out = Path(__file__).resolve().parent
s = eng.from_stars(nine_knots({0,5}))
for _ in range(2):
    eng.play_round(s, eng.Law('ORD','CANCEL-WAIT',None,'nae'), eng.Guard(100))
stars=s.places
c=build_core(stars, max_rank=100)
p, = c.pieces
result=dict(knots=len(stars), stars=stars, cycle=p.cycle, chains=sum(p.chains.values()),
            finished=p.finished, core_births=p.birth_count, twin=p.twin_rank,
            counts=[len(p.ranks[k]) for k in sorted(p.ranks) if k>1])
for law in ('nae','parity'):
    t=time.perf_counter()
    pred,status=predict_core(c,24,law)
    g=grow(stars,rounds=24,knot_law=law)
    first={k:next((i for i,(a,b) in enumerate(zip(g['rows'],pred),1) if a[k]!=b[k]),None)
           for k in ('n','sig0','sig1')}
    i=first['sig0']-1
    def sig(row):
        return Counter({json.dumps(k):n for k,n in row['sig0']})
    a,b=sig(g['rows'][i]),sig(pred[i])
    result[law]=dict(first=first, read=status, end=g['end'], extra=dict(a-b), missing=dict(b-a),
                     grown=[row['n'] for row in g['rows']], predicted=[row['n'] for row in pred],
                     seconds=round(time.perf_counter()-t,4))
    (out/f'tree_witness_{law}.jsonl').write_text(json.dumps(dict(g,stars=stars,name='twice-grown nine-knot witness'))+'\n')
print(json.dumps(result))
