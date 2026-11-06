#!/usr/bin/env python3
"""Producer for WALLS-WITH-CHOICES-20261024-001B-E001: do simple wall cycles decide every odd class on small tori?

For the twelve bending placements of DIRECTIONAL-RIGIDITY-20261023-001B-P001 on the 3 x 3 torus (16 classes) and the 3 x 4 torus
(13 classes), for every configuration and twist, walls.c predicts the contradiction pattern from the simple cycles of the wall
graph (a class contradicts when it is odd and no simple cycle has a transverse class and no overlap in Z c + Z e). The histograms
are compared with the frozen histograms of DIRECTIONAL-RIGIDITY-20261023-001A-E001, in which configurations with an assignment on the
torus are counted under pattern 0.

Controls: totals; the engine reproduces the twelve certified selective patterns of DIRECTIONAL-RIGIDITY-20261023-001B-P001,
Proposition 4; the first-visit-only variant misreads configuration 210021 of placement 151 in twist 01 on 3 x 3; the four
placements whose walls have no choices match on 3 x 3 (their rule is a theorem there).

    python3 -B run.py    writes rows.jsonl and result.json under artifacts/
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "WALLS-WITH-CHOICES-20261024-001B" / HERE.name
FROZEN = ROOT / "artifacts/DIRECTIONAL-RIGIDITY-20261023-001A/DIRECTIONAL-RIGIDITY-20261023-001A-E001_rigidity/rows.jsonl"
WORKERS = min(24, os.cpu_count() or 1)
BENDING = (54, 62, 109, 110, 111, 125, 147, 151, 155, 159, 203, 215)
NO_CHOICES = (54, 109, 147, 151)
TORI = ((3, 3), (3, 4))
CHUNKS = {(3, 3): 8, (3, 4): 256}
TWISTS = ("00", "01", "10", "11")
CERTIFIED = [  # (placement, twist, configuration, pattern over the first eight classes), DIRECTIONAL-RIGIDITY-20261023-001B-P001
    (54, "00", 168100, 195), (62, "00", 77851, 195), (109, "00", 204805, 18), (110, "00", 24642, 195), (111, "00", 36954, 17),
    (125, "00", 49253, 17), (147, "01", 30817, 10), (151, "01", 110633, 162), (155, "01", 45276, 10), (159, "01", 227852, 6),
    (203, "01", 123079, 10), (215, "01", 45302, 6),
]


def run_engine(binary, R, L, M, q, lo, hi, firstonly, classes):
    out = subprocess.run([binary, str(R), str(L), str(M), q[0], q[1], str(lo), str(hi), str(firstonly)]
                         + [str(v) for c in classes for v in c], capture_output=True, text=True, check=True).stdout.split("\n")
    total = int(out[0].split()[1])
    return total, {int(l.split()[0]): int(l.split()[1]) for l in out[1:] if l}


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    assert contract["status"] == "Frozen" and contract["evidence_stage"] == "confirmatory"
    OUT.mkdir(parents=True, exist_ok=True)
    rows_path = OUT / "rows.jsonl"
    if rows_path.exists():
        rows_path.unlink()
    started = time.time()
    frozen = {(r["R"], r["L"], r["M"]): r for r in (json.loads(l) for l in FROZEN.read_text().splitlines() if l.strip())}
    build = Path(tempfile.mkdtemp(prefix="walls-"))
    binary = str(build / "walls")
    subprocess.run(["gcc", "-O2", "-o", binary, str(HERE / "walls.c")], check=True)
    fails, mismatches, summary = [], [], {}
    # controls on the engine
    eight = [tuple(c) for c in frozen[(147, 3, 3)]["classes"][:8]]
    cert_ok = 0
    for R, q, x, pat in CERTIFIED:
        _t, h = run_engine(binary, R, 3, 3, q, x, x + 1, 0, eight)
        cert_ok += next(iter(h)) == pat
    if cert_ok != len(CERTIFIED):
        fails.append(f"certified patterns reproduced: {cert_ok} of {len(CERTIFIED)}")
    _t, h_all = run_engine(binary, 151, 3, 3, "01", 210021, 210022, 0, eight)
    _t, h_first = run_engine(binary, 151, 3, 3, "01", 210021, 210022, 1, eight)
    if next(iter(h_all)) == next(iter(h_first)):
        fails.append("the first-visit-only variant does not misread placement 151, configuration 210021")
    jobs = []
    for L, M in TORI:
        total = 1 << (2 * L * M)
        step = total // CHUNKS[(L, M)]
        for R in BENDING:
            for q in TWISTS:
                jobs += [(R, L, M, q, lo, lo + step) for lo in range(0, total, step)]

    def one(job):
        R, L, M, q, lo, hi = job
        classes = [tuple(c) for c in frozen[(R, L, M)]["classes"]]
        return (R, L, M, q), run_engine(binary, R, L, M, q, lo, hi, 0, classes)

    sums = {}
    with ThreadPoolExecutor(WORKERS) as ex:
        for key, (t, h) in ex.map(one, jobs):
            acc = sums.setdefault(key, [0, {}])
            acc[0] += t
            for m, n in h.items():
                acc[1][m] = acc[1].get(m, 0) + n
    for L, M in TORI:
        equal_all = True
        for R in BENDING:
            row = frozen[(R, L, M)]
            for q in TWISTS:
                total, hist = sums[(R, L, M, q)]
                t = row["twists"][q]
                obs = {int(m): n for m, n in t["patterns"].items()}
                obs[0] = obs.get(0, 0) + t["sat"]
                if total != t["total"]:
                    fails.append(f"total {R} {L}x{M} {q}: {total} against {t['total']}")
                equal = hist == obs
                equal_all &= equal
                if not equal:
                    diff = {m: (hist.get(m, 0), obs.get(m, 0)) for m in set(hist) | set(obs) if hist.get(m, 0) != obs.get(m, 0)}
                    mismatches.append({"R": R, "torus": f"{L}x{M}", "twist": q, "configurations differing": sum(abs(a - b) for a, b in diff.values()) // 2,
                                       "patterns": {str(m): list(v) for m, v in sorted(diff.items())[:20]}})
                    if R in NO_CHOICES and (L, M) == (3, 3):
                        fails.append(f"placement {R} without choices differs on 3 x 3 in twist {q}")
                rec = {"R": R, "L": L, "M": M, "twist": q, "classes": row["classes"], "total": total, "equal": equal,
                       "simple_cycle_histogram": {str(m): n for m, n in sorted(hist.items())},
                       "frozen_histogram": {str(m): n for m, n in sorted(obs.items())}}
                with open(rows_path, "a") as f:
                    f.write(json.dumps(rec, sort_keys=True) + "\n")
        summary[f"P{1 if (L, M) == (3, 3) else 2}_{L}x{M}_simple_cycles_match"] = equal_all
        print(f"{L}x{M}", "match" if equal_all else "differs", round(time.time() - started), flush=True)
    if fails:
        verdict = "invalid"
    elif all(summary.values()):
        verdict = "supported"
    else:
        verdict = "refuted"
    result = {"schema_version": 1, "experiment_id": contract["experiment_id"], "ticket": contract["ticket"],
              "evidence_stage": "confirmatory", "verdict": verdict, "controls_ok": not fails, "control_failures": fails,
              "summary": summary, "mismatches": mismatches, "rows": len(sums), "wall_seconds": round(time.time() - started, 1),
              "workers": WORKERS}
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("controls_ok", "verdict", "wall_seconds", "summary")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
