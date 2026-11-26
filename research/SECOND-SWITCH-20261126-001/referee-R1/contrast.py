"""Recount the predecessor's trials and rebuild its first and second changes."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import gzip
import json
from pathlib import Path
import random
from time import perf_counter


SOURCE = Path(__file__).resolve().parents[2] / "SHORT-AGAIN-20261126-001"
ROUNDS = 12
KNOT_BOUND = 1500
WAIT = "CANCEL-WAIT"
LINK_READINGS = ("class", "direct", "part")


def records(path):
    with gzip.open(path, "rt", encoding="utf-8") as file:
        yield from map(json.loads, file)


def key(row):
    return row["A"], row["B"], row["law"][0]


def phases(row):
    return (row["again"] + [[], []])[:2]


def heard_marks(marks):
    return [mark for mark in marks if mark["heard"] is not None]


def raw_audit():
    jam = defaultdict(Counter)
    selection = {}
    jam_rows = set()
    for row in records(SOURCE / "jam_d3_meeting.jsonl.gz"):
        law = tuple(row["law"])
        trial = (*key(row), law[1])
        assert row["d"] == 3 and row["join"] == "meeting" and trial not in jam_rows
        jam_rows.add(trial)
        far = [mark for mark in row["changes"] if mark["distance"] >= 3]
        heard = heard_marks(far)
        counts = jam[" / ".join(law)]
        counts["pair trials"] += 1
        counts["changes at three or more steps"] += len(far)
        counts["changes heard at three or more steps"] += len(heard)
        counts["pairs hearing a change at three or more steps"] += bool(heard)
        if law[1] == WAIT and heard:
            selection[key(row)] = (row, heard[0])
            counts["selected first changes with an earlier hearing from another change"] += (
                heard[0]["heard"] != min(mark["heard"] for mark in heard)
            )

    archived = {}
    again = defaultdict(Counter)
    second_pairs = defaultdict(set)
    entered = set()
    discrepancies = []
    for row in records(SOURCE / "again_runs.jsonl.gz"):
        case = key(row)
        assert row["d"] == 3 and row["law"][1] == WAIT and case not in entered
        entered.add(case)
        if case not in selection:
            discrepancies.append({"case": case, "unexpected selected pair": row["first"]})
            continue
        original, first = selection[case]
        checks = {
            "first change": (row["first"], first["at"]),
            "first hearing": (row["h1"], first["heard"]),
            "rounds before first comparison": (min(row["rounds"]), first["rounds"]),
            "first hearing with waiting": (
                row["waiting at h1"],
                [first["waiting own without"], first["waiting own with"]],
            ),
        }
        for name, (observed, expected) in checks.items():
            if observed != expected:
                discrepancies.append({"case": case, name: [observed, expected]})

        archived[case] = (row, original, first)
        counts = again[case[2]]
        second, third = phases(row)
        heard_second, heard_third = heard_marks(second), heard_marks(third)
        counts["selected pairs"] += 1
        counts["pairs with a second comparison"] += bool(second)
        counts["second changes compared"] += len(second)
        counts["second changes heard"] += len(heard_second)
        counts["pairs hearing a second change"] += bool(heard_second)
        counts["second changes with fewer than 12 rounds compared"] += sum(
            mark["rounds"] < ROUNDS for mark in second
        )
        counts["pairs with a third comparison"] += bool(third)
        counts["third changes compared"] += len(third)
        counts["third changes heard"] += len(heard_third)
        counts["third changes with exactly one later round compared"] += sum(
            mark["rounds"] - mark["set after round"] == 1 for mark in third
        )
        if heard_second:
            second_pairs[case[2]].add(case[:2])
        for rank, mark in enumerate(second, 1):
            counts[f"second changes tried at rank {rank}"] += 1
            if mark["heard"] is None:
                continue
            counts[f"second changes heard at rank {rank}"] += 1
            counts[f"second changes heard in round {mark['heard']}"] += 1
            counts[f"second changes heard and set after round {mark['set after round']}"] += 1
            counts[f"second changes heard from {mark['sharings from A']} sharings"] += 1
            counts["second changes heard with waiting own knots"] += any(mark["waiting"])
    for case in sorted(selection.keys() - entered):
        discrepancies.append({"case": case, "missing selected pair": selection[case][1]["at"]})

    matched = second_pairs["ONE-FEWER"] == second_pairs["REC-ONE-FEWER"]
    report = {
        "jam trials by law and short-knot treatment": jam,
        "second and third trials by law": again,
        "selected pairs from first hearings at three or more steps": len(selection),
        "selected pairs with a matching archived record": len(archived),
        "raw discrepancies": discrepancies,
        "same ordered pairs heard under the two one-fewer rations": matched,
        "receivers and number of senders hearing a second change under the record's one fewer": Counter(
            A for A, _ in second_pairs["REC-ONE-FEWER"]
        ),
    }
    return report, archived


@dataclass(frozen=True)
class Reading:
    own: tuple
    own_short: int
    links: dict


def grow(state, history=(), fork_after=None):
    readings = list(history)
    fork = state.copy() if state.r == fork_after else None
    while state.r < ROUNDS and len(state.h) <= KNOT_BOUND:
        previous = state.r
        state.step()
        if state.r == previous:
            break
        readings.append(Reading(
            tuple(state.own),
            sum(state.role[u] == 1 for u in state.short),
            state.links(),
        ))
        if state.r == fork_after:
            fork = state.copy()
    return readings, fork


def hearing(without, with_change, after=0, *, counts_only=False):
    def births(reading):
        return len(reading.own) if counts_only else reading.own

    return next((
        r for r, (left, right) in enumerate(zip(without, with_change), 1)
        if r > after and births(left) != births(right)
    ), None)


def waiting_pair(without, with_change, heard):
    if heard is None:
        return None
    return [without[heard - 1].own_short > 0, with_change[heard - 1].own_short > 0]


def read_links(readings, round_number):
    if 1 <= round_number <= len(readings):
        return readings[round_number - 1].links
    return None


def far_candidates(state):
    distances = state.distances()
    members = [u for u, h in enumerate(state.h) if h and state.role[u] == 2]
    ordered = sorted(members, key=lambda u: (distances.get(u, float("inf")), u))
    return [(u, distances.get(u)) for u in ordered[:5]]


def receiver_class(state):
    """Close the receiver's live members under shared distinctions and common knots."""
    live = {u for u, h in enumerate(state.h) if h}
    reached = {u for u in live if state.role[u] == 1}
    pending = list(reached)
    while pending:
        u = pending.pop()
        next_members = set(state.met[u])
        for common in state.met[u]:
            next_members.update(state.met[common])
        unseen = (next_members & live) - reached
        reached.update(unseen)
        pending.extend(unseen)
    return reached


