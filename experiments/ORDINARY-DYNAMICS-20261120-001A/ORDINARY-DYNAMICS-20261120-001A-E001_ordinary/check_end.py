"""Replay ordinary end-only controls against literal stars and the archived engines."""

from collections import Counter, defaultdict
from dataclasses import asdict
from hashlib import file_digest
from itertools import combinations
from pathlib import Path
import json
import sys

import networkx as nx

from end_operator import End, from_stars, local_counts, neighbors, proposals, restricted, step


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "end.json"
ARCHIVE = ROOT / "experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae"
sys.path.insert(0,str(ARCHIVE))
import naelib as archive


def stars_of(n, meetings, opens):
    stars = [[] for _ in range(n)]
    for name,(p,q) in enumerate(meetings):
        stars[p].append(name)
        stars[q].append(name)
    first = len(meetings)
    for p,amount in sorted(opens.items()):
        stars[p].extend(range(first,first+amount))
        first += amount
    return tuple(map(tuple,stars))


def extra_open(stars,parent):
    top = max(bit for row in stars for bit in row)+1
    return tuple((*row,top) if i==parent else row for i,row in enumerate(stars))


def theta(length, all_doubled=False):
    meetings = []
    leaves = []
    for arm in range(3):
        inside = list(range(2+arm*(length-1),2+(arm+1)*(length-1)))
        leaves.append(inside[0])
        line = [0,*inside,1]
        for i,(p,q) in enumerate(zip(line,line[1:])):
            meetings.extend([(p,q)]*(2 if all_doubled or 0<i<length-1 else 1))
    base = stars_of(2+3*(length-1),meetings,dict.fromkeys(leaves,2))
    return base,extra_open(base,1),1


def sharp_variant(active):
    core = [(0,1),(0,2),(1,2)]
    if active:
        core += [(1,3),(2,3)]
    live = 4 if active else 3
    witnesses = list(range(live,live+len(core)))
    meetings = [(p,w) for w,pair in zip(witnesses,core,strict=True) for p in pair]
    meetings += list(zip(witnesses,witnesses[1:]+witnesses[:1]))
    return stars_of(live+len(witnesses),meetings,{0:1,1:2,2:2,**({3:1} if active else {})})


def owner_lists(stars):
    owners = defaultdict(list)
    for i,row in enumerate(stars):
        for bit in row:
            owners[bit].append(i)
    return owners


def graph_of(stars,wired=False):
    graph = {i:set() for i in range(len(stars)+wired)}
    for row in owner_lists(stars).values():
        if len(row)==1 and wired:
            row = [*row,len(stars)]
        if len(row)==2:
            p,q = row
            graph[p].add(q)
            graph[q].add(p)
    return graph


def distances(graph,roots,omit=None):
    levels = dict.fromkeys(roots,0)
    waiting = list(levels)
    for v in waiting:
        for p in graph[v]:
            if p!=omit and p not in levels:
                levels[p] = levels[v]+1
                waiting.append(p)
    return levels


def source_checks(stars):
    wired = graph_of(stars,True)
    full = graph_of(stars)
    end = from_stars(stars)
    gs = proposals(end)
    demand = Counter(v for row in gs for v in row)
    lawful = len(stars)==len(set(stars)) and all(len(s)>=3 for s in stars) and all(
        len(distances(wired,[len(stars)],omit=i))==len(stars) for i in range(len(stars)))
    checks = {"pairs_only":all(len(row)==2 for row in gs),
              "one_or_fewer_witnesses_per_pair":all(len(full[p]&full[q])<=1 for p,q in combinations(end.opens,2)),
              "funded_at_source":all(n>=demand[v] for v,n in end.opens.items()),
              "at_least_two_opens":sum(end.opens.values())>=2}
    return {"knots":len(stars),"distinctions":len(owner_lists(stars)),"parity_stars_pass_bond_gate":lawful,
            "identified_class_clauses":checks,"in_identified_class":all(checks.values())}


def realize(stars,turn):
    owners = owner_lists(stars)
    slots = defaultdict(list)
    for bit, held in sorted(owners.items()):
        if len(held)==1:
            slots[held[0]].append(bit)
    outgoing = {k:iter(row) for k,row in slots.items()}
    fresh_from = max(owners)+1
    births = []
    for group,n in zip(turn.parents,turn.fresh,strict=True):
        spent = tuple(next(outgoing[p]) for p in group)
        births.append((*spent,*range(fresh_from,fresh_from+n)))
        fresh_from += n
    assert all(next(row,None) is None for row in outgoing.values())
    return (*stars,*births)


