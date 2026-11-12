"""The summary of TRAVEL-READ-20261112-001A-E001's run, by the frozen definitions of its contract (T1 to T4, validity).

    .venv/bin/python -B research/TRAVEL-READ-20261112-001/summary.py
Output: research/TRAVEL-READ-20261112-001/summary.json
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "..", "artifacts", "TRAVEL-READ-20261112-001A", "TRAVEL-READ-20261112-001A-E001_law_reading")


def load(name):
    return [json.loads(line) for line in open(os.path.join(D, f"{name}.jsonl"))]


def wilson(k, n):
    if n == 0:
        return None
    z = 1.96
    c = (k + z * z / 2) / (n + z * z)
    h = z * math.sqrt(k * (n - k) / n + z * z / 4) / (n + z * z)
    return [round(c - h, 4), round(c + h, 4)]


dirs, cross, rings = load("dirs"), load("cross"), load("rings")
control = json.load(open(os.path.join(D, "control.json")))
out = {"control holds": control["holds"]}
dropped = [r for r in dirs + cross + rings if "dropped at the cap" in r]
out["dropped"] = len(dropped)
# T1
by_r = {}
for r in dirs:
    by_r.setdefault(r["r"], {"rank 1": 0, "rank 2": 0, "rank 0": 0, "common": 0})
    by_r[r["r"]][f"rank {r['rank']}"] += 1
    by_r[r["r"]]["common"] += r["common pattern"]
out["rank by r"] = by_r
mid = [r for r in dirs if r["r"] in (4, 5)]
k2, k1 = sum(r["rank"] == 2 for r in mid), sum(r["rank"] == 1 for r in mid)
out["T1"] = {"rank 2 at r = 4, 5": [k2, len(mid), wilson(k2, len(mid))], "rank 1": [k1, len(mid), wilson(k1, len(mid))],
             "holds": k2 / len(mid) >= 0.4 and wilson(k2, len(mid))[0] >= 0.3 and k1 / len(mid) >= 0.2}
# T2
cls = {"flat": 0, "line": 0, "open": 0}
rows = []
for r in cross:
    one = {k: v["b"] for k, v in r["one cross-section"].items()}
    diffs, defined6 = [], False
    for sgn in (1, -1):
        b6, b2 = one.get(f"10,{6 * sgn}"), one.get(f"10,{2 * sgn}")
        if b6 is not None:
            defined6 = True
        if b6 is not None and b2 is not None:
            diffs.append(b6 - b2)
    c = "line" if any(d >= 2 for d in diffs) else ("flat" if diffs and defined6 and all(d <= 1 for d in diffs) else "open")
    cls[c] += 1
    cert = sum(1 for v in r["one cross-section"].values() if v.get("certified")) 
    defined = sum(1 for v in r["one cross-section"].values() if v["b"] is not None)
    rows.append({"sample": r["sample"], "r": r["r"], "class": c, "one": one, "two": {k: v["b"] for k, v in r["two cross-sections"].items()},
                 "certified of defined": [cert, defined]})
n2 = sum(cls.values())
out["T2"] = {"classes": cls, "flat share": [cls["flat"], n2, wilson(cls["flat"], n2)], "line share": [cls["line"], n2, wilson(cls["line"], n2)],
             "holds": cls["flat"] / n2 >= 0.5 and cls["line"] / n2 <= 0.2}
out["rank-1 rows"] = rows
# b value distribution (one cross-section)
dist = {}
for r in rows:
    for k, v in r["one"].items():
        dist.setdefault(k, {}).setdefault(str(v), 0)
        dist[k][str(v)] += 1
out["b distribution (one cross-section)"] = dist
cert_tot = [sum(r["certified of defined"][0] for r in rows), sum(r["certified of defined"][1] for r in rows)]
out["certified share of defined one-cross-section bonds"] = cert_tot
# T3
pairs = []
for r in rows:
    for y in (3, -3):
        a, b = r["one"].get(f"10,{y}"), r["one"].get(f"14,{y}")
        if a is not None and b is not None:
            pairs.append(a == b)
out["T3"] = {"equal": [sum(pairs), len(pairs)], "holds": sum(pairs) / len(pairs) >= 0.9 if pairs else None}
# T4
good, tot, ring_rows = 0, 0, []
for r in rings:
    if "rings" not in r:
        continue
    tot += 1
    r3 = [x["b"] for x in r["rings"]["3"]]
    r6 = [x["b"] for x in r["rings"]["6"]]
    reach6 = sum(b is not None for b in r6) / len(r6)
    m3 = max((b for b in r3 if b is not None), default=None)
    m6 = max((b for b in r6 if b is not None), default=None)
    ok = reach6 >= 0.8 and m3 is not None and m6 is not None and m6 <= m3
    good += ok
    ring_rows.append({"sample": r["sample"], "r": r["r"], "reached on ring 3": sum(b is not None for b in r3) / len(r3), "reached on ring 6": round(reach6, 3),
                      "max b ring 3": m3, "max b ring 6": m6, "zero": ok})
out["T4"] = {"zero dimensions": [good, tot, wilson(good, tot)], "holds": good / tot >= 2 / 3}
out["rank-2 rows"] = ring_rows
json.dump(out, open(os.path.join(HERE, "summary.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("rank-1 rows", "rank-2 rows", "b distribution (one cross-section)")}, indent=1))
print(json.dumps(out["b distribution (one cross-section)"]))
