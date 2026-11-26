"""Replay Ticket C from DC 1–4, FD 1–4, and SD 9–67.

The input is a registered start and seed. No study engine is loaded.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, replace
from functools import cache
from itertools import combinations
from random import Random

import networkx as nx


@dataclass(frozen=True)
class Law:
    ration: str
    treatment: str
    release: str
    taking: str
    relation: str
    weighting: str

    @classmethod
    def from_record(cls, value: str) -> Law:
        return cls(*value.split("/"))


@dataclass(frozen=True)
class Knot:
    places: tuple[int, ...]
    made: int
    parents: tuple[int, ...] = ()
    takes: tuple[int, ...] = ()
    extra_take: int | None = None
    fresh: tuple[int, ...] = ()
    kind: str = "start"
    implied: bool = False


@dataclass(frozen=True)
class State:
    round: int
    knots: tuple[Knot, ...]
    holders: tuple[frozenset[int], ...]
    barred: frozenset[int] = frozenset()
    retired: frozenset[int] = frozenset()


@dataclass(frozen=True)
class Roster:
    usable: dict[int, tuple[int, ...]]
    barred_loose: dict[int, tuple[int, ...]]
    met_sets: dict[int, frozenset[int]]
    joinable: nx.Graph
    parts: tuple[tuple[int, ...], ...]


@cache
def atlas():
    return nx.graph_atlas_g()


def initial_state(start_row: dict) -> State:
    graph = atlas()[start_row["g"]]
    places = [[] for _ in range(start_row["n"])]
    holders = []
    for first, second in sorted(tuple(sorted(pair)) for pair in graph.edges()):
        name = len(holders)
        places[first].append(name)
        places[second].append(name)
        holders.append(frozenset((first, second)))
    for member, count in enumerate(start_row["loose"]):
        for _ in range(count):
            places[member].append(len(holders))
            holders.append(frozenset((member,)))
    return State(0, tuple(Knot(tuple(names), 0) for names in places), tuple(holders))


class GuardReached(Exception):
    pass


def roster(state: State, forced_members=(), mask_labels=()) -> Roster:
    loose = {}
    barred_loose = {}
    for distinction, holders in enumerate(state.holders):
        if len(holders) == 1:
            holder = next(iter(holders))
            counts = barred_loose if distinction in state.barred else loose
            counts.setdefault(holder, []).append(distinction)
    for member in forced_members:
        loose.setdefault(member, [])
    usable = {knot: tuple(names) for knot, names in loose.items()}
    barred = {knot: tuple(names) for knot, names in barred_loose.items()}
    met = {}
    incidences = sum(len(holders) * len(usable.keys() & holders) for holders in state.holders)
    if incidences > GUARD["incidences"]:
        raise GuardReached("incidences")
    for holders in state.holders:
        if len(holders) < 2:
            continue
        members = usable.keys() & holders
        if members:
            for common in holders:
                met.setdefault(common, set()).update(members - {common})
    met_sets = {name: frozenset(members) for name, members in met.items() if len(members) >= 2}
    joinable = nx.Graph()
    joinable.add_nodes_from(usable)
    for members in set(met_sets.values()):
        size = len(members)
        if size * (size - 1) // 2 > GUARD["pairs_in_met_set"]:
            raise GuardReached("pairs in a met set")
        if not mask_labels:
            joinable.add_edges_from(combinations(members, 2))
        else:
            joinable.add_edges_from(
                (first, second)
                for first, second in combinations(members, 2)
                if not ((mask_labels[first] & 1 and mask_labels[second] & 2)
                        or (mask_labels[first] & 2 and mask_labels[second] & 1))
            )
        if joinable.number_of_edges() > GUARD["joinable_pairs"]:
            raise GuardReached("joinable pairs")
    parts = tuple(sorted(tuple(sorted(part)) for part in nx.connected_components(joinable)))
    return Roster(usable, barred, met_sets, joinable, parts)


def groups(reading: Roster) -> list[tuple[int, ...]]:
    """Take the largest admissible groups, then uncovered joinable pairs."""
    # A complete part covered by one met set has one maximal clique,
    # which cannot be a group of three or more.
    containing = {}
    for members in set(reading.met_sets.values()):
        for member in members:
            containing.setdefault(member, []).append(members)
    big = []
    covered = set()
    clique_count = 0
    for part in reading.parts:
        if any(members.issuperset(part) for members in containing.get(part[0], ())):
            clique_count += 1
            continue
        for clique in nx.find_cliques(reading.joinable.subgraph(part)):
            clique_count += 1
            if clique_count > GUARD["maximal_cliques"]:
                raise GuardReached("maximal cliques")
            if len(clique) < 3:
                continue
            if any(members.issuperset(clique) for members in containing.get(clique[0], ())):
                continue
            ordered = tuple(sorted(clique))
            big.append(ordered)
            covered.update(combinations(ordered, 2))
    small = {tuple(sorted(pair)) for pair in reading.joinable.edges()} - covered
    if len(big) + len(small) > GUARD["groups"]:
        raise GuardReached("groups")
    return sorted(big) + sorted(small)


def form(reading: Roster, part: tuple[int, ...]) -> nx.Graph:
    graph = nx.Graph()
    for member in part:
        h = len(reading.usable[member])
        k = len(reading.barred_loose.get(member, ()))
        graph.add_node(member, label=(h, k))
    part = frozenset(part)
    distinct = sorted(
        {subset for subset in reading.met_sets.values() if subset <= part},
        key=lambda subset: (-len(subset), tuple(sorted(subset))),
    )
    maximal = []
    for subset in distinct:
        if not any(subset <= other for other in maximal):
            maximal.append(subset)
    for index, subset in enumerate(maximal):
        marker = ("met set", index)
        graph.add_node(marker, label=("met set",))
        graph.add_edges_from((marker, member) for member in subset)
    return graph


def same_form(first: nx.Graph, second: nx.Graph) -> bool:
    if len(first) != len(second) or first.number_of_edges() != second.number_of_edges():
        return False
    return nx.is_isomorphic(first, second, node_match=lambda a, b: a["label"] == b["label"])


def descend(state: State, x, y, s: int) -> tuple[int, ...]:
    labels = [0] * len(state.knots)
    for knot in x:
        labels[knot] |= 1
    for knot in y:
        labels[knot] |= 2
    for name, knot in enumerate(state.knots):
        if knot.made > s:
            for parent in knot.parents:
                labels[name] |= labels[parent]
    return tuple(labels)


def mask_of(distinctions) -> int:
    return sum(1 << name for name in distinctions)


def quotient(row: int, basis: dict[int, int]) -> int:
    """A residue modulo the binary row span."""
    left = row
    residue = 0
    while left:
        pivot = left.bit_length() - 1
        if pivot in basis:
            left ^= basis[pivot]
        else:
            bit = 1 << pivot
            left ^= bit
            residue |= bit
    return residue


def row_basis(rows) -> dict[int, int]:
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return basis


def take_candidates(state: State, law: Law, parents: tuple[int, ...], labels=()):
    if law.taking == "MET":
        met = [
            set().union(*(state.holders[name] for name in state.knots[parent].places)) - {parent}
            for parent in parents
        ]
        sources = set.intersection(*met)
    elif len(parents) == 1 and law.taking in ("STEPS-1", "STEPS-2"):
        sources = set(parents)
        for _ in range(int(law.taking[-1])):
            sources = {parent for knot in sources for parent in state.knots[knot].parents}
    else:
        return []
    already_held = {name for parent in parents for name in state.knots[parent].places}
    choices = {
        name for source in sources for name in state.knots[source].places
        if len(state.holders[name]) >= 2 and name not in already_held
    }
    if labels:
        from_x = any(labels[parent] & 1 for parent in parents)
        from_y = any(labels[parent] & 2 for parent in parents)
        choices = {
            name for name in choices
            if not any((from_x and labels[holder] & 2) or (from_y and labels[holder] & 1)
                       for holder in state.holders[name])
        }
    return sorted(choices)


def fresh_count(law: Law, parents: int, inputs: int, demand: int) -> int:
    if law.ration == "FBP":
        return max(3 - parents, 1)
    if law.ration == "FLOOR1":
        return max(3 - inputs, 1)
    if law.ration == "RATION-2":
        return max(2, 3 - inputs)
    ordinary = max(demand, 3 - inputs, 1)
    if law.ration == "ORD":
        return ordinary
    return min(ordinary, int(law.ration.removeprefix("CAP-")))


def round_step(state: State, law: Law, rnd: Random, labels=(), fully_masked=False) -> State:
    read = roster(state, mask_labels=labels)
    offered_groups = groups(read)
    obligations = Counter(member for group in offered_groups for member in group)
    short = {name for name, count in obligations.items() if len(read.usable[name]) < count}
    kept_groups = [group for group in offered_groups if short.isdisjoint(group)]
    to_pay = {name: deque(names) for name, names in read.usable.items()}
    parents_and_takes = [
        (group, tuple(to_pay[parent].popleft() for parent in group)) for group in kept_groups
    ]
    paid = Counter(member for group in kept_groups for member in group)
    retired = state.retired
    new_barred = state.barred
    if law.treatment == "CANCEL-RETIRE":
        retired = retired | short
        new_barred = new_barred.union(*(read.usable[member] for member in short))
    for member in sorted(to_pay):
        if member in short and law.treatment != "CANCEL-OFFSHOOT":
            continue
        if law.release == "HOLD" and member not in short:
            held = min(len(to_pay[member]), obligations[member] - paid[member])
            for _ in range(held):
                to_pay[member].popleft()
        parents_and_takes.extend(((member,), (name,)) for name in to_pay[member])
    if len(parents_and_takes) > GUARD["births"]:
        raise GuardReached("births")
    births = []
    for parents, payment in parents_and_takes:
        eligible = take_candidates(state, law, parents, labels if fully_masked else ())
        extra = None
        if eligible:
            if law.weighting == "T1":
                extra = eligible[rnd.randrange(len(eligible))]
            else:
                weights = [len(state.holders[name]) for name in eligible]
                extra = rnd.choices(eligible, weights=weights, k=1)[0]
        takes = payment if extra is None else payment + (extra,)
        births.append(Knot(tuple(sorted(takes)), state.round + 1, parents, takes, extra, (),
                           "offshoot" if len(parents) == 1 else "join"))
    first_name = len(state.knots)
    new_names = range(first_name, first_name + len(births))
    pending_holders = [set(holders) for holders in state.holders]
    for name, birth in zip(new_names, births):
        for distinction in birth.takes:
            pending_holders[distinction].add(name)
    proposed = State(state.round + 1, state.knots + tuple(births),
                     tuple(map(frozenset, pending_holders)), new_barred, retired)
    demanded = Counter()
    if law.ration in ("ORD", "CAP-2", "CAP-3", "CAP-4") and births:
        demand_labels = list(labels)
        if labels:
            for birth in births:
                value = 0
                for parent in birth.parents:
                    value |= labels[parent]
                demand_labels.append(value)
        demand_roster = roster(proposed, forced_members=new_names, mask_labels=demand_labels)
        demanded.update(member for group in groups(demand_roster) for member in group)
    basis = row_basis(mask_of(knot.places) for knot in state.knots) if law.relation == "parity" else None
    completed = []
    for name, birth in zip(new_names, births):
        implied = basis is not None and quotient(mask_of(birth.takes), basis) == 0
        count = 0 if implied else fresh_count(law, len(birth.parents), len(birth.takes), demanded[name])
        if len(pending_holders) + count > GUARD["distinctions"]:
            raise GuardReached("distinctions")
        fresh = tuple(range(len(pending_holders), len(pending_holders) + count))
        pending_holders.extend(({name},) * count)
        completed.append(replace(birth, places=birth.places + fresh, fresh=fresh, implied=implied))
    return replace(proposed, knots=state.knots + tuple(completed),
                   holders=tuple(map(frozenset, pending_holders)))


def grow(state: State, law: Law, seed: str, *, x=(), y=(), barred=(),
         mask=False, fully_masked=False) -> tuple[list[State], str | None]:
    if barred:
        at_start = roster(state)
        state = replace(state, barred=state.barred.union(*(at_start.usable[name] for name in barred)))
    states = [state]
    rnd = Random(seed)
    s = state.round
    for _ in range(s, 8):
        labels = descend(state, x, y, s) if mask or fully_masked else ()
        try:
            after = round_step(state, law, rnd, labels, fully_masked)
        except GuardReached as limit:
            return states, "guard: " + str(limit)
        states.append(after)
        if len(after.knots) > 500:
            return states, "knots"
        if after.knots == state.knots and after.barred == state.barred:
            states.extend(replace(after, round=round_number) for round_number in range(after.round + 1, 9))
            return states, None
        state = after
    return states, None


def failing_knots(state: State, law: Law) -> list[int]:
    """Check the projected relation on each knot's places."""
    if law.relation == "parity":
        rules = [mask_of(knot.places) for knot in state.knots]
        rank = len(row_basis(rules))
        return [
            name for name, places in enumerate(rules)
            if rank - len(row_basis(rule & ~places for rule in rules)) != 1
        ]
    from itertools import product

    from pysat.solvers import Solver

    clauses = []
    for knot in state.knots:
        clauses.extend(([name + 1 for name in knot.places], [-name - 1 for name in knot.places]))
    failed = []
    with Solver(bootstrap_with=clauses) as solve:
        for name, knot in enumerate(state.knots):
            # Complementation gives the assignments with the first place 1.
            places = tuple(place + 1 for place in knot.places)
            for signs in product((1, -1), repeat=len(places) - 1):
                if all(sign == 1 for sign in signs):
                    continue
                literals = [places[0]] + [sign * place for place, sign in zip(places[1:], signs)]
                if not solve.solve(assumptions=literals):
                    failed.append(name)
                    break
    return failed


# Limits from DB 3.9, ten times the fold study's registered guard.
GUARD = {
    "incidences": 20_000_000,
    "pairs_in_met_set": 200_000,
    "joinable_pairs": 200_000,
    "maximal_cliques": 2_000_000,
    "groups": 200_000,
    "births": 200_000,
    "distinctions": 4_000_000,
}
