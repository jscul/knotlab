"""Exact ordinary routes among old physical marks and every midpoint ball."""

from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
import gzip
import json
from pathlib import Path

import sources


HERE = Path(__file__).resolve().parent
OUT = sources.ROOT / "artifacts" / HERE.parent.name / HERE.name / "routes.json.gz"
PRIMARY = {"B": 6, "J0": 6, "J1": 12, "J2": 6, "C1": 6, "T4": 12, "T8": 12, "J1x2": 2}
SCORED = ((0, 2), (2, 5), (3, 4), (8, 12), (0, 15))


def incidence(stars, extra_marks=()):
    holders = defaultdict(list)
    for knot, star in enumerate(stars):
        for bit in star:
            holders[bit].append(knot)
    n = len(stars)
    names = []
    neighbors = [[] for _ in stars]
    nodes = {}
    for bit, members in holders.items():
        assert len(members) in (1, 2)
        if len(members) == 1 and bit not in extra_marks:
            continue
        v = n + len(names)
        names.append(bit)
        nodes[bit] = v
        neighbors.append(members)
        for knot in members:
            neighbors[knot].append(v)
    return neighbors, nodes, names


def breadth(neighbors, roots, count=False):
    distance = [-1] * len(neighbors)
    ways = [0] * len(neighbors) if count else None
    order = list(roots)
    for node in order:
        distance[node] = 0
        if count:
            ways[node] = 1
    for node in order:
        step = distance[node] + 1
        for nxt in neighbors[node]:
            if distance[nxt] == -1:
                distance[nxt] = step
                order.append(nxt)
            if count and distance[nxt] == step:
                ways[nxt] += ways[node]
    assert len(order) == len(neighbors)
    return distance, ways, order


def tag_names(rings, seams):
    names = ["knots", "original", "born", "born_now", "path_ancestry", "born_path_ancestry",
             "born_outside_path_ancestry", "born_with_hot_original_ancestor", "born_with_both_exclusive_rings"]
    for i in range(len(rings)):
        names.extend(f"ring_{i}_{topic}" for topic in ("born_exclusive", "born_pure_exclusive", "born_mixed_exclusive", "born_inclusive"))
    for i in range(len(seams)):
        names.extend(f"seam_{i}_{topic}" for topic in ("born_inclusive", "born_without_exclusive_ring_ancestry"))
    return names


def tags_for(origins, birth_ages, age, spec, hot):
    roles = spec["roles"]
    path = set(roles["background"])
    rings = [set(group) for group in roles.get("rings", [])]
    if roles.get("cut_appendage"):
        rings = [set(roles["cut_appendage"])]
    exclusive = [ring - path for ring in rings]
    seams = roles.get("seams", [])
    names = tag_names(rings, seams)
    tags = []
    for ancestors, born in zip(origins, birth_ages, strict=True):
        is_path = ancestors <= path
        evidence = [True, born == 0, born > 0, born == age and born > 0, is_path, born > 0 and is_path,
                    born > 0 and not is_path, born > 0 and bool(ancestors & hot),
                    born > 0 and sum(bool(ancestors & row) for row in exclusive) == 2]
        for ring, group in zip(rings, exclusive, strict=True):
            belongs = born > 0 and bool(ancestors & group)
            evidence.extend((belongs, belongs and ancestors <= ring, belongs and not ancestors <= ring,
                             born > 0 and bool(ancestors & ring)))
        for i, seam in enumerate(seams):
            belongs = born > 0 and seam in ancestors
            evidence.extend((belongs, belongs and not ancestors & exclusive[i]))
        assert len(evidence) == len(names)
        tags.append(tuple(i for i, flag in enumerate(evidence) if flag))
    return names, tags


def route_tag_counts(neighbors, start, targets, scan, tags, width):
    """Count routes visiting each tag by complementary DP on the shortest-route DAG."""
    distance, ways, order = scan
    seen = set(targets)
    queue = list(targets)
    for node in queue:
        for parent in neighbors[node]:
            if distance[parent] + 1 == distance[node] and parent not in seen:
                seen.add(parent)
                queue.append(parent)
    avoids = {start: [1] * width}
    n_knots = len(tags)
    for node in order:
        if node == start or node not in seen:
            continue
        values = [0] * width
        for parent in neighbors[node]:
            if distance[parent] + 1 == distance[node]:
                for i, value in enumerate(avoids[parent]):
                    values[i] += value
        if node < n_knots:
            for i in tags[node]:
                values[i] = 0
        avoids[node] = values
    return {node: [ways[node] - c for c in avoids[node]] for node in targets}


