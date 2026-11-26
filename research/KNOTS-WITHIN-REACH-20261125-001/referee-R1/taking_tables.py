"""Recount the knot-test prefix, the laws with takes, and changes under renaming."""
import argparse
import gzip
import json
import math
import time
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import islice
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = next((HERE.parents[2] / "artifacts").glob("KNOTS-WITHIN-REACH*/*knots_within_reach"))
KINDS = ["hs", "ps", "hs_two_holders", "weighted"]


def stream(stem, limit):
    with gzip.open(RAW / (stem + ".jsonl.gz"), "rt") as handle:
        yield from map(json.loads, islice(handle, limit))


def hub(row):
    reads = row["reads"]
    if "100" not in reads or "50" not in reads:
        return {"ended" if row["ended"] else "no comparison": 1}
    before, after = reads["50"], reads["100"]
    doubles = after["knots"] >= 2 * before["knots"]
    count = {"reached": 1, "doubles": int(doubles)}
    for kind in KINDS:
        changes = [v - u for u, v in zip(before["steps"][kind], after["steps"][kind], strict=True)]
        holds = max(changes) <= 2
        count["step condition " + kind] = int(holds)
        count["both " + kind] = int(doubles and holds)
    return count


def knot_prefix(limit):
    totals = defaultdict(Counter)
    forms = Counter()
    for row in stream("run3", limit):
        forms[row["source"]] += 1
        for law in ["nae", "parity"]:
            check = row[law]
            totals[law].update({k: v for k, v in check.items()
                                if k in ("tested", "untested", "direct_compared", "disagree")})
            totals[law]["failures"] += len(check["fails"])
            totals[law]["structures"] += 1
            totals[law]["total knot occurrences in final structures"] += (
                row["knots"] if law == "nae" else check["structure_knots"])
    # A design counterexample, independent of whether any actual knot fails.
    # 400 hypothetical failures in the 79,203 made knots of a single run,
    # with all other runs passing. Sampling is without replacement per run.
    model = None
    if limit is None:
        rows = [r for r in stream("run3", None) if r["start"]=="census:71" and r["law"]=="L4"]
        assert len(rows)==1
        row, = rows
        made = row["knots"]-4
        assert row["nae"]["tested"]==204 and row["parity"]["tested"]==204
        model = {"hypothetical failing made knots":400,"made knots in that one run":made,
                 "sample in the run":200,
                 "chance of missing all 400":math.prod(1-400/(made-i) for i in range(200)),
                 "overall failure shares by knot occurrences":{
                     law:400/count["total knot occurrences in final structures"] for law,count in totals.items()}}
    return {"by source": forms, "by knot law": totals, "pooled bound design counterexample":model}


