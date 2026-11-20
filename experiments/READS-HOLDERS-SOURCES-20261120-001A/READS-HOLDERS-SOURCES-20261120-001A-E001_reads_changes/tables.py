"""Ordered studies of the split, the separation control, and the alternate law."""
from fractions import Fraction
from itertools import combinations,product
from functools import reduce
from operator import xor
import json
import os
import subprocess
import sys

from operations import (BASELINE, ID, LAW, OUT, ROOT, WORDS, action, change, fit, full_table, inversion, labels,
                        marginal_variation, mask, np, parity, probability_table, questions, read, save,
                        score, sha, signed, times, weighting)
from holdings import certify,next_stage,parity_ties,nae_units


def split(k=2,pad=False):
    stars=[(3*i,3*i+1,3*i+2) for i in range(k)]
    a=[(change(3*i),read(3*i,3*i+1)) for i in range(k)]
    b=[(change(3*i+2),read(3*i+2)) for i in range(k)]
    if pad:
        a.append((change(3),read(3)));b.append((change(4),read(4)))
    return stars,a,b


def table(f,a,b,six=True,solver=True):
    aq=questions(labels(a),"A") if six else [(r,) for r in a[0]]
    bq=questions(labels(b),"B") if six else [(r,) for r in b[0]]
    if six:
        assert all(times(*q)==ID for q in aq)
        assert [times(*q) for q in bq]==[ID,ID,signed(ID,-1)]
    rows=full_table(f,aq,bq)
    result=dict(alice=aq,bob=bq,rows=rows,marginal_total_variation=marginal_variation(rows,aq,bq),
                sign_sum_entries=inversion(f,aq,bq,rows))
    if six:
        result["equal_at_shared"]=score(rows)
    if solver:
        result["common_explanation"]=fit(rows,aq,bq)
    return result


def compare_old(rows):
    old=json.loads(BASELINE.read_text())
    diffs=[]
    assert list(WORDS)==old["order"]
    for r,o in zip(rows,old["six"],strict=True):
        a,b=r["settings"]; assert o["inputs"]==[a,b+3]
        for i,p in enumerate([Fraction(v,r["denominator"]) for v in r["numerators"]]):
            for label,val in (("entries",Fraction(o["numerator"][i],o["denominator"])),
                              ("projectors",Fraction(o["born_numerators_over_256"][i],256))):
                if p!=val: diffs.append([label,a,b,i,str(p),str(val)])
    return dict(source_sha256=sha(BASELINE),n_probability_entries=576,n_projector_entries=576,differences=diffs)


def canonical(stars,law):
    # The SAT/projection certificate supplies the complete local allowed relation to the canonical checker.
    f=weighting(stars,law);result=[]
    for s in stars:
        names=[f"b{i}" for i in range(len(s))]
        words={tuple(x>>b&1 for b in s) for x in range(len(f)) if f[x]}
        forbidden=set(product((0,1),repeat=len(s)))-words
        clauses=[" ".join(("~" if v else "")+n for v,n in zip(w,names)) for w in sorted(forbidden)]
        cmd=[sys.executable,"-B","-m","knotlab","check","--cnf",";".join(clauses),"--loops",*names[:-1],"--contact",names[-1],"--json"]
        checked=json.loads(subprocess.check_output(cmd,cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(ROOT/"tools"))))
        result.append(dict(places=s,allowed=sorted(words),canonical=checked["is_knot"]))
    return result


def get_logical(stars):
    n=1+max(map(max,stars))
    for size in range(2,n-1):
        for a in combinations(range(n),size):
            b=sorted(set(range(n))-set(a));am,bm=mask(a),mask(b)
            proof=parity_ties(stars,a,b)
            if proof["ties"]<2:continue
            zrows=proof["joint_reads"];trows=proof["joint_changes"]
            alls=[reduce(xor,(w for i,w in enumerate(trows) if s>>i&1),0) for s in range(1<<len(trows))]
            for z1,z2 in combinations(zrows,2):
                bysig={(parity(t&z1&am),parity(t&z2&am)):t for t in alls}
                if (1,0) not in bysig or (0,1) not in bysig:continue
                xs=[bysig[1,0],bysig[0,1]];zs=[z1,z2]
                sides=[[( (x&s,0,1), (0,z&s,1) ) for x,z in zip(xs,zs)] for s in (am,bm)]
                return dict(alice=a,bob=b,rank=proof["ties"],xs=xs,zs=zs),sides
    return None,None


