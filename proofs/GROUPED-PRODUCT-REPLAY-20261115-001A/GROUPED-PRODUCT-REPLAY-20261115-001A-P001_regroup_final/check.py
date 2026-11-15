"""Check literal interfaces, strict refutations, raw scope, and the four-bit affine partitions."""
from copy import deepcopy
import argparse
from functools import cache
import hashlib
from itertools import product
import json
from pathlib import Path
import runpy


HERE = Path(__file__).resolve().parent
M = runpy.run_path(str(HERE / "solver.py"))
A, Q, P = (M[k] for k in ("A", "Q", "P"))
ZERO, ONE, add, mul, var, poly, truth, opposite = (M[k] for k in ("ZERO","ONE","add","mul","var","poly","truth","opposite"))


def strict_fixture(inputs, *, nonlinear=False, private_history=False, raw_crossing=False):
    """Make a strict ternary formula and a balanced-tree proof that uses its output AND."""
    k = len(inputs)
    assert k >= 3 and {abs(l) for l in inputs} == set(range(1, k + 1))
    pad1, pad2 = k + 1, k + 2
    cnf = [[lit, i * pad1, j * pad2] for lit in inputs for i, j in product((1,-1), repeat=2)]
    split = list(range(k + 3, 2 * k))
    opposite_clause = [-v for v in inputs]
    if not split:
        cnf.append(opposite_clause)
    else:
        cnf.append([*opposite_clause[:2], split[0]])
        for j in range(1, len(split)):
            cnf.append([-split[j-1], opposite_clause[j+1], split[j]])
        cnf.append([-split[-1], *opposite_clause[-2:]])
    n = 2 * k - 1
    assert all(len(row) == len({abs(x) for x in row}) == 3 for row in cnf)
    dag = A["Dag"](n, cnf)
    work = list(inputs)
    old = []
    while len(work) > 1:
        new = []
        for i in range(0, len(work) - 1, 2):
            left, right = work[i:i+2]
            name, ref = dag.define(truth(left), truth(right))
            old.append((name,left,right,ref))
            new.append(name)
        if len(work) % 2:
            new.append(work[-1])
        work = new
    root, down, up = M["and_portals"](dag, old)
    root_form, first = var(root), truth(inputs[0])
    cross_fact = None
    private_unit = None
    if nonlinear:
        bad_value = opposite(first)
        node = dag.multiply(down[inputs[0]], root_form, bad_value)
        node = dag.multiply(node, bad_value, root_form)
        cross_fact = dag.contract(node, mul(root_form, bad_value))
    if private_history:
        bad_value = opposite(first)
        left = dag.resolve(dag.axiom(0), dag.axiom(1), pad2)
        right = dag.resolve(dag.axiom(2), dag.axiom(3), pad2)
        base_unit = dag.resolve(left, right, pad1)
        private = var(old[1][0])
        m1 = dag.multiply(base_unit, bad_value, private)
        m2 = dag.multiply(base_unit, bad_value, opposite(private))
        restored = dag.combine(m1, m2, mul(bad_value, private), mul(bad_value, opposite(private)))
        zero = dag.multiply(dag.true(), ZERO, mul(private, private))
        private_unit = dag.combine(zero, restored, ZERO, bad_value)
    if raw_crossing:
        cross_true = dag.emit("true", (ZERO,))
    cut = len(dag.proof)

    units = {}
    for index, lit in enumerate(inputs):
        if index == 0 and private_unit is not None:
            units[lit] = private_unit
            continue
        u, v, w, z = (dag.axiom(4 * index + j) for j in range(4))
        u = dag.resolve(u, v, pad2)
        w = dag.resolve(w, z, pad2)
        units[lit] = dag.resolve(u, w, pad1)
    rt = up
    for lit in inputs:
        rt = dag.resolve(units[lit], rt, lit)
    # Nonlinear suffix work on the common output, including a formal square.
    asserted = opposite(root_form)
    s1 = dag.multiply(rt, asserted, root_form)
    s2 = dag.multiply(rt, asserted, asserted)
    rt = dag.combine(s1, s2, mul(asserted, root_form), mul(asserted, asserted))
    if raw_crossing:
        t = dag.multiply(cross_true, ZERO, first)
        rt = dag.combine(t, rt, ZERO, asserted)
    later, definition = dag.define(root_form, first)
    first_step = dag.multiply(rt, asserted, first)
    both = dag.combine(first_step, units[inputs[0]], mul(asserted, first), opposite(first))
    later_unit = dag.combine(both, definition, opposite(mul(root_form,first)), add(var(later), mul(root_form,first)))
    root_again, _, _ = P["extension_clauses"](dag, later, definition, root, inputs[0])
    asserted_root = dag.resolve(later_unit, root_again, later)
    recovered = {}
    for lit in inputs:
        if nonlinear and lit == inputs[0]:
            comp = opposite(first)
            complementary_product = dag.multiply(asserted_root, asserted, comp)
            recovered[lit] = dag.combine(complementary_product, cross_fact, mul(asserted, comp), mul(root_form, comp))
        else:
            recovered[lit] = dag.resolve(asserted_root, down[lit], root)
    negative = dag.axiom(4 * k)
    for j, aux in enumerate(split, 1):
        negative = dag.resolve(negative, dag.axiom(4 * k + j), aux)
    for lit in inputs:
        negative = dag.resolve(recovered[lit], negative, lit)
    assert negative == len(dag.proof) - 1 and not dag.clauses[negative]
    if raw_crossing:
        hidden = old[0][0]
        dag.proof[cross_true]["clause"] = [[[hidden], [hidden]]]
    A["verify"](n, cnf, dag.proof)
    return n, cnf, dag.proof, cut


