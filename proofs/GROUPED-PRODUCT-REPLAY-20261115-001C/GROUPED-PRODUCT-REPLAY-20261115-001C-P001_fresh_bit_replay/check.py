"""Check actual proof rewrites, authenticated reports, a first cubic inference and Boolean witnesses."""
from copy import deepcopy
from itertools import product
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent


def fixture(mod,m,*,next_bit=False,guard_in_inputs=False,raw_sum=False,alias_free=False):
    q=mod["q"]
    var,add,mul=q.var,q.add,q.mul
    z,w,pad1,pad2=range(2*m+1,2*m+5)
    n=pad2
    pairs=tuple((2*i+1,2*i+2) for i in range(m))
    inputs=tuple(range(1,2*m+1))
    literals=(*inputs,-inputs[-1])
    pad=(z,w) if guard_in_inputs else (pad1,pad2)
    cnf=[[lit,a*pad[0],b*pad[1]] for lit in literals for a,b in product((1,-1),repeat=2)]
    dag=mod["named"]["Dag"](n,cnf)
    gates=[]
    pair_defs=[]
    for x,y in pairs:
        p,idx=dag.define(var(x),var(y))
        gates.append((p,x,y,idx))
        pair_defs.append((p,idx))
    p=pair_defs[0][0]
    for other,_ in pair_defs[1:]:
        u,idx=dag.define(var(p),var(other))
        gates.append((u,p,other,idx))
        p=u
    root,implies,all_imply=mod["group"]["and_portals"](dag,gates)
    sum_names=mod["xor"](var(p) for p,_ in pair_defs)
    alias=None if alias_free else dag.define(q.ONE,sum_names)
    u,udef=(None,None) if alias is None else alias
    source_form=sum_names if u is None else var(u)
    s,sdef=dag.define(var(z),source_form)
    assignments=((1,)*len(inputs),(1,)*(len(inputs)-1)+(0,))
    exports=[(mod["assignment_report"](dag,pairs,alpha,pair_defs=pair_defs,alias=alias),alpha)
             for alpha in assignments]
    cut=len(dag.proof)
    units={}
    for j,lit in enumerate(literals):
        idx=4*j
        pos=dag.resolve(dag.axiom(idx),dag.axiom(idx+1),pad[1])
        neg=dag.resolve(dag.axiom(idx+2),dag.axiom(idx+3),pad[1])
        units[lit]=dag.resolve(pos,neg,pad[0])
    root_unit=all_imply
    for v in inputs:
        root_unit=dag.resolve(units[v],root_unit,v)
    reported={}
    for j,(node,alpha) in enumerate(exports):
        for v,b in zip(inputs,alpha):
            lit=v if b else -v
            source=dag.resolve(root_unit,implies[v],root) if j==0 else units[lit]
            node=dag.resolve(source,node,lit)
        reported[sum(i*j for i,j in zip(alpha[::2],alpha[1::2]))%2]=node
    uf=source_form
    if raw_sum and u is not None:
        for b,node in list(reported.items()):
            reported[b]=dag.combine(node,udef,add(uf,mod["bit"](b)),add(uf,sum_names))
        uf=sum_names
    def multiply_reports(multiplier):
        left=dag.multiply(reported[0],uf,multiplier)
        right=dag.multiply(reported[1],add(uf,q.ONE),multiplier)
        return dag.combine(left,right,mul(uf,multiplier),mul(add(uf,q.ONE),multiplier))
    # The gated XOR is selected twice by actual downstream deductions.
    zf=var(z)
    prod=mul(uf,zf)
    first=dag.multiply(reported[0],uf,zf)
    if raw_sum and u is not None:
        # Derive z*U=z*sum(p_i) from the old alias definition.
        up=add(var(u),sum_names)
        bridge=dag.multiply(udef,up,zf)
        sd=dag.combine(sdef,bridge,add(var(s),mul(var(u),zf)),mul(up,zf))
    else:
        sd=sdef
    sf=var(s)
    s_zero=dag.combine(first,sd,prod,add(sf,prod))
    second=dag.multiply(reported[1],add(uf,q.ONE),zf)
    s_eq_z=dag.combine(second,sd,add(prod,zf),add(sf,prod))
    z_zero=dag.combine(s_zero,s_eq_z,sf,add(sf,zf))
    more=None
    if next_bit:
        more=len(dag.proof)
        w_zero=multiply_reports(var(w))
        joined=dag.combine(z_zero,w_zero,zf,var(w))
        pivot=add(zf,var(w))
    else:
        joined,pivot=z_zero,zf
    opposite=multiply_reports(add(q.ONE,pivot))
    dag.delete_false(dag.combine(joined,opposite,pivot,add(q.ONE,pivot)))
    mod["named"]["verify"](n,cnf,dag.proof)
    return n,cnf,dag.proof,cut,pairs,z,{"reports":exports,"first":first,"extra":more,
                                        "xor":u,"gated":s,"root":root,"w":w,"gated_uses":[s_zero,s_eq_z]}


