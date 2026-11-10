#!/usr/bin/env python3
"""Run CROSS-WHY-20261110-001A-E001 (frozen contract beside this file): why stages fail, and schedules that cross a border.

    .venv/bin/python3 -B run.py [M|S|V|X ...]      parts to run (default all), each writing its own result file
On CROSS-WHY-20261110-001B's territory_lib (the stage read on one fundamental domain, exact by its Lemma 1) and, for part V, on
BIRTH-RULE-20261109-001A-E001's double() and readings() with GROW-CHOOSE-20261109-001A-E001's full state. Writes
artifacts/CROSS-WHY-20261110-001A/CROSS-WHY-20261110-001A-E001_schedules_that_cross/run/<part>.json."""
import importlib.util
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/CROSS-WHY-20261110-001B/CROSS-WHY-20261110-001B-P001_balance_is_read_on_one_territory"))
import territory_lib as T  # noqa: E402

OUT = ROOT / "artifacts/CROSS-WHY-20261110-001A/CROSS-WHY-20261110-001A-E001_schedules_that_cross/run"
WORKERS = 8


def mechanism(job):
    """the stage at the second doubling (one run of P lags): balance, the kind of failure, deficiency, crossing"""
    g, P = job
    r = T.NRun(g)
    r.double(0)
    cross = None
    for t in range(1, P + 1):
        r.step()
        if cross is None and r.originals_hearing():
            cross = t
    rank, own = r.own_rank((0, 0))
    old = r.double(P)
    f, per = r.read()
    kind = None
    if f:
        fr, _ = r.read(restricted=True)
        kind = "internal" if fr else "heard"
    return {"g": g, "P": P, "balanced": not f, "kind": kind, "first failure": min(f.values()) if f else None,
            "failing rings born at the stage": len({R for c, R in f if R not in old}),
            "own-cell rank of ring (0, 0)": [rank, own], "first crossing lag": cross}


def schedule(job):
    g, runs = job
    return T.play(g, runs)


def tree(pool, g, ranges, cross_only_after=None):
    nodes, out = [[]], []
    for depth, hi in enumerate(ranges):
        jobs = [(g, nd + [P]) for nd in nodes for P in range(1, hi + 1)]
        nxt = []
        for res in pool.imap(schedule, jobs, chunksize=1):
            if res["every stage balanced"]:
                out.append({"runs": res["runs"], "first crossing lag": res["first crossing lag"],
                            "original rings hearing (0, 0)": len(res["original rings hearing (0, 0)"]),
                            "sides": [s["side"] for s in res["stages"]]})
                if cross_only_after is None or depth + 1 < cross_only_after or res["first crossing lag"] is not None:
                    nxt.append(res["runs"])
        print("g", g, "depth", depth + 1, "balanced", len(nxt), "of", len(jobs), flush=True)
        if depth + 2 == cross_only_after:
            nxt = [r for r in nxt if any(o["runs"] == r and o["first crossing lag"] is not None for o in out)]
        nodes = nxt
    return out


def full_state(job):
    """BIRTH-RULE-20261109-001A-E001's balance reading on the full state at every doubling of the schedule"""
    g, runs = job
    spec = importlib.util.spec_from_file_location(
        "birth_rule_run", ROOT / "experiments/BIRTH-RULE-20261109-001A/BIRTH-RULE-20261109-001A-E001_birth_rules/run.py")
    BR = importlib.util.module_from_spec(spec)
    sys.modules["birth_rule_run"] = BR
    spec.loader.exec_module(BR)
    t0 = time.time()
    run = BR.C.Run2(BR.C.Tube2([0, 1, 2], [0, 1, 2], g))
    old = BR.double(run, 0, "open")
    bal = [BR.readings(run, old)[0]]
    t = 0
    for P in runs:
        for _ in range(P):
            run.step()
            t += 1
        old = BR.double(run, t, "open")
        bal.append(BR.readings(run, old)[0])
        if bal[-1] is False:
            break
    return {"g": g, "runs": runs, "balanced at each doubling": bal, "seconds": round(time.time() - t0)}


def main():
    parts = sys.argv[1:] or ["M", "S", "V", "X"]
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with Pool(WORKERS) as pool:
        if "M" in parts:
            jobs = [(g, P) for g in (2, 3, 4) for P in range(1, 25)]
            res = list(pool.imap(mechanism, jobs, chunksize=1))
            (OUT / "M.json").write_text(json.dumps({"mechanisms": res, "seconds": round(time.time() - t0)}, indent=1) + "\n")
            print("M done", round(time.time() - t0), flush=True)
        if "S" in parts:
            res = {"g = 3": tree(pool, 3, [40, 40, 16], cross_only_after=3),
                   "g = 2": tree(pool, 2, [24, 24]), "g = 5": tree(pool, 5, [24, 24])}
            (OUT / "S.json").write_text(json.dumps({"balanced schedules": res, "seconds": round(time.time() - t0)}, indent=1) + "\n")
            print("S done", round(time.time() - t0), flush=True)
    S = json.loads((OUT / "S.json").read_text())["balanced schedules"]["g = 3"] if (OUT / "S.json").exists() else []
    deep = [o["runs"] for o in S if len(o["runs"]) == 3 and o["first crossing lag"] is not None]
    if "V" in parts:
        controls = [[12, 2, 1], [28, 28, 28]]
        jobs = [(3, r) for r in deep[:2] + controls]
        with Pool(len(jobs)) as pool:
            res = list(pool.imap(full_state, jobs, chunksize=1))
        (OUT / "V.json").write_text(json.dumps({"full-state readings": res, "seconds": round(time.time() - t0)}, indent=1) + "\n")
        print("V done", round(time.time() - t0), flush=True)
    if "X" in parts:
        jobs = [(3, r + [d]) for r in deep[:4] for d in (1, 2)]
        with Pool(min(len(jobs), 4)) as pool:
            res = list(pool.imap(schedule, jobs, chunksize=1))
        (OUT / "X.json").write_text(json.dumps({"one size past": res, "seconds": round(time.time() - t0)}, indent=1) + "\n")
        print("X done", round(time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
