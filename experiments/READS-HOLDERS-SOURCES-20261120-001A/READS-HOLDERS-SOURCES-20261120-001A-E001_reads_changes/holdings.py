"""Physical holdings, binary pairings, and prospective first-step placements."""
from collections import Counter,defaultdict
from itertools import combinations
from random import Random
import hashlib
import json
import sys

from operations import ROOT, LAW, mask, parity, save
import networkx as nx
from scipy.stats import beta
from pysat.solvers import Minisat22

OLD = ROOT / "experiments/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules"
sys.path.append(str(OLD))
from growth import J, ARCHIVE, certify, observe, rule_for

PARTNER = ROOT / "proofs/WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered/job.py"


def echelon(rows):
    basis={}
    for row in rows:
        while row:
            i=row.bit_length()-1
            if i not in basis:
                basis[i]=row
                break
            row^=basis[i]
    return basis


def kernel(rows,n):
    piv=echelon(rows)
    out=[]
    for free in sorted(set(range(n))-set(piv)):
        word=1<<free
        for other,row in sorted(piv.items()):
            if parity(row & word):
                word|=1<<other
        out.append(word)
    return out


def combinations_supported(words,forbid):
    equations=[sum(((w>>b)&1)<<i for i,w in enumerate(words)) for b in forbid]
    selectors=kernel(equations,len(words))
    from functools import reduce
    from operator import xor
    return [reduce(xor,(w for i,w in enumerate(words) if s>>i&1),0) for s in selectors]


def parity_ties(stars,A,B):
    n=max(map(max,stars))+1
    rows=list(map(mask,stars))
    hidden=sorted(set(range(n))-set(A)-set(B))
    reads=combinations_supported(list(echelon(rows).values()),hidden)
    changes=kernel([*rows,*(1<<h for h in hidden)],n)
    am,bm=mask(A),mask(B)
    pairing=[sum(parity(r & t & am)<<i for i,t in enumerate(changes)) for r in reads]
    assert pairing==[sum(parity(r & t & bm)<<i for i,t in enumerate(changes)) for r in reads]
    return dict(ties=len(echelon(pairing)),joint_reads=reads,joint_changes=changes,pairing=pairing)


def next_stage(stars,law):
    stage=J.S.from_junctions(stars)
    step=observe(stage,law,rule_for(law))
    stages=None if step["status"] not in ("grown","closed") else [list(s) for s in stage.bits_of]
    return step,stages


def random_for(label,n,index,purpose):
    tag=f"202611204183|{label}|{n}|{index}|{purpose}"
    return Random(int.from_bytes(hashlib.sha256(tag.encode()).digest(),"big"))


