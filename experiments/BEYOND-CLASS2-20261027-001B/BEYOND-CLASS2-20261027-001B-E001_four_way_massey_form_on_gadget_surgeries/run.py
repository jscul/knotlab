"""Run BEYOND-CLASS2-20261027-001B-E001 once under its frozen contract: machinery checks, then parts A (base), B (steering,
second braid, additivity, dragged insertions, level-model tables, independent lifting test), C (gadgets), D (independent
homomorphism counts), with negative controls.  Writes rows.json and result.json to the artifact directory."""
import json
import os
import sys
import time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fixtures import (C, Bc, mlib, KAPPA, BRAIDS, torus_sum, knot_sum, build, gadget, tensors, predicted_Q,  # noqa: E402
                      predicted_Q_closed_form, BASES_LEVEL, BASES_BRAID, STEERING, STEERING_LEVEL, LIFT_FIXTURE, GRAPHS,
                      GADGET_PRIMES, COUNTS, SAMPLES, LIFT_SAMPLES, base_word, ROOT)
from bm import BraidModel, J_matrix, transport  # noqa: E402
from lp import LevelModel  # noqa: E402

OUT = os.path.join(ROOT, "artifacts/BEYOND-CLASS2-20261027-001B/BEYOND-CLASS2-20261027-001B-E001_four_way_massey_form_on_gadget_surgeries")
rows, fails, machinery_fail, controls = [], [], [], []
T0 = time.time()


def log(*a):
    print("[%7.1f s]" % (time.time() - T0), *a, flush=True)


def samples(Mo, rng, bs=SAMPLES):
    def rc():
        return (rng.integers(0, Mo.p, (bs, len(Mo.Fix))) @ Mo.Fix) % Mo.p
    return {"y": rc(), "x": rc(), "w": rc(), "s": rc()}


def measure(Mo, cols):
    return Mo.Q(cols["y"], cols["x"], cols["w"], cols["s"])


def per_fixture_machinery(Mo, N, name):
    p = Mo.p
    ok = True
    if len(Mo.Fix) != N + 1:
        machinery_fail.append(("M4 dim", name, len(Mo.Fix), N + 1))
        ok = False
    if ((Mo.y_of(Mo.Fix) @ Mo.L3) % p).any():
        machinery_fail.append(("M4 left kernel", name))
        ok = False
    return ok


# ------------------------------------------------------------------ machinery
log("machinery")
for p in (5, 7, 11, 13):
    for n in range(2, 11):
        J = J_matrix(n, p)
        for i in range(1, n):
            for sgn in (1, -1):
                Bm = transport(np.eye(n, dtype=np.int64), [sgn * i], 1, p).T % p
                if ((Bm.T @ J @ Bm - J) % p).any():
                    machinery_fail.append(("M1 J-invariance", p, n, i, sgn))
rng0 = np.random.default_rng(0)
for p in (5, 7, 11, 13):
    for n in range(2, 12):
        s = rng0.integers(0, p, (16, n))
        y = (s @ J_matrix(n, p)) % p
        for q in range(n - 1):
            if ((y[:, q] + y[:, q + 1] + s[:, q + 1] - s[:, q]) % p).any():
                machinery_fail.append(("M2 bundle identity", p, n, q))
for name, w in BRAIDS.items():
    st = mlib.artin_conj(w, 4)
    imgC = mlib.artin(C.cable(w, 2), 8)

    def Y(k):
        return [(2 * k + 1, 1), (2 * k, 1)]
    for j in range(4):
        Wsub = mlib.subst(st[j][0], Y)
        for t in range(2):
            if mlib.red(Wsub + [(2 * j + t, 1)] + mlib.inv(Wsub)) != imgC[2 * j + t]:
                machinery_fail.append(("M3 cable action", name, j, t))
    for p in (5, 7, 11, 13):
        try:
            mlib.degree3_tensor(w, 4, p)
        except AssertionError as e:
            machinery_fail.append(("M3 third term", name, p, str(e)))
        cab = C.cable(w, 2)
        if ((transport(np.eye(8, dtype=np.int64), cab, len(cab), p) - np.eye(8, dtype=np.int64)) % p).any():
            machinery_fail.append(("M3 Burau of the cable", name, p))
