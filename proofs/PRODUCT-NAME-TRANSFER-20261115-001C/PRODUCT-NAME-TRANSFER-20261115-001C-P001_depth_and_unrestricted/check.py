"""Exercise the named-product lower-bound comparisons and their exact syntactic rules."""
import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import runpy
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
T="PRODUCT-NAME-TRANSFER-20261115-001"
HASH="9f7eb894da07496b4cba14cbf7a4a109d64e994837fc0478be541cc4aaa57306"


def product_tree(m,n,signs):
    q=m["Q"]
    var,opp=m["var"],m["opposite"]
    literals=[(1 if signs[i-1] else -1)*i for i in range(1,n+1)]
    cnf=[[lit] for lit in literals]+[[-lit for lit in literals]]
    dag=m["A"]["Dag"](n,cnf)
    names=literals[:]
    units={lit:dag.axiom(j) for j,lit in enumerate(literals)}
    gates=[]
    def truth(literal):
        return var(literal) if literal>0 else opp(var(-literal))
    while len(names)>1:
        new=[]
        for x,y in zip(names[::2],names[1::2]):
            t,decl=dag.define(truth(x),truth(y))
            first,second,third=m["extension_clauses"](dag,t,decl,x,y)
            for resulting,want in zip((first,second,third),((-t,x),(-t,y),(t,-x,-y))):
                assert dag.clauses[resulting]==q["signed_clause"](want)
            partial=dag.resolve(units[x],third,x)
            units[t]=dag.resolve(units[y],partial,y)
            gates.append((t,x,y,first,second))
            new.append(t)
        names=new
    root=names[0]
    # Recover the top assertion through two formal squares before its downstream uses.
    chosen=opp(var(root))
    u=dag.multiply(units[root],chosen,var(root))
    v=dag.multiply(units[root],chosen,chosen)
    a=dag.combine(u,v,m["mul"](chosen,var(root)),m["mul"](chosen,chosen))
    again={root:a}
    for t,x,y,first,second in reversed(gates):
        again[x]=dag.resolve(again[t],first,t)
        again[y]=dag.resolve(again[t],second,t)
    final=dag.axiom(n)
    for x in literals:
        final=dag.resolve(again[x],final,x)
    assert final==len(dag.proof)-1 and dag.clauses[final]==()
    m["A"]["verify"](n,cnf,dag.proof)
    return cnf,dag.proof


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--source-pdf",type=Path)
    pdf=cli.parse_args().source_pdf
    m=runpy.run_path(str(HERE/"solver.py"))
    schema=json.loads((ROOT/"schemas/external_evidence_admission.schema.json").read_text())
    doc=json.loads((HERE/"admission.json").read_text())
    sys.path.insert(0,str(ROOT/"scripts"))
    from external_evidence_admission_schema_model import validate_admission_record
    intake=validate_admission_record(ROOT,schema,doc)
    assert intake.accepted, intake.errors
    assert len(doc)==22 and "fixed" in doc["exact_local_claim"] and "extension" in doc["exact_local_claim"]
    if pdf and hashlib.sha256(pdf.read_bytes()).hexdigest()!=HASH:
        raise ValueError("unexpected primary preprint")
    truth=runpy.run_path(str(ROOT/"proofs"/(T+"B")/(T+"B-P001_bounded_elimination")/"check.py"))["truth_check"]
    examples=[]
    for n in (2,4,8):
        menus=list(product((0,1),repeat=n)) if n==2 else [tuple(i%2 for i in range(n))]
        for signs in menus:
            cnf,proof=product_tree(m,n,signs)
            out,info=m["eliminate"](n,cnf,proof,method="depth")
            truth(n,cnf,out)
            assert info["max_displayed_degree"]==info["permitted_degree"]==2*n
            assert info["declarations"]==n-1
            if n<=4:
                base,baseinfo=m["eliminate"](n,cnf,proof,method="count")
                assert baseinfo["branches"]==1<<(n-1)
                truth(n,cnf,base)
            try:
                m["verify_unnamed"](n,cnf,out,2*n-1)
            except ValueError:
                pass
            else:
                raise AssertionError("a lowered formal degree cap was ignored")
            examples.append({"source_variables":n,"named_nodes":len(proof), **info})
    # Reuse of a previously cached empty CNF axiom with intervening lines.
    empty=[{"rule":"axiom","axiom":0,"clause":[]},{"rule":"true","clause":[[]]},
           {"rule":"axiom","axiom":0,"clause":[]}]
    for method in ("depth","count"):
        out,info=m["eliminate"](0,[[]],empty,method=method)
        assert len(out)==1 and info["empty_input_axiom"]==0
    # Dense affine factors, shared previous names, constants and formal aliases.
    cases=runpy.run_path(str(ROOT/"proofs"/(T+"B")/(T+"B-P001_bounded_elimination")/"check.py"))
    x,y,z=map(m["var"],(1,2,3))
    cnf,proof=cases["example"](3,[(m["add"](x,y),m["opposite"](z)),
                                  (m["add"](m["var"](4),x),m["add"](x,z)),
                                  (m["var"](5),m["var"](5))])
    dense,di=m["expand"](3,cnf,proof)
    truth(3,cnf,dense)
    common=m["add"](x,y)
    chain=[(common,z)]
    for name in range(4,11):
        guard=common if name%2 else m["opposite"](common)
        other=m["add"](m["var"](name),x)
        chain.append((guard,other) if name%2 else (other,guard))
    c,chain_proof=cases["example"](3,chain)
    erased,shared=m["eliminate_shared_factor"](3,c,chain_proof,common)
    truth(3,c,erased)
    assert shared["branches"]==2 and shared["declarations"]==8
    try:
        m["eliminate_shared_factor"](3,c,chain_proof,z)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted a factor missing from a later declaration")
    # A multiplier can have higher formal degree than every displayed clause atom.
    single=[[-1],[1]]
    dag=m["Q"]["Dag"](single)
    zero,one=m["ZERO"],m["ONE"]
    multiplied=dag.multiply(dag.true(),zero,m["mul"](x,x))
    unit=dag.combine(multiplied,dag.axiom(0),zero,x)
    dag.resolve(unit,dag.axiom(1),-1)
    assert m["verify_unnamed"](1,single,dag.proof,2)==2
    # A dead earlier declaration occurs twice in a retained but unnormalized factor.
    named=m["A"]["Dag"](1,single)
    dead,_=named.define(x,x)
    live,definition=named.define(x,one)
    eq=m["add"](m["var"](live),x)
    unit=named.combine(named.axiom(0),definition,x,eq)
    unit=named.combine(unit,definition,m["var"](live),eq)
    named.resolve(unit,named.axiom(1),-1)
    rows=[r.copy() for r in named.proof]
    rows[definition]["factors"]=[[[dead],[dead],[1]],[[]]]
    pruned=m["prune"](1,single,rows)
    defs=[r for r in pruned if r["rule"]=="define"]
    assert len(defs)==1 and defs[0]["variable"]==2 and defs[0]["factors"]==[[[1]],[[]]]
    return {"status":"passed","admission_fields":len(doc),"pinned_source_sha256":HASH,"balanced_trees":examples,
            "all_signed_one_gate_cases":4,"largest_achieved_formal_degree":examples[-1]["max_displayed_degree"],
            "repeated_empty_axiom_methods":2,"dense_three_gate_nodes":di["nodes"],
            "one_shared_affine_factor":shared,"zero_product_printed_multiplier_degree":2,
            "normalized_retained_declarations":len(defs)}


if __name__=="__main__":
    print(json.dumps(main(),sort_keys=True))
