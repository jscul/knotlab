"""Gates of SPEC-MERGE-20261117-001A, run before the freeze; exits non-zero on any failure.

  S1 soundness on 240 small instances (n = 10-16; rand, block, local) with a very eager speculative policy: every reported
     state satisfies every original knot, and every run ends solved;
  S2 with merging switched off (s unreachable) the speculative driver reproduces Novelty+ alone run for run (60 runs);
  S3 the stability counts equal a direct recount on random state sequences;
  S4 every tie the pair probe reports holds in every allowed state (brute force); a wrong-parity mutant is caught;
  S5 this engine reproduces EARN-BUDGET-20261117-001A's run for run for Novelty+ (the flip counter changes nothing).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import slow_loop as S  # noqa: E402
import spec_merge as M  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
EB = ROOT / "experiments/EARN-BUDGET-20261117-001A/EARN-BUDGET-20261117-001A-E001_earn_budget/slow_loop.py"
EAGER = {"e": 0.5, "s": 1, "mu": 0.5, "patience": 1, "warmup": 1, "max_rounds": 1000, "epoch_min": 3}
FAMS = [("rand", 2.1, 4), ("block", 2.5, 4), ("local", 4.0, 3)]


def allowed(n, kv):
    xs = ((np.arange(2 ** n)[:, None] >> np.arange(n)) & 1).astype(np.uint8)
    s = xs[:, kv].sum(axis=2)
    return xs[np.all((s == 1) | (s == 2), axis=1)]


def main() -> int:
    fails = []
    rng = np.random.default_rng(23)
    # S1
    merged = 0
    for i in range(240):
        fam, alpha, w = FAMS[i % 3]
        n = int(rng.integers(10, 17))
        inst = S.planted(fam, n, alpha, 1_950_000 + i, w=w)
        for mode in ("coflip", "random"):
            r = M.run_spec(inst, (0.5, 0.01), seed=i, cap=10**6, pol=EAGER, mode=mode, debug=True)
            merged += r["merges"]
            if not r["solved"] or not r["verified"] or not inst.satisfied(r["state"]):
                fails.append(f"S1 {i} {mode}: solved {r['solved']} verified {r['verified']}")
    print(f"S1 480 speculative runs, {merged} speculative merges made, every reported state checked on the original knots")
    # S1b at sizes where the search runs long enough for many rounds, merges and undos
    eager2 = {"e": 1.0, "s": 2, "mu": 0.1, "patience": 1, "warmup": 1, "max_rounds": 1000}
    m2 = u2 = 0
    for i in range(36):
        fam, alpha, w = [("rand", 2.1, 10), ("local", 4.0, 10), ("block", 2.5, 20)][i % 3]
        inst = S.planted(fam, 800, alpha, 1_955_000 + i, w=w)
        for mode in ("coflip", "random"):
            r = M.run_spec(inst, (0.7, 0.01), seed=i, cap=5 * 10**7, pol=eager2, mode=mode, debug=True)
            m2 += r["merges"]
            u2 += r["undos"]
            if r["solved"] and (not r["verified"] or not inst.satisfied(r["state"])):
                fails.append(f"S1b {i} {mode}: a reported state fails an original knot")
    print(f"S1b 72 runs at n = 800: {m2} speculative merges, {u2} undos, every reported state checked")
    if m2 < 1000:
        fails.append(f"S1b made only {m2} merges")
    # S2
    off = dict(EAGER, s=10**9, e=1.0, epoch_min=100)
    s2 = 0
    for i in range(12):
        fam, alpha, w = [("rand", 2.1, 10), ("local", 4.0, 10), ("block", 2.5, 20)][i % 3]
        inst = S.planted(fam, 800, alpha, 1_960_000 + i, w=w)
        for prm in ((0.7, 0.01), (0.6, 0.02), (0.8, 0.0), (0.7, 0.05), (0.5, 0.1)):
            a = S.run_fast(inst, "novelty_plus", prm, seed=i, cap=10**7)
            b = M.run_spec(inst, prm, seed=i, cap=10**7, pol=off)
            if (a["flips"], a["solved"], a["work_fast"]) != (b["flips"], b["solved"], b["work_fast"]):
                fails.append(f"S2 {fam} {i} {prm}: {a['flips']} vs {b['flips']}")
            s2 += 1
    print(f"S2 {s2} run-for-run checks with merging off")
    # S3
    for trial in range(50):
        n, m = int(rng.integers(5, 40)), int(rng.integers(3, 60))
        kv = np.stack([rng.choice(n, 3, replace=False) for _ in range(m)]).astype(np.int64)
        x = rng.integers(0, 2, n).astype(np.uint8)
        nf = np.zeros(n, np.int32)
        st = M.Stats(kv, x, nf)
        ref = np.zeros(3 * m, np.int64)
        a, b = st.a, st.b
        prev_rel = x[a] ^ x[b]
        prev_nf = nf.copy()
        for step in range(30):
            flipm = rng.random(n) < 0.3
            nf = nf + flipm.astype(np.int32) * rng.integers(1, 3, n).astype(np.int32)
            x = rng.integers(0, 2, n).astype(np.uint8)
            st.update(x, nf)
            rel = x[a] ^ x[b]
            both = (nf[a] > prev_nf[a]) & (nf[b] > prev_nf[b])
            ref = np.where(rel != prev_rel, 0, np.where(both, ref + 1, ref))
            prev_rel, prev_nf = rel, nf.copy()
            if not np.array_equal(ref, st.stab):
                fails.append(f"S3 trial {trial} step {step}")
                break
    print("S3 50 random sequences of 30 updates recounted")
    # S4
    s4 = caught = made = 0
    for i in range(150):
        fam, alpha, w = FAMS[i % 3]
        n = int(rng.integers(10, 15))
        inst = S.planted(fam, n, alpha, 1_970_000 + i, w=w)
        A = allowed(n, inst.knots)
        x, r = S.initial_state(n, i)
        h, _ = S._handle(n, inst.knots, np.zeros(inst.knots.shape, np.uint8), x, np.full(n, -1, np.int64), r, 1, 0)
        wo = np.zeros(1)
        for a in range(n):
            for b in range(a + 1, n):
                res = S.lib().sl_pair_probe(h, a, b, 100000, wo)
                if res == 3:
                    fails.append(f"S4 {i}: both relations refuted for ({a}, {b})")
                elif res:
                    par = 1 if res == 1 else 0  # "equal" refuted: unequal in every allowed state
                    s4 += 1
                    if not np.all((A[:, a] ^ A[:, b]) == par):
                        fails.append(f"S4 {i}: tie ({a}, {b}, {par}) fails in an allowed state")
                    made += 1
                    caught += not np.all((A[:, a] ^ A[:, b]) == 1 - par)
        S.lib().fl_free(h)
    print(f"S4 {s4} probed ties checked by brute force; wrong-parity mutant caught on {caught} of {made}")
    if made < 20 or caught < made:
        fails.append(f"S4 mutant caught {caught} of {made}")
    # S5
    spec = importlib.util.spec_from_file_location("eb_driver", EB)
    eb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(eb)
    s5 = 0
    for i in range(12):
        fam, alpha, w = [("rand", 2.1, 10), ("local", 4.0, 10)][i % 2]
        inst = S.planted(fam, 800, alpha, 1_980_000 + i, w=w)
        for prm in ((0.7, 0.01), (0.8, 0.0)):
            a = S.run_fast(inst, "novelty_plus", prm, seed=i, cap=10**7)
            b = eb.run_fast(eb.planted(fam, 800, alpha, 1_980_000 + i, w=w), "novelty_plus", prm, seed=i, cap=10**7)
            if (a["flips"], a["work"]) != (b["flips"], b["work"]):
                fails.append(f"S5 {fam} {i}: {a['flips']} vs {b['flips']}")
            s5 += 1
    print(f"S5 {s5} run-for-run checks against EARN-BUDGET's engine")
    print("FAILS:", len(fails))
    for f in fails[:30]:
        print("  ", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
