"""Rebuild supplied readings from the word and weighting definitions."""

import argparse
from fractions import Fraction
from itertools import product
from time import perf_counter


def normalize(weights):
    total = sum(weights)
    assert total > 0
    return tuple(Fraction(value, total) for value in weights)


def signed_support(pilot):
    visible = list(product(range(2), repeat=3))
    for a, b, c in visible[:1] if pilot else visible:
        counts = [0, 0]  # positive completions, negative completions
        for u, v, w in product(range(2), repeat=3):
            local = ((a, w, u), (b, v, u), (v, w, c))
            if all(min(t) != max(t) for t in local):
                minus = local.count((1, 1, 0)) % 2
                counts[minus] += 1
        signed = counts[0] - counts[1]
        expected = 0 if a == b == c else (-3 if (a, b, c) == (1, 1, 0) else 3)
        assert sum(counts) > 0 and signed == expected
        print(f"  visible {a}{b}{c}: ordinary={sum(counts)}, signed={signed}")


def two_readers(pilot):
    # Four potential reads in order a0,a1,b0,b1, with a0=b1.
    words = [w for w in product(range(2), repeat=4) if w[0] == w[3]]
    choices = list(product(range(2), repeat=2))
    correlations = {rule: [] for rule in ("unit", "signed", "squared")}
    for i, j in choices[:1] if pilot else choices:
        counts, sums = [0] * 4, [0] * 4
        for a0, a1, b0, b1 in words:
            index = 2 * (a0, a1)[i] + (b0, b1)[j]
            counts[index] += 1
            sums[index] += (-1) ** ((a0 ^ a1) * (b0 ^ b1))
        assert sum(sums) == 4
        for rule, weights in (("unit", counts), ("signed", sums),
                              ("squared", [value**2 for value in sums])):
            probabilities = normalize(weights)
            assert min(probabilities) >= 0
            p00, p01, p10, p11 = probabilities
            assert p00 + p01 == p00 + p10 == Fraction(1, 2)
            correlations[rule].append(p00 + p11 - p01 - p10)
        print(f"  settings {i}{j}, counts={counts}, signed sums={sums}")
    if not pilot:
        for rule, values in correlations.items():
            chsh = max(abs(sum(values) - 2 * value) for value in values)
            print(f"  {rule}: correlations={list(map(str, values))}, CHSH={chsh}")
            assert chsh == (1 if rule == "unit" else 4)


def three_readers(pilot):
    words = list(product(range(2), repeat=3))
    sources = {
        "signed": (1, -1, -1, -1),
        "positive": (1, 1, 1, 1),
        "unequal": (2, 1, 1, 1),
    }
    even_words = [w for w in words if sum(w) % 2 == 0]
    for name, source in sources.items():
        for setting in ([words[0]] if pilot else words):
            amplitudes = []
            for output in words:
                amplitude = 0
                for old, weight in zip(even_words, source):
                    if any(s == 0 and x != y for s, x, y in zip(setting, old, output)):
                        continue
                    flips = sum(s * x * y for s, x, y in zip(setting, old, output))
                    amplitude += weight * (-1)**flips
                amplitudes.append(amplitude)
            rows = (
                normalize([int(a != 0) for a in amplitudes]),
                normalize([abs(a) for a in amplitudes]),
                normalize([a*a for a in amplitudes]),
            )
            if name == "signed":
                assert rows[0] == rows[1] == rows[2]
                if sum(setting) % 2:
                    expected = [Fraction(1, 8)] * 8
                else:
                    expected = [Fraction((sum(w) % 2) == int(any(setting)), 4) for w in words]
                assert rows[0] == tuple(expected)
            if setting in ((0, 0, 0), (0, 1, 1)):
                print(f"  {name}, setting {setting}, amplitudes={amplitudes}, "
                      f"P(001)={[str(row[1]) for row in rows]}, "
                      f"P(A=0)={[str(sum(row[:4])) for row in rows]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="time the first setting of each check")
    pilot = parser.parse_args().pilot
    for check, settings in ((two_readers, 4), (three_readers, 8), (signed_support, 8)):
        before = perf_counter()
        check(pilot)
        elapsed = perf_counter() - before
        print(f"{check.__name__}: {elapsed:.6f}s" +
              (f", projected full {elapsed * settings:.6f}s" if pilot else ""))
