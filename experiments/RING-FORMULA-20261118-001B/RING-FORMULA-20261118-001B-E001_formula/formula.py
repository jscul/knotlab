"""RING-FORMULA-20261118-001B: the (v, S) model for a ring of n knots (n odd) with spare distinctions, against the grown rings.

Ring knots sit at cylinder positions (a, -a), a mod n; the ring order is a -> a + (n + 1)/2 (two cylinder steps are one ring step
back).  A knot of 4 + s places carries s spare distinctions; each spare at position a0 has lifts (a0 + n k, -a0 - n k), k integer.
A junction is (v, S), v = (a, b) of height a + b >= 0 up to the shift (n, -n), S a set of lifts below v; its round is a + b + |S|."""
from math import comb


def lifts_below(a, b, a0, n):
    # k with a0 + n k <= a and -a0 - n k <= b
    lo = -((b + a0) // n)
    hi = (a - a0) // n
    return max(0, hi - lo + 1)


def spares_at(sizes, n):
    """Cylinder positions of the spare distinctions of a ring listed in ring order: ring knot i sits at cylinder position
    a = i (n + 1)/2 mod n (each ring step is (n + 1)/2 cylinder steps)."""
    out = []
    for i, s in enumerate(sizes):
        a0 = (i * (n + 1) // 2) % n
        out += [a0] * (s - 4)
    return out


def model_counts(sizes, T):
    n = len(sizes)
    sp = spares_at(sizes, n)
    c = []
    for t in range(T + 1):
        tot = 0
        for h in range(0, t + 1):
            for a in range(n):
                b = h - a
                m = sum(lifts_below(a, b, a0, n) for a0 in sp)
                tot += comb(m, t - h)
        c.append(tot)
    return c


def predicted_rate(n, j):
    """The real root > 1 of x^(n + j) = (1 + x)^j (1 if j = 0)."""
    if j == 0:
        return 1.0
    lo, hi = 1.0, 3.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if mid ** (n + j) - (1 + mid) ** j > 0:
            hi = mid
        else:
            lo = mid
    return lo
