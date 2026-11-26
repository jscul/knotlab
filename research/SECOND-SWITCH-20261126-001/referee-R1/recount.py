"""Recount saved comparisons, coverage, and timing from the three raw archives."""

import argparse
from collections import Counter, defaultdict
import gzip
from hashlib import sha256
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
LAWS = [f"CAP-{cap}" for cap in range(3, 8)] + ["ORD"]
SENDERS = ("g1:3@0", "g3:22@0", "stub")
SIGNS = ("add", "bar")
CHANGE_TIMES = range(3, 11)
HORIZON_TIMES = (3, 6)
WAITING_TIMES = (3, 5, 8)
ROUND_LIMIT = 24
KNOT_LIMIT = 6000


def archive(name):
    path = HERE.parent / (name + "_runs.jsonl.gz")
    with gzip.open(path, "rt") as stream:
        rows = [json.loads(line) for line in stream]
    return rows, {"file": path.name, "rows": len(rows), "sha256": sha256(path.read_bytes()).hexdigest()}


def first_difference(left, right, after=0):
    return next((round_ for round_, (a, b) in enumerate(zip(left, right), 1) if round_ > after and a != b), None)


def comparison(rows, base, *, final_knots=None):
    end = len(base)
    summary = Counter()
    timings = {step: Counter() for step in (1, 2)}
    ends = Counter()
    delays = Counter()
    early = Counter()
    for row in rows:
        t0, common, sharings, heard = (row[key] for key in ("t0", "rounds", "sharings", "heard"))
        assert t0 < common <= end <= ROUND_LIMIT, row
        assert heard is None or t0 < heard <= common, row
        changed = row.get("own births with")
        summary["tested"] += 1
        summary["heard"] += heard is not None
        summary["unheard"] += heard is None
        if changed is not None:
            assert all(type(count) is int for count in changed)
            assert len(changed) <= ROUND_LIMIT and common == min(end, len(changed)), row
            assert changed[:t0] == base[:t0], row
            assert first_difference(base, changed, t0) == heard, row
            summary["recounted_from_birth_counts"] += 1
        else:
            summary["read_saved_hearing_only"] += 1
        ends[common] += 1
        if sharings == 1:
            early["faster_hearing_impossible_for_one_sharing"] += 1
        elif sharings is not None and sharings > 1:
            early["at_least_one_too_early_round_available"] += 1
            if common >= t0 + sharings - 1:
                early["all_too_early_rounds_available"] += 1
            else:
                early["only_some_too_early_rounds_available"] += 1
        if heard is not None:
            assert sharings is not None
            delays[heard - t0 - sharings] += 1
            continue
        for step, counts in timings.items():
            if sharings is None:
                counts["no_sharing_count"] += 1
                continue
            threshold = t0 + step * sharings
            counts["past_round_limit"] += threshold > ROUND_LIMIT
            if common >= threshold:
                counts["examined_through_threshold"] += 1
            elif end < threshold and end < ROUND_LIMIT and final_knots is not None and final_knots > KNOT_LIMIT:
                counts["baseline_knot_bound_before_threshold"] += 1
                counts["baseline_knot_bound_before_threshold_within_round_limit"] += threshold <= ROUND_LIMIT
            elif common < end:
                counts["change_ended_earlier_before_threshold_cause_not_saved"] += 1
                counts["change_ended_earlier_before_threshold_within_round_limit"] += threshold <= ROUND_LIMIT
            elif common < ROUND_LIMIT:
                counts["baseline_ended_before_threshold_cause_not_saved"] += 1
                counts["baseline_ended_before_threshold_within_round_limit"] += threshold <= ROUND_LIMIT
            else:
                counts["round_limit_before_threshold"] += 1
    return {
        "tested": summary["tested"], "heard": summary["heard"], "unheard": summary["unheard"],
        "recounted_from_birth_counts": summary["recounted_from_birth_counts"],
        "read_saved_hearing_only": summary["read_saved_hearing_only"],
        "common_end_rounds": dict(sorted(ends.items())),
        "opportunities_to_hear_before_t0_plus_sharings": dict(early),
        "first_hearing_minus_t0_minus_sharings": dict(sorted(delays.items())),
        "unheard_timing_sensitivity": {
            f"t0_plus_{step}_times_sharings": dict(counts) for step, counts in timings.items()
        },
    }


