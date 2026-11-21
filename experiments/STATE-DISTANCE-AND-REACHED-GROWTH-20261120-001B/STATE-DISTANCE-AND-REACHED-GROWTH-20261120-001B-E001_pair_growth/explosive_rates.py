"""Exact pair probabilities for uniform and recursively inherited word weights."""

from argparse import ArgumentParser
from bisect import bisect_right
from collections import Counter
from functools import cache
from itertools import combinations
from math import prod

import networkx as nx
import numpy as np

from explosive_stages import LAWS, components, read, write
from census_exact_rates import Operation, owners
from census_rate_tables import group_width, parity_table
from census_rates import point_group
from census_weighted import canonical_weighted
from census_stages import width


WEIGHTS = ('uniform', 'inherited')
PEAK_CELLS = 531441
CELL_BUDGET = 300_000_000


def rules(rows, limits, weighting):
    """Pin classes, integer expansion coefficients and common scale per holder.

    A pin is 0 (omitted), 1 (the bit 0) or 2 (the bit 1). A branch
    specifies the input pin and fresh pin separately. At a funded cut,
    conditional choices of fresh words are independent across births.
    """
    for i, row in enumerate(rows):
        age = bisect_right(limits, i)
        if age == 0 or weighting == 'uniform':
            yield ((0, 0), (1, 1), (2, 2)), (1, -1, -1), 1
            continue
        older = set().union(*rows[:limits[age - 1]])
        inputs = len(older.intersection(row))
        size = 1 << (len(row) - inputs)
        assert inputs >= 1 and size >= 2
        if inputs == 1:
            yield ((0, 0), (1, 1), (2, 2)), (1, -1, -1), size - 1
        else:
            # (a-1) + [inputs constant] - a [whole holder constant].
            yield ((0, 0), (1, 0), (2, 0), (1, 1), (2, 2)), (size - 1, 1, 1, -size, -size), size * (size - 1)


def pin_array(scope, count, pins, limits):
    shape = tuple(len(pins[i]) for i in scope)
    base = np.empty(shape, dtype=object)
    odd, even = base.copy(), base.copy()
    born = max(scope)
    has_parent = len(scope) == 2 and bisect_right(limits, scope[0]) < bisect_right(limits, scope[1])
    input_roles = tuple(not (i == born and has_parent) for i in scope)
    for settings in np.ndindex(shape):
        imposed = {pins[i][mode][role] for i, mode, role in zip(scope, settings, input_roles, strict=True)} - {0}
        if len(imposed) > 1:
            base[settings] = odd[settings] = even[settings] = 0
        elif imposed:
            base[settings] = even[settings] = 1
            odd[settings] = 1 if 1 in imposed else -1
        else:
            base[settings] = 1 << count
            odd[settings] = even[settings] = 0
    return base, odd, even


