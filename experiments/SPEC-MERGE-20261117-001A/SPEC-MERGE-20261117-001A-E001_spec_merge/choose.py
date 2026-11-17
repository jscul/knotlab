"""Policy choice of SPEC-MERGE-20261117-001A, by the frozen score.

  python3 choose.py policy <policy dir> <policies.json>
A (tuned on rand-3200) and Aloc (tuned on local-w10-3200): the setting of least mean, over 8 tuning instances x 3 runs, of
log(W_setting) - log(W_NOV) from the same initial state; an unsolved run scores log(work at the cap) + log(1 + least violated
count); ties go to the first setting in grid order.
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
from longrun import load_results  # noqa: E402

import job  # noqa: E402


def score(run):
    s = math.log(run["work"])
    if not run["solved"]:
        s += math.log1p(max(0, run.get("minviol", 0)))
    return s


def main(d, out):
    recs = load_results(d)
    bad = [k for k, r in recs.items() if r.get("status") != "ok"]
    if bad:
        raise SystemExit(f"{len(bad)} cases not ok")
    res = [r["result"] for r in recs.values()]
    base = {(r["cell"], r["seed"], j): score(x) for r in res if r["k"] < 0 for j, x in enumerate(r["runs"])}
    acc = defaultdict(list)
    for r in res:
        if r["k"] >= 0:
            for j, x in enumerate(r["runs"]):
                acc[(r["cell"], r["k"])].append(score(x) - base[(r["cell"], r["seed"], j)])
    outd = {"_scores": {}}
    for arm, cell in (("A", "rand-3200"), ("Aloc", "local-w10-3200")):
        sc = {k: sum(v) / len(v) for (c, k), v in acc.items() if c == cell}
        assert len(sc) == len(job.GRID) and all(len(acc[(cell, k)]) == 24 for k in sc)
        best = min(sc.values())
        k = min(kk for kk, v in sc.items() if v == best)
        outd[arm] = job.GRID[k]
        outd["_scores"][arm] = {str(kk): round(v, 4) for kk, v in sorted(sc.items())}
        print(arm, k, job.GRID[k], round(best, 4))
    Path(out).write_text(json.dumps(outd, indent=1))


if __name__ == "__main__":
    main(sys.argv[2], sys.argv[3])
