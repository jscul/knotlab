"""Referee R1 for WEAVE-PAIR-20261118-001 (own code; the study's twistlib.py is not imported; its stored results are only compared).

  ../../../.venv/bin/python -B referee_pair.py <part> > referee_pair_<part>.json      (from this directory)

The weave as in WEAVE-MIX-R1: up knot (v(i,j), v(i+1,j), v(i,j+1)), down knot (v(i+1,j), v(i,j+1), v(i+1,j+1)), code k excludes
EXCL[k].  The pair is WEAVE-MIX's survivors 0 and 1, read from its readout.json.

The twist is built independently of the study: no value is read flipped.  Instead the two knots that cross the seam between
column s and s + 1 are re-signed, as a flip of the place that lies in column s + 1 does to an excluded pair: the up knot U(s) on
(v(s), v(s+1), v'(s)) flips its second place, the down knot D(s) on (v(s+1), v'(s), v'(s+1)) its first and third.

Parts:
  spec   dense row transfers (the referee's strip() from WEAVE-LAWS-R1) at widths 6, 9, 12, both arrangements, both sectors, the
         seam at two places: flip-even and flip-odd spectra, per-site, spin and energy gaps, the sector splitting; against the
         study's stored values; and exact relations in the spectra (eigenvalues at exactly lambda_0 / 2).
  site   a transfer applied one distinction at a time (the referee's own, generalised to per-column knots) against the dense one at
         widths 6, 9 and 12 in both sectors; then Arnoldi at 15 and 18.
  corr   width 12, exact: the flip-odd sector's leading eigenvalues as complex numbers (is the equal-magnitude pair complex or
         +-?), the correlation along the transfer C(r) for r = 1..90 at each column position (|C| meets rounding near 90), the study's readings (single-row
         decrease, two-row tick, the slope fit on r = 10..30) and the envelope rate on longer windows.
  s3     WEAVE-MIX's survivor 3 (decoupled two-column strips): its correlation along the transfer at single-row resolution, and its
         flip-odd eigenvalues, for "first on the weave" and "a strict ruler is still not found".
  w21    width 21 for arr1 in both sectors, by the site transfer and Arnoldi.
  phase  the leading flip-odd eigenvalues as complex numbers at widths 6 to 18 (is the pair +- or complex at every width?).
  sym    the half-turn: the image of arr1 under (x, y) -> (-x, -y) shifted, and a search over gauges (one flip bit per distinction,
         period 6 around and 2 along) that turns it into arr2.
"""
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.sparse.linalg import LinearOperator, eigs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/WEAVE-LAWS-20261117-001/referee-R1"))
from referee_scope import strip, flip  # noqa: E402  (the referee's own strip transfer and re-signing, WEAVE-LAWS-R1)

EXCL = [frozenset({(0, 0, 0), (1, 1, 1)}), frozenset({(1, 0, 0), (0, 1, 1)}), frozenset({(0, 1, 0), (1, 0, 1)}),
        frozenset({(0, 0, 1), (1, 1, 0)})]
RD = json.load(open(ROOT / "artifacts/WEAVE-MIX-20261117-001B/WEAVE-MIX-20261117-001B-E001_mixes/readout.json"))
STUDY = json.load(open(ROOT / "artifacts/WEAVE-PAIR-20261118-001B/WEAVE-PAIR-20261118-001B-E001_twist/results.json"))
L3 = math.log(3)


def parse(a):
    return {(int(k.split(",")[0]), int(k.split(",")[1]), k.split(",")[2]): v for k, v in a.items()}


SURV = [parse(s["arrangement"]) for s in RD["post_hoc"]["survivors"]]
PAIR = {"arr1": SURV[0], "arr2": SURV[1]}


def dims(arr):
    return max(i for i, _, _ in arr) + 1, max(j for _, j, _ in arr) + 1


