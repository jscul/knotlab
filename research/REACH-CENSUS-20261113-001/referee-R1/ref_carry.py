"""REACH-CENSUS-R1: do the last-call-ray bounded families carry a top port down that ray by identity?

For a one-definition family, the last-call ray's call is the definition's last SELF call, args (a0, a1, a2): the child's port j is
the parent's distinction a_j. Port positions map j -> a_j when a_j is a port (< 3). A top port is carried at every depth along the
ray iff this partial map on {0, 1, 2} has a cycle (then the same top distinction is a port of every copy on the ray)."""
import gzip, json, sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
A = ROOT / "artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census"


def carried(args):
    f = {j: a for j, a in enumerate(args) if a < 3}
    for start in range(3):
        seen, j = set(), start
        while j in f and j not in seen:
            seen.add(j)
            j = f[j]
        if j in seen:
            return True
    return False


rows = [json.loads(x) for x in gzip.open(A / "alt_growing664_families.jsonl.gz", "rt")]
out = Counter()
ex = []
for r in rows:
    defs = json.loads(r["key"])
    calls = defs[-1][2]
    selfs = [tuple(a) for c, a in calls if c == "SELF"]
    first, last = selfs[0], selfs[-1]
    out[(r["class"], "last carried" if carried(last) else "last not carried", "first carried" if carried(first) else "first not carried")] += 1
    if r["class"] == "bounded" and not carried(last) and len(ex) < 3:
        ex.append(dict(key=r["key"], L_ray=r["L_ray"][:10]))
res = {"|".join(k): v for k, v in sorted(out.items())}
print(json.dumps(res, indent=1))
json.dump(dict(counts=res, bounded_not_carried_examples=ex), open(Path(__file__).with_name("result_carry.json"), "w"), indent=1)
