"""Readout of the referee's THREE-WAY check: job_three.py (runs/referee-three-way) and the one-size-past runs
(runs/referee-three-way-past, -past-groups, -past-triples).

  ../../../.venv/bin/python -B three_readout.py > referee_three.json
"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def rows(run):
    return {(r := json.loads(line))["case"]: r for line in open(ROOT / "runs" / run / "results.jsonl")}


def main():
    R = rows("referee-three-way")
    bad = sorted(c for c, r in R.items() if r["status"] != "ok")
    X = {c: r["result"] for c, r in R.items() if r["status"] == "ok"}
    six = [X[c] for c in sorted(X) if c.startswith("six")]
    stage = {c[len("stage-"):]: X[c] for c in sorted(X) if c.startswith("stage")}
    und = [X[c] for c in sorted(X) if c.startswith("und")]
    grown = [X[c] for c in sorted(X) if c.startswith("grown")]
    gp = [p for x in grown for p in x["pairs"]]
    past_stages = Counter()
    for line in open(ROOT / "runs/referee-three-way-past/results.jsonl"):
        for s in json.loads(line)["result"]["stages"]:
            past_stages[len(s["stars"])] += 1
    pg = []
    for line in open(ROOT / "runs/referee-three-way-past-groups/results.jsonl"):
        pg += json.loads(line)["result"]["table groups"]
    pt = [r["result"] for r in rows("referee-three-way-past-triples").values() if r["status"] == "ok"]
    recs = {}
    for run in ("unique-table", "unique-table-amend2"):
        for c, r in rows(run).items():
            if c not in recs or r["status"] == "ok":
                recs[c] = r
    A = {c: r["result"] for c, r in rows("referee-three-way-527").items() if r["status"] == "ok"}
    all527 = {"stages done (run stopped part way)": len(A),
              "(study's pair forcing spans, referee's pairs only spans, referee's pairs and triples span)": {
                  str(k): v for k, v in Counter((recs[c]["result"]["forced_spans_C"], x["pairs only spans"],
                                                 x["pairs and triples span"]) for c, x in A.items()).items()},
              "every forced word a bond": sum(x["every forced word a bond"] for x in A.values()),
              "not spanned with triples": sorted(c for c, x in A.items() if not x["pairs and triples span"])}
    ptp = [p for x in pt for p in x["pairs"]]
    print(json.dumps({
        "cases not ok": bad,
        "six: rivals": len(six),
        "six: regrown truth = recorded truth": sum(x["regrown truth = recorded truth (isomorphic)"] for x in six),
        "six: pairs differing on the same names (max)": max(x["pairs differing on the same names"] for x in six),
        "six: triples differing on the same names (min, max)": [min(x["triples differing on the same names"] for x in six),
                                                                 max(x["triples differing on the same names"] for x in six)],
        "six: triples no bond holds, truth (min, max)": [min(x["triples no bond holds (truth, rival)"][0] for x in six),
                                                          max(x["triples no bond holds (truth, rival)"][0] for x in six)],
        "six: a renaming keeps pairs (control)": sum(x["a renaming keeps pairs (control)"] is True for x in six),
        "six: a renaming keeps pairs and triples": dict(Counter(str(x["a renaming keeps pairs and triples"]) for x in six)),
        "the six stages: same-states rivals within the bound": {c: x["same-states rivals within the bound"] for c, x in stage.items()},
        "undecided: stages": len(und),
        "undecided: pairs only, forcing spans": sum(x["pairs only: forced, spans"][1] for x in und),
        "undecided: pairs and triples, forcing spans": sum(x["pairs and triples: forced, spans"][1] for x in und),
        "undecided: every forced word a bond of the truth": sum(x["every forced word a bond of the truth"] for x in und),
        "undecided: with a same-states rival within the bound": sum(x["same-states rivals within the bound"] > 0 for x in und),
        "undecided: same-states search capped": sum(x["capped"] for x in und),
        "grown: groups": len(grown),
        "grown: state groups per group": dict(Counter(x["state groups"] for x in grown)),
        "grown: bond pair table = shore table": sum(x["bond pair table = shore table"] for x in grown),
        "grown: pairs of state groups": len(gp),
        "grown: a renaming keeps pairs": sum(p["pairs kept by a renaming"] is True for p in gp),
        "grown: a renaming keeps pairs and triples": dict(Counter(str(p["pairs and triples kept by a renaming"]) for p in gp)),
        "one size past: grown stages of 15 and 16 junctions": dict(sorted(past_stages.items())),
        "one size past: table groups of two or more arrangements": len(pg),
        "one size past: ... same states / other states": [sum(g["state groups"] == 1 for g in pg), sum(g["state groups"] > 1 for g in pg)],
        "one size past: other-states groups with an arrangement meeting once": sum(any(x["meet once"]) for x in pt),
        "one size past: other-states pairs, a renaming keeps pairs": sum(p["pairs kept by a renaming"] is True for p in ptp),
        "one size past: other-states pairs, a renaming keeps pairs and triples": dict(Counter(str(p["pairs and triples kept by a renaming"]) for p in ptp)),
        "forcing on the 527 (extra)": all527,
        "detail": {"six": six, "undecided": und, "one size past": pt}}, indent=1))


if __name__ == "__main__":
    main()
