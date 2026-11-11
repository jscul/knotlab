#!/usr/bin/env python3
"""Checks for SHARED-COUNT-20261111-001A (research/SHARED-COUNT-20261111-001/preregistration.md).

    .venv/bin/python3 -B check.py --part harness|learn2|learn3|summary [--write]
PYTHONHASHSEED=0. harness: V1, the joined harness with one copy (m = 1) at seed 9000 reproduces LEARN-PARITY-20261111-001's first T1 run
exactly; R, every class combination of the copies on J2 (16) and J3 (64), the map at the joined interface by SAT and the exact parity test.
learn2, learn3: ten runs on J2 (seeds 9200 + k) and J3 (9300 + k), targets parity of the held inputs, its negation, parity again, budget
8,000,000 steps per target; each run is appended to runs_<part>.jsonl as it finishes (a run over its cap, 90 minutes on J2 and 120 on J3,
is recorded as dropped and counts as not learned). summary: reads the run files and settles P5 and P7."""
import hashlib
import json
import os
import signal
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
LIB = str((HERE / "join_lib.py").relative_to(ROOT))
PREREG = "research/SHARED-COUNT-20261111-001/preregistration.md"
FIVE = "proofs/PARITY-FIVE-20261111-001A/PARITY-FIVE-20261111-001A-P001_parity_of_five_held_points/five_lib.py"
LP = "proofs/LEARN-PARITY-20261111-001A/LEARN-PARITY-20261111-001A-P001_learning_parity/"
DEPS = [LIB, PREREG, FIVE, LP + "parity_lib.py", LP + "result.json"]
RUNS = {"learn2": (2, 9200, 5400), "learn3": (3, 9300, 7200)}


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def harness():
    import join_lib as J
    prev = json.loads((ROOT / LP / "result.json").read_text())["checks"]["rows"]["T1 run 0"]
    rows = J.run(1, ["01101001", "10010110", "01101001"], 9000)
    out = {"V1: the joined harness with one copy reproduces LEARN-PARITY's first T1 run": json.loads(json.dumps(rows)) == prev}
    for m in (2, 3):
        R = J.realizable(J.Joined(m))
        hits = [r["classes"] for r in R if r["parity at the interface"]]
        out["J%d" % m] = {"class combinations": len(R), "with parity at the interface": hits, "rows": R}
    out["R: parity realizable on J2 and J3"] = all(out["J%d" % m]["with parity at the interface"] for m in (2, 3))
    return out


def job(args):
    import join_lib as J
    m, seed, cap = args
    k = 2 * m + 1
    targets = [J.F.parity_string(k, 0), J.F.parity_string(k, 1), J.F.parity_string(k, 0)]
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(cap)
    t = time.time()
    try:
        rows = J.run(m, targets, seed)
        signal.alarm(0)
    except Timeout:
        rows = [{"target": targets[0], "outcome": "dropped (time cap)"}]
    return {"seed": seed, "seconds": round(time.time() - t, 1), "rows": rows}


def learn(part, write):
    m, base, cap = RUNS[part]
    path = HERE / ("runs_%s.jsonl" % part)
    if write:
        path.write_text("")
    res = []
    with Pool(10) as pool:
        for r in pool.imap_unordered(job, [(m, base + k, cap) for k in range(10)]):
            res.append(r)
            if write:
                with path.open("a") as f:
                    f.write(json.dumps(r) + "\n")
    return verdict(sorted(res, key=lambda r: r["seed"]))


def verdict(res):
    first = [r["rows"][0]["outcome"] for r in res]
    allo = [x["outcome"] for r in res for x in r["rows"]]
    steps = sorted(r["rows"][0]["steps"] for r in res if r["rows"][0]["outcome"] == "learned, held")
    return {"runs": len(res), "first target outcomes": {o: first.count(o) for o in sorted(set(first))},
            "all targets outcomes": {o: allo.count(o) for o in sorted(set(allo))},
            "learned and held at the first target": first.count("learned, held"),
            "median steps of learned first targets": steps[len(steps) // 2] if steps else None,
            "inexact stops": allo.count("inexact stop"), "seconds per run": [r["seconds"] for r in res], "runs detail": res}


def summary():
    out = {}
    for part, mark in (("learn2", "P5: J2 learned and held in at least 8 of 10"), ("learn3", "P7: J3 learned and held in at least 8 of 10")):
        p = HERE / ("runs_%s.jsonl" % part)
        res = [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []
        v = verdict(sorted(res, key=lambda r: r["seed"]))
        v.pop("runs detail")
        v["missing runs (part cap)"] = 10 - len(res)
        out[part] = v
        out[mark] = v["learned and held at the first target"] >= 8
    return out


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    part = sys.argv[sys.argv.index("--part") + 1]
    write = "--write" in sys.argv
    res = harness() if part == "harness" else summary() if part == "summary" else learn(part, write)
    res = json.loads(json.dumps(res, default=str))
    out = {"dependencies": {p: sha(p) for p in DEPS}, "result": res, "seconds": round(time.time() - T0, 1)}
    path = HERE / ("result_%s.json" % part)
    if write:
        path.write_text(json.dumps({"status": "passed", "checks": out}, indent=1) + "\n")
        print("wrote", path, out["seconds"], "s")
        print(json.dumps({k: v for k, v in res.items() if k not in ("rows", "runs detail", "J2", "J3")}, indent=1)[:3000])
    else:
        old = json.loads(path.read_text())["checks"]["result"]
        drop = ("seconds per run",)
        def clean(d):
            d = {k: v for k, v in d.items() if k not in drop}
            if "runs detail" in d:
                d["runs detail"] = [{k: v for k, v in r.items() if k != "seconds"} for r in d["runs detail"]]
            return d
        same = json.dumps(clean(old), sort_keys=True) == json.dumps(clean(res), sort_keys=True)
        print("result reproduced" if same else "result differs")
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()
