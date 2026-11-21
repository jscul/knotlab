"""Exact canonical comparison of complete tables of pair disagreement rates."""

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from math import factorial, gcd, prod

import networkx as nx


@dataclass(frozen=True)
class PairTable:
    key: tuple
    order: tuple
    automorphisms: int


def rate_matrix(width, total, disagreements):
    if total <= 0:
        raise ValueError('pair rates require a nonempty state set')
    rates = [[None] * width for _ in range(width)]
    for i, j in combinations(range(width), 2):
        count = disagreements[i, j]
        unit = gcd(count, total)
        rates[i][j] = rates[j][i] = (count // unit, total // unit)
    return rates


def twin_classes(rates):
    """A transposition within one class preserves the entire pair table."""
    universe = range(len(rates))
    by_profile = defaultdict(list)
    for i in universe:
        profile = tuple(sorted(rates[i][j] for j in universe if i != j))
        by_profile[profile].append(i)
    classes = []
    for nodes in by_profile.values():
        groups = []
        for i in nodes:
            for found in groups:
                j = found[0]
                if all(rates[i][k] == rates[j][k] for k in universe if k != i and k != j):
                    found.append(i)
                    break
            else:
                groups.append([i])
        classes.extend(groups)
    return tuple(tuple(g) for g in classes)


def quotient(rates):
    classes = twin_classes(rates)
    signatures = [(len(g), *(rates[g[0]][g[1]] if len(g) > 1 else (0, 0))) for g in classes]
    quotient_rates = [[rates[g[0]][h[0]] for h in classes] for g in classes]
    graph = nx.Graph()
    graph.add_nodes_from((i, {'kind': ('class', key)}) for i, key in enumerate(signatures))
    for i, (a, b) in enumerate(combinations(range(len(classes)), 2), start=len(classes)):
        graph.add_node(i, kind=('pair', quotient_rates[a][b]))
        graph.add_edges_from(((a, i), (b, i)))
    return classes, signatures, quotient_rates, graph


def partitioned(vertices, signature):
    groups = defaultdict(list)
    for v in vertices:
        groups[signature(v)].append(v)
    return tuple(tuple(members) for _, members in sorted(groups.items()))


def refine(cells, rates):
    while True:
        def signature(i):
            return tuple(tuple(sorted(rates[i][j] for j in cell if i != j)) for cell in cells)

        split = tuple(part for cell in cells for part in partitioned(cell, signature))
        if len(split) == len(cells):
            return split
        cells = split


def kind(graph, point):
    return graph.nodes[point]['kind']


def coloured_match(graph, source, target):
    """Return a colour-preserving automorphism sending source to target."""
    old = kind(graph, source)
    if old != kind(graph, target) or graph.degree(source) != graph.degree(target):
        return None
    marked = graph.copy()
    temporary = ('marked',)
    marked.nodes[source]['kind'] = temporary
    graph.nodes[target]['kind'] = temporary
    found = nx.vf2pp_isomorphism(marked, graph, node_label='kind')
    graph.nodes[target]['kind'] = old
    return found


def exact_search(initial, quotient_rates, signatures, graph):
    """Compare every inequivalent individualization of a refined class."""
    def visit(cells):
        cells = refine(cells, quotient_rates)
        split = next((i for i, group in enumerate(cells) if len(group) > 1), None)
        if split is None:
            order = tuple(group[0] for group in cells)
            code = (tuple(signatures[i] for i in order),
                    tuple(quotient_rates[a][b] for a, b in combinations(order, 2)))
            return code, order, 1

        colored = graph.copy()
        for i, group in enumerate(cells):
            for name in group:
                colored.nodes[name]['kind'] = ('partition', i)
        group = cells[split]
        unchecked = set(group)
        canonical = []
        order_of_stabilizer = None
        while unchecked:
            anchor = min(unchecked)
            unchecked.remove(anchor)
            orbit = {v for v in unchecked if coloured_match(colored, anchor, v) is not None}
            unchecked.difference_update(orbit)
            individualized = cells[:split] + ((anchor,), tuple(v for v in group if v != anchor)) + cells[split + 1:]
            code, ordering, aut = visit(individualized)
            canonical.append((code, ordering))
            total = (1 + len(orbit)) * aut
            if order_of_stabilizer is not None:
                assert total == order_of_stabilizer
            order_of_stabilizer = total
        code, ordering = min(canonical)
        return code, ordering, order_of_stabilizer

    return visit(initial)


def canonical_pair_table(width, total, disagreements):
    """Return exact tuple key, old names in canonical order, and automorphism count.

    Entry (size, numerator, denominator) in the first key sequence describes a
    class of interchangeable names. A singleton has the (0, 0) sentinel for
    its absent internal pair. Rate pairs between classes follow in pair order.
    """
    classes, signatures, weights, graph = quotient(rate_matrix(width, total, disagreements))
    cells = partitioned(range(len(classes)), signatures.__getitem__)
    code, order, automorphisms = exact_search(cells, weights, signatures, graph)
    return PairTable((width, *code), tuple(i for c in order for i in classes[c]),
                     automorphisms * prod(factorial(len(group)) for group in classes))


def point_group(graph, size, keep_generators=False):
    """Exact order of induced permutations on point vertices, with optional generators."""
    pinned = graph.copy()
    total = 1
    generators = []
    for source in range(size - 1):
        orbit = 1
        for target in range(source + 1, size):
            matching = coloured_match(pinned, source, target)
            if matching is not None:
                orbit += 1
                if keep_generators:
                    generators.append(tuple(matching[i] for i in range(size)))
        total *= orbit
        pinned.nodes[source]['kind'] = ('fixed', source)
    return total, generators


def pair_symmetries(width, total, disagreements):
    """Generators of the group preserving an original named complete table."""
    classes, _, _, graph = quotient(rate_matrix(width, total, disagreements))
    for group in classes:
        for a, b in zip(group, group[1:]):
            move = list(range(width))
            move[a], move[b] = b, a
            yield tuple(move)
    _, generators = point_group(graph, len(classes), keep_generators=True)
    for permutation in generators:
        move = list(range(width))
        for i, j in enumerate(permutation):
            for source, target in zip(classes[i], classes[j], strict=True):
                move[source] = target
        yield tuple(move)
