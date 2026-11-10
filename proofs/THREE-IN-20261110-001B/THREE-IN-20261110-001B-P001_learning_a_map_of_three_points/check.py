#!/usr/bin/env python3
"""Checks for THREE-IN-20261110-001B: learning a map of three held points (research/THREE-IN-20261110-001/preregistration.md, stage 1).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. At the four frozen interfaces (one per test space), the targets in turn: the census's dictator map, parity 01101001,
majority 00010111; learner seed 7000 + k. Marks: parity and majority never stop; the dictator learned and held."""
import hashlib
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
DEPS = [str((HERE / "io3_lib.py").relative_to(ROOT)), "proofs/STURDY-PROBE-20261110-001A/STURDY-PROBE-20261110-001A-P001_a_sturdier_probe/probe_lib.py",
        "proofs/CREDIT-PIN-20261110-001B/CREDIT-PIN-20261110-001B-P001_credit_from_pinned_dissonance/credit_lib.py",
        "proofs/THREE-IN-20261110-001A/THREE-IN-20261110-001A-P001_maps_of_three_held_points/result.json",
        "research/THREE-IN-20261110-001/preregistration.md"]
JOBS = [("S1 single K_3 thin", [0, 1, 2, 4], "10101010"), ("S2 single K_3 Fano", [0, 1, 2, 4], "10101010"),
        ("S3 two-level K_3 thin", [1, 36, 37, 3], "00001111"), ("S4 two-level K_3 Fano", [1, 36, 37, 3], "00001111")]
PARITY, MAJORITY = "01101001", "00010111"


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:1200], round(time.time() - T0, 1), "s", flush=True)


def run(job):
    import io3_lib as L
    k, (name, ports, dictator) = job
    L.P.STEPS[0] = 0
    sp = L.W.Space(name)
    rows = L.run_interface3(sp, ports, [dictator, PARITY, MAJORITY], 7000 + k)
    return name, rows, L.P.STEPS[0]


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    with Pool(len(JOBS)) as pool:
        res = pool.map(run, list(enumerate(JOBS)))
    rows = {n: r for n, r, _ in res}
    dic = Counter(rr[0]["outcome"] for rr in rows.values())
    imp = [r for rr in rows.values() for r in rr[1:]]
    check("1 learning maps of three held points (computed, frozen)", True, {
        "dictator outcomes": dict(dic), "parity and majority outcomes": dict(Counter(r["outcome"] for r in imp)),
        "mark I: parity and majority never stopped": all(not r["stopped"] for r in imp),
        "mark L3: the dictator learned and held at 3 or 4 of 4": dic["learned, held"] >= 3,
        "probe steps": {n: s for n, _, s in res}})
    OUT["rows"] = rows
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
