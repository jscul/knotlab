"""Recount the frozen Lemma R control from the archived starts and readings."""

import argparse
from collections import Counter, defaultdict
import gzip
from itertools import combinations, islice, permutations, product
import json
from math import comb
from pathlib import Path
from time import perf_counter


DIRECTORY = Path(__file__).resolve().parent.parent


def live_data(stars):
    """Recover loose distinctions and common-neighbour sets from holdings."""
    multiplicities = Counter(distinction for star in stars for distinction in star)
    assert set(multiplicities.values()) <= {1, 2}
    loose = {
        knot: sum(multiplicities[d] == 1 for d in star)
        for knot, star in enumerate(stars)
    }
    live = {knot: count for knot, count in loose.items() if count}
    neighbours = {
        frozenset(knot for knot in live if knot != i and star & stars[knot])
        for i, star in enumerate(stars)
    }
    return loose, live, neighbours


def canonical_keys(live, neighbours):
    """Canonicalize the maximal common-neighbour sets under all relabelings."""
    counts = tuple(sorted(live.values()))
    by_count = [
        tuple(knot for knot in live if live[knot] == count)
        for count in sorted(set(counts))
    ]
    maximal = {block for block in neighbours if not any(block < b for b in neighbours)}
    full = None
    nontrivial = None
    for blocks in product(*(permutations(group) for group in by_count)):
        names = {knot: i for i, knot in enumerate(k for block in blocks for k in block)}
        all_blocks = tuple(sorted(tuple(sorted(names[k] for k in b)) for b in maximal))
        blocks_of_two_or_more = tuple(b for b in all_blocks if len(b) >= 2)
        if full is None or all_blocks < full:
            full = all_blocks
        if nontrivial is None or blocks_of_two_or_more < nontrivial:
            nontrivial = blocks_of_two_or_more
    return (counts, full), (counts, nontrivial)


def join_groups(live, neighbours):
    """Read the maximal valid groups and their uncovered candidate pairs."""
    candidate_pairs = {
        frozenset(pair)
        for neighbours_of_one in neighbours
        for pair in combinations(neighbours_of_one, 2)
    }
    paired_with = {knot: set() for knot in live}
    for left, right in candidate_pairs:
        paired_with[left].add(right)
        paired_with[right].add(left)

    def cliques(members, remaining):
        if len(members) >= 3:
            yield members
        while remaining:
            knot = remaining.pop()
            yield from cliques(members | {knot}, remaining & paired_with[knot])

    valid = [
        group for group in cliques(frozenset(), set(live))
        if not any(group <= b for b in neighbours)
    ]
    groups = [group for group in valid if not any(group < g for g in valid)]
    groups.extend(pair for pair in candidate_pairs if not any(pair <= g for g in groups))
    return groups


def predicted_first_round(stars, live, neighbours):
    """Read the first births from the holdings under the ordinary count."""
    parents = join_groups(live, neighbours)
    demand = Counter(knot for group in parents for knot in group)
    if any(count < demand[knot] for knot, count in live.items()):
        return None
    for knot, count in live.items():
        parents.extend([frozenset([knot])] * (count - demand[knot]))
    next_neighbours = {
        frozenset(i for i, group in enumerate(parents) if knot in group)
        for knot in live
    }
    next_demand = Counter(
        birth for group in join_groups(range(len(parents)), next_neighbours) for birth in group
    )
    sig0, sig1 = Counter(), Counter()
    for birth, group in enumerate(parents):
        count = len(group)
        fresh = max(3 - count, next_demand[birth], 1)
        summary = ("offshoot" if count == 1 else "join", count, fresh, count + fresh)
        parent_signatures = tuple(sorted(("start", 0, 0, len(stars[k])) for k in group))
        sig0[summary] += 1
        sig1[(summary, parent_signatures)] += 1
    return sig0, sig1


def readings(row):
    sig0 = Counter({tuple(signature): count for signature, count in row["sig0"]})
    sig1 = Counter({
        (tuple(signature), tuple(sorted(map(tuple, parents)))): count
        for (signature, parents), count in row["sig1"]
    })
    assert len(sig0) == len(row["sig0"]) and len(sig1) == len(row["sig1"])
    flattened = Counter()
    for (signature, _), count in sig1.items():
        flattened[signature] += count
    assert flattened == sig0 and sum(sig0.values()) == row["n"]
    return sig0, sig1


def read_phase(phase, limit):
    path = DIRECTORY / f"phase{phase}_grown.jsonl.gz"
    cases = []
    first_round_issues = []
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in islice(stream, limit):
            case = json.loads(line)
            case["phase"] = phase
            stars = list(map(set, case["stars"]))
            loose, live, neighbours = live_data(stars)
            assert list(loose.values()) == case["loose"]
            case["keys"] = canonical_keys(live, neighbours)
            case["readings"] = [readings(row) for row in case["rows"]]
            first = predicted_first_round(stars, live, neighbours)
            if first is None:
                issue = case["end"] != "stalls at round 1" or bool(case["rows"])
            elif sum(first[0].values()):
                issue = not case["readings"] or first != case["readings"][0]
            else:
                issue = bool(case["rows"]) or case["kind"] != "closes"
            if issue:
                first_round_issues.append(case_id(case))
            cases.append(case)
    return cases, first_round_issues


