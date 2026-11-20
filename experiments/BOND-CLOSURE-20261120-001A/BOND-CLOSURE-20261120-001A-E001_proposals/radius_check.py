"""Compact exact controls for bounded bond-radius locality in parity growth."""

from collections import defaultdict
from hashlib import file_digest
from itertools import combinations
from pathlib import Path
import json
import sys

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = "ORDINARY-DYNAMICS-20261120-001A"
sys.path.insert(0,str(ROOT/"experiments"/BASE/f"{BASE}-E001_ordinary"))
from end_operator import from_stars, neighbors, proposals, step

OUT = ROOT/"artifacts"/HERE.parent.name/HERE.name/"radius_check.json"


def stars_of(edges,n):
    stars = [[] for _ in range(n)]
    for bit,(a,b) in enumerate(edges):
        stars[a].append(bit)
        if b!=n:
            stars[b].append(bit)
    return tuple(map(tuple,stars))


def lawful(edges,n):
    graph = nx.Graph(edges)
    return all(len(row)>=3 for row in stars_of(edges,n)) and all(
        nx.is_connected(graph.subgraph(set(graph)-{v})) for v in range(n))


def all_bonds(edges,n):
    graph = nx.Graph(edges)
    vertices = set(graph)
    results = []
    for code in range(1,1<<n):
        inner = {v for v in range(n) if (1<<v)&code}
        if nx.is_connected(graph.subgraph(inner)) and nx.is_connected(graph.subgraph(vertices-inner)):
            results.append(frozenset(i for i,(a,b) in enumerate(edges) if (a in inner)!=(b in inner)))
    return results


def min_bond(bonds,marks):
    return min((len(b) for b in bonds if set(marks)<=b),default=None)


def core_pair_fresh(edges,n,parents):
    old = from_stars(stars_of(edges,n))
    going = step(old,"parity")
    assert going.status=="extend" and not going.implied
    ordinary = nx.Graph((a,b) for a,b in edges if b!=n)
    assert all(len(group)==2 for group in proposals(old))
    assert all(len(set(ordinary[a])&set(ordinary[b]))<=1 for a,b in combinations(old.opens,2))
    assert sum(old.opens.values())>=2
    components = []
    for end in (old,going.end):
        graph = nx.Graph(neighbors(end))
        components.append(sorted(map(len,nx.connected_components(graph))))
    assert list(map(len,components))==[2,2]
    j = going.parents.index(parents)
    return {"demand":going.demand[j],"fresh":going.fresh[j],"source_birth_count":len(going.parents),
            "input_open_counts":[old.opens[p] for p in parents],"end_component_sizes_before_after":components,
            "identified_source":True}


def seven_knots(r):
    # U,V,S,W,A,B,Z,exterior. Only the two final loose distinctions move.
    u,v,s,w,a,b,z,x = range(8)
    reserve = max(2,r+1)
    total_loose = reserve+6
    weight = total_loose+1
    shared = [(i,j) for i,j in ((u,s),(v,s),(w,s),(s,a),(a,b),(b,w),(a,z)) for _ in range(weight)]
    end = len(shared)
    common = (*shared,(u,x),(u,x),(v,x),(v,x),*[(z,x)]*reserve)
    candidates = [(*common,(carrier,x),(carrier,x)) for carrier in (z,w)]
    all_cut_sets = [all_bonds(arm,x) for arm in candidates]
    assert all(lawful(arm,x) for arm in candidates)
    assert all(len(arm)==len(candidates[0]) for arm in candidates)
    assert all(min(map(len,bonds))==total_loose>r+1 for bonds in all_cut_sets)
    input_stars = [tuple(stars_of(arm,x)[k] for k in (u,v)) for arm in candidates]
    assert input_stars[0]==input_stars[1]
    group_reads = [core_pair_fresh(arm,x,(u,v)) for arm in candidates]
    assert [(arm["demand"],arm["fresh"]) for arm in group_reads]==[(2,2),(1,1)]

    classes = {"bundle_U":0,"bundle_V":weight,"loose_U":end,"loose_V":end+2}
    deck = {}
    for k in range(1,5):
        for select in combinations(classes,k):
            exact = [min_bond(bonds,[classes[f] for f in select]) for bonds in all_cut_sets]
            ordinary = [name for name in select if name.startswith("bundle")]
            loose = {name[-1] for name in select if name.startswith("loose")}
            if not ordinary:
                predicted = total_loose
            elif len(ordinary)==2:
                predicted = None if loose else 2*weight+total_loose-4
            elif len(loose)==2:
                predicted = None
            else:
                predicted = weight+(total_loose-2 if loose and ordinary[0][-1] not in loose else 2)
            assert exact==[predicted,predicted]
            deck["+".join(select)] = predicted
    return {"bond_radius":r,"parallel_bundle_weight":weight,"total_loose":total_loose,"n":x,
            "distinctions":len(candidates[0]),"literal_parity_lawfulness":[True,True],"all_min_bonds_size":total_loose,
            "input_stars_quiet_shifted":input_stars,"group_update_quiet_shifted":group_reads,
            "exact_seed_subset_minima_by_crossing_class":deck}


def owners_from(stars,wired=False):
    holders = defaultdict(list)
    for v,row in enumerate(stars):
        for bit in row:
            holders[bit].append(v)
    if wired:
        for sites in holders.values():
            if len(sites)==1:
                sites.append(len(stars))
    return holders


def grow_literal(stars,turn):
    holders = owners_from(stars)
    fresh = max(holders)+1
    available = defaultdict(list)
    for bit,sites in sorted(holders.items()):
        if len(sites)==1:
            available[sites[0]].append(bit)
    slots = {v:iter(bits) for v,bits in available.items()}
    added = []
    for family,width in zip(turn.parents,turn.fresh,strict=True):
        added.append((*[next(slots[parent]) for parent in family],*range(fresh,fresh+width)))
        fresh += width
    assert all(next(line,None) is None for line in slots.values())
    return (*stars,*added)


