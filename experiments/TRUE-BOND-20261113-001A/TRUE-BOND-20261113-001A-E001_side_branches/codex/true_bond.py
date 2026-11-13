"""Exact creator-owned (F, G) summaries for the TRUE-BOND specification.

No experiment is run on import. F and G are sorted tuples of 8-bit masks.
G is formed by forgetting a chosen distinction, never by guessing from F.
Only the supplied BD implementation and study JSONL are read outside CODEX.
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
import importlib.util
import itertools
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BD_PATH = ROOT / "experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/census.py"
RATES_PATH = ROOT / "artifacts/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/rates_all.jsonl"
Summary = tuple[tuple[int, ...], tuple[int, ...]]


@lru_cache(maxsize=1)
def bd_module():
    spec = importlib.util.spec_from_file_location("true_bond_bd", BD_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=1)
def study_families():
    """Use the specified conjunction, with null rates excluded, and check 226."""
    with RATES_PATH.open() as stream:
        rows = [json.loads(line) for line in stream if line.strip()]
    ids = {r["idx"] for r in rows if r.get("complete") is True
           and r.get("lambda_float") is not None and r["lambda_float"] > 0}
    families = {idx: defs for idx, defs in bd_module().families_one_def() if idx in ids}
    if len(ids) != 226 or set(families) != ids:
        raise ValueError(f"study membership mismatch: {len(ids)} rates, {len(families)} definitions")
    return families


def mask_from_boolean(values):
    return sum(1 << state for state, allowed in enumerate(values) if allowed)


def _subsets(values):
    for size in range(len(values) + 1):
        yield from itertools.combinations(values, size)


class FamilyDP:
    """A single definition, with bounded caches and explicit fixed-point closure."""

    def __init__(self, defs, *, mutant=False, deadline=None):
        if len(defs) != 1 or defs[0][0] != 3:
            raise ValueError("exactly one three-port definition is required")
        self.defs = defs
        _, self.locals, calls = defs[0]
        self.v = 3 + self.locals
        self.children = [tuple(args) for callee, args in calls if callee == "SELF"]
        if not self.children:
            raise ValueError("a first SELF call is required")
        self.nchild = len(self.children)
        self.mutant = mutant
        self.deadline = deadline
        self.operations = 0
        _, _, gd = bd_module().L.depth_sequence(defs, bd_module().L.TOP)
        self.g = mask_from_boolean(gd[0])
        self.empty: Summary = ((self.g,), (self.g,) if mutant else ())
        self.knots = [tuple(args) for callee, args in calls if callee == "K"]
        unknown = [callee for callee, _ in calls if callee not in ("K", "SELF")]
        if unknown:
            raise ValueError(f"unsupported callees: {unknown}")
        self.env_all = (1 << (1 << self.v)) - 1
        self.port_env = [0] * 8
        self.literal_env = [[0, 0] for _ in range(self.v)]
        self.argument_env = [[0] * 8 for _ in self.children]
        self.allowed_env = 0
        for env in range(1 << self.v):
            bit = 1 << env
            self.port_env[env & 7] |= bit
            for w in range(self.v):
                self.literal_env[w][(env >> w) & 1] |= bit
            for child, args in enumerate(self.children):
                state = sum(((env >> w) & 1) << j for j, w in enumerate(args))
                self.argument_env[child][state] |= bit
            if all(len({(env >> w) & 1 for w in args}) > 1 for args in self.knots):
                self.allowed_env |= bit
        self.lifts = []
        for child in range(self.nchild):
            table = [0] * 256
            for mask in range(1, 256):
                low = mask & -mask
                table[mask] = table[mask ^ low] | self.argument_env[child][low.bit_length() - 1]
            self.lifts.append(table)
        self.generic = {self.empty: 0}
        self.generic_cap = -1
        self.generic_rounds = []
        self._ray_layers = {}
        self._intersect = lru_cache(maxsize=100_000)(self._intersect_raw)
        self._project = lru_cache(maxsize=30_000)(self._project_raw)
        self._local = {}

    def checkpoint(self):
        self.operations += 1
        if self.operations % 256 == 0 and self.deadline is not None and time.monotonic() >= self.deadline:
            raise TimeoutError("per-family foreground deadline reached")

    @staticmethod
    def _intersect_raw(left, right):
        f, g = left
        ff, gg = right
        full = tuple(sorted({a & b for a in f for b in ff}))
        forgot = tuple(sorted({a & b for a in g for b in ff} | {a & b for a in f for b in gg}))
        return full, forgot

    def _project_raw(self, env_summary):
        def project(envs):
            return sum(1 << state for state, support in enumerate(self.port_env) if support & envs)
        f, g = env_summary
        return tuple(sorted({project(x) for x in f})), tuple(sorted({project(x) for x in g}))

    def _lift(self, summary, child):
        f, g = summary
        table = self.lifts[child]
        return tuple(sorted({table[x] for x in f})), tuple(sorted({table[x] for x in g}))

    def local_options(self, kind):
        """(environment summary, cost), preserving local alpha pairs until union."""
        if kind in self._local:
            return self._local[kind]
        pool = tuple(range(self.v)) if kind == "root" else tuple(range(3, self.v))
        options = []
        for chosen in _subsets(pool):
            if kind == "root" and not any(w < 3 for w in chosen):
                continue
            if kind == "target" and not chosen:
                continue
            full = []
            for alpha in range(1 << len(chosen)):
                mask = self.allowed_env
                for i, w in enumerate(chosen):
                    mask &= self.literal_env[w][(alpha >> i) & 1]
                full.append(mask)
            forgotten = {full[a] | full[a | (1 << i)] for i in range(len(chosen))
                         for a in range(1 << len(chosen)) if not (a >> i) & 1}
            f = tuple(sorted(set(full)))
            g = f if self.mutant else tuple(sorted(forgotten))
            options.append(((f, g), len(chosen)))
        self._local[kind] = options
        return options

    def _admissible(self, summary, cost, kind):
        f, g = summary
        if 0 in g:
            return False
        if kind != "root" and 0 in f:
            return False
        if kind == "generic" and cost > 0 and f == (self.g,):
            return False
        return True

    def combine(self, children, cap, *, kind="generic"):
        """Min-plus composition, deduplicating only equal exact summaries."""
        if len(children) != self.nchild:
            raise ValueError("one child table per ordered SELF occurrence is required")
        layer = {}
        for summary, cost in self.local_options(kind):
            if cost <= cap and 0 not in summary[1] and (kind == "root" or 0 not in summary[0]):
                layer[summary] = min(cost, layer.get(summary, cap + 1))
        for child, table in enumerate(children):
            lifted = [(self._lift(summary, child), cost) for summary, cost in table.items() if cost <= cap]
            next_layer = {}
            for left, c0 in layer.items():
                for right, c1 in lifted:
                    self.checkpoint()
                    cost = c0 + c1
                    if cost > cap:
                        continue
                    result = self._intersect(left, right)
                    if 0 in result[1] or (kind != "root" and 0 in result[0]):
                        continue
                    if cost < next_layer.get(result, cap + 1):
                        next_layer[result] = cost
            layer = next_layer
            if not layer:
                break
        result = {}
        for env_summary, cost in layer.items():
            summary = self._project(env_summary)
            if self.mutant:
                summary = summary[0], summary[0]
            if self._admissible(summary, cost, kind) and cost < result.get(summary, cap + 1):
                result[summary] = cost
        return result

    def generic_fixed_point(self, cap):
        """Kleene iteration from the empty choice, retaining least costs only."""
        if cap < 0:
            return {}
        if cap <= self.generic_cap:
            return {summary: cost for summary, cost in self.generic.items() if cost <= cap}
        table = {summary: cost for summary, cost in self.generic.items() if cost <= cap}
        rounds = 0
        while True:
            self.checkpoint()
            generated = self.combine([table] * self.nchild, cap)
            next_table = dict(table)
            for summary, cost in generated.items():
                if cost < next_table.get(summary, cap + 1):
                    next_table[summary] = cost
            rounds += 1
            if next_table == table:
                self.generic, self.generic_cap = table, cap
                self.generic_rounds.append({"cap": cap, "rounds": rounds, "size": len(table)})
                return table
            table = next_table

    def least(self, s, ray_bound, *, ray_only=False):
        if s < 1:
            raise ValueError("s must be positive")
        generic = {self.empty: 0} if ray_only else self.generic_fixed_point(ray_bound - 2)
        # Each child of C_s may carry choices, including its first SELF child.
        key = ray_only, ray_bound
        layers = self._ray_layers.setdefault(key, [])
        if not layers:
            layers.append(self.combine([generic] * self.nchild, ray_bound - 1, kind="target"))
        while len(layers) < s:
            layers.append(self.combine([layers[-1]] + [generic] * (self.nchild - 1), ray_bound - 1, kind="middle"))
        ray = layers[s - 1]
        root = self.combine([ray] + [generic] * (self.nchild - 1), ray_bound, kind="root")
        costs = [cost for (f, g), cost in root.items() if 0 in f and 0 not in g]
        return min(costs) if costs else None

    def combine_counts(self, children, cap, *, kind="generic"):
        """Validation only: count creator-labeled sets, not their assignments.

        Entries are (summary, exact cost) -> multiplicity. Recompute for each
        finite height; never accumulate counts from earlier heights.
        """
        layer = Counter()
        for summary, cost in self.local_options(kind):
            if cost <= cap and 0 not in summary[1] and (kind == "root" or 0 not in summary[0]):
                layer[summary, cost] += 1
        for child, table in enumerate(children):
            lifted = [(self._lift(summary, child), cost, count) for (summary, cost), count in table.items()]
            next_layer = Counter()
            for (left, c0), n0 in layer.items():
                for right, c1, n1 in lifted:
                    self.checkpoint()
                    cost = c0 + c1
                    if cost > cap:
                        continue
                    result = self._intersect(left, right)
                    if 0 in result[1] or (kind != "root" and 0 in result[0]):
                        continue
                    next_layer[result, cost] += n0 * n1
            layer = next_layer
        result = Counter()
        for (env_summary, cost), count in layer.items():
            summary = self._project(env_summary)
            if self.mutant:
                summary = summary[0], summary[0]
            if self._admissible(summary, cost, kind):
                result[summary, cost] += count
        return result

    def finite_counts(self, s, h, cap, *, convention):
        """Explicit alternative diagnostics; no silent choice of height wording.

        'uniform_depth' builds copies through depth s+h, inclusive.
        'common_side_height' uses the same h-level side table at every C_j.
        The requested comparison is blocked until this conflict is resolved.
        """
        if convention not in ("uniform_depth", "common_side_height"):
            raise ValueError("an explicit height convention is required")
        tables = [Counter({(self.empty, 0): 1})]
        max_height = s + h if convention == "uniform_depth" else h
        for _ in range(max_height):
            tables.append(self.combine_counts([tables[-1]] * self.nchild, cap - 2))
        def side(j):
            return tables[s + h - j] if convention == "uniform_depth" else tables[h]
        ray = self.combine_counts([side(s)] * self.nchild, cap - 1, kind="target")
        for j in range(s - 1, 0, -1):
            ray = self.combine_counts([ray] + [side(j)] * (self.nchild - 1), cap - 1, kind="middle")
        root = self.combine_counts([ray] + [side(0)] * (self.nchild - 1), cap, kind="root")
        counts = Counter()
        for ((f, g), cost), count in root.items():
            if 0 in f and 0 not in g:
                counts[cost] += count
        return {size: counts[size] for size in range(1, cap + 1)}


def bd_ray_values(defs, smax=12):
    """Expand only BD's explicitly detected affine repeat; no extrapolation fit."""
    result = bd_module().run_family(defs, smax=smax)
    values = list(result["L"])
    repeat = result.get("rate")
    while len(values) < smax and repeat:
        previous = len(values) - repeat["period"]
        if previous < 0:
            break
        values.append(values[previous] + repeat["gain"])
    return [None if x >= bd_module().INF else int(x) for x in values[:smax]], result

