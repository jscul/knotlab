#!/usr/bin/env python3
"""Replay quadratic rule transport, or translate/verify a supplied JSON certificate."""

import argparse
import json
import os
import runpy
import sys
from collections import Counter
from copy import deepcopy
from functools import cache
from itertools import product
from pathlib import Path

FAMILY = Path(__file__).resolve().parent
ROOT = FAMILY.parents[2]
sys.path.insert(0, str(FAMILY))
import solver as q


def extra_premise(dag, ref, extra):
    """Use the extra parent in the ancestry of ref's next occurrence."""
    original = dag.clauses[ref]
    target = tuple(sorted(set(original) | set(dag.clauses[extra])))
    current = dag.weaken(dag.contract_all(extra), target)
    for f in sorted(set(target) - set(original)):
        opposite = q.add(q.ONE, f)
        other = dag.weaken(ref, (*original, opposite))
        current = dag.contract_all(dag.delete_false(dag.combine(current, other, f, opposite)))
    q.require(dag.clauses[current] == original, "failed to rejoin the extra proof branch")
    return current


def nonlinear_fixture(convention):
    source = [[1, 2], [-1], [-2]]
    cnf = [[1, -2], [-1], [2], [1, -3, 6], [1, 5], [1, 3, -2, 6]]
    images = [1, -2, 1, -1, 3, -3]
    dag = q.Dag(cnf, convention=convention)
    current = dag.axiom(0)
    f = q.literal(1)
    h = q.add(q.var(2), q.var(3))
    other = q.add(q.ONE, h)
    left = dag.multiply(current, f, h)
    right = dag.multiply(current, f, other)
    current = dag.contract_all(dag.combine(left, right, q.mul(f,h), q.mul(f,other)))
    # F2's zero scalars are legitimate, even for zero and unit multipliers.
    for alpha, beta in ((0,0), (0,1), (1,0)):
        extra = dag.combine(dag.true(), dag.true(), q.ZERO, q.ZERO, alpha, beta)
        current = extra_premise(dag, current, extra)
    for extra in (dag.axiom(3), dag.axiom(4), dag.axiom(5), dag.boolean(2), dag.boolean(5)):
        current = extra_premise(dag, current, extra)
    alias = dag.weaken(current, [*dag.clauses[current], q.literal(3)])
    extra = dag.multiply(alias, f, q.var(3))
    current = extra_premise(dag, current, extra)
    dag.resolve(dag.resolve(current, dag.axiom(1), 1), dag.axiom(2), -2)
    return (2,source,6,cnf,images,dag.proof)


def evaluate(f, assignment, field_product):
    value = 0
    for term in f:
        v = 1
        for i in term:
            v = field_product(v, assignment[i-1])
        value ^= v
    return value


def check_boolean_steps(n, cnf, proof):
    for assignment in product((0,1), repeat=n):
        values = []
        for step in proof:
            value = any(evaluate(f, assignment, int.__mul__) == 0 for f in step["clause"])
            if step["rule"] == "axiom":
                original = cnf[step["axiom"]]
                q.require(value == any((assignment[abs(v)-1] == int(v>0)) for v in original), "axiom truth mismatch")
            else:
                q.require(value or not all(values[i] for i in step.get("parents", [])), "truth check failed")
            values.append(value)
    return len(proof) * (1 << n)


@cache
def gf4(a,b):
    # Polynomial bits in F2[t]/(t^2+t+1).
    value = 0
    for k in range(2):
        if (b >> k) & 1:
            value ^= a << k
    return value ^ 7 if value & 4 else value


def field_census():
    basis = ((), (1,), (2,), (1,1), (1,2), (2,2))
    forms = [q.polynomial(t for i,t in enumerate(basis) if mask & (1<<i)) for mask in range(64)]
    all_states = list(product(range(4), repeat=2))
    values = {f: tuple(evaluate(f, a, gf4) for a in all_states) for f in forms}
    q.require(len(set(values.values())) == 64 and gf4(2,2) != 2, "field control lost formal squares")
    pairs = [(f,g,q.mul(f,g)) for f,g in product(forms,repeat=2)]
    low = [(f,g,h) for f,g,h in pairs if all(len(t) <= 2 for t in h)]
    counts = Counter()
    for images in product((-3,-2,-1,1,2,3), repeat=2):
        subst = q.substitution(2, images)
        image = {f: subst(f) for f in forms}
        for k, state in enumerate(all_states):
            induced = tuple((int(v>0) if abs(v)==3 else state[abs(v)-1] ^ int(v<0)) for v in images)
            j = all_states.index(induced)
            q.require(all(values[image[f]][k] == values[f][j] for f in forms), "wrong signed formal image")
            counts["field_point_polynomial_images"] += len(forms)
        for f,g,h in low:
            q.require(image[h] == q.mul(image[f],image[g]), "legal product failed to commute")
        for f,g in product(forms,repeat=2):
            q.require(image[q.add(f,g)] == q.add(image[f],image[g]), "binary addition failed to commute")
        counts["legal_products"] += len(low)
        counts["binary_sums"] += len(forms)**2
        counts["signed_maps"] += 1
    return dict(counts, distinct_formal_polynomials=len(forms), extension_field_order=4)


