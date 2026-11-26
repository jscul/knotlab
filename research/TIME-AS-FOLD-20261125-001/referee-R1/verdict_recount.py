"""Reconstruct the recorded count and reading tests from the retained fields."""

import argparse
from collections import Counter, defaultdict
import gzip
from itertools import islice, permutations, product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = "TIME-AS-FOLD-20261125-001A"
FROZEN = ROOT / "research" / TICKET
RAW = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_count_of_returns"
RUN_FIELDS = ("group", "start", "base", "rule", "choice", "knot_law")
LAW_FIELDS = ("group", "base", "rule", "choice", "knot_law")
BASES = (
    "RING-LAW", "RING-LAW+FILLERS", "COPY-LAW(RETIRE)", "COPY-LAW(OFFSHOOT)",
    "COPY-LAW(WAIT)", "CAP-3(RETIRE)", "CAP-3(OFFSHOOT)",
)
GROUPS = ("main", "fbp", "dbt", "ring227", "ladder")
CHOICES = ("OLDEST", "NEWEST", "IN-TURN", "BY-COUNT")
KNOT_LAWS = ("nae", "parity")


def rows(stem, limit):
    with gzip.open(RAW / f"{stem}.jsonl.gz", "rt", encoding="utf-8") as handle:
        yield from map(json.loads, islice(handle, limit))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def run_key(row):
    return tuple(row[field] for field in RUN_FIELDS)


def law_key(key):
    return (key[0], *key[2:])


def report_key(key):
    return " | ".join("no taking rule" if part is None else str(part) for part in key)


def primary(key):
    _, _, base, rule, _, _ = key
    return (rule == "STEPS-1" and base.startswith("COPY-LAW")) or (
        rule == "MET" and base in ("RING-LAW", "CAP-3(RETIRE)", "CAP-3(OFFSHOOT)")
    )


class Checks:
    def __init__(self):
        self.count = Counter()
        self.example = {}

    def require(self, name, condition, example):
        if not condition:
            self.count[name] += 1
            self.example.setdefault(name, example)

    def report(self):
        return {"counts": self.count, "first_example": self.example}


def clock_key(p0, t0, periods):
    return tuple(p0), t0, tuple(periods)


def eligible_windows(periods):
    return tuple(
        j for j in (0, 1)
        if len(periods[j:j + 4]) == 4 and len(set(periods[j:j + 4])) == 1
    )


def earliest(artifact, lower, upper):
    return artifact is not None and lower < artifact <= upper


def bar_status(bar, horizon_a, period, checks, where):
    """Use first trace mismatches and reached rounds before reading verdict labels."""
    if "B" not in bar:
        return None
    tick = bar["t_bar"]
    horizon = min(horizon_a, bar["B"]["rounds"])
    comparison_end = min(horizon, tick + 2 * period)
    difference = earliest(bar["course_differs"], tick, comparison_end)
    if difference:
        status = "differs"
    elif horizon >= tick + 2 * period:
        status = "equal"
    else:
        status = "not grown"
    checks.require("bar trace status", status == bar["c_iii"], where)
    checks.require("two-period coverage", bar["grown_2_periods"] == (horizon >= tick + 2 * period), where)
    checks.require("four-period coverage", bar["grown_4_periods"] == (horizon >= tick + 4 * period), where)
    mask_matches = False
    mask_short = False
    if "M" in bar:
        mask_end = min(bar["B"]["rounds"], tick + 2 * period)
        mask_short = bar["M"]["rounds"] < mask_end
        same_as_bar = not mask_short and not earliest(bar["M_differs_from_B_at"], tick, mask_end)
        checks.require("masked two-period equality", same_as_bar == bar["M_equals_B_2"], where)
        mask_matches = difference and same_as_bar
    own_late = sorted(int(t) for t, count in bar["own_B_after_bar_by_round"].items()
                      if count > 0 and int(t) > tick + 2 * period)
    checks.require("late own knots", own_late == bar["own_after_lag_rounds"], where)
    checks.require("all own knots after bar",
                   sum(bar["own_B_after_bar_by_round"].values()) == bar["e"], where)
    return {
        "status": status, "late_own_knots": own_late, "mask_matches": mask_matches, "mask_short": mask_short,
        "two_periods": horizon >= tick + 2 * period, "four_periods": horizon >= tick + 4 * period,
    }


