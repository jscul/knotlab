"""Whole-answer probabilities and exact certificates of membership or separation."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations,product
from math import gcd,lcm,prod
import json
import numpy as np
from scipy import linalg,sparse
from scipy.optimize import linprog
from completions import HERE,ROOT,OUT,gram,literal


def save(name,data):
    (OUT/name).write_text(json.dumps(data,sort_keys=True,separators=(",",":"))+"\n")


def compress(vals,den):
    common=gcd(den,*vals)
    return [v//common for v in vals],den//common


def from_fractions(q):
    den=lcm(*(x.denominator for x in q))
    vals,den=compress([int(x*den) for x in q],den)
    return vals,den


def affine_moment(g,t,z):
    return sum((-1 if (x&z).bit_count()&1 else 1)*int(g[x,x^t]) for x in range(len(g)))


def rows_for(g,settings):
    n=len(settings); trace=sum(int(g[x,x]) for x in range(len(g)))
    assert trace>0
    qs=[];cache={}
    for sets in product(*(range(len(r)) for r in settings)):
        picked=[r[i] for r,i in zip(settings,sets)]
        moments=[]
        for selector in range(1<<n):
            t,z=0,0
            for i,(kind,bits) in enumerate(picked):
                if selector>>i&1:
                    if kind=="X":t^=bits
                    elif kind=="Z":z^=bits
                    else:raise ValueError(kind)
            assert not(t&z)
            if (t,z) not in cache:
                cache[t,z]=affine_moment(g,t,z)
            moments.append(cache[t,z])
        vals=[sum((-1 if (s&x).bit_count()&1 else 1)*c for s,c in enumerate(moments)) for x in range(1<<n)]
        nums,den=compress(vals,trace*(1<<n))
        assert min(nums)>=0 and sum(nums)==den
        qs.append(dict(settings=list(sets),numerators=nums,denominator=den))
    return qs


def seq_prob(row):
    return [F(v,row["denominator"]) for v in row["numerators"]]


def expectation(row,subset):
    return F(sum((-1 if (x&subset).bit_count()&1 else 1)*v for x,v in enumerate(row["numerators"])),row["denominator"])


def margins(rows,n):
    result={}
    for k in range(n):
        for row in rows:
            setting=row["settings"][k];key=f"{k}/{setting}"
            pp=F(sum(v for x,v in enumerate(row["numerators"]) if not (x>>k&1)),row["denominator"])
            if key in result:assert result[key]==str(pp)
            result[key]=str(pp)
    return result


def mermin(rows,n):
    return sum(((-1)**(sum(r["settings"])//2))*expectation(r,(1<<n)-1) for r in rows if sum(r["settings"])%2==0)


def rot_mermin(rows,n):
    return mermin(rows,n)+sum(((-1)**(sum(r["settings"])//2))*expectation(r,(1<<n)-1) for r in rows if sum(r["settings"])%2)


def specs(settings):
    return tuple(tuple(2 for a in party) for party in settings)


@lru_cache(maxsize=16)
def strategy_matrix(sizes):
    """Column index records each party's whole answer to each possible own setting."""
    shapes=[len(p) for p in sizes]
    offsets=np.r_[0,np.cumsum(shapes)]
    per=[o for party in sizes for o in party]
    strategies=np.array(list(product(*(range(k) for k in per))),dtype=np.int16)
    settings=list(product(*(range(k) for k in shapes)))
    offsetsrow=0;rows=[]
    for s in settings:
        mult=1;idx=np.zeros(len(strategies),dtype=int)
        for j,choice in enumerate(s):
            idx+=mult*strategies[:,offsets[j]+choice]
            mult*=sizes[j][choice]
        rows.append(idx+offsetsrow);offsetsrow+=mult
    cols=np.tile(np.arange(len(strategies)),len(rows));rowvector=np.concatenate(rows)
    a=sparse.csc_matrix((np.ones(len(cols)),(rowvector,cols)),shape=(offsetsrow,len(strategies)))
    return a,strategies


