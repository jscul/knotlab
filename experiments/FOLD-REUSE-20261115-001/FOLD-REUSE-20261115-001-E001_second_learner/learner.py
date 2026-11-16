"""Public read-once formula catalogue and counterexample-guided second learner.

There is no task generator, target signature, or panel in this module.  The
base grammar is supplied: input leaves and commutative AND/OR/XOR, each input
used once.  The optional prefix contains all such trees with exactly one
three-argument FOLD node.  Its physical NAND DAG is a supplied shared binding,
not an operation name or a formula substituted by this learner.  Both arms
then generate the identical full base tail; truth-equivalent entries retain
the earliest program.  Enumeration, public hypothesis evaluation, duplicate
rejection, and warm-cache returns are accounted separately.

ASTs are JSON-compatible lists (immutable tuples in memory):
  ('input', j), ('AND'|'OR'|'XOR', a, b), ('FOLD', a, b, c).
The local FOLD DAG addresses arguments 0..2, constants 0/1 as 3/4, and NAND
gate k as 5+k.  ``expand`` uses n inputs, constants n/n+1, gate k at n+2+k.
There is no common-subexpression elimination.  AND/OR/XOR expand to 2/3/4
NANDs; every saved fold gate executes, including any unused saved gate.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from functools import lru_cache


OPS = ("AND", "OR", "XOR")
SCHEMA_VERSION = 1
_BASE_RAW_CACHE = {}
_CATALOG_CACHE = {}
_SYNTAX_WORK = {"base_syntax_generated": 0, "fold_syntax_generated": 0}


def _integer(value, name):
    if type(value) is not int:
        raise ValueError(f"{name} must be an integer")
    return value


def _bit(value, name="label"):
    if type(value) not in (int, bool) or value not in (0, 1):
        raise ValueError(f"{name} must be a literal bit")
    return int(value)


def _ast(expr):
    if not isinstance(expr, (tuple, list)) or not expr:
        raise ValueError("expression must be a nonempty AST list/tuple")
    op = expr[0]
    if op == "input" and len(expr) == 2:
        index = _integer(expr[1], "input index")
        if index < 0:
            raise ValueError("negative input index")
        return ("input", index)
    if op in OPS and len(expr) == 3:
        return (op, _ast(expr[1]), _ast(expr[2]))
    if op == "FOLD" and len(expr) == 4:
        return (op, *(_ast(x) for x in expr[1:]))
    raise ValueError("unknown operation or wrong AST arity")


def _canonical_dag(dag):
    if dag is None:
        return None
    if not isinstance(dag, dict) or "gates" not in dag or "output" not in dag:
        raise ValueError("fold DAG needs gates and output")
    gates = []
    for k, gate in enumerate(dag["gates"]):
        if not isinstance(gate, (list, tuple)) or len(gate) != 2:
            raise ValueError("each fold gate must contain two addresses")
        pair = tuple(_integer(a, "fold address") for a in gate)
        if any(a < 0 or a >= 5 + k for a in pair):
            raise ValueError("fold gate has a nonprevious address")
        gates.append(pair)
    output = _integer(dag["output"], "fold output")
    if output < 0 or output >= 5 + len(gates):
        raise ValueError("fold output address is invalid")
    return {"gates": [list(g) for g in gates], "output": output}


def _dag_key(dag):
    return None if dag is None else (tuple(map(tuple, dag["gates"])), dag["output"])


def _leaves(expr):
    if expr[0] == "input":
        return (expr[1],)
    return tuple(i for child in expr[1:] for i in _leaves(child))


def expand(expr, fold_dag=None, n=None):
    """Compile an AST to physical NAND gates, without semantic substitution.

    Return keys: inputs, gates, output, constants, nand_gates, macro_uses,
    underlying_ops.  A FOLD binding is stored once by the caller/catalogue;
    ASTs refer to it by the literal FOLD operation.
    """
    expr = _ast(expr)
    fold_dag = _canonical_dag(fold_dag)
    leaves = _leaves(expr)
    inferred = max(leaves, default=-1) + 1
    n = inferred if n is None else _integer(n, "n")
    if n < inferred or n < 1:
        raise ValueError("n must include every input leaf")
    gates = []
    ops = {op: 0 for op in OPS}
    macro_uses = 0

    def nand(a, b):
        gates.append([a, b])
        return n + 1 + len(gates)

    def emit(node):
        nonlocal macro_uses
        op = node[0]
        if op == "input":
            return node[1]
        args = [emit(child) for child in node[1:]]
        if op == "FOLD":
            if fold_dag is None:
                raise ValueError("FOLD node requires a supplied physical DAG")
            macro_uses += 1
            local = args + [n, n + 1]
            for left, right in fold_dag["gates"]:
                local.append(nand(local[left], local[right]))
            return local[fold_dag["output"]]
        ops[op] += 1
        a, b = args
        if op == "AND":
            t = nand(a, b)
            return nand(t, t)
        if op == "OR":
            return nand(nand(a, a), nand(b, b))
        t = nand(a, b)
        return nand(nand(a, t), nand(b, t))

    output = emit(expr)
    return {
        "inputs": n, "gates": gates, "output": output,
        "constants": {"zero": n, "one": n + 1},
        "nand_gates": len(gates), "macro_uses": macro_uses,
        "underlying_ops": ops,
    }


def execute(compiled, x):
    """Execute every compiled NAND on one input integer."""
    n = compiled["inputs"]
    x = _integer(x, "x")
    if not 0 <= x < 1 << n:
        raise ValueError("x lies outside the declared input register")
    values = [(x >> j) & 1 for j in range(n)] + [0, 1]
    for left, right in compiled["gates"]:
        values.append(1 ^ (values[left] & values[right]))
    return values[compiled["output"]]


def _columns(n, raw_masks):
    columns = [0] * n
    for lane, x in enumerate(raw_masks):
        x = _integer(x, "raw input")
        if not 0 <= x < 1 << n:
            raise ValueError("raw input lies outside the declared register")
        for j in range(n):
            columns[j] |= ((x >> j) & 1) << lane
    return columns


def _execute_columns(compiled, columns, lanes):
    all_lanes = (1 << lanes) - 1
    values = list(columns) + [0, all_lanes]
    for left, right in compiled["gates"]:
        values.append(all_lanes ^ (values[left] & values[right]))
    return values[compiled["output"]]


def execute_packed(compiled, raw_masks):
    """Return one packed answer column; lane i corresponds to raw_masks[i]."""
    raw_masks = tuple(raw_masks)
    return _execute_columns(compiled, _columns(compiled["inputs"], raw_masks),
                            len(raw_masks))


def eval_expr(expr, x, fold_dag=None, n=None):
    return execute(expand(expr, fold_dag, n), x)


def eval_packed(expr, raw_masks, fold_dag=None, n=None):
    return execute_packed(expand(expr, fold_dag, n), raw_masks)


# Explicit aliases for external scalar/packed interpreters.
evaluate = eval_expr
evaluate_packed = eval_packed


def _bipartitions(mask):
    # Each unordered split appears once, with the lowest variable at left.
    low = mask & -mask
    left = (mask - 1) & mask
    while left:
        right = mask ^ left
        if right and left & low:
            yield left, right
        left = (left - 1) & mask


def _binary(op, a, b):
    return (op, a, b) if a <= b else (op, b, a)


@lru_cache(maxsize=None)
def _base_syntax(mask):
    if mask.bit_count() == 1:
        result = (("input", mask.bit_length() - 1),)
    else:
        result = tuple(sorted(
            _binary(op, a, b)
            for left, right in _bipartitions(mask)
            for a in _base_syntax(left)
            for b in _base_syntax(right)
            for op in OPS
        ))
    _SYNTAX_WORK["base_syntax_generated"] += len(result)
    return result


@lru_cache(maxsize=None)
def _fold_syntax(mask):
    if mask.bit_count() < 3:
        return ()
    expressions = []
    # Ordered FOLD arguments: no symmetry of the saved function is assumed.
    first = (mask - 1) & mask
    while first:
        remaining = mask ^ first
        second = (remaining - 1) & remaining
        while second:
            third = remaining ^ second
            if third:
                expressions.extend(
                    ("FOLD", a, b, c)
                    for a in _base_syntax(first)
                    for b in _base_syntax(second)
                    for c in _base_syntax(third)
                )
            second = (second - 1) & remaining
        first = (first - 1) & mask
    # A single FOLD can also be nested below ordinary binary operations.
    for left, right in _bipartitions(mask):
        for a in _fold_syntax(left):
            for b in _base_syntax(right):
                expressions.extend(_binary(op, a, b) for op in OPS)
        for a in _base_syntax(left):
            for b in _fold_syntax(right):
                expressions.extend(_binary(op, a, b) for op in OPS)
    result = tuple(sorted(expressions))
    _SYNTAX_WORK["fold_syntax_generated"] += len(result)
    return result


def _cache_snapshot():
    return {
        **_SYNTAX_WORK,
        "base_syntax_hits": _base_syntax.cache_info().hits,
        "base_syntax_misses": _base_syntax.cache_info().misses,
        "fold_syntax_hits": _fold_syntax.cache_info().hits,
        "fold_syntax_misses": _fold_syntax.cache_info().misses,
    }


def _raw_entries(n, expressions, fold_dag, work):
    columns = _columns(n, range(1 << n))
    work["input_columns_built"] += n
    work["input_column_bit_reads"] += n * (1 << n)
    entries = []
    for expr in expressions:
        compiled = expand(expr, fold_dag, n)
        truth = _execute_columns(compiled, columns, 1 << n)
        nands = compiled["nand_gates"]
        work["hypothesis_programs_compiled"] += 1
        work["compiled_NANDs"] += nands
        work["public_packed_NANDs"] += nands
        work["public_scalar_equivalent_NANDs"] += nands * (1 << n)
        entries.append({
            "truth": truth, "expr": expr,
            "macro_uses": compiled["macro_uses"],
            "search_operations": sum(compiled["underlying_ops"].values())
                                 + compiled["macro_uses"],
            "expanded_NANDs": nands,
            "underlying_ops": compiled["underlying_ops"],
        })
    return tuple(entries)


def _base_entries(n, work):
    if n in _BASE_RAW_CACHE:
        work["base_raw_cache_hits"] += 1
    else:
        _BASE_RAW_CACHE[n] = _raw_entries(n, _base_syntax((1 << n) - 1),
                                        None, work)
        work["base_raw_cache_misses"] += 1
    return _BASE_RAW_CACHE[n]


def _zero_work():
    return {key: 0 for key in (
        "hypothesis_programs_compiled", "compiled_NANDs",
        "public_packed_NANDs", "public_scalar_equivalent_NANDs",
        "input_columns_built", "input_column_bit_reads",
        "base_raw_cache_hits", "base_raw_cache_misses",
        "base_index_attempts", "fold_index_attempts",
        "base_duplicates_rejected", "fold_duplicates_rejected",
        "base_retained", "fold_retained",
    )}


def build_catalog(n, fold_dag_or_None=None):
    """Build/cache public hypotheses only; no examples or oracle are accepted.

    Candidates are a tuple of dicts with truth, expr, origin, generation_index,
    macro_uses, search_operations, expanded_NANDs and underlying_ops.  Truth
    bit x is the hypothesis output on input x.  The returned dictionary and
    reverse index are fresh; candidate entries are shared read-only records.
    Construction counts describe work in THIS call, not cached historical
    work.  ``catalogue_totals`` retain logical cold build totals for replay.
    """
    started = time.perf_counter()
    n = _integer(n, "n")
    if n not in (4, 5):
        raise ValueError("the frozen public class supports n=4 or n=5")
    dag = _canonical_dag(fold_dag_or_None)
    key = (n, _dag_key(dag))
    before = _cache_snapshot()
    work = _zero_work()
    cache_hit = key in _CATALOG_CACHE
    if not cache_hit:
        base = _base_entries(n, work)
        fold = ()
        if dag is not None:
            # Capacity guard only: compare the supplied 3-input primitive to
            # the supplied base grammar, never to any task target.
            base3 = _base_entries(3, work)
            fold3 = expand(("FOLD", ("input", 0), ("input", 1),
                            ("input", 2)), dag, 3)
            fold_truth = _execute_columns(fold3, _columns(3, range(8)), 8)
            work["input_columns_built"] += 3
            work["input_column_bit_reads"] += 24
            work["hypothesis_programs_compiled"] += 1
            work["compiled_NANDs"] += fold3["nand_gates"]
            work["public_packed_NANDs"] += fold3["nand_gates"]
            work["public_scalar_equivalent_NANDs"] += 8 * fold3["nand_gates"]
            if fold_truth not in {row["truth"] for row in base3}:
                raise ValueError("supplied fold is outside the read-once base class")
            fold = _raw_entries(n, _fold_syntax((1 << n) - 1), dag, work)
        candidates, truth_to_index = [], {}
        generation_index = 0
        for origin, rows in (("fold", fold), ("base", base)):
            for row in rows:
                work[f"{origin}_index_attempts"] += 1
                if row["truth"] in truth_to_index:
                    work[f"{origin}_duplicates_rejected"] += 1
                else:
                    truth_to_index[row["truth"]] = len(candidates)
                    candidates.append({**row, "origin": origin,
                                       "generation_index": generation_index})
                    work[f"{origin}_retained"] += 1
                generation_index += 1
        # This equality is public-class containment, not task evaluation.
        if set(truth_to_index) != {row["truth"] for row in base}:
            raise AssertionError("fold changed the semantic hypothesis class")
        binding = dag
        binding_hash = None if dag is None else hashlib.sha256(
            json.dumps(dag, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        _CATALOG_CACHE[key] = {
            "schema_version": SCHEMA_VERSION, "n": n,
            "fold_dag": binding, "fold_dag_sha256": binding_hash,
            "candidates": tuple(candidates), "truth_to_index": truth_to_index,
            "order": "fold_prefix_then_common_base" if dag else "common_base",
            "raw_base_programs": len(base), "raw_fold_programs": len(fold),
            "catalogue_totals": {
                "index_attempts": len(base) + len(fold),
                "duplicate_rejections": len(base) + len(fold) - len(candidates),
                "unique_truth_functions": len(candidates),
                "fold_retained": sum(row["origin"] == "fold" for row in candidates),
                "base_retained": sum(row["origin"] == "base" for row in candidates),
            },
        }
    stored = _CATALOG_CACHE[key]
    result = {**stored, "truth_to_index": dict(stored["truth_to_index"])}
    after = _cache_snapshot()
    result["construction"] = {
        "catalogue_cache_hit": cache_hit,
        **work,
        **{k: after[k] - before[k] for k in before},
        "return_index_entries_copied": len(result["truth_to_index"]),
        "elapsed_seconds": time.perf_counter() - started,
    }
    return result


def _examples(examples, n):
    normalized, labels = [], {}
    supplied = 0
    for row in examples:
        supplied += 1
        if not isinstance(row, (tuple, list)) or len(row) != 2:
            raise ValueError("examples must be (x,label) pairs")
        x, label = _integer(row[0], "example x"), _bit(row[1])
        if not 0 <= x < 1 << n:
            raise ValueError("example x outside declared inputs")
        if x in labels and labels[x] != label:
            raise ValueError("conflicting labels")
        if x not in labels:
            labels[x] = label
            normalized.append([x, label])
    return normalized, labels, supplied


def fit_rule(catalog, examples, check):
    """First-consistent CEGIS; ``check(expr)`` returns None or (x,label).

    No exhaustive target truth is accepted.  Monotone evidence permits a
    single forward pass over the frozen catalogue: a previously inconsistent
    hypothesis cannot become consistent.  The initial proposal is copied to
    the result before any checker call; checker feedback is stored separately.
    Scalar NAND verification costs belong to the external checker, whereas
    packed hypothesis bit reads for sparse-label selection are counted here.
    """
    started = time.perf_counter()
    n = catalog["n"]
    evidence, labels, supplied = _examples(examples, n)
    initial_examples = [row[:] for row in evidence]
    proposals, feedback, added = [], [], []
    inspected = label_tests = 0
    checker_seconds = 0.0
    initial_proposal = final = None
    final_index = None
    for index, row in enumerate(catalog["candidates"]):
        inspected += 1
        consistent = True
        for x, label in evidence:
            label_tests += 1
            if ((row["truth"] >> x) & 1) != label:
                consistent = False
                break
        if not consistent:
            continue
        proposal = {
            "round": len(proposals) + 1, "candidate_index": index,
            "expr": row["expr"], "origin": row["origin"],
            "generation_index": row["generation_index"],
            "macro_uses": row["macro_uses"],
            "search_operations": row["search_operations"],
            "expanded_NANDs": row["expanded_NANDs"],
            "underlying_ops": dict(row["underlying_ops"]),
        }
        proposals.append(proposal)
        if initial_proposal is None:
            initial_proposal = dict(proposal)
        call_started = time.perf_counter()
        counterexample = check(row["expr"])
        checker_seconds += time.perf_counter() - call_started
        if counterexample is None:
            feedback.append({"round": proposal["round"],
                             "candidate_index": index, "exact": True})
            final, final_index = row, index
            break
        new, _, _ = _examples([counterexample], n)
        x, label = new[0]
        if x in labels:
            raise ValueError("checker repeated an already satisfied input")
        if ((row["truth"] >> x) & 1) == label:
            raise ValueError("checker feedback does not refute the proposal")
        labels[x] = label
        evidence.append([x, label])
        event = {"round": proposal["round"], "candidate_index": index,
                 "x": x, "label": label}
        added.append(event)
        feedback.append({**event, "exact": False})
    elapsed = time.perf_counter() - started
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "exact" if final is not None else "exhausted", "n": n,
        "initial_proposal": initial_proposal, "proposals": proposals,
        "hypotheses_inspected": inspected,
        "consistency_label_tests": label_tests,
        "checker_calls": len(proposals), "checker_failures": len(added),
        "checker_seconds": checker_seconds,
        "learner_seconds": elapsed - checker_seconds,
        "elapsed_seconds": elapsed,
        "checker_feedback": feedback, "added_evidence": added,
        "initial_input_example_count": supplied,
        "initial_examples": initial_examples, "final_examples": evidence,
        "final_candidate_index": final_index,
        "final_expr": None if final is None else final["expr"],
        "final_origin": None if final is None else final["origin"],
        "final_macro_uses": None if final is None else final["macro_uses"],
        "final_search_operations": None if final is None else final["search_operations"],
        "final_expanded_NANDs": None if final is None else final["expanded_NANDs"],
    }


def cache_info():
    """Public retained-state accounting; no task-specific state is cached."""
    return {
        **_cache_snapshot(), "base_raw_entries": {
            str(n): len(rows) for n, rows in sorted(_BASE_RAW_CACHE.items())
        },
        "catalogues": len(_CATALOG_CACHE),
        "catalogue_candidate_entries": sum(
            len(c["candidates"]) for c in _CATALOG_CACHE.values()),
    }


def self_test():
    """Synthetic primitive/class checks only; never import a fresh panel."""
    # A toy public three-input formula generates this fixture's physical DAG.
    toy = ("OR", ("AND", ("input", 0), ("input", 1)), ("input", 2))
    toy_compiled = expand(toy, n=3)
    toy_dag = {"gates": toy_compiled["gates"], "output": toy_compiled["output"]}
    scalar_checks = 0
    catalogues = []
    for n in (4, 5):
        base = build_catalog(n)
        folded = build_catalog(n, toy_dag)
        if set(base["truth_to_index"]) != set(folded["truth_to_index"]):
            raise AssertionError("unequal public classes")
        expected = (405, 180) if n == 4 else (8505, 5670)
        if (base["raw_base_programs"], folded["raw_fold_programs"]) != expected:
            raise AssertionError("syntax enumeration count mismatch")
        for cat in (base, folded):
            # Check all retained programs, every input row, via physical gates.
            for row in cat["candidates"]:
                compiled = expand(row["expr"], cat["fold_dag"], n)
                if compiled["nand_gates"] != row["expanded_NANDs"]:
                    raise AssertionError("gate count mismatch")
                for x in range(1 << n):
                    scalar_checks += 1
                    if execute(compiled, x) != ((row["truth"] >> x) & 1):
                        raise AssertionError("scalar/packed discrepancy")
            catalogues.append({"n": n, "fold": cat["fold_dag"] is not None,
                               **cat["catalogue_totals"]})
        # Constructive toy target; this oracle executes programs row by row.
        target = ("XOR", ("AND", ("input", 0), ("input", 1)),
                  ("OR", ("input", 2), ("input", 3)))
        if n == 5:
            target = ("OR", target, ("input", 4))
        target_code = expand(target, n=n)
        for cat in (base, folded):
            def checker(expr):
                code = expand(expr, cat["fold_dag"], n)
                for x in range(1 << n):
                    want = execute(target_code, x)
                    if execute(code, x) != want:
                        return x, want
                return None
            fitted = fit_rule(cat, [(0, execute(target_code, 0))], checker)
            if fitted["status"] != "exact" or fitted["initial_proposal"] is None:
                raise AssertionError("synthetic feedback fit failed")
            if len(fitted["proposals"]) != fitted["checker_failures"] + 1:
                raise AssertionError("feedback accounting discrepancy")
            # All APIs/checkpoints are serializable without a copied fold per AST.
            json.dumps(fitted)
        warmed = build_catalog(n, toy_dag)
        if not warmed["construction"]["catalogue_cache_hit"]:
            raise AssertionError("public cache was not reused")
        if warmed["construction"]["public_packed_NANDs"] != 0:
            raise AssertionError("warm cache reported cold NAND execution")
    for op in OPS:
        compiled = expand((op, ("input", 0), ("input", 1)), n=2)
        expected_cost = {"AND": 2, "OR": 3, "XOR": 4}[op]
        if compiled["nand_gates"] != expected_cost:
            raise AssertionError("primitive NAND cost mismatch")
        for a, b in itertools.product((0, 1), repeat=2):
            expected = {"AND": a & b, "OR": a | b, "XOR": a ^ b}[op]
            if execute(compiled, a | (b << 1)) != expected:
                raise AssertionError("primitive semantics mismatch")
    return {"synthetic_only": True, "status": "passed",
            "scalar_replays": scalar_checks, "catalogues": catalogues,
            "cache": cache_info()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("use --self-test; official task execution is owned by the caller")
    print(json.dumps(self_test(), sort_keys=True))