def check_truth(n, cnf, proof, assignments):
    """Interpret each original row, chronological definition, and deduction independently."""
    universe = (1 << len(assignments)) - 1
    columns = {v:sum(1 << j for j, point in enumerate(assignments) if point >> (v-1) & 1) for v in range(1,n+1)}
    @cache
    def evaluate(f):
        value = 0
        for monomial in f:
            term = universe
            for v in monomial:
                term &= columns[v]
            value ^= term
        return value
    rows = []
    defined = []
    for row in proof:
        kind = row["rule"]
        if kind == "define":
            v = row["variable"]
            f, g = (poly(raw) for raw in row["factors"])
            columns[v] = evaluate(f) & evaluate(g)
            defined.append(columns[v])
        meaning = 0
        for raw in row["clause"]:
            meaning |= universe ^ evaluate(poly(raw))
        if kind == "axiom":
            expected = 0
            for lit in cnf[row["axiom"]]:
                expected |= columns[abs(lit)] if lit > 0 else universe ^ columns[-lit]
            assert meaning == expected
        elif not row.get("parents"):
            assert meaning == universe
        else:
            antecedents = universe
            for j in row["parents"]:
                antecedents &= rows[j]
            assert antecedents & (universe ^ meaning) == 0
        rows.append(meaning)
    assert rows[-1] == 0
    return defined


def reject(fn, text):
    try:
        fn()
    except ValueError as exc:
        assert text in str(exc), str(exc)
        return str(exc)
    raise AssertionError("invalid control accepted")


def assignments_for(n):
    if n <= 9:
        return list(range(1 << n))
    # Include the all-ones and zero vertices and fixed reproducible inputs on the larger cubes.
    m = (1 << n) - 1
    return list(dict.fromkeys([0,m,*((j * 2654435761) & m for j in range(192))]))


def private_functions(proof, inputs):
    # A product of independent, distinct signed literals is determined by its exact leaf set.
    known = {truth(lit):frozenset([lit]) for lit in inputs}
    groups = []
    for row in proof:
        if row["rule"] == "define":
            f, g = (poly(raw) for raw in row["factors"])
            group = known[f] | known[g]
            known[var(row["variable"])] = group
            groups.append(group)
            if len(groups) == len(inputs)-1:
                break
    return set(groups[:-1])


