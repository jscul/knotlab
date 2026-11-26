"""Read the per-run records for Parts 1, 4 and 5 and the closing diagnostic.

Construct the census and its weights from the declared atlas and loose counts.
The records retain per-run observations, not full birth or retirement traces.
This audit checks those observations and recounts their strata.
"""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import gzip
from itertools import combinations, islice, permutations, product
import json
from math import factorial
from pathlib import Path
import random
from time import perf_counter

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = "DESCENT-HELD-20261125-001A"
ARTIFACTS = ROOT / "artifacts" / TICKET / (TICKET + "-E001_order_in_own_places")
REGISTRATION = ROOT / "research" / TICKET
FORMS = ("PU", "PB", "BB")
THIRD_COUNT_LAWS = {
    "RATION-3, waiting": "R3W",
    "FLOOR1, waiting": "F1W",
    "FLOOR1, offshoots": "F1O",
    "FLOOR1, retiring": "F1R",
    "RATION-3, waiting, HOLD": "H-R3W",
    "FLOOR1, offshoots, HOLD": "H-F1O",
    "FLOOR1, retiring, HOLD": "H-F1R",
}


@dataclass(frozen=True, slots=True)
class Start:
    atlas_index: int
    loose: tuple
    agrees: bool
    kept: bool
    weight: int

    @property
    def size(self):
        return len(self.loose)


def read(path):
    with path.open() as stream:
        return json.load(stream)


def rows(path, field, limit=None):
    """Iterate over a named array of objects or arrays in a source record."""
    open_text = gzip.open if path.suffix == ".gz" else open
    field_marker = f'"{field}"'
    decoder = json.JSONDecoder()
    with open_text(path, "rt") as stream:
        buffer = ""
        while field_marker not in buffer:
            more = stream.read(128 * 1024)
            if not more:
                raise ValueError(f"Missing {field} in {path}")
            buffer = buffer[-len(field_marker):] + more
        buffer = buffer.split(field_marker, 1)[1].lstrip()
        while "[" not in buffer:
            more = stream.read(128 * 1024)
            if not more:
                raise ValueError(f"Missing array for {field} in {path}")
            buffer += more
        buffer = buffer.split("[", 1)[1]
        emitted = 0
        while limit is None or emitted < limit:
            buffer = buffer.lstrip(", \t\r\n")
            if buffer.startswith("]"):
                return
            try:
                value, end = decoder.raw_decode(buffer)
            except json.JSONDecodeError:
                more = stream.read(128 * 1024)
                if not more:
                    raise
                buffer += more
                continue
            yield value
            emitted += 1
            buffer = buffer[end:]


def census(atlas, size):
    """Keep one loose-count tuple per renaming and record its labelled weight.

    For parity, a row sum supported on a knot's places can include a component
    of the other knots only as a whole, and only if it has no loose distinction.
    Such a component would constrain a proper subset of the target's places.
    Connectedness and at least one loose distinction ensure this subset is
    proper. The target's own row constrains the whole, and zero is allowed.
    """
    knots = range(size)
    for atlas_index, graph in enumerate(atlas):
        if len(graph) != size or not nx.is_connected(graph):
            continue
        meetings = [(u, v) for u, v in combinations(knots, 2) if graph.has_edge(u, v)]
        renamings = [
            order for order in permutations(knots)
            if all(graph.has_edge(order[u], order[v]) for u, v in meetings)
        ]
        degree = [graph.degree(u) for u in knots]
        components = {
            sum(1 << u for u in part)
            for removed in knots
            for part in nx.connected_components(graph.subgraph([u for u in knots if u != removed]))
        }
        seen = set()
        for loose in product(*(range(max(0, 3 - d), 4) for d in degree)):
            if not any(loose) or loose in seen:
                continue
            orbit = {tuple(loose[u] for u in order) for order in renamings}
            seen.update(orbit)
            live = sum(1 << u for u in knots if loose[u])
            weight, remainder = divmod(factorial(size) * len(orbit), len(renamings))
            assert not remainder
            counts = [(degree[u] + loose[u]) % 3 for u in knots]
            agrees = all(counts[u] == counts[v] for u, v in meetings)
            yield Start(atlas_index, loose, agrees, all(live & part for part in components), weight)


