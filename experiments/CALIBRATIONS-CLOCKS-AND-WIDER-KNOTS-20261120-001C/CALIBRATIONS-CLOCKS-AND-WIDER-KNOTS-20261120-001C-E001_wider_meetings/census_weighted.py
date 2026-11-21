"""Canonical rate tables by exact point matching on the weighted quotient."""

from collections import defaultdict
from itertools import combinations
from math import factorial, prod

from census_stages import ROOT  # loads the earlier rate-key helper's location
from census_rates import PairTable, partitioned, rate_matrix, refine, twin_classes


def points(mask):
    while mask:
        item = mask & -mask
        yield item.bit_length() - 1
        mask ^= item


def images(weights):
    result = []
    for row in weights:
        classes = defaultdict(int)
        for i, rate in enumerate(row):
            classes[rate] |= 1 << i
        result.append(classes)
    return tuple(result)


def possible(cells, source, target, weights, by_color):
    domains = []
    for cell in cells:
        if len(cell) < 2:
            continue
        mask = sum(1 << i for i in cell)
        for i in cell:
            if i != source:
                available = mask & by_color[target].get(weights[source][i], 0) & ~(1 << target)
                if not available:
                    return False
                domains.append((i, available))

    def visit(remaining):
        if not remaining:
            return True
        pivot = min(range(len(remaining)), key=lambda p: remaining[p][1].bit_count())
        i, permitted = remaining[pivot]
        others = (*remaining[:pivot], *remaining[pivot + 1:])
        for j in points(permitted):
            altered = [(k, mask & by_color[j].get(weights[i][k], 0) & ~(1 << j)) for k, mask in others]
            if all(mask for _, mask in altered) and visit(altered):
                return True
        return False

    return visit(domains)


def canonical_weighted(width, total, disagreements):
    rates = rate_matrix(width, total, disagreements)
    classes = twin_classes(rates)
    signatures = tuple((len(v), *(rates[v[0]][v[1]] if len(v) > 1 else (0, 0))) for v in classes)
    weights = tuple(tuple(rates[v[0]][w[0]] for w in classes) for v in classes)
    by_color = images(weights)

    def visit(cells):
        cells = refine(cells, weights)
        split = next((i for i, cell in enumerate(cells) if len(cell) > 1), None)
        if split is None:
            order = tuple(v[0] for v in cells)
            code = (tuple(signatures[i] for i in order), tuple(weights[i][j] for i, j in combinations(order, 2)))
            return code, order, 1
        cell = cells[split]
        rest = set(cell)
        results = []
        group_order = None
        while rest:
            anchor = min(rest)
            rest.remove(anchor)
            orbit = {target for target in rest if possible(cells, anchor, target, weights, by_color)}
            rest -= orbit
            next_cell = ((anchor,), tuple(v for v in cell if v != anchor))
            code, order, stabilizer = visit((*cells[:split], *next_cell, *cells[split + 1:]))
            results.append((code, order))
            order_of_branch = (len(orbit) + 1) * stabilizer
            assert group_order is None or group_order == order_of_branch
            group_order = order_of_branch
        code, order = min(results)
        return code, order, group_order

    cells = partitioned(range(len(classes)), signatures.__getitem__)
    (labels, pairs), order, group_order = visit(cells)
    group_order *= prod(factorial(len(v)) for v in classes)
    return PairTable((width, labels, pairs), tuple(i for c in order for i in classes[c]), group_order)
