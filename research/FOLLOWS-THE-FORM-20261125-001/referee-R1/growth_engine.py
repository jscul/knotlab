"""Regrow FF starts from FF 1–5b, BD2 1–2, FD 1–3, and SD 1–8.

Round records give the births, the roster before the round, and its owing.
The result supplies the FF 5 and FF 5b counters without distinction names.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
from math import comb


PAIR_LIMIT = 20_000
GROUP_LIMIT = 20_000
BIRTH_LIMIT = 20_000
DISTINCTION_LIMIT = 400_000
INCIDENCE_LIMIT = 2_000_000
CLIQUE_LIMIT = 200_000


@dataclass(frozen=True, slots=True)
class Birth:
    knot: int
    kind: str
    parents: tuple
    given: tuple
    takes: tuple
    fresh: tuple
    demand: int
    ancestry: int

    @property
    def places(self):
        return self.given + self.takes + self.fresh

    @property
    def entry(self):
        return (self.kind, len(self.parents), len(self.places), len(self.fresh), len(self.takes))


@dataclass(frozen=True, slots=True)
class Round:
    births: tuple
    roster: dict
    owing: dict
    short: frozenset

    @property
    def own(self):
        return Counter(birth.entry for birth in self.births if birth.ancestry == 1)

    @property
    def wider(self):
        return Counter(birth.entry + (birth.ancestry == 1,) for birth in self.births if birth.ancestry & 1)

    @property
    def second_only(self):
        return Counter(birth.entry for birth in self.births if birth.ancestry == 2)


@dataclass(frozen=True, slots=True)
class Run:
    rounds: tuple
    knots: tuple
    final_members: frozenset
    stop: str | None
    guard: dict | None

    @property
    def own(self):
        return tuple(record.own for record in self.rounds)

    @property
    def wider(self):
        return tuple(record.wider for record in self.rounds)

    @property
    def second_only(self):
        return tuple(record.second_only for record in self.rounds)


def build_start(first, second=None, *, unlinked=False):
    """Build the linked, bare, or unlinked start of FF 2."""
    first_knots = [tuple(places) for places in first["knots"]]
    link = len(set().union(*map(set, first_knots)))
    first_knots[first["site"]] += (link,)
    if second is None:
        return first_knots, len(first_knots)
    second_knots = [tuple(place + link + 1 for place in places) for places in second["knots"]]
    new_name = max(max(places) for places in second_knots) + 1 if unlinked else link
    second_knots[second["at"]] += (new_name,)
    return first_knots + second_knots, len(first_knots)


class Guard(Exception):
    def __init__(self, what, value, where):
        self.record = dict(what=what, value=value, where=where)


def _roster(holders, barred):
    roster = defaultdict(list)
    for distinction, holding in holders.items():
        if len(holding) == 1 and distinction not in barred:
            roster[holding[0]].append(distinction)
    return {knot: tuple(sorted(usable)) for knot, usable in roster.items()}


def _maximal_cliques(neighbors):
    """Enumerate maximal pairwise-joinable sets, with pivoting."""
    def visit(clique, remaining, seen):
        if not remaining and not seen:
            yield clique
            return
        pivot = max(remaining | seen, key=lambda knot: len(remaining & neighbors[knot]))
        for knot in remaining - neighbors[pivot]:
            compatible = neighbors[knot]
            yield from visit(clique + (knot,), remaining & compatible, seen & compatible)
            remaining.remove(knot)
            seen.add(knot)

    yield from visit((), set(neighbors), set())


def _groups(holders, members, where):
    """Form SD's groups from the holder lists restricted to this roster."""
    met_by_knot = defaultdict(set)
    for holding in holders.values():
        if len(holding) > 1:
            met = members.intersection(holding)
            if met:
                # One witness alone can exceed the pair limit. Avoid copying
                # a large set into the records of all of its other holders.
                largest_met = len(met) - (len(met) == len(holding))
                if comb(largest_met, 2) > PAIR_LIMIT:
                    raise Guard("pairs", comb(largest_met, 2), where)
                for knot in holding:
                    met_by_knot[knot].update(met - {knot})
    met_sets = {tuple(sorted(met)) for met in met_by_knot.values() if len(met) > 1}

    met_sets_by_member = defaultdict(set)
    neighbors = defaultdict(set)
    pair_count = 0
    for index, met in enumerate(sorted(met_sets)):
        pairs_in_met = comb(len(met), 2)
        if pairs_in_met > PAIR_LIMIT:
            raise Guard("pairs", pairs_in_met, where)
        for member in met:
            met_sets_by_member[member].add(index)
        for left, right in combinations(met, 2):
            if right not in neighbors[left]:
                neighbors[left].add(right)
                neighbors[right].add(left)
                pair_count += 1
        if pair_count > PAIR_LIMIT:
            raise Guard("pairs", pair_count, where)

    larger = []
    covered_pairs = set()
    if neighbors:
        for count, clique in enumerate(_maximal_cliques(neighbors), start=1):
            if count > CLIQUE_LIMIT:
                raise Guard("cliques", count, where)
            if len(clique) < 3:
                continue
            ordered = tuple(sorted(clique))
            common = set.intersection(*(met_sets_by_member[knot] for knot in ordered))
            if not common:
                larger.append(ordered)
                covered_pairs.update(combinations(ordered, 2))
                if len(larger) > GROUP_LIMIT:
                    raise Guard("groups", len(larger), where)
    pairs = {(left, right) for left, met in neighbors.items() for right in met if left < right} - covered_pairs
    if len(larger) + len(pairs) > GROUP_LIMIT:
        raise Guard("groups", len(larger) + len(pairs), where)
    return sorted(larger) + sorted(pairs)


