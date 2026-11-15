"""Check the strict source, individual deletion models and explicit named proof DAGs."""

from collections import Counter
import gzip
from hashlib import sha256
from itertools import product
import json
import os
from pathlib import Path
import sys

try:
    from pysat.solvers import Solver
except ModuleNotFoundError:
    interpreter = Path(__file__).resolve().parents[3] / ".venv" / "bin" / "python"
    if not interpreter.exists() or Path(sys.executable) == interpreter:
        raise
    os.execv(str(interpreter),[str(interpreter),"-B",str(Path(__file__).resolve()),*sys.argv[1:]])

import solver as S


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def report(bits, shared):
    x,y,z = bits
    return int(bool(z) and (bool(x and y) != shared))


def satisfies(literal, values):
    return values[abs(literal)] == (literal>0)


def schema(instance):
    owned = set()
    assert len(instance["cnf"]) == sum(6*len(b["rows"]) for b in instance["blocks"])
    for b in instance["blocks"]:
        assert len(b["rows"]) == (72,184)[b["charge"]]
        assert len(set(b["variables"]))==8
        for row in b["rows"]:
            start = row["start"]
            slots = instance["cnf"][start:start+6]
            private = {abs(v) for c in slots for v in c if abs(v)>instance["public_n"]}
            assert set(row["aux"])==private and len(private)==5 and not private & owned
            owned.update(private)
            assert all(len(c)==len({abs(v) for v in c})==3 for c in slots)
            assert set(abs(v) for c in slots for v in c if abs(v) <= instance["public_n"])==set(b["variables"])
    assert owned==set(range(instance["public_n"]+1,instance["n"]+1))


def local_projection(tally):
    """Use an independent SAT backend with each of the 256 original pins supplied."""
    for reversed_order,charge in product((False,True),(0,1)):
        i,j = ((1,0) if reversed_order else (0,1))
        source = S.encode_checks(2,[(i,j,charge)])
        schema(source)
        with Solver(name="g3",bootstrap_with=source["cnf"]) as oracle:
            for bits in product((0,1),repeat=8):
                a,b,*tail = bits
                expected = (report(tail[:3],a*b)^report(tail[3:],a*b)) == charge
                pins = [v if bit else -v for v,bit in enumerate(bits,1)]
                assert oracle.solve(assumptions=pins) == expected
                tally["fully_pinned_one_check_SAT_comparisons"] += 1
    model = S.encode_cycle((0,0,1))
    for h in (3,4):
        for charges in product((0,1),repeat=h):
            instance = S.encode_cycle(charges)
            with Solver(name="g3",bootstrap_with=instance["cnf"]) as oracle:
                assert oracle.solve()==(sum(charges)%2==0)
                tally["signed_cycle_SAT_comparisons"] += 1
    return model


def missing_row_values(instance,missing,deleted):
    """Keep the deleted row's eight bits and solve the remaining path in either orientation."""
    blocks,triples = instance["blocks"],instance["triples"]
    bad = blocks[missing]
    values = [0]*(instance["n"]+1)
    for v,bit in zip(bad["variables"],deleted["bits"]):
        values[v] = bit
    shared = values[1] and values[2]
    i,j = bad["i"],bad["j"]
    value_i = report(tuple(values[v] for v in triples[i]),shared)
    value_j = report(tuple(values[v] for v in triples[j]),shared)
    public = {i:value_i}
    adj = [[] for _ in triples]
    for index,block in enumerate(blocks):
        if index != missing:
            u,v,c = block["i"],block["j"],block["charge"]
            adj[u].append((v,c))
            adj[v].append((u,c))
    stack = [i]
    while stack:
        u = stack.pop()
        for v,c in adj[u]:
            bit = public[u]^c
            if v in public:
                assert public[v]==bit
            else:
                public[v]=bit
                stack.append(v)
    assert len(public)==len(triples) and public[j]==value_j
    for k,(x,y,z) in enumerate(triples):
        if k not in (i,j):
            values[x],values[y],values[z] = (1,1^shared,1) if public[k] else (0,0,0)
    for block in blocks:
        for row in block["rows"]:
            if row["start"]==deleted["start"]:
                continue
            clause = row["clause"]
            assert any(satisfies(l,values) for l in clause)
            still_false = not satisfies(clause[0],values)
            for k,v in enumerate(row["aux"]):
                still_false &= not satisfies(clause[k+1],values)
                values[v] = int(still_false)
    return values


