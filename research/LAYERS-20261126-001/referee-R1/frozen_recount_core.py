"""Independent parity growth, motion and readings for the frozen recount."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations


def mask(names):
    return sum(1 << name for name in names)


def names_of(word):
    while word:
        bit = word & -word
        yield bit.bit_length() - 1
        word ^= bit


class BinarySpan:
    def __init__(self, words=()):
        self.pivots = {}
        for word in words:
            self.add(word)

    def remainder(self, word):
        while word:
            row = self.pivots.get(word.bit_length() - 1)
            if row is None:
                break
            word ^= row
        return word

    def add(self, word):
        word = self.remainder(word)
        if word:
            self.pivots[word.bit_length() - 1] = word

    def __len__(self):
        return len(self.pivots)

    def __contains__(self, word):
        return self.remainder(word) == 0


def perpendicular(words, names):
    equations = BinarySpan(words).pivots
    ordered = sorted(equations.items())
    free = []
    for name in names:
        if name in equations:
            continue
        word = 1 << name
        for pivot, equation in ordered:
            if (word & equation).bit_count() & 1:
                word |= 1 << pivot
        free.append(word)
    return tuple(free)


def evaluate(functional, allowed):
    return sum(1 << i for i, word in enumerate(allowed) if (functional & word).bit_count() & 1)


def owners_of(rows):
    owners = defaultdict(list)
    for i, row in enumerate(rows):
        if len(row) != len(set(row)):
            raise ValueError(f"Repeated distinction at knot {i}")
        for name in row:
            owners[name].append(i)
    if any(len(holders) > 2 for holders in owners.values()):
        raise ValueError("The replay requires at most two holders per distinction")
    return {name: tuple(holders) for name, holders in owners.items()}


def meeting_sets(count, owners):
    meets = [set() for _ in range(count)]
    for holders in owners.values():
        if len(holders) == 2:
            first, second = holders
            meets[first].add(second)
            meets[second].add(first)
    return meets


def components(meets):
    remaining = set(range(len(meets)))
    result = []
    while remaining:
        pending = [min(remaining)]
        remaining.remove(pending[0])
        for knot in pending:
            newly_reached = meets[knot] & remaining
            remaining -= newly_reached
            pending.extend(sorted(newly_reached))
        result.append(tuple(pending))
    return result


def groups_among(witness_sets):
    """Choose all maximal eligible groups, then all uncovered candidate pairs."""
    candidates = defaultdict(set)
    witnesses = defaultdict(set)
    pairs = set()
    for i, members in enumerate(witness_sets):
        for first, second in combinations(sorted(members), 2):
            pairs.add((first, second))
            candidates[first].add(second)
            candidates[second].add(first)
        for member in members:
            witnesses[member].add(i)

    large = []

    def maximal(group, remaining, excluded):
        if not remaining:
            if not excluded and len(group) >= 3:
                if not set.intersection(*(witnesses[knot] for knot in group)):
                    large.append(tuple(sorted(group)))
            return
        pivot = max(remaining | excluded, key=lambda knot: len(remaining & candidates[knot]))
        for knot in sorted(remaining - candidates[pivot]):
            neighbors = candidates[knot]
            maximal(group + (knot,), remaining & neighbors, excluded & neighbors)
            remaining.remove(knot)
            excluded.add(knot)

    maximal((), set(candidates), set())
    covered = {pair for group in large for pair in combinations(group, 2)}
    return sorted(large) + sorted(pairs - covered)


def first_groups(rows, provision_all=False):
    owners = owners_of(rows)
    meets = meeting_sets(len(rows), owners)
    loose = tuple(tuple(d for d in row if len(owners[d]) == 1) for row in rows)
    live = set(range(len(rows))) if provision_all else {i for i, row in enumerate(loose) if row}
    groups = groups_among([neighbors & live for neighbors in meets])
    demand = Counter(knot for group in groups for knot in group)
    return loose, groups, demand


@dataclass(frozen=True)
class Birth:
    parents: tuple
    inputs: tuple
    demand: int
    fresh: tuple
    implied: bool


@dataclass(frozen=True)
class Growth:
    status: str
    stage: tuple
    births: tuple = ()
    shortages: tuple = ()
    distinctions: int = 0


def grow(rows, arm="ordinary", max_distinctions=None):
    """Apply the complete ordinary round or one of the two archived fresh-count cuts."""
    if arm not in ("ordinary", "one_fewer", "arity_floor"):
        raise ValueError(f"Unknown fresh-count rule {arm!r}")
    rows = tuple(tuple(row) for row in rows)
    loose, groups, demand = first_groups(rows)
    num_old = len({d for row in rows for d in row})
    if not any(loose):
        return Growth("closed", rows, distinctions=num_old)
    shortages = tuple((i, demand[i] - len(row)) for i, row in enumerate(loose) if demand[i] > len(row))
    if shortages:
        return Growth("stalled", rows, shortages=shortages, distinctions=num_old)

    # Allocate one distinction per group member, then consume each remainder separately.
    parents = groups + [(i,) for i, row in enumerate(loose) for _ in row[demand[i]:]]
    remaining = [iter(row) for row in loose]
    inputs = [tuple(next(remaining[knot]) for knot in group) for group in parents]
    assert {name for row in inputs for name in row} == {name for row in loose for name in row}

    children = [set() for _ in rows]
    for birth, group in enumerate(parents):
        for knot in group:
            children[knot].add(birth)
    next_groups = groups_among(children)
    next_demand = Counter(birth for group in next_groups for birth in group)
    old_checks = BinarySpan(map(mask, rows))
    next_name = 1 + max(d for row in rows for d in row)
    first_fresh = next_name
    births = []
    for i, (group, row) in enumerate(zip(parents, inputs, strict=True)):
        implied = mask(row) in old_checks
        required = next_demand[i]
        count = required if implied else max(required, 3 - len(row), 1)
        floor = max(0, 3 - len(row))
        if arm == "one_fewer":
            count = min(count, max(floor, count - 1))
        elif arm == "arity_floor":
            count = min(count, floor)
        fresh = tuple(range(next_name, next_name + count))
        next_name += count
        if max_distinctions is not None and num_old + next_name - first_fresh > max_distinctions:
            return Growth("capped", rows, distinctions=num_old + next_name - first_fresh)
        births.append(Birth(group, row, required, fresh, implied))
    return Growth(
        "funded", rows + tuple(birth.inputs + birth.fresh for birth in births),
        tuple(births), distinctions=num_old + next_name - first_fresh,
    )


def incidence(rows, names, owners):
    exterior = len(rows)
    links = [[] for _ in range(exterior + 1)]
    pairs = {}
    for name in names:
        holders = owners[name]
        first = holders[0]
        second = holders[1] if len(holders) == 2 else exterior
        pairs[name] = (first, second)
        links[first].append((second, name))
        links[second].append((first, name))
    return links, pairs


def shortest_moves(links, pairs):
    """List all shortest allowed changes through each distinction, keeping every tie."""
    for name, (first, second) in pairs.items():
        level = [-1] * len(links)
        predecessors = [[] for _ in links]
        level[first] = 0
        current = [first]
        while current and level[second] < 0:
            next_level = []
            for knot in current:
                step = level[knot] + 1
                for other, via in links[knot]:
                    if via == name:
                        continue
                    if level[other] < 0:
                        level[other] = step
                        next_level.append(other)
                    if level[other] == step:
                        predecessors[other].append((knot, via))
            current = next_level
        if level[second] < 0:
            continue
        pending = [(second, 1 << name)]
        while pending:
            knot, support = pending.pop()
            if knot == first:
                yield name, support
            else:
                pending.extend((other, support | (1 << via)) for other, via in predecessors[knot])


def bounded_moves(links, limit):
    """Simple allowed changes span all allowed changes of at most the stated size."""
    for first in range(len(links)):
        pending = [(first, 0, 1 << first, 0)]
        while pending:
            knot, support, visited, size = pending.pop()
            for other, via in links[knot]:
                bit = 1 << via
                if support & bit:
                    continue
                if other == first and size > 0:
                    yield support | bit
                elif other > first and size + 1 < limit and not (visited >> other) & 1:
                    pending.append((other, support | bit, visited | (1 << other), size + 1))


@dataclass(frozen=True)
class Motion:
    rows: tuple
    names: tuple
    allowed: tuple
    moves: tuple
    move_basis: tuple
    ties: int

    @property
    def class_bits(self):
        return len(self.allowed) - len(self.move_basis)

    @property
    def classes(self):
        return 1 << self.class_bits

    def is_label(self, functional):
        keeps = not any((move & functional).bit_count() & 1 for move in self.move_basis)
        return keeps and bool(evaluate(functional, self.allowed))


def motion(rows, mode="shortest", pinned=(), limit=5):
    rows = tuple(tuple(row) for row in rows)
    owners = owners_of(rows)
    names = tuple(sorted(owners.keys() - set(pinned)))
    active = mask(names)
    allowed = perpendicular((mask(row) & active for row in rows), names)
    links, pairs = incidence(rows, names, owners)
    all_ties = 0
    if mode == "up_to":
        moves = set(bounded_moves(links, limit))
    elif mode in ("shortest", "shortest_overall"):
        moves = set()
        for _, change in shortest_moves(links, pairs):
            all_ties += 1
            moves.add(change)
        if mode == "shortest_overall" and moves:
            size = min(change.bit_count() for change in moves)
            moves = {change for change in moves if change.bit_count() == size}
    else:
        raise ValueError(f"Unknown move rule {mode!r}")
    moves = tuple(sorted(moves))
    return Motion(rows, names, allowed, moves, tuple(BinarySpan(moves).pivots.values()), all_ties)


def label_basis(result, readable_names):
    """Return independent class readings as {evaluation: representative parity mask}."""
    restriction = mask(readable_names)
    possible = perpendicular((move & restriction for move in result.move_basis), readable_names)
    selected = {}
    basis = BinarySpan()
    for functional in possible:
        value = evaluate(functional, result.allowed)
        if value not in basis:
            selected[value] = functional
            basis.add(value)
    return selected


def all_words(generators):
    words = {0}
    for generator in generators:
        words |= {word ^ generator for word in words}
    return words


def class_readers(result, enumeration_cap=12):
    """Separate the span of local labels from labels individually read at one knot."""
    names = set(result.names)
    readers = []
    knots = []
    for row in result.rows:
        visible = tuple(sorted(names & set(row)))
        visible_mask = mask(visible)
        available_rank = len(BinarySpan(state & visible_mask for state in result.allowed))
        knots.append(len(visible) >= 3 and available_rank == len(visible) - 1)
        readers.append(label_basis(result, visible))
    all_labels = label_basis(result, result.names)
    assert len(all_labels) == result.class_bits
    output = {"label_basis": all_labels, "readers": readers, "k1_k3": knots}
    for scope, include in (("listed", [True] * len(knots)), ("knots", knots)):
        local = [reader for reader, use in zip(readers, include, strict=True) if use]
        local_span = BinarySpan(value for reader in local for value in reader)
        summary = {"local_rank": len(local_span), "quotient_rank": result.class_bits - len(local_span)}
        if result.class_bits <= enumeration_cap:
            seen = {0}.union(*(all_words(reader) for reader in local))
            unreadable = all_words(all_labels) - seen
            summary.update({
                "locally_readable_count": len(seen) - 1,
                "unreadable_count": len(unreadable),
                "unreadable_rank": len(BinarySpan(unreadable)),
                "locally_readable_values": sorted(seen - {0}),
                "unreadable_values": sorted(unreadable),
            })
        output[scope] = summary
    return output


def projected_equality(old, new):
    keep = mask(old.names)
    after = BinarySpan(word & keep for word in new.allowed)
    return len(after) == len(old.allowed) and all(word in after for word in old.allowed)
