"""Readout of the referee's meet-once rebuild (job_meetonce.py, job_meetonce_groups.py, job_companion.py under scripts/longrun.py).

  ../../../.venv/bin/python -B meetonce_readout.py > referee_grown_meetonce.json
"""
import gzip
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "artifacts/GROWN-PAIR-20261119-001A/GROWN-PAIR-20261119-001A-E001_pairs/results_grown-pair.jsonl.gz"


def main():
    mine = Counter()
    for line in open(ROOT / "runs/referee-grown-meetonce/results.jsonl"):
        for s in json.loads(line)["result"]["stages"]:
            mine[s["round"]] += 1
    theirs = Counter()
    for line in gzip.open(RES, "rt"):
        r = json.loads(line)
        if r.get("status") == "ok":
            for st in r["result"]["stages"]:
                if st["round"] > 0 and st["max_shared"] < 2:
                    theirs[st["round"]] += 1
    classes, groups = 0, []
    for line in open(ROOT / "runs/referee-grown-meetonce-groups/results.jsonl"):
        r = json.loads(line)["result"]
        classes += r["classes"]
        groups += r["table groups"]
    comp = [json.loads(line)["result"] for line in open(ROOT / "runs/referee-grown-companion/results.jsonl")]
    past = Counter()
    for line in open(ROOT / "runs/referee-grown-meetonce16/results.jsonl"):
        for s in json.loads(line)["result"]["stages"]:
            past[len(s["stars"])] += 1
    pgroups = []
    for line in open(ROOT / "runs/referee-grown-meetonce16-groups/results.jsonl"):
        pgroups += json.loads(line)["result"]["table groups"]
    print(json.dumps({
        "meet-once grown stages (rounds 1 to 8, at most 14 junctions), referee": sum(mine.values()),
        "... by round, referee": dict(sorted(mine.items())),
        "... by round, study's results (data)": dict(sorted(theirs.items())),
        "arrangement classes in buckets of two or more": classes,
        "table groups of two or more meet-once grown arrangements": len(groups),
        "... sizes": dict(Counter(g["arrangements"] for g in groups)),
        "... one state group (same states up to renaming)": sum(g["state groups"] == 1 for g in groups),
        "... two or more state groups": sum(g["state groups"] > 1 for g in groups),
        "... undecided searches": sum(g["undecided searches"] for g in groups),
        "groups whose table is also carried by a grown stage with two junctions sharing two (study hash, exact check)": comp,
        "one size past: meet-once grown stages of 15 and 16 junctions (rounds 1 to 8)": dict(sorted(past.items())),
        "... table groups of two or more": len(pgroups),
        "... one state group": sum(g["state groups"] == 1 for g in pgroups),
        "... two or more state groups": sum(g["state groups"] > 1 for g in pgroups),
        "... undecided searches": sum(g["undecided searches"] for g in pgroups),
        "groups": groups, "one size past: groups": pgroups}, indent=1))


if __name__ == "__main__":
    main()