def places(start, atlas):
    graph = atlas[start.atlas_index]
    stars = [[] for _ in start.loose]
    distinction = 0
    for u, v in combinations(range(start.size), 2):
        if graph.has_edge(u, v):
            stars[u].append(distinction)
            stars[v].append(distinction)
            distinction += 1
    for knot, count in enumerate(start.loose):
        stars[knot].extend(range(distinction, distinction + count))
        distinction += count
    return stars


def shares(weights, selected):
    return {
        "census": [len(selected), len(weights)],
        "labelled": [sum(weights[idx] for idx in selected), sum(weights.values())],
    }


def tally_base(by_start, weights, checks, full=True):
    counted = {idx for idx, row in by_start.items() if row["counted"]}
    bprime = {idx for idx, row in by_start.items() if row["bprime_fails"]}
    waiting = {idx for idx, row in by_start.items() if row["lq_fails_rounds"]}
    result = {
        "different_parent_steps": shares(weights, counted),
        "different_parent_steps_counted_in_threes": shares(weights, bprime),
        "different_parent_steps_greatest_difference": dict(
            Counter(by_start[idx]["greatest"] for idx in counted)
        ),
        "first_round_with_different_parent_steps": dict(
            Counter(by_start[idx]["counted_first_round"] for idx in counted)
        ),
        "greatest_difference_all_starts": dict(Counter(row["greatest"] for row in by_start.values())),
        "end": dict(Counter(row["end"] for row in by_start.values())),
        "waiting_condition_fails": shares(weights, waiting),
        "counted_and_waiting_condition_fails": shares(weights, counted & waiting),
        "counted_and_waiting_condition_holds": shares(weights, counted - waiting),
        "different_parent_steps_but_equal_counted_in_threes": len(counted - bprime),
    }
    for idx, row in by_start.items():
        checks["counted_disagrees_with_greatest_difference"] += row["counted"] != (row["greatest"] > 1)
        checks["threes_disagree_with_greatest_difference_at_most_three"] += (
            row["greatest"] <= 3 and row["bprime_fails"] != row["counted"]
        )
    if not full:
        return result, counted

    fives = {idx for idx, row in by_start.items() if row["fives_right_on"]}
    by_round = Counter()
    counted_by_round = Counter()
    first_no_birth = {}
    for idx, row in by_start.items():
        last = row["greatest_by_round"]
        checks["greatest_disagrees_with_rounds"] += row["greatest"] != max(last.values(), default=0)
        checks["fives_disagree_with_greatest_difference_at_most_three"] += (
            row["greatest"] <= 3 and row["fives_right_on"] != (row["greatest"] <= 2)
        )
        checks["threes_stamp_disagrees_with_parent_steps_counted_in_threes"] += (
            row["three_stamp_right_on"] == row["bprime_fails"]
        )
        if row["first_no_birth_round"] is not None:
            first_no_birth[idx] = row["first_no_birth_round"]
        for round_number, difference in last.items():
            key = f"{round_number}:{difference}"
            by_round[key] += 1
            counted_by_round[key] += idx in counted
    stop_swap_counted = {
        idx for idx in counted
        if idx not in first_no_birth or by_start[idx]["counted_first_round"] < first_no_birth[idx]
    }
    stop_swap_record = {idx for idx, row in by_start.items() if row["alt_stop"]["counted"]}
    checks["stopping_swap_counted_disagrees"] += len(stop_swap_counted ^ stop_swap_record)
    result.update({
        "greatest_by_round": dict(by_round),
        "greatest_by_round_among_counted": dict(counted_by_round),
        "fives_right_among_counted": shares({idx: weights[idx] for idx in counted}, fives & counted),
        "fives_right_among_all": shares(weights, fives),
        "fives_right_with_greatest_difference_zero_or_one": sum(by_start[idx]["greatest"] < 2 for idx in fives),
        "stopping_swap_counted": shares(weights, stop_swap_counted),
        "only_counted_with_registered_stopping": [
            {"index": idx, "no_birth_round": first_no_birth[idx],
             "first_different_parent_steps_round": by_start[idx]["counted_first_round"]}
            for idx in sorted(counted - stop_swap_counted)
        ],
    })
    return result, counted


