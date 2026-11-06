#!/usr/bin/env python3
"""Independent check of LINE-DETECTOR-20261023-001A-E001; imports no producer code.

Reads the frozen contract, rows.jsonl and result.json, and:
- checks the roster (tori, placements, the 4 x 4 representatives), the totals, and the controls against the frozen record of
  TRIPLE-SHIELD-20261023-001A-E001;
- recomputes the fitting twists by brute force over hidden assignments (numpy) and from them the odd classes of every twist;
- recomputes P1 to P5 and the verdict from the patterns;
- certifies single configurations with its own solver encoding (PySAT, Glucose 3) along all eight classes: a cylinder contradicts
  when a strip of 30 periods has no assignment, and does not when a cyclic cover of at most 24 sheets has one. The configurations
  are random ones and, located by bisection with the producer's program, selective ones and lone lines of the placements in P4
  and P5. The producer's pattern for each must equal the certified one.

    .venv/bin/python -B check_result.py [artifact directory]
"""

from __future__ import annotations

import hashlib
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from pysat.solvers import Glucose3

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "artifacts/LINE-DETECTOR-20261023-001A" / HERE.name
SHIELD = ROOT / "artifacts/TRIPLE-SHIELD-20261023-001A/TRIPLE-SHIELD-20261023-001A-E001_exact_dual_pairs"
CENSUS = ROOT / "artifacts/TRIPLE-TWIST-20261023-001B/TRIPLE-TWIST-20261023-001B-E001_contact_census/rows.jsonl"
TWISTS = [(0, 0), (0, 1), (1, 0), (1, 1)]
CLASSES = [(1, 0), (0, 1), (1, 1), (1, -1), (1, 2), (2, 1), (1, -2), (2, -1)]
UPO, DNO = ((0, 0), (1, 0), (1, 1)), ((0, 0), (0, 1), (1, 1))
SELECTIVE_ON_3x3 = {54, 62, 109, 110, 111, 125, 147, 151, 155, 159, 203, 215}
IMPURE_LONE = {54, 147, 62, 110, 155, 203}
PURE_UNEQUAL = {91, 94, 111, 125, 159, 215}
STRIP, COVERS = 30, 24


def comp(R):
    return sum(1 << (7 - p) for p in range(8) if R >> p & 1)


def triangles(L, M):
    return [[(i + a, j + b) for a, b in offs] for j in range(M) for i in range(L) for offs in (UPO, DNO)]


def vid(p, L, M):
    return (p[1] % M) * L + p[0] % L


