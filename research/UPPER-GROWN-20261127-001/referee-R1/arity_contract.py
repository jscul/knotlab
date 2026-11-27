"""Ten-knot mixed not-all-equal patterns obtained by two disjoint contractions."""

import argparse
import itertools
import json
from pathlib import Path
import time

from arity_search import HERE, ORIGINAL, PREVIOUS, engine, supports


def canonical(n, links):
    adj=[[0]*n for _ in range(n)]
    for a,b in links:
        adj[a][b]+=1
        adj[b][a]+=1
    def walk(parts):
        cells=[]
        for group in parts:
            buckets={}
            for p in group:
                key=tuple(tuple(sorted(adj[p][q] for q in cell)) for cell in parts)
                buckets.setdefault(key,[]).append(p)
            cells.extend(v for _,v in sorted(buckets.items()))
        if len(cells)>len(parts):
            return walk(cells)
        ambiguous=[i for i,part in enumerate(cells) if len(part)>1]
        if not ambiguous:
            order=[part[0] for part in cells]
            return bytes(adj[p][q] for i,p in enumerate(order) for q in order[i+1:])
        i=min(ambiguous,key=lambda j:len(cells[j]))
        return min(walk(cells[:i]+[[p],[q for q in cells[i] if q!=p]]+cells[i+1:])
                   for p in cells[i])
    return walk([list(range(n))])


def all_raw(patterns):
    for case,links in enumerate(patterns):
        for i,j in itertools.combinations(range(len(links)),2):
            p,q=links[i]
            r,s=links[j]
            if len({p,q,r,s})!=4: continue
            names=[k for k in range(12) if k not in (q,s)]
            rename={k:names.index(p if k==q else r if k==s else k) for k in range(12)}
            result=[tuple(sorted((rename[a],rename[b]))) for k,(a,b) in enumerate(links) if k not in (i,j)]
            yield case, [i,j], result


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--binary',type=Path, required=True)
    p.add_argument('--sources',choices=['all','earlier'],required=True)
    p.add_argument('--limit',type=int)
    p.add_argument('--only-simple',action='store_true')
    p.add_argument('--inventory',action='store_true')
    a=p.parse_args()
    if a.sources=='earlier':
        original=json.loads((PREVIOUS/'layer_witness.json').read_text())['source_knots_not_all_equal']
        bases=[[[i for i,row in enumerate(original) if x in row] for x in range(18)]]
    else:
        bases=[json.loads(line)['links'] for f in sorted((ORIGINAL/'out').glob('cubic_12_*.jsonl'))
               for line in f.read_text().splitlines()]
    known=set()
    counts={'source_patterns':len(bases),'contractions':0,'distinct':0,'distinct_simple':0}
    for i, contracted, links in itertools.islice(all_raw(bases),a.limit):
        counts['contractions']+=1
        simple=len(set(links))==len(links)
        if a.only_simple and not simple: continue
        key=canonical(10,links)
        if key in known: continue
        known.add(key)
        counts['distinct']+=1
        counts['distinct_simple']+=int(simple)
        if a.inventory: continue
        start=time.perf_counter()
        result=engine(a.binary.resolve(),supports(10,links))
        print(json.dumps({'source_index':i,'contracted_distinctions':contracted,
                          'links':links,'seconds':round(time.perf_counter()-start,4),**result}),flush=True)
    print(json.dumps(counts),flush=True)


if __name__=='__main__':
    main()
