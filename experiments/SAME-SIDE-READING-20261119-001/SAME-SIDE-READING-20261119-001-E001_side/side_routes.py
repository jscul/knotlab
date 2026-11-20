"""Ordinary routes and fixed old mark-centered knot balls, with exact side tests."""

from collections import Counter, defaultdict
from hashlib import file_digest
from itertools import combinations
from pathlib import Path
import gzip
import json
import sys

import side_sources as sources


HERE = Path(__file__).resolve().parent
OUT = sources.ROOT / "artifacts" / HERE.parent.name / HERE.name / "side_routes.json.gz"
OLD_ROUTES = sources.OLDER.with_name("routes.py")
sys.path.insert(0, str(OLD_ROUTES.parent))
from routes import breadth, incidence


def digest(path):
    with path.open("rb") as file:
        return file_digest(file, "sha256").hexdigest()


def components(meetings, n, omitted):
    graph = [set() for _ in range(n)]
    for u,v in meetings:
        if u not in omitted and v not in omitted:
            graph[u].add(v)
            graph[v].add(u)
    result = {}
    for u in range(n):
        if u in omitted or u in result:
            continue
        todo = [u]
        found = {u}
        for node in todo:
            for neighbor in graph[node] - found:
                found.add(neighbor)
                todo.append(neighbor)
        key = tuple(sorted(found))
        result.update(dict.fromkeys(found, key))
    return result


def study_plan(spec):
    anchors = tuple(spec["roles"]["anchors"])
    seams = spec["roles"]["seams"] or [4]
    chosen = sources.marksets(spec, full=spec["id"] == "J1")
    translated = set(sources.marksets(spec))
    n = len(spec["sizes"])
    removed = {str(seam): components(spec["meetings"], n, {seam}) for seam in seams}
    if len(seams) > 1:
        removed["interval"] = components(spec["meetings"], n, set(seams))
    rows = []
    for marks in chosen:
        group = {label: next(lookup[h] for mark in marks for h in (mark,mark+1) if h in lookup)
                 for label, lookup in removed.items()}
        assert all(holder in side or holder not in removed[label]
                   for label, side in group.items() for mark in marks for holder in (mark,mark+1))
        rows.append({"marks": marks, "translated": marks in translated,
                     "offsets": {str(s): sources.offset(marks,s) for s in seams}, "side_regions": group})
    return anchors, seams, rows


