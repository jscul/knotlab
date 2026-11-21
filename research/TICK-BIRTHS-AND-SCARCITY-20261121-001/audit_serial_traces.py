"""Check B262's archived serial payments using only recorded physical holdings.

No study implementation is imported here. We rebuild the live-parent candidates
from every actual sharing and reconstruct which parents a prior child took.
The guarded census is also checked against independent coefficient counts.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import json

import networkx as nx
from networkx.algorithms.isomorphism import DiGraphMatcher

from audit_serial_counts import SOURCES, coefficients, tick_parent

HERE = Path(__file__).resolve().parent
LEAF = HERE.name + "B"
ARCHIVE = HERE.parents[1] / "artifacts" / LEAF / (LEAF + "-E001_serial")


def sharing(holdings):
    owners = defaultdict(set)
    for knot, slots in enumerate(holdings):
        for slot in slots:
            owners[slot].add(knot)
    assert all(1 <= len(group) <= 2 for group in owners.values())
    neighbors = [set() for _ in holdings]
    loose = [set() for _ in holdings]
    for slot, group in owners.items():
        if len(group) == 1:
            loose[next(iter(group))].add(slot)
        else:
            a, b = group
            neighbors[a].add(b)
            neighbors[b].add(a)
    return owners, neighbors, loose


def raw_groups(neighbors, live):
    candidates = nx.Graph()
    for visible in neighbors:
        candidates.add_edges_from(combinations(visible & live, 2))
    large = [frozenset(g) for g in nx.find_cliques(candidates)
             if len(g) > 2 and not set.intersection(*(neighbors[p] for p in g))]
    covered = {frozenset(pair) for g in large for pair in combinations(g, 2)}
    return set(large) | {frozenset(pair) for pair in candidates.edges} - covered


def reproduce(holdings, original_count, step, priority, target=None):
    owners, neighbors, loose = sharing(holdings)
    live = {j for j, names in enumerate(loose) if names}
    groups = raw_groups(neighbors, live)
    # Adding a child consumes at most one distinction per older holder.
    # Larger IDs are later writes here, and originals have no input parents.
    children = [{j for j in n if j >= original_count and j > i}
                for i, n in enumerate(neighbors)]
    groups = {g for g in groups if not set.intersection(*(children[j] for j in g))}
    use = Counter(j for g in groups for j in g)
    unary = {frozenset([j]) for j in live if len(loose[j]) > use[j]}
    eligible = groups if priority == "joins_first" and groups else groups | unary
    parents = step['parents']
    assert frozenset(parents) in eligible
    assert step['child'] == len(holdings)
    if target is not None:
        assert step['target_admitted_before'] == (frozenset(target) in eligible)
        assert [set(v) for v in step['target_donor_slots_before']] == [loose[j] for j in target]
    assert len(eligible) == step.get('pool_size', len(eligible))
    assert [loose[j] for j in parents] == [set(v) for v in step['eligible_slots_at_parents']]
    used = step['consumed_slots']
    assert [owners[k] for k in used] == [{j} for j in parents]
    assert len(used) < sum(map(len, loose))
    interim = holdings + [used]
    _, touching, remaining = sharing(interim)
    current = {j for j, slots in enumerate(remaining) if slots} | {len(holdings)}
    demand = {g for g in raw_groups(touching, current) if len(holdings) in g}
    assert demand == {frozenset(g) for g in step['current_demand']}
    fresh = step['fresh']
    assert len(fresh) == max(1, 3-len(parents), len(demand))
    assert len(fresh) == len(set(fresh)) and not set(fresh).intersection(owners)
    if target is not None:
        assert [set(v) for v in step['target_donor_slots_after']] == [remaining[j] for j in target]
    return holdings + [used + fresh]


def ancestry_graph(births, source_size, root):
    graph = nx.DiGraph()
    pending = [root]
    while pending:
        current = pending.pop()
        if current in graph and 'role' in graph.nodes[current]:
            continue
        role = ('original',current) if current < source_size else ('written',current == root)
        graph.add_node(current,role=role)
        for parent in births.get(current, ()):
            graph.add_edge(parent,current)
            pending.append(parent)
    return graph


def check():
    raw = json.loads((ARCHIVE / 'raw.json').read_bytes())['sources']
    priced = json.loads((ARCHIVE / 'receipt.json').read_bytes())['laws']
    variants = [('alone','bare','bare'), ('same_continuation','attachment_3','same'),
                ('other_continuation','attachment_2','other'), (None,'supply_only','supply')]
    losses = steps = cuts = cold_orders = realized = 0
    for law, cases in priced.items():
        for raw_name, key, source_name in variants:
            c = cases[key]
            max_depth = max(map(int, c['depths']))
            births, opens = coefficients(SOURCES[source_name], max_depth + 1)
            for age, physical in c['depths'].items():
                n = int(age) + 1
                assert births[n] == physical['births']
                assert opens[n] == physical['loose']
                cuts += 1
            if raw_name is None:
                continue
            observed = raw[raw_name][law]
            source = c['source']
            assert source == observed['source']
            for age, warm in observed['warm'].items():
                prior = list(source)
                for depth in range(1, int(age)):
                    for birth in c['depths'][str(depth)]['events']:
                        assert birth['knot'] == len(prior)
                        prior.append(birth['consumed'] + birth['fresh'])
                target = warm['physical_target_parents']
                budget, shared = tick_parent(SOURCES[source_name], (int(age)-2)//4)
                for j in target:
                    parent = c['tick_windows'][age]['per_parent'][str(j)]
                    assert len(parent['initial_loose_slots']) == budget
                    assert len(parent['consumer_sibling_children']) == shared
                for priority, cases_at_tick in warm['policies'].items():
                    first = cases_at_tick['immediate_unique_firing']
                    assert first['parents'] == target
                    reproduce(prior,len(source),first,priority,target)
                    steps += 1
                    for arm in cases_at_tick.values():
                        if not isinstance(arm,dict) or arm.get('status') != 'permanent_loss':
                            continue
                        holdings = prior
                        for event in arm['trace']:
                            holdings = reproduce(holdings,len(source),event,priority,target)
                            steps += 1
                        _, neighbors, loose = sharing(holdings)
                        both = set.intersection(*(neighbors[j] for j in target))
                        certificate = arm['certificate']
                        later = sorted(ch for ch in both if ch >= len(prior))
                        assert later == certificate['earlier_children_using_both']
                        empty = [j for j in target if not loose[j]]
                        assert empty == certificate['exhausted_target_donors']
                        assert empty or later
                        losses += 1
            for priority, ordered in observed['cold'].items():
                for outcome in ordered.values():
                    holdings = list(source)
                    raw_parents = {}
                    for event in outcome['trace']:
                        holdings = reproduce(holdings,len(source),event,priority)
                        raw_parents[event['child']] = tuple(event['parents'])
                        steps += 1
                    ordinary = {b['knot']:b['parents'] for depth in range(1,7)
                                for b in c['depths'][str(depth)]['events']}
                    first_tick = c['tick_windows']['6']['tick']
                    required = ancestry_graph(ordinary,len(source),first_tick)
                    hits = []
                    for child in raw_parents:
                        actual = ancestry_graph(raw_parents,len(source),child)
                        if len(required) != len(actual):
                            continue
                        matcher = DiGraphMatcher(required,actual,
                                                 node_match=lambda a,b: a['role'] == b['role'])
                        if matcher.is_isomorphic():
                            hits.append(child)
                    assert hits == outcome['full_realizations']
                    cold_orders += 1
                    realized += bool(hits)
    print(f'{cuts} completed-cohort counts and budgets, {steps} raw steps across the '
          f'archived traces, {losses} irreversible-loss certificates reproduced.')
    print(f'Complete marked ancestry from the originals: {realized}/{cold_orders} '
          'named order-and-law cases.')


if __name__ == '__main__':
    check()

