#!/usr/bin/env python3
"""Check definitions, causal proofs and actual routed certificates, or translate JSON input."""

import argparse
import json
import os
import runpy
import sys
from collections import Counter
from functools import cache
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
from pathlib import Path

FAMILY = Path(__file__).resolve().parent
ROOT = FAMILY.parents[2]
spec = spec_from_file_location("checked_named_product_api", FAMILY/"solver.py")
named = module_from_spec(spec)
spec.loader.exec_module(named)
q = named.q


def family(ticket,slug):
    return runpy.run_path(str(ROOT / "proofs" / ticket / (ticket + "-P001_" + slug) / "check.py"))


def two_levels(dag, base, f, g, h):
    """Convert f to t=fg and then t to u=th, use both named atoms, and recover f."""
    t,first = dag.define(f,g)
    u,second = dag.define(q.var(t),h)
    F,G = q.mul(f,g),q.mul(q.var(t),h)
    df,dg = q.add(q.var(t),F),q.add(q.var(u),G)

    def halves(ref,a,b):
        opposite = q.add(q.ONE,b)
        return dag.multiply(ref,a,b),dag.multiply(ref,a,opposite),q.mul(a,opposite)

    def rejoin(left,right,a,b):
        return dag.contract_all(dag.combine(left,right,a,b))

    fg, f_other, complementary_f = halves(base,f,g)
    tline = dag.combine(fg,first,F,df)
    th, t_other, complementary_t = halves(tline,q.var(t),h)
    uline = dag.combine(th,second,G,dg)
    u_left,u_right,complementary_u = halves(uline,q.var(u),g)
    recovered_u = rejoin(u_left,u_right,q.mul(q.var(u),g),complementary_u)
    recovered_th = dag.combine(recovered_u,second,q.var(u),dg)
    recovered_t = rejoin(recovered_th,t_other,G,complementary_t)
    recovered_fg = dag.combine(recovered_t,first,q.var(t),df)
    recovered_f = rejoin(recovered_fg,f_other,F,complementary_f)
    q.require(dag.clauses[recovered_f] == dag.clauses[base],"quadratic two-level proof failed to restore its clause")
    return recovered_f


def actual_case(n, roster, selected, a,b,d,old_c,oracle):
    raw,pins,images = a["build_projection"](n,roster,selected)
    source = [roster[i] for i in selected]
    cnf = raw.cnf + [[v] for v in pins]
    with oracle(name="g3",bootstrap_with=cnf,with_proof=True) as sat:
        q.require(not sat.solve(),"raw routing fixture is satisfiable")
        additions = [list(map(int,line.split()[:-1])) for line in sat.get_proof() if not line.startswith("d ")]
    if not additions or additions[-1]:
        additions.append([])
    ordinary,end = d["add_reasons"](cnf,additions,b)
    dag = named.Dag(max(images),cnf)
    refs = {}
    inserted = False
    for i in old_c["ancestors"](ordinary,end):
        row = ordinary[i]
        if row["rule"] == "axiom":
            idx = row["axiom"]
            ref = dag.axiom(idx)
            if not inserted and a["clause_image"](cnf[idx],images,n+1) is not None:
                lit = next(v for v in cnf[idx] if abs(images[abs(v)]) <= n)
                others = [j for j in range(1,n+1) if j != abs(images[abs(lit)])]
                ref = two_levels(dag,ref,q.literal(lit),q.var(raw.signals[others[0]]),q.var(raw.signals[others[1]]))
                inserted = True
        elif row["rule"] == "resolve":
            ref = dag.resolve(*(refs[j] for j in row["parents"]),old_c["signed"](row["pivot"]))
        else:
            q.require(row["rule"] == "weaken","unexpected input deduction rule")
            ref = dag.weaken(refs[row["parents"][0]],q.signed_clause(old_c["signed"](v) for v in row["clause"]))
        q.require(dag.clauses[ref] == q.signed_clause(old_c["signed"](v) for v in row["clause"]),
                  "re-emitted raw clause differs")
        refs[i] = ref
    q.require(inserted and refs[end] == len(dag.proof)-1,"two-level definition did not enter the routing proof")
    out,stats = named.translated(n,source,max(images),cnf,images,dag.proof)
    for label,base_n,formula,proof in (("target",max(images),cnf,dag.proof),("source",n,source,out)):
        live = named.ancestors(base_n,formula,proof,include_declarations=False)
        by_index = [(i,row) for i,row in enumerate(proof) if row["rule"]=="define"]
        uses = [sum(proof[j].get("parents",[]).count(i) for j in live) for i,_ in by_index]
        q.require(len(uses)==2 and min(uses)>=2 and all(i in live for i,_ in by_index),"definition lacks two actual proof uses")
        t,u = [row["variable"] for _,row in by_index]
        q.require(any(t in v for form in by_index[1][1]["factors"] for v in form),"second definition lost its first name")
        for _,row in by_index:
            q.require(any(len(term)==2 and term[0]!=term[1] for term in row["clause"][0]),
                      "the source or target definition lost its mixed product")
        q.require(any(proof[i]["rule"]=="multiply" and proof[i]["chosen"]==q.encode(q.var(u)) for i in live),
                  "second name never returned to a live multiplication")
        stats[label]["live_definition_uses"] = uses
    assignments = truth_check(n,source,out)
    declared_target = [row for row in dag.proof if row["rule"]=="define"]
    declared_source = [row for row in out if row["rule"]=="define"]
    for s in product((0,1),repeat=n):
        mapped = [int(v>0) if abs(v)==n+1 else s[abs(v)-1]^int(v<0) for v in (images[j] for j in range(1,max(images)+1))]
        left = extend_values(mapped,declared_target)
        right = extend_values(s,declared_source)
        q.require(left[-2:] == right[-2:],"target/source named values disagree under the literal projection")
    for i in [i for i,row in enumerate(out) if row["rule"]=="define"]:
        wrong = list(out)
        wrong[i] = {**out[i],"factors":[[],out[i]["factors"][1]]}
        try:
            named.verify(n,source,wrong)
        except ValueError:
            pass
        else:
            raise ValueError("invalid declaration on the final ancestry was accepted")
    return {"raw_clauses":len(raw.cnf),"switch_units":len(pins),"route_stages":len(raw.stages),
            "target":stats["target"],"source":stats["source"],"verified_node_bound":stats["verified_node_bound"],
            "source_assignment_checks":assignments,"both_definition_mutations_rejected":True}


