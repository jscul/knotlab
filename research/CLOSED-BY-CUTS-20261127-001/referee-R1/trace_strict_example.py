"""Look for the known strict box's 12 source laws as a subfamily of any census history."""
import argparse
from collections import Counter, defaultdict
from pathlib import Path
from time import perf_counter
import json

import networkx as nx

from growth_replay import LAWS, census_starts, holders, loose, stages

HERE = Path(__file__).resolve().parent
EXAMPLE = HERE.parents[1] / 'UPPER-GROWN-20261127-001/referee-R1/open_witness.json'


def meeting_graph(supports):
    g = nx.Graph()
    three = {i for i,k in enumerate(supports) if len(k)==3}
    g.add_nodes_from(three)
    for owners in holders(supports).values():
        if len(owners)==2 and three.issuperset(owners):
            a,b=owners
            old = g.get_edge_data(a,b,{}).get('count',0)
            g.add_edge(a,b,count=old+1)
    return g


def copies_possible(supports, target):
    if sum(len(k)==3 for k in supports) < len(target):
        return 0,False
    need_cycles = target.number_of_edges()-len(target)+1
    candidate = False
    for group in nx.connected_components(h:=meeting_graph(supports)):
        if len(group)<len(target):
            continue
        part = h.subgraph(group)
        if part.number_of_edges()-len(group)+1 < need_cycles:
            continue
        candidate = True
        matcher = nx.isomorphism.GraphMatcher(part,target,edge_match=lambda a,b:a['count']==b['count'])
        if matcher.subgraph_is_isomorphic():
            return 1,True
    return 0,candidate


def main(pilot):
    example=json.loads(EXAMPLE.read_text())
    target=meeting_graph(example['grown_supports'])
    assert (len(target),target.number_of_edges())==(12,17) and nx.is_connected(target)
    assert copies_possible(example['grown_supports'],target)[0]==1
    assert copies_possible(example['start'],target)[0]==0
    counts=defaultdict(Counter)
    matches=[]
    cache={}
    starts=census_starts()
    ids=range(0,len(starts),113) if pilot else range(len(starts))
    for i in ids:
        for law in LAWS:
            for turn,stage in stages(starts[i],law):
                if not turn or not loose(stage):
                    continue
                counts[law]['open stages after a funded round']+=1
                if stage not in cache:
                    cache[stage]=copies_possible(stage,target)
                found,candidate=cache[stage]
                counts[law]['pass width, connectedness and cycle-count filters']+=candidate
                counts[law]['contain a copy']+=found
                if found:
                    matches.append([law,i,turn])
    return dict(indexed_starts_per_law=len(ids),through_round=6,per_law=counts,
                positive_start_rounds=matches,contains_itself=True,contains_it_before_growth=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot',action='store_true')
    args=parser.parse_args()
    t=perf_counter()
    result=main(args.pilot)
    if not args.pilot:
        (HERE/'trace_strict_example.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['per_law'],round(perf_counter()-t,4))