def ball(neighbors, centers, tags, width):
    distance, _, _ = breadth(neighbors, centers)
    most = max(distance[:len(tags)])
    shells = [[0] * width for _ in range(most+1)]
    for knot, categories in enumerate(tags):
        row = shells[distance[knot]]
        for category in categories:
            row[category] += 1
    cumulative = [shells[0]]
    for row in shells[1:]:
        cumulative.append([a+b for a,b in zip(cumulative[-1], row, strict=True)])
    assert cumulative[-1][0] == len(tags)
    return {"shells": shells, "cumulative": cumulative}


def physical(node, n_knots, distinctions):
    return ["k", node] if node < n_knots else ["d", distinctions[node-n_knots]]


def literal_node(identity, n_knots, nodes):
    kind, number = identity
    return number if kind == "k" else nodes[number]


def shortest_witness(node, goal, distances, neighbors):
    path = [node]
    while node != goal:
        node = min(nxt for nxt in neighbors[node] if distances[nxt] == distances[node]-1)
        path.append(node)
    return path


def grade(stars, anchors, names, tags, source_midpoints):
    neighbors, node_of, distinctions = incidence(stars)
    n = len(stars)
    marks = [node_of[d] for d in anchors]
    scans = {node: breadth(neighbors, (node,), count=True) for node in marks}
    balls = []
    indexed = {}

    def center_ball(midpoints):
        if midpoints not in indexed:
            indexed[midpoints] = len(balls)
            balls.append({"centers": [physical(node, n, distinctions) for node in midpoints],
                          **ball(neighbors, midpoints, tags, len(names))})
        return indexed[midpoints]

    pairs = []
    for i, head in enumerate(marks[:-1]):
        da, wa, order = scans[head]
        from_tag = route_tag_counts(neighbors, head, marks[i+1:], scans[head], tags, len(names))
        internal = defaultdict(list)
        for node in order:
            internal[da[node]].append(node)
        for j in range(i+1, len(marks)):
            tail = marks[j]
            db, wb, _ = scans[tail]
            length = da[tail]
            assert length == 2*(j-i)
            half = length//2
            mids = tuple(sorted(node for node in internal[half] if db[node] == half))
            weights = [wa[node] * wb[node] for node in mids]
            assert sum(weights) == wa[tail]
            route_count = wa[tail]
            counts = from_tag[tail]
            assert all(0 <= v <= route_count for v in counts) and counts[0] == route_count
            assert route_count-counts[names.index("born")] == 1
            key = (i, j)
            if key not in source_midpoints:
                assert len(mids) == 1 and route_count == 1
                source_midpoints[key] = physical(mids[0], n, distinctions)
            fixed = literal_node(source_midpoints[key], n, node_of)
            assert fixed in mids
            row = {"i": i, "j": j, "steps": half, "routes": route_count,
                   "routes_visiting_tag": counts, "route_weights_by_midpoint": weights,
                   "union_profile": center_ball(mids), "fixed_profile": center_ball((fixed,))}
            if key in SCORED:
                walks = [shortest_witness(mid, head, da, neighbors)[::-1] +
                         shortest_witness(mid, tail, db, neighbors)[1:] for mid in mids]
                assert all(len(set(walk)) == length+1 for walk in walks)
                row["one_route_per_midpoint"] = [[physical(node,n,distinctions) for node in walk] for walk in walks]
            pairs.append(row)
    return {"pairs": pairs, "profiles": balls, "tags": names}


def termination_reading(stop, last, requested):
    return {"status": stop["status"], "last": last, "requested": requested,
            **{key: v for key, v in stop.items() if key.startswith("planned_")}}


