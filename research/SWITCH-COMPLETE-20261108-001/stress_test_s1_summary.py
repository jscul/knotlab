#!/usr/bin/env python3
"""SWITCH-COMPLETE-S1, summarized: the direct run on seed 3 against the row-by-row run, and the row-by-row runs on the two 10-line
glues (seeds 6 and 36). usage: stress_test_s1_summary.py DIRECT3.json ROWS3.json ROWS6.json ROWS36.json OUT.json"""
import collections
import json
import sys

d3, r3, r6, r36 = (json.load(open(p)) for p in sys.argv[1:5])


def stats(d):
    C = d["classes"]
    groups = collections.defaultdict(list)
    for c in C:
        groups[json.dumps(c["block"])].append(c)
    empty = [c for c in C if all(x is not None and not any(x) for x in c["block"])]
    return {"glue lines": len(d["glue"]), "classes": len(C), "distinct blocks": len(groups),
            "group sizes": sorted(collections.Counter(len(v) for v in groups.values()).items()),
            "classes where nothing creates": len(empty), "classes without solutions": sum(c["solutions"] == 0 for c in C),
            "sampled rows agree": d.get("sampled rows agree")}


A = {c["mask"]: json.dumps(c["block"]) for c in d3["classes"]}
B = {c["mask"]: json.dumps(c["block"]) for c in r3["classes"]}
out = {"seed 3: row-by-row equals the direct run, class by class": A == B and d3["off-tree incidences"] == r3["off-tree incidences"],
       "seed 3": stats(r3), "seed 6": stats(r6), "seed 36": stats(r36)}
json.dump(out, open(sys.argv[5], "w"), indent=1)
print(json.dumps(out, indent=1))
