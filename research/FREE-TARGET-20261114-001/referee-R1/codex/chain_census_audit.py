"""Independent R1 chain/count/wording audit. Standard library, allowed data only.

Run with the workspace's .venv/bin/python -B. No producer Python is read or
imported. All computational assertions below can fail on changed input.
"""
from __future__ import annotations

import collections
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import resource

resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).with_name("chain_census_audit.json")
CENSUS = Path("artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz")
DRAWS = Path("experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex/draws.jsonl.gz")
SAMPLE = Path("experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/sample")
FREE = Path("experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex")
DOC = Path("research/FREE-TARGET-20261114-001")
INPUTS = [CENSUS, DRAWS, SAMPLE / "G.jsonl", SAMPLE / "phase2.jsonl",
          FREE / "population.json", FREE / "full/results.jsonl",
          FREE / "full/summary.json"] + [DOC / p for p in (
              "free_target.md", "preregistration.md", "codex_spec.md",
              "advisor_review_answer.md")]
COUNTER_KEY = '[[3,0,[["K",[0,1,2]]]],[3,1,[["SELF",[1,3,0]],["K",[3,1,0]]]],[3,1,[["K",[2,0,3]]]],[3,2,[[1,[2,4,1]]]]]'


def read_lines(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(ROOT / path, "rt") as handle:
        for line in handle:
            yield json.loads(line)


def read_json(path):
    return json.loads((ROOT / path).read_text())


def fractions(numerator, denominator):
    return {"numerator": numerator, "denominator": denominator,
            "share": numerator / denominator,
            "percent": 100 * numerator / denominator}


def wilson(successes, total):
    z = 1.959963984540054
    p = successes / total
    den = 1 + z * z / total
    mid = (p + z * z / (2 * total)) / den
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total**2)) / den
    return [mid - half, mid + half]


def flat_self_counters(definitions):
    """Expand only earlier numeric calls, retaining SELF's definition identity.

    A coefficient counts occurrences, not distinct callee names. Unused earlier
    definitions do not create copies. This is a fresh structural computation.
    """
    counters = []
    for index, (_, _, calls) in enumerate(definitions):
        counter = collections.Counter()
        for callee, _ in calls:
            if callee == "SELF":
                counter[index] += 1
            elif isinstance(callee, int):
                assert 0 <= callee < index
                counter.update(counters[callee])
            else:
                assert callee == "K"
        counters.append(counter)
    return counters


def packed(state, variables):
    return sum(((state >> variable) & 1) << index
               for index, variable in enumerate(variables))


def project(states, variables):
    return {packed(state, variables) for state in states}


def is_bond(states, variables):
    return (len(project(states, variables)) < 2 ** len(variables)
            and all(len(project(states, variables[:index] + variables[index + 1:]))
                    == 2 ** (len(variables) - 1)
                    for index in range(len(variables))))


