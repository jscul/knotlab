"""COPRIME-DICHOTOMY-20261027-001B-E001: base terms and steering at characters of order d >= 3 (frozen contract, run once).
Writes result.json, rows.json and run_log.txt to the artifact directory."""
import glob
import json
import os
import sys
import time
import numpy as np

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("CD_ROOT") or os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.environ.get("CD_OUT") or os.path.join(ROOT, "artifacts", "COPRIME-DICHOTOMY-20261027-001B", os.path.basename(HERE))
DRY = bool(os.environ.get("CD_DRY"))     # scoping dry run on trimmed cases (never used for the frozen run)
sys.path.insert(0, HERE)
sys.path.insert(1, glob.glob(os.path.join(ROOT, "proofs/COPRIME-DICHOTOMY-20261027-001A/*P001_*"))[0])
sys.path.insert(2, glob.glob(os.path.join(ROOT, "experiments/TRIPLE-SYSTEM-20261027-001B/*E001_*"))[0])
sys.path.insert(3, glob.glob(os.path.join(ROOT, "proofs/COPRIME-CLASS2-20261026-001B/*P001_*"))[0])
import gd  # noqa: E402
import mlib  # noqa: E402  (read-only: P4 and its Magnus tensor)
import cp_lib as C  # noqa: E402  (read-only: cables, connected sums)
from cd_lib import BraidAlg, CyclicBraidModel, root_of_unity, nullspace, free_graded  # noqa: E402

rows, failures, machinery, controls = [], [], [], []
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s); print(s, flush=True)


def rc(Mo, c, bs, rng):
    B = Mo.cocycles[c]
    return (rng.integers(0, Mo.p, (bs, len(B))) @ B) % Mo.p


def algebra(name, p, d, e):
    if name == "four-way": return gd.four_way(p, d, e)
    if name == "F3": return gd.p2_quotient(free_graded(p, d, [e, -e], 3, ["y", "v"]))
    if name == "layer4": return gd.layer4_algebra(p, d, e)
    if name == "pairfail3": return free_graded(p, d, [e, e], 3, ["y1", "y2"])
    raise KeyError(name)


# ================================================================ machinery
for p in (5, 7, 11, 13):
    for t in range(2, p):
        for n in (3, 6, 10):
            J = gd.squier(n, t, p)
            for g in list(range(1, n)) + [-g for g in range(1, n)]:
                M1 = gd.bur(n, g, t, p); M2 = gd.bur(n, g, pow(t, p - 2, p), p)
                if ((M2.T @ J @ M1 - J) % p).any():
                    machinery.append(f"J_t invariance fails p={p} t={t} n={n} g={g}")
        # bundle identity for t of order d: sum_{i<d} (J^T s)_{o+i} = sum_i t^i s_{o+i}
        for d in range(2, p):
            if (p - 1) % d: continue
            tt = root_of_unity(p, d)
            n = 3 * d + 2
            J = gd.squier(n, tt, p)
            s = np.random.default_rng(p * 100 + d).integers(0, p, n)
            T = (J.T @ s) % p
            for o in range(0, n - d + 1):
                if (T[o:o + d].sum() - sum(pow(tt, i, p) * s[o + i] for i in range(d))) % p:
                    machinery.append(f"bundle identity fails p={p} d={d} o={o}")
log("machinery: J_t invariance and bundle identity", "ok" if not machinery else machinery[:3])

# ================================================================ R1 pinned multiplicativity (exact class counts)
def class_basis(Mo, c):
    """cocycles modulo the coboundary (constant colouring): a basis of class representatives"""
    Z = Mo.cocycles[c]
    one = np.ones((1, Mo.n), dtype=np.int64)
    reps = []
    for z in Z:
        M = np.array(reps + [one[0], z]) % Mo.p
        from cd_lib import rank
        if rank(M, Mo.p) == len(reps) + 2: reps.append(z)
    return np.array(reps, dtype=np.int64)


