"""Canonical atlas representatives of six holders with seven simple meetings."""

from collections import Counter
from hashlib import sha256
from itertools import combinations, permutations
from math import comb, factorial
from tempfile import NamedTemporaryFile
import gzip
import json
import os

import networkx as nx

from physical_checks import (LAWS, OUT, add_physical, fresh_sign_control, grow, literal_founder, owners,
                             relabel, replay_equal_ends, shape_representatives, source_rows,
                             sufficient_projection, width)


N = 6
HOLDER_NAMES = tuple(range(N))


def canonical_graph(graph):
    edges = min(tuple(sorted(tuple(sorted((q[a], q[b]))) for a, b in graph.edges()))
                for q in permutations(HOLDER_NAMES))
    return nx.Graph(edges), edges


def uncoloured():
    kept = [g for g in nx.graph_atlas_g() if len(g) == N and g.number_of_edges() == 7 and nx.is_connected(g)]
    return sorted(map(canonical_graph, kept), key=lambda t: t[1])


def spanning_trees(edges):
    count = 0
    for subset in combinations(edges, N - 1):
        graph = nx.Graph()
        graph.add_nodes_from(HOLDER_NAMES)
        graph.add_edges_from(subset)
        if nx.is_tree(graph):
            count += 1
    return count


def decorated(graph, edges, tau):
    group = tuple(tuple(g[h] for h in HOLDER_NAMES)
                  for g in nx.algorithms.isomorphism.GraphMatcher(graph, graph).isomorphisms_iter())
    for case in shape_representatives(N, graph):
        original = case['extra']
        # The inverse action gives the same orbit and avoids a second sort of pairs.
        flags = min(tuple(original[h] for h in g) for g in group)
        case['extra'] = flags
        case['id'] = f'{edges}:{"".join(map(str, flags))}'
        case['founder_rows'] = source_rows(N, edges, flags)
        case['tau'] = tau
        case['mass_distinct'] = case['mass']
        case['mass_edited'] = tau * case['mass']
        assert case['edges'] == edges and sum(original) == sum(flags)
        allocation = owners(case['founder_rows'])
        assert tuple(sorted(v for v in allocation.values() if len(v) == 2)) == edges
        for h, support in enumerate(case['founder_rows']):
            assert len(support) >= 3
            assert sum(len(allocation[x]) == 1 for x in support) == max(0, 3 - graph.degree(h)) + flags[h]
        yield case


def ineligible(case):
    return {'termination': 'ineligible', 'age': 0, 'cuts': [], 'stall': None, 'terminal_arity': None,
            'positive': None, 'terminal': None, 'final_width': width(case['founder_rows']),
            'final_holders': len(case['founder_rows']), 'live_groups_at_four': None, 'would_cross_b251': False}


def actual_replays(case, can_extend):
    rows = case['founder_rows']
    literal = None if can_extend else literal_founder(rows)
    case['eligible'] = {law: can_extend or (literal[law]['lawful'] and literal[law]['essential']) for law in LAWS}
    case['laws'] = {law: grow(rows, law) if case['eligible'][law] else ineligible(case) for law in LAWS}
    for law in LAWS:
        if case['eligible'][law]:
            add_physical(case, law)
    # Apply the literal founder projector on every initially funded class. It
    # covers all actual terminal classes, regardless of their eventual rank.
    if literal is not None or any(case['laws'][law]['age'] > 0 for law in LAWS):
        literal = literal or literal_founder(rows)
        assert case['eligible'] == {law: literal[law]['lawful'] and literal[law]['essential'] for law in LAWS}
        case['literal_founder_gate'] = literal