def part_one(raw, all_starts, laws, checks):
    populations = {"parity": {}, "nae": {}}
    by_law = defaultdict(dict)
    for row in raw:
        idx = row["idx"]
        start = all_starts[idx]
        checks["census_row_metadata_disagrees"] += (
            (start.size, start.kept, start.weight, start.agrees)
            != (row["n"], row["kept"], row["w"], row["a_places"])
        )
        for knot_law, population in populations.items():
            if start.kept or knot_law == "nae":
                population[idx] = start.weight
        for key, record in row["base"].items():
            by_law[key][idx] = record

    output = {}
    counted = {}
    for law in laws:
        for knot_law, weights in populations.items():
            key = f"{law}|{knot_law}"
            assert set(by_law[key]) == set(weights), key
            result, counted[key] = tally_base(by_law[key], weights, checks)
            result["different_parent_steps_by_start_size"] = {
                size: shares({idx: w for idx, w in weights.items() if all_starts[idx].size == size},
                             {idx for idx in counted[key] if all_starts[idx].size == size})
                for size in range(1, 6)
            }
            output[key] = result
        parity, nae = counted[f"{law}|parity"], counted[f"{law}|nae"]
        output[f"{law}|nae"]["counted_indices_differ_from_parity"] = sorted(parity ^ nae)
        output[f"{law}|nae"]["counted_among_set_aside"] = sorted(idx for idx in nae if not all_starts[idx].kept)
    return output, by_law, counted


def scope_of_fives_total(base, counted):
    keys = ("R3W|parity", "C3W|parity", "C3WF|parity", "F1W|parity")
    weighted_pairs = [base[key]["fives_right_among_counted"] for key in keys]
    return {
        "fives_right_among_counted_start_law_pairs": {
            weighting: [sum(pair[weighting][i] for pair in weighted_pairs) for i in (0, 1)]
            for weighting in ("census", "labelled")
        },
        "different_starts_among_counted_pairs": len(set().union(*(counted[key] for key in keys))),
    }


def threshold(part_five, by_law, recorded, checks):
    output = {}
    for law in recorded:
        base = by_law[f"{law}|parity"]
        retained = {row["idx"]: row["laws"][law] for row in part_five}
        assert retained.keys() == base.keys(), law
        classes = defaultdict(Counter)
        fail_rounds = Counter()
        fail_kinds = Counter()
        fail_rounds_when_reaching_three = Counter()
        alternate_law = Counter()
        exceptions = []
        for idx, short_run in retained.items():
            full_run = base[idx]
            steps = full_run["max_ps"]
            first_fail = short_run["round"]
            alternate_first = full_run["m2_fail_round_every"]
            checks["part_five_and_part_one_first_failure_disagree"] += (
                first_fail != full_run["m2_fail_round_some"]
            )
            classes[steps]["runs"] += 1
            classes[steps]["some_parent_fails"] += first_fail is not None
            classes[steps]["every_parent_fails_at_one_birth"] += alternate_first is not None
            if first_fail is not None:
                fail_rounds[first_fail] += 1
                fail_kinds.update(short_run["failing_births"])
            if steps >= 3:
                alternate_law["every_parent_fails_at_one_birth"] += alternate_first is not None
                alternate_law["some_and_every_first_round_differ"] += first_fail != alternate_first
                if first_fail is None:
                    exceptions.append(idx)
                else:
                    fail_rounds_when_reaching_three[first_fail] += 1
                    alternate_law["first_failure_before_reaching_three"] += short_run["max_ps"] < 3
            if first_fail is None:
                checks["part_five_and_part_one_depth_of_a_run_that_holds_disagree"] += (
                    short_run["max_ps"] != steps
                )
        output[law] = {
            "population": len(retained),
            "by_maximum_parent_steps": {steps: dict(counts) for steps, counts in classes.items()},
            "first_failure_by_round": dict(fail_rounds),
            "failing_birth_kind_at_first_round": dict(fail_kinds),
            "reaches_three": sum(counts["runs"] for steps, counts in classes.items() if steps >= 3),
            "reaches_three_and_first_failure_by_round": dict(fail_rounds_when_reaching_three),
            "reaches_three_with_no_failure_indices": exceptions,
            "among_runs_reaching_three": dict(alternate_law),
        }
    return output


