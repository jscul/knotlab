"""Retest the two post-run comparison stages using exact transforms and holder-disjoint readings."""
from itertools import combinations
from fractions import Fraction
import json
import random
import sys
import numpy as np
from table_rebuild import HERE, GROWTH, forbid
from completion_audit import basis

def transform(f):
    w=f.copy()
    size=1
    while size<len(w):
        pairs=w.reshape((-1,2*size))
        a=pairs[:,:size].copy()
        b=pairs[:,size:]
        pairs[:,:size]=a+b
        b[:]=a-b
        size*=2
    return w

def prepare(idx,law):
    starts=json.loads((GROWTH/'starts.json').read_text())
    rows=forbid.supports_of(starts[idx])
    for _ in range(2): rows=forbid.grown(rows,law,'ordinary')[0]
    n=len(forbid.holders(rows))
    holds={k:set(v) for k,v in forbid.holders(rows).items()}
    ctx=[]
    for a,b in combinations(range(n),2):
        valid=[i for i in range(n) if not holds[i]&(holds[a]|holds[b])]
        for c,d in combinations(valid,2):ctx.append([a*n+c,a*n+d,b*n+c,b*n+d])
    if law=='parity':
        B=basis(rows,n)
        forms=np.array([sum((v>>d&1)<<i for i,v in enumerate(B)) for d in range(n)],dtype='int64')
        words=np.zeros(1,dtype=np.uint32)
        for v in B:words=np.concatenate((words,words^v))
        vals=None
    else:
        words=np.arange(1<<n,dtype=np.uint32)
        forms=1<<np.arange(n)
        ok=np.ones(len(words),dtype=bool)
        for row in rows:
            m=sum(1<<d for d in row); masked=words&m
            ok&=(masked!=0)&(masked!=m)
        vals=transform(ok.astype('int64'))
    return words,forms,np.array(ctx),vals

def evaluate(spectrum,forms,ctx,offset,which):
    n=len(forms);z=int(spectrum[offset]); left=spectrum[forms^offset][:,None];right=left.T
    xy=spectrum[forms[:,None]^forms[None,:]^offset]
    four=np.array([z+left+right+xy,z+left-right-xy,z-left+right-xy,z-left-right+xy])//4
    def finish(e,den,ok):
        score=np.max(np.abs(e.sum(axis=1)[:,None]-2*e),axis=1)
        h=int(((score>2*den)&ok).sum())
        if not np.any(ok):return None,h
        d=den[ok];s=score[ok]
        best=max(Fraction(int(s[d==v].max()),int(v)) for v in np.unique(d))
        return str(best),h
    if which=='R1':
        if not z:return None,0
        ok=(four*np.sign(z)>=0).all(axis=0).ravel()[ctx].all(axis=1)
        return finish(xy.ravel()[ctx],np.full(len(ctx),abs(z)),ok)
    square=four**2
    s=square.sum(axis=0).ravel()[ctx]
    ok=(s>0).all(axis=1)&(s==s[:,:1]).all(axis=1)
    a=(square[0]+square[1]).ravel()[ctx];b=(square[0]+square[2]).ravel()[ctx]
    ok&=(a[:,0]==a[:,1])&(a[:,2]==a[:,3])&(b[:,0]==b[:,2])&(b[:,1]==b[:,3])
    return finish((square[0]-square[1]-square[2]+square[3]).ravel()[ctx],s[:,0],ok)

def run(limit):
    root=HERE.parent
    words,forms,ctx,_=prepare(26,'parity')
    def parity(pairs,r):
        q=np.zeros(len(words),dtype=np.uint32)
        for a,b in pairs:q^=words>>a & (words>>b) & 1
        return evaluate(transform(1-2*q.astype('int64')),forms,ctx,0,r)
    meta=json.loads((root/'posthoc_match_26.json').read_text())
    rng=random.Random(meta['seed'])
    random_best=[]
    for _ in range(min(limit,200)):
        names=list(range(len(forms)));rng.shuffle(names)
        random_best.append(parity(list(zip(names[:22:2],names[1:22:2])),'R1')[0])
    cz=json.loads((root/'posthoc_cz_26.json').read_text())['one pairwise sign on an arbitrary pair']
    cz_bad=0
    for row in cz[:limit]:
        for r in ('R1','R2'):
            cz_bad+=parity([(row['u'],row['v'])],r)!=(row[r+' best'],row[r+' hits'])
    words,forms,ctx,vals=prepare(421,'nae')
    local=json.loads((root/'posthoc_local_421.json').read_text())['two-distinction products of single signs']
    local_bad=0
    best_by= {'R1':[], 'R2':[]}
    for row in local[:limit]:
        for r in ('R1','R2'):
            mx,h=evaluate(vals,forms,ctx,(1<<row['u'])|(1<<row['v']),r)
            local_bad+=(mx,h)!=(row[r+' best'],row[r+' hits'])
            if h:best_by[r].append(Fraction(mx))
    return dict(random_pairings=len(random_best),random_pairings_with_excess=random_best.count('4'),
                random_differences=sum(x!=y for x,y in zip(random_best,meta['random best'])),
                one_pair_trials=len(cz[:limit]),one_pair_differences=cz_bad,
                single_sign_product_trials=len(local[:limit]),single_sign_product_differences=local_bad,
                product_excess={r:[len(v),str(max(v)) if v else None] for r,v in best_by.items()})

if __name__=='__main__':print(json.dumps(run(int(sys.argv[1]) if len(sys.argv)>1 else 253),indent=1))
