# Prototype: Anthropic Theorem B pieces on Q[t1,t2,...] (partition basis), exact integer arithmetic.
import itertools, math, sys, time
from functools import lru_cache
from collections import defaultdict

def partitions(n, maxpart=None):
    if maxpart is None: maxpart=n
    if n==0: yield (); return
    for k in range(min(n,maxpart),0,-1):
        for rest in partitions(n-k,k): yield (k,)+rest

def gbinom(n, j):
    """C(n, j) for integer n (any sign), j >= 0; 0 for j < 0"""
    if j<0: return 0
    num=1
    for i in range(j): num*= (n-i)
    return num//math.factorial(j) if num % math.factorial(j)==0 else None

# polynomials: dict partition(tuple nonincreasing) -> int
def add(acc, poly, c=1):
    for m,v in poly.items():
        acc[m]=acc.get(m,0)+c*v
        if acc[m]==0: del acc[m]
    return acc
def mult_t(poly, l):
    out={}
    for m,v in poly.items():
        nm=tuple(sorted(m+(l,), reverse=True)); out[nm]=out.get(nm,0)+v
    return out
def nabla_pos(poly, k):
    """k d/dt_k"""
    out={}
    for m,v in poly.items():
        c=m.count(k)
        if c==0: continue
        lst=list(m); lst.remove(k); nm=tuple(lst)
        out[nm]=out.get(nm,0)+v*k*c
    return out
def weight(poly):
    ws={sum(m) for m in poly}
    assert len(ws)<=1, ws
    return ws.pop() if ws else None

def apply_mono(parts, r, poly):
    """monomial a = t^parts (tuple, any order), operator a[r] applied to homogeneous poly, via recursion (O2)"""
    if not poly: return {}
    if len(parts)==0:
        return dict(poly) if r==0 else {}
    E=weight(poly)
    n=parts[0]; rest=parts[1:]
    out={}
    # sum_{l>=n} C(l-1,n-1) t_l a'[r-l] f   ; need E + r - l >= 0 for nonzero (a' maps V_E -> V_{E+r-l})
    for l in range(n, E+r+1):
        c=gbinom(l-1,n-1)
        if c==0: continue
        inner=apply_mono(rest, r-l, poly)
        if inner: add(out, mult_t(inner,l), c)
    # sum_{k>=1} C(-k-1, n-1) a'[r+k] nabla_k f
    for k in range(1, E+1):
        c=gbinom(-k-1,n-1)
        if c==0: continue
        d=nabla_pos(poly,k)
        if not d: continue
        inner=apply_mono(rest, r+k, d)
        if inner: add(out, inner, c)
    return out

def apply_poly(a, r, poly):
    out={}
    for m,v in a.items():
        add(out, apply_mono(m, r, poly), v)
    return out

def y_poly(n):
    return {(j,): gbinom(n,j) for j in range(1,n+1)}
def poly_mul(p,q):
    out={}
    for m1,v1 in p.items():
        for m2,v2 in q.items():
            nm=tuple(sorted(m1+m2, reverse=True)); out[nm]=out.get(nm,0)+v1*v2
    return {m:v for m,v in out.items() if v!=0}
def a_mu(mu):
    p={():1}
    for part in mu:
        p=poly_mul(p, {m: ((-1)**(part-1))*v for m,v in y_poly(part).items()})
    return p
def z_mu(mu):
    z=1
    for k in set(mu):
        c=mu.count(k); z*= (k**c)*math.factorial(c)
    return z
def b_mu(mu, h):
    return {tuple(mu): math.factorial(h)//z_mu(mu)}
def a_angle(a, i, h):
    """a<i> = sum_h' C(h'+h, i) abar_h'"""
    out={}
    for m,v in a.items():
        hp=sum(m)
        out[m]=out.get(m,0)+gbinom(hp+h,i)*v
    return {m:v for m,v in out.items() if v!=0}

def Q_s_apply(a, b, s, h, f):
    out={}
    for i in range(0, 2*h+1):
        g=apply_poly(b, h-s-i, f)
        if not g: continue
        ai=a_angle(a,i,h)
        add(out, apply_poly(ai, s-h+i, g), (-1)**i)
    return out

def run(lam):
    h=2
    while len(list(partitions(h)))<2**lam: h+=1
    parts_h=sorted(partitions(h))  # lexicographic as nonincreasing tuples
    # paper: lexicographic list of partitions written as nonincreasing sequences, numbered from 0
    mus=parts_h[:2**lam]
    A={}  # (s,x,y,u,v) -> value
    t0=time.time()
    a_cache={x: a_mu(mus[x]) for x in range(2**lam)}
    b_cache={v: b_mu(mus[v],h) for v in range(2**lam)}
    S=range(-2*h, 2*h+1)
    total=defaultdict(int)
    pieces={}
    for x in range(2**lam):
        for v in range(2**lam):
            for y in range(2**lam):
                f={tuple(mus[y]):1}
                for s in S:
                    q=Q_s_apply(a_cache[x], b_cache[v], s, h, f)
                    for u in range(2**lam):
                        val=q.get(tuple(mus[u]),0)
                        pieces[(s,x,y,u,v)]=val
                        total[(x,y,u,v)]+=val
    ok=all(total[(x,y,u,v)]==math.factorial(h)*int(x==v and y==u) for x in range(2**lam) for y in range(2**lam) for u in range(2**lam) for v in range(2**lam))
    return h, mus, pieces, ok, time.time()-t0

if __name__=='__main__':
    for lam in map(int, sys.argv[1:]):
        h, mus, pieces, ok, dt = run(lam)
        print("lambda",lam,"h",h,"sum identity holds:",ok,"time",round(dt,1))
