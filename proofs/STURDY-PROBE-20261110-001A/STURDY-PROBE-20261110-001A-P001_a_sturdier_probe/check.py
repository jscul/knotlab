#!/usr/bin/env python3
"""Checks for STURDY-PROBE-20261110-001A: a sturdier probe (research/STURDY-PROBE-20261110-001/preregistration.md).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. Check 1: CREDIT-PIN-20261110-001A's run with the old probe counting its steps (it must reproduce that run's rows).
Check 2: the same run (fixed learner, S1 to S4, seeds 3000 + k) with the sturdier probe. Check 3: CREDIT-PIN-20261110-001B's run
(credit learner, S3 and S4 with seeds 3000 + k, S5 with 5000 + k) with the sturdier probe. Mark Z: no inexact stop and no 0001 stop in
checks 2 and 3."""
import hashlib
import json
import os
import statistics
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "proofs/CREDIT-PIN-20261110-001B/CREDIT-PIN-20261110-001B-P001_credit_from_pinned_dissonance"))
T0 = time.time()
OUT = {}
FA = "proofs/CREDIT-PIN-20261110-001A/CREDIT-PIN-20261110-001A-P001_the_fixed_learner"
FB = "proofs/CREDIT-PIN-20261110-001B/CREDIT-PIN-20261110-001B-P001_credit_from_pinned_dissonance"
DEPS = [str((HERE / "probe_lib.py").relative_to(ROOT)), FA + "/fix_lib.py", FA + "/result.json", FB + "/credit_lib.py", FB + "/result.json",
        "research/STURDY-PROBE-20261110-001/preregistration.md"]
SPACES = ["S1 single K_3 thin", "S2 single K_3 Fano", "S3 two-level K_3 thin", "S4 two-level K_3 Fano"]
S5 = "S5 two-level K_3 thin, three composites"
TARGETS = ["1uu0", "u10u", "uuuu", "0uu1", "0001"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def run(job):
    import probe_lib as P
    import credit_lib as C
    F = C.F
    name, iname, ports, seed, learner, probe = job
    P.I.probe = P.old_probe_counted if probe == "old" else P.sturdy_probe
    P.STEPS[0] = 0
    sp = F.W.Space(name)
    t0 = time.time()
    if learner == "fixed":
        rows = F.run_interface(sp, ports, TARGETS, seed)
    else:
        rows = F.run_interface(sp, ports, TARGETS, seed, params=C.PARAMS, learner=C.learn)
    return name, iname, learner, probe, rows, P.STEPS[0], round(time.time() - t0, 1)


def jobs_for(learner, probe):
    import credit_lib as C
    out, k = [], 0
    for name in SPACES:
        sp = C.W.Space(name)
        for iname, ports in C.I.interfaces(sp):
            if learner == "fixed" or name in SPACES[2:]:
                out.append((name, iname, ports, 3000 + k, learner, probe))
            k += 1
    if learner == "credit":
        sp5 = C.W.Space(S5)
        for k5, (iname, ports) in enumerate(C.I.interfaces(sp5)):
            out.append((S5, iname, ports, 5000 + k5, learner, probe))
    return out


def tally(res):
    rows = {"%s / %s" % (r[0], r[1]): r[4] for r in res}
    def kind(key):
        return "composite" if "/ composite" in key else "leaf"
    groups = {}
    for key, rr in rows.items():
        sp = "S5" if key.startswith("S5") else "S1-S4"
        for r in rr:
            g = (sp, "0001" if r["target"] == "0001" else kind(key))
            groups.setdefault(g, Counter())[r["outcome"]] += 1
    learner_steps = sum((r["steps"] if r["steps"] is not None else 4_000_000) for rr in rows.values() for r in rr)
    probe_steps = sum(r[5] for r in res)
    inexact = sum(1 for rr in rows.values() for r in rr if r["outcome"] == "inexact stop")
    and_stops = sum(1 for rr in rows.values() for r in rr if r["target"] == "0001" and r["stopped"])
    return rows, {"%s %s" % g: dict(c) for g, c in sorted(groups.items())}, learner_steps, probe_steps, inexact, and_stops, \
        round(sum(r[6] for r in res), 1)


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    out = {}
    for tag, learner, probe in (("old probe, fixed learner", "fixed", "old"), ("sturdier probe, fixed learner", "fixed", "sturdy"),
                                ("sturdier probe, credit learner", "credit", "sturdy")):
        with Pool(min(22, len(jobs_for(learner, probe)))) as pool:
            res = pool.map(run, jobs_for(learner, probe))
        out[tag] = tally(res)
        print(tag, out[tag][1:], round(time.time() - T0, 1), flush=True)
    prevA = json.loads((ROOT / FA / "result.json").read_text())["checks"]["rows"]
    rowsO = out["old probe, fixed learner"][0]
    same = all([r["outcome"] for r in rowsO[k]] == [r["outcome"] for r in prevA[k]] and
               [r["steps"] for r in rowsO[k]] == [r["steps"] for r in prevA[k]] for k in prevA)
    check("1 the old probe's step cost on CREDIT-PIN-20261110-001A's run (reproduces its rows)", same, {
        "outcomes": out["old probe, fixed learner"][1], "learner steps": out["old probe, fixed learner"][2],
        "probe steps": out["old probe, fixed learner"][3], "inexact stops": out["old probe, fixed learner"][4],
        "0001 stops": out["old probe, fixed learner"][5], "cpu seconds": out["old probe, fixed learner"][6]})
    for n, tag in ((2, "sturdier probe, fixed learner"), (3, "sturdier probe, credit learner")):
        o = out[tag]
        check("%d %s (computed, frozen)" % (n, tag), True, {"outcomes": o[1], "learner steps": o[2], "probe steps": o[3],
                                                         "inexact stops": o[4], "0001 stops": o[5], "cpu seconds": o[6]})
    z = sum(out[t][4] + out[t][5] for t in ("sturdier probe, fixed learner", "sturdier probe, credit learner"))
    OUT["mark Z: no inexact stop and no 0001 stop with the sturdier probe"] = {"pass": z == 0, "info": {"inexact or 0001 stops": z}}
    print("Z", z == 0, z, flush=True)
    OUT["rows"] = {t: out[t][0] for t in out}
    OUT["seconds"] = round(time.time() - T0, 1)
    res_path = HERE / "result.json"
    if write:
        res_path.write_text(json.dumps({"status": "passed", "checks": OUT}, indent=1, default=str) + "\n")
        print("wrote", res_path)
    else:
        old = json.loads(res_path.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        skip = {"seconds"}
        diff = [k for k in OUT if k not in skip and json.dumps(strip(old.get(k)), sort_keys=True) != json.dumps(strip(fresh[k]), sort_keys=True)]
        print("result.json reproduced" if not diff else "result.json differs: %s" % diff)
        sys.exit(0 if not diff else 1)


def strip(v):
    """cpu seconds vary between runs; compare everything else"""
    if isinstance(v, dict):
        return {k: strip(x) for k, x in v.items() if k != "cpu seconds"}
    return v


if __name__ == "__main__":
    main()
