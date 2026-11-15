"""Replace a proof's private conjunction tree and preserve its final-name interface."""
from collections import Counter
from itertools import product
import json
from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[3]
RANK = "AFFINE-FACTOR-RANK-20261115-001C"
prior = runpy.run_path(str(ROOT / "proofs" / RANK / (RANK + "-P001_affine_restrictions") / "solver.py"))
A, B, Q, R = (prior[key] for key in ("named", "bounded", "q", "ranked"))
P = R["prior"]
ZERO, ONE, add, mul, var, poly = (B[k] for k in ("ZERO", "ONE", "add", "mul", "var", "poly"))
opposite = B["opposite"]


def truth(lit):
    return var(lit) if lit > 0 else opposite(var(-lit))


def bit(value):
    return ONE if value else ZERO


def check_inputs(n, inputs):
    if len(inputs) < 2 or any(type(i) is not int or not 1 <= abs(i) <= n for i in inputs):
        raise ValueError("a conjunction needs at least two signed original inputs")
    if len({abs(i) for i in inputs}) != len(inputs):
        raise ValueError("conjunction inputs must have distinct original variables")


def raw_names(raw):
    return {i for term in raw for i in term}


def old_interface(n, cnf, proof, inputs, cut):
    """Validate the complete input and return the old tree and all exported parent rows."""
    A["verify"](n, cnf, proof)
    check_inputs(n, inputs)
    if type(cut) is not int or not 1 <= cut <= len(proof):
        raise ValueError("cut must terminate a nonempty prefix of the proof")
    operands = {truth(lit): lit for lit in inputs}
    subtrees = {lit: frozenset((lit,)) for lit in inputs}
    gates = {}
    for i, row in enumerate(proof[:cut]):
        if row["rule"] != "define":
            continue
        children = []
        for raw in row["factors"]:
            lit = operands.get(poly(raw))
            if lit is None or raw_names(raw) != {abs(lit)}:
                raise ValueError("the old producer must be a literal AND tree on the supplied leaves")
            children.append(lit)
        left, right = children
        if subtrees[left] & subtrees[right]:
            raise ValueError("a leaf occurs twice below an old AND")
        name = row["variable"]
        gates[name] = (name, left, right, i)
        operands[var(name)] = name
        subtrees[name] = subtrees[left] | subtrees[right]
    root = n + len(inputs) - 1
    if len(gates) != len(inputs) - 1 or subtrees.get(root) != frozenset(inputs):
        raise ValueError("prefix does not produce exactly one complete binary AND tree")
    private = set(gates) - {root}
    outgoing = {j for row in proof[cut:] for j in row.get("parents", ()) if j < cut}
    if cut == len(proof):
        outgoing.add(len(proof) - 1)
    for j in outgoing:
        if any(raw_names(raw) & private for raw in proof[j]["clause"]):
            raise ValueError("an imported parent clause reads an old private name")
    for row in proof[cut:]:
        raw = list(A["mentioned_forms"](row))
        if row["rule"] == "define":
            raw.extend(row["factors"])
        if any(raw_names(f) & private for f in raw) or (row["rule"] == "boolean" and row["variable"] in private):
            raise ValueError("a suffix inscription reads an old private name")
    return list(gates.values()), root, sorted(outgoing)


def declare_chain(dag, inputs):
    check_inputs(dag.n, inputs)
    gates = []
    left = inputs[0]
    for right in inputs[1:]:
        name, definition = dag.define(truth(left), truth(right))
        gates.append((name, left, right, definition))
        left = name
    return gates


def and_portals(dag, gates):
    """Given postorder AND definitions, derive all literal clauses for the root AND."""
    if not gates:
        raise ValueError("a product tree needs a root definition")
    upward = {}
    local = {}
    for name, left, right, declaration in gates:
        to_left, to_right, from_both = P["extension_clauses"](dag, name, declaration, left, right)
        local[name] = (to_left, to_right)
        node = from_both
        for child in (left, right):
            if child in upward:
                node = dag.resolve(upward[child], node, child)
        upward[name] = node
    root = gates[-1][0]
    downward = {}
    for name, left, right, _ in reversed(gates):
        for child, implication in zip((left, right), local[name]):
            downward[child] = implication if name == root else dag.resolve(downward[name], implication, name)
    return root, {lit: node for lit, node in downward.items() if lit not in upward}, upward[root]


