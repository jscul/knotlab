"""Exact scalar signs, old-span witnesses, and operator-admission certificates."""

from collections import defaultdict
from itertools import combinations, product
from math import prod

import networkx as nx

from panels_sources import rank


def mask(names):
    return sum(1 << x for x in names)


def points(bits):
    while bits:
        low = bits & -bits
        bits ^= low
        yield low.bit_length() - 1


def span_basis(rows):
    out = {}
    for holder, row in enumerate(rows):
        value = mask(row)
        provenance = 1 << holder
        while value:
            pos = value.bit_length() - 1
            if pos not in out:
                out[pos] = value, provenance
                break
            old, old_provenance = out[pos]
            value ^= old
            provenance ^= old_provenance
    return out


def older_span(basis, support):
    value = mask(support)
    found = 0
    while value:
        pos = value.bit_length() - 1
        if pos not in basis:
            return None
        row, origin = basis[pos]
        value ^= row
        found ^= origin
    return tuple(points(found))


def scalar(rows, holders, odd=()):
    selected = tuple(rows[h] for h in holders)
    used = {x for row in selected for x in row}
    coefficient = tuple(mask(row) for row in selected)
    sign_bit = 1 << (1 + max(used))
    base = rank(coefficient)
    augmented = rank(v | sign_bit if h in odd else v for h, v in zip(holders, coefficient, strict=True))
    return {'names': len(used), 'rank': base, 'augmented_rank': augmented,
            'words': (1 << (len(used) - base)) if base == augmented else 0}


def graph_of(rows, holders):
    held = defaultdict(list)
    for h in holders:
        for x in rows[h]:
            held[x].append(h)
    assert all(len(occupants) == 2 for occupants in held.values())
    graph = nx.Graph()
    graph.add_nodes_from(holders)
    physical = defaultdict(list)
    for name, occupants in held.items():
        pair = tuple(sorted(occupants))
        graph.add_edge(*pair)
        physical[pair].append(name)
    assert nx.is_connected(graph)
    return graph, physical


def positive_certificate(g, obstruction, physical):
    anchors = sorted(n for n, degree in obstruction.degree() if degree != 2)
    core = nx.Graph()
    core.add_nodes_from(anchors)
    groups = {i: [i] for i in anchors}
    paths = []
    interior = set()
    anchors_set = set(anchors)
    for start in anchors:
        for neighbor in obstruction[start]:
            path = [start, neighbor]
            while path[-1] not in anchors_set:
                before, current = path[-2:]
                following, = (i for i in obstruction[current] if i != before)
                assert following not in path
                path.append(following)
            end = path[-1]
            if start < end:
                assert not core.has_edge(start, end)
                core.add_edge(start, end)
                assert not interior.intersection(path[1:-1])
                interior.update(path[1:-1])
                groups[start].extend(path[1:-1])
                names = [min(physical[tuple(sorted((a, b)))]) for a, b in zip(path, path[1:])]
                paths.append({'holders': path, 'named_meetings': names})
    assert set(obstruction) == anchors_set | interior
    if len(anchors) == 5:
        assert all(core.has_edge(a, b) for a, b in combinations(anchors, 2))
        kind = 'five_all_pairs'
        parts = (anchors,)
    else:
        assert len(anchors) == 6 and nx.is_bipartite(core)
        a, b = nx.bipartite.sets(core)
        assert len(a) == len(b) == 3 and all(core.has_edge(i, j) for i, j in product(a, b))
        kind = 'six_three_against_three'
        parts = tuple(sorted((sorted(a), sorted(b))))
    assert len({x for group in groups.values() for x in group}) == sum(map(len, groups.values()))
    assert all(nx.is_connected(g.subgraph(v)) for v in groups.values())
    assert all(any(g.has_edge(x, y) for x, y in product(groups[a], groups[b])) for a, b in core.edges())
    return {'kind': kind, 'anchor_parts': parts, 'groups': sorted(groups.items()), 'paths': paths}


def closure_signs(rows, holders, last):
    graph, physical = graph_of(rows, holders)
    planar, record = nx.check_planarity(graph, counterexample=True)
    if planar:
        around = record.get_data()
        replay = nx.PlanarEmbedding()
        replay.set_data(around)
        replay.check_structure()
        assert all(set(around[h]) == set(graph[h]) for h in graph)
        used = set()
        faces = []
        for a, b in replay.edges():
            if (a, b) not in used:
                faces.append(replay.traverse_face(a, b, mark_half_edges=used))
        assert graph.number_of_nodes() - graph.number_of_edges() + len(faces) == 2
        certificate = {'kind': 'planar_rotation', 'rotation': sorted(around.items()), 'face_count': len(faces)}
    else:
        certificate = positive_certificate(graph, record, physical)
    even, odd = scalar(rows, holders), scalar(rows, holders, (last,))
    assert even['rank'] == len(holders) - 1 and even['words'] == (1 << (even['names'] - len(holders) + 1))
    assert odd['augmented_rank'] == even['rank'] + 1 and odd['words'] == 0
    return {'operator_positive': not planar, 'certificate': certificate, 'all_even_scalar': even,
            'single_odd_scalar': odd, 'simple_meetings': graph.number_of_edges(),
            'shared_names': len({x for v in physical.values() for x in v})}


def union_signs(rows, components, closed):
    """Apply only at physical cuts with at least one real terminal component."""
    ordered = sorted(closed, key=lambda event: min(event['component_holders']))
    closing = tuple(event['holder'] for event in ordered)
    complete = tuple(range(len(rows)))
    scenarios = []
    for signs in product((0, 1), repeat=len(closing)):
        odd = tuple(h for h, sign in zip(closing, signs, strict=True) if sign)
        by_component = []
        for component in components:
            holders = component['holders']
            flips = tuple(i for i in odd if i in holders)
            compatible = all(last['operator_positive'] for last in ordered if last['holder'] in flips)
            literal = scalar(rows, holders, flips)
            assert bool(literal['words']) == (not flips)
            by_component.append({'holders': holders, 'loose': component['loose'], 'operator_admits': compatible,
                                 'scalar_admits': bool(literal['words']), 'scalar': literal})
        union = scalar(rows, complete, odd)
        assert union['words'] == prod(c['scalar']['words'] for c in by_component)
        assert union['rank'] == sum(c['scalar']['rank'] for c in by_component)
        scenarios.append({'signs_by_closing_holder': signs, 'odd_holders': odd, 'components': by_component,
                          'scalar_admits': bool(union['words']), 'operator_admits': all(c['operator_admits'] for c in by_component),
                          'scalar': union})
    return {'ordered_terminal_holders': closing, 'scenarios': scenarios}
