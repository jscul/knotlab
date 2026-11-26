"""Check placement coverage, replay a seeded sample, and test short readings."""

import argparse
from collections import Counter, defaultdict
from contextlib import nullcontext
import gzip
import json
from pathlib import Path
import random
import resource
import sys
from time import process_time
from typing import NamedTuple

from reception_growth import (
    build_pair,
    far_members,
    first_own_difference,
    fork,
    grow,
    law_of,
    link_status,
)


HERE = Path(__file__).resolve().parent
PREDECESSOR = HERE.parent.parent / "LINKED-UNDER-CAP-20261126-001" / "linked_runs.jsonl.gz"
ARCHIVE = HERE.parent / "two_runs.jsonl.gz"
CAPS = ("CAP-3", "CAP-4")
SEED = 20261126
SETTING = 3
PREFIX = 16
MAX_ROUNDS = 32
KNOT_BOUND = 10000


class RoundComparison(NamedTuple):
    round: int
    baseline_births: int
    first_only_births: int
    both_births: int
    baseline_matches_first: bool
    first_matches_both: bool
    baseline_matches_both: bool


def read_rows(path):
    with gzip.open(path, mode="rt", encoding="utf-8") as source:
        for line in source:
            if line.strip():
                yield json.loads(line)


def pair_key(row):
    return row["law"], row["A"], row["B"]


def placements(row):
    """Keys for the intervention, separate from its observed outcome."""
    return tuple(row["first"]), row.get("t"), tuple(row.get("second", ()))


def read_inputs():
    eligible = {}
    for row in read_rows(PREDECESSOR):
        if row.get("law") not in CAPS or not row["A"].startswith("tri:"):
            continue
        linked = row["linked"]
        if len(linked) >= PREFIX and linked[PREFIX - 1] is True:
            key = pair_key(row)
            if key in eligible:
                raise ValueError(f"Repeated predecessor pair {key}")
            eligible[key] = row
    if Counter(key[0] for key in eligible) != {"CAP-3": 28, "CAP-4": 28}:
        raise ValueError("Unexpected predecessor eligibility")
    by_pair = defaultdict(list)
    for row in read_rows(ARCHIVE):
        key = pair_key(row)
        if key not in eligible:
            raise ValueError(f"Pair outside predecessor eligibility {key}")
        by_pair[key].append(row)
    return eligible, by_pair


def first_count(row):
    return sum(z["t0"] == SETTING and z["linked"] for z in row["changes"])


def sampled_keys(keys, eligible, per_stratum):
    rng = random.Random(SEED)
    strata = defaultdict(list)
    for key in keys:
        strata[key[0], first_count(eligible[key])].append(key)
    selected = []
    for candidates in strata.values():
        selected.extend(rng.sample(candidates, min(per_stratum, len(candidates))))
    return sorted(selected)


def count_missing(expected, observed):
    return sorted((Counter(expected) - Counter(observed)).elements())


def trace(whole, single, double):
    """Keep the birth counts and equality of exact descriptions in every common round."""
    return [
        RoundComparison(i, len(w), len(a), len(b), w == a, a == b, w == b)
        for i, (w, a, b) in enumerate(zip(whole.own_births, single.own_births, double.own_births), 1)
    ]


def classify(comparison, first_round, setting):
    next_diff = next((row.round for row in comparison if not row.first_matches_both), None)
    if next_diff is None:
        return "unheard", None
    if next_diff <= setting:
        raise ValueError("The second fork changed an earlier round")
    last = comparison[-1]
    if last.baseline_matches_both and last.round >= first_round:
        return "cancels", next_diff
    if next_diff <= first_round:
        return "merges", next_diff
    if not last.baseline_matches_both and not last.first_matches_both:
        return "two", next_diff
    return "second, not kept", next_diff


