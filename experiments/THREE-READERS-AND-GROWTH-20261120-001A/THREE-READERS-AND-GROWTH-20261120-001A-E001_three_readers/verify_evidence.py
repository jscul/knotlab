"""Verify exact probability certificates and compare marked-clause contraction with literal words."""
from collections import Counter
from fractions import Fraction as F
from itertools import combinations
from math import prod
import json
import numpy as np
from completions import OUT,literal
from three import behavior,full_certificate,save,seq_prob,singleton,strategy_matrix
from certificates import SIZES
from holdings import certify,next_stage


def verify_one(rows,cert,sizes=SIZES):
    a,ss=strategy_matrix(sizes);target=sum((seq_prob(r) for r in rows),[])
    assert cert["lists"]==len(ss) and all(sum(seq_prob(r))==1 for r in rows)
    if cert["local"]:
        incidence=[F(0) for r in target];total=F(0)
        for j,q in cert["mixture"]:
            w=F(q);assert w>=0;total+=w
            for r in a.indices[a.indptr[j]:a.indptr[j+1]]:incidence[r]+=w
        assert incidence==target and total==1
    else:
        coeff=[0]*len(target)
        for i,v in cert["inequality"]:coeff[i]=v
        bound=max(sum(coeff[r] for r in a.indices[a.indptr[j]:a.indptr[j+1]]) for j in range(len(ss)))
        score=sum(v*q for v,q in zip(coeff,target))
        assert bound==cert["bound"] and score==F(cert["value"]) and score>bound


def independent_branches(arities):
    overlaps=[F(1) if q is None else F(2**(q-1)-2,2**(q-1)-1) for q in arities]
    def same_change(a,b):
        if a in (0,7) or b in (0,7):
            return F(0)
        return prod((v for i,v in enumerate(overlaps) if ((a^b)>>i)&1),start=F(1))
    return [[same_change(a,b) for b in range(8)] for a in range(8)]


def tree_controls(samples):
    signatures={}
    for arities in ((3,3,3),(3,3,4),(3,3,5),(3,4,4),(3,3,None)):
        terminal=[[0,1,2]]
        nxt=3
        for i,q in enumerate(arities):
            if q is not None:
                terminal.append([i,*range(nxt,nxt+q-1)]);nxt+=q-1
        targets=[terminal,terminal+[[3,nxt,nxt+1]]]
        marked=[0,1,2];pred=independent_branches(arities)
        for stars in targets:
            f=literal(stars,marked,"nae");g=f.T @ f
            assert all(F(int(g[a,b]),int(g[1,1]))==pred[a][b] for a in range(8) for b in range(8))
        outcome=behavior(g,singleton(3));verify_one(outcome["rows"],outcome["common"])
        px=seq_prob(outcome["rows"][0])
        gaps=[sum(v for word,v in enumerate(px) if all(not (word>>i)&1 for i in pair))-F(2,3)
              for pair in combinations(range(3),2)]
        gap=px[0]-F(1,2)
        assert outcome["common"]["local"]==(max([gap,*gaps])<=0)
        signatures["/".join(str(q) if q else "loose" for q in arities)]=dict(score=outcome["m"],
                    pair_excesses=list(map(str,gaps)),triple_excess=str(gap),common=outcome["common"],
                    physical_stars=targets)
    checked=0
    for vote in samples["votes"]:
        if (vote["label"],vote["law"],vote["age"])!=("tree","nae",0):continue
        stars=samples["cases"][vote["case"]]["stars"]
        for item in vote["all_holders"]:
            h=item["holder"]
            if len(stars[h])!=3:continue
            arities=[next((len(s) for j,s in enumerate(stars) if j!=h and b in s),None) for b in item["marks"]]
            predicted=independent_branches(arities)
            actual=samples["tables"][item["table"]]
            g=actual["gram"]
            assert all(F(g[8*a+b],g[9])==predicted[a][b] for a in range(8) for b in range(8))
            local=None not in arities and sorted(arities) in ([3,3,3],[3,3,4])
            assert actual["common"]["local"]==local
            checked+=1
    return dict(thresholds=signatures,all_drawn_tree_source_ternaries=checked)


def reached_controls():
    source=[[0,1,3],[0,2,4],[1,2,5]];result={}
    for law,added in (("nae",[3,4,5,6]),("parity",[3,4,5])):
        outcome,stars=next_stage(source,law)
        assert outcome["status"] in ("grown","closed") and stars==source+[added]
        assert all(certify(source,law)) and all(certify(stars,law))
        following=next_stage(stars,law)[0]
        if law=="nae":assert following["status"]=="grown"
        result[law]=dict(source=source,grown=stars,first_status=outcome["status"],second_status=following["status"])
    return result


def run():
    samples=json.loads((OUT/"samples.json").read_text())
    comp=Counter()
    for key,e in samples["tables"].items():
        verify_one(e["rows"],e["common"])
        if e["method"]=="minority assignment transport":
            full=full_certificate(e["rows"],SIZES)
            assert full["local"]==e["common"]["local"]
            verify_one(e["rows"],full)
            comp["transport_vs_independent_full_list"]+=1
        comp["every_cell_rational"]+=1
    count=0;done=set()
    for r in samples["votes"]:
        if r["mode"]!="draw":continue
        case=samples["cases"][r["case"]];law=r["law"];age=r["age"]
        stages=case["stars"] if not age else case["laws"][law]["next_stars"]
        if max(map(max,stages))>=12:continue
        for h in r["all_holders"]:
            rid=h["table"]
            if rid in done:continue
            f=literal(stages,h["marks"],law);g=f.T @ f
            expected=samples["tables"][rid]["gram"]
            assert [h["common_completion_unit"]*x for x in expected]==list(map(int,g.flat))
            count+=1;done.add(rid)
    lead=json.loads((OUT/"lead.json").read_text())
    for law,r in lead.items():
        for v in r["attachments"].values():verify_one(v["rows"],v["common"])
        for tag,sizes in (("single_per_reader",((2,)*4,(2,)*2)),("joint_at_two_place_reader",((4,)*4,(2,)*2)),("incoherent_diagonal",SIZES)):
            verify_one(r[tag]["rows"],r[tag]["common"],sizes)
    wide=json.loads((OUT/"widths.json").read_text())
    for n in (3,4,5):
        for law,rec in wide[str(n)].items():
            v=rec["all_marks"];verify_one(v["rows"],v["common"],((2,2),)*n)
            for v in rec["subsets"]:verify_one(v["rows"],v["common"])
    save("validation.json",dict(sample_comparisons=comp,literal_sample_matrices=count,
         tree_arity_checks=tree_controls(samples),reached_witness_program_engine=reached_controls(),
         lead_laws=2,all_attachment_contexts=64,all_attachment_probability_entries=512,
         wide_full_settings=[8,16,32],wide_strategy_counts=[64,256,1024]))
