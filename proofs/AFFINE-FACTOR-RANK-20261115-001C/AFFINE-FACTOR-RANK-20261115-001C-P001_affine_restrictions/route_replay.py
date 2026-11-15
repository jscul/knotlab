"""Run a raw guarded proof through signed projection and two different affine partitions."""
from pathlib import Path
import runpy


def run(root,sem):
    from pysat.solvers import Solver
    prior="PRODUCT-NAME-TRANSFER-20261115-001A"
    accepted=runpy.run_path(str(root/"proofs"/prior/(prior+"-P001_named_substitution")/"check.py"))
    family=accepted["family"]
    n=3
    p="ROUTE-PARITY-TRANSFER-20261115-001"
    a=family(p+"A","literal_projection")
    b=family(p+"B","dag_transport")
    reasons=family(p+"D","encoded_lower_bound")
    old=family("QUADRATIC-ROUTE-TRANSFER-20261115-001C","encoded_products")
    roster=a["compiler"]().clauses_on(n)
    raw,pins,images=a["build_projection"](n,roster,range(len(roster)))
    target_n=max(images)
    cnf=raw.cnf+[[v] for v in pins]
    with Solver(name="g3",bootstrap_with=cnf,with_proof=True) as sat:
        assert not sat.solve()
        additions=[list(map(int,line.split()[:-1])) for line in sat.get_proof() if not line.startswith("d ")]
    if not additions or additions[-1]:
        additions.append([])
    ordinary,end=reasons["add_reasons"](cnf,additions,b)
    named,q=accepted["named"],accepted["q"]
    dag=named.Dag(target_n,cnf)
    refs={}
    controls=[]
    for j in old["ancestors"](ordinary,end):
        row=ordinary[j]
        if row["rule"]=="axiom":
            index=row["axiom"]
            node=dag.axiom(index)
            if not controls and a["clause_image"](cnf[index],images,n+1) is not None:
                lit=next(x for x in cnf[index] if abs(images[abs(x)])<=n)
                source_signal=next(i for i in range(1,n+1) if i!=abs(images[abs(lit)]))
                u=raw.signals[source_signal]
                # A different raw coordinate for the same signed/possibly complemented source variable.
                h=next(i for i in sorted(images) if i!=u and abs(images[i])==abs(images[u]))
                controls=[q.var(u),q.var(h)]
                f=q.literal(lit)
                node=accepted["two_levels"](dag,node,f,q.add(f,controls[0]),controls[1])
        elif row["rule"]=="resolve":
            node=dag.resolve(*(refs[k] for k in row["parents"]),old["signed"](row["pivot"]))
        else:
            assert row["rule"]=="weaken"
            node=dag.weaken(refs[row["parents"][0]],q.signed_clause(old["signed"](x) for x in row["clause"]))
        refs[j]=node
    assert refs[end]==len(dag.proof)-1 and len(controls)==2
    live=set(named.ancestors(target_n,cnf,dag.proof,include_declarations=False))
    used=[sum(dag.proof[i].get("parents",[]).count(j) for i in live)
          for j,row in enumerate(dag.proof) if row["rule"]=="define"]
    assert len(used)==2 and min(used)>=2
    projected,_=named.translated(n,roster,target_n,cnf,images,dag.proof)
    sigma=q.substitution(n,q.image_map(n,target_n,images))
    smaller=[sigma(f) for f in controls]
    target_out,ts=sem["eliminate"](target_n,cnf,dag.proof,controls)
    out,ss=sem["eliminate"](n,roster,projected,smaller)
    assert ts["rank"]==2 and ts["cases"]==4 and ss["rank"]==1 and ss["cases"]==2
    assert ts["factor_cases"]["sum"]==4 and ss["factor_cases"]["sum"]==2
    truth=family("PRODUCT-NAME-TRANSFER-20261115-001B","bounded_elimination")["truth_check"]
    truth(n,roster,out)
    return {"raw_stages":len(raw.stages),"raw_strict_clauses":len(raw.cnf),"guard_pins":len(pins),
            "uses_of_each_definition":used,"raw_named_nodes":len(dag.proof),"source_named_nodes":len(projected),
            "raw_unnamed":ts,"source_unnamed":ss,"checked_source_assignments_per_line":1<<n}
