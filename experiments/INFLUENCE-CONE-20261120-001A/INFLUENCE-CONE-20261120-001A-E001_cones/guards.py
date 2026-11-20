"""Physical controls for distant funding cancellation and parity closing."""

from collections import Counter
from itertools import combinations
from pathlib import Path
import json
import sys

import networkx as nx
from pysat.solvers import Minisat22

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GEN = "GENERATORS-20261120-001A"
sys.path.insert(0, str(ROOT / "experiments" / GEN / (GEN + "-E001_generators")))
from controls import Frame, certify_source, check_relabeling, grow, owners_of, ring_stars, supports
from end_operator import local_counts, neighbors, proposals, restricted, step

OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "guards.json"
LAWS = ("parity", "nae")
MAX_AGE = 5


def ordinary_graph(stars):
    graph = nx.Graph()
    graph.add_nodes_from(range(len(stars)))
    graph.add_edges_from(row for row in owners_of(stars).values() if len(row) == 2)
    return graph


def witnessed_graph(end):
    return nx.Graph(neighbors(end))


def alternate_graph(end):
    graph = nx.Graph()
    graph.add_nodes_from(end.opens)
    graph.add_edges_from(group for group in proposals(end) if len(group) == 2)
    return graph


def distance_or_infinite(graph, a, b):
    try:
        return nx.shortest_path_length(graph, a, b)
    except nx.NetworkXNoPath:
        return "infinite"


def literal_history(stars, law, depth=MAX_AGE):
    result = [Frame(stars, {}, {})]
    while len(result) <= depth:
        if not result[-1].end.opens:
            break
        result.append(grow(result[-1], law))
    return result


def closing_source(length, spare):
    if length is None:
        return supports(4, ((0, 1), (0, 2), (0, 3)), (1, 1, 2, 2, 3, 3) + (0,) * spare), (1, 2, 3), 0
    # Every ordinary meeting of the three internally disjoint paths is doubled.
    # Their terminal s,z indices and internal vertices are distinct.
    s, z = 0, 1
    internal = [tuple(range(2 + i * (length - 1), 2 + (i + 1) * (length - 1))) for i in range(3)]
    paths = [(s, *row, z) for row in internal]
    near = tuple(row[0] for row in internal)
    meetings = [(a, b) for row in paths for a, b in zip(row, row[1:]) for _ in range(2)]
    opens = [v for v in near for _ in range(2)] + [z] * spare
    n = 2 + sum(map(len, internal))
    return supports(n, meetings, opens), near, z


def loose_on(frame, knots):
    holders = owners_of(frame.stars)
    return [d for v in knots for d in frame.stars[v] if len(holders[d]) == 1]


def receiver_projection(stars, marks, law):
    if law == "nae":
        clauses = [[(d + 1) * sign for d in row] for row in stars for sign in (-1, 1)]
        with Minisat22(bootstrap_with=clauses) as solver:
            return [code for code in range(1 << len(marks))
                    if solver.solve(assumptions=[(d + 1) * (1 if code & (1 << i) else -1)
                                                for i, d in enumerate(marks)])]
    # The independent Gaussian reduction tests annihilators on just these
    # marks. A parity projection is cut out by precisely the equations found.
    pivots = {}
    for row in stars:
        mask = sum(1 << d for d in row)
        while mask:
            high = mask.bit_length()
            if high not in pivots:
                pivots[high] = mask
                break
            mask ^= pivots[high]
    restrictions = []
    for code in range(1, 1 << len(marks)):
        support = sum(1 << d for i, d in enumerate(marks) if code & (1 << i))
        while support and support.bit_length() in pivots:
            support ^= pivots[support.bit_length()]
        if support == 0:
            restrictions.append(code)
    return [assignment for assignment in range(1 << len(marks))
            if all((assignment & eq).bit_count() % 2 == 0 for eq in restrictions)]


