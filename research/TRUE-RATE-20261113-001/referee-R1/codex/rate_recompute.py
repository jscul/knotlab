"""Independent minimum-bond summary calculation for three small closed rules.

For a finite marked set W, a summary (F,H) records the set of possible port
relations for assignments to W (F), and for assignments with exactly one mark
forgotten (H).  Join independent marked sets by intersecting their relations;
H is the union of the two choices of which side forgot a mark.  A zero in H
can never be repaired by adding constraints and is safely discarded.  Keep
relations on the *whole environment* until all children are joined.  Generic
summaries mark only distinctions created inside their subtree, never ports.

Closing from the empty marked set covers every finite support in the infinite
unfolding.  No size/cost cap is used.  The ray graph retains a target mark via
its base states; the root acceptance requires a selected original top port.
"""
from __future__ import annotations

import itertools
import hashlib
import json
import resource
import signal
import time
from collections import deque
from fractions import Fraction
from functools import lru_cache

from certificate_audit import HERE, ROOT, Rule, pack

resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))


def canonical(f, h):
    return tuple(sorted(set(f))), tuple(sorted(set(h)))


@lru_cache(maxsize=100000)
def join(a, b):
    f = {x & y for x in a[0] for y in b[0]}
    h = {x & y for x in a[1] for y in b[0]}
    h.update(x & y for x in a[0] for y in b[1])
    if 0 in h:
        return None
    return canonical(f, h)


def relax(table, state, cost):
    if state is not None and cost < table.get(state, 10**30):
        table[state] = cost


class Summaries:
    def __init__(self, defs):
        self.rule = Rule(defs)
        self.g, _ = self.rule.bottomless()
        self.full = (1 << (1 << self.rule.nenv)) - 1
        self.proj_cache = {}
        self.lift_cache = {}
        self.own_cache = {}
        self.project_mask = {}

    def own(self, slots):
        slots = tuple(slots)
        if slots in self.own_cache:
            return self.own_cache[slots]

        def masks(kept):
            answer = []
            for alpha in range(1 << len(kept)):
                bitmask = 0
                for x in self.rule.knot_ok:
                    if all(((x >> slot) & 1) == ((alpha >> j) & 1)
                           for j, slot in enumerate(kept)):
                        bitmask |= 1 << x
                answer.append(bitmask)
            return answer

        state = canonical(masks(slots), itertools.chain.from_iterable(
            masks(slots[:j] + slots[j + 1:]) for j in range(len(slots))))
        self.own_cache[slots] = state
        return state

    def lift(self, state, args):
        key = state, tuple(args)
        if key not in self.lift_cache:
            def convert(mask):
                return sum(1 << x for x in range(1 << self.rule.nenv)
                           if (mask >> pack(x, args)) & 1)
            self.lift_cache[key] = canonical(map(convert, state[0]), map(convert, state[1]))
        return self.lift_cache[key]

    def project(self, state):
        if state not in self.proj_cache:
            def convert(mask):
                if mask not in self.project_mask:
                    self.project_mask[mask] = sum(1 << p for p in range(8)
                                                  if any(mask >> x & 1
                                                         for x in range(p, 1 << self.rule.nenv, 8)))
                return self.project_mask[mask]
            self.proj_cache[state] = canonical(map(convert, state[0]), map(convert, state[1]))
        return self.proj_cache[state]

    def subsets(self, mode):
        loc = list(range(3, self.rule.nenv))
        pool = list(range(self.rule.nenv)) if mode == "root" else loc
        for size in range(len(pool) + 1):
            for w in itertools.combinations(pool, size):
                if mode == "base" and not w:
                    continue
                if mode == "root" and not any(v < 3 for v in w):
                    continue
                yield w

    def combine(self, table, mode, ray_state=None):
        current = {}
        for chosen in self.subsets(mode):
            state = self.own(chosen)
            if 0 not in state[1]:
                relax(current, state, len(chosen))
        for j, args in enumerate(self.rule.children):
            options = [(self.lift(ray_state, args), 0)] if ray_state is not None and j == 0 else [
                (self.lift(state, args), cost) for state, cost in table.items()]
            nxt = {}
            for state, cost in current.items():
                for other, extra in options:
                    relax(nxt, join(state, other), cost + extra)
            current = nxt
        result = {}
        for state, cost in current.items():
            relax(result, self.project(state), cost)
        return result

    def generic(self):
        table = {((self.g,), ()): 0}
        rounds = []
        while True:
            update = self.combine(table, "generic")
            changed = 0
            for state, cost in update.items():
                if cost < table.get(state, 10**30):
                    table[state] = cost
                    changed += 1
            rounds.append({"size": len(table), "cost_updates": changed})
            if not changed:
                return table, rounds


