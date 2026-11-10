#!/usr/bin/env python3
"""Checks for ADDRESS-SEQ-20261110-001A: writing in sequence.

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0, random.Random(88). See research/ADDRESS-SEQ-20261110-001/preregistration.md."""
import hashlib
import json
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
T0 = time.time()
OUT = {}


def check(name, info):
    OUT[name] = {"pass": True, "info": info}
    print("PASS", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    import seq_lib as Q
    write = "--write" in sys.argv
    rng = random.Random(88)
    plans = [(3, (2, 3), None), (4, (2, 3), None), (5, (2, 3), 3), (3, (2, 3, 4), None)]
    seq3 = [(0, 1), (1, 2), (0, 2), (0, 1), (1, 2), (0, 2)]
    seq4 = [(0, 1, 2), (1, 2, 3), (0, 2, 3), (0, 1, 3)] * 2
    rows = []
    for kk, dists, orbits in plans:
        reps, _ = Q.ST.G.line_orbits(Q.SL.octahedral_sphere(kk))
        for l0 in (reps[:orbits] if orbits else reps):
            Y = Q.space(kk, l0, dists)
            K = Y.K()
            P = Q.C.Space(K, Y.S)
            n_atoms = len(dists) + 1
            floor2 = abs(K.chi)
            levels = [Y.face_level(v) for v in range(K.V)]
            upper = [p for p in range(K.n) if Y.levels[K.points[p]] == "U"]
            cur = (sum(b << e for e, b in enumerate(Y.s)), sum(b << p for p, b in enumerate(Y.x)))
            prev_addr = Q.acting(K, Y, cur[0], n_atoms)
            steps = []
            for target in (seq3 if n_atoms == 3 else seq4):
                found, size = Q.search_from(Y, K, P, cur, set(target), n_atoms, levels)
                step = {"target": target, "written": found is not None, "configurations": size}
                if found:
                    step["acting after write"] = Q.acting(K, Y, found[0], n_atoms)
                    s, x = found
                    x ^= 1 << rng.choice(upper)
                    s, x, w = Q.m1(P, s, x, floor2, rng)
                    after = Q.acting(K, Y, s, n_atoms) if w == floor2 else None
                    step["acting after disturbance"] = after
                    step["outcome"] = ("held" if after == tuple(target) else "not at the floor" if after is None
                                       else "previous address" if after == prev_addr else "other")
                    prev_addr = tuple(target)
                    cur = (s, x) if w == floor2 else found
                steps.append(step)
            row = {"sphere": f"K_{kk}", "l0": l0, "atoms": n_atoms, "steps": steps}
            rows.append(row)
            print(round(time.time() - T0, 1), row["sphere"], l0, n_atoms, [(st["written"], st.get("outcome")) for st in steps], flush=True)
    first = [r["steps"][0] for r in rows]
    later = [st for r in rows for st in r["steps"][1:]]
    tally = Counter(st.get("outcome", "write failed") for r in rows for st in r["steps"])
    held_later = sum(1 for st in later if st.get("outcome") == "held") / len(later)
    check("1 A (computed): sequences of addresses written with a disturbance between writes", {
        "outcomes": dict(tally), "writes": sum(1 for r in rows for st in r["steps"]), "written": sum(1 for r in rows for st in r["steps"] if st["written"]),
        "first writes written": sum(st["written"] for st in first), "of first": len(first),
        "later writes written": sum(st["written"] for st in later), "of later": len(later), "later held share": round(held_later, 3),
        "expected (every write, >= 95% held)": tally.get("held", 0) >= 0.95 * sum(tally.values()) and all(st["written"] for r in rows for st in r["steps"]),
        "failure (later fail where first succeeded, or later held < 80%)": held_later < 0.8 or any(r["steps"][0]["written"] and not all(st["written"] for st in r["steps"][1:]) for r in rows),
        "rows": rows})
    OUT["seconds"] = round(time.time() - T0, 1)
    res = HERE / "result.json"
    if write:
        res.write_text(json.dumps({"status": "passed", "checks": OUT}, indent=1, default=str) + "\n")
        print("wrote", res)
    else:
        old = json.loads(res.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        diff = [k for k in OUT if k != "seconds" and json.dumps(old.get(k, {}).get("info"), sort_keys=True) != json.dumps(fresh[k]["info"], sort_keys=True)]
        print("result.json reproduced" if not diff else "result.json differs: %s" % diff)
        sys.exit(0 if not diff else 1)


if __name__ == "__main__":
    main()
