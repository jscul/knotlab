from ref import *
def S_of(n,G): return sorted({g%n for g in G}|{(-g)%n for g in G})
for n in (89,97):
    H=[h for h in range(1,n) if pow(h,4,n)==1]; S=S_of(n,H+[2*h for h in H])
    ex,fl,m=flip_sat(n,S); K=kinds(n,S)
    print(n,"H",H,"S",S,"exists",ex,"flip",fl,"window(n+1) nonperiodic SAT",window_sat(n,K,L=4*n))
for n in (67,71):
    bad=[]
    for t in range(1,n):
        S=S_of(n,[1,2,t]); ex,fl,_=flip_sat(n,S)
        if not (ex and fl): bad.append((t,ex,fl))
    print(n,"t failing (would be harmony/vacuous):",bad)
