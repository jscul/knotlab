"""Check complete independent readings, sample naming and exterior bounds."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations

from control_measure import OUTPUT, WEIGHTS, fractions, read, save
from explosive_rates import nae_rates
from census_rate_tables import parity_table as archived_parity_table
from model import spanned


def verify_selected():
    independent = read(OUTPUT / 'control_target.json')
    observed = {}
    for weighting in WEIGHTS:
        other = tuple(map(Fraction, read(OUTPUT / f'{weighting}_rates.json')))
        primary = fractions(independent['weights'][weighting])
        assert primary == other
        observed[weighting] = len(primary)
    return observed


def verify_named_sample(physical, law):
    age = Counter()
    for target_age in (1, 2):
        trial = next(d for d in physical['draws'] if len(d['stages']) >= target_age)
        stage = trial['stages'][target_age - 1]
        n = stage['width']
        for weighting in WEIGHTS:
            primary = fractions(stage['weights'][weighting])
            if law == 'parity':
                _, basis = archived_parity_table(stage['rows'])
                other = tuple(Fraction(0) if spanned((1 << i) ^ (1 << j), basis) else Fraction(1, 2)
                              for i, j in combinations(range(n), 2))
            else:
                total, counts = nae_rates(stage, weighting)
                other = tuple(Fraction(d, total) for d in counts.values())
            assert primary == other
            age[f'{target_age}:{weighting}'] = len(primary)
    return age


def verify_exterior_redundancy(screen):
    baseline = 0
    failures = 0
    for p in screen['predictions']:
        rejected = p['rejections']
        if 'minimum_and_arity' in rejected or 'historical_screen' in rejected or len(p['support']) < 4:
            continue
        baseline += 1
        if 'companion_triple_exterior' in rejected:
            failures += 1
            assert 'companion_pair_exterior' in rejected or 'absolute_exterior' in rejected
    return baseline, failures


def main():
    selected = verify_selected()
    panels = read(OUTPUT / 'control_panels.json.gz')
    named_samples = {}
    exterior = Counter()
    agreement = Counter()
    for law, populations in panels.items():
        named_samples[law] = {name: verify_named_sample(v, law) for name, v in populations.items()}
        for v in populations.values():
            for item in v['draws']:
                for stage in item['stages']:
                    for payload in stage['weights'].values():
                        if 'unread' in payload:
                            continue
                        a, b = verify_exterior_redundancy(payload['screen'])
                        exterior['tested_companion_sets'] += a
                        exterior['four_name_rejections'] += b
                        for candidate in payload['screen']['predictions']:
                            if candidate['name'] in payload['screen']['historical_false']:
                                gates = candidate['rejections']
                                agree = ('unary_binary_input_row' in gates) == ('companion_pair_exterior' in gates)
                                agreement['tested'] += 1
                                agreement['agree'] += agree
    source_hashes = {name: sha256((OUTPUT / name).read_bytes()).hexdigest() for name in
                     ('selection.json', 'control_target.json', 'control_references.json', 'control_panels.json.gz',
                      'control_panel_summary.json', 'uniform_rates.json', 'inherited_rates.json')}
    data = {'named_target_pairs': selected, 'named_draw_pair_replays': named_samples,
            'companion_four_redundancy': exterior, 'input_row_and_pair_exterior_agreement': agreement,
            'sha256': source_hashes}
    save(OUTPUT / 'control_verification.json', data)
    print(selected, named_samples, exterior, flush=True)


if __name__ == '__main__':
    main()
