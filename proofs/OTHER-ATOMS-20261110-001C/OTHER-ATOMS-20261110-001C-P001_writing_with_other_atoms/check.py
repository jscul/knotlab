#!/usr/bin/env python3
"""Checks for OTHER-ATOMS-20261110-001C: writing with other atoms (tier T3 of research/OTHER-ATOMS-20261110-001/preregistration.md).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. ADDRESS-SEQ-20261110-001A's procedure (seq_lib: the frozen targeted search from any start, the learner M1) unchanged
except for the atom: growth uses multi_lib.grow_one with the atom's torus and Kasteleyn law, and an atom's role is read by SAT (six allowed
patterns: acts as its line; eight: transparent) instead of by enumerating the Fano atom's six inner points. K_3, every line orbit, three atoms
at l0 and distances 2 and 3, the six two-atom addresses in turn, after each write one random sphere point flipped and M1 run.
Code control: the Fano atom with random.Random(88) reproduces ADDRESS-SEQ's K_3 rows exactly. Main run: random.Random(97)."""
import hashlib
import importlib.util
import itertools
import json
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
T0 = time.time()
OUT = {}
SEQ = "proofs/ADDRESS-SEQ-20261110-001A/ADDRESS-SEQ-20261110-001A-P001_writing_in_sequence"
DEPS = [SEQ + "/seq_lib.py", SEQ + "/result.json",
        "proofs/OTHER-ATOMS-20261110-001A/OTHER-ATOMS-20261110-001A-P001_the_role_of_every_torus_atom/atoms_lib.py",
        "proofs/OTHER-ATOMS-20261110-001B/OTHER-ATOMS-20261110-001B-P001_holding_a_unit_with_other_atoms/multi_lib.py",
        "proofs/OTHER-ATOMS-20261110-001B/OTHER-ATOMS-20261110-001B-P001_holding_a_unit_with_other_atoms/result.json",
        "research/OTHER-ATOMS-20261110-001/preregistration.md"]
SEQ3 = [(0, 1), (1, 2), (0, 2), (0, 1), (1, 2), (0, 2)]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def atom_role_sat(K, Y, s, j):
    """'line' if atom j allows six patterns on its three outer points, 'transparent' if eight, else the count (by SAT)"""
    from pysat.solvers import Solver
    lines = [i for i in range(K.n) if Y.levels[K.lines[i]] == j]
    pts = {K.pt[i][k] for i in lines for k in range(3)}
    outer = sorted(p for p in pts if Y.levels[K.points[p]] != j)
    assert len(outer) == 3
    cl = []
    for i in lines:
        L = [(K.pt[i][k] + 1) * (1 if s[3 * i + k] == 0 else -1) for k in range(3)]
        cl += [L, [-a for a in L]]
    with Solver(name="cadical153", bootstrap_with=cl) as so:
        allowed = sum(1 for pat in itertools.product((0, 1), repeat=3)
                      if so.solve(assumptions=[(p + 1) if b else -(p + 1) for p, b in zip(outer, pat)]))
    return {6: "line", 8: "transparent"}.get(allowed, str(allowed))


def run(Q, rng, l0s):
    rows = []
    for l0 in l0s:
        Y = Q.space(3, l0, (2, 3))
        K = Y.K()
        P = Q.C.Space(K, Y.S)
        floor2 = abs(K.chi)
        levels = [Y.face_level(v) for v in range(K.V)]
        upper = [p for p in range(K.n) if Y.levels[K.points[p]] == "U"]
        cur = (sum(b << e for e, b in enumerate(Y.s)), sum(b << p for p, b in enumerate(Y.x)))
        prev_addr = Q.acting(K, Y, cur[0], 3)
        steps = []
        for target in SEQ3:
            found, size = Q.search_from(Y, K, P, cur, set(target), 3, levels)
            step = {"target": target, "written": found is not None, "configurations": size}
            if found:
                step["acting after write"] = Q.acting(K, Y, found[0], 3)
                s, x = found
                x ^= 1 << rng.choice(upper)
                s, x, w = Q.m1(P, s, x, floor2, rng)
                after = Q.acting(K, Y, s, 3) if w == floor2 else None
                step["acting after disturbance"] = after
                step["outcome"] = ("held" if after == tuple(target) else "not at the floor" if after is None
                                   else "previous address" if after == prev_addr else "other")
                prev_addr = tuple(target)
                cur = (s, x) if w == floor2 else found
            steps.append(step)
        rows.append({"sphere": "K_3", "l0": l0, "atoms": 3, "steps": steps})
    return rows


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    Q = load("seq_lib", DEPS[0])
    M = load("multi_lib", DEPS[3])
    A = M.A
    state = {}
    Q.LL.ST.grow_any = lambda S, s, x, t: M.grow_one(S, s, x, t, state["atom"])
    Q.LH.atom_role = atom_role_sat
    l0s = Q.ST.G.line_orbits(Q.SL.octahedral_sphere(3))[0]
    # code control
    state["atom"] = A.Atom((7, 2, 1))
    assert state["atom"].s == [0] * len(state["atom"].s)
    ctrl = run(Q, random.Random(88), l0s)
    old = [r for r in json.loads((ROOT / DEPS[1]).read_text())["checks"]["1 A (computed): sequences of addresses written with a disturbance between writes"]["info"]["rows"]
           if r["sphere"] == "K_3" and r["atoms"] == 3]
    same = json.loads(json.dumps(ctrl)) == json.loads(json.dumps(old))
    check("1 code control: the Fano atom through the patched code with random.Random(88) reproduces ADDRESS-SEQ-20261110-001A's K_3 rows exactly",
          same, {"rows": len(ctrl), "ADDRESS-SEQ rows": len(old)})
    # main run
    passing = json.loads((ROOT / DEPS[4]).read_text())["checks"]["predictions"]["atoms passing T2"]
    order = ["torus(7,2,1)", "torus(2,1,2)", "torus(3,2,2)", "torus(4,3,2)"]
    rng = random.Random(97)
    verdicts, allrows = [], []
    for name in [n for n in order if n in passing]:
        state["atom"] = A.Atom(tuple(int(v) for v in name[6:-1].split(",")))
        rows = run(Q, rng, l0s)
        for r in rows:
            r["atom"] = name
        allrows += rows
        sts = [st for r in rows for st in r["steps"]]
        tally = Counter(st.get("outcome", "write failed") for st in sts)
        held = tally.get("held", 0) / len(sts)
        verdicts.append({"atom": name, "writes": len(sts), "written": sum(st["written"] for st in sts), "outcomes": dict(tally),
                         "held share": round(held, 3), "T3": all(st["written"] for st in sts) and held >= 0.95,
                         "failure (a write not reached, or under 80% held)": (not all(st["written"] for st in sts)) or held < 0.8,
                         "configurations searched": sum(st["configurations"] for st in sts)})
        print(round(time.time() - T0, 1), name, verdicts[-1], flush=True)
    check("2 T3 (computed): writing in sequence with each atom passing T1 and T2, random.Random(97)", True, {"verdicts": verdicts})
    OUT["predictions"] = {"P4: every atom tested passes T3": all(v["T3"] for v in verdicts),
                          "atoms passing T3": [v["atom"] for v in verdicts if v["T3"]],
                          "atoms failing T3": [v["atom"] for v in verdicts if v["failure (a write not reached, or under 80% held)"]]}
    print(json.dumps(OUT["predictions"]), flush=True)
    OUT["rows"] = allrows
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
