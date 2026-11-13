"""Independent archive identity and carried-port audit for TRUE-RATE referee R1.

The default execution imports no study implementation.  It consumes the saved
inventory and independently reconstructs its ordered definitions from the eight
LIMIT-ONLY sample archives.  --refresh-inventory uses only the expressly permitted
BOND-DEPTH families_one_def helper; automatic imports by that helper are allowed.
No TRUE-RATE implementation is opened or imported.

Run with the absolute workspace .venv/bin/python -B path.  Single process;
address-space ceiling 2 GiB.  All outputs stay beside this source file.
"""

from __future__ import annotations

import argparse
import collections
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import time


ROOT = Path("/home/jscul/p-vs-np-contact-first")
OUT = ROOT / "research/TRUE-RATE-20261113-001/referee-R1/codex"
SAMPLES = ROOT / "artifacts/LIMIT-ONLY-20261112-001A/LIMIT-ONLY-20261112-001A-E001_limit_only"
BRANCH = ROOT / "artifacts/BRANCH-DEPTH-20261112-001C/BRANCH-DEPTH-20261112-001C-E001_port_census"
RAYS = ROOT / "artifacts/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/rates_all.jsonl"
TRUE = ROOT / "artifacts/TRUE-RATE-20261113-001A/TRUE-RATE-20261113-001A-E001_true_rates/true_rates_all.jsonl"
HELPER = ROOT / "experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/census.py"


