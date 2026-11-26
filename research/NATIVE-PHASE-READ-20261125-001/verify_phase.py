"""Exact checks of the order argument, ordinary one-reader model and phase probes."""

import json
from collections import Counter
from fractions import Fraction
from itertools import product
from math import prod
from pathlib import Path


BITS = (0, 1)
WORDS = tuple(word for word in product(BITS, repeat=3) if sum(word) % 2 == 0)
AXES = range(3)  # One-reader convention: Z, X, Y.


def check_order_argument():
    # The other changed reader sees the same word in both compared orders.
    for i in AXES:
        for word in WORDS:
            passing = []
            for new_word in WORDS:
                for k in AXES:
                    if k == i:
                        continue
                    possible = any(
                        (u ^ v ^ word[k]) == (u ^ v ^ new_word[k]) == 1
                        for u, v in product(BITS, repeat=2)
                    )
                    if not possible:
                        break
                else:
                    passing.append(new_word)
            assert passing == [word]

    # With all writes idle, any setting-independent seed gives one answer list.
    counts = Counter()
    for answers in product(BITS, repeat=6):
        wins = 0
        for setting in WORDS:
            parity = sum(answers[2 * i + setting[i]] for i in AXES) % 2
            wins += parity == int(any(setting))
        counts[wins] += 1
    assert counts == {1: 32, 3: 32}
    print("All 36 nonidentity writes excluded by the two-order test. All 64 static lists checked.")


def eigenpreparation(axis, bit):
    return {word: Fraction(1, 2) for word in WORDS if word[axis] == bit}


def check_single_reader():
    # Prove closure on the six states by checking every one-step conditional law.
    conditional_laws = 0
    for prepared, value, asked in product(AXES, BITS, AXES):
        joint = Counter()
        for word, prob in eigenpreparation(prepared, value).items():
            for toggle in BITS:
                updated = tuple(v ^ (toggle if i != asked else 0) for i, v in enumerate(word))
                assert updated in WORDS
                joint[word[asked], updated] += prob / 2
        for answer in BITS:
            mass = sum(p for (a, _), p in joint.items() if a == answer)
            expected = int(value == answer) if asked == prepared else Fraction(1, 2)
            assert mass == expected
            if mass:
                conditional = {w: p / mass for (a, w), p in joint.items() if a == answer}
                assert conditional == eigenpreparation(asked, answer)
                conditional_laws += 1
    assert conditional_laws == 30
    print("Six one-reader preparations closed under all 30 possible conditional updates.")
    # After reading X on Z=0, only the chosen disturbance can change Z.
    prepared = eigenpreparation(0, 0)
    for flip_probability in (0, Fraction(1, 2), 1):
        chance_z_one = sum(p * ((1 - flip_probability) * w[0] + flip_probability * (w[0] ^ 1))
                           for w, p in prepared.items())
        assert chance_z_one == flip_probability
    biased = {WORDS[0]: Fraction(3, 4), WORDS[1]: Fraction(1, 4)}
    assert sum(p * w[1] for w, p in biased.items()) == Fraction(1, 4)

    # Use bits for the signs: reversal of a sign flips its bit.
    required = [(z, y ^ 1, x) for z, x, y in WORDS]
    assert all(target not in WORDS for target in required)
    scores = Counter()
    for images in product(WORDS, repeat=4):
        correct = sum(bit == wanted for image, target in zip(images, required)
                      for bit, wanted in zip(image, target))
        scores[correct] += 1
    swap_score = sum(bit == wanted for (z, x, y), target in zip(WORDS, required)
                     for bit, wanted in zip((z, y, x), target))
    assert scores == {0: 1, 2: 12, 4: 54, 6: 108, 8: 81}
    assert swap_score == max(scores) == 8

    enlarged = {w for w in product(BITS, repeat=4) if sum(w) % 2 == 0}
    enlarged_images = {(z, y ^ 1, x, h ^ 1) for z, x, y, h in enlarged}
    assert enlarged_images == enlarged
    print("Best reference-preserving pulse score 8/12 across 256 maps; extra orientation bit permits 12/12.")

    # A pair flip through c can carry an ordinary direction if the preparation
    # and the rule selecting which partner to flip are both supplied.
    forward = {(a, b, c): (b, a ^ 1, c ^ 1) for a, b, c in WORDS}
    backward = {end: start for start, end in forward.items()}
    assert len(backward) == 4
    for word in WORDS:
        assert forward[word] in WORDS and sum(a != b for a, b in zip(word, forward[word])) == 2
        assert forward[forward[word]] != word
        assert forward[forward[forward[forward[word]]]] == word
    prepared = eigenpreparation(0, 0)
    p_forward = sum(p * forward[w][1] for w, p in prepared.items())
    p_backward = sum(p * backward[w][1] for w, p in prepared.items())
    assert (p_forward, p_backward, (p_forward + p_backward) / 2) == (1, 0, Fraction(1, 2))
    print("A lawful directed four-cycle gives chance 1 vs 0 on a prepared reference; mixing directions gives 1/2.")


def quantum_probe(questions, outcomes, sign):
    """Benchmark only. Gaussian-integer numerators for (|000> +/- i|011>)/sqrt(2)."""
    def bra(question, answer, bit):
        if question == "Z":
            return int(answer == bit)
        if bit == 0:
            return 1
        return (-1) ** answer * {"X": 1, "Y": -1j}[question]

    def overlap(word):
        return prod(bra(q, a, b) for q, a, b in zip(questions, outcomes, word))

    amplitude = overlap((0, 0, 0)) + sign * 1j * overlap((0, 1, 1))
    magnitude = int(amplitude.real ** 2 + amplitude.imag ** 2)
    return Fraction(magnitude, 2 ** (1 + sum(q != "Z" for q in questions)))


def check_two_preparations():
    for questions in product(("Z", "Y"), repeat=3):
        for outcome in product(BITS, repeat=3):
            assert quantum_probe(questions, outcome, 1) == quantum_probe(questions, outcome, -1)
    for sign in (1, -1):
        masses = Counter()
        for outcome in product(BITS, repeat=3):
            masses[(-1) ** (outcome[1] + outcome[2])] += quantum_probe("ZXY", outcome, sign)
        assert masses[sign] == 1 and masses[-sign] == 0
    print("Two conjugate benchmark preparations agree in 64 Z/Y cells; a calibrated X and Y gives opposite products.")


def check_benchmark_archive():
    here = Path(__file__).resolve().parent
    artifacts = here.parents[1] / "artifacts"
    old_id = "FOUR-SETTINGS-PARITY-20261125-001"
    old = json.loads((artifacts / old_id / f"{old_id}-E001_four_settings" / "results.json").read_text())
    new_path = artifacts / here.name / f"{here.name}-E001_sequential_readings" / "results.json"
    new = json.loads(new_path.read_text())
    assert old["setting_and_outcome_order"] == new["outcome_order"]
    added = new["added_record_control"]
    control = added["cases"]["fair_record"]
    for setting in old["setting_and_outcome_order"]:
        observed = control["table_numerators_identical_in_every_order"][setting]
        reference = old["born_numerators"][setting]
        assert all(Fraction(a, added["probability_denominator"]) == Fraction(b, old["probability_denominator"])
                   for a, b in zip(observed, reference, strict=True))
    assert len(control["matched_settings_by_order"]) == 6
    assert all(len(v) == 8 for v in control["matched_settings_by_order"].values())
    print("The fair common-bit device matches the independently archived quantum probabilities in every order.")


if __name__ == "__main__":
    check_order_argument()
    check_single_reader()
    check_two_preparations()
    check_benchmark_archive()
