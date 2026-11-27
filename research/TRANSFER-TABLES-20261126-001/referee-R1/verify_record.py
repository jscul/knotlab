"""Compare the independent, already produced evidence to the frozen record and original law."""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys
from time import perf_counter

from read_tables import amplitudes, bitset, product_expectations


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
LAW = ROOT / 'experiments/RING-TO-END-20261119-001/RING-TO-END-20261119-001-E001_transfer'
sys.path.insert(0, str(LAW))
import transfer


def word_label(ones):
    return ''.join('1' if i in ones else '0' for i in range(9))


def original_round(mode, probabilities, listed, limit):
    founders = [set(s) for s in ((), (0, 1), (0, 2), (1, 2))][:limit]
    count = 0
    reached = Counter()
    for old in founders:
        plan = transfer.round_plan(((0, 1, 2),), old)
        births = transfer.realize(plan, mode)['births']
        options = [transfer.lift_options(b, old, mode) for b in births]
        outcomes = list(product(*options))
        for choices in outcomes:
            count += 1
            selected = iter(choices)
            step = transfer.realize(plan, mode, pick=lambda *_: next(selected))
            assert [list(s) for s in step['stars']] == listed
            reached[word_label(step['occupied'])] += Fraction(1, 4 * len(outcomes))
    expected = {word: Fraction(p) for word, p in probabilities.items()
                if {i for i, b in enumerate(word[:3]) if b == '1'} in founders}
    assert reached == expected
    return count


def main(pilot):
    begun = perf_counter()
    record = json.loads((HERE / 'read_tables.json').read_text())
    with gzip.open(STUDY / 'tables_out.jsonl.gz', 'rt') as stream:
        published = [json.loads(line) for line in stream]
    hashes = {}
    for line in (STUDY / 'frozen.sha256').read_text().splitlines():
        expected, name = line.split()
        actual = sha256((STUDY / name).read_bytes()).hexdigest()
        assert actual == expected
        hashes[name] = actual
    weights = {r['weighting']: r for r in record['records']}
    replay = {}
    for mode, key in [('minimum', 'minimum start'), ('exact_two', 'pair start'), ('any_pair', 'pair start')]:
        replay[mode] = original_round(mode, weights[key]['words_in_distinction_order'], record['listed_laws'],
                                      1 if pilot else 4)
    compared = undefined = 0
    coherent = json.loads((HERE / 'unrestricted.json').read_text())
    coherent_arms = ['minimum_start', 'minimum_once', 'pair_start', 'pair_once', 'pair_finish']
    key = lambda a, b: tuple(sorted((tuple(a), tuple(b))))
    bounds = {key(r['A'], r['B']): r['checks'] for r in coherent['splits']}
    for row_set, old, arm in zip(record['records'][:5], published[:5], coherent_arms, strict=True):
        denominator = row_set['weight_denominator']
        lookup = {key(r['A'], r['B']): r for r in old['rows']}
        for new in row_set['rows'][:1 if pilot else None]:
            holding = key(new['small_reader'], new['other_reader'])
            row = lookup[holding]
            bound = bounds[holding][arm]
            assert round(bound['partial_transpose_negativity'], 6) == row['coherent']['negativity']
            assert round(bound['witness_CHSH'], 4) == row['coherent']['CHSH, any reads']
            assert new['unread'] == row['unread']
            num = new['pauli_numerators']['original_pauli_convention']
            assert round(num / denominator, 4) == row['coherent']["CHSH, the model's reads (Pauli products)"]
            value = new['value_numerator_distinct']
            if value is None:
                assert row['value reads, largest CHSH'] == 0
                undefined += 1
            else:
                assert round(value / denominator, 4) == row['value reads, largest CHSH']
            compared += 1
    supplied = json.loads((HERE / 'reweight.json').read_text())
    dist = {int(w[::-1], 2): Fraction(c, supplied['total_count']) for w, c in supplied['positive_integer_counts'].items()}
    assert set(supplied['positive_integer_counts']) == set(weights['pair start']['words_in_distinction_order'])
    lookup = product_expectations(amplitudes(dist, 9))
    reads = [(bitset([3,4,7,8]), 0), (bitset([3,4]), 1 << 7),
             (bitset([7,8]), 1 << 3), (0, bitset([3,7]))]
    numerators = [int(lookup[f,z]) for f,z in reads]
    assert numerators == supplied['E00_E01_E10_E11_numerators_over_total_count']
    print(json.dumps({'pilot': pilot, 'verified_hashes': hashes, 'source_replay_lifts': replay,
                      'registered_split_rows_compared': compared, 'empty_value_menus_printed_as_zero': undefined,
                      'reweight_numerators': numerators, 'elapsed_seconds': perf_counter() - begun}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    main(parser.parse_args().pilot)
