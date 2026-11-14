"""Independent outcome/provenance reconciliation, without producer imports.

Reads only the explicitly admitted data, specification, and JSON provenance.
Writes beside this script. No solver, source execution, network, or theorem claim.
Run: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -B <this file>
"""

from __future__ import annotations

import collections
import gzip
import hashlib
import itertools
import json
import math
import resource
from pathlib import Path

resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))

import numpy as np


ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
ART = ROOT / "artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach"
CODEX = ROOT / "experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex"
RESEARCH = ROOT / "research/LEVEL-REACH-20261114-001"
BOOTSTRAP_SEED = 20261114
BOOTSTRAP_REPLICATES = 100_000


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def read_gzip(name):
    with gzip.open(ART / name, "rt") as handle:
        for line in handle:
            yield json.loads(line)


def weight(record):
    return sum(m["family"] == "W_R" and m["index"] < 2000 for m in record["memberships"])


def profile(record):
    return [entry["L_N"] for entry in record["levels"]]


def classify(record):
    values = profile(record)
    if record["union"] != "alive":
        return record["union"]
    if record["flags"]["no_join"]:
        return "no join"
    if "none" in values:
        return "no bond"
    if "undecided" in values:
        return "undecided"
    if values == [3, 4, 5, 6]:
        return "chained"
    if all(type(value) is int for value in values) and len(set(values)) == 1:
        return "direct"
    return "other"


def compatible(record, kind):
    values = profile(record)
    if kind == "chained":
        return all(v == "undecided" or v == gap + 2 for gap, v in enumerate(values, 1))
    if kind == "direct":
        return all(type(v) is int or v == "undecided" for v in values) and len(
            {v for v in values if type(v) is int}
        ) <= 1
    raise ValueError(kind)


def counts(records, weighted=False):
    result = collections.Counter()
    for record in records:
        amount = weight(record) if weighted else 1
        if amount:
            result[classify(record)] += amount
    return dict(result)


def wilson(successes, size):
    if not size:
        return None
    z = 1.96
    rate = successes / size
    denominator = 1 + z * z / size
    center = (rate + z * z / (2 * size)) / denominator
    half = z * math.sqrt(rate * (1 - rate) / size + z * z / (4 * size * size)) / denominator
    return [max(0, center - half), min(1, center + half)]


canonical_cache = {}


def automaton(record, mode="canonical"):
    raw = tuple([record["key"][0]] + [tuple(v) for v in record["key"][1:4]])
    if mode == "raw":
        return raw
    cache_key = raw, mode
    if cache_key in canonical_cache:
        return canonical_cache[cache_key]
    size, swaps, d0, d1 = raw
    candidates = []
    for ordering in itertools.permutations(range(size)):
        inverse = {old: new for new, old in enumerate(ordering)}
        normalized = (
            size,
            tuple(swaps[old] for old in ordering),
            tuple(inverse[d0[old]] for old in ordering),
            tuple(inverse[d1[old]] for old in ordering),
        )
        candidates.append(normalized)
        if mode == "canonical":
            candidates.append((normalized[0], normalized[1], normalized[3], normalized[2]))
    canonical_cache[cache_key] = min(candidates)
    return canonical_cache[cache_key]


