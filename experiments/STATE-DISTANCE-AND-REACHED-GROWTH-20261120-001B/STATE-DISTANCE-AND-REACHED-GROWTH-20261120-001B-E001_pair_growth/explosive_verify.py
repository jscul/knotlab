"""Replay exact rates using literal extensions and binary-variable elimination."""

from collections import Counter
from fractions import Fraction
from functools import cache
from itertools import combinations, product
from math import comb, prod

import numpy as np

from explosive_compare import matrix_counts
from explosive_rates import LAWS, WEIGHTS, compact, nae_rates, parity_rates
from explosive_stages import read, stages, width, write
from explosive_symmetry import inverse, table_graph_data
from census_rate_tables import as_tuple


def permitted(word, row_mask, law):
    part = word & row_mask
    return part.bit_count() % 2 == 0 if law == 'parity' else part not in (0, row_mask)


def mask(row):
    return sum(1 << x for x in row)


def literal_cuts(source, law):
    physical = stages(source, law)
    n = width(source)
    original = [s for s in range(1 << n) if all(permitted(s, mask(r), law) for r in source)]
    masses = dict.fromkeys(original, Fraction(1, len(original)))
    preceding_width = n
    preceding_rows = len(source)
    for cut in physical['stages']:
        n = cut['width']
        if n > 16:
            break
        added = [mask(r) for r in cut['rows'][preceding_rows:]]
        current = {}
        for before, weight in masses.items():
            words = [(left << preceding_width) | before for left in range(1 << (n - preceding_width))
                     if all(permitted((left << preceding_width) | before, r, law) for r in added)]
            assert words
            m = weight / len(words)
            for word in words:
                current[word] = m
        assert sum(current.values()) == 1
        for weighting in WEIGHTS:
            if law == 'parity':
                _, _, total, counts = parity_rates(cut)
            else:
                total, counts = nae_rates(cut, weighting)
            for (i, j), count in counts.items():
                disagree = (w for w in current if ((w >> i) ^ (w >> j)) & 1)
                actual = sum(1 for _ in disagree) / Fraction(len(current)) if weighting == 'uniform' else sum(current[w] for w in disagree)
                assert actual == Fraction(count, total), (source, law, cut['age'], weighting, (i, j))
        yield (cut['age'], n, len(current))
        masses = current
        preceding_width, preceding_rows = n, len(cut['rows'])


def direct_holders(rows, limits, weighting):
    for index, row in enumerate(rows):
        old = next((cut for cut in reversed(limits[:-1]) if index >= cut), None)
        earlier = set().union(*rows[:old]) if old is not None else set()
        inputs = tuple(k for k, x in enumerate(row) if x in earlier)
        fresh_count = len(row) - len(inputs)
        a = 1 << fresh_count
        factor = np.zeros((2,) * len(row), dtype=object)
        for settings in np.ndindex(factor.shape):
            if min(settings) == max(settings):
                continue
            if old is None or weighting == 'uniform':
                factor[settings] = 1
            else:
                # Count the actual allowed extension set directly on the holder.
                values = [settings[i] for i in inputs]
                allowed = sum(1 for output in product((0, 1), repeat=fresh_count)
                              if 0 in values + list(output) and 1 in values + list(output))
                factor[settings] = (a * (a - 1)) // allowed
                assert factor[settings] * allowed == a * (a - 1)
        yield tuple(row), factor


class BinaryReduction:
    def __init__(self, rows, limits, weighting):
        base = [(scope, np.array((1, 1), dtype=object)) for scope in ((i,) for i in range(width(rows)))]
        base.extend(direct_holders(rows, limits, weighting))
        self.data = [matrix for _, matrix in base]
        pending = {i: scope for i, (scope, _) in enumerate(base)}
        self.operations = []
        remaining = set(range(width(rows)))
        self.largest = 0
        while remaining:
            containers = {name: [i for i, scope in pending.items() if name in scope] for name in remaining}
            scopes = {name: tuple(sorted(set().union(*(pending[i] for i in group)))) for name, group in containers.items()}
            chosen = min(remaining, key=lambda name: (len(scopes[name]), name))
            remaining.remove(chosen)
            union, affected = scopes[chosen], containers[chosen]
            peak = 1 << len(union)
            self.largest = max(self.largest, peak)
            if peak > 1 << 18:
                raise ValueError(('independent binary reduction gate', peak))
            shaped = [(i, tuple(2 if x in pending[i] else 1 for x in union)) for i in affected]
            for i in affected:
                del pending[i]
            target = len(self.data)
            self.data.append(None)
            pending[target] = tuple(i for i in union if i != chosen)
            self.operations.append((target, union.index(chosen), shaped))
        assert all(not scope for scope in pending.values())
        self.terms = tuple(pending)

    def contract(self, marked=(), pinned=()):
        values = self.data.copy()
        for x in marked:
            values[x] = np.array((1, -1), dtype=object)
        for x, bit in pinned:
            values[x] = np.array((1 - bit, bit), dtype=object)
        for target, axis, shaped in self.operations:
            joint = prod(values[i].reshape(shape) for i, shape in shaped)
            values[target] = joint.sum(axis=axis)
        return prod(int(values[i]) for i in self.terms)

    def rate(self, pair, denominator):
        return Fraction(denominator - self.contract(pair), 2 * denominator)


