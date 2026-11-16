"""Independent all-affine-question lower for one trained literal on three AND triples."""
from collections import Counter
from functools import cache
import json


def defects(x, rank):
    return sum((((x >> (3*i+2)) ^ ((x >> (3*i)) & (x >> (3*i+1)))) & 1) << i for i in range(rank))


def parity(x): return x.bit_count() & 1


SIZE=64
FULL=(1 << SIZE)-1
RICH=sum(1<<x for x in range(SIZE) if defects(x,2)==0)
PLAIN=sum(1<<x for x in range(SIZE) if parity(defects(x,2)))
QUESTIONS=[sum(1<<x for x in range(SIZE) if parity(x&q)) for q in range(1,SIZE)]


@cache
def hull(mask):
    if not mask:return 0
    origin=(mask&-mask).bit_length()-1
    basis={}
    while mask:
        bit=mask&-mask
        mask^=bit
        v=(bit.bit_length()-1)^origin
        while v:
            j=v.bit_length()-1
            if j not in basis:
                basis[j]=v
                break
            v^=basis[j]
    span=[origin]
    for v in basis.values():span += [x^v for x in span]
    return sum(1<<x for x in span)


def splits(r,p):
    seen=set()
    for q in QUESTIONS:
        left=(r&q,p&q)
        right=(r^left[0],p^left[1])
        if not any(left) or not any(right):continue
        key=min(left,right)
        if key not in seen:
            seen.add(key)
            yield left,right


@cache
def ordinary(r,p):
    """Exact unit total of paid checks and questions on at most six raw bits."""
    if not r or not p:return 1
    plain_after_rich=p&hull(r)
    rich_after_plain=r&hull(p)
    if not plain_after_rich or not rich_after_plain:return 2
    best=1000
    if plain_after_rich!=p:best=min(best,1+ordinary(r,plain_after_rich))
    if rich_after_plain!=r:best=min(best,1+ordinary(rich_after_plain,p))
    for left,right in splits(r,p):
        left_cost=ordinary(*left)
        if 1+left_cost+1<best:
            best=min(best,1+left_cost+ordinary(*right))
    return best


def affine_chart(mask):
    origin=(mask&-mask).bit_length()-1
    rows=[origin]
    for x in range(SIZE):
        if (mask>>x)&1 and x not in rows:rows += [u^origin^x for u in rows]
    assert sum(1<<x for x in rows)==mask
    return rows


def compact_extension(r,d):
    core=affine_chart(hull(r|d))
    assert len(core)<=8
    rich=plain=0
    for coord,z in enumerate(core):
        if not (d>>z)&1:continue
        for t in range(8):
            point=(coord<<3)|t
            error=defects(t,1)
            if ((r>>z)&1) and not error:rich|=1<<point
            if parity(defects(z,2))^error:plain|=1<<point
    return ordinary(rich,plain)


def spectator_bounds(r,d):
    refined=Counter()

    @cache
    def lower(r,d,refine):
        if not r:return 1
        if refine and r.bit_count()==5 and d.bit_count() in (6,8) and hull(r|d).bit_count()==8:
            exact=compact_extension(r,d)
            refined[exact]+=1
            return exact
        best=1+2*max(2,ordinary(r,d&PLAIN))
        after=d&hull(r)
        if after!=d:best=min(best,1+lower(r,after,refine))
        for left,right in splits(r,d):
            left_cost=lower(*left,refine)
            if 1+left_cost+1<best:
                best=min(best,1+left_cost+lower(*right,refine))
        return max(5,best)

    coarse=lower(r,d,False)
    improved=lower(r,d,True)
    return coarse,improved,dict(sorted(refined.items()))


def audit():
    # The original coordinates give three invertible blocks
    # (x1,x0,u), (x2,x1+x3,v), (x4,x3+x5,s+u+v).
    triples=set()
    named_rich=named_plain=0
    for raw in range(512):
        x=[(raw>>i)&1 for i in range(6)]
        s,u,v=[(raw>>i)&1 for i in (6,7,8)]
        word=sum(b<<i for i,b in enumerate((x[1],x[0],u,x[2],x[1]^x[3],v,x[4],x[3]^x[5],s^u^v)))
        triples.add(word)
        terms=[a*b for a,b in zip(x,x[1:])]
        rich=(s==(sum(terms)&1)) and u==terms[0] and v==(terms[1]^terms[2])
        plain=s!=(sum(terms)&1)
        assert (defects(word,3)==0)==rich and bool(parity(defects(word,3)))==plain
        if x[0] and not v:
            named_rich+=rich
            named_plain+=plain
    assert len(triples)==512 and (named_rich,named_plain)==(24,64)

    # In F, w1=1 and p2=0. The original y1 drops out after replacing p1 by g=p1+y1.
    rich=plain=0
    for x in range(64):
        g,a,b,c,d,p=[(x>>i)&1 for i in range(6)]
        if not g and not(a*b) and p==c*d:rich|=1<<x
        if g^(a*b)^p^(c*d):plain|=1<<x
    train=ordinary(rich,plain)
    f=sum(1<<z for z in range(64) if (z&2) and not(z&32))
    coarse,residual,refined=spectator_bounds(RICH&~f,FULL^f)
    assert (train,coarse,residual,refined)==(7,13,15,{7:12})
    return {'status':'passed', 'checked_original_visible_words':512,
            'forbidden_original_rich_plain':[named_rich,named_plain],
            'complement_original_rich_plain':[64-named_rich,256-named_plain],
            'training_exact_cost':train,'complement_coarse_lower':coarse,
            'compact_residual_exact_costs':refined,'complement_weighted_lower':residual,
            'lower_for_two_citations':train+residual+2}


if __name__=='__main__':print(json.dumps(audit(),sort_keys=True))
