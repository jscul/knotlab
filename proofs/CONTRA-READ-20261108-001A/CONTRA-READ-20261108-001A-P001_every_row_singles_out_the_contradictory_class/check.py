#!/usr/bin/env python3
"""Checks for CONTRA-READ-20261108-001A: every row of creation between glue lines singles out the contradictory class, on the 8- and
10-line trisum glues.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 8 processes."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import contra_lib as CL  # noqa: E402

CL.TR.engine()
SEEDS = [3, 6]
RUNS = CL.PL.SW.generate(SEEDS, 0)
GLUES = {s: CL.Glue(s, RUNS[s]) for s in SEEDS}
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:3000], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def row_task(job):
    s, a, m = job
    return GLUES[s].row(a, m)


def count_task(job):
    s, m = job
    return len(GLUES[s].solutions(m))


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved",
          not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})

    with Pool(8) as pool:
        counts = {s: pool.map(count_task, [(s, m) for m in range(GLUES[s].N)], chunksize=64) for s in SEEDS}
    pf = {s: GLUES[s].mask_of(GLUES[s].minimal) for s in SEEDS}
    unsat = {s: [m for m in range(GLUES[s].N) if counts[s][m] == 0] for s in SEEDS}
    check("1 the contradictory class: on the 8-line glue (seed 3) and the 10-line glue (seed 6), exactly one switching class of signings "
          "has no solution, the class of the generator's Pfaffian signing, whose plain edge-atom spaces are three-fold",
          all(unsat[s] == [pf[s]] for s in SEEDS),
          {str(s): {"lines": GLUES[s].g, "classes": GLUES[s].N, "classes without solutions": len(unsat[s])} for s in SEEDS})

    jobs, keys = [], []
    for s in SEEDS:
        G = GLUES[s]
        for a in range(G.g):
            reps = {}
            for m in range(G.N):
                reps.setdefault(G.restr(a, m), m)
            for r, m in reps.items():
                jobs.append((s, a, m))
                keys.append((s, a, r))
    with Pool(8) as pool:
        res = pool.map(row_task, jobs, chunksize=8)
    R = {k: v for k, v in zip(keys, res)}
    per_line, single, ties = {}, True, True
    for s in SEEDS:
        G = GLUES[s]
        out = []
        for a in range(G.g):
            mine = G.restr(a, pf[s])
            target, tied = R[(s, a, mine)]
            sharing = [r for (s2, a2, r), (row, t) in R.items() if s2 == s and a2 == a and row == target]
            tied_classes = [r for (s2, a2, r), (row, t) in R.items() if s2 == s and a2 == a and t]
            single &= sharing == [mine]
            ties &= tied and tied_classes == [mine]
            out.append(len(sharing))
        per_line[str(s)] = out
    check("2 every single row singles out the contradictory class: for every line a of both glues, among the rows of all switching "
          "classes of the glue without a (128 on the 8-line glue, 512 on the 10-line), only the contradictory class's restriction has its "
          "row; and in the glue without a, line a's three points are tied (two complementary patterns) for that restriction and for no "
          "other class",
          single and ties, {"classes sharing the row, per line": per_line, "rows computed": len(jobs)})

    junction, partner_null = {}, True
    for s in SEEDS:
        G = GLUES[s]
        jl = []
        for a in range(G.g):
            others = [b for b in range(G.g) if b != a]
            mine = G.restr(a, pf[s])
            target = R[(s, a, mine)][0]
            nulls = lambda row: {others[i] for i, x in enumerate(row) if x is None}  # noqa: E731
            partner_null &= all(target[others.index(b)] is None for b in G.partners(a))
            if not G.partners(a):
                same = [r for (s2, a2, r), (row, t) in R.items() if s2 == s and a2 == a and nulls(row) >= nulls(target)]
                jl.append({"line": a, "classes whose degenerate entries include its own": len(same)})
        junction[str(s)] = jl
    check("3 how the rows read it: in the contradictory class's row at a, every line sharing two points with a is degenerate (two of its "
          "points are tied), and at every line that shares two points with no other line, the degenerate entries alone single the class "
          "out",
          partner_null and all(x["classes whose degenerate entries include its own"] == 1 for v in junction.values() for x in v)
          and all(len(v) > 0 for v in junction.values()),
          {"lines sharing two points with no other line": junction})

    OUT["seconds"] = round(time.time() - T0, 1)
    print("ALL OK", OUT["seconds"], "s")
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed", "claim": manifest["claim"],
              "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
    text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
