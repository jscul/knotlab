"""Recount the closed bench streams and measure exposure to a late first difference."""

import argparse
from collections import Counter, defaultdict, deque
from hashlib import sha256
import gzip
from itertools import combinations, combinations_with_replacement, islice, product
import json
from pathlib import Path
from typing import NamedTuple


HERE = Path(__file__).resolve().parent
BENCH = HERE.parent / "bench"
FILES = {
    "main": "bench_runs.jsonl.gz",
    "take marks": "bench_take_marks.jsonl.gz",
    "owing": "bench_owing.jsonl.gz",
    "first launch": "bench_first_launch.jsonl.gz",
}
PATTERNS = ("ring", "copier", "source")
JOINS = ("meeting", "share")
RATIONS = ("CAP-3", "FLOOR1", "ORD")
TREATMENTS = ("CANCEL-WAIT", "CANCEL-RETIRE", "CANCEL-OFFSHOOT")
TAKES = (None, "MET-SOLE", "STEPS1-SOLE", "STEPS2-SOLE")
OWING = (
    "PARENT-OWING",
    "PARENT-OWING-CAP3",
    "PARENT-OWING-CAP4",
    "OFFSHOOT-TWO",
    "OFFSHOOT-THREE",
    "PARENT-OWING-1",
    "PARENT-OWING-PLAIN",
    "MOD2",
)
READINGS = ("A", "B")
ROUND_FIELDS = (
    "own members by round",
    "own births by round",
    "joined by round",
    "kept by round",
    "joined to the other by round",
)
CHECKPOINTS = (2, 4, 6, 8)
MARK = "mark at a start knot of the other"
OWN = "own making first differs"
JOINT = "joint descent first differs"
STUB = "own making differs from with a stub, first round"
STUB_ROUNDS = "rounds compared with the stub"
BARE = "own series is the bare pattern's through"
RETIRED = "other retired after round"
HORIZON = "rounds read"
TOOK = "births that took"
SHORT = "short members by round"
JOINT_BIRTHS = "joint descent, births by round"
STARS = {
    "ring": (
        (4, 0, 5, 6, 7),
        (0, 1, 8, 9, 10),
        (1, 2, 11, 12, 13),
        (2, 3, 14, 15, 16),
        (3, 4, 17, 18, 19),
    ),
    "copier": ((0, 1, 2), (0, 3, 4)),
    "source": (
        (0, 1, 2, 9, 10, 11),
        (0, 1, 3),
        (4, 5, 12, 13, 14),
        (6, 7, 15, 16, 17),
        (2, 3, 4, 6, 18, 19, 20),
        (7, 8, 21, 22),
        (5, 8, 23, 24),
    ),
}


class Case(NamedTuple):
    join: str
    first: str
    second: str
    steps: int
    ration: str
    treatment: str
    take: str | None


def identity(row):
    spec = row.get("spec", row)
    law = spec["law"] if "law" in spec else (spec["ration"], spec["treatment"], spec["take"])
    return Case(spec["join"], spec["A"], spec["B"], spec["steps"], *law)


def valid_first_difference(first, common, after=0):
    return first is None or after < first <= common


def validate_row(key, row, pass_name, marked):
    if "not run" in row:
        assert row["not run"] == "the clock", row
        assert row["spec"]["marks"] == marked, row
        return
    horizon = row[HORIZON]
    bound = 8000 if pass_name == "first launch" else 3000
    assert row["ended by"] in {"rounds", "knots"}, row
    assert 1 <= horizon <= 12, row
    assert (row["knots"] > bound) == (row["ended by"] == "knots"), row
    assert row["ended by"] == "knots" or horizon == 12, row
    assert list(row["reads"]) == list(READINGS), key
    assert len(row[JOINT_BIRTHS]) == horizon, key
    if pass_name != "first launch":
        assert len(row[SHORT]) == horizon, key
    for side in READINGS:
        reading = row["reads"][side]
        own_pattern, other_pattern = (key.first, key.second) if side == "A" else (key.second, key.first)
        assert reading["pattern"] == own_pattern, key
        assert all(len(reading[field]) == horizon for field in ROUND_FIELDS), key
        assert all(k <= j for k, j in zip(reading["kept by round"], reading["joined by round"])), key
        assert 0 <= reading[BARE] <= horizon, key
        assert 0 <= reading[STUB_ROUNDS] <= horizon, key
        assert valid_first_difference(reading[STUB], reading[STUB_ROUNDS]), key
        assert set(reading[RETIRED]) == {str(n) for n in CHECKPOINTS if n <= horizon}, key
        for checkpoint, check in reading[RETIRED].items():
            assert int(checkpoint) <= check["rounds compared"] <= horizon, key
            assert valid_first_difference(check[OWN], check["rounds compared"], int(checkpoint)), key
        assert (MARK in reading) == marked, key
        for i, comparison in enumerate(reading.get(MARK, {}).values()):
            assert i < len(STARS[other_pattern]), key
            assert 0 <= comparison["rounds compared"] <= horizon, key
            assert all(valid_first_difference(comparison[field], comparison["rounds compared"])
                       for field in (OWN, JOINT)), key
        if marked:
            assert set(reading[MARK]) == {str(i) for i in range(len(STARS[other_pattern]))}, key