def inspect_fixture(inputs, order, mode, nonlinear=False, private_history=False):
    n, cnf, proof, cut = strict_fixture(inputs, nonlinear=nonlinear, private_history=private_history)
    out, stats = M["regroup"](n, cnf, proof, order, cut, mode=mode)
    examples = assignments_for(n)
    old = check_truth(n, cnf, proof, examples)
    new = check_truth(n, cnf, out, examples)
    k = len(inputs)
    assert old[k-2:] == new[k-2:]
    if mode == "portals":
        matched = stats["matched_imports"]
        assert matched["root_implies_input"] == k-int(nonlinear) and matched["all_imply_root"] == 1
        assert set(matched) <= {"root_implies_input","all_imply_root","boolean","public_deduction"}
        if nonlinear:
            assert matched["public_deduction"] == 1 and stats["replayed_public_prefix_nodes"] == 3
        assert len(out) < 100 * (len(proof)+k)
    else:
        assert stats["branches"] == 1 << k and len(out) < 100 * (1 << k) * (k+1) * (len(proof)+k)
    identical = len(private_functions(proof, inputs) & private_functions(out, order))
    if n <= 9:
        assert identical == len(set(old[:k-2]) & set(new[:k-2]))
    if nonlinear:
        root_atom = var(n+k-1)
        portal = mul(root_atom, opposite(truth(inputs[0])))
        assert any(tuple(poly(f) for f in proof[j]["clause"]) == (portal,) for j in stats["exported_parent_rows"])
    if private_history:
        reject(lambda: M["regroup"](n,cnf,proof,order,cut,mode="portals"), "public derivation")
        hidden_square = mul(var(n+2), var(n+2))
        positions = [i for i, row in enumerate(proof[:cut]) if row["rule"]=="multiply"
                     and poly(row["chosen"])==ZERO and poly(row["multiplier"])==hidden_square]
        assert len(positions) == 1 and positions[0] in A["ancestors"](n, cnf, proof, include_declarations=False)
        reject(lambda: M["regroup"](n,cnf,proof,order,positions[0],mode="cases"), "old private name")
    return out, {"arity":k, "strict_clauses":len(cnf), "source_originals":n,
                 "truth_assignments":len(examples), "shared_old_private_functions":identical,
                 "nonlinear_boundary":nonlinear,"private_history_exported":private_history, **stats}


def detect_raw_leaks():
    inputs = [1,2,3,4]
    n, cnf, proof, cut = strict_fixture(inputs)
    hidden = n+2
    def attempt(rows, marker, boundary=cut):
        A["verify"](n, cnf, rows)
        return reject(lambda: M["regroup"](n,cnf,rows,inputs,boundary,mode="cases"),marker)
    bad = deepcopy(proof)
    i = len(bad)
    bad.extend([{"rule":"true", "clause":[[]]},
                {"rule":"multiply", "parents":[i], "chosen":[], "multiplier":[[hidden,hidden]], "clause":[[]]},
                {"rule":"weaken","parents":[i-1],"clause":[]}])
    multiplier = attempt(bad, "suffix inscription")
    signaled = deepcopy(proof)
    late = next(j for j,row in enumerate(signaled[cut:],cut) if row["rule"] == "define")
    signaled[late]["factors"][0].extend([[hidden],[hidden]])
    gate = attempt(signaled, "suffix inscription")
    _, _, raw, rc = strict_fixture(inputs, raw_crossing=True)
    crossing = attempt(raw, "imported parent", rc)
    wrong_tree = reject(lambda: M["regroup"](n,cnf,proof,[1,2,3,-4],cut), "literal AND tree")
    wrong_cut = reject(lambda: M["regroup"](n,cnf,proof,inputs,2), "complete binary AND tree")

    # Changing the target clause's formal root square produces a different inference.
    result, _ = M["regroup"](n,cnf,proof,inputs,cut)
    bad_target = deepcopy(result)
    pos = next(j for j,row in enumerate(bad_target) if row["rule"]=="multiply" and
               any(len(term)==2 and term[0]==term[1] for atom in row["clause"] for term in atom))
    bad_target[pos]["multiplier"] = []
    wrong_deduction = reject(lambda: A["verify"](n,cnf,bad_target), "formal rule")
    return {"hidden_square_multiplier":multiplier, "canceled_late_factor":gate,
            "raw_imported_parent":crossing, "wrong_signed_input":wrong_tree, "incomplete_tree":wrong_cut,
            "broken_formal_inference":wrong_deduction}