def step3():
    stars,a,b=split();f=weighting(stars,"parity");main=table(f,a,b)
    main["prior_comparison"]=compare_old(main["rows"])
    assert main["prior_comparison"]["differences"]==[] and main["equal_at_shared"]=="1"
    # Physical incoherent mixture: average each nonzero basis vector's complete probabilities.
    basis_inputs=np.nonzero(f)[0]
    aq,bq=main["alice"],main["bob"]
    p=[]
    for i in basis_inputs:
        v=np.zeros_like(f);v[i]=1
        p.append(probability_table(full_table(v,aq,bq)))
    mixture=[]
    from math import lcm
    for s in range(9):
        vals=[sum(w[s][i] for w in p)/len(p) for i in range(64)]
        d=lcm(*(v.denominator for v in vals))
        mixture.append(dict(settings=[s//3,s%3],numerators=[int(v*d) for v in vals],denominator=d))
    control=dict(rows=mixture,equal_at_shared=score(mixture),common_explanation=fit(mixture,aq,bq))
    controls={}
    candidates={"one":[[0,1,2]],"two_disjoint":stars,"share_two":[[0,1,2],[0,1,3]],
                "share_one":[[0,1,2],[2,3,4]],"three_predecessors":[[0,1,3],[0,2,4],[1,2,5]]}
    for name,holds in candidates.items():
        entry=dict(stars=holds,laws={})
        for law in LAW:
            step,new=next_stage(holds,law)
            entry["laws"][law]=dict(canonical=canonical(holds,law),step=step,grown=new)
        for tag,source in (("source",holds),("grown",entry["laws"]["parity"]["grown"])):
            if source is None or max(map(max,source))>=10:continue
            best,sides=get_logical(source)
            if best:
                q=table(weighting(source,"parity"),*sides,solver=False)
                best.update(game=score(q["rows"]),mismatches=compare_old(q["rows"])["differences"])
            entry[tag+"_logical"]=best
        controls[name]=entry
    save("split_parity.json",dict(main=main,ordinary_mixture=control,controls=controls))


def step4_separated():
    stars=[(0,1,2),(2,3,4)];a=[(change(0),read(0,1))];b=[(change(4),read(3,4))]
    results={}
    for law in LAW:
        f=weighting(stars,law)
        r=table(f,a,b,six=False)
        conditional=[]
        for h in (0,1):
            coeff=np.array([[int(f[(i & 3) | (h<<2) | ((j & 3)<<3)]) for j in range(4)] for i in range(4)])
            assert np.linalg.matrix_rank(coeff)==1
            conditional.append(dict(unread=h,coefficients=coeff.tolist(),weight=str(Fraction(int((coeff**2).sum()),int(f@f)))))
        r["conditioned"]=conditional
        results[law]=r
    save("separation.json",results)


def step6():
    result={}
    for law in LAW:
        cs={}
        for k in (1,2):
            stars,a,b=split(k);f=weighting(stars,law);states=set(int(i) for i in np.nonzero(f)[0])
            trans=[t for t in range(len(f)) if {x^t for x in states}==states]
            orbits={min(x^t for t in trans) for x in states}
            moves={x:sorted(x^y for y in states) for x in sorted(states)}
            single_changes=nx_graph_components(states,moves)
            item=dict(translations=trans,differences=moves,orbits=sorted(orbits),fixed_space_dimension=len(orbits),
                      one_place_legal_motion_components=single_changes)
            if k==1:
                item["intrinsic"]=table(f,a,b,six=False)
                _,a,b=split(1,pad=True)
                item["six_with_local_zeros"]=table(weighting(stars,law,5,(3,4)),a,b)
            else:
                item["six"]=table(f,a,b)
            cs[k]=item
        result[law]=cs
    save("alternate_law.json",result)


def nx_graph_components(states,moves):
    import networkx as nx
    g=nx.Graph();g.add_nodes_from(states)
    for x in states:
        for t in moves[x]:
            if t.bit_count()==1:
                g.add_edge(x,x^t)
    return sorted(sorted(c) for c in nx.connected_components(g))


def step7_counts():
    octob=[]
    for x in range(8):
        # One signed hidden bit for each of the clauses excluding 000 and 111, Theorem 3.
        terms=[(-1)**(h0+h1)*int(not h0 or x==0)*int(not h1 or x==7) for h0,h1 in product((0,1),repeat=2)]
        assert sum(terms)==int(x not in (0,7))
        octob.append(dict(word=x,terms=terms,sum=sum(terms)))
    f=weighting([(0,1,2)],"nae")
    out=[]
    for word in [read(*[b for b in range(3) if z>>b&1]) for z in range(8)]+[change(0)]:
        vs=[f+sign*action(word,f) for sign in (1,-1)]
        norms2=[int(v@v) for v in vs];norms1=[int(np.abs(v).sum()) for v in vs]
        probs=lambda a: [str(Fraction(v,sum(a))) for v in a]
        out.append(dict(word=word,squared=probs(norms2),absolute=probs(norms1)))
    save("signed_counts.json",dict(october=octob,readings=out))


def minimum_census():
    """Exhaust complete named, unordered connected sources through five physical distinctions, including repeats."""
    from itertools import combinations_with_replacement
    from collections import Counter
    import networkx as nx
    items=[]
    for n in range(3,6):
        candidates=[p for size in range(3,n+1) for p in combinations(range(n),size)]
        for m in range(1,2*n//3+1):
            for stars in combinations_with_replacement(candidates,m):
                occ=Counter(b for h in stars for b in h)
                if len(occ)!=n or max(occ.values())>2:continue
                g=nx.Graph();g.add_nodes_from(range(m))
                g.add_edges_from((i,j) for i,j in combinations(range(m),2) if set(stars[i])&set(stars[j]))
                if not nx.is_connected(g):continue
                check=certify(stars,"parity")
                if not all(check):continue
                step,new=next_stage(stars,"parity")
                if new is not None:
                    assert 1+max(map(max,new))>5 or step["status"]=="closed"
                best=0
                if new is not None and 1+max(map(max,new))<=5:
                    width=1+max(map(max,new))
                    best=max(parity_ties(new,q,sorted(set(range(width))-set(q)))["ties"]
                             for a in range(1,width) for q in combinations(range(width),a))
                items.append(dict(n=n,m=m,stars=stars,next_status=step["status"],next_width=step.get("distinctions"),
                                  next_eligible_rank=best))
    assert all(x["next_eligible_rank"]<2 for x in items)
    controls=json.loads((OUT/"split_parity.json").read_text())["controls"]
    six=controls["three_predecessors"]["laws"]["parity"]["grown"]
    ex=parity_ties(six,[0,2,5],[1,3,4])
    assert ex["ties"]==3
    save("minimum.json",dict(named_lawful_connected_sources=items,six_distinction_reached_rank_three=ex))
