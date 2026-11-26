"""Independent finite growth replay for the fresh-count comparisons."""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from hashlib import sha1
from itertools import combinations

import networkx as nx


GUARD_LIMITS = {
    "pairs": 20_000,
    "groups": 20_000,
    "births": 20_000,
    "distinctions": 400_000,
    "incidences": 2_000_000,
    "cliques": 200_000,
}


class GuardStop(Exception):
    pass


@dataclass(frozen=True, slots=True)
class Birth:
    knot: int
    descent: str
    owner: str
    p: int
    D: int
    f: int
    kind: str
    parents: tuple[int, ...]

    @property
    def ordinary(self):
        return max(self.D, 3 - self.p, 1)


@dataclass(frozen=True, slots=True)
class Round:
    births: tuple[Birth, ...]
    receiver_signature: tuple[tuple[str, int, int], ...]
    made_short: int
    knot_count: int


@dataclass(frozen=True, slots=True)
class Mark:
    knot: int
    descent: str
    sharings: int | None


@dataclass(frozen=True, slots=True)
class State:
    places: tuple[tuple[int, ...], ...]
    holders: tuple[tuple[int, ...], ...]
    descents: tuple[str, ...]
    ancestry: tuple[int, ...]
    parity_basis: dict[int, int] | None


def _guard(limits, name, size):
    if size > limits[name]:
        raise GuardStop(name, size)


def _pair_count(n):
    return n * (n - 1) // 2


def _with_loose(holders):
    """Find the usable loose distinctions of each knot, in archive order."""
    loose = defaultdict(list)
    for distinction, knots in enumerate(holders):
        if len(knots) == 1:
            loose[knots[0]].append(distinction)
    return loose


def _groups(places, holders, members, limits):
    """Read the join groups of the roster or the demand of proposed births."""
    member_counts = Counter(d for u in members for d in places[u])
    incidences = sum(count * (len(holders[d]) - 1) for d, count in member_counts.items())
    _guard(limits, "incidences", incidences)
    if member_counts:
        _guard(limits, "pairs", _pair_count(max(member_counts.values()) - 1))

    met = defaultdict(set)
    for u in members:
        for d in places[u]:
            for w in holders[d]:
                if w != u:
                    met[w].add(u)
    supports = sorted({frozenset(value) for value in met.values() if len(value) >= 2},
                      key=len, reverse=True)
    _guard(limits, "pairs", _pair_count(len(supports[0])) if supports else 0)
    maximal = defaultdict(list)
    pairs = set()
    for support in supports:
        member = min(support, key=lambda u: len(maximal[u]))
        if any(support <= other for other in maximal[member]):
            continue
        for u in support:
            maximal[u].append(support)
        pairs.update(combinations(sorted(support), 2))
        _guard(limits, "pairs", len(pairs))

    graph = nx.Graph()
    graph.add_nodes_from(members)
    graph.add_edges_from(pairs)
    higher = []
    for n, clique in enumerate(nx.find_cliques(graph), 1):
        _guard(limits, "cliques", n)
        if len(clique) >= 3:
            member = min(clique, key=lambda u: len(maximal[u]))
            group = frozenset(clique)
            if all(not group <= support for support in maximal[member]):
                higher.append(tuple(sorted(clique)))
    for group in higher:
        pairs.difference_update(combinations(group, 2))
    groups = sorted(higher) + sorted(pairs)
    _guard(limits, "groups", len(groups))
    return groups


def _parity_row(distinctions):
    row = 0
    for d in distinctions:
        row ^= 1 << d
    return row


def _remainder(row, basis):
    while row:
        pivot = row.bit_length() - 1
        if pivot not in basis:
            break
        row ^= basis[pivot]
    return row


def _add_equation(basis, distinctions):
    row = _remainder(_parity_row(distinctions), basis)
    if row:
        basis[row.bit_length() - 1] = row


def _equations(places):
    basis = {}
    for distinctions in places:
        _add_equation(basis, distinctions)
    return basis


def _fresh(law, kind, p, D, owing):
    if callable(law):
        return law(kind, p, D, owing)
    floor = max(3 - p, 1)
    ordinary = max(D, floor)
    match law:
        case "ORD":
            return ordinary
        case "FLOOR1":
            return floor
        case "CAP3-JOINS":
            ceiling = 3 if kind == "join" else ordinary
        case "HALF":
            ceiling = (D + 1) // 2 + 1
        case "PLACES":
            ceiling = p + 1
        case "PLACES-JOINS":
            ceiling = p + 1 if kind == "join" else ordinary
        case "PLACES-OFFSHOOTS":
            ceiling = p + 1 if kind == "offshoot" else ordinary
        case str() if law.startswith("CAP-"):
            ceiling = int(law.removeprefix("CAP-"))
        case _:
            raise ValueError(f"Unknown fresh-count law {law!r}")
    return max(floor, min(ordinary, ceiling))


