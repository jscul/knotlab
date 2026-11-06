#!/usr/bin/env python3
"""Producer of PATTERN-3D-20261025-001B-E001 (complete censuses of counting laws on three and four labels).

census.c decides, for every rule in a range, whether its pure counting law satisfies the ordered 2-3 and 1-4 identities with
constants lam, mu >= 1 (see the header of census.c). Parts, each split into chunks run on 24 processes:
- rel2: all 2^8 triangle relations on two labels (control part);
- tab3: all 3^9 multiplication tables on three labels;
- rel3: all 2^27 triangle relations on three labels, 32 chunks;
- tab4: all 4^16 multiplication tables on four labels, 96 chunks.
Rows (one per chunk, with the census statistics and every survivor) are appended to rows.jsonl as chunks finish; summarize()
reduces every survivor to its triangles lying in allowed tetrahedra, classifies it and writes result.json.

    python3 -B run.py            run everything (skips chunks already in rows.jsonl), then summarize
    python3 -B run.py --summarize
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from multiprocessing import Pool

from common import A, OUT, build_binary, canon, classify_reduced, decode_relation, decode_table, run_census

PARTS = [("rel", 2, 1), ("tab", 3, 1), ("rel", 3, 32), ("tab", 4, 96)]
SEVEN = {"one constant", "two constants", "three constants", "Z2", "Z3", "free on 2 labels", "free on 3 labels"}
FIVE = {"one constant", "two constants", "pair groupoid", "Z4", "Z2xZ2"}


def chunks():
    for mode, n, k in PARTS:
        total = 2 ** (n ** 3) if mode == "rel" else n ** (n * n)
        step = -(-total // k)
        for i in range(k):
            yield (mode, n, i, i * step, min(total, (i + 1) * step))


def work(args):
    exe, (mode, n, i, s, e) = args
    t0 = time.time()
    surv, stats = run_census(exe, mode, n, s, e)
    return {"part": f"{mode}{n}", "chunk": i, "start": s, "end": e, "stats": stats, "survivors": surv,
            "seconds": round(time.time() - t0, 1)}


def summarize():
    rows = [json.loads(l) for l in (OUT / "rows.jsonl").read_text().splitlines()]
    expected = {(f"{m}{n}", i) for m, n, i, _, _ in chunks()}
    have = {(r["part"], r["chunk"]) for r in rows}
    complete = expected <= have
    parts = {}
    for p in sorted({r["part"] for r in rows}):
        rs = [r for r in rows if r["part"] == p]
        stats = Counter()
        for r in rs:
            stats.update(r["stats"])
        n = int(p[-1])
        names, orbits, bad, lam_mu = Counter(), set(), [], Counter()
        for r in rs:
            for idx, lam, mu in r["survivors"]:
                R = decode_relation(idx, n) if p.startswith("rel") else decode_table(idx, n)
                Rr = A.reduced(R)
                name, ok = classify_reduced(Rr, n, lam, mu)
                names[str(name)] += 1
                lam_mu[f"{lam},{mu}"] += 1
                if p.startswith("rel"):
                    orbits.add(canon(Rr, n))
                if not ok:
                    bad.append([idx, lam, mu])
        parts[p] = {"rules": sum(r["end"] - r["start"] for r in rs), "stats": dict(stats), "survivors by type": dict(names),
                    "survivors by (lam, mu)": dict(lam_mu), "reduced orbits": len(orbits) if p.startswith("rel") else None,
                    "survivors not a groupoid pullback matching (lam, mu)": bad[:20], "count not matching": len(bad)}
    controls = json.loads((OUT / "controls.json").read_text()) if (OUT / "controls.json").exists() else {"all_pass": False}
    pr = {}
    r2, t3, r3, t4 = (parts.get(k, {}) for k in ("rel2", "tab3", "rel3", "tab4"))
    pr["P1_relations_three_labels"] = (r3.get("count not matching") == 0 and set(r3.get("survivors by type", {})) == SEVEN
                                       and r3.get("reduced orbits") == 7)
    pr["P2_tables_four_labels"] = (t4.get("count not matching") == 0 and set(t4.get("survivors by type", {})) == FIVE
                                   and all(k.startswith("1,") for k in t4.get("survivors by (lam, mu)", {})))
    pr["P3_small_parts"] = (r2.get("survivors by type") == {"one constant": 4, "two constants": 1, "Z2": 2, "free on 2 labels": 1}
                            and t3.get("survivors by type") == {"Z3": 3} and r2.get("count not matching") == 0
                            and t3.get("count not matching") == 0)
    if not complete or not controls.get("all_pass"):
        verdict = "invalid" if not controls.get("all_pass") else "incomplete"
    else:
        verdict = "supported" if all(pr.values()) else "refuted: " + ", ".join(k for k, v in pr.items() if not v)
    result = {"schema_version": 1, "experiment_id": "PATTERN-3D-20261025-001B-E001", "evidence_stage": "confirmatory",
              "complete": complete, "controls_pass": controls.get("all_pass"), "parts": parts, "predictions": pr, "verdict": verdict}
    (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "parts"}, indent=1))
    return result


def main():
    if "--summarize" in sys.argv:
        summarize()
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    rows_path = OUT / "rows.jsonl"
    done = set()
    if rows_path.exists():
        done = {(json.loads(l)["part"], json.loads(l)["chunk"]) for l in rows_path.read_text().splitlines()}
    exe = build_binary()
    todo = [c for c in chunks() if (f"{c[0]}{c[1]}", c[2]) not in done]
    todo.sort(key=lambda c: (c[0] != "tab" or c[1] != 4,))  # long table chunks first
    t0 = time.time()
    with Pool(24) as pool, rows_path.open("a") as f:
        for row in pool.imap_unordered(work, [(exe, c) for c in todo]):
            f.write(json.dumps(row) + "\n")
            f.flush()
    print(f"census done in {time.time() - t0:.0f} s")
    summarize()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