def canonical(value):
    """Preserve every definition, call and argument in its original order."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def key_hash(key):
    return hashlib.sha256(key.encode()).hexdigest()


def file_hash(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def usual(defs):
    """Add the own-port NAE when SELF receives a permutation of all ports.

    A single added copy suffices because NAE is symmetric and idempotent.
    None of the 664 surviving definitions needs this transformation.
    """
    result = []
    for arity, nlocals, calls in defs:
        body = [[callee, list(args)] for callee, args in calls]
        if any(callee == "SELF" and sorted(args) == list(range(arity))
               for callee, args in body):
            body.append(["K", list(range(arity))])
        result.append([arity, nlocals, body])
    return result


def project_assignment(env, args):
    return sum(((env >> var) & 1) << position for position, var in enumerate(args))


def valid_envs(defs, relation):
    arity, nlocals, calls = defs[0]
    for env in range(1 << (arity + nlocals)):
        for callee, args in calls:
            values = project_assignment(env, args)
            if callee == "K":
                good = values not in (0, (1 << len(args)) - 1)
            elif callee == "SELF":
                good = bool(relation & (1 << values))
            else:
                raise ValueError(f"Unexpected one-definition callee: {callee!r}")
            if not good:
                break
        else:
            yield env


def greatest_port_relation(defs):
    """Fresh scalar exhaustive truth tables; start with all eight port states."""
    assert len(defs) == 1 and defs[0][0] == 3
    relation = 255
    sequence = [relation]
    while True:
        successor = 0
        for env in valid_envs(defs, relation):
            successor |= 1 << (env & 7)
        assert successor & ~relation == 0
        sequence.append(successor)
        if successor == relation:
            return relation, sequence
        relation = successor


def first_transition(defs, relation):
    args = next(args for callee, args in defs[0][2] if callee == "SELF")
    return sorted({(env & 7, project_assignment(env, args))
                   for env in valid_envs(defs, relation)})


def cycles_and_carried(args):
    """Count only cycle members, excluding paths that merely reach a cycle."""
    cycles = []
    carried = []
    for start in range(3):
        current = start
        path = []
        while current < 3 and current not in path:
            path.append(current)
            current = args[current]
        if current == start:
            carried.append(start)
            if min(path) == start:
                cycles.append(path)
    return cycles, carried


def actual_top_identities(args, depth=6):
    """Separate check: unfold identities, assigning fresh locals at each copy."""
    ports = [("top", i) for i in range(3)]
    per_depth = []
    for level in range(depth):
        env = ports + [("local", level, j) for j in range(3, max(args + [2]) + 1)]
        ports = [env[arg] for arg in args]
        per_depth.append(sorted(item[1] for item in ports if item[0] == "top"))
    return sorted(set(per_depth[-1])), per_depth


def duplicate_values(values):
    return sorted((value, count) for value, count in collections.Counter(values).items() if count > 1)


def load_jsonl(path):
    with path.open() as handle:
        return [json.loads(line) for line in handle if line.strip()]


def check_selected_linear_endpoints(mappings):
    """Check the root-port scope of exactly the 66 selected BRANCH chains.

    The records' integer top/out fields are checked against the actual ordered
    rule: top is an incoming port, out is a ray-child port slot, and the outgoing
    carrier is the local to which that slot is bound.  Recompute each marked
    ternary relation, including its lift for every full incoming port state.
    """
    selected = [row for row in mappings if row["in_positive_complete_ray_set"]
                and row["branch"]["outcome"] == "linear"]
    sources = {
        "chains": json.loads((BRANCH / "chains.json").read_text())["rows"],
        "silent_ports": json.loads((BRANCH / "silent_ports.json").read_text()),
    }
    by_address = collections.defaultdict(list)
    for source_name, rows in sources.items():
        for record in rows:
            by_address[(record["file"], record["line"])].append((source_name, record))
    counts = collections.Counter()
    checked_rows, issues = [], []
    for row in selected:
        idx, defs, g = row["idx"], row["defs"], row["independent_port_mask"]
        address = (row["source"]["file"], row["source"]["line_one_based"])
        candidates = by_address[address]
        if len(candidates) != 1:
            issues.append({"idx": idx, "failure": "certificate_count", "count": len(candidates)})
            continue
        source_name, record = candidates[0]
        cycle = record["cycle"]
        counts[source_name + "_families"] += 1
        counts["all_eight_input_states_families"] += int(g == 255)
        if g != 255 or not cycle:
            issues.append({"idx": idx, "failure": "nonfree_input_or_empty_cycle"})
            continue
        ray = row["first_self_args"]
        calls = [args for callee, args in defs[0][2] if callee == "SELF"]
        envs = list(valid_envs(defs, g))
        step_rows = []
        noncarry_steps = []
        for step, witness in enumerate(cycle):
            top, out = witness["top"], witness["out"]
            port_scope_ok = (top in (0, 1, 2) and out in (0, 1, 2)
                             and out == cycle[(step + 1) % len(cycle)]["top"])
            if not port_scope_ok:
                issues.append({"idx": idx, "step": step, "failure": "port_scope_or_cycle_link"})
                continue
            if witness.get("kind") == "carry":
                identity_ok = ray[out] == top
                counts["identity_steps"] += 1
                if not identity_ok:
                    issues.append({"idx": idx, "step": step, "failure": "identity_step"})
                step_rows.append({"top": top, "out": out, "kind": "carry",
                                  "identity_verified": identity_ok})
                continue

            noncarry_steps.append(step)
            counts["bond_steps"] += 1
            carrier, helper, child = witness["carrier"], witness["var"], witness["child"]
            carrier_ok = carrier == ray[out] and 3 <= carrier < 3 + defs[0][1]
            helper_local_ok = 3 <= helper < 3 + defs[0][1]
            if not carrier_ok or not helper_local_ok:
                issues.append({"idx": idx, "step": step, "failure": "local_endpoint_or_helper"})
                continue
            if child is None:
                counts["own_helper_steps"] += 1
                helper_slots = [slot for slot, arg in enumerate(ray) if arg == helper]
                counts["own_helpers_also_bound_to_other_ray_ports"] += int(bool(helper_slots))

                def helper_values(env):
                    return {(env >> helper) & 1}
            else:
                counts["side_helper_steps"] += 1
                if not (0 < child < len(calls)):
                    issues.append({"idx": idx, "step": step, "failure": "side_child_index"})
                    continue
                helper_slots = []
                child_args = calls[child]
                child_choices = collections.defaultdict(set)
                for child_env in envs:
                    child_choices[child_env & 7].add((child_env >> helper) & 1)

                def helper_values(env):
                    return child_choices[project_assignment(env, child_args)]

            mask = 0
            sections = collections.defaultdict(set)
            for env in envs:
                incoming = env & 7
                top_value, carrier_value = (env >> top) & 1, (env >> carrier) & 1
                for helper_value in helper_values(env):
                    mask |= 1 << (top_value | (carrier_value << 1) | (helper_value << 2))
                    sections[incoming].add((carrier_value, helper_value))
            lift_mismatches = []
            for incoming in range(8):
                expected = {(bit, value) for bit in range(2) for value in range(2)
                            if witness["mask"] & (1 << (((incoming >> top) & 1)
                                                        | (bit << 1) | (value << 2)))}
                if sections[incoming] != expected:
                    lift_mismatches.append(incoming)
            counts["full_incoming_state_sections_checked"] += 8
            pair_free = all({sum(((state >> bit) & 1) << pos for pos, bit in enumerate(pair))
                             for state in range(8) if mask & (1 << state)} == set(range(4))
                            for pair in ((0, 1), (0, 2), (1, 2)))
            bond_ok = 0 < mask < 255 and pair_free
            if mask != witness["mask"] or lift_mismatches or not bond_ok:
                issues.append({"idx": idx, "step": step, "failure": "bond_or_universal_lift",
                               "computed_mask": mask, "recorded_mask": witness["mask"],
                               "failed_incoming_states": lift_mismatches, "minimal_bond": bond_ok})
            step_rows.append({"top": top, "out": out, "kind": "bond", "carrier": carrier,
                              "child": child, "helper_local": helper, "mask": mask,
                              "recorded_mask_verified": mask == witness["mask"],
                              "minimal_ternary_bond_verified": bond_ok,
                              "all_eight_full_incoming_lifts_verified": not lift_mismatches,
                              "helper_also_passed_to_ray_slots": helper_slots})
        if not noncarry_steps:
            issues.append({"idx": idx, "failure": "no_fresh_local_terminal_step"})
        counts["root_port_start_families"] += int(all(e["top"] in (0, 1, 2) for e in cycle))
        checked_rows.append({"idx": idx, "file": address[0], "line_one_based": address[1],
                             "certificate_source": source_name, "cycle_length": len(cycle),
                             "cycle_start_root_port": cycle[0]["top"],
                             "phases_with_fresh_own_local_terminal": noncarry_steps,
                             "steps": step_rows})
    return {
        "passed": not issues and len(checked_rows) == 66,
        "selected_linear_families": len(selected), "counts": dict(counts),
        "checked_family_indices": [row["idx"] for row in selected],
        "interpretation": "Every cycle begins at an incoming root port numbered 0..2, and each out slot is the next incoming port. Every cycle includes a bond step whose outgoing carrier is a fresh own local. Since any root port may be chosen, rotate the initial cycle phase so that its step at C_s ends at that fresh local of C_s. The recorded existence construction therefore has the required root-port endpoint; it is not restricted to starting at a root local.",
        "helper_identity_note": "Own helpers are fresh locals at their creating copy; four are also passed to unused ray-port slots. This is allowed: universal lifting was checked with all three incoming ports fixed, and each step's selected outgoing carrier follows the recorded cycle.",
        "evidence_limit": "Focused finite verification of the 66 recorded port-chain witnesses and their endpoint scope, not a re-audit of BRANCH's general chain theorem or lower-bound proof.",
        "issues": issues, "rows": checked_rows,
    }


def refresh_inventory():
    os.environ.update(OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    spec = importlib.util.spec_from_file_location("permitted_inventory_helper", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = [{"idx": idx, "defs": defs} for idx, defs in module.families_one_def()]
    (OUT / "family_inventory.json").write_text(json.dumps(rows, indent=1) + "\n")


def main():
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    started = time.monotonic()
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh-inventory", action="store_true")
    options = parser.parse_args()
    if options.refresh_inventory:
        refresh_inventory()

    inventory_path = OUT / "family_inventory.json"
    inventory = json.loads(inventory_path.read_text())
    ports_document = json.loads((BRANCH / "port_tables.json").read_text())
    outcome_document = json.loads((BRANCH / "outcomes.json").read_text())
    receipt = json.loads((BRANCH / "receipt.json").read_text())
    port_rows, outcome_rows = ports_document["rows"], outcome_document["rows"]
    rays, trues = load_jsonl(RAYS), load_jsonl(TRUE)
    mismatches = collections.defaultdict(list)

    source_files = sorted(SAMPLES.glob("sample_*.jsonl.gz"))
    samples = {}
    all_definitions_by_address = {}
    raw_candidates = []
    first_by_raw_key = {}
    archive_duplicates = []
    for path in source_files:
        counts = collections.Counter()
        with gzip.open(path, "rt") as handle:
            for line1, line in enumerate(handle, 1):
                record = json.loads(line)
                counts["physical_lines"] += 1
                counts["metadata_rows" if "kind" in record else "source_rows"] += 1
                if "defs" in record:
                    all_definitions_by_address[(path.name, line1)] = record
                if not (record.get("limit_only") and "defs" in record):
                    continue
                counts["limit_only_definition_rows"] += 1
                raw_key = canonical(record["defs"])
                address = [path.name, line1]
                if raw_key in first_by_raw_key:
                    archive_duplicates.append({"address": address,
                                               "first": first_by_raw_key[raw_key]["address"]})
                    continue
                item = {"idx": len(raw_candidates), "address": address,
                        "line0": line1 - 1, "record": record, "raw_key": raw_key}
                first_by_raw_key[raw_key] = item
                raw_candidates.append(item)
                counts["first_seen_unique_candidates"] += 1
        actual_hash = file_hash(path)
        samples[path.name] = {**counts, "sha256": actual_hash,
                              "matches_branch_source_hash": actual_hash == ports_document["source_files"].get(path.name)}
        if not samples[path.name]["matches_branch_source_hash"]:
            mismatches["source_hash"].append(path.name)

    independent_eligible = {}
    excluded = []
    relation_histogram = collections.Counter()
    for candidate in raw_candidates:
        raw_defs = candidate["record"]["defs"]
        if len(raw_defs) != 1:
            continue
        transformed = usual(raw_defs)
        relation, iterations = greatest_port_relation(transformed)
        if not relation:
            excluded.append({"idx": candidate["idx"], "source": candidate["address"],
                             "raw_key_sha256": key_hash(candidate["raw_key"]),
                             "usual_key_sha256": key_hash(canonical(transformed)),
                             "port_iteration_masks": iterations})
            continue
        key = canonical(transformed)
        if key in independent_eligible:
            mismatches["duplicate_surviving_usual_key"].append(candidate["idx"])
        independent_eligible[key] = {**candidate, "defs": transformed,
                                     "usual_key": key, "port_relation": relation,
                                     "port_iterations": iterations}
        relation_histogram[relation] += 1

    inventory_by_key = {canonical(row["defs"]): row for row in inventory}
    inventory_keys, eligible_keys = set(inventory_by_key), set(independent_eligible)
    for side, keys in (("inventory_only", inventory_keys - eligible_keys),
                       ("archive_only", eligible_keys - inventory_keys)):
        mismatches[side].extend(key_hash(key) for key in sorted(keys))

    branch_by_key = {}
    for row in outcome_rows:
        address = (row["file"], row["line"])
        archived = all_definitions_by_address.get(address)
        if archived is None:
            mismatches["branch_address_missing_definition"].append(address)
            continue
        key = canonical(usual(archived["defs"]))
        if key in branch_by_key:
            mismatches["duplicate_branch_rule_key"].append(key_hash(key))
        branch_by_key[key] = row
    for side, keys in (("branch_only_rule_key", set(branch_by_key) - eligible_keys),
                       ("eligible_missing_branch_rule_key", eligible_keys - set(branch_by_key))):
        mismatches[side].extend(key_hash(key) for key in sorted(keys))

    ports_by_address = {(row["file"], row["line"]): row for row in port_rows}
    rays_by_idx, trues_by_idx = {r["idx"]: r for r in rays}, {r["idx"]: r for r in trues}
    selected = {r["idx"] for r in rays if r.get("complete") and (r.get("lambda_float") or 0) > 0}
    identity_idx_set = {row["idx"] for row in inventory}
    identity_checks = {
        "inventory_duplicate_indices": duplicate_values(row["idx"] for row in inventory),
        "inventory_duplicate_rule_keys": duplicate_values(canonical(row["defs"]) for row in inventory),
        "outcome_duplicate_addresses": duplicate_values((r["file"], r["line"]) for r in outcome_rows),
        "port_duplicate_addresses": duplicate_values((r["file"], r["line"]) for r in port_rows),
        "ray_duplicate_indices": duplicate_values(r["idx"] for r in rays),
        "true_duplicate_indices": duplicate_values(r["idx"] for r in trues),
        "ray_indices_missing": sorted(identity_idx_set - set(rays_by_idx)),
        "ray_indices_extra": sorted(set(rays_by_idx) - identity_idx_set),
        "selected_missing_from_true": sorted(selected - set(trues_by_idx)),
        "true_indices_outside_selected": sorted(set(trues_by_idx) - selected),
        "port_address_only": sorted(set(ports_by_address) - {(r["file"], r["line"]) for r in outcome_rows}),
        "outcome_address_only": sorted({(r["file"], r["line"]) for r in outcome_rows} - set(ports_by_address)),
    }
    for name, values in identity_checks.items():
        mismatches[name].extend(values)

    mappings = []
    wrong_offsets = {0: {"matches": [], "wrong_rule": [], "no_definition": []},
                     1: {"matches": [], "wrong_rule": [], "no_definition": []},
                     2: {"matches": [], "wrong_rule": [], "no_definition": []}}
    for key, family in sorted(inventory_by_key.items(), key=lambda item: item[1]["idx"]):
        idx = family["idx"]
        if key not in independent_eligible or key not in branch_by_key:
            continue
        source = independent_eligible[key]
        branch = branch_by_key[key]
        address = (branch["file"], branch["line"])
        port = ports_by_address.get(address)
        defs = family["defs"]
        relation = source["port_relation"]
        transition = first_transition(defs, relation)
        expected_allowed = [state for state in range(8) if relation & (1 << state)]
        ray_args = list(next(args for callee, args in defs[0][2] if callee == "SELF"))
        cycles, carried = cycles_and_carried(ray_args)
        unfolded, identity_trace = actual_top_identities(ray_args)
        if carried != unfolded:
            mismatches["cycle_vs_identity_unfolding"].append(idx)
        if source["idx"] != idx:
            mismatches["family_index_provenance"].append({"helper_idx": idx, "archive_idx": source["idx"]})
        if list(address) != source["address"]:
            mismatches["branch_source_address"].append(idx)
        if port is None or sorted(tuple(pair) for pair in port["transition"]) != transition:
            mismatches["recomputed_transition"].append(idx)
        if port is None or port["allowed"] != expected_allowed:
            mismatches["recomputed_port_relation"].append(idx)
        if port is None or port["own"] != defs[0][1] or port["children"] != sum(c == "SELF" for c, _ in defs[0][2]):
            mismatches["port_rule_shape"].append(idx)
        if port is None or port["first_dead"] != source["record"]["first_dead"]:
            mismatches["first_dead_provenance"].append(idx)
        for offset, checks in wrong_offsets.items():
            test_address = (source["address"][0], source["line0"] + offset)
            test = all_definitions_by_address.get(test_address)
            category = "no_definition" if test is None else ("matches" if canonical(usual(test["defs"])) == key else "wrong_rule")
            checks[category].append(idx)
        ray, true = rays_by_idx.get(idx, {}), trues_by_idx.get(idx)
        if ray.get("lambda") is not None:
            if (Fraction(ray["lambda"]) > 0) != ((ray.get("lambda_float") or 0) > 0):
                mismatches["exact_vs_float_positive_ray"].append(idx)
        mappings.append({
            "idx": idx, "defs": defs, "rule_key_sha256": key_hash(key),
            "raw_rule_key_sha256": key_hash(source["raw_key"]),
            "usual_changes_rule": source["raw_key"] != key,
            "source": {"file": source["address"][0], "line_zero_based": source["line0"],
                       "line_one_based": source["address"][1], "candidate_index": source["idx"]},
            "branch": branch,
            "independent_port_mask": relation,
            "port_iteration_masks": source["port_iterations"],
            "independent_transition": transition,
            "first_self_args": ray_args, "port_cycles": cycles,
            "carried_ports": carried, "fixed_ports": [j for j in range(3) if ray_args[j] == j],
            "identity_unfolding_top_ports_depths_1_to_6": identity_trace,
            "ray_complete": ray.get("complete"), "lambda_ray": ray.get("lambda"),
            "lambda_ray_float": ray.get("lambda_float"), "in_positive_complete_ray_set": idx in selected,
            "true_rate_record": None if true is None else {name: true.get(name) for name in
                ("closed", "complete", "analysis_complete", "gate_ok", "upper_bound", "lambda_true", "lambda_true_float", "status")},
        })

    selected_rows = [row for row in mappings if row["in_positive_complete_ray_set"]]
    carried_selected = [row for row in selected_rows if row["carried_ports"]]
    bounded = [row for row in mappings if row["branch"]["outcome"] in {"exactly_three", "eventually_exactly_four"}]
    uncarried_bounded = [row for row in bounded if not row["carried_ports"]]
    selected_exact_three = [row for row in selected_rows if row["branch"]["outcome"] == "exactly_three"]
    other_carried = [row for row in carried_selected if row not in selected_exact_three]
    census = {
        "eligible": len(mappings),
        "branch_outcomes": dict(collections.Counter(row["branch"]["outcome"] for row in mappings)),
        "branch_bounded": len(bounded),
        "branch_bounded_carried": sum(bool(row["carried_ports"]) for row in bounded),
        "branch_bounded_uncarried": len(uncarried_bounded),
        "branch_bounded_uncarried_outcomes": dict(collections.Counter(row["branch"]["outcome"] for row in uncarried_bounded)),
        "branch_outcomes_by_carriage": {kind: dict(collections.Counter(row["branch"]["outcome"] for row in mappings
                                                             if bool(row["carried_ports"]) == flag))
                                       for kind, flag in (("carried", True), ("uncarried", False))},
        "positive_complete_rays": len(selected_rows),
        "positive_complete_carried": len(carried_selected),
        "positive_complete_branch_outcomes": dict(collections.Counter(row["branch"]["outcome"] for row in selected_rows)),
        "positive_complete_carried_indices": [row["idx"] for row in carried_selected],
        "positive_complete_exact_three_indices": [row["idx"] for row in selected_exact_three],
        "other_ten_carried_by_branch_outcome": {
            outcome: [row["idx"] for row in other_carried if row["branch"]["outcome"] == outcome]
            for outcome in sorted({row["branch"]["outcome"] for row in other_carried})},
        "other_ten_carried_new_true_rate_evidence": [{"idx": row["idx"], "branch_outcome": row["branch"]["outcome"],
                                                      **row["true_rate_record"]} for row in other_carried],
        "all_cycle_length_counts": dict(collections.Counter(len(cycle) for row in mappings for cycle in row["port_cycles"])),
        "selected_cycle_length_counts": dict(collections.Counter(len(cycle) for row in selected_rows for cycle in row["port_cycles"])),
        "selected_carried_cycles": [{"idx": row["idx"], "args": row["first_self_args"],
                                      "cycles": row["port_cycles"], "carried_ports": row["carried_ports"]} for row in carried_selected],
    }

    expected = {"eligible": 664, "branch_bounded": 432, "branch_bounded_carried": 320,
                "branch_bounded_uncarried": 112, "positive_complete_rays": 226,
                "positive_complete_carried": 20,
                "branch_bounded_uncarried_outcomes": {"exactly_three": 73, "eventually_exactly_four": 39},
                "positive_complete_branch_outcomes": {"linear": 66, "linear_lower_bound_only": 144,
                                                      "exactly_three": 10, "larger_sizes_unresolved": 6},
                "positive_complete_exact_three_indices": [262, 269, 302, 363, 579, 642, 662, 908, 975, 1144]}
    for name, value in expected.items():
        if census[name] != value:
            mismatches["expected_census"].append({"field": name, "observed": census[name], "expected": value})
    if census["branch_outcomes"] != outcome_document["totals"]:
        mismatches["outcome_totals"].append(census["branch_outcomes"])

    fixtures = []
    for label, args, expected_carried in (
        ("two_cycle_without_fixed_point", [1, 0, 3], [0, 1]),
        ("chain_ending_in_fresh_local", [1, 3, 0], []),
        ("tail_reaching_cycle_is_not_itself_carried", [1, 1, 3], [1]),
        ("three_cycle_without_fixed_point", [1, 2, 0], [0, 1, 2]),
    ):
        cycles, carried = cycles_and_carried(args)
        unfolded, _ = actual_top_identities(args)
        good = carried == expected_carried == unfolded
        fixtures.append({"name": label, "args": args, "cycles": cycles,
                         "carried": carried, "expected": expected_carried,
                         "identity_unfolding_agrees": unfolded == carried, "passed": good})
        if not good:
            mismatches["cycle_fixture"].append(label)
    for offset, checks in wrong_offsets.items():
        expected_matches = len(mappings) if offset == 1 else 0
        if len(checks["matches"]) != expected_matches:
            mismatches["line_offset_control"].append({"offset": offset, "matching": checks["matches"]})

    endpoint_check = check_selected_linear_endpoints(mappings)
    if not endpoint_check["passed"]:
        mismatches["selected_linear_root_port_endpoint"].append(endpoint_check["issues"])

    inputs = [inventory_path, HELPER, RAYS, TRUE, Path(__file__),
              ROOT / "research/TRUE-RATE-20261113-001/true_rate.md",
              ROOT / "research/TRUE-RATE-20261113-001/preregistration.md",
              ROOT / "research/TRUE-RATE-20261113-001/codex_spec.md",
              ROOT / "research/BRANCH-DEPTH-20261112-001/depth.md",
              BRANCH / "outcomes.json", BRANCH / "port_tables.json", BRANCH / "receipt.json",
              BRANCH / "chains.json", BRANCH / "silent_ports.json", *source_files]
    hashes = {str(path.relative_to(ROOT)): file_hash(path) for path in inputs}
    receipt_checks = {str(path.relative_to(ROOT)): receipt["bindings"].get(str(path.relative_to(ROOT))) == hashes[str(path.relative_to(ROOT))]
                      for path in (BRANCH / "outcomes.json", BRANCH / "port_tables.json",
                                   BRANCH / "chains.json", BRANCH / "silent_ports.json")}
    for path, good in receipt_checks.items():
        if not good:
            mismatches["branch_receipt_binding"].append(path)
    failures = {name: rows for name, rows in mismatches.items() if rows}
    report = {
        "audit": "Independent actual-rule identity mapping and carried-port recount; referee R1 points 2 and 3",
        "question": "Do the published first-ray census counts and per-family BRANCH identifications survive independent reconstruction?",
        "scope": "TRUE-RATE-20261113-001", "all_checks_pass": not failures,
        "authority": "Fresh finite truth-table checks for mapping and carriage; existing BRANCH and rate verdicts remain record inputs.",
        "definitions": {
            "rule_identity": "Compact JSON of every ordered (arity,locals,ordered calls with ordered args) definition; no isomorphism quotient. First SELF remains distinguished by order.",
            "family_index": "Zero-based index after first-seen exact-raw-definition dedup of limit_only=true definition rows, sample files in lexical order; counts include multi-definition families before one-definition filtering.",
            "usual_limit": "When a SELF call receives a permutation of all own ports, add their NAE constraint. Descend the monotone finite port-relation map from all 8 states to its greatest fixed point; require nonempty. None of the surviving 664 rules needs a usual transformation.",
            "source_line_offset": "An archive line at enumerate(...,start=0) value n is at BRANCH's enumerate(...,start=1) value n+1; family idx is a separate filtered ordinal. All 664 offset+1 addresses recover the identical complete ordered rule.",
            "carried": "A top port is a member of a directed cycle of j->a_j where a_j<3; reaching a cycle from a tail does not make the tail carried. Confirmed separately by unfolding fresh-local identities for six levels.",
            "selected_rays": "complete == true and lambda_float > 0, with positivity cross-checked against the exact fraction lambda.",
        },
        "provenance": {"samples": samples, "archive_raw_candidates": len(raw_candidates),
                       "archive_exact_duplicate_definitions": archive_duplicates,
                       "one_definition_candidates": len(excluded) + len(independent_eligible),
                       "empty_usual_limit_count": len(excluded), "eligible_usual_limit_masks": dict(relation_histogram),
                       "all_inventory_archive_usual_keys_equal": inventory_keys == eligible_keys,
                       "all_branch_archive_usual_keys_equal": set(branch_by_key) == eligible_keys,
                       "inventory_rule_keyset_sha256": key_hash(canonical(sorted(inventory_keys))),
                       "branch_rule_keyset_sha256": key_hash(canonical(sorted(branch_by_key))),
                       "branch_receipt_bindings_checked": receipt_checks},
        "census": census,
        "controls": {"cycle_fixtures": fixtures, "line_offsets_from_zero_based_source": {
            str(offset): {name: len(rows) for name, rows in checks.items()} for offset, checks in wrong_offsets.items()},
                     "wrong_offset_matching_indices": {str(offset): checks["matches"] for offset, checks in wrong_offsets.items() if offset != 1}},
        "identity_checks": identity_checks,
        "selected_linear_root_port_endpoint_check": endpoint_check,
        "mismatches": failures, "excluded_empty_usual_families": excluded,
        "mappings": mappings, "input_sha256": hashes,
        "evidence_limits": [
            "No independent re-proof of BRANCH outcomes or verification of the general TRUE-RATE summary graph and rate method is performed in this lane.",
            "Of the other ten carried selected families, BRANCH proves true linear growth in four and leaves six unresolved. The six have new TRUE-RATE closed/complete positive exact-rate records; this lane records those inputs without independently certifying their algorithm.",
            "Ordered definition equality is the appropriate family identity here; semantic equivalence between distinct rules is not claimed.",
            "No theorem, lifecycle, publication or unrelated working-tree records were changed.",
        ],
        "runtime": {"seconds": round(time.monotonic() - started, 6),
                    "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
                    "address_space_ceiling_bytes": 2 * 1024**3, "processes": 1,
                    "python": os.sys.executable, "codex_thread_id": os.environ.get("CODEX_THREAD_ID")},
    }
    (OUT / "mapping_audit.json").write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"all_checks_pass": report["all_checks_pass"], "census": census,
                      "controls": report["controls"], "mismatches": failures,
                      "selected_linear_endpoint_check": {key: endpoint_check[key] for key in
                          ("passed", "selected_linear_families", "counts", "issues")},
                      "runtime": report["runtime"]}, indent=1))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
