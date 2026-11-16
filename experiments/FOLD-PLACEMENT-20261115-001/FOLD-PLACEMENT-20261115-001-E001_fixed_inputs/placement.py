"""Infer an intermediate Boolean program and use its output as a later input.

A group's eight assignments are classified by their truth columns over all
outside inputs. Two distinct columns give an exact one-bit intermediate. The
class of the all-zero assignment is named zero. The replacement input occurs
at the lowest public index in the group. Every solver uses this convention.
"""

from itertools import combinations
from pathlib import Path
import sys
from time import perf_counter, process_time_ns


PREVIOUS = "experiments/FOLD-DISCOVERY-20261115-001/FOLD-DISCOVERY-20261115-001-E001_learned_library"
_previous_dir = Path(__file__).resolve().parents[3] / PREVIOUS
if str(_previous_dir) not in sys.path:
    sys.path.insert(0, str(_previous_dir))
import library_solver

if Path(library_solver.__file__).resolve().parent != _previous_dir:
    raise ImportError("placement requires the frozen library solver")
SOURCE_DEPENDENCIES = (PREVIOUS + "/library_solver.py", *library_solver.SOURCE_DEPENDENCIES)
PLACEMENT_COUNTERS = (
    "placement_group_requests", "placement_group_trials", "placement_group_cache_hits",
    "placement_group_failures", "placement_group_passes", "placement_source_bit_reads",
    "placement_packed_shifts", "placement_packed_masks", "placement_packed_column_comparisons",
    "placement_cofactor_rows_equivalent", "placement_layout_mask_terms",
    "placement_quotient_bit_reads", "placement_layouts_built", "placement_layout_entries",
    "placement_inner_failures", "placement_quotient_failures", "placement_contractions",
    "placement_substitution_nodes", "placement_hint_solution_hits", "placement_scan_fallbacks",
    "placement_inline_nodes",
)


def _embeddings(positions):
    values = [0]
    for j in positions:
        values.extend([a | (1 << j) for a in values])
    return tuple(values)


