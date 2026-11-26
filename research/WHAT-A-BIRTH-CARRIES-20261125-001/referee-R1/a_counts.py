"""Recount the ordinary-count ticket from saved per-run and pair records."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations, islice, product
from math import comb
from pathlib import Path
import gzip
import json

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = "WHAT-A-BIRTH-CARRIES-20261125-001A"
DATA = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_which_under_ordinary_count"
REGISTRATION = ROOT / "research" / TICKET
ABSENT = object()


def read_json(name):
    with gzip.open(DATA / name, "rt") as source:
        return json.load(source)


def read_rows(name):
    path = DATA / name
    opener = gzip.open if path.suffix == ".gz" else Path.open
    with opener(path, "rt") as source:
        for line in source:
            yield json.loads(line)


def tuple_tree(value):
    if isinstance(value, list):
        return tuple(map(tuple_tree, value))
    return value


def birth_count(h, a):
    return comb(a, 2) + a * (h - a)


def law_key(row):
    law = row["law"]
    return (law["ration"], law["treatment"], law["take"], law["choice"], law["knot_law"])


def course_graph(payload):
    # An incidence link has one distinction endpoint, and a parent link has
    # two knot endpoints. Birth rounds recover the direction of a parent link.
    graph = nx.Graph()
    graph.add_nodes_from((i, {"label": label}) for i, label in enumerate(payload["labels"]))
    for a, b, kind in payload["edges"]:
        assert kind == ("p" if max(a, b) < payload["n_knots"] else "i")
        graph.add_edge(a, b)
    return graph


def isomorphic(first, second):
    return nx.vf2pp_is_isomorphic(first, second, node_label="label")


class CourseClasses:
    def __init__(self):
        self.exact = {}
        self.buckets = defaultdict(list)
        self.next_class = 0
        self.searches = 0

    def find(self, payload):
        labels = tuple(payload["labels"])
        links = tuple(sorted((min(a, b), max(a, b), kind) for a, b, kind in payload["edges"]))
        exact = labels, links
        if exact in self.exact:
            return self.exact[exact]
        graph = course_graph(payload)
        # Neighbor labels are only a necessary invariant. Every match between
        # two different encodings is confirmed by an exact isomorphism test.
        invariant = frozenset(
            Counter((labels[a], tuple(sorted(labels[b] for b in graph[a]))) for a in graph).items()
        )
        for old, number in self.buckets[invariant]:
            self.searches += 1
            if isomorphic(old, graph):
                self.exact[exact] = number
                return number
        number = self.next_class
        self.next_class += 1
        self.buckets[invariant].append((graph, number))
        self.exact[exact] = number
        return number


@dataclass(slots=True)
class Run:
    a: int
    nu: int
    marks: tuple
    classes: dict
    values: tuple
    join_position: tuple | None
    fingerprint: str
    meeting: int | None
    last: int
    valid_knots: bool


def join_position(values):
    for step, _, position, value in values:
        if step == 4 and value[0] == "join":
            return ("D", position[1])
    return None


def run_record(row, classes):
    values = tuple_tree(row["values_r2"])
    knot_test = row["knot_test"]
    return Run(
        row["a"], row["nu"], tuple(row["usable"]),
        {int(r): classes.find(course) for r, course in row["courses"].items()},
        values, join_position(values), row["fingerprint"], row["meet_round"], row["rounds_read"],
        not any(knot_test[k] for k in ("n_fail", "n_disagree", "n_untested")),
    )


def start_roles(stars):
    x = next(k for k, places in enumerate(stars) if len(places) == 3)
    y = 1 - x
    e, = set(stars[x]) & set(stars[y])
    return x, y, e


def s4_count(row):
    _, _, e = start_roles(row["stars"])
    h, a, audit = row["h"], row["a"], row["s4"]
    m = birth_count(h, a)
    values = tuple_tree(row["values_r2"])
    births = {position[1]: value for step, _, position, value in values if step == 4}
    demands = {position[1]: value for step, _, position, value in values if step == 6}
    candidates = {position[1]: value for step, _, position, value in values if step == 5}
    round2 = row["round_summaries"]["2"]
    join, = (name for name, value in births.items() if value[0] == "join")
    d, descents = demands[join]
    listed, taken = candidates[join]
    checks = {
        "J_sole_candidate_and_take_e": tuple(x[0] for x in listed) == taken == (f"d{e}",),
        "J_demand_2_plus_M": d == audit["D"] == 2 + m,
        "J_fresh_2_plus_M": audit["f"] == 2 + m,
        "J_places_5_plus_M": audit["places"] == 5 + m,
        "J_partners_descents": Counter(descents) == {"X only": 2, **({"Y only": m} if m else {})},
        "r2_births_3_plus_M": sum(item[-1] for item in round2) == 3 + m,
        "Y_births_M": audit["M"] == audit["M_births"] == m,
        "Y_births_take_from_Y_start": audit["y_take_one_place"],
        "Y_start_meets_J_and_Y_births": audit["Ystart_meets"],
        "J_groups_pairs": audit["groups_all_pairs"],
        "J_loose_inputs_from_parents": audit["loose_inputs_ok"],
        "J_not_implied": not audit["implied"],
        "J_partners_exact": audit["partners_ok"],
    }
    return checks


def inventory_row(row, counts, registered):
    counts["runs"] += 1
    h, a = row["h"], row["a"]
    counts[f"stops_after_r{row['rounds_read']}"] += 1
    counts[f"stop:{row['stop']}"] += 1
    counts["short_after1"] += len(row["short_after1"])
    counts["implied_rounds"] += len(row["implied_rounds"])
    for key, value in row["knot_test"].items():
        if isinstance(value, int):
            counts[f"knot_test:{key}"] += value
    if row["meet_round"] is not None:
        counts[f"meet_r{row['meet_round']}_a{'+' if a else '0'}"] += 1
        counts[f"meet_how:{'+'.join(row['meet_how'])}"] += 1
    else:
        counts[f"no_meeting_a{'+' if a else '0'}"] += 1
    if not a and row["meet_round"] is not None:
        counts["barred_control_meets"] += 1
    for r, trace in row["trace_counts"].items():
        counts[f"joint_births_r{r}"] += trace["joint_births"]
    if row["s4"] is None:
        return
    counts["S4_all_individual_checks"] += all(s4_count(row).values())
    for key, result in s4_count(row).items():
        if not result:
            counts[f"S4_fail:{key}"] += 1
    if row["stars"] == registered[f"made-{h}"] and row["law"]["choice"] == "OLDEST":
        s4 = row["s4"]
        counts["S3_registered_runs"] += 1
        m = birth_count(h, a)
        holds = (
            all(int(d) == 2 + m for d in s4["x_births_D"])
            and all(item[2] == [0] for item in row["round_summaries"]["2"])
        )
        counts["S3_registered_takes_and_X_D"] += holds
    if row["s4"]["every_birth_takes_e"]:
        counts["every_r2_birth_takes_e"] += 1


def numberings_check(registered):
    reports = {}
    for h in (3, 4, 5, 6):
        names = set(range(h + 3))
        expected = set()
        for e in names:
            for x_pair in combinations(sorted(names - {e}), 2):
                x = tuple(sorted((e, *x_pair)))
                y = tuple(sorted(names - set(x_pair)))
                expected.update(((x, y), (y, x)))
        roster = tuple_tree(registered["made_class"][f"made-{h}"])
        assert len(roster) == len(set(roster)) and set(roster) == expected
        report = {"numberings": len(roster), "marked_per_a": {}}
        for a in range(h + 1):
            marks = registered["class_h_by_a"].get(f"made-{h}|a={a}")
            if marks is None:
                continue
            expected_marks = set()
            for stars in roster:
                _, y, e = start_roles(stars)
                expected_marks.update((stars, m) for m in combinations(sorted(set(stars[y]) - {e}), a))
            actual_marks = {(tuple_tree(m["stars"]), tuple(m["usable"])) for m in marks}
            assert len(marks) == len(actual_marks) and actual_marks == expected_marks
            report["marked_per_a"][a] = len(marks)
        reports[h] = report
    return reports


def str_key(*parts):
    return "|".join(map(str, parts))


def index_rows(label, classes, registered, smoke):
    indexed = defaultdict(dict)
    inventory = defaultdict(Counter)
    s5 = defaultdict(dict)
    rows = read_rows(f"run{label}_runs.jsonl.gz")
    if smoke:
        rows = islice(rows, 8 if label == "1r" else 16)
    for row in rows:
        law, h, nu = law_key(row), row["h"], row["nu"]
        run = run_record(row, classes)
        cohort = law, h
        assert (nu, run.marks) not in indexed[cohort]
        indexed[cohort][nu, run.marks] = run
        inventory[str_key(*law, h)].update({"invalid_knot_runs": int(not run.valid_knots)})
        inventory_row(row, inventory[str_key(*law, h)], registered["registered"])
        if law[3] == "OLDEST" and row["stars"] == registered["registered"][f"made-{h}"]:
            if row["a"] in (h - 1, h):
                s5[str_key(*law, h)][str(run.marks)] = {
                    "a": run.a,
                    "round_2_births": sum(item[-1] for item in row["round_summaries"]["2"]),
                    "round_3_births": row["round_summaries"].get("3"),
                    "courses": run.classes,
                }
    return indexed, inventory, s5


def all_cell_comparisons(cells):
    report = {}
    for a, b in combinations(sorted(cells), 2):
        runs_a, runs_b = cells[a], cells[b]
        last = min(run.last for run in runs_a + runs_b)
        data = {"longest_shared_prefix": last, "prefixes": {}}
        for r in range(2, last + 1):
            counts_a = Counter(run.classes[r] for run in runs_a)
            counts_b = Counter(run.classes[r] for run in runs_b)
            shared = counts_a.keys() & counts_b.keys()
            metrics = {
                "classes_A": len(counts_a), "classes_B": len(counts_b), "intersection": len(shared),
                "only_A": len(counts_a) - len(shared), "only_B": len(counts_b) - len(shared),
                "cross_numbering_and_same_numbering_equal_run_pairs": sum(counts_a[k] * counts_b[k] for k in shared),
            }
            if shared and (len(shared) < len(counts_a) or len(shared) < len(counts_b)):
                for name, runs, counts in (("A", runs_a, counts_a), ("B", runs_b, counts_b)):
                    only = counts.keys() - shared
                    metrics[f"exclusive_example_{name}"] = next(
                        ({"nu": run.nu, "marks": run.marks, "course_class": run.classes[r]}
                         for run in runs if run.classes[r] in only), None
                    )
            data["prefixes"][r] = metrics
        report[str_key(a, b)] = data
    return report


def cohort_report(cohort, rows):
    law, h = cohort
    cells = defaultdict(list)
    by_numbering = defaultdict(list)
    for run in rows.values():
        cells[run.a].append(run)
        by_numbering[run.nu].append(run)
    last = min(run.last for a, cell in cells.items() if a for run in cell)
    report = {
        "by_a": {a: len(cell) for a, cell in sorted(cells.items())},
        "numberings": len(by_numbering),
        "missing_numberings": sorted(set(range(2 * (h + 3) * comb(h + 2, 2))) - by_numbering.keys()),
        "longest_prefix_over_active_cells": last,
        "active_classes_by_prefix": {
            r: len({run.classes[r] for a, cell in cells.items() if a for run in cell})
            for r in range(2, last + 1)
        },
        "cell_comparisons": all_cell_comparisons(cells),
        "within_each_cell": {},
    }
    for a, cell in sorted(cells.items()):
        last = min(run.last for run in cell)
        report["within_each_cell"][a] = {
            r: {
                "classes": len({run.classes[r] for run in cell}),
                "within_numbering_pairs": sum(comb(sum(run.a == a for run in group), 2) for group in by_numbering.values()),
                "within_numbering_unequal": sum(
                    x.classes[r] != y.classes[r] for group in by_numbering.values()
                    for x, y in combinations((run for run in group if run.a == a), 2)
                ),
            }
            for r in range(2, last + 1)
        }
    for comparison, data in report["cell_comparisons"].items():
        a, b = map(int, comparison.split("|"))
        m_differs = birth_count(h, a) != birth_count(h, b)
        data["different_M"] = m_differs
    return report


def classify_part(fd):
    if fd is None:
        return "none recorded"
    if fd["kind"] in {"implied", "closing", "stall", "guard", "roundwide"}:
        return "round-wide"
    part = fd["part"]
    if any(descent == "Y only" for _, descent, _ in part):
        return "through the meeting"
    if any(descent in ("both", "neither") for _, descent, _ in part):
        return "a third part (a start knot)" if all(start for _, _, start in part) else "a third part"
    return "unclassified"


def first_round2_difference(first, second):
    second_values = {position: value for _, _, position, value in second.values}
    return next(
        ((step, kind, position, value, second_values.get(position, ABSENT))
         for step, kind, position, value in first.values if second_values.get(position, ABSENT) != value),
        None,
    )


def pair_report(label, indexed, cohorts, smoke):
    counts = defaultdict(Counter)
    examples = {}
    joint_checks = Counter()
    seen = defaultdict(set)
    for row in read_rows(f"run{label}_pairs.jsonl.gz"):
        cohort = tuple(row["key"]), row["h"]
        group = indexed.get(cohort, {})
        nu = row["nu"]
        marks_a, marks_b = tuple(row["A"]), tuple(row["B"])
        if smoke and (nu, marks_b) not in group:
            break
        first, second = group[nu, marks_a], group[nu, marks_b]
        assert (nu, marks_a, marks_b) not in seen[cohort]
        seen[cohort].add((nu, marks_a, marks_b))
        assert (first.a, second.a) == (row["a"], row["b"])
        same_m = birth_count(row["h"], first.a) == birth_count(row["h"], second.a)
        assert first.meeting == row["mA"] and second.meeting == row["mB"]
        scope = str_key(*cohort[0], cohort[1], first.a, second.a)
        stat = counts[scope]
        stat["pairs"] += 1
        stat[f"same_meeting:{row['same_meeting']}"] += 1
        stat[f"meeting_rounds:{first.meeting},{second.meeting}"] += 1
        stat[f"pair_prefix:{row['last_both']}"] += 1
        stat[
            f"link_class_A:{','.join(row['linkA']) or 'none'}__B:{','.join(row['linkB']) or 'none'}"
        ] += 1
        assert row["last_both"] == min(first.last, second.last)
        for r, recorded in row["course_equal"].items():
            actual = first.classes[int(r)] == second.classes[int(r)]
            assert recorded == actual
            stat[f"r{r}_equal"] += actual
            stat[f"r{r}_unequal"] += not actual
        if smoke:
            common = min(first.last, second.last)
        else:
            common = cohorts[str_key(*cohort[0], cohort[1])]["cell_comparisons"][
                str_key(first.a, second.a)
            ]["longest_shared_prefix"]
        unequal = first.classes[common] != second.classes[common]
        fd = row["fd"]
        classification = classify_part(fd)
        if fd is not None:
            if classification != fd["class"]:
                stat["archive_class_disagreements"] += 1
            stat[f"recorded_first_difference:r{fd['round']}:{fd['kind']}:{fd['class']}"] += 1
        if unequal:
            assert fd is not None and fd["round"] <= common
            first_difference = f"r{fd['round']}:{fd['kind']}:{classification}"
            stat[f"course_difference_on_common_prefix:{first_difference}"] += 1
            if same_m:
                example_key = str_key(*cohort[0], cohort[1], first_difference)
                examples.setdefault(example_key, {
                    "nu": nu, "A": marks_a, "B": marks_b, "rounds_compared": common,
                    "first_course_difference": min(r for r in range(2, common + 1) if first.classes[r] != second.classes[r]),
                    "first_reported_value_difference": fd,
                })
        elif fd is not None and fd["round"] <= common:
            stat["value_difference_but_equal_course_on_common_prefix"] += 1
        difference = first_round2_difference(first, second)
        if same_m:
            if difference is not None:
                stat[f"raw_round2_value_difference:{difference[1]}"] += 1
        else:
            assert difference is not None
            step, kind, position, value_a, value_b = difference
            assert step == 6 and kind == "demand" and position == first.join_position == second.join_position
            assert value_a[0] == 2 + birth_count(row["h"], first.a)
            assert value_b[0] == 2 + birth_count(row["h"], second.a)
            assert fd["round"] == 2 and tuple_tree(fd["pos"]) == position
            assert fd["step"] == step and tuple_tree(fd["value_A"]) == value_a and tuple_tree(fd["value_B"]) == value_b
            assert classification == "through the meeting" and unequal
            stat["different_M_J_D_through_meeting"] += 1
            if first.a:
                stat["R9_pair_same_round_and_all_knots"] += (
                    first.meeting == second.meeting == 2 and first.valid_knots and second.valid_knots
                )
        joint_checks["pairwise_course_equalities_rechecked"] += len(row["course_equal"])
    if not smoke:
        for cohort, group in indexed.items():
            by_nu = defaultdict(list)
            for (nu, _), run in group.items():
                by_nu[nu].append(run)
            actual_set = seen[cohort]
            expected = {
                (nu, first.marks, second.marks) for nu, runs in by_nu.items()
                for first, second in combinations(sorted(runs, key=lambda run: run.a), 2) if first.a < second.a
            }
            if actual_set != expected:
                joint_checks["pair_rows_missing"] += len(expected - actual_set)
                joint_checks["pair_rows_extra"] += len(actual_set - expected)
    return {"counts": counts, "equal_M_examples": examples, "checks": joint_checks}


def partition(runs, get_value):
    parts = defaultdict(set)
    for run in runs:
        parts[get_value(run)].add(run.marks)
    return frozenset(frozenset(part) for part in parts.values())


def handed_report(label, indexed, cohorts, smoke):
    counts = defaultdict(Counter)
    examples = {}
    for row in read_rows(f"run{label}_handed.jsonl.gz"):
        cohort = tuple(row["key"]), row["h"]
        nu = row["nu"]
        runs = [run for run in indexed[cohort].values() if run.nu == nu and run.a]
        if smoke and not runs:
            break
        scope = str_key(*cohort[0], cohort[1])
        last = cohorts[scope]["longest_prefix_over_active_cells"]
        values = {run.marks: {p: v for _, _, p, v in run.values} for run in runs}
        kinds = {p: (step, kind) for run in runs for step, kind, p, _ in run.values}
        assert len({run.join_position for run in runs}) == 1
        join = runs[0].join_position
        for prefix, archived in row["handed"].items():
            r = int(prefix)
            exact = partition(runs, lambda run: run.classes[r])
            expected = frozenset(frozenset(tuple(mark) for mark in part) for part in archived["P_entries"])
            assert exact == expected and len(exact) == archived["n_classes"]
            # A count induces the course classes only if it also distinguishes
            # courses within a fixed number of usable Y members when those differ.
            j_count = partition(runs, lambda run: values[run.marks][join][0]) == exact
            j_full = partition(runs, lambda run: values[run.marks][join]) == exact
            assert j_full == archived["J_demand_r2_induces"]
            stat = counts[f"{scope}|r{r}"]
            stat["numberings"] += 1
            stat[f"course_partition_size:{len(exact)}"] += 1
            stat["J_round2_scalar_count_induces"] += j_count
            stat["J_round2_full_entry_induces"] += j_full
            matches_r2 = []
            mixed_missing = 0
            for pos, (step, kind) in kinds.items():
                get_value = lambda run: values[run.marks].get(pos, ABSENT)
                if partition(runs, get_value) == exact:
                    matches_r2.append((step, kind, pos))
                    mixed_missing += any(get_value(run) is ABSENT for run in runs)
            stat["some_round2_entry_induces"] += bool(matches_r2)
            stat["round2_induction_can_use_absence"] += bool(mixed_missing)
            stat["round2_scalar_demand_induces"] += any(
                partition(runs, lambda run: values[run.marks][pos][0]) == exact
                for (pos, (step, kind)) in kinds.items() if step == 6
            )
            if r == 2:
                demand_positions = [pos for pos, (step, _) in kinds.items() if step == 6]
                minimum_demands = next((n for n in range(1, 4) if any(
                    partition(runs, lambda run: tuple(values[run.marks][pos][0] for pos in positions)) == exact
                    for positions in combinations(demand_positions, n)
                )), None)
                stat[f"minimum_round2_demand_positions:{minimum_demands}"] += 1
            archive_r2 = sum(n for (rr, _, _), n in archived["inducing_kinds"] if rr == 2)
            if archive_r2 != len(matches_r2):
                stat["round2_position_count_disagrees"] += 1
            stat[f"archive_verdict:{archived['verdict']}"] += 1
            stat["archive_demand_alone_induces"] += archived["demand_alone_induces"]
            stat["archive_first_is_count"] += archived["first_is_count"]
            stat["archive_some_later_position_induces"] += any(rr > 2 for (rr, _, _), _ in archived["inducing_kinds"])
            count_kinds = {"D", "f", "m"}
            scalar_candidates = [position for position, _ in archived["inducing_kinds"] if position[2] in count_kinds]
            stat["archive_induction_at_count_typed_position"] += bool(scalar_candidates)
            first = archived["first_inducing"]
            if first:
                stat[str_key("archive_first_inducing", first["round"], first["step"], first["pos_kind"])] += 1
            if r == last and not j_count:
                reason = "no_round2_full_entry" if not matches_r2 else "other_round2_entry"
                if not archived["demand_alone_induces"]:
                    reason += "_no_archive_scalar_demand"
                examples.setdefault(f"{scope}|{reason}", {
                    "nu": nu, "prefix": r, "P": sorted(sorted(part) for part in exact),
                    "a_by_class": archived["P"], "first_inducing": first,
                    "inducing_kinds": archived["inducing_kinds"],
                    "J_round2_count_by_marks": [(run.marks, values[run.marks][join][0]) for run in runs],
                })
    return {"counts": counts, "positions_examples": examples}


def compare_height(indexed):
    report = {}
    for law in {law for law, _ in indexed}:
        if (law, 3) not in indexed or (law, 4) not in indexed:
            continue
        for a in range(4):
            small = [run for run in indexed[law, 3].values() if run.a == a]
            large = [run for run in indexed[law, 4].values() if run.a == a]
            data = all_cell_comparisons({3: small, 4: large})["3|4"]
            report[str_key(*law, a)] = data
    return report


def crosscheck_treatments(main, swap):
    counts = defaultdict(Counter)
    for (law, h), runs in swap.items():
        _, treatment, _, choice, knot_law = law
        retire_law = (law[0], "CANCEL-RETIRE", *law[2:])
        control = main.get((retire_law, h), {})
        stat = counts[str_key(choice, knot_law, treatment)]
        for key, run in runs.items():
            if key not in control:
                stat["unpaired"] += 1
                continue
            paired = control[key]
            stat["paired"] += 1
            stat["same_fingerprint"] += run.fingerprint == paired.fingerprint
            stat["same_courses"] += run.classes == paired.classes
            stat["same_completed_rounds"] += run.last == paired.last
    return counts


def gate_inventory():
    rows = [row for i in range(4) for row in read_rows(f"G_engine_{i}_of_4.jsonl")]
    rest = json.loads((DATA / "G_rest.json").read_text())
    expected = json.loads((REGISTRATION / "attribution_records.json").read_text())["records"]
    gate_lines = (REGISTRATION / "gate_listing.txt").read_text().splitlines()
    return {
        "archived_comparisons": len(rows),
        "archived_equal": sum(row["equal"] and not row["diffs"] for row in rows),
        "gate_listing_line_count": len(gate_lines),
        "gate_listing_same": gate_lines == rest["gate_listing"]["got"],
        "attribution_records_expected": len(expected),
        "attribution_records_equal": sum(r["got"] == e["expected"] for r, e in zip(rest["attribution_records"], expected, strict=True)),
        "symmetric_pairs": len(rest["symmetric_pairs"]),
        "symmetric_same_named_start": sum(
            tuple(tuple(sorted(k)) for k in r["stars"]) == tuple(tuple(sorted(k)) for k in r["stars_listed"])
            for r in rest["symmetric_pairs"]
        ),
        "symmetric_archived_identical": sum(r["identical"] for r in rest["symmetric_pairs"]),
    }


def two_starts_report(label, classes, registered):
    source = read_json(f"run{label}.json.gz")
    by_law = defaultdict(dict)
    control_rows = defaultdict(Counter)
    for row in source["runs"]:
        run = run_record(row, classes)
        by_law[row["law_name"]][row["h"], row["a"]] = run
        inventory_row(row, control_rows[row["law_name"]], registered["registered"])
    comparisons = {}
    for row in source["comparisons"]:
        key = row["law"]
        a, b = ((5, 0), (6, 0)) if label == "P" else ((5, 5), (6, 6))
        first, second = by_law[key][a], by_law[key][b]
        actual = {str(r): first.classes[r] == second.classes[r] for r in range(2, 1 + min(first.last, second.last))}
        assert actual == row["course_equal"]
        fd = row["fd"]
        comparisons[key] = {"course_equal": actual, "first_difference": fd, "attribution": classify_part(fd)}
        if row["criterion"]:
            comparisons[key]["archive_planted_criterion"] = row["criterion"]
    return {"inventory": control_rows, "comparison": comparisons}


def negative_report(indexed):
    report = defaultdict(Counter)
    for (law, _), runs in indexed.items():
        stat = report[law[-1]]
        stat["runs"] += len(runs)
        stat["meeting_runs"] += sum(run.meeting is not None for run in runs.values())
    for knot_law, stat in report.items():
        runs = [run for (law, _), group in indexed.items() if law[-1] == knot_law for run in group.values()]
        last = min(run.last for run in runs)
        stat["common_prefix"] = last
        for r in range(2, last + 1):
            stat[f"distinct_courses_r{r}"] = len({run.classes[r] for run in runs})
    return report


# Replay the specified rounds using sets of holders, including the provisional
# roster after the takes and before the fresh distinctions are made.
@dataclass(slots=True)
class Knot:
    places: tuple
    parents: tuple
    round: int
    kind: str
    answer: tuple
    descent: int


DESCENT = ("neither", "X only", "Y only", "both")


def holders_of(knots):
    result = defaultdict(set)
    for k, knot in enumerate(knots):
        for d in knot.places:
            result[d].add(k)
    return result


def round_groups(knots, holders, roster):
    active_holders = {d: hs & roster for d, hs in holders.items()}
    met = set()
    for k, knot in enumerate(knots):
        members = frozenset().union(*(active_holders[d] for d in knot.places)) - {k}
        if len(members) >= 2:
            met.add(members)
    adj = nx.Graph()
    for members in met:
        adj.add_edges_from(combinations(sorted(members), 2))
    large = []
    for component in nx.connected_components(adj):
        if frozenset(component) in met:
            continue
        for clique in nx.find_cliques(adj.subgraph(component)):
            if len(clique) >= 3 and not any(set(clique) <= members for members in met):
                large.append(tuple(sorted(clique)))
    used_pairs = {pair for clique in large for pair in combinations(clique, 2)}
    pairs = {tuple(sorted(pair)) for pair in adj.edges()} - used_pairs
    return sorted(large) + sorted(pairs)


def span_parity(rows):
    echelon = {}
    for row in rows:
        while row and row.bit_length() in echelon:
            row ^= echelon[row.bit_length()]
        if row:
            echelon[row.bit_length()] = row
    return echelon


def parity_support(places):
    return sum(1 << d for d in places)


def implied_by(parity, places):
    row = parity_support(places)
    while row and row.bit_length() in parity:
        row ^= parity[row.bit_length()]
    return not row


class Growth:
    def __init__(self, stars, marks, law):
        self.x, self.y, _ = start_roles(stars)
        self.marked = set(marks)
        self.ration, self.treatment, self.take, self.choice, self.knot_law = law
        self.knots = [Knot(tuple(k), (), 0, "start", ("s", i), 0) for i, k in enumerate(stars)]
        self.distinction_answers = [("s", d) for d in range(max(map(max, stars)) + 1)]
        self.made_by = [0] * len(self.distinction_answers)
        self.barred = set()
        self.at_s = 0
        self.loose_history = {}
        self.entries = {}
        self.round_info = {}

    def loose_counts(self, holders, k):
        loose = {d for d in self.knots[k].places if holders[d] == {k}}
        return len(loose - self.barred), len(loose & self.barred)

    def round(self, t):
        old = self.knots
        holders = holders_of(old)
        loose = {k: [d for d in sorted(knot.places) if holders[d] == {k} and d not in self.barred]
                 for k, knot in enumerate(old)}
        roster = {k for k in loose if loose[k]}
        groups = round_groups(old, holders, roster)
        owes = Counter(k for group in groups for k in group)
        short = {k for k in roster if len(loose[k]) < owes[k]}
        kept_groups = [group for group in groups if short.isdisjoint(group)]
        taken_count = Counter(k for group in kept_groups for k in group)
        if self.treatment == "CANCEL-RETIRE":
            self.barred.update(d for k in short for d in loose[k])
            offshoot_parents = roster - short
        elif self.treatment == "CANCEL-WAIT":
            offshoot_parents = roster - short
        else:
            assert self.treatment == "CANCEL-OFFSHOOT"
            offshoot_parents = roster
        tasks = [(group, "join", -1) for group in kept_groups]
        tasks += [((k,), "offshoot", i) for k in sorted(offshoot_parents)
                  for i in range(len(loose[k]) - taken_count[k])]
        eligible = {d for d, hs in holders.items() if len(hs) > 1}
        neighbours = [set().union(*(holders[d] for d in knot.places)) - {k} for k, knot in enumerate(old)]
        made = []
        birth_details = []
        used = Counter()
        parity = span_parity(parity_support(knot.places) for knot in old) if self.knot_law == "parity" else None
        for parents, kind, index in tasks:
            inputs = tuple(loose[k][used[k]] for k in parents)
            used.update(parents)
            parent_places = set().union(*(old[k].places for k in parents))
            candidates = defaultdict(set)
            if self.take == "MET":
                sources = set.intersection(*(neighbours[k] for k in parents))
                for k in sources:
                    for d in (set(old[k].places) & eligible) - parent_places:
                        candidates[d].add(k)
            else:
                assert self.take is None
            ordered = tuple(sorted(candidates))
            takes = ()
            if ordered:
                takes = ordered if self.choice == "EVERY" else (ordered[0 if self.choice == "OLDEST" else -1],)
            descent = 0
            if t == 1:
                descent = 1 if parents == (self.x,) else 2 if parents == (self.y,) else 0
            else:
                for p in parents:
                    descent |= old[p].descent
            answer = ("b", t, kind, tuple(sorted(old[p].answer for p in parents)), index)
            knot = Knot(inputs + takes, parents, t, kind, answer, descent)
            made.append(knot)
            birth_details.append((inputs, candidates, takes))
        provisional = old + made
        demand_roster = set(range(len(old), len(provisional)))
        if self.treatment == "CANCEL-WAIT":
            demand_roster |= short
        demand_groups = round_groups(provisional, holders_of(provisional), demand_roster)
        groups_at = defaultdict(list)
        for group in demand_groups:
            for k in group:
                groups_at[k].append(group)
        info = []
        for j, born in enumerate(made, start=len(old)):
            inputs, candidates, takes = birth_details[j - len(old)]
            d = len(groups_at[j])
            p = len(born.places)
            fresh = max(d, 3 - p, 1)
            if self.ration == "CAP-3":
                fresh = min(3, fresh)
            else:
                assert self.ration == "ORD"
            implied = parity is not None and implied_by(parity, born.places)
            if implied:
                fresh = 0
            new_start = len(self.distinction_answers)
            born.places += tuple(range(new_start, new_start + fresh))
            self.distinction_answers.extend(("f", born.answer, i) for i in range(fresh))
            self.made_by.extend([born.descent] * fresh)
            info.append((born, inputs, candidates, takes, d, p, implied, fresh))
        self.knots = provisional
        if t == 1:
            self.at_s = len(self.distinction_answers)
            new_holders = holders_of(self.knots)
            for j, knot in enumerate(self.knots):
                if knot.descent == 2 and knot.places[0] not in self.marked:
                    self.barred.update(d for d in knot.places if new_holders[d] == {j})
        holders = holders_of(self.knots)
        self.loose_history[t] = {k: self.loose_counts(holders, k) for k, knot in enumerate(self.knots) if knot.descent == 1}
        self.round_info[t] = info
        self.entries[t] = self.read_entries(old, t, groups, roster, owes, short, info, groups_at)

    def read_entries(self, old, t, groups, roster, owes, short, info, groups_at):
        active_x = {k for k in roster if old[k].descent == 1}
        entries = {}
        group_rank = Counter()
        for group in groups:
            x = tuple(sorted(old[k].answer for k in group if k in active_x))
            if x:
                entries[t, "g", x, group_rank[x]] = len(group), tuple(sorted(DESCENT[old[k].descent] for k in group))
                group_rank[x] += 1
        for k in active_x:
            answer = old[k].answer
            entries[t, "m", answer] = owes[k], k in short
            entries[t, "a", answer] = self.treatment if k in short else "none"
        for j, (born, loose, candidates, takes, d, p, implied, f) in enumerate(info, start=len(old)):
            if active_x.isdisjoint(born.parents):
                continue
            answer = born.answer
            entries[t, "b", answer] = born.kind, answer[3], tuple(self.distinction_answers[d] for d in loose)
            candidates_with_suppliers = tuple(sorted(
                (self.distinction_answers[d], tuple(sorted(old[k].answer for k in sources)))
                for d, sources in candidates.items()
            ))
            entries[t, "c", answer] = candidates_with_suppliers, tuple(sorted(self.distinction_answers[d] for d in takes))
            # The archive deduplicates partners of the same birth. Keep both
            # readings to check the frozen wording on demand-group members.
            partners = [k for group in groups_at[j] for k in group if k != j]
            entries[t, "D", answer] = d, tuple(sorted(DESCENT[self.knots[k].descent] for k in set(partners)))
            entries[t, "demand_with_repeats", answer] = d, tuple(sorted(DESCENT[self.knots[k].descent] for k in partners))
            entries[t, "f", answer] = p, implied, f
        entries[t, "w"] = (any(row[-2] for row in info), None)
        return entries

    def course(self, t):
        x = {k: knot for k, knot in enumerate(self.knots) if knot.descent == 1}
        names = {kn: i for i, kn in enumerate(x)}
        usage = defaultdict(list)
        for k, knot in x.items():
            for d in knot.places:
                usage[d].append(names[k])

        def distinction_label(d):
            origin = "E" if d < self.at_s else "FX" if self.made_by[d] == 1 else "FO"
            return f"{origin}:{int(d in self.barred)}"

        labels = []
        for k, knot in x.items():
            leaves = Counter(distinction_label(d) for d in knot.places if len(usage[d]) == 1)
            leaves_label = ",".join(f"{label}*{n}" for label, n in sorted(leaves.items()))
            loose = ",".join("%d.%d" % self.loose_history[r][k] for r in range(knot.round, t + 1))
            labels.append(f"K|{knot.round}|{knot.kind}|{len(knot.places)}|{loose}|{leaves_label}")
        edges = []
        for d, hs in sorted(usage.items()):
            if len(hs) > 1:
                edges.extend((k, len(labels), "i") for k in hs)
                labels.append("D|" + distinction_label(d))
        edges.extend((names[k], names[p], "p") for k, knot in x.items() for p in knot.parents if p in names)
        return {"labels": labels, "edges": edges, "n_knots": len(x)}


def recheck_numbering(runs, stars, law, prefix, classes):
    target = partition(runs, lambda run: run.classes[prefix])
    values = {}
    for run in runs:
        grown = Growth(stars, run.marks, law)
        for r in range(1, prefix + 1):
            grown.round(r)
            if r >= 2:
                replayed = classes.find(grown.course(r))
                assert replayed == run.classes[r], (law, stars, run.marks, r, replayed, run.classes[r])
        values[run.marks] = {p: value for r in range(2, prefix + 1) for p, value in grown.entries[r].items()}
    positions = set().union(*(set(entries) for entries in values.values()))
    exact = set()
    read_with_repeats = set()
    scalar = {}
    for pos in positions:
        read = lambda run: values[run.marks].get(pos, ABSENT)
        if partition(runs, read) == target:
            if pos[1] == "demand_with_repeats":
                read_with_repeats.add((pos[0], "D", *pos[2:]))
            else:
                exact.add(pos)
        components = {"g": [(0, "group size")], "m": [(0, "owing")], "D": [(0, "D")], "f": [(0, "p"), (2, "f")]}
        for index, name in components.get(pos[1], []):
            def get_component(run):
                entry = read(run)
                return ABSENT if entry is ABSENT else entry[index]

            if partition(runs, get_component) == target:
                scalar[pos, name] = all(read(run) is not ABSENT for run in runs)
    replacement = {p for p in exact if p[1] != "D"} | read_with_repeats
    return {
        "marks": len(runs),
        "exact_positions": exact,
        "scalar_positions": scalar,
        "same_inducing_positions_with_repeated_partners": exact == replacement,
        "some_inducing_entry_with_repeated_partners": bool(replacement),
        "target": target,
        "values": values,
    }


def step_number(kind):
    return {"g": 1, "m": 2, "a": 3, "b": 4, "c": 5, "D": 6, "f": 7, "w": 8}[kind]


def replay_late_positions(label, indexed, cohorts, registered, classes):
    counts = defaultdict(Counter)
    examples = {}
    jobs = defaultdict(list)
    for (law, h), group in indexed.items():
        for run in group.values():
            if run.a:
                jobs[law, h, run.nu].append(run)
    for row in read_rows(f"run{label}_handed.jsonl.gz"):
        law, h, nu = tuple(row["key"]), row["h"], row["nu"]
        runs = jobs.get((law, h, nu))
        if runs is None:
            continue
        scope = str_key(*law, h)
        prefix = cohorts[scope]["longest_prefix_over_active_cells"]
        archive = row["handed"][str(prefix)]
        stat = counts[scope]
        if archive["J_demand_r2_induces"]:
            stat["already_recounted_using_saved_round2_values"] += 1
            continue
        stars = registered["made_class"][f"made-{h}"][nu]
        witness = recheck_numbering(runs, stars, law, prefix, classes)
        inducing = witness["exact_positions"]
        scalar = witness["scalar_positions"]
        expected = Counter({tuple(key): n for key, n in archive["inducing_kinds"]})
        actual = Counter((r, step_number(kind), kind) for r, kind, *_ in inducing)
        stat["replayed_numberings"] += 1
        stat["replayed_runs"] += witness["marks"]
        stat["replayed_courses_by_prefix"] += witness["marks"] * (prefix - 1)
        stat["inducing_positions_agree_by_round_step_and_kind"] += actual == expected
        stat["one_registered_entry"] += bool(inducing)
        stat["some_scalar_with_absence_allowed"] += bool(scalar)
        stat["some_scalar_without_absence"] += any(scalar.values())
        stat["some_D_anywhere"] += any(name == "D" for _, name in scalar)
        stat["same_inducing_positions_with_repeated_partners"] += witness["same_inducing_positions_with_repeated_partners"]
        stat["some_inducing_entry_with_repeated_partners"] += witness["some_inducing_entry_with_repeated_partners"]
        limit = "no_scalar" if not scalar else "scalar_needs_absence" if not any(scalar.values()) else "scalar_present"
        is_second_newest_numbering = nu == 1 and law[3] == "NEWEST" and h == 4
        if is_second_newest_numbering or f"{scope}|{limit}" not in examples:
            match = f"{scope}|{limit}"
            if is_second_newest_numbering:
                match = f"{scope}|second_numbering|{limit}"
            examples[match] = {
                "nu": nu, "stars": stars, "prefix": prefix,
                "course_partition": sorted(sorted(part) for part in witness["target"]),
                "inducing_structured_positions": sorted(inducing),
                "inducing_scalar_positions": sorted((pos, name, complete) for (pos, name), complete in scalar.items()),
                "archived_inducing_position_counts": archive["inducing_kinds"],
                "replayed_inducing_position_counts": sorted(actual.items()),
            }
            if is_second_newest_numbering and len(inducing) == 1:
                (position,) = inducing
                examples[match]["entries_by_mark"] = [
                    {
                        "marks": marks,
                        "round_2_demands": [entry[0] for (r, kind, *_), entry in entries.items() if (r, kind) == (2, "D")],
                        "inducing_demand": entries[position][0],
                        "inducing_partner_descents": Counter(entries[position][1]),
                    }
                    for marks, entries in witness["values"].items()
                ]
    return {"counts": counts, "examples": examples}


def replay_smoke(registered, classes):
    by_case = defaultdict(list)
    target = {("NEWEST", 3, 0): 4, ("NEWEST", 4, 1): 3}
    for row in read_rows("run1r_runs.jsonl.gz"):
        key = row["law"]["choice"], row["h"], row["nu"]
        if key in target and row["a"]:
            by_case[key].append(run_record(row, classes))
        if len(by_case) == len(target) and all(len(runs) == 2**key[1] - 1 for key, runs in by_case.items()):
            break
    report = {}
    for (choice, h, nu), runs in by_case.items():
        law = "ORD", "CANCEL-RETIRE", "MET", choice, "parity"
        stars = registered["made_class"][f"made-{h}"][nu]
        result = recheck_numbering(runs, stars, law, target[choice, h, nu], classes)
        report[f"h={h}, nu={nu}"] = (len(result["exact_positions"]), len(result["scalar_positions"]))
    return report


def replay_planted(classes):
    base = defaultdict(dict)
    for row in read_json("runP.json.gz")["runs"]:
        if row["a"]:
            continue
        law = law_key(row)
        grown = Growth(row["stars"], (), law)
        for r in range(1, 4):
            grown.round(r)
            if r > 1:
                assert classes.find(grown.course(r)) == classes.find(row["courses"][str(r)])
        base[law[-1]][row["h"]] = grown
    report = {}
    for knot_law, runs in base.items():
        left, right = runs[5], runs[6]
        differences = defaultdict(set)
        for r in (2, 3):
            first, second = left.entries[r], right.entries[r]
            for pos in first.keys() | second.keys():
                if pos[1] != "demand_with_repeats" and first.get(pos) != second.get(pos):
                    differences[r, step_number(pos[1])].add(pos)
        first = min(differences)
        added = []
        for pos in sorted(differences[first]):
            assert pos[1] == "c"
            old, new = left.entries[first[0]][pos][0], right.entries[first[0]][pos][0]
            added.append(sorted(set(new) - set(old)))
        assert first == (3, 5) and all(item == [(('s', 8), (('s', right.y),))] for item in added)
        report[knot_law] = {
            "round_2_course_equal": not any(r == 2 for r, _ in differences),
            "first_difference_round_and_step": first,
            "round_3_join_candidate_lists_differing_first": len(added),
            "extra_candidate_and_supplier": added[0],
        }
    return report


def recount(smoke):
    registered = json.loads((REGISTRATION / "numberings.json").read_text())
    classes = CourseClasses()
    report = {
        "archive_input": str(DATA.relative_to(ROOT)),
        "gate_inventory": gate_inventory(),
        "numberings": numberings_check(registered),
        "inventory": {}, "course_sets": {}, "paired_rows": {}, "handed_rows": {}, "S5": {},
        "independent_late_entries": {},
    }
    main = {}
    for label in ("1", "1r", "1b", "N"):
        indexed, inventory, s5 = index_rows(label, classes, registered, smoke)
        report["inventory"][label] = inventory
        report["S5"].update(s5)
        if label == "N":
            report["negative_no_taking"] = negative_report(indexed)
            continue
        cohorts = {str_key(*law, h): cohort_report((law, h), rows) for (law, h), rows in indexed.items()}
        report["course_sets"].update(cohorts)
        report["paired_rows"][label] = pair_report(label, indexed, cohorts, smoke)
        report["handed_rows"][label] = handed_report(label, indexed, cohorts, smoke)
        if label == "1b":
            report["treatment_comparisons"] = crosscheck_treatments(main, indexed)
        else:
            assert not main.keys() & indexed.keys()
            main.update(indexed)
            if not smoke:
                report["independent_late_entries"][label] = replay_late_positions(label, indexed, cohorts, registered, classes)
    report["cross_height"] = compare_height(main)
    report["planted_control"] = two_starts_report("P", classes, registered)
    report["planted_control"]["independent_replay_to_round_3"] = replay_planted(classes)
    report["comparison_starts"] = two_starts_report("2", classes, registered)
    report["course_class_searches"] = {
        "distinct_raw_encodings": len(classes.exact), "exact_isomorphism_calls": classes.searches,
        "distinct_courses_pooled_over_all_runs_and_prefixes": classes.next_class,
    }
    if smoke:
        report["independent_late_entries"] = replay_smoke(registered, classes)
    return report


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="time the first complete jobs and controls without writing")
    args = parser.parse_args()
    report = recount(args.smoke)
    if args.smoke:
        print(json.dumps({key: report[key] for key in ("course_class_searches", "independent_late_entries")}, sort_keys=True))
        return
    (HERE / "a_counts.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
