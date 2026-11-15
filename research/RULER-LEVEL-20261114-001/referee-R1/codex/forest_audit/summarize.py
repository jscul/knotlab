"""Produce the compact, digest-bound referee result from saved raw records."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(HERE))
import job


def records(folder):
    return [json.loads(line) for line in (HERE / folder / "results.jsonl").read_text().splitlines()]


raw, cross = records("run"), records("crosscheck_run")
assert all(row["status"] == "ok" for row in raw + cross)
by_case = {r["case"]: r["result"] for r in raw}
cross_case = {r["case"]: r["result"] for r in cross}
patterns = [p for row in raw if row["case"].startswith("random_") for p in row["result"]["patterns"]]
queries = [q for p in patterns for q in p["level_queries"]]
coverage = Counter()
for pattern in patterns:
    rows, levels = pattern["knots"], pattern["levels"]
    _, dist = job.incidence(rows, pattern["n"])
    components = len({tuple(v for v in range(pattern["n"]) if dist[u][v] is not None)
                      for u in range(pattern["n"])})
    coverage["with_multiple_components"] += components > 1
    coverage["with_within_level_knots"] += any(len({levels[v] for v in row}) == 1 for row in rows)
    coverage["with_path_without_descending_chain_query"] += any(q["path_without_descending_chain"] for q in pattern["level_queries"])
    coverage["pairs"] += pattern["pairs"]
    coverage["bonds"] += len(pattern["bonds"])
    coverage["truth_projections"] += pattern["tested_supports"]
summary = {
    "scope_id": "RULER-LEVEL-20261114-001",
    "lane": "independent forest theorem audit",
    "verdict": "A** and T1 sound for distinct endpoints; summary requires narrowing",
    "validation": "V2 independent same-task reimplementation; not external replication",
    "exhaustive": by_case["exhaustive_seven"],
    "random": {"patterns": len(patterns), "n_range": [min(p["n"] for p in patterns), max(p["n"] for p in patterns)],
               "seeds": [min(p["seed"] for p in patterns), max(p["seed"] for p in patterns)],
               "coverage": dict(coverage), "level_queries": len(queries),
               "descending_chain_queries": sum(q["descending_chain"] for q in queries),
               "no_path_queries": sum(q["minimum_distance_knots"] is None for q in queries),
               "path_without_descending_chain_queries": sum(q["path_without_descending_chain"] for q in queries),
               "T1_violations": sum(len(p["T1_violations"]) for p in patterns),
               "level_formula_violations": sum(not q["match"] for q in queries),
               "chain_equivalence_violations": sum(not q["chain_iff_distance_s"] for q in queries)},
    "controls": [{"name": f["name"], "forest": f["forest"], "states": f["states"],
                  "T1_formula_failures": f["T1_violations"],
                  "engine_crosschecks_agree": all(c["all_agree"] for c in f["engine_crosschecks"])}
                 for f in by_case["controls"]["fixtures"]],
    "malformed_repeated_member_triple_rejects": by_case["controls"]["malformed_rejected"],
    "ambient_detour": cross_case["ambient_detour"],
    "random_exact_engine_crosschecks": {
        "patterns": cross_case["random_exact_engines"]["patterns"],
        "level_queries": len(cross_case["random_exact_engines"]["level_query_crosschecks"]),
        "complete_bond_families": len(cross_case["random_exact_engines"]["complete_bond_family_crosschecks"]),
        "failures": cross_case["random_exact_engines"]["failures"]},
    "detour_active_truth": next(f for f in by_case["controls"]["fixtures"] if f["name"] == "within_level_detour"),
    "resources": {"compute_workers": 1, "case_memory_limit_gib": 1, "runner_memory_limit_gib": 2,
                  "total_case_seconds": sum(r["seconds"] for r in raw + cross),
                  "max_observed_rss_mib": max(max(r["peak_rss_mb"], r["result"]["resources"]["max_rss_kib"] / 1024) for r in raw + cross),
                  "raw_case_status_counts": dict(Counter(r["status"] for r in raw + cross))},
    "restrictions": {"producer_python_read_or_imported": False, "network_used": False,
                     "git_mutations": False, "writes_outside_lane": False},
    "source_sha256": {},
}
sources = [
    "proofs/RULER-LEVEL-20261114-001A/RULER-LEVEL-20261114-001A-P001_forest_ruler/proof.md",
    "proofs/RULER-LEVEL-20261114-001A/RULER-LEVEL-20261114-001A-P001_forest_ruler/result.json",
    "proofs/RANDOM-FATES-20261112-001B/RANDOM-FATES-20261112-001B-P001_no_cycle_and_four_consecutive/proof.md",
    "research/RULER-LEVEL-20261114-001/ruler_level.md",
    "research/RULER-LEVEL-20261114-001/advisor_question.md",
    "research/RULER-LEVEL-20261114-001/advisor_answer.md",
    "research/LEVEL-REACH-20261114-001/referee-R1/codex/fresh_search.py",
    "research/LEVEL-REACH-20261114-001/referee-R1/codex/fresh_pattern.py",
    "research/LEVEL-REACH-20261114-001/referee-R1/codex/brute_audit/brute_supports.py",
]
sources += [str(p.relative_to(ROOT)) for p in (HERE / "job.py", HERE / "crosscheck_job.py", HERE / "summarize.py")]
for name in sources:
    summary["source_sha256"][name] = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
assert not summary["exhaustive"]["violations"]
assert not summary["random"]["T1_violations"]
assert not summary["random"]["level_formula_violations"]
assert not summary["random"]["chain_equivalence_violations"]
assert not summary["random_exact_engine_crosschecks"]["failures"]
(HERE / "results.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({k: summary[k] for k in ("verdict", "random", "random_exact_engine_crosschecks", "resources")}, indent=2))