def add_summaries(summaries):
    total = Counter()
    subcounts = defaultdict(Counter)
    sensitivity = defaultdict(Counter)
    for summary in summaries:
        for key, value in summary.items():
            if key == "unheard_timing_sensitivity":
                for threshold, counts in value.items():
                    sensitivity[threshold].update(counts)
            elif isinstance(value, dict):
                subcounts[key].update(value)
            else:
                total[key] += value
    return dict(total) | {key: dict(counts) for key, counts in subcounts.items()} | {
        "unheard_timing_sensitivity": {key: dict(counts) for key, counts in sensitivity.items()}
    }


def differences(series, after=3):
    return [right - left for left, right in zip(series[after - 1:], series[after:]) if None not in (left, right)]


def main_panel(rows, *, pilot):
    assert not any("not run" in row for row in rows)
    groups = defaultdict(lambda: defaultdict(list))
    for row in rows:
        groups[(row["law"], row["B"])][row["reading"]].append(row)
    assert set(groups) == {(law, far) for law in LAWS for far in SENDERS}
    cells = sorted(groups)[:1] if pilot else list(groups)
    details = []
    for law, far in cells:
        readings = groups[law, far]
        base, = readings["base"]
        far_history, = readings["far end distance"]
        receiver = f"tri:{int(law[-1]) - 2 if law != 'ORD' else 1}22@0"
        end, final_knots = base["rounds"], base["knots"]
        own, stub = base["own births"], base["own births with a stub"]
        distances = far_history["by round"]
        assert all(row["A"] == receiver for records in readings.values() for row in records)
        assert all(type(count) is int for count in own + stub)
        assert stub == groups[law, "stub"]["base"][0]["own births"]
        assert end == len(own) == len(distances) <= ROUND_LIMIT
        assert end == ROUND_LIMIT or final_knots > KNOT_LIMIT
        far_rows, horizon = readings["change"], readings["horizon"]
        changes = defaultdict(list)
        for row in far_rows:
            assert row["t0"] in CHANGE_TIMES, row
            changes[row["t0"]].append(row)
        horizon_at = defaultdict(list)
        for row in horizon:
            assert row["t0"] in HORIZON_TIMES and row["sharings"] in range(1, 9), row
            assert row["class"] != "A", row
            horizon_at[row["t0"], row["sharings"]].append(row)
        far_cells = []
        for t0 in CHANGE_TIMES:
            candidates = changes[t0]
            targets = defaultdict(list)
            for row in candidates:
                targets[row["knot"]].append(row)
            assert len(targets) <= 5
            for trials in targets.values():
                assert sorted(row["sign"] for row in trials) == list(SIGNS), trials
                assert len({row["sharings"] for row in trials}) == 1, trials
            nearest = distances[t0 - 1] if t0 <= end else None
            if t0 < end:
                assert min((row["sharings"] for row in candidates if row["sharings"] is not None), default=None) == nearest
            status = "tested" if targets else "no live reachable far member recorded"
            if t0 >= end:
                assert not targets
                status = "no round available after set round" if t0 == end else "set round not computed"
            far_cells.append({
                "t0": t0, "status": status, "targets": len(targets), "nearest_sharings": nearest,
                "placements_by_sharings": dict(Counter(trials[0]["sharings"] for trials in targets.values())),
                "add": comparison([row for row in candidates if row["sign"] == "add"], own, final_knots=final_knots),
                "bar": comparison([row for row in candidates if row["sign"] == "bar"], own, final_knots=final_knots),
            })
        horizon_cells = []
        for t0 in HORIZON_TIMES:
            for sharings in range(1, 9):
                candidates = horizon_at[t0, sharings]
                assert len(candidates) == len({row["knot"] for row in candidates}) <= 3
                horizon_cells.append({
                    "t0": t0, "sharings": sharings, "classes": dict(Counter(row["class"] for row in candidates)),
                    "comparison": comparison(candidates, own, final_knots=final_knots),
                })
        hearing = [row for row in horizon if row["heard"] is not None]
        exact_controls = {(row["t0"], row["sharings"]) for row in horizon}
        details.append({
            "law": law, "receiver": receiver, "far_end": far, "baseline_rounds": end,
            "baseline_final_knots": final_knots,
            "baseline_limit": "knot bound" if final_knots > KNOT_LIMIT else "round limit",
            "stub_common_end_round": min(end, len(stub)),
            "first_baseline_birth_count_difference_from_stub": first_difference(own, stub),
            "baseline_birth_count_differences_from_stub": [i for i, (a, b) in enumerate(zip(own, stub), 1) if a != b],
            "nearest_far_sharings": distances,
            "nearest_far_steps_from_round_three": differences(distances),
            "far_changes": comparison(far_rows, own, final_knots=final_knots),
            "far_changes_by_set_round": far_cells,
            "far_changes_with_same_round_and_sharings_horizon_control": sum(
                (row["t0"], row["sharings"]) in exact_controls for row in far_rows
            ),
            "horizon": comparison(horizon, own, final_knots=final_knots),
            "horizon_cells": horizon_cells,
            "horizon_hearings": [
                {key: row[key] for key in ("t0", "knot", "class", "sharings", "heard", "rounds")} for row in hearing
            ],
        })
    return details


