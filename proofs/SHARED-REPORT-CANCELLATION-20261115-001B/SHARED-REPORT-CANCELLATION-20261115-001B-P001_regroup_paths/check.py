"""Independent projections, signed and primitive proof replay, schedule and scope controls."""
from copy import copy
from functools import cache
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import runpy


HERE = Path(__file__).resolve().parent
M = runpy.run_path(str(HERE/"solver.py"))
A = M["A"]
STATES = tuple(product((0,1), repeat=3))


def oracle(shared, private):
    a,b = shared
    x,y,z = private
    return int(bool(z) and (bool(x and y) != bool(a and b)))


def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise AssertionError("invalid operation was accepted")


def digest(rows):
    h = sha256()
    for row in rows:
        h.update(json.dumps(row, separators=(",",":"), sort_keys=True).encode())
        h.update(b"\n")
    return h.hexdigest()


def compact(dag, stats):
    i = stats
    return {k:i[k] for k in ("edges","strict_clauses","axioms","resolutions","nodes","quadratic_nodes",
                              "max_width","all_nodes_live")} | {
        "source_cnf_sha256":digest(dag.cnf),
        "ordinary_proof_sha256":digest(zip(dag.steps, dag.clauses, strict=True)),
        "join_resolutions":[e["after_node"]-e["first_node"] for e in i["events"] if e["op"]=="join"],
    }


def validate_counts(encoded, dag, stats, *, quadratic=False):
    events = stats["events"]
    joins = [e for e in events if e["op"] == "join"]
    selected = [e["edge"] for e in events if e["op"]=="edge"]
    rows = sum(len(encoded["blocks"][e]["rows"]) for e in selected)
    assert all(len(encoded["blocks"][e]["rows"]) == (72,184)[encoded["blocks"][e]["charge"]] for e in selected)
    join_total = 0
    for e in joins:
        expected = M["join_cost"](*e["charges"], middle_order=stats["middle_order"])
        assert expected == e["after_node"]-e["first_node"]
        join_total += expected
    assert events[-1]["after_node"]-events[-1]["first_node"]==255
    assert stats["nodes"]==11*rows + join_total+255 and stats["axioms"]==6*rows
    assert stats["resolutions"]==5*rows+join_total+255 and stats["all_nodes_live"]
    assert stats["max_width"] <= 10 and dag.cnf is encoded["cnf"]
    p_cost = sum(M["join_cost"](*e["charges"],middle_order=stats["middle_order"],primitive=True) for e in joins)
    assert stats["quadratic_nodes"] == 16*rows+p_cost+2048
    if quadratic:
        actual = M["verify_quadratic"](dag)
        assert actual["lines"] == stats["quadratic_nodes"]
        assert set(actual["rules"]) == {"axiom","combine","delete_false","contract"}
        assert actual["max_width"] <= 19
        return actual
    return None


def check_semantics():
    tuples = completions = bad_rows = 0
    for a,b,c,d in product((0,1), repeat=4):
        for u,w in product(STATES,repeat=2):
            f,g = oracle((a,b),u),oracle((a,b),w)
            expected = (f^g)==(c^d)
            witnesses = []
            for v in STATES:
                m = oracle((a,b),v)
                left, right = f^m == c, m^g == d
                if not expected:
                    assert left != right
                witnesses.append(left and right)
                completions += 1
            assert any(witnesses) == expected
            tuples += 1
            bad_rows += not expected
    return {"endpoint_cases":tuples, "middle_completions":completions, "forbidden_endpoint_cases":bad_rows}


def join_matrices():
    result = {}
    for order in ((2,0,1),(0,1,2)):
        numbers, kernel_counts = [], []
        for c,d in product((0,1),repeat=2):
            encoded = A["encode_cycle"]((c,d,1^c^d))
            builder = M["PathBuilder"](encoded,middle_order=order)
            left, right = builder.edge(0), builder.edge(1)
            before = len(builder.dag.steps)
            previous_primitive = M["quadratic_node_count"](builder.dag)
            joined = builder.join(left,right)
            numbers.append(len(builder.dag.steps)-before)
            kernel_counts.append(M["quadratic_node_count"](builder.dag)-previous_primitive)
            assert kernel_counts[-1] == M["join_cost"](c,d,middle_order=order,primitive=True)
            assert joined.charge == c^d and numbers[-1] == M["join_cost"](c,d,middle_order=order)
        result["".join("xyz"[i] for i in order)] = {"ordinary":numbers,"primitive":kernel_counts}
    assert result["zxy"] == {"ordinary":[268,680,680,420],"primitive":[1968,4984,4984,3296]}
    assert result["xyz"]["ordinary"] == [336,758,758,484]
    return result