def bootstrap(groups, joint):
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    if not joint:
        rates = []
        for activity in ("exponential", "finitary"):
            data = np.asarray([groups[activity][key] for key in sorted(groups[activity])])
            indices = rng.integers(0, len(data), size=(BOOTSTRAP_REPLICATES, len(data)))
            totals = data[indices].sum(axis=1)
            rates.append(totals[:, 0] / totals[:, 1])
        differences = rates[0] - rates[1]
    else:
        keys = sorted(set(groups["exponential"]) | set(groups["finitary"]))
        data = np.asarray([
            [*groups["exponential"].get(key, [0, 0]), *groups["finitary"].get(key, [0, 0])]
            for key in keys
        ])
        # Batches bound peak memory while preserving deterministic random order.
        differences = np.empty(BOOTSTRAP_REPLICATES)
        for start in range(0, BOOTSTRAP_REPLICATES, 5000):
            stop = min(start + 5000, BOOTSTRAP_REPLICATES)
            indices = rng.integers(0, len(data), size=(stop - start, len(data)))
            totals = data[indices].sum(axis=1)
            differences[start:stop] = totals[:, 0] / totals[:, 1] - totals[:, 2] / totals[:, 3]
    return {
        "replicates": BOOTSTRAP_REPLICATES,
        "seed": BOOTSTRAP_SEED,
        "rng": "numpy.random.default_rng",
        "quantile_method": "linear",
        "joint_automaton_resampling": joint,
        "ci95": np.quantile(differences, [0.025, 0.975]).tolist(),
    }


slim = list(read_gzip("records_slim.jsonl.gz"))
by_case = {record["case"]: record for record in slim}
labels = {record["case"]: classify(record) for record in slim}
description_counts = counts(slim)
weighted_counts = counts(slim, True)
alive = sum(weight(r) for r in slim if r["union"] == "alive")
none = weighted_counts["no join"] + weighted_counts["no bond"]
conditioned = alive - none
undecided = [r for r in slim if classify(r) == "undecided"]
compatibility = {
    kind: {
        "descriptions": sum(compatible(r, kind) for r in undecided),
        "W_weight": sum(weight(r) for r in undecided if compatible(r, kind)),
        "cases": [r["case"] for r in undecided if compatible(r, kind)],
    }
    for kind in ("chained", "direct")
}
loose = {}
tight = {}
for kind in ("chained", "direct"):
    loose[kind] = [weighted_counts[kind] / alive, (weighted_counts[kind] + weighted_counts["undecided"]) / alive]
    tight[kind] = [weighted_counts[kind] / alive, (weighted_counts[kind] + compatibility[kind]["W_weight"]) / alive]
loose["none"] = [none / alive, (none + weighted_counts["undecided"]) / alive]
tight["none_frozen_label"] = [none / alive, none / alive]

per_s = {}
for gap in range(1, 5):
    counter = collections.Counter()
    for r in slim:
        counter[str(r["levels"][gap - 1]["L_N"])] += weight(r)
    per_s[str(gap)] = dict(counter)

by_activity = {
    activity: counts([r for r in slim if r["classes"]["relative"]["class"] == activity], True)
    for activity in sorted({r["classes"]["relative"]["class"] for r in slim})
}

other_profiles = {}
for r in slim:
    if classify(r) != "other":
        continue
    key = json.dumps(profile(r), separators=(",", ":"))
    item = other_profiles.setdefault(key, {"profile": profile(r), "descriptions": 0, "W_weight": 0, "cases": []})
    item["descriptions"] += 1
    item["W_weight"] += weight(r)
    item["cases"].append(r["case"])

q5 = {}
for activity in ("bounded", "polynomial", "exponential_W"):
    selected = [
        r for r in slim
        if (activity == "exponential_W" and r["classes"]["relative"]["class"] == "exponential" and weight(r))
        or (activity != "exponential_W" and r["classes"]["relative"]["class"] == activity
            and any(m["family"] == "E_R" for m in r["memberships"]))
    ]
    counter = counts(selected, activity == "exponential_W")
    denominator = sum(counter.get(label, 0) for label in ("chained", "direct", "other"))
    item = {
        "outcomes": counter,
        "decided_bond_profile_denominator": denominator,
        "ruler": counter.get("chained", 0) / denominator,
        "ruler_ci": wilson(counter.get("chained", 0), denominator),
        "direct": counter.get("direct", 0) / denominator,
        "direct_ci": wilson(counter.get("direct", 0), denominator),
    }
    item["weight" if activity == "exponential_W" else "descriptions"] = sum(counter.values())
    q5[activity] = item

