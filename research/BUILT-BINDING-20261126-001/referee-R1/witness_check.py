"""Replay the sampled paths and the static three-ring construction.

The earlier certificates and this study's readouts supply comparison data.
The growth, carriers, parity equations, and move readers below are independent.
"""

import argparse
from collections import Counter, defaultdict, deque
from functools import reduce
from itertools import combinations, count, product
import json
from operator import xor
from pathlib import Path
from random import Random
import resource
import sys
from time import perf_counter

from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = HERE.parents[2]
EARLIER = STUDY.parent / 'BINDING-20261126-001' / 'referee-R1'
LAYER = STUDY.parent / 'LAYERS-20261126-001' / 'referee-R1'
EVEN = ['000', '011', '101', '110']
ALL = [f'{v:03b}' for v in range(8)]
MEMORY = 2 * 1024**3


def mask(names):
    return sum(1 << i for i in names)


def bits(word):
    while word:
        lowest = word & -word
        yield lowest.bit_length() - 1
        word ^= lowest


def odd(left, right):
    return (left & right).bit_count() & 1


def space(generators):
    words = [0]
    for generator in generators:
        words += [word ^ generator for word in words]
    return words


class Laws:
    """Reduce binary linear equations and keep a certificate of row sums."""

    def __init__(self, equations):
        self.pivots = {}
        for i, equation in enumerate(equations):
            rest, used = self.reduce(equation)
            if rest:
                self.pivots[rest.bit_length() - 1] = (rest, used ^ (1 << i))
        self.order = sorted(self.pivots)

    def reduce(self, word):
        used = 0
        for i in sorted(self.pivots, reverse=True):
            if (word >> i) & 1:
                row, parents = self.pivots[i]
                word ^= row
                used ^= parents
        return word, used

    def rank(self):
        return len(self.pivots)

    def null_basis(self, width):
        for free in range(width):
            if free in self.pivots:
                continue
            solution = 1 << free
            for i in self.order:
                if odd(solution, self.pivots[i][0]):
                    solution |= 1 << i
            yield solution


def image(solutions, carriers):
    directions = [mask(i for i, f in enumerate(carriers) if odd(state, f)) for state in solutions]
    pivots = Laws(directions).pivots
    words = space(row for row, _ in pivots.values())
    return sorted(''.join(str(word >> i & 1) for i in range(len(carriers))) for word in words)


def owners(rows):
    held = defaultdict(list)
    for knot, row in enumerate(rows):
        assert len(set(row)) == len(row)
        for d in row:
            held[d].append(knot)
    assert set(held) == set(range(len(held)))
    assert all(len(knots) in (1, 2) for knots in held.values())
    return held


def neighbours(rows):
    result = [set() for _ in rows]
    for knots in owners(rows).values():
        if len(knots) == 2:
            a, b = knots
            result[a].add(b)
            result[b].add(a)
    return result


def join_groups(roster, neighbours_of):
    """List maximal pairwise candidates without a common neighbour, then unused pairs."""
    pairs = {(a, b) for a, b in combinations(roster, 2) if neighbours_of[a] & neighbours_of[b]}
    after = defaultdict(set)
    for a, b in pairs:
        after[a].add(b)
    valid = set()
    pending = [(pair, after[pair[0]] & after[pair[1]]) for pair in pairs]
    while pending:
        members, choices = pending.pop()
        if len(members) >= 3 and not set.intersection(*(neighbours_of[k] for k in members)):
            valid.add(frozenset(members))
        intermediate = ((members + (k,), choices & after[k]) for k in choices)
        pending.extend(intermediate)
    maximal = [tuple(sorted(group)) for group in valid if not any(group < other for other in valid)]
    covered = {pair for group in maximal for pair in combinations(group, 2)}
    return sorted(maximal) + sorted(pairs - covered)


