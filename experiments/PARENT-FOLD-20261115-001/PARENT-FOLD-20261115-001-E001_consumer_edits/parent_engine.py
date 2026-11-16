"""Shared incremental NAND parent context and an ordinary structural rival.

Public Parent input needs n,gates,upstream_count,frontier,outputs,pieces only.
Stage truth tables quantify m independent frontier signals. The raw prefix
is also evaluated for historical accounting; a separate checker validates
the frontier/raw composition. No original global answer is inferred for free.

Each edit branches from immutable original gates/tables. Only geometric
layouts transfer from Parent to State: completed semantic recipes, groups,
codes and answers NEVER pass between sibling States, including edit(None).
Public helpers return (value,local_work). parent.work is history only;
state.work is edit construction only. state.adaptation_work accumulates
public helper costs, including abandoned attempts; callers sum helper returns.

partition gives first-occurrence joint residual IDs for8 local states.
select proves the global width, with an optional feasible incumbent, without
compiling a competing answer. finish builds prescribed local bytes or an
ordinary code, reuses valid source taps, keeps source consumers where legal,
and repairs only bypassing outputs. Every physical attempt has its own cut-
scoped source memo and semantic wire set. No raw inverse-node alias crosses
the cut. Existing source gates can be normalized by exact semantic equality.

Answers are stage-only JointSolver-style records. The common harness owns
raw physical lifting/verification and charges it once.
"""

from __future__ import annotations

from collections import Counter, deque
from itertools import combinations
import hashlib
import importlib.util
from math import comb
from pathlib import Path
import sys
from time import perf_counter, process_time_ns


_ROOT = Path(__file__).resolve().parents[3]
SOURCE_DEPENDENCIES = (
    "experiments/FOLD-TWO-OUTPUT-20261115-001/FOLD-TWO-OUTPUT-20261115-001-E001_joint_tables/joint_solver.py",
)
SOURCE_SHA256 = {SOURCE_DEPENDENCIES[0]: "a9b5d4a0ab99cbcfad7f266092157139bcef0059495f6bb136c453a8c59e6391"}
_path = _ROOT / SOURCE_DEPENDENCIES[0]
if hashlib.sha256(_path.read_bytes()).hexdigest() != SOURCE_SHA256[SOURCE_DEPENDENCIES[0]]:
    raise RuntimeError("immutable joint primitive backend changed")
_alias = "_parent_fold_joint_primitive"
if _alias in sys.modules:
    _joint = sys.modules[_alias]
else:
    _spec = importlib.util.spec_from_file_location(_alias, _path)
    _joint = importlib.util.module_from_spec(_spec)
    sys.modules[_alias] = _joint
    _spec.loader.exec_module(_joint)
if Path(_joint.__file__).resolve() != _path.resolve():
    raise ImportError("joint primitive alias points elsewhere")


def _int(value, name):
    if type(value) is not int:
        raise ValueError(name + " must be an integer")
    return value


def _group(value, m):
    value = tuple(value)
    if (len(value) != 3 or any(type(j) is not int or not 0 <= j < m for j in value)
            or value != tuple(sorted(set(value)))):
        raise ValueError("group needs three sorted stage input indices")
    return value


