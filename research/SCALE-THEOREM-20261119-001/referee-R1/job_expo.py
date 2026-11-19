"""Shared-runner job: the four in-class samples the theorem reads as exponential, grown by the referee's engine (the program's
rule) to round 30, with the ratio of successive counts.  The samples are read from runs/referee-scale-theorem (job_scale.py).

  .venv/bin/python -B scripts/longrun.py launch research/SCALE-THEOREM-20261119-001/referee-R1/job_expo.py \\
      --out runs/referee-scale-expo --unit referee-scale-expo --workers 4 --case-timeout 1800 --case-mem 3G --mem-max 16G
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import job_scale  # noqa: E402,F401  (sets the referee's paths)


def cases():
    for line in open(ROOT / "runs/referee-scale-theorem/results.jsonl"):
        r = json.loads(line)
        for i, counts, sizes, flat in r["result"]["exponential"]:
            yield f"{r['case']}-{i}", {"sizes": sizes, "flat": flat}


def run(case_id, p):
    import job_double as JD
    import job_relay as RL
    sizes, flat = p["sizes"], p["flat"]
    n = len(sizes)
    _, counts = RL.grow_keys(n, JD.data(sizes, flat)[1], list(sizes), 30, maxj=400000)
    num = [c for c in counts if isinstance(c, int)]
    return {"counts": counts, "ratios from round 20": [round(num[t] / num[t - 1], 4) for t in range(20, len(num))]}