def certificate(mod,next_bit=False):
    n,cnf,proof,cut,pairs,z,info=fixture(mod,2,alias_free=True,next_bit=next_bit)
    mode="parity" if next_bit else "fresh"
    new,trace=mod["replay"](n,cnf,proof,cut,pairs,z,reports=info["reports"],mode=mode)
    return {"n":n,"cnf":cnf,"source_cut":cut,"input_pairs":pairs,"fresh_bit":z,
            "original_proof":proof,"rewritten_proof":new,"prefix_reports":info["reports"],
            "trace":trace,"old_first_gated_multiply":info["first"],
            "old_multiply_by_another_bit":info["extra"]}


def run():
    mod=runpy.run_path(str(HERE/"solver.py"))
    family=mod["ROOT"]/"proofs"/(mod["OLD"]+"A")/(mod["OLD"]+"A-P001_named_substitution")
    truth=runpy.run_path(str(family/"check.py"))["truth_check"]
    out={}
    def attempt(inputs,mode):
        n,cnf,p,cut,pairs,z,data=inputs
        try:
            rows,info=mod["replay"](n,cnf,p,cut,pairs,z,reports=data["reports"],mode=mode)
        except mod["ReplayError"] as exc:
            return {"line":exc.line,"rule":exc.rule,"field":exc.field,"case":exc.case,
                    "first_excess_monomial":exc.monomial}
        assert not rows[-1]["clause"] and info["output_names"]==2*len(pairs)-1
        names=[row for row in rows if row["rule"]=="define"]
        original_pairs={frozenset((mod["var"](x),mod["var"](y))) for x,y in pairs}
        assert not any(frozenset(mod["q"].polynomial(a) for a in row["factors"]) in original_pairs for row in names)
        if len(pairs)<=3:
            truth(n,cnf,rows)
        trace=info.pop("source_to_target")
        inspected={}
        for idx in [data["first"],*data["gated_uses"],*([data["extra"]] if data["extra"] is not None else [])]:
            inspected[idx]=[(tags[idx-cut],rows[tags[idx-cut]]["clause"]) for tags in trace]
        extra={"old_first_multiply_line":data["first"],"old_extra_multiply_line":data["extra"],
               "raw_selected_old_step":p[data["first"]],"traced_conclusions":inspected} if len(pairs)==2 else {}
        return {**info,**extra}
    for k in (2,3,5,9):
        data=fixture(mod,k)
        r=attempt(data,"fresh")
        assert r["cases"]==2
        out[f"{k}_pair_fresh"]=r
        if k==2:
            bad=attempt(data,"direct")
            assert bad["line"]==data[-1]["first"] and bad["field"]=="product"
            out["direct_failure"]=bad
    extra=fixture(mod,2,next_bit=True)
    blocked=attempt(extra,"fresh")
    assert blocked["line"]==extra[-1]["extra"] and blocked["field"]=="product"
    out["next_failure"]=blocked
    for label,vals,mode in [("parity_after_extra",extra,"parity"),
                           ("no_alias_fresh",fixture(mod,2,alias_free=True),"fresh"),
                           ("no_alias_parity",fixture(mod,2,alias_free=True,next_bit=True),"parity"),
                           ("raw_sum_fresh",fixture(mod,2,raw_sum=True),"fresh"),
                           ("raw_sum_parity",fixture(mod,2,next_bit=True,raw_sum=True),"parity"),
                           ("guard_in_input_axioms",fixture(mod,2,guard_in_inputs=True),"fresh")]:
        result=attempt(vals,mode)
        assert result["cases"]==2
        out[label]=result
    # Each failure persists on a three-bit restriction where every target AND gate is zero.
    witnesses=[]
    for vals,fresh,leftover in [(fixture(mod,2),True,"z"),(extra,False,"w")]:
        n,cnf,old,cut,pairs,z,data=vals
        roster=range(1,n+1)
        values=[]
        for a,x,h in product((0,1),repeat=3):
            v={i:0 for i in roster}
            v[1],v[2]=a,x
            v[z]=h if fresh else 1
            if not fresh:
                v[data["w"]]=h
            assert v[3]==0
            Q=sum(v[i]*v[j] for i,j in pairs)%2
            values.append(h*Q)
        assert values==[0]*7+[1]
        witnesses.append({"free":["x1","y1",leftover],"common_AND_names":0,"values":values})
    out["cubic_restrictions"]=witnesses
    # Permit genuine later names local to each branch and check even a multiplier of zero.
    n,cnf,p,cut,pairs,z,data=extra
    def splice(rows,idx):
        return [*p[:idx],*rows,*[
            {**row,**({"parents":[j+len(rows) if j>=idx else j for j in row["parents"]]}
                       if "parents" in row else {})} for row in p[idx:]]]
    later=mod["named"]["Dag"](n,cnf)
    later.live=data["gated"]
    f=mod["add"](mod["var"](data["xor"]),mod["var"](1))
    g=mod["complement"](mod["var"](data["w"]))
    v,decl=later.define(f,g)
    later.boolean(v)
    with_definition=splice(later.proof,cut)
    rewritten,desc=mod["replay"](n,cnf,with_definition,cut,pairs,z,reports=data["reports"],mode="parity")
    assert desc["output_names"]==2*len(pairs)+1
    truth(n,cnf,rewritten)
    out["case_local_extensions"]=desc["output_names"]
    discarded=splice([{"rule":"true","clause":[[]]},
                       {"rule":"multiply","parents":[cut],"chosen":[],
                        "multiplier":[[data["xor"],data["w"]]],"clause":[[]]}],cut)
    try:
        mod["replay"](n,cnf,discarded,cut,pairs,z,reports=data["reports"],mode="fresh")
    except mod["ReplayError"] as err:
        assert (err.line,err.field)==(cut+1,"multiplier")
        out["zero_times_cubic_multiplier"]=[err.line,err.field,err.monomial]
    else:
        raise AssertionError("the cubic multiplier of zero was accepted")
    saved=json.loads((HERE/"rewrite.json").read_text())
    for key in ("original_proof","rewritten_proof"):
        mod["named"]["verify"](saved["n"],saved["cnf"],saved[key])
        truth(saved["n"],saved["cnf"],saved[key])
    expected=certificate(mod)
    assert json.loads(json.dumps(expected))==saved
    direct=attempt(fixture(mod,2,alias_free=True),"direct")
    assert direct["line"]==saved["old_first_gated_multiply"]
    out["saved_direct_failure"]=direct
    out["saved_certificate"]={"source":len(saved["original_proof"]),
                              "target":len(saved["rewritten_proof"]),"checked":True}
    second_saved=json.loads((HERE/"parity_rewrite.json").read_text())
    assert json.loads(json.dumps(certificate(mod,next_bit=True)))==second_saved
    for key in ("original_proof","rewritten_proof"):
        mod["named"]["verify"](second_saved["n"],second_saved["cnf"],second_saved[key])
        truth(second_saved["n"],second_saved["cnf"],second_saved[key])
    extra_raw=attempt(fixture(mod,2,alias_free=True,next_bit=True),"fresh")
    assert extra_raw["line"]==second_saved["old_multiply_by_another_bit"] and extra_raw["field"]=="product"
    out["saved_next_failure"]=extra_raw
    # An already derived clause containing repeated nonlinear disjuncts, including z².
    q=mod["q"]
    for b in (0,1):
        sample=mod["named"]["Dag"](2,[[]])
        f=q.polynomial([[1,1],[1,2],[]])
        known=sample.weaken(sample.true(),(q.ZERO,f,f))
        folded=mod["restrict_known"](sample,known,1,b)
        under_b=q.var(2) if b else q.ONE
        expected=tuple(sorted((q.ZERO,under_b,under_b,mod["complement"](q.add(q.var(1),mod["bit"](b))))))
        assert sample.clauses[folded]==expected
        sample.axiom(0)
        mod["named"]["verify"](2,[[]],sample.proof)
    out["formal_square_and_duplicate_restrictions"]=2
    # Reject a genuine but unsupported import and restore real degree/scope checks before either split.
    n,cnf,p,cut,pairs,z,data=extra
    for case,reports in [("missing_report",data["reports"][:-1]),
                         ("wrong_report",[(data["reports"][0][0],data["reports"][1][1]),data["reports"][1]])]:
        try:
            mod["replay"](n,cnf,p,cut,pairs,z,reports=reports)
        except ValueError as err:
            out[case]=str(err)
        else:
            raise AssertionError(case)
    broken=deepcopy(p)
    broken[data["first"]]["multiplier"]+=[[99999],[99999]]
    try:
        mod["replay"](n,cnf,broken,cut,pairs,z,reports=data["reports"])
    except ValueError as err:
        out["canceled_future_variable"]=str(err)
    else:
        raise AssertionError("lost written-scope check")
    out["status"]="passed"
    return out


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