def _root(parents, u):
    while u != parents[u]:
        parents[u] = parents[parents[u]]
        u = parents[u]
    return u


def _cross_part_takes(state, members, groups):
    """Read the shared distinctions supplied by live members of other parts."""
    parents = {u: u for u in members}
    for group in groups:
        first = _root(parents, group[0])
        for u in group[1:]:
            parents[_root(parents, u)] = first
    part = {u: _root(parents, u) for u in members}

    sources = {}
    for u in members:
        group = part[u]
        for d in state.places[u]:
            if len(state.holders[d]) > 1 and sources.setdefault(d, group) != group:
                sources[d] = None  # More than one part supplies this distinction.
    ordered = sorted(sources.items())
    takes = {group: tuple(d for d, source in ordered if source != group)
             for group in set(part.values())}
    return {u: takes[group] for u, group in part.items()}


def _live_sender_groups(state):
    """Find live sender knots in parts linked to and separate from live receiver knots."""
    members = _with_loose(state.holders)
    receiver = [u for u in members if state.ancestry[u] == 1]
    sender = [u for u in members if state.ancestry[u] == 2]
    if not receiver or not sender:
        return None, (), tuple(sender)

    # Two live knots are in the same class if they share directly or meet
    # a common knot. Each historical knot supplies one class identification.
    parents = {u: u for u in members}
    representative = parents.copy()
    for u in members:
        for d in state.places[u]:
            for w in state.holders[d]:
                parents[_root(parents, u)] = _root(parents, representative.setdefault(w, u))

    receivers = {_root(parents, u) for u in receiver}
    linked = []
    separate = []
    for u in sender:
        (linked if _root(parents, u) in receivers else separate).append(u)
    return bool(linked), tuple(linked), tuple(separate)


def _sharings(state):
    """Count sharings to the nearest receiver ancestor or descendant, live or spent."""
    counts = {u: 0 for u, ancestry in enumerate(state.ancestry) if ancestry == 1}
    waiting = deque(counts)
    read = set()
    while waiting:
        u = waiting.popleft()
        n = counts[u] + 1
        for d in state.places[u]:
            if d in read:
                continue
            read.add(d)
            for w in state.holders[d]:
                if w not in counts:
                    counts[w] = n
                    waiting.append(w)
    return counts


