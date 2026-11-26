"""Reconstruct the numbered start catalogue and meetings for replay.

The conventional graph atlas supplies the archived catalogue numbering.
The linked sampling frame uses the earlier cap census to identify membership.
"""

from functools import cache
import gzip
from itertools import permutations, product
import json
from pathlib import Path
from random import Random
import re

from networkx import graph_atlas_g, is_connected


HOLDINGS = tuple[tuple[int, ...], ...]
NAMED_STARTS = {
    "ring": tuple(((k - 1) % 5, k, *range(5 + 3 * k, 8 + 3 * k)) for k in range(5)),
    "copier": ((0, 1, 2), (0, 3, 4)),
    "source": (
        (0, 1, 2, 9, 10, 11), (0, 1, 3), (4, 5, 12, 13, 14), (6, 7, 15, 16, 17),
        (2, 3, 4, 6, 18, 19, 20), (7, 8, 21, 22), (5, 8, 23, 24),
    ),
}
SENDERS = ("g1:3@0", "g3:22@0", "g6:122@0", "g7:122@0", "stub")
SWITCH_RECEIVER = "tri:122@0"
CENSUS_SEED = 20261126
LINKED_ARCHIVE = (
    Path(__file__).resolve().parents[2] / "LINKED-UNDER-CAP-20261126-001" / "linked_runs.jsonl.gz"
)
NUMBERED = re.compile(r"(?:n(\d+):)?g(\d+):([0-3]+)@(\d+)")
MUTUAL_THREE = re.compile(r"tri:([0-9]{3})@(\d+)")


@cache
def atlas():
    return graph_atlas_g()


def sharing_pairs(entry):
    return tuple(sorted(tuple(sorted(pair)) for pair in entry.edges))


@cache
def pattern(label: str) -> tuple[HOLDINGS, int]:
    """Return the ordered holdings and selected knot of one start."""
    if label in NAMED_STARTS:
        return NAMED_STARTS[label], 0

    if match := NUMBERED.fullmatch(label):
        size, number, loose_counts, site = match.groups()
        entry = atlas()[int(number)]
        count = len(entry)
        if size is not None and count != int(size):
            raise ValueError(f"Inconsistent count in start {label!r}")
        pairs = sharing_pairs(entry)
    elif match := MUTUAL_THREE.fullmatch(label):
        loose_counts, site = match.groups()
        count = 3
        pairs = ((0, 1), (0, 2), (1, 2))
    else:
        raise ValueError(f"Unknown start {label!r}")

    selected = int(site)
    if len(loose_counts) != count or selected >= count:
        raise ValueError(f"Inconsistent loose counts or selected knot in start {label!r}")
    holdings = [[] for _ in range(count)]
    for distinction, (first, second) in enumerate(pairs):
        holdings[first].append(distinction)
        holdings[second].append(distinction)
    next_distinction = len(pairs)
    for places, count in zip(holdings, map(int, loose_counts)):
        places.extend(range(next_distinction, next_distinction + count))
        next_distinction += count
    return tuple(map(tuple, holdings)), selected


def build_pair(receiver: str, far: str) -> tuple[HOLDINGS, tuple[str, ...]]:
    """Put the two starts in their archived order and join through two link knots."""
    holdings = []
    roles = []
    next_distinction = 0

    def put_pattern(label, role):
        nonlocal next_distinction
        places, selected = pattern(label)
        first_knot = len(holdings)
        holdings.extend([next_distinction + distinction for distinction in row] for row in places)
        roles.extend([role] * len(places))
        next_distinction += 1 + max(distinction for row in places for distinction in row)
        return first_knot + selected

    def add_knot(role):
        index = len(holdings)
        holdings.append([])
        roles.append(role)
        return index

    def meet(first, second):
        nonlocal next_distinction
        common = add_knot("spent")
        first_share, second_share, other_share, first_loose, second_loose = range(
            next_distinction, next_distinction + 5
        )
        holdings[common].extend((first_share, second_share, other_share))
        holdings[first].extend((first_share, first_loose))
        holdings[second].extend((second_share, other_share, second_loose))
        next_distinction += 5

    current = put_pattern(receiver, "A")
    destination = None if far == "stub" else put_pattern(far, "B")
    for _ in range(2):
        link = add_knot("link")
        meet(current, link)
        current = link
    if destination is None:
        destination = add_knot("B")
    meet(current, destination)
    return tuple(map(tuple, holdings)), tuple(roles)


@cache
def catalogue() -> tuple[str, ...]:
    """All 646 selected starts in census order, including named starts."""
    names = []
    for number, entry in enumerate(atlas()):
        size = len(entry)
        if size not in (1, 2, 3, 4) or not is_connected(entry):
            continue
        pairs = set(sharing_pairs(entry))
        automorphisms = [
            perm for perm in permutations(range(size))
            if {tuple(sorted((perm[first], perm[second]))) for first, second in pairs} == pairs
        ]
        counts = (range(max(3 - entry.degree(knot), 0), 4) for knot in range(size))
        for loose in product(*counts):
            if not any(loose):
                continue
            orbit = [(tuple(loose[knot] for knot in perm), perm) for perm in automorphisms]
            if loose != min(relabelled for relabelled, _ in orbit):
                continue
            fixed = [perm for relabelled, perm in orbit if relabelled == loose]
            for knot in range(size):
                if knot == min(perm[knot] for perm in fixed):
                    digits = "".join(map(str, loose))
                    names.append(f"n{size}:g{number}:{digits}@{knot}")
    return (*names, *NAMED_STARTS)


def census_pairs(*, include_controls: bool = True) -> tuple[tuple[str, str], ...]:
    """Seeded census draw and, by default, its additional control receiver."""
    receivers = catalogue()
    indices = sorted(Random(CENSUS_SEED).sample(range(len(receivers)), 100))
    sampled = [receivers[index] for index in indices]
    if include_controls:
        sampled.extend(name for name in ("n3:g7:122@0", "n4:g15:2123@0") if name not in sampled)
    return tuple((receiver, sender) for receiver in sampled for sender in SENDERS)


def linked_pairs() -> tuple[tuple[str, str], ...]:
    """Prior cap-of-three records with both patterns still linked after round 16."""
    far_ends = set()
    with gzip.open(LINKED_ARCHIVE, "rt", encoding="utf-8") as archive:
        for line in archive:
            record = json.loads(line)
            if record.get("law") != "CAP-3" or record.get("A") != SWITCH_RECEIVER:
                continue
            linkage = record["linked"]
            if len(linkage) >= 16 and linkage[15] is True:
                far_ends.add(record["B"])
    return tuple((SWITCH_RECEIVER, far) for far in sorted(far_ends))
