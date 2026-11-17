"""EARN-BUDGET-R1 task 1: does charge v2 count all of the rebuild's work?

Under test (called, never edited): the study's slow_loop.run_slow with policy E (policies.json) and the cell's re-tuned
Novelty+ (retuned.json), on the first 10 test instances (seeds 8,100,000 + i, job.py's SEED_TEST) of local35-w15-3200 and
local-w20-3200, runs 0 and 1 (run_seed("test", cell, seed, r), as job.py), 20 runs per cell. Instrumentation from outside:
  - a proxy on slow_loop's module-level numpy times every np.unique / isin / union1d / bincount / where / concatenate call
    and counts the elements of each sort-based call (n log2 n), including the idx.sort() that follows np.unique;
  - slow_loop._sortcost is wrapped to total what charge v2 adds for sorts;
  - the C entry points are timed; sl_reduce's own charge (out[1]) and each rebuilt handle's 3m (fl_new) are read back, so
    that work_rebuild splits into SLOW-LOOP's charge (v1) and v2's additions.
The reruns' results are compared with the stored test runs. From the stored runs (all 250 per cell): CPU per charged
incidence of each part, and R against Novelty+ with the uncharged part added in two ways. Output:
referee_earn_task1_charging.json.
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
EXP = os.path.join(ROOT, "experiments/EARN-BUDGET-20261117-001A/EARN-BUDGET-20261117-001A-E001_earn_budget")
ART = os.path.join(ROOT, "artifacts/EARN-BUDGET-20261117-001A/EARN-BUDGET-20261117-001A-E001_earn_budget")
os.environ["SLOW_LOOP_BUILD"] = \
    "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/866db0bb-326b-5add-835e-78bf03179706/scratchpad/build_earn"
sys.path.insert(0, EXP)
import numpy as np  # noqa: E402

import slow_loop as S  # noqa: E402  (under test)

CELLS = {"local35-w15-3200": ("local", 3.5, 15, 3200, 2 * 10**8), "local-w20-3200": ("local", 4.0, 20, 3200, 2 * 10**8)}
SEED_TEST = 8_100_000


def gm(v):
    return float(np.exp(np.mean(np.log(np.maximum(v, 1e-12)))))


def stored_runs():
    runs = collections.defaultdict(lambda: collections.defaultdict(dict))
    for line in open(os.path.join(ART, "test", "results.jsonl")):
        x = json.loads(line).get("result")
        if not x or x["arm"] == "CDCL" or x["cell"] not in CELLS:
            continue
        runs[x["cell"]][x["arm"]][x["seed"]] = x["runs"]
    return runs


def part_stored(runs):
    out = {}
    for cell in CELLS:
        seeds = sorted(runs[cell]["NOV"])
        Wn = np.array([gm([q["work"] for q in runs[cell]["NOV"][s]]) for s in seeds])
        Wp = np.array([gm([q["work"] for q in runs[cell]["PS"][s]]) for s in seeds])
        Cn = np.array([gm([q["cpu"] for q in runs[cell]["NOV"][s]]) for s in seeds])
        Cp = np.array([gm([q["cpu"] for q in runs[cell]["PS"][s]]) for s in seeds])
        best = "NOV" if np.median(Wn) <= np.median(Wp) else "PS"
        Wb, Cb = (Wn, Cn) if best == "NOV" else (Wp, Cp)
        A = runs[cell]["E"]
        Q = [q for s in seeds for q in A[s]]
        rate = sum(q["cpu_fast"] for q in Q) / sum(q["work_fast"] for q in Q)  # E's C fast loop, pooled

        def corr(q, which):
            ex_rb = max(0.0, q["cpu_rebuild"] / rate - q["work_rebuild"])
            ex_sl = max(0.0, q["cpu_slow"] / rate - q["work_slow"])
            other = max(0.0, (q["cpu"] - q["cpu_fast"] - q["cpu_slow"] - q["cpu_rebuild"]) / rate)
            return q["work"] + ex_rb + (ex_sl + other if which == "all" else 0.0)

        W = np.array([gm([q["work"] for q in A[s]]) for s in seeds])
        C = np.array([gm([q["cpu"] for q in A[s]]) for s in seeds])
        Wr = np.array([gm([corr(q, "rebuild") for q in A[s]]) for s in seeds])
        Wa = np.array([gm([corr(q, "all") for q in A[s]]) for s in seeds])
        rng = np.random.default_rng(17)
        idx = rng.integers(0, len(seeds), (10000, len(seeds)))
        den = np.minimum(np.median(Wn[idx], 1), np.median(Wp[idx], 1))
        ci = lambda X: [float(np.quantile(np.median(X[idx], 1) / den, q)) for q in (0.005, 0.995)]
        med = lambda k: float(np.median([q[k] for q in Q]))
        out[cell] = {
            "instances": len(seeds), "better_fast_rule": best,
            "ns_per_charged_incidence_median_of_runs": {
                "fast": float(np.median([q["cpu_fast"] / q["work_fast"] for q in Q]) * 1e9),
                "slow": float(np.median([q["cpu_slow"] / q["work_slow"] for q in Q if q["work_slow"]]) * 1e9),
                "rebuild": float(np.median([q["cpu_rebuild"] / q["work_rebuild"] for q in Q if q["work_rebuild"]]) * 1e9)},
            "ns_per_charged_incidence_pooled": {
                "fast": rate * 1e9,
                "slow": sum(q["cpu_slow"] for q in Q) / sum(q["work_slow"] for q in Q) * 1e9,
                "rebuild": sum(q["cpu_rebuild"] for q in Q) / max(1, sum(q["work_rebuild"] for q in Q)) * 1e9},
            "nov_whole_run_ns_per_incidence": float(np.median([q["cpu"] / q["work"] for s in seeds
                                                               for q in runs[cell]["NOV"][s]]) * 1e9),
            "median_run": {k: med(k) for k in ("work", "work_fast", "work_slow", "work_rebuild", "cpu", "cpu_fast",
                                               "cpu_slow", "cpu_rebuild", "rebuilds", "epochs")},
            "share_rebuild_of_work_median": float(np.median([q["work_rebuild"] / q["work"] for q in Q])),
            "R_work": float(np.median(W) / np.median(Wb)), "R_work_ci99": ci(W),
            "R_work_plus_rebuild_cpu_excess": float(np.median(Wr) / np.median(Wb)), "ci99_rebuild": ci(Wr),
            "R_work_plus_all_uncharged_cpu": float(np.median(Wa) / np.median(Wb)), "ci99_all": ci(Wa),
            "R_cpu": float(np.median(C) / np.median(Cb)),
            "median_rebuild_cpu_excess_over_work_rebuild": float(np.median(
                [max(0.0, q["cpu_rebuild"] / rate - q["work_rebuild"]) / q["work_rebuild"] for q in Q if q["work_rebuild"]])),
        }
    return out


class Rec:
    def __init__(self):
        self.t = collections.defaultdict(float)
        self.calls = collections.Counter()
        self.sortops = collections.defaultdict(float)
        self.lin = collections.defaultdict(float)
        self.charged_sort = 0
        self.sl_reduce_w = 0
        self.fl_new_w = []


def nlog(n):
    return n * math.log2(max(n, 2)) if n > 0 else 0.0


def instrument(R):
    L = S.lib()
    orig = {k: getattr(L, k) for k in ("sl_reduce", "fl_new", "sl_probe", "fl_run")}

    def timed(name, f, after=None):
        def g(*a, **k):
            t0 = time.thread_time()
            try:
                return f(*a, **k)
            finally:
                R.t[name] += time.thread_time() - t0
                R.calls[name] += 1
                if after:
                    after(a)
        return g

    def after_reduce(a):
        R.sl_reduce_w += int(a[-1][1])

    def after_new(a):
        R.fl_new_w.append(int(a[-1]._obj.value))

    L.sl_reduce = timed("C.sl_reduce", orig["sl_reduce"], after_reduce)
    L.fl_new = timed("C.fl_new", orig["fl_new"], after_new)
    L.sl_probe = timed("C.sl_probe", orig["sl_probe"])
    L.fl_run = timed("C.fl_run", orig["fl_run"])

    def w_unique(a, *r, **k):
        t0 = time.thread_time()
        res = np.unique(a, *r, **k)
        R.t["np.unique"] += time.thread_time() - t0
        R.calls["np.unique"] += 1
        R.sortops["np.unique"] += nlog(int(np.size(a)))
        if k.get("return_index"):
            R.sortops["idx.sort after unique (uncharged)"] += nlog(int(np.size(res[0])))
        return res

    def w_sort2(name, f):
        def g(a, b, *r, **k):
            t0 = time.thread_time()
            res = f(a, b, *r, **k)
            R.t[name] += time.thread_time() - t0
            R.calls[name] += 1
            R.sortops[name] += nlog(int(np.size(a) + np.size(b)))
            return res
        return g

    def w_lin(name, f, size):
        def g(*a, **k):
            t0 = time.thread_time()
            res = f(*a, **k)
            R.t[name] += time.thread_time() - t0
            R.calls[name] += 1
            R.lin[name] += size(*a, **k)
            return res
        return g

    class NpProxy:
        def __getattr__(self, k):
            m = {"unique": w_unique, "isin": w_sort2("np.isin", np.isin), "union1d": w_sort2("np.union1d", np.union1d),
                 "bincount": w_lin("np.bincount", np.bincount, lambda a, *r, **k: int(np.size(a))),
                 "where": w_lin("np.where", np.where, lambda c, *r, **k: int(np.size(c))),
                 "concatenate": w_lin("np.concatenate", np.concatenate,
                                      lambda s, *r, **k: int(sum(np.size(z) for z in s)))}
            return m.get(k) or getattr(np, k)

    sc_orig, sk_orig = S._sortcost, S.sig_keys

    def sc(k):
        v = sc_orig(k)
        R.charged_sort += v
        return v

    S._sortcost = sc
    S.sig_keys = w_lin("py.sig_keys", sk_orig, lambda kv, *r, **k: int(len(kv)))
    S.np = NpProxy()

    def restore():
        for k, f in orig.items():
            setattr(L, k, f)
        S._sortcost, S.sig_keys, S.np = sc_orig, sk_orig, np
    return restore


def part_rerun(runs, n_inst=10, run_idx=(0, 1)):
    tun = json.load(open(os.path.join(ART, "retuned.json")))
    pol = json.load(open(os.path.join(ART, "policies.json")))["E"]
    out = {}
    for cell, (fam, a, w, n, cap) in CELLS.items():
        nov = tuple(tun[cell]["NOV"])
        per = []
        repro = collections.Counter()
        tot = collections.defaultdict(float)
        for i in range(n_inst):
            seed = SEED_TEST + i
            inst = S.planted(fam, n, a, seed, w=w)
            for r in run_idx:
                R = Rec()
                restore = instrument(R)
                try:
                    res = S.run_slow(inst, "novelty_plus", nov, S.run_seed("test", cell, seed, r), cap, dict(pol))
                finally:
                    restore()
                q = runs[cell]["E"][seed][r]
                keys = ("flips", "work", "work_fast", "work_slow", "work_rebuild", "rebuilds", "ties", "n_final",
                        "m_final", "doublings", "epochs")
                repro["identical" if all(res[k] == q[k] for k in keys) else "DIFFERENT"] += 1
                nb = R.calls["C.sl_reduce"]
                v1 = R.sl_reduce_w + nb * n + sum(R.fl_new_w[1:])  # the first handle's 3m is fast work
                v2_add = res["work_rebuild"] - v1
                actual_sort = sum(R.sortops.values())
                unch = {k: v for k, v in R.sortops.items()}
                py_t = sum(v for k, v in R.t.items() if k.startswith(("np.", "py.")))
                c_rb = R.t["C.sl_reduce"] + sum(0 for _ in [0])
                row = {"work": res["work"], "work_fast": res["work_fast"], "work_slow": res["work_slow"],
                       "work_rebuild": res["work_rebuild"], "rebuild_v1_part": v1, "rebuild_v2_additions": v2_add,
                       "v2_sort_charges": R.charged_sort, "actual_sort_ops": actual_sort,
                       "actual_sort_ops_by_call": unch,
                       "uncharged_sort_ops_net": max(0.0, actual_sort - R.charged_sort),
                       "uncharged_idx_sort": R.sortops.get("idx.sort after unique (uncharged)", 0.0),
                       "linear_elements": dict(R.lin), "rebuilds": res["rebuilds"],
                       "cpu": res["cpu"], "cpu_fast": res["cpu_fast"], "cpu_slow": res["cpu_slow"],
                       "cpu_rebuild": res["cpu_rebuild"], "cpu_parts": dict(R.t), "python_numpy_cpu": py_t}
                per.append(row)
                for k in ("work", "work_fast", "work_slow", "work_rebuild", "rebuild_v1_part", "rebuild_v2_additions",
                          "v2_sort_charges", "actual_sort_ops", "uncharged_sort_ops_net", "uncharged_idx_sort", "cpu",
                          "cpu_fast", "cpu_slow", "cpu_rebuild", "python_numpy_cpu", "rebuilds"):
                    tot[k] += row[k]
                for k, v in R.t.items():
                    tot["cpu:" + k] += v
        nr = len(per)
        m = {k: v / nr for k, v in tot.items()}
        fast_rate = m["cpu:C.fl_run"] / m["work_fast"]  # C fast loop (fl_run only) per charged fast incidence
        c_rebuild = m.get("cpu:C.sl_reduce", 0) + m.get("cpu:C.fl_new", 0)
        py_rebuild = m["cpu_rebuild"] - c_rebuild
        out[cell] = {
            "runs": nr, "reproduction_vs_stored": dict(repro), "mean_per_run": m,
            "share_v2_additions_of_work_rebuild": m["rebuild_v2_additions"] / m["work_rebuild"],
            "uncharged_sort_ops_net_share_of_work_rebuild": m["uncharged_sort_ops_net"] / m["work_rebuild"],
            "uncharged_sort_ops_net_share_of_work": m["uncharged_sort_ops_net"] / m["work"],
            "uncharged_idx_sort_share_of_work_rebuild": m["uncharged_idx_sort"] / m["work_rebuild"],
            "uncharged_idx_sort_share_of_work": m["uncharged_idx_sort"] / m["work"],
            "actual_sort_ops_over_v2_sort_charges": m["actual_sort_ops"] / max(1, m["v2_sort_charges"]),
            "ns_per_charged_incidence": {"fast (C fl_run)": fast_rate * 1e9,
                                         "slow (C sl_probe)": m["cpu:C.sl_probe"] / max(1, m["work_slow"]) * 1e9,
                                         "rebuild (all, as reported)": m["cpu_rebuild"] / m["work_rebuild"] * 1e9,
                                         "rebuild C part (sl_reduce + fl_new) over the v1 part":
                                             c_rebuild / max(1, m["rebuild_v1_part"]) * 1e9,
                                         "rebuild Python part over the v2 additions":
                                             py_rebuild / max(1, m["rebuild_v2_additions"]) * 1e9},
            "rebuild_python_cpu_in_fast_equiv_minus_v2_additions_share_of_work_rebuild":
                (py_rebuild / fast_rate - m["rebuild_v2_additions"]) / m["work_rebuild"],
            "rebuild_python_cpu_in_fast_equiv_minus_v2_additions_share_of_work":
                (py_rebuild / fast_rate - m["rebuild_v2_additions"]) / m["work"],
            "median_per_run_uncharged_sort_share_of_work": float(np.median(
                [r["uncharged_sort_ops_net"] / r["work"] for r in per])),
            "median_per_run_idx_sort_share_of_work": float(np.median([r["uncharged_idx_sort"] / r["work"] for r in per])),
            "per_run": per,
        }
    return out


def main():
    t0 = time.time()
    runs = stored_runs()
    res = {"stored": part_stored(runs)}
    t1 = time.time()
    res["rerun"] = part_rerun(runs)
    for cell in CELLS:
        rw = res["stored"][cell]["R_work"]
        res["rerun"][cell]["R_work_times_1_plus_uncharged_sort_share"] = rw * (
            1 + res["rerun"][cell]["median_per_run_uncharged_sort_share_of_work"])
        res["rerun"][cell]["R_work_times_1_plus_idx_sort_share"] = rw * (
            1 + res["rerun"][cell]["median_per_run_idx_sort_share_of_work"])
    res["seconds"] = {"stored": round(t1 - t0, 1), "rerun": round(time.time() - t1, 1)}
    with open(os.path.join(HERE, "referee_earn_task1_charging.json"), "w") as f:
        json.dump(res, f, indent=1)
    for cell in CELLS:
        s, r = res["stored"][cell], res["rerun"][cell]
        print(cell, json.dumps({k: v for k, v in s.items() if k != "median_run"}, indent=None))
        print("  rerun", json.dumps({k: v for k, v in r.items() if k not in ("per_run", "mean_per_run")}, indent=None))
        print("  mean", json.dumps({k: round(v, 5) if isinstance(v, float) else v for k, v in r["mean_per_run"].items()}))
    print(res["seconds"])


if __name__ == "__main__":
    main()
