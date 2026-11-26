"""Rebuild complete rounds with waiting, release and the not-all-equal law.

The definitions come from RING-IN-BALANCE, PARTS-MEET-AGAIN and the
hold-back note. Numbered starts use the census atlas and the three named
starts use the published holdings. The atlas and maximal-clique algorithm
are shared library primitives. No study code is imported.
"""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import cache
from itertools import combinations
import re
from typing import Callable

from networkx import Graph, find_cliques, graph_atlas


RECEIVER, FAR, OTHER = 1, 2, 4
LIMITS = {
    "pairs": 20_000, "groups": 20_000, "births": 20_000,
    "distinctions": 400_000, "incidences": 2_000_000, "cliques": 200_000,
}
NAMED_STARTS = {
    "ring": tuple(((u - 1) % 5, u, *range(5 + 3 * u, 8 + 3 * u)) for u in range(5)),
    "copier": ((0, 1, 2), (0, 3, 4)),
    "source": (
        (0, 1, 2, 9, 10, 11), (0, 1, 3), (4, 5, 12, 13, 14), (6, 7, 15, 16, 17),
        (2, 3, 4, 6, 18, 19, 20), (7, 8, 21, 22), (5, 8, 23, 24),
    ),
}


@dataclass(frozen=True, slots=True)
class Birth:
    demand: int
    inputs: tuple[int, ...]
    parents: tuple[int, ...]
    parent_places: tuple[int, ...]

    @property
    def floor(self):
        return max(3 - len(self.inputs), 1)


@dataclass(frozen=True, slots=True)
class Law:
    ration: Callable[[Birth], int]
    take: str | None = None
    choice: str | None = None


LAWS = {
    "ORD": Law(lambda birth: max(birth.demand, birth.floor)),
    "CAP-3": Law(lambda birth: min(max(birth.demand, birth.floor), 3)),
    "INHERIT": Law(lambda birth: max(min(birth.demand, len(birth.inputs)), birth.floor)),
    "NET-OWING": Law(lambda birth: max(birth.demand - len(birth.inputs) + 1, birth.floor)),
}

TAKE_LAWS = {
    ("ORD", take, choice): Law(LAWS["ORD"].ration, take, choice)
    for take, choice in (
        ("MET", "OLDEST"), ("MET", "NEWEST"), ("MET-SOLE", None),
        ("STEPS1-SOLE", None), ("STEPS2-SOLE", None),
    )
}


class LimitReached(Exception):
    pass


def within_limit(what, count, multiplier=4):
    if count > LIMITS[what] * multiplier:
        raise LimitReached(what, count)


@dataclass(slots=True)
class State:
    places: list[tuple]
    holders: list[tuple]
    parents: list[tuple]
    roles: list[int]
    names: list[int]

    def copy(self):
        return State(self.places.copy(), self.holders.copy(), self.parents.copy(),
                     self.roles.copy(), self.names.copy())

    def loose(self):
        return {u: ds for u, places in enumerate(self.places)
                if (ds := tuple(sorted(d for d in places if len(self.holders[d]) == 1)))}


@cache
def pattern(label):
    if label in NAMED_STARTS:
        return NAMED_STARTS[label], 0
    match = re.fullmatch(r"(?:(?:n(\d+):)?g(\d+)|tri):(\d+)@(\d+)", label)
    if match is None:
        raise ValueError(f"Unknown start {label!r}")
    size, index, loose, site = match.groups()
    if index is None:
        meetings = ((0, 1), (0, 2), (1, 2))
        count = 3
    else:
        numbered = graph_atlas(int(index))
        meetings = sorted(tuple(sorted(pair)) for pair in numbered.edges)
        count = numbered.number_of_nodes()
    if len(loose) != count or (size and int(size) != count) or int(site) >= count:
        raise ValueError(f"Inconsistent start {label!r}")
    places = [[] for _ in range(count)]
    for d, (u, v) in enumerate(meetings):
        places[u].append(d)
        places[v].append(d)
    next_distinction = len(meetings)
    for row, extra in zip(places, map(int, loose)):
        row.extend(range(next_distinction, next_distinction + extra))
        next_distinction += extra
    return tuple(map(tuple, places)), int(site)


