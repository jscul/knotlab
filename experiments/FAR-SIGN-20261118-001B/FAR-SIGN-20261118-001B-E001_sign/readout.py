"""FAR-SIGN-20261118-001B-E001 read-out: the frozen predictions R0 to R7, the harness checks, coverage strata and the ablation.
Run after run.py: python -B readout.py  (prints JSON and writes readout.json next to the results)."""
import gzip
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import signlib as SL  # noqa: E402

OUT = os.path.join(SL.ROOT, "artifacts", "FAR-SIGN-20261118-001B", "FAR-SIGN-20261118-001B-E001_sign")


def load(part):
    with gzip.open(os.path.join(OUT, f"part_{part}.json.gz"), "rt") as f:
        return json.load(f)


def strat_min(orders):
    if not orders:
        return "none"
    m = min(orders)
    return str(m) if m < 3 else ">=3"


def main():
    S = load("S")
    out = {"starts": len(S), "seconds": sum(r["seconds"] for r in S)}
    ext = [(r["n0"], row) for r in S for row in r["rows"]]
    out["crossing_extensions"] = len(ext)
    out["copy_steps"] = sum(row["seed"] for _, row in ext)
    h = Counter()
    conf = Counter()
    weak, near, patt = Counter(), Counter(), Counter()
    counter = {"R1": [], "R2": [], "R3": [], "R4": [], "R6": []}
    r2 = Counter(); r3 = Counter(); r4 = Counter(); r6 = Counter(); r0 = Counter(); orient = Counter()
    strata = Counter()
    cover = Counter()
    closure_v = defaultdict(set)
    marked_v = defaultdict(set)
    inclass = Counter()
    for n0, row in ext:
        h["mine == seed"] += row["mine"] == row["seed"]
        sets = [s for s in row["sets"] if s]
        treated = [s for s in sets if s.get("near_to_shared")]
        for s in sets:
            orient["near pins r to the shared distinction" if s.get("near_to_shared") else
                   ("two-place touch" if s.get("two_touch") else "near pins r to the other distinction")] += 1
        for s in treated:
            h["L1"] += s["L1"]; h["L2"] += s["L2"]; h["K1"] += s["K1"]; h["treated sets"] += 1
        sign_any = any(s["sign"] for s in sets)
        conf[f"seed={int(row['seed'])} sign={int(sign_any)}"] += 1
        if row["seed"] != sign_any and len(counter["R1"]) < 50:
            counter["R1"].append({"n0": n0, **row})
        weak[f"seed={int(row['seed'])} weak={int(any(s['weak'] for s in sets))}"] += 1
        near[f"seed={int(row['seed'])} near={int(any(s.get('near_none') for s in sets))}"] += 1
        if row["seed"]:
            r0["copy steps with a treated knot set"] += bool(treated)
            r0["copy steps"] += 1
        for s in treated:
            if s["F1_premise"]:
                r2["premise"] += 1
                r2["with the sign"] += s["sign"]
                if not s["sign"] and len(counter["R2"]) < 50:
                    counter["R2"].append({"n0": n0, "n": row["n"], "seed": row["seed"], **s})
            if s["sign"]:
                r3["with the sign"] += 1
                good = s["T1"] and s["T2"]
                r3["T1 and T2"] += good
                cover[("sign", strat_min(s["orders"]))] += 1
                if not good and len(counter["R3"]) < 50:
                    counter["R3"].append({"n0": n0, "n": row["n"], "seed": row["seed"], **s})
            key = "copy" if row["seed"] else "refused"
            r4[f"{key}: pattern={int(s['pattern'])}"] += 1
            if s["pattern"] != row["seed"] and len(counter["R4"]) < 50:
                counter["R4"].append({"n0": n0, "n": row["n"], "seed": row["seed"], **s})
            r6["alpha" if s["alpha"] else ("beta" if s["beta"] else "neither")] += 1
            strata[("copies_before", min(row["copies_before"], 2), "seed", row["seed"])] += 1
            strata[("p_is_earlier_r", s["p_is_earlier_r"], "seed", row["seed"])] += 1
            strata[("min order", strat_min(s["orders"]), "seed", row["seed"])] += 1
            if s.get("closure") is not None:
                closure_v[s["closure"]].add(row["seed"])
                marked_v[(s["closure"], json.dumps(s["marked"]))].add(row["seed"])
                if s["closure"] == SL.COPY_CLASS:
                    inclass[f"seed={int(row['seed'])} sign={int(s['sign'])}"] += 1
        states = {("alpha" if s["alpha"] else "other") for s in treated}
        if len(states) > 1:
            r6["fills with both states"] += 1
            if len(counter["R6"]) < 20:
                counter["R6"].append({"n0": n0, **row})
    out["harness"] = dict(h)
    out["orientation of crossing-making knot sets"] = dict(orient)
    out["R0"] = dict(r0)
    out["R1 sign vs SEED (extensions)"] = dict(conf)
    out["R2 F1"] = dict(r2)
    out["R3 T1 and T2 under the sign"] = dict(r3)
    out["R3 coverage: sign sets by smaller order"] = {k[1]: v for k, v in cover.items()}
    out["R4 pair pattern"] = dict(r4)
    out["R5 weak sign"] = dict(weak)
    out["R5 near-pair sign"] = dict(near)
    out["R6 states"] = dict(r6)
    out["R7 copy class: knot sets in it"] = dict(inclass)
    out["R7 closure pictures with both verdicts"] = sum(1 for v in closure_v.values() if len(v) > 1)
    out["R7 marked pictures with both verdicts"] = sum(1 for v in marked_v.values() if len(v) > 1)
    out["R7 closure pictures / marked pictures"] = [len(closure_v), len(marked_v)]
    out["strata"] = {" ".join(map(str, k)): v for k, v in sorted(strata.items(), key=str)}
    starts = Counter()
    for r in S:
        starts[(r["n0"], r["nmax"])] += 1
    out["starts by line"] = {f"{a} to {b}": c for (a, b), c in sorted(starts.items())}
    out["counterexamples"] = {k: v for k, v in counter.items() if v}
    A = [row for r in load("A") for row in r["rows"]]
    ab = defaultdict(Counter)
    for x in A:
        k = "pq={} ap={} cd={}".format(*map(int, x["pattern_coknotted"]))
        c = ab[k]
        c["knot sets"] += 1
        c["copy"] += x["seed"]
        c["sign"] += x["sign"]
        c["sign != copy"] += x["sign"] != x["seed"]
        c["F1 fails"] += x["F1_premise"] and not x["sign"]
        c["T1/T2 fail under the sign"] += x["sign"] and not (x["T1"] and x["T2"])
    out["ablation (no prediction)"] = {k: dict(v) for k, v in sorted(ab.items())}
    with open(os.path.join(OUT, "readout.json"), "w") as f:
        json.dump(out, f, indent=1, default=str)
    show = {k: v for k, v in out.items() if k != "counterexamples"}
    show["counterexamples (counts)"] = {k: len(v) for k, v in counter.items()}
    print(json.dumps(show, indent=1, default=str))


if __name__ == "__main__":
    main()