def measure_stage(stars, roots, ancestry, frameset, age, verify_formula=False):
    table, points, _ = incidence(stars)
    active_marks = sorted({mark for query in frameset for mark in query["marks"]})
    n = len(stars)
    scans = {mark: breadth(table, (points[roots[mark]],), count=True) for mark in active_marks}
    measured = {}
    for i, j in sorted({pair for query in frameset for pair in combinations(query["marks"],2)}):
        d, paths, _ = scans[i]
        node = points[roots[j]]
        assert d[node] == 2*(j-i)
        measured[(i,j)] = paths[node]

    shellsets = {}
    reach = max(max(scan[0][:n]) for scan in scans.values())
    for mark, (distance, _, _) in scans.items():
        shells = [0] * ((reach+1)//2)
        for knot, d in enumerate(distance[:n]):
            assert d % 2 == 1
            shells[(d-1)//2] |= 1 << knot
        for k in range(1,len(shells)):
            shells[k] |= shells[k-1]
        assert shells[-1].bit_count() == n
        shellsets[mark] = shells

    sides = {key for row in frameset for key in row["side_regions"].values()}
    unmapped = {side: [knot for knot, origin in enumerate(ancestry) if not origin <= allowed]
                for side in sides for allowed in (set(side),)}
    bad = {(side,mark): min((scans[mark][0][knot] for knot in knots), default=None)
           for side, knots in unmapped.items() for mark in active_marks}
    profiles = []
    packed = {}
    index = []
    side_boundaries = []
    for row in frameset:
        selected = row["marks"]
        counts = []
        for layer in zip(*(shellsets[i] for i in selected), strict=True):
            union = 0
            for mask in layer:
                union |= mask
            count = union.bit_count()
            counts.append(count)
            if count == n:
                break
        curve = tuple(counts)
        slot = packed.setdefault(curve, len(profiles))
        if slot == len(profiles):
            profiles.append(curve)
        index.append(slot)
        side_boundaries.append({label: min((bad[side,j] for j in selected if bad[side,j] is not None), default=None)
                                for label,side in row["side_regions"].items()})
    result = {"knots": n, "distinctions": sum(map(len,stars))-sum(len(a)==2 for a in table[n:]),
              "ball_profiles_at_odd_hops": profiles, "query_profile_ids": index,
              "first_non_side_ancestry_hops": side_boundaries,
              "pairs": [[i,j,measured[i,j]] for i,j in measured]}
    if verify_formula:
        # Phase-zero incidence is the restriction to source knots; all other links are measured by ancestry.
        n_source = next((i for i,x in enumerate(age) if x), len(age))
        old_graph, old_points, _ = incidence(stars[:n_source])
        for mark, (distance, _, _) in scans.items():
            original, _, _ = breadth(old_graph, (old_points[roots[mark]],))
            assert all(distance[v] == 2*age[v]+min(original[p] for p in lineage)
                       for v,lineage in enumerate(ancestry))
    return result


def ancestry_at(frame, age, ancestry, knot_ages):
    if age == 0:
        ancestry.extend({j} for j in range(len(frame["stars"])))
        knot_ages.extend([0] * len(ancestry))
    else:
        for born in frame["born"]:
            assert born == len(ancestry)
            parents = frame["parent_sets"][born]
            assert all(knot_ages[p] == age-1 for p in parents)
            ancestry.append(set.union(*(ancestry[p] for p in parents)))
            knot_ages.append(age)


def make_trace(spec, occupied, anchors, queries, verify_flip=False):
    ancestry, knot_ages = [], []
    cap_age = sources.AGES[spec["id"]]
    stages = {}
    graph_stages = sources.generate(spec, occupied, cap_age, caps=sources.CAPS)
    renaming = None
    while True:
        try:
            age, frame = next(graph_stages)
        except StopIteration as finish:
            result = {"last_completed_age": max(stages), "requested_age": cap_age, "status": finish.value["status"],
                      **{key:v for key,v in finish.value.items() if key.startswith("planned_")}}
            return {"stages": stages, "termination": result, "relabel_age": renaming}
        ancestry_at(frame, age, ancestry, knot_ages)
        stages[age] = measure_stage(frame["stars"], anchors, ancestry, queries, knot_ages,
                                    verify_formula=age <= 2 or verify_flip)
        assert stages[age]["knots"] == len(frame["stars"])
        assert stages[age]["distinctions"] == frame["distinction_count"]
        if age:
            prior = stages[age-1]
            for q in range(len(queries)):
                u,v = curve_at(prior,q),curve_at(stages[age],q)
                for k in range(max(len(u),len(v))):
                    assert value_at(u,k) <= value_at(v,k)
                    if k < age:
                        assert value_at(u,k) == value_at(v,k)
        if verify_flip and age == 2:
            top = max(d for star in frame["stars"] for d in star)
            permuted = [tuple(top-d for d in reversed(star)) for star in reversed(frame["stars"])]
            check = measure_stage(permuted, tuple(top-d for d in anchors), list(reversed(ancestry)), queries,
                                  list(reversed(knot_ages)))
            assert check == stages[age]
            renaming = age


def curve_at(stage, query):
    return stage["ball_profiles_at_odd_hops"][stage["query_profile_ids"][query]]


def value_at(curve, k):
    return curve[min(k,len(curve)-1)]


def age_contrast(first, second, queries, donor):
    matched = sorted(first["stages"].keys() & second["stages"].keys())
    scope = {"matched_ages": matched, "ages_only_quiet": sorted(first["stages"].keys()-second["stages"].keys()),
             "ages_only_treatment": sorted(second["stages"].keys()-first["stages"].keys())}
    donor = str(donor)
    by_age = {}
    best_below, best_side, radius_by_offset = [], [], {}
    for age in matched:
        quiet, treated = first["stages"][age], second["stages"][age]
        lookup_q = {(i,j):v for i,j,v in quiet["pairs"]}
        route_rows = [[i,j,lookup_q[i,j],count] for i,j,count in treated["pairs"] if count != lookup_q[i,j]]
        data = []
        for q,row in enumerate(queries):
            b0,b1 = curve_at(quiet,q), curve_at(treated,q)
            changes = [(2*k+1,value_at(b0,k),value_at(b1,k)) for k in range(max(len(b0),len(b1)))
                       if value_at(b0,k) != value_at(b1,k)]
            if not changes:
                continue
            left = quiet["first_non_side_ancestry_hops"][q][donor]
            right = treated["first_non_side_ancestry_hops"][q][donor]
            reach = 2*row["offsets"][donor]+1
            below = [entry for entry in changes if entry[0] < reach]
            pure = [entry for entry in changes if all(r is None or entry[0] < r for r in (left,right))]
            assert not below or age >= 2
            assert all(reach <= 2*(r-1)+5 for r,_,_ in changes)
            data.append([q,*changes[0],len(changes),below[0] if below else None,pure[0] if pure else None])
            for kind, collection in ((below,best_below),(pure,best_side)):
                if kind:
                    hops,a,b = kind[0]
                    collection.append({"hops":hops,"age":age,"query":q,"marks":row["marks"],"offset":row["offsets"][donor],
                                       "quiet_loaded":[a,b],"ancestry_boundary_hops":[left,right]})
            offset = row["offsets"][donor]
            previous = radius_by_offset.setdefault(offset,{})
            previous[age] = min(changes[0][0], previous.get(age,changes[0][0]))
        by_age[age] = {"changed_route_counts": route_rows,"changed_balls": data}
    earliest = lambda rows: sorted(rows,key=lambda r:(r["hops"],r["age"],r["offset"],r["query"]))[:12]
    return {**scope,"cohort":by_age,"smallest_below_seam":earliest(best_below),"smallest_side_ancestry":earliest(best_side),
            "minimum_changed_hops_by_offset_age":radius_by_offset}


def joint(traces, queries, seams):
    valid = set.intersection(*(set(row["stages"]) for row in traces))
    stages = {}
    first = {"any":None,"below_both":None,"side_ancestry":None}
    for age in sorted(valid):
        frames = [row["stages"][age] for row in traces]
        count = Counter()
        for q,row in enumerate(queries):
            curves = [curve_at(s,q) for s in frames]
            nearby = min(2*row["offsets"][str(seam)]+1 for seam in seams)
            boundaries = [s["first_non_side_ancestry_hops"][q]["interval"] for s in frames]
            for k in range(max(map(len,curves))):
                vals = [value_at(c,k) for c in curves]
                contrast = vals[3]-vals[2]-vals[1]+vals[0]
                if not contrast:
                    continue
                assert age >= 2
                radius = 2*k+1
                data = {"age":age,"hops":radius,"query":q,"marks":row["marks"],"counts_neither_first_second_both":vals,
                        "interaction":contrast,"nearest_seam_hops":nearby,"interval_boundary_hops":boundaries}
                for flag in ("any", *(("below_both",) if radius<nearby else ()),
                             *(("side_ancestry",) if all(b is None or radius<b for b in boundaries) else ())):
                    count[flag] += 1
                    incumbent = first[flag]
                    if incumbent is None or (age,radius,q)<(incumbent["age"],incumbent["hops"],incumbent["query"]):
                        first[flag] = data
        stages[age] = {"nonadditive_cells": count}
    return {"matched_ages":sorted(valid),"by_age":stages,"first":first}


def dose(choices, panels, queries, seam):
    weights = defaultdict(list)
    for code,row in choices.items():
        weights[row["load_count"]].append(code)
    ranges = {}
    best = {"any":None,"below_seam":None,"side_ancestry":None}
    for weight, codes in sorted(weights.items()):
        match = set.intersection(*(set(panels[c]["stages"]) for c in codes))
        entries = {}
        for age in sorted(match):
            frames = [panels[c]["stages"][age] for c in codes]
            diff_cells = 0
            for q,query in enumerate(queries):
                curves = [curve_at(s,q) for s in frames]
                nearby = 2*query["offsets"][str(seam)]+1
                bounds = [s["first_non_side_ancestry_hops"][q][str(seam)] for s in frames]
                for k in range(max(map(len,curves))):
                    observations = [value_at(c,k) for c in curves]
                    a,b = min(observations),max(observations)
                    if a == b:
                        continue
                    diff_cells += 1
                    r = 2*k+1
                    physical = list(range(len(codes)))
                    confined = [i for i in physical if bounds[i] is None or r<bounds[i]]
                    subsets = {"any":physical,"below_seam":physical if r<nearby else [],"side_ancestry":confined}
                    for flag, eligible in subsets.items():
                        if len(eligible) < 2:
                            continue
                        ia = min(eligible,key=observations.__getitem__)
                        ib = max(eligible,key=observations.__getitem__)
                        if observations[ia] == observations[ib]:
                            continue
                        data = {"weight":weight,"assignments_of_weight":len(codes),"eligible_assignments":len(eligible),
                                "age":age,"hops":r,"query":q,"marks":query["marks"],
                                "range":[observations[ia],observations[ib]],"mean":[sum(observations[i] for i in eligible),len(eligible)],
                                "low_high_preparations":[codes[ia],codes[ib]],"seam_hops":nearby,
                                "low_high_side_boundary_hops":[bounds[ia],bounds[ib]]}
                        incumbent = best[flag]
                        if incumbent is None or (r,age,q,weight)<(incumbent["hops"],incumbent["age"],incumbent["query"],incumbent["weight"]):
                            best[flag] = data
            entries[age] = diff_cells
        ranges[weight] = {"physical_preparations":len(codes),"different_cells_by_age":entries}
    return {"by_weight":ranges,"examples":best}


def arm_signature(spec, occupied):
    stars = sources.growth.predecessor().source_stars(spec)
    return tuple(i for i,star in enumerate(stars) if occupied.intersection(star))


def witness(spec, before, after, picked, seam):
    """Independently recompute two actual sets of counted knots from rootwise union."""
    marks = picked["marks"]
    age = picked["age"]
    radius = picked["hops"]
    anchors = spec["roles"]["anchors"]
    counted = []
    for state in (before,after):
        ancestry,knot_ages = [],[]
        for layer,frame in sources.generate(spec,state,age,caps=sources.CAPS):
            ancestry_at(frame,layer,ancestry,knot_ages)
        assert layer == age
        graph,points,_ = incidence(frame["stars"])
        sources_set = [points[anchors[m]] for m in marks]
        near,_,_ = breadth(graph,sources_set)
        per_source = [breadth(graph,(root,))[0] for root in sources_set]
        assert near == [min(values) for values in zip(*per_source,strict=True)]
        source_components = components(spec["meetings"],len(spec["sizes"]),{seam})
        side = set(next(source_components[h] for m in marks for h in (m,m+1) if h!=seam))
        result = [[i,knot_ages[i],near[i],sorted(lineage)] for i,lineage in enumerate(ancestry) if near[i]<=radius]
        counted.append({"knot_id_age_hops_ancestry":result,"all_ancestry_on_marked_side":all(set(row[3])<=side for row in result),
                        "first_not_side_hops":min((near[i] for i,lineage in enumerate(ancestry) if not lineage<=side),default=None)})
    assert [len(row["knot_id_age_hops_ancestry"]) for row in counted] == picked["quiet_loaded"]
    return {"query":picked,"both_arms":counted}


def main():
    result = {}
    extremes = {"strict":None,"pure":None}
    literal_witnesses = {}
    for case,spec in sources.cases().items():
        anchors,seams,queries = study_plan(spec)
        states = sources.loads(spec)
        geometries,choices,panels = {},{},{}
        for arm, state in states.items():
            activity = arm_signature(spec,state)
            key = ",".join(map(str,activity))
            choices[arm] = {"physical_occupied":sorted(state),"load_count":len(state),"activity_mask":key}
            if key not in geometries:
                geometries[key] = make_trace(spec,state,anchors,queries,verify_flip=case=="J1")
            panels[arm] = geometries[key]
        profiles = {"queries":queries,"mark_distinction_ids":anchors,"assignments":choices,"geometries":geometries}
        comparisons = []
        if set(panels) == {"0","1"}:
            comparisons.append(("0","1",seams[0]))
        elif set(panels) == {"0","1","2","3"}:
            comparisons.extend((("0","1",seams[0]),("2","3",seams[0]),("0","2",seams[1]),("1","3",seams[1])))
            profiles["joint"] = joint([panels[str(i)] for i in range(4)],queries,seams)
        elif len(panels) == 64:
            profiles["dose"] = dose(choices,panels,queries,seams[0])
            blank = panels["w00"]["stages"]
            assert all(stage["pairs"] == blank[age]["pairs"] for geom in geometries.values()
                       for age,stage in geom["stages"].items() if age in blank)
        all_comparisons = []
        for before,after,donor in comparisons:
            comp = age_contrast(panels[before],panels[after],queries,donor)
            comp.update(before=before,after=after,donor=donor)
            all_comparisons.append(comp)
            if case == "J1" and comp["smallest_below_seam"]:
                picked = comp["smallest_below_seam"][0]
                literal_witnesses["single_below_seam"] = {"case":case,"before":before,"after":after,"donor":donor,
                                                           **witness(spec,states[before],states[after],picked,donor)}
            for label,key in (("strict","smallest_below_seam"),("pure","smallest_side_ancestry")):
                if not comp[key]:
                    continue
                picked = comp[key][0]
                other = extremes[label]
                new_rank = (picked["hops"],picked["age"],picked["offset"],picked["query"])
                if other is None or new_rank<other[0]:
                    extremes[label] = (new_rank,case,before,after,donor,picked)
        profiles["donor_comparisons"] = all_comparisons
        result[case] = profiles
        print(case, len(queries), len(states), len(geometries), [x["termination"]["last_completed_age"] for x in geometries.values()],flush=True)
    for label,item in extremes.items():
        if item is None:
            continue
        _,case,before,after,donor,picked = item
        spec = sources.cases()[case]
        states = sources.loads(spec)
        literal_witnesses[label] = {"case":case,"before":before,"after":after,"donor":donor,
                                    **witness(spec,states[before],states[after],picked,donor)}
    receipt = {"sources_sha256":digest(HERE/"side_sources.py"),"inputs_sha256":digest(HERE/"inputs.json"),
               "source_sha256":digest(Path(__file__)),"caps":sources.CAPS,"cases":result,"smallest_literal_witnesses":literal_witnesses,
               "profile_conventions":{"first_index_hops":1,"successive_hops":2,"hop_zero_knots":0,
                                      "even_hops":"same knot count as preceding odd hop","shells":"successive differences including from zero",
                                      "after_first_saturation":"constant"}}
    with OUT.open("wb") as handle, gzip.GzipFile(filename="",fileobj=handle,mode="wb",mtime=0) as zipped:
        writer = json.JSONEncoder(separators=(",", ":"))
        chunk = []
        for token in writer.iterencode(receipt):
            chunk.append(token)
            if len(chunk) == 16_384:
                zipped.write("".join(chunk).encode())
                chunk.clear()
        zipped.write(("".join(chunk)+"\n").encode())
    print(OUT.name,OUT.stat().st_size,extremes,flush=True)


if __name__ == "__main__":
    main()
