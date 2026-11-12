from pysat.solvers import Cadical153
from math import gcd
from functools import reduce
p=61; S=[1,2,11,22]
assert all((11*s)%p in {t%p for t in S}|{(-t)%p for t in S} for s in S)
trip=set()
for s in S:
  for sg in (1,-1):
    for t in range(p): trip.add(frozenset(((t+sg*k*s)%p) for k in range(3)))
K=sorted({(0,a,b) for a in range(1,p) for b in range(a+1,p) if frozenset({0,a,b}) in trip})
print("(1) kinds",len(K),K)
print("residue triples",len(trip))
def nae(sol,v): sol.add_clause(v); sol.add_clause([-x for x in v])
# (2) enumerate periodic words
sol=Cadical153()
for T in trip: nae(sol,[r+1 for r in T])
W=[]
while sol.solve():
  m=sol.get_model(); w=tuple(1 if m[r]>0 else 0 for r in range(p)); W.append(w)
  sol.add_clause([-(r+1) if w[r] else r+1 for r in range(p)])
print("(2) count",len(W))
Ws=set(W)
orbits=[];seen=set()
for w in W:
  if w in seen: continue
  o={w[k:]+w[:k] for k in range(p)}; seen|=o; orbits.append(o)
print(" orbits",len(orbits),[len(o) for o in orbits])
fl=tuple(1-v for v in next(iter(orbits[0])))
print(" flip swaps orbits:",fl in orbits[1])
# allowed periodic check via kinds directly on bi-infinite (one period suffices)
def ok(w): return all(len({w[i%p],w[(i+a)%p],w[(i+b)%p]})==2 for i in range(p) for _,a,b in K)
print(" all satisfy K:",all(ok(w) for w in W))
# (3)
d1=sum(1 for i in range(len(W)) for j in range(i+1,len(W)) if sum(x!=y for x,y in zip(W[i],W[j]))==1)
print("(3) pairs at distance 1:",d1, " min dist:",min(sum(x!=y for x,y in zip(W[i],W[j])) for i in range(len(W)) for j in range(i+1,len(W))))
# (5) direct SAT on long window
for N in (400,1000):
  s=Cadical153()
  for i in range(N):
    for _,a,b in K:
      if i+b<N: nae(s,[i+1,i+a+1,i+b+1])
  for j in range(N//2-80,N//2+20):
    r=s.solve(assumptions=[]) if False else None
  # one solve with disjunction of differences in middle band
  aux=[]
  base=N+1
  for k,j in enumerate(range(N//2-80,N//2+20)):
    d=base+k; aux.append(d)
    # d -> x_j != x_{j+61}
    s.add_clause([-d,j+1,j+62]); s.add_clause([-d,-(j+1),-(j+62)])
  s.add_clause(aux)
  print("(5) N=%d nonperiodic band SAT?"%N, s.solve())
  s2=Cadical153()
  for i in range(N):
    for _,a,b in K:
      if i+b<N: nae(s2,[i+1,i+a+1,i+b+1])
  print("    window satisfiable at all:",s2.solve())
# minimal margin: smallest N where x_c != x_{c+61} centered is UNSAT
offs=[o for k in K for o in k[1:]]
print("(6) gcd",reduce(gcd,offs))
