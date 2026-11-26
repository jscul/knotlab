"""Give one or two connecting knots loose distinctions in the 30-knot preparation."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path
import resource
from time import perf_counter

from cuts_reader import Incidence, bits, inspect, mask, normal, simple, span
from replay_growth import ARMS, demand, grow


HERE = Path(__file__).resolve().parent


def cases(initial):
    loose = [len([d for d in row if len(initial.owners[d]) == 1]) for row in initial.supports]
    existing = {i for i, count in enumerate(loose) if count}
    available = sorted(set(range(len(loose))) - existing)
    assert available == list(range(15, 30))
    neighbors = [set() for _ in loose]
    for own in initial.owners.values():
        if len(own) == 2:
            a, b = own
            neighbors[a].add(b)
            neighbors[b].add(a)
    for size in (1, 2):
        for selected in combinations(available, size):
            live = existing | set(selected)
            needed = Counter(k for group in demand([meet & live for meet in neighbors]) for k in group)
            for reading in ("one added, previous funding kept", "meet the demand", "meet demand plus one"):
                amounts = [0] * len(loose)
                for knot in live:
                    if reading == "one added, previous funding kept":
                        amounts[knot] = int(knot in selected)
                    else:
                        amounts[knot] = max(0, max(1, needed[knot]) - loose[knot])
                        if reading == "meet demand plus one" and knot in selected:
                            amounts[knot] += 1
                next_name = max(initial.owners) + 1
                rows = []
                for old, new in zip(initial.supports, amounts):
                    rows.append((*old, *range(next_name, next_name + new)))
                    next_name += new
                yield reading, selected, tuple(rows)


def three(stage, parities):
    codes = [normal(c, stage.laws) for c in parities]
    rank = len(span(codes))
    adds_to_zero = codes[0] ^ codes[1] ^ codes[2] == 0
    ring_knot = rank == 2 and adds_to_zero
    shortest = stage.projected_moves(parities[0] | parities[1] | parities[2])
    all_are_labels = all(code and all((f & m).bit_count() % 2 == 0 for m in shortest)
                         for code, f in zip(codes, parities))
    all_unread = False
    if all_are_labels:
        listed, _ = stage.reader_spaces()
        all_unread = all(all(normal(code, reader) for reader in listed) for code in codes)
    closed = all(not (f & stage.loose) and simple(stage, f) for f in parities)
    return {"rank": rank, "minimal even relation": ring_knot, "simple cycles": closed,
            "three unread nonconstant labels": all_unread}


def run(pilot):
    started = perf_counter()
    source_record = next(iter(json.loads((HERE / "construct_born.json").read_text())["preparations"].values()))
    original = Incidence(tuple(map(tuple, source_record["source supports"])))
    original_three = [mask(d for d, own in original.owners.items() if len(own) == 1 and r <= own[0] < r + 5)
                      for r in (0, 5, 10)]
    totals = defaultdict(Counter)
    examples = {}
    finishes = Counter()
    count = Counter()
    unique = set()
    cache = {}
    for reading, selected, rows in cases(original):
        if pilot and selected not in ((15,), (17,), (15, 16), (17, 25)):
            continue
        count[reading, len(selected)] += 1
        unique.add(rows)
        if rows not in cache:
            initial = Incidence(rows)
            source_three = three(initial, original_three)
            arms = {}
            for arm in ARMS:
                previous, previous_three = initial, source_three
                sequence = [(0, source_three, None)]
                stop = "studied through round 3"
                for age in (1, 2, 3):
                    following, status = grow(previous.supports, arm)
                    if status != "funded":
                        stop = f"{status} at round {age}"
                        break
                    stage = Incidence(following)
                    if len(stage.owners) > 512:
                        stop = f"over 512 distinctions at round {age}, not read"
                        break
                    outcome = inspect(stage, previous, initial)
                    current_three = three(stage, original_three)
                    sequence.append((age, current_three, outcome))
                    if arm == "ordinary":
                        assert outcome["old state rank removed"] == 0
                        assert current_three["rank"] == previous_three["rank"]
                    previous, previous_three = stage, current_three
                arms[arm] = (sequence, stop)
            cache[rows] = arms
        for arm, (sequence, stop) in cache[rows].items():
            finishes[reading, len(selected), arm, stop] += 1
            last = None
            for age, reading_three, outcome in sequence:
                tally = totals[reading, len(selected), arm, age]
                tally["settings with this stage"] += 1
                tally["original three values freely vary"] += int(reading_three["rank"] == 3)
                tally["original three parities make a minimal even relation"] += int(reading_three["minimal even relation"])
                tally["original three are unread labels"] += int(reading_three["three unread nonconstant labels"])
                tally["original three give a frozen binding"] += int(all(
                    reading_three[k] for k in ("minimal even relation", "three unread nonconstant labels", "simple cycles")))
                if last is not None and last["rank"] == 3 and reading_three["minimal even relation"]:
                    tally["new minimal relation on the original three"] += 1
                    if reading_three["three unread nonconstant labels"] and reading_three["simple cycles"]:
                        tally["new frozen binding on the original three"] += 1
                if outcome:
                    interesting = []
                    for field in ("old state rank removed", "forced dimension newly added by this growth"):
                        if outcome[field] > 0:
                            tally["settings with " + field] += 1
                    if not outcome["complete"]:
                        tally["search incomplete"] += 1
                        interesting.append("unresolved search")
                    for reader in ("all listed supports", "only supports passing K1–K3"):
                        if reader in outcome:
                            for field in ("minimal splits", "new at this growth"):
                                if outcome[reader][field] > 0:
                                    tally[f"{reader}, settings with {field}"] += 1
                                    interesting.append(f"{reader}, {field}")
                    if last is not None and last["rank"] == 3 and reading_three["minimal even relation"]:
                        interesting.append("three original values gain a minimal relation")
                    for reason in interesting:
                        key = f"{arm}: {reason}"
                        if key not in examples:
                            examples[key] = {
                                "selected source knots": selected, "funding": reading, "round": age,
                                "modified start": rows, "specified parities": [list(bits(c)) for c in original_three],
                                "before": last, "after": reading_three, "all-carrier search": outcome}
                last = reading_three
    return {
        "pilot": pilot, "weighting": "Use every one- or two-element subset of the fifteen initially unprovided connecting knots of the 30-knot preparation with each of three stated funding rules. Each setting has one vote. Identical resulting starts are computed once and retain their setting weights.",
        "fixed three labels": "Keep exactly the ten originally loose distinctions belonging to each of the three five-knot rings, including after changes to funding. The generic cycle search is separately free to use other supports.",
        "distinct modified starts": len(unique),
        "settings": [{"funding": r, "number of selected connecting knots": n, "count": v}
                     for (r, n), v in sorted(count.items())],
        "tables": [{"funding": r, "number of selected connecting knots": n, "growth law": arm,
                    "round": t, **v} for (r, n, arm, t), v in sorted(totals.items())],
        "finishes": [{"funding": r, "number of selected connecting knots": n, "growth law": arm,
                      "finish": stop, "settings": v} for (r, n, arm, stop), v in sorted(finishes.items())],
        "first examples": examples,
        "elapsed seconds": perf_counter() - started,
        "peak resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024 ** 3, 2 * 1024 ** 3))
    result = run(args.pilot)
    filename = "cuts_changes_pilot.json" if args.pilot else "cuts_changes.json"
    (HERE / filename).write_text(json.dumps(result, indent=2) + "\n")
    print(filename, result["elapsed seconds"], result["distinct modified starts"])
