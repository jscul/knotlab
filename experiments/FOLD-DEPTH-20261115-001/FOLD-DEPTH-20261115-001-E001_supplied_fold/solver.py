"""Exact semantic read-once synthesis, with a supplied-component control.

Inputs: n and a complete Boolean truth column (row x has input bit j=x>>j&1),
or every labeled row. No target expression, depth, layout, or family is read.
The public grammar is unnegated read-once AND/OR/XOR on independent inputs;
constants and irrelevant-input removal are public primitive simplifications.

All arms use the same memoized binary split/cofactor engine. Named and flat
add IDENTICAL unlocated proposals: find an outer XOR split, and an AND split
inside either side. All viable outer XOR splits remain eligible. A checked
contrary root kind prunes a placement, but a failed probe never certifies it.
Flat consumes the same factor certificates; it does not rediscover the AND.
Named executes the supplied seven-NAND F. Flat evaluates AND then XOR and
emits their actual six-NAND implementation. Authored length is not work.

Canonicalization removes irrelevant variables and renumbers each subproblem
by increasing support index only. There is NO permutation/isomorphism search,
associative normal form, target-boundary input, or prebuilt output catalogue.
Root-kind pruning uses nonconstant disjoint full-support factors in this
declared read-once class. Cofactor normalization outside this class is not a
general synthesis claim; unsupported inputs are retained as failures.

AST: ('input',j), ('const',bit), ('AND'|'OR'|'XOR',A,B), ('FOLD',A,B,C).
FOLD binds once to a supplied DAG: args0..2, constants3/4, NAND gate k=5+k.
Physical output uses inputs0..n-1, constants n/n+1, NAND gate k=n+2+k.
All saved NANDs execute; AND/OR/XOR expand to2/3/4 gates, without global CSE.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time


SOURCE_DEPENDENCIES = ()
SCHEMA_VERSION = 1
OPS = ("AND", "OR", "XOR")
COUNTERS = (
    "input_rows_received", "input_label_bit_reads", "support_variable_probes",
    "support_packed_bit_ops", "support_remap_calls", "support_remap_truth_bit_reads",
    "layout_requests", "layout_cache_hits", "layout_tables_built",
    "layout_rows_indexed", "layout_embedding_entries", "layout_broadcast_bit_ops",
    "factor_requests", "factor_cache_hits", "factor_sections_extracted",
    "factor_truth_bit_reads", "factor_nonconstant_sections", "factor_constant_sections",
    "factor_lift_bit_ors", "binary_placement_requests", "binary_placement_trials",
    "binary_placement_cache_hits", "binary_placement_passes", "binary_placement_failures",
    "binary_early_rejections", "binary_recomposition_ops",
    "binary_comparison_rows_equivalent", "root_certificate_requests",
    "root_certificate_cache_hits", "root_certificate_failures", "root_kind_prunes",
    "outer_xor_screens", "outer_xor_failures", "inner_and_screens", "inner_and_failures",
    "ternary_placements_considered", "ternary_placement_tests", "ternary_placement_passes",
    "ternary_placement_failures", "ternary_named_packed_NANDs",
    "ternary_flat_AND_ops", "ternary_flat_XOR_ops", "ternary_comparison_rows_equivalent",
    "subproblem_requests", "successful_subproblem_cache_hits",
    "failed_subproblem_cache_hits", "successful_subproblems_cached", "failed_subproblems_cached",
    "AST_nodes_built", "AST_remap_requests", "AST_remap_cache_hits", "AST_remap_nodes",
    "physical_compile_requests", "physical_compile_cache_hits", "physical_programs_compiled",
    "physical_NANDs_compiled", "physical_macro_calls_compiled", "verification_packed_NANDs",
    "verification_scalar_equivalent_NANDs", "verification_rows", "verification_comparisons",
    "verification_input_bit_reads", "archive_validation_scalar_NANDs",
    "archive_validation_input_bit_reads",
)


def _integer(x, name):
    if type(x) is not int:
        raise ValueError(f"{name} must be an integer")
    return x


def _bit(x):
    if type(x) not in (int, bool) or x not in (0, 1):
        raise ValueError("a label/constant must be a literal bit")
    return int(x)


def _dag(dag):
    if not isinstance(dag, dict) or "gates" not in dag or "output" not in dag:
        raise ValueError("fold requires gates/output")
    gates = []
    for k, pair in enumerate(dag["gates"]):
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            raise ValueError("a NAND needs two addresses")
        left, right = (_integer(x, "address") for x in pair)
        if min(left, right) < 0 or max(left, right) >= 5 + k:
            raise ValueError("nonprevious local fold address")
        gates.append([left, right])
    output = _integer(dag["output"], "fold output")
    if not 0 <= output < 5 + len(gates):
        raise ValueError("invalid fold output")
    return {"gates": gates, "output": output}


def expand(expr, fold_dag=None, n=None):
    """Compile actual NANDs; no semantic replacement or shared-gate CSE."""
    def leaves(node):
        if not isinstance(node, (tuple, list)) or not node:
            raise ValueError("invalid AST")
        if node[0] == "input" and len(node) == 2:
            j = _integer(node[1], "input index")
            if j < 0:
                raise ValueError("negative input index")
            return [j]
        if node[0] == "const" and len(node) == 2:
            _bit(node[1])
            return []
        if (node[0] in OPS and len(node) == 3) or (node[0] == "FOLD" and len(node) == 4):
            return [j for child in node[1:] for j in leaves(child)]
        raise ValueError("invalid AST operation/arity")
    used = leaves(expr)
    inferred = max(used, default=-1) + 1
    n = max(1, inferred) if n is None else _integer(n, "n")
    if n < inferred or n < 1:
        raise ValueError("n excludes an input leaf")
    dag = None if fold_dag is None else _dag(fold_dag)
    gates, counts = [], {op: 0 for op in OPS}
    macros = 0

    def nand(a, b):
        gates.append([a, b])
        return n + 1 + len(gates)

    def emit(node):
        nonlocal macros
        op = node[0]
        if op == "input":
            return node[1]
        if op == "const":
            return n + int(node[1])
        args = [emit(child) for child in node[1:]]
        if op == "FOLD":
            if dag is None:
                raise ValueError("unbound FOLD")
            local = args + [n, n + 1]
            for a, b in dag["gates"]:
                local.append(nand(local[a], local[b]))
            macros += 1
            return local[dag["output"]]
        counts[op] += 1
        a, b = args
        if op == "AND":
            t = nand(a, b)
            return nand(t, t)
        if op == "OR":
            return nand(nand(a, a), nand(b, b))
        t = nand(a, b)
        return nand(nand(a, t), nand(b, t))
    output = emit(expr)
    return {"inputs": n, "gates": gates, "output": output,
            "constants": {"zero": n, "one": n + 1}, "nand_gates": len(gates),
            "macro_uses": macros, "underlying_ops": counts}


def execute(circuit, x):
    n = circuit["inputs"]
    x = _integer(x, "x")
    if not 0 <= x < 1 << n:
        raise ValueError("input outside register")
    values = [(x >> j) & 1 for j in range(n)] + [0, 1]
    for a, b in circuit["gates"]:
        values.append(1 ^ (values[a] & values[b]))
    return values[circuit["output"]]


def packed_truth(circuit):
    n = circuit["inputs"]
    rows = 1 << n
    full = (1 << rows) - 1
    values = [sum(((x >> j) & 1) << x for x in range(rows)) for j in range(n)] + [0, full]
    for a, b in circuit["gates"]:
        values.append(full ^ (values[a] & values[b]))
    return values[circuit["output"]]


class Solver:
    """Cold per construction, or identically reusable warm caches per arm.

    ``solve`` requires a packed truth integer, a vector of2**n literal bits,
    or2**n (x,label) pairs covering every input. No sparse-label completion,
    private oracle, target shape or family is accepted. The flat arm needs no
    archived DAG/file; named needs the supplied seven-NAND binding.
    """

    def __init__(self, n, arm="primitive", fold_dag=None, trace_limit=32):
        started = time.perf_counter()
        self.n = _integer(n, "n")
        if not 1 <= n <= 9:
            raise ValueError("bounded solver supports1..9 inputs")
        if arm not in ("primitive", "named", "flat"):
            raise ValueError("unknown arm")
        self.arm = arm
        self.trace_limit = max(0, _integer(trace_limit, "trace_limit"))
        self.fold_dag = None
        self._work = {key: 0 for key in COUNTERS}
        if arm == "named":
            self.fold_dag = _dag(fold_dag)
            if len(self.fold_dag["gates"]) != 7:
                raise ValueError("named archive must contain exactly seven NANDs")
            for x in range(8):
                vals = [(x >> j) & 1 for j in range(3)] + [0, 1]
                self._work["archive_validation_input_bit_reads"] += 3
                for a, b in self.fold_dag["gates"]:
                    vals.append(1 ^ (vals[a] & vals[b]))
                if vals[self.fold_dag["output"]] != (((x & 1) & ((x >> 1) & 1)) ^ ((x >> 2) & 1)):
                    raise ValueError("archive does not implement the declared supplied F")
                self._work["archive_validation_scalar_NANDs"] += 7
        self._layouts, self._splits, self._factors, self._probes = {}, {}, {}, {}
        self._roots, self._success, self._failure = {}, {}, set()
        self._remaps, self._circuits = {}, {}
        self._trace, self._dropped = [], 0
        self._totals = {"setup_seconds": time.perf_counter() - started,
                        "input_seconds": 0.0, "search_seconds": 0.0,
                        "build_seconds": 0.0, "verification_seconds": 0.0,
                        "search_cpu_ns": 0, "solve_calls": 0}

    def _event(self, kind, **values):
        if len(self._trace) < self.trace_limit:
            self._trace.append({"kind": kind, **values})
        else:
            self._dropped += 1

    def _layout(self, k, group):
        self._work["layout_requests"] += 1
        key = (k, group)
        if key in self._layouts:
            self._work["layout_cache_hits"] += 1
            return self._layouts[key]
        def embeddings(mask):
            vals = (0,)
            for j in range(k):
                if (mask >> j) & 1:
                    vals += tuple(x | (1 << j) for x in vals)
            self._work["layout_embedding_entries"] += len(vals)
            return vals
        positions = tuple(j for j in range(k) if (group >> j) & 1)
        inside = embeddings(group)
        outside = embeddings(((1 << k) - 1) ^ group)
        broadcasts = []
        for x in inside:
            column = 0
            for y in outside:
                column |= 1 << (x | y)
            broadcasts.append(column)
        result = (positions, inside, tuple(broadcasts))
        self._layouts[key] = result
        self._work["layout_tables_built"] += 1
        self._work["layout_rows_indexed"] += 1 << k
        self._work["layout_broadcast_bit_ops"] += 3 * (1 << k)
        return result

    def _support(self, k, truth):
        group = 0
        for j in range(k):
            low_rows = self._layout(k, 1 << j)[2][0]
            if (truth ^ (truth >> (1 << j))) & low_rows:
                group |= 1 << j
            self._work["support_variable_probes"] += 1
            self._work["support_packed_bit_ops"] += 3
        return group

    def _factor(self, k, truth, group, fixed):
        self._work["factor_requests"] += 1
        key = (k, truth, group, fixed)
        if key in self._factors:
            self._work["factor_cache_hits"] += 1
            return self._factors[key]
        positions, assignments, broadcasts = self._layout(k, group)
        compact = lifted = 0
        for j, x in enumerate(assignments):
            self._work["factor_truth_bit_reads"] += 1
            if (truth >> (x | fixed)) & 1:
                compact |= 1 << j
                lifted |= broadcasts[j]
                self._work["factor_lift_bit_ors"] += 1
        full_child = (1 << (1 << len(positions))) - 1
        name = "factor_constant_sections" if compact in (0, full_child) else "factor_nonconstant_sections"
        self._work[name] += 1
        self._work["factor_sections_extracted"] += 1
        result = (compact, lifted, positions)
        self._factors[key] = result
        return result

    def _groups(self, k):
        if k not in self._splits:
            mask = (1 << k) - 1
            # Symmetric binary operands: the smaller group goes first; equal
            # sizes tie by mask. All disjoint bipartitions occur once.
            self._splits[k] = tuple(sorted(
                (g for g in range(1, mask) if (g.bit_count(), g) <= ((mask ^ g).bit_count(), mask ^ g)),
                key=lambda g: (g.bit_count(), g)))
        return self._splits[k]

    def _probe(self, k, truth, group, op):
        self._work["binary_placement_requests"] += 1
        key = (k, truth, group, op)
        if key in self._probes:
            self._work["binary_placement_cache_hits"] += 1
            return self._probes[key]
        # A NEW op+split counts even if a cofactor rejects it before any
        # recomposition. Cached failures never increment this counter again.
        self._work["binary_placement_trials"] += 1
        other = ((1 << k) - 1) ^ group
        witness = (truth & -truth).bit_length() - 1
        a = self._factor(k, truth, group, (witness & other) if op == "AND" else 0)
        b = self._factor(k, truth, other, (witness & group) if op == "AND" else 0)
        a_full = (1 << (1 << group.bit_count())) - 1
        b_full = (1 << (1 << other.bit_count())) - 1
        valid = (a[0] not in (0, a_full) and b[0] not in (0, b_full)
                 and not (a[0] & 1) and not (b[0] & 1))
        if valid:
            result = (a[1] & b[1]) if op == "AND" else ((a[1] | b[1]) if op == "OR" else (a[1] ^ b[1]))
            self._work["binary_recomposition_ops"] += 1
            self._work["binary_comparison_rows_equivalent"] += 1 << k
            valid = result == truth
        else:
            self._work["binary_early_rejections"] += 1
        cert = {"op": op, "group": group, "other": other, "a": a, "b": b} if valid else None
        self._probes[key] = cert
        self._work["binary_placement_passes" if valid else "binary_placement_failures"] += 1
        self._event("binary", inputs=k, group=group, op=op, passed=bool(valid))
        return cert

    def _first_binary(self, k, truth):
        self._work["root_certificate_requests"] += 1
        key = (k, truth)
        if key in self._roots:
            self._work["root_certificate_cache_hits"] += 1
            return self._roots[key]
        cert = None
        for group in self._groups(k):
            for op in OPS:
                cert = self._probe(k, truth, group, op)
                if cert is not None:
                    break
            if cert is not None:
                break
        self._roots[key] = cert
        if cert is None:
            self._work["root_certificate_failures"] += 1
        return cert

    def _remap(self, expr, positions):
        self._work["AST_remap_requests"] += 1
        key = (expr, positions)
        if key in self._remaps:
            self._work["AST_remap_cache_hits"] += 1
            return self._remaps[key]
        op = expr[0]
        if op == "input":
            result = (op, positions[expr[1]])
        elif op == "const":
            result = expr
        else:
            result = (op, *(self._remap(child, positions) for child in expr[1:]))
        self._work["AST_remap_nodes"] += 1
        self._remaps[key] = result
        return result

    def _join_binary(self, k, truth, cert):
        a, b = cert["a"], cert["b"]
        left = self._solve(len(a[2]), a[0])
        if left is None:
            return None
        right = self._solve(len(b[2]), b[0])
        if right is None:
            return None
        expr = (cert["op"], self._remap(left[0], a[2]), self._remap(right[0], b[2]))
        self._work["AST_nodes_built"] += 1
        return expr, left[1] + right[1]

    def _template(self, k, truth):
        for group in self._groups(k):
            self._work["outer_xor_screens"] += 1
            outer = self._probe(k, truth, group, "XOR")
            if outer is None:
                self._work["outer_xor_failures"] += 1
                continue
            for inner, c in ((outer["a"], outer["b"]), (outer["b"], outer["a"])):
                if len(inner[2]) < 2:
                    continue
                self._work["ternary_placements_considered"] += 1
                self._work["inner_and_screens"] += 1
                cert = self._first_binary(len(inner[2]), inner[0])
                if cert is None or cert["op"] != "AND":
                    self._work["inner_and_failures"] += 1
                    if cert is not None:
                        self._work["root_kind_prunes"] += 1
                    self._event("inner_prune", inputs=k, inner_inputs=len(inner[2]),
                                root=None if cert is None else cert["op"])
                    continue
                # Convert inner child support coordinates to this parent's
                # positions. Both arms reuse this SAME already-paid cert.
                a, b = cert["a"], cert["b"]
                a_pos = tuple(inner[2][j] for j in a[2])
                b_pos = tuple(inner[2][j] for j in b[2])
                a_mask = sum(1 << j for j in a_pos)
                b_mask = sum(1 << j for j in b_pos)
                a_lift = self._lift(k, a_mask, a[0])
                b_lift = self._lift(k, b_mask, b[0])
                c_lift = c[1]
                self._work["ternary_placement_tests"] += 1
                if self.arm == "named":
                    full = (1 << (1 << k)) - 1
                    values = [a_lift, b_lift, c_lift, 0, full]
                    for aa, bb in self.fold_dag["gates"]:
                        values.append(full ^ (values[aa] & values[bb]))
                    composed = values[self.fold_dag["output"]]
                    self._work["ternary_named_packed_NANDs"] += 7
                else:
                    composed = (a_lift & b_lift) ^ c_lift
                    self._work["ternary_flat_AND_ops"] += 1
                    self._work["ternary_flat_XOR_ops"] += 1
                self._work["ternary_comparison_rows_equivalent"] += 1 << k
                if composed != truth:
                    self._work["ternary_placement_failures"] += 1
                    continue
                self._work["ternary_placement_passes"] += 1
                self._event("ternary", inputs=k, groups=[a_mask, b_mask, sum(1 << j for j in c[2])])
                children = [self._solve(len(z[2]), z[0]) for z in (a, b, c)]
                if any(child is None for child in children):
                    continue
                aa = self._remap(children[0][0], a_pos)
                bb = self._remap(children[1][0], b_pos)
                cc = self._remap(children[2][0], c[2])
                if self.arm == "named":
                    expr = ("FOLD", aa, bb, cc)
                    self._work["AST_nodes_built"] += 1
                else:
                    expr = ("XOR", ("AND", aa, bb), cc)
                    self._work["AST_nodes_built"] += 2
                return expr, 1 + sum(child[1] for child in children)
        return None

    def _lift(self, k, group, compact):
        columns = self._layout(k, group)[2]
        lifted = 0
        while compact:
            bit = compact & -compact
            lifted |= columns[bit.bit_length() - 1]
            compact ^= bit
            self._work["factor_lift_bit_ors"] += 1
        return lifted

    def _solve(self, k, truth):
        self._work["subproblem_requests"] += 1
        key = (k, truth)
        if key in self._success:
            self._work["successful_subproblem_cache_hits"] += 1
            return self._success[key]
        if key in self._failure:
            self._work["failed_subproblem_cache_hits"] += 1
            return None
        full = (1 << (1 << k)) - 1
        result = None
        if truth in (0, full):
            result = (("const", int(truth != 0)), 0)
        elif k == 1 and truth == 2:
            result = (("input", 0), 0)
        elif k >= 2 and not (truth & 1):
            root = self._first_binary(k, truth)
            if root is not None:
                if self.arm != "primitive":
                    if root["op"] == "XOR":
                        result = self._template(k, truth)
                    else:
                        self._work["root_kind_prunes"] += 1
                if result is None:
                    result = self._join_binary(k, truth, root)
                if result is None:
                    # If an out-of-class child failed, retain honest failure
                    # and still try the other same-kind disjoint splits.
                    for group in self._groups(k):
                        if group == root["group"]:
                            continue
                        cert = self._probe(k, truth, group, root["op"])
                        if cert is not None:
                            result = self._join_binary(k, truth, cert)
                            if result is not None:
                                break
        if result is None:
            self._failure.add(key)
            self._work["failed_subproblems_cached"] += 1
        else:
            if truth in (0, full) or (k == 1 and truth == 2):
                self._work["AST_nodes_built"] += 1
            self._success[key] = result
            self._work["successful_subproblems_cached"] += 1
        return result

    def _input(self, supplied):
        rows = 1 << self.n
        full = (1 << rows) - 1
        if type(supplied) is int:
            if not 0 <= supplied <= full:
                raise ValueError("packed truth outside declared row count")
            truth = supplied
            self._work["input_rows_received"] += rows
        else:
            supplied = list(supplied)
            if len(supplied) != rows:
                raise ValueError("exact synthesis requires all input labels")
            if all(type(x) in (int, bool) for x in supplied):
                truth = sum(_bit(label) << i for i, label in enumerate(supplied))
            else:
                labels = {}
                for row in supplied:
                    if not isinstance(row, (tuple, list)) or len(row) != 2:
                        raise ValueError("expected complete (x,label) rows")
                    x = _integer(row[0], "row input")
                    if not 0 <= x < rows or x in labels:
                        raise ValueError("duplicate/out-of-range row")
                    labels[x] = _bit(row[1])
                truth = sum(label << x for x, label in labels.items())
            self._work["input_rows_received"] += rows
            self._work["input_label_bit_reads"] += rows
        support = self._support(self.n, truth)
        positions, assignments, _ = self._layout(self.n, support)
        compact = 0
        for j, x in enumerate(assignments):
            compact |= ((truth >> x) & 1) << j
        self._work["support_remap_calls"] += 1
        self._work["support_remap_truth_bit_reads"] += len(assignments)
        return truth, positions, compact

    def _cache_sizes(self):
        return {"layout_tables": len(self._layouts), "factor_sections": len(self._factors),
                "binary_probe_results": len(self._probes), "root_certificates": len(self._roots),
                "successful_subproblems": len(self._success), "failed_subproblems": len(self._failure),
                "AST_layouts": len(self._remaps), "physical_programs": len(self._circuits)}

    def work_counters(self):
        return dict(self._work)

    def ledger(self):
        return {"schema_version": SCHEMA_VERSION, "arm": self.arm, "n": self.n,
                "counters": self.work_counters(), "timing": dict(self._totals),
                "cache": self._cache_sizes()}

    def solve(self, supplied):
        """Return a physical exact program or an explicit unsupported result.

        W=binary_placement_trials+ternary_placement_tests counts NEW executed
        candidate screens, including early rejected binary cofactors. Requests
        include cache hits and are not added to W. factor_truth_bit_reads is
        actual extracted-row work; packed comparison row equivalents remain
        distinct. AST construction belongs to search timing, final NAND
        compilation to build timing, all-row physical replay to verification.
        """
        total_start = time.perf_counter()
        before, cache_before = self.work_counters(), self._cache_sizes()
        self._trace, self._dropped = [], 0
        started = time.perf_counter()
        truth, positions, compact = self._input(supplied)
        input_seconds = time.perf_counter() - started
        started, cpu = time.perf_counter(), time.process_time_ns()
        solved = self._solve(len(positions), compact)
        expr = None if solved is None else self._remap(solved[0], positions)
        search_cpu = time.process_time_ns() - cpu
        search_seconds = time.perf_counter() - started
        started = time.perf_counter()
        circuit, compile_hit = None, False
        if expr is not None:
            self._work["physical_compile_requests"] += 1
            compile_hit = expr in self._circuits
            if compile_hit:
                self._work["physical_compile_cache_hits"] += 1
                circuit = self._circuits[expr]
            else:
                circuit = expand(expr, self.fold_dag, self.n)
                self._circuits[expr] = circuit
                self._work["physical_programs_compiled"] += 1
                self._work["physical_NANDs_compiled"] += circuit["nand_gates"]
                self._work["physical_macro_calls_compiled"] += circuit["macro_uses"]
        build_seconds = time.perf_counter() - started
        started = time.perf_counter()
        verified = None
        if circuit is not None:
            verified = packed_truth(circuit)
            self._work["verification_input_bit_reads"] += self.n * (1 << self.n)
            self._work["verification_packed_NANDs"] += circuit["nand_gates"]
            self._work["verification_scalar_equivalent_NANDs"] += circuit["nand_gates"] * (1 << self.n)
            self._work["verification_rows"] += 1 << self.n
            self._work["verification_comparisons"] += 1
            if verified != truth:
                raise AssertionError("synthesized physical circuit is incorrect")
        verification_seconds = time.perf_counter() - started
        timing = {"input_seconds": input_seconds, "search_seconds": search_seconds,
                  "search_cpu_ns": search_cpu, "build_seconds": build_seconds,
                  "verification_seconds": verification_seconds,
                  "elapsed_seconds": time.perf_counter() - total_start}
        for key in ("input_seconds", "search_seconds", "search_cpu_ns", "build_seconds", "verification_seconds"):
            self._totals[key] += timing[key]
        self._totals["solve_calls"] += 1
        return {
            "schema_version": SCHEMA_VERSION, "arm": self.arm, "n": self.n,
            "status": "exact" if solved is not None else "unsupported",
            "expr": expr, "circuit": circuit, "truth": verified,
            "input_support": list(positions),
            "macro_uses": 0 if circuit is None else circuit["macro_uses"],
            "template_uses": 0 if solved is None else solved[1],
            "expanded_NANDs": None if circuit is None else circuit["nand_gates"],
            "physical_compile_cache_hit": compile_hit,
            "work": {key: self._work[key] - before[key] for key in COUNTERS},
            "timing": timing, "cache_before": cache_before, "cache_after": self._cache_sizes(),
            "trace": list(self._trace), "trace_dropped": self._dropped,
            "canonicalization": "essential support compressed in increasing input order; no permutation/associative canonicalization",
            "fold_dag": self.fold_dag,
        }


def solve(n, supplied, arm="primitive", fold_dag=None, trace_limit=32):
    """Convenience cold run; use Solver directly for explicitly warm runs."""
    return Solver(n, arm, fold_dag, trace_limit).solve(supplied)


def self_test():
    """Synthetic primitives and arbitrary layouts only; imports no task data."""
    for op, cost in (("AND", 2), ("OR", 3), ("XOR", 4)):
        circuit = expand((op, ("input", 0), ("input", 1)), n=2)
        if circuit["nand_gates"] != cost:
            raise AssertionError("primitive physical cost mismatch")
        for a, b in itertools.product((0, 1), repeat=2):
            expected = {"AND": a & b, "OR": a | b, "XOR": a ^ b}[op]
            if execute(circuit, a | (b << 1)) != expected:
                raise AssertionError("primitive truth mismatch")
    # The fixture is six public primitive NANDs plus one genuinely executed
    # dead NAND, deliberately testing that named expansion keeps all seven.
    flat = expand(("XOR", ("AND", ("input", 0), ("input", 1)), ("input", 2)), n=3)
    dag = {"gates": flat["gates"] + [[3, 4]], "output": flat["output"]}
    summaries = []
    for n in (3, 5, 7, 9):
        # Toy formula is intentionally separate from any task panel/generator.
        expr = ("XOR", ("AND", ("input", n - 1), ("input", 0)), ("input", 1))
        for j in range(2, n - 1):
            expr = (("OR" if j % 2 else "XOR"), expr, ("input", j))
        target = packed_truth(expand(expr, n=n))
        results = {}
        for arm in ("primitive", "named", "flat"):
            engine = Solver(n, arm, dag if arm == "named" else None)
            result = engine.solve(target)
            if result["status"] != "exact" or result["truth"] != target:
                raise AssertionError("synthetic exact synthesis failed")
            scalar = sum(execute(result["circuit"], x) << x for x in range(1 << n))
            if scalar != target:
                raise AssertionError("scalar NAND replay disagrees")
            warm = engine.solve([(x, (target >> x) & 1) for x in range(1 << n)])
            if warm["work"]["binary_placement_trials"] or warm["work"]["ternary_placement_tests"]:
                raise AssertionError("successful semantic memo was not reused")
            if not warm["physical_compile_cache_hit"]:
                raise AssertionError("physical compile memo was not reused")
            json.dumps(result)
            results[arm] = result
        for key in ("binary_placement_trials", "ternary_placement_tests", "factor_truth_bit_reads",
                    "outer_xor_screens", "inner_and_screens"):
            if results["named"]["work"][key] != results["flat"]["work"][key]:
                raise AssertionError("matched candidate/control paths diverged")
        summaries.append({"n": n, "exact_arms": 3,
                          "binary_trials": results["named"]["work"]["binary_placement_trials"],
                          "ternary_tests": results["named"]["work"]["ternary_placement_tests"]})
    # Completeness regression: first viable XOR split need not expose AND.
    expr = ("XOR", ("XOR", ("AND", ("input", 3), ("input", 4)),
                    ("input", 1)), ("XOR", ("input", 0), ("input", 2)))
    target = packed_truth(expand(expr, n=5))
    for arm in ("named", "flat"):
        result = solve(5, target, arm, dag if arm == "named" else None)
        if result["template_uses"] == 0:
            raise AssertionError("only first outer XOR split was considered")
    # Two calls in separate parts of a six-input toy test recursive binding
    # and physical expansion without using the experiment's path templates.
    parallel = ("XOR", ("XOR", ("AND", ("input", 0), ("input", 2)), ("input", 4)),
                ("XOR", ("AND", ("input", 1), ("input", 5)), ("input", 3)))
    target = packed_truth(expand(parallel, n=6))
    multiple = {}
    for arm in ("named", "flat"):
        result = solve(6, target, arm, dag if arm == "named" else None)
        if result["template_uses"] != 2 or result["truth"] != target:
            raise AssertionError("recursive multiple-template runtime failed")
        multiple[arm] = result
    if multiple["named"]["macro_uses"] != 2 or multiple["flat"]["macro_uses"] != 0:
        raise AssertionError("physical macro counts are not literal")
    # Public simplifications and an out-of-class failure are retained.
    engine = Solver(5)
    for expr in (("const", 0), ("const", 1), ("input", 4)):
        if engine.solve(packed_truth(expand(expr, n=5)))["status"] != "exact":
            raise AssertionError("primitive simplification failed")
    negative = engine.solve(1)  # not zero-preserving, nonconstant
    again = engine.solve(1)
    if negative["status"] != "unsupported" or again["work"]["failed_subproblem_cache_hits"] != 1:
        raise AssertionError("negative memo control failed")
    return {"synthetic_only": True, "status": "passed", "cases": summaries}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("use --self-test; real tasks are owned by the experiment orchestrator")
    print(json.dumps(self_test(), sort_keys=True))
