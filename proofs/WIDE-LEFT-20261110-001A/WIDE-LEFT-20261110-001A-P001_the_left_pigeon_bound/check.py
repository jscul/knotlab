"""Checks for WIDE-LEFT-20261110-001A: the numbers behind the density count (D) and the star packing.

    python3 -B check.py          verify against result.json
    python3 -B check.py --write  write result.json from a fresh run

1. The proof's bracket: for l = 20 to 200, 1/(8l(3l + 2)) - (l + 2)/(32 l^3) - 1/(128 l^4) - 2/2^l >= 0.005 / l^2.
2. (D) in floating point, exactly (term by term) for l = 20 to 32 and by the proof's sequential bound for l = 33 to 80, at k = floor(n/(64 l^3)) and the largest admissible h: the log bound
   log e_k(non-spare rows) - log C(v + k, k) + h k^2/(v + k) is at least k * 0.005 / l^2 - 1, and the side conditions hold
   (2l k(4h + 2) <= n + 1, 4h + 1 >= 2h + l + 1, 2k(l + 1) <= n, k(l + 2) <= 2n, h(k + 1) + 1 <= v).
3. Star packing: greedy choice of centres at pairwise distance >= 3 finds 2k hole centres in {0,1}^l and k pigeon centres in {0,1}^(l+1),
   by the counting bound n / (1 + l + C(l, 2)) >= 2k, l = 20 to 80; and by explicit greedy search for l = 8 to 14 with k = 4."""
import hashlib
import itertools
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = {}
T0 = time.time()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)
    if not ok:
        print(json.dumps(info, indent=1, default=str)[:3000])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def log_binom(a, b):
    return math.lgamma(a + 1) - math.lgamma(b + 1) - math.lgamma(a - b + 1)


def log_ek(m, a, n, b, k):
    terms = [log_binom(m, i) + i * math.log(a) + log_binom(n, k - i) + (k - i) * math.log(b) for i in range(max(0, k - n), min(m, k) + 1)]
    top = max(terms)
    return top + math.log(sum(math.exp(t - top) for t in terms))


def greedy_centres(width, count):
    chosen = []
    for c in range(1 << width):
        if all(bin(c ^ d).count("1") >= 3 for d in chosen):
            chosen.append(c)
            if len(chosen) == count:
                return chosen
    return chosen


def main():
    write = "--write" in sys.argv
    man = json.loads((HERE / "manifest.json").read_text())
    bound = man.get("parent_bindings", {})
    check("0_dependencies_bound", bool(bound) and all(sha(ROOT / p) == h for p, h in bound.items()), bound)

    worst = math.inf
    for l in range(20, 201):
        n = 2.0 ** l
        br = 1 / (8 * l * (3 * l + 2)) - (l + 2) / (32 * l ** 3) - 1 / (128 * l ** 4) - 2 / n
        worst = min(worst, br * l * l)
    check("1_bracket_at_least_0.005_over_l2", worst >= 0.005, {"smallest bracket times l^2, l = 20 to 200": round(worst, 6)})

    ok2, rows = True, []
    for l in range(20, 81):
        n = 2 ** l
        k = n // (64 * l ** 3)
        h = math.floor(((n + 1) / (2 * l * k) - 2) / 4)
        v = 2 * n * l + n * (l + 1)
        side = (2 * l * k * (4 * h + 2) <= n + 1 and 4 * h + 1 >= 2 * h + l + 1 and 2 * k * (l + 1) <= n and k * (l + 2) <= 2 * n
                and h * (k + 1) + 1 <= v)
        if l <= 32:
            log_ratio = log_ek(2 * n - k * (l + 2), l, n - 2 * k * (l + 1), l + 1, k) - log_binom(v + k, k)
        else:                             # the proof's sequential bound, for k too large to sum term by term
            s = k * (l + 2) * l + 2 * k * (l + 1) * (l + 1)
            log_ratio = -(2 * k * s + (l + 2) * k * (k - 1) + 2 * k) / v
        val = log_ratio + h * k * k / (v + k)
        ok2 &= side and val >= k * 0.005 / l ** 2 - 1
        rows.append({"l": l, "k": k, "h": h, "log bound": round(val, 3), "k * 0.005 / l^2": round(k * 0.005 / l ** 2, 3)})
    check("2_density_count", ok2, {"first": rows[0], "l = 30": rows[10], "l = 60": rows[40], "last": rows[-1]})

    ok3 = True
    for l in range(20, 81):
        n = 2 ** l
        k = n // (64 * l ** 3)
        ok3 &= n // (1 + l + math.comb(l, 2)) >= 2 * k and (2 * n) // (2 + l + math.comb(l + 1, 2)) >= k
    small = {}
    for l in range(8, 15):
        hc = greedy_centres(l, 8)
        pc = greedy_centres(l + 1, 4)
        small[l] = (len(hc), len(pc))
        ok3 &= len(hc) == 8 and len(pc) == 4
    check("3_star_packing", ok3, {"greedy centres found (holes, pigeons), k = 4": small})

    allok = all(v["pass"] for v in OUT.values())
    result = {"ticket": "WIDE-LEFT-20261110-001A", "checks": OUT, "status": "passed" if allok else "failed",
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
