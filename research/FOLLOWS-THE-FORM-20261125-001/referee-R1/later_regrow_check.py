"""Regrow complete later studies and selected five-knot swap pairs."""

from argparse import ArgumentParser
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from gzip import open as open_gzip
from itertools import combinations, permutations
from math import comb
from pathlib import Path
import json
import resource
import time

from growth_engine import build_start, grow


EPIC = Path(__file__).resolve().parent.parent
ARCHIVE = EPIC / "checks" / "what_decides_the_class"
SEEDS = EPIC.with_name(EPIC.name + "A") / "seeds.json"

# O is a ring of four, C a ring of three, D a chain of three held at an end,
# and K a single knot. Include the three count-profile positives, a contrasting
# control, and the two waiting studies with a two-step exception and no take.
STUDIES = {
    "retire-count": ("CAP-3", "CANCEL-RETIRE", None, "O"),
    "ordinary-count": ("ORD", "CANCEL-RETIRE", None, "O"),
    "take-count": ("CAP-3", "CANCEL-RETIRE", "MET-SOLE", "C"),
    "retire-control": ("FLOOR1", "CANCEL-RETIRE", None, "K"),
    "wait-reach": ("CAP-3", "CANCEL-WAIT", None, "C"),
    "wait-reach-chain": ("CAP-3", "CANCEL-WAIT", None, "D"),
}

# M is a three-knot chain held at an end, L a two-knot first seed.
# Indices identify adjacent pairs in the archive and are zero-based.
SWAPS = {
    "floor-positive": (("FLOOR1", "CANCEL-WAIT", None, "O"), (0, 3)),
    "cap-positive": (("CAP-3", "CANCEL-WAIT", None, "M"), (20,)),
    "take-positive": (("ORD", "CANCEL-WAIT", "MET-SOLE", "L"), (2, 5)),
    "floor-control": (("FLOOR1", "CANCEL-RETIRE", None, "O"), (0, 3)),
    "cap-control": (("CAP-3", "CANCEL-RETIRE", None, "M"), (20,)),
    "take-control": (("ORD", "CANCEL-WAIT", None, "L"), (2, 5)),
}

DOCUMENTED_PAIR = ("path:1,1,2,2@0", "path:1,2,1,2@0")


@dataclass(frozen=True, slots=True)
class Replay:
    rounds: int
    own: tuple
    wider: tuple
    second: tuple
    both: tuple


def archive_study(filename, law):
    fields = ("ration", "treatment", "take", "first")
    with open_gzip(ARCHIVE / f"{filename}.jsonl.gz", "rt") as source:
        for line in source:
            row = json.loads(line)
            if tuple(row["spec"][field] for field in fields) == law:
                return row
    raise ValueError(f"study is absent from {filename}: {law}")


def decode_seed(name):
    """Use loose counts and held-knot placement encoded in the later archive."""
    kind, label = name.split(":")
    if kind == "row5":
        counts = tuple(map(int, label.replace("[", "").replace("]", "").split(",")))
        held = 2
        kind = "path"
    else:
        plain, at = label.split("@")
        counts = tuple(map(int, plain.replace(";", ",").split(",")))
        held = {"centre": 0, "arm": 1}.get(at, at)
        held = int(held)
    if kind == "star3":
        partners = [(0, arm) for arm in range(1, 4)]
    else:
        if kind not in {"path", "ring"}:
            raise ValueError(f"unrecognized seed name: {name}")
        partners = list(zip(range(len(counts) - 1), range(1, len(counts))))
        if kind == "ring":
            partners.append((len(counts) - 1, 0))
    knots = [[] for _ in counts]
    for distinction, (left, right) in enumerate(partners):
        knots[left].append(distinction)
        knots[right].append(distinction)
    next_distinction = len(partners)
    for knot, count in zip(knots, counts):
        knot.extend(range(next_distinction, next_distinction + count))
        next_distinction += count
    return {"name": name, "knots": knots, "at": held}