def compare(case, archived_row, jam_row, first, rebuild_second):
    from growth import start

    A, B, law = case
    h1 = archived_row["h1"]
    without, _ = grow(start(A, B, law))
    with_first, fork = grow(start(A, B, law, change=archived_row["first"]), fork_after=h1)
    comparisons = {
        "rounds": ([len(without), len(with_first)], archived_row["rounds"]),
        "first hearing": (hearing(without, with_first), h1),
        "first waiting": (waiting_pair(without, with_first, h1), archived_row["waiting at h1"]),
        "baseline own births each round": ([len(row.own) for row in without], jam_row["own births"]),
        "marked own births each round": ([len(row.own) for row in with_first], first["own births with"]),
        "baseline waiting counts each round": ([row.own_short for row in without], jam_row["A short"]),
        "marked waiting counts each round": ([row.own_short for row in with_first], first["A short with"]),
    }
    discrepancies = {
        name: {"rebuild": observed, "record": recorded}
        for name, (observed, recorded) in comparisons.items() if observed != recorded
    }
    second, _ = phases(archived_row)
    candidates = far_candidates(fork) if fork and h1 < len(with_first) else []
    recorded_candidates = [(m["knot"], m["sharings from A"]) for m in second]
    if candidates != recorded_candidates:
        discrepancies["second candidates"] = {"rebuild": candidates, "record": recorded_candidates}

    linked_to_receiver = receiver_class(fork) if candidates else set()
    second_rows = []
    for (u, distance), record in zip(candidates, second):
        if (u, distance) != (record["knot"], record["sharings from A"]):
            continue
        row = {
            "knot": u,
            "sharings": distance,
            "recorded hearing": record["heard"],
            "marked member shares a class with an own member of the receiver at setting": u in linked_to_receiver,
        }
        if rebuild_second:
            changed = fork.copy()
            changed.mark(u, "add")
            with_second, _ = grow(changed, history=with_first[:h1])
            h2 = hearing(with_first, with_second, after=h1)
            waiting = waiting_pair(with_first, with_second, h2)
            observed = (h2, min(len(with_first), len(with_second)), waiting)
            expected = (record["heard"], record["rounds"], record["waiting"])
            if observed != expected:
                row["discrepancy"] = {"rebuild": observed, "record": expected}
            row["rebuilt hearing"] = h2
            if h2 is not None:
                row["hearing by birth counts alone"] = hearing(with_first, with_second, after=h1, counts_only=True)
                row["links at hearing"] = {
                    name: [read_links(readings, h2 - 1), read_links(readings, h2)]
                    for name, readings in (("without", without), ("first", with_first), ("second", with_second))
                }
        second_rows.append(row)

    return {
        "receiver": A,
        "sender": B,
        "ration": law,
        "first change": archived_row["first"],
        "first hearing": h1,
        "recorded second hearing": bool(heard_marks(second)),
        "without first change": [row.links for row in without],
        "with first change": [row.links for row in with_first],
        "second marks": second_rows,
        "discrepancies": discrepancies,
    }