def components(adj):
    """Tarjan, independently written; adj is a list of {successor:cost}."""
    serial = 0
    numbering, low, stack, active, out = {}, {}, [], set(), []

    def visit(v):
        nonlocal serial
        numbering[v] = low[v] = serial
        serial += 1
        stack.append(v)
        active.add(v)
        for w in adj[v]:
            if w not in numbering:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in active:
                low[v] = min(low[v], numbering[w])
        if low[v] == numbering[v]:
            comp = []
            while True:
                w = stack.pop()
                active.remove(w)
                comp.append(w)
                if w == v:
                    break
            out.append(comp)

    for v in range(len(adj)):
        if v not in numbering:
            visit(v)
    return out


def cycle_mean(adj, comp):
    n = len(comp)
    ix = {v: j for j, v in enumerate(comp)}
    arcs = [(ix[v], ix[w], c) for v in comp for w, c in adj[v].items() if w in ix]
    if n == 1 and not arcs:
        return None
    infinity = 10**30
    # Virtual source with zero cost to every node.
    dp = [[0] * n]
    for _ in range(n):
        row = [infinity] * n
        for v, w, cost in arcs:
            row[w] = min(row[w], dp[-1][v] + cost)
        dp.append(row)
    return min(max(Fraction(dp[n][v] - dp[k][v], n - k)
                   for k in range(n) if dp[k][v] < infinity)
               for v in range(n) if dp[n][v] < infinity)


def controls():
    assert cycle_mean([{0: 2}], [0]) == 2
    assert cycle_mean([{1: 0}, {0: 1}], [0, 1]) == Fraction(1, 2)
    assert cycle_mean([{0: 0}], [0]) == 0
    assert cycle_mean([{}], [0]) is None
    # Direct marked-assignment enumeration checks an environment-level join.
    engine = Summaries([[3, 2, [["K", [0, 3, 4]], ["SELF", [0, 1, 2]]]]])
    assert join(engine.own((0,)), engine.own((3, 4))) == engine.own((0, 3, 4))
    constrained = engine.project(engine.own((0, 3, 4)))
    assert 0 in constrained[0] and 0 not in constrained[1]
    pair = engine.project(engine.own((0, 3)))
    assert 0 not in pair[0]
    return {"cycle_mean_controls": "positive, fractional, zero, acyclic passed",
            "direct_assignment_join_control": True,
            "NAE_three_mark_accepts_pair_rejects": True}


def run(idx, defs):
    start = time.monotonic()
    engine = Summaries(defs)
    table, rounds = engine.generic()
    base_by_state = engine.combine(table, "base")
    states = list(base_by_state)
    ids = {state: j for j, state in enumerate(states)}
    adj = []
    accept = {}
    cursor = 0
    while cursor < len(states):
        state = states[cursor]
        candidates = engine.combine(table, "generic", state)
        edges = {}
        for to, cost in candidates.items():
            if to not in ids:
                ids[to] = len(states)
                states.append(to)
            edges[ids[to]] = cost
        adj.append(edges)
        candidates = engine.combine(table, "root", state)
        costs = [cost for out, cost in candidates.items() if 0 in out[0] and 0 not in out[1]]
        if costs:
            accept[cursor] = min(costs)
        cursor += 1

    reverse = [[] for _ in states]
    for v, edges in enumerate(adj):
        for w in edges:
            reverse[w].append(v)
    live = set(accept)
    work = deque(live)
    while work:
        for v in reverse[work.popleft()]:
            if v not in live:
                live.add(v)
                work.append(v)
    trimmed = [{w: c for w, c in edges.items() if w in live} if v in live else {}
               for v, edges in enumerate(adj)]
    means = [cycle_mean(trimmed, comp) for comp in components(trimmed)
             if all(v in live for v in comp)]
    means = [m for m in means if m is not None]
    rate = min(means) if means else None
    layer = {ids[s]: cost for s, cost in base_by_state.items()}
    lengths = []
    seen_vectors = {}
    vector_repeat = None
    for depth in range(1, 31):
        possible = [cost + accept[v] for v, cost in layer.items() if v in accept]
        lengths.append(min(possible) if possible else None)
        retained = {v: cost for v, cost in layer.items() if v in live}
        if retained:
            offset = min(retained.values())
            key = tuple((v, retained[v] - offset) for v in sorted(retained))
            if key in seen_vectors and vector_repeat is None:
                earlier_depth, earlier_offset = seen_vectors[key]
                vector_repeat = {"from_depth": earlier_depth,
                                 "repeated_at_depth": depth,
                                 "period": depth - earlier_depth,
                                 "gain": offset - earlier_offset,
                                 "normalized_live_cost_vector": key,
                                 "argument": "The min-plus transition is deterministic and additively homogeneous. An exact normalized-vector repeat proves the same period/gain for every later layer and its accepted minimum."}
            seen_vectors.setdefault(key, (depth, offset))
        nxt = {}
        for v, cost in layer.items():
            for w, extra in adj[v].items():
                nxt[w] = min(nxt.get(w, 10**30), cost + extra)
        layer = nxt
    result = {"idx": idx, "uncapped_table_closed": True, "generic_states": len(table),
              "closure_rounds": rounds, "reachable_nodes": len(states), "trimmed_nodes": len(live),
              "cyclic_component_means": [str(m) for m in means],
              "lambda_true": str(rate) if rate is not None else None,
              "exact_cost_vector_repeat": vector_repeat,
              "L_depths_1_to_30": lengths, "seconds": time.monotonic() - start,
              "generic_table": [{"F": s[0], "H": s[1], "cost": c} for s, c in table.items()],
              "ray_graph": [{"id": v, "F": s[0], "H": s[1],
                             "base_cost": base_by_state.get(s), "accept_cost": accept.get(v),
                             "successors": adj[v]} for v, s in enumerate(states)]}
    join.cache_clear()
    return result


