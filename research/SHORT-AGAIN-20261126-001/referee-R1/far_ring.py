"""Recount the unchanged far runs and the ring comparisons from the archives."""

import argparse
from collections import Counter
import gzip
from itertools import islice, product
import json
from pathlib import Path


RECORD = Path(__file__).resolve().parent.parent
STEPS = range(1, 9)
FAR_LAWS = ("ORD", "JOIN-FEWER", "BUSY-FEWER", "ONE-FEWER", "ODD-FEWER", "THIRD-FEWER")
TREATMENTS = ("CANCEL-WAIT", "CANCEL-RETIRE")
FEWER = ("JOIN-FEWER", "ONE-FEWER", "REC-ONE-FEWER")
RING_LAWS = ("ORD", "CAP-3", *FEWER)
JOINS = ("meeting", "share")


def archive(name, limit):
    with gzip.open(RECORD / name, "rt", encoding="utf-8") as src:
        return [json.loads(line) for line in islice(src, limit)]


def covers(keys, expected, pilot):
    assert len(keys) == len(set(keys))
    assert set(keys) <= expected if pilot else set(keys) == expected


def far_counts(rows, pilot):
    covers(
        [(row["d"], *row["law"]) for row in rows],
        set(product(STEPS, FAR_LAWS, TREATMENTS)),
        pilot,
    )
    frozen = []
    endpoints = Counter()
    heard = {}
    change_count = 0
    for row in rows:
        d = row["d"]
        law, treatment = row["law"]
        rounds = row["rounds"]
        assert row["A"] == row["B"] == "source"
        assert 1 <= rounds <= 16
        assert all(len(row[field]) == rounds for field in ("short", "kept", "own births", "joint births"))
        endpoints[row["ended"]] += 1
        changes = row["changes"]
        assert set(changes) == {
            "two", "less", *(f"B{i}" for i in range(7)), *(f"L{i}" for i in range(1, d)),
        }
        change_count += len(changes)
        for mark, observation in changes.items():
            horizon = observation["rounds"]
            assert 1 <= horizon <= rounds
            assert all(1 <= x <= horizon for x in (observation[k] for k in ("own", "joint", "groups")) if x is not None)
            if observation["own"] is not None:
                assert 1 <= observation["groups"] <= observation["own"]
                heard.setdefault(f"{law}/{treatment}", []).append([d, mark, observation["own"], horizon])

        # Two seven-knot sources, d-1 link knots, and one spent knot in each
        # meeting. With no short member in round 1, all usable old distinctions
        # are spent. Every round-1 birth receives a usable distinction.
        # Thus when the round-2 short count equals all cumulative births, the
        # endpoint count was already reached in round 1 and cannot later change.
        initial_knots = 2 * 7 + (d - 1) + d
        all_births = row["knots"] - initial_knots
        fixed = (
            treatment == "CANCEL-WAIT"
            and rounds == 16
            and all_births > 0
            and row["short"] == [0] + [all_births] * 15
        )
        expected_fixed = treatment == "CANCEL-WAIT" and (
            law in ("JOIN-FEWER", "ONE-FEWER") or (law == "BUSY-FEWER" and d <= 2)
        )
        assert fixed == expected_fixed, (d, law, treatment)
        if fixed:
            assert row["ended"] == "rounds"
            assert row["knots"] == 29 + 3 * d
            assert not any(value for series in ("own births", "joint births", "kept") for value in row[series][1:])
            frozen.append({
                "steps": d,
                "law": law,
                "initial_knots": initial_knots,
                "round_one_births": all_births,
                "round_two_through_sixteen_short": row["short"][1],
                "final_knots": row["knots"],
            })

    return {
        "cells": len(rows),
        "changes": change_count,
        "endpoint_reasons": endpoints,
        "unchanged_common_rounds": dict(sorted(Counter(row["rounds"] for row in rows).items())),
        "frozen_cells": frozen,
        "hearing_counts": {key: len(events) for key, events in heard.items()},
        "retiring_hearings": {key: events for key, events in heard.items() if key.endswith("CANCEL-RETIRE")},
        "busy_waiting_hearings": heard.get("BUSY-FEWER/CANCEL-WAIT", []),
        "changed_total_knots_saved": False,
    }


def count_checks(series, initial_knots):
    knots = series["knots"]
    counts = series["own births"]
    assert len(knots) == len(counts) == len(series["births by"]) == len(series["short by"])
    for old, new, births, counts_a in zip([initial_knots, *knots[:-1]], knots, series["births by"], counts):
        assert new - old == sum(births.values())
        assert counts_a == births.get("A", 0)


def distance_group(d):
    return "one_step" if d == 1 else "two_to_eight_steps"


