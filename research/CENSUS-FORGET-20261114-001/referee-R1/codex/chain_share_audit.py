"""R1 points 3--4: independent chain and weighted-share recount.

Question: do the stated chain strata and recorded forgetting verdicts produce
the published numerical totals? Branch: deterministic code analysis, referee
recomputation. Inputs: allowed raw data and study prose only; no producer Python
under FREE-TARGET or CENSUS-FORGET is opened or imported. Outputs: this lane's
JSON and Markdown. The strongest controls are complete raw-key reconciliation,
occurrence-sensitive structural controls, a five-variable equality
counterexample, and direct comparisons to reading.json. One process, 2 GiB,
no network. Stop after this complete recount. First-ray growth and the validity
of the supplied semigroup certificates remain inherited evidence.

Run from any directory with the workspace .venv/bin/python -B.
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
import sys

resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
CENSUS = Path("artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz")
DRAWS = Path("experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex/draws.jsonl.gz")
FULL = Path("experiments/CENSUS-FORGET-20261114-001A/CENSUS-FORGET-20261114-001A-E001_forget_census/full")
READING = FULL.parent / "reading.json"
SAMPLE = Path("experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/sample")
DOCUMENTS = [Path("research/CENSUS-FORGET-20261114-001") / name for name in
             ("census_forget.md", "preregistration.md", "advisor_review_answer.md")]
PREVIOUS = Path("research/FREE-TARGET-20261114-001/referee-R1/codex")
TARGET_INVENTORY = Path("research/CENSUS-FORGET-20261114-001/referee-R1/codex/target_inventory.json")
INPUTS = [CENSUS, DRAWS, FULL / "job.json", FULL / "results.jsonl", READING,
          SAMPLE / "G.jsonl", SAMPLE / "phase2.jsonl",
          PREVIOUS / "codex_report.md", PREVIOUS / "chain_wording_audit.md",
          TARGET_INVENTORY] + DOCUMENTS
ABSENT = 10**9
VERDICTS = ("certified", "non-forgetting", "capped")
COUNTER_KEY = '[[3,0,[["K",[0,1,2]]]],[3,1,[["SELF",[1,3,0]],["K",[3,1,0]]]],[3,1,[["K",[2,0,3]]]],[3,2,[[1,[2,4,1]]]]]'


def rows(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(ROOT / path, "rt") as handle:
        for line in handle:
            yield json.loads(line)


def read_json(path):
    return json.loads((ROOT / path).read_text())


def sha256(path):
    digest = hashlib.sha256()
    with open(ROOT / path, "rb") as handle:
        for data in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(data)
    return digest.hexdigest()


def wilson(successes, total):
    """Nominal two-sided 95% Wilson score interval; z=Phi^-1(0.975)."""
    assert 0 <= successes <= total and total > 0
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total**2)) / denominator
    return [max(0.0, center - half), min(1.0, center + half)]


def rate(successes, total):
    return {"numerator": successes, "denominator": total,
            "share": successes / total, "percent": 100 * successes / total,
            "wilson95": wilson(successes, total)}


def self_occurrences(definitions):
    """Inline earlier numeric calls, retaining each SELF's definition identity.

    Counters count occurrences rather than unique callee names. Recursive SELF
    is retained, not recursively expanded. Unused definitions have no effect.
    """
    output = []
    for index, (_, _, calls) in enumerate(definitions):
        counter = collections.Counter()
        for callee, _ in calls:
            if callee == "SELF":
                counter[index] += 1
            elif isinstance(callee, int):
                assert 0 <= callee < index
                counter.update(output[callee])
            else:
                assert callee == "K"
        output.append(counter)
    return output


def controls():
    # Repeated finite calls really duplicate recursive entries.
    ds = [[3, 0, [["SELF", [0, 1, 2]]]],
          [3, 0, [[0, [0, 1, 2]], [0, [0, 1, 2]]]]]
    assert self_occurrences(ds) == [{0: 1}, {0: 2}]
    # An unused earlier recursive definition does not make main branch.
    ds = [[3, 0, [["SELF", [0, 1, 2]]]],
          [3, 1, [["K", [0, 1, 3]], ["SELF", [0, 1, 3]]]]]
    assert self_occurrences(ds)[-1] == {1: 1}
    assert abs(wilson(0, 10)[1] - 0.2775327998628892) < 1e-14
    assert abs(wilson(10, 10)[0] - (1 - wilson(0, 10)[1])) < 1e-14
    return {"occurrence_multiplicity": True, "unused_definition": True,
            "wilson_zero_all_symmetry": True}


def counterexample(source):
    def nae(state, indices):
        return len({(state >> index) & 1 for index in indices}) == 2

    def projection(states, indices):
        return {sum(((state >> variable) & 1) << i
                    for i, variable in enumerate(indices)) for state in states}

    def bond(states, indices):
        return bool(states) and len(projection(states, indices)) < 2**len(indices) and all(
            len(projection(states, indices[:i] + indices[i + 1:])) == 2**(len(indices) - 1)
            for i in range(len(indices)))

    states2 = [state for state in range(16)
               if nae(state, [0, 1, 2]) and nae(state, [1, 2, 3])]
    states3 = [state for state in range(32)
               if nae(state, [0, 1, 2]) and nae(state, [1, 2, 3]) and nae(state, [2, 3, 4])]
    prefix = [list(indices) for size in range(2, 5)
              for indices in itertools.combinations(range(4), size)
              if 0 in indices and 3 in indices and bond(states2, indices)]
    chosen = (0, 1, 3, 4)
    image = projection(states3, chosen)
    drops = [len(projection(states3, chosen[:i] + chosen[i + 1:])) for i in range(4)]
    assert not prefix
    assert bond(states3, chosen) and drops == [8, 8, 8, 8]
    assert set(range(16)) - image == {3, 12}
    assert not bond(states3, (0, 1, 2, 3))
    assert not bond(list(range(32)), chosen)
    assert source["L_ray"][1] == ABSENT and source["chain"]
    return {"key": COUNTER_KEY, "source_lambda": source["lambda"],
            "source_L_ray": source["L_ray"], "source_n_defs": source["n_defs"],
            "constraints": [["a", "b", "c"], ["b", "c", "d"], ["c", "d", "e"]],
            "origins": {"a": "participating root port", "b": "main own distinction",
                        "c": "depth 1 own distinction", "d": "depth 2 own distinction",
                        "e": "depth 3 own distinction"},
            "prefix_allowed_state_count": len(states2),
            "prefix_bonds_containing_a_d": prefix,
            "extended_allowed_state_count": len(states3),
            "bond": ["a", "b", "d", "e"],
            "bond_missing_assignments_in_abde_order": ["0011", "1100"],
            "bond_allowed_packed_states": sorted(image),
            "one_forgotten_projection_sizes": drops,
            "negative_controls": {"nonminimal_superset_rejected": True,
                                  "full_relation_rejected": True},
            "infinite_extension": "Each next fresh bit can satisfy the next NAE triple; all finite allowed prefixes extend. The exact port limit is TOP.",
            "verdict": "L_any(2)<=4 but prefix L_ray(2) absent; equality false in counted chain class."}


def main():
    control_results = controls()
    all_keys = set()
    growers = {}
    classes = collections.Counter()
    stratum_keys = collections.defaultdict(set)
    n_defs_chains = collections.Counter()
    structural_splits = collections.Counter()
    for row in rows(CENSUS):
        key = row["key"]
        assert key not in all_keys
        all_keys.add(key)
        classes[row["class"]] += 1
        if row["class"] != "grows":
            continue
        ds = json.loads(key)
        counters = self_occurrences(ds)
        S = row["S"]
        c = sum(callee == "SELF" for callee, _ in ds[S][2])
        assert c >= 1 and len(ds) == row["n_defs"]
        chain = counters[S] == {S: 1} and counters[-1] == {S: 1}
        literal = len(ds) == 1 and c == 1
        other_S = any(index != S for index in counters[S])
        other_main = any(index != S for index in counters[-1])
        stratum = "chain" if chain else "c>=2" if c >= 2 else "c=1 other"
        kept = {name: row.get(name) for name in
                ("S", "n_defs", "L_ray", "lambda", "lambda_status", "complete",
                 "status", "eventually_bounded", "missing_residues", "period")}
        kept.update({"c": c, "chain": chain, "literal": literal,
                     "other_S": other_S, "other_main": other_main,
                     "S_occurrences_in_main": counters[-1][S], "stratum": stratum})
        growers[key] = kept
        stratum_keys[stratum].add(key)
        stratum_keys["all"].add(key)
        if literal:
            stratum_keys["literal one definition"].add(key)
        if not chain:
            stratum_keys["nonchain"].add(key)
        if chain:
            n_defs_chains[len(ds)] += 1
        elif c == 1:
            structural_splits[str((other_S, other_main, counters[-1][S]))] += 1

    weights = collections.Counter()
    draw_fates = collections.defaultdict(collections.Counter)
    draw_alive = collections.defaultdict(collections.Counter)
    for row in rows(DRAWS):
        key = row["key"]
        weights[key] += 1
        if key in growers:
            draw_fates[key][row["fate"]] += 1
            draw_alive[key][row["limit_alive"]] += 1
    assert set(weights) == all_keys
    growth_weights = sum(weights[key] for key in growers)
    all_weights = sum(weights.values())
    limit_only = set()
    for key, row in growers.items():
        if row["n_defs"] == 1 and row["c"] >= 2:
            fates = draw_fates[key]
            if any(fate != "forever" for fate in fates):
                assert "forever" not in fates
                assert set(draw_alive[key]) == {True}
                limit_only.add(key)
    stratum_keys["one-definition limit-only"] = limit_only

    results = {}
    runner_status = collections.Counter()
    result_field_mismatches = []
    caps = collections.Counter()
    nonforget_witness_flags = collections.Counter()
    empty = []
    audit_counts = collections.Counter()
    for record in rows(FULL / "results.jsonl"):
        runner_status[record["status"]] += 1
        assert record["status"] == "ok" and record["error"] is None
        key = record["case"]
        assert key in growers and key not in results
        result = record["result"]
        source = growers[key]
        for name, expected in (("chain", source["chain"]), ("c", source["c"]),
                               ("n_defs", source["n_defs"]),
                               ("other_holding_calls", source["other_S"] or source["other_main"])):
            if result[name] != expected:
                result_field_mismatches.append({"key": key, "field": name,
                                                "expected": expected, "actual": result[name]})
        verdict = result["verdict"]
        assert verdict in VERDICTS
        if verdict == "certified":
            assert isinstance(result["r"], int) and result["r"] >= 1
            audit_counts["certified_with_audit_field"] += "audit_mismatches" in result
            audit_counts["certified_nonempty_mismatch_list"] += bool(result.get("audit_mismatches"))
        elif verdict == "capped":
            caps[result["cap"]] += 1
        else:
            witness = result["recurring_word"]
            nonforget_witness_flags[str((bool(witness["cycle"]), witness["all_nonempty_prefixes_nonrectangular"]))] += 1
        if result["empty_relation"]:
            empty.append(key)
        results[key] = {"verdict": verdict, "r": result.get("r"),
                        "other_holding_calls": result["other_holding_calls"]}
    assert set(results) == set(growers)
    assert not result_field_mismatches

    tables = {}
    r_tables = {}
    for name, keys in sorted(stratum_keys.items()):
        family_counts = collections.Counter(results[key]["verdict"] for key in keys)
        draw_counts = collections.Counter()
        r_family = collections.Counter()
        r_draw = collections.Counter()
        for key in keys:
            result = results[key]
            draw_counts[result["verdict"]] += weights[key]
            if result["verdict"] == "certified":
                r_family[result["r"]] += 1
                r_draw[result["r"]] += weights[key]
        families = len(keys)
        draws = sum(weights[key] for key in keys)
        tables[name] = {"families": families, "draws": draws,
                        "by_count": {v: rate(family_counts[v], families) for v in VERDICTS},
                        "by_weight": {v: rate(draw_counts[v], draws) for v in VERDICTS}}
        r_tables[name] = {"families": dict(sorted(r_family.items())),
                          "draws": dict(sorted(r_draw.items()))}

    G = {row["key"]: row for row in rows(SAMPLE / "G.jsonl")}
    assert len(G) == 300 and set(G) <= stratum_keys["c>=2"]
    replacement_count = 0
    for row in rows(SAMPLE / "phase2.jsonl"):
        if row["key"] in G:
            G[row["key"]] = row
            replacement_count += 1
    outside = stratum_keys["c>=2"] - set(G)
    outside_success = {key for key in outside if results[key]["verdict"] == "certified"}
    outside_weight = sum(weights[key] for key in outside)
    outside_cert_weight = sum(weights[key] for key in outside_success)
    sample_by_path = {}
    for path_class in sorted({row["class_path"] for row in G.values()}):
        keys = {key for key, row in G.items() if row["class_path"] == path_class}
        sample_by_path[path_class] = {
            "families": len(keys), "draws": sum(weights[key] for key in keys),
            "verdicts_by_count": dict(collections.Counter(results[key]["verdict"] for key in keys)),
            "verdicts_by_weight": dict(sum((collections.Counter({results[key]["verdict"]: weights[key]}) for key in keys), collections.Counter()))}
    outside_summary = {"excluded_families": len(G),
                       "excluded_draws": sum(weights[key] for key in G),
                       "excluded_certified_families": sum(results[key]["verdict"] == "certified" for key in G),
                       "excluded_certified_draws": sum(weights[key] for key in G if results[key]["verdict"] == "certified"),
                       "families": len(outside), "draws": outside_weight,
                       "certified_by_count": rate(len(outside_success), len(outside)),
                       "certified_by_weight": rate(outside_cert_weight, outside_weight),
                       "phase2_replacements": replacement_count,
                       "sample_by_path_class": sample_by_path,
                       "prediction_band": [0.08, 0.25],
                       "P1_holds": 0.08 <= outside_cert_weight / outside_weight <= 0.25}

    chains = stratum_keys["chain"]
    union = chains | {key for key in growers if not growers[key]["chain"] and results[key]["verdict"] == "certified"}
    union_weight = sum(weights[key] for key in union)
    headline = {
        "chains_plus_certified_nonchains_first_ray_growth_by_count": rate(len(union), len(growers)),
        "chains_plus_certified_nonchains_first_ray_growth_by_weight": rate(union_weight, growth_weights),
        "certified_nonchains_by_weight": tables["nonchain"]["by_weight"]["certified"],
        "certified_two_or_more_SELF_by_weight": tables["c>=2"]["by_weight"]["certified"],
        "certified_one_SELF_nonchains_by_weight": tables["c=1 other"]["by_weight"]["certified"],
        "chains_plus_certified_nonchains_all_nested_by_weight": rate(union_weight, all_weights),
        "chain_share_of_combined_weight": rate(tables["chain"]["draws"], union_weight),
        "original_label_aggregation_complement_weight": rate(growth_weights - union_weight, growth_weights)}
    # The lead owns this structural audit. Here its totals are only reconciled
    # to our raw strata before computing the requested conservative fractions.
    inventory = read_json(TARGET_INVENTORY)
    inventory_scope = inventory["all_certificate_scope"]
    for name in ("chain", "c>=2", "c=1 other"):
        assert inventory_scope[name]["families"] == tables[name]["by_count"]["certified"]["numerator"]
    safe_c2 = inventory_scope["c>=2"]["no_other_own"] - inventory_scope["c>=2"]["no_other_own_but_delayed_S"]
    safe_c1 = inventory_scope["c=1 other"]["no_other_own"] - inventory_scope["c=1 other"]["no_other_own_but_delayed_S"]
    other_own = sum(inventory_scope[name]["other_own"] for name in ("c>=2", "c=1 other"))
    delay_extra = sum(inventory_scope[name]["no_other_own_but_delayed_S"] for name in ("c>=2", "c=1 other"))
    safe_count = tables["chain"]["draws"] + safe_c2 + safe_c1
    assert (safe_c2, safe_c1, other_own, delay_extra, safe_count) == (1046, 384, 186, 2, 7063)
    assert len(inventory["all_certified_with_delayed_S"]) == 8
    assert sum(not row["has_other_own"] for row in inventory["all_certified_with_delayed_S"]) == 2
    corrected_bound = {
        "inventory_source": str(TARGET_INVENTORY),
        "inventory_authority": "Lead referee's separately computed target-type inventory; subgroup membership not independently rederived in this numeric lane.",
        "chain_draws": tables["chain"]["draws"],
        "certified_c_ge_2_draws_passing_both_scope_conditions": safe_c2,
        "certified_c1_nonchain_draws_passing_both_scope_conditions": safe_c1,
        "excluded_for_other_reachable_type_own_distinctions": other_own,
        "excluded_additionally_for_zero_own_recursive_type_delaying_S": delay_extra,
        "excluded_certified_nonchain_draws_requiring_further_argument": other_own + delay_extra,
        "conditional_conservative_lower_tally": safe_count,
        "status": "conditional on corrected chain and S-only-ancestry gap arguments",
        "structural_scope_condition": "Every deep own target has S-only recursive ancestry after main's finite expansion; other reachable recursive types neither introduce own distinctions nor delay later S targets.",
        "first_ray_growth_weight": rate(safe_count, growth_weights),
        "all_nested_weight": rate(safe_count, all_weights),
        "outside_tally_first_ray_growth_draws": growth_weights - safe_count,
        "meaning": "Conditional conservative lower tally, not exact all-copy-growth incidence. The lead found bounded counterexamples among exclusions for other own types and zero-own recursive types delaying S."}
    assert 7251 - safe_count == other_own + delay_extra

    holes = []
    declines = []
    for key in sorted(chains):
        row = growers[key]
        values = row["L_ray"]
        missing = [index + 1 for index, value in enumerate(values) if value >= ABSENT]
        if missing:
            holes.append({"key": key, "n_defs": row["n_defs"], "literal": row["literal"],
                          "draws": weights[key], "missing_depths": missing,
                          "missing_residues": row["missing_residues"], "period": row["period"],
                          "L_ray": values})
        drops = [{"s": index + 1, "from": values[index], "to": values[index + 1]}
                 for index in range(len(values) - 1) if values[index] > values[index + 1]]
        if drops:
            declines.append({"key": key, "literal": row["literal"], "draws": weights[key], "drops": drops})
    hole_summary = {
        "observed_depth_lengths": dict(collections.Counter(len(growers[key]["L_ray"]) for key in chains)),
        "families_with_absence": len(holes), "draws_with_absence": sum(row["draws"] for row in holes),
        "families_with_absence_after_depth20": sum(any(s > 20 for s in row["missing_depths"]) for row in holes),
        "draws_with_absence_after_depth20": sum(row["draws"] for row in holes if any(s > 20 for s in row["missing_depths"])),
        "literal_families_with_absence": sum(row["literal"] for row in holes),
        "literal_draws_with_absence": sum(row["draws"] for row in holes if row["literal"]),
        "declining_families": len(declines),
        "finite_to_finite_declining_families": sum(any(drop["from"] < ABSENT for drop in row["drops"]) for row in declines),
        "absence_records": holes, "decline_records": declines}

    reading = read_json(READING)
    comparisons = {}
    for name in ("chain", "c>=2", "c=1 other", "all"):
        actual = tables[name]
        expected = reading["strata"][name]
        assert (actual["families"], actual["draws"]) == (expected["families"], expected["draws"])
        for measure, count_field in (("by_count", "n"), ("by_weight", "draws")):
            for verdict in VERDICTS:
                computed = actual[measure][verdict]
                reported = expected[measure].get(verdict)
                if reported is None:
                    assert computed["numerator"] == 0
                    continue
                assert computed["numerator"] == reported[count_field]
                assert abs(computed["share"] - reported["share"]) <= 0.000051
                assert all(abs(a - b) <= 0.000051 for a, b in zip(computed["wilson95"], reported["wilson"]))
        comparisons[name] = "all counts, shares and intervals match stated precision"
    assert {str(k): v for k, v in r_tables["all"]["families"].items()} == reading["r_distribution"]
    assert {str(k): v for k, v in r_tables["nonchain"]["families"].items()} == reading["r_distribution_nonchain"]
    assert tables["one-definition limit-only"]["by_count"]["certified"]["numerator"] == 0
    assert {v: tables["one-definition limit-only"]["by_count"][v]["numerator"] for v in ("non-forgetting", "capped")} == reading["the_224"]
    assert (outside_summary["families"], outside_weight, len(outside_success), outside_cert_weight) == (
        reading["P1"]["families"], reading["P1"]["draws"], reading["P1"]["certified_families"], reading["P1"]["certified_draws"])
    assert abs(outside_summary["certified_by_weight"]["share"] - reading["P1"]["share"]) <= 0.000051
    assert all(abs(a - b) <= 0.000051 for a, b in zip(outside_summary["certified_by_weight"]["wilson95"], reading["P1"]["wilson"]))
    assert len(chains) == 5190 and tables["chain"]["draws"] == 5633
    assert tables["literal one definition"]["families"] == 4035 and tables["literal one definition"]["draws"] == 4478
    assert union_weight == 7251 and growth_weights == 13279 and all_weights == 223261
    assert headline["certified_nonchains_by_weight"]["numerator"] == 1618

    output = {
        "scope": "CENSUS-FORGET-20261114-001 R1, referee points 3--4",
        "evidence": "V2 fresh same-task deterministic recount; supplied growth classes and semigroup verdict validity inherited",
        "interpreter": sys.executable, "address_space_limit_bytes": 2 * 1024**3,
        "inputs_sha256": {str(path): sha256(path) for path in INPUTS},
        "audit_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "controls": control_results,
        "raw_data": {"families": len(all_keys), "draws": all_weights,
                     "family_classes": dict(classes), "first_ray_growth_families": len(growers),
                     "first_ray_growth_draws": growth_weights, "runner_status": dict(runner_status)},
        "strata": tables, "headline": headline,
        "supplemental_corrected_bound": corrected_bound,
        "chain_structure": {
            "filter": "After expanding numeric earlier-definition calls, both S and main have exactly SELF-occurrence counter {S:1}.",
            "families_by_n_defs": dict(sorted(n_defs_chains.items())),
            "multiple_definition_families": len(chains) - tables["literal one definition"]["families"],
            "multiple_definition_draws": tables["chain"]["draws"] - tables["literal one definition"]["draws"],
            "c1_nonchain_structural_split_key": "(has_other_SELF_identity_in_S, has_other_SELF_identity_in_main, number_S_occurrences_in_main)",
            "c1_nonchain_structural_splits": dict(sorted(structural_splits.items())),
            "c1_nonchain_recorded_other_holding_calls": dict(collections.Counter(str(results[key]["other_holding_calls"]) for key in stratum_keys["c=1 other"])),
            "result_structural_field_mismatches": result_field_mismatches,
            "missing_depths": hole_summary},
        "r_distributions": r_tables,
        "outside_EVERY_RAY_sample": outside_summary,
        "recorded_certificate_metadata": {"empty_relation_keys": empty, "caps": dict(caps),
                                          "nonforgetting_recurring_word_flags": dict(nonforget_witness_flags),
                                          "producer_audit_fields": dict(audit_counts)},
        "reading_json_comparison": comparisons,
        "equality_counterexample": counterexample(growers[COUNTER_KEY]),
        "corrected_chain_bound": "inf_{d>=s} L_ray(d) <= L_any(s) <= L_ray(s), with absent minima interpreted as infinity; use greatest member introduction depth d of each finite bond.",
        "qualifications": [
            "Chains are broader than literal one-definition descriptions; numeric helper calls must first be expanded and both S and main checked.",
            "Prefix L_ray need not equal members-anywhere L_any; a finite bond may use members below its target.",
            "An inherited positive uniform linear lower bound transfers on this class. At-depth existence is separate; missing ray minima must not be silently treated as finite.",
            "7251 is chains plus nonchains bearing the producer's forgetting-certified label, not the 6144 weighted forgetting certificates alone. Its all-copy-growth interpretation fails the lead's separate target-type check.",
            "No certificate for 224 is not a proof that all 224 never forget: 203 have recorded non-forgetting certificates and 21 are capped.",
            "Non-forgetting proves persistence of a port correlation, not boundedness of members-anywhere bonds; capped cases decide neither.",
            "Shares are exact for recorded draws and distinct description keys. Nominal Wilson intervals are binomial calculations, not theorem bounds or a verified inclusion model.",
            "This lane independently recounts verdict labels and does not validate their mathematical soundness or re-prove inherited first-ray classifications."]}
    (HERE / "chain_share_audit.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    (HERE / "chain_share_audit.md").write_text(report(output))
    print(json.dumps({"output": str((HERE / "chain_share_audit.json").relative_to(ROOT)),
                      "all_checks_passed": True, "headline_weight": [union_weight, growth_weights],
                      "literal_chain_families_draws": [4035, 4478],
                      "nonchain_family_draw_totals": [tables["nonchain"]["families"], tables["nonchain"]["draws"]],
                      "outside_sample_weight": [outside_cert_weight, outside_weight],
                      "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}, sort_keys=True))


def report(data):
    out = ["# R1: chain definition and census shares", "",
           "**Verdict: the arithmetic reproduces; the broad growth interpretation does not follow from it.** The stated 7,251/13,279 and 7,251/223,261 totals reproduce from recorded verdict labels and the broader 5,190-family chain filter. They are not thereby proved counts of all-copy growth: the lead's separate target-type check has counterexamples. The literal one-definition filter gives 4,035 families / 4,478 draws. Prefix-restricted `L_ray = L_any` is false for the counted class; the weaker lower-bound transfer survives. No new proof of the supplied first-ray or forgetting verdicts is claimed.", "",
           "This is an offline, independently authored, same-task referee recount (V2), using only permitted data and prior referee material. Producer Python under FREE-TARGET and CENSUS-FORGET was neither opened nor imported. All writes are confined to the three assigned chain-share files. No Git mutations, publication, network calls, or subagents were used.", "",
           "## Recorded strata", "",
           "A family here is a distinct description key; draws retain multiplicity from the raw REACH census. The raw keys reconcile exactly: 124,572 family rows, 223,261 nested draws, and 12,772 first-ray-growing families / 13,279 draws. Every current result is present exactly once and has runner status `ok`.", "",
           "| Stratum | Families | Draws | Forgetting certified, families / draws | Non-forgetting, families / draws | Capped, families / draws |",
           "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for name in ("chain", "c>=2", "c=1 other", "nonchain", "all", "one-definition limit-only"):
        row = data["strata"][name]
        cells = [f'{row["by_count"][v]["numerator"]:,} / {row["by_weight"][v]["numerator"]:,}' for v in VERDICTS]
        out.append(f'| {name} | {row["families"]:,} | {row["draws"]:,} | ' + " | ".join(cells) + " |")
    out += ["", "## Headline arithmetic and nominal Wilson intervals", "",
            "| Recorded weighted quantity | Exact fraction | Percent | Nominal 95% Wilson interval |",
            "| --- | ---: | ---: | ---: |"]
    for name, label in (
        ("chains_plus_certified_nonchains_first_ray_growth_by_weight", "Chains + certified nonchains / first-ray growers"),
        ("certified_nonchains_by_weight", "Certified nonchains / nonchains"),
        ("certified_two_or_more_SELF_by_weight", "Certified c>=2 / c>=2"),
        ("certified_one_SELF_nonchains_by_weight", "Certified c=1 nonchains / c=1 nonchains"),
        ("chains_plus_certified_nonchains_all_nested_by_weight", "Chains + certified nonchains / all nested draws")):
        row = data["headline"][name]
        lo, hi = row["wilson95"]
        out.append(f'| {label} | {row["numerator"]:,} / {row["denominator"]:,} | {row["percent"]:.6f}% | {100*lo:.6f}%–{100*hi:.6f}% |')
    out += ["", "These are exact observed fractions. The intervals are the requested binomial Wilson calculations with z = 1.959963984540054; the audit does not reconstruct or validate the description-weight sampling model. Distinct-key Wilson calculations in the JSON address a different weighting. `reading.json` agrees at its stated four-decimal precision in every tested stratum, share and interval.", "",
            "The 7,251 combined draws consist of 5,633 chain draws and 1,618 certified nonchain draws. They are not the forgetting-certificate total: that is 5,841 families / 6,144 draws. Some chain families fail the forgetting test and retain their separate inherited chain-growth argument. The complement of this original label aggregation is 6,028 first-ray-growth draws: 5,962 non-forgetting and 66 capped. Their members-anywhere growth is undecided by this test. The target-type scope exclusions below remove another 188 draws from the conditional conservative tally.", "",
            "## What the chain count means", "",
            "The reproducing filter expands every earlier numeric call, preserving each occurrence and the definition identity of each `SELF`. Both S and main must then have exactly counter `{S: 1}`. This permits finite helpers, wrappers, and unused definitions. It is broader than the preregistration's literal 'one definition, one SELF call': 1,155 counted families / 1,155 draws have multiple definitions. The claimed 5,190 / 5,633 count needs this actual filter stated.", "",
            "The 657 `c=1 other` rows are the complement of chains among one-SELF rows. Of them, 489 have `other_holding_calls=true` in the used expansion of S or main. The other 168 have only the S recursive type but multiple entries from main. The JSON records exact occurrence-counter splits. Thus 'one SELF call and other self-holding calls' needs to include additional entries from main and must not be read as 'another recursive type in S'. The independently derived `chain`, c, n_defs, and used-expansion other-type flags match every recorded result.", ""]
    h = data["chain_structure"]["missing_depths"]
    out += [f'Among the counted chains, {h["families_with_absence"]} families / {h["draws_with_absence"]} draws have at least one absent prefix ray bond in the 30 recorded depths; {h["families_with_absence_after_depth20"]} families / {h["draws_with_absence_after_depth20"]} draws still do after depth 20. Literal one-definition chains account for {h["literal_families_with_absence"]} such families / {h["literal_draws_with_absence"]} draws. There are {h["declining_families"]} chains with a recorded decline, including {h["finite_to_finite_declining_families"]} with a finite-to-finite decline. These are retained in the JSON; absence is not a zero-sized bond.', "",
            "The prior referee's counterexample is freshly re-enumerated. Its three successive constraints are `NAE(a,b,c), NAE(b,c,d), NAE(c,d,e)`, with c,d,e introduced at depths 1,2,3. No prefix-only bond through depth two contains root a and depth-two d. Yet `{a,b,d,e}` is a four-member bond: exactly `0011` and `1100` are forbidden, and every deletion leaves all eight states. Every allowed prefix extends infinitely. This counted family therefore has `L_any(2)<=4` while `L_ray(2)` is absent. Equality is false for the counted class.", "",
            "A finite bond reaching depth s also reaches the greatest introduction depth d of any member, and qualifies for prefix-only `L_ray(d)`. Therefore the replacement is", "",
            "```text", "inf_{d>=s} L_ray(d) <= L_any(s) <= L_ray(s).", "```", "",
            "An inherited uniform positive linear lower bound on finite ray minima transfers to every finite members-anywhere minimum. When ray minima are eventually finite at every depth and equal `lambda*s+O(1)`, the same asymptotic rate follows. At-depth existence remains a separate premise. The census conclusions already qualify their lower bound by 'at depths where a bond exists'; keep that qualification and do not use the false equality as its proof.", "",
            "## The 224 limit-only rows and r", "",
            "Reconstructing one-definition limit-only growth rows from raw draws (`fate != forever`, `limit_alive=true`, at least two SELF calls) gives exactly 224 keys / 224 draws: zero certified, 203 non-forgetting, 21 capped. The heading 'never forget' overstates this: the 21 capped cases remain undecided for forgetting. A failed forgetting test does not imply bounded members-anywhere bond size, and no claim that the growth is absent follows.", "",
            "| r | Certified families, all / nonchains | Certified draws, all / nonchains |",
            "| --- | ---: | ---: |"]
    for r in range(1, 13):
        a = data["r_distributions"]["all"]
        n = data["r_distributions"]["nonchain"]
        out.append(f'| {r} | {a["families"].get(r, 0):,} / {n["families"].get(r, 0):,} | {a["draws"].get(r, 0):,} / {n["draws"].get(r, 0):,} |')
    sample = data["outside_EVERY_RAY_sample"]
    outside = sample["certified_by_weight"]
    lo, hi = outside["wilson95"]
    out += ["", "All reported family r distributions reproduce exactly; the JSON additionally gives weighted r distributions and every stratum. No recorded empty relation occurs. All 66 caps report the 250,000-product construction cap, so 'none found up to a tested r' is not their recorded stopping reason.", "",
            "## Outside EVERY-RAY's selected sample", "",
            f'After replacing the 28 matching phase-two sample rows, G contains 300 keys / {sample["excluded_draws"]} raw draws. Excluding all of them from c>=2 leaves {sample["families"]:,} keys / {sample["draws"]:,} draws. Certified successes are {outside["numerator"]:,} keys / {outside["numerator"]:,} draws: **{outside["percent"]:.6f}%**, nominal Wilson **{100*lo:.6f}%–{100*hi:.6f}%**. The preregistered 8%–25% band holds. The exclusion removes {sample["excluded_certified_families"]} certified keys / {sample["excluded_certified_draws"]} draws, rather than just the 43 certified path growers: one further certified key was unresolved in the path computation.', "",
            "The refreshed sample has 208 path-bounded, 66 path-growing and 26 unresolved families. Its 208 bounded rows contain no forgetting-certified family; 43 of the 66 growers and one of the 26 unresolved rows are certified. This is a consistency check, as preregistered, and not independent proof of the growth argument.", "",
            "## Supplemental restricted arithmetic", ""]
    corrected = data["supplemental_corrected_bound"]
    out += ["**Conditional conservative lower tally: 7,063 draws.** The lead's separate `target_inventory.json` identifies 186 certified nonchain draws with own distinctions in another reachable recursive type: 33 among c>=2 and 153 among c=1 nonchains. Another two have a zero-own recursive type that can take arbitrarily many SELF steps before calling S, creating deep S targets without corresponding S transitions. There are eight delayed-S cases in total, six overlapping the first exclusion. Direct checks in the lead's lane found bounded counterexamples from both excluded classes. This lane reconciles the supplied inventory totals with its raw strata but does not independently repeat that structural inventory or its SAT checks.", "",
            "Excluding all 188 leaves `5633 + 1046 + 384 = 7063` draws. The sufficient scope condition is that every deep own target has S-only recursive ancestry after main's finite expansion: other reachable recursive types neither introduce own distinctions nor delay later S targets. Subject to the corrected chain and gap arguments, this is a conservative lower tally, not an exact incidence of all-copy growth. The 6,216 first-ray-growth draws outside this tally include both undecided cases and counterexamples; they are not all established nongrowers.", ""]
    for name, label in (("first_ray_growth_weight", "Of first-ray-growth draws"), ("all_nested_weight", "Of all nested draws")):
        row = corrected[name]
        lo, hi = row["wilson95"]
        out.append(f'{label}: **{row["numerator"]:,}/{row["denominator"]:,} = {row["percent"]:.6f}%**, nominal Wilson **{100*lo:.6f}%–{100*hi:.6f}%**.')
        out.append("")
    out += ["## Provenance and limits", "",
            "Run: `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/CENSUS-FORGET-20261114-001/referee-R1/codex/chain_share_audit.py`. Inputs and audit code have SHA-256 hashes in `chain_share_audit.json`. The script compares complete raw key sets, independently derives structural strata, streams every draw and result, checks nominal intervals, re-enumerates the finite counterexample with rejection controls, and verifies all reading.json totals requested in this lane. It uses one compute process with a 2 GiB address-space ceiling.", "",
            "Certificate soundness, exact limit relations, the general gap proof, target-type scope, depth shifts for wrappers, and re-proving the inherited census graph analysis are outside this numerical lane. The combined 54.6% and 3.25% reproduce the original label aggregation; the lead's counterexamples prevent reporting those values as proved all-copy-growth shares. They are observed certificate-label-and-chain yields under recorded description weight, not exact probabilities over all nested patterns or the full share that truly grows.", ""]
    return "\n".join(out)


if __name__ == "__main__":
    main()
