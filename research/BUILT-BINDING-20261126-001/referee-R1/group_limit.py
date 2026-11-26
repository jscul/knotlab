"""Check how limiting parent groups to three affects the source of class facts.

Reads no analysis implementation. A knot law is one even-parity row. Counts of
fresh distinctions use parity implication on the preceding stage, computed by
row reduction. The comparison with the frozen files takes place after growth.
Run from the repository root with .venv/bin/python -B and this filename.
"""

import argparse
import json
import resource
import time
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


HERE = Path(__file__).resolve().parent
MAX_BITS = 700
MAX_BIRTHS = 100
LIMIT_BYTES = 3 * 2**29
OUT = -1


def insert(basis, value):
    while value:
        key = value.bit_length() - 1
        if key not in basis:
            basis[key] = value
            return True
        value ^= basis[key]
    return False


def vanishes_on_states(laws, mask):
    while mask:
        row = laws.get(mask.bit_length() - 1)
        if row is None:
            return False
        mask ^= row
    return True


def row(bits):
    return sum(1 << b for b in bits)


def census(values):
    return dict(sorted(Counter(values).items()))


def construction(name):
    if name.startswith("one knot"):
        arity = 3 if name.endswith("three") else 4
        return [tuple(range(arity))]
    rosters = []
    next_bit = 0

    def add(*owners):
        nonlocal next_bit
        for owner in owners:
            rosters[owner].append(next_bit)
        next_bit += 1

    if name.startswith("three rings"):
        rosters = [[] for _ in range(18)]
        for index in range(12):
            add(index, index // 4 * 4 + (index + 1) % 4)
            add(index)
            add(index)
        partners_seen = [0, 0, 0]
        for p, (i, j) in enumerate(combinations(range(3), 2)):
            left, right = 12 + 2 * p, 13 + 2 * p
            for ring, attaching in [(i, left), (j, right)]:
                home = 4 * ring + 2 * partners_seen[ring]
                add(home, attaching)
                add(home, attaching)
                partners_seen[ring] += 1
            add(left, right)
            add(left, right)
    elif name.startswith("four live with triple neighbours"):
        rosters = [[] for _ in range(8)]
        for omitted in range(4):
            for live in set(range(4)) - {omitted}:
                add(live, 4 + omitted)
        loose = 1 if name.endswith("one loose each") else 3
        for live in range(4):
            for _ in range(loose):
                add(live)
    else:
        pairs = list(combinations(range(4), 2))
        if name == "two overlapping groups of three":
            pairs.remove((2, 3))
        rosters = [[] for _ in range(4 + len(pairs))]
        for joining, (i, j) in enumerate(pairs, 4):
            for live in (i, j):
                add(live, joining)
                add(live, joining)
        for live in range(4):
            for _ in range(3):
                add(live)
    assert all(len(bits) >= 3 for bits in rosters)
    return [tuple(bits) for bits in rosters]


def holders_and_neighbours(knots):
    owners = defaultdict(list)
    for knot, bits in enumerate(knots):
        for bit in bits:
            owners[bit].append(knot)
    neighbours = [set() for _ in knots]
    for owners_of_bit in owners.values():
        if len(owners_of_bit) == 2:
            u, v = owners_of_bit
            neighbours[u].add(v)
            neighbours[v].add(u)
        else:
            assert len(owners_of_bit) == 1
    return owners, neighbours


def maximal_sets(candidates):
    def visit(chosen, possible, used):
        if not possible and not used:
            yield chosen
            return
        pivot = max(possible | used, key=lambda u: len(possible & candidates[u]))
        for u in sorted(possible - candidates[pivot]):
            yield from visit(chosen | {u}, possible & candidates[u], used & candidates[u])
            possible.remove(u)
            used.add(u)

    yield from visit(set(), set(candidates), set())


def select_groups(neighbours, live, capped):
    """Valid triples when capped, maximal valid sets otherwise, then leftover pairs."""
    candidates = {u: set() for u in live}
    pairs = []
    for u, v in combinations(live, 2):
        if neighbours[u] & neighbours[v]:
            candidates[u].add(v)
            candidates[v].add(u)
            pairs.append((u, v))
    if capped:
        larger = [(u, v, w) for u, v in pairs
                  for w in candidates[u] & candidates[v] if w > v]
    else:
        larger = [tuple(sorted(group)) for group in maximal_sets(candidates) if len(group) >= 3]
    selected = sorted(group for group in larger
                      if not set.intersection(*(neighbours[u] for u in group)))
    covered = {pair for group in selected for pair in combinations(group, 2)}
    return selected + [pair for pair in pairs if pair not in covered]


def next_round(knots, capped):
    owners, neighbours = holders_and_neighbours(knots)
    loose = {u: sorted(b for b in bits if len(owners[b]) == 1) for u, bits in enumerate(knots)}
    live = sorted(u for u in loose if loose[u])
    if not live:
        return None, {"stop": "closed"}
    groups = select_groups(neighbours, live, capped)
    uses = Counter(u for group in groups for u in group)
    shortages = {u: [len(loose[u]), uses[u]] for u in live if len(loose[u]) < uses[u]}
    if shortages:
        return None, {"stop": "stall", "held and required": shortages}
    groups.extend((u,) for u in live for _ in range(len(loose[u]) - uses[u]))
    if len(groups) > MAX_BIRTHS:
        return None, {"stop": "birth limit before lookahead", "births": len(groups)}
    taken = Counter()
    inputs = []
    for group in groups:
        inputs.append(tuple(loose[u][taken[u]] for u in group))
        taken.update(group)
    trial_knots = knots + inputs
    newborn = list(range(len(knots), len(trial_knots)))
    _, trial_neighbours = holders_and_neighbours(trial_knots)
    demand = Counter(u for group in select_groups(trial_neighbours, newborn, capped) for u in group)
    laws = {}
    for bits in knots:
        insert(laws, row(bits))
    fresh = [0 if vanishes_on_states(laws, row(trial_knots[u])) else
             max(1, 3 - len(trial_knots[u]), demand[u]) for u in newborn]
    nbits = len(owners)
    if nbits + sum(fresh) > MAX_BITS:
        return None, {"stop": "distinction limit", "distinctions": nbits + sum(fresh)}
    for u, count in zip(newborn, fresh):
        trial_knots[u] += tuple(range(nbits, nbits + count))
        nbits += count

    # Re-read parents and candidate pairs from the actual old and grown incidences.
    after_owners, _ = holders_and_neighbours(trial_knots)
    old_bits_spent = Counter(b for u in newborn for b in trial_knots[u] if b in owners)
    assert old_bits_spent == Counter(b for bits in loose.values() for b in bits)
    actual_parents = [tuple(owners[b][0] for b in trial_knots[u] if b in owners) for u in newborn]
    assert all(len(p) == len(set(p)) for p in actual_parents)
    pair_counts = Counter(pair for parents in actual_parents for pair in combinations(sorted(parents), 2))
    expected = {pair for common in range(len(knots)) for pair in combinations(
        sorted(u for u in live if common in neighbours[u]), 2)}
    assert set(pair_counts) == expected
    zero = [u for u, count in zip(newborn, fresh) if count == 0]
    for u in zero:
        # Every hand-built start in this check is connected.
        assert len(newborn) == 1
        assert all(len(loose[owners[b][0]]) == 1 for b in trial_knots[u])
    assert all(len(after_owners[b]) == 2 for b in old_bits_spent)
    detail = {
        "birth sizes by parent count": census(map(len, actual_parents)),
        "fresh distinctions by birth": census(fresh),
        "common-neighbour pairs by number of common children": census(pair_counts.values()),
        "zero-fresh births": len(zero),
        "knots": len(trial_knots),
        "distinctions": nbits,
    }
    if len(live) == 4 and (max(map(len, actual_parents)) >= 3 or len(expected) == 6):
        detail["multiple-parent births"] = [list(p) for p in actual_parents if len(p) >= 2]
    return trial_knots, detail


def origin_ranks(knots, source_bits):
    """Certify both readings directly if legal changes span every source-preserving change."""
    owners, _ = holders_and_neighbours(knots)
    basis = {}
    for bits in knots:
        insert(basis, row(bits) >> source_bits)
    dimension = len(owners) - source_bits - len(basis)
    same_holders = defaultdict(list)
    incidence = {}
    for b, holders in owners.items():
        u, v = holders if len(holders) == 2 else (OUT, holders[0])
        same_holders[min(u, v), max(u, v)].append(b)
        incidence[b] = row(holders)
    neighbours = defaultdict(set)
    new_neighbours = defaultdict(set)
    fresh_links = {}
    for (u, v), labels in same_holders.items():
        neighbours[u].add(v)
        neighbours[v].add(u)
        new = sorted(b for b in labels if b >= source_bits)
        if new:
            fresh_links[u, v] = new
            new_neighbours[u].add(v)
            new_neighbours[v].add(u)

    short = {}
    upto_five = {}
    examined = Counter()
    example = None

    def inspect(bits, lengths):
        nonlocal example
        toggled = 0
        for b in bits:
            toggled ^= incidence[b]
        assert toggled == 0 and all(b >= source_bits for b in bits)
        change = row(bits)
        insert(upto_five, change)
        if len(bits) in lengths:
            insert(short, change)
        examined[len(bits)] += 1
        if max(lengths) == 4 and min(lengths) < 4 and example is None:
            example = {"distinctions": bits, "shortest lengths in that order": lengths,
                       "holders in the same order": [owners[b] for b in bits]}

    for labels in fresh_links.values():
        for b in labels[1:]:
            inspect([labels[0], b], [2, 2])
    two_steps = defaultdict(list)
    for via, partners in new_neighbours.items():
        for endpoints in combinations(sorted(partners), 2):
            two_steps[endpoints].append(via)
    for (u, v), via in two_steps.items():
        for mid in via[1:]:
            ring = (u, via[0], v, mid, u)
            pairs = [tuple(sorted(pair)) for pair in zip(ring, ring[1:])]
            bits = [fresh_links[pair][0] for pair in pairs]
            # Each link is on this loop of four. A second distinction with the
            # same holders gives length two, another common neighbour gives three.
            lengths = [2 if len(same_holders[a, b]) > 1 else
                       3 if neighbours[a] & neighbours[b] else 4 for a, b in pairs]
            inspect(bits, lengths)
    # One fixed representative per pair of holders suffices modulo the pairs.
    # For fixed opposite holders, differences against the first two-step route
    # span all pairwise differences of such routes. The two ranks are exact.
    assert len(short) == len(upto_five) == dimension
    return {
        "dimension of changes fixing the start": dimension,
        "rank certified by shortest changes": len(short),
        "rank certified by changes of at most five": len(upto_five),
        "origin gap under each reading": [0, 0],
        "generators tested by size": dict(examined),
        "four-change shortest through only some distinctions": example,
    }


CASES = {
    "one knot with three": 8,
    "one knot with four": 10,
    "four live with triple neighbours and one loose each": 4,
    "four live with triple neighbours and three loose each": 8,
    "four live with distinct pair neighbours": 8,
    "two overlapping groups of three": 8,
    "three rings of four with paired attachments and double links": 7,
}


def trajectory(name, capped, bound):
    knots = construction(name)
    source = len(holders_and_neighbours(knots)[0])
    stages = []
    for number in range(1, bound + 1):
        grown, detail = next_round(knots, capped)
        if grown is None:
            return {"start distinctions": source, "reached": stages, "end": detail}
        detail.update(origin_ranks(grown, source))
        detail["round"] = number
        stages.append(detail)
        knots = grown
    return {"start distinctions": source, "reached": stages, "end": {"stop": "round limit"}}


def frozen_comparison(runs):
    name = "3 rings of 4, paired, double"
    replay = runs["three rings of four with paired attachments and double links"]["ordinary"]["reached"]
    counts = []
    with (HERE.parent / "frozen_built.jsonl").open() as f:
        for line in f:
            entry = json.loads(line).get("new carriers", {})
            if entry.get("family") == name:
                counts = [(a["round"], a["distinctions"]) for a in entry["rounds"]]
                break
    ranks = []
    with (HERE.parent / "frozen_premises_built.jsonl").open() as f:
        for line in f:
            entry = json.loads(line)
            if entry["start"] == name:
                ranks = [(a["round"], a["span"]["dim Z_new"]) for a in entry["rounds"] if "span" in a]
                break
    assert counts and ranks
    assert all(replay[t - 1]["distinctions"] == n for t, n in counts)
    assert all(replay[t - 1]["dimension of changes fixing the start"] == n for t, n in ranks)
    return {"family": name, "matched distinction counts": counts, "matched dimensions fixing the start": ranks}


def literal_small_changes():
    """Test all changes through length five without using holder paths."""
    knots = construction("one knot with four")
    for _ in range(2):
        knots, _detail = next_round(knots, capped=False)
    laws = [row(bits) for bits in knots]
    n = max(b for bits in knots for b in bits) + 1
    minimum = {}
    moves = []
    tested = 0
    for length in range(1, 6):
        for support in combinations(range(n), length):
            mask = row(support)
            tested += 1
            if any((mask & law).bit_count() % 2 for law in laws):
                continue
            moves.append((support, mask))
            for bit in support:
                minimum.setdefault(bit, (length, support))
    assert len(minimum) == n
    quantities = {}
    for rule in ("shortest", "at most five"):
        allowed = []
        for support, mask in moves:
            if rule == "at most five" or any(len(support) == minimum[b][0] for b in support):
                allowed.append(mask)
        basis, old_projection = {}, {}
        for mask in allowed:
            insert(basis, mask)
            insert(old_projection, mask & 15)
        quantities[rule] = {
            "moves": len(allowed),
            "rank": len(basis),
            "rank on the four source distinctions": len(old_projection),
            "dimension in their span fixing the start": len(basis) - len(old_projection),
        }
        assert quantities[rule]["dimension in their span fixing the start"] == 14
    example = [4, 5, 18, 16]
    assert any(mask == row(example) for _, mask in moves)
    return {
        "stage": "one four-place knot after two ordinary rounds",
        "distinctions": n,
        "knot laws": [list(bits) for bits in knots],
        "supports tested through size five": tested,
        "shortest length for every distinction determined": True,
        "readings": quantities,
        "four-change": example,
        "shortest change containing each member": [minimum[b][1] for b in example],
    }


def counts_by_rule(runs):
    summary = {}
    for rule in ("ordinary", "cap three"):
        all_runs = [value[rule] for value in runs.values()]
        stages = [s for value in all_runs for s in value["reached"]]
        coverage = Counter()
        for stage in stages:
            coverage.update(stage["common-neighbour pairs by number of common children"])
        summary[rule] = {
            "completed stages": len(stages),
            "stages after round six": sum(s["round"] > 6 for s in stages),
            "births": sum(sum(s["birth sizes by parent count"].values()) for s in stages),
            "eligible pair occurrences": sum(coverage.values()),
            "eligible pair occurrences with multiple common children": sum(
                count for n, count in coverage.items() if n > 1),
            "rank checks matched under both readings": sum(s["origin gap under each reading"] == [0, 0] for s in stages),
            "largest dimension fixing the start": max(s["dimension of changes fixing the start"] for s in stages),
            "stops by reason": census(r["end"]["stop"] for r in all_runs),
        }
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (LIMIT_BYTES, LIMIT_BYTES))
    started = time.monotonic()
    runs = {}
    for name, bound in CASES.items():
        runs[name] = {}
        for capped in (False, True):
            n = min(bound, 3) if args.pilot else bound
            runs[name]["cap three" if capped else "ordinary"] = trajectory(name, capped, n)
    literal = literal_small_changes()
    seconds = time.monotonic() - started
    stages = sum(len(r["reached"]) for by_rule in runs.values() for r in by_rule.values())
    summary = {"completed stages": stages, "seconds": round(seconds, 3),
               "peak resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    if not args.pilot:
        record = {
            "selection": "Seven stated starts, each with equal weight in counts of starts. The stages compare the ordinary parity fresh count under two group rules.",
            "caps": {"rounds": CASES, "births per round before lookahead": MAX_BIRTHS,
                     "distinctions per stage": MAX_BITS, "address space bytes": LIMIT_BYTES, "compute processes": 1},
            "definitions": [
                "A pair of live knots with a common neighbour is covered by a selected larger group, or receives its own two-parent birth. With a cap of three all valid triples are selected. A larger valid group has mutually eligible pairs and no neighbour common to all its members.",
                "When a round is funded, the required pair coverage is existential. Multiple births may cover one pair.",
                "The source-fixing dimension is the number of new distinctions less the rank of the grown laws restricted to them. Origin gap counts independent source-fixing changes outside the span of small changes of the whole stage.",
                "The short generators checked here are pairs or loops of four on new distinctions. Shortest means shortest through at least one member in the entire stage. A rank reaching the source-fixing dimension certifies an exact zero origin gap under the chosen reading.",
                "The eight-knot starts have four live knots, and four other knots each meeting a different triple. In the ten-knot start six other knots each meet a distinct pair. The nine-knot start omits the meeting of the last pair, leaving two valid groups of three with two common members.",
            ],
            "comparison with frozen ordinary records": frozen_comparison(runs),
            "direct parity-law comparison": literal,
            "counts by group rule": counts_by_rule(runs),
            "scope": [
                "The cap changes which groups form and their next-round demand. In a funded round it preserves the common-child premise for every candidate pair by the explicit two-parent fallback. On stalls there is no next stage.",
                "A four-change need only be shortest through at least one distinction to enter the shortest-change span. The direct comparison gives shortest witnesses of lengths four, four, two and two for one such change in an ordinary stage.",
                "These finite ranks answer the sensitivity test outside the frozen ordinary roster. Unread stages beyond the stated bounds and the larger starts do not contribute to the counts.",
            ],
            "summary": summary, "runs": runs,
        }
        with (HERE / "group_limit.json").open("w") as f:
            json.dump(record, f, indent=2)
            f.write("\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
