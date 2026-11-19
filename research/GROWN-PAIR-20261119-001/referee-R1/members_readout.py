"""Readout of job_members.py (runs/referee-grown-members): the full membership of the 152 other-state groups.

  ../../../.venv/bin/python -B members_readout.py > referee_grown_members.json
"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main():
    rows = {}
    for line in open(ROOT / "runs/referee-grown-members/results.jsonl"):
        r = json.loads(line)
        rows[r["case"]] = r["result"] if r["status"] == "ok" else {"error": r["status"]}
    ok = [x for x in rows.values() if "error" not in x]
    print(json.dumps({
        "groups": len(rows), "cases not ok": sorted(c for c, x in rows.items() if "error" in x),
        "grown stages carrying the groups' study table hashes": sum(x["stages in the hash bucket"] for x in ok),
        "... of these, table not isometric (hash collision)": sum(x["not isometric (hash collision)"] for x in ok),
        "state groups per table group": dict(Counter(x["state groups"] for x in ok)),
        "starts per state group (sorted), by count of groups": {str(k): v for k, v in sorted(
            Counter(tuple(sorted(x["stages per state group"])) for x in ok).items())},
        "groups with one start in two state groups": sum(bool(x["starts in two state groups"]) for x in ok),
        "undecided searches": sum(x["undecided searches"] for x in ok),
        "by group": rows}, indent=1))


if __name__ == "__main__":
    main()
