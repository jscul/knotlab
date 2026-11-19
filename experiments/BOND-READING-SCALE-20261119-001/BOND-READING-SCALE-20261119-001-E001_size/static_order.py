"""Exact certificates for a split junction in a complete bipartite graph.

The growing end replaces one fixed unit distinction. This experiment concerns
a later reading of arbitrary order, including failures that stay hidden in pairs.
"""
from functools import lru_cache
from itertools import combinations
from math import inf
from pathlib import Path
import json

@lru_cache(None)
def components(weak, capacity, minimum=(1, 1)):
    """Nontrivial weak-only components, sorted; unused weak sites stand alone."""
    families = [()]
    for count in range(minimum[0], min(weak, capacity) + 1):
        start = minimum[1] if count == minimum[0] else 1
        for middle in range(start, capacity - count + 2):
            cost = count + middle - 1
            for rest in components(weak - count, capacity - cost, (count, middle)):
                families.append(((count, middle),) + rest)
    return tuple(families)

@lru_cache(None)
def profiles(order, weak):
    result = set()
    for heavy_weak in range(min(weak, order - 1) + 1):
        for heavy_middle in range(order - heavy_weak + 1):
            if heavy_weak and not heavy_middle:
                continue
            for others in components(weak - heavy_weak, order - heavy_weak - heavy_middle):
                used = sum(a for a, _ in others)
                happy = heavy_middle + sum(b for _, b in others)
                if not happy:
                    continue
                # All weak sites in a component choose one side. The strong site is negative.
                choices = {(0, happy)}
                for a, b in others:
                    choices |= {(pos + a, marked - b) for pos, marked in choices}
                free = weak - heavy_weak - used
                options = sorted({(positive + f, positive_middles)
                                  for positive, positive_middles in choices for f in range(free+1)})
                result.add((happy,tuple(options)))
    return tuple(result)

def required_weight(order, weak, per_hub):
    """Exact strict cheap-bond screen, across all marked subsets up to order."""
    q = 2 * per_hub
    need = 1
    for touched, options in profiles(order, weak):
        if touched > q:
            continue
        best = inf
        for a, n_marked_positive in options:
            m = n_marked_positive
            if a == 0:
                m = 1
                if n_marked_positive > 1:
                    continue
            elif a >= 2:
                m = max(1, m)
            max_m = q - (touched - n_marked_positive)
            if m > max_m or m >= per_hub:
                continue
            # The hub has L copies per spoke. A cut is cheap if
            # (s-m)L > 2a(s-m)+weak*m. The left threshold increases with m.
            min_l = 2 * a + (weak * m) // (per_hub - m) + 1
            best = min(best, min_l)
        if best > weak:
            return None
        need = max(need, best)
    return need

def samples(max_order=12):
    out=[]
    for r in range(2,max_order+1):
        best_j=best_n=None
        covered=0
        for t in range(2,r+3):
            for s in range(2,2*r+6):
                covered+=1
                L=required_weight(r,t,s)
                if L is None:
                    continue
                j=t+2*s+4
                n=2*s*(t+L)+5
                case=dict(order=r,junctions=j,distinctions=n,anchors=t,per_hub=s,spoke_weight=L,
                          exposed_later_order=s)
                if best_j is None or (j,n)<(best_j['junctions'],best_j['distinctions']):
                    best_j=case
                if best_n is None or (n,j)<(best_n['distinctions'],best_n['junctions']):
                    best_n=case
        assert best_j and best_n
        out.append(dict(r=r,panels=covered,least_j_then_n=best_j,least_n_then_j=best_n))
    return out

def brute_control():
    for r,t,s in [(2,2,3),(2,3,4),(3,3,3),(3,3,5),(3,4,4),(4,3,3)]:
        # Direct independent listing on literal support type names.
        q=2*s
        edges=[(a,t+1+b) for a in range(t+1) for b in range(q)]
        tested=[]
        for L in range(1,t+1):
            low=[]
            for mask in range(1,1<<(t+q)):
                k=mask<<1
                a=(k & ((1<<(t+1))-1)).bit_count()
                m=(k>>(t+1)).bit_count()
                if (not a and m!=1) or (not m and a!=1) or (m==q and t+1-a!=1):
                    continue
                selected=sum(1<<e for e,(i,j) in enumerate(edges) if ((k>>i)^(k>>j))&1)
                cost=sum(L if i==0 else 1 for e,(i,j) in enumerate(edges) if selected&(1<<e))
                if cost < s*L:
                    low.append(selected)
            # By monotonicity it is enough to query every r-subset.
            queries=[sum(1<<x for x in xs) for xs in combinations(range(len(edges)),r)]
            ok=all(any(v&x==x for v in low) for x in queries)
            tested.append(ok)
        exact=next((i for i,v in enumerate(tested,1) if v),None)
        assert exact==required_weight(r,t,s),(r,t,s,exact,required_weight(r,t,s))
    return 6

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--through',type=int,default=10)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    result=dict(target="a later reading of arbitrary order",direct_controls=brute_control(),
                rows=samples(args.through))
    args.output.write_text(json.dumps(result,indent=2)+'\n')
