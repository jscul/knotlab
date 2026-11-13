"""PROVED-RATE-R1: the referee's audit of the three batches against the merged file (Codex was barred from the batch files)."""
import json
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
E = ROOT / "experiments/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/codex"
A = ROOT / "artifacts/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/rates_all.jsonl"
load = lambda p: [json.loads(x) for x in open(p) if x.strip()]
b = {n: load(E / n) for n in ("rates_first_508.jsonl", "rates_next_92.jsonl", "rates_last_64.jsonl")}
ids = [r["idx"] for x in b.values() for r in x]
allr = {r["idx"]: r for r in load(A)}
sci = ["lambda", "bounded_all", "zero_mean", "complete", "nodes", "trimmed_nodes", "gate_ok", "L_recomputed"]
out = dict(batch_sizes={k: len(v) for k, v in b.items()}, total=len(ids), unique=len(set(ids)),
           duplicates=[k for k, v in Counter(ids).items() if v > 1], missing=sorted(set(allr) - set(ids)),
           rows_differing=sum(1 for x in b.values() for r in x if any(r.get(k) != allr[r["idx"]].get(k) for k in sci)))
print(json.dumps(out))
json.dump(out, open(Path(__file__).with_name("result_history.json"), "w"), indent=1)
