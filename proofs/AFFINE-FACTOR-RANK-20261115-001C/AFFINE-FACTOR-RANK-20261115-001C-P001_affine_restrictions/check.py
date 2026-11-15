"""Independent finite truth-table, degree-two proof, search and signed routing controls."""
from itertools import combinations, product
from functools import lru_cache
import json
import os
from pathlib import Path
from random import Random
import runpy
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def spaces(n):
    """Enumerate by closure under XOR, with no call to the proof's elimination routine."""
    found={frozenset({0}):()}
    todo=list(found)
    for members in todo:
        for j in range(1,1<<n):
            if j not in members:
                new=members | {v^j for v in members}
                if new not in found:
                    found[new]=found[members]+(j,)
                    todo.append(new)
    return sorted(found.values(),key=len)


def form(sem,mask):
    return sem["polynomial"]([(i,) for i in range(1,mask.bit_length()) if mask>>i&1]+
                             ([()] if mask & 1 else []))


def allowed_tables(n):
    return [sum(((((i&v).bit_count()&1)^c)<<i) for i in range(1<<n))
            for v in range(1<<n) for c in (0,1)]


def fibre_masks(n,basis):
    parts={}
    for x in range(1<<n):
        key=tuple((g&x).bit_count()&1 for g in basis)
        parts[key]=parts.get(key,0)|(1<<x)
    return parts.values()


def all_values(n,gates):
    universe=(1<<(1<<n))-1
    values={i:sum(1<<x for x in range(1<<n) if x>>(i-1)&1) for i in range(1,n+1)}
    def eval_affine(f):
        v=0
        for term in f:
            v^=universe if not term else values[term[0]]
        return v
    out=[]
    for v,(f,g) in enumerate(gates,n+1):
        values[v]=eval_affine(f)&eval_affine(g)
        out.append(values[v])
    return out


def compare(sem,example):
    rng=Random(31967)
    programs=[]
    for f,g in product(range(8),repeat=2):
        programs.append((2,[(form(sem,f),form(sem,g))]))
    for _ in range(72):
        gates=[]
        for available in range(3,3+rng.randrange(2,8)):
            gates.append(tuple(form(sem,rng.randrange(1<<(available+1))) for _ in range(2)))
        programs.append((3,gates))
    comparisons=budgets=0
    for n,gates in programs:
        cnf,proof=example(n,gates)
        defs=sem["bounded"]["declarations"](n,proof)
        values=all_values(n,gates)
        functions=allowed_tables(n)
        best=n
        for rows in spaces(n):
            basis=[form(sem,i<<1) for i in rows]
            folds=sem["ranked"]["AffineBasis"](n,basis)
            good=all(any((y^linear)&part==0 for linear in functions)
                     for part in fibre_masks(n,rows) for y in values)
            failure=sem["first_failure"](n,defs,folds)
            assert (failure is None)==good
            if good:
                best=min(best,len(rows))
            else:
                corners=failure.corners
                points=[sum(bit<<i for i,bit in enumerate(p)) for p in corners]
                assert len(set(points))==4 and points[0]^points[1]^points[2]^points[3]==0
                assert all(len({(p&j).bit_count()&1 for p in points})==1 for j in rows)
                truth=values[failure.variable-n-1]
                assert sum(truth>>p&1 for p in points)%2==1
            comparisons+=1
        for budget in range(best+1):
            got=sem["find_controls"](n,cnf,proof,budget)
            assert (got is not None)==(budget>=best)
            if got is not None:
                assert len(got)==best
            budgets+=1
    return {"programs":len(programs),"supplied_spaces":comparisons,"search_budgets":budgets}