def grow(rows):
    """Complete-round ordinary growth, with the parity implication tested by row sums."""
    held = owners(rows)
    loose = {i: deque(d for d in row if len(held[d]) == 1) for i, row in enumerate(rows)}
    live = [k for k, remaining in loose.items() if remaining]
    if not live:
        return rows, {'end': 'closed'}
    groups = join_groups(live, neighbours(rows))
    demand = Counter(k for group in groups for k in group)
    shortages = {k: demand[k] - len(loose[k]) for k in live if demand[k] > len(loose[k])}
    if shortages:
        return rows, {'end': 'stalled', 'shortages': shortages}
    paid = [tuple(loose[k].popleft() for k in group) for group in groups]
    paid.extend((d,) for k in live for d in loose[k])
    assert sorted(d for row in paid for d in row) == sorted(d for d, ks in held.items() if len(ks) == 1)
    new_knots = range(len(rows), len(rows) + len(paid))
    scratch = rows + tuple(paid)
    forecast = Counter(k for group in join_groups(new_knots, neighbours(scratch)) for k in group)
    law_span = Laws(map(mask, rows))
    names = count(len(held))
    births = []
    for knot, inputs in zip(new_knots, paid, strict=True):
        implied = law_span.reduce(mask(inputs))[0] == 0
        fresh_count = forecast[knot] if implied else max(forecast[knot], 3 - len(inputs), 1)
        fresh = tuple(next(names) for _ in range(fresh_count))
        assert implied or fresh
        births.append(tuple(sorted(inputs)) + fresh)
    return rows + tuple(births), {'births': len(births)}


def sample_start(last=34):
    """Generate accepted ten-knot samples at the declared weighting through index last."""
    size = 10
    seed = 61261226 + size
    rng = Random(seed)
    pairs = tuple(combinations(range(size), 2))
    accepted = 0
    attempts = 0
    while accepted <= last:
        attempts += 1
        selected = [p for p in pairs if rng.random() < 2.75 / (size - 1)]
        meetings = [(a, b, rng.choice((1, 2))) for a, b in selected]
        loose = tuple(rng.choice((0, 1, 2)) for _ in range(size))
        named = count()
        rows = [[] for _ in range(size)]
        for a, b, multiplicity in meetings:
            for _ in range(multiplicity):
                d = next(named)
                rows[a].append(d)
                rows[b].append(d)
        for knot, extra in enumerate(loose):
            rows[knot].extend(next(named) for _ in range(extra))
        if sum(m for _, _, m in meetings) + sum(loose) > 30 or any(len(row) < 3 for row in rows):
            continue
        near = neighbours(rows)
        reached = {0}
        queue = [0]
        for knot in queue:
            new = near[knot] - reached
            reached.update(new)
            queue.extend(sorted(new))
        if len(reached) != size:
            continue
        accepted += 1
    return tuple(map(tuple, rows)), attempts


def static_start(variant):
    rows = [[] for _ in range(14)]
    names = count()

    def shared(a, b):
        name = next(names)
        rows[a].append(name)
        rows[b].append(name)
        return name

    rings = []
    from_joining_knots = []
    for a, b, c, d in ((0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11)):
        rings.append([shared(p, q) for p, q in ((a, b), (b, c), (c, d), (d, a))])
        rows[b].extend(next(names) for _ in range(2))
        rows[d].extend(next(names) for _ in range(2))
        from_joining_knots.append([shared(a, 12), shared(c, 13)])
    if variant != 'no v':
        shared(12, 13)
    extra = {'J loose': 1, 'J two loose': 2}.get(variant, 0)
    rows[12].extend(next(names) for _ in range(extra))
    return tuple(map(tuple, rows)), tuple(map(mask, rings)), tuple(map(mask, from_joining_knots))


def incidence(rows, separate_loose=False):
    links = defaultdict(list)
    ends = {}
    for d, knots in owners(rows).items():
        a = knots[0]
        if len(knots) == 2:
            b = knots[1]
        else:
            b = len(rows) + (d if separate_loose else 0)
        links[a].append((b, d))
        links[b].append((a, d))
        ends[d] = (a, b)
    return links, ends


def shortest(links, a, maximum=None, omit=None):
    distances = {a: 0}
    predecessors = defaultdict(list)
    queue = [a]
    for knot in queue:
        if distances[knot] == maximum:
            continue
        new_distance = distances[knot] + 1
        for other, distinction in links[knot]:
            if distinction == omit:
                continue
            if other not in distances:
                distances[other] = new_distance
                queue.append(other)
            if distances[other] == new_distance:
                predecessors[other].append((knot, distinction))
    return distances, predecessors


def shortest_supports(predecessors, a, b):
    pending = [(b, 0)]
    while pending:
        knot, used = pending.pop()
        if knot == a:
            yield used
        else:
            pending.extend((k, used | (1 << d)) for k, d in predecessors[knot])


