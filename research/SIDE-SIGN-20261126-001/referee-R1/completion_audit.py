"""Test for both signs at the SAME four values on every archived hit, including unannotated hits."""
import gzip
import json
import sys
from collections import Counter, defaultdict
from itertools import islice
import numpy as np
from table_rebuild import GROWTH, HERE, forbid, lift

def basis(rows, n):
    eq = {}
    for row in rows:
        v = sum(1 << i for i in row)
        for p in sorted(eq, reverse=True):
            if v >> p & 1:
                v ^= eq[p]
        if v:
            eq[v.bit_length()-1] = v
    vectors = []
    for i in range(n):
        if i not in eq:
            v = 1 << i
            for p in sorted(eq):
                v |= ((eq[p] & v).bit_count() % 2) << p
            vectors.append(v)
    return vectors

def reduce_mask(v, e):
    for p in sorted(e, reverse=True):
        if v >> p & 1:
            v ^= e[p]
    return v

def parity_checker(rows, perm, pairs, name):
    b=basis(rows,len(perm))
    cols=[sum((v>>d & 1)<<i for i,v in enumerate(b)) for d in range(len(perm))]
    # q(x+y)+q(x)+q(y) against each basis vector is a linear form.
    pol=[0]*len(b)
    for l,r in pairs:
        for i in range(len(b)):
            if cols[l]>>i & 1: pol[i]^=cols[r]
            if cols[r]>>i & 1: pol[i]^=cols[l]
    def both(F):
        span={}
        for i in F:
            v=reduce_mask(cols[i],span)
            if v: span[v.bit_length()-1]=v
        if any(reduce_mask(v,span) for v in pol):
            return True
        ker=basis([[i for i in range(len(b)) if v>>i&1] for v in span.values()],len(b))
        def change(t):
            q=0
            for l,r in pairs:
                a,b=(cols[l]&t).bit_count()&1,(cols[r]&t).bit_count()&1
                q^=a*b
                if name=='W1c': q^=a^b
            return q
        return any(change(t) for t in ker)
    return both

def samples_nae(rows, perm, name):
    n=len(perm)
    pairs=[(d,g) for d,g in enumerate(perm) if d<g]
    def sector(mode):
        if mode=='flipped' and any(d==g for d,g in enumerate(perm)):
            return np.array([],dtype=np.uint32)
        if mode=='all':
            x=np.arange(1<<n,dtype=np.uint32)
        else:
            reps=[d for d,g in enumerate(perm) if d<=g]
            u=np.arange(1<<len(reps),dtype=np.uint32)
            x=np.zeros(len(u),dtype=np.uint32)
            for i,d in enumerate(reps):
                v=(u>>i)&1
                x|=v<<d
                if perm[d]!=d:
                    x|=(v ^ int(mode!='fixed'))<<perm[d]
        for r in rows:
            m=sum(1<<d for d in r)
            y=x&m
            x=x[(y!=0)&(y!=m)]
        return x
    if name in ('W3','W3m'):
        return sector('fixed'),sector('flipped' if name=='W3' else 'moved')
    x=sector('fixed' if name=='W1k' else 'all')
    odd=np.zeros(len(x),dtype=bool)
    for l,r in pairs:
        odd^=(((x>>l)&(x>>r)&1)!=0)
    return x[~odd],x[odd]

def pattern_bits(words, n):
    one=[int.from_bytes(np.packbits((words>>d)&1,bitorder='little').tobytes(),'little') for d in range(n)]
    return (1<<len(words))-1,one

def common_word(pos,neg,F):
    pairs=[(pos[0],neg[0])]
    for d in F:
        u,v=pos[1][d],neg[1][d]
        nxt=[]
        for a,b in pairs:
            if (a&u) and (b&v): nxt.append((a&u,b&v))
            if (a&~u) and (b&~v): nxt.append((a&~u,b&~v))
        if not nxt: return False
        pairs=nxt
    return True

def run(limit):
    starts=json.loads((GROWTH/'starts.json').read_text())
    counts=defaultdict(Counter)
    examples={}
    with gzip.open(HERE.parent/'census_results.jsonl.gz','rt') as f:
        for line in islice(f,limit):
            for row in json.loads(line)['result']['rows']:
                if isinstance(row['classes'],str):continue
                law=row['law']; rd=row['round']; idx=row['start'];rows=None
                for c in row['classes']:
                    # Complementation under not-all-equal bijects W1 and W1c fibres.
                    for nm,w in c['weightings'].items():
                        if law=='nae' and nm=='W1c':continue
                        hits={reading:{(tuple(h[0]),tuple(h[1])) for h in w[reading]['hits']} for reading in ('R1','R2')}
                        H=hits['R1']|hits['R2']
                        if not H:continue
                        if rows is None:
                            rows=forbid.supports_of(starts[idx])
                            for _ in range(rd):rows=forbid.grown(rows,law,'ordinary')[0]
                            holds=forbid.holders(rows)
                        p=c['perm'];perm=lift(rows,p)
                        if c['lift']=='max':
                            by=defaultdict(list)
                            for d,hs in holds.items():by[tuple(hs)].append(d)
                            for hs, ds in by.items():
                                if sorted(p[h] for h in hs)==list(hs):
                                    group=sorted(ds)
                                    for a,b in zip(group[::2],group[1::2]):perm[a],perm[b]=b,a
                        pairs=[(d,g) for d,g in enumerate(perm) if d<g]
                        if law=='parity':
                            if nm=='W2':
                                moved={i for i,j in enumerate(p) if i!=j}
                                a={min(moved)}
                                while True:
                                    bigger=a|{h for d,hs in holds.items() if perm[d]!=d and set(hs)<=moved
                                              and a.intersection(hs) for h in hs}
                                    if a==bigger:break
                                    a=bigger
                                sides=[[d for d,hs in holds.items() if set(hs)<=k] for k in (a,moved-a)]
                                pairs=[(i,j) for i in sides[0] for j in sides[1]]
                            else:
                                assert nm in ('W1','W1c')
                            judge=parity_checker(rows,perm,pairs,nm)
                        else:
                            positive,negative=samples_nae(rows,perm,nm)
                            # A small prefix proves presence. If it cannot decide, use every word.
                            short=[pattern_bits(xx[:256],len(perm)) for xx in (positive,negative)]
                            full=None
                            def judge(F):
                                nonlocal full
                                if common_word(*short,F):return True
                                if full is None:full=[pattern_bits(xx,len(perm)) for xx in (positive,negative)]
                                return common_word(*full,F)
                        cache={}
                        for a,b in H:
                            F=tuple(sorted(a+b))
                            if F not in cache:cache[F]=judge(F)
                            yes=cache[F]
                            for reading in hits:
                                if (a,b) in hits[reading]:
                                    key=f'{law}/{rd}/{nm}/{reading}'
                                    counts[key]['both signs' if yes else 'no opposite signs']+=1
                                    if not yes:
                                        examples.setdefault(key,dict(start=idx,perm=p,lift=c['lift'],readers=[a,b]))
    return dict(counts=counts,first_without_opposites=examples)

if __name__=='__main__':
    print(json.dumps(run(int(sys.argv[1]) if len(sys.argv)>1 else None),indent=1))
