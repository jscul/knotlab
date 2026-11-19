"""Check cyclic persistence, component survival and lawful higher-dimensional closing controls."""

import argparse
from collections import Counter
from itertools import combinations, product
import json
from pathlib import Path


def candidate_graph(points, blocks):
    graph = {v:set() for v in points}
    for block in blocks:
        for a, b in combinations(sorted(block), 2):
            graph[a].add(b)
            graph[b].add(a)
    return graph


def initial(raw):
    degrees = Counter(v for edge in raw["edges"] for v in edge)
    opens = {i:strength - degrees[i] for i,strength in enumerate(raw["sizes"]) if strength > degrees[i]}
    neighbors = [set() for _ in raw["sizes"]]
    for a,b in raw["edges"]:
        neighbors[a].add(b)
        neighbors[b].add(a)
    return opens, [set(opens) & block for block in neighbors]


def groups(points, blocks):
    graph = candidate_graph(points, blocks)
    edges = [(u,v) for u in graph for v in graph[u] if u < v]
    large = []
    # All checked controls and age-zero arrangements have few live names.
    for k in range(3, len(graph)+1):
        for subset in combinations(sorted(graph), k):
            s = set(subset)
            if any(not s-{v} <= graph[v] for v in s):
                continue
            if any(s <= b for b in blocks) or any(s <= graph[t] for t in graph.keys()-s):
                continue
            large.append(s)
    return large + [set((u,v)) for u,v in edges if not any(u in s and v in s for s in large)]


def reached(opens, blocks):
    children = groups(opens, blocks)
    demand = Counter(u for s in children for u in s)
    shortage = {u:demand[u]-s for u,s in opens.items() if demand[u] > s}
    if shortage:
        return None, shortage
    for u, s in opens.items():
        children.extend([{u}] * (s-demand[u]))
    return children, {}


def from_children(children):
    old = sorted(set().union(*children)) if children else []
    blocks = [{i for i,group in enumerate(children) if u in group} for u in old]
    return list(range(len(children))), blocks


def step(opens, blocks):
    children,shortage=reached(opens,blocks)
    assert not shortage
    vertices,new_blocks=from_children(children)
    next_groups=groups(vertices,new_blocks)
    demand=Counter(x for s in next_groups for x in s)
    fresh = {i:(demand[i] if len(children)==1 else max(demand[i],3-len(parents),1))
             for i,parents in enumerate(children)}
    return children,fresh,new_blocks


def hub_source(n, held, opens):
    links = [(v,n+i) for i,s in enumerate(held) for v in s]
    sizes = [opens[v]+sum(v in s for s in held) for v in range(n)]
    sizes.extend(len(block) for block in held)
    raw = dict(edges=links,sizes=sizes)
    counts,recovered = initial(raw)
    assert counts == opens
    assert set(map(frozenset,filter(None,recovered))) == set(map(frozenset,held))
    incidence={v:set() for v in range(len(sizes))}
    for u,v in links:
        incidence[u].add(v)
        incidence[v].add(u)
    seen={0}
    while True:
        expanded=seen.union(*(incidence[u] for u in seen))
        if expanded==seen:
            break
        seen=expanded
    assert len(seen)==len(sizes) and min(sizes)>=3 and len(set(links))==len(links)
    return raw


def closing_partnered(n):
    transversals=[]
    held=[]
    for choices in product((0,1),repeat=n):
        s={2*i+x for i,x in enumerate(choices)}
        transversals.append(s)
        if sum(choices[:3])%2:
            held.append(s)
    opens={v:2**(n-2) for v in range(2*n)}
    raw=hub_source(2*n,held,opens)
    source_graph=candidate_graph(opens,held)
    assert all(source_graph[v]==set(opens)-{v,v^1} for v in opens)
    children,fresh,blocks=step(opens,held)
    assert set(map(frozenset,children))==set(map(frozenset,transversals))-set(map(frozenset,held))
    assert all(a&b for a,b in combinations(children,2))
    assert set.intersection(*children)==set() and set(fresh.values())=={1}
    final,fresh2,_=step(fresh,blocks)
    assert final==[set(fresh)] and fresh2=={0:0}
    rims=Counter(face for s in transversals for face in combinations(sorted(s),n-1))
    assert set(rims.values())=={2}
    return dict(n=n,physical_knots=len(raw['sizes']),physical_shared_distinctions=len(raw['edges']),
                physical_loose_distinctions=sum(opens.values()),source_flag_dimension=n-1,
                top_cycle_facets=len(transversals),held_transversals=len(held),
                births=[len(children),len(final)],fresh_per_birth=[1,0])


def five_cycle():
    q={i:2 for i in range(5)}
    blocks=[{i,(i+1)%5} for i in range(5)]
    records=[]
    for _ in range(5):
        graph=candidate_graph(q,blocks)
        assert len(graph)==5 and set(map(len,graph.values()))=={2}
        assert not any(graph[u]&graph[v] for u in graph for v in graph[u])
        children,q,blocks=step(q,blocks)
        assert len(children)==5 and all(len(row)==2 for row in children) and set(q.values())=={2}
        records.append(len(children))
    return records


def other_controls():
    # Three pair blocks have a held-complex loop, while their flag is full and the only birth closes.
    child,loose,_=step({i:1 for i in range(3)},[{0,1},{1,2},{0,2}])
    assert child == [{0,1,2}] and loose == {0:0}
    # Two separated live holders each exhaust their local loose supply. Both births stay live.
    children,opens,blocks=step({0:1,1:1},[])
    assert children == [{0},{1}] and opens == {0:2,1:2}
    second,supply,next_blocks=step(opens,blocks)
    graph=candidate_graph(supply,next_blocks)
    assert len(second)==4 and set(supply.values())=={2} and set(map(len,graph.values()))=={1}
    return dict(held_three_cycle_final_fresh=0,two_isolated_successive_births=[len(children),len(second)])


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("output",type=Path)
    args=ap.parse_args()
    result=dict(closing_partnered_candidates=[closing_partnered(n) for n in (3,4,5)],
                nonpartnered_five_cycle=five_cycle(), other=other_controls())
    with args.output.open("x") as out:
        json.dump(result,out,indent=2)
        out.write("\n")
    print(json.dumps(result,separators=(",",":")))


