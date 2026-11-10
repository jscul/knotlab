"""Checks for AUDIT-LEFT-20261110-001A (the left-pigeon bound re-derived).

Written independently of WIDE-LEFT-20261110-001A's check.py. Run with the workspace venv (mpmath):
    .venv/bin/python -B proofs/AUDIT-LEFT-20261110-001A/AUDIT-LEFT-20261110-001A-P001_the_left_pigeon_bound_audited/check.py
1. The bracket of the density count times l^2 is increasing for l >= 3 and at least 0.005 from l = 20 (exact rationals).
2. Parameters, side conditions and the density count for l = 20..200 at 80-digit precision; exact dim U_0 for l = 20..30.
3. Spare stars from a linear code of distance 3 (distance checked by enumeration for l <= 12; counts for l = 20..1000).
4. Consistency with the degree cap of RES-XOR-COUNT-20261110-001A (density form <= exp(d^2/(36 v))).
5. Minimum parity decision trees (tree-like Res(xor)) at n = 2, by exhaustive search (pdt.c).
"""
import itertools, json, math, subprocess, sys
from fractions import Fraction as Q
from pathlib import Path
import mpmath as mp

HERE = Path(__file__).resolve().parent
mp.mp.dps = 80
out = {}

# 1. bracket b(l) = 1/(8l(3l+2)) - (l+2)/(32 l^3) - 1/(128 l^4) - 2/2^l
def bracket_l2(l):
    return Q(l, 8 * (3 * l + 2)) - Q(l + 2, 32 * l) - Q(1, 128 * l * l) - Q(2 * l * l, 2 ** l)
vals = [bracket_l2(l) for l in range(3, 1001)]
assert all(b < a for b, a in zip(vals, vals[1:])), "not increasing"
out["1_bracket"] = {"increasing from l = 3 to 1000": True, "value at l = 20": float(bracket_l2(20)),
                    "limit 1/24 - 1/32": 1 / 24 - 1 / 32, "at least 0.005 from l = 20": float(bracket_l2(20)) >= 0.005}
assert bracket_l2(20) >= Q(5, 1000) and bracket_l2(19) < Q(5, 1000)

