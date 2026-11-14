"""Deterministic independent controls for G-pattern and G-brute.

The functions return JSON-compatible evidence; the main gate runner owns
writing gate results.  G-brute creates only its own temporary case work
directories during execution and removes them on exit.
"""

from pathlib import Path
import random
import tempfile
import time

import pattern as producer
import population
import reference


HERE = Path(__file__).resolve().parent
PATTERN_SEED = "LEVEL-REACH-20261114-001A-G-pattern"
BRUTE_SEED = "LEVEL-REACH-20261114-001A-G-brute"
PATTERN_CASES = 200
BRUTE_CASES = 300


def g_pattern():
    """Compare 200 keys at both study depths and cycling boundary depths."""
    started = time.monotonic()
    rng = random.Random(PATTERN_SEED)
    cases, failures, keys = [], [], []
    levels = {str(N): 0 for N in range(11)}
    identifiers = set()
    for index in range(PATTERN_CASES):
        key = population.random_key(rng)
        keys.append(key)
        identifier = population.key_id(key)
        identifiers.add(identifier)
        N = index % 11
        levels[str(N)] += 1
        begin = time.monotonic()
        try:
            actual = [tuple(int(item) for item in row) for row in producer.pattern(key, N)]
            expected = reference.pattern(key, N)
            matches = actual == expected
            row = {"index": index, "key_id": identifier, "N": N,
                   "producer_knots": len(actual), "reference_knots": len(expected),
                   "passed": matches}
            if not matches:
                failure = {"index": index, "key": population.key_json(key), "N": N,
                           "reason": "producer and reference patterns differ",
                           "only_producer": [list(t) for t in sorted(set(actual) - set(expected))[:10]],
                           "only_reference": [list(t) for t in sorted(set(expected) - set(actual))[:10]]}
                failures.append(failure)
        except Exception as error:
            row = {"index": index, "key_id": identifier, "N": N, "passed": False,
                   "error": f"{type(error).__name__}: {error}"}
            failures.append({**row, "key": population.key_json(key)})
        row["wall_seconds"] = time.monotonic() - begin
        cases.append(row)
    additional = []
    # Every random key is checked at both actual study depths, as well as
    # the cycling small-depth controls above.
    for index, key in enumerate(keys):
        for N in (9, 10):
            if N == index % 11:
                continue
            levels[str(N)] += 1
            actual = [tuple(int(item) for item in row) for row in producer.pattern(key, N)]
            expected = reference.pattern(key, N)
            matches = actual == expected
            additional.append({'index': index, 'N': N, 'passed': matches,
                               'knots': len(actual)})
            if not matches:
                failures.append({'index': index, 'N': N, 'key': population.key_json(key),
                                 'reason': 'producer and reference differ at actual study depth'})
    return {"gate": "G-pattern", "passed": not failures,
            "seed": PATTERN_SEED, "case_count": len(cases),
            "unique_keys": len(identifiers),
            "fixture_rule": "population.random_key; N=index%11 plus N=9,10 for every key",
            "checks": {"pattern_comparisons": len(cases) + len(additional), "by_N": levels},
            "cases": cases, "additional_depth_checks": additional, "failures": failures,
            "wall_seconds": time.monotonic() - started}


def brute_fixtures():
    """Yield the 300 reproducible tiny description keys without running them."""
    rng = random.Random(BRUTE_SEED)
    for index in range(BRUTE_CASES):
        yield index, population.random_key(rng)


def brute_expected(key):
    """Independently enumerate a fixture's states and supports at both gaps."""
    rows = reference.pattern(key, 3)
    top = tuple(range(1, 3))
    answers = {}
    for gap, target in ((1, tuple(range(3, 7))), (2, tuple(range(7, 15)))):
        answers[gap] = reference.brute_bonds(rows, 15, top, target, kmax=7)
    return rows, answers


