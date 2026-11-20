"""Anonymous local arrival rules and exact controls for physical and bond nearness."""

import argparse
import hashlib
import itertools
import json
import random
from collections import Counter, defaultdict, deque

from motion_stage import INPUTS, STAGES, MotionStage, load_case_record


def co_knotted_pairs(stars):
    near = defaultdict(set)
    for star in stars:
        for bit in star:
            near[bit].update(set(star) - {bit})
    return dict(near)


def distances(graph, start, omitted=None, cap=None):
    seen = {start: 0}
    queue = deque([start])
    while queue:
        v = queue.popleft()
        if seen[v] == cap:
            continue
        for w in graph[v]:
            if w != omitted and w not in seen:
                seen[w] = seen[v] + 1
                queue.append(w)
    return seen


def return_legs(graph, v):
    near = graph[v]
    within = set().union(near, *(graph[w] for w in near)) - {v}
    local = {w: graph[w] & within for w in within}
    return {w: bool((set(distances(local, w, cap=3)) & near) - {w}) for w in near}


def matching_exits(graph, legs, incoming):
    p, v = incoming
    exits = graph[v] - {p}
    if len(graph[v]) <= 2:
        return exits
    return {w for w in exits if legs[v][w] == legs[v][p]}


class ReturnRule:
    """All production data are inferred from unweighted co-knotted pairs."""

    def __init__(self, near):
        closed = {bit: row | {bit} for bit, row in near.items()}
        supports = {tuple(sorted(closed[a] & closed[b]))
                    for a, row in near.items() for b in row if a < b}
        self.stars = tuple(sorted(supports))
        if not all(len(row) >= 3 for row in self.stars) or co_knotted_pairs(self.stars) != near:
            raise ValueError("co-knotted pairs failed the triangle-free holder reconstruction")
        self.stage = MotionStage(self.stars)
        self.source = set()
        for v, row in enumerate(self.stars):
            support = set(row)
            if all(closed[bit] - support for bit in row):
                self.source.add(v)
        self.full = {v: set(row) - {self.stage.outside} for v, row in enumerate(self.stage.bundles[:-1])}
        if any(len(self.stage.bundles[v][w]) != 1 or self.full[v] & self.full[w]
               for v in self.full for w in self.full[v]):
            raise ValueError("ordinary holder meetings must be simple and triangle-free")
        self.graph = {v: self.full[v] & self.source for v in self.source}
        self.legs = {v: return_legs(self.graph, v) for v in self.source}

    def exits(self, incoming):
        return matching_exits(self.graph, self.legs, incoming)

    def packet(self, triple):
        u, v, w = triple
        children = (self.full[u] & self.full[w]) - self.source
        if len(children) != 1:
            raise ValueError("a raw turn must have exactly one common first child")
        child, = children
        meetings = self.stage.bundles
        return frozenset(meetings[a][b][0] for a, b in ((u, v), (v, w), (w, child), (child, u)))


def deterministic_orbit(start, choices):
    visited = {}
    triples = []
    state = start
    while state not in visited:
        visited[state] = len(triples)
        leaves = choices(state)
        if len(leaves) != 1:
            return triples, state, "stop" if not leaves else "tie", None
        w, = leaves
        u, v = state
        triples.append((u, v, w))
        state = (v, w)
    return triples, state, "repeat", visited[state]


def ordinary_exits(graph, incoming, policy="all"):
    u, v = incoming
    exits = graph[v] - {u}
    if not exits and policy == "reflect":
        return {u}
    if exits and policy == "degree":
        gap = min(abs(len(graph[w]) - len(graph[u])) for w in exits)
        return {w for w in exits if abs(len(graph[w]) - len(graph[u])) == gap}
    return exits


def event_closure(seeds, exits, order):
    pending = deque(sorted(seeds))
    known = set(seeds)
    while pending:
        event = pending.popleft() if order == "queue" else pending.pop()
        _, v = event
        successors = {(v, w) for w in exits(event)} - known
        known.update(successors)
        pending.extend(sorted(successors, reverse=order == "reverse"))
    return known


def checked_closure(seeds, exits):
    known = event_closure(seeds, exits, "queue")
    for order in ("stack", "reverse"):
        if known != event_closure(seeds, exits, order):
            raise AssertionError("fair worklists disagree on arrival closure")
    return known


