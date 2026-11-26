"""Replay growth readings and aggregate the retained stage and history rows."""

import argparse
from collections import Counter, defaultdict
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, permutations, product
import json
from math import inf
from pathlib import Path
from random import Random
from statistics import median
from time import process_time

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARCHIVE = ROOT / "artifacts"
INPUT = ARCHIVE / HERE.parent.name / f"{HERE.parent.name}-E001_operator_test"
REWIRE_SEEDS = range(2026112310, 2026112318)
REPLAY_SEED = 2026112601


def holdings(rows):
    result = defaultdict(list)
    for knot, row in enumerate(rows):
        for distinction in row:
            result[distinction].append(knot)
    return result


def source_from(meetings, loose_counts):
    rows = [[] for _ in loose_counts]
    for distinction, (a, b) in enumerate(meetings):
        rows[a].append(distinction)
        rows[b].append(distinction)
    next_name = len(meetings)
    for row, count in zip(rows, loose_counts, strict=True):
        row.extend(range(next_name, next_name + count))
        next_name += count
    return rows


def present_supply(rows):
    loose = [[] for _ in rows]
    shared = [set() for _ in rows]
    for distinction, owners in holdings(rows).items():
        if len(owners) == 1:
            loose[owners[0]].append(distinction)
        else:
            a, b = owners
            shared[a].add(b)
            shared[b].add(a)
    return loose, shared


def proposals(witnesses, payers):
    groups = {frozenset(witness & payers) for witness in witnesses}
    pairs = {pair for group in groups for pair in combinations(sorted(group), 2)}
    compatible = nx.Graph(pairs)
    larger = sorted(
        tuple(sorted(part))
        for part in nx.find_cliques(compatible)
        if len(part) >= 3 and not any(group.issuperset(part) for group in groups)
    )
    covered_pairs = {pair for part in larger for pair in combinations(part, 2)}
    return larger + sorted(pairs - covered_pairs)


def grow(start, law, horizon, cap):
    rows = [list(row) for row in start]
    next_name = max(d for row in rows for d in row) + 1
    stage_ends = [len(rows)]
    births = []
    outcome = "horizon"
    for _ in range(horizon):
        loose, shared = present_supply(rows)
        payers = {knot for knot, spendable in enumerate(loose) if spendable}
        if not payers:
            outcome = "closed"
            break
        parents = proposals(shared, payers)
        used = Counter(parent for group in parents for parent in group)
        if any(used[knot] > len(loose[knot]) for knot in payers):
            outcome = "stall"
            break
        parents.extend(
            (knot,)
            for knot in sorted(payers)
            for _ in range(len(loose[knot]) - used[knot])
        )
        if len(rows) + len(parents) > cap:
            outcome = "cap"
            break
        children = [set() for _ in rows]
        for child, group in enumerate(parents):
            for parent in group:
                children[parent].add(child)
        demand = Counter(child for group in proposals(children, set(range(len(parents)))) for child in group)
        closing = law == "parity" and len(parents) == 1
        step = []
        for child, group in enumerate(parents):
            new_count = 0 if closing else max(1, 3 - len(group), demand[child])
            rows.append([loose[parent].pop() for parent in group] + list(range(next_name, next_name + new_count)))
            next_name += new_count
            step.append((len(group), new_count))
        births.append(step)
        stage_ends.append(len(rows))
        if closing:
            outcome = "closed"
            break
    return rows, stage_ends, births, outcome


