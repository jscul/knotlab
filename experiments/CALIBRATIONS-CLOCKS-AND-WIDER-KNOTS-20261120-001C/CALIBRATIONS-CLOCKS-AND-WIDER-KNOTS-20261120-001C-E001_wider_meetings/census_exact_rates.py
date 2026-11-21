"""Exact uniform pair rates using elimination over three-state holder labels."""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from itertools import combinations

import networkx as nx
import numpy as np


def owners(rows):
    places = defaultdict(list)
    for i, row in enumerate(rows):
        for x in row:
            places[x].append(i)
    assert all(len(cluster) in (1, 2) for cluster in places.values())
    return {x: tuple(cluster) for x, cluster in places.items()}


def components(rows):
    """Return the holder indices and actual names of each physical component."""
    holding = owners(rows)
    meets = [set() for _ in rows]
    for places in holding.values():
        if len(places) == 2:
            a, b = places
            meets[a].add(b)
            meets[b].add(a)
    remaining = set(range(len(rows)))
    while remaining:
        visit = [min(remaining)]
        remaining.remove(visit[0])
        for i in visit:
            fresh = meets[i] & remaining
            visit.extend(sorted(fresh))
            remaining -= fresh
        yield tuple(sorted(visit)), tuple(sorted({x for i in visit for x in rows[i]}))


def constant_factor(scope, multiplicity):
    """Count and first-sign factors under holder labels (unpinned, 0, 1)."""
    standard = np.empty((3,) * len(scope), dtype=object)
    odd = standard.copy()
    even = standard.copy()
    for labels in np.ndindex(standard.shape):
        pinned = set(labels) - {0}
        if len(pinned) > 1:
            standard[labels] = odd[labels] = even[labels] = 0
        elif pinned:
            standard[labels] = even[labels] = 1
            odd[labels] = 1 if next(iter(pinned)) == 1 else -1
        else:
            standard[labels] = 1 << multiplicity
            odd[labels] = even[labels] = 0
    return standard, odd, even


@dataclass(frozen=True)
class Operation:
    result: int
    inputs: tuple
    shapes: tuple
    removed_axis: int
    dependency_mask: int
    volume: int


class Elimination:
    def __init__(self, multiplicities, holders, newest):
        self.scopes = tuple(sorted(multiplicities))
        self.scope_lookup = {scope: i for i, scope in enumerate(self.scopes)}
        signs = np.array((1, -1, -1), dtype=object)
        initial = {i: constant_factor(scope, multiplicities[scope]) for i, scope in enumerate(self.scopes)}
        self.base = [initial[i][0] for i in range(len(initial))] + [signs] * holders
        self.marked = {i: (values[1], values[2]) for i, values in initial.items()}
        pending = dict(enumerate((*self.scopes, *((i,) for i in range(holders)))))
        masks = dict((i, 1 << i) for i in pending)
        index = len(pending)
        self.operations = []
        variables = set(range(holders))
        newest_set = set(newest)
        while variables:
            candidates = newest_set & variables or variables
            nearby = {v: set().union(*(set(scope) for scope in pending.values() if v in scope)) for v in candidates}
            variable = min(candidates, key=lambda v: (len(nearby[v]), v))
            variables.remove(variable)
            used = tuple(i for i, scope in pending.items() if variable in scope)
            union = tuple(sorted(nearby[variable]))
            rest = tuple(v for v in union if v != variable)
            shapes = tuple(tuple(3 if v in pending[i] else 1 for v in union) for i in used)
            dependency = 0
            for i in used:
                dependency |= masks[i]
                del pending[i]
            pending[index] = rest
            masks[index] = dependency
            self.operations.append(Operation(index, used, shapes, union.index(variable), dependency, 3 ** len(union)))
            index += 1
        assert all(not scope for scope in pending.values())
        self.outputs = tuple(pending)
        self.base.extend([None] * len(self.operations))

    def changes(self, first, second):
        if first == second:
            return {first: self.marked[first][1]}
        return {first: self.marked[first][0], second: self.marked[second][0]}

    def work(self, marks):
        changed = sum(1 << i for i in marks)
        return sum(op.volume * len(op.inputs) for op in self.operations if op.dependency_mask & changed)

    def contract(self, marks=None):
        given = {} if marks is None else marks
        values = self.base if marks is None else self.base.copy()
        for i, factor in given.items():
            values[i] = values[i] * factor
        changed = sum(1 << i for i in given)
        for op in self.operations:
            if marks is not None and not op.dependency_mask & changed:
                continue
            terms = None
            for i, shape in zip(op.inputs, op.shapes, strict=True):
                block = values[i].reshape(shape)
                terms = block if terms is None else terms * block
            values[op.result] = np.asarray(terms.sum(axis=op.removed_axis), dtype=object)
        answer = 1
        for i in self.outputs:
            answer *= int(values[i])
        return answer


