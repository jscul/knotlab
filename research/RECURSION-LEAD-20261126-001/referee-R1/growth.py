"""Rebuild the all-at-once parity round used by the frozen readings."""

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from itertools import combinations
from pathlib import Path
from random import Random


Stage = tuple[frozenset[int], ...]
RESEARCH = Path(__file__).resolve().parents[2]
ARMS = ("ordinary", "one_fewer", "arity_floor")


@dataclass(frozen=True)
class Birth:
    parents: tuple[int, ...]
    taken: frozenset[int]
    demand: int
    implied: bool
    ordinary_fresh: int
    fresh: frozenset[int]


def meetings(stage: Stage):
    """Index the shared distinctions and the loose stock of each holder."""
    holders = defaultdict(list)
    for knot, row in enumerate(stage):
        for distinction in row:
            holders[distinction].append(knot)

    neighbours = [set() for _ in stage]
    loose = [set() for _ in stage]
    for distinction, owners in holders.items():
        if len(owners) == 1:
            loose[owners[0]].add(distinction)
        else:
            a, b = owners
            neighbours[a].add(b)
            neighbours[b].add(a)
    return neighbours, loose


def components(neighbours):
    unseen = set(range(len(neighbours)))
    while unseen:
        current = {unseen.pop()}
        pending = list(current)
        while pending:
            more = neighbours[pending.pop()] & unseen
            unseen.difference_update(more)
            current.update(more)
            pending.extend(more)
        yield current


def parent_groups(neighbours, live):
    """Keep maximal cliques with no common witness, then uncovered pairs."""
    candidates = {i: set() for i in live}
    witnesses = [witness & live for witness in neighbours]
    for witness in witnesses:
        for a, b in combinations(witness, 2):
            candidates[a].add(b)
            candidates[b].add(a)

    def maximal_cliques(group, pending, visited):
        if not pending and not visited:
            yield group
            return
        pivot = max(pending | visited, key=lambda i: len(candidates[i] & pending))
        for i in pending - candidates[pivot]:
            yield from maximal_cliques(group | {i}, pending & candidates[i], visited & candidates[i])
            pending.remove(i)
            visited.add(i)

    large = [tuple(sorted(group)) for group in maximal_cliques(set(), set(live), set())
             if len(group) >= 3 and not any(group <= witness for witness in witnesses)]
    covered = {pair for group in large for pair in combinations(group, 2)}
    pairs = [(a, b) for a in live for b in candidates[a] if a < b and (a, b) not in covered]
    return sorted(large) + sorted(pairs)


def fresh_count(arm, parents, ordinary):
    floor = max(0, 3 - parents)
    if arm == "ordinary":
        return ordinary
    if arm == "one_fewer":
        return min(ordinary, max(floor, ordinary - 1))
    if arm == "arity_floor":
        return min(ordinary, floor)
    raise ValueError(arm)


def round_detail(stage: Stage, arm="ordinary", implies=None):
    """Return the new stage, the funding status and the birth records.

    An optional implication test on the old distinctions lets an audit check
    another law without changing the growth rule or the round's demand.
    """
    neighbours, loose = meetings(stage)
    live = {i for i, stock in enumerate(loose) if stock}
    if not live:
        return stage, "closed", ()

    groups = parent_groups(neighbours, live)
    uses = Counter(i for group in groups for i in group)
    if any(uses[i] > len(loose[i]) for i in live):
        return stage, "stalled", ()
    groups.extend((i,) for i in sorted(live) for _ in range(len(loose[i]) - uses[i]))

    stock = [iter(sorted(bits)) for bits in loose]
    taken = [frozenset(next(stock[i]) for i in group) for group in groups]

    together = [set() for _ in range(len(stage) + len(groups))]
    newborns = set(range(len(stage), len(together)))
    for child, group in zip(sorted(newborns), groups, strict=True):
        together[child].update(group)
        for parent in group:
            together[parent].add(child)
    demand = Counter(i for group in parent_groups(together, newborns) for i in group)

    if implies is None:
        # A parity sum on loose distinctions selects whole connected parts.
        # Leaving out one holder of a shared distinction cannot cancel it.
        boundaries = {frozenset().union(*(loose[i] for i in part)) for part in components(neighbours)}
        implies = boundaries.__contains__

    next_id = max(max(row) for row in stage if row) + 1
    births = []
    for child, group, inputs in zip(sorted(newborns), groups, taken, strict=True):
        implied = implies(inputs)
        minimum = 0 if implied else max(1, 3 - len(group))
        ordinary = max(demand[child], minimum)
        count = fresh_count(arm, len(group), ordinary)
        fresh = frozenset(range(next_id, next_id + count))
        births.append(Birth(group, inputs, demand[child], implied, ordinary, fresh))
        # The recorded cuts retain a subset of each ordinary allocation.
        next_id += ordinary
    return stage + tuple(b.taken | b.fresh for b in births), "funded", tuple(births)


