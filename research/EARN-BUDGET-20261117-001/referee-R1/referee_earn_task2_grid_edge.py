"""EARN-BUDGET-R1 task 2: the comparator at the grid edge, on the primary cell local35-w15-3200 (local, density 3.5,
window 15, n = 3200).

The referee's own Novelty+ (referee_earn_sls_work.c: the WHERE-NEXT referee's engine plus a charged-work counter in the
studies' incidence units). Instances from the study's generator (slow_loop.planted, read-only use).
  tune  p in {0.7, 0.75, 0.8, 0.85, 0.9} x wp in {0, 0.005, 0.01} as asked, plus p in {0.775, 0.825} at the same wp (finer
        steps around the best), on 20 tuning instances (seeds 8,500,000 + i, i < 20: the study's 8 tuning instances and
        12 more from the same unused stream), 2 runs each, flip cap 2*10^7 (job.py's TUNE_CAP). Score as the study's
        choose.py: the mean over runs of log(work), an unsolved run adding log(1 + least violated count).
  test  the referee's best setting and (0.8, 0) on 20 test instances (seeds 8,100,000 + i, job.py's SEED_TEST), 3 runs each,
        cap 2*10^8: the median over instances of each instance's geometric-mean work, the paired ratio with a bootstrap
        99% interval; and the study's stored NOV arm (0.8, 0) on the same instances, as a calibration of the two engines.
Output: referee_earn_task2_grid_edge.json.
"""
from __future__ import annotations

import ctypes
import json
import math
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
EXP = os.path.join(ROOT, "experiments/EARN-BUDGET-20261117-001A/EARN-BUDGET-20261117-001A-E001_earn_budget")
ART = os.path.join(ROOT, "artifacts/EARN-BUDGET-20261117-001A/EARN-BUDGET-20261117-001A-E001_earn_budget")
BUILD = "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/866db0bb-326b-5add-835e-78bf03179706/scratchpad/build_earn"
SO = os.path.join(BUILD, "referee_earn_sls_work.so")
os.environ["SLOW_LOOP_BUILD"] = BUILD
sys.path.insert(0, EXP)
import numpy as np  # noqa: E402

import slow_loop as S  # noqa: E402  (generator only)

CELL, FAM, ALPHA, W, N = "local35-w15-3200", "local", 3.5, 15, 3200
GRID = [(p, wp) for p in (0.7, 0.75, 0.775, 0.8, 0.825, 0.85, 0.9) for wp in (0.0, 0.005, 0.01)]
ASKED = {(p, wp) for p in (0.7, 0.75, 0.8, 0.85, 0.9) for wp in (0.0, 0.005, 0.01)}
TUNE_CAP, TEST_CAP = 2 * 10**7, 2 * 10**8
_L = None


def lib():
    global _L
    if _L is None:
        if not os.path.exists(SO):
            os.makedirs(BUILD, exist_ok=True)
            subprocess.run(["gcc", "-O2", "-fPIC", "-shared", "-o", SO, os.path.join(HERE, "referee_earn_sls_work.c"),
                            "-lm"], check=True)
        L = ctypes.CDLL(SO)
        i32p = np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS")
        f64p = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
        u8p = np.ctypeslib.ndpointer(dtype=np.uint8, flags="C_CONTIGUOUS")
        L.ref_run.argtypes = [ctypes.c_int, ctypes.c_int, i32p, ctypes.c_int, f64p, ctypes.c_uint64, ctypes.c_int64, f64p,
                              ctypes.c_void_p, u8p]
        _L = L
    return _L


_INST = {}


def inst(seed):
    if seed not in _INST:
        _INST[seed] = S.planted(FAM, N, ALPHA, seed, w=W)
    return _INST[seed]


def one(job):
    """job = (p, wp, seed, run, cap) -> dict(work, flips, solved, minviol, ok)."""
    p, wp, seed, r, cap = job
    I = inst(seed)
    kv = np.ascontiguousarray(I.knots.reshape(-1), dtype=np.int32)
    o = np.zeros(7)
    x = np.zeros(N, np.uint8)
    rs = (seed * 1_000_003 + r * 7919 + int(round(p * 1000)) * 31 + int(round(wp * 10000))) & (2**64 - 1)
    lib().ref_run(N, I.m, kv, 2, np.array([p, wp, 0.0, 0.0]), ctypes.c_uint64(rs), cap, o, None, x)
    s = (x[I.knots].astype(np.int64)).sum(axis=1)
    ok = bool(np.all((s == 1) | (s == 2))) if o[1] else None
    return {"p": p, "wp": wp, "seed": seed, "run": r, "work": float(o[6]), "flips": float(o[0]), "solved": bool(o[1]),
            "minviol": int(o[2]), "ok": ok}


def score(rr):
    s = math.log(rr["work"])
    if not rr["solved"]:
        s += math.log1p(max(0, rr["minviol"]))
    return s


def gm(v):
    return float(np.exp(np.mean(np.log(v))))


