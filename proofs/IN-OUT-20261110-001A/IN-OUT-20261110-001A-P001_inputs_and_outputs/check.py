#!/usr/bin/env python3
"""Checks for IN-OUT-20261110-001A: inputs and outputs (research/IN-OUT-20261110-001/preregistration.md, ticket A).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. Check 1 (exact): at every interface of S1 to S4 (each leaf's sides, each composite's sides), the map in every class,
with theorem D (every map self-dual) and lemma G (a gauge flip at an interface point negates that input or the output) checked on every
class. Check 2 (computed, frozen): the example learner at every interface, targets 1uu0, u10u, uuuu, 0uu1 and then the impossible
0001, learner seed 3000 + k for the k-th interface. Interfaces run in parallel."""
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
WL = "proofs/NATIVE-WRITE-20261110-001A/NATIVE-WRITE-20261110-001A-P001_native_writing/write_lib.py"
DEPS = [str((HERE / "io_lib.py").relative_to(ROOT)), WL, "research/IN-OUT-20261110-001/preregistration.md"]
TEST = ["S1 single K_3 thin", "S2 single K_3 Fano", "S3 two-level K_3 thin", "S4 two-level K_3 Fano"]
TARGETS = ["1uu0", "u10u", "uuuu", "0uu1", "0001"]
GATES = {"1uu0", "0uu1", "u10u", "u01u"}
NEG = {"0": "1", "1": "0", "u": "u", "x": "x"}


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def self_dual(m):
    return m[3] == NEG[m[0]] and m[2] == NEG[m[1]]


def gauged(s, K, p):
    """the law with point p's three sites flipped (a gauge flip at p, with the state flip that goes with it)"""
    t = list(s)
    for i in range(K.n):
        for k in range(3):
            if K.pt[i][k] == p:
                t[3 * i + k] ^= 1
    return t


def predicted(m, which):
    """lemma G: flipping input a or b relabels the inputs; flipping the output negates the readings"""
    order = {"a": [2, 3, 0, 1], "b": [1, 0, 3, 2]}
    if which == "o":
        return "".join(NEG[c] for c in m)
    return "".join(m[k] for k in order[which])


def census(name):
    import io_lib as I
    W = I.W
    sp = W.Space(name)
    rows = {}
    for iname, ports in I.interfaces(sp):
        c, dual, gauge = Counter(), True, True
        group = ("leaf", int(iname.split()[1])) if iname.startswith("leaf") else ("composite", int(iname.split()[1]))
        for s in sp.O.classes(sp.K):
            m = I.read_map(sp.K, s, ports)
            if group[0] == "leaf":
                act = group[1] in sp.acting(s)
            else:
                lines, outer, _ = sp.O.group_parts(sp.K, (group[1],))
                act = W.N.group_role(sp.K, s, lines, outer) == "line"
            c[("acting" if act else "transparent", "gate" if m in GATES else m)] += 1
            dual &= self_dual(m)
            for which, p in zip("abo", ports):
                gauge &= I.read_map(sp.K, gauged(s, sp.K, p), ports) == predicted(m, which)
        rows[iname] = {"ports": ports, "maps": {"%s, %s" % k: v for k, v in sorted(c.items())}, "every map self-dual (D)": dual,
                       "gauge flips act as lemma G says": gauge}
    return name, rows


def run(job):
    import io_lib as I
    name, iname, ports, seed = job
    sp = I.W.Space(name)
    t0 = time.time()
    rows = I.run_interface(sp, ports, TARGETS, seed)
    return name, iname, rows, round(time.time() - t0, 1)


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    import io_lib as I
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    with Pool(4) as pool:
        cen = dict(pool.map(census, TEST))
    ok1 = all(r["every map self-dual (D)"] and r["gauge flips act as lemma G says"] for v in cen.values() for r in v.values())
    check("1 census: the map at every interface in every class; theorem D and lemma G on every class (exact)", ok1, cen)
    jobs, k = [], 0
    for name in TEST:
        sp = I.W.Space(name)
        for iname, ports in I.interfaces(sp):
            jobs.append((name, iname, ports, 3000 + k))
            k += 1
    with Pool(len(jobs)) as pool:
        res = pool.map(run, jobs)
    rows = {"%s / %s" % (n, i): r for n, i, r, _ in res}
    def kind(key):
        return "composite" if "/ composite" in key else "leaf"
    writes = [(kind(key), j, r) for key, rr in rows.items() for j, r in enumerate(rr) if r["target"] != "0001"]
    oc = {g: dict(Counter(r["outcome"] for kk, j, r in writes if kk == g)) for g in ("leaf", "composite")}
    share = {g: sum(1 for kk, j, r in writes if kk == g and r["outcome"] == "learned, held") / max(1, sum(1 for kk, j, r in writes if kk == g))
             for g in ("leaf", "composite")}
    gate_on = {g: [r["steps"] for kk, j, r in writes if kk == g and j in (0, 3) and r["steps"] is not None] for g in ("leaf", "composite")}
    med = {g: (statistics.median(v) if v else None) for g, v in gate_on.items()}
    ctrl = [r for key, rr in rows.items() for r in rr if r["target"] == "0001"]
    inexact = sum(1 for kk, j, r in writes if r["outcome"] == "inexact stop") + sum(1 for r in ctrl if r["stopped"])
    check("2 learning from examples at every interface (computed, frozen)", True, {
        "outcomes": oc, "learned and held share": share,
        "L: leaves at least 90%": share["leaf"] >= 0.9, "C: composites at least 90%": share["composite"] >= 0.9,
        "A: the impossible 0001 never stopped": all(not r["stopped"] for r in ctrl), "0001 outcomes": dict(Counter(r["outcome"] for r in ctrl)),
        "R: inexact stops": inexact,
        "median steps to turn a gate on (targets 1uu0 and 0uu1, stopped writes)": med,
        "K: composite median at least 4 times the leaf median": (med["composite"] is not None and med["leaf"] is not None and med["composite"] >= 4 * med["leaf"])})
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