def comparison_differs(bar, alternative, period, checks, where):
    value = bar[alternative]
    if isinstance(value, dict):
        return earliest(value["course_differs"], bar["t_bar"], bar["t_bar"] + 2 * period)
    if alternative == "Ball":
        checks.require("known Ball alias", value == "one qualifying part: the same as B(r)", where)
        return earliest(bar["course_differs"], bar["t_bar"], bar["t_bar"] + 2 * period)
    checks.require("known B-prime alias",
                   value == "no parts given off: nothing barred (the same as run A)", where)
    return False


def recount_tests(limit, checks):
    tests_by_run = defaultdict(Counter)
    tests_by_clock = defaultdict(lambda: defaultdict(Counter))
    tested_second_parts = defaultdict(set)
    main_totals = Counter()
    outcomes = defaultdict(Counter)
    holds_by_rule = defaultdict(Counter)
    positives = defaultdict(list)
    unconfirmed = defaultdict(Counter)
    c_possible = set()

    for row in rows("run4", limit):
        if "P0" not in row:
            main_totals["rows without a recorded test"] += 1
            continue
        key = run_key(row)
        clock = clock_key(row["P0"], row["t0"], row["Y_periods"])
        round_chosen = row["t_j"]
        period = row["period"]
        t_all = row["tick_rounds"]
        where = [*key, list(clock), row["j"], row["X"]]
        grouped = (key, clock, row["j"])
        second = tuple(row["X"])
        checks.require("one row per clock and second part", second not in tested_second_parts[grouped], where)
        tested_second_parts[grouped].add(second)
        checks.require("at most eight second parts per clock and round", len(tested_second_parts[grouped]) <= 8, where)
        checks.require("eligible clock and tick",
                       row["Y_size"] >= 2 and row["j"] in eligible_windows(row["Y_periods"]) and
                       t_all == [round_chosen + i * period for i in range(5)] and
                       round_chosen == row["t0"] + sum(row["Y_periods"][:row["j"]]) and
                       not set(row["P_j"]).intersection(row["X"]), where)
        own = row["own_A_by_round"]
        own_by_period = [sum(own.get(str(t), 0) for t in range(a + 1, b + 1))
                         for a, b in zip(t_all, t_all[1:])]
        clause1 = own_by_period[0] > 0 and len(set(own_by_period)) == 1
        uniform_per_round = len(set(own.get(str(t), 0) for t in range(t_all[0] + 1, t_all[-1] + 1))) == 1
        checks.require("own knots per period", own_by_period == row["own_A_per_period"], where)
        checks.require("clause 1", clause1 == row["clause1"], where)
        horizon_a = row["run_A"]["rounds"]
        bars = []
        count = Counter(tests=1)
        count["A enough for every two-period comparison"] += horizon_a >= t_all[3] + 2 * period
        count["A enough for every four-period comparison"] += horizon_a >= t_all[3] + 4 * period
        if clause1:
            count["fixed positive own count"] += 1
            count["fixed positive own count and A long enough"] += horizon_a >= t_all[3] + 4 * period
            count["fixed positive own count also uniform per round"] += uniform_per_round
        for index, bar in enumerate(row["bars"], start=1):
            checks.require("bar order and tick",
                           bar["r"] == index and ("B" not in bar or bar["t_bar"] == t_all[index]), where)
            observation = bar_status(bar, horizon_a, period, checks, where)
            if observation is None:
                count["bars skipped"] += 1
                continue
            bars.append(observation)
            count["bars stored"] += 1
            count[f"bar {observation['status']}"] += 1
            count["mask reproduced difference"] += observation["mask_matches"]
            count["mask did not reproduce difference"] += (
                observation["status"] == "differs" and not observation["mask_matches"]
            )
            count["mask run recorded"] += "M" in bar
            count["mask did not reach required comparison end"] += observation["mask_short"]
            count["mask checked by two periods and A and B differ later"] += (
                "M" in bar and observation["status"] == "equal" and bar["M_equals_B_2"]
            )
            count["bars with X descendant in barred part"] += bar["X_desc_in_barred_part"] > 0
            count["B-prime actual bar"] += isinstance(bar["B'"], dict)
            count["Ball actual additional bar"] += isinstance(bar["Ball"], dict)
            b_prime_diff = comparison_differs(bar, "B'", period, checks, where)
            count["B-prime differs within two periods"] += b_prime_diff
            count["B-prime differs within two periods while B is equal"] += (
                b_prime_diff and observation["status"] == "equal"
            )
            count["Ball differs within two periods"] += comparison_differs(bar, "Ball", period, checks, where)

        c_reason = None
        if not clause1:
            c_reason = "clause 1"
        elif any(bar["late_own_knots"] for bar in bars):
            c_reason = "an own knot after the lag"
        else:
            c_possible.add((key, clock, row["j"], second))
        verdict_c = "fails" if c_reason else "unresolved here"
        if any(bar["status"] == "equal" for bar in bars):
            verdict_iii = "fails"
        elif len(bars) == 3 and all(bar["mask_matches"] for bar in bars):
            verdict_iii = "holds"
        else:
            verdict_iii = "undecided"
        checks.require("C verdict", verdict_c == row["verdict_C"], where)
        checks.require("C reason", c_reason == row.get("C_fail_reason"), where)
        checks.require("C-iii verdict", verdict_iii == row["verdict_C_iii"], where)
        checks.require("skipped bars follow two decided failures",
                       len(bars) == 3 or (verdict_c == verdict_iii == "fails"), where)
        count[f"C {verdict_c}"] += 1
        count[f"C-iii {verdict_iii}"] += 1
        count["C fails at clause 1"] += c_reason == "clause 1"
        count["C fails from late own birth"] += c_reason == "an own knot after the lag"
        count["C decided at or before first bar"] += not clause1 or bool(bars[0]["late_own_knots"])
        count["C-iii decided failure at first bar"] += bars[0]["status"] == "equal"
        count["both fail at or before first bar"] += (
            (not clause1 or bool(bars[0]["late_own_knots"])) and bars[0]["status"] == "equal"
        )
        count["three bars stored"] += len(bars) == 3
        count["all three bars reach two periods"] += len(bars) == 3 and all(bar["two_periods"] for bar in bars)
        count["all three bars reach four periods"] += len(bars) == 3 and all(bar["four_periods"] for bar in bars)
        count["all three bars differ"] += len(bars) == 3 and all(bar["status"] == "differs" for bar in bars)
        treatment = (key[2].endswith("(OFFSHOOT)") and key[-1] == "nae" and
                     all(bar["joint_B_after_bar"] == 0 for bar in row["bars"] if "B" in bar))
        checks.require("short-treatment flag", treatment == row.get("ruled_out_by_treatment", False), where)
        count["ruled out by short treatment"] += treatment
        if verdict_iii == "undecided":
            unconfirmed[key][(clock, row["j"])] += 1
            count["qualifies for second pass judged on C-iii alone"] += 1
            count["undecided with at least one bar short of two periods"] += any(not b["two_periods"] for b in bars)
            for i, bar in enumerate(bars, start=1):
                count[f"undecided with bar {i} short of two periods"] += not bar["two_periods"]
            count["every bar differs without a reproduced mask"] += (
                len(bars) == 3 and all(b["status"] == "differs" and not b["mask_matches"] for b in bars)
            )
        if verdict_iii == "holds":
            outcome = row["X_barred"]
            common_end = min(horizon_a, outcome["rounds"])
            ticks_a = [t for t in outcome["Y_ticks_A"] if t <= common_end]
            ticks_x = [t for t in outcome["Y_ticks_X_barred"] if t <= common_end]
            positive = {
                "clock": clock, "second_part": second, "j": row["j"], "round_chosen": round_chosen,
                "period_rounds": period, "own_per_period": own_by_period, "C_failure": c_reason,
                "Y_ticks_A": ticks_a, "Y_ticks_X_barred": ticks_x,
                "Y_ticks_A_beyond_common_horizon": [t for t in outcome["Y_ticks_A"] if t > common_end],
                "Y_ticks_X_barred_beyond_common_horizon": [t for t in outcome["Y_ticks_X_barred"] if t > common_end],
                "Y_comparison_horizon": common_end,
                "bar_to_first_difference_rounds": [b["course_differs"] - b["t_bar"] for b in row["bars"]],
                "B_prime_differs_at_all_three": count["B-prime differs within two periods"] == 3,
                "B_all_differs_at_all_three": count["Ball differs within two periods"] == 3,
                "B_prime_differences": [
                    b["B'"]["course_differs"] if isinstance(b["B'"], dict) else None for b in row["bars"]
                ],
                "meeting_classes": row["what_made_meeting"], "first_difference_kind": [b["way"] for b in row["bars"]],
                "two_periods_all_bars": all(b["two_periods"] for b in bars),
                "four_periods_all_bars": all(b["four_periods"] for b in bars),
                "fixed_count_uniform_per_round": uniform_per_round,
                "own_after_four_periods_in_A": sum(c for t, c in own.items() if int(t) > t_all[-1]),
            }
            positives[key].append(positive)
            hold = holds_by_rule[key[3]]
            hold["tests"] += 1
            hold["fixed positive count"] += clause1
            hold["fixed positive count also uniform per round"] += clause1 and uniform_per_round
            hold["strictly increasing counts"] += all(a < b for a, b in zip(own_by_period, own_by_period[1:]))
            hold["strictly decreasing counts"] += all(a > b for a, b in zip(own_by_period, own_by_period[1:]))
            hold["nonincreasing unequal counts"] += (
                not clause1 and all(a >= b for a, b in zip(own_by_period, own_by_period[1:]))
            )
            hold["first course difference entirely in groups or owing"] += (
                set(positive["first_difference_kind"]) == {"a group or owing"}
            )
            hold["Y ticks unchanged with X barred"] += ticks_a == ticks_x
            hold["Y ticks with X barred agree only within the shared horizon"] += (
                ticks_a == ticks_x and outcome["Y_ticks_A"] != outcome["Y_ticks_X_barred"]
            )
            hold["Y ticks fewer with X barred"] += len(ticks_x) < len(ticks_a)
            hold["Y ticks absent with X barred"] += not ticks_x and bool(ticks_a)
            hold["B-prime differs at all three"] += positive["B_prime_differs_at_all_three"]
            hold["B-prime earlier than B at all three"] += all(
                alt is not None and alt < bar["course_differs"]
                for alt, bar in zip(positive["B_prime_differences"], row["bars"])
            )
            hold["Ball differs at all three"] += positive["B_all_differs_at_all_three"]
            hold["two periods reached for all bars"] += positive["two_periods_all_bars"]
            hold["four periods reached for all bars"] += positive["four_periods_all_bars"]
            hold[f"X size {len(second)}"] += 1
            hold[f"meeting classes {', '.join(row['what_made_meeting'])}"] += 1
            hold[f"own counts {tuple(own_by_period)}"] += 1

        tests_by_run[key].update(count)
        tests_by_clock[key][(clock, row["j"])].update(count)
        main_totals.update(count)
        outcomes[key[0]].update(count)
        outcomes[f"run A stop: {row['run_A']['stop']}"].update(count)
        if primary(key):
            outcomes[f"primary {key[0]}"].update(count)
    return main_totals, outcomes, tests_by_run, tests_by_clock, positives, unconfirmed, holds_by_rule, c_possible


