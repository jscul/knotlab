"""Current two-axis certificates inside the frozen paid parent verifier.

``pair_proofs`` contains [axis0, axis1, outside] with axis0 < axis1 and
both axis bits clear in outside.  The optional fourth integer selects three
or four corners: bits 0,1,2,3 mean outside, axis0, axis1, both.  No supplied
output value is trusted.  Three distinct current joint outputs license only
a width-at-least-two bound for triples containing those two axes.
"""

import ast
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import sys
from time import perf_counter_ns, process_time_ns
from types import MethodType, ModuleType


PARENT_PATH = (
    "experiments/PARENT-FOLD-20261115-001/"
    "PARENT-FOLD-20261115-001-E001_consumer_edits/parent_checker.py"
)
PARENT_SHA256 = "86ee82cd29d9e948dd6e6755b17f5a526bee289c3f99edde5a9319f88652e069"


def _parent_module():
    name = "_pair_pinned_parent_checker_" + PARENT_SHA256
    module = sys.modules.get(name)
    if module is not None:
        return module
    path = Path(__file__).resolve().parents[3] / PARENT_PATH
    source = path.read_bytes()
    if sha256(source).hexdigest() != PARENT_SHA256:
        raise ValueError("frozen parent checker source changed")
    module = ModuleType(name)
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec"), module.__dict__)
    sys.modules[name] = module
    return module


_PARENT = _parent_module()
HistoricalChecker = _PARENT.Checker
_JOINT_VERIFY = {}


def _joint_verify(profile):
    """Redirect only alternatives; optionally time the two unchanged blocks."""
    if profile in _JOINT_VERIFY:
        return _JOINT_VERIFY[profile]
    path = Path(__file__).resolve().parents[3] / _PARENT.HISTORICAL_CHECKER
    source = path.read_bytes()
    if sha256(source).hexdigest() != _PARENT.HISTORICAL_SHA256:
        raise ValueError("historical joint checker source changed")
    module = ast.parse(source, filename=str(path))
    owner = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == "JointChecker")
    function = next(node for node in owner.body if isinstance(node, ast.FunctionDef) and node.name == "verify")
    original = [ast.dump(node) for node in function.body]
    comparison = ast.parse("bits > 1", mode="eval").body
    alternatives_if = next(node for node in ast.walk(function) if isinstance(node, ast.If)
                           and ast.dump(node.test) == ast.dump(comparison))
    original_alternatives = alternatives_if.body
    alternative_timer = None
    if profile:
        alternative_timer = ast.parse(
            "_pair_alternatives_begin = _pair_clock()\n"
            "try:\n    pass\n"
            "finally:\n"
            "    self._pair_owner._add('alternative_checks_cpu_ns', _pair_clock() - _pair_alternatives_begin)\n"
        ).body
        alternative_timer[1].body = original_alternatives
        alternatives_if.body = alternative_timer
    loop = next(node for node in ast.walk(function) if isinstance(node, ast.For)
                and isinstance(node.target, ast.Name) and node.target.id == "other")
    old_iterator = loop.iter
    expected = ast.parse("combinations(sorted(common), 3)", mode="eval").body
    if ast.dump(old_iterator) != ast.dump(expected):
        raise ValueError("historical alternative iterator changed")
    replacement = ast.parse(
        "self._pair_owner._alternatives_to_check(common, group, bits, targets)", mode="eval").body
    loop.iter = replacement
    boundary = next(i for i, node in enumerate(function.body)
                    if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "gates" for target in node.targets))
    prefix, suffix = function.body[:boundary], function.body[boundary:]
    if profile:
        timed = []
        for label, body in (("minimum_phase_cpu_ns", prefix), ("stage_program_and_cut_cpu_ns", suffix)):
            scaffold = ast.parse(
                "_pair_block_begin = _pair_clock()\n"
                "try:\n    pass\n"
                "finally:\n"
                f"    self._pair_owner._add('{label}', _pair_clock() - _pair_block_begin)\n"
            ).body
            scaffold[1].body = body
            timed.extend(scaffold)
        function.body = timed
        recovered = timed[1].body + timed[3].body
    else:
        recovered = function.body
    # Restoring that one iterator must reproduce every original statement,
    # including branch/raise/return order.  No physical/cut statement changes.
    loop.iter = old_iterator
    alternatives_if.body = original_alternatives
    if [ast.dump(node) for node in recovered] != original:
        raise ValueError("checker transformation changed another original statement")
    loop.iter = replacement
    if alternative_timer is not None:
        alternatives_if.body = alternative_timer
    code = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    namespace = {"combinations": combinations, "_pair_clock": process_time_ns}
    exec(compile(code, str(path), "exec"), namespace)
    _JOINT_VERIFY[profile] = namespace["verify"]
    return _JOINT_VERIFY[profile]


