"""Replay m²-to-m-to-one terminal costs via the archived complete-round verifier."""

import argparse
from collections import Counter, defaultdict, deque
import importlib.util
import json
from pathlib import Path
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = "GROWN-END-SWAP-20261119-001"
CHECKER = ROOT / "experiments" / OLD / f"{OLD}-E001_reached" / "verify.py"
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "scale_square_branch.json"


def dot(i, j):
    return (i & j).bit_count() % 2


def coverage(m, sign):
    minimum = m
    for i in range(1, m + 1):
        occur = {sign(i, j) for j in range(1, m + 1) if j != i}
        if occur != {0, 1}:
            return 0
        for k in range(1, i):
            counts = [0] * 4
            for j in range(1, m + 1):
                if i != j and k != j:
                    counts[2 * sign(i, j) + sign(k, j)] += 1
            minimum = min(minimum, *counts)
    return minimum


class Source:
    def __init__(self):
        self.rows = []
        self.loose = defaultdict(deque)
        self.next_name = 0

    def site(self):
        self.rows.append(set())
        return len(self.rows) - 1

    def link(self, a, b, count=1):
        block = range(self.next_name, self.next_name + count)
        self.rows[a].update(block)
        self.rows[b].update(block)
        self.next_name += count

    def give(self, a, count):
        block = range(self.next_name, self.next_name + count)
        self.rows[a].update(block)
        self.loose[a].extend(block)
        self.next_name += count

    def born(self, parents, fresh):
        site = self.site()
        self.rows[site].update(self.loose[parent].popleft() for parent in parents)
        self.give(site, fresh)
        return site

    def snapshot(self, verify):
        return verify.Arrangement(tuple(frozenset(row) for row in self.rows))


def make_branch(source, root, m):
    indices = range(1, m + 1)
    shared = [source.site() for _ in range(m - 1)]
    pair = {i: (source.site(), source.site()) for i in indices}
    for a in shared:
        source.link(root, a, m)
    for a, b in pair.values():
        source.link(root, a)
        source.link(root, b)

    first = []
    for j in indices:
        private, w0, w1 = (source.site() for _ in range(3))
        source.link(private, w0)
        source.link(private, w1)
        selected = [pair[i][dot(i, j)] for i in indices if i != j]
        for a in shared:
            source.link(w0, a)
        for b in selected:
            source.link(w1, b)
        first.append((private, *shared, *selected))
    first += [pair[i] for i in indices]
    for parents in first:
        for u in parents:
            source.give(u, 1)
    return first


def weighted_graph(stage, selected=None):
    graph = nx.Graph()
    for ends in stage.owners.values():
        if selected is not None and any(u not in selected for u in ends):
            continue
        u, v = ends if len(ends) == 2 else (ends[0], "outside")
        if not graph.has_edge(u, v):
            graph.add_edge(u, v, capacity=0)
        graph[u][v]["capacity"] += 1
    return graph


def run(verify, d):
    m = (1 << d) - 1
    minimum = coverage(m, dot)
    assert minimum >= 1 and not coverage(m, lambda i, j: 0)
    source = Source()
    roots = [source.site(), source.site()]
    source.link(*roots)
    first = []
    branch_nodes = []
    for root in roots:
        before = len(source.rows)
        first.append(make_branch(source, root, m))
        branch_nodes.append({root, *range(before, len(source.rows))})
    stages = [source.snapshot(verify)]
    second = []
    for plans, local in zip(first, branch_nodes):
        x = [source.born(parents, m - 1) for parents in plans[:m]]
        y = [source.born(parents, 1) for parents in plans[m:]]
        local.update(x + y)
        second.append([[y[i], *[site for j, site in enumerate(x) if j != i]] for i in range(m)])
    stages.append(source.snapshot(verify))
    third = []
    for plans, local in zip(second, branch_nodes):
        g = [source.born(parents, 1) for parents in plans]
        local.update(g)
        third.append(g)
    stages.append(source.snapshot(verify))
    for parents, local in zip(third, branch_nodes):
        local.add(source.born(parents, 1))
    stages.append(source.snapshot(verify))

    reached_sites = (len(stages[1].stars) - len(roots)) // 2
    reached_width = (len(stages[1].labels) - 1) // 2
    assert len(stages[1].stars) == len(roots) + 2 * (8 * m - 1)
    assert len(stages[1].labels) == 1 + 2 * (6 * m * m + 2 * m)
    replayed = []
    role_counts = {}
    for age, (earlier, later) in enumerate(zip(stages, stages[1:]), 1):
        records = verify.round_replay(earlier, later)
        assert all(not row["implied"] for row in records)
        observed = Counter((len(row["taken"]), row["demand"], len(row["fresh"]))
                           for row in records)
        expected_roles = {
            1: {"X": ((2 * m - 1, m - 1, m - 1), 2 * m),
                "Y": ((2, 1, 1), 2 * m)},
            2: {"G": ((m, 1, 1), 2 * m)},
            3: {"cap": ((m, 0, 1), 2)},
        }[age]
        assert observed == Counter(dict(expected_roles.values()))
        for role, (signature, count) in expected_roles.items():
            parents, demand, fresh = signature
            role_counts[role] = {"parents": parents, "next_demand": demand, "fresh": fresh,
                                 "ordinary_sites_in_two_copies": observed[signature]}
        replayed.append(len(records))
    prices = []
    for stage in stages:
        graph = weighted_graph(stage)
        assert all(len(row) >= 3 for row in stage.stars)
        assert not any(u != "outside" for u in nx.articulation_points(graph))
        assert all(graph[u][v]["capacity"] > 1 for u, v in nx.bridges(graph))
    for root, local in zip(roots, branch_nodes):
        values = [nx.minimum_cut_value(weighted_graph(stage, local), root, "outside") for stage in stages[1:]]
        assert values == [m * m, m, 1]
        prices.append(values)
    return {"dimension": d, "m": m, "minimum_punctured_pair_pattern_multiplicity": minimum,
            "ordinary_sites_by_age": [len(stage.stars) for stage in stages],
            "literal_width_by_age": [len(stage.labels) for stage in stages],
            "new_junction_counts": replayed, "fewest_fresh_by_role": role_counts,
            "separating_prices_ages_one_two_three": prices,
            "reached_junctions_per_branch_excluding_root": reached_sites,
            "reached_width_per_branch_excluding_core": reached_width,
            "constant_sign_control_pair_coverage": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("scale_complete_previous", CHECKER)
    verify = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = verify
    spec.loader.exec_module(verify)
    data = {"scope": "Two independent shield branches with roots joined by one ordinary name. All loose ends share one exterior.",
            "checker": str(CHECKER.relative_to(ROOT)), "cases": [run(verify, d) for d in (4, 5)]}
    encoded = json.dumps(data, indent=2) + "\n"
    if args.check:
        if OUT.read_text() != encoded:
            raise SystemExit("saved squared-price replay differs")
    else:
        OUT.write_text(encoded)
    print("All three complete rounds and all four terminal-price sequences passed.")