def case_id(case):
    return {k: case[k] for k in ("phase", "n knots", "index", "kind")}


def example(case):
    return case_id(case) | {
        "stars": case["stars"],
        "loose": case["loose"],
        "initial places": list(map(len, case["stars"])),
        "round 1": case["rows"][0],
    }


def summarize(groups, key_index, cross_phase=False):
    pair_counts = Counter()
    kinds = Counter()
    horizons = Counter()
    first_differences = {"sig0 from round 1": Counter(), "sig1 from round 1": Counter(),
                         "sig1 from round 2": Counter()}
    round_one_counterexample = None
    different_sizes_counterexample = None
    literal_invariant_difference = []
    for key, cases in groups.items():
        matched = 0
        for left, right in combinations(cases, 2):
            if cross_phase and left["phase"] == right["phase"]:
                continue
            matched += 1
            pair_counts["pairs"] += 1
            kinds[tuple(sorted((left["kind"], right["kind"])))] += 1
            pair_counts["different kinds"] += left["kind"] != right["kind"]
            pair_counts["different numbers of starting knots"] += left["n knots"] != right["n knots"]
            pair_counts["different final recorded rounds"] += len(left["readings"]) != len(right["readings"])
            pair_counts["different recorded endings"] += left["end"] != right["end"]
            if left["keys"][0] != right["keys"][0]:
                pair_counts["extra pairs from omitting singleton blocks"] += 1
                if not literal_invariant_difference:
                    literal_invariant_difference = [case_id(left), case_id(right)]
            rounds = list(zip(left["readings"], right["readings"]))
            horizons[len(rounds)] += 1
            if not rounds:
                pair_counts["zero common recorded rounds"] += 1
                pair_counts["both marked stall at round 1"] += (
                    left["end"] == right["end"] == "stalls at round 1"
                )
                continue

            for label, reading, first_round in [
                ("sig0 from round 1", 0, 1),
                ("sig1 from round 1", 1, 1),
                ("sig1 from round 2", 1, 2),
            ]:
                if len(rounds) < first_round:
                    continue
                pair_counts[f"{label}, compared"] += 1
                differing = next((
                    i for i, (a, b) in enumerate(rounds, 1)
                    if i >= first_round and a[reading] != b[reading]
                ), None)
                if differing is None:
                    pair_counts[f"{label}, equal"] += 1
                else:
                    first_differences[label][differing] += 1
                    if label == "sig1 from round 1" and (
                        round_one_counterexample is None or
                        (different_sizes_counterexample is None and left["n knots"] != right["n knots"])
                    ):
                        witness = {"key": key, "pair": [example(left), example(right)]}
                        if round_one_counterexample is None:
                            round_one_counterexample = witness
                        if different_sizes_counterexample is None and left["n knots"] != right["n knots"]:
                            different_sizes_counterexample = witness
        pair_counts["classes contributing pairs"] += bool(matched)
    result = {
        "invariant": (
            "Loose counts plus all inclusion-maximal live-neighbour sets" if key_index == 0 else
            "Loose counts plus inclusion-maximal live-neighbour sets of size at least two"
        ),
        "counts": dict(pair_counts),
        "first differing rounds": first_differences,
        "pairs by recorded kind": [[pair, count] for pair, count in sorted(kinds.items())],
        "pairs by shared recorded rounds": dict(sorted(horizons.items())),
        "round 1 sig1 counterexample": round_one_counterexample,
        "round 1 sig1 counterexample with different start sizes": different_sizes_counterexample,
        "first extra pair from omitting singleton blocks": literal_invariant_difference or None,
    }
    assert pair_counts["pairs"] == sum(horizons.values()) == sum(kinds.values())
    return result


def audit(cases, cross_phase):
    groupings = [defaultdict(list), defaultdict(list)]
    for case in cases:
        for groups, key in zip(groupings, case["keys"]):
            groups[key].append(case)
    by_phase = Counter(case["phase"] for case in cases)
    possible = (
        by_phase[1] * by_phase[2] if cross_phase else comb(len(cases), 2)
    )
    return {
        "starts": by_phase,
        "marks": dict(Counter(case["kind"] for case in cases)),
        "possible pairs before matching the invariant": possible,
        "comparisons": [
            summarize(groups, key_index, cross_phase) for key_index, groups in enumerate(groupings)
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="Read only this many archive rows from each phase.")
    parser.add_argument("--output", required=True, type=Path)
    options = parser.parse_args()
    begin = perf_counter()
    phases = {}
    issues = {}
    for phase in (1, 2):
        phases[phase], issues[phase] = read_phase(phase, options.limit)
    parsed = perf_counter()
    out = {
        "prefix limit per phase": options.limit,
        "exceptions to independent first-round reconstruction": issues,
        "phase 1": audit(phases[1], False),
        "phase 2": audit(phases[2], False),
        "across phases, through each pair's last shared round": audit(phases[1] + phases[2], True),
        "seconds": {"read and reconstruct": parsed - begin, "compare": perf_counter() - parsed},
    }
    options.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
