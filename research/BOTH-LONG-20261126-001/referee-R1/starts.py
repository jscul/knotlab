"""Starts and ordinary parity growth for the connected starts in this study.

The joining and funding rules are in Intuitions, lesson 8.1, and section 0
of the fresh-count and ring identification proofs. Distinction numbers in a
start come from the ring convention or from the archived start records.
"""

import gzip
import json
from collections import Counter, defaultdict
from collections.abc import Iterable
from functools import cache
from itertools import combinations
from pathlib import Path


Knots = tuple[tuple[int, ...], ...]
ARCHIVE = Path(__file__).resolve().parents[2] / "FORBID-EDITS-20261126-001"


def ring(n: int) -> Knots:
    """Return a ring of n four-place knots with two loose distinctions each."""
    if n < 3:
        raise ValueError("A ring start needs at least three knots.")
    return tuple((i, (i + 1) % n, n + 2 * i, n + 2 * i + 1) for i in range(n))


@cache
def _census_records():
    with (ARCHIVE / "starts.json").open(encoding="utf-8") as source:
        return json.load(source)


def census_start(start_id: int) -> Knots:
    """Read an original census ID, numbering shared distinctions first."""
    records = _census_records()
    if not 0 <= start_id < len(records):
        raise KeyError(start_id)
    n, shared_counts, loose_counts = records[start_id]
    rows = [[] for _ in range(n)]
    distinction = 0
    for first, second, count in shared_counts:
        for _ in range(count):
            rows[first].append(distinction)
            rows[second].append(distinction)
            distinction += 1
    for row, count in zip(rows, loose_counts, strict=True):
        row.extend(range(distinction, distinction + count))
        distinction += count
    return tuple(tuple(row) for row in rows)


@cache
def _extension_shard(first_id: int) -> dict[int, Knots]:
    # The E1 count archive records the original supports for all 1,000 starts
    # in each shard. Use only the input fields and keep the original labels.
    starts = {}
    with gzip.open(ARCHIVE / f"xcount_E1_{first_id}.jsonl.gz", "rt", encoding="utf-8") as source:
        for line in source:
            record = json.loads(line)
            start_id = record["start"]
            if start_id not in starts:
                starts[start_id] = tuple(tuple(row) for row in record["supports"])
    return starts


def extension_start(start_id: int) -> Knots:
    """Read an original extension ID and its distinction numbers."""
    if not 0 <= start_id < 3000:
        raise KeyError(start_id)
    return _extension_shard(start_id // 1000 * 1000)[start_id]


def _maximal_candidate_sets(candidates: dict[int, set[int]]):
    """Enumerate maximal sets whose members are pairwise candidates."""
    def visit(group, remaining, used):
        if not remaining and not used:
            yield tuple(sorted(group))
            return
        pivot = max(remaining | used, key=lambda knot: len(remaining & candidates[knot]))
        for knot in remaining - candidates[pivot]:
            partners = candidates[knot]
            yield from visit(group + (knot,), remaining & partners, used & partners)
            remaining.remove(knot)
            used.add(knot)

    if candidates:
        yield from visit((), set(candidates), set())


def _groups(neighbours: dict[int, set[int]]) -> list[tuple[int, ...]]:
    """Find joining groups from each live knot's set of neighbours."""
    through = defaultdict(list)
    for knot, partners in neighbours.items():
        for partner in partners:
            through[partner].append(knot)
    candidates = {knot: set() for knot in neighbours}
    for knots in through.values():
        for first, second in combinations(knots, 2):
            candidates[first].add(second)
            candidates[second].add(first)

    pairs = {(a, b) for a, partners in candidates.items() for b in partners if a < b}
    larger = []
    for group in _maximal_candidate_sets(candidates):
        if len(group) >= 3 and not set.intersection(*(neighbours[i] for i in group)):
            larger.append(group)
            pairs.difference_update(combinations(group, 2))
    return sorted(larger + list(pairs))


def grow(knots: Iterable[Iterable[int]]) -> Knots:
    """Apply one complete round, returning the old knots on a stall or closure."""
    rows = tuple(tuple(knot) for knot in knots)
    holders = defaultdict(list)
    for knot, row in enumerate(rows):
        for distinction in row:
            holders[distinction].append(knot)
    neighbours = defaultdict(set)
    loose = defaultdict(list)
    for distinction, owners in holders.items():
        if len(owners) == 1:
            loose[owners[0]].append(distinction)
        else:
            for first, second in combinations(owners, 2):
                neighbours[first].add(second)
                neighbours[second].add(first)
    if not loose:
        return rows

    groups = _groups({knot: neighbours[knot] for knot in loose})
    demand = Counter(knot for group in groups for knot in group)
    if any(demand[knot] > len(loose[knot]) for knot in demand):
        return rows

    available = {knot: iter(sorted(distinctions)) for knot, distinctions in sorted(loose.items())}
    planned = [(group, tuple(next(available[knot]) for knot in group)) for group in groups]
    planned.extend(((knot,), (distinction,)) for knot, rest in available.items() for distinction in rest)

    # Every new knot is provisionally live. Two new knots can have a
    # common neighbour only among the old knots from which they take.
    following = _groups({i: set(parents) for i, (parents, _) in enumerate(planned)})
    next_demand = Counter(knot for group in following for knot in group)
    new_id = max(holders) + 1
    new_rows = []
    for i, (parents, taken) in enumerate(planned):
        # On a connected start, a single birth taking all loose distinctions
        # has the parity already implied by the old knots.
        fresh = next_demand[i] if len(planned) == 1 else max(next_demand[i], 3 - len(parents), 1)
        new_rows.append(taken + tuple(range(new_id, new_id + fresh)))
        new_id += fresh
    return rows + tuple(new_rows)