def larger_field_control():
    basis = [(),(1,),(2,),(3,),*((i,j) for i in (1,2,3) for j in range(i,4))]
    forms = [q.polynomial(t for i,t in enumerate(basis) if bits & (1<<i)) for bits in range(1<<len(basis))]
    states = list(product(range(4), repeat=3))
    values = {f: tuple(evaluate(f,a,gf4) for a in states) for f in forms}
    q.require(len(set(values.values())) == len(forms), "larger field failed to separate formal polynomials")
    maps = [(3,-2,1),(-1,1,-1),(4,-4,4),(-4,2,-1),(2,-3,2)]
    for signed in maps:
        projected = q.substitution(3,signed)
        indices = [states.index(tuple(int(v>0) if abs(v)==4 else s[abs(v)-1] ^ int(v<0)
                                      for v in signed)) for s in states]
        for f in forms:
            q.require(values[projected(f)] == tuple(values[f][j] for j in indices),
                      "three-name formal image disagrees on F4")
    return {"formal_polynomials":len(forms),"signed_maps":len(maps),"points_per_map":len(states),
            "point_value_checks":len(forms)*len(states)*len(maps)}


def wide(n):
    # Both premises have the same long side context. It stays doubled inside
    # the actual binary rule. No charge for contracting it arises in transport.
    zero, f = q.ZERO, q.literal(1)
    cnf = [[1],[-1]]
    dag = q.Dag(cnf)
    base = dag.axiom(0)
    linear = [q.polynomial(((i+1,) for i in range(n) if bits & (1<<i))) for bits in range(1<<n)]
    side = [q.add(h,q.mul(q.var(n),q.var(n))) for h in linear]
    l = dag.weaken(base, [f,*side])
    r = dag.weaken(base, [f,*side])
    joined = dag.combine(l,r,f,f)
    q.require(len(dag.clauses[joined]) == 2*(1<<n)+1 and zero in dag.clauses[joined],
              "wide multiset contexts were silently contracted")
    # There is no requirement that unused nodes be pruned. Keep the long
    # shared context separate from the unbounded-width *axiom* repair below.
    dag.resolve(base, dag.axiom(1), 1)
    images = [1, *([-1] * (n-1))]
    out, stats = q.translated(1, cnf, n, cnf, images, dag.proof)
    q.require(stats["source"]["lines"] == stats["target"]["lines"] and
              stats["source"]["max_width"] == stats["target"]["max_width"], "width caused extra source nodes")
    # A live input-axiom control: a target clause has a true letter
    # only after substitution. Its entire raw image needs just one weakening.
    axioms = [[1],[-1],[n, *range(1,n+1)]]
    repair = q.Dag(axioms)
    recovered = extra_premise(repair, repair.axiom(0), repair.axiom(2))
    repair.resolve(recovered, repair.axiom(1), 1)
    _, live = q.translated(1,cnf,n,axioms,[1]+[2]*(n-1),repair.proof)
    return {"variables": n, "widest_inference": len(dag.clauses[joined]),
            "target_nodes": len(dag.proof), "source_nodes":len(out), "wide_initial_axiom_arity":len(axioms[-1]),
            "initial_repair_weakenings":live["repairs"]["axiom_weakening"]}


def live_width(k):
    names = list(range(1,k+1))
    choice = k+1
    cnf = [[*names,choice],[*names,-choice],*[[-v] for v in names]]
    dag = q.Dag(cnf)
    left, right = dag.axiom(0), dag.axiom(1)
    merged = dag.combine(left,right,q.literal(choice),q.literal(-choice))
    current = dag.contract_all(dag.delete_false(merged))
    for i in names:
        current = dag.resolve(current,dag.axiom(i+1),i)
    source = [[1,2],[1,-2],[-1]]
    out, stats = q.translated(2,source,choice,cnf,[*([1]*k),2],dag.proof)
    q.require(stats["source"]["rules"]["contract"] == stats["target"]["rules"]["contract"] == k and
              stats["source"]["max_width"] == stats["target"]["max_width"] == 2*k+1,
              "width-dependent implicit contraction in live contexts")
    q.require(check_boolean_steps(2,source,out) == 4*len(out), "wide source transcript invalid")
    return {"context_width":k,"widest_live_inference":2*k+1,"target_nodes":len(dag.proof),
            "source_nodes":len(out),"explicit_contractions_each":k}


