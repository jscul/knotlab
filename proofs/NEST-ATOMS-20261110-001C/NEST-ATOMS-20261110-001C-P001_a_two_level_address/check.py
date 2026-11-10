#!/usr/bin/env python3
"""Checks for NEST-ATOMS-20261110-001C: a two-level address (research/NEST-ATOMS-20261110-001/preregistration.md, ticket C).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0, random.Random(104). Space (b) of ticket B for each leaf type: K_2 with two composites C(2, leaf) at L0 and L1, leaves 0
and 1 in the first, 2 and 3 in the second, floor 3 units. ADDRESS-SEQ-20261110-001A's frozen targeted search (seq_lib.search_from) and
learner M1, unchanged, with a leaf's role read by SAT on its outer points; the acting leaf sets A1, A2, A4, A3, A1, A2 written in turn
from the class where every leaf is transparent and the solver's first satisfying state; after each write one random point of the outer
host flipped and M1 run to the floor."""
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
A_DIR = ROOT / "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms"
sys.path.insert(0, str(A_DIR))
T0 = time.time()
OUT = {}
SEQ = "proofs/ADDRESS-SEQ-20261110-001A/ADDRESS-SEQ-20261110-001A-P001_writing_in_sequence"
DEPS = [SEQ + "/seq_lib.py", "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/nest_lib.py",
        "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/spaces_lib.py",
        "proofs/NEST-ATOMS-20261110-001B/NEST-ATOMS-20261110-001B-P001_units_at_every_level/result.json",
        "research/NEST-ATOMS-20261110-001/preregistration.md"]
TARGETS = [(0, 1, 2), (0, 2, 3), (0, 1, 3), (1, 2, 3), (0, 1, 2), (0, 2, 3)]


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


class Shim:
    """what seq_lib reads of a layered space: a level per triangle (leaf index or "U") and a level per face"""

    def __init__(self, O, K):
        self.O, self.leaves = O, O.leaves()
        idx = {q: j for j, q in enumerate(self.leaves)}
        self.levels = [idx.get(O.path[t], "U") for t in range(O.S.nt)]
        self.parts = {j: O.group_parts(K, q) for q, j in idx.items()}
        self.tops = {t: O.group_parts(K, t) for t in sorted({q[:1] for q in self.leaves})}

    def face_level(self, v):
        levs = {self.levels[t] for t in range(self.O.S.nt) if v in self.O.S.vert[t]}
        if levs == {"U"}:
            return "upper"
        return "atom %d" % next(iter(levs)) if len(levs) == 1 else "junction"


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    Q = load("seq_lib", DEPS[0])
    import spaces_lib as SP
    N = SP.N

    def role(K, Y, s, j):
        lines, outer, _ = Y.parts[j]
        return N.group_role(K, s, lines, outer)
    Q.LH.atom_role = role
    rng = random.Random(104)
    rows, verdicts = [], []
    for leaf in ("Fano", "thin"):
        O = SP.outer_with([SP.C2(leaf), SP.C2(leaf)])
        K = O.K()
        Y = Shim(O, K)
        P = Q.C.Space(K, O.S)
        floor2 = abs(K.chi)
        levels = [Y.face_level(v) for v in range(K.V)]
        upper = [p for p in range(K.n) if O.path[K.points[p]] == ()]
        start = next(s for s in O.classes(K) if all(role(K, Y, s, j) == "transparent" for j in range(4)))
        ok, model = K.sat(start)
        assert ok
        x0 = [int(model[p] > 0) for p in range(K.n)]
        cur = (sum(b << e for e, b in enumerate(start)), sum(b << p for p, b in enumerate(x0)))

        def outer_addr(s_int):
            s = Q.bits(s_int, 3 * K.n)
            return tuple(t[0] for t, (lines, outer, _) in Y.tops.items() if N.group_role(K, s, lines, outer) == "line")
        steps = []
        prev = Q.acting(K, Y, cur[0], 4)
        for target in TARGETS:
            found, size = Q.search_from(Y, K, P, cur, set(target), 4, levels)
            step = {"target": target, "outer target": tuple(t for t in (0, 1) if {2 * t, 2 * t + 1} <= set(target)),
                    "written": found is not None, "configurations": size}
            if found:
                step["acting after write"] = Q.acting(K, Y, found[0], 4)
                step["outer after write"] = outer_addr(found[0])
                s, x = found
                x ^= 1 << rng.choice(upper)
                s, x, w = Q.m1(P, s, x, floor2, rng)
                after = Q.acting(K, Y, s, 4) if w == floor2 else None
                step["acting after disturbance"] = after
                step["outer after disturbance"] = outer_addr(s) if w == floor2 else None
                step["outcome"] = ("held" if after == tuple(target) else "not at the floor" if after is None
                                   else "previous address" if after == prev else "other")
                step["outer held"] = step["outer after disturbance"] == step["outer target"]
                prev = tuple(target)
                cur = (s, x) if w == floor2 else found
            steps.append(step)
            print(round(time.time() - T0, 1), leaf, target, step.get("outcome", "not written"), step.get("outer after disturbance"), size, flush=True)
        rows.append({"leaf": leaf, "points": K.n, "steps": steps})
        held = sum(st.get("outcome") == "held" for st in steps) / len(steps)
        outer = sum(bool(st.get("outer held")) for st in steps) / len(steps)
        verdicts.append({"leaf": leaf, "writes": len(steps), "written": sum(st["written"] for st in steps),
                         "outcomes": dict(Counter(st.get("outcome", "write failed") for st in steps)), "held share": round(held, 3),
                         "outer held share": round(outer, 3),
                         "outer held whenever held": all(st.get("outer held") for st in steps if st.get("outcome") == "held"),
                         "expected": all(st["written"] for st in steps) and held >= 0.95,
                         "failure": (not all(st["written"] for st in steps)) or held < 0.8})
    check("1 a two-level address written in sequence and returned (computed)", True, {"verdicts": verdicts})
    OUT["predictions"] = {"expected held for every leaf type": all(v["expected"] and v["outer held whenever held"] for v in verdicts),
                          "failure for some leaf type": any(v["failure"] for v in verdicts)}
    print(json.dumps(OUT["predictions"]), flush=True)
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
