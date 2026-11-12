#!/usr/bin/env python3
"""Referee LIFE-JUMPS-R1, part 1: J1 to J6 recomputed from the census's records (runs.jsonl) with the referee's own summary code
(no import of census.py or summary_fixed.py), against summary.json; the deviations (the merged file against the side units' files);
J4's baselines and censoring (density m / n, the share and the hazard, by AUC and by a censored concordance; positives split by end
time); J6 read against the records.

    python3 -B ref_records.py      (writes result_records.json)"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2] / "artifacts" / "LIFE-JUMPS-20261112-001A" / "LIFE-JUMPS-20261112-001A-E001_whole_lives"


def load(name):
    return [json.loads(l) for l in (ART / name).read_text().splitlines()]


def nearest_read(r, m):
    keys = [int(k) for k in r["reads"]]
    return r["reads"][str(min(keys, key=lambda x: abs(x - m)))]


def frac(r, f):
    return nearest_read(r, max(1, int(round(r["M"] * f))))


def lag(r, k):
    return r["reads"].get(str(r["knots"] - k))


def auc(pos, neg):
    if not pos or not neg:
        return None
    pos, neg = np.array(pos), np.array(neg)
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


def cindex(rows, key):
    """Harrell's concordance: pairs where one ends before the other's end or censoring; concordant if the earlier has the larger key"""
    num = den = 0.0
    for i in rows:
        for j in rows:
            if i is j or not i["dead"]:
                continue
            if i["knots"] < j["knots"] or (not j["dead"] and i["knots"] <= j["knots"]):
                den += 1
                num += 1.0 if key(i) > key(j) else (0.5 if key(i) == key(j) else 0.0)
    return num / den if den else None


def main():
    recs = load("runs.jsonl")
    by = defaultdict(list)
    for r in recs:
        by[r["label"]].append(r)
    out = {"growths": len(recs), "per setting": {k: len(v) for k, v in by.items()}}
    # J1
    out["J1"] = {lab: {"share <= 0.05 at 40 before": float(np.mean([lag(r, 40)["share"] <= 0.05 for r in by[lab] if lag(r, 40)])),
                       "share >= 0.5 at the last base": float(np.mean([lag(r, 1)["share"] >= 0.5 for r in by[lab]])),
                       "ended": sum(r["dead"] for r in by[lab])} for lab in ("U100", "U200", "U300")}
    out["J1b"] = {lab: float(np.median([lag(r, 10)["share"] for r in by[lab] if r["dead"] and lag(r, 10)])) for lab in ("U100", "U200", "U300")}
    G4 = ("X0.3", "X0.35", "Og0.3", "Ol0.3")
    j2 = {}
    for lab in G4:
        rs = [r for r in by[lab] if r["dead"] and r["knots"] >= 200]
        j2[lab] = {"ended after >= 200": len(rs), "class >= 10 and share >= 0.05 at half": float(np.mean([frac(r, 0.5)["largest"] >= 10 and frac(r, 0.5)["share"] >= 0.05 for r in rs]))}
    out["J2"] = j2
    out["J3"] = {lab: float(np.median([lag(r, 20)["share"] / lag(r, 1)["share"] for r in by[lab] if r["dead"] and lag(r, 20)]))
                 for lab in ("U100", "U200", "U300") + G4}
    # J4 with baselines
    j4 = {}
    for m in (300, 1000):
        alive = [r for r in by["X0.3"] if str(m) in r["reads"] and r["knots"] > m]
        pos = [r for r in alive if r["dead"]]
        neg = [r for r in alive if not r["dead"]]
        rd = lambda r, f: f(r["reads"][str(m)])
        preds = {"share": lambda x: x["share"], "hazard": lambda x: x["hazard"], "density m / n": lambda x: x["m"] / x["n"],
                 "largest class": lambda x: x["largest"], "tied distinctions": lambda x: x["tied"]}
        e = {"later end": len(pos), "still a base at 6,000": len(neg)}
        for name, f in preds.items():
            e["AUC " + name] = auc([rd(r, f) for r in pos], [rd(r, f) for r in neg])
            e["censored concordance " + name] = cindex(alive, lambda r, f=f: rd(r, f))
        late = [r for r in pos if r["knots"] > 3000]
        e["AUC share, positives ending after 3,000 only"] = auc([rd(r, preds["share"]) for r in late], [rd(r, preds["share"]) for r in neg])
        e["positives ending after 3,000"] = len(late)
        # share against density: partial association (rank of share within density terciles)
        dens = np.array([rd(r, preds["density m / n"]) for r in alive])
        lab_ = np.array([r["dead"] for r in alive])
        sh = np.array([rd(r, preds["share"]) for r in alive])
        strata = np.digitize(dens, np.quantile(dens, [1 / 3, 2 / 3]))
        within = []
        for s in range(3):
            idx = strata == s
            a = auc(list(sh[idx & lab_]), list(sh[idx & ~lab_]))
            within.append([int((idx & lab_).sum()), int((idx & ~lab_).sum()), a])
        e["AUC share within density terciles (pos, neg, AUC)"] = within
        j4[str(m)] = e
    out["J4"] = j4
    xs = [r["reads"]["6000"]["largest"] for r in by["X0.2"] if "6000" in r["reads"]]
    out["J5"] = {"runs reaching 6,000 knots": len(xs), "largest <= 15": float(np.mean([x <= 15 for x in xs])), "max": max(xs),
                 "still a base after 6,000 moves": sum(not r["dead"] for r in by["X0.2"])}
    out["J6"] = {lab: float(np.mean([lag(r, 1)["members_median_index"] < (r["n_end"] - 1) / 2 for r in by[lab]
                                     if r["dead"] and lag(r, 1).get("members_median_index") is not None])) for lab in G4}
    out["J6 median of (members' median index) / n_end"] = {lab: float(np.median([lag(r, 1)["members_median_index"] / r["n_end"] for r in by[lab]
                                                                                 if r["dead"] and lag(r, 1).get("members_median_index") is not None])) for lab in G4}
    # the census's summary
    summ = json.loads((ART / "summary.json").read_text())
    out["census summary predictions"] = summ["predictions"]
    # deviations: the side units' records against the merged file
    merged = {(r["label"], r["run"]): r for r in recs}
    dev = {}
    for name in ("runs_xo.jsonl", "runs_u.jsonl", "runs_u300.jsonl"):
        side = load(name)
        same = sum(1 for r in side if merged.get((r["label"], r["run"])) and {k: v for k, v in merged[(r["label"], r["run"])].items() if k != "seconds"} == {k: v for k, v in r.items() if k != "seconds"})
        dev[name] = {"records": len(side), "identical to the merged record (seconds aside)": same}
    out["deviations"] = dev
    (HERE / "result_records.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "census summary predictions"}, indent=1))


if __name__ == "__main__":
    main()