q4_modes = {}
for mode in ("raw", "state_relabeling", "canonical"):
    groups = {}
    for activity in ("exponential", "finitary"):
        group = collections.defaultdict(lambda: [0, 0])
        for r in slim:
            label = classify(r)
            if r["classes"]["relative"]["class"] != activity or label not in ("chained", "direct", "other") or not weight(r):
                continue
            key = automaton(r, mode)
            group[key][0] += weight(r) * (label != "chained")
            group[key][1] += weight(r)
        groups[activity] = dict(group)
    shared = sorted(set(groups["exponential"]) & set(groups["finitary"]))
    item = {
        "clusters": [len(groups["exponential"]), len(groups["finitary"])],
        "shared_automata": [
            {"automaton": key, "exponential": groups["exponential"][key], "finitary": groups["finitary"][key]}
            for key in shared
        ],
        "totals": {activity: np.asarray(list(group.values())).sum(axis=0).tolist() for activity, group in groups.items()},
    }
    if mode == "canonical":
        item["independent_by_activity"] = bootstrap(groups, False)
        item["joint_across_activity"] = bootstrap(groups, True)
        dump("q4_clusters.json", {
            activity: [{"automaton": key, "nonruler_weight": group[key][0], "total_weight": group[key][1]} for key in sorted(group)]
            for activity, group in groups.items()
        })
    q4_modes[mode] = item

consistency_errors = []
found_bonds = 0
deep_bonds = []
equal_restricted = 0
restricted_undecided = []
certificate_flags = collections.Counter()
certificate_hash_pairs = set()
record_certificates = 0
statuses = collections.Counter()
job_shas = collections.Counter()
budgets = collections.Counter()
budget_scopes = collections.Counter()
finish_times = []
histogram_nonnull = 0
slim_histogram_missing = 0
overshoot_mismatches = []


def record_refs(obj):
    global record_certificates
    if isinstance(obj, dict):
        if "proof_sha256" in obj and "cnf_sha256" in obj:
            record_certificates += 1
            certificate_hash_pairs.add((obj["cnf_sha256"], obj["proof_sha256"]))
            certificate_flags.update((key, str(obj.get(key))) for key in ("checked", "deleted_after_check", "unanchored"))
        for value in obj.values():
            record_refs(value)
    elif isinstance(obj, list):
        for value in obj:
            record_refs(value)


for outer in read_gzip("results.jsonl.gz"):
    case = outer["case"]
    statuses[outer["status"]] += 1
    job_shas[outer["job_sha"]] += 1
    finish_times.append(outer["finished_at"])
    full = outer["result"]
    short = by_case[case]
    budgets[full["budget_seconds_per_key_s"]] += 1
    budget_scopes[full["budget_scope"]] += 1
    record_refs(full)
    for key in ("case", "key", "memberships", "flags", "classes", "knot_count", "seconds"):
        if short[key] != full[key]:
            consistency_errors.append({"case": case, "field": key, "kind": "slim_full_mismatch"})
    if short["union"] != full["union"]["verdict"]:
        consistency_errors.append({"case": case, "field": "union", "kind": "slim_full_mismatch"})
    if short["certificate_totals"] != full["checked_certificate_totals"]:
        consistency_errors.append({"case": case, "field": "certificate_totals", "kind": "slim_full_mismatch"})
    for gap, (entry, abbreviated) in enumerate(zip(full["levels"], short["levels"]), 1):
        for field in ("s", "components", "L_N", "L_target"):
            if entry[field] != abbreviated[field]:
                consistency_errors.append({"case": case, "s": gap, "field": field, "kind": "slim_full_mismatch"})
        if entry.get("histogram") is not None:
            histogram_nonnull += 1
            if abbreviated.get("per_target_hist") is None:
                slim_histogram_missing += 1
        anywhere = entry.get("anywhere", {})
        if abbreviated["bond"] != anywhere.get("bond"):
            consistency_errors.append({"case": case, "s": gap, "field": "bond", "kind": "slim_full_mismatch"})
        if type(entry["L_N"]) is not int:
            continue
        found_bonds += 1
        bond = anywhere["bond"]
        levels = [(v + 1).bit_length() - 1 for v in bond]
        target = 3 + gap
        overshoot = max(levels) - target
        if entry.get("overshoot") != overshoot:
            overshoot_mismatches.append({"case": case, "s": gap, "reported": entry.get("overshoot"), "computed": overshoot})
        if len(bond) != entry["L_N"] or not anywhere["optimality_proved"]:
            consistency_errors.append({"case": case, "s": gap, "kind": "numeric_bond_shape_or_optimality"})
        if entry["L_target"] == entry["L_N"]:
            equal_restricted += 1
        elif entry["L_target"] == "undecided":
            restricted_undecided.append({"case": case, "s": gap, "L_N": entry["L_N"], "bond": bond, "levels": levels})
        else:
            consistency_errors.append({"case": case, "s": gap, "kind": "L_N_L_target_disagreement", "values": [entry["L_N"], entry["L_target"]]})
        if overshoot > 0:
            restricted_bond = entry["target_restricted"].get("bond")
            restricted_levels = [(v + 1).bit_length() - 1 for v in restricted_bond or []]
            deep_bonds.append({
                "case": case, "s": gap, "L_N": entry["L_N"], "L_target": entry["L_target"],
                "bond": bond, "levels": levels, "overshoot": overshoot,
                "target_bond": restricted_bond, "target_levels": restricted_levels,
                "equal_size_in_target": len(restricted_bond or []) == entry["L_N"] and max(restricted_levels, default=999) <= target,
                "W_weight": weight(short), "key": full["key"],
            })

