"""Compare the full signed-family search with exact synthetic controls."""

import argparse
from itertools import combinations, product
import json
from math import comb
import os
from pathlib import Path
from random import Random
import subprocess
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
CARRIER_MASKS = tuple(3 << (2 * i) for i in range(6))
SEED = 17291


def canonical_pairs(pairs):
    return tuple(sorted(tuple(sorted(pair)) for pair in pairs))


def transversal_family(pairs, parity):
    return tuple(sorted(
        tuple(sorted(pair[index] for pair, index in zip(pairs, choices)))
        for choices in product((0, 1), repeat=3)
        if sum(choices) % 2 == parity
    ))


def matchings(literals):
    if not literals:
        yield ()
        return
    first, *rest = literals
    for i, second in enumerate(rest):
        for later in matchings(rest[:i] + rest[i + 1:]):
            yield ((first, second),) + later


def brute_families(clauses):
    """Visit every four-clause set and recover pairs by absence of co-occurrence."""
    bonds = sorted({tuple(sorted(clause)) for clause in clauses})
    expected = {}
    for family in combinations(bonds, 4):
        literals = {literal for clause in family for literal in clause}
        if len(literals) != 6:
            continue
        masks = [literal >> 1 for literal in literals]
        if any(a & b for a, b in combinations(masks, 2)):
            continue
        partners = {literal: literals - {literal} for literal in literals}
        for clause in family:
            for literal in clause:
                partners[literal].difference_update(clause)
        if any(len(candidates) != 1 for candidates in partners.values()):
            continue
        paired = {literal: next(iter(candidates)) for literal, candidates in partners.items()}
        pairs = tuple(sorted((literal, mate) for literal, mate in paired.items() if literal < mate))
        if family == transversal_family(pairs, 0) or family == transversal_family(pairs, 1):
            expected[family] = pairs
    return expected


def upper_relation(family, pairs, both):
    """Enumerate agreement values, keeping the selected value of every sign."""
    literals = sorted({literal for pair in pairs for literal in pair})
    words = set()
    states = []
    for values in product((0, 1), repeat=6):
        selected = {literal: value == (literal & 1) for literal, value in zip(literals, values)}
        if any(all(selected[literal] for literal in clause) for clause in family):
            continue
        upper = tuple(
            all(selected[literal] for literal in pair) if i == both
            else any(selected[literal] for literal in pair)
            for i, pair in enumerate(pairs)
        )
        words.add(sum(value << i for i, value in enumerate(upper)))
        states.append((selected, upper))
    return words, states


def test_upper_roles(family, pairs):
    deletions = 0
    unread = 0
    for both in range(3):
        words, states = upper_relation(family, pairs, both)
        assert words == set(range(7)), (both, words)
        for clause in family:
            remaining = tuple(other for other in family if other != clause)
            restored, _ = upper_relation(remaining, pairs, both)
            assert restored == set(range(8)), (both, clause, restored)
            deletions += 1
            for upper_index in range(3):
                values_by_lower_word = {}
                for selected, upper in states:
                    lower = tuple(selected[literal] for literal in clause)
                    values_by_lower_word.setdefault(lower, set()).add(upper[upper_index])
                assert any(values == {False, True} for values in values_by_lower_word.values())
                unread += 1
    return deletions, unread


def serialize(cases):
    lines = [str(len(cases))]
    for clauses in cases:
        lines.append(str(len(clauses)))
        lines.extend(' '.join(map(str, clause)) for clause in clauses)
    return '\n'.join(lines) + '\n'


