"""Independent exhaustive support/projection audit; no study-code imports.

Patterns are re-derived directly from the specification. The old referee's
address actions and word catalogue are the only inherited executable logic.
All support searches use exact SAT projections, testing every assignment
modulo global complement symmetry, and enumerate candidate supports by size.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import itertools as it
import json
import random
import time
from pathlib import Path

from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
OLD = ROOT / "research/ADDR-KNOTS-20261113-001/referee-R1/codex/fresh_patterns.py"
_spec = importlib.util.spec_from_file_location("old_referee_patterns", OLD)
old = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(old)


def freeze_key(key):
    return (key[0], tuple(key[1]), tuple(key[2]), tuple(key[3]), tuple(map(tuple, key[4])))


def placement_pattern(key, N):
    """Loop implementation, with append performed after the composed action."""
    catalogue = [(w, a) for w in old.words(key[0]) for a in (None, 0, 1)]
    triples = set()
    for n in range(N + 1):
        maps = old.state_actions(key, n)
        for placement in key[4]:
            terms = [catalogue[i] for i in placement]
            if any(n + (a is not None) > N for _, a in terms):
                continue
            for x in range(1 << n):
                image = []
                for word, a in terms:
                    y = x
                    for q in reversed(word):
                        y = maps[q][y]
                    target_n = n
                    if a is not None:
                        y = 2 * y + a
                        target_n += 1
                    image.append((1 << target_n) - 1 + y)
                if len(set(image)) == 3:
                    triples.add(tuple(sorted(image)))
    return sorted(triples)


def direct_pattern(key, N):
    """Second term implementation, using the old letterwise automaton."""
    catalogue = [(w, a) for w in old.words(key[0]) for a in (None, 0, 1)]
    found = set()
    for indices in key[4]:
        terms = [catalogue[t] for t in indices]
        for depth in range(N + 1):
            if any(a is not None for _, a in terms) and depth == N:
                continue
            for address in range(1 << depth):
                image = []
                for word, appended in terms:
                    y = address
                    for q in reversed(word):
                        y = old.direct_state(key, q, y, depth)
                    n = depth
                    if appended is not None:
                        y = (y << 1) | appended
                        n += 1
                    image.append((1 << n) - 1 + y)
                if len(set(image)) == 3:
                    found.add(tuple(sorted(image)))
    return sorted(found)


def clauses(triples):
    return [c for t in triples for c in ([v + 1 for v in t], [-v - 1 for v in t])]


def components(triples, nvars):
    parent = list(range(nvars))

    def root(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for triple in triples:
        r = root(triple[0])
        for v in triple[1:]:
            parent[root(v)] = r
    groups = {}
    for v in range(nvars):
        groups.setdefault(root(v), []).append(v)
    return list(groups.values())


class ProjectionOracle:
    def __init__(self, triples, nvars):
        self.solver = Solver(name="cadical195", bootstrap_with=clauses(triples))
        self.nvars = nvars
        self.calls = 0
        self.cache = {}
        self.alive = self.solver.solve()
        self.calls += 1

    def close(self):
        self.solver.delete()

    def missing(self, support):
        """Return a forbidden assignment, or None for a full projection."""
        support = tuple(sorted(support))
        if support in self.cache:
            return self.cache[support]
        if not support:
            result = None if self.alive else ()
            self.cache[support] = result
            return result
        # Each NAE model has its complement; first bit zero suffices.
        for tail in it.product((0, 1), repeat=len(support) - 1):
            bits = (0,) + tail
            assumptions = [v + 1 if b else -v - 1 for v, b in zip(support, bits)]
            self.calls += 1
            if not self.solver.solve(assumptions=assumptions):
                self.cache[support] = bits
                return bits
        self.cache[support] = None
        return None


def least_bond(triples, nvars, A, B, cap=4):
    """All crossing supports through cap; no heuristic pruning.

    A minimal non-full support is contained in one independent constraint
    component: a support spanning components has a non-full proper subset.
    Consequently product-component elimination is an exact reduction.
    """
    started = time.perf_counter()
    oracle = ProjectionOracle(triples, nvars)
    stats = {"candidate_supports": {}, "nonfull_nonminimal": 0, "cap": cap}
    if not oracle.alive:
        oracle.close()
        return {"L": "dead", "seconds": time.perf_counter() - started, **stats}
    A, B = set(A), set(B)
    relevant = [c for c in components(triples, nvars) if A.intersection(c) and B.intersection(c)]
    stats["relevant_components"] = [len(c) for c in relevant]
    if not relevant:
        oracle.close()
        return {"L": "none", "seconds": time.perf_counter() - started, **stats}
    for size in range(2, cap + 1):
        examined = 0
        for component in relevant:
            for support in it.combinations(component, size):
                if not A.intersection(support) or not B.intersection(support):
                    continue
                examined += 1
                missing = oracle.missing(support)
                if missing is None:
                    continue
                proper = [support[:j] + support[j + 1:] for j in range(size)]
                if any(oracle.missing(sub) is not None for sub in proper):
                    stats["nonfull_nonminimal"] += 1
                    continue
                stats["candidate_supports"][str(size)] = examined
                stats["sat_calls"] = oracle.calls
                result = {"L": size, "support": list(support), "forbidden": list(missing),
                          "proper_projections_full": True, "optimality_exhausted": True,
                          "seconds": time.perf_counter() - started, **stats}
                oracle.close()
                return result
        stats["candidate_supports"][str(size)] = examined
    stats["sat_calls"] = oracle.calls
    oracle.close()
    return {"L": f"> {cap}", "optimality_exhausted": True,
            "seconds": time.perf_counter() - started, **stats}


def enumerated_bonds(triples, nvars, A, B, cap=None):
    """Fully independent truth-table reference, used for small countermodels."""
    states = [bits for bits in it.product((0, 1), repeat=nvars)
              if all(len({bits[v] for v in t}) > 1 for t in triples)]
    if not states:
        return {"L": "dead", "states": 0}
    A, B = set(A), set(B)
    cap = cap or nvars
    full = {(): True}
    bonds = []
    for size in range(1, cap + 1):
        for support in it.combinations(range(nvars), size):
            values = {tuple(bits[v] for v in support) for bits in states}
            full[support] = len(values) == (1 << size)
            if not full[support] and all(full[support[:j] + support[j + 1:]] for j in range(size)):
                bonds.append(support)
    crossing = [s for s in bonds if A.intersection(s) and B.intersection(s)]
    return {"L": min(map(len, crossing)) if crossing else "none" if cap == nvars else f"> {cap}",
            "states": len(states), "all_bonds": list(map(list, bonds)),
            "crossing_bonds": list(map(list, crossing))}


def population_records():
    path = ROOT / "artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz"
    with gzip.open(path, "rt") as f:
        return list(map(json.loads, f))


def label(record):
    if record["union"] == "dead":
        return "dead"
    ls = [r["L_N"] for r in record.get("levels", [])]
    if record["flags"]["no_join"]:
        return "no_join"
    if "none" in ls:
        return "no_bond"
    if all(isinstance(x, int) for x in ls):
        if ls == [3, 4, 5, 6]:
            return "chained"
        if len(set(ls)) == 1:
            return "direct"
        return "other"
    return "undecided"


def choose_cases(per_stratum=2):
    records = population_records()
    groups = {}
    for r in records:
        groups.setdefault(label(r), []).append(r)
    chosen = []
    rng = random.Random("independent-N4-support-audit-20261114")
    for group in sorted(groups):
        selected = rng.sample(groups[group], min(per_stratum, len(groups[group])))
        for record in selected:
            chosen.append({"source": "actual_registered_population", "stratum_N9": group,
                           "case": record["case"], "key": record["key"],
                           "classes": record["classes"], "study_N9_L": [r["L_N"] for r in record.get("levels", [])]})
    controls = [
        {"case": "plain_tree", "key": [1, [0], [0], [0], [[0, 1, 2]]]},
        {"case": "empty_placement", "key": [1, [0], [0], [0], []]},
        {"case": "duplicate_images", "key": [1, [0], [0], [0], [[0, 3, 6]]]},
    ]
    for r in controls:
        chosen.append({"source": "specified_control", "stratum_N9": "control", **r})
    return chosen


def countermodels():
    # R0 = NAE(a,b,c). The new knots force a != c, making R0 redundant.
    first = [(0, 1, 2)]
    added = [(0, 2, 3), (0, 2, 4), (0, 2, 5), (3, 4, 5)]
    monotone = {"nvars": 6, "A": [0], "B": [1], "initial": first,
                "added": added,
                "before": enumerated_bonds(first, 6, [0], [1]),
                "after": enumerated_bonds(first + added, 6, [0], [1])}
    # Two adjacent-level knots overlap in the two intermediate distinctions.
    # A middle unequal pair satisfies both independently of either endpoint.
    chain = [(0, 1, 2), (1, 2, 3)]
    adjacent = {"nvars": 4, "levels": [[0], [1, 2], [3]], "knots": chain,
                "result": enumerated_bonds(chain, 4, [0], [3])}
    return {"nonmonotone_under_constraint_addition": monotone,
            "connected_adjacent_level_chain_no_crossing_bond": adjacent}


def run_audit(output, cap=4, per_stratum=2, N=4, k0=2):
    cases = choose_cases(per_stratum)
    rows = []
    with output.open("w") as f:
        for case in cases:
            started = time.perf_counter()
            key = freeze_key(case["key"])
            triples = placement_pattern(key, N)
            assert triples == direct_pattern(key, N), case["case"]
            nvars = (1 << (N + 1)) - 1
            levels = []
            for s in range(1, N - k0 + 1):
                A = range((1 << k0) - 1, (1 << (k0 + 1)) - 1)
                B = range((1 << (k0 + s)) - 1, (1 << (k0 + s + 1)) - 1)
                result = least_bond(triples, nvars, A, B, cap)
                levels.append({"s": s, **result})
            row = {**case, "N": N, "k0": k0, "nvars": nvars,
                   "knot_count": len(triples), "pattern_sha256": hashlib.sha256(json.dumps(triples).encode()).hexdigest(),
                   "pattern_reconstructions_agree": True, "levels": levels,
                   "seconds": time.perf_counter() - started}
            rows.append(row)
            f.write(json.dumps(row, sort_keys=True) + "\n")
            f.flush()
            print(json.dumps({"case": case["case"], "stratum": case["stratum_N9"],
                              "knots": len(triples), "L": [x["L"] for x in levels],
                              "seconds": row["seconds"]}), flush=True)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "brute_results.jsonl")
    parser.add_argument("--cap", type=int, default=4)
    parser.add_argument("--per-stratum", type=int, default=2)
    parser.add_argument("--N", type=int, default=4)
    parser.add_argument("--k0", type=int, default=2)
    args = parser.parse_args()
    (HERE / "countermodels.json").write_text(json.dumps(countermodels(), indent=2) + "\n")
    run_audit(args.output, args.cap, args.per_stratum, args.N, args.k0)


if __name__ == "__main__":
    main()
