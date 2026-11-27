"""Replay published draws and resolve each hash group up to exact renaming.

Every shared distinction in these weightings has two holders. Matching the
number of places on each knot and the shared-distinction multiplicity on each
pair preserves the meeting pattern. The number of loose distinctions on a
knot is its number of places minus the sum of its shared multiplicities.
"""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
import json
from pathlib import Path
import random
import resource
import time

from networkx import Graph, is_isomorphic, weisfeiler_lehman_graph_hash
from networkx.algorithms.isomorphism import categorical_edge_match, categorical_node_match

from sampling import KNOT_COUNTS, WEIGHTINGS, draw_start, read_start, start_check


SEED = 2026112701
PUBLISHED_DRAWS = 3000
HERE = Path(__file__).resolve().parent
PUBLISHED_COUNTS = HERE.parent / "counts"
LIMITS = (5000, 250000, 25)
MATCH_PLACES = categorical_node_match("p", None)
MATCH_MULTIPLICITY = categorical_edge_match("m", None)


@dataclass
class Representative:
    graph: Graph
    stars: list
    first_draw: int
    admission: str
    draws: int = 1


def describe(stars):
    """Keep places and multiplicities, the attributes used in the study hash."""
    holders = defaultdict(list)
    graph = Graph()
    for knot, star in enumerate(stars):
        graph.add_node(knot, p=str(len(star)))
        for distinction in star:
            holders[distinction].append(knot)
    if any(len(held) > 2 or len(held) != len(set(held)) for held in holders.values()):
        raise ValueError("Hash representation requires each distinction in at most two distinct knots")
    multiplicities = Counter(tuple(held) for held in holders.values() if len(held) == 2)
    for (a, b), multiplicity in multiplicities.items():
        graph.add_edge(a, b, m=str(multiplicity))
    return graph


def study_hash(graph):
    return weisfeiler_lehman_graph_hash(graph, node_attr="p", edge_attr="m", iterations=4)


def exact_match(left, right):
    return is_isomorphic(left, right, node_match=MATCH_PLACES, edge_match=MATCH_MULTIPLICITY)


def check_matcher():
    stars = [[0, 1, 2, 3], [0, 1, 4], [2, 5, 6]]
    renamed = [[24, 25, 20], [25, 23, 21, 22], [26, 22, 21]]
    different_places = [[0, 1, 2, 3, 7], [0, 1, 4], [2, 5, 6]]
    different_multiplicities = [[0, 1, 2, 3], [0, 4, 7], [2, 5, 6]]
    original = describe(stars)
    assert study_hash(original) == study_hash(describe(renamed))
    assert exact_match(original, describe(renamed))
    assert not exact_match(original, describe(different_places))
    assert not exact_match(original, describe(different_multiplicities))

    # With identical attributes, two connected regular graphs of the same
    # order can have the same hash. Only one of these has triples that all share.
    left, right = Graph(), Graph()
    for graph in (left, right):
        graph.add_nodes_from(range(6), p="8")
    left.add_edges_from(((a, b) for a in range(3) for b in range(3, 6)), m="1")
    right.add_edges_from(((0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3),
                          (0, 3), (1, 4), (2, 5)), m="1")
    assert study_hash(left) == study_hash(right)
    assert not exact_match(left, right)
    return ["renaming preserves exact match and hash", "places and multiplicities affect exact match",
            "two connected regular graphs exercise collision detection"]


def classify(stars):
    status, portion, loose, pieces = start_check(stars, *LIMITS, "all", "nae")
    if status == "finished":
        failures = {name for piece in pieces for name in piece["witnesses"]}
        if "N1" in failures:
            label = "fails N1 (chained twins)"
        elif "N2" in failures:
            label = "fails N2 only (lifts do not meet)"
        elif "N3" in failures:
            label = "fails N3 only"
        else:
            label = "in the class, with chains" if any(p["chain_bases"] for p in pieces) else "in the class, no chains"
    elif status == "rank cap":
        label = "core does not finish by rank 25"
    else:
        assert status in {"birth cap", "maximal-family cap", "parent-pair cap"}
        label = "core over the cap"
    return {"label": label, "piece_type": portion, "loose_distinctions": loose, "pieces": pieces}


