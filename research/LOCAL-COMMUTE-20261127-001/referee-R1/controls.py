"""Independent checks of the frozen controls, the circular-order criterion and the ten losses."""
import argparse
import itertools
import json
import random
from collections import Counter
from functools import cache
from pathlib import Path

from core import State, history, read_starts

HERE = Path(__file__).resolve().parent
RECORD = HERE.parent
ROOT = RECORD.parents[1]
TYPES = ROOT / "artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/census.json"
RING = ((0, 1, 2), (1, 3, 4), (3, 0, 5))
THREE_LABEL = ((0, 1, 2), (0, 3, 4), (1, 5, 6), (2, 7, 8))


def pair(a, b):
    return (a, b) if a < b else (b, a)


def from_sharing(count, sharing):
    knots = [[] for _ in range(count)]
    for distinction, (a, b) in enumerate(sharing):
        knots[a].append(distinction)
        knots[b].append(distinction)
    return State(knots)


def word_cost(state, failing, order):
    """Cancel the right mate of the leftmost occurrence by moving it left."""
    word = [d for k in order for d in state.knots[k]]
    sign = 0
    while word:
        first = word.pop(0)
        mate = word.index(first)
        sign ^= sum(pair(first, d) in failing for d in word[:mate]) % 2
        word.pop(mate)
    return sign


def commute(state, failing):
    for left, right in itertools.combinations(state.knots, 2):
        if sum(pair(a, b) in failing for a in left for b in right) % 2:
            return False
    return True


def choices(state, pairs):
    """Track column dependencies to construct a basis of actual commuting choices."""
    pairs = list(pairs)
    knot_pairs = list(itertools.combinations(range(len(state.knots)), 2))
    pivot = {}
    free = []
    for i, (a, b) in enumerate(pairs):
        column = sum(1 << j for j, (u, v) in enumerate(knot_pairs)
                     if ((a in state.knots[u] and b in state.knots[v]) !=
                         (b in state.knots[u] and a in state.knots[v])))
        assignment = 1 << i
        while column:
            first = column & -column
            if first not in pivot:
                pivot[first] = column, assignment
                break
            other, changed = pivot[first]
            column ^= other
            assignment ^= changed
        if not column:
            free.append(assignment)
    return free


def selected(pairs, assignment):
    return {p for i, p in enumerate(pairs) if assignment & (1 << i)}


def odd_witness(state, pairs):
    for member in choices(state, pairs):
        failing = selected(pairs, member)
        if word_cost(state, failing, range(len(state.knots))):
            assert commute(state, failing)
            return sorted(failing)
    return None


@cache
def admits_circular_order(n, meetings):
    """Place knots successively. A prefix cannot contain alternating ends.

    Every unused knot will follow this prefix. A shared distinction leaving an
    interior knot of an already placed pair cannot end at any unused knot.
    """
    neighbors = [set() for _ in range(n)]
    for a, b in meetings:
        neighbors[a].add(b)
        neighbors[b].add(a)
    first = max(range(n), key=lambda k: len(neighbors[k]))

    def extend(order, left):
        if not left:
            return True
        for k in sorted(left, key=lambda u: -len(neighbors[u])):
            unused = left - {k}
            valid = True
            for i, u in enumerate(order):
                if k not in neighbors[u]:
                    continue
                outside = unused.union(order[:i])
                if any(neighbors[v] & outside for v in order[i + 1:]):
                    valid = False
                    break
            if valid and extend(order + (k,), unused):
                return True
        return False

    return extend((first,), set(range(n)) - {first})


def circular(state):
    meetings = tuple(sorted({tuple(holders) for holders in state.holders.values() if len(holders) == 2}))
    return admits_circular_order(len(state.knots), meetings)


def control_gates():
    census = json.loads(TYPES.read_text())
    type_odd = sum(odd_witness(state, state.whole_pairs) is not None
                   for row in census for state in [from_sharing(row["n"], row["sharing"])])
    rings = []
    for n, copies in [(3, 2), (4, 2), (5, 2), (4, 3)]:
        state = from_sharing(n, [(i, (i + 1) % n) for i in range(n) for _ in range(copies)])
        result = {"knots": n, "shared per meeting": copies, "unheld pairs": len(state.whole_pairs),
                  "odd": odd_witness(state, state.whole_pairs) is not None, "circular order": circular(state)}
        if (n, copies) == (4, 2):
            single = next(p for p in state.whole_pairs if word_cost(state, {p}, [0, 2, 1, 3]))
            result["mutant one failing pair"] = single
            result["mutant satisfies the commuting conditions"] = commute(state, {single})
        rings.append(result)
    ring = history(RING)
    state = ring.states[-1]
    natural = set(state.birth_pairs)
    seed_closed = State(state.knots)
    assert seed_closed.closed and len(choices(seed_closed, seed_closed.birth_pairs)) == 1
    star = history(THREE_LABEL)
    last = star.states[-1]
    return {"whole odd on prior types": [type_odd, len(census)], "repeated meetings": rings,
            "three-knot start with one loose distinction each": {
                "closes at": state.round, "closed": state.closed, "matching": sorted(natural),
                "commuting": commute(state, natural), "natural cost": word_cost(state, natural, range(4)),
                "same four knots presented already closed": list(state.knots)},
            "one knot meeting three others with two loose distinctions each": {
                "closes at": last.round, "closed": last.closed, "knots": len(last.knots),
                "birth odd": odd_witness(last, last.birth_pairs) is not None,
                "whole odd": odd_witness(last, last.whole_pairs) is not None,
                "natural first failure": next(s.round for s in star.states if not commute(s, set(s.birth_pairs)))}}