flag_errors = []
for record in slim:
    placements = record["key"][4]
    expected = {
        "no_join": not any(any(term % 3 == 0 for term in p) and any(term % 3 != 0 for term in p) for p in placements),
        "tree_only": all(p == [0, 1, 2] for p in placements),
        "s1": record["key"][0] == 1,
    }
    if record["flags"] != expected:
        flag_errors.append({"case": record["case"], "reported": record["flags"], "computed": expected})

q3 = {
    "found_bonds": found_bonds,
    "recorded_anywhere_bonds_below_target": len(deep_bonds),
    "descriptions_with_deep_bonds": len({entry["case"] for entry in deep_bonds}),
    "by_s": dict(collections.Counter(entry["s"] for entry in deep_bonds)),
    "deep_bonds": deep_bonds,
    "numeric_L_target_equal": equal_restricted,
    "L_target_undecided": restricted_undecided,
    "all_deep_have_equal_size_in_target": all(entry["equal_size_in_target"] for entry in deep_bonds),
    "all_numeric_have_a_reported_least_bond_in_target": all(entry["equal_size_in_target"] for entry in deep_bonds)
        and all(max(entry["levels"]) <= 3 + entry["s"] for entry in restricted_undecided),
    "overshoot_field_mismatches": overshoot_mismatches,
    "frozen_literal_verdict": "fails: every least bond found does not lie within its target",
    "narrower_existential_verdict": "supported by reported representatives, subject to independent search/certificate validity",
}
dump("q3_membership.json", q3)

selection = json.loads((CODEX / "mono_selection.json").read_text())
mono_rows = []
mono_ok = {}
mono_file_statuses = {}
mono_paths = [CODEX / "mono_gate/results.jsonl"] + sorted(CODEX.glob("mono*retry*/results.jsonl"))
for path in mono_paths:
    status_counts = collections.Counter()
    for line in path.read_text().splitlines():
        row = json.loads(line)
        status_counts[row["status"]] += 1
        item = {key: row.get(key) for key in ("case", "status", "error", "seconds", "peak_rss_mb", "job_sha", "finished_at")}
        item["file"] = str(path.relative_to(ROOT))
        mono_rows.append(item)
        if row["status"] == "ok":
            result = row["result"]
            mono_ok[row["case"]] = {
                "case": row["case"], "key": result["key"], "comparisons": result["comparisons"],
                "reported_passed": result["passed"], "file": item["file"],
                "N9_alive": result["N9"]["union"]["verdict"], "N10_alive": result["N10"]["union"]["verdict"],
            }
    mono_file_statuses[str(path.relative_to(ROOT))] = dict(status_counts)
