"""Rebuild the declared funded starts and their parity classes from their definitions."""

import argparse
from collections import Counter, defaultdict, deque
from copy import copy
import gzip
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import re
from resource import getrusage, RUSAGE_SELF
from time import monotonic


RESEARCH = Path(__file__).resolve().parents[2]
SIGN = RESEARCH / 'TWO-CLASS-SIGN-20261126-001'
LONG = RESEARCH / 'BOTH-LONG-20261126-001'


def mask(names):
    return sum(1 << name for name in names)


def support(word):
    while word:
        bit = word & -word
        yield bit.bit_length() - 1
        word ^= bit


def overlap(first, second):
    return (first & second).bit_count() % 2


class Span:
    def __init__(self, words=()):
        self.rows = {}
        for word in words:
            self.add(word)

    def remainder(self, word):
        while word and (pivot := word.bit_length() - 1) in self.rows:
            word ^= self.rows[pivot]
        return word

    def add(self, word):
        if word := self.remainder(word):
            self.rows[word.bit_length() - 1] = word
        return bool(word)

    def __iter__(self):
        return iter(self.rows.values())

    def __len__(self):
        return len(self.rows)


def null_basis(rows, places):
    pivots = Span(rows).rows
    ordered = sorted(pivots.items())
    for free in places:
        if free in pivots:
            continue
        word = 1 << free
        for pivot, row in ordered:
            word |= overlap(row, word) << pivot
        yield word


def holdings(rows):
    holders = defaultdict(list)
    for knot, row in enumerate(rows):
        for distinction in row:
            holders[distinction].append(knot)
    assert all(len(knots) in (1, 2) for knots in holders.values())
    return holders


def maximal_cliques(neighbours):
    def visit(clique, available, used):
        if not available and not used:
            yield clique
            return
        pivot = max(available | used, key=lambda key: len(available & neighbours[key]))
        for knot in sorted(available - neighbours[pivot]):
            yield from visit(clique | {knot}, available & neighbours[knot], used & neighbours[knot])
            available.remove(knot)
            used.add(knot)

    yield from visit(set(), set(neighbours), set())


def multi_parent_groups(witnesses):
    pairs = {pair for witness in witnesses for pair in combinations(sorted(witness), 2)}
    neighbours = defaultdict(set)
    for a, b in pairs:
        neighbours[a].add(b)
        neighbours[b].add(a)
    big = sorted(tuple(sorted(group)) for group in maximal_cliques(neighbours)
                 if len(group) >= 3 and not any(group <= witness for witness in witnesses))
    used = {pair for group in big for pair in combinations(group, 2)}
    return big + sorted(pairs - used)


def shared_neighbours(holders, count):
    neighbours = [set() for _ in range(count)]
    for knots in holders.values():
        if len(knots) == 2:
            a, b = knots
            neighbours[a].add(b)
            neighbours[b].add(a)
    return neighbours


def grow(rows, arm='ordinary'):
    """A funded round, with the declared first-available loose distinction allocation."""
    holders = holdings(rows)
    loose = {k: deque(d for d in row if len(holders[d]) == 1) for k, row in enumerate(rows)}
    live = {k for k, bits in loose.items() if bits}
    if not live:
        return None, {'status': 'closed'}
    witnesses = [neighbours & live for neighbours in shared_neighbours(holders, len(rows))]
    parents = multi_parent_groups(witnesses)
    demand = Counter(knot for group in parents for knot in group)
    if any(demand[knot] > len(loose[knot]) for knot in live):
        return None, {'status': 'stalled'}
    parents += [(knot,) for knot in sorted(live) for _ in range(len(loose[knot]) - demand[knot])]
    children_at = [set() for _ in rows]
    for birth, group in enumerate(parents):
        for parent in group:
            children_at[parent].add(birth)
    lookahead = Counter(birth for group in multi_parent_groups(children_at) for birth in group)
    constraints = Span(mask(row) for row in rows)
    first_fresh = max(holders) + 1
    newborn = []
    zero_fresh = 0
    independent_zero_fresh = 0
    for birth, group in enumerate(parents):
        taken = tuple(loose[knot].popleft() for knot in group)
        floor = max(0, 3 - len(group))
        implied = constraints.remainder(mask(taken)) == 0
        ordinary = lookahead[birth] if implied else max(lookahead[birth], floor, 1)
        fresh = ordinary
        if arm == 'one_fewer':
            fresh = min(ordinary, max(floor, ordinary - 1))
        if arm == 'arity_floor':
            fresh = min(ordinary, floor)
        newborn.append(taken + tuple(range(first_fresh, first_fresh + fresh)))
        first_fresh += fresh
        zero_fresh += fresh == 0
        independent_zero_fresh += fresh == 0 and not implied
    assert not any(loose.values())
    return rows + tuple(newborn), {'status': 'funded', 'births': len(newborn), 'zero_fresh': zero_fresh,
                                   'zero_fresh_not_implied_at_start_of_round': independent_zero_fresh}