def independent_parity(rows):
    n = width(rows)
    equations = [mask(row) for row in rows]
    pivot = []
    for j in range(n):
        row = next((equations[i] for i in range(len(pivot), len(equations)) if equations[i] & (1 << j)), 0)
        if row:
            equations.remove(row)
            equations.insert(len(pivot), row)
            for i in range(len(equations)):
                if i != len(pivot) and equations[i] & (1 << j):
                    equations[i] ^= row
            pivot.append(j)
    signatures = [0] * n
    for j in set(range(n)) - set(pivot):
        signatures[j] |= 1 << j
        for i, k in enumerate(pivot):
            if equations[i] & (1 << j):
                signatures[k] |= 1 << j
    for row in rows:
        witness = 0
        for x in row:
            witness ^= signatures[x]
        assert witness == 0
    return signatures, 1 << (n - len(pivot))


def verify_key(stage, result):
    key = as_tuple(result['key'])
    blocks, between = table_graph_data(key)
    same = [signature[1:] for signature in key[1]]
    group = {x: i for i, block in enumerate(blocks) for x in block}
    raw_to_canonical = inverse(result['order'])
    total = result['total']
    for (a, b), count in matrix_counts(stage['width'], result).items():
        i, j = (group[raw_to_canonical[x]] for x in (a, b))
        p, q = same[i] if i == j else between[i][j]
        assert p * total == q * count


