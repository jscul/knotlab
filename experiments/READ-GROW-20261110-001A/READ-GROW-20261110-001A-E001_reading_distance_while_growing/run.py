#!/usr/bin/env python3
"""Run READ-GROW-20261110-001A-E001 (frozen contract beside this file): a growing plane that reads distance 1, then 2.

    .venv/bin/python3 -B run.py [C|S|V|X ...]     parts to run (default all), each writing its own result file
Code 1 is CROSS-WHY-20261110-001B's territory_lib (the stage read on one fundamental domain, exact by its Lemma 1); code 2 is grid_lib
beside this file, written independently; part V uses BIRTH-RULE-20261109-001A-E001's double() and readings() on the full state.
Writes artifacts/READ-GROW-20261110-001A/READ-GROW-20261110-001A-E001_reading_distance_while_growing/run/<part>.json."""
import importlib.util
import itertools
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "proofs/CROSS-WHY-20261110-001B/CROSS-WHY-20261110-001B-P001_balance_is_read_on_one_territory"))
import grid_lib as G2  # noqa: E402
import territory_lib as T  # noqa: E402

OUT = ROOT / "artifacts/READ-GROW-20261110-001A/READ-GROW-20261110-001A-E001_reading_distance_while_growing/run"
N, GSP = 5, 3
RANGES = (48, 40)


def disp(a, b, n=N):
    """an original ring's displacement from (0, 0) on the n x n torus, coordinates in -n//2 .. n//2"""
    f = lambda x: x if x <= n // 2 else x - n   # noqa: E731
    return f(a), f(b)


def taxi(v):
    return abs(v[0]) + abs(v[1])


def play_h(job):
    """code 1: the schedule from the open 5 x 5 tube; each stage read at its doubling; each original ring's first hearing of (0, 0),
    with the number of doublings before it"""
    n, g, runs = job
    r = T.NRun(g, n)
    r.double(0)
    f, per = r.read()
    stages = [{"lag": 0, "side": len(r.tube.cols), "balanced": not f, "period": per}]
    first, t = {}, 0
    for k, P in enumerate(runs):
        for _ in range(P):
            r.step()
            t += 1
            for Y in r.originals_hearing():
                first.setdefault("%d,%d" % Y, [t, k + 1])
        r.double(t)
        f, per = r.read()
        stages.append({"lag": t, "side": len(r.tube.cols), "balanced": not f, "period": per,
                       "first failure": min(f.values()) if f else None})
        if f:
            break
    return {"n": n, "g": g, "runs": list(runs), "stages": stages,
            "every stage balanced": all(s["balanced"] for s in stages) and len(stages) == len(runs) + 1, "first hearing": first}


def lags(res):
    """{displacement: first hearing lag}"""
    out = {}
    for key, (lag, k) in res["first hearing"].items():
        a, b = map(int, key.split(","))
        out[disp(a, b)] = lag
    return out


