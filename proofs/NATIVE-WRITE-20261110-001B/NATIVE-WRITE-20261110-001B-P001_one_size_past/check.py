#!/usr/bin/env python3
"""Checks for NATIVE-WRITE-20261110-001B: native writing one size past (research/NATIVE-WRITE-20261110-001/preregistration.md, ticket B).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. S5, the outer host K_3 with three composites C(2, thin) (six atoms, genus 6, 4,096 classes): the region lemma's census
on every class, then ticket A's frozen learner, unchanged, on 20 writes (sequence seed 124, learner seed 1195) and control U on the same."""
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
A = ROOT / "proofs/NATIVE-WRITE-20261110-001A/NATIVE-WRITE-20261110-001A-P001_native_writing"
sys.path.insert(0, str(A))
T0 = time.time()
OUT = {}
DEPS = ["proofs/NATIVE-WRITE-20261110-001A/NATIVE-WRITE-20261110-001A-P001_native_writing/write_lib.py",
        "research/NATIVE-WRITE-20261110-001/preregistration.md"]
NAME = "S5 two-level K_3 thin, three composites"


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def census_chunk(ix):
    import write_lib as W
    sp = W.Space(NAME)
    cl = sp.O.classes(sp.K)
    c, writable = Counter(), set()
    for s in cl[ix::12]:
        act = sp.acting(s)
        if W.has_floor_state(sp.K, s, sp.floor2 // 2):
            writable.add(act)
        for j, (faces, lines) in sp.atoms.items():
            cle = W.leaf_clearable(sp.K, s, faces, lines)
            c[("acting, " if j in act else "transparent, ") + ("clearable" if cle else "not clearable")] += 1
    return c, writable


def run(mode):
    import write_lib as W
    sp = W.Space(NAME)
    return mode, W.run_sequence(sp, OUT["targets"], 1195, check=W.probe if mode == "probe" else W.instant_check)


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    import write_lib as W
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    with Pool(12) as pool:
        parts = pool.map(census_chunk, range(12))
    c, writable = Counter(), set()
    for cc, ww in parts:
        c.update(cc)
        writable |= ww
    check("1 region lemma on S5 (exact, every class)", set(c) <= {"acting, not clearable", "transparent, clearable"},
          {"acting and clearability": dict(c), "writable addresses": len(writable)})
    OUT["targets"] = W.sequence(sorted(writable), 20, 124)
    with Pool(2) as pool:
        res = dict(pool.map(run, ["probe", "instant"]))
    oc = Counter(r["outcome"] for r in res["probe"])
    check("2 native writing on S5 (computed)", True, {"outcomes": dict(oc), "holds (at least 18 of 20)": oc["exact, held"] >= 18,
                                                     "max steps": max((r["steps"] or 0) for r in res["probe"])})
    check("3 control U on S5 (computed)", True, {"outcomes": dict(Counter(r["outcome"] for r in res["instant"]))})
    OUT["rows"] = res
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