def census(emit):
    initial_by_shape = []
    labelled_by_k = Counter()
    histories_by_k = Counter()
    closing_classes = []
    funded_classes = []
    connected_after_four = []
    terminal_cells = {}
    general = Counter()
    fate = Counter()
    distinct = Counter()
    edited = Counter()
    max_size = {l: [0, 0] for l in LAWS}
    fresh_control = None
    number_labelled = 0
    previous_tree_histories = 0
    for graph, edges in uncoloured():
        tau = spanning_trees(edges)
        can_extend, projection = sufficient_projection(graph)
        size_summary = {'edges': edges, 'tau': tau, 'degree_based_projection_certified': can_extend,
                        'projection_checks': projection}
        general['shapes'] += 1
        general['shapes_with_projection_premise'] += can_extend
        by_shape = Counter()
        uncoloured_weight = None
        for case in decorated(graph, edges, tau):
            uncoloured_weight = factorial(N) // case['uncoloured_aut']
            flag_count = sum(case['extra'])
            by_shape[flag_count] += case['labelled']
            labelled_by_k[flag_count] += case['labelled']
            histories_by_k[flag_count] += tau * case['labelled']
            actual_replays(case, can_extend)
            general['decorated_classes'] += 1
            general['literal_founder_gates'] += 'literal_founder_gate' in case
            if any(r['age'] for r in case['laws'].values()):
                funded_classes.append(case)
            for law, r in case['laws'].items():
                max_size[law][0] = max(max_size[law][0], r['final_holders'])
                max_size[law][1] = max(max_size[law][1], r['final_width'])
                cell = (law, r['termination'], r['age'], r['terminal_arity'], r['positive'])
                fate[cell] += 1
                distinct[cell] += case['mass_distinct']
                edited[cell] += case['mass_edited']
                general[f'{law}_cuts'] += r['age']
                general[f'{law}_births'] += sum(len(c['births']) for c in r['cuts'])
                if r['terminal']:
                    general['incidence_and_named_pauli_agreement'] += 1
                    closing_classes.append({'id': case['id'], 'law': law, 'founder': case['founder_rows'],
                                            'terminal': r['terminal'], 'mass_distinct': case['mass_distinct'],
                                            'mass_edited': case['mass_edited']})
                    terminal_cells.setdefault(cell, case)
                if r['live_groups_at_four'] == 1:
                    connected_after_four.append({'id': case['id'], 'law': law, 'edges': edges, 'extra': case['extra'],
                                                 'first_split_age': r['first_separated_age'], 'tau': tau,
                                                 'mass_distinct': case['mass_distinct'], 'mass_edited': case['mass_edited'],
                                                 'equal_ends_proved_by_isomorphism': replay_equal_ends(r)})
            if fresh_control is None:
                fresh_control = fresh_sign_control(case)
            emit(case)
        assert by_shape == {k: uncoloured_weight * comb(N, k) for k in range(N + 1)}
        number_labelled += uncoloured_weight
        previous_tree_histories += uncoloured_weight * tau
        initial_by_shape.append(size_summary | {'labelled_undecorated': uncoloured_weight, 'labelled_by_flags': by_shape})

    assert previous_tree_histories == N ** (N - 2) * comb(10, 2)
    assert labelled_by_k == {k: number_labelled * comb(N, k) for k in range(N + 1)}
    assert histories_by_k == {k: previous_tree_histories * comb(N, k) for k in range(N + 1)}
    for law in LAWS:
        assert sum(x for k, x in distinct.items() if k[0] == law) == number_labelled * 4 ** N
        assert sum(x for k, x in edited.items() if k[0] == law) == previous_tree_histories * 4 ** N
    for case in terminal_cells.values():
        assert case in funded_classes
    print('population complete', general, dict(fate), max_size, flush=True)
    controls = [relabel(case, law) for case in funded_classes for law in LAWS if case['eligible'][law]]
    return {'shapes': initial_by_shape, 'labelled_holdings': number_labelled,
            'labelled_tree_and_edit_origins': previous_tree_histories, 'labelled_by_k': labelled_by_k,
            'origins_by_k': histories_by_k, 'distinct_denominator': number_labelled * 4 ** N,
            'edited_denominator': previous_tree_histories * 4 ** N, 'general': general, 'max_size_by_law': max_size,
            'outcomes': [{'key': key, 'classes': fate[key], 'mass_distinct': distinct[key], 'mass_edited': edited[key]}
                         for key in sorted(fate, key=repr)], 'closing_classes': closing_classes,
            'connected_open_at_four': connected_after_four, 'positive_fresh_sign_control': fresh_control,
            'reversal_named_replays': controls}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / 'physical_population.json.gz'
    with NamedTemporaryFile(dir=OUT, prefix='.physical_population.', delete=False) as scratch:
        try:
            with gzip.GzipFile(filename='', fileobj=scratch, mode='wb', mtime=0) as stream:
                stream.write(b'[\n')
                already = False

                def emit(row):
                    nonlocal already
                    if already:
                        stream.write(b',\n')
                    already = True
                    stream.write(json.dumps(row, sort_keys=True, separators=(',', ':')).encode())

                audit = census(emit)
                stream.write(b'\n]\n')
            scratch.flush()
            os.replace(scratch.name, final)
        finally:
            if os.path.exists(scratch.name):
                os.unlink(scratch.name)
    audit['physical_population_sha256'] = sha256(final.read_bytes()).hexdigest()
    (OUT / 'physical_audit.json').write_text(json.dumps(audit, sort_keys=True, separators=(',', ':')) + '\n')
    print('complete', final.name, 'relabels', len(audit['reversal_named_replays']),
          'connected at fourth', len(audit['connected_open_at_four']), flush=True)


if __name__ == '__main__':
    main()