log("machinery failures:", machinery_fail)
TENS = {p: tensors(p) for p in (5, 7, 11, 13)}
rows.append({"part": "tensors", "P4_p5": {str(j): {str(k): v for k, v in TENS[5]["P4"][j].items()} for j in range(4)},
             "P4B_p5": {str(j): {str(k): v for k, v in TENS[5]["P4B"][j].items()} for j in range(4)}})

# ------------------------------------------------------------------ part A: base vanishing
log("part A, level model full tables")
for kind, p, N in BASES_LEVEL:
    if kind.startswith("T2"):
        word, n = torus_sum(N, p)
    else:
        word, n = knot_sum(kind, N)
    Lm = LevelModel(word, n, p, Bc)
    lk = all(Lm.in_left_kernel(Lm.y_of(s)) for s in Lm.Z1)
    if not lk:
        machinery_fail.append(("M5 level left kernel", kind, N))
    if len(Lm.H) != N:
        machinery_fail.append(("M5 level dim", kind, N, len(Lm.H)))
    T = Lm.table(Lm.H)
    zero = all(v == 0 for v in T.values())
    rows.append({"part": "A-level", "base": f"{kind} x{N}", "p": p, "dimV": len(Lm.H), "entries": len(T), "Q0_zero": zero})
    if not zero:
        fails.append(("A-level", kind, N))
    log(f"  {kind} x{N} p={p}: dim V {len(Lm.H)}, {len(T)} entries, Q0 = 0: {zero}")
log("part A, braid model samples")
for idx, (p, N) in enumerate(BASES_BRAID):
    word, n = torus_sum(N, p)
    Mo = BraidModel(word, n, p)
    per_fixture_machinery(Mo, N, f"T(2,{p})x{N}")
    cols = samples(Mo, np.random.default_rng(100 + idx))
    Q = measure(Mo, cols)
    zero = not Q.any()
    rows.append({"part": "A-braid", "base": f"T(2,{p})x{N}", "p": p, "dimV": len(Mo.Fix) - 1, "samples": SAMPLES, "Q0_zero": zero})
    if not zero:
        fails.append(("A-braid", p, N))
    log(f"  T(2,{p})x{N}: Q0 = 0 on {SAMPLES} samples: {zero}")

# ------------------------------------------------------------------ part B: steering
log("part B, braid model")
for idx, (name, spec, p, inserts) in enumerate(STEERING):
    base, n = base_word(spec, p)
    word, events = build(base, inserts)
    Mo = BraidModel(word, n, p)
    Nsum = spec[2] if spec[0] == "knot" else spec[1]
    per_fixture_machinery(Mo, Nsum, name)
    cols = samples(Mo, np.random.default_rng(200 + idx))
    Q = measure(Mo, cols)
    pred = predicted_Q(cols, word, events, p, TENS[p])
    eq = bool((Q == pred).all())
    rows.append({"part": "B-braid", "fixture": name, "p": p, "crossings": len(word), "strands": n, "dimV": len(Mo.Fix) - 1,
                 "samples": SAMPLES, "Q_nonzero": int((Q != 0).sum()), "equal": eq})
    if not eq:
        fails.append(("B-braid", name))
    log(f"  {name} p={p}: {len(word)} crossings, Q nonzero {int((Q != 0).sum())}/{SAMPLES}, Q == rule R1: {eq}")
    if idx == 0:
        rng = np.random.default_rng(999)
        Trand = {"P4": [{tuple(int(x) for x in rng.integers(0, 4, 3)): int(rng.integers(1, p)) for _ in range(4)}
                        for _ in range(4)]}
        for cname, cpred in [("X3 random tensor", predicted_Q(cols, word, events, p, Trand)),
                             ("X4 kappa = 1", predicted_Q(cols, word, events, p, TENS[p], kappa=1))]:
            matched = bool((Q == cpred).all())
            controls.append({"control": cname, "fixture": name, "matched": matched})
            log(f"  control {cname}: matched {matched} (must be False)")
