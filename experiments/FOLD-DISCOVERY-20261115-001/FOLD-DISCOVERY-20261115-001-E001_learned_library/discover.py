"""Blind recurring two-gate fragment discovery from supplied primitive ASTs.

No task generator, labels, predecessor component, or test result is imported.
Each binary parent/child adjacency becomes two primitive gates with three
anonymous boundary holes. All6 hole permutations define its semantic orbit;
the least8-bit truth integer is its canonical key. Support counts DISTINCT
training task IDs, then occurrences. Selection ties use that key alone.

All three-hole essential classes are nontrivial, including associative pairs.
No association/operator class is favored or excluded. A canonical executable
representative is the least serialized AST realizing the canonical truth in
the universal108 two-gate AND/OR/XOR expressions on3 distinct holes. This is
representation canonicalization, not a candidate-support prior.

fit(programs) -> deterministic JSON-safe checkpoint. Recommended input rows:
  {'task_id': opaque str/int, 'expr': primitive AST or JSON/Python-literal AST}
An optional status must be 'exact'; other statuses/missing programs are
counted as rejected inputs. Plain AST rows get their list index as task ID.
Duplicate (task ID,exact AST) records are counted once. Different programs
from one task may add occurrences but never additional task support.

ASTs: ['input',j], ['const',bit], ['AND'|'OR'|'XOR',A,B]. No FOLD node is
accepted. Fragment holes abstract complete boundary subexpressions, including
literal/constant bindings, without inspecting or evaluating those bindings.
Whole source-program truth tables are never evaluated by discovery.

Selected/proposal DAGs use inputs0..2, constants0/1 at3/4, NAND k at5+k.
AND/OR/XOR compile to2/3/4 standard NANDs with no shared-subexpression CSE.
Inference executes these gates; the truth byte is a semantic identifier only.
"""

from __future__ import annotations

import argparse
import ast
import itertools
import json


SOURCE_DEPENDENCIES = ()
SCHEMA_VERSION = 1
OPS = ("AND", "OR", "XOR")
PERMUTATIONS = tuple(itertools.permutations(range(3)))
INPUT_COLUMNS = (170, 204, 240)
COUNTERS = (
    "input_records", "rejected_input_records", "duplicate_task_program_records",
    "successful_program_records", "distinct_successful_programs", "training_tasks",
    "source_AST_nodes_parsed", "source_binary_gates", "adjacent_gate_pairs",
    "generic_representative_programs", "generic_raw_truth_values",
    "fragment_permutation_evaluations", "semantic_truth_evaluations",
    "semantic_binary_ops", "essentiality_variable_checks",
    "task_support_membership_checks", "new_task_supports", "occurrence_updates",
    "proposal_classes", "eligible_classes", "rejected_classes", "one_off_classes",
    "unselected_eligible_classes", "matched_occurrences", "discarded_occurrences",
    "matched_program_records", "matched_training_tasks", "physical_programs_compiled",
    "physical_NANDs_compiled", "physical_scalar_NANDs_verified", "physical_input_bits_read",
)


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _parse(value, work):
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            try:
                value = ast.literal_eval(value)
            except (ValueError, SyntaxError) as exc:
                raise ValueError("expr string must be a literal primitive AST") from exc
    if not isinstance(value, (tuple, list)) or not value:
        raise ValueError("expected a primitive AST")
    work["source_AST_nodes_parsed"] += 1
    op = value[0]
    if op == "input" and len(value) == 2:
        j = value[1]
        if type(j) is not int or j < 0:
            raise ValueError("input index must be a nonnegative integer")
        return (op, j)
    if op == "const" and len(value) == 2:
        bit = value[1]
        if type(bit) not in (int, bool) or bit not in (0, 1):
            raise ValueError("constant must be a literal bit")
        return (op, int(bit))
    if op in OPS and len(value) == 3:
        return (op, _parse(value[1], work), _parse(value[2], work))
    raise ValueError("only primitive AND/OR/XOR/input/const ASTs are accepted")