def exact_lift_count(word, n, A, q, e, d, p):
    Mo = CyclicBraidModel(word, n, A, q)
    Bx, By = class_basis(Mo, e % d), class_basis(Mo, (-e) % d)
    kx, ky = len(Bx), len(By)
    import itertools
    coeffs = np.array(list(itertools.product(range(p), repeat=kx + 2 * ky)), dtype=np.int64)
    total = 0
    ix, iy, iw = (A.idx[s] for s in "xyw")
    for b0 in range(0, len(coeffs), 20000):
        cf = coeffs[b0:b0 + 20000]
        inputs = {ix: (cf[:, :kx] @ Bx) % p, iy: (cf[:, kx:kx + ky] @ By) % p, iw: (cf[:, kx + ky:] @ By) % p}
        ok, _, _ = Mo.solve(inputs)
        total += int(ok.sum())
    return total, (kx, ky)


R1 = []
for (p, d, e, kname) in ([(5, 4, 1, "6_1")] if DRY else [(5, 4, 1, "6_1"), (7, 3, 1, "6_1"), (7, 6, 1, "3_1")]):
    zeta = root_of_unity(p, d)
    A = BraidAlg(gd.four_way(p, d, e), zeta)
    K = gd.CHIRAL[kname]
    KK = C.connected_sum([K, K])
    res = {}
    for q in (1, p):
        c1, dims1 = exact_lift_count(K[0], K[1], A, q, e, d, p)
        c2, dims2 = exact_lift_count(KK[0], KK[1], A, q, e, d, p)
        res[q] = (c1, c2, dims1, dims2)
    row = {"test": "R1", "p": p, "d": d, "e": e, "knot": kname,
           "slope d/p: count(K), count(K#K), product": [res[p][0], res[p][1], res[p][0] ** 2],
           "slope d/1: count(K), count(K#K), product": [res[1][0], res[1][1], res[1][0] ** 2],
           "class dims (x; y, w)": [res[p][2], res[p][3]]}
    row["multiplicative at d/p"] = res[p][1] == res[p][0] ** 2
    row["multiplicative at d/1"] = res[1][1] == res[1][0] ** 2
    R1.append(row); rows.append(row); log(json.dumps(row))
if not all(r["multiplicative at d/p"] for r in R1): failures.append("R1: some slope-d/p count is not multiplicative")
if all(r["multiplicative at d/1"] for r in R1): failures.append("R1: no slope-d/1 channel observed")

# ================================================================ R2 local forms
rng = np.random.default_rng(20261027)


def lift_fraction(word, n, L, p, d, q, bs=32):
    zeta = root_of_unity(p, d)
    A = BraidAlg(L, zeta)
    Mo = CyclicBraidModel(word, n, A, q)
    odd = [k for k in range(L.D) if L.chars[k] % d]
    inputs = {k: rc(Mo, int(L.chars[k]), bs, rng) for k in odd}
    ok, _, _ = Mo.solve(inputs)
    return float(ok.mean()), {c: len(Mo.cocycles[c]) for c in range(1, d)}


def roots_of(word, n, p, d):
    zeta = root_of_unity(p, d)
    L1 = gd.four_way(p, d, 1)
    Mo = CyclicBraidModel(word, n, BraidAlg(L1, zeta), p)
    return [c for c in range(1, d) if len(Mo.cocycles[c]) == 2 and len(Mo.cocycles[(-c) % d]) == 2 and np.gcd(c, d) == 1]


R2 = []
chiral_cases = [("3_1", 13, 6), ("5_2", 11, 5), ("6_1", 7, 3), ("6_1", 5, 4), ("7_5", 7, 3), ("8_5", 13, 6)][:2 if DRY else 99]
for kname, p, d in chiral_cases:
    w, n = gd.CHIRAL[kname]
    for e in roots_of(w, n, p, d):
        fr, dims = lift_fraction(w, n, gd.four_way(p, d, e), p, d, p)
        row = {"test": "R2 chiral", "knot": kname, "p": p, "d": d, "e": e, "algebra": "four-way", "lift fraction": fr}
        R2.append(row); rows.append(row)
        if fr == 1.0: failures.append(f"R2: chiral {kname} p={p} d={d} e={e} does not obstruct")