def load_rows(limit):
    pairs = tuple(combinations_with_replacement(PATTERNS, 2))
    starts = tuple((join, *pair, steps) for join, pair, steps in product(JOINS, pairs, (1, 2, 3)))
    main = [Case(*start, ration, treatment, take)
            for take, start, ration, treatment in product(TAKES, starts, RATIONS, TREATMENTS)]
    plans = {
        "main": main,
        "take marks": [key for key in main if key.take == "MET-SOLE"],
        "owing": [Case(*start, ration, treatment, None)
                  for start, ration, treatment in product(starts, OWING, TREATMENTS)],
        "first launch": main[:123],
    }
    result = {}
    for pass_name, filename in FILES.items():
        with gzip.open(BENCH / filename, "rt", encoding="utf-8") as source:
            rows = [json.loads(line) for line in islice(source, limit)]
        plan = plans[pass_name][:limit]
        assert len(rows) == len(plan), (pass_name, len(rows), len(plan))
        index = {}
        for key, row in zip(plan, rows):
            assert identity(row) == key, (pass_name, key, identity(row))
            validate_row(key, row, pass_name, pass_name != "main" or key.take is None)
            index[key] = row
        result[pass_name] = index
    return result


def complete(rows):
    return {case: row for case, row in rows.items() if "reads" in row}


def readings(rows):
    for row in rows:
        for side, reading in row["reads"].items():
            yield row, side, reading


def mark_records(rows):
    for row, side, reading in readings(rows):
        for mark_index, mark in reading.get(MARK, {}).items():
            yield row, side, int(mark_index), mark


def maximum_positive(seq):
    return max((i for i, n in enumerate(seq, 1) if n > 0), default=0)


def firsts(items, field):
    return dict(sorted(Counter(v[field] for v in items if v[field] is not None).items()))


def checkpoint_counts(rows):
    out = {}
    for checkpoint in CHECKPOINTS:
        records = [(row, reading[RETIRED][str(checkpoint)])
                   for row, _, reading in readings(rows) if str(checkpoint) in reading[RETIRED]]
        changed = [(row, check) for row, check in records if check[OWN] is not None]
        out[checkpoint] = {
            "fork recorded": len(records),
            "original continued": sum(row[HORIZON] > checkpoint for row, _ in records),
            "both continued": sum(check["rounds compared"] > checkpoint for _, check in records),
            "first differences": firsts([check for _, check in changed], OWN),
            "changes by step count": dict(Counter(row["steps"] for row, _ in changed)),
        }
    return out


def witnessed_steps(case, receiver, mark_index):
    """Shortest initial co-input route in the marked start.

    One step joins any pair met by the same third knot.
    A witness may itself have loose distinctions. Only the route's endpoints at
    each step need a loose distinction. The added mark can make its holder live.
    This is an initial route length and does not require a birth to be kept.
    """
    first = [set((0, d) for d in knot) for knot in STARS[case.first]]
    second = [set((1, d) for d in knot) for knot in STARS[case.second]]
    right = len(first)
    stars = first + second + [set() for _ in range(case.steps - 1)]
    endpoints = [0] + list(range(right + len(second), len(stars))) + [right]
    for step, (left, next_knot) in enumerate(zip(endpoints, endpoints[1:])):
        if case.join == "share":
            stars[left].add((2, step))
            stars[next_knot].add((2, step))
        else:
            d = 5 * step
            stars[left].update(((2, d), (2, d + 3)))
            stars[next_knot].update(((2, d + 1), (2, d + 2), (2, d + 4)))
            stars.append({(2, d), (2, d + 1), (2, d + 2)})
    if case.join == "share":
        for i in endpoints[1:-1]:
            stars[i].add((3, i))
    marked = right + mark_index if receiver == "A" else mark_index
    stars[marked].add((4, 0))
    multiplicities = Counter(d for knot in stars for d in knot)
    live = {i for i, knot in enumerate(stars) if any(multiplicities[d] == 1 for d in knot)}
    others = range(right) if receiver == "A" else range(right, right + len(second))
    targets = set(others) & live
    partners = {i: set() for i in live}
    for w, witness in enumerate(stars):
        met = [j for j in live if j != w and witness & stars[j]]
        for a, b in combinations(met, 2):
            partners[a].add(b)
            partners[b].add(a)
    pending = deque([(marked, 0)])
    reached = {marked}
    while pending:
        i, steps = pending.popleft()
        if i in targets:
            return steps
        for j in partners[i] - reached:
            pending.append((j, steps + 1))
            reached.add(j)
    return None


