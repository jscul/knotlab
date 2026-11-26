"""Replay the complete-round, no-extra-take growth law from its definitions.

The law is not-all-equal with waiting and release. The ration is the cap,
or the ordinary count if the cap is absent. This is a growth and reading
check on the supplied starts and laws.
"""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass, replace
from functools import cache
from hashlib import sha1
from itertools import combinations
import re

from networkx import graph_atlas


RECEIVER = frozenset({'A'})
FAR = frozenset({'B'})


@dataclass(frozen=True, slots=True)
class Knot:
    places: tuple
    parents: tuple
    roles: frozenset
    born: int
    kind: str
    label: str
    spent: bool = False
    fresh: int = 0


@dataclass(frozen=True, slots=True)
class State:
    round: int
    knots: tuple
    holders: tuple
    barred: frozenset
    members: tuple

    def usable(self, knot):
        return tuple(sorted(d for d in self.knots[knot].places
                            if len(self.holders[d]) == 1 and d not in self.barred))


@dataclass(frozen=True, slots=True)
class Pair:
    start: State
    receiver_site: int
    far_site: int
    receiver_knots: tuple
    far_knots: tuple
    link_knots: tuple


@dataclass(frozen=True, slots=True)
class Roster:
    members: tuple
    groups: tuple
    parts: tuple
    part_of: dict
    class_of: dict


@dataclass(frozen=True, slots=True)
class Round:
    births: tuple
    short: frozenset
    owe: dict
    demand: dict
    groups: tuple
    own_births: tuple


@dataclass(frozen=True, slots=True)
class Growth:
    pair: Pair
    cap: int | None
    rounds: int
    bound: int
    states: tuple
    rows: tuple
    edits: dict
    stop: str


@cache
def _atlas_incidence(index):
    pattern = graph_atlas(index)
    return pattern.number_of_nodes(), tuple(sorted(tuple(sorted(pair)) for pair in pattern.edges))


def _start_places(label):
    """Recover the placement and chosen site encoded by an archived label."""
    if label == 'ring':
        return [[(k - 1) % 5, k, 5 + 3 * k, 6 + 3 * k, 7 + 3 * k] for k in range(5)], 0
    if label == 'copier':
        return [[0, 1, 2], [0, 3, 4]], 0
    if label == 'source':
        return [[0, 1, 2, 9, 10, 11], [0, 1, 3], [4, 5, 12, 13, 14], [6, 7, 15, 16, 17],
                [2, 3, 4, 6, 18, 19, 20], [7, 8, 21, 22], [5, 8, 23, 24]], 0
    matched = re.fullmatch(r'(?:(?:n(\d+):)?g(\d+)|tri):(\d+)@(\d+)', label)
    if matched is None:
        raise ValueError(f'Unknown start label {label!r}')
    prefix, atlas_index, counts, site = matched.groups()
    split_counts = tuple(map(int, counts))
    if atlas_index is None:
        count, sharings = 3, ((0, 1), (0, 2), (1, 2))
    else:
        count, sharings = _atlas_incidence(int(atlas_index))
    if len(split_counts) != count or (prefix and int(prefix) != count) or not 0 <= int(site) < count:
        raise ValueError(f'Inconsistent start label {label!r}')
    places = [[] for _ in split_counts]
    for d, (a, b) in enumerate(sharings):
        places[a].append(d)
        places[b].append(d)
    d = len(sharings)
    for holding, loose_count in zip(places, split_counts):
        holding.extend(range(d, d + loose_count))
        d += loose_count
    return places, int(site)


