"""Inspect the four observed ends. The proof checks do not grow any fifth cut."""
from collections import Counter
from itertools import combinations
import networkx as nx
from catalog import components_of, from_stars


def physical_ends(rows, law):
    current = tuple(map(tuple, rows))
    result = [from_stars(current)]
    for cut in law['cuts']:
        current += tuple(tuple(b['support']) for b in cut['births'])
        result.append(from_stars(current))
    assert len(result) <= 5
    return result


def describe(end):
    return {'loose_counts': sorted(end.opens.items()),'witness_subsets': end.blocks,
            'live_components': components_of(end)}


def witness_graph(end):
    graph = nx.Graph()
    for h,n in end.opens.items():
        graph.add_node(('point',h),label=('point',n))
    for i,block in enumerate(end.blocks):
        w = ('witness',i)
        graph.add_node(w,label=('witness',len(block)))
        for h in block:
            graph.add_edge(('point',h),w)
    return graph


def isomorphism(first, second):
    if sorted(first.opens.values()) != sorted(second.opens.values()):
        return None
    match = nx.algorithms.isomorphism.GraphMatcher(
            witness_graph(first),witness_graph(second),node_match=lambda a,b:a['label']==b['label'])
    ordered=tuple(sorted(first.opens))
    images=(tuple(p[('point',h)][1] for h in ordered) for p in match.isomorphisms_iter())
    selected=min(images,default=None)
    if selected is None:
        return None
    mapping=dict(zip(ordered,selected,strict=True))
    assert sorted(second.opens) == sorted(mapping.values())
    assert all(first.opens[a] == second.opens[b] for a,b in mapping.items())
    transformed = {tuple(sorted(mapping[h] for h in block)) for block in first.blocks}
    assert transformed == set(second.blocks)
    return sorted(mapping.items())


def uniform_path(end):
    if len(end.opens)<3 or set(end.opens.values())!={2} or any(len(b)!=2 for b in end.blocks):
        return False
    graph = nx.Graph(end.blocks)
    return set(graph)==set(end.opens) and nx.is_tree(graph) and max(dict(graph.degree()).values())==2


def survivor_certificate(case, canonical_law, prior_end):
    ends = physical_ends(case['founder_rows'],canonical_law)
    assert len(ends)==5 and len(components_of(ends[-1]))==1
    base = {'source_rows':case['founder_rows'],'ends':list(map(describe,ends)),
            'paid_parents_and_fresh':[[[b['parents'],b['fresh']] for b in cut['births']] for cut in canonical_law['cuts']]}
    for a,b in combinations(range(5),2):
        mapping=isomorphism(ends[a],ends[b])
        if mapping is not None:
            return base | {'fate':'recurrent_end','from_age':a,'to_age':b,'live_knot_map':mapping}
    if all(map(uniform_path,ends)):
        lengths=[len(end.opens) for end in ends]
        assert lengths==list(range(lengths[0],lengths[0]+5))
        return base | {'fate':'growing_two_opening_path','witnessed_path_sizes':lengths}
    mapping = isomorphism(ends[-1],prior_end)
    if mapping is not None:
        return base | {'fate':'later_closure_implied_by_observed_end','matched_next_birth':'known funded ternary with zero fresh',
                       'fourth_to_observed_closer_third':mapping,'later_operator_test':'not observed'}
    return base | {'fate':'later_fate_unresolved'}