amph_count = 0
for kname, (w, n) in list(gd.AMPH.items())[:1 if DRY else 99]:
    for p in ((11,) if DRY else (7, 11, 13, 17, 19)):
        for d in range(3, p):
            if (p - 1) % d: continue
            for e in roots_of(w, n, p, d):
                for aname in ("four-way", "F3", "layer4"):
                    fr, dims = lift_fraction(w, n, algebra(aname, p, d, e), p, d, p, bs=16)
                    row = {"test": "R2 amphichiral", "knot": kname, "p": p, "d": d, "e": e, "algebra": aname, "lift fraction": fr}
                    R2.append(row); rows.append(row); amph_count += 1
                    if fr < 1.0: failures.append(f"R2: amphichiral {kname} p={p} d={d} e={e} {aname} obstructs")
log("R2 amphichiral rows", amph_count)
cable_count = 0
for (p, d, k) in ([(5, 4, 2), (7, 6, 3)] if DRY else [(5, 4, 2), (13, 4, 2), (7, 6, 3), (13, 6, 3), (11, 10, 5), (13, 12, 6), (17, 8, 4)]):
    w, n = gd.torus_cable(p, k)
    zeta = root_of_unity(p, d)
    for e in [c for c in range(1, d) if pow(zeta, c * k, p) == p - 1][:2]:
        for aname in ("four-way", "F3", "layer4", "pairfail3"):
            L = algebra(aname, p, d, e)
            fr, dims = lift_fraction(w, n, L, p, d, p, bs=12)
            row = {"test": "R2 cable", "summand": f"({k},1)-cable of T(2,{p})", "p": p, "d": d, "e": e, "algebra": aname,
                   "lift fraction": fr, "roots (dim Z1 = 2)": [c for c, v in dims.items() if v == 2]}
            R2.append(row); rows.append(row); cable_count += 1
            if fr < 1.0: failures.append(f"R2: cable k={k} p={p} d={d} e={e} {aname} obstructs")
            expect = sorted(c for c in range(1, d) if pow(zeta, c * k, p) == p - 1)
            if sorted(c for c, v in dims.items() if v == 2) != expect:
                failures.append(f"R2: cable k={k} p={p} d={d}: roots {dims} differ from t^k = -1")
log("R2 cable rows", cable_count)

# ================================================================ R3 steering on single insertions
def steer_case(p, d, e, summand, ncopies, aname, level_frac, offset, bs=10, kap=None, reverse=True, check_base=True):
    zeta = root_of_unity(p, d)
    L = algebra(aname, p, d, e); A = BraidAlg(L, zeta)
    base, n = C.connected_sum([summand] * ncopies)
    lev = int(len(base) * level_frac)
    w2 = base[:lev] + C.cable(mlib.P4, d, offset=offset) + base[lev:]
    Mb, Mi = CyclicBraidModel(base, n, A, p), CyclicBraidModel(w2, n, A, p)
    same = all(len(Mb.cocycles[c]) == len(Mi.cocycles[c]) and
               not ((Mi.Lin[c] @ Mb.cocycles[c].T) % p).any() for c in range(1, d))
    odd = [k for k in range(L.D) if L.chars[k] % d]
    inputs = {k: rc(Mb, int(L.chars[k]), bs, rng) for k in odd if L.layer[k] <= 3}
    data = {k: v for k, v in inputs.items() if L.layer[k] <= 2}
    events = [(lev, offset, [[offset + j * d + i for i in range(d)] for j in range(4)])]
    out = []
    for comp in [k for k in odd if L.layer[k] >= 3]:
        s = rc(Mb, (-int(L.chars[comp])) % d, bs, rng)
        Qb, okb, Rb, _ = gd.measure_Q(Mb, inputs, int(L.layer[comp]), comp, s)
        Qi, oki, Ri, _ = gd.measure_Q(Mi, inputs, int(L.layer[comp]), comp, s)
        valid = okb & oki
        pred = gd.predict_Q(L, A, base, n, events, data, s, comp, p, k_override=kap, reverse=reverse)
        dQ = (Qi - Qb) % p
        # identity among relations: (J^T 1, 0) annihilates every obstruction vector
        one = np.ones((bs, n), dtype=np.int64)
        tcomp = pow(zeta, int(L.chars[comp]), p)
        y1 = (one @ gd.squier(n, tcomp, p)) % p
        ann = not ((Ri[:, :n, comp] * y1).sum(axis=1) % p)[valid].any()
        out.append({"component": L.names[comp], "layer": int(L.layer[comp]), "valid samples": int(valid.sum()),
                    "base Q zero": bool((Qb[valid] == 0).all()), "match": bool((dQ[valid] == pred[valid]).all()),
                    "nonzero": int((dQ[valid] != 0).sum()), "J^T 1 annihilates": ann})
    return same, out