def simple_walks(links, first, limit, closed):
    """Enumerate supports once up to their reverse or, for circuits, their start."""
    pending = [(first, frozenset((first,)), 0, 0)]
    while pending:
        knot, seen, used, length = pending.pop()
        for other, d in links[knot]:
            bit = 1 << d
            if used & bit:
                continue
            if closed and other == first and length >= 1:
                yield other, used | bit, length + 1
            elif other not in seen and (not closed or other > first):
                if not closed and other > first:
                    yield other, used | bit, length + 1
                if length + 1 < limit:
                    pending.append((other, seen | {other}, used | bit, length + 1))


def moves(rows):
    links, ends = incidence(rows)
    short = set()
    minimum = Counter()
    for d, (a, b) in ends.items():
        distances, predecessors = shortest(links, a, omit=d)
        length = distances.get(b)
        if length is not None:
            minimum[length + 1] += 1
            short.update(p | (1 << d) for p in shortest_supports(predecessors, a, b))
    circuits = {word for first in links for _, word, _ in simple_walks(links, first, 5, closed=True)}
    pairs = {word for word in circuits if word.bit_count() == 2}
    threes = {word for word in circuits if word.bit_count() == 3}
    # Any nonzero allowed change is a distinction-disjoint sum of circuits.
    # With no one-distinction circuits, 2+2 and 2+3 are the only extra cases through five.
    union = {a | b for a, b in combinations(pairs, 2) if not a & b}
    union.update(a | b for a, b in product(pairs, threes) if not a & b)
    small = circuits | union
    assert Laws(small).rank() == Laws(circuits).rank()
    assert all(all(not odd(m, mask(r)) for r in rows) for m in (short | small))
    return short, small, {
        'distinctions by shortest change size': dict(sorted(minimum.items())),
        'shortest changes by size': dict(sorted(Counter(m.bit_count() for m in short).items())),
        'changes of at most five by size': dict(sorted(Counter(m.bit_count() for m in small).items())),
        'elementary changes of at most five': len(circuits),
        'non-elementary changes of at most five': len(small - circuits),
    }


def minimum_changing_move(rows, carrier):
    """The shortest odd walk returning to its first holder gives a minimum change."""
    links, _ = incidence(rows)
    best = None
    for first in links:
        start = (first, 0)
        target = (first, 1)
        reached = {start}
        queue = [(start, 0, 0)]
        for (knot, parity), support, length in queue:
            if best is not None and length >= best.bit_count():
                break
            if (knot, parity) == target:
                best = support
                break
            for other, d in links[knot]:
                reached_state = (other, parity ^ ((carrier >> d) & 1))
                if reached_state not in reached:
                    reached.add(reached_state)
                    queue.append((reached_state, support ^ (1 << d), length + 1))
    if best is not None:
        assert odd(best, carrier) and all(not odd(best, mask(r)) for r in rows)
    return None if best is None else list(bits(best))


def reading(solutions, rows, carriers, changes):
    width = len(owners(rows))
    out = []
    initial = image(solutions, carriers)
    fixed = []
    for row in rows:
        fixed_zero = list(Laws([*map(mask, rows), *(1 << d for d in row)]).null_basis(width))
        fixed.append((fixed_zero, image(fixed_zero, carriers)))
    for carrier in carriers:
        flipped = sorted((move for move in changes if odd(carrier, move)), key=lambda m: (m.bit_count(), m))
        readable = [i for i, (states, _) in enumerate(fixed) if all(not odd(carrier, s) for s in states)]
        out.append({
            'class fact': bool(not flipped and any(odd(carrier, s) for s in solutions)),
            'read by no single knot': not readable,
            'knots that can read it': readable,
            'changes that flip it': len(flipped),
            'example changing support': list(bits(flipped[0])) if flipped else None,
        })
    assignments = [len(image(solutions, [1 << d for d in row])) for row in rows]
    return out, {
        'knots with all tuples in every feasible reading': sum(values == initial for _, values in fixed),
        'knots checked': len(rows),
        'feasible readings counted over the knots': sum(assignments),
        'tuple counts with each knot fixed to zero': [len(values) for _, values in fixed],
    }


