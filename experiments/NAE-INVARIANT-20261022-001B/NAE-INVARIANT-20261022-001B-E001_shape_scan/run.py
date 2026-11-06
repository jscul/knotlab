#!/usr/bin/env python3
"""Producer for NAE-INVARIANT-20261022-001B-E001: not-all-equal's critical emergence over torus shapes.

Confirmatory Monte Carlo over the roster frozen in contract.json. sim.c (compiled here with gcc -O2) builds the
literal graph of a fair not-all-equal world on a sheared square-lattice torus (the swap-reversed orientation of the
double cover), finds strongly connected components, and classifies the projected cyclic edges (contractible, cross,
winding class). The same program measures untwisted orientations, plane boxes and arms. This script runs the jobs on
worker threads, aggregates the counts, and evaluates the frozen hypotheses; published and candidate values are read
only in the analysis.

    python3 -B run.py    writes raw_rows.jsonl and result.json under artifacts/
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import resource
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "NAE-INVARIANT-20261022-001B" / HERE.name
WORKERS = min(24, os.cpu_count() or 1)
RADII = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]

ROSTER = {
    "F_sq11": [(33, 33, 0, 400000), (65, 65, 0, 400000), (129, 129, 0, 200000)],
    "F_r53": [(21, 35, 0, 400000), (39, 65, 0, 400000), (75, 125, 0, 400000)],
    "F_r3": [(11, 33, 0, 400000), (21, 63, 0, 400000), (43, 129, 0, 400000)],
    "F_sq10": [(65, 64, 0, 1000000), (65, 66, 0, 1000000), (129, 128, 0, 1000000), (129, 130, 0, 1000000),
               (257, 256, 0, 400000), (257, 258, 0, 400000)],
    "F_r2s": [(33, 66, 0, 400000), (65, 130, 0, 400000), (129, 258, 0, 200000)],
    "F_r2l": [(65, 32, 0, 400000), (129, 64, 0, 400000), (257, 128, 0, 200000)],
    "F_r4s": [(17, 68, 0, 400000), (33, 132, 0, 400000), (65, 260, 0, 400000)],
    "F_r4l": [(65, 16, 0, 400000), (129, 32, 0, 400000), (257, 64, 0, 400000)],
    "F_sh11": [(65, 65, 32, 400000), (129, 129, 64, 400000)],
    "F_sh10": [(65, 65, 33, 400000), (129, 129, 65, 400000)],
    "F_rot21": [(65, 13, 26, 400000), (125, 25, 50, 400000)],
    "F_rot32": [(65, 5, 40, 400000), (117, 9, 72, 400000)],
    "F_cyl65": [(65, 260, 0, 400000), (65, 390, 0, 400000), (65, 520, 0, 400000)],
    "F_cyl33": [(33, 132, 0, 400000), (33, 198, 0, 400000), (33, 264, 0, 400000)],
    "F_small": [(9, 9, 0, 40000), (9, 8, 0, 40000)],
}
MASS = [(65, 65, 0, 40000), (129, 129, 0, 20000), (257, 257, 0, 10000), (513, 513, 0, 5000)]
UNTWISTED = [(128, 128, 0, 200000), (256, 256, 0, 100000), (17, 17, 0, 20000)]
CONTROLS = [(64, 64, 0, 4000), (128, 64, 0, 2000)]
SCAN = ["F_sq11", "F_r53", "F_r3", "F_r2s", "F_r2l", "F_r4s", "F_r4l", "F_sh11", "F_sh10"]
FIT_ROWS = ["F_sq11", "F_r53", "F_r3", "F_r2s", "F_r2l", "F_r4s", "F_r4l", "F_sh11", "F_sh10"]


def seed_of(family: str, label: str, chunk: int) -> int:
    return int(hashlib.sha256(f"{family}|{label}|{chunk}".encode()).hexdigest()[:15], 16)


def chunks(n: int) -> list[int]:
    return [n // WORKERS + (1 if i < n % WORKERS else 0) for i in range(WORKERS)]


def parse_line(out: str) -> dict:
    d = {}
    for tok in out.split()[1:]:
        k, v = tok.split("=")
        d[k] = float(v) if ("e" in v or "." in v) else int(v)
    return d


def run_torus(binary, mode, family, Lh, Lv, s, n, mass=False):
    label = f"{Lh}x{Lv} s={s}"
    jobs = [(k, seed_of(family, label, i)) for i, k in enumerate(chunks(n)) if k]

    def one(job):
        k, seed = job
        args = [binary, mode, str(Lh), str(Lv), str(s), str(k), str(seed)] + (["mass"] if mass else [])
        return parse_line(subprocess.run(args, capture_output=True, text=True, check=True).stdout)

    with ThreadPoolExecutor(WORKERS) as ex:
        parts = list(ex.map(one, jobs))
    tot: dict = {}
    for d in parts:
        for k, v in d.items():
            if k in ("Lh", "Lv", "s"):
                continue
            tot[k] = tot.get(k, 0) + v
    classes = {k[1:]: v for k, v in tot.items() if k.startswith("w") and k[1].isdigit()}
    row = {"family": family, "label": label, "mode": mode, "Lh": Lh, "Lv": Lv, "s": s, "samples": tot["n"],
           "parity": [Lh % 2, (s + Lv) % 2]}
    for key in ("cons", "inc_scc", "inc_topo", "mismatch", "contr", "cross", "wind_odd", "wind_even"):
        row[key] = tot[key]
    row["classes"] = classes
    if mass:
        row.update({"m1": tot["m1"], "m2": tot["m2"], "chi": tot["chi"]})
    if mode == "twisted":
        p = row["cons"] / row["samples"]
        row["E"] = -math.log2(p) if p > 0 else None
        row["se_E"] = math.sqrt((1 - p) / (row["samples"] * p)) / math.log(2) if 0 < p < 1 else 0.0
    return row


def run_arms(binary, L, n):
    jobs = [(k, seed_of("F_arms", str(L), i)) for i, k in enumerate(chunks(n)) if k]

    def one(job):
        k, seed = job
        lines = subprocess.run([binary, "arms", str(L), str(k), str(seed)], capture_output=True, text=True,
                               check=True).stdout.splitlines()[1:]
        hist = {}
        for ln in lines:
            r, *c = map(int, ln.split())
            hist[r] = c
        surv = {}
        for R in RADII:
            surv[R] = [sum(c[j] for r, c in hist.items() if r >= R) for j in range(4)]
        return k, hist, surv

    with ThreadPoolExecutor(WORKERS) as ex:
        parts = list(ex.map(one, jobs))
    per_chunk = [{"samples": k, "survival": {str(R): v for R, v in surv.items()}} for k, _h, surv in parts]
    agg = {}
    for _k, hist, _s in parts:
        for r, c in hist.items():
            a = agg.setdefault(r, [0, 0, 0, 0])
            for j in range(4):
                a[j] += c[j]
    return {"family": "F_arms", "label": f"{L}x{L}", "mode": "arms", "L": L, "samples": n,
            "columns": ["out", "in", "both", "strong_component"], "chunks": per_chunk,
            "histogram": {str(r): agg[r] for r in sorted(agg)}}


def run_box(binary, L, n):
    jobs = [(k, seed_of("F_box", str(L), i)) for i, k in enumerate(chunks(n)) if k]

    def one(job):
        k, seed = job
        return parse_line(subprocess.run([binary, "box", str(L), str(k), str(seed)], capture_output=True, text=True,
                                         check=True).stdout)

    with ThreadPoolExecutor(WORKERS) as ex:
        parts = list(ex.map(one, jobs))
    return {"family": "F_box", "label": f"{L}x{L}", "mode": "box", "L": L, "samples": n,
            "central_edges": sum(p["central_edges"] for p in parts), "central_cyclic": sum(p["central_cyclic"] for p in parts)}


# ------------------------------------------------------------------ Coulomb-gas family (Pinson, Arguin)

def eta_abs2(tR, tI, N=200):
    q = complex(math.cos(2 * math.pi * tR), math.sin(2 * math.pi * tR)) * math.exp(-2 * math.pi * tI)
    prod, qn = 1 + 0j, 1 + 0j
    for _ in range(1, N):
        qn *= q
        prod *= 1 - qn
        if abs(qn) < 1e-18:
            break
    return (math.exp(-2 * math.pi * tI / 24) * abs(prod)) ** 2


def Zmn(m, mp, gs, tR, tI, E):
    return math.sqrt(gs) / (math.sqrt(tI) * E) * math.exp(-math.pi * gs * (m * m * tI * tI + (mp - m * tR) ** 2) / tI)


def classes_list(A=4):
    out = []
    for a in range(0, A + 1):
        for b in range(-A, A + 1):
            if math.gcd(a, b) != 1 or (a == 0 and b != 1):
                continue
            out.append((a, b))
    return out


CLASSES = classes_list()


class Shape:
    def __init__(self, row):
        self.Lh, self.Lv, self.s, self.n = row["Lh"], row["Lv"], row["s"], row["samples"]
        self.tR, self.tI = self.s / self.Lh, self.Lv / self.Lh
        self.E = eta_abs2(self.tR, self.tI)
        self.obs = {"P0": row["contr"] / self.n}
        for c in ((1, 0), (0, 1), (1, 1), (1, -1)):
            self.obs[c] = row["classes"].get(f"{c[0]},{c[1]}", 0) / self.n
        self._zhat = {}

    def parity(self, a, b):
        return (a * self.Lh + b * (self.s + self.Lv)) % 2

    def zhat1(self, gs, M=14):
        key = round(gs, 12)
        if key not in self._zhat:
            tot = 0.0
            for m in range(-M, M + 1):
                for mp in range(-M, M + 1):
                    tot += Zmn(m, mp, gs, self.tR, self.tI, self.E) * math.cos(math.pi * math.gcd(m, mp))
            self._zhat[key] = tot
        return self._zhat[key]

    def model(self, gs, eo, ee, K=12):
        W0 = 0.5 * self.zhat1(gs)
        W = {}
        for (a, b) in CLASSES:
            e = eo if self.parity(a, b) else ee
            tot = 0.0
            for k in range(-K, K + 1):
                if k:
                    tot += Zmn(-k * b, k * a, gs, self.tR, self.tI, self.E) * (math.cos(math.pi * e * k) - math.cos(math.pi * k))
            W[(a, b)] = tot
        T = 2 * W0 + sum(W.values())
        return {"P0": W0 / T, **{c: W[c] / T for c in W}}


def chi2(shapes, x):
    gs, eo, ee = x
    total = 0.0
    for sh in shapes:
        m = sh.model(gs, eo, ee)
        for key in ("P0", (1, 0), (0, 1), (1, 1), (1, -1)):
            p = min(max(m.get(key, 0.0), 0.0), 1.0)
            var = max(p, 1e-5) * (1 - p) / sh.n
            total += (sh.obs[key] - p) ** 2 / max(var, 1e-12)
    return total


def nelder_mead(f, x0, lo, hi, step=0.05, iters=300):
    clip = lambda x: [min(max(v, l), h) for v, l, h in zip(x, lo, hi)]
    pts = [clip(x0)] + [clip([x0[j] + (step if j == i else 0) for j in range(3)]) for i in range(3)]
    vals = [f(p) for p in pts]
    for _ in range(iters):
        order = sorted(range(4), key=lambda i: vals[i])
        pts, vals = [pts[i] for i in order], [vals[i] for i in order]
        cen = [sum(p[j] for p in pts[:3]) / 3 for j in range(3)]
        xr = clip([cen[j] + (cen[j] - pts[3][j]) for j in range(3)]); fr = f(xr)
        if fr < vals[0]:
            xe = clip([cen[j] + 2 * (cen[j] - pts[3][j]) for j in range(3)]); fe = f(xe)
            pts[3], vals[3] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < vals[2]:
            pts[3], vals[3] = xr, fr
        else:
            xc = clip([cen[j] + 0.5 * (pts[3][j] - cen[j]) for j in range(3)]); fc = f(xc)
            if fc < vals[3]:
                pts[3], vals[3] = xc, fc
            else:
                for i in (1, 2, 3):
                    pts[i] = clip([pts[0][j] + 0.5 * (pts[i][j] - pts[0][j]) for j in range(3)])
                    vals[i] = f(pts[i])
    i = min(range(4), key=lambda k: vals[k])
    return pts[i], vals[i]


def fit_family(rows):
    shapes = []
    for fam in FIT_ROWS:
        fr = [r for r in rows if r["family"] == fam]
        shapes.append(Shape(max(fr, key=lambda r: r["Lh"] * r["Lv"])))
    for r in [r for r in rows if r["family"] == "F_sq10" and r["Lh"] == 257]:
        shapes.append(Shape(r))
    grid = []
    for gi in range(11):
        gs = 0.5 + 0.05 * gi
        for oi in range(11):
            for ei in range(11):
                x = (gs, 0.1 * oi, 0.1 * ei)
                grid.append((chi2(shapes, x), x))
    grid.sort()
    best_x, best = list(grid[0][1]), grid[0][0]
    for _c, x0 in grid[:3]:
        x, v = nelder_mead(lambda z: chi2(shapes, z), list(x0), [0.5, 0.0, 0.0], [1.0, 1.0, 1.0])
        if v < best:
            best_x, best = x, v
    dof = 5 * len(shapes) - 3
    return {"best_fit": {"gs": best_x[0], "e_odd": best_x[1], "e_even": best_x[2]}, "chi2": best, "dof": dof,
            "chi2_per_dof": best / dof, "grid_best_chi2": grid[0][0], "shapes": [f"{s.Lh}x{s.Lv} s={s.s}" for s in shapes]}


# ------------------------------------------------------------------ analysis

def wls_line(xs, ys, ses):
    w = [1 / s ** 2 for s in ses]
    S, Sx, Sy = sum(w), sum(wi * x for wi, x in zip(w, xs)), sum(wi * y for wi, y in zip(w, ys))
    Sxx, Sxy = sum(wi * x * x for wi, x in zip(w, xs)), sum(wi * x * y for wi, x, y in zip(w, xs, ys))
    D = S * Sxx - Sx * Sx
    slope, icpt = (S * Sxy - Sx * Sy) / D, (Sxx * Sy - Sx * Sxy) / D
    return icpt, slope, math.sqrt(Sxx / D), math.sqrt(S / D)


def analyse(rows, contract):
    pred = contract["predictions"]
    ngz = pred["ngz_values"]
    by = {}
    for r in rows:
        by.setdefault(r["family"], []).append(r)
    out = {}
    # H_shape
    shape = {}
    for fam in SCAN:
        fr = sorted(by[fam], key=lambda r: r["Lh"] * r["Lv"])
        a, b = fr[-2], fr[-1]
        d = b["E"] - a["E"]
        sd = math.sqrt(a["se_E"] ** 2 + b["se_E"] ** 2)
        shape[fam] = {"E": [round(r["E"], 5) for r in fr], "se": [round(r["se_E"], 5) for r in fr],
                      "last_step": round(d, 5), "sigma": round(sd, 5), "ok": abs(d) <= 3 * sd + 0.02}
    pairs = {}
    for L in (65, 129, 257):
        two = [r for r in by["F_sq10"] if r["Lh"] == L]
        pairs[L] = (sum(r["E"] for r in two) / 2, 0.5 * math.sqrt(sum(r["se_E"] ** 2 for r in two)))
    d = pairs[257][0] - pairs[129][0]
    sd = math.sqrt(pairs[257][1] ** 2 + pairs[129][1] ** 2)
    shape["F_sq10_pairs"] = {"E": [round(pairs[L][0], 5) for L in (65, 129, 257)], "se": [round(pairs[L][1], 5) for L in (65, 129, 257)],
                             "last_step": round(d, 5), "sigma": round(sd, 5), "ok": abs(d) <= 3 * sd + 0.02}
    out["H_shape"] = {"families": shape, "holds": all(v["ok"] for v in shape.values()),
                      "max_drift_sigma_plus": max(abs(v["last_step"]) - 5 * v["sigma"] for v in shape.values())}
    # H_rotation
    sq = max(by["F_sq11"], key=lambda r: r["Lh"])
    rot = {}
    for fam in ("F_rot21", "F_rot32"):
        fr = by[fam]
        w = [1 / r["se_E"] ** 2 for r in fr]
        m = sum(wi * r["E"] for wi, r in zip(w, fr)) / sum(w)
        se = math.sqrt(1 / sum(w))
        dd = m - sq["E"]
        rot[fam] = {"mean": round(m, 5), "se": round(se, 5), "square": round(sq["E"], 5), "diff": round(dd, 5),
                    "ok": abs(dd) <= 3 * math.sqrt(se ** 2 + sq["se_E"] ** 2) + 0.02}
    out["H_rotation"] = {"rotations": rot, "holds": all(v["ok"] for v in rot.values())}
    # H_family
    fam = fit_family(rows)
    fam["holds"] = fam["chi2_per_dof"] >= 10
    fam["fits"] = fam["chi2_per_dof"] < 3
    out["H_family"] = fam
    # H_class
    mass = sorted(by["F_mass"], key=lambda r: r["Lh"])
    M = [(r["Lh"], r["m1"] / r["samples"], math.sqrt(max(r["m2"] / r["samples"] - (r["m1"] / r["samples"]) ** 2, 0) / r["samples"])) for r in mass]
    slopes = []
    for (L1, M1, s1), (L2, M2, s2) in zip(M, M[1:]):
        slopes.append({"sides": [L1, L2], "d_f": math.log(M2 / M1) / math.log(L2 / L1),
                       "sigma": math.sqrt((s1 / M1) ** 2 + (s2 / M2) ** 2) / math.log(L2 / L1)})
    last = slopes[-1]
    a_ok = abs(last["d_f"] - ngz["fractal_dimension"]) <= 3 * last["sigma"] + 0.02
    u = next(r for r in by["F_untwisted"] if r["Lh"] == 256)
    n = u["samples"]
    cl = {tuple(map(int, k.split(","))): v for k, v in u["classes"].items()}
    either = 1 - u["contr"] / n
    horiz = (u["cross"] + sum(v for (a, b), v in cl.items() if a != 0)) / n
    vert = (u["cross"] + sum(v for (a, b), v in cl.items() if b != 0)) / n
    one = (horiz + vert) / 2
    both = (u["cross"] + sum(v for (a, b), v in cl.items() if a != 0 and b != 0)) / n
    wrap = {}
    for name, val, ref in (("either", either, ngz["wrap_either"]), ("one_direction", one, ngz["wrap_one_direction"]),
                           ("both", both, ngz["wrap_both"])):
        sig = math.sqrt(val * (1 - val) / n)
        wrap[name] = {"value": round(val, 5), "sigma": round(sig, 5), "published": ref,
                      "ok": abs(val - ref) <= 3 * sig + 0.01, "gross": abs(val - ref) > 0.03}
    arms = by["F_arms"][0]
    Rfit = [16, 32, 64, 128, 256, 512]

    def exponent(chunk_list, col):
        tot = sum(c["samples"] for c in chunk_list)
        ys = [math.log(sum(c["survival"][str(R)][col] for c in chunk_list) / tot) for R in Rfit]
        xs = [math.log(R) for R in Rfit]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        return -sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)

    exps = {}
    for col, name in enumerate(arms["columns"]):
        full = exponent(arms["chunks"], col)
        jack = [exponent(arms["chunks"][:i] + arms["chunks"][i + 1:], col) for i in range(len(arms["chunks"]))]
        k = len(jack)
        mj = sum(jack) / k
        se = math.sqrt((k - 1) / k * sum((j - mj) ** 2 for j in jack))
        exps[name] = {"exponent": round(full, 5), "sigma": round(se, 5)}
    xb, sb = exps["both"]["exponent"], exps["both"]["sigma"]
    c_ok = abs(xb - 5 / 24) > 3 * sb
    box = by["F_box"][0]
    dens = box["central_cyclic"] / box["central_edges"]
    d_ok = abs(dens - 0.5) <= 0.005
    out["H_class"] = {"mass_slopes": [{"sides": s["sides"], "d_f": round(s["d_f"], 5), "sigma": round(s["sigma"], 5)} for s in slopes],
                      "a_dimension_ok": a_ok, "untwisted_wrapping": wrap,
                      "b_wrapping_ok": all(v["ok"] for v in wrap.values()), "arm_exponents": exps,
                      "c_not_independent": c_ok, "central_cyclic_fraction": round(dens, 5), "d_density_ok": d_ok}
    out["H_class"]["holds"] = a_ok and out["H_class"]["b_wrapping_ok"] and c_ok and d_ok
    # candidates
    xs = [1 / L for L in (65, 129, 257)]
    ys = [pairs[L][0] for L in (65, 129, 257)]
    ses = [pairs[L][1] for L in (65, 129, 257)]
    icpt, slope, s_icpt, _s = wls_line(xs, ys, ses)
    half = {"E_inf": round(icpt, 5), "sigma": round(s_icpt, 5), "slope_1_over_L": round(slope, 4),
            "accepted": abs(icpt - 0.5) <= 3 * s_icpt}
    cyl = sorted(by["F_cyl65"], key=lambda r: r["Lv"])
    ks = [r["Lv"] / r["Lh"] for r in cyl]
    icpt2, s2, _si, s2_se = wls_line(ks, [r["E"] for r in cyl], [r["se_E"] for r in cyl])
    x = s2 * math.log(2) / (2 * math.pi)
    xs_ = s2_se * math.log(2) / (2 * math.pi)
    six = {"slope_bits_per_aspect": round(s2, 5), "slope_sigma": round(s2_se, 5), "x": round(x, 5), "x_sigma": round(xs_, 5),
           "accepted": abs(x - 1 / 16) <= 3 * xs_ + 0.001}
    cyl33 = sorted(by["F_cyl33"], key=lambda r: r["Lv"])
    _i3, s3, _a, s3_se = wls_line([r["Lv"] / r["Lh"] for r in cyl33], [r["E"] for r in cyl33], [r["se_E"] for r in cyl33])
    six["slope_circumference_33"] = round(s3, 5)
    six["slope_circumference_33_sigma"] = round(s3_se, 5)
    arms_eq = {"exponent_both": xb, "sigma": sb, "beta_over_nu": ngz["beta_over_nu"],
               "accepted": abs(xb - ngz["beta_over_nu"]) <= 3 * sb + 0.005}
    out["candidates"] = {"half_bit": half, "sixteenth": six, "arms_equal_cluster": arms_eq}
    return out


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    assert contract["status"] == "Frozen" and contract["evidence_stage"] == "confirmatory"
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.time()
    build = Path(tempfile.mkdtemp(prefix="nae-sim-"))
    binary = str(build / "sim")
    subprocess.run(["gcc", "-O2", "-o", binary, str(HERE / "sim.c")], check=True)
    gcc = subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    rows, failures = [], []
    try:
        for (Lh, Lv, s, n) in CONTROLS:
            r = run_torus(binary, "twisted", "control_bipartite", Lh, Lv, s, n)
            rows.append(r)
            if r["cons"] != r["samples"]:
                failures.append(f"bipartite control {r['label']} inconsistent")
        if not failures:
            for fam, roster in ROSTER.items():
                for (Lh, Lv, s, n) in roster:
                    rows.append(run_torus(binary, "twisted", fam, Lh, Lv, s, n))
                    print(fam, rows[-1]["label"], round(rows[-1]["E"], 5), flush=True)
            for (Lh, Lv, s, n) in MASS:
                rows.append(run_torus(binary, "twisted", "F_mass", Lh, Lv, s, n, mass=True))
            for (Lh, Lv, s, n) in UNTWISTED:
                rows.append(run_torus(binary, "untwisted", "F_untwisted", Lh, Lv, s, n))
            rows.append(run_arms(binary, 2049, 240000))
            rows.append(run_box(binary, 512, 1000))
            for r in rows:
                if r.get("mode") == "twisted" and r["family"] != "control_bipartite":
                    if r["mismatch"]:
                        failures.append(f"test disagreement {r['family']} {r['label']}")
                    if abs(r["contr"] - r["cross"]) > 4 * math.sqrt(r["contr"] + r["cross"]):
                        failures.append(f"duality {r['family']} {r['label']}")
    finally:
        shutil.rmtree(build, ignore_errors=True)
    with open(OUT / "raw_rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    result = {"schema_version": 1, "experiment_id": contract["experiment_id"], "ticket": contract["ticket"],
              "evidence_stage": contract["evidence_stage"], "controls_ok": not failures, "control_failures": failures,
              "rows": len(rows), "compiler": gcc, "workers": WORKERS}
    if failures:
        result["verdict"] = "invalid"
    else:
        a = analyse(rows, contract)
        result.update(a)
        fam, cls, shp = a["H_family"], a["H_class"], a["H_shape"]
        primary = {"H_shape": shp["holds"], "H_rotation": a["H_rotation"]["holds"], "H_family": fam["holds"],
                   "H_class": cls["holds"]}
        refuted = (fam["fits"] or abs(cls["mass_slopes"][-1]["d_f"] - contract["predictions"]["ngz_values"]["fractal_dimension"]) > 0.05
                   or any(v["gross"] for v in cls["untwisted_wrapping"].values()) or shp["max_drift_sigma_plus"] > 0.05)
        result["primary"] = primary
        result["verdict"] = "supported" if all(primary.values()) else ("refuted" if refuted else "closed-null")
    result["wall_seconds"] = round(time.time() - started, 1)
    result["max_rss_mib"] = round(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024, 1)
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("controls_ok", "verdict", "wall_seconds") if k in result}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
