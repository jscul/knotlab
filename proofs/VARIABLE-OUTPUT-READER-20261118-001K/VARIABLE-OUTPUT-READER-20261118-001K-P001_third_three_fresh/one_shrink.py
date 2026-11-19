"""Determine all reachable answers for a single-shrink K table through D=5."""

from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
from random import Random
import hashlib
import json

import networkx as nx

HERE = Path(__file__).resolve().parent
PROOFS = HERE.parents[1]
measure_file, = (PROOFS / "VARIABLE-OUTPUT-READER-20261118-001H").glob("*/check_reader.py")
spec = spec_from_file_location("serial_short_bonds", measure_file)
measure = module_from_spec(spec)
spec.loader.exec_module(measure)
oracle = measure.oracle


def low_sites(width, entries):
    """Recover the seed, four-place sites and five-place shrink from the anonymous short pairs."""
    sites = []
    shrinks = None
    for size in (3, 4, 5):
        if size == 5 and shrinks == 2:
            break
        graph = nx.Graph()
        graph.add_nodes_from(range(width))
        graph.add_edges_from(pair for pair, k in entries.items() if k <= size)
        if size == 5:
            seed, = (row for row in sites if len(row) == 3)
            for row in sites:
                if len(row) == 4 and seed & row:
                    graph.remove_edges_from((a, b) for a in seed - row for b in row - seed)
        sites.extend(frozenset(c) for c in nx.find_cliques(graph) if len(c) == size)
        if size == 4:
            assert width % 2 == 0
            number_of_sites = (width - 4) // 2
            shrinks = number_of_sites - sum(len(row) == 4 for row in sites) - 2
            assert 0 <= shrinks <= 2
    assert sum(len(row) == 3 for row in sites) == 1
    assert shrinks == 2 or sum(len(row) == 5 for row in sites) == shrinks
    return shrinks, tuple(sorted(sites, key=lambda row: (len(row), sorted(row))))


def incidence(rows, width):
    holders = [[] for _ in range(width)]
    neighbors = [set() for _ in rows]
    for i, row in enumerate(rows):
        for bit in row:
            holders[bit].append(i)
    for group in holders:
        if len(group) == 2:
            left, right = group
            neighbors[left].add(right)
            neighbors[right].add(left)
    return holders, neighbors


def clipped_table(rows, width):
    measured, _, _ = measure.measured_short_bonds(rows, width, 6)
    return measured


def reachable_order(rows, neighbors, first, second):
    """On a fixed ordinary graph, prescribed indegrees give at most one acyclic orientation."""
    seed, = (i for i, row in enumerate(rows) if len(row) == 3)
    need = [len(row) - (3 if i in (first, second) or len(row) == 6 else 2)
            for i, row in enumerate(rows)]
    need[seed] = 0
    if sum(need) != sum(map(len, neighbors)) // 2:
        return None
    active = set(range(len(rows)))
    seen, order = set(), []
    for _ in rows:
        if len(order) < 3:
            site = (seed, first, second)[len(order)]
            if site not in active or need[site] != 0:
                return None
        else:
            site = next((i for i in sorted(active) if need[i] == 0), None)
            if site is None:
                return None
        parents = neighbors[site] & seen
        if len(parents) >= 2:
            if any(not (neighbors[a] & neighbors[b] & seen) for a, b in combinations(parents, 2)):
                return None
            if len(parents) == 3 and set.intersection(*(neighbors[a] for a in parents)) & seen:
                return None
        for other in neighbors[site] & active:
            need[other] -= 1
            if need[other] < 0:
                return None
        active.remove(site)
        seen.add(site)
        order.append(site)
    # Independently reapply the original loose-bit law to the concrete supports.
    oracle.replay_history(tuple(tuple(sorted(s)) for s in rows), tuple(order))
    return tuple(order)


def realize(rows, neighbors):
    seed, = (i for i, row in enumerate(rows) if len(row) == 3)
    trials = 0
    for first in sorted(neighbors[seed]):
        if len(rows[first]) != 4:
            continue
        next_unary = (neighbors[first] | neighbors[seed]) - {seed, first}
        for second in sorted(next_unary):
            if len(rows[second]) != 4:
                continue
            trials += 1
            order = reachable_order(rows, neighbors, first, second)
            if order is not None:
                return order, trials
    return None, trials


