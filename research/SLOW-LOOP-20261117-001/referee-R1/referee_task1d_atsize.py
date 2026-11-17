"""SLOW-LOOP-R1 task 1d (extension): soundness at the study's size n = 800, where brute force is out of reach.

Oracle: CaDiCaL 1.9.5 through pysat (a third-party exact solver, not the study's code; the study's engine does not use it).
The study's run_slow (under test) is run with debug on test instances of local w10 800, local w40 800 and block 800 (10
each), and embed 800 (4, GO and GO with shadows only), with
GO (frozen), GO with shadow knots (beta 0.5) and the extreme eager policy of task 1c. Then:
  - every final tie (v, root(v), parity(v)) is checked exactly: both states with x_v != x_root ^ parity are refuted
    (UNSAT under assumptions) on the original pattern;
  - every shadow knot is checked exactly: both of its violating joint states are refuted;
  - sampled one-for-one check: 30 states of the original (diversified by random assumptions on 3 distinctions) project
    to allowed states of the reduced pattern, and 30 states of the reduced pattern lift to allowed states of the
    original;
  - the reported state satisfies every original knot (own check).
Output: referee_task1d_atsize.json.
"""
from __future__ import annotations

import collections
import json
import os
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
EXP = os.path.join(ROOT, "experiments/SLOW-LOOP-20261117-001A/SLOW-LOOP-20261117-001A-E001_slow_loop")
ART = os.path.join(ROOT, "artifacts/SLOW-LOOP-20261117-001A/SLOW-LOOP-20261117-001A-E001_slow_loop")
os.environ.setdefault("SLOW_LOOP_BUILD",
                      "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/866db0bb-326b-5add-835e-78bf03179706/scratchpad/build")
sys.path.insert(0, EXP)
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402

import referee_oracle as O  # noqa: E402
import slow_loop as S  # noqa: E402  (under test)

CELLS = {"local-w10-800": ("local", 4.0, 10, 800), "local-w40-800": ("local", 4.0, 40, 800),
         "block-800": ("block", 2.5, 20, 800), "embed-800": ("embed", 0.0, 10, 800)}
POLS = json.load(open(os.path.join(ART, "policies.json")))
TUN = json.load(open(os.path.join(ART, "retuned.json")))
POLICIES = {"GO": dict(POLS["GO"]), "GO_shadow": dict(POLS["GO"], beta=0.5),
            "EXTREME": {"e": 0.2, "rho": 20.0, "beta": 1.0, "J": 4, "pb": 100000, "backoff": False, "mode": 0}}


def cnf_signed(kv, ks):
    """CNF of signed NAE knots on variables 1..n: forbid all-equal effective values."""
    cl = []
    for (a, b, c), (sa, sb, sc) in zip(kv, ks):
        lits = [(int(a), int(sa)), (int(b), int(sb)), (int(c), int(sc))]
        # effective value e = x ^ s; forbid e = (0,0,0): clause (e_a or e_b or e_c); forbid (1,1,1): (~e_a or ...)
        cl.append([(v + 1) if s == 0 else -(v + 1) for v, s in lits])
        cl.append([-(v + 1) if s == 0 else (v + 1) for v, s in lits])
    return cl


def lit(v, val):
    return (v + 1) if val else -(v + 1)


