"""Independent target rates, physical next roster and both law controls."""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations

from control_draws import OUT, ROOT, PREVIOUS, PREVIOUS_FAMILY, all_sign_screen
from control_measure import WEIGHTS, binary_table, freeze, fractions, measure_independent
from control_measure import parity_counterexample, parity_table, read, save, stages, target as prior_positive, width
from explosive_rates import nae_rates
from explosive_symmetry import inverse, profile_move, table_moves
from census_replay import check_source
from census_weighted import canonical_weighted


def named_stabilizer(stage, total, counts, loose):
    key = canonical_weighted(stage['width'], total, counts)
    generators, order = table_moves(key.key)
    assert order == key.automorphisms
    perm = inverse(key.order)
    profile = profile_move(stage['profile'], perm)
    named_loose = {perm[x] for x in loose}
    return {'group_order': order, 'generators': len(generators),
            'fixed_profile': all(profile_move(profile, g) == profile for g in generators),
            'fixed_loose_set': all({g[x] for x in named_loose} == named_loose for g in generators)}


def measure_target():
    reference = read(OUT / 'reference.json')
    age = reference['age']
    founder = freeze(reference['source'])
    size = width(founder)
    check_source(founder, 'nae', size)
    physical = stages(founder, 'nae')
    stage = physical['stages'][age - 1]
    assert (stage['width'], stage['rows'], stage['limits']) == (reference['width'], freeze(reference['stage']), freeze(reference['limits']))
    assert (stage['next_status'], stage['next_count'], freeze(stage['profile'])) == (
        reference['next_status'], reference['next_count'], freeze(reference['profile']))
    tables = measure_independent(stage, 'nae')
    stabilizers = {}
    for weighting, measurement in tables.items():
        actual = fractions(measurement)
        sealed = OUT / f'target_{weighting}.json'
        assert sha256(sealed.read_bytes()).hexdigest() == reference['table_sha256'][weighting]
        assert actual == tuple(map(Fraction, read(sealed)))
        holder_total, holder_counts = nae_rates(stage, weighting)
        assert actual == tuple(Fraction(c, holder_total) for c in holder_counts.values())
        loose = measurement['screen']['actual_loose']
        assert loose == reference['loose']
        measurement['all_sign'] = all_sign_screen(stage, measurement)
        stabilizers[weighting] = named_stabilizer(stage, holder_total, holder_counts, loose)
    assert tables['inherited']['all_sign']['remaining_spent'] == reference['survived_spent_indices']
    preceding = {'width': size, 'rows': founder, 'limits': (len(founder),)} if age == 1 else physical['stages'][age - 2]
    old_table = binary_table(preceding, 'uniform' if age == 1 else 'inherited')
    before = {p: Fraction(c, old_table[0]) for p, c in old_table[1].items()}
    indexed = tuple(combinations(range(stage['width']), 2))
    later = {weight: dict(zip(indexed, fractions(tables[weight]), strict=True)) for weight in WEIGHTS}
    assert all(before[p] == later['inherited'][p] for p in before)
    delta = {p: abs(later['uniform'][p] - later['inherited'][p]) for p in indexed}
    change = {'changed_pairs': sum(v > 0 for v in delta.values()), 'total_pairs': len(delta),
              'maximum_change': str(max(delta.values())),
              'maximum_change_pairs': [p for p in indexed if delta[p] == max(delta.values())],
              'preceding_pairs': len(before), 'inherited_preserved_pairs': len(before),
              'uniform_changes_to_preceding_pairs': sum(before[p] != later['uniform'][p] for p in before)}

    check_source(founder, 'parity', size)
    parity = stages(founder, 'parity')
    named_parity = parity['stages'][age - 1]
    parity_tables = measure_independent(named_parity, 'parity')
    from explosive_rates import parity_rates as holder_parity
    _, _, holder_total, holder_counts = holder_parity(named_parity)
    assert fractions(parity_tables['uniform']) == tuple(Fraction(c, holder_total) for c in holder_counts.values())
    law_control = {'history': parity, 'weights': parity_tables, 'same_named_holders': stage['rows'] == named_parity['rows'],
                   'same_next_named_roster': stage['profile'] == named_parity['profile'],
                   'allowed_words': parity_table(named_parity)[0]}
    if named_parity['width'] == stage['width']:
        law_control['named_pairs_different_from_nae'] = {
            w: sum(a != b for a, b in zip(fractions(tables[w]), fractions(parity_tables[w]), strict=True)) for w in WEIGHTS}

    return {'draw': reference['draw'], 'age': age, 'reference_table_sha256': reference['table_sha256'],
            'named_source': founder, 'native_history': physical, 'pairs': indexed, 'weights': tables,
            'stabilizers': stabilizers, 'weight_change': change, 'lawful_parity_from_same_founder': law_control}


def reference_controls():
    prior = prior_positive()
    archive = ROOT / 'artifacts' / PREVIOUS / PREVIOUS_FAMILY
    for weighting, table in prior['weights'].items():
        other = tuple(map(Fraction, read(archive / f'{weighting}_rates.json')))
        assert other == fractions(table)
    return {'prior_29': prior, 'parity_obstructions': parity_counterexample()}


def main():
    result = measure_target()
    save(OUT / 'control_target.json', result)
    save(OUT / 'control_references.json', reference_controls())
    p = result['lawful_parity_from_same_founder']
    print(result['draw'], result['age'], result['weight_change'], result['stabilizers'],
          p['same_named_holders'], p['same_next_named_roster'], p['allowed_words'], flush=True)


if __name__ == '__main__':
    main()