def value(form,bits):
    answer = 0
    for term in form:
        answer ^= int(all(bits[i-1] for i in term))
    return answer


def extend_values(bits,declarations):
    values = list(bits)
    for row in declarations:
        f,g = row["factors"]
        values.append(value(f,values) * value(g,values))
    return tuple(values)


def truth_check(n,cnf,proof):
    declared = [row for row in proof if row["rule"]=="define"]
    assignments = list(product((0,1),repeat=n))
    recovered = []
    for s in assignments:
        b = extend_values(s,declared)
        extensions = [z for z in product((0,1),repeat=len(declared)) if all(
            value(row["clause"][0],s+z)==0 for row in declared)]
        q.require(extensions == [b[n:]],"definition extension failed uniqueness")
        recovered.append(b)
    universe = (1<<len(recovered))-1
    @cache
    def meaning(f):
        return sum(1<<i for i,b in enumerate(recovered) if value(f,b)==0)
    rows = []
    for row in proof:
        models = 0
        for f in row["clause"]:
            models |= meaning(q.polynomial(f))
        if row["rule"]=="axiom":
            expected = sum(1<<i for i,b in enumerate(recovered) if any(b[abs(v)-1] == int(v>0) for v in cnf[row["axiom"]]))
            q.require(models==expected,"source input truth check failed")
        else:
            common = universe
            for p in row.get("parents",[]):
                common &= rows[p]
            q.require(not common & ~models,"named proof step lost a legal valuation")
        rows.append(models)
    q.require(rows[-1]==0,"truth evaluation did not end in empty")
    return {"original_valuations":len(recovered),"named_assignments_tried":len(recovered)*(1<<len(declared)),
            "observed_name_pairs":sorted({b[n:] for b in recovered}),"nodes_per_valuation":len(proof)}


def declaration_census(n):
    """Independent bit-vector truth tables for every ordered pair of declarations at this size."""
    all_bits = list(product((0,1),repeat=n+2))
    space = (1<<len(all_bits))-1
    bits = [sum((b[i]<<j) for j,b in enumerate(all_bits)) for i in range(n+2)]
    def all_affines(variable_count):
        forms = []
        for mask in range(1<<(variable_count+1)):
            result = space if mask&1 else 0
            for i in range(variable_count):
                if mask&(1<<(i+1)):
                    result ^= bits[i]
            forms.append(result)
        return forms
    first, second = all_affines(n),all_affines(n+1)
    count = 0
    for f,g in product(first,repeat=2):
        a = space ^ ((f&g)^bits[n])
        for h,k in product(second,repeat=2):
            models = a & (space^((h&k)^bits[n+1]))
            q.require(all(((models >> (4*j)) & 15).bit_count()==1 for j in range(1<<n)),
                      "two-definition program failed unique completion")
            count += 1
    return {"base_variables":n,"ordered_two_definition_programs":count,"base_fibres_tested":count*(1<<n)}