def class_counts(rows, width, equations, solutions, changes):
    move_span = Laws(changes)
    labels = list(move_span.null_basis(width))
    representatives = Laws(equations)
    label_basis = Laws(representatives.reduce(f)[0] for f in labels)
    k = label_basis.rank()
    nonzero = [f for f in space(v for v, _ in label_basis.pivots.values()) if f]
    local = [Laws(representatives.reduce(1 << d)[0] for d in row) for row in rows]
    readable = [f for f in nonzero if any(law.reduce(f)[0] == 0 for law in local)]
    unread = sorted(set(nonzero) - set(readable))
    triples = Counter()
    for a, b, c in combinations(unread, 3):
        label = 'three unread labels, independent' if a ^ b ^ c else 'three unread labels, the third the sum of two'
        triples[label] += 1
    assert k == len(solutions) - move_span.rank()
    return {'k': k, 'joint rank': k, 'individually unread': len(unread),
            'jointly unread': k - Laws(readable).rank(), 'triples of unread labels': dict(triples)}


def sat_image(rows, carriers):
    """Check every tuple with a direct truth-table parity encoding."""
    width = len(owners(rows))

    def excludes(group, assignment):
        return [-(d + 1) if b else d + 1 for d, b in zip(group, assignment, strict=True)]

    def parity_clauses(group, parity):
        return [excludes(group, assignment) for assignment in product((0, 1), repeat=len(group))
                if (sum(assignment) & 1) != parity]

    clauses = [clause for row in rows for clause in parity_clauses(row, 0)]
    attained = {}
    for values in product((0, 1), repeat=len(carriers)):
        extra = [clause for carrier, value in zip(carriers, values, strict=True)
                 for clause in parity_clauses(list(bits(carrier)), value)]
        with Solver(bootstrap_with=clauses + extra) as solver:
            if solver.solve():
                model = mask(literal - 1 for literal in solver.get_model() if 0 < literal <= width)
                assert all(not odd(model, mask(row)) for row in rows)
                assert tuple(odd(model, carrier) for carrier in carriers) == values
                attained[''.join(map(str, values))] = list(bits(model))
    return attained


def knot_tests(values):
    """Pass only the measured relation to the canonical checker."""
    sys.path.insert(0, str(ROOT / 'tools'))
    from knotlab.cli import parse_cnf
    from knotlab.knots import check_knot
    from knotlab.relations import Relation

    names = ('z1', 'z2', 'z3')
    clauses = '; '.join(' '.join(name if v == '0' else '~' + name for name, v in zip(names, word))
                        for word in ALL if word not in values) or 'z1 ~z1'
    result = []
    for contact in ('z3', 'z1', 'z2'):
        loops = [name for name in names if name != contact]
        relation = Relation.from_cnf(parse_cnf(clauses), [*loops, contact])
        verdict = check_knot(relation, loops, contact)
        result.append({'contact': contact, 'clauses': clauses, 'checker': {
            **verdict.as_dict(), 'notes': list(verdict.notes), 'loops': list(verdict.loops),
            'allowed': sorted(relation.table()), 'variables': list(relation.variables),
        }})
    return result


def representatives(start, rows, carriers):
    older = len(owners(start))
    old_mask = (1 << older) - 1
    new_laws = list(map(mask, rows))
    start_laws = list(map(mask, start))
    new_only = Laws(row & ~old_mask for row in new_laws)
    start_solutions = list(Laws(start_laws).null_basis(older))
    projected = [s & old_mask for s in Laws(new_laws).null_basis(len(owners(rows)))]
    assert Laws(projected).rank() == len(start_solutions)
    assert all(all(not odd(s, r) for r in start_laws) for s in projected)
    reps = []
    traces = []
    for f in carriers:
        remainder, law_sum = new_only.reduce(f & ~old_mask)
        if remainder:
            return None, None
        combined = f ^ reduce(xor, (new_laws[i] for i in bits(law_sum)), 0)
        assert combined & ~old_mask == 0
        reps.append(combined)
        traces.append(list(bits(law_sum)))
    return reps, traces


def start_supports(start, representatives):
    """Enumerate all start supports that read the same values."""
    laws = Laws(map(mask, start))
    constraints = space(row for row, _ in laws.pivots.values())
    return [[f ^ constraint for constraint in constraints] for f in representatives]