def incidence_steps(case, receiver, mark_index):
    """Declared join steps plus initial shared-distinction steps inside the marked pattern."""
    pattern = case.second if receiver == "A" else case.first
    stars = [set(knot) for knot in STARS[pattern]]
    pending = deque([(0, 0)])
    reached = {0}
    while pending:
        i, steps = pending.popleft()
        if i == mark_index:
            return case.steps + steps
        for j in range(len(stars)):
            if j not in reached and stars[i] & stars[j]:
                reached.add(j)
                pending.append((j, steps + 1))
    raise AssertionError((pattern, mark_index))


def exposure(rows, witnessed, incidence):
    marks = list(mark_records(rows))
    marked_rows = {identity(row): row for row, _, _, _ in marks}
    out = {
        "cases": len(rows),
        "case horizons": dict(Counter(row[HORIZON] for row in rows)),
        "cases past round 6": sum(row[HORIZON] > 6 for row in rows),
        "marked cases": len(marked_rows),
        "marked cases whose baseline goes past round 6": sum(row[HORIZON] > 6 for row in marked_rows.values()),
        "readings": sum(len(row["reads"]) for row in rows),
        "readings whose baseline goes past round 6": sum(len(row["reads"]) for row in rows if row[HORIZON] > 6),
        "marked readings": len({(identity(row), side) for row, side, _, _ in marks}),
        "marks": len(marks),
        "mark common horizons": dict(Counter(mark["rounds compared"] for _, _, _, mark in marks)),
        "first differences": {field: firsts([m for _, _, _, m in marks], field) for field in (OWN, JOINT)},
        "late first differences": [],
        "own first differences at round 6": [],
        "initial witnessed steps": Counter(),
        "initial sharing steps within marked pattern plus join steps": Counter(),
        "unheard by own knots at round 6 and compared past round 6 by initial witnessed steps": Counter(),
        "unheard by own knots at round 6 and compared past round 6 by initial sharing steps plus join steps": Counter(),
        "joint first difference versus initial witnessed steps": Counter(),
    }
    categories = {field: {"round 6 reached": set(), "past round 6": set(), "at risk": set()}
                  for field in (OWN, JOINT)}
    for row, side, index, mark in marks:
        case = identity(row)
        key = (case.join, case.first, case.second, case.steps, side, index)
        distance = witnessed[key]
        sharing_distance = incidence[key]
        out["initial witnessed steps"][str(distance) if distance is not None else "disconnected"] += 1
        out["initial sharing steps within marked pattern plus join steps"][sharing_distance] += 1
        if mark[OWN] == 6:
            out["own first differences at round 6"].append({
                "case": case, "reading": side, "mark": index,
                "rounds compared": mark["rounds compared"], "witnessed steps": distance,
            })
        for field in (OWN, JOINT):
            first = mark[field]
            horizon = mark["rounds compared"]
            cells = categories[field]
            if first is not None and first > 6:
                out["late first differences"].append({
                    "case": case, "reading": side, "mark": index, "field": field,
                    "first difference": first, "rounds compared": horizon, "witnessed steps": distance,
                })
            if horizon >= 6 and (first is None or first > 6):
                cells["round 6 reached"].add((case, side, index))
            if horizon > 6:
                cells["past round 6"].add((case, side, index))
                if first is None or first > 6:
                    cells["at risk"].add((case, side, index))
                    if field == OWN:
                        out["unheard by own knots at round 6 and compared past round 6 by initial witnessed steps"][
                            str(distance) if distance is not None else "disconnected"] += 1
                        out["unheard by own knots at round 6 and compared past round 6 by initial sharing steps plus join steps"][
                            sharing_distance] += 1
        if mark[JOINT] is not None:
            same = distance is not None and mark[JOINT] == distance
            out["joint first difference versus initial witnessed steps"]["equal" if same else "different"] += 1
    out["exposure"] = {
        field: {
            label: {"marks": len(cells), "cases": len({case for case, _, _ in cells}),
                    "readings": len({(case, side) for case, side, _ in cells})}
            for label, cells in groups.items()
        }
        for field, groups in categories.items()
    }
    past_seven = [
        (identity(row), side, index, mark[JOINT]) for row, side, index, mark in marks
        if mark["rounds compared"] > 7
    ]
    still_unheard = [(key, side) for key, side, _, first in past_seven if first is None or first > 7]
    out["joint exposure past round 7"] = {
        "marks compared past 7": len(past_seven),
        "still unheard through 7 and compared past 7": len(still_unheard),
        "cases with such a mark": len({key for key, _ in still_unheard}),
        "readings with such a mark": len(set(still_unheard)),
        "first differences past 7": sum(first is not None and first > 7 for _, _, _, first in past_seven),
    }
    return out


