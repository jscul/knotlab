"""SLOW-LOOP-R1 task 3: what `work` charges and what it leaves out, for GO (and the other slow arms).

(a) From test/results.jsonl (stored runs): per cell and arm, the CPU per charged incidence of each part (fast loop, probes,
    rebuild), the rebuild CPU in excess of what its charged work would cost at the fast loop's rate (the cell's C fast-loop
    CPU per incidence, pooled over every slow-arm run; an estimate of
    uncharged rebuild work, in incidence-equivalents), the remaining Python driver CPU, and R recomputed with those
    estimates added, next to R_W and R_CPU.
(b) Instrumented reruns of the study's run_slow (under test, unchanged; only wrapped from outside): GO on the first 10
    test instances of local-w10-3200, 5 runs each (and the same on local-w40-3200, embed-3200, local-w10-800). Timers wrap the numpy calls the driver makes (through a proxy on
    slow_loop's module-level `np`) and the C entry points; sizes of every sort-based call (unique, isin, union1d) and of
    qsort in guided target selection (visited knots, read with fl_get before each probe) are recorded. The reruns'
    flips and work are compared with the stored runs (reproduction check).
Output: referee_task3_charging.json.
"""
from __future__ import annotations

import collections
import json
import math
import os
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
EXP = os.path.join(ROOT, "experiments/SLOW-LOOP-20261117-001A/SLOW-LOOP-20261117-001A-E001_slow_loop")
ART = os.path.join(ROOT, "artifacts/SLOW-LOOP-20261117-001A/SLOW-LOOP-20261117-001A-E001_slow_loop")
os.environ.setdefault("SLOW_LOOP_BUILD",
                      "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/866db0bb-326b-5add-835e-78bf03179706/scratchpad/build")
sys.path.insert(0, EXP)
import numpy as np  # noqa: E402

import slow_loop as S  # noqa: E402  (under test)


def gm(v):
    return float(np.exp(np.mean(np.log(np.maximum(v, 1e-12)))))


