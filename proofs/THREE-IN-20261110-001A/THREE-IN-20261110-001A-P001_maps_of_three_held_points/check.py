#!/usr/bin/env python3
"""Checks for THREE-IN-20261110-001A: the exact census of maps with three held points (research/THREE-IN-20261110-001/preregistration.md).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. On every class of the dev spaces and S1 to S4, at every group (leaf or top-level composite), every interface of
census_lib.interfaces: the map read exactly from the projection of the floor states onto the group's neighbourhood. Check 1: every map
is self-dual (theorem D of IN-OUT-20261110-001). Check 2: the kinds of map that occur, by space and group, with the group acting or not,
and the first instance of every total majority or parity map and of every partial non-unate map."""
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
DEPS = [str((HERE / "census_lib.py").relative_to(ROOT)), "proofs/IN-OUT-20261110-001A/IN-OUT-20261110-001A-P001_inputs_and_outputs/io_lib.py",
        "research/THREE-IN-20261110-001/preregistration.md"]
SPACES = ["dev thin", "dev Fano", "S1 single K_3 thin", "S2 single K_3 Fano", "S3 two-level K_3 thin", "S4 two-level K_3 Fano"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:1500], round(time.time() - T0, 1), "s", flush=True)


def census(name):
    import census_lib as C
    W = C.W
    sp = W.Space(name)
    K = sp.K
    counts, examples, dual, n_maps = Counter(), {}, True, 0
    for gname, ports in C.I.interfaces(sp):
        Np = C.neighbourhood(K, ports)
        idx = {p: j for j, p in enumerate(Np)}
        tups = C.interfaces(ports, Np)
        gk = gname.split()[0]
        for ci, s in enumerate(sp.O.classes(K)):
            if gk == "leaf":
                act = int(gname.split()[1]) in sp.acting(s)
            else:
                lines, outer, _ = sp.O.group_parts(K, (int(gname.split()[1]),))
                act = W.N.group_role(K, s, lines, outer) == "line"
            P = C.projection(K, s, Np)
            for ins, o in tups:
                m = C.read(P, idx, ins, o)
                n_maps += 1
                dual &= C.self_dual(m)
                k = C.kind(m)
                held = "sides" if set(ins) == set(ports) else "two sides and one point"
                counts[(gk, "acting" if act else "transparent", held, k)] += 1
                if k in ("total majority", "total parity", "partial, non-unate", "total other"):
                    key = "%s | %s | %s" % (gk, held, k)
                    if key not in examples:
                        examples[key] = {"group": gname, "class index": ci, "acting": act, "inputs": ins, "output": o, "map": m,
                                         "non-unate inputs": C.non_unate(m)}
    return name, {"maps read": n_maps, "every map self-dual": dual,
                  "kinds": {" | ".join(k): v for k, v in sorted(counts.items())}, "first instances": examples}


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    with Pool(len(SPACES)) as pool:
        res = dict(pool.map(census, SPACES))
    check("1 every map with three held points is self-dual (exact)", all(v["every map self-dual"] for v in res.values()),
          {n: v["maps read"] for n, v in res.items()})
    summary = Counter()
    for v in res.values():
        for k, c in v["kinds"].items():
            summary[k.split(" | ")[-1]] += c
    check("2 the kinds of map that occur (exact)", True, {"over all spaces": dict(summary), "by space": res})
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