def controls():
    source = [[1],[-1]]
    dag = q.Dag(source)
    first = dag.axiom(1)
    second = dag.multiply(first,q.var(1),q.var(1))
    sq = q.mul(q.var(1), q.var(1))
    dag.resolve(dag.axiom(0), first, 1)
    rejected = []

    def reject(name, fn):
        try:
            fn()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("missed negative control " + name)

    def replacement(name, update):
        wrong = deepcopy(dag.proof)
        wrong[second] = {**wrong[second], **update}
        reject(name, lambda: q.verify(1, source, wrong))

    replacement("boolean_squaring_is_not_formal_equality", {"clause":[q.encode(q.var(1))]})
    replacement("disallowed_quadratic_semantic_weakening", {"rule":"weaken"})
    replacement("cubic_product_hidden_by_boolean_evaluation", {"multiplier":q.encode(sq)})
    replacement("arbitrary_boolean_tautology_is_not_default", {"rule":"true","parents":[],
                "clause":[q.encode(q.add(sq,q.var(1)))]})
    replacement("unlicensed_forward_parent", {"parents":[len(dag.proof)]})
    replacement("spurious_contraction", {"rule":"contract","chosen":q.encode(q.var(1))})
    wrong_constant = q.Dag(source)
    current = wrong_constant.axiom(0)
    false_on_bits = q.add(q.ONE,q.add(sq,q.var(1)))
    parent = wrong_constant.weaken(current,[q.literal(1),false_on_bits])
    wrong_constant.emit("delete_false",(q.literal(1),),parents=[parent])
    wrong_constant.resolve(current,wrong_constant.axiom(1),1)
    reject("boolean_false_polynomial_is_not_a_formal_false_constant",
           lambda:q.verify(1,source,wrong_constant.proof))
    bad = q.Dag([[1,2],[-1],[-2]])
    initial = bad.axiom(0)
    mixed = bad.combine(initial,initial,q.literal(1),q.literal(1))
    bad.resolve(bad.resolve(initial,bad.axiom(1),1),bad.axiom(2),2)
    false_set = deepcopy(bad.proof)
    false_set[mixed]["clause"] = [q.encode(p) for p in sorted(set(bad.clauses[mixed]))]
    reject("binary_contexts_silently_deduplicated",lambda:q.verify(2,bad.cnf,false_set))
    reject("unused_nonaxiom_image",lambda:q.backtranslate(2,source,2,[*source,[1,2]],[1,2],dag.proof))
    reject("one_substitution_missing_a_name",lambda:q.backtranslate(2,source,2,source,[1],dag.proof))
    reject("target_rule_may_not_be_repaired_only_after_projection",
           lambda:q.backtranslate(1,[],1,source,[2],[*dag.proof[:second],
               {**dag.proof[second],"clause":[q.encode(q.var(1))]},*dag.proof[second+1:]]))
    return rejected


def unusual_inputs():
    dags = {}
    raw = q.Dag([[1],[-1]])
    raw.resolve(raw.axiom(0),raw.axiom(1),1)
    _, s = q.translated(1,[[1,1,1],[-1]],1,raw.cnf,[1],raw.proof)
    q.require(s["repairs"]["source_duplicate_contractions"] == 2, "uncounted duplicate input contractions")
    dags["duplicate_source_axiom"] = s
    base = q.Dag([[]])
    base.axiom(0)
    base.true()
    base.proof.append(base.proof[0].copy())
    out, stats = q.translated(0,[[]],0,[[]],[],base.proof)
    q.require(out[-1]["clause"] == [], "shared empty axiom lost its final occurrence")
    dags["cached_empty_final"] = stats
    # With a set convention a side may explicitly retain the selected atom.
    # The source constructs a strict canonical step and, if necessary, weakens.
    retained = q.Dag([[1],[-1]], convention="set")
    start = retained.axiom(0)
    mid = retained.multiply(start,q.literal(1),q.var(2))
    retained.proof[mid]["clause"].append(q.encode(q.literal(1)))
    retained.resolve(start,retained.axiom(1),1)
    _, s = q.translated(2,source_cnf=retained.cnf,target_n=2,target_cnf=retained.cnf,images=[1,2],
                        target_proof=retained.proof,convention="set")
    q.require(s["repairs"]["set_context_weakening"] == 1, "retained set context was not exercised")
    dags["set_retained_context"] = s
    return dags


