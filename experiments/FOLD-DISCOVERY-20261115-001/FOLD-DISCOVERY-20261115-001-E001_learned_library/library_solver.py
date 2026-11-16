"""Synthesize with an optional, data-defined three-input primitive composition.

entry['truth'] has bit r for input ((r>>0)&1, (r>>1)&1, (r>>2)&1).
entry['expr'] contains two AND/OR/XOR operations and each input exactly once.
The physical binding can be supplied as fold_dag (or entry['dag']). The
named arm uses that binding and the flat arm substitutes the entry's AST.
"""

from itertools import combinations, permutations
from pathlib import Path
import sys
from time import perf_counter, process_time_ns
from typing import NamedTuple


PREDECESSOR = "experiments/FOLD-DEPTH-20261115-001/FOLD-DEPTH-20261115-001-E001_supplied_fold"
SOURCE_DEPENDENCIES = (PREDECESSOR + "/solver.py", PREDECESSOR + "/peel.py")
_source_dir = Path(__file__).resolve().parents[3] / PREDECESSOR
if str(_source_dir) not in sys.path:
    sys.path.insert(0, str(_source_dir))
import peel
import solver

if any(Path(module.__file__).resolve().parent != _source_dir for module in (peel, solver)):
    raise ImportError("library solver requires the bound predecessor modules")


LIBRARY_COUNTERS = (
    "library_AST_NANDs_compiled", "library_AST_validation_packed_NANDs",
    "library_binding_validation_packed_NANDs", "library_permutations_compiled",
    "library_entry_bits_read", "library_distinct_roles", "library_column_comparisons",
)


class _Role(NamedTuple):
    signature: tuple
    witness: int
    pivot: int
    argument_order: tuple
    checks: tuple


def _primitive_ast(node, leaves):
    if not isinstance(node, (tuple, list)) or not node:
        raise ValueError("a library entry needs a primitive AST")
    if node[0] == "input" and len(node) == 2:
        index = node[1]
        if type(index) is not int or not 0 <= index < 3:
            raise ValueError("template input must be 0, 1 or 2")
        leaves.append(index)
        return "input", index
    if node[0] not in solver.OPS or len(node) != 3:
        raise ValueError("template nodes must be binary AND, OR or XOR")
    return node[0], _primitive_ast(node[1], leaves), _primitive_ast(node[2], leaves)


def _compile_roles(truth):
    """Classify each cofactor as constant 0, NOT(H), H or constant 1.

    Those unary columns have two-bit truth tables 0, 1, 2 and 3. The
    signature orders the raw-variable assignments as 00,10,01,11.
    """
    roles = []
    seen = set()
    for x_pin, y_pin, h_pin in permutations(range(3)):
        signature = []
        for raw in range(4):
            low = ((raw & 1) << x_pin) | ((raw >> 1) << y_pin)
            high = low | (1 << h_pin)
            signature.append(((truth >> low) & 1) | (((truth >> high) & 1) << 1))
        signature = tuple(signature)
        if signature in seen:
            continue
        seen.add(signature)
        # In this grammar every hole is essential, so a nonconstant column
        # exists. Prefer one that gives H directly.
        pivot = signature.index(2) if 2 in signature else signature.index(1)
        witness = sum((signature[j] & 1) << (j - 1) for j in (1, 2, 3))
        pins = (x_pin, y_pin, h_pin)
        order = tuple(pins.index(j) for j in range(3))
        checks = tuple((i, code) for i, code in enumerate(signature) if i != pivot)
        roles.append(_Role(signature, witness, pivot, order, checks))
    # Eligibility and trial order depend only on the function up to a
    # renaming of its formal inputs. argument_order maps a hit back to the
    # supplied physical pins; it never decides which role is tried first.
    roles.sort(key=lambda role: (-sum(code in (1, 2) for code in role.signature),
                                 role.signature))
    return tuple(roles)


def _inline(node, args):
    if node[0] == "input":
        return args[node[1]]
    return node[0], _inline(node[1], args), _inline(node[2], args)