def census(rows):
    assert len(rows) == len({row["B"] for row in rows})
    classes = defaultdict(list)
    waiting_candidates = {}
    for row in rows:
        name = row["B"]
        end = row["rounds"]
        far, old = row["nearest far member"], row["nearest far member that waited"]
        assert end == len(far) == len(old) == len(row["own births"]) <= 16
        steps = differences(far)
        if any(delta <= 0 for delta in steps):
            status = "at_least_one_nonpositive_step"
            if any(distance is not None for distance in old[2:]):
                waiting_candidates[name] = row
        elif end >= 4 and all(distance is None for distance in far[3:]):
            status = "no_reachable_far_member_from_round_four"
        elif steps and all(delta == 1 for delta in steps):
            status = "every_recorded_step_is_one"
        elif steps:
            status = "all_recorded_steps_positive_with_a_step_above_one"
        else:
            status = "no_available_step_from_round_three"
        classes[status].append(name)
    coverage = {
        "cases": len(rows), "round_ends": dict(Counter(row["rounds"] for row in rows)),
        "classes": {key: len(names) for key, names in classes.items()},
        "cases_with_nonpositive_step": classes.get("at_least_one_nonpositive_step", []),
        "remaining_cases": {key: names for key, names in classes.items() if key.startswith(("all_recorded_steps_positive", "no_available_step"))},
    }
    return coverage, waiting_candidates


def waiting_panel(rows, candidates, *, pilot):
    by_far = defaultdict(list)
    for row in rows:
        by_far[row["B"]].append(row)
    if pilot:
        by_far = {name: by_far[name] for name in candidates}
    assert set(by_far) <= set(candidates), sorted(set(by_far) - set(candidates))
    details = []
    for far, census_row in candidates.items():
        records = by_far[far]
        base = records[0]["own births"] if records else census_row["own births"]
        old = census_row["nearest far member that waited"]
        end = census_row["rounds"]
        assert all(row["own births"] == base for row in records)
        assert base[:end] == census_row["own births"]
        by_round = defaultdict(list)
        for row in records:
            assert row["t0"] in WAITING_TIMES and row["made"] < row["t0"]
            by_round[row["t0"]].append(row)
        for t0 in WAITING_TIMES:
            trials = by_round[t0]
            assert bool(trials) == (t0 < len(base) and (t0 > end or old[t0 - 1] is not None))
            if trials:
                assert sorted(row["sign"] for row in trials) == list(SIGNS)
                assert len({(row["knot"], row["made"], row["sharings"]) for row in trials}) == 1
                if t0 <= end:
                    assert trials[0]["sharings"] == old[t0 - 1]
        first_old = next(i for i, distance in enumerate(old[2:], 3) if distance is not None)
        later_distances = old[first_old - 1:]
        fixed = len(set(later_distances)) == 1 and 6 <= later_distances[0] <= 8
        details.append({
            "far_end": far, "census_rounds": end, "baseline_rounds": len(base) if records else None,
            "nearest_far_sharings": census_row["nearest far member"], "nearest_waiting_sharings": old,
            "first_nearest_waiting_round_from_three": first_old,
            "waiter_distance_fixed_in_six_to_eight_from_first_appearance": fixed,
            "waiter_distance_fixed_in_six_to_eight_from_three_through_sixteen": fixed and first_old == 3 and end == 16,
            "first_count_difference_from_census": first_difference(base, census_row["own births"]),
            "set_rounds_without_record": [t0 for t0 in WAITING_TIMES if not by_round[t0]],
            "distinct_target_knots": len({row["knot"] for row in records}),
            "targets": [{key: row[key] for key in ("t0", "knot", "made", "sharings")} for row in records if row["sign"] == "add"],
            "comparison": comparison(records, base),
        })
    return details


