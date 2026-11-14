"""Reproduce the compiler checks already executed by the reference worker.

Retention itself did not rerun these checks.  This script uses the same
fixtures and random seed as those executions; it adds no scientific cases.
It prints a JSON record and starts no external certificate processes.

Run from the repository with:
    .venv/bin/python -B <CODEX>/validate_compiled.py
"""

import hashlib
import itertools
import json
from pathlib import Path
import random
import time

from pysat.solvers import Minisat22

from compiled_search import CompiledPattern


HERE = Path(__file__).resolve().parent
RANDOM_SEED = "LEVEL-REACH-compiled-n15-20261114"


def check_smoke_and_fallbacks():
    """The preceding tiny smoke cases and the two limit fallbacks."""
    partials = solver_checks = 0
    cases = []
    for rows, n in (([], 0), ([], 2), ([(0, 1, 2)], 3)):
        compiled = CompiledPattern(rows, n)
        assert compiled.available, compiled.reason
        valid = [state for state in range(1 << n)
                 if all(len({(state >> v) & 1 for v in row}) > 1 for row in rows)]
        with Minisat22(bootstrap_with=compiled.clauses) as solver:
            for values in itertools.product(range(3), repeat=n):
                units, constraints = [], []
                for v, value in enumerate(values):
                    s0, s1 = 2*v+1, 2*v+2
                    units += [s0 if value == 1 else -s0, s1 if value == 2 else -s1]
                    if value:
                        constraints.append((v, value - 1))
                expected = any(all(((state >> v) & 1) == value
                                   for v, value in constraints) for state in valid)
                if type(compiled.root) is bool:
                    assert compiled.root == expected
                    assert solver.solve(assumptions=units)
                    solver_checks += 1
                else:
                    right = compiled.root if expected else -compiled.root
                    assert solver.solve(assumptions=units + [right])
                    assert not solver.solve(assumptions=units + [-right])
                    solver_checks += 2
                partials += 1
        cases.append({"nvars": n, "knots": len(rows), "root": compiled.root,
                      "stats": compiled.stats})
    wide = CompiledPattern(list(itertools.combinations(range(5), 3)), 5, width_limit=3)
    limited = CompiledPattern([(0, 1, 2)], 3, gate_limit=1)
    assert not wide.available and not wide.clauses and wide.root is None
    assert not limited.available and not limited.clauses and limited.root is None
    return {"passed": True, "patterns": len(cases), "ternary_assignments": partials,
            "compiled_root_SAT_checks": solver_checks, "cases": cases,
            "fallback_tests": {"passed": 2, "width": {"reason": wide.reason, "stats": wide.stats},
                               "gate": {"reason": limited.reason, "stats": limited.stats}}}


def check_exhaustive():
    """Every NAE pattern on 0..5 ids, every ternary partial assignment."""
    started = time.monotonic()
    patterns = partials = solver_checks = 0
    max_gates = max_width = 0
    for n in range(6):
        knots = list(itertools.combinations(range(n), 3))
        fixtures = []
        for values in itertools.product(range(3), repeat=n):
            selectors, mask, required = [], 0, 0
            for v, value in enumerate(values):
                selectors.extend((2*v+1 if value == 1 else -(2*v+1),
                                  2*v+2 if value == 2 else -(2*v+2)))
                if value:
                    mask |= 1 << v
                    required |= (value - 1) << v
            compatible = sum(1 << state for state in range(1 << n)
                             if state & mask == required)
            fixtures.append((selectors, compatible))
        for chosen in range(1 << len(knots)):
            rows = [row for j, row in enumerate(knots) if (chosen >> j) & 1]
            compiled = CompiledPattern(rows, n)
            assert compiled.available, (n, chosen, compiled.reason)
            max_gates = max(max_gates, compiled.gate_count)
            max_width = max(max_width, compiled.width)
            masks = [sum(1 << v for v in row) for row in rows]
            allowed = sum(1 << state for state in range(1 << n)
                          if all(0 < state & mask < mask for mask in masks))
            with Minisat22(bootstrap_with=compiled.clauses) as solver:
                for selectors, compatible in fixtures:
                    expected = bool(allowed & compatible)
                    if type(compiled.root) is bool:
                        assert compiled.root == expected, (n, chosen, selectors, "constant root")
                        assert solver.solve(assumptions=selectors)
                        solver_checks += 1
                    else:
                        right = compiled.root if expected else -compiled.root
                        assert solver.solve(assumptions=selectors + [right]), (
                            n, chosen, selectors, "correct root rejected")
                        assert not solver.solve(assumptions=selectors + [-right]), (
                            n, chosen, selectors, "wrong root accepted")
                        solver_checks += 2
                    partials += 1
            patterns += 1
    empty = CompiledPattern([], 5)
    presence_checks = 0
    with Minisat22(bootstrap_with=empty.clauses) as solver:
        for values in itertools.product(range(3), repeat=5):
            selectors = []
            for v, value in enumerate(values):
                selectors.extend((2*v+1 if value == 1 else -(2*v+1),
                                  2*v+2 if value == 2 else -(2*v+2)))
            for v, value in enumerate(values):
                wrong = -empty.presence[v] if value else empty.presence[v]
                assert not solver.solve(assumptions=selectors + [wrong])
                presence_checks += 1
    return {"passed": True, "all_patterns_through_n5": patterns,
            "all_ternary_partials": partials, "compiled_root_SAT_checks": solver_checks,
            "presence_checks": presence_checks, "max_width": max_width,
            "max_gates": max_gates, "wall_seconds": time.monotonic() - started}


