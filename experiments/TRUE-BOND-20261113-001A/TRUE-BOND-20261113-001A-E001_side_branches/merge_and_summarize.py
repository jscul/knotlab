"""The thread's merge and summary for TRUE-BOND-A1: the runner's part files (seven instances, then the skipped seventh part in four),
one record per family, and the pre-registration's readings over the depths each family reached within its 1,100-second limit."""
import glob, json, os
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(HERE, "codex")
OUT = os.path.join(HERE, "../../../artifacts/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches")
rows = {}
for f in sorted(glob.glob(os.path.join(C, "true_rates_part*.jsonl"))):
    for line in open(f):
        r = json.loads(line)
        rows.setdefault(r["idx"], r)
rows = sorted(rows.values(), key=lambda r: r["idx"])
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "true_rates_all.jsonl"), "w") as f:
    for r in rows:
        f.write(json.dumps(r, sort_keys=True) + "\n")
def reached(r):
    return max([i + 1 for i, x in enumerate(r["L"]) if x is not None] + [0])
def deficits(r):
    return [(lr - l) if (l is not None and lr is not None) else None for l, lr in zip(r["L"], r["L_ray"])]
S = dict(families=len(rows), status=dict(Counter(r["status"] for r in rows)),
         depth_reached=dict(sorted(Counter(reached(r) for r in rows).items())))
short = [r for r in rows if any(d is not None and d > 0 for d in deficits(r))]
S["P1_shortened_within_reached"] = [len(short), len(rows)]
S["negative_deficit"] = sum(any(d is not None and d < 0 for d in deficits(r)) for r in rows)
both = [r for r in short if r["L"][11] is not None and r["L"][5] is not None]
S["P2_deficit_growth_6_to_12"] = dict(Counter((r["L_ray"][11] - r["L"][11]) - (r["L_ray"][5] - r["L"][5]) for r in both))
p3 = [r for r in rows if r["L"][11] is not None and r["L"][5] is not None]
S["P3_L12_gt_L6"] = [sum(r["L"][11] > r["L"][5] for r in p3), len(p3)]
deep = [r for r in rows if reached(r) >= 8]
S["grows_within_reached_ge8"] = [sum(r["L"][reached(r) - 1] > r["L"][3] for r in deep), len(deep)]
S["max_deficit"] = dict(Counter(max([d for d in deficits(r) if d is not None] + [0]) for r in rows))
S["deficit_profiles_shortened"] = {r["idx"]: [d for d in deficits(r) if d is not None] for r in short}
json.dump(S, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in S.items() if k != "deficit_profiles_shortened"}, indent=1))