def minimum_supports(alternatives):
    width = min(support.bit_count() for support in alternatives)
    return {'number of equivalent supports': len(alternatives), 'smallest count': width,
            'all smallest supports': sorted(list(bits(s)) for s in alternatives if s.bit_count() == width)}


def minimum_disjoint_triples(supports):
    grouped = []
    for family in supports:
        by_size = defaultdict(list)
        for support in family:
            by_size[support.bit_count()].append(support)
        grouped.append(by_size)
    best = None
    matches = []
    for counts in sorted(product(*grouped), key=sum):
        total = sum(counts)
        if best is not None and total > best:
            break
        for a, b, c in product(*(g[w] for g, w in zip(grouped, counts, strict=True))):
            if not (a & b or (a | b) & c):
                best = total
                matches.append((a, b, c))
    assert best is not None
    return best, sorted(matches)


def check_relabelled(rows, carriers, short, small):
    width = len(owners(rows))

    def rename(word):
        return mask(width - 1 - d for d in bits(word))

    renamed_rows = tuple(tuple(width - 1 - d for d in row) for row in reversed(rows))
    renamed_carriers = [rename(carrier) for carrier in carriers]
    renamed_short, renamed_small, _ = moves(renamed_rows)
    assert {rename(m) for m in renamed_short} == short
    assert {rename(m) for m in renamed_small} == small
    assert sorted(sat_image(renamed_rows, renamed_carriers)) == sorted(sat_image(rows, carriers))
    return True


def deletion_counts(equations, width, carriers, start_size):
    frees = []
    unchanged = []
    for i in range(len(equations)):
        without = Laws(equations[:i] + equations[i + 1:]).null_basis(width)
        values = image(without, carriers)
        if values == ALL:
            frees.append(i)
        else:
            assert values == EVEN
            unchanged.append(i)
    return {'start knots': sum(i < start_size for i in frees), 'born knots': sum(i >= start_size for i in frees),
            'of start / born': [start_size, len(equations) - start_size], 'indices freeing it': frees,
            'indices leaving it': unchanged}


def forced_cycle_sums(rows, equations):
    held = owners(rows)
    coefficients = [mask(i for i, row in enumerate(equations) if odd(row, trial)) for trial in equations]
    intersect = Laws(coefficients)
    def to_support(v):
        return reduce(xor, (equations[i] for i in bits(v)), 0)

    intersection_rank = Laws(to_support(v) for v in intersect.null_basis(len(rows))).rank()
    coefficients += [1 << ks[0] for ks in held.values() if len(ks) == 1]
    restricted = Laws(coefficients)
    basis = Laws(to_support(v) for v in restricted.null_basis(len(rows)))
    return intersection_rank, sorted(space(row for row, _ in basis.pivots.values()))[1:]


def paths(rows, carriers, short, small, previous, start):
    links, ends = incidence(rows, separate_loose=True)
    equations = Laws(map(mask, rows))
    local = [Laws(equations.reduce(1 << d)[0] for d in row) for row in rows]
    previous_laws = Laws(map(mask, previous))
    start_laws = Laws(map(mask, start))
    families = {name: defaultdict(set) for name in ('shortest', 'all', 'shortest up to five', 'all up to five')}
    total_paths = set()
    shortest_paths = set()
    for first in sorted(links):
        distances, _ = shortest(links, first, maximum=8)
        for last, support, length in simple_walks(links, first, 8, closed=False):
            total_paths.add(support)
            is_shortest = length == distances[last]
            if is_shortest:
                shortest_paths.add(support)
            value = equations.reduce(support)[0]
            if value == 0 or any(law.reduce(value)[0] == 0 for law in local):
                continue
            for changes, all_name, shortest_name in ((short, 'all', 'shortest'), (small, 'all up to five', 'shortest up to five')):
                if any(odd(support, m) for m in changes):
                    continue
                families[all_name][value].add(support)
                if is_shortest:
                    families[shortest_name][value].add(support)
    output = {'all supports visited': len(total_paths), 'shortest supports visited': len(shortest_paths),
              'maximum path length': 8}
    for name, by_value in families.items():
        triples = []
        for a, b, c in combinations(sorted(by_value), 3):
            if a ^ b ^ c:
                continue
            for p, q, r in product(by_value[a], by_value[b], by_value[c]):
                if p & q or (p | q) & r:
                    continue
                total = p ^ q ^ r
                tuples = image(equations.null_basis(len(ends)), (p, q, r))
                assert tuples == EVEN
                triples.append({'supports': sorted(list(bits(m)) for m in (p, q, r)),
                                'uses the current round': previous_laws.reduce(total)[0] != 0,
                                'uses post-start laws': start_laws.reduce(total)[0] != 0})
        output[name] = {'unread values': len(by_value), 'unread supports': sum(map(len, by_value.values())),
                        'disjoint triples': sorted(triples, key=lambda x: x['supports'])}
    tied = []
    for carrier in carriers:
        degrees = Counter(k for d in bits(carrier) for k in ends[d])
        a, b = sorted(k for k, degree in degrees.items() if degree == 1)
        assert all(degree <= 2 for degree in degrees.values())
        distances, back = shortest(links, a)
        alternatives = sorted(shortest_supports(back, a, b))
        assert carrier in alternatives and distances[b] == carrier.bit_count()
        tied.append({
            'endpoints': [k if k < len(rows) else f'loose {k - len(rows)}' for k in (a, b)],
            'path length': distances[b], 'shortest supports': len(alternatives),
            'invariant under shortest changes': [list(bits(m)) for m in alternatives if all(not odd(m, c) for c in short)],
            'invariant under changes of at most five': [list(bits(m)) for m in alternatives if all(not odd(m, c) for c in small)],
        })
    output['tied at the reported endpoints'] = tied
    return output


