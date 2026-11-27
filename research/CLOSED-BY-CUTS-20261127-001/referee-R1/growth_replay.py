"""Replay the two fresh-distinction cuts on the frozen census archive."""

from collections import Counter, defaultdict
from dataclasses import replace
from functools import cache
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
ARCHIVE = RESEARCH / "FORBID-EDITS-20261126-001/starts.json"
LAWS = ("one_fewer", "arity_floor")

sys.path.insert(0, str(RESEARCH / "NAE-LAYER-20261127-001/referee-R1"))
from growth_rule import advance as ordinary_advance, groups, holders, loose, supports_of


@cache
def census_starts():
    """Return indexed support tuples in the archived census order."""
    return tuple(supports_of(row) for row in json.loads(ARCHIVE.read_text()))


def advance(supports, law):
    """Use the independent ordinary allotment to apply A129 or A130."""
    if law not in LAWS:
        raise ValueError(law)
    ordinary = ordinary_advance(supports)
    if ordinary.status != "funded":
        return ordinary

    # A cut retains the earliest IDs in each ordinary allotment. Omitted
    # IDs stay omitted, even when a later birth still has one to retain.
    births = []
    for birth in ordinary.births:
        floor = max(0, 3 - len(birth.parents))
        ordinary_count = len(birth.fresh)
        cutoff = max(floor, ordinary_count - 1) if law == "one_fewer" else floor
        keep = min(ordinary_count, cutoff)
        births.append(replace(birth, fresh=birth.fresh[:keep]))
    old_supports = ordinary.supports[:len(supports)]
    new_supports = tuple(birth.inputs + birth.fresh for birth in births)
    return replace(ordinary, supports=old_supports + new_supports, births=tuple(births))


def stages(start_supports, law, through=6):
    """Yield formed rounds and their supports, including round zero."""
    supports = start_supports
    yield 0, supports
    for round_number in range(1, through + 1):
        growth = advance(supports, law)
        if growth.status != "funded":
            return
        supports = growth.supports
        yield round_number, supports


def stage_funding(supports):
    """Return status and shortages without forming a further round."""
    overlaps = defaultdict(set)
    loose_counts = Counter()
    for owners in holders(supports).values():
        if len(owners) == 1:
            loose_counts.update(owners)
        else:
            first, second = owners
            overlaps[first].add(second)
            overlaps[second].add(first)
    if not loose_counts:
        return "closed", {}
    demand = Counter(knot for group in groups(overlaps, set(loose_counts)) for knot in group)
    shortages = dict(demand - loose_counts)
    return ("stalled" if shortages else "funded"), shortages


def stage_status(supports):
    return stage_funding(supports)[0]