def row_knots(w, arr, j, twist, seam=None):
    pc, _ = dims(arr)
    ups = [set(EXCL[arr[(i % pc, j, "U")]]) for i in range(w)]
    downs = [set(EXCL[arr[(i % pc, j, "D")]]) for i in range(w)]
    if twist:
        s = w - 1 if seam is None else seam
        ups[s] = flip(ups[s], (0, 1, 0))
        downs[s] = flip(downs[s], (1, 0, 1))
    return ups, downs


def dense(w, arr, twist, seam=None):
    _, pr = dims(arr)
    M = None
    for j in range(pr):
        T = strip(w, *row_knots(w, arr, j, twist, seam)).astype(np.float64)
        M = T if M is None else M @ T
    return M


def sector_mats(M, w):
    R = 1 << w
    reps = [a for a in range(R) if a < (a ^ (R - 1))]
    comp = [a ^ (R - 1) for a in reps]
    A, B = M[np.ix_(reps, reps)], M[np.ix_(reps, comp)]
    return A + B, A - B, reps


def readings(ev_e, ev_o, w, pr=1):
    lam0 = ev_e[0]
    sec = next(x for x in ev_e[1:] if x < lam0 * (1 - 1e-9))
    return {"per_site": float(lam0 ** (1 / (w * pr))), "spin_gap": float(math.log(lam0 / ev_o[0]) / L3 / pr),
            "energy_gap": float(math.log(lam0 / sec) / L3 / pr), "lambda0": float(lam0), "top_odd": float(ev_o[0])}


def part_spec():
    out = {}
    for name, arr in PAIR.items():
        for w in (6, 9, 12):
            for tw in (False, True):
                for seam in ((None,) if not tw else (None, 0)):
                    M = dense(w, arr, tw, seam)
                    E, O, _ = sector_mats(M, w)
                    ev_e = np.sort(np.abs(np.linalg.eigvals(E)))[::-1]
                    ev_o = np.sort(np.abs(np.linalg.eigvals(O)))[::-1]
                    r = readings(ev_e, ev_o, w)
                    r["even_at_exactly_half_lambda0"] = int(np.sum(np.abs(ev_e - ev_e[0] / 2) < 1e-8 * ev_e[0]))
                    r["even_top4"] = [float(x) for x in ev_e[:4]]
                    r["odd_top4"] = [float(x) for x in ev_o[:4]]
                    key = f"{name}:{w}:{'anti' if tw else 'per'}" + ("" if seam is None else ":seam_at_0")
                    st = STUDY["W2"].get(f"{name}:{w}:{'anti' if tw else 'per'}")
                    if st:
                        r["study_differs_by"] = max(abs(r[k] - st[k]) for k in ("per_site", "spin_gap", "energy_gap"))
                    out[key] = r
                    print("spec", key, json.dumps(r), file=sys.stderr, flush=True)
    for w in (6, 9, 12):
        a = out[f"arr1:{w}:per"]["lambda0"], out[f"arr1:{w}:anti"]["lambda0"]
        b = out[f"arr2:{w}:per"]["lambda0"], out[f"arr2:{w}:anti"]["lambda0"]
        out[f"splitting:{w}"] = {"log3_per_row_arr1": abs(math.log(a[0] / a[1]) / L3),
                                 "arr1_equals_arr2_same_sector": abs(a[0] - b[0]) < 1e-9 * a[0] and abs(a[1] - b[1]) < 1e-9 * a[0],
                                 "arr1_equals_arr2_other_sector": abs(a[0] - b[1]) < 1e-9 * a[0] and abs(a[1] - b[0]) < 1e-9 * a[0]}
    return out


