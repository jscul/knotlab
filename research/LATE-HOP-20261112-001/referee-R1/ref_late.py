"""LATE-HOP-R1: spot recomputation of LATE-HOP-20261112-001 with the referee's own builder (TWO-BIT-ROWS-R1's ref_two.py).

Rules: the late rule that settles at 47 (k = 28) to depth 80, one hop and one flat harmony to depth 120, compared with the census's
depth-200 records over the same depths.  ref_late.py -> result_late.json
"""
import glob, json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research" / "TWO-BIT-ROWS-20261112-001" / "referee-R1"))
import ref_two as T

rows = {r["k"]: r for r in (json.loads(x) for n in glob.glob(str(ROOT / "artifacts" / "LATE-HOP-20261112-001A" / "*" / "runs_*.jsonl"))
                             for x in open(n))}
hop_h = min(k for k, r in rows.items() if r["variant"] == "hop" and r["top_class"][0] == "harmony")
flat_h = min(k for k, r in rows.items() if r["variant"] == "flat" and r["top_class"][0] == "harmony")
out = []
for k, depth in ((28, 80), (hop_h, 120), (flat_h, 120)):
    r = rows[k]
    t0 = time.time()
    alive, top = T.read(r["variant"], [tuple(x) for x in r["rule"]], tmax=depth)
    out.append(dict(k=k, variant=r["variant"], why=r["why"], depth=depth, match=(alive == r["alive"][:depth] and top == r["top"][:depth]),
                    top_changes_after_40=[t for t in T.changes(top) if t > 40][:12], alive_changes=T.changes(alive),
                    seconds=round(time.time() - t0)))
    print(json.dumps(out[-1]), flush=True)
json.dump(out, open(HERE / "result_late.json", "w"), indent=1)