def ranked_events(graph, seeds, exits, horizon):
    front = set(seeds)
    arrivals = [sorted(front)]
    mergers = []
    roots = {v for _, v in front}
    rulers = [distances(graph, v) for v in roots]
    for depth in range(1, horizon + 1):
        incoming = Counter((v, w) for u, v in front for w in exits((u, v)))
        front = set(incoming)
        mergers.extend({"depth": depth, "arrival": event, "predecessors": count}
                       for event, count in sorted(incoming.items()) if count > 1)
        if any(min((row.get(w, float("inf")) for row in rulers), default=float("inf")) > depth
               for _, w in front):
            raise AssertionError("causal depth failed to bound physical reach")
        arrivals.append(sorted(front))
    return {"arrivals": arrivals, "frontiers": [sorted({v for _, v in row}) for row in arrivals],
            "coalescences": mergers}


def undirected_graph(links):
    graph = defaultdict(set)
    for i, j in links:
        graph[i].add(j)
        graph[j].add(i)
    return dict(graph)


def arrival_controls():
    line = undirected_graph([(0, 1), (1, 2), (2, 3), (3, 4)])
    asym = undirected_graph([(0, 1), (1, 2), (2, 3), (3, 4), (2, 5)])
    sym = undirected_graph([(0, 1), (1, 2), (2, 3), (3, 4), (2, 5), (5, 6)])
    diamond = undirected_graph([(0, 1), (1, 2), (1, 3), (2, 4), (3, 4), (4, 5)])
    cases = (
        ("directed_line", line, {(0, 1)}, "all"),
        ("one_unmarked_location", line, {(2, w) for w in line[2]}, "all"),
        ("explicit_end_reflection", line, {(0, 1)}, "reflect"),
        ("asymmetric_fork_all", asym, {(1, 2)}, "all"),
        ("degree_continuity_asymmetric_fork", asym, {(1, 2)}, "degree"),
        ("degree_continuity_symmetric_fork", sym, {(1, 2)}, "degree"),
        ("reconvergent_fork", diamond, {(0, 1)}, "all"),
    )
    out = {}
    for name, graph, seeds, policy in cases:
        def exits(event):
            return ordinary_exits(graph, event, policy)
        visited = checked_closure(seeds, exits)
        out[name] = ranked_events(graph, seeds, exits, 8) | {
            "closure": sorted(visited), "wake_locations": sorted({v for _, v in visited}),
            "policy": policy, "physical_links": sorted((u, v) for u in graph for v in graph[u] if u < v),
        }
    assert out["directed_line"]["frontiers"][:5] == [[1], [2], [3], [4], []]
    assert out["explicit_end_reflection"]["frontiers"][:9] == [[1], [2], [3], [4], [3], [2], [1], [0], [1]]
    assert out["degree_continuity_asymmetric_fork"]["frontiers"][1] == [3]
    assert out["degree_continuity_symmetric_fork"]["frontiers"][1] == [3, 5]
    assert {"depth": 3, "arrival": (4, 5), "predecessors": 2} in out["reconvergent_fork"]["coalescences"]
    legs = {v: return_legs(sym, v) for v in sym}
    assert matching_exits(sym, legs, (1, 2)) == {3, 5}
    out["symmetric_no_return_stop"] = {"incoming": [1, 2], "eligible": [3, 5],
                                       "outcome": "tie", "return_legs": legs[2]}
    return out


def recoding_check(near, rule, packets, case_number):
    labels = sorted(near)
    renamed = list(range(1000, 1000 + len(labels)))
    random.Random(20261119 + case_number).shuffle(renamed)
    recode = dict(zip(labels, renamed, strict=True))
    reversed_code = {new: old for old, new in recode.items()}
    renear = {recode[bit]: {recode[x] for x in row} for bit, row in near.items()}
    other = ReturnRule(renear)
    index = {tuple(sorted(reversed_code[bit] for bit in row)): i for i, row in enumerate(other.stars)}
    permutation = {i: index[row] for i, row in enumerate(rule.stars)}
    assert {permutation[v] for v in rule.source} == other.source
    for holder, adjacent in rule.graph.items():
        assert {permutation[w] for w in adjacent} == other.graph[permutation[holder]]
        assert {permutation[w]: bit for w, bit in rule.legs[holder].items()} == other.legs[permutation[holder]]
        for previous in adjacent:
            pair = (previous, holder)
            moved = (permutation[previous], permutation[holder])
            assert {permutation[w] for w in rule.exits(pair)} == other.exits(moved)
    for triple, quad in packets.items():
        recoded = other.packet(tuple(permutation[v] for v in triple))
        assert quad == frozenset(reversed_code[bit] for bit in recoded)