def ring_start(size, loose):
    return tuple((i, (i + 1) % size, *range(size + i * loose, size + (i + 1) * loose))
                 for i in range(size))


def funded_start(meetings, count, minimum=2, extra=0, fill_to_three=False):
    rows = [[] for _ in range(count)]
    for distinction, (a, b) in enumerate(meetings):
        rows[a].append(distinction)
        rows[b].append(distinction)
    neighbours = shared_neighbours(holdings(rows), count)
    demand = Counter(knot for group in multi_parent_groups(neighbours) for knot in group)
    first_fresh = len(meetings)
    already_loose = [0] * count
    if fill_to_three:
        for knot, row in enumerate(rows):
            new = max(0, 3 - len(row))
            row.extend(range(first_fresh, first_fresh + new))
            first_fresh += new
            already_loose[knot] = new
    for knot, row in enumerate(rows):
        fresh = max(minimum, demand[knot] + extra) - already_loose[knot]
        row.extend(range(first_fresh, first_fresh + fresh))
        first_fresh += fresh
    return tuple(tuple(row) for row in rows), [demand[knot] for knot in range(count)]


def ring_meetings(sizes, joins):
    members = [[(ring, k) for k in range(size)] for ring, size in enumerate(sizes)]
    aliases = {right: left for kind, left, right, _ in joins if kind == 'shared knot'}
    canonical = lambda member: aliases.get(member, member)
    knots = {key: i for i, key in enumerate(dict.fromkeys(canonical(m) for ring in members for m in ring))}
    meetings, ring_names = [], []
    for ring in members:
        first = len(meetings)
        meetings.extend((knots[canonical(a)], knots[canonical(b)]) for a, b in zip(ring, ring[1:] + ring[:1]))
        ring_names.append(tuple(range(first, len(meetings))))
    count = len(knots)
    for kind, left, right, chain in joins:
        if kind == 'shared knot':
            continue
        route = [knots[canonical(left)], *range(count, count + chain), knots[canonical(right)]]
        meetings.extend(zip(route, route[1:]))
        count += chain
    return meetings, count, ring_names


