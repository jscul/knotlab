"""Remove acyclic product names from a well-formed proof by branching on one factor."""
from functools import cache
from itertools import product
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[3]
BASE_ID = "QUADRATIC-ROUTE-TRANSFER-20261115-001A"
BASE = runpy.run_path(str(ROOT / "proofs" / BASE_ID / (BASE_ID + "-P001_quadratic_substitution") / "solver.py"))
ZERO, ONE = BASE["ZERO"], BASE["ONE"]
add, mul, var, poly = (BASE[name] for name in ("add", "mul", "var", "polynomial"))


def opposite(f):
    return add(f, ONE)


def affine_image(raw, images):
    """The substitution is simultaneous, including formal powers and the constant term."""
    result = ZERO
    for monomial in poly(raw):
        term = ONE
        for i in monomial:
            term = mul(term, images[i])
        result = add(result, term)
    return result


def remove_extra_context(dag, node, context):
    # Contract exactly the extra occurrences. Other multiplicities belong to the proof.
    for atom in context:
        node = dag.contract(node, atom)
    return node


def cut(dag, left, right, pivot, context):
    """Cut complementary equations under identical multiset contexts."""
    node = dag.combine(left, right, pivot, opposite(pivot))
    node = remove_extra_context(dag, dag.delete_false(node), context)
    if dag.clauses[node] != tuple(sorted(context)):
        raise ValueError("case merge produced a different context")
    return node


def boolean_gate(dag, f, ef, g, eg, *, product_gate):
    """From Boolean disjunctions for f and g derive one for f+g or fg."""
    target = mul(f, g) if product_gate else add(f, g)
    target_pair = (target, opposite(target))
    by_first = []
    for i in (0, 1):
        selected_f = opposite(f) if i else f
        failed_f = opposite(selected_f)
        branches = []
        for j in (0, 1):
            selected_g = opposite(g) if j else g
            if product_gate:
                multiplied = dag.multiply(ef, selected_f, g)
                node = dag.combine(multiplied, eg, mul(selected_f, g), selected_g, 1, i)
            else:
                node = dag.combine(ef, eg, selected_f, selected_g)
            branches.append(dag.weaken(node, (*target_pair, failed_f, opposite(selected_g))))
        by_first.append(cut(dag, branches[0], branches[1], opposite(g), (*target_pair, failed_f)))
    return cut(dag, by_first[0], by_first[1], opposite(f), target_pair)


def affine_boolean_builder(dag):
    """Construct excluded middle for an affine form from variable axioms."""
    @cache
    def get(f):
        if any(len(term) > 1 for term in f):
            raise ValueError("an affine form is required")
        variables = [term[0] for term in f if term]
        if not variables:
            return dag.weaken(dag.true(), (ZERO, ONE))
        current = var(variables[0])
        node = dag.boolean(variables[0])
        for variable in variables[1:]:
            g = var(variable)
            node = boolean_gate(dag, current, node, g, dag.boolean(variable), product_gate=False)
            current = add(current, g)
        # Adding the constant 1 exchanges the two occurrences in a multiset.
        return node
    return get


def guarded_step(dag, row, refs, image, context, target):
    """Replay an ordinary primitive inference after substitution under one disjunction."""
    rule = row["rule"]
    parents = [refs[i] for i in row["parents"]]
    if rule == "weaken":
        return dag.weaken(parents[0], (*target, *context))
    if rule == "contract":
        return dag.contract(parents[0], image(row["chosen"]))
    if rule == "delete_false":
        return dag.delete_false(parents[0])
    if rule == "multiply":
        return dag.multiply(parents[0], image(row["chosen"]), image(row["multiplier"]))
    if rule == "combine":
        f, g = map(image, row["chosen"])
        node = dag.combine(*parents, f, g, *row["coefficients"])
        return remove_extra_context(dag, node, context)
    raise ValueError("unexpected deduction rule: " + rule)


def declarations(n, proof):
    result = []
    available = n
    for row in proof:
        if row["rule"] == "define":
            if row.get("parents") or row["variable"] != available + 1 or len(row["factors"]) != 2:
                raise ValueError("invalid product declaration")
            f, g = (poly(raw, available) for raw in row["factors"])
            if any(len(term) > 1 for term in f + g):
                raise ValueError("a product factor is not affine")
            available += 1
            if tuple(poly(raw, available) for raw in row["clause"]) != (add(var(available), mul(f, g)),):
                raise ValueError("definition does not display the declared product equation")
            result.append((available, f, g))
        if row["rule"] == "boolean" and not 1 <= row["variable"] <= available:
            raise ValueError("variable Boolean axiom before availability")
        for raw in row["clause"]:
            BASE["checked_poly"](raw, available)
    return result


def eliminate(n, cnf, proof):
    """Convert a well-formed multiset proof, returning an independently verifiable base DAG."""
    definitions = declarations(n, proof)
    count = len(definitions)
    if not proof or proof[-1]["clause"]:
        raise ValueError("a refutation must end in the empty disjunction")
    dag = BASE["Dag"](cnf)
    boolean = affine_boolean_builder(dag)
    leaves = []
    for bits in product((0, 1), repeat=count):
        images = {v: var(v) for v in range(1, n + 1)}
        context = []
        definition_images = {}
        for (v, raw_f, raw_g), bit in zip(definitions, bits):
            f = affine_image(raw_f, images)
            g = affine_image(raw_g, images)
            images[v] = g if bit else ZERO
            selected = opposite(f) if bit else f
            definition_images[v] = (f, selected, g)
            context.append(opposite(selected))
        refs = []
        def image(raw):
            return affine_image(raw, images)
        for index, row in enumerate(proof):
            rule = row["rule"]
            if any(type(i) is not int or not 0 <= i < index for i in row.get("parents", [])):
                raise ValueError("invalid parent reference")
            target = [image(f) for f in row["clause"]]
            if rule in ("define", "axiom", "true", "boolean"):
                if rule == "define":
                    f, selected, g = definition_images[row["variable"]]
                    node = dag.multiply(boolean(f), selected, g)
                elif rule == "axiom":
                    node = dag.axiom(row["axiom"])
                elif rule == "true":
                    node = dag.true()
                else:
                    node = boolean(images[row["variable"]])
                full = tuple(sorted((*target, *context)))
                if dag.clauses[node] != full:
                    node = dag.weaken(node, full)
            else:
                node = guarded_step(dag, row, refs, image, context, target)
            if dag.clauses[node] != tuple(sorted((*context, *target))):
                raise ValueError("the replayed deduction has a different image")
            refs.append(node)
        leaves.append((refs[-1], tuple(context)))
    while len(leaves) > 1:
        next_level = []
        for (left, a), (right, b) in zip(leaves[::2], leaves[1::2]):
            if a[:-1] != b[:-1] or opposite(a[-1]) != b[-1]:
                raise ValueError("inconsistent branch split")
            next_level.append((cut(dag, left, right, a[-1], a[:-1]), a[:-1]))
        leaves = next_level
    BASE["verify"](n, cnf, dag.proof)
    return dag.proof, {"declarations": count, "branches": 1 << count, "nodes": len(dag.proof)}