def seed_properties(seed):
    knots = [frozenset(knot) for knot in seed["knots"]]
    held = seed["at"]
    holders = Counter(distinction for knot in knots for distinction in knot)
    if set(holders) != set(range(len(holders))) or (
        max(holders.values()) > 2
        or any(len(knot) + (index == held) < 3 for index, knot in enumerate(knots))
        or any(len(knot & other) > 1 for knot, other in combinations(knots, 2))
    ):
        raise ValueError(f"invalid later seed: {seed['name']}")
    partners = [
        frozenset(index for index, other in enumerate(knots) if index != own and knot & other)
        for own, knot in enumerate(knots)
    ]
    steps = {held: 0}
    pending = deque([held])
    while pending:
        current = pending.popleft()
        for partner in partners[current] - steps.keys():
            steps[partner] = steps[current] + 1
            pending.append(partner)
    if len(steps) != len(knots):
        raise ValueError(f"later seed is disconnected: {seed['name']}")
    tags = [
        (steps[index], sum(holders[x] == 1 for x in knot), len(partners[index]))
        for index, knot in enumerate(knots)
    ]
    held_knot = (len(knots[held]) + 1, *tags[held][1:])
    return held, held_knot, tags, partners


def rooted_pattern(properties, stop):
    held, _, tags, partners = properties
    other = [knot for knot, tag in enumerate(tags) if knot != held and tag[0] <= stop]

    def arranged(order):
        return (
            tuple(tags[knot] for knot in order),
            tuple(right in partners[left] for left, right in combinations(order, 2)),
        )

    return min(arranged((held, *order)) for order in permutations(other))


def by_steps(properties, stop):
    return tuple(sorted(tag for tag in properties[2] if tag[0] <= stop))


def load_cases(archive, seeds, swap_indices):
    names = archive["names"]
    if len(names) != (54 if swap_indices else 345) or len(names) != len(set(names)):
        raise ValueError("unexpected later seed roster")
    explicit = {seed["name"]: seed for family in seeds["second"].values() for seed in family}
    if swap_indices:
        for pair_index in swap_indices:
            left_name, right_name = names[2 * pair_index:2 * pair_index + 2]
            left, right = decode_seed(left_name), decode_seed(right_name)
            left_props, right_props = seed_properties(left), seed_properties(right)
            left_numbers = [tag[1] for tag in left_props[2]]
            right_numbers = [tag[1] for tag in right_props[2]]
            if (
                left_props[:2] != right_props[:2]
                or by_steps(left_props, 4) != by_steps(right_props, 4)
                or rooted_pattern(left_props, 4) == rooted_pattern(right_props, 4)
                or left_numbers != [right_numbers[-1], *right_numbers[1:-1], right_numbers[0]]
            ):
                raise ValueError(f"not a five-knot end swap: {left_name}, {right_name}")
        names = [name for pair in swap_indices for name in names[2 * pair:2 * pair + 2]]
    cases = {name: explicit[name] if name in explicit else decode_seed(name) for name in names}
    properties = {name: seed_properties(seed) for name, seed in cases.items()}
    if not swap_indices and len({rooted_pattern(props, 4) for props in properties.values()}) != 345:
        raise ValueError("full later roster includes repeated forms")
    return cases, properties


def regrow(first, seed, law, rounds):
    ration, treatment, take, _ = law
    run = grow(
        *build_start(first, seed), ration=ration, treatment=treatment, take=take,
        max_rounds=rounds, knot_limit=3000,
    )
    wider = normalize(run.wider)
    both = tuple(
        tuple((entry[:5], count) for entry, count in one_round if not entry[5])
        for one_round in wider
    )
    return Replay(len(run.rounds), normalize(run.own), wider, normalize(run.second_only), both)


def partition(signatures):
    groups = defaultdict(list)
    for index, signature in enumerate(signatures):
        groups[signature].append(index)
    return {tuple(members) for members in groups.values()}


def pair_count(counts):
    return sum(comb(amount, 2) for amount in counts.values())


def tally(profiles, own_signatures):
    counts = Counter(profiles)
    same = pair_count(counts)
    return {
        "values": len(counts),
        "pairs sharing it": same,
        "of those told apart": same - pair_count(Counter(zip(profiles, own_signatures))),
    }


def first_difference(left, right):
    return next((step for step, (a, b) in enumerate(zip(left, right), 1) if a != b), None)


def normalize(profiles):
    return tuple(tuple(sorted(one_round.items())) for one_round in profiles)


