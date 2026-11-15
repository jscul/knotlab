"""Fresh exact crossing-support audit; no prohibited study-code imports."""
from __future__ import annotations

import argparse
import hashlib
import itertools as it
import json
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
REFEREE = ROOT / "research/LEVEL-REACH-20261114-001/referee-R1/codex"
sys.path.insert(0, str(REFEREE))
import fresh_pattern as pattern
import fresh_search
from pysat.solvers import Solver


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def crossing_supports(nvars, A, B, size):
    """Every crossing support once: A,B,C partition the variable set."""
    A, B = tuple(sorted(A)), tuple(sorted(B))
    assert not set(A).intersection(B)
    C = tuple(v for v in range(nvars) if v not in set(A) | set(B))
    for na in range(1, min(size - 1, len(A)) + 1):
        for nb in range(1, min(size - na, len(B)) + 1):
            nc = size - na - nb
            if nc > len(C):
                continue
            for aa in it.combinations(A, na):
                for bb in it.combinations(B, nb):
                    for cc in it.combinations(C, nc):
                        yield tuple(sorted(aa + bb + cc))


class Projections:
    def __init__(self, knots, nvars):
        self.knots = knots
        self.nvars = nvars
        self.solver = Solver(name="cadical195", bootstrap_with=pattern.cnf(knots))
        self.cache = {}
        self.calls = 1
        self.alive = self.solver.solve()

    def missing(self, support):
        support = tuple(sorted(support))
        if support in self.cache:
            return self.cache[support]
        result = None
        if not support:
            result = None if self.alive else ()
        else:
            # Global complement symmetry makes the first value zero WLOG.
            for tail in it.product((0, 1), repeat=len(support) - 1):
                bits = (0,) + tail
                self.calls += 1
                if not self.solver.solve(assumptions=[v+1 if b else -v-1
                                                      for v, b in zip(support, bits)]):
                    result = bits
                    break
        self.cache[support] = result
        return result

    def certificate(self, support, forbidden):
        """Retain all maximal proper assignments and checked extensions."""
        rows = []
        for removed in support:
            subset = tuple(v for v in support if v != removed)
            for bits in it.product((0, 1), repeat=len(subset)):
                assumptions = [v+1 if b else -v-1 for v, b in zip(subset, bits)]
                assert self.solver.solve(assumptions=assumptions)
                values = [0] * self.nvars
                for lit in self.solver.get_model():
                    if abs(lit) <= self.nvars:
                        values[abs(lit)-1] = int(lit > 0)
                assert all(len({values[v] for v in row}) == 2 for row in self.knots)
                assert all(values[v] == b for v, b in zip(subset, bits))
                rows.append({"removed": removed, "support": subset, "assignment": bits,
                             "model": values})
        assumptions = [v+1 if b else -v-1 for v, b in zip(support, forbidden)]
        independent = Solver(name="glucose4", bootstrap_with=pattern.cnf(self.knots))
        try:
            assert not independent.solve(assumptions=assumptions)
        finally:
            independent.delete()
        return {"support": support, "forbidden_assignment": forbidden,
                "forbidden_independent_solver": "glucose4: UNSAT",
                "maximal_proper_projection_models": rows,
                "all_models_directly_evaluated": True}


def least_bond(knots, nvars, A, B, cap):
    started = time.perf_counter()
    oracle = Projections(knots, nvars)
    stats = {"enumerated": {}, "native_nonminimal_skips": {}, "exact": True,
             "exhausted_sizes": [], "cap": cap}
    native = set(map(tuple, knots))
    try:
        if not oracle.alive:
            return {"L": "dead", **stats}
        for size in range(2, cap + 1):
            examined = skips = 0
            for support in crossing_supports(nvars, A, B, size):
                examined += 1
                if size > 3 and any(subset in native for subset in it.combinations(support, 3)):
                    skips += 1
                    continue
                missing = oracle.missing(support)
                if missing is None:
                    continue
                if any(oracle.missing(support[:j]+support[j+1:]) is not None
                       for j in range(size)):
                    continue
                stats["enumerated"][size] = examined
                stats["native_nonminimal_skips"][size] = skips
                return {"L": size, "certificate": oracle.certificate(support, missing),
                        "seconds": time.perf_counter()-started, "sat_calls": oracle.calls,
                        "cached_projections": len(oracle.cache), **stats}
            stats["enumerated"][size] = examined
            stats["native_nonminimal_skips"][size] = skips
            stats["exhausted_sizes"].append(size)
        return {"L": f"> {cap}", "seconds": time.perf_counter()-started,
                "sat_calls": oracle.calls, **stats}
    finally:
        oracle.solver.delete()


def actions(key, word, n):
    values = list(range(1 << n))
    maps = pattern.previous.state_actions(key, n)
    for q in reversed(word):
        values = [maps[q][v] for v in values]
    return values


def address(v):
    n = pattern.level(v)
    return "" if n == 0 else format(v - ((1 << n)-1), f"0{n}b")


