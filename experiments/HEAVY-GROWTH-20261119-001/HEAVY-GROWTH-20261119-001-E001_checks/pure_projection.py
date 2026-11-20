"""Check two explicit projection hypotheses on the reached age-eight stages."""

import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx

from pure_turns import ART, HUB, automaton, exact_small_groups, file_for, members, signatures

sys.path.insert(0, str(HUB))
from group_profile import Stage


def old_hood(stage, vertex):
    return stage.hood(stage.at[vertex]) | (1 << vertex)


def private_parents(stage, degrees):
    sizes = [mask.bit_count() for mask in stage.blocks]
    minima = [min(degrees[v] for v in members(mask)) for mask in stage.blocks]
    counts = Counter()
    rejected = []
    witnesses = []
    for p, owners in enumerate(stage.at):
        degree = degrees[p]
        if degree < 2:
            counts["degree_below_two"] += 1
            continue
        if any(sizes[i] == degree + 1 for i in owners):
            counts["closed_neighborhood_is_a_holding_block"] += 1
            continue
        if min(minima[i] for i in owners) < degree:
            counts["neighbor_has_smaller_degree"] += 1
            continue
        closed = old_hood(stage, p)
        assert closed.bit_count() == degree + 1
        for x in members(closed):
            missed = closed & ~old_hood(stage, x)
            if missed:
                y = (missed & -missed).bit_length() - 1
                assert x != y and not set(stage.at[x]).intersection(stage.at[y])
                rejected.append([p, x, y])
                break
        else:
            witnesses.append(p)
    assert sum(counts.values()) + len(rejected) + len(witnesses) == stage.n
    return dict(filters=dict(counts), remaining_rejected_point_and_two_incompatible_neighbors=rejected,
                private_parents_of_large_births=witnesses)


