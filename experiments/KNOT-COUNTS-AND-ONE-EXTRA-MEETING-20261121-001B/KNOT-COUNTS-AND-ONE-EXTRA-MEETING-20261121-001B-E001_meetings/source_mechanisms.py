"""Read witnesses directly from the founders and check all possible deletions of each ranked example."""

from collections import Counter
from itertools import combinations, permutations
import sys

import networkx as nx
from cycle_counts import ROOT


TREE = 'IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B'
sys.path.insert(0, str(ROOT/'experiments'/TREE/(TREE+'-E001_trees')))
from representatives_growth import grow
from panels_sources import from_meetings, founder_check
from panels_certificates import scalar


def components(points, adj):
    unseen = set(points)
    groups = []
    while unseen:
        queue = [min(unseen)]
        unseen.remove(queue[0])
        for u in queue:
            for v in sorted(adj[u] & unseen):
                unseen.remove(v)
                queue.append(v)
        groups.append(sorted(queue))
    return sorted(groups)


def initial_read(n, edges, flags, private=None):
    neighbors = [set() for _ in range(n)]
    for u, v in edges:
        neighbors[u].add(v)
        neighbors[v].add(u)
    if private is None:
        private = [max(0, 3 - len(adj)) + f for adj, f in zip(neighbors, flags, strict=True)]
    active = [i for i, count in enumerate(private) if count]
    witnesses = {(a, b): sorted(neighbors[a] & neighbors[b]) for a, b in combinations(active, 2)}
    witnesses = {pair: ws for pair, ws in witnesses.items() if ws}
    live_neighbors = {i: set() for i in active}
    for a, b in witnesses:
        live_neighbors[a].add(b)
        live_neighbors[b].add(a)
    maximal_unheld = []
    held_blocks = [adj & set(active) for adj in neighbors]
    for k in range(len(active), 2, -1):
        for subset in combinations(active, k):
            group = set(subset)
            if any(group <= z for z in held_blocks) or any(group <= set(z) for z in maximal_unheld):
                continue
            if all(pair in witnesses for pair in combinations(subset, 2)):
                maximal_unheld.append(subset)
    used = {p for group in maximal_unheld for p in combinations(group, 2)}
    proposals = sorted(maximal_unheld) + sorted(p for p in witnesses if p not in used)
    demand = Counter(i for group in proposals for i in group)
    shortage = {i: d - private[i] for i, d in demand.items() if d > private[i]}
    full = None if shortage else proposals + [(i,) for i in active for _ in range(private[i] - demand[i])]
    return {'private': list(private), 'live': active, 'live_components': components(active, live_neighbors),
            'witnessed_pairs': [{'pair': pair, 'witnesses': ws} for pair, ws in witnesses.items()],
            'unheld_maximal_groups': maximal_unheld, 'multi_parent_groups': proposals,
            'demand': [demand[i] for i in range(n)], 'shortages': shortage, 'funded_parents': full}


def canonical_names(n, edges, flags):
    best = None
    for names in permutations(range(n)):
        pairs = tuple(sorted(tuple(sorted((names[a], names[b]))) for a, b in edges))
        if best is not None and pairs > best[0]:
            continue
        deco = [0] * n
        for h, destination in enumerate(names):
            deco[destination] = flags[h]
        word = (pairs, tuple(deco))
        if best is None or word < best:
            best = word
    return best


def source_rank(row, code):
    x = row['laws']['parity']
    return (x['final_holders'], x['final_width'], row['n'], x['age'], x['terminal_arity'],
            len({v for holder in row['founder_rows'] for v in holder}), sum(row['extra']), code)


def named_phys(n, edges, flags, private):
    original = from_meetings(n,tuple((*e,1) for e in edges),private)
    count = len({x for row in original for x in row})
    draw = {'source_rows':original, 'source_name_permutation':list(range(count)), 'source_holder_order_to_original':list(range(n)), 'before_permutation':original}
    gates = {law:founder_check(draw,law) for law in ('parity','nae')}
    assert all(g['lawful'] and g['essential'] for g in gates.values())
    return {'source_rows':original,'gates':gates,'first_cut':initial_read(n, edges, flags, private),
            'laws':{law:grow(original,law) for law in ('parity','nae')}}


def deletion_classes(n, graph, flags):
    ring, = nx.cycle_basis(graph)
    possible = {tuple(sorted((a, b))) for a,b in zip(ring,ring[1:]+ring[:1],strict=True)}
    for i in range(n):
        graph.nodes[i]['extra'] = flags[i]
    eq = lambda a,b: a['extra'] == b['extra']
    group = tuple(nx.algorithms.isomorphism.GraphMatcher(graph,graph,node_match=eq).isomorphisms_iter())
    while possible:
        choice = min(possible)
        orbit = {tuple(sorted((p[choice[0]],p[choice[1]]))) for p in group}
        assert orbit <= possible
        possible -= orbit
        yield choice, sorted(orbit)


def positive_grant_control(witness):
    before = tuple(map(tuple,witness['founder']['source_rows']))
    cut = witness['founder']['laws']['parity']['cuts'][0]
    birth = next(b for b in cut['births'] if b['fresh'] > 0)
    after = before + tuple(tuple(b['support']) for b in cut['births'])
    h = birth['holder']
    f = birth['new_names'][0]
    assert [i for i, row in enumerate(after) if f in row] == [h]
    all_holders = tuple(range(len(after)))
    even = scalar(after,all_holders)
    odd = scalar(after,all_holders,(h,))
    old = scalar(before,tuple(range(len(before))))
    assert even['words'] == odd['words'] and even['words'] >= old['words'] > 0
    return {'age':1, 'parent_group':birth['parents'], 'fresh':birth['fresh'], 'flipped_only_holder':h,
            'flipped_only_name':f,'old_even':old,'all_even':even,'one_odd':odd,
            'example_even_ones':[], 'example_odd_ones':[f],
            'bijection_over_every_old_word':'flip this private name. No older holder or sibling contains it.'}


def named_witness(row):
    n = row['n']
    edges, flags = canonical_names(n,row['edges'],row['extra'])
    graph = nx.Graph(edges)
    private = [max(0, 3 - graph.degree(i)) + flags[i] for i in range(n)]
    founder = named_phys(n,edges,flags,private)
    expected = row['laws']['parity']
    got = founder['laws']['parity']
    for item in ('termination','age','terminal_arity','positive','final_width','final_holders'):
        assert got[item] == expected[item]
    controls = []
    for cut, orbit in deletion_classes(n,graph,flags):
        tree = tuple(e for e in edges if e != cut)
        degrees = Counter(x for e in tree for x in e)
        required = [max(0,3-degrees[i]) for i in range(n)]
        restored = [a+b for a,b in zip(required,flags,strict=True)]
        adjusted = [p-a for p,a in zip(private,required,strict=True)]
        erased = {'deleted':cut,'orbit':orbit,'fixed_flags':named_phys(n,tree,flags,restored),
                  'fixed_supply_flags':adjusted,'fixed_supply_arity_failures': [i for i in range(n) if private[i] + degrees[i] < 3]}
        if not erased['fixed_supply_arity_failures']:
            assert all(x in (0,1) for x in adjusted)
            erased['fixed_supply'] = named_phys(n,tree,adjusted,private)
        controls.append(erased)
    result = {'n':n, 'edges':edges,'flags':flags,'decorated_automorphisms':row['aut'],'founder':founder,'predecessors':controls}
    result['fresh_sign_control'] = positive_grant_control(result) if got['cuts'][0]['births'][0]['fresh'] else None
    return result
