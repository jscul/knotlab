"""Gate G of WHERE-NEXT-20261116-001A, copied and extended for SCALE-MEMORY-20261116-001A and MEET-TRANSFER-20261117-001A
(G1 also runs flag 32 and the block family; G6 compares with SCALE-MEMORY's engine, on the rules and its L3sm policy too) (G1 also runs the
scale-free flag 16; G6 checks that this engine reproduces WHERE-NEXT's engine run for run on every rule and on the
trained L3 policy): the engine, the instances and the exact solver are checked before
any learned arm is scored. Exits non-zero on any failure.

  G0 the knot law passes K1-K3 (knotlab check);
  G1 small instances: every planted instance allows its hidden state, brute force finds the same allowed set
     size as a second count, and every arm's reported solution satisfies every knot;
  G2 incremental counts equal recomputation after 10,000 random flips (several instances);
  G3 zero weights choose uniformly: the policy at zero weights has the random agent's run-length law (KS test);
  G4 a mutant probSAT that prefers breaking (cb < 0) is slower than probSAT;
  G5 every CaDiCaL model satisfies every knot, and CaDiCaL agrees with brute force on satisfiability.
"""
from __future__ import annotations

import itertools
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine as E  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
ARMS = [("rw", ()), ("walksat", (0.3,)), ("probsat_poly", (2.3, 1.0)), ("probsat_exp", (2.5,)),
        ("novelty_plus", (0.3, 0.01)), ("greedy_where", (2.3, 1.0, 0.2)), ("sticky", (2.3, 1.0, 0.5)),
        ("fms", (0.3,))]
POLICY_FLAGS = [0, E.LEARN_WHERE, E.LEARN_WHERE | E.MEM_AGE | E.MEM_RNN, E.LEARN_WHERE | E.WHAT_PROBSAT,
                E.LEARN_WHERE | E.MEM_AGE | E.MEM_RNN | E.MEM_SF, E.MEM_AGE | E.MEM_RNN | E.MEM_SF,
                E.LEARN_WHERE | E.MEM_AGE | E.MEM_RNN | E.MEM_SF | E.DEGNORM, E.LEARN_WHERE | E.DEGNORM]
OLD = ROOT / "experiments/SCALE-MEMORY-20261116-001A/SCALE-MEMORY-20261116-001A-E001_scale_memory"
OLD_L3SM = ROOT / "artifacts/SCALE-MEMORY-20261116-001A/SCALE-MEMORY-20261116-001A-E001_scale_memory/training/runs/L3sm_s0/theta_best.npy"
OLD_L3 = ROOT / "artifacts/WHERE-NEXT-20261116-001A/WHERE-NEXT-20261116-001A-E001_where_next/training/runs/L3_s1/theta_best.npy"


def brute_count(inst: E.Instance) -> int:
    n = inst.n
    xs = ((np.arange(2 ** n)[:, None] >> np.arange(n)) & 1).astype(np.int8)
    s = xs[:, inst.knots].sum(axis=2)
    return int(np.all((s == 1) | (s == 2), axis=1).sum())


