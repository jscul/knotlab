"""EVERY-RAY-20261113-001A, the thread's frozen stratified sample (pre-registration, third clarification), on Codex's runner unchanged.
Strata of eligible families (two or more SELF calls, not S1-S3) by the census's first-ray class: G first-ray growers (excluding the
224 one-definition growers of gate G-last), N first-ray none or lost, B first-ray bounded (carried split only). One Random(20261114)
stream draws sorted keys: G 300, then N 200, then B 100. Phase 2 reruns G and N families left unresolved by a cap at 1,000 s and
1,000,000 nodes. Run from the repository root:  sample_paths.py --phase 1|2"""
import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "codex"))
from pathlib import Path
import paths_dp as P
import run_paths as RP
out = Path(HERE) / "codex" / "sample"
out.mkdir(exist_ok=True)
recs = P.load_census_records()
eligible = sorted(P.eligible_keys(recs))
last224 = {c["key"] for c in json.load(open(os.path.join(HERE, "codex", "gate_last_keys.json")))["cases"]}
G = [k for k in eligible if recs[k]["class"] == "grows" and k not in last224]
N = [k for k in eligible if recs[k]["class"] in ("none at any depth", "lost at large depths")]
B = [k for k in eligible if recs[k]["class"] == "bounded"]
sel_path = out / "selection.json"
if sel_path.exists():
    sel = json.loads(sel_path.read_text())
else:
    rng = random.Random(20261114)
    sel = dict(seed=20261114, sizes=dict(G=len(G), N=len(N), B=len(B)),
               G=rng.sample(G, 300), N=rng.sample(N, 200), B=rng.sample(B, 100))
    sel_path.write_text(json.dumps(sel, indent=0))
phase = sys.argv[sys.argv.index("--phase") + 1]
if phase == "1":
    for s in ("G", "N", "B"):
        RP.run_tasks(sel[s], out / f"{s}.jsonl", 3, census_records=recs)
else:
    capped = []
    for s in ("G", "N"):
        for x in open(out / f"{s}.jsonl"):
            r = json.loads(x)
            if r.get("class") == "unresolved" and r.get("status") in ("timeout", "memory_limit", "done"):
                capped.append(r["key"])
    RP.run_tasks(sorted(capped), out / "phase2.jsonl", 3, census_records=recs, seconds=1000, node_cap=1_000_000)