def check_deletions(instance):
    schema(instance)
    count = 0
    for bi,block in enumerate(instance["blocks"]):
        for row in block["rows"]:
            values = missing_row_values(instance,bi,row)
            start = row["start"]
            slots = instance["cnf"][start:start+6]
            # Private variables of this row can now change without changing any
            # other raw clause; schema verified disjointness above.
            for i,clause in enumerate(instance["cnf"]):
                if not start <= i < start+6:
                    assert any(satisfies(l,values) for l in clause)
            for gap in range(6):
                for j,aux in enumerate(row["aux"]):
                    values[aux] = int(j<gap)
                assert [k for k,c in enumerate(slots) if not any(satisfies(v,values) for v in c)] == [gap]
                count += 1
    assert count==len(instance["cnf"])
    return count


def first_raw_failure(instance,dag):
    images={}
    def expand(raw):
        result=S.ZERO
        for t in S.Q.polynomial(raw):
            term=S.ONE
            for v in t:
                term=S.mul(term,images.get(v,S.var(v)))
            result=S.add(result,term)
        return result
    for i,step in enumerate(dag.proof):
        if step["rule"]=="define":
            f,g=(expand(raw) for raw in step["factors"])
            images[step["variable"]]=S.mul(f,g)
        forms=[expand(p) for p in S.A.mentioned_forms(step)]
        exceeded=[f for f in forms if any(len(t)>2 for t in f)]
        if exceeded:
            assert step["rule"]=="multiply"
            selected=expand(step["chosen"])
            multiplier=expand(step["multiplier"])
            result=S.mul(selected,multiplier)
            assert result in exceeded and all(v<=instance["public_n"] for t in result for v in t)
            return {"index":i,"old_row":step,"selected_image":S.Q.encode(selected),
                    "multiplier_image":S.Q.encode(multiplier),"product_image":S.Q.encode(result)}
    raise AssertionError("full raw inlining missed its first cubic")


def trace_record(instance,dag,trace):
    roots = trace["edge_roots"]
    example = instance["blocks"][0]["rows"][0]
    return {"coordinates":{"shared":[1,2],"triples":instance["triples"]},
            "charges":[b["charge"] for b in instance["blocks"]],
            "checks":[[b["i"],b["j"],b["charge"]] for b in instance["blocks"]],
            "base_variables":instance["n"],"strict_clauses":len(instance["cnf"]),
            "named_nodes":len(dag.proof),"cnf_sha256":digest(instance["cnf"]),"proof_sha256":digest(dag.proof),
            "definitions":[[i,row] for i,row in enumerate(dag.proof) if row["rule"]=="define"],
            "first_over_degree_after_removing_all_names":first_raw_failure(instance,dag),
            "first_forbidden_row":{**example,"strict_clauses":instance["cnf"][example["start"]:example["start"]+6]},
            "check_roots":[[i,dag.proof[i]] for i in roots],
            "cancellation":[[i,dag.proof[i]] for i in [*trace["addition_nodes"],trace["empty"]]],
            "raw_indices_are_zero_based":True}


def audit_proof(instance,dag,trace,tally,label):
    needed = set()
    work = [trace["empty"]]
    while work:
        i = work.pop()
        if i not in needed:
            needed.add(i)
            work.extend(dag.proof[i].get("parents",()))
    assert {r["axiom"] for i,r in enumerate(dag.proof) if i in needed and r["rule"]=="axiom"} == set(range(len(instance["cnf"])))
    defs = [r for i,r in enumerate(dag.proof) if i in needed and r["rule"]=="define"]
    assert len(defs)==1+len(instance["triples"])
    assert all(i in needed for i in trace["edge_roots"])
    declared = [tuple(S.Q.polynomial(f) for f in row["factors"]) for row in defs]
    pairs = [(instance["a"],instance["b"]),*[(x,y) for x,y,_ in instance["triples"]]]
    assert declared==[(S.var(x),S.var(y)) for x,y in pairs]
    for j,block in enumerate(instance["blocks"]):
        i,k,c = block["i"],block["j"],block["charge"]
        zi,zj = instance["triples"][i][2],instance["triples"][k][2]
        base = instance["n"]+1
        terms = [(zi,base),(zi,base+i+1),(zj,base),(zj,base+k+1)]
        expected_eq = S.Q.polynomial(terms+([()] if c else []))
        assert dag.clauses[trace["edge_roots"][j]]==(expected_eq,)
    assert dag.clauses[trace["false_unit"]]==(S.ONE,) and dag.clauses[trace["empty"]]==()
    h=len(instance["triples"])
    assert len(dag.proof) <= 10744*h+1
    width=max(len(row["clause"]) for row in dag.proof)
    degree=max(len(term) for row in dag.proof for atom in S.A.mentioned_forms(row) for term in atom)
    assert width<=17 and degree==2
    tally[label+"_uniform_node_bound"] = 10744*h+1
    tally[label+"_maximum_width"] = width
    tally[label+"_maximum_printed_degree"] = degree
    return len(defs)