class Changes:
    """Use the incidence representation for shortest changes and parity linear algebra for reads."""

    def __init__(self, rows, pinned=False, compare_cap=False):
        holders = holdings(rows)
        self.rows = rows
        self.loose = [d for d, knots in holders.items() if len(knots) == 1]
        self.active = sorted(d for d, knots in holders.items() if len(knots) == 2 or not pinned)
        self.meetings = {d: tuple(knots) if len(knots) == 2 else (knots[0], len(rows))
                         for d, knots in holders.items() if not pinned or len(knots) == 2}
        self.adjacent = [[] for _ in range(len(rows) + (not pinned))]
        for d, (a, b) in self.meetings.items():
            self.adjacent[a].append((b, d))
            self.adjacent[b].append((a, d))
        active_mask = mask(self.active)
        self.allowed = list(null_basis((mask(row) & active_mask for row in rows), self.active))
        moves = set()
        self.capped_moves = set()
        self.move_ties = {}
        self.move_sizes = {}
        order = {d: i for i, d in enumerate(self.meetings)}
        for d, (a, b) in self.meetings.items():
            ties = self.shortest_changes(a, b, d)
            self.move_ties[d] = len(ties)
            if ties:
                self.move_sizes[d] = ties[0].bit_count()
                moves.update(ties)
                if compare_cap:
                    if len(ties) > 64:
                        ties.sort(key=lambda change: self.backward_path_order(change ^ (1 << d), b, order), reverse=True)
                    self.capped_moves.update(ties[:64])
        self.set_moves(moves)

    def set_moves(self, moves):
        self.moves = moves
        self.motion = Span(self.moves)
        extension = Span(self.motion)
        self.quotient = [word for word in self.allowed if extension.add(word)]
        assert len(extension) == len(self.allowed)

    def backward_path_order(self, path, knot, distinction_order):
        """The old cap keeps the first reverse DFS paths in holdings order."""
        order = []
        while path:
            next_knot, distinction = next((other, d) for other, d in self.adjacent[knot] if path & (1 << d))
            order.append(distinction_order[distinction])
            path ^= 1 << distinction
            knot = next_knot
        return tuple(order)

    def shortest_changes(self, source, target, marked):
        """BFS until the target layer, carrying every distinct tie through that layer."""
        at_tie = {source: [0]}
        visited = set()
        while at_tie and target not in at_tie:
            visited.update(at_tie)
            after = defaultdict(list)
            for knot, ties in at_tie.items():
                for other, distinction in self.adjacent[knot]:
                    if distinction != marked and other not in visited:
                        after[other].extend(tie | (1 << distinction) for tie in ties)
            at_tie = after
        return [path | (1 << marked) for path in at_tie.get(target, [])]

    def signature(self, read):
        return sum(overlap(word, read) << i for i, word in enumerate(self.quotient))

    def is_label(self, read):
        return bool(self.signature(read)) and not any(overlap(word, read) for word in self.motion)

    def readings(self):
        all_readers, knot_readers = Span(), Span()
        best_holder = 0
        failed_knot_test = []
        for knot, row in enumerate(self.rows):
            held = mask(row)
            allowed_rank = len(Span(word & held for word in self.allowed))
            local = Span(self.signature(read) for read in null_basis((word & held for word in self.motion), row))
            assert allowed_rank <= len(row) - 1
            best_holder = max(best_holder, len(local))
            for read in local:
                all_readers.add(read)
                if allowed_rank == len(row) - 1 and len(row) >= 3:
                    knot_readers.add(read)
            if allowed_rank != len(row) - 1 or len(row) < 3:
                failed_knot_test.append(knot)
        return {'best_single_holder_bits': best_holder, 'all_local_bits': len(all_readers),
                'local_bits_at_knots_passing_K1_K3': len(knot_readers),
                'whole_held_bits': len(self.quotient) - len(knot_readers),
                'holders_failing_knot_test': failed_knot_test}

    def loose_preserving_bits(self):
        loose = mask(self.loose)
        pinned_changes = (null_basis((mask(row) & ~loose for row in self.rows),
                                     [d for d in self.active if not (1 << d) & loose]))
        return len(Span([*self.motion, *pinned_changes])) - len(self.motion)

    def summary(self):
        return {'knots': len(self.rows), 'distinctions': len(holdings(self.rows)), 'active': len(self.active),
                'rank_allowed': len(self.allowed), 'rank_moves': len(self.motion),
                'classes': 1 << len(self.quotient), 'shortest_ties': len(self.moves),
                'move_lengths': dict(sorted(Counter(word.bit_count() for word in self.moves).items())),
                'largest_tie_count_at_one_distinction': max(self.move_ties.values(), default=0),
                'distinctions_with_more_than_64_ties': sum(count > 64 for count in self.move_ties.values())}

    def old_change_rank(self, old):
        previous = mask(holdings(old))
        assert all(not overlap(change, mask(row)) for change in self.allowed for row in old)
        return len(Span(word & previous for word in self.allowed))


def prescribed_label(changes, signature):
    """Solve for a read orthogonal to the moves with the given values on quotient generators."""
    equations = {(row.bit_length() - 1): (row, 0) for row in changes.motion}
    for i, row in enumerate(changes.quotient):
        value = (signature >> i) & 1
        while (pivot := row.bit_length() - 1) in equations:
            known_row, known_value = equations[pivot]
            row ^= known_row
            value ^= known_value
        assert row
        equations[pivot] = row, value
    label = 0
    for pivot, (row, value) in sorted(equations.items()):
        label |= (overlap(row, label) ^ value) << pivot
    assert changes.is_label(label) and changes.signature(label) == signature
    return label


