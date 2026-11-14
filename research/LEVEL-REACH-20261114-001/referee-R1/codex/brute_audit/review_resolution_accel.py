"""Independent truth-table controls for the optional resolution pruning."""
from __future__ import annotations

import hashlib
import itertools as it
import json
import random
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import resolution_accel as accel
import fresh_search


def states_and_bonds(knots, nvars):
    states = [bits for bits in it.product((0, 1), repeat=nvars)
              if all(len({bits[v] for v in row}) == 2 for row in knots)]
    if not states:
        return [], []
    full = {(): True}
    bonds = []
    for size in range(1, nvars + 1):
        for support in it.combinations(range(nvars), size):
            projection = {tuple(bits[v] for v in support) for bits in states}
            full[support] = len(projection) == 1 << size
            if not full[support] and all(full[support[:j] + support[j + 1:]] for j in range(size)):
                bonds.append(support)
    return states, bonds


def normalize(value, cap):
    return "none" if value == f"> {cap}" else value


def digest(circuit):
    return hashlib.sha256(json.dumps([circuit.top, circuit.clauses], separators=(",", ":")).encode()).hexdigest()


def main():
    started = time.perf_counter()
    cases = []
    triples4 = list(it.combinations(range(4), 3))
    for mask in range(1 << len(triples4)):
        cases.append((4, [row for i, row in enumerate(triples4) if mask >> i & 1], "all_N4_NAE_patterns"))
    rng = random.Random("independent-resolution-pruning-review-20261114")
    for nvars, count in ((6, 32), (7, 16)):
        possible = list(it.combinations(range(nvars), 3))
        for _ in range(count):
            size = rng.randrange(len(possible) + 1)
            cases.append((nvars, sorted(rng.sample(possible, size)), "random_NAE_patterns"))
    outputs = []
    support_checks = 0
    mutation_checks = 0
    maximum_extra_variables = 0
    for case_index, (nvars, knots, source) in enumerate(cases):
        states, bonds = states_and_bonds(knots, nvars)
        support_cache = accel.derived_nonfull(knots)
        supports = support_cache[0]
        if states:
            for support in supports:
                projection = {tuple(bits[v] for v in support) for bits in states}
                assert len(projection) < (1 << len(support)), (case_index, support)
                support_checks += 1
        precompiled = fresh_search.compile_existence(knots, nvars, time.monotonic() + 30, width_limit=8)
        original = digest(precompiled[0])
        if nvars == 4:
            endpoints = [([a], [b]) for a in range(nvars) for b in range(nvars) if a != b]
        else:
            endpoints = [([0], [nvars - 1]), (list(range(nvars // 2)), list(range(nvars // 2, nvars))),
                         ([1, 2], [3, 4]), ([], [0])]
        for A, B in endpoints:
            crossing = [row for row in bonds if set(A).intersection(row) and set(B).intersection(row)]
            truth = "dead" if not states else min(map(len, crossing)) if crossing else "none"
            # Allocation/mutation check exercises the public filter operation.
            filtered, blocks = accel.add_support_filters(precompiled, supports, A, B)
            circuit = filtered[0]
            assert circuit is not precompiled[0]
            assert circuit.top >= precompiled[0].top >= 2 * nvars
            assert circuit.clauses[:len(precompiled[0].clauses)] == precompiled[0].clauses
            extra = circuit.top - precompiled[0].top
            maximum_extra_variables = max(maximum_extra_variables, extra)
            assert all(abs(lit) <= circuit.top for clause in circuit.clauses for lit in clause)
            # The new prefix is selector/presence equivalence in three-clause groups.
            new = circuit.clauses[len(precompiled[0].clauses):]
            allocated = set()
            for i in range(extra):
                c0, c1, c2 = new[3 * i:3 * i + 3]
                p = c0[1]
                assert precompiled[0].top < p <= circuit.top and p not in allocated
                allocated.add(p)
                assert c1[1] == p and c2[0] == -p
                assert -c0[0] + 1 == -c1[0]
                assert c2[1:] == [-c0[0], -c1[0]]
                assert 1 <= -c0[0] <= 2 * nvars and 1 <= -c1[0] <= 2 * nvars
            assert len(new) == 3 * extra + blocks
            for clause in new[3 * extra:]:
                assert all(lit < 0 and -lit in allocated for lit in clause)
            plain = fresh_search.search(knots, nvars, A, B, cap=nvars, seconds=10, precompiled=precompiled)
            fast = accel.accelerated_search(knots, nvars, A, B, cap=nvars, seconds=10,
                                            precompiled=precompiled, support_cache=support_cache)
            assert plain["exact"] and fast["exact"], (case_index, plain, fast)
            assert normalize(plain["L"], nvars) == normalize(fast["L"], nvars) == truth, (case_index, A, B, truth, plain, fast)
            assert digest(precompiled[0]) == original
            mutation_checks += 1
            outputs.append({"case": case_index, "nvars": nvars, "knots": knots, "source": source,
                            "A": A, "B": B, "truth": truth, "plain": plain["L"], "accelerated": fast["L"],
                            "extra_presence_variables": extra, "support_filters": blocks})
    result = {"review": "approved_subject_to_matching_cache_input_contract", "formulas": len(cases),
              "comparisons": len(outputs), "all_comparisons_match": True,
              "alive_derived_support_truth_checks": support_checks,
              "precompiled_nonmutation_checks": mutation_checks,
              "maximum_extra_presence_variables": maximum_extra_variables,
              "seconds": time.perf_counter() - started,
              "max_rss_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "soundness_argument": [
                  "Each new clause is a non-tautological resolvent of an original clause and an original/proved clause.",
                  "A non-tautological implicate witnesses a non-full projection on its support.",
                  "A support missing A or B is a strict subset of any crossing superset, so forbidding its supersets removes no bond.",
                  "Filter auxiliaries start after original circuit.top; search continues after the updated top before its own auxiliaries.",
                  "Shallow-copy memo is never mutated by these paths; clause lists and top counters are independent.",
              ],
              "limits": [
                  "The optional precompiled and support_cache arguments must be derived from the identical knots/nvars; the wrapper does not validate that contract.",
                  "Resolution preparation has no deadline check; clause_limit bounds retained clauses, not resolution attempts or preparation wall time.",
                  "The parent's depth benchmark was neither rerun nor inspected.",
              ],
              "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                                [HERE.parent / "resolution_accel.py", HERE.parent / "fresh_search.py", Path(__file__)]},
              "controls": outputs}
    (HERE / "resolution_accel_review.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("controls", "soundness_argument", "source_sha256")}, indent=2))


if __name__ == "__main__":
    main()
