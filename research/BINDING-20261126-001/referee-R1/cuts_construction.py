"""Check all carriers on the proposed preparations and trace their meanings across growth."""

import argparse
from collections import Counter, deque
import json
from pathlib import Path
import resource
from time import perf_counter

from cuts_reader import Incidence, bits, inspect, kernel, mask, normal, simple, span
from replay_growth import ARMS, grow


HERE = Path(__file__).resolve().parent


def values(parities, allowed):
    basis = []
    for state in allowed:
        value = sum(((state & label).bit_count() % 2) << i for i, label in enumerate(parities))
        basis.append(value)
    image = {0}
    for value in basis:
        image |= {before ^ value for before in image}
    return sorted(image)


def through_distinctions(stage, labels):
    """Check literal shortest return lengths, allowing each of eight label changes."""
    adjacency = [[] for _ in range(len(stage.supports) + 1)]
    signs = {}
    for name, owners in stage.owners.items():
        a, b = owners if len(owners) == 2 else (*owners, len(stage.supports))
        code = sum(((label >> name) & 1) << i for i, label in enumerate(labels))
        signs[name] = code
        adjacency[a].append((b, name, code))
        adjacency[b].append((a, name, code))
    changed = [0] * len(labels)
    participating = 0
    for d, owners in stage.owners.items():
        a, b = owners if len(owners) == 2 else (*owners, len(stage.supports))
        seen = {(a, 0)}
        pending = deque([(a, 0, 0)])
        shortest = None
        discovered = set()
        while pending:
            knot, parity, length = pending.popleft()
            if shortest is not None and length > shortest:
                break
            if knot == b:
                shortest = length
                discovered.add(parity ^ signs[d])
            elif shortest is None:
                for other, via, value in adjacency[knot]:
                    candidate = (other, parity ^ value)
                    if via != d and candidate not in seen:
                        seen.add(candidate)
                        pending.append((*candidate, length + 1))
        if discovered:
            participating += 1
            for i in range(len(labels)):
                changed[i] += int(any((value >> i) & 1 for value in discovered))
    return {"distinctions with any shortest change": participating,
            "distinctions admitting a shortest change of each ring parity": changed}


def joint(stage, labels):
    permitted = list(kernel(stage.checks, stage.owners))
    local_sizes = Counter()
    for row in stage.supports:
        restricted = kernel([*stage.checks, *(1 << d for d in row)], stage.owners)
        local_sizes[len(values(labels, restricted))] += 1
    moves = stage.projected_moves(stage.all_names)
    changes = [any((m & f).bit_count() % 2 for m in moves) for f in labels]
    direct = through_distinctions(stage, labels)
    assert [n > 0 for n in direct["distinctions admitting a shortest change of each ring parity"]] == changes
    return {"joint values": [f"{w:03b}"[::-1] for w in values(labels, permitted)],
            "numbers of listed supports by count of reachable joint values when fixed": local_sizes,
            "all three are simple cycles": all(not (c & stage.loose) and simple(stage, c) for c in labels),
            "class dimension of stage": len(permitted) - len(moves), **direct}


def born(stage, following, labels):
    next_labels = [0, 0, 0]
    used = [0, 0, 0]
    for row in following.checks[len(stage.checks):]:
        inputs = row & stage.all_names
        fresh = row & ~stage.all_names
        for i, f in enumerate(labels):
            if inputs and inputs & f == inputs:
                next_labels[i] |= fresh
                used[i] |= inputs
    assert used == list(labels)
    assert all(not normal(old ^ new, following.laws) for old, new in zip(labels, next_labels))
    return next_labels


def run(pilot):
    t = perf_counter()
    source_file = json.loads((HERE / "construct_born.json").read_text())["preparations"]
    output = {}
    for index, (preparation, case) in enumerate(source_file.items()):
        if pilot and index:
            break
        initial = Incidence(tuple(map(tuple, case["source supports"])))
        initial_labels = [mask(d for d, own in initial.owners.items() if len(own) == 1 and lo <= own[0] < lo + 5)
                          for lo in (0, 5, 10)]
        by_arm = {}
        for arm in ARMS:
            prior = None
            stage = initial
            labels = [initial_labels]
            records = []
            finish = "studied through round limit"
            for age in range(2 if pilot else 4):
                profile = inspect(stage, prior, initial, include_carriers=True)
                record = {"round": age, "generic cycle search": profile, "ring readings by date of distinction": []}
                for since, family in enumerate(labels):
                    reading = joint(stage, family)
                    reading["created in round"] = since
                    reading["all three equal their respective source representatives"] = all(
                        not normal(new ^ old, stage.laws) for new, old in zip(family, initial_labels))
                    record["ring readings by date of distinction"].append(reading)
                generic = {tuple(c) for c in profile["all listed supports"]["all candidate supports"]}
                expected = {tuple(bits(c)) for family in labels[:-1] for c in family}
                record["generic unread candidates are exactly the older three ring supports per round"] = (
                    generic == expected)
                records.append(record)
                if age == (1 if pilot else 3):
                    break
                next_rows, stop = grow(stage.supports, arm)
                if stop != "funded":
                    finish = f"{stop} at round {age + 1}"
                    break
                following = Incidence(next_rows)
                next_labels = born(stage, following, labels[-1])
                if arm == "ordinary":
                    batch = case[("first ordinary births", "second ordinary births", "third ordinary births")[age]]
                    assert list(next_rows[len(stage.supports):]) == [
                        tuple(row["inputs"] + row["fresh"]) for row in batch]
                    if age in (0, 1):
                        saved = case[("ring-wise supports born in the first round",
                                      "ring-wise supports born in the second round")[age]]
                        assert next_labels == list(map(mask, saved))
                prior, stage = stage, following
                labels.append(next_labels)
            by_arm[arm] = {"stages": records, "finish": finish}
        output[preparation] = by_arm
    return {"pilot": pilot, "scope": "The first three groups of five specified knots and all simple cycles on the full stage. Starts were supplied by the construction. All growth and readings were independently reconstructed.",
            "value tuples are in the order of the three rings": True, "preparations": output,
            "seconds": perf_counter() - t}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024 ** 3, 2 * 1024 ** 3))
    result = run(args.pilot)
    filename = "cuts_construction_pilot.json" if args.pilot else "cuts_construction.json"
    (HERE / filename).write_text(json.dumps(result, indent=2) + "\n")
    print(filename, result["seconds"])
