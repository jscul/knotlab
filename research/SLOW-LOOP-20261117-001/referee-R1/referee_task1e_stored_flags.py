"""SLOW-LOOP-R1 task 1e: the stored runs' own soundness flags (test/, stress/, posthoc/ results.jsonl): contradictions
reported, runs unsolved, runs solved but failing the engine's verification. Output: referee_task1e_stored_flags.json."""
import collections, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "../../../artifacts/SLOW-LOOP-20261117-001A/SLOW-LOOP-20261117-001A-E001_slow_loop")
out = {}
for stage in ("test", "stress", "posthoc"):
    c = collections.Counter(); uns = collections.Counter()
    for line in open(os.path.join(ART, stage, "results.jsonl")):
        r = json.loads(line)
        x = r.get("result")
        if r.get("status") != "ok" or not x:
            c["records_not_ok"] += 1; continue
        if x["arm"] == "CDCL":
            c["cdcl_records"] += 1
            c["cdcl_model_not_ok"] += int(x["cdcl"].get("model_ok") is False); continue
        for q in x["runs"]:
            c["runs"] += 1
            c["contradiction"] += int(bool(q.get("contradiction")))
            c["unsolved"] += int(not q["solved"])
            c["solved_but_unverified"] += int(q["solved"] and q.get("verified") is not True)
            if not q["solved"]:
                uns[f'{x["cell"]}|{x["arm"]}|{x["seed"]}'] += 1
    out[stage] = {"counts": dict(c), "unsolved_by_cell_arm_seed": dict(uns)}
json.dump(out, open(os.path.join(HERE, "referee_task1e_stored_flags.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