def prepare_trace(spec, occupied, requested):
    stages = {}
    source_midpoints = {}
    origins = []
    birth_ages = []
    hot = set()
    before = None
    anchors = spec["roles"]["anchors"]
    assert len(anchors) == 16
    generated = sources.generate(spec, occupied, requested)
    while True:
        try:
            age, frame = next(generated)
        except StopIteration as stop:
            return {"stages": stages, "termination": termination_reading(stop.value, max(stages), requested),
                    "activity_mask": sorted(hot), "original_mark_labels": anchors}
        stars = frame["stars"]
        if age == 0:
            for j, support in enumerate(stars):
                origins.append({j})
                birth_ages.append(0)
                if occupied.intersection(support):
                    hot.add(j)
        else:
            for j in frame["born"]:
                assert j == len(origins)
                born_from = frame["parent_sets"][j]
                assert all(birth_ages[p] == age-1 for p in born_from)
                origins.append(set.union(*(origins[p] for p in born_from)))
                birth_ages.append(age)
        names, tags = tags_for(origins, birth_ages, age, spec, hot)
        scored = grade(stars, anchors, names, tags, source_midpoints)
        scored.update(knots=len(stars), distinctions=frame["distinction_count"], introduced=len(frame["born"]))
        if before is not None:
            for old, new in zip(before["pairs"], scored["pairs"], strict=True):
                assert old["routes"] <= new["routes"]
                old_mids = before["profiles"][old["union_profile"]]["centers"]
                new_mids = scored["profiles"][new["union_profile"]]["centers"]
                assert all(mid in new_mids for mid in old_mids)
                if age > (new["steps"]-1)//2:
                    assert new["routes"] == old["routes"] and len(old_mids) == len(new_mids)
        stages[age] = scored
        before = scored


def side_bins(i, j, seam):
    kind = "opposite" if i < seam <= j else "same_side"
    near = min(abs(seam-v) for v in (i, i+1, j, j+1))
    return [kind, "far_endpoints" if near >= 3 else "near_endpoint"]


def geometry(frame, pair, key):
    profile = frame["profiles"][pair[key]]
    return [row[0] for row in profile["cumulative"]]


def pair_contrast(arm, quiet, seams):
    outcome = Counter()
    by_seam = {str(seam): defaultdict(Counter) for seam in seams}
    witness = {}
    for x, y in zip(arm["pairs"], quiet["pairs"], strict=True):
        k = (x["i"], x["j"])
        assert x["steps"] == y["steps"]
        delta = x["routes"] - y["routes"]
        result = "more" if delta > 0 else "fewer" if delta < 0 else "equal"
        outcome[result] += 1
        for seam in seams:
            for kind in side_bins(*k, seam):
                by_seam[str(seam)][kind][result] += 1
        for key in ("union_profile", "fixed_profile"):
            if geometry(arm, x, key) != geometry(quiet, y, key):
                outcome[f"different_{key}"] += 1
        if k in SCORED:
            witness[f"{k[0]},{k[1]}"] = {"route_counts_quiet_treatment": [y["routes"], x["routes"]],
                                       "profiles_quiet_treatment": {k: [geometry(quiet, y, k), geometry(arm, x, k)]
                                                                    for k in ("union_profile", "fixed_profile")}}
    return {"pairs_comparison": dict(outcome), "by_seam": by_seam, "selected": witness}


def compare(arm, quiet, seams):
    shared = sorted(arm["stages"].keys() & quiet["stages"].keys())
    return {age: pair_contrast(arm["stages"][age], quiet["stages"][age], seams) for age in shared}


def interaction(traces):
    shared = set.intersection(*(set(row["stages"]) for row in traces))
    result = {}
    for age in sorted(shared):
        frames = [row["stages"][age] for row in traces]
        routes, union, fixed = {}, {}, {}
        for x0, x1, x2, x3 in zip(*(frame["pairs"] for frame in frames), strict=True):
            pair = f"{x0['i']},{x0['j']}"
            interaction = x3["routes"] - x1["routes"] - x2["routes"] + x0["routes"]
            if interaction:
                routes[pair] = interaction
            for key, report in (("union_profile", union), ("fixed_profile", fixed)):
                profiles = [geometry(frame, row, key) for frame, row in zip(frames, (x0,x1,x2,x3), strict=True)]
                totals = []
                for radius in range(max(map(len, profiles))):
                    a,b,c,d = (values[min(radius, len(values)-1)] for values in profiles)
                    totals.append(d-b-c+a)
                if any(totals):
                    report[pair] = totals
        result[age] = {"nonzero_route_interactions": routes, "nonzero_midpoint_ball_interactions": union,
                       "nonzero_fixed_ball_interactions": fixed}
    return result


