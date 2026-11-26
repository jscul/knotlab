"""Replay the study's round definitions with a live-count and meeting state.

The round follows RING-IN-BALANCE-20261123-001/definitions.md. The join and
the stub follow the documented TWO-PATTERNS bench construction. With no
taking rule or barred distinctions, shared distinctions never change
holders. The sets of knots that meet and the loose counts therefore suffice
for every group, payment and demand. This module reads no author code.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache, reduce
from itertools import combinations, count
from operator import or_
import re
from weakref import WeakValueDictionary


@dataclass(frozen=True, slots=True)
class Start:
    stars: tuple[tuple[int, ...], ...]
    site: int = 0

    @property
    def loose(self) -> tuple[int, ...]:
        holders = Counter(x for knot in self.stars for x in knot)
        return tuple(sum(holders[x] == 1 for x in knot) for knot in self.stars)


def from_sharings(loose, sharings, *, site=0) -> Start:
    stars = [[] for _ in loose]
    distinction = count()
    for a, b in sharings:
        x = next(distinction)
        stars[a].append(x)
        stars[b].append(x)
    for knot, number in zip(stars, loose):
        knot.extend(next(distinction) for _ in range(number))
    return Start(tuple(map(tuple, stars)), site)


def mutual_three(site_loose, other_loose=(2, 2), *, site=0) -> Start:
    loose = list(other_loose)
    loose.insert(site, site_loose)
    return from_sharings(loose, ((0, 1), (0, 2), (1, 2)), site=site)


@cache
def _atlas_sharings(index):
    # The archive keys use these published graph-atlas numbers and labels.
    from networkx.generators.atlas import graph_atlas

    return tuple(graph_atlas(index).edges())


@cache
def start(name: str) -> Start:
    if name == "stub":
        return Start(())
    if name == "ring":
        return from_sharings((3,) * 5, ((i, (i + 1) % 5) for i in range(5)))
    if name == "copier":
        return from_sharings((2, 2), ((0, 1),))
    if name == "source":
        return Start(((0, 1, 2, 9, 10, 11), (0, 1, 3), (4, 5, 12, 13, 14),
                      (6, 7, 15, 16, 17), (2, 3, 4, 6, 18, 19, 20),
                      (7, 8, 21, 22), (5, 8, 23, 24)))
    match = re.fullmatch(r"(?:n\d+:)?g(\d+):(\d+)@(\d+)", name)
    if match:
        index, loose, site = match.groups()
        return from_sharings(tuple(map(int, loose)), _atlas_sharings(int(index)), site=int(site))
    match = re.fullmatch(r"tri:(\d)(\d)(\d)@(\d+)", name)
    if match:
        a, b, c, site = map(int, match.groups())
        return from_sharings((a, b, c), ((0, 1), (0, 2), (1, 2)), site=site)
    raise ValueError(f"Unrecognized start {name!r}")


@dataclass(frozen=True, slots=True, eq=False, weakref_slot=True)
class BirthName:
    """An interned name, with a start knot named by its ordinal alone."""

    parents: tuple[BirthName, ...]
    ordinal: int
    order: int


_name_serial = count()
_names = WeakValueDictionary()


def _name(parents, ordinal):
    parents = tuple(sorted(parents, key=lambda p: p.order))
    key = (parents, ordinal)
    name = _names.get(key)
    if name is None:
        name = BirthName(parents, ordinal, next(_name_serial))
        _names[key] = name
    return name


BirthRead = tuple[BirthName, int, int]


@dataclass(frozen=True, slots=True)
class Round:
    knots: int
    own_signature: tuple[BirthRead, ...]
    sender_signature: tuple[BirthRead, ...]
    own_short: int
    sender_short: int
    own_members: int
    sender_members: int
    receiver_inclusive_births: int
    sender_site_owed_and_held: tuple[int, int] | None
    sender_site_live_neighbours: int

    @property
    def own_births(self):
        return len(self.own_signature)

    @property
    def sender_births(self):
        return len(self.sender_signature)


_OWN, _SENDER, _OTHER = 1, 2, 4


class _Structure:
    def __init__(self, receiver, sender, steps, join):
        self.meets: list[set[int]] = []
        self.loose: list[int] = []
        self.descent: list[int] = []
        self.names: list[BirthName | None] = []
        left = self.put(receiver, _OWN)
        self.sender_site = right = self.put(sender, _SENDER)
        line = [left]
        line.extend(self.add_knot(1 if join == "share" else 0) for _ in range(steps - 1))
        line.append(right)
        for x, y in zip(line, line[1:]):
            if join == "share":
                self.add_meeting(x, y)
            else:
                spent = self.add_knot(0)
                self.add_meeting(x, spent)
                self.add_meeting(y, spent)
                self.loose[x] += 1
                self.loose[y] += 1
        if not receiver.stars:
            self.loose[left] = 2
        if not sender.stars:
            self.loose[right] = 2 if join == "share" else 1

    def add_knot(self, loose, descent=_OTHER, name=None):
        knot = len(self.meets)
        self.meets.append(set())
        self.loose.append(loose)
        self.descent.append(descent)
        self.names.append(name)
        return knot

    def add_meeting(self, a, b):
        self.meets[a].add(b)
        self.meets[b].add(a)

    def put(self, pattern, role):
        if not pattern.stars:
            return self.add_knot(0, role, _name((), 0))
        first = len(self.meets)
        holders = defaultdict(list)
        for x, (places, loose) in enumerate(zip(pattern.stars, pattern.loose)):
            knot = self.add_knot(loose, role, _name((), x))
            for place in places:
                holders[place].append(knot)
        for knots in holders.values():
            if len(knots) > 2:
                raise ValueError("A start distinction must have one or two holders")
            if len(knots) == 2:
                self.add_meeting(*knots)
        return first + pattern.site


def _unwitnessed_maximal_cliques(neighbours, witness_sets):
    """Bron–Kerbosch search for maximal groups of three or more."""
    witness_of = defaultdict(list)
    for met in witness_sets:
        for member in met:
            witness_of[member].append(met)

    def search(chosen, candidates, excluded):
        if len(chosen) + len(candidates) < 3:
            return
        anchor = min(chosen or candidates, key=lambda u: len(witness_of[u]))
        if any(chosen <= met and candidates <= met for met in witness_of[anchor]):
            return
        if not candidates and not excluded:
            yield tuple(sorted(chosen))
            return
        pivot = max(candidates | excluded, key=lambda u: len(candidates & neighbours[u]))
        for member in candidates - neighbours[pivot]:
            adjacent = neighbours[member]
            yield from search(chosen | {member}, candidates & adjacent, excluded & adjacent)
            candidates.remove(member)
            excluded.add(member)

    unvisited = {member for member in neighbours if len(neighbours[member]) >= 2}
    while unvisited:
        first = unvisited.pop()
        component = {first}
        pending = [first]
        while pending:
            new = neighbours[pending.pop()] & unvisited
            unvisited.difference_update(new)
            component.update(new)
            pending.extend(new)
        if len(component) >= 3:
            yield from search(set(), component, set())


def _groups(meets, members):
    met_by = defaultdict(set)
    for member in members:
        for common in meets[member]:
            met_by[common].add(member)
    witness_sets = {frozenset(group) for group in met_by.values() if len(group) >= 2}
    neighbours = defaultdict(set)
    for met in witness_sets:
        for a, b in combinations(met, 2):
            neighbours[a].add(b)
            neighbours[b].add(a)
    large = sorted(_unwitnessed_maximal_cliques(neighbours, witness_sets))
    covered = {pair for group in large for pair in combinations(group, 2)}
    pairs = ((a, b) for a in neighbours for b in neighbours[a] if a < b and (a, b) not in covered)
    return large + sorted(pairs)


def _ration(law):
    if law == "ORD":
        return max
    if law == "REC-ONE-FEWER":
        return lambda demand, minimum, _: max(minimum, max(demand, minimum, 1) - 1)
    match = re.fullmatch(r"CAP-([3-9]\d*|[1-9]\d+)", law)
    if match:
        cap = int(match.group(1))
        return lambda demand, minimum, one: min(cap, max(demand, minimum, one))
    raise ValueError(f"Unrecognized law {law!r}")


def _advance(structure, ration):
    loose, meets, descent = structure.loose, structure.meets, structure.descent
    members = [u for u, number in enumerate(loose) if number > 0]
    groups = _groups(meets, members)
    owing = Counter(u for group in groups for u in group)
    short = {u for u in members if owing[u] > loose[u]}
    sender_site = structure.sender_site
    sender_site_owed_and_held = (owing[sender_site], loose[sender_site]) if loose[sender_site] else None
    sender_site_live_neighbours = sum(loose[v] > 0 for v in meets[sender_site])
    parents = [group for group in groups if short.isdisjoint(group)]
    for group in parents:
        for u in group:
            loose[u] -= 1
    for u in members:
        if u not in short:
            parents.extend([(u,)] * loose[u])
            loose[u] = 0

    first_new = len(meets)
    ordinal = Counter()
    for group in parents:
        family = reduce(or_, (descent[u] for u in group))
        name = None
        if family in (_OWN, _SENDER):
            name = _name((structure.names[u] for u in group), ordinal[group])
            ordinal[group] += 1
        birth = structure.add_knot(0, family, name)
        for u in group:
            structure.add_meeting(u, birth)

    watched = {_OWN: [], _SENDER: []}
    if parents:
        prospective = short | set(range(first_new, len(meets)))
        demand = Counter(u for group in _groups(meets, prospective) for u in group)
        for birth, group in enumerate(parents, start=first_new):
            size = len(group)
            loose[birth] = fresh = ration(demand[birth], max(3 - size, 0), 1)
            family = descent[birth]
            if family in watched:
                watched[family].append((structure.names[birth], fresh, size + fresh))

    return Round(
        len(meets),
        tuple(sorted(watched[_OWN], key=lambda reading: reading[0].order)),
        tuple(sorted(watched[_SENDER], key=lambda reading: reading[0].order)),
        sum(descent[u] == _OWN for u in short),
        sum(descent[u] == _SENDER for u in short),
        sum(descent[u] == _OWN for u in members),
        sum(descent[u] == _SENDER for u in members),
        sum(bool(family & _OWN) for family in descent[first_new:]),
        sender_site_owed_and_held,
        sender_site_live_neighbours,
    )


def grow(receiver: str | Start, sender: str | Start, d: int, law: str, *,
         rounds: int = 16, bound: int = 3000, join: str = "meeting",
         mark_after: int | None = None) -> list[Round]:
    """Read the complete rounds with waiting and release, including a last over-bound round."""
    if d < 1:
        raise ValueError("The join requires at least one step")
    if join not in {"meeting", "share", "shared"}:
        raise ValueError(f"Unrecognized join {join!r}")
    if isinstance(receiver, str):
        receiver = start(receiver)
    if isinstance(sender, str):
        sender = start(sender)
    ration = _ration(law)
    structure = _Structure(receiver, sender, d, "meeting" if join == "meeting" else "share")
    rows = []
    for completed in range(rounds):
        if completed == mark_after:
            structure.loose[structure.sender_site] += 1
        row = _advance(structure, ration)
        rows.append(row)
        if row.knots > bound:
            break
    return rows