def _truth(expr, work):
    def evaluate(node):
        if node[0] == "input":
            return INPUT_COLUMNS[node[1]]
        a, b = evaluate(node[1]), evaluate(node[2])
        work["semantic_binary_ops"] += 1
        return (a & b) if node[0] == "AND" else ((a | b) if node[0] == "OR" else (a ^ b))
    work["semantic_truth_evaluations"] += 1
    return evaluate(expr)


def _rename(expr, permutation):
    if expr[0] == "input":
        return ("input", permutation[expr[1]])
    return (expr[0], _rename(expr[1], permutation), _rename(expr[2], permutation))


def _canonical_truth(fragment, work):
    values = []
    for permutation in PERMUTATIONS:
        values.append(_truth(_rename(fragment, permutation), work))
        work["fragment_permutation_evaluations"] += 1
    return min(values)


def _representatives(work):
    # Fixed language enumeration, independent of data/operator frequencies.
    # Store one representative for each raw truth; observed fragments choose
    # their canonical orbit key afterward. No class gets artificial support.
    representatives, keys = {}, {}
    for outer, inner, permutation, side in itertools.product(OPS, OPS, PERMUTATIONS, (0, 1)):
        a, b, c = (("input", j) for j in permutation)
        expr = (outer, (inner, a, b), c) if side == 0 else (outer, a, (inner, b, c))
        truth = _truth(expr, work)
        key = _json(expr)
        if truth not in representatives or key < keys[truth]:
            representatives[truth], keys[truth] = expr, key
        work["generic_representative_programs"] += 1
    work["generic_raw_truth_values"] = len(representatives)
    return representatives


def _fragments(expr, work):
    if expr[0] not in OPS:
        return
    work["source_binary_gates"] += 1
    for side in (1, 2):
        child = expr[side]
        if child[0] in OPS:
            a, b, c = (("input", j) for j in range(3))
            fragment = ((expr[0], (child[0], a, b), c) if side == 1
                        else (expr[0], a, (child[0], b, c)))
            work["adjacent_gate_pairs"] += 1
            yield fragment
    yield from _fragments(expr[1], work)
    yield from _fragments(expr[2], work)


def _essential(truth, work):
    good = True
    for j, column in enumerate(INPUT_COLUMNS):
        work["essentiality_variable_checks"] += 1
        if not ((truth ^ (truth >> (1 << j))) & (255 ^ column)):
            good = False
    return good


def _compile(expr, work):
    gates = []
    def nand(a, b):
        gates.append([a, b])
        return 4 + len(gates)
    def emit(node):
        op = node[0]
        if op == "input":
            return node[1]
        a, b = emit(node[1]), emit(node[2])
        if op == "AND":
            t = nand(a, b)
            return nand(t, t)
        if op == "OR":
            return nand(nand(a, a), nand(b, b))
        t = nand(a, b)
        return nand(nand(a, t), nand(b, t))
    output = emit(expr)
    work["physical_programs_compiled"] += 1
    work["physical_NANDs_compiled"] += len(gates)
    return {"gates": gates, "output": output}


def execute_dag(dag, a, b, c):
    """Run the frozen physical circuit on literal bits; no truth lookup."""
    if any(type(v) not in (int, bool) or v not in (0, 1) for v in (a, b, c)):
        raise ValueError("physical inputs must be literal bits")
    values = [int(a), int(b), int(c), 0, 1]
    for left, right in dag["gates"]:
        values.append(1 ^ (values[left] & values[right]))
    return values[dag["output"]]