def chain_portals(dag, inputs):
    """Return root, {signed input: root-implies-input node}, all-inputs-imply-root node."""
    return and_portals(dag, declare_chain(dag, inputs))


def copy_node(dag, row, refs):
    fields = {key: value for key, value in row.items() if key not in ("clause", "rule", "parents")}
    if "parents" in row:
        fields["parents"] = [refs[p] for p in row["parents"]]
    return dag.emit(row["rule"], (poly(raw) for raw in row["clause"]), **fields)


def shared_suffix(n, cnf, proof, inputs, cut, imports):
    out = A["Dag"](n, cnf)
    root, implications, converse = chain_portals(out, inputs)
    seeds = [(Q["signed_clause"]([-root, lit]), "root_implies_input", ref) for lit, ref in implications.items()]
    seeds.append((Q["signed_clause"]([root, *(-lit for lit in inputs)]), "all_imply_root", converse))
    seeds.extend((Q["signed_clause"](clause), "axiom", i) for i, clause in enumerate(cnf))
    seeds.append(((ZERO,), "true", None))
    for v in (*range(1, n + 1), root):
        seeds.append((tuple(sorted((var(v), opposite(var(v))))), "boolean", v))
    seed_bags = [(Counter(seed), seed, kind, value) for seed, kind, value in seeds]
    plan = {}
    todo = list(imports)
    private = set(range(n + 1, root))
    while todo:
        j = todo.pop()
        if j in plan:
            continue
        row = proof[j]
        desired = tuple(sorted(poly(raw) for raw in proof[j]["clause"]))
        bag = Counter(desired)
        if any(raw_names(raw) & private for raw in row["clause"]):
            raise ValueError("public prefix deduction needs an unsupported private premise")
        for count, seed, kind, value in seed_bags:
            if count <= bag:
                plan[j] = (kind, seed, value)
                break
        else:
            if row["rule"] == "define" or not row.get("parents") or any(
                raw_names(raw) & private for raw in A["mentioned_forms"](row)
            ):
                raise ValueError("clean crossing row lacks a supported public derivation")
            plan[j] = ("public_deduction", None, None)
            todo.extend(row["parents"])

    refs = {}
    materialized = {"axiom":out.axiom, "boolean":out.boolean}
    for j in sorted(plan):
        kind, seed, value = plan[j]
        if kind == "public_deduction":
            refs[j] = copy_node(out, proof[j], refs)
            continue
        if kind in materialized:
            ref = materialized[kind](value)
        elif kind == "true":
            ref = out.true()
        else:
            ref = value
        desired = tuple(sorted(poly(raw) for raw in proof[j]["clause"]))
        refs[j] = ref if seed == desired else out.weaken(ref, desired)
    for i in range(cut, len(proof)):
        refs[i] = copy_node(out, proof[i], refs)
    if refs[len(proof) - 1] != len(out.proof) - 1:
        out.weaken(refs[len(proof) - 1], ())
    uses = Counter(plan[i][0] for i in imports)
    return out, {"branches":0, "matched_imports":dict(sorted(uses.items())),
                 "replayed_public_prefix_nodes":sum(kind == "public_deduction" for kind, _, _ in plan.values())}


def case_product(dag, left, right, context):
    """From H,[f+a] and H,[g+b] derive H,[fg+ab] without Boolean reduction."""
    f, a, ef = left
    g, b, eg = right
    selected = add(f, bit(a))
    product_step = dag.multiply(ef, selected, g)
    combined = dag.combine(product_step, eg, mul(selected, g), add(g, bit(b)), 1, a)
    return B["remove_extra_context"](dag, combined, context)


