"""Replay the funded retraction witness using literal parity supports and the roster rule."""

from collections import Counter
from itertools import combinations, product
import json
from pathlib import Path
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(next((ROOT / 'proofs/WALL-READ-20261119-001A').glob('*-P001_partnered'))))
sys.path.insert(0, str(next((ROOT / 'experiments/GROWN-END-SWAP-20261119-001').glob('*-E001_reached'))))
import rosterlib
import verify


def listed(family):
    return sorted(sorted(block) for block in family)


def precursor():
    target_groups = [frozenset(t) for t in product((0, 1), (2, 3), (4, 5))]
    target_blocks = {frozenset((u, v)) for u, v in combinations(range(6), 2) if u // 2 != v // 2}
    desired = [t | {6 + i} if 0 in t else t for i, t in enumerate(target_groups)]
    desired.append(frozenset(range(6, 11)))

    graph = nx.Graph()
    for parents in desired:
        graph.add_edges_from(combinations(sorted(parents), 2))
    maximal = {frozenset(clique) for clique in nx.find_cliques(graph)}
    assert set(desired) <= maximal
    # Every candidate pair belongs to a requested group. Hold every other maximal clique.
    pairs = {frozenset(pair) for pair in graph.edges}
    source_blocks = verify.maximal_sets((maximal - set(desired)) | pairs)
    return target_blocks, target_groups, source_blocks, desired


def literal_start(blocks, opens):
    """One dead hub per maximal block. A cycle through those hubs connects the assembly."""
    blocks = listed(blocks)
    first_hub = len(opens)
    stars = [[] for _ in range(first_hub + len(blocks))]
    meetings = [(v, first_hub + i) for i, block in enumerate(blocks) for v in block]
    meetings.extend((first_hub + i, first_hub + (i + 1) % len(blocks)) for i in range(len(blocks)))
    for name, (u, v) in enumerate(meetings):
        stars[u].append(name)
        stars[v].append(name)
    name = len(meetings)
    for v, count in enumerate(opens):
        stars[v].extend(range(name, name + count))
        name += count
    stage = verify.Arrangement.parse(stars)
    audit = verify.start_audit(stage)
    assert audit['census_open_legal'] and audit['meets_once']
    read_opens, read_blocks = rosterlib.roster_of([len(s) for s in stars], meetings)
    assert read_opens == opens and listed(read_blocks) == blocks
    return stage, audit


def born(previous, parents):
    """Construct actual new supports in the specified order and replay them independently."""
    loose = {v: sorted(x for x, holder in previous.loose.items() if holder == v) for v in previous.live}
    assert Counter(v for group in parents for v in group) == Counter({v: len(xs) for v, xs in loose.items()})
    assert set(parents) == verify.groups(previous.neighbors, previous.live)
    children = range(len(previous.stars), len(previous.stars) + len(parents))
    blocks = rosterlib.maximal_blocks({i for i, group in zip(children, parents) if v in group} for v in loose)
    next_groups = rosterlib.groups_of(children, blocks)
    demand = Counter(i for members in next_groups for i in members)
    stars = [sorted(star) for star in previous.stars]
    name = max(previous.labels) + 1
    for j, group in zip(children, parents):
        taken = [loose[v].pop() for v in sorted(group)]
        count = max(demand[j], 3 - len(group), 1)
        stars.append(taken + list(range(name, name + count)))
        name += count
    following = verify.Arrangement.parse(stars)
    checked = verify.round_replay(previous, following)
    assert all(not r['implied'] and r['fresh'] for r in checked)
    return following, list(children)


def live_blocks(stage):
    family = verify.common_meeters(stage.neighbors, stage.live)
    return verify.maximal_sets({b for b in family if len(b) >= 2})


def verify_retraction(source_blocks, target_blocks, mapping, section):
    assert set(mapping.values()) == set(section)
    assert all(mapping[s] == t for t, s in section.items())
    images = [frozenset(mapping[v] for v in block) for block in source_blocks]
    assert all(any(image <= b for b in target_blocks) for image in images)
    restrictions = {frozenset(mapping[p] for p in b if p in section.values()) for b in source_blocks}
    assert verify.maximal_sets({b for b in restrictions if len(b) >= 2}) == target_blocks
    return listed(images)


def counts(opens, blocks, last):
    result = []
    for record in rosterlib.grow(opens, blocks, last):
        assert 'end' not in record
        if 'count' in record:
            assert record['offshoots'] == 0
            result.append(record['count'])
            if len(result) == last:
                break  # No following target demands need to be materialized.
    return result


def positive_realization(blocks, requested_opens):
    """One exact round from a legal connected start to the requested funded roster."""
    original = listed(blocks)
    private = len(original)
    desired = []
    for v in range(len(requested_opens)):
        holders = {i for i, block in enumerate(original) if v in block}
        desired.append(frozenset(holders | set(range(private, private + 3))))
        private += 3
    graph = nx.Graph()
    for group in desired:
        graph.add_edges_from(combinations(group, 2))
    maximal = {frozenset(c) for c in nx.find_cliques(graph)}
    assert set(desired) <= maximal
    blocks_before = verify.maximal_sets((maximal - set(desired)) | {frozenset(pair) for pair in graph.edges})
    use = Counter(v for group in desired for v in group)
    before, audit = literal_start(blocks_before, [use[i] for i in range(private)])
    after, children = born(before, desired)
    recovered = {frozenset(children.index(v) for v in b) for b in live_blocks(after)}
    assert recovered == blocks
    opens = Counter(after.loose.values())
    assert [opens[v] for v in children] == requested_opens
    return dict(before_junctions=len(before.stars), before_distinctions=len(before.labels),
                after_junctions=len(after.stars), after_distinctions=len(after.labels),
                live_children=len(children), recovered_open_counts=requested_opens, start_audit=audit)


def main():
    target_blocks, target_parents, source_blocks, source_parents = precursor()
    source_demand = Counter(v for group in source_parents for v in group)
    source_opens = [source_demand[v] for v in range(11)]
    target_opens = [4] * 6
    assert source_opens == [4] * 6 + [2] * 4 + [1]
    target0, target_audit = literal_start(target_blocks, target_opens)
    source0, source_audit = literal_start(source_blocks, source_opens)
    mapping0 = {v: v if v < 6 else 0 for v in range(11)}
    images0 = verify_retraction(live_blocks(source0), live_blocks(target0), mapping0, {v: v for v in range(6)})

    source1, source_names = born(source0, source_parents)
    target1, target_names = born(target0, target_parents)
    section1 = dict(zip(target_names, source_names[:8]))
    mapping1 = {s: t for t, s in section1.items()}
    extra = source_names[8]
    mapping1[extra] = target_names[0]
    images1 = verify_retraction(live_blocks(source1), live_blocks(target1), mapping1, section1)
    held = frozenset(target_names[:4])
    assert held in live_blocks(target1)
    true_source_groups = verify.groups(source1.neighbors, source1.live)
    true_target_groups = verify.groups(target1.neighbors, target1.live)
    extra_group = frozenset(source_names[:4]) | {extra}
    assert extra_group in true_source_groups
    assert frozenset(mapping1[v] for v in extra_group) == held
    assert all(not held <= g for g in true_target_groups)
    mapped_target_groups = [frozenset(section1[v] for v in g) for g in sorted(true_target_groups, key=sorted)]
    assert true_source_groups == set(mapped_target_groups) | {extra_group}

    source2, second_names = born(source1, [*mapped_target_groups, extra_group])
    universal = second_names[-1]
    third_parents = verify.groups(source2.neighbors, source2.live)
    assert len(third_parents) == 28 and all(len(g) == 6 and universal in g for g in third_parents)
    source3, third_names = born(source2, sorted(third_parents, key=sorted))
    assert live_blocks(source3) == {frozenset(third_names)}
    assert Counter(source3.loose.values()) == {j: 27 for j in third_names}
    fourth_parents = verify.groups(source3.neighbors, source3.live)
    assert len(fourth_parents) == 378 and all(len(g) == 2 for g in fourth_parents)
    assert counts(source_opens, source_blocks, 4) == [9, 11, 28, 378]
    assert counts(target_opens, target_blocks, 4) == [8, 10, 24, 4086]

    double_opens = target_opens * 2
    double_blocks = target_blocks | {frozenset(v + 6 for v in b) for b in target_blocks}
    double_start, double_audit = literal_start(double_blocks, double_opens)
    both_parents = [*target_parents, *(frozenset(v + 6 for v in group) for group in target_parents)]
    double1, double_names = born(double_start, both_parents)
    # The orientation through the first original partner pair picks T_i from each complementary pair.
    complement_color = [0, 1, 2, 3, 3, 2, 1, 0]
    double_map = dict(zip(double_names[:8], target_names))
    double_map.update((v, target_names[color]) for v, color in zip(double_names[8:], complement_color))
    verify_retraction(live_blocks(double1), live_blocks(target1), double_map, dict(zip(target_names, double_names)))
    assert all(len(set(double_map[v] for v in b)) == len(b) for b in live_blocks(double1))
    side_groups = [g for g in verify.groups(double1.neighbors, double1.live) if g <= set(double_names[8:])]
    assert len(side_groups) == 10 and all({double_map[v] for v in g} == held for g in side_groups)

    return dict(
        source_start=dict(junctions=len(source0.stars), distinctions=len(source0.labels),
                          stars=[sorted(s) for s in source0.stars], audit=source_audit,
                          blocks=listed(source_blocks), open_counts=source_opens, groups=listed(source_parents),
                          block_images=images0),
        target_start=dict(junctions=len(target0.stars), distinctions=len(target0.labels),
                          stars=[sorted(s) for s in target0.stars], audit=target_audit,
                          blocks=listed(target_blocks), open_counts=target_opens, groups=listed(target_parents)),
        start_map=[mapping0[v] for v in range(11)],
        age_one=dict(source_to_target=sorted(mapping1.items()), target_to_source=sorted(section1.items()),
                     source_open_counts=[Counter(source1.loose.values())[v] for v in source_names],
                     target_open_counts=[Counter(target1.loose.values())[v] for v in target_names],
                     source_block_images=images1, source_group=sorted(extra_group), held_image=sorted(held)),
        source_populations=[9, 11, 28, 378], target_populations=[8, 10, 24, 4086],
        common_block_size=len(third_names), first_strict_deficit_absolute_age=4,
        positive_age_realization_of_both_initial_rosters=dict(
            source=positive_realization(source_blocks, source_opens),
            target=positive_realization(target_blocks, target_opens)),
        proper_map_control=dict(positive_age=1, start_audit=double_audit,
                                one_copy_groups_with_held_image=len(side_groups),
                                source_count=2 * len(side_groups), target_count=len(true_target_groups)))


if __name__ == '__main__':
    result = main()
    (HERE / 'retraction_check.json').write_text(json.dumps(result, indent=1) + '\n')
    print('source', result['source_populations'], 'target', result['target_populations'])