def threshold_totals(by_law):
    first_failure = Counter()
    threshold_stats = Counter()
    exact_depth = defaultdict(Counter)
    for record in by_law.values():
        first_failure.update(record["reaches_three_and_first_failure_by_round"])
        threshold_stats.update(record["among_runs_reaching_three"])
        for depth, counts in record["by_maximum_parent_steps"].items():
            exact_depth[depth].update(counts)
    return {
        "population_start_law_pairs": sum(record["population"] for record in by_law.values()),
        "reaches_three_and_first_failure_by_round": first_failure,
        "among_runs_reaching_three": threshold_stats,
        "by_maximum_parent_steps": dict(exact_depth),
    }


def count_form_run(result, examples, record, law, form, label, start_agrees, checks):
    a, bprime, c, d = (record[key] for key in ("a", "bprime", "c", "d"))
    checks["a_disagrees_with_start"] += a != (form == "BB" or start_agrees)
    checks["bprime_disagrees_with_recorded_birth_count"] += bprime != (record["bprime_births"] == 0)
    checks["d_disagrees_with_closing_counterfactual"] += d != all(s == 0 for s in record["closing_hyp_s"])

    right = record["right_on_every_structure"]
    last = record["place_rule_last_by_kind"]
    wrong_last = sum(wrong for _, wrong in last.values())
    places_last = sum(right_count + wrong for right_count, wrong in last.values())
    checks["right_disagrees_with_first_wrong_round"] += right != (record["first_round_with_a_wrong_place"] is None)
    if form != "BB" or not record["retired_knots"]:
        checks["right_disagrees_with_fixed_counts_and_final_places"] += right != (wrong_last == 0)
        checks["c_disagrees_with_fixed_counts"] += not c

    result["runs"] += 1
    result["right"] += right
    result["bprime_false_and_right"] += not bprime and right
    result["bprime_false"] += not bprime
    eligible = {
        "P3": a and bprime and c and d,
        "P4": a and not bprime and c and d,
        "P5": form in ("PU", "PB") and not a,
        "P6": form == "BB" and law["treatment"] == "CANCEL-RETIRE" and a and bprime and d,
    }
    for prediction, applies in eligible.items():
        verdict = record[prediction]
        checks[f"{prediction}_eligibility_disagrees"] += applies != (verdict is not None)
        result[f"{prediction}_eligible"] += applies
        result[f"{prediction}_recorded_failure"] += verdict is False

    if eligible["P3"]:
        result["P3_wrong"] += not right
        result["P3_no_birth"] += record["new_knots"] == 0
        result["P3_no_shared_place"] += places_last == 0
        result["P3_no_parent_place"] += sum(last["parent"]) == 0
    if eligible["P4"]:
        result["P4_right"] += right
        result["P4_reported_sets_equal"] += record["counted_step3_equals_bprime_births"]
        result["P4_no_birth_counted_at_step_3"] += record["counted_step3"] == 0
        if "P4_first_births_counted" in record:
            result["P4_first_round_flag_retained"] += 1
            result["P4_first_round_flag_false"] += not record["P4_first_births_counted"]
        elif not record["counted_step3_equals_bprime_births"]:
            result["P4_first_round_flag_unavailable_without_equal_sets"] += 1
    if eligible["P5"]:
        result["P5_no_wrong_start_place"] += last["start"][1] == 0
        result["P5_no_birth"] += record["new_knots"] == 0
    if form == "BB" and law["treatment"] == "CANCEL-RETIRE":
        key = f"c_{str(c).lower()}_right_{str(right).lower()}"
        result[key] += 1
        if not c and right and len(examples["BB_retiring_c_false_and_right"]) < 4:
            examples["BB_retiring_c_false_and_right"].append({
                **label,
                "new_knots": record["new_knots"],
                "retired_knots": record["retired_knots"],
                "places_between_start_knots_checked_at_end": sum(last["start"]),
            })
        if eligible["P6"]:
            result[f"P6_{key}"] += 1
            result["P6_with_retirement"] += record["retired_knots"] > 0
            result["P6_without_retirement"] += record["retired_knots"] == 0
            result["P6_no_birth"] += record["new_knots"] == 0
            result["P6_wrong_in_last_structure"] += wrong_last > 0
            result["P6_wrong_before_last_structure_only"] += not right and wrong_last == 0
            records = record.get("P6_rows", [])
            result["P6_runs_with_round_rows"] += bool(records)
            result["P6_round_rows"] += len(records)
            result["P6_round_rows_predicting_a_wrong_place"] += sum(row["predicted"] > 0 for row in records)
            result["P6_round_rows_with_mismatch"] += sum(
                not row["equal"] or row["wrong"] != row["predicted"] for row in records
            )