def checked_common_bound(edges,n,roots):
    """Unrestricted mincut gives a lower bound; verify both shores of a witness."""
    sink = n
    source = n+1
    graph = nx.DiGraph()
    graph.add_nodes_from(range(n+2))
    for u,v in edges:
        for a,b in ((u,v),(v,u)):
            prev = graph[a][b]["capacity"] if graph.has_edge(a,b) else 0
            graph.add_edge(a,b,capacity=prev+1)
    for u in roots:
        graph.add_edge(source,u,capacity=len(edges)+1)
    lower,_ = nx.minimum_cut(graph,source,sink)
    return lower


def cube(k,extra):
    source_exterior = k+1
    edges = [(0,i) for i in range(1,k+1)] + [(i,source_exterior) for i in range(1,k+1) for _ in range(k-1)]
    edges += [(0,source_exterior)]*extra
    assert lawful(edges,source_exterior)
    stars = stars_of(edges,source_exterior)
    labels = [0,*[1<<j for j in range(k)]]
    for _ in range(k-2):
        turn = step(from_stars(stars))
        assert turn.status=="extend" and not turn.implied
        for group in turn.parents:
            frontier = [labels[knot] for knot in group]
            if any(mask in (0,None) for mask in frontier):
                labels.append(None)
            else:
                label = 0
                for part in frontier:
                    label |= part
                labels.append(label)
        stars = grow_literal(stars,turn)
    full = (1<<k)-1
    assert sorted(mask for mask in labels if mask is not None)==list(range(full))
    old_count = len(stars)
    labels.append(full)
    wired = owners_from(stars,True)
    core = {tuple(sorted((labels[a],labels[b]))) for a,b in wired.values() if labels[a] is not None and labels[b] is not None}
    expected = {(mask,mask|(1<<j)) for mask in range(full) for j in range(k) if not(mask&(1<<j))}
    assert core==expected
    assert len(core)==sum(labels[a] is not None and labels[b] is not None for a,b in wired.values())
    graph = nx.Graph()
    graph.add_weighted_edges_from((a,b,1) for a,b in core)
    assert nx.stoer_wagner(graph)[0]==k
    present = from_stars(stars)
    parent_knots = sorted(p for p in present.opens if labels[p] is not None)
    assert len(parent_knots)==k and all(present.opens[p]==1 for p in parent_knots)
    next_ = step(present)
    j = next_.parents.index(tuple(parent_knots))
    assert next_.fresh[j]==extra
    seed_labels = {v:sorted(tuple(sorted((labels[a],labels[b]))) for bit,(a,b) in wired.items() if v in (a,b))
                   for v in parent_knots}
    physical_edges = list(wired.values())
    remote = {i for i,mask in enumerate(labels[:-1]) if mask is None}
    away = set(range(old_count))-remote
    physical = nx.Graph(physical_edges)
    assert nx.is_connected(physical.subgraph(away)) and nx.is_connected(physical.subgraph(remote|{old_count}))
    upper = sum((a in away)!=(b in away) for a,b in physical_edges)
    pair_min = checked_common_bound(physical_edges,old_count,parent_knots[:2])
    all_min = checked_common_bound(physical_edges,old_count,parent_knots)
    assert pair_min==all_min==upper==k+extra
    return {"source_leaves":k,"age":k-2,"n":old_count,"distinctions":len(wired),"edge_connectivity_of_wired_core":k,
            "fresh_at_common_top":next_.fresh[j],"exact_pair_and_full_input_bond_size":upper,
            "root_stars_by_subset_mask":{labels[v]:r for v,r in seed_labels.items()}}


def exact_table_only():
    s,u,v,w,f,a,z,x = range(8)
    common = [(s,u),(s,v),*[(u,x)]*3,*[(v,x)]*3,*[(s,a)]*2,*[(a,z)]*2,*[(z,x)]*2]
    quiet = (*common,*[(s,w)]*4,*[(w,x)]*3,*[(s,f)]*3,*[(f,x)]*4)
    flip = (*common,*[(w,x)]*4,*[(s,w)]*3,*[(f,x)]*3,*[(s,f)]*4)
    arms = (quiet,flip)
    bonds = [set(all_bonds(row,x)) for row in arms]
    assert all(lawful(row,x) for row in arms) and bonds[0]==bonds[1]
    support = [tuple(stars_of(row,x)[k] for k in (u,w)) for row in arms]
    assert support[0]==support[1]
    scores = [core_pair_fresh(row,x,(u,w)) for row in arms]
    assert [r["fresh"] for r in scores]==[2,3]
    return {"all_literal_bond_supports_equal":True,"bond_count":len(bonds[0]),"parent_supports":support[0],
            "group_update_original_flipped":scores,"same_selected_loose_distinctions_supplied":False}


def main():
    broad = [seven_knots(r) for r in (0,1,2,4,8,16,32)]
    lifted = []
    for k in (3,4,5,6):
        a,b = (cube(k,extra) for extra in (0,1))
        assert a["root_stars_by_subset_mask"]==b["root_stars_by_subset_mask"]
        lifted.append([a,b])
    with Path(__file__).open("rb") as handle:
        source_hash = file_digest(handle,"sha256").hexdigest()
    receipt = {"source_sha256":source_hash,"continuing_identified_families":broad,"reached_cube_families":lifted,
               "unrestricted_global_deck_control":exact_table_only()}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(receipt,indent=2)+"\n")
    print(len(broad),len(lifted),receipt["unrestricted_global_deck_control"]["bond_count"],flush=True)


if __name__=="__main__":
    main()