def clock_inventory(row, positives, unconfirmed, checks, run):
    series = row["nopast_series"]
    has_four = {}
    grouped = {}
    full_period_tuple = {}
    for record in series:
        periods = tuple(record["periods"])
        size = len(record["P0"])
        has_equal_periods = size >= 2 and any(
            len(set(periods[j:j + 4])) == 1 for j in range(len(periods) - 3)
        )
        checks.require("census four-period clock label", has_equal_periods == record["clock"], run)
        if not has_equal_periods:
            continue
        key = clock_key(record["P0"], record["t0"], periods)
        has_four[key] = eligible_windows(periods)
        shape = (size, record["t0"] % 2)
        for pool, signature in ((grouped, (shape, frozenset(periods))),
                                (full_period_tuple, (shape, periods))):
            if signature not in pool or min(key[0]) < min(pool[signature][0]):
                pool[signature] = key

    if positives or unconfirmed:
        by_clock = {clock_key(s["P0"], s["t0"], s["periods"]): s for s in series}
        for positive in positives:
            y = by_clock[positive["clock"]]
            ticks = y["ticks"][positive["j"]:positive["j"] + 4]
            positive["Y_parts_given_off_counts"] = [tick[2] for tick in ticks]
            post_x_return_rounds = set()
            for record in series:
                if record["size"] != len(positive["second_part"]):
                    continue
                members_at_round = [(record["t0"], tuple(record["P0"]))]
                members_at_round += [(t[0], tuple(t[1])) for t in record["ticks"]]
                if (positive["round_chosen"], positive["second_part"]) in members_at_round:
                    post_x_return_rounds.update(t[0] for t in record["ticks"] if t[0] > positive["round_chosen"])
            positive["X_baseline_returns_in_census_series"] = sorted(post_x_return_rounds)
    selected = {(key, j) for key in grouped.values() for j in has_four[key]}
    metrics = Counter(
        clocks_with_four_equal_periods_anywhere=len(has_four),
        clocks_with_a_registered_choice_round=sum(bool(v) for v in has_four.values()),
        windows_without_clock_grouping=sum(map(len, has_four.values())),
        windows_using_whole_period_tuple=sum(len(has_four[key]) for key in full_period_tuple.values()),
        windows_using_set_of_period_lengths=len(selected),
    )
    for (clock, j), count in unconfirmed.items():
        four_ticks = by_clock[clock]["ticks"][j:j + 4]
        metrics["undecided C-iii tests whose clock gives off parts at all four ticks"] += (
            count if all(tick[2] > 0 for tick in four_ticks) else 0
        )
    return metrics, selected


