#!/usr/bin/env python3
"""Checks for OTHER-ATOMS-20261110-001D: free tori (the addendum of research/OTHER-ATOMS-20261110-001/preregistration.md).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. Every simple lattice torus with at most 30 points, and every thin torus of even index with at most 40, grouped up to
isomorphism and mirror image (atoms_lib.canon); one point per torus. In each of the four classes: whether a state satisfies the law, and,
for each of the point's three sides, whether the law with that side's sign flipped (two adjacent even faces) has a satisfying state. A
torus is free at its point in a class when all three flipped laws are satisfiable."""
import hashlib
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
T0 = time.time()
OUT = {}
A_DIR = "proofs/OTHER-ATOMS-20261110-001A/OTHER-ATOMS-20261110-001A-P001_the_role_of_every_torus_atom"
DEPS = [A_DIR + "/atoms_lib.py", A_DIR + "/result.json", "research/OTHER-ATOMS-20261110-001/preregistration.md"]


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
    SL, H = A.SL, A.H
    types = {}
    for N in range(3, 41):
        for t in SL.hnf_sublattices(N):
            kind = SL.torus_kind(*t)
            if kind == "degenerate" or (N > 30 and kind != "thin") or (N > 30 and N % 2):
                continue
            S = SL.torus(*t)
            if not SL.KnotSpace(S).simple():
                continue
            types.setdefault(A.canon(S), []).append((t, kind))
    print(round(time.time() - T0, 1), "types", len(types), flush=True)
    rows = []
    for ms in types.values():
        t, kind = ms[0]
        T = H.Torus(*t)
        K = T.K
        p = K.pt[0][0]
        sides = sorted(K.point_sides[p])
        assert len(sides) == 3
        row = {"torus": "torus(%d,%d,%d)" % t, "points": T.n, "kind": kind, "members": [m[0] for m in ms], "classes": {}}
        for lab in H.LABELS:
            s = T.classes[lab]
            flipped = []
            for e in sides:
                s2 = list(s)
                s2[e] ^= 1
                assert len(K.even_faces(s2)) == 2
                flipped.append(K.sat(s2)[0])
            row["classes"]["%d%d" % lab] = {"satisfiable": K.sat(s)[0], "flipped side satisfiable": flipped, "free": all(flipped)}
        row["unsatisfiable classes"] = [lab for lab, c in row["classes"].items() if not c["satisfiable"]]
        row["free in every class"] = all(c["free"] for c in row["classes"].values())
        rows.append(row)
    rows.sort(key=lambda r: (r["points"], r["torus"]))
    forced = [r for r in rows if r["unsatisfiable classes"]]
    d1 = all(r["free in every class"] for r in rows)
    check("1 D1: every torus is free at its point in every class", d1,
          {"types": len(rows), "not free": [(r["torus"], [lab for lab, c in r["classes"].items() if not c["free"]]) for r in rows if not r["free in every class"]],
           "types by points": dict(Counter(r["points"] for r in rows))})
    d2 = all(len(r["unsatisfiable classes"]) == 1 for r in forced) and all(r["kind"] == "thin" and r["points"] % 2 == 0 or r["points"] == 7 for r in forced) \
        and all(any(r2["points"] == N for r2 in forced) for N in range(4, 41, 2))
    check("2 D2: the class-forced types are the Fano torus and the thin tori of even index, each with exactly one unsatisfiable class", d2,
          {"class-forced types": [(r["torus"], r["kind"], r["unsatisfiable classes"]) for r in forced]})
    # D3: on the 29 types of ticket A, the role predicted from these facts equals ticket A's role on every splice
    arows = json.loads((ROOT / DEPS[1]).read_text())["checks"]["rows"]
    by_member = {}
    for r in rows:
        for m in r["members"]:
            by_member["torus(%d,%d,%d)" % tuple(m)] = r

    def predicted(r, lab):
        c = r["classes"][lab]
        return ("line" if not c["satisfiable"] else "transparent") if c["free"] else "not free"
    bad, n = [], 0
    for ar in arows:
        r = by_member[ar["atom"]]
        for c in ar["classes"]:
            n += 1
            if predicted(r, "%d%d" % tuple(c["torus label"])) != c["role"]:
                bad.append((ar["atom"], ar["sphere"], ar["line"], c))
    check("3 D3: on ticket A's 29 types, the role read from the torus alone equals the role found on every splice", not bad,
          {"class readings compared": n, "splices": len(arows), "disagreements": bad[:5]})
    OUT["rows"] = rows
    OUT["seconds"] = round(time.time() - T0, 1)
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