class PairChecker(HistoricalChecker):
    """Check optional current certificates, then retain exact fallback.

    The chosen triple always receives its full exact residual check.  A
    successful certificate replaces only a narrower-alternative check whose
    bound is two classes.  Width-three answers and every uncovered triple use
    the frozen exact checker.  The superclass retains raw replay, structural
    cuts, strict physical linking, and original-only expression/value reuse.
    """

    def __init__(self, case, *, raw_replay="history", geometry_cache=None,
                 exact_fallback="compact", profile=True, profile_alternative_calls=False):
        wall, cpu = perf_counter_ns(), process_time_ns()
        if exact_fallback not in ("compact", "historical"):
            raise ValueError("exact_fallback must be compact or historical")
        if geometry_cache is not None and not isinstance(geometry_cache, dict):
            raise ValueError("geometry_cache must be a dictionary of checker-owned layouts")
        self._profile = bool(profile)
        self._profile_alternative_calls = bool(profile_alternative_calls)
        self.exact_fallback = exact_fallback
        super().__init__(case, raw_replay=raw_replay)
        self._historical_exact_classes = self._joint._classes
        geometry = {} if geometry_cache is None else geometry_cache
        self._geometry = geometry
        shared = geometry.setdefault(("pair-checker-layouts", self.m), {})
        for group, (mask, offsets) in self._joint.layouts.items():
            layout = (mask, tuple(offsets))
            if group in shared:
                old_mask, old_offsets = shared[group]
                if old_mask != mask or tuple(old_offsets) != tuple(offsets):
                    raise ValueError("shared geometry conflicts with an independently derived layout")
            shared[group] = layout
        self._joint.layouts = shared
        self._packed_layouts = geometry.setdefault(("pair-checker-packed-layouts", self.m), {})
        self._exact_classes = self._compact_classes if exact_fallback == "compact" else self._historical_exact_classes
        self._joint._classes = self._classes_with_proofs
        self._joint._pair_owner = self
        self._joint.verify = MethodType(_joint_verify(self._profile), self._joint)
        self._pending_proofs = ()
        self._current_raw_targets = None
        self._current_stage_targets = None
        self._proofs_ready = False
        self._certified_pairs = set()
        self._proof_row_values = {}
        self._compact_joint = None
        self._work["checker_setup_cpu_ns"] = process_time_ns() - cpu
        self._work["checker_setup_wall_ns"] = perf_counter_ns() - wall
        self.setup_work = dict(self._work)

    def _alternatives_to_check(self, common, group, bits, targets):
        axes = tuple(sorted(common))
        if bits != 2 or not self._pending_proofs:
            return combinations(axes, 3)
        if tuple(targets) != self._current_stage_targets:
            return combinations(axes, 3)
        self._prepare_proofs()
        if not self._certified_pairs:
            return combinations(axes, 3)
        key = ("pair-checker-cover-layouts", self.m, axes)
        geometry = self._geometry.get(key)
        if geometry is None:
            triples = tuple(combinations(axes, 3))
            covers, locations = {}, {}
            for position, triple in enumerate(triples):
                a, b, c = (1 << axis for axis in triple)
                bit = 1 << position
                locations[triple] = position
                for pair in (a | b, a | c, b | c):
                    covers[pair] = covers.get(pair, 0) | bit
            geometry = self._geometry[key] = (triples, covers, locations)
            self._add("coverage_geometry_triples_built", len(triples))
            self._add("coverage_geometry_pair_masks_built", len(covers))
        else:
            self._add("coverage_geometry_cache_hits", 1)
        triples, covers, locations = geometry
        eligible = (1 << len(triples)) - 1
        eligible ^= 1 << locations[group]
        covered = 0
        for pair in self._certified_pairs:
            covered |= covers.get(pair, 0)
            self._add("pair_proof_coverage_unions", 1)
        covered &= eligible
        remaining = eligible & ~covered
        self._add("alternative_groups_eligible", len(triples) - 1)
        self._add("alternative_exact_checks_avoided", covered.bit_count())
        self._add("alternative_groups_selected_for_exact", remaining.bit_count())
        return self._groups_from_bits(triples, remaining)

    @staticmethod
    def _groups_from_bits(triples, remaining):
        while remaining:
            first = remaining & -remaining
            yield triples[first.bit_length() - 1]
            remaining ^= first

    def _compact_classes(self, outputs, group, stop_above=None):
        if stop_above != 2:
            return self._historical_exact_classes(outputs, group, stop_above=stop_above)
        self._add("stage_class_calls", 1)
        self._add("compact_alternative_exact_checks", 1)
        packed = self._packed_layouts.get(group)
        if packed is None:
            mask, offsets = self._layout(group)
            packed = self._packed_layouts[group] = (mask | (mask << self.stage_rows), tuple(offsets[1:]))
            self._add("compact_packed_layout_builds", 1)
        else:
            self._add("compact_packed_layout_hits", 1)
        if self._compact_joint is None:
            self._compact_joint = outputs[0] | (outputs[1] << self.stage_rows)
            self._add("compact_joint_table_packings", 1)
        joint = self._compact_joint
        mask, remaining = packed
        first, second = joint & mask, -1
        read = 1
        for shift in remaining:
            value = (joint >> shift) & mask
            read += 1
            if value == first or value == second:
                continue
            if second >= 0:
                self._add("compact_residual_columns_read", read)
                return 3
            second = value
        self._add("compact_residual_columns_read", read)
        return 1 if second < 0 else 2

    def _raw_targets(self, selected):
        cpu = process_time_ns() if self._profile else None
        try:
            raw, stage = super()._raw_targets(selected)
        finally:
            if cpu is not None:
                self._add("current_target_replay_cpu_ns", process_time_ns() - cpu)
        self._current_raw_targets = raw
        self._current_stage_targets = stage
        self._add("pair_proofs_supplied", len(self._pending_proofs)
                  if isinstance(self._pending_proofs, (list, tuple)) else 0)
        return raw, stage

    def _replay_raw_return(self, gates):
        cpu = process_time_ns() if self._profile else None
        try:
            return super()._replay_raw_return(gates)
        finally:
            if cpu is not None:
                self._add("returned_raw_replay_cpu_ns", process_time_ns() - cpu)

    def _return_shape(self, answer, cache_key):
        cpu = process_time_ns() if self._profile else None
        try:
            return super()._return_shape(answer, cache_key)
        finally:
            if cpu is not None:
                self._add("physical_link_check_cpu_ns", process_time_ns() - cpu)

    def _prepare_proofs(self):
        if self._proofs_ready:
            return
        self._proofs_ready = True
        cpu = process_time_ns()
        seen = set()
        try:
            if not isinstance(self._pending_proofs, (tuple, list)):
                self._add("pair_proof_schema_failures", 1)
                return
            raw0, raw1 = self._current_raw_targets
            for supplied in self._pending_proofs:
                # Failed or malformed advice cannot license a skip.  The
                # normal residual test remains authoritative for that group.
                if (not isinstance(supplied, (tuple, list)) or len(supplied) not in (3, 4)
                        or any(type(value) is not int for value in supplied)):
                    self._add("pair_proof_schema_failures", 1)
                    continue
                a, b, outside = supplied[:3]
                corners = supplied[3] if len(supplied) == 4 else 15
                if not (0 <= a < b < self.m and 0 <= outside < self.stage_rows
                        and corners in (7, 11, 13, 14, 15)):
                    self._add("pair_proof_schema_failures", 1)
                    continue
                pair = (1 << a) | (1 << b)
                if outside & pair:
                    self._add("pair_proof_schema_failures", 1)
                    continue
                key = (a, b, outside, corners)
                if key in seen:
                    self._add("pair_proof_duplicate_certificates", 1)
                    continue
                seen.add(key)
                self._add("pair_proof_unique_certificates_checked", 1)
                observed = 0
                for corner in range(4):
                    if not corners & (1 << corner):
                        continue
                    stage_row = outside | (((corner & 1) << a)) | (((corner >> 1) << b))
                    self._add("pair_proof_row_requests", 1)
                    value = self._proof_row_values.get(stage_row)
                    if value is None:
                        cell = self._frontier_cells[stage_row]
                        # The superclass checked the full raw/stage
                        # projection.  Read a current raw row backing this
                        # corner rather than supplied old response labels.
                        raw_row = (cell & -cell).bit_length() - 1
                        value = ((raw0 >> raw_row) & 1) | (((raw1 >> raw_row) & 1) << 1)
                        self._proof_row_values[stage_row] = value
                        self._add("pair_proof_raw_rows_read", 1)
                        self._add("pair_proof_output_bits_read", 2)
                    else:
                        self._add("pair_proof_row_cache_hits", 1)
                    observed |= 1 << value
                rows = corners.bit_count()
                self._add("pair_proof_certificate_row_requests", rows)
                if observed.bit_count() >= 3:
                    self._certified_pairs.add(pair)
                    self._add("pair_proof_successes", 1)
                else:
                    self._add("pair_proof_current_data_failures", 1)
        finally:
            self._add("pair_proof_verification_cpu_ns", process_time_ns() - cpu)

    def _classes_with_proofs(self, outputs, group, stop_above=None):
        if stop_above is None:
            self._add("chosen_group_exact_checks", 1)
            return self._exact_classes(outputs, group)
        cpu = process_time_ns() if self._profile_alternative_calls else None
        try:
            exact_cpu = process_time_ns() if self._profile_alternative_calls else None
            try:
                self._add("alternative_exact_checks_actual", 1)
                return self._exact_classes(outputs, group, stop_above=stop_above)
            finally:
                if exact_cpu is not None:
                    self._add("alternative_exact_cpu_ns", process_time_ns() - exact_cpu)
        finally:
            if cpu is not None:
                self._add("alternative_callback_cpu_ns", process_time_ns() - cpu)

    def verify(self, edit, answer):
        wall, cpu = perf_counter_ns(), process_time_ns()
        self._pending_proofs = answer.get("pair_proofs", ()) if isinstance(answer, dict) else ()
        self._proofs_ready = False
        self._certified_pairs = set()
        self._proof_row_values = {}
        self._compact_joint = None
        self._current_raw_targets = None
        self._current_stage_targets = None
        fast = isinstance(self._pending_proofs, (tuple, list)) and not self._pending_proofs
        self._joint._classes = self._exact_classes if fast else self._classes_with_proofs
        result = None
        try:
            result = super().verify(edit, answer)
            return result
        finally:
            work = result if result is not None else dict(self.last_work)
            elapsed_cpu, elapsed_wall = process_time_ns() - cpu, perf_counter_ns() - wall
            self._work["verification_cpu_ns"] += elapsed_cpu - work.get("verification_cpu_ns", 0)
            self._work["verification_wall_ns"] += elapsed_wall - work.get("verification_wall_ns", 0)
            work["verification_cpu_ns"] = elapsed_cpu
            work["verification_wall_ns"] = elapsed_wall
            minimum = work.get("minimum_phase_cpu_ns", 0)
            if fast:
                chosen = int(bool(work.get("stage_class_calls", 0)))
                actual = max(0, work.get("stage_class_calls", 0) - chosen)
                work["chosen_group_exact_checks"] = chosen
                work["alternative_exact_checks_actual"] = actual
                work["alternative_groups_considered"] = actual
                work["alternative_exact_checks_avoided"] = 0
                for name in ("chosen_group_exact_checks", "alternative_exact_checks_actual"):
                    self._work[name] = self._work.get(name, 0) + work[name]
            work["pair_no_proof_fast_path"] = fast
            work["alternative_groups_considered"] = (work.get("alternative_exact_checks_actual", 0)
                                                       + work.get("alternative_exact_checks_avoided", 0))
            work["global_minimum_alternative_groups_certified"] = work["alternative_groups_considered"]
            for name in ("alternative_groups_considered", "global_minimum_alternative_groups_certified"):
                self._work[name] = self._work.get(name, 0) + work[name]
            work["phase_profile_enabled"] = self._profile
            work["exact_fallback"] = self.exact_fallback
            # Removing this whole measured minimum block is an optimistic
            # counterfactual floor, not an executable or certified method.
            work["verification_remainder_cpu_ns"] = elapsed_cpu - minimum
            if self._profile:
                work["optimistic_no_minimum_cpu_floor_ns"] = elapsed_cpu - minimum
                work["optimistic_no_minimum_is_certified"] = False
                work["optimistic_no_alternative_cpu_floor_ns"] = elapsed_cpu - work.get("alternative_checks_cpu_ns", 0)
                work["optimistic_no_alternative_is_certified"] = False
            physical = sum(work.get(name, 0) for name in (
                "stage_program_and_cut_cpu_ns", "current_target_replay_cpu_ns",
                "returned_raw_replay_cpu_ns", "physical_link_check_cpu_ns"))
            work["physical_and_target_blocks_cpu_ns"] = physical
            work["verification_unattributed_cpu_ns"] = elapsed_cpu - minimum - physical
            work["pair_proof_certified_axis_pairs"] = len(self._certified_pairs)
            work["pair_proof_distinct_rows"] = len(self._proof_row_values)
            work["pair_parent_checker_sha256"] = PARENT_SHA256
            self._work["verification_remainder_cpu_ns"] = self._work.get("verification_remainder_cpu_ns", 0) + elapsed_cpu - minimum
            self.last_work = dict(work)
            # No current witness, proof label, or successful pair survives to
            # the sibling edit.  The frozen superclass alone owns history.
            self._pending_proofs = ()
            self._current_raw_targets = None
            self._current_stage_targets = None
            self._certified_pairs = set()
            self._proof_row_values = {}
            self._proofs_ready = False
            self._compact_joint = None

    def verify_history(self, history):
        """Independently price old witnesses on this parent's original pair.

        This establishes original scope only.  Edited verification never
        consults this verdict and rereads its own current raw responses.
        """
        wall, cpu = perf_counter_ns(), process_time_ns()
        work = {"history_verification_calls": 1}
        self._active = work
        self._proofs_ready = False
        self._certified_pairs = set()
        self._proof_row_values = {}
        self._current_raw_targets = self._original_raw_targets
        self._current_stage_targets = self._original_stage_targets
        try:
            if (not isinstance(history, dict) or type(history.get("schema")) is not int
                    or history["schema"] != 1 or type(history.get("m")) is not int
                    or history["m"] != self.m or history.get("strategy") not in ("packed", "scalar")):
                raise ValueError("invalid original witness history schema or scope")
            tables = history.get("tables")
            if (not isinstance(tables, (list, tuple)) or len(tables) != 2
                    or any(type(table) is not int for table in tables)
                    or tuple(tables) != self._original_stage_targets):
                raise ValueError("history output pair does not match this original parent")
            faces, proofs = history.get("faces"), history.get("proofs")
            if not isinstance(faces, (list, tuple)) or not isinstance(proofs, (list, tuple)):
                raise ValueError("invalid original witness collection")
            pairs = tuple(combinations(range(self.m), 2))
            if len(faces) != len(pairs):
                raise ValueError("history does not index every stage pair")
            expected = []
            for (a, b), face in zip(pairs, faces):
                if face is None:
                    continue
                if not isinstance(face, (list, tuple)) or len(face) != 2 or any(type(v) is not int for v in face):
                    raise ValueError("invalid indexed historical witness")
                expected.append((a, b, *face))
            if (any(not isinstance(proof, (list, tuple)) or len(proof) != 4
                    or any(type(value) is not int for value in proof) for proof in proofs)
                    or len(proofs) != len(expected)
                    or set(map(tuple, proofs)) != set(expected)):
                raise ValueError("indexed faces disagree with historical proofs")
            self._pending_proofs = proofs
            self._add("pair_proofs_supplied", len(proofs))
            self._prepare_proofs()
            if work.get("pair_proof_schema_failures", 0) or work.get("pair_proof_current_data_failures", 0):
                raise ValueError("historical witness fails on the actual original output pair")
            work.update(exact_history=True, history_scope="this parent original output pair",
                        source_sha256=self.source_sha256,
                        pair_proof_certified_axis_pairs=len(self._certified_pairs),
                        pair_proof_distinct_rows=len(self._proof_row_values),
                        global_minimum_queries=0)
            return work
        finally:
            work["history_verification_cpu_ns"] = process_time_ns() - cpu
            work["history_verification_wall_ns"] = perf_counter_ns() - wall
            self.last_history_work = dict(work)
            for name, value in work.items():
                if type(value) is int:
                    self._work[name] = self._work.get(name, 0) + value
            self._pending_proofs = ()
            self._current_raw_targets = None
            self._current_stage_targets = None
            self._certified_pairs = set()
            self._proof_row_values = {}
            self._proofs_ready = False
            self._active = self._work
