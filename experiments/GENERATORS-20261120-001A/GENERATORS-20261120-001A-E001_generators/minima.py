"""Exploratory small-atlas lower bound for rank-two witnessed live parts."""

from collections import Counter
from itertools import combinations, combinations_with_replacement, islice
from pathlib import Path
import json

import networkx as nx
from controls import book, certify_source, history, supports

OUT = Path(__file__).resolve().parents[3] / "artifacts"
HERE = Path(__file__).resolve().parent
OUT = OUT / HERE.parent.name / HERE.name / "minima.json"
LIMIT = 7


def inspect_mask(graph, adjacent, mask):
    live = tuple(sorted(v for v in graph if mask >> v & 1))
    witnesses = tuple((w, tuple(v for v in adjacent[w] if mask >> v & 1)) for w in graph)
    witnesses = tuple((w, row) for w, row in witnesses if len(row) >= 2)
    by_pair = {}
    for w, row in witnesses:
        for a, b in combinations(row, 2):
            if (a, b) in by_pair:
                return "multiple_witnesses", (), ()
            by_pair[a, b] = w
    for a, b, c in combinations(live, 3):
        corners = ((a, b), (a, c), (b, c))
        if all(p in by_pair for p in corners) and len({by_pair[p] for p in corners}) != 1:
            return "unheld_triple", (), ()
    # Separate live and witness roles even when one physical holder has both.
    incidence = nx.Graph()
    incidence.add_nodes_from((0, v) for v in live)
    incidence.add_edges_from(((0, v), (1, w)) for w, row in witnesses for v in row)
    ranks = []
    for members in nx.connected_components(incidence):
        edges = sum(incidence.degree(v) for v in members) // 2
        ranks.append(edges - len(members) + 1)
    return "passes", ranks, witnesses


def new_row():
    return {"connected_atlas_graphs": 0, "live_subsets_with_empty": 0, "nonempty_live_subsets": 0,
            "repeated_witness_rejections": 0, "unheld_triple_rejections_after_unique_witness_gate": 0,
            "passes_both_witness_gates": 0, "passing_subsets_with_candidate_pairs": 0,
            "passing_graphs_with_candidate_pairs": 0, "passing_candidate_pair_occurrences": 0,
            "incidence_components_by_cycle_rank": Counter(), "highest_component_rank_by_nonempty_mask": Counter(),
            "rank_two_or_higher_components": 0, "rank_two_or_higher_masks": 0,
            "rank_two_or_higher_graphs": 0}