def separate_loose_control(spec):
    stream = sources.generate(spec, frozenset(), 1)
    _, source = next(stream)
    _, successor = next(stream)
    # Take the first (smallest named) source loose distinction at b0 and b2.
    roots = [min(source["loose"][k]) for k in (0, 2)]
    readings = []
    for stage in (source, successor):
        graph, nodes, _ = incidence(stage["stars"], roots)
        reading, ways, _ = breadth(graph, (nodes[roots[0]],), count=True)
        readings.append({"hops": reading[nodes[roots[1]]], "routes": ways[nodes[roots[1]]],
                         "holders": [graph[nodes[bit]] for bit in roots]})
    assert readings[0]["hops"] == 6 and readings[1]["hops"] == 2
    return {"source": spec["id"], "physical_source_loose_marks": roots, "readings": readings}


def original_pair_spans(spec):
    result = {}
    for seam in spec["roles"]["seams"]:
        coordinate = seam * 2
        pairs = []
        for i,j in combinations(range(16),2):
            a,b = 2*i+1,2*j+1
            pairs.append({"i":i,"j":j,"kind_and_endpoint_offset_class": side_bins(i,j,seam),
                          "source_interval_to_seam_hops": max(a-coordinate, coordinate-b, 0),
                          "source_midpoint_to_seam_hops": abs((a+b)//2-coordinate)})
        result[str(seam)] = pairs
    return result


def parallel_control():
    # Distinct names 0,1 and 2 all meet the same two ordinary holders.
    graph, nodes, _ = incidence(((0,1,2), (0,1,2)))
    distance, paths, _ = breadth(graph, (nodes[0],), count=True)
    assert distance[nodes[1]] == 2 and paths[nodes[1]] == 2
    return {"distance_hops": 2, "routes": 2, "midpoint_knots": [0,1]}


def literal_route_replay(spec, load, scored, through):
    """Independently enumerate each literal shortest route on a small matched control."""
    stage = None
    origins = []
    birth_ages = []
    hot = set()
    for age, frame in sources.generate(spec, load, through):
        stage = frame
        if age == 0:
            origins = [{k} for k in range(len(stage["stars"]))]
            birth_ages = [0] * len(origins)
            hot = {k for k, star in enumerate(stage["stars"]) if load.intersection(star)}
        else:
            for k in stage["born"]:
                origins.append(set.union(*(origins[p] for p in stage["parent_sets"][k])))
                birth_ages.append(age)
    assert stage is not None and age == through
    graph, nodes, names = incidence(stage["stars"])
    marks = [nodes[d] for d in spec["roles"]["anchors"]]
    n = len(stage["stars"])
    tags, marked = tags_for(origins, birth_ages, through, spec, hot)
    assert tags == scored["tags"]
    total = 0
    for row in scored["pairs"]:
        start, end = marks[row["i"]], marks[row["j"]]
        distance, _, _ = breadth(graph, (end,))
        queue = [(start,)]
        counted = 0
        mids = Counter()
        categories = Counter()
        while queue:
            path = queue.pop()
            if path[-1] != end:
                queue.extend((*path, nxt) for nxt in graph[path[-1]] if distance[nxt] == distance[path[-1]]-1)
                continue
            counted += 1
            categories.update({k for v in path if v < n for k in marked[v]})
            assert len(path) == 2*row["steps"]+1
            mids[tuple(physical(path[len(path)//2], n, names))] += 1
        centers = scored["profiles"][row["union_profile"]]["centers"]
        assert counted == row["routes"] and [categories[i] for i in range(len(tags))] == row["routes_visiting_tag"]
        assert mids == dict(zip(map(tuple,centers), row["route_weights_by_midpoint"], strict=True))
        total += counted
    return {"age": through, "pairs": len(scored["pairs"]), "shortest_routes": total}


def dose_summary(assignments, masks):
    quiet = masks[assignments["w00"]["activity_mask"]]
    by_weight = defaultdict(list)
    for word, item in assignments.items():
        by_weight[item["loaded"]].append(masks[item["activity_mask"]])
    result = {}
    for weight, histories in sorted(by_weight.items()):
        ages = set.intersection(set(quiet["stages"]), *(set(x["stages"]) for x in histories))
        result[weight] = {}
        for age in sorted(ages):
            q = quiet["stages"][age]["pairs"]
            changes = []
            by_pair = [[] for _ in q]
            for history in histories:
                current = history["stages"][age]["pairs"]
                delta = [x["routes"]-y["routes"] for x,y in zip(current,q,strict=True)]
                changes.append(sum(delta))
                for values, shift in zip(by_pair, delta, strict=True):
                    values.append(shift)
            result[weight][age] = {"assignments": len(histories), "range_of_total_route_change": [min(changes), max(changes)],
                                   "mean_total_route_change": [sum(changes), len(changes)],
                                   "pair_change_range_and_mean": {f"{row['i']},{row['j']}": [[min(delta),max(delta)],
                                                                                           [sum(delta),len(delta)]]
                                                                  for row,delta in zip(q,by_pair,strict=True)}}
    return result


def main():
    specs = sources.cases()
    cases = {}
    for case, requested in PRIMARY.items():
        spec = specs[case]
        loads = sources.loads(spec)
        if case in {"J0", "J2"}:
            loads = {"0":loads["0"]}
        traces = {}
        assignments = {}
        source_stars = sources.growth.predecessor().source_stars(spec)
        for code, occupied in loads.items():
            mask = ",".join(str(j) for j, support in enumerate(source_stars) if occupied.intersection(support))
            assignments[code] = {"loaded": len(occupied), "activity_mask": mask, "physical_occupied": sorted(occupied)}
            if mask not in traces:
                traces[mask] = prepare_trace(spec, occupied, requested)
                print(case, code, traces[mask]["termination"], flush=True)
        line = {"assignments": assignments, "activity_geometries": traces}
        line["source_spans"] = original_pair_spans(spec)
        if case == "J1x2":
            line["dose_summary"] = dose_summary(assignments, traces)
        else:
            by_code = {code: traces[entry["activity_mask"]] for code, entry in assignments.items()}
            seams = spec["roles"]["seams"]
            if len(by_code)>1:
                line["loaded_vs_quiet"] = {code: compare(row, by_code["0"], seams)
                                            for code, row in by_code.items() if code != "0"}
            if len(by_code)==4:
                line["joint_interaction"] = interaction([by_code[str(i)] for i in range(4)])
                line["conditional_donor"] = {"ring_0_receiver_1_loaded": compare(by_code["3"], by_code["2"], seams),
                                             "ring_1_receiver_0_loaded": compare(by_code["3"], by_code["1"], seams)}
        cases[case] = line
    quiet_stages = cases["B"]["activity_geometries"][""]["stages"]
    quiet_controls = {}
    for case in ("J0", "J1", "J2", "C1", "T4", "T8"):
        arm = cases[case]["activity_geometries"][""]["stages"]
        checked = 0
        for age in sorted(arm.keys() & quiet_stages.keys()):
            for observed,expected in zip(arm[age]["pairs"],quiet_stages[age]["pairs"],strict=True):
                assert observed["routes"] == expected["routes"]
                checked += 1
        quiet_controls[case] = checked
    direct = {}
    for case,code in (("J1","0"),("J1","1"),("T4","3"),("T8","3"),("J1x2","w02")):
        arm = cases[case]
        tag = arm["assignments"][code]["activity_mask"]
        direct[f"{case}/{code}"] = literal_route_replay(specs[case], sources.loads(specs[case])[code],
                                                       arm["activity_geometries"][tag]["stages"][2], 2)
    receipt = {"source_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
               "input_sha256": sha256((HERE/"inputs.json").read_bytes()).hexdigest(),
               "sources_code_sha256": sha256((HERE/"sources.py").read_bytes()).hexdigest(),
               "case_counts": {"assignments": sum(len(row["assignments"]) for row in cases.values()),
                               "geometries": sum(len(row["activity_geometries"]) for row in cases.values())},
               "controls": {"parallel_shared_distinctions": parallel_control(), "older_loose_marks":separate_loose_control(specs["B"]),
                            "literal_routes_no_dynamic_count": direct, "matches_against_bare_background": quiet_controls},
               "caps": sources.DEFAULT_CAPS, "cases": cases}
    with OUT.open("wb") as raw, gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as zipped:
        writer = json.JSONEncoder(separators=(",", ":"))
        chunk = []
        for token in writer.iterencode(receipt):
            chunk.append(token)
            if len(chunk) == 16_384:
                zipped.write("".join(chunk).encode())
                chunk.clear()
        zipped.write(("".join(chunk)+"\n").encode())
    print(OUT.name, OUT.stat().st_size, receipt["case_counts"], flush=True)


if __name__ == "__main__":
    main()
