"""Regrow the archived start roster and reconstruct the binary systems before reading verdicts."""

import json
import sys
from collections import Counter, defaultdict
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = ROOT / "research/LOCAL-COMMUTE-20261127-001/referee-R1"
sys.path.insert(0, str(PREVIOUS))
import core

CENSUS = ROOT / "artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/census.json"


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def history(start):
    """Skip pair decisions for unfinished starts. Preserve every admitted stage for closures."""
    stages = [start]
    while True:
        knots = stages[-1]
        twice = Counter(d for knot in knots for d in knot)
        if all(count == 2 for count in twice.values()):
            return "closed", stages
        later, status, _ = core.forbid.grown(knots, "parity", "ordinary")
        if status == "stalled":
            return "stalled", stages
        assert status == "funded"
        if len(stages) == 5:
            return "growing", stages
        if len(later) > 40:
            return "cut", stages
        stages.append(later)


def alternate(left, right, ranks):
    a, b = sorted(ranks[h] for h in left)
    c, d = sorted(ranks[h] for h in right)
    return a < c < b < d or c < a < d < b


def build(stages):
    previous = None
    for knots in stages:
        previous = core.State(knots, previous)
    state = previous
    pairs = state.birth_pairs
    holders = state.holders
    k = len(state.knots)
    knot_pairs = list(combinations(range(k), 2))
    indices = {key: i for i, key in enumerate(knot_pairs)}
    rows = [0] * len(indices)
    groups = defaultdict(list)
    cost = 0
    for i, (a, b) in enumerate(pairs):
        u, v = holders[a], holders[b]
        assert len(u) == len(v) == 2 and not set(u).intersection(v)
        for left, right in product(u, v):
            rows[indices[tuple(sorted((left, right)))]] |= 1 << i
        cost |= int(alternate(u, v, range(k))) << i
        groups[tuple(sorted((u, v)))].append(i)
    assert rows == list(core.commutation(state, pairs))
    assert cost == core.closing_cost(state, pairs)
    basis = core.basis(rows)
    for positions in groups.values():
        for mask in [*rows, cost]:
            assert len({(mask >> i) & 1 for i in positions}) == 1

    # Moving the two consecutive knot words past one another toggles precisely
    # their common parity equation. Adjacent exchanges generate every order.
    for (a, b), row in zip(knot_pairs, rows, strict=True):
        rest = [u for u in range(k) if u not in (a, b)]
        left = core.closing_cost(state, pairs, [a, b, *rest])
        right = core.closing_cost(state, pairs, [b, a, *rest])
        assert left ^ right == row and core.remainder(left ^ cost, basis) == 0
    assert core.closing_cost(state, pairs, reversed(range(k))) == cost
    return {
        "knots": k, "supports": state.knots, "pairs": pairs, "checks": rows, "cost": cost,
        "groups": list(groups.values()), "holder multiplicities": list(Counter(holders.values()).values()),
        "dimension": len(pairs) - len(basis), "odd attainable": bool(core.remainder(cost, basis)),
        "natural rule keeps a state": all(r.bit_count() % 2 == 0 for r in rows),
        "all unheld decidable": pairs == state.whole_pairs,
    }


def main():
    counts = Counter()
    starts = core.read_starts()  # The earlier referee regenerated and compared the complete roster in order.
    with (HERE / "codes.jsonl").open("w") as target:
        def emit(data):
            target.write(json.dumps(data, separators=(",", ":")) + "\n")

        for i, start in enumerate(starts):
            end, stages = history(start)
            t = len(stages) - 1
            counts["already closed" if end == "closed" and not t else end] += 1
            if end != "closed" or not t:
                continue
            data = build(stages)
            closed = core.State(stages[-1])
            whole = closed.whole_pairs
            full_rows = core.basis(core.commutation(closed, whole))
            if core.remainder(core.closing_cost(closed, whole), full_rows):
                counts["odd attainable on the finished holding"] += 1
            else:
                assert not data["odd attainable"]
            if data["odd attainable"]:
                emit({"start": i, "round": t, **data})
                counts["retained closures"] += 1

        for i, pattern in enumerate(json.loads(CENSUS.read_text())):
            holders = pattern["sharing"]
            knots = [tuple(d for d, owners in enumerate(holders) if u in owners) for u in range(pattern["n"])]
            data = build([knots])
            assert data["all unheld decidable"]
            emit({"type": i, "labelled": pattern["labelled"], **data})
        ring = ((0, 1, 2), (1, 3, 4), (3, 0, 5))
        end, stages = history(ring)
        assert end == "closed"
        emit({"hand": "three-knot start", **build(stages)})
        for k in (4, 5):
            knots = [tuple([k + (j - 1) % k, j, k + j]) for j in range(k)] + [tuple(range(k))]
            emit({"hand": f"{k} knots around one", **build([knots])})
    save(HERE / "population.json", {"starts": len(starts), **counts})


if __name__ == "__main__":
    main()
