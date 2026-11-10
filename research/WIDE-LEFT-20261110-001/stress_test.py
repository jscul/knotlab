"""Stress test of WIDE-LEFT-20261110-001 one size past (research-next-steps, "Stress-Test Published Claims").

    .venv/bin/python3 -B stress_test.py    writes stress_test.json beside this file

1. Lemma 2 (the spare-row lemma) one size past at k = 1: n = 16 and 32 (checked to 8), U_0 against the kernel, with one hole star and one
   pigeon star centred at 0, and every cube identity.
2. Lemma 2 at (16, 2) on 60 more top monomials, a second seed (60 checked with seed 20261110).
3. Lemma 3's bracket to l = 1000 (checked to 200) and its side conditions to l = 200 (checked to 80)."""
import importlib.util
import json
import math
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
X = ROOT / "experiments/WIDE-LEFT-20261110-001B/WIDE-LEFT-20261110-001B-E001_spare_rows"
spec = importlib.util.spec_from_file_location("wide_run", X / "run.py")
R = importlib.util.module_from_spec(spec)
sys.modules["wide_run"] = R
spec.loader.exec_module(R)
spec = importlib.util.spec_from_file_location("wide_finish", X / "finish.py")
F = importlib.util.module_from_spec(spec)
sys.modules["wide_finish"] = F
spec.loader.exec_module(F)
OUT = {}
T0 = time.time()


def record(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info, "seconds": round(time.time() - T0, 1)}
    print(("PASS " if ok else "FAIL ") + name, round(time.time() - T0), flush=True)


def main():
    rows = []
    ok1 = True
    for n in (16, 32):
        l = n.bit_length() - 1
        R.SPARES[(n, 1)] = (R.stars(l, [0]), R.stars(l + 1, [0]))
        r, W, E, P, hs, ps = R.q1(n, 1)
        okc, tops = R.q2(W, E, P, hs, ps, 1)
        rows.append({"n": n, "dim U_0": r["dim U_0"], "dim U_0 ∩ K_1": r["dim U_0 ∩ K_k"], "cubes": tops, "identities": okc})
        ok1 &= r["dim U_0 ∩ K_k"] == 0 and okc
    record("1_lemma_2_at_k_1_n_16_32", ok1, rows)
    r, W, E, P, hs, ps = R.q1(16, 2)
    ok2, cnt = F.q2_sample(W, E, P, hs, ps, 2, 60, 20261111)
    record("2_lemma_2_at_16_2_second_seed", ok2 and r["dim U_0 ∩ K_k"] == 0, {"cubes": cnt, "dim U_0 ∩ K_2": r["dim U_0 ∩ K_k"]})
    worst = math.inf
    for l in range(20, 1001):
        n = 2.0 ** l
        br = 1 / (8 * l * (3 * l + 2)) - (l + 2) / (32 * l ** 3) - 1 / (128 * l ** 4) - (2 / n if l < 1000 else 0)
        worst = min(worst, br * l * l)
    side = True
    for l in range(20, 201):
        n = 2 ** l
        k = n // (64 * l ** 3)
        h = (((n + 1) // (2 * l * k)) - 2) // 4
        v = 2 * n * l + n * (l + 1)
        side &= (2 * l * k * (4 * h + 2) <= n + 1 and 4 * h + 1 >= 2 * h + l + 1 and 2 * k * (l + 1) <= n and k * (l + 2) <= 2 * n
                 and h * (k + 1) + 1 <= v and k >= 1)
    record("3_lemma_3_to_l_1000", worst >= 0.005 and side, {"smallest bracket times l^2": round(worst, 6), "side conditions to l = 200": side})
    out = {"epic": "WIDE-LEFT-20261110-001", "checks": OUT, "status": "passed" if all(x["pass"] for x in OUT.values()) else "failed",
           "seconds": round(time.time() - T0, 1)}
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(out["status"], out["seconds"])


if __name__ == "__main__":
    main()
