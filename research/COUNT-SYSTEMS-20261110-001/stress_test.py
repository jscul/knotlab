"""Stress test for COUNT-SYSTEMS-20261110-001, one size past each ticket's checks, with the tickets' own code:
A: the left-pigeon map to SINK on every instance with N = 4 (checked to 3), and 12 random instances with N = 4 through the grid colouring
(checked to N = 3); B: the corner identities and the corner LP on K_9 and K_10 (checked to K_8 and K_6).

    .venv/bin/python3 -B stress_test.py    writes stress_test.json beside it
"""
import importlib.util
import json
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


A = load("check_a", ROOT / "proofs/COUNT-SYSTEMS-20261110-001A/COUNT-SYSTEMS-20261110-001A-P001_bounded_depth_frege/check.py")
B = load("check_b", ROOT / "proofs/COUNT-SYSTEMS-20261110-001B/COUNT-SYSTEMS-20261110-001B-P001_corner_count/check.py")
T = A.T

if __name__ == "__main__":
    t0 = time.time()
    out = {}
    ok, n, sols = True, 0, 0
    for f, g in A.instances(4):
        succ, pred = A.to_sink(4, f, g)
        s = [v for v in range(5) if T.is_sink_solution(succ, pred, v)]
        n += 1
        sols += len(s)
        ok &= bool(s) and all(A.left_pigeon_violation(f, g, v) for v in s)
    out["A: left pigeon to SINK, N = 4, every instance"] = {"instances": n, "answers": sols, "pass": ok}
    rng = random.Random(20261111)
    L = T.layout(5)
    insts = rng.sample(list(A.instances(4)), 12)
    ok2, tri = True, 0
    for f, g in insts:
        succ, pred = A.to_sink(4, f, g)
        col, route, clash, cr = T.colouring(L, succ, pred)
        full = [t for t, o in T.full_triangles(col, L["m"]) if o == 1]
        ok2 &= not clash and bool(full)
        for t in full:
            v = T.back_map(succ, pred, T.triangle_node(L, t))
            ok2 &= T.is_sink_solution(succ, pred, v) and A.left_pigeon_violation(f, g, v)
            tri += 1
    out["A: composed through the grid colouring, N = 4, 12 random instances"] = {"grid side": L["m"], "triangles decoded": tri, "pass": ok2}
    for k in (9, 10):
        lines, sg, nn, cs, fpts = B.geometry(k)
        byl, byf = defaultdict(list), defaultdict(list)
        for c, (l, a, b, f) in enumerate(cs):
            byl[l].append(c)
            byf[f].append(c)
        coef = defaultdict(int)
        for crn in byl.values():
            for c in crn:
                coef[c] += 1
        for crn in byf.values():
            for c in crn:
                coef[c] -= 1
        m = len(cs)
        A_eq = np.zeros((len(byl), m))
        for i, crn in enumerate(byl.values()):
            A_eq[i, crn] = 1
        A_ub = np.zeros((len(byf), m))
        for i, crn in enumerate(byf.values()):
            A_ub[i, crn] = -1
        r = linprog(np.zeros(m), A_ub=A_ub, b_ub=-np.ones(len(byf)), A_eq=A_eq, b_eq=np.ones(len(byl)), bounds=(0, 1), method="highs")
        out["B: K_%d" % k] = {"points": nn, "faces minus lines": len(fpts) - len(lines), "sums cancel": all(v == 0 for v in coef.values()),
                              "corner LP": "infeasible" if r.status == 2 else "feasible",
                              "pass": len(fpts) - len(lines) == 2 and all(v == 0 for v in coef.values()) and r.status == 2}
    out["all pass"] = all(v["pass"] for v in out.values() if isinstance(v, dict))
    out["seconds"] = round(time.time() - t0, 1)
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
