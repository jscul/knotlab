"""Exact six-bin transport for a marked not-all-equal triple and a constructive parity model."""
from fractions import Fraction as F
from itertools import combinations
from math import lcm
import networkx as nx
import numpy as np
from three import seq_prob,strategy_matrix

SIZES=((2,2),)*3


def index(x,z):
    vals=sum(([x>>i&1,z>>i&1] for i in range(3)),[])
    return sum(b<<(5-i) for i,b in enumerate(vals))


def check_mixture(rows,w):
    assert sum(w.values())==1 and min(w.values())>=0
    a,s=strategy_matrix(SIZES); counts=[F(0)]*a.shape[0]
    for j,weight in w.items():
        for r in a.indices[a.indptr[j]:a.indptr[j+1]]:counts[r]+=weight
    assert counts==sum((seq_prob(r) for r in rows),[])
    return dict(local=True,lists=len(s),mixture=[[j,str(v)] for j,v in sorted(w.items()) if v])


def parity_model(rows):
    px=seq_prob(rows[0]);pz=seq_prob(rows[-1])
    return check_mixture(rows,{index(x,z):a*b for x,a in enumerate(px) for z,b in enumerate(pz) if a and b})


def physical_inequality(rows,subset):
    size=len(subset);bits=sum(1<<i for i in subset);cs=[]
    for row in rows:
        s=row["settings"]
        for x in range(8):
            if sum(s)==0:q=int(not(x & bits))
            elif sum(s)==3:q=-(size-1)*int(x in (0,7))
            elif sum(s)==2 and s.index(0) in subset:
                k=s.index(0);other=7^(1<<k)
                q=int((x>>k)&1 and (x&other) in (0,other))
            else:q=0
            cs.append(q)
    a,lists=strategy_matrix(SIZES);bound=int(max(a.T.dot(cs)))
    target=sum((seq_prob(r) for r in rows),[])
    val=sum(c*t for c,t in zip(cs,target))
    assert bound==1 and val>1
    return dict(local=False,lists=len(lists),inequality=[[j,v] for j,v in enumerate(cs) if v],bound=bound,
                value=str(val),subset=list(subset))


def hall(rows):
    px=seq_prob(rows[0]);pz=seq_prob(rows[-1])
    assert pz[0]==pz[7]==0
    p=[pz[1<<i]+pz[7^(1<<i)] for i in range(3)]
    checks=[]
    for k in (2,3):
        for subset in combinations(range(3),k):
            mask=sum(1<<i for i in subset)
            val=sum(t for x,t in enumerate(px) if not x&mask)+sum(p[i]/2 for i in subset)
            checks.append((val,subset))
    worst,chosen=max(checks)
    if worst>1:cert=physical_inequality(rows,chosen)
    else:
        den=lcm(*(q.denominator for q in px),*((q/2).denominator for q in p))
        graph=nx.DiGraph()
        for x,w in enumerate(px):
            graph.add_edge("source",x,capacity=int(w*den))
            for i in range(3):
                graph.add_edge(x,(i,x>>i&1),capacity=den)
        for i,w in enumerate(p):
            for sign in (0,1): graph.add_edge((i,sign),"sink",capacity=int(w*den/2))
        value,flows=nx.maximum_flow(graph,"source","sink",flow_func=nx.algorithms.flow.edmonds_karp)
        assert value==den
        weights={}
        for x in range(8):
            for (i,_),v in flows[x].items():
                for z in ((1<<i),7^(1<<i)):
                    if v:weights[index(x,z)]=F(v,2*den)
        cert=check_mixture(rows,weights)
    cert["hall"]=[dict(subset=list(s),left=str(v),bound=1) for v,s in checks]
    return cert
