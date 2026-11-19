"""Realize a first one-unit loss behind four named unit links with distinct terminals."""
import json
from pathlib import Path
import sys
import networkx as nx

from attachment_telescope import by_owners, extend, layout, verify, widths


def run():
    deck = layout((6,6),True,True)
    weights = widths(deck,set())
    values = []
    queries = [('ha','hu1','hu2'),('hc','hu1','hu2')]
    for price in (4,3):
        weights[deck.index['ou0']] = price
        costs = deck.cut_matrix @ weights
        values.append([int(costs[deck.marks(q)].min()) for q in queries])
    assert values==[[40,40],[39,40]]

    idx = {name:j for j,name in enumerate(deck.sites)}
    rows = [set() for _ in idx]
    pos = 0
    def new():
        rows.append(set())
        return len(rows)-1
    def edge(*holders):
        nonlocal pos
        for u in holders: rows[u].add(pos)
        pos += 1
        return pos-1
    names = {}
    for name,a,b in deck.edges:
        amount = 2 if name=='ou0' else int(weights[deck.index[name]])
        names[name] = [edge(idx[a],idx[b]) for _ in range(amount)]
    original = pos
    ends, tips, fixed = [],[],set(range(original))
    def unit_link(pole,child):
        p,r,u,v = (new() for _ in range(4))
        for a,b in ((pole,p),(p,u),(p,v),(r,u),(r,v),(u,v)):
            fixed.add(edge(a,b))
        ends.append(r)
        tips.append(edge(r,child))
    a,b,s,t,w = (new() for _ in range(5))
    unit_link(idx['u0'],a)
    unit_link(idx['u0'],b)
    for e in ((a,s),(a,t),(b,s),(b,w),(t,w)): edge(*e)
    for e in (s,s,t,w): edge(e)
    for _ in range(2):
        u,v,w = (new() for _ in range(3))
        unit_link(idx['o'],u)
        for e in ((u,v),(u,w),(v,w)): edge(*e)
        edge(v)
        edge(w)
    first = list(map(frozenset,rows))
    here = extend.grow1(first)
    later = extend.grow1(here)
    stages = [verify.Arrangement.parse([sorted(row) for row in phase]) for phase in (first,here,later)]
    fr = [verify.round_replay(prior,nxt) for prior,nxt in zip(stages,stages[1:])]
    assert all(not row['implied'] for rr in fr for row in rr)
    assert all(verify.start_audit(phase)['census_open_legal'] for phase in stages)
    pi = {x:y for a,b in deck.swapped.items() for x,y in zip(names[a],names[b],strict=True)}
    capacities = []
    for j,phase in enumerate(stages):
        owners,_,outside = phase.holder_graph()
        h = nx.Graph()
        q = nx.Graph()
        exterior = nx.Graph()
        for name,(a,b) in owners.items():
            (h if name in fixed else q).add_edge(a,b)
            if name>=original:
                if exterior.has_edge(a,b): exterior[a][b]['capacity'] += 1
                else: exterior.add_edge(a,b,capacity=1)
        assert set(h)&set(q)==set(ends)
        assert all(q.degree[u]==1 for u in ends)
        assert nx.is_connected(h) and nx.is_connected(q.subgraph(set(q)-set(ends)))
        assert all(u in q and u not in h for u in phase.live)
        assert all(pi.get(x,x)==x for u in phase.live for x in phase.stars[u])
        blocks = {frozenset(cls) for cls in by_owners(phase).values()}
        assert {frozenset(pi.get(x,x) for x in cls) for cls in blocks}==blocks
        if j:
            capacities.append(int(nx.minimum_cut_value(exterior,idx['u0'],idx['o'])))
    assert capacities==[2,1]
    return dict(four_distinct_unit_terminals=ends,four_unit_names=tips,variable_price=capacities,
                fixed_parallel_offset=2,full_price=[4,3],literal_triples=[[names[n][0] for n in q] for q in queries],
                current_next_K=values,sizes=[[len(a.stars),len(a.labels)] for a in stages],
                starting_and_later_projections=True,marks_outside_growing_end=True)


if __name__=='__main__':
    s=json.dumps(run(),indent=2)+'\n'
    path=Path(__file__).with_suffix('.json')
    if sys.argv[1:]==['--check']:
        assert path.read_text()==s
    else:
        path.write_text(s)
