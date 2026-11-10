#!/usr/bin/env python3
"""Checks for GROW-STUCK-20261110-001A: a learner that grows only when stuck.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, PYTHONHASHSEED=0. Check 1 confirms the floor W >= |chi|/2 on every configuration visited (a proved identity); check 2 is the
computation P3."""
import hashlib
import importlib.util
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import stuck_lib as S_  # noqa: E402

SL = S_.SL
T0 = time.time()
OUT = {}
DEPS = ["proofs/GROW-HANDLE-20261110-001A/GROW-HANDLE-20261110-001A-P001_a_fano_atom_grown_at_the_dissonance/grow_lib.py",
        "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py",
        "research/GROW-STUCK-20261110-001/preregistration.md"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)
    if not ok and not os.environ.get("NOEXIT"):
        sys.exit(1)


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    spec = importlib.util.spec_from_file_location("steer_lib", ROOT / DEPS[1])
    L = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(L)
    rows = []
    for k in (2, 3, 4, 5):
        S = SL.octahedral_sphere(k)
        sph = L.Sphere(S, f"K_{k}")
        reps, orbit = S_.G.line_orbits(S)
        for l0 in reps:
            x = sph.flat_state(sph.K.lines.index(l0))
            for r in (1, 2, 3, 4):
                rec = S_.grow_r(S, sph.s0, x, r)
                rows.append({"sphere": f"K_{k}", "l0": l0, "r": r, "first decision stuck": rec["first decision stuck"],
                             "first growth at l0": bool(rec["growths"]) and rec["growths"][0]["line"] == l0,
                             "growths": len(rec["growths"]), "resolved": rec["resolved"], "sign changes": rec["sign changes"],
                             "final chi": rec["chi"], "final W": rec["W"], "floor respected": rec["floor respected"],
                             "stopped": rec.get("stopped"), "growth sites": [g["at"] for g in rec["growths"]]})
            print("  K_%d line %d" % (k, l0), round(time.time() - T0, 1), flush=True)
    check("1 P0: W >= |chi| / 2 on every configuration GROW-r visited", all(r["floor respected"] for r in rows),
          {"runs": len(rows)})
    by = Counter((r["r"] >= 3, r["growths"], r["resolved"], r["final chi"], r["final W"]) for r in rows)
    p1 = all(r["first decision stuck"] and r["first growth at l0"] for r in rows)
    p3a = all(r["growths"] == 1 and r["resolved"] and r["sign changes"] == 3 for r in rows if r["r"] >= 3)
    p3b = all(not r["resolved"] and r["growths"] >= 2 for r in rows if r["r"] <= 2)
    check("2 P1 and P3 (computed): on every start the first decision is stuck and the first growth is at l0; with r >= 3 GROW-r grows once and "
          "resolves in 3 sign changes; with r <= 2 it grows again and never resolves", p1 and p3a and p3b,
          {"P1": p1, "P3, r >= 3": p3a, "P3, r <= 2": p3b,
           "(r >= 3, growths, resolved, final chi, final W)": {str(k): v for k, v in sorted(by.items(), key=str)}, "rows": rows})
    OUT["seconds"] = round(time.time() - T0, 1)
    res = HERE / "result.json"
    if write:
        res.write_text(json.dumps({"status": "passed", "checks": OUT}, indent=1, default=str) + "\n")
        print("wrote", res)
    else:
        old = json.loads(res.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        diff = [k for k in OUT if k != "seconds" and json.dumps(old.get(k, {}).get("info"), sort_keys=True)
                != json.dumps(fresh[k]["info"], sort_keys=True)]
        print("result.json reproduced" if not diff else "result.json differs: %s" % diff)
        sys.exit(0 if not diff else 1)


if __name__ == "__main__":
    main()