def arm_w(census_rows, named_rows, laws, all_starts, named, checks):
    results = {part: defaultdict(Counter) for part in ("census", "named")}
    examples = defaultdict(list)
    for row in census_rows:
        idx = row["idx"]
        for key, record in row["armw"].items():
            law, form = key.split("|")
            count_form_run(results["census"][key], examples, record, laws[law], form,
                           {"census_index": idx, "law": law, "form": form}, all_starts[idx].agrees, checks)
    for row in named_rows:
        start_stars = named[row["start"]]["stars"]
        agrees = all((len(x) - len(y)) % 3 == 0 for x, y in combinations(start_stars, 2) if set(x) & set(y))
        checks["named_start_a_disagrees_with_start_definition"] += agrees != named[row["start"]]["start_values_agree"]
        for form in FORMS:
            law = row["law"]
            key = f'{law}|{row["knot_law"]}|{form}'
            count_form_run(results["named"][key], examples, row["forms"][form], laws[law], form,
                           {"named_start": row["start"], "law": law, "form": form,
                            "knot_law": row["knot_law"]}, agrees, checks)
    totals = {part: Counter() for part in results}
    for part, table in results.items():
        for counts in table.values():
            totals[part].update(counts)
    return {"totals": totals, "by_law_form": results, "examples": examples}


def closing_readings(census_rows, all_starts, atlas, expected, checks):
    weights = {idx: start.weight for idx, start in enumerate(all_starts) if start.kept}
    by_form = defaultdict(lambda: {"all": set(), "own": set(), "both": set(), "closing_checked": 0})
    for row in census_rows:
        idx = row["idx"]
        for key, run in row["armw"].items():
            groups = by_form[key]
            if run["right_on_every_structure"]:
                for reading in ("all", "own", "both"):
                    groups[reading].add(idx)
                continue
            if not run["closing_births"]:
                continue
            groups["closing_checked"] += 1
            # The closing birth is last and there can have been no retirement.
            # A wrong start place or a mix of parent counts before closing
            # already witnesses a wrong place with neither holder closing.
            # Otherwise agreement and fixed counts give correctness up to the
            # closing birth. Only the kind of its wrong places is then needed.
            assert run["closing_births"] == 1 and not run["retired_knots"] and run["c"]
            first_differs = run["bprime_first_round"]
            if not run["a"] or (first_differs is not None and first_differs < run["rounds"]):
                continue
            kinds = run["place_rule_last_by_kind"]
            assert kinds["start"][1] == 0 and kinds["other"][1] == 0
            groups["both"].add(idx)
            if kinds["child"][1] == 0:
                groups["own"].add(idx)
    output = {}
    for key, groups in by_form.items():
        x1, x2 = sorted(groups["own"] - groups["all"]), sorted(groups["both"] - groups["all"])
        source = expected[key]
        checks["closing_diagnostic_disagrees"] += (
            x1 != source["starts_gained_X1"] or x2 != source["starts_gained_X2"]
            or len(groups["all"]) != source["joint_every_place (deviations 10)"]
            or len(groups["own"]) != source["joint_closing_knot_own_places_left_out"]
            or len(groups["both"]) != source["joint_both_places_of_closing_knot_left_out"]
        )
        output[key] = {
            "every_place": shares(weights, groups["all"]),
            "omit_closing_knot_own_places": shares(weights, groups["own"]),
            "omit_both_places_of_its_shared_distinctions": shares(weights, groups["both"]),
            "gained_omitting_own_places": x1,
            "additional_gains_omitting_both_places": sorted(set(x2) - set(x1)),
            "closing_runs_with_a_wrong_place": groups["closing_checked"],
        }
    extra = sorted({idx for record in output.values() for idx in record["additional_gains_omitting_both_places"]})
    return {"by_law_form": output, "extra_gain_starts": {idx: places(all_starts[idx], atlas) for idx in extra}}