def enumerate_atlas():
    summary = {n: new_row() for n in range(1, LIMIT + 1)}
    matches = []
    for index, graph in enumerate(nx.graph_atlas_g()):
        n = len(graph)
        if n == 0 or n > LIMIT or not nx.is_connected(graph):
            continue
        row = summary[n]
        row["connected_atlas_graphs"] += 1
        adjacent = {v: sorted(graph[v]) for v in graph}
        found_candidate = False
        found_rank_two = False
        for mask in range(1 << n):
            row["live_subsets_with_empty"] += 1
            row["nonempty_live_subsets"] += bool(mask)
            status, ranks, witnesses = inspect_mask(graph, adjacent, mask)
            if status == "multiple_witnesses":
                row["repeated_witness_rejections"] += 1
                continue
            if status == "unheld_triple":
                row["unheld_triple_rejections_after_unique_witness_gate"] += 1
                continue
            row["passes_both_witness_gates"] += 1
            if witnesses:
                found_candidate = True
                row["passing_subsets_with_candidate_pairs"] += 1
                row["passing_candidate_pair_occurrences"] += sum(
                    len(live) * (len(live) - 1) // 2 for _, live in witnesses)
            row["incidence_components_by_cycle_rank"].update(ranks)
            if ranks:
                row["highest_component_rank_by_nonempty_mask"][max(ranks)] += 1
            high = sum(r >= 2 for r in ranks)
            if high:
                found_rank_two = True
                row["rank_two_or_higher_components"] += high
                row["rank_two_or_higher_masks"] += 1
                matches.append({"atlas_index": index, "knots": n, "ordinary_meetings": sorted(graph.edges()),
                                "live_subset": [v for v in graph if mask >> v & 1],
                                "witness_live_rosters": witnesses, "component_cycle_ranks": ranks})
        row["passing_graphs_with_candidate_pairs"] += found_candidate
        row["rank_two_or_higher_graphs"] += found_rank_two
    return summary, matches


def physical_minima(matches):
    configurations = {}
    examples = {}
    flags = ("lawful_and_funded", "all_originals_covered_by_repeats", "rigid_given_original_subset",
             "repeated_cover_and_rigidity")
    for match in matches:
        edges = tuple(map(tuple, match["ordinary_meetings"]))
        live = set(match["live_subset"])
        n = match["knots"]
        demands = Counter(v for _, row in match["witness_live_rosters"]
                          for a, b in combinations(row, 2) for v in (a, b))
        assert len(live) >= 2 and all(demands[v] >= 2 for v in live)
        for extra in range(5):
            for repeated_indices in combinations_with_replacement(range(len(edges)), extra):
                occurrences = Counter(repeated_indices)
                weighted_degree = Counter(v for i, row in enumerate(edges) for v in row
                                          for _ in range(1 + occurrences[i]))
                opens = {v: max(1, demands[v], 3 - weighted_degree[v]) for v in live}
                assert opens == demands
                budget = len(edges) + extra + sum(opens.values())
                stats = configurations.setdefault(budget, Counter())
                stats["repeat_distributions_with_minimum_opens"] += 1
                if any(weighted_degree[v] < 3 for v in set(range(n)) - live):
                    stats["reject_spent_arity"] += 1
                    continue
                graph = nx.Graph()
                graph.add_nodes_from((v, {"opens": opens.get(v, 0)}) for v in range(n))
                graph.add_edges_from((a, b, {"multiplicity": 1 + occurrences[i]})
                                     for i, (a, b) in enumerate(edges))
                for removed in graph:
                    remaining = graph.subgraph(set(graph) - {removed})
                    assert all(component & live for component in nx.connected_components(remaining))
                assert len(set(graph) - live) == 1
                dead = next(iter(set(graph) - live))
                assert all(other in live for other in graph[dead]) and len(graph[dead]) >= 2
                # Hence either law permits each source star: parity by the
                # wired deletion test above; for NAE each unpinned live knot
                # reserves its loose pair and the spent knot can use a free meeting.
                graph_matcher = nx.algorithms.isomorphism.GraphMatcher(
                    graph, graph, node_match=lambda a, b: a["opens"] == b["opens"],
                    edge_match=lambda a, b: a["multiplicity"] == b["multiplicity"])
                rigid = len(list(islice(graph_matcher.isomorphisms_iter(), 2))) == 1
                covered = len({v for i in occurrences for v in edges[i]}) == n
                for flag, holds in zip(flags, (True, covered, rigid, covered and rigid), strict=True):
                    if not holds:
                        continue
                    stats[flag] += 1
                    if flag not in examples or budget < examples[flag][0]:
                        examples[flag] = (budget, match, tuple(edges[i] for i in repeated_indices), opens)
    witnesses = {}
    for flag, (budget, match, repeats, opens) in examples.items():
        meetings = [*map(tuple, match["ordinary_meetings"]), *repeats]
        stars = supports(match["knots"], meetings, [v for v, h in sorted(opens.items()) for _ in range(h)])
        assert sum(map(len, stars)) - len(meetings) == budget
        witnesses[flag] = {"budget": budget, "atlas_index": match["atlas_index"],
                           "extra_meetings": repeats, "opens": opens,
                           "starting_source": certify_source(stars),
                           "first_steps": {law: [book(f) for f in history(stars, law, 2)]
                                           for law in ("parity", "nae")}}
    return {"minimum_open_rule": "max(1, candidate-pair demand, 3-weighted ordinary degree) at live knots",
            "counting": ("distributions of up to four additional shared distinctions, "
                         "no surplus loose distinctions beyond the minimum; both literal masks counted"),
            "by_distinctions": configurations, "minimum_witnesses": witnesses}


def main():
    summary, matches = enumerate_atlas()
    out = {"scope": "exploratory exhaustive structural screen of connected ordinary simple graphs",
           "atlas": "networkx.graph_atlas_g",
           "counting": "all literal masks per unlabelled graph; distinct witness and live roles",
           "maximum_original_knots": LIMIT, "by_size": summary, "rank_two_witnesses": matches,
           "seven_knot_physical_budgets": physical_minima(matches)}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    main()
