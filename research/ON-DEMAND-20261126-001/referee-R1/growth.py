"""Complete rounds from the live roster and a reader chosen among the start knots.

The two inputs are the holder sets and counts in the shared definitions of
RING-IN-BALANCE. Its ordinary ration, stall treatment and release rule are used.
Original numbers of places are needed for the first round's parent reading.
"""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import cached_property
from itertools import combinations

import networkx as nx


def joins(members, blocks):
    """Maximal pairwise-joinable sets lacking a common holder, then uncovered pairs."""
    member_set = set(members)
    blocks = {frozenset(block) & member_set for block in blocks}
    graph = nx.Graph()
    holders = defaultdict(set)
    for number, block in enumerate(blocks):
        if len(block) >= 2:
            for member in block:
                holders[member].add(number)
            graph.add_edges_from(combinations(sorted(block), 2))
    large = []
    uncovered = {tuple(sorted(pair)) for pair in graph.edges}
    for clique in nx.find_cliques(graph):
        if len(clique) < 3 or set.intersection(*(holders[m] for m in clique)):
            continue
        group = tuple(sorted(clique))
        large.append(group)
        uncovered.difference_update(combinations(group, 2))
    return sorted(large) + sorted(uncovered)


@dataclass
class Roster:
    loose: dict
    places: dict
    blocks: tuple

    @classmethod
    def from_counts(cls, loose, places, blocks):
        if not hasattr(loose, "items"):
            loose = dict(enumerate(loose))
        live = {k: h for k, h in loose.items() if h > 0}
        if any(k < 0 or places[k] < h for k, h in live.items()):
            raise ValueError("invalid counts or negative knot number")
        cut = {frozenset(block).intersection(live) for block in blocks}
        return cls(live, {k: places[k] for k in live},
                   tuple(sorted((b for b in cut if len(b) >= 2), key=sorted)))

    @classmethod
    def from_graph(cls, sizes, edges):
        """One pair per shared distinction, including repeated pairs."""
        sizes = dict(sizes) if hasattr(sizes, "items") else dict(enumerate(sizes))
        loose = sizes.copy()
        neighbours = defaultdict(set)
        for a, b in edges:
            if a == b:
                raise ValueError("two places in one knot cannot name the same distinction")
            loose[a] -= 1
            loose[b] -= 1
            neighbours[a].add(b)
            neighbours[b].add(a)
        if any(h < 0 for h in loose.values()):
            raise ValueError("more shared distinctions than places")
        return cls.from_counts(loose, sizes, neighbours.values())

    @classmethod
    def from_holdings(cls, holdings):
        owners = defaultdict(list)
        for k, places in enumerate(holdings):
            if len(places) != len(set(places)):
                raise ValueError("a distinction occurs twice at one knot")
            for distinction in places:
                owners[distinction].append(k)
        if any(len(pair) > 2 for pair in owners.values()):
            raise ValueError("a distinction has more than two holders")
        return cls.from_graph([len(places) for places in holdings],
                              (pair for pair in owners.values() if len(pair) == 2))

    def restrict(self, members):
        members = set(members)
        if not members <= self.loose.keys():
            raise ValueError("region contains a knot outside the live roster")
        return Roster.from_counts({k: self.loose[k] for k in sorted(members)},
                                  self.places, self.blocks)

    @cached_property
    def neighbours(self):
        near = {k: set() for k in self.loose}
        for block in self.blocks:
            for k in block:
                near[k].update(block)
        for k in near:
            near[k].discard(k)
        return near

    def steps_from(self, reader):
        found = {reader: 0}
        waiting = deque([reader])
        while waiting:
            k = waiting.popleft()
            for neighbour in self.neighbours[k] - found.keys():
                found[neighbour] = found[k] + 1
                waiting.append(neighbour)
        return found

    def within(self, reader, steps):
        return frozenset(k for k, count in self.steps_from(reader).items() if count <= steps)


@dataclass(frozen=True, slots=True)
class Birth:
    # Parents are positions in the preceding row. The start row uses sorted IDs.
    parents: tuple
    fresh: int
    ancestry: int
    description: tuple
    with_parents: tuple


