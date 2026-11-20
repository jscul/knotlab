"""Exact signed changes, whole-answer tables and checkable common explanations."""
from fractions import Fraction
from itertools import combinations, product
import hashlib
import json
import os
from pathlib import Path

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
import numpy as np
from scipy import sparse
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
BASELINE = ROOT / "artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/games.json"
ID = (0, 0, 1)
LAW = ("parity", "nae")
WORDS = tuple("".join(p) for p in product("01", repeat=3))


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, sort_keys=True, separators=(",", ":"))+"\n")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parity(x):
    return x.bit_count() & 1


def mask(s):
    return sum(1 << bit for bit in s)


def mul(left, right):
    t, z, sign = left
    u, v, scale = right
    return t ^ u, z ^ v, sign * scale * (-1 if parity(z & u) else 1)


def times(*words):
    result = ID
    for word in words:
        result = mul(result, word)
    return result


def read(*bits):
    return 0, mask(bits), 1


def change(*bits):
    return mask(bits), 0, 1


def signed(word, sign):
    return word[0], word[1], word[2]*sign


def action(word, vector):
    t,z,sign = word
    inds = np.arange(len(vector))
    flip = np.array([1-2*parity(int(x) & z) for x in inds], dtype=np.int64)
    return (sign * flip * vector)[inds ^ t]


def labels(logicals):
    (x,z),(u,v) = logicals
    return (x,u,mul(x,u),v,z,mul(z,v),mul(x,v),mul(z,u),signed(times(x,z,u,v),-1))


def questions(ops, role):
    ix = range(3)
    return tuple(tuple(ops[3*i+j] for j in ix) for i in ix) if role=="A" else tuple(tuple(ops[3*i+j] for i in ix) for j in ix)


def allowed(x, s, law):
    v = x & mask(s)
    return not parity(v) if law=="parity" else v not in (0,mask(s))


def weighting(stars, law, width=None, pins=()):
    width = width or (1+max(map(max,stars)))
    return np.array([int(all(allowed(x,s,law) for s in stars) and not x & mask(pins)) for x in range(1 << width)],dtype=np.int64)


def records(width):
    return tuple("".join(x) for x in product("01",repeat=width))


def projector(vector, question, rec):
    for word,ch in zip(question, rec, strict=True):
        vector = vector + (1-2*int(ch))*action(word,vector)
    return vector