def rewire(start, births, seed):
    rows = [list(row) for row in start]
    loose, _ = present_supply(start)
    eligible = [knot for knot, spendable in enumerate(loose) if spendable]
    next_name = max(d for row in rows for d in row) + 1
    rng = Random(seed)
    missing_parents = 0
    short_births = 0
    for step in births:
        children = []
        for parent_count, fresh_count in step:
            parents = rng.sample(eligible, min(parent_count, len(eligible)))
            missing = parent_count - len(parents)
            missing_parents += missing
            short_births += bool(missing)
            paid = []
            for parent in parents:
                paid.append(loose[parent].pop())
                if not loose[parent]:
                    index = eligible.index(parent)
                    eligible[index] = eligible[-1]
                    eligible.pop()
            fresh = list(range(next_name, next_name + fresh_count))
            next_name += fresh_count
            if fresh:
                children.append(len(rows))
            rows.append(paid + fresh)
            loose.append(fresh)
        eligible.extend(children)
    return rows, missing_parents, short_births


def projected_graph(count, owners):
    # Removing loose distinctions and suppressing each shared distinction
    # preserves planarity when at most two knots hold a distinction.
    graph = nx.Graph()
    graph.add_nodes_from(range(count))
    if all(len(part) <= 2 for part in owners.values()):
        graph.add_edges_from(part for part in owners.values() if len(part) == 2)
    else:
        graph.add_edges_from(
            (knot, ("distinction", d)) for d, part in owners.items() for knot in part
        )
    return graph


def verdict(count, owners):
    return "pass" if nx.check_planarity(projected_graph(count, owners))[0] else "fail"


def stage(rows):
    owners = holdings(rows)
    graph = projected_graph(len(rows), owners)
    components = nx.number_connected_components(graph)
    links = sum(map(len, rows))
    return {
        "knots": len(rows),
        "distinctions": len(owners),
        "loose": sum(len(part) == 1 for part in owners.values()),
        "links": links,
        "parts": components,
        "loop_rank": links - len(rows) - len(owners) + components,
        "T": "pass" if nx.check_planarity(graph)[0] else "fail",
    }


def first_failure(rows, stage_ends, initial_verdict):
    if initial_verdict == "fail":
        return 0
    for t, end in enumerate(stage_ends[1:], 1):
        if verdict(end, holdings(rows[:end])) == "fail":
            return t
    return None


def literal_second_holder_mutant(rows):
    owners = holdings(rows)
    return verdict(len(rows), {d: knots[:1] + knots[2:] for d, knots in owners.items()})


def reconstruct_draws():
    rng = Random(2026112301)
    for arm, draw in product(range(4), range(256)):
        n = rng.randint(4, 8)
        word = [rng.randrange(n) for _ in range(n - 2)]
        multiplicity = Counter(word)
        meetings = []
        unused = set(range(n))
        for knot in word:
            leaf = min(k for k in unused if not multiplicity[k])
            meetings.append(tuple(sorted((leaf, knot))))
            unused.remove(leaf)
            multiplicity[knot] -= 1
        meetings.append(tuple(sorted(unused)))
        coins = [int(rng.randrange(4) == 0) for _ in range(n)]
        available = sorted(set(combinations(range(n), 2)) - set(meetings))
        extra = sorted(rng.sample(available, arm))
        meetings = sorted(meetings + extra)
        degree = Counter(knot for pair in meetings for knot in pair)
        loose_counts = [max(3 - degree[knot], 0) + coins[knot] for knot in range(n)]
        yield (arm, draw), (source_from(meetings, loose_counts), meetings, loose_counts, extra)


