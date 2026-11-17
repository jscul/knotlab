"""Gate G of SLOW-LOOP-20261117-001A, copied and extended for EARN-BUDGET-20261117-001A (G1, G4 and G7 also run the earned
budget with batched rebuilds; G9 checks that this driver reproduces SLOW-LOOP's run for run on its policies). Exits non-zero on
any failure.

  G0 the knot law and a signed knot pass K1-K3 (knotlab check);
  G1 small instances (brute force): every tie and every derived knot the slow loop finds (guided with a large
     budget, and static) holds in every allowed state; the mutated pattern's allowed states, mapped back, are exactly
     the original's, one for one; every reported solution satisfies every original knot;
  G2 incremental counts on signed patterns equal recomputation after random runs of flips;
  G3 with no slow budget (rho = 0) the slow-loop driver reproduces the fast loop alone run for run;
  G4 a mutant slow loop that applies every tie with the wrong parity is caught: its mutated pattern's states, mapped
     back, differ from the original's on every small instance where it made a tie;
  G5 every CaDiCaL model satisfies every knot, and CaDiCaL agrees with brute force on satisfiability;
  G6 this engine reproduces SCALE-MEMORY-20261116-001A's engine run for run (Novelty+ and probSAT, rand and local),
     and the generator reproduces MEET-TRANSFER-20261117-001A's on the block pattern;
  G7 at n = 800 and 3200, every tie and shadow knot found holds in the planted state, and every reported solution
     checks (a run may stop unsolved at the cap: very many shadow knots slow the search, which is a finding, not a fault);
  G8 the earned budget rises on a pattern full of ties and stays at its floor on one with none;
  G9 this driver reproduces SLOW-LOOP-20261117-001A's driver run for run (flips, work, moves) for G, GO and ST, under
     SLOW-LOOP's charge (v1);
  G10 the corrected charge (v2, after SLOW-LOOP's referee) only adds the rebuild's sorting where no budget is counted in it
      (static probing; a random-target run before its first rebuild).
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import slow_loop as S  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SM = ROOT / "experiments/SCALE-MEMORY-20261116-001A/SCALE-MEMORY-20261116-001A-E001_scale_memory/engine.py"
MT = ROOT / "experiments/MEET-TRANSFER-20261117-001A/MEET-TRANSFER-20261117-001A-E001_meet_transfer/engine.py"
AGGR = {"e": 0.2, "rho": 20.0, "beta": 1.0, "J": 4, "pb": 100000, "backoff": False, "mode": 0}
EARN_AGGR = {"e": 0.2, "beta": 1.0, "J": 4, "pb": 100000, "backoff": False, "mode": 1, "earn": True, "theta": 0.0,
             "rho_min": 0.5, "rho_max": 20.0, "rb": 0.003}
# gate-only: epochs of one flip on the small instances, so that the slow loop runs before the search solves them
EARN_SMALL = dict(EARN_AGGR, e=0.01, epoch_min=1)
AGGR_SMALL = dict(AGGR, e=0.01, epoch_min=1)
SL = ROOT / "experiments/SLOW-LOOP-20261117-001A/SLOW-LOOP-20261117-001A-E001_slow_loop"
FAMS = [("rand", 2.1, 4), ("block", 2.5, 4), ("local", 4.0, 3)]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def allowed(n, kv, ks):
    xs = ((np.arange(2 ** n)[:, None] >> np.arange(n)) & 1).astype(np.uint8)
    e = xs[:, kv] ^ ks[None, :, :]
    s = e.sum(axis=2)
    return xs[np.all((s == 1) | (s == 2), axis=1)]


def main() -> int:
    fails = []
    env = {**os.environ, "PYTHONPATH": str(ROOT / "tools")}
    for cnf in ["a b c; ~a ~b ~c", "a ~b c; ~a b ~c"]:
        r = subprocess.run([sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf, "--loops", "a", "b",
                            "--contact", "c", "--json"], capture_output=True, text=True, env=env, cwd=ROOT)
        g0 = json.loads(r.stdout)
        print("G0", cnf, "knot:", g0["is_knot"])
        if not g0["is_knot"]:
            fails.append(f"G0 {cnf} not a knot")

    # G1 and G5
    rng = np.random.default_rng(11)
    n_moves = n_bij = n_sol = n_moves_earn = 0
    from pysat.solvers import Solver
    for i in range(240):
        fam, alpha, w = FAMS[i % 3]
        n = int(rng.integers(8, 15))
        inst = S.planted(fam, n, alpha, 950_000 + i, w=w)
        A = allowed(n, inst.knots, np.zeros_like(inst.knots, dtype=np.uint8))
        if len(A) < 2:
            fails.append(f"G1 instance {i} allows {len(A)} states")
        for static, pol in ((False, AGGR_SMALL), (True, AGGR), (False, EARN_SMALL)):
            r = S.run_slow(inst, "novelty_plus", (0.5, 0.01), seed=i, cap=10**6, policy=pol, static=static,
                           debug=True)
            if not (r["solved"] and r["verified"]):
                fails.append(f"G1 {i} static={static} solved={r['solved']} verified={r['verified']}")
            n_sol += 1
            if r["contradiction"]:
                fails.append(f"G1 {i} contradiction reported")
            root, rpar = r["root"], r["rpar"]
            if not np.all((A ^ A[:, root]) == rpar[None, :]):
                fails.append(f"G1 {i} static={static}: a tie fails in some allowed state")
            for (a, b, c, sa, sb, sc) in r["shadow_list"]:
                e = np.stack([A[:, a] ^ sa, A[:, b] ^ sb, A[:, c] ^ sc], axis=1).sum(axis=1)
                if not np.all((e == 1) | (e == 2)):
                    fails.append(f"G1 {i}: derived knot {(a, b, c, sa, sb, sc)} fails in some allowed state")
                n_moves += 1
            n_moves += int(np.sum(root != np.arange(n)))
            if pol is EARN_SMALL:
                n_moves_earn += int(np.sum(root != np.arange(n))) + len(r["shadow_list"])
            # the mutated pattern on its classes, mapped back, is exactly the original's allowed set
            roots = r["roots"]
            idx = np.full(n, -1)
            idx[roots] = np.arange(len(roots))
            B = allowed(len(roots), idx[r["kv"]], r["ks"]) if len(r["kv"]) else \
                ((np.arange(2 ** len(roots))[:, None] >> np.arange(len(roots))) & 1).astype(np.uint8)
            back = np.zeros((len(B), n), np.uint8)
            back[:, :] = B[:, idx[root]] ^ rpar[None, :]
            sa_ = {bytes(x) for x in A}
            sb_ = {bytes(x) for x in back}
            if sa_ != sb_ or len(back) != len(A):
                fails.append(f"G1 {i} static={static}: mutated pattern's states differ ({len(back)} vs {len(A)})")
            n_bij += 1
        with Solver(name="cadical195", bootstrap_with=inst.cnf(break_symmetry=False)) as sv:
            ok = sv.solve()
            if ok != (len(A) > 0):
                fails.append(f"G5 CaDiCaL disagrees on {i}")
            if ok:
                mdl = sv.get_model()
                x = np.array([1 if lit > 0 else 0 for lit in mdl[:n]], dtype=np.int8)
                if not inst.satisfied(x):
                    fails.append(f"G5 model violates {i}")
    print(f"G1 {n_sol} slow runs, {n_bij} one-for-one checks, {n_moves} moves checked against brute force "
          f"({n_moves_earn} of them by the earned budget)")

    # G2 incremental counts on signed patterns
    g2 = 0
    for i in range(30):
        n = int(rng.integers(50, 400))
        inst = S.planted(["rand", "local"][i % 2], n, 3.0, 960_000 + i, w=5)
        ks = rng.integers(0, 2, inst.knots.shape).astype(np.uint8)
        x, rs = S.initial_state(n, i)
        h, _ = S._handle(n, inst.knots, ks, x, np.full(n, -1, np.int64), rs, 1, 0)
        out = np.zeros(5)
        for step in range(10):
            S.lib().fl_run(h, [4, 2][step % 2], np.array([0.5, 0.02, 0, 0.0]) if step % 2 == 0 else
                           np.array([2.3, 1.0, 0, 0.0]), int(rng.integers(1, 2000)), out)
            xs = np.zeros(n, np.uint8)
            S.lib().fl_get(h, xs, np.zeros(n, np.int64), np.zeros(2, np.uint64), None, np.zeros(len(ks), np.int32),
                           np.zeros(len(ks), np.uint8))
            e = (xs[inst.knots] ^ ks).sum(axis=1)
            nv = int(np.sum((e == 0) | (e == 3)))
            if nv != S.lib().fl_nviol(h):
                fails.append(f"G2 count mismatch on {i} step {step}: {nv} vs {S.lib().fl_nviol(h)}")
            g2 += 1
        S.lib().fl_free(h)
    print(f"G2 {g2} recounts")

    # G3 and G6
    old = load(SM, "sm_engine")
    zero = {"e": 1.0, "rho": 0.0, "beta": 0.5, "J": 2, "pb": 4000, "backoff": True, "mode": 0}
    g3 = g6 = 0
    for i in range(12):
        fam = ["rand", "local"][i % 2]
        alpha = 2.1 if fam == "rand" else 4.0
        n = [200, 800][i % 3 % 2]
        a = old.planted(fam, n, alpha, 970_000 + i)
        b = S.planted(fam, n, alpha, 970_000 + i)
        if not np.array_equal(a.knots, b.knots):
            fails.append(f"G6 generator differs on {fam} {i}")
        for algo, prm in [("novelty_plus", (0.7, 0.01)), ("novelty_plus", (0.7, 0.0)), ("novelty_plus", (0.5, 0.05)),
                          ("probsat_poly", (2.3, 1.0)), ("probsat_poly", (1.4, 1.0))]:
            ro = old.run(a, algo, prm, seed=i, max_flips=10**7)
            rn = S.run_fast(b, algo, prm, seed=i, cap=10**7)
            if (ro["flips"], ro["work"], ro["solved"]) != (rn["flips"], rn["work_fast"], rn["solved"]):
                fails.append(f"G6 {algo}{prm} {fam} {i}: old {ro['flips']},{ro['work']} new {rn['flips']},"
                             f"{rn['work_fast']}")
            g6 += 1
            rz = S.run_slow(b, algo, prm, seed=i, cap=10**7, policy=zero)
            if (rz["flips"], rz["solved"]) != (rn["flips"], rn["solved"]) or rz["work_slow"] != 0:
                fails.append(f"G3 {algo}{prm} {fam} {i}: slow driver {rz['flips']} vs fast {rn['flips']}")
            g3 += 1
    mt = load(MT, "mt_engine")
    for i in range(6):
        a = mt.planted("block", 800, 2.5, 980_000 + i, w=20)
        b = S.planted("block", 800, 2.5, 980_000 + i, w=20)
        if not np.array_equal(a.knots, b.knots):
            fails.append(f"G6 block generator differs on {i}")
    print(f"G3 {g3} run-for-run checks; G6 {g6} run-for-run checks and 18 generator checks")

    # G4 the mutant is caught
    caught = made = made_earn = 0
    for i in range(160):
        fam, alpha, w = FAMS[1 + i % 2]
        n = int(rng.integers(10, 15))
        inst = S.planted(fam, n, alpha, 985_000 + i, w=w)
        A = allowed(n, inst.knots, np.zeros_like(inst.knots, dtype=np.uint8))
        r = S.run_slow(inst, "novelty_plus", (0.5, 0.01), seed=i, cap=10**5, policy=AGGR if i % 2 else EARN_SMALL,
                       static=bool(i % 2), debug=True, mutant=True)
        if r["ties"] == 0:
            continue
        made += 1
        made_earn += i % 2 == 0
        roots = r["roots"]
        idx = np.full(n, -1)
        idx[roots] = np.arange(len(roots))
        Bm = allowed(len(roots), idx[r["kv"]], r["ks"]) if len(r["kv"]) else \
            ((np.arange(2 ** len(roots))[:, None] >> np.arange(len(roots))) & 1).astype(np.uint8)
        back = Bm[:, idx[r["root"]]] ^ r["rpar"][None, :]
        if {bytes(x) for x in back} != {bytes(x) for x in A} or r["contradiction"] or \
                (r["solved"] and not r["verified"]) or not r["solved"]:
            caught += 1
    print(f"G4 mutant caught on {caught} of {made} instances where it made a tie ({made_earn} by the earned budget)")
    if made < 20 or caught < made:
        fails.append(f"G4 mutant caught on {caught} of {made}")

    # G7 at size, against the planted state
    g7 = g7_unsolved = 0
    for fam, alpha, w in [("rand", 2.1, 10), ("block", 2.5, 20), ("local", 4.0, 10), ("local", 4.0, 40)]:
        for n in (800, 3200):
            for i in range(3):
                inst = S.planted(fam, n, alpha, 990_000 + i, w=w)
                hid = inst.hidden.astype(np.uint8)
                for static, pol0 in ((False, AGGR), (True, AGGR), (False, EARN_AGGR)):
                    pol = dict(pol0, pb=4000)
                    r = S.run_slow(inst, "novelty_plus", (0.7, 0.01), seed=i, cap=10**8, policy=pol, static=static,
                                   debug=True)
                    if (r["solved"] and not r["verified"]) or r["contradiction"]:
                        fails.append(f"G7 {fam} {n} {i} static={static}: solved {r['solved']} verified {r['verified']}")
                    g7_unsolved += not r["solved"]
                    if not np.all((hid ^ hid[r["root"]]) == r["rpar"]):
                        fails.append(f"G7 {fam} {n} {i} static={static}: a tie fails in the planted state")
                    for (a, b, c, sa, sb, sc) in r["shadow_list"]:
                        e = (hid[a] ^ sa) + (hid[b] ^ sb) + (hid[c] ^ sc)
                        if e in (0, 3):
                            fails.append(f"G7 {fam} {n} {i}: derived knot fails in the planted state")
                    g7 += int(np.sum(r["root"] != np.arange(n))) + len(r["shadow_list"])
    print(f"G7 {g7} moves checked against the planted state ({g7_unsolved} aggressive runs unsolved at the cap)")

    # G8 the earned budget rises with finds and stays at its floor without
    earn = {"e": 1.0, "beta": 0.0, "J": 2, "pb": 4000, "backoff": False, "mode": 1, "earn": True, "theta": 0.03,
            "rho_min": 0.03, "rho_max": 1.0, "rb": 0.01}
    hi = [S.run_slow(S.planted("local", 3200, 4.0, 995_000 + i, w=10), "novelty_plus", (0.7, 0.05), seed=i, cap=10**8,
                     policy=earn)["rho_top"] for i in range(3)]
    lo = [S.run_slow(S.planted("rand", 3200, 2.1, 995_000 + i), "novelty_plus", (0.7, 0.05), seed=i, cap=10**8,
                     policy=earn)["rho_top"] for i in range(3)]
    print(f"G8 earned budget's top on local w10: {hi}; on rand: {lo}")
    if min(hi) < 0.12 or max(lo) > 0.03 + 1e-12:
        fails.append(f"G8 earned budget did not respond: {hi} {lo}")

    # G9 run for run with SLOW-LOOP's driver
    old = load(SL / "slow_loop.py", "sl_driver")
    pols = json.loads((ROOT / "artifacts/SLOW-LOOP-20261117-001A/SLOW-LOOP-20261117-001A-E001_slow_loop/policies.json")
                      .read_text())
    g9 = g10 = 0
    for i in range(12):
        fam, alpha, w = [("local", 4.0, 10), ("block", 2.5, 20), ("rand", 2.1, 10)][i % 3]
        inst = S.planted(fam, 800, alpha, 996_000 + i, w=w)
        inst_o = old.planted(fam, 800, alpha, 996_000 + i, w=w)
        for name, static in (("G", False), ("GO", False), ("ST", True)):
            a = S.run_slow(inst, "novelty_plus", (0.7, 0.05), seed=i, cap=10**7, policy=pols[name], static=static,
                           charge="v1")
            if name == "ST":
                # static probing has no slow budget, so the charge cannot change its run: v2 must only add the sorting
                a2 = S.run_slow(inst, "novelty_plus", (0.7, 0.05), seed=i, cap=10**7, policy=pols[name], static=static)
                if (a2["flips"], a2["ties"], a2["n_final"], a2["work_fast"], a2["work_slow"]) != \
                        (a["flips"], a["ties"], a["n_final"], a["work_fast"], a["work_slow"]) or \
                        (a["rebuilds"] and a2["work_rebuild"] <= a["work_rebuild"]):
                    fails.append(f"G10 charge v2 changed a static run or added nothing: {fam} {i}")
                g10 += 1
            b = old.run_slow(inst_o, "novelty_plus", (0.7, 0.05), seed=i, cap=10**7, policy=pols[name], static=static)
            ka = tuple(a[k] for k in ("flips", "work", "ties", "shadows", "n_final", "rebuilds"))
            kb = tuple(b[k] for k in ("flips", "work", "ties", "shadows", "n_final", "rebuilds"))
            if ka != kb:
                fails.append(f"G9 {name} {fam} {i}: {ka} vs {kb}")
            g9 += 1
    print(f"G9 {g9} run-for-run checks against SLOW-LOOP's driver (charge v1); G10 {g10} static runs under charge v2")
    # G10, budgeted arms: their slow budget is counted in charged work, so the corrected charge can change their runs (a
    # costlier sort leaves fewer probes in a budget); with random targets and no rebuild yet nothing differs
    inst = S.planted("rand", 800, 2.1, 997_000)
    gb = {"e": 1.0, "rho": 0.3, "beta": 0.0, "J": 2, "pb": 4000, "backoff": False, "mode": 1, "rb": 0.03}
    r1 = S.run_slow(inst, "novelty_plus", (0.7, 0.05), seed=1, cap=10**7, policy=gb, charge="v1")
    r2 = S.run_slow(inst, "novelty_plus", (0.7, 0.05), seed=1, cap=10**7, policy=gb, charge="v2")
    if r1["rebuilds"] == 0 and (r1["flips"], r1["work"]) != (r2["flips"], r2["work"]):
        fails.append("G10 charge v2 changed a random-target run with no rebuild")

    print("FAILS:", len(fails))
    for f in fails[:40]:
        print("  ", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
