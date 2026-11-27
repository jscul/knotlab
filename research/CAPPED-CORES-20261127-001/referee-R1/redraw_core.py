"""Independent parent-incidence calculation for the capped-start redraw."""

from collections import Counter, defaultdict
from itertools import combinations
from math import comb


class LimitReached(Exception):
    def __init__(self, criterion, lower_bound):
        self.criterion = criterion
        self.lower_bound = lower_bound


def maximal_families(neighbors):
    """Enumerate maximal pairwise-sharing families by pivoted backtracking."""
    remaining = set(neighbors)
    while remaining:
        first = min(remaining)
        component = {first}
        pending = [first]
        while pending:
            for other in neighbors[pending.pop()] - component:
                component.add(other)
                pending.append(other)
        remaining.difference_update(component)

        if all(len(neighbors[knot]) == len(component) - 1 for knot in component):
            yield frozenset(component)
            continue

        # Explicit stack keeps a wide family from consuming the recursion limit.
        possible, excluded = set(component), set()
        stack = [((), possible, excluded, None)]
        while stack:
            family, possible, excluded, choices = stack[-1]
            if choices is None:
                if not possible:
                    if not excluded:
                        yield frozenset(family)
                    stack.pop()
                    continue
                pivot = max(
                    possible | excluded,
                    key=lambda member: (len(possible & neighbors[member]), -member),
                )
                choices = iter(sorted(possible - neighbors[pivot]))
                stack[-1] = (family, possible, excluded, choices)
            member = next(choices, None)
            if member is None:
                stack.pop()
                continue
            next_possible = possible & neighbors[member]
            next_excluded = excluded & neighbors[member]
            possible.remove(member)
            excluded.add(member)
            stack.append(((*family, member), next_possible, next_excluded, None))


def parent_incidence_round(current, budget=None, pair_cap=None):
    children = defaultdict(list)
    for member, parents in current.items():
        for parent in parents:
            children[parent].append(member)
    pair_count = sum(comb(len(family), 2) for family in children.values())
    if pair_cap is not None and pair_count > pair_cap:
        raise LimitReached("parent-sharing pair occurrences in one rank", pair_count)

    neighbors = {member: set() for member in current}
    for family in children.values():
        for member in family:
            neighbors[member].update(family)
            neighbors[member].remove(member)

    births = []
    explained = defaultdict(set)
    listed = 0
    for listed, family in enumerate(maximal_families(neighbors), 1):
        if budget is not None and listed > budget:
            raise LimitReached("maximal pairwise-sharing families in one rank", listed)
        if len(family) < 3 or set.intersection(*(current[member] for member in family)):
            continue
        births.append(tuple(sorted(family)))
        for member in family:
            explained[member].update(family)
    for member, meets in neighbors.items():
        for other in meets - explained[member]:
            if member < other:
                births.append((member, other))
                if budget is not None and len(births) > budget:
                    raise LimitReached("births beyond remaining core budget", len(births))
    return tuple(sorted(births)), pair_count, listed


def brute_round(current):
    """Small-case control that tests every subset directly."""
    candidates = []
    for size in range(2, len(current) + 1):
        for family in combinations(current, size):
            if any(not (current[a] & current[b]) for a, b in combinations(family, 2)):
                continue
            if size == 2 or not set.intersection(*(current[member] for member in family)):
                candidates.append(frozenset(family))
    return tuple(sorted(tuple(sorted(family)) for family in candidates
                        if not any(family < larger for larger in candidates)))


def first_ranks(sizes, shared_distinctions):
    overlaps = [set() for _ in sizes]
    held = Counter()
    for a, b in shared_distinctions:
        overlaps[a].add(b)
        overlaps[b].add(a)
        held.update((a, b))
    loose = [places - held[knot] for knot, places in enumerate(sizes)]
    live = {knot for knot, count in enumerate(loose) if count > 0}
    parent_sets = {knot: overlaps[knot] for knot in sorted(live)}
    groups, _, _ = parent_incidence_round(parent_sets)
    demands = Counter(knot for family in groups for knot in family)
    offshoots = [loose[knot] - demands[knot] if knot in live else 0
                 for knot in range(len(sizes))]
    return loose, groups, offshoots, bool(live) and min(offshoots) >= 0


def pieces(loose, groups, offshoots):
    live = {knot for knot, count in enumerate(loose) if count > 0}
    memberships = {knot: {knot} for knot in live}
    for family in groups:
        joined = set().union(*(memberships[knot] for knot in family))
        for knot in joined:
            memberships[knot] = joined
    for knots in sorted({tuple(sorted(family)) for family in memberships.values()}):
        in_piece = set(knots)
        rank_one = [family for family in groups if family[0] in in_piece]
        rank_one.extend((knot,) for knot in knots for _ in range(offshoots[knot]))
        yield knots, tuple(rank_one)


def progress(rank_zero, rank_one, *, node_cap, pair_cap, last_rank):
    """Record exact widths and any bound that prevented the next rank."""
    current = {knot: set(family) for knot, family in enumerate(rank_one)}
    widths = [len(rank_zero), len(current)]
    count = sum(widths)
    rank_log = []
    subset_pattern = None
    for rank in range(1, last_rank):
        if not current:
            break
        common = set.intersection(*current.values())
        if len(current) > 1 and common and subset_pattern is None:
            subset_pattern = {"rank": rank, "width": len(current),
                              "common_parent_count": len(common)}
        try:
            births, pair_count, listed = parent_incidence_round(
                current, node_cap - count, pair_cap
            )
        except LimitReached as limit:
            return {
                "rank_widths": widths,
                "round_transitions": rank_log,
                "stop": "cap",
                "next_rank": rank + 1,
                "completed_node_count": count,
                "criterion": limit.criterion,
                "lower_bound": limit.lower_bound,
                "subset_pattern": subset_pattern,
            }
        rank_log.append({"parent_share_occurrences": pair_count,
                         "maximal_pairwise_families": listed})
        current = {knot: set(family) for knot, family in enumerate(births)}
        widths.append(len(current))
        count += widths[-1]
    return {
        "rank_widths": widths,
        "round_transitions": rank_log,
        "stop": "empty rank" if not current else "rank horizon",
        "completed_node_count": count,
        "subset_pattern": subset_pattern,
    }