def placement(label,n,i,age,width):
    v=list(range(width));random_for(label,n,i,f"marks:{age}").shuffle(v)
    u=max(1,width//5); a=(width-u)//2
    return sorted(v[u:u+a]), sorted(v[u+a:]), sorted(v[:u])


def fresh_source(label,n,i):
    rng=random_for(label,n,i,"tree")
    word=[rng.randrange(n) for _ in range(n-2)]
    g=nx.from_prufer_sequence(word)
    extra=None
    if label=="extra":
        extra=rng.choice([p for p in combinations(range(n),2) if not g.has_edge(*p)])
        g.add_edge(*extra)
    pairs=sorted(tuple(sorted(x)) for x in g.edges)
    return J.stars_from([max(3,g.degree(v)) for v in range(n)],pairs),dict(prufer=word,extra=extra)


def hosted():
    import importlib.util
    spec=importlib.util.spec_from_file_location("reads_partner_job",PARTNER)
    wall=importlib.util.module_from_spec(spec)
    sys.path.insert(0,str(PARTNER.parent))
    spec.loader.exec_module(wall)
    opens,blocks=wall.partnered(3)
    sizes,meetings=wall.hub_start(opens,blocks)
    archived=json.loads(ARCHIVE.read_text())["named_archive_starts"]["start-03"]
    return {"archive03":archived["gate"]["literal_supports"],"partnered":J.stars_from(sizes,meetings)}


def nae_units(stars):
    """For every physical distinction, find a pair of allowed assignments differing there alone."""
    width=1+max(map(max,stars)); answers=[]
    for witness in range(width):
        with Minisat22() as solver:
            for s in stars:
                residual=[b+1 for b in s if b!=witness]
                solver.add_clause(residual);solver.add_clause([-b for b in residual])
            if not solver.solve():
                raise AssertionError(("missing one-change witness",stars,witness))
            assignment=sum(1<<(x-1) for x in solver.get_model() if x>0)
        answers.append(assignment & ~(1<<witness))
    return answers


def analyze(stars):
    res={}
    for law in LAW:
        checks=certify(stars,law)
        entry=dict(age0_full_projections=checks,age0=stars)
        if all(checks):
            step,new=next_stage(stars,law)
            entry.update(step=step,age1=new)
            if new is not None:
                # An ordinary parity closing tie may have fewer than three places.
                entry["age1_full_projections"]=certify(new,law)
        if law=="nae" and all(checks):
            entry["age0_unit_witnesses"]=nae_units(stars)
            if entry.get("age1") is not None:
                entry["age1_unit_witnesses"]=nae_units(entry["age1"])
        res[law]=entry
    return res


def run_samples():
    sources={};draws=[]; groups=defaultdict(list)
    def take(label,n,i,stars,origin,key,frames):
        draws.append(dict(stratum=label,n=n,index=i,source=key,origin=origin,placements={}))
        row=draws[-1]; data=row["placements"]
        for law in LAW:
            src=frames[law]
            data[law]={}
            if not all(src["age0_full_projections"]):
                continue
            for age in (0,1):
                stage=src.get(f"age{age}")
                if stage is None:
                    continue
                width=1+max(map(max,stage))
                a,b,u=placement(label,n,i,age,width)
                placements=[("source" if age==0 else "grown",a,b,u)]
                if age==1:
                    ao,bo,uo=data[law]["source"]["marks"]
                    placements.append(("kept_old",ao,bo,sorted(set(range(width))-set(ao)-set(bo))))
                for tag,x,y,h in placements:
                    report=parity_ties(stage,x,y) if law=="parity" else dict(ties=0,unit_witnesses=f"age{age}_unit_witnesses")
                    data[law][tag]=dict(marks=[x,y,h],**report)
                    groups[label,n,law,tag].append(report["ties"])
    for label in ("tree","extra"):
        for n in range(4,9):
            for i in range(32):
                stars,origin=fresh_source(label,n,i);key=f"{label}/{n}/{i}"
                sources[key]=analyze(stars)
                take(label,n,i,stars,origin,key,sources[key])
    for label,stars in hosted().items():
        n=len(stars);sources[label]=analyze(stars)
        for i in range(32):
            take(label,n,i,stars,dict(fixed_host=True),label,sources[label])
    rate=[]
    for label,ns in (("tree",list(range(4,9))),("extra",list(range(4,9))),("archive03",[6]),("partnered",[30])):
        for n in [*ns]+([0] if len(ns)>1 else []):
            for law in LAW:
                for tag in ("source","grown","kept_old"):
                    values=sum((groups[label,m,law,tag] for m in (ns if n==0 else [n])),[])
                    total=len(values);wins=sum(v>=2 for v in values)
                    ci=([0. if not wins else float(beta.ppf(.025,wins,total-wins+1)),
                         1. if wins==total else float(beta.ppf(.975,wins+1,total-wins))] if total else [])
                    rate.append(dict(stratum=label,n=n,law=law,age=tag,draws=32*(len(ns) if n==0 else 1),observed=total,
                                     histogram=dict(Counter(values)),two_or_more=wins,interval95=ci))
    save("placements.json",dict(seed=202611204183,sources=sources,draws=draws,rates=rate))
