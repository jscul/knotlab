"""Check the four attachment distinctions held by each pair of ring readers."""

import argparse
from itertools import chain, product
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
from time import perf_counter

from part_b import FROZEN_ROUNDS, MEMORY_LIMIT, grow, mask, pivots_and_remainders, ring_start


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def project(rules, universe, shown, assumptions=()):
    """Forget every other distinction and verify a full completion of each surviving state."""
    right_hand_side = 1 << universe.bit_length()
    equations = rules + [row | (right_hand_side if value else 0) for row, value in assumptions]
    pivots, projected = pivots_and_remainders(equations, universe ^ mask(shown))
    hidden_equations = sorted(pivots.items(), reverse=True)

    def satisfies(row, state):
        return (row & state).bit_count() % 2 == bool(row & right_hand_side)

    allowed = []
    for word in product((0, 1), repeat=len(shown)):
        state = mask(name for name, value in zip(shown, word, strict=True) if value)
        if all(satisfies(equation, state) for equation in projected):
            completion = state
            for pivot, equation in hidden_equations:
                if not satisfies(equation, completion):
                    completion |= pivot
            assert completion & mask(shown) == state
            assert all(satisfies(equation, completion) for equation in equations)
            allowed.append(''.join(map(str, word)))
    return allowed


def canonical_command(shown, allowed):
    """Check the computed four-distinction projection using its excluding clauses."""
    names = [f'd{name}' for name in shown]
    clauses = []
    for values in product('01', repeat=len(shown)):
        if ''.join(values) not in allowed:
            clauses.append(' '.join(('~' if bit == '1' else '') + name
                                    for name, bit in zip(names, values, strict=True)))
    query = [sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', ';'.join(clauses),
             '--loops', *names[:-1], '--contact', names[-1], '--json']
    output = subprocess.check_output(query, cwd=ROOT, env={**os.environ, 'PYTHONPATH': str(ROOT / 'tools')})
    result = json.loads(output)
    assert result['variables'] == names and result['allowed'] == allowed
    return {key: result[key] for key in ('binding', 'loss_on_erasure', 'coexistence', 'is_knot')}


def readers(knots, lineage, rings):
    regions = [mask(chain.from_iterable(knot for knot, ring in zip(knots, lineage, strict=True) if ring == i))
               for i in range(len(rings))]
    return regions


def per_pair_data(round_number, knots, lineage, rings, attachments, fact_sums, selections):
    laws = list(map(mask, knots))
    universe = mask(chain.from_iterable(knots))
    regions = readers(knots, lineage, rings)
    results = []
    expected = [''.join(word) for word in product('01', repeat=4) if word.count('1') % 2 == 0]
    for index in range(0, len(attachments), 2):
        (left, right), left_names = attachments[index]
        pair, right_names = attachments[index + 1]
        assert pair == (left, right)
        shown = list(left_names + right_names)
        connecting_rules = knots[12 + index:14 + index]
        common = sorted(set.intersection(*map(set, connecting_rules)))
        assert mask(shown) == mask(connecting_rules[0]) ^ mask(connecting_rules[1])
        assert len(common) == 2 and not mask(common) & (regions[left] | regions[right])
        assert mask(left_names) & regions[left] == mask(left_names)
        assert mask(right_names) & regions[right] == mask(right_names)
        assert not any(law & regions[left] and law & regions[right] for law in laws)

        baseline = project(laws, universe, shown)
        assert baseline == expected
        same = [[], []]
        empty = [[], []]
        for selection in selections:
            for value in (0, 1):
                allowed = project(laws, universe, shown, [(fact_sums[selection], value)])
                if allowed:
                    assert allowed == expected
                    same[value].append(selection)
                else:
                    assert value == 1
                    empty[value].append(selection)

        # Fixing the two shared connector values is already enough to constrain
        # the readers' own attachment parities separately.
        conditional = []
        for record in product((0, 1), repeat=2):
            assumptions = [(mask([name]), value) for name, value in zip(common, record, strict=True)]
            local = project(laws, universe, shown, assumptions)
            parity = sum(record) % 2
            assert local == [word for word in expected
                             if word[:2].count('1') % 2 == parity and word[2:].count('1') % 2 == parity]
            conditional.append({'values': record, 'allowed': local})

        results.append({'readers': [left, right], 'support': shown, 'two_connecting_rules': connecting_rules,
                        'baseline_allowed': baseline, 'restriction_masks_preserving_projection_by_value': same,
                        'restriction_masks_without_an_allowed_state_by_value': empty,
                        'shared_connector_distinctions': common, 'conditional_on_connector_values': conditional})
    return {'round': round_number, 'frozen_round': round_number in FROZEN_ROUNDS,
            'knots': len(knots), 'distinctions': universe.bit_count(), 'reader_pairs': results}


def controls(row):
    shown = row['support']
    positive = canonical_command(shown, row['baseline_allowed'])
    assert positive['is_knot']
    conditioned = canonical_command(shown, row['conditional_on_connector_values'][0]['allowed'])
    assert conditioned['binding'] and conditioned['coexistence'] and not conditioned['loss_on_erasure']

    unjoined, _, _, attachments = ring_start(linked=False)
    unjoined_shown = list(attachments[0][1] + attachments[1][1])
    unjoined_rows = project(list(map(mask, unjoined)), mask(chain.from_iterable(unjoined)), unjoined_shown)
    assert len(unjoined_rows) == 16
    negative = canonical_command(unjoined_shown, unjoined_rows)
    assert not negative['binding'] and negative['coexistence'] and negative['loss_on_erasure']
    return {'linked_projection': positive, 'conditioned_on_zero_connector_values': conditioned,
            'unjoined_start_projection': negative}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT, MEMORY_LIMIT))
    start = perf_counter()

    knots, rings, loose, attachments = ring_start(linked=True)
    lineage = [label for label, members in enumerate(rings) for _ in members] + [None] * 6
    selections = (1, 7, 10) if args.pilot else range(1, 32)
    stages = []
    for round_number in range(1, 2 if args.pilot else 8):
        births = grow(knots, lineage)
        if round_number == 1:
            halves = (set(rings[0][::2]), set(rings[0][1::2]))
            supports = loose + tuple(tuple(chain.from_iterable(fresh for parents, fresh in births
                                                               if set(parents) <= half)) for half in halves)
            fact_sums = [0]
            for support in supports:
                fact_sums += [row ^ mask(support) for row in fact_sums]
        stages.append(per_pair_data(round_number, knots, lineage, rings, attachments, fact_sums, selections))

    checks = controls(stages[0]['reader_pairs'][0])
    projected_count = len(stages) * 3 * (1 + 2 * len(selections))
    elapsed = perf_counter() - start
    result = {'pilot': args.pilot, 'rounds': stages, 'case_projections': projected_count,
              'canonical_command': checks, 'elapsed_seconds': elapsed,
              'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              'peak_checker_rss_kib': resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
              'address_space_limit_bytes_per_process': MEMORY_LIMIT}
    path = HERE / ('part_b_separation_pilot.json' if args.pilot else 'part_b_separation.json')
    path.write_text(json.dumps(result, indent=2) + '\n')
    print(f'{len(stages)} rounds and {projected_count} baseline or restriction projections in {elapsed:.3f} s')


if __name__ == '__main__':
    main()