def controls():
    cnf = [[1],[-1]]
    dag = named.Dag(2,cnf)
    old = dag.axiom(0)
    t,i = dag.define(q.var(1),q.var(2))
    u,j = dag.define(q.var(t),q.var(1))
    k = dag.boolean(t)
    dag.resolve(old,dag.axiom(1),1)
    bad = []
    def reject(name,fn):
        try:
            fn()
        except ValueError:
            bad.append(name)
        else:
            raise ValueError("negative control passed "+name)
    def change(name, index, **fields):
        rows = list(dag.proof)
        rows[index] = {**rows[index],**fields}
        reject(name,lambda:named.verify(2,cnf,rows))
    change("old_variable_redefined",i,variable=1)
    change("skipped_fresh_slot",i,variable=4)
    change("duplicate_declaration",j,variable=t)
    change("true_default_before_name_exists",0,rule="boolean",variable=t,clause=dag.proof[k]["clause"])
    change("future_symbol_inside_factor",i,factors=[q.encode(q.var(u)),q.encode(q.ONE)])
    change("self_dependency",i,factors=[q.encode(q.var(t)),q.encode(q.ONE)])
    change("quadratic_factor_times_zero",i,factors=[q.encode(q.mul(q.var(1),q.var(1))),[]])
    change("invented_definition_equation",i,clause=[q.encode(q.var(t))])
    change("declaration_with_unrelated_disjunct",i,clause=[*dag.proof[i]["clause"],q.encode(q.ZERO)])
    change("declaration_from_prior_proof_line",i,parents=[0])
    change("fake_internal_empty_input_axiom",0,axiom=len(cnf),clause=[])
    change("negative_parent_into_shadow_verifier",k,rule="weaken",parents=[-1],clause=[])
    z = named.Dag(1,[[]])
    z.true()
    z.define(q.var(1),q.ZERO)
    z.axiom(0)
    forward = [z.proof[0],{"rule":"multiply","parents":[0],"chosen":[],"multiplier":[[2]],"clause":[[]]},
               *z.proof[1:]]
    reject("future_variable_in_zero_product_multiplier",lambda:named.verify(z.n,z.cnf,forward))
    z = named.Dag(1,[[]])
    _,sq = z.define(q.var(1),q.var(1))
    z.axiom(0)
    z.proof[sq] = {**z.proof[sq],"clause":[q.encode(q.add(q.var(2),q.var(1)))]}
    reject("unauthorized_square_multilinearization",lambda:named.verify(1,z.cnf,z.proof))
    # An actual empty-base counterfeit: its two simultaneous equations demand
    # t=1+u and u=t. Their combination yields a false constant and hence empty.
    v = q.Dag([])
    x,y = q.var(1),q.var(2)
    def fake(name,factor):
        return v.emit("define",(q.add(q.var(name),factor),),variable=name,factors=[q.encode(factor),q.encode(q.ONE)])
    h = fake(1,q.add(q.ONE,y)); k = fake(2,x)
    v.delete_false(v.combine(h,k,v.clauses[h][0],v.clauses[k][0]))
    reject("cyclic_equations_cannot_refute_empty_input",lambda:named.verify(0,[],v.proof))
    reject("raw_source_formula_mentions_a_later_name",lambda:named.verify(1,[[2]],dag.proof))
    reject("old_literal_map_cannot_capture_a_future_source_name",
           lambda:named.backtranslate(1,cnf,2,cnf,[1,-3],dag.proof))
    return bad