def verification_reduction(sem,example):
    """z1,z2,z3 form a supplied basis. A successful input assignment leaves xy in its case."""
    var,opp=sem["var"],sem["opposite"]
    roster=list(product((0,1),repeat=3))
    ok=bad=0
    for mask in range(256):
        gates=[]
        def gate(f,g):
            gates.append((f,g))
            return var(5+len(gates))
        total=sem["ONE"]
        for j,signs in enumerate(roster):
            if mask>>j&1:
                # Literal is false on the indicated source bit. The entire disjunction
                # is false at exactly the signed row being forbidden.
                falses=[var(i+1) if bit else opp(var(i+1)) for i,bit in enumerate(signs)]
                false=gate(gate(falses[0],falses[1]),falses[2])
                total=gate(total,opp(false))
        partial=gate(total,var(4))
        gate(partial,var(5))
        cnf,proof=example(5,gates)
        sem["named"]["verify"](5,cnf,proof)
        obs=sem["ranked"]["AffineBasis"](5,[var(i) for i in (1,2,3)])
        failed=sem["first_failure"](5,sem["bounded"]["declarations"](5,proof),obs)
        if mask==255:
            assert failed is None
            ok+=1
        else:
            assert failed is not None and failed.variable==5+len(gates)
            bad+=1
    return {"valid_observations":ok,"invalid_observations":bad}


def graph_cases(sem,example):
    var=sem["var"]
    edges=list(combinations(range(1,5),2))
    for mask in range(1<<len(edges)):
        chosen=[edge for i,edge in enumerate(edges) if mask>>i&1]
        expected=min(bits.bit_count() for bits in range(16)
                     if all((bits>>(i-1))&1 or (bits>>(j-1))&1 for i,j in chosen))
        cnf,proof=example(4,[(var(i),var(j)) for i,j in chosen])
        assert len(sem["find_controls"](4,cnf,proof,4))==expected
    return 1<<len(edges)


def adaptive_example(sem):
    """Find the smallest affine partition for ax, by, and their product on all 16 inputs."""
    var=sem["var"]
    names=all_values(4,[(var(1),var(3)),(var(2),var(4)),(var(5),var(6))])
    affine=allowed_tables(4)
    all_parts=set()
    usable=set()
    fixed=[]
    for rows in spaces(4):
        family=list(fibre_masks(4,rows))
        all_parts.update(family)
        usable_here=[part for part in family
                     if all(any(((output^f)&part)==0 for f in affine) for output in names)]
        usable.update(usable_here)
        if len(usable_here)==len(family):
            fixed.append(len(family))

    @lru_cache(None)
    def minimum(remaining):
        if not remaining:
            return 0
        first=remaining & -remaining
        return 1+min(minimum(remaining^part) for part in usable
                     if part&first and (part&remaining)==part)

    tree={}
    for point in range(16):
        a,b,x=(point>>i&1 for i in range(3))
        answers=(a,b,x) if a and b else (a,b)
        tree[answers]=tree.get(answers,0) | (1<<point)
    assert all(part in usable for part in tree.values())
    sizes=sorted(part.bit_count() for part in tree.values())
    best=minimum((1<<16)-1)
    assert (len(all_parts),len(usable),min(fixed),best,sizes)==(307,163,8,5,[2,2,4,4,4])
    return {"all_affine_parts":len(all_parts),"valid_parts":len(usable),
            "fixed_parts":min(fixed),"fewest_parts":best,"leaf_sizes":sizes}


def check_written_forms(sem,example):
    var=sem["var"]
    cnf,proof=example(2,[(var(1),var(1)),(var(2),var(2))])
    gate=next(row for row in proof if row.get("rule")=="define" and row["variable"]==4)
    factor=gate["factors"][0]
    gate["factors"][0]=factor+[[3],[3]]
    out,_=sem["eliminate"](2,cnf,proof,[])
    sem["q"]["verify"](2,cnf,out)
    gate["factors"][0]=factor+[[4],[4]]
    try:
        sem["eliminate"](2,cnf,proof,[])
    except ValueError as exc:
        assert "invalid polynomial variable" in str(exc)
    else:
        raise AssertionError("a canceled reference to the name being defined was accepted")

    rows=[{"rule":"true","clause":[[]]},
          {"rule":"multiply","parents":[0],"chosen":[],"multiplier":[[1,1]],"clause":[[]]},
          {"rule":"axiom","axiom":0,"clause":[]}]
    out,_=sem["eliminate"](1,[[]],rows,[])
    assert any(row.get("multiplier")==[[1,1]] for row in out)
    rows[1]["multiplier"]=[[1,1,1]]
    try:
        sem["eliminate"](1,[[]],rows,[])
    except ValueError as exc:
        assert "degree above two" in str(exc)
    else:
        raise AssertionError("a cubic displayed multiplier of zero was accepted")
    return {"canceled_earlier_name":"accepted","canceled_undeclared_name":"rejected",
            "quadratic_multiplier_of_zero":"accepted","cubic_multiplier_of_zero":"rejected"}


