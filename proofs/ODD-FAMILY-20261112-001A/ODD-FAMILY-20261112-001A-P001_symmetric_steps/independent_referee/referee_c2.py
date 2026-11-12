from ref import *
for n in (67,71):
    S=sorted({1,2,3,n-1,n-2,n-3}); K=kinds(n,S); cl=[]
    L=n
    for (a,b) in K:
        for i in range(L-b): nae(cl,[i+1,i+a+1,i+b+1])
    with Solver(bootstrap_with=cl) as s: print(n,"t=3 kinds",len(K),"window length n satisfiable:",s.solve())
