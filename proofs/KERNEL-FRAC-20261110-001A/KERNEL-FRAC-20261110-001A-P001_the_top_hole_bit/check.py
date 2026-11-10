"""Checks for KERNEL-FRAC-20261110-001A: the top hole bit closes the decoder route for bit LeftPigeon (n + 1 pigeons).

    python3 -B check.py          verify against result.json
    python3 -B check.py --write  write result.json from a fresh run

1. tau~(g_h,l) = X_n,h (only pigeon n = 100...0 has the top code bit) and tau~(g_h,l g_h',l) = 0 modulo the unary ideal, for every pair of
   holes, n = 4, 8, 16, 32.
2. The cap: for l = 2 to 30, n = 2^l, every k up to n/2 on a grid, and the largest accuracy h allowed by Theorem (R) (2l k(4h + 2) <= n + 1),
   the most Braun's criterion can certify through the decoder, (low_k / C(v + k, k)) * exp(h k^2 / (v + k)), is at most 5.2, where
   low_k counts the row-linear monomials of degree <= k with at most one top hole bit (exact integers for l <= 12, the proof's bound
   (1 + nk/v) exp(-(k - 1) n / (v + k)) beyond)."""
import hashlib
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HX = ROOT / "experiments/HOLE-SEP-20261110-001B/HOLE-SEP-20261110-001B-E001_decoder_kernel"
spec = importlib.util.spec_from_file_location("hole_sep_run", HX / "run.py")
R = importlib.util.module_from_spec(spec)
sys.modules["hole_sep_run"] = R
spec.loader.exec_module(R)
OUT = {}
T0 = time.time()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)
    if not ok:
        print(json.dumps(info, indent=1, default=str)[:3000])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def in_span(v, basis):
    while v:
        b = v.bit_length() - 1
        if b not in basis:
            return False
        v ^= basis[b]
    return True


def low_exact(n, k):
    l = n.bit_length() - 1
    m = n + 1
    low = 0
    for d in range(k + 1):
        for b in range(0, min(n, d) + 1):
            a = d - b
            if a > m:
                continue
            low += math.comb(m, a) * l ** a * math.comb(n, b) * (l ** b + (b * l ** (b - 1) if b >= 1 else 0))
    return low


def log_binom(a, b):
    return math.lgamma(a + 1) - math.lgamma(b + 1) - math.lgamma(a - b + 1)


def main():
    write = "--write" in sys.argv
    man = json.loads((HERE / "manifest.json").read_text())
    bound = man.get("parent_bindings", {})
    check("0_dependencies_bound", bool(bound) and all(sha(ROOT / p) == h for p, h in bound.items()), bound)
    ok1, cases = True, 0
    for n in (4, 8, 16, 32):
        S = R.Space(n, 2)
        basis = {}
        for v in S.relations():
            R.insert(basis, v)
        l = S.l
        for h in range(n):
            ok1 &= S.image([("g", h, l)]) == 1 << S.index[frozenset({(n, h)})]
            for h2 in range(h + 1, n):
                ok1 &= in_span(S.image([("g", h, l), ("g", h2, l)]), basis)
                cases += 1
    check("1_top_bit_is_one_pigeon", ok1, {"pairs of holes": cases, "n": [4, 8, 16, 32]})
    worst, rows = 0.0, []
    for l in range(2, 31):
        n = 2 ** l
        m = n + 1
        v = m * l + n * (l + 1)
        for k in sorted({1, 2, 3, 4, 6, 8, 12, 16, 32, 64, 128, 256, 1024, n // 64, n // 16, n // 4, n // 2}):
            if k < 1 or k > n // 2:
                continue
            h = math.floor(((n + 1) / (2 * l * k) - 2) / 4)
            if h < 1:
                continue
            if l <= 12 and k <= 4096:
                log_low = math.log(low_exact(n, k))
            else:
                log_low = math.log1p(n * k / v) - (k - 1) * n / (v + k) + log_binom(v + k, k)
            val = log_low - log_binom(v + k, k) + h * k * k / (v + k)
            worst = max(worst, val)
        rows.append(l)
    check("2_the_criterion_through_the_decoder_certifies_a_constant", math.exp(worst) <= 5.2,
          {"largest certified value": round(math.exp(worst), 4), "l": [rows[0], rows[-1]]})
    allok = all(v["pass"] for v in OUT.values())
    result = {"ticket": "KERNEL-FRAC-20261110-001A", "checks": OUT, "status": "passed" if allok else "failed",
              "seconds": round(time.time() - T0, 1)}
    path = HERE / "result.json"
    if write:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote", path)
    else:
        old = json.loads(path.read_text())
        same = {k: v["pass"] for k, v in old["checks"].items()} == {k: v["pass"] for k, v in OUT.items()}
        print("matches result.json" if same else "DIFFERS from result.json")
        sys.exit(0 if same and allok else 1)


if __name__ == "__main__":
    main()
