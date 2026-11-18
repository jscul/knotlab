"""Score T1-T3 of research/MEET-TWIST-20261118-001/preregistration.md.

  ../../../.venv/bin/python -B merge.py <runner output dir>
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from longrun import load_results

recs = load_results(sys.argv[1])
bad = sorted(k for k, v in recs.items() if v["status"] != "ok")
per = defaultdict(lambda: {"cases": 0, "option_states_ok": 0, "option_states_bad": 0, "levels_carried": 0, "levels": 0,
                           "states_added": 0, "first_failures": []})
for k, v in recs.items():
    if v["status"] != "ok":
        continue
    r = v["result"]
    d = per[r["n0"]]
    d["cases"] += 1
    for L in r["levels"]:
        d["option_states_ok"] += L["option_states_ok"]
        d["option_states_bad"] += L["option_states_bad"]
        d["levels"] += 1
        d["levels_carried"] += L["law_carried"]
        d["states_added"] += L["states_added"]
        if (L["option_states_bad"] or not L["law_carried"]) and len(d["first_failures"]) < 5:
            d["first_failures"].append({"ordered": r["ordered"], "n": L["n"]})
pred = {"T1": all(d["option_states_bad"] == 0 for d in per.values()),
        "T2": all(d["levels_carried"] == d["levels"] for d in per.values()),
        "T3": all(d["states_added"] == 0 for d in per.values())}
out = {"cases": len(recs), "not_ok": bad, "per_n0": dict(per), "predictions": pred}
dest = ROOT / "artifacts/MEET-TWIST-20261118-001B/MEET-TWIST-20261118-001B-E001_knotmap"
dest.mkdir(parents=True, exist_ok=True)
(dest / "results.json").write_text(json.dumps(out, indent=1, sort_keys=True))
print(json.dumps(pred), "not ok:", bad)
for n0, d in sorted(per.items()):
    print(n0, {k: d[k] for k in ("cases", "option_states_ok", "option_states_bad", "levels_carried", "levels", "states_added")})
