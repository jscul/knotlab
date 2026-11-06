#!/usr/bin/env python3
"""Producer for SC-TORUS-EXACT-20261022-001B-E001: precision tests of the exact-looking torus values.

Confirmatory Monte Carlo over the roster frozen in contract.json. simx.c (compiled here with gcc -O2) samples uniform random
orientations of square-lattice tori, imposes a twist on the double cover where asked, finds strongly connected components and
classifies the projected cyclic edges; it also runs the four twist sectors on common random numbers and tests directed
winding. This script runs the jobs on worker threads, aggregates the counts, and evaluates the frozen rules; candidate and
published values are read only in the analysis.

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
OUT = ROOT / "artifacts" / "SC-TORUS-EXACT-20261022-001B" / HERE.name
WORKERS = min(24, os.cpu_count() or 1)

SECTORS = {
    "F_small": [(16, 16, 0, 1, 0, 20000), (16, 16, 0, 0, 0, 20000)],
    "F_half": [(64, 64, 0, 1, 0, 7000000), (128, 128, 0, 1, 0, 7000000), (256, 256, 0, 1, 0, 3200000), (512, 512, 0, 1, 0, 1100000)],
    "F_34": [(64, 64, 0, 0, 0, 6000000), (128, 128, 0, 0, 0, 6000000), (256, 256, 0, 0, 0, 3300000), (512, 512, 0, 0, 0, 1400000)],
    "F_long": [(128, 64, 0, 1, 0, 1000000), (192, 64, 0, 1, 0, 1500000), (256, 64, 0, 1, 0, 3000000)],
    "F_short": [(64, 128, 0, 1, 0, 400000), (64, 192, 0, 1, 0, 400000), (64, 256, 0, 1, 0, 400000)],
    "F_scan": [(256, 256, 0, 1, 1, 400000), (128, 128, 64, 1, 0, 400000), (128, 128, 64, 0, 1, 400000), (128, 128, 64, 1, 1, 400000),
               (256, 128, 0, 1, 0, 400000), (128, 256, 0, 1, 0, 400000), (256, 128, 0, 1, 1, 400000)],
}
CRN = [(64, 64, 0, 2200000), (128, 128, 0, 2200000), (256, 256, 0, 800000), (128, 64, 0, 1000000)]
DIR = [(16, 20000), (64, 400000), (128, 200000)]


def seed_of(family, label, chunk):
    return int(hashlib.sha256(f"{family}|{label}|{chunk}".encode()).hexdigest()[:15], 16)


def chunks(n):
    return [n // WORKERS + (1 if i < n % WORKERS else 0) for i in range(WORKERS)]


def parse(out):
    return {k: float(v) if ("." in v or "e" in v) else int(v) for k, v in (t.split("=") for t in out.split()[1:])}


def run_jobs(binary, args_of, family, label, n):
    jobs = [(k, seed_of(family, label, i)) for i, k in enumerate(chunks(n)) if k]

    def one(job):
        k, seed = job
        return parse(subprocess.run([binary] + args_of(k, seed), capture_output=True, text=True, check=True).stdout)

    with ThreadPoolExecutor(WORKERS) as ex:
        parts = list(ex.map(one, jobs))
    tot = {}
    for d in parts:
        for k, v in d.items():
            tot[k] = tot.get(k, 0) + v
    return tot


def sector_row(binary, family, Lh, Lv, s, px, py, n):
    label = f"{Lh}x{Lv} s={s} p=({px},{py})"
    t = run_jobs(binary, lambda k, seed: ["sector", str(Lh), str(Lv), str(s), str(px), str(py), str(k), str(seed)], family, label, n)
    classes = {k[1:]: v for k, v in t.items() if k.startswith("w") and k[1].isdigit()}
    row = {"family": family, "label": label, "mode": "sector", "Lh": Lh, "Lv": Lv, "s": s, "px": px, "py": py, "samples": t["n"]}
    for k in ("contr", "cross", "wind_odd", "wind_even", "hwrap", "vwrap", "hvwrap", "cons", "invariant", "mismatch"):
        row[k] = t[k]
    row["classes"] = classes
    return row


def crn_row(binary, Lh, Lv, s, n):
    label = f"{Lh}x{Lv} s={s}"
    t = run_jobs(binary, lambda k, seed: ["crn", str(Lh), str(Lv), str(s), str(k), str(seed)], "F_add", label, n)
    row = {"family": "F_add", "label": label, "mode": "crn", "Lh": Lh, "Lv": Lv, "s": s, "samples": t["n"]}
    for k in ("c00", "c10", "c01", "c11", "x00", "x10", "x01", "x11", "dsum", "dsq", "ssum", "ssq"):
        row[k] = t[k]
    return row


def dir_row(binary, L, n):
    t = run_jobs(binary, lambda k, seed: ["dir", str(L), str(k), str(seed)], "F_dir", str(L), n)
    return {"family": "F_dir", "label": f"{L}x{L}", "mode": "dir", "L": L, "samples": t["n"],
            "states": [t[f"s{i}"] for i in range(16)]}


# ------------------------------------------------------------------ analysis

def sym_consistent(r):
    """P(consistent) = 1/2 + (P(even) - P(odd))/2 and its standard error."""
    n = r["samples"]
    pe, po = r["wind_even"] / n, r["wind_odd"] / n
    mean = 0.5 + 0.5 * (pe - po)
    second = pe + 0.25 * (1 - pe - po)
    return mean, math.sqrt(max(second - mean * mean, 0) / n)


def sym_wrap(r):
    """Untwisted one-direction wrapping (P(H) + P(V))/2 and its standard error."""
    n = r["samples"]
    ph, pv, phv = r["hwrap"] / n, r["vwrap"] / n, r["hvwrap"] / n
    mean = 0.5 * (ph + pv)
    second = 0.25 * (ph + pv + 2 * phv)
    return mean, math.sqrt(max(second - mean * mean, 0) / n)


def wls(xs, ys, ses):
    w = [1 / s ** 2 for s in ses]
    S = sum(w); Sx = sum(a * b for a, b in zip(w, xs)); Sy = sum(a * b for a, b in zip(w, ys))
    Sxx = sum(a * b * b for a, b in zip(w, xs)); Sxy = sum(a * b * c for a, b, c in zip(w, xs, ys))
    D = S * Sxx - Sx * Sx
    icpt, slope = (Sxx * Sy - Sx * Sxy) / D, (S * Sxy - Sx * Sy) / D
    chi2 = sum(wi * (y - icpt - slope * x) ** 2 for wi, x, y in zip(w, xs, ys))
    return icpt, slope, math.sqrt(Sxx / D), math.sqrt(S / D), chi2


def wls_quad(xs, ys, ses):
    """E = a + b x + c x^2 by weighted least squares (normal equations); returns a and its standard error."""
    w = [1 / s ** 2 for s in ses]
    M = [[sum(wi * x ** (i + j) for wi, x in zip(w, xs)) for j in range(3)] for i in range(3)]
    v = [sum(wi * y * x ** i for wi, x, y in zip(w, xs, ys)) for i in range(3)]
    # invert 3x3
    a, b, c = M[0]; d, e, f = M[1]; g, h, k = M[2]
    det = a * (e * k - f * h) - b * (d * k - f * g) + c * (d * h - e * g)
    inv = [[(e * k - f * h) / det, (c * h - b * k) / det, (b * f - c * e) / det],
           [(f * g - d * k) / det, (a * k - c * g) / det, (c * d - a * f) / det],
           [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det]]
    coef = [sum(inv[i][j] * v[j] for j in range(3)) for i in range(3)]
    return coef[0], math.sqrt(inv[0][0])


def analyse(rows, contract):
    out, by = {}, {}
    for r in rows:
        by.setdefault(r["family"], []).append(r)
    # half bit
    half = sorted(by["F_half"], key=lambda r: r["Lh"])
    pts = []
    for r in half:
        p, sp = sym_consistent(r)
        raw = (r["contr"] + r["wind_even"]) / r["samples"]
        pts.append({"L": r["Lh"], "P": p, "sigma_P": sp, "P_raw": raw, "E": -math.log2(p), "sigma_E": sp / (p * math.log(2))})
    E_inf, cE, sE, _sc, chiE = wls([1 / q["L"] for q in pts], [q["E"] for q in pts], [q["sigma_E"] for q in pts])
    E_inf2, sE2 = wls_quad([1 / q["L"] for q in pts], [q["E"] for q in pts], [q["sigma_E"] for q in pts])
    out["half_bit"] = {"points": pts, "E_inf": E_inf, "sigma": sE, "slope": cE, "chi2": chiE, "E_inf_quadratic": E_inf2,
                       "sigma_quadratic": sE2, "deviation_sigmas": (E_inf - 0.5) / sE,
                       "accepted": abs(E_inf - 0.5) <= 3 * sE, "decisively_rejected": abs(E_inf - 0.5) > 5 * sE}
    # three quarters
    w34 = sorted(by["F_34"], key=lambda r: r["Lh"])
    pts = []
    for r in w34:
        m, s = sym_wrap(r)
        pts.append({"L": r["Lh"], "W": m, "sigma": s, "W_raw_h": r["hwrap"] / r["samples"]})
    W_inf, cW, sW, _s, chiW = wls([1 / q["L"] for q in pts], [q["W"] for q in pts], [q["sigma"] for q in pts])
    W_inf2, sW2 = wls_quad([1 / q["L"] for q in pts], [q["W"] for q in pts], [q["sigma"] for q in pts])
    out["three_quarters"] = {"points": pts, "W_inf": W_inf, "sigma": sW, "slope": cW, "chi2": chiW, "W_inf_quadratic": W_inf2,
                             "sigma_quadratic": sW2, "deviation_sigmas": (W_inf - 0.75) / sW,
                             "accepted": abs(W_inf - 0.75) <= 3 * sW, "decisively_rejected": abs(W_inf - 0.75) > 5 * sW,
                             "published": 0.75001}
    # additivity
    adds = by["F_add"]
    pts = []
    for r in adds:
        n = r["samples"]
        D = r["ssum"] / n
        sD = math.sqrt(max(r["ssq"] / n - D * D, 0) / n)
        Dr = r["dsum"] / n
        sDr = math.sqrt(max(r["dsq"] / n - Dr * Dr, 0) / n)
        pts.append({"label": r["label"], "Lh": r["Lh"], "Lv": r["Lv"], "D": D, "sigma": sD, "D_raw": Dr, "sigma_raw": sDr,
                    "P00": r["c00"] / n, "P10": (r["c10"] + r["x10"]) / (2 * n), "P01": (r["c01"] + r["x01"]) / (2 * n),
                    "P11": (r["c11"] + r["x11"]) / (2 * n)})
    sq = sorted([q for q in pts if q["Lh"] == q["Lv"]], key=lambda q: q["Lh"])
    D_inf, cD, sDi, _s, chiD = wls([1 / q["Lh"] for q in sq], [q["D"] for q in sq], [q["sigma"] for q in sq])
    rect = next(q for q in pts if q["Lh"] != q["Lv"])
    out["additivity"] = {"points": pts, "D_inf": D_inf, "sigma": sDi, "slope": cD, "chi2": chiD,
                         "rectangle": {"D": rect["D"], "sigma": rect["sigma"]},
                         "accepted": abs(D_inf) <= 3 * sDi and abs(rect["D"]) <= 3 * rect["sigma"]}
    # beta/nu from the long side
    lg = sorted(by["F_long"], key=lambda r: r["Lh"])
    ks, ys, ses = [], [], []
    for r in lg:
        p, sp = sym_consistent(r)
        q = 1 - p
        ks.append(r["Lh"] / r["Lv"]); ys.append(math.log(q)); ses.append(sp / q)
    a, sl, _sa, ssl, chiL = wls(ks, ys, ses)
    x = -sl / (2 * math.pi); sx = ssl / (2 * math.pi)
    out["beta_nu"] = {"aspects": ks, "log_inconsistent": ys, "x": x, "sigma": sx, "chi2": chiL, "beta_over_nu": 0.19635,
                      "accepted": abs(x - 0.19635) <= 3 * sx + 0.005}
    sh = sorted(by["F_short"], key=lambda r: r["Lv"])
    ks, ys, ses = [], [], []
    for r in sh:
        p, sp = sym_consistent(r)
        ks.append(r["Lv"] / r["Lh"]); ys.append(math.log(p)); ses.append(sp / p)
    a2, sl2, _s2, ssl2, chiS = wls(ks, ys, ses)
    out["short_side_exponent"] = {"aspects": ks, "x": -sl2 / (2 * math.pi), "sigma": ssl2 / (2 * math.pi), "chi2": chiS}
    # directed winding law
    dirs = {}
    for r in by["F_dir"]:
        n = r["samples"]; s = [c / n for c in r["states"]]
        P = lambda f: sum(s[i] for i in range(16) if f(i & 1, (i >> 1) & 1, (i >> 2) & 1, (i >> 3) & 1))
        dirs[r["label"]] = {"samples": n, "H+ only": P(lambda hp, hm, vp, vm: hp and not hm),
                            "H- only": P(lambda hp, hm, vp, vm: hm and not hp), "both": P(lambda hp, hm, vp, vm: hp and hm),
                            "neither": P(lambda hp, hm, vp, vm: not hp and not hm),
                            "no winding at all": P(lambda hp, hm, vp, vm: not (hp or hm or vp or vm)),
                            "all four": P(lambda hp, hm, vp, vm: hp and hm and vp and vm)}
    out["directed_law"] = dirs
    # scan
    scan = []
    for r in by["F_scan"] + by["F_small"]:
        n = r["samples"]
        p, sp = sym_consistent(r) if (r["px"] or r["py"]) else (None, None)
        notH = (n - r["hwrap"]) / n
        scan.append({"label": r["label"], "family": r["family"], "P_consistent": p, "sigma": sp,
                     "E": -math.log2(p) if p else None, "P_contractible": (r["contr"] + r["cross"]) / (2 * n) if (r["px"] or r["py"]) else r["contr"] / n,
                     "P_no_horizontal": notH, "P_no_vertical": (n - r["vwrap"]) / n})
    out["scan"] = scan
    return out


def controls(rows):
    fails = []
    for r in rows:
        if r["mode"] != "sector" or not (r["px"] or r["py"]):
            continue
        if r["mismatch"]:
            fails.append(f"test disagreement {r['label']}")
        if abs(r["contr"] - r["cross"]) > 4 * math.sqrt(r["contr"] + r["cross"]):
            fails.append(f"duality {r['family']} {r['label']}")
    und = {r["Lh"]: r for r in rows if r["family"] == "F_34"}
    for r in rows:
        if r["mode"] == "dir" and r["L"] in und:
            n = r["samples"]; s = r["states"]
            neither = sum(s[i] for i in range(16) if not (i & 1) and not ((i >> 1) & 1)) / n
            u = und[r["L"]]; m = u["samples"]
            notH = 1 - u["hwrap"] / m
            sig = math.sqrt(neither * (1 - neither) / n + notH * (1 - notH) / m)
            if abs(neither - notH) > 4 * sig:
                fails.append(f"directed vs undirected at L={r['L']}: {neither:.5f} vs {notH:.5f}")
    return fails


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    assert contract["status"] == "Frozen" and contract["evidence_stage"] == "confirmatory"
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.time()
    build = Path(tempfile.mkdtemp(prefix="simx-"))
    binary = str(build / "simx")
    subprocess.run(["gcc", "-O2", "-o", binary, str(HERE / "simx.c")], check=True)
    gcc = subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    rows = []
    try:
        for fam in ("F_small", "F_half", "F_34", "F_long", "F_short", "F_scan"):
            for (Lh, Lv, s, px, py, n) in SECTORS[fam]:
                rows.append(sector_row(binary, fam, Lh, Lv, s, px, py, n))
                print(fam, rows[-1]["label"], rows[-1]["samples"], flush=True)
        for (Lh, Lv, s, n) in CRN:
            rows.append(crn_row(binary, Lh, Lv, s, n))
            print("F_add", rows[-1]["label"], flush=True)
        for (L, n) in DIR:
            rows.append(dir_row(binary, L, n))
            print("F_dir", L, flush=True)
    finally:
        shutil.rmtree(build, ignore_errors=True)
    with open(OUT / "raw_rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    fails = controls(rows)
    result = {"schema_version": 1, "experiment_id": contract["experiment_id"], "ticket": contract["ticket"],
              "evidence_stage": contract["evidence_stage"], "controls_ok": not fails, "control_failures": fails,
              "rows": len(rows), "compiler": gcc, "workers": WORKERS}
    if fails:
        result["verdict"] = "invalid"
    else:
        a = analyse(rows, contract)
        result.update(a)
        h, t = a["half_bit"], a["three_quarters"]
        result["primary"] = {"half_bit_accepted": h["accepted"], "three_quarters_accepted": t["accepted"]}
        result["secondary"] = {"additivity_accepted": a["additivity"]["accepted"], "beta_nu_accepted": a["beta_nu"]["accepted"]}
        if h["accepted"] and t["accepted"]:
            result["verdict"] = "supported"
        elif h["decisively_rejected"] or t["decisively_rejected"]:
            result["verdict"] = "refuted"
        else:
            result["verdict"] = "closed-null"
    result["wall_seconds"] = round(time.time() - started, 1)
    result["max_rss_mib"] = round(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024, 1)
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("controls_ok", "verdict", "wall_seconds") if k in result}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
