"""The exact group of a complete named table, and its action on profiles."""

from functools import cache
from itertools import combinations, product
from math import factorial, prod

import networkx as nx

from explosive_stages import ROOT
from census_weighted import images, partitioned, points, refine


HALF = (1, 2)


def table_graph_data(key):
    width, groups, between = key
    blocks = []
    at = 0
    for size, _, _ in groups:
        blocks.append(tuple(range(at, at + size)))
        at += size
    assert at == width
    rates = [[None] * len(groups) for _ in groups]
    for (i, j), rate in zip(combinations(range(len(groups)), 2), between, strict=True):
        rates[i][j] = rates[j][i] = rate
    return tuple(blocks), tuple(tuple(s) for s in rates)


def quotient_match(cells, source, target, rates, colours):
    domains = []
    fixed = {source: target}
    for cell in cells:
        if len(cell) == 1:
            fixed[cell[0]] = cell[0]
            continue
        other = sum(1 << i for i in cell) & ~(1 << target)
        for i in cell:
            if i != source:
                choices = other & colours[target].get(rates[source][i], 0)
                if not choices:
                    return None
                domains.append((i, choices))

    def search(todo):
        if not todo:
            return {}
        at = min(range(len(todo)), key=lambda p: todo[p][1].bit_count())
        i, current = todo[at]
        for j in points(current):
            rest = [(h, allowed & colours[j].get(rates[i][h], 0) & ~(1 << j))
                    for h, allowed in (*todo[:at], *todo[at + 1:])]
            if all(allowed for _, allowed in rest):
                found = search(rest)
                if found is not None:
                    found[i] = j
                    return found
        return None

    found = search(domains)
    if found is not None:
        return tuple(i for _, i in sorted((fixed | found).items()))
    return None


@cache
def table_moves(key):
    """Return a generating family in canonical coordinates and its exact order."""
    width, signatures, _ = key
    blocks, rates = table_graph_data(key)
    order = prod(factorial(len(group)) for group in blocks)
    generators = []
    for block in blocks:
        for i, j in zip(block, block[1:]):
            move = list(range(width))
            move[i], move[j] = j, i
            generators.append(tuple(move))
    cells = refine(partitioned(range(len(blocks)), signatures.__getitem__), rates)
    colours = images(rates)
    while any(len(cell) > 1 for cell in cells):
        place = next(i for i, cell in enumerate(cells) if len(cell) > 1)
        source, *others = cells[place]
        orbit = 1
        for target in others:
            chosen = quotient_match(cells, source, target, rates, colours)
            if chosen is None:
                continue
            assert all(signatures[i] == signatures[j] for i, j in enumerate(chosen))
            assert all(rates[i][j] == rates[chosen[i]][chosen[j]] for i, j in combinations(range(len(blocks)), 2))
            move = list(range(width))
            for i, j in enumerate(chosen):
                for a, b in zip(blocks[i], blocks[j], strict=True):
                    move[a] = b
            orbit += 1
            generators.append(tuple(move))
        order *= orbit
        cells = refine((*cells[:place], (source,), tuple(others), *cells[place + 1:]), rates)
    return tuple(generators), order


def inverse(order):
    mapping = [None] * len(order)
    for new, old in enumerate(order):
        mapping[old] = new
    return tuple(mapping)


def rows_move(rows, perm):
    return tuple(sorted(tuple(sorted(perm[x] for x in row)) for row in rows))


def profile_move(profile, perm):
    """Transport every distinction in each current parent support."""
    return tuple(sorted((rows_move(parents, perm), f) for parents, f in profile))


def nonhalf_entries(key):
    blocks, rates = table_graph_data(key)
    for i, (_, numer, denom) in enumerate(key[1]):
        if (numer, denom) != HALF:
            for a, b in combinations(blocks[i], 2):
                yield a, b, (numer, denom)
        for j in range(i + 1, len(blocks)):
            if rates[i][j] != HALF:
                for a, b in product(blocks[i], blocks[j]):
                    yield a, b, rates[i][j]


def enriched_graph(key, profile):
    """An isomorphism uses one permutation for the table and the profile."""
    graph = nx.Graph()
    graph.add_nodes_from((('name', i), {'kind': ('name',)}) for i in range(key[0]))
    for a, b, rate in nonhalf_entries(key):
        node = ('pair', a, b)
        graph.add_node(node, kind=('pair_rate', rate))
        graph.add_edges_from((node, ('name', x)) for x in (a, b))
    for i, (parents, f) in enumerate(profile):
        child = ('child', i)
        graph.add_node(child, kind=('child', f))
        for parent in parents:
            holder = ('holder', *parent)
            if holder not in graph:
                graph.add_node(holder, kind=('holder',))
                graph.add_edges_from((holder, ('name', name)) for name in parent)
            graph.add_edge(child, holder)
    return graph


def profile_invariant(profile):
    return tuple(sorted((f, tuple(sorted(map(len, parents)))) for parents, f in profile))


def profile_match(key, left, right):
    if profile_invariant(left) != profile_invariant(right):
        return None
    graph_a = enriched_graph(key, left)
    graph_b = enriched_graph(key, right)
    match = nx.vf2pp_isomorphism(graph_a, graph_b, node_label='kind')
    if match is None:
        return None
    move = tuple(match['name', i][1] for i in range(key[0]))
    assert profile_move(left, move) == right
    return move