def total_births(one_round):
    return sum(count for _, count in one_round)


def profile_tallies(archive, cases, properties, own, second, mixed):
    names = tuple(cases)
    held = [properties[name][1] for name in names]
    registered = list(zip(held, (tuple(map(total_births, births)) for births in second)))
    by_knot = [
        (hold, tuple(sorted(tag[1:] for tag in properties[name][2])))
        for name, hold in zip(names, held)
    ]
    profiles = [
        held, registered, list(zip(held, second)), list(zip(held, second, mixed)),
        list(zip(held, (tuple(map(total_births, births)) for births in mixed))),
        list(zip(held, mixed)), mixed, by_knot,
    ]
    families = [
        "counts 0:", "counts 1:", "counts 2:", "counts 3:",
        "shared 1:", "shared 2:", "shared 3:", "knots:",
        "reach 0:", "reach 1:", "reach 2:", "reach 3:", "reach all:",
        "layers 1:", "layers 2:", "layers all:",
    ]
    profiles.extend([rooted_pattern(properties[name], limit) for name in names] for limit in range(5))
    profiles.extend([by_steps(properties[name], limit) for name in names] for limit in (1, 2, 4))
    pairs_by_first_round = defaultdict(Counter)
    results = {}
    for family, values in zip(families, profiles, strict=True):
        reference = next(key for key in archive["profiles"] if key.startswith(family))
        counts = tally(values, own)
        results[family.rstrip(":")] = {"regrown": counts, "recorded": archive["profiles"][reference]}
        if family in {"counts 1:", "knots:", "reach 2:", "reach 3:"}:
            grouped = defaultdict(list)
            for index, value in enumerate(values):
                grouped[value].append(index)
            for members in grouped.values():
                for left, right in combinations(members, 2):
                    step = first_difference(own[left], own[right])
                    pairs_by_first_round[family.rstrip(":")][step if step is not None else "same through common round"] += 1
    return results, pairs_by_first_round


def full_study(archive, first, cases, properties, law):
    rounds = archive["spec"]["rounds"]
    bare = regrow(first, None, law, rounds)
    raw_runs = {name: regrow(first, seed, law, rounds) for name, seed in cases.items()}
    common_round = min(bare.rounds, *(run.rounds for run in raw_runs.values()))
    own = [run.own for run in raw_runs.values()]
    second = [run.second[:common_round] for run in raw_runs.values()]
    mixed = [run.both[:common_round] for run in raw_runs.values()]
    class_by_round = [
        partition(births[:step] for births in own)
        for step in range(1, common_round + 1)
    ]
    recorded_partitions = [partition(labels) for labels in archive["class by round"]]
    total_pairs = comb(len(cases), 2)
    profiles, first_rounds = profile_tallies(
        archive, cases, properties, [births[:common_round] for births in own], second, mixed,
    )
    result = {
        "law": archive["spec"],
        "second seeds": len(cases),
        "bare rounds": bare.rounds,
        "completed rounds for second seeds": dict(Counter(run.rounds for run in raw_runs.values())),
        "common round": {"regrown": common_round, "recorded": archive["R*"]},
        "class counts by round": [len(groups) for groups in class_by_round],
        "partitions match for every common round": class_by_round == recorded_partitions,
        "partitions match by round": [
            actual == expected for actual, expected in zip(class_by_round, recorded_partitions)
        ],
        "class counts": {"regrown": len(class_by_round[-1]), "recorded": archive["classes"]},
        "pairs told apart": {
            "regrown": total_pairs - sum(comb(len(group), 2) for group in class_by_round[-1]),
            "recorded": archive["pairs told apart"],
        },
        "profiles": profiles,
        "first differences by round for equal profiles": first_rounds,
    }
    if law == STUDIES["retire-control"]:
        result["documented pair"] = [
            {
                "name": name,
                "round 1 first-only births": raw_runs[name].own[0],
                "round 1 births of both": raw_runs[name].both[0],
            }
            for name in DOCUMENTED_PAIR
        ]
    return result


