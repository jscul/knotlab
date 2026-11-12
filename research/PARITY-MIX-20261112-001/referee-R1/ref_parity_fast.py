#!/usr/bin/env python3
"""Referee PARITY-MIX-R1, a lighter survival check for the largest harmonies: each copy's bits satisfy the harmony's own kinds
cyclically (for a harmony these words are exactly its states W), with the stitches and parity knots as in ref_parity.py, no class
variables. A state check per translation class of placements on 4 x 4; every member of a surviving class is then analysed with
ref_parity.analyse (the one-hot encoding). Rows are written as each class finishes.

    python3 -B ref_parity_fast.py <harmony name> [n] [kinds as JSON]      (appends to result_p4_fast.jsonl, or result_alt4_fast.jsonl
                                                                          with another kind set)"""
import itertools
import json
import os
import sys
import time
from pathlib import Path

from pysat.solvers import Glucose4, Solver

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ref_parity as RP  # noqa: E402
import ref_parity_enum as E  # noqa: E402


def light_cnf(st, n, K):
    P = st["P"]
    var = lambda x, i: x * P + (i % P) + 1
    nxt = n * n * P + 1
    cl = []
    v = lambda r, c: (r % n) * n + (c % n)
    for x in range(n * n):
        for a, b in st["kinds"]:
            for i in range(P):
                t = [var(x, i), var(x, i + a), var(x, i + b)]
                cl += [t, [-l for l in t]]
    for r in range(n):
        for c in range(n):
            x, y, z = v(r, c), v(r, c + 1), v(r + 1, c)
            if r * n + c in K:
                t = nxt
                nxt += 1
                for i in range(P):
                    lits = [var(x, i), var(y, i), var(z, i), t]
                    for sg in itertools.product((1, -1), repeat=4):
                        if sum(s < 0 for s in sg) % 2:
                            cl.append([s * l for s, l in zip(sg, lits)])
            else:
                for a, b in st["kinds"]:
                    for i in range(P):
                        t3 = [var(x, i), var(y, i + a), var(z, i + b)]
                        cl += [t3, [-l for l in t3]]
    return cl


def main():
    name = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    hs = {RP.setup(h)["name"]: h for h in RP.hs()}
    h = dict(hs[name])
    out = HERE / "result_p4_fast.jsonl"
    if len(sys.argv) > 3:
        h["kinds"] = json.loads(sys.argv[3])
        out = HERE / "result_alt4_fast.jsonl"
    st = RP.setup(h)
    func = RP.census(st)["functional slots"]
    t0 = time.time()
    done = 0
    solver = os.environ.get("REF_SOLVER")       # e.g. cadical153 for the slowest classes (default Glucose 4)
    skip = set()
    resume = Path(os.environ["REF_RESUME"]) if os.environ.get("REF_RESUME") else None   # skip classes already in this file
    if os.environ.get("REF_OUT"):
        out = HERE / os.environ["REF_OUT"]
    if resume and resume.exists():
        for line in resume.read_text().splitlines():
            d = json.loads(line)
            if d["harmony"] == name and d.get("kinds", st["kinds"]) == st["kinds"]:
                skip.add(frozenset(d["rows"][0]["cells"]))
    for orb in RP.classes(n, n):
        if any(frozenset(K) in skip for K in orb):
            continue
        with (Solver(name=solver, bootstrap_with=light_cnf(st, n, orb[0])) if solver else Glucose4(bootstrap_with=light_cnf(st, n, orb[0]))) as s:
            alive = s.solve()
        analyse = (lambda K: {"cells": sorted(K), **E.analyse_light(st, n, K, func)}) if os.environ.get("REF_LIGHT_FIX") else \
            (lambda K: {"cells": sorted(K), **RP.analyse(st, n, n, K, func)})
        rows = [analyse(K) for K in orb] if alive else \
               [{"cells": sorted(K), "k": len(K), "state": False} for K in orb]
        with open(out, "a") as fh:
            fh.write(json.dumps({"harmony": name, "kinds": st["kinds"], "n": n, "rows": rows}) + "\n")
        done += 1
        if done % 200 == 0:
            print(done, "classes", round(time.time() - t0), "s", flush=True)
    print("done", name, round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
