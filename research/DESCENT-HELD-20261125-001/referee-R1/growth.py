"""Complete rounds from the shared and study-specific frozen definitions."""

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class Law:
    ration: str
    treatment: str
    release: str = "RELEASE"
    extras: tuple = ()
    knot_law: str = "parity"
    form: str | None = None
    mismatch_swap: bool = False
    closing_swap: bool = False

    @classmethod
    def from_record(cls, record, **overrides):
        fields = {
            "ration": record["ration"],
            "treatment": record["treatment"],
            "release": record.get("release", "RELEASE"),
            "extras": tuple(record.get("extras", ())),
        }
        return cls(**(fields | overrides))


class Structure:
    def __init__(self, stars, barred=()):
        self.stars = [tuple(star) for star in stars]
        self.barred = set(barred)
        self.meetings = [set() for star in self.stars]
        self.holders = {}
        for knot, star in enumerate(self.stars):
            if len(set(star)) != len(star):
                raise ValueError("a distinction occupies more than one place in a knot")
            for distinction in star:
                old_holders = self.holders.get(distinction, ())
                if len(old_holders) > 1:
                    raise ValueError("a distinction has more than two holders")
                self.holders[distinction] = old_holders + (knot,)
                if old_holders:
                    other = old_holders[0]
                    self.meetings[knot].add(other)
                    self.meetings[other].add(knot)
        self.loose = {distinction for distinction, holders in self.holders.items()
                      if len(holders) == 1}
        if not self.barred <= self.loose:
            raise ValueError("a barred distinction is missing or shared")
        self.next_distinction = max(self.holders, default=-1) + 1

    def usable(self):
        roster = {}
        for distinction in self.loose - self.barred:
            knot, = self.holders[distinction]
            roster.setdefault(knot, set()).add(distinction)
        return {
            knot: [distinction for distinction in self.stars[knot] if distinction in places]
            for knot, places in roster.items()
        }


@dataclass(frozen=True)
class Birth:
    knot: int
    parents: tuple
    taken: tuple
    demand: int
    base_fresh: int
    added: int
    barred_at_birth: int
    parent_counts: tuple
    suppressed_added: int
    fresh: tuple


@dataclass(frozen=True)
class Round:
    births: tuple
    short: frozenset
    waited: frozenset
    retired: frozenset
    closing: bool
    status: str


@dataclass(frozen=True)
class Run:
    structure: Structure
    rounds: tuple
    status: str


def met_sets(meetings, members):
    """Distinct met sets, including those held by knots outside the roster."""
    return {frozenset(met) for others in meetings if len(met := others & members) >= 2}


def _bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def _maximal_joinable_sets(links):
    """Enumerate maximal pairwise joinable sets by pivoted search."""
    stack = [(0, (1 << len(links)) - 1, 0)]
    while stack:
        chosen, pending, excluded = stack.pop()
        if not pending:
            if not excluded:
                yield chosen
            continue
        if all(links[index] & pending == pending for index in _bits(pending)):
            if all(links[index] & pending != pending for index in _bits(excluded)):
                yield chosen | pending
            continue
        pivot = max(_bits(pending | excluded),
                    key=lambda index: ((links[index] ^ (1 << index)) & pending).bit_count())
        for index in _bits(pending & ~(links[pivot] ^ (1 << pivot))):
            bit = 1 << index
            neighbors = links[index] ^ bit
            stack.append((chosen | bit, pending & neighbors, excluded & neighbors))
            pending ^= bit
            excluded |= bit


def groups(meetings, members):
    met = met_sets(meetings, members)
    participants = sorted(set().union(*met))
    index_of = {knot: index for index, knot in enumerate(participants)}
    links = [0] * len(participants)
    held = [[] for _ in participants]
    for met_set in met:
        mask = sum(1 << index_of[knot] for knot in met_set)
        for index in _bits(mask):
            links[index] |= mask
            held[index].append(mask)
    covered = [0] * len(participants)
    found = []
    for mask in _maximal_joinable_sets(links):
        if mask.bit_count() < 3:
            continue
        indices = tuple(_bits(mask))
        if any(mask & witness == mask for witness in held[indices[0]]):
            continue
        found.append(tuple(participants[index] for index in indices))
        for index in indices:
            covered[index] |= mask
    for index, knot in enumerate(participants):
        later = links[index] & ~covered[index] & ~((2 << index) - 1)
        found.extend((knot, participants[other]) for other in _bits(later))
    return tuple(sorted(found))


def _ration(name, parents, demand):
    ordinary = max(demand, 3 - parents, 1)
    if name == "ORD":
        return ordinary
    if name.startswith("CAP-"):
        return min(ordinary, int(name[4:]))
    if name.startswith("RATION-"):
        return max(int(name[7:]), 3 - parents)
    if name == "ONE-FEWER":
        return min(ordinary, max(3 - parents, 0, ordinary - 1))
    if name in {"FLOOR0", "FLOOR1"}:
        return max(3 - parents, int(name[-1]))
    raise ValueError(f"unknown ration {name}")