def named_sources():
    # Inputs are the holdings given in the source records.
    seven = [(0, 1), (0, 4), (1, 4), (2, 4), (2, 6), (3, 4), (3, 5), (5, 6), (0, 1)]
    nine = [(0, 2), (0, 3), (0, 5), (1, 2), (2, 7), (3, 8), (4, 5), (4, 8), (5, 6), (6, 7)]
    founder_count = [2, 1, 1, 1, 3]
    five = [(i, (i + 1) % 5) for i, count in enumerate(founder_count) for _ in range(count)]
    witnessed_pairs = [
        ("v", "r1"), ("r1", "r2"), ("r2", "r3"), ("r3", "v"), ("v", "s"), ("t", "v"),
        ("s", "b0"), ("t", "b0"), ("s", "b1"), ("b1", "t"), ("t", "b2"), ("b2", "s"),
    ]
    witnesses = [f"w{i}" for i in range(len(witnessed_pairs))]
    names = sorted({knot for pair in witnessed_pairs for knot in pair} | set(witnesses))
    index = {name: i for i, name in enumerate(names)}
    twenty_one = [
        (index[knot], index[witness])
        for (a, b), witness in zip(witnessed_pairs, witnesses, strict=True)
        for knot in (a, b, b)
    ]
    opened = Counter(knot for pair in witnessed_pairs for knot in pair)
    sources = {
        "seven_knot": source_from(seven, [3, 0, 3, 3, 3, 2, 2]),
        "nine_knot_drawn": source_from(nine, [5, 2, 4, 3, 3, 4, 3, 3, 2]),
        "knots21_two_clocks": source_from(twenty_one, [opened[name] for name in names]),
        "five_founder_clock": source_from(five, [2] * 5),
    }
    record = next((ARCHIVE / "HEAVY-GROWTH-20261119-001").glob("*/sources_audit.json"))
    archived = json.loads(record.read_text())["named_archive_starts"]
    for name in ("start-00", "start-04", "start-13"):
        data = archived[name]
        degree = Counter(knot for pair in data["meetings"] for knot in pair)
        sources[f"archive_{name}"] = source_from(
            data["meetings"], [size - degree[knot] for knot, size in enumerate(data["sizes"])]
        )
    return sources


def cubic_benchmark():
    rows = [[0, 1, 2]]
    supply = {0: rows[0].copy()}
    next_name = 3
    yield 0, stage(rows)
    for depth in range(1, 7):
        loose, shared = present_supply(rows)
        assert {knot for knot, row in enumerate(loose) if row} == supply.keys()
        groups = proposals(shared, set(supply))
        assert all(len(group) <= 3 for group in groups)
        used = Counter(knot for group in groups for knot in group)
        assert all(used[knot] <= 3 for knot in supply)
        groups += [(knot,) for knot in supply for _ in range(3 - used[knot])]
        next_supply = {}
        for group in groups:
            fresh = list(range(next_name, next_name + 3))
            next_name += 3
            next_supply[len(rows)] = fresh
            rows.append([supply[parent].pop() for parent in group] + fresh)
        assert not any(supply.values())
        supply = next_supply
        yield depth, stage(rows)


def bounded_bond_benchmark(depth):
    offsets = (((0, 0), (0, 1), (1, 0)), ((0, 0), (0, 2), (1, 2)))
    locations = {location: i for i, location in enumerate(product(range(-depth, depth + 1), repeat=2))}
    rows = []
    for x, y in locations:
        for kind in offsets:
            members = [(x + dx, y + dy) for dx, dy in kind]
            if all(member in locations for member in members):
                rows.append([locations[member] for member in members])
    return rows


def read_archive():
    stages_by_rank = defaultdict(Counter)
    by_population = defaultdict(Counter)
    rank_by_population = defaultdict(lambda: defaultdict(Counter))
    benchmark = {}
    sources = {}
    draws = {}
    draw_stages = defaultdict(dict)
    source_stages = defaultdict(dict)
    for path in sorted(INPUT.glob("p[123]_*.jsonl")):
        for line in path.read_text().splitlines():
            row = json.loads(line)
            group = row["population"]
            by_population[group][row["kind"]] += 1
            if row["kind"] == "stage":
                stages_by_rank[row["loop_rank"]][row["T"]] += 1
                rank_by_population[group][row["loop_rank"]][row["T"]] += 1
                if group == "P1":
                    benchmark[row["construction"], row["depth"]] = row
                elif group == "P2":
                    source_stages[row["source"], row["law"]][row["t"]] = row
                else:
                    draw_stages[row["law"], row["arm"], row["draw"]][row["t"]] = row
            elif row["kind"] == "history":
                if group == "P2":
                    sources[row["source"], row["law"]] = row
                else:
                    draws[row["law"], row["arm"], row["draw"]] = row
    return stages_by_rank, by_population, rank_by_population, benchmark, sources, draws, draw_stages, source_stages