def shortest_odd_cycle(changes, label, available):
    """Find the least closed walk of odd label parity by searching both parity copies of each knot."""
    best = None
    limit = len(available) + 1
    for knot in range(len(changes.adjacent)):
        source, target = 2 * knot, 2 * knot + 1
        predecessors = {source: (None, None)}
        todo = deque([(source, 0)])
        while todo and target not in predecessors:
            here, depth = todo.popleft()
            if depth + 1 >= limit:
                continue
            for neighbour, distinction in changes.adjacent[here // 2]:
                parity = ((label >> distinction) ^ here) & 1
                next_state = 2 * neighbour + parity
                if distinction in available and next_state not in predecessors:
                    predecessors[next_state] = here, distinction
                    todo.append((next_state, depth + 1))
        if target in predecessors:
            limit = 0
            best = 0
            while target != source:
                target, distinction = predecessors[target]
                best ^= 1 << distinction
                limit += 1
    if best is not None:
        assert best.bit_count() == limit and overlap(best, label)
    return best


def cut_translation_search(changes, initial, lower):
    """Find a minimum weight read in one cut coset using exact cardinality decisions."""
    from pysat.card import ITotalizer
    from pysat.solvers import Solver

    knot_variables = len(changes.adjacent)
    labels = {distinction: i for i, distinction in enumerate(changes.active, knot_variables + 1)}
    clauses = []
    for distinction, (a, b) in changes.meetings.items():
        local_variables = [a + 1, b + 1, labels[distinction]]
        expected = (initial >> distinction) & 1
        for values in product((0, 1), repeat=3):
            if sum(values) % 2 != expected:
                clauses.append([(-var if value else var) for var, value in zip(local_variables, values)])
    upper = initial.bit_count()
    witness = initial
    with ITotalizer(lits=list(labels.values()), ubound=upper - 1) as totalizer:
        with Solver(name='g3', bootstrap_with=clauses + totalizer.cnf.clauses) as solver:
            while lower < upper:
                bound = (lower + upper - 1) // 2
                if solver.solve(assumptions=[-totalizer.rhs[bound]]):
                    model = set(solver.get_model())
                    witness = mask(d for d, var in labels.items() if var in model)
                    upper = witness.bit_count()
                    assert lower <= upper <= bound
                else:
                    lower = bound + 1
    return witness


def descend_label(changes, label):
    """Lower the starting upper bound by translating by one knot equation at a time."""
    active = mask(changes.active)
    constraints = [mask(row) & active for row in changes.rows]
    while True:
        previous = label.bit_count()
        for row in constraints:
            alternative = label ^ row
            if alternative.bit_count() < label.bit_count():
                label = alternative
        if label.bit_count() == previous:
            return label


def ring_distances(changes, old_ring):
    if not changes.quotient:
        return {}
    assert len(changes.quotient) == 1
    label = old_ring if changes.is_label(old_ring) else prescribed_label(changes, 1)
    label = descend_label(changes, label)
    active = set(changes.active)
    change = shortest_odd_cycle(changes, label, active)
    assert change is not None and changes.motion.remainder(change)
    move = change
    packing = []
    while move is not None and len(packing) < label.bit_count():
        packing.append(list(support(move)))
        active.difference_update(packing[-1])
        move = shortest_odd_cycle(changes, label, active)
    used_solver = len(packing) < label.bit_count()
    least_label = cut_translation_search(changes, label, len(packing)) if used_solver else label
    assert changes.signature(least_label) == 1 and changes.is_label(least_label)
    allowed = Span(changes.allowed)
    return {'d_read': least_label.bit_count(), 'd_change': change.bit_count(), 'read': list(support(least_label)),
            'change': list(support(change)), 'disjoint_odd_change_pack': packing, 'read_needed_cardinality_solver': used_solver,
            'old_ring_is_label': changes.is_label(old_ring), 'old_ring_exchanges_classes': bool(changes.motion.remainder(old_ring)),
            'old_ring_is_minimum_label': changes.is_label(old_ring) and old_ring.bit_count() == least_label.bit_count(),
            'old_ring_is_minimum_change': bool(changes.motion.remainder(old_ring)) and old_ring.bit_count() == change.bit_count(),
            'selected_least_change_is_label': changes.is_label(change),
            'selected_least_label_is_allowed': allowed.remainder(least_label) == 0}


def full_span(basis):
    words = [0]
    for word in basis:
        words.extend(change ^ word for change in words[:])
    return words


def literal_checks(changes, distances):
    checked = []
    if len(changes.allowed) <= 15:
        words = full_span(changes.allowed)
        smallest = defaultdict(set)
        for change in sorted(words[1:], key=int.bit_count):
            for d in support(change):
                if not smallest[d] or next(iter(smallest[d])).bit_count() == change.bit_count():
                    smallest[d].add(change)
        assert set().union(*smallest.values()) == changes.moves
        if distances:
            assert min(word.bit_count() for word in words if changes.motion.remainder(word)) == distances['d_change']
        checked.append('all allowed assignments')
    if distances:
        active = mask(changes.active)
        constraints = Span(mask(row) & active for row in changes.rows)
        if len(constraints) <= 14:
            label = mask(distances['read'])
            assert min((label ^ word).bit_count() for word in full_span(constraints)) == distances['d_read']
            checked.append('all equivalent reads')
    return checked


FIRST = (0, 0)
SECOND = (1, 0)
THIRD = (2, 0)
SHARE = ('shared knot', FIRST, SECOND, 0)
MEET = ('shared distinction', FIRST, SECOND, 0)
CHAIN = ('chain', FIRST, SECOND, 1)
THREE_SHARE = (SHARE, ('shared knot', FIRST, THIRD, 0))
THREE_CHAIN = (MEET, ('shared distinction', (1, 2), THIRD, 0))
THREE_CYCLE = (*THREE_CHAIN, ('shared distinction', (2, 2), (0, 2), 0))


def declared_builds():
    principal = [((n,), ()) for n in (5, 7, 4)] + [
        ((5, 5), (SHARE,)), ((5, 5), (MEET,)), ((5, 5), (CHAIN,)),
        ((5, 5), (('chain', FIRST, SECOND, 2),)), ((5, 5, 5), THREE_SHARE),
        ((5, 5, 5), THREE_CYCLE), ((4, 4), (MEET,)), ((4, 4, 4), THREE_CYCLE),
    ]
    for sizes, joins in principal:
        yield 'principal', sizes, joins
    for sizes in ((3, 5), (5, 7), (7, 7), (3, 3), (4, 6), (5, 6)):
        for joins in ((SHARE,), (MEET,), (CHAIN,), ()):
            yield 'supplement', sizes, joins
    for sizes in ((5, 5, 5), (3, 5, 7)):
        for joins in (THREE_SHARE, THREE_CHAIN, ()):
            yield 'supplement', sizes, joins


def ring_parity_labels(changes, ring_names):
    return [list(indices) for count in range(1, len(ring_names) + 1)
            for indices in combinations(range(len(ring_names)), count)
            if changes.is_label(mask(d for i in indices for d in ring_names[i]))]


def built_stage(stage, original, source_rank, ring_names=None, tree_names=None):
    changes = Changes(stage, compare_cap=True)
    result = changes.summary() | changes.readings()
    held = holdings(stage)
    meeting_pattern = tuple(sorted(tuple(knots) for knots in held.values()))
    result['fixed_knot_order_meeting_digest'] = sha256(repr(meeting_pattern).encode()).hexdigest()
    projected = changes.old_change_rank(original)
    result['old_change_rank'] = projected
    result['original_allowed_changes_preserved'] = projected == source_rank
    result['old_knots_with_loose_distinctions'] = sum(any(len(held[d]) == 1 for d in row) for row in original)
    if ring_names is not None:
        all_old_shared = mask(d for d, old in holdings(original).items() if len(old) == 2)
        result['ring_parity_labels'] = ring_parity_labels(changes, ring_names)
        result['all_old_shared_parity_label'] = changes.is_label(all_old_shared)
    if tree_names is not None:
        result['all_nine_old_shared_parity_label'] = changes.is_label(mask(tree_names))
    capped = copy(changes)
    capped.set_moves(changes.capped_moves)
    result['cap_64'] = {'rank_moves': len(capped.motion), 'shortest_ties': len(capped.moves),
                        'same_span': len(capped.motion) == len(changes.motion)}
    if not result['cap_64']['same_span']:
        result['cap_64'] |= {'classes': 1 << len(capped.quotient), **capped.readings()}
        if ring_names is not None:
            result['cap_64']['ring_parity_labels'] = ring_parity_labels(capped, ring_names)
            result['cap_64']['all_old_shared_parity_label'] = capped.is_label(all_old_shared)
        if tree_names is not None:
            result['cap_64']['all_nine_old_shared_parity_label'] = capped.is_label(mask(tree_names))
    return result


def built_outcome(rows, opening_demand, rounds, *, ring_names=None, tree_names=None, cuts=False):
    original_holders = holdings(rows)
    rank = len(original_holders) - len(Span(mask(row) for row in rows))
    outcome = {'demand': opening_demand,
               'start_loose_counts': [sum(len(original_holders[d]) == 1 for d in row) for row in rows],
               'start_allowed_rank': rank,
               'start': built_stage(rows, rows, rank, ring_names, tree_names)}
    arms = [('ordinary', rounds)] + ([('one_fewer', 1), ('arity_floor', 1)] if cuts else [])
    for arm, horizon in arms:
        stage = rows
        outcome[arm] = []
        for age in range(1, horizon + 1):
            stage, birth = grow(stage, arm)
            entry = {'round': age} | birth
            if stage is not None:
                entry |= built_stage(stage, rows, rank, ring_names, tree_names)
            outcome[arm].append(entry)
            if stage is None:
                break
    return outcome


def funded_replays(pilot):
    builds, controls = [], []
    for tier, sizes, joins in declared_builds():
        if pilot and (tier != 'principal' or sizes not in ((5,), (5, 5, 5))):
            continue
        meetings, count, ring_names = ring_meetings(sizes, joins)
        rows, demand = funded_start(meetings, count, fill_to_three=True)
        builds.append({'tier': tier, 'ring_sizes': sizes, 'joins': joins, 'supports': rows, 'ring_names': ring_names}
                      | built_outcome(rows, demand, 2, ring_names=ring_names, cuts=tier == 'principal'))
    tree = [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 6), (2, 7), (3, 8), (3, 9)]
    for extra in (0, 1):
        rows, demand = funded_start(tree, 10, extra=extra)
        controls.append({'description': 'ten-knot tree', 'extra': extra, 'supports': rows}
                        | built_outcome(rows, demand, 1, tree_names=list(range(9))))
        for size in ((4, 5) if pilot else (4, 5, 7)):
            meetings, count, ring_names = ring_meetings((size,), ())
            rows, demand = funded_start(meetings, count, minimum=0 if extra else 2, extra=extra,
                                        fill_to_three=not extra)
            controls.append({'description': f'{size}-knot ring', 'extra': extra, 'supports': rows}
                            | built_outcome(rows, demand, 1, ring_names=ring_names))
    meetings, count, ring_names = ring_meetings((4,), ())
    original, demand = funded_start(meetings, count, fill_to_three=True)
    first_new = max(holdings(original)) + 1
    rows = tuple(row + (first_new + knot,) for knot, row in enumerate(original))
    diagnostic = {'description': 'four-knot ring, one extra loose distinction above the built baseline',
                  'supports': rows} | built_outcome(rows, demand, 1, ring_names=ring_names)
    return {'built': builds, 'funding_controls': controls, 'funding_diagnostic': diagnostic}


