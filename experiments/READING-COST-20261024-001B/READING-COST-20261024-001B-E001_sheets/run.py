#!/usr/bin/env python3
"""Producer of READING-COST-20261024-001B-E001 (cover sheets for walls with choices).

For each placement, torus, non-fitting twist and chunk of sampled configurations:
- walls_sample (the wall graph and cycle test of walls.c, WALLS-WITH-CHOICES-20261024-001B-E001, unchanged) draws configurations
  uniformly and reports, for each, the odd classes that no simple cycle of the wall graph serves (predicted contradictions);
- each predicted contradiction is decided with PySAT: a strip of 12, 24 or 48 periods without an assignment certifies a
  contradiction; otherwise the cyclic covers with 1, 2, ..., 24 sheets are tried in order, and the first with an assignment gives
  the fewest sheets of a misjudged class; a strip of 96 periods is tried last; anything else is undetermined.
Rows are appended to rows.jsonl as chunks finish; result.json is written at the end by summarize().

    .venv/bin/python -B run.py            run everything (skips chunks already in rows.jsonl)
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts/READING-COST-20261024-001B/READING-COST-20261024-001B-E001_sheets"
ENGINE = OUT / "walls_sample"
_spec = importlib.util.spec_from_file_location(
    "dr_check", sorted((ROOT / "proofs/DIRECTIONAL-RIGIDITY-20261023-001B").glob("*/check.py"))[0])
DR = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(DR)

HONEYCOMB = (111, 125, 159, 215)     # honeycomb placements with a free place
DIRECTED = (62, 110, 155, 203)       # directed placements with a free place (controls)
CLASSES = [(1, 0), (0, 1), (1, 1), (1, -1), (1, 2), (2, 1), (1, -2), (2, -1), (1, 3), (3, 1), (3, -1), (3, 2), (4, 1)]
PLAN = {  # (L, M): (samples per twist for honeycomb placements, for directed placements, chunk size)
    (4, 4): (100000, 20000, 10000),
    (4, 5): (40000, 10000, 2500),
}
BASELINE_3X4 = {"misjudged": 9168, "predicted": 4009750}   # per honeycomb placement, exact, from the frozen 3 x 4 histograms


def jobs():
    out = []
    for (L, M), (n_h, n_d, chunk) in PLAN.items():
        for R in HONEYCOMB + DIRECTED:
            n = n_h if R in HONEYCOMB else n_d
            for q in ((0, 0), (0, 1), (1, 0), (1, 1)):
                if q in DR.fitting(R, L, M):
                    continue
                for k in range(n // chunk):
                    seed = int(hashlib.sha256(f"READING-COST-B:{R}:{L}x{M}:{q[0]}{q[1]}:{k}".encode()).hexdigest()[:15], 16)
                    out.append({"R": R, "L": L, "M": M, "q": q, "chunk": k, "samples": chunk, "seed": seed})
    return out


def solve(clauses):
    from pysat.solvers import Cadical153
    with Cadical153(bootstrap_with=clauses) as s:
        return s.solve()


def truth(R, L, M, q, x, c):
    for K in (12, 24, 48):
        if not solve(DR.clauses(R, L, M, q, x, c, K, False)[1]):
            return "contradiction", K
    for m in range(1, 25):
        if solve(DR.clauses(R, L, M, q, x, c, m, True)[1]):
            return "assignment", m
    if not solve(DR.clauses(R, L, M, q, x, c, 96, False)[1]):
        return "contradiction", 96
    return "undetermined", None


def run_chunk(job):
    R, L, M, q = job["R"], job["L"], job["M"], tuple(job["q"])
    t0 = time.time()
    out = subprocess.run([str(ENGINE), str(R), str(L), str(M), str(q[0]), str(q[1]), str(job["samples"]), str(job["seed"]), "0"]
                         + [str(v) for c in CLASSES for v in c], capture_output=True, text=True, check=True).stdout.split("\n")
    t1 = time.time()
    tally, sheets, misjudged = Counter(), Counter(), []
    oddmask = int(out[0].split()[3])
    tally["odd classes per configuration"] = bin(oddmask).count("1")
    for line in out[1:]:
        if not line:
            continue
        x, pattern = map(int, line.split())
        tally["configurations with a predicted contradiction"] += 1
        for k, c in enumerate(CLASSES):
            if pattern >> k & 1:
                tally["predicted contradictions"] += 1
                verdict, n = truth(R, L, M, q, x, c)
                tally[verdict] += 1
                if verdict == "assignment":
                    sheets[n] += 1
                    misjudged.append([x, list(c), n])
    return {**job, "q": list(q), "tally": dict(tally), "sheets": {str(k): v for k, v in sorted(sheets.items())},
            "misjudged": misjudged, "engine_seconds": round(t1 - t0, 1), "truth_seconds": round(time.time() - t1, 1)}


def summarize(rows):
    agg = {}
    for r in rows:
        key = (r["R"], f"{r['L']}x{r['M']}")
        a = agg.setdefault(key, Counter())
        a["samples"] += r["samples"]
        for k, v in r["tally"].items():
            if k != "odd classes per configuration":
                a[k] += v
        for k, v in r["sheets"].items():
            a[f"sheets {k}"] += v
    table = []
    for (R, torus), a in sorted(agg.items()):
        for k in ("predicted contradictions", "contradiction", "assignment", "undetermined",
                  "configurations with a predicted contradiction"):
            a[k] += 0   # zero counts are absent from a chunk's tally; record them explicitly
        pred = a["predicted contradictions"]
        table.append({"placement": R, "torus": torus, "kind": "honeycomb" if R in HONEYCOMB else "directed", **dict(sorted(a.items())),
                      "misjudged share": (a["assignment"] / pred) if pred else None})
    base = BASELINE_3X4["misjudged"] / BASELINE_3X4["predicted"]
    def share(rows_, R=None, torus=None):
        mis = sum(t["assignment"] for t in rows_ if (R is None or t["placement"] == R) and t["torus"] == torus and t["kind"] == "honeycomb")
        pred = sum(t["predicted contradictions"] for t in rows_ if (R is None or t["placement"] == R) and t["torus"] == torus and t["kind"] == "honeycomb")
        return mis, pred
    P1 = all(t["assignment"] == 0 for t in table if t["kind"] == "directed")
    P2 = all(t["assignment"] >= 1 for t in table if t["kind"] == "honeycomb")
    P3 = all((lambda mp: mp[1] > 0 and mp[0] / mp[1] > base)(share(table, R, "4x4")) for R in HONEYCOMB)
    m45, p45 = share(table, None, "4x5")
    P4 = p45 > 0 and m45 / p45 > base
    undetermined = sum(t.get("undetermined", 0) for t in table)
    return table, {"P1_directed_never_misjudged": P1, "P2_honeycomb_misjudged_on_both_tori": P2,
                   "P3_honeycomb_share_4x4_above_3x4_each": P3, "P4_honeycomb_share_4x5_above_3x4_pooled": P4,
                   "baseline_3x4_share": base, "pooled_4x5": [m45, p45], "undetermined": undetermined}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    if not ENGINE.exists() or ENGINE.stat().st_mtime < (HERE / "walls_sample.c").stat().st_mtime:
        subprocess.run(["gcc", "-O2", "-std=c99", "-o", str(ENGINE), str(HERE / "walls_sample.c")], check=True)
    rows_path = OUT / "rows.jsonl"
    done = set()
    if rows_path.exists():
        for line in rows_path.read_text().splitlines():
            r = json.loads(line)
            done.add((r["R"], r["L"], r["M"], tuple(r["q"]), r["chunk"]))
    todo = [j for j in jobs() if (j["R"], j["L"], j["M"], tuple(j["q"]), j["chunk"]) not in done]
    todo.sort(key=lambda j: -(j["L"] * j["M"] * (3 if j["R"] in HONEYCOMB else 1)))   # longest first
    t0 = time.time()
    with Pool(24) as pool, rows_path.open("a") as fh:
        for row in pool.imap_unordered(run_chunk, todo):
            fh.write(json.dumps(row, sort_keys=True) + "\n")
            fh.flush()
    rows = [json.loads(line) for line in rows_path.read_text().splitlines()]
    table, verdicts = summarize(rows)
    controls = json.loads((OUT / "controls.json").read_text()) if (OUT / "controls.json").exists() else {}
    controls_ok = bool(controls) and all(controls.values())
    if not controls_ok or not verdicts["P1_directed_never_misjudged"]:
        verdict = "invalid"
    elif verdicts["P2_honeycomb_misjudged_on_both_tori"] and verdicts["P3_honeycomb_share_4x4_above_3x4_each"] and \
            verdicts["P4_honeycomb_share_4x5_above_3x4_pooled"]:
        verdict = "supported"
    else:
        verdict = "refuted"
    result = {"schema_version": 1, "experiment_id": "READING-COST-20261024-001B-E001", "ticket": "READING-COST-20261024-001B",
              "evidence_stage": "confirmatory", "verdict": verdict, "summary": verdicts, "controls": controls,
              "table": table, "rows": len(rows), "wall_seconds_this_run": round(time.time() - t0, 1)}
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": verdict, "summary": verdicts}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