def ring_counts(rows, pilot):
    covers(
        [(row["d"], row["law"], row["join"]) for row in rows],
        set(product(STEPS, RING_LAWS, JOINS)),
        pilot,
    )
    conditions = {}
    returned = []
    marks = {distance_group(d): {"first": [], "second_or_third": []} for d in (1, 2)}
    aligned = []
    direct_meetings = []
    shared_differences = []
    cap_meeting_differences = []
    direct_first_heard = []
    for row in rows:
        d, law, join = row["d"], row["law"], row["join"]
        rounds = row["rounds"]
        whole, stub = row["whole"], row["stub"]
        assert rounds == len(whole["knots"])
        links_and_spent = d - 1 + (d if join == "meeting" else 0)
        count_checks(whole, 7 + 5 + links_and_spent)
        count_checks(stub, 7 + 1 + links_and_spent)
        cap = row["ended"] == "knots"
        assert cap or row["ended"] == "rounds"
        assert all(n <= 3000 for n in whole["knots"][:-1])
        assert cap == (whole["knots"][-1] > 3000)
        assert cap or rounds == 16
        a, b = whole["own births"], stub["own births"]
        same_recorded_births = row["own births differ from with a stub, rounds"]
        assert same_recorded_births == sorted(set(same_recorded_births))
        assert all(1 <= r <= min(len(a), len(b)) for r in same_recorded_births)
        unequal_counts = [i for i, (x, y) in enumerate(zip(a, b), 1) if x != y]
        assert set(unequal_counts) <= set(same_recorded_births)
        if same_recorded_births:
            first_difference = [d, law, same_recorded_births[0], unequal_counts[0] if unequal_counts else None]
            if join == "share":
                shared_differences.append(first_difference)
            elif law == "CAP-3":
                cap_meeting_differences.append(first_difference)

        returns = row["ring returns"]
        should_return = law == "CAP-3" and ((join == "meeting" and d == 1) or (join == "share" and d >= 2))
        assert bool(returns) == should_return
        assert all(1 <= s < t <= rounds and k >= 5 for s, t, k in returns)
        assert row["changes from"] == ("returns" if returns else "rounds")
        tested = Counter(event[0] for event in row["marks"])
        if returns:
            returned_sizes = {}
            for _, end, size in returns:
                if end < rounds:
                    returned_sizes.setdefault(end, size)
            assert tested == {r: returned_sizes[r] for r in sorted(returned_sizes)[:6]}
            returned.append({"steps": d, "law": law, "join": join, "returns": returns, "marks": len(row["marks"])})
        else:
            assert tested == {r: 5 for r in range(2, 13, 2) if r < rounds}

        group = marks[distance_group(d)]
        assert len({(event[0], event[1]) for event in row["marks"]}) == len(row["marks"])
        for event in row["marks"]:
            placed, knot, heard, horizon = event
            assert 0 <= knot < whole["knots"][placed - 1]
            assert 2 <= placed < horizon <= rounds
            assert heard is None or placed < heard <= horizon
            group["first"].append(event)
            if heard is not None:
                direct_first_heard.append([d, law, join, *event])
        assert bool(row["again"]) == any(event[2] is not None for event in row["marks"])
        for event in row["again"]:
            placed, knot, heard, horizon = event
            assert 2 <= placed < horizon <= 16
            assert heard is None or placed < heard <= horizon
            group["second_or_third"].append(event)

        condition = conditions.setdefault(f"{law}/{join}", Counter())
        condition["starts"] += 1
        condition["first_marks"] += len(row["marks"])
        condition["heard_first_marks"] += sum(event[2] is not None for event in row["marks"])
        condition["second_or_third_marks"] += len(row["again"])

        if law not in FEWER or join != "meeting":
            continue
        delay = 1 if law == "JOIN-FEWER" else 2
        ring_start = d + 2 + delay
        assert not any(a[1:ring_start - 1]) and a[ring_start - 1] > 0
        if d == 1:
            previous_births = stub["births by"][0]
            assert not any(b[1:])
            assert stub["short by"][1:] == [previous_births] * (len(b) - 1)
            assert not any(stub["births by"][1:])
            direct_meetings.append({"law": law, "ring_restart": ring_start, "stub_rounds": len(b)})
            continue
        stub_start = d + 2
        assert not any(b[1:stub_start - 1]) and b[stub_start - 1] > 0
        tail_a, tail_b = a[ring_start - 1:], b[stub_start - 1:]
        overlap = min(len(tail_a), len(tail_b))
        assert overlap > 0 and tail_a[:overlap] == tail_b[:overlap]
        assert whole["births by"][0]["link"] == d == stub["births by"][0]["link"]
        assert whole["short by"][1]["link"] == d
        assert stub["short by"][1]["link"] == d - 1
        assert not whole["births by"][1].get("link") and stub["births by"][1]["link"] == 1
        if delay == 2:
            assert whole["short by"][2]["link"] == d and not whole["births by"][2].get("link")
        aligned.append({
            "steps": d, "law": law, "ring_restart": ring_start, "stub_restart": stub_start,
            "ring_end": len(a), "stub_end": len(b), "equal_counts_from_restart": tail_a[:overlap],
        })

    mark_totals = {
        name: {
            "first_marks": len(group["first"]),
            "first_heard": sum(event[2] is not None for event in group["first"]),
            "second_or_third_marks": len(group["second_or_third"]),
            "second_or_third_heard": sum(event[2] is not None for event in group["second_or_third"]),
            "rounds_read_after_first_marks": dict(sorted(Counter(r[3] - r[0] for r in group["first"]).items())),
        }
        for name, group in marks.items()
    }
    return {
        "starts": len(rows),
        "conditions": conditions,
        "returning_starts": returned,
        "first_mark_hearings": direct_first_heard,
        "mark_totals": mark_totals,
        "meeting_restart_comparisons": aligned,
        "direct_meeting_restart_comparisons": direct_meetings,
        "shared_starts_differing_from_stub": shared_differences,
        "cap_meetings_differing_from_stub": cap_meeting_differences,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", type=int, metavar="ROWS", help="read only the first ROWS per archive")
    args = parser.parse_args()
    if args.pilot is not None and args.pilot < 1:
        parser.error("--pilot must be positive")
    pilot = args.pilot is not None
    print(json.dumps({
        "far": far_counts(archive("far.jsonl.gz", args.pilot), pilot),
        "ring": ring_counts(archive("ring_line_runs.jsonl.gz", args.pilot), pilot),
    }, indent=2))


if __name__ == "__main__":
    main()
