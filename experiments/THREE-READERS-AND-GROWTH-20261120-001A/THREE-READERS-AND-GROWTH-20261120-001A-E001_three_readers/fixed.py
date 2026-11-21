"""Isolated and embedded controls. Each probability is checked two ways."""
from fractions import Fraction as F
from itertools import combinations,product
import json
import os
import subprocess
import sys
from math import lcm
import numpy as np
from completions import ROOT,OUT,gram,literal,mask
from three import (basic,behavior,compress,expectation,full_certificate,literal_projectors,
                   margins,mermin,rot_mermin,rows_for,save,seq_prob,singleton,specs,strategy_matrix)


def physical(stars,marks,law):
    g=gram(stars,marks,law);f=literal(stars,marks,law)
    assert np.array_equal(g,f.T @ f)
    return g,f


def fix(c=0):
    return [[0,1,2],*[[i,3+2*i,4+2*i] for i in range(c)]]


def step2():
    result={}
    qs=singleton(3)
    for law in ("nae","parity"):
        items={}
        for c in range(4):
            stars=fix(c);g,f=physical(stars,[0,1,2],law)
            b=basic(g);assert b["rows"]==literal_projectors(f,qs)
            b.update(stars=stars,gram=g.tolist())
            items[c]=b
        g,f=physical(fix(),[0,1,2],law)
        sparse=[[("X",1),("Z",1),("X",2),("Z",2)],[("X",4),("Z",4)]]
        single=behavior(g,sparse);assert single["rows"]==literal_projectors(f,sparse)
        grouped=[dict(r,settings=[2*r["settings"][0]+r["settings"][1],r["settings"][2]]) for r in items[0]["rows"]]
        group=full_certificate(grouped,((4,4,4,4),(2,2)))
        gm={}
        for r in grouped:
            pp=seq_prob(r)
            for role,way in ((0,[sum(pp[t] for t in (w,w+4)) for w in range(4)]),(1,[sum(pp[j:j+4]) for j in (0,4)])):
                key=str([role,r["settings"][role]])
                row=list(map(str,way))
                assert key not in gm or gm[key]==row
                gm[key]=row
        diag=basic(np.diag(np.diag(g)))
        result[law]=dict(attachments=items,single_per_reader=single,joint_at_two_place_reader=dict(rows=grouped,common=group,margins=gm),
                         incoherent_diagonal=diag)
    save("lead.json",result)


def common_parity(rows,n,visible=None):
    if visible is None:visible=list(range(n))
    strategies=[]
    # Sample independent Z word in the even code and X instructions in {0, all ones}.
    for x in range(1<<n):
        if x.bit_count()&1:continue
        for p in (0,1):
            bits=sum(([p,x>>i&1] for i in visible),[])
            ident=sum(b<<(len(bits)-j-1) for j,b in enumerate(bits))
            strategies.append(ident)
    from collections import Counter
    hist=Counter(strategies);size=1<<n
    a,ss=strategy_matrix(tuple((2,2) for i in visible))
    target=sum((seq_prob(r) for r in rows),[])
    measured=a[:,list(hist)].dot(np.array(list(hist.values()),dtype=float)).astype(int)
    assert [F(int(t),size) for t in measured]==target
    return dict(local=True,lists=len(ss),mixture=[[i,str(F(w,size))] for i,w in sorted(hist.items())])


def hardy(rows,n):
    # Every deterministic distribution satisfies this direct union bound; check all lists.
    sizes=tuple((2,2) for i in range(n));a,ss=strategy_matrix(sizes)
    cs=[]
    for r in rows:
        s=r["settings"]; count=s.count(1)
        for x in range(1<<n):
            if count==0: val=int(x.bit_count()>=2)
            elif count==n:val=-int(x in (0,(1<<n)-1))
            elif count==n-1:
                i=s.index(0);rest=((1<<n)-1)^(1<<i)
                val=-int((x>>i)&1 and (x&rest) not in (0,rest))
            else:val=0
            cs.append(val)
    target=sum((seq_prob(r) for r in rows),[])
    bound=int(max(a.T.dot(np.array(cs))));value=sum(c*q for c,q in zip(cs,target))
    assert bound==0 and value==F(2,1<<n)
    return dict(local=False,lists=len(ss),inequality=[[i,v] for i,v in enumerate(cs) if v],bound=bound,value=str(value))


def check_canonical(stars,law):
    from growth import certify
    assert all(certify(stars,law))
    results=[]
    for n in sorted(set(map(len,stars))):
        names=[f"v{i}" for i in range(n)]
        clauses=[]
        for t in range(1<<n):
            banned= (t.bit_count()%2==1) if law=="parity" else t in (0,(1<<n)-1)
            if banned:clauses.append(" ".join(("~" if (t>>i)&1 else "")+b for i,b in enumerate(names)))
        args=[sys.executable,"-B","-m","knotlab","check","--cnf",";".join(clauses),"--loops",*names[:-1],"--contact",names[-1],"--json"]
        answer=json.loads(subprocess.check_output(args,cwd=ROOT,env={**os.environ,"PYTHONPATH":str(ROOT/"tools")}))
        assert answer["is_knot"];results.append(dict(arity=n,law=law,canonical=True))
    return results


def step3():
    out={}
    for n in (3,4,5):
        laws={}
        for law in ("nae","parity"):
            stars=[tuple(range(n))];g,f=physical(stars,list(range(n)),law)
            whole=behavior(g,singleton(n),certificate=False)
            assert whole["rows"]==literal_projectors(f,singleton(n))
            whole["rotated"]=str(rot_mermin(whole["rows"],n));whole["bound"]=1<<(n//2)
            whole["common"]=hardy(whole["rows"],n) if law=="nae" else common_parity(whole["rows"],n)
            trs=[]
            for marks in combinations(range(n),3):
                g,f=physical(stars,list(marks),law)
                b=basic(g);assert b["rows"]==literal_projectors(f,singleton(3))
                trs.append(dict(marks=marks,**b))
            laws[law]=dict(all_marks=whole,subsets=trs,projected_rules=check_canonical(stars,law))
        out[str(n)]=laws
    # Two allowed tuples plus one: the explicit conditional two-reader auxiliary, ordered [0,1,2,3].
    f=np.array([0,1,1,1],dtype=int)
    out["conditional_two_mark_control"]=basic(np.outer(f,f))
    save("widths.json",out)
