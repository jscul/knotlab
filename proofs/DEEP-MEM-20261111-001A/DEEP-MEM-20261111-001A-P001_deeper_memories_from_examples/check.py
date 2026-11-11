#!/usr/bin/env python3
"""Checks for DEEP-MEM-20261111-001A: deeper memories from examples (research/DEEP-MEM-20261111-001/preregistration.md).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. Check 1 (exact): at every group of T1 to T3, whether some class with a floor state has the group acting with a gate on
its sides (the targets are realizable). Check 2 (computed, frozen): the credit learner with the sturdier probe at every group, targets
1uu0, u10u, uuuu, 0uu1, 0001, learner seed 8000 + k, budget 8,000,000 steps per target. Marks L, D1, D3, W3, A, R; costs by kind."""
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
T0 = time.time()
OUT = {}
DEPS = [str((HERE / "deep_lib.py").relative_to(ROOT)),
        "proofs/STURDY-PROBE-20261110-001A/STURDY-PROBE-20261110-001A-P001_a_sturdier_probe/probe_lib.py",
        "proofs/CREDIT-PIN-20261110-001B/CREDIT-PIN-20261110-001B-P001_credit_from_pinned_dissonance/credit_lib.py",
        "research/DEEP-MEM-20261111-001/preregistration.md"]
SPACES = ["T1 D2 D2 thin", "T2 C3 C3 thin", "T3 D2 D2 Fano"]
TARGETS = ["1uu0", "u10u", "uuuu", "0uu1", "0001"]
GATES = {"1uu0", "0uu1", "u10u", "u01u"}
BUDGET = 8_000_000


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:1500], round(time.time() - T0, 1), "s", flush=True)


def realizable(job):
    import deep_lib as L
    name, chunk = job
    sp = L.W.Space(name)
    K = sp.K
    gs = L.groups(sp)
    ok = {str(g): False for g, _, _ in gs}
    for s in sp.O.classes(K)[chunk::8]:
        if not L.W.has_floor_state(K, s, sp.floor2 // 2):
            continue
        for g, ports, kind in gs:
            if ok[str(g)]:
                continue
            lines, outer, _ = sp.O.group_parts(K, g)
            if L.W.N.group_role(K, s, lines, outer) == "line" and L.I.read_map(K, s, ports) in GATES:
                ok[str(g)] = True
    return name, ok


def run(job):
    import deep_lib as L
    name, g, ports, kind, seed = job
    L.P.STEPS[0] = 0
    sp = L.W.Space(name)
    rows = L.run(sp, ports, TARGETS, seed, BUDGET)
    return name, str(g), kind, rows, L.P.STEPS[0]


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    import deep_lib as L
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    with Pool(24) as pool:
        parts = pool.map(realizable, [(n, c) for n in SPACES for c in range(8)])
    real = {}
    for n, ok in parts:
        for g, v in ok.items():
            real.setdefault(n, {}).setdefault(g, False)
            real[n][g] |= v
    check("1 every gate target is realizable at every group (exact)", all(all(v.values()) for v in real.values()), real)
    jobs, k = [], 0
    for name in SPACES:
        sp = L.W.Space(name)
        for g, ports, kind in L.groups(sp):
            jobs.append((name, g, ports, kind, 8000 + k))
            k += 1
    with Pool(len(jobs)) as pool:
        res = pool.map(run, jobs)
    def cls(kind):
        return ("leaf" if kind == "leaf" else "one atom, depth 2" if kind.startswith("composite of 1") else
                "two atoms, depth 3" if kind.startswith("composite of 2") else "three atoms, depth 2")
    by = {}
    for name, g, kind, rows, steps in res:
        for j, r in enumerate(rows):
            c = "0001" if r["target"] == "0001" else cls(kind)
            by.setdefault(c, Counter())[r["outcome"]] += 1
    share = {c: round(v["learned, held"] / sum(v.values()), 3) for c, v in by.items() if c != "0001"}
    cost = {}
    for name, g, kind, rows, steps in res:
        for j in (0, 3):
            if rows[j]["outcome"] == "learned, held":
                cost.setdefault(cls(kind), []).append(rows[j]["steps"])
    inexact = sum(1 for _, _, _, rows, _ in res for r in rows if r["outcome"] == "inexact stop")
    and_stops = sum(1 for _, _, _, rows, _ in res for r in rows if r["target"] == "0001" and r["stopped"])
    check("2 learning at every group (computed, frozen)", True, {
        "outcomes": {c: dict(v) for c, v in by.items()}, "learned and held share": share,
        "L: leaves at least 90%": share.get("leaf", 0) >= 0.9,
        "D1: one-atom composites (depth 2) at least 90%": share.get("one atom, depth 2", 0) >= 0.9,
        "D3: two-atom composites at depth 3 at least 90%": share.get("two atoms, depth 3", 0) >= 0.9,
        "W3: three-atom composites at least 90%": share.get("three atoms, depth 2", 0) >= 0.9,
        "A: 0001 never stopped": and_stops == 0, "R: inexact stops": inexact,
        "median steps of learned gate-on writes": {c: (statistics.median(v), len(v)) for c, v in cost.items()},
        "probe steps": sum(s for *_, s in res)})
    OUT["rows"] = {"%s / %s" % (n, g): {"kind": kind, "rows": rows} for n, g, kind, rows, _ in res}
    OUT["seconds"] = round(time.time() - T0, 1)
    res_path = HERE / "result.json"
    if write:
        res_path.write_text(json.dumps({"status": "passed", "checks": OUT}, indent=1, default=str) + "\n")
        print("wrote", res_path)
    else:
        old = json.loads(res_path.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        diff = [k for k in OUT if k != "seconds" and json.dumps(old.get(k), sort_keys=True) != json.dumps(fresh[k], sort_keys=True)]
        print("result.json reproduced" if not diff else "result.json differs: %s" % diff)
        sys.exit(0 if not diff else 1)


if __name__ == "__main__":
    main()
