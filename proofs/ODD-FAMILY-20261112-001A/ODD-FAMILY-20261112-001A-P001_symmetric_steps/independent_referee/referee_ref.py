import sys, itertools, math
from pysat.solvers import Cadical153 as Solver
def kinds(n,S):
    K=set()
    for a in range(1,n):
        for b in range(a+1,n):
            R={0,a,b}
            if any({(t+k*s)%n for k in range(3)}==R for s in S for t in R): K.add((a,b))
    return sorted(K)
def triples(n,S):
    return {frozenset((r+k*s)%n for k in range(3)) for s in S for r in range(n)}
def nae(cl,v):  # v: list of literals
    cl.append(list(v)); cl.append([-x for x in v])
def enum(n,S):
    T=triples(n,S); cl=[]
    for t in T: nae(cl,[r+1 for r in t])
    sols=[]
    with Solver(bootstrap_with=cl) as s:
        while s.solve():
            m=s.get_model(); w=tuple(1 if m[i]>0 else 0 for i in range(n)); sols.append(w)
            s.add_clause([-m[i] for i in range(n)])
    return sols,T
def compat(w,T): return all(len({w[r] for r in t})==2 for t in T)
def classes(sols,n):
    seen=set(); c=0
    for w in sols:
        if w in seen: continue
        c+=1
        for k in range(n):
            r=w[k:]+w[:k]; seen.add(r); seen.add(tuple(1-x for x in r))
    return c
def window_sat(n,K,L=None,j=None):
    L=L or 4*n; j=2*n if j is None else j; cl=[]
    for (a,b) in K:
        for i in range(L-b): nae(cl,[i+1,i+a+1,i+b+1])
    cl+= [[j+1,j+n+1],[-(j+1),-(j+n+1)]]
    with Solver(bootstrap_with=cl) as s: return s.solve()
def flip_sat(n,S):  # compatible w with w^(pos0 flipped) also compatible; also whether any compatible exists
    T=triples(n,S); cl=[]; cl0=[]
    for t in T:
        v=[r+1 for r in t]; nae(cl,v); nae(cl0,v)
        if 0 in t: nae(cl,[-(r+1) if r==0 else r+1 for r in t])
    with Solver(bootstrap_with=cl0) as s: ex=s.solve()
    with Solver(bootstrap_with=cl) as s: fl=s.solve(); m=s.get_model() if fl else None
    return ex,fl,m
if __name__=="__main__":
    for n,S in [(73,[1,2,27,54]),(193,[1,2,31,54,65,81,112,128,139,162,191,192])]:
        S=sorted({s%n for s in S}|{(-s)%n for s in S}); K=kinds(n,S)
        print(n,"S=",S,"#kinds",len(K),K)
        print(" gcd offsets",math.gcd(*[x for k in K for x in k]))
        sols,T=enum(n,S); print(" #words",len(sols),"classes",classes(sols,n), "all compat",all(compat(w,T) for w in sols))
        # check enumerated words have minimal period n
        print(" nonconst",all(len(set(w))==2 for w in sols))
        import numpy as np
        A=np.array(sols,dtype=np.int16); D=(A[:,None,:]!=A[None,:,:]).sum(2); np.fill_diagonal(D,10**6)
        print(" min dist",D.min())
        print(" window 4n SAT (x_j!=x_{j+n}):",window_sat(n,K), " window n+1:",window_sat(n,K,L=n+1,j=0))