def g_brute(search_factory):
    """Compare the actual generic search against all tiny projections.

    ``search_factory`` is the SearchEngine class or an equivalent callable:
    ``factory(K, nvars, workdir, certify=False, tree_optimization=False)``.
    Its instance has ``alive``, ``search(A, B, allowed=None, kmax=7,
    deadline=...)`` and ``close()``.  The certificates are checked separately
    by G-cert, so this control avoids LRAT subprocesses.
    """
    started = time.monotonic()
    cases, failures = [], []
    alive_cases = dead_cases = 0
    fate_checks = bond_checks = pattern_checks = 0
    state_boundaries = support_boundaries = 0
    identifiers = set()
    work_root = HERE / "work"
    work_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="g-brute-", dir=work_root) as scratch:
        for index, key in brute_fixtures():
            begin = time.monotonic()
            identifier = population.key_id(key)
            identifiers.add(identifier)
            row = {"index": index, "key_id": identifier, "passed": True,
                   "expected": {}, "actual": {}, "search_seconds": {}}
            engine = None
            try:
                reference_rows, expected = brute_expected(key)
                actual_rows = producer.pattern(key, 3)
                actual_plain = [tuple(int(item) for item in knot) for knot in actual_rows]
                pattern_checks += 1
                row["pattern_match"] = actual_plain == reference_rows
                row["knots"] = len(reference_rows)
                if not row["pattern_match"]:
                    row["passed"] = False
                    failures.append({"index": index, "reason": "tiny producer pattern mismatch",
                                     "key": population.key_json(key)})
                alive = expected[1]["alive"]
                if expected[2]["alive"] != alive:
                    raise AssertionError("the two reference reads disagree on fate")
                row["alive"] = alive
                row["state_count"] = expected[1]["state_count"]
                row["states_examined"] = expected[1]["states_examined"]
                row["support_count"] = expected[1]["support_count"]
                state_boundaries += expected[1]["states_examined"]
                support_boundaries += expected[1]["support_count"]
                if alive:
                    alive_cases += 1
                else:
                    dead_cases += 1
                engine = search_factory(actual_rows, 15, Path(scratch) / f"case-{index:04d}",
                                        certify=False, tree_optimization=False)
                observed_alive = engine.alive
                fate_checks += 1
                row["fate_match"] = observed_alive is not None and bool(observed_alive) == alive
                if not row["fate_match"]:
                    row["passed"] = False
                    failures.append({"index": index, "reason": "union fate mismatch",
                                     "reference_alive": alive, "search_alive": observed_alive,
                                     "key": population.key_json(key)})
                # The specified L observable has no value on a dead union.
                if alive and row["fate_match"]:
                    for gap, target in ((1, tuple(range(3, 7))), (2, tuple(range(7, 15)))):
                        search_begin = time.monotonic()
                        result = engine.search(tuple(range(1, 3)), target, allowed=None,
                                               kmax=7, deadline=time.monotonic() + 300)
                        label = str(gap)
                        row["search_seconds"][label] = time.monotonic() - search_begin
                        row["expected"][label] = expected[gap]["L"]
                        row["actual"][label] = result["L"]
                        bond_checks += 1
                        if result["L"] != expected[gap]["L"]:
                            row["passed"] = False
                            failures.append({"index": index, "gap": gap,
                                             "reason": "least bond size mismatch",
                                             "reference_L": expected[gap]["L"],
                                             "search_L": result["L"],
                                             "key": population.key_json(key)})
            except Exception as error:
                row["passed"] = False
                row["error"] = f"{type(error).__name__}: {error}"
                failures.append({"index": index, "reason": "exception",
                                 "error": row["error"], "key": population.key_json(key)})
            finally:
                if engine is not None:
                    try:
                        engine.close()
                    except Exception as error:
                        row["passed"] = False
                        failures.append({"index": index, "reason": "engine close exception",
                                         "error": f"{type(error).__name__}: {error}"})
            row["wall_seconds"] = time.monotonic() - begin
            cases.append(row)
            if not row["passed"]:
                break
    return {"gate": "G-brute", "passed": not failures and len(cases) == BRUTE_CASES,
            "seed": BRUTE_SEED, "case_count": len(cases),
            "requested_case_count": BRUTE_CASES, "stopped_after_failure": bool(failures),
            "unique_keys": len(identifiers), "alive_cases": alive_cases,
            "dead_cases": dead_cases,
            "fixture_rule": "population.random_key; N=3; k0=1; gaps=1,2; kmax=7",
            "checks": {"pattern_comparisons": pattern_checks, "fate_comparisons": fate_checks,
                       "bond_size_comparisons": bond_checks,
                       "state_space_boundaries_total": state_boundaries,
                       "support_boundaries_total": support_boundaries,
                       "states_per_case": 32768, "supports_per_case": 16384},
            "search_configuration": {"certify": False, "tree_optimization": False,
                                     "seconds_per_key_gap": 300},
            "exhaustion": "all 32768 states and all 16384 supports of sizes 0..7 per tiny pattern",
            "dead_L_policy": "compare fate only; L is undefined and never given a sentinel",
            "cases": cases, "failures": failures,
            "wall_seconds": time.monotonic() - started}