def chain_counterexample(selected):
    """Exact five-variable proof calculation, independent of census DP.

    In COUNTER_KEY, call D1 from main on (root port 2, main own 4,
    root port 1). D1's own variable is fresh and its rules are
    NAE(own, port1, port0), SELF(port1, own, port0).
    Three consecutive D1 copies give NAE(a,b,c), NAE(b,c,d), NAE(c,d,e).
    Each prefix extends indefinitely: at every step a fresh bit can make the
    newest triple NAE. Thus these finite projections are globally exact.
    """
    source = selected[COUNTER_KEY]
    definitions = json.loads(COUNTER_KEY)
    assert definitions[1] == [3, 1, [["SELF", [1, 3, 0]], ["K", [3, 1, 0]]]]
    assert definitions[-1] == [3, 2, [[1, [2, 4, 1]]]]

    def nae(state, variables):
        return len({(state >> variable) & 1 for variable in variables}) == 2

    first_two = [state for state in range(16)
                 if nae(state, [0, 1, 2]) and nae(state, [1, 2, 3])]
    first_three = [state for state in range(32)
                   if nae(state, [0, 1, 2]) and nae(state, [1, 2, 3])
                   and nae(state, [2, 3, 4])]
    prefix_bonds = [list(variables)
                    for count in range(2, 5)
                    for variables in itertools.combinations(range(4), count)
                    if 0 in variables and 3 in variables and is_bond(first_two, variables)]
    variables = (0, 1, 3, 4)
    image = project(first_three, variables)
    drop_counts = [len(project(first_three, variables[:index] + variables[index + 1:]))
                   for index in range(4)]
    assert not prefix_bonds
    assert is_bond(first_three, variables)
    assert set(range(16)) - image == {3, 12}
    assert all(count == 8 for count in drop_counts)
    assert not is_bond(first_three, (0, 1, 2, 3))  # contains a smaller NAE bond
    assert not is_bond(list(range(32)), variables)  # completely unconstrained

    # Direct exact port relation of D1, starting at TOP. It stays TOP.
    local_allowed = [state for state in range(16)
                     if nae(state, [3, 1, 0])]
    exact_ports = project(local_allowed, (0, 1, 2))
    assert exact_ports == set(range(8))
    return {
        "key": COUNTER_KEY,
        "source_L_ray_first_six": source["L_ray"][:6],
        "source_n_defs": source["n_defs"],
        "source_lambda": source["lambda"],
        "source_in_5190": True,
        "source_in_literal_4035": False,
        "depth_convention": "entry S copy has depth 1; d belongs to depth 2, e to depth 3; agrees with source [3,10^9,4,...]",
        "labels": {"a": "root port 2", "b": "main own variable 4",
                   "c": "own variable of first S copy",
                   "d": "own variable of second S copy",
                   "e": "own variable of third S copy"},
        "irrelevant_variables": "root ports 0 and 1 and main own variable 3 never occur in an NAE constraint of this used expansion",
        "constraints": [["a", "b", "c"], ["b", "c", "d"], ["c", "d", "e"]],
        "exact_G_S_allowed_packed_states": sorted(exact_ports),
        "prefix_two_copies_allowed_state_count": len(first_two),
        "prefix_bonds_containing_a_d": prefix_bonds,
        "three_copies_allowed_state_count": len(first_three),
        "bond": ["a", "b", "d", "e"],
        "bond_allowed_packed_states": sorted(image),
        "bond_missing_packed_states": sorted(set(range(16)) - image),
        "bond_missing_assignments_in_abde_order": ["0011", "1100"],
        "one_forgotten_projection_sizes": drop_counts,
        "negative_controls": {"nonminimal_superset_rejected": True,
                              "full_relation_rejected": True},
        "conclusion": "For the intended broader counted class, L_any(2)<=4 while no prefix-only bond to depth 2 exists. Exact L_any=L_ray is refuted.",
    }