def grade_routes(roles, rule, evaluator, judge, orbits, packets):
    def score(kind, raw_path, anchors):
        points = [evaluator[v] for v in raw_path]
        a, b = points[:2]
        triples, end, reason, repeat = orbits[a, b]
        centers = [judge[v] for _, v, _ in triples]
        rulers = [distances(rule.full, evaluator[v]) for v in anchors]
        phases = [{"source_triple": [judge[v] for v in (u, v, w)],
                   "visible_support": sorted(packets[u, v, w]),
                   "marked_incoming_distinction": rule.stage.bundles[u][v][0],
                   "source_holder_arities": [len(rule.stars[x]) for x in (u, v, w)]}
                  for u, v, w in triples]
        return {"kind": kind, "launch": [judge[a], judge[b]],
                "stops_at": [judge[v] for v in end], "outcome": reason,
                "centers": centers, "repeat_index": repeat, "landmarks": anchors,
                "steps_to_landmarks": [[dist[evaluator[v]] for dist in rulers] for v in centers],
                "seams_crossed": [v for v in centers if v in roles["seams"]],
                "phases": phases, "distinct_visible_supports": len({packets[t] for t in triples}),
                "translations_before_stop_or_return": len(triples) if repeat is not None
                                                      else max(0, len(triples) - 1),
                "closed_period": len(triples) - repeat if repeat is not None else None,
                "matched_route": (centers == raw_path[1:-1] and reason == "stop") if kind == "path"
                                 else (set(centers) == set(raw_path) and len(centers) == len(raw_path)
                                       and repeat == 0)}
    rows = []
    path = roles["background"]
    if path:
        rows.extend(score("path", p, (path[0], path[-1])) for p in (path, path[::-1]))
    for ring in roles["rings"]:
        rows.extend(score("ring", p, ring[:2]) for p in (ring, ring[:1] + ring[:0:-1]))
    return rows


