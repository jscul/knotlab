"""Independent size-six check using uncoloured sources and unreduced flag vectors."""

from collections import Counter
from fractions import Fraction
from functools import cache
from itertools import combinations, pairwise, product
from math import comb, factorial
from pathlib import Path
import sys

import networkx as nx
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
ORDINARY = 'ORDINARY-DYNAMICS-20261120-001A'
sys.path.insert(0, str(ROOT / 'experiments' / ORDINARY / (ORDINARY + '-E001_ordinary')))
from end_operator import End, neighbors, step


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


@cache
def connected_count(n, edges):
    """Count the connected labelled patterns by removing the component of label 0."""
    total = choose(comb(n, 2), edges)
    for size in range(1, n):
        outside = comb(n - size, 2)
        for internal in range(min(comb(size, 2), edges) + 1):
            total -= (comb(n - 1, size - 1) * connected_count(size, internal)
                      * choose(outside, edges - internal))
    return total


def count_trees(graph):
    n = len(graph)
    return sum(nx.is_connected(nx.Graph(subset)) and len(set().union(*map(set, subset))) == n
               for subset in combinations(graph.edges(), n - 1))


def check_projections(graph):
    for holder in graph:
        remainder = graph.subgraph(set(graph) - {holder})
        for part in nx.connected_components(remainder):
            assert any(graph.degree(v) <= 2 for v in part)


def initial_end(graph, flags):
    supply = {v: max(0, 3 - graph.degree(v)) + flags[v] for v in graph}
    live = {v: s for v, s in supply.items() if s}
    return End(live, tuple(set(graph[v]) & live.keys() for v in graph))


def live_groups(end):
    relation = neighbors(end)
    return nx.number_connected_components(nx.Graph(relation)) if relation else 0


def trajectory(end, law):
    for age in range(1, 5):
        turn = step(end, law)
        if turn.status == 'stall':
            assert age == 1
            return 'stall'
        assert turn.status == 'extend'
        if not turn.end.opens:
            assert all(f == 0 for f in turn.fresh) and law == 'parity'
            return 'closed ' + str(age)
        end = turn.end
        if live_groups(end) > 1:
            # Distinct groups cannot merge. The grant meets the next demand.
            return 'open separate'
    return 'open connected'


def closing_certificate():
    """Replay the actual last sign on the closing holding with real matrices."""
    graph = nx.Graph([(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (3, 4), (3, 5)])
    end = initial_end(graph, (0, 0, 0, 0, 1, 1))
    previous_ids = list(range(6))
    for size, grant in [(4, 8), (4, 7), (3, 3), (1, 0)]:
        turn = step(end, 'parity')
        assert len(turn.parents) == size and sum(turn.fresh) == grant
        first = len(graph)
        for j, group in enumerate(turn.parents):
            graph.add_edges_from((previous_ids[parent], first + j) for parent in group)
        previous_ids = list(range(first, first + size))
        end = turn.end
    assert not end.opens and nx.is_connected(graph)
    assert (len(graph), graph.size(), previous_ids) == (18, 31, [17])

    unit = np.eye(2, dtype=int)
    x = np.array([[0, 1], [1, 0]])
    z = np.diag([1, -1])
    j = np.array([[0, -1], [1, 0]])
    tensor = np.kron
    setting = [[tensor(x, unit), tensor(unit, x), tensor(x, x)],
               [tensor(unit, z), tensor(z, unit), tensor(z, z)],
               [tensor(x, z), tensor(z, x), -tensor(j, j)]]
    routes = [[(14, 13, 9, 5, 3, 4, 6, 10), (14, 12), (14, 17)],
              [(15, 10), (15, 11, 7, 12), (15, 17)],
              [(16, 10), (16, 12), (16, 17)]]
    identity = np.eye(4, dtype=int)
    assigned = {}
    for row, paths in enumerate(routes):
        for column, path in enumerate(paths):
            operator = setting[row][column]
            assert np.array_equal(operator, operator.T)
            assert np.array_equal(operator @ operator, identity)
            for a, b in pairwise(path):
                name = tuple(sorted((a, b)))
                assert graph.has_edge(a, b) and name not in assigned
                assigned[name] = operator
    for holder in graph:
        operators = [assigned.get(tuple(sorted((holder, other))), identity)
                     for other in graph[holder]]
        for a, b in combinations(operators, 2):
            assert np.array_equal(a @ b, b @ a)
        result = identity
        for operator in operators:
            result = result @ operator
        assert np.array_equal(result, -identity if holder == 17 else identity)
    print('All 18 operator products verified. Only the actual closing holder has negative sign.')


def main():
    totals = {'labelled': Counter(), 'tree_edits': Counter()}
    masses = {law: {weight: Counter() for weight in totals} for law in ('parity', 'nae')}
    graphs = [g for g in nx.graph_atlas_g() if len(g) == 6 and g.size() == 7 and nx.is_connected(g)]
    for graph in graphs:
        check_projections(graph)
        a = sum(1 for _ in nx.isomorphism.GraphMatcher(graph, graph).isomorphisms_iter())
        labelled = factorial(6) // a
        multiplicities = {'labelled': labelled, 'tree_edits': labelled * count_trees(graph)}
        for weighting, choices in multiplicities.items():
            totals[weighting]['ordinary_patterns'] += choices
        for flags in product((0, 1), repeat=6):
            flag_mass = 3 ** (6 - sum(flags))
            end = initial_end(graph, flags)
            for law in masses:
                fate = trajectory(end, law)
                for weighting, choices in multiplicities.items():
                    masses[law][weighting][fate] += choices * flag_mass
    u = connected_count(6, 7)
    expected = {'labelled': u, 'tree_edits': 6 ** 4 * comb(10, 2)}
    assert all(totals[w]['ordinary_patterns'] == n for w, n in expected.items())
    for law, weights in masses.items():
        for weight, counts in weights.items():
            den = expected[weight] * 4 ** 6
            assert sum(counts.values()) == den
            print(law, weight, 'denominator', den, sorted(counts.items()))
            print('funded', Fraction(den - counts['stall'], den))
    print('shapes', len(graphs), 'labelled patterns', u, 'tree edits', expected['tree_edits'])
    closing_certificate()


if __name__ == '__main__':
    main()