class Contraction:
    def __init__(self, sizes, rows, limits, weighting, reverse_ties=False):
        self.scopes = tuple(sorted(sizes))
        self.index = {scope: i for i, scope in enumerate(self.scopes)}
        pins, coefficients, scales = zip(*rules(rows, limits, weighting), strict=True)
        self.scale = prod(scales)
        dims = tuple(len(p) for p in pins)
        factors = [pin_array(s, sizes[s], pins, limits) for s in self.scopes]
        self.values = [f[0] for f in factors] + [np.array(c, dtype=object) for c in coefficients]
        self.markings = tuple((f[1], f[2]) for f in factors)
        pending = dict(enumerate((*self.scopes, *((i,) for i in range(len(rows))))))
        masks = {i: 1 << i for i in pending}
        sequence = []
        remaining = set(range(len(rows)))
        while remaining:
            near = {i: set().union(*(set(scope) for scope in pending.values() if i in scope)) for i in remaining}
            index = min(remaining, key=lambda i: (prod(dims[h] for h in near[i]), i if reverse_ties else -i))
            remaining.remove(index)
            used = tuple(i for i, scope in pending.items() if index in scope)
            union = tuple(sorted(near[index]))
            shape = tuple(tuple(dims[h] if h in pending[i] else 1 for h in union) for i in used)
            rest = tuple(i for i in union if i != index)
            dependency = 0
            for i in used:
                dependency |= masks[i]
                del pending[i]
            target = len(self.values)
            self.values.append(None)
            pending[target] = rest
            masks[target] = dependency
            sequence.append(Operation(target, used, shape, union.index(index), dependency, prod(dims[i] for i in union)))
        assert all(not scope for scope in pending.values())
        self.output = tuple(pending)
        self.sequence = tuple(sequence)

    def measure(self, first=None, second=None):
        storage = self.values if first is None else self.values.copy()
        if first is None:
            changed = -1
        elif first == second:
            changed = 1 << first
            storage[first] = self.markings[first][1]
        else:
            changed = (1 << first) | (1 << second)
            for place in (first, second):
                storage[place] = self.markings[place][0]
        for op in self.sequence:
            if op.dependency_mask & changed:
                terms = iter(value.reshape(shape) for value, shape in ((storage[i], s) for i, s in zip(op.inputs, op.shapes, strict=True)))
                joined = next(terms)
                for term in terms:
                    joined = joined * term
                storage[op.result] = np.asarray(joined.sum(axis=op.removed_axis), dtype=object)
        return prod(int(storage[i]) for i in self.output)

    def estimate(self, query_classes):
        peak = max(op.volume for op in self.sequence)
        masks = [-1] + [(1 << a) | (1 << b) for (a, b), _ in query_classes]
        work = sum(op.volume * len(op.inputs) for changed in masks
                   for op in self.sequence if op.dependency_mask & changed)
        return dict(queries=len(query_classes), peak_cells=peak, total_cells=work)


def scope_moves(sizes, holders, limits, plan):
    graph = nx.Graph()
    graph.add_nodes_from((i, {'kind': ('holder', bisect_right(limits, i), sizes[i,])}) for i in range(holders))
    for at, (scope, size) in enumerate((p for p in sizes.items() if len(p[0]) == 2), start=holders):
        graph.add_node(at, kind=('meeting', size))
        graph.add_edges_from((at, i) for i in scope)
    order, generators = point_group(graph, holders, keep_generators=True)
    moves = []
    for generator in generators:
        targets = tuple(tuple(sorted(generator[h] for h in scope)) for scope in plan.scopes)
        assert all(sizes[a] == sizes[b] for a, b in zip(plan.scopes, targets, strict=True))
        moves.append(tuple(plan.index[t] for t in targets))
    return tuple(moves), order


def scope_queries(plan, sizes, moves):
    queries = set(combinations(range(len(plan.scopes)), 2))
    queries.update((i, i) for i, scope in enumerate(plan.scopes) if sizes[scope] >= 2)
    while queries:
        source = min(queries)
        selected = [source]
        queries.remove(source)
        for i, j in selected:
            for move in moves:
                target = tuple(sorted((move[i], move[j])))
                if target in queries:
                    queries.remove(target)
                    selected.append(target)
        yield source, tuple(selected)


@cache
def component_plan(rows, limits, weighting):
    held = owners(rows)
    sizes = Counter(held.values())
    plan = Contraction(sizes, rows, limits, weighting)
    moves, automorphisms = scope_moves(sizes, len(rows), limits, plan)
    queries = tuple(scope_queries(plan, sizes, moves))
    estimate = plan.estimate(queries) | {'holder_permutations': automorphisms, 'holder_count': len(rows),
                                          'width': width(rows), 'weight': weighting, 'limits': limits}
    return held, plan, queries, estimate


@cache
def component_rates(rows, limits, weighting):
    held, plan, queries, estimate = component_plan(rows, limits, weighting)
    if estimate['peak_cells'] > PEAK_CELLS or estimate['total_cells'] > CELL_BUDGET:
        raise ValueError(('contraction resource gate', estimate))
    total = plan.measure()
    assert total > 0
    if weighting == 'inherited':
        source = rows[:limits[0]]
        source_held = owners(source)
        end = Contraction(Counter(source_held.values()), source, (), 'uniform').measure()
        assert total == end * plan.scale
    pairs = {}
    for pair, copies in queries:
        signed = plan.measure(*pair)
        assert -total <= signed <= total and (total - signed) % 2 == 0
        for copy in copies:
            pairs[copy] = (total - signed) // 2
    scattered = {(x, y): pairs[tuple(sorted((plan.index[held[x]], plan.index[held[y]])))]
                 for x, y in combinations(sorted(held), 2)}
    return total, scattered, estimate