def earlier_closures(closures):
    path = RECORD.parent / "BUILT-BINDING-20261126-001/closing_census_parity.jsonl"
    earlier = {}
    births = 0
    for line in path.read_text().splitlines():
        row = json.loads(line)
        for birth in row.get("births", ()):
            if "implied" in birth:
                births += 1
                if birth["implied"]:
                    assert birth["takes all"]
                    earlier[int(row["start"].split()[1])] = birth["round"]
    here = {row["start"]: row["closing round"] for row in closures}
    return {"earlier parity births": births, "earlier implied births": len(earlier),
            "same census indices and closing rounds": earlier == here}


def check_loss(run, identifier):
    last = run.states[-1]
    assert odd_witness(last, last.birth_pairs) is None and odd_witness(last, last.whole_pairs) is not None
    start = run.states[0]
    neighbors = [set() for _ in start.knots]
    for holders in start.holders.values():
        if len(holders) == 2:
            a, b = holders
            neighbors[a].add(b)
            neighbors[b].add(a)
    excluded = sorted(set(last.whole_pairs) - set(last.birth_pairs))
    # Retain the cost and the three omitted coordinates of every whole choice.
    # Their image has at most sixteen elements, independent of the full dimension.
    profiles = {0}
    for member in choices(last, last.whole_pairs):
        failing = selected(last.whole_pairs, member)
        value = word_cost(last, failing, range(len(last.knots)))
        for i, p in enumerate(excluded, start=1):
            if p in failing:
                value |= 1 << i
        profiles |= {prior ^ value for prior in profiles}
    odd_profiles = [[p for i, p in enumerate(excluded, start=1) if value & (1 << i)]
                    for value in sorted(profiles) if value & 1]
    certified = []
    for a, b in excluded:
        (u,), (v,) = start.holders[a], start.holders[b]
        if not (neighbors[u] & neighbors[v]):
            certified.append((a, b))
    witness = odd_witness(last, tuple(last.birth_pairs) + tuple(certified))
    # The original A1 control checks only the final holders of the supplied list.
    # Admit every unheld pair. This changes the sign verdict on this case.
    final_only_control = all(not set(last.holders[a]).intersection(last.holders[b])
                             for a, b in last.whole_pairs)
    new_knots = run.states[1].knots[len(start.knots):]
    split_same_knot = [p for knot in start.knots for p in itertools.combinations(sorted(knot), 2)
                       if all(len(start.holders[d]) == 1 for d in p)
                       and not any(set(p).issubset(k) for k in new_knots)]
    return {"start index": identifier, "forbidden by birth rule": excluded,
            "possible subsets of the forbidden pairs in an odd whole choice": odd_profiles,
            "two initially coheld loose distinctions taken apart in round one": split_same_knot,
            "A1 final-holder test passes after allowing every whole pair": final_only_control,
            "forbidden pairs whose holders have no common neighbor at round zero": certified,
            "odd witness when permitting only those additional pairs": witness}


def order_trials(state, rng):
    tally = Counter()
    for pairs in (state.birth_pairs, state.whole_pairs):
        free = choices(state, pairs)
        for _ in range(5):
            member = 0
            for vector in free:
                if rng.getrandbits(1):
                    member ^= vector
            failing = selected(pairs, member)
            assert commute(state, failing)
            signs = {word_cost(state, failing, rng.sample(range(len(state.knots)), len(state.knots)))
                     for _ in range(5)}
            tally["choices"] += 1
            tally["agree"] += len(signs) == 1
            tally["odd"] += signs == {1}
    return tally


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="Number of closed rows for a timed prefix, with no file output.")
    args = parser.parse_args()
    rows = [json.loads(line) for line in (RECORD / "results.jsonl").read_text().splitlines()]
    closures = [r for r in rows if "closing round" in r]
    seeded = random.Random(20261127).sample(closures, 10)
    picked = {r["start"] for r in seeded}
    rng = random.Random(43027)
    starts = read_starts()
    checks = Counter()
    order = Counter()
    excluded = []
    for r in closures[:args.limit]:
        identifier = r["start"]
        run = history(starts[identifier])
        state = run.states[-1]
        assert state.closed
        decision = circular(state)
        checks["closures"] += 1
        checks["admits circular order"] += decision
        checks["disagrees with recorded order criterion"] += decision != r["outerplanar"]
        if r["whole choices attain odd"] and not r["birth choices attain odd"]:
            excluded.append(check_loss(run, identifier))
        if identifier in picked:
            order.update(order_trials(state, rng))
    result = {"controls": control_gates(), "circular order": dict(checks),
              "prior whole-closure count": earlier_closures(closures),
              "separate seeded trial of the two choices under five orders": dict(order),
              "losses with a present-round certificate": excluded}
    if args.limit is None:
        (HERE / "controls.json").write_text(json.dumps(result, indent=2) + "\n")
    print(dict(checks), dict(order), len(excluded))


if __name__ == "__main__":
    main()
