#!/usr/bin/env python3
"""Stress test for OTHER-ATOMS-20261110-001, one size past ticket D: freeness and the unsatisfiable classes on every simple lattice torus
with 31 to 34 points, grouped up to isomorphism, by ticket D's method. Writes stress_test.json next to this file.

    .venv/bin/python3 -B research/OTHER-ATOMS-20261110-001/stress_test.py"""
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/OTHER-ATOMS-20261110-001A/OTHER-ATOMS-20261110-001A-P001_the_role_of_every_torus_atom"))


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    import atoms_lib as A
    SL, H = A.SL, A.H
    t0 = time.time()
    types = {}
    for N in range(31, 35):
        for t in SL.hnf_sublattices(N):
            if SL.torus_kind(*t) == "degenerate":
                continue
            S = SL.torus(*t)
            if SL.KnotSpace(S).simple():
                types.setdefault(A.canon(S), []).append((t, SL.torus_kind(*t)))
    rows = []
    for ms in types.values():
        t, kind = ms[0]
        T = H.Torus(*t)
        K = T.K
        p = K.pt[0][0]
        unsat, notfree = [], []
        for lab in H.LABELS:
            s = T.classes[lab]
            if not K.sat(s)[0]:
                unsat.append("%d%d" % lab)
            for e in sorted(K.point_sides[p]):
                s2 = list(s)
                s2[e] ^= 1
                if not K.sat(s2)[0]:
                    notfree.append(("%d%d" % lab, e))
        rows.append({"torus": "torus(%d,%d,%d)" % t, "points": T.n, "kind": kind, "unsatisfiable classes": unsat, "not free": notfree})
    out = {"types": len(rows), "every type free in every class": all(not r["not free"] for r in rows),
           "class-forced types": [(r["torus"], r["kind"], r["unsatisfiable classes"]) for r in rows if r["unsatisfiable classes"]],
           "class-forced are thin of even index with one unsatisfiable class": all(r["kind"] == "thin" and r["points"] % 2 == 0 and len(r["unsatisfiable classes"]) == 1
                                                                                   for r in rows if r["unsatisfiable classes"]),
           "seconds": round(time.time() - t0, 1), "rows": sorted(rows, key=lambda r: (r["points"], r["torus"]))}
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}))


if __name__ == "__main__":
    main()
