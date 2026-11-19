"""Post hoc (after the run was read): refined radius for the rank >= 2 pieces whose run estimate exceeds 2.25: the least solution by iteration, then Newton at fixed z, and z counts as below the radius when the solution is finite with Jacobian spectral radius below 1; bisection on z. Output recorded in posthoc_rates.json."""
import sys, numpy as np
from collections import Counter
sys.path.insert(0,'/home/jscul/p-vs-np-contact-first/proofs/DEAD-CAP-20261119-001A/DEAD-CAP-20261119-001A-P001_dead')
import deadlib as DL
sys.path.insert(0,'/home/jscul/p-vs-np-contact-first/scripts')
from longrun import load_results
def system(A,P):
    inc=[(p,w) for w in P['blocks'] for p in A['blocks'][w]]
    idx={x:i for i,x in enumerate(inc)}
    terms=[]
    for (p,w) in inc:
        fac=[]
        for q in A['blocks'][w]:
            if q==p: continue
            fac.append((q,[idx[(q,w2)] for w2 in A['of'].get(q,[]) if w2!=w]))
        terms.append(fac)
    def e(q,z):
        sp,rp,o=A['spares'][q],A['raypend'][q],A['open'][q]
        v=(1+z)**sp
        if rp and o==2: v*=(1/(1-z))**rp
        elif rp and o==1: v*=(1+z/(1-z)**2)**rp
        return v
    def F(b,z):
        out=np.empty(len(inc))
        for i,fac in enumerate(terms):
            prod=1.0
            for q,js in fac:
                t=z*e(q,z)
                for j in js: t*=b[j]
                prod*=1+t
            out[i]=prod
        return out
    def Jac(b,z):
        M=len(inc); Jm=np.zeros((M,M))
        for i,fac in enumerate(terms):
            vals=[]
            for q,js in fac:
                t=z*e(q,z)
                for j in js: t*=b[j]
                vals.append(1+t)
            tot=np.prod(vals)
            for k,(q,js) in enumerate(fac):
                rest=tot/vals[k]
                t=z*e(q,z)
                for j in js:
                    d=t
                    for j2 in js:
                        if j2!=j: d*=b[j2]
                    Jm[i,j]+=rest*d
        return Jm
    return len(inc),F,Jac
def below(A,P,z):
    M,F,Jac=system(A,P)
    b=np.ones(M)
    for _ in range(3000):
        nb=F(b,z)
        if not np.all(np.isfinite(nb)) or np.max(nb)>1e9: return False
        if np.max(np.abs(nb-b))<1e-12: b=nb; break
        b=nb
    for _ in range(60):
        g=F(b,z)-b
        if np.max(np.abs(g))<1e-12: break
        try: b=b-np.linalg.solve(Jac(b,z)-np.eye(M),g)
        except Exception: return False
        if not np.all(np.isfinite(b)) or np.min(b)<1: return False
    if np.max(np.abs(F(b,z)-b))>1e-9: return False
    return max(abs(np.linalg.eigvals(Jac(b,z))))<1
def rate(A,P,lo=0.0,hi=1.0):
    for _ in range(45):
        mid=(lo+hi)/2
        if below(A,P,mid): lo=mid
        else: hi=mid
    return 1/lo
if __name__=='__main__':
    R=load_results('/home/jscul/p-vs-np-contact-first/runs/dead-cap')
    st=[x for cid,r in R.items() if cid.startswith('skel') or cid.startswith('fam') for x in r['result']['starts'] if x['edges'] and max(x['ranks'])>=2]
    top=[x for x in st if x['rate']>2.25]
    worst=0; out=[]
    for x in top:
        A=DL.analyse(x['sizes'],x['edges'])
        for P in A['pieces']:
            if P['rank']>=2:
                r=rate(A,P); out.append((round(r,6), round(x['rate'],6))); worst=max(worst,r)
    print(len(top), 'refined max', worst)
    print(Counter(o[0] for o in out).most_common(6))
    print('max shift from the run estimate', max(a-b for a,b in out))
