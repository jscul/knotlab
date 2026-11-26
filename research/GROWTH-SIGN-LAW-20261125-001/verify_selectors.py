"""Enumerate the possible exterior readings without attributing them to a birth."""

import argparse
from collections import Counter
from itertools import product
import json
from math import prod
from pathlib import Path


def words(n):
    return product((0, 1), repeat=n)


def parity(word):
    return sum(word) % 2


def key(word):
    return "".join(map(str, word))


def tensor(word, signed):
    if parity(word):
        return 0
    return (-1) ** (sum(word) // 2) if signed else 1


def three_copy_control(n):
    rows = {}
    for exterior in words(n):
        fills = {}
        for shared in words(n):
            local = [(shared[i-1], shared[i], exterior[i]) for i in range(n)]
            if any(parity(w) for w in local):
                continue
            fills[key(shared)] = prod(tensor(w, True) for w in local)
        rows[key(exterior)] = {"complete_fillings": fills, "positive": len(fills),
                               "signed": sum(fills.values())}
    return rows


def six_private_distinctions():
    """Each old four-place holder has two private and two shared distinctions."""
    multiplicities = Counter()
    xor_multiplicities = Counter()
    payment_triples = {choice: Counter() for choice in words(3)}
    for private in words(6):
        pairs = [private[2*i:2*i+2] for i in range(3)]
        checksum = tuple(parity(pair) for pair in pairs)
        for shared in words(3):
            if any(parity((shared[i-1], shared[i], *pairs[i])) for i in range(3)):
                continue
            multiplicities[key(private)] += 1
            xor_multiplicities[key(checksum)] += 1
            for choice, counts in payment_triples.items():
                paid = tuple(pair[c] for pair, c in zip(pairs, choice))
                counts[key(paid)] += 1
    assert len(multiplicities) == 32 and set(multiplicities.values()) == {2}
    assert len(xor_multiplicities) == 4 and set(xor_multiplicities.values()) == {16}
    assert all(len(table) == 8 and set(table.values()) == {8} for table in payment_triples.values())
    return {"six_private_words": dict(sorted(multiplicities.items())),
            "three_private_pair_xors": dict(sorted(xor_multiplicities.items())),
            "three_actual_payments_by_choice": {key(c): dict(sorted(t.items())) for c, t in payment_triples.items()}}


def matrix_values():
    result = {}
    for u, v in ((1, 0), (1, 1), (1, -1), (0, 1), (2, -3)):
        row = {}
        for signed, label in ((False, "positive"), (True, "signed")):
            matrix = [[sum(w * tensor((x, y, z), signed) for z, w in enumerate((u, v)))
                       for y in (0, 1)] for x in (0, 1)]
            (a, b), (c, d) = matrix
            det = a*d-b*c
            assert det == (-(u*u+v*v) if signed else u*u-v*v)
            row[label] = {"matrix": matrix, "determinant": det}
        result[str((u, v))] = row
    return result


def extension_signs():
    """Ordinary extensions copy each input record and may keep arbitrary signs."""
    # One unary ternary birth through a distinguished bit of an old ternary.
    fibres = {w: [(*w, y, z) for y, z in words(2) if not parity((w[0], y, z))]
              for w in words(3) if not parity(w)}
    lifts = {}
    for label, signed in (("positive", False), ("signed", True)):
        lifted = {out: tensor(w, signed) for w, outputs in fibres.items() for out in outputs}
        recovered = {key(w): sum(lifted[out] for out in outputs) for w, outputs in fibres.items()}
        assert all(recovered[key(w)] == 2 * tensor(w, signed) for w in fibres)
        lifts[label] = recovered
    same_first = [[sum(y == observed for y, z in words(2) if not parity((x, y, z)))
                   for observed in (0, 1)] for x in (0, 1)]
    assert same_first == [[1, 1], [1, 1]]
    return {"extensions_per_word": 2, "single_fresh_bit_counts": same_first,
            "two_fresh_bits_recover_inherited_bit": all((o[-1] ^ o[-2]) == o[0]
                for outputs in fibres.values() for o in outputs), "lift_then_sum_back": lifts}


def run():
    three, four = three_copy_control(3), three_copy_control(4)
    for name, row in three.items():
        assert row["positive"] == (0 if parity(tuple(map(int, name))) else 2)
        assert row["signed"] == 0
    assert three["000"]["complete_fillings"] == {"000": 1, "111": -1}
    assert all(abs(row["signed"]) == row["positive"] for row in four.values())
    assert four["0000"]["signed"] == 2
    return {"ternary_three": three, "ternary_four_offline": four,
            "four_place_three": six_private_distinctions(), "open_sums": matrix_values(),
            "ordinary_lift": extension_signs()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if args.smoke:
        print(three_copy_control(3)["000"])
        return
    encoded = json.dumps(run(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if encoded != args.check.read_text():
            raise SystemExit("Exterior and determinant receipt differs")
        print("Exterior and determinant receipt matches")
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
