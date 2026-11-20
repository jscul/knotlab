"""Compare exact step observations and bond decisions under two named weightings."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
import json
import math
from pathlib import Path
from random import Random
import resource
import sys

import networkx as nx

from bond_checks import (SMALL_KNOT_LIMIT, check_projections, incidence,
                         loose_bond_tightness, mask, parity_implied, small_bond_table)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ID = "BOND-CLOSURE-20261120-001"
DESIGN = ROOT / "research" / ID / "preregistration.md"
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "sample.json"
FEEDBACK = "STATE-FEEDS-GROWTH-20261119-001"
sys.path.insert(0, str(ROOT / "experiments" / FEEDBACK / (FEEDBACK + "-E001_feedback")))
import growth  # noqa: E402


TREE_SEED = 202611201451
ROUTE_SEED = 202611201463
ARM_SEED = 202611201464
N = 128
CAPS = {"junctions": 2048, "distinctions": 8192}
MEMORY_LIMIT = 6 * 1024**3
SMALL_FRAME_BUDGET = 32


def material(n, meetings, open_counts):
    stars = [[] for _ in range(n)]
    for d, (v, w) in enumerate(meetings):
        stars[v].append(d)
        stars[w].append(d)
    last = len(meetings)
    for star, open_count in zip(stars, open_counts, strict=True):
        star.extend(range(last, last + open_count))
        last += open_count
    return tuple(map(tuple, stars))


def trees():
    rng = Random(TREE_SEED)
    for n in range(4, 9):
        for number in range(N):
            word = [rng.randrange(n) for _ in range(n - 2)]
            tree = nx.from_prufer_sequence(word)
            meetings = sorted(tuple(sorted(e)) for e in tree.edges)
            surplus = [int(rng.random() < 0.25) for v in range(n)]
            opens = [max(0, 3 - tree.degree(v)) + surplus[v] for v in range(n)]
            yield f"n{n}/{number:03}", {"prufer_word": word, "open_counts": opens,
                                         "surplus": surplus, "meetings": meetings}, material(n, meetings, opens)


def routes():
    rng, coin = Random(ROUTE_SEED), Random(ARM_SEED)
    for number in range(N):
        lengths = [rng.randint(4, 8) for _ in range(3)]
        meetings, interiors, rail_records = [], [], []
        total = 2
        for length in lengths:
            within = list(range(total, total + length - 1))
            interiors.append(within)
            total += length - 1
            path = [0, *within, 1]
            multiplicity = [rng.randint(1, 2) if x in (0, length - 1) else rng.randint(2, 3)
                            for x in range(length)]
            rail_records.append({"holders": path, "multiplicity": multiplicity})
            for u, v, reps in zip(path[:-1], path[1:], multiplicity, strict=True):
                meetings.extend([tuple(sorted((u, v)))] * reps)
        near = [inner[0] for inner in interiors]
        ear = None
        if rng.random() < 0.5:
            choices = [(v, w) for i, j in combinations(range(3), 2)
                       for v in interiors[i][1:] for w in interiors[j][1:]]
            a, b = rng.choice(choices)
            length = rng.randint(2, 4)
            path = [a, *range(total, total + length - 1), b]
            total += length - 1
            ear = {"path_holders": path, "multiplicity": 2}
            for u, v in zip(path, path[1:]):
                meetings.extend([tuple(sorted((u, v)))] * 2)
        opens = [2 * (v in near) for v in range(total)]
        stars = [material(total, meetings, [o + int(v == 1) * extra for v, o in enumerate(opens)])
                 for extra in (0, 1)]
        yield f"route/{number:03}", {"lengths": lengths, "rails": rail_records, "ear": ear,
                                      "near": near, "far": 1, "meetings": meetings,
                                      "fair_arm": coin.randrange(2)}, stars


def lawful(stars):
    held, _ = incidence(stars)
    wired = nx.Graph()
    wired.add_nodes_from(range(len(stars) + 1))
    outside = len(stars)
    for row in held.values():
        a, b = tuple(row) if len(row) == 2 else (row[0], outside)
        wired.add_edge(a, b)
    ordinary_connected = len(stars) >= 1 and nx.is_connected(wired.subgraph(range(len(stars))))
    failed = [v for v in range(len(stars))
              if len(stars[v]) < 3 or not nx.is_connected(wired.subgraph(set(wired) - {v}))]
    if failed or not ordinary_connected:
        return {"lawful": False, "failed_knots": failed, "ordinary_connected": ordinary_connected}
    return {"lawful": True, "projection_rank": check_projections(stars)}


def observed_component(stars, parents, live):
    held, ordinary = incidence(stars)
    live = set(live)
    blocks = sorted({frozenset(row & live) for row in ordinary if row & live}, key=lambda b: (-len(b), sorted(b)))
    maximal = []
    for b in blocks:
        if not any(b <= x for x in maximal):
            maximal.append(b)
    lookup = defaultdict(list)
    for block in maximal:
        for v in block:
            lookup[v].append(block)
    seen = set(parents[:1])
    waiting = list(seen)
    for v in waiting:
        for block in lookup[v]:
            unread = block - seen
            seen.update(unread)
            waiting.extend(sorted(unread))
    assert set(parents) <= seen
    by_order = sorted(seen)
    translate = {v: j for j, v in enumerate(by_order)}
    # Keep live counts from the actual physical incidence, not from witness counts.
    open_counts = Counter(row[0] for row in held.values() if len(row) == 1)
    nodes = [(int(v in parents), open_counts[v]) for v in by_order]
    shows = sorted(tuple(sorted(translate[v] for v in b)) for b in maximal if b <= seen)
    return tuple(nodes), tuple(shows)


def witness_graph(observation):
    colors, blocks = observation
    graph = nx.Graph()
    graph.add_nodes_from((v, {"color": (0, marked, degree)}) for v, (marked, degree) in enumerate(colors))
    for w, block in enumerate(blocks, len(colors)):
        graph.add_node(w, color=(1, 0, 0))
        graph.add_edges_from((w, v) for v in block)
    return graph


class Observations:
    """Bucket by invariants, and merge only after checking a literal isomorphism."""

    def __init__(self):
        self.buckets = defaultdict(list)
        self.literal = {}
        self.types = {}

    def add(self, shape):
        if shape in self.literal:
            return self.literal[shape]
        graph = witness_graph(shape)
        key = tuple(sorted(Counter((row["color"], graph.degree(v)) for v, row in graph.nodes(data=True)).items()))
        for type_id, other in self.buckets[key]:
            matcher = nx.algorithms.isomorphism.GraphMatcher(
                graph, other, node_match=lambda a, b: a["color"] == b["color"])
            if matcher.is_isomorphic():
                f = matcher.mapping
                assert len(f) == len(graph) == len(set(f.values()))
                assert all(graph.nodes[v] == other.nodes[f[v]]
                           and {f[w] for w in graph[v]} == set(other[f[v]]) for v in graph)
                self.literal[shape] = type_id
                return type_id
        type_id = str(len(self.types))
        self.types[type_id] = shape
        self.buckets[key].append((type_id, graph))
        self.literal[shape] = type_id
        return type_id


def bridge_supports(stars):
    """All physical size-three cuts containing at least two loose distinctions."""
    held, _ = incidence(stars)
    graph = nx.Graph()
    graph.add_nodes_from(range(len(stars)))
    shared = defaultdict(list)
    loose = defaultdict(set)
    for d, ends in held.items():
        if len(ends) == 2:
            shared[tuple(sorted(ends))].append(d)
        else:
            loose[ends[0]].add(d)
    graph.add_edges_from(shared)
    assert nx.is_connected(graph)
    all_loose = set().union(*loose.values())
    cuts = {}
    if len(all_loose) == 3:
        cut = tuple(sorted(all_loose))
        cuts.update({pair: cut for pair in combinations(cut, 2)})
    # Both induced shores are connected in each bridge case: the side
    # containing the exterior has at least one other loose distinction.
    for a, b in list(nx.bridges(graph)):
        names = shared[tuple(sorted((a, b)))]
        if len(names) != 1:
            continue
        graph.remove_edge(a, b)
        left = nx.node_connected_component(graph, a)
        graph.add_edge(a, b)
        left_loose = set().union(*(loose[v] for v in left))
        assert len(all_loose) >= 3
        for side in (left_loose, all_loose - left_loose):
            if len(side) == 2:
                key = tuple(sorted(side))
                cuts[key] = tuple(sorted([*key, names[0]]))
    return cuts


class CrossCheck:
    def __init__(self):
        self.frames = set()
        self.rows = []
        self.permuted = False

    def verify(self, trial, age, stars, marks, closure, pair_tests, observations, shape, group):
        if len(stars) <= SMALL_KNOT_LIMIT and stars not in self.frames and len(self.frames) < SMALL_FRAME_BUDGET:
            self.frames.add(stars)
            exact = small_bond_table(stars, marks)
            assert (exact[tuple(sorted(marks))] == 3) == closure
            assert all(exact[p] is not None and (exact[p] == 3) == prediction for p, prediction in pair_tests)
            self.rows.append({"draw": trial, "age": age, "knots": len(stars), "marks": marks,
                              "exact_sizes": [[q, size] for q, size in exact.items()]})
        if not self.permuted:
            rng = Random(202611201474)
            knots = list(range(len(stars)))
            rng.shuffle(knots)
            translate = {v: index for index, v in enumerate(knots)}
            d = sorted(set(k for row in stars for k in row))
            news = d[:]
            rng.shuffle(news)
            rename = dict(zip(d, news, strict=True))
            recoded = tuple(tuple(rename[x] for x in stars[v]) for v in knots)
            ren_marks = tuple(rename[x] for x in marks)
            candidate = bridge_supports(recoded)
            assert all((tuple(sorted(rename[x] for x in p)) in candidate) == pred for p, pred in pair_tests)
            assert loose_bond_tightness(recoded, ren_marks) == closure
            _, adjacency = incidence(recoded)
            actual_live = set(translate[v] for v in growth._index(stars).loose)
            assert set(growth._index(recoded).loose) == actual_live and nx.is_connected(nx.Graph(
                [(u, v) for u, row in enumerate(adjacency) for v in row]))
            moved = observed_component(recoded, tuple(translate[v] for v in group), actual_live)
            assert observations.add(moved) == observations.add(shape)
            self.permuted = True


def step(stars, trial, age, compare, audit):
    plan = growth.plan_round(stars, (), growth.ORDINARY, caps=CAPS)
    groups = [tuple(row["parents"]) for row in plan.details.get("candidate_groups", ()) if len(row["parents"]) == 3]
    obs = {"age": age, "knots": len(stars), "distinctions": len(plan.stage.names),
           "live": len(plan.stage.loose), "status": plan.status, "prospective_ternaries": groups,
           "scored": []}
    if plan.status != "extend":
        obs.update({k: v for k, v in plan.details.items() if k == "shortages" or k.startswith("planned_")})
        if plan.status == "arity_stop":
            arity = plan.details["implied_arity"]
            assert arity == 2
            obs.update({"archived_exception_closes": True, "without_archived_exception": "arity_stop",
                        "implied_arity": arity})
        return None, obs
    physical_allocations = growth.literal_allocation(plan)
    frame = growth.realize_round(plan, allocation=physical_allocations)
    triples = [(birth, marks) for birth, marks in zip(plan.births, physical_allocations, strict=True)
               if len(birth.parents) == 3]
    assert {b.parents for b, _ in triples} == set(groups) and len(triples) == len(groups)
    if not triples:
        return tuple(frame["stars"]), obs
    bridges = bridge_supports(stars)
    loose = {d for row in plan.stage.loose.values() for d in row}
    parity_rows = tuple(map(mask, stars))
    for birth, marks in triples:
        marks = tuple(sorted(marks))
        actual = birth.fresh == 0
        exhaust = set(marks) == loose
        implied = parity_implied(parity_rows, mask(marks))
        closes = not frame["live"]
        tight = loose_bond_tightness(stars, marks)
        assert len(marks) == 3
        shape = observed_component(stars, birth.parents, plan.stage.loose)
        local_exhaustion = shape[0] == ((1, 1),) * 3
        assert not actual or local_exhaustion
        if local_exhaustion:
            # Every marking of a single root within this full component is
            # isomorphic, since all three independent pair witnesses occur.
            assert shape[1] == ((0, 1), (0, 2), (1, 2))
        pair_tests = [(q, q in bridges) for q in combinations(marks, 2)]
        audit.verify(trial, age, stars, marks, tight, pair_tests, compare, shape, birth.parents)
        obs["scored"].append({"parents": birth.parents, "marked_loose_distinctions": marks,
                              "allocated_marks_equivalent_choices": math.prod(len(plan.stage.loose[v]) for v in birth.parents),
                              "fresh_count": birth.fresh, "exhausts": exhaust, "implied": implied,
                              "fresh_zero": actual,
                              "closes": closes, "triple_bond_size_three": tight,
                              "pair_bond_size_three": pair_tests,
                              "physical_size_three_witnesses": [[p, bridges[p]] for p, yes in pair_tests if yes],
                              "local_exhaustion": local_exhaustion, "step_type": compare.add(shape)})
    return tuple(frame["stars"]), obs


def tree_trace(stars, key, compare, audit):
    gate = lawful(stars)
    if not gate["lawful"]:
        return {"lawfulness": gate, "outcome": "nonlawful", "stages": []}
    reached = []
    outcome = "scheduled horizon"
    for age in range(4):
        successor, row = step(stars, key, age, compare, audit)
        reached.append(row)
        if successor is None:
            outcome = "closed by archived two-input exception" if row.get("archived_exception_closes") else row["status"]
            break
        if not growth._index(successor).loose:
            outcome = "closed"
            break
        stars = successor
    return {"lawfulness": gate, "outcome": outcome, "stages": reached}


def audit_route(spec, key, starts, compare, audit):
    result = []
    for i, stars in enumerate(starts):
        gate = lawful(stars)
        if not gate["lawful"]:
            result.append({"lawfulness": gate, "outcome": "nonlawful", "stages": []})
            continue
        here = f"{key}/{i}"
        first, layer_zero = step(stars, here, 0, compare, audit)
        trace = [layer_zero]
        item = {"lawfulness": gate, "outcome": layer_zero["status"], "stages": trace}
        result.append(item)
        if first is None:
            continue
        source_live = set(growth._index(stars).loose)
        expected_live = set(spec["near"]) | ({spec["far"]} if i else set())
        assert source_live == expected_live
        _, near = incidence(stars)
        witnesses = {(a, b): sorted(near[a] & near[b]) for a, b in combinations(sorted(source_live), 2)
                     if near[a] & near[b]}
        assert witnesses == {p: [0] for p in combinations(sorted(spec["near"]), 2)}
        item["source_binary_witnesses"] = [[pair, support] for pair, support in witnesses.items()]
        next_stage, layer_one = step(first, here, 1, compare, audit)
        trace.append(layer_one)
        if next_stage is None:
            item["outcome"] = layer_one["status"]
            continue
        assert not layer_zero["prospective_ternaries"]
        picked, = layer_one["scored"]
        assert picked["fresh_count"] == i
        item["outcome"] = "closes at layer two" if picked["closes"] else "continues at layer two"
        # The continuing cut consists of the three marked loose inputs and the
        # one shared input of the remote unary child. Both sides are checked.
        held, _ = incidence(first)
        remote = set(growth._index(first).loose) - set(picked["parents"])
        if i:
            extra, = remote
            shore = set(range(len(first))) - {extra}
            g = nx.Graph()
            g.add_nodes_from(range(len(first) + 1))
            physical = {}
            for d, ends in held.items():
                physical[d] = ends if len(ends) == 2 else [ends[0], len(first)]
                g.add_edge(*physical[d])
            assert nx.is_connected(g.subgraph(shore)) and nx.is_connected(g.subgraph(set(g) - shore))
            bound = [d for d, (u, v) in physical.items() if (u in shore) != (v in shore)]
            assert len(bound) == 4 and set(picked["marked_loose_distinctions"]) <= set(bound)
            assert not any(truth for _, truth in picked["pair_bond_size_three"])
            picked["exact_pair_and_triple_minimum_size"] = 4
            picked["physical_minimum_cut"] = sorted(bound)
        else:
            assert not remote and all(truth for _, truth in picked["pair_bond_size_three"])
            picked["exact_pair_and_triple_minimum_size"] = 3
            picked["physical_minimum_cut"] = sorted(picked["marked_loose_distinctions"])
    return result


def sample_scores(trials):
    closes, continues = "closing", "continuing"
    shapes = defaultdict(Counter)
    items = []
    for record in trials:
        for stage in record["stages"]:
            for reading in stage["scored"]:
                kind = closes if reading["closes"] else continues
                items.append((kind, reading))
                shapes[reading["step_type"]][kind] += 1
    ambiguous = {typ for typ, counts in shapes.items() if len(counts) == 2}
    tally = defaultdict(Counter)
    for kind, reading in items:
        closed = kind == closes
        tally[kind]["funded_ternaries"] += 1
        tally[kind]["component_could_exhaust"] += reading["local_exhaustion"]
        tally[kind]["global_mechanism_agrees"] += (closed == reading["exhausts"] == reading["implied"] ==
                                                     reading["fresh_zero"] == reading["triple_bond_size_three"])
        tally[kind]["step_observed_with_both_fates"] += reading["step_type"] in ambiguous
        tally[kind]["component_all_loose_rule_correct"] += reading["local_exhaustion"] == closed
        hits = [prediction == closed for _, prediction in reading["pair_bond_size_three"]]
        tally[kind]["all_three_pair_rules_correct"] += all(hits)
        tally[kind]["individual_pair_rules_correct"] += sum(hits)
        tally[kind]["individual_pair_rule_queries"] += len(hits)
        tally[kind]["individual_pair_rule_failures"] += len(hits) - sum(hits)
        tally[kind]["empirical_step_ambiguity_and_all_pair_rules_correct"] += reading["step_type"] in ambiguous and all(hits)
    return {"physical_histories": len(trials), "source_outcomes": dict(Counter(t["outcome"] for t in trials)),
            "sources_with_funded_ternary": sum(any(s["scored"] for s in t["stages"]) for t in trials),
            "unfunded_or_capped_prospective_ternaries": sum(len(s["prospective_ternaries"])
                for t in trials for s in t["stages"] if s["status"] != "extend"),
            "exact_step_types": len(shapes), "ambiguous_types": {t: dict(shapes[t]) for t in sorted(ambiguous, key=int)},
            "optimistic_step_only_errors_on_observed_proposals": sum(min(shapes[t].values()) for t in ambiguous),
            "by_fate": {kind: dict(tally[kind]) for kind in (closes, continues)}}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    _, hard = resource.getrlimit(resource.RLIMIT_AS)
    soft = min(hard, MEMORY_LIMIT) if hard != resource.RLIM_INFINITY else MEMORY_LIMIT
    resource.setrlimit(resource.RLIMIT_AS, (soft, hard))

    observed = Observations()
    tree_audit = CrossCheck()
    tree_records = []
    for key, source, stars in trees():
        run = tree_trace(stars, key, observed, tree_audit)
        tree_records.append({"draw": key, "source_knots": len(stars), **source, **run})
    summary = sample_scores(tree_records)
    by_size = {size: sample_scores([r for r in tree_records if r["source_knots"] == size]) for size in range(4, 9)}
    print("trees", summary, flush=True)

    route_audit = CrossCheck()
    live_routes, arms, paired = [], [], []
    paired_ambiguity = 0
    for key, source, stars in routes():
        couple = audit_route(source, key, stars, observed, route_audit)
        paired.append({"draw": key, **source, "arms": couple})
        live_routes.extend(couple)
        arms.append(couple[source["fair_arm"]])
        s = [row["stages"][-1]["scored"] if row["stages"] else [] for row in couple]
        paired_ambiguity += (len(s[0]) == len(s[1]) == 1 and s[0][0]["step_type"] == s[1][0]["step_type"]
                             and s[0][0]["closes"] != s[1][0]["closes"])
    route = {"base_draws": len(paired), "directly_ambiguous_base_pairs": paired_ambiguity,
             "joint_arm_description": sample_scores(live_routes), "fair_arm": sample_scores(arms)}
    print("routes", route, flush=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result = {"schema": 1, "design_sha256": sha256(DESIGN.read_bytes()).hexdigest(),
              "limits": {"caps": CAPS, "memory_bytes": soft, "full_small_bond_checks_per_panel_cap": SMALL_FRAME_BUDGET},
              "seeds": {"tree": TREE_SEED, "route": ROUTE_SEED, "independent_fair_arm": ARM_SEED},
              "step_types": observed.types,
              "tree": {"source_draws": len(tree_records), "draws": tree_records, "scores": summary, "by_source_size": by_size,
                       "small_bond_table_checks": tree_audit.rows, "permutation_control": tree_audit.permuted},
              "routes": {"draws": paired, "scores": route, "small_bond_table_checks": route_audit.rows,
                         "permutation_control": route_audit.permuted}}
    args.out.write_text(json.dumps(result, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
