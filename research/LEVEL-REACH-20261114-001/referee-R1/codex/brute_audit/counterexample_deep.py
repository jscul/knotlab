"""Exact model-table analysis and k0=2 falsification search."""
from __future__ import annotations

import itertools as it
import json
import random
import resource
import time
from pathlib import Path

from pysat.solvers import Solver
import brute_supports as brute
from compare_and_extend import bounds

HERE = Path(__file__).resolve().parent


def enumerate_models(triples, nvars, limit=65536):
    """Block each complete assignment; never use a producer model enumerator."""
    models = []
    solver = Solver(name="cadical195", bootstrap_with=brute.clauses(triples))
    solver.add_clause([nvars, -nvars])
    while solver.solve():
        assignment = set(solver.get_model())
        bits = tuple(int(v + 1 in assignment) for v in range(nvars))
        assert all(len({bits[v] for v in t}) == 2 for t in triples)
        models.append(bits)
        if len(models) > limit:
            solver.delete()
            return models, False
        solver.add_clause([-v - 1 if b else v + 1 for v, b in enumerate(bits)])
    solver.delete()
    return models, True


def quotient_bonds(models, A, B):
    """Exact reduction by equality/opposition; at most one per larger bond.

    Variables whose model columns are equal or complementary form a binary
    bond class. Any minimal non-full support of size >=3 uses at most one
    member of each class, because otherwise it contains a non-full pair.
    The remaining support search is exhaustive over the quotient relation.
    """
    A, B = set(A), set(B)
    groups = {}
    for v in range(len(models[0])):
        column = tuple(m[v] for m in models)
        complement = tuple(1 - b for b in column)
        signature = min(column, complement)
        groups.setdefault(signature, []).append(v)
    groups = list(groups.values())
    result = {"binary_classes": groups, "class_count": len(groups)}
    for group in groups:
        if A.intersection(group) and B.intersection(group):
            return {**result, "L": 2, "complete": True}
    reps = [g[0] for g in groups]
    quotient = {tuple(m[v] for v in reps) for m in models}
    result["quotient_models"] = sorted(map(list, quotient))
    if len(groups) > 18:
        return {**result, "complete": False, "reason": "more than 18 quotient distinctions"}
    all_bonds = []
    crossing = []
    full = {(): True}
    for size in range(1, len(groups) + 1):
        for support in it.combinations(range(len(groups)), size):
            values = {tuple(bits[i] for i in support) for bits in quotient}
            full[support] = len(values) == (1 << size)
            if not full[support] and all(full[support[:j] + support[j + 1:]] for j in range(size)):
                all_bonds.append(support)
                if any(A.intersection(groups[i]) for i in support) and any(B.intersection(groups[i]) for i in support):
                    crossing.append(support)
    return {**result, "L": min(map(len, crossing)) if crossing else "none", "complete": True,
            "quotient_bonds": list(map(list, all_bonds)), "crossing_quotient_bonds": list(map(list, crossing))}


def analyze_witness():
    original = json.loads((HERE / "actual_monotonicity_violation.json").read_text())
    key = brute.freeze_key(original["key"])
    out = {"case": original["case"], "key": original["key"], "k0": original["k0"], "s": original["s"], "levels": []}
    for N in (original["N_before"], original["N_after"]):
        triples = brute.placement_pattern(key, N)
        nvars = (1 << (N + 1)) - 1
        models, complete = enumerate_models(triples, nvars)
        A, B = bounds(original["k0"], original["s"])
        quotient = quotient_bonds(models, A, B) if complete else None
        A, B = bounds(original["k0"], original["s"])
        exact_cap4 = brute.least_bond(triples, nvars, A, B, 4)
        row = {"N": N, "knots": triples, "model_count": len(models), "models_complete": complete,
               "models": list(map(list, models)) if complete else None,
               "quotient": quotient, "brute_cap4": exact_cap4}
        out["levels"].append(row)
        print(json.dumps({"witness_N": N, "models": len(models), "complete": complete,
                          "classes": quotient["class_count"] if quotient else None,
                          "L": quotient.get("L") if quotient else None}), flush=True)
    (HERE / "actual_monotonicity_model_tables.json").write_text(json.dumps(out, indent=2) + "\n")


def search_k2():
    records = brute.population_records()
    random.Random("k2-monotonicity-20261114").shuffle(records)
    attempted = 0
    checks = 0
    started = time.perf_counter()
    violations = []
    with (HERE / "monotonicity_k2_results.jsonl").open("w") as f:
        for record in records:
            attempted += 1
            key = brute.freeze_key(record["key"])
            for N, s in ((3, 1), (4, 2), (4, 1)):
                first = brute.placement_pattern(key, N)
                A, B = bounds(2, s)
                before = brute.least_bond(first, (1 << (N + 1)) - 1, A, B, 4)
                if not isinstance(before["L"], int):
                    continue
                second = brute.placement_pattern(key, N + 1)
                A, B = bounds(2, s)
                after = brute.least_bond(second, (1 << (N + 2)) - 1, A, B, before["L"])
                violation = after["L"] != "dead" and (not isinstance(after["L"], int) or after["L"] > before["L"])
                checks += 1
                row = {"case": record["case"], "key": record["key"], "N_before": N, "N_after": N + 1,
                       "k0": 2, "s": s, "before": before, "after": after, "violation": violation}
                f.write(json.dumps(row) + "\n")
                f.flush()
                if violation:
                    violations.append(row)
                    (HERE / "actual_k2_monotonicity_violation.json").write_text(json.dumps(row, indent=2) + "\n")
                    print(json.dumps({"K2_VIOLATION": record["case"], "N": N, "s": s,
                                      "before": before["L"], "after": after["L"]}), flush=True)
                    break
            if violations:
                break
    result = {"descriptions_attempted": attempted, "finite_before_comparisons": checks,
              "violations": violations, "seconds": time.perf_counter() - started}
    (HERE / "monotonicity_k2_summary.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    started = time.perf_counter()
    analyze_witness()
    search_k2()
    (HERE / "resources_counterexample.json").write_text(json.dumps({
        "seconds": time.perf_counter() - started,
        "max_rss_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }, indent=2) + "\n")