def main():
    signal.alarm(600)
    inventory = json.loads((HERE / "family_inventory.json").read_text())
    families = {r["idx"]: r["defs"] for r in inventory}
    result = {"method": __doc__, "controls": controls(), "rows": []}
    for idx in (105, 429, 874):
        row = run(idx, families[idx])
        result["rows"].append(row)
        (HERE / "rate_recompute.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({k: row[k] for k in ("idx", "generic_states", "reachable_nodes", "trimmed_nodes", "lambda_true", "seconds")}), flush=True)
    # Read the study/reference numbers only after finishing the fresh runs.
    data = ROOT / "artifacts"
    true_file = data / "TRUE-RATE-20261113-001A/TRUE-RATE-20261113-001A-E001_true_rates/true_rates_all.jsonl"
    ray_file = data / "PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/rates_all.jsonl"
    bond_file = data / "TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/true_rates_all.jsonl"
    true = {r["idx"]: r for r in map(json.loads, true_file.open())}
    ray = {r["idx"]: r for r in map(json.loads, ray_file.open())}
    bond = {r["idx"]: r for r in map(json.loads, bond_file.open())}
    comparisons = []
    for row in result["rows"]:
        idx = row["idx"]
        repeat = row["exact_cost_vector_repeat"]
        assert repeat and Fraction(repeat["gain"], repeat["period"]) == Fraction(row["lambda_true"])
        cells = [(s, expected) for s, expected in enumerate(bond[idx]["L"], 1)
                 if expected is not None]
        lengths_ok = all(row["L_depths_1_to_30"][s - 1] == value for s, value in cells)
        rate_ok = Fraction(row["lambda_true"]) == Fraction(true[idx]["lambda_true"]) == Fraction(ray[idx]["lambda"])
        assert lengths_ok and rate_ok
        comparisons.append({"idx": idx, "study_lambda_true": true[idx]["lambda_true"],
                            "proved_ray_rate": ray[idx]["lambda"],
                            "finite_reference_cells_checked": len(cells),
                            "all_finite_values_match": lengths_ok, "all_rates_match": rate_ok})
    closed = [r for r in true.values() if r.get("closed") and r.get("complete")]
    distribution = {}
    for r in closed:
        label = str(Fraction(r["lambda_true"]))
        distribution[label] = distribution.get(label, 0) + 1
    result.update({"reference_comparisons": comparisons,
                   "record_only_checks": {
                       "closed_complete_count": len(closed), "rate_distribution": distribution,
                       "all_24_rate_strings_equal_ray": all(Fraction(r["lambda_true"]) == Fraction(ray[r["idx"]]["lambda"]) for r in closed),
                       "all_24_unshortened_in_reached_reference": all(
                           all(a == b for a, b in zip(bond[r["idx"]]["L"], bond[r["idx"]]["L_ray"]) if a is not None and b is not None)
                           for r in closed)},
                   "inputs_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in (HERE / "family_inventory.json", true_file, ray_file, bond_file)},
                   "peak_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024})
    (HERE / "rate_recompute.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