def sibling_audit(key, N):
    """Actual sibling pairs share a tree-placement upper member, not a prefix."""
    catalog = pattern.previous.words(key[0])
    tree_placements = [p for p in key[4] if sorted(t % 3 for t in p) == [0, 1, 2]]
    assert len(tree_placements) == 1
    p = tree_placements[0]
    tree_only = key[:4] + [[p]]
    tree = pattern.build(tree_only, N)
    within = [(i, q) for i, q in enumerate(key[4]) if len({bool(t % 3) for t in q}) == 1]
    assert len(within) == len(key[4])-1
    witnesses = []
    for triple in tree:
        parent = min(triple, key=pattern.level)
        children = tuple(v for v in triple if v != parent)
        for index, q in within:
            local = key[:4] + [[q]]
            for knot in pattern.build(local, N):
                if set(children) <= set(knot):
                    n = pattern.level(parent)
                    term_by_letter = {t % 3: t for t in p}
                    maps = {a: actions(key, catalog[t//3], n) for a, t in term_by_letter.items()}
                    upper_x = parent - ((1 << n)-1)
                    w = maps[0].index(upper_x)
                    expected = (((1 << (n+1))-1) + 2*maps[1][w],
                                ((1 << (n+1))-1) + 2*maps[2][w]+1)
                    assert set(expected) == set(children)
                    witness = {"tree_placement": p, "within_placement_index": index,
                               "within_placement": q, "w": format(w, f"0{n}b") if n else "",
                               "parent": parent, "parent_word": address(parent),
                               "siblings": list(children), "sibling_words": list(map(address, children)),
                               "tree_knot": triple, "within_knot": knot,
                               "ordinary_prefix_siblings": address(children[0])[:-1] == address(children[1])[:-1]}
                    witnesses.append(witness)
    return {"tree_placement": p, "count": len(witnesses), "first_witness": witnesses[0] if witnesses else None,
            "witnesses": witnesses,
            "definition": "children of one upper distinction in the designated tree-type placement"}


def controls():
    rows = []
    n = 5
    for size in range(2, 6):
        expected = {s for s in it.combinations(range(n), size) if 0 in s and set(s)&{3,4}}
        actual = list(crossing_supports(n, [0], [3,4], size))
        assert len(actual) == len(set(actual)) and set(actual) == expected
    triples = list(it.combinations(range(4), 3))
    for mask in range(1 << len(triples)):
        knots = [row for j, row in enumerate(triples) if mask >> j & 1]
        states = [bits for bits in it.product((0, 1), repeat=4)
                  if all(len({bits[v] for v in row}) == 2 for row in knots)]
        full = {(): True}
        bonds = []
        for size in range(1, 5):
            for support in it.combinations(range(4), size):
                full[support] = len({tuple(bits[v] for v in support) for bits in states}) == (1 << size)
                if not full[support] and all(full[support[:j]+support[j+1:]] for j in range(size)):
                    bonds.append(support)
        for A, B in (([0], [3]), ([0,1], [2,3])):
            crossing = [s for s in bonds if set(s)&set(A) and set(s)&set(B)]
            truth = min(map(len, crossing)) if crossing else "none"
            result = least_bond(knots, 4, A, B, 4)
            other = fresh_search.search(knots, 4, A, B, cap=4, seconds=5)
            normalize = lambda value: "none" if value == "> 4" else value
            assert normalize(result["L"]) == normalize(other["L"]) == truth
            rows.append({"knots": knots, "A": A, "B": B, "truth": truth,
                         "fresh_enumeration": result["L"], "inherited_circuit": other["L"]})
    assert any(len({[0,0,0][v] for v in knot}) != 2 for knot in [(0,1,2)])
    output = {"candidate_partition_matches_plain_combinations": True,
              "comparisons": rows, "all_passed": True,
              "corrupted_all_zero_model_rejected": True}
    (HERE / "controls.json").write_text(json.dumps(output, indent=2)+"\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=int)
    parser.add_argument("--controls", action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2300*1024**2, 2300*1024**2))
    started = time.perf_counter()
    if args.controls:
        controls()
        print("controls passed", flush=True)
        return
    log = ROOT / "research/RULER-LEVEL-20261114-001/exploratory/tree_plus_within.log"
    rows = json.loads(log.read_text().split("counterexamples ",1)[1])
    assert args.case and 1 <= args.case <= len(rows)
    recorded = rows[args.case-1]
    key = recorded["key"]
    knots = pattern.build(key, 6)
    assert knots == pattern.direct_build(key, 6)
    _, width = fresh_search.elimination_order(knots, 127, 126)
    output = {"case": args.case, "key": key, "N": 6, "k": 1,
              "claimed_L": recorded["L"], "knots": knots, "knot_count": len(knots),
              "pattern_sha256": digest(knots), "two_builders_agree": True,
              "elimination_width": width, "siblings": sibling_audit(key, 6), "levels": []}
    destination = HERE / f"case_{args.case}.json"
    for s in (1, 2, 3):
        A, B = fresh_search.levels(1, s)
        result = least_bond(knots, 127, A, B, 4)
        output["levels"].append({"s": s, "A": A, "B": B, **result})
        output["seconds"] = time.perf_counter()-started
        output["max_rss_KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        output["sources_sha256"] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in [Path(__file__), log, REFEREE/"fresh_pattern.py",
                                              REFEREE/"fresh_search.py", pattern.OLD]}
        destination.write_text(json.dumps(output, indent=2)+"\n")
        print(json.dumps({"case": args.case, "s": s, "L": result["L"],
                          "seconds": result.get("seconds"), "enumerated": result.get("enumerated"),
                          "sibling_witnesses": output["siblings"]["count"]}), flush=True)


if __name__ == "__main__":
    main()