def compact(stage):
    rows = tuple(tuple(row) for row in stage['rows'])
    for holders, names in components(rows):
        local_name = {x: i for i, x in enumerate(names)}
        local = tuple(tuple(local_name[x] for x in rows[i]) for i in holders)
        local_limits = tuple(sum(i < lim for i in holders) for lim in stage['limits'])
        yield names, local, local_limits


def nae_rates(stage, weighting):
    entries = {}
    factors = []
    for names, local, limits in compact(stage):
        denominator, values, _ = component_rates(local, limits, weighting)
        factors.append(denominator)
        entries.update({(names[i], names[j]): (p, denominator) for (i, j), p in values.items()})
    total = prod(factors)
    assert total % 2 == 0
    return total, {pair: entries[pair][0] * (total // entries[pair][1]) if pair in entries else total // 2
                   for pair in combinations(range(stage['width']), 2)}


def parity_rates(stage):
    table, checks = parity_table(stage['rows'])
    widths = [names for (_, count, _), names in group_width(stage['width'], checks) if count == 0 and len(names) > 1]
    equal = {pair for block in widths for pair in combinations(sorted(block), 2)}
    total = 1 << (stage['width'] - len(checks))
    counts = {pair: 0 if pair in equal else total // 2 for pair in combinations(range(stage['width']), 2)}
    return table, checks, total, counts


def rate_pass(data, plan_only=False):
    estimates = {}
    output = {law: [] for law in LAWS}
    for weighting in WEIGHTS:
        for source in data['nae']['sources']:
            for stage in reversed(source['stages']):
                for _, local, limits in compact(stage):
                    if (local, limits, weighting) not in estimates:
                        estimates[local, limits, weighting] = component_plan(local, limits, weighting)[-1]
    work = {weight: [x for x in estimates.values() if x['weight'] == weight] for weight in WEIGHTS}
    summary = {weight: {'components': len(entries), 'pair_query_classes': sum(e['queries'] for e in entries),
                        'largest_cell_count': max(e['peak_cells'] for e in entries),
                        'total_work_estimate': sum(e['total_cells'] for e in entries),
                        'largest_work_estimate': max(e['total_cells'] for e in entries)} for weight, entries in work.items()}
    if plan_only:
        print(summary, flush=True)
        return summary
    for law in LAWS:
        for source in data[law]['sources']:
            for stage in reversed(source['stages']):
                weights = {}
                if law == 'parity':
                    key, _, total, counts = parity_rates(stage)
                    payload = dict(total=total, counts=list(counts.values()), key=key.key, order=key.order,
                                   automorphisms=key.automorphisms)
                    weights = dict.fromkeys(WEIGHTS, payload)
                else:
                    for weighting in WEIGHTS:
                        try:
                            total, counts = nae_rates(stage, weighting)
                        except ValueError as error:
                            weights[weighting] = dict(unread=error.args)
                            continue
                        key = canonical_weighted(stage['width'], total, counts)
                        weights[weighting] = dict(total=total, counts=list(counts.values()), key=key.key,
                                                   order=key.order, automorphisms=key.automorphisms)
                output[law].append(dict(source_id=source['id'], age=stage['age'], weights=weights))
        print(law, len(output[law]), 'reached stages read for both weights', flush=True)
    return dict(cost=summary, reads=output)


def main():
    parser = ArgumentParser()
    parser.add_argument('--plan', action='store_true')
    args = parser.parse_args()
    result = rate_pass(read('explosive_stages.json.gz'), plan_only=args.plan)
    if not args.plan:
        write('explosive_rates.json.gz', result)


if __name__ == '__main__':
    main()