def site_operator(w, arr, twist):
    """v -> v M, one distinction at a time, front of w + 1 bits (bit w keeps the old row's column 0 for the seam)."""
    _, pr = dims(arr)
    N = 1 << (w + 1)
    s = np.arange(N)
    bit = [(s >> t) & 1 for t in range(w + 1)]

    def bad(ex, a, b, c):
        m = np.zeros(N, bool)
        for p in ex:
            m |= (a == p[0]) & (b == p[1]) & (c == p[2])
        return m
    plan = []
    for j in range(pr):
        ups, downs = row_knots(w, arr, j, twist)
        for i in range(w):
            masks, idxs = [], []
            for x in (0, 1):
                xs = np.full(N, x)
                old_next = bit[i + 1] if i + 1 < w else bit[w]
                m = bad(ups[i], bit[i], old_next, xs)                 # U(i): (a_i, a_{i+1}, b_i)
                if i >= 1:
                    m |= bad(downs[i - 1], bit[i], bit[i - 1], xs)    # D(i-1): (a_i, b_{i-1}, b_i)
                if i == w - 1:
                    m |= bad(downs[w - 1], bit[w], xs, bit[0])        # D(w-1): (a_0, b_{w-1}, b_0)
                idx = (s & ~(1 << i)) | (x << i)
                if i == 0:
                    idx = (idx & ~(1 << w)) | (bit[0] << w)
                masks.append(~m)
                idxs.append(idx)
            plan.append((masks, idxs))

    def apply(v):
        V = np.zeros(N)
        V[: 1 << w] = v
        for k, (masks, idxs) in enumerate(plan):
            new = np.zeros(N)
            for ok, idx in zip(masks, idxs):
                new += np.bincount(idx[ok], weights=V[ok], minlength=N)
            V = new
            if (k + 1) % w == 0:
                V[: 1 << w] += V[1 << w:]
                V[1 << w:] = 0
        return V[: 1 << w]
    return apply


def arnoldi(w, arr, twist, k=6):
    op = site_operator(w, arr, twist)
    R = 1 << w
    fl = np.arange(R) ^ (R - 1)
    res = []
    for sgn in (1, -1):
        def mv(v, sgn=sgn):
            u = op(np.asarray(v).reshape(-1))
            return 0.5 * (u + sgn * u[fl])
        L = LinearOperator((R, R), matvec=mv, dtype=np.float64)
        v0 = np.random.default_rng(7 + w).random(R) + 1.0
        v0 = 0.5 * (v0 + sgn * v0[fl])
        ev = eigs(L, k=k if sgn == 1 else 4, which="LM", return_eigenvectors=False, tol=1e-11, maxiter=20000, v0=v0)
        res.append(np.sort(np.abs(ev))[::-1])
    return res


def part_site():
    import time
    out = {"site_vs_dense": {}, "arnoldi": {}}
    for w in (6, 9, 12):
        for tw in (False, True):
            worst = 0.0
            for name, arr in PAIR.items():
                M = dense(w, arr, tw)
                op = site_operator(w, arr, tw)
                for seed in range(3):
                    v = np.random.default_rng(seed).random(1 << w)
                    worst = max(worst, float(np.max(np.abs(v @ M - op(v)))))
            out["site_vs_dense"][f"{w}:{'anti' if tw else 'per'}"] = worst
            print("site", w, tw, worst, file=sys.stderr, flush=True)
    for w in (15, 18):
        for name, arr in PAIR.items():
            for tw in (False, True):
                t = time.time()
                ev_e, ev_o = arnoldi(w, arr, tw)
                r = readings(ev_e, ev_o, w)
                st = STUDY["W2"][f"{name}:{w}:{'anti' if tw else 'per'}"]
                r["study_differs_by"] = max(abs(r[k] - st[k]) for k in ("per_site", "spin_gap", "energy_gap"))
                r["seconds"] = round(time.time() - t, 1)
                out["arnoldi"][f"{name}:{w}:{'anti' if tw else 'per'}"] = r
                print("arnoldi", name, w, tw, json.dumps(r), file=sys.stderr, flush=True)
    return out


