"""Bind the finite census to named rows, whole and proper-component tests and end isomorphisms."""
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
import gzip
import json
import sys
import networkx as nx

from census import HERE, ROOT, OUT, LAWS, HOLDERS, PAIRS, components, connected, cut_census, end_data, from_stars, load, save, source_rows, step


def span(rows):
    piv={}
    for x in rows:
        while x:
            h=x.bit_length()-1
            if h not in piv:
                piv[h]=x
                break
            x^=piv[h]
    return piv


def mask(seq):
    return sum(1<<bit for bit in seq)


def named(source,law,limit=4):
    rows=tuple(tuple(x) for x in source)
    history=[]
    for age in range(1,limit+1):
        curr=from_stars(rows)
        t=step(curr,law)
        if t.status!="extend":break
        ownership=Counter(x for row in rows for x in row)
        loose={x for x,n in ownership.items() if n==1}
        available={h:iter(sorted(x for x in row if x in loose)) for h,row in enumerate(rows)}
        nextname=max(ownership)+1
        before=[mask(row) for row in rows]
        oldrank=len(span(before))
        spent=set();new=[];births=[]
        for p,need,grant in zip(t.parents,t.demand,t.fresh,strict=True):
            paid=[next(available[h]) for h in p]; assert not spent.intersection(paid)
            spent.update(paid)
            newids=list(range(nextname,nextname+grant));nextname+=grant
            support=paid+newids
            row=mask(paid); implied=len(span([*before,row]))==oldrank
            assert implied==(set(paid)==loose) and (grant==0)==(implied and law=="parity")
            births.append({"child":len(rows)+len(new),"parents":p,"paid":paid,"next_demand":need,"fresh":newids,
                           "indicator_oldspan_parity":implied,"other_old_loose":sorted(loose-set(paid)),
                           "old_row_rank":oldrank})
            new.append(support)
        assert loose==spent
        after=rows+tuple(new);nextend=from_stars(after)
        closing=not nextend.opens; h={"age":age,"before":rows,"births":births,
                                      "live_before":components(curr),"live_after":components(nextend),
                                      "all_old_loose":sorted(loose),"whole":closing}
        if closing:
            assert len(births)==1 and Counter(x for row in after for x in row)==dict.fromkeys(ownership,2)
            even=[mask(row) for row in after];width=len(ownership)
            odd=[*even[:-1],even[-1]|(1<<(max(ownership)+1))]
            combined=0
            for r in before:combined^=r
            assert combined==even[-1]
            r0,ro=len(span(even)),len(span(odd))
            assert r0==oldrank and ro==r0+1
            h["closure"]={"width":width,"holders":len(after),"even_rank":r0,"old_rank":oldrank,
                          "odd_augmented_rank":ro,"old_words":2**(width-r0),"even_words":2**(width-r0),
                          "odd_words":0,"all_older_rows_xor":sorted(loose),"twice_held":True}
        history.append(h);rows=after
        if closing:break
    return {"source":source,"history":history,"final_rows":rows}


def kernel_control():
    # Archived daughter names were deliberately kept equal across the extra.
    # The first four rows are original, followed by actual ordinary children.
    from closing_projection import literal_stars, projections
    output={}
    for spare in (False,True):
        original,first=literal_stars(spare)
        matched=(*original,*first)
        n=named(original,"parity",1)
        # The archive assigned first private names in a different order.
        a=from_stars(n["final_rows"]); b=from_stars(matched)
        g1,_=end_graph(end_data(a));g2,_=end_graph(end_data(b))
        assert nx.is_isomorphic(g1,g2,node_match=MATCH)
        out={}
        for law in LAWS:
            second=named(matched,law,1)
            target,=[c for c in second["history"][0]["births"] if len(c["parents"])==3]
            assert sorted(target["paid"])==[10,11,12]
            proj=projections(matched,(10,11,12),law)
            out[law]={"matched_paid_input":target,"turn":second["history"][0],"actual_joint_projection":proj}
        a=out["parity"]["matched_paid_input"]
        assert len(a["fresh"])==int(spare) and a["indicator_oldspan_parity"]==(not spare)
        assert a["other_old_loose"]==([13,14] if spare else [])
        assert len(out["nae"]["matched_paid_input"]["fresh"])==1
        output[str(spare)]={"first_cut_source":original,"first_cut_physical_children":first,**out}
    return output