comparisons = [dict(entry, case=key) for key, result in mono_ok.items() for entry in result["comparisons"]]
numeric = [entry for entry in comparisons if type(entry["L_9"]) is int and type(entry["L_10"]) is int]
mono = {
    "selected_keys": len(selection), "successful_unique_keys": len(mono_ok),
    "missing_selected_keys": sorted(set(selection) - set(mono_ok)),
    "unexpected_successful_keys": sorted(set(mono_ok) - set(selection)),
    "numeric_comparisons": len(numeric),
    "equal_numeric_comparisons": sum(entry["L_9"] == entry["L_10"] for entry in numeric),
    "decreases": [entry for entry in numeric if entry["L_10"] < entry["L_9"]],
    "increases": [entry for entry in numeric if entry["L_10"] > entry["L_9"]],
    "file_statuses": mono_file_statuses, "attempts": mono_rows, "successful_results": list(mono_ok.values()),
}
dump("monotonicity.json", mono)

input_hashes = {}
for name in ("records_slim.jsonl.gz", "results.jsonl.gz", "summary.json", "raw_hashes.json"):
    path = ART / name
    input_hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    if name.endswith(".gz"):
        digest = hashlib.sha256()
        with gzip.open(path, "rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        input_hashes[str(path.relative_to(ROOT)) + ":uncompressed"] = digest.hexdigest()
raw_hashes = json.loads((ART / "raw_hashes.json").read_text())
registered_hash_matches = raw_hashes["registered/results.jsonl"] == input_hashes[str((ART / "results.jsonl.gz").relative_to(ROOT)) + ":uncompressed"]
provenance = {
    "input_hashes": input_hashes, "registered_raw_hash_matches": registered_hash_matches,
    "pilot_hash_not_rechecked": "Pilot raw file is outside this worker's admitted inputs.",
    "record_statuses": dict(statuses), "job_shas": dict(job_shas), "budget_seconds_per_key_s": dict(budgets),
    "budget_scopes": dict(budget_scopes), "finish_timestamp_range": [min(finish_times), max(finish_times)],
    "refutation_metadata_occurrences": record_certificates, "unique_CNF_proof_hash_pairs": len(certificate_hash_pairs),
    "refutation_metadata_flags": {f"{key}={value}": count for (key, value), count in certificate_flags.items()},
    "certificate_files_not_rechecked": "Only JSON retention metadata inspected; actual CNF/LRAT files are outside this worker's admitted inputs.",
    "provenance_documents": {path.name: json.loads(path.read_text()) for path in sorted(CODEX.glob("*provenance*.json"))},
    "gate_metadata": {},
    "limitations": [
        "No producer Python or C source was opened, imported, hashed, or executed.",
        "Budget/population/retention behavior is reconciled from records and documentary specifications, not source inspection.",
        "Memoization and presence-encoding JSON claims do not independently prove semantic equivalence of the executed sources.",
        "Presence-encoding controls disclose finite checks; memoization provenance explicitly allows timing, representative, and undecided changes.",
        "The specification permits pre-run population cuts; preregistration fixes first 2000 W_R samples and E_R relative-class filter.",
    ],
}
for path in sorted(CODEX.glob("g_*.json")):
    gate = json.loads(path.read_text())
    provenance["gate_metadata"][path.name] = {key: value for key, value in gate.items() if key not in ("cases", "additional_depth_checks")}
dump("provenance_audit.json", provenance)

memberships = [m for r in slim for m in r["memberships"]]
registered_W = [m for m in memberships if m["family"] == "W_R" and m["index"] < 2000]
population = {
    "description_rows": len(slim), "unique_cases": len(by_case),
    "W_R_accepted_samples_below_2000": len(registered_W),
    "W_R_unique_sample_indices_below_2000": len({m["index"] for m in registered_W}),
    "W_R_distinct_descriptions": sum(weight(r) > 0 for r in slim),
    "W_R_attached_memberships_at_or_above_2000_excluded": sum(m["family"] == "W_R" and m["index"] >= 2000 for m in memberships),
    "E_R_memberships": sum(m["family"] == "E_R" for m in memberships),
    "E_R_distinct_descriptions": sum(any(m["family"] == "E_R" for m in r["memberships"]) for r in slim),
    "W_E_overlap_descriptions": sum(weight(r) > 0 and any(m["family"] == "E_R" for m in r["memberships"]) for r in slim),
    "unrepresented_first_2000_indices": sorted(set(range(2000)) - {m["index"] for m in registered_W}),
    "unrepresented_index_status": "Not independently classified as rejected here; no producer sampler imported.",
}

summary = {
    "population": population,
    "cases": dict(statuses), "descriptions": len(slim),
    "outcomes_by_description": description_counts, "outcomes_by_weight_W": weighted_counts,
    "outcomes_by_class_W": by_activity, "L_by_s_W": per_s,
    "Q0": {"alive_draws": alive, "loose_supplied_style": loose, "tight_by_known_levels": tight},
    "Q1_Q2": {
        "connected_non_none_weight": conditioned,
        "proven_numeric_at_every_s_weight": sum(weight(r) for r in slim if all(type(v) is int for v in profile(r))),
        "any_greater_than_10_weight": sum(weight(r) for r in slim if "> 10" in profile(r)),
        "ruler_loose": [weighted_counts["chained"] / conditioned, (weighted_counts["chained"] + weighted_counts["undecided"]) / conditioned],
        "ruler_tight_fixed_denominator": [weighted_counts["chained"] / conditioned, (weighted_counts["chained"] + compatibility["chained"]["W_weight"]) / conditioned],
        "direct_loose": [weighted_counts["direct"] / conditioned, (weighted_counts["direct"] + weighted_counts["undecided"]) / conditioned],
        "direct_tight_fixed_denominator": [weighted_counts["direct"] / conditioned, (weighted_counts["direct"] + compatibility["direct"]["W_weight"]) / conditioned],
        "interpretation": "893 is a connected/non-none-label denominator; existence of a bond at every s is not proved for its 150 undecided and 13 >10 W weight.",
        "frozen_Q1_rule": "not falsified; upper bound >=70%; lower bound <70% does not establish prediction",
        "frozen_Q2_rule": "not falsified; lower bound <=10%; upper bound >10% does not establish prediction",
    },
    "Q3": {key: value for key, value in q3.items() if key != "deep_bonds"},
    "Q4": q4_modes, "Q5": q5,
    "undecided_compatibility": compatibility, "other_profiles": list(other_profiles.values()),
}
dump("independent_summary.json", summary)
dump("classification_consistency.json", {
    "full_vs_slim_errors": consistency_errors, "independent_flag_errors": flag_errors,
    "full_histogram_nonnull_level_rows": histogram_nonnull,
    "slim_per_target_hist_null_despite_full_histogram": slim_histogram_missing,
    "note": "Slim per_target_hist is null despite available full histogram; primary L_N classification fields agree.",
})

with (OUT / "classifications.jsonl").open("w") as handle:
    for r in slim:
        handle.write(json.dumps({
            "case": r["case"], "label": classify(r), "profile": profile(r), "W_weight": weight(r),
            "relative_class": r["classes"]["relative"]["class"],
            "E_R": any(m["family"] == "E_R" for m in r["memberships"]),
            "ruler_compatible": compatible(r, "chained") if classify(r) == "undecided" else None,
            "direct_compatible": compatible(r, "direct") if classify(r) == "undecided" else None,
        }, sort_keys=True) + "\n")

supplied = json.loads((ART / "summary.json").read_text())
exact_checks = {}
for key in ("cases", "descriptions", "outcomes_by_description", "outcomes_by_weight_W", "outcomes_by_class_W", "L_by_s_W"):
    exact_checks[key] = supplied[key] == summary[key]
for activity in ("bounded", "polynomial", "exponential_W"):
    exact_checks["Q5_" + activity] = all(
        supplied["Q5"][activity][key] == value
        for key, value in q5[activity].items() if key in supplied["Q5"][activity]
    )
dump("discrepancies.json", {
    "exact_supplied_field_checks": exact_checks,
    "research_and_artifact_summary_equal": supplied == json.loads((RESEARCH / "summary.json").read_text()),
    "substantive": [
        {"id": "Q3-frozen-literal", "recommendation": "Block", "supplied": "count_below=0; every least bond found within target; Q3 holds", "independent": f"{len(deep_bonds)} anywhere bond representatives have positive overshoot; all have equal-size in-target alternatives", "evidence": "q3_membership.json"},
        {"id": "uncertainty-bands", "recommendation": "Narrowing", "supplied": "all 150 undecided W weight added to each upper bound", "independent": "126 ruler-compatible;91 direct-compatible;0 can change to frozen disconnected/no-join label", "evidence": "independent_summary.json"},
        {"id": "Q1-Q2-interpretation", "recommendation": "Narrowing", "supplied": "predictions held", "independent": "not falsified by asymmetric frozen failure criteria; neither prediction established by its full uncertainty band", "evidence": "independent_summary.json"},
        {"id": "Q1-Q2-denominator", "recommendation": "Narrowing", "supplied": "893 with a bond at every s", "independent": "730 have numeric bonds every s;150 undecided and13 >10 are included in893", "evidence": "independent_summary.json"},
        {"id": "Q4-reproducibility", "recommendation": "Narrowing", "supplied": "99/40 automaton classes;CI[-0.05626,0.40320]", "independent": "99/40 reproduced under state relabeling plus binary-letter conjugation; unstated bootstrap details prevent exact interval reproduction; seven automata cross activity groups; joint resampling sensitivity retained", "evidence": "q4_clusters.json"},
        {"id": "Q5-intervals", "recommendation": "Narrowing", "supplied": "intervals for E classes only", "independent": "exponential_W intervals were also requested; ordinary Wilson intervals ignore repeated-automaton dependence and do not repair censoring", "evidence": "independent_summary.json"},
        {"id": "G-mono-completion", "recommendation": "Block", "supplied": "50-key gate required;49/50 completed disclosed", "independent": "49 unique successful keys;108 equal numeric comparisons;one selected key has four memory failures", "evidence": "monotonicity.json"},
        {"id": "slim-histograms", "recommendation": "Narrowing", "supplied": "slim per_target_hist field", "independent": f"{slim_histogram_missing} null slim fields discard full histogram values; no primary classification mismatch", "evidence": "classification_consistency.json"},
        {"id": "provenance-only", "recommendation": "Not a block", "supplied": "disclosed implementation/budget/population/retention changes", "independent": "admitted metadata is internally consistent for300-second budgets and retention; semantic equivalence and pre-freeze chronology not independently established by this worker", "evidence": "provenance_audit.json"},
    ],
})

print(json.dumps({
    "descriptions": len(slim), "W_weight": sum(weight(r) for r in slim),
    "exact_checks": exact_checks,
    "consistency_errors": len(consistency_errors), "flag_errors": len(flag_errors),
    "Q3_deep_bonds": len(deep_bonds), "Q3_deep_descriptions": q3["descriptions_with_deep_bonds"],
    "Q3_by_s": q3["by_s"], "Q3_all_deep_have_equal_target_alternative": q3["all_deep_have_equal_size_in_target"],
    "mono_successful": len(mono_ok), "mono_numeric": len(numeric),
    "Q4_independent": q4_modes["canonical"]["independent_by_activity"]["ci95"],
    "Q4_joint": q4_modes["canonical"]["joint_across_activity"]["ci95"],
    "peak_rss_MB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
}, indent=2))