def full_certificate(rows,sizes):
    a,strategies=strategy_matrix(sizes);target=sum((seq_prob(r) for r in rows),[])
    f=np.array(list(map(float,target)))
    result=linprog(np.zeros(len(strategies)),A_eq=a,b_eq=f,bounds=(0,None),method="highs-ds")
    if result.success:
        active=np.where(result.x>1e-10)[0]
        arr=a[:,active].toarray().astype(int)
        vals=[F(float(result.x[i])).limit_denominator(4096) for i in active]
        def valid(ws):
            if any(x<0 for x in ws) or sum(ws)!=1:return False
            return all(sum(w for w,v in zip(ws,row) if v)==q for row,q in zip(arr,target))
        if not valid(vals):
            import sympy as sp
            _,_,piv=linalg.qr(arr.T,pivoting=True,mode="economic")
            independent=[int(v) for v in piv[:len(active)]]
            mat=sp.Matrix(arr[independent,:])
            exact=mat.inv(method="DM")*sp.Matrix([sp.Rational(target[i].numerator,target[i].denominator) for i in independent])
            vals=[F(int(x.p),int(x.q)) for x in exact]
        if valid(vals):
            return dict(local=True,lists=len(strategies),mixture=[[int(i),str(w)] for i,w in zip(active,vals) if w])
    # Separate by an inequality; floating point only chooses its proposed coefficients.
    q=sparse.hstack((a.T,-np.ones((len(strategies),1))),format="csr")
    dual=linprog(np.r_[-f,1.0],A_ub=q,b_ub=np.zeros(len(strategies)),
                 bounds=[(-1,1)]*len(f)+[(None,None)],method="highs-ds")
    assert dual.success
    coeff=[F(float(x)).limit_denominator(10000) for x in dual.x[:-1]]
    d=lcm(*(x.denominator for x in coeff));ys=[int(c*d) for c in coeff]
    factor=gcd(*ys) or 1;ys=[v//factor for v in ys]
    counts=np.asarray(a.T.dot(np.array(ys,dtype=np.int64))).ravel()
    bound=int(max(counts)); measured=sum(c*t for c,t in zip(ys,target))
    if measured<=bound:
        return exact_phase_one(rows,sizes)
    return dict(local=False,lists=len(strategies),inequality=[[i,v] for i,v in enumerate(ys) if v],bound=bound,value=str(measured))


def singleton(n):
    return [[("X",1<<i),("Z",1<<i)] for i in range(n)]


def behavior(g,settings,certificate=True):
    rows=rows_for(g,settings)
    out=dict(rows=rows,margins=margins(rows,len(settings)),m=str(mermin(rows,len(settings))) if all(len(s)==2 for s in settings) else None)
    if certificate:out["common"]=full_certificate(rows,specs(settings))
    return out


def basic(g):
    return behavior(g,singleton((len(g)-1).bit_length()))


def literal_projectors(f,settings):
    """Project each physical assignment on every choice, independently of the off-diagonal trace route."""
    hidden,dimension=f.shape;n=len(settings);trace=int((f*f).sum());inds=np.arange(dimension)
    out=[]
    for sets in product(*(range(len(q)) for q in settings)):
        choices=[q[j] for q,j in zip(settings,sets)]
        vals=[]
        for x in range(1<<n):
            v=f
            for i,(kind,bits) in enumerate(choices):
                if kind=="X":w=v[:,inds^bits]
                else:w=v*np.array([(-1 if (int(k)&bits).bit_count()&1 else 1) for k in inds])
                v=v+(1-2*(x>>i&1))*w
            vals.append(int((v*v).sum()))
        v,d=compress(vals,trace*(4**n))
        out.append(dict(settings=list(sets),numerators=v,denominator=d))
    return out


@lru_cache(maxsize=3)
def phase_one_rows(sizes):
    a,_=strategy_matrix(sizes); dense=a.toarray()
    _,r,piv=linalg.qr(dense.T,pivoting=True,mode="economic")
    rank=int(np.count_nonzero(np.abs(np.diag(r))>1e-8))
    select=[int(i) for i in piv[:rank]]
    return select,dense[select].astype(int)


def exact_phase_one(rows,sizes):
    """Exact Phase I with Bland pivots for probabilities found too close to a face numerically."""
    a,strategies=strategy_matrix(sizes)
    target=sum((seq_prob(r) for r in rows),[])
    selected,arr=phase_one_rows(sizes)
    r,n=arr.shape
    vals=[target[i] for i in selected]
    tableau=[[F(int(v)) for v in line]+[F(int(j==i)) for j in range(r)] for i,line in enumerate(arr)]
    basis=[n+i for i in range(r)]
    reduced=[sum(row[j] for row in tableau) for j in range(n)]+[F(0)]*r
    while True:
        entry=next((j for j,v in enumerate(reduced) if v>0),None)
        if entry is None:break
        choices=[(vals[i]/line[entry],basis[i],i) for i,line in enumerate(tableau) if line[entry]>0]
        _,_,i=min(choices)
        div=tableau[i][entry];new=[v/div for v in tableau[i]];rhs=vals[i]/div
        for k,line in enumerate(tableau):
            if k!=i and line[entry]:
                coeff=line[entry]
                tableau[k]=[u-coeff*v for u,v in zip(line,new)]
                vals[k]-=coeff*rhs
        tableau[i]=new;vals[i]=rhs;basis[i]=entry
        coeff=reduced[entry];reduced=[c-coeff*v for c,v in zip(reduced,new)]
    if not sum(v for j,v in zip(basis,vals) if j>=n):
        mixture={k:v for k,v in zip(basis,vals) if k<n and v}
        actual=[F(0)]*len(target)
        for j,v in mixture.items():
            for i in a.indices[a.indptr[j]:a.indptr[j+1]]:actual[i]+=v
        assert min(mixture.values())>=0 and sum(mixture.values())==1 and actual==target
        return dict(local=True,lists=n,mixture=[[j,str(v)] for j,v in sorted(mixture.items())],exact_phase_one=True)
    coeffs=[F(0)]*len(target)
    for j,idx in enumerate(selected):
        coeffs[idx]=sum(tableau[i][n+j] for i,b in enumerate(basis) if b>=n)
    scale=lcm(*(v.denominator for v in coeffs))
    cs=[int(v*scale) for v in coeffs]
    sign=gcd(*cs) or 1;cs=[v//sign for v in cs]
    # Python integer evaluation keeps the dual valid even when counts exceed a machine word.
    bound=max(sum(cs[i] for i in a.indices[a.indptr[j]:a.indptr[j+1]]) for j in range(n))
    observed=sum(c*q for c,q in zip(cs,target))
    assert observed>bound
    return dict(local=False,lists=n,inequality=[[i,v] for i,v in enumerate(cs) if v],bound=bound,value=str(observed),exact_phase_one=True)
