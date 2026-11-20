"""Compare two physical clocks and the sharp funded radius-two control."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import sys

import networkx as nx
from pysat.solvers import Minisat22


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "fixtures.json"
RELAY = ROOT / "experiments/COPIES-AND-MEETINGS-20261120-001A/" \
    "COPIES-AND-MEETINGS-20261120-001A-E001_copies"
sys.path.insert(0, str(RELAY))
import mediator as relay
from end_operator import from_stars, local_counts, step


ordinary = relay.ordinary


def role(cell):
    lo, hi, extra = cell
    assert not extra
    return (0, lo, hi)


def min_steps(graph, left, right):
    if not left or not right:
        return None
    lengths = nx.multi_source_dijkstra_path_length(graph, left)
    return min((lengths[r] for r in right if r in lengths), default=None)


def binary_graph(rows, law):
    plan = step(from_stars(rows), law, max_births=1024)
    assert plan.status == "extend"
    _, physical, loose = ordinary.incidence(rows)
    _, witnessed = ordinary.witnessed_end(physical, loose)
    co_inputs = {tuple(sorted(pair)) for group in plan.parents for pair in combinations(group, 2)}
    assert co_inputs == {tuple(sorted(pair)) for pair in witnessed.edges}
    graph = nx.Graph()
    graph.add_nodes_from(loose)
    graph.add_edges_from(group for group in plan.parents if len(group) == 2)
    return graph


def historical_roles(levels, d):
    names = {k: role(c) for level in levels for c, k in level.items()}
    names.update((d + 1 + i, (1, i, i + 1)) for i in range(d))
    return names


def annotated_ball(frame, names, root, radius):
    """Induced ordinary-holder ball with true arity, loose count, and internal multiplicities."""
    owners, graph, loose = ordinary.incidence(frame)
    ball = nx.single_source_shortest_path_length(graph, root, cutoff=radius)
    annotations = {names[k]: (r, len(frame[k]), len(loose.get(k, ()))) for k, r in ball.items()}
    multiplicities = Counter(tuple(sorted(names[k] for k in at))
                             for at in owners.values() if len(at) == 2 and all(k in ball for k in at))
    return annotations, multiplicities


def verify_inputs(quiet, edited, q_maps, e_maps, d):
    """Transport actual shared inputs and retain every old distinction identity at the source."""
    base_root, edit_root = quiet.frames[0], edited.frames[0]
    source_bits = {bit for row in base_root for bit in row}
    assert all(q == e for k, (q, e) in enumerate(zip(base_root, edit_root, strict=True)) if k != d)
    assert edit_root[d][:-1] == base_root[d] and edit_root[d][-1] not in source_bits
    images = dict(zip(source_bits, source_bits, strict=True))
    matched_holders = {k: k for k in range(len(base_root))}
    counts = []
    for age, (left, right) in enumerate(zip(q_maps[1:], e_maps[1:], strict=True), 1):
        assert quiet.frames[age][:-len(quiet.born[age])] == quiet.frames[age - 1]
        assert edited.frames[age][:-len(edited.born[age])] == edited.frames[age - 1]
        input_edges = 0
        for cell in sorted(left):
            q, e = quiet.born[age][left[cell]], edited.born[age][right[cell]]
            e_by_parent = dict(zip(e.parents, e.inputs, strict=True))
            assert {matched_holders[p] for p in q.parents} == e_by_parent.keys()
            for p, bit in zip(q.parents, q.inputs, strict=True):
                image = e_by_parent[matched_holders[p]]
                assert images.setdefault(bit, image) == image
                input_edges += 1
            matched_holders[q.knot] = e.knot
        counts.append(input_edges)
    assert len(images) == len(set(images.values()))
    for age, (left, right) in enumerate(zip(q_maps[1:], e_maps[1:], strict=True), 1):
        for cell in sorted(left):
            q, e = quiet.born[age][left[cell]], edited.born[age][right[cell]]
            already_used = {images[bit] for bit in q.fresh if bit in images}
            assert already_used <= set(e.fresh)
            pending = [bit for bit in q.fresh if bit not in images]
            spare = sorted(set(e.fresh) - already_used)
            assert len(spare) >= len(pending)
            images.update(zip(pending, spare))
    assert len(images) == len(set(images.values()))
    q_owners = ordinary.incidence(quiet.frames[-1])[0]
    e_owners = ordinary.incidence(edited.frames[-1])[0]
    assert set(images) == q_owners.keys()
    matched_set = set(matched_holders.values())
    assert all({matched_holders[k] for k in holders} == (set(e_owners[images[bit]]) & matched_set)
               for bit, holders in q_owners.items())
    assert all(set(e_owners[target]) <= matched_set for target in images.values())
    return {"common_input_edges_per_age": counts, "frozen_source_distinctions": len(source_bits),
            "matched_final_holders": len(matched_holders), "matched_final_distinctions": len(images)}


def origin_families(history, d):
    left, right = {0}, {d}
    result = [(left, right)]
    for born in history.born[1:]:
        left = {k for k, b in born.items() if left.intersection(b.parents)}
        right = {k for k, b in born.items() if right.intersection(b.parents)}
        result.append((left, right))
    return result


def verify_backward(history, origins, launches):
    """Read root membership by iterating actual parent sets backwards from each target."""
    marks = (launches[0]["a_inclusive"], launches[0]["b_inclusive"])
    count = 0
    for age, level in enumerate(history.born[1:], 1):
        for k in level:
            current = {k}
            for i in range(age, 0, -1):
                if i == 1:
                    for key, anchors in zip(("a_inclusive", "b_inclusive"), marks, strict=True):
                        assert bool(current & anchors) == (k in launches[age-1][key])
                current = {p for child in current for p in history.born[i][child].parents}
            for anchors, descendants in zip(origins[0], origins[age], strict=True):
                assert bool(current & anchors) == (k in descendants)
            count += 1
    return count


def first_families(quiet, edited, q_maps, e_maps, q_families, e_families):
    first_price, first_roster = None, None
    records = []
    for age, (q, e) in enumerate(zip(q_maps[1:], e_maps[1:], strict=True), 1):
        q_left = {s for s, k in q.items() if k in q_families[age]}
        e_left = {s for s, k in e.items() if k in e_families[age]}
        assert q_left <= e_left
        h_q, h_e = quiet.born[age], edited.born[age]
        changed = sorted(c for c in q_left if len(h_q[q[c]].fresh) != len(h_e[e[c]].fresh))
        new = sorted(e_left - q_left)
        if changed and first_price is None:
            assert len(changed) == 1
            cell, = changed
            first_price = {"age": age, "size": age + 1,
                           "quiet": relay.physical_birth(quiet, q_maps, age + 1, cell),
                           "edited": relay.physical_birth(edited, e_maps, age + 1, cell)}
        if new and first_roster is None:
            assert len(new) == 1
            cell, = new
            first_roster = {"age": age, "size": age + 1, "birth": relay.physical_birth(edited, e_maps, age + 1, cell)}
        fresh_q = Counter(len(h_q[q[c]].fresh) for c in q_left)
        fresh_e = Counter(len(h_e[e[c]].fresh) for c in e_left)
        records.append({"age": age, "matched_h_changes": changed, "only_edited_births": new,
                        "fresh_profiles": [sorted(fresh_q.items()), sorted(fresh_e.items())]})
    return first_price, first_roster, records


def path_pair(d, law):
    s = relay.source(d, 1)
    changed, edit = relay.add_distinction(s, (d,))
    limit = d + 5
    quiet, edited = (relay.grow(rows, law, limit) for rows in (s, changed))
    q_maps = relay.match_intervals(quiet, d, right_ray=False)
    e_maps = relay.match_intervals(edited, d, right_ray=True)
    q_names, e_names = [historical_roles(maps, d) for maps in (q_maps, e_maps)]
    relay.check_roles(quiet, d, law)
    relay.check_roles(edited, d, law)
    transport = verify_inputs(quiet, edited, q_maps, e_maps, d)
    q_origin, e_origin = [origin_families(h, d) for h in (quiet, edited)]
    q_launch, _ = relay.ancestry(quiet, d)
    e_launch, _ = relay.ancestry(edited, d)
    back_checks = [verify_backward(h, origins, launches) for h, origins, launches in (
        (quiet, q_origin, q_launch), (edited, e_origin, e_launch))]
    original_price, original_roster, original_profiles = first_families(
        quiet, edited, q_maps, e_maps, [l for l, _ in q_origin], [l for l, _ in e_origin])
    launch_price, launch_roster, launch_profiles = first_families(
        quiet, edited, q_maps, e_maps, [set(), *(x["a_inclusive"] for x in q_launch)],
        [set(), *(x["a_inclusive"] for x in e_launch)])
    assert [original_price["age"], original_roster["age"], launch_price["age"], launch_roster["age"]] == [d, d+1, d+1, d+2]
    assert original_price["edited"]["cell"] == (0, d, False)
    assert original_roster["birth"]["cell"] == (0, d + 1, False)
    assert launch_price["edited"]["cell"] == (-1, d, False)
    assert launch_roster["birth"]["cell"] == (-1, d + 1, False)
    for price in (original_price, launch_price):
        assert len(price["quiet"]["fresh"]) == 1 and len(price["edited"]["fresh"]) == 2

    radii = []
    price_chain = []
    for t, (q, e) in enumerate(zip(q_maps, e_maps, strict=True)):
        q_frame, e_frame = quiet.frames[t], edited.frames[t]
        q_graph, e_graph = [ordinary.incidence(frame)[1] for frame in (q_frame, e_frame)]
        q_view, e_view = [relay.live_read(frame) for frame in (q_frame, e_frame)]
        a, p = (-t, 0, False), (d - t, d, False)
        assert {c for c in q if len(q_view[0][q[c]]) != len(e_view[0][e[c]])} == {p}
        assert [len(q_view[0][q[p]]), len(e_view[0][e[p]])] == [1, 2]
        assert {e[p]} | {e[c] for c in e.keys() - q.keys()} == e_origin[t][1]
        assert nx.shortest_path_length(q_view[2], q[a], q[p]) == nx.shortest_path_length(e_view[2], e[a], e[p]) == d
        assert nx.shortest_path_length(q_graph, q[a], q[p]) == nx.shortest_path_length(e_graph, e[a], e[p]) == 2 * d
        assert nx.shortest_path_length(q_graph, q[a], d) == nx.shortest_path_length(e_graph, e[a], d) == 2 * d + t
        assert nx.shortest_path_length(q_graph, 0, d) == nx.shortest_path_length(e_graph, 0, d) == 2 * d
        assert nx.shortest_path_length(e_graph, d, e[p]) == t
        for r in range(d):
            assert relay.projected_end(q_view, q, q[a], r) == relay.projected_end(e_view, e, e[a], r)
        assert relay.projected_end(q_view, q, q[a], d) != relay.projected_end(e_view, e, e[a], d)
        for r in range(2 * d):
            assert annotated_ball(q_frame, q_names, q[a], r) == annotated_ball(e_frame, e_names, e[a], r)
        assert annotated_ball(q_frame, q_names, q[a], 2 * d) != annotated_ball(e_frame, e_names, e[a], 2 * d)

        forward = [min_steps(view[2], *family[t]) for view, family in ((q_view, q_origin), (e_view, e_origin))]
        physical = [min_steps(g, *family[t]) for g, family in ((q_graph, q_origin), (e_graph, e_origin))]
        assert forward == [max(0, d - t)] * 2 and physical == [2 * max(0, d - t)] * 2
        q_two, e_two = binary_graph(q_frame, law), binary_graph(e_frame, law)
        assert [min_steps(g, *f[t]) for g, f in ((q_two, q_origin), (e_two, e_origin))] == forward
        record = {"age": t, "original_inclusive_witnessed": forward, "original_inclusive_ordinary": physical,
                  "tip_to_matched_price_holder_witnessed": d, "tip_to_matched_price_holder_ordinary": 2*d,
                  "tip_to_original_donor_ordinary": 2*d+t}
        if t:
            f = e_launch[t-1]
            launch_sets = (f["a_inclusive"], f["b_inclusive"])
            w, physical = min_steps(e_view[2], *launch_sets), min_steps(e_graph, *launch_sets)
            assert w == max(0, d + 2 - t) and physical == 2*w
            assert min_steps(e_two, *launch_sets) == w
            assert bool(f["mixed"]) == (t >= d+2) and not f["direct"] and not f["pure_A_and_B_descendant"]
            assert min_steps(e_view[2], f["pure_a"], f["b_inclusive"]) == d + 1
            record.update(steps_after_release=t-1, release_inclusive_witnessed=w, release_inclusive_ordinary=physical,
                          pure_A_to_inclusive_B_witnessed=d+1)
            b = relay.physical_birth(edited, e_maps, t + 1, p)
            chosen = e_maps[t-1][(d-t+1, d, False)]
            assert chosen in b["parents"]
            price_chain.append({"age":t, "older":chosen, "newer":b["knot"],
                                "shared_distinction":b["consumed"][b["parents"].index(chosen)]})
        radii.append(record)
    return {"d": d, "sources": [s, changed], "one_edit": edit, "through_size": limit,
            "physical_transport": transport, "radii": radii, "actual_price_chain": price_chain,
            "backward_ancestry_targets": back_checks, "actual_binary_only_matches_path_steps_at_all_reached_sizes": True,
            "original_clock": {"first_price": original_price, "first_extra_birth": original_roster,
                               "profiles": original_profiles},
            "release_clock": {"first_price": launch_price, "first_extra_birth": launch_roster,
                              "profiles": launch_profiles}, "fixed_map_replays": [quiet.replay, edited.replay]}


def witnessed_fixture(pairs, opens):
    meetings = [(k, 4 + i) for i, pair in enumerate(pairs)
                for k, thickness in zip(pair, (1, 2), strict=True) for _ in range(thickness)]
    return ordinary.source_from(meetings, list(opens) + [0]*len(pairs))


def witness_sets(rows):
    _, shared, loose = ordinary.incidence(rows)
    return {w: sorted(set(shared[w]) & loose.keys()) for w in shared if len(set(shared[w]) & loose.keys()) >= 2}


def radius_one(rows):
    loose, witnesses, graph = relay.live_read(rows)
    relevant = {0} | set(graph[0])
    return {k: len(loose[k]) for k in sorted(relevant)}, Counter(
        tuple(sorted(b & relevant)) for b in witnesses if len(b & relevant) >= 2)


def allowed_words(rows, scope, law):
    if law == "parity":
        return ordinary.parity_words(rows, scope)
    with Minisat22() as solver:
        for row in rows:
            ordinary.nae_add(solver, row)
        return ordinary.nae_words(solver, scope)


def sharp_arm(source, law, *, verify_second):
    history = relay.grow(source, law, 3 if verify_second else 2)
    frames, born = history.frames, history.born
    _, shared, loose = ordinary.incidence(source)
    _, graph = ordinary.witnessed_end(shared, loose)
    two = binary_graph(source, law)
    assert min_steps(graph, {0}, {1}) == 1 and min_steps(two, {0}, {1}) is None
    p, = [b for b in born[1].values() if 0 in b.parents]
    assert p.parents == (0, 1, 2) and len(born[1]) > 1 and p.fresh
    before_words = allowed_words(source, p.inputs, law)
    after_words = allowed_words(frames[1], p.inputs, law)
    assert before_words == after_words == tuple(range(8))
    local = local_counts(from_stars(source), 0)
    assert local == ((p.parents, len(p.fresh), len(p.fresh)),)
    _, next_shared, next_loose = ordinary.incidence(frames[1])
    next_witnesses, next_graph = ordinary.witnessed_end(next_shared, next_loose)
    lookahead = [tuple(born[1][child].parents for child in group)
                 for group in ordinary.multi_groups(next_witnesses, next_graph) if p.knot in group]
    assert len(lookahead) == len(p.fresh)
    assert frames[1][0] == source[0] and len(loose[0]) == 1 and 0 not in next_loose
    renamed, inverse = ordinary.rename(source, 20261120875)
    status, writes, _ = ordinary.literal_turn(renamed, law)
    expected = Counter((frozenset(b.parents), len(b.fresh)) for b in born[1].values())
    assert status == "extend"
    assert expected == Counter((frozenset(inverse[i] for i in b.parents), len(b.fresh)) for b in writes)
    result = {"source": source, "opens": {k: len(row) for k, row in loose.items()},
              "witness_sets": witness_sets(source),
              "steps_u_to_x": {"witnessed": min_steps(graph, {0}, {3}), "ordinary_holders": min_steps(shared, {0}, {3}),
                               "x_live": 3 in loose, "binary_only": min_steps(two, {0}, {3})},
              "steps_u_to_a": {"witnessed": 1, "ordinary_holders": min_steps(shared, {0}, {1}),
                               "binary_only": None, "first_common_birth_step": 1},
              "first_physical_births": [vars(b) for b in born[1].values()], "receiver": vars(p),
              "receiver_old_held_distinctions": source[0], "receiver_loose_before_after": [1, 0],
              "receiver_child_arity": len(p.support), "old_input_value_alphabet_before_after": [before_words, after_words],
              "lookahead_groups_through_receiver_child": lookahead}
    if verify_second:
        x_children = {b.knot for b in born[1].values() if 3 in b.parents}
        assert p.knot not in x_children
        assert min_steps(next_graph, {p.knot}, x_children) == 1
        assert min_steps(next_shared, {p.knot}, x_children) == 2
        common = [b for b in born[2].values() if p.knot in b.parents and x_children.intersection(b.parents)]
        assert common
        result.update(first_u_x_common_birth_step=2, actual_first_u_x_common_births=[vars(b) for b in common],
                      distance_from_P_to_x_children_after_step_one={"witnessed": 1, "ordinary_holders": 2},
                      live_knots_after_second_births=len(ordinary.incidence(frames[2])[2]))
    result["replay"] = history.replay
    return result


def lookahead(law):
    pairs = ((0, 1), (0, 2), (1, 2), (1, 3))
    rows = witnessed_fixture(pairs, (1, 2, 2, 2))
    shared_rows, shared_edit = relay.add_distinction(rows, (3, 6))
    loose_rows, loose_edit = relay.add_distinction(rows, (3,))
    assert radius_one(rows) == radius_one(shared_rows) == radius_one(loose_rows)
    base, shared, extra_loose = (sharp_arm(r, law, verify_second=True) for r in (rows, shared_rows, loose_rows))
    scopes = [candidate["receiver"]["inputs"] for candidate in (base, shared, extra_loose)]
    assert scopes[0] == scopes[1] == scopes[2]
    assert [len(x["receiver"]["fresh"]) for x in (base, shared, extra_loose)] == [2, 1, 2]
    assert shared["live_knots_after_second_births"] == (0 if law == "parity" else 1)
    assert base["opens"] == shared["opens"] and base["witness_sets"] == extra_loose["witness_sets"]
    assert base["witness_sets"].keys() == shared["witness_sets"].keys()
    assert {k: b for k, b in shared["witness_sets"].items() if b != base["witness_sets"][k]} == {6: [1, 2, 3]}
    _, q_graph, _ = ordinary.incidence(rows)
    _, e_graph, _ = ordinary.incidence(shared_rows)
    assert min_steps(q_graph, {0}, {3}) == min_steps(e_graph, {0}, {3}) == 4
    assert min_steps(q_graph, {0}, {6}) == min_steps(e_graph, {0}, {6}) == 3
    inactive = witnessed_fixture((*pairs, (2, 3)), (1, 2, 2, 0))
    active, activation_edit = relay.add_distinction(inactive, (3,))
    assert radius_one(inactive) == radius_one(active)
    dormant, activated = (sharp_arm(s, law, verify_second=False) for s in (inactive, active))
    assert [len(x["receiver"]["fresh"]) for x in (dormant, activated)] == [2, 1]
    assert dormant["receiver"]["inputs"] == activated["receiver"]["inputs"]
    assert not dormant["steps_u_to_x"]["x_live"] and activated["steps_u_to_x"]["witnessed"] == 2
    return {"same_active_set": {"base": base, "shared_edit": shared_edit, "shared": shared,
                               "loose_edit": loose_edit, "extra_loose": extra_loose,
                               "edited_spent_holder_ordinary_steps_to_u": [3, 3],
                               "changed_pair_witness_facts": {"u_witnessed_radius": 1, "gained_pair": [2, 3],
                                                              "gained_duplicate_witness_pair": [1, 3]}},
            "activation": {"edit": activation_edit, "base": dormant, "active": activated}}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    by_law = {}
    for law in ("parity", "nae"):
        by_law[law] = {"lookahead": lookahead(law), "paths": {str(d): path_pair(d, law) for d in (2, 3, 5, 8)}}
    result = {"design": "74571080614c79af14fae2a2ba9e2775cb0bdc39", "laws": by_law,
              "all_actual_co_input_pairs_equal_witnessed_relation_at_every_scored_cut": True}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
