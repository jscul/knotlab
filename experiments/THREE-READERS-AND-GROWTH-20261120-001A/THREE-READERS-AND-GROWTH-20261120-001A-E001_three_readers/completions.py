"""Integer counts of common outside completions for two assignments on marked distinctions."""
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
import os
import sys

for name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS"):
    os.environ[name]="1"
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OUT=ROOT/"artifacts"/HERE.parent.name/HERE.name
PRIOR=ROOT/"experiments/READS-HOLDERS-SOURCES-20261120-001A/READS-HOLDERS-SOURCES-20261120-001A-E001_reads_changes"
sys.path.append(str(PRIOR))
from holdings import echelon
from operations import mask
from exact_counts import Parity


def valid(x,stars,law):
    return all((x & h).bit_count()%2==0 for h in stars) if law=="parity" else all((x & h) not in (0,h) for h in stars)


def literal(stars,marks,law):
    n=max(map(max,stars))+1
    if n>18:
        raise ValueError("literal enumeration exceeds its named finite control")
    hs=list(map(mask,stars)); hidden=sorted(set(range(n))-set(marks))
    f=np.zeros((1<<len(hidden),1<<len(marks)),dtype=np.int64)
    for x in range(1<<n):
        if valid(x,hs,law):
            a=sum(((x>>b)&1)<<i for i,b in enumerate(marks))
            h=sum(((x>>b)&1)<<i for i,b in enumerate(hidden))
            f[h,a]=1
    return f


def intersect(factors):
    scope=tuple(sorted({h for sc,f in factors for h in sc}))
    val=np.ones((3,)*len(scope),dtype=object)
    for sc,f in factors:
        val*=np.asarray(f,dtype=object).reshape(tuple(3 if h in sc else 1 for h in scope))
    return scope,val


def nea_contraction(stars,marks):
    """Expand a holder as one minus its all-zero and all-one completions.

    Keep the ternary choice for each named holder incident on a mark. Eliminate other
    holders first so every off-diagonal entry uses the same counted exterior.
    """
    pos={b:i for i,b in enumerate(marks)}
    owners=defaultdict(list)
    for h,star in enumerate(stars):
        for b in star:
            if b not in pos:owners[b].append(h)
    loose=Counter(); meetings=Counter()
    for hs in owners.values():
        if len(hs)==1:loose[hs[0]]+=1
        else:
            assert len(hs)==2
            meetings[tuple(hs)]+=1
    live={h for hs in owners.values() for h in hs}
    marked={h:mask(pos[b] for b in s if b in pos) for h,s in enumerate(stars)}
    pure=[marked[h] for h in range(len(stars)) if h not in live]
    border={h:marked[h] for h in sorted(live) if marked[h]}
    factors=[((h,),np.array([1<<loose[h],-1,-1],dtype=object)) for h in sorted(live)]
    for hs,n in meetings.items():
        factors.append((hs,np.array([[1<<n,1,1],[1,1,0],[1,0,1]],dtype=object)))
    rest=live-set(border)
    while rest:
        covered={h:set() for h in rest}
        for sc,f in factors:
            for h in set(sc)&rest:
                covered[h].update(sc)
        h=min(rest,key=lambda x:(len(covered[x]),x))
        take=[f for f in factors if h in f[0]]
        factors=[f for f in factors if h not in f[0]]
        sc,val=intersect(take)
        axis=sc.index(h)
        factors.append((tuple(x for x in sc if x!=h),val.sum(axis=axis)))
        rest.remove(h)
    sc,weights=intersect(factors); states=1<<len(marks)
    total=np.zeros((states,states),dtype=object)
    for assignment in product(range(3),repeat=len(sc)):
        v=int(weights[assignment])
        if not v:continue
        # Each active holder forbids an extreme in at least one of the two marked words.
        checks=[(border[h],s-1) for h,s in zip(sc,assignment) if s]
        for x in range(states):
            if any((x & q) in (0,q) for q in pure):continue
            for y in range(x,states):
                if any((y & q) in (0,q) for q in pure):continue
                if all((x & q)==q*b or (y & q)==q*b for q,b in checks):
                    total[x,y]+=v
    for x in range(states):
        for y in range(x):
            total[x,y]=total[y,x]
    assert all(v>=0 for v in total.flat)
    return total


def gram(stars,marks,law):
    if law=="nae":return nea_contraction(stars,marks)
    assert law=="parity"
    q=Parity(stars); restrictions=q.projected_rows(marks);n=len(marks)
    embeds=[mask(b for i,b in enumerate(marks) if x>>i&1) for x in range(1<<n)]
    seen=[all(not ((z&x).bit_count()&1) for z in restrictions) for x in embeds]
    allowed_diffs=[all(not ((z&x).bit_count()&1) for z in q.rows) for x in embeds]
    size=q.total//sum(seen)
    return np.array([[size*int(seen[x] and allowed_diffs[x^y]) for y in range(1<<n)] for x in range(1<<n)],dtype=object)