def link_summary(cases):
    summary = defaultdict(Counter)
    for case in cases:
        heard = "recorded second hearing" if case["recorded second hearing"] else "no recorded second hearing"
        out = summary[f"{case['ration']} / {heard}"]
        out["pairs rebuilt"] += 1
        out["pairs with any discrepancy"] += bool(case["discrepancies"]) or any(
            "discrepancy" in mark for mark in case["second marks"]
        )
        first_round = case["first hearing"]
        for course in ("without first change", "with first change"):
            sequence = case[course]
            out[f"{course}: round 12 read"] += len(sequence) == ROUNDS
            for reading in LINK_READINGS:
                values = [row[reading] for row in sequence]
                out[f"{course}: {reading} from round 1 through 12"] += (
                    len(values) == ROUNDS and all(v is True for v in values)
                )
                out[f"{course}: {reading} at round 12"] += (
                    len(values) == ROUNDS and values[-1] is True
                )
                out[f"{course}: {reading} at first hearing"] += (
                    len(values) >= first_round and values[first_round - 1] is True
                )
            out[f"{course}: both ends present at round 12"] += (
                len(sequence) == ROUNDS and sequence[-1]["class"] is not None
            )
            out[f"{course}: wholly apart by round 4 through 12 with both ends present"] += (
                len(sequence) == ROUNDS and all(row["class"] is False for row in sequence[3:])
            )
            first_apart = next((r for r, row in enumerate(sequence, 1) if row["class"] is False), None)
            if first_apart is not None:
                out[f"{course}: first wholly apart in round {first_apart}"] += 1
                out[f"{course}: wholly apart by round 4 and never later linked through rounds read"] += (
                    first_apart <= 4 and not any(row["class"] is True for row in sequence[first_apart:])
                )

        for mark in case["second marks"]:
            linked = mark["marked member shares a class with an own member of the receiver at setting"]
            recorded = mark["recorded hearing"] is not None
            out["second candidates rebuilt"] += 1
            out["second candidates in the receiver's class at setting"] += linked
            out["archived second hearings reproduced as candidates"] += recorded
            out["archived second hearings in the receiver's class at setting"] += recorded and linked
            out["second comparisons rebuilt"] += "rebuilt hearing" in mark
            if "links at hearing" not in mark:
                continue
            out["second changes heard in the rebuild"] += 1
            out["second changes heard in the same round by birth counts alone"] += (
                mark["hearing by birth counts alone"] == mark["rebuilt hearing"]
            )
            for arm, (before, after) in mark["links at hearing"].items():
                for when, links in (("before", before), ("after", after)):
                    out[f"{arm}: round read {when} second hearing"] += links is not None
                    out[f"{arm}: both ends present {when} second hearing"] += (
                        links is not None and links["class"] is not None
                    )
                    for reading in LINK_READINGS:
                        out[f"{arm}: {reading} {when} second hearing"] += (
                            links is not None and links[reading] is True
                        )
    return summary