def pair_start(receiver, far):
    """Join the two starts by three meetings through two link knots."""
    places, holders, roles = [], [], []

    def knot(role):
        roles.append(role)
        places.append([])
        return len(places) - 1

    def distinction(*owners):
        d = len(holders)
        holders.append(owners)
        for u in owners:
            places[u].append(d)

    def add_pattern(label, role):
        rows, site = pattern(label)
        offset = len(places)
        owners = [[] for _ in range(1 + max(d for row in rows for d in row))]
        for row in rows:
            u = knot(role)
            for d in row:
                owners[d].append(u)
        for holding in owners:
            distinction(*holding)
        return offset + site

    here = add_pattern(receiver, RECEIVER)
    destination = None if far == "stub" else add_pattern(far, FAR)
    for step in range(3):
        if step < 2:
            following = knot(OTHER)
        else:
            following = knot(FAR) if destination is None else destination
        common = knot(OTHER)
        distinction(here, common)
        distinction(following, common)
        distinction(following, common)
        distinction(here)
        distinction(following)
        here = following
    return State(list(map(tuple, places)), holders, [()] * len(roles),
                 roles, list(range(len(roles))))


def live_holdings(state, members):
    holdings = defaultdict(set)
    for u in members:
        for d in state.places[u]:
            holdings[d].add(u)
    return holdings


def common_knots_of(state, holdings):
    common_knots = defaultdict(set)
    for d, active in holdings.items():
        for other in state.holders[d]:
            if len(active) > 1 or other not in active:
                common_knots[other].update(active - {other})
    return common_knots


def meetings(state, members):
    """Use one incidence list for each common knot and one for each distinction."""
    holdings = live_holdings(state, members)
    return common_knots_of(state, holdings), holdings