# X5: no insertion, predicted as if inserted
word, n = torus_sum(8, 5)
Mo = BraidModel(word, n, 5)
cols = samples(Mo, np.random.default_rng(300))
Q = measure(Mo, cols)
cpred = predicted_Q(cols, word, [(0, 1, "P4")], 5, TENS[5])
controls.append({"control": "X5 no insertion predicted as inserted", "fixture": "T(2,5)x8", "matched": bool((Q == cpred).all())})
log("  control X5: matched", controls[-1]["matched"], "(must be False)")

log("part B, level model full tables")
for name, spec, p, inserts in STEERING_LEVEL:
    base, n = base_word(spec, p)
    word, events = build(base, inserts)
    Lold = LevelModel(base, n, p, Bc)
    Lnew = LevelModel(word, n, p, Bc)
    H = Lold.H
    Hn = Lnew.matched(H, Lold)
    Told, Tnew = Lold.table(H), Lnew.table(Hn)
    (lev, off, braid), = events
    M = TENS[p][braid]
    d = len(H)

    def ell(c, k):
        return (c[Lnew.gen(lev, off + 2 * k + 1)] - c[Lnew.gen(lev, off + 2 * k)]) % p
    ok = True
    nz = 0
    for key in Told:
        iw, ix, iy, i_s = key
        tot = 0
        for j in range(4):
            lam = sum(v * ell(Hn[iy], k[0]) * ell(Hn[ix], k[1]) * ell(Hn[iw], k[2]) for k, v in M[j].items())
            tot += lam * ell(Hn[i_s], j)
        diff = (Tnew[key] - Told[key]) % p
        nz += diff != 0
        ok &= diff == (-KAPPA * tot) % p
    rows.append({"part": "B-level", "fixture": name, "p": p, "dimV": d, "entries": len(Told), "dQ_nonzero": nz, "equal": ok})
    if not ok:
        fails.append(("B-level", name))
    log(f"  {name}: full table {len(Told)} entries, dQ nonzero {nz}, dQ == -KAPPA * rule: {ok}")

log("part B, independent lifting test (BCH group, Wirtinger presentation)")
name, spec, p, inserts = LIFT_FIXTURE
base, n = base_word(spec, p)
word, events = build(base, inserts)
Mo = BraidModel(word, n, p)
U, rels, arc = C.presentation(word, n, 2)
L4 = Bc.four_way_algebra(p, 2, 1)
ix, iy, iw = (L4.idx[s] for s in "xyw")


def arc_values(top):
    vals = [None] * U
    cur = np.array(top, dtype=np.int64).copy()
    for l, g in enumerate(word):
        for q in range(n):
            a = arc[(l, q)]
            if vals[a] is None:
                vals[a] = int(cur[q])
            elif vals[a] != int(cur[q]):
                raise AssertionError("arc color mismatch")
        cur = transport(cur[None, :], [g], 1, p)[0]
    return vals


rng = np.random.default_rng(400)
ones = np.ones(n, dtype=np.int64)
agree, lifts, comp_ok = 0, 0, True
dimH = len(Mo.Fix) - 1
for t in range(LIFT_SAMPLES):
    cy, cx, cw = ((rng.integers(0, p, (1, len(Mo.Fix))) @ Mo.Fix) % p for _ in range(3))
    if t < 10:
        cy = (int(rng.integers(0, p)) * ones[None, :]) % p          # zero class
    elif t < 20:
        cx = (int(rng.integers(0, p)) * ones[None, :]) % p
    qzero = bool(Mo.Q_vanishes_identically(cy, cx, cw)[0])
    cnt = Bc.direct_count(L4, U, rels, 1, fix_f1={ix: arc_values(cx[0]), iy: arc_values(cy[0]), iw: arc_values(cw[0])})
    agree += (cnt > 0) == qzero
    lifts += cnt > 0
    if cnt not in (0, p ** (dimH + 1)):
        comp_ok = False
eq = agree == LIFT_SAMPLES and comp_ok
rows.append({"part": "B-lift", "fixture": name, "p": p, "samples": LIFT_SAMPLES, "agree": agree, "lifting": int(lifts),
             "completions_p^(N+1)": comp_ok, "equal": eq})
if not eq:
    fails.append(("B-lift", agree, comp_ok))
log(f"  {name}: lift <=> Q(c; .) = 0 on {agree}/{LIFT_SAMPLES} samples ({lifts} lift), completions p^(N+1): {comp_ok}")