def signed_cycles():
    counts = {3:[0,0],4:[0,0]}
    even_models = 0
    for h in (3,4):
        for charges in product((0,1), repeat=h):
            encoded = A["encode_cycle"](charges)
            parity = sum(charges)%2
            counts[h][parity] += 1
            if parity == 0:
                for a,b,f in product((0,1), repeat=3):
                    model = M["even_model"](encoded, shared=(a,b), first_report=f)
                    assert all(any(model[abs(s)] == (s>0) for s in row) for row in encoded["cnf"])
                    even_models += 1
            else:
                start = sum(i*c for i,c in enumerate(charges))%h
                reverse = bool(charges[0])
                tree, last = M["path_plan"](h,"balanced",start=start,reverse=reverse)
                dag, stats = M["prove_tree"](encoded,tree,last,reverse=reverse)
                validate_counts(encoded,dag,stats)
    return {"even_odd_charge_vectors":counts,"full_strict_even_models":even_models}


def triangle_trace():
    charges = (0,0,1)
    encoded = A["encode_cycle"](charges)
    b = M["PathBuilder"](encoded)
    left, right = b.edge(0), b.edge(1)
    joined = b.join(left,right)
    key = (0,0,0,7)
    a,shared_b,u,w = key
    middle = encoded["triples"][1]
    order = b.middle_order
    leaves = []
    ids = []
    for branch in product((0,1),repeat=3):
        xyz = [0,0,0]
        for j, val in zip(order,branch):
            xyz[j]=val
        v=M["state_id"](xyz)
        source = left if (a,shared_b,u,v) in left.rows else right
        ref = left.rows[(a,shared_b,u,v)] if source is left else right.rows[(a,shared_b,v,w)]
        leaves.append({"middle_xyz":xyz,"source_edge":0 if source is left else 1,"node":ref})
        ids.append(ref)
    trace = []
    for pivot in (middle[j] for j in reversed(order)):
        nxt = []
        for j in range(0,len(ids),2):
            p,q = ids[j:j+2]
            ref = b.dag._deductions[p,q,pivot]
            trace.append({"node":ref, "parents":[p,q], "pivot":pivot,"signed_clause":b.dag.clauses[ref]})
            nxt.append(ref)
        ids = nxt
    assert ids == [joined.rows[key]] and set(x["source_edge"] for x in leaves)=={0,1}
    dag, stats = b.close(joined,b.edge(2))
    recorded=(HERE/"triangle.res").read_text()
    from_file=M["read_certificate"](encoded,recorded)
    assert M["certificate_text"](dag)==recorded and from_file.steps==dag.steps and from_file.clauses==dag.clauses
    checked=validate_counts(encoded,from_file,stats,quadratic=True)
    reordered = []
    for start, backwards in ((0,False),(1,False),(2,True)):
        tree,last=M["path_plan"](3,"left",start=start,reverse=backwards)
        d,s=M["prove_tree"](encoded,tree,last,reverse=backwards)
        validate_counts(encoded,d,s)
        reordered.append({"start":start,"reverse":backwards,"nodes":s["nodes"],"source":digest(d.cnf)})
    assert len({s["source"] for s in reordered})==1
    return {"charges":charges,**compact(dag,stats),"quadratic_kernel":checked,
            "certificate_file_sha256":sha256(recorded.encode()).hexdigest(),"certificate_bytes":len(recorded.encode()),"grouping_events":stats["events"],
            "example_endpoint_key":key,"origin_of_eight_leaves":leaves,
            "seven_ordinary_resolutions":trace, "rotation_and_reversal":reordered}


def exhaustive_plans():
    @cache
    def trees(lo,hi):
        if hi-lo==1:
            return (lo,)
        return tuple((l,r) for j in range(lo+1,hi) for l in trees(lo,j) for r in trees(j,hi))
    weights = {(c,d):(M["join_cost"](c,d),M["join_cost"](c,d,primitive=True))
               for c,d in product((0,1),repeat=2)}
    pairs = all_shapes = 0
    for width in range(2,7):
        for charges in product((0,1),repeat=width):
            def measure(tree):
                if type(tree) is int:
                    return charges[tree],0,0
                x,u,p=measure(tree[0])
                y,v,q=measure(tree[1])
                ordinary,primitive=weights[x,y]
                return x^y,u+v+ordinary,p+q+primitive
            all_costs=[measure(t)[1:] for t in trees(0,width)]
            planned,_,cost=M["optimal_plan"]((*charges,1^(sum(charges)%2)))
            _,chosen_ordinary,chosen_primitive=measure(planned)
            assert cost==chosen_ordinary==min(o for o,_ in all_costs)
            assert chosen_primitive==min(q for _,q in all_costs)
            assert all((o==chosen_ordinary)==(q==chosen_primitive) for o,q in all_costs)
            all_shapes+=len(all_costs)
            pairs+=1
    return {"open_charge_orders":pairs,"evaluated_parenthesizations":all_shapes}