def json_lines(path):
    with gzip.open(path, 'rt') as source:
        return [json.loads(line) for line in source]


def stages_of_ring(size, loose, horizon):
    stage = ring_start(size, loose)
    yield stage, 'start'
    for _ in range(horizon):
        stage, birth = grow(stage)
        yield stage, birth['status']
        if stage is None:
            break


def compare(result, expected, address, comparison):
    comparison['profiles'] += 1
    comparison['fields'] += len(expected)
    for key, wanted in expected.items():
        actual = result.get(key)
        if actual != wanted:
            comparison['mismatches'].append({'row': address, 'field': key, 'replay': actual, 'archive': wanted})


def sign_view(changes, old_ring):
    readings = changes.readings()
    return changes.summary() | readings | {
        'old_shared_parity_nonconstant': any(overlap(word, old_ring) for word in changes.allowed),
        'old_shared_parity_on_some_move': any(overlap(word, old_ring) for word in changes.motion),
        'whole_old_ring_changes_class': bool(changes.motion.remainder(old_ring)),
        'whole_old_ring_allowed': all(not overlap(mask(row), old_ring) for row in changes.rows),
        'loose_preserving_class_bits': changes.loose_preserving_bits(),
        'bits_readable_in_one_knot': readings['best_single_holder_bits'],
    }


