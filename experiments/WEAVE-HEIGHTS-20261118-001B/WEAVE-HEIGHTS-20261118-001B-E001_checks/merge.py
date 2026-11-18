"""Merge WEAVE-HEIGHTS-B1 and score Q1-Q7.   .venv/bin/python -B merge.py <runner out dir>"""
import json
import sys
from pathlib import Path

ART = Path(__file__).resolve().parents[3] / "artifacts/WEAVE-HEIGHTS-20261118-001B/WEAVE-HEIGHTS-20261118-001B-E001_checks"
KEYS = ("discs", "flag_fail", "convex_fail", "triangle_fail", "level_knots", "dd_fail", "lone_fail", "states_vs_omega_fail", "omega_checked",
        "criterion_sets", "criterion_fail", "bonded_pairs", "below_bound")


def main(rundir):
    res = {}
    for line in open(Path(rundir) / "results.jsonl"):
        r = json.loads(line)
        res[r["case"]] = r
    failed = sorted(c for c, r in res.items() if r["status"] != "ok")
    ok = [r["result"] for r in res.values() if r["status"] == "ok"]
    tot = {k: sum(v.get(k, 0) for v in ok) for k in KEYS}
    by_k = {}
    for v in ok:
        by_k[v["k"]] = by_k.get(v["k"], 0) + v["discs"]
    pred = {
        "Q1": tot["omega_checked"] > 0 and tot["states_vs_omega_fail"] == 0,
        "Q2": tot["criterion_sets"] > 0 and tot["criterion_fail"] == 0,
        "Q3": tot["flag_fail"] == 0,
        "Q4": tot["convex_fail"] == 0 and tot["triangle_fail"] == 0,
        "Q5": tot["level_knots"] == 0,
        "Q6": tot["dd_fail"] == 0 and tot["lone_fail"] == 0,
        "Q7": tot["bonded_pairs"] > 0 and tot["below_bound"] == 0,
    }
    out = {"failed_cases": failed, "cases": len(res), "totals": tot, "discs_by_knots": by_k,
           "predictions": {k: ("held" if v else "failed") for k, v in pred.items()}}
    ART.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(ART / "results.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
