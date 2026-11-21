"""Exhaust a small, deterministic family against the acyclic true-parent formulas."""
from argparse import ArgumentParser
from collections import Counter
from itertools import combinations, product
import json
from pathlib import Path

import networkx as nx

import built


def check():
    counts=Counter()
    cases=[]
    examples={}
    for n in range(2,6):
        for shape,tree in enumerate(nx.nonisomorphic_trees(n)):
            edges=sorted(tuple(sorted(row)) for row in tree.edges)
            for surplus in product((0,1),repeat=n):
                source=built.fixtures.source_from(edges,[max(0,3-tree.degree[k])+surplus[k] for k in range(n)])
                ordinary,loose=built.multis(source,'O')
                needs=Counter(k for group in ordinary for k in group)
                if any(needs[k]>len(bits) for k,bits in loose.items()):
                    counts['first_funding_veto']+=1
                    continue
                counts['funded_sources']+=1
                h=nx.Graph();h.add_nodes_from(loose);h.add_edges_from(ordinary)
                for r,s in combinations(sorted(loose),2):
                    route=nx.shortest_path(tree,r,s)
                    k=len(route)-1
                    d=k//2 if k%2==0 and all(t in loose for t in route[::2]) else None
                    assert d==(nx.shortest_path_length(h,r,s) if nx.has_path(h,r,s) else None)
                    for sender,receiver in ((r,s),(s,r)):
                        if d is None:
                            # Distinct parts remain disjoint by the actual complete-parent identities.
                            counts['distinct_parts_ordered']+=1
                            continue
                        assert d>0
                        spine=set(route[::2]);part=nx.node_connected_component(h,sender)
                        b=sum(len(loose[t])-needs[t] for t in spine)+len(set.union(*(set(h[t]) for t in spine))-spine)
                        if b==0:
                            assert part==spine
                        observed=built.paired_trace(source,built.extra(source,sender),'nae',receiver,sender,d+2)
                        assert all(v['terminal']==['extend','extend'] for v in observed)
                        assert next(v['stage'] for v in observed if any(v['both']))==d
                        assert next(v['stage'] for v in observed if any(v['unmatched']))==d+1
                        prices=[v['stage'] for v in observed if v['matched_changed_price']]
                        if b:
                            assert prices[0]==d
                        else:
                            assert not prices and all(v['matched_births']==0 for v in observed[d:])
                        tag='positive_boundary' if b else 'completed_path'
                        counts[tag]+=1
                        key=f'{tag}_d{d}'
                        examples.setdefault(key,{'n':n,'shape':shape,'edges':edges,'surplus':surplus,'sender':sender,'receiver':receiver,'d':d,'boundary':b,'trace':observed})
                if all(len(v)==3 for v in source):
                    counts['funded_ternary']+=1
                    assert all(len(nx.shortest_path(h,i,j))<=2 for comp in nx.connected_components(h) for i,j in combinations(comp,2))
                for rule in ('D','W'):
                    gs,ls=built.multis(source,rule)
                    charges=Counter(t for g in gs for t in g)
                    if len(ls)!=n or any(charges[p]>len(ls[p]) for p in ls):continue
                    g=nx.Graph();g.add_nodes_from(ls);g.add_edges_from(e for row in gs for e in combinations(row,2))
                    for r,s in combinations(range(n),2):
                        distance=nx.shortest_path_length(tree,r,s)
                        predicted=(distance+1)//2 if rule=='D' or n>2 else None
                        actual=nx.shortest_path_length(g,r,s) if nx.has_path(g,r,s) else None
                        assert actual==predicted
                        counts[f'{rule}_all_live_funded_pairs']+=1
    return {'bounds':'one of every unlabelled physical tree shape on 2..5 holders, each 0/1 surplus mask on its fixed numbering','counts':dict(counts),'examples':examples}


if __name__=='__main__':
    parser=ArgumentParser();parser.add_argument('--out',type=Path,default=built.ROOT/'artifacts'/built.HERE.parent.name/built.HERE.name/'tree_checks.json')
    args=parser.parse_args();result=check();args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['counts'])