def verify_distance(old, turn, flags):
    """Check the exact child formula as well as both parent-endpoint extrema."""
    if not turn.end.opens:
        flags["closing_steps_without_next_distance"] += 1
        return
    a,b = neighbors(old),neighbors(turn.end)
    p0 = {v:distances(a,[v]) for v in a}
    p1 = {v:distances(b,[v]) for v in b}
    children = defaultdict(set)
    for y,row in enumerate(turn.parents):
        for x in row:
            children[x].add(y)
    for x,y in combinations(b,2):
        near = [p0[p][q] for p in turn.parents[x] for q in turn.parents[y] if q in p0[p]]
        assert p1[x].get(y)==(min(near)+1 if near else None)
        flags["exact_child_distances"] += 1
    for p,q in combinations(a,2):
        ds = [p1[x].get(y) for x in children[p] for y in children[q]]
        before = p0[p].get(q)
        if before is None:
            assert all(d is None for d in ds)
            flags["disconnected_parent_pairs"] += 1
            continue
        assert all(d is not None and max(0,before-1)<=d<=before+1 for d in ds)
        assert min(ds)==max(0,before-1)
        flags["nearest_contractions"] += 1
        flags["arbitrary_child_upper_attained"] += max(ds)==before+1


def end_graph(end,root,radius):
    clip = restricted(end,distances(neighbors(end),[root]).keys() if radius is None else
                      (p for p,d in distances(neighbors(end),[root]).items() if d<=radius))
    graph = nx.Graph()
    for k,n in clip.opens.items():
        graph.add_node((0,k),color=(0,n,k==root))
    for j,group in enumerate(clip.blocks):
        graph.add_node((1,j),color=(1,))
        graph.add_edges_from(((1,j),(0,k)) for k in group)
    return graph


def end_match(a,p,b,q,radius):
    x,y = end_graph(a,p,radius),end_graph(b,q,radius)
    mapping = nx.vf2pp_isomorphism(x,y,node_label="color")
    if mapping is None:
        return False
    assert all(x.nodes[k]==y.nodes[v] and {mapping[t] for t in x[k]}==set(y[v]) for k,v in mapping.items())
    return True


def read_archived(raw, turn, law, old_count):
    fn = archive.nae_rule(archive.F.fewest) if law=="nae" else archive.parity_rule(archive.F.fewest)
    verdict = raw.step(fn,None)
    state = "stall" if verdict is None else "extend" if verdict["new"] else "closed"
    assert turn.status==state
    if state=="extend":
        rows = []
        for k in range(old_count,len(raw.bits_of)):
            inputs = (next(p for p in raw.owner[x] if p!=k) for x in raw.bits_of[k] if len(raw.owner[x])==2)
            rows.append((tuple(sorted(inputs)),raw.fresh[k],raw.demand_at_birth[k]))
        assert rows==list(zip(turn.parents,turn.fresh,turn.demand,strict=True))


def rooted_labels(turn,names):
    used = Counter()
    result = []
    for parents in turn.parents:
        key = tuple(sorted(names[p] for p in parents))
        rank = used[key]
        used[key] += 1
        result.append(f"({','.join(key)})/{rank}")
    return result


def replay(source, law, through, flags):
    raw = archive.S.from_junctions([list(s) for s in source])
    stars = source
    names = {i:f"o{i:04d}" for i in range(len(stars))}
    ancestry = {i:{i} for i in names}
    first = {i for i in names}
    layers = []
    for age in range(through+1):
        end = from_stars(stars)
        layers.append({"age":age,"stars":stars,"end":end,"names":names.copy(),"ancestry":ancestry.copy(),"born":first})
        turn = step(end,law)
        layers[-1]["plan"] = turn
        read_archived(raw,turn,law,len(stars))
        flags["archived_steps_including_stop"] += 1
        if age==through or turn.status!="extend":
            break
        if not turn.implied:
            for anchor in end.opens:
                truth = tuple((g,d,f) for g,d,f in zip(turn.parents,turn.demand,turn.fresh,strict=True) if anchor in g)
                assert local_counts(end,anchor)==truth
                flags["tested_radius_two_parent_local_counts"] += 1
        verify_distance(end,turn,flags)
        labels = rooted_labels(turn,names)
        n = len(stars)
        next_stars = realize(stars,turn)
        assert tuple(map(tuple,raw.bits_of))==next_stars
        exact_end = from_stars(next_stars)
        assert End({k-n:v for k,v in exact_end.opens.items()},tuple(tuple(i-n for i in row) for row in exact_end.blocks))==turn.end
        if turn.end.opens:
            assert tuple(row for k,row in enumerate(next_stars) if k not in exact_end.opens)==stars
            flags["peeled_live_end_to_predecessor"] += 1
        for idx,g in enumerate(turn.parents,start=n):
            names[idx] = labels[idx-n]
            ancestry[idx] = set.union(*(ancestry[k] for k in g))
        first = set(range(n,len(next_stars)))
        stars = next_stars
    return layers