def representative_pairs(local, limits):
    source_n = width(local[:limits[0]])
    n = width(local)
    return {(0, 1), (0, n - 1), (n - 2, n - 1), (n // 3, (2 * n) // 3), (source_n - 1, n - 1)} - {(n - 1, n - 1)}


@cache
def local_binary_read(rows, limits, weighting, complete=False):
    plan = BinaryReduction(rows, limits, weighting)
    total = plan.contract()
    queries = combinations(range(width(rows)), 2) if complete else representative_pairs(rows, limits)
    pairs = {choice: plan.rate(choice, total) for choice in queries}
    projections = 0
    if complete and weighting == 'uniform':
        for row in rows:
            for bits in product((0, 1), repeat=len(row)):
                if min(bits) != max(bits):
                    assert plan.contract(pinned=tuple(zip(row, bits, strict=True))) > 0
                    projections += 1
    return total, pairs, plan.largest, projections


def check_nae(items, physical):
    audit = Counter()
    for outcome in items:
        stage = physical[outcome['source_id']]['stages'][outcome['age'] - 1]
        components = tuple(compact(stage))
        for weighting, data in outcome['weights'].items():
            verify_key(stage, data)
            counts = matrix_counts(stage['width'], data)
            denominator = data['total']
            factors = []
            for names, rows, limits in components:
                total, expected, peak, projections = local_binary_read(rows, limits, weighting, complete=True)
                factors.append(total)
                audit[f'{weighting}:largest_binary_cells'] = max(audit[f'{weighting}:largest_binary_cells'], peak)
                for (i, j), value in expected.items():
                    assert value * denominator == counts[names[i], names[j]]
                audit[f'{weighting}:component_pair_replays'] += len(expected)
                audit['allowed_local_projections'] += projections
            if weighting == 'uniform':
                assert prod(factors) == denominator
            for a, b in combinations((names for names, _, _ in components), 2):
                for i, j in product(a, b):
                    assert counts[min(i, j), max(i, j)] * 2 == denominator
                audit[f'{weighting}:cross_component_pairs'] += len(a) * len(b)
            audit[f'{weighting}:stage_tables'] += 1
    return audit


def check_parity(items, physical):
    audit = Counter()
    for outcome in items:
        stage = physical[outcome['source_id']]['stages'][outcome['age'] - 1]
        signatures, words = independent_parity(stage['rows'])
        data = outcome['weights']['uniform']
        assert data == outcome['weights']['inherited'] and data['total'] == words
        verify_key(stage, data)
        for (a, b), d in matrix_counts(stage['width'], data).items():
            assert d == (0 if signatures[a] == signatures[b] else words // 2)
            audit['exact_pair_replays'] += 1
        for row in stage['rows']:
            basis = {}
            for x in row:
                v = signatures[x]
                while v:
                    high = v.bit_length()
                    if high not in basis:
                        basis[high] = v
                        break
                    v ^= basis[high]
            assert len(basis) == len(row) - 1
            audit['full_local_projections'] += 1
        audit['stage_tables'] += 1
    return audit


def check_renamed(physical, rates):
    audit = Counter()
    for law in LAWS:
        seen = set()
        indexed = {(raw['source_id'], raw['age']): raw for raw in rates['reads'][law]}
        for item in physical[law]['samples']['draws']:
            if item['source_id'] in seen:
                continue
            seen.add(item['source_id'])
            for stage in item['stages']:
                raw = indexed[item['source_id'], stage['age']]
                perm = stage['canonical_source_stage_transport']
                old = inverse(perm)
                for weighting in WEIGHTS:
                    data = raw['weights'][weighting]
                    total, counts = data['total'], matrix_counts(stage['width'], data)
                    if law == 'parity':
                        a, t = independent_parity(stage['rows'])
                        pairs = {pair: Fraction(0 if a[pair[0]] == a[pair[1]] else t // 2, t)
                                 for pair in combinations(range(stage['width']), 2)}
                    else:
                        rows = tuple(map(tuple, stage['rows']))
                        _, pairs, _, _ = local_binary_read(rows, tuple(stage['limits']), weighting)
                    for pair, exact in pairs.items():
                        source_pair = tuple(sorted(old[i] for i in pair))
                        assert exact * total == counts[source_pair]
                    audit[law] += len(pairs)
    return audit


def ring_coefficient(loose, age):
    """The ring theorem's lifted intervals with chosen leftover distinctions."""
    size = len(loose)
    return sum(comb(sum(loose[(start + 2 * j) % size] - 2 for j in range(m)), age + 1 - m)
               for start in range(size) for m in range(1, age + 2))


def replay_ring_theorem(physical):
    tested = []
    for law in LAWS:
        for source in physical[law]['sources']:
            if source['family'] != 'ring':
                continue
            rows = source['source_rows']
            meet, loose = source['ring_pattern']
            sizes = Counter(x for row in rows for x in row)
            assert len(rows) == 5 and all(o in (2, 3) for o in loose) and loose.count(3) in (1, 2)
            assert all(sum(sizes[x] == 1 for x in row) == o for row, o in zip(rows, loose, strict=True))
            for i, j in combinations(range(5), 2):
                expected = meet[i] if j - i == 1 else meet[j] if (i, j) == (0, 4) else 0
                assert len(set(rows[i]).intersection(rows[j])) == expected
            first, second = source['stages']
            observed = (len(rows), len(first['births']), first['next_count'], second['next_count'])
            expected = tuple(ring_coefficient(loose, a) for a in range(4))
            assert expected == observed
            tested.append(dict(law=law, source_id=source['id'], initial_meetings=meet, loose=loose,
                               age_zero_through_three=expected, leftover_count=loose.count(3)))
    return tested


def main():
    physical = read('explosive_stages.json.gz')
    results = read('explosive_rates.json.gz')
    panels = {law: {source['id']: source for source in physical[law]['sources']} for law in LAWS}
    tiny = (((0, 1, 2),), ((0, 1, 2), (1, 2, 3)), ((0, 1, 2), (2, 3, 4)))
    literal = {law: [{'source': source, 'cuts': list(literal_cuts(source, law))} for source in tiny] for law in LAWS}
    audit = {'literal': literal,
             'nae': check_nae(results['reads']['nae'], panels['nae']),
             'parity': check_parity(results['reads']['parity'], panels['parity']),
             'renamed_pair_replays': check_renamed(physical, results),
             'ring_theorem_replay': replay_ring_theorem(physical),
             'binary_calculation_distinct_components': local_binary_read.cache_info().currsize}
    print(audit, flush=True)
    write('explosive_verification.json', audit)


if __name__ == '__main__':
    main()