def table_row(rows, heading, join, ration, treatment):
    read = [reading for _, _, reading in readings(rows)]
    marks = [mark for _, _, _, mark in mark_records(rows)]
    retire8 = [r[RETIRED]["8"] for r in read if "8" in r[RETIRED]]
    return {
        "table": heading,
        "join": join,
        "ration": ration,
        "treatment": treatment,
        "cases": len(rows),
        "readings": len(read),
        "cases with a short knot": sum(any(row[SHORT]) for row in rows),
        "still joined at the last round read": sum(r["joined by round"][-1] > 0 for r in read),
        "latest kept join": max(maximum_positive(r["kept by round"]) for r in read),
        "differs from with a stub": sum(r[STUB] is not None for r in read),
        "retired after 8: tested": len(retire8),
        "retired after 8: own births differ": sum(m[OWN] is not None for m in retire8),
        "marks": len(marks),
        "marks heard by own knots": sum(m[OWN] is not None for m in marks),
        "latest first round, own": max((m[OWN] for m in marks if m[OWN] is not None), default=None),
        "marks heard by the joint descent": sum(m[JOINT] is not None for m in marks),
        "latest first round, joint": max((m[JOINT] for m in marks if m[JOINT] is not None), default=None),
    }


def published_table(no_take, take_mark, full):
    take_title = (
        f"A birth may take a sole candidate from a knot its parent meets "
        f"({len(take_mark)} cases read, {324 - len(take_mark)} not run)"
    )
    headings = {"meeting": "a meeting", "share": "a shared distinction"}
    ration_labels = {"ORD": "ordinary count", "CAP-3": "cap of three", "FLOOR1": "just enough for three"}
    treatment_labels = dict(zip(TREATMENTS, ("waits", "retires", "offshoots")))
    table = []
    markdown_cells = []
    correction = []
    for title, rows in (("Nothing taken", no_take), (take_title, take_mark)):
        for join, ration, treatment in product(JOINS, ("ORD", "CAP-3", "FLOOR1"), TREATMENTS):
            cell = [row for case, row in rows.items() if (case.join, case.ration, case.treatment)
                    == (join, ration, treatment)]
            if not cell:
                continue
            counts = table_row(cell, title, join, ration, treatment)
            table.append(counts)
            denominator = checkpoint_counts(cell)[8]["both continued"]
            if denominator != counts["retired after 8: tested"]:
                correction.append({
                    "row": len(table), "table": title, "join": join, "ration": ration, "treatment": treatment,
                    "reported": counts["retired after 8: tested"], "both continued": denominator,
                    "positive": counts["retired after 8: own births differ"],
                })
            markdown_cells.append([
                headings[join], ration_labels[ration], treatment_labels[treatment], str(counts["readings"]),
                f"{counts['cases with a short knot']} of {counts['cases']}",
                str(counts["still joined at the last round read"]), str(counts["latest kept join"]),
                str(counts["differs from with a stub"]),
                f"{counts['retired after 8: own births differ']} of {counts['retired after 8: tested']}",
                f"{counts['marks heard by own knots']} of {counts['marks']} ({counts['latest first round, own']})",
                f"{counts['marks heard by the joint descent']} of {counts['marks']} ({counts['latest first round, joint']})",
            ])
    result = {"recount": table, "checkpoint denominators needing a later common round": correction}
    if full:
        expected_json = json.loads((BENCH / "bench_table.json").read_text(encoding="utf-8"))["table"]
        md_lines = [(i, [cell.strip() for cell in line.strip("|").split("|")])
                    for i, line in enumerate((BENCH / "bench_table.md").read_text(encoding="utf-8").splitlines(), 1)
                    if line.startswith(("| a meeting |", "| a shared distinction |"))]
        assert len(table) == len(expected_json) == len(md_lines), (len(table), len(expected_json), len(md_lines))
        result["json mismatches"] = [dict(row=i, actual=actual, expected=expected)
                                     for i, (actual, expected) in enumerate(zip(table, expected_json), 1)
                                     if actual != expected]
        result["markdown mismatches"] = [dict(line=i, actual=actual, expected=expected)
                                         for actual, (i, expected) in zip(markdown_cells, md_lines) if actual != expected]
        for item in correction:
            item["markdown line"] = md_lines[item["row"] - 1][0]
    return result


