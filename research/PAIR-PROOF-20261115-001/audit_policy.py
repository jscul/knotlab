#!/usr/bin/env python3
"""Independent E002 audit.  Held reads require the supervisor's recorded freeze.

No producer/checker is imported for correctness: a hash-pinned, terminal
independent oracle enumerates literal stage assignments and replays the raw
NAND return.  Timing is read from paid receipts, never remeasured here.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from datetime import datetime
from functools import lru_cache
import gzip
import hashlib
import importlib.util
from itertools import combinations
import json
from pathlib import Path
from statistics import median
import sys


ROOT = Path(__file__).resolve().parents[2]
TICKET = "PAIR-PROOF-20261115-001"
FAMILY = TICKET + "-E002_local_policy"
SOURCE = ROOT / "experiments" / TICKET / FAMILY
DEFAULT = ROOT / "artifacts" / TICKET / FAMILY
PRIOR = ROOT / "artifacts/PARENT-FOLD-20261115-001/PARENT-FOLD-20261115-001-E001_consumer_edits/explicit-piece"
INDEPENDENT = ROOT / "research/PARENT-FOLD-20261115-001/audit.py"
INDEPENDENT_SHA256 = "4ca6901f79b85cb5dd1f8ebdb9a2d5a5b99416377f32aa7a4de52d8efd3dc90a"
FIELDS = ("n", "upstream_count", "gates", "frontier", "outputs", "pieces")
EDIT_FIELDS = ("gate", "pin", "to")
MODES = ("ordinary", "compact", "no-proof", "balanced", "fixed", "same-menu", "learned")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_bytes())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def path(value):
    result = (ROOT / value).resolve()
    require(result.is_relative_to(ROOT), "bound path escapes this research repository")
    return result


@lru_cache(maxsize=1)
def independent():
    require(digest(INDEPENDENT) == INDEPENDENT_SHA256, "terminal independent certificate auditor changed")
    spec = importlib.util.spec_from_file_location("_independent_e002_ancestor", INDEPENDENT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_evidence(case, grade=None, *, exact=True):
    p = independent()
    require(set(case) == {"id", *FIELDS, "edits"}, "public case mixes private metadata")
    n, m = case["n"], len(case["frontier"])
    require(n == m + 2 and len(case["edits"]) == 2, "parent dimensions or edit count")
    original_raw, original_stage = p.raw_words(case), p.stage_words(case)
    mapping, multiplicity = p.frontier_domain(case, original_raw)
    require(multiplicity == {4: 1 << m}, "frontier preimage multiplicity")
    p.project_source(case, original_raw, original_stage, mapping)
    for piece in case["pieces"]:
        group = tuple(piece["inputs"])
        require(group == tuple(sorted(set(group))) and len(group) == 3, "historical group")
        require(p.oracle().support(m, original_stage[piece["bit"]]) == group, "historical bit support")
        ports = tuple(original_stage[w] for w in piece["ports"])
        retained = p.old_bit_retention(m, ports, group, original_stage[piece["bit"]])
        require(retained["old_bit_sufficient"], "historical ports do not factor through their bit")
    snapshots, families = {}, []
    for edit in (None, *case["edits"]):
        eid = None if edit is None else edit["id"]
        raw = original_raw if edit is None else p.raw_words(case, edit)
        stage = original_stage if edit is None else p.stage_words(case, edit)
        p.project_source(case, raw, stage, mapping)
        targets = tuple(stage[w] for w in case["outputs"])
        facts = p.oracle().characterize(m, targets) if exact else None
        if exact:
            require(facts["common_essential"] == tuple(range(m)), "a fixture output drops a stage input")
        snapshot = dict(raw=raw, stage=stage, targets=targets, facts=facts)
        if edit is not None:
            snapshot["cone_stage"] = p.changed_cone(case, edit, original_stage, stage)
            require(snapshot["cone_stage"] == p.changed_cone(case, edit, original_raw, raw), "raw/stage changed cone")
        snapshots[eid] = snapshot
        families.append(p.prior().raw_family(m, targets))
        if grade is not None and exact:
            saved = grade["base"] if eid is None else grade["edits"][eid]
            require(list(targets) == saved["outputs"], "saved source output grade differs")
            require([count for _, count in facts["ranks"]] == saved["candidate_classes"], "saved global class labels differ")
            require(facts["minimum_bits"] == saved["width"], "saved global width differs")
    if grade is not None:
        require(set(grade["edit_ids"]) == set(snapshots) - {None}, "grade edit identities differ")
        families = [p.prior().raw_family(m, snapshots[eid]["targets"]) for eid in (None, *grade["edit_ids"])]
        require(families == grade["truth_families"], "declared raw truth families differ")
        structure = p.context_family(case, grade)
        require(structure == grade["structure"], "declared downstream family differs")
    else:
        structure = None
    return dict(before_raw=original_raw, before_stage=original_stage,
                raw_to_stage=mapping, snapshots=snapshots, family_keys=families,
                structure=structure, prefix_multiplicity=multiplicity)


def physical_family(case, edit=None):
    """Independent coarse graph invariant, insensitive to raw/gate naming."""
    n = case["n"]
    stamps = [b"R"] * n + [b"F", b"T"]
    gates = independent().edited_gates(case, edit)
    for a, b in gates:
        children = sorted((stamps[a], stamps[b]))
        stamps.append(hashlib.sha256(b"N" + b"".join(v.ljust(32, b"\0") for v in children)).digest())
    def series(indices):
        return b"".join(sorted(stamps[i] for i in indices))
    first = n + 2
    stop = first + case["upstream_count"]
    data = b"|".join((str(n).encode(), series(range(first, stop)), series(range(stop, len(stamps))),
                        series(case["frontier"]), series(case["outputs"])))
    return hashlib.sha256(data).hexdigest()


def inspect_split(directory, *, domain, exact=False):
    public, grades = load(directory / "public.json"), load(directory / "grades.json")
    require(len(public) == len(grades) == 36, "split must have 36 parents")
    families = {key: set() for key in ("physical", "downstream", "truth", "parent_ids", "edit_ids")}
    cells = Counter()
    evidence = {}
    seeds, sizes = set(), set()
    for case in public:
        pid = case["id"]
        require(pid not in evidence and pid in grades, "duplicate or unknown parent")
        grade = grades[pid]
        ev = source_evidence(case, grade, exact=exact)
        evidence[pid] = ev
        m = len(case["frontier"])
        require(grade["m"] == m, "grade stage arity")
        seeds.add(grade["seed"])
        sizes.add(m)
        cells[m, grade["seed"], grade["operation"], grade["stratum"]] += 1
        require(int(ev["structure"][:8], 16) % 3 == domain, "downstream split domain")
        require(all(int(k[:8], 16) % 3 == domain for k in ev["family_keys"]), "truth split domain")
        families["downstream"].add(ev["structure"])
        families["truth"].update(ev["family_keys"])
        families["physical"].update(physical_family(case, edit) for edit in (None, *case["edits"]))
        families["parent_ids"].add(pid)
        families["edit_ids"].update(edit["id"] for edit in case["edits"])
    expected = {(m, seed, op, kind) for m in sizes for seed in seeds
                for op in ("fold", "mux") for kind in ("direct", "masked")}
    require(len(seeds) == len(sizes) == 3 and set(cells) == expected and set(cells.values()) == {1}, "seed/size/structure balance")
    require(len(families["parent_ids"]) == 36 and len(families["edit_ids"]) == 72
            and len(families["downstream"]) == 36 and len(families["truth"]) == 108, "distinct split families")
    return public, grades, evidence, families, dict(seeds=sorted(seeds), frontier_sizes=sorted(sizes),
        parents=36, edits=72, fingerprint_domain=domain,
        family_counts={key: len(value) for key, value in families.items()})


def bindings(directory, recorded_freeze):
    # This is the first artifact read.  No held data is opened until the
    # explicit supervisor-provided freeze matches its complete byte digest.
    require(len(recorded_freeze) == 64 and digest(directory / "freeze.json") == recorded_freeze,
            "recorded pre-blind freeze is required")
    freeze = load(directory / "freeze.json")
    for name, expected in freeze["sources_and_inputs"].items():
        require(digest(path(name)) == expected, "changed frozen training source/input " + name)
    require(digest(directory / "model.json") == freeze["model_sha256"], "changed model")
    design = load(directory / "design.json")
    for collection in ("sources", "data"):
        for name, expected in design[collection].items():
            require(digest(path(name)) == expected, "changed bound " + collection + " " + name)
    require(path(design["model"]) == directory / "model.json", "benchmark model differs from freeze")
    origins = {split: load(directory / split / "origin.json") for split in ("train", "blind")}
    for split, origin in origins.items():
        require(origin["split"] == split, "wrong origin scope")
        for name, expected in origin["files"].items():
            require(digest(directory / split / name) == expected, "changed generated split file")
        require(origin["worker_cpu_ns"] == origin["worker_user_cpu_ns"] + origin["worker_system_cpu_ns"], "generator worker CPU sum")
        require(origin["cpu_ns"] == origin["worker_cpu_ns"] + origin["supervisor_cpu_ns_to_receipt"], "generator total CPU sum")
    held_model = origins["blind"]["model"]
    require(held_model["sha256"] == freeze["model_sha256"] and path(held_model["file"]) == directory / "model.json", "blind not bound to frozen model")
    require(held_model["training_origin_sha256"] == digest(directory / "train/origin.json"), "blind training-origin binding")
    frozen_ns = int(datetime.fromisoformat(freeze["frozen_utc"]).timestamp() * 1e9)
    require(frozen_ns <= origins["blind"]["generation_start_unix_ns"], "blind generation predates model freeze")
    cost = load(directory / "training-cost.json")
    require(cost["returncode"] == 0 and cost["freeze_sha256"] == recorded_freeze
            and cost["model_sha256"] == freeze["model_sha256"], "complete training receipt binding")
    require(cost["cpu_ns"] == cost["child_cpu_ns"] + cost["supervisor_ns_to_receipt"], "full training debit sum")
    require(0 <= freeze["fit_cpu_ns"] <= freeze["train_process_cpu_ns"] <= cost["child_cpu_ns"], "training CPU containment")
    require((directory / "training-cost.json").stat().st_mtime_ns <= origins["blind"]["generation_start_unix_ns"], "blind predates completed training charge")
    failed = load(directory / "failed-fits.json") if (directory / "failed-fits.json").exists() else []
    debit = origins["train"]["cpu_ns"] + cost["cpu_ns"] + sum(row["cpu_ns"] for row in failed)
    return design, freeze, origins, dict(training_generation_cpu_ns=origins["train"]["cpu_ns"],
        complete_fit_process_cpu_ns=cost["cpu_ns"], failed_fit_cpu_ns=sum(row["cpu_ns"] for row in failed),
        total_training_debit_cpu_ns=debit, failed_fits=len(failed),
        scope="Generation, labels, fit, selection and model delivery; one full debit per prospective held horizon.")


def _policy_module():
    spec = importlib.util.spec_from_file_location("_e002_policy_leakage_replay", SOURCE / "local_policy.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def policy_replay(directory, freeze, train_cases):
    """Re-derive the frozen fit using train only; inspect inference call graph."""
    filename = SOURCE / "local_policy.py"
    require(digest(filename) == freeze["sources_and_inputs"][str(filename.relative_to(ROOT))], "policy differs from training freeze")
    tree = ast.parse(filename.read_bytes())
    definitions = {node.name: node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    reached, pending = set(), ["propose", "fixed_actions"]
    while pending:
        name = pending.pop()
        if name in reached:
            continue
        reached.add(name)
        node = definitions[name]
        calls = {child.func.id for child in ast.walk(node) if isinstance(child, ast.Call) and isinstance(child.func, ast.Name)}
        pending += list((calls & definitions.keys()) - reached)
        require(not calls & {"open", "eval", "exec", "__import__", "Path", "load"}, "inference call graph includes I/O or code evaluation")
        keys = {child.slice.value for child in ast.walk(node) if isinstance(child, ast.Subscript)
                and isinstance(child.slice, ast.Constant) and isinstance(child.slice.value, str)}
        require(not keys & {"tables", "grades", "role", "id", "seed", "edits", "hint", "anchor"}, "forbidden inference field")
    require(not reached & {"fit", "_train_engine", "_training_trial", "_label", "_lookup"}, "inference reaches training labels")
    policy = _policy_module()
    saved, selection = load(directory / "model.json"), load(directory / "training-selection.json")
    require(set(saved) == {"schema", "radius", "split", "plan", "recipes"}, "model contains non-policy data")
    require(saved["radius"] in (0, 1, 2, 4), "selected radius outside offered training grid")
    require(selection["parent_block_edit_counts"] == [2] * 36 and selection["trained_parents"] == 36
            and selection["trained_edits"] == 72, "training leaves sibling edits in different blocks")
    stripped = [{**{key: case[key] for key in FIELDS},
                 "edits": [{key: edit[key] for key in EDIT_FIELDS} for edit in case["edits"]]}
                for case in train_cases]
    guard = {"stage": "fit"}
    denied = []
    held = (directory / "blind").resolve()
    def audit_io(event, args):
        if event != "open" or not guard["stage"] or not args or not isinstance(args[0], (str, bytes)):
            return
        opened = Path(args[0]).resolve()
        if guard["stage"] == "inference" or opened.is_relative_to(held):
            denied.append(str(opened))
            raise ValueError("policy attempted forbidden I/O during " + guard["stage"])
    sys.addaudithook(audit_io)
    try:
        fitted, replay_selection = policy.fit(stripped, radii=(0, 1, 2, 4))
    finally:
        guard["stage"] = None
    require(canonical(fitted) == canonical(saved) and canonical(replay_selection) == canonical(selection),
            "frozen fit/selection is not reproduced from train-only inputs")
    require(hashlib.sha256(canonical(saved)).hexdigest() == selection["model_sha256_canonical"], "canonical model selection binding")
    updates = selection["recipe_updates"]
    require(any(row["changed_from_fixed_primary"] > 0 and row["supervised_pair_examples"] > 0 for row in updates), "no recorded fitted update")
    info = dict(train_only_fit_exact_replay=True, training_parents=36, training_edits=72,
                whole_parent_validation=True, selected_radius=saved["radius"], selected_plan=saved["plan"],
                selected_two_bit_proxy_units=selection["selected_two_bit_units"],
                selected_mixed_proxy_units=selection["selected_mixed_units"],
                inference_reachable_functions=sorted(reached), forbidden_io_attempts=denied,
                producer_import_scope="Policy fitting/provenance only; mathematical correctness uses independent terminal oracle.")
    return policy, saved, guard, info


def proof_facts(case, snapshot, answer, evidence):
    proofs = answer.get("pair_proofs", ())
    counts = Counter(pair_proofs_supplied=len(proofs))
    require(isinstance(proofs, (tuple, list)), "proof collection shape")
    m = len(case["frontier"])
    if answer["width"] != 2:
        require(not proofs, "unused proof returned outside two-bit scope")
        return dict(counts), set()
    witnesses = {}
    for raw, stage in enumerate(evidence["raw_to_stage"]):
        witnesses.setdefault(stage, raw)
    raw_targets = tuple(snapshot["raw"][w] for w in case["outputs"])
    seen, cache, pairs = set(), {}, set()
    for request in proofs:
        require(isinstance(request, (tuple, list)) and len(request) in (3, 4)
                and all(type(v) is int for v in request), "proof request shape")
        a, b, base = request[:3]
        mask = request[3] if len(request) == 4 else 15
        require(0 <= a < b < m and 0 <= base < 1 << m and base & ((1 << a) | (1 << b)) == 0
                and mask in (7, 11, 13, 14, 15), "proof axes/outside/corners")
        key = (a, b, base, mask)
        if key in seen:
            counts["pair_proof_duplicate_certificates"] += 1
            continue
        seen.add(key)
        counts["pair_proof_unique_certificates_checked"] += 1
        values = []
        for corner in range(4):
            if not mask >> corner & 1:
                continue
            row = base | ((corner & 1) << a) | ((corner >> 1) << b)
            counts["pair_proof_row_requests"] += 1
            if row in cache:
                counts["pair_proof_row_cache_hits"] += 1
            else:
                actual = witnesses[row]
                cache[row] = tuple((truth >> actual) & 1 for truth in raw_targets)
                require(cache[row] == tuple((truth >> row) & 1 for truth in snapshot["targets"]), "current raw proof response differs from stage response")
                counts["pair_proof_raw_rows_read"] += 1
                counts["pair_proof_output_bits_read"] += 2
            values.append(cache[row])
        counts["pair_proof_certificate_row_requests"] += len(values)
        valid = len(set(values)) >= 3
        counts["pair_proof_successes" if valid else "pair_proof_current_data_failures"] += 1
        if valid:
            pairs.add((a, b))
    covered = {group for group, _ in snapshot["facts"]["ranks"] if any(set(pair) <= set(group) for pair in pairs)}
    counts["pair_proof_certified_axis_pairs"] = len(pairs)
    counts["pair_proof_distinct_rows"] = len(cache)
    return dict(counts), covered


def check_receipt(case, snapshot, evidence, answer, check, exact, raw, proof_counts, covered):
    p = independent()
    n, m, prefix = case["n"], len(case["frontier"]), case["upstream_count"]
    gates = len(answer["circuit"]["gates"])
    omitted = len(covered - {tuple(sorted(answer["triple"]))}) if answer["width"] == 2 else 0
    alternatives = exact["alternatives_checked"]
    expected = dict(exact=True, width=exact["width"], classes=exact["classes"],
        minimum_universe="jointly-essential stage-frontier triples", structural_locality=True,
        raw_assignments=1 << n, stage_assignments=1 << m, raw_outputs=2,
        raw_gates_returned=len(answer["physical"]["gates"]), stage_gates_returned=gates,
        active_stage_gates=exact["active_gates"], shared_stage_gates=exact["shared_gates"],
        shared_summary_wires=exact["shared_summary_wires"], raw_return_replay="history",
        source_sha256=hashlib.sha256(canonical(case)).hexdigest(), verification_calls=1,
        physical_prefix_gates_compared=prefix, physical_stage_gates_linked=gates,
        returned_stage_NAND_evaluations=gates, returned_stage_output_bits_compared=2 << m,
        global_minimum_alternative_groups_checked=alternatives - omitted,
        raw_return_prefix_NANDs_reused=prefix, raw_return_output_bits_compared=2 << n,
        stage_support_axis_tests=2 * m, stage_class_calls=1 + alternatives - omitted,
        original_verification_cache_hits=0)
    cone = snapshot["cone_stage"]
    for label in ("raw_source", "source_stage"):
        expected.update({label + "_gates_examined": cone["examined"], label + "_NAND_evaluations": cone["recomputed"],
            label + ("_unchanged_NANDs_reused" if label == "raw_source" else "_NANDs_reused"): cone["reused"],
            label + "_changed_values": cone["changed"], label + "_recomputed_unchanged_values": cone["recomputed_unchanged"]})
    expected.update(raw_source_prefix_NANDs_reused=prefix, raw_source_NAND_row_equivalents=cone["recomputed"] * (1 << n),
                    raw_stage_projection_tests=2 << m, raw_stage_output_bits_covered=2 << n)
    original_ids = p._source_fingerprints(case)
    history = {identity: evidence["before_raw"][wire] for wire, identity in enumerate(original_ids) if wire >= n + 2}
    returned_ids = p.oracle().circuit_shape(answer["physical"], n)[3]
    hits, new = 0, set()
    for wire in range(n + 2 + prefix, len(returned_ids)):
        key = returned_ids[wire]
        if key in history:
            require(raw[wire] == history[key], "stale raw expression cache value")
            hits += 1
        else:
            new.add(key)
    expected.update(raw_return_history_expression_lookups=gates, raw_return_history_expression_hits=hits,
        raw_return_history_expression_misses=gates - hits, raw_return_new_expression_identities=len(new),
        raw_return_NANDs_reused=prefix + hits, raw_return_NAND_evaluations=gates - hits,
        raw_return_NAND_row_equivalents=(gates - hits) * (1 << n))
    for name, value in expected.items():
        require(check.get(name, 0) == value, "checker counter/assertion " + name)
    if "pair_no_proof_fast_path" in check:
        proof_names = {"pair_proofs_supplied", "pair_proof_schema_failures", "pair_proof_duplicate_certificates",
            "pair_proof_unique_certificates_checked", "pair_proof_row_requests", "pair_proof_row_cache_hits",
            "pair_proof_raw_rows_read", "pair_proof_output_bits_read", "pair_proof_certificate_row_requests",
            "pair_proof_successes", "pair_proof_current_data_failures", "pair_proof_certified_axis_pairs", "pair_proof_distinct_rows"}
        for name in proof_names:
            value = proof_counts.get(name, 0)
            require(check.get(name, 0) == value, "literal current proof count " + name)
        for name, value in dict(alternative_exact_checks_avoided=omitted,
                                alternative_exact_checks_actual=alternatives - omitted,
                                chosen_group_exact_checks=1, alternative_groups_considered=alternatives,
                                global_minimum_alternative_groups_certified=alternatives).items():
            require(check.get(name, 0) == value, "independent fallback obligation " + name)
    require(check["verification_remainder_cpu_ns"] == check["verification_cpu_ns"] - check["minimum_phase_cpu_ns"]
            if "minimum_phase_cpu_ns" in check else True, "verification phase subtraction")
    if "minimum_phase_cpu_ns" in check:
        require(check.get("optimistic_no_minimum_is_certified") is False
                and check.get("optimistic_no_alternative_is_certified") is False, "optimistic floor promoted to certificate")
        require(check.get("alternative_checks_cpu_ns", 0) <= check["minimum_phase_cpu_ns"], "nested alternative timer")
    return omitted


def audit_all(directory, recorded_freeze):
    design, freeze, origins, training_bill = bindings(directory, recorded_freeze)
    p = independent()
    audit_cpu = p.pin_away_from_timing()
    old_public, old_grade, _, old_families, old_info = inspect_split(PRIOR, domain=0, exact=False)
    train, train_grades, _, train_families, train_info = inspect_split(directory / "train", domain=1, exact=False)
    held, grades, evidence, held_families, held_info = inspect_split(directory / "blind", domain=2, exact=True)
    require(train_info["seeds"] == [245261, 245269, 245279] and held_info["seeds"] == [281219, 281227, 281233], "frozen seed plans differ")
    require(train_info["frontier_sizes"] == held_info["frontier_sizes"] == [8, 9, 10], "held/train sizes")
    for earlier, later in ((old_info, train_info), (old_info, held_info), (train_info, held_info)):
        require(set(earlier["seeds"]).isdisjoint(later["seeds"]), "seed sets overlap")
    intersections = {}
    for earlier, first, later, second in (("E001", old_families, "train", train_families),
                                          ("E001", old_families, "blind", held_families),
                                          ("train", train_families, "blind", held_families)):
        overlap = {name: len(first[name] & second[name]) for name in first}
        require(not any(overlap.values()), "cross-split family or identity collision")
        intersections[earlier + "/" + later] = overlap
    for split, info in (("train", train_info), ("blind", held_info)):
        require(origins[split]["families"] == info["family_counts"], "origin family counts differ")
        require(origins[split]["seeds"] == info["seeds"], "origin seed count differs")
        for name, value in origins[split]["generator_dependencies"].items():
            require(digest(path(name)) == value, "generator prerequisite changed")
    policy, model, io_guard, fitting = policy_replay(directory, freeze, train)
    frozen_model = canonical(model)
    claimed = load(directory / "result.json")
    broken = load(directory / "broken.json")
    actual_cases = {case["id"]: case for case in held}
    known = {(case["id"], edit["id"]): evidence[case["id"]]["snapshots"][edit["id"]]
             for case in held for edit in case["edits"]}
    for case in held:
        two = [edit["id"] for edit in case["edits"] if known[case["id"], edit["id"]]["facts"]["minimum_bits"] == 2]
        require(two == [broken[case["id"]]], "harness two-bit membership differs from exact global minima")
    physical_cache, proof_cache, ledger_cache, action_cache = {}, {}, {}, {}
    totals = Counter()
    runs, counts, seeded = {}, defaultdict(lambda: defaultdict(Counter)), defaultdict(Counter)
    named = {f"{pid}/{eid}": {"seed": grades[pid]["seed"], "width": info["facts"]["minimum_bits"], "methods": {}}
             for (pid, eid), info in known.items()}
    outer_rows = [json.loads(line) for line in (directory / "results.jsonl").read_bytes().splitlines()]
    for outer in outer_rows:
        require(outer["status"] == "ok", "failed primary deployment")
        envelope = outer["result"]
        panel, arm, block = (envelope[key] for key in ("panel", "arm", "block"))
        require(panel in ("broken", "mixed") and arm in design["arms"] and block in range(8), "unfrozen stream identity")
        key = panel, arm, block
        require(key not in runs and outer["case"] == f"{panel}-{block}-{arm}", "duplicate or misnamed primary stream")
        require(envelope["mode"] == design["arms"][arm]["mode"] and envelope["model_sha256"] == freeze["model_sha256"], "stream model/method binding")
        require(outer["job_sha"] == design["sources"][str((SOURCE / "job.py").relative_to(ROOT))], "stream harness binding")
        filename = directory / envelope["file"]
        require(digest(filename) == envelope["sha256"], "changed held trace")
        with gzip.open(filename, "rt") as handle:
            rows = [json.loads(line) for line in handle]
        require(len(rows) == envelope["parents"] == envelope["public_parents"] == 36 and envelope["failures"] == 0, "incomplete parent deployment")
        expected_cases = held if block % 2 == 0 else held[::-1]
        require([row["id"] for row in rows] == [case["id"] for case in expected_cases], "unpaired parent order")
        expected_tasks = {(pid, eid) for pid, eid in known if panel == "mixed" or broken[pid] == eid}
        observed, order, step_costs = set(), [], []
        phases, seed_times, correct, proof_seed = Counter(startup=envelope["startup_ns"]), Counter(), Counter(), Counter()
        require(sum(envelope["startup_phases"].values()) <= envelope["startup_ns"], "startup phase containment")
        require(("model_load" in envelope["startup_phases"]) == (arm == "learned"), "model loading debit/scope")
        for row, case in zip(rows, expected_cases, strict=True):
            pid, ev = case["id"], evidence[case["id"]]
            require(row["failure"] is None, "parent failure")
            require(all(type(v) is int and v >= 0 for v in row["phases"].values()), "parent phase type")
            prepared = sum(row["phases"].values())
            require(prepared + sum(query["cpu_ns"] for query in row["edits"]) <= row["cpu_ns"], "parent CPU containment")
            phases.update(row["phases"])
            seed = str(grades[pid]["seed"])
            seed_times[seed] += row["cpu_ns"]
            position = len(step_costs)
            originals = {name: case[name] for name in FIELDS}
            expected_edits = case["edits"] if block % 2 == 0 else case["edits"][::-1]
            expected_edits = [edit for edit in expected_edits if panel == "mixed" or edit["id"] == broken[pid]]
            require([q["id"] for q in row["edits"]] == [edit["id"] for edit in expected_edits], "unpaired sibling order")
            for query, edit in zip(row["edits"], expected_edits, strict=True):
                eid, snapshot = edit["id"], known[pid, edit["id"]]
                require((pid, eid) not in observed and (pid, eid) in expected_tasks, "duplicate/extra held task")
                observed.add((pid, eid)); order.append((pid, eid))
                require(query["failure"] is None and query["answer"], "held return failed")
                require(all(type(value) is int and value >= 0 for value in query["phases"].values())
                        and sum(query["phases"].values()) <= query["cpu_ns"], "edit CPU containment")
                require(("propose" in query["phases"]) == (arm in ("learned", "same-menu")), "upfront proposal missing or charged to wrong arm")
                if arm in ("learned", "same-menu"):
                    action_key = arm, pid, eid
                    if action_key not in action_cache:
                        stripped_edit = {name: edit[name] for name in EDIT_FIELDS}
                        io_guard["stage"] = "inference"
                        try:
                            actions = policy.propose(model, originals, stripped_edit) if arm == "learned" else policy.fixed_actions(originals, stripped_edit)
                        finally:
                            io_guard["stage"] = None
                        require(canonical(model) == frozen_model, "inference mutated frozen parameters")
                        action_cache[action_key] = actions
                    require(query["actions"] == action_cache[action_key] and query["proposed_actions"] == len(query["actions"]), "requests differ from immutable local-only policy")
                answer = query["answer"]
                body = {name: value for name, value in answer.items() if name != "pair_proofs"}
                program = hashlib.sha256(canonical(body)).hexdigest()
                physical_key = pid, eid, program
                if physical_key not in physical_cache:
                    p.check_lift(case, answer)
                    exact, _ = p.oracle().verify_result(len(case["frontier"]), snapshot["targets"], answer)
                    raw = p.physical_words(answer["physical"])
                    require(tuple(raw[wire] for wire in answer["physical"]["outputs"]) == tuple(snapshot["raw"][wire] for wire in case["outputs"]), "wrong actual raw-input NAND output")
                    physical_cache[physical_key] = exact, raw
                    totals["executed_unique_programs"] += 1
                    totals["executed_unique_raw_rows"] += 1 << case["n"]
                    totals["executed_unique_stage_rows"] += 1 << len(case["frontier"])
                exact, raw = physical_cache[physical_key]
                proof_key = pid, eid, hashlib.sha256(canonical(answer.get("pair_proofs", []))).hexdigest()
                if proof_key not in proof_cache:
                    proof_cache[proof_key] = proof_facts(case, snapshot, answer, ev)
                proof_counts, covered = proof_cache[proof_key]
                ledger = physical_key, proof_key, arm
                stable = {name: value for name, value in query["check"].items()
                          if not name.endswith("_ns") and "layout" not in name and "geometry" not in name}
                if ledger not in ledger_cache:
                    check_receipt(case, snapshot, ev, answer, query["check"], exact, raw, proof_counts, covered)
                    ledger_cache[ledger] = stable
                else:
                    require(stable == ledger_cache[ledger], "repeated semantic verification receipt changed")
                require(query["check"]["verification_cpu_ns"] <= query["phases"]["verify"], "checker CPU not debited")
                require(query["bytes"] == len(canonical(answer)), "return serialization size")
                work = query["work"]
                require(work.get("face_tests", 0) == work.get("face_successes", 0) + work.get("face_failures", 0), "probe outcomes not conserved")
                require(work.get("query_row_requests", 0) == work.get("query_unique_rows", 0) + work.get("query_reused_rows", 0)
                        and work.get("query_output_bit_reads", 0) == 2 * work.get("query_unique_rows", 0), "solver observation debit")
                require(work.get("proofs_returned", 0) == len(answer.get("pair_proofs", [])), "returned proof count")
                totals["verified_timed_returns"] += 1
                totals["covered_raw_rows"] += 1 << case["n"]
                totals["covered_raw_output_bits"] += 2 << case["n"]
                width = snapshot["facts"]["minimum_bits"]
                kind = "broken" if width == 2 else "surviving"
                require(grades[pid]["edits"][eid]["kind"] == kind, "private kind differs from independent minimum")
                correct[seed, kind] += 1
                proof_seed[seed] += work.get("proofs_returned", 0)
                if block == 0:
                    for label, values in (("solver", work), ("checker", query["check"])):
                        counts[panel, arm][kind + "." + label].update({name: value for name, value in values.items()
                            if type(value) is int and not name.endswith(("_ns", "_ms"))})
                named[f"{pid}/{eid}"]["methods"].setdefault(arm, set()).add(program)
                step_costs.append(query["cpu_ns"])
                phases.update({"edits." + name: value for name, value in query["phases"].items()})
            require(len(step_costs) > position, "empty parent after stream filtering")
            step_costs[position] += prepared
            step_costs[-1] += row["cpu_ns"] - prepared - sum(q["cpu_ns"] for q in row["edits"])
        require(observed == expected_tasks and len(observed) == envelope["edits"], "incomplete named held edit matrix")
        require(envelope["startup_ns"] + sum(row["cpu_ns"] for row in rows) <= envelope["cpu_ns"], "whole process debit containment")
        step_costs[0] += envelope["startup_ns"]
        step_costs[-1] += envelope["cpu_ns"] - sum(step_costs)
        cumulative, value = [], 0
        for step in step_costs:
            require(step >= 0, "negative prospective step")
            value += step; cumulative.append(value)
        require(value == envelope["cpu_ns"], "forward CPU prefix does not close")
        phases["total"] = envelope["cpu_ns"]
        runs[key] = dict(total=value, phases=phases, seeds=seed_times, order=order,
                         prefix=cumulative, correct=correct, proofs=proof_seed)
    require(set(runs) == {(panel, arm, block) for panel in ("mixed", "broken") for arm in MODES for block in range(8)}, "incomplete named method/block matrix")
    require(totals["verified_timed_returns"] == 6048, "held return cardinality")
    debit = training_bill["total_training_debit_cpu_ns"]
    require(claimed["training_bill"]["training_ns"] == debit and claimed["failures"] == [], "claimed training debit/failures")
    comparison_summary = {}
    for panel in ("mixed", "broken"):
        for arm in MODES:
            saved = claimed["panels"][panel]["arms"][arm]
            entries = [runs[panel, arm, block] for block in range(8)]
            for name in set().union(*(entry["phases"] for entry in entries)):
                require(saved["median_ns"][name] == median(entry["phases"].get(name, 0) for entry in entries), "claimed phase median")
            require(saved["counts"] == {name: dict(value) for name, value in counts[panel, arm].items()}, "first-block semantic count aggregation")
            require(saved["whole_with_training_ns"] == median(entry["total"] for entry in entries) + (debit if arm == "learned" else 0), "training charged more/less than once")
            kinds = {kind for _, kind in entries[0]["correct"]}
            unique_correct = {kind: sum(value for (_, label), value in entries[0]["correct"].items() if label == kind) for kind in kinds}
            require(saved["correct_unique"] == unique_correct, "unique exact-return totals")
            by_seed = {seed: {kind: entries[0]["correct"].get((seed, kind), 0) for kind in kinds}
                       for seed in map(str, held_info["seeds"])}
            require(saved["correct_by_seed"] == by_seed and saved["proofs_by_seed"] == dict(entries[0]["proofs"]), "per-seed correctness/proof counts")
            for seed in map(str, held_info["seeds"]):
                require(saved["seed_deployment_ns"][seed] == median(entry["seeds"][seed] for entry in entries), "per-seed deployment median")
        comparisons = {}
        for arm in set(MODES) - {"learned"}:
            deltas = [runs[panel, arm, block]["total"] - runs[panel, "learned", block]["total"] for block in range(8)]
            curves = []
            for block in (0, 2, 4, 6):
                first, second = runs[panel, arm, block], runs[panel, "learned", block]
                require(first["order"] == second["order"], "unpaired prospective order")
                curves.append([x - y - debit for x, y in zip(first["prefix"], second["prefix"], strict=True)])
            forward = [median(values) for values in zip(*curves)]
            expected = dict(verification_and_deployment_gains_ns=deltas, median_paired_ns=median(deltas),
                paid_paired_ns=median(deltas) - debit, wins_without_training=sum(x > 0 for x in deltas),
                wins_with_training=sum(x > debit for x in deltas), first_paid_break_even=next((i for i, v in enumerate(forward, 1) if v >= 0), None),
                cheapest_remaining_prefix_gap_ns=max(0, -max(forward)), final_forward_prefix_net_ns=forward[-1], forward_net_ns=forward)
            require(expected == claimed["panels"][panel]["comparisons"][arm], "claimed paired costs or break-even differs")
            comparisons[arm] = {name: value for name, value in expected.items() if name not in ("forward_net_ns", "verification_and_deployment_gains_ns")}
        comparison_summary[panel] = comparisons
    require(digest(directory / "model.json") == freeze["model_sha256"] and canonical(model) == frozen_model, "final model changed")
    for task in named.values():
        require(set(task["methods"]) == set(MODES), "named task omitted by a method")
        task["methods"] = {name: sorted(values) for name, values in task["methods"].items()}
    return dict(schema_version=1, ticket=TICKET, artifact_id=TICKET + "-E002", evidence_stage="exploratory",
        verdict="PASS", auditor_sha256=digest(Path(__file__)), independent_oracle_sha256=INDEPENDENT_SHA256,
        recorded_freeze_sha256=recorded_freeze, model_sha256=freeze["model_sha256"], audit_cpu=audit_cpu,
        source_design_sha256=digest(directory / "design.json"), raw_manifest_sha256=digest(directory / "results.jsonl"),
        result_sha256=digest(directory / "result.json"), split_integrity=dict(splits={"E001": old_info, "train": train_info, "blind": held_info}, intersections=intersections),
        fitting_and_inference=fitting, training_bill=training_bill, held_replay=dict(totals),
        streams=len(runs), named_tasks=named, comparison_summary=comparison_summary,
        correctness_scope="Each unique current program is raw/stage executed and cut/minimum checked; repeated immutable program/target/proof hashes reuse only that independent verdict. Every receipt and named method is checked.",
        timing_scope="Saved primary CPU only; this auditor makes no primary timing measurement.",
        limitations=["Held sizes8,9,10 also occur in training; this is seed/family transfer within one generator.",
                     "The training selector optimizes a declared work proxy, not held CPU; its selected mixed proxy score is negative.",
                     "Eight paired fresh-process blocks on one CPU are a bounded runtime comparison, not a population theorem.",
                     "This is source-independent same-task replay, not an external research-team replication."],
        self_test=self_test())


def self_test():
    p = independent()
    case = dict(id="audit-synthetic", n=5, upstream_count=0, frontier=[0, 1, 2, 3, 4],
                gates=[[0, 1], [7, 7], [8, 2], [9, 9], [10, 10]],
                outputs=[10, 11], pieces=[], edits=[])
    raw, stage = p.raw_words(case), p.stage_words(case)
    mapping, _ = p.frontier_domain(case, raw)
    p.project_source(case, raw, stage, mapping)
    targets = tuple(stage[w] for w in case["outputs"])
    answer = dict(status="exact", n=5, triple=[0, 1, 2], width=1, class_count=2,
                  summary_wires=[10], circuit=dict(n=5, gates=case["gates"], outputs=case["outputs"]))
    answer["physical"] = dict(n=5, gates=case["gates"], outputs=case["outputs"],
                              summary_wires=[10], frontier=case["frontier"])
    p.check_lift(case, answer)
    checked, _ = p.oracle().verify_result(5, targets, answer)
    require(checked["exact"] and checked["width"] == 1, "independent synthetic minimum")
    require(tuple(p.physical_words(answer["physical"])[w] for w in case["outputs"]) == targets, "synthetic raw replay")
    return dict(raw_rows=32, stage_rows=32, producer_or_checker_imports=0,
                exact_triple_minimum=True, raw_NAND_output_replay=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--directory", type=Path, default=DEFAULT)
    parser.add_argument("--recorded-freeze-sha256")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), sort_keys=True))
        return
    if args.recorded_freeze_sha256 is None:
        parser.error("held audit requires --recorded-freeze-sha256 from the authorized pre-blind record")
    require(args.directory.resolve() == DEFAULT.resolve(), "audit output ownership is limited to E002")
    result = audit_all(args.directory.resolve(), args.recorded_freeze_sha256)
    output = args.directory / "audit.json"
    data = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if output.exists():
        require(output.read_text() == data, "unequal existing audit receipt")
    else:
        with output.open("x") as handle:
            handle.write(data)
    print(json.dumps(dict(verdict=result["verdict"], streams=result["streams"], held_replay=result["held_replay"],
                          model_sha256=result["model_sha256"], output=str(output)), sort_keys=True))


if __name__ == "__main__":
    main()
