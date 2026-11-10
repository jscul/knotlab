#!/usr/bin/env python3
"""Checks for NATIVE-ATOM-20261110-001A: uniform growth (research/NATIVE-ATOM-20261110-001/preregistration.md, ticket A).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. For each lattice-torus type of OTHER-ATOMS-20261110-001D (every simple lattice torus to 30 points, thin tori of even
index to 40, grouped up to isomorphism) and each of the 8 uniform sign patterns (one sign per side index on every line): whether the law
has no even face, whether it is satisfiable, and its class against the torus's unsatisfiable class."""
import hashlib
import itertools
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A_DIR = "proofs/OTHER-ATOMS-20261110-001A/OTHER-ATOMS-20261110-001A-P001_the_role_of_every_torus_atom"
T0 = time.time()
OUT = {}
DEPS = [A_DIR + "/atoms_lib.py", "proofs/OTHER-ATOMS-20261110-001D/OTHER-ATOMS-20261110-001D-P001_free_tori/result.json",
        "research/NATIVE-ATOM-20261110-001/preregistration.md"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    sys.path.insert(0, str(ROOT / A_DIR))
    import atoms_lib as A
    H = A.H
    Drows = json.loads((ROOT / DEPS[1]).read_text())["checks"]["rows"]
    rows, bad = [], []
    for r in Drows:
        t = tuple(int(v) for v in r["torus"][6:-1].split(","))
        T = H.Torus(*t)
        K = T.K
        for p in itertools.product((0, 1), repeat=3):
            s = [p[k] for i in range(K.n) for k in range(3)]
            kast = K.even_faces(s) == []
            sat = K.sat(s)[0]
            lab = T.label(s) if kast else None
            row = {"torus": r["torus"], "points": T.n, "pattern": "".join(map(str, p)), "no even face": kast, "satisfiable": sat,
                   "class": lab, "in the unsatisfiable class": (lab in [tuple(f) for f in T.forced]) if kast else None}
            rows.append(row)
            expect_unsat = t == (7, 2, 1) and p[0] == p[1] == p[2]
            if not kast or sat == expect_unsat:
                bad.append(row)
    unsat = [r for r in rows if not r["satisfiable"]]
    check("1 census: every uniform law has no even face and is satisfiable, except the Fano torus's constant laws", not bad,
          {"types": len(Drows), "laws": len(rows), "unsatisfiable": [(r["torus"], r["pattern"]) for r in unsat], "exceptions": bad[:10],
           "class-forced types whose uniform laws are all satisfiable": sorted({r["torus"] for r in rows if r["torus"] != "torus(7,2,1)" and
                                                                                any(x["torus"] == r["torus"] for x in Drows if x["unsatisfiable classes"])})})
    OUT["predictions"] = {"census as expected": not bad, "failure line crossed": bool(bad)}
    OUT["rows"] = rows
    OUT["seconds"] = round(time.time() - T0, 1)
    print(json.dumps(OUT["predictions"]), flush=True)
    res = HERE / "result.json"
    if write:
        res.write_text(json.dumps({"status": "passed", "checks": OUT}, indent=1, default=str) + "\n")
        print("wrote", res)
    else:
        old = json.loads(res.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        diff = [k for k in OUT if k != "seconds" and json.dumps(old.get(k, {}).get("info") if isinstance(old.get(k), dict) and "info" in old.get(k, {}) else old.get(k), sort_keys=True)
                != json.dumps(fresh[k]["info"] if isinstance(fresh[k], dict) and "info" in fresh[k] else fresh[k], sort_keys=True)]
        print("result.json reproduced" if not diff else "result.json differs: %s" % diff)
        sys.exit(0 if not diff else 1)


if __name__ == "__main__":
    main()