def part_a():
    runs = collections.defaultdict(lambda: collections.defaultdict(dict))
    for line in open(os.path.join(ART, "test", "results.jsonl")):
        x = json.loads(line).get("result")
        if not x or x["arm"] == "CDCL":
            continue
        runs[x["cell"]][x["arm"]][x["seed"]] = x["runs"]
    out = {}
    for cell in sorted(runs):
        nov = runs[cell]["NOV"]
        seeds = sorted(nov)
        # the fast loop's CPU per incidence, from NOV itself (whole-run thread CPU over charged work)
        nov_rate = float(np.median([q["cpu"] / q["work"] for s in seeds for q in nov[s]]))
        Wn = np.array([gm([q["work"] for q in nov[s]]) for s in seeds])
        Cn = np.array([gm([q["cpu"] for q in nov[s]]) for s in seeds])
        allq = [q for arm in ("G", "GO", "RND", "ST", "Gx") for s in seeds for q in runs[cell][arm][s]]
        pooled_rate = sum(q["cpu_fast"] for q in allq) / sum(q["work_fast"] for q in allq)
        res = {"nov_ns_per_incidence": nov_rate * 1e9, "pooled_fast_ns_per_incidence": pooled_rate * 1e9, "arms": {}}
        for arm in ("G", "GO", "RND", "ST", "Gx"):
            A = runs[cell][arm]
            Q = [q for s in seeds for q in A[s]]
            fr = np.median([q["cpu_fast"] / q["work_fast"] for q in Q])
            sr = np.median([q["cpu_slow"] / q["work_slow"] for q in Q if q["work_slow"] > 0]) if any(
                q["work_slow"] > 0 for q in Q) else float("nan")
            rr = np.median([q["cpu_rebuild"] / q["work_rebuild"] for q in Q if q["work_rebuild"] > 0]) if any(
                q["work_rebuild"] > 0 for q in Q) else float("nan")

            def est(q, which):
                rate = pooled_rate  # the cell's fast-loop C time per incidence, pooled over every slow-arm run
                ex_rb = max(0.0, q["cpu_rebuild"] / rate - q["work_rebuild"])
                other = max(0.0, (q["cpu"] - q["cpu_fast"] - q["cpu_slow"] - q["cpu_rebuild"]) / rate)
                ex_sl = max(0.0, q["cpu_slow"] / rate - q["work_slow"])
                if which == "rebuild":
                    return q["work"] + ex_rb
                if which == "rebuild+slow":
                    return q["work"] + ex_rb + ex_sl
                return q["work"] + ex_rb + ex_sl + other

            W = np.array([gm([q["work"] for q in A[s]]) for s in seeds])
            C = np.array([gm([q["cpu"] for q in A[s]]) for s in seeds])
            Wr = np.array([gm([est(q, "rebuild") for q in A[s]]) for s in seeds])
            Wrs = np.array([gm([est(q, "rebuild+slow") for q in A[s]]) for s in seeds])
            Wall = np.array([gm([est(q, "all") for q in A[s]]) for s in seeds])
            med = lambda key: float(np.median([q[key] for q in Q]))
            res["arms"][arm] = {
                "ns_per_charged_incidence": {"fast": float(fr * 1e9), "probes": float(sr * 1e9),
                                             "rebuild": float(rr * 1e9)},
                "median_run": {k: med(k) for k in ("work", "work_fast", "work_slow", "work_rebuild", "cpu", "cpu_fast",
                                                   "cpu_slow", "cpu_rebuild", "rebuilds")},
                "median_uncharged_rebuild_equiv": float(np.median(
                    [max(0.0, q["cpu_rebuild"] / pooled_rate - q["work_rebuild"]) for q in Q])),
                "median_driver_cpu_s": float(np.median([q["cpu"] - q["cpu_fast"] - q["cpu_slow"] - q["cpu_rebuild"]
                                                        for q in Q])),
                "R_work_vs_NOV": float(np.median(W) / np.median(Wn)),
                "R_cpu_vs_NOV": float(np.median(C) / np.median(Cn)),
                "R_work_plus_uncharged_rebuild": float(np.median(Wr) / np.median(Wn)),
                "R_work_plus_uncharged_rebuild_and_probe": float(np.median(Wrs) / np.median(Wn)),
                "R_work_plus_all_uncharged_cpu": float(np.median(Wall) / np.median(Wn)),
            }
        out[cell] = res
    return out


class Timed:
    def __init__(self):
        self.t = collections.defaultdict(float)
        self.calls = collections.Counter()
        self.sortops = collections.defaultdict(float)  # sum of n log2 n over sort-based calls
        self.lin = collections.defaultdict(float)  # sum of element counts for linear passes

    def wrap(self, name, f, size=None, kind=None):
        def g(*a, **k):
            t0 = time.thread_time()
            try:
                return f(*a, **k)
            finally:
                self.t[name] += time.thread_time() - t0
                self.calls[name] += 1
                if size is not None:
                    nn = size(*a, **k)
                    if kind == "sort":
                        self.sortops[name] += nn * math.log2(max(nn, 2))
                    else:
                        self.lin[name] += nn
        return g


class NpProxy:
    def __init__(self, T):
        self._T = T
        sz1 = lambda a, *r, **k: int(np.size(a))
        sz2 = lambda a, b, *r, **k: int(np.size(a) + np.size(b))
        self._w = {"unique": T.wrap("np.unique", np.unique, sz1, "sort"),
                   "isin": T.wrap("np.isin", np.isin, sz2, "sort"),
                   "union1d": T.wrap("np.union1d", np.union1d, sz2, "sort"),
                   "bincount": T.wrap("np.bincount", np.bincount, sz1, "lin"),
                   "where": T.wrap("np.where", np.where, lambda c, *r, **k: int(np.size(c)), "lin"),
                   "concatenate": T.wrap("np.concatenate", np.concatenate,
                                         lambda s, *r, **k: int(sum(np.size(z) for z in s)), "lin")}

    def __getattr__(self, k):
        return self._w.get(k) or getattr(np, k)


