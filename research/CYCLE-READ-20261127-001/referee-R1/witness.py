"""Nine-knot realisation of four overlapping groups; exercise the complete growth and both readings."""
from collections import Counter
import json
from pathlib import Path
import sys
import time

from core import build_core, read_map
from reader import predict_core
from replay import oldest_twin, score

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'LOOK-ALIKE-20261126-001'))
from alike import grow


def nine_knots(ends):
    # Six live knots in an alternating cycle witness the inner pairs of 012 and
    # 345. Three spent knots witness the remaining pairs 13, 23, 24.
    stars = [[] for _ in range(9)]
    label = 0
    pairs = [(0,3),(3,1),(1,4),(4,2),(2,5),(5,0),
             (1,6),(3,6),(2,7),(3,7),(2,8),(4,8),(6,7),(7,8)]
    for a,b in pairs:
        stars[a].append(label)
        stars[b].append(label)
        label += 1
    for i,n in enumerate([1+int(0 in ends),2,3,3,2,1+int(5 in ends)]):
        for _ in range(n):
            stars[i].append(label)
            label += 1
    return stars


def match(ends, save):
    start = time.perf_counter()
    s = nine_knots(ends)
    mapped, = read_map(s).pieces
    core = build_core(s)
    p, = core.pieces
    # Direct pair-of-births test, including first-round births.
    marked = []
    pairs = Counter()
    for rank, layer in p.ranks.items():
        for j, a in enumerate(layer):
            for b in layer[:j]:
                shared = sorted(set(p.nodes[a].parents) & set(p.nodes[b].parents))
                if len(shared)<2:
                    continue
                pairs[rank-1] += 1
                for i,c in enumerate(shared):
                    for d in shared[:i]:
                        for g in set(p.nodes[c].parents) & set(p.nodes[d].parents):
                            if p.nodes[g].points & p.chains.keys():
                                marked.append((rank-1,a,b,c,d,g))
    out=dict(chain_ends=sorted(ends), stars=s, places=list(map(len,s)), groups=mapped.groups,
             knots=len(s), map_class='cycle' if p.cycle else 'tree', stop=p.stop, chain_bases=p.chains,
             births_by_round=[len(layer) for rank,layer in p.ranks.items() if rank>1], unqualified_twins=pairs,
             chained_twins=marked)
    for law in ('nae','parity'):
        g=grow(s,rounds=24,knot_law=law)
        rows,why=predict_core(core,24,law)
        first=score(g,rows)
        diffs={}
        for key in ('n','sig0','sig1'):
            delta=next((i for i,(actual,want) in enumerate(zip(g['rows'],rows),1) if actual[key]!=want[key]),None)
            diffs[key]=delta
        t=first-1 if isinstance(first,int) else 0
        def cnt(row):
            return Counter({json.dumps(k):n for k,n in row['sig0']})
        out[law]=dict(first=diffs, end=g['end'], read=why, rounds=len(g['rows']),
                      grown=[r['n'] for r in g['rows']], predicted=[r['n'] for r in rows],
                      excess=dict(cnt(g['rows'][t])-cnt(rows[t])),missing=dict(cnt(rows[t])-cnt(g['rows'][t])))
        if save and len(ends)==2:
            (HERE / ('witness_'+law+'.jsonl')).write_text(json.dumps(dict(g,stars=s,name='nine-knot two-chain witness'))+'\n')
    out['seconds']=round(time.perf_counter()-start,4)
    return out

if __name__=='__main__':
    for ends in ([{0,5}] if sys.argv[1]=='pilot' else [set(),{0},{5},{0,5}]):
        print(json.dumps(match(ends,sys.argv[1]!='pilot')),flush=True)