class Growth:
    def __init__(self, knots, roles, law="ORD", *, guard_multiplier=4, knot_law="nae", take=None):
        if knot_law not in ("nae", "parity"):
            raise ValueError(f"Unknown knot law {knot_law!r}")
        if take not in (None, "J-EACH-PART"):
            raise ValueError(f"Unsupported take {take!r}")
        index = {d: n for n, d in enumerate(sorted({d for knot in knots for d in knot}))}
        places = tuple(tuple(index[d] for d in knot) for knot in knots)
        holders = [[] for _ in index]
        for u, distinctions in enumerate(places):
            for d in distinctions:
                holders[d].append(u)
        descents = []
        counts = Counter()
        for role in roles:
            descents.append(f"{role}{counts[role]}")
            counts[role] += 1
        self.law = law
        self.take = take
        self.guard_limits = {name: base * guard_multiplier for name, base in GUARD_LIMITS.items()}
        self.start_count = len(places)
        self.rounds = []
        self.stop = "rounds"
        self._snapshots = [State(places, tuple(map(tuple, holders)), tuple(descents),
                                 tuple({"A": 1, "B": 2}.get(role, 4) for role in roles),
                                 _equations(places) if knot_law == "parity" else None)]
        self._links = {}
        self._sharings = {}

    def _advance(self):
        state = self._snapshots[-1]
        loose = _with_loose(state.holders)
        members = sorted(loose)
        groups = _groups(state.places, state.holders, members, self.guard_limits)
        owed = Counter(u for group in groups for u in group)
        short = {u for u in members if len(loose[u]) < owed[u]}
        made_short = sum(u >= self.start_count for u in short)
        joins = [group for group in groups if short.isdisjoint(group)]
        kept = Counter(u for group in joins for u in group)
        proposals = [("join", group) for group in joins]
        for knot in members:
            if knot not in short:
                proposals.extend([("offshoot", (knot,))] * (len(loose[knot]) - kept[knot]))
        _guard(self.guard_limits, "births", len(proposals))
        if not proposals:
            return state, Round((), (), made_short, len(state.places))

        takes = _cross_part_takes(state, members, groups) if self.take else {}
        remaining = {u: iter(ds) for u, ds in loose.items()}
        inputs = []
        for kind, parents in proposals:
            given = tuple(next(remaining[u]) for u in parents)
            if kind == "offshoot":
                given += takes.get(parents[0], ())
            inputs.append(given)
        places = list(state.places) + inputs
        holders = list(state.holders)
        first = len(state.places)
        new_holders = defaultdict(list)
        for knot, distinctions in enumerate(inputs, first):
            for d in distinctions:
                new_holders[d].append(knot)
        for d, knots in new_holders.items():
            holders[d] += tuple(knots)
        demand_members = sorted(short) + list(range(first, len(places)))
        demand = Counter(u for group in _groups(places, holders, demand_members, self.guard_limits)
                         for u in group)

        descents = list(state.descents)
        ancestry = list(state.ancestry)
        parity = state.parity_basis.copy() if state.parity_basis is not None else None
        seen = Counter()
        births = []
        for knot, (kind, parents) in enumerate(proposals, first):
            ps = tuple(sorted(descents[u] for u in parents))
            key = (kind, ps)
            descent = sha1(repr((kind, ps, seen[key])).encode()).hexdigest()[:16]
            seen[key] += 1
            ancestors = 0
            for u in parents:
                ancestors |= ancestry[u]
            owner = {1: "A", 2: "B", 3: "joint", 7: "joint"}.get(ancestors, "link")
            given = places[knot]
            p, D = len(given), demand[knot]
            implied = parity is not None and not _remainder(_parity_row(given), parity)
            owing = owed[parents[0]] if kind == "offshoot" else None
            f = 0 if implied else _fresh(self.law, kind, p, D, owing)
            births.append(Birth(knot, descent, owner, p, D, f, kind, parents))
            descents.append(descent)
            ancestry.append(ancestors)

        fresh_total = sum(birth.f for birth in births)
        _guard(self.guard_limits, "distinctions", len(holders) + fresh_total)
        for birth in births:
            start = len(holders)
            holders.extend([(birth.knot,)] * birth.f)
            places[birth.knot] += tuple(range(start, len(holders)))
        if parity is not None:
            for distinctions in places[first:]:
                _add_equation(parity, distinctions)

        signature = tuple(sorted((b.descent, b.f, b.p + b.f) for b in births if b.owner == "A"))
        next_state = State(tuple(places), tuple(holders), tuple(descents), tuple(ancestry), parity)
        return next_state, Round(tuple(births), signature, made_short, len(places))

    def run(self, rounds, bound):
        while self.stop == "rounds" and len(self.rounds) < rounds:
            try:
                state, row = self._advance()
            except GuardStop:
                self.stop = "guard"
                break
            self._snapshots.append(state)
            self.rounds.append(row)
            if row.knot_count > bound:
                self.stop = "knots"
        return self

    def fork(self, round_number, law=None):
        if not 0 <= round_number <= len(self.rounds):
            raise ValueError(f"Cannot fork after round {round_number}")
        branch = Growth.__new__(Growth)
        branch.law = self.law if law is None else law
        branch.take = self.take
        branch.guard_limits = self.guard_limits
        branch.start_count = self.start_count
        branch.rounds = self.rounds[:round_number]
        branch.stop = "rounds"
        branch._snapshots = self._snapshots[:round_number + 1]
        branch._links = {}
        branch._sharings = {}
        return branch

    def mark(self, knot, renew=True):
        state = self._snapshots[-1]
        places = list(state.places)
        places[knot] += (len(state.holders),)
        places = tuple(places)
        parity = state.parity_basis
        if renew and parity is not None:
            parity = _equations(places)
        self._snapshots[-1] = State(places, state.holders + ((knot,),), state.descents,
                                    state.ancestry, parity)
        self._links.pop(len(self.rounds), None)
        self._sharings.pop(len(self.rounds), None)
        return self

    def _sharing_classes(self, round_number):
        if round_number not in self._links:
            self._links[round_number] = _live_sender_groups(self._snapshots[round_number])
        return self._links[round_number]

    def linked(self, round_number):
        return self._sharing_classes(round_number)[0]

    def mark_candidates(self, round_number, linked):
        state = self._snapshots[round_number]
        _, linked_knots, separate_knots = self._sharing_classes(round_number)
        candidates = linked_knots if linked else separate_knots
        if not candidates:
            return ()
        if round_number not in self._sharings:
            self._sharings[round_number] = _sharings(state)
        sharings = self._sharings[round_number]
        ordered = sorted(candidates, key=lambda u: (sharings.get(u, float("inf")), u))
        return tuple(Mark(u, state.descents[u], sharings.get(u)) for u in ordered)


def first_hearing(unchanged, changed, after):
    """Compare receiver births over the rounds reached by both growths."""
    common = min(len(unchanged.rounds), len(changed.rounds))
    for i in range(after, common):
        if unchanged.rounds[i].receiver_signature != changed.rounds[i].receiver_signature:
            return i + 1
    return None
