"""Independent checks on parent lists. The empty list is the terminal rank."""
from itertools import combinations
import argparse
import json
import resource
import time

import networkx as nx


def sharing(parents):
    graph = nx.Graph()
    graph.add_nodes_from(range(len(parents)))
    for a, b in combinations(graph, 2):
        if parents[a] & parents[b]:
            graph.add_edge(a, b)
    return graph


def literal_step(parents):
    """Exhaustive definition, for small positive and negative controls."""
    graph = sharing(parents)
    large = []
    for size in range(len(parents), 2, -1):
        for members in combinations(graph, size):
            group = frozenset(members)
            if (all(graph.has_edge(i, j) for i, j in combinations(group, 2))
                    and not set.intersection(*(set(parents[i]) for i in group))
                    and not any(group <= other for other in large)):
                large.append(group)
    return large + [frozenset(pair) for pair in graph.edges
                    if not any(set(pair) <= group for group in large)]


def step(parents):
    graph = sharing(parents)
    groups = [frozenset(c) for c in nx.find_cliques(graph)
              if len(c) >= 3 and not set.intersection(*(set(parents[i]) for i in c))]
    covered = {tuple(sorted(pair)) for g in groups for pair in combinations(g, 2)}
    return groups + [frozenset((a, b)) for a, b in sorted(graph.edges)
                     if tuple(sorted((a, b))) not in covered]


def parity_certificate(parents):
    """Normalize pair marks along a spanning forest. Row-reduce the triple equations."""
    graph = sharing(parents)
    forest = nx.minimum_spanning_tree(graph)
    chords = [tuple(sorted(pair)) for pair in graph.edges if not forest.has_edge(*pair)]
    idx = {pair: i for i, pair in enumerate(chords)}
    basis = {}
    for a, b in graph.edges:
        if a > b:
            a, b = b, a
        for c in set(graph[a]) & set(graph[b]):
            if c <= b:
                continue
            row = sum(1 << idx[p] for p in ((a, b), (a, c), (b, c)) if p in idx)
            while row:
                lead = row.bit_length() - 1
                if lead not in basis:
                    basis[lead] = row
                    break
                row ^= basis[lead]
    dim = len(chords) - len(basis)
    if not dim:
        return {"independent_marks": 0}
    free = next(i for i in range(len(chords)) if i not in basis)
    sol = 1 << free
    for pivot, row in sorted(basis.items()):
        if (sol & row).bit_count() % 2:
            sol |= 1 << pivot
    marked = {p for i, p in enumerate(chords) if (sol >> i) & 1}
    for a, b, c in combinations(graph, 3):
        if graph.has_edge(a, b) and graph.has_edge(a, c) and graph.has_edge(b, c):
            assert sum(tuple(sorted(p)) in marked for p in combinations((a,b,c), 2)) % 2 == 0
    u, v = chords[free]
    walk = nx.shortest_path(forest, u, v) + [u]
    assert sum(tuple(sorted(p)) in marked for p in zip(walk, walk[1:])) % 2
    return {"independent_marks": dim, "marked_pairs": sorted(marked), "odd_closed_walk": walk}


def verify_transport(parents, certificate):
    """Transfer explicit pair marks and a closed walk for one rank."""
    graph = sharing(parents)
    children = step(parents)
    marked = {tuple(p) for p in certificate["marked_pairs"]}

    def bit(a, b):
        return int(tuple(sorted((a, b))) in marked)

    def potential(child, member):
        return bit(min(children[child]), member)

    new_marks = {}
    for first, second in combinations(range(len(children)), 2):
        common = children[first] & children[second]
        if common:
            values = {potential(first, v) ^ potential(second, v) for v in common}
            assert len(values) == 1
            new_marks[first, second] = values.pop()

    next_graph = nx.Graph()
    next_graph.add_edges_from(new_marks)
    for a, b in new_marks:
        for c in set(next_graph[a]) & set(next_graph[b]):
            if c > b:
                assert new_marks[a,b] ^ new_marks[a,c] ^ new_marks[b,c] == 0

    old_walk = certificate["odd_closed_walk"]
    lifted = []
    for u, v in zip(old_walk, old_walk[1:]):
        assert graph.has_edge(u, v)
        lifted.append(next(i for i, family in enumerate(children) if {u,v} <= family))
    total = 0
    for a, b in zip(lifted, lifted[1:]+lifted[:1]):
        if a != b:
            total ^= new_marks[tuple(sorted((a,b)))]
    assert total == 1
    return lifted


def controls(limit):
    out = {}
    for m in range(1, limit+1):
        # Repeated parent sets and several shared parents are intentional.
        par = [frozenset([31, 37]) for _ in range(m)]
        labels = [frozenset([i]) for i in range(m)]
        widths = []
        for k in range(1, m+1):
            nxt = step(par)
            if len(par) <= 10:
                assert set(literal_step(par)) == set(nxt)
            expected = {frozenset(c) for c in combinations(range(m), k+1)}
            mapped = [frozenset.union(*(labels[i] for i in family)) for family in nxt]
            assert set(mapped) == expected and len(nxt) == len(expected)
            for family, label in zip(nxt, mapped):
                assert {labels[i] for i in family} == {label-{i} for i in label}
            widths.append(len(nxt))
            labels, par = mapped, nxt
        assert sum(widths) == 2**m-m-1
        out[str(m)] = widths
    common = [frozenset([0]), frozenset([0]), frozenset([0])]
    separate = [frozenset([0, 1]), frozenset([1, 2]), frozenset([0, 2])]
    assert nx.is_isomorphic(sharing(common), sharing(separate))
    assert [len(step(common)),len(step(separate))] == [3,1]
    ring = [frozenset([i,(i+1)%5]) for i in range(5)]
    assert parity_certificate(common)["independent_marks"] == 0
    for _ in range(4):
        assert parity_certificate(ring)["independent_marks"] == 1
        ring = sorted(step(ring), key=sorted)
    return {"subset_following_widths":out,"equal_sharing_different_next":[3,1],
            "five_member_periodic_control":parity_certificate(ring)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("max_m", type=int)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30))
    started = time.monotonic()
    result = controls(args.max_m)
    result["seconds"] = time.monotonic()-started
    print(json.dumps(result, indent=2))
