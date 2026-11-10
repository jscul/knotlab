#!/usr/bin/env python3
"""Checks for MANY-POINTS-20261110-001C: writing with more addresses (research/MANY-POINTS-20261110-001/preregistration.md, ticket C).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0, random.Random(105). NEST-ATOMS-20261110-001C's procedure unchanged on space (b) (outer host K_2) and on the same space
with the outer host K_3, for the Fano and thin (2,1,2) leaves, the targets A1, A2, A4, A3 cycled six times (24 writes each)."""
import hashlib
import importlib.util
import json
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NA = ROOT / "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms"
sys.path.insert(0, str(NA))
T0 = time.time()
OUT = {}
SEQ = "proofs/ADDRESS-SEQ-20261110-001A/ADDRESS-SEQ-20261110-001A-P001_writing_in_sequence"
NC = "proofs/NEST-ATOMS-20261110-001C/NEST-ATOMS-20261110-001C-P001_a_two_level_address/check.py"
DEPS = [SEQ + "/seq_lib.py", NC, "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/spaces_lib.py",
        "research/MANY-POINTS-20261110-001/preregistration.md"]
TARGETS = [(0, 1, 2), (0, 2, 3), (0, 1, 3), (1, 2, 3)] * 6


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    Q = load("seq_lib", DEPS[0])
    NCm = load("nest_c", NC)
    import spaces_lib as SP
    N, SL = SP.N, SP.SL

    def role(K, Y, s, j):
        lines, outer, _ = Y.parts[j]
        return N.group_role(K, s, lines, outer)
    Q.LH.atom_role = role
    rng = random.Random(105)
    rows = []
    for host in (2, 3):
        for leaf in ("Fano", "thin"):
            O = N.Nested(SP.SPH[host].S, SP.SPH[host].s0)
            for l in SP.lines_of(host):
                Cc = SP.C2(leaf)
                O.grow_closed(O.where[l], Cc, SP.standard_point(Cc))
            K = O.K()
            Y = NCm.Shim(O, K)
            P = Q.C.Space(K, O.S)
            floor2 = abs(K.chi)
            levels = [Y.face_level(v) for v in range(K.V)]
            upper = [p for p in range(K.n) if O.path[K.points[p]] == ()]
            start = next(s for s in O.classes(K) if all(role(K, Y, s, j) == "transparent" for j in range(4)))
            model = K.sat(start)[1]
            cur = (sum(b << e for e, b in enumerate(start)), sum(int(model[p] > 0) << p for p in range(K.n)))
            prev = Q.acting(K, Y, cur[0], 4)
            for target in TARGETS:
                found, size = Q.search_from(Y, K, P, cur, set(target), 4, levels)
                step = {"host": f"K_{host}", "leaf": leaf, "target": target, "written": found is not None, "configurations": size}
                if found:
                    step["acting after write"] = Q.acting(K, Y, found[0], 4)
                    step["exact write"] = step["acting after write"] == target
                    s, x = found
                    x ^= 1 << rng.choice(upper)
                    s, x, w = Q.m1(P, s, x, floor2, rng)
                    after = Q.acting(K, Y, s, 4) if w == floor2 else None
                    step["acting after disturbance"] = after
                    step["outcome"] = ("held" if after == target else "not at the floor" if after is None
                                       else "previous address" if after == prev else "other")
                    prev = target
                    cur = (s, x) if w == floor2 else found
                rows.append(step)
            sub = [r for r in rows if r["host"] == f"K_{host}" and r["leaf"] == leaf]
            print(round(time.time() - T0, 1), host, leaf, dict(Counter(r.get("outcome", "not written") for r in sub)),
                  "exact writes", sum(r.get("exact write", False) for r in sub), flush=True)
    verdicts = []
    for leaf in ("Fano", "thin"):
        sub = [r for r in rows if r["leaf"] == leaf]
        held = sum(r.get("outcome") == "held" for r in sub)
        exact = [r for r in sub if r.get("exact write")]
        verdicts.append({"leaf": leaf, "writes": len(sub), "reached": sum(r["written"] for r in sub), "held": held, "held share": round(held / len(sub), 3),
                         "outcomes": dict(Counter(r.get("outcome", "not written") for r in sub)), "exact writes": len(exact),
                         "held among exact writes": sum(r.get("outcome") == "held" for r in exact),
                         "expected (>= 95% held)": all(r["written"] for r in sub) and held >= 0.95 * len(sub),
                         "failure (a write not reached, or under 80% held)": (not all(r["written"] for r in sub)) or held < 0.8 * len(sub)})
    check("1 writing with more addresses (computed)", True, {"verdicts": verdicts})
    OUT["predictions"] = {"expected for both leaf types": all(v["expected (>= 95% held)"] for v in verdicts),
                          "failure for some leaf type": any(v["failure (a write not reached, or under 80% held)"] for v in verdicts)}
    print(json.dumps(verdicts, indent=1), json.dumps(OUT["predictions"]), flush=True)
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
