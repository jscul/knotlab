"""Literal depth controls for fixed-terminal growth on the dense split core."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
OLD_GRAFT = Path("GROWN-END-READING-20261119-001/GROWN-END-READING-20261119-001-E001_readings")
EXTEND_ROUND = Path("EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend")
sys.path.insert(0, str(ROOT / "experiments" / OLD_GRAFT))
from graft_check import rows_from_edges  # noqa: E402
from verify import Arrangement, connected, reading, round_replay, start_audit  # noqa: E402


def original():
    n = 21
    index_pairs = list(combinations(range(n), 2))
    middle = {pair: n + i for i, pair in enumerate(index_pairs)}
    dark, light = n + len(index_pairs), n + len(index_pairs) + 1
    names = {}
    edges = []
    for a, b in index_pairs:
        hub = dark if min(b - a, n + a - b) <= 5 else light
        for role, end in ((a, a), (b, b), ("hub", hub)):
            name = len(edges)
            names[a, b, role] = name
            edges.append((name, middle[a, b], end))
    sigma = {2: 3, 3: 2}
    phi = {}
    for (a, b, role), x in names.items():
        u, v = sorted((sigma.get(a, a), sigma.get(b, b)))
        phi[x] = names[u, v, sigma.get(role, role)]
    return edges, names, middle, (dark, light), phi


def graft(edges, e, multiplicity):
    _, s, t = next(row for row in edges if row[0] == e)
    n = max(v for _, a, b in edges for v in (a, b)) + 1
    u, v, exterior = n, n + 1, n + 2
    extra = len(edges)
    left = tuple(range(extra, extra + multiplicity))
    right = tuple(range(extra + multiplicity, extra + 2 * multiplicity))
    loose = extra + 2 * multiplicity
    additions = [*((x, s, u) for x in left), *((x, t, v) for x in right),
                 (loose, u, exterior), (loose + 1, u, exterior),
                 (loose + 2, v, exterior), (loose + 3, v, exterior)]
    start = rows_from_edges([row for row in edges if row[0] != e] + additions)[:-1]
    return start, (s, t), (u, v), (left, right)


def path_end(ends, start, route, exterior_names=None):
    at = start
    for x in route:
        assert exterior_names is None or x in exterior_names
        a, b = ends[x]
        assert at in (a, b)
        at = b if a == at else a
    return at


def separating_paths(stage, core_names, poles, entries, ports, tips):
    ends, _, exterior = stage.holder_graph()
    assert exterior is not None
    exterior_names = set(stage.labels) - core_names
    routes = []
    for j, branch in enumerate(tips):
        loose_used = set()
        paths = []
        for tip, history in branch:
            loose = min(x for x in stage.stars[tip] if x in stage.loose and x not in loose_used)
            loose_used.add(loose)
            route = (*history, loose)
            assert path_end(ends, entries[j], route, exterior_names) == exterior
            paths.append(route)
        assert not set(paths[0]) & set(paths[1])
        # The only links of the exterior piece at the old terminal are its fixed ports.
        assert {x for x in exterior_names if poles[j] in ends[x]} == set(ports[j])
        routes.append(paths)
    complete = []
    for i, (left, right) in enumerate(zip(*ports)):
        path = (left, *routes[0][i], *reversed(routes[1][i]), right)
        assert path_end(ends, poles[0], path, exterior_names) == poles[1]
        complete.append(path)
    assert len({x for path in complete for x in path}) == sum(map(len, complete))
    return complete


def born_offshoot_tips(earlier, records, tips, first):
    offspring = defaultdict(list)
    for j, row in enumerate(records, len(earlier.stars)):
        if len(row["taken"]) == 1:
            u, x = next(iter(row["taken"].items()))
            if any(u == p for branch in tips for p, _ in branch):
                assert len(row["fresh"]) == 2 and row["demand"] == 1 and not row["implied"]
                offspring[u].append((j, x))
    if first:
        return [[(j, (x,)) for j, x in offspring[branch[0][0]]] for branch in tips]
    result = []
    for branch in tips:
        newborn = []
        for parent, old_path in branch:
            ((j, x),) = offspring[parent]
            newborn.append((j, (*old_path, x)))
        result.append(newborn)
    return result


def arity_four(stage, names, middle, hubs, marking, poles, core_count):
    dark, light = hubs
    marks = {names[2, 8, "hub"], names[2, 8, 8], names[0, 8, 8], names[0, 8, 0]}
    image = {marking[x] for x in marks}
    ends, neighbors, exterior = stage.holder_graph()
    assert set(stage.stars[middle[0, 8]]) == {names[0, 8, x] for x in (0, 8, "hub")}
    # Before the exchange, all neighbors of w2 are forced together on the shore opposite both middles.
    forced = {0, 8, light}
    assert all(set(ends[x]) & forced for x in marks)
    assert {next(v for v in ends[x] if v != middle[0, 8]) for x in stage.stars[middle[0, 8]]} == forced
    assert {x for x in stage.stars[middle[2, 8]] if x in marks} == {names[2, 8, "hub"], names[2, 8, 8]}

    shore = {light, middle[3, 8], middle[0, 8], 3, middle[3, 13]}
    # Place the entire graft except the first terminal with the second terminal.
    if poles[1] in shore:
        shore.update(range(core_count, len(stage.stars)))
        shore.add(exterior)
    mask = sum(1 << j for j in shore)
    full = (1 << len(neighbors)) - 1
    assert connected(mask, neighbors) and connected(full ^ mask, neighbors)
    cut = {x for x, (u, v) in ends.items() if (u in shore) != (v in shore)}
    assert image <= cut
    return {"marks_without_common_bond": sorted(marks), "image_marks": sorted(image),
            "image_witness_bond": sorted(cut), "image_witness_size": len(cut), "image_witness_shore": sorted(shore)}


def check_marking(stage, core_names, core_marking, names, middle, hubs, poles, core_count):
    marking = {x: core_marking[x] if x in core_names else x for x in stage.labels}
    assert set(marking.values()) == set(stage.labels)
    assert all(marking[x] == x for j in stage.live for x in stage.stars[j])
    assert reading(stage, stage, marking)[1]["keeps_reading"]
    holder_classes = defaultdict(set)
    for x, holders in stage.owners.items():
        holder_classes[tuple(holders)].add(x)
    groups = {frozenset(group) for group in holder_classes.values()}
    assert {frozenset(marking[x] for x in group) for group in groups} == groups

    dark, _ = hubs
    old_row = stage.stars[dark]
    image = {marking[x] for x in old_row}
    state = {names[2, 8, "hub"], names[2, 8, 8], names[0, 8, 8], names[0, 8, "hub"]}
    assert all(len(row & state) % 2 == 0 for row in stage.stars) and len(image & state) == 1
    _, neighbors, _ = stage.holder_graph()
    assert len(old_row) == 105 and connected(((1 << len(neighbors)) - 1) ^ (1 << dark), neighbors)
    return {"pointwise_live_and_flip_relation_verified": True, "allowed_difference": sorted(state),
            "violating_name": next(iter(state & image)), "current_dark_star_minimum": len(old_row),
            "image_minimum_lower_bound_or_infinite": len(image) + 1,
            "four_name_discrepancy": arity_four(stage, names, middle, hubs, marking, poles, core_count)}


def history(core, names, middle, hubs, phi, removed, multiplicity, depth, grow1):
    e = names[removed]
    assert phi[e] == e
    core_names = {x for x, _, _ in core} - {e}
    core_count = max(hubs) + 1
    raw, poles, entries, ports = graft(core, e, multiplicity)
    current = Arrangement.parse(raw)
    origin = start_audit(current)
    assert origin["census_open_legal"] and origin["meets_once"] == (multiplicity == 1)
    assert all(len(s) >= 3 for s in current.stars)
    tips = [[(p, ()), (p, ())] for p in entries]
    branch = {p: i for i, p in enumerate(entries)}
    rounds = []
    stages = []
    for age in range(depth + 1):
        assert all(len(branch_tips) == 2 for branch_tips in tips)
        paths = separating_paths(current, core_names, poles, entries, ports, tips)
        stages.append({"age": age, "junctions": len(current.stars), "distinctions": len(current.labels),
                       "live_per_branch": dict(Counter(branch[p] for p in current.live)),
                       "exterior_minimum": len(paths), "edge_disjoint_routes": paths,
                       **check_marking(current, core_names, phi, names, middle, hubs, poles, core_count)})
        if age == depth:
            break
        following = Arrangement.parse([sorted(row) for row in grow1(current.stars)])
        records = round_replay(current, following)
        for j, record in enumerate(records, len(current.stars)):
            parent_branches = {branch[p] for p in record["taken"]}
            assert len(parent_branches) == 1 and record["fresh"] and not record["implied"]
            branch[j] = next(iter(parent_branches))
        assert {branch[p] for p in following.live} == {0, 1}
        tips = born_offshoot_tips(current, records, tips, age == 0)
        rounds.append({"age": age + 1, "added_supports": [sorted(s) for s in following.stars[len(current.stars):]],
                       "added_fresh_counts": [len(record["fresh"]) for record in records]})
        current = following
    return {"removed_name": removed, "removed_original_label": e, "port_multiplicity": multiplicity,
            "start": raw, "start_audit": origin, "stages": stages, "rounds": rounds}


def changing_capacity_history(core, names, middle, hubs, phi, depth, grow1):
    from networkx import DiGraph, minimum_cut

    e = names[0, 1, 0]
    _, s, t = core[e]
    n = max(hubs) + 1
    u, v, a, b, c, z, outside = range(n, n + 7)
    branch_edges = [(s, u), (s, v), (u, a), (u, b), (v, a), (v, c), (b, c),
                    (a, outside), (a, outside), (b, outside), (c, outside),
                    (t, z), (t, z), (z, outside), (z, outside)]
    added = [(x, *uv) for x, uv in enumerate(branch_edges, len(core))]
    bare = [edge for edge in core if edge[0] != e]
    core_names = {x for x, _, _ in bare}
    raw = rows_from_edges([*bare, *added])[:-1]
    stage = Arrangement.parse(raw)
    audit = start_audit(stage)
    assert audit["census_open_legal"]
    trace = []
    additions = []
    for age in range(depth + 1):
        ends, _, _ = stage.holder_graph()
        graph = DiGraph()
        for x in stage.labels:
            if x in core_names:
                continue
            p, q = ends[x]
            capacity = graph.get_edge_data(p, q, {}).get("capacity", 0) + 1
            graph.add_edge(p, q, capacity=capacity)
            graph.add_edge(q, p, capacity=capacity)
        value, (left, right) = minimum_cut(graph, s, t)
        crossing = sorted(x for x, (p, q) in ends.items()
                          if x not in core_names and (p in left) != (q in left))
        assert int(value) == len(crossing) == (2 if age < 2 else 1)
        trace.append({"age": age, "junctions": len(stage.stars), "distinctions": len(stage.labels),
                      "exterior_minimum": int(value), "minimum_exterior_cut": crossing,
                      **check_marking(stage, core_names, phi, names, middle, hubs, (s, t), n)})
        if age == depth:
            break
        next_stage = Arrangement.parse([sorted(row) for row in grow1(stage.stars)])
        records = round_replay(stage, next_stage)
        assert all(record["fresh"] and not record["implied"] for record in records)
        additions.append([sorted(row) for row in next_stage.stars[len(stage.stars):]])
        stage = next_stage
    return {"removed_name": (0, 1, 0), "start": raw, "start_audit": audit, "stages": trace, "round_additions": additions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--depth", type=int, default=12)
    args = parser.parse_args()
    assert args.depth >= 1
    sys.path.insert(0, str(ROOT / "experiments" / EXTEND_ROUND))
    from extend import grow1

    core, names, middle, hubs, phi = original()
    family = [((0, 1, 0), 1), ((0, 1, 1), 1), ((4, 5, 4), 1), ((8, 9, 9), 1), ((0, 1, 0), 2)]
    results = [history(core, names, middle, hubs, phi, e, r, args.depth, grow1) for e, r in family]
    changing = changing_capacity_history(core, names, middle, hubs, phi, args.depth, grow1)
    archived = ROOT / "artifacts" / OLD_GRAFT / "graft_check.json"
    baseline = json.loads(archived.read_text())["dense"]
    assert results[0]["start"] == baseline["start"]
    paired = zip(results[0]["stages"], baseline["marked_checks"])
    assert all((a["junctions"], a["distinctions"]) == (b["ordinary_junctions"], b["distinctions"]) for a, b in paired)
    print(json.dumps({"depth": args.depth, "families": results,
                      "changing_capacity": changing,
                      "baseline_replayed": str(archived.relative_to(ROOT)),
                      "pair_and_triple_readings": "all ages by the capacity-matched substitution proof"},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
