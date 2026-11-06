#!/usr/bin/env python3
"""Producer for LINE-DETECTOR-20261023-001A-E001: which classes a configuration contradicts along.

The worlds are the 54 tiling placements of TRIPLE-TWIST-20261023-001B-E001 on L x M triangular tori, as in
TRIPLE-SHIELD-20261023-001A-E001. For every configuration of the visible bits (all of them on 3 x 3 and 3 x 4, a seeded sample
of 2^22 per twist on 4 x 4), spat.c decides for each of eight classes whether the cylinder cover along it has a hidden
assignment, and the histogram of the resulting patterns is recorded.

A pattern is the set of classes, among the eight, along which the cylinder contradicts. With the classes odd relative to every
fitting twist (only these can contradict), a pattern follows the trichotomy when it is empty, a single class, or every odd class
of the eight; otherwise it is selective.

Controls: totals; on 3 x 3 and 3 x 4 the counts of torus contradictions, cylinder contradictions, lone lines and crosses
implied by the patterns equal the frozen record of TRIPLE-SHIELD-20261023-001A-E001 for every placement and twist.

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
OUT = ROOT / "artifacts" / "LINE-DETECTOR-20261023-001A" / HERE.name
CENSUS = ROOT / "artifacts/TRIPLE-TWIST-20261023-001B/TRIPLE-TWIST-20261023-001B-E001_contact_census/rows.jsonl"
SHIELD = ROOT / "artifacts/TRIPLE-SHIELD-20261023-001A/TRIPLE-SHIELD-20261023-001A-E001_exact_dual_pairs"
WORKERS = min(24, os.cpu_count() or 1)
TORI = (("F_seen", 3, 3, "e"), ("F_fresh", 3, 4, "e"), ("F_fresh", 4, 4, "s"))
SAMPLE = 1 << 22
CHUNKS = 16
TWISTS = ((0, 0), (0, 1), (1, 0), (1, 1))
CLASSES = ((1, 0), (0, 1), (1, 1), (1, -1), (1, 2), (2, 1), (1, -2), (2, -1))
SELECTIVE_ON_3x3 = (54, 62, 109, 110, 111, 125, 147, 151, 155, 159, 203, 215)
IMPURE_LONE = (54, 147, 62, 110, 155, 203)
PURE_UNEQUAL = (91, 94, 111, 125, 159, 215)


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


def odd_mask(fit, q):
    return sum(1 << k for k, g in enumerate(CLASSES)
               if fit and all(((q[0] ^ f[0]) * g[0] + (q[1] ^ f[1]) * g[1]) & 1 for f in fit))


def selective(m, om):
    return m and m != om and bin(m).count("1") >= 2


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
    shield_rows = [json.loads(l) for l in (SHIELD / "rows.jsonl").read_text().splitlines() if l.strip()]
    shield = {(r["L"], r["M"], r["R"]): r for r in shield_rows}
    reps = json.loads((SHIELD / "result.json").read_text())["orbit_representatives_4x4"]
    build = Path(tempfile.mkdtemp(prefix="spat-"))
    binary = str(build / "spat")
    subprocess.run(["gcc", "-O2", "-o", binary, str(HERE / "spat.c")], check=True)
    extra = [str(v) for g in CLASSES[3:] for v in g]
    records, fails = [], []
    try:
        for fam, L, M, mode in TORI:
            todo = sorted(tiling) if (L, M) != (4, 4) else sorted(reps)
            jobs = []
            for R in todo:
                for q in TWISTS:
                    if mode == "e":
                        total = 1 << (2 * L * M)
                        step = max(1, total // CHUNKS)
                        for lo in range(0, total, step):
                            jobs.append((R, q, "e", lo, min(total, lo + step), 1))
                    else:
                        step = SAMPLE // CHUNKS
                        for c in range(CHUNKS):
                            seed = int(hashlib.sha256(f"{L}x{M}/{R}/{q[0]}{q[1]}/{c}".encode()).hexdigest()[:15], 16)
                            jobs.append((R, q, "s", 0, step, seed))

            def one(j):
                R, q, md, lo, hi, seed = j
                out = subprocess.run([binary, str(R), str(L), str(M), str(q[0]), str(q[1]), md, str(lo), str(hi), str(seed)] + extra,
                                     capture_output=True, text=True, check=True).stdout.split("\n")
                head = out[0].split()
                hist = {int(l.split()[0]): int(l.split()[1]) for l in out[1:] if l}
                return (R, q), int(head[1]), int(head[3]), hist

            sums = {}
            with ThreadPoolExecutor(WORKERS) as ex:
                for key, total, sat, hist in ex.map(one, jobs):
                    acc = sums.setdefault(key, [0, 0, {}])
                    acc[0] += total
                    acc[1] += sat
                    for m, n in hist.items():
                        acc[2][m] = acc[2].get(m, 0) + n
            for R in todo:
                fit = [tuple(f) for f in shield[(L, M, R)]["fitting"]]
                rec = {"family": fam, "L": L, "M": M, "R": R, "type": tiling[R], "mode": mode, "fitting": [list(f) for f in fit],
                       "classes": [list(g) for g in CLASSES], "twists": {}}
                for q in TWISTS:
                    total, sat, hist = sums[(R, q)]
                    rec["twists"][f"{q[0]}{q[1]}"] = {"total": total, "sat": sat, "odd_mask": odd_mask(fit, q),
                                                      "patterns": {str(m): n for m, n in sorted(hist.items())}}
                records.append(rec)
                with open(rows_path, "a") as f:
                    f.write(json.dumps(rec, sort_keys=True) + "\n")
            print(fam, f"{L}x{M}", len(todo), "placements", round(time.time() - started), flush=True)
    finally:
        shutil.rmtree(build, ignore_errors=True)
    # controls
    for rec in records:
        L, M = rec["L"], rec["M"]
        for qs, v in rec["twists"].items():
            want = (1 << (2 * L * M)) if rec["mode"] == "e" else SAMPLE
            if v["total"] != want:
                fails.append(f"total {L}x{M} R={rec['R']} {qs}")
            if rec["mode"] != "e":
                continue
            pats = {int(m): n for m, n in v["patterns"].items()}
            unsat = sum(pats.values())
            cyl = [sum(n for m, n in pats.items() if m >> k & 1) for k in range(3)]
            lone = [sum(n for m, n in pats.items() if m & 7 == 1 << k) for k in range(3)]
            cross = sum(n for m, n in pats.items() if m & 7 == 0)
            rec_shield = shield[(L, M, rec["R"])]["counts"][qs]
            if [unsat, cyl, lone, cross] != [rec_shield["unsat"], rec_shield["cyl"], rec_shield["lone"], rec_shield["cross"]]:
                fails.append(f"frozen record {L}x{M} R={rec['R']} {qs}: {[unsat, cyl, lone, cross]}")
    result = {"schema_version": 1, "experiment_id": contract["experiment_id"], "ticket": contract["ticket"],
              "evidence_stage": contract["evidence_stage"], "controls_ok": not fails, "control_failures": fails[:40],
              "rows": len(records), "workers": WORKERS}
    if fails:
        result["verdict"] = "invalid"
    else:
        p1, p2, p3_missing, p4 = [], [], set(SELECTIVE_ON_3x3), []
        tally, pure_pairs = {}, []
        for rec in records:
            L, M, R, t = rec["L"], rec["M"], rec["R"], rec["type"]
            for qs, v in rec["twists"].items():
                om = v["odd_mask"]
                for m, n in ((int(m), n) for m, n in v["patterns"].items()):
                    if m & ~om:
                        p1.append([L, M, R, qs, m])
                    if selective(m, om):
                        key = f"{rec['family']} {L}x{M} {t}"
                        tally.setdefault(key, {"placements_selective": set(), "configurations": 0})
                        tally[key]["placements_selective"].add(R)
                        tally[key]["configurations"] += n
                        if t != "three":
                            p2.append([L, M, R, qs, m, n])
                        if (L, M) == (3, 4):
                            p3_missing.discard(R)
                    if (L, M) == (3, 4) and R in IMPURE_LONE and m in (1, 2, 4):
                        p4.append([L, M, R, qs, m, n])
            # pure lines along a class relative to the eight: pattern exactly one tracked class
            fit = [tuple(f) for f in rec["fitting"]]
            for ci, c in enumerate(CLASSES[:3]):
                odd = [q for q in TWISTS if fit and all(((q[0] ^ f[0]) * c[0] + (q[1] ^ f[1]) * c[1]) & 1 for f in fit)]
                if len(odd) == 2:
                    counts = [rec["twists"][f"{q[0]}{q[1]}"]["patterns"].get(str(1 << ci), 0) for q in odd]
                    lone = [sum(n for m, n in rec["twists"][f"{q[0]}{q[1]}"]["patterns"].items() if int(m) & 7 == 1 << ci) for q in odd]
                    pure_pairs.append({"torus": f"{L}x{M}", "R": R, "type": t, "class": list(c), "twists": [f"{q[0]}{q[1]}" for q in odd],
                                       "lone": lone, "pure_in_eight": counts})
        for k in tally:
            tally[k]["placements_selective"] = sorted(tally[k]["placements_selective"])
        p5 = [p for p in pure_pairs if p["torus"] == "3x4" and p["R"] in PURE_UNEQUAL and p["pure_in_eight"][0] != p["pure_in_eight"][1]]
        result["summary"] = {"P1_even_classes_never_contradict": not p1, "P1_failures": p1[:20],
                             "P2_two_literal_trichotomy": not p2, "P2_failures": p2[:20],
                             "P3_selective_on_3x4": not p3_missing, "P3_missing": sorted(p3_missing),
                             "P4_lone_lines_impure_on_3x4": not p4, "P4_exceptions": p4[:20],
                             "P5_pure_lines_unequal_on_3x4": bool(p5), "P5_witnesses": p5[:20],
                             "selective_tally": tally, "pure_pairs": pure_pairs}
        if p1 or p2:
            result["verdict"] = "refuted"
        elif not p3_missing and not p4 and p5:
            result["verdict"] = "supported"
        else:
            result["verdict"] = "partially supported"
    result["wall_seconds"] = round(time.time() - started, 1)
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("controls_ok", "verdict", "wall_seconds")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