def fit(programs):
    """Return a deterministic checkpoint; caller meters fitting wall/CPU.

    selected is None unless a three-essential-hole class appears in at least
    two DISTINCT task IDs. Proposals retain every observed semantic class,
    its support IDs/counts, occurrences, canonical AST/circuit and disposition.
    Counts are integer-only. No nondeterministic timing enters the checkpoint.
    'distinct_successful_programs' means distinct exact AST serializations,
    not semantic equivalence or distinct target truth tables.
    """
    work = {key: 0 for key in COUNTERS}
    representatives = _representatives(work)
    accepted, seen_records, unique_programs, task_ids = [], set(), set(), {}
    for index, record in enumerate(programs):
        work["input_records"] += 1
        if isinstance(record, dict):
            task_id = record.get("task_id", record.get("id", index))
            expr = record.get("expr")
            status = record.get("status", "exact")
        else:
            task_id, expr, status = index, record, "exact"
        if type(task_id) not in (str, int):
            raise ValueError("task_id must be an opaque string/integer")
        if status != "exact" or expr is None:
            work["rejected_input_records"] += 1
            continue
        parsed = _parse(expr, work)
        task_key, program_key = _json(task_id), _json(parsed)
        if (task_key, program_key) in seen_records:
            work["duplicate_task_program_records"] += 1
            continue
        seen_records.add((task_key, program_key))
        accepted.append((task_key, program_key, task_id, parsed))
        unique_programs.add(program_key)
        task_ids[task_key] = task_id
    work["successful_program_records"] = len(accepted)
    work["distinct_successful_programs"] = len(unique_programs)
    work["training_tasks"] = len(task_ids)
    # Sorting makes the complete checkpoint invariant to record arrival order
    # when caller supplies explicit stable IDs. No task ID affects selection.
    accepted.sort(key=lambda row: (row[0], row[1]))
    classes, trace = {}, []
    for task_key, _, task_id, expr in accepted:
        counts = {}
        for fragment in _fragments(expr, work):
            truth = _canonical_truth(fragment, work)
            counts[truth] = counts.get(truth, 0) + 1
            if truth not in classes:
                classes[truth] = {"tasks": set(), "occurrences": 0}
            candidate = classes[truth]
            work["task_support_membership_checks"] += 1
            if task_key not in candidate["tasks"]:
                candidate["tasks"].add(task_key)
                work["new_task_supports"] += 1
            candidate["occurrences"] += 1
            work["occurrence_updates"] += 1
        trace.append({"task_id": task_id, "pairs": sum(counts.values()),
                      "class_counts": [[key, counts[key]] for key in sorted(counts)]})
    proposals = []
    for truth in sorted(classes):
        entry = classes[truth]
        expr = representatives[truth]
        dag = _compile(expr, work)
        actual = 0
        for x in range(8):
            actual |= execute_dag(dag, x & 1, (x >> 1) & 1, (x >> 2) & 1) << x
        work["physical_input_bits_read"] += 24
        work["physical_scalar_NANDs_verified"] += 8 * len(dag["gates"])
        if actual != truth:
            raise AssertionError("canonical fragment circuit failed physical replay")
        tasks = sorted(entry["tasks"])
        nontrivial = _essential(truth, work)
        proposals.append({
            "truth": truth, "expr": json.loads(_json(expr)), "dag": dag,
            "nand_gates": len(dag["gates"]), "input_arity": 3,
            "distinct_tasks": len(tasks), "occurrences": entry["occurrences"],
            "supporting_task_ids": [task_ids[key] for key in tasks],
            "nontrivial": nontrivial, "eligible": nontrivial and len(tasks) >= 2,
        })
    eligible = [p for p in proposals if p["eligible"]]
    selected = min(eligible, key=lambda p: (-p["distinct_tasks"], -p["occurrences"], p["truth"])) if eligible else None
    for proposal in proposals:
        proposal["selected"] = proposal is selected
        proposal["disposition"] = (
            "selected" if proposal is selected else
            "trivial" if not proposal["nontrivial"] else
            "one_off" if proposal["distinct_tasks"] < 2 else "eligible_not_selected"
        )
    work["proposal_classes"] = len(proposals)
    work["eligible_classes"] = len(eligible)
    work["rejected_classes"] = len(proposals) - len(eligible)
    work["one_off_classes"] = sum(p["disposition"] == "one_off" for p in proposals)
    work["unselected_eligible_classes"] = sum(p["disposition"] == "eligible_not_selected" for p in proposals)
    work["matched_occurrences"] = 0 if selected is None else selected["occurrences"]
    work["discarded_occurrences"] = work["adjacent_gate_pairs"] - work["matched_occurrences"]
    work["matched_training_tasks"] = 0 if selected is None else selected["distinct_tasks"]
    work["matched_program_records"] = 0 if selected is None else sum(
        any(truth == selected["truth"] for truth, _ in row["class_counts"]) for row in trace)
    result = {
        "schema_version": SCHEMA_VERSION, "selected": selected,
        "proposals": proposals, "accounting": work, "training_trace": trace,
        "selection_rule": "distinct training tasks descending, occurrences descending, canonical truth byte ascending; at least two tasks and three essential holes",
        "canonicalization": "minimum truth byte over six input permutations; minimum serialized generic two-gate AST at that truth; no input/output negations",
        "representative_grammar": {"binary_ops": list(OPS), "binary_gates": 2,
                                   "distinct_input_holes": 3, "NAND_costs": {"AND": 2, "OR": 3, "XOR": 4}},
    }
    # A JSON round trip breaks internal shared references and checks that the
    # complete frozen envelope is plain data. No timing/sample state is saved.
    return json.loads(_json(result))


