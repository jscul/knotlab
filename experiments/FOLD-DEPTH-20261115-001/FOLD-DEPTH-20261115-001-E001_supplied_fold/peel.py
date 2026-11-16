"""Directly recognize two raw leaves and an unknown function in one search step.

For a pair x,y, let the four columns be T00,T10,T01,T11 in that order.
The three possible roles in (A AND B) XOR C give respectively
(H,H,H,~H), (0,H,1,~H), and (0,1,H,~H). Here H is a complete function of
the remaining variables. Its tree and its leaf positions are unknown.
The competitors receive the same public table, raw-leaf order and physical
checker. Each also has a complete memoized primitive split fallback.
"""

from itertools import combinations
from time import perf_counter

from solver import OPS, Solver


PEEL_COUNTERS = (
    "peel_pair_probes", "peel_role_probes", "peel_role_witness_rejections",
    "peel_role_column_checks", "peel_single_op_probes",
    "peel_single_witness_rejections", "peel_single_column_checks",
    "peel_cofactor_requests", "peel_cofactor_hits", "peel_cofactor_misses",
    "peel_cofactor_bit_reads", "peel_witness_bit_reads",
    "peel_index_tables_built", "peel_index_row_pairs",
    "peel_child_failures", "peel_general_fallbacks",
)
# [truth on x alone][truth on y alone] when truth on both raw inputs is one.
ROLE_AT_ZERO = ((0, 1), (2, -1))


