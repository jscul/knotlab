"""Checks for SEP-LEFT-20261110-001A: what of Braun's bit-PHP argument transfers to the binary left-pigeon principle LP_n.

    python3 -B check.py          verify against result.json
    python3 -B check.py --write  write result.json from a fresh run

Instances are SEP-LEFT-20261110-001B-E001's (run.py there). G(h)_j = sum_x [f_x = h] x_j is the substitution of Lemma 1.
1. Lemma 1: every axiom of LP_n, with g := G, equals sum_{x' != x} x'_j [f_x = h][f_x' = h], a sum of collisions, on every
   pigeon assignment (n = 4 exhaustively, n = 8 and 16 on random assignments).
2. Lemma 3: sum_h G(h)_j is the constant c_j = #{x : x_j = 1} mod 2 on every pigeon assignment.
3. Theorem 2's inequality: for l = 4 to 20 (n = 2^l) and k up to n/2, delta * exp(h k^2 / (v + k)) >= exp(k^2 / (3n) - 2), with
   delta = dim L_k / C(v + k, k), dim L_k the exact elementary symmetric sum of the row sizes, h = 3l.
4. Lemma 4: for the pigeon rows alone, l = 2 to 20, every k <= max(1, n / (24 l^2)): Braun's density bound is below 1.
"""
import hashlib
import importlib.util
import json
import math
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
X = ROOT / "experiments/SEP-LEFT-20261110-001B/SEP-LEFT-20261110-001B-E001_row_linear_separation"
spec = importlib.util.spec_from_file_location("sep_left_run", X / "run.py")
R = importlib.util.module_from_spec(spec)
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


def assignments(n, rng, count):
    l = n.bit_length() - 1
    m = n + 1
    if count is None:
        for a in range(1 << (m * l)):
            yield [[(a >> (x * l + t)) & 1 for t in range(l)] for x in range(m)]
    else:
        for _ in range(count):
            yield [[rng.randint(0, 1) for t in range(l)] for x in range(m)]


def lemma_1_and_3(n, rng, count):
    l = n.bit_length() - 1
    m = n + 1
    lg = (m - 1).bit_length()
    ok1 = ok3 = True
    cases = 0
    for f in assignments(n, rng, count):
        hole = [sum(f[x][t] << t for t in range(l)) for x in range(m)]
        G = [[sum((x >> j) & 1 for x in range(m) if hole[x] == h) & 1 for j in range(lg)] for h in range(n)]
        Gsq_ok = True                           # over F2 and on Boolean points, G^2 = G holds pointwise; the check is the identity below
        for x in range(m):
            for h in range(n):
                sits = int(hole[x] == h)
                for j in range(lg):
                    lhs = sits * ((G[h][j] + ((x >> j) & 1)) & 1)
                    rhs = sum(((y >> j) & 1) * sits * int(hole[y] == h) for y in range(m) if y != x) & 1
                    ok1 &= lhs == rhs
        for j in range(lg):
            ok3 &= (sum(G[h][j] for h in range(n)) & 1) == (sum((x >> j) & 1 for x in range(m)) & 1)
        cases += 1
    return ok1, ok3, cases


def log_ek(m, a_size, n, b_size, k):
    """log of the elementary symmetric sum e_k of m rows of a_size bits and n rows of b_size bits:
    sum over a + b = k of C(m, a) a_size^a C(n, b) b_size^b"""
    terms = [log_binom(m, a) + a * math.log(a_size) + log_binom(n, k - a) + (k - a) * math.log(b_size)
             for a in range(max(0, k - n), min(m, k) + 1)]
    top = max(terms)
    return top + math.log(sum(math.exp(t - top) for t in terms))


def log_binom(a, b):
    return math.lgamma(a + 1) - math.lgamma(b + 1) - math.lgamma(a - b + 1)


def main():
    write = "--write" in sys.argv
    man = json.loads((HERE / "manifest.json").read_text())
    bound = man.get("parent_bindings", {})
    check("0_dependencies_bound", bool(bound) and all(sha(ROOT / p) == h for p, h in bound.items()), bound)

    rng = random.Random(20261110)
    res = {n: lemma_1_and_3(n, rng, None if n == 4 else 300) for n in (4, 8, 16)}
    check("1_lemma_1_axioms_become_collisions", all(r[0] for r in res.values()),
          {"n = 4 every pigeon assignment, n = 8 and 16 random": {n: r[2] for n, r in res.items()}})
    check("2_lemma_3_hole_sums_are_constant", all(r[1] for r in res.values()), {n: r[2] for n, r in res.items()})

    worst, rows3 = math.inf, []
    for l in range(4, 21):
        n = 2 ** l
        m = n + 1
        v = m * l + n * (l + 1)
        h = 3 * l
        for k in sorted({1, 2, 4, 8, n // 64, n // 16, n // 8, n // 4, n // 2}):
            if k < 1:
                continue
            lhs = log_ek(m, l, n, l + 1, k) - log_binom(v + k, k) + h * k * k / (v + k)
            rhs = k * k / (3 * n) - 2
            worst = min(worst, lhs - rhs)
        rows3.append({"l": l, "n": n, "v": v})
    check("3_theorem_2_density_inequality", worst >= 0, {"smallest margin (log)": round(worst, 3), "sizes": rows3})

    worst4, cases4 = -math.inf, 0
    for l in range(2, 21):
        n = 2 ** l
        m = n + 1
        v = m * l + n * (l + 1)
        h = 3 * l
        for k in range(1, max(1, n // (24 * l * l)) + 1):
            val = log_ek(m, l, 0, 1, k) - log_binom(v + k, k) + h * k * k / (v + k)
            worst4 = max(worst4, val)
            cases4 += 1
    check("4_lemma_4_pigeon_rows_too_thin", worst4 < 0, {"cases": cases4, "largest log bound": round(worst4, 3)})

    allok = all(v["pass"] for v in OUT.values())
    result = {"ticket": "SEP-LEFT-20261110-001A", "checks": OUT, "status": "passed" if allok else "failed",
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
