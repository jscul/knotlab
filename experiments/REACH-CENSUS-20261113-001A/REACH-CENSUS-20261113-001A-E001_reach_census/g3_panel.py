"""REACH-CENSUS-20261113-001A, the thread's G3 panel selection (pre-registration, clarification C1), frozen before the full run.

Pool: the smoke run's computed families (codex/smoke_families.jsonl) that are not unresolved. Order: (largest block, key).
One Random(7) stream, in this order: for each computed class (grows, bounded, mixed by residue, lost at large depths, none at
any depth) sample 10 from its 30 smallest (all if fewer); then, if fewer than 40 of the panel have several definitions, sample the
deficit from the 120 smallest remaining several-definition families; then fill to 150 from the 300 smallest remaining families.
Prints only whether each quota was met (the thread stays blind to class shares). Writes codex/g3_keys.json.
"""
import json, os, random
HERE = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(x) for x in open(os.path.join(HERE, "codex/smoke_families.jsonl"))]
pool = [r for r in rows if r.get("status") != "settled" and not str(r.get("class", "")).startswith("S") and r.get("class") != "unresolved"]
size = lambda r: (max(r.get("main_block_size") or 0, r.get("s_block_size") or 0), r["key"])
rng, panel, met = random.Random(7), [], {}
for c in ["grows", "bounded", "mixed by residue", "lost at large depths", "none at any depth"]:
    cand = sorted((r for r in pool if r["class"] == c), key=size)[:30]
    pick = rng.sample(cand, min(10, len(cand)))
    panel += pick
    met[c] = len(pick) == 10
chosen = {r["key"] for r in panel}
multi = sum(r["n_defs"] > 1 for r in panel)
if multi < 40:
    cand = sorted((r for r in pool if r["n_defs"] > 1 and r["key"] not in chosen), key=size)[:120]
    pick = rng.sample(cand, min(40 - multi, len(cand)))
    panel += pick; chosen |= {r["key"] for r in pick}
met["several definitions >= 40"] = sum(r["n_defs"] > 1 for r in panel) >= 40
cand = sorted((r for r in pool if r["key"] not in chosen), key=size)[:300]
panel += rng.sample(cand, min(150 - len(panel), len(cand)))
met["total 150"] = len(panel) == 150
json.dump([r["key"] for r in panel], open(os.path.join(HERE, "codex/g3_keys.json"), "w"), indent=0)
print(json.dumps(met))
