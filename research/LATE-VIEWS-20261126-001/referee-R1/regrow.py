"""Replay complete-round cheapest growth from the starting distinctions.

Definitions: the joining roster in WALL-READ, Lemma R in REDUCE-BLOCKS,
and the fresh-distinction rule in FRESH-COUNT and NAE-GROWTH.

Inputs are the numbered distinctions of each start knot, a law, and a
round and knot cap. The output contains one histogram of each reading
per completed birth round, the stop reason, and the number of knots.
Optional traces give each birth's parent indices in the preceding round
and its number of fresh distinctions. Each trace is independent of the
saved growth and the frozen predictions.
"""

from collections import Counter, defaultdict
from itertools import combinations


PAIR_INCIDENCE_LIMIT = 2_000_000
SEARCH_LIMIT = 1_000_000
RECURSION_LIMIT = 500


class ReplayLimit(Exception):
    """A roster exceeded an explicit resource limit."""


def start_state(stars):
    holders = defaultdict(list)
    for knot, distinctions in enumerate(stars):
        if len(distinctions) < 3 or len(distinctions) != len(set(distinctions)):
            raise ValueError("a start knot must hold at least three distinct distinctions")
        for distinction in distinctions:
            holders[distinction].append(knot)

    loose = [0] * len(stars)
    neighbours = [set() for _ in stars]
    for owners in holders.values():
        if len(owners) == 1:
            loose[owners[0]] += 1
        elif len(owners) == 2:
            a, b = owners
            neighbours[a].add(b)
            neighbours[b].add(a)
        else:
            raise ValueError("a distinction has more than two holders")

    # The parity exception uses the total of the loose distinctions of
    # a connected start. Every subsequent birth keeps that connectedness.
    unseen = set(range(len(stars))) - {0}
    agenda = [0] if stars else []
    while agenda:
        found = neighbours[agenda.pop()] & unseen
        unseen.difference_update(found)
        agenda.extend(found)
    if unseen:
        raise ValueError("the replay expects a connected start")

    live = {i for i, count in enumerate(loose) if count}
    return loose, [block & live for block in neighbours]


def joins(total, blocks):
    """Find maximal sets of pairwise candidates with no common block.

    Then add each candidate pair that lies in none of those sets.
    """
    blocks = tuple({frozenset(block) for block in blocks if len(block) > 1})
    pair_incidences = sum(len(block) * (len(block) - 1) // 2 for block in blocks)
    if pair_incidences > PAIR_INCIDENCE_LIMIT:
        raise ReplayLimit("candidate pair incidences")

    candidate = [set() for _ in range(total)]
    memberships = [set() for _ in range(total)]
    for block_id, block in enumerate(blocks):
        for knot in block:
            candidate[knot].update(block)
            candidate[knot].discard(knot)
            memberships[knot].add(block_id)

    groups = []
    visited = 0

    def seek(members, possible, earlier, common_blocks):
        nonlocal visited
        visited += 1
        if visited > SEARCH_LIMIT or len(members) >= RECURSION_LIMIT:
            raise ReplayLimit("maximal candidate search")
        if len(members) + len(possible) < 3:
            return
        if any(possible <= blocks[block_id] for block_id in common_blocks):
            return
        if not possible:
            if not earlier:
                groups.append(tuple(sorted(members)))
            return

        # Branch on a proposed member and remove candidates incompatible
        # with it. A pivot omits branches already reached with a neighbour.
        pivot = max(possible | earlier, key=lambda knot: len(possible & candidate[knot]))
        for knot in sorted(possible - candidate[pivot]):
            seek(
                (*members, knot),
                possible & candidate[knot],
                earlier & candidate[knot],
                common_blocks & memberships[knot],
            )
            possible.remove(knot)
            earlier.add(knot)

    for knot, neighbours in enumerate(candidate):
        possible = {other for other in neighbours if other > knot}
        if len(possible) >= 2:
            seek((knot,), possible, neighbours - possible, memberships[knot])

    for group in groups:
        for a, b in combinations(group, 2):
            candidate[a].discard(b)
            candidate[b].discard(a)
    pairs = [
        (a, b)
        for a, neighbours in enumerate(candidate)
        for b in sorted(neighbours)
        if a < b
    ]
    return sorted(groups) + pairs


def demand(total, roster):
    counts = [0] * total
    for parents in roster:
        for parent in parents:
            counts[parent] += 1
    return counts


def children_by_parent(parent_count, births):
    children = [set() for _ in range(parent_count)]
    for child, parents in enumerate(births):
        for parent in parents:
            children[parent].add(child)
    return children


def read_births(births, fresh, older):
    current = []
    sig0, sig1 = Counter(), Counter()
    for parents, new in zip(births, fresh, strict=True):
        count = len(parents)
        kind = "offshoot" if count == 1 else "join"
        description = (kind, count, new, count + new)
        parent_descriptions = tuple(sorted(older[i] for i in parents))
        current.append(description)
        sig0[description] += 1
        sig1[description, parent_descriptions] += 1
    row = {
        "n": len(births),
        "sig0": [[list(kind), count] for kind, count in sorted(sig0.items())],
        "sig1": [
            [[list(kind), [list(parent) for parent in parent_kinds]], count]
            for (kind, parent_kinds), count in sorted(sig1.items())
        ],
    }
    return current, row


def grow(stars, rounds=24, law="nae", cap=30_000, trace_rounds=0):
    if law not in ("nae", "parity"):
        raise ValueError(f"unknown knot law {law!r}")

    loose, blocks = start_state(stars)
    older = [("start", 0, 0, len(distinctions)) for distinctions in stars]
    size = len(stars)
    rows, traces = [], []
    end = "rounds"
    try:
        roster = joins(len(loose), blocks)
        for round_number in range(1, rounds + 1):
            asks = demand(len(loose), roster)
            if any(used > supply for used, supply in zip(asks, loose, strict=True)):
                end = f"stalls at round {round_number}"
                break
            if not any(loose):
                end = f"closes at round {round_number}"
                break

            births = roster + [
                (knot,)
                for knot, (used, supply) in enumerate(zip(asks, loose, strict=True))
                for _ in range(supply - used)
            ]
            assert sum(map(len, births)) == sum(loose)
            candidates = children_by_parent(len(loose), births)
            next_roster = joins(len(births), candidates)
            next_demand = demand(len(births), next_roster)
            if len(births) == 1 and law == "parity":
                fresh = [0]
            else:
                fresh = [
                    max(1, 3 - len(parents), asks_next)
                    for parents, asks_next in zip(births, next_demand, strict=True)
                ]

            if round_number <= trace_rounds:
                traces.append([
                    {"parents": list(parents), "fresh": new, "parent descriptions": [older[i] for i in parents]}
                    for parents, new in zip(births, fresh, strict=True)
                ])
            older, row = read_births(births, fresh, older)
            rows.append(row)
            size += len(births)
            if size > cap:
                end = "bound"
                break
            loose, roster = fresh, next_roster
    except ReplayLimit as limit:
        end = f"replay limit: {limit}"
    return {"rows": rows, "end": end, "knots": size, "traces": traces}
