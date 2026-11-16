"""Referee R1, task 3 read-out: compares the referee's recomputation with the
study's run (results.jsonl, summary.json, read as data) and the decision
note's table; fresh samples are compared statistically."""

import glob
import json
import os

import numpy as np
from scipy.stats import mannwhitneyu

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ART = os.path.join(ROOT, "artifacts", "CARRY-STRANDS-20261116-001A", "CARRY-STRANDS-20261116-001A-E001_carried")

NOTE = {64: dict(sigma=3, R=12, T1=9, T2s=7, T2k=7, P2k=2, after=0.28),
        256: dict(sigma=5, R=22.5, T1=16, T2s=12.5, T2k=12, P2k=3, after=0.079),
        1024: dict(sigma=6, R=32.5, T1=22, T2s=15, T2k=15, P2k=3, after=0.065),
        4096: dict(sigma=8.5, R=60, T1=35, T2s=23.5, T2k=23, P2k=4, after=0.089)}


def readings(r):
    return {"sigma": r["sigma_max"], "R": r["R"], "P1": r["w1"]["P"], "T1": r["w1"]["T"],
            "P2s": r["w2"]["P"], "T2s": r["w2"]["T"], "P2k": r["w2k"]["P"], "T2k": r["w2k"]["T"],
            "gain": r.get("keep_gain_fraction"), "before": r.get("keep_gain_before"),
            "after": r.get("keep_gain_after"), "ratio": r["T2_over_T1"],
            "P2k_eq_ceil": r["w2k"]["P"] == -(-r["w1"]["P"] // 2), "T2_le_T1": r["w2"]["T"] <= r["w1"]["T"]}


def med(xs):
    xs = [x for x in xs if x is not None]
    return float(np.median(xs)) if xs else None


def main():
    mine = []
    for f in sorted(glob.glob(os.path.join(HERE, "referee_task3_random_n*.json"))):
        mine += json.load(open(f))["samples"]
    study = {}
    for line in open(os.path.join(ART, "run", "results.jsonl")):
        rec = json.loads(line)
        if rec["case"].startswith("rand-") and rec["status"] == "ok":
            r = rec["result"]
            study[(r["n"], int(rec["case"].split("-s")[1]))] = r
    summ = json.load(open(os.path.join(ART, "summary.json")))["tables"]["random"]

    out = {"per_sample_study_instances": {}, "medians": {}, "fresh_vs_study_tests": {}, "checks_failed": []}
    fields = []
    for r in mine:
        if r["checks"]:
            out["checks_failed"].append((r["kind"], r["n"], r["s"], r["checks"]))
    # 1. per sample, study instances
    by_n = {}
    for r in mine:
        if r["kind"] != "study":
            continue
        s = study.get((r["n"], r["s"]))
        d = by_n.setdefault(r["n"], {"samples": 0, "exact": 0, "diffs": []})
        d["samples"] += 1
        diffs = []
        for key, mv, sv in (
                ("k_star", r["k_star"], s["k_star"]), ("forced", r["forced"], s["forced"]),
                ("sigma_max", r["sigma_max"], s["sigma_max"]), ("R", r["R"], s["R"]),
                *[(f"{law}.{x}", r[law][x], s["laws"][law][x]) for law in ("w1", "w2", "w2k") for x in ("P", "T", "L", "states")],
                ("w1.phase_sizes", r["phase_sizes_w1"], s["laws"]["w1"]["phase_sizes"]),
                ("gain", r.get("keep_gain_fraction"), s["laws"]["w2k"].get("keep_gain_fraction")),
                ("before", r.get("keep_gain_before"), s["laws"]["w2k"].get("keep_gain_before")),
                ("after", r.get("keep_gain_after"), s["laws"]["w2k"].get("keep_gain_after"))):
            if isinstance(mv, float) or isinstance(sv, float):
                same = (mv is None and sv is None) or (mv is not None and sv is not None and abs(mv - sv) < 1e-12)
            else:
                same = mv == sv
            if not same:
                diffs.append((key, mv, sv))
        if "w3" in r and "w3" in s["laws"]:
            if (r["w3"]["P"], r["w3"]["T"]) != (s["laws"]["w3"]["P"], s["laws"]["w3"]["T"]):
                diffs.append(("w3", r["w3"], s["laws"]["w3"]))
        if diffs:
            d["diffs"].append({"s": r["s"], "diffs": diffs})
        else:
            d["exact"] += 1
    out["per_sample_study_instances"] = by_n
    # 2. medians
    for kind in ("study", "fresh"):
        for n in sorted({r["n"] for r in mine}):
            rs = [readings(r) for r in mine if r["kind"] == kind and r["n"] == n]
            if not rs:
                continue
            row = {k: med([x[k] for x in rs]) for k in ("sigma", "R", "P1", "T1", "P2s", "T2s", "P2k", "T2k",
                                                         "gain", "before", "after", "ratio")}
            row["samples"] = len(rs)
            row["share_P2k_eq_ceil"] = float(np.mean([x["P2k_eq_ceil"] for x in rs]))
            row["share_T2_le_T1"] = float(np.mean([x["T2_le_T1"] for x in rs]))
            row["max_before"] = max((x["before"] for x in rs if x["before"] is not None), default=None)
            out["medians"][f"{kind}-{n}"] = row
    # summary.json rows for comparison
    keymap = {"sigma": "sigma", "R": "R", "P1": "P1", "T1": "T1", "P2s": "P2_spend", "T2s": "T2_spend",
              "P2k": "P2_keep", "T2k": "T2_keep", "gain": "keep_gain_fraction", "before": "keep_gain_before",
              "after": "keep_gain_after", "ratio": "median_T2_over_T1", "share_P2k_eq_ceil": "share_P2keep_eq_ceil",
              "share_T2_le_T1": "share_T2_le_T1"}
    cmp_summary = {}
    for n in sorted({r["n"] for r in mine}):
        row = out["medians"].get(f"study-{n}")
        srow = summ.get(str(n))
        if row and srow:
            cmp_summary[n] = {k: (row[k], srow[v]) for k, v in keymap.items()
                              if not (row[k] == srow[v] or (row[k] is not None and srow[v] is not None and abs(row[k] - srow[v]) < 1e-9))}
    out["study_instances_median_vs_summary_json_differences"] = cmp_summary
    note_cmp = {}
    for n, nr in NOTE.items():
        for kind in ("study", "fresh"):
            row = out["medians"].get(f"{kind}-{n}")
            if not row:
                continue
            note_cmp[f"{kind}-{n}"] = {k: (row[{"sigma": "sigma", "R": "R", "T1": "T1", "T2s": "T2s", "T2k": "T2k",
                                                "P2k": "P2k", "after": "after"}[k]], v) for k, v in nr.items()}
    out["vs_decision_note_table"] = note_cmp
    # 3. fresh vs study instances (study numbers from results.jsonl), Mann-Whitney two-sided
    for n in sorted({r["n"] for r in mine}):
        fr = [readings(r) for r in mine if r["kind"] == "fresh" and r["n"] == n]
        st = [readings(r) for r in mine if r["kind"] == "study" and r["n"] == n]
        if not fr or not st:
            continue
        tests = {}
        for k in ("sigma", "R", "T1", "T2s", "T2k", "P2k", "after", "ratio"):
            a = [x[k] for x in fr if x[k] is not None]
            b = [x[k] for x in st if x[k] is not None]
            if len(set(a + b)) <= 1:
                tests[k] = {"p": 1.0, "fresh_median": med(a), "study_median": med(b)}
                continue
            p = float(mannwhitneyu(a, b, alternative="two-sided").pvalue)
            tests[k] = {"p": round(p, 4), "fresh_median": med(a), "study_median": med(b)}
        out["fresh_vs_study_tests"][n] = tests
    with open(os.path.join(HERE, "referee_task3_summary.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)
    print("checks failed:", out["checks_failed"])
    for n, d in by_n.items():
        print("study instances n", n, "exact", d["exact"], "/", d["samples"], d["diffs"][:2])
    print("median diffs vs summary.json:", cmp_summary)
    for k, v in out["medians"].items():
        print(k, {x: (round(y, 3) if isinstance(y, float) else y) for x, y in v.items()})
    for n, t in out["fresh_vs_study_tests"].items():
        print("MW", n, {k: v["p"] for k, v in t.items()})


if __name__ == "__main__":
    main()
