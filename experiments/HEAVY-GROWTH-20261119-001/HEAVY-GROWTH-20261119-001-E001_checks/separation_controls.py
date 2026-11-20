"""Exact controls for distance transfer and loss in funded pure growth."""

import itertools
import json
import tempfile
from collections import Counter
from pathlib import Path

import networkx as nx

from separation_screen import Roster, diameter


def maximal_blocks(family):
    out = []
    for block in sorted(set(map(frozenset, family)), key=lambda b: (-len(b), sorted(b))):
        if len(block) >= 2 and not any(block <= other for other in out):
            out.append(block)
    return tuple(out)


def candidate_graph(n, blocks):
    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    for block in blocks:
        graph.add_edges_from(itertools.combinations(block, 2))
    return graph


def groups(n, blocks):
    graph = candidate_graph(n, blocks)
    big = [frozenset(clique) for clique in nx.find_cliques(graph)
           if len(clique) >= 3 and not any(set(clique) <= block for block in blocks)]
    covered = {tuple(sorted(edge)) for clique in big for edge in itertools.combinations(clique, 2)}
    remaining = [frozenset(pair) for pair in graph.edges if tuple(sorted(pair)) not in covered]
    return tuple(sorted(big + remaining, key=lambda support: sorted(support)))


def after(parents, n):
    return maximal_blocks([i for i, support in enumerate(parents) if v in support] for v in range(n))


def replay_distance(n, blocks, parents):
    old = dict(nx.all_pairs_shortest_path_length(candidate_graph(n, blocks)))
    new = dict(nx.all_pairs_shortest_path_length(candidate_graph(len(parents), after(parents, n))))
    total = 0
    for i, j in itertools.combinations(range(len(parents)), 2):
        expected = 1 + min(old[a][b] for a in parents[i] for b in parents[j])
        if new[i][j] != expected:
            raise AssertionError((i, j, expected, new[i][j]))
        total += 1
    return total


def pure_history(n, blocks, ages, file):
    record = []
    checks = 0
    for age in range(ages):
        graph = candidate_graph(n, blocks)
        blocks_text = "".join(" ".join(map(str, sorted(block))) + "\n" for block in blocks)
        file.write_text(f"{n} {len(blocks)}\n" + blocks_text)
        expected_diameter = nx.diameter(graph)
        read = diameter(Roster(file))
        if expected_diameter != read["diameter"]:
            raise AssertionError((expected_diameter, read))
        if expected_diameter:
            a, b = read["antipodes"]
            if nx.shortest_path_length(graph, a, b) != expected_diameter:
                raise AssertionError("literal diameter witness failed")
        parents = groups(n, blocks)
        supply = Counter(v for group in parents for v in group)
        if len(supply) != n or any(not value for value in supply.values()):
            raise AssertionError("control must be funded and pure")
        terminal = len(parents) == 1 and parents[0] == frozenset(range(n))
        if not terminal:
            checks += replay_distance(n, blocks, parents)
        record.append({"age": age, "live": n, "diameter": expected_diameter, "births": len(parents),
                       "terminal_birth": terminal,
                       "six_pair_cycle": n == 6 and all(len(block) == 2 for block in blocks)
                       and nx.is_isomorphic(graph, nx.cycle_graph(6))})
        if terminal:
            break
        n, blocks = len(parents), after(parents, n)
    return {"history": record, "distance_formula_checks": checks}


def bag_roster(count, cycle=False):
    junctions = 0
    bags = []
    for i in range(count):
        if i == 0:
            bag = [0, 1, 2, 3]
            junctions = 4
        elif cycle and i == count - 1:
            bag = [junctions - 1, 0, junctions, junctions + 1]
            junctions += 2
        else:
            bag = [junctions - 1, junctions, junctions + 1, junctions + 2]
            junctions += 3
        bags.append(frozenset(bag))
    blocks = maximal_blocks(pair for bag in bags for pair in itertools.combinations(bag, 2))
    return junctions, blocks, bags


