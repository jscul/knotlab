"""Stress test of RES-XOR-COUNT-20261110-001 one size past what ticket A checked (research-next-steps, "Stress-Test Published Claims").

    .venv/bin/python3 -B stress_test.py    writes stress_test.json beside this file

1. Lemma 1 (Braun's criterion capped at exp(d^2 / 6v)), checked for v up to 5,000: v = 20,000 and 100,000, d up to 2v/3 on a coarse grid.
2. Lemma 3 (no stifling gadget is affine), checked on every function of at most 4 bits: on 5 bits, all 64 affine functions and 20,000
   random others, and Maj_5 2-stifled.
3. Lemma 5's ceiling one sphere past K_2: K_3 is not refuted at resolution width 4, so its width is at least 5 and its polynomial-calculus
   degree 4 (PC-COUNT-20261110-001B) is at most the width plus 1."""
import importlib.util
import json
import math
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A = ROOT / "proofs/RES-XOR-COUNT-20261110-001A/RES-XOR-COUNT-20261110-001A-P001_where_each_route_stops"
spec = importlib.util.spec_from_file_location("res_xor_a", A / "check.py")
CA = importlib.util.module_from_spec(spec)
sys.modules["res_xor_a"] = CA
spec.loader.exec_module(CA)
OUT = {}
T0 = time.time()


def record(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info, "seconds": round(time.time() - T0, 1)}
    print(("PASS " if ok else "FAIL ") + name, round(time.time() - T0), flush=True)


def main():
    worst_r, worst_d, cases = 0.0, 0.0, 0
    for v in (20000, 100000):
        for d in sorted({16, int(math.sqrt(v)), 4 * int(math.sqrt(v)), v // 100, v // 10, 2 * v // 3}):
            for h in sorted({1, 2, 3, 5, 10, 30, 100, d // 8, d // 5}):
                if h < 1:
                    continue
                for w in (3, 12, 50):
                    Dg = max(2 * h + w, 4 * h + 1)
                    kmax = (d - 1) // (Dg + 1)
                    for k in sorted({1, 2, kmax // 2, kmax}):
                        if k < 1 or k * (Dg + 1) >= d or h * (k + 1) + 1 > v:
                            continue
                        r = h * (k + 1) + 1
                        lr = CA.log_binom(v + k, k) - CA.log_binom(v - r + k, k)
                        worst_r = max(worst_r, lr / (d * d / (6 * v)))
                        worst_d = max(worst_d, (h * k * k / (v + k)) / (d * d / (36 * v)))
                        cases += 1
    record("1_lemma_1_at_v_100000", worst_r <= 1 and worst_d <= 1,
           {"cases": cases, "largest ratio to exp(d^2/6v)": round(worst_r, 4), "largest density ratio": round(worst_d, 4)})
    rng = random.Random(20261111)
    pts = CA.table(5)
    affine = []
    for c in (0, 1):
        for T in range(32):
            affine.append([c ^ (bin(T & int("".join(map(str, p)), 2)).count("1") & 1) for p in pts])
    bad = sum(CA.is_stifled(f, 5, 1) for f in affine)
    others = 0
    for _ in range(20000):
        f = [rng.randint(0, 1) for _ in range(32)]
        if CA.is_stifled(f, 5, 1) and CA.is_affine(f, 5):
            others += 1
    maj5 = [int(sum(p) > 2) for p in pts]
    record("2_lemma_3_on_5_bits", bad == 0 and others == 0 and CA.is_stifled(maj5, 5, 2),
           {"affine 1-stifled": bad, "random functions both affine and 1-stifled": others, "Maj_5 2-stifled": True})
    cls = [frozenset((v + 1) * (1 if val == 0 else -1) for v, val in f) for f in CA.S.falsifiers(3)]
    w4 = CA.resolution_refutes(cls, 4)
    pc = json.loads((ROOT / "artifacts/PC-COUNT-20261110-001B/PC-COUNT-20261110-001B-E001_small_sphere_degrees/run/result.json").read_text())
    d3 = pc["readings"]["K_3 count pc"]["degree"]
    record("3_ceiling_on_K_3", (not w4) and d3 <= 5 + 1, {"K_3 refuted at width 4": w4, "K_3 width at least": 5, "K_3 PC degree": d3})
    out = {"epic": "RES-XOR-COUNT-20261110-001", "checks": OUT, "status": "passed" if all(v["pass"] for v in OUT.values()) else "failed",
           "seconds": round(time.time() - T0, 1)}
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(out["status"], out["seconds"])


if __name__ == "__main__":
    main()
