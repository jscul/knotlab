#!/usr/bin/env python3
"""Checks for PARITY-FIVE-20261111-001A (research/PARITY-FIVE-20261111-001/preregistration.md).

    .venv/bin/python3 -B check.py --part harness|search|extra|composed|learn [--write]
PYTHONHASHSEED=0. harness: the five-input harness run with three held inputs on LEARN-PARITY-20261111-001's torus T1 at seed 9000 must
reproduce that epic's first T1 run exactly (the learner unchanged), and the exact method must find three-input parity on the torus
(2, 0, 4) in class 3 only, at the sets (0, 1, 4, 5) and (2, 3, 6, 7). Every space: every class, its floor states by SAT (a class over 200,000 states is dropped by rule and counted), the exact
parity sets of size 4 (three held inputs) and size 6 (five held inputs); 600 seconds per space, over it the space is dropped by rule.
search: every simple non-degenerate lattice torus with 3 to 24 points; its size-4 tori up to 20 points must be exactly PARITY-NEEDS-
20261111-001's 16. extra (only if search finds no size-6 set): the lattice tori with 25 to 32 points. composed: K_2 with the torus
(2, 0, 4) grown at both its lines, genus 2. learn (only if some part found a size-6 set): the space with the fewest points that has one
(lattice tori before the composed space at equal size), its first set in sorted order, the first five points held and the last read;
targets five-input parity, its negation, parity; ten runs, seed 9100 + k, budget 8,000,000 steps per target, 90 minutes per run (over it the run is dropped by rule and counts as not learned); every stop
read by SAT."""
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
LIB = str((HERE / "five_lib.py").relative_to(ROOT))
PREREG = "research/PARITY-FIVE-20261111-001/preregistration.md"
PREV = "proofs/PARITY-NEEDS-20261111-001A/PARITY-NEEDS-20261111-001A-P001_the_parity_gadget_refereed/result_tori.json"
LEARNER = ["proofs/LEARN-PARITY-20261111-001A/LEARN-PARITY-20261111-001A-P001_learning_parity/parity_lib.py",
           "proofs/THREE-IN-20261110-001B/THREE-IN-20261110-001B-P001_learning_a_map_of_three_points/io3_lib.py",
           "proofs/CREDIT-PIN-20261110-001B/CREDIT-PIN-20261110-001B-P001_credit_from_pinned_dissonance/credit_lib.py",
           "proofs/STURDY-PROBE-20261110-001A/STURDY-PROBE-20261110-001A-P001_a_sturdier_probe/probe_lib.py"]
DEPS = {"harness": [LIB, PREREG] + LEARNER + [LEARNER[0].replace("parity_lib.py", "result.json")], "search": [LIB, PREREG, PREV], "extra": [LIB, PREREG], "composed": [LIB, PREREG] + LEARNER[:1],
        "learn": [LIB, PREREG] + LEARNER}
SPACE_CAP = 600
RUN_CAP = 5400


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def load(part):
    p = HERE / ("result_%s.json" % part)
    return json.loads(p.read_text())["checks"]["result"] if p.exists() else None


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def read_space(name, K, points):
    import five_lib as F
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(SPACE_CAP)
    try:
        rows = []
        for ci, s in enumerate(F.U.all_classes(K)):
            st = F.floor_states(K, s)
            if st is None:
                rows.append({"class": ci, "dropped (state cap)": True})
                continue
            rows.append({"class": ci, "floor states": len(st), "three-input sets": F.parity_sets(st, K.n, 4),
                         "five-input sets": F.parity_sets(st, K.n, 6) if K.n >= 6 else []})
        signal.alarm(0)
        return {"space": name, "points": points, "classes": rows}
    except Timeout:
        return {"space": name, "points": points, "dropped (time cap)": True}


def torus_job(job):
    import five_lib as F
    t, n = job
    return read_space(list(t), F.SL.KnotSpace(F.SL.torus(*t)), n)


def summary(rows):
    hits = [r for r in rows if any(c.get("five-input sets") for c in r.get("classes", []))]
    first = None
    for r in sorted(hits, key=lambda r: (r["points"], r["space"] == "composed", str(r["space"]))):
        c = next(c for c in r["classes"] if c.get("five-input sets"))
        T, val = c["five-input sets"][0]
        first = {"space": r["space"], "points": r["points"], "class": c["class"], "set": list(T), "check value": val}
        break
    return {"spaces": len(rows), "dropped (time cap)": [r["space"] for r in rows if r.get("dropped (time cap)")],
            "classes dropped (state cap)": sum(1 for r in rows for c in r.get("classes", []) if c.get("dropped (state cap)")),
            "three-input parity spaces": [r["space"] for r in rows if any(c.get("three-input sets") for c in r.get("classes", []))],
            "five-input parity spaces": [{"space": r["space"], "points": r["points"],
                                          "classes": {c["class"]: len(c["five-input sets"]) for c in r["classes"] if c.get("five-input sets")}}
                                         for r in hits],
            "F: a five-input parity set exists": bool(hits), "first": first}


