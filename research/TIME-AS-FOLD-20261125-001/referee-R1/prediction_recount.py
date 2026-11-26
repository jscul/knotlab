"""Recount the registered predictions from recorded runs and earlier gate data."""

import argparse
from collections import Counter, defaultdict
import gzip
from itertools import islice, product
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TICKET = "TIME-AS-FOLD-20261125-001A"
DATA = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_count_of_returns"
REGISTRATION = ROOT / "research" / TICKET
EARLIER = ROOT / "artifacts"
ITEM_FIELDS = ("group", "rule", "base", "start", "choice", "knot_law")
MODES = ("past", "nopast")
CLOCK = "runs with a clock of 4 equal ticks"
OFF4 = "runs with a clock giving parts off at 4 ticks"
OFF2 = "runs with a series giving parts off at 2+ ticks"
THREE = ("Ring(5,3)", "Ring(7,3)", "Ring(9,3)")


def read_json(path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt") as stream:
            return json.load(stream)
    return json.loads(path.read_text())


def read_lines(path, limit=None):
    with gzip.open(path, "rt") as stream:
        yield from map(json.loads, islice(stream, limit))


def item_key(row):
    return tuple(row[field] for field in ITEM_FIELDS)


def ration(base):
    return "FLOOR1" if base.startswith("COPY-LAW") else "CAP-3"


def primary(row):
    if "+FILLERS" in row["base"]:
        return False
    return (row["rule"], ration(row["base"])) in (("STEPS-1", "FLOOR1"), ("MET", "CAP-3"))


def gates(limit):
    match = read_json(DATA / "g1a.json")["runs"][:limit]
    ring_rows = read_json(DATA / "g1b_rows.json.gz")[:limit]
    ring = "RING-IN-BALANCE-20261123-001B"
    old_ring = read_json(EARLIER / ring / f"{ring}-E001_reference" / "p3_census_detail.json")["runs"]
    old_returning = {(row["g"], tuple(row["loose"])) for row in old_ring if row["law"] == "two"}
    new_returning = {(row["g"], tuple(row["loose"])) for row in ring_rows if row.get("past")}
    starts = read_json(REGISTRATION / "starts.json")
    registered = {(row["atlas_index"], tuple(row["loose"])) for row in starts["ring_study_returning_starts"]}
    g2 = read_json(DATA / "g2.json")["runs"][:limit]
    meet = "PARTS-MEET-AGAIN-20261124-001A"
    source = EARLIER / meet / f"{meet}-E001_meet_again"
    source_count = Counter()
    excluded = 0
    for run in ("run1", "run3"):
        for row in read_lines(source / f"{run}.jsonl.gz", limit):
            fields = row["law_fields"]
            if fields["joinable"] != "MET" or fields["take"] in ("CARRY", "FIRST"):
                excluded += 1
            else:
                source_count[(run, row["start"], row["law"], len(row["per_round"]))] += 1
    g2_count = Counter((row["run"], row["start"], row["law"], row["rounds"]) for row in g2)
    g3 = read_json(DATA / "g3.json")
    return {
        "G1a": {"rows": len(match), "matches": sum(row["same"] and not row["diffs"] for row in match),
                 "distinct_run_keys": len({(r["start"], r["base"], r["knot_law"]) for r in match}),
                 "rounds": sum(row["rounds"] for row in match)},
        "G1b": {"rows": len(ring_rows), "distinct_start_keys": len({(r["g"], tuple(r["loose"])) for r in ring_rows}),
                 "past": len(new_returning), "nopast": sum(bool(row.get("nopast")) for row in ring_rows),
                 "set_aside": sum(bool(row.get("set_aside")) for row in ring_rows),
                 "set_aside_disagreements": sum(bool(row.get("disagree")) for row in ring_rows),
                 "old_returning": len(old_returning), "matches_old_and_registered": new_returning == old_returning == registered},
        "G2": {"rows": len(g2), "reported_match": sum(row["ok"] and not row["bad"] and row["rounds"] == row["mine_rounds"] for row in g2),
               "rounds": sum(row["rounds"] for row in g2), "frozen_rows": source_count.total(),
               "frozen_rounds": sum(key[-1] * count for key, count in source_count.items()),
               "frozen_excluded": excluded, "frozen_run_keys_match": g2_count == source_count},
        "G3": {"renamed_accepted": sum(row["accepted"] and row["accepted_vf2"] for row in g3["renamed"]),
               "altered_brute_and_rejected": sum(row["brute_not_same"] and row["rejected"] and row["rejected_vf2"] for row in g3["altered"]),
               "large_renamed_reported": g3["summary"]["supplement_large_accepted"]},
    }


def four_periods(periods, off=None):
    for i in range(len(periods) - 3):
        if len(set(periods[i:i + 4])) == 1 and (off is None or all(off[i:i + 4])):
            return True
    return False


def series_flags(series):
    periods = series["periods"]
    off = [bool(tick[2]) for tick in series["ticks"]]
    copies = [bool(tick[4]) for tick in series["ticks"]]
    assert len(periods) == len(off)
    assert periods == [b - a for a, b in zip([series["t0"]] + [t[0] for t in series["ticks"]], [t[0] for t in series["ticks"]])]
    clock = series["size"] >= 2 and four_periods(periods)
    return {"clock": bool(clock), "clock_off4": bool(clock and four_periods(periods, off)),
            "clock_off4_anywhere": bool(clock and sum(off) >= 4), "series_off2": sum(off) >= 2,
            "ticks_off": sum(off), "ticks_off_or_copies": sum(a or b for a, b in zip(off, copies))}


def prototype_key(key):
    group, rule, variant, base, start, choice, knot_law, _ = key.split("|")
    if variant.startswith("MET:"):
        rule = variant
    elif variant.startswith("STEPS:"):
        rule += ":" + variant.split(":")[1]
    if group == "ring227":
        atlas, loose = start[1:].split(":")
        start = f"atlas {atlas} loose {','.join(loose)}"
    return group, rule, base, start, choice, knot_law


def cell_key(row):
    return "|".join((row["group"], row["rule"] or "none", ration(row["base"])))


def run123(limit):
    prototype = read_json(REGISTRATION / "compare.json")["census"]
    old_excluded = {prototype_key(key) for key in prototype["unfinished"]}
    matched_exclusions = set()
    old_ladder = read_json(REGISTRATION / "compare.json")["ladder"]["per_run"]
    old_ladder_by_key = {(r["start"], r["k"], r["choice"], r["knot_law"]): r for r in old_ladder}
    files = [DATA / f"run1_part{i}.jsonl.gz" for i in range(1, 9)]
    files.extend(DATA / name for name in ("run2.jsonl.gz", "run3.jsonl.gz"))
    totals = defaultdict(Counter)
    final_cells = defaultdict(Counter)
    compare_cells = defaultdict(Counter)
    compare_singleton_only = defaultdict(Counter)
    inconsistencies = Counter()
    keys = set()
    run2_starts = set()
    run2_control_positive_starts = set()
    p2 = defaultdict(Counter)
    p3 = defaultdict(Counter)
    p4 = Counter()
    p7 = defaultdict(Counter)
    late_returns = []
    next_expected_returns = []
    early_takes = []
    p7_differences = []
    convention_swaps = Counter()
    four_tick_alternatives = Counter()
    for path in files:
        for row in read_lines(path, limit):
            key = item_key(row)
            assert key not in keys, key
            keys.add(key)
            group, rule, base, start, choice, knot_law = key
            totals[group]["runs"] += 1
            totals[group][f"stop:{row.get('stop')}"] += 1
            if row.get("stop") in ("time", "unfinished") or "past" not in row:
                totals[group]["no_series_recorded"] += 1
                continue
            modes = MODES + (("past_greatest", "nopast_greatest") if "past_greatest" in row else ())
            for mode in modes:
                summaries = [series_flags(s) for s in row[f"{mode}_series"]]
                for measure in ("clock", "clock_off4", "clock_off4_anywhere", "series_off2"):
                    actual = row[mode][measure]
                    computed = any(summary[measure] for summary in summaries)
                    if actual != computed:
                        inconsistencies[f"{mode}:{measure}"] += 1
                        assert measure == "series_off2" and actual and not computed
                for flag in ("clock", "clock_off4"):
                    if mode not in MODES:
                        first = row[mode.split("_")[0]][flag]
                        if row[mode][flag] != first:
                            convention_swaps[f"{mode}:{flag}"] += 1
                if mode not in MODES or group == "ladder":
                    continue
                if row[mode]["clock_off4"] != row[mode]["clock_off4_anywhere"]:
                    four_tick_alternatives[f"{group}:{mode}"] += 1
                cell = cell_key(row)
                for col, field in ((CLOCK, "clock"), (OFF4, "clock_off4"), (OFF2, "series_off2")):
                    final_cells[cell][f"{mode}: {col}"] += row[mode][field]
                    if key not in old_excluded:
                        compare_cells[cell][f"{mode}: {col}"] += row[mode][field] * (2 if rule == "MET:join" and choice == "OLDEST" else 1)
                if key not in old_excluded and row[mode]["series_off2"] and not any(
                        saved["size"] > 1 and flags["series_off2"] for saved, flags in zip(row[f"{mode}_series"], summaries)):
                    compare_singleton_only[cell][f"{mode}: {OFF2}"] += 2 if rule == "MET:join" and choice == "OLDEST" else 1
            if group != "ladder":
                final_cells[cell_key(row)]["runs"] += 1
                if key in old_excluded:
                    matched_exclusions.add(key)
                else:
                    compare_cells[cell_key(row)]["runs"] += 2 if rule == "MET:join" and choice == "OLDEST" else 1
            if group in ("main", "dbt") and ration(base) == "FLOOR1" and rule in (
                    "Q", "MET", "MET:offshoot", "STEPS-1", "STEPS-2", "UP-TO-2"):
                count = p2[f"{group}|{rule}"]
                count["runs"] += 1
                for mode in MODES:
                    summary = row[mode]
                    bound = "p2_exceeds_k_bound" if rule == "STEPS-2" else "p2_exceeds_start_bound"
                    count[f"{mode}:violating_series"] += summary[bound]
                    count[f"{mode}:max_ticks_off_or_copies"] = max(count[f"{mode}:max_ticks_off_or_copies"], summary["max_ticks_off_or_copies"])
            if (group in ("main", "fbp", "dbt") and primary(row)) or (group == "fbp" and rule == "Q" and ration(base) == "FLOOR1"):
                count = p3[f"{group}|{rule}"]
                count["runs"] += 1
                count[f"stop:{row['stop']}"] += 1
                for mode in MODES:
                    count[f"{mode}:clock"] += row[mode]["clock"]
                    count[f"{mode}:off4"] += row[mode]["clock_off4"]
            if group == "main" and rule == "MET" and primary(row) and start in read_named_ring_starts:
                p4["runs"] += 1
                p4["with_returns"] += bool(row["start_roster_returns"])
                p4[f"stop:{row['stop']}"] += 1
            if group == "ring227":
                run2_starts.add(start)
                if rule is None and row["past"]["clock_off4"] and row["nopast"]["clock_off4"]:
                    run2_control_positive_starts.add(start)
            if group == "ladder":
                k = row["k"]
                raw_returns = row["start_roster_returns"]
                expected_early = list(range(2, 2 * k + 1, 2))
                count = p7[f"k={k}|{choice}"]
                count["runs"] += 1
                count["finished"] += row["stop"] is None
                count["no_returns"] += not raw_returns
                count["exact_early_returns"] += raw_returns == expected_early
                count["completed_early_sequence"] += raw_returns[:k] == expected_early
                count["completed_early_sequence_and_saw_next_round"] += raw_returns[:k] == expected_early and row["rounds"] >= 2 * k + 2
                take = row["ring_member_offshoot_first_take"]
                count["any_ring_member_offshoot_take"] += take is not None
                count["take_at_2k+1"] += take == 2 * k + 1
                ladder_key = (start, k, choice, knot_law)
                if take is not None and take <= 2 * k:
                    early_takes.append([ladder_key, take])
                if raw_returns[:k + 1] == expected_early + [2 * k + 2]:
                    next_expected_returns.append(ladder_key)
                if raw_returns and raw_returns[-1] > 2 * k:
                    late_returns.append([ladder_key, raw_returns])
                old = old_ladder_by_key[ladder_key]
                if (raw_returns, row["rounds"], row["stop"]) != (old["returns"], old["rounds"], old["stop"]):
                    p7_differences.append([ladder_key, raw_returns, old])
    differences = {}
    singleton_excluded_differences = {}
    for cell, new in compare_cells.items():
        old = prototype["table"][cell]
        delta = {field: [value, old.get(field, 0)] for field, value in new.items() if old.get(field, 0) != value}
        if delta:
            differences[cell] = delta
        by_size = {field: [new[field] - compare_singleton_only[cell][field], old.get(field, 0)]
                   for field in (f"past: {OFF2}", f"nopast: {OFF2}")
                   if new[field] - compare_singleton_only[cell][field] != old.get(field, 0)}
        if by_size:
            singleton_excluded_differences[cell] = by_size
    p4_comparison = round_one(limit)
    return {"runs_by_group": totals, "series_without_singleton_off_counts": inconsistencies,
            "P2": p2, "P3": p3, "P4": {"runs": p4, "round_one": p4_comparison},
            "P7": {"by_k_choice": p7, "late_returns": sorted(late_returns), "early_ring_member_takes": sorted(early_takes),
                   "next_expected_returns": sorted(next_expected_returns), "differences_from_prototype": sorted(p7_differences)},
            "P8": {"census_starts_run": len(run2_starts), "control_positive_starts_both_modes": len(run2_control_positive_starts),
                   "control": final_cells["ring227|none|CAP-3"], "MET": final_cells["ring227|MET|CAP-3"]},
            "P9": {key: value for key, value in final_cells.items() if key.startswith("main|") and ":" in key},
            "greatest_name_differences": convention_swaps, "four_tick_alternative_additions": four_tick_alternatives,
            "census": {"prototype_exclusions": len(old_excluded),
                "matched_prototype_exclusions": len(matched_exclusions), "rows_compared": len(compare_cells),
                "differences": differences, "off2_singleton_only": compare_singleton_only,
                "off2_differences_if_singletons_excluded": singleton_excluded_differences}}


read_named_ring_starts = {*THREE, "Ring(5,4)", "D2(4,3)", "D2(5,3)", "D2(6,3)", "DW(5,3)"}


def round_one(limit):
    rows = read_json(DATA / "p4_round1.json")[:limit]
    mismatches = []
    size = defaultdict(Counter)
    for row in rows:
        name = row["start"]
        if name not in THREE:
            continue
        n = int(name[5])
        used, control = row["MET"], row["control"]
        candidates = dict((tuple(k), count) for k, count in used["candidates"])
        expected_candidates = {("join", 0): n, ("offshoot", 2): n}
        actual = {tuple(k): count for k, count in used["births_kind_f_D"]}
        if n == 5:
            fresh = {("join", 2, 2): n, ("offshoot", 3, 4): n}
        else:
            fresh = {kind: count for kind, count in actual.items() if kind[1] == 3}
        check = (used["parents_loose_r1"] == control["parents_loose_r1"] and candidates == expected_candidates
                 and actual == fresh and used["members_after_r1"] == control["members_after_r1"]
                 and (n == 5 or used["short_in_r2"] == 2 * n and control["short_in_r2"] == n))
        if not check:
            mismatches.append(row)
        size[name]["cases"] += 1
        size[name]["agrees"] += check
    return {"recorded_rows": len(rows), "cases": size, "mismatches": mismatches}


def run45(limit):
    controls = Counter()
    primary_tests = Counter()
    ciii_periods = Counter()
    control_examples = []
    primary_examples = []
    for row in read_lines(DATA / "run4.jsonl.gz", limit):
        group, rule, _, _, _, knot_law = item_key(row)
        if group == "main" and rule is None and knot_law == "nae":
            controls["tests"] += 1
            for bar in row["bars"]:
                if "not_run" in bar:
                    controls["bars_not_run"] += 1
                    continue
                controls["B_run"] += 1
                controls["B_differs"] += bar["course_differs"] is not None
                controls["B_observed_through_two_periods"] += bar["grown_2_periods"]
                for variant in ("B'", "Ball"):
                    comparison = bar.get(variant)
                    controls[f"{variant}_new_comparison"] += isinstance(comparison, dict)
                    if isinstance(comparison, dict):
                        controls[f"{variant}_differs"] += comparison["course_differs"] is not None
                    elif comparison is None:
                        control_examples.append([item_key(row), bar["r"], variant])
        if group != "main" or not primary(row):
            continue
        primary_tests[f"C:{row['verdict_C']}"] += 1
        primary_tests[f"C-iii:{row['verdict_C_iii']}"] += 1
        if row["base"].endswith("(OFFSHOOT)") and knot_law == "nae":
            comparisons = [bar for bar in row["bars"] if "not_run" not in bar]
            primary_tests["offshoot_nae_tests"] += 1
            primary_tests["offshoot_nae_with_no_joint_in_run_bars"] += all(b["joint_B_after_bar"] == 0 for b in comparisons)
            primary_tests["offshoot_nae_all_three_bars_run"] += len(comparisons) == 3
            primary_tests["offshoot_nae_all_three_bars_run_and_no_joint"] += len(comparisons) == 3 and all(b["joint_B_after_bar"] == 0 for b in comparisons)
        if row["verdict_C_iii"] == "holds":
            ciii_periods[str(row["own_A_per_period"])] += 1
            primary_examples.append({"item": item_key(row), "t_j": row["t_j"], "period": row["period"],
                                     "own_A_per_period": row["own_A_per_period"],
                                     "bar_rounds": [bar["t_bar"] for bar in row["bars"]],
                                     "first_different_rounds": [bar["course_differs"] for bar in row["bars"]]})
    numberings = {}
    original = read_json(REGISTRATION / "starts.json")["named"]["two-knot"]
    for name in ("run5", "run5_near_case"):
        cases = defaultdict(Counter)
        case_starts = defaultdict(set)
        seen = set()
        for row in read_lines(DATA / f"{name}.jsonl.gz", limit):
            item = row["item"]
            if item["start"] != "two-knot" or item["rule"] != "STEPS-1":
                continue
            d_order, k_order = row["numbering"]["dist"], row["numbering"]["knots"]
            case = f"{item['choice']}|{item['knot_law']}"
            key = (case, tuple(d_order), tuple(k_order))
            assert key not in seen, key
            seen.add(key)
            new_stars = tuple(tuple(sorted(d_order.index(d) for d in original[k])) for k in k_order)
            assert new_stars == tuple(tuple(sorted(star)) for star in row["named_start"])
            case_starts[case].add(new_stars)
            shared, = set(new_stars[0]) & set(new_stars[1])
            expect = shared == min(new_stars[1]) if name == "run5" else any(shared == min(s) for s in new_stars)
            cases[case]["tested"] += 1
            cases[case]["survives"] += row["C_iii_holds"] > 0
            cases[case]["matches_condition"] += (row["C_iii_holds"] > 0) == expect
            cases[case]["has_undecided"] += row["undecided_C_iii"] > 0
            cases[case]["has_unfinished"] += row["unfinished_tests"] > 0
        numberings[name] = {case: dict(count, distinct_named_starts=len(case_starts[case])) for case, count in cases.items()}
    return {"P1": {"counts": controls, "missing_derived_variants": control_examples}, "P5": primary_tests,
            "P6": {"own_knots_per_period": ciii_periods, "primary_cases": primary_examples, "numberings": numberings}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="Take at most this many rows from each file for timing.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = {"prefix_per_file": args.limit, "gates": gates(args.limit), "runs_1_to_3": run123(args.limit),
              "recorded_comparisons": run45(args.limit)}
    report = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(report, end="")
    else:
        args.output.write_text(report)


if __name__ == "__main__":
    main()