def three_counts(third, all_starts, by_law, counted):
    output = {}
    for name, key in THIRD_COUNT_LAWS.items():
        record = third["laws"][name]
        parity = counted[f"{key}|parity"]
        other_count = set(record["counted census indices"])
        base = by_law[f"{key}|parity"]
        output[key] = {
            "third_population": third["census starts"],
            "third_counted": record["counted"],
            "different_counted_indices": sorted(parity ^ other_count),
            "third_counted_among_set_aside": sorted(idx for idx in other_count if not all_starts[idx].kept),
            "agree_on_split_by_size": Counter(str(all_starts[idx].size) for idx in parity)
            == record["by knots of the start"],
            "agree_on_split_by_greatest_difference": Counter(str(base[idx]["greatest"]) for idx in parity)
            == record["by greatest difference, child less parent"],
        }
    return output


def compare_printed_tables(base, p2, closing, checks):
    part_one_table = read(ARTIFACTS / "part1.json")
    part_five_table = read(ARTIFACTS / "part5.json")["by_law"]
    for key, observed in base.items():
        expected = part_one_table["laws"][key]
        counted, pop = observed["different_parent_steps"]["census"]
        labelled_counted, labelled_pop = observed["different_parent_steps"]["labelled"]
        checks["part_one_counted_summary_disagrees"] += (
            (counted, pop) != (expected["counted"], expected["population"])
            or labelled_counted / labelled_pop != expected["counted_labelled_share"]
            or observed["different_parent_steps_greatest_difference"]
            != {int(k): v for k, v in expected["counted_greatest"].items()}
            or observed["fives_right_among_counted"]["census"][0] != expected["fives_right_on_among_counted"]
            or observed["waiting_condition_fails"]["census"][0] != expected["lq_fails"]
        )
    for key, observed in p2.items():
        expected = part_five_table[key]
        checks["part_five_summary_disagrees"] += (
            observed["reaches_three"] != expected["reach_three_parent_steps (part 1)"]
            or observed["first_failure_by_round"] != {int(k): v for k, v in expected["fail_by_round"].items()}
            or observed["reaches_three_with_no_failure_indices"] != expected["exceptions (reach three, no failing birth)"]
        )
    for key, observed in closing["by_law_form"].items():
        expected = part_one_table["armw"][key]
        count, _ = observed["every_place"]["census"]
        labelled_count, labelled_pop = observed["every_place"]["labelled"]
        checks["part_one_joint_summary_disagrees"] += (
            count != expected["joint_stratum"] or labelled_count / labelled_pop != expected["joint_labelled_share"]
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", type=int, help="Time prefixes of all input families and leave the report untouched.")
    args = parser.parse_args()
    clock_start = perf_counter()
    timing = {}
    atlas = nx.graph_atlas_g()
    laws_source = read(REGISTRATION / "laws.json")
    recorded = [law["name"] for law in laws_source["recorded"]]
    laws = {law["name"]: law for law in laws_source["recorded"] + laws_source["holding"]}
    named_starts = read(REGISTRATION / "starts.json")["starts"]
    if args.probe:
        for size in range(1, 7):
            before = perf_counter()
            prefix = list(islice(census(atlas, size), args.probe))
            timing[f"census_size_{size}"] = [len(prefix), round(perf_counter() - before, 4)]
    else:
        by_size = {size: list(census(atlas, size)) for size in range(1, 7)}
        all_starts = [start for size in range(1, 6) for start in by_size[size]]
        timing["census"] = round(perf_counter() - clock_start, 4)

    streams = {
        "census_rows": ("part1_runs.json.gz", "census_rows"),
        "six_rows": ("part1_runs.json.gz", "six_rows"),
        "six_kept_a": ("part1_runs.json.gz", "six_kept_a"),
        "named_rows": ("part4.json", "runs"),
        "part_five": ("part5.json", "rows"),
    }
    records = {}
    for key, (filename, field) in streams.items():
        before = perf_counter()
        records[key] = list(rows(ARTIFACTS / filename, field, args.probe))
        timing[key] = [len(records[key]), round(perf_counter() - before, 4)]
    if args.probe:
        before = perf_counter()
        census_prefix = records["census_rows"]
        prefix_starts = list(islice(
            (start for size in range(1, 6) for start in census(atlas, size)), len(census_prefix)
        ))
        probe_checks = Counter()
        _, by_law, _ = part_one(census_prefix, prefix_starts, laws, probe_checks)
        retained = {row["idx"] for row in census_prefix if row["kept"]}
        threshold([row for row in records["part_five"] if row["idx"] in retained], by_law, recorded, probe_checks)
        arm_w(census_prefix, records["named_rows"], laws, prefix_starts, named_starts, probe_checks)
        timing["analysis_prefix"] = round(perf_counter() - before, 4)
        print(json.dumps(timing, indent=2))
        return

    before = perf_counter()
    checks = Counter()
    raw = records["census_rows"]
    assert [row["idx"] for row in raw] == list(range(len(all_starts)))
    base, by_law, counted = part_one(raw, all_starts, laws, checks)
    p2 = threshold(records["part_five"], by_law, recorded, checks)
    strata = arm_w(raw, records["named_rows"], laws, all_starts, named_starts, checks)
    for example in strata["examples"]["BB_retiring_c_false_and_right"]:
        if "census_index" in example:
            example["start_knots_and_distinctions"] = places(all_starts[example["census_index"]], atlas)
    for summary in base.values():
        for example in summary["only_counted_with_registered_stopping"]:
            example["start_knots_and_distinctions"] = places(all_starts[example["index"]], atlas)
    diagnostic = read(ARTIFACTS / "part1_joint_closing.json")["by_law_form"]
    closing = closing_readings(raw, all_starts, atlas, diagnostic, checks)
    third = three_counts(read(HERE.parent / "checks" / "recount.json"), all_starts, by_law, counted)
    compare_printed_tables(base, p2, closing, checks)

    populations = {}
    for population, parity_only in (("parity_kept", True), ("all_census_starts", False)):
        populations[population] = {}
        for size, starts in by_size.items():
            weights = {idx: start.weight for idx, start in enumerate(starts) if start.kept or not parity_only}
            selected = {idx for idx in weights if starts[idx].agrees}
            populations[population][size] = shares(weights, selected)
        weights = {idx: start.weight for idx, start in enumerate(all_starts) if start.kept or not parity_only}
        populations[population]["up_to_five"] = shares(weights, {idx for idx in weights if all_starts[idx].agrees})

    six = by_size[6]
    six_flags = [[start.kept, start.agrees] for start in six]
    checks["six_census_kept_or_agreement_flags_disagree"] += sum(
        case != recorded_case for case, recorded_case in zip(six_flags, records["six_kept_a"], strict=True)
    )
    order = list(range(len(six)))
    random.Random("DESCENT-HELD-20261125-001|six|v2").shuffle(order)
    expected = [idx for idx in order if six[idx].kept][:3000]
    observed = [row["idx6"] for row in records["six_rows"]]
    six_weights = {idx: six[idx].weight for idx in observed}
    checks["six_sample_not_the_registered_prefix"] += observed != expected[:len(observed)]
    checks["six_sample_weights_disagree"] += sum(row["w"] != six_weights[row["idx6"]] for row in records["six_rows"])
    six_counts = {}
    for law in laws:
        runs = {row["idx6"]: row["base"][law] for row in records["six_rows"]}
        six_counts[law], _ = tally_base(runs, six_weights, checks, full=False)

    timing["analysis"] = round(perf_counter() - before, 4)
    result = {
        "observations": "Per-run census and named-start records retain summaries rather than complete histories.",
        "place_count_start_agreement_by_population_and_size": populations,
        "part_one_counted": base,
        "fives_total_scope": scope_of_fives_total(base, counted),
        "part_five_threshold": {"totals": threshold_totals(p2), "by_law": p2},
        "parts_one_and_four_count_forms": strata,
        "closing_diagnostic": closing,
        "third_count": third,
        "six_knot_sample": {
            "registered_count": len(expected),
            "run_count": len(observed),
            "not_run": len(expected) - len(observed),
            "first_20_indices": observed[:20],
            "last_run_index": observed[-1],
            "first_not_run_index": expected[len(observed)] if len(observed) < len(expected) else None,
            "by_law": six_counts,
        },
        "crosscheck_mismatch_counts": dict(checks),
    }
    (HERE / "census_counts.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"timing_seconds": timing, "crosscheck_mismatch_counts": dict(checks)}, indent=2))


if __name__ == "__main__":
    main()