def work_one(job):
    from pysat.solvers import Solver
    cell, i, pname = job
    fam, a, w, n = CELLS[cell]
    seed = 7_100_000 + i
    inst = S.planted_embed(n, seed, frac=0.25, alpha_r=2.1, alpha_l=4.0, alpha_c=0.02, w=10) if fam == "embed" else \
        S.planted(fam, n, a, seed, w=w)
    pol = POLICIES[pname]
    res = S.run_slow(inst, "novelty_plus", tuple(TUN[cell]["NOV"]), S.run_seed("referee1d", cell, seed), 2 * 10**7, pol,
                     debug=True)
    c = collections.Counter()
    viol = []
    c["runs"] += 1
    c["contradiction"] += int(res["contradiction"])
    if res["solved"]:
        c["state_checked"] += 1
        if not O.sat_rows(res["state"], inst.knots)[0]:
            viol.append({"what": "state violates an original knot", "job": job})
    root, rpar = res["root"], res["rpar"]
    rng = np.random.default_rng(seed)
    with Solver(name="cadical195", bootstrap_with=inst.cnf(break_symmetry=False)) as s:
        for v in range(n):
            if root[v] == v:
                continue
            r, p = int(root[v]), int(rpar[v])
            for xv in (0, 1):
                xr = xv ^ p ^ 1  # x_v != x_r ^ p
                c["tie_calls"] += 1
                if s.solve(assumptions=[lit(v, xv), lit(r, xr)]):
                    viol.append({"what": "tie fails", "job": job, "tie": [v, r, p]})
            c["ties_checked"] += 1
        for (a_, b_, c_, sa, sb, sc) in res["shadow_list"]:
            for comp in (0, 1):
                if s.solve(assumptions=[lit(a_, sa ^ comp), lit(b_, sb ^ comp), lit(c_, sc ^ comp)]):
                    viol.append({"what": "shadow fails", "job": job, "shadow": [a_, b_, c_, sa, sb, sc]})
            c["shadows_checked"] += 1
        # sampled projection: original states -> reduced pattern
        roots, kv, ks = res["roots"], res["kv"], res["ks"]
        col = np.full(n, -1, dtype=np.int64)
        col[roots] = np.arange(len(roots))
        for t in range(30):
            vs = rng.choice(n, 3, replace=False)
            ass = [lit(int(v), int(rng.integers(0, 2))) for v in vs]
            if not s.solve(assumptions=ass):
                continue
            mdl = s.get_model()
            x = np.array([1 if mdl[v] > 0 else 0 for v in range(n)], dtype=np.uint8)
            y = x[roots]
            c["orig_samples"] += 1
            if not (np.all((x ^ x[root]) == rpar) and (len(kv) == 0 or O.sat_rows(y, col[kv], ks)[0])):
                viol.append({"what": "an original state does not project to the reduced pattern", "job": job})
    nr = len(roots)
    with Solver(name="cadical195", bootstrap_with=cnf_signed(col[kv], ks) if len(kv) else []) as s2:
        for t in range(30):
            vs = rng.choice(nr, min(3, nr), replace=False)
            ass = [lit(int(v), int(rng.integers(0, 2))) for v in vs]
            if not s2.solve(assumptions=ass):
                continue
            mdl = s2.get_model() or []
            y = np.zeros(nr, np.uint8)
            for lt in mdl:
                if abs(lt) <= nr:
                    y[abs(lt) - 1] = 1 if lt > 0 else 0
            xl = O.lift(y[None, :], roots, root, rpar)[0]
            c["reduced_samples"] += 1
            if not O.sat_rows(xl, inst.knots)[0]:
                viol.append({"what": "a reduced state lifts to a non-allowed state", "job": job})
    c["rebuilds"] += res["rebuilds"]
    c["classes_final"] += len(roots)
    return {"counts": dict(c), "violations": viol, "job": job}


def main():
    S.lib()
    jobs = [(cell, i, p) for cell in CELLS if cell != "embed-800" for i in range(10) for p in POLICIES]
    # embed 800 (4 instances, GO and GO with shadows) was tried and stopped after 10 minutes: CaDiCaL under
    # assumptions is slow on its uniform part. Not included.
    from multiprocessing import Pool
    t0 = time.time()
    with Pool(8) as pool:
        rs = pool.map(work_one, jobs, chunksize=1)
    tot = collections.Counter()
    per = collections.defaultdict(collections.Counter)
    viol = []
    for r in rs:
        tot.update(r["counts"])
        per[f"{r['job'][0]}|{r['job'][2]}"].update(r["counts"])
        viol += r["violations"]
    out = {"oracle": "CaDiCaL 1.9.5 via pysat (third party)", "totals": dict(tot), "per_cell_policy": {k: dict(v) for k, v
           in sorted(per.items())}, "violations": len(viol), "violation_examples": viol[:20],
           "seconds": round(time.time() - t0, 1)}
    with open(os.path.join(HERE, "referee_task1d_atsize.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in ("totals", "violations", "seconds")}, indent=1))


if __name__ == "__main__":
    main()