def correlations(M, w, positions, rmax):
    """C(r) = <s_c(0) s_c(r)> on the infinite cylinder (spins 2v - 1; mean 0 by the flip), for each column c."""
    ev, Rv = np.linalg.eig(M)
    evL, Lv = np.linalg.eig(M.T)
    i0, j0 = int(np.argmax(np.abs(ev))), int(np.argmax(np.abs(evL)))
    lam = ev[i0].real
    r = np.abs(Rv[:, i0].real)
    l = np.abs(Lv[:, j0].real)
    S = 2.0 * ((np.arange(1 << w)[:, None] >> np.arange(w)[None, :]) & 1) - 1.0
    out = {}
    for c in positions:
        v = S[:, c] * r
        seq = []
        for _ in range(rmax):
            v = M @ v / lam
            seq.append(float((l * S[:, c]) @ v / (l @ r)))
        out[c] = seq
    return out


def study_readings(seq):
    mags = [abs(x) for x in seq[:30]]
    cut = next((k for k, m in enumerate(mags) if m < 1e-8), len(mags))
    live = mags[:cut]
    single = all(live[k + 1] < live[k] for k in range(len(live) - 1))
    ev, od = live[1::2], live[0::2]
    two = all(ev[k + 1] < ev[k] for k in range(len(ev) - 1)) and all(od[k + 1] < od[k] for k in range(len(od) - 1))
    tau = [-math.log(m, 3) if m > 0 else float("inf") for m in mags]
    rs = [k + 1 for k in range(9, 30) if mags[k] > 1e-14]
    fit = float(np.polyfit(rs, [tau[q - 1] for q in rs], 1)[0])
    return single, two, fit


def envelope_rate(seq, r0, r1, period):
    """Slope of -log3 of the running maximum of |C| over windows of one oscillation period, fitted on r0..r1."""
    mags = np.abs(np.array(seq))
    xs, ys = [], []
    for r in range(r0, r1 - period + 1, period):
        win = mags[r - 1:r - 1 + period]
        k = int(np.argmax(win))
        xs.append(r + k)
        ys.append(-math.log(win[k], 3))
    return float(np.polyfit(xs, ys, 1)[0])


def part_corr(w=12):
    out = {}
    for name, arr in PAIR.items():
        for tw in (False, True):
            M = dense(w, arr, tw)
            E, O, _ = sector_mats(M, w)
            ee = np.linalg.eigvals(E)
            eo = np.linalg.eigvals(O)
            lam0 = float(np.max(np.abs(ee)))
            order = np.argsort(-np.abs(eo))
            top = [complex(eo[i]) for i in order[:6]]
            phases = [float(np.angle(z) / np.pi) for z in top]
            gap = math.log(lam0 / abs(top[0])) / L3
            seqs = correlations(M, w, (0, 1, 2), 90)              # |C| reaches rounding (~1e-14) near r = 90
            pos = {}
            for c, seq in seqs.items():
                single, two, fit = study_readings(seq)
                signs = "".join("+" if x > 0 else "-" for x in seq[:30])
                pos[c] = {"C_1_to_12": [round(x, 8) for x in seq[:12]], "signs_r1_30": signs,
                          "single_row_decrease": single, "two_row_tick": two, "fit_r10_30": fit,
                          "fit_r10_60": float(np.polyfit(range(10, 61), [-math.log(abs(x), 3) for x in seq[9:60]], 1)[0]),
                          "envelope_rate_r30_84": None}
            out[f"{name}:{'anti' if tw else 'per'}"] = {"lambda0": lam0, "spin_gap": gap,
                                                         "odd_top6": [[z.real, z.imag] for z in top],
                                                         "odd_top6_over_lambda0": [abs(z) / lam0 for z in top],
                                                         "odd_top6_phase_over_pi": phases, "positions": pos}
            # the oscillation period from the leading pair's phase
            th = abs(phases[0]) * math.pi
            period = max(2, int(round(2 * math.pi / th))) if th > 1e-9 else 1
            for c, seq in seqs.items():
                out[f"{name}:{'anti' if tw else 'per'}"]["positions"][c]["envelope_rate_r30_84"] = envelope_rate(seq, 30, 84, period)
            out[f"{name}:{'anti' if tw else 'per'}"]["oscillation_period_rows"] = period
            st = STUDY["W3"][f"{name}:{'anti' if tw else 'per'}"]["positions"]
            out[f"{name}:{'anti' if tw else 'per'}"]["study_C_differs_by"] = max(
                abs(a - b) for c in (0, 1, 2) for a, b in zip(seqs[c][:12], st[str(c)]["C"]))
            print("corr", name, tw, json.dumps({k: v for k, v in out[f"{name}:{'anti' if tw else 'per'}"].items() if k != "positions"}),
                  file=sys.stderr, flush=True)
    return out


