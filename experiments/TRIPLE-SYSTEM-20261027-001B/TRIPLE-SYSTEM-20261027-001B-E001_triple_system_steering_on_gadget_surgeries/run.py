"""Run TRIPLE-SYSTEM-20261027-001B-E001 once under its frozen contract (see tsfix.py for the rules)."""
import itertools
import json
import os
import sys
import time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tsfix import (ROOT, BX, algebras, predicted_Q, fixture_words, base_words, KAPPA, FX)  # noqa: E402
from lm import LieBraidModel, Grp, transport  # noqa: E402
import cp_lib as C  # noqa: E402
import bc_lib as Bc  # noqa: E402
import bm  # noqa: E402  (BEYOND-CLASS2-20261027-001B-E001's matrix model, read-only)

OUT = os.path.join(ROOT, "artifacts/TRIPLE-SYSTEM-20261027-001B/TRIPLE-SYSTEM-20261027-001B-E001_triple_system_steering_on_gadget_surgeries")
SAMPLES = 32
rows, fails, machinery_fail, controls = [], [], [], []
T0 = time.time()


def log(*a):
    print("[%7.1f s]" % (time.time() - T0), *a, flush=True)


def rand_cols(Mo, rng, bs=SAMPLES):
    return (rng.integers(0, Mo.p, (bs, len(Mo.Fix))) @ Mo.Fix) % Mo.p


def measure(Mo, A, rng, bs=SAMPLES):
    """random free data and duals; returns (Q, inputs, svals)"""
    inputs = {k: rand_cols(Mo, rng, bs) for k in A["free"]}
    svals = {b: rand_cols(Mo, rng, bs) for b in A["measured"]}
    o = Mo.solve(inputs, A["measured"])
    Q = np.zeros(bs, dtype=np.int64)
    for b in A["measured"]:
        Q = (Q + (o[b] * Mo.y_of(svals[b])).sum(axis=1)) % Mo.p
    return Q, inputs, svals


# ------------------------------------------------------------------ machinery
log("machinery")
for p in (5, 7, 11):
    rng = np.random.default_rng(p)
    for name, A in algebras(p).items():
        L = A["L"]
        X, Y, Z = (rng.integers(0, p, (16, L.D)) for _ in range(3))
        if ((L.br(X, Y) - np.einsum("bi,bj,ijk->bk", X, Y, L.C)) % p).any():
            machinery_fail.append(("M1 sparse bracket", p, name))
        if ((L.bch(L.bch(X, Y), Z) - L.bch(X, L.bch(Y, Z))) % p).any():
            machinery_fail.append(("M2 BCH associativity", p, name))
        G = Grp(L)
        a = (X, 1)
        if (G.mul(a, G.inv(a))[0] % p).any():
            machinery_fail.append(("M3 inverse", p, name))
log("machinery failures:", machinery_fail)

# ------------------------------------------------------------------ R2 bases and R0 abelian triple systems (no obstruction)
log("R2 bases and R0 abelian triple systems")
for p in (5, 7):
    words = dict(base_words(p))
    words.update(fixture_words(p))
    for fname, (w, n, ev, N) in words.items():
        for name, A in algebras(p).items():
            is_base = not ev
            if not (is_base or A["abelian"]):
                continue
            Mo = LieBraidModel(w, n, A["L"])
            if len(Mo.Fix) != N + 1 or ((Mo.y_of(Mo.Fix) @ Mo.Lin[-1]) % p).any():
                machinery_fail.append(("M4 fixture", p, fname, name))
            rng = np.random.default_rng(1000 + p)
            inputs = {k: rand_cols(Mo, rng, 16) for k in range(A["L"].D) if A["L"].sign[k] == -1}
            try:
                Mo.solve(inputs, [])
                lifted = True
            except AssertionError:
                lifted = False
            rows.append({"part": "R2 base" if is_base else "R0 abelian", "p": p, "fixture": fname, "algebra": name,
                         "samples": 16, "all lift": lifted})
            if not lifted:
                fails.append(("R2/R0", p, fname, name))
            log(f"  p={p} {fname} {name}: all free data lift: {lifted}")