def mathematical_relabel(end):
    rename = {p:901-7*i for i,p in enumerate(end.opens)}
    return End({rename[p]:n for p,n in end.opens.items()},tuple(tuple(rename[p] for p in row) for row in end.blocks)),rename


def core_result(a,b,law):
    reachable_a, reachable_b = a[1]["end"], b[1]["end"]
    n,m = len(a[0]["stars"]),len(b[0]["stars"])
    core_a,core_b = tuple(sorted(reachable_a.opens)),tuple(sorted(reachable_b.opens))[:3]
    assert core_a==(n,n+1,n+2) and core_b==(m,m+1,m+2)
    assert reachable_a.opens==dict.fromkeys(core_a,1)
    assert [reachable_b.opens[k] for k in core_b]==[1,1,1]
    assert len(reachable_b.opens)==4 and reachable_b.opens[m+3]==2
    assert not neighbors(reachable_b)[m+3]
    for p,q in zip(core_a,core_b,strict=True):
        assert end_match(reachable_a,p,reachable_b,q,None)
    permuted, rename = mathematical_relabel(reachable_a)
    assert all(end_match(reachable_a,v,permuted,rename[v],None) for v in core_a)
    x,y = a[1]["plan"], b[1]["plan"]
    assert x.parents[0]==core_a and y.parents[0]==core_b
    assert (x.fresh[0],y.fresh[0])==((0,1) if law=="parity" else (1,1))
    return {"core_parents": [core_a,core_b],"core_first_opens":[1,1,1],"isolated_first_unary_opens":2,
            "whole_rooted_components_isomorphic_for_all_three_roots":True,
            "permutation_control":True,"core_ternary_fresh_quiet_extra":[x.fresh[0],y.fresh[0]],
            "core_ternary_places_quiet_extra":[len(x.parents[0])+x.fresh[0],len(y.parents[0])+y.fresh[0]],
            "core_demand_quiet_extra":[x.demand[0],y.demand[0]]}


def groups_named(layer,points):
    return {layer["names"][p]:p for p in points}


def share(left,right,changing_source):
    data = []
    for a,b in zip(left,right):
        assert a["age"]==b["age"]
        ea,eb = a["end"],b["end"]
        xa,xb = groups_named(a,ea.opens),groups_named(b,eb.opens)
        born_a,born_b = groups_named(a,a["born"]),groups_named(b,b["born"])
        shared = xa.keys()&xb.keys()
        compared = bool(ea.opens and eb.opens)
        local = {}
        for radius in (0,1,2):
            local[radius] = {"matched_local_types_differ":sum(not end_match(ea,xa[k],eb,xb[k],radius) for k in shared),
                             "paired_live_knots":len(shared)} if compared else None
        def lineages(layer):
            ancestors = [layer["ancestry"][k] for k in layer["end"].opens]
            return {"any":sum(changing_source in part for part in ancestors),
                    "pure":sum(part=={changing_source} for part in ancestors),"live_denominator":len(ancestors)}
        data.append({"layer":a["age"],"live_quiet_extra":[len(xa),len(xb)],
                     "live_only_quiet_extra":[len(xa.keys()-xb.keys()),len(xb.keys()-xa.keys())],
                     "live_share_available_on_both_sides":compared,"shared_live_patterns":local,
                     "births_quiet_extra":[len(born_a),len(born_b)],
                     "births_only_quiet_extra":[len(born_a.keys()-born_b.keys()),len(born_b.keys()-born_a.keys())],
                     "matched_births_with_changed_support_size":sum(len(a["stars"][born_a[k]])!=len(b["stars"][born_b[k]]) for k in born_a.keys()&born_b.keys()),
                     "matched_born_denominator":len(born_a.keys()&born_b.keys()),
                     "any_or_pure_ancestry_quiet_extra":[lineages(a),lineages(b)]})
    return data


def other_ruler(layers,origin):
    result = []
    for stage in layers:
        points = stage["end"].opens
        remote = [p for p in points if stage["ancestry"][p]=={origin}]
        core = [p for p in points if origin not in stage["ancestry"][p]]
        if not (remote and core):
            continue
        assert not any(q in distances(neighbors(stage["end"]),remote) for q in core)
        whole = distances(graph_of(stage["stars"]),remote)
        assert all(p in whole for p in core)
        result.append({"age":stage["age"],"core_live":len(core),"remote_live":len(remote),"end_separation":"disconnected",
                       "nearest_whole_ordinary_knot_steps":min(whole[q] for q in core)})
    return result