def _met_candidate(parents, knots, holders):
    """Return MET-SOLE's single extra distinction, as a possibly empty tuple."""
    meeting_sets = []
    for parent in parents:
        meets = {other for place in knots[parent] for other in holders[place]}
        meets.remove(parent)
        meeting_sets.append(meets)
    sources = set.intersection(*meeting_sets)
    excluded = {place for parent in parents for place in knots[parent]}
    candidates = set()
    for source in sources:
        for place in knots[source]:
            if place not in excluded and len(holders[place]) >= 2:
                candidates.add(place)
                if len(candidates) > 1:
                    return ()
    return tuple(candidates)


def _mask(places):
    return sum(1 << place for place in places)


def _reduce(mask, basis):
    while mask:
        pivot = mask.bit_length() - 1
        row = basis.get(pivot)
        if row is None:
            break
        mask ^= row
    return mask


def _insert(places, basis):
    remainder = _reduce(_mask(places), basis)
    if remainder:
        basis[remainder.bit_length() - 1] = remainder


def _round(knots, ancestry, holders, barred, basis, ration, treatment, take):
    roster = _roster(holders, barred)
    groups = _groups(holders, set(roster), "roster")
    owing = Counter(parent for group in groups for parent in group)
    short = frozenset(knot for knot, usable in roster.items() if owing[knot] > len(usable))
    retired = set()
    waiting = set()
    if treatment == "CANCEL-RETIRE":
        retired = {place for knot in short for place in roster[knot]}
    if treatment == "CANCEL-WAIT":
        waiting = set(short)

    births = []
    given_count = Counter()
    for group in groups:
        if short.isdisjoint(group):
            given = tuple(roster[parent][given_count[parent]] for parent in group)
            births.append(("j", group, given))
            given_count.update(group)
    for parent, usable in sorted(roster.items()):
        if parent not in short or treatment == "CANCEL-OFFSHOOT":
            births.extend(("o", (parent,), (place,)) for place in usable[given_count[parent]:])
    if len(births) > BIRTH_LIMIT:
        raise Guard("births", len(births), "births")

    after = holders.copy()
    # All candidates are from the start of the round. Every prospective
    # birth is in the demand roster, before any fresh count is assigned.
    inputs = []
    for knot, (_, parents, given) in enumerate(births, start=len(knots)):
        taken = _met_candidate(parents, knots, holders) if take else ()
        inputs.append(taken)
        for place in given + taken:
            after[place] += (knot,)

    demand_members = waiting.union(range(len(knots), len(knots) + len(births)))
    demand = Counter(member for group in _groups(after, demand_members, "demand") for member in group)

    records = []
    next_distinction = max(holders, default=-1) + 1
    for knot, ((kind, parents, given), taken) in enumerate(zip(births, inputs), start=len(knots)):
        places = given + taken
        floor = max(3 - len(places), 1)
        fresh_count = floor
        if ration != "FLOOR1":
            fresh_count = max(floor, demand[knot])
            if ration == "CAP-3":
                fresh_count = min(fresh_count, 3)
        if basis is not None and _reduce(_mask(places), basis) == 0:
            fresh_count = 0

        side = 0
        for parent in parents:
            side |= ancestry[parent]
        fresh = tuple(range(next_distinction, next_distinction + fresh_count))
        next_distinction += fresh_count
        for place in fresh:
            after[place] = (knot,)
        records.append(Birth(knot, kind, parents, given, taken, fresh, demand[knot], side))

    if len(after) > DISTINCTION_LIMIT:
        raise Guard("distinctions", len(after), "births")
    incidence_count = sum(map(len, after.values()))
    if incidence_count > INCIDENCE_LIMIT:
        raise Guard("incidences", incidence_count, "births")
    return Round(tuple(records), roster, dict(owing), short), after, retired


def grow(knots, first_count, *, ration, treatment, take=None, knot_law="nae", max_rounds=9, knot_limit=3000):
    """Read complete rounds through the frozen bounds, including empty rounds."""
    if ration not in {"FLOOR1", "CAP-3", "ORD"}:
        raise ValueError(f"Unknown ration {ration!r}")
    if treatment not in {"CANCEL-RETIRE", "CANCEL-OFFSHOOT", "CANCEL-WAIT"}:
        raise ValueError(f"Unknown treatment {treatment!r}")
    if take not in {None, "none", "sole", "MET-SOLE"}:
        raise ValueError(f"Unknown taking rule {take!r}")
    if knot_law not in {"nae", "parity"}:
        raise ValueError(f"Unknown knot law {knot_law!r}")
    take = take in {"sole", "MET-SOLE"}

    knots = list(map(tuple, knots))
    ancestry = [1] * first_count + [2] * (len(knots) - first_count)
    initial_holders = defaultdict(list)
    basis = {} if knot_law == "parity" else None
    for knot, places in enumerate(knots):
        for place in places:
            initial_holders[place].append(knot)
        if basis is not None:
            _insert(places, basis)
    holders = {place: tuple(holding) for place, holding in initial_holders.items()}
    barred = set()
    rounds = []
    stop = None
    guard = None
    for index in range(max_rounds):
        try:
            record, after, retired = _round(knots, ancestry, holders, barred, basis, ration, treatment, take)
        except Guard as error:
            stop = "guard"
            guard = dict(error.record, round=index + 1)
            break
        rounds.append(record)
        holders = after
        barred.update(retired)
        for birth in record.births:
            knots.append(birth.places)
            ancestry.append(birth.ancestry)
            if basis is not None:
                _insert(birth.places, basis)
        if len(knots) > knot_limit:
            stop = "knots"
            break

    return Run(tuple(rounds), tuple(knots), frozenset(_roster(holders, barred)), stop, guard)