def score_case(case, row, case_number):
    near = co_knotted_pairs(row["stages"]["1"]["stars"])
    rule = ReturnRule(near)
    actual = {tuple(sorted(star)): i for i, star in enumerate(row["stages"]["1"]["stars"])}
    judge = {i: actual[star] for i, star in enumerate(rule.stars)}
    evaluator = {old: new for new, old in judge.items()}
    frozen = row["input"]
    assert set(rule.stars) == set(actual)
    assert {judge[v] for v in rule.source} == set(range(len(frozen["sizes"])))
    assert {frozenset((judge[u], judge[v])) for u in rule.graph for v in rule.graph[u]} == {
        frozenset(link) for link in frozen["meetings"]
    }
    packets = {(u, v, w): rule.packet((u, v, w)) for v, neighbors in rule.graph.items()
               for u in neighbors for w in neighbors - {u}}
    recoding_check(near, rule, packets, case_number)
    handoffs = 0
    support_reach = Counter()
    support_shift = Counter()
    packet_rulers = {}
    for triple, quad in packets.items():
        u, v, w = triple
        assert quad == packets[w, v, u]
        assert len(quad) == 4 and rule.stage.allowed_change(quad)
        for a, b in ((u, v), (v, w)):
            original = rule.stage.bundles[a][b][0]
            minimum = rule.stage.minimum_response(original, pinned_loose=False)
            assert minimum.minimum_size == 4 and quad in minimum.supports
        choices = rule.exits((v, w))
        if len(choices) == 1:
            z, = choices
            following = packets[v, w, z]
            assert len(quad & following) == 1
            assert len(quad ^ following) == 6 and rule.stage.allowed_change(quad ^ following)
            common, = quad & following
            local = distances(near, common, cap=2)
            reach = max(local[bit] for bit in quad | following)
            for packet in (quad, following):
                if packet not in packet_rulers:
                    packet_rulers[packet] = rule.stage.distances_from(packet)
            change = max(max(packet_rulers[quad][bit] for bit in following),
                         max(packet_rulers[following][bit] for bit in quad))
            assert reach <= 2 and change <= 2
            support_reach[reach] += 1
            support_shift[change] += 1
            handoffs += 1
    arcs = sorted((u, v) for u in rule.graph for v in rule.graph[u])
    orbits = {arc: deterministic_orbit(arc, rule.exits) for arc in arcs}
    outcomes = Counter()
    wave_counts = Counter()
    launches = []
    for arc, (triples, last, reason, repeat) in orbits.items():
        outcomes[reason] += 1
        visited = checked_closure({arc}, lambda event: ordinary_exits(rule.graph, event))
        wave_count = len(visited)
        wave_counts[wave_count] += 1
        launches.append({"seed": [judge[v] for v in arc], "reason": reason,
                         "terminal_or_repeat": [judge[v] for v in last], "quad_centers": len(triples),
                         "cycle_length": len(triples) - repeat if repeat is not None else None,
                         "all_exit_arrivals": wave_count,
                         "all_exit_forks": sum(len(ordinary_exits(rule.graph, event)) > 1 for event in visited)})
    all_ports = {judge[v]: {judge[w]: bit for w, bit in exits.items()} for v, exits in rule.legs.items()}
    junction_modes = {judge[v]: {
        str(judge[p]): {"return": sorted(judge[w] for w in rule.exits((p, v))),
                        "degree": sorted(judge[w] for w in ordinary_exits(rule.graph, (p, v), "degree")),
                        "all": sorted(judge[w] for w in ordinary_exits(rule.graph, (p, v)))}
        for p in rule.graph[v]} for v in rule.source if len(rule.graph[v]) >= 3}
    seam_positions = set(frozen["roles"]["seams"])
    assert seam_positions <= junction_modes.keys()
    return {"case": case, "junctions": len(rule.stars), "distinctions": len(near),
            "recovered_source_junctions": len(rule.source), "all_launches": len(arcs), "launches": launches,
            "deterministic_outcomes": outcomes, "all_exit_size_histogram": wave_counts,
            "distinct_minimum_quads": len(set(packets.values())), "checked_raw_handoffs": handoffs,
            "distinction_step_reach_from_common_port": support_reach,
            "distinction_step_hausdorff_change": support_shift,
            "anonymous_recoding_verified": True, "return_bits": all_ports, "branch_choices": junction_modes,
            "landmark_routes": grade_routes(frozen["roles"], rule, evaluator, judge, orbits, packets)}


def bond_codes(matrix):
    n = len(matrix)
    nearest = set()
    for i, row in enumerate(matrix):
        finite = {j: d for j, d in enumerate(row) if i != j and isinstance(d, int)}
        floor = min(finite.values(), default=None)
        nearest.update((i, j) for j, d in finite.items() if d == floor)

    weights = {(i, j): matrix[i][j] - 1 for i, j in itertools.combinations(range(n), 2)
               if isinstance(matrix[i][j], int)}
    pair_weights = weights | {(j, i): d for (i, j), d in weights.items()}
    atomic = set()
    forest = set()
    seen_weight = defaultdict(list)
    triangle_failures = 0
    for (i, j), d in weights.items():
        via = [pair_weights[i, k] + pair_weights[k, j] for k in range(n)
               if (i, k) in pair_weights and (k, j) in pair_weights]
        if d not in via:
            atomic.add((i, j))
        triangle_failures += sum(length < d for length in via)
        seen_weight[d].append((i, j))
    lighter = {i: set() for i in range(n)}
    for _, group in sorted(seen_weight.items()):
        forest.update((i, j) for i, j in group if j not in distances(lighter, i))
        for i, j in group:
            lighter[i].add(j)
            lighter[j].add(i)

    def directed(links):
        return links | {(j, i) for i, j in links}
    return {"nearest_ties": nearest, "additive_indivisibility_of_d_minus_one": directed(atomic),
            "minimum_spanning_forest_union": directed(forest)}, triangle_failures