def check_examples(sem,example,truth,static):
    var,add,opp=sem["var"],sem["add"],sem["opposite"]
    # Each pair z_i,z_i+u forces a new explicit slope, but one observation u suffices.
    n=8
    u=var(1)
    pairs=[(var(i),add(var(i),u)) for i in range(2,n+1)]
    cnf,proof=example(n,pairs)
    literal_rank=static["minimum_proof_span"](n,cnf,proof)["rank"]
    assert literal_rank==n-1 and sem["find_controls"](n,cnf,proof,0) is None
    found=sem["find_controls"](n,cnf,proof,1)
    assert tuple(found)==(u,)
    out,stats=sem["eliminate"](n,cnf,proof,[u,opp(u),sem["ONE"]])
    assert stats["rank"]==1 and stats["factor_cases"]["sum"]==2*(n-1)
    truth(n,cnf,out)
    # Both old names reuse the supplied factors, but their product at 11 is xy.
    f,g,x,y=map(var,(1,2,3,4))
    nested=[(f,x),(g,y),(var(5),var(6))]
    cnf,proof=example(4,nested)
    try:
        sem["eliminate"](4,cnf,proof,[f,g])
    except sem["NonAffineProduct"] as failure:
        assert failure.case==(1,1) and failure.variable==7
    else:
        raise AssertionError("a remaining xy on case 11 was accepted")
    assert sem["find_controls"](4,cnf,proof,2) is None
    assert len(sem["find_controls"](4,cnf,proof,3))==3
    # A program using just two original bits can encode AND and still becomes
    # affine after fixing either bit. A dependent factor sum can be the unique best choice.
    cnf,proof=example(3,[(f,g),(add(f,g),add(var(4),x))])
    span=sem["find_controls"](3,cnf,proof,1)
    assert tuple(span)==(add(f,g),)
    out,unique=sem["eliminate"](3,cnf,proof,span)
    truth(3,cnf,out)
    # A real zero-rank square and a complemented duplicate in a proof reusing its last empty axiom.
    cnf,proof=example(2,[(f,f),(var(3),opp(var(3)))])
    out,square=sem["eliminate"](2,cnf,proof,[])
    truth(2,cnf,out)
    empty=[{"rule":"axiom","axiom":0,"clause":[]},{"rule":"true","clause":[[]]},
           {"rule":"axiom","axiom":0,"clause":[]}]
    emptyout,emptyinfo=sem["eliminate"](0,[[]],empty,[])
    sem["q"]["verify"](0,[[]],emptyout)
    return {"variable_static_rank":literal_rank,"semantic_rank":stats["rank"],"seven_gates":stats,
            "ancestor_only_minimum":3,"unique_sum_controls":unique["rank"],"zero_rank_square_cases":square["cases"],
            "repeated_empty_axiom_final_empty":emptyout[-1]["clause"]==[]}


def main():
    sem=runpy.run_path(str(HERE/"solver.py"))
    b=ROOT/"proofs"/(sem["OLD"]+"B")/(sem["OLD"]+"B-P001_bounded_elimination")/"check.py"
    old=runpy.run_path(str(b))
    static=sem["component"](sem["EPIC"]+"B","finding_factors")
    args=(sem,old["example"])
    result={"cube_oracle":compare(*args),"checking_reduction":verification_reduction(*args),
            "four_vertex_graphs":graph_cases(*args),"examples":check_examples(*args,old["truth_check"],static)}
    result["adaptive"]=adaptive_example(sem)
    result["written_forms"]=check_written_forms(*args)
    result["raw_route"]=runpy.run_path(str(HERE/"route_replay.py"))["run"](ROOT,sem)
    result["status"]="passed"
    return result


if __name__=="__main__":
    venv=ROOT/".venv/bin/python"
    if venv.is_file() and Path(sys.prefix).resolve()!=venv.parent.parent.resolve():
        os.execv(str(venv),[str(venv),"-B",str(Path(__file__).resolve())])
    print(json.dumps(main(),sort_keys=True))