def matched_collective_controls(file):
    tests = {}
    for label, cyclic in (("finite", False), ("periodic", True)):
        n, blocks, bags = bag_roster(6, cyclic)
        pair = bags[0], bags[3] if cyclic else bags[-1]
        graph = candidate_graph(n, blocks)
        if pair[0] & pair[1] or any(graph.has_edge(a, b) for a in pair[0] for b in pair[1]):
            raise AssertionError("the two collective supports should be away from one another")
        if not all(group in groups(n, blocks) for group in pair):
            raise AssertionError("each support must be a legal maximal group")
        report = pure_history(n, blocks, 8, file)
        report["separated_supports"] = [sorted(group) for group in pair]
        tests[label] = report
    if not tests["finite"]["history"][-1]["terminal_birth"]:
        raise AssertionError("bounded chain failed to close")
    periodic = tests["periodic"]["history"][1:]
    if not all(row["six_pair_cycle"] and row["births"] == 6 and not row["terminal_birth"] for row in periodic):
        raise AssertionError("expected the six-group repeated support")
    return tests


def reach_by_incidence(n, target_blocks):
    """Build a funded predecessor of each marked roster in the collision."""
    parents_of = tuple(frozenset(j for j, block in enumerate(target_blocks) if v in block) for v in range(n))
    old_size = len(target_blocks)
    graph = nx.Graph()
    graph.add_nodes_from(range(old_size))
    graph.add_edges_from(
        (a, b) for a, b in itertools.combinations(range(old_size), 2) if target_blocks[a] & target_blocks[b]
    )
    held = [frozenset(clique) for clique in nx.find_cliques(graph) if frozenset(clique) not in parents_of]
    blocks = maximal_blocks(held + [frozenset(pair) for pair in graph.edges])
    next_parents = groups(old_size, blocks)
    if set(parents_of) != set(next_parents) or any(len(p) < 2 for p in next_parents):
        raise AssertionError((parents_of, next_parents))
    demand = Counter(v for child in next_parents for v in child)
    if set(after(parents_of, old_size)) != set(target_blocks):
        raise AssertionError("actual child incidence does not recreate target blocks")
    return {"live": old_size, "loose": [demand[v] for v in range(old_size)],
            "blocks": [sorted(block) for block in blocks],
            "parents_in_target_order": [sorted(parents) for parents in parents_of]}


def pure_collision():
    first = frozenset((0, 1, 2, 3))
    second = frozenset((0, 4, 5, 6))
    pairs = [frozenset(pair) for bag in (first, second) for pair in itertools.combinations(bag, 2)]
    a = maximal_blocks(pairs)
    b = maximal_blocks(pairs + [frozenset((1, 2, 3))])
    if sorted(map(len, a)) == sorted(map(len, b)):
        raise AssertionError("the two states must differ even up to relabeling")
    direct_groups = groups(7, a)
    if set(direct_groups) != {first, second} or direct_groups != groups(7, b):
        raise AssertionError("states did not have the same funded successor support")
    loose = Counter(v for child in direct_groups for v in child)
    next_blocks = after(direct_groups, 7)
    next_loose = Counter(v for group in groups(len(direct_groups), next_blocks) for v in group)
    receipt = {"same_live_supply": [loose[v] for v in range(7)],
               "same_next_parents": [sorted(group) for group in direct_groups],
               "same_next_blocks": [sorted(block) for block in next_blocks],
               "same_next_loose": [next_loose[v] for v in range(len(direct_groups))]}
    for label, target in (("pairs", a), ("one_triple", b)):
        receipt[label] = {"reached_blocks": [sorted(block) for block in target],
                          "predecessor": reach_by_incidence(7, target)}
    return receipt


def partnered_width_control():
    n = 12
    blocks = maximal_blocks((a, b) for a, b in itertools.combinations(range(n), 2)
                            if a // 6 == b // 6 and a // 2 != b // 2)
    sizes = [n]
    separated = None
    for age in range(3):
        components = list(nx.connected_components(candidate_graph(n, blocks)))
        if len(components) != 2:
            raise AssertionError("both partnered components must stay separate")
        parents = groups(n, blocks)
        if any(len(group) < 3 for group in parents) or any(not any(group <= c for c in components)
                                                           for group in parents):
            raise AssertionError("expected pure supported groups in each component")
        if age == 0:
            separated = [sorted(next(group for group in parents if group <= comp)) for comp in components]
        blocks = after(parents, n)
        n = len(parents)
        sizes.append(n)
    if sizes != [12, 16, 20, 48]:
        raise AssertionError(sizes)
    return {"initial_separated_supports": separated, "live_prefix": sizes,
            "continuation_basis": "two disjoint canonical partnered rosters of WALL-READ"}


def main():
    with tempfile.TemporaryDirectory(prefix="separation-control-") as directory:
        file = Path(directory) / "blocks.txt"
        results = matched_collective_controls(file)
        results["pure_reached_collision"] = pure_collision()
        results["partnered_width_control"] = partnered_width_control()
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