def separate_tree_count():
    bits={p:1<<i for i,p in enumerate(PAIRS)}
    frequencies=Counter()
    tree_count=0
    for tree in combinations(PAIRS,6):
        if not connected(tree):continue
        t=sum(bits[e] for e in tree); tree_count+=1
        missing=[bits[e] for e in PAIRS if t & bits[e]==0]
        for a,b in combinations(missing,2):frequencies[t|a|b]+=1
    catalog=load("catalogue_checks.json")
    assert len(frequencies)==catalog["all_connected_labelled"]
    tau_hist=Counter(frequencies.values()); expected=Counter()
    for s in catalog["shapes"]:
        e=sum(bits[tuple(p)] for p in s["edges"])
        assert frequencies[e]==s["tau"]
        expected[s["tau"]]+=s["labelled"]
    assert tau_hist==expected and sum(frequencies.values())==catalog["all_tree_edit_origins"]
    return {"labelled_trees":tree_count,"ordered_tree_plus_unordered_two_edits":sum(frequencies.values()),
            "distinct_destinations":len(frequencies),"labelled_destinations_by_tree_count":tau_hist}


def end_graph(stage):
    graph=nx.Graph()
    for v,q in stage["h"]:
        graph.add_node(("holder",v),kind=("holder",q))
    for i,b in enumerate(stage["blocks"]):
        n=("witness",i)
        graph.add_node(n,kind=("witness",len(b)))
        graph.add_edges_from((n,("holder",v)) for v in b)
    signature=tuple(sorted((d["kind"],graph.degree(v)) for v,d in graph.nodes(data=True)))
    return graph,signature


MATCH=nx.algorithms.isomorphism.categorical_node_match("kind",None)


def path_certificate(stage):
    if len(stage["h"])<3 or not all(q==2 for _,q in stage["h"]) or not all(len(b)==2 for b in stage["blocks"]):
        return False
    graph=nx.Graph();graph.add_nodes_from(v for v,q in stage["h"]);graph.add_edges_from(stage["blocks"])
    return nx.is_tree(graph) and max(dict(graph.degree()).values())==2


