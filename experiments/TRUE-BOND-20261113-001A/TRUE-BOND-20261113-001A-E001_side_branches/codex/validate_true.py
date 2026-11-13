#!/usr/bin/env python
"""Bounded validation; preserve skipped ambiguities and incomplete SAT sizes."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time

for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"

from pysat.solvers import Solver
from sat_validation import build_truncation, count_bonds, tiny_fixture_checks
from true_bond import FamilyDP, HERE, bd_ray_values, study_families


HEIGHT_QUESTION = (
    "Should finite validation use uniform depth D=s+h (side table T_(D-j) at C_j), "
    "or the same T_h side table at every ray copy? These allow different W."
)
CAP_QUESTION = (
    "For counts through least+1, may the validation-only multiplicity table "
    "use cost cap (least+1)-2, one above the production side cap if least=L_ray?"
)
SMALLEST_QUESTION = (
    "Which size ordering defines the smallest family: own count, description "
    "length, SELF count, or number of identities in the validation truncation?"
)


def validation_ranking(item):
    idx, defs = item
    _, own, calls = defs[0]
    branches = sum(callee == "SELF" for callee, _ in calls)
    n = 3 + own * sum(branches ** depth for depth in range(6))
    return n, len(calls), idx


def save(data):
    # All task-generated files, including the atomic replacement, are in CODEX.
    temporary = HERE / "validation.json.tmp"
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    temporary.replace(HERE / "validation.json")


def sat_bond_witness(truncation, chosen):
    """Direct SAT for every assignment of W and each single deletion; no masks."""
    with Solver(name="g3", bootstrap_with=truncation["clauses"]) as solver:
        def free(variables):
            return all(solver.solve(assumptions=[w + 1 if (a >> j) & 1 else -(w + 1)
                                                for j, w in enumerate(variables)])
                       for a in range(1 << len(variables)))
        constrained = not free(chosen)
        deletions = [free(chosen[:j] + chosen[j + 1:]) for j in range(len(chosen))]
    return {"chosen": chosen, "constrained": constrained, "deletions_free": deletions,
            "pass": constrained and all(deletions)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-seconds", type=float, default=5)
    parser.add_argument("--candidate-limit", type=int, default=100_000)
    args = parser.parse_args(argv)
    families = study_families()
    selected = [idx for idx, _ in sorted(families.items(), key=validation_ranking)[:10]]
    data = {
        "study_count": len(families), "selected_small_families": selected,
        "selection_rule": "ten smallest uniform D=5 identity counts, then call count, then idx; smallest requirement remains ambiguous",
        "ambiguous_smallest_candidate": selected[0], "full_study_run": False,
        "ambiguities": [HEIGHT_QUESTION, CAP_QUESTION, SMALLEST_QUESTION],
        "fixtures": tiny_fixture_checks(), "brute_force": [], "ray_check": [],
        "shortening": {"cases": [], "pass": None, "status": "pending"},
        "mutant": {"pass": None, "status": "pending"},
        "all_required_pass": False,
    }
    save(data)
    # SAT is unaffected by the conflicting DP height convention. Execute it
    # independently, without claiming the requested comparison has passed.
    cases = [(idx, s, 2) for idx in selected for s in (1, 2, 3)]
    # Do not designate a smallest family. These are conditional diagnostics.
    cases += [(selected[0], s, 3) for s in (1, 2, 3)]
    for idx, s, h in cases:
        sat = count_bonds(families[idx], s, h, candidate_limit=args.candidate_limit,
                          seconds_limit=args.case_seconds)
        data["brute_force"].append({"idx": idx, "s": s, "h": h,
                                   "sat": sat, "pass": None,
                                   "status": "skipped_ambiguity",
                                   "reason": HEIGHT_QUESTION,
                                   "smallest_designation_pending": h == 3})
        save(data)
        print(json.dumps({"kind": "SAT", "idx": idx, "s": s, "h": h,
                          "sat_status": sat["status"], "complete_through": sat["complete_through"],
                          "seconds": round(sat["seconds"], 3)}), flush=True)

    # Show both explicit alternative readings without selecting either.
    idx, s, h, count_cap = 709, 1, 2, 4
    alternatives = {}
    for convention in ("uniform_depth", "common_side_height"):
        dp = FamilyDP(families[idx], deadline=time.monotonic() + 15)
        alternatives[convention] = dp.finite_counts(s, h, count_cap, convention=convention)
    sat = next(case["sat"] for case in data["brute_force"] if case["idx"] == idx and case["s"] == s and case["h"] == h)
    data["height_diagnostic"] = {
        "idx": idx, "s": s, "h": h, "count_cap": count_cap,
        "alternatives": alternatives, "sat_counts": sat["counts"],
        "status": "diagnostic_only_no_convention_selected",
    }
    # Literal G:=F must reject a known nonempty collection of bonds.
    mutant = FamilyDP(families[idx], mutant=True, deadline=time.monotonic() + 15)
    mutant_counts = mutant.finite_counts(s, h, count_cap, convention="uniform_depth")
    truncation = build_truncation(families[idx], s, h)
    target = truncation["target"][0]
    witness = sat_bond_witness(truncation, [0, 2, target])
    data["mutant"] = {
        "idx": idx, "s": s, "h": h, "mutation": "G_S := F_S, including the empty choice",
        "sat_counts": sat["counts"], "mutant_counts": mutant_counts,
        "witness": witness,
        "pass": witness["pass"] and mutant_counts[3] == 0 and sat["counts"].get("3", 0) > 0,
        "status": "complete", "scope": "explicit uniform-truncation diagnostic; resolves no height ambiguity",
    }
    save(data)

    # Each family is checked at every requested ray depth, not just the depths
    # reached by the slower true-minimum smoke calculation.
    ray_ids = sorted(set(selected + [46, 231, 296, 914, 1304]))
    for idx in ray_ids:
        started = time.monotonic()
        expected, raw = bd_ray_values(families[idx], 12)
        dp = FamilyDP(families[idx], deadline=started + 45)
        for s in range(1, 13):
            if s > len(expected) or expected[s - 1] is None:
                case = {"idx": idx, "s": s, "pass": None, "status": "reference_not_reached"}
            else:
                try:
                    observed = dp.least(s, expected[s - 1], ray_only=True)
                    case = {"idx": idx, "s": s, "expected": expected[s - 1], "observed": observed,
                            "pass": observed == expected[s - 1], "status": "complete",
                            "bd_repeat": raw.get("rate")}
                except TimeoutError:
                    case = {"idx": idx, "s": s, "pass": None, "status": "timeout"}
            data["ray_check"].append(case)
        save(data)
        print(json.dumps({"kind": "ray", "idx": idx,
                          "seconds": round(time.monotonic() - started, 3)}), flush=True)

    # Bounded shortening search. This is validation, not the registered full run.
    for idx in selected:
        started = time.monotonic()
        reference, _ = bd_ray_values(families[idx], 3)
        dp = FamilyDP(families[idx], deadline=started + 10)
        for s, bound in enumerate(reference, 1):
            try:
                observed = dp.least(s, bound)
                case = {"idx": idx, "s": s, "L": observed, "L_ray": bound,
                        "shorter": observed is not None and observed < bound, "status": "complete"}
            except TimeoutError:
                case = {"idx": idx, "s": s, "L": None, "L_ray": bound,
                        "shorter": None, "status": "timeout"}
            data["shortening"]["cases"].append(case)
        save(data)
    shorter = [case for case in data["shortening"]["cases"] if case["shorter"]]
    data["shortening"].update(
        status="found" if shorter else "none_in_bounded_search",
        found=shorter, pass_note="requested finite DP comparison is skipped for height ambiguity",
    )
    # A finite SAT witness for the minimum also validates a shortening case
    # in the infinite pattern: boundary G was the supplied exact relation.
    for found in shorter:
        matched = next((case for case in data["brute_force"]
                        if case["idx"] == found["idx"] and case["s"] == found["s"]
                        and case["h"] == 2 and case["sat"]["through_least_plus_one"]), None)
        if matched is None:
            continue
        sat = matched["sat"]
        witness = next((chosen for chosen in sat["sample_bonds"] if len(chosen) == found["L"]), None)
        if witness is None:
            continue
        truncation = build_truncation(families[found["idx"]], found["s"], 2)
        locations = {identity: {"path": copy["path"], "own_index": j}
                     for copy in truncation["copies"] for j, identity in enumerate(copy["own"])}
        locations.update({j: {"top_port": j} for j in range(3)})
        diagnostic = {"idx": found["idx"], "s": found["s"], "h": 2,
                      "count_cap": found["L"] + 1, "witness": witness,
                      "creator_locations": [locations[w] for w in witness],
                      "sat_counts": sat["counts"], "alternatives": {},
                      "status": "diagnostic_only_no_convention_selected"}
        for convention in ("uniform_depth", "common_side_height"):
            dp = FamilyDP(families[found["idx"]], deadline=time.monotonic() + 15)
            diagnostic["alternatives"][convention] = dp.finite_counts(
                found["s"], 2, found["L"] + 1, convention=convention)
        diagnostic["direct_sat_witness"] = sat_bond_witness(truncation, witness)
        data["shortening_diagnostic"] = diagnostic
        data["shortening"]["pass"] = diagnostic["direct_sat_witness"]["pass"]
        break
    data["summary"] = {
        "sat_cases": len(data["brute_force"]),
        "sat_complete_through_least_plus_one": sum(case["sat"]["through_least_plus_one"] for case in data["brute_force"]),
        "required_count_comparisons_passed": 0,
        "required_count_comparisons_skipped_ambiguity": len(data["brute_force"]),
        "ray_checks_passed": sum(case["pass"] is True for case in data["ray_check"]),
        "ray_checks_total": len(data["ray_check"]),
        "mutant_pass": data["mutant"]["pass"],
        "shortening_found": len(shorter),
    }
    save(data)
    print(json.dumps(data["summary"], sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
