"""REACH-CENSUS-20261113-001A, the thread's stress test (after the census, exploratory): the last-call ray on every one-definition
limit-only family that grows along the first ray (PROVED-RATE-20261113-001's growing families, at the census caps), with Codex's
runner unchanged. Writes codex/full/alt_growing664_families.jsonl."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "codex"))
from pathlib import Path
import run_census as RC
full = Path(HERE) / "codex" / "full"
fam = {}
for x in open(full / "families.jsonl"):
    r = json.loads(x); fam[r["key"]] = r
keys = [json.loads(x)["key"] for x in open(full / "gate664.jsonl")][:664]
grow = sorted(k for k in keys if fam[k]["class"] == "grows")
print(len(grow), flush=True)
RC.run_tasks(grow, full / "alt_growing664_families.jsonl", 4, ray="last")