def second_alone(whole, single, double, t, second, comparison):
    # Use exact far ancestry and birth identity to match the target in the baseline.
    identity = single.identities[second]
    if identity is None:
        raise ValueError("The selected knot has no strictly far ancestry")
    counterparts = [
        u for u in range(whole.states[t].n_knots)
        if whole.identities[u] == identity and whole.states[t].usable(u)
    ]
    if len(counterparts) != 1:
        return {"live counterparts": counterparts}
    alone = fork(whole, t, counterparts[0])
    return {
        "target in unchanged growth": counterparts[0],
        "heard alone": first_own_difference(whole, alone, t)[0],
        "counts and agreement": [
            [*row[:4], len(a), a == w, a == f, a == b]
            for row, a, w, f, b in zip(
                comparison, alone.own_births, whole.own_births, single.own_births, double.own_births
            )
        ],
    }


def check_pair(key, predecessor, archived, replay=False):
    law, receiver, far = key
    pair = build_pair(receiver, far)
    whole = grow(pair, law_of(law), rounds=MAX_ROUNDS if replay else PREFIX)
    first_members = far_members(whole, SETTING) if whole.last_round >= SETTING else []
    link_through_prefix = [
        link_status(whole, t) for t in range(1, min(PREFIX, whole.last_round) + 1)
    ]
    histories, full_rows, new_rows = [], [], []
    for rank, (u, sharings) in enumerate(first_members):
        first = rank, u, sharings
        single = fork(whole, SETTING, u)
        r1, n = first_own_difference(whole, single, SETTING)
        if r1 is None and not replay and whole.last_round == single.last_round == PREFIX:
            whole = grow(pair, law_of(law))
            single = fork(whole, SETTING, u)
            r1, n = first_own_difference(whole, single, SETTING)
        second_members = (
            {t: far_members(single, t) for t in range(SETTING + 1, r1)} if r1 else {}
        )
        histories.append({
            "first": first,
            "r1": r1,
            "common rounds": n,
            "candidates after round": second_members,
            "first tie across rank 2": rank == 1 and len(first_members) > 2
            and sharings == first_members[2][1],
            "second tie across rank 5": [
                t for t, choices in second_members.items()
                if len(choices) > 5 and choices[4][1] == choices[5][1]
            ],
            "second tie across rank 8": [
                t for t, choices in second_members.items()
                if len(choices) > 8 and choices[7][1] == choices[8][1]
            ],
        })
        if not replay or rank >= 2:
            continue
        spec = dict(A=receiver, B=far, law=law, first=first, r1=r1)
        if r1 is None:
            new_rows.append(spec)
        controlled_cancel = False
        for t, choices in second_members.items():
            for u2, steps in choices:
                double = fork(single, t, u2)
                comparison = trace(whole, single, double)
                kind, r2 = classify(comparison, r1, t)
                row = dict(**spec, t=t, second=(u2, steps), kind=kind, r2=r2, rounds=len(comparison))
                new_rows.append(row)
                details = {
                    "row": row,
                    "reads": [whole.last_round, single.last_round, double.last_round],
                    "stops": [whole.stop, single.stop, double.stop],
                    "trace": comparison,
                }
                if kind == "cancels" and not controlled_cancel:
                    details["single second control"] = second_alone(whole, single, double, t, u2, comparison)
                    controlled_cancel = True
                full_rows.append(details)

    expected = []
    for history in histories[:2]:
        first = history["first"]
        if history["r1"] is None:
            expected.append((first, None, ()))
        for t, members in history["candidates after round"].items():
            expected.extend((first, t, member) for member in members)
    observed = [placements(row) for row in archived]
    predecessors = [
        (row["knot"], row["sharings"], row["heard"])
        for row in predecessor["changes"] if row["t0"] == SETTING and row["linked"]
    ]
    prefix_matches = [
        (u, steps, h["r1"]) for (u, steps), h in zip(first_members, histories)
    ][:5] == predecessors
    out = {
        "pair": key,
        "baseline link through 16": link_through_prefix,
        "baseline matches predecessor": link_through_prefix == predecessor["linked"][:PREFIX],
        "first histories match predecessor through its rank limit": prefix_matches,
        "first histories": histories,
        "archive rows": len(archived),
        "placement missing from archive": count_missing(expected, observed),
        "placement unsupported or repeated in archive": count_missing(observed, expected),
    }
    if replay:
        normalized_archive = [
            dict(row, first=tuple(row["first"]), **({"second": tuple(row["second"])} if "second" in row else {}))
            for row in archived
        ]
        expected_by_placement = {placements(row): row for row in normalized_archive}
        comparisons = [
            (row, expected_by_placement.get(placements(row))) for row in new_rows
        ]
        out.update({
            "rows rebuilt": len(new_rows),
            "archive rows exactly matched": sum(got == expected for got, expected in comparisons),
            "bad outcome comparisons": [(got, expected) for got, expected in comparisons if got != expected],
            "trace columns": RoundComparison._fields,
            "full comparison traces": full_rows,
        })
    return out


