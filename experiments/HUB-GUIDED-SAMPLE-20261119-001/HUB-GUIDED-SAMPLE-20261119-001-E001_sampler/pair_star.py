"""Exact maximal groups when the many-block junctions all meet and the rest have two blocks."""
from collections import Counter
from functools import lru_cache
import argparse
import json
from pathlib import Path
from group_profile import Stage,pack,members


def intersection_count(patterns, high):
    states={high}
    for p in sorted(patterns,key=lambda r:(r.bit_count(),r)):
        states.update([old & p for old in states])
    return len(states)


def solve(path):
    context=Stage(path)
    H=[u for u,s in enumerate(context.at) if len(s)>2]
    high=(1<<len(H))-1
    assert len(H) and all(len(s)>=2 for s in context.at)
    highs=pack(H,context.n)
    assert all(context.hood(context.at[u]) & highs == highs for u in H)
    k=len(context.blocks)
    hb=[0]*k
    for j,u in enumerate(H):
        for b in context.at[u]:
            hb[b]|=1<<j
    ng=[set() for _ in range(k)]
    a={}
    for u,s in enumerate(context.at):
        if len(s)==2:
            b,c=s
            assert (b,c) not in a and b<c
            ng[b].add(c)
            ng[c].add(b)
            a[b,c]=hb[b]|hb[c]
    def support(b,c):
        return a[min(b,c),max(b,c)]
    patterns=[Counter(support(b,c) for c in ng[b]) for b in range(k)]
    memo={}
    for b,counts in enumerate(patterns):
        vals=tuple(sorted(counts))
        if vals in memo:
            continue
        memo[vals]=intersection_count(vals,high)
    local_counts=[memo[tuple(sorted(counts))] for counts in patterns]
    @lru_cache(maxsize=None)
    def through(b,T):
        # All that matters here is whether one or two junctions are the entire star.
        total=0
        for p,count in patterns[b].items():
            if p & T == T:
                total+=count
                if total>2:return 3
        return total
    local_empty=sum(through(b,high)==0 for b in range(k))
    global_empty=not any(v==high for v in a.values())
    singleton_deduction=sum(through(b,T)==1 or through(c,T)==1 for (b,c),T in a.items())
    corners=0
    triangles=0
    for b in range(k):
        for c in ng[b]:
            if c<=b:continue
            for d in ng[b]&ng[c]:
                if d<=c:continue
                triangles+=1
                e,f,g=support(b,c),support(b,d),support(c,d)
                for vertex,p,q,other in ((b,e,f,g),(c,e,g,f),(d,f,g,e)):
                    common=p&q
                    corners+=other & common==common and through(vertex,common)==2
    total=sum(local_counts)-local_empty+int(global_empty)-singleton_deduction-corners+triangles
    return dict(live=context.n,high_junctions=len(H),pair_junctions=len(a),blocks=k,
                candidate_pairs=meta_candidate(context),sum_local_maxima=sum(local_counts),
                local_zero=local_empty,global_zero=int(global_empty),singleton_deduction=singleton_deduction,
                extendible_two_member_corners=corners,three_distinct_pairs=triangles,maximal_groups=total,
                local_maxima_hist=dict(sorted(Counter(local_counts).items())),
                checked_all_high_pairs=True)


def meta_candidate(stage):
    return sum(stage.hood(sig).bit_count()-1 for sig in stage.at)//2


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('roster',type=Path)
    ap.add_argument('result',type=Path)
    q=ap.parse_args()
    v=solve(q.roster)
    q.result.write_text(json.dumps(v,indent=1)+'\n')
    print(v['maximal_groups'],v['three_distinct_pairs'],flush=True)
