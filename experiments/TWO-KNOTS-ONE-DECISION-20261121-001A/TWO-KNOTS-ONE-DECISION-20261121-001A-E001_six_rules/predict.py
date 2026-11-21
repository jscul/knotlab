"""Independent predictions from the six requested holdings, before comparison.

Bits in an output mask follow the order of its holding. The table itself uses
lexicographic displayed three-bit words, so the rightmost bit changes faster.
This program has no repository imports and accepts no comparison input.
"""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from json import dumps
from pathlib import Path


HOLDS = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8))
ROLES = ((0, 1, 2), (3, 4, 5))
SMALL_HOLDS = ((0, 1, 2), (0, 3, 4))
SMALL_ROLES = ((0,), (1,))
WORDS = tuple(range(8))
READ_ORDER = tuple(sorted(WORDS, key=lambda w: tuple(w >> j & 1 for j in range(3))))


def text_word(word):
    return ''.join(str(word >> j & 1) for j in range(3))


def parity(value):
    return value.bit_count() % 2


def allowed_for(holds, kind):
    if kind == 'nae':
        return tuple(tuple(range(1, 7)) for _ in holds)
    return tuple(tuple(w for w in WORDS if parity(w) == (kind == 'signed' and h == 5))
                 for h in range(len(holds)))


def named_word(marks, word):
    return sum((word >> j & 1) << e for j, e in enumerate(marks))


def restrict(marks, word):
    return sum((word >> e & 1) << j for j, e in enumerate(marks))


def primitive_compile(holds, permitted, reversals=frozenset()):
    n = max(e for holding in holds for e in holding) + 1
    origins = []
    for h, (marks, answers) in enumerate(zip(holds, permitted, strict=True)):
        assert answers
        for subset in WORDS:
            bits = {parity(subset & w) for w in answers}
            if len(bits) == 1:
                origins.append((h, tuple(sorted(e for j, e in enumerate(marks) if subset >> j & 1)), bits.pop()))

    def change(e, f):
        return 1 << (n * e + f)

    active_reversals = frozenset((max(h for h, marks in enumerate(holds) if e in marks), e) for e in reversals)
    systems = [(change(e, e), 0) for e in range(n)]
    for h, marks, rhs in origins:
        systems.extend((sum(change(e, f) for f in marks), 0) for e in range(n))
        systems.extend((sum(change(e, f) for e in marks), 0) for f in range(n))
        signs = sum(1 << (n * n + e) for e in marks)
        ordered = sum(change(e, f) for e, f in combinations(marks, 2))
        systems.append((signs | ordered, rhs ^ (sum((h, e) in active_reversals for e in marks) % 2)))
    for marks in holds:
        systems.extend((change(e, f) | change(f, e), 0) for e, f in combinations(marks, 2))

    # Eliminate the last variable first. Each pivot is forced by earlier bits,
    # while every non-pivot can choose zero without eliminating a completion.
    basis = {}
    for row, bit in sorted(set(systems)):
        while row and row.bit_length() - 1 in basis:
            old_row, old_bit = basis[row.bit_length() - 1]
            row ^= old_row
            bit ^= old_bit
        if row:
            basis[row.bit_length() - 1] = row, bit
        else:
            assert bit == 0, 'frozen six-case equations inconsistent'
    choice = 0
    for place, (row, bit) in sorted(basis.items()):
        choice |= (bit ^ parity(choice & row)) << place

    assert all(parity(choice & row) == bit for row, bit in systems)
    masks = tuple(choice >> (n * e) & ((1 << n) - 1) for e in range(n))
    signs = tuple(choice >> (n * n + e) & 1 for e in range(n))
    carrier = tuple(w for w in range(1 << n) if all(sum(w >> e & 1 for e in marks) % 2 == 0
                                                  for _, marks, _ in origins))
    if any(masks):
        assert all(len(states) * len([row for j, row, _ in origins if j == h]) == 8
                   for h, states in enumerate(permitted))
        accepted = carrier
    else:
        accepted = tuple(w for w in carrier if all(
            sum(((w >> e & 1) ^ signs[e] ^ ((h, e) in active_reversals)) << j for j, e in enumerate(marks)) in answers
            for h, (marks, answers) in enumerate(zip(holds, permitted, strict=True))))
    return masks, signs, carrier, accepted, active_reversals


