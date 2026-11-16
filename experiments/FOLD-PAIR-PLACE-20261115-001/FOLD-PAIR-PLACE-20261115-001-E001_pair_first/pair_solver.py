"""Blind synthesis by exact bottom-up pair contraction, optionally extended once.

Every pair is tested on all outside assignments by four aligned packed
columns. A quotient removes the higher-index input and puts the pair's
answer at its lower index. In the guided search a third input is checked
in that quotient. An admissible extension is exactly a second primitive
whose composition with the certified first one has the supplied truth
table up to pin permutation. No input comes with a known group or role.
"""

from itertools import combinations, permutations
from pathlib import Path
import sys
from time import perf_counter, process_time_ns
from typing import NamedTuple


PREVIOUS = "experiments/FOLD-PLACEMENT-20261115-001/FOLD-PLACEMENT-20261115-001-E001_fixed_inputs"
_previous_dir = Path(__file__).resolve().parents[3] / PREVIOUS
if str(_previous_dir) not in sys.path:
    sys.path.insert(0, str(_previous_dir))
import placement

if Path(placement.__file__).resolve().parent != _previous_dir:
    raise ImportError("pair search requires the frozen placement module")
SOURCE_DEPENDENCIES = (PREVIOUS + "/placement.py", *placement.SOURCE_DEPENDENCIES)
library = placement.library_solver
OPS = library.solver.OPS

PAIR_COUNTERS = (
    "pair_requests", "pair_trials", "pair_failures", "pair_passes", "pair_cache_hits",
    "pair_find_requests", "pair_extension_probe_requests",
    "pair_packed_shifts", "pair_packed_masks", "pair_column_comparisons",
    "pair_cofactor_rows_equivalent", "pair_layout_masks_built", "pair_axis_masks_built",
    "pair_quotient_requests", "pair_quotient_builds", "pair_quotient_cache_hits",
    "pair_quotient_packed_shifts", "pair_quotient_packed_ors", "pair_quotient_packed_masks",
    "extension_requests", "extension_trials", "extension_failures", "extension_passes",
    "extension_cache_hits", "extension_ineligible_pairs", "extension_quotient_failures",
    "pair_atomic_contractions", "pair_guided_contractions", "pair_guided_rebuild_nodes",
    "pair_no_reduction", "pair_extension_recipes_checked", "pair_permuted_entry_bits_read",
)


class _Certificate(NamedTuple):
    op: str
    zero: int
    one: int


def _binary(op, a, b):
    if op == "AND":
        return a & b
    if op == "OR":
        return a | b
    return a ^ b


def _guide(truth):
    """Map two certified operations to the supplied operation's physical pins."""
    oriented = {}
    for order in permutations(range(3)):
        byte = 0
        for row in range(8):
            address = sum(((row >> raw) & 1) << pin for pin, raw in enumerate(order))
            byte |= ((truth >> address) & 1) << row
        oriented.setdefault(byte, order)
    x, y, z = (sum(((row >> pin) & 1) << row for row in range(8)) for pin in range(3))
    recipes = {}
    for inner in OPS:
        for outer in OPS:
            byte = _binary(outer, _binary(inner, x, y), z)
            if byte in oriented:
                recipes.setdefault(inner, {})[outer] = oriented[byte]
    return recipes