def inspect_stage(rows, carriers, start, round_number, literal=False):
    width = len(owners(rows))
    equations = list(map(mask, rows))
    law_span = Laws(equations)
    solutions = list(law_span.null_basis(width))
    short, small, move_counts = moves(rows)
    result = {'round': round_number, 'knots': len(rows), 'distinctions': width,
              'allowed states': 1 << len(solutions), 'moves': move_counts}
    if literal:
        allowed = space(solutions)
        assert all(all(not odd(s, r) for r in equations) for s in allowed)
        assert small == {s for s in allowed if 0 < s.bit_count() <= 5}
        first_sizes = {}
        literal_short = set()
        for state in sorted(allowed, key=int.bit_count):
            length = state.bit_count()
            for d in bits(state):
                if first_sizes.setdefault(d, length) == length:
                    literal_short.add(state)
        assert short == literal_short
        result['moves']['literal enumeration matched'] = True
    result['class counts'] = {rule: class_counts(rows, width, equations, solutions, changes)
                              for rule, changes in (('SHORT', short), ('UPTO5', small))}
    if not carriers:
        return result, short, small
    result['carriers'] = [list(bits(m)) for m in carriers]
    result['tuples'] = image(solutions, carriers)
    attained = sat_image(rows, carriers)
    assert sorted(attained) == result['tuples']
    result['assignments for attained tuples'] = attained
    result['SHORT'], conditional = reading(solutions, rows, carriers, short)
    result['UPTO5'], _ = reading(solutions, rows, carriers, small)
    result['conditional reads'] = conditional
    result['least changing support'] = [minimum_changing_move(rows, f) for f in carriers]
    if result['tuples'] == EVEN:
        rest, used = law_span.reduce(reduce(xor, carriers))
        assert not rest
        result['laws giving even parity'] = list(bits(used))
        result['laws whose removal frees every tuple'] = deletion_counts(equations, width, carriers, len(start))
    return result, short, small


def flags(facts):
    return [[fact['class fact'], fact['read by no single knot']] for fact in facts]


