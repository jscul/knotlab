#!/usr/bin/env python3
"""Run METRIC-GROW-20261110-001A-E001 (frozen contract beside this file): time lengths of a growing plane.

    .venv/bin/python3 -B run.py [C|S5|S7|V|X ...]     parts to run (default all), each writing its own result file
Code 1: metric_lib (on CROSS-WHY-20261110-001B's territory_lib); code 2: code2_metric (on READ-GROW-20261110-001A-E001's grid_lib).
Writes artifacts/METRIC-GROW-20261110-001A/METRIC-GROW-20261110-001A-E001_time_length_while_growing/run/<part>.json."""
import itertools
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import code2_metric as C2  # noqa: E402
import metric_lib as M  # noqa: E402

OUT = ROOT / "artifacts/METRIC-GROW-20261110-001A/METRIC-GROW-20261110-001A-E001_time_length_while_growing/run"
G = 3


def key(d):
    return {"%d,%d" % Y: lag for Y, lag in sorted(d.items())}


def roundtrip(T1, n):
    """R1(v) = T1(v) + T1(-v), where both are defined, keyed by original label"""
    out = {}
    for (a, b), lag in T1.items():
        back = ((-a) % n, (-b) % n)
        if back in T1:
            out[(a, b)] = lag + T1[back]
    return out


def evaluate(job):
    n, runs = job
    res = M.run_schedule(n, G, runs)
    rec = {"n": n, "runs": runs, "every stage balanced": res["every stage balanced"],
           "sides": [s["side"] for s in res["stages"]], "periods": [s["period"] for s in res["stages"]]}
    if res["every stage balanced"]:
        fz = {"%d,%d" % Y: M.freeze_check(res, Y, "T") for Y in res["T"]}
        fz1 = {"%d,%d" % Y: M.freeze_check(res, Y, "T1") for Y in res["T1"]}
        T1ok = {Y: lag for Y, lag in res["T1"].items() if fz1["%d,%d" % Y]}
        R1 = roundtrip(T1ok, n)
        rec.update({"T": key(res["T"]), "T1": key(res["T1"]), "L": key(res["L"]), "R1": key(R1),
                    "T read through freezes": all(fz.values()), "T1 read through freezes": all(fz1.values()),
                    "freeze failures": [k for k, v in fz.items() if not v] + ["T1 " + k for k, v in fz1.items() if not v],
                    "R1 report": M.metric_report(R1, n), "T report": M.metric_report(res["T"], n),
                    "T1 report": M.metric_report(T1ok, n), "L report": M.metric_report(res["L"], n)})
    return rec


def tree(pool, n, ranges):
    nodes, out = [[]], []
    for depth, rng in enumerate(ranges):
        jobs = [(n, nd + [P]) for nd in nodes for P in rng]
        nxt = []
        for rec in pool.imap(evaluate, jobs, chunksize=1):
            if rec["every stage balanced"]:
                out.append(rec)
                nxt.append(rec["runs"])
        print("n", n, "depth", depth + 1, "balanced", len(nxt), "of", len(jobs), flush=True)
        nodes = nxt
    return out


def code2(job):
    n, runs, bal = job
    t0 = time.time()
    r = C2.play(n, G, runs, read_balance=bal)
    return {"n": n, "runs": runs, "every stage balanced": r["every stage balanced"] if bal else None,
            "T": key(r["T"]), "T1": key(r["T1"]), "L": key(r["L"]), "seconds": round(time.time() - t0)}


def main():
    parts = sys.argv[1:] or ["C", "S5", "S7", "V", "X"]
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    if "C" in parts:
        cases = [(3, [12, 1]), (3, [28, 1]), (5, [12, 28]), (5, [28, 1]), (5, [35, 1]), (7, [20]), (7, [40, 1])]
        with Pool(7) as pool:
            raw = pool.map(lambda_free_c1, cases, chunksize=1)
            two = pool.map(code2, [(n, r, False) for n, r in cases], chunksize=1)
        res = [{"case": [n, r], "agree": a == {k: b[k] for k in ("T", "T1", "L")}}
               for (n, r), a, b in zip(cases, raw, two)]
        (OUT / "C.json").write_text(json.dumps({"agreement": res, "all agree": all(x["agree"] for x in res)}, indent=1) + "\n")
        print("C done", all(x["agree"] for x in res), round(time.time() - t0), flush=True)
        if not all(x["agree"] for x in res):
            return
    with Pool(8) as pool:
        if "S5" in parts:
            out = tree(pool, 5, [range(1, 49), range(1, 65)])
            (OUT / "S5.json").write_text(json.dumps({"balanced schedules": out, "seconds": round(time.time() - t0)}, indent=1) + "\n")
            print("S5 done", round(time.time() - t0), flush=True)
        if "S7" in parts:
            out = tree(pool, 7, [range(1, 73), (1, 2)])
            (OUT / "S7.json").write_text(json.dumps({"balanced schedules": out, "seconds": round(time.time() - t0)}, indent=1) + "\n")
            print("S7 done", round(time.time() - t0), flush=True)
    S5 = json.loads((OUT / "S5.json").read_text())["balanced schedules"] if (OUT / "S5.json").exists() else []
    S7 = json.loads((OUT / "S7.json").read_text())["balanced schedules"] if (OUT / "S7.json").exists() else []

    def picks(S, n):
        two_run = [o for o in S if len(o["runs"]) == 2]
        pos = [o["runs"] for o in two_run if o["R1 report"]["metric"]]
        if pos:
            return pos[:2], True
        best = max((o["R1 report"]["reached to distance"] for o in two_run), default=0)
        return [o["runs"] for o in two_run if o["R1 report"]["reached to distance"] == best][:2], False
    p5, m5 = picks(S5, 5)
    p7, m7 = picks(S7, 7)
    if "V" in parts:
        jobs = [(5, r, True) for r in p5] + [(7, r, False) for r in p7]
        with Pool(max(1, len(jobs))) as pool:
            two = pool.map(code2, jobs, chunksize=1)
        one = {(o["n"], tuple(o["runs"])): o for o in S5 + S7}
        res = [{"n": t["n"], "runs": t["runs"], "metric positive": (m5 if t["n"] == 5 else m7),
                "code 2": t, "agree": all(one[(t["n"], tuple(t["runs"]))][k] == t[k] for k in ("T", "T1", "L"))
                and (t["every stage balanced"] in (None, True))} for t in two]
        (OUT / "V.json").write_text(json.dumps({"second code": res}, indent=1) + "\n")
        print("V done", round(time.time() - t0), flush=True)
    if "X" in parts and m5:
        jobs = [(5, r + [1]) for r in p5]
        with Pool(len(jobs)) as pool:
            one = pool.map(evaluate, jobs, chunksize=1)
            two = pool.map(code2, [(5, r + [1], True) for r in p5], chunksize=1)
        res = [{"runs": a["runs"], "code 1 every stage balanced": a["every stage balanced"],
                "code 2 every stage balanced": b["every stage balanced"], "R1 report": a.get("R1 report"),
                "code 2 seconds": b["seconds"]} for a, b in zip(one, two)]
        (OUT / "X.json").write_text(json.dumps({"one size past": res}, indent=1) + "\n")
        print("X done", round(time.time() - t0), flush=True)


def lambda_free_c1(case):
    n, r = case
    res = M.run_schedule(n, G, r, read_balance=False)
    return {"T": key(res["T"]), "T1": key(res["T1"]), "L": key(res["L"])}


if __name__ == "__main__":
    main()
