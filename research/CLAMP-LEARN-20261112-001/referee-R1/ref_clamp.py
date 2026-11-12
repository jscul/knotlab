#!/usr/bin/env python3
"""Referee CLAMP-LEARN-R1 (lean, as asked): the restricted blind chance and medians from result_baselines.json's own shares, the
consistency rule read from check.py, the tallies and step sums from runs.jsonl, each rule's steps per second on found runs (what the
five-minute cap means in steps), and the walk's shares. No regeneration.

    python3 -B ref_clamp.py      (writes result_clamp.json)"""
import json
import math
import statistics as st
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = HERE.parents[2] / "proofs" / "CLAMP-LEARN-20261112-001A" / "CLAMP-LEARN-20261112-001A-P001_a_clamped_phase"


def blind_median(p):
    return 1 if p >= 1 else math.ceil(math.log(0.5) / math.log(1 - p))


def main():
    base = json.loads((D / "result_baselines.json").read_text())["checks"]["result"]
    out = {"baselines": {}}
    for k, b in base.items():
        pr = b["p uniform"] / b["share consistent with the positive examples"]
        out["baselines"][k] = {"p restricted recomputed": pr, "matches": abs(pr - b["p restricted"]) < 1e-12,
                               "blind medians recomputed (uniform, restricted)": [blind_median(b["p uniform"]), blind_median(pr)],
                               "census": [b["blind median uniform"], b["blind median restricted"]]}
    rows = [json.loads(l) for l in (D / "runs.jsonl").read_text().splitlines() if l.strip()]
    tally = {}
    for key in sorted({(r["rule"], r["target"]) for r in rows}):
        rr = [r for r in rows if (r["rule"], r["target"]) == key]
        f = [r for r in rr if r.get("found")]
        dropped = [r for r in rr if r.get("dropped (time cap)")]
        unf_budget = [r for r in rr if not r.get("found") and not r.get("dropped (time cap)")]
        rate = [r["all steps"] / r["seconds"] for r in f if r["seconds"] > 1]
        tally["%s / %s" % key] = {"runs": len(rr), "found": len(f), "dropped at the 300 s cap": len(dropped),
                                  "unfound at the step budget": len(unf_budget),
                                  "found flag equals map == target": all(r["found"] == (r["map at the stop"] == r["target"]) for r in rr if "map at the stop" in r),
                                  "all steps = learning + wrong copy + probe walk": all(r["all steps"] == r["learning steps"] + r["wrong copy steps"] + r["probe walk steps"] for r in rr if "all steps" in r),
                                  "median steps per second (found runs)": round(st.median(rate)) if rate else None}
    out["runs"] = tally
    out["walk"] = json.loads((D / "result_walk.json").read_text())["checks"]["result"]
    (HERE / "result_clamp.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
