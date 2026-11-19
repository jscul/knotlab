"""Shared-runner job: the referee's table read to distance 8 (referee_meet.table8) for every meet-once grown stage of 15 to 40
junctions, as rebuilt by the referee's engine (runs/referee-meet-once-pop, from GROWN-PAIR-R1's job_meetonce.py with --param
lo=15 --param hi=40 --param notable=1).  For stages of at most 18 junctions, the table is also checked against the referee's full
shore table (CENSUS-READ-R1), entry by entry for every entry of at most nine.

  .venv/bin/python -B scripts/longrun.py launch research/MEET-ONCE-20261119-001/referee-R1/job_meet_tables.py \\
      --out runs/referee-meet-once-tables --unit referee-meet-once-tables --workers 6 --case-timeout 3600 --case-mem 2G \\
      --mem-max 16G
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
for p in ("research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1", "research/CENSUS-READ-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
STAGES = []


def setup(params):                                     # --param src=runs/referee-meet-once-past for 14 and 41 to 50 junctions
    for line in open(ROOT / params.get("src", "runs/referee-meet-once-pop") / "results.jsonl"):
        STAGES.extend(json.loads(line)["result"]["stages"])
    STAGES.sort(key=lambda s: (s["index"], s["round"]))


def cases():
    for k, s in enumerate(STAGES):
        yield f"s{k:04d}", s


def run(case_id, s):
    import time
    import referee_meet as RM
    labels = sorted({b for st in s["stars"] for b in st})
    idx = {b: i for i, b in enumerate(labels)}
    stars = [sorted(idx[b] for b in st) for st in s["stars"]]
    nb = len(labels)
    t0 = time.time()
    t = RM.table8(stars)
    out = {"index": s["index"], "round": s["round"], "junctions": len(stars), "distinctions": nb, "stars": stars,
           "closed": all(sum(b in st for st in stars) == 2 for b in range(nb)),
           "table8": [[a, b, d] for (a, b), d in sorted(t.items())], "invariant": RM.invariant(nb, t),
           "seconds": round(time.time() - t0, 2)}
    if len(stars) <= 18:
        import referee_census as RC
        import referee_f as F
        K, lab = RC.shore_table(stars)
        full = {(a, b): int(K[a][b]) for a in range(nb) for b in range(a + 1, nb) if K[a][b] < F.INF and K[a][b] <= 9}
        out["equals the full shore table at <= 9"] = full == t
    return out
