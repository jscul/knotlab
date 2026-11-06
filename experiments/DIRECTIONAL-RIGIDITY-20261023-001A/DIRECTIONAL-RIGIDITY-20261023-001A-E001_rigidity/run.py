#!/usr/bin/env python3
"""Producer for DIRECTIONAL-RIGIDITY-20261023-001A-E001: rigid and selective contacts with more classes and larger tori.

The worlds are the 54 tiling placements of TRIPLE-TWIST-20261023-001B-E001. For every configuration of the visible bits (3 x 3 and
3 x 4) or a seeded sample (4 x 4, 4 x 5, 5 x 5), the programs decide for each class in the torus's list whether the cylinder cover
along it has a hidden assignment; the histogram of patterns is recorded.
- spat.c (LINE-DETECTOR-20261023-001A-E001) on 3 x 3, 3 x 4 and 4 x 4: classes (1,0), (0,1), (1,1) by the sliding-window transfer,
  further classes by the generalized transfer; it also reports configurations with an assignment on the torus.
- spat2.c on 4 x 5 and 5 x 5: every class by the transfer generalized to levels of up to six vertices.

A pattern is selective when it contains at least two classes and misses an odd class of the list (odd relative to every fitting
twist). Groups of three-place placements, from the scoping on 3 x 3: saturated, one-dimensional (doubly allowed patterns constrain
only the pair (a, c)), never contradicting, and selective.

Controls: totals; on 3 x 3 and 3 x 4 the torus, cylinder, lone and cross counts implied by the patterns equal the frozen record of
TRIPLE-SHIELD-20261023-001A-E001; on 3 x 3, spat2 and spat give the same patterns over their common classes for every placement and
twist.

    python3 -B run.py    writes rows.jsonl and result.json under artifacts/
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "DIRECTIONAL-RIGIDITY-20261023-001A" / HERE.name
CENSUS = ROOT / "artifacts/TRIPLE-TWIST-20261023-001B/TRIPLE-TWIST-20261023-001B-E001_contact_census/rows.jsonl"
SHIELD = ROOT / "artifacts/TRIPLE-SHIELD-20261023-001A/TRIPLE-SHIELD-20261023-001A-E001_exact_dual_pairs"
WORKERS = min(24, os.cpu_count() or 1)
TWISTS = ((0, 0), (0, 1), (1, 0), (1, 1))
TRACKED = ((1, 0), (0, 1), (1, 1))
EXTRA = {
    (3, 3): ((1, -1), (1, 2), (2, 1), (1, -2), (2, -1), (1, 3), (3, 1), (1, -3), (3, -1), (2, 3), (3, 2), (1, 4), (4, 1)),
    (3, 4): ((1, -1), (1, 2), (2, 1), (1, -2), (2, -1), (1, 3), (3, 1), (3, -1), (3, 2), (4, 1)),
    (4, 4): ((1, -1), (1, 2), (2, 1), (1, -2), (2, -1), (1, 3), (3, 1), (2, 3), (3, 2)),
}
WIDE = {
    (4, 5): ((1, 0), (0, 1), (1, 1), (1, -1), (1, 2), (2, 1), (2, -1), (3, 1), (3, 2)),
    (5, 5): ((1, 0), (0, 1), (1, 1), (1, -1), (1, 2), (2, 1)),
}
TORI = (("F_seen", 3, 3, "spat", "e", 0), ("F_fresh", 3, 4, "spat", "e", 0), ("F_fresh", 4, 4, "spat", "s", 1 << 22),
        ("F_fresh", 4, 5, "spat2", "s", 1 << 22), ("F_fresh", 5, 5, "spat2", "s", 1 << 20))
CHUNKS = 16
SATURATED = (45, 61, 101, 103, 135, 149, 157, 199)
ONE_DIMENSIONAL = (91, 94, 123, 183, 167, 173)
NEVER = (127, 223, 191, 239)
SELECTIVE = (54, 62, 109, 110, 111, 125, 147, 151, 155, 159, 203, 215)
UPO, DNO = ((0, 0), (1, 0), (1, 1)), ((0, 0), (0, 1), (1, 1))


def comp(R):
    return sum(1 << (7 - p) for p in range(8) if R >> p & 1)


def depends(R):
    return [k for k in range(3) if any(((R >> p) & 1) != ((R >> (p ^ (1 << k))) & 1) for p in range(8))]


def placement_type(R, kind):
    if kind != "pair":
        return kind
    d, size = depends(R), bin(R).count("1")
    if len(d) == 2 and size == 6:
        return "orientation" if set(d) in ({0, 1}, {1, 2}) else "diagonal-clause"
    return "shared-coin"


def group(R, t):
    if t != "three":
        return "two-literal"
    for name, members in (("saturated", SATURATED), ("one-dimensional", ONE_DIMENSIONAL), ("never", NEVER), ("selective", SELECTIVE)):
        if R in members:
            return name
    return "other"


def fitting(R, L, M):
    """Twists with a doubly allowed assignment, by backtracking over the vertices."""
    U = R & comp(R)
    tris = [[(i + a, j + b) for a, b in offs] for j in range(M) for i in range(L) for offs in (UPO, DNO)]
    V = L * M
    out = []
    for q in TWISTS:
        by_last = [[] for _ in range(V)]
        for P in tris:
            vs = [(p[1] % M) * L + p[0] % L for p in P]
            g = [(q[0] * (p[0] // L) + q[1] * (p[1] // M)) & 1 for p in P]
            by_last[max(vs)].append((vs, g))
        h = [0] * V

        def go(v):
            if v == V:
                return True
            for b in (0, 1):
                h[v] = b
                if all(U >> sum((h[vs[k]] ^ g[k]) << k for k in range(3)) & 1 for vs, g in by_last[v]) and go(v + 1):
                    return True
            return False

        if go(0):
            out.append(q)
    return out


def odd_mask(classes, fit, q):
    return sum(1 << k for k, g in enumerate(classes) if fit and all(((q[0] ^ f[0]) * g[0] + (q[1] ^ f[1]) * g[1]) & 1 for f in fit))


def selective(m, om):
    return m and m != om and bin(m).count("1") >= 2 and not (m & ~om)


def diagonal_class(L, M):
    from math import gcd
    l = L * M // gcd(L, M)
    return (l // L, l // M)


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    assert contract["status"] == "Frozen" and contract["evidence_stage"] == "confirmatory"
    OUT.mkdir(parents=True, exist_ok=True)
    rows_path = OUT / "rows.jsonl"
    if rows_path.exists():
        rows_path.unlink()
    started = time.time()
    census = [json.loads(l) for l in CENSUS.read_text().splitlines() if l.strip()]
    tiling = {r["R"]: placement_type(r["R"], r["kind"]) for r in census if r["class"] == "TILING"}
    shield = {(r["L"], r["M"], r["R"]): r for r in (json.loads(l) for l in (SHIELD / "rows.jsonl").read_text().splitlines() if l.strip())}
    reps = json.loads((SHIELD / "result.json").read_text())["orbit_representatives_4x4"]
    build = Path(tempfile.mkdtemp(prefix="rigidity-"))
    bins = {"spat": str(build / "spat"), "spat2": str(build / "spat2")}
    for name, path in bins.items():
        subprocess.run(["gcc", "-O2", "-o", path, str(HERE / f"{name}.c")], check=True)
    records, fails = [], []
    try:
        for fam, L, M, prog, mode, sample in TORI:
            classes = TRACKED + EXTRA[(L, M)] if prog == "spat" else WIDE[(L, M)]
            extra = [str(v) for g in (EXTRA[(L, M)] if prog == "spat" else WIDE[(L, M)]) for v in g]
            todo = sorted(tiling) if (L, M) in ((3, 3), (3, 4)) else sorted(reps)
            jobs = []
            for R in todo:
                for q in TWISTS:
                    if mode == "e":
                        total = 1 << (2 * L * M)
                        step = max(1, total // CHUNKS)
                        jobs += [(R, q, "e", lo, min(total, lo + step), 1) for lo in range(0, total, step)]
                    else:
                        for c in range(CHUNKS):
                            seed = int(hashlib.sha256(f"rigidity/{L}x{M}/{R}/{q[0]}{q[1]}/{c}".encode()).hexdigest()[:15], 16)
                            jobs.append((R, q, "s", 0, sample // CHUNKS, seed))

            def one(j, L=L, M=M, prog=prog, extra=extra):
                R, q, md, lo, hi, seed = j
                out = subprocess.run([bins[prog], str(R), str(L), str(M), str(q[0]), str(q[1]), md, str(lo), str(hi), str(seed)] + extra,
                                     capture_output=True, text=True, check=True).stdout.split("\n")
                head = out[0].split()
                sat = int(head[3]) if prog == "spat" else 0
                return (R, q), int(head[1]), sat, {int(l.split()[0]): int(l.split()[1]) for l in out[1:] if l}

            sums = {}
            with ThreadPoolExecutor(WORKERS) as ex:
                for key, total, sat, hist in ex.map(one, jobs):
                    acc = sums.setdefault(key, [0, 0, {}])
                    acc[0] += total
                    acc[1] += sat
                    for m, n in hist.items():
                        acc[2][m] = acc[2].get(m, 0) + n
            for R in todo:
                fit = ([tuple(f) for f in shield[(L, M, R)]["fitting"]] if (L, M, R) in shield else fitting(R, L, M))
                rec = {"family": fam, "L": L, "M": M, "R": R, "type": tiling[R], "group": group(R, tiling[R]), "program": prog,
                       "mode": mode, "fitting": [list(f) for f in fit], "classes": [list(g) for g in classes],
                       "diagonal_class": list(diagonal_class(L, M)), "twists": {}}
                for q in TWISTS:
                    total, sat, hist = sums[(R, q)]
                    rec["twists"][f"{q[0]}{q[1]}"] = {"total": total, "sat": sat, "odd_mask": odd_mask(classes, fit, q),
                                                      "patterns": {str(m): n for m, n in sorted(hist.items())}}
                records.append(rec)
                with open(rows_path, "a") as f:
                    f.write(json.dumps(rec, sort_keys=True) + "\n")
            print(fam, f"{L}x{M}", len(todo), "placements", round(time.time() - started), flush=True)
        # control: spat2 against spat on 3 x 3 over the classes common to both lists
        common = (TRACKED + EXTRA[(3, 3)])[:8]
        spat3 = {r["R"]: r for r in records if (r["L"], r["M"]) == (3, 3)}

        def cmp(job):
            R, q = job
            out = subprocess.run([bins["spat2"], str(R), "3", "3", str(q[0]), str(q[1]), "e", "0", str(1 << 18), "1"]
                                 + [str(v) for g in common for v in g], capture_output=True, text=True, check=True).stdout.split("\n")
            mine = {int(l.split()[0]): int(l.split()[1]) for l in out[1:] if l}
            v = spat3[R]["twists"][f"{q[0]}{q[1]}"]
            ref = {}
            for m, n in v["patterns"].items():
                ref[int(m) & 0xFF] = ref.get(int(m) & 0xFF, 0) + n
            ref[0] = ref.get(0, 0) + v["sat"]
            return R, q, mine == {k: n for k, n in ref.items() if n}

        with ThreadPoolExecutor(WORKERS) as ex:
            for R, q, ok in ex.map(cmp, [(R, q) for R in sorted(spat3) for q in TWISTS]):
                if not ok:
                    fails.append(f"spat2 and spat differ on 3x3 R={R} {q}")
    finally:
        shutil.rmtree(build, ignore_errors=True)
    for rec in records:
        L, M = rec["L"], rec["M"]
        for qs, v in rec["twists"].items():
            want = (1 << (2 * L * M)) if rec["mode"] == "e" else {(a, b): n for _f, a, b, _p, _m, n in TORI}[(L, M)]
            if v["total"] != want:
                fails.append(f"total {L}x{M} R={rec['R']} {qs}")
            if rec["mode"] == "e":
                pats = {int(m): n for m, n in v["patterns"].items()}
                mine = [sum(pats.values()), [sum(n for m, n in pats.items() if m >> k & 1) for k in range(3)],
                        [sum(n for m, n in pats.items() if m & 7 == 1 << k) for k in range(3)], sum(n for m, n in pats.items() if m & 7 == 0)]
                s = shield[(L, M, rec["R"])]["counts"][qs]
                if mine != [s["unsat"], s["cyl"], s["lone"], s["cross"]]:
                    fails.append(f"frozen record {L}x{M} R={rec['R']} {qs}")
    result = {"schema_version": 1, "experiment_id": contract["experiment_id"], "ticket": contract["ticket"],
              "evidence_stage": contract["evidence_stage"], "controls_ok": not fails, "control_failures": fails[:40],
              "rows": len(records), "workers": WORKERS}
    if fails:
        result["verdict"] = "invalid"
    else:
        p1, p2, p3, p4, p5, p6_seen, p7 = [], [], [], [], [], {}, []
        table = {}
        for rec in records:
            L, M, R, g = rec["L"], rec["M"], rec["R"], rec["group"]
            classes = [tuple(c) for c in rec["classes"]]
            dmask = sum(1 << k for k, c in enumerate(classes) if c in (tuple(rec["diagonal_class"]), tuple(-v for v in rec["diagonal_class"])))
            single = allodd = sel = 0
            for qs, v in rec["twists"].items():
                om = v["odd_mask"]
                for m, n in ((int(m), n) for m, n in v["patterns"].items()):
                    if m & ~om:
                        p1.append([L, M, R, qs, m])
                    if selective(m, om):
                        sel += n
                        if g == "two-literal":
                            p2.append([L, M, R, qs, m, n])
                    if g == "one-dimensional" and m & ~dmask:
                        p3.append([L, M, R, qs, m, n])
                    if g == "saturated" and m and m != om:
                        p4.append([L, M, R, qs, m, n])
                    if g == "never" and m:
                        p5.append([L, M, R, qs, m, n])
                    if m and bin(m).count("1") == 1:
                        single += n
                    if m and m == om and bin(om).count("1") >= 2:
                        allodd += n
            if g == "selective" and (L, M) in ((4, 5), (5, 5)):
                p6_seen[(L, M, R)] = sel > 0
            if rec["type"] == "three" and single and allodd and not sel:
                p7.append([L, M, R, single, allodd])
            table.setdefault(f"{L}x{M}", {}).setdefault(g, {"placements": 0, "selective_placements": 0})
            table[f"{L}x{M}"][g]["placements"] += 1
            table[f"{L}x{M}"][g]["selective_placements"] += sel > 0
        p6 = [list(k) for k, v in p6_seen.items() if not v]
        result["summary"] = {"P1_even_classes_never": not p1, "P1_failures": p1[:20],
                             "P2_two_literal_rigid": not p2, "P2_failures": p2[:20],
                             "P3_one_dimensional_only_diagonal": not p3, "P3_failures": p3[:20],
                             "P4_saturated_all_odd": not p4, "P4_exceptions": p4[:20],
                             "P5_never_contradict": not p5, "P5_exceptions": p5[:20],
                             "P6_selective_on_larger_tori": not p6 and bool(p6_seen), "P6_missing": p6,
                             "P7_lines_and_global_imply_selective": not p7, "P7_exceptions": p7[:20],
                             "groups": table}
        if p1 or p2 or p3:
            result["verdict"] = "refuted"
        elif not (p4 or p5 or p6 or p7):
            result["verdict"] = "supported"
        else:
            result["verdict"] = "partially supported"
    result["wall_seconds"] = round(time.time() - started, 1)
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("controls_ok", "verdict", "wall_seconds")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