def full_table(vector, alice, bob):
    from math import gcd
    rows = []
    for i,aq in enumerate(alice):
        for j,bq in enumerate(bob):
            assert all(mul(a,b)==mul(b,a) for a,b in combinations((*aq,*bq),2))
            assert all(mul(a,a)==ID for a in (*aq,*bq))
            words_a,words_b = records(len(aq)),records(len(bq))
            counts=[]
            vnorm=int(vector@vector)
            for a in words_a:
                av=projector(vector,aq,a)
                for b in words_b:
                    v=projector(av,bq,b)
                    counts.append(int(v@v))
            den=vnorm * 4**(len(aq)+len(bq))
            assert sum(counts)==den
            common=gcd(den,*counts)
            rows.append(dict(settings=[i,j],numerators=[v//common for v in counts],denominator=den//common,
                             raw_denominator=den))
    return rows


def probability_table(rows):
    return [[Fraction(n,r["denominator"]) for n in r["numerators"]] for r in rows]


def keep_words(context, role):
    if len(context)==2:
        return [["0","1"]]*2
    return [[w for w in WORDS if sum(map(int,w))%2 == int(role=="B" and k==2)] for k in range(3)]


def fit(rows, alice, bob):
    """Fit all deterministic context responses, verifying every rational weight or separating inequality."""
    aw,bw = keep_words(alice,"A"),keep_words(bob,"B")
    settings = [(a,b) for a in range(len(aw)) for b in range(len(bw))]
    labels = [(a,b,x,y) for a,b in settings for x in aw[a] for y in bw[b]]
    numbers={x:i for i,x in enumerate(labels)}
    full = probability_table(rows)
    aorder,border=records(len(alice[0])), records(len(bob[0]))
    target=[full[a*len(bw)+b][aorder.index(x)*len(border)+border.index(y)] for a,b,x,y in labels]
    assert sum(target)==len(settings)
    strategies=list(product(*(aw+bw)))
    ncols=len(strategies)
    rowidx=[numbers[a,b,s[a],s[len(aw)+b]] for s in strategies for a,b in settings]
    colidx=np.repeat(np.arange(ncols),len(settings))
    matrix=sparse.csc_matrix((np.ones(len(rowidx)),(rowidx,colidx)),shape=(len(labels),ncols))
    target_float=np.fromiter(map(float,target),float)
    opt=linprog(np.zeros(ncols),A_eq=matrix,b_eq=target_float,bounds=(0,None),method="highs-ds")
    if opt.success:
        used=np.where(opt.x>1e-10)[0]
        vals=[Fraction(float(opt.x[i])).limit_denominator(10**7) for i in used]
        def verify(weights):
            result=[Fraction(0)]*len(labels)
            for i,w in zip(used,weights):
                s=strategies[i]
                for a,b in settings:
                    result[numbers[a,b,s[a],s[len(aw)+b]]]+=w
            return result
        if verify(vals)!=target:
            import sympy as sp
            selected=sp.Matrix(matrix[:,used].toarray().astype(int))
            exact,params=selected.gauss_jordan_solve(sp.Matrix([sp.Rational(q.numerator,q.denominator) for q in target]))
            assert not params.rows
            vals=[Fraction(int(x.p),int(x.q)) for x in exact]
        assert all(v>=0 for v in vals) and sum(vals)==1 and verify(vals)==target
        return dict(common=True,n_strategies=ncols,mixture=[[list(strategies[i]),str(v)] for i,v in zip(used,vals)],
                    verified_entries=len(full)*len(aorder)*len(border))
    assert opt.status==2
    constraints=sparse.hstack((matrix.T,-np.ones((ncols,1))),format="csr")
    alt=linprog(np.r_[-target_float,1.0],A_ub=constraints,b_ub=np.zeros(ncols),
                bounds=[(-1,1)]*len(labels)+[(None,None)],method="highs-ds")
    assert alt.success
    coeff=[Fraction(float(val)).limit_denominator(10000) for val in alt.x[:-1]]
    from math import lcm,gcd
    scale=lcm(*(q.denominator for q in coeff))
    vals=[int(q*scale) for q in coeff]
    d=gcd(*vals); vals=[v//d for v in vals]
    scores=[sum(vals[numbers[a,b,s[a],s[len(aw)+b]]] for a,b in settings) for s in strategies]
    observed=sum(v*p for v,p in zip(vals,target))
    assert observed>max(scores)
    return dict(common=False,n_strategies=ncols,coefficients=[[list(label),v] for label,v in zip(labels,vals) if v],
                bound=max(scores),observed=str(observed),verified_entries=len(rows)*len(aorder)*len(border))


def score(rows):
    q=probability_table(rows)
    matched=[sum(row[i*8+j] for i,x in enumerate(WORDS) for j,y in enumerate(WORDS) if x[col]==y[r])
             for (r,col),row in zip(product(range(3),repeat=2),q)]
    return str(sum(matched)/9)


def marginal_variation(rows, alice, bob):
    q=probability_table(rows); a,b=len(records(len(alice[0]))),len(records(len(bob[0])))
    rows=[[r[i*b:(i+1)*b] for i in range(a)] for r in q]
    out=[]
    for role in (0,1):
        ms=[[sum(x) for x in (r if role==0 else zip(*r))] for r in rows]
        far=len(bob) if role==0 else len(alice)
        cmp=[]
        for near in range(len(alice) if role==0 else len(bob)):
            get=lambda k: ms[near*len(bob)+k if role==0 else k*len(bob)+near]
            cmp.extend(sum(abs(u-v) for u,v in zip(get(i),get(j)))/2 for i,j in combinations(range(far),2))
        out.append(str(max(cmp,default=0)))
    return out


def inversion(vector, aq, bq, rows):
    # Walsh inversion uses product means, independently of the projector calculation.
    nrm=int(vector@vector)
    for r in rows:
        a,b=r["settings"]; ops=(*aq[a],*bq[b]); k=len(ops)
        means=[int(vector@action(times(*(op for j,op in enumerate(ops) if pick>>j & 1)),vector)) for pick in range(1<<k)]
        probs=[]
        for wa,wb in product(records(len(aq[a])),records(len(bq[b]))):
            word=sum(int(c)<<i for i,c in enumerate(wa+wb))
            probs.append(Fraction(sum((-1 if parity(word&i) else 1)*m for i,m in enumerate(means)),nrm*(1<<k)))
        assert probs==[Fraction(v,r["denominator"]) for v in r["numerators"]]
    return len(rows)*len(rows[0]["numerators"])
