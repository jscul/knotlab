"""Stress test of HOLE-SEP-20261110-001 one size past (research-next-steps, "Stress-Test Published Claims").

    .venv/bin/python3 -B stress_test.py    writes stress_test.json beside this file

1. P1 one size past: dim K_1 = (l + 1)^2 = 36 at n = 32 (read to n = 16).
2. The post-hoc reading of the killed family, made before this run: the kernel fraction at degree 2 follows (l + 1)^2 * k / v (v the
   number of variables), with the observed values 0.73, 0.49 and 0.32 at n = 4, 8, 16 against 0.82, 0.54 and 0.34. Prediction, written
   before this run: at n = 32, k = 2 the fraction lies between 0.15 and 0.21 ((l + 1)^2 k / v = 0.20)."""
import importlib.util
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
X = ROOT / "experiments/HOLE-SEP-20261110-001B/HOLE-SEP-20261110-001B-E001_decoder_kernel"
spec = importlib.util.spec_from_file_location("hole_sep_run", X / "run.py")
R = importlib.util.module_from_spec(spec)
sys.modules["hole_sep_run"] = R
spec.loader.exec_module(R)
OUT = {}
T0 = time.time()


def record(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info, "seconds": round(time.time() - T0, 1)}
    print(("PASS " if ok else "FAIL ") + name, round(time.time() - T0), flush=True)
    (HERE / "stress_test.json").write_text(json.dumps({"epic": "HOLE-SEP-20261110-001", "checks": OUT}, indent=1) + "\n")


def main():
    r1, S = R.kernel_dim(32, 1)
    ok, cnt = R.known_elements_check(S)
    record("1_P1_at_n_32", r1["dim K_k"] == 36 and ok, {"dim K_1": r1["dim K_k"], "known elements in K_1": ok, "count": cnt})
    r2, _ = R.kernel_dim(32, 2)
    v = 33 * 5 + 32 * 6
    record("2_kernel_fraction_at_n_32_k_2", 0.15 <= r2["kernel fraction"] <= 0.21,
           {"reading": r2, "(l + 1)^2 k / v": round(36 * 2 / v, 4)})
    out = {"epic": "HOLE-SEP-20261110-001", "checks": OUT, "status": "passed" if all(x["pass"] for x in OUT.values()) else "failed",
           "seconds": round(time.time() - T0, 1)}
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(out["status"], out["seconds"])


if __name__ == "__main__":
    main()
