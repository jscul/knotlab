"""Recount small birth and census codes and replay the closed-pattern sample."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations, product
import json
from pathlib import Path
import random
import resource
from time import monotonic


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
RESEARCH = STUDY.parent
PRIOR = RESEARCH / 'READER-SPLIT-20261127-001' / 'referee-R1'
SMALL_LIMIT = 14
LIST_LIMIT = 8
SAMPLE_PER_CODE = 64
SAMPLE_SEED = 20261127
PATTERN_SEED = 4040
PATTERN_ATTEMPTS = 450
PATTERN_LIMIT = 12


def read_jsonl(path):
    with path.open() as stream:
        for line in stream:
            yield json.loads(line)


def positions(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def dependency_basis(columns):
    """Use column elimination while tracking the combination of input columns."""
    pivots = {}
    basis = []
    for index, column in enumerate(columns):
        word = 1 << index
        while column:
            lead = column.bit_length() - 1
            old = pivots.get(lead)
            if old is None:
                pivots[lead] = column, word
                break
            column ^= old[0]
            word ^= old[1]
        else:
            basis.append(word)
    return basis


def words(basis):
    word = 0
    for ordinal in range(1, 1 << len(basis)):
        word ^= basis[(ordinal & -ordinal).bit_length() - 1]
        yield ordinal, word


def steps(cycle):
    return zip(cycle, cycle[1:] + cycle[:1])


def cyclic_order(one, other):
    """Take the alternating order with least first knot and least next knot."""
    if min(one) > min(other):
        one, other = other, one
    a, b = sorted(one)
    c, d = sorted(other)
    return a, c, b, d


def cross_pair(a, b):
    return (a, b) if a < b else (b, a)


class Code:
    def __init__(self, supports, pairs=None):
        self.supports = supports
        holders = defaultdict(list)
        for knot, distinctions in enumerate(supports):
            for distinction in distinctions:
                holders[distinction].append(knot)
        assert all(len(set(holdings)) == len(holdings) == 2 for holdings in holders.values())
        self.holders = holders
        self.pairs = list(pairs) if pairs is not None else [
            (a, b) for a, b in combinations(sorted(holders), 2)
            if set(holders[a]).isdisjoint(holders[b])
        ]
        assert len({tuple(pair) for pair in self.pairs}) == len(self.pairs)

        # Build each commutation column from holders independently of cycle order.
        knot_pairs = list(combinations(range(len(supports)), 2))
        knot_pair_id = {pair: i for i, pair in enumerate(knot_pairs)}
        self.checks = [0] * len(knot_pairs)
        cost = 0
        step_cost = 0
        columns = []
        incident_by_distinction = defaultdict(int)
        self.cycles = []
        for index, (a, b) in enumerate(self.pairs):
            left, right = holders[a], holders[b]
            assert len(set(left) | set(right)) == 4
            column = 0
            for u, v in product(left, right):
                j = knot_pair_id[cross_pair(u, v)]
                self.checks[j] |= 1 << index
                column |= 1 << j
            columns.append(column)
            for distinction in (a, b):
                incident_by_distinction[distinction] |= 1 << index

            # One inversion per pair of occurrences exchanged when sorted by distinction.
            cost |= (sum(u > v for u, v in product(left, right)) % 2) << index
            cycle = cyclic_order(left, right)
            self.cycles.append(cycle)
            step_cost |= (sum(u < v for u, v in steps(cycle)) % 2) << index

        assert cost == step_cost
        self.cost = cost
        self.columns = columns
        self.basis = dependency_basis(columns)
        assert all(not (basis & check).bit_count() % 2 for basis in self.basis for check in self.checks)
        active = 0
        for word in self.basis:
            active |= word
        self.coverage_masks = [check & active for check in self.checks if check & active]
        self.strict_masks = sorted(
            (mask & active for mask in incident_by_distinction.values() if (mask & active).bit_count() > 1),
            key=int.bit_count, reverse=True,
        )

    def sign(self, word):
        return (word & self.cost).bit_count() % 2

    def strict(self, word):
        return all((word & mask).bit_count() <= 1 for mask in self.strict_masks)

    def cycle_word(self, word):
        return [self.cycles[index] for index in positions(word)]

    def minimal(self, word):
        return len(dependency_basis([self.columns[i] for i in positions(word)])) == 1

    def witness(self, word):
        selected = list(positions(word))
        return {
            'holdings': self.supports,
            'sign': self.sign(word),
            'strict': self.strict(word),
            'minimal': self.minimal(word),
            'selected failing pairs': [self.pairs[i] for i in selected],
            'cycles of those pairs': [self.cycles[i] for i in selected],
            'cross-pair coverage': [
                [u, v, (self.checks[i] & word).bit_count()]
                for i, (u, v) in enumerate(combinations(range(len(self.supports)), 2))
                if self.checks[i] & word
            ],
        }

    def reader_partition(self, word):
        failing = [self.pairs[i] for i in positions(word)]
        active = {distinction for pair in failing for distinction in pair}
        groups = DisjointSets(active)
        for a, b in failing:
            groups.join(a, b)
        occupied = defaultdict(set)
        readers = defaultdict(list)
        for distinction in sorted(active):
            parent = groups.root(distinction)
            holders = self.holders[distinction]
            if not occupied[parent].isdisjoint(holders):
                return None
            occupied[parent].update(holders)
            readers[parent].append(distinction)
        return sorted(readers.values())


class DisjointSets:
    def __init__(self, elements):
        self.parent = {element: element for element in elements}

    def root(self, element):
        parent = self.parent
        while parent[element] != element:
            parent[element] = parent[parent[element]]
            element = parent[element]
        return element

    def join(self, first, second):
        self.parent[self.root(first)] = self.root(second)


def cycle_incidences(cycles):
    occurrences = defaultdict(list)
    for index, cycle in enumerate(cycles):
        assert len(set(cycle)) == 4
        for u, v in steps(cycle):
            occurrences[cross_pair(u, v)].append((index, u < v))
    return occurrences


def lists_forward(incidences, rng):
    n = max(i for row in incidences.values() for i, _ in row) + 1
    flipped_cycles = rng.getrandbits(n)
    flipped_references = rng.getrandbits(len(incidences))
    total = 0
    same = 0
    for pair_index, row in enumerate(incidences.values()):
        reverse_ref = (flipped_references >> pair_index) & 1
        forward = sum(direction ^ ((flipped_cycles >> cycle_index) & 1) ^ reverse_ref
                      for cycle_index, direction in row)
        total += forward
        same += len(row) == 2 and forward != 1
    return total % 2, same % 2


def weak_balance(incidences, n):
    # Each row states how the listed parity changes when its cycles reverse.
    rows = [sum(1 << i for i, _ in row)
            | (((len(row) // 2 - sum(direction for _, direction in row)) % 2) << n)
            for row in incidences.values()]
    rhs = 1 << n
    mask = rhs - 1
    pivots = {}
    for row in rows:
        while row & mask:
            lead = (row & mask).bit_length() - 1
            if lead not in pivots:
                pivots[lead] = row
                break
            row ^= pivots[lead]
        else:
            if row == rhs:
                return False
    return True


def orientable(cycles, incidences, weak):
    if not weak:
        return False
    if all(len(row) == 2 for row in incidences.values()):
        # For two occurrences, odd forward count means exactly one forward.
        return True

    # A group of repeated cycles contributes a signed multiplicity between
    # minus and plus its size in steps of two. Search these exact integer sums.
    pair_id = {pair: index for index, pair in enumerate(incidences)}
    grouped = Counter(cycles)
    constraints = []
    residual = [0] * len(incidences)
    capacity = [len(row) for row in incidences.values()]
    for cycle, multiplicity in grouped.items():
        effects = [(pair_id[cross_pair(u, v)], 1 if u < v else -1) for u, v in steps(cycle)]
        pivot_order = sum(capacity[pair] for pair, _ in effects)
        constraints.append((pivot_order, multiplicity, effects))
    constraints.sort()

    def balance(index):
        if index == len(constraints):
            return True
        _, multiplicity, effects = constraints[index]
        lo, hi = -multiplicity, multiplicity
        for pair, direction in effects:
            capacity[pair] -= multiplicity
            center = -direction * residual[pair]
            lo = max(lo, center - capacity[pair])
            hi = min(hi, center + capacity[pair])
        lo += (lo - multiplicity) % 2
        options = sorted(range(lo, hi + 1, 2), key=abs)
        for difference in options:
            for pair, direction in effects:
                residual[pair] += difference * direction
            if balance(index + 1):
                return True
            for pair, direction in effects:
                residual[pair] -= difference * direction
        for pair, _ in effects:
            capacity[pair] += multiplicity
        return False

    return balance(0)


def two_colourable(pairs):
    neighbours = defaultdict(set)
    for u, v in pairs:
        neighbours[u].add(v)
        neighbours[v].add(u)
    colours = {}
    for knot in neighbours:
        if knot in colours:
            continue
        colours[knot] = 0
        pending = [knot]
        while pending:
            u = pending.pop()
            for v in neighbours[u]:
                wanted = 1 - colours[u]
                if v in colours:
                    if colours[v] != wanted:
                        return False
                else:
                    colours[v] = wanted
                    pending.append(v)
    return True


def separation(cycles, incidences):
    # Identify the two occurrences of each end of each twice-covered pair.
    occurrences = DisjointSets((i, knot) for i, cycle in enumerate(cycles) for knot in cycle)
    components = DisjointSets(range(len(cycles)))
    for (u, v), ((i, _), (j, _)) in incidences.items():
        occurrences.join((i, u), (j, u))
        occurrences.join((i, v), (j, v))
        components.join(i, j)
    roots = {occurrences.root(item) for item in occurrences.parent}
    split_cycles = [tuple(occurrences.root((i, knot)) for knot in cycle) for i, cycle in enumerate(cycles)]
    split_pairs = cycle_incidences(split_cycles)
    assert len(split_pairs) == len(incidences) and all(len(row) == 2 for row in split_pairs.values())
    before = sum(row[0][1] == row[1][1] for row in incidences.values())
    after = sum(row[0][1] == row[1][1] for row in split_pairs.values())
    assert before % 2 == after % 2
    return len(roots), len({components.root(i) for i in range(len(cycles))})


def structure(cycles, incidences):
    max_cover = max(map(len, incidences.values()))
    assert all(len(row) % 2 == 0 for row in incidences.values())
    weak = weak_balance(incidences, len(cycles))
    oriented = orientable(cycles, incidences, weak)
    coloured = two_colourable(incidences)
    knots = len({knot for cycle in cycles for knot in cycle})
    out = {'exactly two': max_cover == 2, 'one cycle at every knot': False, 'orientable': oriented,
           'two-colourable': coloured, 'weak even condition': weak,
           'Euler count': knots - len(incidences) + len(cycles), 'most at a cross pair': max_cover}
    if max_cover == 2:
        separated_knots, components = separation(cycles, incidences)
        out.update({'one cycle at every knot': separated_knots == knots,
                    'separated Euler count': separated_knots - len(incidences) + len(cycles),
                    'separated components': components})
    return out


def brute_balance(incidences, n):
    targets = [len(row) // 2 for row in incidences.values()]
    can_balance = can_orient = False
    for flips in product((0, 1), repeat=n):
        actual = [sum(direction ^ flips[i] for i, direction in row) for row in incidences.values()]
        can_orient |= actual == targets
        can_balance |= all((a - b) % 2 == 0 for a, b in zip(actual, targets))
    return can_orient, can_balance


def check_corollaries(feature, sign):
    assert not (sign and any(feature[k] for k in ('orientable', 'weak even condition', 'two-colourable')))


def score(cycles, sign, rng, algebra_control=False):
    incidences = cycle_incidences(cycles)
    first, first_same = lists_forward(incidences, rng)
    second, second_same = lists_forward(incidences, rng)
    assert first == second == sign
    feature = structure(cycles, incidences)
    if feature['exactly two']:
        assert first_same == second_same == sign
    check_corollaries(feature, sign)
    if algebra_control and len(cycles) <= 8:
        assert (feature['orientable'], feature['weak even condition']) == brute_balance(incidences, len(cycles))
    return feature


@lru_cache(maxsize=32768)
def score_cycle_multiset(cycles):
    incidences = cycle_incidences(cycles)
    sign = sum(direction for row in incidences.values() for _, direction in row) % 2
    feature = structure(cycles, incidences)
    if feature['exactly two']:
        assert sign == sum(row[0][1] == row[1][1] for row in incidences.values()) % 2
    check_corollaries(feature, sign)
    return sign, feature


def tally():
    return {'choices': 0, 'theorem holds': 0, 'exactly two': 0, 'one cycle at every knot': 0, 'orientable': 0,
            'two-colourable': 0, 'weak even condition': 0, 'Euler counts': Counter(),
            'separated Euler counts': Counter(), 'most at a cross pair': Counter()}


def record(totals, feature, multiplicity=1):
    totals['choices'] += multiplicity
    totals['theorem holds'] += multiplicity
    for field in ('exactly two', 'one cycle at every knot', 'orientable', 'two-colourable', 'weak even condition'):
        totals[field] += multiplicity * feature[field]
    for field, source in (('Euler counts', 'Euler count'), ('separated Euler counts', 'separated Euler count'),
                          ('most at a cross pair', 'most at a cross pair')):
        if source in feature:
            totals[field][str(feature[source])] += multiplicity


def merge(target, incoming):
    for field, value in incoming.items():
        if isinstance(value, Counter):
            target[field].update(value)
        else:
            target[field] += value


def category(strict, sign):
    return ('strict' if strict else 'not strict') + (', odd' if sign else ', even')


def closed_sources():
    for source in read_jsonl(PRIOR / 'rebuilt_inputs.jsonl'):
        if source['population'] in {'birth', 'type'}:
            yield source


def compare_exact(exact, archive, population, key):
    for group in exact:
        expected = archive.get('small code, ' + group, tally())
        assert exact[group] == expected, (population, key, group, exact[group], expected)
    matching_groups = {name.removeprefix('small code, ') for name in archive if name.startswith('small code, ')}
    assert matching_groups == exact.keys(), (population, key, matching_groups, exact.keys())


def tally_codes(probe):
    archive = {
        'birth': {r['start']: r for r in read_jsonl(STUDY / 'results.jsonl')},
        'type': {r['type']: r for r in read_jsonl(STUDY / 'census_types.jsonl')},
    }
    prior_splits = {(r['population'], r['key']): r for r in read_jsonl(PRIOR / 'split_rows.jsonl')}
    totals = defaultdict(Counter)
    complete = defaultdict(lambda: defaultdict(tally))
    examined = defaultdict(lambda: defaultdict(tally))
    separated_parts = defaultdict(Counter)
    minimal_strict_sizes = defaultdict(Counter)
    list_overlap = Counter()
    rows = {'birth': {}, 'type': {}}
    examples = {}
    time_by_dimension = Counter()
    probe_dims = Counter()
    for source in closed_sources():
        population, key = source['population'], source['key']
        if probe and (source['dimension'] not in {1, 6, 10, 14} or probe_dims[source['dimension']] >= 1):
            continue
        probe_dims[source['dimension']] += 1
        started = monotonic()
        code = Code(source['supports'], source['pairs'])
        dim = len(code.basis)
        archived_row = archive[population][key]
        prior_split = prior_splits[population, key]
        no_split = prior_split['general_min'] is None
        strict_positive = prior_split['strict_min'] is not None
        assert (code.checks, code.cost, dim) == (source['checks'], source['cost'], source['dimension'])
        assert dim == archived_row['free choices']
        assert no_split == (archived_row["readers study's kind"] == 'none')
        totals[population]['codes'] += 1
        if population == 'birth':
            totals['no split']['codes'] += no_split
        if dim > SMALL_LIMIT:
            continue
        assert not archived_row.get('sizes at the cap')
        assert prior_split['strict_min'] == archived_row.get('fewest strict readers')
        unit = 'census start' if population == 'birth' else 'census type'
        groups = [population] + (['no split'] if population == 'birth' and no_split else [])
        for name in groups:
            totals[name]['small codes'] += 1
        selection_rng = random.Random(f'{SAMPLE_SEED}-{population}-{key}')
        sample = set(selection_rng.sample(range(1, 1 << dim), min(SAMPLE_PER_CODE, (1 << dim) - 1)))
        order_rng = random.Random(f'{SAMPLE_SEED}-orders-{population}-{key}')
        cycles_by_group = defaultdict(Counter)
        coverage_by_group = defaultdict(Counter)
        take = defaultdict(tally)
        sampled = defaultdict(tally)
        part_counts = defaultdict(Counter)
        sign_totals = Counter()
        for ordinal, word in words(code.basis):
            sign = code.sign(word)
            strict = code.strict(word)
            group = category(strict, sign)
            sign_totals[sign] += 1
            cycles = code.cycle_word(word)
            profile = tuple(sorted(cycles))
            cycles_by_group[group][profile] += 1
            largest = max((word & mask).bit_count() for mask in code.coverage_masks)
            coverage_by_group[group][str(largest)] += 1
            if strict and code.minimal(word):
                size = word.bit_count()
                for name in groups:
                    minimal_strict_sizes[name][f'{group}, {size} pairs'] += 1
                if strict_positive and size <= LIST_LIMIT:
                    list_overlap[group] += 1
            if largest > 18 and population == 'birth' and f'coverage {largest}' not in examples:
                examples[f'coverage {largest}'] = {unit: key, **code.witness(word)}
            if not (strict or largest == 2 or ordinal in sample):
                continue

            feature = score(cycles, sign, order_rng, algebra_control=ordinal in sample)
            assert feature['most at a cross pair'] == largest
            assert (sign, feature) == score_cycle_multiset(profile)
            record(take[group], feature)
            if ordinal in sample:
                record(sampled[group], feature)
            if sign == 0 and not feature['orientable'] and population == 'birth':
                strict_group = 'strict' if strict else 'nonstrict'
                readers = code.reader_partition(word)
                label = f'even non-orientable {strict_group} with reader partition={readers is not None}'
                older = examples.get(label)
                if older is None or word.bit_count() < len(older['selected failing pairs']):
                    orientations = brute_balance(cycle_incidences(cycles), len(cycles)) if len(cycles) <= 16 else None
                    if orientations is not None:
                        assert orientations == (feature['orientable'], feature['weak even condition'])
                    examples[label] = {unit: key, **code.witness(word), 'reader groups': readers,
                                       'all cyclic reversals tested': orientations is not None, **feature}

        mass = 1 << dim
        odd_attainable = any(code.sign(v) for v in code.basis)
        target = {0: mass // 2 - 1, 1: mass // 2} if odd_attainable else {0: mass - 1, 1: 0}
        assert all(sign_totals[sign] == target[sign] for sign in (0, 1))
        exact = defaultdict(tally)
        for group, profile_counts in cycles_by_group.items():
            sign = int(group.endswith(', odd'))
            for profile, multiplicity in profile_counts.items():
                baseline, feature = score_cycle_multiset(profile)
                assert baseline == sign
                record(exact[group], feature, multiplicity)
                if feature['exactly two']:
                    part_counts[group][str(feature['separated components'])] += multiplicity
            assert exact[group]['most at a cross pair'] == coverage_by_group[group]
        compare_exact(exact, archived_row['tallies'], population, key)
        for name in groups:
            for group, row in exact.items():
                totals[name][group] += row['choices']
                merge(complete[name][group], row)
                if group in take:
                    merge(examined[name][group], take[group])
                for parts, number in part_counts[group].items():
                    separated_parts[name][f'{group}, {parts} component(s)'] += number
            totals[name]['checked structural choices'] += sum(v['choices'] for v in take.values())
            totals[name]['drawn for structural sample'] += len(sample)
            totals[name]['cycle multisets by code and category'] += sum(map(len, cycles_by_group.values()))
        rows[population][key] = {'no odd reader split': no_split, 'dimension': dim, 'exact': exact,
                                 'checked in two independently drawn orders': take, 'sample': sampled,
                                 'separated components': part_counts}
        time_by_dimension[str(dim)] += monotonic() - started

    if not probe:
        assert {pop: totals[pop]['codes'] for pop in archive} == {pop: len(r) for pop, r in archive.items()}
    list_account = {}
    if not probe:
        archived_counts = Counter()
        for cohort in archive.values():
            for row in cohort.values():
                for name, fields in row['tallies'].items():
                    archived_counts[name] += fields['choices']
                if row.get('fewest strict readers') is not None:
                    assert row['fewest strict readers'] <= LIST_LIMIT
                    assert row['fewest listing complete'] and all(sign == 0 for sign, _ in row['sizes at the cap'])
        visits = sum(archived_counts.values())
        fewer = archived_counts['fewest strict']
        assert visits == json.loads((STUDY / 'gates.json').read_text())[
            'theorem holds on every choice of the populations (failures, choices)'][1]
        list_account = {
            'archived visits by category': archived_counts,
            'archived visits in gate': visits,
            'fewest strict visits also in the minimal strict odd list': fewer,
            'small choices also in a minimal strict list': list_overlap,
            'distinct recorded nonempty choices with code identity retained': visits - fewer - sum(list_overlap.values()),
        }

    return {'population counts': totals, 'exact fields by population': complete,
            'tallies checked in two independently drawn orders': examined, 'separated component counts': separated_parts,
            'minimal strict choices by size': minimal_strict_sizes, 'archived gate population accounting': list_account,
            'per-code rows': rows, 'witnesses': examples, 'cycle multiset cache': score_cycle_multiset.cache_info()._asdict(),
            'seconds by code dimension': {k: round(v, 3) for k, v in time_by_dimension.items()}}


def sample_closed_patterns(probe):
    pattern_rng = random.Random(PATTERN_SEED)
    reference_rng = random.Random(SAMPLE_SEED)
    scores = tally()
    sign_mass = Counter()
    strata = Counter()
    attempts = []
    for trial in range(30 if probe else PATTERN_ATTEMPTS):
        n = pattern_rng.randint(4, 7)
        meetings = [(pattern_rng.randrange(k), k) for k in range(1, n)]
        meetings.extend(sorted(pattern_rng.sample(range(n), 2)) for _ in range(pattern_rng.randint(n, 2 * n)))
        supports = tuple(tuple(i for i, pair in enumerate(meetings) if k in pair) for k in range(n))
        if min(map(len, supports)) < 2:
            strata['rejected for a knot with fewer than two distinctions'] += 1
            continue
        code = Code(supports)
        dimension = len(code.basis)
        if dimension > PATTERN_LIMIT:
            strata['rejected for more than 12 free choices'] += 1
            continue
        strata['accepted patterns'] += 1
        if dimension == 0:
            strata['accepted patterns with no nonempty commuting choices'] += 1
        count = 0
        advance = 0
        for ordinal, word in words(code.basis):
            sign = code.sign(word)
            feature = score(code.cycle_word(word), sign, reference_rng, algebra_control=ordinal == 1)
            record(scores, feature)
            sign_mass[category(code.strict(word), sign)] += 1
            count += 1
            # The archived generator used the same stream for both order checks.
            # Each check drew once per cycle and once per distinct cross pair.
            advance += 2 * (word.bit_count() + sum(bool(mask & word) for mask in code.coverage_masks))
        for _ in range(advance):
            pattern_rng.random()
        attempts.append([trial, n, len(meetings), dimension, count, advance])
    assert sum(sign_mass.values()) == scores['choices']
    if not probe:
        reference = json.loads((STUDY / 'summary.json').read_text())['random patterns (theorem gate)']
        assert scores == reference, (scores, reference)
    return {'draws': strata, 'choices by sign and strictness': sign_mass, 'feature tallies': scores,
            'accepted draws (trial, knots, distinctions, free choices, nonempty choices, order draws)': attempts}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--probe', action='store_true', help='Run a short scaling check without writing files.')
    args = parser.parse_args()
    started = monotonic()
    counts = tally_codes(args.probe)
    print(json.dumps(counts['population counts']), flush=True)
    print(json.dumps(counts['seconds by code dimension']), flush=True)
    random_started = monotonic()
    random_counts = sample_closed_patterns(args.probe)
    print(json.dumps(random_counts['draws']), flush=True)
    print(json.dumps(random_counts['feature tallies']), flush=True)
    runtime = {'seconds': round(monotonic() - started, 3), 'seconds for random patterns': round(monotonic() - random_started, 3),
               'peak KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    print(json.dumps(runtime), flush=True)
    if not args.probe:
        output = {
            'inputs': ['../../READER-SPLIT-20261127-001/referee-R1/rebuilt_inputs.jsonl',
                       '../../READER-SPLIT-20261127-001/referee-R1/split_rows.jsonl'],
            'weighting': 'One vote per labelled, nonempty commuting choice within each code, with codes counted per census start or type as named. A random pattern contributes all its nonempty choices.',
            'scope': 'All codes with at most 14 free choices. Each category retains the exact mass of labelled words for each multiset of cycles canonicalized by rotation and reversal. Structural measurements and a baseline order are evaluated by multiset and multiplied by its mass. Two independently drawn orders are checked for all strict and twice-covered words and a simple sample of up to 64 words per code. All random-pattern words have full structural measurements and two independently drawn orders.',
            'sample seed': SAMPLE_SEED, 'random pattern seed': PATTERN_SEED, 'random pattern attempts': PATTERN_ATTEMPTS,
            'scope totals and rows': counts, 'random patterns': random_counts, 'resources': runtime,
        }
        (HERE / 'small_results.json').write_text(json.dumps(output, indent=1) + '\n')


if __name__ == '__main__':
    main()