def census_opportunities(limit, checks, starts, rules, tests_by_run, tests_by_clock, positives, unconfirmed):
    files = [*(f"run1_part{i}" for i in range(1, 9)), "run2", "run3"]
    rules = [None if r["id"] == "none" else r["id"] for r in rules["rules"] if not r["arm"].startswith("ladder")]
    rules += [f"STEPS-{i}" for i in range(3, 9)]
    eligible = {}
    saved_order = []
    status = defaultdict(Counter)
    by_law = defaultdict(Counter)
    for file in files:
        for row in rows(file, limit):
            key = run_key(row)
            status[key[0]]["census rows"] += 1
            by_law[law_key(key)]["census rows"] += 1
            if "nopast_series" not in row:
                status[key[0]]["census rows without series"] += 1
                by_law[law_key(key)]["census rows without series"] += 1
                continue
            census_clock_inventory = clock_inventory(row, positives.get(key, ()), unconfirmed.get(key, {}), checks, key)
            has_clock = census_clock_inventory[0]["clocks_with_four_equal_periods_anywhere"] > 0
            checks.require("census clock-bearing run label", has_clock == row["nopast"]["clock"], key)
            if has_clock:
                checks.require("unique census run with a clock", key not in eligible, key)
                status[key[0]]["clock-bearing census runs"] += 1
                by_law[law_key(key)]["clock-bearing census runs"] += 1
                eligible[key] = census_clock_inventory
                saved_order.append(key)
    start_order = {start: index for index, start in enumerate(starts)}

    def run_order(key):
        group, start, base, rule, choice, knot_law = key
        return (GROUPS.index(group), start_order.get(start, len(start_order)), BASES.index(base),
                rules.index(rule), CHOICES.index(choice), KNOT_LAWS.index(knot_law))

    selected = set(saved_order[:5000])
    registered = set(sorted(eligible, key=run_order)[:5000])
    discrepancy = {
        "actual_prefix_only": [{"run": r, "clock_inventory": dict(eligible[r][0])}
                               for r in sorted(selected - registered, key=report_key)],
        "registered_prefix_only": [{"run": r, "clock_inventory": dict(eligible[r][0])}
                                   for r in sorted(registered - selected, key=report_key)],
    }
    if limit is None:
        checks.require("every recorded test in the registered prefix",
                       set(tests_by_run) <= selected, sorted(set(tests_by_run) - selected, key=report_key)[:10])
    run_inventory = {}
    for key, (opportunities, windows) in eligible.items():
        in_prefix = key in selected
        runs = status[key[0]], by_law[law_key(key)]
        for bucket in runs:
            bucket.update(opportunities)
            bucket["in tested prefix"] += in_prefix
            bucket["has at least one test"] += key in tests_by_run
            bucket["in tested prefix with no persisted tests"] += in_prefix and key not in tests_by_run
        observed = set(tests_by_clock.get(key, ()))
        if key in tests_by_run:
            checks.require("recorded windows follow grouped clock reading", observed <= windows,
                           [key, list(observed - windows)[:5]])
        if in_prefix:
            opportunities["selected windows with no test"] += len(windows - observed)
            if key in tests_by_run:
                opportunities.update(tests_by_run[key])
            for bucket in runs:
                bucket["selected windows with no test"] += opportunities["selected windows with no test"]
                bucket["windows without clock grouping in prefix"] += opportunities["windows_without_clock_grouping"]
                bucket["windows using whole period tuple in prefix"] += opportunities["windows_using_whole_period_tuple"]
                bucket["windows using set of period lengths in prefix"] += opportunities["windows_using_set_of_period_lengths"]
        row = {"in_prefix": in_prefix, "counts": opportunities}
        if in_prefix:
            row["selected_windows"] = [
                [clock, j, {label: count for label, count in tests_by_clock.get(key, {}).get((clock, j), {}).items()
                            if count}]
                for clock, j in sorted(windows)
            ]
        run_inventory[report_key(key)] = row
    for key, count in tests_by_run.items():
        by_law[law_key(key)].update(count)
    total_status = sum(status.values(), Counter())
    by_primary_law = {report_key(key): counts for key, counts in by_law.items()
                      if primary((key[0], "", *key[1:]))}
    return total_status, status, by_law, by_primary_law, run_inventory, discrepancy