def check_rendered_table(main):
    rendered_far = {}
    rendered_horizon = {}
    for line in (HERE.parent / "second_table.md").read_text().splitlines():
        if not line.startswith("| tri:"):
            continue
        receiver, law, far, *columns = (field.strip() for field in line.strip("|").split("|"))
        key = law, far
        if len(columns) == 5:
            assert key not in rendered_far
            rendered_far[key] = (receiver, *columns)
        else:
            set_round, fractions = columns
            horizon_key = key, int(set_round)
            assert horizon_key not in rendered_horizon
            rendered_horizon[horizon_key] = (receiver, {
                int(sharings): (int(heard), int(tested))
                for sharings, heard, tested in re.findall(r"(\d+): (\d+)/(\d+)", fractions)
            })
    checked_far = checked_horizon = 0
    for cell in main:
        key = cell["law"], cell["far_end"]
        recorded = cell["nearest_far_sharings"]
        end = cell["baseline_rounds"]
        displayed_sharings = ", ".join(str(recorded[r - 1]) if r <= end else "-" for r in (3, 6, 10, end))
        totals = cell["far_changes"]
        assert totals["heard"] == 0, "A hearing must be compared against the rendered earliest round."
        assert rendered_far.pop(key) == (
            cell["receiver"], str(end), displayed_sharings, f"{totals['heard']} of {totals['tested']}", "-", "-",
        )
        checked_far += 1
        for t0 in HORIZON_TIMES:
            fractions = {row["sharings"]: (row["comparison"]["heard"], row["comparison"]["tested"])
                         for row in cell["horizon_cells"] if row["t0"] == t0 and row["comparison"]["tested"]}
            assert rendered_horizon.pop((key, t0)) == (cell["receiver"], fractions)
            checked_horizon += len(fractions)
    if len(main) == len(LAWS) * len(SENDERS):
        assert not rendered_far and not rendered_horizon
    return {"matching_far_rows": checked_far, "matching_horizon_distance_fractions": checked_horizon}