def summarize_draws(draws, draw_stages):
    outcomes = defaultdict(Counter)
    comparisons = defaultdict(Counter)
    exceptions = []
    rank_examples = {}
    for key, row in draws.items():
        law, arm, draw = key
        stages = draw_stages[key]
        failing = [t for t, item in stages.items() if item["T"] == "fail"]
        first = min(failing, default=None)
        assert first == row["first_failing_step"]
        assert list(stages) == list(range(row["steps"] + 1))
        assert [item["knots"] for item in stages.values()] == row["n_at"]
        assert not failing or failing == list(range(first, row["steps"] + 1))
        for t, item in stages.items():
            if item["loop_rank"] == 5 and item["T"] not in rank_examples:
                rank_examples[item["T"]] = {"law": law, "arm": arm, "draw": draw, "t": t, **item}
        outcomes[law]["histories"] += 1
        outcomes[law]["funded"] += bool(row["steps"])
        outcomes[law]["passing_funded_reached_stages"] += bool(row["steps"] and first is None)
        outcomes[law]["passing_funded_reached_step_12"] += row["steps"] == 12 and first is None
        outcomes[law]["failed_funded"] += bool(row["steps"] and first is not None)
        if row["steps"] and row["outcome"] == "closed":
            outcomes[law][f"funded_closed_step_{row['steps']}_{'pass' if first is None else 'fail'}"] += 1
        if not row["steps"]:
            continue
        start_failure = inf if first is None else first
        failures = [inf if r["first_failing_step"] is None else r["first_failing_step"] for r in row["rewired"]]
        assert [r["seed"] for r in row["rewired"]] == list(REWIRE_SEEDS)
        short = sum(r["shortfall"] for r in row["rewired"])
        qualified = min(start_failure, *failures) < inf
        median_failure = median(failures)
        for label in (law, "both"):
            counts = comparisons[label]
            counts["replicas"] += len(failures)
            counts["replicas_with_shortfall"] += sum(bool(r["shortfall"]) for r in row["rewired"])
            counts["missing_parents"] += short
            counts["histories_affected_by_shortfalls"] += bool(short)
            counts["qualifying_histories"] += qualified
            counts["no_earlier_than_median"] += qualified and start_failure >= median_failure
            counts["qualifying_histories_no_shortfall"] += qualified and not short
            counts["no_earlier_than_median_no_shortfall"] += qualified and not short and start_failure >= median_failure
            counts["qualifying_ordinary_pass_all_stages"] += qualified and start_failure == inf
            counts["ordinary_pass_all_eight_rewirings_fail"] += start_failure == inf and max(failures) < inf
            counts["median_failure_step_2_to_4"] += qualified and 2 <= median_failure <= 4
            counts["ordinary_pass_median_failure_step_2_to_4"] += start_failure == inf and 2 <= median_failure <= 4
            counts["qualifying_infinite_median"] += qualified and median_failure == inf
        if start_failure < median_failure:
            exceptions.append({"law": law, "arm": arm, "draw": draw, "first_failure": first,
                               "rewired_failures": [r["first_failing_step"] for r in row["rewired"]]})
    return {"outcomes": outcomes, "comparisons": comparisons, "exceptions": exceptions, "rank_5_examples": rank_examples}