def numbering_key(row):
    spec = row["numbering"]
    return tuple(spec["dist"]), tuple(spec["knots"])


def normalized_shift_name(name):
    words = name.replace(",", "").split()
    return int(words[1]), words[2:3] in (["distinctions"], ["reversed"]), words[-2:] == ["knots", "reversed"]


def rebased_start(stars, distinctions, knots):
    name = {distinction: rank for rank, distinction in enumerate(distinctions)}
    return [sorted(name[distinction] for distinction in stars[i]) for i in knots]


def check_numbered_row(row, stars, checks):
    key = run_key(row["item"])
    ordering = numbering_key(row)
    where = [key, ordering, row["swap"]]
    expected = rebased_start(stars[key[1]], *ordering)
    checks.require("numbered start from frozen stars", expected == row["named_start"], where)
    holds_from_tests = Counter(test["verdict_C_iii"] for test in row["held_tests"])
    # The record retains at most the first six supporting tests per row.
    checks.require("numbering held count from retained tests",
                   holds_from_tests["holds"] == min(6, row["C_iii_holds"]), where)
    survives = holds_from_tests["holds"] > 0
    checks.require("numbering survival from retained tests", survives == row["survives"], where)
    if survives:
        disposition = "has a hold"
    elif row.get("unfinished") or row["unfinished_tests"] or row["undecided_C_iii"]:
        disposition = "no hold, with unfinished or undecided tests"
    elif row["tests"]:
        disposition = "has only decided failures"
    else:
        disposition = "no tests"
    if len(expected) == 2:
        shared, = set(expected[0]) & set(expected[1])
        least = tuple(shared == min(star) for star in expected)
        checks.require("shared distinction rank from frozen stars", list(least) == row["shared_least_in_knot"], where)
    else:
        least = None
    return key, disposition, least