def taking(limit):
    by_law, by_group, tests = (defaultdict(Counter) for _ in range(3))
    ranks, parity, hist, steps, by_method = (Counter() for _ in range(5))
    base_rows = {(r["start"], r["knot_law"], r["base"]): r for r in stream("run4_base", None)}
    smallest = []
    positive_ids = set()
    examples = {}
    ratio = []
    differences = []
    ties = Counter()
    for row in stream("run4", limit):
        law = row["law"]
        knot_law = row["knot_law"]
        group = "uniform" if int(law[1:]) <= 8 else "oldest"
        key = f"{law} {knot_law}"
        stats = hub(row)
        for counts in (by_law[key], by_group[group]):
            counts.update(stats)
            counts["rows"] += 1
        test = row["knot_test"]
        tests[knot_law].update({k: test[k] for k in ("tested", "untested", "disagree")})
        tests[knot_law]["failures"] += len(test["fails"])
        tests[knot_law]["runs with failures"] += bool(test["fails"])
        if row["knots_per_round"][1:] != [n+b for n,b in zip(row["knots_per_round"],row["births"])]:
            raise ValueError("birth totals inconsistent")
        base = "L6" if law in ("T1","T2","T3","T4","T9") else "L3"
        base_reads = base_rows[row["start"], knot_law, base]["reads"]
        for stage, record in row["reads"].items():
            assert record["knots"] == row["knots_per_round"][int(stage)]
            if stage in base_reads:
                by_method["matched stage"] += 1
                by_method["holder maxima differ from base"] += record["steps"]["hs"] != base_reads[stage]["hs"]
        if stats.get("reached"):
            r = row["reads"]
            hist.update(r["100"]["steps"]["holders_hist"])
            if group == "uniform":
                ratio.append(Fraction(r["100"]["knots"],r["50"]["knots"]))
                differences.append(max(v-u for u,v in zip(r["50"]["steps"]["hs"],r["100"]["steps"]["hs"])))
            for k in KINDS:
                if stats["both "+k] and k not in examples:
                    examples[k] = [row["start"], law, row["seed"], knot_law, r["50"]["knots"], r["100"]["knots"],
                                   r["50"]["steps"][k],r["100"]["steps"][k]]
        if knot_law != "parity":
            continue
        for stage, rule in row["lambda"].items():
            count = row["reads"][stage]["knots"]
            distribution = row["reads"][stage]["steps"]["holders_hist"]
            assert rule["loose"] == distribution.get("1", 0)
            assert rule["shared"] == sum(v for k,v in distribution.items() if k!="1")
            weight = rule["least"]
            has_rule = weight is not None and weight < rule["loose"]
            assert has_rule == rule["least_lt_loose"]
            if row["births"][int(stage)-1]==0:
                parity["stage records with no birth in that round"] += 1
                parity["shorter-rule records with no birth in that round"] += has_rule
                if int(stage)<=10:
                    ties["pair occurrences with no birth in that round"] += row["tied"].get(stage,{}).get("n",0)
            ranks[rule["rank"]] += 1
            parity["tested stages"] += 1
            parity["at most 20 distinctions"] += rule["loose"] + rule["shared"] <= 20
            parity["at least two loose"] += rule["loose"] >= 2
            parity["nonzero rank"] += bool(rule["rank"])
            parity["inexact least"] += not rule["least_exact"]
            if has_rule:
                parity["stages with a shorter rule"] += 1
                positive_ids.add((row["start"],law,row["seed"]))
                if not smallest or count < smallest[0][0]:
                    smallest = []
                if not smallest or count == smallest[0][0]:
                    smallest.append([count,row["start"],law,row["seed"],int(stage),weight,rule["loose"],rule["rank"]])
        parity["bad in original small-state enumeration"] += row["check_P"]["bad"]
        tied_this_run = False
        for t_stage, data in row["tied"].items():
            if int(t_stage)>10:
                continue
            ties["declared before holder tests"] += data["n"]
            ties["listed before holder tests"] += len(data["rows"])
            for tied in data["rows"]:
                if all(tied["pass"]):
                    steps[tied["hs"]] += 1
                    tied_this_run = True
        ties["runs with confirmed pairs"] += tied_this_run
    parity["runs with a shorter rule"] = len(positive_ids)
    return {"hub by law": by_law, "hub by choice": by_group, "hub examples": examples,
            "uniform knot ratio min/max": [str(min(ratio)), str(max(ratio))] if ratio else [],
            "uniform greatest hs increase min/max": [min(differences), max(differences)] if differences else [],
            "base runs": len(base_rows), "compared to bases": by_method, "holders at 100": hist,
            "sampled knot tests": tests, "parity": parity, "parity ranks": ranks,
            "minimum shorter rules": smallest, "tied pairs rounds 1–10": ties, "passing tied pairs by holder steps": steps}


def numberings(limit):
    groups = defaultdict(set)
    totals = Counter()
    for row in stream("run4c", limit):
        readings = hub(row)
        totals.update(readings)
        totals["rows"] += 1
        key = row["start"], row["law"], row["knot_law"], row["choice"]
        flag = "held" if readings.get("both hs") else ("not held" if readings.get("reached") else "ended")
        groups[key].add(flag)
    changed = Counter()
    for (_, law, _, choice), verdicts in groups.items():
        if len(verdicts) > 1:
            changed[law if law in ("T9","T10") else choice] += 1
    return {"groups": len(groups), "changed": changed, "conditions": totals}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    started = time.perf_counter()
    result = {"knot testing prefix": knot_prefix(args.limit), "taking": taking(args.limit),
              "renumberings": numberings(args.limit)}
    print("elapsed seconds", round(time.perf_counter()-started,3))
    if args.limit is None:
        (HERE/"taking_counts.json").write_text(json.dumps(result, indent=2)+"\n")


if __name__ == "__main__":
    main()