def sign_replays(pilot):
    profile = {}
    for size in ((3, 5, 13, 31) if pilot else (*range(3, 14), 31)):
        for loose in (1, 2) if size <= 9 else (2,):
            for age, (stage, status) in enumerate(stages_of_ring(size, loose, 2 if loose == 2 and size <= 13 else 1)):
                old_ring = (1 << size) - 1
                for pinned in (False, True):
                    changes = Changes(stage, pinned) if stage is not None else None
                    profile[size, loose, age, pinned] = changes, status

    def new_comparison():
        return {'profiles': 0, 'fields': 0, 'mismatches': [], 'archive_not_run': []}

    comparisons = {name: new_comparison() for name in ('original_canonical', 'fold_archive_comparison', 'original_rings2',
                                                        'referee_round_two', 'motion_archive')}
    for name, file in [('original_canonical', 'rings_canonical.jsonl.gz'), ('fold_archive_comparison', 'rings_fold.jsonl.gz')]:
        for row in json_lines(SIGN / file):
            size, loose = (int(value) for value in re.findall(r'\d+', row['structure']))
            if (size, loose, 0, False) not in profile:
                continue
            for age, stage_name in enumerate(('start', 'after one round')):
                for pinned, reading in enumerate(('loose free', 'loose pinned')):
                    address = size, loose, age, bool(pinned)
                    changes, status = profile[address]
                    archived = row[stage_name]
                    if isinstance(archived, str):
                        compare({'has_growth': status == 'funded'}, {'has_growth': False}, address, comparisons[name])
                        continue
                    field = archived[reading]
                    if 'not run' in field:
                        comparisons[name]['archive_not_run'].append({'row': address, 'reason': field['not run']})
                        continue
                    view = {'distinctions': len(holdings(changes.rows)), 'dim S': len(changes.allowed),
                            'dim H': len(changes.motion), 'classes': 1 << len(changes.quotient),
                            'a class change avoids the loose distinctions': changes.loose_preserving_bits() > 0}
                    compare(view, field, address, comparisons[name])

    for row in json_lines(SIGN / 'rings2.jsonl.gz'):
        size = int(re.search(r'n=(\d+)', row['structure'])[1])
        if (size, 2, 0, False) not in profile:
            continue
        stage_data = []
        for age, stage_name in enumerate(('start', 'after one round')):
            address = size, 2, age, False
            changes, _ = profile[address]
            stage_data.append(changes)
            expected = row[stage_name]
            least = min(changes.move_sizes.values(), default=0)
            overall = Span(word for word in changes.moves if word.bit_count() == least)
            pinned = Changes(changes.rows, True)
            dimensions = {}
            for kind, span in (('shortest through each distinction', changes.motion), ('shortest overall', overall)):
                dimensions[kind] = {'dim H': len(span), 'classes': 1 << (len(changes.allowed) - len(span)),
                                    'dim (S0+H)/H': len(Span([*span, *pinned.allowed])) - len(span),
                                    'dim S/H': len(changes.allowed) - len(span),
                                    'distinctions with no short change': sum(not count for count in changes.move_ties.values())}
            dimensions['shortest through each distinction']['the class read inside one knot'] = bool(changes.readings()['best_single_holder_bits'])
            compare({'distinctions': len(changes.active), 'dim S': len(changes.allowed), **dimensions}, expected,
                    address, comparisons['original_rings2'])
        start, grown = stage_data
        old = mask(start.active)
        compare({'kept': all(start.motion.remainder(word & old) == 0 for word in grown.moves)},
                {'kept': row['old classes kept by the grown moves']}, (size, 2, 'old moves'), comparisons['original_rings2'])

    referee = json.loads((SIGN / 'referee-R1/ring_results.json').read_text())
    for row in referee['rows']:
        address = row['n'], 2, row['age'], row['pinned']
        if address not in profile:
            continue
        changes, _ = profile[address]
        expected = {key: val for key, val in row.items() if key not in ('n', 'age', 'pinned', 'matched_motion_archive')}
        answer = sign_view(changes, (1 << row['n']) - 1)
        answer['move_lengths'] = {str(length): count for length, count in answer['move_lengths'].items()}
        compare(answer, expected, address, comparisons['referee_round_two'])

    motion_path = (RESEARCH.parent / 'artifacts/READS-HOLDERS-SOURCES-20261120-001A/'
                   'READS-HOLDERS-SOURCES-20261120-001A-E001_reads_changes/motion.json')
    for row in json.loads(motion_path.read_text())['rings']:
        address = row['ring'], 2, row['age'], row['loose_pinned']
        changes, _ = profile[address]
        answer = changes.summary() | {
            'allowed_states': str(1 << len(changes.allowed)), 'states_per_class': str(1 << len(changes.motion))}
        expected = {'rank_allowed': row['allowed_change_rank'], 'rank_moves': row['shortest_rank'],
                    'classes': row['shortest_fixed_weighting_dimension'], 'shortest_ties': row['shortest_generators'],
                    'allowed_states': str(row['allowed_assignments'])}
        if 'orbit_sizes' in row:
            expected['states_per_class'] = str(row['orbit_sizes'][0])
        compare(answer, expected, address, comparisons['motion_archive'])
    rows = []
    for (size, loose, age, pinned), (changes, status) in profile.items():
        row = {'ring_size': size, 'loose_each_at_start': loose, 'round': age, 'pinned_by_stage': pinned, 'status': status}
        rows.append(row | (sign_view(changes, (1 << size) - 1) if changes is not None else {}))
    return {'rows': rows, 'comparisons': comparisons}