def rebuild_draw(key, spec, history, stored_stages):
    law, _, _ = key
    start, meetings, opens, extra = spec
    assert [list(pair) for pair in meetings] == history["meetings"], key
    assert [list(pair) for pair in extra] == history["extra_meetings"], key
    assert opens == history["opens"], key
    rows, ends, births, outcome = grow(start, law, 12, 5000)
    assert ends == history["n_at"] and outcome == history["outcome"], key
    assert list(map(len, births)) == history["births_per_step"], key
    readings = [stage(rows[:end]) for end in ends]
    for t, reading in enumerate(readings):
        assert all(stored_stages[t][field] == value for field, value in reading.items()), (key, t, reading)
        step = births[t - 1] if t else []
        assert stored_stages[t]["one_parent_births"] == sum(p == 1 for p, _ in step), (key, t)
    assert next((t for t, row in enumerate(readings) if row["T"] == "fail"), None) == history["first_failing_step"]
    replayed = 0
    if births:
        for observed in history["rewired"]:
            replica, short, short_births = rewire(start, births, observed["seed"])
            failure = first_failure(replica, ends, readings[0]["T"])
            assert (failure, short, short_births) == (
                observed["first_failing_step"], observed["shortfall"], observed["births_with_shortfall"]
            ), (key, observed, failure, short, short_births)
            replayed += 1
    return len(readings), bool(births), replayed


def rebuild_sources(pilot, histories, stored_stages):
    output = {}
    cases = named_sources()
    selected = cases if not pilot else {"knots21_two_clocks": cases["knots21_two_clocks"]}
    for source, start in selected.items():
        output[source] = {}
        for law in ("parity", "nae"):
            rows, ends, _, _ = grow(start, law, 2, 20000)
            readings = [stage(rows[:end]) for end in ends]
            first = next(t for t, row in enumerate(readings) if row["T"] == "fail")
            for t, values in enumerate(readings):
                recorded = stored_stages[source, law][t]
                assert all(recorded[field] == value for field, value in values.items()), (source, law, t)
            assert first == histories[source, law]["first_failing_step"]
            output[source][law] = {
                "first_failure": first, "first_failure_knots": readings[first]["knots"],
                "reconstructed": readings, "archived_horizon": histories[source, law]["steps"],
            }
    return output


