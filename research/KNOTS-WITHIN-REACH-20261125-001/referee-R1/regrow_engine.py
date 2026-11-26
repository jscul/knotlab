"""Taking-free complete rounds from the frozen shared and taking definitions.

The shared definitions give met sets, complete rounds, and rations. Section 2
of the study of parts that meet again gives names and implied parity closure.
The arrays retain the places, holders, parents, and round of each birth.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations


# Ration, ration count, treatment of a short member, filler rule.
LAWS = {
    "L0": ("ordinary", 0, "stall", False),
    "L1": ("cap", 3, "wait", False),
    "L2": ("cap", 3, "wait", True),
    "L3": ("floor", 1, "retire", False),
    "L4": ("floor", 1, "offshoot", False),
    "L5": ("floor", 1, "wait", False),
    "L6": ("cap", 3, "retire", False),
    "L7": ("cap", 3, "offshoot", False),
    "L8": ("fixed", 3, "stall", False),
    "L9": ("ordinary", 0, "retire", False),
    "L10": ("cap", 2, "retire", False),
    "L11": ("cap", 4, "retire", False),
}


def connected_parts(neighbors):
    pending = set(neighbors)
    while pending:
        start = pending.pop()
        part = [start]
        for knot in part:
            new = pending.intersection(neighbors[knot])
            pending.difference_update(new)
            part.extend(new)
        yield part


def maximal_cliques(knot, candidates, excluded, neighbors):
    if not candidates and not excluded:
        yield frozenset(knot)
        return
    pivot = max(candidates | excluded, key=lambda v: len(candidates & neighbors[v]))
    for v in candidates - neighbors[pivot]:
        yield from maximal_cliques(
            knot + (v,), candidates & neighbors[v], excluded & neighbors[v], neighbors
        )
        candidates.remove(v)
        excluded.add(v)


@dataclass
class Roster:
    met_sets: set[frozenset[int]]
    neighbors: dict[int, set[int]]

    @classmethod
    def read(cls, meeting, members):
        met_by_knot = defaultdict(set)
        for member in members:
            for common in meeting[member]:
                met_by_knot[common].add(member)
        met_sets = {frozenset(row) for row in met_by_knot.values() if len(row) >= 2}
        neighbors = {member: set() for member in members}
        for row in met_sets:
            for knot in row:
                neighbors[knot].update(row)
        for knot, others in neighbors.items():
            others.discard(knot)
        return cls(met_sets, neighbors)

    def groups(self):
        # A clique that does not fit in any one met set has no superset
        # that fits. It suffices to examine the maximal cliques.
        met_at = defaultdict(list)
        for row in self.met_sets:
            for member in row:
                met_at[member].append(row)
        larger = []
        covered = set()
        for member, neighbors in self.neighbors.items():
            later = {v for v in neighbors if v > member}
            if not later:
                continue
            for clique in maximal_cliques((member,), later, neighbors - later, self.neighbors):
                if len(clique) >= 3 and not any(clique <= row for row in met_at[member]):
                    group = tuple(sorted(clique))
                    larger.append(group)
                    covered.update(combinations(group, 2))
        pairs = {
            (member, other)
            for member, neighbors in self.neighbors.items()
            for other in neighbors
            if member < other
        }
        return sorted(larger) + sorted(pairs - covered)


class Growth:
    def __init__(self, stars, law="L0", knot_law="nae", *, hold=False):
        self.ration, self.ration_count, self.treatment, self.fillers = LAWS[law]
        if knot_law not in {"nae", "parity"}:
            raise ValueError(f"Unknown knot law {knot_law}")
        self.parity = knot_law == "parity"
        self.hold = hold
        self.round = 0
        self.places = [tuple(sorted(row)) for row in stars]
        self.parents = [()] * len(stars)
        self.birth_rounds = [0] * len(stars)
        self.demand = [None] * len(stars)
        self.holders = {}
        self.meeting = [set() for _ in stars]
        for knot, row in enumerate(self.places):
            for distinction in row:
                holders = self.holders.setdefault(distinction, [])
                holders.append(knot)
                if len(holders) == 2:
                    older, newer = holders
                    self.meeting[older].add(newer)
                    self.meeting[newer].add(older)
                elif len(holders) > 2:
                    raise ValueError("This engine requires at most two holders")
        self.members = {}
        for knot, row in enumerate(self.places):
            loose = tuple(d for d in row if len(self.holders[d]) == 1)
            if loose:
                self.members[knot] = loose
        self.barred = set()
        self._next_distinction = max(self.holders, default=-1) + 1
        self._component = [None] * len(stars)
        self._loose_count = {}
        for component, part in enumerate(connected_parts(dict(enumerate(self.meeting)))):
            for knot in part:
                self._component[knot] = component
            self._loose_count[component] = sum(len(self.members.get(knot, ())) for knot in part)
        self.status = "running" if self.members else "stopped"

    def roster(self):
        return Roster.read(self.meeting, self.members)

    def _fresh_count(self, parents, demand):
        ordinary = max(demand, 3 - parents, 1)
        if self.ration == "ordinary":
            return ordinary
        if self.ration == "cap":
            return min(ordinary, self.ration_count)
        return max(3 - parents, self.ration_count)

    def step(self):
        if self.status != "running":
            return 0
        groups = self.roster().groups()
        owes = Counter(u for group in groups for u in group)
        short = {u for u, ds in self.members.items() if owes[u] > len(ds)}
        if short and self.treatment == "stall":
            self.status = "stalled"
            return 0

        joins = [group for group in groups if not short.intersection(group)]
        used = Counter()
        births = []
        for group in joins:
            taken = tuple(self.members[u][used[u]] for u in group)
            births.append((group, taken))
            used.update(group)

        kept = {}
        for u in sorted(self.members):
            ds = self.members[u]
            if u in short:
                if self.treatment == "wait":
                    kept[u] = ds
                    continue
                if self.treatment == "retire":
                    self.barred.update(ds)
                    continue
            elif self.hold and owes[u] > used[u]:
                kept[u] = ds[used[u]:owes[u]]
                used[u] = owes[u]
            births.extend(((u,), (d,)) for d in ds[used[u]:])

        if not births:
            self.members = kept
            self.status = "jammed" if kept else "stopped"
            return 0

        # Implied parity is tested before adding any holder. Over GF(2),
        # a sum of old rules without shared distinctions selects all or none
        # of the knots in each holder component. Its remaining distinctions
        # are exactly that component's loose ones, barred ones included.
        implied = []
        if self.parity:
            implied = [
                self._loose_count[self._component[parents[0]]] == len(taken)
                for parents, taken in births
            ]

        first = len(self.places)
        temporary_members = set(kept)
        for i, (parents, taken) in enumerate(births, start=first):
            self.meeting.append(set(parents))
            for parent, distinction in zip(parents, taken, strict=True):
                self.meeting[parent].add(i)
                self.holders[distinction].append(i)
            temporary_members.add(i)

        next_groups = Roster.read(self.meeting, temporary_members).groups()
        demands = Counter(u for group in next_groups for u in group)
        self.members = kept
        self.round += 1
        for offset, (parents, taken) in enumerate(births):
            u = first + offset
            demand = demands[u]
            fresh_count = self._fresh_count(len(parents), demand)
            if self.parity and implied[offset]:
                fresh_count = 0
            usable_count = min(fresh_count, demand) if self.fillers else fresh_count
            fresh = tuple(range(self._next_distinction, self._next_distinction + fresh_count))
            self._next_distinction += fresh_count
            self.barred.update(fresh[usable_count:])
            for distinction in fresh:
                self.holders[distinction] = [u]
            if usable_count:
                self.members[u] = fresh[:usable_count]
            self.places.append(taken + fresh)
            self.parents.append(parents)
            self.birth_rounds.append(self.round)
            self.demand.append(demand)
            component = self._component[parents[0]]
            self._component.append(component)
            self._loose_count[component] += fresh_count - len(taken)
        if not self.members:
            self.status = "stopped"
        return len(births)