def groups(state, members):
    holdings = live_holdings(state, members)
    within_limit("incidences", sum(len(v) * (len(state.holders[d]) - 1)
                                   for d, v in holdings.items()))
    largest_shared = max(map(len, holdings.values()), default=1) - 1
    within_limit("pairs", largest_shared * (largest_shared - 1) // 2)
    common_knots = common_knots_of(state, holdings)
    met_sets = {frozenset(met) for met in common_knots.values() if len(met) >= 2}
    largest_met = max(map(len, met_sets), default=1)
    within_limit("pairs", largest_met * (largest_met - 1) // 2)

    pairs = set()
    met_by_member = defaultdict(list)
    for met in sorted(met_sets, key=len, reverse=True):
        u = min(met, key=lambda member: len(met_by_member[member]))
        if any(met <= larger for larger in met_by_member[u]):
            continue
        pairs.update(combinations(sorted(met), 2))
        within_limit("pairs", len(pairs))
        for u in met:
            met_by_member[u].append(met)
    joinable = Graph()
    joinable.add_nodes_from(members)
    joinable.add_edges_from(pairs)

    larger = []
    for count, clique in enumerate(find_cliques(joinable), 1):
        within_limit("cliques", count)
        if len(clique) < 3:
            continue
        family = frozenset(clique)
        # A met set is pairwise joinable, so a maximal family it contains equals it.
        if family in met_sets:
            continue
        larger.append(tuple(sorted(family)))
        within_limit("groups", len(larger))
    covered = {pair for group in larger for pair in combinations(group, 2)}
    result = sorted(larger) + sorted(pairs - covered)
    within_limit("groups", len(result))
    return result


def extra_distinctions(state, law):
    @cache
    def met_by(knot):
        return {v for d in state.places[knot] for v in state.holders[d] if v != knot}

    @cache
    def for_parents(parents):
        if law.take in {"MET", "MET-SOLE"}:
            suppliers = set.intersection(*(met_by(u) for u in parents)).difference(parents)
        elif len(parents) > 1:
            return ()
        elif law.take == "STEPS1-SOLE":
            suppliers = state.parents[parents[0]]
        elif law.take == "STEPS2-SOLE":
            suppliers = {v for u in state.parents[parents[0]] for v in state.parents[u]}
        else:
            raise ValueError(f"Unknown take {law.take!r}")
        excluded = {d for u in parents for d in state.places[u]}
        candidates = {d for u in suppliers for d in state.places[u]
                      if d not in excluded and len(state.holders[d]) >= 2}
        if law.take == "MET" and candidates:
            select = {"OLDEST": min, "NEWEST": max}[law.choice]
            return (select(candidates),)
        return tuple(candidates) if len(candidates) == 1 else ()

    return for_parents


@dataclass(frozen=True, slots=True)
class Round:
    births: int
    own_births: tuple
    made_short: int
    counts: Counter


def advance(state, law, namebook):
    loose = state.loose()
    groups_now = groups(state, loose)
    owing = Counter(u for group in groups_now for u in group)
    waiting = {u for u in loose if owing[u] > len(loose[u])}
    joins = [group for group in groups_now if waiting.isdisjoint(group)]
    paid = Counter(u for group in joins for u in group)
    within_limit("births", len(joins))
    births = joins + [(u,) for u in loose if u not in waiting
                      for _ in range(len(loose[u]) - paid[u])]
    within_limit("births", len(births))
    spending = {u: iter(ds) for u, ds in loose.items()}

    new = state.copy()
    first_birth = len(new.places)
    extra = extra_distinctions(state, law) if law.take is not None else None
    for u, parents in enumerate(births, first_birth):
        inherited = tuple(next(spending[parent]) for parent in parents)
        if extra is not None:
            inherited += extra(parents)
        new.places.append(inherited)
        for d in inherited:
            new.holders[d] += (u,)

    demand = Counter()
    if births:
        possible = sorted(waiting) + list(range(first_birth, len(new.places)))
        demand.update(u for group in groups(new, possible) for u in group)
    rationed = [
        Birth(demand[u], new.places[u], parents, tuple(len(state.places[p]) for p in parents))
        for u, parents in enumerate(births, first_birth)
    ]
    fresh_counts = [law.ration(birth) for birth in rationed]
    if any(fresh < birth.floor for birth, fresh in zip(rationed, fresh_counts)):
        raise ValueError("A ration gave fewer fresh distinctions than the floor")
    within_limit("distinctions", len(new.holders) + sum(fresh_counts))

    own = []
    occurrences = Counter()
    counts = Counter()
    for u, (birth, fresh) in enumerate(zip(rationed, fresh_counts), first_birth):
        roles = 0
        for p in birth.parents:
            roles |= state.roles[p]
        names = tuple(sorted(state.names[p] for p in birth.parents))
        ordinal = occurrences[names]
        occurrences[names] += 1
        name = namebook.setdefault((names, ordinal), len(namebook) + namebook.first_birth)
        start = len(new.holders)
        new.places[u] += tuple(range(start, start + fresh))
        new.holders.extend([(u,)] * fresh)
        new.parents.append(birth.parents)
        new.roles.append(roles)
        new.names.append(name)
        counts[len(birth.inputs), birth.demand, fresh] += 1
        if roles == RECEIVER:
            own.append((name, fresh, len(new.places[u])))
    return new, Round(len(births), tuple(sorted(own)),
                      sum(bool(state.parents[u]) for u in waiting), counts)


class Names(dict):
    def __init__(self, first_birth):
        super().__init__()
        self.first_birth = first_birth


@dataclass(slots=True)
class Growth:
    law: Law
    rounds: int
    bound: int
    states: list[State]
    rows: list[Round]
    names: Names
    stop: str = "rounds"


def continue_growth(growth, state):
    while len(growth.rows) < growth.rounds:
        try:
            state, row = advance(state, growth.law, growth.names)
        except LimitReached:
            growth.stop = "guard"
            break
        growth.rows.append(row)
        growth.states.append(state)
        if len(state.places) > growth.bound:
            growth.stop = "knots"
            break
    return growth


def grow(receiver, far, law, *, rounds, bound):
    state = pair_start(receiver, far)
    growth = Growth(law, rounds, bound, [state], [], Names(len(state.places)))
    return continue_growth(growth, state)


def perturb(baseline, after, knot):
    state = baseline.states[after].copy()
    state.places[knot] += (len(state.holders),)
    state.holders.append((knot,))
    changed = Growth(baseline.law, baseline.rounds, baseline.bound,
                     baseline.states[:after] + [state], baseline.rows[:after], baseline.names)
    return continue_growth(changed, state)


def link_membership(state):
    """Associate each live far knot with its linkage to the receiver."""
    live = state.loose()
    common_knots, holdings = meetings(state, live)
    aliases = {u: u for u in live}

    def representative(u):
        while aliases[u] != u:
            aliases[u] = aliases[aliases[u]]
            u = aliases[u]
        return u

    for family in (common_knots, holdings):
        for group in family.values():
            leader, *rest = group
            for u in rest:
                aliases[representative(u)] = representative(leader)
    near = {representative(u) for u in live if state.roles[u] == RECEIVER}
    far = {u: representative(u) in near for u in live if state.roles[u] == FAR}
    return (any(far.values()) if near and far else None), far


def sharing_counts(state):
    """Count shared distinctions along the shortest chain to a receiver knot."""
    counts = {u: 0 for u, role in enumerate(state.roles) if role == RECEIVER}
    remaining = deque(counts)
    seen = set()
    while remaining:
        here = remaining.popleft()
        for d in state.places[here]:
            if d in seen:
                continue
            seen.add(d)
            for u in state.holders[d]:
                if u not in counts:
                    counts[u] = counts[here] + 1
                    remaining.append(u)
    return counts


def measure(receiver, far, law, *, rounds, bound, edits_after, edit_limit=None):
    """Record the archive's fields and the chosen knot of each paired edit."""
    baseline = grow(receiver, far, law, rounds=rounds, bound=bound)
    affiliations = [link_membership(state) for state in baseline.states[1:]]
    row = {
        "rounds": len(baseline.rows),
        "ended": baseline.stop,
        "made short": [record.made_short for record in baseline.rows],
        "linked": [status for status, _ in affiliations],
        "births": [record.births for record in baseline.rows],
        "changes": [],
    }
    details = []
    for t0 in edits_after:
        if t0 >= len(baseline.rows) or row["linked"][t0 - 1] is None:
            continue
        membership = affiliations[t0 - 1][1]
        sharings = sharing_counts(baseline.states[t0])
        for linked, limit in ((True, 5), (False, 2)):
            candidates = sorted((u for u, status in membership.items() if status == linked),
                                key=lambda u: (sharings.get(u, float("inf")), u))
            for knot in candidates[:limit]:
                changed = perturb(baseline, t0, knot)
                common = min(len(baseline.rows), len(changed.rows))
                differences = [i + 1 for i in range(t0, common)
                               if baseline.rows[i].own_births != changed.rows[i].own_births]
                heard = differences[0] if differences else None
                row["changes"].append({
                    "t0": t0, "linked": linked, "sharings": sharings.get(knot),
                    "heard": heard, "rounds": common,
                    "births with": [record.births for record in changed.rows] if heard else None,
                })
                details.append({"knot": knot, "changed ended": changed.stop,
                                "own births differ in rounds": differences})
                if len(details) == edit_limit:
                    return row, details
    return row, details