# ------------------------------------------------------------------ part C: gadgets
log("part C, gadgets")
for p in GADGET_PRIMES:
    for gi, (gname, (nv, edges)) in enumerate(GRAPHS.items()):
        word, nstr, events, leaves, N = gadget(nv, edges, p)
        Mo = BraidModel(word, nstr, p)
        per_fixture_machinery(Mo, N, f"gadget {gname} p={p}")
        cols = samples(Mo, np.random.default_rng(500 + 10 * p + gi))
        Q = measure(Mo, cols)
        pred_t = predicted_Q(cols, word, events, p, TENS[p])
        pred_c = predicted_Q_closed_form(cols, leaves, p, TENS[p])
        leaves_ok = True
        for (lev, off, _), lv in zip(events, leaves):
            mid = transport(cols["s"], word, lev, p)
            for k in range(4):
                a, b = lv[k]
                if ((mid[:, off + 2 * k + 1] - mid[:, off + 2 * k] - (cols["s"][:, b] - cols["s"][:, a])) % p).any():
                    leaves_ok = False
        eq = bool((Q == pred_c).all()) and bool((Q == pred_t).all()) and leaves_ok
        rows.append({"part": "C-gadget", "graph": gname, "p": p, "vertices": nv, "edges": len(edges), "crossings": len(word),
                     "strands": nstr, "summands": N, "dimV": len(Mo.Fix) - 1, "samples": SAMPLES,
                     "Q_nonzero": int((Q != 0).sum()), "closed_form_leaves": leaves_ok, "equal": eq})
        if not eq:
            fails.append(("C-gadget", gname, p))
        log(f"  {gname} p={p}: {len(word)} crossings, {nstr} strands, dim V {len(Mo.Fix) - 1}, Q nonzero "
            f"{int((Q != 0).sum())}/{SAMPLES}, Q == rule R2: {eq} (closed-form leaves {leaves_ok})")
        if p == 5 and gname == "K3":
            cp = predicted_Q_closed_form(cols, leaves[:-1], p, TENS[p])
            controls.append({"control": "X1 one edge dropped", "fixture": "gadget K3 p=5", "matched": bool((Q == cp).all())})
            log("  control X1: matched", controls[-1]["matched"], "(must be False)")
        if p == 5 and gname == "P3":
            cp = predicted_Q(cols, word, events, p, TENS[p], swap02=True)
            controls.append({"control": "X2 bundles 0 and 2 swapped", "fixture": "gadget P3 p=5", "matched": bool((Q == cp).all())})
            log("  control X2: matched", controls[-1]["matched"], "(must be False)")

# ------------------------------------------------------------------ part D: independent homomorphism counts
log("part D, independent counts")
for name, (w, n), p, N, k in COUNTS:
    U, rels, _ = C.presentation(w, n, 2)
    L4 = Bc.four_way_algebra(p, 2, 1)
    t1 = time.time()
    cnt = Bc.direct_count(L4, U, rels, k)
    pred = p ** (N + 4 + 3 * N) if k == 1 else 1
    rows.append({"part": "D-count", "manifold": f"S^3_2({name})", "p": p, "sector": k, "count": cnt, "predicted": pred,
                 "equal": cnt == pred, "seconds": round(time.time() - t1, 1)})
    if cnt != pred:
        fails.append(("D-count", name, k, cnt, pred))
    log(f"  S^3_2({name}) sector {k}: {cnt} (predicted {pred})")

# ------------------------------------------------------------------ verdict
bad_controls = [c for c in controls if c["matched"]]
if machinery_fail or bad_controls:
    verdict = "invalid"
elif not fails:
    verdict = "supported"
else:
    verdict = "refuted"
result = {"experiment_id": "BEYOND-CLASS2-20261027-001B-E001", "verdict": verdict, "machinery_failures": machinery_fail,
          "failures": fails, "controls": controls, "rows": len(rows), "seconds": round(time.time() - T0, 1)}
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "rows.json"), "w") as f:
    json.dump(rows, f, indent=1, default=str)
with open(os.path.join(OUT, "result.json"), "w") as f:
    json.dump(result, f, indent=1, default=str)
log("verdict:", verdict, "failures:", fails, "machinery:", machinery_fail, "bad controls:", bad_controls)