def cross_pass(early, main, marked_take):
    summary = {"early shared": len(early.keys() & main.keys()), "early only": len(early.keys() - main.keys()),
               "marked take shared": len(marked_take.keys() & main.keys()),
               "marked take only": len(marked_take.keys() - main.keys())}
    series = Counter()
    differences = Counter()
    early_stub = defaultdict(Counter)
    early_marks = Counter()
    compared_joint_rounds = 0
    unequal_joint_rounds = 0
    common_horizons = Counter()
    for key in early.keys() & main.keys():
        before, after = early[key], main[key]
        common = min(before[HORIZON], after[HORIZON])
        common_horizons[(before[HORIZON], after[HORIZON])] += 1
        compared_joint_rounds += common
        unequal_joint_rounds += sum(a != b for a, b in zip(before[JOINT_BIRTHS][:common], after[JOINT_BIRTHS][:common]))
        for side in READINGS:
            previous, final = before["reads"][side], after["reads"][side]
            for field in ROUND_FIELDS:
                series[field] += common
                differences[field] += sum(a != b for a, b in zip(previous[field][:common], final[field][:common]))
            early_stub[side]["first differences in early raw"] += previous[STUB] is not None
            early_stub[side]["first differences in final raw"] += final[STUB] is not None
            rounds = min(previous[STUB_ROUNDS], final[STUB_ROUNDS])
            seen_then = previous[STUB] if previous[STUB] and previous[STUB] <= rounds else None
            seen_now = final[STUB] if final[STUB] and final[STUB] <= rounds else None
            early_stub[side]["first difference verdicts disagree in common rounds"] += seen_then != seen_now
            for mark_name, earlier in previous[MARK].items():
                later = final[MARK][mark_name]
                shared = min(earlier["rounds compared"], later["rounds compared"])
                early_marks["matched mark comparisons"] += 1
                early_marks["early mark read further"] += earlier["rounds compared"] > later["rounds compared"]
                for field in (OWN, JOINT):
                    seen = [mark[field] if mark[field] and mark[field] <= shared else None for mark in (earlier, later)]
                    early_marks[f"{field}: unequal first differences in shared rounds"] += seen[0] != seen[1]
    summary["early horizon pairs"] = {f"{a},{b}": n for (a, b), n in sorted(common_horizons.items())}
    summary["early common series entries"] = series
    summary["early common series entries that differ"] = differences
    summary["early stub raw verdict comparisons"] = early_stub
    summary["early mark comparisons"] = early_marks
    summary["early joint birth counts"] = {"rounds compared": compared_joint_rounds, "unequal": unequal_joint_rounds}
    summary["marked repeats with unequal non-mark records excluding elapsed seconds"] = []
    for key in marked_take.keys() & main.keys():
        marked = {f: value for f, value in marked_take[key].items() if f not in {"seconds", "reads"}}
        baseline = {f: value for f, value in main[key].items() if f not in {"seconds", "reads"}}
        nonmark = {side: {f: value for f, value in mark_read.items() if f != MARK}
                   for side, mark_read in marked_take[key]["reads"].items()}
        if marked != baseline or nonmark != main[key]["reads"]:
            summary["marked repeats with unequal non-mark records excluding elapsed seconds"].append(key)
    return summary


def take_comparisons(main):
    results = {}
    for take in TAKES[1:]:
        counts = Counter()
        for case, row in main.items():
            if case.take != take:
                continue
            counts["completed take cases"] += 1
            counts["cases where a birth took"] += row[TOOK] > 0
            counts["births that took"] += row[TOOK]
            baseline = main.get(case._replace(take=None))
            if baseline is None:
                counts["no completed baseline"] += 1
                continue
            counts["paired cases"] += 1
            common = min(row[HORIZON], baseline[HORIZON])
            counts["different baseline horizons"] += row[HORIZON] != baseline[HORIZON]
            exact_change = False
            common_change = False
            for side in READINGS:
                a, b = row["reads"][side], baseline["reads"][side]
                fields = ("own births by round", "joined by round", "kept by round")
                compare = min(a[STUB_ROUNDS], b[STUB_ROUNDS])
                in_a = a[STUB] if a[STUB] and a[STUB] <= compare else None
                in_b = b[STUB] if b[STUB] and b[STUB] <= compare else None
                exact = a[STUB] != b[STUB] or any(a[field] != b[field] for field in fields)
                sliced = in_a != in_b or any(a[field][:common] != b[field][:common] for field in fields)
                counts["reported field mismatches per directed reading"] += exact
                counts["reading differences on comparable rounds"] += sliced
                exact_change |= exact
                common_change |= sliced
            counts["reported field mismatches per case"] += exact_change
            counts["cases differing on comparable rounds"] += common_change
            counts["cases with differences attributable only to incomparable horizons"] += exact_change and not common_change
            if row[TOOK] == 0:
                counts["paired cases with no birth taking"] += 1
                counts["paired cases differing on comparable rounds despite no birth taking"] += common_change
            if take != "MET-SOLE":
                nonmark = {side: {f: value for f, value in rd.items() if f != MARK}
                           for side, rd in baseline["reads"].items()}
                counts["pairs unequal on any stored reading field ignoring marks"] += nonmark != row["reads"]
                fields = (HORIZON, "ended by", "knots", TOOK, SHORT, JOINT_BIRTHS)
                counts["pairs unequal on any stored baseline count field"] += any(row[f] != baseline[f] for f in fields)
        results[take] = counts
    return results


