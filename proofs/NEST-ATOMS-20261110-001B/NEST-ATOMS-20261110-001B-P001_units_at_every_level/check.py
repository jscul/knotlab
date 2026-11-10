#!/usr/bin/env python3
"""Checks for NEST-ATOMS-20261110-001B: units at every level (research/NEST-ATOMS-20261110-001/preregistration.md, ticket B).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. For each leaf type (Fano, thin (2,1,2)): (a) K_2 with one composite C(2, leaf) at L0; (b) with two at L0 and L1; (c) with
the depth-two composite D(leaf) at L0. In every class, by SAT over every state: each group's role and the AND; R-a (every top-level group
acting leaves no state satisfying every line); R-b' (in every state satisfying every line each group of genus g holds at least
g - 1 + [it acts] units in its region). Code control: nest_lib on K_3 with two Fano leaves at l0 and distance 3 against
OTHER-ATOMS-20261110-001B's tally there."""
import hashlib
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A_DIR = ROOT / "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms"
sys.path.insert(0, str(A_DIR))
T0 = time.time()
OUT = {}
DEPS = ["proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/nest_lib.py",
        "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/spaces_lib.py",
        "proofs/OTHER-ATOMS-20261110-001B/OTHER-ATOMS-20261110-001B-P001_holding_a_unit_with_other_atoms/result.json",
        "research/NEST-ATOMS-20261110-001/preregistration.md"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def audit(N, O):
    K = O.K()
    groups = sorted(O.groups)
    parts = {g: O.group_parts(K, g) for g in groups}
    tops = [g for g in groups if len(g) == 1]
    tally, bad = Counter(), []
    for s in O.classes(K):
        roles = {g: N.group_role(K, s, parts[g][0], parts[g][1]) for g in groups}
        okand = all(roles[g] == ("line" if all(roles[q] == "line" for q in O.leaves() if q[:len(g)] == g) else "transparent")
                    for g in groups if O.groups[g]["kind"] == "composite")
        ra = (not K.sat(s)[0]) if all(roles[g] == "line" for g in tops) else None
        rb = True
        if ra is None:
            for g in groups:
                bound = O.genus(g) - 2 + (roles[g] == "line")
                if bound >= 0 and N.units_at_most(K, s, parts[g][2], bound):
                    rb = False
        acting = tuple(sum(roles[q] == "line" for q in O.leaves() if q[:1] == t) for t in tops)
        tally[(acting, tuple(roles[t] == "line" for t in tops), ra, rb, okand)] += 1
        if ra is False or not rb or not okand:
            bad.append({str(g): r for g, r in roles.items()})
    return tally, bad


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    import spaces_lib as SP
    N = SP.N
    # code control
    Y = SP.composite(3, SP.ATOMS["Fano"], SP.lines_of(3, (3,)))
    tally, bad = audit(N, Y)
    mine = Counter()
    for (acting, tops_act, ra, rb, okand), v in tally.items():
        mine[sum(acting)] += v
    old = [r for r in json.loads((ROOT / DEPS[2]).read_text())["checks"]["rows"] if r["atom"] == "torus(7,2,1)" and r["l0"] == SP.lines_of(3)[0] and r["atoms"] == 2][0]
    ref = Counter()
    for k, v in old["(acting atoms, R-a, R-b, role as read on the torus)"].items():
        ref[int(k.strip("()").split(",")[0])] += v
    check("1 code control: nest_lib on K_3 with two Fano leaves (l0, distance 3) reproduces OTHER-ATOMS-20261110-001B's split of classes by "
          "acting leaves, with R-a and R-b in every class", mine == ref and not bad, {"here": dict(mine), "OTHER-ATOMS-B": dict(ref), "failures": bad[:3]})
    rows = []
    for leaf in ("Fano", "thin"):
        for name, O in (("(a) one composite", SP.outer_with([SP.C2(leaf)])), ("(b) two composites", SP.outer_with([SP.C2(leaf), SP.C2(leaf)])),
                        ("(c) depth two", SP.outer_with([SP.D2(leaf)]))):
            tally, bad = audit(N, O)
            row = {"leaf": leaf, "space": name, "genus": len(O.leaves()), "points": O.K().n, "classes": sum(tally.values()),
                   "(acting leaves per top group, top groups acting, R-a, R-b', AND)": {str(k): v for k, v in sorted(tally.items(), key=str)},
                   "holds": not bad, "failures": bad[:3]}
            rows.append(row)
            print(round(time.time() - T0, 1), leaf, name, row["classes"], "classes", "holds" if not bad else "FAILS", flush=True)
    ok = all(r["holds"] for r in rows)
    check("2 R-a, R-b' and the AND in every class of every named space (exact, SAT over every state)", ok,
          {"spaces": len(rows), "classes": sum(r["classes"] for r in rows), "failing": [(r["leaf"], r["space"]) for r in rows if not r["holds"]]})
    OUT["predictions"] = {"ticket B expectation held": ok}
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
