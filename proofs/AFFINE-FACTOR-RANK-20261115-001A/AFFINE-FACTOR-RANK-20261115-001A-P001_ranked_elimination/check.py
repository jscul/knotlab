"""Exercise original refutations, Gaussian coordinates, and the primitive guarded deductions."""
from copy import deepcopy
from itertools import permutations, product
import json
from pathlib import Path
import runpy


HERE = Path(__file__).resolve().parent
M = runpy.run_path(str(HERE / "solver.py"))
A, B, Q = (M[key] for key in ("A", "B", "Q"))
ZERO, ONE, add, var, opposite = (M[key] for key in ("ZERO", "ONE", "add", "var", "opposite"))
mul = Q["mul"]
OLD_B = "PRODUCT-NAME-TRANSFER-20261115-001B"
old_checks = runpy.run_path(str(M["ROOT"] / "proofs" / OLD_B / (OLD_B + "-P001_bounded_elimination") / "check.py"))
truth_check = old_checks["truth_check"]


def rank_two_example():
    """Every definition is an ordinary ancestor of the contradiction. The first name is reused."""
    x, y, z = map(var, (1, 2, 3))
    cnf = [[1], [2], [3], [-1, -2, -3]]
    dag = A["Dag"](3, cnf)
    boolean = B["affine_boolean_builder"](dag)

    def forward(name, declaration, f, ef, g, eg):
        # ef and eg assert f=1 and g=1. Derive name=1 from the defining equation.
        first = dag.multiply(ef, opposite(f), g)
        both = dag.combine(first, eg, mul(opposite(f), g), opposite(g))
        equation = add(var(name), mul(f, g))
        return dag.combine(both, declaration, opposite(mul(f, g)), equation)

    def backward(name, declaration, unit, factor, other):
        # Derive name -> factor from the definition and E_factor, then apply name=1.
        product_value = mul(factor, other)
        step = dag.multiply(boolean(factor), factor, other)
        implies = dag.combine(step, declaration, product_value, add(var(name), product_value))
        return dag.delete_false(dag.combine(unit, implies, opposite(var(name)), var(name)))

    ex, ey, ez = (dag.axiom(i) for i in range(3))
    t, dt = dag.define(x, z)
    vt = var(t)
    et = forward(t, dt, x, ex, z, ez)
    # Reconstitute this live unit through a formal square, using its DAG parent twice.
    sq1 = dag.multiply(et, opposite(vt), vt)
    sq2 = dag.multiply(et, opposite(vt), opposite(vt))
    et = dag.combine(sq1, sq2, mul(opposite(vt), vt), mul(opposite(vt), opposite(vt)))
    u, du = dag.define(vt, y)
    eu = forward(u, du, vt, et, y, ey)

    mixed = opposite(add(x, y))
    other = opposite(add(vt, z))
    emixed = dag.combine(ex, ey, opposite(x), opposite(y))
    eother = dag.combine(et, ez, opposite(vt), opposite(z))
    v, dv = dag.define(mixed, other)
    ev = forward(v, dv, mixed, emixed, other, eother)

    joined = opposite(add(var(u), var(v)))
    ej = dag.combine(eu, ev, opposite(var(u)), opposite(var(v)))
    w, dw = dag.define(joined, y)
    ew = forward(w, dw, joined, ej, y, ey)
    ej = backward(w, dw, ew, joined, y)
    eu = dag.combine(ej, ev, opposite(joined), opposite(var(v)))
    et = backward(u, du, eu, vt, y)
    ey = backward(u, du, eu, y, vt)
    ex = backward(t, dt, et, x, z)
    ez = backward(t, dt, et, z, x)
    node = dag.axiom(3)
    for i, unit in enumerate((ex, ey, ez), 1):
        node = dag.resolve(unit, node, i)
    assert dag.clauses[node] == () and node == len(dag.proof) - 1
    return cnf, dag.proof


def mask_form(n, code):
    return tuple([()] * (code & 1) + [(i,) for i in range(1, n + 1) if code >> i & 1])


def form_mask(form):
    return sum(1 << (term[0] if term else 0) for term in form)