def run_fixture(binary, cases):
    output = subprocess.run([binary], input=serialize(cases), check=True, text=True,
                            capture_output=True).stdout
    lines = iter(output.splitlines())
    results = []
    for _ in cases:
        found = {}
        previous = None
        for _ in range(int(next(lines))):
            values = tuple(map(int, next(lines).split()))
            assert len(values) == 18
            family = tuple(values[i:i + 3] for i in range(0, 12, 3))
            pairs = tuple(values[i:i + 2] for i in range(12, 18, 2))
            assert previous is None or previous < family
            assert all(tuple(sorted(clause)) == clause for clause in family)
            assert pairs == canonical_pairs(pairs)
            found[family] = pairs
            previous = family
        results.append(found)
    assert next(lines, None) is None
    return results


def random_clauses(n, count, rng, mandatory=()):
    supports = [sum(1 << i for i in members)
                for size in (2, 3) for members in combinations(range(n), size)]
    by_support = {tuple(literal >> 1 for literal in clause): clause for clause in mandatory}
    while len(by_support) < count:
        raw = tuple(sorted(rng.sample(supports, 3)))
        if any(a & b for a, b in combinations(raw, 2)) or raw in by_support:
            continue
        by_support[raw] = tuple((mask << 1) | rng.randrange(2) for mask in raw)
    return list(by_support.values())


def controls(binary, smoke):
    rng = Random(SEED)
    base_literals = tuple((mask << 1) | (i % 2) for i, mask in enumerate(CARRIER_MASKS))
    planted_pairs = canonical_pairs(zip(base_literals[::2], base_literals[1::2]))
    planted = transversal_family(planted_pairs, 1)

    cases = {
        'empty': (),
        'two_parities_same_pairs': planted + transversal_family(planted_pairs, 0),
        'all_matchings_on_same_carriers': tuple(combinations(base_literals, 3)),
        'shuffled_duplicate_clauses': tuple(reversed(planted)) + (planted[0][::-1],),
        'one_signed_occurrence_changed': (
            (planted[0][0] ^ 1, *planted[0][1:]), *planted[1:]
        ),
        'six_literals_each_twice_but_repeated_clause_intersections': tuple(
            tuple(base_literals[i] for i in indices)
            for indices in ((0, 1, 2), (0, 1, 3), (2, 4, 5), (3, 4, 5))
        ),
    }
    last = base_literals[-1]
    high = ((1 << 63) | (1 << 62)) | (last & 1)
    cases['high_carrier_bits'] = tuple(tuple(high if literal == last else literal for literal in clause)
                                       for clause in planted)
    for name, first, second in (
        ('overlap_between_least_pair_carriers', 0, 1),
        ('overlap_between_other_pair_carriers', 2, 3),
    ):
        changed = list(base_literals)
        common_bit = CARRIER_MASKS[first] & -CARRIER_MASKS[first]
        new_bit = CARRIER_MASKS[second] & -CARRIER_MASKS[second]
        changed[second] = ((common_bit | new_bit) << 1) | (changed[second] & 1)
        cases[name] = transversal_family(tuple(zip(changed[::2], changed[1::2])), 1)
    changed = list(base_literals)
    changed[1] = changed[0] ^ 1
    cases['opposite_signs_on_same_carrier'] = transversal_family(
        tuple(zip(changed[::2], changed[1::2])), 1
    )
    for i, deleted in enumerate(planted):
        cases[f'lower_clause_deleted_{i}'] = tuple(clause for clause in planted if clause != deleted)

    # Both alternatives within a group overlap. A disjoint family chooses one
    # per group. The four parity triples each have 2 ** 3 clause refinements.
    alternatives = tuple(tuple((mask << (3 * i + 1)) | (i % 2) for mask in (3, 5))
                         for i in range(6))
    many = set()
    for choices in product(*alternatives):
        many.update(transversal_family(tuple(zip(choices[::2], choices[1::2])), 0))
    cases['more_than_sixty_patterns'] = tuple(sorted(many))
    assert len(many) == 32

    cases_by_name = list(cases.values())
    oracle_cases = list(cases_by_name)
    signs = (0, 42, 63) if smoke else range(64)
    all_pairings = list(matchings(list(range(6))))
    positive_cases = []
    expected_positive = []
    for matching in all_pairings:
        for sign_mask in signs:
            literals = tuple((mask << 1) | ((sign_mask >> i) & 1)
                             for i, mask in enumerate(CARRIER_MASKS))
            pairs = canonical_pairs(tuple(tuple(literals[i] for i in pair) for pair in matching))
            for parity in (0, 1):
                family = transversal_family(pairs, parity)
                clauses = [list(clause) for clause in family]
                for clause in clauses:
                    rng.shuffle(clause)
                rng.shuffle(clauses)
                positive_cases.append(clauses)
                expected_positive.append({family: pairs})
    random_cases = 8 if smoke else 120
    for trial in range(random_cases):
        mandatory = planted if trial % 2 == 0 else ()
        oracle_cases.append(random_clauses(12 + trial % 5, 12 + trial % 10, rng, mandatory))

    exact = run_fixture(binary, oracle_cases + positive_cases)
    for i, (clauses, actual) in enumerate(zip(oracle_cases, exact)):
        oracle = brute_families(clauses)
        assert actual == oracle, (i, actual, oracle)
    assert exact[len(oracle_cases):] == expected_positive

    known = dict(zip(cases, map(len, exact[:len(cases_by_name)])))
    positive_counts = {
        'two_parities_same_pairs': 2,
        'all_matchings_on_same_carriers': 30,
        'shuffled_duplicate_clauses': 1,
        'high_carrier_bits': 1,
        'more_than_sixty_patterns': 64,
    }
    assert known == {name: positive_counts.get(name, 0) for name in cases}
    deletion_checks, unread_checks = test_upper_roles(planted, planted_pairs)
    return {
        'named_controls': {name: {'clauses': len(cases[name]), 'patterns': count}
                           for name, count in known.items()},
        'exact_oracle_inputs': len(oracle_cases),
        'exact_oracle_four_clause_sets': sum(
            comb(len({tuple(sorted(clause)) for clause in clauses}), 4)
            for clauses in oracle_cases
        ),
        'signed_matching_inputs': len(positive_cases),
        'planted_family_pairings': len(all_pairings),
        'parities_per_pairing': 2,
        'sign_assignments_per_pairing': len(signs),
        'upper_both_roles_checked': 3,
        'single_lower_clause_deletions_restoring_upper_111': deletion_checks,
        'upper_readings_unread_at_each_lower_clause': unread_checks,
        'seed': SEED,
    }


