"""Check archived closure certificates against the named physical holdings."""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import gzip
from itertools import combinations, product
import json
from pathlib import Path


ARCHIVE = (
    "artifacts/ERASURE-AND-CLOSING-SIGNS-20261121-001B/"
    "ERASURE-AND-CLOSING-SIGNS-20261121-001B-E001_closures/panels_histories.json.gz"
)


def require(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def physical_incidence(rows):
    incidence = defaultdict(list)
    for holder, row in enumerate(rows):
        require(len(set(row)) == len(row), "duplicate name in a physical knot")
        for name in row:
            incidence[name].append(holder)
    return incidence


def connected(start, allowed, neighbors):
    reached = {start}
    pending = [start]
    while pending:
        holder = pending.pop()
        unseen = (neighbors[holder] & allowed) - reached
        reached.update(unseen)
        pending.extend(unseen)
    return reached


def derived_closures(cut, incidence, neighbors):
    rows = cut["after_rows"]
    universe = set(range(len(rows)))
    require(all(0 < len(holders) <= 2 for holders in incidence.values()),
            "physical name has more than two holders")
    found = {}
    for birth in cut["births"]:
        holder = birth["holder"]
        require(cut["before_holder_count"] <= holder < len(rows), "invalid birth holder")
        require(birth["fresh"] == len(birth["new_names"]), "invalid physical grant size")
        require(set(rows[holder]) == set(birth["inputs"]) | set(birth["new_names"]),
                "birth support differs from the physical rows")
        if birth["new_names"]:
            continue
        component = connected(holder, universe, neighbors)
        names = {name for member in component for name in rows[member]}
        if all(len(incidence[name]) == 2 for name in names):
            found[holder] = component, names
    return found


def group_certificate(component, meetings, physical_pairs, neighbors, certificate):
    kind = certificate["kind"]
    parts = certificate["anchor_parts"]
    groups = dict(certificate["groups"])
    anchors = [anchor for part in parts for anchor in part]
    require(len(anchors) == len(set(anchors)), "repeated group anchor")
    require(len(groups) == len(certificate["groups"]) == len(anchors)
            and set(groups) == set(anchors), "wrong group roster")
    if kind == "five_all_pairs":
        require([len(part) for part in parts] == [5], "wrong five-group partition")
        required_pairs = {frozenset(pair) for pair in combinations(anchors, 2)}
    else:
        require(kind == "six_three_against_three", "unknown connected-group kind")
        require([len(part) for part in parts] == [3, 3], "wrong six-group partition")
        required_pairs = {frozenset(pair) for pair in product(*parts)}

    owner = {}
    for anchor, listed in groups.items():
        members = set(listed)
        require(len(members) == len(listed) and anchor in members and members <= component,
                "group does not contain its anchor or lies outside the physical component")
        require(members.isdisjoint(owner), "connected groups overlap")
        require(connected(anchor, members, neighbors) == members, "disconnected group")
        owner.update({member: anchor for member in members})

    available_pairs = {
        frozenset((owner[left], owner[right]))
        for left, right in meetings
        if left in owner and right in owner and owner[left] != owner[right]
    }
    require(required_pairs <= available_pairs, "required group meeting is absent")

    named_pairs = set()
    for path in certificate["paths"]:
        holders = path["holders"]
        names = path["named_meetings"]
        require(len(holders) >= 2 and len(holders) == len(names) + 1
                and len(holders) == len(set(holders)), "invalid named chain shape")
        left, right = holders[0], holders[-1]
        pair = frozenset((left, right))
        require(pair in required_pairs and pair not in named_pairs, "wrong named chain endpoints")
        crossings = 0
        for a, b, name in zip(holders, holders[1:], names):
            require(physical_pairs.get(name) == tuple(sorted((a, b))),
                    f"wrong physical name {name} between knots {a} and {b}")
            require(owner.get(a) in pair and owner.get(b) in pair,
                    "named chain leaves its two groups")
            crossings += owner[a] != owner[b]
        require(crossings == 1, "named chain crosses between its groups more than once")
        named_pairs.add(pair)
    require(named_pairs == required_pairs, "named chains omit a required group meeting")
    return len(named_pairs)


def rotation_words(component, rows, neighbors, meetings, certificate):
    rotation = dict(certificate["rotation"])
    require(len(rotation) == len(certificate["rotation"]) and set(rotation) == component,
            "cyclic orders omit or duplicate a holder")
    for holder, order in rotation.items():
        require(set(order) == neighbors[holder] and len(order) == len(neighbors[holder]),
                "cyclic order omits or duplicates a neighboring holder")

    # Count cycles of the successor map on directed pairs of neighboring knots.
    successors = {
        (neighbor, holder): (holder, order[(index + 1) % len(order)])
        for holder, order in rotation.items()
        for index, neighbor in enumerate(order)
    }
    unused = set(successors)
    cycle_count = 0
    while unused:
        start = min(unused)
        current = start
        while current in unused:
            unused.remove(current)
            current = successors[current]
        require(current == start, "the successor map does not consist of cycles")
        cycle_count += 1
    require(cycle_count == certificate["face_count"]
            and len(component) - len(meetings) + cycle_count == 2,
            "cyclic orders fail the recorded embedding count")

    # Use every physical name. Opposite orders across a repeated meeting make
    # the same names cancel as nested pairs even after the equations are joined.
    words = {}
    for holder, order in rotation.items():
        word = []
        for neighbor in order:
            meeting = meetings[tuple(sorted((holder, neighbor)))]
            word.extend(sorted(meeting, reverse=(holder > neighbor)))
        require(sorted(word) == sorted(rows[holder]), "physical word does not match its knot")
        words[holder] = word
    return words


def rotate(word, shift):
    return word[shift:] + word[:shift]


def literal_reduction(words, physical_pairs, odd_holder):
    meetings = defaultdict(list)
    for name, (a, b) in physical_pairs.items():
        meetings[a].append((b, name))
        meetings[b].append((a, name))
    root = min(words)
    reached = {root}
    pending = [root]
    merged = words[root].copy()
    odd = root == odd_holder
    joins = []
    for earlier in pending:
        for holder, name in sorted(meetings[earlier]):
            if holder in reached:
                continue
            reached.add(holder)
            pending.append(holder)
            new = words[holder]
            require(merged.count(name) == new.count(name) == 1, "illegal equation merger")
            shift_left = (merged.index(name) + 1) % len(merged)
            shift_right = new.index(name)
            left = rotate(merged, shift_left)
            right = rotate(new, shift_right)
            require(left[-1] == right[0] == name, "merger does not cancel a repeated factor")
            merged = left[:-1] + right[1:]
            odd ^= holder == odd_holder
            joins.append([holder, name, shift_left, shift_right])
    require(reached == set(words), "equation mergers omit a knot")

    cancellations = []
    while merged:
        for shift in range(len(merged)):
            if len(merged) >= 2 and merged[shift] == merged[(shift + 1) % len(merged)]:
                cancellations.append([shift, merged[shift]])
                merged = rotate(merged, shift)[2:]
                break
        else:
            raise ValueError(f"physical word cannot cancel further: {merged}")
    require(odd, "reduction has even scalar product")
    return {
        "root": root,
        "physical_cyclic_words": words,
        "joins": joins,
        "remaining_cancellations": cancellations,
        "sign_bit": int(odd),
    }


def check_closure(draw, cut, event, component, names, incidence, neighbors):
    holder = event["holder"]
    rows = cut["after_rows"]
    require(holder in component and sorted(component) == event["component_holders"],
            "named holders differ from the actual closing component")
    require(sorted(names) == event["component_names"] and not event["new_names"]
            and event["fresh"] == 0 and event["support"] == rows[holder]
            and event["closing_arity"] == len(rows[holder]),
            "named distinctions or closing row differ from actual closure")
    physical_pairs = {name: tuple(incidence[name]) for name in sorted(names)}
    meetings = defaultdict(list)
    for name, pair in physical_pairs.items():
        require(len(pair) == 2 and set(pair) <= component, "name is not held twice in component")
        meetings[pair].append(name)
    require(len(names) == event["shared_names"] and len(meetings) == event["simple_meetings"],
            "recorded meeting multiplicities differ")
    certificate = event["certificate"]
    kind = certificate["kind"]
    positive = kind in {"five_all_pairs", "six_three_against_three"}
    require(positive == event["operator_positive"], "certificate contradicts archived verdict")

    record = {
        "panel": draw["panel"],
        "draw": draw["draw"],
        "age": cut["age"],
        "odd_holder": holder,
        "certificate": kind,
        "holders": len(component),
        "physical_names": len(names),
        "simple_meetings": len(meetings),
        "repeated_meetings": [
            {"holders": pair, "physical_names": values}
            for pair, values in meetings.items() if len(values) > 1
        ],
    }
    if positive:
        record["verified_named_chains"] = group_certificate(
            component, meetings, physical_pairs, neighbors, certificate
        )
    else:
        require(kind == "planar_rotation", "unknown negative certificate")
        words = rotation_words(component, rows, neighbors, meetings, certificate)
        record["literal_reduction"] = literal_reduction(words, physical_pairs, holder)
    return record, (record, rows, component, meetings, physical_pairs, neighbors, certificate)


def must_reject(label, operation, expected_message):
    try:
        operation()
    except ValueError as exc:
        require(expected_message in str(exc), f"{label} rejected for the wrong reason: {exc}")
        return label
    raise ValueError(f"{label} accepted")


def certificate_controls(positive, negative):
    _, _, component, meetings, pairs, neighbors, original = positive
    paths = original["paths"]
    path = paths[0]
    expected_pair = pairs[path["named_meetings"][0]]
    bad_name = next(name for name in sorted(pairs) if pairs[name] != expected_pair)
    forged_path = {**path, "named_meetings": [bad_name, *path["named_meetings"][1:]]}
    forged = {**original, "paths": [forged_path, *paths[1:]]}
    controls = {
        "rejected": [must_reject(
            "substituted physical name on a positive chain",
            lambda: group_certificate(component, meetings, pairs, neighbors, forged),
            "wrong physical name",
        )]
    }

    record, rows, component, meetings, pairs, neighbors, original = negative
    root, cyclic_order = original["rotation"][0]
    bad_rotation = {**original, "rotation": [
        [root, [cyclic_order[1], cyclic_order[0], *cyclic_order[2:]]],
        *original["rotation"][1:],
    ]}
    controls["rejected"].append(must_reject(
        "swapped local order with every physical name retained",
        lambda: rotation_words(component, rows, neighbors, meetings, bad_rotation),
        "fail the recorded embedding count",
    ))

    # The archive has no repeated negative, so exercise that code separately
    # by adding another physical name at an existing meeting of a known negative.
    left, right = min(meetings)
    extra = max(pairs) + 1
    extended_rows = list(rows)
    extended_rows[left] = [*rows[left], extra]
    extended_rows[right] = [*rows[right], extra]
    extended_meetings = {**meetings, (left, right): [*meetings[left, right], extra]}
    extended_pairs = {**pairs, extra: (left, right)}
    words = rotation_words(component, extended_rows, neighbors, extended_meetings, original)
    reduction = literal_reduction(words, extended_pairs, record["odd_holder"])
    require(sum(word.count(extra) for word in words.values()) == 2
            and any(name == extra for _, name in reduction["remaining_cancellations"]),
            "extra physical name never cancelled")
    controls["repeated_negative"] = {
        "based_on": {key: record[key] for key in ("panel", "draw", "age", "odd_holder")},
        "added_name": extra,
        "holders": (left, right),
        "literal_reduction": reduction,
    }
    return controls


def run(inputs, limit):
    records = []
    examples = {}
    for draw in inputs:
        for cut in draw["laws"]["parity"]["cuts"]:
            incidence = physical_incidence(cut["after_rows"])
            neighbors = {holder: set() for holder in range(len(cut["after_rows"]))}
            for holders in incidence.values():
                if len(holders) == 2:
                    left, right = holders
                    neighbors[left].add(right)
                    neighbors[right].add(left)
            derived = derived_closures(cut, incidence, neighbors)
            events = cut["new_closing_components"]
            require(len(derived) == len(events) and set(derived) == {x["holder"] for x in events},
                    "archived closures differ from the archived full physical cut")
            for event in events:
                if limit is not None and len(records) >= limit:
                    return records, examples
                component, names = derived[event["holder"]]
                record, example = check_closure(
                    draw, cut, event, component, names, incidence, neighbors
                )
                records.append(record)
                examples.setdefault(record["certificate"], example)
    return records, examples


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=Path(ARCHIVE))
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    with gzip.open(args.archive, "rt") as handle:
        inputs = json.load(handle)
    records, examples = run(inputs, args.limit)
    panels = defaultdict(Counter)
    multiplicities = Counter()
    for record in records:
        panels[record["panel"]][record["certificate"]] += 1
        multiplicities[record["physical_names"] - record["simple_meetings"]] += 1
    controls = None
    if {"five_all_pairs", "planar_rotation"} <= examples.keys():
        controls = certificate_controls(examples["five_all_pairs"], examples["planar_rotation"])
    report = {
        "archive": str(args.archive),
        "archive_sha256": sha256(args.archive.read_bytes()).hexdigest(),
        "sample_limit": args.limit,
        "sample_count": len(records),
        "by_panel_and_certificate": panels,
        "excess_physical_name_counts": multiplicities,
        "literal_reductions": sum("literal_reduction" in record for record in records),
        "positive_named_chains": sum(record.get("verified_named_chains", 0) for record in records),
        "controls": controls,
        "samples": records,
    }
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