R3 = []
steer_cases = [(7, 3, 1, gd.AMPH["6_3"], 6), (7, 3, 2, gd.AMPH["6_3"], 6), (13, 3, 1, gd.AMPH["8_17"], 6),
               (11, 5, 2, gd.AMPH["4_1"], 6), (13, 4, 1, gd.torus_cable(13, 2), 6), (5, 4, 1, gd.torus_cable(5, 2), 6),
               (7, 6, 1, gd.torus_cable(7, 3), 6), (13, 6, 5, gd.torus_cable(13, 3), 6)]
for (p, d, e, summ, nc) in (steer_cases[:1] + steer_cases[6:7] if DRY else steer_cases):
    for aname in ("four-way", "F3", "layer4"):
        for (lf, off) in ((0.0, 0), (0.6, 1)):
            same, out = steer_case(p, d, e, summ, nc, aname, lf, off)
            row = {"test": "R3", "p": p, "d": d, "e": e, "algebra": aname, "level fraction": lf, "offset": off,
                   "cocycle spaces unchanged": same, "components": out}
            R3.append(row); rows.append(row)
            if not same: machinery.append(f"R3 cocycles changed p={p} d={d} {aname}")
            for o in out:
                if not o["J^T 1 annihilates"]: machinery.append(f"R3 identity among relations p={p} d={d} {aname} {o['component']}")
                if not (o["base Q zero"] and o["match"]): failures.append(f"R3 p={p} d={d} e={e} {aname} lf={lf}: {o}")
            if not any(o["nonzero"] for o in out): failures.append(f"R3 p={p} d={d} e={e} {aname} lf={lf}: no nonzero change")
log("R3 rows", len(R3))

# ================================================================ R4 gadgets
R4 = []
gadget_cases = [(7, 3, 1, gd.AMPH["6_3"], "K2", (2, [(0, 1)])), (7, 3, 1, gd.AMPH["6_3"], "P3", (3, [(0, 1), (1, 2)])),
                (7, 3, 2, gd.AMPH["6_3"], "K3", (3, [(0, 1), (1, 2), (0, 2)])),
                (13, 4, 1, gd.torus_cable(13, 2), "P3", (3, [(0, 1), (1, 2)])), (7, 6, 1, gd.torus_cable(7, 3), "K2", (2, [(0, 1)]))]