def parity_bond_sizes(frame, receiver, sender_child):
    """Lower bound by unrestricted cuts and attain it with connected shores."""
    owners = owners_of(frame.stars)
    exterior = len(frame.stars)
    super_source = exterior + 1
    graph = nx.DiGraph()
    graph.add_nodes_from(range(super_source + 1))
    for row in owners.values():
        a, b = row if len(row) == 2 else (*row, exterior)
        capacity = graph.get_edge_data(a, b, {}).get("capacity", 0) + 1
        graph.add_edge(a, b, capacity=capacity)
        graph.add_edge(b, a, capacity=capacity)
    shore = set(range(exterior)) - ({sender_child} if sender_child is not None else set())
    complement = set(range(exterior + 1)) - shore
    ordinary = graph.to_undirected()
    assert nx.is_connected(ordinary.subgraph(shore)) and nx.is_connected(ordinary.subgraph(complement))
    capacity = sum(1 for a, b in (row if len(row) == 2 else (*row, exterior) for row in owners.values())
                   if (a in shore) != (b in shore))
    results = {}
    for size in (2, 3):
        for marks in combinations(receiver, size):
            constrained = graph.copy()
            constrained.add_edges_from((super_source, v, {"capacity": len(owners) + 1}) for v in marks)
            lower = nx.minimum_cut_value(constrained, super_source, exterior)
            assert lower == capacity
            results[",".join(map(str, marks))] = capacity
    return results


def receiver_rows(frames, near):
    region = set(near)
    rows = []
    for age, frame in enumerate(frames):
        if age:
            region = {v for v, p in frame.parents.items() if set(p) <= region}
        rows.append({"age": age, "receiver_count": len(region), "receiver_knots": sorted(region),
                     "receiver_parent_arity_and_fresh": sorted(
                         (len(frame.parents[v]), frame.fresh[v]) for v in region) if age else [],
                     "receiver_scope_open": sum(v in frame.end.opens for v in region),
                     "all_live": len(frame.end.opens)})
    return rows


def check_fixed_writing_order(old, new, law):
    children = tuple(new.parents)
    known = {v: star for v, star in enumerate(old.stars)}
    final = {v: star for v, star in enumerate(new.stars)}
    for order in (children, children[::-1]):
        supports_written = dict(known)
        owners = Counter(d for row in known.values() for d in row)
        for v in order:
            star = final[v]
            parent_count = len(new.parents[v])
            consumed = set(star[:parent_count])
            fresh = set(star[parent_count:])
            assert all(owners[d] == 1 for d in consumed)
            assert all(owners[d] == 0 for d in fresh)
            assert len(fresh) == new.fresh[v]
            if law == "parity":
                assert (not fresh) == (consumed == {d for d, n in owners.items() if n == 1})
            else:
                assert fresh
            supports_written[v] = star
            owners.update(star)
        assert supports_written == final
    return True


def compare_prebirth_balls(frame0, frame1, receiver, sender):
    a, b = ordinary_graph(frame0.stars), ordinary_graph(frame1.stars)
    first, second = owners_of(frame0.stars), owners_of(frame1.stars)
    mark_renaming = {}
    # Near fresh identities may shift with the extra original distinction.
    for v in receiver:
        old, new = loose_on(frame0, (v,)), loose_on(frame1, (v,))
        assert len(old) == len(new) == 1
        mark_renaming[old[0]] = new[0]
    distances = []
    for root in receiver:
        distance = nx.shortest_path_length(a, root, sender)
        assert distance == nx.shortest_path_length(b, root, sender)
        inner = nx.single_source_shortest_path_length(a, root, cutoff=distance - 1)
        assert inner == nx.single_source_shortest_path_length(b, root, cutoff=distance - 1)
        assert set(a.subgraph(inner).edges()) == set(b.subgraph(inner).edges())
        for v in inner:
            assert tuple(mark_renaming.get(d, d) for d in frame0.stars[v]) == frame1.stars[v]
            assert all(len(first[d]) == len(second[mark_renaming.get(d, d)]) for d in frame0.stars[v])
        assert len(frame0.stars[sender]) + 1 == len(frame1.stars[sender])
        distances.append(distance)
    return distances


