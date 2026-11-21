"""Independent direct sum on ordinary allowed words for the finite reader controls.

Run with Python 3 and compare its standard output with reading_replay.json.
"""
from fractions import Fraction
from itertools import product
import json


def direct_table(holders, readers, law):
    """Project sign changes and ordinary reads, summing amplitudes at fixed unread words."""
    size = 1 + max(max(holder) for holder in holders)
    masks = [sum(1 << i for i in holder) for holder in holders]

    def lawful(word):
        if law == "parity":
            return all((word & mask).bit_count() % 2 == 0 for mask in masks)
        return all((word & mask) not in (0, mask) for mask in masks)

    words = [word for word in range(1 << size) if lawful(word)]
    outputs = list(product((0, 1), repeat=len(readers)))
    table = {}
    marginals = {}
    for setting in product("XZ", repeat=len(readers)):
        x_mask = sum(1 << i for i, op in zip(readers, setting) if op == "X")
        z_mask = sum(1 << i for i, op in zip(readers, setting) if op == "Z")
        rows = {}
        for out in outputs:
            negative = sum(bit << i for i, bit in zip(readers, out))
            sums = {}
            for word in words:
                if (word & z_mask) == (negative & z_mask):
                    exterior = word & ~x_mask
                    sign = (-1) ** ((word & negative & x_mask).bit_count())
                    sums[exterior] = sums.get(exterior, 0) + sign
            rows[out] = Fraction(sum(v * v for v in sums.values()), len(words) * (1 << x_mask.bit_count()))
        assert sum(rows.values()) == 1
        for i, op in enumerate(setting):
            plus = sum(p for out, p in rows.items() if out[i] == 0)
            assert marginals.setdefault((i, op), plus) == plus
        table[setting] = rows
    return table


def signed_score(table, coefficients=(1, 0, -1, 0)):
    return sum(coefficients[setting.count("Z") % 4] *
               sum((-1) ** sum(out) * p for out, p in rows.items())
               for setting, rows in table.items())


def minority_shortfall(table):
    """Largest exact deficiency in the six-bin matching for a physical NAE ternary."""
    ordinary = table[tuple("ZZZ")]
    changes = table[tuple("XXX")]
    demands = {}
    for i in range(3):
        j, k = [v for v in range(3) if v != i]
        mass = sum(p for o, p in ordinary.items() if o[j] == o[k] != o[i])
        for answer in (0, 1):
            demands[i, answer] = mass / 2
    assert sum(demands.values()) == 1
    largest = Fraction(0)
    for flags in product((False, True), repeat=len(demands)):
        bins = [key for key, yes in zip(demands, flags) if yes]
        need = sum(demands[key] for key in bins)
        available = sum(p for o, p in changes.items() if any(o[i] == sign for i, sign in bins))
        largest = max(largest, need - available)
    return largest


def replay():
    result = {}
    for law in ("not-all-equal", "parity"):
        tests = {}
        for k in range(4):
            holders = [range(3)] + [(i, 3 + 2*i, 4 + 2*i) for i in range(k)]
            t = direct_table(holders, range(3), law)
            case = {"score": str(signed_score(t))}
            if law == "not-all-equal":
                case["common_list_mass_shortfall"] = str(minority_shortfall(t))
            tests[f"attached_ternaries_{k}"] = case
        for width in (4, 5):
            full = direct_table([range(width)], range(width), law)
            three = direct_table([range(width)], range(3), law)
            tests[f"isolated_{width}"] = {
                "full_score": str(signed_score(full)),
                "three_reader_score": str(signed_score(three)),
            }
            if width % 2 == 0:
                tests[f"isolated_{width}"]["rotated_full_score"] = str(signed_score(full, (1, 1, -1, -1)))
        result[law] = tests
    result["three_attached_four_place_score"] = str(signed_score(direct_table(
        [range(3)] + [(i, *range(3 + 3*i, 6 + 3*i)) for i in range(3)], range(3), "not-all-equal")))
    assert result["not-all-equal"]["attached_ternaries_2"]["common_list_mass_shortfall"] == "5/216"
    return result


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2, sort_keys=True))