def holder_generators(multiplicities, holders, youngest):
    """Generate age-preserving permutations of holder indices, for count reuse."""
    from census_rates import point_group

    young = set(youngest)
    older = tuple(i for i in range(holders) if i not in young)
    indices = {holder: i for i, holder in enumerate(older)}
    children = defaultdict(list)
    for i in sorted(young):
        parents = [x for group in multiplicities if len(group) == 2 and i in group for x in group if x != i]
        assert not any(x in young for x in parents)
        shape = (tuple(sorted(parents)), multiplicities[i,])
        children[shape].append(i)
    graph = nx.Graph()
    graph.add_nodes_from((i, {'kind': ('old', multiplicities[h,])}) for i, h in enumerate(older))
    node = len(older)
    for group, amount in multiplicities.items():
        if len(group) == 2 and not young.intersection(group):
            graph.add_node(node, kind=('meeting', amount))
            graph.add_edges_from((node, indices[a]) for a in group)
            node += 1
    for (parents, loose), group in children.items():
        graph.add_node(node, kind=('children', loose, len(group)))
        graph.add_edges_from((node, indices[a]) for a in parents)
        node += 1
    _, generators = point_group(graph, len(older), keep_generators=True)
    for g in generators:
        permutation = {h: older[g[i]] for i, h in enumerate(older)}
        for (parents, loose), group in children.items():
            target = (tuple(sorted(permutation[h] for h in parents)), loose)
            permutation.update(zip(group, children[target], strict=True))
        yield tuple(permutation[i] for i in range(holders))
    for group in children.values():
        for a, b in zip(group, group[1:]):
            permutation = list(range(holders))
            permutation[a], permutation[b] = b, a
            yield tuple(permutation)


def pair_classes(plan, multiplicities, holders, youngest, reuse=True):
    queries = {(i, j) for i, j in combinations(range(len(plan.scopes)), 2)}
    queries.update((i, i) for i, scope in enumerate(plan.scopes) if multiplicities[scope] >= 2)
    moves = []
    if reuse:
        for perm in holder_generators(multiplicities, holders, youngest):
            image = tuple(tuple(sorted(perm[i] for i in scope)) for scope in plan.scopes)
            assert all(multiplicities[s] == multiplicities[t] != 0 for s, t in zip(plan.scopes, image, strict=True))
            moves.append(tuple(plan.scope_lookup[s] for s in image))
    while queries:
        start = min(queries)
        queries.remove(start)
        seen = {start}
        waiting = deque([start])
        while waiting:
            a, b = waiting.popleft()
            for mapping in moves:
                image = tuple(sorted((mapping[a], mapping[b])))
                if image not in seen:
                    seen.add(image)
                    queries.remove(image)
                    waiting.append(image)
        yield start, seen


@dataclass
class RatePlan:
    held: dict
    elimination: Elimination
    representatives: tuple

    @property
    def work(self):
        initial = sum(op.volume * len(op.inputs) for op in self.elimination.operations)
        return initial + sum(self.elimination.work(pair) for pair, _ in self.representatives)

    def measure(self):
        total = self.elimination.contract()
        assert total > 0
        pairs = {}
        for source, copies in self.representatives:
            signs = self.elimination.contract(self.elimination.changes(*source))
            assert -total <= signs <= total and (total - signs) % 2 == 0
            for pair in copies:
                pairs[pair] = (total - signs) // 2
        equivalent = {name: self.elimination.scope_lookup[s] for name, s in self.held.items()}
        result = {(i, j): pairs[tuple(sorted((equivalent[i], equivalent[j])))]
                  for i, j in combinations(sorted(self.held), 2)}
        return total, result


def rate_plan(rows, youngest, reuse=True):
    held = owners(rows)
    sizes = Counter(held.values())
    recipe = Elimination(sizes, len(rows), youngest)
    representatives = tuple(pair_classes(recipe, sizes, len(rows), youngest, reuse))
    return RatePlan(held, recipe, representatives)
