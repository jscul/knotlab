#!/usr/bin/env python3
"""Checks for UNATE-20261111-001A: are maps of held points unate (research/UNATE-20261111-001/preregistration.md).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. Check 1 (exact): THREE-IN-20261110-001's census on DEEP-MEM-20261111-001's spaces T1 and T3 (radius 1); the radius-2 census
on S1 was dropped as infeasible before any result was read. Check 2 (exact): random small knot
spaces, n = 6, 8, 10, 12 points, seeds 0 to 199 for each n, every class, every interface of three held points and one output. Check 3:
every non-unate instance re-read independently by SAT. Mark N: some map of held points is not unate."""
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
sys.path.insert(0, str(ROOT / "proofs/DEEP-MEM-20261111-001A/DEEP-MEM-20261111-001A-P001_deeper_memories_from_examples"))
T0 = time.time()
OUT = {}
DEPS = [str((HERE / "unate_lib.py").relative_to(ROOT)),
        "proofs/THREE-IN-20261110-001A/THREE-IN-20261110-001A-P001_maps_of_three_held_points/census_lib.py",
        "proofs/DEEP-MEM-20261111-001A/DEEP-MEM-20261111-001A-P001_deeper_memories_from_examples/deep_lib.py",
        "research/UNATE-20261111-001/preregistration.md"]
NS, SEEDS = (6, 8, 10, 12), range(200)
INTERESTING = ("total majority", "total parity", "partial, non-unate", "total other")
# Census 2 (S1 at radius 2) was dropped before any result was read: projecting the floor states onto its radius-2 neighbourhoods (26 to
# 29 of 45 points) by SAT enumeration had not finished one group after two hours (see the pre-registration's deviation note).
CENSUS = [("T1 D2 D2 thin", 1), ("T3 D2 D2 Fano", 1)]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:1500], round(time.time() - T0, 1), "s", flush=True)


def census(job):
    import deep_lib  # noqa: F401  (registers the deeper spaces)
    import unate_lib as U
    C = U.C
    name, radius = job
    sp = C.W.Space(name)
    K = sp.K
    counts, first, n_maps = Counter(), {}, 0
    for gname, ports in C.I.interfaces(sp):
        N1 = C.neighbourhood(K, ports)
        if radius == 1:
            Np, tups = N1, C.interfaces(ports, N1)
        else:
            Np = sorted({K.pt[i][k] for i in C.I.near_lines(K, N1, 0) for k in range(3)})
            sides, others = sorted(ports), [p for p in Np if p not in ports]
            tups = []
            for pair in __import__("itertools").combinations(sides, 2):
                for h in others:
                    ins = tuple(sorted(pair + (h,)))
                    tups += [(ins, o) for o in Np if o not in ins]
        idx = {p: j for j, p in enumerate(Np)}
        for ci, s in enumerate(sp.O.classes(K)):
            P = C.projection(K, s, Np)
            for ins, o in tups:
                m = C.read(P, idx, ins, o)
                k = C.kind(m)
                counts[k] += 1
                n_maps += 1
                if k in INTERESTING and k not in first:
                    first[k] = {"group": gname, "class index": ci, "inputs": ins, "output": o, "map": m}
    return "%s, radius %d" % (name, radius), {"maps": n_maps, "kinds": dict(counts), "first instances": first}


def search(job):
    import unate_lib as U
    n, seed = job
    S, K = U.space(n, seed)
    if not (S.connected() and K.simple()):
        return n, seed, None
    counts, first = Counter(), {}
    classes = U.all_classes(K)
    for ci, s in enumerate(classes):
        sols = U.floor_states(K, s)
        for (tri, o), mask in U.masks(sols, n).items():
            k = U.kind_of(mask)
            counts[k] += 1
            if k in INTERESTING and k not in first:
                first[k] = {"n": n, "seed": seed, "class index": ci, "inputs": tri, "output": o, "map": U.mask_map(mask)}
    return n, seed, {"genus": (2 - K.chi) // 2, "classes": len(classes), "kinds": dict(counts), "first instances": first}


def reread(inst):
    """the instance's map read again by SAT, independently of the brute-force enumeration"""
    import unate_lib as U
    S, K = U.space(inst["n"], inst["seed"])
    s = U.all_classes(K)[inst["class index"]]
    from pysat.solvers import Solver
    m = ""
    with Solver(name="cadical153", bootstrap_with=K.clauses(s)) as so:
        for x in U.C.PATTERNS:
            a = [(p + 1) if v else -(p + 1) for p, v in zip(inst["inputs"], x)]
            o = inst["output"]
            v0, v1 = so.solve(assumptions=a + [-(o + 1)]), so.solve(assumptions=a + [o + 1])
            m += "x" if not (v0 or v1) else ("u" if v0 and v1 else ("1" if v1 else "0"))
    return m == inst["map"], m


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    with Pool(len(CENSUS)) as pool:
        cen = dict(pool.map(census, CENSUS))
    nonunate_census = {k: v["first instances"] for k, v in cen.items() if v["first instances"]}
    check("1 census on the deeper spaces and at radius 2 (exact)", True, {"by space": cen, "non-unate or other found": nonunate_census})
    with Pool(22) as pool:
        res = pool.map(search, [(n, s) for n in NS for s in SEEDS], chunksize=4)
    by_n, firsts, skipped, genus = {}, {}, Counter(), Counter()
    for n, seed, r in res:
        if r is None:
            skipped[n] += 1
            continue
        genus[(n, r["genus"])] += 1
        c = by_n.setdefault(n, Counter())
        c.update(r["kinds"])
        for k, inst in r["first instances"].items():
            key = "%s (n=%d)" % (k, n)
            if key not in firsts or (inst["seed"] < firsts[key]["seed"]):
                firsts[key] = inst
    check("2 random small knot spaces, every class and interface (exact)", True, {
        "kinds by n": {n: dict(c) for n, c in by_n.items()}, "skipped (disconnected)": dict(skipped),
        "spaces by (n, genus)": {"%d, %d" % k: v for k, v in sorted(genus.items())}, "first instances": firsts})
    rr = {k: reread(v) for k, v in firsts.items()}
    check("3 every recorded instance re-read by SAT", all(ok for ok, _ in rr.values()), rr)
    found = bool(nonunate_census) or bool(firsts)
    OUT["mark N: some map of held points is not unate"] = {"pass": found, "info": {"census": bool(nonunate_census), "random spaces": sorted(firsts)}}
    print("N", found, flush=True)
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