def main():
    classes = collections.Counter()
    census_keys = set()
    growers = {}
    chains = {}
    literal = set()
    by_n_defs = collections.Counter()
    declines = []
    absent_first_30 = []
    absent_after_20 = []
    source_flags = collections.Counter()
    for record in read_lines(CENSUS):
        assert record["key"] not in census_keys
        census_keys.add(record["key"])
        classes[record.get("class")] += 1
        if record.get("class") != "grows":
            continue
        definitions = json.loads(record["key"])
        counters = flat_self_counters(definitions)
        S = record["S"]
        raw_self = sum(callee == "SELF" for callee, _ in definitions[S][2])
        assert raw_self >= 1
        chain = counters[S] == {S: 1} and counters[-1] == {S: 1}
        record["audit_structure"] = {"raw_self_count_S": raw_self,
            "flat_S": dict(counters[S]), "flat_main": dict(counters[-1]),
            "intended_single_sequence": chain}
        growers[record["key"]] = record
        if len(definitions) == 1 and raw_self == 1:
            literal.add(record["key"])
        if not chain:
            continue
        chains[record["key"]] = record
        by_n_defs[record["n_defs"]] += 1
        source_flags[str((record.get("complete"), record.get("status"),
                          record.get("lambda_status"), record.get("eventually_bounded")))] += 1
        values = record["L_ray"]
        drops = [{"s": index + 1, "at_s": values[index], "at_s_plus_1": values[index + 1]}
                 for index in range(len(values) - 1) if values[index] > values[index + 1]]
        if drops:
            declines.append({"key": record["key"], "n_defs": record["n_defs"],
                             "L_ray": values, "drops": drops})
        if any(value >= 10**9 for value in values):
            absent_first_30.append(record["key"])
        if any(value >= 10**9 for value in values[20:]):
            absent_after_20.append(record["key"])

    draws = collections.Counter()
    distinct_draws = set()
    strata_keys = collections.defaultdict(set)
    for record in read_lines(DRAWS):
        key = record["key"]
        distinct_draws.add(key)
        draws["all_nested"] += 1
        if key not in growers:
            continue
        draws["first_ray_growth"] += 1
        g = growers[key]
        raw_self = g["audit_structure"]["raw_self_count_S"]
        finite_alive = record["fate"] == "forever"
        if key in literal:
            draws["literal_one_definition_one_SELF"] += 1
        if key in chains:
            draws["intended_single_sequence"] += 1
            strata_keys["intended_single_sequence"].add(key)
        elif raw_self == 1:
            draws["one_SELF_other_recursion_or_multiple_entries"] += 1
            strata_keys["one_SELF_other_recursion_or_multiple_entries"].add(key)
        if raw_self >= 2:
            draws["two_or_more_SELF"] += 1
            if g["n_defs"] == 1 and not finite_alive:
                draws["one_definition_limit_only_excluded"] += 1
                strata_keys["one_definition_limit_only_excluded"].add(key)
            else:
                draws["G_eligible_reconstructed"] += 1
                strata_keys["G_eligible_reconstructed"].add(key)
    assert distinct_draws == census_keys

    G = {record["key"]: record for record in read_lines(SAMPLE / "G.jsonl")}
    assert len(G) == 300
    replacements = 0
    for record in read_lines(SAMPLE / "phase2.jsonl"):
        if record["key"] in G:
            G[record["key"]] = record
            replacements += 1
    path_classes = collections.Counter(record["class_path"] for record in G.values())
    population = {key: record for key, record in G.items() if record["class_path"] == "grows"}
    assert len(population) == 66
    assert set(G) <= strata_keys["G_eligible_reconstructed"]
    frozen = read_json(FREE / "population.json")
    assert set(frozen["keys"]) == set(population)
    runner_rows = list(read_lines(FREE / "full/results.jsonl"))
    assert len(runner_rows) == 66
    assert all(record["status"] == "ok" for record in runner_rows)
    results = {record["result"]["key"]: record["result"] for record in runner_rows}
    assert set(results) == set(population)
    verdicts = collections.Counter(record["verdict"] for record in results.values())
    r_counts = collections.Counter(record["r"] for record in results.values() if record["verdict"] == "grows")
    bounded_budgets = collections.Counter()
    main_not_S = []
    for key, record in results.items():
        prep = record["preparation"]
        if prep["S"] != prep["n_defs"] - 1:
            main_not_S.append({"key": key, "verdict": record["verdict"],
                               "bounded_reason": record["bounded_search"]["reason"],
                               "attempt_count": len(record["bounded_search"]["attempts"])})
        for attempt in record["bounded_search"]["attempts"]:
            bounded_budgets[str((attempt["k"], attempt["status"]))] += 1
    unresolved_reasons = collections.Counter(record["reason"] for record in results.values()
                                            if record["verdict"] == "unresolved")
    summary = read_json(FREE / "full/summary.json")
    assert all(value["count"] == verdicts[key]
               for key, value in summary["verdicts"].items())
    assert set(verdicts) <= set(summary["verdicts"])
    assert len(chains) == 5190 and draws["intended_single_sequence"] == 5633
    assert len(literal) == 4035 and draws["literal_one_definition_one_SELF"] == 4478
    assert draws["one_definition_limit_only_excluded"] == 224
    assert draws["one_SELF_other_recursion_or_multiple_entries"] == 657
    assert draws["G_eligible_reconstructed"] == 6765
    assert draws["first_ray_growth"] == 13279
    assert draws["all_nested"] == 223261
    estimate = (5633 + 6765 * 43 / 300) / 223261
    output = {
        "scope": "FREE-TARGET-20261114-001, R1 points 4-5 only",
        "validation": "V2 independent same-task reimplementation of recount and finite countermodel; not external replication; inherited first-ray classifications are not re-proved",
        "resource_limit_bytes": 2 * 1024**3,
        "inputs_sha256": {str(path): hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                          for path in INPUTS},
        "census": {"family_rows": len(census_keys), "distinct_draw_keys": len(distinct_draws),
                   "classes": dict(classes), "draw_counts": dict(draws),
                   "strata_distinct_keys": {key: len(value) for key, value in strata_keys.items()}},
        "chain_filter": {
            "exact": "class == grows; expand numeric earlier-definition calls recursively, retain every SELF occurrence with its definition index; flat counter of S == {S:1} and flat counter of main == {S:1}",
            "families": len(chains), "sample_records": draws["intended_single_sequence"],
            "families_by_number_of_definitions": dict(by_n_defs),
            "literal_n_defs_one_families": len(literal),
            "literal_n_defs_one_sample_records": draws["literal_one_definition_one_SELF"],
            "not_literal_one_definition": len(chains) - len(literal),
            "nested_weight_fraction": fractions(5633, 223261),
            "first_ray_growth_weight_fraction": fractions(5633, 13279),
            "source_flags": dict(source_flags),
            "monotonicity_decline_count": len(declines),
            "finite_to_finite_decline_count": sum(any(drop["at_s"] < 10**9 for drop in row["drops"]) for row in declines),
            "decline_records": declines,
            "sentinel_first_30_count": len(absent_first_30),
            "sentinel_after_20_count": len(absent_after_20),
            "sentinel_after_20_keys": absent_after_20,
        },
        "counterexample": chain_counterexample(chains),
        "sample_and_wording": {
            "G_rows": len(G), "phase2_replacements": replacements,
            "G_path_classes": dict(path_classes), "population": len(population),
            "verdicts": dict(verdicts), "unresolved_reasons": dict(unresolved_reasons),
            "r_counts": dict(r_counts), "main_not_S_cases": main_not_S,
            "bounded_budget_status_counts": dict(bounded_budgets),
            "actual_bounded_search_families": sum(bool(record["bounded_search"]["attempts"]) for record in results.values()),
            "skipped_bounded_search_families": sum(not record["bounded_search"]["attempts"] for record in results.values()),
            "certified_fraction_of_66": fractions(43, 66),
            "certified_fraction_of_G300": fractions(43, 300),
            "wilson_43_66": wilson(43, 66), "wilson_43_300": wilson(43, 300),
            "about_3_percent_arithmetic": {
                "formula": "(5633 + 6765 * 43/300) / 223261",
                "point_share": estimate, "point_percent": 100 * estimate,
                "status": "exploratory extrapolation, not established census prevalence; sample inclusion law not recoverable from allowed rows; preregistration explicitly disallows extrapolation while unresolved remain",
            },
        },
        "algebraic_claims_argued_in_prose": {
            "whole_infinite_ray_support": "Unique-sequence identity would equate candidate supports if L_ray meant the whole infinite sequence.",
            "prefix_support_countertransfer": "For a finite bond B to depth s, let d>=s be its greatest member origin depth. Then B qualifies prefix-only L_ray(d), hence inf_{d>=s}L_ray(d)<=L_any(s)<=L_ray(s). This is a lower-bound transfer, not exact equality or existence at every s.",
            "positive_slope": "If the inherited finite-graph theorem supplies L_ray(d)>=lambda*d-C at all finite values, then every finite L_any(s)>=lambda*s-C. If L_ray(s) is finite eventually and lambda*s+O(1), both give L_any(s)=lambda*s+O(1). Sentinel holes prevent obtaining existence at each large s from this upper bound alone.",
        },
    }
    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(OUT.relative_to(ROOT)),
        "chains": len(chains), "chain_sample_records": 5633,
        "literal_chains": len(literal), "nested_denominator": 223261,
        "growth_denominator": 13279, "G_eligible": 6765,
        "L_any_equals_prefix_L_ray_refuted_for_counted_class": True,
        "sample_verdicts": dict(verdicts)}, sort_keys=True))


if __name__ == "__main__":
    main()
