"""Lawfulness, exact visible ends, and scalar sign checks on physical rows."""

from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
PRIOR = 'IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B'
sys.path.insert(0, str(ROOT / 'experiments' / PRIOR / f'{PRIOR}-E001_trees'))
from representatives import source_rows, shape_representatives
from representatives_audit import decoded, relabel
from representatives_growth import grow
from panels_certificates import scalar
from panels_sources import founder_check, width
from census_exact_rates import owners
from census_stages import end_of


LAWS = ('parity', 'nae')


def literal_founder(source):
    template = {'source_rows': source, 'before_permutation': source,
                'source_name_permutation': tuple(range(width(source))),
                'source_holder_order_to_original': tuple(range(len(source)))}
    return {law: founder_check(template, law) for law in LAWS}


def sufficient_projection(graph):
    evidence = []
    for fixed in sorted(graph):
        parts = []
        for c in nx.connected_components(graph.subgraph(set(graph) - {fixed})):
            private_holder = next((v for v in sorted(c) if graph.degree(v) <= 2), None)
            parts.append({'remaining_holders': tuple(sorted(c)), 'degree_based_private_holder': private_holder})
        evidence.append({'fixed_holder': fixed, 'remaining_components': parts})
    all_certified = all(p['degree_based_private_holder'] is not None for r in evidence for p in r['remaining_components'])
    return all_certified, evidence


def named_end(rows):
    owned = owners(rows)
    source = nx.Graph()
    source.add_nodes_from(range(len(rows)))
    source.add_edges_from(v for v in owned.values() if len(v) == 2)
    assert nx.is_connected(source)
    opens = defaultdict(list)
    for x, holds in owned.items():
        if len(holds) == 1:
            opens[holds[0]].append(x)
    seen = defaultdict(list)
    for w in range(len(rows)):
        for a, b in combinations(sorted(set(source[w]).intersection(opens)), 2):
            seen[a, b].append(w)
    visible = nx.Graph()
    visible.add_nodes_from(opens)
    visible.add_edges_from(seen)
    parts = tuple(sorted(tuple(sorted(p)) for p in nx.connected_components(visible)))
    other, raw = end_of(rows)
    assert {h: tuple(sorted(sp)) for h, sp in opens.items()} == {h: tuple(sorted(sp)) for h, sp in raw.items()}
    assert set(seen) == {p for w in other.blocks for p in combinations(w, 2)}
    return {'openings': tuple((h, tuple(sorted(z))) for h, z in sorted(opens.items())),
            'witnessed_pairs': tuple((a, b, tuple(seen[a, b])) for a, b in sorted(seen)),
            'effective_witness_subsets': other.blocks, 'live_components': parts, 'live_count': len(parts)}


def add_physical(case, law):
    record = case['laws'][law]
    all_rows = decoded(case['founder_rows'], record)
    ends = tuple(named_end(rows) for rows in all_rows)
    for age, cut in enumerate(record['cuts']):
        old, current = ends[age:age + 2]
        old_loose = {x for _, opens in old['openings'] for x in opens}
        new_loose = {x for _, opens in current['openings'] for x in opens}
        births = cut['births']
        assert old_loose == {x for b in births for x in b['inputs']}
        assert new_loose == {x for b in births for x in b['new_names']}
        zero = [b for b in births if not b['fresh']]
        assert bool(zero) == cut['whole_closed'] == (not new_loose)
        assert all((p['old_span_rows'] is not None) == (p['fresh'] == 0) for p in births)
        groups = tuple(p['parents'] for p in births if len(p['parents']) > 1)
        demand = Counter(x for g in groups for x in g)
        cut['multi_parent_groups'] = groups
        cut['initial_group_demand'] = tuple((h, demand[h]) for h, _ in old['openings'])
        cut['after_rows'] = all_rows[age + 1]
        cut['zero_grants'] = tuple(b['holder'] for b in zero)
        if zero:
            assert law == 'parity' and len(zero) == len(births) == 1
            terminal = record['terminal']
            assert terminal['holder'] == zero[0]['holder']
            assert set(terminal['inputs']) == old_loose
            before, after = all_rows[age:age + 2]
            reduce_old = Counter(x for row in before for x in row)
            assert set(terminal['support']) == {x for x, amount in reduce_old.items() if amount % 2}
            old_even = scalar(before, tuple(range(len(before))))
            assert old_even['words'] > 0 and old_even['words'] == terminal['all_even_scalar']['words']
            assert terminal['single_odd_scalar']['words'] == 0
            assert terminal['operator_positive'] == terminal['binary_pauli']['exists']
            terminal['old_even_scalar'] = old_even
            terminal['old_word_extensions'] = {'even_each': 1, 'odd_each': 0}
    record['end_by_age'] = ends
    record['first_separated_age'] = next((a for a, e in enumerate(ends) if e['live_count'] > 1), None)
    record['live_groups_at_four'] = ends[-1]['live_count'] if record['termination'] == 'open' and len(ends) == 5 else None
    return record


