#!/usr/bin/env python3
"""Check CUTWIDTH-DEPTH-20261020-001B-P001: toggle width is cutwidth + 1 on graphs of degree at most 3.

Runs the proof's constructions as algorithms on every graph of the census
CUTWIDTH-DEPTH-20261020-001A-E001 (1,453 graphs), starting from optimal
toggle paths and from random toggle paths that also remove vertices:

1. Peak elimination: a toggle path whose steps cost at most k becomes a
   one-vertex-at-a-time path from the empty set to V whose visited cuts are all
   at most k - 1 and whose steps still cost at most k (connected graphs with
   at least 3 vertices).
2. Uncrossing (Fomin and Thilikos 2003, Lemma 1, after Bienstock and
   Seymour): repeatedly replace A_i by A_(i-1) union A_i when that lowers its
   cut, else A_(i-1) by A_(i-1) intersect A_i; the result is monotone, adds one
   vertex at a time, and keeps every cut at most k - 1. So cutwidth <= k - 1.
3. The monotone bound: along a cutwidth-optimal ordering, adding v with d
   earlier neighbours costs at most cutwidth + min(d, deg v - d), so at most
   cutwidth + floor(maxdegree / 2).

Together: cutwidth + 1 <= toggle width <= monotone toggle width <=
cutwidth + floor(maxdegree / 2), with equality cutwidth + 1 at maximum degree
at most 3. Controls: the single edge (2 vertices) escapes the lower bound;
skipping the uncrossing leaves a non-monotone sequence on some input; peak
elimination with k - 1 in place of k leaves a step costing more than k - 1 on
some input.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import json
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENSUS = ROOT / "artifacts/CUTWIDTH-DEPTH-20261020-001A/CUTWIDTH-DEPTH-20261020-001A-E001_monotone_census"


class Graph:
    def __init__(self, n, edges):
        self.n, self.edges = n, [tuple(e) for e in edges]
        self.stars = [frozenset(i for i, e in enumerate(self.edges) if v in e) for v in range(n)]
        self.degree = [len(s) for s in self.stars]
        self._cut = {}

    def cut(self, U):
        if U not in self._cut:
            self._cut[U] = frozenset(i for i, (a, b) in enumerate(self.edges) if (a in U) != (b in U))
        return self._cut[U]

    def step_cost(self, U, W):
        (v,) = tuple(U ^ W)
        return len(self.cut(U) | self.stars[v])


def toggled(U, W):
    diff = U ^ W
    assert len(diff) == 1, "a toggle path changes one vertex per step"
    return next(iter(diff))


def optimal_toggle_path(g, k):
    start, goal = frozenset(), frozenset(range(g.n))
    previous, todo = {start: None}, [start]
    while todo:
        U = todo.pop(0)
        if U == goal:
            path = [U]
            while previous[path[-1]] is not None:
                path.append(previous[path[-1]])
            return path[::-1]
        for v in range(g.n):
            W = U ^ {v}
            if W not in previous and len(g.cut(U) | g.stars[v]) <= k:
                previous[W] = U
                todo.append(W)
    return None


def random_toggle_path(g, k, rng, tries=200):
    """A random walk from the empty set to V with steps costing at most k, removing vertices now and then."""
    goal = frozenset(range(g.n))
    for _ in range(tries):
        path = [frozenset()]
        for _ in range(20 * g.n):
            U = path[-1]
            if U == goal:
                return path
            moves = [v for v in range(g.n) if len(g.cut(U) | g.stars[v]) <= k]
            adds = [v for v in moves if v not in U]
            removes = [v for v in moves if v in U]
            if not moves:
                break
            v = rng.choice(removes) if removes and (not adds or rng.random() < 0.3) else rng.choice(adds)
            path.append(U ^ {v})
    return None


def eliminate_peaks(g, path, k):
    path = list(path)
    while True:
        peak = next((t for t in range(1, len(path) - 1) if len(g.cut(path[t])) == k), None)
        if peak is None:
            return path
        before, U, after = path[peak - 1], path[peak], path[peak + 1]
        v, w = toggled(before, U), toggled(U, after)
        assert g.stars[v] <= g.cut(U) and g.stars[w] <= g.cut(U), "a peak's neighbouring toggles have all edges cut"
        if v == w:
            path = path[:peak] + path[peak + 2:]
        else:
            path = path[:peak] + [before ^ {w}] + path[peak + 1:]


def uncross(g, sequence):
    seq = list(sequence)
    rho = lambda A: len(g.cut(A))
    changed = True
    while changed:
        changed = False
        for i in range(1, len(seq)):
            a, b = seq[i - 1], seq[i]
            union = a | b
            if rho(union) < rho(b):
                seq[i] = union
                changed = True
            elif not a <= b:
                inter = a & b
                assert rho(inter) <= rho(a), "submodularity of the cut function"
                seq[i - 1] = inter
                changed = True
    return seq


def monotone_bound(g, order):
    cw = 0
    worst = 0
    U = frozenset()
    for v in order:
        d = sum(1 for e in g.stars[v] if e in g.cut(U))
        cost = len(g.cut(U) | g.stars[v])
        U = U | {v}
        cw = max(cw, len(g.cut(U)))
        worst = max(worst, cost - min(d, g.degree[v] - d))
    return cw, worst


def run() -> dict[str, object]:
    rows = [json.loads(line) for line in (CENSUS / "raw_rows.jsonl").read_text().splitlines()]
    graphs = [r for r in rows if r["part"] == "graph"]
    rng = random.Random(20261020)
    tally, failures = Counter(), []
    for r in graphs:
        g = Graph(r["vertices"], r["edges"])
        if g.n < 3:
            continue
        cw, tgw = r["cutwidth"], r["toggle_width"]
        inputs = [("optimal", tgw, optimal_toggle_path(g, tgw))]
        for k in (tgw, tgw + 1):
            path = random_toggle_path(g, k, rng)
            if path is not None:
                inputs.append(("random", k, path))
        for kind, k, path in inputs:
            assert path[0] == frozenset() and path[-1] == frozenset(range(g.n))
            assert max(g.step_cost(a, b) for a, b in zip(path, path[1:])) <= k
            tally[f"{kind}_paths"] += 1
            tally["paths_with_removals"] += any(len(b) < len(a) for a, b in zip(path, path[1:]))
            flat = eliminate_peaks(g, path, k)
            ok = (flat[0] == frozenset() and flat[-1] == frozenset(range(g.n))
                  and all(len(g.cut(U)) <= k - 1 for U in flat)
                  and all(len(a ^ b) == 1 and g.step_cost(a, b) <= k for a, b in zip(flat, flat[1:])))
            if not ok:
                failures.append(f"peak elimination n={g.n} {r['edges']} k={k}")
                continue
            mono = uncross(g, flat)
            ok = (mono[0] == frozenset() and mono[-1] == frozenset(range(g.n))
                  and all(a <= b and len(b - a) <= 1 for a, b in zip(mono, mono[1:]))
                  and all(len(g.cut(U)) <= k - 1 for U in mono))
            if not ok:
                failures.append(f"uncrossing n={g.n} {r['edges']} k={k}")
                continue
            tally["orderings_of_cutwidth_at_most_k_minus_1"] += 1
        bound_cw, worst = monotone_bound(g, r["order"])
        if bound_cw != cw or worst > cw:
            failures.append(f"monotone bound n={g.n} {r['edges']}")
        max_degree = max(g.degree)
        if not cw + 1 <= tgw <= r["monotone_toggle_width"] <= cw + max_degree // 2:
            failures.append(f"sandwich n={g.n} {r['edges']}")
        if max_degree <= 3:
            tally["degree_at_most_3"] += 1
            if not tgw == r["monotone_toggle_width"] == cw + 1:
                failures.append(f"equality at degree <= 3 n={g.n} {r['edges']}")
    # controls
    edge = Graph(2, [(0, 1)])
    single_edge = optimal_toggle_path(edge, 1)
    controls = {
        "single edge escapes the lower bound": single_edge is not None and max(
            edge.step_cost(a, b) for a, b in zip(single_edge, single_edge[1:])) == 1,
    }
    skipped, too_tight = False, False
    for r in graphs:
        g = Graph(r["vertices"], r["edges"])
        if g.n < 4:
            continue
        path = random_toggle_path(g, r["toggle_width"] + 1, rng)
        if path is None:
            continue
        flat = eliminate_peaks(g, path, r["toggle_width"] + 1)
        skipped |= any(not a <= b for a, b in zip(flat, flat[1:]))
        try:
            tight = eliminate_peaks(g, path, r["toggle_width"])
            too_tight |= any(g.step_cost(a, b) > r["toggle_width"] for a, b in zip(tight, tight[1:]))
        except AssertionError:
            too_tight = True
        if skipped and too_tight:
            break
    controls["without uncrossing some sequence is not monotone"] = skipped
    controls["peak elimination with k - 1 for k breaks a step bound"] = too_tight
    census = json.loads((CENSUS / "result.json").read_text())
    checks = {"tally": dict(tally), "controls": controls,
              "census_agrees": all(census["predictions"].values()) and census["signal"]}
    failures += [name for name, ok in controls.items() if not ok]
    if not checks["census_agrees"]:
        failures.append("census disagreement")
    return {"checks": checks, "failures": failures}


def main() -> int:
    outcome = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not outcome["failures"] else "failed",
        "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
        "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
        "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"],
        "checks": outcome["checks"], "failures": outcome["failures"][:30],
    }
    result = json.loads(json.dumps(result))
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if "--write" in sys.argv[1:]:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != result:
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    tally = outcome["checks"]["tally"]
    print(f"{result['status']}: {tally.get('orderings_of_cutwidth_at_most_k_minus_1', 0)} toggle paths turned into "
          f"orderings ({tally.get('paths_with_removals', 0)} with removals)" if result["status"] == "passed"
          else f"failed: {outcome['failures'][:10]}")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
