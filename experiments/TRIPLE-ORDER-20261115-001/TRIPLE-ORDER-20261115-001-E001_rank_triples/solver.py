"""Shared exact primitive search with ordering as the only matched difference.

OrderedSolver(n, ranker=None, remember=True).solve((truth0,truth1)) uses the
sealed JointSolver primitive code/builder. Every order uses this same direct
lazy packed-column check, bound updates, caches, and physical constructor.
Ranker protocol: order(outputs,eligible) -> iterable of triples. None means
lazy lex, without ranking materialization or sorting. Runtime checks visited
membership, skips duplicates, and appends unseen lex proposals on exhaustion.
Only a proved minimum width1 allows an unfinished priority iterator to stop.

Memory is arm-local and initially empty: each single complete output truth
maps to its last physically verified selected triple. Eligible remembered
triples are proposals ONLY and are rechecked on both current outputs. They
precede the policy, so a successful width1 recall avoids all scoring.

search_audit.attempts rows:
  [g0,g1,g2,bound_before,exact_K_or_0_if_truncated,columns_read,source]
source0=remembered,1=ordinary policy/lex,2=lex completion of a partial policy.
first_minimum_rank is1-based in this actual deduplicated scan, the position
of its last strict width improvement. No offline oracle is used. Exact-pair
interface-cache hits have no current attempts and expose the cached rank.

One uniform preparation timer is used by ALL matched methods when ordinary
ordering is reached: create/call the iterator and perform first next(). This
captures eager scoring/sorting or lazy initial preparation. ranking_cpu_ns
reports that segment for rankers (zero for lex), not arbitrary later iterator
work; later work remains in full paid group/search CPU. No per-attempt timer.

FixedRanker(n) is an extra untrained four-cofactor-diversity ordering, separate
from any supplied fixed_model(). PrimitiveReference is lazily re-exported as
a strong independent full-scan comparator. No task/model/data files are read.
"""

from __future__ import annotations

import hashlib
import importlib.util
from itertools import chain, combinations
from math import comb
import operator
from pathlib import Path
import sys
from time import perf_counter, process_time_ns


_ROOT = Path(__file__).resolve().parents[3]
_PREVIOUS = "experiments/FOLD-TWO-OUTPUT-20261115-001/FOLD-TWO-OUTPUT-20261115-001-E001_joint_tables"
SOURCE_DEPENDENCIES = (_PREVIOUS + "/joint_solver.py", _PREVIOUS + "/primitive_reference.py")
SOURCE_SHA256 = {
    SOURCE_DEPENDENCIES[0]: "a9b5d4a0ab99cbcfad7f266092157139bcef0059495f6bb136c453a8c59e6391",
    SOURCE_DEPENDENCIES[1]: "1f00eae0857e74b290e87ae1d9b335fb1d8c9ed0ed25ebd7d59201b91005a105",
}


def _load(relative, alias):
    path = _ROOT / relative
    if hashlib.sha256(path.read_bytes()).hexdigest() != SOURCE_SHA256[relative]:
        raise RuntimeError("frozen primitive dependency changed: " + relative)
    if alias in sys.modules:
        module = sys.modules[alias]
        if Path(module.__file__).resolve() != path.resolve():
            raise ImportError("primitive module alias points elsewhere")
        return module
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


_joint = _load(SOURCE_DEPENDENCIES[0], "_triple_order_frozen_joint")


def __getattr__(name):
    if name == "PrimitiveReference":
        cls = _load(SOURCE_DEPENDENCIES[1], "_triple_order_frozen_reference").PrimitiveReference
        globals()[name] = cls
        return cls
    raise AttributeError(name)


ORDER_COUNTERS = (
    "order_interface_hits", "order_ranker_calls", "order_ranker_candidates_supplied",
    "order_received_proposals", "order_duplicate_proposals", "order_memory_duplicates_skipped",
    "order_lex_completion_proposals", "order_remembered_outputs_seen",
    "order_remembered_eligible", "order_remembered_trials", "order_remembered_incumbents",
    "order_remembered_minimum_hits", "order_memory_updates", "order_attempts",
    "order_exact_group_counts", "order_truncated_group_checks",
)


