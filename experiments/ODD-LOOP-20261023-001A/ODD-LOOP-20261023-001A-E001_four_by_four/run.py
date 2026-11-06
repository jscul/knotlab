#!/usr/bin/env python3
"""Producer for ODD-LOOP-20261023-001A-E001: exact counts of the odd-loop identity by exhaustive enumeration.

Every orientation of each torus in the frozen roster is enumerated by enumx.c (compiled here with gcc -O2) in chunks of the bit-mask
range, run on worker threads. Each finished torus is appended to raw_rows.jsonl; result.json evaluates the frozen rule. The
enumeration is deterministic: there are no seeds.

    python3 -B run.py    writes raw_rows.jsonl (torus by torus) and result.json under artifacts/
"""

from __future__ import annotations

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
OUT = ROOT / "artifacts" / "ODD-LOOP-20261023-001A" / HERE.name
WORKERS = min(24, os.cpu_count() or 1)
SECTORS = ((0, 0), (1, 0), (0, 1), (1, 1))
ROSTER = [("F_check", 3, 3, 0), ("F_check", 3, 3, 1),
          ("F_small", 4, 3, 0), ("F_small", 4, 3, 1), ("F_small", 4, 3, 2), ("F_small", 3, 4, 0), ("F_small", 3, 4, 1),
          ("F_five", 5, 3, 0), ("F_five", 5, 3, 1), ("F_five", 5, 3, 2),
          ("F_four", 4, 4, 0), ("F_four", 4, 4, 1), ("F_four", 4, 4, 2)]


def parse(out):
    return {k: int(v) for k, v in (t.split("=") for t in out.split()[1:])}


def enumerate_torus(binary, Lh, Lv, s):
    total = 1 << (2 * Lh * Lv)
    pieces = WORKERS * (4 if total >= 1 << 30 else 1)
    step = -(-total // pieces)
    ranges = [(i * step, min(total, (i + 1) * step)) for i in range(pieces) if i * step < total]

    def one(r):
        return parse(subprocess.run([binary, str(Lh), str(Lv), str(s), str(r[0]), str(r[1])],
                                    capture_output=True, text=True, check=True).stdout)

    with ThreadPoolExecutor(WORKERS) as ex:
        parts = list(ex.map(one, ranges))
    tot = {}
    for d in parts:
        for k, v in d.items():
            tot[k] = tot.get(k, 0) + v
    assert tot["n"] == total
    return tot


def lines_of(row, q):
    return {tuple(map(int, k.split(","))): v for k, v in row[f"lines{q}"].items()}


def odd_under(cls, p):
    return (cls[0] * p[0] + cls[1] * p[1]) & 1


def analyse(rows):
    tests, per_row = [], []
    for r in rows:
        lines = {q: lines_of(r, q) for q in range(4)}
        classes = sorted(set().union(*(lines[q].keys() for q in (1, 2, 3))))
        rec = {"label": r["label"], "comparisons": []}
        for cls in classes:
            qs = [q for q in (1, 2, 3) if odd_under(cls, SECTORS[q])]
            assert len(qs) == 2
            a, b = (lines[qs[0]].get(cls, 0), lines[qs[1]].get(cls, 0))
            rec["comparisons"].append({"class": list(cls), "sectors": [list(SECTORS[qs[0]]), list(SECTORS[qs[1]])], "counts": [a, b],
                                       "equal": a == b})
            tests.append(a == b)
        per_row.append(rec)
    return {"rows": per_row, "comparisons": len(tests), "all_equal": all(tests), "differences": sum(not t for t in tests)}


def controls(rows):
    fails = []
    for r in rows:
        n = r["orientations"]
        for q in range(4):
            wind = sum(r[f"lines{q}"].values())
            if r[f"contractible{q}"] + r[f"cross{q}"] + wind != n:
                fails.append(f"totals {r['label']} sector {q}")
        for q in (1, 2, 3):
            if r[f"mis{q}"]:
                fails.append(f"test disagreement {r['label']} sector {q}")
            if r[f"contractible{q}"] != r[f"cross{q}"]:
                fails.append(f"exact duality {r['label']} sector {q}")
        if r["mis0"] or r["inv0"]:
            fails.append(f"untwisted sector flagged {r['label']}")
    return fails


def main() -> int:
    contract = json.loads((HERE / "contract.json").read_text())
    assert contract["status"] == "Frozen" and contract["evidence_stage"] == "confirmatory"
    OUT.mkdir(parents=True, exist_ok=True)
    raw = OUT / "raw_rows.jsonl"
    if raw.exists():
        raw.unlink()
    started = time.time()
    build = Path(tempfile.mkdtemp(prefix="enumx-"))
    binary = str(build / "enumx")
    subprocess.run(["gcc", "-O2", "-o", binary, str(HERE / "enumx.c")], check=True)
    gcc = subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    rows = []
    try:
        for fam, Lh, Lv, s in ROSTER:
            t = enumerate_torus(binary, Lh, Lv, s)
            row = {"family": fam, "label": f"{Lh}x{Lv} s={s}", "Lh": Lh, "Lv": Lv, "s": s, "orientations": t["n"]}
            for q in range(4):
                row[f"contractible{q}"], row[f"cross{q}"] = t[f"c{q}"], t[f"x{q}"]
                row[f"inv{q}"], row[f"mis{q}"] = t[f"inv{q}"], t[f"mis{q}"]
                row[f"lines{q}"] = {k.split(":")[1]: v for k, v in t.items() if k.startswith(f"w{q}:")}
            rows.append(row)
            with open(raw, "a") as f:
                f.write(json.dumps(row, sort_keys=True) + "\n")
            print(fam, row["label"], row["orientations"], round(time.time() - started), flush=True)
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
        result["identity"] = a
        result["verdict"] = "supported" if a["all_equal"] else "refuted"
    result["wall_seconds"] = round(time.time() - started, 1)
    result["max_rss_mib"] = round(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024, 1)
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("controls_ok", "verdict", "wall_seconds") if k in result}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