def deck(p, L, M):
    return (p[0] // L, p[1] // M)


def gauge(p, q, L, M):
    d = deck(p, L, M)
    return (q[0] * d[0] + q[1] * d[1]) & 1


def fitting(R, L, M):
    V = L * M
    H = np.arange(1 << V, dtype=np.int64)
    U = R & comp(R)
    out = []
    for q in TWISTS:
        ok = np.ones(1 << V, dtype=bool)
        for P in triangles(L, M):
            pat = np.zeros(1 << V, dtype=np.int64)
            for k, p in enumerate(P):
                pat |= (((H >> vid(p, L, M)) & 1) ^ gauge(p, q, L, M)) << k
            ok &= ((U >> pat) & 1).astype(bool)
            if not ok.any():
                break
        if ok.any():
            out.append(q)
    return out


def odd_mask(fit, q):
    return sum(1 << k for k, g in enumerate(CLASSES) if fit and all(((q[0] ^ f[0]) * g[0] + (q[1] ^ f[1]) * g[1]) & 1 for f in fit))


def selective(m, om):
    return m != 0 and m != om and bin(m).count("1") >= 2


# ------------------------------------------------------------------ certificates

def complement_basis(c):
    """u with c0 u1 - c1 u0 = 1 (c primitive)."""
    for u0 in range(-4, 5):
        for u1 in range(-4, 5):
            if c[0] * u1 - c[1] * u0 == 1:
                return (u0, u1)
    raise ValueError(c)


def lifted_clauses(R, L, M, q, x, c, sheets, cyclic):
    u = complement_basis(c)
    var, out = {}, []
    for f, P in enumerate(triangles(L, M)):
        rel = comp(R) if (x >> f) & 1 else R
        g = [gauge(p, q, L, M) for p in P]
        corners = []
        for p in P:
            d = deck(p, L, M)
            corners.append((vid(p, L, M), c[0] * d[1] - c[1] * d[0]))     # coordinate along u, since det [c u] = 1
        bad = [pat for pat in range(8) if not (rel >> pat) & 1]
        for m in range(sheets):
            vs = [var.setdefault((v, (t + m) % sheets if cyclic else t + m), len(var) + 1) for v, t in corners]
            for pat in bad:
                out.append([(-vs[k] if ((pat >> k) & 1) ^ g[k] else vs[k]) for k in range(3)])
    return out


def solvable(cl):
    with Glucose3(bootstrap_with=cl) as s:
        return s.solve()


def certified_pattern(R, L, M, q, x):
    """(pattern, undetermined classes); pattern -1 when the torus has an assignment."""
    if solvable(lifted_clauses(R, L, M, q, x, (1, 0), 1, True)):
        return -1, 0
    m = und = 0
    for k, c in enumerate(CLASSES):
        if not solvable(lifted_clauses(R, L, M, q, x, c, STRIP, False)):
            m |= 1 << k
        elif not any(solvable(lifted_clauses(R, L, M, q, x, c, s, True)) for s in range(2, COVERS + 1)):
            und |= 1 << k
    return m, und


def program(binary, R, L, M, q, lo, hi):
    extra = [str(v) for g in CLASSES[3:] for v in g]
    out = subprocess.run([binary, str(R), str(L), str(M), str(q[0]), str(q[1]), "e", str(lo), str(hi), "1"] + extra,
                         capture_output=True, text=True, check=True).stdout.split("\n")
    head = out[0].split()
    return int(head[3]), {int(l.split()[0]): int(l.split()[1]) for l in out[1:] if l}


def single(binary, R, L, M, q, x):
    sat, hist = program(binary, R, L, M, q, x, x + 1)
    return -1 if sat else next(iter(hist))


def locate(binary, R, L, M, q, rng, want, blocks=8, size=4096):
    """A configuration whose pattern satisfies want(pattern), by bisection inside random aligned blocks."""
    total = 1 << (2 * L * M)
    for _ in range(blocks):
        lo = rng.randrange(max(1, total // size)) * size
        hi = min(total, lo + size)
        if not any(want(m) for m in program(binary, R, L, M, q, lo, hi)[1]):
            continue
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if any(want(m) for m in program(binary, R, L, M, q, lo, mid)[1]):
                hi = mid
            else:
                lo = mid
        return lo
    return None


def main() -> int:
    problems = []
    contract = json.loads((HERE / "contract.json").read_text())
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(l) for l in (ART / "rows.jsonl").read_text().splitlines() if l.strip()]
    shield = {(r["L"], r["M"], r["R"]): r for r in (json.loads(l) for l in (SHIELD / "rows.jsonl").read_text().splitlines() if l.strip())}
    reps = json.loads((SHIELD / "result.json").read_text())["orbit_representatives_4x4"]
    tiling = sorted(r["R"] for r in (json.loads(l) for l in CENSUS.read_text().splitlines() if l.strip()) if r["class"] == "TILING")
    if contract["status"] != "Frozen" or len(tiling) != 54:
        problems.append("contract not frozen or census not 54 tiling placements")
    by = {(r["L"], r["M"], r["R"]): r for r in rows}
    for (L, M), want in (((3, 3), tiling), ((3, 4), tiling), ((4, 4), sorted(reps))):
        got = sorted(R for (l, m, R) in by if (l, m) == (L, M))
        if got != want:
            problems.append(f"roster {L}x{M}: {len(got)} rows, expected {len(want)}")
    controls_ok = not problems
    odd = {}
    for (L, M, R), r in by.items():
        fit = fitting(R, L, M)
        if sorted(map(list, fit)) != sorted(r["fitting"]):
            problems.append(f"fitting twists R={R} {L}x{M}")
        for q in TWISTS:
            v = r["twists"][f"{q[0]}{q[1]}"]
            om = odd_mask(fit, q)
            odd[(L, M, R, q)] = om
            if v["odd_mask"] != om:
                problems.append(f"odd classes R={R} {L}x{M} {q}")
            want_total = (1 << (2 * L * M)) if r["mode"] == "e" else (1 << 22)
            pats = {int(m): n for m, n in v["patterns"].items()}
            if v["total"] != want_total or v["sat"] + sum(pats.values()) != want_total:
                problems.append(f"total R={R} {L}x{M} {q}")
                controls_ok = False
            if r["mode"] == "e":
                s = shield[(L, M, R)]["counts"][f"{q[0]}{q[1]}"]
                mine = [sum(pats.values()), [sum(n for m, n in pats.items() if m >> k & 1) for k in range(3)],
                        [sum(n for m, n in pats.items() if m & 7 == 1 << k) for k in range(3)], sum(n for m, n in pats.items() if m & 7 == 0)]
                if mine != [s["unsat"], s["cyl"], s["lone"], s["cross"]]:
                    problems.append(f"frozen record R={R} {L}x{M} {q}")
                    controls_ok = False
    print("roster, fitting twists and controls checked", flush=True)
    # predictions and verdict
    types = {(r["L"], r["M"], r["R"]): r["type"] for r in rows}
    p1 = p2 = p4 = True
    sel34, p5 = set(), False
    for (L, M, R), r in by.items():
        for q in TWISTS:
            om = odd[(L, M, R, q)]
            for m, n in ((int(m), n) for m, n in r["twists"][f"{q[0]}{q[1]}"]["patterns"].items()):
                p1 &= not (m & ~om)
                if selective(m, om):
                    if types[(L, M, R)] != "three":
                        p2 = False
                    if (L, M) == (3, 4):
                        sel34.add(R)
                if (L, M) == (3, 4) and R in IMPURE_LONE and m in (1, 2, 4):
                    p4 = False
        if (L, M) == (3, 4) and R in PURE_UNEQUAL:
            fit = fitting(R, L, M)
            for ci, c in enumerate(CLASSES[:3]):
                pair = [q for q in TWISTS if fit and all(((q[0] ^ f[0]) * c[0] + (q[1] ^ f[1]) * c[1]) & 1 for f in fit)]
                if len(pair) == 2:
                    counts = [r["twists"][f"{q[0]}{q[1]}"]["patterns"].get(str(1 << ci), 0) for q in pair]
                    p5 |= counts[0] != counts[1]
    p3 = SELECTIVE_ON_3x3 <= sel34
    if not controls_ok:
        verdict = "invalid"
    elif not (p1 and p2):
        verdict = "refuted"
    elif p3 and p4 and p5:
        verdict = "supported"
    else:
        verdict = "partially supported"
    if verdict != result.get("verdict"):
        problems.append(f"verdict: own {verdict}, result {result.get('verdict')}")
    s = result.get("summary", {})
    for name, own in (("P1_even_classes_never_contradict", p1), ("P2_two_literal_trichotomy", p2), ("P3_selective_on_3x4", p3),
                      ("P4_lone_lines_impure_on_3x4", p4), ("P5_pure_lines_unequal_on_3x4", p5)):
        if s.get(name) != own:
            problems.append(f"{name}: own {own}, result {s.get(name)}")
    print("verdict recomputed", verdict, flush=True)
    # certificates
    stats = {"configurations": 0, "undetermined classes": 0, "selective certified": 0, "lone certified": 0}
    with tempfile.TemporaryDirectory() as build:
        binary = str(Path(build) / "spat")
        subprocess.run(["gcc", "-O2", "-o", binary, str(HERE / "spat.c")], check=True)

        def check(R, L, M, q, x, kind):
            mine, und = certified_pattern(R, L, M, q, x)
            theirs = single(binary, R, L, M, q, x)
            stats["configurations"] += 1
            if und:
                stats["undetermined classes"] += bin(und).count("1")
                if theirs >= 0 and (theirs & ~und) != (mine & ~und):
                    problems.append(f"configuration {x} R={R} {L}x{M} {q}: program {theirs}, certified {mine} (undetermined {und})")
                return
            if mine != theirs:
                problems.append(f"configuration {x} R={R} {L}x{M} {q}: program {theirs}, certified {mine}")
            elif kind:
                stats[kind] += 1

        for (L, M, R), r in sorted(by.items()):
            for q in TWISTS:
                key = f"{L}x{M}/{R}/{q[0]}{q[1]}"
                rng = random.Random(int(hashlib.sha256(key.encode()).hexdigest(), 16))
                check(R, L, M, q, rng.randrange(1 << (2 * L * M)), None)
                om = odd[(L, M, R, q)]
                pats = {int(m) for m in r["twists"][f"{q[0]}{q[1]}"]["patterns"]}
                if any(selective(m, om) for m in pats):
                    x = locate(binary, R, L, M, q, rng, lambda m, om=om: selective(m, om))
                    if x is not None:
                        check(R, L, M, q, x, "selective certified")
                if R in IMPURE_LONE | PURE_UNEQUAL and any(m & 7 in (1, 2, 4) for m in pats):
                    x = locate(binary, R, L, M, q, rng, lambda m: m & 7 in (1, 2, 4))
                    if x is not None:
                        check(R, L, M, q, x, "lone certified")
            print("certified", f"{L}x{M}", R, stats, flush=True)
    print(json.dumps({"problems": problems[:40], "n_problems": len(problems), "own_verdict": verdict,
                      "P1": p1, "P2": p2, "P3": p3, "P4": p4, "P5": p5, "certificates": stats}, indent=1))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
