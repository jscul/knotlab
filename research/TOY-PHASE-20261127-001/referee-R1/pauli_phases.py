"""Recount the fixed closure's Pauli projectors and the two phase readings.

From the repository root, run:
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 prlimit --as=1879048192 -- \
        .venv/bin/python -B research/TOY-PHASE-20261127-001/referee-R1/pauli_phases.py

Pauli projectors use exact signed word products and trace orthogonality.
The phase preparations use direct counting and exact action on basis states.
Every probability table in the output is recorded in units of 1/8.
"""

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, permutations, product
import json
from math import prod
from pathlib import Path


HERE = Path(__file__).resolve().parent
BITS = tuple(product((0, 1), repeat=3))
KNOTS = ((0, 1, 2), (1, 3, 4), (0, 3, 5), (2, 4, 5))
READERS = ((3, 2), (0, 4), (1, 5))
READ_DISTINCTIONS = {
    settings: tuple(pair[choice] for pair, choice in zip(READERS, settings, strict=True))
    for settings in BITS
}
SCORED = tuple(
    next(settings for settings, distinctions in READ_DISTINCTIONS.items()
         if set(distinctions) == set(knot))
    for knot in KNOTS
)
TARGET_LAWS = (0, 0, 0, 1)

# Powers of i describe signed words and their intermediate products.
ROOTS = (1, 1j, -1, -1j)
IDENTITY = "III"
CYCLIC_PRODUCT = {("X", "Y"): "Z", ("Y", "Z"): "X", ("Z", "X"): "Y"}


@dataclass(frozen=True)
class Pauli:
    word: str
    power: int = 0

    def __mul__(self, other):
        word = []
        power = self.power + other.power
        for left, right in zip(self.word, other.word, strict=True):
            if left == "I":
                word.append(right)
            elif right == "I":
                word.append(left)
            elif left == right:
                word.append("I")
            elif (left, right) in CYCLIC_PRODUCT:
                word.append(CYCLIC_PRODUCT[left, right])
                power += 1
            else:
                word.append(CYCLIC_PRODUCT[right, left])
                power -= 1
        return Pauli("".join(word), power % 4)


def bits_text(bits):
    return "".join(map(str, bits))


def signed(read, bit):
    return Pauli(read.word, (read.power + 2 * bit) % 4)


def selected_word(reads, settings, selected):
    factors = [
        pair[setting] if use else Pauli("I")
        for pair, setting, use in zip(reads, settings, selected, strict=True)
    ]
    return Pauli("".join(factor.word for factor in factors),
                 sum(factor.power for factor in factors) % 4)


def expansion(reads):
    return {settings: [selected_word(reads, settings, selected) for selected in BITS]
            for settings in BITS}


def measurement_table(read_words, expectation):
    table = {}
    for settings, words in read_words.items():
        correlations = [expectation(word) for word in words]
        probabilities = [
            sum(value * (-1) ** sum(a * b for a, b in zip(answer, selected, strict=True))
                for value, selected in zip(correlations, BITS, strict=True))
            for answer in BITS
        ]
        assert sum(probabilities) == 8 and min(probabilities) >= 0
        table[settings] = tuple(probabilities)
    return table


def ideal_table(laws):
    required = dict(zip(SCORED, laws, strict=True))
    return {
        settings: (
            tuple(2 * (sum(answer) % 2 == required[settings]) for answer in BITS)
            if settings in required else (1,) * 8
        )
        for settings in BITS
    }


def matches(first, second):
    return sum(a == b for settings in BITS
               for a, b in zip(first[settings], second[settings], strict=True))


def serial_table(table):
    return {bits_text(settings): values for settings, values in table.items()}


def parity_numerators(table):
    return [sum((-1) ** sum(answer) * numerator
                for answer, numerator in zip(BITS, table[settings], strict=True))
            for settings in SCORED]


def sign_profile(table):
    return [0 if value == 8 else 1 if value == -8 else None
            for value in parity_numerators(table)]


def projector_expansion(knot_ops):
    # The unnormalized product of the four (I + signed knot operator) factors.
    return [
        (used, prod((op for use, op in zip(used, knot_ops, strict=True) if use),
                    start=Pauli(IDENTITY)))
        for used in product((0, 1), repeat=4)
    ]


