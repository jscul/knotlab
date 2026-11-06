#!/usr/bin/env python3
"""Independent check of DIRECTIONAL-RIGIDITY-20261023-001A-E001; imports no producer code.

Reads the frozen contract, rows.jsonl and result.json, and:
- checks the roster (tori, placements, class lists), the totals, and the controls against the frozen record of
  TRIPLE-SHIELD-20261023-001A-E001;
- recomputes the fitting twists (brute force over hidden assignments with numpy up to 16 vertices, an own PySAT search above) and
  from them the odd classes of every twist;
- recomputes P1 to P7 and the verdict from the patterns;
- certifies single configurations with its own solver encoding (PySAT, Glucose 3) along every listed class: a cylinder contradicts
  when a strip of 30 periods has no assignment, and does not when a cyclic cover of at most 24 sheets has one. The configurations
  are random ones and, located by bisection with the producer's programs, selective ones. The producer's pattern for each must
  equal the certified one.

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
ART = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "artifacts/DIRECTIONAL-RIGIDITY-20261023-001A" / HERE.name
SHIELD = ROOT / "artifacts/TRIPLE-SHIELD-20261023-001A/TRIPLE-SHIELD-20261023-001A-E001_exact_dual_pairs"
CENSUS = ROOT / "artifacts/TRIPLE-TWIST-20261023-001B/TRIPLE-TWIST-20261023-001B-E001_contact_census/rows.jsonl"
TWISTS = [(0, 0), (0, 1), (1, 0), (1, 1)]
UPO, DNO = ((0, 0), (1, 0), (1, 1)), ((0, 0), (0, 1), (1, 1))
SATURATED = {45, 61, 101, 103, 135, 149, 157, 199}
ONE_DIMENSIONAL = {91, 94, 123, 183, 167, 173}
NEVER = {127, 223, 191, 239}
SELECTIVE = {54, 62, 109, 110, 111, 125, 147, 151, 155, 159, 203, 215}
TORI = {(3, 3): ("spat", "e", 0), (3, 4): ("spat", "e", 0), (4, 4): ("spat", "s", 1 << 22), (4, 5): ("spat2", "s", 1 << 22),
        (5, 5): ("spat2", "s", 1 << 20)}
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
    """Twists with a doubly allowed assignment: numpy brute force up to 16 vertices, an own PySAT encoding above."""
    V = L * M
    U = R & comp(R)
    out = []
    for q in TWISTS:
        if V <= 16:
            H = np.arange(1 << V, dtype=np.int64)
            ok = np.ones(1 << V, dtype=bool)
            for P in triangles(L, M):
                pat = np.zeros(1 << V, dtype=np.int64)
                for k, p in enumerate(P):
                    pat |= (((H >> vid(p, L, M)) & 1) ^ gauge(p, q, L, M)) << k
                ok &= ((U >> pat) & 1).astype(bool)
                if not ok.any():
                    break
            found = bool(ok.any())
        else:
            cl = []
            for P in triangles(L, M):
                vs = [vid(p, L, M) + 1 for p in P]
                g = [gauge(p, q, L, M) for p in P]
                for pat in range(8):
                    if not (U >> pat) & 1:
                        cl.append([(-vs[k] if ((pat >> k) & 1) ^ g[k] else vs[k]) for k in range(3)])
            found = solvable(cl)
        if found:
            out.append(q)
    return out


def odd_mask(classes, fit, q):
    return sum(1 << k for k, g in enumerate(classes) if fit and all(((q[0] ^ f[0]) * g[0] + (q[1] ^ f[1]) * g[1]) & 1 for f in fit))


def selective(m, om):
    return m != 0 and m != om and bin(m).count("1") >= 2 and not (m & ~om)


def diagonal_class(L, M):
    from math import gcd
    l = L * M // gcd(L, M)
    return (l // L, l // M)


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


def certified_pattern(R, L, M, q, x, classes):
    """(pattern over the classes, undetermined classes); the torus is not tested, so pattern 0 includes satisfiable tori."""
    m = und = 0
    for k, c in enumerate(classes):
        if not solvable(lifted_clauses(R, L, M, q, x, c, STRIP, False)):
            m |= 1 << k
        elif not any(solvable(lifted_clauses(R, L, M, q, x, c, s, True)) for s in range(1, COVERS + 1)):
            und |= 1 << k
    return m, und


def program(bins, prog, R, L, M, q, lo, hi, classes):
    if prog == "spat":
        args = [str(v) for g in classes[3:] for v in g]
    else:
        args = [str(v) for g in classes for v in g]
    out = subprocess.run([bins[prog], str(R), str(L), str(M), str(q[0]), str(q[1]), "e", str(lo), str(hi), "1"] + args,
                         capture_output=True, text=True, check=True).stdout.split("\n")
    hist = {int(l.split()[0]): int(l.split()[1]) for l in out[1:] if l}
    if prog == "spat":
        sat = int(out[0].split()[3])
        if sat:
            hist[0] = hist.get(0, 0) + sat
    return hist


def single(bins, prog, R, L, M, q, x, classes):
    return next(iter(program(bins, prog, R, L, M, q, x, x + 1, classes)))


def locate(bins, prog, R, L, M, q, rng, want, classes, blocks=6, size=4096):
    total = 1 << (2 * L * M)
    for _ in range(blocks):
        lo = rng.randrange(max(1, total // size)) * size
        hi = min(total, lo + size)
        if not any(want(m) for m in program(bins, prog, R, L, M, q, lo, hi, classes)):
            continue
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if any(want(m) for m in program(bins, prog, R, L, M, q, lo, mid, classes)):
                hi = mid
            else:
                lo = mid
        return lo
    return None


def group(R, t):
    if t != "three":
        return "two-literal"
    for name, members in (("saturated", SATURATED), ("one-dimensional", ONE_DIMENSIONAL), ("never", NEVER), ("selective", SELECTIVE)):
        if R in members:
            return name
    return "other"


def main() -> int:
    problems = []
    contract = json.loads((HERE / "contract.json").read_text())
    result = json.loads((ART / "result.json").read_text())
    rows = [json.loads(l) for l in (ART / "rows.jsonl").read_text().splitlines() if l.strip()]
    shield = {(r["L"], r["M"], r["R"]): r for r in (json.loads(l) for l in (SHIELD / "rows.jsonl").read_text().splitlines() if l.strip())}
    reps = json.loads((SHIELD / "result.json").read_text())["orbit_representatives_4x4"]
    census = [json.loads(l) for l in CENSUS.read_text().splitlines() if l.strip()]
    kinds = {r["R"]: r["kind"] for r in census if r["class"] == "TILING"}
    if contract["status"] != "Frozen" or len(kinds) != 54:
        problems.append("contract not frozen or census not 54 tiling placements")
    by = {(r["L"], r["M"], r["R"]): r for r in rows}
    for (L, M) in TORI:
        want = sorted(kinds) if (L, M) in ((3, 3), (3, 4)) else sorted(reps)
        got = sorted(R for (l, m, R) in by if (l, m) == (L, M))
        if got != want:
            problems.append(f"roster {L}x{M}: {len(got)} rows, expected {len(want)}")
    controls_ok = not problems
    odd = {}
    for (L, M, R), r in by.items():
        classes = [tuple(c) for c in r["classes"]]
        fit = fitting(R, L, M)
        if sorted(map(list, fit)) != sorted(r["fitting"]):
            problems.append(f"fitting twists R={R} {L}x{M}")
        for q in TWISTS:
            v = r["twists"][f"{q[0]}{q[1]}"]
            om = odd_mask(classes, fit, q)
            odd[(L, M, R, q)] = om
            if v["odd_mask"] != om:
                problems.append(f"odd classes R={R} {L}x{M} {q}")
            prog, mode, sample = TORI[(L, M)]
            want_total = (1 << (2 * L * M)) if mode == "e" else sample
            pats = {int(m): n for m, n in v["patterns"].items()}
            if v["total"] != want_total or v["sat"] + sum(pats.values()) != want_total:
                problems.append(f"total R={R} {L}x{M} {q}")
                controls_ok = False
            if mode == "e":
                s = shield[(L, M, R)]["counts"][f"{q[0]}{q[1]}"]
                mine = [sum(pats.values()), [sum(n for m, n in pats.items() if m >> k & 1) for k in range(3)],
                        [sum(n for m, n in pats.items() if m & 7 == 1 << k) for k in range(3)], sum(n for m, n in pats.items() if m & 7 == 0)]
                if mine != [s["unsat"], s["cyl"], s["lone"], s["cross"]]:
                    problems.append(f"frozen record R={R} {L}x{M} {q}")
                    controls_ok = False
    print("roster, fitting twists and controls checked", flush=True)
    # predictions
    p1 = p2 = p3 = p4 = p5 = p7 = True
    p6_seen = {}
    for (L, M, R), r in by.items():
        g = group(R, "pair" if kinds[R] == "pair" else "three")
        if r["group"] != g:
            problems.append(f"group R={R}")
        classes = [tuple(c) for c in r["classes"]]
        d = diagonal_class(L, M)
        dmask = sum(1 << k for k, c in enumerate(classes) if c in (d, (-d[0], -d[1])))
        single_n = allodd = sel = 0
        for q in TWISTS:
            om = odd[(L, M, R, q)]
            for m, n in ((int(m), n) for m, n in r["twists"][f"{q[0]}{q[1]}"]["patterns"].items()):
                p1 &= not (m & ~om)
                if selective(m, om):
                    sel += n
                    p2 &= g != "two-literal"
                if g == "one-dimensional" and m & ~dmask:
                    p3 = False
                if g == "saturated" and m and m != om:
                    p4 = False
                if g == "never" and m:
                    p5 = False
                if m and bin(m).count("1") == 1:
                    single_n += n
                if m and m == om and bin(om).count("1") >= 2:
                    allodd += n
        if g == "selective" and (L, M) in ((4, 5), (5, 5)):
            p6_seen[(L, M, R)] = sel > 0
        if g != "two-literal" and single_n and allodd and not sel:
            p7 = False
    p6 = bool(p6_seen) and all(p6_seen.values())
    if not controls_ok:
        verdict = "invalid"
    elif not (p1 and p2 and p3):
        verdict = "refuted"
    elif p4 and p5 and p6 and p7:
        verdict = "supported"
    else:
        verdict = "partially supported"
    if verdict != result.get("verdict"):
        problems.append(f"verdict: own {verdict}, result {result.get('verdict')}")
    s = result.get("summary", {})
    for name, own in (("P1_even_classes_never", p1), ("P2_two_literal_rigid", p2), ("P3_one_dimensional_only_diagonal", p3),
                      ("P4_saturated_all_odd", p4), ("P5_never_contradict", p5), ("P6_selective_on_larger_tori", p6),
                      ("P7_lines_and_global_imply_selective", p7)):
        if s.get(name) != own:
            problems.append(f"{name}: own {own}, result {s.get(name)}")
    print("verdict recomputed", verdict, flush=True)
    # certificates
    stats = {"configurations": 0, "undetermined classes": 0, "selective certified": 0}
    with tempfile.TemporaryDirectory() as build:
        bins = {name: str(Path(build) / name) for name in ("spat", "spat2")}
        for name, path in bins.items():
            subprocess.run(["gcc", "-O2", "-o", path, str(HERE / f"{name}.c")], check=True)

        def check(R, L, M, q, x, classes, prog, kind):
            mine, und = certified_pattern(R, L, M, q, x, classes)
            theirs = single(bins, prog, R, L, M, q, x, classes)
            stats["configurations"] += 1
            stats["undetermined classes"] += bin(und).count("1")
            if (theirs & ~und) != (mine & ~und):
                problems.append(f"configuration {x} R={R} {L}x{M} {q}: program {theirs}, certified {mine} (undetermined {und})")
            elif kind and not und:
                stats[kind] += 1

        for (L, M, R), r in sorted(by.items()):
            prog = TORI[(L, M)][0]
            classes = [tuple(c) for c in r["classes"]]
            for q in TWISTS:
                key = f"{L}x{M}/{R}/{q[0]}{q[1]}"
                rng = random.Random(int(hashlib.sha256(key.encode()).hexdigest(), 16))
                if (L, M) in ((3, 3), (3, 4), (4, 4)) or q in ((0, 1), (1, 0)):
                    check(R, L, M, q, rng.randrange(1 << (2 * L * M)), classes, prog, None)
                om = odd[(L, M, R, q)]
                pats = {int(m) for m in r["twists"][f"{q[0]}{q[1]}"]["patterns"]}
                if (L, M) in ((3, 3), (3, 4), (4, 4)) and any(selective(m, om) for m in pats):
                    x = locate(bins, prog, R, L, M, q, rng, lambda m, om=om: selective(m, om), classes)
                    if x is not None:
                        check(R, L, M, q, x, classes, prog, "selective certified")
            print("certified", f"{L}x{M}", R, stats, flush=True)
    print(json.dumps({"problems": problems[:40], "n_problems": len(problems), "own_verdict": verdict,
                      "P1": p1, "P2": p2, "P3": p3, "P4": p4, "P5": p5, "P6": p6, "P7": p7, "certificates": stats}, indent=1))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