def part_s3(w=12):
    arr = SURV[3]
    T0 = strip(w, *row_knots(w, arr, 0, False)).astype(np.float64)
    T1 = strip(w, *row_knots(w, arr, 1, False)).astype(np.float64)
    M = T0 @ T1
    ev, Rv = np.linalg.eig(M)
    evL, Lv = np.linalg.eig(M.T)
    i0, j0 = int(np.argmax(np.abs(ev))), int(np.argmax(np.abs(evL)))
    lam = ev[i0].real
    r = np.abs(Rv[:, i0].real)
    l = np.abs(Lv[:, j0].real)
    S = 2.0 * ((np.arange(1 << w)[:, None] >> np.arange(w)[None, :]) & 1) - 1.0
    Ts = [T0, T1]
    # <s_c(o) s_c(o + k)> for a start at row o of the period (o = 0, 1): the measure is l (T_0 ... ) r closed at period boundaries
    res = {}
    for o in (0, 1):
        left0 = l @ T0 if o == 1 else l.copy()
        for c in (0, 1):
            seq = []
            for k in range(1, 41):
                vec = left0 * S[:, c]
                vz = left0.copy()
                for q in range(k):
                    T = Ts[(o + q) % 2]
                    vec = vec @ T
                    vz = vz @ T
                rest = T1 @ r if (o + k) % 2 == 1 else r
                seq.append(float((vec @ (S[:, c] * rest)) / (vz @ rest)))
            mags = [abs(x) for x in seq]
            live = [m for m in mags if m > 1e-12]
            res[f"start row {o}, column {c}"] = {
                "C_1_to_16": [round(x, 8) for x in seq[:16]],
                "signs": "".join("+" if x > 1e-12 else ("-" if x < -1e-12 else "0") for x in seq),
                "abs_strictly_decreasing_single_row": all(live[k + 1] < live[k] for k in range(len(live) - 1)),
                "signed_strictly_decreasing": all(seq[k + 1] < seq[k] for k in range(len(seq) - 1))}
    E, O, _ = sector_mats(M, w)
    eo = np.linalg.eigvals(O)
    lam0 = float(np.max(np.abs(np.linalg.eigvals(E))))
    order = np.argsort(-np.abs(eo))
    res["odd_top4_over_lambda0"] = [[float(eo[i].real / lam0), float(eo[i].imag / lam0)] for i in order[:4]]
    res["spin_gap_per_row"] = float(math.log(lam0 / abs(eo[order[0]])) / L3 / 2)
    return res


def part_sym():
    """arr1 under the half-turn (x, y) -> (-x, -y), shifted by (sx, sy), then a gauge g (period 6 around, 2 along): does it equal
    arr2 knot by knot?  A knot's excluded pair under a gauge flips each place whose distinction's g is 1."""
    A1, A2 = PAIR["arr1"], PAIR["arr2"]

    def knot(arr, i, j, t):
        vs = ((i, j), (i + 1, j), (i, j + 1)) if t == "U" else ((i + 1, j), (i, j + 1), (i + 1, j + 1))
        return vs, EXCL[arr[(i % 3, 0, t)]]
    # every knot of the image, keyed by its vertex set, with its excluded pair read in the target's place order
    found = []
    for sx in range(6):
        for sy in range(2):
            img = {}
            for i in range(-8, 8):
                for j in range(-4, 4):
                    for t in "UD":
                        vs, ex = knot(A1, i, j, t)
                        new = [(-x + sx, -y + sy) for x, y in vs]
                        img[frozenset(new)] = (new, ex)
            for bits in range(1 << 12):
                g = lambda x, y: (bits >> ((x % 6) + 6 * (y % 2))) & 1
                ok = True
                for i in range(6):
                    for j in range(2):
                        for t in "UD":
                            vs, ex = knot(A2, i, j, t)
                            new, ex1 = img[frozenset(vs)]
                            perm = [new.index(v) for v in vs]
                            mapped = {tuple(p[q] ^ g(*vs[k]) for k, q in enumerate(perm)) for p in ex1}
                            if mapped != set(ex):
                                ok = False
                                break
                        if not ok:
                            break
                    if not ok:
                        break
                if ok:
                    gs = [[g(x, y) for x in range(6)] for y in range(2)]
                    found.append({"shift": [sx, sy], "gauge_rows": gs,
                                  "antiperiodic_with_period_3": all(gs[y][x] != gs[y][x + 3] for y in range(2) for x in range(3))})
    return {"maps_found": len(found), "shifts": sorted({tuple(f["shift"]) for f in found}), "examples": found[:4],
            "every_map_needs_the_seam": all(f["antiperiodic_with_period_3"] for f in found) if found else None}


