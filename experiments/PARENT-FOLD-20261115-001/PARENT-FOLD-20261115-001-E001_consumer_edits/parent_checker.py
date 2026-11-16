"""Paid exact checker for the original parent and independently branched edits.

The minimum is over triples of *stage-frontier* inputs essential to both
outputs.  It is not a minimum over raw-input triples.  Only the unchanged
source expressions, generic group layouts, and explicitly verified original
answers are retained; no answer or expression cache is populated by an edit.
"""

from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter_ns, process_time_ns
from types import MappingProxyType


HISTORICAL_CHECKER = (
    "experiments/FOLD-TWO-OUTPUT-20261115-001/"
    "FOLD-TWO-OUTPUT-20261115-001-E001_joint_tables/checker.py"
)
HISTORICAL_SHA256 = "19b66a34415d14f73264eb2188cc984da28df250317f8aae9fa66c48438efdb0"
MINIMUM_UNIVERSE = "jointly-essential stage-frontier triples"
_HISTORICAL_CLASS = None


def _int(value, label, lower=0, upper=None):
    if type(value) is not int or value < lower or (upper is not None and value >= upper):
        raise ValueError(f"invalid {label}")
    return value


def _list(value, label, length=None):
    if not isinstance(value, (list, tuple)) or (length is not None and len(value) != length):
        raise ValueError(f"invalid {label}")
    return value


