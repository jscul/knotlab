"""Independent ordinary growth for finite, two-holder not-all-equal starts."""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class Birth:
    knot: int
    parents: tuple[int, ...]
    inputs: tuple[int, ...]
    demand: int
    fresh: tuple[int, ...]


@dataclass(frozen=True)
class Growth:
    status: str
    supports: tuple[tuple[int, ...], ...]
    births: tuple[Birth, ...]
    shortages: dict[int, int]


class GrowthLimit(RuntimeError):
    pass


def supports_of(start):
    knot_count, shared_multiplicities, loose_counts = start
    supports = [[] for _ in range(knot_count)]
    distinction = 0
    for first, second, multiplicity in shared_multiplicities:
        shared = range(distinction, distinction + multiplicity)
        supports[first].extend(shared)
        supports[second].extend(shared)
        distinction += multiplicity
    for support, count in zip(supports, loose_counts, strict=True):
        support.extend(range(distinction, distinction + count))
        distinction += count
    return tuple(tuple(support) for support in supports)


def holders(supports):
    result = defaultdict(list)
    for knot, support in enumerate(supports):
        if len(support) < 3 or len(set(support)) != len(support):
            raise ValueError("Each start support must contain at least three distinct identities")
        for distinction in support:
            result[distinction].append(knot)
    if any(len(owners) > 2 for owners in result.values()):
        raise ValueError("A distinction may have at most two holders")
    return result


def loose(supports):
    return tuple(sorted(distinction for distinction, owners in holders(supports).items() if len(owners) == 1))


def maximal_candidate_sets(adjacency, search_limit):
    """Enumerate maximal cliques of the mathematical candidate graph."""
    visits = 0

    def search(chosen, remaining, excluded):
        nonlocal visits
        visits += 1
        if search_limit is not None and visits > search_limit:
            raise GrowthLimit("candidate-set search limit")
        if not remaining and not excluded:
            yield tuple(sorted(chosen))
            return
        pivot = max(remaining | excluded, key=lambda knot: (len(remaining & adjacency[knot]), -knot))
        for knot in sorted(remaining - adjacency[pivot]):
            neighbours = adjacency[knot]
            yield from search(chosen + (knot,), remaining & neighbours, excluded & neighbours)
            remaining.remove(knot)
            excluded.add(knot)

    if adjacency:
        yield from search((), set(adjacency), set())


def groups(overlaps, live, search_limit=None):
    by_knot = {knot: set() for knot in live}
    for witness, neighbours in overlaps.items():
        for knot in live & neighbours:
            by_knot[knot].add(witness)
    adjacency = {knot: set() for knot in live}
    for neighbours in overlaps.values():
        available = live & neighbours
        for knot in available:
            adjacency[knot].update(available - {knot})

    # Absence of a common witness is preserved under enlargement. Each
    # maximal valid group is therefore a maximal clique of this graph.
    large = [
        group
        for group in maximal_candidate_sets(adjacency, search_limit)
        if len(group) >= 3 and not set.intersection(*(by_knot[knot] for knot in group))
    ]
    covered = {pair for group in large for pair in combinations(group, 2)}
    pairs = sorted((first, second) for first in adjacency for second in adjacency[first] if first < second)
    return sorted(large) + [pair for pair in pairs if pair not in covered]


def advance(supports, *, max_births=None, search_limit=None):
    """Build one complete round. Identity order only resolves equivalent choices of loose distinctions."""
    supports = tuple(map(tuple, supports))
    owners = holders(supports)
    unused = {
        knot: deque(distinction for distinction in support if len(owners[distinction]) == 1)
        for knot, support in enumerate(supports)
    }
    live = {knot for knot, distinctions in unused.items() if distinctions}
    if not live:
        return Growth("closed", supports, (), {})

    overlaps = defaultdict(set)
    for knots in owners.values():
        if len(knots) == 2:
            first, second = knots
            overlaps[first].add(second)
            overlaps[second].add(first)
    joined = groups(overlaps, live, search_limit)
    spent = Counter(knot for joined_group in joined for knot in joined_group)
    shortages = {knot: spent[knot] - len(unused[knot]) for knot in sorted(live) if spent[knot] > len(unused[knot])}
    if shortages:
        return Growth("stalled", supports, (), shortages)

    roster = joined + [(knot,) for knot in sorted(live) for _ in range(len(unused[knot]) - spent[knot])]
    if max_births is not None and len(roster) > max_births:
        raise GrowthLimit(f"birth count {len(roster)} exceeds {max_births}")
    children = defaultdict(set)
    for knot, parents in enumerate(roster, start=len(supports)):
        for parent in parents:
            children[parent].add(knot)
    newborn = set(range(len(supports), len(supports) + len(roster)))
    demand = Counter(child for group in groups(children, newborn, search_limit) for child in group)

    # The two-holder implication lemma gives a fresh distinction even at
    # zero demand. Each chosen input removes only one place from an old knot.
    next_distinction = max(owners) + 1
    births = []
    for knot, parents in enumerate(roster, start=len(supports)):
        inputs = tuple(sorted(unused[parent].popleft() for parent in parents))
        count = max(demand[knot], 3 - len(parents), 1)
        fresh = tuple(range(next_distinction, next_distinction + count))
        next_distinction += count
        births.append(Birth(knot, parents, inputs, demand[knot], fresh))
    return Growth("funded", supports + tuple(birth.inputs + birth.fresh for birth in births), tuple(births), {})