def cap_swap(case):
    """Give the same starts and first change a cap, at the archived setting round."""
    from growth import start

    A, B = case["receiver"], case["sender"]
    h1, mark = case["first hearing"], case["first change"]
    without, _ = grow(start(A, B, "CAP-3"))
    with_first, _ = grow(start(A, B, "CAP-3", change=mark))
    return {
        "receiver": A,
        "sender": B,
        "first change": mark,
        "second change set after round under the record's one fewer": h1,
        "first hearing under a cap of three": hearing(without, with_first),
        "with first change": [row.links for row in with_first],
        "without first change": [row.links for row in without],
    }


def cap_swap_summary(cases):
    summary = Counter()
    for case in cases:
        round_number = case["second change set after round under the record's one fewer"]
        summary["pairs rebuilt with the cap"] += 1
        summary["first change heard with the cap"] += case["first hearing under a cap of three"] is not None
        for course in ("without first change", "with first change"):
            reads = case[course]
            summary[f"{course}: class linked at any round from 4 on"] += any(
                row["class"] is True for row in reads[3:]
            )
            if len(reads) < round_number:
                summary[f"{course}: setting round beyond the knot bound"] += 1
            elif reads[round_number - 1]["class"] is None:
                summary[f"{course}: an end absent at setting round"] += 1
            elif reads[round_number - 1]["class"]:
                summary[f"{course}: class linked at setting round"] += 1
            else:
                summary[f"{course}: wholly apart at setting round"] += 1
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--raw-only", action="store_true")
    parser.add_argument("--law", action="append")
    parser.add_argument("--sample-per-group", type=int)
    parser.add_argument("--seed", type=int, default=20261126)
    parser.add_argument("--second", choices=("all", "recorded-hearing-pairs", "none"), default="all")
    args = parser.parse_args()

    t0 = perf_counter()
    raw, archived = raw_audit()
    result = {"raw": raw}
    cases = []
    if not args.raw_only:
        groups = defaultdict(list)
        for case, (row, _, _) in sorted(archived.items()):
            if not args.law or case[2] in args.law:
                groups[(case[2], bool(heard_marks(phases(row)[0])))].append(case)
        rng = random.Random(args.seed)
        chosen = []
        for members in groups.values():
            if args.sample_per_group is not None and len(members) > args.sample_per_group:
                members = sorted(rng.sample(members, args.sample_per_group))
            chosen.extend(members)
        for case in chosen:
            row, jam, first = archived[case]
            replay = args.second == "all" or (
                args.second == "recorded-hearing-pairs" and heard_marks(phases(row)[0])
            )
            cases.append(compare(case, row, jam, first, rebuild_second=replay))
        capped = [
            cap_swap(case) for case in cases
            if case["ration"] == "REC-ONE-FEWER" and case["recorded second hearing"]
        ]
        result["rebuild"] = {
            "round limit": ROUNDS,
            "knot bound": KNOT_BOUND,
            "seed": args.seed if args.sample_per_group is not None else None,
            "sample per group": args.sample_per_group,
            "second comparisons": args.second,
            "pairs rebuilt": len(cases),
            "pairs with records but no rebuild": len(archived) - len(cases),
            "summary": link_summary(cases),
            "cases": cases,
            "cap swap on pairs hearing twice under the record's one fewer": {
                "summary": cap_swap_summary(capped),
                "cases": capped,
            },
        }
    result["elapsed seconds"] = round(perf_counter() - t0, 3)

    if args.out is not None:
        args.out.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "archived": len(archived),
        "raw discrepancies": len(raw["raw discrepancies"]),
        "rebuilt": len(cases),
        "rebuild discrepancies": sum(len(case["discrepancies"]) for case in cases),
        "second discrepancies": sum("discrepancy" in mark for case in cases for mark in case["second marks"]),
        "elapsed seconds": result["elapsed seconds"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