def long_replays(pilot):
    archive = {(row['ring'], row['round']): row for row in json_lines(LONG / 'rings_dist.jsonl.gz')}
    comparison = {'profiles': 0, 'fields': 0, 'mismatches': []}
    rows = []
    for size in ((4, 6, 8, 12) if pilot else range(4, 13)):
        horizon = (6 if size == 12 else 2) if pilot else 6
        old_ring = (1 << size) - 1
        for age, (stage, status) in enumerate(stages_of_ring(size, 2, horizon)):
            assert stage is not None, (size, age, status)
            row = {'ring_size': size, 'round': age}
            for pinned, reading in enumerate(('loose free', 'loose pinned')):
                changes = Changes(stage, pinned)
                distance = ring_distances(changes, old_ring)
                view = changes.summary() | distance
                view['literal_checks'] = literal_checks(changes, distance)
                expected = archive[size, age][reading]
                basics = {'knots': 'knots', 'distinctions': 'active', 'dim S': 'rank_allowed', 'dim H': 'rank_moves',
                          'classes': 'classes', 'tie cap reached': 'distinctions_with_more_than_64_ties',
                          'd_change': 'd_change', 'd_read': 'd_read'}
                archived_numbers = {our: expected[their] for their, our in basics.items()
                                    if their in expected and isinstance(expected[their], int)}
                if 'the least change, as distinctions' in expected:
                    witness = mask(expected['the least change, as distinctions'])
                    archived_numbers['archived_change_is_minimum'] = True
                    archived_numbers['archived_change_is_label'] = expected['the least change is also a class label']
                    view['archived_change_is_minimum'] = (witness.bit_count() == view['d_change'] and
                                                          Span(changes.allowed).remainder(witness) == 0 and
                                                          changes.motion.remainder(witness) != 0)
                    view['archived_change_is_label'] = changes.is_label(witness)
                view['archived_read_missing'] = 'd_read' in expected and not isinstance(expected['d_read'], int)
                compare(view, archived_numbers, (size, age, reading), comparison)
                row[reading] = view
            rows.append(row)
    return {'rows': rows, 'compared_to_committed_ring_archive': comparison}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--part', choices=('funded', 'sign', 'long'), required=True)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    start = monotonic()
    data = {'funded': funded_replays, 'sign': sign_replays, 'long': long_replays}[args.part](args.pilot)
    meta = {'part': args.part, 'pilot': args.pilot, 'seconds': round(monotonic() - start, 3),
            'peak_rss_kib': getrusage(RUSAGE_SELF).ru_maxrss}
    print(json.dumps(meta | data, indent=2))


if __name__ == '__main__':
    main()
