"""Stress test of RING-LAW-20261109-001 one size past its census (research-next-steps, "Stress-Test Published Claims").

    .venv/bin/python3 -B stress_test.py    writes stress_test.json beside this file

1. H2 one size past: the 32 laws that bind to lag 6 on the square line networks of n = 4 and 5 (a parity table on one ring, a nonlinear
   table on the other), read on the square 6 x 6 line network (binding read by E002 only to n = 5).
2. H1 one size past: the same 32 laws and the 128 nonlinear laws with both rings passing, on the square 7 x 7 torus (read to 6 x 6): no
   law that sees the routing binds.
3. H3 and H4 one size past: the eight symmetric nonlinear laws on the square 7 x 7 torus and its line network: every representative
   contact needs both rings to lag 64 and every pair is on time."""
import importlib.util
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
X = ROOT / "experiments/RING-LAW-20261109-001B/RING-LAW-20261109-001B-E002_tori_then_lines"
spec = importlib.util.spec_from_file_location("run_e002", X / "run.py")
R = importlib.util.module_from_spec(spec)
sys.modules["run_e002"] = R
spec.loader.exec_module(R)
L = R.L
OUT = {}
T0 = time.time()
BINDERS = [(u, v) for u in (6, 9) for v in (1, 2, 4, 7, 8, 11, 13, 14)] + [(v, u) for u in (6, 9) for v in (1, 2, 4, 7, 8, 11, 13, 14)]


def record(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info, "seconds": round(time.time() - T0, 1)}
    print(("PASS " if ok else "FAIL ") + name, round(time.time() - T0), flush=True)
    (HERE / "stress_test.json").write_text(json.dumps({"epic": "RING-LAW-20261109-001", "checks": OUT}, indent=1) + "\n")


def main():
    with Pool(6, maxtasksperchild=1) as pool:
        r1 = dict(pool.map(R.timed_r1, [("square", 6, "lines", law) for law in BINDERS], chunksize=1))
        vals = {str(k[3]): v[0] for k, v in r1.items()}
        record("1_H2_square_6_lines", all(v == "binds to lag 6" for v in vals.values()), vals)
        laws = sorted(set(BINDERS) | {law for law in R.LAWS if not L.classify(law)["affine"] and L.classify(law)["both rings pass"]})
        r1t = dict(pool.map(R.timed_r1, [("square", 7, "torus", law) for law in laws], chunksize=1))
        binders = [k[3] for k, v in r1t.items() if v[0].startswith("binds")]
        record("2_H1_square_7_torus", not binders, {"laws read": len(laws), "laws that bind": binders})
        sel = [law for law in R.SELECTED if not L.classify(law)["affine"]]
        r23 = dict(pool.map(R.timed_r23, [("square", 7, gr, law) for gr in ("torus", "lines") for law in sel], chunksize=1))
        ok = all(v[0]["needs both rings at every lag to %d" % R.H] and v[0]["late"] == 0 for v in r23.values())
        record("3_H3_H4_square_7", ok, {"%s %s" % (k[2], k[3]): {kk: vv for kk, vv in v[0].items() if "examples" not in kk} for k, v in r23.items()})
    out = {"epic": "RING-LAW-20261109-001", "checks": OUT, "status": "passed" if all(x["pass"] for x in OUT.values()) else "failed",
           "seconds": round(time.time() - T0, 1)}
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(out["status"], out["seconds"])


if __name__ == "__main__":
    main()