def project_columns(holds, compiled, holder, answer, *, tag=None):
    """Integer amplitudes with denominator 2**len(marks) for one local outcome.

    tag fixes whether the first controlled branch applied U. None sums both
    alternatives coherently. The effect of a retained tag is resolved before
    summing its probabilities or conditioning on it.
    """
    masks, signs, _, accepted, reversals = compiled
    marks = holds[holder]
    columns = []
    for initial in accepted:
        row = Counter({initial: 1})
        for place, mark in enumerate(marks):
            next_row = Counter()
            for w, a in row.items():
                if place or tag != 1:
                    next_row[w] += a
                if place or tag != 0:
                    bit = ((w >> mark) ^ (answer >> place) ^ signs[mark] ^ ((holder, mark) in reversals)) & 1
                    next_row[w ^ masks[mark]] += -a if bit else a
            row = {w: a for w, a in next_row.items() if a}
        columns.append(row)
    return tuple(columns)


def initial_tables(holds, roles, permitted, compiled):
    _, _, carrier, accepted, _ = compiled
    assert accepted
    columns = {(h, w): project_columns(holds, compiled, h, w) for h in range(len(holds)) for w in WORDS}
    q = Fraction(len(accepted), len(carrier))
    compiled_tables = {source: {} for source in ('coherent', 'dephased', 'independent', 'literal', 'literal_biased')}
    for a, b in product(*roles):
        support = sum(1 << e for e in set(holds[a]) & set(holds[b]))
        eligible = {}
        biased = {}
        for word_a, word_b in product(READ_ORDER, repeat=2):
            address = text_word(word_a) + ',' + text_word(word_b)
            ca = columns[a, word_a]
            cb = columns[b, word_b]
            # Tr(P_a P_b) by the Frobenius inner product of the real symmetric projections.
            numerator = sum(sum(u * col_b.get(i, 0) for i, u in col_a.items())
                            for col_a, col_b in zip(ca, cb, strict=True))
            diag_a = tuple(col.get(w, 0) for w, col in zip(accepted, ca, strict=True))
            diag_b = tuple(col.get(w, 0) for w, col in zip(accepted, cb, strict=True))
            compiled_tables['coherent'].setdefault(f'{a},{b}', {})[address] = Fraction(numerator, 64 * len(accepted))
            compiled_tables['dephased'].setdefault(f'{a},{b}', {})[address] = Fraction(
                sum(u * v for u, v in zip(diag_a, diag_b, strict=True)), 64 * len(accepted))
            compiled_tables['independent'].setdefault(f'{a},{b}', {})[address] = Fraction(
                sum(diag_a) * sum(diag_b), 64 * len(accepted)**2)
            value_a, value_b = named_word(holds[a], word_a), named_word(holds[b], word_b)
            eligible[address] = int(word_a in permitted[a] and word_b in permitted[b]
                                    and not ((value_a ^ value_b) & support))
            biased[address] = eligible[address] * (1 + bool(value_a & (support & -support)))
        for label, weights in (('literal', eligible), ('literal_biased', biased)):
            compiled_tables[label][f'{a},{b}'] = {key: Fraction(w, sum(weights.values())) for key, w in weights.items()}
    result = {}
    for source, tables in compiled_tables.items():
        assert all(sum(table.values()) == 1 for table in tables.values())
        herald = Fraction(1) if source.startswith('literal') else q
        result[source] = {key: {'conditional': [str(x) for x in table.values()],
                                'launch': [str(herald * x) for x in table.values()],
                                'launch_both_refused': str(1 - herald),
                                'other_failure_cells': '0'} for key, table in tables.items()}
    return result


def calculate():
    result = {'holdings': HOLDS, 'roles': ROLES, 'small_holdings': SMALL_HOLDS, 'small_roles': SMALL_ROLES,
              'pairs_order': 'increasing left holder then right holder',
              'words_order': [text_word(w) for w in READ_ORDER], 'cells_order': 'left readout varies more slowly',
              'pair_weight_six': '1/9', 'pair_weight_small': '1', 'catalogues': {}}
    for label, holds, roles, kind in (('signed', HOLDS, ROLES, 'signed'), ('even', HOLDS, ROLES, 'even'),
                                      ('nae', HOLDS, ROLES, 'nae'), ('small_even', SMALL_HOLDS, SMALL_ROLES, 'even'),
                                      ('small_nae', SMALL_HOLDS, SMALL_ROLES, 'nae')):
        permitted = allowed_for(holds, kind)
        device = primitive_compile(holds, permitted)
        masks, signs, carrier, accepted, _ = device
        result['catalogues'][label] = {'masks': masks, 'signs': signs, 'carrier': carrier, 'accepted': accepted,
                                       'tables': initial_tables(holds, roles, permitted, device)}
    return result


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    path = parser.parse_args().output
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as out:
        out.write(dumps(calculate(), indent=2) + '\n')
