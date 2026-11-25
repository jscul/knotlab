"""Certify each projected relation in the raw, complete roster histories."""

from bisect import bisect_right
from collections import Counter, defaultdict
from dataclasses import dataclass
import gzip
import hashlib
import json

from projection import ExactSolver, Projection, own_relation


@dataclass(frozen=True)
class Stage:
    knots: int
    distinctions: int


@dataclass(frozen=True)
class History:
    supports: list[tuple[int, ...]]
    stages: list[Stage]


def read_history(path, expected_digest):
    digest = hashlib.sha256()
    supports = []
    stages = []
    old_distinctions = 0
    with gzip.open(path, "rb") as source:
        for t, line in enumerate(source):
            digest.update(line)
            row = json.loads(line)
            if row["round"] != t:
                raise ValueError(f"round {t} missing or out of order")
            fresh = set()
            for support in row["supports"]:
                if not support or len(set(support)) != len(support):
                    raise ValueError(f"invalid support for knot {len(supports)}")
                for d in support:
                    if type(d) is not int or d < 0:
                        raise ValueError(f"invalid distinction in round {t}: {d}")
                    if d >= old_distinctions:
                        fresh.add(d)
                supports.append(tuple(sorted(support)))
            knots = len(supports)
            distinctions = old_distinctions + len(fresh)
            if (knots, distinctions) != (row["knots"], row["distinctions"]):
                raise ValueError(f"support totals differ from claimed round {t}")
            if fresh and max(fresh) >= distinctions:
                raise ValueError(f"distinction names have a gap in round {t}")
            stages.append(Stage(knots, distinctions))
            old_distinctions = distinctions
    if not stages or not stages[0].knots:
        raise ValueError("missing nonempty start")
    if digest.hexdigest() != expected_digest:
        raise ValueError("support history digest mismatch")
    return History(supports, stages)


class LooseComponents:
    """Shared-distinction components with their currently loose counts."""

    def __init__(self, stage):
        self.parent = list(range(stage.knots))
        self.size = [1] * stage.knots
        self.loose = [0] * stage.knots
        self.owner = [-1] * stage.distinctions

    def root(self, u):
        while self.parent[u] != u:
            self.parent[u] = self.parent[self.parent[u]]
            u = self.parent[u]
        return u

    def attach(self, u, d):
        owner = self.owner[d]
        here = self.root(u)
        if owner == -1:
            self.owner[d] = u
            self.loose[here] += 1
            return True
        if owner == -2:
            return False
        self.owner[d] = -2
        there = self.root(owner)
        self.loose[there] -= 1
        if here != there:
            if self.size[here] < self.size[there]:
                here, there = there, here
            self.parent[there] = here
            self.size[here] += self.size[there]
            self.loose[here] += self.loose[there]
        return True


