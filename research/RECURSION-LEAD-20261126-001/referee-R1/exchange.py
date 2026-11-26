"""Exact exchange of a finite parity pattern with at most two holders per distinction."""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import cache


Pattern = tuple[frozenset[int], ...]


def holders(pattern: Pattern) -> dict[int, tuple[int, ...]]:
    result = defaultdict(list)
    for knot, support in enumerate(pattern):
        for distinction in support:
            result[distinction].append(knot)
    return {distinction: tuple(held) for distinction, held in result.items()}


@dataclass(frozen=True)
class Exchange:
    supports: Pattern
    minima: dict[int, int]
    pins: frozenset[int]
    missing: frozenset[int]

    @property
    def failures(self) -> tuple[str, ...]:
        return tuple(reason for failed, reason in (
            (not self.supports, "empty"),
            (any(len(row) < 3 for row in self.supports), "fewer than three places"),
            (any(len(held) > 2 for held in holders(self.supports).values()), "more than two holders"),
        ) if failed)

    @property
    def lawful(self) -> bool:
        return not self.failures


def shortest_completions(links, first, last, omit):
    """Return all shortest chains between the holders with the given distinction excluded."""
    levels = {first: 0}
    predecessors = defaultdict(list)
    pending = deque([first])
    while pending:
        here = pending.popleft()
        level = levels[here] + 1
        if last in levels and level > levels[last]:
            break
        for there, distinction in links[here]:
            if distinction == omit:
                continue
            if there not in levels:
                levels[there] = level
                pending.append(there)
            if levels[there] == level:
                predecessors[there].append((here, distinction))

    @cache
    def chains(knot):
        if knot == first:
            return (0,)
        return tuple(prefix | (1 << distinction)
                     for previous, distinction in predecessors[knot] for prefix in chains(previous))

    if last not in levels:
        return None, ()
    return levels[last], chains(last)


def exchange(pattern: Pattern, pinned: bool | frozenset[int]) -> Exchange:
    """Read every tied shortest allowed change through each distinction.

    An allowed change has even incidence at each knot. Attach each free loose
    distinction to one additional holder. The additional parity equation is
    the sum of the original equations. Each even-incidence selection splits
    into closed chains, so a minimum through one distinction is that distinction
    and a shortest chain between its holders after removing it.
    """
    incidence = holders(pattern)
    if any(len(held) > 2 for held in incidence.values()):
        raise ValueError("exchange requires at most two holders per distinction")
    if pinned is True:
        pins = frozenset(d for d, held in incidence.items() if len(held) == 1)
    elif pinned is False:
        pins = frozenset()
    else:
        pins = frozenset(pinned)
        if pins - incidence.keys():
            raise ValueError("unknown pinned distinction")

    names = sorted(incidence.keys() - pins)
    links = [[] for _ in range(len(pattern) + 1)]
    pairs = []
    for index, name in enumerate(names):
        held = incidence[name]
        first, last = held if len(held) == 2 else (held[0], len(pattern))
        pairs.append((first, last))
        links[first].append((last, index))
        links[last].append((first, index))

    minima, changes = {}, set()
    for index, (first, last) in enumerate(pairs):
        length, paths = shortest_completions(links, first, last, index)
        if length is not None:
            minima[names[index]] = length + 1
            changes.update(path | (1 << index) for path in paths)

    supports = tuple(frozenset(names[i] for i in positions(change)) for change in sorted(changes))
    return Exchange(supports, minima, pins, frozenset(set(names) - minima.keys()))


def positions(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def sharing(pattern):
    by_pair = [Counter() for _ in pattern]
    loose = [0] * len(pattern)
    for held in holders(pattern).values():
        if len(held) == 1:
            loose[held[0]] += 1
        elif len(held) == 2:
            i, j = held
            by_pair[i][j] += 1
            by_pair[j][i] += 1
        else:
            raise ValueError("comparison requires at most two holders per distinction")
    return by_pair, loose


def renaming(source: Pattern, target: Pattern):
    """Find a bijection preserving every holder, distinction and loose count."""
    if len(source) != len(target):
        return None
    share_source, loose_source = sharing(source)
    share_target, loose_target = sharing(target)
    colors = [(loose, tuple(sorted(shared.values()))) for loose, shared in zip(loose_source, share_source)]
    target_colors = [(loose, tuple(sorted(shared.values()))) for loose, shared in zip(loose_target, share_target)]
    if Counter(colors) != Counter(target_colors):
        return None
    candidates = [tuple(j for j, color in enumerate(target_colors) if color == c) for c in colors]
    order = sorted(range(len(source)), key=lambda i: (len(candidates[i]), -len(share_source[i])))

    def match(depth, assigned, occupied):
        if depth == len(order):
            return assigned.copy()
        i = order[depth]
        for j in candidates[i]:
            if j in occupied or any(share_source[i][k] != share_target[j][l] for k, l in assigned.items()):
                continue
            assigned[i] = j
            occupied.add(j)
            result = match(depth + 1, assigned, occupied)
            if result is not None:
                return result
            occupied.remove(j)
            del assigned[i]
        return None

    knots = match(0, {}, set())
    if knots is None:
        return None
    target_buckets = defaultdict(list)
    for d, held in holders(target).items():
        target_buckets[held].append(d)
    distinctions = {}
    for d, held in sorted(holders(source).items()):
        distinctions[d] = target_buckets[tuple(sorted(knots[i] for i in held))].pop()

    assert set(distinctions.values()) == set(holders(target))
    assert all(frozenset(distinctions[d] for d in row) == target[knots[i]] for i, row in enumerate(source))
    return {"knots": knots, "distinctions": distinctions}


def parity_columns(pattern, pins=frozenset()):
    incidence = holders(pattern)
    names = sorted(incidence.keys() - pins)
    return names, [sum(1 << knot for knot in incidence[d]) for d in names]


def kernel_basis(columns):
    """Count and construct independent parity dependencies by column elimination."""
    pivots, dependencies = {}, []
    for i, column in enumerate(columns):
        word = 1 << i
        while column:
            top = column.bit_length() - 1
            if top not in pivots:
                pivots[top] = column, word
                break
            other_column, other_word = pivots[top]
            column ^= other_column
            word ^= other_word
        else:
            dependencies.append(word)
    return dependencies
