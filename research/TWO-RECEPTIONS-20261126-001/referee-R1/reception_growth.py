"""Reconstruct paired starts and read shared-engine growth without the study's readers."""

from collections import Counter, deque
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path
import re
import sys

from networkx import graph_atlas


ROOT = Path(__file__).resolve().parents[3]
ENGINE_DIR = (
    ROOT / "experiments" / "WHAT-A-BIRTH-CARRIES-20261125-001B"
    / "WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot"
)
sys.path.insert(0, str(ENGINE_DIR))
import eng


RECEIVER, FAR, OTHER = 1, 2, 4
BENCH_STARTS = {
    "ring": tuple(((u - 1) % 5, u, *range(5 + 3*u, 8 + 3*u)) for u in range(5)),
    "copier": ((0, 1, 2), (0, 3, 4)),
    "source": (
        (0, 1, 2, 9, 10, 11), (0, 1, 3), (4, 5, 12, 13, 14),
        (6, 7, 15, 16, 17), (2, 3, 4, 6, 18, 19, 20),
        (7, 8, 21, 22), (5, 8, 23, 24),
    ),
}


@dataclass
class Pair:
    stars: tuple
    roles: tuple
    receiver_site: int
    far_site: int
    link_knots: tuple
    # Equal descriptions receive exactly the same identity across the three histories.
    identities: dict = field(default_factory=dict, repr=False)


@dataclass
class Growth:
    pair: Pair
    law: eng.Law
    rounds: int
    bound: int
    mult: int
    states: list
    own_births: list
    ancestry: list
    identities: list
    stop: str = "rounds"

    @property
    def last_round(self):
        return len(self.own_births)


@cache
def start_places(label):
    if label in BENCH_STARTS:
        return BENCH_STARTS[label], 0
    match = re.fullmatch(r"(?:(?:n(\d+):)?g(\d+)|tri):(\d+)@(\d+)", label)
    if match is None:
        raise ValueError(f"Unknown start {label!r}")
    size, atlas_index, holdings, site = match.groups()
    if atlas_index is None:
        n, pairs = 3, ((0, 1), (0, 2), (1, 2))
    else:
        source = graph_atlas(int(atlas_index))
        n = source.number_of_nodes()
        pairs = sorted(tuple(sorted(pair)) for pair in source.edges)
    site = int(site)
    if len(holdings) != n or size is not None and int(size) != n or not 0 <= site < n:
        raise ValueError(f"Wrong census label {label!r}")
    places = [[] for _ in range(n)]
    for distinction, (u, v) in enumerate(pairs):
        places[u].append(distinction)
        places[v].append(distinction)
    distinction = len(pairs)
    for u, loose in enumerate(map(int, holdings)):
        places[u].extend(range(distinction, distinction + loose))
        distinction += loose
    return tuple(map(tuple, places)), site


def build_pair(receiver, far, steps=3):
    """Join the two chosen knots by meetings through steps minus one link knots."""
    if steps < 1:
        raise ValueError("At least one meeting is required")
    stars, roles = [], []
    serial = 0

    def knot(role):
        stars.append([])
        roles.append(role)
        return len(stars) - 1

    def put_start(label, role):
        nonlocal serial
        if label == "stub":
            return None
        placed, site = start_places(label)
        base = len(stars)
        for local in placed:
            stars[knot(role)].extend(serial + d for d in local)
        serial += 1 + max(d for local in placed for d in local)
        return base + site

    def place(*holders):
        nonlocal serial
        for u in holders:
            stars[u].append(serial)
        serial += 1

    def meet(near_site, far_site):
        shared_with = knot(OTHER)
        place(shared_with, near_site)
        place(shared_with, far_site)
        place(shared_with, far_site)
        place(near_site)
        place(far_site)

    a, b = put_start(receiver, RECEIVER), put_start(far, FAR)
    if a is None:
        a = knot(RECEIVER)
    current = a
    links = []
    for _ in range(steps - 1):
        next_link = knot(OTHER)
        links.append(next_link)
        meet(current, next_link)
        current = next_link
    if b is None:
        b = knot(FAR)
    meet(current, b)
    for label, u in ((receiver, a), (far, b)):
        if label == "stub":
            while len(stars[u]) < 3:
                place(u)
    return Pair(tuple(map(tuple, stars)), tuple(roles), a, b, tuple(links))


class CappedCount(eng.Law):
    def __init__(self, cap, take, choice):
        super().__init__("ORD", "CANCEL-WAIT", take, "nae", choice)
        self.cap = cap

    def fresh(self, kind, p, demand, owed):
        return min(self.cap, super().fresh(kind, p, demand, owed))


def law_of(ration, take=None, choice=None):
    if ration == "CAP-4":
        return CappedCount(4, take, choice)
    return eng.Law(ration, "CANCEL-WAIT", take, "nae", choice)


