"""Enumerate previously spent holders and the finite source choices for a cover."""
from collections import Counter
from itertools import combinations
from math import ceil
import networkx as nx
from select_target import OUT
from census_stages import End, end_of, step


def forced_old_cover(n,options,indices,previous,summary,forced_triples):
    now=tuple(frozenset(options[j]['support']) for j in indices)
    first=tuple(map(frozenset,previous))
    occupied=now+first
    residual=tuple(summary['residual'])
    names=tuple(i for i,d in enumerate(residual) if d)
    active=summary['previous_groups']
    allowed_pairs={frozenset(p) for source in active for p in combinations(source,2)}
    big={frozenset(source) for source in active if len(source)>=3}
    obligations=set(map(frozenset,summary['previous_witness_obligations']))
    possible=[]
    for size in range(3,len(names)+1):
        for row in combinations(names,size):
            H=frozenset(row)
            if any(t<H for t in forced_triples) or size==3 and H not in forced_triples:continue
            if any(u<=H or H<=u for u in occupied):continue
            touched=frozenset(j for j,K in enumerate(first) if K&H)
            if any(frozenset(p) not in allowed_pairs for p in combinations(touched,2)):continue
            if any(s<=touched for s in big):continue
            possible.append((H,touched))
    byname={i:{j for j,(H,_) in enumerate(possible) if i in H} for i in names}
    def visit(need,permitted,chosen,unmet):
        if not any(need):
            if not unmet:
                yield tuple(tuple(sorted(possible[j][0])) for j in chosen)
            return
        active_names={x for x,d in enumerate(need) if d}
        viable=tuple(j for j in permitted if possible[j][0]<=active_names)
        opts=set(viable)
        x=min(active_names,key=lambda z:(len(byname[z]&opts)-need[z],z))
        partners=sorted(byname[x]&opts)
        if len(partners)<need[x]:return
        # Choosing all remaining incident holders of one named pivot
        # avoids duplicates without making an order restriction on others.
        for local in combinations(partners,need[x]):
            if any(possible[i][0]<=possible[j][0] or possible[j][0]<=possible[i][0] for i,j in combinations(local,2)):continue
            counts=list(need)
            for j in local:
                for z in possible[j][0]:counts[z]-=1
            if min(counts)<0:continue
            removed=opts-byname[x]
            remaining={i for i in removed if all(not (possible[i][0]<=possible[j][0] or possible[j][0]<=possible[i][0]) for j in local)}
            covered={e for e in unmet if any(e<=possible[j][1] for j in local)}
            yield from visit(tuple(counts),remaining,chosen+local,unmet-covered)
    yield from visit(residual,set(range(len(possible))),(),obligations)


def reverse_once(rows):
    """Recover the sole possible preceding rows and validate this actual cut."""
    degree=Counter(x for H in rows for x in H)
    born=tuple(H for H in rows if any(degree[x]==1 for x in H))
    older=tuple(H for H in rows if H not in born)
    if not born or not older:return None
    own={}
    for i,H in enumerate(older):
        for x in H:own.setdefault(x,[]).append(i)
    if any(not any(x in own for x in H) for H in born):return None
    seen=Counter()
    actual=Counter()
    for H in born:
        ids=[]
        for x in H:
            if x in own:
                if len(own[x])!=1:return None
                ids.append(own[x][0]);seen[x]+=1
        if len(set(ids))!=len(ids):return None
        actual[tuple(sorted(ids)),sum(x not in own for x in H)]+=1
    if set(seen)!={x for x,r in own.items() if len(r)==1}:return None
    earlier,_=end_of(older)
    forecast=step(earlier,'nae')
    if forecast.status!='extend' or Counter(zip(forecast.parents,forecast.fresh))!=actual:return None
    return older


def histories(rows):
    cuts=[tuple(tuple(sorted(row)) for row in rows)]
    while (earlier:=reverse_once(cuts[-1])) is not None:
        cuts.append(earlier)
    # Every truncation still needs its proposed initial full-projection and
    # essentiality check before it counts as an actually lawful history.
    return tuple(tuple(reversed(cuts[:depth+1])) for depth in range(1,len(cuts)))