def grouped_retirements(no_take, marked_take):
    by_pattern = defaultdict(set)
    by_side = defaultdict(set)
    differing = []
    for case, row in (no_take | marked_take).items():
        for side, rd in row["reads"].items():
            fork = rd[RETIRED].get("8")
            if fork is None or fork[OWN] is None:
                continue
            key = case.take, case.join, case.first, case.second, case.steps, case.treatment
            by_pattern[(*key, rd["pattern"])].add(case.ration)
            by_side[(*key, side)].add(case.ration)
            differing.append({
                "case": case, "reading": side, "first difference": fork[OWN],
                "latest original kept join": maximum_positive(rd["kept by round"]),
                "joined in round 8": rd["joined by round"][7] > 0,
            })
    return {
        "positive reading-law rows": len(differing),
        "grouped by receiver pattern across rations": len(by_pattern),
        "grouped by directed reading across rations": len(by_side),
        "two or more rations grouped by receiver pattern": sum(len(rs) >= 2 for rs in by_pattern.values()),
        "two or more rations grouped by directed reading": sum(len(rs) >= 2 for rs in by_side.values()),
        "by receiver pattern under two or more rations": [
            {"group": group, "rations": sorted(rs)} for group, rs in sorted(by_pattern.items(), key=lambda item: str(item[0]))
            if len(rs) >= 2
        ],
        "positive cases with no original kept join after 8": [
            item for item in differing if item["latest original kept join"] <= 8
        ],
    }