# ------------------------------------------------------------------ R1 steering
log("R1 steering")
for p in (5, 7, 11):
    T = FX.tensors(p)
    words = fixture_words(p) if p != 11 else {}
    if p == 11:
        base, n = FX.torus_sum(8, 11)
        w, ev = FX.build(base, [(0, "P4B", 1, [])])
        words = {"T(2,11)x8 + P4B (0,1)": (w, n, ev, 8)}
    for fname, (w, n, ev, N) in words.items():
        for ai, (name, A) in enumerate(algebras(p).items()):
            if A["abelian"]:
                continue
            Mo = LieBraidModel(w, n, A["L"])
            rng = np.random.default_rng(2000 + 31 * p + ai)
            Q, inputs, svals = measure(Mo, A, rng)
            pred = predicted_Q(A["L"], w, ev, inputs, svals, T)
            eq = bool((Q == pred).all())
            rows.append({"part": "R1 steering", "p": p, "fixture": fname, "algebra": name, "crossings": len(w),
                         "dim": A["L"].D, "free": len(A["free"]), "measured": len(A["measured"]), "samples": SAMPLES,
                         "Q_nonzero": int((Q != 0).sum()), "equal": eq})
            if not eq:
                fails.append(("R1", p, fname, name))
            log(f"  p={p} {fname} {name}: Q nonzero {int((Q != 0).sum())}/{SAMPLES}, Q == R1: {eq}")
            if p == 5 and fname.startswith("4_1x4") and name == "free3 (y1-, y2-)":
                for cname, cp in [("X1 kappa = 1", predicted_Q(A["L"], w, ev, inputs, svals, T, kappa=1)),
                                  ("X2 P4B tensor for a P4 insertion", predicted_Q(A["L"], w, ev, inputs, svals, T,
                                                                                   braid_override="P4B"))]:
                    controls.append({"control": cname, "fixture": fname, "algebra": name, "matched": bool((Q == cp).all())})
                    log(f"  control {cname}: matched {controls[-1]['matched']} (must be False)")
            if p == 5 and fname == "gadget K3" and name == "free3 (x+, y1-, y2-)":
                cp = predicted_Q(A["L"], w, ev, inputs, svals, T, drop_last=True)
                controls.append({"control": "X3 one edge dropped", "fixture": fname, "algebra": name,
                                 "matched": bool((Q == cp).all())})
                log(f"  control X3: matched {controls[-1]['matched']} (must be False)")
            if p == 5 and fname == "gadget K3" and name == "cross4 (x+, y-)":
                cp = predicted_Q(A["L"], w, ev, inputs, svals, T, swap02=True)
                controls.append({"control": "X4 leaves 0 and 2 swapped", "fixture": fname, "algebra": name,
                                 "matched": bool((Q == cp).all())})
                lay1 = {k: v for k, v in inputs.items() if A["L"].layer[k] == 1}
                cp2 = predicted_Q(A["L"], w, ev, lay1, svals, T)
                controls.append({"control": "X5 layer-1 data only", "fixture": fname, "algebra": name,
                                 "matched": bool((Q == cp2).all())})
                log(f"  controls X4, X5: matched {controls[-2]['matched']}, {controls[-1]['matched']} (must be False)")

# ------------------------------------------------------------------ R3 model agreement (u4: BCH model vs matrix model)
log("R3 model agreement")
for p in (5, 7):
    for fname, (w, n, ev, N) in fixture_words(p).items():
        A = algebras(p)["u4 four-way"]
        L = A["L"]
        Mo = LieBraidModel(w, n, L)
        rng = np.random.default_rng(3000 + p)
        Q, inputs, svals = measure(Mo, A, rng)
        Mb = bm.BraidModel(w, n, p)
        Qb = Mb.Q(inputs[L.idx["y"]], inputs[L.idx["x"]], inputs[L.idx["w"]], svals[L.idx["t"]])
        eq = bool((Q == Qb).all())
        rows.append({"part": "R3 model agreement", "p": p, "fixture": fname, "samples": SAMPLES,
                     "Q_nonzero": int((Q != 0).sum()), "equal": eq})
        if not eq:
            fails.append(("R3", p, fname))
        log(f"  p={p} {fname}: BCH model == matrix model: {eq}")

