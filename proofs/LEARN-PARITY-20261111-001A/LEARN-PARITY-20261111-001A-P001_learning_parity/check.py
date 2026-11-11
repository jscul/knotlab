#!/usr/bin/env python3
"""Checks for LEARN-PARITY-20261111-001A: a learned memory that computes parity (research/LEARN-PARITY-20261111-001/preregistration.md).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. Check 1 (exact): at each space's interface, the map in every class (parity must be realizable). Check 2 (computed,
frozen): ten runs per space (learner seed 9000 + k), targets 01101001, 10010110, 01101001 in turn, budget 8,000,000 steps per target,
every stop scored by SAT. Marks P1 and P2."""
import hashlib
import itertools
import json
import os
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
DEPS = [str((HERE / "parity_lib.py").relative_to(ROOT)),
        "proofs/THREE-IN-20261110-001B/THREE-IN-20261110-001B-P001_learning_a_map_of_three_points/io3_lib.py",
        "proofs/CREDIT-PIN-20261110-001B/CREDIT-PIN-20261110-001B-P001_credit_from_pinned_dissonance/credit_lib.py",
        "proofs/STURDY-PROBE-20261110-001A/STURDY-PROBE-20261110-001A-P001_a_sturdier_probe/probe_lib.py",
        "research/LEARN-PARITY-20261111-001/preregistration.md"]
TARGETS = ["01101001", "10010110", "01101001"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:1500], round(time.time() - T0, 1), "s", flush=True)


def realizable(which):
    import parity_lib as L
    sp = L.t1() if which == "T1" else L.t2()
    K = sp.K
    s0, Z = K.signing(), K.classes()
    maps = []
    for a in itertools.product((0, 1), repeat=len(Z)):
        s = list(s0)
        for ai, z in zip(a, Z):
            if ai:
                s = [u ^ w for u, w in zip(s, z)]
        maps.append(L.L3.read_map3(K, s, sp.ports))
    return which, {"maps by class": maps, "parity realizable": any(m in TARGETS for m in maps)}


def run(job):
    import parity_lib as L
    which, k = job
    sp = L.t1() if which == "T1" else L.t2()
    t0 = time.time()
    rows = L.run(sp, TARGETS, 9000 + k)
    return which, k, rows, round(time.time() - t0, 1)


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    real = dict(map(realizable, ("T1", "T2")))
    check("1 parity is realizable at each interface (exact)", all(v["parity realizable"] for v in real.values()), real)
    with Pool(20) as pool:
        res = pool.map(run, [(w, k) for w in ("T1", "T2") for k in range(10)])
    verdict = {}
    for w in ("T1", "T2"):
        rr = [r for ww, k, r, _ in res if ww == w]
        first = Counter(r[0]["outcome"] for r in rr)
        verdict[w] = {"first target outcomes": dict(first), "all targets outcomes": dict(Counter(x["outcome"] for r in rr for x in r)),
                      "learned and held at the first target": first["learned, held"],
                      "median steps of learned first targets": sorted(r[0]["steps"] for r in rr if r[0]["outcome"] == "learned, held")[
                          len([r for r in rr if r[0]["outcome"] == "learned, held"]) // 2] if first["learned, held"] else None,
                      "inexact stops": sum(1 for r in rr for x in r if x["outcome"] == "inexact stop")}
    check("2 learning parity from examples (computed, frozen)", True, {
        "verdicts": verdict, "P1: T1 learned and held in at least 8 of 10": verdict["T1"]["learned and held at the first target"] >= 8,
        "P2: T2 learned and held in at least 8 of 10": verdict["T2"]["learned and held at the first target"] >= 8})
    OUT["rows"] = {"%s run %d" % (w, k): r for w, k, r, _ in res}
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
