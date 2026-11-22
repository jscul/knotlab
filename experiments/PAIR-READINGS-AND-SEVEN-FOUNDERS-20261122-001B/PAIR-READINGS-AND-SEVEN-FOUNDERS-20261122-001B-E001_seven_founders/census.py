"""Exact four-cut ledger, with direct labelled-population and tree-edit checks."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from itertools import combinations, permutations, product
import json
from math import comb, factorial
from pathlib import Path
import sys

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
END_TICKET = "ORDINARY-DYNAMICS-20261120-001A"
sys.path.insert(0, str(ROOT / "experiments" / END_TICKET / (END_TICKET+"-E001_ordinary")))
from end_operator import from_stars, neighbors, proposals, step

LAWS = ("parity", "nae")
N = 7
HOLDERS = tuple(range(N))
PAIRS = tuple(combinations(HOLDERS, 2))
BUS = {pair: 1 << i for i,pair in enumerate(PAIRS)}
PERMS = tuple(permutations(HOLDERS))
FATE = ("status","paid_cuts","last_components","terminal_arity")


def save(name, value):
    raw = (json.dumps(value,sort_keys=True,separators=(",",":"))+"\n").encode()
    if name.endswith(".gz"):
        raw = gzip.compress(raw,compresslevel=6,mtime=0)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/name).write_bytes(raw)


def load(name):
    raw=(OUT/name).read_bytes()
    return json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)


def connected(edges):
    parts=[1<<i for i in HOLDERS]
    for a,b in edges:
        joined=parts[a]|parts[b]
        bits=joined
        while bits:
            low=bits & -bits
            parts[low.bit_length()-1]=joined
            bits-=low
    return parts[0]==127


def rearrange(edges,p):
    return tuple(sorted((min(p[a],p[b]),max(p[a],p[b])) for a,b in edges))


def flagged(flags,p):
    changed=[0]*N
    for i,b in enumerate(flags):
        changed[p[i]]=b
    return tuple(changed)


def det(matrix):
    """Small exact determinant via fraction-free elimination."""
    a=[x[:] for x in matrix]
    sign=1
    previous=1
    for i in range(len(a)-1):
        if not a[i][i]:
            pivot=next((j for j in range(i+1,len(a)) if a[j][i]),None)
            if pivot is None:return 0
            a[i],a[pivot]=a[pivot],a[i]
            sign=-sign
        for j in range(i+1,len(a)):
            for k in range(i+1,len(a)):
                val=a[j][k]*a[i][i]-a[j][i]*a[i][k]
                assert val%previous==0
                a[j][k]=val//previous
        previous=a[i][i]
    return sign*a[-1][-1]


def source_rows(edges,flags):
    rows=[[] for _ in flags]
    for d,(a,b) in enumerate(edges):
        rows[a].append(d); rows[b].append(d)
    next_id=len(edges)
    for i,row in enumerate(rows):
        q=max(0,3-len(row))+flags[i]
        row.extend(range(next_id,next_id+q))
        next_id+=q
    return tuple(tuple(row) for row in rows)


def catalog():
    # Build orbits from the seven-holder atlas; independently check that their
    # complete explicit label images cover exactly the connected eight-subsets.
    uncoloured=[]
    for g in nx.graph_atlas_g():
        if len(g)==N and g.number_of_edges()==8 and nx.is_connected(g):
            uncoloured.append(min(rearrange(g.edges(),p) for p in PERMS))
    assert len(uncoloured)==len(set(uncoloured))
    orbits={}
    all_labelled=set()
    counts=Counter(); by_k=Counter(); tree_by_k=Counter(); shape_rows=[]
    for edges in sorted(uncoloured):
        label_images=set(); aut=[]
        for p in PERMS:
            image=rearrange(edges,p)
            if image==edges:aut.append(p)
            label_images.add(sum(BUS[e] for e in image))
        assert len(label_images)*len(aut)==factorial(N)
        assert not all_labelled.intersection(label_images)
        all_labelled.update(label_images)
        g=nx.Graph();g.add_nodes_from(HOLDERS);g.add_edges_from(edges)
        tau=sum(connected(t) for t in combinations(edges,N-1))
        lap=[[g.degree(i) if i==j else -int(g.has_edge(i,j)) for j in HOLDERS[:-1]] for i in HOLDERS[:-1]]
        assert tau==det(lap)
        pivots={}
        for h in HOLDERS:
            components=nx.connected_components(g.subgraph(set(HOLDERS)-{h}))
            pivots[h]=[[sorted(c),min(v for v in c if g.degree(v)<3)] for c in components]
        occupied=set()
        for flags in product((0,1),repeat=N):
            if flags in occupied:continue
            images={flagged(flags,p) for p in aut}
            assert min(images)==flags and not occupied.intersection(images)
            occupied.update(images)
            mult=len(images)*len(label_images)
            stabilizer=sum(flagged(flags,p)==flags for p in aut)
            assert mult*stabilizer==factorial(N)
            k=sum(flags)
            uid="-".join(f"{a}{b}" for a,b in edges)+"_"+"".join(map(str,flags))
            mass=mult*3**(N-k)
            orbits[uid]={"id":uid,"edges":edges,"flags":flags,"labelled":mult,"tau":tau,
                         "aut":stabilizer,"distinct_mass":mass,"tree_edit_mass":mass*tau}
            by_k[k]+=mult; tree_by_k[k]+=mult*tau
        assert len(occupied)==2**N
        counts["labelled"]+=len(label_images);counts["origin"]+=tau*len(label_images)
        shape_rows.append({"edges":edges,"tau":tau,"labelled":len(label_images),
                           "uncoloured_aut":len(aut),"deletion_pivots":pivots})
    direct={sum(BUS[e] for e in v) for v in combinations(PAIRS,8) if connected(v)}
    assert direct==all_labelled and len(direct)==counts["labelled"]
    assert counts["origin"]==N**(N-2)*comb(len(PAIRS)-N+1,2)
    assert all(by_k[i]==comb(N,i)*len(direct) and tree_by_k[i]==comb(N,i)*counts["origin"] for i in range(N+1))
    cases=list(orbits.values())
    save("population.json.gz",cases)
    save("catalogue_checks.json",{"shapes":shape_rows,"decorated_types":len(cases),"uncoloured_shapes":len(shape_rows),
                                  "direct_subsets_considered":comb(len(PAIRS),8),"all_connected_labelled":len(direct),
                                  "all_tree_edit_origins":counts["origin"],"labelled_by_flags":by_k,
                                  "tree_edits_by_flags":tree_by_k,"full_denominators":{
                                      "orbit":len(cases),"labelled_decorated":len(direct)*2**N,
                                      "distinct_mass":len(direct)*4**N,"tree_edit_mass":counts["origin"]*4**N}})
    return cases


def components(end):
    adj=neighbors(end)
    rest=set(adj); parts=[]
    while rest:
        todo=[min(rest)]
        rest.remove(todo[0])
        for h in todo:
            new=sorted(adj[h]&rest)
            todo.extend(new);rest.difference_update(new)
        parts.append(sorted(todo))
    return parts


def end_data(end):
    return {"h":[[i,q] for i,q in end.opens.items()],"blocks":end.blocks,"components":components(end)}


def cut_census(source,law):
    having=from_stars(source)
    assert having.opens
    state=end_data(having)
    info={"initial":state,"cuts":[],"paid_cuts":0,"last_components":len(state["components"]),
          "first_separation":0 if len(state["components"])>1 else None,"initial_live":len(having.opens),
          "terminal_arity":None,"status":"open","stall":None}
    for age in range(1,5):
        old_components=components(having)
        groups=proposals(having)
        turn=step(having,law)
        if turn.status=="stall":
            bill=Counter(i for b in groups for i in b)
            needed=[[h,having.opens[h],bill[h]] for h,excess in turn.shortages]
            assert all(b>a for _,a,b in needed)
            info.update(status="stall",stall={"attempted_cut":age,"groups":groups,"shortages":needed})
            break
        assert turn.status=="extend"
        assert Counter(h for p in turn.parents for h in p)==Counter(having.opens)
        if len(old_components)>1:
            assert len(turn.parents)>=len(old_components) and min(turn.fresh)>=1
        following=end_data(turn.end)
        ncomp=len(following["components"])
        old_cmap={h:i for i,c in enumerate(old_components) for h in c}
        child_cmap=[]
        for p in turn.parents:
            identities={old_cmap[h] for h in p}
            assert len(identities)==1
            child_cmap.append(next(iter(identities)))
        assert all(len({child_cmap[i] for i in row})==1 for row in following["components"])
        assert ncomp>=len(old_components) or not ncomp
        info["cuts"].append({"age":age,"parents":turn.parents,"lookahead":turn.demand,"grants":turn.fresh,
                             "next":following})
        info["paid_cuts"]=age
        info["last_components"]=ncomp
        if ncomp>1 and info["first_separation"] is None:info["first_separation"]=age
        if not ncomp:
            assert law=="parity" and len(turn.parents)==1 and turn.fresh==(0,)
            assert tuple(sorted(turn.parents[0]))==tuple(having.opens) and all(v==1 for v in having.opens.values())
            info.update(status="closed",terminal_arity=len(turn.parents[0]))
            break
        assert min(turn.fresh)>=1
        having=turn.end
    info["total_holders"]=len(source)+sum(len(c["parents"]) for c in info["cuts"])
    info["total_names"]=len({n for r in source for n in r})+sum(sum(c["grants"]) for c in info["cuts"])
    return info


def census(cases):
    summaries={law:defaultdict(Counter) for law in LAWS}; raw=[]
    for c in cases:
        source=source_rows(c["edges"],c["flags"])
        laws={law:cut_census(source,law) for law in LAWS}
        p,n=laws.values()
        assert n["status"]!="closed"
        assert p["initial"]==n["initial"]
        for pc,nc in zip(p["cuts"],n["cuts"]):
            assert pc["parents"]==nc["parents"] and pc["lookahead"]==nc["lookahead"]
            if pc["grants"]!=(0,):
                assert pc==nc
        for law,s in laws.items():
            key=tuple(s[k] for k in FATE)
            a=summaries[law][key]
            a["orbit"]+=1
            for k in ("labelled","distinct_mass","tree_edit_mass"):a[k]+=c[k]
        raw.append({"id":c["id"],**laws})
    save("census.json.gz",raw)
    labels=load("catalogue_checks.json")["full_denominators"]
    norm={"orbit":"orbit","labelled":"labelled_decorated","distinct_mass":"distinct_mass","tree_edit_mass":"tree_edit_mass"}
    totals={}
    for law,rows in summaries.items():
        totals[law]=[]
        for key,a in sorted(rows.items(),key=lambda kv:str(kv[0])):
            totals[law].append(dict(zip(FATE,key))|dict(a)|{"fractions":{
                k:str(Fraction(a[k],labels[v])) for k,v in norm.items()}})
        assert all(sum(v[k] for v in rows.values())==labels[f] for k,f in norm.items())
    save("census_totals.json",{"denominators":labels,"outcomes":totals,"law_order":LAWS})
    return raw


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase",choices=("catalog","growth","all"),default="all")
    args=parser.parse_args()
    cases=catalog() if args.phase!="growth" else load("population.json.gz")
    if args.phase!="catalog":census(cases)
    print(f"{args.phase} completed for {len(cases)} decorated types.",flush=True)