def selected_swaps(archive, first, cases, properties, law):
    names = tuple(cases)
    columns = {name: index for index, name in enumerate(archive["names"])}
    runs = {
        name: regrow(first, seed, law, archive["spec"]["rounds"])
        for name, seed in cases.items()
    }
    results = []
    for left_name, right_name in zip(names[::2], names[1::2]):
        left, right = runs[left_name], runs[right_name]
        shared_round = min(left.rounds, right.rounds)
        difference = first_difference(left.own, right.own)
        left_col, right_col = columns[left_name], columns[right_name]
        recorded_round = archive["R*"]
        comparisons = [
            {
                "round": step,
                "same regrown": left.own[:step] == right.own[:step],
                "same recorded": labels[left_col] == labels[right_col],
            }
            for step, labels in enumerate(archive["class by round"], 1)
            if step <= shared_round
        ]
        results.append({
            "names": [left_name, right_name],
            "knot counts by steps": by_steps(properties[left_name], 4),
            "rounds completed": [left.rounds, right.rounds],
            "recorded study's common round": recorded_round,
            "first difference through pair's rounds": difference,
            "first difference through recorded common round": next(
                (row["round"] for row in comparisons if not row["same recorded"]), None,
            ),
            "comparisons through every recorded common round": comparisons,
            "first difference birth entries": (
                [left.own[difference - 1], right.own[difference - 1]] if difference is not None else None
            ),
            "same wider record of round 1": left.wider[0] == right.wider[0],
        })
    return {"law": archive["spec"], "pairs": results}


def pilot(archive, first, cases, law, swap_indices):
    if swap_indices:
        chosen = list(cases)[:2]
        later_growths = len(cases)
    else:
        names = tuple(cases)
        most_places = max(names, key=lambda name: sum(map(len, cases[name]["knots"])))
        chosen = [None, names[0], names[120], names[240], most_places]
        later_growths = 1 + len(cases)
    samples = []
    for name in chosen:
        started = time.monotonic()
        run = regrow(first, cases[name] if name is not None else None, law, archive["spec"]["rounds"])
        samples.append({
            "name": name,
            "rounds": run.rounds,
            "seconds": time.monotonic() - started,
            "births with either seed as ancestor": sum(map(total_births, run.wider)) + sum(map(total_births, run.second)),
        })
    return {
        "law": archive["spec"],
        "samples": samples,
        "full cases": later_growths,
        "projected seconds using slowest pilot case": max(s["seconds"] for s in samples) * later_growths,
    }


def run_case(case, pilot_only):
    if case in STUDIES:
        law = STUDIES[case]
        swap_indices = ()
        archive = archive_study("every_seed", law)
    else:
        law, swap_indices = SWAPS[case]
        archive = archive_study("swap_family", law)
    seeds = json.loads(SEEDS.read_text())
    first = seeds["first"][law[-1]]
    started = time.monotonic()
    cases, properties = load_cases(archive, seeds, swap_indices)
    if pilot_only:
        result = pilot(archive, first, cases, law, swap_indices)
    elif swap_indices:
        result = selected_swaps(archive, first, cases, properties, law)
    else:
        result = full_study(archive, first, cases, properties, law)
    result["execution seconds"] = time.monotonic() - started
    result["peak resident memory KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if pilot_only:
        return result, True
    if swap_indices:
        for pair in result["pairs"]:
            comparisons = pair["comparisons through every recorded common round"]
            if len(comparisons) != archive["R*"] or any(
                row["same regrown"] != row["same recorded"] for row in comparisons
            ):
                return result, False
        return result, True
    matches = (
        result["partitions match for every common round"]
        and all(result[key]["regrown"] == result[key]["recorded"] for key in ("common round", "class counts", "pairs told apart"))
        and all(row["regrown"] == row["recorded"] for row in result["profiles"].values())
    )
    return result, matches


def main():
    cases = tuple(STUDIES) + tuple(SWAPS)
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=(*cases, "all"))
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    cap = 2 * 1024**3
    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    if args.case == "all":
        if args.pilot:
            parser.error("all includes a pilot before each replay")
        results = {}
        matches = True
        for case in cases:
            timing, _ = run_case(case, True)
            replay, agrees = run_case(case, False)
            results[case] = {"pilot": timing, "replay": replay}
            matches &= agrees
    else:
        results, matches = run_case(args.case, args.pilot)
    print(json.dumps(results, indent=2))
    if not matches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