def read_table(width, short_entries):
    """Only this routine receives the observation. Bits use integers to index the table."""
    shrinks, low = low_sites(width, short_entries)
    if shrinks == 2:
        return {"shrinks": 2, "counts": {}, "matches": [], "possible_menus": [[]]}
    holders, low_adj = incidence(low, width)
    ground_high = frozenset(i for i, sites in enumerate(holders) if not sites)
    dangling = tuple(i for i, sites in enumerate(holders) if len(sites) == 1)
    assert all(len(sites) <= 2 for sites in holders)
    assert len(ground_high) <= 3 and len(dangling) == 13 - shrinks - 2 * len(ground_high)
    low_graph = nx.Graph()
    low_graph.add_nodes_from(range(len(low)))
    low_graph.add_edges_from((i, j) for i, near in enumerate(low_adj) for j in near)
    assert nx.is_connected(low_graph)
    colors = nx.algorithms.bipartite.color(low_graph)
    k = 6 - len(ground_high)
    allowed_pairs = set(short_entries)
    counts = Counter()
    matches = []
    for selected in combinations(dangling, k):
        counts["high_subsets"] += 1
        adjacent = {holders[bit][0] for bit in selected}
        if len(adjacent) != k or len({colors[i] for i in adjacent}) != 1:
            continue
        high = ground_high | frozenset(selected)
        exterior = ground_high | (set(dangling) - set(selected))
        short_stars = (high, exterior) if shrinks == 1 else (high,)
        if any(pair not in allowed_pairs for support in short_stars
               for pair in combinations(sorted(support), 2)):
            continue
        counts["simple_short_candidates"] += 1
        rows = (*low, high)
        neighbors = [a.copy() for a in low_adj]
        for site in adjacent:
            neighbors[site].add(len(low))
        neighbors.append(adjacent)
        order, trials = realize(rows, neighbors)
        counts["startup_trials"] += trials
        if order is None:
            continue
        counts["reachable_supports"] += 1
        chronological = tuple(tuple(sorted(rows[i])) for i in order)
        if clipped_table(chronological, width) == short_entries:
            menu = sorted(oracle.permissions(chronological))
            matches.append({"six_place_support": sorted(high), "legal_marks": menu,
                            "one_reachable_order": list(order)})
    assert matches
    menus = sorted({tuple(tuple(mark) for mark in record["legal_marks"]) for record in matches})
    return dict(shrinks=shrinks, counts=counts, matches=matches, possible_menus=menus)


def grade(rows, name):
    flat = tuple(tuple(row) for row in rows)
    width = 1 + max(map(max, flat))
    observed = clipped_table(flat, width)
    expected = sorted(oracle.permissions(flat))
    out = read_table(width, observed)
    answers = out["matches"]
    true_high, = (row for row in flat if len(row) == 6)
    if out["shrinks"] < 2:
        assert sorted(true_high) in [rec["six_place_support"] for rec in answers]
        assert expected in [rec["legal_marks"] for rec in answers]
    else:
        assert not expected
    return {"name": name, "width": width, "sites": len(flat), "legal_marks": expected, **out}


def fixtures():
    closure = json.loads((HERE / "closure.json").read_bytes())
    cases = []
    for c in closure["shortest_post_exception_histories"]:
        if c["prior_shrinks"] + c["subsequent_shrinks"] in (0, 1, 2):
            for key in ("first_history", "first_with_a_legal_triple", "first_with_a_legal_triple_using_high_output"):
                if key in c:
                    cases.append((f"high_after_{c['prior_shrinks']}_{key}", c[key]["junction_supports"]))
    for c in closure["last_site_complement_test"]["all_complementary_cases"]:
        cases.append(("complementary_prefix", c["prefix"]["junction_supports"]))
    # Width 28, two state spaces even for the exact table. It is a test of the enumeration itself.
    prior = json.loads(next((PROOFS / "VARIABLE-OUTPUT-READER-20261118-001J").glob("*/frontier.json")).read_bytes())
    base = prior["sharp_distance_four"]["junction_supports"]
    cases.append(("equation_changes_on_full_table", [*base, [12,20,21,25,26,27]]))
    seen = set()
    for name, rows in cases:
        key = tuple(tuple(row) for row in rows)
        if key not in seen:
            yield name, key
            seen.add(key)


def named_controls():
    cases = []
    for name, rows in fixtures():
        out = grade(rows, name)
        width = out["width"]
        permutation = list(range(width))
        Random(17011 + width).shuffle(permutation)
        original = clipped_table(rows, width)
        renamed = {tuple(sorted((permutation[a], permutation[b]))): k
                   for (a, b), k in original.items()}
        second = read_table(width, renamed)
        expected = {tuple(sorted(tuple(sorted(permutation[i] for i in mark)) for mark in menu))
                    for menu in out["possible_menus"]}
        assert expected == {tuple(menu) for menu in second["possible_menus"]}
        assert {tuple(sorted(permutation[i] for i in item["six_place_support"])) for item in out["matches"]} == {
            tuple(item["six_place_support"]) for item in second["matches"]}
        out["renaming_checked"] = permutation
        cases.append(out)
    return cases


def compare_positive_representatives():
    from closure import explore, literal_options
    _, representatives, _, _, _ = explore()
    counts = Counter()
    rows_digest = hashlib.sha256()
    for state, (rows, high) in representatives.items():
        if high is None or state.shrinks != 1:
            continue
        _, _, groups = literal_options(rows, state, high)
        if not any(len(group) == 3 for group in groups):
            continue
        out = grade(rows, "single_shrink")
        counts[(state.prior_shrinks, out["counts"]["simple_short_candidates"],
                len(out["matches"]), len(out["possible_menus"]))] += 1
        rows_digest.update(json.dumps([rows, out], sort_keys=True, separators=(",", ":")).encode())
    return {"records": sum(counts.values()), "history_and_answer_sha256": rows_digest.hexdigest(),
            "distribution": [{"shrinks_before_high": prior, "simple_short_candidates": candidates,
                              "reachable_matches": matches, "distinct_menus": menus, "records": count}
                             for (prior, candidates, matches, menus), count in sorted(counts.items())]}


if __name__ == "__main__":
    print(json.dumps({"controls": named_controls(),
                      "one_history_per_positive_frontier": compare_positive_representatives()}, indent=2))
