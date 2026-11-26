"""Reconstruct the planned order and the per-job prefixes of the take census."""
import argparse
from collections import Counter
import json
from pathlib import Path
import random
import sys

from archive import records

STUDY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STUDY.parent / "SWITCH-RECEIVERS-20261126-001"))
import receivers


def audit(jobs):
    roster = receivers.register()
    chosen = [roster[i][0] for i in sorted(random.Random(20261126).sample(range(len(roster)), 100))]
    takes = [("MET", "OLDEST"), ("MET", "NEWEST"), ("MET-SOLE", None),
             ("STEPS1-SOLE", None), ("STEPS2-SOLE", None)]
    rows = list(records(STUDY / "takes_runs.jsonl.gz"))
    successes = [(r["A"], r["B"], *r["law"][1:]) for r in rows if "law" in r]
    failed = {tuple(r["job"]): r for r in rows if "job" in r}
    accounted = set()
    unexplained_jobs = []
    missing_interrupted = 0
    missing = Counter()
    reasons = Counter()
    for start in range(0, 2 * jobs, 2):
        interval = (start, start+2)
        names = chosen[start:start+2]
        planned = [(a, b, take, choice) for a in names for b in receivers.SENDERS for take, choice in takes]
        actual = [k for k in successes if k[0] in names]
        if interval in failed:
            count = failed[interval]["lines read"]
            missing_interrupted += len(planned) - count
        elif actual:
            count = len(planned)
        else:
            unexplained_jobs.append(interval)
            count = 0
        assert actual == planned[:count]
        accounted.update(planned[:count])
        for _, _, take, choice in planned[count:]:
            missing[choice or take] += 1
        if interval in failed:
            reasons[failed[interval]["not run"]] += 1
    if jobs == 50:
        assert len(accounted) == len(successes) and len(failed) == sum(reasons.values())
    return dict(jobs=jobs,planned=jobs*50,completed=len(accounted),missing_by_setting=missing,
                interrupted_jobs=reasons, missing_in_interrupted_jobs=missing_interrupted,
                no_rows_or_job_record=unexplained_jobs, receivers_with_record=len({k[0] for k in accounted}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, choices=range(1,51), default=50)
    print(json.dumps(audit(parser.parse_args().jobs), indent=2))
