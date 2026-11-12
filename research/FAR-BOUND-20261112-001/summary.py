"""The summary of FAR-BOUND-20261112-001A-E001's run by its contract's definitions (F1 to F3, validity), and the exploratory
cross-tabulation with second_direction.json.

    .venv/bin/python -B research/FAR-BOUND-20261112-001/summary.py
Output: research/FAR-BOUND-20261112-001/summary.json
"""
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
D = os.path.join(ROOT, "artifacts", "FAR-BOUND-20261112-001A", "FAR-BOUND-20261112-001A-E001_bounded_far")
TRR = os.path.join(ROOT, "artifacts", "TRAVEL-READ-20261112-001A", "TRAVEL-READ-20261112-001A-E001_law_reading", "rings.jsonl")
load = lambda n: [json.loads(l) for l in open(os.path.join(D, f"{n}.jsonl"))]
rec, far, rings = load("recheck"), load("far"), load("rings")
out = {"control": json.load(open(os.path.join(D, "control.json")))["holds"]}
cls = Counter(r.get("class", "dropped") for r in rec)
out["F1"] = {"classes": dict(cls), "bounded across": cls["bounded across"], "holds": cls["bounded across"] >= 40,
             "TRAVEL-READ headline": "narrowed" if cls["bounded across"] < 56 else "kept", "overturned": cls["bounded across"] < 33}
recd = {(r["sample"], r["r"]): r for r in rec}
sd = json.load(open(os.path.join(HERE, "second_direction.json")))
f2 = Counter()
rows = []
for r in far:
    key = (r["sample"], r["r"])
    rank = sd[f"{key[0]},{key[1]}"][0]
    if "far" not in r:
        f2["dropped"] += 1
        rows.append({"sample": key[0], "r": key[1], "outcome": "dropped", "second direction (exploratory)": rank == 2})
        continue
    near = max(v["b_cert"] for v in recd[key]["profile"].values() if v["b_cert"] is not None)
    fb = [v["b_cert"] for v in r["far"].values()]
    d = [b for b in fb if b is not None]
    share = len(d) / len(fb)
    ok = all(b <= near + 1 for b in d) and share >= 0.8
    outc = "bounded" if ok else ("grows by 2 or more" if d and max(d) >= near + 2 else "certificates missing")
    f2[outc] += 1
    rows.append({"sample": key[0], "r": key[1], "outcome": outc, "near max": near, "far max": max(d) if d else None,
                 "certified share": round(share, 3), "second direction (exploratory)": rank == 2})
dec = len(far) - f2["dropped"]
out["F2"] = {"outcomes": dict(f2), "bounded of decided": [f2["bounded"], dec], "dropped share": round(f2["dropped"] / len(far), 3),
             "holds": f2["bounded"] >= 2 / 3 * dec and f2["dropped"] <= 0.2 * len(far)}
out["far rows"] = rows
cross = Counter((x["outcome"], "second direction" if x["second direction (exploratory)"] else "one direction") for x in rows)
out["exploratory: far outcome by second direction"] = {f"{a} / {b}": n for (a, b), n in cross.items()}
by_y = {}
for r in far:
    for t, v in r.get("far", {}).items():
        a, y = map(int, t.split(","))
        if v["b_cert"] is not None:
            by_y.setdefault(abs(y), []).append(v["b_cert"])
out["mean certified b by |y|"] = {y: round(sum(v) / len(v), 3) for y, v in sorted(by_y.items())}
tr = {(r["sample"], r["r"]): r for r in map(json.loads, open(TRR))}
good = tot = drop = 0
cs = []
for r in rings:
    if "rings" not in r:
        drop += 1
        continue
    tot += 1
    r3 = [x["b"] for x in tr[(r["sample"], r["r"])]["rings"]["3"] if x["b"] is not None]
    t15 = r["rings"]["15"]
    reach = [x["b_win"] for x in t15]
    ok15 = [b for b in reach if b is not None and b <= 5]
    m15 = max([b for b in reach if b is not None], default=None)
    good += len(ok15) / len(reach) >= 0.8 and r3 and m15 is not None and m15 <= max(r3) + 1
    cs.append(sum(x["b_cert"] is not None for x in t15) / len(t15))
out["F3"] = {"held": [good, tot], "dropped": drop, "mean certified share on ring 15": round(sum(cs) / len(cs), 3), "holds": good >= 2 / 3 * tot}
json.dump(out, open(os.path.join(HERE, "summary.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "far rows"}, indent=1))
