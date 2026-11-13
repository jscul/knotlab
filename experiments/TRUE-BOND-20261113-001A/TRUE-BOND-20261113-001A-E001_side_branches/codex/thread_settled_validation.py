"""Written by the thread, not Codex: settles REPORT.md ambiguity 1 as the uniform-depth reading (the truncation at depth s + h has side
tables of height D - j at ray copy C_j) and compares Codex's FamilyDP.finite_counts under that reading with every direct-SAT count
Codex recorded, through each case's exhausted size."""
import json, sys, time, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from true_bond import FamilyDP, study_families
v = json.load(open(os.path.join(HERE, "validation.json")))
families = study_families()
out = []
for case in v["brute_force"]:
    sat = case["sat"]
    upto = sat.get("complete_through")
    if not upto:
        continue
    dp = FamilyDP(families[case["idx"]], deadline=time.monotonic() + 120)
    try:
        counts = dp.finite_counts(case["s"], case["h"], upto, convention="uniform_depth")
    except Exception as e:
        out.append(dict(idx=case["idx"], s=case["s"], h=case["h"], error=repr(e))); continue
    sc = {int(k): n for k, n in sat["counts"].items() if 1 <= int(k) <= upto}   # size 0 is never a bond
    dc = {int(k): n for k, n in counts.items() if int(k) <= upto}
    out.append(dict(idx=case["idx"], s=case["s"], h=case["h"], through=upto, sat=sc, dp=dc, equal=sc == dc))
    print(out[-1], flush=True)
json.dump(dict(convention="uniform_depth", cases=out, all_equal=all(c.get("equal") for c in out)), open(os.path.join(HERE, "thread_settled_validation.json"), "w"), indent=1)