def test_coordinates():
    pairs = queries = 0
    for aa, bb in product(range(16), repeat=2):
        # Direct subset sums on the three input names, independent of Gaussian elimination.
        generators = [mask_form(3, aa), mask_form(3, bb)]
        expected = {0, aa & ~1, bb & ~1, (aa ^ bb) & ~1}
        basis = M["AffineBasis"](3, generators)
        assert len(expected) == 2 ** basis.rank
        for query in range(16):
            coords = basis.coordinates(mask_form(3, query))
            assert (coords is not None) == ((query & ~1) in expected)
            if coords is not None:
                constant, mask = coords
                rebuilt = constant
                for i, f in enumerate(basis.forms):
                    if mask >> i & 1:
                        rebuilt ^= form_mask(f)
                assert rebuilt == query
            queries += 1
        pairs += 1
    # Four overlapping generators in five variables all have the same highest pivot.
    vectors = [1 << i | 1 << 5 for i in range(1, 5)]
    extra_queries = 0
    for order in permutations(vectors):
        generators = [mask_form(5, code | (i % 2)) for i, code in enumerate(order)]
        dependent = order[0] ^ order[2]
        basis = M["AffineBasis"](5, [ONE, *generators, mask_form(5, dependent | 1)])
        assert basis.rank == 4
        for query in range(64):
            result = basis.coordinates(mask_form(5, query))
            # The linear span consists exactly of the even-weight vectors in five variables.
            assert (result is not None) == ((query >> 1).bit_count() % 2 == 0)
            if result is not None:
                constant, mask = result
                reconstructed = constant
                for i, code in enumerate(order):
                    if mask >> i & 1:
                        reconstructed ^= code
                assert reconstructed == query
            extra_queries += 1
    return {"ordered_generator_pairs": pairs, "span_and_coordinate_queries": queries,
            "rank_four_overlapping_basis_queries": extra_queries}


def test_guard_equations():
    branch_count = mask_count = 0
    for r in range(5):
        basis = M["AffineBasis"](r, [opposite(var(i)) for i in range(1, r + 1)])
        dag = Q["Dag"]([[]])
        boolean = B["affine_boolean_builder"](dag)
        for bits in product((0, 1), repeat=r):
            context, derive = M["guard_equation_builder"](dag, basis.forms, bits, boolean)
            expected_context = [mask_form(r, (1 << (i + 1)) | (bit ^ 1)) for i, bit in enumerate(bits)]
            assert list(context) == expected_context
            for mask in range(1 << r):
                selected, node = derive(mask)
                constant = sum(b for i, b in enumerate(bits) if mask >> i & 1) % 2
                expected = mask_form(r, (mask << 1) | constant)
                assert selected == expected and dag.clauses[node] == tuple(sorted([*expected_context, expected]))
                mask_count += 1
            branch_count += 1
        dag.axiom(0)
        Q["verify"](r, [[]], dag.proof)
        truth_check(r, [[]], dag.proof)
    return {"ranks": list(range(5)), "branch_contexts": branch_count, "subset_equations": mask_count}


def reject(fn):
    try:
        fn()
    except ValueError as error:
        return str(error)
    raise AssertionError("semantically malformed control was accepted")


def replay(n, cnf, proof, generators):
    out, stats = M["eliminate"](n, cnf, proof, generators)
    truth_check(n, cnf, out)
    assert stats["nodes"] == len(out) <= stats["verified_node_bound"]
    assert all(row["rule"] != "define" for row in out)
    return out, stats


def fixture_report():
    cnf, proof = rank_two_example()
    named = A["verify"](3, cnf, proof)
    definitions = B["declarations"](3, proof)
    ancestors = set(A["ancestors"](3, cnf, proof, include_declarations=False))
    assert all(i in ancestors for i, row in enumerate(proof) if row["rule"] == "define")
    assert sum(var(4)[0] in factor for _, f, g in definitions[1:] for factor in (f, g)) == 2
    gate_tables = []
    for x, y, z in product((0, 1), repeat=3):
        t = x & z
        u = t & y
        v = (1 ^ x ^ y) & (1 ^ t ^ z)
        w = (1 ^ u ^ v) & y
        assignment = {1:x, 2:y, 3:z}
        def affine_value(form):
            return sum(assignment[term[0]] if term else 1 for term in form) % 2
        for name, left, right in definitions:
            assignment[name] = affine_value(left) & affine_value(right)
        actual = tuple(assignment[name] for name, _, _ in definitions)
        assert actual == (t, u, v, w)
        gate_tables.append(actual)
    columns = list(zip(*gate_tables))
    assert len(set(columns)) == 4 and all(0 in c and 1 in c for c in columns)

    x, y, z = map(var, (1, 2, 3))
    supplied = [opposite(x), y, add(x, y), opposite(add(x, y)), ONE, ZERO, x]
    out, stats = replay(3, cnf, proof, supplied)
    assert stats["rank"] == 2 and stats["branches"] == 4
    assert stats["chosen_factor_coordinates"] == [[0, 1], [0, 2], [1, 3], [0, 2]]
    squares = sum(any(len(t) == 2 and t[0] == t[1] for t in atom) for row in out for atom in row["clause"])
    assert squares > 0
    missing = 0
    for direction in range(2, 16, 2):
        trial = M["AffineBasis"](3, [mask_form(3, direction)])
        reject(lambda: M["gate_cover"](trial, definitions))
        missing += 1
    projections = []
    for n, new_cnf, old_images, menu, expected in (
        (2, [[1], [2], [-1, -2]], [1, 1, 2], [var(1), var(1), ZERO, ONE], 1),
        (1, [[1], [-1]], [2, 2, 1], [ONE, ONE, ZERO], 0),
    ):
        transported = A["backtranslate"](n, new_cnf, 3, cnf, old_images, proof)
        _, collapsed = replay(n, new_cnf, transported, menu)
        assert collapsed["rank"] == expected and collapsed["branches"] == 1 << expected
        assert collapsed["maximum_definition_depth"] == named["maximum_definition_depth"]
        projections.append({"source_variables": n, "projected_named_nodes": len(transported), **collapsed})

    # A valid source with changed multiplier now has a different formal inference result.
    damaged = deepcopy(out)
    pos = next(i for i, row in enumerate(damaged) if row["rule"] == "multiply"
               and mul(Q["polynomial"](row["chosen"]), Q["polynomial"](row["multiplier"])) != ZERO)
    damaged[pos]["multiplier"] = []
    mutation = reject(lambda: Q["verify"](3, cnf, damaged))
    return ({"named_nodes": len(proof), "ordinary_ancestors": len(ancestors),
             "distinct_nonconstant_named_truth_tables": len(set(columns)), "rank_one_spans_excluded": missing,
             "formal_square_occurrences": squares, **stats}, projections, mutation)