def self_test():
    """Synthetic AST fixtures only, including neutral/one-off alternatives."""
    x = tuple(("input", j) for j in range(8))
    # Associative and mixed classes compete under the identical ranking.
    a = ("OR", ("OR", x[0], x[1]), x[2])
    b = ("OR", x[5], ("OR", x[3], x[4]))
    c = ("AND", ("XOR", x[0], x[1]), x[2])
    checkpoint = fit([{"task_id": "a", "expr": a},
                      {"task_id": "b", "expr": _json(b)},
                      {"task_id": "c", "expr": c}])
    if checkpoint["selected"] is None or checkpoint["selected"]["distinct_tasks"] != 2:
        raise AssertionError("recurrence selection failed")
    if checkpoint["accounting"]["one_off_classes"] != 1:
        raise AssertionError("one-off proposals were not retained")
    if checkpoint["accounting"]["generic_representative_programs"] != 108:
        raise AssertionError("universal two-gate grammar was truncated")
    if checkpoint["accounting"]["generic_raw_truth_values"] != 21:
        raise AssertionError("generic truth catalogue discrepancy")
    rows = [{"task_id": "a", "expr": a}, {"task_id": "b", "expr": b},
            {"task_id": "c", "expr": c}]
    if fit(rows) != fit(list(reversed(rows))):
        raise AssertionError("record arrival order changed checkpoint")
    # Repeating a program/task record never manufactures recurring support.
    duplicate = fit([{"task_id": 1, "expr": a}, {"task_id": 1, "expr": a}])
    if duplicate["selected"] is not None or duplicate["accounting"]["duplicate_task_program_records"] != 1:
        raise AssertionError("duplicate task/program inflated support")
    # A parent with two binary children has both connected pairs, plus their
    # deeper adjacencies if any; repeated occurrences within one task remain
    # a single task support.
    branched = ("AND", a, ("XOR", x[3], x[4]))
    one = fit([{"task_id": "one", "expr": branched}])
    if one["accounting"]["adjacent_gate_pairs"] != 3 or one["selected"] is not None:
        raise AssertionError("connected pair enumeration or support failed")
    empty = fit([{"task_id": 0, "status": "unsupported", "expr": None}, x[0]])
    if empty["selected"] is not None or empty["proposals"]:
        raise AssertionError("empty fragment input selected a component")
    if empty["accounting"]["rejected_input_records"] != 1:
        raise AssertionError("unsuccessful source program was not counted")
    bad = 0
    for invalid in (("FOLD", x[0], x[1], x[2]), ("input", -1)):
        try:
            fit([invalid])
        except ValueError:
            bad += 1
    if bad != 2:
        raise AssertionError("forbidden/malformed source AST accepted")
    # All generic templates under all input permutations give the same orbit.
    work = {key: 0 for key in COUNTERS}
    catalogue = _representatives(work)
    classes = set()
    for expr in catalogue.values():
        truth = _canonical_truth(expr, work)
        classes.add(truth)
        if any(_canonical_truth(_rename(expr, p), work) != truth for p in PERMUTATIONS):
            raise AssertionError("input permutation changed semantic class")
    if len(classes) != 9:
        raise AssertionError("unexpected two-gate semantic class count")
    return {"synthetic_only": True, "status": "passed", "generic_programs": 108,
            "raw_truth_values": 21, "permutation_classes": 9,
            "recurrence_duplicate_empty_order_and_circuit_checks": "passed"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("use --self-test; real fitting belongs to the parent orchestrator")
    print(_json(self_test()))