def benchmark(binary, size):
    rng = Random(SEED)
    clauses = random_clauses(19, size, rng)
    sample = subprocess.run([binary, '--counts-only'], input=serialize([clauses]),
                            check=True, text=True, capture_output=True).stdout.split()
    patterns, elapsed, memory = sample
    return {
        'raw_distinctions': 19,
        'clauses': size,
        'patterns': int(patterns),
        'search_seconds': float(elapsed),
        'peak_rss_KiB': int(memory),
        'seed': SEED,
    }


def main():
    args = argparse.ArgumentParser()
    args.add_argument('--smoke', action='store_true')
    args.add_argument('--benchmark', type=int, nargs='*', default=[])
    options = args.parse_args()
    with TemporaryDirectory(prefix='read_pattern_', dir=HERE) as scratch:
        binary = str(Path(scratch) / 'read_pattern_fixture')
        compile_environment = {**os.environ, 'TMPDIR': scratch}
        subprocess.run(['g++', '-pipe', '-O3', '-std=c++17', '-Wall', '-Wextra', '-Wconversion',
                        '-pedantic', '-Werror', str(HERE / 'read_pattern_fixture.cpp'),
                        '-o', binary], check=True, cwd=scratch, env=compile_environment)
        stats = controls(binary, options.smoke)
        if options.benchmark:
            stats['synthetic_scaling'] = [benchmark(binary, size) for size in options.benchmark]
    print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    main()