def continuation(census):
    # Use observed cuts only. No forward seven-founder cut is generated here.
    prior="TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A"
    stored=ROOT/"artifacts"/prior/(prior+"-E001_meetings")/"physical_population.json.gz"
    older=json.loads(gzip.decompress(stored.read_bytes()))
    histories={}
    for c in older:
        s=c["laws"]["parity"]
        if len(s["end_by_age"][0]["live_components"])!=1 or not s["cuts"]:continue
        uid="six:"+str(c["edges"])+":"+"".join(map(str,c["extra"]))
        histories[uid]=[{"h":[[h,len(names)] for h,names in v["openings"]],
                        "blocks":v["effective_witness_subsets"]} for v in s["end_by_age"]]
    for row in census:
        s=row['parity']
        if len(s["initial"]["components"])!=1 or not s["cuts"]:continue
        histories[row["id"]]=[s["initial"],*[t["next"] for t in s["cuts"]]]
    representatives=[]; buckets=defaultdict(list); entries={}; transitions={}; paths=set()
    for uid,hist in histories.items():
        previous=None
        for age,stage in enumerate(hist):
            graph,sig=end_graph(stage)
            which=None
            for key in buckets[sig]:
                matcher=nx.algorithms.isomorphism.GraphMatcher(graph,representatives[key][0],node_match=MATCH)
                # Several true isomorphisms can exist. Publish the least
                # holder correspondence so replay does not depend on hash order.
                ids=sorted(n for n in graph if n[0]=="holder")
                mapping=min(matcher.isomorphisms_iter(),default=None,
                            key=lambda image:tuple(image[n][1] for n in ids))
                if mapping is not None:
                    which=key
                    break
            if which is None:
                which=len(representatives);buckets[sig].append(which)
                representatives.append((graph,uid,age,stage))
                mapping={n:n for n in graph}
            mapped=sorted([h[1],v[1]] for h,v in mapping.items() if h[0]=="holder")
            images=dict(mapped)
            target=representatives[which][3]
            assert {images[a]:b for a,b in stage["h"]}==dict(target["h"])
            assert {tuple(sorted(images[a] for a in b)) for b in stage["blocks"]}==set(map(tuple,target["blocks"]))
            entries[uid,age]={"key":which,"holder_map":mapped,"representative":[representatives[which][1],representatives[which][2]]}
            if previous is not None:
                if previous in transitions:assert transitions[previous]["to"]==which
                else:transitions[previous]={"to":which,"witness":[uid,age-1]}
            if path_certificate(stage):paths.add(which)
            previous=which
    out={}
    for row in census:
        uid=row["id"];s=row["parity"]
        if s["status"]!="open" or s["last_components"]!=1:continue
        base=entries[uid,4];current=base["key"];seen={};walk=[]
        while True:
            v=representatives[current]
            if not v[3]["h"]:verdict="forced later closure";break
            if current in paths:verdict="unbounded two-opening path";break
            if current in seen:verdict="repeating end";break
            if current not in transitions:verdict="later fate unresolved";break
            seen[current]=len(walk);d=transitions[current];walk.append(d);current=d["to"]
        certificate=None;consequence_age=4+len(walk)
        if verdict=="later fate unresolved":
            start=s["initial"]
            core=nx.Graph()
            core.add_nodes_from(h for h,_ in start["h"])
            if all(len(block)==2 for block in start["blocks"]):
                core.add_edges_from(start["blocks"])
                q=dict(start["h"])
                if len(core)==4 and nx.is_tree(core) and max(dict(core.degree()).values())==2 and all(
                        q[h]==(3 if deg==1 else 2) for h,deg in core.degree()):
                    # Check the hypotheses of the finite-tree proof only.
                    # Do not generate any new paid cohort or post-cut-four end.
                    extended=core.copy()
                    pendants=[]
                    for h,deg in core.degree():
                        for j in range(q[h]-deg):
                            leaf=f"extra_at_{h}_{j}"
                            extended.add_edge(h,leaf);pendants.append((h,leaf))
                    assert nx.is_tree(extended) and all(extended.degree(h)==q[h] for h in core)
                    assert all(extended.degree(h)-1>=2 for h,_ in pendants)
                    by_holder={h:frozenset((h,)) for h in core}
                    spare={h:iter([leaf for owner,leaf in pendants if owner==h]) for h in core}
                    matched=[]
                    for age,cut in enumerate(s["cuts"],1):
                        after={}
                        for i,(parents,grant) in enumerate(zip(cut["parents"],cut["grants"],strict=True)):
                            cluster=frozenset().union(*(by_holder[h] for h in parents))
                            if len(parents)==1:
                                assert age==1
                                cluster|={next(spare[parents[0]])}
                            assert len(cluster)==age+1 and nx.is_connected(extended.subgraph(cluster))
                            boundary=set().union(*(set(extended[h]) for h in cluster))-cluster
                            assert grant==len(boundary)
                            after[i]=cluster
                        expected={frozenset(c) for c in combinations(extended,age+1)
                                  if nx.is_connected(extended.subgraph(c))}
                        assert len(after)==len(expected) and set(after.values())==expected
                        matched.append({"paid_cut":age,"all_subsets_bijective":len(expected),
                                        "by_born_position":[sorted(map(str,c)) for c in after.values()]})
                        by_holder=after
                    certificate={"matched_original_four_cuts":matched,
                                 "core_holders":sorted(core),"core_pairs":sorted(sorted(p) for p in core.edges),
                                 "initial_openings":start["h"],"pendants":pendants,"tree_vertices":len(extended),
                                 "terminal_arity":sum(deg==1 for _,deg in extended.degree())}
                    consequence_age=len(extended)-1
                    verdict="finite four-role tree, later closure by proof"
        out[uid]={"fourth_end":base,"verdict":verdict,"consequence_age":consequence_age,
                  "period":len(walk)-seen[current] if verdict=="repeating end" else None,"path_to_class":walk,
                  "structural_certificate":certificate}
    return {"seven_survivors":out,"representatives":[{"id":i,"case":u,"cut":a,"stage":s} for i,(_,u,a,s) in enumerate(representatives)],
            "equivalences":[{"case":u,"cut":a,**c} for (u,a),c in entries.items()]}


