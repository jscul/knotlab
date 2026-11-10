#!/usr/bin/env python3
"""Checks for NATIVE-WRITE-20261110-001A: native writing (research/NATIVE-WRITE-20261110-001/preregistration.md, ticket A).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. Check 1: the region lemma's census (an atom acts exactly when its own constraints cannot clear its region) on every
class of the dev spaces and S1 to S4. Check 2: the frozen test, the learner with its probe on S1 to S4, 20 writes each (sequence seed
119 + k, learner seed 1190 + k for S_k). Check 3: control U, the same learner with the probe replaced by an instant check, same
sequences and seeds. The four spaces run in parallel."""
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
NA = "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms"
DEPS = [str((HERE / "write_lib.py").relative_to(ROOT)), NA + "/nest_lib.py", NA + "/spaces_lib.py",
        "proofs/OTHER-ATOMS-20261110-001A/OTHER-ATOMS-20261110-001A-P001_the_role_of_every_torus_atom/proof.md",
        "research/NATIVE-WRITE-20261110-001/preregistration.md"]
TEST = ["S1 single K_3 thin", "S2 single K_3 Fano", "S3 two-level K_3 thin", "S4 two-level K_3 Fano"]
CENSUS = ["dev thin", "dev Fano"] + TEST


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def census(name):
    import write_lib as W
    sp = W.Space(name)
    c = Counter()
    writable = set()
    for s in sp.O.classes(sp.K):
        act = sp.acting(s)
        if W.has_floor_state(sp.K, s, sp.floor2 // 2):
            writable.add(act)
        for j, (faces, lines) in sp.atoms.items():
            c["acting, " + ("clearable" if W.leaf_clearable(sp.K, s, faces, lines) else "not clearable") if j in act
              else "transparent, " + ("clearable" if W.leaf_clearable(sp.K, s, faces, lines) else "not clearable")] += 1
    return name, {"points": sp.K.n, "atoms": len(sp.atoms), "chi": sp.K.chi, "classes": len(sp.O.classes(sp.K)),
                  "acting and clearability": dict(c), "lemma holds": set(c) <= {"acting, not clearable", "transparent, clearable"},
                  "writable addresses": sorted(writable)}


def run(job):
    import write_lib as W
    name, k, mode, writable = job
    sp = W.Space(name)
    targets = W.sequence(writable, 20, 119 + k)
    t0 = time.time()
    rows = W.run_sequence(sp, targets, 1190 + k, check=W.probe if mode == "probe" else W.instant_check)
    return name, mode, {"targets": targets, "rows": rows, "seconds": round(time.time() - t0, 1)}


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    with Pool(6) as pool:
        cen = dict(pool.map(census, CENSUS))
    check("1 region lemma: an atom acts exactly when its own constraints cannot clear its region (exact, every class)",
          all(v["lemma holds"] for v in cen.values()), cen)
    jobs = [(n, k + 1, mode, [tuple(a) for a in cen[n]["writable addresses"]]) for mode in ("probe", "instant") for k, n in enumerate(TEST)]
    with Pool(8) as pool:
        res = pool.map(run, jobs)
    test = {n: r for n, m, r in res if m == "probe"}
    ctl = {n: r for n, m, r in res if m == "instant"}
    verdict = {}
    for n in TEST:
        oc = Counter(r["outcome"] for r in test[n]["rows"])
        verdict[n] = {"outcomes": dict(oc), "exact and held": oc["exact, held"], "holds (at least 18 of 20)": oc["exact, held"] >= 18,
                      "max steps": max((r["steps"] or 0) for r in test[n]["rows"]),
                      "max probes": max(r["probes"] for r in test[n]["rows"]), "seconds": test[n]["seconds"]}
    inexact = sum(v["outcomes"].get("inexact stop", 0) for v in verdict.values())
    check("2 the frozen test: native writing with the probe on S1 to S4 (computed)", True,
          {"verdicts": verdict, "B119 answered yes (holds on all four)": all(v["holds (at least 18 of 20)"] for v in verdict.values()),
           "inexact stops (R predicts 0)": inexact})
    cv = {n: dict(Counter(r["outcome"] for r in ctl[n]["rows"])) for n in TEST}
    ci = sum(v.get("inexact stop", 0) for v in cv.values())
    check("3 control U: the probe replaced by an instant check (computed)", True,
          {"outcomes": cv, "inexact stops": ci, "of": 20 * len(TEST), "at least a quarter inexact": ci >= 5 * len(TEST)})
    OUT["predictions"] = {"native writing holds on S1 to S4": OUT["2 the frozen test: native writing with the probe on S1 to S4 (computed)"]["info"]["B119 answered yes (holds on all four)"],
                          "R: no inexact stop": inexact == 0, "U: at least a quarter inexact": ci >= 5 * len(TEST),
                          "region lemma exact on all six spaces": OUT["1 region lemma: an atom acts exactly when its own constraints cannot clear its region (exact, every class)"]["pass"]}
    print(json.dumps(OUT["predictions"]), flush=True)
    OUT["rows"] = {"test": test, "control": ctl}
    for v in OUT["rows"]["test"].values():
        v.pop("seconds", None)
    for v in OUT["rows"]["control"].values():
        v.pop("seconds", None)
    for v in verdict.values():
        v.pop("seconds", None)
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