def _columns(n):
    full = (1 << (1 << n)) - 1
    zero = tuple(full // ((1 << (1 << j)) + 1) for j in range(n))
    return full, zero, tuple(full ^ z for z in zero)


def _support(truth, zero, work, key):
    result = 0
    for j, mask in enumerate(zero):
        work[key] += 1
        if (truth ^ (truth >> (1 << j))) & mask:
            result |= 1 << j
    return result


def _layout(m, full, zero, group):
    mask, offsets = full, [0]
    for j in group:
        mask &= zero[j]
        offsets += [offset + (1 << j) for offset in offsets]
    outside = tuple(j for j in range(m) if j not in group)
    return mask | (mask << (1 << m)), tuple(offsets), outside


class Parent:
    def __init__(self, case):
        wall, cpu = perf_counter(), process_time_ns()
        self.work = Counter()
        self.n = _int(case["n"], "raw n")
        self.upstream_count = _int(case["upstream_count"], "upstream_count")
        if self.n < 1:
            raise ValueError("raw arity must be positive")
        self.gates = tuple(tuple(pair) for pair in case["gates"])
        self.first_gate = self.n + 2
        self.first_suffix = self.first_gate + self.upstream_count
        if not 0 <= self.upstream_count <= len(self.gates):
            raise ValueError("invalid prefix length")
        self.frontier = tuple(case["frontier"])
        self.m = len(self.frontier)
        if (self.m < 3 or len(set(self.frontier)) != self.m
                or any(type(w) is not int or not 0 <= w < self.first_suffix or w in (self.n, self.n + 1)
                       for w in self.frontier)):
            raise ValueError("invalid frontier")
        self.frontier_index = {wire: j for j, wire in enumerate(self.frontier)}
        self.output_wires = tuple(case["outputs"])
        if len(self.output_wires) != 2:
            raise ValueError("parent needs two outputs")
        raw_full, _, raw_columns = _columns(self.n)
        raw = [*raw_columns, 0, raw_full]
        fanout, structural, canonical = {}, {}, {w: w for w in range(self.first_gate)}
        for index, pair in enumerate(self.gates):
            wire = self.first_gate + index
            if len(pair) != 2 or any(type(w) is not int or not 0 <= w < wire for w in pair):
                raise ValueError("invalid source NAND/address")
            a, b = pair
            raw.append(raw_full ^ (raw[a] & raw[b]))
            self.work["history_raw_NANDs"] += 1
            for pin, source in enumerate(pair):
                fanout.setdefault(source, []).append((wire, pin))
                self.work["history_fanout_edges"] += 1
            key = tuple(sorted((canonical[a], canonical[b])))
            old = structural.setdefault(key, wire)
            canonical[wire] = old
            self.work["history_structural_lookups"] += 1
            self.work["history_structural_aliases"] += old != wire
        self.raw_values = tuple(raw)
        self.fanout = {wire: tuple(edges) for wire, edges in fanout.items()}
        self.canonical_wires = canonical
        self.full, self.zero, self.columns = _columns(self.m)
        values = {self.n: 0, self.n + 1: self.full}
        supports = {self.n: 0, self.n + 1: 0}
        for j, wire in enumerate(self.frontier):
            values[wire], supports[wire] = self.columns[j], 1 << j
        for index in range(self.upstream_count, len(self.gates)):
            wire = self.first_gate + index
            a, b = self.gates[index]
            if a not in values or b not in values:
                raise ValueError("suffix accesses an upstream wire outside frontier")
            values[wire] = self.full ^ (values[a] & values[b])
            supports[wire] = supports[a] | supports[b]
            self.work["history_stage_NANDs"] += 1
            self.work["history_support_unions"] += 1
        if any(wire not in values for wire in self.output_wires):
            raise ValueError("outputs lie outside the stage")
        self.original_values, self.original_supports = values, supports
        self.original_tables = tuple(values[w] for w in self.output_wires)
        self.original_raw_tables = tuple(raw[w] for w in self.output_wires)
        self.group_layouts = {}
        pieces = []
        for supplied in case["pieces"]:
            group = _group(supplied["inputs"], self.m)
            source_bit = _int(supplied["bit"], "historical bit")
            ports = tuple(supplied["ports"])
            if len(ports) != 2 or source_bit not in values or any(w not in values for w in ports):
                raise ValueError("historical piece source is unavailable")
            group_mask = sum(1 << j for j in group)
            actual = _support(values[source_bit], self.zero, self.work, "history_piece_support_tests")
            if actual != group_mask:
                raise ValueError("historical bit is not essentially local to its declared triple")
            layout = self.group_layouts.get(group)
            if layout is None:
                layout = self.group_layouts[group] = _layout(self.m, self.full, self.zero, group)
                self.work["history_group_layouts_built"] += 1
            mask, offsets, outside = layout
            single_mask = mask & self.full
            byte = sum(((values[source_bit] >> offset) & 1) << local for local, offset in enumerate(offsets))
            by_bit = {}
            for local, offset in enumerate(offsets):
                residual = tuple((values[port] >> offset) & single_mask for port in ports)
                self.work["history_piece_residual_columns"] += 2
                bit = (byte >> local) & 1
                previous = by_bit.setdefault(bit, residual)
                self.work["history_piece_partition_comparisons"] += 1
                if previous != residual:
                    raise ValueError("historical ports do not factor through the old local bit")
            pieces.append({"inputs": group, "bit": source_bit, "ports": ports,
                           "bit_truth": byte, "bit_table": values[source_bit],
                           "port_tables": tuple(values[w] for w in ports),
                           "structural_bit_local": not (supports[source_bit] & ~group_mask)})
            self.work["history_pieces_validated"] += 1
        self.pieces = tuple(pieces)
        self.work["history_source_gates"] = len(self.gates)
        self.work["history_frontier_inputs"] = self.m
        self.timing = {"cpu_ns": process_time_ns() - cpu, "seconds": perf_counter() - wall}

    @property
    def base(self):
        return self.edit(None)

    def edit(self, edit):
        return State(self, edit)


class State:
    def __init__(self, parent, edit):
        wall, cpu = perf_counter(), process_time_ns()
        self.parent, self.m = parent, parent.m
        self.work, self.adaptation_work = Counter(), Counter()
        self.edit = None if edit is None else dict(edit)
        self.output_wires = parent.output_wires
        self.gates = parent.gates
        self.values = dict(parent.original_values)
        self.supports = dict(parent.original_supports)
        self.work["edit_stage_entries_copied"] = len(self.values) + len(self.supports)
        affected, changed = set(), set()
        if edit is not None:
            gate, pin, to = (_int(edit[k], k) for k in ("gate", "pin", "to"))
            if not parent.first_suffix <= gate < parent.first_gate + len(parent.gates) or pin not in (0, 1):
                raise ValueError("edit must address a suffix NAND pin")
            if to not in self.values or to >= gate:
                raise ValueError("edit target is not a legal previous stage wire")
            gates = list(parent.gates)
            operands = list(gates[gate - parent.first_gate])
            operands[pin] = to
            gates[gate - parent.first_gate] = tuple(operands)
            self.gates = tuple(gates)
            self.work["edit_gate_refs_copied"] = len(gates)
            self.work["edit_pin_writes"] = 1
            pending = [gate]
            while pending:
                wire = pending.pop()
                if wire in affected:
                    continue
                affected.add(wire)
                for other, _ in parent.fanout.get(wire, ()):
                    pending.append(other)
                    self.work["edit_fanout_edges"] += 1
            for wire in sorted(affected):
                a, b = self.gates[wire - parent.first_gate]
                self.supports[wire] = self.supports[a] | self.supports[b]
                self.work["edit_support_unions"] += 1
                if wire != gate and a not in changed and b not in changed:
                    self.work["edit_unchanged_descendants_skipped"] += 1
                    continue
                value = parent.full ^ (self.values[a] & self.values[b])
                self.work["edit_packed_NANDs"] += 1
                if value != parent.original_values[wire]:
                    changed.add(wire)
                else:
                    self.work["edit_unchanged_recomputations"] += 1
                self.values[wire] = value
        self.affected, self.changed = tuple(sorted(affected)), tuple(sorted(changed))
        self.work["edit_fanout_vertices"] = len(affected)
        self.work["edit_changed_tables"] = len(changed)
        self.tables = tuple(self.values[w] for w in self.output_wires)
        self.work["edit_output_table_comparisons"] = 2
        self.work["edit_changed_outputs"] = sum(a != b for a, b in zip(self.tables, parent.original_tables))
        self.timing = {"cpu_ns": process_time_ns() - cpu, "seconds": perf_counter() - wall}
        self._joint = None
        self._shared = None
        self._partitions, self._lower_bounds, self._locals, self._source_records = {}, {}, {}, {}
        self._global_width = None


def _engine(state):
    if state._joint is None:
        state._joint = _joint.JointSolver(state.m, arm="primitive")
        # Only paid, immutable geometry transfers from original history.
        state._joint._layouts = dict(state.parent.group_layouts)
    return state._joint


def _shared(state, work):
    if state._shared is None:
        first = _support(state.tables[0], state.parent.zero, work, "shared_support_tests")
        second = _support(state.tables[1], state.parent.zero, work, "shared_support_tests")
        state._shared = tuple(j for j in range(state.m) if (first & second) & (1 << j))
    else:
        work["shared_support_cache_hits"] += 1
    return state._shared


def _measure(state, function, *args, **kwargs):
    wall, cpu = perf_counter(), process_time_ns()
    work = Counter()
    before = {} if state._joint is None else state._joint.work_counters()
    value = function(state, work, *args, **kwargs)
    after = {} if state._joint is None else state._joint.work_counters()
    for key, count in after.items():
        delta = count - before.get(key, 0)
        if delta:
            work["joint_" + key] += delta
    work["helper_cpu_ns"] += process_time_ns() - cpu
    work["helper_wall_ns"] += round((perf_counter() - wall) * 1e9)
    state.adaptation_work.update(work)
    return value, dict(work)


def _partition(state, work, triple, bound=8):
    triple = _group(triple, state.m)
    work["group_requests"] += 1
    if triple in state._partitions:
        work["group_cache_hits"] += 1
        info = state._partitions[triple]
        return info if info["class_count"] <= bound else None
    if state._lower_bounds.get(triple, 0) > bound:
        work["group_lower_bound_cache_hits"] += 1
        return None
    solver = _engine(state)
    mask, offsets, outside = solver._layout(triple)
    joint = state.tables[0] | (state.tables[1] << (1 << state.m))
    labels, classes, unique = {}, [], []
    work["group_trials"] += 1
    for offset in offsets:
        value = (joint >> offset) & mask
        work["group_packed_columns"] += 1
        label = labels.get(value)
        if label is None:
            label = len(unique)
            labels[value] = label
            unique.append(value)
            if len(unique) > bound:
                state._lower_bounds[triple] = max(state._lower_bounds.get(triple, 0), len(unique))
                work["group_bound_rejections"] += 1
                return None
        classes.append(label)
    pairs = tuple((value & state.parent.full, value >> (1 << state.m)) for value in unique)
    info = {"triple": triple, "group": triple, "class_count": len(unique), "count": len(unique),
            "width": (len(unique) - 1).bit_length(), "classes": tuple(classes),
            "columns": tuple(pairs[c] for c in classes), "outside": outside,
            "eligible": all(j in _shared(state, work) for j in triple)}
    state._partitions[triple] = info
    work["group_exact_partitions"] += 1
    if info["eligible"] and info["width"] == 1:
        state._global_width = 1
    return info


def partition(state, triple):
    return _measure(state, _partition, triple)


def _source_record(state, work, triple, wire):
    key = (triple, wire)
    if key in state._source_records:
        work["local_source_record_hits"] += 1
        return state._source_records[key]
    work["local_source_wire_tests"] += 1
    mask = sum(1 << j for j in triple)
    support = state.supports.get(wire, 0)
    value = state.values.get(wire)
    result = None
    if support and not support & ~mask and value not in (None, 0, state.parent.full):
        offsets = _engine(state)._layout(triple)[1]
        byte = sum(((value >> offset) & 1) << local for local, offset in enumerate(offsets))
        work["local_source_bit_reads"] += 8
        result = {"wire": wire, "support": support, "truth": byte, "table": value}
    state._source_records[key] = result
    return result


def _local_sources(state, work, triple):
    triple = _group(triple, state.m)
    if triple in state._locals:
        work["local_source_cache_hits"] += 1
        return state._locals[triple]
    preferred = [p["bit"] for p in state.parent.pieces if p["inputs"] == triple]
    records = []
    for wire in state.supports:
        record = _source_record(state, work, triple, wire)
        if record is not None:
            records.append(record)
    records.sort(key=lambda row: (row["wire"] not in preferred, row["wire"]))
    state._locals[triple] = records
    return records


def local_sources(state, group):
    return _measure(state, _local_sources, group)


class _Bypass(Exception):
    pass


def _import_source(state, work, physical, wire, mapping, failed, semantic=True):
    work["source_wire_requests"] += 1
    if wire in mapping:
        work["source_wire_cache_hits"] += 1
        return mapping[wire]
    if semantic:
        work["source_alias_lookups"] += 1
        alias = physical.semantic.get(state.values[wire])
        if alias is not None:
            work["source_semantic_alias_hits"] += 1
            mapping[wire] = alias
            return alias
    if wire in failed or wire < state.parent.first_suffix:
        work["source_bypass_hits"] += 1
        raise _Bypass
    operands = state.gates[wire - state.parent.first_gate]
    children, bypass = [], False
    # Inspect both fanins even if one fails: the allowed side can cheaply
    # construct a semantic alias for a masked/cancelled parent expression.
    for child in operands:
        try:
            children.append(_import_source(state, work, physical, child, mapping, failed, semantic))
        except _Bypass:
            children.append(None)
            bypass = True
    if bypass:
        alias = physical.semantic.get(state.values[wire]) if semantic else None
        if alias is not None:
            work["source_semantic_alias_hits"] += 1
            mapping[wire] = alias
            return alias
        failed.add(wire)
        raise _Bypass
    result = physical.nand(*children)
    mapping[wire] = result
    work["source_NANDs_imported"] += 1
    return result


def _new_physical(state, work, triple, bits, source_wires=None, prior=None):
    solver = _engine(state)
    physical = _joint._Physical(solver)
    requested = tuple(source_wires) if source_wires is not None else (None,) * len(bits)
    if len(requested) != len(bits):
        raise ValueError("one source hint per summary bit")
    mapping = {wire: j for j, wire in enumerate(state.parent.frontier)}
    mapping.update({state.parent.n: state.m, state.parent.n + 1: state.m + 1})
    taps, retained = [], []
    for bit, requested_wire in zip(bits, requested):
        work["summary_source_requests"] += 1
        record = _source_record(state, work, triple, requested_wire) if requested_wire is not None else None
        wire = requested_wire if record is not None and record["truth"] == bit else None
        if wire is None:
            for candidate in _local_sources(state, work, triple):
                if candidate["truth"] == bit:
                    wire = candidate["wire"]
                    break
        if wire is not None:
            tap = _import_source(state, work, physical, wire, mapping, set(), semantic=True)
            retained.append(wire)
            work["summary_source_wires_reused"] += 1
        else:
            # The old physical encoder can be purchased separately. Its
            # primitive cone is reusable only if its stage group/code match.
            tap = _prior_tap(state, work, physical, triple, bit, prior)
            if tap is None:
                tap = physical.build(solver._recipe(3, bit), triple)
                work["summary_bits_synthesized"] += 1
            retained.append(None)
        taps.append(tap)
    outside = tuple(j for j in range(state.m) if j not in triple)
    physical.enter_cut(outside, taps)
    allowed = {state.parent.frontier[j]: j for j in outside}
    allowed.update({state.parent.n: state.m, state.parent.n + 1: state.m + 1})
    for wire, tap in zip(retained, taps):
        if wire is not None:
            allowed[wire] = tap
    return physical, taps, retained, allowed


def _prior_tap(state, work, physical, triple, bit, prior):
    if prior is None or tuple(prior.get("triple", ())) != triple:
        return None
    old_bits = prior.get("summary_truths", ())
    if bit not in old_bits:
        return None
    circuit = prior.get("circuit")
    taps = prior.get("summary_wires", ())
    if not circuit or circuit.get("n") != state.m or len(taps) != len(old_bits):
        return None
    selected = taps[list(old_bits).index(bit)]
    memo = {j: j for j in range(state.m + 2)}
    def build(wire):
        if wire in memo:
            return memo[wire]
        a, b = circuit["gates"][wire - state.m - 2]
        memo[wire] = physical.nand(build(a), build(b))
        work["prior_encoder_NANDs_imported"] += 1
        return memo[wire]
    # A trusted purchased answer is still checked for local dependencies.
    def deps(wire):
        if wire < state.m:
            return {wire}
        if wire < state.m + 2:
            return set()
        a, b = circuit["gates"][wire - state.m - 2]
        return deps(a) | deps(b)
    if not deps(selected) <= set(triple):
        return None
    tap = build(selected)
    mask, offsets, _ = _engine(state)._layout(triple)
    mask &= state.parent.full
    expected = 0
    for local, offset in enumerate(offsets):
        if (bit >> local) & 1:
            expected |= mask << offset
            work["prior_encoder_truth_blocks"] += 1
    if physical.values[tap] != expected:
        return None
    work["prior_encoder_taps_reused"] += 1
    return tap


def _answer(state, work, physical, ends, taps, triple, bits, count, retained, reuse_flags):
    observed = tuple(physical.values[wire] for wire in ends)
    work["returned_table_comparisons"] += 2
    if observed != state.tables:
        raise AssertionError("returned physical stage program is incorrect")
    circuit, final_taps, used, fanout, shared_gates = physical.finish(ends, taps)
    shared = _shared(state, work)
    width = len(bits)
    return {"status": "exact", "n": state.m, "arm": "primitive", "triple": list(triple),
            "width": width, "class_count": count, "summary_wires": final_taps,
            "summary_truths": list(bits), "circuit": circuit, "truth": list(observed),
            "outputs": circuit["outputs"], "expanded_NANDs": len(circuit["gates"]),
            "summary_wires_by_output": used, "summary_pin_fanouts": fanout,
            "shared_gates": shared_gates, "shared_summary_wires": len(set(used[0]) & set(used[1])),
            "shared_support": list(shared), "eligible_groups": comb(len(shared), 3),
            "retained_source_wires": list(retained), "output_reuse": reuse_flags,
            "global_minimum_certified": width == 1 or width == state._global_width,
            "fold_uses": 0, "named_fold_uses": 0, "flat_fold_uses": 0}


def _reuse(state, work, triple, taps_abs):
    triple = _group(triple, state.m)
    taps_abs = tuple(taps_abs)
    if len(taps_abs) not in (1, 2, 3) or not all(j in _shared(state, work) for j in triple):
        work["reuse_ineligible"] += 1
        return None
    records = {wire: _source_record(state, work, triple, wire) for wire in taps_abs}
    if any(record is None for record in records.values()):
        work["reuse_invalid_current_source"] += 1
        return None
    bits = tuple(records[wire]["truth"] for wire in taps_abs)
    physical, taps, retained, mapping = _new_physical(state, work, triple, bits, taps_abs)
    ends, flags, failed = [], [], set()
    for output in state.output_wires:
        aliases = work["source_semantic_alias_hits"]
        try:
            ends.append(_import_source(state, work, physical, output, mapping, failed, semantic=True))
        except _Bypass:
            work["reuse_output_bypasses"] += 1
            return None
        flags.append("semantic_alias" if work["source_semantic_alias_hits"] > aliases else "source")
    if len(bits) == 1:
        count = 2  # physical cut + shared essentiality proves exactly2.
        state._global_width = 1
        work["onebit_counts_inferred_from_cut"] += 1
    else:
        count = _partition(state, work, triple)["class_count"]
    return _answer(state, work, physical, ends, taps, triple, bits, count, retained, flags)


def reuse(state, triple, taps_abs):
    return _measure(state, _reuse, triple, taps_abs)


def _finish(state, work, triple, bits=None, source_wires=None, prior=None):
    triple = _group(triple, state.m)
    info = _partition(state, work, triple)
    if not info["eligible"]:
        work["finish_ineligible"] += 1
        return None
    solver = _engine(state)
    classes, columns, count = info["classes"], info["columns"], info["class_count"]
    if bits is None:
        bits = None
        if count == 2:
            h = sum(c << i for i, c in enumerate(classes))
            for record in _local_sources(state, work, triple):
                if record["truth"] in (h, h ^ 255):
                    bits, source_wires = (record["truth"],), (record["wire"],)
                    break
        if bits is None:
            bits = solver._code(classes, columns, count, None)[0]
    bits = tuple(bits)
    if (len(bits) != info["width"] or any(type(b) is not int or not 0 <= b < 256 for b in bits)):
        work["finish_nonminimal_local_code"] += 1
        return None
    codes = tuple(sum(((bit >> row) & 1) << i for i, bit in enumerate(bits)) for row in range(8))
    seen = {}
    for row, code in enumerate(codes):
        work["finish_code_checks"] += 1
        if seen.setdefault(code, classes[row]) != classes[row]:
            work["finish_insufficient_code"] += 1
            return None
    # Equal codes must have equal residuals. Equal residuals MAY use different
    # codes, including a3-class joint partition occupying all4 two-bit words.
    individual = solver._individual_classes(columns)
    projections = tuple(solver._projections(labels, codes, len(bits)) for labels in individual)
    physical, taps, retained, mapping = _new_physical(state, work, triple, bits, source_wires, prior)
    ends, flags, failed, dense = [], [], set(), {}
    for output_index, output in enumerate(state.output_wires):
        alias_before = work["source_semantic_alias_hits"]
        try:
            end = _import_source(state, work, physical, output, mapping, failed, semantic=True)
            flag = "semantic_alias" if work["source_semantic_alias_hits"] > alias_before else "source"
        except _Bypass:
            projection = projections[output_index]
            quotient = solver._quotient(output_index, projection, columns, info["outside"], triple, dense)
            subset = projection[0]
            wires = info["outside"] + tuple(taps[j] for j in subset)
            end = physical.build(solver._recipe(len(wires), quotient), wires)
            flag = "synthesized"
            work["consumer_functions_repaired"] += 1
        ends.append(end)
        flags.append(flag)
    return _answer(state, work, physical, ends, taps, triple, bits, count, retained, flags)


def finish(state, triple, bits=None, source_wires=None, prior=None):
    return _measure(state, _finish, triple, bits, source_wires, prior)


def _priorities(state, work, hint=None):
    shared = _shared(state, work)
    result, seen = [], set()
    def add(group):
        group = tuple(group)
        if group not in seen and all(j in shared for j in group):
            result.append(group)
            seen.add(group)
    if hint is not None:
        add(_group(hint, state.m))
        work["ordinary_hint_candidates"] += 1
    distance = {}
    if state.edit is not None:
        pending = deque([(state.edit["gate"], 0)])
        while pending:
            wire, depth = pending.popleft()
            if wire in distance:
                continue
            distance[wire] = depth
            work["ordinary_adjacency_vertices"] += 1
            if wire >= state.parent.first_suffix:
                for parent in state.gates[wire - state.parent.first_gate]:
                    pending.append((parent, depth + 1))
                    work["ordinary_adjacency_edges"] += 1
    pieces = sorted(enumerate(state.parent.pieces), key=lambda item: (
        min((distance.get(w, 1 << 30) for w in (item[1]["bit"], *item[1]["ports"])), default=1 << 30),
        not any(w in state.affected for w in item[1]["ports"]), item[0]))
    for _, piece in pieces:
        add(piece["inputs"])
        work["ordinary_history_candidates"] += 1
    shared_mask = sum(1 << j for j in shared)
    masks = set()
    for support in state.supports.values():
        work["ordinary_source_support_tests"] += 1
        if support.bit_count() == 3 and not support & ~shared_mask:
            masks.add(support)
    for mask in sorted(masks):
        add(tuple(j for j in shared if mask & (1 << j)))
    return result


def _select(state, work, hint=None, incumbent=None):
    shared = _shared(state, work)
    if len(shared) < 3:
        return None
    best, bound, incumbent_group, incumbent_width = None, 8, None, None
    if incumbent is not None:
        incumbent_group = _group(incumbent["triple"], state.m)
        incumbent_width = incumbent["width"]
        info = _partition(state, work, incumbent_group)
        if info["eligible"] and info["width"] <= incumbent_width:
            best = info
            if info["width"] == 1:
                state._global_width = 1
                return {**info, "incumbent_retained": incumbent_width == 1}
            bound = 1 << (info["width"] - 1)
    order, seen = _priorities(state, work, hint), set()
    for triple in (*order, *combinations(shared, 3)):
        if triple in seen:
            continue
        seen.add(triple)
        if best is not None and triple == best["triple"]:
            continue
        info = _partition(state, work, triple, bound)
        if info is None:
            continue
        best = info
        work["global_incumbent_updates"] += 1
        if info["width"] == 1:
            break
        bound = 1 << (info["width"] - 1)
    state._global_width = best["width"]
    return {**best, "incumbent_retained": (best["triple"] == incumbent_group and best["width"] == incumbent_width)}


def select(state, hint=None, incumbent=None):
    return _measure(state, _select, hint, incumbent)


def _source_cut(state, work, triple, width):
    """Complete existing-source single/pair cut; raw group taps are allowed."""
    mask = sum(1 << j for j in triple)
    candidates = [record["wire"] for record in _local_sources(state, work, triple)]
    if not candidates:
        return None
    bits = {wire: 1 << i for i, wire in enumerate(candidates)}
    full = (1 << len(candidates)) - 1
    work["ordinary_structural_group_tests"] += 1
    def mandatory(removed=None):
        dom = {state.parent.n: full, state.parent.n + 1: full}
        for j, wire in enumerate(state.parent.frontier):
            dom[wire] = bits.get(wire, 0) if j in triple else full
        if removed in dom:
            dom[removed] = full
        for index in range(state.parent.upstream_count, len(state.gates)):
            wire = state.parent.first_gate + index
            work["ordinary_dominator_gate_visits"] += 1
            if wire == removed:
                dom[wire] = full
            else:
                a, b = state.gates[index]
                dom[wire] = (dom[a] & dom[b]) | bits.get(wire, 0)
        return dom[state.output_wires[0]] & dom[state.output_wires[1]]
    if width == 1:
        value = mandatory()
        return None if not value else (candidates[(value & -value).bit_length() - 1],)
    for i, first in enumerate(candidates):
        value = mandatory(first) & (full ^ ((1 << (i + 1)) - 1))
        if value:
            return first, candidates[(value & -value).bit_length() - 1]
    return None


def _ordinary(state, work, hint=None, prior=None):
    priorities = _priorities(state, work, hint)
    # Give the ordinary arm the same contextual historical bit opportunity,
    # using current tables and semantic aliases, before broad generic work.
    for triple in priorities:
        historical = [p["bit"] for p in state.parent.pieces if p["inputs"] == triple]
        for wire in historical:
            work["ordinary_historical_wire_attempts"] += 1
            answer = _reuse(state, work, triple, (wire,))
            if answer is not None:
                answer["route"] = "ordinary-history-source"
                return answer
        taps = _source_cut(state, work, triple, 1)
        if taps is not None:
            answer = _reuse(state, work, triple, taps)
            if answer is not None:
                answer["route"] = "ordinary-structural-source"
                return answer
    # A purchased encoder is available in addition to the original DAG.
    if prior is not None and hint is not None and tuple(prior.get("triple", ())) == tuple(hint):
        answer = _finish(state, work, tuple(hint), prior.get("summary_truths"), prior=prior)
        if answer is not None and answer["width"] == 1:
            state._global_width = 1
            answer["global_minimum_certified"] = True
            answer["route"] = "ordinary-prior-encoder"
            return answer
    incumbent = None
    for triple in priorities:
        taps = _source_cut(state, work, triple, 2)
        if taps is not None:
            incumbent = _reuse(state, work, triple, taps)
            if incumbent is not None:
                break
    selected = _select(state, work, hint, incumbent)
    if selected is None:
        return {"status": "no_eligible_triple", "n": state.m, "circuit": None,
                "triple": None, "width": None, "class_count": None, "summary_wires": []}
    if incumbent is not None and selected["incumbent_retained"]:
        incumbent["global_minimum_certified"] = True
        incumbent["route"] = "ordinary-two-source-cut"
        return incumbent
    answer = _finish(state, work, selected["triple"], prior=prior)
    if answer is None:
        raise AssertionError("exact ordinary selection lacked a physical program")
    answer["route"] = "ordinary-exact-repair"
    return answer


def ordinary(state, hint=None, prior=None):
    return _measure(state, _ordinary, hint, prior)


class Ordinary:
    def __init__(self, parent, hint=None, prior=None):
        self.parent, self.hint, self.prior = parent, hint, prior
    def solve(self, state):
        if state.parent is not self.parent:
            raise ValueError("ordinary context mismatch")
        return ordinary(state, self.hint, self.prior)


def self_test():
    """Small standalone source circuits; no generator/panel imports."""
    n = 7
    gates = []
    def nand(a, b):
        gates.append([a, b])
        return n + 1 + len(gates)
    def land(a, b):
        h = nand(a, b)
        return nand(h, h)
    def xor(a, b):
        h = nand(a, b)
        return nand(nand(a, h), nand(b, h))
    first = nand(0, 0)
    frontier = [first, *range(1, n)]
    a, b, c, z, v, *_ = frontier
    ab = land(a, b)
    h = xor(ab, c)
    j = xor(land(a, c), b)
    alias = nand(nand(h, h), nand(h, h))
    p0 = xor(h, z)
    editable = nand(h, v)
    p1 = nand(editable, editable)
    case = {"n": n, "gates": gates, "upstream_count": 1, "frontier": frontier,
            "outputs": [p0, p1], "pieces": [{"inputs": [0, 1, 2], "bit": h, "ports": [p0, p1]}]}
    parent = Parent(case)
    def check(state, answer):
        assert answer["status"] == "exact"
        circ = answer["circuit"]
        group, taps = set(answer["triple"]), set(answer["summary_wires"])
        deps = [{i} for i in range(parent.m)] + [set(), set()]
        cut = [set() if i in taps else {i} for i in range(parent.m)] + [set(), set()]
        for index, (a0, b0) in enumerate(circ["gates"]):
            wire = parent.m + 2 + index
            deps.append(deps[a0] | deps[b0])
            cut.append(set() if wire in taps else cut[a0] | cut[b0])
        assert all(deps[t] <= group for t in taps)
        assert all(not cut[o] & group for o in circ["outputs"])
        for row in range(1 << parent.m):
            values = [(row >> i) & 1 for i in range(parent.m)] + [0, 1]
            for a0, b0 in circ["gates"]:
                values.append(1 ^ (values[a0] & values[b0]))
            assert tuple(values[o] for o in circ["outputs"]) == tuple((t >> row) & 1 for t in state.tables)
    original = parent.edit(None)
    old, _ = ordinary(original)
    check(original, old)
    same = parent.edit({"gate": editable, "pin": 0, "to": alias})
    answer, _ = ordinary(same)
    check(same, answer)
    assert answer["width"] == 1
    broken = parent.edit({"gate": editable, "pin": 0, "to": j})
    answer, _ = ordinary(broken, hint=old["triple"], prior=old)
    check(broken, answer)
    assert answer["width"] == 2
    info, _ = partition(broken, (0, 1, 2))
    extra = next(record for record in local_sources(broken, (0, 1, 2))[0] if record["wire"] == j)
    fixed, _ = finish(broken, (0, 1, 2), bits=(parent.pieces[0]["bit_truth"], extra["truth"]),
                      source_wires=(h, j))
    check(broken, fixed)
    selected, _ = select(broken, incumbent=fixed)
    assert selected["width"] == 2 and selected["incumbent_retained"]
    assert info["count"] == 4
    # No completed program/partition/recipe can leak to a sibling query.
    sibling = parent.edit({"gate": editable, "pin": 0, "to": j})
    assert sibling._joint is None and not sibling._partitions and not sibling._locals
    assert parent.original_tables == original.tables and parent.gates == tuple(map(tuple, gates))
    assert broken.values[h] == parent.original_values[h]
    # A current source changed into a different local function cannot pass a
    # historical name match: retained source slot must follow actual bytes.
    wrong, _ = finish(broken, (0, 1, 2), bits=(parent.pieces[0]["bit_truth"], extra["truth"]),
                      source_wires=(j, h))
    check(broken, wrong)
    assert wrong["retained_source_wires"] != [j, h]
    # A feasible2-tap seed does not establish that2 bits are necessary on its
    # OWN triple. Here its XOR already is the old1-bit global interface.
    seeded_state = parent.edit(None)
    seeded, _ = reuse(seeded_state, (0, 1, 2), (ab, c))
    assert seeded["width"] == 2 and seeded["class_count"] == 2
    assert not seeded["global_minimum_certified"]
    improved, _ = select(seeded_state, incumbent=seeded)
    assert improved["width"] == 1 and not improved["incumbent_retained"]
    improved_answer, _ = finish(seeded_state, improved["triple"])
    check(seeded_state, improved_answer)
    # A3-class response partition may use all4 words of a pinned two-bit
    # code. Equal code implies equal response; the converse is not required.
    gates = []
    first = nand(0, 0)
    second_frontier = [first, *range(1, n)]
    a, b, c = second_frontier[:3]
    parity = xor(xor(a, b), c)
    and_port = land(parity, a)
    or_port = nand(nand(parity, parity), nand(a, a))
    three = Parent({"n": n, "gates": gates, "upstream_count": 1,
                    "frontier": second_frontier, "outputs": [and_port, or_port], "pieces": []})
    three_state = three.edit(None)
    three_info, _ = partition(three_state, (0, 1, 2))
    assert three_info["class_count"] == 3
    three_answer, _ = finish(three_state, (0, 1, 2), bits=(150, 170), source_wires=(parity, a))
    assert three_answer is not None and three_answer["class_count"] == 3 and three_answer["width"] == 2
    check(three_state, three_answer)
    return {"synthetic_only": True, "status": "passed", "old_and_preserving_width": 1,
            "broken_width": 2, "independent_branches_cut_and_source_validation": "passed",
            "seed_own_triple_onebit_and_threeclass_fourword_code": "passed"}


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("use --self-test; official cases are supplied by the caller")
    print(json.dumps(self_test(), sort_keys=True))
