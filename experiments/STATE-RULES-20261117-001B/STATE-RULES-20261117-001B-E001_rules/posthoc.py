"""Post hoc for STATE-RULES-20261117-001B-E001 (written after the read-out, labelled): two readings the frozen output did not store.
1. R17: KF3's exact split at n = 5 by class of states alone (subdivision against pendant).
2. R19: in KF3's frozen runs from the two six-starts (recomputed from the frozen seeds, so the same runs), how many keep 12 states
   to n = 12, and their two-order counts at every n.
    .venv/bin/python -B posthoc.py      (writes artifacts/.../posthoc.json)
"""
import collections
import json
import os

import rules as R
import run as RUN

out = {}
levels, canon = R.knot_exact("fewest", 3, "line", 5, "knot")
sc = R.Canon()
split = collections.Counter()
for c, p, m in levels[-1]["dist"]:
    st, nn, kk = canon.reps[c]
    split[sc.cid(list(st), nn)] += p
out["R17_KF3_n5_by_states_class"] = {str(k): round(v, 12) for k, v in split.items()}
for start in ("fan6", "nonfan6"):
    traces = RUN.knot_runs("fewest", start, 12, 30, f"E8:KF3:{start}", "knot")
    out[f"R19_KF3_{start}"] = {"N_12_at_12": sum(1 for tr in traces if tr[-1]["n"] == 12 and tr[-1]["N"] == 12),
                               "two_way_by_n": {str(n): sum(1 for tr in traces for r in tr if r["n"] == n and r.get("two_way"))
                                                for n in range(6, 13)}}
json.dump(out, open(os.path.join(RUN.OUT, "posthoc.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
