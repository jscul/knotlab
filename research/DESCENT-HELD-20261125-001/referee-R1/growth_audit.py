"""Replay growth, start census, restart controls, and hand cases."""

import argparse
from collections import Counter, defaultdict
from dataclasses import replace
import gzip
from itertools import combinations, permutations, product
import json
from math import factorial
from pathlib import Path
import random
from time import perf_counter

import networkx as nx

from growth import Law, Structure, complete_round, groups, run


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = "DESCENT-HELD-20261125-001A"
INPUT = ROOT / "research" / TICKET
OUTPUT = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_order_in_own_places"
FORMS = {"base": None, "PU": "PU", "PB": "PB", "BB": "BB"}
FORM_NAMES = {"base": "base", "PU": "NEXT3-PLACES (usable)",
              "PB": "NEXT3-PLACES (barred)", "BB": "NEXT3-BARRED"}


def load(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as source:
        return json.load(source)


class Comparison:
    def __init__(self):
        self.cases = Counter()
        self.disagreements = Counter()
        self.examples = {}

    def compare(self, category, name, obtained, expected):
        self.cases[category] += 1
        if obtained != expected:
            self.disagreements[category] += 1
            examples = self.examples.setdefault(category, [])
            if len(examples) < 4:
                examples.append({"case": name, "obtained": obtained, "saved": expected})

    def fields(self, category, name, obtained, expected):
        self.compare(category, name, obtained, {key: expected[key] for key in obtained})


def birth_totals(records):
    return [len(record.births) for record in records]


def depth_data(trial, start):
    steps = [0] * len(start.stars)
    sizes = [len(star) for star in trial.structure.stars]
    unequal = []
    unequal_mod3 = []
    greatest_by_round = {}
    waiting_failure = []
    first_some = first_every = first_fives = None
    stamp_three_right = True
    for number, record in enumerate(trial.rounds, 1):
        acting_start = {parent for birth in record.births for parent in birth.parents
                        if parent < len(start.stars)}
        if any(start.meetings[knot] & acting_start for knot in record.waited
               if knot < len(start.stars)):
            waiting_failure.append(number)
        for birth in record.births:
            parents = [steps[parent] for parent in birth.parents]
            step = max(parents) + 1
            steps.append(step)
            differences = [step - parent for parent in parents]
            greatest_by_round[str(number)] = max(greatest_by_round.get(str(number), 0),
                                                max(differences))
            if len(set(parents)) > 1:
                unequal.append((number, birth.knot))
            if len({parent % 3 for parent in parents}) > 1:
                unequal_mod3.append((number, birth.knot))
            if first_fives is None and any(difference % 5 not in {1, 2}
                                           for difference in differences):
                first_fives = number
            stamp_three_right &= all(difference % 3 == 1 for difference in differences)
            place_mismatch = [(sizes[birth.knot] - sizes[parent]) % 3 != 1
                              for parent in birth.parents]
            if first_some is None and any(place_mismatch):
                first_some = number
            if first_every is None and all(place_mismatch):
                first_every = number
    return {
        "rounds": sum(record.status == "changed" for record in trial.rounds),
        "rounds_run": len(trial.rounds),
        "knots": len(trial.structure.stars),
        "end": trial.status,
        "births": birth_totals(trial.rounds),
        "counted": bool(unequal),
        "counted_first_round": unequal[0][0] if unequal else None,
        "bprime_fails": bool(unequal_mod3),
        "bprime_first_round": unequal_mod3[0][0] if unequal_mod3 else None,
        "greatest": max(greatest_by_round.values(), default=0),
        "greatest_by_round": greatest_by_round,
        "max_ps": max(steps),
        "lq_fails_rounds": waiting_failure,
        "first_no_birth_round": next((r for r, record in enumerate(trial.rounds, 1)
                                      if not record.births), None),
        "closing_births": sum(record.closing for record in trial.rounds),
        "fives_right_on": first_fives is None,
        "fives_first_wrong_round": first_fives,
        "three_stamp_right_on": stamp_three_right,
        "m2_fail_round_some": first_some,
        "m2_fail_round_every": first_every,
    }, steps, unequal_mod3


def parity_fails(structure):
    """The shared definitions' cut test using the distinguished outside."""
    outside = len(structure.stars)
    meetings = [others.copy() for others in structure.meetings] + [set()]
    for distinction in structure.loose:
        knot, = structure.holders[distinction]
        meetings[outside].add(knot)
        meetings[knot].add(outside)
    failed = []
    for omitted in range(outside):
        incident = meetings[omitted]
        if len(incident) <= 1:
            continue
        first = next(iter(incident))
        seen = {omitted, first}
        pending = [first]
        while pending:
            new = meetings[pending.pop()] - seen
            pending.extend(new)
            seen.update(new)
        if not incident <= seen:
            failed.append(omitted)
    return failed


def start_agreement(structure, form):
    counts = [knot_count(structure, knot, form) for knot in range(len(structure.stars))]
    return all(counts[left] == counts[right]
               for left, others in enumerate(structure.meetings) for right in others)


def knot_count(structure, knot, form):
    if form == "BB":
        return sum(place in structure.barred for place in structure.stars[knot]) % 3
    return len(structure.stars[knot]) % 3


def catalogue(max_n):
    """Enumerate starts using atlas meetings and independent renaming checks."""
    for pattern in nx.graph_atlas_g():
        n = len(pattern)
        if not 1 <= n <= max_n or not nx.is_connected(pattern):
            continue
        pairs = list(pattern.edges())
        degrees = tuple(pattern.degree(knot) for knot in range(n))
        pair_set = {tuple(sorted(pair)) for pair in pairs}
        symmetries = [order for order in permutations(range(n))
                      if all(degrees[knot] == degrees[order[knot]] for knot in range(n))
                      and all(tuple(sorted((order[left], order[right]))) in pair_set
                              for left, right in pairs)]
        options = [range(max(0, 3 - degree), 4) for degree in degrees]
        for loose in product(*options):
            if not any(loose):
                continue
            renamed = [tuple(loose[knot] for knot in order) for order in symmetries]
            if min(renamed) != loose:
                continue
            stars = [[] for _ in range(n)]
            for distinction, (left, right) in enumerate(pairs):
                stars[left].append(distinction)
                stars[right].append(distinction)
            distinction = len(pairs)
            for knot, count in enumerate(loose):
                stars[knot].extend(range(distinction, distinction + count))
                distinction += count
            yield Structure(stars), factorial(n) // renamed.count(loose)


def meeting_key(structure):
    """Exact key for a small unbarred pattern with single shared distinctions."""
    single_counts = Counter(holders[0] for holders in structure.holders.values()
                            if len(holders) == 1)
    meetings = [holders for holders in structure.holders.values() if len(holders) == 2]
    if (structure.barred or any(len(star) < 3 for star in structure.stars)
            or not single_counts or max(single_counts.values()) > 3
            or len(set(meetings)) != len(meetings)):
        return None
    classes = defaultdict(list)
    for knot, others in enumerate(structure.meetings):
        classes[len(others), single_counts[knot]].append(knot)
    labels = tuple(sorted(classes))
    canonical = None
    for orders in product(*(permutations(classes[label]) for label in labels)):
        order = {knot: index for index, knot in
                 enumerate(knot for section in orders for knot in section)}
        pattern = tuple(sorted(tuple(sorted((order[left], order[right])))
                               for left, right in meetings))
        if canonical is None or pattern < canonical:
            canonical = pattern
    return tuple((label, len(classes[label])) for label in labels), canonical


def census_restarts(census, kept, laws, saved, check, pilot):
    targets = {meeting_key(start): index for index, (start, _) in enumerate(census)
               if kept[index]}
    if len(targets) != sum(kept):
        raise ValueError("census includes repeated or invalid starts")
    sources = [(index, start) for index, (start, _) in enumerate(census)
               if len(start.stars) <= 4]
    keys = ("prefix", "complete", "subset")
    reaches = {name: [{key: set() for key in keys} for _ in range(2)]
               for name in laws}
    checked = Counter()
    for index, source in (sources[:15] if pilot else sources):
        small = len(source.stars)
        for name, law in laws.items():
            structure = Structure(source.stars)
            complete_round(structure, law)
            candidates = range(small, len(structure.stars))
            for size in range(1, min(5 - small, len(candidates)) + 1):
                prefix = tuple(candidates[:size])
                for subset in combinations(candidates, size):
                    rows = structure.stars[:small] + [structure.stars[knot] for knot in subset]
                    distinctions = set().union(*rows)
                    child = Structure(rows, structure.barred & distinctions)
                    key = meeting_key(child)
                    selections = ["subset"]
                    if subset == prefix:
                        selections.append("prefix")
                    if size == len(candidates):
                        selections.append("complete")
                    checked.update(selections)
                    if key in targets:
                        for source_tier in range(1 + kept[index]):
                            for selection in selections:
                                reaches[name][source_tier][selection].add(targets[key])
    summary = {"candidates_with_multiplicity": dict(checked),
               "sources_all": len(sources), "sources_kept": sum(kept[i] for i, _ in sources)}
    for tier, tier_name in enumerate(("from_223", "from_220_kept")):
        exact = {name: {key: sorted(values) for key, values in tables[tier].items()}
                 for name, tables in reaches.items()}
        unions = {key: set().union(*(tables[tier][key] for tables in reaches.values()))
                  for key in keys}
        result = {key: len(values) for key, values in unions.items()}
        result["within_only"] = len(unions["prefix"] - unions["complete"])
        result["subset_minus_prefix"] = len(unions["subset"] - unions["prefix"])
        result["by_law"] = {name: {key: len(values) for key, values in tables.items()}
                            for name, tables in exact.items()}
        result["complete_list"] = sorted(unions["complete"])
        if not pilot:
            check.fields("census restarts totals", tier_name, result, saved[tier_name])
            for name, tables in exact.items():
                check.fields("census restarts index lists", (tier_name, name), tables,
                             saved[tier_name]["by_law_lists"][name])
        summary[tier_name] = result
    return summary


def parse_law(text, **changes):
    parts = text.split("/") if isinstance(text, str) else text
    return Law(*parts[:3], extras=tuple(parts[3:]), **changes)


def small_cases(input_records, saved, census, check):
    results = {}
    for name, case in input_records.items():
        if name.startswith("H1_"):
            variants = case["forms"]
            law_name = case["base"]
        elif "rounds" in case:
            variants = {"base": case["rounds"]}
            law_name = case["law"]
        else:
            continue
        start = case["stars"]
        if "census_index" in case:
            check.compare("census numbered witnesses", name,
                          [list(row) for row in census[case["census_index"]][0].stars], start)
        for form, expected in variants.items():
            trial = run(start, parse_law(law_name, form=None if form == "base" else form),
                        len(expected))
            steps = [0] * len(start)
            observed = []
            for number, row in enumerate(trial.rounds, 1):
                births = []
                for birth in row.births:
                    parents = [steps[parent] for parent in birth.parents]
                    steps.append(max(parents) + 1)
                    births.append({"knot": birth.knot, "parents": list(birth.parents),
                                   "parents_parent_steps": parents,
                                   "parent_steps": steps[-1],
                                   "places": len(trial.structure.stars[birth.knot]),
                                   "p": len(birth.parents), "F": birth.base_fresh,
                                   "s": birth.added, "barred_at_birth": birth.barred_at_birth})
                observed.append({"round": number, "new_knots": births,
                                 "short_members_that_waited": sorted(row.waited)})
            check.compare("frozen hand birth records", (name, form), observed, expected)
            results[f"{name}/{form}"] = {"births": birth_totals(trial.rounds),
                                        "unequal_parents": [
                                            [round_data["round"], birth]
                                            for round_data in observed
                                            for birth in round_data["new_knots"]
                                            if len(set(birth["parents_parent_steps"])) > 1]}

    for case in saved["b_hand_cases"]["T"]["rows"]:
        start = input_records["T_triangle_closing"]["stars"]
        swap = case["closing_reading"] == "swap"
        law = parse_law(case["law"], form=case["form"], closing_swap=swap)
        trial = run(start, law, 1)
        record, = trial.rounds
        birth, = record.births
        counts = [knot_count(trial.structure, knot, "BB" if law.form == "NEXT3-BARRED" else "PB")
                  for knot in range(len(trial.structure.stars))]
        observed = {"closing_flag": record.closing, "parents": list(birth.parents),
                    "places": len(trial.structure.stars[birth.knot]),
                    "F": birth.base_fresh, "s": birth.added, "z": birth.barred_at_birth,
                    "hyp_s": None if swap else birth.suppressed_added,
                    "parity_test_t1_fail": parity_fails(trial.structure)}
        if not swap:
            observed["counts_after"] = counts
        check.fields("three-knot closing", (case["law"], case["form"], swap), observed, case)
    return results


def lone_cases(rations, saved, check):
    expected = {(record["ration"], record["a"], record["form"]): record
                for record in saved["rows"]}
    result = Counter()
    for ration, sizes in rations.items():
        for count in sizes:
            for form in FORMS:
                source = [tuple(range(count))]
                trial = run(source, Law(ration, "STALL", form=FORMS[form]), 1)
                birth = trial.rounds[0].births[0]
                kept = set(source[0]) | set(birth.taken + birth.fresh)
                partial = Structure(source + [birth.taken + birth.fresh],
                                    trial.structure.barred & kept)
                patterns = Counter((holders, place in partial.barred)
                                   for place, holders in partial.holders.items())
                renamed = Counter({(tuple(sorted(1 - knot for knot in holders)), barred): num
                                   for (holders, barred), num in patterns.items()})
                fixed = 1
                for num in patterns.values():
                    fixed *= factorial(num)
                swaps = fixed if patterns == renamed else 0
                obtained = {"exists": bool(swaps), "start_knot_places": len(partial.stars[0]),
                            "offshoot_places": len(partial.stars[1]),
                            "offshoot_D": birth.demand, "offshoot_barred": birth.barred_at_birth,
                            "renamings_exchanging_the_two_knots": swaps,
                            "renamings_of_the_structure": fixed + swaps, "s": birth.added}
                key = ration, count, FORM_NAMES[form]
                check.fields("lone knot and first offshoot", key, obtained, expected[key])
                result[form + " tested"] += 1
                result[form + " exchanges"] += bool(swaps)
    return result


def named_stars(name, starts):
    if name in starts:
        return starts[name]["stars"]
    if name.startswith("D2("):
        size, count = map(int, name[3:-1].split(","))
        stars = [[] for _ in range(2 * size)]
        distinction = 0
        for knot in range(size):
            for member in (knot, (knot + 1) % size):
                for _ in range(2):
                    stars[member].append(distinction)
                    stars[size + knot].append(distinction)
                    distinction += 1
        for knot in range(size):
            stars[knot].extend(range(distinction, distinction + count))
            distinction += count
        return stars
    raise KeyError(name)


def gate_checks(starts, laws, saved, prior, check):
    gates = saved["a_gate"]
    total_rounds = Counter()
    for category, cases in (("gate", gates["pairs"]),
                            ("extra HOLD", gates["extra_HOLD_against_own_round"]["pairs"])):
        for case in cases:
            start = named_stars(case["start"], starts)
            trial = run(start, parse_law(case["law"]), 8, 3000)
            knots = len(start)
            obtained = []
            for number, record in enumerate(trial.rounds, 1):
                births = len(record.births)
                knots += births
                obtained.append([number, births, knots])
            expected = [[row["round"], row["births"], row["knots"]] for row in case["rows"]]
            check.compare(category, (case["start"], case["law"]), obtained, expected)
            total_rounds[category] += len(obtained)
    for case in prior["P3"]:
        start = named_stars(case["start"], starts)
        trial = run(start, laws[case["law_short"]], 6)
        observed = birth_totals(trial.rounds)
        expected = [event["births"] for event in case["events"]]
        check.compare("prior HOLD events", (case["start"], case["law_short"]),
                      (observed, len(trial.structure.stars), depth_data(trial, Structure(start))[0]["counted"]),
                      (expected, case["knots"], bool(case["births_with_unequal_parents"])))
        total_rounds["prior HOLD events"] += len(observed)
    return dict(total_rounds)


def snapshots(stars, law, rounds):
    state = Structure(stars)
    snapshots = [(tuple(state.stars), frozenset(state.barred))]
    records = []
    for _ in range(rounds):
        record = complete_round(state, law)
        records.append(record)
        snapshots.append((tuple(state.stars), frozenset(state.barred)))
        if record.status != "changed":
            break
    return snapshots, records


def restart_controls(starts, laws, saved, check):
    totals = Counter()
    ended = []
    for case in saved["restart_control"]["runs"]:
        label, law_name = case["start"], case["law"]
        initial = named_stars(label, starts)
        law = laws[law_name]
        states, records = snapshots(initial, law, 5)
        for case_row in case["rows"]:
            number = case_row["t"]
            applicable = number < len(records)
            check.compare("restart classified", (label, law_name, number), applicable,
                          case_row["applicable"])
            if not applicable:
                ended.append({"start": label, "law": law_name, "t": number,
                              "ended_at": len(records), "state": records[-1].status})
                continue
            stars, barred = states[number]
            restarted = Structure(stars, barred)
            future = records[number:number + 2]
            totals["restarts"] += 1
            totals["with barred distinctions at hand-in"] += bool(barred)
            totals["allowed starts at hand-in"] += not barred and all(len(row) >= 3 for row in stars)
            totals["first continuation round changes structure"] += future[0].status == "changed"
            totals["with a later birth"] += any(record.births for record in future)
            totals["with two later rounds executed"] += len(future) == 2
            for after, continuation in enumerate(future, number + 1):
                replayed = complete_round(restarted, law)
                expected_stars, expected_barred = states[after]
                totals["rounds compared"] += 1
                totals["later changes compared"] += replayed.status == "changed"
                totals["later rounds with births compared"] += bool(replayed.births)
                same_record = replayed == continuation
                same_stars = tuple(restarted.stars) == expected_stars
                same_marks = frozenset(restarted.barred) == expected_barred
                check.compare("restart exact states and births", (label, law_name, number, after),
                              (same_record, same_stars, same_marks), (True, True, True))
            check.fields("restart saved totals", (label, law_name, number),
                         {"knots": len(restarted.stars), "births_continuation": birth_totals(future)},
                         case_row)
    for case in saved["handins"]["runs"]:
        label, law, form = case["start"], case["law"], case["form"]
        initial = named_stars(label, starts)
        trial = run(initial, replace(laws[law], form=form), 1)
        record, = trial.rounds
        counts = [knot_count(trial.structure, knot, form)
                  for knot in range(len(trial.structure.stars))]
        reread = [(counts[birth.knot] - counts[parent]) % 3 for birth in record.births
                  for parent in birth.parents]
        totals["hand-ins"] += 1
        totals["hand-ins with barred marks"] += bool(trial.structure.barred)
        totals["old parent distinctions in hand-ins"] += len(reread)
        obtained = {"old_parent_places": len(reread),
                    "wrong_from_new_knot_side": reread.count(1),
                    "right_from_new_knot_side": len(reread) - reread.count(1),
                    "right_from_parent_side": len(reread) - reread.count(2),
                    "wrong_from_parent_side": reread.count(2),
                    "handin_meets_a": start_agreement(trial.structure, form),
                    "handin_carries_barred": len(trial.structure.barred)}
        check.fields("round-one hand-ins", (label, law, form), obtained, case)
    return dict(totals) | {"ended": ended}


def growth_of_forms(start, trials, saved, label, check):
    totals = Counter()
    there_was_a_close = next((number for number, record in enumerate(trials["base"].rounds, 1)
                              if record.closing), None)
    birth_lists = {
        form: [tuple(birth.parents for birth in record.births) for record in trial.rounds]
        for form, trial in trials.items()}
    for form, trial in trials.items():
        depth, _, mismatches = depth_data(trial, start)
        expected = saved[form]
        if form == "base":
            check.fields("named base growth", label, depth, expected)
            continue
        births = [birth for record in trial.rounds for birth in record.births]
        closing_s = [birth.suppressed_added for record in trial.rounds if record.closing
                     for birth in record.births]
        parent_variation = sum(len(set(birth.parent_counts)) > 1 for birth in births)
        common_births = all(left == right for left, right in
                            zip(birth_lists["base"], birth_lists[form]))
        growth_fields = {key: depth[key] for key in ("rounds", "rounds_run", "knots", "end",
                         "births", "greatest", "bprime_first_round", "closing_births")}
        growth_fields.update({
            "a": start_agreement(start, form),
            "b": not depth["counted"],
            "bprime": not depth["bprime_fails"],
            "bprime_births": len(mismatches),
            "bprime_first_births": [knot for step, knot in mismatches
                                    if step == depth["bprime_first_round"]],
            "d": not any(closing_s),
            "closing_hyp_s": closing_s,
            "counted_step3": parent_variation,
            "new_knots": len(births),
            "retired_knots": sum(len(record.retired) for record in trial.rounds),
            "s_positive": sum(birth.added > 0 for birth in births),
            "s_sum": sum(birth.added for birth in births),
            "same_births (DH 6.2)": common_births,
        })
        totals[form + " new knots"] += len(births)
        totals[form + " new knots receiving s"] += growth_fields["s_positive"]
        totals[form + " sum s"] += growth_fields["s_sum"]
        if form == "PU":
            totals["usable form runs with same birth totals"] += (
                growth_fields["births"] == birth_totals(trials["base"].rounds))
        else:
            horizon = there_was_a_close or len(trials["base"].rounds)
            survived = all(birth_lists["base"][i] == (
                birth_lists[form][i] if i < len(birth_lists[form]) else ())
                for i in range(horizon))
            later_birth = bool(there_was_a_close and any(birth_lists[form][there_was_a_close:]))
            totals["barred form comparisons"] += 1
            totals["barred form equals base through required round"] += survived
            totals["barred form base closes"] += bool(there_was_a_close)
            totals["barred form actually closes at base closure round"] += bool(
                there_was_a_close and len(trial.rounds) >= there_was_a_close
                and trial.rounds[there_was_a_close - 1].closing)
            totals["barred form gains a later birth"] += later_birth
            growth_fields.update({"base_closes_at": there_was_a_close,
                                  "goes_on_after_base_closes": later_birth})
        check.fields("named count form growth", (*label, form), growth_fields, expected)
    return totals


def named_runs(starts, laws, saved, check, pilot):
    totals = Counter()
    for case in saved:
        label, law_name, knot_law = (case[key] for key in ("start", "law", "knot_law"))
        if pilot and (label, law_name) not in {("C8X3", "ORD"), ("D2(4,3)", "ORD"),
                                             ("LONE-THREE", "C3WF"), ("SCC", "R3W")}:
            continue
        start = Structure(named_stars(label, starts))
        rule = replace(laws[law_name], knot_law=knot_law)
        trials = {form: run(start.stars, replace(rule, form=value), 8, 3000)
                  for form, value in FORMS.items()}
        totals.update(growth_of_forms(start, trials, case["forms"], (label, law_name, knot_law),
                                      check))
    return totals


def closure_examples(starts, laws):
    examples = {}
    for start_name, law_name in (("LONE-THREE", "C3WF"), ("TRIANGLE", "ORD")):
        for form in ("base", "PB", "BB"):
            start = named_stars(start_name, starts)
            law = replace(laws[law_name], form=FORMS[form])
            states, records = snapshots(start, law, 8)
            examples[f"{start_name}/{law_name}/{form}"] = {
                "start": start,
                "births": birth_totals(records),
                "end": records[-1].status,
                "usable_distinctions_after": sum(
                    len(places) for places in Structure(*states[-1]).usable().values()),
                "rounds": [{"closing": record.closing, "barred_before": len(states[i][1]),
                            "barred_after": len(states[i + 1][1]),
                            "births": [{"parents": birth.parents, "demand": birth.demand,
                                        "F": birth.base_fresh, "s": birth.added,
                                        "barred_at_birth": birth.barred_at_birth}
                                       for birth in record.births]}
                           for i, record in enumerate(records)],
            }
    return examples


def disconnected_parity_example(starts, laws):
    first_piece = named_stars("TRIANGLE", starts)
    stars = first_piece + [[6, 7, 8]]
    trial = run(stars, laws["ORD"], 1)
    first, = trial.rounds
    return {
        "start": stars,
        "start_failures": parity_fails(Structure(stars)),
        "closing": first.closing,
        "new_knots": [{"knot": birth.knot, "parents": list(birth.parents),
                       "places": list(trial.structure.stars[birth.knot]),
                       "fresh": list(birth.fresh)} for birth in first.births],
        "failures_after_round_one": parity_fails(trial.structure),
    }


def shortness_control(starts, laws, saved, check, pilot):
    totals = Counter()
    for case in saved:
        name, law, form = case["start"], case["law"], case["form"]
        if pilot and name not in {"LONE-FOUR", "C8X3"}:
            continue
        structure = Structure(named_stars(name, starts))
        rule = replace(laws[law], form=form)
        opportunities = differences = 0
        for _ in range(8):
            usable = structure.usable()
            holding_barred = Counter(structure.holders[place][0] for place in structure.barred)
            opportunities += sum(bool(holding_barred[knot]) for knot in usable)
            owed = Counter(member for group in groups(structure.meetings, set(usable))
                           for member in group)
            short_using_all_loose = {knot for knot in usable if
                                     owed[knot] > len(usable[knot]) + holding_barred[knot]}
            record = complete_round(structure, rule)
            differences += short_using_all_loose != record.short
            if record.status != "changed" or len(structure.stars) > 3000:
                break
        observed = {"member_rounds_holding_barred_places": opportunities,
                    "rounds_where_all_loose_reading_gives_another_short_set": differences}
        check.fields("shortness control", (name, law, form), observed, case)
        totals.update(observed)
        totals["runs with different short set on some round"] += bool(differences)
    return totals


def census_sample(census, kept, six_census, saved, laws, small_laws, check, pilot):
    generator = random.Random(223515)
    all_small = [index for index, (start, _) in enumerate(census) if len(start.stars) <= 4]
    sample_large = sorted(generator.sample(range(len(all_small), len(census)), 50))
    chosen = ([0, 23, 62, 64, 133] + sample_large[:5]) if pilot else all_small + sample_large
    for index in chosen:
        start, _ = census[index]
        rows = saved["census_rows"][index]
        for descriptor, case in rows["base"].items():
            name, knot_law = descriptor.split("|")
            growth = run(start.stars, replace(laws[name], knot_law=knot_law), 8, 3000)
            metrics = depth_data(growth, start)[0]
            check.fields("sample base growth through five knots", (index, descriptor),
                         {key: value for key, value in metrics.items() if key in case}, case)
        if not kept[index]:
            continue
        for descriptor, case in rows["armw"].items():
            name, form = descriptor.split("|")
            assert name in small_laws
            growth = run(start.stars, replace(laws[name], form=form), 8, 3000)
            metrics, _, mismatches = depth_data(growth, start)
            checked = {key: metrics[key] for key in ("knots", "rounds", "end", "greatest",
                       "bprime_first_round", "closing_births")}
            births = [birth for record in growth.rounds for birth in record.births]
            checked.update({"b": not metrics["counted"], "bprime": not metrics["bprime_fails"],
                            "bprime_births": len(mismatches),
                            "a": start_agreement(start, form),
                            "counted_step3": sum(len(set(birth.parent_counts)) > 1 for birth in births),
                            "new_knots": len(births), "s_sum": sum(birth.added for birth in births),
                            "s_positive": sum(birth.added > 0 for birth in births)})
            check.fields("sample count form growth through five knots", (index, descriptor),
                         checked, case)
    six_rows = saved["six_rows"][:5 if pilot else 60]
    for row in six_rows:
        index = row["idx6"]
        start, _ = six_census[index]
        for name, case in row["base"].items():
            growth = run(start.stars, laws[name], 8, 3000)
            metrics = depth_data(growth, start)[0]
            check.fields("sample six-knot base growth", (index, name),
                         {key: value for key, value in metrics.items() if key in case}, case)
    return {"up_to_four_selected": sum(index in all_small for index in chosen),
            "five_selected": [index for index in chosen if index not in all_small],
            "five_sample_seed": 223515, "six_prefix_in_registered_order": len(six_rows),
            "six_selected": [row["idx6"] for row in six_rows]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="Time a small replay in the same configuration")
    opts = parser.parse_args()
    check = Comparison()
    start_time = perf_counter()
    starts = load(INPUT / "starts.json")["starts"]
    raw_laws = load(INPUT / "laws.json")
    laws = {row["name"]: Law.from_record(row) for row in raw_laws["recorded"] + raw_laws["holding"]}
    release = {row["name"]: laws[row["name"]] for row in raw_laws["recorded"]}
    small_laws = {row["name"] for row in raw_laws["recorded"] if row["base"]}
    part0 = load(OUTPUT / "part0.json")
    part2 = load(OUTPUT / "part2.json")
    saved_census = load(OUTPUT / "part1_runs.json.gz")
    prior = "LEAST-RECORD-20261124-001A"
    prior_holds = load(ROOT / "artifacts" / prior / f"{prior}-E001_least_record" / "generations.json")
    results = {}
    phase_seconds = {}

    def section(name, calculate):
        then = perf_counter()
        results[name] = calculate()
        elapsed = round(perf_counter() - then, 3)
        phase_seconds[name] = elapsed
        print(f"{name}: {elapsed:.3f} s", flush=True)

    then = perf_counter()
    census = []
    six_census = []
    for item in catalogue(6):
        (six_census if len(item[0].stars) == 6 else census).append(item)
    kept = [not parity_fails(start) for start, _ in census]
    census_conditions = [(not parity_fails(start), start_agreement(start, None))
                         for start, _ in six_census]
    for index, ((start, weight), is_kept) in enumerate(zip(census, kept)):
        row = saved_census["census_rows"][index]
        check.fields("census population through five knots", index,
                     {"n": len(start.stars), "kept": is_kept, "w": weight,
                      "a_places": start_agreement(start, None)}, row)
    for index, flags in enumerate(census_conditions):
        check.compare("six-knot census population", index, list(flags),
                      saved_census["six_kept_a"][index])
    results["census population"] = {
        "up to five knots": len(census), "up to five kept": sum(kept),
        "up to five kept agreeing": sum(is_kept and start_agreement(start, None)
                                       for (start, _), is_kept in zip(census, kept)),
        "six knots": len(six_census), "six kept": sum(a for a, _ in census_conditions),
        "six kept agreeing": sum(a and b for a, b in census_conditions)}
    phase_seconds["census population"] = round(perf_counter() - then, 3)

    section("hand cases", lambda: small_cases(load(INPUT / "hand_cases.json"), part0,
                                              census, check))
    section("lone cases", lambda: lone_cases(raw_laws["lone_knot_rations"],
                                             load(OUTPUT / "part3.json"), check))
    section("gates", lambda: gate_checks(starts, laws, part0, prior_holds, check))
    section("restarts", lambda: restart_controls(starts, laws, part2, check))
    section("census restarts", lambda: census_restarts(census, kept, release,
                                                      part2["census_restarts"], check, opts.pilot))
    section("closure limits", lambda: closure_examples(starts, laws))
    section("disconnected parity example", lambda: disconnected_parity_example(starts, laws))
    section("named growth", lambda: named_runs(starts, laws, load(OUTPUT / "part4.json")["runs"],
                                              check, opts.pilot))
    section("shortness", lambda: shortness_control(starts, laws, part0["f_shortness"]["runs"],
                                                  check, opts.pilot))
    section("census sample", lambda: census_sample(census, kept, six_census, saved_census, laws,
                                                  small_laws, check, opts.pilot))
    results.update({"comparisons": dict(check.cases), "disagreements": dict(check.disagreements),
                    "examples": check.examples, "phase_seconds": phase_seconds,
                    "seconds": round(perf_counter() - start_time, 3)})
    if not opts.pilot:
        (HERE / "growth_counts.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({key: results[key] for key in ("comparisons", "disagreements", "examples",
                                                   "seconds")}, indent=2))
    return bool(check.disagreements)


if __name__ == "__main__":
    raise SystemExit(main())