def birth_projections(history, law, evidence):
    """Find birth projections and check that every round preserves old states."""
    supports, stages = history.supports, history.stages
    components = LooseComponents(stages[-1])
    start = stages[0]
    with ExactSolver(supports[:start.knots], start.distinctions, law, "minisat22") as solver:
        results = [solver.projection(support) for support in supports[:start.knots]]
        evidence["birth_sat_calls"] += solver.calls
    if law == "nae" and all(not result.count() for result in results):
        return [Projection(len(support), "table") for support in supports], None
    for u in range(start.knots):
        for d in supports[u]:
            if not components.attach(u, d):
                return None, {"round": 0, "knot": u, "reason": "more_than_two_holders"}

    for t, (previous, stage) in enumerate(zip(stages, stages[1:]), start=1):
        spent = set()
        fresh = set()
        checks = []
        for u in range(previous.knots, stage.knots):
            support = supports[u]
            old_groups = defaultdict(int)
            fresh_mask = 0
            for i, d in enumerate(support):
                bit = 1 << i
                if d >= previous.distinctions:
                    if d in fresh:
                        return None, {"round": t, "knot": u, "reason": "nonprivate_fresh"}
                    fresh.add(d)
                    fresh_mask |= bit
                    continue
                owner = components.owner[d]
                if owner < 0 or d in spent:
                    return None, {"round": t, "knot": u, "reason": "input_not_sole_use_loose"}
                spent.add(d)
                old_groups[components.root(owner)] |= bit
            saturated = [
                mask for root, mask in old_groups.items()
                if mask.bit_count() == components.loose[root]
            ]
            evidence["saturated_component_uses"] += len(saturated)
            if not fresh_mask:
                if law != "parity" or sum(saturated) != (1 << len(support)) - 1:
                    return None, {"round": t, "knot": u, "reason": "unproved_old_extension"}
                evidence["implied_closing_births"] += 1
            checks.append((u, saturated))
        needs_sat = law == "nae" and any(saturated for _, saturated in checks)
        if needs_sat:
            with ExactSolver(supports[:stage.knots], stage.distinctions, law, "minisat22") as solver:
                for u, saturated in checks:
                    if saturated:
                        evidence["saturated_nae_sat_targets"] += 1
                        results.append(solver.projection(supports[u]))
                    else:
                        results.append(own_relation(len(supports[u]), law))
                evidence["birth_sat_calls"] += solver.calls
        else:
            for u, saturated in checks:
                width = len(supports[u])
                if law == "parity" and saturated:
                    remaining = ((1 << width) - 1) ^ sum(saturated)
                    groups = saturated + ([remaining] if remaining else [])
                    results.append(Projection(width, "even_groups", tuple(sorted(groups))))
                else:
                    results.append(own_relation(width, law))
        for u in range(previous.knots, stage.knots):
            for d in supports[u]:
                if not components.attach(u, d):
                    raise AssertionError("validated sole-use inputs acquired a third holder")
    return results, None


def holders_of(supports, distinctions):
    holders = [[] for _ in range(distinctions)]
    for u, support in enumerate(supports):
        for d in support:
            holders[d].append(u)
    return holders


def nae_unsafe(supports, holders):
    """Find targets for which the whole-stage extension criterion is unavailable."""
    if any(len(support) < 3 for support in supports) or any(len(h) > 2 for h in holders):
        return set(range(len(supports)))
    shared = Counter(tuple(h) for h in holders if len(h) == 2)
    unsafe = set()
    for (a, b), count in shared.items():
        if len(supports[b]) - count < 2:
            unsafe.add(a)
        if len(supports[a]) - count < 2:
            unsafe.add(b)
    return unsafe


def separating_intervals(graph):
    """Child intervals separated by deleting each vertex of an undirected graph."""
    n = len(graph)
    entered = [-1] * n
    low = [-1] * n
    separating = [[] for _ in range(n)]
    time = 0
    for root in range(n):
        if entered[root] >= 0:
            continue
        entered[root] = low[root] = time
        time += 1
        stack = [(root, -1, iter(graph[root]))]
        while stack:
            u, arrived_on, neighbors = stack[-1]
            item = next(neighbors, None)
            if item is None:
                stack.pop()
                if stack:
                    parent = stack[-1][0]
                    if low[u] >= entered[parent]:
                        separating[parent].append((entered[u], time))
                    low[parent] = min(low[parent], low[u])
                continue
            v, edge = item
            if edge == arrived_on:
                continue
            if entered[v] >= 0:
                low[u] = min(low[u], entered[v])
                continue
            entered[v] = low[v] = time
            time += 1
            stack.append((v, edge, iter(graph[v])))
        if len(separating[root]) <= 1:
            separating[root].clear()
    return entered, separating


def parity_projections(supports, holders, targets):
    outside = len(supports)
    graph = [[] for _ in range(outside + 1)]
    for d, h in enumerate(holders):
        u = h[0]
        v = h[1] if len(h) == 2 else outside
        graph[u].append((v, d))
        graph[v].append((u, d))
    entered, separating = separating_intervals(graph)
    results = {}
    for u in targets:
        support = supports[u]
        width = len(support)
        intervals = separating[u]
        if not intervals:
            results[u] = own_relation(width, "parity")
            continue
        starts = [start for start, _ in intervals]
        groups = defaultdict(int)
        for i, (v, _) in enumerate(graph[u]):
            group = bisect_right(starts, entered[v]) - 1
            if group >= 0 and entered[v] >= intervals[group][1]:
                group = -1
            groups[group] |= 1 << i
        # Distinctions are appended to graph[u] in sorted support order.
        results[u] = Projection(width, "even_groups", tuple(sorted(groups.values())))
    return results


