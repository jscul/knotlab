"""Search one unmaterialized round using physical child supports around selected parents.

A certified residual pair P,Q at the new age meets at x. Every child that
meets both contains x. Thus every larger compatible group containing that
pair is held. An absent edge or cycle in this partial graph is only a bound.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from collections import defaultdict
from functools import lru_cache
from itertools import combinations
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[3]
HUB = "HUB-GUIDED-SAMPLE-20261119-001"
sys.path.insert(0, str(ROOT / "experiments" / HUB / f"{HUB}-E001_sampler"))
from group_profile import Stage, members


def enumerate_at(stage, x, limit, y=None):
    """Contract equal closed neighborhoods inside N[x] before listing maximal groups."""
    base = stage.hood(stage.at[x])
    if y is not None:
        base &= stage.hood(stage.at[y])
    twins = defaultdict(int)
    for v in members(base):
        twins[stage.hood(stage.at[v]) & base] |= 1 << v
    reps = [(mask & -mask).bit_length() - 1 for mask in twins.values()]
    masks = list(twins.values())
    adjacent = [sum(1 << j for j, v in enumerate(reps) if hood >> v & 1)
                for hood in twins]
    index = next(j for j, mask in enumerate(masks) if mask >> x & 1)
    answer = set()
    count = 0

    def visit(chosen, possible, excluded):
        nonlocal count
        if not possible and not excluded:
            count += 1
            physical = 0
            for j in members(chosen):
                physical |= masks[j]
            if physical.bit_count() >= 3 and all(
                    physical & ~stage.blocks[h] for h in stage.at[x]):
                answer.add(physical)
            return
        pivot = max(members(possible | excluded),
                    key=lambda j: (adjacent[j] & possible).bit_count())
        todo = possible & (~adjacent[pivot] | (1 << pivot))
        for j in members(todo):
            if count >= limit:
                return
            bit = 1 << j
            neighbors = adjacent[j] ^ bit
            visit(chosen | bit, possible & neighbors, excluded & neighbors)
            possible ^= bit
            excluded |= bit

    visit(1 << index, ((1 << len(masks)) - 1) ^ (1 << index), 0)
    full = count < limit
    if full and y is None:
        uncovered = base ^ (1 << x)
        for mask in answer:
            uncovered &= ~mask
        answer.update((1 << x) | (1 << v) for v in members(uncovered))
    elif full and not answer:
        answer.add((1 << x) | (1 << y))
    return answer, full, count


def run(cache, start, age, cap, number, group_cap, audit_cap, shared_cap=0,
        pair_cap=16000, multiple=False, check_small=False):
    roster = cache / f"start-{start:02}-age{age:02}"
    stage = Stage(roster.with_suffix(".txt"))
    with gzip.open(roster.with_suffix(".degrees.json.gz"), "rt") as f:
        degrees = json.load(f)
    with gzip.open(roster.with_suffix(".parents.json.gz"), "rt") as f:
        parents = json.load(f)
    anchors = sorted((v for v, d in enumerate(degrees) if 0 < d <= cap),
                     key=lambda v: (degrees[v], v))[:number]
    childsets = {}
    exhausted = set()
    for v in anchors:
        found, full, _ = enumerate_at(stage, v, group_cap)
        childsets[v] = found
        if full:
            exhausted.add(v)
        # In these reached rosters one certified unary child is born at the tip.
        if len(parents[v]) == 1 and degrees[v] == 1:
            found.add(1 << v)
    supports = set().union(*childsets.values()) if anchors else set()
    pair_lists = {}
    considered = 0
    if shared_cap:
        small_blocks = sorted((b for b in stage.blocks if b.bit_count() <= shared_cap),
                              key=lambda b: (b.bit_count(), b))
        seen_pairs = set()
        for block in small_blocks:
            if len(pair_lists) >= pair_cap:
                break
            for a, b in combinations(members(block), 2):
                if (a, b) in seen_pairs or a in exhausted or b in exhausted:
                    continue
                seen_pairs.add((a, b))
                considered += 1
                joint = stage.hood(stage.at[a]) & stage.hood(stage.at[b])
                if joint.bit_count() > shared_cap:
                    continue
                choices, complete, _ = enumerate_at(stage, a, group_cap, b)
                supports.update(choices)
                if complete:
                    pair_lists[(a, b)] = tuple(choices)
                if len(pair_lists) >= pair_cap:
                    break
    all_residuals = None
    previous = ROOT / "artifacts" / HUB / f"{HUB}-E001_sampler" / f"literal_residual{start:02}.json"
    latest_literal = {3: 8, 6: 7, 7: 7, 12: 7, 13: 7, 15: 8}
    if previous.exists() and age == latest_literal.get(start):
        pairs = json.loads(previous.read_text())["residual_pairs"]
        all_residuals = {tuple(sorted(pair)) for pair in pairs}
        supports.update((1 << a) | (1 << b) for a, b in pairs)
    incident_residual = defaultdict(set)
    for v, w in all_residuals or ():
        incident_residual[v].add(w)
        incident_residual[w].add(v)
    by_parent = defaultdict(list)
    ordered = sorted(supports)
    for j, group in enumerate(ordered):
        for v in members(group):
            by_parent[v].append(j)
    # Any compatible pair crossing the two outside portions is checked using
    # a full incident-child list whenever either endpoint was exhausted.
    @lru_cache(maxsize=32768)
    def cross_possible(v, w, x):
        if not (stage.hood(stage.at[v]) >> w & 1):
            return False
        if v in exhausted or w in exhausted:
            v, w = (v, w) if v in exhausted else (w, v)
            return any((g >> w & 1) and not (g >> x & 1) for g in childsets[v])
        pair = tuple(sorted((v, w)))
        if pair in pair_lists:
            return any(not (g >> x & 1) for g in pair_lists[pair])
        common = stage.hood(stage.at[v]) & stage.hood(stage.at[w])
        if common & ~stage.hood(stage.at[x]):
            return True
        # Every maximal clique through v,w also contains x. The only possible
        # counter-witness is the two-parent child itself. Rule it out either
        # from a literal list or from an unheld triple through that pair.
        if all_residuals is not None:
            return tuple(sorted((v, w))) in all_residuals
        held_union = 0
        for h in set(stage.at[v]).intersection(stage.at[w]):
            held_union |= stage.blocks[h]
        return not bool(common & ~held_union)

    @lru_cache(maxsize=32768)
    def every_child_uses(v, x):
        if v in exhausted:
            return all(g >> x & 1 for g in childsets[v])
        if all_residuals is None or len(parents[v]) <= 1 or degrees[v] == 0:
            return False
        return (not (stage.hood(stage.at[v]) & ~stage.hood(stage.at[x]))
                and incident_residual[v] <= {x})

    edges = set()
    skipped = 0
    for x, incident in by_parent.items():
        if len(incident) > audit_cap:
            skipped += 1
            continue
        bit = 1 << x
        for i, j in combinations(incident, 2):
            p, q = ordered[i], ordered[j]
            common = p & q
            if common != bit and (not multiple or
                                  not all(every_child_uses(v, x) for v in members(common ^ bit))):
                continue
            a, b = p ^ common, q ^ common
            if any(cross_possible(v, w, x) for v in members(a) for w in members(b)):
                continue
            edges.add((i, j))
    neighbors = defaultdict(set)
    for i, j in edges:
        neighbors[i].add(j)
        neighbors[j].add(i)
    turns = nx.DiGraph()
    for j, nb in neighbors.items():
        for i, k in combinations(nb, 2):
            if not ordered[i] & ordered[k]:
                turns.add_edge((i, j), (j, k))
                turns.add_edge((k, j), (j, i))
    cyc = [s for s in nx.strongly_connected_components(turns) if len(s) > 1]
    radial = None
    radial_witness = []
    if start in (3,14):
        tip, = [i for i,g in enumerate(parents) if len(g)==1]
        from outer_layer import radial_layers
        layers = radial_layers(stage, tip)
        rad = [0 if g == 1 << tip else next(i for i,m in enumerate(layers) if m & g) + 1
               for g in ordered]
        radial = []
        for threshold in range(max(rad, default=0)+1):
            far_edges = sum(min(rad[i],rad[j]) >= threshold for i,j in edges)
            if not far_edges:
                break
            states = [s for s in turns if min(rad[i] for i in s) >= threshold]
            sub = turns.subgraph(states)
            depth = None if not nx.is_directed_acyclic_graph(sub) else (
                nx.dag_longest_path_length(sub)+1 if states else 1)
            radial.append([threshold, far_edges,depth])
            if depth and depth > 1 and threshold in (4,6) and start==3 and age==8:
                path = nx.dag_longest_path(sub)
                indices = [path[0][0]] + [s[1] for s in path]
                radial_witness.append(dict(minimum_old_radius=threshold,pairs=depth,
                                      age_nine_parent_lists=[list(members(ordered[v])) for v in indices]))
    sample = None
    if cyc:
        component = max(cyc, key=len)
        cycle = nx.find_cycle(turns.subgraph(component))
        sample = [list(members(ordered[edge[0][0]])) for edge in cycle]
    if check_small:
        from stages import archived
        assert len(exhausted) == stage.n and len(ordered) <= 120
        old_blocks = [frozenset(members(b)) for b in stage.blocks]
        all_groups = archived.groups_of(list(range(stage.n)), old_blocks)
        actual = {sum(1 << v for v in g) for g in all_groups}
        actual.update(1 << v for v in anchors if len(parents[v]) == degrees[v] == 1)
        assert set(ordered) == actual
        new_blocks = [frozenset(items) for items in by_parent.values()]
        new_groups = archived.groups_of(list(range(len(ordered))), new_blocks)
        new_pairs = {tuple(sorted(g)) for g in new_groups if len(g) == 2}
        assert edges <= new_pairs
    return dict(start=start, age=age, new_age=age+1, width=stage.n,
                anchor_degree_cap=cap, anchor_count_cap=number, clique_limit=group_cap,
                included_multiple_shared_parents=multiple,
                anchor_count=len(anchors), exhausted_anchors=len(exhausted),
                largest_anchor_degree=max((degrees[v] for v in anchors),default=0),
                incident_child_cutoff=audit_cap, skipped_pivots=skipped,
                small_joint_neighborhood_limit=shared_cap, small_pair_budget=pair_cap,
                inspected_old_pairs=considered, exhausted_old_pair_lists=len(pair_lists),
                minimum_candidate_distance_and_longest_protected_walk=radial,
                radial_walks=radial_witness,
                verified_children=len(ordered), verified_residual_pairs=len(edges),
                directed_turns=turns.number_of_edges(), cyclic_components=len(cyc),
                largest_cyclic_component=max(map(len,cyc),default=0), cycle=sample,
                longest_turn_path_if_acyclic=None if cyc else
                (nx.dag_longest_path_length(turns) if turns else 0))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cache", type=Path)
    parser.add_argument("start", type=int)
    parser.add_argument("age", type=int)
    parser.add_argument("--degree", type=int, default=256)
    parser.add_argument("--anchors", type=int, default=256)
    parser.add_argument("--limit", type=int, default=300)
    parser.add_argument("--incident", type=int, default=192)
    parser.add_argument("--shared", type=int, default=0)
    parser.add_argument("--pair-cap", type=int, default=16000)
    parser.add_argument("--multiple", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.cache, args.start, args.age, args.degree, args.anchors,
                 args.limit, args.incident, args.shared, args.pair_cap, args.multiple)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print({k: v for k, v in result.items() if k != "cycle"})
