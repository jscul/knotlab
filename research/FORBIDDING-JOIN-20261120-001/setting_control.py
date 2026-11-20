"""Exact one-context comparison. Run from any working directory."""
from collections import Counter
from fractions import Fraction
from itertools import product

PAIRS = tuple(product(range(2), repeat=2))


def answers(pair, setting, reading):
    return pair[setting] if reading == "I" else int(pair == (setting, setting))


def distributions(context, reading, operation, prob_one=Fraction(1, 2)):
    x, y = context
    bits = Counter()
    registers = (Counter(), Counter())
    for r, s, mode in product(range(2), repeat=3):
        weight = (prob_one if r else 1 - prob_one) / 4
        left = (r, s)
        direct = mode == 0 or (context == (0, 0) and operation == "change")
        if operation == "filter" and context == (0, 0) and mode:
            continue
        right = (r, 1 - s) if direct else (s, r)
        registers[0][left] += weight
        registers[1][right] += weight
        bits[(answers(left, x, reading), answers(right, y, reading))] += weight
    mass = sum(bits.values())
    for counts in (bits, *registers):
        for key in counts:
            counts[key] /= mass
    return bits, registers, mass


def score(reading, operation, prob_one=Fraction(1, 2)):
    data = {ctx: distributions(ctx, reading, operation, prob_one) for ctx in PAIRS}
    correlations = [sum((-1)**(a+b)*v for (a,b),v in data[c][0].items()) for c in PAIRS]
    signed = sum(correlations[:3]) - correlations[3]
    for reader in (0,1):
        for own in (0,1):
            c,d = [(own,0),(own,1)] if reader == 0 else [(0,own),(1,own)]
            if prob_one == Fraction(1,2):
                assert data[c][1][reader] == data[d][1][reader]
    return correlations, signed, data


def maximum(correlations):
    return max(sum(sign * value for sign, value in zip(signs, correlations))
               for signs in product((-1, 1), repeat=4) if signs.count(-1) % 2)


def verify():
    for reading in ("I","II"):
        base = score(reading, "ordinary")
        changed = score(reading, "change")
        filtered = score(reading, "filter")
        assert changed[:2] == filtered[:2]
        assert [filtered[2][c][2] for c in PAIRS] == [Fraction(1,2),1,1,1]
        assert all(changed[2][c][2] == 1 for c in PAIRS)
        if reading == "I":
            assert base[1] == 2 and changed[1] == Fraction(5,2)
            assert maximum(base[0]) == 2 and maximum(changed[0]) == Fraction(5,2)
        else:
            assert maximum(base[0]) == 1 and maximum(changed[0]) == Fraction(1,2)
        print(reading, "baseline", tuple(map(str,base[0])), base[1], "one changed context",tuple(map(str,changed[0])),changed[1])
    tables = score("I","change",Fraction(3,4))[2]
    bob = [sum(v for (a,b),v in tables[c][0].items() if b) for c in [(0,0),(1,0)]]
    assert bob == [Fraction(3,4),Fraction(5,8)]
    print("biased control: Bob's setting 0",*bob)
    for law in ("parity","not-all-equal"):
        for pair in PAIRS:
            completions=[v for v in (0,1) if (sum((*pair,v)) % 2 == 0 if law == "parity" else len(set((*pair,v))) > 1)]
            assert completions
        for c in PAIRS:
            for side in score("I","change")[2][c][1]:
                assert set(side)==set(PAIRS)

if __name__ == "__main__":
    verify()
