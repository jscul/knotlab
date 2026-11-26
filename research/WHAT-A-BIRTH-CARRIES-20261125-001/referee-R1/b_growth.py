"""Replay the growth rule from SD, FD and BD2 without the recorded engine."""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from functools import cached_property
from itertools import combinations
from math import comb


LIMITS = {
    "pairs": 20_000,
    "groups": 20_000,
    "births": 20_000,
    "distinctions": 400_000,
    "incidences": 2_000_000,
    "cliques": 200_000,
}


@dataclass(frozen=True)
class Law:
    ration: str
    treatment: str
    take: str | None
    knot_law: str
    choice: str | None = None


@dataclass(frozen=True)
class Knot:
    places: tuple
    parents: tuple = ()
    kind: str = "start"
    made: int = 0
    fresh: tuple = ()


def holders_of(places):
    holders = defaultdict(set)
    for knot, distinctions in enumerate(places):
        for distinction in distinctions:
            holders[distinction].add(knot)
    return dict(holders)


@dataclass(frozen=True)
class State:
    number: int
    knots: tuple
    bars: frozenset = frozenset()

    @cached_property
    def holders(self):
        return holders_of(knot.places for knot in self.knots)

    @cached_property
    def member_loose(self):
        loose = defaultdict(list)
        for distinction, holders in self.holders.items():
            if len(holders) == 1 and distinction not in self.bars:
                loose[next(iter(holders))].append(distinction)
        return {knot: tuple(sorted(loose[knot])) for knot in sorted(loose)}

    @cached_property
    def met(self):
        met = [set() for _ in self.knots]
        for holders in self.holders.values():
            for knot in holders:
                met[knot].update(holders - {knot})
        return met

    def loose_counts(self, knot):
        usable = len(self.member_loose.get(knot, ()))
        barred = sum(d in self.bars for d in self.knots[knot].places)
        return usable, barred


@dataclass
class Roster:
    members: tuple
    met_sets: dict
    partners: dict

    @cached_property
    def parts(self):
        return components(self.partners)


def components(partners):
    remaining = set(partners)
    parts = []
    while remaining:
        part = {min(remaining)}
        pending = list(part)
        while pending:
            new = partners[pending.pop()] - part
            part.update(new)
            pending.extend(new)
        remaining.difference_update(part)
        parts.append(tuple(sorted(part)))
    return parts


def roster_for(holders, members, counts=None, where=None):
    members = tuple(sorted(members))
    member_set = set(members)
    met_members = defaultdict(set)
    incidences = 0
    largest_sharing = 0
    relevant = []
    for sharing in holders.values():
        if len(sharing) <= 1:
            continue
        represented = sharing & member_set
        if not represented:
            continue
        largest_sharing = max(largest_sharing, len(represented))
        incidences += (len(sharing) - 1) * len(represented)
        relevant.append((sharing, represented))
    if counts is not None:
        counts.note("incidences", incidences, where)
        # The sharing bound excludes a member that supplies the met set.
        counts.check("pairs", comb(max(largest_sharing - 1, 0), 2), where)
    for sharing, represented in relevant:
        for knot in sharing:
            met_members[knot].update(represented - {knot})
    met_sets = {knot: frozenset(met) for knot, met in met_members.items() if len(met) >= 2}
    if counts is not None:
        counts.check("pairs", comb(max((len(met) for met in met_sets.values()), default=0), 2), where)
    partners = {member: set() for member in members}
    number_of_pairs = 0
    for met in set(met_sets.values()):
        for a, b in combinations(met, 2):
            if b not in partners[a]:
                partners[a].add(b)
                partners[b].add(a)
                number_of_pairs += 1
                if counts is not None and number_of_pairs > counts.limits["pairs"]:
                    counts.note("pairs", number_of_pairs, where)
    if counts is not None:
        counts.note("pairs", number_of_pairs, where)
    return Roster(members, met_sets, partners)


def maximal_joinable(partners, chosen=frozenset(), possible=None, excluded=None):
    """List maximal pairwise joinable sets of at least two members."""
    if possible is None:
        possible = {member for member, others in partners.items() if others}
        excluded = set()
    if not possible and not excluded:
        if len(chosen) >= 2:
            yield chosen
        return
    pivot = max(possible | excluded, key=lambda u: len(possible & partners[u]))
    for member in sorted(possible - partners[pivot]):
        yield from maximal_joinable(
            partners,
            chosen | {member},
            possible & partners[member],
            excluded & partners[member],
        )
        possible.remove(member)
        excluded.add(member)


