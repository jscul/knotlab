"""Ordinary parity growth rebuilt from the complete-round joining rule."""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class Birth:
    knot: int
    parents: tuple[int, ...]
    inputs: tuple[int, ...]
    fresh: tuple[int, ...]
    demand: int
    implied: bool


def meeting_pattern(supports):
    """Give the holders of each distinction, each knot's meetings, and its loose names."""
    owners = defaultdict(list)
    for knot, row in enumerate(supports):
        for name in row:
            owners[name].append(knot)
    meetings = tuple(set() for _ in supports)
    for name, held in owners.items():
        if len(held) == 2 and held[0] != held[1]:
            a, b = held
            meetings[a].add(b)
            meetings[b].add(a)
        elif len(held) != 1:
            raise ValueError(f"Invalid holders for distinction {name}: {held}")
    loose = {
        knot: tuple(name for name in row if len(owners[name]) == 1)
        for knot, row in enumerate(supports)
    }
    return (
        {name: tuple(held) for name, held in owners.items()},
        meetings,
        {knot: names for knot, names in loose.items() if names},
    )


def components(adjacency):
    unseen = set(adjacency)
    while unseen:
        first = min(unseen)
        unseen.remove(first)
        pending = [first]
        members = {first}
        while pending:
            new = adjacency[pending.pop()] & unseen
            members.update(new)
            unseen.difference_update(new)
            pending.extend(new)
        yield tuple(sorted(members))


def witnesses(meetings, live):
    live = set(live)
    return tuple(contacts & live for contacts in meetings if contacts & live)


def candidate_adjacency(witnesses):
    adjacency = defaultdict(set)
    for group in witnesses:
        for a, b in combinations(group, 2):
            adjacency[a].add(b)
            adjacency[b].add(a)
    return adjacency


def families(supports):
    """The starting live knots grouped by candidate connectivity."""
    _, meetings, loose = meeting_pattern(supports)
    joined = candidate_adjacency(witnesses(meetings, loose))
    return tuple(components({knot: joined[knot] for knot in loose}))


def family_facts(supports, groups):
    """The starting family facts, as supports of parities of loose distinctions."""
    _, _, loose = meeting_pattern(supports)
    return tuple(tuple(name for knot in group for name in loose[knot]) for group in groups)


def _maximal_groups(adjacency):
    """List maximal sets of pairwise candidates by the pivoted clique algorithm."""
    pending = [(frozenset(), set(adjacency), set())]
    while pending:
        group, available, earlier = pending.pop()
        if not available:
            if not earlier:
                yield group
            continue

        pivot = max(available | earlier, key=lambda knot: len(adjacency[knot] & available))
        for knot in available - adjacency[pivot]:
            contacts = adjacency[knot]
            pending.append((group | {knot}, available & contacts, earlier & contacts))
            available.remove(knot)
            earlier.add(knot)


def joining_groups(blocks):
    """Unwitnessed maximal groups and every remaining candidate pair, in allocation order."""
    adjacency = candidate_adjacency(blocks)
    pairs = {(a, b) for a in adjacency for b in adjacency[a] if a < b}
    if not pairs:
        return ()
    large = sorted(
        tuple(sorted(group))
        for group in _maximal_groups(adjacency)
        if len(group) >= 3 and not any(group <= block for block in blocks)
    )
    covered = {pair for group in large for pair in combinations(group, 2)}
    return tuple(large + sorted(pairs - covered))


def name_mask(names):
    return sum(1 << name for name in names)


def reduce_mask(mask, basis):
    while mask:
        pivot = basis.get(mask.bit_length())
        if pivot is None:
            return mask
        mask ^= pivot
    return 0


def parity_basis(rows):
    basis = {}
    for row in rows:
        mask = reduce_mask(name_mask(row), basis)
        if mask:
            basis[mask.bit_length()] = mask
    return basis


def advance(supports):
    """Give the next supports, funding status, and funded birth records."""
    supports = tuple(map(tuple, supports))
    holders, meetings, loose = meeting_pattern(supports)
    if not loose:
        return supports, "closed", ()
    groups = joining_groups(witnesses(meetings, loose))
    demand = Counter(parent for group in groups for parent in group)
    if any(demand[parent] > len(names) for parent, names in loose.items()):
        return supports, "stalled", ()

    available = {parent: iter(names) for parent, names in loose.items()}
    plan = [(group, tuple(sorted(next(available[p]) for p in group))) for group in groups]
    plan.extend(
        ((parent,), (name,))
        for parent in sorted(available)
        for name in available[parent]
    )

    paid = defaultdict(set)
    for index, (parents, _) in enumerate(plan, len(supports)):
        for parent in parents:
            paid[parent].add(index)
    next_groups = joining_groups(tuple(paid.values()))
    next_demand = Counter(knot for group in next_groups for knot in group)
    old_laws = parity_basis(supports)
    fresh_start = max(holders) + 1
    births = []
    for knot, (parents, inputs) in enumerate(plan, len(supports)):
        implied = not reduce_mask(name_mask(inputs), old_laws)
        demand = next_demand[knot]
        count = demand if implied else max(demand, 3 - len(inputs), 1)
        fresh = tuple(range(fresh_start, fresh_start + count))
        fresh_start += count
        births.append(Birth(knot, parents, inputs, fresh, demand, implied))
    return supports + tuple(birth.inputs + birth.fresh for birth in births), "funded", tuple(births)


def stages(supports, rounds=4, cap=300):
    """Yield round, supports if readable, status, and births."""
    births = ()
    supports = tuple(map(tuple, supports))
    for round_number in range(rounds + 1):
        if round_number:
            supports, status, births = advance(supports)
            if status != "funded":
                yield round_number, None, status, births
                return
        if cap is not None and len({name for row in supports for name in row}) > cap:
            yield round_number, None, "not read", births
            return
        yield round_number, supports, "stage", births


def family_step_counts(supports, groups):
    """Minimum holder-step counts in the start, between all pairs of families."""
    _, meetings, _ = meeting_pattern(supports)
    distances = {}
    for i, group in enumerate(groups):
        steps = {knot: 0 for knot in group}
        todo = deque(group)
        while todo:
            knot = todo.popleft()
            for other in meetings[knot]:
                if other not in steps:
                    steps[other] = steps[knot] + 1
                    todo.append(other)
        for j in range(i + 1, len(groups)):
            reachable = [steps[knot] for knot in groups[j] if knot in steps]
            distances[i, j] = min(reachable, default=None)
    return distances