class PeelSolver(Solver):
    """Use one engine per arm with the same cache lifetime as Solver."""

    def __init__(self, n, arm="primitive", fold_dag=None, trace_limit=32):
        started = perf_counter()
        super().__init__(n, arm, fold_dag, trace_limit)
        self._work.update(dict.fromkeys(PEEL_COUNTERS, 0))
        self._section_layouts = {}
        self._sections = {}
        self._totals["setup_seconds"] = perf_counter() - started

    def _cofactors(self, k, truth, variable):
        """Compact both sections in increasing order of the remaining inputs."""
        work = self._work
        work["peel_cofactor_requests"] += 1
        key = (k, truth, variable)
        if key in self._sections:
            work["peel_cofactor_hits"] += 1
            return self._sections[key]
        work["peel_cofactor_misses"] += 1
        layout_key = (k, variable)
        if layout_key not in self._section_layouts:
            delta = 1 << variable
            source_masks = []
            for dest in range(1 << (k - 1)):
                low = (dest & (delta - 1)) | ((dest >> variable) << (variable + 1))
                source_masks.append((1 << low, 1 << (low | delta), 1 << dest))
            self._section_layouts[layout_key] = source_masks
            work["peel_index_tables_built"] += 1
            work["peel_index_row_pairs"] += len(source_masks)
        low = high = 0
        for low_mask, high_mask, dest_mask in self._section_layouts[layout_key]:
            if truth & low_mask:
                low |= dest_mask
            if truth & high_mask:
                high |= dest_mask
        work["peel_cofactor_bit_reads"] += 1 << k
        work["factor_truth_bit_reads"] += 1 << k
        self._sections[key] = low, high
        return low, high

    def _joint(self, k, truth, singletons):
        work = self._work
        full = (1 << (1 << (k - 2))) - 1
        for x, y in combinations(range(k), 2):
            work["peel_pair_probes"] += 1
            # At residual input zero, H=0. These actual public label reads
            # cheaply reject impossible roles before collecting whole columns.
            at_xy = (truth >> ((1 << x) | (1 << y))) & 1
            work["peel_witness_bit_reads"] += 1
            work["factor_truth_bit_reads"] += 1
            eligible_role = ROLE_AT_ZERO[singletons[x]][singletons[y]] if at_xy else -1
            for role in range(3):
                work["peel_role_probes"] += 1
                work["ternary_placement_tests"] += 1
                if role != eligible_role:
                    work["peel_role_witness_rejections"] += 1
                    work["ternary_placement_failures"] += 1
                    continue
                work["peel_role_column_checks"] += 1
                x0, x1 = self._cofactors(k, truth, x)
                # Removing x shifts the position of y down by one.
                c00, c01 = self._cofactors(k - 1, x0, y - 1)
                c10, c11 = self._cofactors(k - 1, x1, y - 1)
                if role == 0:
                    residual = c00
                    matches = c10 == c01 == c00 and c11 == (full ^ c00)
                elif role == 1:
                    residual = c10
                    matches = c00 == 0 and c01 == full and c11 == (full ^ c10)
                else:
                    residual = c01
                    matches = c00 == 0 and c10 == full and c11 == (full ^ c01)
                if not matches:
                    work["ternary_placement_failures"] += 1
                    continue
                work["ternary_placement_passes"] += 1
                self._event("direct_pair", inputs=k, x=x, y=y, role=role)
                child = self._solve(k - 2, residual)
                if child is None:
                    work["peel_child_failures"] += 1
                    continue
                positions = tuple(j for j in range(k) if j != x and j != y)
                h = self._remap(child[0], positions)
                left, right = ("input", x), ("input", y)
                if role == 0:
                    args = left, right, h
                elif role == 1:
                    args = left, h, right
                else:
                    args = right, h, left
                if self.arm == "named":
                    expr = ("FOLD", *args)
                    work["AST_nodes_built"] += 3
                else:
                    a, b, c = args
                    expr = ("XOR", ("AND", a, b), c)
                    work["AST_nodes_built"] += 4
                return expr, child[1] + 1
        return None

    def _single(self, k, truth, singletons):
        work = self._work
        full = (1 << (1 << (k - 1))) - 1
        for variable in range(k):
            sections = None
            for op in OPS:
                work["peel_single_op_probes"] += 1
                work["binary_placement_requests"] += 1
                work["binary_placement_trials"] += 1
                if singletons[variable] != int(op != "AND"):
                    work["peel_single_witness_rejections"] += 1
                    work["binary_placement_failures"] += 1
                    continue
                work["peel_single_column_checks"] += 1
                if sections is None:
                    sections = self._cofactors(k, truth, variable)
                low, high = sections
                if op == "AND":
                    matches, residual = low == 0, high
                elif op == "OR":
                    matches, residual = high == full, low
                else:
                    matches, residual = high == (full ^ low), low
                if not matches:
                    work["binary_placement_failures"] += 1
                    continue
                work["binary_placement_passes"] += 1
                child = self._solve(k - 1, residual)
                if child is None:
                    work["peel_child_failures"] += 1
                    continue
                self._event("direct_single", inputs=k, variable=variable, op=op)
                positions = tuple(j for j in range(k) if j != variable)
                work["AST_nodes_built"] += 2
                return (op, ("input", variable), self._remap(child[0], positions)), child[1]
        return None

    def _fallback(self, k, truth):
        """Same general primitive split routine in all arms, on the same memo."""
        self._work["peel_general_fallbacks"] += 1
        # A nonconstant zero-preserving one-input factor must be the
        # input itself. Every such split already failed in _single.
        for group in self._groups(k):
            if group.bit_count() == 1:
                continue
            for op in OPS:
                cert = self._probe(k, truth, group, op)
                if cert is not None:
                    result = self._join_binary(k, truth, cert)
                    if result is not None:
                        return result
        return None

    def _solve(self, k, truth):
        key = (k, truth)
        full = (1 << (1 << k)) - 1
        # Share the base cases, positive/negative memo receipts and all
        # physical operations with the original solver.
        if (key in self._success or key in self._failure or k < 2 or
                truth in (0, full) or truth & 1):
            return super()._solve(k, truth)
        self._work["subproblem_requests"] += 1
        singletons = tuple((truth >> (1 << j)) & 1 for j in range(k))
        self._work["peel_witness_bit_reads"] += k
        self._work["factor_truth_bit_reads"] += k
        result = None
        if self.arm != "primitive" and k >= 3:
            result = self._joint(k, truth, singletons)
        if result is None:
            result = self._single(k, truth, singletons)
        if result is None:
            result = self._fallback(k, truth)
        if result is None:
            self._failure.add(key)
            self._work["failed_subproblems_cached"] += 1
        else:
            self._success[key] = result
            self._work["successful_subproblems_cached"] += 1
        return result

    def _cache_sizes(self):
        return {**super()._cache_sizes(), "peel_cofactor_layouts": len(self._section_layouts),
                "peel_cofactor_pairs": len(self._sections)}

    def solve(self, supplied):
        before = {name: self._work[name] for name in PEEL_COUNTERS}
        result = super().solve(supplied)
        result["work"].update({name: self._work[name] - before[name] for name in PEEL_COUNTERS})
        return result
