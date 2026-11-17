"""SLOW-LOOP-R1 task 4: the comparator. An independent Novelty+ (referee_sls_wherenext_copy.c, the WHERE-NEXT referee's own
engine for unsigned NAE knots, copied unchanged: own occurrence lists, own RNG, exact score ties broken uniformly) at the
study's re-tuned Novelty+ settings (retuned.json), 5 runs on each of the first 20 test instances (seeds 7,100,000-7,100,019)
of local-w10-3200 and rand-3200. Instances from the study's generator (slow_loop.planted, read-only use). Every final
state is checked on the knots by the referee's own code. Compared with the study's NOV arm on the same instances
(test/results.jsonl): the median over instances of each instance's geometric-mean flips, the ratio with a paired
bootstrap 99% interval, and the per-instance rank correlation. Output: referee_task4_comparator.json.
"""
from __future__ import annotations

import ctypes
import json
import os
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
EXP = os.path.join(ROOT, "experiments/SLOW-LOOP-20261117-001A/SLOW-LOOP-20261117-001A-E001_slow_loop")
ART = os.path.join(ROOT, "artifacts/SLOW-LOOP-20261117-001A/SLOW-LOOP-20261117-001A-E001_slow_loop")
SO = "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/866db0bb-326b-5add-835e-78bf03179706/scratchpad/build/referee_sls.so"
os.environ.setdefault("SLOW_LOOP_BUILD", os.path.dirname(SO))
sys.path.insert(0, EXP)
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402

import referee_oracle as O  # noqa: E402
import slow_loop as S  # noqa: E402  (generator only)

if not os.path.exists(SO):
    import subprocess
    os.makedirs(os.path.dirname(SO), exist_ok=True)
    subprocess.run(["gcc", "-O2", "-fPIC", "-shared", "-o", SO, os.path.join(HERE, "referee_sls_wherenext_copy.c"), "-lm"],
                   check=True)
L = ctypes.CDLL(SO)
i32p = np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS")
f64p = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
u8p = np.ctypeslib.ndpointer(dtype=np.uint8, flags="C_CONTIGUOUS")
L.ref_run.argtypes = [ctypes.c_int, ctypes.c_int, i32p, ctypes.c_int, f64p, ctypes.c_uint64, ctypes.c_int64, f64p,
                      ctypes.c_void_p, u8p]
L.ref_run.restype = ctypes.c_int
NOVPLUS = 2
CELLS = {"local-w10-3200": ("local", 4.0, 10, 3200, 2 * 10**8), "rand-3200": ("rand", 2.1, 10, 3200, 2 * 10**8)}


def gm(v):
    return float(np.exp(np.mean(np.log(v))))


def main():
    tun = json.load(open(os.path.join(ART, "retuned.json")))
    stored = {}
    for line in open(os.path.join(ART, "test", "results.jsonl")):
        x = json.loads(line).get("result")
        if x and x["arm"] == "NOV" and x["cell"] in CELLS:
            stored[(x["cell"], x["seed"])] = x["runs"]
    out = {}
    t0 = time.time()
    for cell, (fam, a, w, n, cap) in CELLS.items():
        prm = np.array(list(tun[cell]["NOV"]) + [0.0, 0.0], dtype=np.float64)
        mine, theirs, unsolved, bad = [], [], 0, 0
        for i in range(20):
            seed = 7_100_000 + i
            inst = S.planted(fam, n, a, seed, w=w)
            kv = np.ascontiguousarray(inst.knots.reshape(-1), dtype=np.int32)
            fl = []
            for r in range(5):
                o = np.zeros(6)
                x = np.zeros(n, np.uint8)
                L.ref_run(n, inst.m, kv, NOVPLUS, prm, ctypes.c_uint64(990_000_000 + 1000 * i + r), cap, o, None, x)
                if not o[1]:
                    unsolved += 1
                elif not O.sat_rows(x, inst.knots)[0]:
                    bad += 1
                fl.append(max(1.0, o[0]))
            mine.append(gm(fl))
            theirs.append(gm([max(1, q["flips"]) for q in stored[(cell, seed)]]))
        mine, theirs = np.array(mine), np.array(theirs)
        rng = np.random.default_rng(4)
        idx = rng.integers(0, 20, (10000, 20))
        rb = np.median(mine[idx], 1) / np.median(theirs[idx], 1)
        rk = lambda v: np.argsort(np.argsort(v))
        out[cell] = {"setting": tun[cell]["NOV"], "referee_median_flips": float(np.median(mine)),
                     "study_NOV_median_flips": float(np.median(theirs)),
                     "ratio_referee_over_study": float(np.median(mine) / np.median(theirs)),
                     "ratio_ci99": [float(np.quantile(rb, 0.005)), float(np.quantile(rb, 0.995))],
                     "spearman_per_instance": float(np.corrcoef(rk(mine), rk(theirs))[0, 1]),
                     "referee_unsolved_runs": unsolved, "referee_states_failing_check": bad,
                     "per_instance": {"referee": mine.tolist(), "study": theirs.tolist()}}
    out["seconds"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "referee_task4_comparator.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: ({kk: vv for kk, vv in v.items() if kk != "per_instance"} if isinstance(v, dict) else v)
                      for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    main()
