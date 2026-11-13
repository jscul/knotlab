"""TRUE-RATE: uncapped side summaries and exact ray-summary cycle means.

Only finite summaries with finite construction witnesses are introduced.  A
closed table is the least min-plus fixed point, not a cost-truncated table.
Graph joins retain full environment masks until ALL children have joined.
Importing this module runs no study and writes no files.
"""
from __future__ import annotations

from functools import lru_cache
import importlib.util
import json
import math
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TB_PATH = ROOT / "experiments/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/codex/true_bond.py"
GRAPH_PATH = ROOT / "experiments/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/codex/graph_algorithms.py"
REFERENCE_PATH = ROOT / "artifacts/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/true_rates_all.jsonl"
RAY_REFERENCE_PATH = ROOT / "artifacts/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/rates_all.jsonl"
TABLE_LIMIT = 200_000
NODE_LIMIT = 2_000_000
SMAX = 12


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=1)
def tb_module():
    return _load("true_rate_tb", TB_PATH)


@lru_cache(maxsize=1)
def graph_module():
    return _load("true_rate_graph_algorithms", GRAPH_PATH)


def study_families():
    return tb_module().study_families()


@lru_cache(maxsize=1)
def reference_rows():
    rows = {}
    with REFERENCE_PATH.open() as stream:
        for line in stream:
            if not line.strip():
                continue
            row = json.loads(line)
            if row["idx"] in rows:
                raise ValueError("duplicate TRUE-BOND reference index")
            if len(row["L"]) != SMAX or len(row["L_ray"]) != SMAX:
                raise ValueError("reference must have twelve depth cells")
            rows[row["idx"]] = row
    if set(rows) != set(study_families()):
        raise ValueError("TRUE-BOND reference does not match the 226-family study")
    return rows


def peak_mb():
    """Process high-water RSS, MiB; cumulative if a worker serves many cases."""
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value / (1024 * 1024 if sys.platform == "darwin" else 1024)


class Budget:
    def __init__(self, deadline):
        self.deadline = deadline
        self.operations = 0

    def check(self):
        if time.monotonic() >= self.deadline:
            raise TimeoutError("phase time limit reached")

    def tick(self):
        self.operations += 1
        if self.operations & 255 == 0:
            self.check()


class GraphCapReached(Exception):
    pass