def past_benchmark(row):
    return row["t"] + row["second"][1] + 1


def extend_row(key, row, extra_rounds, bound):
    law, receiver, far = key
    benchmark = past_benchmark(row)
    target = benchmark + extra_rounds
    pair = build_pair(receiver, far)
    whole = grow(pair, law_of(law), rounds=target, bound=bound)
    first_rank, u1, _ = row["first"]
    assert far_members(whole, SETTING)[first_rank] == tuple(row["first"][1:])
    single = fork(whole, SETTING, u1)
    t, (u2, _) = row["t"], row["second"]
    assert tuple(row["second"]) in far_members(single, t)
    double = fork(single, t, u2)
    r1, _ = first_own_difference(whole, single, SETTING)
    comparison = trace(whole, single, double)
    kind, r2 = classify(comparison, r1, t)
    return {
        "archive row": row,
        "first hearing": r1,
        "benchmark": benchmark,
        "target round": target,
        "knot bound": bound,
        "reads": [whole.last_round, single.last_round, double.last_round],
        "stops": [whole.stop, single.stop, double.stop],
        "knots at end": [arm.states[-1].n_knots for arm in (whole, single, double)],
        "kind": kind,
        "r2": r2,
        "trace columns": RoundComparison._fields,
        "trace": comparison,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("coverage", "sample", "extend"))
    parser.add_argument("--cap", choices=CAPS)
    parser.add_argument("--case", help="Far-pattern label for one case")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--sample-per-stratum", type=int, default=2)
    parser.add_argument("--benchmark", type=int, help="Extension stratum")
    parser.add_argument("--extra-rounds", type=int, default=0)
    parser.add_argument("--bound", type=int, default=KNOT_BOUND)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    eligible, archive = read_inputs()
    keys = sorted(key for key in eligible if (args.cap is None or key[0] == args.cap)
                  and (args.case is None or key[2] == args.case))
    if not keys:
        parser.error("No eligible pairs matched")
    if args.mode == "sample" and not args.case:
        keys = sampled_keys(keys, eligible, args.sample_per_stratum)

    with args.out.open("x", encoding="utf-8") if args.out else nullcontext(sys.stdout) as out:
        if args.mode == "extend":
            pool = [
                (key, row) for key in keys for row in archive[key]
                if row.get("kind") == "unheard" and past_benchmark(row) > row["rounds"]
                and (args.benchmark is None or past_benchmark(row) == args.benchmark)
            ]
            if not pool:
                parser.error("No extension candidates met the filter")
            cases = random.Random(SEED).sample(pool, min(len(pool), args.limit or 1))
        else:
            cases = keys[:args.limit]
        for case in cases:
            started = process_time()
            if args.mode == "extend":
                key, row = case
                result = extend_row(key, row, args.extra_rounds, args.bound)
            else:
                result = check_pair(case, eligible[case], archive[case], replay=args.mode == "sample")
            result["cpu seconds"] = round(process_time() - started, 3)
            result["process peak KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            out.write(json.dumps(result, separators=(",", ":")) + "\n")
            out.flush()


if __name__ == "__main__":
    main()