def twin_quotient(stage, degrees):
    # This small signature only rejects distinct neighborhoods. Every remaining
    # match is resolved by equality of the full physical neighborhood bitsets.
    sample = list(range(0, stage.n, max(1, stage.n // 1800)))
    projection = [0] * len(stage.blocks)
    for k, x in enumerate(sample):
        for b in stage.at[x]:
            projection[b] |= 1 << k
    tentative = defaultdict(list)
    for v, holders in enumerate(stage.at):
        signature = 0
        for b in holders:
            signature |= projection[b]
        tentative[degrees[v], signature].append(v)
    classes = []
    for group in tentative.values():
        if len(group) == 1:
            classes.append(group)
        else:
            exact = defaultdict(list)
            for v in group:
                exact[old_hood(stage, v)].append(v)
            classes.extend(exact.values())
    ids = {v: i for i, group in enumerate(classes) for v in group}
    candidates = defaultdict(list)
    block_hist = Counter()
    for j, block in enumerate(stage.blocks):
        types = set()
        for v in members(block):
            types.add(ids[v])
            if len(types) == 3:
                break
        block_hist[len(types)] += 1
        if len(types) == 2:
            candidates[tuple(sorted(types))].append(j)
    rows = []
    for (i, j), holders in candidates.items():
        p, q = classes[i][0], classes[j][0]
        union = sum(1 << v for v in classes[i] + classes[j])
        further = old_hood(stage, p) & old_hood(stage, q) & ~union
        held = [b for b in holders if not union & ~stage.blocks[b]]
        rows.append(dict(physical_representatives=[p, q], class_sizes=[len(classes[i]), len(classes[j])],
                         two_class_holding_blocks=holders, held_entire_union_by=held,
                         further_common_sites=further.bit_count(),
                         example_further_common_site=next(members(further), None)))
    return dict(physical_classes=len(classes), class_size_histogram=dict(sorted(Counter(map(len, classes)).items())),
                holding_blocks_touching_one_two_or_at_least_three_classes=dict(block_hist),
                possible_bare_pairs=rows)


def unheld_cone(stage, name):
    # Fixed witnesses found among every 1/180 of the physical roster.
    if name == "start-03":
        rim, apex = (0, 8419, 9822, 24167), 9510
    else:
        rim, apex = (0, 2705, 18037, 29761), 54112
    supporting = {v: set(stage.at[v]) for v in (*rim, apex)}
    assert min(map(len, supporting.values())) >= 3
    assert not supporting[rim[0]] & supporting[rim[2]]
    assert not supporting[rim[1]] & supporting[rim[3]]
    faces = []
    for a, b in zip(rim, rim[1:] + rim[:1]):
        pair = supporting[a] & supporting[b]
        assert pair and supporting[a] & supporting[apex] and supporting[b] & supporting[apex]
        assert not pair & supporting[apex]
        faces.append(dict(rim_pair=[a, b], common_blocks_of_rim_pair=sorted(pair),
                          example_blocks_for_first_and_second_cone_meetings=[
                              min(supporting[a] & supporting[apex]), min(supporting[b] & supporting[apex])]))
    return dict(rim=rim, cone=apex, numbers_of_incident_holding_blocks={
        v: len(holders) for v, holders in supporting.items()}, four_unheld_faces=faces)


def test_stage(name, meta, folder):
    blocks = file_for(folder, meta[name, 8], "blocks")
    degrees_file = file_for(folder, meta[name, 8], "degrees")
    with gzip.open(degrees_file, "rt") as stream:
        degrees = json.load(stream)
    stage = Stage(blocks)
    assert len(degrees) == stage.n
    return dict(live=stage.n, blocks=len(stage.blocks), stage_sha256=hashlib.sha256(blocks.read_bytes()).hexdigest(),
                private=private_parents(stage, degrees), twins=twin_quotient(stage, degrees),
                actual_unheld_cone=unheld_cone(stage, name))


def control():
    # Four outer sites of a cycle, one common cone site, a private point
    # on each rim pair, and the single-candidate funded tip at the cone.
    w, tip = 4, 9
    blocks = [(w, tip)]
    private = []
    for i in range(4):
        j, p = (i + 1) % 4, 5 + i
        blocks.extend([(w, i, j), (i, p), (j, p)])
        private.append(frozenset((i, j, p)))
    base, residual = exact_small_groups(10, blocks)
    old = automaton(signatures(blocks, 10), residual)
    assert nx.is_directed_acyclic_graph(old) and all(w in edge for edge in residual)
    assert set(g for g in base if len(g) >= 3) == set(private)
    # Fund the old tip by two, all other sites by exact actual demand.
    children = base + [frozenset((tip,))]
    new_blocks = [[i for i, g in enumerate(children) if v in g] for v in range(10)]
    _, next_residual = exact_small_groups(len(children), new_blocks)
    new = automaton(signatures(new_blocks, len(children)), next_residual)
    ring = [children.index(g) for g in private]
    states = list(zip(ring, ring[1:] + ring[:1]))
    assert all(new.has_edge(x, y) for x, y in zip(states, states[1:] + states[:1]))
    assert all(sum(v in g for g in children) == 1 for v in range(5, 9))
    return dict(old_blocks=blocks, open_counts=[sum(x in g for g in children) for x in range(10)],
                private_larger_rosters=[sorted(g) for g in private], old_residual_pairs=sorted(residual),
                initial_residual_turn_graph_acyclic=True, new_residual_turn_cycle=ring,
                all_children_including_offshoot=[sorted(g) for g in children])


def run(folder):
    meta = {(r["case"], r["age"]): r for r in json.loads((ART / "stages.json").read_text())["stages"]}
    with gzip.open(file_for(folder, meta["start-13", 6], "parents"), "rt") as stream:
        parents = json.load(stream)
    uses = Counter(x for row in parents for x in row)
    reuse = {i: min(uses[x] for x in parents[i]) for i in (85, 105, 178, 179, 824)}
    return dict(stages={tag: test_stage(tag, meta, folder) for tag in ("start-03", "start-14")},
                higher_arity_positive_control=control(), start13_minimum_use_of_each_carrier_sites_parents=reuse)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exports", type=Path, default=Path("/var/tmp/hub-sample-20261119"))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    raw = json.dumps(run(args.exports), indent=2) + "\n"
    if args.out:
        args.out.write_text(raw)
    else:
        print(raw, end="")
