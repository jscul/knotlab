"""Secondary tests of a minimal physical source and products that can emit again."""
from argparse import ArgumentParser
from collections import defaultdict
from functools import cache
from pathlib import Path
import json

import networkx as nx
from periodic import (A as NEUTRAL, P, ROOT, HERE, canonical, compact_source, contact,
                      meeting_source, windows)
from boundaries import law_gate, ownership, recode, source, stage_size, write_layer
from end_operator import from_stars, neighbors, step

OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "small_periodic.json"
A = (4,0,2,5)
B = (4,0,3,6)
SWAP = {2:3, 3:2, 5:6, 6:5}


def swapped(w):
    return tuple(SWAP.get(x,x) for x in w)


def rotate_factors(w, k):
    return {canonical(v) for v in windows(w, k)}


@cache
def definition(n):
    u = A*n+B
    v = A*(n+1)+B
    first, second = u*5+v, u*6+v
    # If two periodic walks agree through the product of their periods,
    # their whole walks agree. Find the exact maximum below that length.
    lo, hi = 0, 2*max(len(first),len(second))
    while rotate_factors(first, hi) & rotate_factors(second, hi):
        lo,hi=hi,hi*2
        assert hi<=2*len(first)*len(second)
    while hi-lo>1:
        k=(hi+lo)//2
        if rotate_factors(first,k) & rotate_factors(second,k):
            lo=k
        else:
            hi=k
    assert lo>=5*len(u)
    words=(first,second)
    banned=set().union(*(rotate_factors(w,hi)|rotate_factors(swapped(w),hi) for w in words))
    return words,hi,banned


def is_source(w):
    for n in range(2,len(w)//20+1,2):
        (_,k,banned)=definition(n)
        if k<=len(w) and any(canonical(w[i:i+k]) in banned for i in range(len(w)-k+1)):
            return False
    return True


def physical(law):
    links=[(0,1),(0,4),(1,4),(2,4),(2,6),(3,4),(3,5),(5,6),(0,1)]
    initial=source(7,links,(3,0,3,3,3,2,2))
    assert law_gate(initial,law,{})
    origin_graph=contact(initial)
    for q,row in initial.items():
        origin_graph.nodes[q]["arity"]=len(row)
    stars=initial
    results=[]
    for h in range(1,6):
        observations=[]
        for present in (stars,recode(stars,20261120750+h)[0]):
            snapshot=present.copy()
            while snapshot:
                graph=contact(snapshot)
                open_knots={p[0] for p in ownership(snapshot).values() if len(p)==1}
                if any(graph.has_edge(a,b) for a in open_knots for b in open_knots):
                    break
                snapshot={v:row for v,row in snapshot.items() if v not in open_knots}
            og=contact(snapshot)
            for q,row in snapshot.items():
                og.nodes[q]["arity"]=len(row)
            match=nx.algorithms.isomorphism.GraphMatcher(origin_graph,og,
                  edge_match=lambda a,b:a["weight"]==b["weight"],node_match=lambda a,b:a["arity"]==b["arity"])
            maps=list(match.isomorphisms_iter())
            assert len(maps)==2
            actual=contact(present)
            age=nx.multi_source_dijkstra_path_length(actual,set(snapshot),weight=None)
            by_parents=defaultdict(list)
            for x,a in age.items():
                if a:
                    ps=frozenset(p for p in actual[x] if age[p]+1==a)
                    by_parents[ps].append(x)
            marked=[]
            for mp in maps:
                @cache
                def find(w):
                    if len(w)==1:
                        return mp[w[0]]
                    ps=frozenset([find(w[:-1]),find(w[1:])])
                    assert len(ps)==2 and len(by_parents[ps])==1
                    return by_parents[ps][0]
                ws=definition(2)[0]
                seen={find(w) for word in ws for w in windows(word,h)}
                marked.append(len(seen))
            observations.append(marked)
        assert observations[0]==observations[1]
        results.append(dict(cluster_size=h,holdings=stage_size(stars),
                            distinct_physical_windows_by_arm=observations[0]))
        if h<5:
            stars=write_layer(stars,law)
    return results


def meeting(n):
    (a,b),k,_=definition(n)
    for w in (a,b):
        assert all(is_source(v) for v in windows(w,k-1))
        assert not any(is_source(v) for v in windows(w,k))
        for length in (k,k+1,k+2):
            parents=rotate_factors(w,length-1)
            assert all(canonical(v[1:]) in parents and canonical(v[:-1]) in parents
                       for v in rotate_factors(w,length))
    keys=rotate_factors(a,k-1) & rotate_factors(b,k-1)
    assert keys and not (rotate_factors(a,k)&rotate_factors(b,k))
    assert not (rotate_factors(a,k-1)&rotate_factors(swapped(b),k-1))
    # A concrete orphan-free mixed interval. Enumerate both orientations.
    right=defaultdict(set)
    for v in windows(b,k):
        for seq in (v,v[::-1]):
            right[seq[:-1]].add(seq[-1])
    mixed=set()
    for v in windows(a,k):
        for aseq in (v,v[::-1]):
            mixed.update(canonical(aseq+(last,)) for last in right[aseq[1:]])
    assert mixed and all(canonical(v[:-1])!=canonical(v[1:]) for v in mixed)
    return dict(n=n,periods=[len(a),len(b)],longest_common=k-1,release=k,
                pure_phases=[len(rotate_factors(w,k)) for w in (a,b)],shared_parents=len(keys),
                certified_straight_mixed_births=len(mixed),opposite_arm_shared_parents=0)


def nested(n,ell):
    u0,u1 = (NEUTRAL*n+P[j] for j in (0,1))
    s=len(u0)
    w=u0*ell+u1
    p=len(w)
    # These particular windows all belong to the two-choice language.
    assert all(meeting_source(v) for v in windows(w,2*s-1))
    assert not any(meeting_source(v) for v in windows(w,2*s))
    assert all(compact_source(v) for v in windows(w,2*p-1))
    assert not any(compact_source(v) for v in windows(w,2*p))
    assert len(rotate_factors(w,2*p))==p
    return dict(outer=n,inner=ell,outer_release=2*s,inner_release=2*p,inner_phases=p)


def main():
    ap=ArgumentParser()
    ap.add_argument("--out",type=Path,default=OUT)
    path=ap.parse_args().out
    record={"physical":{law:physical(law) for law in ("parity","nae")},
            "encounters":[meeting(n) for n in (2,4,6,8)],
            "nested":[nested(n,ell) for n in range(1,5) for ell in range(1,6)]}
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(record,indent=2)+"\n")


if __name__=="__main__":
    main()