class FixedRanker:
    """Fixed cheap rule: prefer fewer distinct zero/singleton joint columns.

    Computes four aligned packed columns per candidate; ties are lex. The
    rule has no learned weights, component identities, or data-dependent
    constants. Its own public layout/feature caches persist within an arm.
    """
    name = "four-cofactor-diversity"

    def __init__(self, n):
        if type(n) is not int or n < 3:
            raise ValueError("ranker requires at least three inputs")
        self.n, self.rows = n, 1 << n
        self.full = (1 << self.rows) - 1
        self.zero = tuple(self.full // ((1 << (1 << j)) + 1) for j in range(n))
        self._layouts, self._features = {}, {}
        self._work = {key: 0 for key in (
            "fixed_order_calls", "fixed_candidates", "fixed_feature_hits", "fixed_layout_builds",
            "fixed_packed_shifts", "fixed_packed_masks", "fixed_response_keys")}

    def work_counters(self):
        return dict(self._work)

    def order(self, outputs, eligible):
        self._work["fixed_order_calls"] += 1
        joint = outputs[0] | (outputs[1] << self.rows)
        scored = []
        for group in eligible:
            self._work["fixed_candidates"] += 1
            key = (outputs, group)
            score = self._features.get(key)
            if score is None:
                layout = self._layouts.get(group)
                if layout is None:
                    mask = self.full
                    for j in group:
                        mask &= self.zero[j]
                    layout = self._layouts[group] = (mask | (mask << self.rows), (0, *(1 << j for j in group)))
                    self._work["fixed_layout_builds"] += 1
                mask, offsets = layout
                score = len({(joint >> shift) & mask for shift in offsets})
                self._work["fixed_packed_shifts"] += 4
                self._work["fixed_packed_masks"] += 4
                self._work["fixed_response_keys"] += 4
                self._features[key] = score
            else:
                self._work["fixed_feature_hits"] += 1
            scored.append((score, group))
        scored.sort()
        return (group for _, group in scored)


class OrderedSolver(_joint.JointSolver):
    def __init__(self, n, ranker=None, remember=True):
        wall, cpu = perf_counter(), process_time_ns()
        super().__init__(n, arm="primitive")
        if ranker is not None and not callable(getattr(ranker, "order", None)):
            raise ValueError("ranker needs order(outputs,eligible)")
        if type(remember) is not bool:
            raise ValueError("remember must be Boolean")
        self.ranker, self.remember = ranker, remember
        self.order_name = "lex" if ranker is None else getattr(ranker, "name", type(ranker).__name__)
        self._remembered, self._search_audits = {}, {}
        self._current_audit = None
        self._work.update(dict.fromkeys(ORDER_COUNTERS, 0))
        self.setup_cpu_ns = process_time_ns() - cpu
        self.setup_seconds = perf_counter() - wall
        self._setup_record = {"cpu_ns": self.setup_cpu_ns, "seconds": self.setup_seconds,
                              "work": self.work_counters()}

    def _group(self, joint, group, bound):
        """Primitive-only fast loop; no fold witnesses or column closure."""
        mask, offsets, _ = self._layout(group)
        labels, lookup, unique = [], {}, []
        seen = shifts = 0
        failed = False
        for shift in offsets:
            pair = (joint >> shift) & mask if shift else joint & mask
            seen += 1
            shifts += int(bool(shift))
            label = lookup.get(pair)
            if label is None:
                label = len(unique)
                lookup[pair] = label
                unique.append(pair)
                if len(unique) > bound:
                    failed = True
                    break
            labels.append(label)
        work = self._work
        work["residual_joint_rows"] += seen
        work["residual_packed_shifts"] += shifts
        work["residual_packed_masks"] += seen
        work["residual_row_equivalents"] += seen * (self.rows >> 2)
        work["joint_class_lookups"] += seen
        if failed:
            work["group_bound_rejections"] += 1
            return None
        pairs = tuple((value & self.full, value >> self.rows) for value in unique)
        work["residual_pairs_unpacked"] += len(pairs)
        return len(pairs), tuple(labels), tuple(pairs[label] for label in labels), None

    @staticmethod
    def _normalize_group(value, shared):
        try:
            group = value if isinstance(value, tuple) and all(type(j) is int for j in value) else tuple(operator.index(j) for j in value)
        except (TypeError, ValueError) as exc:
            raise ValueError("policy proposed a malformed triple") from exc
        if (len(group) != 3 or not (group[0] < group[1] < group[2])
                or any(j not in shared for j in group)):
            raise ValueError("policy proposed an ineligible/noncanonical triple")
        return group

    def _proposals(self, tables, shared, audit):
        delivered = set()
        if self.remember:
            for truth in tables:
                group = self._remembered.get(truth)
                if group is None:
                    continue
                self._work["order_remembered_outputs_seen"] += 1
                if any(j not in shared for j in group) or group in delivered:
                    continue
                self._work["order_remembered_eligible"] += 1
                audit["remembered_candidates"].append(list(group))
                delivered.add(group)
                yield group, 0
        # This block is not entered when a remembered candidate proves width1.
        wall, cpu = perf_counter(), process_time_ns()
        if self.ranker is None:
            iterable = combinations(shared, 3)
        else:
            eligible = tuple(combinations(shared, 3))
            self._work["order_ranker_calls"] += 1
            self._work["order_ranker_candidates_supplied"] += len(eligible)
            audit["ranking_called"] = True
            iterable = self.ranker.order(tables, eligible)
        iterator = iter(iterable)
        sentinel = object()
        first = next(iterator, sentinel)
        audit["ordering_prepare_cpu_ns"] = process_time_ns() - cpu
        audit["ordering_prepare_seconds"] = perf_counter() - wall
        if self.ranker is not None:
            audit["ranking_cpu_ns"] = audit["ordering_prepare_cpu_ns"]
        policy_seen = set()
        sequence = iterator if first is sentinel else chain((first,), iterator)
        if self.ranker is None:
            # combinations() is already canonical, unique, and in-domain.
            # Keep lazy lex as the genuinely cheap matched primitive control.
            for group in sequence:
                self._work["order_received_proposals"] += 1
                if group in delivered:
                    self._work["order_memory_duplicates_skipped"] += 1
                    continue
                yield group, 1
            return
        shared_set = frozenset(shared)
        for raw in sequence:
            self._work["order_received_proposals"] += 1
            group = self._normalize_group(raw, shared_set)
            if group in policy_seen:
                self._work["order_duplicate_proposals"] += 1
                continue
            policy_seen.add(group)
            if group in delivered:
                self._work["order_memory_duplicates_skipped"] += 1
                continue
            delivered.add(group)
            yield group, 1
        if self.ranker is not None:
            # A partial priority list is safe: all unvisited triples remain
            # available unless width1 already proved the global lower bound.
            for group in combinations(shared, 3):
                if group not in delivered:
                    self._work["order_lex_completion_proposals"] += 1
                    delivered.add(group)
                    yield group, 2

    def _interface(self, tables):
        work = self._work
        if tables in self._interfaces:
            work["group_cache_hits"] += 1
            work["order_interface_hits"] += 1
            saved = self._search_audits[tables]
            self._current_audit = {
                **saved, "interface_cache_hit": True, "attempts": [], "candidates_considered": 0,
                "first_minimum_rank": None, "cached_first_minimum_rank": saved["first_minimum_rank"],
                "ranking_called": False, "ranking_cpu_ns": 0, "ordering_prepare_cpu_ns": 0,
                "ordering_prepare_seconds": 0.0, "remembered_candidates": [],
            }
            return self._interfaces[tables]
        support = tuple(tuple(i for i, mask in enumerate(self.zero) if (t ^ (t >> (1 << i))) & mask)
                        for t in tables)
        work["support_bit_tests"] += self.n * 2
        shared = tuple(sorted(set(support[0]) & set(support[1])))
        eligible_count = comb(len(shared), 3)
        work["eligible_group_count"] += eligible_count
        audit = {
            "order": self.order_name, "memory_enabled": self.remember,
            "eligible_count": eligible_count, "interface_cache_hit": False,
            "attempts": [], "candidates_considered": 0, "first_minimum_rank": None,
            "cached_first_minimum_rank": None, "remembered_candidates": [],
            "ranking_called": False, "ranking_cpu_ns": 0, "ordering_prepare_cpu_ns": 0,
            "ordering_prepare_seconds": 0.0,
            "ranking_cpu_scope": "order() plus first next(); later iterator work is in total group/search CPU",
            "attempt_fields": ["g0", "g1", "g2", "bound", "exact_K_or_0", "columns", "source"],
            "source_codes": {"0": "remembered", "1": "ordinary", "2": "lex_completion"},
            "stopped_at_minimum_one": False, "full_eligible_covered": False,
        }
        best, bound = None, 8
        if eligible_count:
            joint = tables[0] | (tables[1] << self.rows)
            work["joint_tables_joined"] += 1
            for group, source in self._proposals(tables, shared, audit):
                work["groups_requested"] += 1
                work["group_trials"] += 1
                work["order_attempts"] += 1
                if source == 0:
                    work["order_remembered_trials"] += 1
                old_columns = work["residual_joint_rows"]
                result = self._group(joint, group, bound)
                count = 0 if result is None else result[0]
                audit["attempts"].append([*group, bound, count,
                                           work["residual_joint_rows"] - old_columns, source])
                audit["candidates_considered"] += 1
                if result is None:
                    work["group_failures"] += 1
                    work["order_truncated_group_checks"] += 1
                    continue
                work["order_exact_group_counts"] += 1
                count, classes, columns, orientation = result
                if count < 2:
                    raise AssertionError("an eligible group must essentially affect both outputs")
                width = (count - 1).bit_length()
                best = (group, count, classes, columns, orientation)
                work["group_incumbents"] += 1
                audit["first_minimum_rank"] = audit["candidates_considered"]
                if source == 0:
                    work["order_remembered_incumbents"] += 1
                if width == 1:
                    audit["stopped_at_minimum_one"] = True
                    if source == 0:
                        work["order_remembered_minimum_hits"] += 1
                    break
                bound = 1 << (width - 1)
        audit["full_eligible_covered"] = audit["candidates_considered"] == eligible_count
        self._interfaces[tables] = (shared, best)
        self._search_audits[tables] = audit
        self._current_audit = audit
        return shared, best

    def _ranking_snapshot(self):
        method = None if self.ranker is None else getattr(self.ranker, "work_counters", None)
        if not callable(method):
            return {}
        values = method()
        if not isinstance(values, dict):
            raise ValueError("ranker work_counters() must return a dictionary")
        try:
            return {key: operator.index(value) for key, value in values.items()}
        except TypeError as exc:
            raise ValueError("ranker work counters must be integers") from exc

    def solve(self, supplied, second=None):
        wall, cpu = perf_counter(), process_time_ns()
        before = self.work_counters()
        ranking_before = self._ranking_snapshot()
        result = super().solve(supplied, second)
        tables = tuple(supplied) if second is None else (supplied, second)
        if self.remember and result["status"] == "exact":
            group = tuple(result["triple"])
            for truth in tables:
                self._remembered[truth] = group
                self._work["order_memory_updates"] += 1
        result["work"].update({key: self._work[key] - before[key] for key in ORDER_COUNTERS})
        result["search_audit"] = {**self._current_audit,
                                  "remembered_output_columns": len(self._remembered)}
        ranking_after = self._ranking_snapshot()
        result["ranking_work"] = {key: ranking_after.get(key, 0) - ranking_before.get(key, 0)
                                  for key in set(ranking_before) | set(ranking_after)}
        # Include the matched wrapper's public memory update/audit bookkeeping
        # in reported total CPU/wall; common external paid timing remains the
        # final authority for the complete return and serialization.
        elapsed_cpu, elapsed = process_time_ns() - cpu, perf_counter() - wall
        extra_cpu = max(0, elapsed_cpu - result["timing"]["cpu_ns"])
        extra_wall = max(0.0, elapsed - result["timing"]["elapsed_seconds"])
        result["timing"]["ordering_wrapper_cpu_ns"] = extra_cpu
        result["timing"]["ordering_wrapper_seconds"] = extra_wall
        result["timing"]["cpu_ns"] = elapsed_cpu
        result["timing"]["elapsed_seconds"] = elapsed
        result["timing"]["search_cpu_ns"] += extra_cpu
        result["timing"]["search_seconds"] += extra_wall
        self._total_cpu_ns += extra_cpu
        self._total_seconds += extra_wall
        return result

    def ledger(self):
        result = super().ledger()
        result["cache_entries"].update(remembered_output_columns=len(self._remembered),
                                       ordered_search_audits=len(self._search_audits))
        return result


def _check(result, tables):
    assert result["status"] == "exact"
    circuit = result["circuit"]
    n, taps = circuit["n"], set(result["summary_wires"])
    group = set(result["triple"])
    dependencies = [{j} for j in range(n)] + [set(), set()]
    cut_dependencies = [{j} if j not in taps else set() for j in range(n)] + [set(), set()]
    for index, (a, b) in enumerate(circuit["gates"]):
        wire = n + 2 + index
        dependencies.append(dependencies[a] | dependencies[b])
        cut_dependencies.append(set() if wire in taps else cut_dependencies[a] | cut_dependencies[b])
    assert all(dependencies[tap] <= group for tap in taps)
    assert all(not (cut_dependencies[o] & group) for o in circuit["outputs"])
    for x in range(1 << n):
        values = [(x >> j) & 1 for j in range(n)] + [0, 1]
        for a, b in circuit["gates"]:
            values.append(1 ^ (values[a] & values[b]))
        assert tuple(values[o] for o in circuit["outputs"]) == tuple((t >> x) & 1 for t in tables)


def _oracle(tables, n):
    support = [j for j in range(n) if all(any(((truth >> x) & 1) != ((truth >> (x ^ (1 << j))) & 1)
                                            for x in range(1 << n)) for truth in tables)]
    classes = {}
    for group in combinations(support, 3):
        outside = tuple(j for j in range(n) if j not in group)
        profiles = set()
        for local in range(8):
            offset = sum(((local >> j) & 1) << p for j, p in enumerate(group))
            profiles.add(tuple(tuple((truth >> (offset | sum(((v >> j) & 1) << p for j, p in enumerate(outside)))) & 1
                                       for v in range(1 << len(outside))) for truth in tables))
        classes[group] = len(profiles)
    return support, classes


def self_test():
    """Synthetic truth tables and stub policies, never official data/models."""
    n = 4
    parity = sum((x.bit_count() & 1) << x for x in range(16))
    conjunction = 1 << 15
    complement = 65535 ^ parity
    wide = [0, 0]
    for x in range(16):
        a, b, c, d = ((x >> j) & 1 for j in range(4))
        wide[0] |= (a ^ (b & c) ^ d) << x
        wide[1] |= (b ^ (a & d) ^ c) << x

    class Reverse:
        name = "synthetic-reverse"
        def __init__(self):
            self.calls = 0
        def order(self, outputs, eligible):
            self.calls += 1
            return reversed(eligible)

    class Partial:
        def order(self, outputs, eligible):
            yield eligible[-1]
            yield eligible[-1]

    tests = ((parity, complement), (parity, conjunction), tuple(wide))
    checked = 0
    for tables, expected in zip(tests, (1, 2, 3)):
        shared, classes = _oracle(tables, n)
        minimum = min((count - 1).bit_length() for count in classes.values())
        assert minimum == expected
        for ranker in (None, FixedRanker(n), Reverse(), Partial()):
            engine = OrderedSolver(n, ranker, remember=False)
            result = engine.solve(tables)
            assert result["width"] == minimum and result["class_count"] == classes[tuple(result["triple"])]
            _check(result, tables)
            audit = result["search_audit"]
            attempted = [tuple(row[:3]) for row in audit["attempts"]]
            assert len(set(attempted)) == len(attempted)
            first = next(i for i, group in enumerate(attempted, 1)
                         if (classes[group] - 1).bit_length() == minimum)
            assert audit["first_minimum_rank"] == first
            assert audit["candidates_considered"] == len(audit["attempts"]) == result["work"]["group_trials"]
            assert sum(row[5] for row in audit["attempts"]) == result["work"]["residual_joint_rows"]
            assert result["fold_uses"] == 0
            if minimum > 1:
                assert set(attempted) == set(classes) and audit["full_eligible_covered"]
            cached = engine.solve(tables)
            assert cached["search_audit"]["interface_cache_hit"]
            assert not cached["search_audit"]["attempts"] and not cached["work"]["group_trials"]
            checked += 1
    # Tied minima select different first triples without changing exactness.
    lex = OrderedSolver(n, remember=False).solve(tests[0])
    reverse = OrderedSolver(n, Reverse(), remember=False).solve(tests[0])
    assert lex["triple"] != reverse["triple"] and lex["width"] == reverse["width"] == 1
    # A recalled single output neither promises its partner nor freezes K.
    policy = Reverse()
    memory = OrderedSolver(n, policy)
    initial = memory.solve(tests[0])
    calls = policy.calls
    recalled = memory.solve((parity, parity))
    assert not recalled["search_audit"]["ranking_called"] and policy.calls == calls
    assert recalled["search_audit"]["attempts"][0][-1] == 0 and recalled["width"] == 1
    changed = memory.solve((parity, conjunction))
    assert changed["width"] == 2 and changed["search_audit"]["ranking_called"]
    assert changed["search_audit"]["attempts"][0][4] == 3
    _check(changed, (parity, conjunction))
    # Eligibility is semantic intersection, and empty domains stay explicit.
    singleton = sum((x & 1) << x for x in range(16))
    absent = OrderedSolver(n).solve((parity, singleton))
    assert absent["status"] == "no_eligible_triple" and absent["shared_support"] == [0]
    # The independent former primitive comparator is a real separate method.
    reference = __getattr__("PrimitiveReference")(n).solve(tests[1])
    assert reference["width"] == 2
    _check(reference, tests[1])
    return {"synthetic_only": True, "status": "passed", "ordered_cases": checked,
            "widths": [1, 2, 3], "ties_partial_orders_recall_partner_change_and_cut": "passed"}


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("use --self-test; data and frozen policies are supplied by the caller")
    print(json.dumps(self_test(), sort_keys=True))
