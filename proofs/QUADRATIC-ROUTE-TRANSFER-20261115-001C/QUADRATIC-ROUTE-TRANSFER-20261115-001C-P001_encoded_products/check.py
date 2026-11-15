"""Translate actual pinned route refutations containing two mixed, live products."""
from functools import cache
from itertools import product
import json
import os
from pathlib import Path
import runpy
import sys


def family(root, ticket, slug, filename="check.py"):
    return runpy.run_path(str(root/"proofs"/ticket/(ticket+"-P001_"+slug)/filename))


def ancestors(proof,end):
    seen=set()
    todo=[end]
    while todo:
        i=todo.pop()
        if i not in seen:
            seen.add(i)
            todo.extend(proof[i].get("parents",()))
    return sorted(seen)


def signed(pair):
    mask,b=pair
    assert mask.bit_count()==1
    return mask.bit_length()*(1 if b else -1)


def actual_dag(q,ordinary,end,cnf,raw,projection,source_n,a):
    dag=q["Dag"](cnf)
    refs={}
    inserted=False
    for i in ancestors(ordinary,end):
        row=ordinary[i]
        rule=row["rule"]
        if rule=="axiom":
            node=dag.axiom(row["axiom"])
            if not inserted and a["clause_image"](cnf[row["axiom"]],projection,source_n+1) is not None:
                chosen=next(x for x in cnf[row["axiom"]] if abs(projection[abs(x)])<=source_n)
                target_name=next(k for k in range(1,source_n+1) if k!=abs(projection[abs(chosen)]))
                factor=q["var"](raw.signals[target_name])
                f=q["literal"](chosen)
                opposite=q["add"](q["ONE"],factor)
                first=dag.multiply(node,f,factor)
                second=dag.multiply(node,f,opposite)
                new=dag.combine(first,second,q["mul"](f,factor),q["mul"](f,opposite))
                rebuilt=dag.contract_all(new)
                assert dag.clauses[rebuilt]==dag.clauses[node]
                inserted=True
                node=rebuilt
        elif rule=="resolve":
            left,right=(refs[j] for j in row["parents"])
            node=dag.resolve(left,right,signed(row["pivot"]))
        else:
            assert rule=="weaken"
            node=dag.weaken(refs[row["parents"][0]],q["signed_clause"](signed(lit) for lit in row["clause"]))
        assert dag.clauses[node]==q["signed_clause"](signed(atom) for atom in row["clause"])
        refs[i]=node
    assert inserted and refs[end]==len(dag.proof)-1
    return dag.proof


def evaluate_proof(n,cnf,proof):
    universe=(1 << (1<<n))-1
    varmask={i:sum(1<<t for t in range(1<<n) if t>>(i-1)&1) for i in range(1,n+1)}
    @cache
    def solutions(polynomial):
        values=0
        for term in polynomial:
            mask=universe
            for v in term:
                mask &= varmask[v]
            values ^= mask
        return universe ^ values
    meanings=[]
    for node in proof:
        meaning=0
        for p in node["clause"]:
            meaning |= solutions(tuple(map(tuple,p)))
        if node["rule"]=="axiom":
            expected=0
            for lit in cnf[node["axiom"]]:
                expected |= varmask[lit] if lit>0 else (universe^varmask[-lit])
            assert meaning==expected
        elif not node.get("parents"):
            assert meaning==universe
        else:
            joint=universe
            for parent in node["parents"]:
                joint &= meanings[parent]
            assert joint & ~meaning == 0
        meanings.append(meaning)
    assert meanings and not meanings[-1]
    mixed=[i for i in ancestors(proof,len(proof)-1) if proof[i]["rule"]=="multiply" and
           any(len(m)==2 and m[0]!=m[1] for p in proof[i]["clause"] for m in p)]
    assert len(mixed)>=2
    return mixed


def case(n,roster,selected,solver_type,a,b,d,q):
    raw,pins,images=a["build_projection"](n,roster,selected)
    source=[roster[i] for i in selected]
    cnf=raw.cnf+[[g] for g in pins]
    with solver_type(name="g3",bootstrap_with=cnf,with_proof=True) as solver:
        assert not solver.solve()
        additions=[list(map(int,l.split()[:-1])) for l in solver.get_proof() if not l.startswith("d ")]
    if not additions or additions[-1]:
        additions.append([])
    ordinary,end=d["add_reasons"](cnf,additions,b)
    target=actual_dag(q,ordinary,end,cnf,raw,images,n,a)
    projected,stats=q["translated"](n,source,max(images),cnf,images,target)
    mixed=evaluate_proof(n,source,projected)
    assert len(projected)<=2*len(target)
    # Retain all old conclusions but corrupt a multiplier to an actual cubic.
    bad=[dict(node) for node in projected]
    bad[mixed[0]]["multiplier"]=[[1,2,3]]
    try:
        q["verify"](n,source,bad)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted a displayed cubic multiplier")
    return {"stages":len(raw.stages),"strict_clauses":len(raw.cnf),"guard_pins":len(pins),
            "target_nodes":len(target),"source_nodes":len(projected),"live_source_mixed_products":len(mixed),
            "truth_assignments_per_source_line":1<<n,"cubic_control_rejected":True,
            "source_axiom_repairs":stats["repairs"]}


def main(root):
    from pysat.solvers import Solver
    old="ROUTE-PARITY-TRANSFER-20261115-001"
    a=family(root,old+"A","literal_projection")
    b=family(root,old+"B","dag_transport")
    d=family(root,old+"D","encoded_lower_bound")
    q=family(root,"QUADRATIC-ROUTE-TRANSFER-20261115-001A","quadratic_substitution","solver.py")
    r3=a["compiler"]().clauses_on(3)
    r4=a["compiler"]().clauses_on(4)
    # A repeated row in the actual list, one extra active fourth-variable slot on fixed wiring.
    sparse=r3+[r3[2]]
    selected=sorted([*(i for i,r in enumerate(r4) if r in r3),13])
    return {"status":"passed","listed":case(3,sparse,range(len(sparse)),Solver,a,b,d,q),
            "fixed":case(4,r4,selected,Solver,a,b,d,q)}


if __name__=="__main__":
    root=Path(__file__).resolve().parents[3]
    python=root/".venv/bin/python"
    if python.exists() and Path(sys.prefix).resolve()!=python.parent.parent.resolve():
        os.execv(str(python),[str(python),"-B",str(Path(__file__).resolve())])
    print(json.dumps(main(root),sort_keys=True))