def main():
    from multiprocessing import Pool
    t0 = time.time()
    tune_seeds = [8_500_000 + i for i in range(20)]
    jobs = [(p, wp, s, r, TUNE_CAP) for (p, wp) in GRID for s in tune_seeds for r in range(2)]
    with Pool(8) as pool:
        tr = pool.map(one, jobs, chunksize=2)
    table = {}
    for (p, wp) in GRID:
        rows = [x for x in tr if (x["p"], x["wp"]) == (p, wp)]
        sc8 = [score(x) for x in rows if x["seed"] < 8_500_008]  # the study's 8 tuning instances
        table[f"[{p}, {wp}]"] = {"score_20x2": float(np.mean([score(x) for x in rows])), "score_study8x2": float(np.mean(sc8)),
                                 "unsolved": sum(not x["solved"] for x in rows),
                                 "median_inst_gm_work": float(np.median([gm([x["work"] for x in rows if x["seed"] == s])
                                                                         for s in tune_seeds])),
                                 "asked": (p, wp) in ASKED}
    best = min(table, key=lambda k: table[k]["score_20x2"])
    best_asked = min((k for k in table if table[k]["asked"]), key=lambda k: table[k]["score_20x2"])
    bp = tuple(json.loads(best))
    t1 = time.time()
    test_seeds = [8_100_000 + i for i in range(20)]
    settings = [bp] if bp == (0.8, 0.0) else [bp, (0.8, 0.0)]
    jobs = [(p, wp, s, r, TEST_CAP) for (p, wp) in settings for s in test_seeds for r in range(3)]
    with Pool(8) as pool:
        te = pool.map(one, jobs, chunksize=1)
    stored = {}
    for line in open(os.path.join(ART, "test", "results.jsonl")):
        x = json.loads(line).get("result")
        if x and x["cell"] == CELL and x["arm"] in ("NOV", "E") and x["seed"] in test_seeds:
            stored[(x["arm"], x["seed"])] = x["runs"]
    tun = json.load(open(os.path.join(ART, "retuned.json")))
    G = {st: np.array([gm([x["work"] for x in te if (x["p"], x["wp"]) == st and x["seed"] == s]) for s in test_seeds])
         for st in settings}
    study_nov = np.array([gm([q["work"] for q in stored[("NOV", s)]]) for s in test_seeds])
    study_E = np.array([gm([q["work"] for q in stored[("E", s)]]) for s in test_seeds])
    E_fast_share = float(np.median([q["work_fast"] / q["work"] for s in test_seeds for q in stored[("E", s)]]))
    rng = np.random.default_rng(29)
    idx = rng.integers(0, 20, (10000, 20))

    def ratio(a, b):
        rb = np.median(a[idx], 1) / np.median(b[idx], 1)
        return {"ratio": float(np.median(a) / np.median(b)),
                "ci99": [float(np.quantile(rb, 0.005)), float(np.quantile(rb, 0.995))]}

    test = {"settings": [list(s) for s in settings],
            "median_work": {str(list(s)): float(np.median(G[s])) for s in settings},
            "study_NOV_(0.8,0)_median_work": float(np.median(study_nov)),
            "referee_(0.8,0)_over_study_NOV": ratio(G[(0.8, 0.0)], study_nov),
            "unsolved": sum(not x["solved"] for x in te), "failed_state_checks": sum(x["ok"] is False for x in te)}
    if bp != (0.8, 0.0):
        test["best_over_(0.8,0)"] = ratio(G[bp], G[(0.8, 0.0)])
    d = 1.0 - (test["best_over_(0.8,0)"]["ratio"] if bp != (0.8, 0.0) else 1.0)
    R_E = float(np.median(study_E) / np.median(study_nov))
    f = E_fast_share
    test["E_on_these_20"] = {"R_E_vs_study_NOV": R_E, "E_fast_share_of_work": f,
                             "R_E_if_comparator_improved_by_d_and_E_fast_loop_equally":
                                 R_E * (1 - f * d) / (1 - d) if d < 1 else None,
                             "R_E_if_comparator_improved_by_d_and_E_fast_loop_not_at_all": R_E / (1 - d) if d < 1 else None,
                             "d": d}
    out = {"cell": CELL, "study_choice": tun[CELL]["NOV"], "tune_table": table, "referee_best": best,
           "referee_best_among_asked": best_asked,
           "best_vs_(0.8,0)_tune_score_diff": table[best]["score_20x2"] - table["[0.8, 0.0]"]["score_20x2"],
           "test": test, "tune_unsolved_total": sum(not x["solved"] for x in tr),
           "tune_failed_state_checks": sum(x["ok"] is False for x in tr),
           "seconds": {"tune": round(t1 - t0, 1), "test": round(time.time() - t1, 1)}}
    with open(os.path.join(HERE, "referee_earn_task2_grid_edge.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    for k, v in sorted(table.items(), key=lambda kv: kv[1]["score_20x2"]):
        print(k, {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()})
    print(json.dumps({k: v for k, v in out.items() if k != "tune_table"}, indent=1))


if __name__ == "__main__":
    main()
