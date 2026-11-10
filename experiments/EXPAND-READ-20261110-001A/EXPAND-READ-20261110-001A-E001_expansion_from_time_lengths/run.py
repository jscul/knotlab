#!/usr/bin/env python3
"""Run EXPAND-READ-20261110-001A-E001 (frozen contract beside this file): the expansion read from time lengths.

    .venv/bin/python3 -B run.py
On METRIC-GROW-20261110-001A-E001's metric_lib (code 1: routes, freeze readings) and code2_metric (code 2, for a sample). Writes
artifacts/EXPAND-READ-20261110-001A/EXPAND-READ-20261110-001A-E001_expansion_from_time_lengths/run/result.json."""
import itertools
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MG = ROOT / "experiments/METRIC-GROW-20261110-001A/METRIC-GROW-20261110-001A-E001_time_length_while_growing"
sys.path.insert(0, str(MG))
import code2_metric as C2  # noqa: E402
import metric_lib as M  # noqa: E402

OUT = ROOT / "artifacts/EXPAND-READ-20261110-001A/EXPAND-READ-20261110-001A-E001_expansion_from_time_lengths/run"


def families():
    F1 = [(5, 3, [a, b, c]) for a in range(8, 29, 4) for b in range(4, 25, 4) for c in range(8, 65, 8)]
    F2 = [(5, g, [a, b]) for g in (2, 5) for a in range(4, 65, 4) for b in range(4, 65, 4)]
    F3 = [(7, 3, [a, b]) for a in range(8, 49, 8) for b in range(8, 65, 8)]
    mg = ROOT / "artifacts/METRIC-GROW-20261110-001A/METRIC-GROW-20261110-001A-E001_time_length_while_growing/run"
    F4 = [(o["n"], 3, o["runs"]) for f in ("S5.json", "S7.json") for o in json.loads((mg / f).read_text())["balanced schedules"]
          if len(o["runs"]) == 2]
    F4 += [(5, 3, r) for r in ([28, 1, 1], [28, 1, 2], [35, 1, 1])]
    return {"F1": F1, "F2": F2, "F3": F3, "F4 (balanced)": F4}


def wrapf(n):
    def disp(a, b):
        f = lambda x: x if x <= n // 2 else x - n   # noqa: E731
        return f(a), f(b)
    return disp


