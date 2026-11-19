"""Exact small weighted populations and an independent strict-future order reader."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
from heapq import heapify, heappop, heappush
from itertools import combinations, permutations, product
import json
from math import comb, factorial
from pathlib import Path
import sys

import networkx as nx


ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments"
VERIFY = "GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached"
EXTEND = "EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend"
SCALE_OUTPUT = ROOT / "artifacts/BOND-READING-SCALE-20261119-001/BOND-READING-SCALE-20261119-001-E001_size"
sys.path[:0] = [str(EXP / VERIFY), str(EXP / EXTEND)]
from verify import Arrangement, groups, round_replay, start_audit  # noqa: E402
from extend import grow1  # noqa: E402


def raw(stage):
    return [sorted(row) for row in stage.stars]


def fingerprint(stage):
    canonical_rows = sorted(raw(stage))
    return sha256(json.dumps(canonical_rows, separators=(",", ":")).encode()).hexdigest()


def graph(stage):
    ends, adjacent, outside = stage.holder_graph()
    result = nx.MultiGraph()
    result.add_nodes_from((j, {"exterior": j == outside}) for j in range(len(adjacent)))
    result.add_edges_from(ends.values())
    return result


def same_shape(a, b):
    return nx.is_isomorphic(graph(a), graph(b), node_match=lambda v, w: v["exterior"] == w["exterior"])


def prufer(m, word):
    degree = [1] * m
    for u in word:
        degree[u] += 1
    leaves = [u for u in range(m) if degree[u] == 1]
    heapify(leaves)
    links = []
    for u in word:
        v = heappop(leaves)
        links.append(tuple(sorted((u, v))))
        degree[u] -= 1
        if degree[u] == 1:
            heappush(leaves, u)
    links.append(tuple(sorted(leaves)))
    return tuple(sorted(links))


def population(m):
    tree = Counter(prufer(m, code) for code in product(range(m), repeat=m - 2))
    assert len(tree) == m ** (m - 2) and set(tree.values()) == {1}
    recursive = Counter(tuple(sorted(tuple(sorted((p[u], p[v]))) for v, u in enumerate(parents, 1)))
                        for parents in product(*(range(v) for v in range(1, m))) for p in permutations(range(m)))
    assert set(recursive) == set(tree) and sum(recursive.values()) == factorial(m - 1) * factorial(m)
    missing_count = comb(m, 2) - (m - 1)
    extra = (m + 2) // 4
    all_links = set(combinations(range(m), 2))
    augmented = Counter(tuple(sorted((*links, *chosen))) for links in tree
                        for chosen in combinations(sorted(all_links - set(links)), extra))
    assert sum(augmented.values()) == len(tree) * comb(missing_count, extra)
    if extra == 1:
        for links, count in augmented.items():
            cycles = nx.cycle_basis(nx.Graph(links))
            assert len(cycles) == 1 and len(cycles[0]) == count
    return {"uniform_labelled_tree": tree, "uniform_tree_plus_links": augmented, "uniform_recursive_tree": recursive}


@cache
def shape_id(m, links):
    return min(tuple(sorted(tuple(sorted((p[u], p[v]))) for u, v in links)) for p in permutations(range(m)))


def start_for(m, links):
    rows = [[] for _ in range(m)]
    for name, (u, v) in enumerate(links):
        rows[u].append(name)
        rows[v].append(name)
    fresh = len(links)
    for row in rows:
        count = max(0, 3 - len(row))
        row.extend(range(fresh, fresh + count))
        fresh += count
    stage = Arrangement.parse(rows)
    assert start_audit(stage)["census_open_legal"]
    return stage


def demand_deficits(stage):
    demand = Counter(u for component in groups(stage.neighbors, stage.live) for u in component)
    available = Counter(stage.loose.values())
    return [(u, demand[u], available[u]) for u in sorted(stage.live) if demand[u] > available[u]]


def advance(stage):
    if not stage.live:
        return "closed", None
    success = not demand_deficits(stage)
    native = grow1(stage.stars)
    assert (native is not None) == success
    if native is None:
        return "demand_stall", None
    next_stage = Arrangement.parse([sorted(x) for x in native])
    round_replay(stage, next_stage)
    return ("next_open" if next_stage.live else "next_closes"), next_stage


def trajectory(start, depth=3):
    stages = [start]
    transitions = []
    for _ in range(depth):
        status, next_stage = advance(stages[-1])
        transitions.append(status)
        if next_stage is None:
            break
        stages.append(next_stage)
    return stages, transitions


def labels_of(word):
    while word:
        bit = word & -word
        word ^= bit
        yield bit.bit_length() - 1


def independent_bonds(stage):
    equations = {0}
    for row in stage.masks:
        equations |= {row ^ word for word in equations}
    minimal = []
    for word in sorted(equations - {0}, key=lambda w: (w.bit_count(), w)):
        if not any(word & item == item for item in minimal):
            minimal.append(word)

    ends, adjacency, _ = stage.holder_graph()
    full = (1 << len(adjacency)) - 1

    def connected(shore):
        pending = shore & -shore
        left = shore ^ pending
        while pending:
            u = pending & -pending
            pending ^= u
            found = adjacency[u.bit_length() - 1] & left
            pending |= found
            left ^= found
        return left == 0

    graph_words = set()
    for shore in range(1, (full + 1) // 2):
        if connected(shore) and connected(full ^ shore):
            word = sum(stage.label_bits[x] for x, (u, v) in ends.items() if ((shore >> u) ^ (shore >> v)) & 1)
            graph_words.add(word)
    assert graph_words == set(minimal)
    return minimal, equations


def table_at(bonds, order):
    table = {}
    for word in bonds:
        for mark in combinations(labels_of(word), order):
            table.setdefault(mark, word.bit_count())
    return table


def preserves_rows(permutation, stage, equations):
    return all(sum(1 << permutation[x] for x in labels_of(row)) in equations for row in stage.masks)


def fixed_indices(stage):
    return {j for i in stage.live for j in labels_of(stage.masks[i])}


def preserving_generators(stage, tables):
    width = len(stage.labels)
    fixed = fixed_indices(stage)
    movable = sorted(set(range(width)) - fixed)
    identity = list(range(width))
    order = len(tables)
    if order <= 1:
        colors = defaultdict(list)
        for x in movable:
            colors[tables[0].get((x,)) if order else None].append(x)
        for members in colors.values():
            for a, b in zip(members, members[1:]):
                g = identity.copy()
                g[a], g[b] = b, a
                yield g
        return

    # Signatures may use already marked names, as their images are fixed in all groups.
    signatures = {}
    for x in movable:
        signature = [tables[0].get((x,))]
        for arity, table in enumerate(tables[1:], 2):
            signature.append(tuple(table.get(tuple(sorted((x, *key)))) for key in combinations(sorted(fixed), arity - 1)))
            if arity == 2:
                signature.append(Counter(table.get(tuple(sorted((x, y)))) for y in range(width) if y != x))
        signatures[x] = signature
    potential = {x: {y for y in movable if signatures[x] == signatures[y]} for x in movable}

    def fits(x, y, partial):
        return all(table.get(tuple(sorted((x, *key)))) == table.get(tuple(sorted((y, *(partial[z] for z in key)))))
                   for arity, table in enumerate(tables[1:], 2) for key in combinations(partial, arity - 1)
                   if not fixed.issuperset(key))

    def find(partial, unused):
        if not unused:
            return [partial[x] for x in range(width)]
        choices = {x: [y for y in sorted(unused & potential[x]) if fits(x, y, partial)]
                   for x in movable if x not in partial}
        x = min(choices, key=lambda a: (len(choices[a]), a))
        for y in choices[x]:
            candidate = find(partial | {x: y}, unused - {y})
            if candidate is not None:
                return candidate
        return None

    partial = {x: x for x in fixed}
    for x in movable:
        unused = set(movable) - partial.keys() - {x}
        for y in sorted(potential[x] & unused):
            if not fits(x, y, partial):
                continue
            candidate = find(partial | {x: y}, (unused | {x}) - {y})
            if candidate is not None:
                assert all(candidate[z] == z for z in fixed)
                assert all(all(table.get(tuple(sorted(candidate[t] for t in mark))) == value
                               for mark, value in table.items()) for table in tables)
                yield candidate
        partial[x] = x


def exact_order(stage, status, cap=3):
    if status in {"closed", "demand_stall"}:
        return {"order": 0, "decides_future": True, "tests": []}
    bonds, equations = independent_bonds(stage)
    table_list = []
    tested = []
    for i in range(cap + 1):
        if i:
            table_list.append(table_at(bonds, i))
        checks = 0
        first_failure = None
        for candidate in preserving_generators(stage, table_list):
            checks += 1
            if not preserves_rows(candidate, stage, equations):
                first_failure = [(stage.labels[u], stage.labels[v]) for u, v in enumerate(candidate) if u != v]
                break
        tested.append({"order": i, "generators_checked": checks, "changes_equations": first_failure})
        if first_failure is None:
            return {"order": i, "decides_future": True, "tests": tested}
    return {"order": cap + 1, "decides_future": False, "tests": tested}


def literal_group_audit(stage, bonds):
    width = len(stage.labels)
    labels = tuple(range(width))
    movable = sorted(set(labels) - fixed_indices(stage))
    assert len(movable) <= 7
    all_maps = {tuple(dict(zip(movable, p)).get(x, x) for x in labels) for p in permutations(movable)}
    tables, reported = [], []
    for order in range(4):
        if order:
            table = table_at(bonds, order)
            tables.append(table)
            all_maps = {phi for phi in all_maps if all(table.get(mark) == table.get(tuple(sorted(phi[x] for x in mark)))
                                                        for mark in combinations(labels, order))}
        generators = list(preserving_generators(stage, tables))
        closure, todo = {labels}, [labels]
        while todo:
            head = todo.pop()
            for g in generators:
                action = tuple(head[g[x]] for x in labels)
                if action not in closure:
                    todo.append(action)
                    closure.add(action)
        assert closure == all_maps
        reported.append({"order": order, "full_group": len(all_maps), "generators": len(generators)})
    return reported


def archived_controls():
    summary = json.loads((SCALE_OUTPUT / "lower_native_center_summary_17.json").read_text())
    small = summary["least_observed"]["changes_equations"]["unrestricted"]["witness_at_min_width"]
    large = json.loads((SCALE_OUTPUT / "lower_probe_symmetric.json").read_text())["witnesses"]["least_junctions"]["replay"]
    results = []
    for order, supports, literal in [(2, small["current"], small["any_arity"]["permutation"]),
                                     (3, large["support_history"][1], large["map"])]:
        stage = Arrangement.parse(supports)
        named = dict(literal)
        index = {x: i for i, x in enumerate(stage.labels)}
        candidate = [index[named[x]] for x in stage.labels]
        assert all(candidate[z] == z for z in fixed_indices(stage))
        bonds, equations = independent_bonds(stage)
        assert not preserves_rows(candidate, stage, equations)
        counts = []
        for i in range(1, order + 1):
            table = table_at(bonds, i)
            assert all(table.get(tuple(sorted(candidate[z] for z in mark))) == value for mark, value in table.items())
            counts.append({"order": i, "all_entries": comb(len(stage.labels), i), "finite": len(table)})
        following, _ = advance(stage)
        assert following in {"next_open", "next_closes"}
        result = {"J": len(stage.stars), "n": len(stage.labels), "insufficient_order": order,
                  "finite_and_absent_checks": counts, "stage_sha256": fingerprint(stage)}
        if order == 2:
            result["literal_group_stabilizer_audit"] = literal_group_audit(stage, bonds)
            result["exact_strict_future_order"] = exact_order(stage, following)
            assert result["exact_strict_future_order"]["order"] == 3
        results.append(result)
    return results


def observed(stages, transitions, age, cap):
    if age >= len(stages):
        return {"status": f"unreached_{transitions[-1]}", "terminal_age": len(stages) - 1}
    stage = stages[age]
    future = transitions[age]
    return {"status": "reached", "J": len(stage.stars), "n": len(stage.labels), "future_status": future,
            "order": exact_order(stage, future, cap), "stage_sha256": fingerprint(stage), "rows": raw(stage)}


def census(m, cap):
    weightings = population(m)
    shapes = {}
    labelled = {}
    for links in sorted(set().union(*weightings.values())):
        shape = shape_id(m, links)
        history = trajectory(start_for(m, links))
        labelled[links] = shape
        if shape not in shapes:
            shapes[shape] = {"trajectory": history, "labelled_representative": links, "counts": {}}
            continue
        primary, transitions = shapes[shape]["trajectory"]
        replay, recalc = history
        assert transitions == recalc and len(primary) == len(replay)
        assert all(same_shape(a, b) for a, b in zip(primary, replay, strict=True))
    results = {}
    for shape in shapes.values():
        stages, transitions = shape.pop("trajectory")
        shape["first_round_status"] = transitions[0]
        shape["first_round_demand_deficits"] = demand_deficits(stages[0])
        shape["age_1_2"] = [observed(stages, transitions, age, cap) for age in (1, 2)]

    for key, samples in weightings.items():
        total = sum(samples.values())
        by_shape = Counter()
        for allocation, multiplicity in samples.items():
            by_shape[labelled[allocation]] += multiplicity
        summaries = []
        for age in (1, 2):
            statuses, future, orders = Counter(), Counter(), Counter()
            for code, count in by_shape.items():
                datum = shapes[code]["age_1_2"][age - 1]
                statuses[datum["status"]] += count
                if datum["status"] == "reached":
                    future[datum["future_status"]] += count
                    result = datum["order"]
                    label = str(result["order"]) if result["decides_future"] else f">={result['order']}"
                    orders[label] += count
            reached = statuses["reached"]
            assert sum(statuses.values()) == total and sum(future.values()) == sum(orders.values()) == reached
            summaries.append({"age": age, "generation_counts_by_status": dict(statuses),
                              "strict_future_by_status_if_reached": dict(future), "strict_order_if_reached": dict(orders),
                              "mass_reached": str(Fraction(reached, total)),
                              "order_probability_conditional_reached": {k: str(Fraction(v, reached)) for k, v in orders.items()}})
        results[key] = {"generation_outcomes": total, "distinct_labelled_starts": len(samples), "age_1_2": summaries}
        for shape, count in by_shape.items():
            shapes[shape]["counts"][key] = count
    material = [{"canonical_simple_start": shape, **values} for shape, values in sorted(shapes.items())]
    return {"m": m, "labelled_starts_replayed": len(labelled), "shapes": material, "weightings": results}


def sample_key(row):
    return row["weighting"], row["m"], row["replicate"], row["age"]


def audit_four_sample_cells(indexed, four):
    entries = {tuple(map(tuple, item["canonical_simple_start"])): item["age_1_2"] for item in four["shapes"]}
    checked, mass = [], defaultdict(Counter)
    for key, row in indexed.items():
        weighting, m, replicate, age = key
        if m != 4 or age != 0:
            continue
        allocation = tuple(map(tuple, row["ordinary_links"]))
        reference = entries[shape_id(m, allocation)]
        for i, expectation in enumerate(reference, 1):
            sample = indexed.get((weighting, m, replicate, i))
            if expectation["status"] != "reached":
                assert sample is None
                mass[weighting, i]["not_reached"] += 1
                continue
            assert sample is not None and expectation["order"]["decides_future"]
            stage = Arrangement.parse(sample["stars"])
            assert same_shape(stage, Arrangement.parse(expectation["rows"]))
            assert sample["can_grow"] == (expectation["future_status"] in {"next_open", "next_closes"})
            order = expectation["order"]["order"]
            mass[weighting, i][str(order)] += 1
            checked.append([weighting, m, replicate, i, order, fingerprint(stage)])
    return {"rows": sorted(checked), "counts_by_weighting_and_age": [[key, data] for key, data in sorted(mass.items())]}


def compare_engines(indexed, audit, shapes_path, result_paths):
    independent = {tuple(row[:4]): (row[4], row[5]) for row in audit["all_four_junction_start_cells_through_age_two"]["rows"]}
    for row in audit["rows"] + audit.get("targeted_interval_rows", []):
        assert row["order"]["decides_future"]
        pair = row["order"]["order"], row["stage_sha256"]
        assert independent.setdefault(sample_key(row), pair) == pair
    indexed_shapes = {}
    shapes = json.loads(shapes_path.read_text())["shapes"]
    for shape in shapes:
        for key in map(tuple, shape["observations"]):
            if key not in independent:
                continue
            assert key not in indexed_shapes
            actual = Arrangement.parse(indexed[key]["stars"])
            assert fingerprint(actual) == independent[key][1]
            assert same_shape(actual, Arrangement.parse(shape["stars"]))
            indexed_shapes[key] = str(shape["shape"])
    assert independent.keys() == indexed_shapes.keys()

    compared = []
    for path in result_paths:
        scores = json.loads(path.read_text())
        assert indexed_shapes.values() and all(s in scores for s in indexed_shapes.values())
        strict = Counter()
        contained = set()
        for key, (order, _) in independent.items():
            target = indexed_shapes[key]
            low, high = scores[target]["lo"], scores[target]["hi"]
            assert low <= order <= high, (key, target, order, low, high)
            strict["exact_agreement" if low == high else "interval_contains_exact_value"] += 1
            if low != high:
                contained.add((target, order, low, high))
        compared.append({"path": path.name, "sha256": sha256(path.read_bytes()).hexdigest(),
                         "observations": dict(strict), "distinct_shapes": len(set(indexed_shapes.values())),
                         "nonsingleton_intervals": sorted(contained)})
    return compared


def score_sample(indexed, key, cache_result, cap=3):
    row = indexed[key]
    start_row = indexed[(*key[:3], 0)]
    original = start_for(row["m"], tuple(map(tuple, start_row["ordinary_links"])))
    assert raw(original) == start_row["stars"]
    source = Arrangement.parse(indexed[(*key[:3], key[-1] - 1)]["stars"])
    stage = Arrangement.parse(row["stars"])
    round_replay(source, stage)
    _, produced = advance(source)
    assert produced is not None and same_shape(produced, stage)
    status, _ = advance(stage)
    assert row["next_round"]["status"] == {"demand_stall": "stalled", "closed": "closed",
                                            "next_open": "available", "next_closes": "available"}[status]
    assert row["J"] == len(stage.stars) and row["n"] == len(stage.labels)
    digest = fingerprint(stage)
    if digest not in cache_result or not cache_result[digest]["decides_future"]:
        cache_result[digest] = exact_order(stage, status, cap)
    return {"weighting": key[0], "m": key[1], "replicate": key[2], "age": key[3],
            "J": row["J"], "n": row["n"], "stage_sha256": digest, "future_status": status,
            "order": cache_result[digest]}


def audit_sample_stream(path, four, shapes_path=None, result_paths=(), max_j=15, max_n=48):
    """Audit in-cap stages selected by hash within weighting, size, age and next status."""
    indexed = {}
    buckets = defaultdict(list)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as handle:
        for line in handle:
            row = json.loads(line)
            if row["kind"] not in {"start", "stage"}:
                continue
            key = sample_key(row)
            assert key not in indexed
            indexed[key] = row
            if row["kind"] == "stage" and row["J"] <= max_j and row["n"] <= max_n:
                choice = sha256(json.dumps(key, separators=(",", ":")).encode()).hexdigest()
                weighting, m, _, age = key
                buckets[weighting, m, age, row["next_round"]["status"]].append((choice, key))
    by_literal_digest = {}
    scores = []
    for bucket, available in sorted(buckets.items()):
        _, key = min(available)
        row = indexed[key]
        assert bucket == (key[0], key[1], key[3], row["next_round"]["status"])
        scores.append(score_sample(indexed, key, by_literal_digest) | {"eligible_in_bucket": len(available)})
    audit = {"stage_file_sha256": sha256(path.read_bytes()).hexdigest(), "maximum_used_J": max_j,
             "maximum_used_n": max_n, "rows": scores, "distinct_literal_fingerprints": len(by_literal_digest),
             "all_four_junction_start_cells_through_age_two": audit_four_sample_cells(indexed, four)}
    if result_paths:
        first_scores = json.loads(result_paths[0].read_text())
        interval_probe = []
        for shape in json.loads(shapes_path.read_text())["shapes"]:
            if shape["J"] > max_j or shape["n"] > max_n:
                continue
            primary = first_scores[str(shape["shape"])]
            if primary["lo"] != primary["hi"]:
                assert primary["hi"] <= 4
                key = tuple(shape["observations"][0])
                report = score_sample(indexed, key, by_literal_digest, primary["hi"])
                interval_probe.append(report | {"shape": shape["shape"], "coarse_interval": [primary["lo"], primary["hi"]]})
        audit["targeted_interval_rows"] = interval_probe
        audit["reader_comparison"] = compare_engines(indexed, audit, shapes_path, result_paths)
    return audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--archived-only", action="store_true")
    parser.add_argument("--sample-stream", type=Path)
    parser.add_argument("--shape-index", type=Path)
    parser.add_argument("--reader-results", type=Path, action="append", default=[])
    args = parser.parse_args()
    if args.reader_results and (not args.sample_stream or not args.shape_index):
        parser.error("comparison requires --sample-stream and --shape-index")
    result = {"archived_controls": archived_controls()}
    if not args.archived_only:
        result["exhaustive_populations"] = [census(m, 3) for m in (4, 5)]
    if args.sample_stream:
        four = result["exhaustive_populations"][0] if not args.archived_only else census(4, 3)
        result["sample_audit"] = audit_sample_stream(args.sample_stream, four, args.shape_index, args.reader_results)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