def cubic_control():
    # Set a=b=0 and the other report to zero. Check BOTH signs against every
    # possible degree-two Boolean function on the remaining three bits.
    low=((),(0,),(1,),(2,),(0,1),(0,2),(1,2))
    pts=list(product((0,1),repeat=3))
    tested=0
    for c in (0,1):
        actual=[report(xyz,0)^c for xyz in pts]
        for mask in range(1<<len(low)):
            candidate=[sum(all(point[i] for i in term) for j,term in enumerate(low) if mask>>j&1)%2 for point in pts]
            assert candidate!=actual
            tested+=1
    return tested


def main():
    for path,expected in ((S.named_path,"d81e4f0e8dfc8b8260587d0b7f19672bfaef87827665c8689167b72100806929"),
                          (S.cut_path,"7a381b7606d03304391fc1fc5e1bab52e53b55637187aaa1ced3b5aeae939312"),
                          (Path(S.Q.__file__),"84a7cdc149c8945061e8c46daaf9b3686cbcf4cee26f73b4e79c663bda25b71e")):
        assert sha256(path.read_bytes()).hexdigest()==expected
    tally = Counter()
    triangle = local_projection(tally)
    tally["triangle_individual_strict_clause_deletion_models"] = check_deletions(triangle)
    square = S.encode_checks(4,[(2,1,1),(0,3,1),(1,0,1),(3,2,0)])
    tally["reoriented_square_individual_strict_clause_deletion_models"] = check_deletions(square)
    tally["direct_cubic_low_degree_comparisons"] = cubic_control()
    dag,trace = S.named_refutation(triangle)
    tally["triangle_charged_names"] = audit_proof(triangle,dag,trace,tally,"triangle")
    tally["triangle_proof_nodes"] = len(dag.proof)
    tally["triangle_input_variables"] = triangle["n"]
    record = trace_record(triangle,dag,trace)
    saved=json.loads(Path(__file__).with_name("trace.json").read_text())
    assert json.loads(json.dumps(record))==saved
    with gzip.open(Path(__file__).with_name("triangle.json.gz"),"rt",encoding="utf-8") as source:
        stored=json.load(source)
    assert stored=={"n":triangle["n"],"cnf":triangle["cnf"],"proof":dag.proof}
    tally["first_cubic_row_under_full_inlining"] = record["first_over_degree_after_removing_all_names"]["index"]
    for k in (0,1):
        block = triangle["blocks"][2*k]
        tally["forbidden_rows_charge_"+str(k)] = len(block["rows"])
    broken = dict(triangle["blocks"][0]["rows"][0])
    broken["start"] += 1
    try:
        S.lift_row(S.A.Dag(triangle["n"],triangle["cnf"]),broken)
    except ValueError:
        tally["wrong_source_row_rejected"] = 1
    else:
        raise AssertionError("lift accepted a different six-clause source")
    # Rotate the order to combine nonconsecutive displayed checks first.
    dag,trace = S.named_refutation(square,order=(0,1,3,2))
    tally["square_charged_names"] = audit_proof(square,dag,trace,tally,"square")
    tally["square_proof_nodes"] = len(dag.proof)
    tally["square_first_sum_quadratic_terms"] = sum(len(t)==2 for t in dag.clauses[trace["addition_nodes"][0]][0])
    assert tally["square_first_sum_quadratic_terms"]==8
    return {"status":"passed",**dict(sorted(tally.items()))}


if __name__=="__main__":
    if len(sys.argv)==3 and sys.argv[1]=="--emit-triangle":
        instance=S.encode_cycle((0,0,1))
        dag,trace=S.named_refutation(instance)
        record={"n":instance["n"],"cnf":instance["cnf"],"proof":dag.proof,"trace":trace_record(instance,dag,trace)}
        Path(sys.argv[2]).write_text(json.dumps(record,separators=(",",":"))+"\n",encoding="utf-8")
    elif len(sys.argv)==1:
        print(json.dumps(main(),indent=2,sort_keys=True))
    else:
        raise SystemExit("usage: check.py [--emit-triangle OUTPUT.json]")
