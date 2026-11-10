"""Stress test for AUDIT-LEFT-20261110-001, one size past each check of AUDIT-LEFT-20261110-001A's check.py.

Run with the workspace venv: .venv/bin/python -B research/AUDIT-LEFT-20261110-001/stress_test.py
1. The density count's exponent against 0.005 k / l^2 for l = 201..1000 (checked to 200), at 120 digits.
2. Exact dim U_0 for l = 31, 32 (checked to 30).
3. The code construction's distance by enumeration at lengths 13 and 14 (checked to 12).
"""
import itertools, json, math
from pathlib import Path
import mpmath as mp

mp.mp.dps = 120
out = {}
def params(l):
    n = 2 ** l
    k = n // (64 * l ** 3)
    h = ((n + 1) // (2 * l * k) - 2) // 4
    assert 2 * l * k * (4 * h + 2) <= n + 1 < 2 * l * k * (4 * (h + 1) + 2)
    v = n * (3 * l + 1)
    s = k * (l + 2) * l + 2 * k * (l + 1) ** 2
    return n, k, h, v, s
worst = None
for l in range(201, 1001):
    n, k, h, v, s = params(l)
    B = k * (4 * h + 2)
    assert 2 * h >= l and 2 * l * B - 1 <= n and h * (k + 1) + 1 <= v and n >= 2 * k + 1
    c, d = mp.mpf(v - s), mp.mpf(l + 1)
    logdelta = k * mp.log(d) + mp.loggamma(c / d + 1) - mp.loggamma(c / d - k + 1) - mp.loggamma(v + k + 1) + mp.loggamma(v + 1)
    ratio = (logdelta + mp.mpf(h) * k * k / (v + k)) / (mp.mpf(5) / 1000 * k / l ** 2)
    assert ratio >= 1, l
    worst = ratio if worst is None or ratio < worst else worst
out["1_density_l_201_to_1000"] = {"pass": True, "smallest ratio to 0.005 k/l^2": float(worst)}
exact = {}
for l in (31, 32):
    n, k, h, v, s = params(l)
    r, q = 2 * n - k * (l + 2), n - 2 * k * (l + 1)
    A, Bq = [1], [1]                     # A[a] = C(r, a) l^a, Bq[b] = C(q, b) (l+1)^b, built incrementally
    for i in range(k):
        A.append(A[-1] * (r - i) * l // (i + 1))
        Bq.append(Bq[-1] * (q - i) * (l + 1) // (i + 1))
    pre = list(itertools.accumulate(Bq))
    dim = sum(A[a] * pre[k - a] for a in range(k + 1))
    left = mp.log(dim) - mp.log(math.comb(v + k, k)) + mp.mpf(h) * k * k / (v + k)
    exact[l] = {"k": k, "ratio": float(left / (mp.mpf(5) / 1000 * k / l ** 2))}
    assert left >= mp.mpf(5) / 1000 * k / l ** 2
out["2_exact_l_31_32"] = exact
def distance_ok(L):
    r = 1
    while 2 ** r - 1 < L:
        r += 1
    cols = list(range(1, L + 1))
    masks = [sum(((c >> b) & 1) << i for i, c in enumerate(cols)) for b in range(r)]
    words = [x for x in range(2 ** L) if all(bin(x & m).count("1") % 2 == 0 for m in masks)]
    assert len(words) == 2 ** (L - r)
    return min(bin(w).count("1") for w in words if w) >= 3      # linear code: distance = least nonzero weight
out["3_code_distance_13_14"] = {L: distance_ok(L) for L in (13, 14)}
assert all(out["3_code_distance_13_14"].values())
Path(__file__).with_name("stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
