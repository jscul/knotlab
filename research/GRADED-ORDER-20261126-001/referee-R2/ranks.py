"""Check both ends and support identity when comparing graded sets with the finite core."""
import argparse
from collections import Counter
import json
import sys
from reading import HERE, core

sys.path.insert(0,str(HERE.parent))
import order


def audit(stars):
    # Parity suppresses the relay in a single finite piece. Discard relay births
    # in every piece explicitly; this audit concerns only births from groups.
    m = order.late.Map(stars)
    pieces = [order.late.GeneralPiece(pts,m.adj,m.chains,lambda v:v<m.n,None,lambda k:1,m.cells)
              for pts,_,_ in m.pieces]
    top = max(w for p in pieces for w in p.sizes_of.values())
    bs = core(stars, 'nae', top+1)
    # The two implementations use the same order for the surplus slots, but our
    # birth identities occupy some intervening integers. Recover the bijection.
    base_ids = {}
    for k in m.live:
        ours = sorted(i for i,b in bs.items() if b.grade==1 and b.parents==(k,))
        theirs = sorted(v for v in m.adj[k] if v>=m.n)
        assert len(ours)==len(theirs)
        base_ids.update(zip(ours,theirs))
    def support(b):
        return tuple(sorted(base_ids.get(v,v) for v in b.support))
    valid, got = Counter(),Counter()
    for p in pieces:
        for s,z in p.sizes_of.items():
            valid[z-1,tuple(sorted(s)),tuple(sorted(tuple(sorted(t)) for t in p.core_parents[s]))]+=1
    for i,b in bs.items():
        if b.grade>1 and len(b.parents)==1:
            continue
        got[b.grade,support(b),tuple(sorted(support(bs[j]) for j in b.parents))]+=1
    errors = (valid-got) + (got-valid)
    return min((k[0] for k in errors),default=None)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--limit',type=int,default=1000)
    args=p.parse_args()
    for name in ('fresh7_treeplus','fresh7_grow','held_treeplus','held_grow','held8_treeplus','referee-R1/small_nae','referee-R1/obstruction_nae'):
        counts=Counter()
        with (HERE.parent/(name+'.jsonl')).open() as f:
            for i,r in enumerate(map(json.loads,f)):
                if i>=args.limit:break
                if 'stars' not in r:
                    continue
                new=audit(r['stars'])
                old=order.check_start(r['stars'],'nae')
                interior=min((t for t,ok in old if not ok),default=None)
                counts[(new,interior)]+=1
        print(name,dict(counts))