def incidence_for_end(end):
    graph = nx.Graph()
    for h, names in end['openings']:
        graph.add_node(h, colour=('holder', len(names)))
    # Negative node identifiers keep the incidence witness distinct from all
    # actual holders and keep isomorphism tie-breaking independent of hash seed.
    for i, block in enumerate(end['effective_witness_subsets'], start=1):
        key = -i
        graph.add_node(key, colour=('witness',))
        graph.add_edges_from((key, h) for h in block)
    return graph


def replay_equal_ends(record):
    ends = record['end_by_age']
    if record['termination'] != 'open' or record['live_groups_at_four'] != 1:
        return []
    found = []
    instances = tuple(map(incidence_for_end, ends))
    for a, b in combinations(range(len(ends)), 2):
        pair = nx.algorithms.isomorphism.GraphMatcher(instances[a], instances[b],
                  node_match=lambda p, q: p['colour'] == q['colour'])
        if pair.is_isomorphic():
            live_map = {x: y for x, y in pair.mapping.items() if x >= 0}
            by_open = {h: len(names) for h, names in ends[b]['openings']}
            assert all(len(names) == by_open[live_map[h]] for h, names in ends[a]['openings'])
            transported = {tuple(sorted(live_map[h] for h in block)) for block in ends[a]['effective_witness_subsets']}
            assert transported == set(ends[b]['effective_witness_subsets'])
            found.append({'ages': (a, b), 'holder_map': tuple(sorted(live_map.items())),
                          'effective_witness_subsets_earlier': ends[a]['effective_witness_subsets'],
                          'effective_witness_subsets_later': ends[b]['effective_witness_subsets']})
    return found


def fresh_sign_control(case):
    info = case['laws']['parity']
    boards = decoded(case['founder_rows'], info)
    for i, cut in enumerate(info['cuts']):
        for birth in cut['births']:
            if not birth['fresh']:
                continue
            before, after = boards[i:i + 2]
            toggled = birth['new_names'][0]
            assert owners(after)[toggled] == (birth['holder'],)
            a = scalar(before, tuple(range(len(before))))
            b = scalar(after, tuple(range(len(after))))
            c = scalar(after, tuple(range(len(after))), (birth['holder'],))
            extensions = 1 << sum(max(0, x['fresh'] - 1) for x in cut['births'])
            assert a['words'] > 0 and b['words'] == c['words'] == extensions * a['words']
            return {'id': case['id'], 'age': i + 1, 'founder_rows': case['founder_rows'], 'before_rows': before,
                    'after_rows': after, 'birth': birth, 'flip_fresh_name': toggled, 'older_even': a,
                    'new_all_even': b, 'new_child_odd': c, 'extensions_per_older_word_at_each_sign': extensions}
    return None
