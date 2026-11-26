"""Ordinary complete rounds under not-all-equal, from the frozen joining rule.

Sources: RING-IN-BALANCE-20261123-001/definitions.md, "One complete round",
and PARTS-MEET-AGAIN-20261124-001/definitions.md, 1.3 and 2.1. No study
code is imported. Each usable loose distinction is taken once. Thus after
paying a full round with no short member the common knots for the new roster
are exactly its parents, each meeting precisely the children it contributed
to. Recording those sets gives the literal next join test. A short member
raises an error; this comparison covers only starts with no shortage.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations


def groups(met_sets):
    """Maximal pairwise joinable sets with no common knot, then uncovered pairs."""
    partners = defaultdict(set)
    meeting_at = defaultdict(list)
    pairs = set()
    for members in set(frozenset(m) for m in met_sets if len(m) >= 2):
        for member in members:
            meeting_at[member].append(members)
        for left, right in combinations(sorted(members), 2):
            partners[left].add(right)
            partners[right].add(left)
            pairs.add((left, right))

    # Extend each smallest member to maximal pairwise joinable sets.
    # 'earlier' rules out a nonmaximal answer and duplicate enumeration.
    larger_groups = []

    def extend(chosen, available, earlier):
        if not available:
            if not earlier and len(chosen) >= 3:
                if not any(chosen <= m for m in meeting_at[min(chosen)]):
                    larger_groups.append(tuple(sorted(chosen)))
            return
        pivot = max(available | earlier, key=lambda u: len(available & partners[u]))
        for member in sorted(available - partners[pivot]):
            extend(chosen | {member}, available & partners[member], earlier & partners[member])
            available.remove(member)
            earlier.add(member)

    for member, others in partners.items():
        if len(others) >= 2:
            later = {u for u in others if u > member}
            if len(later) >= 2:
                extend({member}, later, others - later)
    for group in larger_groups:
        pairs.difference_update(combinations(group, 2))
    return sorted(larger_groups) + sorted(pairs)


@dataclass(frozen=True, slots=True)
class Birth:
    number: int
    parents: tuple
    kind: str
    fresh: int
    places: int
    sig0: tuple
    sig1: tuple


class Ordinary:
    def __init__(self, stars):
        self.start = tuple(tuple(knot) for knot in stars)
        holders = defaultdict(list)
        for knot, places in enumerate(self.start):
            if len(places) < 3 or len(set(places)) != len(places):
                raise ValueError("A start knot needs at least three distinct places.")
            for distinction in places:
                holders[distinction].append(knot)
        self.start_neighbors = [set() for _ in self.start]
        for owners in holders.values():
            for a, b in combinations(owners, 2):
                self.start_neighbors[a].add(b)
                self.start_neighbors[b].add(a)
        self.holdings = {
            k: count for k, places in enumerate(self.start)
            if (count := sum(len(holders[d]) == 1 for d in places))
        }
        self.joins = groups([self.holdings.keys() & met for met in self.start_neighbors])
        self.signatures = {k: ("start", 0, 0, len(self.start[k])) for k in self.holdings}
        self.next_number = len(self.start)

    def step(self):
        parents = list(self.joins)
        owing = Counter(member for group in self.joins for member in group)
        for member, held in self.holdings.items():
            if owing[member] > held:
                raise ValueError(f"Short member {member}: owes {owing[member]}, holds {held}.")
            parents.extend([(member,)] * (held - owing[member]))

        children = defaultdict(list)
        for knot, old in enumerate(parents, self.next_number):
            for parent in old:
                children[parent].append(knot)
        self.joins = groups(children.values())
        demand = Counter(member for group in self.joins for member in group)

        births = []
        for knot, old in enumerate(parents, self.next_number):
            number_of_parents = len(old)
            fresh = max(1, 3 - number_of_parents, demand[knot])
            places = number_of_parents + fresh
            kind = "offshoot" if number_of_parents == 1 else "join"
            sig0 = (kind, number_of_parents, fresh, places)
            sig1 = sig0 + (tuple(sorted(self.signatures[p] for p in old)),)
            births.append(Birth(knot, old, kind, fresh, places, sig0, sig1))
        self.holdings = {b.number: b.fresh for b in births}
        self.signatures = {b.number: b.sig0 for b in births}
        self.next_number += len(births)
        return births


def row_start(length):
    """A row, giving each knot the least loose count for arity and first joins."""
    if length < 2:
        raise ValueError("A row needs at least two knots.")
    result = []
    next_distinction = length - 1
    for i in range(length):
        shared = [j for j in (i - 1, i) if 0 <= j < length - 1]
        first_joins = int(i >= 2) + int(i < length - 2)
        loose = max(1, 3 - len(shared), first_joins)
        result.append(shared + list(range(next_distinction, next_distinction + loose)))
        next_distinction += loose
    return result


def ring_start(loose_counts):
    """A ring with the given loose count per knot, in cyclic order."""
    n = len(loose_counts)
    if n < 3:
        raise ValueError("A ring needs at least three knots.")
    result = []
    next_distinction = n
    for i, loose in enumerate(loose_counts):
        result.append([(i - 1) % n, i] + list(range(next_distinction, next_distinction + loose)))
        next_distinction += loose
    return result
