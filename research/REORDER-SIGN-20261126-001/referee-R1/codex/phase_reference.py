"""Exact independent check of what information is provided by parent signs.

Fix the ascending exterior basis a,b,c for the parents. Group each old mode x
with its child modes y,z in the output basis. Within such a group F1 on x,y
is X_x X_y. Its flip changes x while preserving z and y=x XOR z.
"""

from itertools import combinations, permutations, product
import json
from math import prod
from pathlib import Path


LABELS = 'abc'
ORDERS = [''.join(order) for order in permutations(LABELS)]
PAIRS = [''.join(pair) for pair in combinations(LABELS, 2)]
EVEN = ['', *PAIRS]


def exchange_sign(order, occupied, reference):
    """Sign from sorting the occupied subsequence into the reference listing."""
    indices = [reference.index(item) for item in order if item in occupied]
    inversions = sum(a > b for a, b in combinations(indices, 2))
    return (-1) ** inversions


def phase_after_births(start, order, parents):
    # Each child block has the parity of its parent. Move the blocks, which
    # were created by left multiplication, to just after their parents.
    return start[parents] * exchange_sign(order, parents, LABELS)


def check_grouping_identity():
    basis = [(label, name) for label in LABELS for name in 'xyz']
    checked = 0
    for order, occupied_parents, spectators in product(
            ORDERS, EVEN, product((0, 1), repeat=3)):
        occupied = set()
        for label, z in zip(LABELS, spectators):
            x = int(label in occupied_parents)
            for name, bit in zip('xyz', (x, x ^ z, z)):
                if bit:
                    occupied.add((label, name))
        left_product = ([(label, name) for label in reversed(order) for name in 'yz']
                        + [(label, 'x') for label in LABELS])
        direct = exchange_sign(left_product, occupied, basis)
        expected = exchange_sign(order, occupied_parents, LABELS)
        assert direct == expected
        checked += 1
    return checked


def changed_parents(word, flips):
    return ''.join(label for label in LABELS if (label in word) != (label in flips))


def exact_even_correlations(start, order):
    # Spectator sum contributes eight identical terms under the standard F1.
    amp = {word: phase_after_births(start, order, word) for word in EVEN}
    numerators = []
    for flips in EVEN:
        numerator = sum(amp[word] * amp[changed_parents(word, flips)]
                        * (-1) ** sum(label not in flips for label in word)
                        for word in EVEN)
        numerators.append(numerator)
    return numerators  # divide by four


def check_starts():
    rows = []
    for pair_phases in product((1, -1), repeat=3):
        start = dict(zip(EVEN, (1, *pair_phases)))
        # Applying parent creators successively prepends each new operator.
        chronological = [rho for rho in ORDERS
                         if all(start[w] == exchange_sign(rho[::-1], w, LABELS)
                                for w in EVEN)]
        full, exact_parities = [], []
        for order in ORDERS:
            nums = exact_even_correlations(start, order)
            if prod(nums) == -(4**4):
                full.append(order)
            if nums == [4, -4, -4, -4]:
                exact_parities.append(order)
        assert full == [order for order in ORDERS
                        if prod(pair_phases) * exchange_sign(order, LABELS, LABELS) == -1]
        assert exact_parities == chronological
        rows.append({'pair_phases_ab_ac_bc': pair_phases, 'positive_chronological_order': chronological,
                     'full': full, 'fixed_target_parities': exact_parities})
    return rows


def four_reader_control():
    """One size beyond the reported Fock model. Build each exterior monomial."""
    n = 4
    grouped_order = list(range(3 * n))  # each consecutive triple is x,y,z
    even = [mask for mask in range(1 << n) if mask.bit_count() % 2 == 0]
    xmask = sum(1 << (3 * j) for j in range(n))
    full = []
    for order in permutations(range(n)):
        creator_product = ([3 * j + k for j in reversed(order) for k in (1, 2)]
                           + [3 * j for j in reversed(range(n))])
        state = {}
        for parents, spectator in product(even, range(1 << n)):
            occupied = [3 * j + k for j in range(n)
                        for k, word in enumerate((parents, parents ^ spectator, spectator))
                        if (word >> j) & 1]
            mask = sum(1 << mode for mode in occupied)
            state[mask] = exchange_sign(creator_product, occupied, grouped_order)
        cor = {}
        for t in even:
            flip = sum(3 << (3 * j) for j in range(n) if (t >> j) & 1)
            read_z = xmask & ~flip
            cor[t] = sum(amplitude * state[mask ^ flip] * (-1) ** (mask & read_z).bit_count()
                         for mask, amplitude in state.items())
        norm = len(state)
        if (all(abs(value) == norm for value in cor.values())
                and any(cor[a] * cor[b] != cor[a ^ b] * cor[0] for a, b in product(even, repeat=2))):
            full.append(''.join('abcd'[j] for j in order))
    assert full == ['abcd', 'bcda', 'cdab', 'dabc']
    return {'parent_chronology': 'abcd', 'commit_orders': 24,
            'nonzero_basis_words_per_order': 128, 'full_F1': full}


if __name__ == '__main__':
    result = {'basis': 'canonical ascending parent monomials a,b,c; amplitude of vacuum +',
              'inventory_groupings_checked': check_grouping_identity(), 'starts': check_starts(),
              'four_readers': four_reader_control()}
    Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
