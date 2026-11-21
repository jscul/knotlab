"""Replay width-ten case tables using literal clauses, covers and growth."""

from collections import Counter
import gzip
import json
from math import factorial

from census_width_ten import OUTPUT, WIDTH
from census_irredundant import exact_projection
from census_verify import canonical_law, indices, to_mask, verify


def direct_reading(packed, all_words):
    allowed = set(indices(packed))
    forbidden = set(all_words) - allowed
    candidates = [s for s in all_words if s.bit_count() >= 3 and exact_projection(WIDTH, packed, s, 'nae')]
    violations = {s: {w for w in forbidden if w & s in (0, s)} for s in candidates}
    counts = Counter(w for words in violations.values() for w in words)
    assert set(counts) == forbidden
    mandatory = {s for s, words in violations.items() if any(counts[w] == 1 for w in words)}
    only_flip = set()
    derivative = [set() for _ in range(WIDTH)]
    for word in forbidden:
        repairs = [i for i in range(WIDTH) if word ^ (1 << i) in allowed]
        only_flip.add(to_mask(repairs))
        for i in repairs:
            derivative[i].add(word)
    sole_holders = [{s for s in candidates if s & (1 << i) and derivative[i] <= violations[s]}
                    for i in range(WIDTH)]
    assert sole_holders and all(derivative)

    def complete(used):
        return set().union(*(violations[s] for s in used)) == forbidden

    return complete(mandatory), complete(only_flip.intersection(candidates)), sole_holders


def direct_diagnostics(rows, expected):
    named = Counter()
    representatives = Counter()
    successful = Counter()
    all_words = range(1 << WIDTH)
    for row in rows:
        mandatory, single_word, sole_holders = direct_reading(int(row['state_words_hex'], 16), all_words)
        successful['mandatory_orbits'] += mandatory
        successful['single_word_orbits'] += single_word
        successful['mandatory_named_states'] += mandatory * row['named_states_in_orbit']
        successful['single_word_named_states'] += single_word * row['named_states_in_orbit']
        for start in row['presentations']:
            holders = [to_mask(s) for s in start['supports']]
            tally = Counter()
            for i, read in enumerate(sole_holders):
                actual = [s for s in holders if s & (1 << i)]
                if len(actual) == 1:
                    assert actual[0] in read
                    tally['loose'] += 1
                    tally['loose_unique'] += len(read) == 1
                    tally['loose_multiple_candidates'] += len(read) > 1
                else:
                    assert len(actual) == 2
                    tally['shared'] += 1
                    tally['shared_passing_sole_holder_test'] += bool(read)
            representatives.update(tally)
            multiplicity = factorial(WIDTH) // start['presentation_automorphisms']
            named.update({k: v * multiplicity for k, v in tally.items()})
    assert representatives == expected['distinctive_reads_over_presentation_representatives']
    assert named == expected['distinctive_reads_over_named_presentations']
    for key, value in successful.items():
        assert value == expected['recovery'][key]
    return {'certificate_successes': successful, 'role_reads_on_representatives': representatives,
            'role_reads_on_named_presentations': named}


def main():
    with gzip.open(OUTPUT / 'census_cases.json.gz', 'rt') as record:
        cases = json.load(record)
    expected = json.loads((OUTPUT / 'census_diagnostics.json').read_text())[str(WIDTH)]
    receipts = {'width': WIDTH, 'replay': {}, 'knotlab_full_projected_relations': {}}
    for law, rows in cases.items():
        receipts['replay'][law] = verify(WIDTH, law, rows)
        receipts['knotlab_full_projected_relations'][law] = canonical_law(WIDTH, law)
        print(law, receipts['replay'][law], flush=True)
    receipts['literal_not_all_equal_diagnostics'] = direct_diagnostics(cases['nae'], expected)
    print(receipts['literal_not_all_equal_diagnostics'], flush=True)
    (OUTPUT / 'census_verification.json').write_text(json.dumps(receipts, indent=2) + '\n')


if __name__ == '__main__':
    main()
