"""Partial trace versus its mixture of conditional products, with exact entries."""
import argparse
from itertools import islice, product
from time import perf_counter


def readers_given(u, j, r, weighted):
    # One even-parity knot per reader. Its two local distinctions are encoded by r.
    if r.bit_count() % 2 != u:
        return 0
    return (1 + j + r) + (u - r) * 1j if weighted else 1


def check(n, weighted, prefix):
    words = list(product(range(4), repeat=n))
    records = [(v,) * n for v in (0, 1)]
    if n == 3:
        # Each reader shares a distinct bit with one unread even-parity knot.
        records = [u for u in product((0, 1), repeat=n) if sum(u) % 2 == 0]
    joint = {}
    for u in records:
        for word in words:
            amp = 1
            for j, r in enumerate(word):
                amp *= readers_given(u[j], j, r, weighted)
            joint[u, word] = amp
    checked = 0
    for a, b in islice(product(words, repeat=2), prefix):
        direct = sum(joint[u, a] * joint[u, b].conjugate() for u in records)
        mixture = 0
        for u in records:
            term = 1
            for j in range(n):
                term *= readers_given(u[j], j, a[j], weighted)
                term *= readers_given(u[j], j, b[j], weighted).conjugate()
            mixture += term
        assert direct == mixture
        checked += 1
    if not weighted and n == 2:
        mass = sum(abs(z) ** 2 for z in joint.values())
        both_even = sum(abs(z) ** 2 for (_, w), z in joint.items()
                        if all(r.bit_count() % 2 == 0 for r in w[:2]))
        assert both_even == mass / 2
    return checked


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    for n in (1, 2, 3):
        start = perf_counter()
        cells = sum(check(n, weighted, 8 if args.pilot else None)
                    for weighted in (False, True))
        print(f"{n} readers, {cells} entries, {perf_counter() - start:.6f} s")