def paired_case_groups(main, no_take, take_mark):
    groups = {}
    for label, cohort in (("nothing taken", no_take), ("sole take with marks", take_mark)):
        for join in JOINS:
            for ration in RATIONS:
                for treatment in TREATMENTS:
                    group = [row for case, row in cohort.items()
                             if (case.join, case.ration, case.treatment) == (join, ration, treatment)]
                    if group:
                        groups[f"{label}, {join}, {ration}, {treatment}"] = {
                            "baseline horizons": dict(Counter(row[HORIZON] for row in group)),
                            "rounds with short members": dict(Counter(i for row in group
                                                                     for i, n in enumerate(row[SHORT], 1) if n)),
                            "latest candidate join": max(maximum_positive(rd["joined by round"])
                                                         for _, _, rd in readings(group)),
                            "own mark first differences": firsts(
                                [mark for _, _, _, mark in mark_records(group)], OWN),
                            "readings with at least one own mark first difference": len({
                                (identity(row), side) for row, side, _, mark in mark_records(group)
                                if mark[OWN] is not None
                            }),
                            "checkpoints": checkpoint_counts(group),
                        }
    ordinary = [row for case, row in no_take.items() if case.join == "meeting" and case.ration == "ORD"]
    shares = [row for case, row in no_take.items() if case.join == "share"]
    ordinary_all = [row for case, row in main.items() if case.join == "meeting" and case.ration == "ORD"]
    kept = defaultdict(Counter)
    for row, _, rd in readings(ordinary):
        pattern = rd["pattern"]
        last = maximum_positive(rd["kept by round"])
        kept[pattern]["readings"] += 1
        kept[pattern]["positive last"] += last == row[HORIZON]
        kept[pattern]["positive every observed round"] += all(rd["kept by round"])
        kept[pattern]["positive uninterrupted first 3 and no later"] += last == 3 and all(rd["kept by round"][:3])
    bare = {
        join: dict(Counter(rd[BARE] for _, _, rd in readings(row for case, row in no_take.items()
                                                            if case.join == join and case.steps == 1)))
        for join in JOINS
    }
    sites = {}
    for label, at_site in (("site", True), ("deeper", False)):
        marks = [mark for _, _, i, mark in mark_records(shares) if (i == 0) == at_site]
        sites[label] = {"marks": len(marks), "own first differences": firsts(marks, OWN)}
    mark_results = defaultdict(dict)
    missed_joint = Counter()
    for row, side, index, mark in mark_records(ordinary):
        case = identity(row)
        comparison_key = case.first, case.second, case.steps, side, index
        mark_results[comparison_key][case.treatment] = mark
        if mark[JOINT] is None:
            missed_joint[(case.second if side == "A" else case.first, index)] += 1
    treatment_mark_diffs = [
        {"mark": key, "comparisons": values}
        for key, values in mark_results.items()
        if len({(value[OWN], value[JOINT]) for value in values.values()}) > 1
    ]
    two_copiers = []
    for step, treatment in product((1, 2), TREATMENTS):
        ordinary_key = Case("share", "copier", "copier", step, "ORD", treatment, None)
        cap_key = ordinary_key._replace(ration="CAP-3")
        if ordinary_key not in no_take or cap_key not in no_take:
            continue
        ordinary_row, cap_row = no_take[ordinary_key], no_take[cap_key]
        two_copiers.append({
            "steps of bare sharing": step,
            "treatment": treatment,
            "short counts": {"ORD": ordinary_row[SHORT], "CAP-3": cap_row[SHORT]},
            "equal saved baseline and comparison fields": all(ordinary_row[field] == cap_row[field]
                                                                for field in ordinary_row if field not in {"law", "seconds"}),
        })
    return {
        "all law group checks": groups,
        "ordinary meeting nothing taken": {
            "cases": len(ordinary),
            "short cases": sum(any(row[SHORT]) for row in ordinary),
            "readings": 2 * len(ordinary),
            "stub differences": sum(rd[STUB] is not None for _, _, rd in readings(ordinary)),
            "stub comparison horizons": dict(Counter(rd[STUB_ROUNDS] for _, _, rd in readings(ordinary))),
            "baseline horizons": dict(Counter(row[HORIZON] for row in ordinary)),
            "kept by receiver pattern": kept,
            "one step checkpoint counts": checkpoint_counts([row for row in ordinary if row["steps"] == 1]),
            "checkpoint counts across all step counts": checkpoint_counts(ordinary),
            "joint mark nulls by marked pattern and index": {f"{p},{i}": n for (p, i), n in missed_joint.items()},
            "treatment changes in recorded first differences": treatment_mark_diffs,
        },
        "ordinary meeting across all main passes": {"cases": len(ordinary_all), "short cases": sum(any(row[SHORT])
                                                                                               for row in ordinary_all)},
        "shared distinction nothing taken": {
            "cases": len(shares), "cases short at any round": sum(any(row[SHORT]) for row in shares),
            "cases short at first round": sum(row[SHORT][0] > 0 for row in shares), "readings": 2 * len(shares),
            "stub differences": sum(rd[STUB] is not None for _, _, rd in readings(shares)), "marks by site": sites,
        },
        "one step bare matched-prefix lengths by join": bare,
        "ordinary and cap compared for two two-knot parts": two_copiers,
    }


def observational_counts(main):
    by_start = defaultdict(Counter)
    for key, row in main.items():
        point = key[:4]
        fields = (HORIZON, TOOK, "knots", SHORT, JOINT_BIRTHS)
        record = (
            tuple(tuple(row[f]) if isinstance(row[f], list) else row[f] for f in fields),
            tuple(tuple(tuple(r[f]) for f in ROUND_FIELDS) for r in row["reads"].values()),
        )
        by_start[point][record] += 1
    return [
        {"start": point, "completed configurations": sum(records.values()),
         "different saved baseline count series at their respective horizons": len(records)}
        for point, records in by_start.items()
    ]


def owing_counts(owing):
    result = {}
    for ration in OWING:
        rows = [row for key, row in owing.items() if key.ration == ration]
        result[ration] = {
            "cases": len(rows),
            "cases with no kept join between an own knot and another": sum(
                not any(any(rd["kept by round"]) for rd in row["reads"].values()) for row in rows),
            "last kept join between an own knot and another": max(
                (maximum_positive(rd["kept by round"]) for _, _, rd in readings(rows)), default=0),
            "cases with no candidate join between an own knot and another": sum(
                not any(any(rd["joined by round"]) for rd in row["reads"].values()) for row in rows),
            "last candidate join between an own knot and another": max(
                (maximum_positive(rd["joined by round"]) for _, _, rd in readings(rows)), default=0),
            "checkpoints": checkpoint_counts(rows),
        }
    return result