def part_w21():
    """Width 21 for arr1 in both sectors (arr2 follows by the identity of spec), against the study's stored values."""
    import time
    out = {}
    for tw in (False, True):
        t = time.time()
        ev_e, ev_o = arnoldi(21, PAIR["arr1"], tw)
        r = readings(ev_e, ev_o, 21)
        st = STUDY["W2"][f"arr1:21:{'anti' if tw else 'per'}"]
        r["study_differs_by"] = max(abs(r[k] - st[k]) for k in ("per_site", "spin_gap", "energy_gap"))
        r["even_top"] = [float(x) for x in ev_e[:6]]
        r["seconds"] = round(time.time() - t, 1)
        out[f"arr1:21:{'anti' if tw else 'per'}"] = r
        print("w21", tw, json.dumps(r), file=sys.stderr, flush=True)
    return out


def part_phase():
    """The leading flip-odd eigenvalues as complex numbers, arr1, both sectors: dense at widths 6, 9, 12; Arnoldi at 15, 18.
    Is the equal-magnitude pair a +- pair (phases 0 and pi) or a complex pair, and does that depend on the width?"""
    out = {}
    for w in (6, 9, 12, 15, 18):
        for tw in (False, True):
            if w <= 12:
                M = dense(w, PAIR["arr1"], tw)
                E, O, _ = sector_mats(M, w)
                lam0 = float(np.max(np.abs(np.linalg.eigvals(E))))
                eo = np.linalg.eigvals(O)
            else:
                op = site_operator(w, PAIR["arr1"], tw)
                R = 1 << w
                fl = np.arange(R) ^ (R - 1)
                vals = {}
                for sgn in (1, -1):
                    L = LinearOperator((R, R), matvec=lambda v, sgn=sgn: (lambda u: 0.5 * (u + sgn * u[fl]))(op(np.asarray(v).reshape(-1))),
                                       dtype=np.float64)
                    v0 = np.random.default_rng(3 + w).random(R) + 1.0
                    v0 = 0.5 * (v0 + sgn * v0[fl])
                    vals[sgn] = eigs(L, k=6, which="LM", return_eigenvectors=False, tol=1e-11, maxiter=20000, v0=v0)
                lam0 = float(np.max(np.abs(vals[1])))
                eo = vals[-1]
            order = np.argsort(-np.abs(eo))[:4]
            out[f"{w}:{'anti' if tw else 'per'}"] = {"over_lambda0": [round(float(abs(eo[i]) / lam0), 9) for i in order],
                                                     "phase_over_pi": [round(float(np.angle(eo[i]) / np.pi), 6) for i in order]}
            print("phase", w, tw, json.dumps(out[f"{w}:{'anti' if tw else 'per'}"]), file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    res = {"spec": part_spec, "site": part_site, "corr": part_corr, "s3": part_s3, "sym": part_sym, "w21": part_w21, "phase": part_phase}[part]()
    print(json.dumps(res, indent=1, default=str))
