"""Exact comparison of support families by individualizing only distinctions."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from math import factorial, prod


def bits(mask):
    while mask:
        item = mask & -mask
        yield item.bit_length() - 1
        mask ^= item


@dataclass
class Incidences:
    distinctions: tuple
    colors: tuple
    neighbors: tuple
    supports: Counter

    @property
    def groups(self):
        return len(self.distinctions)

    @property
    def twin_order(self):
        return prod(factorial(len(group)) for group in self.distinctions)

    @property
    def signature(self):
        return tuple(sorted(Counter(zip(self.colors, map(len, self.neighbors), strict=True)).items()))


def incidence_family(width, supports):
    same_owners = defaultdict(list)
    for i in range(width):
        same_owners[tuple(j for j, mask in enumerate(supports) if mask & (1 << i))].append(i)
    groups = tuple(map(tuple, same_owners.values()))
    m = len(groups)
    h = len(supports)
    rows = [0] * h
    point_neighbors = []
    for g, group in enumerate(same_owners):
        point_neighbors.append(tuple(m + j for j in group))
        for j in group:
            rows[j] |= 1 << g
    arcs = tuple(point_neighbors) + tuple(tuple(bits(row)) for row in rows)
    colors = tuple((0, len(group)) for group in groups) + tuple((1, mask.bit_count()) for mask in supports)
    return Incidences(groups, colors, arcs, Counter(rows))


def normalize(left, right):
    codes = {v: i for i, v in enumerate(sorted(set(left) | set(right)))}
    return tuple(codes[x] for x in left), tuple(codes[x] for x in right)


def refine(left, right, left_colors, right_colors):
    while True:
        if Counter(left_colors) != Counter(right_colors):
            return None

        def signatures(family, colors):
            return tuple((c, tuple(sorted(colors[i] for i in adj)))
                         for c, adj in zip(colors, family.neighbors, strict=True))

        a, b = normalize(signatures(left, left_colors), signatures(right, right_colors))
        if len(set(a)) == len(set(left_colors)) and len(set(b)) == len(set(right_colors)):
            if Counter(a) != Counter(b):
                return None
            return a, b
        left_colors, right_colors = a, b


def point_classes(size, colors):
    by_color = defaultdict(list)
    for i in range(size):
        by_color[colors[i]].append(i)
    return by_color


def pinned(colors, i, code):
    return colors[:i] + (code,) + colors[i + 1:]


def matching(left, right, colors=None):
    if left.groups != right.groups or left.signature != right.signature:
        return None
    if colors is None:
        colors = normalize(left.colors, right.colors)

    def visit(a, b):
        stable = refine(left, right, a, b)
        if stable is None:
            return None
        a, b = stable
        lclasses = point_classes(left.groups, a)
        rclasses = point_classes(right.groups, b)
        unresolved = [c for c, members in lclasses.items() if len(members) > 1]
        if not unresolved:
            move = tuple(rclasses[a[i]][0] for i in range(left.groups))
            recoded = Counter({sum(1 << move[i] for i in bits(row)): k for row, k in left.supports.items()})
            return move if recoded == right.supports else None
        c = min(unresolved, key=lambda key: (len(lclasses[key]), key))
        i = lclasses[c][0]
        code = max(a) + 1
        for j in rclasses[c]:
            solution = visit(pinned(a, i, code), pinned(b, j, code))
            if solution is not None:
                return solution
        return None

    return visit(*colors)


def automorphisms(family):
    colors = normalize(family.colors, family.colors)[0]
    order = family.twin_order
    while True:
        colors = refine(family, family, colors, colors)[0]
        cells = point_classes(family.groups, colors)
        unresolved = [v for v in cells.values() if len(v) > 1]
        if not unresolved:
            return order
        orbit = min(unresolved, key=len)
        i = orbit[0]
        code = max(colors) + 1
        individualized = pinned(colors, i, code)
        order *= 1 + sum(matching(family, family, (individualized, pinned(colors, j, code))) is not None
                         for j in orbit[1:])
        colors = individualized
