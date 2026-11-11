#!/usr/bin/env python3
"""After the run (not pre-registered): why the composed space computes nothing. For the one-atom memory (LEARN-PARITY-20261111-001's T2)
and the composed space, every class: the whole space of parity checks of the floor states (the orthogonal complement of their differences),
its dimension, the points tied in pairs (checks of weight 2) and the parity sets of size 4. Also the sizes of the three-input parity tori
in the search.

    .venv/bin/python3 -B after_run.py [--write]"""
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import five_lib as F  # noqa: E402

T0 = time.time()


def nullspace(rows, n):
    piv = F.echelon(rows)
    out = []
    for f in (p for p in range(n) if p not in piv):
        v = 1 << f
        for b, r in piv.items():
            if (r >> f) & 1:
                v |= 1 << b
        out.append(v)
    return out


def read(K):
    rows = []
    for ci, s in enumerate(F.U.all_classes(K)):
        st = F.floor_states(K, s)
        N = nullspace([x ^ st[0] for x in st], K.n)
        checks = []
        for c in itertools.product((0, 1), repeat=len(N)):
            v = 0
            for b, w in zip(c, N):
                v ^= w if b else 0
            if v:
                checks.append([p for p in range(K.n) if (v >> p) & 1])
        full = [T for T in checks if len({tuple((x >> p) & 1 for p in T[:-1]) for x in st}) == 2 ** (len(T) - 1)]
        rows.append({"class": ci, "floor states": len(st), "check dimension": len(N),
                     "tied pairs": [T for T in checks if len(T) == 2], "parity sets of size 4": [T for T in full if len(T) == 4]})
    return rows


def main():
    PL = F._parity_lib()
    t2 = PL.t2()
    Y = F.composed()
    K = F.SL.KnotSpace(Y.S)
    search = json.loads((HERE / "result_search.json").read_text())["checks"]["result"]
    sizes = {str(r["space"]): r["points"] for r in search["rows"]}
    out = {"one-atom memory (T2)": read(t2.K), "T2 host points": [p for p in range(t2.K.n) if t2.nested.path[t2.K.points[p]] == ()],
           "composed": read(K),
           "three-input parity tori by points": sorted((sizes[str(t)], t) for t in search["three-input parity spaces"]),
           "seconds": None}
    out["seconds"] = round(time.time() - T0, 1)
    if "--write" in sys.argv:
        (HERE / "result_after.json").write_text(json.dumps(out, indent=1) + "\n")
    for k in ("one-atom memory (T2)", "composed"):
        for r in out[k]:
            print(k, r["class"], r["floor states"], r["check dimension"], len(r["tied pairs"]), r["parity sets of size 4"])
    print(out["three-input parity tori by points"], out["seconds"], "s")


if __name__ == "__main__":
    main()