def build_pair(receiver_label, far_label, join='meeting', separation=3):
    """Build a pair in the archive's order of names, including its common knots."""
    if join == 'shared':
        join = 'share'
    if join not in {'meeting', 'share'} or separation < 1:
        raise ValueError('A join requires a known construction and positive separation')
    places = []
    roles = []
    next_distinction = 0

    def take_start(label, role):
        nonlocal next_distinction
        if label == 'stub':
            return None
        local_places, site = _start_places(label)
        offset = len(places)
        places.extend([d + next_distinction for d in holding] for holding in local_places)
        roles.extend([role] * len(local_places))
        next_distinction += 1 + max(d for holding in local_places for d in holding)
        return offset + site

    def add_knot(role):
        knot = len(places)
        places.append([])
        roles.append(role)
        return knot

    def add_distinction(*holders):
        nonlocal next_distinction
        for knot in holders:
            places[knot].append(next_distinction)
        next_distinction += 1

    def connect(a, b):
        if join == 'share':
            add_distinction(a, b)
            return
        common = add_knot('spent')
        add_distinction(common, a)
        add_distinction(common, b)
        add_distinction(common, b)
        add_distinction(a)
        add_distinction(b)

    receiver_site = take_start(receiver_label, 'A')
    far_site = take_start(far_label, 'B')
    if receiver_site is None:
        receiver_site = add_knot('A')
    links = []
    previous = receiver_site
    for _ in range(separation - 1):
        link = add_knot('link')
        connect(previous, link)
        links.append(link)
        previous = link
    if far_site is None:
        far_site = add_knot('B')
    connect(previous, far_site)
    to_fill = links.copy() if join == 'share' else []
    if receiver_label == 'stub':
        to_fill.append(receiver_site)
    if far_label == 'stub':
        to_fill.append(far_site)
    for knot in to_fill:
        for _ in range(3 - len(places[knot])):
            add_distinction(knot)

    holders = [[] for _ in range(next_distinction)]
    knots = []
    seen = Counter()
    for knot, (holding, role) in enumerate(zip(places, roles)):
        for d in holding:
            holders[d].append(knot)
        name = f'{role}{seen[role]}'
        seen[role] += 1
        knots.append(Knot(tuple(holding), (), frozenset({role}), 0, 'start', name, role == 'spent'))
    members = tuple(k for k, holding in enumerate(places) if any(len(holders[d]) == 1 for d in holding))
    state = State(0, tuple(knots), tuple(map(tuple, holders)), frozenset(), members)
    receiver_knots = tuple(i for i, role in enumerate(roles) if role == 'A')
    far_knots = tuple(i for i, role in enumerate(roles) if role == 'B')
    return Pair(state, receiver_site, far_site, receiver_knots, far_knots, tuple(links))


def _met_sets(knots, holders, members):
    by_common = defaultdict(set)
    for member in members:
        for d in knots[member].places:
            for common in holders[d]:
                if common != member:
                    by_common[common].add(member)
    return {frozenset(met) for met in by_common.values() if len(met) >= 2}


def _neighbors(members, met_sets):
    joinable = {member: set() for member in members}
    for met in met_sets:
        for member in met:
            joinable[member].update(met)
    for member, partners in joinable.items():
        partners.discard(member)
    return joinable


def _components(neighbors):
    parts = []
    seen = set()
    for start in neighbors:
        if start in seen:
            continue
        todo = [start]
        seen.add(start)
        part = []
        while todo:
            member = todo.pop()
            part.append(member)
            others = neighbors[member] - seen
            seen.update(others)
            todo.extend(others)
        parts.append(tuple(sorted(part)))
    return tuple(parts)


def _maximal_families(joinable):
    """Enumerate inclusion-maximal pairwise joinable sets of size at least three."""
    # Iterative Bron–Kerbosch. Each frame has a growing family, unvisited
    # possible members and visited possible members.
    remaining = set(joinable)
    visited = set()
    for member in joinable:
        remaining.remove(member)
        pending = [({member}, remaining & joinable[member], visited & joinable[member])]
        visited.add(member)
        while pending:
            family, candidates, excluded = pending.pop()
            if len(family) + len(candidates) < 3:
                continue
            if not candidates:
                if not excluded:
                    yield family
                continue
            pivot = max(candidates | excluded, key=lambda k: len(candidates & joinable[k]))
            for next_member in candidates - joinable[pivot]:
                candidates.remove(next_member)
                pending.append((family | {next_member}, candidates & joinable[next_member],
                                excluded & joinable[next_member]))
                excluded.add(next_member)


