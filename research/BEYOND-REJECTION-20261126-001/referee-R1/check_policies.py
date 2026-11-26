"""Compare all binary policy choices with the reference address on exact integer masses."""
import argparse
import json
from collections import Counter
from itertools import product
from time import perf_counter

BITS = (0, 1)
WORDS = tuple(product(BITS, repeat=3))


def changes(weight, side, own, visible):
    """For each visible sender input, accumulate the change in receiver record counts."""
    distinct = tuple(product(BITS, WORDS)) if visible else WORDS
    changes = {v: Counter() for v in distinct}
    for (u, v, a, b), mass in weight.items():
        near, far = ((u, a), (v, b)) if side == 0 else ((v, b), (u, a))
        if near[0] == own:
            key = far if visible else far[1]
            for address, coeff in [(0, -1), (1, 1)]:
                changes[key][near + (address == far[0],)] += coeff * mass
    return list(changes.values())


def count_preserving(parts):
    """Gray order changes one policy value per step; retain a sparse exact difference."""
    current = Counter()
    last = 0
    same = 1
    for i in range(1, 1 << len(parts)):
        word = i ^ (i >> 1)
        bit = (last ^ word).bit_length() - 1
        sign = 1 if word & (1 << bit) else -1
        for record, delta in parts[bit].items():
            current[record] += sign * delta
            if current[record] == 0:
                del current[record]
        same += not current
        last = word
    return same


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="time the first full-visibility case at full alphabet")
    pilot = parser.parse_args().pilot
    begin = perf_counter()
    cases = {}
    for u, v, a in product(BITS, BITS, WORDS):
        b = a if (u, v) != (1, 1) else (a[2], a[0], a[1])
        cases.setdefault("parity_uniform", {})[u, v, a, b] = 1
        if not any(a) or all(a):
            cases.setdefault("parity_mixture", {})[u, v, a, a] = 1
        for other in WORDS:
            cases.setdefault("nae_uniform", {})[u, v, a, other] = 1
    result = []
    for name, weights in cases.items():
        for visible, side, own in product((True, False), BITS, BITS):
            slices = changes(weights, side, own, visible)
            total = 1 << len(slices)
            same = count_preserving(slices)
            invariant = all(all(n == 0 for n in sl.values()) for sl in slices)
            assert invariant == (total == same)
            result.append(dict(source=name, sees_label=visible, receiving_side=side, own_address=own,
                               total=total, same_as_constant_zero=same, joint_equalities=invariant))
            if pilot:
                break
        if pilot:
            break
    print(json.dumps({"checks": result, "elapsed_seconds": round(perf_counter() - begin, 6)}, indent=2))


if __name__ == "__main__":
    main()
