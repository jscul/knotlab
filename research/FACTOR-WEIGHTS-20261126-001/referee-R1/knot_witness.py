"""Compare listed rules with knots on the actual named distinctions of one sampled start."""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
import os
from pathlib import Path
import random
import resource
import subprocess
import sys
from time import perf_counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENSUS = HERE.parent.parent / 'FORBID-EDITS-20261126-001'
sys.path.insert(0, str(CENSUS))
import forbid  # Only the roster decoding and the actual ordinary growth transition.


def allowed(knots):
    names = {d for knot in knots for d in knot}
    width = max(names) + 1
    unused = ((1 << width) - 1) ^ sum(1 << d for d in names)
    masks = [sum(1 << d for d in knot) for knot in knots]
    states = [w for w in range(1 << width)
              if not w & unused and all((mask & w).bit_count() % 2 == 0 for mask in masks)]
    return width, states


def size_of_projection(states, keep):
    return len({w & keep for w in states})


def canonical_command(knots, scope):
    # Encode every odd assignment of each parity rule by its excluding clause.
    clauses = []
    for knot in knots:
        for word in product((0, 1), repeat=len(knot)):
            if sum(word) % 2:
                clauses.append(' '.join(('-' if bit else '') + f'd{d}' for d, bit in zip(knot, word)))
    rest = sorted(set().union(*map(set, knots)) - set(scope))
    command = [sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', ';'.join(clauses),
               '--loops', *(f'd{d}' for d in scope[:-1]), '--contact', f'd{scope[-1]}',
               '--witnesses', *(f'd{d}' for d in rest), '--json']
    report = json.loads(subprocess.check_output(command, cwd=ROOT,
                                               env={**os.environ, 'PYTHONPATH': str(ROOT / 'tools')}))
    return {k: report[k] for k in ('binding', 'loss_on_erasure', 'coexistence', 'is_knot')}


def initially_valid(census, picks, pilot):
    # A separate question: does checking the starting rules once suffice?
    index = 30
    start = forbid.supports_of(census[index])
    before = [canonical_command(start, sorted(scope)) for scope in (start[:1] if pilot else start)]
    assert all(item['is_knot'] for item in before)
    new, status, _ = forbid.grown(start, 'parity', 'one_fewer')
    assert status == 'funded'
    _, old = allowed(start)
    _, words = allowed(new)
    scope = next(sorted(scope) for scope in new if {9, 10} <= set(scope))
    result = canonical_command(new, scope)
    pair = (1 << 9) | (1 << 10)
    remainders = {w & ~pair for w in words}
    assert set(words) == {other | bits for other in remainders for bits in (0, pair)}
    assert not result['is_knot']
    return {'census_index': index, 'position_in_sample': picks.index(index) + 1,
            'start': start, 'starting_checks': before, 'first_round': new,
            'old_allowed': len(old), 'new_allowed': len(words), 'distinct_remainders': len(remainders),
            'rule_containing_9_and_10': scope, 'rule_check': result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    clock = perf_counter()
    census = json.loads((CENSUS / 'starts.json').read_text())
    index = 3480
    picks = random.Random(20261129).sample(range(len(census)), 300)
    assert index in picks
    stages = [forbid.supports_of(census[index])]
    statuses = []
    for _ in range(2):
        new, status, _ = forbid.grown(stages[-1], 'parity', 'ordinary')
        statuses.append(status)
        if status != 'funded':
            break
        stages.append(new)
    start_width, old = allowed(stages[0])
    width, states = allowed(stages[-1])
    assert len(stages) == 2 and width == 12
    old_mask = (1 << start_width) - 1
    multiplicity = Counter(w & old_mask for w in states)
    assert set(old) == set(multiplicity)
    pair = (9, 10)
    pairmask = sum(1 << d for d in pair)
    finish_table = []
    start_table = []
    for a, b in product((0, 1), repeat=2):
        w = (a << pair[0]) | (b << pair[1])
        finish_table.append(str(Fraction(w in states, len(states))))
        start_table.append(str(Fraction(1, len(old) * multiplicity[w & old_mask]) if w in states else 0))
    assert finish_table == start_table
    assert finish_table[1:3] == ['0', '0'] and Fraction(finish_table[0]) > 0
    # Every allowed assignment off the pair occurs with both allowed values of the pair.
    other_states = {w & ~pairmask for w in states}
    assert set(states) == {w | bits for w in other_states for bits in (0, pairmask)}
    largest = 3 if args.pilot else width
    qualified = []
    tested = 0
    for size in range(3, largest + 1):
        for scope in combinations(range(width), size):
            tested += 1
            mask = sum(1 << d for d in scope)
            if size_of_projection(states, mask) == 1 << size:
                continue
            if all(size_of_projection(states, mask ^ (1 << d)) == 1 << (size - 1) for d in scope):
                qualified.append(scope)
    assert not any(set(scope) & set(pair) for scope in qualified)
    listed = [sorted(rule) for rule in stages[-1] if set(pair) <= set(rule)]
    # Pass the two listed rules that hold the pair to the canonical command.
    scopes = listed[:1] if args.pilot else listed
    verdicts = [{'scope': s, **canonical_command(stages[-1], s)} for s in scopes]
    assert all(not check['loss_on_erasure'] for check in verdicts)
    second = initially_valid(census, picks, args.pilot)
    print(json.dumps({'census_index': index, 'position_in_sample': picks.index(index) + 1,
                      'statuses': statuses, 'stages': stages, 'start_states': len(old),
                      'final_states': len(states), 'distinct_remainders': len(other_states),
                      'per_start_completions': sorted(set(multiplicity.values())),
                      'both_countings_given_other_values_zero_unnormalised_slice': finish_table,
                      'subsets_tested': tested, 'knots_on_named_distinctions': qualified,
                      'listed_rules_holding_pair': verdicts, 'initially_valid_example': second,
                      'seconds': round(perf_counter() - clock, 4),
                      'peak_rss_kib': max(resource.getrusage(kind).ru_maxrss for kind in
                                          (resource.RUSAGE_SELF, resource.RUSAGE_CHILDREN))}, indent=2))


if __name__ == '__main__':
    main()
