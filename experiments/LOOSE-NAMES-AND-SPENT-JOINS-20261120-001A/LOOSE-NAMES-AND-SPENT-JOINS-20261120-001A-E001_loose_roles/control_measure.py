"""Independent binary contraction and native replay of the frozen target."""

from collections import Counter
from fractions import Fraction
import gzip
from itertools import combinations
import json
from math import comb, gcd, lcm
from pathlib import Path
import sys

from control_role_rows import controls


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
OUTPUT = ROOT / 'artifacts' / TICKET / HERE.name
PRIOR = 'STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B'
PRIOR_FAMILY = f'{PRIOR}-E001_pair_growth'
WIDE = 'CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001C'
WIDE_FAMILY = f'{WIDE}-E001_wider_meetings'
WEIGHTS = ('uniform', 'inherited')
sys.path.insert(0, str(ROOT / 'experiments' / PRIOR / PRIOR_FAMILY))
from explosive_stages import stages, width
from explosive_verify import BinaryReduction, independent_parity, literal_cuts
from census_compare import name_permutation
from census_stages import mask_of, reduced
from explosive_symmetry import rows_move


def read(path):
    with (gzip.open(path, 'rt') if path.suffix == '.gz' else path.open()) as stream:
        return json.load(stream)


def save(path, data):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(data, sort_keys=True) + '\n').encode()
    path.write_bytes(gzip.compress(encoded, mtime=0) if path.suffix == '.gz' else encoded)


def freeze(data):
    return tuple(map(freeze, data)) if isinstance(data, list) else data


def binary_table(stage, weighting):
    n = stage['width']
    rows = freeze(stage['rows'])
    if max(map(len, rows)) > 18:
        raise ValueError('independent factor arity ceiling')
    plan = BinaryReduction(rows, stage['limits'], weighting)
    work = (1 + comb(n, 2)) * sum(len(inputs) * (1 << len(inputs[0][1])) for _, _, inputs in plan.operations)
    if work > 300_000_000:
        raise ValueError(('independent binary calculation ceiling', n, work))
    scale = plan.contract()
    counts = {}
    for pair in combinations(range(n), 2):
        difference = scale - plan.contract(pair)
        assert 0 <= difference <= 2 * scale and difference % 2 == 0
        counts[pair] = difference // 2
    return scale, counts, {'cell_bound': work, 'peak_cells': plan.largest}


def parity_table(stage):
    patterns, total = independent_parity(stage['rows'])
    counts = {(i, j): 0 if patterns[i] == patterns[j] else total // 2
              for i, j in combinations(range(len(patterns)), 2)}
    return total, counts


