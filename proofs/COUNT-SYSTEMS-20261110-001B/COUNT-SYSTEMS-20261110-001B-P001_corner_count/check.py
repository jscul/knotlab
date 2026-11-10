"""Checks for COUNT-SYSTEMS-20261110-001B: the sphere's count over corner agreements. Geometry from COUNT-NOTE-20261107-001B's sa_lib
(TWO-ROUND-BRIDGE-20261106-001B's count_lib): the lines, their Kasteleyn signs, and the corners (line, point, point, face).

    python3 -B check.py          verify against result.json
    python3 -B check.py --write  write result.json from a fresh run
"""
import hashlib
import importlib.util
import itertools
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SA = next((ROOT / "proofs/COUNT-NOTE-20261107-001B").iterdir())
spec = importlib.util.spec_from_file_location("sa_lib", SA / "sa_lib.py")
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
C = S.C
KS = range(2, 9)
LP_KS = range(2, 7)
OUT = {}
T0 = time.time()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)
    if not ok:
        print(json.dumps(info, indent=1, default=str)[:3000])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def geometry(k):
    lines, signs, n = S.sphere(k)
    sg = {(i, p): s for i, (L, s_) in enumerate(zip(lines, signs)) for p, s in zip(L, s_)}
    cs, fpts = C.corners([list(L) for L in lines], n)
    return lines, sg, n, cs, fpts


def agree(x, sg, l, a, b):
    return int((x[a] ^ sg[(l, a)]) == (x[b] ^ sg[(l, b)]))


def main():
    write = "--write" in sys.argv
    man = json.loads((HERE / "manifest.json").read_text())
    bound = man.get("parent_bindings", {})
    check("0_dependencies_bound", bool(bound) and all(sha(ROOT / p) == h for p, h in bound.items()), bound)

    info1, info2, info3, ok1, ok2, ok3 = {}, {}, {}, True, True, True
    for k in KS:
        lines, sg, n, cs, fpts = geometry(k)
        byl, byf = defaultdict(list), defaultdict(list)
        for c, (l, a, b, f) in enumerate(cs):
            byl[l].append(c)
            byf[f].append(c)
        # 1. every corner on one line and one face; three per line; two more faces than lines
        ok1 &= all(len(v) == 3 for v in byl.values()) and len(byl) == len(lines) and len(fpts) - len(lines) == 2
        info1[k] = {"points": n, "lines": len(lines), "faces": len(fpts), "corners": len(cs)}
        # 2. locally, under every assignment of a line's (face's) points: a line has 1 agreeing corner if satisfied, 3 if violated;
        # a face has an odd number. So every corner parity holds identically, and the integer facts are the contradiction.
        for l, crn in byl.items():
            pts = sorted({p for c in crn for p in cs[c][1:3]})
            for bits in itertools.product((0, 1), repeat=len(pts)):
                x = dict(zip(pts, bits))
                lits = [x[p] ^ sg[(l, p)] for p in pts]
                agreeing = sum(agree(x, sg, *cs[c][:3]) for c in crn)
                ok2 &= agreeing == (3 if len(set(lits)) == 1 else 1)
        for f, crn in byf.items():
            pts = sorted({p for c in crn for p in cs[c][1:3]})
            for bits in itertools.product((0, 1), repeat=len(pts)):
                x = dict(zip(pts, bits))
                ok2 &= sum(agree(x, sg, *cs[c][:3]) for c in crn) % 2 == 1
        info2[k] = {"lines": len(byl), "faces": len(byf)}
        # 3. the linear refutation over corner atoms: sum over lines of (sum e - 1) minus sum over faces of (sum e - 1) is F - L = 2
        # as a linear form it is the constant -(L - F) ... checked coefficient by coefficient
        coef = defaultdict(int)
        const = 0
        for l, crn in byl.items():
            for c in crn:
                coef[c] += 1
            const -= 1
        for f, crn in byf.items():
            for c in crn:
                coef[c] -= 1
            const += 1
        ok3 &= all(v == 0 for v in coef.values()) and const == 2
        info3[k] = {"line equalities": len(byl), "face inequalities": len(byf), "constant left": const}
        if k in LP_KS:
            # the LP over e in [0, 1] with every line's sum equal to 1 and every face's at least 1 is infeasible
            m = len(cs)
            A_eq = np.zeros((len(byl), m))
            for i, (l, crn) in enumerate(byl.items()):
                A_eq[i, crn] = 1
            A_ub = np.zeros((len(byf), m))
            for i, (f, crn) in enumerate(byf.items()):
                A_ub[i, crn] = -1
            r = linprog(np.zeros(m), A_ub=A_ub, b_ub=-np.ones(len(byf)), A_eq=A_eq, b_eq=np.ones(len(byl)), bounds=(0, 1), method="highs")
            info3[k]["LP over corner atoms"] = "infeasible" if r.status == 2 else "feasible"
            ok3 &= r.status == 2
            # the LP over the points alone (NAE as 1 <= sum of literals <= 2) is feasible at y = 1/2
            half = all(1 <= sum((0.5 if not sg[(i, p)] else 1 - 0.5) for p in L) <= 2 for i, L in enumerate(lines))
            info3[k]["LP over points at y = 1/2"] = "feasible" if half else "infeasible"
            ok3 &= half
    check("1_corners_lie_on_one_line_and_one_face", ok1, info1)
    check("2_every_corner_parity_holds_identically", ok2, {"lines and faces read under every local assignment": info2})
    check("3_linear_refutation_over_corner_atoms", ok3, info3)

    allok = all(v["pass"] for v in OUT.values())
    result = {"ticket": "COUNT-SYSTEMS-20261110-001B", "checks": OUT, "status": "passed" if allok else "failed",
              "seconds": round(time.time() - T0, 1)}
    path = HERE / "result.json"
    if write:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote", path)
    else:
        old = json.loads(path.read_text())
        same = {k: v["pass"] for k, v in old["checks"].items()} == {k: v["pass"] for k, v in OUT.items()}
        print("matches result.json" if same else "DIFFERS from result.json")
        sys.exit(0 if same and allok else 1)


if __name__ == "__main__":
    main()