def case_weights(c):
    return {"orbits":1,"labelled":c["labelled"],"distinct_mass":c["distinct_mass"],"tree_edit_mass":c["tree_edit_mass"]}


def detail(cases,rows):
    funnel={law:defaultdict(Counter) for law in LAWS}; details=[]; chosen={}
    for c,r in zip(cases,rows,strict=True):
        assert c["id"]==r["id"]
        for law in LAWS:
            s=r[law];cur=s["initial"];qual=[];component_soles=0
            for t in s['cuts']:
                partition=cur["components"]
                for part in map(set,partition):
                    p=[(g,f) for g,f in zip(t["parents"],t["grants"]) if part.intersection(g)]
                    if len(p)==1:
                        assert set(p[0][0])==part
                        if len(partition)>1:component_soles+=1
                if len(t["parents"])==1:qual.append(t["age"])
                cur=t["next"]
            for label,present in (("all starts",True),("initially funded",bool(s["paid_cuts"])),
                                  ("funded and one live group initially",s["paid_cuts"] and len(s["initial"]["components"])==1),
                                  ("has sole whole-paying candidate",bool(qual)),
                                  ("has whole zero grant",s["status"]=="closed"),
                                  ("has sole candidate in proper live part",bool(component_soles))):
                counter=funnel[law][label]
                if not counter:counter.update(dict.fromkeys(case_weights(c),0))
                if present:counter.update(case_weights(c))
        if r["parity"]["status"]=='closed':details.append(c)
        elif r["parity"]["status"]=='stall':chosen.setdefault("initial_refusal",c)
        elif len(r["parity"]["initial"]["components"])>1:chosen.setdefault("funded_split",c)
        else:chosen.setdefault("one_component_still_open",c)
    details.sort(key=lambda c:(next(r["parity"]["paid_cuts"] for r in rows if r["id"]==c["id"]),
                               next(r["parity"]["total_holders"] for r in rows if r["id"]==c["id"]),
                               next(r["parity"]["total_names"] for r in rows if r["id"]==c["id"]),
                               len(set(sum((list(r) for r in source_rows(c["edges"],c["flags"])),[]))),
                               c["edges"],c["flags"]))
    to_show={f"closure_{i+1}":c for i,c in enumerate(details)}|chosen
    return funnel,{k:{"case":c,"laws":{law:named(source_rows(c["edges"],c["flags"]),law) for law in LAWS}}
                   for k,c in to_show.items()}


if __name__=="__main__":
    cases=load("population.json.gz"); rows=load("census.json.gz")
    funnel,examples=detail(cases,rows); saved={"funnel":funnel,"seven_examples":examples}
    saved["four_founder_whole_and_split"]=kernel_control()
    saved["six_founder_positive"]={l:named(source_rows([(0,1),(0,2),(0,3),(1,2),(1,4),(3,4),(3,5)],(0,0,0,0,1,1)),l) for l in LAWS}
    assert saved['six_founder_positive']['parity']['history'][-1]['closure']['even_words']==16384
    assert len(saved['six_founder_positive']['nae']['history'][-1]['births'][0]['fresh'])==1
    saved["direct_tree_edit_check"]=separate_tree_count()
    save("physical_controls.json",saved)
    save("surviving_ends.json",continuation(rows))