class PairSolver(placement.PlacementSolver):
    def __init__(self, n, arm="primitive", entry=None, fold_dag=None,
                 strategy="atomic", trace_limit=32):
        start, cpu = perf_counter(), process_time_ns()
        if strategy == "atomic":
            if arm != "primitive" or entry is not None or fold_dag is not None:
                raise ValueError("atomic pair search uses the primitive library alone")
        elif strategy == "guided":
            if entry is None:
                raise ValueError("guided search requires the public frozen entry")
            if arm == "primitive" and fold_dag is not None:
                raise ValueError("guided primitive reconstruction has no physical macro binding")
        else:
            raise ValueError("unknown pair search strategy")
        # A guidance-only primitive solver validates the same byte and AST as
        # the inline arm, and constructs its own two verified primitive gates.
        init_arm = "flat" if strategy == "guided" and arm == "primitive" else arm
        super().__init__(n, init_arm, entry, fold_dag, "placement",
                         sys.maxsize if trace_limit is None else trace_limit)
        self.reported_arm = arm
        if arm == "primitive":
            self.arm = "primitive"
        self.strategy = strategy
        self._work.update(dict.fromkeys(PAIR_COUNTERS, 0))
        self._recipes = _guide(self.entry_truth) if strategy == "guided" else {}
        if strategy == "guided":
            self._work["pair_extension_recipes_checked"] = len(OPS) ** 2
            self._work["pair_permuted_entry_bits_read"] = 6 * 8
        self._axis_masks = {}
        self._pair_masks = {}
        self._pair_certificates = {}
        self._pair_quotients = {}
        self._extensions = {}
        self._pair_trace = []
        self._extension_trace = []
        self._totals["setup_cpu_ns"] = process_time_ns() - cpu
        self._totals["setup_seconds"] = perf_counter() - start
        self._setup_record.update(cpu_ns=self._totals["setup_cpu_ns"],
                                  seconds=self._totals["setup_seconds"])
        self._setup_record["work"].update({k: self._work[k] for k in
                                          ("pair_extension_recipes_checked", "pair_permuted_entry_bits_read")})

    def _axis_mask(self, k, axis):
        key = (k, axis)
        if key not in self._axis_masks:
            width = 1 << axis
            full = (1 << (1 << k)) - 1
            self._axis_masks[key] = full // ((1 << (2 * width)) - 1) * ((1 << width) - 1)
            self._work["pair_axis_masks_built"] += 1
        return self._axis_masks[key]

    def _pair_test(self, k, truth, pair, purpose):
        work = self._work
        work["pair_requests"] += 1
        work["pair_find_requests" if purpose == "find" else "pair_extension_probe_requests"] += 1
        key = (k, truth, pair)
        cached = key in self._pair_certificates
        if cached:
            work["pair_cache_hits"] += 1
            cert = self._pair_certificates[key]
        else:
            work["pair_trials"] += 1
            i, j = pair
            mask_key = (k, pair)
            if mask_key not in self._pair_masks:
                self._pair_masks[mask_key] = self._axis_mask(k, i) & self._axis_mask(k, j)
                work["pair_layout_masks_built"] += 1
            mask = self._pair_masks[mask_key]
            di, dj = 1 << i, 1 << j
            c00, c10 = truth & mask, (truth >> di) & mask
            c01, c11 = (truth >> dj) & mask, (truth >> (di + dj)) & mask
            work["pair_packed_shifts"] += 3
            work["pair_packed_masks"] += 4
            work["pair_cofactor_rows_equivalent"] += 1 << k
            # All three primitives are commutative, so unequal off-diagonal
            # columns immediately eliminate them all. Reject one-class pairs.
            cert = None
            comparisons = 1
            if c10 == c01:
                comparisons += 2
                same_low, same_high = c10 == c00, c10 == c11
                if same_low and not same_high:
                    cert = _Certificate("AND", c00, c11)
                elif same_high and not same_low:
                    cert = _Certificate("OR", c00, c10)
                elif not same_low and not same_high:
                    comparisons += 1
                    if c00 == c11:
                        cert = _Certificate("XOR", c00, c10)
            work["pair_column_comparisons"] += comparisons
            work["pair_passes" if cert is not None else "pair_failures"] += 1
            self._pair_certificates[key] = cert
        if self.trace_limit and len(self._pair_trace) < self.trace_limit:
            self._pair_trace.append((k, pair[0], pair[1], purpose, None if cert is None else cert.op, cached))
        return cert

    def _quotient(self, k, truth, pair, cert):
        work = self._work
        work["pair_quotient_requests"] += 1
        key = (k, truth, pair)
        if key in self._pair_quotients:
            work["pair_quotient_cache_hits"] += 1
            return self._pair_quotients[key]
        i, j = pair
        # Put the new bit at i with j fixed to zero. Compact the empty
        # intervals caused by j in successively doubled packed blocks.
        result = cert.zero | (cert.one << (1 << i))
        for axis in range(j + 1, k):
            shift = 1 << (axis - 1)
            result = (result | (result >> shift)) & self._axis_mask(k, axis)
        steps = k - j - 1
        work["pair_quotient_packed_shifts"] += steps + 1
        work["pair_quotient_packed_ors"] += steps + 1
        work["pair_quotient_packed_masks"] += steps
        work["pair_quotient_builds"] += 1
        operands = tuple(-1 if a == i else a for a in range(k) if a != j)
        self._pair_quotients[key] = (result, operands)
        return result, operands

    def _extension(self, k, truth, pair, third, quotient, outer_pair, allowed):
        work = self._work
        work["extension_requests"] += 1
        key = (k, truth, pair, third)
        cached = key in self._extensions
        if cached:
            work["extension_cache_hits"] += 1
            accepted, observed = self._extensions[key]
        else:
            work["extension_trials"] += 1
            cert = self._pair_test(k - 1, quotient, outer_pair, "extend")
            observed = None if cert is None else cert.op
            accepted = cert if observed in allowed else None
            work["extension_passes" if accepted is not None else "extension_failures"] += 1
            self._extensions[key] = (accepted, observed)
        if self.trace_limit and len(self._extension_trace) < self.trace_limit:
            self._extension_trace.append((k, pair[0], pair[1], third, observed, accepted is not None, cached))
        return accepted

    def _try_extensions(self, k, truth, pair, cert, quotient, operands):
        work = self._work
        allowed = self._recipes.get(cert.op)
        if not allowed:
            work["extension_ineligible_pairs"] += 1
            return None
        left, right = pair
        for third in range(k):
            if third in pair:
                continue
            # The pair's answer is at left. Dropping right renumbers third.
            z = third - (third > right)
            outer_pair = (left, z) if left < z else (z, left)
            outer_cert = self._extension(k, truth, pair, third, quotient, outer_pair, allowed)
            if outer_cert is None:
                continue
            smaller, outer_operands = self._quotient(k - 1, quotient, outer_pair, outer_cert)
            child = self._solve(k - 2, smaller)
            if child is None:
                work["extension_quotient_failures"] += 1
                continue
            raw = (("input", left), ("input", right), ("input", third))
            if self.reported_arm == "primitive":
                group = (outer_cert.op, (cert.op, raw[0], raw[1]), raw[2])
                work["pair_guided_rebuild_nodes"] += 2
                uses = child[1]
            else:
                order = allowed[outer_cert.op]
                group = ("FOLD", *(raw[index] for index in order))
                uses = child[1] + 1
            args = tuple(group if idx == -1 else ("input", operands[idx]) for idx in outer_operands)
            expr = self._substitute(child[0], args)
            work["pair_guided_contractions"] += 1
            self._event("pair_extended", inputs=k, pair=pair, third=third, first=cert.op, second=outer_cert.op)
            return expr, uses
        return None

    def _search(self, k, truth, hint):
        key = (k, truth)
        full = (1 << (1 << k)) - 1
        if (key in self._success or key in self._failure or k < 2 or
                truth in (0, full) or truth & 1):
            return library.solver.Solver._solve(self, k, truth)
        work = self._work
        work["subproblem_requests"] += 1
        result = None
        for pair in combinations(range(k), 2):
            cert = self._pair_test(k, truth, pair, "find")
            if cert is None:
                continue
            quotient, operands = self._quotient(k, truth, pair, cert)
            if self.strategy == "guided" and k >= 3:
                result = self._try_extensions(k, truth, pair, cert, quotient, operands)
            if result is None:
                child = self._solve(k - 1, quotient)
                if child is not None:
                    group = (cert.op, ("input", pair[0]), ("input", pair[1]))
                    args = tuple(group if i == -1 else ("input", i) for i in operands)
                    result = self._substitute(child[0], args), child[1]
                    work["pair_atomic_contractions"] += 1
                    self._event("pair_atomic", inputs=k, pair=pair, op=cert.op)
            # In a positive read-once formula any exact primitive pair can
            # be grouped by associativity at the lowest common ancestor.
            # If a correct extension failed, the full pair quotient has
            # already been solved (or proved unsupported) by this point.
            break
        else:
            work["pair_no_reduction"] += 1
        if result is None:
            self._failure.add(key)
            work["failed_subproblems_cached"] += 1
        else:
            self._success[key] = result
            work["successful_subproblems_cached"] += 1
        return result

    def _cache_sizes(self):
        record = super()._cache_sizes()
        record.update(pair_axis_masks=len(self._axis_masks), pair_group_masks=len(self._pair_masks),
                      pair_certificates=len(self._pair_certificates), pair_quotients=len(self._pair_quotients),
                      pair_extensions=len(self._extensions))
        return record

    def solve(self, supplied, hint=None):
        if hint is not None:
            raise ValueError("pair-first search accepts no grouping hint")
        self._pair_trace, self._extension_trace = [], []
        before = {key: self._work[key] for key in PAIR_COUNTERS}
        result = super().solve(supplied)
        result["work"].update({key: self._work[key] - before[key] for key in PAIR_COUNTERS})
        result["pair_trace"] = self._pair_trace
        result["extension_trace"] = self._extension_trace
        result["pair_trace_dropped"] = result["work"]["pair_requests"] - len(self._pair_trace)
        result["extension_trace_dropped"] = result["work"]["extension_requests"] - len(self._extension_trace)
        return result