def advance(stage: Stage):
    next_stage, status, births = round_detail(stage)
    return next_stage, status, len(births)


def _supports(n, shared, loose):
    rows = [set() for _ in range(n)]
    distinction = 0
    for a, b, count in shared:
        for _ in range(count):
            rows[a].add(distinction)
            rows[b].add(distinction)
            distinction += 1
    for i, count in enumerate(loose):
        rows[i].update(range(distinction, distinction + count))
        distinction += count
    return tuple(map(frozenset, rows))


@cache
def census():
    """Read the archived roster in its recorded index order."""
    path = RESEARCH / "FORBID-EDITS-20261126-001/starts.json"
    return tuple(_supports(*record) for record in json.loads(path.read_text()))


@cache
def heldout():
    """Repeat the frozen labelled draws in their original order."""
    out = {}
    for n in (6, 7, 8):
        rng = Random(20261206 + n)
        possible = tuple(combinations(range(n), 2))
        count = 0
        while count < 300:
            pairs = [pair for pair in possible if rng.random() < 1 / 3]
            shared = [(a, b, rng.choice((1, 2))) for a, b in pairs]
            loose = [rng.choice((0, 1, 2)) for _ in range(n)]
            if sum(m for _, _, m in shared) + sum(loose) > 18:
                continue
            stage = _supports(n, shared, loose)
            if any(len(row) < 3 for row in stage):
                continue
            neighbours, _ = meetings(stage)
            if len(next(components(neighbours))) != n:
                continue
            out[n, count] = stage
            count += 1
    return out


def ring(n, loose=2):
    return tuple(frozenset((i, (i + 1) % n, *range(n + loose*i, n + loose*(i + 1)))) for i in range(n))


def _joined_rings(rings, joins):
    aliases = {b: a for kind, a, b, *_ in joins if kind == "share"}
    names = {}
    for r, n in enumerate(rings):
        for i in range(n):
            name = r, i
            names[name] = names[aliases[name]] if name in aliases else len(set(names.values()))
    shared = [(names[r, i], names[r, (i + 1) % n], 1) for r, n in enumerate(rings) for i in range(n)]
    n = len(set(names.values()))
    for kind, a, b, *length in joins:
        if kind == "share":
            continue
        middle = length[0] if length else 0
        sequence = [names[a], *range(n, n + middle), names[b]]
        shared.extend((i, j, 1) for i, j in zip(sequence, sequence[1:]))
        n += middle

    bare = _supports(n, shared, [0] * n)
    padded = _supports(n, shared, [max(0, 3 - len(row)) for row in bare])
    neighbours, loose = meetings(padded)
    demand = Counter(i for group in parent_groups(neighbours, set(range(n))) for i in group)
    next_id = max(map(max, padded)) + 1
    rows = []
    for i, row in enumerate(padded):
        extra = max(2, demand[i]) - len(loose[i])
        rows.append(row | frozenset(range(next_id, next_id + extra)))
        next_id += extra
    return tuple(rows)


@cache
def joined():
    """The funded one-ring and joined-ring starts of the tower cohort."""
    touching_cycle = (("touch", (0, 0), (1, 0)), ("touch", (1, 2), (2, 0)), ("touch", (2, 2), (0, 2)))
    specimens = (
        ("one ring of 5", (5,), ()),
        ("one ring of 7", (7,), ()),
        ("one ring of 4", (4,), ()),
        ("two rings of 5 sharing a knot", (5, 5), (("share", (0, 0), (1, 0)),)),
        ("two rings of 5 touching", (5, 5), (("touch", (0, 0), (1, 0)),)),
        ("two rings of 5 joined by a chain of 1", (5, 5), (("chain", (0, 0), (1, 0), 1),)),
        ("two rings of 5 joined by a chain of 2", (5, 5), (("chain", (0, 0), (1, 0), 2),)),
        ("three rings of 5 sharing a knot", (5, 5, 5), (("share", (0, 0), (1, 0)), ("share", (0, 0), (2, 0)))),
        ("three rings of 5 touching in a cycle", (5, 5, 5), touching_cycle),
        ("two rings of 4 touching", (4, 4), (("touch", (0, 0), (1, 0)),)),
        ("three rings of 4 touching in a cycle", (4, 4, 4), touching_cycle),
    )
    return {name: _joined_rings(rings, joins) for name, rings, joins in specimens}
