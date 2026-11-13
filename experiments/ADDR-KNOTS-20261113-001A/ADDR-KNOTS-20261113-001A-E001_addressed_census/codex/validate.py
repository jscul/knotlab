"""Independent registered checks; run exactly one named gate per invocation.

Validation seeds are procedural controls, not replacements for either frozen
scientific population: V-act=20261117, V-rel=20261118, V-sat small=20261119,
V-sat panel=20261120, V-act-class=20261121.  V-code uses the frozen W draw
seed 20261113 through run_census.build_draws and does no census solving.

All durable output is written beneath this file's directory.  Heavy gates
are deliberately opt-in; merely importing this module launches no work.
"""

import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import traceback

for _thread_variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_thread_variable] = "1"

import reference


HERE = Path(__file__).resolve().parent
PARTS = HERE / "validation_parts"
GATES = ("V-act", "V-rel", "V-sat", "V-B0", "V-act-class", "V-code")
DENSITY_EDGES = (0.0, 1.0, 1.5, 2.1, 3.0, 4.5, float("inf"))


def plain(value):
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [plain(v) for v in value]
    if hasattr(value, "tolist"):
        return plain(value.tolist())
    if hasattr(value, "item"):
        return value.item()
    return value


def digest(value):
    raw = json.dumps(plain(value), separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()


def progress(gate, done, total):
    print(f"{gate}: {done}/{total}", flush=True)


def random_automaton(rng, s):
    return (
        tuple(rng.randrange(2) for _ in range(s)),
        tuple(rng.randrange(s) for _ in range(s)),
        tuple(rng.randrange(s) for _ in range(s)),
    )


def random_key(rng):
    s = rng.randint(1, 5)
    aut = random_automaton(rng, s)
    r = rng.randint(1, 8)
    word_count = 1 + s + s * s
    # Drawing a uniformly chosen sorted 3-subset, with independent list draws.
    placements = tuple(sorted({tuple(sorted(rng.sample(range(word_count), 3))) for _ in range(r)}))
    return (s, *aut, placements), r


def _core():
    import addr
    return addr


def gate_act(_args):
    core = _core()
    seed = 20261117
    rng = random.Random(seed)
    failures, cases, addresses = [], 0, 0
    automata = []
    for i in range(200):
        s = rng.randint(1, 5)
        aut = random_automaton(rng, s)
        automata.append((s, aut))
        for word in reference.words(s):
            for n in range(0, 9):
                expected = reference.recursive_action(aut, word, n)
                actual = tuple(map(int, core.action(aut, word, n)))
                cases += 1
                addresses += 1 << n
                if actual != expected:
                    failures.append({"automaton_index": i, "aut": aut, "word": word, "n": n,
                                     "actual": actual, "expected": expected})
        if (i + 1) % 20 == 0:
            progress("V-act", i + 1, 200)
    return {"passed": not failures, "seed": seed, "automata": 200,
            "action_cases": cases, "address_comparisons": addresses,
            "automata_sha256": digest(automata), "failures": failures,
            "reference": "Plain recursive first-letter action, every W_s word, levels 0..8 including the empty address."}


def gate_rel(_args):
    core = _core()
    seed = 20261118
    rng = random.Random(seed)
    failures, cases, addresses = [], 0, 0
    provenance = []
    for i in range(200):
        s = rng.randint(1, 5)
        aut = random_automaton(rng, s)
        placement = tuple(rng.sample(reference.words(s), 3))
        provenance.append((s, aut, placement))
        for ii, jj in itertools.permutations(range(3), 2):
            items = core.relative_product(placement[ii], placement[jj])
            product = core.product_automaton(aut, items)
            for n in range(0, 9):
                expected = reference.relative_permutation(aut, placement[ii], placement[jj], n)
                actual = tuple(map(int, core.action(product, (0,), n)))
                cases += 1
                addresses += 1 << n
                if expected != actual:
                    failures.append({"automaton_index": i, "aut": aut, "placement": placement,
                                     "i": ii, "j": jj, "items": items, "n": n,
                                     "actual": actual, "expected": expected})
        if (i + 1) % 20 == 0:
            progress("V-rel", i + 1, 200)
    return {"passed": not failures, "seed": seed, "automata_and_placements": 200,
            "relative_maps_per_placement": 6, "action_cases": cases,
            "address_comparisons": addresses, "panel_sha256": digest(provenance),
            "failures": failures,
            "reference": "Independent ordinary-word permutations; inverse by explicit array inversion; gj after gi^-1."}


def gate_act_class(_args):
    core = _core()
    seed = 20261121
    rng = random.Random(seed)
    comparisons, failures = [], []
    for i in range(500):
        s = rng.randint(1, 5)
        aut = random_automaton(rng, s)
        starts = tuple(range(s))
        theta = reference.exact_activity_counts(aut, starts, 160)
        expected = reference.activity_label(theta)
        actual, degree = core.activity_class(aut, starts)
        row = {"index": i, "s": s, "aut": aut, "exact_letter_class": actual,
               "degree_not_tested": degree, "counted_class": expected,
               "theta_80": theta[79], "theta_160": theta[159],
               "max_1_80": max(theta[:80]), "max_81_160": max(theta[80:])}
        comparisons.append(row)
        if actual != expected:
            failures.append({**row, "theta_1_160": theta})
        if (i + 1) % 50 == 0:
            progress("V-act-class", i + 1, 500)
    return {"passed": not failures, "seed": seed, "automata": 500,
            "U": "All original state maps of each sampled automaton, aggregated by maximum.",
            "reference": "Nonidentity by reachability to a root swap; exact integer section-count DP.",
            "classification": {"finitary": "theta_160=0",
                               "exponential": "theta_80>0 and theta_160>=1000*theta_80",
                               "bounded": "remaining, max(theta_81..160)<=max(theta_1..80)",
                               "polynomial": "remaining"},
            "class_counts": dict(Counter(r["exact_letter_class"] for r in comparisons)),
            "comparisons": comparisons, "failures": failures}


def _population():
    import run_census
    draws, keys = run_census.build_draws()
    if not isinstance(draws, list) or not isinstance(keys, dict):
        raise TypeError("build_draws must return (list[draw], dict[key_id:key])")
    return draws, {str(k): reference.unpack_key(v) for k, v in keys.items()}


def gate_code(_args):
    draws, _keys = _population()
    rows = [row for row in draws if row["population"] == "W"]
    s = [row["s"] for row in rows]
    r = [row["r"] for row in rows if "r" in row and row["r"] is not None]
    s_test = reference.gamma_chisquare(s, 0.01)
    r_test = reference.gamma_chisquare(r, 0.01)
    rejected_s = sum(row.get("rejected") == "s" for row in rows)
    rejected_r = sum(row.get("rejected") == "r" for row in rows)
    checks = {
        "exactly_40000_W_draws": len(rows) == 40000,
        "every_s_retained_even_when_rejected": len(s) == 40000,
        "r_reached_exactly_when_s_accepted": len(r) == sum(int(row["s"]) <= 5 for row in rows),
        "s_gamma_test": s_test["passed"], "r_gamma_test": r_test["passed"],
    }
    return {"passed": all(checks.values()), "seed": 20261113,
            "panel": "Sampling only: frozen W draws; no level patterns or SAT calls.",
            "W_draws": len(rows), "r_samples": len(r), "rejected_s": rejected_s,
            "rejected_r": rejected_r, "checks": checks,
            "s": s_test, "r": r_test,
            "s_r_metadata_sha256": digest([(row["index"], row["s"], row.get("r"), row.get("rejected")) for row in rows]),
            "pooling_note": "The low-expected upper-tail values are pooled into one cell; each tested cell has expected count >=5."}


def independent_solve(pattern, n, solver_name="glucose4", budget=2000000):
    """Independent SAT wrapper, with both NAE clauses built by plain loops."""
    from pysat.solvers import Solver
    started = time.perf_counter()
    clauses = []
    for triple in pattern:
        literals = [int(v) + 1 for v in triple]
        clauses.append(literals)
        clauses.append([-v for v in literals])
    if clauses:
        smallest_address = min(int(address) for triple in pattern for address in triple)
        clauses.append([smallest_address + 1])
    with Solver(name=solver_name, bootstrap_with=clauses) as solver:
        solver.conf_budget(int(budget))
        result = solver.solve_limited(expect_interrupt=False)
        statistics = solver.accum_stats()
        model = solver.get_model() if result is True else None
    values = None
    if result is True:
        values = [False] * (1 << n)
        for literal in model or ():
            if 0 < abs(literal) <= len(values):
                values[abs(literal) - 1] = literal > 0
    return {"verdict": None if result is None else int(result),
            "conflicts": int(statistics.get("conflicts", 0)),
            "wall_seconds": time.perf_counter() - started,
            "model": values}


def _solver_summary(result, pattern, n):
    verdict = result["verdict"]
    return {"verdict": verdict, "conflicts": int(result["conflicts"]),
            "wall_seconds": float(result["wall_seconds"]),
            "model_valid": reference.model_satisfies(pattern, result.get("model"), n) if verdict == 1 else None}


def density_bin(density):
    for i in range(len(DENSITY_EDGES) - 1):
        if DENSITY_EDGES[i] <= density < DENSITY_EDGES[i + 1]:
            return i
    raise ValueError("invalid knot density")


def _sat_panel(draws, keys, seed=20261120, per_level=150):
    """Choose the entire comparison panel before asking either solver.

    Candidate keys are sampled in round-robin (s, original r) strata, with
    at most 1,200 distinct E keys per level.  Actual level density supplies
    the six frozen bins.  Round-robin selection from those bins retains
    150 instances at each level and records each unavailable density cell.
    """
    core = _core()
    rng = random.Random(seed)
    by_key = {}
    for draw in draws:
        if draw["population"] == "E":
            by_key.setdefault(str(draw["key_id"]), draw)
    strata = defaultdict(list)
    for key_id, draw in by_key.items():
        strata[(int(draw["s"]), int(draw["r"]))].append(key_id)
    for values in strata.values():
        rng.shuffle(values)
    groups = sorted(strata)
    candidate_ids = []
    offset = 0
    while len(candidate_ids) < min(1200, len(by_key)):
        added = False
        for group in groups:
            if offset < len(strata[group]):
                candidate_ids.append(strata[group][offset])
                added = True
                if len(candidate_ids) == min(1200, len(by_key)):
                    break
        if not added:
            break
        offset += 1
    panel, metadata = [], []
    for n in (9, 10):
        bins = [[] for _ in range(6)]
        for i, key_id in enumerate(candidate_ids):
            pattern = core.level_pattern(keys[key_id], n)
            density = len(pattern) / (1 << n)
            provenance = {field: by_key[key_id].get(field) for field in ("population", "s", "a", "j", "r", "r_capped")}
            row = {"key_id": key_id, "n": n, "knots": len(pattern),
                   "density": density, "density_bin": density_bin(density),
                   "provenance": provenance, "pattern_sha256": digest(pattern)}
            bins[row["density_bin"]].append(row)
            if (i + 1) % 200 == 0:
                progress(f"V-sat density panel n={n}", i + 1, len(candidate_ids))
        available = [len(cell) for cell in bins]
        selected = []
        offset = 0
        while len(selected) < per_level:
            added = False
            for cell in bins:
                if offset < len(cell):
                    selected.append(cell[offset])
                    added = True
                    if len(selected) == per_level:
                        break
            if not added:
                break
            offset += 1
        panel.extend(selected)
        metadata.append({"n": n, "candidates": len(candidate_ids),
                         "available_by_density_bin": available,
                         "selected_by_density_bin": [sum(row["density_bin"] == b for row in selected) for b in range(6)],
                         "selected": len(selected)})
    return panel, {"seed": seed, "candidate_key_count": len(candidate_ids),
                   "candidate_key_ids_sha256": digest(candidate_ids),
                   "sampling": "Round-robin (s, original r) strata; first 1200 distinct E keys; actual-density bins before solver calls.",
                   "density_edges": [0, 1, 1.5, 2.1, 3, 4.5, "infinity"],
                   "selection": "Round-robin across six density bins; record empty cells and transfer only their unused slots.",
                   "levels": metadata}


def gate_sat(_args):
    core = _core()
    seed = 20261119
    rng = random.Random(seed)
    small, failures = [], []
    for i in range(1000):
        key, r = random_key(rng)
        n = 1 + i % 4
        pattern = reference.level_pattern(key, n)
        vector_pattern = tuple(tuple(map(int, p)) for p in core.level_pattern(key, n))
        brute = reference.brute_force_nae(pattern, n)
        produced = core.solve_pattern(core.level_pattern(key, n), n, solver_name="cadical195", budget=2000000)
        summary = _solver_summary(produced, pattern, n)
        row = {"index": i, "key": key, "key_sha256": digest(key), "original_r": r,
               "n": n, "knots": len(pattern), "pattern_sha256": digest(pattern),
               "pattern_agrees": pattern == vector_pattern, "brute_force": brute,
               "cadical195": summary}
        small.append(row)
        if not row["pattern_agrees"] or summary["verdict"] != brute["verdict"] or (summary["verdict"] == 1 and not summary["model_valid"]):
            failures.append({"part": "brute_force", **row})
        if (i + 1) % 100 == 0:
            progress("V-sat exhaustive small instances", i + 1, 1000)
    draws, keys = _population()
    panel, panel_metadata = _sat_panel(draws, keys)
    panel_path = PARTS / "V-sat-panel.json"
    panel_path.write_text(json.dumps(plain({"metadata": panel_metadata, "panel": panel}), indent=2) + "\n")
    large, tiny_attempts = [], []
    both_decide = both_null = one_null = 0
    for i, panel_row in enumerate(panel):
        n, key_id = panel_row["n"], panel_row["key_id"]
        pattern = core.level_pattern(keys[key_id], n)
        first = core.solve_pattern(pattern, n, solver_name="cadical195", budget=2000000)
        second = independent_solve(pattern, n, "glucose4", 2000000)
        row = {**panel_row, "cadical195": _solver_summary(first, pattern, n),
               "glucose4": _solver_summary(second, pattern, n)}
        ca, gl = row["cadical195"]["verdict"], row["glucose4"]["verdict"]
        if ca is None and gl is None:
            both_null += 1
        elif ca is None or gl is None:
            one_null += 1
        else:
            both_decide += 1
            if ca != gl:
                failures.append({"part": "two_solvers", **row})
        for solver_name in ("cadical195", "glucose4"):
            solver_result = row[solver_name]
            if solver_result["verdict"] == 1 and not solver_result["model_valid"]:
                failures.append({"part": "invalid_model", "solver": solver_name, **row})
        large.append(row)
        if (i + 1) % 10 == 0:
            progress("V-sat budgeted solver comparisons", i + 1, len(panel))
    # Reuse full-budget decided panel instances; keep every budget-ten attempt.
    for row in large:
        if row["cadical195"]["verdict"] is None:
            continue
        n, key_id = row["n"], row["key_id"]
        pattern = core.level_pattern(keys[key_id], n)
        tiny = core.solve_pattern(pattern, n, solver_name="cadical195", budget=10)
        attempt = {"key_id": key_id, "n": n, "knots": len(pattern),
                   "density": row["density"], "full_verdict": row["cadical195"]["verdict"],
                   "budget": 10, **_solver_summary(tiny, pattern, n)}
        tiny_attempts.append(attempt)
        if tiny["verdict"] is None:
            break
    panel_checks = {
        "exactly_300_instances": len(panel) == 300,
        "150_at_level9": sum(row["n"] == 9 for row in panel) == 150,
        "150_at_level10": sum(row["n"] == 10 for row in panel) == 150,
        "dense_actual_patterns_present": any(row["density"] >= 2.1 for row in panel),
        "both_solvers_decide_on_some_instances": both_decide > 0,
        "tiny_budget_demonstrated_undecided": any(row["verdict"] is None for row in tiny_attempts),
    }
    return {"passed": not failures and all(panel_checks.values()),
            "small_seed": seed, "small_instances": len(small),
            "small_levels": dict(Counter(row["n"] for row in small)),
            "assignments_read": sum(row["brute_force"]["assignments_read"] for row in small),
            "small_comparisons": small, "panel_metadata": panel_metadata,
            "panel_path": str(panel_path.relative_to(HERE)), "large_comparisons": large,
            "budget_per_solver": 2000000, "both_decide": both_decide,
            "both_undecided": both_null, "one_undecided": one_null,
            "tiny_budget_attempts": tiny_attempts, "checks": panel_checks,
            "failures": failures,
            "note": "Nulls are retained. Agreement is required whenever both budgeted solvers decide; a null is never an alive verdict."}


def _smoke_records(smoke_dir):
    records = []
    for path in sorted((smoke_dir / "keys").glob("*.jsonl")):
        for line_number, line in enumerate(path.read_text().splitlines(), 1):
            if line.strip():
                records.append((path.name, line_number, json.loads(line)))
    return records


def _record_levels(record):
    if "knots_n" in record and "verdict_n" in record:
        if len(record["knots_n"]) != len(record["verdict_n"]):
            raise ValueError("unequal smoke profile lengths")
        return [{"n": n, "knots": knots, "verdict": verdict}
                for n, (knots, verdict) in enumerate(zip(record["knots_n"], record["verdict_n"]), 1)]
    if "levels" in record:
        levels = record["levels"]
        if isinstance(levels, dict):
            return [levels[k] for k in sorted(levels, key=int)]
        return levels
    if "n" in record and "verdict" in record:
        return [record]
    raise KeyError("smoke record has neither levels nor a level verdict")


def check_settled_smoke(smoke_dir):
    """P1 checks, with the known F0/P1 conflict explicitly quarantined."""
    rows = _smoke_records(smoke_dir)
    by_key = defaultdict(list)
    key_values = {}
    for filename, line_number, record in rows:
        key = reference.unpack_key(record["key"])
        identity = record.get("key_id", digest(key))
        key_values[identity] = key
        for level in _record_levels(record):
            by_key[identity].append((filename, line_number, level))
    cases, failures, skipped = [], [], []
    for identity, records in sorted(by_key.items()):
        key = key_values[identity]
        levels = [row[2] for row in sorted(records, key=lambda item: int(item[2]["n"]))]
        counts = [int(level.get("knots", level.get("knot_count", level.get("knots_n", -1)))) for level in levels]
        if min(counts) < 0:
            raise KeyError("smoke level missing knot count")
        verdicts = [level["verdict"] for level in levels]
        fate = reference.independent_fate(verdicts, counts)
        single = len(key[4]) == 1
        first_letter = reference.first_letter_settled(key)
        case = {"key_id": identity, "single_distinct_placement": single,
                "first_letter_settled": first_letter, "levels": [level["n"] for level in levels],
                "knot_counts": counts, "verdicts": verdicts, "independent_fate": fate}
        if single or first_letter:
            cases.append(case)
            if fate == "F0":
                skipped.append({**case, "affected_assertion": "P1 demands F3 although the frozen fate definition gives F0 when every read level has no knot."})
            elif fate != "F3":
                failures.append(case)
    ambiguities = []
    if skipped:
        ambiguities.append("P1/F0 conflict: a settled description can place no knot at every read level. The F3 assertion alone is skipped for these explicitly listed F0 cases; all other assertions remain active.")
    return {"passed": bool(rows) and not failures,
            "smoke_directory": str(smoke_dir), "source_jsonl_rows": len(rows),
            "distinct_keys": len(by_key), "settled_cases": cases,
            "skipped_F0_assertions": skipped, "failures": failures,
            "ambiguities": ambiguities}


def gate_b0(args):
    check_path = HERE / "check.py"
    result_path = HERE / "result.json"
    before_sha = hashlib.sha256(check_path.read_bytes()).hexdigest()
    process = subprocess.run([sys.executable, "-B", str(check_path)], cwd=HERE,
                             capture_output=True, text=True, check=False)
    proof = json.loads(result_path.read_text()) if result_path.exists() else {}
    smoke = check_settled_smoke(Path(args.smoke_dir).resolve())
    hash_agrees = proof.get("check_sha256") == before_sha
    return {"passed": process.returncode == 0 and proof.get("status") == "passed" and hash_agrees and smoke["passed"],
            "check_sha256": before_sha,
            "result_check_sha256_agrees": hash_agrees,
            "command": [sys.executable, "-B", str(check_path)],
            "returncode": process.returncode, "printed_line": process.stdout.strip(),
            "stderr": process.stderr, "proof_result": proof,
            "settled_smoke": smoke, "ambiguities": smoke["ambiguities"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", required=True, choices=GATES,
                        help="Run one gate only; heavy work starts only on this explicit request.")
    parser.add_argument("--smoke-dir", default=str(HERE / "smoke_uninterrupted"))
    args = parser.parse_args(argv)
    PARTS.mkdir(exist_ok=True)
    started = time.perf_counter()
    functions = {"V-act": gate_act, "V-rel": gate_rel, "V-sat": gate_sat,
                 "V-B0": gate_b0, "V-act-class": gate_act_class, "V-code": gate_code}
    try:
        result = functions[args.gate](args)
    except Exception as error:
        result = {"passed": False, "exception": type(error).__name__,
                  "error": str(error), "traceback": traceback.format_exc()}
    result.update({"gate": args.gate, "status": "passed" if result["passed"] else "failed",
                   "wall_seconds": time.perf_counter() - started,
                   "python": sys.executable,
                   "validation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   "reference_sha256": hashlib.sha256((HERE / "reference.py").read_bytes()).hexdigest()})
    output = PARTS / (args.gate + ".json")
    output.write_text(json.dumps(plain(result), indent=2, allow_nan=False) + "\n")
    print(f"{args.gate}: {result['status']} ({result['wall_seconds']:.3f}s); {output}", flush=True)
    if not result["passed"]:
        print(json.dumps({key: result[key] for key in ("exception", "error", "checks") if key in result}), flush=True)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