def search():
    import five_lib as F
    with Pool(22) as pool:
        rows = pool.map(torus_job, F.tori(), chunksize=1)
    out = summary(rows)
    prev = json.loads((ROOT / PREV).read_text())["checks"]["result"]["rows"]
    prev3 = sorted(tuple(r["torus"]) for r in prev if "total parity" in r["first"])
    mine = sorted(tuple(r["space"]) for r in rows if r["points"] <= 20 and any(c.get("three-input sets") for c in r.get("classes", [])))
    out["V: three-input parity tori up to 20 points are exactly PARITY-NEEDS's"] = mine == prev3 and len(prev3) == 16
    out["rows"] = rows
    return out


def extra():
    import five_lib as F
    if load("search")["F: a five-input parity set exists"]:
        return {"not run": "search found a five-input parity set"}
    with Pool(22) as pool:
        rows = pool.map(torus_job, F.tori(25, F.EXTRA_N), chunksize=1)
    return dict(summary(rows), rows=rows)


def composed():
    import five_lib as F
    Y = F.composed()
    K = F.SL.KnotSpace(Y.S)
    rows = [read_space("composed", K, K.n)]
    return dict(summary(rows), genus=1 - K.chi // 2, rows=rows)


def harness():
    import five_lib as F
    PL = F._parity_lib()
    prev = json.loads((ROOT / LEARNER[0]).with_name("result.json").read_text())["checks"]["rows"]["T1 run 0"]
    rows = F.run(PL.t1(), ["01101001", "10010110", "01101001"], 9000)
    K = F.SL.KnotSpace(F.SL.torus(2, 0, 4))
    sets = {ci: F.parity_sets(F.floor_states(K, s), K.n, 4) for ci, s in enumerate(F.U.all_classes(K))}
    return {"V1: LEARN-PARITY's first T1 run reproduced": json.loads(json.dumps(rows)) == prev, "rows": rows,
            "V2: three-input sets on (2, 0, 4) as found before": {ci: v for ci, v in sets.items() if v} == {3: [((0, 1, 4, 5), 0), ((2, 3, 6, 7), 0)]},
            "three-input sets by class": sets}


def learn_job(found, targets, seed):
    import five_lib as F
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(RUN_CAP)
    try:
        rows = F.run_found(found, targets, seed)
        signal.alarm(0)
        return rows
    except Timeout:
        return [{"target": targets[0], "outcome": "dropped (time cap)"}]


def learn():
    import five_lib as F
    firsts = [r["first"] for r in (load("search"), load("extra"), load("composed")) if r and r.get("first")]
    if not firsts:
        return {"not run": "no five-input parity set in any part"}
    found = min(firsts, key=lambda f: (f["points"], f["space"] == "composed"))
    sp = F.space(found)
    targets = [F.parity_string(5, 0), F.parity_string(5, 1), F.parity_string(5, 0)]
    start = F.read_map_k(sp.K, sp.start()[0], sp.ports)
    with Pool(10) as pool:
        res = pool.starmap(learn_job, [(found, targets, 9100 + k) for k in range(10)])
    first = [r[0]["outcome"] for r in res]
    allo = [x["outcome"] for r in res for x in r]
    steps = sorted(r[0]["steps"] for r in res if r[0]["outcome"] == "learned, held")
    return {"space": found, "interface (five held, one read)": sp.ports, "targets": targets, "map at the start": start,
            "first target outcomes": {o: first.count(o) for o in sorted(set(first))},
            "all targets outcomes": {o: allo.count(o) for o in sorted(set(allo))},
            "median steps of learned first targets": steps[len(steps) // 2] if steps else None,
            "inexact stops": allo.count("inexact stop"),
            "P5: learned and held at the first target in at least 8 of 10": first.count("learned, held") >= 8, "rows": res}


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    part = sys.argv[sys.argv.index("--part") + 1]
    res = {"harness": harness, "search": search, "extra": extra, "composed": composed, "learn": learn}[part]()
    res = json.loads(json.dumps(res, default=str))
    out = {"dependencies": {p: sha(p) for p in DEPS[part]}, "result": res, "seconds": round(time.time() - T0, 1)}
    path = HERE / ("result_%s.json" % part)
    if "--write" in sys.argv:
        path.write_text(json.dumps({"status": "passed", "checks": out}, indent=1) + "\n")
        print("wrote", path, out["seconds"], "s")
        print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1)[:4000])
    else:
        old = json.loads(path.read_text())["checks"]["result"]
        same = json.dumps(old, sort_keys=True) == json.dumps(res, sort_keys=True)
        print("result reproduced" if same else "result differs")
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()
