"""Independent small-graph checks of whole-span recovery, cut bases and finite bounds."""
from itertools import combinations
from pathlib import Path
import argparse
import json
import networkx as nx

def span(rows):
    words={0}
    for x in rows:
        words |= {x^y for y in words}
    return words

def check_graph(graph, double_edge):
    vertices=tuple(graph)
    edges=list(graph.edges)
    if double_edge is not None:
        edges.append(edges[double_edge])
    m=len(edges)
    stars=tuple(sum(1<<i for i,e in enumerate(edges) if v in e) for v in vertices)
    cut=span(stars)
    bonds=set()
    cuts=[]
    for mask in range(1,1<<(len(vertices)-1)):
        first={v for i,v in enumerate(vertices) if mask & (1<<i)}
        other=set(vertices)-first
        word=sum(1<<i for i,(a,b) in enumerate(edges) if (a in first)!=(b in first))
        cuts.append((first,word))
        if nx.is_connected(graph.subgraph(first)) and nx.is_connected(graph.subgraph(other)):
            bonds.add(word)
    assert bonds=={x for x in cut if x and not any(y!=x and y and y&x==y for y in cut)}
    k=[m+1]*(1<<m)
    for x in bonds:
        t=x
        while t:
            k[t]=min(k[t],x.bit_count())
            t=(t-1)&x
    assert {i for i,v in enumerate(k) if v==i.bit_count()} == bonds
    for root,rootstar in enumerate(stars):
        rows_live=[stars[v] for v in range(len(stars)) if v!=root and rootstar&stars[v]]
        shared_bonds=[x for x in range(1,1<<m) if x&rootstar==0 and k[x]==x.bit_count()]
        assert span([*shared_bonds,*rows_live])==cut
    mincuts=set()
    for u,v in combinations(vertices,2):
        options=[x for shore,x in cuts if (u in shore)!=(v in shore)]
        best=min(x.bit_count() for x in options)
        mincuts.update(x for x in options if x.bit_count()==best)
    for weight in {x.bit_count() for x in bonds}:
        selected=span(x for x in mincuts if x.bit_count()<=weight)
        assert all(x in selected for x in cut if x.bit_count()<=weight)
    first_orders={}
    for i,j in combinations(range(m),2):
        toggles=(1<<i)|(1<<j)
        def perm(x):
            active=x & toggles
            return x^toggles if active and active!=toggles else x
        # Membership for all words is independent of the oracle construction.
        mismatched=[x for x in cut if perm(x) not in cut]
        if not mismatched:
            continue
        b=min(x.bit_count() for x in mismatched)
        # One of the differing names must be marked, so compare two equal-length arrays.
        first=min(x.bit_count() for x in range(1,1<<m) if k[x]!=k[perm(x)])
        assert first<=b//2+3
        first_orders[first]=first_orders.get(first,0)+1
    return first_orders

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    totals={}
    checked=0
    rooted=0
    atlas=nx.graph_atlas_g()
    for graph in atlas:
        v=len(graph); e=graph.number_of_edges()
        if v<3 or v>6 or e>11 or not nx.is_biconnected(graph):
            continue
        for double in [None,*range(e)]:
            orders=check_graph(graph,double)
            checked+=1;rooted+=v
            for order,count in orders.items():
                totals[order]=totals.get(order,0)+count
    args.output.write_text(json.dumps(dict(max_vertices=6,max_simple_edges=11,
        graphs_and_single_doublings=checked,rooted_shared_only_recoveries=rooted,
        equation_changing_transpositions_by_first_order=totals),indent=2)+'\n')
if __name__=='__main__':
    main()