def collision_details(key, group, corrections):
    accepted = [rep for rep in group if rep.admission == "admitted"]
    reports = []
    for rep in group:
        row = {"first_draw": rep.first_draw, "admission": rep.admission, "draws": rep.draws, "stars": rep.stars}
        row["mutually_overlapping_triples"] = [triple for triple in combinations(rep.graph, 3)
                                              if all(rep.graph.has_edge(*pair) for pair in combinations(triple, 2))]
        if len(accepted) > 1 and rep.admission == "admitted":
            row["classification"] = classify(rep.stars)
        reports.append(row)
    classified = [row for row in reports if "classification" in row]
    if classified:
        cached = classified[0]["classification"]["label"]
        for row in classified[1:]:
            label = row["classification"]["label"]
            corrections["distinct"][label] += 1
            if label != cached:
                corrections["draws"][cached] -= row["draws"]
                corrections["draws"][label] += row["draws"]
    return {"hash": key, "representatives": reports}


def replay(weighting, knots, draws, seed):
    published = json.loads((PUBLISHED_COUNTS / f"{weighting}_{knots}.json").read_text())
    assert (published["weighting"], published["knots"], published["draws"], published["seed"]) == (
        weighting, knots, PUBLISHED_DRAWS, seed)
    rng = random.Random(seed)
    groups = defaultdict(list)
    admission_counts = Counter()
    for draw in range(draws):
        stars = draw_start(weighting, knots, rng)
        admission, _, _ = read_start(stars)
        admission_counts[admission] += 1
        graph = describe(stars)
        group = groups[study_hash(graph)]
        for representative in group:
            if exact_match(representative.graph, graph):
                assert representative.admission == admission
                representative.draws += 1
                break
        else:
            group.append(Representative(graph, stars, draw, admission))

    admitted_groups = [[rep for rep in group if rep.admission == "admitted"] for group in groups.values()]
    accepted_hashes = sum(bool(group) for group in admitted_groups)
    accepted_distinct = sum(map(len, admitted_groups))
    accepted_draws = admission_counts["admitted"]
    published_draws = draws - published["accepted draws with repeats"].get("not accepted", 0)
    published_distinct = sum(published["distinct accepted starts"].values())
    corrections = {"distinct": Counter(), "draws": Counter()}
    collisions = [collision_details(key, group, corrections) for key, group in groups.items() if len(group) > 1]
    return {
        "weighting": weighting, "knots": knots, "draws": draws, "seed": seed,
        "admission": dict(admission_counts), "accepted_draws": accepted_draws,
        "accepted_exact_starts": accepted_distinct, "accepted_hash_groups": accepted_hashes,
        "accepted_repeat_draws": accepted_draws - accepted_distinct,
        "accepted_hash_collision_groups": sum(len(group) > 1 for group in admitted_groups),
        "accepted_distinct_starts_merged_by_hash": accepted_distinct - accepted_hashes,
        "all_hash_groups": len(groups), "all_exact_starts": sum(map(len, groups.values())),
        "all_hash_collision_groups": len(collisions), "collisions": collisions,
        "collision_corrections_by_bin": corrections,
        "published_accepted_draws": published_draws if draws == PUBLISHED_DRAWS else None,
        "published_distinct_starts": published_distinct if draws == PUBLISHED_DRAWS else None,
        "matches_published_totals": (accepted_draws, accepted_distinct) == (published_draws, published_distinct)
        if draws == PUBLISHED_DRAWS else None,
    }