def benchmark_builders():
    # Use the independent source definitions for the two substitutions.
    path = next((ROOT / "experiments" / "GROWTH-STATISTICS-20261121-001A").glob("*/sources.py"))
    spec = spec_from_file_location("benchmark_definitions", path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.planar_pattern


def rebuild_benchmark(pilot, benchmark):
    readings = {}
    builders = benchmark_builders()
    for name, depth in sorted(benchmark):
        if name == "cubic":
            continue
        if pilot and (name, depth) not in {("pinwheel", 5), ("periodic", 8), ("bounded_bond", 4)}:
            continue
        rows = bounded_bond_benchmark(depth) if name == "bounded_bond" else builders(name, depth).knots
        readings[name, depth] = stage(rows)
        if name == "bounded_bond":
            readings[name, depth]["literal_second_holder_mutant"] = literal_second_holder_mutant(rows)
    readings.update({("cubic", depth): reading for depth, reading in cubic_benchmark()})
    results = defaultdict(dict)
    for (name, depth), row in readings.items():
        assert all(benchmark[name, depth][field] == value for field, value in row.items()
                   if field != "literal_second_holder_mutant"), (name, depth, row)
        results[name][depth] = row
    return results


def one_parent_counterexample():
    initial = source_from(list(product(range(3), range(3, 6))), [1, 0, 0, 0, 0, 0])
    rows, ends, births, outcome = grow(initial, "parity", 12, 5000)
    return {
        "initial_holdings": initial,
        "outcome": outcome,
        "parent_and_fresh_counts": births,
        "stage_verdicts": [stage(rows[:end])["T"] for end in ends],
    }


def five_founder_witness():
    rows, _, _, _ = grow(named_sources()["five_founder_clock"], "parity", 1, 20000)
    graph = projected_graph(len(rows), holdings(rows))
    for partners in permutations(range(5, 10)):
        groups = list(enumerate(partners))
        if all(graph.has_edge(*group) for group in groups) and all(
            any(graph.has_edge(a, b) for a, b in product(left, right))
            for left, right in combinations(groups, 2)
        ):
            return groups
    raise AssertionError("No five pairwise meeting groups found")


def bounded_bond_removal_example():
    rows = bounded_bond_benchmark(2)
    owners = holdings(rows)
    pairs = {pair for part in owners.values() for pair in combinations(part, 2)}
    claimed_lower = len(pairs) - (3 * len(rows) - 6)
    removed = []
    graph = projected_graph(len(rows), owners)
    while True:
        passes, witness = nx.check_planarity(graph, counterexample=True)
        if passes:
            break
        distinction_nodes = [node for node in witness if isinstance(node, tuple)]
        chosen = max(distinction_nodes, key=lambda node: (graph.degree(node), -node[1]))
        graph.remove_node(chosen)
        removed.append(chosen[1])
    assert len(removed) < claimed_lower
    return {"claimed_lower": claimed_lower, "distinct_sharing_pairs": len(pairs), "removed_distinctions": removed}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("pilot", "full", "sample"), required=True)
    args = parser.parse_args()
    pilot = args.mode == "pilot"
    begin = process_time()
    rank, population, rank_by_population, benchmark, sources, draws, draw_stages, source_stages = read_archive()
    result = {
        "mode": args.mode,
        "archived_rows": population,
        "archived_draw_summary": summarize_draws(draws, draw_stages),
        "archived_ranks": {
            "distinct_ranks": len(rank),
            "mixed_ranks": sum(len(counts) == 2 for counts in rank.values()),
            "mixed_ranks_by_population": {
                group: sum(len(counts) == 2 for counts in values.values())
                for group, values in rank_by_population.items()
            },
            "ranks_0_to_4": {r: rank[r] for r in range(5)},
            "least_failing_rank": min(r for r, counts in rank.items() if counts.get("fail")),
        },
    }
    timings = {"aggregate_cpu_s": process_time() - begin}
    begin = process_time()
    result["rebuilt_source_prefixes"] = rebuild_sources(pilot, sources, source_stages)
    timings["sources_cpu_s"] = process_time() - begin
    begin = process_time()
    result["rebuilt_benchmark"] = rebuild_benchmark(pilot, benchmark)
    timings["benchmark_cpu_s"] = process_time() - begin
    begin = process_time()
    specs = dict(reconstruct_draws())
    keys = sorted(draws)
    if pilot:
        random_funded = set(Random(REPLAY_SEED).sample([key for key in keys if draws[key]["steps"]], 16))
        longest = set(sorted(keys, key=lambda key: draws[key]["n_at"][-1])[-8:])
        keys = sorted(random_funded | longest | {("parity", 2, 180), ("nae", 2, 180)})
    elif args.mode == "sample":
        rng = Random(REPLAY_SEED)
        draws_sample = {
            (arm, draw)
            for arm in range(4)
            for draw in rng.sample(range(256), 80)
        }
        draws_sample.add((2, 180))
        keys = [key for key in keys if key[1:] in draws_sample]
    totals = Counter()
    for key in keys:
        count, funded, rewired = rebuild_draw(key, specs[key[1:]], draws[key], draw_stages[key])
        totals["histories"] += 1
        totals["funded_histories"] += funded
        totals["stages"] += count
        totals["rewirings"] += rewired
    result["rebuilt_draw_counts"] = totals
    result["rebuilt_draw_scope"] = {"keys": keys if args.mode != "full" else "all", "sample_seed": REPLAY_SEED}
    timings["fresh_draws_cpu_s"] = process_time() - begin
    result["one_parent_counterexample"] = one_parent_counterexample()
    result["five_founder_pairwise_meeting_groups"] = five_founder_witness()
    result["bounded_bond_removal_counterexample"] = bounded_bond_removal_example()
    result["timings"] = timings
    target = HERE / f"growth_readings_{args.mode}.json"
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": target.name, "counts": totals, "timings": timings}, sort_keys=True))


if __name__ == "__main__":
    main()