def _groups(joinable, met_sets):
    containing = defaultdict(list)
    for met in met_sets:
        for member in met:
            containing[member].append(met)
    larger = []
    covered = set()
    for family in _maximal_families(joinable):
        member = min(family, key=lambda k: len(containing[k]))
        if any(family <= met for met in containing[member]):
            continue
        group = tuple(sorted(family))
        larger.append(group)
        covered.update(combinations(group, 2))
    pairs = ((a, b) for a, partners in joinable.items() for b in partners
             if a < b and (a, b) not in covered)
    return tuple(sorted(larger)) + tuple(sorted(pairs))


def _linked_classes(state, parts, part_of):
    linked = {i: set() for i in range(len(parts))}
    for part, members in enumerate(parts):
        for u in members:
            for d in state.knots[u].places:
                linked[part].update(part_of[v] for v in state.holders[d] if v in part_of)
    return {u: class_id for class_id, component in enumerate(_components(linked))
            for part in component for u in parts[part]}


def roster(state):
    met_sets = _met_sets(state.knots, state.holders, state.members)
    joinable = _neighbors(state.members, met_sets)
    parts = _components(joinable)
    part_of = {u: part for part, members in enumerate(parts) for u in members}
    return Roster(state.members, _groups(joinable, met_sets), parts, part_of,
                  _linked_classes(state, parts, part_of))


def _unpartitioned_groups(knots, holders, members):
    met_sets = _met_sets(knots, holders, members)
    return _groups(_neighbors(members, met_sets), met_sets)


def _birth_label(kind, parents, occurrence):
    # The recorded own-birth reading names births by parent names and the
    # occurrence among births of the same kind with those parents.
    return sha1(repr((kind, parents, occurrence)).encode()).hexdigest()[:16]


def _advance(state, cap):
    groups = _unpartitioned_groups(state.knots, state.holders, state.members)
    owe = Counter(member for group in groups for member in group)
    usable = {u: state.usable(u) for u in state.members}
    waiting = tuple(u for u in state.members if owe[u] > len(usable[u]))
    short = frozenset(waiting)
    paid = [group for group in groups if short.isdisjoint(group)]
    demand_paid = Counter(member for group in paid for member in group)
    parents_by_birth = paid + [(u,) for u in state.members if u not in short
                               for _ in range(len(usable[u]) - demand_paid[u])]
    available = {u: iter(holding) for u, holding in usable.items()}
    knots = list(state.knots)
    for u in state.members:
        if u not in short:
            knots[u] = replace(knots[u], spent=True)
    holders = list(state.holders)
    born = state.round + 1
    first_birth = len(knots)
    births = tuple(range(first_birth, first_birth + len(parents_by_birth)))
    occurrences = Counter()
    for knot, parents in zip(births, parents_by_birth):
        inherited = tuple(next(available[u]) for u in parents)
        kind = 'join' if len(parents) > 1 else 'offshoot'
        family = frozenset().union(*(knots[u].roles for u in parents))
        parent_labels = tuple(sorted(knots[u].label for u in parents))
        name_key = kind, parent_labels
        label = _birth_label(kind, parent_labels, occurrences[name_key])
        occurrences[name_key] += 1
        knots.append(Knot(inherited, parents, family, born, kind, label))
        for d in inherited:
            holders[d] += (knot,)

    members = waiting + births
    demand_groups = _unpartitioned_groups(knots, holders, members) if births else ()
    demand = Counter(u for group in demand_groups for u in group)
    own = []
    for u in births:
        knot = knots[u]
        fresh = max(demand[u], 3 - len(knot.parents), 1)
        if cap is not None:
            fresh = min(fresh, cap)
        new_places = tuple(range(len(holders), len(holders) + fresh))
        holders.extend([(u,)] * fresh)
        places = knot.places + new_places
        knots[u] = replace(knot, places=places, fresh=fresh)
        if knot.roles == RECEIVER:
            own.append((knot.label, fresh, len(places)))
    state = State(born, tuple(knots), tuple(holders), state.barred, members)
    return state, Round(births, short, dict(owe), dict(demand), groups, tuple(sorted(own)))