def registered_numberings(stars):
    names = sorted({name for knot in stars for name in knot})
    knots = tuple(range(len(stars)))
    if len(names) <= 6:
        return set(product(permutations(names), permutations(knots)))
    rotations = [tuple(names[i:] + names[:i]) for i in range(len(names))]
    return {(dist, order) for shift in rotations for dist in (shift, shift[::-1]) for order in (knots, knots[::-1])}


def summarize_numberings(records, stars, checks, near=False, full=True):
    tables = defaultdict(Counter)
    by_case = defaultdict(dict)
    distinct = defaultdict(dict)
    for row in records:
        key, disposition, least = check_numbered_row(row, stars, checks)
        ordering = numbering_key(row)
        checks.require("unique numbering per case", ordering not in by_case[key], [key, ordering])
        by_case[key][ordering] = disposition
        outcome = tables[key]
        outcome["numberings"] += 1
        outcome[disposition] += 1
        outcome["tests"] += row["tests"]
        outcome["test holds"] += row["C_iii_holds"]
        outcome["test undecided"] += row["undecided_C_iii"]
        outcome["test unfinished"] += row["unfinished_tests"]
        outcome["C test holds"] += row["C_holds"]
        named = tuple(tuple(knot) for knot in row["named_start"])
        survives = disposition == "has a hold"
        if named in distinct[key]:
            checks.require("same named start has same verdict", distinct[key][named] == disposition, [key, named])
        distinct[key][named] = disposition
        if least is not None:
            expected = any(least) if near or key[3] == "STEPS-2:join" else least[1]
            outcome[f"shared least in first {least[0]}, second {least[1]}: {disposition}"] += 1
            checks.require("shared distinction rank predicts survival", survives == expected, [key, ordering])
        elif row["numbering"]["kind"].startswith("shift 0"):
            outcome["four reversals with a hold"] += survives
    for key, outcome in tables.items():
        if full:
            checks.require("complete registered numbering roster",
                           set(by_case[key]) == registered_numberings(stars[key[1]]), key)
        outcome["distinct named starts"] = len(distinct[key])
        outcome["distinct named starts that hold"] = sum(x == "has a hold" for x in distinct[key].values())
    return {report_key(key): data for key, data in tables.items()}