class PlacementSolver(library_solver.LibrarySolver):
    """Arm-local caches. Only the current call's optional group comes from outside."""

    def __init__(self, n, arm="primitive", entry=None, fold_dag=None,
                 strategy="placement", trace_limit=32):
        start, cpu = perf_counter(), process_time_ns()
        if strategy not in ("placement", "direct"):
            raise ValueError("unknown placement strategy")
        super().__init__(n, arm, entry, fold_dag, trace_limit)
        self.reported_arm = arm
        self.strategy = strategy
        # During a library search keep a call node in both arms. This fixes
        # the actual application sites through remapping and substitution.
        # At the final root the flat arm lowers those calls to its exact AST.
        if arm == "flat" and self.entry_expr is not None:
            self.arm = "named"
        self._work.update(dict.fromkeys(PLACEMENT_COUNTERS, 0))
        self._group_layouts = {}
        self._decompositions = {}
        self._hinted_solutions = {}
        self._top_pending = False
        self._direct_primitive = False
        self._hint = self._compact_hint = None
        self._hint_status = "absent"
        self._call_tree = None
        self._hist = None
        self._totals["setup_cpu_ns"] = process_time_ns() - cpu
        self._totals["setup_seconds"] = perf_counter() - start
        self._setup_record.update(cpu_ns=self._totals["setup_cpu_ns"],
                                  seconds=self._totals["setup_seconds"])

    def _input(self, supplied):
        truth, positions, compact = super()._input(supplied)
        if self._hint is not None:
            if all(i in positions for i in self._hint):
                self._compact_hint = tuple(positions.index(i) for i in self._hint)
            else:
                self._hint_status = "contains_irrelevant_input"
        return truth, positions, compact

    def _group_layout(self, k, group):
        key = (k, group)
        if key not in self._group_layouts:
            outside = tuple(i for i in range(k) if i not in group)
            inside_rows, outside_rows = _embeddings(group), _embeddings(outside)
            # Merge group into its lowest position, retaining all outside
            # operands in order. -1 denotes that single derived operand.
            operands = tuple(-1 if i == group[0] else i for i in range(k)
                             if i == group[0] or i not in group)
            slot = operands.index(-1)
            quotient_low = _embeddings(tuple(i for i in range(k - 2) if i != slot))
            mask = 0
            for row in outside_rows:
                mask |= 1 << row
            self._group_layouts[key] = (inside_rows, outside_rows, mask, operands, slot, quotient_low)
            self._work["placement_layouts_built"] += 1
            self._work["placement_layout_entries"] += len(inside_rows) + 2 * len(outside_rows)
            self._work["placement_layout_mask_terms"] += len(outside_rows)
        return self._group_layouts[key]

    def _decompose(self, k, truth, group):
        work = self._work
        key = (k, truth, group)
        work["placement_group_requests"] += 1
        if key in self._decompositions:
            work["placement_group_cache_hits"] += 1
            return self._decompositions[key]
        work["placement_group_trials"] += 1
        inside, outside, mask, operands, slot, low_rows = self._group_layout(k, group)
        # Outside row v has zeros in every group position. Its bit in the
        # aligned column for offset u is truth[v + u] = truth[v | u].
        zero = truth & mask
        one = None
        inner = 0
        probes, comparisons = 1, 0
        result = None
        for assignment, offset in enumerate(inside[1:], 1):
            column = (truth >> offset) & mask
            probes += 1
            comparisons += 1
            if column != zero:
                if one is None:
                    one = column
                else:
                    comparisons += 1
                    if column != one:
                        break
                inner |= 1 << assignment
        else:
            if one is not None:
                quotient = 0
                for row, low in zip(outside, low_rows):
                    quotient |= ((zero >> row) & 1) << low
                    quotient |= ((one >> row) & 1) << (low | (1 << slot))
                work["placement_quotient_bit_reads"] += 2 * len(low_rows)
                result = (inner, quotient, operands)
        work["placement_packed_shifts"] += probes - 1
        work["placement_packed_masks"] += probes
        work["placement_packed_column_comparisons"] += comparisons
        work["placement_cofactor_rows_equivalent"] += probes * len(outside)
        if result is not None:
            work["placement_group_passes"] += 1
        else:
            work["placement_group_failures"] += 1
        self._decompositions[key] = result
        return result

    def _substitute(self, expr, operands):
        self._work["placement_substitution_nodes"] += 1
        if expr[0] == "input":
            return operands[expr[1]]
        if expr[0] == "const":
            return expr
        return (expr[0], *(self._substitute(child, operands) for child in expr[1:]))

    def _contract(self, k, truth, group):
        decomposition = self._decompose(k, truth, group)
        if decomposition is None:
            return None
        inner, quotient, operand_ids = decomposition
        local = self._solve(3, inner)
        if local is None:
            self._work["placement_inner_failures"] += 1
            return None
        outer = self._solve(k - 2, quotient)
        if outer is None:
            self._work["placement_quotient_failures"] += 1
            return None
        inner_expr = self._remap(local[0], group)
        operands = tuple(inner_expr if i == -1 else ("input", i) for i in operand_ids)
        expr = self._substitute(outer[0], operands)
        self._work["placement_contractions"] += 1
        self._event("group", inputs=k, group=group, inner=inner, quotient=quotient)
        return expr, local[1] + outer[1]

    def _search(self, k, truth, hint):
        if hint is not None:
            # A hint never replaces another hint's or the blind path's root program.
            key = (k, truth, hint)
            if key in self._hinted_solutions:
                self._work["placement_hint_solution_hits"] += 1
                result = self._hinted_solutions[key]
            else:
                result = self._contract(k, truth, hint)
                self._hinted_solutions[key] = result
            self._hint_status = "accepted" if result is not None else "rejected"
            if result is not None:
                self._work["subproblem_requests"] += 1
                return result
        key = (k, truth)
        if (self.strategy == "direct" or k <= 3 or truth & 1 or
                key in self._success or key in self._failure):
            return super()._solve(k, truth)
        for group in combinations(range(k), 3):
            if group == hint:
                continue
            result = self._contract(k, truth, group)
            if result is not None:
                self._work["subproblem_requests"] += 1
                self._work["successful_subproblems_cached"] += 1
                self._success[key] = result
                return result
        self._work["placement_scan_fallbacks"] += 1
        return super()._solve(k, truth)

    def _lower_calls(self, node, histogram):
        if node[0] in ("input", "const"):
            return node
        children = tuple(self._lower_calls(child, histogram) for child in node[1:])
        if node[0] == "FOLD":
            count = sum(child[0] not in ("input", "const") for child in children)
            histogram[count] += 1
            if self.reported_arm == "flat":
                self._work["placement_inline_nodes"] += 2
                return library_solver._inline(self.entry_expr, children)
        return (node[0], *children)

    def _solve(self, k, truth):
        if self._direct_primitive:
            return super()._solve(k, truth)
        root = self._top_pending
        self._top_pending = False
        result = self._search(k, truth, self._compact_hint if root else None)
        if root and result is not None and result[1]:
            # At this point every derived operand has its full expression.
            # Keep the annotated tree in compressed essential-input order.
            self._call_tree = result[0]
            expr = self._lower_calls(result[0], self._hist)
            if sum(self._hist) != result[1]:
                raise AssertionError("library call count changed during substitution")
            return expr, result[1]
        return result

    def _cache_sizes(self):
        return {**super()._cache_sizes(), "placement_layouts": len(self._group_layouts),
                "placement_group_certificates": len(self._decompositions),
                "placement_hinted_roots": len(self._hinted_solutions)}

    def ledger(self):
        record = super().ledger()
        record["arm"] = self.reported_arm
        record["strategy"] = self.strategy
        return record

    def solve(self, supplied, hint=None):
        if hint is not None:
            values = tuple(hint)
            if (len(values) != 3 or any(type(i) is not int or not 0 <= i < self.n for i in values)
                    or len(set(values)) != 3):
                raise ValueError("a group must contain three distinct original input indices")
            hint = tuple(sorted(values))
        self._hint, self._compact_hint = hint, None
        self._hint_status = "absent" if hint is None else "pending"
        self._top_pending = True
        self._direct_primitive = self.strategy == "direct" and hint is None and self.arm == "primitive"
        self._call_tree, self._hist = None, [0, 0, 0, 0]
        before = {key: self._work[key] for key in PLACEMENT_COUNTERS}
        try:
            result = super().solve(supplied)
        finally:
            self._top_pending = self._direct_primitive = False
        result["work"].update({key: self._work[key] - before[key] for key in PLACEMENT_COUNTERS})
        result["arm"] = self.reported_arm
        result["strategy"] = self.strategy
        result["hint"] = hint
        result["hint_status"] = self._hint_status
        result["template_computed_arg_histogram"] = self._hist
        result["library_call_tree"] = self._call_tree
        return result
