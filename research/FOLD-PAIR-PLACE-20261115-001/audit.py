"""Independent stored-program and paid-receipt audit; never run a solver.

Imports only the Python standard library. Raw primitive/call ASTs and NAND
circuits are interpreted here on every original input. Source truth/pairing
and fresh relabelings are checked from sealed JSON, without calling a task
generator. Failed-search totals are reaggregated and accounting identities
checked; with trace_limit=0 this is NOT a replay of unrecorded search trials.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parents[2]
TICKET = "FOLD-PAIR-PLACE-20261115-001"
FAMILY = TICKET + "-E001_pair_first"
DEFAULT = ROOT / "artifacts" / TICKET / FAMILY
SOURCE = ROOT / "experiments" / TICKET / FAMILY
PRIOR = ROOT / "artifacts/FOLD-PLACEMENT-20261115-001/FOLD-PLACEMENT-20261115-001-E001_fixed_inputs"
METHODS = ("reference-primitive", "triple-primitive", "triple-named", "triple-flat",
           "atomic-primitive", "guided-primitive", "guided-named", "guided-flat")
BLOCK = (0, 1, 7, 2, 6, 3, 5, 4)
OPS = ("AND", "OR", "XOR")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ensure(condition, message):
    if not condition:
        raise ValueError(message)


def bit(value):
    ensure(type(value) in (int, bool) and value in (0, 1), "nonliteral bit")
    return int(value)


def validate_circuit(circuit, expected_inputs):
    ensure(isinstance(circuit, dict), "missing physical circuit")
    n = circuit.get("inputs")
    ensure(type(n) is int and n == expected_inputs, "physical input arity mismatch")
    gates = circuit.get("gates")
    ensure(isinstance(gates, list), "physical gates must be a list")
    for index, gate in enumerate(gates):
        ensure(isinstance(gate, list) and len(gate) == 2, "malformed NAND")
        ensure(all(type(address) is int and 0 <= address < n + 2 + index for address in gate),
               "forward/noninteger NAND address")
    output = circuit.get("output")
    ensure(type(output) is int and 0 <= output < n + 2 + len(gates), "bad physical output")
    if "constants" in circuit:
        ensure(circuit["constants"] == {"zero": n, "one": n + 1}, "constant address metadata")
    if "nand_gates" in circuit:
        ensure(circuit["nand_gates"] == len(gates), "NAND length metadata")
    return circuit


def nand_scalar(circuit, x):
    n = circuit["inputs"]
    values = [(x >> j) & 1 for j in range(n)] + [0, 1]
    for a, b in circuit["gates"]:
        values.append(0 if values[a] and values[b] else 1)
    return values[circuit["output"]]


def ast_scalar(expr, x, binding):
    op = expr[0]
    if op == "input":
        return (x >> expr[1]) & 1
    if op == "const":
        return expr[1]
    values = [ast_scalar(child, x, binding) for child in expr[1:]]
    if op == "FOLD":
        local = values + [0, 1]
        for a, b in binding["gates"]:
            local.append(0 if local[a] and local[b] else 1)
        return local[binding["output"]]
    a, b = values
    if op == "AND":
        return int(bool(a) and bool(b))
    if op == "OR":
        return int(bool(a) or bool(b))
    return int(a != b)


def inspect_ast(expr, n):
    ensure(isinstance(expr, (list, tuple)) and expr, "malformed AST")
    op = expr[0]
    if op == "input":
        ensure(len(expr) == 2 and type(expr[1]) is int and 0 <= expr[1] < n, "bad AST input")
        return Counter(inputs=1)
    if op == "const":
        ensure(len(expr) == 2, "bad constant arity")
        bit(expr[1])
        return Counter(constants=1)
    ensure((op in OPS and len(expr) == 3) or (op == "FOLD" and len(expr) == 4), "bad AST gate/arity")
    counts = Counter({op: 1})
    for child in expr[1:]:
        counts.update(inspect_ast(child, n))
    return counts


def dependency_digest(circuit):
    # Commutativity and physical emission order do not change dependencies.
    values = [hashlib.sha256(f"input:{j}".encode()).digest() for j in range(circuit["inputs"])]
    values += [hashlib.sha256(b"const:0").digest(), hashlib.sha256(b"const:1").digest()]
    for a, b in circuit["gates"]:
        first, second = sorted((values[a], values[b]))
        values.append(hashlib.sha256(b"NAND" + first + second).digest())
    return values[circuit["output"]].hex()


def call_histogram(expr):
    hist = [0, 0, 0, 0]
    if expr[0] in ("input", "const"):
        return hist
    for child in expr[1:]:
        child_hist = call_histogram(child)
        hist = [a + b for a, b in zip(hist, child_hist)]
    if expr[0] == "FOLD":
        hist[sum(child[0] not in ("input", "const") for child in expr[1:])] += 1
    return hist


def source_scalar(tree, assignment):
    if type(tree) is int:
        ensure(0 <= tree < 9, "bad private source input")
        return (assignment >> tree) & 1
    ensure(isinstance(tree, (list, tuple)) and len(tree) == 4, "bad private source")
    op = tree[0]
    a, b, c = [source_scalar(child, assignment) for child in tree[1:]]
    if op == "F":
        return int((a and b) != bool(c))
    if op == "R-a":
        return int(bool(a) and (b != c))
    ensure(op == "R-b", "unknown private source operation")
    return int(bool(b) and (a != c))


def renamed_source(tree, permutation):
    if type(tree) is int:
        return permutation[tree]
    return [tree[0], *[renamed_source(child, permutation) for child in tree[1:]]]


def check_panel(panel, grades, prior_panel, prior_grades, earlier):
    ensure(len(panel) == 48 and len(grades) == 48, "wrong panel cardinality")
    ensure(len({row["id"] for row in panel}) == 48 and len({row["truth"] for row in panel}) == 48,
           "duplicate task identity/truth")
    ensure(set(grades) == {row["id"] for row in panel}, "grade/public mismatch")
    previous = {row["id"]: row for row in prior_panel}
    excluded = {row["truth"] for row in prior_panel}
    for rows in earlier:
        excluded.update(row["truth"] for row in rows if row["n"] == 9)
    ensure(len(excluded) == 84, "sealed exclusion population changed")
    pair_counts = Counter(grade["pair"] for grade in grades.values())
    ensure(len(pair_counts) == 24 and set(pair_counts.values()) == {2}, "wrong paired-unit count")
    ensure({grade["stage1_id"] for grade in grades.values()} == set(previous), "predecessor task mismatch")
    counts, scalar_rows, rename_rows = Counter(), 0, 0
    for row in panel:
        ensure(set(row) == {"id", "n", "truth"} and row["n"] == 9, "hint/private field entered public input")
        ensure(type(row["truth"]) is int and 0 <= row["truth"] < 1 << 512, "invalid public truth")
        ensure(row["truth"] not in excluded, "exact prior target reused")
        ensure(isinstance(row["id"], str) and len(row["id"]) == 32, "unexpected opaque ID")
        grade = grades[row["id"]]
        partner = grades[grade["partner"]]
        permutation = grade["permutation"]
        ensure(sorted(permutation) == list(range(9)), "invalid fresh permutation")
        ensure(partner["partner"] == row["id"] and partner["pair"] == grade["pair"], "asymmetric pair")
        ensure(partner["permutation"] == permutation and partner["depth"] == grade["depth"], "unmatched pair relabeling")
        ensure({partner["kind"], grade["kind"]} == {"positive", "negative"}, "pair is not matched positive/negative")
        old = previous[grade["stage1_id"]]
        old_grade = prior_grades[grade["stage1_id"]]
        ensure(old_grade["partner"] == partner["stage1_id"], "predecessor pair altered")
        ensure(renamed_source(old_grade["source"], permutation) == grade["source"], "source relabeling mismatch")
        ensure(old_grade["normalized_structure"] == grade["normalized_structure"], "structural novelty incorrectly changed")
        for x in range(512):
            target = (row["truth"] >> x) & 1
            ensure(source_scalar(grade["source"], x) == target, "private scalar source disagrees")
            scalar_rows += 1
            renamed = sum(((x >> j) & 1) << permutation[j] for j in range(9))
            ensure(((old["truth"] >> x) & 1) == ((row["truth"] >> renamed) & 1), "unmatched fresh truth labels")
            rename_rows += 1
        for j in range(9):
            ensure(any(((row["truth"] >> x) & 1) != ((row["truth"] >> (x ^ (1 << j))) & 1)
                       for x in range(512)), "target has irrelevant input")
        counts[grade["depth"], grade["kind"]] += 1
    ensure(counts == {(depth, kind): 8 for depth in (2, 3, 4) for kind in ("positive", "negative")}, "task strata changed")
    return {"tasks": 48, "matched_pairs": len({g["pair"] for g in grades.values()}),
            "private_source_scalar_rows": scalar_rows, "relabeling_rows": rename_rows,
            "excluded_prior_exact_truths": len(excluded), "exact_overlaps": 0,
            "new_structural_mechanisms_claimed": False,
            "strata": {f"{d}-{k}": v for (d, k), v in sorted(counts.items())}}


def check_work(work):
    ensure(isinstance(work, dict) and all(type(v) is int and v >= 0 for v in work.values()), "invalid work count")
    checked = 0
    for trials in work:
        if not trials.endswith("_trials"):
            continue
        prefix = trials[:-len("_trials")]
        passes, failures = prefix + "_passes", prefix + "_failures"
        if passes in work and failures in work:
            ensure(work[trials] == work[passes] + work[failures], "pass/fail identity: " + prefix)
            checked += 1
        requests, hits = prefix + "_requests", prefix + "_cache_hits"
        if requests in work and hits in work:
            ensure(work[requests] == work[trials] + work[hits], "request/cache identity: " + prefix)
            checked += 1
    if "ternary_placement_tests" in work:
        ensure(work["ternary_placement_tests"] == work.get("ternary_placement_passes", 0)
               + work.get("ternary_placement_failures", 0), "ternary pass/fail identity")
        checked += 1
    if "pair_requests" in work:
        ensure(work["pair_requests"] == work["pair_find_requests"] + work["pair_extension_probe_requests"],
               "pair request purpose mismatch")
        ensure(work["pair_extension_probe_requests"] == work["extension_trials"],
               "one pair request per uncached extension")
        ensure(work["pair_packed_shifts"] == 3 * work["pair_trials"]
               and work["pair_packed_masks"] == 4 * work["pair_trials"], "literal pair column work")
        ensure(3 * work["pair_passes"] + work["pair_failures"] <= work["pair_column_comparisons"]
               <= 4 * work["pair_trials"], "pair comparison count bounds")
        ensure(4 * work["pair_trials"] <= work["pair_cofactor_rows_equivalent"]
               <= 512 * work["pair_trials"], "pair logical row bounds")
        ensure(work["pair_quotient_requests"] == work["pair_quotient_builds"] + work["pair_quotient_cache_hits"],
               "pair quotient cache accounting")
        checked += 6
    return checked


def verify_program(result, target, binding, n=9):
    ensure(result.get("status") == "exact", "nonexact solver result")
    circuit = validate_circuit(result.get("circuit"), n)
    counts = inspect_ast(result.get("expr"), n)
    ensure(result.get("hint") is None and result.get("hint_status", "absent") == "absent", "hint used by blind method")
    ensure(result.get("truth") == target, "reported result truth mismatch")
    cost = 2 * counts["AND"] + 3 * counts["OR"] + 4 * counts["XOR"] + len(binding["gates"]) * counts["FOLD"]
    ensure(cost == len(circuit["gates"]) == result["expanded_NANDs"], "physical NAND count mismatch")
    ensure(counts["FOLD"] == result.get("macro_uses", 0), "literal macro count mismatch")
    work = result["work"]
    ensure(work.get("verification_rows") == 1 << n, "timed full-input verification missing")
    ensure(work.get("verification_packed_NANDs") == len(circuit["gates"]), "verification NAND work mismatch")
    ensure(work.get("verification_scalar_equivalent_NANDs") == len(circuit["gates"]) * (1 << n), "equivalent verification work mismatch")
    hist = result.get("template_computed_arg_histogram", [0, 0, 0, 0])
    tree = result.get("library_call_tree")
    if tree is not None:
        inspect_ast(tree, n)
        ensure(hist == call_histogram(tree), "computed-argument histogram mismatch")
        ensure(sum(hist) == result.get("template_uses", 0), "template count changed under substitution")
    for x in range(1 << n):
        expected = (target >> x) & 1
        ensure(nand_scalar(circuit, x) == expected, "independent NAND scalar replay failed")
        ensure(ast_scalar(result["expr"], x, binding) == expected, "independent AST scalar replay failed")
        if tree is not None:
            ensure(ast_scalar(tree, x, binding) == expected, "call-tree scalar replay failed")
    return dependency_digest(circuit), check_work(work)


def expected_cases():
    result = []
    for repeat in range(8):
        caches = ("warm", "cold") if repeat % 2 == 0 else ("cold", "warm")
        for cache in caches:
            if cache == "cold" and repeat > 1:
                continue
            for i in BLOCK:
                method = METHODS[(i + repeat + 4 * int(cache == "cold")) % 8]
                result.append((f"{cache}-{repeat}-{method}", cache, repeat, method))
    return result


def check_harness_arguments():
    tree = ast.parse((SOURCE / "job.py").read_text())
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Attribute) and node.func.attr == "solve"]
    ensure(len(calls) == 1 and len(calls[0].args) == 1 and not calls[0].keywords,
           "unexpected policy invocation")
    argument = calls[0].args[0]
    ensure(isinstance(argument, ast.Subscript) and isinstance(argument.value, ast.Name)
           and argument.value.id == "task" and isinstance(argument.slice, ast.Constant)
           and argument.slice.value == "truth", "private data passed to policy")
    return {"policy_arguments": ["truth"], "accounting_id_not_passed": True,
            "hints_not_passed": True}


def _semantic_work(work):
    excluded = ("physical_", "verification_", "archive_", "library_AST_", "library_binding_", "AST_")
    return {k: v for k, v in work.items() if not k.startswith(excluded)
            and not k.endswith(("_ns", "_inline_nodes"))}


def _summary(streams):
    methods = {"warm": {}, "cold": {}}
    for cache, repeats in (("warm", 8), ("cold", 2)):
        for method in METHODS:
            values = [streams[cache, method, repeat] for repeat in range(repeats)]
            methods[cache][method] = {
                name: median(v[name] for v in values)
                for name in ("paid_cpu_ns", "paid_wall_ns", "marginal_cpu_ns", "marginal_wall_ns",
                             "startup_cpu_ns", "startup_ns", "physical_nands")}
            keys = set().union(*(v["work"].keys() for v in values))
            methods[cache][method]["work"] = {k: median(v["work"].get(k, 0) for v in values) for k in sorted(keys)}
            methods[cache][method]["cpu_repeats_ns"] = [v["paid_cpu_ns"] for v in values]
            methods[cache][method]["wall_repeats_ns"] = [v["paid_wall_ns"] for v in values]
    warm = methods["warm"]
    baseline = min(("reference-primitive", "triple-primitive", "atomic-primitive"),
                   key=lambda m: warm[m]["paid_cpu_ns"])
    b = warm[baseline]
    comparisons = {}
    for method, value in warm.items():
        comparisons[method] = {
            "percent_cpu_saved": 100 * (1 - value["paid_cpu_ns"] / b["paid_cpu_ns"]),
            "paired_cpu_wins": sum(x < y for x, y in zip(value["cpu_repeats_ns"], b["cpu_repeats_ns"])),
            "paired_wall_wins": sum(x < y for x, y in zip(value["wall_repeats_ns"], b["wall_repeats_ns"])),
            "lower_wall": value["paid_wall_ns"] < b["paid_wall_ns"],
            "lower_marginal_cpu": value["marginal_cpu_ns"] < b["marginal_cpu_ns"],
        }
    primary = comparisons["guided-named"]
    gate = (primary["percent_cpu_saved"] >= 10 and primary["paired_cpu_wins"] >= 6
            and primary["lower_wall"] and primary["lower_marginal_cpu"]
            and comparisons["guided-flat"]["lower_marginal_cpu"])
    return {"benchmark": baseline, "fold_gate": bool(gate), "comparisons": comparisons, "methods": methods}


def audit(data_dir=DEFAULT):
    out = Path(data_dir)
    checker_self_test = self_test()
    design = read(out / "design.json")
    harness = check_harness_arguments()
    required = [SOURCE / name for name in ("job.py", "pair_solver.py", "bind.py", "contract.json")]
    required += [ROOT / name for name in (
        "experiments/FOLD-PLACEMENT-20261115-001/FOLD-PLACEMENT-20261115-001-E001_fixed_inputs/placement.py",
        "experiments/FOLD-DISCOVERY-20261115-001/FOLD-DISCOVERY-20261115-001-E001_learned_library/library_solver.py",
        "experiments/FOLD-DEPTH-20261115-001/FOLD-DEPTH-20261115-001-E001_supplied_fold/peel.py",
        "experiments/FOLD-DEPTH-20261115-001/FOLD-DEPTH-20261115-001-E001_supplied_fold/solver.py")]
    ensure(all(str(p.relative_to(ROOT)) in design["sources"] for p in required), "unbound solver dependency")
    digests = {}
    for name, wanted in design["sources"].items():
        ensure(sha(ROOT / name) == wanted, "bound source changed: " + name)
        digests[name] = wanted
    for name, wanted in design["data"].items():
        ensure(sha(out / name) == wanted, "bound data changed: " + name)
        digests[str((out / name).relative_to(ROOT))] = wanted
    ensure(sha(PRIOR / "design.json") == design["prior_design_sha256"], "prior design changed")
    ensure(sha(out / "given.json") == sha(PRIOR / "given.json"), "provided component changed")
    given = read(out / "given.json")
    ensure(set(given) == {"truth", "expr", "dag"}, "task-specific metadata in supplied component")
    binding = given["dag"]
    binding_circuit = validate_circuit({"inputs": 3, **binding}, 3)
    ensure(len(binding["gates"]) == 6, "wrong supplied physical component")
    inspect_ast(given["expr"], 3)
    for x in range(8):
        ensure(nand_scalar(binding_circuit, x) == ((given["truth"] >> x) & 1)
               == ast_scalar(given["expr"], x, binding), "supplied component mismatch")
    panel, grades = read(out / "panel.json"), read(out / "grades.json")
    prior_panel, prior_grades = read(PRIOR / "panel.json"), read(PRIOR / "grades.json")
    earlier = [read(ROOT / name) for name in (
        "artifacts/FOLD-DEPTH-20261115-001/FOLD-DEPTH-20261115-001-E001_supplied_fold/public.json",
        "artifacts/FOLD-DISCOVERY-20261115-001/FOLD-DISCOVERY-20261115-001-E001_learned_library/held.json")]
    population = check_panel(panel, grades, prior_panel, prior_grades, earlier)
    runner = read(out / "job.json")
    ensure(runner["workers"] == 1 and runner["max_cases_per_worker"] == 1 and runner["case_timeout"] == 120,
           "fresh sequential worker envelope changed")
    expected = expected_cases()
    receipts = [json.loads(line) for line in (out / "results.jsonl").read_text().splitlines()]
    ensure(len(receipts) == len(expected) == 80, "incomplete receipt set")
    ensure([r["case"] for r in receipts] == [r[0] for r in expected], "counterbalanced stream sequence changed")
    ensure(len({r["worker"] for r in receipts}) == 80, "worker reused across method streams")
    job_digest = design["sources"][str((SOURCE / "job.py").relative_to(ROOT))]
    ensure(runner["job_sha"] == job_digest, "runner job binding mismatch")
    streams, signatures, physical = {}, {}, {}
    all_work, setup_work, checks, scalar_rows, call_rows = Counter(), Counter(), 0, 0, 0
    affinities = set()
    for receipt, (case, cache, repeat, method) in zip(receipts, expected):
        ensure(receipt["status"] == "ok" and receipt["attempt"] == 1 and receipt["job_sha"] == job_digest,
               "failed/retried/unbound worker receipt")
        run = receipt["result"]
        ensure((run["cache"], run["repeat"], run["method"]) == (cache, repeat, method), "case payload mismatch")
        ensure(run["tasks"] == 48, "wrong stream task count")
        rawfile = out / run["file"]
        ensure(rawfile.parent == out and sha(rawfile) == run["sha256"], "raw stream file binding mismatch")
        digests[str(rawfile.relative_to(ROOT))] = run["sha256"]
        with gzip.open(rawfile, "rt") as handle:
            rows = [json.loads(line) for line in handle]
        ensure(len(rows) == 48, "truncated raw stream")
        affinities.add(run["affinity"])
        totals = Counter(startup_cpu_ns=run["startup_cpu_ns"], startup_ns=run["startup_ns"])
        stream_work = Counter()
        work_vector, dependency_vector = [], []
        previous_cache = None
        for index, (task, row) in enumerate(zip(panel, rows)):
            ensure(row["id"] == task["id"], "task order differs across methods")
            result = row["result"]
            digest, identities = verify_program(result, task["truth"], binding)
            checks += identities
            scalar_rows += 512
            if result.get("library_call_tree") is not None:
                call_rows += 512
            ensure(all(type(row[key]) is int and row[key] >= 0 for key in ("cpu_ns", "wall_ns", "init_ns", "return_bytes")),
                   "bad paid row cost")
            ensure(row["wall_ns"] >= row["init_ns"], "unpaid constructor")
            ensure(row["return_bytes"] == len(canonical(result["circuit"]).encode()), "physical serialization size differs")
            timing = result["timing"]
            ensure(all(timing[key] >= 0 for key in ("input_seconds", "search_seconds", "build_seconds", "verification_seconds", "search_cpu_ns")),
                   "negative phase timing")
            ensure(timing["search_cpu_ns"] <= row["cpu_ns"], "search CPU outside paid envelope")
            ensure(timing["elapsed_seconds"] * 1e9 <= row["wall_ns"] + 1_000_000, "solver wall outside paid envelope")
            work = result["work"]
            cache_before, cache_after = result["cache_before"], result["cache_after"]
            if cache == "cold" or index == 0:
                ensure(all(v == 0 for v in cache_before.values()), "search caches did not start empty")
            else:
                ensure(cache_before == previous_cache, "warm cache state was replaced or hidden")
            previous_cache = cache_after
            if "pair_requests" in work:
                ensure(result["pair_trace_dropped"] == work["pair_requests"] and not result["pair_trace"],
                       "unexpected/missing pair trace accounting")
                ensure(result["extension_trace_dropped"] == work["extension_requests"] and not result["extension_trace"],
                       "unexpected/missing extension trace accounting")
                for cache_name, work_name in (
                    ("pair_axis_masks", "pair_axis_masks_built"),
                    ("pair_group_masks", "pair_layout_masks_built"),
                    ("pair_certificates", "pair_trials"),
                    ("pair_quotients", "pair_quotient_builds"),
                    ("pair_extensions", "extension_trials"),
                ):
                    ensure(cache_after[cache_name] - cache_before[cache_name] == work[work_name],
                           "pair cache unit mismatch: " + cache_name)
                    checks += 1
            setup = result.get("library_setup")
            if method != "reference-primitive":
                ensure((setup is not None) == (cache == "cold" or index == 0), "constructor setup receipt missing/repeated")
                if setup is not None:
                    ensure(setup["cpu_ns"] <= row["cpu_ns"] and setup["seconds"] * 1e9 <= row["wall_ns"] + 1_000_000,
                           "constructor validation outside paid envelope")
                    setup_work.update(setup["work"])
            all_work.update(work)
            stream_work.update(work)
            totals.update(marginal_cpu_ns=row["cpu_ns"], marginal_wall_ns=row["wall_ns"],
                          physical_nands=len(result["circuit"]["gates"]))
            work_vector.append((_semantic_work(work), result.get("template_uses", 0),
                                result.get("template_computed_arg_histogram", [0, 0, 0, 0])))
            dependency_vector.append((digest, len(result["circuit"]["gates"])))
        totals["paid_cpu_ns"] = totals["startup_cpu_ns"] + totals["marginal_cpu_ns"]
        totals["paid_wall_ns"] = totals["startup_ns"] + totals["marginal_wall_ns"]
        ensure(totals["paid_wall_ns"] <= receipt["seconds"] * 1e9 + 2_000_000, "paid time exceeds runner wall")
        streams[cache, method, repeat] = {**totals, "work": dict(stream_work)}
        signatures[cache, method, repeat] = canonical(work_vector)
        physical[cache, method, repeat] = dependency_vector
    ensure(len(affinities) == 1, "CPU affinity differs across methods")
    for cache, repeats in (("warm", 8), ("cold", 2)):
        for method in METHODS:
            ensure(all(signatures[cache, method, i] == signatures[cache, method, 0] for i in range(repeats)),
                   "repeated deterministic work differs")
            if method.endswith("-named"):
                flat = method[:-len("named")] + "flat"
                for repeat in range(repeats):
                    ensure(signatures[cache, method, repeat] == signatures[cache, flat, repeat], "named/flat semantic work differs")
                    ensure(physical[cache, method, repeat] == physical[cache, flat, repeat], "named/flat physical dependencies differ")
    comparisons = _summary(streams)
    if (out / "result.json").exists():
        reported = read(out / "result.json")
        ensure(reported["benchmark"] == comparisons["benchmark"] and reported["fold_gate"] == comparisons["fold_gate"],
               "reported CPU gate differs from independent receipts")
        for method in METHODS:
            for key, value in comparisons["comparisons"][method].items():
                ensure(reported["comparisons"][method][key] == value, "reported comparison differs: " + method + "/" + key)
    rationales = {
        "scope_and_authority": "Exploratory bounded successor; source/data hashes and prior design match their sealed identities.",
        "information_leakage": "Engine receives truth only; public rows contain id/n/truth; no hints; given entry contains only truth/expr/dag.",
        "split_integrity": "48 unique labels exclude84 prior exact nine-input tables, with24 paired relabelings; mathematical structures intentionally reused.",
        "comparator_fairness": "Same labels/order, arm-local initially empty caches; within-stream warm reuse checked. Atomic fallback preserves valid pairs after failed extensions.",
        "artifact_and_checker": "Separate scalar AST/NAND interpreters replay all outputs and supplied entry; no producer/assessment imports.",
        "identifiability": "Question is prescribed pair location at fixed width, not discovering a new component or identifying new mathematical structures.",
        "resource_fairness": "80 fresh one-case worker PIDs, one configured worker, common CPU affinity; paid process/wall receipts recomputed with disclosed exclusions.",
        "statistical_validity": "Eight warm counterbalanced timing blocks and two cold blocks; fixed candidate and strongest predeclared no-library baseline; no retrospective task/repeat selection.",
        "representation_robustness": "Fresh paired input renamings checked on all512 original assignments; no extrapolation beyond these representations.",
        "causal_alternatives": "Guided primitive reconstruction and equal-search inline controls retained; no claim separates semantic guidance from a shared locator improvement.",
        "independent_replay": "All3840 saved outputs independently scalar-replayed; failed-trial counters checked by receipt identities, not a hidden solver rerun.",
        "adversarial_mutation": "Synthetic forward NAND address, malformed AST input and false pass/fail receipt are rejected; hash mismatches and hidden argument paths are guarded.",
        "claim_scope": "Supplied component is free, task mathematics reused, CPU results host-specific; later selection/acquisition remains separately paid.",
    }
    categories = {key: {"status": "pass", "rationale": value} for key, value in rationales.items()}
    return {
        "schema_version": 1, "ticket": TICKET, "verdict": "PASS", "categories": categories,
        "design_sha256": sha(out / "design.json"), "audit_source_sha256": sha(Path(__file__)),
        "input_digests": digests, "population": population, "harness": harness,
        "checker_self_test": checker_self_test,
        "replay": {"streams": 80, "programs": 3840, "physical_scalar_rows": scalar_rows,
                   "AST_scalar_rows": scalar_rows, "call_tree_scalar_rows": call_rows,
                   "counter_identities": checks, "affinity": next(iter(affinities)),
                   "reported_work_totals": dict(all_work), "paid_setup_work_totals": dict(setup_work)},
        "comparison": comparisons,
        "timing_boundary": "Method import/library parsing, construction, solve and circuit JSON; excludes common scientific binding/hash checks, affinity, runner and trace output. Source bytes OS-warmed by common hashing.",
        "independence": "Standalone scalar AST/NAND checker imports no producer, generator or assessment. Reviewer authored a base-solver predecessor; a separate read-only helper checked pre-outcome methodology.",
        "limits": ["No solver or search reruns. Failed search tests are receipt reaggregation/identity checks, not independent replay of unlogged rejected proposals.",
                   "Pair and extension counters are nested: each fresh extension invokes one pair request, which may hit its cache. They are reported separately, not summed as independent work.",
                   "Named/flat semantic-placement equality excludes AST construction/remapping and inline-lowering work. Flat's expanded AST can require more remapping; all such work remains in returned counters and paid CPU/wall totals.",
                   "Fresh exact labels reuse the predecessor mathematics up to input permutation; no new-structure transfer claim.",
                   "Eight timing repeats measure this host/workload, not independent scientific mechanisms.",
                   "Given component is free in this locator diagnostic; acquisition and paid selection remain separate."],
    }


def self_test():
    circuit = {"inputs": 2, "gates": [[0, 1], [4, 4]], "output": 5}
    validate_circuit(circuit, 2)
    ensure([nand_scalar(circuit, x) for x in range(4)] == [0, 0, 0, 1], "hand AND fixture")
    expr = ["AND", ["input", 0], ["input", 1]]
    inspect_ast(expr, 2)
    ensure([ast_scalar(expr, x, {}) for x in range(4)] == [0, 0, 0, 1], "hand AST fixture")
    rejected = 0
    for action in (
        lambda: validate_circuit({"inputs": 2, "gates": [[0, 4]], "output": 4}, 2),
        lambda: inspect_ast(["input", 0.2], 2),
        lambda: check_work({"binary_placement_trials": 2, "binary_placement_passes": 1,
                            "binary_placement_failures": 0}),
    ):
        try:
            action()
        except ValueError:
            rejected += 1
    ensure(rejected == 3, "mutation fixture accepted")
    cases = expected_cases()
    ensure(len(cases) == len(set(case for case, *_ in cases)) == 80, "case count fixture")
    for position in range(8):
        methods = [method for _, cache, _, method in cases if cache == "warm"]
        ensure(len({methods[position + 8 * repeat] for repeat in range(8)}) == 8, "warm Latin order fixture")
    return {"synthetic_only": True, "status": "passed", "corruptions_rejected": rejected}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(canonical(self_test()))
    elif args.audit:
        report = audit()
        destination = DEFAULT / "audit.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(canonical({"verdict": report["verdict"], "replay": {k: v for k, v in report["replay"].items()
              if k != "reported_work_totals"}, "benchmark": report["comparison"]["benchmark"],
              "fold_gate": report["comparison"]["fold_gate"]}))
    else:
        parser.error("use --self-test or --audit; this module never runs a solver")
