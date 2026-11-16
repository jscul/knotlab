"""Lazy public semantic index and on-demand physical program search.

The supplied primitive class is read-once AND/OR/XOR on all n inputs.  A
separate optional catalogue contains exactly one call to a supplied archived
seven-NAND ternary circuit.  Indexing stores only integer Boolean columns;
no output ASTs, derivation backpointers, or physical programs are built until
selected.  The lower median is by ascending DISTINCT integer truth column.

This module receives labeled rows only.  It has no task source, target table,
private verifier, data schedule, training gate, or feedback loop.  A fresh
new_task() state incrementally filters each explicitly supplied row prefix.
Backend-local persistent caches contain public hypotheses/row indexes and
on-demand ASTs, physical circuits and physically validated output columns.

AST and physical address conventions are the frozen FOLD-REUSE conventions:
('input',j), ('AND'|'OR'|'XOR',A,B), ('FOLD',A,B,C).  A shared local fold DAG
uses arguments0..2, constants0/1 at3/4, NAND gate k at5+k.  Compiled programs
use n input addresses, constants n/n+1, NAND gate k at n+2+k.  The pinned
compiler expands AND/OR/XOR to2/3/4 NANDs without global CSE, and inlines all
seven archived gates.  Public factorization recovers ASTs; inference executes
their actual NAND gates, never a replacement formula for the fold.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import pickle
import time


SCHEMA_VERSION = 1
PRIMITIVE_SHA256 = "7058a42e3e66d15191a3b5359c48c671a7fb63a1e8ad7dfaa172e35de617fe92"
PRIMITIVE_RELATIVE = (
    "experiments/FOLD-REUSE-20261115-001/"
    "FOLD-REUSE-20261115-001-E001_second_learner/learner.py"
)
OPS = ("AND", "OR", "XOR")
COUNTERS = (
    "source_bytes_hashed", "source_modules_loaded", "input_column_bit_reads",
    "task_states_created", "example_rows_validated", "constraint_bitset_ops",
    "primitive_semantic_requests", "primitive_semantic_cache_hits",
    "primitive_subsets_built", "primitive_semantic_join_results",
    "primitive_semantic_duplicates", "primitive_semantic_values_retained",
    "fold_semantic_requests", "fold_semantic_cache_hits", "fold_subsets_built",
    "fold_root_join_results", "fold_binary_join_results",
    "fold_semantic_duplicates", "fold_semantic_values_retained",
    "fold_semantic_packed_NANDs", "fold_class_guards",
    "semantic_sorts", "semantic_values_sorted",
    "row_bitsets_built", "row_bitset_truth_tests", "row_bitset_one_writes",
    "row_bitset_bytes_allocated", "candidate_calls", "default_candidate_calls",
    "fold_candidate_calls", "empty_fold_selections", "median_popcounts",
    "median_word_ops", "materialization_requests", "materialization_cache_hits",
    "primitive_ASTs_built", "fold_ASTs_built", "AST_cache_hits",
    "factor_requests", "factor_memo_hits", "cofactor_calls",
    "cofactor_truth_tests", "cofactor_broadcast_ors", "broadcast_rows_indexed",
    "reconstruction_partitions_tested", "reconstruction_binary_checks",
    "reconstruction_binary_results",
    "reconstruction_fold_checks", "reconstruction_fold_packed_NANDs",
    "physical_programs_compiled", "physical_NANDs_compiled",
    "physical_programs_validated", "validation_packed_NANDs", "pickle_restores",
    "validation_scalar_equivalent_NANDs", "fold_guard_packed_NANDs",
)


def _int(value, name):
    if type(value) is not int:
        raise ValueError(f"{name} must be an integer")
    return value


def _subsets(mask):
    result = []
    sub = mask
    while sub:
        result.append(sub)
        sub = (sub - 1) & mask
    return tuple(reversed(result))


def _binary(op, a, b):
    return (op, a, b) if a <= b else (op, b, a)


class _TaskState:
    __slots__ = ("owner", "rows", "eligible", "processed")

    def __init__(self, owner):
        self.owner = owner
        self.rows = ()
        self.eligible = {}
        self.processed = {}


class SearchBackend:
    """One arm's independent lazy caches and work ledger; no target access.

    ``default_candidate(examples,state=None)`` always emits a primitive-only
    program. ``fold_candidate(...)`` uses the lower median of the exactly-one
    FOLD subset, or None when absent/empty.  The caller alone controls whether
    and when the optional route is tried.  Use one new_task() per rule and the
    SAME state for its routes if incremental prefix filtering is desired.
    Returned expr/circuit objects are backend-owned cache records: callers
    may serialize/replay them but must not mutate them.
    """

    def __init__(self, n=6, fold_dag=None):
        started = time.perf_counter()
        self.n = _int(n, "n")
        if n not in (5, 6):
            raise ValueError("the frozen backend supports n=5 or n=6")
        self.rows = 1 << n
        self.full = (1 << self.rows) - 1
        self.mask = (1 << n) - 1
        self._work = {name: 0 for name in COUNTERS}
        self._seconds = {"setup_seconds": 0.0, "candidate_seconds": 0.0,
                         "restore_seconds": 0.0}
        self._owner = object()
        self._load_primitive()
        self.fold_dag = self._primitive._canonical_dag(fold_dag)
        if self.fold_dag is not None and len(self.fold_dag["gates"]) != 7:
            raise ValueError("the inherited physical fold must have exactly seven NANDs")
        self.fold_sha256 = None if self.fold_dag is None else hashlib.sha256(
            json.dumps(self.fold_dag, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        self._inputs = tuple(sum(((x >> j) & 1) << x for x in range(self.rows))
                             for j in range(n))
        self._work["input_column_bit_reads"] += n * self.rows
        self._base = {}                  # mask -> (sorted truth columns, membership set)
        self._fold = {}
        self._partitions = {}
        self._tripartitions = {}
        self._broadcasts = {}
        self._row_indexes = {}           # (route,input row) -> hypothesis membership bits
        self._asts = {}                  # only selected subprograms: (route,mask,truth)
        self._programs = {}              # only selected complete physical programs
        self._fold_guard_done = False
        self._seconds["setup_seconds"] = time.perf_counter() - started

    def _load_primitive(self):
        source = Path(__file__).resolve().parents[3] / PRIMITIVE_RELATIVE
        content = source.read_bytes()
        self._work["source_bytes_hashed"] += len(content)
        if hashlib.sha256(content).hexdigest() != PRIMITIVE_SHA256:
            raise RuntimeError("immutable primitive compiler SHA256 mismatch")
        spec = importlib.util.spec_from_file_location("fold_gate_pinned_primitive", source)
        self._primitive = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self._primitive)
        self._work["source_modules_loaded"] += 1

    def __getstate__(self):
        state = dict(self.__dict__)
        state.pop("_primitive")   # executable code is immutable, not a learned cache
        return state

    def __setstate__(self, state):
        started = time.perf_counter()
        self.__dict__.update(state)
        self._load_primitive()
        self._work["pickle_restores"] += 1
        self._seconds["restore_seconds"] += time.perf_counter() - started

    def new_task(self):
        """Fresh task-facing state; previous labels are never inherited."""
        self._work["task_states_created"] += 1
        return _TaskState(self._owner)

    def _parts(self, mask):
        if mask not in self._partitions:
            low = mask & -mask
            self._partitions[mask] = tuple(
                (left, mask ^ left) for left in _subsets(mask)
                if left != mask and left & low
            )
        return self._partitions[mask]

    def _triples(self, mask):
        if mask not in self._tripartitions:
            self._tripartitions[mask] = tuple(
                (a, b, mask ^ a ^ b)
                for a in _subsets(mask) if a != mask
                for b in _subsets(mask ^ a) if b != (mask ^ a)
            )
        return self._tripartitions[mask]

    def _base_values(self, mask):
        self._work["primitive_semantic_requests"] += 1
        if mask in self._base:
            self._work["primitive_semantic_cache_hits"] += 1
            return self._base[mask]
        if mask.bit_count() == 1:
            out = {self._inputs[mask.bit_length() - 1]}
            attempts = 1
        else:
            out, attempts = set(), 0
            for left, right in self._parts(mask):
                ls = self._base_values(left)[0]
                rs = self._base_values(right)[0]
                for a in ls:
                    for b in rs:
                        out.add(a & b)
                        out.add(a | b)
                        out.add(a ^ b)
                attempts += 3 * len(ls) * len(rs)
            self._work["primitive_semantic_join_results"] += attempts
        ordered = tuple(sorted(out))
        self._base[mask] = (ordered, frozenset(out))
        self._work["primitive_subsets_built"] += 1
        self._work["primitive_semantic_values_retained"] += len(out)
        self._work["primitive_semantic_duplicates"] += attempts - len(out)
        self._work["semantic_sorts"] += 1
        self._work["semantic_values_sorted"] += len(out)
        return self._base[mask]

    def _fold_eval(self, a, b, c):
        values = [a, b, c, 0, self.full]
        for left, right in self.fold_dag["gates"]:
            values.append(self.full ^ (values[left] & values[right]))
        return values[self.fold_dag["output"]]

    def _guard_fold_class(self):
        if not self._fold_guard_done:
            value = self._fold_eval(*self._inputs[:3])
            if value not in self._base_values(7)[1]:
                raise ValueError("inherited fold is outside the supplied base class")
            self._work["fold_class_guards"] += 1
            self._work["fold_guard_packed_NANDs"] += 7
            self._fold_guard_done = True

    def _fold_values(self, mask):
        self._work["fold_semantic_requests"] += 1
        if mask in self._fold:
            self._work["fold_semantic_cache_hits"] += 1
            return self._fold[mask]
        if self.fold_dag is None or mask.bit_count() < 3:
            self._fold[mask] = ((), frozenset())
            return self._fold[mask]
        self._guard_fold_class()
        out, root_attempts, binary_attempts = set(), 0, 0
        for a_mask, b_mask, c_mask in self._triples(mask):
            aa = self._base_values(a_mask)[0]
            bb = self._base_values(b_mask)[0]
            cc = self._base_values(c_mask)[0]
            for a in aa:
                for b in bb:
                    for c in cc:
                        out.add(self._fold_eval(a, b, c))
            root_attempts += len(aa) * len(bb) * len(cc)
        for left, right in self._parts(mask):
            for ls, rs in ((self._fold_values(left)[0], self._base_values(right)[0]),
                           (self._base_values(left)[0], self._fold_values(right)[0])):
                for a in ls:
                    for b in rs:
                        out.add(a & b)
                        out.add(a | b)
                        out.add(a ^ b)
                binary_attempts += 3 * len(ls) * len(rs)
        if not out.issubset(self._base_values(mask)[1]):
            raise AssertionError("fold altered primitive hypothesis expressivity")
        self._fold[mask] = (tuple(sorted(out)), frozenset(out))
        self._work["fold_subsets_built"] += 1
        self._work["fold_root_join_results"] += root_attempts
        self._work["fold_binary_join_results"] += binary_attempts
        self._work["fold_semantic_packed_NANDs"] += 7 * root_attempts
        self._work["fold_semantic_duplicates"] += root_attempts + binary_attempts - len(out)
        self._work["fold_semantic_values_retained"] += len(out)
        self._work["semantic_sorts"] += 1
        self._work["semantic_values_sorted"] += len(out)
        return self._fold[mask]

    def _values(self, route):
        return (self._base_values if route == "default" else self._fold_values)(self.mask)[0]

    def _normalize(self, examples):
        rows, seen = [], {}
        for item in examples:
            self._work["example_rows_validated"] += 1
            if not isinstance(item, (tuple, list)) or len(item) != 2:
                raise ValueError("examples must contain (input_integer,label_bit) pairs")
            x = _int(item[0], "example input")
            label = item[1]
            if type(label) not in (int, bool) or label not in (0, 1):
                raise ValueError("example label must be a literal bit")
            if not 0 <= x < self.rows:
                raise ValueError("example input outside declared register")
            label = int(label)
            if x in seen and seen[x] != label:
                raise ValueError("conflicting labels")
            if x not in seen:
                rows.append((x, label))
                seen[x] = label
        return tuple(rows)

    def _row_bits(self, route, x, values):
        key = (route, x)
        if key not in self._row_indexes:
            packed = bytearray((len(values) + 7) // 8)
            writes = 0
            for j, truth in enumerate(values):
                if (truth >> x) & 1:
                    packed[j >> 3] |= 1 << (j & 7)
                    writes += 1
            self._row_indexes[key] = int.from_bytes(packed, "little")
            self._work["row_bitsets_built"] += 1
            self._work["row_bitset_truth_tests"] += len(values)
            self._work["row_bitset_one_writes"] += writes
            self._work["row_bitset_bytes_allocated"] += len(packed)
        return self._row_indexes[key]

    def _eligible(self, route, examples, state):
        values = self._values(route)
        rows = self._normalize(examples)
        if state is None:
            state = self.new_task()
        if not isinstance(state, _TaskState) or state.owner is not self._owner:
            raise ValueError("prefix state belongs to another backend")
        if len(rows) < len(state.rows) or rows[:len(state.rows)] != state.rows:
            raise ValueError("task state requires an unchanged growing row prefix")
        state.rows = rows
        all_hypotheses = (1 << len(values)) - 1
        eligible = state.eligible.get(route, all_hypotheses)
        processed = state.processed.get(route, 0)
        for x, label in rows[processed:]:
            bits = self._row_bits(route, x, values)
            eligible &= bits if label else (all_hypotheses ^ bits)
            self._work["constraint_bitset_ops"] += 1 if label else 2
        state.eligible[route] = eligible
        state.processed[route] = len(rows)
        return values, eligible

    def _median(self, bits):
        count = bits.bit_count()
        self._work["median_popcounts"] += 1
        rank, offset = (count - 1) // 2, 0
        while bits.bit_length() > 64:
            cut = bits.bit_length() // 2
            lower = bits & ((1 << cut) - 1)
            low_count = lower.bit_count()
            self._work["median_popcounts"] += 1
            self._work["median_word_ops"] += 3
            if rank < low_count:
                bits = lower
            else:
                bits >>= cut
                offset += cut
                rank -= low_count
                self._work["median_word_ops"] += 1
        while rank:
            bits &= bits - 1
            rank -= 1
            self._work["median_word_ops"] += 2
        return offset + (bits & -bits).bit_length() - 1, count

    def _cofactor(self, truth, group, fixed):
        if group not in self._broadcasts:
            columns = {assignment: 0 for assignment in (0,) + _subsets(group)}
            for x in range(self.rows):
                columns[x & group] |= 1 << x
            self._broadcasts[group] = tuple(sorted(columns.items()))
            self._work["broadcast_rows_indexed"] += self.rows
        result = 0
        for assignment, column in self._broadcasts[group]:
            self._work["cofactor_truth_tests"] += 1
            if (truth >> (assignment | fixed)) & 1:
                result |= column
                self._work["cofactor_broadcast_ors"] += 1
        self._work["cofactor_calls"] += 1
        return result

    def _factor(self, truth, group, parent, memo):
        self._work["factor_requests"] += 1
        key = (truth, group, parent)
        if key in memo:
            self._work["factor_memo_hits"] += 1
            return memo[key]
        # All supplied primitives are zero-preserving.  For a true disjoint
        # functional factor, any nonconstant unary section is its child or
        # its complement. Normalizing the all-zero row recovers that child.
        # Composition is always checked afterward, so a spurious section of
        # a nonfactorable partition cannot introduce an incorrect program.
        for fixed in (0,) + _subsets(parent ^ group):
            section = self._cofactor(truth, group, fixed)
            if section not in (0, self.full):
                if section & 1:
                    section ^= self.full
                memo[key] = section
                return section
        memo[key] = None
        return None

    def _ast(self, route, mask, truth, memo):
        key = (route, mask, truth)
        if key in self._asts:
            self._work["AST_cache_hits"] += 1
            return self._asts[key]
        if route == "default" and mask.bit_count() == 1:
            expr = ("input", mask.bit_length() - 1)
            if truth != self._inputs[expr[1]]:
                raise AssertionError("invalid primitive leaf")
        else:
            expr = self._find_ast(route, mask, truth, memo)
        self._asts[key] = expr
        self._work["primitive_ASTs_built" if route == "default" else "fold_ASTs_built"] += 1
        return expr

    def _find_ast(self, route, mask, truth, memo):
        if route == "fold":
            for aa, bb, cc in self._triples(mask):
                self._work["reconstruction_partitions_tested"] += 1
                a = self._factor(truth, aa, mask, memo)
                b = self._factor(truth, bb, mask, memo)
                c = self._factor(truth, cc, mask, memo)
                if (a not in self._base_values(aa)[1]
                        or b not in self._base_values(bb)[1]
                        or c not in self._base_values(cc)[1]):
                    continue
                self._work["reconstruction_fold_checks"] += 1
                self._work["reconstruction_fold_packed_NANDs"] += 7
                if self._fold_eval(a, b, c) == truth:
                    return ("FOLD", self._ast("default", aa, a, memo),
                            self._ast("default", bb, b, memo),
                            self._ast("default", cc, c, memo))
        for left, right in self._parts(mask):
            self._work["reconstruction_partitions_tested"] += 1
            a = self._factor(truth, left, mask, memo)
            b = self._factor(truth, right, mask, memo)
            types = (("default", "default"),) if route == "default" else (
                ("fold", "default"), ("default", "fold"))
            for a_type, b_type in types:
                a_set = (self._base_values if a_type == "default" else self._fold_values)(left)[1]
                b_set = (self._base_values if b_type == "default" else self._fold_values)(right)[1]
                if a not in a_set or b not in b_set:
                    continue
                self._work["reconstruction_binary_results"] += 3
                for op, result in (("AND", a & b), ("OR", a | b), ("XOR", a ^ b)):
                    self._work["reconstruction_binary_checks"] += 1
                    if result == truth:
                        return _binary(op, self._ast(a_type, left, a, memo),
                                       self._ast(b_type, right, b, memo))
        raise AssertionError("public semantic value lacked an on-demand derivation")

    def _program(self, route, truth):
        self._work["materialization_requests"] += 1
        key = (route, truth)
        if key in self._programs:
            self._work["materialization_cache_hits"] += 1
            return self._programs[key]
        expr = self._ast(route, self.mask, truth, {})
        circuit = self._primitive.expand(expr, self.fold_dag, self.n)
        if circuit["macro_uses"] != int(route == "fold"):
            raise AssertionError("incorrect number of inherited calls")
        # This independently executes the compiled representation on public
        # input columns.  The semantic index alone never certifies a circuit.
        values = list(self._inputs) + [0, self.full]
        for left, right in circuit["gates"]:
            values.append(self.full ^ (values[left] & values[right]))
        physical_truth = values[circuit["output"]]
        if physical_truth != truth:
            raise AssertionError("physical circuit disagrees with semantic index")
        cost = len(circuit["gates"])
        self._work["physical_programs_compiled"] += 1
        self._work["physical_NANDs_compiled"] += cost
        self._work["physical_programs_validated"] += 1
        self._work["validation_packed_NANDs"] += cost
        self._work["validation_scalar_equivalent_NANDs"] += cost * self.rows
        record = {"truth": physical_truth, "expr": expr, "circuit": circuit,
                  "expanded_NANDs": cost, "macro_uses": circuit["macro_uses"],
                  "underlying_ops": dict(circuit["underlying_ops"])}
        self._programs[key] = record
        return record

    def _candidate(self, route, examples, state):
        started = time.perf_counter()
        before = dict(self._work)
        self._work["candidate_calls"] += 1
        self._work[f"{route}_candidate_calls"] += 1
        values, bits = self._eligible(route, examples, state)
        if not bits:
            if route == "default":
                raise ValueError("no primitive hypothesis is consistent with received labels")
            self._work["empty_fold_selections"] += 1
            self._seconds["candidate_seconds"] += time.perf_counter() - started
            return None
        index, count = self._median(bits)
        physical_cache_hit = (route, values[index]) in self._programs
        program = self._program(route, values[index])
        elapsed = time.perf_counter() - started
        self._seconds["candidate_seconds"] += elapsed
        return {
            **program, "route": route, "candidate_index": index,
            "consistent_hypotheses": count,
            "physical_cache_hit": physical_cache_hit,
            "verified_truth_cache_hit": physical_cache_hit,
            "work": {k: self._work[k] - before[k] for k in COUNTERS},
            "elapsed_seconds": elapsed,
        }

    def default_candidate(self, examples, state=None):
        """Exact lower median of primitive semantics, primitive physical AST."""
        return self._candidate("default", examples, state)

    def fold_candidate(self, examples, state=None):
        """Exact lower median of the one-FOLD subset, or None; never switches."""
        return self._candidate("fold", examples, state)

    def work_counters(self):
        """Return a lightweight copy of cumulative integer work counts."""
        return dict(self._work)

    def ledger(self):
        """Cumulative actual counts and retained public state, per backend.

        Semantic AND/OR/XOR join counts are indexing work, not physical NAND
        executions. Actual saved-DAG indexing, materialization validation,
        and external verifier work are distinct.  The external verifier and
        common feedback schedule are owned/timed by the caller, not here.
        """
        return {
            "schema_version": SCHEMA_VERSION, "n": self.n,
            "primitive_source_sha256": PRIMITIVE_SHA256,
            "fold_dag_sha256": self.fold_sha256,
            "counters": dict(self._work), "timing": dict(self._seconds),
            "cache": {
                "primitive_semantic_subsets": len(self._base),
                "primitive_semantic_values": sum(len(v[0]) for v in self._base.values()),
                "primitive_full_functions": len(self._base.get(self.mask, ((),))[0]),
                "fold_semantic_subsets": len(self._fold),
                "fold_semantic_values": sum(len(v[0]) for v in self._fold.values()),
                "fold_full_functions": len(self._fold.get(self.mask, ((),))[0]),
                "row_bitsets": len(self._row_indexes),
                "AST_nodes_materialized": len(self._asts),
                "physical_programs": len(self._programs),
                "physical_NANDs_retained": self._work["physical_NANDs_compiled"],
                "physically_verified_columns": len(self._programs),
            },
        }


def self_test():
    """Synthetic/public-class checks only; this function imports no panel."""
    setup = SearchBackend(5)
    toy = ("OR", ("XOR", ("input", 0), ("input", 1)), ("input", 2))
    compiled = setup._primitive.expand(toy, n=3)
    dag = {"gates": compiled["gates"], "output": compiled["output"]}
    if len(dag["gates"]) != 7:
        raise AssertionError("toy fixture cost mismatch")
    summaries, replayed = [], 0
    for n, expected in ((5, 3933), (6, 81819)):
        back = SearchBackend(n, dag)
        first = back.default_candidate([])
        fold = back.fold_candidate([])
        if len(back._base[back.mask][0]) != expected:
            raise AssertionError("public semantic count discrepancy")
        for candidate in (first, fold):
            if candidate is None:
                raise AssertionError("missing synthetic fold candidate")
            scalar = sum(back._primitive.execute(candidate["circuit"], x) << x
                         for x in range(1 << n))
            if scalar != candidate["truth"]:
                raise AssertionError("physical scalar/packed disagreement")
            replayed += 1 << n
        # Explicit toy target and supplied prefixes, never a hidden stream.
        target = ("AND", ("XOR", ("input", 0), ("input", 1)),
                  ("OR", ("input", 2), ("input", 3)))
        for j in range(4, n):
            target = ("XOR", target, ("input", j))
        physical = back._primitive.expand(target, n=n)
        labels = [(x, back._primitive.execute(physical, x)) for x in range(1 << n)]
        state = back.new_task()
        for length in (8, 12, 16, 24, 32) + ((48, 64) if n == 6 else ()):
            candidate = back.default_candidate(labels[:length], state)
            eligible = [t for t in back._base[back.mask][0]
                        if all(((t >> x) & 1) == y for x, y in labels[:length])]
            if candidate["truth"] != eligible[(len(eligible) - 1) // 2]:
                raise AssertionError("selector did not return the true lower median")
        if candidate["truth"] != sum(y << x for x, y in labels):
            raise AssertionError("full-label synthetic selection failed")
        # Publicly chosen index samples test derivation without materializing
        # the whole output catalogue.  Selection is unrelated to stream tasks.
        for route in ("default", "fold"):
            values = back._values(route)
            for index in range(0, len(values), max(1, len(values) // 32)):
                record = back._program(route, values[index])
                if record["truth"] != values[index]:
                    raise AssertionError("sampled materialization discrepancy")
        before = back.ledger()["counters"]
        repeated = back.default_candidate(labels, state)
        after = back.ledger()["counters"]
        if after["physical_programs_compiled"] != before["physical_programs_compiled"]:
            raise AssertionError("physical program cache missed identical proposal")
        if repeated["work"]["constraint_bitset_ops"] != 0:
            raise AssertionError("prefix state reread old feedback rows")
        if back.ledger()["cache"]["physical_programs"] >= 100:
            raise AssertionError("smoke eagerly materialized output programs")
        # The optional subset uses exactly the same lower-median convention.
        fold_prefix = labels[:12]
        eligible_fold = [t for t in back._fold[back.mask][0]
                         if all(((t >> x) & 1) == y for x, y in fold_prefix)]
        selected_fold = back.fold_candidate(fold_prefix)
        if eligible_fold:
            if selected_fold["truth"] != eligible_fold[(len(eligible_fold) - 1) // 2]:
                raise AssertionError("fold selector lower-median discrepancy")
        elif selected_fold is not None:
            raise AssertionError("empty fold subset did not return None")
        outside_fold = next(t for t in back._base[back.mask][0]
                            if t not in back._fold[back.mask][1])
        if back.fold_candidate([(x, (outside_fold >> x) & 1)
                                for x in range(1 << n)]) is not None:
            raise AssertionError("inconsistent fold probe did not return None")
        # Snapshot carries already-paid public caches, never task feedback.
        saved = pickle.dumps(back)
        restored = pickle.loads(saved)
        prior_programs = back.ledger()["cache"]["physical_programs"]
        carried = restored.default_candidate(labels)
        if not carried["physical_cache_hit"] or not carried["verified_truth_cache_hit"]:
            raise AssertionError("physical/verified cache did not survive pickle")
        if restored.ledger()["cache"]["physical_programs"] != prior_programs:
            raise AssertionError("restore changed retained programs")
        if restored.ledger()["counters"]["pickle_restores"] != 1:
            raise AssertionError("restore work missing from ledger")
        # A distinct arm has a cold cache and makes the same default choice.
        separate = SearchBackend(n)
        matched = separate.default_candidate(labels[:8])
        same = back.default_candidate(labels[:8])
        if matched["truth"] != same["truth"] or matched["expr"] != same["expr"]:
            raise AssertionError("default semantic/physical selection depends on fold availability")
        if separate.ledger()["cache"]["physical_programs"] != 1:
            raise AssertionError("backend caches leaked across arms")
        if separate.fold_candidate(labels[:8]) is not None:
            raise AssertionError("a backend without a fold emitted a fold program")
        json.dumps(same)
        summaries.append({"n": n, "public_functions": expected,
                          "materialized_programs": back.ledger()["cache"]["physical_programs"],
                          "snapshot_bytes": len(saved),
                          "ledger": back.ledger()})
    bad = 0
    for call in (lambda: setup.default_candidate([(0, 0), (0, 1)]),
                 lambda: setup.default_candidate([(0, 0.2)]),
                 lambda: setup.default_candidate([(0, 0)], SearchBackend(5).new_task())):
        try:
            call()
        except ValueError:
            bad += 1
    if bad != 3:
        raise AssertionError("bad input/state validation failed")
    return {"synthetic_only": True, "status": "passed", "scalar_rows_replayed": replayed,
            "bad_inputs_rejected": bad, "catalogues": summaries}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("use --self-test; official stream orchestration belongs to the caller")
    print(json.dumps(self_test(), sort_keys=True))