def _observe(growth, state, births):
    roles, names = growth.ancestry, growth.identities
    occurrences = Counter()
    own = []
    for birth in births:
        u, parents = birth["id"], birth["parents"]
        assert u == len(roles)
        role = 0
        for p in parents:
            role |= roles[p]
        roles.append(role)
        if role not in (RECEIVER, FAR):
            names.append(None)
            continue
        family = birth["kind"], tuple(sorted(names[p] for p in parents))
        identity_key = (*family, occurrences[family])
        occurrences[family] += 1
        table = growth.pair.identities
        identity = table.setdefault(identity_key, len(growth.pair.stars) + len(table))
        names.append(identity)
        if role == RECEIVER:
            own.append((identity, birth["f"], len(state.places[u])))
    return tuple(sorted(own))


def _continue(growth):
    guard = eng.Guard(growth.mult)
    while growth.last_round < growth.rounds:
        current = growth.states[-1]
        if current.n_knots > growth.bound:
            growth.stop = "knots"
            break
        trial = current.copy()
        try:
            births = eng.play_round(trial, growth.law, guard)["births"]
        except eng.GuardStop:
            growth.stop = "guard"
            break
        growth.states.append(trial)
        growth.own_births.append(_observe(growth, trial, births))
        if trial.n_knots > growth.bound:
            growth.stop = "knots"
            break
    return growth


def grow(pair, law, rounds=32, bound=10000, mult=100):
    start = eng.from_stars(pair.stars)
    names = [u if role in (RECEIVER, FAR) else None for u, role in enumerate(pair.roles)]
    return _continue(Growth(pair, law, rounds, bound, mult, [start], [], list(pair.roles), names))


def fork(growth, after, knot, rounds=None, bound=None, sign="add"):
    """Apply one edit after round after, then use the same law and guard."""
    state = growth.states[after].copy()
    if sign == "add":
        state.places[knot].append(len(state.holders))
        state.holders.append([knot])
        state.barred.append(False)
        state.maker.append(knot)
    elif sign == "bar":
        usable = state.usable(knot)
        if not usable:
            raise ValueError(f"Knot {knot} has no usable loose distinction after round {after}")
        state.barred[usable[-1]] = True
    else:
        raise ValueError(f"Unknown edit {sign!r}")
    n = state.n_knots
    target = growth.rounds if rounds is None else rounds
    ceiling = growth.bound if bound is None else bound
    return _continue(Growth(
        growth.pair, growth.law, target, ceiling, growth.mult, growth.states[:after] + [state],
        growth.own_births[:after], growth.ancestry[:n], growth.identities[:n],
    ))


def _own_classes(growth, after):
    """Read transitive links between live members from incidence and holdings."""
    state = growth.states[after]
    members = [u for u in range(state.n_knots)
               if any(len(state.holders[d]) == 1 and not state.barred[d] for d in state.places[u])]
    component = {u: u for u in members}

    def root(u):
        while u != component[u]:
            component[u] = component[component[u]]
            u = component[u]
        return u

    def union(u, v):
        component[root(v)] = root(u)

    # Meeting the same historical knot joins live members into parts.
    first_to_meet = {}
    for u in members:
        for d in state.places[u]:
            for other in state.holders[d]:
                if u != other:
                    union(u, first_to_meet.setdefault(other, u))
    # Sharing one distinction links those parts. Both joins are transitive.
    first_holder = {}
    for u in members:
        for d in state.places[u]:
            union(u, first_holder.setdefault(d, u))
    roles = growth.ancestry
    near = {root(u) for u in members if roles[u] == RECEIVER}
    far = {u: root(u) for u in members if roles[u] == FAR}
    return near, far


def link_status(growth, after):
    near, far = _own_classes(growth, after)
    return bool(near.intersection(far.values())) if near and far else None


def sharing_steps(growth, after):
    """Fewest sharings from any receiver-owned knot, including spent knots."""
    state = growth.states[after]
    steps = {u: 0 for u in range(state.n_knots) if growth.ancestry[u] == RECEIVER}
    pending = deque(steps)
    seen = set()
    while pending:
        u = pending.popleft()
        for d in state.places[u]:
            if d in seen:
                continue
            seen.add(d)
            for v in state.holders[d]:
                if v not in steps:
                    steps[v] = steps[u] + 1
                    pending.append(v)
    return steps


def far_members(growth, after, linked=True):
    """Return every eligible member as (knot, sharing steps), nearest first."""
    near, far = _own_classes(growth, after)
    eligible = [u for u, part in far.items() if linked is None or (part in near) == linked]
    if not eligible:
        return []
    steps = sharing_steps(growth, after)
    return [(u, steps.get(u)) for u in sorted(eligible, key=lambda u: (steps.get(u, float("inf")), u))]


def first_own_difference(growth, changed, after):
    if growth.pair is not changed.pair:
        raise ValueError("The histories must use the same exact birth identities")
    common = min(growth.last_round, changed.last_round)
    first = next((i + 1 for i in range(after, common)
                  if growth.own_births[i] != changed.own_births[i]), None)
    return first, common