def growth():
    charges = (1,0,0,0,0)
    encoded = A["encode_cycle"](charges)
    five = {}
    for group in ("left","balanced","optimal"):
        if group=="optimal":
            tree, last, _ = M["optimal_plan"](charges)
        else:
            tree,last=M["path_plan"](5,group)
        dag,stats=M["prove_tree"](encoded,tree,last)
        q=validate_counts(encoded,dag,stats,quadratic=group in ("left","optimal"))
        five[group]={**compact(dag,stats),"tree":tree}
        if q is not None:
            five[group]["quadratic_kernel"]=q
    assert len({i["source_cnf_sha256"] for i in five.values()})==1
    assert [five[g]["nodes"] for g in five]==[7487,7075,6663]
    larger=[]
    for h in (8,12,17):
        c=tuple(int(i%4==1) for i in range(h-1))
        c=(*c,1^(sum(c)%2))
        e=A["encode_cycle"](c)
        cases=[]
        for name in ("left","balanced"):
            tree,last=M["path_plan"](h,name,start=h-2,reverse=True)
            dag,stats=M["prove_tree"](e,tree,last,reverse=True)
            validate_counts(e,dag,stats)
            cases.append({"grouping":name,**compact(dag,stats)})
        assert cases[0]["source_cnf_sha256"]==cases[1]["source_cnf_sha256"]
        larger.append({"h":h,"charges":c,"proofs":cases})
    return five,larger


def graph_controls():
    # The chosen 3->1->4->3 cycle uses original edge IDs 1,2,4. Edge 2 is presented backwards.
    e=A["encode_checks"](6,[(0,5,1),(3,1,0),(4,1,1),(2,0,0),(4,3,0),(5,2,1)])
    cycle=[(1,False),(2,True),(4,False)]
    b=M["PathBuilder"](e,cycle_edges=cycle)
    assert not b.dag.steps
    edge2=b.edge(2,reverse=True)
    edge4=b.edge(4)
    p=b.join(edge2,edge4)
    assert p.walk==(1,4,3)
    dag,s=b.close(p,b.edge(1))
    validate_counts(e,dag,s)
    actual={row[1] for row in dag.steps if row[0]=="axiom"}
    permitted={i for edge in (1,2,4) for row in e["blocks"][edge]["rows"] for i in range(row["start"],row["start"]+6)}
    assert actual==permitted and len(actual)<len(e["cnf"])
    return {**compact(dag,s),"original_edges_in_arrival_order":[2,4,1],"original_cycle":cycle,
            "unused_original_strict_clauses":len(e["cnf"])-len(actual),"event_order":[j["op"] for j in s["events"]]}


def failure_controls():
    e=A["encode_cycle"]((0,0,0))
    # F=0 at all vertices, but removing the z literal of the forbidden middle 111 row rejects this model.
    public=[0]*(e["public_n"]+1)
    x,y,z=e["triples"][1]
    public[x]=public[y]=1
    actual=M["lift_public"](e,public)
    victim=next(row for row in e["blocks"][0]["rows"] if row["bits"]==(0,0,0,0,0,1,1,1))
    weakened_scope=[s for s in victim["clause"] if abs(s)!=z]
    assert any(actual[abs(s)] == (s>0) for s in victim["clause"])
    assert not any(actual[abs(s)] == (s>0) for s in weakened_scope)
    splits=[]
    for shared in product((0,1),repeat=2):
        left=oracle(shared,(0,0,0))^oracle(shared,(0,0,1))
        right=oracle(shared,(0,0,1))^oracle(shared,(0,0,0))
        splits.append((left==0,right==1))
    assert any(l for l,_ in splits) and any(r for _,r in splits) and not any(l and r for l,r in splits)
    assert oracle((1,1),(1,1,1)) == oracle((1,1),(0,0,0)) and 1*1*1 != 0*0*0
    denied_even=reject(lambda:M["path_refutation"]((0,0,0)))
    d,s=M["path_refutation"]((0,0,1))
    forged=copy(d); forged.steps=d.steps.copy()
    j=next(i for i,row in enumerate(forged.steps) if row[0]=="resolve")
    rule,l,r,p=forged.steps[j];forged.steps[j]=rule,l,r,-p
    bad_pivot=reject(lambda:M["verify_resolution"](forged))
    wrong=copy(d);wrong.cnf=A["encode_cycle"]((1,0,0))["cnf"]
    bad_formula=reject(lambda:M["verify_resolution"](wrong))
    b=M["PathBuilder"](A["encode_cycle"]((1,0,0,0)))
    t0,t2=b.edge(0),b.edge(2)
    disconnected=reject(lambda:b.join(t0,t2))
    return {"dropping_middle_z_falsifies_a_strict_model":True, "projected_shared_bit_answers":splits,
            "omitted_shared_term_flips_a_check":True, "even_cycle":denied_even,
            "altered_pivot":bad_pivot,"different_original_cnf":bad_formula,"nonadjacent_join":disconnected}


def main():
    five,larger=growth()
    return {"status":"passed","truth_composition":check_semantics(),"ordinary_join_costs":join_matrices(),
            "all_small_charge_vectors":signed_cycles(),"triangle":triangle_trace(),
            "five_cycle_same_cnf":five,"growing_cycles":larger,"ordered_optimum_check":exhaustive_plans(),
            "original_subcycle":graph_controls(),"failure_controls":failure_controls()}


if __name__=="__main__":
    print(json.dumps(main(),sort_keys=True,indent=2))