def outcomes(res):
    """O1, O2 and O3 as frozen in the contract"""
    L = lags(res)
    stage = {}
    for key, (lag, k) in res["first hearing"].items():
        a, b = map(int, key.split(","))
        stage[disp(a, b)] = k
    d1 = [v for v in L if taxi(v) == 1]
    d2 = [v for v in L if taxi(v) == 2]
    o1 = res["every stage balanced"] and len(d1) == 4 and bool(d2) and max(L[v] for v in d1) < min(L[v] for v in d2)
    o2 = o1 and min(stage[v] for v in d2) > max(stage[v] for v in d1)
    allv = [v for v in itertools.product(range(-(N // 2), N // 2 + 1), repeat=2) if v != (0, 0)]
    full = all(v in L for v in allv)
    sym = full and all(L[v] == L[(-v[0], -v[1])] for v in allv)

    def wrap(u):
        return disp(u[0] % N, u[1] % N)
    tri = full and all(L[wrap((u[0] + w[0], u[1] + w[1]))] <= L[u] + L[w]
                       for u in allv for w in allv if wrap((u[0] + w[0], u[1] + w[1])) != (0, 0))
    classes = {}
    for v in allv:
        if v in L:
            classes.setdefault(taxi(v), set()).add(L[v])
    by_class = full and all(len(s) == 1 for s in classes.values())
    increasing = by_class and all(min(classes[d + 1]) > max(classes[d]) for d in range(1, max(classes)))
    return {"O1": bool(o1), "O2": bool(o2), "every original heard": full, "symmetric": bool(sym), "triangle inequality": bool(tri),
            "constant on taxicab classes": bool(by_class), "strictly increasing in taxicab distance": bool(increasing),
            "O3 (a metric reading the lattice distance)": bool(full and sym and tri and by_class and increasing),
            "lags by taxicab distance": {str(d): sorted(s) for d, s in sorted(classes.items())}}


def tree(pool):
    nodes, out = [[]], []
    for depth, hi in enumerate(RANGES):
        jobs = [(N, GSP, nd + [P]) for nd in nodes for P in range(1, hi + 1)]
        nxt = []
        for res in pool.imap(play_h, jobs, chunksize=1):
            if res["every stage balanced"]:
                rec = {"runs": res["runs"], "first hearing": res["first hearing"], "sides": [s["side"] for s in res["stages"]],
                       "periods": [s["period"] for s in res["stages"]]}
                if depth == len(RANGES) - 1:
                    rec["outcomes"] = outcomes(res)
                out.append(rec)
                nxt.append(res["runs"])
        print("depth", depth + 1, "balanced", sum(1 for o in out if len(o["runs"]) == depth + 1), "of", len(jobs),
              "extended", len(nxt), flush=True)
        nodes = nxt
    return out


def code2(job):
    n, g, runs = job
    t0 = time.time()
    r = G2.play(n, g, runs)
    r["seconds"] = round(time.time() - t0)
    return r


def full_state(job):
    n, g, runs = job
    spec = importlib.util.spec_from_file_location(
        "birth_rule_run", ROOT / "experiments/BIRTH-RULE-20261109-001A/BIRTH-RULE-20261109-001A-E001_birth_rules/run.py")
    BR = importlib.util.module_from_spec(spec)
    sys.modules["birth_rule_run"] = BR
    spec.loader.exec_module(BR)
    t0 = time.time()
    run = BR.C.Run2(BR.C.Tube2(list(range(n)), list(range(n)), g))
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
    return {"n": n, "g": g, "runs": runs, "balanced at each doubling": bal, "seconds": round(time.time() - t0)}


def agree(a, b):
    return ([s["balanced"] for s in a["stages"]] == [s["balanced"] for s in b["stages"]]
            and [s.get("first failure") for s in a["stages"]] == [s.get("first failure") for s in b["stages"]]
            and {k: v[0] for k, v in a["first hearing"].items()} == b["first hearing lag"])


def main():
    parts = sys.argv[1:] or ["C", "S", "V", "X"]
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    if "C" in parts:
        cases = [(3, 3, [6]), (3, 3, [8]), (3, 3, [12]), (3, 3, [12, 1]), (3, 3, [12, 3]), (3, 2, [2]), (3, 2, [5]),
                 (5, 3, [8]), (5, 3, [12]), (5, 3, [12, 1]), (5, 2, [6, 1])]
        with Pool(8) as pool:
            one = pool.map(play_h, cases, chunksize=1)
            two = pool.map(code2, cases, chunksize=1)
        res = [{"case": list(c), "agree": agree(a, b), "code 1": [s["balanced"] for s in a["stages"]],
                "code 2": [s["balanced"] for s in b["stages"]]} for c, a, b in zip(cases, one, two)]
        (OUT / "C.json").write_text(json.dumps({"agreement": res, "all agree": all(r["agree"] for r in res)}, indent=1) + "\n")
        print("C done", all(r["agree"] for r in res), round(time.time() - t0), flush=True)
    if "S" in parts:
        with Pool(8) as pool:
            out = tree(pool)
        (OUT / "S.json").write_text(json.dumps({"balanced schedules": out, "seconds": round(time.time() - t0)}, indent=1) + "\n")
        print("S done", round(time.time() - t0), flush=True)
    S = json.loads((OUT / "S.json").read_text())["balanced schedules"] if (OUT / "S.json").exists() else []
    pos = [o["runs"] for o in S if o.get("outcomes", {}).get("O1")]
    if "V" in parts and pos:
        jobs = [(N, GSP, r) for r in pos[:2]]
        with Pool(len(jobs)) as pool:
            full = pool.map(full_state, jobs, chunksize=1)
            two = pool.map(code2, jobs, chunksize=1)
        (OUT / "V.json").write_text(json.dumps({"full-state readings": full, "code 2": two}, indent=1, default=str) + "\n")
        print("V done", round(time.time() - t0), flush=True)
    if "X" in parts and pos:
        jobs = [(N, GSP, r + [d]) for r in pos[:4] for d in (1, 2)]
        with Pool(8) as pool:
            one = pool.map(play_h, jobs, chunksize=1)
            two = pool.map(code2, jobs, chunksize=1)
        res = [{"runs": a["runs"], "code 1 every stage balanced": a["every stage balanced"],
                "code 2 every stage balanced": b["every stage balanced"], "agree": agree(a, b),
                "code 1 stages": a["stages"], "code 2 seconds": b["seconds"]} for a, b in zip(one, two)]
        (OUT / "X.json").write_text(json.dumps({"one size past": res}, indent=1, default=str) + "\n")
        print("X done", round(time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