def closing_panel(length):
    sources = [closing_source(length, extra) for extra in (0, 1)]
    near, sender = sources[0][1:]
    assert sources[1][1:] == (near, sender)
    assert all(len(sources[1][0][i]) - len(sources[0][0][i]) == int(i == sender)
               for i in range(len(sources[0][0])))
    result = {"source_path_length_S_to_Z": length,
              "sender_to_original_receiver_min_ordinary_steps":
                  min(nx.shortest_path_length(ordinary_graph(sources[0][0]), sender, v) for v in near),
              "literal_sources": [certify_source(stars) for stars, _, _ in sources],
              "laws": {}}
    for law in LAWS:
        frames = [literal_history(stars, law) for stars, _, _ in sources]
        first = [series[1] for series in frames]
        both_orders = [[check_fixed_writing_order(series[age - 1], series[age], law)
                        for age in (1, 2)] for series in frames]
        end_births = [Counter(frame.parents.values()) for frame in first]
        if length == 3:
            ready = tuple(sorted((*near, sender)))
            assert end_births[1][ready] == 1 and all(end_births[0][p] == 1 for p in combinations(near, 2))
            assert not any(p in end_births[1] for p in combinations(near, 2))
            near_end = frames[1][0].end
            alternate = [distance_or_infinite(alternate_graph(near_end), sender, v) for v in near]
            assert alternate == ["infinite"] * 3
            result["laws"][law] = {"short_control": True, "has_matched_receiver_triple": False,
                                   "two_fixed_cohort_orders_quiet_and_armed_by_age": both_orders,
                                   "first_source_end_sender_distances":
                                       [nx.shortest_path_length(witnessed_graph(near_end), sender, v) for v in near],
                                   "first_source_alternate_sender_distances": alternate,
                                   "first_births_by_arity":
                                       [dict(sorted(Counter(map(len, f.parents.values())).items())) for f in first],
                                   "first_parent_and_fresh":
                                       [[(p, f.fresh[v]) for v, p in f.parents.items()] for f in first]}
            continue
        receiver = tuple(v for v, p in first[0].parents.items() if set(p) <= set(near))
        receiver_armed = tuple(v for v, p in first[1].parents.items() if set(p) <= set(near))
        assert len(receiver) == 3 and receiver == receiver_armed
        q = next(v for v, p in first[1].parents.items() if p == (sender,))
        original_distances = compare_prebirth_balls(*first, receiver, sender)
        assert set(original_distances) == {2 if length is None else length}
        end_only = [restricted(frame.end, receiver) for frame in first]
        assert end_only[0] == end_only[1]
        assert all(set(nx.node_connected_component(witnessed_graph(frame.end), receiver[0])) == set(receiver)
                   for frame in first)
        assert nx.has_path(witnessed_graph(first[1].end), q, receiver[0]) is False
        physical_distances = [nx.shortest_path_length(ordinary_graph(first[1].stars), q, v) for v in receiver]
        assert set(physical_distances) == {original_distances[0] + 1}
        alternate_distances = [[distance_or_infinite(alternate_graph(frame.end), a, b)
                                for a, b in combinations(receiver, 2)] for frame in first]
        assert alternate_distances == [["infinite"] * 3] * 2

        budget, projected, rows = [], [], []
        for series in frames:
            first_frame, birth_frame = series[1:3]
            child = [v for v, p in birth_frame.parents.items() if p == tuple(sorted(receiver))]
            assert len(child) == 1
            v = child[0]
            marks = loose_on(first_frame, receiver)
            assert len(marks) == 3 and set(marks) <= set(birth_frame.stars[v])
            budget.append({"parents": len(receiver), "new_support_size": len(birth_frame.stars[v]),
                           "fresh": birth_frame.fresh[v], "child_present": True,
                           "new_open_end": v in birth_frame.end.opens})
            projected.append(receiver_projection(first_frame.stars, marks, law))
            rows.append(receiver_rows(series, near))
        if law == "parity":
            assert [b["fresh"] for b in budget] == [0, 1]
            assert projected == [[0, 3, 5, 6], list(range(8))]
        else:
            assert [b["fresh"] for b in budget] == [1, 1]
            assert projected == [list(range(8)), list(range(8))]
        local = [local_counts(frame.end, receiver[0]) for frame in first]
        assert local[0] == local[1] == ((tuple(sorted(receiver)), 0, 1),)
        entry = {"whole_receiver_end_identical_before_birth": True,
                 "two_fixed_cohort_orders_quiet_and_armed_by_age": both_orders,
                 "receiver_has_no_witnessed_end_route_to_live_sender_child": True,
                 "receiver_pair_distances_primary_and_alternate_at_age_one":
                     {"primary_both_arms": [1, 1, 1], "alternate_by_arm": alternate_distances,
                      "including_all_pairs_of_a_true_birth_both_arms": [1, 1, 1]},
                 "sender_to_receiver_at_age_one_ordinary_distances": original_distances,
                 "sender_child_to_receiver_at_age_one_ordinary_distances": physical_distances,
                 "receiver_inputs_from_whole_stage_projected_assignments": projected,
                 "receiver_birth_budget": budget,
                 "receiver_histories_quiet_and_armed": rows,
                 "local_nonclosing_prediction": local[0],
                 "anonymous_joint_relabeling_passes_in_each_arm": [check_relabeling(f, law) for f in first],
                 "physical_whole_end_counts_quiet_and_armed": [
                     [len(f.parents) for f in series[1:]] for series in frames]}
        if law == "parity":
            deck = [parity_bond_sizes(f, receiver, q if arm else None) for arm, f in enumerate(first)]
            assert [set(row.values()) for row in deck] == [{3}, {4}]
            entry["exact_minimum_parity_bond_sizes_for_pairs_and_triple"] = deck
        result["laws"][law] = entry
    return result