def read_path(pilot):
    certificate = json.loads((EARLIER / 'path_certificate.json').read_text())
    archive = json.loads((STUDY / 'repro_paths.json').read_text())
    layer_record = json.loads((LAYER / 'extended_witness.json').read_text())[0]
    start, attempts = sample_start()
    assert [list(row) for row in start] == layer_record['start supports']
    carriers = tuple(map(mask, certificate['path_supports']))
    stages = [start]
    for _ in range(3 if pilot else 4):
        next_stage, status = grow(stages[-1])
        assert 'births' in status
        stages.append(next_stage)
    initial, _ = representatives(start, stages[3], carriers)
    start_laws = Laws(map(mask, start))
    support_options = start_supports(start, initial)
    minimum, disjoint = minimum_disjoint_triples(support_options)
    disjoint = [[list(bits(s)) for s in triple] for triple in disjoint]
    assert minimum == 9 and disjoint == [[[0, 18], [10, 11, 27, 28], [21, 22, 24]]]
    disjoint_carriers = tuple(map(mask, disjoint[0]))
    rounds = []
    for t, rows in enumerate(stages):
        if t < 3 and pilot:
            continue
        if t == 3:
            assert [list(row) for row in rows] == certificate['grown_knots']
        preceding = stages[t - 1] if t else start
        present = tuple(carrier for carrier in carriers if carrier.bit_length() <= len(owners(rows)))
        record, short, small = inspect_stage(rows, present, start, t, literal=t == 0)
        record['paths through eight distinctions'] = paths(rows, carriers if t >= 3 else (), short, small, preceding, start)
        source_reads, _, _ = inspect_stage(rows, disjoint_carriers, start, t)
        record['read on disjoint start supports'] = {field: source_reads[field]
                                                     for field in ('tuples', 'SHORT', 'UPTO5', 'conditional reads',
                                                                   'laws giving even parity')}
        assert source_reads['tuples'] == EVEN
        assert all(k < len(start) for k in source_reads['laws giving even parity'])
        assert flags(source_reads['SHORT']) == ([[True, True]] * 3 if t else [[True, True], [False, True], [False, True]])
        assert flags(source_reads['UPTO5']) == ([[False, True]] * 2 + [[True, True]] if t >= 2 else [[False, True]] * 3)
        if t >= 3:
            old_reps, sources = representatives(start, rows, carriers)
            assert old_reps == initial
            assert all(not start_laws.reduce(f ^ g)[0] for f, g in zip(old_reps, disjoint_carriers, strict=True))
            current, _, _ = inspect_stage(start, old_reps, start, 0)
            assert current['tuples'] == record['tuples']
            expected = next(row for row in archive['rounds'] if row['round'] == t)
            for rule in ('SHORT', 'UPTO5'):
                assert flags(record[rule]) == expected[rule]
                assert flags(current[rule]) == expected['origin'][f'facts at the start, {rule}']
            assert [f.bit_count() for f in old_reps] == expected['origin']['start representatives (sizes)']
            assert record['tuples'] == EVEN and expected['tuples'] == 4 and expected['one rule']
            for key, value in expected['laws whose removal frees every tuple'].items():
                assert record['laws whose removal frees every tuple'][key] == value
            record['origin'] = {'start representatives': [list(bits(f)) for f in old_reps],
                                'birth-law sums used to replace each support': sources,
                                'start law sum': current['laws giving even parity'],
                                'start SHORT': current['SHORT'], 'start UPTO5': current['UPTO5'],
                                'start least changing support': current['least changing support'],
                                'start conditional reads': current['conditional reads']}
            if t == 3:
                assert sum(record['moves']['shortest changes by size'].values()) == certificate['shortest_changes']
                assert record['laws giving even parity'] == certificate['laws_giving_the_relation']
                record['canonical checks'] = knot_tests(record['tuples'])
                assert all(c['checker']['is_knot'] for c in record['canonical checks'])
                record['renaming preserved both move sets and the tuples'] = check_relabelled(rows, carriers, short, small)
                trip = record['paths through eight distinctions']['shortest']
                assert trip['unread supports'] == 10 and len(trip['disjoint triples']) == 3
        rounds.append(record)
    return {'weighting': {'knots': 10, 'seed': 61261236, 'meeting chance per pair': '2.75/9',
                         'shared multiplicity uniform on': [1, 2], 'loose counts uniform on': [0, 1, 2],
                         'kept if': 'connected, at least three distinctions per knot, at most 30 distinctions',
                         'accepted sample index, counting from zero': 34, 'proposals through it': attempts},
            'start': start, 'rounds': rounds, 'minimum start representations': list(map(minimum_supports, support_options)),
            'disjoint start supports with fewest total distinctions': {'total distinctions': minimum, 'triples': disjoint}}