class LibrarySolver(peel.PeelSolver):
    """A frozen single entry and arm-local search, failure and circuit caches."""

    def __init__(self, n, arm="primitive", entry=None, fold_dag=None, trace_limit=32):
        started, cpu = perf_counter(), process_time_ns()
        if arm not in ("primitive", "named", "flat"):
            raise ValueError("unknown library arm")
        # Initialize the shared primitive machinery, bypassing the older
        # named arm's validation of one particular seven-NAND function.
        super().__init__(n, "primitive", None, trace_limit)
        self.arm = arm
        self._work.update(dict.fromkeys(LIBRARY_COUNTERS, 0))
        self.entry_truth = None
        self.entry_expr = None
        self._roles = ()
        if arm != "primitive" and entry is not None:
            truth = entry["truth"]
            if type(truth) is not int or not 0 <= truth < 256:
                raise ValueError("template truth must be an unsigned byte")
            leaves = []
            ast = _primitive_ast(entry["expr"], leaves)
            if sorted(leaves) != [0, 1, 2]:
                raise ValueError("a binary two-operation template must use each of three inputs once")
            circuit = solver.expand(ast, n=3)
            self._work["library_AST_NANDs_compiled"] += len(circuit["gates"])
            self._work["library_AST_validation_packed_NANDs"] += len(circuit["gates"])
            if solver.packed_truth(circuit) != truth:
                raise ValueError("template AST and declared truth byte differ")
            if arm == "named":
                supplied = fold_dag if fold_dag is not None else entry.get("dag")
                if supplied is None:
                    self.fold_dag = {"gates": circuit["gates"], "output": circuit["output"]}
                else:
                    self.fold_dag = solver._dag(supplied)
                    self._work["library_binding_validation_packed_NANDs"] += len(self.fold_dag["gates"])
                    if solver.packed_truth({"inputs": 3, **self.fold_dag}) != truth:
                        raise ValueError("supplied physical template and declared truth byte differ")
            self.entry_truth, self.entry_expr = truth, ast
            self._roles = _compile_roles(truth)
            self._work["library_permutations_compiled"] = 6
            self._work["library_entry_bits_read"] = 6 * 8
            self._work["library_distinct_roles"] = len(self._roles)
        elif arm != "primitive" and fold_dag is not None:
            raise ValueError("a physical binding needs a frozen template")
        self._totals["setup_cpu_ns"] = process_time_ns() - cpu
        self._totals["setup_seconds"] = perf_counter() - started
        self._setup_record = {
            "cpu_ns": self._totals["setup_cpu_ns"], "seconds": self._totals["setup_seconds"],
            "work": {key: self._work[key] for key in LIBRARY_COUNTERS},
            "truth": self.entry_truth, "expr": self.entry_expr,
        }

    def _joint(self, k, truth, singletons):
        if not self._roles:
            return None
        work = self._work
        full = (1 << (1 << (k - 2))) - 1
        for x, y in combinations(range(k), 2):
            work["peel_pair_probes"] += 1
            at_xy = (truth >> ((1 << x) | (1 << y))) & 1
            work["peel_witness_bit_reads"] += 1
            work["factor_truth_bit_reads"] += 1
            witness = singletons[x] | (singletons[y] << 1) | (at_xy << 2)
            columns = None
            for number, role in enumerate(self._roles):
                work["peel_role_probes"] += 1
                work["ternary_placement_tests"] += 1
                if role.witness != witness:
                    work["peel_role_witness_rejections"] += 1
                    work["ternary_placement_failures"] += 1
                    continue
                work["peel_role_column_checks"] += 1
                if columns is None:
                    x0, x1 = self._cofactors(k, truth, x)
                    c00, c01 = self._cofactors(k - 1, x0, y - 1)
                    c10, c11 = self._cofactors(k - 1, x1, y - 1)
                    columns = c00, c10, c01, c11
                residual = columns[role.pivot]
                if role.signature[role.pivot] == 1:
                    residual ^= full
                unary = (0, full ^ residual, residual, full)
                for index, code in role.checks:
                    work["library_column_comparisons"] += 1
                    if columns[index] != unary[code]:
                        break
                else:
                    work["ternary_placement_passes"] += 1
                    self._event("library_pair", inputs=k, x=x, y=y, role=number)
                    child = self._solve(k - 2, residual)
                    if child is None:
                        work["peel_child_failures"] += 1
                        continue
                    positions = tuple(j for j in range(k) if j != x and j != y)
                    operands = (("input", x), ("input", y), self._remap(child[0], positions))
                    args = tuple(operands[i] for i in role.argument_order)
                    if self.arm == "named":
                        expr = ("FOLD", *args)
                        work["AST_nodes_built"] += 3
                    else:
                        expr = _inline(self.entry_expr, args)
                        work["AST_nodes_built"] += 4
                    return expr, child[1] + 1
                work["ternary_placement_failures"] += 1
        return None

    def solve(self, supplied):
        first = self._totals["solve_calls"] == 0
        before = {key: self._work[key] for key in LIBRARY_COUNTERS}
        result = super().solve(supplied)
        result["work"].update({key: self._work[key] - before[key] for key in LIBRARY_COUNTERS})
        result["library_setup"] = self._setup_record if first else None
        return result


def check_pin_renaming():
    """Synthetic regression: all formal pin orders must schedule identical searches."""
    pins = tuple(("input", i) for i in range(3))
    raw = (pins[0], pins[1], ("OR", pins[2], ("input", 3)))
    checked = 0
    for outer in solver.OPS:
        for inner in solver.OPS:
            template = (outer, (inner, pins[0], pins[1]), pins[2])
            targets = [solver.packed_truth(solver.expand(_inline(template, args), n=4))
                       for args in permutations(raw)]
            # Four-variable majority-of-first-three is outside the read-once grammar.
            targets.append(sum(((row & 7).bit_count() >= 2) << row for row in range(16)))
            for arm in ("named", "flat"):
                reference = None
                for perm in permutations(pins):
                    renamed = _inline(template, perm)
                    byte = solver.packed_truth(solver.expand(renamed, n=3))
                    engine = LibrarySolver(4, arm, {"truth": byte, "expr": renamed})
                    schedule = [tuple(role.signature for role in engine._roles)]
                    for t in targets:
                        result = engine.solve(t)
                        if result["circuit"] is not None:
                            scalar = sum(solver.execute(result["circuit"], x) << x for x in range(16))
                            if scalar != t:
                                raise AssertionError("permuted physical template disagrees with labels")
                        work = result["work"]
                        steps = {key: value for key, value in work.items()
                                 if key.startswith(("peel_", "binary_", "ternary_", "subproblem_"))
                                 or key in ("factor_truth_bit_reads", "library_column_comparisons")}
                        schedule.append((result["status"], result["trace"], result["template_uses"], steps))
                        checked += 1
                    if reference is not None and schedule != reference:
                        raise AssertionError("formal pin names change the semantic trial schedule")
                    reference = schedule
    return checked