def groups_for(roster, counts, where):
    covered = set()
    groups = []
    cliques = sum(not partners for partners in roster.partners.values())
    counts.note("cliques", cliques, where)
    for members in maximal_joinable(roster.partners):
        cliques += 1
        if cliques > counts.limits["cliques"]:
            counts.note("cliques", cliques, where)
        if len(members) >= 3 and all(not members <= met for met in roster.met_sets.values()):
            ordered = tuple(sorted(members))
            groups.append(ordered)
            covered.update(combinations(ordered, 2))
    counts.note("cliques", cliques, where)
    pairs = (
        (a, b)
        for a, partners in roster.partners.items()
        for b in partners
        if a < b and (a, b) not in covered
    )
    result = tuple(sorted(groups) + sorted(pairs))
    counts.note("groups", len(result), where)
    return result


class CountLimit(Exception):
    pass


@dataclass
class Counts:
    limits: dict = field(default_factory=lambda: dict(LIMITS))
    peaks: dict = field(default_factory=lambda: dict.fromkeys(LIMITS, 0))

    def check(self, count, value, where):
        if value > self.limits[count]:
            raise CountLimit(count, value, where)

    def note(self, count, value, where=None):
        self.peaks[count] = max(self.peaks[count], value)
        self.check(count, value, where)


@dataclass(frozen=True)
class Birth:
    knot: int
    kind: str
    parents: tuple
    loose: tuple
    takes: tuple
    candidates: dict
    demand: int
    demand_partners: tuple
    owing: int | None
    implied: bool
    fresh: tuple

    @property
    def inputs(self):
        return self.loose + self.takes


@dataclass
class Step:
    roster: Roster
    groups: tuple
    owing: Counter
    short: tuple
    retired: tuple
    waiting: tuple
    kept: dict
    demand_roster: Roster
    demand_groups: tuple
    births: dict


@dataclass
class Run:
    states: list
    steps: dict
    peaks: dict
    stop: str | None = None
    guard: dict | None = None


def source_candidates(state, parents, kind, rule, other_parts):
    if rule is None:
        return {}
    parent = parents[0]
    excluded = set()
    if rule.startswith("MET"):
        suppliers = set.intersection(*(state.met[member] for member in parents))
        excluded.update(d for member in parents for d in state.knots[member].places)
    elif kind == "join":
        return {}
    elif rule in {"STEPS1-SOLE", "STEPS2-SOLE"}:
        suppliers = set(state.knots[parent].parents)
        if rule == "STEPS2-SOLE":
            suppliers = {a for member in suppliers for a in state.knots[member].parents}
        excluded.update(state.knots[parent].places)
    elif rule == "J-EACH-PART":
        suppliers = other_parts[parent]
    else:
        raise ValueError(rule)

    candidates = defaultdict(set)
    for supplier in suppliers:
        for distinction in state.knots[supplier].places:
            if distinction not in excluded and len(state.holders[distinction]) >= 2:
                candidates[distinction].add(supplier)
    return {d: tuple(sorted(candidates[d])) for d in sorted(candidates)}


def choose(candidates, law):
    if law.take == "J-EACH-PART" or len(candidates) == 1:
        return tuple(candidates)
    if law.take == "MET" and candidates:
        if law.choice == "OLDEST":
            return (min(candidates),)
        if law.choice == "NEWEST":
            return (max(candidates),)
        raise ValueError(law.choice)
    return ()


def bit_vector(distinctions):
    return sum(1 << d for d in distinctions)


def reduce(vector, basis):
    while vector:
        pivot = vector.bit_length() - 1
        if pivot not in basis:
            break
        vector ^= basis[pivot]
    return vector


def parity_basis(knots):
    basis = {}
    for knot in knots:
        vector = reduce(bit_vector(knot.places), basis)
        if vector:
            basis[vector.bit_length() - 1] = vector
    return basis


def ration_count(ration, kind, places, demand, owing):
    floor = max(3 - places, 1)
    ordinary = max(demand, floor)
    if ration == "ORD":
        return ordinary
    if ration == "CAP-3":
        return min(ordinary, 3)
    if kind == "join" or ration == "FLOOR1":
        return floor
    if ration == "PARENT-OWING":
        return max(2, owing)
    if ration == "PARENT-OWING-CAP3":
        return min(max(2, owing), 3)
    if ration == "PARENT-OWING-CAP4":
        return min(max(2, owing), 4)
    if ration == "PARENT-OWING-1":
        return max(1, owing)
    if ration == "PARENT-OWING-PLAIN":
        return max(owing, floor)
    if ration == "OFFSHOOT-TWO":
        return 2
    if ration == "OFFSHOOT-THREE":
        return 3
    if ration == "MOD2":
        return 2 + owing % 2
    raise ValueError(ration)