def evaluate(job):
    n, g, runs = job
    res = M.run_schedule(n, g, runs, read_balance=False)
    stages = res["_ctx"][0]
    D = [s.start for s in stages[1:]]                 # doubling lags after lag 0
    k = lambda tau: sum(1 for d in D if 0 < d <= tau)   # noqa: E731  stage of the step tau -> tau + 1
    phi = lambda t: sum(2.0 ** -k(tau) for tau in range(t))   # noqa: E731  conformal time of lag t
    disp = wrapf(n)
    T1 = {Y: lag for Y, lag in res["T1"].items() if M.freeze_check(res, Y, "T1")}
    T = {Y: lag for Y, lag in res["T"].items() if M.freeze_check(res, Y, "T")}
    t1 = {disp(*Y): lag for Y, lag in T1.items()}
    tt = {disp(*Y): lag for Y, lag in T.items()}
    wrap = lambda u: disp(u[0] % n, u[1] % n)   # noqa: E731
    D1 = D[0] if D else 10 ** 9
    # X1: directed T1 triangle violations, and whether each needs T1(u) + T1(w) > D1
    x1 = {"violations": 0, "within the first stage": 0}
    for u in t1:
        for w in t1:
            z = wrap((u[0] + w[0], u[1] + w[1]))
            if z != (0, 0) and z in t1 and t1[z] > t1[u] + t1[w]:
                x1["violations"] += 1
                if t1[u] + t1[w] <= D1:
                    x1["within the first stage"] += 1
    # X2: increments along each axis between consecutive multiples first reached in the same stage
    x2 = []
    for name, lagmap in (("T", tt), ("T1", t1)):
        for e in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for d in range(1, n // 2):
                a, b = wrap((d * e[0], d * e[1])), wrap(((d + 1) * e[0], (d + 1) * e[1]))
                if a in lagmap and b in lagmap and k(lagmap[a] - 1) == k(lagmap[b] - 1):
                    st = k(lagmap[a] - 1)
                    x2.append({"reading": name, "axis": list(e), "d": d, "stage": st, "increment": lagmap[b] - lagmap[a],
                               "predicted": 4 * g * 2 ** st})
    # X3: conformal round trip and plain round trip
    R, Rc = {}, {}
    for v, lag in t1.items():
        back = wrap((-v[0], -v[1]))
        if back in t1:
            R[v] = lag + t1[back]
            Rc[v] = phi(lag) + phi(t1[back])
    def viol(f):
        out = []
        for u in f:
            for w in f:
                z = wrap((u[0] + w[0], u[1] + w[1]))
                if z != (0, 0) and z in f and f[z] > f[u] + f[w] + 1e-9:
                    out.append(f[z] - f[u] - f[w])
        return out
    vR, vRc = viol(R), viol(Rc)
    return {"n": n, "g": g, "runs": runs, "doublings": D, "T1 defined": len(t1), "T1 not read through freezes": len(res["T1"]) - len(T1),
            "T not read through freezes": len(res["T"]) - len(T), "round trips": len(R),
            "X1": x1, "X2": x2, "R1 violations": len(vR), "R1 largest excess": max(vR, default=0),
            "conformal violations": len(vRc), "conformal largest excess": max(vRc, default=0),
            "R1": {"%d,%d" % v: x for v, x in sorted(R.items())}, "conformal R1": {"%d,%d" % v: x for v, x in sorted(Rc.items())},
            "T1": {"%d,%d" % v: x for v, x in sorted(t1.items())}}


def code1_raw(job):
    n, g, runs = job
    r = M.run_schedule(n, g, runs, read_balance=False)
    return {"T": r["T"], "T1": r["T1"]}


def code2(job):
    n, g, runs = job
    r = C2.play(n, g, runs, read_balance=False)
    return {"T": r["T"], "T1": r["T1"]}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    fam = families()
    out = {}
    with Pool(8) as pool:
        for name, jobs in fam.items():
            out[name] = list(pool.imap(evaluate, jobs, chunksize=1))
            print(name, len(jobs), "schedules", round(time.time() - t0), "s", flush=True)
        sample = (fam["F1"] + fam["F2"] + fam["F3"])[::25]
        one = pool.map(code1_raw, sample, chunksize=1)
        two = pool.map(code2, sample, chunksize=1)
    agree = [a == b for a, b in zip(one, two)]
    summary = {}
    for name, rows in out.items():
        x2 = [r for row in rows for r in row["X2"]]
        summary[name] = {
            "schedules": len(rows),
            "X1: T1 violations": sum(r["X1"]["violations"] for r in rows),
            "X1: violations within the first stage": sum(r["X1"]["within the first stage"] for r in rows),
            "X2: increments read": len(x2), "X2: increments as predicted": sum(1 for r in x2 if r["increment"] == r["predicted"]),
            "X2: by stage": {str(s): sorted({r["increment"] for r in x2 if r["stage"] == s}) for s in sorted({r["stage"] for r in x2})},
            "R1: schedules with a violation": sum(1 for r in rows if r["R1 violations"]),
            "X3: schedules with a conformal violation": sum(1 for r in rows if r["conformal violations"]),
            "X3: conformal violations": sum(r["conformal violations"] for r in rows),
            "X3: largest conformal excess": max((r["conformal largest excess"] for r in rows), default=0),
            "T1 not read through freezes": sum(r["T1 not read through freezes"] for r in rows)}
    result = {"experiment_id": "EXPAND-READ-20261110-001A-E001", "summary": summary,
              "code 2 sample": {"schedules": len(sample), "agree": sum(agree)}, "rows": out, "seconds": round(time.time() - t0)}
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(summary, indent=1), "code 2", sum(agree), "of", len(sample), round(time.time() - t0), "s", flush=True)


if __name__ == "__main__":
    main()