def main():
    # Use the original archived subset enumerator, independent of our pivot split.
    archive.J.fastlib.uninstall(archive.F)
    flags = Counter()
    star = stars_of(4,[(0,i) for i in (1,2,3)],{1:2,2:2,3:2})
    main_pair = {"three_leaf_single_hub": (star,extra_open(star,0),0),
                 **{f"theta_{length}":theta(length) for length in (4,5,8,16)},
                 "theta_4_all_meetings_doubled":theta(4,True)}
    scenarios = {}
    for key,(base,extra,origin) in main_pair.items():
        qualified = [source_checks(stars) for stars in (base,extra)]
        assert all(row["parity_stars_pass_bond_gate"] and row["in_identified_class"] for row in qualified)
        record = {"source_checks_quiet_extra":qualified,"source_stars_quiet_extra":[base,extra],"added_port_holder":origin,
                  "laws":{}}
        for law in ("parity","nae"):
            a,b = (replay(stars,law,4,flags) for stars in (base,extra))
            rr = core_result(a,b,law)
            rr["layer_profiles"] = share(a,b,origin)
            rr["whole_ruler_on_extra_arm"] = other_ruler(b,origin)
            rr["cohort_birth_counts_quiet_extra"] = [[len(row["born"]) for row in experiment] for experiment in (a,b)]
            rr["terminal_status_quiet_extra"] = [x[-1]["plan"].status if x[-1]["age"]<4 else "scored_through_4" for x in (a,b)]
            record["laws"][law]=rr
        scenarios[key] = record
        print(key,qualified[0]["knots"],record["laws"]["parity"]["core_ternary_fresh_quiet_extra"],flush=True)

    two_hubs = stars_of(8,[(0,1),*((0,j) for j in (2,3,4)),*((1,j) for j in (5,6,7))],dict.fromkeys(range(2,8),2))
    five_loop = [(i,(i+1)%5) for i in range(5)]
    five_bare = stars_of(5,five_loop,dict.fromkeys(range(5),2))
    path = stars_of(9,[(i,i+1) for i in range(8)],dict.fromkeys(range(9),2))
    deficient = stars_of(5,[(i,i+1) for i in range(4)],{0:2,1:2,2:1,3:2,4:2})
    single = ((0,1,2),)
    controls = {}
    control_cases = {"linked_hub_copies":two_hubs,"bare_five_loop":five_bare,"one_spare_five_loop":extra_open(five_bare,0),
                     "deficient_five_knot_path":deficient,"one_three_place_knot":single,
                     "sharp_radius_base":sharp_variant(False),"sharp_radius_extended":sharp_variant(True)}
    for tag,stars in control_cases.items():
        check = source_checks(stars)
        assert check["parity_stars_pass_bond_gate"]
        row = {"source_checks":check,"source_stars":stars,"laws":{}}
        for law in ("parity","nae"):
            history = replay(stars,law,4,flags)
            row["laws"][law] = [{"age":frame["age"],"plan":asdict(frame["plan"])} for frame in history]
        controls[tag]=row
    assert controls["linked_hub_copies"]["laws"]["parity"][1]["plan"]["fresh"]==(1,1)
    assert controls["deficient_five_knot_path"]["laws"]["parity"][0]["plan"]["shortages"]==((2,1),)
    a,b = (from_stars(control_cases[k]) for k in ("sharp_radius_base","sharp_radius_extended"))
    assert end_match(a,0,b,0,1)
    sharp = [local_counts(e,0) for e in (a,b)]
    assert sharp==[(((0,1,2),2,2),),(((0,1,2),1,1),)]

    extra_path = extra_open(path,4)
    path_series = {}
    for law in ("parity","nae"):
        path_series[law] = share(*(replay(stars,law,5,flags) for stars in (path,extra_path)),changing_source=4)
    receipt = {"scenarios":scenarios,"controls":controls,
               "radius_one_misses_fresh_demand":{"same_exact_root_pattern":True,"fresh_and_demand_by_arm":sharp},
               "nine_knot_path_one_added_open":{"quiet_source":path,"extra_source":extra_path,"added_port_holder":4,"laws":path_series},
               "checked_counts":flags,
               "archive_comparator":"FRESH-COUNT original valid-subset enumeration; GF(2) or archived SAT implication",
               "digests":{}}
    for file in (Path(__file__),HERE/"end_operator.py",Path(archive.__file__),Path(archive.F.__file__)):
        with file.open("rb") as row:
            receipt["digests"][file.name] = file_digest(row,"sha256").hexdigest()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(receipt,indent=2)+"\n")
    print(dict(flags),flush=True)


if __name__=="__main__":
    main()