def _target(counts, modulus, mismatch_swap):
    different = set(counts)
    if len(different) == 1:
        return (counts[0] + 1) % modulus
    if modulus == 5:
        return next(((count + 1) % 5 for count in sorted(different)
                     if all((count - other) % 5 < 3 for other in different)), None)
    if mismatch_swap and len(different) == 2:
        count, = (count for count in different if (count + 1) % 3 in different)
        return (count + 2) % 3
    return None


def complete_round(structure, law):
    """Apply one round in place, retaining the chosen names and birth record."""
    available = structure.usable()
    if not available:
        return Round((), frozenset(), frozenset(), frozenset(), False, "stopped")
    active_groups = groups(structure.meetings, set(available))
    owing = Counter(member for group in active_groups for member in group)
    short = frozenset(knot for knot in available if owing[knot] > len(available[knot]))
    if short and law.treatment == "STALL":
        return Round((), short, frozenset(), frozenset(), False, "stalled")
    waited = short if law.treatment == "CANCEL-WAIT" else frozenset()
    retired = short if law.treatment == "CANCEL-RETIRE" else frozenset()
    planned = []
    cancelled = Counter()
    for group in active_groups:
        if short.intersection(group):
            cancelled.update(group)
        else:
            planned.append((group, tuple(available[knot].pop() for knot in group)))
    newly_barred = set()
    kept_members = set()
    for knot in sorted(available):
        remaining = available[knot]
        if knot in waited:
            kept_members.add(knot)
            continue
        if knot in retired:
            newly_barred.update(remaining)
            continue
        keep = cancelled[knot] if law.release == "HOLD" and knot not in short else 0
        if keep:
            kept_members.add(knot)
        while len(remaining) > keep:
            taken = remaining.pop()
            if "NO-OFFSHOOT" in law.extras:
                newly_barred.add(taken)
            else:
                planned.append(((knot,), (taken,)))
    structure.barred.update(newly_barred)
    if not planned:
        return Round((), short, waited, retired, False, "changed" if newly_barred else "jammed")

    old_size = len(structure.stars)
    # Demand counts each planned new knot once even if its ration gives it no usable place.
    next_members = kept_members | set(range(old_size, old_size + len(planned)))
    # Old meetings among the provisional members never change during the birth.
    provisional = [others & next_members for others in structure.meetings]
    for knot, (parents, _) in enumerate(planned, old_size):
        provisional.append(set(parents) & next_members)
        for parent in parents:
            provisional[parent].add(knot)
    demand = Counter(member for group in groups(provisional, next_members) for member in group)
    closing = (law.knot_law == "parity" and len(planned) == 1
               and len(planned[0][1]) == len(structure.loose))
    fillers = "FILLERS" in law.extras
    barred_count = law.form in {"NEXT3-BARRED", "NEXT5-BARRED", "BB"}
    usable_form = law.form in {"NEXT3-PLACES (usable)", "PU"}
    modulus = 5 if law.form == "NEXT5-BARRED" else 3
    births = []
    for knot, (parents, taken) in enumerate(planned, old_size):
        required = demand[knot]
        closes = closing and not law.closing_swap
        base_fresh = 0 if closes else _ration(law.ration, len(parents), required)
        fixed_barred = max(base_fresh - required, 0) if fillers else 0
        counts = ()
        added = suppressed = 0
        if law.form is not None:
            if barred_count:
                counts = tuple(sum(place in structure.barred for place in structure.stars[parent])
                               % modulus for parent in parents)
            else:
                counts = tuple(len(structure.stars[parent]) % modulus for parent in parents)
            target = _target(counts, modulus, law.mismatch_swap)
            if target is not None:
                base_count = fixed_barred if barred_count else len(parents) + base_fresh
                needed = (target - base_count) % modulus
                if closes:
                    suppressed = needed
                else:
                    added = needed
        if usable_form:
            barred = max(base_fresh + added - required, 0) if fillers else 0
        else:
            barred = fixed_barred + added
        n_fresh = base_fresh + added
        fresh = tuple(range(structure.next_distinction, structure.next_distinction + n_fresh))
        structure.next_distinction += n_fresh
        if barred:
            structure.barred.update(fresh[-barred:])
        structure.stars.append(taken + fresh)
        structure.meetings.append(set(parents))
        for parent, distinction in zip(parents, taken):
            structure.meetings[parent].add(knot)
            structure.holders[distinction] = (parent, knot)
        structure.loose.difference_update(taken)
        structure.loose.update(fresh)
        structure.holders.update((distinction, (knot,)) for distinction in fresh)
        births.append(Birth(knot, parents, taken, required, base_fresh, added, barred, counts,
                            suppressed, fresh))
    return Round(tuple(births), short, waited, retired, closing, "changed")


def run(stars, law, rounds, max_knots=None, barred=()):
    structure = Structure(stars, barred)
    records = []
    status = "R"
    for _ in range(rounds):
        record = complete_round(structure, law)
        records.append(record)
        if record.status != "changed":
            status = record.status
            break
        if max_knots is not None and len(structure.stars) > max_knots:
            status = "N"
            break
    return Run(structure, tuple(records), status)
