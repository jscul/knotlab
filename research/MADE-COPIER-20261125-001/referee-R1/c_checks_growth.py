"""Independent finite growth for the disclosed MET histories, from SD, FD, D and DC.

Only rations with no demand term are needed here. Roster forms use exact
isomorphism. The parity calculation uses a basis of the allowed values.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from functools import cached_property
from itertools import combinations

import networkx as nx


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask -= bit


def start_from_counts(graph, loose):
    rows = [set() for _ in loose]
    edges = sorted(tuple(sorted(e)) for e in graph.edges)
    for d, (u, v) in enumerate(edges):
        rows[u].add(d)
        rows[v].add(d)
    next_d = len(edges)
    for u, n in enumerate(loose):
        rows[u].update(range(next_d, next_d + n))
        next_d += n
    return State(tuple(map(frozenset, rows)), ((),) * len(rows), (0,) * len(rows),
                 ('start',) * len(rows))


@dataclass(frozen=True)
class State:
    places: tuple
    parents: tuple
    made: tuple
    kinds: tuple
    barred: frozenset = frozenset()
    retired: frozenset = frozenset()

    @cached_property
    def holders(self):
        holders = [set() for _ in range(1 + max(max(row) for row in self.places if row))]
        for u, row in enumerate(self.places):
            for d in row:
                holders[d].add(u)
        return holders

    @cached_property
    def meets(self):
        return [set().union(*(self.holders[d] for d in row)) - {u}
                for u, row in enumerate(self.places)]

    @cached_property
    def loose(self):
        return [sorted(d for d in row if len(self.holders[d]) == 1)
                for row in self.places]

    @cached_property
    def usable(self):
        return [[d for d in row if d not in self.barred] for row in self.loose]

    @cached_property
    def roster(self):
        return Roster(self)

    @cached_property
    def coordinates(self):
        basis = {}
        for row in self.places:
            mask = sum(1 << d for d in row)
            while mask:
                p = mask.bit_length() - 1
                if p not in basis:
                    basis[p] = mask ^ (1 << p)
                    break
                mask ^= basis[p] | (1 << p)
        out = []
        for d in range(len(self.holders)):
            val = 1 << d
            if d in basis:
                val = 0
                for p in bits(basis[d]):
                    val ^= out[p]
            out.append(val)
        return out

    def bar(self, knots):
        marks = frozenset(d for u in knots for d in self.usable[u])
        return replace(self, barred=self.barred | marks)


class Roster:
    def __init__(self, state, sides=None):
        self.state = state
        members = {u for u, us in enumerate(state.usable) if us}
        met_sets = {frozenset(h & members) for h in state.meets if len(h & members) >= 2}
        self.mets = []
        for m in sorted(met_sets, key=len, reverse=True):
            if not any(m < other for other in self.mets):
                self.mets.append(m)
        self.graph = nx.Graph()
        self.graph.add_nodes_from(members)
        for m in self.mets:
            for u, v in combinations(m, 2):
                if sides is not None and ((sides[u] & 1 and sides[v] & 2)
                                          or (sides[v] & 1 and sides[u] & 2)):
                    continue
                self.graph.add_edge(u, v)
        self.parts = sorted(tuple(sorted(p)) for p in nx.connected_components(self.graph))

    @cached_property
    def groups(self):
        larger = sorted(tuple(sorted(q)) for q in nx.find_cliques(self.graph)
                        if len(q) >= 3 and not any(set(q) <= m for m in self.mets))
        covered = {pair for q in larger for pair in combinations(q, 2)}
        pairs = {tuple(sorted(e)) for e in self.graph.edges}
        return larger + sorted(pairs - covered)

    def form(self, part):
        assert tuple(part) in self.parts
        labels = {u: (len(self.state.usable[u]), len(self.state.loose[u]) -
                      len(self.state.usable[u])) for u in part}
        sets = [m for m in self.mets if m <= set(part)]
        return Form(labels, sets)


class Form:
    def __init__(self, labels, sets):
        self.labels = labels
        self.sets = sets
        self.signature = (tuple(sorted(labels.values())), tuple(sorted(map(len, sets))))

    @cached_property
    def incidence(self):
        graph = nx.Graph()
        for u, mark in self.labels.items():
            graph.add_node(('k', u), t=mark)
        for i, met in enumerate(self.sets):
            graph.add_node(('m', i), t='met')
            graph.add_edges_from((('m', i), ('k', u)) for u in met)
        return graph

    def matches(self, other):
        if self.signature != other.signature:
            return False
        if len(self.labels) <= 2:
            return True
        return nx.is_isomorphic(self.incidence, other.incidence,
                                node_match=lambda a, b: a['t'] == b['t'])


def births_for(state, treatment, take, sides=None, fully_masked=False):
    roster = state.roster if sides is None else Roster(state, sides)
    groups = roster.groups
    owed = Counter(u for g in groups for u in g)
    short = {u for u in owed if owed[u] > len(state.usable[u])}
    joins = [g for g in groups if not short.intersection(g)]
    retained = Counter(u for g in joins for u in g)
    parents = list(joins)
    for u, loose in enumerate(state.usable):
        if u not in short or treatment == 'CANCEL-OFFSHOOT':
            parents.extend([(u,)] * (len(loose) - retained[u]))
    retired = short if treatment == 'CANCEL-RETIRE' else set()
    barred = {d for u in retired for d in state.usable[u]}
    allocated = [iter(xs) for xs in state.usable]
    plans = []
    for ps in parents:
        loose = tuple(next(allocated[u]) for u in ps)
        holders = set()
        if len(ps) == 1:
            u, = ps
            holders = state.meets[u] if take == 'MET' else set(state.parents[u])
        elif take == 'MET':
            holders = set.intersection(*(state.meets[u] for u in ps))
        candidates = set().union(*(state.places[u] for u in holders))
        candidates -= set().union(*(state.places[u] for u in ps))
        candidates = sorted(d for d in candidates if len(state.holders[d]) >= 2)
        if fully_masked:
            in_x = any(sides[u] & 1 for u in ps)
            in_y = any(sides[u] & 2 for u in ps)
            candidates = [d for d in candidates if not any(
                (in_x and sides[v] & 2) or (in_y and sides[v] & 1)
                for v in state.holders[d])]
        plans.append((ps, loose, candidates))
    return plans, barred, retired


def finish(state, round_no, ration, parity, prep, taken):
    plans, barred, retired = prep
    rows, parents, kinds = [], [], []
    next_d = len(state.holders)
    for (ps, loose, _), extra in zip(plans, taken, strict=True):
        inputs = set(loose)
        if extra is not None:
            inputs.add(extra)
        v = 0
        if parity:
            for d in inputs:
                v ^= state.coordinates[d]
        p = len(ps) if ration == 'FBP' else len(inputs)
        if ration not in ('FLOOR1', 'FBP', 'RATION-2'):
            raise ValueError(ration)
        n = 0 if parity and not v else max(3 - p, 2 if ration == 'RATION-2' else 1)
        inputs.update(range(next_d, next_d + n))
        next_d += n
        rows.append(frozenset(inputs))
        parents.append(ps)
        kinds.append('join' if len(ps) > 1 else 'offshoot')
    return State(state.places + tuple(rows), state.parents + tuple(parents),
                 state.made + (round_no,) * len(rows), state.kinds + tuple(kinds),
                 state.barred | barred, state.retired | retired)


def grow(state, s, end, bound, c, rnd, sides=None, mask=False, full=False, take='MET'):
    states = []
    if sides is not None:
        sides = list(sides)
    for r in range(s + 1, end + 1):
        prep = births_for(state, c['treatment'], take, sides if mask else None, full)
        taken = [ds[rnd.randrange(len(ds))] if ds else None for _, _, ds in prep[0]]
        state = finish(state, r, c['ration'], c['knot_law'] == 'parity', prep, taken)
        if sides is not None:
            for ps, _, _ in prep[0]:
                descended = 0
                for u in ps:
                    descended |= sides[u]
                sides.append(descended)
        states.append(state)
        if len(state.places) > bound:
            break
    return states


def initial_sides(state, c):
    sides = [0] * len(state.places)
    for u in c['X']:
        sides[u] = 1
    for u in c['Y']:
        sides[u] = 2
    return sides


def events(ref, histories, c):
    s = c['s']
    x, y = ref.roster.form(c['X']), ref.roster.form(c['Y'])
    same = x.matches(y)
    sides = initial_sides(ref, c)
    elig = set()
    if c['knot_law'] == 'parity' and c['reading'] == 'values':
        xvalues = {ref.coordinates[d] for u in c['X'] for d in ref.places[u]}
        elig = {d for u in c['Y'] for d in ref.places[u]
                if ref.coordinates[d] and ref.coordinates[d] not in xvalues}
    meet = None
    first, after = {}, {}
    for r, state in enumerate(histories, s + 1):
        for ps in state.parents[len(sides):]:
            side = 0
            for u in ps:
                side |= sides[u]
            sides.append(side)
        found = set()
        counts = Counter()
        for pt in state.roster.parts:
            if meet is None and any(sides[u] & 1 for u in pt) and any(sides[u] & 2 for u in pt):
                meet = r
            if any(state.made[u] > s for u in pt) and len(pt) == len(y.labels):
                if y.matches(state.roster.form(pt)):
                    labels = {sides[u] for u in pt}
                    counts[next(iter(labels)) if len(labels) == 1 else 'mixed'] += 1
        if counts[1] >= 2:
            found.add('formany_X')
            if not same:
                found.add('form')
        if counts[3] >= 2:
            found.add('both')
        if counts[2] >= 2:
            found.add('Yown_form')
        if sum(counts.values()) >= 2:
            found.add('yform_any')
        if elig:
            target = {state.coordinates[v] for v in elig}
            by_value = defaultdict(list)
            for u in range(len(ref.places), len(sides)):
                for d in state.usable[u]:
                    if d >= len(ref.holders) and state.coordinates[d] in target:
                        by_value[state.coordinates[d]].append(sides[u])
            for group in by_value.values():
                if len(group) < 2:
                    continue
                if any(tag & 1 for tag in group):
                    found.add('vA')
                if group.count(1) >= 2:
                    found.add('vX')
                if group.count(2) >= 2:
                    found.add('Yown_val')
        for key in found:
            first.setdefault(key, r)
            if meet is not None:
                after.setdefault(key, r)
    return same, meet, first, after


def state_hash(state):
    graph = nx.Graph()
    for u, (row, ps) in enumerate(zip(state.places, state.parents)):
        graph.add_node(('k', u), a=f'K|{state.kinds[u]}|{state.made[u]}|{int(u in state.retired)}')
        for d in row:
            graph.add_node(('d', d), a=f'D|{int(d in state.barred)}')
            graph.add_edge(('k', u), ('d', d), e='place')
        for p in ps:
            graph.add_edge(('k', u), ('k', p), e='parent')
    return nx.weisfeiler_lehman_graph_hash(graph, node_attr='a', edge_attr='e', iterations=6)