def additional_cases():
    x, y, z, payload = map(var, range(1, 5))
    controls = [x, y, z, opposite(add(add(x, y), z))]
    factors = [(controls[0], payload)]
    for i in range(1, 10):
        g = controls[i % len(controls)]
        other = add(var(4 + i), payload)
        factors.append((other, g) if i % 2 else (g, other))
    cnf, proof = old_checks["example"](4, factors)
    _, rank_three = replay(4, cnf, proof, [x, y, z, add(x, y)])
    assert rank_three["branches"] == 8 and rank_three["maximum_definition_depth"] == 10

    repeated = [{"rule":"axiom", "axiom":0, "clause":[]}, {"rule":"true", "clause":[[]]},
                {"rule":"axiom", "axiom":0, "clause":[]}]
    _, empty = replay(0, [[]], repeated, [ZERO, ONE])
    assert empty["branches"] == 1
    cnf0, p0 = old_checks["example"](1, [(ZERO, x), (var(2), ONE)])
    _, constant = replay(1, cnf0, p0, [])
    assert constant["rank"] == 0 and constant["declarations"] == 2

    wide = []
    for width in (1, 257):
        cnf = [[-1], [1]]
        dag = A["Dag"](2, cnf)
        left, right = dag.axiom(0), dag.axiom(1)
        a = dag.weaken(left, [x] + [y] * width)
        b = dag.weaken(right, [opposite(x)] + [y] * width)
        dag.combine(a, b, x, opposite(x))
        dag.resolve(left, right, -1)
        _, result = replay(2, cnf, dag.proof, [x, y])
        wide.append({"side_occurrences": width, "input_nodes": len(dag.proof), "output_nodes": result["nodes"]})
    assert wide[0]["output_nodes"] == wide[1]["output_nodes"]
    return rank_three, empty, constant, wide


def negative_controls():
    cnf, proof = rank_two_example()
    x, y = var(1), var(2)
    invalid = {}
    invalid["uncovered_declaration"] = reject(lambda: M["eliminate"](3, cnf, proof, [x]))
    invalid["fresh_generator"] = reject(lambda: M["eliminate"](3, cnf, proof, [x, var(4)]))
    invalid["quadratic_generator"] = reject(lambda: M["eliminate"](3, cnf, proof, [mul(x, x)]))
    target = next(i for i, row in enumerate(proof) if row["rule"] == "define")
    wrong = deepcopy(proof)
    wrong[target]["variable"] += 1
    invalid["fresh_order"] = reject(lambda: M["eliminate"](3, cnf, wrong, [x, y]))
    wrong = deepcopy(proof)
    wrong[target]["factors"][0] += [[4], [4]]
    invalid["canceled_future_name"] = reject(lambda: M["eliminate"](3, cnf, wrong, [x, y]))
    malformed = [{"rule":"axiom", "axiom":0, "clause":[]},
                 {"rule":"boolean", "variable":1, "clause":[[[1]], [[], [1]]]},
                 {"rule":"axiom", "axiom":0, "clause":[]}]
    invalid["inactive_invalid_boolean_before_empty"] = reject(lambda: M["eliminate"](0, [[]], malformed, []))
    return invalid


def main():
    ranked, projected, mutation = fixture_report()
    three, empty, constant, wide = additional_cases()
    negative = negative_controls()
    negative["wrong_projected_multiplier"] = mutation
    return {"status":"passed", "coordinate_census":test_coordinates(), "guard_deductions":test_guard_equations(),
            "original_rank_two":ranked, "literal_projection_rank_collapse":projected, "rank_three":three,
            "repeated_empty_rank_zero":empty, "constant_factor_rank_zero":constant,
            "width_control":wide, "rejected_controls":negative}


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, indent=2))