def main() -> int:
    fails = []
    # G0
    r = subprocess.run([sys.executable, "-B", "-m", "knotlab", "check", "--cnf", "a b c; ~a ~b ~c", "--loops", "a", "b",
                        "--contact", "c", "--json"], capture_output=True, text=True,
                       env={**os.environ, "PYTHONPATH": str(ROOT / "tools")}, cwd=ROOT)
    g0 = json.loads(r.stdout)
    if not g0["is_knot"]:
        fails.append("G0 not a knot")
    print("G0 knot law K1-K3:", g0["is_knot"], g0["allowed"])

    # G1 and G5 on small instances
    rng = np.random.default_rng(7)
    nsol, nruns, ncad = 0, 0, 0
    for i in range(300):
        fam = ("rand", "local", "block")[i % 3]
        n = int(rng.integers(8, 15))
        alpha = {"rand": 2.1, "local": 4.0, "block": 2.5}[fam]
        inst = E.planted(fam, n, alpha, 900_000 + i, w=3 if fam != "block" else 4)
        if not inst.satisfied(inst.hidden):
            fails.append(f"G1 hidden state violates instance {i}")
        cnt = brute_count(inst)
        if cnt < 2:  # the hidden state and its complement
            fails.append(f"G1 brute count {cnt} < 2 on instance {i}")
        for a, prm in ARMS:
            res = E.run(inst, a, prm, seed=i, max_flips=10**6, want_state=True)
            nruns += 1
            if res["solved"]:
                nsol += 1
                if not inst.satisfied(res["state"].astype(np.int8)):
                    fails.append(f"G1 {a} reported a violating state on {i}")
            else:
                fails.append(f"G1 {a} unsolved on tiny instance {i}")
        th = np.random.default_rng(i).normal(0, 0.5, E.ntheta())
        for fl in POLICY_FLAGS:
            res = E.run(inst, "policy", (2.3, 1.0), theta=th, flags=fl, seed=i, max_flips=10**6, want_state=True)
            nruns += 1
            if res["solved"]:
                nsol += 1
                if not inst.satisfied(res["state"].astype(np.int8)):
                    fails.append(f"G1 policy flags {fl} reported a violating state on {i}")
            else:
                fails.append(f"G1 policy flags {fl} unsolved on tiny instance {i}")
        c = E.cadical(inst, 10)
        ncad += 1
        if c["result"] is not True or not c["model_ok"]:
            fails.append(f"G5 cadical on {i}: {c}")
    # an unsatisfiable instance: every triple of five distinctions (no 2-colouring of K5^(3) exists)
    unsat = E.Instance(5, np.array(list(itertools.combinations(range(5), 3)), dtype=np.int32))
    if brute_count(unsat) != 0 or E.cadical(unsat, 10)["result"] is not False:
        fails.append("G5 unsatisfiable control")
    print(f"G1 {nsol}/{nruns} runs solved and checked on 300 small instances; G5 {ncad} CaDiCaL models checked, "
          "unsatisfiable control refuted")

    # G2
    bad = 0
    for i in range(6):
        inst = E.planted("rand" if i % 2 == 0 else "local", 300, 2.1 if i % 2 == 0 else 4.0, 950_000 + i)
        bad += E.selftest(inst, i, 10_000)
    if bad:
        fails.append(f"G2 {bad} incremental mismatches")
    print("G2 incremental mismatches over 60,000 flips:", bad)

    # G3
    inst = E.planted("rand", 14, 2.1, 960_000)
    a = [E.run(inst, "rw", seed=s, max_flips=10**7)["flips"] for s in range(3000)]
    b = [E.run(inst, "policy", flags=E.LEARN_WHERE | E.MEM_AGE | E.MEM_RNN, seed=10**6 + s, max_flips=10**7)["flips"]
         for s in range(3000)]
    ks = stats.ks_2samp(a, b)
    # the zero-weight where step chooses among up to 6 candidates (just-violated ones included), not the
    # violated list, so compare the what step alone too
    c = [E.run(inst, "policy", flags=0, seed=2 * 10**6 + s, max_flips=10**7)["flips"] for s in range(3000)]
    ks0 = stats.ks_2samp(a, c)
    if ks0.pvalue < 0.001:
        fails.append(f"G3 zero-weight what differs from random: p={ks0.pvalue}")
    print(f"G3 zero weights, what only vs random agent: KS p={ks0.pvalue:.3f}; with where (not required "
          f"uniform over all violated knots): KS p={ks.pvalue:.3f}, medians {np.median(a):.0f} / {np.median(b):.0f}")

    # G4
    inst = E.planted("rand", 200, 2.1, 970_000)
    good = [E.run(inst, "probsat_poly", (2.3, 1.0), seed=s, max_flips=10**6)["flips"] for s in range(40)]
    mut = [E.run(inst, "probsat_poly", (-2.3, 1.0), seed=s, max_flips=10**6)["flips"] for s in range(40)]
    if not np.median(mut) > 5 * np.median(good):
        fails.append("G4 mutant not slower")
    print(f"G4 probSAT median {np.median(good):.0f} flips, break-preferring mutant {np.median(mut):.0f}")

    # G6: this engine reproduces WHERE-NEXT's run for run (the rules and the old policy flags)
    code = (
        "import sys, json, numpy as np; sys.path.insert(0, sys.argv[1]); import engine as E\n"
        "out = []\n"
        "th = np.load(sys.argv[2])\n"
        "for i in range(12):\n"
        "    fam = 'rand' if i % 2 == 0 else 'local'\n"
        "    inst = E.planted(fam, 400, 2.1 if fam == 'rand' else 4.0, 990_000 + i)\n"
        "    for a, prm in " + repr(ARMS) + ":\n"
        "        r = E.run(inst, a, prm, seed=i, max_flips=10**6); out.append([a, r['flips'], r['work']])\n"
        "    r = E.run(inst, 'policy', theta=th, flags=7, seed=i, max_flips=10**6); out.append(['L3', r['flips'], r['work']])\n"
        "    r = E.run(inst, 'policy', theta=np.load(sys.argv[3]), flags=23, seed=i, max_flips=10**6); out.append(['L3sm', r['flips'], r['work']])\n"
        "print(json.dumps(out))\n")
    res = []
    for d in (OLD, Path(__file__).resolve().parent):
        r = subprocess.run([sys.executable, "-B", "-c", code, str(d), str(OLD_L3), str(OLD_L3SM)], capture_output=True, text=True,
                           env={**os.environ, "WHERE_NEXT_BUILD": os.environ.get("WHERE_NEXT_BUILD", "/tmp/where_next_build")})
        if r.returncode:
            fails.append("G6 run failed: " + r.stderr[-300:])
            res.append(None)
        else:
            res.append(json.loads(r.stdout))
    same = res[0] is not None and res[0] == res[1]
    if not same:
        fails.append("G6 engines differ")
    print(f"G6 this engine reproduces SCALE-MEMORY's on {len(res[1] or [])} runs (8 rules, L3 and L3sm, 12 instances): {same}")

    print("GATE", "PASS" if not fails else "FAIL")
    for f in fails[:30]:
        print("  ", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
