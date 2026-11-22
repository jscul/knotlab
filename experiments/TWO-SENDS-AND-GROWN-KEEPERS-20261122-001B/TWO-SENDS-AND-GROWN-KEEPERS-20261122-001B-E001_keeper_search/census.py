"""Literal growth, complete projections and original-launch pricing for B303."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import gzip
import json
import inspect
import sys

import networkx as nx
import numpy as np
from pysat.solvers import Minisat22

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = "TWO-SENDS-AND-GROWN-KEEPERS-20261122-001B"
OUT = ROOT / "artifacts" / TICKET / HERE.name
RESEARCH = ROOT / "research" / TICKET
def family(name, slug):
    return ROOT / "experiments" / name / (name + "-E001_" + slug)

NAE = family("NAE-GROWTH-20261119-001B", "nae")
ORD = family("ORDINARY-DYNAMICS-20261120-001A", "ordinary")
FUND = family("FORBIDDING-JOIN-20261120-001B", "free_readings")
sys.path[:0] = list(map(str,(NAE,ORD,FUND,ROOT / "tools")))
import end_operator as compact
import naelib as engine
import rival_growth as literal
from knotlab.knots import check_knot
from knotlab.relations import Relation

def sources():
    def named(edges, loose):
        rows = [[] for _ in loose]
        name = 0
        for a,b,count in sorted(edges):
            ns=tuple(range(name,name+count))
            rows[a].extend(ns)
            rows[b].extend(ns)
            name+=count
        for i,count in enumerate(loose):
            rows[i].extend(range(name,name+count))
            name+=count
        return tuple(map(tuple,rows))
    for s,p,k in product(range(1,4),(4,5),range(3)):
        yield f"D-s{s}-p{p}-k{k}",named([(0,1,s)],(p,k)),2,False
    for a,b,p,w in product((1,2),(1,2),(3,4),(0,1)):
        yield f"W-a{a}-b{b}-p{p}-w{w}",named([(0,1,a),(1,2,b)],(p,w,2)),2,False
    for a,p in product((1,2),(3,4)):
        yield f"T-a{a}-p{p}",named([(0,1,a),(1,2,1),(0,2,1)],(p,1,1)),2,False
    yield "control-isolated-four",((0,1,2,3),),3,True
    yield "control-isolated-three",((0,1,2),),3,True
    yield "control-recurring-three",((0,1,3,4),(0,1,2,5),(2,6,7)),3,True


def legal(w,n,law):
    return w.bit_count()%2==0 if law=="parity" else w not in (0,(1<<n)-1)


def incidences(stars):
    owners=defaultdict(list)
    for h,row in enumerate(stars):
        assert len(set(row))==len(row)
        for n in row: owners[n].append(h)
    assert all(1<=len(scope)<=2 for scope in owners.values())
    return {n:tuple(v) for n,v in owners.items()}


@cache
def canonical(width,law):
    if width<3:return False
    assert width<15, ("certify large width symbolically",width)
    places=tuple(map(str,range(width)))
    rows=frozenset(tuple(bool(w & (1<<j)) for j in range(width))
                   for w in range(1<<width) if legal(w,width,law))
    return check_knot(Relation(places,rows),places[:-1],places[-1]).is_knot


class Projector:
    def __init__(self,stars,law):
        self.solver=Minisat22()
        self.stars=stars
        self.law=law
        self.cache={}
        aux=max(n for row in stars for n in row)+1
        for row in stars:
            args=tuple(n+1 for n in row)
            if law=="nae":
                self.solver.add_clause(list(args))
                self.solver.add_clause([-x for x in args])
            else:
                a=args[0]
                for b in args[1:]:
                    aux+=1
                    c=aux
                    for clause in ((-a,-b,-c),(a,b,-c),(a,-b,c),(-a,b,c)):
                        self.solver.add_clause(list(clause))
                    a=c
                self.solver.add_clause([-a])

    def pins(self,pins):
        return self.solver.solve(assumptions=[(n+1) if v else -(n+1) for n,v in pins])

    def projection(self,marks, paid=None, val=None):
        key=tuple(marks),paid,val
        if key not in self.cache:
            assert len(marks)<=15, ("full finite register needs an equivalent projection",key)
            fixed=[] if paid is None else [(paid,val)]
            out=[]
            for w in range(1<<len(marks)):
                pins=fixed+[(n,(w>>j)&1) for j,n in enumerate(marks)]
                if self.pins(pins):out.append(w)
            self.cache[key]=tuple(out)
        return self.cache[key]

    def example(self,pins):
        if not self.pins(pins):
            return None
        assigned={lit-1 for lit in self.solver.get_model() if lit>0}
        actual=incidences(self.stars)
        return sum(1<<n for n in actual if n in assigned)

    def close(self):
        self.solver.delete()


def gf2_rank(rows):
    pivots={}
    for v in rows:
        while v and (p:=v.bit_length()-1) in pivots: v^=pivots[p]
        if v:pivots[v.bit_length()-1]=v
    return len(pivots)


def parity_count(stars,pins):
    n=max(d for row in stars for d in row)+1
    base=[sum(1<<d for d in row) for row in stars]+[1<<d for d,v in pins]
    joined=[x<<1 for x in base]
    for i,(d,v) in enumerate(pins): joined[len(stars)+i]|=v
    rank=gf2_rank(base)
    return 0 if gf2_rank(joined)!=rank else 1<<(n-rank)


class CounterModel:
    """Exact binary contractions with one small auxiliary index per holder.

    A NAE factor is 1 - [all zero] - [all one]. A normalized positive-grant
    multi-input completion adds two terms pinning only its paid inputs.
    The coefficients are scaled to integers, with their denominators retained.
    """
    def __init__(self,stars,law,history):
        self.stars=stars
        self.law=law
        self.history=history
        self.owners=incidences(stars)
        self.factors={}
        self.memo={}
        self.denominators={}
        for chronological in (False,True):
            states=[]
            scale=1
            for h,row in enumerate(stars):
                fixed=frozenset(row)
                b=history.get(h)
                if chronological and b is not None and b["fresh"]:
                    p=frozenset(b["paid"]);g=len(b["fresh"]);u=1<<g
                    if len(p)==1:
                        scale*=u-1
                        opts=[(1,(),0),(-1,fixed,0),(-1,fixed,1)]
                    else:
                        scale*=u*(u-1)
                        opts=[(u-1,(),0),(1,p,0),(1,p,1),(-u,fixed,0),(-u,fixed,1)]
                else:
                    opts=[(1,(),0),(-1,fixed,0),(-1,fixed,1)]
                states.append(opts)
            self.factors[chronological]=states
            self.denominators[chronological]=scale

    def count(self,pins=(),chronological=False):
        pins=tuple(sorted(pins))
        key=pins,chronological
        if key in self.memo:return self.memo[key]
        if len({d for d,v in pins})!=len(pins):
            if any((d,1-v) in pins for d,v in pins):return 0
            return self.count(tuple(set(pins)),chronological)
        if self.law=="parity":
            total=parity_count(self.stars,pins)
            if chronological:
                divisors=1
                for b in self.history.values():
                    if b["fresh"]:divisors*=1<<(len(b["fresh"])-1)
                total=Fraction(total,divisors)
        else:
            states=self.factors[chronological]
            fixed=dict(pins)
            factors=[((h,),np.array([opt[0] for opt in opts],dtype=object)) for h,opts in enumerate(states)]
            scopes=defaultdict(list)
            for d,own in self.owners.items():scopes[own].append(d)
            for own,marks in scopes.items():
                shape=tuple(len(states[h]) for h in own)
                t=np.empty(shape,dtype=object)
                for ix in np.ndindex(shape):
                    options=[states[h][i] for h,i in zip(own,ix)]
                    coeff=1
                    for d in marks:
                        specified={val for k,ss,val in options if d in ss}
                        if d in fixed:specified.add(fixed[d])
                        if len(specified)>1:
                            coeff=0
                            break
                        if not specified:
                            coeff*=2
                    t[ix]=coeff
                factors.append((own,t))
            alive=set(range(len(states)))
            while alive:
                neighborhoods={h:set().union(*(ss for ss,t in factors if h in ss)) for h in alive}
                h=min(alive,key=lambda v:(np.prod([len(states[x]) for x in neighborhoods[v]],dtype=object),v))
                joined=tuple(sorted(neighborhoods[h]))
                used=[(ss,t) for ss,t in factors if h in ss]
                factors=[(ss,t) for ss,t in factors if h not in ss]
                merged=1
                for ss,t in used:
                    dims=[len(states[v]) if v in ss else 1 for v in joined]
                    merged=merged*t.reshape(dims)
                result=np.sum(merged,axis=joined.index(h),dtype=object)
                factors.append((tuple(v for v in joined if v!=h),result))
                alive.remove(h)
            total=1
            for ss,arr in factors:
                assert not ss
                total*=int(arr)
            if chronological: total=Fraction(total,self.denominators[True])
        self.memo[key]=total
        return total


def canonical_rows(stars,law,solver):
    rows=[]
    for h,row in enumerate(stars):
        actual=solver.projection(row)
        full=tuple(w for w in range(1<<len(row)) if legal(w,len(row),law))
        absent=sorted(set(full)-set(actual))
        erased=[len({(w & ~(1<<j)) for w in actual}) for j in range(len(row))]
        rows.append({"holder":h,"width":len(row),"projected_count":len(actual),
                     "expected_count":len(full),"missing_first":absent[0] if absent else None,
                     "K1":len(actual)<(1<<len(row)),"K2":all(q==(1<<(len(row)-1)) for q in erased),
                     "K3":bool(actual),"omission_counts":erased,"canonical_width":canonical(len(row),law),
                     "whole_relation":actual==full})
    return rows


def intersection_receipt(stars,history):
    owners=incidences(stars)
    pairs=defaultdict(list); singles=defaultdict(list)
    for n,hs in owners.items():
        if len(hs)==2:pairs[hs].append(n)
        else:singles[hs[0]].append(n)
    return {"shared":[[a,b,sorted(ns)] for (a,b),ns in sorted(pairs.items())],
            "private":[[h,sorted(singles[h])] for h in range(len(stars))],
            "supported_double":[[a,b,max(history.get(h,{"cut":0})["cut"] for h in (a,b)),
                                 sorted([list(z) for z in combinations(ns,2)])]
                                for (a,b),ns in sorted(pairs.items()) if len(ns)>=2],
            "concerted":[[a,b,d,i,j] for (a,b),ns in sorted(pairs.items()) for d in ns
                         for i in singles[a] for j in singles[b]],
            "private_internal_swaps":[[h,[list(z) for z in combinations(ns,2)]]
                                      for h,ns in sorted(singles.items()) if len(ns)>=2]}


def native_step(stars,law,oldsol):
    turn=compact.step(compact.from_stars(stars),law,max_births=64)
    if turn.status=="cap":
        return None,{"status":"cap","at_least":turn.planned_births_lower}
    end,receipt=literal.grow(stars,law,"ordinary",engine)
    status={"extend":"funded","stall":"stalled","closed":"closed"}[turn.status]
    assert status==receipt["status"]
    owners=incidences(stars)
    loose={n for n,hs in owners.items() if len(hs)==1}
    witnesses={i:{j for n in row for j in owners[n] if j!=i} for i,row in enumerate(stars)}
    if end is None:
        return None,{"status":status,"shortages":sorted(receipt.get("shortages",{}).items()),
                     "all_old_names_unchanged":True,"unspent":sorted(loose),"births":[]}
    births=[]
    paid_all=[]
    new_all=[]
    for i,b in enumerate(receipt["births"]):
        h=b["knot"]
        parents=tuple(b["parents"]);paid=tuple(b["inputs"]);fresh=tuple(b["fresh"])
        assert (parents,len(fresh),b["D"])==(turn.parents[i],turn.fresh[i],turn.demand[i])
        paid_by=[(owners[n][0],n) for n in paid]
        assert sorted(k for k,n in paid_by)==list(parents)
        inputs=oldsol.projection(paid)
        implied=all(legal(w,len(paid),law) for w in inputs)
        assert b["old_inputs_already_imply_law"]==implied
        whole_survives=bool(fresh) or implied
        assert whole_survives
        births.append({"holder":h,"parents":parents,"paid":paid,"paid_by":paid_by,"fresh":fresh,
                       "demand":b["D"],"implied":implied,"old_paid_words":inputs,
                       "actual_common_witnesses":sorted(set.intersection(*(witnesses[p] for p in parents))) if len(parents)>1 else [],
                       "all_old_words_extend":whole_survives})
        paid_all.extend(paid);new_all.extend(fresh)
    assert set(paid_all)==loose and len(paid_all)==len(loose)
    assert len(set(new_all))==len(new_all) and not set(new_all).intersection(owners)
    assert tuple(end[:len(stars)])==stars
    return tuple(end),{"status":"funded","births":births,"all_old_names_unchanged":True,
                       "unspent":[],"old_names":len(owners),"all_old_words_survive":True,
                       "changed_old_addresses":sorted(set(new_all)&set(owners)),
                       "new_meetings_between_old_and_new":[[h,k,n] for b in births for h,n in b["paid_by"]
                                                           for k in [b["holder"]]],
                       "distinct_newborn_intersections":[[a["holder"],b["holder"],sorted(
                           set(a["paid"]+a["fresh"])&set(b["paid"]+b["fresh"]))]
                           for a,b in combinations(births,2) if
                           set(a["paid"]+a["fresh"])&set(b["paid"]+b["fresh"])]}


def offered_support(stars,roles,focal,keeper,cut):
    prohibited=set(focal["fresh"])
    shared={}
    for a,b,ns in roles["shared"]:
        if keeper in (a,b):
            shared[str(b if a==keeper else a)]=[n for n in ns if n not in prohibited]
    outside=[[a,b,p,q] for a,b,origin,pp in roles["supported_double"] if keeper in (a,b)
             for p,q in pp if not {p,q}.intersection(prohibited)]
    concert=[row for row in roles["concerted"] if keeper in row[:2] and not prohibited.intersection(row[2:])]
    u=focal["paid"][0]
    paid_guard=[t for t in outside if u in stars[t[0] if t[1]==keeper else t[1]] and u not in t[2:]]
    return {"actual_sharings":shared,"external_writable_pairs":outside,
            "same_acting_knot_as_paid_guard":paid_guard,"concerted_ways":concert}


def availability(marks,projector,counter,u,stage_mass,launch_mass):
    marks=tuple(marks)
    sets=[set(projector.projection(marks,u,v)) for v in (0,1)]
    overlap=sets[0]&sets[1]
    exclusive=[sorted(s-overlap) for s in sets]
    costs=[]
    for v,words in enumerate(exclusive):
        if not words:
            costs.append({"uniform_count":0,"uniform":"0","chronological":"0"});continue
        # Complement symmetry prices a port containing every input of this orientation exactly.
        if not overlap:
            count=counter.count(((u,v),))
            chronological=Fraction(counter.count(((u,v),),True),launch_mass)
        else:
            count=0;chronological=Fraction(0)
            for w in words:
                pins=tuple((n,(w>>i)&1) for i,n in enumerate(marks))+((u,v),)
                count+=counter.count(pins)
                chronological+=Fraction(counter.count(pins,True),launch_mass)
        costs.append({"uniform_count":int(count),"uniform":str(Fraction(count,stage_mass)),
                      "chronological":str(chronological)})
    return {"marks":marks,"local_words_u0":sorted(sets[0]),"local_words_u1":sorted(sets[1]),
            "exclusive":exclusive,"both":len(overlap),"per_orientation_per_original_launch":costs}


def fresh_information(proj,b,u=None):
    """Price of a change in the actual native fresh register at fixed other payments."""
    p,g=len(b["paid"]),len(b["fresh"])
    allowed=set(b["old_paid_words"])
    def fresh(w):
        return {v for v in range(1<<g) if legal(w | v<<p,p+g,proj.law)}
    rows={w:fresh(w) for w in sorted(allowed)}
    dependencies=[]
    for j in range(p):
        for x in sorted(allowed):
            y=x^(1<<j)
            if x>=y or y not in allowed:continue
            if rows[x]!=rows[y]:
                dependencies.append([j,x,y,sum(1 for bit in range(g) if
                                      {v>>bit&1 for v in rows[x]}!={v>>bit&1 for v in rows[y]}),
                                     not bool(rows[x]&rows[y])])
    return {"actual_paid_bits":b["paid"],"fresh_names":b["fresh"],
            "completions":{str(w):sorted(vs) for w,vs in rows.items()},
            "changed_input_comparisons":[list(z) for z in dependencies]}


def inspect_stage(stars,law,history,cut,source_count,failed=False):
    pr=Projector(stars,law)
    canonical_data=canonical_rows(stars,law,pr)
    valid=all(row["canonical_width"] and row["whole_relation"] and row["K1"] and row["K2"] and row["K3"]
              for row in canonical_data)
    if failed:valid=False
    counter=CounterModel(stars,law,history)
    n=counter.count()
    if not history:source_count=n
    chronological=counter.count((),True)
    # At each funded cut every old word extends, and independent completion has unit total.
    assert chronological==source_count
    own=incidences(stars)
    roles=intersection_receipt(stars,history)
    if cut:
        assert not roles["concerted"]
        assert all(origin==0 for _,_,origin,_ in roles["supported_double"])
    focal_rows=[]
    all_focal=[b for b in history.values() if len(b["paid"])==1 and len(b["fresh"])==3]
    for f in all_focal:
        fid=f["holder"];u=f["paid"][0];xyz=f["fresh"];fage=f["cut"]
        loose=[z for z in xyz if own[z]==(fid,)]
        charges=[[z,own[z]] for z in xyz if z not in loose]
        record={"focal":fid,"birth_cut":fage,"paid":u,"settings":xyz,"still_loose":loose,
                "later_charges":charges,"keepers":[]}
        if len(loose)!=3 or not valid:
            record["refusal"]="focal settings spent" if len(loose)!=3 else "canonical stage unavailable"
            focal_rows.append(record);continue
        payer=f["parents"][0]
        payments=sorted(n for b in history.values() if b["cut"]==fage
                        for owner,n in b["paid_by"] if owner==payer)
        assert len(payments)==4 and u in payments and f["demand"]==3
        siblings=set(payments)-{u}
        separate=[k for k,star in enumerate(stars) if k!=fid and u not in star]
        residual=[len(siblings-set(stars[k])-set(stars[l])) for k,l in combinations(separate,2)]
        assert all(n>=1 for n in residual)
        record["four_loose_at_payer"]={"payer":payer,"names":payments,
            "pre_birth_other_loose_names":sorted(siblings),"actual_lookahead_demand":f["demand"],
            "separate_keeper_pairs":len(residual),"untouched_sibling_payments_per_pair_histogram":dict(Counter(residual))}
        for k,star in enumerate(stars):
            if k==fid:continue
            assert not set(xyz).intersection(star)
            direct=u in star
            marks=tuple(x for x in star if x!=u)
            age=history[k]["cut"] if k in history else 0
            entry={"keeper":k,"age":age,"direct_paid_holder":direct,
                   "timing":"original" if not age else "older-grown" if age<fage else "co-born" if age==fage else "later",
                   "coincident_old_ready_eligible":age<fage and cut==fage,
                   "postbirth_same_stage_register":True,
                   "held":star,"external_supported":offered_support(stars,roles,f,k,cut),
                   "direct_read_u":direct,
                   "local_register":availability(marks,pr,counter,u,n,source_count)}
            compared=entry["local_register"]
            common=sorted(set(compared["local_words_u0"])&set(compared["local_words_u1"]))
            # A fixed physical ready word can be allowed on both inputs even
            # when the native rule never emits a start signal for the device.
            # Record concrete complete word histories. Direct-payer rows omit u
            # only from the proposed *separate* register.
            entry["possible_common_ready_words"]=len(common)
            if common:
                ready=common[0]
                pins=[(d,(ready>>i)&1) for i,d in enumerate(marks)]
                witnesses=[pr.example([*pins,(u,v)]) for v in (0,1)]
                assert all(w is not None for w in witnesses)
                saved=list(marks) if age<fage else []
                local=lambda word,marks:sum(((word>>d)&1)<<i for i,d in enumerate(marks))
                entry["same_ready_concrete_histories"]={
                    "ready_register_word":ready,"complete_reached_words_u0_u1":witnesses,
                    "pre_focal_old_addresses":saved,
                    "before_after_on_these_preexisting_addresses":[
                        [local(w,saved),local(w,saved)] for w in witnesses] if saved else None,
                    "readiness_acquisition":"possible preparation; no separate ordinary ready flag"}
            entry["growth_ready_herald"]=None
            if not direct:
                assert len(siblings.intersection(marks))<=1
                checked=0
                for fixed in common:
                    pinned=[(d,(fixed>>i)&1) for i,d in enumerate(marks)]
                    for v in (0,1):
                        for focal_word in range(8):
                            if legal(v|(focal_word<<1),4,law):
                                trial=[*pinned,(u,v),*((z,(focal_word>>i)&1) for i,z in enumerate(xyz))]
                                assert pr.pins(trial)
                                checked+=1
                entry["all_focal_words_at_every_separate_local_word"]={
                    "checks":checked,"true":not any(compared["exclusive"]),
                    "untouched_other_payer_payments":sorted(siblings-set(marks))}
                assert entry["all_focal_words_at_every_separate_local_word"]["true"]
            if k in history:
                b=history[k]
                entry["fresh_register"]=availability(b["fresh"],pr,counter,u,n,source_count)
                # The complete sibling or older fresh-output conditional factors
                # from the kinetic cut; later correlations are tested on the
                # full CURRENT stage as well, by a joint K-word projection.
                whole=[set(pr.projection(b["paid"]+b["fresh"],u,v)) for v in (0,1)]
                by_paid={}
                p=len(b["paid"])
                for paid in range(1<<p):
                    views=[sorted(w>>p for w in ws if w&((1<<p)-1)==paid) for ws in whole]
                    if any(views):by_paid[str(paid)]=views
                entry["fresh_at_fixed_actual_incoming_paid"]=by_paid
            record["keepers"].append(entry)
        focal_rows.append(record)
    result={"cut":cut,"holdings":stars,"uniform_complete_stage_words":int(n),
            "chronological_unconditional_mass":str(Fraction(chronological,source_count)) if source_count else None,
            "global_nonempty":bool(n),"canonical":valid,"canonical_checks":canonical_data,"physical_incidence":roles,
            "focals":focal_rows}
    return result,pr,source_count


def run_host(code,source,horizon,control,law):
    stages=[];transitions=[];history={};source_count=None
    stage=source
    for cut in range(horizon+1):
        data,pr,source_count=inspect_stage(stage,law,history,cut,source_count)
        stages.append(data)
        if not data["canonical"]:
            pr.close()
            break
        if cut==horizon:
            pr.close()
            break
        nxt,t=native_step(stage,law,pr)
        for b in t.get("births",[]):
            b["available_fresh_by_old_inputs"]=fresh_information(pr,b)
            history[b["holder"]]=dict(b,cut=cut+1)
        transitions.append(t)
        pr.close()
        if nxt is None:break
        stage=nxt
    for state in stages:
        i=state["cut"]
        for f in state["focals"]:
            for k in f["keepers"]:
                comparisons={}
                for name,j in (("coincident_with_focal_birth",i-1),("after_focal_birth",i)):
                    if name.startswith("coincident") and (i!=f["birth_cut"] or k["age"]>=i):
                        continue
                    if j>=len(transitions):
                        comparisons[name]={"status":"beyond enrolled horizon"}
                        continue
                    t=transitions[j]
                    k_names=set(k["local_register"]["marks"])
                    old_changed=set(t.get("changed_old_addresses",()))
                    payments=[b["holder"] for b in t["births"] if k["keeper"] in b["parents"]]
                    comparisons[name]={"status":t["status"],"changed_old_keeper_marks":sorted(k_names&old_changed),
                        "keeper_own_funded_children":payments,"keeper_own_old_payments":[
                            [b["holder"],n] for b in t["births"] for payer,n in b["paid_by"] if payer==k["keeper"]],
                        "number_of_assignments_seen_by_roster":0,
                        "delivered_on_old_register":bool(k_names&old_changed),
                        "loose_focal_names_on_delivery":[x for x in f["settings"] if
                             len(incidences(stages[j+1]["holdings"] if t["status"]=="funded" else
                                            stages[j]["holdings"]).get(x,()))==1]}
                k["ordinary_transition_comparisons"]=comparisons
                k["old_address_changed"]=any(x.get("delivered_on_old_register") for x in comparisons.values())
                k["native_value_invocations"]=0  # Full archived call inventory below.
    raw_width=max(incidences(source))+1
    source_masks=[sum(1<<n for n in row) for row in source]
    old_words=[w for w in range(1<<raw_width) if all(
        ((w&m).bit_count()%2==0 if law=="parity" else (w&m) not in (0,m)) for m in source_masks)]
    assert len(old_words)==stages[0]["uniform_complete_stage_words"]
    first_count=None
    if transitions and transitions[0]["status"]=="funded":
        first_count=0
        for w in old_words:
            ways=1
            for b in transitions[0]["births"]:
                n=len(b["fresh"])
                vals={(w>>d)&1 for d in b["paid"]}
                if law=="parity": ways*=2**(n-1) if n else 1
                elif n: ways*=2**n - int(len(vals)==1)
                else: ways*=int(len(vals)>1)
            first_count+=ways
        assert first_count==stages[1]["uniform_complete_stage_words"]
    return {"source":code,"law":law,"historical_control":control,"attempt_limit":horizon,
            "independent_source_and_first_cut_word_counts":[len(old_words),first_count],
            "stages":stages,"transitions":transitions}


def aggregate(records):
    results={}
    for historical,law in product((False,True),("parity","nae")):
        run=[h for h in records if h["historical_control"]==historical and h["law"]==law]
        counts=Counter()
        timing=Counter()
        passive=Counter()
        examples={}
        for h in run:
            counts["inputs"]+=1
            if not h["stages"][0]["canonical"]:
                counts["rejected_sources"]+=1
                for a in h["stages"][0]["canonical_checks"]:
                    if not a["canonical_width"]:counts["undersized_source_holders"]+=1
                    if not a["whole_relation"]:counts["noncanonical_source_projections"]+=1
                continue
            counts["admitted_sources"]+=1
            for t in h["transitions"]:
                counts[t["status"]+"_attempts"]+=1
                counts["births"]+=len(t.get("births",[]))
                counts["max_births_per_cut"]=max(counts["max_births_per_cut"],len(t.get("births",[])))
                for b in t.get("births",[]):
                    counts["births_with_changed_fresh_support"]+=bool(b["available_fresh_by_old_inputs"]["changed_input_comparisons"])
                    counts["births_with_forced_single_mark_response"]+=any(c[3] for c in b["available_fresh_by_old_inputs"]["changed_input_comparisons"])
                    counts["zero_grants"]+=not b["fresh"]
            for s in h["stages"]:
                counts["reached_stages"]+=1
                counts["noncanonical_reached_stages"]+=not s["canonical"]
                counts["max_width"]=max(counts["max_width"],max(map(len,s["holdings"])))
                for fp in s["focals"]:
                    counts["focal_births"]+=fp["birth_cut"]==s["cut"]
                    if len(fp["still_loose"])!=3:
                        counts["focal_stages_after_settings_spent"]+=1;continue
                    counts["usable_focal_placements"]+=1
                    if "four_loose_at_payer" in fp:
                        counts["two_keeper_placements_with_spare_old_payer_bit"]+=fp["four_loose_at_payer"]["separate_keeper_pairs"]
                    for k in fp["keepers"]:
                        gate="direct" if k["direct_paid_holder"] else "separate"
                        if gate=="separate":
                            counts["pinned_keeper_orientation_focal_words_verified"]+=k["all_focal_words_at_every_separate_local_word"]["checks"]
                        counts[gate+"_keeper_placements"]+=1
                        counts[gate+"_pooled_complete_word_placements"]+=s["uniform_complete_stage_words"]
                        if k["coincident_old_ready_eligible"]:counts[gate+"_older_at_focal_birth"]+=1
                        m=k["external_supported"]
                        counts[gate+"_with_actual_writable_shared_pair"]+=bool(m["external_writable_pairs"])
                        counts[gate+"_with_concerted_offer"]+=bool(m["concerted_ways"])
                        counts[gate+"_with_shared_write_at_actual_paid_holder"]+=bool(m["same_acting_knot_as_paid_guard"])
                        counts[gate+"_with_a_common_ready_register"]+=bool(k["possible_common_ready_words"])
                        counts[gate+"_with_native_two_port_change"]+=bool(k["old_address_changed"]
                                                                        and k["native_value_invocations"])
                        timing[gate+"_"+k["timing"]]+=1
                        for reg in ("local_register","fresh_register"):
                            if reg not in k:continue
                            z=k[reg]["exclusive"]
                            assert bool(z[0])==bool(z[1])
                            lab=gate+"_"+reg
                            passive[lab+"_placements"]+=1
                            if z[0]:
                                passive[lab+"_two_exclusive_ports"]+=1
                                examples.setdefault(lab,[h["source"],s["cut"],fp["focal"],k["keeper"],
                                                        k[reg]["per_orientation_per_original_launch"]])
                        if "fresh_at_fixed_actual_incoming_paid" in k:
                            for views in k["fresh_at_fixed_actual_incoming_paid"].values():
                                if all(views):
                                    counts["fixed_input_pairs_with_both_orientations"]+=1
                                    if views[0]!=views[1]:counts["fixed_input_different_fresh_support"]+=1
        results[("controls" if historical else "alternatives")+"/"+law]={
            "counts":dict(sorted(counts.items())),"by_timing":dict(sorted(timing.items())),
            "passive":dict(sorted(passive.items())),"examples":examples,
            "native_two_port_same_address_writes":counts["separate_with_native_two_port_change"],
            "native_direct_payer_separate_register_writes":counts["direct_with_native_two_port_change"],
            "native_positive_conditional_settings_table":None}
    return results


def focal_readouts():
    """When growth never writes the enrolled keeper, every launch is a decline."""
    records={}
    for law in ("parity","nae"):
        by_port={}
        for tag in ("retained","ordinary_diagonal","copied_first_focal_bit","returned_focal_bit"):
            def entry(i,j):
                if tag=="ordinary_diagonal" and i!=j:
                    return Fraction(0)
                if tag=="copied_first_focal_bit" and (i^j)&1:
                    return Fraction(0)
                allowed=[sum(legal(u|(x<<1),4,law) for x in range(8)) for u in (0,1)]
                return sum((Fraction(1,2*allowed[u])
                        for u in (0,1) if legal(u|(i<<1),4,law) and legal(u|(j<<1),4,law)),Fraction())
            gram=[[entry(i,j) for j in range(8)] for i in range(8)]
            table=[]
            for xs in range(8):
                row=[]
                for out in range(8):
                    compatible=[w for w in range(8) if ((w^out)&(7^xs))==0]
                    weight=sum(gram[i][j]*(-1)**((xs&out&(i^j)).bit_count())
                               for i,j in product(compatible,repeat=2)) / (1<<xs.bit_count())
                    row.append(weight)
                assert sum(row)==1 and min(row)>=0
                table.append([str(x) for x in row])
            by_port[tag]={"Gram":[[str(x) for x in row] for row in gram],"Z_or_X_settings_by_outcomes":table}
        records[law]={"go_mass_per_original_launch":"0","go_conditional":None,
                      "decline_mass_per_original_launch":"1","decline_conditional":by_port}
    return records


def operator_inventory():
    model=engine.J.S.from_junctions(((0,1,2),))
    fs=(("full_preserved_identity_step",type(model).step),("compact_full_funding",compact.step),
        ("ordinary_fresh",engine.J.F.fewest),("parity_implication",engine.parity_rule),
        ("nae_implication",engine.nae_rule),("literal_all_payment_reconstruction",literal.grow))
    records=[]
    for label,fn in fs:
        path=Path(inspect.getsourcefile(fn)).resolve()
        lines,start=inspect.getsourcelines(fn)
        records.append({"operation":label,"file":str(path.relative_to(ROOT)),"first_line":start,
                        "last_line":start+len(lines)-1,"arguments":str(inspect.signature(fn)),
                        "sha256":sha256(path.read_bytes()).hexdigest()})
    return {"source_operations":records,"grant_inputs":"holdings, potential live groups, payable names, lookahead and whole previous relation implication",
            "state_extension":"Retain literal old addresses at their values, adjoin a disjoint allowed fresh tuple per funded child. An internally installed action must be present in this transition or append a genuinely distinguishing port.",
            "value_motion_calls_in_these_operations":[],
            "founder_double_sharing_de_novo_possible":"No. One name per old parent and disjoint newborns exhaust all new meetings."}


def input_hashes():
    paths=[Path(__file__),HERE/"contract.json",HERE/"identity.json",RESEARCH/"preregistration.md",
           RESEARCH/"advisor_receipt.json",NAE/"naelib.py",ORD/"end_operator.py",FUND/"rival_growth.py",
           family("FIRST-KNOT-20261118-001B","two_knots")/"startlib.py",
           family("FRESH-COUNT-20261118-001B","free_count")/"freelib.py",
           ROOT/"research/SIBLING-ANNOUNCEMENTS-AND-RECEIVER-BIRTHS-20261121-001B/native.py",
           ROOT/"research/SIBLING-CHANGE-ANNOUNCEMENTS-20261121-001D/native_checks.md",
           ROOT/"research/ERASURE-AND-CLOSING-SIGNS-20261121-001A/ordinary_routes.py"]
    return {str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths}


def store(record,check):
    data=(json.dumps(record,sort_keys=True,separators=(",",":"))+"\n").encode()
    content=gzip.compress(data,compresslevel=7,mtime=0)
    OUT.mkdir(exist_ok=True,parents=True)
    archive=OUT/"census.json.gz"
    if check:
        if archive.read_bytes()!=content:raise SystemExit("census replay byte disagreement")
    else:archive.write_bytes(content)
    summary=OUT/"census_summary.json"
    summary_bytes=(json.dumps(record["aggregate"],indent=2,sort_keys=True)+"\n").encode()
    if check:
        if summary.read_bytes()!=summary_bytes:raise SystemExit("summary byte disagreement")
    else:summary.write_bytes(summary_bytes)
    print(sha256(content).hexdigest(),archive.name, len(data),"uncompressed bytes")


def main():
    parser=ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write",action="store_true")
    group.add_argument("--check",action="store_true")
    group.add_argument("--one",nargs=2,metavar=("SOURCE","LAW"))
    args=parser.parse_args()
    rows=[]
    for code,src,horizon,control in sources():
        for law in ("parity","nae"):
            if args.one and [code,law]!=args.one:continue
            rows.append(run_host(code,src,horizon,control,law))
    if args.one:
        print(json.dumps(aggregate(rows),indent=2,sort_keys=True))
    else:
        store({"schema":1,"ticket":TICKET,"evidence_stage":"exploratory","inputs_sha256":input_hashes(),
               "word_convention":"Bit j of a projected word belongs to the j-th listed actual name, least significant first.",
               "operator_inventory":operator_inventory(),"native_unconditional_readout":focal_readouts(),"records":rows,"aggregate":aggregate(rows)},args.check)

if __name__=="__main__":
    main()
