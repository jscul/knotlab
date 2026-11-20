"""Literal induced current exterior on the frozen 128-mark path."""

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import json

import networkx as nx

from current import DATA, distances, loads, padded, stages
from current_exterior import View
from front_local import BudgetReached, CAPS, Incidence, LimitedMatcher, digest, refine, sources, validated


HERE = Path(__file__).resolve().parent
OUT = DATA / "exterior_check.json"
THROUGH = 8
SEAM = 64
MARKS = 128


def restricted_component(links, start, allowed):
    found = {start}
    waiting = [start]
    for node in waiting:
        for other in links[node]:
            if other in allowed and other not in found:
                found.add(other)
                waiting.append(other)
    return found


def prepare(stage):
    graph = Incidence.from_stars(stage.stars,stage.occupied)
    literal = distances(graph.neighbors,[SEAM])
    projected = distances(stage.neighbors,[SEAM])
    assert len(literal)==len(graph.neighbors)
    assert all(literal[i]==2*projected[i] for i in range(graph.knot_count))
    assert all(literal[bit]==1+min(literal[knot] for knot in graph.neighbors[bit])
               for bit in graph.distinctions.values())
    return graph,literal,projected


def view(stage, prepared, radius_offset, mark, target):
    physical, hops, knot_steps = prepared
    root = physical.distinctions[mark]
    retained = {node for node,h in hops.items() if h>=2*radius_offset}
    assert root in retained
    near_knots = {v for v,h in knot_steps.items() if h>=radius_offset}
    if target=="root_component":
        retained = restricted_component(physical.neighbors,root,retained)
        near_knots = restricted_component(stage.neighbors,stage.ends[mark][0],near_knots)
    graph = {v:tuple(other for other in physical.neighbors[v] if other in retained) for v in retained}
    colors = {v:(v>=physical.knot_count,v==root) for v in retained}
    shown_knots = {v for v in retained if v<physical.knot_count}
    names = {v:stage.ids[v] for v in shown_knots}
    projected = View(stage,near_knots,{mark},False)
    assert set(projected.graph)==shown_knots
    held = {physical.distinctions[b] for b,knots in stage.ends.items() if all(k in shown_knots for k in knots)}
    assert held==retained-shown_knots
    sizes = {"knots":len(shown_knots),"distinctions":len(retained)-len(shown_knots),
             "incidences":sum(map(len,graph.values()))//2}
    assert projected.size==(sizes["knots"],sizes["distinctions"])
    unvisited = set(retained)
    components = 0
    while unvisited:
        unvisited -= restricted_component(graph,next(iter(unvisited)),unvisited)
        components += 1
    sizes["components"] = components
    return graph,colors,names,sizes


def name_pairing(views):
    (a,ca,na,_),(b,cb,nb,_) = views
    inverse = {code:v for v,code in nb.items()}
    if set(na.values())!=set(inverse):
        return None
    proposed = {v:inverse[code] for v,code in na.items()}
    groups = defaultdict(list)
    for v in b:
        if cb[v][0]:
            groups[tuple(sorted(b[v])),cb[v]].append(v)
    for v in a:
        if ca[v][0]:
            pool = groups[tuple(sorted(proposed[k] for k in a[v])),ca[v]]
            if not pool:
                return None
            proposed[v] = pool.pop()
    return proposed


def compact_mapping(views, mapping, method):
    (a,ca,_,_),(b,cb,_,_) = views
    assert validated(a,b,mapping,ca,cb)
    pairs = sorted(mapping.items())
    encoded = json.dumps(pairs,separators=(",", ":")).encode()
    return {"result":"isomorphic","method":method,"bijection_pairs":len(pairs),
            "verified_incidences":sum(map(len,a.values()))//2,"bijection_sha256":sha256(encoded).hexdigest()}


def compare(views):
    (a,ca,_,size_a),(b,cb,_,size_b) = views
    different = [key for key in size_a if size_a[key]!=size_b[key]]
    if different:
        return {"result":"different","method":"literal_invariant","different_invariants":different}
    proposed = name_pairing(views)
    if proposed is not None and validated(a,b,proposed,ca,cb):
        return compact_mapping(views,proposed,"validated_physical_correspondence")
    refined = refine((a,b),(ca,cb))
    if refined is None:
        return {"result":"different","method":"literal_color_refinement"}
    classes = []
    for labels in refined:
        by_label = defaultdict(list)
        for v,label in labels.items():
            by_label[label].append(v)
        classes.append(by_label)
    candidate = {v:w for color,group in classes[0].items()
                 for v,w in zip(sorted(group),sorted(classes[1][color]),strict=True)}
    if validated(a,b,candidate,ca,cb):
        return compact_mapping(views,candidate,"validated_refinement_correspondence")
    task = []
    for graph,labels in zip((a,b),refined,strict=True):
        actual = nx.Graph(graph)
        nx.set_node_attributes(actual,labels,"color")
        task.append(actual)
    matcher = LimitedMatcher(*task)
    try:
        iso = matcher.is_isomorphic()
    except (BudgetReached,RecursionError):
        return {"result":"unresolved","method":"exact_search_cap","feasibility_trials":matcher.checks}
    if not iso:
        return {"result":"different","method":"exact_search","feasibility_trials":matcher.checks}
    return compact_mapping(views,matcher.mapping,"exact_search_and_literal_validation")


def planned_stop(stage):
    sizes = {"knots":len(stage.stars),"distinctions":len(stage.ends)}
    if stage.age==THROUGH:
        return {"last_layer":stage.age,"status":"age_limit",**sizes}
    plan = sources.growth.plan_round(stage.stars,stage.occupied,("P","V"),caps=CAPS)
    assert plan.status!="extend"
    return {"last_layer":stage.age,"status":plan.status,**sizes,
            **{k:v for k,v in plan.details.items() if k.startswith("planned_")}}


def prediction(age,delta,question,quiet,lit,check):
    if age==0 or delta==3 or (delta==2 and question=="root_component"):
        return check["result"]=="isomorphic"
    if delta==1 and question=="root_component":
        return lit["knots"]-quiet["knots"]==2*age-1
    if delta==2 and question=="union":
        return lit["knots"]>quiet["knots"]
    return None


def main():
    spec = padded("exterior128",MARKS,[SEAM])
    both = loads(spec)
    shared_codes = {}
    arms = [list(stages(spec,both[code],THROUGH,shared_codes)) for code in ("0","1")]
    limits = [planned_stop(arm[-1]) for arm in arms]
    rows = []
    whole = []
    for quiet,lit in zip(*arms):
        age = quiet.age
        assert lit.age==age
        selected_arms = quiet,lit
        physical = [prepare(stage) for stage in selected_arms]
        whole.append({"age":age,"quiet_loaded":[[len(stage.stars),len(stage.ends)] for stage in selected_arms]})
        for delta in (1,2,3):
            d = age+delta
            for side,mark in (("left",SEAM-1-d),("right",SEAM+d)):
                for domain in ("root_component","union"):
                    views = [view(stage,known,d,mark,domain) for stage,known in zip(selected_arms,physical,strict=True)]
                    q,l = (item[3] for item in views)
                    verdict = compare(views)
                    rows.append({"age":age,"offset":d,"offset_minus_age":delta,"side":side,"old_mark":mark,
                                 "domain":domain,"quiet":q,"loaded":l,"loaded_minus_quiet_knots":l["knots"]-q["knots"],
                                 "comparison":verdict,"specified_prediction_held":prediction(age,delta,domain,q,l,verdict)})
        print(age,whole[-1]["quiet_loaded"],Counter(x["comparison"]["method"] for x in rows if x["age"]==age),flush=True)
    receipt = {"source":{"path_marks":MARKS,"attachment":SEAM,"end_spares":[0,1,MARKS-1,MARKS]},
               "comparison":"retained typed induced incidence, threshold 2d hops from old attachment, no external labels",
               "limits":{"caps":CAPS,"requested_through":THROUGH,"arm_status_quiet_loaded":limits},
               "common_whole_stage_sizes":whole,"rows":rows,
               "comparisons":dict(Counter(x["comparison"]["method"] for x in rows)),
               "specified_predictions":dict(Counter(str(x["specified_prediction_held"]).lower() for x in rows)),
               "digests":{p.name:digest(p) for p in (Path(__file__),HERE/"current.py",HERE/"current_exterior.py",HERE/"front_local.py",
                           HERE.parents[2]/"research"/HERE.parent.name/"exterior_validation_design.md")}}
    OUT.write_text(json.dumps(receipt,indent=2)+"\n")
    print(OUT.name,receipt["specified_predictions"],limits,flush=True)


if __name__=="__main__":
    main()