def funding_panel(width):
    intact = Frame(ring_stars(width), {}, {})
    graph = ordinary_graph(intact.stars)
    end = intact.end
    compatible = witnessed_graph(end)
    alternate = alternate_graph(end)
    assert set(alternate.edges()) == set(compatible.edges())
    records = {}
    for law in LAWS:
        kept = literal_history(intact.stars, law, 3)
        assert len(kept) == 4
        correct = step(end, law)
        assert correct.status == "extend" and len(correct.parents) == width
        assert all(len(p) == 2 and f == 2 for p, f in zip(correct.parents, correct.fresh, strict=True))
        rows = []
        for sender in range(width):
            omitted = loose_on(intact, (sender,))[0]
            adjusted = tuple(tuple(d for d in star if d != omitted) for star in intact.stars)
            altered = Frame(adjusted, {}, {})
            evidence = certify_source(altered.stars)
            failed = step(altered.end, law)
            assert failed.status == "stall" and failed.shortages == ((sender, 1),)
            assert proposals(end) == proposals(altered.end)
            assert neighbors(end) == neighbors(altered.end)
            assert set(alternate_graph(altered.end).edges()) == set(alternate.edges())
            for receiver in set(range(width)) - {sender}:
                d_end = nx.shortest_path_length(compatible, sender, receiver)
                d_physical = nx.shortest_path_length(graph, sender, receiver)
                good_view = nx.single_source_shortest_path_length(compatible, receiver, cutoff=d_end - 1)
                assert restricted(end, good_view) == restricted(altered.end, good_view)
                physical_view = nx.single_source_shortest_path_length(graph, receiver, cutoff=d_physical - 1)
                assert all(intact.stars[j] == adjusted[j] for j in physical_view)
                candidate = [(p, f) for p, f in zip(correct.parents, correct.fresh, strict=True) if receiver in p]
                assert len(candidate) == 2 and all(f == 2 for _, f in candidate)
                if d_end > 1:
                    assert local_counts(end, receiver) == local_counts(altered.end, receiver)
                rows.append({"sender": sender, "receiver": receiver, "removed_loose": omitted,
                             "ordinary_distance": d_physical, "witnessed_end_distance": d_end,
                             "both_sources_lawful": True, "stalled_source_distinctions": evidence["distinctions"],
                             "intact_receiver_births_and_fresh": candidate,
                             "canceled_receiver_executed_births": None,
                             "local_nonclosing_plan_agrees_when_sender_outside_receiver_neighborhood": d_end > 1})
        assert len(rows) == width * (width - 1)
        records[law] = {"ordered_root_sender_rows": rows,
                        "funded_live_births": [len(f.parents) for f in kept[1:]],
                        "only_shortage_edited_live_sender_one_slot": True}
    assert records["parity"] == records["nae"]
    distances = Counter((r["ordinary_distance"], r["witnessed_end_distance"])
                        for r in records["parity"]["ordered_root_sender_rows"])
    return {"source": certify_source(intact.stars), "laws": records,
            "matched_distance_pair_histogram": [[*ds, n] for ds, n in sorted(distances.items())]}


def main():
    result = {"closing_panel": [closing_panel(length) for length in (None, 3, 4, 5, 9)],
              "funding_panel": {n: funding_panel(n) for n in (7, 9, 13)}}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