def recount(*, pilot):
    second, second_source = archive("second")
    recede, recede_source = archive("recede")
    waiting, waiting_source = archive("waiting_far")
    main = main_panel(second, pilot=pilot)
    if pilot:
        recede = recede[:12] + [row for row in recede[12:] if row["B"] == waiting[0]["B"]]
    coverage, waiting_candidates = census(recede)
    waiting_details = waiting_panel(waiting, waiting_candidates, pilot=pilot)
    cap_far = add_summaries(row["far_changes"] for row in main if row["law"] != "ORD")
    ord_far = add_summaries(row["far_changes"] for row in main if row["law"] == "ORD")
    waiting_far = add_summaries(row["comparison"] for row in waiting_details)
    horizon_cells = [cell for row in main for cell in row["horizon_cells"]]
    far_cells = [cell for row in main for cell in row["far_changes_by_set_round"]]
    receding_steps = [row["nearest_far_steps_from_round_three"] for row in main if row["nearest_far_steps_from_round_three"]]
    fast_baselines = [row for row in main if row["law"] != "ORD" and row["far_end"] == "g3:22@0"]
    fast_after_six = add_summaries(cell["comparison"] for row in fast_baselines for cell in row["horizon_cells"] if cell["t0"] == 6)
    return {
        "source_archives": [second_source, recede_source, waiting_source],
        "birth_observable": "Archived own-birth series retain counts only. Saved hearing rounds are counted for all rows; the change and waiting panels also permit an independent first-count-difference check. The horizon rows do not preserve the changed series.",
        "timing_sensitivity": "The t0 plus s and t0 plus 2s thresholds are illustrative. A saved total above 6000 identifies a baseline knot-bound case. Other early endpoints lack a saved reason. A threshold past 24 can also be preceded by a knot-bound endpoint.",
        "main_far_totals": {"all": add_summaries(row["far_changes"] for row in main), "capped": cap_far, "ordinary": ord_far},
        "main_horizon_totals": {"all": add_summaries(row["horizon"] for row in main),
                                "capped": add_summaries(row["horizon"] for row in main if row["law"] != "ORD"),
                                "ordinary": add_summaries(row["horizon"] for row in main if row["law"] == "ORD"),
                                "by_sharings": {s: add_summaries(cell["comparison"] for cell in horizon_cells if cell["sharings"] == s)
                                                for s in range(1, 9)}},
        "horizon_two_knot_capped_after_round_six": {
            "first_baseline_birth_count_difference_from_stub": {row["law"]: row["first_baseline_birth_count_difference_from_stub"] for row in fast_baselines},
            "t0": 6,
            "edits_before_first_stub_difference": fast_after_six,
        },
        "coverage": {
            "main_far_set_round_cells": dict(Counter(cell["status"] for cell in far_cells)),
            "main_horizon_distance_cells": {"populated": sum(cell["comparison"]["tested"] > 0 for cell in horizon_cells),
                                            "empty": sum(cell["comparison"]["tested"] == 0 for cell in horizon_cells)},
            "main_far_changes_with_matched_horizon_control": sum(row["far_changes_with_same_round_and_sharings_horizon_control"] for row in main),
            "main_runs_with_an_observed_step_from_round_three": len(receding_steps),
            "main_runs_with_every_observed_step_exactly_one": sum(set(steps) == {1} for steps in receding_steps),
            "waiting_candidates_with_no_edit_at_a_scheduled_round": sum(row["baseline_rounds"] is None for row in waiting_details),
            "waiting_candidates_with_at_least_one_edit": sum(row["baseline_rounds"] is not None for row in waiting_details),
            "waiting_candidates_with_nearest_waiter_fixed_through_round_sixteen": sum(
                row["waiter_distance_fixed_in_six_to_eight_from_three_through_sixteen"] for row in waiting_details
            ),
            "rendered_table": check_rendered_table(main),
        },
        "main_trial_configuration": add_summaries(row["far_changes"] for row in main if row["law"] == "CAP-3" and row["far_end"] == "g1:3@0"),
        "main_capped_excluding_trial_configuration": add_summaries(row["far_changes"] for row in main if row["law"] != "ORD" and (row["law"], row["far_end"]) != ("CAP-3", "g1:3@0")),
        "main_cells": main,
        "census_coverage": coverage,
        "waiting_candidates": len(waiting_candidates),
        "waiting_totals": waiting_far,
        "waiting_totals_fixed_distance_through_round_sixteen": add_summaries(
            row["comparison"] for row in waiting_details if row["waiter_distance_fixed_in_six_to_eight_from_three_through_sixteen"]
        ),
        "waiting_details": waiting_details,
        "pooled_far_totals": {"all": add_summaries([cap_far, ord_far, waiting_far]), "capped": add_summaries([cap_far, waiting_far])},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    settings = parser.parse_args()
    result = recount(pilot=settings.pilot)
    if not settings.pilot:
        (HERE / "recount.json").write_text(json.dumps(result, indent=2) + "\n")
    print({"baseline_setups": len(result["main_cells"]), "census_entries": result["census_coverage"]["cases"],
           "waiting_configurations": result["waiting_candidates"], "far_totals": result["pooled_far_totals"]})
