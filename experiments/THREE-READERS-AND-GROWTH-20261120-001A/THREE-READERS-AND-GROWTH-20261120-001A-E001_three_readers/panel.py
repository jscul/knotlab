"""Fresh placements weighted by source, by named holder and by fixed explosive host."""
from collections import Counter,defaultdict
from fractions import Fraction as F
from itertools import combinations
from math import gcd
from random import Random
import hashlib
import json
import numpy as np
import networkx as nx
from scipy.stats import beta
from completions import gram
from three import rows_for,margins,mermin,singleton,save,full_certificate,specs
from certificates import hall,parity_model
from holdings import J,certify,hosted,next_stage


def seeded(label,n,i,purpose):
    return Random(int.from_bytes(hashlib.sha256(f"202611205189|{label}|{n}|{i}|{purpose}".encode()).digest(),"big"))


def fresh(label,n,i):
    r=seeded(label,n,i,"source");word=[r.randrange(n) for _ in range(n-2)]
    graph=nx.from_prufer_sequence(word)
    added=None
    if label=="extra":
        added=r.choice([p for p in combinations(range(n),2) if not graph.has_edge(*p)])
        graph.add_edge(*added)
    meet=sorted(tuple(sorted(p)) for p in graph.edges)
    holds=J.stars_from([max(3,graph.degree(k)) for k in range(n)],meet)
    return holds,dict(prufer=word,extra=added)


def interval(k,n):
    return ([0. if k==0 else float(beta.ppf(.025,k,n-k+1)),
             1. if k==n else float(beta.ppf(.975,k+1,n-k))] if n else None)


def run():
    cases={};registry={};spectra={};votes=[]; qs=singleton(3)
    def assess(stars,marks,law):
        key=(tuple(map(tuple,stars)),tuple(marks),law)
        if key not in spectra:
            g=gram(stars,marks,law)
            numbers=[int(v) for v in g.flat];scale=gcd(*numbers)
            norm=tuple(v//scale for v in numbers)
            rid=law+"-"+hashlib.sha256(str(norm).encode()).hexdigest()[:20]
            if rid not in registry:
                rows=rows_for(g,qs)
                if law=="parity":
                    cert=parity_model(rows);method="independent parity instructions"
                elif norm[0]==norm[-1]==0:
                    cert=hall(rows);method="minority assignment transport"
                else:
                    cert=full_certificate(rows,specs(qs));method="rational 64-list membership"
                registry[rid]=dict(gram=norm,rows=rows,common=cert,method=method,
                                   m=str(mermin(rows,3)),margins=margins(rows,3))
            else:assert registry[rid]["gram"]==norm
            spectra[key]=(rid,scale)
        return spectra[key]

    def attach(label,n,i,key,law,age,stars,mode):
        wider={}
        for h,s in enumerate(stars):
            if len(s)<3:continue
            if len(s)==3:wider[h]=tuple(sorted(s))
            else:wider[h]=seeded(label,n,i,f"wide:{age}:{h}").choice(list(combinations(sorted(s),3)))
        exact=[h for h,s in enumerate(stars) if len(s)==3]
        wider_keys=sorted(wider)
        choose=lambda eligible,tag:seeded(label,n,i,f"{tag}:{age}").choice(eligible) if eligible else None
        sup=choose(wider_keys,"uniform");tri=choose(exact,"ternary")
        def item(h):
            rid,scale=assess(stars,wider[h],law)
            return dict(holder=h,marks=wider[h],table=rid,common_completion_unit=scale)
        census={h:item(h) for h in wider_keys} if mode!="fixed_vote" else {}
        vote=dict(label=label,n=n,index=i,case=key,law=law,age=age,mode=mode,
                  holder_count=len(stars),eligible_ternary=len(exact),eligible_wide=len(wider_keys))
        if census:vote["all_holders"]=[census[h] for h in wider_keys]
        if mode!="fixed_roster":
            vote["uniform"]=None if sup is None else (census[sup] if census else item(sup))
            vote["ternary"]=None if tri is None else (census[tri] if census else item(tri))
        votes.append(vote)

    def host(label,n,i,stars,origin,fixed=False):
        key=label if fixed else f"{label}/{n}/{i}"
        cases[key]=dict(stars=stars,origin=origin,laws={})
        for law in ("nae","parity"):
            valid=certify(stars,law);rec=dict(source_projection=valid);cases[key]["laws"][law]=rec
            if not all(valid):continue
            outcome,stage=next_stage(stars,law);rec["step"]=outcome
            if stage is not None:
                rec["next_stars"]=stage
                rec["grown_projections"]=certify(stage,law)
                rec["next_funding"]=next_stage(stage,law)[0]["status"]
            for age,frame in enumerate((stars,stage)):
                if frame is None:continue
                if fixed:
                    attach(label,n,32,key,law,age,frame,"fixed_roster")
                    for j in range(32):attach(label,n,j,key,law,age,frame,"fixed_vote")
                else:attach(label,n,i,key,law,age,frame,"draw")
    for label in ("tree","extra"):
        for n in range(4,9):
            for i in range(12):
                stars,origin=fresh(label,n,i);host(label,n,i,stars,origin)
    for label,stars in hosted().items():host(label,len(stars),0,stars,dict(fixed=True),True)
    results=[]
    for label in ("tree","extra","archive03","partnered"):
        ns=list(range(4,9)) if label in ("tree","extra") else [6 if label=="archive03" else 30]
        for size in ns+([0] if len(ns)>1 else []):
            for law in ("nae","parity"):
                for age in (0,1):
                    selected=[r for r in votes if (size==0 or r["n"]==size) and (r["label"],r["law"],r["age"])==(label,law,age)]
                    for tag in ("all_holders","all_ternaries","uniform","ternary"):
                        cells=[]
                        for r in selected:
                            if tag.startswith("all"):
                                if r["mode"]=="fixed_vote":continue
                                stage=cases[r["case"]]["stars"] if age==0 else cases[r["case"]]["laws"][law]["next_stars"]
                                cells.extend(t for t in r["all_holders"] if tag=="all_holders" or len(stage[t["holder"]])==3)
                            elif r["mode"]!="fixed_roster" and r.get(tag):cells.append(r[tag])
                        rs=[registry[t["table"]] for t in cells]; scores=[F(q["m"]) for q in rs]
                        nonlocal_count=sum(not q["common"]["local"] for q in rs)
                        results.append(dict(label=label,size=size,law=law,age=age,weighting=tag,n=len(rs),nonlocal_count=nonlocal_count,
                                            above_two=sum(s>2 for s in scores),maximum=str(max(scores)) if rs else None,
                                            exact95=(interval(nonlocal_count,len(rs)) if tag in ("uniform","ternary") and size else None)))
    save("samples.json",dict(seed=202611205189,cases=cases,tables=registry,votes=votes,rates=results))
