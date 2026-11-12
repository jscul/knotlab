#!/usr/bin/env python3
"""Checks for ODD-SEARCH-20261112-001A (research/ODD-SEARCH-20261112-001/preregistration.md).

    .venv/bin/python3 -B check.py --part p31|p37|targeted|ap|route|summary|referee [--write]
p31, p37: the complete word search by defect number (odd k up to p/3). targeted: p = 41 and 43 with k <= 9, p = 47 with k <= 7.
ap: the progression family at every prime 31 to 61. route: after the run, whether each fully blocked word reaches its flip by steps
of one or two places. summary: S1, S2. referee: odd_referee.py (fresh code)."""
import hashlib
import json
import os
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()
DEPS = [str((HERE / f).relative_to(ROOT)) for f in ("odd_lib.py", "odd_referee.py")] + ["research/ODD-SEARCH-20261112-001/preregistration.md"]
PLANS = {"p31": [(31, k) for k in range(1, 10, 2)], "p37": [(37, k) for k in range(1, 12, 2)],
         "targeted": [(p, k) for p in (41, 43) for k in range(1, 10, 2)] + [(47, k) for k in range(1, 8, 2)]}


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def job(pk):
    import odd_lib as O
    p, k = pk
    t = time.time()
    tally, blocked, counter = O.search_defect_fast(O.Fast(p), k)
    return {"p": p, "k": k, "tally": tally, "fully blocked": blocked, "counterexamples": counter, "seconds": round(time.time() - t, 1)}


def ap_job(p):
    import odd_lib as O
    out = {"p": p, "sets": 0, "satisfiable": 0, "counterexamples": []}
    for A, P in O.ap_sets(p):
        out["sets"] += 1
        w1, w2 = O.test_set(sorted(set(P)), p)
        if w1 is not None:
            out["satisfiable"] += 1
            if w2 is None:
                out["counterexamples"].append({"steps": A, "word": "".join(map(str, w1))})
    return out


def run_part(part):
    import odd_lib as O
    if part in PLANS:
        jobs = sorted(PLANS[part], key=lambda j: -j[1])
        with Pool(min(16, len(jobs))) as pool:
            rows = pool.map(job, jobs, chunksize=1)
        return {"rows": sorted(rows, key=lambda r: (r["p"], r["k"]))}
    if part == "ap":
        primes = [p for p in range(31, 62, 2) if all(p % d for d in range(3, int(p ** 0.5) + 1, 2))]
        with Pool(len(primes)) as pool:
            return {"rows": pool.map(ap_job, primes)}
    if part == "route":
        out = []
        for name in ("p31", "p37", "targeted"):
            f = HERE / ("result_%s.json" % name)
            if not f.exists():
                continue
            for r in json.loads(f.read_text())["checks"]["result"]["rows"]:
                for b in r["fully blocked"]:
                    import numpy as np
                    c = np.array([int(x) for x in b["word"]], dtype=np.int8)
                    _, P, _ = O.Fast(r["p"]).analyse(c)
                    res = O.connected_to_complement(P, r["p"], b["word"])
                    out.append({"p": r["p"], "word": b["word"], "patterns": len(P), "reaches its flip": None if res is None else res[0],
                                "compatible words": None if res is None else res[1]})
        return {"rows": out}
    if part == "referee":
        r = subprocess.run([sys.executable, "-B", str(HERE / "odd_referee.py")], capture_output=True, text=True)
        print(r.stdout[-3000:], r.stderr[-3000:])
        return json.loads((HERE / "referee.json").read_text())


def summary():
    out = {}
    for name in ("p31", "p37", "targeted"):
        f = HERE / ("result_%s.json" % name)
        if not f.exists():
            out[name] = "dropped or not run"
            continue
        rows = json.loads(f.read_text())["checks"]["result"]["rows"]
        out[name] = {"%d k=%d" % (r["p"], r["k"]): dict(r["tally"], counterexamples=len(r["counterexamples"])) for r in rows}
    ap = json.loads((HERE / "result_ap.json").read_text())["checks"]["result"]["rows"] if (HERE / "result_ap.json").exists() else []
    out["ap"] = {str(r["p"]): {"sets": r["sets"], "satisfiable": r["satisfiable"], "counterexamples": len(r["counterexamples"])} for r in ap}
    c = lambda name: [x for r in json.loads((HERE / ("result_%s.json" % name)).read_text())["checks"]["result"]["rows"] for x in r["counterexamples"]] if (HERE / ("result_%s.json" % name)).exists() else []
    out["S1 no counterexample at p = 31 and 37"] = not c("p31") and not c("p37")
    out["S2 no counterexample in the targeted ranges"] = not c("targeted") and not any(r["counterexamples"] for r in ap)
    out["counterexamples"] = c("p31") + c("p37") + c("targeted") + [x for r in ap for x in r["counterexamples"]]
    return out


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    part = sys.argv[sys.argv.index("--part") + 1]
    write = "--write" in sys.argv
    res = summary() if part == "summary" else run_part(part)
    res = {"dependencies": {p: sha(p) for p in DEPS}, "result": res, "seconds": round(time.time() - T0, 1)}
    path = HERE / ("result_%s.json" % part if part != "summary" else "result.json")
    if write:
        path.write_text(json.dumps({"status": "passed", "checks": res}, indent=1, default=str) + "\n")
        print("wrote", path, round(time.time() - T0, 1), "s")
    else:
        old = json.loads(path.read_text())["checks"]
        same = json.dumps(old["result"], sort_keys=True, default=str) == json.dumps(json.loads(json.dumps(res["result"], default=str)), sort_keys=True)
        print("result reproduced" if same else "result differs")
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()
