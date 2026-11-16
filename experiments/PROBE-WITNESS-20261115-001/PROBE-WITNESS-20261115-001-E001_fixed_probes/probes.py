"""Fixed-context conclusive screens around one shared exact primitive backend.

ProbeSolver(n,enabled=True,scheme=0).solve((truth0,truth1),advice=None).
No data, models, task IDs or target formulas are imported. Disabled and all
four fixed schemes share lexical candidate order, exact checks, minimum-width
bounds and the frozen JointSolver primitive physical builder. A >1bit witness
is used only at bound2. Bounds8/4 still need a feasible wider incumbent and
therefore use exact checking directly. Unresolved screens also use exact.

Each task has its own GLOBAL raw-assignment observation cache, containing the
two-bit ordered output pair. Requests, unique reads and reuse are distinct.
Schedule: first context locals0,1,2; second context locals0,1,2; then locals3..7
with first-context read/check before second-context read/check. Stop as soon
as either single set or the paired set has3 distinct signatures. A second
context's single witness is preferred over its simultaneous paired witness.
At most16 requested rows per screened group; a certificate uses3 or6 rows.

witnesses records are [group_mask,local_a,local_b,local_c,settings_mask,scheme].
Local bits refer to ascending raw group indices. Settings1/2/3 select first,
second or both fixed contexts. Scheme0=(all0,all1); schemes1/2/3 use raw bits
(i//scheme)%2==0 and its complement. Group bits are cleared before inserting
each local assignment. No observed output values are included. A verifier
must independently read the original tables. Redundant earlier certificates
are discarded on reaching width1; discovery cost remains in the counters.

advice is an explicit CALIBRATION-ONLY dict group_mask -> -1(skip) or0..3.
It is never a callback and normal calls receive None. Its interface/proof
cache namespace is isolated so oracle calibration cannot seed primary proofs.
All source-specific exact interfaces/recipes remain public arm-local caches.
"""

from __future__ import annotations

import hashlib
import importlib.util
from itertools import combinations
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
    raise RuntimeError("sealed joint primitive dependency changed")
_alias = "_probe_witness_frozen_joint"
if _alias in sys.modules:
    _joint = sys.modules[_alias]
    if Path(_joint.__file__).resolve() != _path.resolve():
        raise ImportError("joint primitive alias points elsewhere")
else:
    _spec = importlib.util.spec_from_file_location(_alias, _path)
    _joint = importlib.util.module_from_spec(_spec)
    sys.modules[_alias] = _joint
    _spec.loader.exec_module(_joint)


PROBE_COUNTERS = (
    "probe_candidates", "probe_witness_hits", "probe_unresolved_fallback",
    "resolved_by_witness", "attempted_by_exact", "exact_bound_rejections",
    "probe_disabled_groups", "probe_skipped_for_wider_bound", "probe_skipped_by_advice",
    "probe_row_requests", "probe_row_unique", "probe_row_reuses", "probe_output_bit_reads",
    "probe_signature_tests", "witness_single_hits", "witness_double_hits",
    "witnesses_discarded_after_width1", "witness_records_returned", "witness_single_returned",
    "witness_double_returned", "witness_row_references", "witness_distinct_rows",
    "witness_single_distinct_rows", "witness_double_distinct_rows",
    "probe_advice_calls", "probe_interface_cache_hits", "witness_cache_records_reused",
)


