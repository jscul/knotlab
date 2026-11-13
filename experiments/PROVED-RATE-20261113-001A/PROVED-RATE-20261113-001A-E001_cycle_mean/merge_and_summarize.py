"""Merge Codex's three batches (its first run, killed with its session after 508 families; then two runs of its own runner on the
rest, the first killed for memory after 92) into one record per family, and summarise with Codex's make_summary plus the counts the
pre-registration tests. Run from the repository root."""
import json, os, sys
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(HERE, "codex")
sys.path.insert(0, C)
import run_rates as RR
OUT = os.path.join(HERE, "../../../artifacts/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean")
rows = {}
for f in ("rates_first_508.jsonl", "rates_next_92.jsonl", "rates_last_64.jsonl"):
    for line in open(os.path.join(C, f)):
        r = json.loads(line)
        rows.setdefault(r["idx"], r)
rows = sorted(rows.values(), key=lambda r: r["idx"])
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "rates_all.jsonl"), "w") as f:
    for r in rows:
        f.write(json.dumps(r, sort_keys=True) + "\n")
S = dict(codex_summary=RR.make_summary(rows, 0, 7))
comp = [r for r in rows if r["complete"]]
pos = lambda r: bool(r["lambda_float"]) and r["lambda_float"] > 0
S["families"], S["complete"], S["gate_mismatches"] = len(rows), len(comp), sum(r.get("gate_ok") is False for r in rows)
S["P1_complete_share_of_653"] = round(sum(r["complete"] for r in rows if r["gate_status"] != "skipped_no_record_L") / 653, 4)
by = {}
for cl in ("bounded", "rising", "flat", "capped", None):
    R = [r for r in comp if r["record_class"] == cl]
    by[str(cl)] = dict(complete=len(R), lambda_positive=sum(pos(r) for r in R), zero_mean=sum(r["zero_mean"] is True for r in R),
                       bounded_all=sum(r["bounded_all"] is True for r in R), lambda_none=sum(r["lambda"] is None for r in R),
                       rates=dict(Counter(r["lambda"] for r in R if pos(r))))
S["by_record_class"] = by
S["P2_rising_lambda_positive_share"] = round(by["rising"]["lambda_positive"] / by["rising"]["complete"], 4)
S["P3_flat_bounded_all_share"] = round(by["flat"]["bounded_all"] / by["flat"]["complete"], 4)
S["all_complete"] = dict(lambda_positive=sum(pos(r) for r in comp), zero_mean=sum(r["zero_mean"] is True for r in comp),
                         bounded_all=sum(r["bounded_all"] is True for r in comp), lambda_none=sum(r["lambda"] is None for r in comp),
                         rates=dict(Counter(r["lambda"] for r in comp if pos(r))))
json.dump(S, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in S.items() if k != "codex_summary"}, indent=1))
