"""Check a three-attachment witness with all current effective triples and literal growth."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import json
import sys
from unittest.mock import patch

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = 'LATER-BOND-READING-20261119-001'
sys.path.insert(0, str(ROOT / 'research' / OLD))
sys.path.insert(0, str(ROOT / 'experiments' / OLD / (OLD + '-E001_future')))
from boundary_linear import extend, fastlib, verify
from constructive_branch import attach_branches


def host(n, s, l, d, m):
    hot = list('abcd')
    inner_mids = hot + ['u'] + ['i'+str(i) for i in range(n)]
    inner_weak = ['x'+str(i) for i in range(n)]
    inner_anchors = ['v','w'] + inner_weak
    shield = ['p'+str(i) for i in range(2*s)]
    outer_anchors = ['y'+str(i) for i in range(n)]
    middle = inner_mids + shield
    anchors = inner_anchors + outer_anchors
    # Hub/anchor to middle, with two distinguishable weighted links at a shield.
    edges = []
    for mid in inner_mids:
        hub = 'h0' if mid in ('a','b') else 'h1'
        edges.append((hub, mid, l if mid in hot else (d if mid=='u' else 1)))
        for a in inner_anchors:
            weight = l if a=='v' and mid in hot else (d if a=='w' and mid in ('a','c','u') else 1)
            edges.append((a,mid,weight))
    for j, p in enumerate(shield):
        edges.append(('h0' if j<s else 'h1',p,m))
        edges.append(('O',p,m))
        edges.extend((a,p,1) for a in outer_anchors)
    edges.extend(('t',a,1) for a in anchors)
    return edges, middle, anchors, inner_weak, outer_anchors, shield


def template_check(edges, middle, anchors, inner_weak, outer_anchors, order):
    # Each tested class contributes at most one middle/anchor. Positive shore
    # is t, one untouched weak anchor in each block, and exactly the touched middles.
    folded = lambda u: 'z' if u in ('h0','h1','O') else u
    edge_degrees = Counter()
    for a,b,w in edges:
        edge_degrees[folded(a)] += w
        edge_degrees[folded(b)] += w
    base = (edge_degrees['t'] + edge_degrees[inner_weak[0]] + edge_degrees[outer_anchors[0]] - 4)
    mbit = {u:1<<j for j,u in enumerate(middle)}
    abit = {u:1<<j for j,u in enumerate(anchors)}
    ms = [mbit.get(b,0) for a,b,w in edges]
    aa = [abit.get(a,0) | abit.get(b,0) for a,b,w in edges]
    left = sum(abit[u] for u in inner_weak)
    right = sum(abit[u] for u in outer_anchors)
    costs = {}
    terms = [edge_degrees[u]-2 for u in middle]
    def middle_cost(mask):
        if mask not in costs:
            costs[mask] = base + sum(terms[j] for j in range(len(middle)) if mask >> j & 1)
        return costs[mask]
    tested, maxima, witnesses = {}, {}, {}
    for k in range(1,order+1):
        count = high = 0
        for selected in combinations(range(len(edges)),k):
            m = a = 0
            for j in selected:
                a |= aa[j]
                m |= ms[j]
            assert left & ~a and right & ~a
            bound = middle_cost(m)
            if bound > high:
                high, best = bound, selected
            count += 1
        tested[k], maxima[k] = count, high
        # Build the maximizing certificate independently and verify all crossings.
        touched = {u for j in best for u in edges[j][:2]}
        side = ({'t', next(u for u in inner_weak if u not in touched),
                 next(u for u in outer_anchors if u not in touched)} | (set(middle)&touched))
        graph = nx.Graph()
        for a,b,w in edges:
            graph.add_edge(folded(a),folded(b))
        assert nx.is_connected(graph.subgraph(side)) and nx.is_connected(graph.subgraph(set(graph)-side))
        assert all((folded(edges[j][0]) in side) != (edges[j][1] in side) for j in best)
        assert sum(w for a,b,w in edges if (folded(a) in side)!=(b in side)) == high
        witnesses[k] = [list(edges[j][:2]) for j in best]
    return dict(classes=len(edges),tested=tested,maximum_constructed_cost=maxima,
                marks_attaining_maximum=witnesses)


def build_physical(edges, shield, m):
    labels = sorted({u for a,b,w in edges for u in (a,b)}-{'O'})
    index = {u:i for i,u in enumerate(labels)}
    rows = [set() for u in labels]
    bundles = {}
    last = 0
    for a,b,w in edges:
        if a == 'O':
            continue
        bundle = range(last,last+w)
        rows[index[a]].update(bundle)
        rows[index[b]].update(bundle)
        bundles[a,b] = bundle
        last += w
    roots = [index[u] for u in shield]
    initial, branch_names = attach_branches(m,rows,roots)
    with patch.object(extend.C.F.Presentation,'groups_among',fastlib.groups_among):
        current = extend.grow1(initial)
        next_stage = extend.grow1(current)
    stages = [verify.Arrangement.parse([sorted(r) for r in phase])
              for phase in (initial,current,next_stage)]
    assert all(verify.start_audit(phase)['census_open_legal'] for phase in stages)
    records = [verify.round_replay(a,b) for a,b in zip(stages, stages[1:])]
    assert all(not item['implied'] for step in records for item in step)
    assert not (set(range(len(rows))) & set(stages[1].live))
    pi = {}
    for (a,b), ids in bundles.items():
        if b not in ('a','c'):
            continue
        other = 'c' if b=='a' else 'a'
        outer = ('h1' if a=='h0' else 'h0') if a in ('h0','h1') else a
        for x,y in zip(ids,bundles[outer,other],strict=True):
            pi[x] = y
    for phase in stages:
        assert all(pi.get(x,x)==x for j in phase.live for x in phase.stars[j])
        classes = {}
        for x,owners in phase.owners.items():
            classes.setdefault(tuple(owners),set()).add(x)
        bits = {frozenset(cl) for cl in classes.values()}
        assert {frozenset(pi.get(x,x) for x in cl) for cl in bits} == bits
    local_cuts = []
    for phase in stages[1:]:
        ends, _, outside = phase.holder_graph()
        graph = nx.Graph()
        for x,(a,b) in ends.items():
            if x<last: continue
            if graph.has_edge(a,b): graph[a][b]['capacity'] += 1
            else: graph.add_edge(a,b,capacity=1)
        graph_without_outside = graph.copy()
        graph_without_outside.remove_node(outside)
        minimum = []
        for pole in roots:
            component = nx.node_connected_component(graph_without_outside,pole)
            sub = graph.subgraph(component|{outside})
            minimum.append(int(nx.minimum_cut_value(sub,pole,outside)))
        local_cuts.append(sorted(set(minimum)))
    assert local_cuts == [[m],[1]]
    pairs = [list(bundles['h0','a'])[:2],list(bundles['h1','c'])[:2]]
    return dict(sizes=[[len(a.stars),len(a.labels)] for a in stages],
                local_branch_costs=local_cuts, all_stages_full_projection=True,
                end_pointwise_and_flip_classes_preserved=True, singleton_marks=[p[0] for p in pairs],
                parallel_old_pairs=pairs,
                nonparallel_old_pairs=[[bundles['h0','a'][0],bundles['h0','b'][0]],
                                       [bundles['h1','c'][0],bundles['h0','b'][0]]])


def singleton_values(edges, price):
    g = nx.Graph()
    for a,b,w in edges:
        g.add_edge(a,b,capacity=price if a=='O' else w)
    result = []
    for hub,mid in (('h0','a'),('h1','c')):
        cost,(x,y) = nx.minimum_cut(g,hub,mid)
        assert nx.is_connected(g.subgraph(x)) and nx.is_connected(g.subgraph(y))
        result.append(int(cost))
    return result


def run():
    n,s,m,r = 4,8,48,3
    d = l = s*(n+1)+1
    edges, mids, anchors, inner, outer, shields = host(n,s,l,d,m)
    core = template_check(edges,mids,anchors,inner,outer,r)
    assert max(core['maximum_constructed_cost'].values()) < s*m
    ages = [singleton_values(edges,j) for j in (m,1)]
    assert ages[0][0] == ages[0][1] and ages[1][0] < ages[1][1]
    literal = build_physical(edges,shields,m)
    return dict(parameters=dict(n=n,s=s,L=l,D=d,M=m), shared_junctions=['h0','h1','t'],
                folded_certificates=core, shielding_threshold=s*m,
                exact_singleton_K_current_next=ages, physical=literal,
                nonparallel_pair_next_upper_and_image_lower=[2*l+s*(n+1),4*l])


if __name__ == '__main__':
    report = json.dumps(run(),indent=2)+'\n'
    out = Path(__file__).with_suffix('.json')
    if sys.argv[1:]==['--check']:
        assert out.read_text()==report
    else:
        out.write_text(report)