def record(stage, law, weighting, total, counts, cost):
    n = stage['width']
    assert list(counts) == list(combinations(range(n), 2))
    result = controls(n, total, counts.values(), stage['rows'], law)
    return {'weighting': weighting, 'total': total, 'disagreement_counts': tuple(counts.values()),
            'reduced_rate_denominator': lcm(*(total // gcd(v, total) for v in counts.values())),
            'screen': result, 'cost': cost}


def measure_independent(stage, law):
    if law == 'parity':
        total, counts = parity_table(stage)
        control = record(stage, law, 'uniform', total, counts, {'method': 'binary nullspace'})
        return {'uniform': control, 'inherited': {**control, 'weighting': 'inherited'}}
    data = {}
    for weight in WEIGHTS:
        total, counts, cost = binary_table(stage, weight)
        data[weight] = record(stage, law, weight, total, counts, cost | {'method': 'binary distinction contraction'})
    return data


def fractions(measurement):
    return tuple(Fraction(i, measurement['total']) for i in measurement['disagreement_counts'])


def target():
    selection = read(OUTPUT / 'selection.json')
    source = freeze(selection['source'])
    reference = freeze(selection['physical_stage'])
    replay = stages(source, 'nae')
    stage = replay['stages'][selection['age'] - 1]
    assert stage['rows'] == reference and stage['width'] == selection['reached_name_count']
    assert tuple(stage['limits'][:-1]) == freeze(selection['holder_cut_limits'])
    assert tuple(stage['profile']) == tuple(sorted(freeze(selection['reference_named_roster'])))
    weights = measure_independent(stage, 'nae')
    uniform = weights['uniform']
    assert uniform['total'] == selection['uniform_word_count']
    assert uniform['disagreement_counts'] == freeze(selection['uniform_disagreements'])
    assert uniform['screen']['historical_false'] == selection['previous_candidates']['extra_spent_indices']
    assert all(weights[w]['screen']['actual_loose'] == selection['actual_loose'] for w in WEIGHTS)
    deltas = tuple(abs(a - b) for a, b in zip(*(fractions(weights[w]) for w in WEIGHTS), strict=True))
    original = {'rows': source, 'width': width(source), 'limits': (len(source),)}
    old_total, old_pairs, _ = binary_table(original, 'uniform')
    before_width = width(source if selection['age'] == 1 else replay['stages'][selection['age'] - 2]['rows'])
    if selection['age'] > 1:
        old_total, old_pairs, _ = binary_table(replay['stages'][selection['age'] - 2], 'inherited')
    current_rates = dict(zip(combinations(range(stage['width']), 2), fractions(weights['inherited']), strict=True))
    assert all(current_rates[pair] == Fraction(d, old_total) for pair, d in old_pairs.items())
    assert len(old_pairs) == comb(before_width, 2)
    result = {'selected_key': selection['selected_key'], 'source': source, 'history': replay,
              'named_pair_order': tuple(combinations(range(stage['width']), 2)), 'weights': weights,
              'weight_conflict': {'different_entries': sum(d != 0 for d in deltas), 'total_entries': len(deltas),
                                  'maximum_change': str(max(deltas)), 'old_rates_preserved': len(old_pairs)}}
    return result


def prior_28():
    reference = read(ROOT / 'artifacts' / PRIOR / PRIOR_FAMILY / 'target.json')
    replay = stages(((0, 1, 2, 3),), 'nae')
    stage = replay['stages'][1]
    assert stage['rows'] == freeze(reference['observed_holders']) and stage['width'] == 28
    assert tuple(stage['profile']) == tuple(sorted(freeze(reference['physical_next']['parent_supports_and_fresh'])))
    weights = measure_independent(stage, 'nae')
    for w in WEIGHTS:
        assert fractions(weights[w]) == tuple(map(Fraction, reference[w]['fractions']))
    return {'history': replay, 'independent_pair_entries_per_weight': 378, 'weights': weights}


def parity_counterexample():
    old = read(ROOT / 'artifacts' / WIDE / WIDE_FAMILY / 'census_summary.json')
    paired = {}
    for case in ('different_next_birth_counts', 'same_states_different_births'):
        witness = old['parity']['minima'][case]
        sides = []
        for arm in witness['arms']:
            replay = stages(freeze(arm['source_rows']), 'parity')
            stage = replay['stages'][arm['age'] - 1]
            transform = arm['reached_name_transport']
            renamed = rows_move(stage['rows'], transform)
            assert renamed == freeze(arm['stage_rows'])
            assert stage['next_count'] == arm['next_birth_count']
            payload = dict(stage, rows=renamed)
            reading = measure_independent(payload, 'parity')
            basis = reduced(name_permutation(mask_of(row), transform) for row in stage['rows'])
            sides.append({'source': arm['source_rows'], 'age': stage['age'], 'common_rows': renamed,
                          'current_to_common': transform, 'basis': basis, 'weights': reading,
                          'next_roster': tuple((rows_move(p, transform), f) for p, f in stage['profile']),
                          'next_count': stage['next_count']})
        a, b = sides
        assert all(fractions(a['weights'][w]) == fractions(b['weights'][w]) for w in WEIGHTS)
        assert a['next_count'] != b['next_count']
        assert (a['basis'] == b['basis']) == (case == 'same_states_different_births')
        paired[case] = sides
    return paired


def main():
    target_read = target()
    save(OUTPUT / 'control_target.json', target_read)
    for w in WEIGHTS:
        data = target_read['weights'][w]
        print('selected', w, data['total'], data['screen']['historical_false'],
              data['screen']['surviving_false'], data['cost'], flush=True)
    ordinary = ((0, 1, 2),)
    data = {'prior_28': prior_28(), 'parity': parity_counterexample(),
            'literal_ordinary': {law: tuple(literal_cuts(ordinary, law)) for law in ('nae', 'parity')}}
    save(OUTPUT / 'control_references.json', data)


if __name__ == '__main__':
    main()
