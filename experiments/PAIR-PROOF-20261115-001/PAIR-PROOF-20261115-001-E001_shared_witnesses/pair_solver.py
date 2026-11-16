"""Paid two-signal exclusions with the ordinary exact selector and compiler.

``prepare_history(parent)`` mines one original witness per signal pair.
``solve(state, mode, history=None, advice=None)`` returns a stage answer and
local work counters; raw lifting and independent verification belong to the
common harness.  Each edited State has its own observations and proof cache.

A proof is [i,j,base,corner_mask], with i<j and both bits clear in base.
Corners are base, base|2**i, base|2**j, base|2**i|2**j.  Three distinct
CURRENT joint output values exclude a one-bit summary for every triple
containing i,j.  They never establish feasibility, exclude two bits, or
replace checking the selected group.  Only a fully checked two-bit incumbent
enables these exclusions.  An unresolved alternative is checked exactly.

The compact ordinary path and proof paths call the very same packed
two-residual test.  No per-residual instrumentation taxes only one arm.
``minimum_selection_cpu_ns`` is one enclosing timer from contextual candidate
selection through the complete minimum proof; physical construction follows.

Main work fields (absent Counter entries mean zero):
* query_row_requests/unique_rows/reused_rows count explicit logical two-output
  observations; query_output_bit_reads counts two bits per unique row.
* packed_pair_queries counts executed vectorized searches; outside_settings
  and corner_equivalents describe their parallel extent, not scalar queries.
* proof_avoided_exact_groups counts alternatives actually excluded in bulk or
  at the historical fallback; proof_unresolved_exact_fallbacks counts executed
  uncovered exact attempts.  proof_uncovered_exact_groups is the initial
  pending set size, which can exceed actual attempts when one bit wins early.
* compact_exact_alternatives/exclusions/passes distinguish executed <=2 tests,
  early >2 rejections and full residual completions.  wider_exact_alternatives
  and the inherited group_* counters cover every remaining exact path.
* proof_shape_* covers geometry construction/cache use.  All stored shapes
  are output-independent; current rows and certificates never cross States.

Default audit=False avoids per-test diagnostic allocations.  audit=True adds
pair_audit to the answer for synthetic replay, with identical decisions.
"""

from collections import Counter
from functools import cache
from itertools import combinations
import hashlib
import importlib.util
from pathlib import Path
import sys
from time import perf_counter_ns, process_time_ns


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = "experiments/PARENT-FOLD-20261115-001/PARENT-FOLD-20261115-001-E001_consumer_edits/"
SOURCE_DEPENDENCIES = (
    PREVIOUS + "parent_engine.py", PREVIOUS + "controls.py",
    "experiments/FOLD-TWO-OUTPUT-20261115-001/FOLD-TWO-OUTPUT-20261115-001-E001_joint_tables/joint_solver.py",
    str((HERE / "compact_control.py").relative_to(ROOT)),
    str((HERE / "packed_faces.py").relative_to(ROOT)),
)
SOURCE_SHA256 = {
    SOURCE_DEPENDENCIES[0]: "afb5fa26473dcebf898b1c4f94989c2aba7429a652f9b6fafbf9b638f0be1e18",
    SOURCE_DEPENDENCIES[1]: "9e4c13d73bd38c29d20bfc177666a73d89433d61d007e75c1f846035e8b93cfe",
}


def _module(name, path, expected=None):
    if expected and hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise RuntimeError("immutable predecessor changed: " + name)
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    module = sys.modules[name]
    if Path(module.__file__).resolve() != path.resolve():
        raise ImportError("module name points to another source: " + name)
    return module


_engine = _module("parent_engine", ROOT / SOURCE_DEPENDENCIES[0], SOURCE_SHA256[SOURCE_DEPENDENCIES[0]])
_ordinary = _module("controls", ROOT / SOURCE_DEPENDENCIES[1], SOURCE_SHA256[SOURCE_DEPENDENCIES[1]])
_compact = _module("compact_control", HERE / "compact_control.py")
_packed = _module("packed_faces", HERE / "packed_faces.py")