def read_static(variant, archived, checked, pilot):
    start, rings, smaller = static_start(variant)
    rows = start
    rounds = []
    for t in range(1 if pilot or variant == 'J two loose' else 4):
        if t:
            rows, growing = grow(rows)
            if 'end' in growing:
                rounds.append({'round': t, **growing})
                assert archived[t]['end'] == growing['end']
                break
        data, short, small = inspect_stage(rows, rings, start, t, literal=t == 0)
        equations = list(map(mask, rows))
        assert all(Laws(equations).reduce(f ^ g)[0] == 0 for f, g in zip(rings, smaller, strict=True))
        representatives_here, _ = representatives(start, rows, rings)
        assert list(rings) == representatives_here
        data['equivalent two-distinction supports'] = [list(bits(f)) for f in smaller]
        if variant in ('J loose', 'J two loose'):
            loose = [d for d in rows[12] if len(owners(rows)[d]) == 1]
            assert Laws(equations).reduce(reduce(xor, rings) ^ mask(loose))[0] == 0
            data['sum of the ring parities is the parity of these loose distinctions'] = loose
        intersection_rank, cycle_sums = forced_cycle_sums(rows, equations)
        assert cycle_sums in ([], [reduce(xor, rings)])
        data['forced cycle sum supports'] = [list(bits(f)) for f in cycle_sums]
        data['dimension of law sums that are changes'] = intersection_rank
        data['conditional read with two joining knots fixed to zero'] = image(
            Laws([*equations, *(1 << d for d in sorted(set(rows[12]) | set(rows[13])))])
            .null_basis(len(owners(rows))), rings,
        )
        if archived:
            expected = archived[t]
            equality_b = expected['B']
            assert len(data['tuples']) == expected['tuples of the ring facts']
            assert (data['tuples'] == EVEN) == expected['one parity rule, every proper part free']
            assert data['distinctions'] == expected['distinctions'] == equality_b['distinctions']
            assert equality_b['dim Z'] == data['allowed states'].bit_length() - 1
            assert equality_b['dim of laws ∩ changes'] == intersection_rank
            assert equality_b['dim B'] == len(cycle_sums)
            if cycle_sums:
                element, = equality_b['elements']
                assert element['size'] == cycle_sums[0].bit_count()
                assert element['knots summing to it'] == data['laws giving even parity']
                assert not element['holds a knot born after the start']
            for rule in ('SHORT', 'UPTO5'):
                expected_facts = expected[rule]['ring facts']
                assert flags(data[rule]) == [[f['label'], f['read by no single knot']] for f in expected_facts]
                assert data['class counts'][rule] == expected[rule]['classes']
                if cycle_sums:
                    assert expected[rule]['judge']['most cycles in a split'] == len(rings)
                if data['tuples'] == EVEN and all(f == [True, True] for f in flags(data[rule])):
                    assert [list(bits(ring)) for ring in rings] == expected[rule]['judge']['bindings'][0]['parts as distinctions']
                else:
                    assert not expected[rule]['judge']['bindings']
        if t == 0 and checked:
            data['canonical checks'] = knot_tests(data['tuples'])
            assert [[int(v) for v in word] for word in data['tuples']] == checked['tuples']
            assert data['canonical checks'] == checked['checks']
            if variant == 'base':
                data['renaming preserved both move sets and the tuples'] = check_relabelled(rows, rings, short, small)
        rounds.append(data)
    return {'start': start, 'rounds': rounds,
            'minimum start representations': list(map(minimum_supports, start_supports(start, rings)))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY, MEMORY))
    began = perf_counter()
    archived = {}
    for name in ('built_explore.jsonl', 'built_controls_explore.jsonl'):
        archived.update({row['variant']: row['rounds'] for line in (STUDY / name).read_text().splitlines()
                         for row in (json.loads(line),)})
    checked = {row['variant']: row for row in json.loads((STUDY / 'checker.json').read_text())}
    path = read_path(args.pilot)
    variants = ('base', 'J two loose') if args.pilot else ('base', 'no v', 'J loose', 'J two loose')
    static = {v: read_static(v, archived.get(v), checked.get(v), args.pilot) for v in variants}
    output = {'sampled ten-knot paths': path, 'static three-ring start and controls': static,
              'seconds': round(perf_counter() - began, 3)}
    if args.output:
        assert args.output.resolve().parent == HERE and args.output.name.startswith('witness_')
        args.output.write_text(json.dumps(output, indent=2) + '\n')
    print(f"{len(path['rounds'])} sampled path stages and "
          f"{sum(len(item['rounds']) for item in static.values())} static and control entries in {output['seconds']} s")


if __name__ == '__main__':
    main()
