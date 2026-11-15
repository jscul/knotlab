#!/usr/bin/env python3
"""Independent finite affine-cell, restriction, signed-sum and 3-CNF checks."""

import json
import random
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path

import solver


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def reference_outputs(n, edges, report):
    indexed = [(report // 2**i) % 2 for i in range(n)]
    individual = [int(indexed[u] == indexed[v] == 1) for u, v in edges]
    return sum(value * 2**i for i, value in enumerate(individual)), sum(individual) % 2


@lru_cache(maxsize=None)
def cells(n):
    """Generate every *set of points* of an affine space by adjoining directions."""
    cube = range(1 << n)
    queue = [frozenset({0})]
    seen = set(queue)
    for space in queue:
        for v in cube:
            if v in space:
                continue
            new = space | {x ^ v for x in space}
            if new not in seen:
                seen.add(new)
                queue.append(new)
    result = []
    for space in seen:
        left = set(cube)
        while left:
            o = min(left)
            points = tuple(sorted(o ^ x for x in space))
            left.difference_update(points)
            squares = {(o, x, y, o ^ x ^ y) for x, y in combinations(points[1:], 2)
                       if y < o ^ x ^ y}
            result.append((points, tuple(sorted(squares)), sum(1 << x for x in points)))
    return tuple(sorted(result, key=lambda item: (len(item[0]), item[0])))


def good_masks(values, all_cells):
    return [mask for _, squares, mask in all_cells
            if all(values[o] ^ values[x] ^ values[y] ^ values[z] == 0
                   for o, x, y, z in squares)]


def min_partition(n, masks):
    """Search disjoint subpartitions by branching on the smallest uncovered point."""
    covering = {v: sorted((mask for mask in masks if mask >> v & 1),
                          key=int.bit_count, reverse=True) for v in range(1 << n)}
    area = max(mask.bit_count() for mask in masks)

    @lru_cache(maxsize=None)
    def visit(uncovered):
        if not uncovered:
            return 0
        first = (uncovered & -uncovered).bit_length() - 1
        best = uncovered.bit_count()
        lower = (best + area - 1) // area
        for cell in covering[first]:
            if cell & uncovered == cell:
                best = min(best, 1 + visit(cell ^ uncovered))
                if best == lower:
                    break
        return best

    return visit((1 << (1 << n)) - 1)


def labelled_graphs(n):
    pairs = list(combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [edge for i, edge in enumerate(pairs) if mask >> i & 1]


def independent_size(n, edges):
    return max(choice.bit_count() for choice in range(1 << n)
               if all(choice & (1 << u | 1 << v) != (1 << u | 1 << v) for u, v in edges))


def compare_cells():
    graph_count = 0
    searched = {}
    for n in range(5):
        for edges in labelled_graphs(n):
            outputs = [reference_outputs(n, edges, r) for r in range(1 << n)]
            full = good_masks([p | (t << len(edges)) for p, t in outputs], cells(n))
            scalar = good_masks([t for _, t in outputs], cells(n))
            alpha = independent_size(n, edges)
            rank = solver.polar_rank(n, edges)
            require(max(m.bit_count() for m in full) == 1 << alpha, (n, edges, "individual"))
            require(max(m.bit_count() for m in scalar) == 1 << (n - rank // 2), (n, edges, "scalar"))
            graph_count += 1
            names = []
            if edges == solver.path(n):
                names.append("path")
            if edges == solver.star(n):
                names.append("star")
            if n >= 3 and len(edges) == n * (n - 1) // 2:
                names.append("complete")
            if names:
                observed = [min_partition(n, full), min_partition(n, scalar)]
                require(observed == [1 << (n - alpha), 1 << (rank // 2)], (n, edges, observed))
                for name in names:
                    searched[f"{name}_{n}"] = observed
    for edges in (solver.path(5), solver.star(5)):
        outputs = [reference_outputs(5, edges, r) for r in range(32)]
        for index in (0, 1):
            good = good_masks([value[index] for value in outputs], cells(5))
            require(max(m.bit_count() for m in good) == (8 if edges == solver.path(5) else 16),
                    ("one size past", edges, index))
    require(searched["complete_3"] == [4, 2], "individual products and the scalar differ")
    return {"all_labelled_graphs_through_four_reports": graph_count,
            "affine_sets_by_dimension": [len(cells(n)) for n in range(6)],
            "exact_min_partitions_full_then_scalar": searched}


def exact_query_tree(points, query_values, affine_terminal, totals):
    """Binary splits by every permitted parity; independently optimize size and depth."""
    width = max(query_values, default=0).bit_length()
    splits = {sum(((v & mask).bit_count() % 2) << i for i, v in enumerate(query_values))
              for mask in range(1, 1 << width)}

    @lru_cache(maxsize=None)
    def visit(subset):
        indices = [i for i in range(len(points)) if subset >> i & 1]
        if affine_terminal:
            points_here = {points[i] for i in indices}
            anchor = min(points_here)
            terminal = all(x ^ y ^ anchor in points_here for x, y in combinations(points_here, 2))
        else:
            terminal = len({totals[i] for i in indices}) == 1
        if terminal:
            return 1, 0
        candidates = {min(part, subset ^ part) for split in splits if (part := split & subset) not in (0, subset)}
        children = [(visit(part), visit(subset ^ part)) for part in candidates]
        return min(l[0] + r[0] for l, r in children), 1 + min(max(l[1], r[1]) for l, r in children)

    return visit((1 << len(points)) - 1)


def readout_models():
    results = {}
    for n, free in ((2, 0), (3, 1), (4, 0)):
        edges = solver.path(n)
        points = list(brute_report_graph(n, edges, free, True))
        totals = [(p >> (n + len(edges))) & 1 for p in points]
        report_only = [p & ((1 << n) - 1) for p in points]
        ambient = exact_query_tree(points, points, True, totals)
        report_bit = exact_query_tree(points, report_only, False, totals)
        oracle_bit = exact_query_tree(points, points, False, totals)
        require(ambient == (1 << (n // 2), n // 2) and report_bit == ((3, 2) if n < 4 else (7, 3))
                and oracle_bit == (2, 1), "affine cover and bit-only query tasks")
        results[f"path_{n}_free_{free}"] = {"ambient_exact_affine_relation": list(ambient),
                                             "report_queries_bit_output": list(report_bit),
                                             "ambient_queries_bit_output": list(oracle_bit)}
    return results


def points_for_checks(checks, p):
    return all((mask & p).bit_count() % 2 == rhs for mask, rhs in checks)


def defining_rows(points, n):
    """Use *every* constant parity to supply each restriction set independently."""
    return [(mask, next(iter(values))) for mask in range(1 << n)
            if len(values := {(mask & x).bit_count() % 2 for x in points}) == 1]


def brute_report_graph(n, edges, free, all_products=False):
    for a, w in product(range(1 << n), range(1 << free)):
        p, t = reference_outputs(n, edges, a)
        if all_products:
            yield a | p << n | t << (n + len(edges)) | w << (n + len(edges) + 1)
        else:
            yield a | t << n | w << (n + 1)


def check_decision(n, edges, free, rows, expected):
    observed = solver.decide(n, edges, rows, free)
    require((observed["status"] == "sat") == bool(expected), ("decision", n, edges, rows))
    if expected:
        r = observed["report"]
        require(observed["point"] in expected and
                reference_outputs(n, edges, r) == (observed["products"], observed["total"]),
                "the reconstructed witness must lie in the precise affine restriction")
    elif observed["points_tested"]:
        dim = observed["affine_dimension"]
        require(observed["points_tested"] == 1 + dim + dim * (dim - 1) // 2, "complete quadratic test")
    return observed


def check_restrictions(rng):
    exhaustive = 0
    for n in range(4):
        all_rows = [(set(points), defining_rows(points, n + 1)) for points, _, _ in cells(n + 1)]
        for edges in labelled_graphs(n):
            graph = set(brute_report_graph(n, edges, 0))
            for points, rows in all_rows:
                check_decision(n, edges, 0, rows, graph & points)
                exhaustive += 1
    random_trials = 0
    for n in range(2, 9):
        for trial in range(48):
            free = trial % 3
            pairs = combinations(range(n), 2)
            edges = [edge for edge in pairs if rng.randrange(3) == 0]
            rows = [(rng.randrange(1 << (n + free + 1)), rng.randrange(2))
                    for _ in range(rng.randrange(n + free + 4))]
            graph = brute_report_graph(n, edges, free)
            check_decision(n, edges, free, rows, {p for p in graph if points_for_checks(rows, p)})
            random_trials += 1
    square = [(3, 0), (5, 1)]   # R1=R0 and T=R0+1, so x²+x+1 evaluates to 1.
    folded = check_decision(2, [(0, 1)], 0, square, set())
    pair = solver.decide(2, [(0, 1)], [(4, 1)])
    require(folded["certificate"] == "constant-one Boolean quadratic" and
            pair["report"] == 3 and pair["points_tested"] == 4, "Boolean-square/pair controls")
    require(solver.decide(2, [], [(0, 1)])["points_tested"] == 0, "linear inconsistency")
    return {"every_nonempty_affine_restriction_through_3_reports": exhaustive,
            "random_reports_totals_and_free_witness_trials": random_trials,
            "formal_square_cancellation": folded, "two_free_ones_needed": pair}


def check_growth():
    table = []
    for n in [1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 17, 33, 65]:
        record = {"checks": n - 1, "reports": n}
        for name, edges, depth in (("star", solver.star(n), int(n > 1)), ("path", solver.path(n), n // 2)):
            cover = (1 << 0 if n > 1 else 0) if name == "star" else sum(1 << i for i in range(1, n, 2))
            require(all(cover & (1 << u | 1 << v) for u, v in edges), "claimed cover misses an edge")
            require(depth == cover.bit_count() == solver.polar_rank(n, edges) // 2, "upper/lower meeting")
            if n <= 9:
                for r in range(1 << n):
                    fixed = r & cover
                    expected = 0
                    for j, (u, v) in enumerate(edges):
                        exponent = u if cover & (1 << u) else v
                        other = v if exponent == u else u
                        expected |= (((fixed >> exponent) & (r >> other)) & 1) << j
                    require(reference_outputs(n, edges, r)[0] == expected, "whole-graph affine witness")
            record[name] = {"pieces": 1 << depth, "depth": depth}
        table.append(record)
    return table


def reflection():
    result = []
    for k in (1, 2, 3, 4, 8, 16, 32):
        n = 2 * k + 1
        rows = [(1 << i | 1 << (2 * k - i), 0) for i in range(k)]
        sat = solver.decide(n, solver.path(n), rows + [(1 << n, 0)])
        unsat = solver.decide(n, solver.path(n), rows + [(1 << n, 1)])
        require(sat["status"] == "sat" and unsat["certificate"] == "constant-one Boolean quadratic",
                "reflected path has zero total")
        if k <= 8:
            for r in range(1 << (k + 1)):
                chosen = list(range(k + 1)) + list(reversed(range(k)))
                reflected = sum(((r >> index) & 1) << i for i, index in enumerate(chosen))
                p, t = reference_outputs(n, solver.path(n), reflected)
                small, _ = reference_outputs(k + 1, solver.path(k + 1), r)
                bits = [(small >> i) & 1 for i in range(k)]
                require(t == 0 and p == sum(v << i for i, v in enumerate(bits + bits[::-1])),
                        "palindromic product values")
        result.append({"reports": n, "free_after_pinning_T": unsat["affine_dimension"],
                       "pieces_for_separate_products_on_reflection": 1 << ((k + 1) // 2),
                       "constant_one_points_checked": unsat["points_tested"]})
    return result


def check_scalar_sums(rng):
    tested = 0
    for n in range(5):
        monomials = [0] + [1 << i for i in range(n)] + [1 << i | 1 << j
                                                         for i, j in combinations(range(n), 2)]
        # All Boolean quadratics up to 4 variables (2,048 at n=4).
        for coeff in range(1 << len(monomials)):
            terms = [m for i, m in enumerate(monomials) if coeff >> i & 1]

            def evaluate(r):
                return sum((r & m) == m for m in terms) % 2

            exact = sum((-1)**evaluate(r) for r in range(1 << n))
            require(solver.quadratic_signed_sum(n, evaluate) == exact, (n, coeff, "signed sum"))
            tested += 1
    full_trials = star_trials = 0
    for n in range(7):
        for trial in range(60):
            free = trial % 2
            edges = solver.star(n) if trial % 3 == 0 else solver.path(n)
            if trial % 3 == 2:
                edges = [e for e in combinations(range(n), 2) if rng.randrange(3) == 0]
            width = n + len(edges) + 1 + free
            rows = [(rng.randrange(1 << width), rng.randrange(2)) for _ in range(rng.randrange(8))]
            exact = {p for p in brute_report_graph(n, edges, free, True) if points_for_checks(rows, p)}
            answer = solver.count_product_rows(n, edges, rows, free)
            require(answer["count"] == len(exact), ("full count", n, edges, rows, answer))
            full_trials += 1
            if edges == solver.star(n):
                observed = solver.decide_star(n, rows, free)
                require((observed["status"] == "sat") == bool(exact) and
                        (not exact or observed["point"] in exact), "star full-coordinate witness")
                star_trials += 1
    opposite = solver.count_product_rows(2, solver.path(2), [(4, 0), (4, 1)])
    require(opposite == {"count": 0, "product_rank": 1, "scalar_sums": 0},
            "opposite equations with the same product part must yield an affine contradiction")
    duplicate_with_linear = solver.count_product_rows(2, solver.path(2), [(4, 0), (5, 1)])
    require(duplicate_with_linear["count"] == 1, "dependent product rows may force a report bit")
    return {"scalar_quadratics_tested_exhaustively": tested, "full_coordinate_count_trials": full_trials,
            "star_two_branch_decision_trials": star_trials, "opposite_equal_product_rows": opposite}


def sparse_satisfied(rows, point):
    return all(sum((point >> i) & 1 for i in bits) % 2 == rhs for bits, rhs in rows)


def original_satisfied(clauses, original):
    return all(any(bool(original >> (abs(lit) - 1) & 1) == (lit > 0) for lit in clause)
               for clause in clauses)


def full_point(instance, report):
    p, t = reference_outputs(instance["reports"], instance["edges"], report)
    return report | p << instance["reports"] | t << instance["total_index"]


def reduction_controls():
    signs = list(product((1, -1), repeat=3))
    clauses = [tuple(sign * (i + 1) for i, sign in enumerate(pattern)) for pattern in signs]
    counts = {"instances": 0, "full_report_assignments": 0}
    for formula in [()] + [(clause,) for clause in clauses] + list(product(clauses, repeat=2)):
        instance = solver.reduce_3cnf(3, formula)
        expected = {r for r in range(8) if original_satisfied(formula, r)}
        empirical = []
        for r in range(1 << instance["reports"]):
            p = full_point(instance, r)
            if sparse_satisfied(instance["rows"], p):
                empirical.append(p)
        require(set(empirical) == {solver.extend_3cnf(instance, r) for r in expected}, "full projection")
        require(len(empirical) == len(expected) and {p & 7 for p in empirical} == expected, "unique lift")
        counts["instances"] += 1
        counts["full_report_assignments"] += 1 << instance["reports"]
    eight = solver.reduce_3cnf(3, clauses)
    seven_plus_repeat = solver.reduce_3cnf(3, [clauses[1]] + clauses[1:])
    require(eight["edges"] == seven_plus_repeat["edges"] and len(eight["rows"]) == 40, "matched paths")
    matched = []
    for instance in (eight, seven_plus_repeat):
        allowed = [r for r in range(8) if sparse_satisfied(instance["rows"], solver.extend_3cnf(instance, r))]
        require(allowed == [r for r in range(8) if original_satisfied(instance["clauses"], r)], "SAT originals")
        matched.append(allowed)
    require(matched == [[], [0]], "one changed clause must distinguish the matched instances")
    empty = solver.reduce_3cnf(0, [])
    require(solver.extend_3cnf(empty, 0) == 0 and not empty["rows"], "empty formula/control")
    # Omitting the second product wire gives a spurious lift for the all-false clause.
    one = solver.reduce_3cnf(3, [clauses[0]])
    r = (1 << 3) | (1 << 4) | (1 << 6)   # false, false, incorrect intermediate zero, false
    broken = [row for at, row in enumerate(one["rows"]) if at != 3]
    p = full_point(one, r)
    require(sparse_satisfied(broken, p) and not sparse_satisfied(one["rows"], p) and (p & 7) == 0,
            "removing the intermediate wire must introduce a false answer")
    counts.update({"matched_reports": eight["reports"], "matched_path_products": len(eight["edges"]),
                   "matched_affine_rows": len(eight["rows"]), "matched_UNSAT_then_SAT_originals": matched,
                   "broken_intermediate_wire_falsifying_original": p & 7})
    return counts


def four_reports():
    n = 4
    rows = []
    for s, t in product(range(2), repeat=2):
        coefficient = [s, 0, s ^ t, 0]
        coef_mask = sum(v << i for i, v in enumerate(coefficient))
        matches = []
        for r in range(16):
            if ((r >> 1) & 1, (r >> 3) & 1) == (s, t):
                matches.append(r)
                p, total = reference_outputs(4, solver.path(n), r)
                require((p & 1) == (s & r & 1) and (p >> 1 & 1) == (s & (r >> 2) & 1) and
                        (p >> 2 & 1) == (t & (r >> 2) & 1) and total == (r & coef_mask).bit_count() % 2,
                        "four-report explicit cell")
        rows.append({"R1_R3": [s, t], "reports_as_masks": matches, "T_affine_mask": coef_mask})
    return rows


def raw_section():
    checked = 0
    for n in (3, 4, 5):
        for a, b in product(range(2), repeat=2):
            for r in range(1 << n):
                x, y = 1, 1 ^ (a & b)
                got = sum((((r >> i) & 1) & ((x & y) ^ (a & b))) << i for i in range(n))
                require(got == r, "report lift does not realize its intended vector")
                checked += 1
    return checked


def main():
    rng = random.Random(20261115)
    result = {"status": "passed", "affine_census": compare_cells(), "growth": check_growth(),
              "first_strict_four_report_partition": four_reports(), "raw_report_sections": raw_section(),
              "exact_query_leaves_then_depth": readout_models(),
              "single_checksum_decision": check_restrictions(rng), "reflected_path": reflection(),
              "multiple_product_checksums": check_scalar_sums(rng), "fixed_path_3cnf_reduction": reduction_controls()}
    saved = Path(__file__).with_name("checks.json")
    if saved.exists():
        require(json.loads(saved.read_text()) == result, "checked output differs from the recorded certificate")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