for (p, d, e, summ, gname, (nv, edges)) in (gadget_cases[:1] if DRY else gadget_cases):
    zeta = root_of_unity(p, d)
    word, n, events, vstr, pb = gd.build_gadget(nv, edges, d, summ, summ)
    for aname in ("four-way", "layer4"):
        L = algebra(aname, p, d, e); A = BraidAlg(L, zeta)
        Mo = CyclicBraidModel(word, n, A, p)
        bs = 8
        odd = [k for k in range(L.D) if L.chars[k] % d]
        inputs = {k: rc(Mo, int(L.chars[k]), bs, rng) for k in odd if L.layer[k] <= 3}
        data = {k: v for k, v in inputs.items() if L.layer[k] <= 2}
        out = []
        for comp in [k for k in odd if L.layer[k] >= 3]:
            s = rc(Mo, (-int(L.chars[comp])) % d, bs, rng)
            Q, ok, _, _ = gd.measure_Q(Mo, inputs, int(L.layer[comp]), comp, s)
            pred = gd.predict_Q(L, A, word, n, events, data, s, comp, p)
            out.append({"component": L.names[comp], "match": bool((Q[ok] == pred[ok]).all()), "nonzero": int((Q[ok] != 0).sum()),
                        "valid": int(ok.sum())})
        # leaves: bundle 0 reads X_v - X_u, bundles 1-3 the private coordinates (at every odd character, layer-1 cocycles)
        leaf_ok = True
        for (level, off, bundles), (u, v) in zip(events, edges):
            for k in [k for k in odd if L.layer[k] == 1]:
                tk = pow(zeta, int(L.chars[k]), p)
                vals = inputs[k]
                l0 = gd.leaf_values(word, n, level, bundles[0], vals, tk, p)
                if ((l0 - (vals[:, vstr[v]] - vals[:, vstr[u]])) % p).any(): leaf_ok = False
        row = {"test": "R4", "p": p, "d": d, "e": e, "graph": gname, "crossings": len(word), "strands": n, "algebra": aname,
               "components": out, "vertex leaf = X_v - X_u": leaf_ok}
        R4.append(row); rows.append(row); log(json.dumps(row))
        if not leaf_ok: machinery.append(f"R4 vertex leaf p={p} d={d} {gname}")
        for o in out:
            if not o["match"]: failures.append(f"R4 p={p} d={d} {gname} {aname}: {o}")
        if not any(o["nonzero"] for o in out): failures.append(f"R4 p={p} d={d} {gname} {aname}: form identically zero")

# ================================================================ negative controls (each must mismatch)
def control(name, ok_match):
    controls.append({"control": name, "matched": bool(ok_match)})
    log("control", name, "matched" if ok_match else "mismatch (as required)")


same, out = steer_case(7, 6, 1, gd.torus_cable(7, 3), 6, "four-way", 0.0, 0, kap=2)
control("X1 kappa = 2 (the r = 2 constant) at d = 6, p = 7", all(o["match"] for o in out))
same, out = steer_case(13, 3, 1, gd.AMPH["8_17"], 6, "four-way", 0.0, 0, reverse=False)
control("X2 bundle product in forward order (d = 3, p = 13)", all(o["match"] for o in out))
same, out = steer_case(7, 3, 1, gd.CHIRAL["6_1"], 6, "four-way", 0.0, 0)
control("X3 twist-knot base (6_1, p = 7, d = 3): base Q zero and rule holds", all(o["match"] and o["base Q zero"] for o in out))

verdict = "invalid" if machinery or any(c["matched"] for c in controls) else ("supported" if not failures else "refuted")
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "result.json"), "w") as fh:
    json.dump({"experiment_id": "COPRIME-DICHOTOMY-20261027-001B-E001", "verdict": verdict, "machinery_failures": machinery,
               "failures": failures, "controls": controls,
               "counts": {"R1": len(R1), "R2": len(R2), "R3": len(R3), "R4": len(R4)},
               "seconds": round(time.time() - T0, 1)}, fh, indent=1)
    fh.write("\n")
with open(os.path.join(OUT, "rows.json"), "w") as fh:
    json.dump(rows, fh, indent=1, default=str); fh.write("\n")
with open(os.path.join(OUT, "run_log.txt"), "w") as fh:
    fh.write("\n".join(LOG) + "\n")
log("verdict", verdict, "failures", failures[:5], "seconds", round(time.time() - T0, 1))