def _columns(n):
    rows = 1 << n
    full = (1 << rows) - 1
    return rows, full, tuple(full // ((1 << (1 << i)) + 1) << (1 << i) for i in range(n))


def _encoded(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    except (TypeError, ValueError) as exc:
        raise ValueError("return must have a finite JSON representation") from exc


def _historical_class(owner):
    global _HISTORICAL_CLASS
    if _HISTORICAL_CLASS is not None:
        owner._add("historical_checker_class_reuses", 1)
        return _HISTORICAL_CLASS
    path = Path(__file__).resolve().parents[3] / HISTORICAL_CHECKER
    source = path.read_bytes()
    if sha256(source).hexdigest() != HISTORICAL_SHA256:
        raise ValueError("historical checker source changed")
    owner._add("historical_source_bytes_hashed", len(source))
    owner._add("historical_checker_class_loads", 1)
    namespace = {"__name__": "_pinned_joint_checker", "__file__": str(path)}
    exec(compile(source, str(path), "exec"), namespace)
    _HISTORICAL_CLASS = namespace["JointChecker"]
    return _HISTORICAL_CLASS


class Checker:
    """Common verifier.  ``verify(edit, answer)`` returns work or raises.

    ``edit=None`` means the unchanged source.  A public case may include its
    allowed ``edits``; when present, each supplied edit must match one exactly.
    ``setup_work`` and ``work_counters()`` expose constructor cost and failures
    too.  CPU and wall measurements include validation and cache lookup work.
    """

    def __init__(self, case, *, raw_replay="history"):
        wall, cpu = perf_counter_ns(), process_time_ns()
        if raw_replay not in ("history", "direct"):
            raise ValueError("raw_replay must be history or direct")
        self.raw_replay = raw_replay
        self._work = {}
        self.last_work = {}
        self._original_verified = {}
        self._active = self._work
        # Freeze our own complete copy before any later caller mutation.
        self.case = json.loads(_encoded(case))
        self.case_id = self.case.get("id")
        self.source_sha256 = sha256(_encoded(self.case)).hexdigest()
        self.n = _int(self.case["n"], "raw input count", lower=1)
        self.gates = tuple(self._gates(self.case["gates"], self.n, "source"))
        self.upstream_count = _int(self.case["upstream_count"], "prefix length", upper=len(self.gates) + 1)
        self.raw_start = self.n + 2
        self.prefix_end = self.raw_start + self.upstream_count
        self.raw_end = self.raw_start + len(self.gates)
        self.frontier = tuple(_list(self.case["frontier"], "frontier"))
        self.m = len(self.frontier)
        if self.m < 3 or self.m > self.n or len(set(self.frontier)) != self.m:
            raise ValueError("frontier must contain distinct, jointly attainable stage inputs")
        for wire in self.frontier:
            _int(wire, "frontier wire", upper=self.prefix_end)
        self.outputs = tuple(_list(self.case["outputs"], "source outputs", 2))
        for wire in self.outputs:
            _int(wire, "source output", upper=self.raw_end)
        self.rows, self.full, self.columns = _columns(self.n)
        self.stage_rows, self.stage_full, self.stage_columns = _columns(self.m)
        self._add("raw_columns_built", self.n)
        self._add("stage_columns_built", self.m)
        raw = [*self.columns, 0, self.full]
        for a, b in self.gates:
            raw.append(self.full ^ (raw[a] & raw[b]))
        self._add("raw_setup_NAND_evaluations", len(self.gates))
        self._add("raw_setup_NAND_row_equivalents", len(self.gates) * self.rows)
        self._prefix_values = tuple(raw[:self.prefix_end])
        self._original_raw_values = tuple(raw)
        if self.raw_replay == "history":
            self._index_original_raw_expressions()
        self._original_raw_targets = tuple(raw[w] for w in self.outputs)
        self._raw_frontier = tuple(raw[w] for w in self.frontier)
        # Marginal balance/essentiality is insufficient.  Partition all raw
        # assignments by the complete frontier vector and require every cell.
        cells = [self.full]
        for column in self._raw_frontier:
            low = self.full ^ column
            self._add("frontier_cell_intersections", 2 * len(cells))
            cells = [cell & low for cell in cells] + [cell & column for cell in cells]
        if any(cell == 0 for cell in cells):
            raise ValueError("frontier signals are not jointly independently attainable")
        self._frontier_cells = tuple(cells)
        self._add("frontier_assignments_verified", len(cells))
        self._add("raw_frontier_assignments_covered", self.rows)

        # Only the generic, hash-pinned Python class is process-shared.  The
        # first use buys loading; every parent has fresh semantic authority.
        legacy = _historical_class(self)
        owner = self

        class MeteredChecker(legacy):
            def _essential(self, table):
                owner._add("stage_support_axis_tests", self.n)
                return super()._essential(table)

            def _classes(self, outputs, group, stop_above=None):
                owner._add("stage_class_calls", 1)
                owner._add("stage_layout_hits" if group in self.layouts else "stage_layout_builds", 1)
                return super()._classes(outputs, group, stop_above)

        self._joint = MeteredChecker(self.m)
        self._original_stage_values, self._source_map = self._stage_values(None)
        self._original_stage_targets = tuple(self._original_stage_values[self._source_map[w]] for w in self.outputs)
        self._check_raw_projection(self._original_raw_targets, self._original_stage_targets)
        self._check_pieces()
        self._edits = None
        if "edits" in self.case:
            self._edits = {}
            for edit in _list(self.case["edits"], "edits"):
                self._validate_edit(edit)
                key = _encoded(edit)
                ident = _encoded(edit.get("id"))
                if ident in self._edits:
                    raise ValueError("duplicate edit id")
                self._edits[ident] = key
        self._work["checker_setup_cpu_ns"] = process_time_ns() - cpu
        self._work["checker_setup_wall_ns"] = perf_counter_ns() - wall
        self.setup_work = dict(self._work)

    def _add(self, key, amount):
        self._active[key] = self._active.get(key, 0) + amount

    def _index_original_raw_expressions(self):
        """Index checked expressions, never merely original numeric wire IDs.

        Leaves are the distinct raw input identities and two constants.  An
        internal identity is interned from the unordered pair of its child
        identities.  Only this immutable original history supplies values.
        """
        identities = list(range(self.raw_start))
        values = list(self._original_raw_values[:self.raw_start])
        expressions = {}
        duplicates = 0
        for index, (a, b) in enumerate(self.gates):
            pair = tuple(sorted((identities[a], identities[b])))
            identity = expressions.get(pair)
            if identity is None:
                identity = len(values)
                expressions[pair] = identity
                values.append(self._original_raw_values[self.raw_start + index])
            else:
                duplicates += 1
            identities.append(identity)
        self._historical_raw_expressions = MappingProxyType(expressions)
        self._historical_raw_expression_values = tuple(values)
        self._prefix_expression_ids = tuple(identities[:self.prefix_end])
        self._add("historical_raw_source_identities", self.raw_start)
        self._add("historical_raw_expression_gates_indexed", len(self.gates))
        self._add("historical_raw_expression_duplicates", duplicates)
        self._add("historical_raw_expressions_retained", len(expressions))

    def _replay_raw_return(self, gates):
        """Exactly replay a validated return, optionally using original facts.

        New identities are local to this one replay and are discarded.  Even
        repeated new expressions are evaluated normally, so historical cache
        wins are not conflated with new within-return value caching.
        """
        raw = list(self._prefix_values)
        self._add("raw_return_prefix_NANDs_reused", self.upstream_count)
        count = len(gates) - self.upstream_count
        hits = 0
        if self.raw_replay == "direct":
            for a, b in gates[self.upstream_count:]:
                raw.append(self.full ^ (raw[a] & raw[b]))
            self._add("raw_return_direct_replays", 1)
            self._add("raw_return_direct_NAND_evaluations", count)
        else:
            identities = list(self._prefix_expression_ids)
            history = self._historical_raw_expressions
            historical_values = self._historical_raw_expression_values
            local = {}
            next_identity = len(historical_values)
            for a, b in gates[self.upstream_count:]:
                pair = tuple(sorted((identities[a], identities[b])))
                identity = history.get(pair)
                if identity is not None:
                    hits += 1
                    value = historical_values[identity]
                else:
                    value = self.full ^ (raw[a] & raw[b])
                    identity = local.get(pair)
                    if identity is None:
                        identity = next_identity
                        next_identity += 1
                        local[pair] = identity
                identities.append(identity)
                raw.append(value)
            self._add("raw_return_history_expression_lookups", count)
            self._add("raw_return_new_expression_identities", len(local))
        self._add("raw_return_history_expression_hits", hits)
        self._add("raw_return_history_expression_misses", count - hits if self.raw_replay == "history" else 0)
        self._add("raw_return_NANDs_reused", self.upstream_count + hits)
        self._add("raw_return_NAND_evaluations", count - hits)
        self._add("raw_return_NAND_row_equivalents", (count - hits) * self.rows)
        return raw

    @staticmethod
    def _gates(gates, n, label):
        result = []
        for index, pair in enumerate(_list(gates, f"{label} gates")):
            pair = _list(pair, f"{label} NAND", 2)
            result.append(tuple(_int(wire, f"{label} gate input", upper=n + 2 + index) for wire in pair))
        return result

    def _validate_edit(self, edit):
        if not isinstance(edit, dict):
            raise ValueError("invalid edit")
        _int(edit["gate"], "edited gate", lower=self.prefix_end, upper=self.raw_end)
        _int(edit["pin"], "edited pin", upper=2)
        _int(edit["to"], "replacement wire", upper=edit["gate"])

    def _selected_edit(self, edit):
        if edit is None:
            return None
        self._validate_edit(edit)
        if self._edits is not None and self._edits.get(_encoded(edit.get("id"))) != _encoded(edit):
            raise ValueError("edit does not match this immutable public case")
        return (edit["gate"], edit["pin"], edit["to"])

    def _stage_values(self, selected):
        if selected is not None:
            values = list(self._original_stage_values)
            changed = [False] * len(values)
            mapping = self._source_map
            recomputed = different = 0
            for index in range(self.upstream_count, len(self.gates)):
                absolute = self.raw_start + index
                pair = list(self.gates[index])
                if selected[0] == absolute:
                    pair[selected[1]] = selected[2]
                try:
                    a, b = (mapping[w] for w in pair)
                except KeyError as exc:
                    raise ValueError("consumer reads a prefix wire outside the declared frontier") from exc
                wire = mapping[absolute]
                if selected[0] == absolute or changed[a] or changed[b]:
                    recomputed += 1
                    value = self.stage_full ^ (values[a] & values[b])
                    changed[wire] = value != values[wire]
                    different += changed[wire]
                    values[wire] = value
            count = len(self.gates) - self.upstream_count
            self._add("source_stage_gates_examined", count)
            self._add("source_stage_NAND_evaluations", recomputed)
            self._add("source_stage_NANDs_reused", count - recomputed)
            self._add("source_stage_changed_values", different)
            self._add("source_stage_recomputed_unchanged_values", recomputed - different)
            return tuple(values), mapping
        values = [*self.stage_columns, 0, self.stage_full]
        mapping = {wire: i for i, wire in enumerate(self.frontier)}
        mapping.update({self.n: self.m, self.n + 1: self.m + 1})
        for index in range(self.upstream_count, len(self.gates)):
            absolute = self.raw_start + index
            pair = list(self.gates[index])
            if selected is not None and selected[0] == absolute:
                pair[selected[1]] = selected[2]
            try:
                a, b = (mapping[w] for w in pair)
            except KeyError as exc:
                raise ValueError("consumer reads a prefix wire outside the declared frontier") from exc
            mapping[absolute] = len(values)
            values.append(self.stage_full ^ (values[a] & values[b]))
        if any(wire not in mapping for wire in self.outputs):
            raise ValueError("source output is outside the declared stage")
        self._add("source_stage_NAND_evaluations", len(self.gates) - self.upstream_count)
        return tuple(values), mapping

    def _raw_targets(self, selected):
        if selected is None:
            self._add("original_source_target_reuses", 1)
            return self._original_raw_targets, self._original_stage_targets
        raw = list(self._original_raw_values)
        changed = [False] * len(raw)
        recomputed = different = 0
        self._add("raw_source_prefix_NANDs_reused", self.upstream_count)
        for index in range(self.upstream_count, len(self.gates)):
            absolute = self.raw_start + index
            pair = list(self.gates[index])
            if selected[0] == absolute:
                pair[selected[1]] = selected[2]
            a, b = pair
            if selected[0] == absolute or changed[a] or changed[b]:
                recomputed += 1
                value = self.full ^ (raw[a] & raw[b])
                changed[absolute] = value != raw[absolute]
                different += changed[absolute]
                raw[absolute] = value
        count = len(self.gates) - self.upstream_count
        self._add("raw_source_gates_examined", count)
        self._add("raw_source_NAND_evaluations", recomputed)
        self._add("raw_source_NAND_row_equivalents", recomputed * self.rows)
        self._add("raw_source_unchanged_NANDs_reused", count - recomputed)
        self._add("raw_source_changed_values", different)
        self._add("raw_source_recomputed_unchanged_values", recomputed - different)
        stage, mapping = self._stage_values(selected)
        targets = tuple(raw[w] for w in self.outputs)
        stage_targets = tuple(stage[mapping[w]] for w in self.outputs)
        self._check_raw_projection(targets, stage_targets)
        return targets, stage_targets

    def _check_raw_projection(self, raw_targets, stage_targets):
        # This also catches accidental bit-order or source-wiring mistakes in
        # the independently evaluated stage representation.
        for raw, stage in zip(raw_targets, stage_targets):
            for assignment, cell in enumerate(self._frontier_cells):
                expected = cell if (stage >> assignment) & 1 else 0
                if raw & cell != expected:
                    raise ValueError("raw source behavior is not the claimed stage behavior")
        self._add("raw_stage_projection_tests", 2 * self.stage_rows)
        self._add("raw_stage_output_bits_covered", 2 * self.rows)

    def _check_pieces(self):
        values, mapping = self._original_stage_values, self._source_map
        for piece in _list(self.case.get("pieces", []), "historical pieces"):
            group = tuple(_list(piece["inputs"], "piece inputs", 3))
            if tuple(sorted(group)) != group or len(set(group)) != 3:
                raise ValueError("piece inputs must be three sorted distinct stage indices")
            for axis in group:
                _int(axis, "piece stage input", upper=self.m)
            bit = _int(piece["bit"], "piece bit", upper=self.raw_end)
            ports = tuple(_list(piece["ports"], "piece ports", 2))
            for port in ports:
                _int(port, "piece port", upper=self.raw_end)
            if bit not in mapping or any(port not in mapping for port in ports):
                raise ValueError("piece bit or port is outside the declared stage")
            truth = values[mapping[bit]]
            if self._joint._essential(truth) != set(group):
                raise ValueError("historical bit is not a local nonconstant group summary")
            mask, offsets = self._layout(group)
            representatives = {}
            for offset in offsets:
                code = (truth >> offset) & 1
                residual = tuple((values[mapping[port]] >> offset) & mask for port in ports)
                if code in representatives and representatives[code] != residual:
                    raise ValueError("historical ports do not factor through the claimed bit")
                representatives[code] = residual
            self._add("historical_piece_residual_pair_checks", 8)
            self._add("historical_pieces_verified", 1)

    def _layout(self, group):
        layout = self._joint.layouts.get(group)
        if layout is None:
            mask, offsets = self.stage_full, [0]
            for axis in group:
                mask &= self._joint.zero[axis]
                offsets += [offset + (1 << axis) for offset in offsets]
            layout = self._joint.layouts[group] = (mask, offsets)
            self._add("stage_layout_builds", 1)
        else:
            self._add("stage_layout_hits", 1)
        return layout

    def _return_shape(self, answer, cache_key):
        if not isinstance(answer, dict) or answer.get("status") != "exact":
            raise ValueError("incomplete exact parent answer")
        if _int(answer["n"], "answer stage input count") != self.m:
            raise ValueError("answer stage input size changed")
        group = tuple(_list(answer["triple"], "answer triple", 3))
        for axis in group:
            _int(axis, "answer group input", upper=self.m)
        _int(answer["width"], "summary width", lower=1, upper=4)
        _int(answer["class_count"], "class count", lower=2, upper=9)
        circuit = answer["circuit"]
        if _int(circuit.get("n", self.m), "circuit stage input count") != self.m:
            raise ValueError("circuit stage input size changed")
        gates = tuple(self._gates(circuit["gates"], self.m, "returned stage"))
        bound = self.m + 2 + len(gates)
        ends = tuple(_list(circuit["outputs"], "returned stage outputs", 2))
        taps = tuple(_list(answer["summary_wires"], "summary wires"))
        for wire in ends + taps:
            _int(wire, "returned stage endpoint", upper=bound)
        physical = answer.get("physical")
        if not isinstance(physical, dict):
            raise ValueError("serialized physical return is required")
        if _int(physical["n"], "physical raw input count") != self.n:
            raise ValueError("physical input size changed")
        raw_frontier = tuple(_list(physical["frontier"], "physical frontier"))
        for wire in raw_frontier:
            _int(wire, "physical frontier wire", upper=self.prefix_end)
        if raw_frontier != self.frontier:
            raise ValueError("physical frontier changed")
        raw_gates = tuple(self._gates(physical["gates"], self.n, "returned raw"))
        expected = list(self.gates[:self.upstream_count])
        lift = [*self.frontier, self.n, self.n + 1]
        for a, b in gates:
            expected.append((lift[a], lift[b]))
            lift.append(self.n + 2 + len(expected) - 1)
        if raw_gates != tuple(expected):
            raise ValueError("physical gates are not the unchanged prefix plus the lifted stage program")
        raw_ends = tuple(_list(physical["outputs"], "physical outputs", 2))
        raw_taps = tuple(_list(physical["summary_wires"], "physical summary wires"))
        for wire in raw_ends + raw_taps:
            _int(wire, "physical endpoint", upper=self.raw_start + len(raw_gates))
        if raw_ends != tuple(lift[w] for w in ends) or raw_taps != tuple(lift[w] for w in taps):
            raise ValueError("physical outputs or taps do not match the stage lift")
        self._add("physical_prefix_gates_compared", self.upstream_count)
        self._add("physical_stage_gates_linked", len(gates))
        core = dict(status="exact", n=self.m, triple=list(group), width=answer["width"],
                    class_count=answer["class_count"], summary_wires=list(taps),
                    circuit=dict(n=self.m, gates=gates, outputs=ends),
                    physical=dict(n=self.n, gates=raw_gates, outputs=raw_ends,
                                  summary_wires=raw_taps, frontier=self.frontier))
        key = _encoded(core) if cache_key else None
        if key is not None:
            self._add("original_cache_key_bytes", len(key))
        return core, key, raw_gates, raw_ends

    def verify(self, edit, answer):
        wall, cpu = perf_counter_ns(), process_time_ns()
        work = {"verification_calls": 1}
        self._active = work
        try:
            selected = self._selected_edit(edit)
            raw_targets, stage_targets = self._raw_targets(selected)
            core, key, raw_gates, raw_ends = self._return_shape(
                answer, selected is None or bool(self._original_verified))
            if "truth" in answer and tuple(answer["truth"]) != stage_targets:
                raise ValueError("reported stage answers are false")
            if "outputs" in answer and tuple(answer["outputs"]) != tuple(core["circuit"]["outputs"]):
                raise ValueError("reported stage outputs disagree with the program")
            prior = self._original_verified.get(key)
            if prior is not None and raw_targets == self._original_raw_targets:
                # Reuse only authority actually bought for the immutable
                # original, never a sibling edit's target, minimum or program.
                receipt = dict(prior)
                self._add("original_verification_cache_hits", 1)
                self._add("raw_return_NANDs_reused", len(raw_gates))
                self._add("raw_return_prefix_NANDs_reused", self.upstream_count)
                self._add("raw_return_verified_program_NANDs_reused", len(raw_gates) - self.upstream_count)
            else:
                receipt = self._joint.verify(stage_targets, core)
                count = len(core["circuit"]["gates"])
                self._add("returned_stage_NAND_evaluations", count)
                self._add("returned_stage_output_bits_compared", 2 * self.stage_rows)
                self._add("global_minimum_alternative_groups_checked", receipt["alternatives_checked"])
                raw = self._replay_raw_return(raw_gates)
                if tuple(raw[w] for w in raw_ends) != raw_targets:
                    raise ValueError("serialized physical return disagrees with edited raw outputs")
                self._add("raw_return_output_bits_compared", 2 * self.rows)
                if selected is None:
                    self._original_verified[key] = dict(receipt)
                    self._add("original_verifications_retained", 1)
            work.update(exact=True, width=receipt["width"], classes=receipt["classes"],
                        minimum_universe=MINIMUM_UNIVERSE, structural_locality=True,
                        raw_assignments=self.rows, stage_assignments=self.stage_rows,
                        raw_outputs=2, raw_gates_returned=len(raw_gates),
                        raw_return_replay=self.raw_replay,
                        stage_gates_returned=len(core["circuit"]["gates"]),
                        active_stage_gates=receipt["active_gates"],
                        shared_stage_gates=receipt["shared_gates"],
                        shared_summary_wires=receipt["shared_summary_wires"],
                        source_sha256=self.source_sha256,
                        historical_checker_sha256=HISTORICAL_SHA256)
            return work
        finally:
            work["verification_cpu_ns"] = process_time_ns() - cpu
            work["verification_wall_ns"] = perf_counter_ns() - wall
            self.last_work = dict(work)
            for name, value in work.items():
                if type(value) is int:
                    self._work[name] = self._work.get(name, 0) + value
            self._active = self._work

    def work_counters(self):
        return dict(self._work)