# ------------------------------------------------------------------ R4 lifting (independent group law)
log("R4 lifting")
p = 5
A = algebras(p)["free3 (y1-, y2-)"]
L = A["L"]
w, n, ev, N = fixture_words(p)["4_1x4 + P4 (0,0)"]
Mo = LieBraidModel(w, n, L)
U, rels, arc = C.presentation(w, n, 2)
brk = {}
for i in range(L.D):
    for j in range(i + 1, L.D):
        v = L.C[i, j]
        if v.any():
            brk[(L.names[i], L.names[j])] = {L.names[k]: int(v[k]) for k in np.nonzero(v)[0]}
GL = Bc.GradedLie(p, 2, L.names, [int(x) for x in L.layer], [0 if s == 1 else 1 for s in L.sign], brk)


def arc_values(top):
    vals = [None] * U
    cur = np.array(top, dtype=np.int64).copy()
    for l, g in enumerate(w):
        for q in range(n):
            a = arc[(l, q)]
            if vals[a] is None:
                vals[a] = int(cur[q])
            elif vals[a] != int(cur[q]):
                raise AssertionError("arc color mismatch")
        cur = transport(cur[None, :], [g], 1, p)[0]
    return vals


rng = np.random.default_rng(4000)
agree, lifts, comp_ok, total = 0, 0, True, 24
dimZ = len(Mo.Fix)
y1, y2 = L.idx["y1"], L.idx["y2"]
ones = np.ones(n, dtype=np.int64)
for t in range(total):
    c1, c2 = rand_cols(Mo, rng, 1), rand_cols(Mo, rng, 1)
    if t < 8:
        c2 = (int(rng.integers(0, p)) * ones[None, :]) % p
    inputs = {y1: c1, y2: c2}
    for k in A["free"]:
        if k not in inputs:
            inputs[k] = np.zeros((1, n), dtype=np.int64)
    o = Mo.solve(inputs, A["measured"])
    qzero = all(not ((o[b] @ Mo.y_of(Mo.Fix).T) % p).any() for b in A["measured"])
    cnt = Bc.direct_count(GL, U, rels, 1, fix_f1={GL.idx["y1"]: arc_values(c1[0]), GL.idx["y2"]: arc_values(c2[0])})
    agree += (cnt > 0) == qzero
    lifts += cnt > 0
    if cnt not in (0, p ** (2 * dimZ)):
        comp_ok = False
eq = agree == total and comp_ok
rows.append({"part": "R4 lifting", "p": p, "algebra": "free3 (y1-, y2-)", "samples": total, "agree": agree,
             "lifting": int(lifts), "completions |Z1|^2": comp_ok, "equal": eq})
if not eq:
    fails.append(("R4", agree, comp_ok))
log(f"  lift <=> Q(x; .) = 0 on {agree}/{total} ({lifts} lift), completions |Z1|^2: {comp_ok}")

# ------------------------------------------------------------------ verdict
bad = [c for c in controls if c["matched"]]
verdict = "invalid" if (machinery_fail or bad) else ("supported" if not fails else "refuted")
result = {"experiment_id": "TRIPLE-SYSTEM-20261027-001B-E001", "verdict": verdict, "machinery_failures": machinery_fail,
          "failures": fails, "controls": controls, "rows": len(rows), "seconds": round(time.time() - T0, 1)}
os.makedirs(OUT, exist_ok=True)
json.dump(rows, open(os.path.join(OUT, "rows.json"), "w"), indent=1, default=str)
json.dump(result, open(os.path.join(OUT, "result.json"), "w"), indent=1, default=str)
log("verdict:", verdict, "failures:", fails, "machinery:", machinery_fail, "bad controls:", bad)
