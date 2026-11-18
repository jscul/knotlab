"""Recover the small-arity presentation from scalar thresholds in two mixed examples."""

from itertools import combinations

import networkx as nx

from targeted_countermodel import ROOT, adjoin, continuation


def read_junctions(distances):
    graph = nx.Graph()
    graph.add_edges_from(pair for pair, value in distances.items() if value <= 3)
    words3 = {
        frozenset((a, b, c))
        for a, b, c in combinations(graph, 3)
        if all(distances[tuple(sorted(pair))] == 2 for pair in ((a, b), (a, c), (b, c)))
    }
    for left, right in combinations(words3, 2):
        if left & right:
            graph.remove_edges_from((a, b) for a in left - right for b in right - left)
    return {frozenset(clique) for clique in nx.find_cliques(graph)}


def main():
    gluing = continuation.load(ROOT, *continuation.SOURCES[-1])
    examples = (
        (((0,), 3), ((0,), 2), ((0,), 2), ((1, 2), 2), ((1, 3), 2), ((2, 3), 2)),
        (((0,), 2), ((1,), 2), ((0, 2), 2), ((1, 3), 2), ((2, 4), 2), ((5,), 3)),
    )
    for recipe in examples:
        sites = ((0, 1, 2),)
        for parents, count in recipe:
            sites, _ = adjoin(gluing, sites, parents, count)
        gluing.replay(sites)
        width = max(bit for star in sites for bit in star) + 1
        table = gluing.scalar_table(continuation.cut_supports(gluing, sites), width)
        expected = {frozenset(star) for star in sites}
        assert read_junctions(table) == expected
        raw = nx.Graph()
        raw.add_edges_from(pair for pair, value in table.items() if value <= 3)
        assert {frozenset(group) for group in nx.find_cliques(raw)} != expected
        print(f"Recovered all {len(sites)} junctions at width {width}.")


if __name__ == "__main__":
    main()
