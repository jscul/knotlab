# Referee's own minimal check: is heap id 7 (level 3) tied to heap id 255 (level 8) in P_N for d50c90fa37ed?
import gzip, json, sys, itertools
from pysat.solvers import Minisat22
CENSUS='/home/jscul/p-vs-np-contact-first/artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz'
key=None
for l in gzip.open(CENSUS,'rt'):
    r=json.loads(l)
    if r['case'].startswith('d50c90fa37ed'): key=r['key']; break
s, sw, d0, d1, placements = key
W=[()]+[(q,) for q in range(s)]+[(q,r) for q in range(s) for r in range(s)]
def apply(word, bits):
    ws=list(word); out=[]
    for b in bits:
        c=b
        for i in range(len(ws)-1,-1,-1):
            q=ws[i]; ws[i]= d0[q] if c==0 else d1[q]; c^=sw[q]
        out.append(c)
    return tuple(out)
def hid(bits):  # heap id: root 0, children 2v+1, 2v+2
    v=0
    for b in bits: v=2*v+1+b
    return v
def pattern(N):
    knots=set()
    for n in range(N+1):
        for bits in itertools.product((0,1),repeat=n):
            for p in placements:
                mem=[]; skip=False
                for t in p:
                    wi,slot=divmod(t,3); a=apply(W[wi],bits)
                    if slot: 
                        if n==N: skip=True; break
                        a=a+(slot-1,)
                    mem.append(hid(a))
                if skip or len(set(mem))<3: continue
                knots.add(tuple(sorted(mem)))
    return knots
def tied(N,u,v):
    K=pattern(N); res=[]
    for want in (0,1):   # 0: u==v possible? 1: u!=v possible?
        S=Minisat22()
        for a,b,c in K:
            S.add_clause([a+1,b+1,c+1]); S.add_clause([-(a+1),-(b+1),-(c+1)])
        S.add_clause([u+1]); S.add_clause([v+1] if want==0 else [-(v+1)])
        res.append(S.solve()); S.delete()
    return res, len(K)
for N in (9,10,11):
    print(N, 'u=v sat, u!=v sat:', tied(N,7,255))
