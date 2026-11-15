"""Classify short trees on six inputs for a pinned total and a pinned sketch."""
from collections import Counter
from functools import cache
from itertools import combinations
import json


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length()-1
        mask ^= bit


def insert(rows, value):
    while value:
        n = value.bit_length()-1
        if rows[n]:
            value ^= rows[n]
        else:
            rows[n] = value
            return True
    return False


def n_rank(rows):
    basis = [0]*6
    return sum(insert(basis,row) for row in rows)


def scalar(i,j):
    return (i & j).bit_count() % 2


def partner(i):
    return ((i & 0b010101) << 1) | ((i & 0b101010) >> 1)


pairs = list(combinations(range(6),2))
full = (1<<64)-1
q_polar = sum(1<<z for z,(i,j) in enumerate(pairs) if j==i+1 and i%2==0)
linear_one = [sum(1<<x for x in range(64) if scalar(x,l)) for l in range(64)]
monomials = [linear_one[1<<i] & linear_one[1<<j] for i,j in pairs]


@cache
def hull(points):
    if not points:
        return 0
    init=(points & -points).bit_length()-1
    basis=[0]*6
    for p in bits(points):
        insert(basis,p^init)
    vals=[init]
    for v in basis:
        if v:
            vals += [x^v for x in vals]
    return sum(1<<x for x in vals)


def saturate(w, left, right):
    while w:
        after=hull(w & left) & hull(w & right)
        if after==w:
            break
        w=after
    return w


def solve_tiny(w,left,right):
    w=saturate(w,left,right)
    if not w:
        return 1,0
    for linear,yes in enumerate(linear_one[1:],1):
        h0,h1=w & (full ^ yes), w & yes
        if not h0 or not h1:
            continue
        if not saturate(h0,left,right) and not saturate(h1,left,right):
            return 2,linear
    return 3,None


def form(mask):
    rows=[0]*6
    table=0
    for k in bits(mask):
        i,j=pairs[k]
        rows[i] |= 1<<j
        rows[j] |= 1<<i
        table ^= monomials[k]
    return table,rows


def xor_all(values):
    z=0
    for v in values:
        z ^= v
    return z


def transvections():
    # A complete orbit is unnecessary: any exact partition into verified
    # linear equivalences suffices, including using a subset of generators.
    maps=[]
    units=[1<<i for i in range(6)]
    for k in [1,2,4,8,16,32,5,20,17]:
        tr=[u ^ (k if scalar(u,partner(k)) else 0) for u in units]
        if n_rank(tr) != 6:
            raise ValueError("the proposed variable change is singular")
        images=[]
        for a,b in pairs:
            cols=[(scalar(1<<a,z),scalar(1<<b,z)) for z in tr]
            image=sum((cols[i][0]*cols[j][1] ^ cols[i][1]*cols[j][0])<<p
                      for p,(i,j) in enumerate(pairs))
            images.append(image)
        if xor_all(images[i] for i in bits(q_polar)) != q_polar:
            raise ValueError("the generator does not preserve the total polar form")
        maps.append(images)
    return maps


def orbits():
    gens=transvections()
    # Reuse low/high lookup tables for each linear map on the 15 coefficients.
    transforms=[]
    for g in gens:
        ls=[xor_all(g[i] for i in bits(x)) for x in range(256)]
        hs=[xor_all(g[i+8] for i in bits(x)) for x in range(128)]
        transforms.append((ls,hs))
    seen=set()
    for seed in range(1<<15):
        if seed in seen:
            continue
        todo=[seed]
        seen.add(seed)
        size=0
        while todo:
            cur=todo.pop()
            size+=1
            for lo,hi in transforms:
                nxt=lo[cur&255]^hi[cur>>8]
                if nxt not in seen:
                    todo.append(nxt)
                    seen.add(nxt)
        yield seed,size


def audit():
    qt,_=form(q_polar)
    counts=Counter()
    failures=[]
    shapes=[]
    for seed,mul in orbits():
        ft,rows=form(seed)
        _,sumrows=form(seed^q_polar)
        if n_rank(sumrows)!=6:
            continue
        for aff in linear_one:
            g=ft^aff
            for f in [g,full^g]:
                if f.bit_count()>=32:
                    continue
                for q in [qt,full^qt]:
                    left=(full^q)&(full^f)
                    right=q
                    k,query=solve_tiny(full,left,right)
                    counts[(n_rank(rows)//2,k)] += mul
                    if k<3 and len(failures)<12:
                        failures.append((seed,mul,aff,f,q,k,query))
        shapes.append((seed,mul))
    return {"census":{str(k):v for k,v in counts.items()},
            "failures":failures,"orbits":shapes}


if __name__=="__main__":
    print(json.dumps(audit()))
