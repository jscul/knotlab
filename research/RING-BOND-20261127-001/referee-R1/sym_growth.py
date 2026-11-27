"""Incidence symmetries and checked ordinary birth histories."""

from collections import defaultdict
from itertools import permutations, product
from math import factorial, prod
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
RESEARCH = STUDY.parent
EARLIER = RESEARCH / "NAE-LAYER-20261127-001" / "referee-R1"
sys.path.insert(0, str(EARLIER))
from growth_rule import advance, supports_of


RING = ((0, 1, 3), (1, 2, 4), (2, 0, 5))


def owner_classes(supports):
    holders = defaultdict(list)
    for knot, support in enumerate(supports):
        for x in support:
            holders[x].append(knot)
    by_holders = defaultdict(list)
    for x, owners in sorted(holders.items()):
        by_holders[tuple(owners)].append(x)
    return dict(by_holders)


def eligible_knot_permutations(supports):
    """Every colour-preserving renaming of knots, ignoring the order within supports."""
    by_holders = owner_classes(supports)
    profiles = {
        knot: (len(support), len(by_holders.get((knot,), [])))
        for knot, support in enumerate(supports)
    }
    groups = defaultdict(list)
    for knot, profile in profiles.items():
        groups[profile].append(knot)
    for pieces in product(*(permutations(group) for group in groups.values())):
        rename = dict(zip((i for group in groups.values() for i in group), (j for p in pieces for j in p)))
        image = {
            owners: tuple(sorted(rename[knot] for knot in owners))
            for owners in by_holders
        }
        if all(len(by_holders.get(new, ())) == len(by_holders[old]) for old, new in image.items()):
            yield rename, image


def symmetry_orders(supports):
    by_holders = owner_classes(supports)
    knot_order = sum(1 for _ in eligible_knot_permutations(supports))
    return knot_order, knot_order * prod(factorial(len(group)) for group in by_holders.values())


def distinction_maps(supports):
    by_holders = owner_classes(supports)
    for _, image in eligible_knot_permutations(supports):
        source = tuple(x for group in by_holders.values() for x in group)
        for groups in product(*(permutations(by_holders[image[owners]]) for owners in by_holders)):
            yield dict(zip(source, (y for group in groups for y in group), strict=True))


def history(start, rounds):
    stages = [tuple(tuple(s) for s in start)]
    births = []
    for _ in range(rounds):
        result = advance(stages[-1])
        if result.status != "funded":
            break
        stages.append(result.supports)
        births.append(result.births)
    return stages, births


def check_maps(start, order, rename_start, rounds):
    """Check the stated identity map at each round, for both supports and birth records."""
    stages, growth = history(start, rounds)
    relabelled = tuple(tuple(rename_start[x] for x in start[k]) for k in order)
    others, growth_other = history(relabelled, rounds)
    offset = max(rename_start.values()) - max(rename_start)
    def rename(x):
        return rename_start[x] if x in rename_start else x + offset

    def knot(k):
        return order.index(k) if k < len(start) else k

    stages_ok = []
    for stage, other in zip(stages, others, strict=True):
        stages_ok.append(all({rename(x) for x in support} == set(other[knot(k)])
                             for k, support in enumerate(stage)))
    births_ok = []
    for step, other_step in zip(growth, growth_other, strict=True):
        by_knot = {b.knot: b for b in other_step}
        ok = True
        for b in step:
            c = by_knot[knot(b.knot)]
            ok &= (set(c.parents) == {knot(p) for p in b.parents}
                   and set(c.inputs) == {rename(x) for x in b.inputs}
                   and set(c.fresh) == {rename(x) for x in b.fresh}
                   and c.demand == b.demand)
        births_ok.append(ok)
    return stages_ok, births_ok


def history_graph(stages, anchored=None):
    """A distinction's two holders of different ages identify its birth and its spending."""
    import networkx as nx

    graph = nx.Graph()
    knots_seen = 0
    distinctions_seen = set()
    anchor = anchored or {}
    for age, stage in enumerate(stages):
        for k in range(knots_seen, len(stage)):
            graph.add_node(("k", k), colour=("knot", age))
            for x in stage[k]:
                if x not in distinctions_seen:
                    colour = ("fixed", anchor[x]) if x in anchor else ("distinction", age)
                    graph.add_node(("d", x), colour=colour)
                    distinctions_seen.add(x)
                graph.add_edge(("k", k), ("d", x))
        knots_seen = len(stage)
    return graph


def extendible_maps(stages, group):
    """Return exactly the earlier renamings admitting an extension of the coloured history."""
    from networkx.algorithms.isomorphism import GraphMatcher

    identity = {x: x for x in group[0]}
    target = history_graph(stages, identity)
    kept = []
    for mapping in group:
        source = history_graph(stages, mapping)
        match = GraphMatcher(source, target, node_match=lambda a, b: a["colour"] == b["colour"])
        if match.is_isomorphic():
            kept.append(mapping)
    return kept
