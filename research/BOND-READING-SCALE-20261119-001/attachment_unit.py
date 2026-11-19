"""Check three fixed unit boundary probes and the one-exterior-mark reduction."""
from itertools import combinations
from math import inf
from pathlib import Path
import json
import sys

import networkx as nx

TERMINALS = (0,1,2)
TIPS = ('q0','q1','q2')


def subsets(names, limit):
    return [frozenset(s) for k in range(1,limit+1) for s in combinations(names,k)]


def graphs(edges):
    g = nx.Graph()
    for name,u,v in edges:
        g.add_edge(u,v)
    vertices = list(g)
    for side_mask in range(1,1 << (len(vertices)-1)):
        left = {v for j,v in enumerate(vertices) if side_mask >> j & 1}
        right = set(vertices)-left
        cut = frozenset(name for name,u,v in edges if (u in left)!=(v in left))
        yield cut,list(nx.connected_components(g.subgraph(left))),list(nx.connected_components(g.subgraph(right)))


def readings(edges,k):
    table = {}
    for bond,left,right in graphs(edges):
        if len(left)==len(right)==1:
            for t in subsets(sorted(bond),min(k,len(bond))):
                table[t] = min(len(bond),table.get(t,inf))
    return table


def local(edges,k):
    costs = {}
    for cut,left,right in graphs(edges):
        if any(not (part & set(TERMINALS)) for part in left+right):
            continue
        sides = [set.union(*left),set.union(*right)]
        lone = [j for j,side in enumerate(sides) if len(side & set(TERMINALS))==1]
        if len(lone)!=1:
            continue
        i = next(iter(sides[lone[0]] & set(TERMINALS)))
        for subset in subsets(sorted(cut),min(k,len(cut))):
            for strict in ([False,True] if len(left)==len(right)==1 else [False]):
                key = (subset,i,strict)
                costs[key] = min(len(cut),costs.get(key,inf))
    return costs


def exterior(ports,interior):
    return [(name,t,p) for t,(name,p) in enumerate(zip(TIPS,ports))] + [
        ('y'+str(j),u,v) for j,(u,v) in enumerate(interior)]


def check(inner, current, future, p):
    old = readings(inner+current,p)
    new = readings(inner+future,p)
    h = local(inner,p)
    q = local(future,p)
    hmarks = [e[0] for e in inner]
    qmarks = [e[0] for e in future]
    mixed = absent = singles = split = 0
    for x in subsets(hmarks,p):
        assert old.get(x,inf)==new.get(x,inf)
        if len(x)==p: continue
        avec = [h.get((x,i,False),inf) for i in TERMINALS]
        bvec = [h.get((x,i,True),inf) for i in TERMINALS]
        clipped = [old.get(x|{TIPS[i]},inf)-1 for i in TERMINALS]
        assert clipped==[min(avec[i],*(bvec[j]+1 for j in TERMINALS if j!=i)) for i in TERMINALS]
        if len(x)<=p-2:
            assert bvec==[old.get(x|{TIPS[j] for j in TERMINALS if j!=i},inf)-2 for i in TERMINALS]
        for y in subsets(qmarks,p-len(x)):
            u = [q.get((y,i,True),inf) for i in TERMINALS]
            v = [q.get((y,i,False),inf) for i in TERMINALS]
            actual = new.get(x|y,inf)
            assert actual == min(min(a+b for a,b in zip(avec,u)),min(a+b for a,b in zip(bvec,v)))
            together = min(a+b for a,b in zip(clipped,u))
            if len(y)==1:
                singles += 1
                split += any(a<b for a,b in zip(v,u))
                predicted = together
            else:
                predicted = min(together,min(a+b for a,b in zip(bvec,v)))
            assert actual == predicted
            mixed += 1
            absent += actual==inf
    return (mixed,absent,singles,split)


def run():
    # Both arms allow parallel ordinary links and an interior with only one vertex.
    static_edges = [
        [(3,t) for t,m in enumerate((4,2,3)) for _ in range(m)],
        [(0,3),(0,3),(1,3),(1,4),(2,4),(2,3),(3,4),(0,1)],
        [(0,3),(0,4),(1,3),(1,4),(2,3),(2,4),(3,4),(3,4)]]
    pieces = [exterior((10,10,10),[]),
              exterior((10,11,11),[(10,11),(10,11)]),
              exterior((10,11,12),[(10,11),(11,12),(10,12),(11,12)]),
              exterior((10,11,12),[(10,13),(11,13),(12,13),(10,11)])]
    results = []
    for i,inner in enumerate(static_edges):
        h = [('x'+str(j),u,v) for j,(u,v) in enumerate(inner)]
        sums = [0]*4
        for old in pieces:
            for new in pieces:
                sums = [a+b for a,b in zip(sums,check(h,old,new,4))]
        results.append(dict(interior=i,current_future_pairs=16, mixed_queries=sums[0],
                            absent=sums[1], one_exterior_mark=sums[2],
                            one_exterior_mark_in_a_strictly_cheaper_relaxed_state=sums[3]))
    return dict(maximum_query_order=4,panels=results)


if __name__ == '__main__':
    data = json.dumps(run(),indent=2)+'\n'
    path = Path(__file__).with_suffix('.json')
    if sys.argv[1:]==['--check']:
        assert path.read_text()==data
    else:
        path.write_text(data)