class RateComputation:
    def __init__(self, defs, budget, *, table_limit=TABLE_LIMIT, node_limit=NODE_LIMIT):
        self.budget = budget
        self.dp = tb_module().FamilyDP(defs)
        self.dp.checkpoint = budget.tick
        self.table_limit = table_limit
        self.node_limit = node_limit
        self.table = dict(self.dp.generic)
        self.closed = False
        self.table_rounds = 0
        self.table_reason = None
        self.nodes = []
        self.index = {}
        self.base_cost = {}
        self.adj = []
        self.close_cost = []
        self.expanded_nodes = 0
        self.base_complete = False
        self.complete = False
        self.graph_reason = None
        self._side_lifts = None

    def close_table(self):
        """TB composition without a cost cap, including strict cost decreases.

        The snapshot prevents accidental use of an unfinished iteration as a
        proof of closure.  If a composition times out, previous iterations are
        retained; each retained entry still has a finite witness.
        """
        dp = self.dp
        while True:
            self.budget.check()
            changed = False
            for summary, cost in self._generic_round():
                self.budget.tick()
                if cost < self.table.get(summary, math.inf):
                    self.table[summary] = cost
                    changed = True
                    # Stop PAST the specified cap, preserving the last witness.
                    if len(self.table) > self.table_limit:
                        self.table_reason = "summary_cap"
                        return
            self.table_rounds += 1
            if not changed:
                self.closed = True
                return

    def _generic_round(self):
        """TB.combine at infinite cap, streaming its FINAL port projections.

        Its exact full-environment min-plus merging is retained for the side
        table.  Streaming the final stage enforces the summary cap immediately
        rather than allocating an unbounded generated port-summary dictionary.
        The graph's stricter no-partial-deduplication rule is in _joins.
        """
        dp = self.dp
        layer = {}
        for summary, cost in dp.local_options("generic"):
            if 0 not in summary[0] and 0 not in summary[1]:
                layer[summary] = min(cost, layer.get(summary, math.inf))
        for child in range(dp.nchild):
            lifted = []
            for summary, cost in self.table.items():
                self.budget.tick()
                lifted.append((dp._lift(summary, child), cost))
            following = {}
            for left, cost in layer.items():
                for right, added in lifted:
                    self.budget.tick()
                    result = dp._intersect(left, right)
                    if 0 in result[0] or 0 in result[1]:
                        continue
                    candidate = cost + added
                    if candidate < following.get(result, math.inf):
                        following[result] = candidate
            layer = following
            if not layer:
                break
        for environment, cost in layer.items():
            self.budget.tick()
            summary = dp._project(environment)
            if dp._admissible(summary, cost, "generic"):
                yield summary, cost

    def _joins(self, kind, ray=None):
        """Yield fully joined/projected summaries, with no partial deduplication.

        A graph node is a PORT summary.  Every intermediate here is instead an
        ENVIRONMENT summary.  Even equal intermediate summaries are enumerated
        separately; only the caller merges equal final projected summaries.
        """
        dp = self.dp
        if self._side_lifts is None:
            side_lifts = []
            for child in range(dp.nchild):
                lifted = []
                for summary, cost in self.table.items():
                    self.budget.tick()
                    lifted.append((dp._lift(summary, child), cost))
                side_lifts.append(lifted)
            self._side_lifts = side_lifts
        children = list(self._side_lifts)
        if ray is not None:
            children[0] = [(dp._lift(ray, 0), 0)]

        def visit(child, left, cost):
            if child == dp.nchild:
                projected = dp._project(left)
                if dp._admissible(projected, cost, kind):
                    yield projected, cost
                return
            for right, added in children[child]:
                self.budget.tick()
                result = dp._intersect(left, right)
                if 0 in result[1] or (kind != "root" and 0 in result[0]):
                    continue
                yield from visit(child + 1, result, cost + added)

        for summary, cost in dp.local_options(kind):
            self.budget.tick()
            if 0 in summary[1] or (kind != "root" and 0 in summary[0]):
                continue
            yield from visit(0, summary, cost)

    def _intern(self, summary):
        known = self.index.get(summary)
        if known is not None:
            return known
        if len(self.nodes) >= self.node_limit:
            self.graph_reason = "node_cap"
            raise GraphCapReached("reachable node cap reached")
        node = len(self.nodes)
        self.index[summary] = node
        self.nodes.append(summary)
        self.adj.append([])
        self.close_cost.append(math.inf)
        return node

    def build_graph(self):
        self.budget.check()
        for summary, cost in self._joins("target"):
            node = self._intern(summary)
            if node is not None:
                self.base_cost[node] = min(cost, self.base_cost.get(node, math.inf))
        self.base_complete = self.graph_reason is None
        # Interning order is breadth-first reachability, so every listed node
        # has a finite path from a base even if an expansion is interrupted.
        cursor = 0
        while cursor < len(self.nodes):
            self.budget.check()
            summary = self.nodes[cursor]
            # Retain acceptance and arcs incrementally, not only on completion
            # of a large expansion.  Every partial arc remains an exact join.
            for (f, g), cost in self._joins("root", summary):
                if 0 in f and 0 not in g:
                    self.close_cost[cursor] = min(self.close_cost[cursor], cost)
            costs = dict(self.adj[cursor])
            self.adj[cursor] = costs
            try:
                for target, cost in self._joins("middle", summary):
                    target_node = self._intern(target)
                    if target_node is not None and cost < costs.get(target_node, math.inf):
                        costs[target_node] = cost
            finally:
                self.adj[cursor] = list(costs.items())
            self.expanded_nodes += 1
            cursor += 1
        self.complete = self.base_complete and self.graph_reason is None

    def gate(self, reference=None):
        """s-1 middle arcs followed by the C_0 accepting/root arc: s steps.

        At s=1 the target base at C_1 goes directly to C_0.  Charging s
        middle arcs PLUS acceptance would be an off-by-one error.
        """
        layer = dict(self.base_cost)
        observed = []
        expected = reference["L"] if reference is not None else [None] * SMAX
        mismatches = []
        checked = 0
        for s in range(1, SMAX + 1):
            self.budget.check()
            value = min((cost + self.close_cost[node] for node, cost in layer.items()),
                        default=math.inf)
            value = None if math.isinf(value) else value
            observed.append(value)
            if expected[s - 1] is not None:
                checked += 1
                if value != expected[s - 1]:
                    kind = ("below_reference" if value is not None and value < expected[s - 1]
                            else "exact_disagreement" if self.closed and self.complete
                            else "missing_witness_in_partial_graph")
                    mismatches.append({"s": s, "expected": expected[s - 1],
                                       "observed": value, "kind": kind})
            if s < SMAX:
                following = {}
                for source, cost in layer.items():
                    for target, weight in self.adj[source]:
                        self.budget.tick()
                        candidate = cost + weight
                        if candidate < following.get(target, math.inf):
                            following[target] = candidate
                layer = following
        return {"L": observed, "gate_checked": checked, "mismatches": mismatches,
                "gate_ok": not mismatches if checked else None,
                "gate_status": ("checked" if self.closed and self.complete
                                else "checked_partial") if checked else "no_reference"}

    def analyze(self):
        """Reuse PROVED-RATE's iterative components and exact two-pass Karp."""
        self.budget.check()
        graph = graph_module()
        # Its interface uses a finite sentinel.  Scaling finite closing costs
        # to 0 preserves EXACTLY the accepting set used for graph trimming;
        # closing costs do not enter a cycle mean.  The gate uses real costs.
        acceptance = [0 if cost < math.inf else graph.INF for cost in self.close_cost]
        result = graph.analyze_graph(self.adj, acceptance, [None] * len(self.nodes),
                                     self.complete and self.closed, self.budget.check)
        return {"lambda_true": result["lambda"],
                "lambda_true_float": result["lambda_float"],
                "zero_cycle": result["zero_mean"],
                "acyclic": result["cyclic_sccs"] == 0,
                "trimmed_nodes": result["trimmed_nodes"],
                "sccs": result["sccs"], "cyclic_sccs": result["cyclic_sccs"],
                "cyclic_scc_edges": result["cyclic_scc_edges"],
                "max_cyclic_scc_nodes": result["max_cyclic_scc_nodes"],
                "analysis_complete": True}