def projector_terms(terms, laws):
    coefficients = Counter()
    for used, pauli in terms:
        assert pauli.power % 2 == 0
        coefficients[pauli.word] += (-1) ** (
            pauli.power // 2 + sum(a * b for a, b in zip(used, laws, strict=True))
        )
    return {word: weight for word, weight in coefficients.items() if weight}


def trace_expectation(coefficients, pauli):
    assert pauli.power % 2 == 0
    return (-1) ** (pauli.power // 2) * coefficients.get(pauli.word, 0)


def recount_paulis():
    rows = []
    rank_patterns = set()
    compatible_laws = tuple((*parents, 1 ^ (sum(parents) % 2)) for parents in BITS)
    for assignments in product(tuple(permutations("XYZ", 2)), repeat=3):
        reads = tuple(tuple(Pauli(axis) for axis in pair) for pair in assignments)
        knot_ops = tuple(selected_word(reads, settings, (1, 1, 1)) for settings in SCORED)
        assert all(a * b == b * a for a, b in combinations(knot_ops, 2))
        operator_product = prod(knot_ops, start=Pauli(IDENTITY))
        assert operator_product == Pauli(IDENTITY, 2)
        for reader in range(3):
            # Cycle the parents to put this reader's loose distinction in second place.
            ordering = ((reader - 1) % 3, reader, (reader + 1) % 3, 3)
            ordered = tuple(knot_ops[index] for index in ordering)
            for position, pair in enumerate(reads):
                local_factors = tuple(op.word[position] for op in ordered)
                local_product = prod(map(Pauli, local_factors), start=Pauli("I"))
                expected_local_product = (pair[0] * pair[1]) if position == reader else Pauli("I")
                if position == reader:
                    expected_local_product *= expected_local_product
                assert local_product == expected_local_product
            assert prod(ordered, start=Pauli(IDENTITY)) == operator_product

        terms = projector_expansion(knot_ops)
        assert len({pauli.word for used, pauli in terms if not used[3]}) == 8
        measurements = expansion(reads)
        ranks = {}
        table_matches = {}
        for laws in product((0, 1), repeat=4):
            projector = projector_terms(terms, laws)
            # The exact trace is 8/16 times the identity coefficient.
            identity_coefficient = projector.get(IDENTITY, 0)
            assert identity_coefficient % 2 == 0
            rank = identity_coefficient // 2
            ranks[bits_text(laws)] = rank
            assert rank == int(laws in compatible_laws)
            if rank:
                assert all(weight in (-2, 2) for weight in projector.values())
                stabilizer = {word: weight // 2 for word, weight in projector.items()}
                table = measurement_table(measurements,
                                          lambda word: trace_expectation(stabilizer, word))
                table_matches[bits_text(laws)] = matches(table, ideal_table(laws))
                assert table_matches[bits_text(laws)] == 64
            else:
                assert not projector
        rank_patterns.add(tuple(ranks.items()))
        rows.append({
            "reader_assignments": ["".join(pair) for pair in assignments],
            "knot_operators": [op.word for op in knot_ops],
            "product": "-III",
            "matches_by_compatible_law": table_matches,
        })
    assert len(rows) == 216 and len(rank_patterns) == 1
    return {
        "assignments": len(rows),
        "commuting_assignments": len(rows),
        "independent_parent_word_rank": 3,
        "common_eigenspace_rank_by_law_for_each_assignment": dict(rank_patterns.pop()),
        "entries_compared_for_frozen_odd_law": len(rows) * 64,
        "entries_compared_for_all_odd_total_laws": len(rows) * len(compatible_laws) * 64,
        "expected_tables_by_compatible_law": {
            bits_text(laws): serial_table(ideal_table(laws)) for laws in compatible_laws
        },
        "rows": rows,
    }


def act_on_basis(pauli, state, spectator=False):
    image = []
    power = pauli.power
    for position, (axis, bit) in enumerate(zip(pauli.word, state, strict=True)):
        if spectator and position == 0 and bit == 2:
            assert axis in "IXY"
            image.append(bit)
            continue
        image.append(bit ^ (axis in "XY"))
        power += {"I": 0, "X": 0, "Y": 1 + 2 * bit, "Z": 2 * bit}[axis]
    return tuple(image), power % 4


def ghz_expectation(pauli, phase, spectator=False):
    # The vector has only |000> and |111> terms, with amplitudes 1 and
    # i**phase before division by sqrt(2).
    terms = {(0, 0, 0): 0, (1, 1, 1): phase}
    total = 0j
    for state, amplitude in terms.items():
        moved, operator_power = act_on_basis(pauli, state, spectator)
        if moved in terms:
            total += ROOTS[(amplitude + operator_power - terms[moved]) % 4]
    assert total.imag == 0 and total.real in (-2, 0, 2)
    return int(total.real) // 2


def ghz_table(reads, phase, spectator=False):
    return measurement_table(expansion(reads), lambda word: ghz_expectation(word, phase, spectator))


def qubit_read(offset):
    # The conjugations of X by S**offset, in increasing order.
    return (Pauli("X"), Pauli("Y"), Pauli("X", 2), Pauli("Y", 2))[offset % 4]


def qubit_reads(phases, first_offsets=(0, 0, 0)):
    return tuple((qubit_read(offset), qubit_read(offset + phase))
                 for offset, phase in zip(first_offsets, phases, strict=True))


LOCAL_STATES = tuple(product((0, 1), repeat=2))
TOY_PHASES = {
    "1": LOCAL_STATES,
    "a": tuple((q, p ^ (q == 0)) for q, p in LOCAL_STATES),
    "b": tuple((q, p ^ (q == 1)) for q, p in LOCAL_STATES),
    "ab": tuple((q, p ^ 1) for q, p in LOCAL_STATES),
}
TOY_BASE = tuple(
    state for state in product(LOCAL_STATES, repeat=3)
    if len({q for q, _ in state}) == 1 and sum(p for _, p in state) % 2 == 0
)


def toy_move(phase, state):
    return phase[LOCAL_STATES.index(state)]


def compose(left, right):
    return tuple(toy_move(left, state) for state in right)


def toy_table(phases, preparation="1", prep_reader=0, first_offsets=("1", "1", "1")):
    support = [
        tuple(toy_move(TOY_PHASES[preparation], value) if i == prep_reader else value
              for i, value in enumerate(state))
        for state in TOY_BASE
    ]
    assert len(support) == len(set(support)) == 8
    tables = {}
    for settings in BITS:
        read_map = [
            compose(TOY_PHASES[phase if setting else "1"], TOY_PHASES[offset])
            for phase, setting, offset in zip(phases, settings, first_offsets, strict=True)
        ]
        words = Counter(tuple(toy_move(phase, value)[1]
                              for phase, value in zip(read_map, state, strict=True))
                        for state in support)
        tables[settings] = tuple(words[answer] for answer in BITS)
    return tables


def phase_row(phases, preparation, table):
    signs = sign_profile(table)
    return {
        "reader_phases": phases,
        "preparation_phase": preparation,
        "laws_in_knot_order": signs,
        "total_parity": sum(signs) % 2 if None not in signs else None,
        "matches_frozen_target": matches(table, ideal_table(TARGET_LAWS)),
        "probability_numerators": serial_table(table),
    }


def recount_phases():
    toy_rows, toy_controls = [], []
    qubit_rows, qubit_controls = [], []
    displaced_toy = displaced_qubit = 0
    arithmetic_mutant = []
    for phases in product("ab", repeat=3):
        product_map = prod_toy_phase(phases)
        doubled = compose(product_map, product_map)
        assert doubled == TOY_PHASES["1"]
        # The odd exponents are forced to double to 2 in this arithmetic substitution.
        mutant_prediction = 2 * sum({"a": 1, "b": 3}[phase] for phase in phases) % 4
        assert mutant_prediction == 2
        arithmetic_mutant.append({
            "toy_reader_phases": phases,
            "square_of_composed_toy_permutations": "1",
            "doubled_z4_label_sum": mutant_prediction,
        })
        for prep in ("a", "b"):
            table = toy_table(phases, prep)
            row = phase_row(phases, prep, table)
            assert row["total_parity"] == 0
            assert table == ideal_table(row["laws_in_knot_order"])
            for reader in range(3):
                assert toy_table(phases, prep, prep_reader=reader) == table
            assert toy_table(phases, first_offsets=(prep, "1", "1")) == table
            displaced_toy += 1
            toy_rows.append(row)
        for prep in ("1", "ab"):
            control = phase_row(phases, prep, toy_table(phases, prep))
            assert control["laws_in_knot_order"] == [None] * 4
            toy_controls.append(control)

    for phases in product((1, 3), repeat=3):
        doubled = 2 * sum(phases) % 4
        assert doubled == 2
        for prep in (1, 3):
            table = ghz_table(qubit_reads(phases), prep)
            row = phase_row(phases, prep, table)
            assert row["total_parity"] == 1
            assert table == ideal_table(row["laws_in_knot_order"])
            assert ghz_table(qubit_reads(phases, (-prep, 0, 0)), 0) == table
            displaced_qubit += 1
            qubit_rows.append(row)
        for prep in (0, 2):
            control = phase_row(phases, prep, ghz_table(qubit_reads(phases), prep))
            assert control["laws_in_knot_order"] == [None] * 4
            qubit_controls.append(control)

    for rows, total_parity in ((toy_rows, 0), (qubit_rows, 1)):
        counts = Counter(tuple(row["laws_in_knot_order"]) for row in rows)
        expected_profiles = {(*parents, total_parity ^ (sum(parents) % 2)): 2
                             for parents in BITS}
        assert counts == expected_profiles
    assert sum(row["matches_frozen_target"] == 64 for row in qubit_rows) == 2
    assert all(row["matches_frozen_target"] != 64 for row in toy_rows)
    assert sum(row["laws_in_knot_order"] == [0] * 4 for row in toy_rows) == 2

    all_qubit_phases = Counter()
    for phases in product(range(4), repeat=3):
        for preparation in range(4):
            signs = sign_profile(ghz_table(qubit_reads(phases), preparation))
            expected = []
            for settings in SCORED:
                power = (sum(k * setting for k, setting in zip(phases, settings, strict=True))
                         - preparation) % 4
                expected.append(power // 2 if power % 2 == 0 else None)
            assert signs == expected
            key = "uncertain" if None in signs else ("odd" if sum(signs) % 2 else "even")
            all_qubit_phases[key] += 1
    assert all_qubit_phases == {"uncertain": 224, "odd": 16, "even": 16}

    return {
        "toy": toy_rows,
        "qubit": qubit_rows,
        "toy_identity_and_double_swap_controls": toy_controls,
        "qubit_identity_and_Z_controls": qubit_controls,
        "same_64_entries_after_moving_preparation_into_readers": {
            "toy_choices": displaced_toy, "qubit_choices": displaced_qubit,
        },
        "algebraic_toy_mutant": arithmetic_mutant,
        "all_qubit_phase_choices_with_fixed_first_reads": all_qubit_phases,
    }


def prod_toy_phase(phases):
    result = TOY_PHASES["1"]
    for phase in phases:
        result = compose(result, TOY_PHASES[phase])
    return result


def rephase_controls():
    target = ideal_table(TARGET_LAWS)
    base = qubit_reads((1, 1, 1))
    assert ghz_table(base, 1) == target
    displaced = qubit_reads((1, 1, 1), (-1, 0, 0))
    assert displaced[0] == (Pauli("Y", 2), Pauli("X"))
    assert ghz_table(displaced, 0) == target

    unsigned_read_pairs = tuple(permutations("XYZ", 2))
    profiles = Counter()
    signed_matches = []
    for assignment in product(unsigned_read_pairs, repeat=3):
        reads = tuple(tuple(Pauli(axis) for axis in pair) for pair in assignment)
        table = ghz_table(reads, 0)
        profile = sign_profile(table)
        profiles["certain" if None not in profile else "uncertain"] += 1
        if None in profile:
            continue
        count = 0
        for relabels in product(((0, 0), (0, 1), (1, 0), (1, 1)), repeat=3):
            rephased = tuple(tuple(signed(read, bit) for read, bit in zip(pair, change, strict=True))
                             for pair, change in zip(reads, relabels, strict=True))
            count += ghz_table(rephased, 0) == target
        signed_matches.append({"reads": ["".join(pair) for pair in assignment],
                               "unphased_laws": profile, "signed_matches": count})
    assert profiles == {"certain": 4, "uncertain": 212}
    assert all(row["signed_matches"] == 8 for row in signed_matches)
    assert all(row["unphased_laws"] != list(TARGET_LAWS) for row in signed_matches)

    # A third basis value on reader 0 is fixed by each read with sign +1.
    # The read-pair product is iZ on the first two values and +1 on the third.
    x = Pauli("X")
    y = Pauli("Y")
    square_phases = []
    for bit in range(3):
        state = (bit,)
        phase = 0
        for read in (y, x, y, x):
            state, factor = act_on_basis(read, state, spectator=True)
            phase += factor
        assert state == (bit,)
        square_phases.append(phase % 4)
    assert square_phases == [2, 2, 0]
    assert ghz_table(base, 1, spectator=True) == target

    xy = x * y
    assert xy == Pauli("Z", 1)
    assert xy * xy == Pauli("I", 2)
    assert (xy * x * Pauli("Z", 3)) == Pauli("X", 2)
    assert qubit_read(1) == y and qubit_read(2) == Pauli("X", 2)
    return {
        "fixed_unphased_ghz_all_unsigned_assignments": profiles,
        "four_certain_unsigned_assignments_and_signed_relabellings": signed_matches,
        "exact_target_on_unphased_ghz": {
            "reads": [["-Y", "X"], ["X", "Y"], ["X", "Y"]],
            "matches": matches(ghz_table(displaced, 0), target),
        },
        "spectator_extension_on_reader_0": {
            "local_dimension": 3,
            "local_read_pair_product_squared_diagonal": [-1, -1, 1],
            "matches": matches(ghz_table(base, 1, spectator=True), target),
        },
        "XY": "iZ; square -I; conjugates X to -X",
        "S": "diag(1,i); square Z; conjugates X to Y",
    }


def imperfect_score_control():
    # A(theta) maps |b> to exp(i*(-1)**b * theta)|1-b>. On the two
    # GHZ terms the full correlation is the cosine of the sum of read
    # angles minus the preparation angle. Angles here are in units of pi/4.
    read_angles = (0, 1)
    preparation_angle = 1
    exact_cosines = {0: 1, 2: 0, 4: -1, 6: 0}
    correlations = [
        exact_cosines[(sum(read_angles[setting] for setting in settings) - preparation_angle) % 8]
        for settings in SCORED
    ]
    wins = [Fraction(1 + (-1) ** law * correlation, 2)
            for law, correlation in zip(TARGET_LAWS, correlations, strict=True)]
    score = sum(wins) / len(wins)
    # A(0)A(pi/4) is diagonal, so its square doubles the two opposite phases.
    squared_angles = [2 * (read_angles[1] - read_angles[0]) * (-1) ** bit % 8
                      for bit in (0, 1)]
    assert correlations == [1, 1, 1, 0] and score == Fraction(7, 8)
    assert squared_angles == [2, 6]
    return {
        "reads_on_every_qubit": ["X", "(X + Y)/sqrt(2)"],
        "GHZ_relative_phase": "exp(i*pi/4)",
        "scored_parity_expectations_in_knot_order": correlations,
        "win_probabilities_in_knot_order": list(map(str, wins)),
        "equally_weighted_score": str(score),
        "square_of_each_read_pair": "iZ",
    }


def written_closure():
    assert all(len(set(a) & set(b)) == 1 for a, b in combinations(KNOTS, 2))
    uncovered = {pair for pair in combinations(range(6), 2)
                 if not any(set(pair) <= set(knot) for knot in KNOTS)}
    assert uncovered == {tuple(sorted(reads)) for reads in READERS}
    return {"knots": KNOTS, "readers": READERS, "scored_contexts_in_knot_order": SCORED}


def compare_frozen_results(paulis, phases, controls):
    reference = json.loads((HERE.parent / "results.json").read_text())
    assert reference["gate"]["stabilizer state matches the target (of 64)"] == 64
    assert reference["gate"]["mutant flips the closing sign"]
    assert reference["P3"]["assignments"] == paulis["assignments"]
    for theory in ("toy", "qubit"):
        rows = phases[theory]
        frozen = reference["P4"][theory]
        assert len(rows) == len(frozen) == 16
        for row, original in zip(rows, frozen, strict=True):
            labels = "".join(row["reader_phases"]) if theory == "toy" else list(row["reader_phases"])
            assert labels == original["phases"]
            assert row["preparation_phase"] == original["state phase"]
            assert original["certain"] and row["total_parity"] == original["closing"]
    assert controls["exact_target_on_unphased_ghz"]["matches"] == 64


def main():
    assert SCORED == ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1))
    paulis = recount_paulis()
    phases = recount_phases()
    controls = rephase_controls()
    compare_frozen_results(paulis, phases, controls)
    result = {"written_closure": written_closure(), "Pauli_assignments": paulis,
              "phase_readings": phases, "alternative_reads": controls,
              "imperfect_score_control": imperfect_score_control()}
    (HERE / "pauli_phases.json").write_text(json.dumps(result, indent=2) + "\n")
    print("Pauli assignments:", paulis["assignments"],
          "phase choices:", len(phases["toy"]) + len(phases["qubit"]))


if __name__ == "__main__":
    main()
