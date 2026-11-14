"""Controls for the lead's fresh code; independent truth-table expectations."""
from __future__ import annotations
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import random
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
sys.path.insert(0, str(PARENT))
import fresh_pattern as pattern
import fresh_search as search
from pysat.solvers import Solver
from audit_certificates import rebuild


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def states(knots, n):
    masks = [sum(1 << v for v in triple) for triple in knots]
    return [m for m in range(1 << n) if all((m & t) not in (0, t) for t in masks)]


def selector_inputs(n):
    for choices in itertools.product(range(4), repeat=n):
        fixed, zeros, ones = [], 0, 0
        for v, choice in enumerate(choices):
            fixed.extend([(2*v+1) if choice & 1 else -(2*v+1),
                          (2*v+2) if choice & 2 else -(2*v+2)])
            if choice & 1:
                zeros |= 1 << v
            if choice & 2:
                ones |= 1 << v
        yield choices, fixed, zeros, ones


def circuit_check(circuit, root, n, models, clauses=None, stop_first=False):
    errors, checked = [], 0
    solver = Solver(name='g4', bootstrap_with=circuit.clauses if clauses is None else clauses)
    try:
        for choices, fixed, zeros, ones in selector_inputs(n):
            expected = not (zeros & ones) and any((m & zeros) == 0 and (m & ones) == ones for m in models)
            if isinstance(root, bool):
                possible = solver.solve(assumptions=fixed)
                positive, negative = possible and root, possible and not root
            else:
                positive = solver.solve(assumptions=fixed + [root])
                negative = solver.solve(assumptions=fixed + [-root])
            checked += 1
            if positive != expected or negative != (not expected):
                errors.append({'choices': choices, 'expected': expected,
                               'root_true_possible': positive, 'root_false_possible': negative})
                if stop_first:
                    break
    finally:
        solver.delete()
    return checked, errors


def plain_components(knots, n):
    adjacency = [set() for _ in range(n)]
    for row in knots:
        for v in row:
            adjacency[v].update(row)
    components = []
    unseen = set(range(n))
    while unseen:
        todo = [min(unseen)]
        found = set()
        while todo:
            v = todo.pop()
            if v in found:
                continue
            found.add(v)
            todo.extend(adjacency[v] - found)
        components.append(found)
        unseen -= found
    return components


def full(models, support):
    projections = {sum(((m >> v) & 1) << j for j, v in enumerate(support)) for m in models}
    return len(projections) == (1 << len(support))


def brute_answer(knots, n, A, B, allowed, cap, models):
    if not models:
        return 'dead'
    if not any(c & set(A) and c & set(B) for c in plain_components(knots, n)):
        return 'none'
    for size in range(2, min(cap, len(allowed)) + 1):
        for support in itertools.combinations(sorted(allowed), size):
            if not set(support) & set(A) or not set(support) & set(B):
                continue
            if full(models, support):
                continue
            if all(full(models, [x for x in support if x != v]) for v in support):
                return size
    return f'> {cap}'


def main():
    resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
    start = time.monotonic()
    rng = random.Random(20261114936)
    formula_cases = []
    for n in (3, 4):
        catalog = list(itertools.combinations(range(n), 3))
        for included in range(1 << len(catalog)):
            formula_cases.append((n, [t for i, t in enumerate(catalog) if included >> i & 1]))
    for n, count in ((5, 24), (6, 8), (7, 10)):
        catalog = list(itertools.combinations(range(n), 3))
        for _ in range(count):
            formula_cases.append((n, sorted(rng.sample(catalog, rng.randrange(len(catalog) + 1)))))
    circuit_total = search_total = pattern_total = 0
    error_rows = []
    count_by_n = Counter()
    for fi, (n, knots) in enumerate(formula_cases):
        models = states(knots, n)
        compiled = search.compile_existence(knots, n, time.monotonic() + 30, width_limit=8)
        circuit, root, _ = compiled
        if n <= 6:
            count, errors = circuit_check(circuit, root, n, models)
            circuit_total += count
            count_by_n[n] += 1
            if errors:
                error_rows.append({'fixture': fi, 'check': 'circuit', 'errors': errors[:3]})
        endpoints = [([0], [n-1]), (list(range(n//2)), list(range(n//2, n)))]
        for A, B in endpoints:
            for cap in sorted({2, 3, n}):
                for restriction in (False, True):
                    allowed = set(range(n)) if not restriction else set(A) | set(B) | {v for v in range(n) if rng.randrange(2)}
                    expected = brute_answer(knots, n, A, B, allowed, cap, models)
                    actual = search.search(knots, n, A, B, cap=cap, seconds=30,
                                           precompiled=compiled, model_name='g4', allowed=allowed)
                    search_total += 1
                    if actual['L'] != expected or not actual['exact']:
                        error_rows.append({'fixture': fi, 'check': 'search', 'knots': knots, 'A': A, 'B': B,
                                           'allowed': sorted(allowed), 'cap': cap, 'expected': expected, 'actual': actual})
                    if isinstance(actual['L'], int):
                        support = actual['bond']
                        ass = actual['forbidden_assignment']
                        compatible = any(all(((m >> v) & 1) == b for v, b in zip(support, ass)) for m in models)
                        if compatible or full(models, support) or not all(full(models, [x for x in support if x != v]) for v in support):
                            error_rows.append({'fixture': fi, 'check': 'returned witness invalid', 'actual': actual})
    # The compiler's actual dual rails are tested above, including both rails on.
    circuit, root, _ = search.compile_existence([(0, 1, 2)], 3, time.monotonic() + 30)
    models = states([(0, 1, 2)], 3)
    _, root_wrong = circuit_check(circuit, -root, 3, models, stop_first=True)
    changed = [list(c) for c in circuit.clauses]
    changed[0][0] = -changed[0][0]
    _, gate_wrong = circuit_check(circuit, root, 3, models, changed, stop_first=True)
    plan = json.loads((PARENT / 'sample_plan.json').read_text())
    for entry in plan['sample']:
        for N in (0, 1, 3, 5):
            a = pattern.build(entry['key'], N)
            b = pattern.direct_build(entry['key'], N)
            c = rebuild(entry['key'], N)
            pattern_total += 1
            if a != b or a != c:
                error_rows.append({'case': entry['case'], 'N': N, 'check': 'pattern builder mismatch'})
    result = {'source_sha256': {p.name: sha(p) for p in (PARENT / 'fresh_pattern.py', PARENT / 'fresh_search.py')},
              'formula_fixtures': len(formula_cases), 'circuit_fixtures_by_n': dict(count_by_n),
              'complete_actual_selector_assignments_checked': circuit_total,
              'brute_relation_vs_search_comparisons': search_total,
              'pattern_build_comparisons': pattern_total,
              'flipped_root_mutation_rejected': bool(root_wrong), 'flipped_gate_literal_mutation_rejected': bool(gate_wrong),
              'mutation_witnesses': {'flipped_root': root_wrong, 'flipped_gate_literal': gate_wrong},
              'errors': error_rows, 'passed': not error_rows and bool(root_wrong) and bool(gate_wrong),
              'seconds': time.monotonic() - start,
              'peak_rss_mb': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024}
    (HERE / 'search_review_controls.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
