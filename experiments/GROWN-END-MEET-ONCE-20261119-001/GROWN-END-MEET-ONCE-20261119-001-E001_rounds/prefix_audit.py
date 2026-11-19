"""Audit a finite prefix via literal loose counts and all marked permutations."""
from collections import Counter
from itertools import product,combinations
import json
from pathlib import Path
import sys

import networkx as nx
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'proofs/GROWN-END-MEET-ONCE-20261119-001A/GROWN-END-MEET-ONCE-20261119-001A-P001_pointwise'))
from check import all_readings, independent, law

def mappings(labels, table, fixed):
    dom = {}
    for a in labels-fixed:
        def can_match(b):
            return all(table[tuple(sorted((a,f)))]==table[tuple(sorted((b,f)))] for f in fixed)
        dom[a]=set(b for b in labels-fixed if can_match(b))
    perm={x:x for x in fixed}
    def search():
        free=set(dom)-perm.keys()
        if not free:
            yield dict(perm)
            return
        choices={}
        for x in free:
            choices[x]=[y for y in dom[x]-set(perm.values()) if all(
                table[tuple(sorted((x,z)))]==table[tuple(sorted((y,t)))] for z,t in perm.items())]
        x=min(free,key=lambda z:(len(choices[z]),z))
        for y in choices[x]:
            perm[x]=y
            yield from search()
            del perm[x]
    yield from search()

def run(engine):
    cap=8
    totals={k:Counter() for k in range(4,cap+1)}
    for graph in nx.graph_atlas_g():
        n=len(graph)
        if n==0 or n>cap-3 or not nx.is_connected(graph):
            continue
        shared=[set() for _ in graph]
        for name,(a,b) in enumerate(sorted(graph.edges())):
            shared[a].add(name);shared[b].add(name)
        for multiplicity in product(range(cap-n+1),repeat=n):
            if not any(multiplicity) or any(len(s)+l<3 for s,l in zip(shared,multiplicity)):
                continue
            wired=graph.copy();wire=n
            wired.add_edges_from((u,wire) for u in graph if multiplicity[u])
            if any(v!=wire for v in nx.articulation_points(wired)):
                continue
            next_name=graph.number_of_edges()
            seed=[]
            for s,l in zip(shared,multiplicity):
                seed.append(sorted(s|set(range(next_name,next_name+l))))
                next_name+=l
            system=law.C.S.from_junctions(seed)
            candidates=system.groups_among([j for j in range(n) if multiplicity[j]],None)
            demand=Counter(i for group in candidates for i in group)
            if any(demand[j]>multiplicity[j] for j in range(n)):
                continue
            births=len(candidates)+sum(multiplicity)-sum(demand.values())
            if not 3<=births<=cap-n:
                continue
            step=system.step(law.C.S.gf2(law.C.F.fewest),None)
            assert step and step['new']==births
            rows=[sorted(s) for s in system.bits_of]
            current=independent.Arrangement.parse(rows)
            independent.round_replay(independent.Arrangement.parse(seed),current)
            stat=totals[len(rows)]
            stat['histories']+=1
            fixed=set().union(*(current.stars[j] for j in current.live))
            labels=set(current.labels)
            if len(labels-fixed)<=1:
                stat['identity_only_by_number_fixed']+=1
                continue
            _,table,_=all_readings(engine,rows)
            basis=independent.linear_basis(current.masks)
            after=None
            for phi in mappings(labels,table,fixed):
                if all(x==y for x,y in phi.items()):
                    continue
                stat['nonidentity_permutations']+=1
                if all(independent.reduce_word(sum(current.label_bits[phi[x]] for x in row),basis)==0 for row in current.stars):
                    stat['preserve_equations']+=1
                    continue
                if after is None:
                    step=system.step(law.C.S.gf2(law.C.F.fewest),None);assert step
                    successor=[sorted(row) for row in system.bits_of]
                    independent.round_replay(current,independent.Arrangement.parse(successor))
                    _,after,successor_owners=all_readings(engine,successor)
                lift={x:phi.get(x,x) for x in successor_owners}
                if all(after[tuple(sorted((lift[a],lift[b])))]==k for (a,b),k in after.items()):
                    stat['non_equation_extend_by_identity_on_new']+=1
                else:
                    fresh=set(successor_owners)-labels
                    domains={x:({phi[x]} if x in phi else fresh) for x in successor_owners}
                    assert independent.find_matching(after,after,domains,phi) is not None
                    stat['need_different_fresh_naming']+=1
    return totals

if __name__=='__main__':
    result=run(Path(sys.argv[1]))
    print(json.dumps(result,indent=2))