def check_random_n15():
    """The same 100 seeded patterns and assignments versus original SAT."""
    rng = random.Random(RANDOM_SEED)
    all_rows = list(itertools.combinations(range(15), 3))
    available = fallback = partials = additional_boolean = 0
    max_width = max_gates = max_tables = 0
    started = time.monotonic()
    for case in range(100):
        rows = sorted(rng.sample(all_rows, rng.randrange(25)))
        compiled = CompiledPattern(rows, 15)
        if not compiled.available:
            fallback += 1
            assert not compiled.clauses and compiled.root is None and not compiled.presence
            continue
        available += 1
        max_width = max(max_width, compiled.width)
        max_gates = max(max_gates, compiled.gate_count)
        max_tables = max(max_tables, compiled.table_entries)
        clauses = []
        for row in rows:
            clauses.extend(([v + 1 for v in row], [-v - 1 for v in row]))
        with Minisat22(bootstrap_with=clauses) as original, \
                Minisat22(bootstrap_with=compiled.clauses) as circuit:
            for sample in range(110):
                values = [rng.randrange(3) if sample < 100 else rng.randrange(4)
                          for _ in range(15)]
                selectors, units = [], []
                for v, value in enumerate(values):
                    zero, one = value in (1, 3), value in (2, 3)
                    selectors.extend((2*v+1 if zero else -(2*v+1),
                                      2*v+2 if one else -(2*v+2)))
                    if zero:
                        units.append(-v - 1)
                    if one:
                        units.append(v + 1)
                expected = original.solve(assumptions=units)
                if type(compiled.root) is bool:
                    assert compiled.root == expected, (case, sample, compiled.root, expected)
                    assert circuit.solve(assumptions=selectors)
                else:
                    right = compiled.root if expected else -compiled.root
                    assert circuit.solve(assumptions=selectors + [right]), (case, sample, "right root")
                    assert not circuit.solve(assumptions=selectors + [-right]), (case, sample, "wrong root")
                if sample < 100:
                    partials += 1
                else:
                    additional_boolean += 1
    return {"passed": True, "seed": RANDOM_SEED, "random_n15_patterns": 100,
            "available": available, "width_fallbacks": fallback,
            "ternary_assignments_vs_original_SAT": partials,
            "additional_boolean_selector_assignments": additional_boolean,
            "max_width": max_width, "max_gate_count": max_gates,
            "max_table_entries": max_tables, "wall_seconds": time.monotonic() - started}


def first_pilot_compile_assay():
    """Retain the already executed, non-evidence first-key compilation assay."""
    import pattern
    import population

    key = population.build_population("P")["keys"][0]["key"]
    rows = pattern.pattern(key, 7)
    started = time.monotonic()
    compiled = CompiledPattern(rows, (1 << 8) - 1)
    return {"first_P_key_N7": population.key_id(key), "knots": len(rows),
            "available": compiled.available, "reason": compiled.reason,
            "stats": compiled.stats, "wall_seconds": time.monotonic() - started}


def main():
    source_hash = hashlib.sha256((HERE / "compiled_search.py").read_bytes()).hexdigest()
    result = {"status": "passed", "execution": "this invocation executed the retained checks",
              "compiled_search_sha256": source_hash,
              "smoke_and_fallbacks": check_smoke_and_fallbacks(),
              "exhaustive": check_exhaustive(), "random_n15": check_random_n15(),
              "first_pilot_compile_assay": first_pilot_compile_assay()}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