def all_cases(n, cnf, proof, inputs, cut, old_gates, root):
    out = A["Dag"](n, cnf)
    new_gates = declare_chain(out, inputs)
    post_definitions = {}
    for row in proof[cut:]:
        if row["rule"] == "define":
            name, node = out.define(*(poly(f) for f in row["factors"]))
            if name != row["variable"]:
                raise ValueError("post-boundary variable order changed")
            post_definitions[name] = node
    boolean = B["affine_boolean_builder"](out)
    old = {name: (left, right) for name, left, right, _ in old_gates}
    leaves = []
    for bits in product((0, 1), repeat=len(inputs)):
        context, derive = R["guard_equation_builder"](out, tuple(map(truth, inputs)), bits, boolean)
        base_values = {lit: (truth(lit), val, derive(1 << j)[1]) for j, (lit, val) in enumerate(zip(inputs, bits))}
        target_values = dict(base_values)
        for name, left, right, decl in new_gates:
            l, r = target_values[left], target_values[right]
            value = l[1] & r[1]
            fg = mul(l[0], r[0])
            node = case_product(out, l, r, context)
            node = out.combine(node, decl, add(fg, bit(value)), add(var(name), fg))
            target_values[name] = (var(name), value, node)

        images = {v:var(v) for v in range(1, n + 1)}
        old_values = dict(base_values)
        refs = []
        def image(raw):
            return B["affine_image"](raw, images)

        for row in proof:
            kind = row["rule"]
            if kind == "define":
                name = row["variable"]
                if name in old:
                    left, right = old[name]
                    l, r = old_values[left], old_values[right]
                    value = l[1] & r[1]
                    node = case_product(out, l, r, context)
                    if name == root:
                        images[name] = var(root)
                        target, target_value, target_unit = target_values[root]
                        if value != target_value:
                            raise ValueError("the two AND producers disagree")
                        node = out.combine(node, target_unit, add(mul(l[0], r[0]), bit(value)), add(target, bit(value)))
                        node = B["remove_extra_context"](out, node, context)
                    else:
                        images[name] = bit(value)
                        old_values[name] = (images[name], value, derive(0)[1])
                else:
                    images[name] = var(name)
                    node = post_definitions[name]
            elif kind == "axiom":
                node = out.axiom(row["axiom"])
            elif kind == "true":
                node = out.true()
            elif kind == "boolean":
                node = boolean(images[row["variable"]])
            else:
                node = None
            atoms = tuple(image(raw) for raw in row["clause"])
            if node is None:
                node = B["guarded_step"](out, row, refs, image, context, atoms)
            full = tuple(sorted((*atoms, *context)))
            if out.clauses[node] != full:
                if kind not in ("axiom", "true", "boolean") and not (
                    kind == "define" and row["variable"] in post_definitions
                ):
                    raise ValueError("conditional old line has the wrong formal image")
                node = out.weaken(node, full)
            refs.append(node)
        leaves.append((refs[-1], context))

    while len(leaves) > 1:
        merged = []
        for (left, failures), (right, others) in zip(leaves[::2], leaves[1::2]):
            shared, pivot = failures[:-1], failures[-1]
            if others != (*shared, opposite(pivot)):
                raise ValueError("inconsistent case merge")
            merged.append((B["cut"](out, left, right, pivot, shared), shared))
        leaves = merged
    return out, {"branches":1 << len(inputs)}


def proof_bytes(proof):
    return len(json.dumps(proof, separators=(",", ":"), sort_keys=True).encode("utf-8"))


def regroup(n, cnf, proof, inputs, cut, *, mode="portals"):
    """Return a checked proof using a chain in the supplied leaf order and its resource counts."""
    inputs = tuple(inputs)
    old, root, imports = old_interface(n, cnf, proof, inputs, cut)
    if mode == "portals":
        out, extra = shared_suffix(n, cnf, proof, inputs, cut, imports)
    elif mode == "cases":
        out, extra = all_cases(n, cnf, proof, inputs, cut, old, root)
    else:
        raise ValueError("mode must be portals or cases")
    A["verify"](n, cnf, out.proof)
    return out.proof, {
        "mode": mode, "inputs": list(inputs), "root":root, "exported_parent_rows":imports,
        "source_nodes":len(proof), "target_nodes":len(out.proof),
        "source_proof_bytes":proof_bytes(proof), "target_proof_bytes":proof_bytes(out.proof), **extra,
    }