def compiler_inputs():
    family = ROOT / "proofs/ROUTE-PARITY-TRANSFER-20261115-001A"
    check = runpy.run_path(str(family / (family.name + "-P001_literal_projection") / "check.py"))
    choices = [(3, [(1,-2,3),(-1,2,-3),(1,-2,3)], [0,1,2]), (4, [(1,2,4),(-2,3,4)], [1])]
    results = []
    for n, catalog, selected in choices:
        raw, pins, images = check["build_projection"](n,catalog,selected)
        target = raw.cnf + [[g] for g in pins]
        source = [catalog[i] for i in selected]
        table = q.image_map(n,len(images),images)
        plans = q.axiom_plans(n,source,target,table)
        counts = Counter(kind for kind,_ in plans)
        q.require(counts["axiom"] == len(source) and all(kind == "true" for kind,_ in plans[len(raw.cnf):]),
                  "unexpected route axiom or nonconstant switch image")
        results.append({"source_n": n, "selected_occurrences":len(source), "target_axioms":len(target),
                        "source_axiom_images":counts["axiom"], "true_seeds":counts["true"],
                        "boolean_seeds":counts["boolean"], "positive_and_negative_guard_units":len(pins)})
    return results


def corpus():
    result = {"formal_field_census":field_census(), "three_name_control":larger_field_control(),
              "negative_controls":controls(), "edge_cases":unusual_inputs(),
              "wide_contexts":[wide(5),wide(8)], "live_identified_contexts":[live_width(8),live_width(32)],
              "compiler_axiom_plans":compiler_inputs()}
    for convention in ("multiset","set"):
        case = nonlinear_fixture(convention)
        n, source, nt, target, _, proof = case
        output, stats = q.translated(*case,convention=convention)
        verified = check_boolean_steps(nt,target,proof) + check_boolean_steps(n,source,output)
        ancestors = {len(output)-1}
        for i in reversed(range(len(output))):
            if i in ancestors:
                ancestors.update(output[i].get("parents",[]))
        products = [q.mul(node["chosen"],node["multiplier"]) for i,node in enumerate(output)
                    if node["rule"] == "multiply" and i in ancestors]
        terms = {term for f in products for term in f if len(term)==2}
        q.require(len(products) == stats["source"]["rules"]["multiply"] and
                  any(a != b for a,b in terms) and any(a == b for a,b in terms),
                  "final refutation lost an actual mixed product or formal square")
        q.require(set(stats["target"]["rules"]) >= {"axiom","true","boolean","multiply","weaken","combine","delete_false"},
                  "fixture missed a primitive rule")
        if convention == "multiset":
            q.require(stats["target"]["rules"]["contract"] > 0, "fixture lacked explicit contraction")
        else:
            q.require(stats["repairs"]["set_context_weakening"] > 0, "alias never required a set repair")
        stats["truth_evaluated_nodes"] = verified
        stats["products_in_ancestry_of_empty"] = len(products)
        result[convention+"_DAG"] = stats
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--translate", metavar="JSON")
    group.add_argument("--verify", metavar="JSON")
    group.add_argument("--emit", action="store_true")
    parser.add_argument("--expected",type=Path,default=FAMILY/"checks.json")
    args = parser.parse_args()
    path = args.translate or args.verify
    if path:
        data = json.load(sys.stdin) if path == "-" else json.loads(Path(path).read_text())
        conv = data.get("convention","multiset")
        if args.translate:
            proof, stats = q.translated(**data)
            print(json.dumps({"n":data["source_n"],"cnf":data["source_cnf"],"proof":proof,"convention":conv,"stats":stats}))
        else:
            print(json.dumps({"status":"passed",**q.verify(data["n"],data["cnf"],data["proof"],convention=conv)}))
        return
    python = ROOT / ".venv/bin/python"
    if python.exists() and Path(sys.prefix).resolve() != python.parent.parent.resolve():
        os.execv(str(python),[str(python),"-B",str(Path(__file__).resolve()),*sys.argv[1:]])
    result = corpus()
    if args.emit:
        print(json.dumps(result,indent=2,sort_keys=True))
    else:
        q.require(json.loads(args.expected.read_text()) == result, "numeric receipt disagrees with replay")
        print(json.dumps({"status":"passed",**result},sort_keys=True))


if __name__ == "__main__":
    main()
