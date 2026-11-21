"""Build all fine maps from four local analyzer bits and both meter paths.

Coefficients are integers with explicit shared normalization. The only external
input is the previously recorded identification of names 28, 29 and 30.
"""
from collections import Counter
from itertools import product
from pathlib import Path
from runpy import run_path
import numpy as np


def fine_map(ax, bx, az, bz, *, reverse_a=False, reverse_b=False):
    """Eight times the data operator for these four physical analyzer bits."""
    result = np.zeros((4, 4), dtype=int)
    for data, mx, mz in product(range(4), range(2), range(2)):
        a, b = divmod(data, 2)
        last_a, last_b = a ^ mx, b ^ mx
        phase_a = a if reverse_a else last_a
        phase_b = b if reverse_b else last_b
        sign = (-1) ** (mx * (ax + bx) + mz * (az + bz + phase_a + phase_b))
        result[2 * last_a + last_b, data] += sign
    return result


def separated_probe(k):
    # Reorder the coefficients on (out_A, untouched_A) x (out_B, untouched_B).
    view = np.zeros((4, 4), dtype=int)
    for out, old in product(range(4), repeat=2):
        view[2*(out//2) + old//2, 2*(out%2) + old%2] = k[out, old]
    return view


def check_ordinary_records():
    earlier = Path(__file__).resolve().parents[1] / "ERASURE-AND-CLOSING-SIGNS-20261121-001A"
    engine = run_path(str(earlier / "ordinary_routes.py"))
    laws = engine["_canonical_ternaries"]()
    assert len(laws["parity"]["allowed"]) == 4 and len(laws["nae"]["allowed"]) == 6
    for port in range(2):
        a, b = (engine["encode"](0, q=port, keeper=k) for k in ("011", "001"))
        assert not engine["_failed_physical"](a, "nae") and not engine["_failed_physical"](b, "nae")
        mask = engine["mask"](engine["HOLDER"])
        assert a & mask == b & mask and a != b
    print("Both ternary laws pass K1–K3; at both ports a not-all-equal holder cannot distinguish 011 from 001.")


def main():
    x = np.array([[0, 1], [1, 0]])
    z = np.diag([1, -1])
    j = x @ z
    one = np.eye(4, dtype=int)
    xx, zz, m = np.kron(x, x), np.kron(z, z), -np.kron(j, j)
    assert np.array_equal(xx @ zz @ m, -one)
    kept = Counter()
    third = Counter()
    for ax, bx, az, bz in product(range(2), repeat=4):
        sx, sz = (-1)**(ax + bx), (-1)**(az + bz)
        k = fine_map(ax, bx, az, bz)
        four_q = (one + sx*xx) @ (one + sz*zz)
        assert np.array_equal(k, four_q)  # K = Q/2, where 8 K = 4 Q.
        assert np.array_equal(fine_map(ax, bx, az, bz, reverse_a=True, reverse_b=True), k)
        for reverse_a, reverse_b in ((True, False), (False, True)):
            reversed_k = fine_map(ax, bx, az, bz, reverse_a=reverse_a, reverse_b=reverse_b)
            assert np.array_equal(reversed_k.T @ reversed_k, 4*one)
        assert np.array_equal(k.T @ k, 4*k)
        assert np.trace(k) == 4
        probe = separated_probe(k)
        assert np.array_equal(probe @ probe.T, 4*one)
        kept[sx, sz, -sx*sz] += 1
        for am, bm in product(range(2), repeat=2):
            sm = (-1)**(am + bm)
            trial = (one + sm*m) @ k
            allowed = sm == -sx*sz
            assert np.array_equal(trial, 2*k if allowed else 0*k)
            third[allowed] += 1
    assert sorted(kept.values()) == [4, 4, 4, 4] and third == {False: 32, True: 32}
    for sx, sz in product((-1, 1), repeat=2):
        two_px = one + sx*xx
        four_q = two_px @ (one + sz*zz)
        effect = 0*one
        # Rival: an exact first sign followed by resolving the two individual bits.
        for word in range(4):
            a, b = divmod(word, 2)
            if (-1)**(a + b) != sz:
                continue
            keep = 0*one
            keep[word, word] = 1
            two_k = keep @ two_px
            effect += two_k.T @ two_k
            assert four_q[word, word] == 2  # 1/2 squared overlap on every surviving word.
        assert np.array_equal(effect, four_q)
    print("16/16 fine maps give Q/2; four joint sign triples survive, four have zero weight.")
    print("For each sign the two local spectator probes yield four equal squared coefficients 1/4.")
    print("All 64 direct third refinements: 32 compatible fine maps and 32 zero maps.")
    print("Reversing both local orders preserves the read. Reversing only one gives effect I/16 for every record.")
    print("The one-pair destructive rival has all four ideal effects; each surviving word has overlap 1/2.")
    check_ordinary_records()


if __name__ == "__main__":
    main()