def special_cases():
    # n+1 is a constant sentinel in the external images and the first real
    # source product name in a proof. Their uses must remain distinguishable.
    dag = named.Dag(2,[[1],[-1]])
    t,first = dag.define(q.var(1),q.var(2))
    second_var,second = dag.define(q.var(t),q.add(q.ONE,q.var(2)))
    dag.boolean(2)
    dag.boolean(t)
    dag.boolean(second_var)
    dag.resolve(dag.axiom(0),dag.axiom(1),1)
    output,stats = named.translated(1,[[1],[-1]],2,dag.cnf,[1,2],dag.proof)
    defs = [node for node in output if node["rule"]=="define"]
    q.require(defs[0]["variable"]==2 and defs[0]["factors"]==[q.encode(q.var(1)),q.encode(q.ONE)]
              and defs[1]["factors"]==[q.encode(q.var(2)),q.encode(q.ZERO)],"constant sentinel captured a name")
    truth_check(1,dag.cnf,output)
    # Independent syntax fallback for set contexts, with a surviving named square.
    s = named.Dag(2,[[1],[-1]],convention="set")
    _,decl = s.define(q.var(1),q.var(2))
    ref=s.axiom(0)
    s.resolve(ref,s.axiom(1),1)
    sent,ss = named.translated(1,[[1],[-1]],2,s.cnf,[1,1],s.proof,convention="set")
    defined = next(row for row in sent if row["rule"]=="define")
    q.require(defined["clause"]==[q.encode(q.add(q.var(2),q.mul(q.var(1),q.var(1))))],
              "named square became multilinear")
    # An implicit causal dependency can be absent from ordinary explicit parent edges.
    trace = named.Dag(1,[[1],[-1]])
    n1,p1=trace.define(q.var(1),q.ONE)
    p2=trace.boolean(n1)
    initial=trace.axiom(0)
    add_boolean=trace.weaken(initial,[q.literal(1),q.var(n1)])
    j=trace.combine(add_boolean,p2,q.var(n1),q.add(q.ONE,q.var(n1)))
    j=trace.delete_false(j)
    neg=trace.weaken(initial,[q.literal(1),q.add(q.ONE,q.var(n1))])
    j=trace.contract_all(trace.delete_false(trace.combine(j,neg,q.var(n1),q.add(q.ONE,q.var(n1)))))
    trace.resolve(j,trace.axiom(1),1)
    named.verify(1,trace.cnf,trace.proof)
    logical=named.ancestors(1,trace.cnf,trace.proof,include_declarations=False)
    causal=named.ancestors(1,trace.cnf,trace.proof)
    q.require(p1 not in logical and p1 in causal,"pruning lost a symbol declaration")
    # A cached empty input is recited after unrelated materialized declaration
    # and Boolean rows. The output certificate itself must still end in empty.
    cached = {}
    for mode in ("multiset","set"):
        e=named.Dag(0,[[]],convention=mode)
        e.axiom(0)
        fresh,_=e.define(q.ONE,q.ONE)
        e.boolean(fresh)
        e.proof.append(dict(e.proof[0]))
        recovered,info=named.translated(0,[[]],0,[[]],[],e.proof,convention=mode)
        last=recovered[-1]
        q.require(last["rule"]=="weaken" and last["clause"]==[] and last["parents"]==[0]
                  and recovered[-2]["clause"],"cached empty input failed to become the final output occurrence")
        cached[mode]={"input_nodes":len(e.proof),"output_nodes":len(recovered),"final_parent":last["parents"][0],
                      "final_rule":last["rule"],"node_bound":info["verified_node_bound"]}
    return {"sentinel_and_first_fresh":stats,"set_alias_named_square":ss,"causal_pruning_keeps_extra_declaration":True,
            "recited_empty_input_after_named_rows":cached}


def corpus():
    from pysat.solvers import Solver
    prior = "ROUTE-PARITY-TRANSFER-20261115-001"
    a=family(prior+"A","literal_projection")
    b=family(prior+"B","dag_transport")
    d=family(prior+"D","encoded_lower_bound")
    c=family("QUADRATIC-ROUTE-TRANSFER-20261115-001C","encoded_products")
    three=a["compiler"]().clauses_on(3)
    four=a["compiler"]().clauses_on(4)
    selected=[i for i,cl in enumerate(four) if cl in three or i==13]
    return {"named_program_census":[declaration_census(i) for i in (0,1,2)],
            "negative_controls":controls(),"special_cases":special_cases(),
            "raw_listed":actual_case(3,three,range(len(three)),a,b,d,c,Solver),
            "raw_fixed_catalog":actual_case(4,four,selected,a,b,d,c,Solver)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    action=parser.add_mutually_exclusive_group()
    action.add_argument("--translate",metavar="JSON")
    action.add_argument("--verify",metavar="JSON")
    action.add_argument("--emit",action="store_true")
    parser.add_argument("--expected",type=Path,default=FAMILY/"checks.json")
    args=parser.parse_args()
    filename=args.translate or args.verify
    if filename:
        data=json.load(sys.stdin) if filename=="-" else json.loads(Path(filename).read_text())
        conv=data.get("convention","multiset")
        if args.translate:
            proof,stats=named.translated(**data)
            print(json.dumps({"n":data["source_n"],"cnf":data["source_cnf"],"proof":proof,"convention":conv,"stats":stats}))
        else:
            print(json.dumps({"status":"passed",**named.verify(data["n"],data["cnf"],data["proof"],convention=conv)}))
        return
    python=ROOT/".venv/bin/python"
    if python.exists() and Path(sys.prefix).resolve()!=python.parent.parent.resolve():
        os.execv(str(python),[str(python),"-B",str(Path(__file__).resolve()),*sys.argv[1:]])
    result=corpus()
    if args.emit:
        print(json.dumps(result,sort_keys=True,indent=2))
    else:
        q.require(json.loads(args.expected.read_text())==json.loads(json.dumps(result)),"numeric receipt disagrees with replay")
        print(json.dumps({"status":"passed",**result},sort_keys=True))


if __name__=="__main__":
    main()