_MODES = {
    "no-proof": (None, None, False),
    "old-three": ("three", None, False),
    "same-four": ("four", None, False),
    "fresh": (None, "fixed", False),
    "new": (None, "fixed", False),
    "packed": (None, "packed", False),
    "balanced": (None, "balanced", False),
    "old-fresh": ("four", "fixed", False),
    "old-packed": ("four", "packed", False),
    "old3-packed": ("three", "packed", False),
    "advice": (None, None, True),
    "old-advice": ("four", None, True),
}
MODES = tuple(_MODES)


def _pair_index(m, i, j):
    return i * (2 * m - i - 1) // 2 + j - i - 1


@cache
def _stars(m, axes):
    """Public geometry only; no output values, historical labels or solutions."""
    layouts = _compact._layouts(m, axes)
    stars = [0] * (m * (m - 1) // 2)
    indices = {}
    for k, (triple, _, _) in enumerate(layouts):
        indices[triple] = k
        for i, j in combinations(triple, 2):
            stars[_pair_index(m, i, j)] |= 1 << k
    pairs = tuple(combinations(axes, 2))
    classes = {axis: k & 1 for k, axis in enumerate(axes)}
    balanced = tuple((i, j) for i, j in pairs if classes[i] == classes[j])
    return tuple(stars), indices, pairs, balanced


def _action(action, m):
    if not isinstance(action, (tuple, list)) or len(action) not in (3, 4):
        raise ValueError("a proof request needs i,j,base and optional corner mask")
    i, j, base = action[:3]
    mask = action[3] if len(action) == 4 else 15
    if (any(type(v) is not int for v in (i, j, base, mask))
            or not 0 <= i < j < m or not 0 <= base < 1 << m
            or base & ((1 << i) | (1 << j)) or mask not in (7, 11, 13, 14, 15)):
        raise ValueError("invalid pair witness request")
    return i, j, base, mask


class _Rows:
    def __init__(self, tables, work):
        self.first, self.second = tables
        self.values, self.work = {}, work

    def read(self, row):
        work = self.work
        work["query_row_requests"] += 1
        value = self.values.get(row, -1)
        if value < 0:
            value = ((self.first >> row) & 1) | (((self.second >> row) & 1) << 1)
            self.values[row] = value
            work["query_unique_rows"] += 1
            work["query_output_bit_reads"] += 2
        else:
            work["query_reused_rows"] += 1
        return value

    def test(self, i, j, base, mask):
        """Read every requested corner; return the first three distinct ones."""
        self.work["face_tests"] += 1
        seen, selected = 0, 0
        for corner, row in enumerate((base, base | (1 << i), base | (1 << j),
                                      base | (1 << i) | (1 << j))):
            if mask & (1 << corner):
                value = self.read(row)
                if not seen & (1 << value):
                    seen |= 1 << value
                    if selected.bit_count() < 3:
                        selected |= 1 << corner
        accepted = selected if selected.bit_count() == 3 else 0
        self.work["face_successes" if accepted else "face_failures"] += 1
        return accepted


def _packed_context(tables, m, work):
    work["packed_contexts_built"] += 1
    work["packed_table_vectors_read"] += 2
    work["packed_zero_masks_built"] += m
    return _packed.PackedFaces(tables, m)


def _first(context, m, i, j, work):
    work["packed_pair_queries"] += 1
    work["packed_outside_settings"] += 1 << (m - 2)
    work["packed_corner_equivalents"] += 1 << m
    result = context.first(i, j)
    work["packed_pair_hits" if result is not None else "packed_pair_misses"] += 1
    return result


def prepare_history(parent, strategy="packed"):
    """Acquire original witnesses, including failures, without a global solve.

    ``faces`` aligns with lexicographic combinations(range(m),2).  Each item
    is None or [base,three_corner_mask]; ``proofs`` contains the same successes
    as explicit [i,j,base,mask] records.  ``tables`` binds the public original
    source only.  Edited States never inherit row observations or truth values.
    Scalar acquisition enumerates all legal bases ascending, stopping at the
    first successful base; packed acquisition finds exactly that same base.
    """
    cpu, wall = process_time_ns(), perf_counter_ns()
    if strategy not in ("packed", "scalar"):
        raise ValueError("history strategy must be packed or scalar")
    work = Counter()
    m, tables = parent.m, parent.original_tables
    rows = _Rows(tables, work)
    context = _packed_context(tables, m, work) if strategy == "packed" else None
    faces, proofs = [], []
    for i, j in combinations(range(m), 2):
        work["old_acquisition_pairs"] += 1
        if context is not None:
            base = _first(context, m, i, j, work)
            mask = rows.test(i, j, base, 15) if base is not None else 0
            if base is not None and not mask:
                raise RuntimeError("packed discovery did not yield a valid witness")
        else:
            base, mask = None, 0
            axes = (1 << i) | (1 << j)
            for candidate in range(1 << m):
                work["scalar_base_enumerations"] += 1
                if candidate & axes:
                    continue
                work["scalar_face_queries"] += 1
                found = rows.test(i, j, candidate, 15)
                if found:
                    base, mask = candidate, found
                    break
        if mask:
            faces.append([base, mask])
            proofs.append([i, j, base, mask])
            work["old_acquisition_hits"] += 1
        else:
            faces.append(None)
            work["old_acquisition_misses"] += 1
    history = dict(schema=1, m=m, strategy=strategy, tables=list(tables), faces=faces, proofs=proofs)
    work["old_acquisition_saved_proofs"] = len(proofs)
    work["old_acquisition_face_entries"] = len(faces)
    work["acquisition_cpu_ns"] = process_time_ns() - cpu
    work["acquisition_wall_ns"] = perf_counter_ns() - wall
    return history, dict(work)


class _Proofs:
    """Edit-local observation/cache; all successful uses have current evidence."""
    def __init__(self, state, work, mode, history, advice, shared, audit=False):
        self.state, self.work, self.m = state, work, state.m
        self.old, self.new, self.use_advice = _MODES[mode]
        self.history, self.advice = history, advice
        self.rows = _Rows(state.tables, work)
        self.certified = self.old_tried = self.new_tried = 0
        self.certificates, self.used, self.tested = {}, set(), {}
        self.context, self.advice_done = None, False
        self.audit = audit
        self.tests, self.queries, self.skipped = ([], [], []) if audit else (None, None, None)
        self.pending, self.stars = None, None
        self.classes = {axis: k & 1 for k, axis in enumerate(shared)}
        if self.old:
            if (not isinstance(history, dict) or history.get("schema") != 1
                    or history.get("m") != self.m
                    or tuple(history.get("tables", ())) != state.parent.original_tables
                    or len(history.get("faces", ())) != self.m * (self.m - 1) // 2):
                raise ValueError("history does not bind this public original parent")
            work["old_history_bindings"] += 1
        if self.use_advice and advice is not None and not isinstance(advice, (tuple, list)):
            raise ValueError("advice must be a list of legal observation requests")

    def _test(self, action, source):
        i, j, base, mask = _action(action, self.m)
        index = _pair_index(self.m, i, j)
        if self.pending is not None and not self.pending & self.stars[index]:
            self.work["proof_actions_omitted_no_uncovered_groups"] += 1
            return False
        if self.certified & (1 << index):
            self.work["proof_requests_omitted_already_certified"] += 1
            return True
        key = (i, j, base, mask)
        if key in self.tested:
            self.work["proof_test_cache_hits"] += 1
            return bool(self.tested[key])
        self.work[source + "_tests"] += 1
        accepted = self.rows.test(i, j, base, mask)
        self.tested[key] = accepted
        if self.audit:
            self.tests.append([source, i, j, base, mask, accepted])
        self.work[source + ("_successes" if accepted else "_failures")] += 1
        if accepted:
            self.certified |= 1 << index
            self.certificates[index] = [i, j, base, accepted]
            self.work["proofs_discovered"] += 1
            if self.pending is not None:
                covered = self.pending & self.stars[index]
                self.work["proof_coverage_union_updates"] += 1
                self.work["proof_avoided_exact_groups"] += covered.bit_count()
                self.pending &= ~self.stars[index]
                if covered:
                    self.used.add(index)
        return bool(accepted)

    def _old_pair(self, i, j):
        index = _pair_index(self.m, i, j)
        self.work["old_lookup_requests"] += 1
        if self.old_tried & (1 << index):
            self.work["old_lookup_cache_hits"] += 1
            return False
        self.old_tried |= 1 << index
        face = self.history["faces"][index]
        if face is None:
            self.work["old_lookup_misses"] += 1
            return False
        self.work["old_lookup_hits"] += 1
        base, mask = face
        return self._test([i, j, base, mask if self.old == "three" else 15],
                          "old_three" if self.old == "three" else "old_four")

    def _new_pair(self, i, j):
        index = _pair_index(self.m, i, j)
        if self.new_tried & (1 << index):
            self.work["new_pair_cache_hits"] += 1
            return False
        self.new_tried |= 1 << index
        if self.new == "fixed":
            for base in dict.fromkeys((0, ((1 << self.m) - 1) ^ ((1 << i) | (1 << j)))):
                if self._test([i, j, base], "fresh_fixed"):
                    return True
            return False
        if self.context is None:
            self.context = _packed_context(self.state.tables, self.m, self.work)
        base = _first(self.context, self.m, i, j, self.work)
        if self.audit:
            self.queries.append([i, j, -1 if base is None else base])
        if base is None:
            return False
        if not self._test([i, j, base], "fresh_packed"):
            raise RuntimeError("packed discovery did not yield a valid current witness")
        return True

    def _covered(self, triple):
        self.work["proof_coverage_lookups"] += 1
        a, b, c = triple
        mask = ((1 << _pair_index(self.m, a, b)) | (1 << _pair_index(self.m, a, c))
                | (1 << _pair_index(self.m, b, c))) & self.certified
        if not mask:
            return False
        index = (mask & -mask).bit_length() - 1
        self.used.add(index)
        return True

    def excludes(self, triple):
        if self._covered(triple):
            return True
        pairs = tuple(combinations(triple, 2))
        if self.old:
            for i, j in pairs:
                if self._old_pair(i, j):
                    return self._covered(triple)
        if self.use_advice and not self.advice_done:
            self.advice_done = True
            for request in self.advice or ():
                self.work["advice_requests"] += 1
                self._test(request, "advice")
            if self._covered(triple):
                return True
        if self.new:
            for i, j in pairs:
                if self.new == "balanced" and self.classes[i] != self.classes[j]:
                    self.work["balanced_cross_class_pairs_omitted"] += 1
                    continue
                if self._new_pair(i, j):
                    return self._covered(triple)
        return False

    def bulk(self, shared, incumbent):
        """Execute useful fixed/advised actions, then return uncovered groups.

        Pair-to-group incidence is shape-cached.  Each accepted proof unions
        its group mask once; the exact fallback visits only surviving bits.
        Old witnesses precede new/advised actions.  Pair order is ascending;
        balanced uses the two alternating classes of ascending eligible axes.
        No actions are executed after every alternative is covered.
        """
        work = self.work
        before = _stars.cache_info().hits
        stars, indices, pairs, balanced = _stars(self.m, shared)
        hit = _stars.cache_info().hits != before
        work["proof_shape_cache_hits" if hit else "proof_shape_builds"] += 1
        if not hit:
            work["proof_shape_group_entries_built"] += len(indices)
            work["proof_shape_pair_masks_built"] += len(stars)
            work["proof_shape_incidence_memberships"] += 3 * len(indices)
        self.stars = stars
        self.pending = ((1 << len(indices)) - 1) ^ (1 << indices[incumbent])
        work["proof_initial_alternatives"] += self.pending.bit_count()
        if self.old:
            for i, j in pairs:
                if not self.pending:
                    break
                work["proof_action_coverage_tests"] += 1
                if self.pending & stars[_pair_index(self.m, i, j)]:
                    self._old_pair(i, j)
                else:
                    work["proof_actions_omitted_no_uncovered_groups"] += 1
        if self.use_advice:
            self.advice_done = True
            for request in self.advice or ():
                if not self.pending:
                    break
                work["advice_requests"] += 1
                self._test(request, "advice")
        if self.new:
            proposals = balanced if self.new == "balanced" else pairs
            for i, j in proposals:
                if not self.pending:
                    break
                work["proof_action_coverage_tests"] += 1
                if self.pending & stars[_pair_index(self.m, i, j)]:
                    self._new_pair(i, j)
                else:
                    work["proof_actions_omitted_no_uncovered_groups"] += 1
        work["proof_uncovered_exact_groups"] += self.pending.bit_count()
        if self.audit:
            covered = (((1 << len(indices)) - 1) ^ (1 << indices[incumbent])) & ~self.pending
            self.skipped.extend(sum(1 << j for j in triple)
                                for triple, k in indices.items() if covered & (1 << k))
        return self.pending

    def decorate(self, selected, mode):
        width = selected["width"]
        proofs = [self.certificates[i] for i in sorted(self.used)] if width == 2 else []
        self.work["proofs_returned"] = len(proofs)
        self.work["proofs_unused_or_discarded"] = len(self.certificates) - len(proofs)
        self.work["proof_row_cache_entries"] = len(self.rows.values)
        result = {**selected, "pair_proofs": proofs}
        if self.audit:
            result["pair_audit"] = dict(mode=mode, tests=self.tests, packed_queries=self.queries,
                                        skipped_groups=self.skipped)
        return result


def _cutoff(state, work, joint, triple, mask, remaining):
    work["compact_exact_alternatives"] += 1
    if _compact.third_residual(joint, mask, remaining):
        work["compact_exact_exclusions"] += 1
        state._lower_bounds[triple] = max(state._lower_bounds.get(triple, 0), 3)
        return None
    work["compact_exact_passes"] += 1
    return _engine._partition(state, work, triple)


def _minimum(state, work, mode, history, advice, hint, audit):
    """One complete measured minimum-selection block; no physical synthesis."""
    if mode not in _MODES:
        raise ValueError("unknown pair-proof mode: " + str(mode))
    preferred = hint if hint is not None else _ordinary._location(state, work)
    incumbent = _engine._partition(state, work, preferred) if preferred is not None else None
    if incumbent is not None and not incumbent["eligible"]:
        incumbent = None
    if incumbent is not None and incumbent["width"] == 1:
        state._global_width = 1
        return {**incumbent, "pair_proofs": []}
    shared = _engine._shared(state, work)
    if len(shared) < 3:
        raise ValueError("no jointly essential triple")
    pool = None
    joint = state.tables[0] | (state.tables[1] << (1 << state.m))

    def excluded(triple):
        nonlocal pool
        if mode == "no-proof":
            return False
        if pool is None:
            pool = _Proofs(state, work, mode, history, advice, shared, audit)
        if pool.excludes(triple):
            work["proof_avoided_exact_groups"] += 1
            if audit:
                pool.skipped.append(sum(1 << j for j in triple))
            state._lower_bounds[triple] = max(state._lower_bounds.get(triple, 0), 3)
            return True
        work["proof_unresolved_exact_fallbacks"] += 1
        return False

    # Same location-seeded lexicographic compact branch as compact_control.
    if incumbent is not None and incumbent["width"] == 2:
        selected = incumbent
        work["compact_layout_requests"] += 1
        before = _compact._layouts.cache_info().hits
        layouts = _compact._layouts(state.m, shared)
        hit = _compact._layouts.cache_info().hits != before
        work["compact_layout_cache_hits" if hit else "compact_layout_builds"] += 1
        if mode == "no-proof":
            pending = None
            candidates = layouts
        else:
            pool = _Proofs(state, work, mode, history, advice, shared, audit)
            pending = pool.bulk(shared, preferred)
            candidates = None
        # Only surviving group bits are visited in the bulk proof path.
        if candidates is None:
            def surviving():
                bits = pending
                while bits:
                    bit = bits & -bits
                    bits ^= bit
                    yield layouts[bit.bit_length() - 1]
            candidates = surviving()
        for triple, mask, remaining in candidates:
            if triple == preferred:
                continue
            work["minimum_alternatives_visited"] += 1
            if mode != "no-proof":
                work["proof_unresolved_exact_fallbacks"] += 1
            info = _cutoff(state, work, joint, triple, mask, remaining)
            if info is not None:
                selected = info
                break
    else:
        # Preserve historical priorities and exact wider-bound behavior when
        # a contextual two-bit seed was not available.  A later two-bit
        # incumbent enables the identical cutoff and proof rule.
        best, bound = incumbent, 8 if incumbent is None else 1 << (incumbent["width"] - 1)
        priorities = _engine._priorities(state, work, preferred)
        seen, layout_map = set(), None
        for triple in (*priorities, *combinations(shared, 3)):
            if triple in seen:
                continue
            seen.add(triple)
            if best is not None and triple == best["triple"]:
                continue
            work["minimum_alternatives_visited"] += 1
            if bound == 2:
                if excluded(triple):
                    continue
                if layout_map is None:
                    work["compact_layout_requests"] += 1
                    layout_map = {row[0]: row[1:] for row in _compact._layouts(state.m, shared)}
                    work["compact_layout_index_entries"] += len(layout_map)
                mask, remaining = layout_map[triple]
                info = _cutoff(state, work, joint, triple, mask, remaining)
            else:
                work["wider_exact_alternatives"] += 1
                info = _engine._partition(state, work, triple, bound)
            if info is None:
                continue
            best = info
            work["global_incumbent_updates"] += 1
            if info["width"] == 1:
                break
            bound = 1 << (info["width"] - 1)
        selected = best
    if selected is None:
        raise ValueError("no jointly essential triple")
    state._global_width = selected["width"]
    return (pool.decorate(selected, mode) if pool is not None
            else {**selected, "pair_proofs": []})


def _timed_minimum(state, work, mode, history, advice, hint, audit=False):
    cpu = process_time_ns()
    try:
        return _minimum(state, work, mode, history, advice, hint, audit)
    finally:
        work["minimum_selection_cpu_ns"] += process_time_ns() - cpu


def finish_selected(state, work, selected):
    """Uninstrumented ordinary physical core, usable by matched selectors.

    ``work`` is the caller's Counter.  This is the unchanged post-selection
    logic of frozen controls._exact_first: try generic existing source pairs,
    then use the same cut-scoped primitive compiler and caches.
    """
    if selected is None:
        raise ValueError("no jointly essential triple")
    group, width = selected["triple"], selected["width"]
    bits = sources = None
    if width == 2:
        classes = selected["classes"]
        need = sum(1 << i for i, (a, b) in enumerate(_ordinary.PAIRS) if classes[a] != classes[b])
        candidates = {}
        for entry in _engine._local_sources(state, work, group):
            mask = _ordinary._separates(entry["truth"]) & need
            if mask:
                candidates.setdefault(mask, entry)
        for (left, a), (right, b) in combinations(candidates.items(), 2):
            work["generic_source_pair_tests"] += 1
            if left | right == need:
                bits, sources = (a["truth"], b["truth"]), (a["wire"], b["wire"])
                work["generic_source_pair_found"] += 1
                break
    return _engine._finish(state, work, group, bits=bits, source_wires=sources)


def _complete(state, work, mode, history, advice, hint, audit):
    selected = _timed_minimum(state, work, mode, history, advice, hint, audit)
    answer = finish_selected(state, work, selected)
    answer["pair_proofs"] = selected["pair_proofs"]
    if "pair_audit" in selected:
        answer["pair_audit"] = selected["pair_audit"]
    return answer


def solve(state, mode="no-proof", history=None, advice=None, hint=None, audit=False):
    """Return (stage_answer,work); advice is only a legal action sequence."""
    return _engine._measure(state, _complete, mode, history, advice, hint, audit)


def select_only(state, mode="no-proof", history=None, advice=None, hint=None, audit=False):
    """Return (full selected partition,work), without compiling any program."""
    return _engine._measure(state, _timed_minimum, mode, history, advice, hint, audit)