def exact_targets(supports, distinctions, law, targets, backend, evidence, calls_key):
    if not targets:
        return {}
    with ExactSolver(supports, distinctions, law, backend) as solver:
        results = {u: solver.projection(supports[u]) for u in targets}
        evidence[calls_key] += solver.calls
    return results


def whole_stage(history, t, law, targets, evidence):
    """Compute exact whole-stage projections without birth or freshness."""
    stage = history.stages[t]
    supports = history.supports[:stage.knots]
    holders = holders_of(supports, stage.distinctions)
    if law == "parity" and all(len(h) <= 2 for h in holders):
        evidence["direct_cut_targets"] += len(targets)
        return parity_projections(supports, holders, targets)
    unsafe = targets
    results = {}
    if law == "nae":
        unsafe = set(targets) & nae_unsafe(supports, holders)
        results = {
            u: own_relation(len(supports[u]), law) for u in targets if u not in unsafe
        }
        evidence["direct_degree_targets"] += len(results)
    evidence["direct_sat_targets"] += len(unsafe)
    results.update(exact_targets(
        supports, stage.distinctions, law, unsafe, "cadical195", evidence, "direct_sat_calls"
    ))
    return results


def certify_history(history, law):
    """Compare exact relations from two methods and account for every stage."""
    evidence = Counter()
    birth, birth_problem = birth_projections(history, law, evidence)
    final_round = len(history.stages) - 1
    final = whole_stage(history, final_round, law, range(history.stages[-1].knots), evidence)
    # Every earlier projection contains the terminal projection and is
    # contained in the support's own relation. Equality closes both bounds.
    changing = [
        u for u, projection in final.items()
        if not projection.same_relation(own_relation(len(history.supports[u]), law))
    ]
    counts = Counter()
    reports = []
    failures = []
    covered = 0
    for t, stage in enumerate(history.stages):
        older = [u for u in changing if u < stage.knots]
        if t == final_round:
            stage_overrides = {u: final[u] for u in older}
        else:
            stage_overrides = whole_stage(history, t, law, older, evidence) if older else {}
        if birth is None:
            # When preservation is unavailable, the second solver applies
            # the exact quantified definition at each reported stage.
            reference = exact_targets(
                history.supports[:stage.knots], stage.distinctions, law, range(stage.knots),
                "minisat22", evidence, "birth_sat_calls",
            )
            compare = range(stage.knots)
        else:
            reference = birth
            compare = list(range(covered, stage.knots)) + [u for u in older if u < covered]

        disagreements = []
        for u in compare:
            result = stage_overrides.get(u, final[u])
            if not result.same_relation(reference[u]):
                disagreements.append({
                    "knot": u, "direct": result.spec(), "independent": reference[u].spec(),
                })
        if disagreements:
            raise ValueError(f"exact relation disagreement in round {t}: {disagreements[:3]}")

        for u in range(covered, stage.knots):
            counts[final[u].canonical_form()] += 1
        covered = stage.knots
        stage_counts = counts.copy()
        for u, override in stage_overrides.items():
            stage_counts[final[u].canonical_form()] -= 1
            stage_counts[override.canonical_form()] += 1

        failed = 0
        for projection, n in stage_counts.items():
            if n and not projection.report()["is_knot"]:
                failed += n
        if failed:
            for u in range(stage.knots):
                projection = stage_overrides.get(u, final[u])
                verdict = projection.report()
                if not verdict["is_knot"]:
                    failures.append({
                        "round": t, "knot": u, "support": history.supports[u],
                        "projection": projection.spec(), **verdict,
                    })
        reports.append({
            "round": t,
            "knots": stage.knots,
            "distinctions": stage.distinctions,
            "passed": stage.knots - failed,
            "failed": failed,
            "unclassified": 0,
            "independent_agreements": stage.knots,
            "relations": [
                {"projection": projection.spec(), "knots": n, **projection.report()}
                for projection, n in stage_counts.items() if n
            ],
        })
    return {
        "stages": reports,
        "failure_details": failures,
        "birth_method_fallback": birth_problem,
        "evidence": dict(evidence),
    }