@dataclass
class Growth:
    start: tuple
    rows: list
    end: str
    shortages: dict
    cap_births: int | None = None

    def views(self, reader=None, rounds=None):
        """Read each round, padding an ended growth with empty rounds."""
        if rounds is None:
            rounds = len(self.rows)
        if self.end == "cap" and rounds > len(self.rows):
            raise ValueError("a round omitted at the cap has no reading")
        answer = []
        for row in self.rows[:rounds]:
            first, second = Counter(), Counter()
            for birth in row:
                if reader is None or (birth.ancestry >> reader) & 1:
                    first[birth.description] += 1
                    second[birth.with_parents] += 1
            answer.append((first, second))
        answer.extend((Counter(), Counter()) for _ in range(rounds - len(answer)))
        return tuple(answer)

    def needed(self, reader, rounds):
        """Count the reader's births and the earlier births needed by them."""
        parents_of_later = set()
        count = 0
        total = 0
        for row in reversed(self.rows[:rounds]):
            needed = parents_of_later | {i for i, b in enumerate(row) if (b.ancestry >> reader) & 1}
            count += len(needed)
            total += len(row)
            parents_of_later = {p for i in needed for p in row[i].parents}
        return count, total

    def names(self, catalogue):
        """Count recursively named births; sharing a catalogue makes comparisons exact."""
        old = [-k - 1 for k in self.start]
        answer = []
        for row in self.rows:
            current = []
            for birth in row:
                key = tuple(sorted(old[p] for p in birth.parents))
                current.append(catalogue.setdefault(key, len(catalogue)))
            answer.append(Counter(current))
            old = current
        return answer


def grow(roster, rounds, law="nae", cap=None):
    if law not in ("nae", "parity"):
        raise ValueError("unknown knot law")
    start = tuple(sorted(roster.loose))
    slots = {k: i for i, k in enumerate(start)}
    old_labels = [("start", 0, 0, roster.places[k]) for k in start]
    ancestry = [1 << k for k in start]
    counts = [roster.loose[k] for k in start]
    blocks = [tuple(slots[k] for k in block) for block in roster.blocks]
    owed = joins(range(len(counts)), blocks)
    rows = []
    for number in range(1, rounds + 1):
        if not counts:
            return Growth(start, rows, "closed", {})
        demand = Counter(i for group in owed for i in group)
        deficiencies = {i: (demand[i], h) for i, h in enumerate(counts) if demand[i] > h}
        if deficiencies:
            if number != 1:
                raise AssertionError("the preceding ration was too small")
            return Growth(start, rows, "stall", {start[i]: v for i, v in deficiencies.items()})
        surplus = [h - demand[i] for i, h in enumerate(counts)]
        number_born = len(owed) + sum(surplus)
        if cap is not None and number_born > cap:
            return Growth(start, rows, "cap", {}, number_born)
        parents = list(owed)
        for i, h in enumerate(surplus):
            parents.extend([(i,)] * h)
        # All loose distinctions are used exactly once. A single birth therefore takes them all.
        closing = law == "parity" and number_born == 1
        children = defaultdict(list)
        for i, group in enumerate(parents):
            for parent in group:
                children[parent].append(i)
        owed = joins(range(number_born), children.values())
        next_demand = Counter(i for group in owed for i in group)
        row = []
        for i, group in enumerate(parents):
            p = len(group)
            fresh = 0 if closing else max(1, 3 - p, next_demand[i])
            desc = ("join" if p > 1 else "offshoot", p, fresh, p + fresh)
            old_desc = tuple(sorted(old_labels[parent] for parent in group))
            origin = 0
            for parent in group:
                origin |= ancestry[parent]
            row.append(Birth(group, fresh, origin, desc, (desc, old_desc)))
        rows.append(tuple(row))
        if closing:
            return Growth(start, rows, "closed", {})
        counts = [b.fresh for b in row]
        old_labels = [b.description for b in row]
        ancestry = [b.ancestry for b in row]
    return Growth(start, rows, "rounds", {})