def error_result(idx, seconds=0.0, status="error", message=None):
    """Conservative schema for a killed/failed attempt, never a fabricated rate."""
    return {"idx": idx, "closed": False, "table_size": 0, "complete": False,
            "nodes": 0, "trimmed_nodes": None, "gate_ok": None,
            "mismatches": [], "lambda_true": None, "lambda_true_float": None,
            "zero_cycle": None, "acyclic": None, "upper_bound": True,
            "seconds": round(seconds, 6), "peak_mb": round(peak_mb(), 3),
            "status": status, "error": message, "analysis_complete": False,
            "L": [None] * SMAX, "gate_checked": 0, "gate_status": "not_run"}


def run_family(idx, *, defs=None, reference=None, seconds_limit=60.0,
               table_limit=TABLE_LIMIT, node_limit=NODE_LIMIT):
    """One bounded attempt; reserve graph/analysis time for an honest fallback.

    Phase deadlines are 55%, 88%, and 100% of the family budget.  Earlier
    completion passes its unused time forward.  No cost cutoff is used.
    A timeout/cap leaves genuine finite constructions only.  Missing cycles
    are null (not a numerical bound), and partial acyclicity is only local.
    """
    if not math.isfinite(seconds_limit) or seconds_limit <= 0:
        raise ValueError("seconds_limit must be finite and positive")
    started = time.monotonic()
    budget = Budget(started + seconds_limit)
    result = error_result(idx)
    stages = {}
    state = None
    stage = "initialization"
    phase_start = started
    try:
        if defs is None:
            defs = study_families()[idx]
            if reference is None:
                reference = reference_rows()[idx]
        state = RateComputation(defs, budget, table_limit=table_limit, node_limit=node_limit)
        stages[stage] = time.monotonic() - phase_start
        # Every full table contains the empty side choice.  Compute a bounded
        # subset first and retain its witnessed arcs, so an interrupted later
        # base enumeration need not erase an already known cycle bound.
        stage, phase_start = "seed_graph", time.monotonic()
        budget.deadline = started + min(3.0, 0.08 * seconds_limit)
        try:
            state.build_graph()
        except (TimeoutError, GraphCapReached):
            pass
        except MemoryError:
            state.dp._intersect.cache_clear()
            state.dp._project.cache_clear()
        result["seed_nodes"] = len(state.nodes)
        result["seed_complete"] = state.complete
        state.complete = state.base_complete = False
        state.graph_reason = None
        state.expanded_nodes = 0
        state._side_lifts = None
        stages[stage] = time.monotonic() - phase_start
        stage, phase_start = "table", time.monotonic()
        budget.deadline = started + 0.55 * seconds_limit
        try:
            state.close_table()
        except TimeoutError:
            state.table_reason = "time_limit"
        except MemoryError:
            state.table_reason = "memory_limit"
            state.dp._intersect.cache_clear()
            state.dp._project.cache_clear()
        stages[stage] = time.monotonic() - phase_start
        state._side_lifts = None
        stage, phase_start = "graph", time.monotonic()
        budget.deadline = started + 0.88 * seconds_limit
        try:
            state.build_graph()
        except TimeoutError:
            state.graph_reason = "time_limit"
        except GraphCapReached:
            state.graph_reason = "node_cap"
        except MemoryError:
            state.graph_reason = "memory_limit"
        stages[stage] = time.monotonic() - phase_start
        state.dp._intersect.cache_clear()
        state.dp._project.cache_clear()
        for node, edges in enumerate(state.adj):
            if isinstance(edges, dict):
                state.adj[node] = list(edges.items())
        stage, phase_start = "gate", time.monotonic()
        budget.deadline = started + seconds_limit
        result.update(state.gate(reference))
        stages[stage] = time.monotonic() - phase_start
        stage, phase_start = "analysis", time.monotonic()
        result.update(state.analyze())
        stages[stage] = time.monotonic() - phase_start
        exact = state.closed and state.complete
        result["status"] = ("gate_mismatch" if result["gate_ok"] is False
                            else "done" if exact else "upper_bound")
        result["error"] = None
    except (TimeoutError, MemoryError) as exc:
        result["status"] = "analysis_timeout" if isinstance(exc, TimeoutError) else "memory_limit"
        result["error"] = str(exc) or type(exc).__name__
        stages[stage] = time.monotonic() - phase_start
    except Exception as exc:
        result["status"] = "error"
        result["error"] = f"{type(exc).__name__}: {exc}"
        stages[stage] = time.monotonic() - phase_start
    finally:
        if state is not None:
            result.update(closed=state.closed, table_size=len(state.table), complete=state.complete,
                          nodes=len(state.nodes), base_nodes=len(state.base_cost),
                          base_complete=state.base_complete, expanded_nodes=state.expanded_nodes,
                          edges=sum(len(edges) for edges in state.adj),
                          table_rounds=state.table_rounds, table_reason=state.table_reason,
                          graph_reason=state.graph_reason, operations=budget.operations)
            result["upper_bound"] = not (state.closed and state.complete and result["analysis_complete"])
            state.dp._intersect.cache_clear()
            state.dp._project.cache_clear()
        result["stage"] = stage
        result["stage_seconds"] = {key: round(value, 6) for key, value in stages.items()}
        result["seconds"] = round(time.monotonic() - started, 6)
        result["seconds_limit"] = seconds_limit
        result["peak_mb"] = round(peak_mb(), 3)
        result["peak_scope"] = "worker_lifetime_high_water_rss"
        result["limits"] = {"summaries": table_limit, "nodes": node_limit,
                            "table_deadline_fraction": 0.55, "graph_deadline_fraction": 0.88}
    return result