def group_sample(rows):
    groups = defaultdict(list)
    for row, stars in rows:
        graph = describe(stars)
        group = groups[study_hash(graph)]
        for representative, records in group:
            if exact_match(representative, graph):
                records.append(row)
                break
        else:
            group.append((graph, [row]))
    grouped = [records for group in groups.values() for _, records in group]
    return {"rows": len(rows), "exact_starts": len(grouped), "hash_groups": len(groups),
            "repeated_classes": [records for records in grouped if len(records) > 1]}


def replay_shapes():
    research = HERE.parent.parent
    paths = {name: research / folder / name for folder, names in (
        ("GRADED-ORDER-20261126-001", ("held_grow.jsonl", "replays.jsonl")),
        ("CYCLE-READ-20261127-001", ("twin8_draw.jsonl", "twin9_draw.jsonl", "cyc6_uniform.jsonl")),
    ) for name in names}
    records = {name: path.read_text().splitlines() for name, path in paths.items()}
    comparison = json.loads((HERE / "comparison.json").read_text())["sample"]
    failures, agreement, capped, witnesses = [], [], [], []
    for row in comparison:
        source = json.loads(records[row["file"]][row["line"] - 1])
        metadata = {**row, "draw": source.get("draw", source.get("index"))}
        target = capped if row["status"] != "finished" else failures if row["child_round"] else agreement
        target.append((metadata, source["stars"]))
    path = HERE.parent / "referee_witnesses.jsonl"
    index = {row["line"]: row for row in json.loads((HERE / "first_failures.json").read_text())
             if row["file"].endswith("/referee_witnesses.jsonl")}
    for line, source in enumerate(map(json.loads, path.read_text().splitlines()), 1):
        row = index[line]
        metadata = {"file": path.name, "line": line, "witness": source["draw"],
                    "status": row["status"], "child_round": row.get("child_round")}
        witnesses.append((metadata, source["stars"]))
    assert tuple(map(len, (failures, agreement, capped, witnesses))) == (67, 369, 2, 7)
    return {"failing_shape_rows": group_sample(failures), "agreeing_shape_rows": group_sample(agreement),
            "capped_shape_rows": group_sample(capped), "supplied_witness_rows": group_sample(witnesses),
            "all_failing_rows_including_witnesses": group_sample(failures + [
                (row, stars) for row, stars in witnesses if row["status"] == "failure"]),
            "all_shape_and_witness_rows": group_sample(failures + agreement + capped + witnesses)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draws", type=int, default=PUBLISHED_DRAWS)
    parser.add_argument("--shapes", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.draws <= PUBLISHED_DRAWS:
        parser.error("Choose a nonempty prefix of the published draws")
    controls = check_matcher()
    cpu_start, wall_start = time.process_time(), time.perf_counter()
    if args.shapes:
        shapes = replay_shapes()
        for sample, details in shapes.items():
            print(sample, details["rows"], details["exact_starts"], details["hash_groups"], flush=True)
        write_result(args.output, {"controls": controls, **shapes, **resources(cpu_start, wall_start)})
        return
    cells = []
    for weighting in WEIGHTINGS:
        for knots in KNOT_COUNTS:
            cell = replay(weighting, knots, args.draws, SEED)
            cells.append(cell)
            print(weighting, knots, "draws/exact/hash", cell["accepted_draws"], cell["accepted_exact_starts"],
                  cell["accepted_hash_groups"], "collisions among all", cell["all_hash_collision_groups"], flush=True)
    result = {
        "draw_index_origin": 0, "controls": controls,
        "classification_limits": dict(zip(("core_nodes", "parent_pairs", "rank"), LIMITS)),
        **resources(cpu_start, wall_start), "cells": cells,
    }
    print(round(result["cpu_seconds"], 3), "CPU seconds", result["peak_rss_kib"], "KiB peak RSS", flush=True)
    write_result(args.output, result)


def resources(cpu_start, wall_start):
    return {"cpu_seconds": time.process_time() - cpu_start, "wall_seconds": time.perf_counter() - wall_start,
            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def write_result(path, result):
    if path is not None:
        with path.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")


if __name__ == "__main__":
    main()