def numbering_controls(limit, checks, stars, positive_cases):
    grouped = list(rows("run5", limit))
    every = list(rows("run5_every_clock", limit))
    near = list(rows("run5_near_case", limit))
    by_numbering = {(run_key(r["item"]), numbering_key(r)): r for r in grouped}
    every_by_numbering = {(run_key(r["item"]), numbering_key(r)): r for r in every}
    if limit is None:
        checks.require("numbered cases match positive run A cases",
                       {k[0] for k in by_numbering} == set(positive_cases), "run5")
        expected_every = {key for key, r in by_numbering.items()
                          if r["item"]["rule"] == "STEPS-2" and not r["held_tests"]}
        checks.require("every-clock reruns all grouped STEPS-2 non-passes",
                       set(every_by_numbering) == expected_every, "run5_every_clock")
    merged = [every_by_numbering.get((run_key(row["item"]), numbering_key(row)), row) for row in grouped]
    tables = {
        "grouped_numberings": summarize_numberings(grouped, stars, checks, full=limit is None),
        "every_clock_where_rerun": summarize_numberings(merged, stars, checks, full=limit is None),
        "one_member_near_case": summarize_numberings(near, stars, checks, near=True, full=limit is None),
    }
    for name in ("grouped_numberings", "every_clock_where_rerun"):
        steps_two = [(key, tally) for key, tally in tables[name].items() if " | STEPS-2 | " in key]
        if steps_two:
            ordered = sorted(steps_two, key=lambda item: item[1].get("has a hold", 0) / item[1]["numberings"])
            tables[f"{name}_steps_two_summary"] = {
                "cases": len(steps_two),
                "numberings": sum(tally["numberings"] for _, tally in steps_two),
                "pass_range": [
                    {"case": case, "passed": tally.get("has a hold", 0), "numberings": tally["numberings"]}
                    for case, tally in (ordered[0], ordered[-1])
                ],
                "cases with at least one only-decided-failures numbering": sum(
                    tally.get("has only decided failures", 0) > 0 for _, tally in steps_two
                ),
                "cases with at least one no-tests numbering": sum(tally.get("no tests", 0) > 0 for _, tally in steps_two),
                "cases with at least one no-tests or only-decided-failures numbering": sum(
                    tally.get("no tests", 0) + tally.get("has only decided failures", 0) > 0 for _, tally in steps_two
                ),
            }
    changes = Counter()
    if limit is None:
        prototype = read_json(FROZEN / "compare.json")
        retained_shift_keys = {
            (r["item"]["start"], r["item"]["choice"], r["item"]["knot_law"],
             normalized_shift_name(r["numbering"]["kind"])):
            (bool(r["held_tests"]), bool(every_by_numbering.get(k, r)["held_tests"]))
            for k, r in by_numbering.items() if r["item"]["rule"] == "STEPS-2"
        }
        compared = set()
        for r in prototype["shifts"]["rows"]:
            key = (r["start"], r["choice"], r["knot_law"], normalized_shift_name(r["numbering"]))
            original, supplement = retained_shift_keys[key]
            compared.add(key)
            changes["shared shift rows"] += 1
            changes["grouped differences from prototype on shared shifts"] += original != r["passes"]
            changes["every-clock differences from prototype on shared shifts"] += supplement != r["passes"]
            changes["changed in supplement on shared shifts"] += original != supplement
        for key, (original, supplement) in retained_shift_keys.items():
            if key not in compared:
                changes["additional shift rows"] += 1
                changes["changed in supplement on additional shifts"] += original != supplement
        four = defaultdict(Counter)
        shared_cases = {key[:3] for key in compared}
        for row in merged:
            source = row["item"]
            if source["rule"] != "STEPS-2":
                continue
            distinctions, knots = numbering_key(row)
            values = tuple(sorted(distinctions))
            star_order = tuple(sorted(knots))
            if distinctions in (values, values[::-1]) and knots in (star_order, star_order[::-1]):
                label = (source["start"], source["choice"], source["knot_law"])
                four[label]["run"] += 1
                four[label]["pass"] += bool(row["held_tests"])
        changes["original cases passing all four reversals"] = sum(
            v["run"] == v["pass"] == 4 for k, v in four.items() if k in shared_cases
        )
        changes["additional cases passing all four reversals"] = sum(
            v["run"] == v["pass"] == 4 for k, v in four.items() if k not in shared_cases
        )
    tables["clock_reading_effect"] = changes
    return tables


