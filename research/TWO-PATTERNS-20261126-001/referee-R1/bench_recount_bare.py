"""Check bare-pattern survival and compare finite joint-birth sequences."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

from bench_recount import (
    Case, HORIZON, JOINT_BIRTHS, PATTERNS, RATIONS, SHORT, TOOK, TREATMENTS, complete, load_rows,
)
from regrow_engine import Growth, WorkLimit, joined


ROUNDS = 12
BENCH_CAP = 3000
EXTENSION_CAP = 25_000
PILOT_BARE = {
    ("source", "ORD", "CANCEL-WAIT"),
    ("ring", "ORD", "CANCEL-WAIT"),
    ("source", "FLOOR1", "CANCEL-OFFSHOOT"),
    ("source", "FLOOR1", "CANCEL-WAIT"),
    ("copier", "ORD", "CANCEL-WAIT"),
}
PILOT_PAIRS = {
    (1, "CAP-3", "CANCEL-WAIT"),
    (2, "ORD", "CANCEL-WAIT"),
    (2, "FLOOR1", "CANCEL-OFFSHOOT"),
}


def grow(a, b, steps, ration, treatment, bound, names=None, retire=None, join="share", take=None):
    stars, roles = joined(a, b, steps, join)
    state = Growth(stars, roles, ration, treatment, take, name_table=names)
    records, own_names = [], []
    stop = "rounds"
    for round_number in range(1, ROUNDS + 1):
        try:
            step = state.step()
        except WorkLimit as err:
            stop = str(err)
            break
        ancestry = state.ancestry
        joint_births = sum({"A", "B"} <= ancestry[knot] for knot in step["births"])
        by_side = {}
        signatures = {}
        for side, other in (("A", "B"), ("B", "A")):
            own = frozenset([side])
            own_births = [k for k in step["births"] if ancestry[k] == own]
            cross = [group for group in step["groups"]
                     if any(ancestry[k] == own for k in group) and any(ancestry[k] != own for k in group)]
            by_side[side] = {
                "members": sum(ancestry[k] == own for k in step["members"]),
                "births": len(own_births),
                "candidate joins": len(cross),
                "kept joins": sum(step["short"].isdisjoint(group) for group in cross),
                "joins with other descent": sum(any(other in ancestry[k] for k in group) for group in cross),
            }
            if names is not None:
                signatures[side] = sorted((state.tokens[k], step["fresh"][k], len(state.places[k]))
                                          for k in own_births)
        own_names.append(signatures)
        records.append({
            "round": round_number, "knots": len(state.places),
            "members before births": len(step["members"]), "members after births": len(state.active),
            "short": len(step["short"]), "births": len(step["births"]),
            "joint births": joint_births, "takes": step["takes"], "by side": by_side,
        })
        if retire is not None and round_number == retire[0]:
            records[-1]["members retired"] = state.retire(retire[1])
        if len(state.places) > bound:
            stop = "knots"
            break
    return records, own_names, stop


def bare_case(pattern, ration, treatment):
    records, _, stop = grow(pattern, None, 1, ration, treatment, EXTENSION_CAP)
    first_over_bench_cap = next((row["round"] for row in records if row["knots"] > BENCH_CAP), None)
    return {
        "pattern": pattern, "ration": ration, "treatment": treatment,
        "rounds checked": len(records), "stop": stop,
        "first round over the bench knot cap": first_over_bench_cap,
        "round 12": records[-1] if len(records) == ROUNDS else None,
        "rounds": [{key: value for key, value in row.items() if key != "by side"} for row in records],
    }


def pair_case(case, raw, check_retirement=False):
    first, second = case.first, case.second
    steps, ration, treatment = case.steps, case.ration, case.treatment
    names = {} if check_retirement else None
    records, signatures, stop = grow(first, second, steps, ration, treatment, BENCH_CAP, names,
                                     join=case.join, take=case.take)
    check = {
        HORIZON: len(records), "ended by": stop, "knots": records[-1]["knots"] if records else None,
        JOINT_BIRTHS: [row["joint births"] for row in records],
        SHORT: [row["short"] for row in records], TOOK: sum(row["takes"] for row in records),
    }
    differences = [key for key, value in check.items() if value != raw[key]]
    fields = {
        "own members by round": "members", "own births by round": "births",
        "joined by round": "candidate joins", "kept by round": "kept joins",
        "joined to the other by round": "joins with other descent",
    }
    for side in ("A", "B"):
        for field, measured in fields.items():
            if raw["reads"][side][field] != [row["by side"][side][measured] for row in records]:
                differences.append(f"{side}: {field}")
    result = {
        "case": case,
        "differences from closed baseline fields": differences,
        "joint births": check[JOINT_BIRTHS], "own births": {
            side: [row["by side"][side]["births"] for row in records] for side in ("A", "B")
        },
        "short by round": check[SHORT], "terminal knot count": check["knots"],
        "kept joins": {side: [row["by side"][side]["kept joins"] for row in records] for side in ("A", "B")},
    }
    if check_retirement:
        alternate, changed, _ = grow(first, second, steps, ration, treatment, BENCH_CAP, names, retire=(8, "B"),
                                     join=case.join, take=case.take)
        common = min(len(alternate), len(records))
        first = next((i + 1 for i in range(8, common) if signatures[i]["A"] != changed[i]["A"]), None)
        result["retire other descent after round 8"] = {
            "members retired": alternate[7]["members retired"],
            "first own difference, by exact making": first, "rounds compared": common,
            "closed comparison": raw["reads"]["A"]["other retired after round"]["8"],
        }
    return result


def arithmetic_suffix(counts):
    """Length and increment of the longest positive arithmetic suffix."""
    if not counts[-1]:
        return 0, None
    if len(counts) < 2 or not counts[-2]:
        return 1, None
    increment = counts[-1] - counts[-2]
    length = 2
    for i in range(len(counts) - 3, -1, -1):
        if counts[i] <= 0 or counts[i + 1] - counts[i] != increment:
            break
        length += 1
    return length, increment


def sequence_inventory(rows):
    summary = Counter()
    by_first = {}
    by_suffix = {}
    smaller_series = []
    for case, row in rows.items():
        series = row[JOINT_BIRTHS]
        summary["recorded configurations"] += 1
        if len(series) < ROUNDS:
            summary["ended before round 12"] += 1
            continue
        summary["through round 12"] += 1
        if not any(series):
            summary["no joint birth through round 12"] += 1
            continue
        if not series[-1]:
            summary["joint births had ceased at round 12"] += 1
            continue
        summary["joint births in round 12"] += 1
        length, increment = arithmetic_suffix(series)
        first = next(i for i, count in enumerate(series) if count > 0)
        if length >= 4:
            key = (*case[:4], length, increment)
            result = by_suffix.setdefault(key, {"cases": 0, "representative": case, "births": series})
            result["cases"] += 1
            summary["at least four final positive rounds of arithmetic growth"] += 1
            if length == len(series) - first:
                key = (*case[:4], first + 1, increment)
                result = by_first.setdefault(key, {"cases": 0, "representative": case, "births": series})
                result["cases"] += 1
                summary["arithmetic from first positive to round 12, at least four positive rounds"] += 1
        if length < len(series) - first and series[-1] <= 24 and all(series[first:]):
            summary["nonarithmetic and continuously positive from first birth with at most 24 births in round 12"] += 1
            smaller_series.append({"case": case, "births": series})
    return {
        "counts": summary,
        "arithmetic from first positive round": [
            {"start and first round and increment": key, **value} for key, value in by_first.items()
        ],
        "arithmetic in at least the final four positive rounds": [
            {"start and suffix length and increment": key, **value} for key, value in by_suffix.items()
        ],
        "continuously positive smaller nonarithmetic examples": sorted(
            smaller_series, key=lambda example: (example["births"][-1], repr(example["case"])))[:5],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = load_rows(None)
    main_runs = complete(rows["main"])
    owing = complete(rows["owing"])
    nothing_taken = {case: row for case, row in main_runs.items() if case.take is None}
    bare_plan = tuple(product(PATTERNS, RATIONS, TREATMENTS))
    pair_replays = tuple(Case("share", "copier", "copier", *plan, None) for plan in product((1, 2), RATIONS, TREATMENTS))
    all_relevant = {case: row for case, row in (main_runs | owing).items() if case.take in (None, "MET-SOLE")}
    near_replays = [
        case for case, row in all_relevant.items() if case not in pair_replays
        and row[HORIZON] == ROUNDS and arithmetic_suffix(row[JOINT_BIRTHS])[0] >= 4
    ]
    if args.pilot:
        bare_plan = [plan for plan in bare_plan if plan in PILOT_BARE]
        pair_replays = tuple(case for case in pair_replays if (case.steps, case.ration, case.treatment) in PILOT_PAIRS)
        near_replays = [
            max((case for case in near_replays if case in cohort), key=lambda case: cohort[case]["knots"])
            for cohort in (nothing_taken, owing, {case: row for case, row in main_runs.items() if case.take == "MET-SOLE"})
        ]
    output = {
        "closed study commit": "9b6dad2e0c", "pilot": args.pilot,
        "original rounds and knot cap": [ROUNDS, BENCH_CAP], "extension knot cap for bare patterns": EXTENSION_CAP,
        "bare independent replays": [bare_case(*plan) for plan in bare_plan],
        "joined two-part independent replays": [
            pair_case(case, nothing_taken[case], case.steps == 1 and case.ration == "ORD" and case.treatment == "CANCEL-WAIT")
            for case in pair_replays
        ],
        "near alternative independent replays": [
            pair_case(case, all_relevant[case]) for case in near_replays
        ],
        "raw near alternatives": {
            "main nothing taken": sequence_inventory(nothing_taken),
            "main all nominal laws": sequence_inventory(main_runs),
            "main only the active take": sequence_inventory({case: row for case, row in main_runs.items()
                                                             if case.take == "MET-SOLE"}),
            "later owing pass": sequence_inventory(owing),
        },
    }
    payload = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    main()
