"""The summary of WEIGHTS-20261112-001A-E001 by its frozen definitions: per weighting, the prefix of samples in index order up to the
stopping index (40 travelling bases with a new kind, or 300 samples), from census.jsonl (before the pause) and the resumed run's
results.jsonl (after it; main arm only, the enlarged arm infeasible, recorded as a deviation). The completion pass (completion.json,
certificates repeating along and across outside a finite box) moves each forced-but-uncertified base it certifies to "two certified";
both counts are reported.

    .venv/bin/python -B research/WEIGHTS-20261112-001/summary.py
Output: research/WEIGHTS-20261112-001/summary.json
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
O = os.path.join(HERE, "..", "..", "artifacts", "WEIGHTS-20261112-001A", "WEIGHTS-20261112-001A-E001_two_shifts")


def wilson(k, n):
    if n == 0:
        return None
    z = 1.96
    c = (k + z * z / 2) / (n + z * z)
    h = z * math.sqrt(k * (n - k) / n + z * z / 4) / (n + z * z)
    return [round(c - h, 4), round(c + h, 4)]


recs = {}
for line in open(os.path.join(O, "census.jsonl")):
    r = json.loads(line)
    if "beta" in r:
        recs[(r["beta"], r["sample"])] = r
for line in open(os.path.join(O, "resume_census", "results.jsonl")):
    r = json.loads(line)
    if r.get("status") == "ok":
        x = r["result"]
        recs[(x["beta"], x["sample"])] = {"beta": x["beta"], "sample": x["sample"], "by r": x["by r"]}
done = {(c["beta"], c["sample"], c["r"]) for c in json.load(open(os.path.join(HERE, "completion.json"))) if c["certified now"]}
out = {}
for beta in (0, 1, 2):
    n, i, stop = 0, 0, None
    while (beta, i) in recs and i < 300:
        for v in recs[(beta, i)]["by r"].values():
            if v["class"] == "travels" and v["stratum"] == "new kinds":
                n += 1
        if n >= 40:
            stop = i
            break
        i += 1
    prefix = [recs[(beta, j)] for j in range(0, (stop if stop is not None else i - 1) + 1) if (beta, j) in recs]
    st = {"stopping index": stop, "samples counted": len(prefix)}
    for stratum in ("new kinds", "old box"):
        cnt = {"two certified": 0, "forced, uncertified": 0, "one direction, unresolved": 0}
        bases = trav = completed = 0
        for r in prefix:
            for rr, v in r["by r"].items():
                if v["stratum"] != stratum:
                    continue
                bases += v["outcome"] == "base"
                if v["class"] != "travels":
                    continue
                trav += 1
                m = v.get("main", {})
                e = v.get("enlarged") or {}
                if m.get("rank certified") == 2 or e.get("rank certified") == 2:
                    cnt["two certified"] += 1
                elif m.get("rank forced") == 2 or e.get("rank forced") == 2:
                    cnt["forced, uncertified"] += 1
                    completed += (beta, r["sample"], rr) in done
                else:
                    cnt["one direction, unresolved"] += 1
        k = cnt["two certified"]
        w = wilson(k, trav)
        verdict = None
        if stratum == "new kinds" and trav:
            verdict = "pass" if (w[0] >= 0.5 and k / trav >= 0.7) else ("fail" if w[1] < 0.7 else "inconclusive")
            if trav < 40:
                verdict = "inconclusive (size)"
        k2 = k + completed
        w2 = wilson(k2, trav)
        verdict2 = None
        if stratum == "new kinds" and trav:
            verdict2 = "pass" if (w2[0] >= 0.5 and k2 / trav >= 0.7) else ("fail" if w2[1] < 0.7 else "inconclusive")
            if trav < 40:
                verdict2 = "inconclusive (size)"
        st[stratum] = {"bases": bases, "travelling": trav, "travelling per base": round(trav / bases, 3) if bases else None,
                       "counts": cnt, "two certified": [k, trav, w], "W1": verdict,
                       "after completion": {"two certified": [k2, trav, w2], "W1": verdict2}}
    out[beta] = st
cal = [json.loads(l) for l in open(os.path.join(O, "calibration.jsonl"))]
# every attempted calibration item so far was capped and has no outcome (referee R1); count outcomes only where there is one
out["calibration"] = {"attempted": len(cal), "of": 23, "capped, no outcome": sum(1 for c in cal if "dropped at the cap" in c),
                      "gained": sum(1 for c in cal if (c.get("enlarged") or {}).get("rank certified") == 2),
                      "note": "the enlarged arm is infeasible at this scale (over 30 minutes a base); the rest not run; W3 undecided "
                              "with no observation"}
json.dump(out, open(os.path.join(HERE, "summary.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