def grade_bond_input(path=STAGES.with_name("bond_profiles.json")):
    raw = path.read_bytes()
    profile = json.loads(raw)
    rows = []
    witnesses = []
    for row in profile["records"]:
        if not row["path"] or row["age"] > 1:
            continue
        matrix = [p["path_bond_distances"] for p in row["path"]]
        case, age = row["case"], row["age"]
        missing = sum(isinstance(d, str) and d != "infinite" for i, line in enumerate(matrix) for d in line[i+1:])
        if missing:
            rows.append({"case": case, "age": age, "status": "censored", "unknown_pairs": missing})
            continue
        marks = [p["name"] for p in row["path"]]
        stage = load_case_record(case)["stages"][str(age)]
        near = co_knotted_pairs(stage["stars"])
        actual = {(i, j) for i, p in enumerate(marks) for j, q in enumerate(marks) if q in near[p]}
        rules, triangle_failures = bond_codes(matrix)
        rows.append({"case": case, "age": age, "status": "exact", "marks": len(marks),
                     "physical_arcs": sorted(actual), "d_minus_one_triangle_failures": triangle_failures,
                     "reconstructions": {name: {"missing": sorted(actual - found),
                                                 "added": sorted(found - actual)}
                                         for name, found in rules.items()}})
        if age == 0:
            assert rules["additive_indivisibility_of_d_minus_one"] == actual
            assert rules["minimum_spanning_forest_union"] == actual
        d2 = defaultdict(list)
        for i, j in itertools.permutations(range(len(marks)), 2):
            d2[matrix[i][j]].append(((i, j), (i, j) in actual))
        if any(any(status for _, status in pairs) and any(not status for _, status in pairs) for pairs in d2.values()):
            if not witnesses:
                value, pairs = next((v, pairs) for v, pairs in d2.items()
                                    if {status for _, status in pairs} == {True, False})
                witnesses.append({"case": case, "age": age, "equal_bond_distance": value,
                                  "physical_neighbours": next(pair for pair, status in pairs if status),
                                  "physical_non_neighbours": next(pair for pair, status in pairs if not status)})
    return {"restricted_exact_tables": rows, "scalar_tie_example": witnesses,
            "archive_sha256": hashlib.sha256(raw).hexdigest()}


def bond_obstruction():
    # Each bundle has two literal shared distinctions. No loose marks are supplied.
    groups = [frozenset((2*i, 2*i+1)) for i in range(4)]
    stars = [groups[i-1] | groups[i] for i in range(4)]
    near = co_knotted_pairs(stars)
    allowed = [x for x in range(256) if all(sum((x >> bit) & 1 for bit in star) % 2 == 0 for star in stars)]
    free = [len({x & mask for x in allowed}) == 1 << mask.bit_count() for mask in range(256)]
    bonds = [[i for i in range(8) if mask & (1 << i)] for mask in range(1, 256)
             if not free[mask] and all(free[mask ^ (1 << i)] for i in range(8) if mask & (1 << i))]
    expected = [sorted(a | b) for a, b in itertools.combinations(groups, 2)]
    assert sorted(bonds) == sorted(expected)
    matrix = [[0 if i == j else min(len(bond) - 1 for bond in bonds if i in bond and j in bond)
               for j in range(8)] for i in range(8)]
    # Fix (6, 0) and exchange a valid exit at 2 with a non-neighbour at 4.
    swap = {i: (4 if i == 2 else 2 if i == 4 else i) for i in range(8)}
    assert all(matrix[i][j] == matrix[swap[i]][swap[j]] for i in range(8) for j in range(8))
    assert 0 in near[6] and 2 in near[0] and 4 not in near[0]
    return {"supports": [sorted(star) for star in stars], "all_held_twice": True,
            "allowed_states": len(allowed), "minimal_nonfree_sets": bonds, "complete_bond_table": matrix,
            "directed_input": [6, 0], "exchanged_exit_and_non_exit": [2, 4]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", help="run one literal case for a focused replay")
    args = parser.parse_args()
    document = json.loads(INPUTS.read_text())
    digest = hashlib.sha256(STAGES.read_bytes()).hexdigest()
    if digest != document["archive_sha256"]:
        raise ValueError("literal EDDY archive differs from the frozen predecessor")
    names = [row["id"] for row in document["cases"]]
    if len(names) != len(set(names)):
        raise ValueError("frozen motion inputs contain duplicate case identities")
    if args.case and args.case not in names:
        parser.error(f"unknown case {args.case}")
    controls = arrival_controls() | {"same_bond_table_obstruction": bond_obstruction()}
    cases = [score_case(name, load_case_record(name), i) for i, name in enumerate(names)
             if not args.case or name == args.case]
    print(json.dumps({"archive_sha256": digest, "fixed_age": 1, "controls": controls,
                      "bond_nearness": grade_bond_input(), "cases": cases}, indent=2))


if __name__ == "__main__":
    main()
