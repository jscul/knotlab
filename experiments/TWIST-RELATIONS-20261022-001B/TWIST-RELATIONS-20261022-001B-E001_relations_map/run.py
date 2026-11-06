#!/usr/bin/env python3
"""Producer for TWIST-RELATIONS-20261022-001B-E001: the twist relations across shapes.

Confirmatory Monte Carlo over the roster frozen in contract.json. simt.c (compiled here with gcc -O2) classifies every sampled
orientation in all four twist sectors on common random numbers and reports the joint type pattern. This script runs the jobs on
worker threads, appends each finished row to raw_rows.jsonl, and evaluates the frozen rules into result.json; candidate values
enter only the analysis.

    python3 -B run.py    writes raw_rows.jsonl (row by row) and result.json under artifacts/
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
OUT = ROOT / "artifacts" / "TWIST-RELATIONS-20261022-001B" / HERE.name
WORKERS = min(24, os.cpu_count() or 1)
SECTORS = ((0, 0), (1, 0), (0, 1), (1, 1))

ROSTER = {
    "F_exact": [(3, 3, 0, 2000000), (3, 3, 1, 2000000)],
    "F_odd": [(7, 5, 0, 30000000), (8, 8, 0, 30000000), (10, 6, 0, 30000000), (12, 8, 3, 30000000), (9, 7, 2, 30000000),
              (12, 12, 0, 20000000), (16, 10, 5, 20000000), (24, 24, 0, 4000000)],
    "F_shear": [(12, 8, 0, 30000000), (12, 8, 2, 30000000), (12, 8, 4, 30000000), (12, 8, 6, 30000000)],
    "F_rect": [(48, 32, 0, 1200000), (96, 64, 0, 600000), (64, 32, 0, 1200000), (128, 64, 0, 600000), (96, 32, 0, 1200000),
               (192, 64, 0, 600000)],
    "F_conf": [(64, 32, 32, 1200000), (128, 64, 64, 600000)],
    "F_harm": [(64, 64, 0, 600000), (64, 64, 8, 600000), (64, 64, 16, 600000), (64, 64, 24, 600000), (64, 64, 32, 600000),
               (128, 64, 0, 300000), (128, 64, 16, 300000), (128, 64, 32, 300000), (128, 64, 48, 300000), (128, 64, 64, 300000)],
}


def seed_of(family, label, chunk):
    return int(hashlib.sha256(f"{family}|{label}|{chunk}".encode()).hexdigest()[:15], 16)


def chunks(n):
    return [n // WORKERS + (1 if i < n % WORKERS else 0) for i in range(WORKERS)]


def parse(out):
    return {k: int(v) for k, v in (t.split("=") for t in out.split()[1:])}


def run_row(binary, family, Lh, Lv, s, n):
    label = f"{Lh}x{Lv} s={s}"
    jobs = [(k, seed_of(family, label, i)) for i, k in enumerate(chunks(n)) if k]

    def one(job):
        k, seed = job
        return parse(subprocess.run([binary, "joint", str(Lh), str(Lv), str(s), str(k), str(seed)],
                                    capture_output=True, text=True, check=True).stdout)

    with ThreadPoolExecutor(WORKERS) as ex:
        parts = list(ex.map(one, jobs))
    tot = {}
    for d in parts:
        for k, v in d.items():
            tot[k] = tot.get(k, 0) + v
    row = {"family": family, "label": label, "Lh": Lh, "Lv": Lv, "s": s, "samples": tot["n"]}
    for q in range(4):
        for key in ("c", "x", "inv", "mis"):
            row[f"{key}{q}"] = tot[f"{key}{q}"]
        row[f"classes{q}"] = {k.split(":")[1]: v for k, v in tot.items() if k.startswith(f"w{q}:")}
    row["joint_types"] = {k[2:]: v for k, v in tot.items() if k.startswith("jt")}
    return row


# ------------------------------------------------------------------ analysis

def types(index):
    return [(index // 5 ** q) % 5 for q in range(4)]


def moments(row, f):
    """Mean and standard error of a per-sample statistic f(types) over the joint type pattern."""
    n = row["samples"]
    s1 = s2 = 0.0
    for k, v in row["joint_types"].items():
        x = f(types(int(k)))
        s1 += x * v
        s2 += x * x * v
    m = s1 / n
    return m, math.sqrt(max(s2 / n - m * m, 0.0) / n)


def contr(t, q):
    return 1 if t[q] == 0 else 0


def odd_line(t, q):
    """Winding odd under the twist of sector q (types 2/3/4 are classes = (1,0)/(0,1)/(1,1) mod 2)."""
    return 1 if (q == 1 and t[1] in (2, 4)) or (q == 2 and t[2] in (3, 4)) or (q == 3 and t[3] in (2, 3)) else 0


def analyse(rows):
    by = {}
    for r in rows:
        by.setdefault(r["family"], []).append(r)
    out = {}
    # primary: the odd-line identity, per torus and per type
    stats = []
    for r in by["F_odd"]:
        rec = {"label": r["label"], "samples": r["samples"]}
        for name, f in (("(1,0): sector 10 - sector 11", lambda t: (t[1] == 2) - (t[3] == 2)),
                        ("(0,1): sector 01 - sector 11", lambda t: (t[2] == 3) - (t[3] == 3)),
                        ("(1,1): sector 10 - sector 01", lambda t: (t[1] == 4) - (t[2] == 4))):
            m, se = moments(r, f)
            rec[name] = {"difference": m, "sigma": se, "z": m / se if se else 0.0}
        rec["P_line_10_(1,0)"] = r["classes1"].get("1,0", 0) / r["samples"]
        rec["P_line_11_(1,0)"] = r["classes3"].get("1,0", 0) / r["samples"]
        stats.append(rec)
    zs = [abs(v["z"]) for rec in stats for k, v in rec.items() if isinstance(v, dict)]
    out["odd_line"] = {"tori": stats, "max_abs_z": max(zs), "accepted": all(z <= 4 for z in zs),
                       "decisively_rejected": any(z > 6 for z in zs)}
    # shear independence of the odd horizontal line (class (1,0)) in the sector odd on w1 and even on w2
    sh = sorted(by["F_shear"], key=lambda r: r["s"])
    base = sh[0]
    pb = base["classes1"].get("1,0", 0) / base["samples"]
    comps = []
    for r in sh[1:]:
        p = r["classes1"].get("1,0", 0) / r["samples"]
        se = math.sqrt(p * (1 - p) / r["samples"] + pb * (1 - pb) / base["samples"])
        comps.append({"s": r["s"], "P_line": p, "P_line_s0": pb, "z": (p - pb) / se})
    out["shear_independence"] = {"comparisons": comps, "accepted": all(abs(c["z"]) <= 4 for c in comps),
                                 "decisively_rejected": any(abs(c["z"]) > 6 for c in comps)}
    # secondary: rectangle additivity, extrapolated from two sizes per aspect (D_inf = 2 D(large) - D(small))
    rect = {}
    for r in by["F_rect"]:
        D, se = moments(r, lambda t: contr(t, 0) - contr(t, 1) - contr(t, 2) + contr(t, 3))
        rect.setdefault(r["Lh"] / r["Lv"], []).append((r["Lv"], D, se, r["label"]))
    rows_out, ok = [], True
    for aspect, pts in sorted(rect.items()):
        (l1, d1, s1, lab1), (l2, d2, s2, lab2) = sorted(pts)
        dinf, sinf = 2 * d2 - d1, math.sqrt(4 * s2 ** 2 + s1 ** 2)
        ok &= abs(dinf) <= 3 * sinf
        rows_out.append({"aspect": aspect, "small": {"label": lab1, "D": d1, "sigma": s1}, "large": {"label": lab2, "D": d2, "sigma": s2},
                         "D_inf": dinf, "sigma": sinf})
    out["rectangle_additivity"] = {"aspects": rows_out, "accepted": ok}
    # the 45-degree rotated square: additivity in its orthogonal basis (w2, w1 - w2), and in the axis basis
    conf = sorted(by["F_conf"], key=lambda r: r["Lv"])
    vals = []
    for r in conf:
        Dp, sp = moments(r, lambda t: contr(t, 0) + contr(t, 2) - contr(t, 1) - contr(t, 3))
        Da, sa = moments(r, lambda t: contr(t, 0) - contr(t, 1) - contr(t, 2) + contr(t, 3))
        vals.append({"label": r["label"], "D_orthogonal": Dp, "sigma_orthogonal": sp, "D_axis": Da, "sigma_axis": sa})
    dinf, sinf = 2 * vals[1]["D_orthogonal"] - vals[0]["D_orthogonal"], math.hypot(2 * vals[1]["sigma_orthogonal"], vals[0]["sigma_orthogonal"])
    out["rotated_square"] = {"sizes": vals, "D_orthogonal_inf": dinf, "sigma": sinf, "accepted": abs(dinf) <= 3 * sinf,
                             "axis_basis_far_from_zero": abs(vals[1]["D_axis"]) > 10 * vals[1]["sigma_axis"]}
    # descriptive: harmonic content of E, O, U, G under shear
    harm = {}
    for r in by["F_harm"]:
        rec = {"s": r["s"], "s_over_Lh": r["s"] / r["Lh"]}
        for name, f in (("E", lambda t: contr(t, 0) - contr(t, 2)), ("O", lambda t: contr(t, 1) - contr(t, 3)),
                        ("U", lambda t: contr(t, 0) + contr(t, 2)), ("G", lambda t: contr(t, 1) + contr(t, 3)),
                        ("D", lambda t: contr(t, 0) - contr(t, 1) - contr(t, 2) + contr(t, 3))):
            m, se = moments(r, f)
            rec[name], rec["sigma_" + name] = m, se
        harm.setdefault(f"{r['Lh']}x{r['Lv']}", []).append(rec)
    out["harmonics"] = {k: sorted(v, key=lambda x: x["s"]) for k, v in harm.items()}
    # companion relations on rectangles (reported): odd-winding additivity and the consistency relation
    comp = []
    for r in by["F_rect"]:
        R2, s2 = moments(r, lambda t: odd_line(t, 1) + odd_line(t, 2) - odd_line(t, 3))
        diag, sd = moments(r, lambda t: (t[1] == 4) + (t[2] == 4))
        R3, s3 = moments(r, lambda t: (1 - (1 - (t[1] == 1) - odd_line(t, 1)) - (1 - (t[2] == 1) - odd_line(t, 2))
                                       + (1 - (t[3] == 1) - odd_line(t, 3))) - contr(t, 0))
        comp.append({"label": r["label"], "odd10_plus_odd01_minus_odd11": R2, "sigma": s2, "diagonal_odd_lines": diag,
                     "sigma_diagonal": sd, "consistency_relation_residual": R3, "sigma_R3": s3})
    out["companions"] = comp
    return out


def controls(rows):
    fails = []
    for r in rows:
        n = r["samples"]
        for q in (1, 2, 3):
            if r[f"mis{q}"]:
                fails.append(f"test disagreement {r['label']} sector {q}")
            c, x = r[f"c{q}"], r[f"x{q}"]
            if abs(c - x) > 4 * math.sqrt(c + x):
                fails.append(f"duality {r['family']} {r['label']} sector {q}")
        if r["mis0"] or r["inv0"]:
            fails.append(f"untwisted sector flagged {r['label']}")
        if sum(r["joint_types"].values()) != n:
            fails.append(f"joint pattern total {r['label']}")
    return fails


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    assert contract["status"] == "Frozen" and contract["evidence_stage"] == "confirmatory"
    OUT.mkdir(parents=True, exist_ok=True)
    raw = OUT / "raw_rows.jsonl"
    if raw.exists():
        raw.unlink()
    started = time.time()
    build = Path(tempfile.mkdtemp(prefix="simt-"))
    binary = str(build / "simt")
    subprocess.run(["gcc", "-O2", "-o", binary, str(HERE / "simt.c")], check=True)
    gcc = subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    rows = []
    try:
        for fam in ("F_exact", "F_odd", "F_shear", "F_rect", "F_conf", "F_harm"):
            for (Lh, Lv, s, n) in ROSTER[fam]:
                row = run_row(binary, fam, Lh, Lv, s, n)
                rows.append(row)
                with open(raw, "a") as f:
                    f.write(json.dumps(row, sort_keys=True) + "\n")
                print(fam, row["label"], row["samples"], round(time.time() - started), flush=True)
    finally:
        shutil.rmtree(build, ignore_errors=True)
    fails = controls(rows)
    result = {"schema_version": 1, "experiment_id": contract["experiment_id"], "ticket": contract["ticket"],
              "evidence_stage": contract["evidence_stage"], "controls_ok": not fails, "control_failures": fails,
              "rows": len(rows), "compiler": gcc, "workers": WORKERS}
    if fails:
        result["verdict"] = "invalid"
    else:
        a = analyse(rows)
        result.update(a)
        result["primary"] = {"odd_line_accepted": a["odd_line"]["accepted"], "shear_independence_accepted": a["shear_independence"]["accepted"]}
        result["secondary"] = {"rectangle_additivity_accepted": a["rectangle_additivity"]["accepted"],
                               "rotated_square_accepted": a["rotated_square"]["accepted"]}
        if a["odd_line"]["accepted"] and a["shear_independence"]["accepted"]:
            result["verdict"] = "supported"
        elif a["odd_line"]["decisively_rejected"] or a["shear_independence"]["decisively_rejected"]:
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