def candidate_joins_beyond_one(rows):
    results = {}
    for join, steps in product(JOINS, (2, 3)):
        items = [(identity(row), side, reading["joined to the other by round"])
                 for row, side, reading in readings(rows) if row["join"] == join and row["steps"] == steps]
        positive = [(case, side, series) for case, side, series in items if any(series)]
        results[f"{join}, {steps}"] = {
            "readings": len(items),
            "positive readings": len(positive),
            "cases with a positive reading": len({case for case, _, _ in positive}),
            "readings positive in first round": sum(series[0] > 0 for _, _, series in positive),
            "example": dict(zip(("case", "reading", "joined to the other by round"), positive[0])) if positive else None,
        }
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="pilot prefix per compressed stream")
    parser.add_argument("--output", type=Path, help="write the recount here")
    args = parser.parse_args()
    passes = load_rows(args.limit)
    good = {label: complete(p) for label, p in passes.items()}
    primary = good["main"]
    marked_take = good["take marks"]
    no_take = {case: row for case, row in primary.items() if case.take is None}
    owing = good["owing"]
    marked = no_take | marked_take | owing
    distinct = primary | marked_take | owing
    scheduled = passes["main"] | passes["take marks"] | passes["owing"]
    mark_schedule = ({case: row for case, row in passes["main"].items() if case.take is None}
                     | passes["take marks"] | passes["owing"])
    mark_keys = {(key.join, key.first, key.second, key.steps, side, i)
                 for key in good["first launch"] | marked
                 for side, pattern in (("A", key.second), ("B", key.first)) for i in range(len(STARS[pattern]))}
    witness = {key: witnessed_steps(Case(*key[:4], "ORD", "CANCEL-WAIT", None), key[4], key[5]) for key in mark_keys}
    sharing = {key: incidence_steps(Case(*key[:4], "ORD", "CANCEL-WAIT", None), key[4], key[5]) for key in mark_keys}
    failed = {label: set(rows) - set(good[label]) for label, rows in passes.items()}
    result = {
        "closed study commit": "9b6dad2e0c",
        "pilot prefix per stream": args.limit,
        "streams": {
            label: {
                "file": FILES[label],
                "sha256": sha256((BENCH / FILES[label]).read_bytes()).hexdigest(),
                "scheduled": len(rows), "completed": len(good[label]), "not run": len(failed[label]),
                "clock stops": sum(row.get("not run") == "the clock" for row in rows.values()),
                "clock stop factors": dict(Counter(f"{key.join}, {key.ration}, {key.treatment}, {key.take}" for key in failed[label])),
                "ended by": dict(Counter(row["ended by"] for row in good[label].values())),
                "greatest terminal knot count": max((row["knots"] for row in good[label].values()), default=0),
            } for label, rows in passes.items()
        },
        "distinct scheduled main plus later passes": len(scheduled),
        "distinct completed main plus later passes": len(distinct),
        "distinct scheduled with marks excluding the first launch": len(mark_schedule),
        "distinct completed with marks excluding the first launch": len(marked),
        "individual comparisons scheduled with marks": sum(len(STARS[key.first]) + len(STARS[key.second]) for key in mark_schedule),
        "clock stopped distinct configurations without any completion": len(scheduled.keys() - distinct.keys()),
        "clock stopped in both the main and mark passes": len(failed["main"] & failed["take marks"]),
        "completed main cases whose later marks timed out": len(primary.keys() & failed["take marks"]),
        "first launch and marked take comparisons": cross_pass(good["first launch"], primary, marked_take),
        "exposure": {
            "main": exposure(list(primary.values()), witness, sharing),
            "nothing taken": exposure(list(no_take.values()), witness, sharing),
            "take marks": exposure(list(marked_take.values()), witness, sharing),
            "owing": exposure(list(owing.values()), witness, sharing),
            "first launch": exposure(list(good["first launch"].values()), witness, sharing),
            "headline distinct": exposure(list(distinct.values()), witness, sharing),
            "all marked headline cases": exposure(list(marked.values()), witness, sharing),
            "ordinary meeting nothing taken": exposure(
                [row for case, row in no_take.items() if case.join == "meeting" and case.ration == "ORD"], witness, sharing),
        },
        "published bench table": published_table(no_take, marked_take, args.limit is None),
        "take comparisons": take_comparisons(primary),
        "grouped retirements after 8": grouped_retirements(no_take, marked_take),
        "bench README checks": paired_case_groups(primary, no_take, marked_take),
        "candidate joins between own knots and other descent beyond one step": {
            label: candidate_joins_beyond_one(rows.values()) for label, rows in good.items()
        },
        "distinct recorded baseline series per joined start": observational_counts(primary),
        "owing rations": owing_counts(owing),
    }
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    main()