def scheme_masks(n, scheme):
    """Public fixed GLOBAL masks; clear candidate group bits before use."""
    if type(scheme) is not int or not 0 <= scheme <= 3:
        raise ValueError("scheme must be0..3")
    full = (1 << n) - 1
    first = 0 if scheme == 0 else sum(1 << i for i in range(n) if (i // scheme) % 2 == 0)
    return first, first ^ full


class ProbeSolver(_joint.JointSolver):
    def __init__(self, n, enabled=True, scheme=0):
        wall, cpu = perf_counter(), process_time_ns()
        super().__init__(n, arm="primitive")
        if type(enabled) is not bool:
            raise ValueError("enabled must be Boolean")
        scheme_masks(n, scheme)
        self.enabled, self.scheme = enabled, scheme
        self.raw_full = (1 << n) - 1
        self._schemes = tuple(scheme_masks(n, s) for s in range(4))
        self._work.update(dict.fromkeys(PROBE_COUNTERS, 0))
        self._namespaces = {None: self._interfaces}
        self._proofs = {}
        self._active_namespace = None
        self._tables, self._advice = None, {}
        self._observations, self._witnesses = {}, []
        self.setup_cpu_ns = process_time_ns() - cpu
        self.setup_seconds = perf_counter() - wall
        self._setup_record = {"cpu_ns": self.setup_cpu_ns, "seconds": self.setup_seconds,
                              "work": self.work_counters()}

    def _observe(self, row):
        work = self._work
        work["probe_row_requests"] += 1
        value = self._observations.get(row)
        if value is None:
            value = ((self._tables[0] >> row) & 1) | (((self._tables[1] >> row) & 1) << 1)
            self._observations[row] = value
            work["probe_row_unique"] += 1
            work["probe_output_bit_reads"] += 2
        else:
            work["probe_row_reuses"] += 1
        return value

    def _screen(self, group, offsets, scheme):
        """No unsupported inference: three distinct signatures is the test."""
        group_mask = sum(1 << j for j in group)
        first, second = self._schemes[scheme]
        first &= self.raw_full ^ group_mask
        second &= self.raw_full ^ group_mask
        seen0, seen1, seen_both = [-1] * 4, [-1] * 4, [-1] * 16
        rows0, rows1, rows_both = [], [], []
        values0 = [None] * 8
        observe, work = self._observe, self._work

        def insert(seen, representatives, value, local, settings):
            work["probe_signature_tests"] += 1
            if seen[value] < 0:
                seen[value] = local
                representatives.append(local)
                if len(representatives) == 3:
                    work["probe_witness_hits"] += 1
                    work["witness_double_hits" if settings == 3 else "witness_single_hits"] += 1
                    return (group_mask, *representatives, settings, scheme)
            return None

        for local in range(3):
            value = values0[local] = observe(first | offsets[local])
            witness = insert(seen0, rows0, value, local, 1)
            if witness is not None:
                return witness
        for local in range(3):
            value = observe(second | offsets[local])
            witness = insert(seen1, rows1, value, local, 2)
            if witness is not None:
                return witness
            witness = insert(seen_both, rows_both, values0[local] | (value << 2), local, 3)
            if witness is not None:
                return witness
        for local in range(3, 8):
            a = observe(first | offsets[local])
            witness = insert(seen0, rows0, a, local, 1)
            if witness is not None:
                return witness  # Do not pay for this local's second read.
            b = observe(second | offsets[local])
            witness = insert(seen1, rows1, b, local, 2)
            if witness is not None:
                return witness
            witness = insert(seen_both, rows_both, a | (b << 2), local, 3)
            if witness is not None:
                return witness
        return None

    def _exact_group(self, joint, layout, bound):
        """Same fast exact packed loop in enabled and disabled ablations."""
        mask, offsets, _ = layout
        lookup, unique, classes = {}, [], []
        seen = shifts = 0
        rejected = False
        for offset in offsets:
            value = (joint >> offset) & mask if offset else joint & mask
            seen += 1
            shifts += int(bool(offset))
            label = lookup.get(value)
            if label is None:
                label = len(unique)
                lookup[value] = label
                unique.append(value)
                if len(unique) > bound:
                    rejected = True
                    break
            classes.append(label)
        work = self._work
        work["residual_joint_rows"] += seen
        work["residual_packed_shifts"] += shifts
        work["residual_packed_masks"] += seen
        work["residual_row_equivalents"] += seen * (self.rows >> 2)
        work["joint_class_lookups"] += seen
        if rejected:
            work["group_bound_rejections"] += 1
            work["exact_bound_rejections"] += 1
            return None
        pairs = tuple((value & self.full, value >> self.rows) for value in unique)
        work["residual_pairs_unpacked"] += len(pairs)
        return len(pairs), tuple(classes), tuple(pairs[label] for label in classes), None

    def _group(self, joint, group, bound):
        layout = self._layout(group)
        work = self._work
        if not self.enabled:
            work["probe_disabled_groups"] += 1
        elif bound > 2:
            work["probe_skipped_for_wider_bound"] += 1
        else:
            group_mask = sum(1 << j for j in group)
            scheme = self._advice.get(group_mask, self.scheme)
            if scheme == -1:
                work["probe_skipped_by_advice"] += 1
            else:
                work["probe_candidates"] += 1
                witness = self._screen(group, layout[1], scheme)
                if witness is not None:
                    self._witnesses.append(witness)
                    work["resolved_by_witness"] += 1
                    work["group_bound_rejections"] += 1
                    return None
                work["probe_unresolved_fallback"] += 1
        work["attempted_by_exact"] += 1
        return self._exact_group(joint, layout, bound)

    def _interface(self, tables):
        key = (self._active_namespace, tables)
        if tables in self._interfaces:
            self._work["probe_interface_cache_hits"] += 1
            self._witnesses = list(self._proofs[key])
            self._work["witness_cache_records_reused"] += len(self._witnesses)
            return super()._interface(tables)
        result = super()._interface(tables)
        interface = result[1]
        if interface is not None and (interface[1] - 1).bit_length() == 1:
            self._work["witnesses_discarded_after_width1"] += len(self._witnesses)
            self._witnesses.clear()
        self._proofs[key] = tuple(self._witnesses)
        return result

    def _advice_map(self, advice):
        if advice is None:
            return None, {}
        if not isinstance(advice, dict):
            raise ValueError("calibration advice must be a group-mask dictionary")
        result = {}
        for mask, scheme in advice.items():
            if (type(mask) is not int or not 0 <= mask <= self.raw_full or mask.bit_count() != 3
                    or type(scheme) is not int or not -1 <= scheme <= 3):
                raise ValueError("invalid calibration group/scheme")
            result[mask] = scheme
        return tuple(sorted(result.items())), result

    def _certificate_rows(self, witness):
        mask, *tail = witness
        locals_, settings, scheme = tail[:3], tail[3], tail[4]
        group = tuple(i for i in range(self.n) if (mask >> i) & 1)
        for setting in range(2):
            if (settings >> setting) & 1:
                outside = self._schemes[scheme][setting] & (self.raw_full ^ mask)
                for local in locals_:
                    yield outside | sum(((local >> j) & 1) << raw for j, raw in enumerate(group))

    def solve(self, tables, advice=None):
        wall, cpu = perf_counter(), process_time_ns()
        if (not isinstance(tables, (tuple, list)) or len(tables) != 2
                or any(type(t) is not int or not 0 <= t <= self.full for t in tables)):
            raise ValueError("need two complete packed truth integers")
        tables = tuple(tables)
        namespace, mapping = self._advice_map(advice)
        before = self.work_counters()
        if advice is not None:
            self._work["probe_advice_calls"] += 1
        self._active_namespace = namespace
        self._advice, self._tables = mapping, tables
        self._interfaces = self._namespaces.setdefault(namespace, {})
        self._observations, self._witnesses = {}, []
        try:
            result = super().solve(tables)
            single, double = set(), set()
            for witness in self._witnesses:
                rows = list(self._certificate_rows(witness))
                self._work["witness_row_references"] += len(rows)
                if witness[4] == 3:
                    self._work["witness_double_returned"] += 1
                    double.update(rows)
                else:
                    self._work["witness_single_returned"] += 1
                    single.update(rows)
            self._work["witness_records_returned"] += len(self._witnesses)
            self._work["witness_distinct_rows"] += len(single | double)
            self._work["witness_single_distinct_rows"] += len(single)
            self._work["witness_double_distinct_rows"] += len(double)
            result["witnesses"] = [list(w) for w in self._witnesses]
            result["probe_enabled"] = self.enabled
            result["probe_scheme"] = self.scheme
            result["calibration_advice_used"] = advice is not None
            result["work"].update({key: self._work[key] - before[key] for key in PROBE_COUNTERS})
            result["witness_fields"] = ["group_mask", "local_a", "local_b", "local_c", "settings_mask", "scheme"]
            elapsed_cpu, elapsed = process_time_ns() - cpu, perf_counter() - wall
            extra_cpu = max(0, elapsed_cpu - result["timing"]["cpu_ns"])
            extra_wall = max(0.0, elapsed - result["timing"]["elapsed_seconds"])
            result["timing"].update(probe_wrapper_cpu_ns=extra_cpu, probe_wrapper_seconds=extra_wall,
                                    cpu_ns=elapsed_cpu, elapsed_seconds=elapsed)
            result["timing"]["search_cpu_ns"] += extra_cpu
            result["timing"]["search_seconds"] += extra_wall
            self._total_cpu_ns += extra_cpu
            self._total_seconds += extra_wall
            return result
        finally:
            self._tables, self._advice = None, {}
            self._observations = {}

    def ledger(self):
        result = super().ledger()
        result["cache_entries"].update(probe_namespaces=len(self._namespaces),
                                       probe_total_interfaces=sum(len(v) for v in self._namespaces.values()),
                                       probe_proof_records=sum(len(v) for v in self._proofs.values()))
        return result


def _check_witness(witness, tables, n):
    """Standalone synthetic checker; no producer values or class labels."""
    mask, a, b, c, settings, scheme = witness
    assert type(mask) is int and 0 <= mask < 1 << n and mask.bit_count() == 3
    assert len({a, b, c}) == 3 and all(type(x) is int and 0 <= x < 8 for x in (a, b, c))
    assert settings in (1, 2, 3) and scheme in range(4)
    group = [i for i in range(n) if mask & (1 << i)]
    patterns = (0, (1 << n) - 1) if scheme == 0 else tuple(
        sum(int(((i // scheme) % 2 == 0) != bool(side)) << i for i in range(n)) for side in range(2))
    signatures = []
    for local in (a, b, c):
        sig = []
        offset = sum(((local >> j) & 1) << raw for j, raw in enumerate(group))
        for setting, pattern in enumerate(patterns):
            if settings & (1 << setting):
                row = (pattern & ~mask) | offset
                sig.extend((truth >> row) & 1 for truth in tables)
        signatures.append(tuple(sig))
    assert len(set(signatures)) == 3


def _check_program(result, tables):
    n, circuit = result["n"], result["circuit"]
    group, taps = set(result["triple"]), set(result["summary_wires"])
    dependencies = [{j} for j in range(n)] + [set(), set()]
    cut = [set() if j in taps else {j} for j in range(n)] + [set(), set()]
    for index, (a, b) in enumerate(circuit["gates"]):
        wire = n + 2 + index
        dependencies.append(dependencies[a] | dependencies[b])
        cut.append(set() if wire in taps else cut[a] | cut[b])
    assert all(dependencies[t] <= group for t in taps)
    assert all(not cut[o] & group for o in circuit["outputs"])
    for row in range(1 << n):
        values = [(row >> j) & 1 for j in range(n)] + [0, 1]
        for a, b in circuit["gates"]:
            values.append(1 ^ (values[a] & values[b]))
        assert tuple(values[o] for o in circuit["outputs"]) == tuple((t >> row) & 1 for t in tables)


def self_test():
    """Hand/random synthetic regressions; never import a study panel or fit."""
    import random
    rng = random.Random(261115)
    checked = witnesses = discarded = 0
    # Small arbitrary tables exercise width3 and many tied minima as well as
    # chance one-bit groups; parity/conjunction provide known widths1/2.
    for n in (4, 5):
        full = (1 << (1 << n)) - 1
        parity = sum((x.bit_count() & 1) << x for x in range(1 << n))
        conjunction = 1 << ((1 << n) - 1)
        targets = [(parity, full ^ parity), (parity, conjunction)]
        targets += [tuple(rng.getrandbits(1 << n) for _ in range(2)) for _ in range(8)]
        for tables in targets:
            exact = ProbeSolver(n, enabled=False).solve(tables)
            for scheme in range(4):
                engine = ProbeSolver(n, scheme=scheme)
                result = engine.solve(tables)
                assert (result["status"], result["width"], result["triple"], result["class_count"]) == (
                    exact["status"], exact["width"], exact["triple"], exact["class_count"])
                if result["status"] != "exact":
                    continue
                assert result["circuit"] == exact["circuit"]
                _check_program(result, tables)
                for witness in result["witnesses"]:
                    _check_witness(witness, tables, n)
                work = result["work"]
                assert work["probe_row_requests"] == work["probe_row_unique"] + work["probe_row_reuses"]
                assert work["probe_output_bit_reads"] == 2 * work["probe_row_unique"]
                assert work["probe_row_unique"] <= 1 << n
                assert work["probe_candidates"] == work["probe_witness_hits"] + work["probe_unresolved_fallback"]
                assert work["group_trials"] == work["attempted_by_exact"] + work["resolved_by_witness"]
                assert work["group_bound_rejections"] == work["exact_bound_rejections"] + work["resolved_by_witness"]
                assert work["witness_records_returned"] == len(result["witnesses"])
                assert work["probe_row_requests"] <= 16 * work["probe_candidates"]
                witnesses += len(result["witnesses"])
                discarded += work["witnesses_discarded_after_width1"]
                repeated = engine.solve(tables)
                assert repeated["work"]["probe_row_requests"] == 0
                assert repeated["witnesses"] == result["witnesses"]
                # Calibration namespaces cannot feed a proof to primary mode.
                advice = {sum(1 << j for j in g): -1 for g in combinations(range(n), 3)}
                other = engine.solve(tables, advice=advice)
                assert not other["work"]["probe_row_requests"] and not other["witnesses"]
                assert other["work"]["attempted_by_exact"] == other["work"]["group_trials"]
                assert engine.solve(tables)["witnesses"] == result["witnesses"]
                checked += 1
    assert witnesses > 0
    # A mathematically width3 pair needs all wider-incumbent checks, even
    # though a fixed-context >1bit proof would be true. Such proofs alone
    # must never incorrectly turn a width3 minimum into a width2 assertion.
    wide = [0, 0]
    for row in range(16):
        a, b, c, d = ((row >> j) & 1 for j in range(4))
        wide[0] |= (a ^ (b & c) ^ d) << row
        wide[1] |= (b ^ (a & d) ^ c) << row
    wide_result = ProbeSolver(4).solve(tuple(wide))
    assert wide_result["width"] == 3 and wide_result["work"]["probe_candidates"] == 0
    assert wide_result["work"]["attempted_by_exact"] == wide_result["work"]["group_trials"] == 4
    _check_program(wide_result, tuple(wide))
    # A late one-bit triple follows an earlier wider incumbent and witnessed
    # rejections. Past discovery remains charged, but no redundant proof is
    # returned when the eventual lower bound is already attained.
    late = [0, 0]
    for row in range(32):
        a, b, c, d, e = ((row >> j) & 1 for j in range(5))
        h = c & d & e
        late[0] |= (h ^ a ^ b) << row
        late[1] |= (h | (a & b)) << row
    result = ProbeSolver(5).solve(tuple(late))
    baseline = ProbeSolver(5, enabled=False).solve(tuple(late))
    assert result["width"] == 1 and result["triple"] == [2, 3, 4]
    assert result["circuit"] == baseline["circuit"] and not result["witnesses"]
    assert result["work"]["probe_witness_hits"] > 0
    assert result["work"]["witnesses_discarded_after_width1"] == result["work"]["probe_witness_hits"]
    _check_program(result, tuple(late))
    discarded += result["work"]["witnesses_discarded_after_width1"]
    # Independent screen schedule guard: three first-context signatures use
    # exactly3 row requests, and an immediate first-context hit skips its pair.
    engine = ProbeSolver(4)
    engine._tables = (0b1010101010101010, 0b1100110011001100)
    witness = engine._screen((0, 1, 2), tuple(range(8)), 0)
    assert witness[4] == 1 and engine.work_counters()["probe_row_requests"] == 3
    _check_witness(witness, engine._tables, 4)
    return {"synthetic_only": True, "status": "passed", "scheme_cases": checked,
            "returned_witnesses_checked": witnesses, "earlier_witnesses_discarded": discarded,
            "same_exact_program_all_schemes_reuse_and_advice_isolation": "passed"}


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("use --self-test; real tables and calibration are supplied by the caller")
    print(json.dumps(self_test(), sort_keys=True))