def _continue(pair, cap, rounds, bound, state, states, rows, edits):
    for _ in range(state.round, rounds):
        state, row = _advance(state, cap)
        states.append(state)
        rows.append(row)
        if len(state.knots) > bound:
            return Growth(pair, cap, rounds, bound, tuple(states), tuple(rows), edits, 'knots')
    return Growth(pair, cap, rounds, bound, tuple(states), tuple(rows), edits, 'rounds')


def grow(pair, cap=3, rounds=32, bound=10000):
    if cap is not None and cap < 2:
        raise ValueError('The ration must give a one-parent knot at least three places')
    return _continue(pair, cap, rounds, bound, pair.start, [pair.start], [], {})


def edit_state(state, knot, sign='add'):
    """Change a holding after a round. Barring uses the latest usable distinction."""
    if not 0 <= knot < len(state.knots):
        raise ValueError(f'No knot {knot} after round {state.round}')
    if sign == 'add':
        knots = list(state.knots)
        holding = knots[knot].places + (len(state.holders),)
        knots[knot] = replace(knots[knot], places=holding)
        return replace(state, knots=tuple(knots), holders=state.holders + ((knot,),),
                       members=tuple(sorted(set(state.members) | {knot})))
    if sign == 'bar':
        usable = state.usable(knot)
        if not usable:
            return None
        members = state.members if len(usable) > 1 else tuple(u for u in state.members if u != knot)
        return replace(state, barred=state.barred | {usable[-1]}, members=members)
    raise ValueError(f'Unknown change {sign!r}')


def perturb(growth, t0, knot, sign='add', rounds=None, bound=None):
    """Fork after round t0, keeping the archived convention of pre-edit snapshots."""
    if not 0 <= t0 < len(growth.states):
        raise ValueError(f'No snapshot after round {t0}')
    original = growth.edits.get(t0, growth.states[t0])
    state = edit_state(original, knot, sign)
    if state is None:
        return None
    edits = {c: s for c, s in growth.edits.items() if c < t0}
    edits[t0] = state
    return _continue(growth.pair, growth.cap, growth.rounds if rounds is None else rounds,
                     growth.bound if bound is None else bound, state, list(growth.states[:t0 + 1]),
                     list(growth.rows[:t0]), edits)


def sharing_counts(state, sources=None):
    """Count holder steps from the nearest source, through all knots."""
    if sources is None:
        sources = (u for u, knot in enumerate(state.knots) if knot.roles == RECEIVER)
    counts = dict.fromkeys(sources, 0)
    remaining = deque(counts)
    seen_distinctions = set()
    while remaining:
        u = remaining.popleft()
        for d in state.knots[u].places:
            if d in seen_distinctions:
                continue
            seen_distinctions.add(d)
            for v in state.holders[d]:
                if v not in counts:
                    counts[v] = counts[u] + 1
                    remaining.append(v)
    return counts


def _strict_classes(state):
    r = roster(state)
    near = {r.class_of[u] for u in r.members if state.knots[u].roles == RECEIVER}
    far = {u: r.class_of[u] for u in r.members if state.knots[u].roles == FAR}
    return near, far


def link_status(state):
    near, far = _strict_classes(state)
    return bool(near.intersection(far.values())) if near and far else None


def far_members(state, linked=None):
    near, far = _strict_classes(state)
    counts = sharing_counts(state)
    members = (u for u, part in far.items() if linked is None or (part in near) == linked)
    ordered = sorted(members, key=lambda u: (counts.get(u, float('inf')), u))
    return [(u, counts.get(u)) for u in ordered]


def first_own_difference(before, after, t0):
    common_rounds = min(len(before.rows), len(after.rows))
    first = next((i + 1 for i in range(t0, common_rounds)
                  if before.rows[i].own_births != after.rows[i].own_births), None)
    return first, common_rounds