def plan_births(state, groups, owing, short, law):
    loose = state.member_loose
    available = {member: iter(distinctions) for member, distinctions in loose.items()}
    kept_groups = (group for group in groups if short.isdisjoint(group))
    plan = [("join", group, tuple(next(available[member]) for member in group)) for group in kept_groups]
    retired = []
    waiting = []
    kept = {}
    for member, unused in available.items():
        unused = tuple(unused)
        if member in short:
            if law.treatment == "CANCEL-WAIT":
                waiting.append(member)
                kept[member] = unused
                continue
            if law.treatment == "CANCEL-RETIRE":
                retired.append(member)
                continue
            if law.treatment == "SHORT-BY":
                count = min(len(unused), owing[member] - len(unused))
                if count < len(unused):
                    kept[member] = unused[count:]
                unused = unused[:count]
            elif law.treatment != "CANCEL-OFFSHOOT":
                raise ValueError(law.treatment)
        plan.extend(("offshoot", (member,), (d,)) for d in unused)
    return plan, retired, waiting, kept


def advance(state, law, counts):
    old_roster = roster_for(state.holders, state.member_loose, counts, "roster")
    groups = groups_for(old_roster, counts, "roster")
    owing = Counter(member for group in groups for member in group)
    short = frozenset(member for member, n in owing.items() if n > len(state.member_loose[member]))
    plan, retired, waiting, kept = plan_births(state, groups, owing, short, law)
    counts.note("births", len(plan))
    new_knots = len(state.knots)
    other_parts = {}
    if law.take == "J-EACH-PART":
        for part in old_roster.parts:
            other_parts.update({member: set(old_roster.members) - set(part) for member in part})
    proposals = {}
    demand_holders = {d: set(holders) for d, holders in state.holders.items()}
    for knot, (kind, parents, loose) in enumerate(plan, new_knots):
        candidates = source_candidates(state, parents, kind, law.take, other_parts)
        taken = choose(candidates, law)
        proposals[knot] = (kind, parents, loose, taken, candidates)
        for distinction in loose + taken:
            demand_holders[distinction].add(knot)
    demand_roster = roster_for(demand_holders, kept.keys() | proposals.keys(), counts, "demand")
    demand_groups = groups_for(demand_roster, counts, "demand")
    demand = defaultdict(list)
    for group in demand_groups:
        for member in group:
            demand[member].append(group)

    basis = parity_basis(state.knots) if law.knot_law == "parity" else None
    next_distinction = max(state.holders, default=-1) + 1
    births = {}
    made = []
    for knot, (kind, parents, loose, taken, candidates) in proposals.items():
        inputs = loose + taken
        implied = basis is not None and reduce(bit_vector(inputs), basis) == 0
        parent_owing = owing[parents[0]] if kind == "offshoot" else None
        fresh_count = 0 if implied else ration_count(law.ration, kind, len(inputs), len(demand[knot]), parent_owing)
        fresh = tuple(range(next_distinction, next_distinction + fresh_count))
        next_distinction += fresh_count
        births[knot] = Birth(
            knot, kind, parents, loose, taken, candidates, len(demand[knot]), tuple(demand[knot]), parent_owing,
            implied, fresh,
        )
        made.append(Knot(inputs + fresh, parents, kind, state.number + 1, fresh))
    counts.note("distinctions", len(state.holders) + sum(len(birth.fresh) for birth in births.values()))
    bars = state.bars.union(d for member in retired for d in state.member_loose[member])
    new_state = State(state.number + 1, state.knots + tuple(made), bars)
    step = Step(old_roster, groups, owing, tuple(sorted(short)), tuple(retired), tuple(waiting), kept,
                demand_roster, demand_groups, births)
    return new_state, step


def extend(states, steps, law, rounds, knot_bound, guard_scale):
    counts = Counts({key: guard_scale * limit for key, limit in LIMITS.items()})
    counts.note("distinctions", len(states[-1].holders))
    result = Run(states, steps, counts.peaks)
    if len(states[-1].knots) > knot_bound:
        result.stop = "knots"
        return result
    while states[-1].number < rounds:
        state = states[-1]
        try:
            new_state, step = advance(state, law, counts)
        except CountLimit as error:
            what, value, where = error.args
            result.guard = dict(round=state.number + 1, what=what, value=value, where=where)
            result.stop = "guard"
            break
        states.append(new_state)
        steps[new_state.number] = step
        if len(new_state.knots) > knot_bound:
            result.stop = "knots"
            break
        # BD2 1 reads through the round bound when a later round makes no births.
    return result


def grow(stars, law, rounds=7, knot_bound=1_500, guard_scale=1):
    start = State(0, tuple(Knot(tuple(places)) for places in stars))
    return extend([start], {}, law, rounds, knot_bound, guard_scale)


def bar(run, s, knots, law, rounds=7, knot_bound=1_500, guard_scale=1):
    state = run.states[s]
    bars = state.bars.union(d for member in knots for d in state.member_loose.get(member, ()))
    split = State(s, state.knots, bars)
    return extend(run.states[:s] + [split], {t: step for t, step in run.steps.items() if t <= s},
                  law, rounds, knot_bound, guard_scale)