# 2. the density count
def params(l):
    n = 2 ** l
    k = n // (64 * l ** 3)
    h = ((n + 1) // (2 * l * k) - 2) // 4          # largest h with 2lk(4h+2) <= n+1
    assert 2 * l * k * (4 * h + 2) <= n + 1 < 2 * l * k * (4 * (h + 1) + 2)
    v = n * (3 * l + 1)
    w = l + 1
    D = max(2 * h + w, 4 * h + 1)
    B = k * (D + 1)
    s = k * (l + 2) * l + 2 * k * (l + 1) ** 2      # variables in the stars: k pigeon stars, 2k hole stars
    return n, k, h, v, w, D, B, s
rows = {}
first_nontrivial = None
for l in range(20, 201):
    n, k, h, v, w, D, B, s = params(l)
    assert k >= 1 and h >= 1
    assert D == 4 * h + 1 and 2 * l * B - 1 <= n and B >= 2 and k <= B, l     # D1 and the reduction's conditions
    assert h * (k + 1) + 1 <= v                                                # the criterion's condition
    assert 2 * k * (l + 1) <= n and k * (l + 2) <= 2 * n and n >= 2 * k + 1   # the spare-row lemma's conditions
    # log density lower bound: e_k >= prod_{i<k} (v - s - i(l+1)) / k!, k! C(v+k,k) = prod_{i=1..k} (v+i)
    c, d = mp.mpf(v - s), mp.mpf(l + 1)
    logdelta = k * mp.log(d) + mp.loggamma(c / d + 1) - mp.loggamma(c / d - k + 1) - mp.loggamma(v + k + 1) + mp.loggamma(v + 1)
    gain = mp.mpf(h) * k * k / (v + k)
    total = logdelta + gain
    target = mp.mpf(5) / 1000 * k / l ** 2
    assert total >= target, (l, total, target)
    logJ = mp.log(2 * n * n * (l + 1))
    if first_nontrivial is None and target - 1 > logJ:
        first_nontrivial = l
    if l in (20, 21, 25, 30, 40, 47, 48, 50, 60, 100, 200):
        rows[l] = {"k": k, "h": h, "B": B, "log density >=": float(logdelta), "gain": float(gain), "left side": float(total),
                   "0.005 k / l^2": float(target), "ratio": float(total / target), "log |J|": float(logJ)}
out["2_density"] = {"rows": rows, "first l with exp(0.005 k/l^2 - 1) > |J|": first_nontrivial}
# exact dim U_0 for small l (truncated product of (1 + l x)^r (1 + (l+1) x)^q)
exact = {}
for l in range(20, 31):
    n, k, h, v, w, D, B, s = params(l)
    r = 2 * n - k * (l + 2)            # pigeon rows outside the stars
    q = n - 2 * k * (l + 1)            # hole rows outside the stars
    dim = 0
    for j in range(k + 1):
        dim += sum(math.comb(r, a) * l ** a * math.comb(q, j - a) * (l + 1) ** (j - a) for a in range(j + 1))
    logdens = mp.log(dim) - mp.log(math.comb(v + k, k))
    exact[l] = {"k": k, "exact log density": float(logdens), "exact left side": float(logdens + mp.mpf(h) * k * k / (v + k)),
                "0.005 k / l^2": float(mp.mpf(5) / 1000 * k / l ** 2)}
    assert logdens + mp.mpf(h) * k * k / (v + k) >= mp.mpf(5) / 1000 * k / l ** 2
out["2_exact_small_l"] = exact

# 3. spare stars from a linear code with distance 3: parity checks = l distinct nonzero columns in F_2^r
def code_size(length):
    r = 1
    while 2 ** r - 1 < length:
        r += 1
    return 2 ** (length - r), r
def check_distance(length):
    size, r = code_size(length)
    cols = list(range(1, length + 1))                   # distinct nonzero r-bit columns
    words = [x for x in range(2 ** length) if not any(bin(x & sum(((c >> b) & 1) << i for i, c in enumerate(cols))).count("1") % 2 for b in range(r))]
    assert len(words) == size
    return min(bin(a ^ b).count("1") for a, b in itertools.combinations(words, 2)) >= 3
assert all(check_distance(L) for L in range(3, 13))
for l in range(20, 1001):
    n = 2 ** l
    k = n // (64 * l ** 3)
    assert code_size(l)[0] >= 2 * k and code_size(l + 1)[0] >= k
out["3_stars"] = {"distance >= 3 checked by enumeration": "lengths 3 to 12",
                  "enough centres (2k hole, k pigeon)": "l = 20 to 1000", "hole centres at l = 20 over 2k": code_size(20)[0] / (2 * (2 ** 20 // (64 * 8000)))}

# 4. the cap: a PC refutation of degree d caps the density form at exp(d^2/(36 v)); separation at B forces d > B
cap = {}
for l in (20, 30, 47, 60, 100, 200):
    n, k, h, v, w, D, B, s = params(l)
    need = mp.sqrt(36 * v * (mp.mpf(5) / 1000 * k / l ** 2))     # degrees below this would contradict the bound
    cap[l] = {"B (refutation degree exceeds it)": B, "degree that would contradict": float(need), "B / that": float(B / need)}
    assert B > need
out["4_cap"] = cap

# 5. minimum parity decision trees at n = 2
exe = HERE / "pdt"
subprocess.run(["gcc", "-O2", "-o", str(exe), str(HERE / "pdt.c")], check=True)
names = {2: "bit PHP, 3 pigeons, 2 holes", 3: "bit PHP, 4 pigeons, 2 holes", 1: "LP_3 (n + 1 = 3 pigeons)", 0: "WLP_2 (2n = 4 pigeons)"}
pdt = {}
for kind in (2, 3, 1, 0):
    line = subprocess.run([str(exe), str(kind)], check=True, capture_output=True, text=True).stdout.split()
    f = dict(x.split("=") for x in line)
    pdt[names[kind]] = {"variables": int(f["vars"]), "clauses": int(f["clauses"]), "min leaves": int(f["min_size(leaves)"]),
                        "min depth": int(f["min_depth"])}
exe.unlink()
assert pdt[names[0]]["min leaves"] <= pdt[names[1]]["min leaves"]
out["5_min_tree_like_n2"] = pdt

out = {"status": "passed", "checks": out}                  # every assert above held
(HERE / "result.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