def part_b(n_inst=10, n_runs=5, cell="local-w10-3200"):
    tun = json.load(open(os.path.join(ART, "retuned.json")))
    pols = json.load(open(os.path.join(ART, "policies.json")))
    stored = {}
    for line in open(os.path.join(ART, "test", "results.jsonl")):
        x = json.loads(line).get("result")
        if x and x["cell"] == cell and x["arm"] == "GO":
            stored[x["seed"]] = x["runs"]
    L = S.lib()
    T = Timed()
    orig = {k: getattr(L, k) for k in ("sl_reduce", "fl_new", "sl_probe", "fl_run", "fl_get", "fl_free")}
    qs = {"nord_sum": 0.0, "nord_log": 0.0, "nvis_plus_nord_charged": 0.0, "calls": 0}

    def sl_probe_wrapped(h, mode, *rest):
        # read the visit counts (only to size the sort; fl_get copies, it changes nothing in the handle)
        if mode == 0:
            hh = h
            # number of knots of the handle: from the last fl_new size recorded
            m = cur_m[0]
            vis = np.zeros(max(1, m), np.int32)
            pr = np.zeros(max(1, m), np.uint8)
            nn = max(1, cur_n[0])
            orig["fl_get"](hh, np.zeros(nn, np.uint8), np.zeros(nn, np.int64), np.zeros(2, np.uint64), None, vis, pr)
            nvis = int(np.sum(vis > 0))
            nord = int(np.sum((vis > 0) & (pr == 0)))
            qs["nord_sum"] += nord
            qs["nord_log"] += nord * math.log2(max(nord, 2))
            qs["nvis_plus_nord_charged"] += nvis + nord
            qs["calls"] += 1
        return T.wrap("C.sl_probe", orig["sl_probe"])(h, mode, *rest)

    cur_m = [0]
    cur_n = [0]

    def fl_new_wrapped(n, m, *rest):
        cur_m[0] = int(m)
        cur_n[0] = int(n)
        return T.wrap("C.fl_new", orig["fl_new"])(n, m, *rest)

    L.sl_reduce = T.wrap("C.sl_reduce", orig["sl_reduce"])
    L.fl_new = fl_new_wrapped
    L.sl_probe = sl_probe_wrapped
    L.fl_run = T.wrap("C.fl_run", orig["fl_run"])
    sig_orig = S.sig_keys
    S.sig_keys = T.wrap("py.sig_keys", sig_orig, lambda kv, *r, **k: int(len(kv)), "lin")
    S.np = NpProxy(T)
    fam, a, w, n, cap = {"local-w10-3200": ("local", 4.0, 10, 3200, 2 * 10**8),
                         "local-w40-3200": ("local", 4.0, 40, 3200, 2 * 10**8),
                         "embed-3200": ("embed", 0.0, 10, 3200, 2 * 10**8),
                         "local-w10-800": ("local", 4.0, 10, 800, 2 * 10**7)}[cell]
    nov = tuple(tun[cell]["NOV"])
    per_run_inflation = []
    agg = collections.Counter()
    repro = collections.Counter()
    t_total = 0.0
    try:
        for i in range(n_inst):
            seed = 7_100_000 + i
            inst = S.planted_embed(n, seed, frac=0.25, alpha_r=2.1, alpha_l=4.0, alpha_c=0.02, w=10) \
                if fam == "embed" else S.planted(fam, n, a, seed, w=w)
            for r in range(n_runs):
                rs = S.run_seed("test", cell, seed, r)
                t0 = time.thread_time()
                so0 = sum(T.sortops.values()) + qs["nord_log"]
                res = S.run_slow(inst, "novelty_plus", nov, rs, cap, dict(pols["GO"]))
                per_run_inflation.append((sum(T.sortops.values()) + qs["nord_log"] - so0) / res["work"])
                t_total += time.thread_time() - t0
                for k in ("work", "work_fast", "work_slow", "work_rebuild", "rebuilds", "flips"):
                    agg[k] += res[k]
                for k in ("cpu", "cpu_fast", "cpu_slow", "cpu_rebuild"):
                    agg[k] += res[k]
                q = stored[seed][r]
                same = all(res[k] == q[k] for k in ("flips", "work", "work_fast", "work_slow", "work_rebuild",
                                                    "rebuilds", "ties", "n_final", "m_final"))
                repro["identical" if same else "DIFFERENT"] += 1
    finally:
        for k, f in orig.items():
            setattr(L, k, f)
        S.np = np
        S.sig_keys = sig_orig
    nr = n_inst * n_runs
    fast_rate = agg["cpu_fast"] / agg["work_fast"]
    py_uncharged_t = sum(T.t[k] for k in T.t if k.startswith("np.") or k.startswith("py."))
    res = {
        "runs": nr, "reproduction_vs_stored": dict(repro),
        "per_run_mean": {k: agg[k] / nr for k in agg},
        "cpu_s_per_run": {k: T.t[k] / nr for k in sorted(T.t)},
        "calls_per_run": {k: T.calls[k] / nr for k in sorted(T.calls)},
        "sort_element_ops_per_run (n log2 n)": {k: T.sortops[k] / nr for k in T.sortops},
        "linear_elements_per_run": {k: T.lin[k] / nr for k in T.lin},
        "guided_qsort_per_run": {"nord": qs["nord_sum"] / nr, "nord_log2_nord": qs["nord_log"] / nr,
                                 "charged_nvis_plus_nord": qs["nvis_plus_nord_charged"] / nr,
                                 "calls": qs["calls"] / nr},
        "fast_ns_per_incidence": fast_rate * 1e9,
        "python_side_uncharged_cpu_s_per_run": py_uncharged_t / nr,
        "python_side_uncharged_in_fast_incidence_equiv_per_run": py_uncharged_t / nr / fast_rate,
        "sort_ops_total_per_run": sum(T.sortops.values()) / nr + qs["nord_log"] / nr,
    }
    res["median_per_run_sort_ops_over_work"] = float(np.median(per_run_inflation))
    res["ratio_sort_ops_to_work_rebuild"] = res["sort_ops_total_per_run"] / res["per_run_mean"]["work_rebuild"]
    res["ratio_sort_ops_to_work"] = res["sort_ops_total_per_run"] / res["per_run_mean"]["work"]
    res["ratio_python_uncharged_equiv_to_work_rebuild"] = (
        res["python_side_uncharged_in_fast_incidence_equiv_per_run"] / res["per_run_mean"]["work_rebuild"])
    res["ratio_python_uncharged_equiv_to_work"] = (
        res["python_side_uncharged_in_fast_incidence_equiv_per_run"] / res["per_run_mean"]["work"])
    return res


def main():
    t0 = time.time()
    out = {"a_stored": part_a()}
    t1 = time.time()
    out["b_instrumented_GO_local_w10_3200"] = part_b()
    for cell in ("local-w40-3200", "embed-3200", "local-w10-800"):
        out[f"b_instrumented_GO_{cell}"] = part_b(cell=cell)
    for k, v in out.items():
        if k.startswith("b_instrumented_GO_"):
            cell = k[len("b_instrumented_GO_"):].replace("_", "-")
            rw = out["a_stored"][cell]["arms"]["GO"]["R_work_vs_NOV"]
            v["R_work_times_1_plus_sort_ops_share"] = rw * (1 + v["median_per_run_sort_ops_over_work"])
    out["seconds"] = {"a": round(t1 - t0, 1), "b": round(time.time() - t1, 1)}
    with open(os.path.join(HERE, "referee_task3_charging.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out["b_instrumented_GO_local_w10_3200"], indent=1))
    for cell in ("local-w10-3200", "local-w40-3200", "embed-3200", "local-w10-800"):
        print(cell, json.dumps({a: {k: round(v, 3) for k, v in d.items() if k.startswith("R_")}
                                for a, d in out["a_stored"][cell]["arms"].items()}))


if __name__ == "__main__":
    main()