def swap_controls(limit, checks, stars, positive_cases):
    output = {}
    origins = {}
    for stem in ("run6", "run6_every_clock"):
        indexed = {}
        cases = defaultdict(Counter)
        outcomes = defaultdict(Counter)
        for row in rows(stem, limit):
            key, disposition, _ = check_numbered_row(row, stars, checks)
            reading = row["swap"]
            checks.require("unique case and swap", (key, reading) not in indexed, [key, reading])
            indexed[(key, reading)] = disposition
            cases[reading]["cases"] += 1
            cases[reading][disposition] += 1
            cases[reading]["tests"] += row["tests"]
            cases[reading]["test holds"] += row["C_iii_holds"]
            cases[reading]["test undecided"] += row["undecided_C_iii"]
            cases[reading]["test unfinished"] += row["unfinished_tests"]
            cases[reading]["C test holds"] += row["C_holds"]
            outcomes[key[3], reading][disposition] += 1
        if limit is None:
            checks.require("same cases under each swap", set(k[0] for k in indexed) == set(positive_cases), stem)
            checks.require("all seven swaps present per case",
                           set(cases) == {"names reversed", "order of births reversed", "demand before the takes",
                                          "fresh by parents", "HOLD", "the ration", "the knot law"}
                           and all(v["cases"] == len(positive_cases) for v in cases.values()), stem)
        changes = {report_key((*key, reading)): [origins.get((key, reading)), outcome]
                   for (key, reading), outcome in indexed.items()
                   if origins and origins.get((key, reading)) != outcome}
        output[stem] = {
            "by_swap": cases,
            "by_rule_and_swap": {report_key(k): v for k, v in outcomes.items()},
            "changed_dispositions": changes,
            "each_case_and_swap": {report_key((*key, reading)): value for (key, reading), value in indexed.items()},
        }
        if stem == "run6":
            origins = indexed
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", type=int, help="maximum rows per input stream")
    parser.add_argument("--write", action="store_true", help="write the full recount beside this script")
    args = parser.parse_args()
    if args.smoke is not None and args.write:
        parser.error("--smoke and --write are mutually exclusive")
    starts = read_json(FROZEN / "starts.json")["named"]
    rules = read_json(FROZEN / "rules.json")
    checks = Checks()
    total, group_totals, by_run, by_clock, holds, unconfirmed, held_breakdown, c_possible = recount_tests(args.smoke, checks)
    population, population_by_group, law, primary_law, inventory, prefix_discrepancy = census_opportunities(
        args.smoke, checks, starts, rules, by_run, by_clock, holds, unconfirmed
    )
    numbered = numbering_controls(args.smoke, checks, starts, holds)
    swaps = swap_controls(args.smoke, checks, starts, holds)
    report = {
        "scope": {
            "run_4": "The verdict recount uses recorded own births by round, first trace differences and reached rounds. "
                     "The stored fields do not contain the complete growth or course required to derive those inputs.",
            "run_5_and_6": "Each numbered start is reconstructed from the frozen stars. Survival is the presence of a "
                           "supporting test in the retained listing, with undisclosed tests represented by stored tallies.",
            "clock_grouping": "The ungrouped window counts keep the least-name first-return convention and j = 0 or 1. "
                              "The opportunity counts are before testing eligibility of any second part.",
            "counting_units": "The 88,299 rows count tests once. Numbering counts weight each order once, including "
                              "orders that produce the same named start. Swap counts count each law and start case once.",
        },
        "run_4": {
            "tests": total,
            "test_groups": group_totals,
            "underlying_runs": population,
            "underlying_runs_by_group": population_by_group,
            "saved_vs_registered_order": prefix_discrepancy,
            "primary_laws": primary_law,
            "every_law": {report_key(k): v for k, v in law.items()},
            "C_tests_requiring_a_positive_decision": len(c_possible),
            "C_iii_by_rule": held_breakdown,
            "C_iii_holds_by_run": {report_key(k): v for k, v in holds.items()},
        },
        "run_5": numbered,
        "run_6": swaps,
        "record_consistency": checks.report(),
    }
    print(json.dumps({"run_4_tests": total, "run_4_underlying_runs": population,
                      "record_consistency": checks.report()}, sort_keys=True))
    if args.write:
        (HERE / "verdict_counts.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        clock_index = {"run_key": RUN_FIELDS, "law_key": LAW_FIELDS,
                       "selected_window": ["clock", "j", "observed_counts"],
                       "clock": ["first_part", "first_round", "periods"],
                       "run_opportunities": inventory}
        compact_index = json.dumps(clock_index, separators=(",", ":"), sort_keys=True) + "\n"
        (HERE / "verdict_opportunities.json.gz").write_bytes(gzip.compress(compact_index.encode("utf-8"), mtime=0))


if __name__ == "__main__":
    main()