def affine_part_counts():
    n = 4
    cube = range(1 << n)
    linear = {frozenset([0])}
    pending = list(linear)
    while pending:
        v = pending.pop()
        for u in cube:
            new = v | frozenset(x ^ u for x in v)
            if new not in linear:
                linear.add(new)
                pending.append(new)
    parts = {frozenset(x ^ u for x in v) for v in linear for u in cube}
    tables = []
    for pt in cube:
        a,x,b,y = [(pt >> j) & 1 for j in range(n)]
        tables.append((a*x,b*y,a*x*b*y,a*x*b,a*b))
    def affine(part, f):
        o = next(iter(part))
        return all(tables[x][f] ^ tables[y][f] ^ tables[o][f] ^ tables[x^y^o][f] == 0 for x in part for y in part)
    def minimum(indices):
        possible = [sum(1 << v for v in p) for p in parts if all(affine(p, i) for i in indices)]
        @cache
        def cover(mask):
            if mask == 0:
                return 0
            lowest = mask & -mask
            return 1+min(cover(mask^p) for p in possible if p & lowest and p & mask == p)
        return cover((1<<16)-1)
    result = {"affine_parts":len(parts),"balanced_all_names":minimum([0,1,2]),
              "first_pair_retained_chain":minimum([0,3,2]),"crossed_chain":minimum([4,3,2]),
              "final_function_only":minimum([2])}
    assert list(result.values()) == [307,5,4,4,4]
    return result


def sample_rewrite():
    inputs, order = [1,2,3,4], [1,3,2,4]
    n, cnf, original, cut = strict_fixture(inputs)
    target, stats = M["regroup"](n,cnf,original,order,cut)
    specified, specified_stats = M["regroup"](n,cnf,original,inputs,cut)
    return {"original_variables":n, "cnf":cnf, "source_leaf_order":inputs, "target_chain_order":order,
            "specified_chain_order":inputs, "cut":cut, "mode":"portals", "statistics":stats,
            "specified_chain_statistics":specified_stats, "old_proof":original,
            "new_proof":target, "specified_chain_proof":specified}


def sample_bytes(sample):
    # Put each checked node on one physical line so a reader can follow zero-based references.
    fields = []
    compact = lambda obj: json.dumps(obj, separators=(",",":"), sort_keys=True)
    for k, v in sample.items():
        encoded = "[\n    "+",\n    ".join(compact(row) for row in v)+"\n  ]" if k.endswith("_proof") else compact(v)
        fields.append("  "+json.dumps(k)+": "+encoded)
    return ("{\n"+",\n".join(fields)+"\n}\n").encode()


def main():
    old_order, crossed = [1,2,3,4], [1,3,2,4]
    results = []
    for order in (old_order, crossed):
        _, facts = inspect_fixture(old_order, order, "portals")
        assert facts["shared_old_private_functions"] == (1 if order == old_order else 0)
        results.append(facts)
    _, arbitrary = inspect_fixture(old_order, crossed, "cases", nonlinear=True, private_history=True)
    assert arbitrary["shared_old_private_functions"] == 0
    larger = []
    for k in (5, 8, 12):
        signed = [j if j % 3 else -j for j in range(1,k+1)]
        _, case = inspect_fixture(signed, signed[::2]+signed[1::2], "portals")
        larger.append(case)
    _, quadratic = inspect_fixture([1,2,3,4,5], [2,4,1,3,5], "portals", nonlinear=True)
    recorded = (HERE/"rewrite.json").read_bytes()
    sample = sample_rewrite()
    assert recorded == sample_bytes(sample)
    pruned = {}
    for which in ("old_proof", "new_proof", "specified_chain_proof"):
        rows = sample[which]
        n, cnf = sample["original_variables"], sample["cnf"]
        ancestors = set(A["ancestors"](n, cnf, rows, include_declarations=False))
        assert all(i in ancestors for i, row in enumerate(rows) if row["rule"] == "define")
        reduced = P["prune"](n, cnf, rows)
        assert A["verify"](n, cnf, reduced)["lines"] == len(ancestors) == 142
        pruned[which] = len(reduced)
    return {"status":"passed", "recorded_rewrite_sha256":hashlib.sha256(recorded).hexdigest(),
            "pruned_stored_rewrite_nodes":pruned,
            "original_four_portal_replays":results,
            "arbitrary_quadratic_boundary":arbitrary, "scalable_signed_inputs":larger,
            "public_quadratic_derivation":quadratic,
            "rejected_controls":detect_raw_leaks(), "optimal_affine_parts":affine_part_counts()}


if __name__=="__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--write-example", action="store_true")
    if cli.parse_args().write_example:
        (HERE/"rewrite.json").write_bytes(sample_bytes(sample_rewrite()))
    print(json.dumps(main(), sort_keys=True, indent=2))
