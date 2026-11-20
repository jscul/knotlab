"""Four literal parity histories checking the held-ancestry proof boundaries."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path
import sys

import networkx as nx

from sources_span import labels, physical_words, qualify

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACTS = ROOT / "artifacts" / HERE.parent.name / HERE.name
sys.path.insert(0, str(ROOT / "experiments/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached"))
from verify import Arrangement, round_replay


def wired_start(opens, blocks):
    """Use a dead holder for each block and pad short live supports with singleton holders."""
    live = len(opens)
    meets = Counter(u for block in blocks for u in block)
    padded = list(blocks)
    for u in range(live):
        padded.extend([(u,)] * max(0, 3 - opens[u] - meets[u]))
    padded.extend([(0,)] * max(0, 2 - len(padded)))
    a, b = live + len(padded), live + len(padded) + 1
    links = [(a, b)]
    for hub, block in enumerate(padded, live):
        links.extend([(hub, a), (hub, b)])
        links.extend((u, hub) for u in block)
    links.sort()
    shared = Counter(u for pair in links for u in pair)
    sizes = [shared[u] + (opens[u] if u < live else 0) for u in range(b + 1)]
    assert qualify(sizes, links)["canonical"]
    words, _, _ = physical_words(sizes, links)
    return Arrangement.parse([labels(w) for w in words])


def groups_at(neighbors, live):
    """Generate unheld candidate maxima and then uncovered pairs."""
    held = {frozenset(points & live) for points in neighbors}
    pairs = {frozenset(pair) for points in held for pair in combinations(points, 2)}
    graph = nx.Graph()
    graph.add_nodes_from(sorted(live))
    graph.add_edges_from(sorted(tuple(sorted(pair)) for pair in pairs))
    big = [frozenset(c) for c in nx.find_cliques(graph) if len(c) >= 3 and not any(set(c) <= h for h in held)]
    residual = [p for p in pairs if not any(p <= c for c in big)]
    return sorted(big + residual, key=lambda g: tuple(sorted(g)))


def complete_round(stage):
    legal = groups_at(stage.neighbors, stage.live)
    used = Counter(u for group in legal for u in group)
    supply = defaultdict(list)
    for distinction, u in sorted(stage.loose.items()):
        supply[u].append(distinction)
    assert all(used[u] <= len(available) for u, available in supply.items())
    parents = legal + [frozenset((u,)) for u in sorted(supply) for _ in range(len(supply[u]) - used[u])]
    assert parents
    first = len(stage.stars)
    following_names = range(first, first + len(parents))
    links = [set(row) for row in stage.neighbors] + [set(p) for p in parents]
    for child, group in zip(following_names, parents, strict=True):
        for u in group:
            links[u].add(child)
    demand = Counter(u for group in groups_at(links, set(following_names)) for u in group)
    old_stars = [sorted(row) for row in stage.stars]
    fresh = max(stage.labels) + 1
    for child, group in zip(following_names, parents, strict=True):
        taken = [supply[u].pop() for u in sorted(group)]
        implied = len(taken) == len(stage.loose)
        count = demand[child] if implied else max(demand[child], 3 - len(group), 1)
        old_stars.append(taken + list(range(fresh, fresh + count)))
        fresh += count
    successor = Arrangement.parse(old_stars)
    expected = dict(zip(following_names, parents, strict=True))
    checked = round_replay(stage, successor)
    assert [frozenset(row["taken"]) for row in checked] == parents
    return successor, expected, {u for u, row in zip(following_names, checked, strict=True) if row["implied"]}


def source_start(arm_count, crossing):
    blocks = [(0, 1, 2)] if crossing else [(0, 1), (0, 2)]
    blocks.extend((0, u) for u in range(3, arm_count + 1))
    pairs = {frozenset(edge) for block in blocks for edge in combinations(block, 2)}
    opens = [sum(v in e for e in pairs) for v in range(arm_count + 1)]
    return wired_start(opens, blocks), pairs


def passed_checks(crossing, mark_all=False):
    start, original_pairs = source_start(4 if mark_all else 5, crossing)
    stage, actual_incoming, implied = complete_round(start)
    assert not implied and set(actual_incoming.values()) == original_pairs
    by_group = {group: u for u, group in actual_incoming.items()}
    mark = {by_group[frozenset((0, i))] for i in range(1, 5)}
    held = stage.neighbors[0] & stage.live
    assert mark == held if mark_all else mark < held

    pure = {u: frozenset((u,)) for u in mark}
    earlier_pure, residual, gap, outsider_overlap = {}, set(), None, None
    layers = [{"j": 1, "pure_births": len(pure), "pure_live": len(pure),
               "parents": {u: sorted(p) for u, p in actual_incoming.items()}}]
    current = stage
    for j in range(2, 6):
        nxt, children, terminal = complete_round(current)
        if j == 2:
            residual = {p for p in children.values() if len(p) == 2 and p <= mark}
        pair_uses = Counter(tuple(sorted(ab)) for p in children.values() for ab in combinations(p, 2))
        pure_children = {}
        for u, group in children.items():
            if group <= pure.keys():
                support = frozenset.union(*(pure[parent] for parent in group))
                assert len(support) == j and {pure[v] for v in group} == {support - {w} for w in support}
                assert all(pair_uses[tuple(sorted(ab))] == 1 for ab in combinations(group, 2))
                pure_children[u] = support
        expected = {frozenset(c) for c in combinations(sorted(mark), j)
                    if all(frozenset(e) in residual for e in combinations(c, 2))}
        assert len(expected) == len(pure_children) and expected == set(pure_children.values())
        if j == 4 and not (crossing or mark_all):
            hits = [(u, [v for v in sorted(pure) if parents & actual_incoming[v]])
                    for u, parents in actual_incoming.items() if u not in pure]
            assert max(len(v) for _, v in hits) == 2
            u, matched = min((u, v) for u, v in hits if len(v) == 2)
            outsider_overlap = {"outside_node": u, "parents": sorted(actual_incoming[u]),
                                "compatible_pure_facets": matched}
        if crossing and j == 4:
            a, b = sorted(pure)
            common, = actual_incoming[a] & actual_incoming[b]
            outsider = min(u for u, parents in actual_incoming.items()
                           if u not in pure and common not in parents and
                           parents & actual_incoming[a] and parents & actual_incoming[b])
            s = earlier_pure[common]
            p, q = (min(actual_incoming[v] & actual_incoming[outsider]) for v in (a, b))
            assert earlier_pure[p] & earlier_pure[q] and earlier_pure[p] | earlier_pure[q] != s
            group, = (u for u, parents in children.items() if {a, b, outsider} <= parents)
            assert len(children[group]) >= 3 and group not in pure_children
            gap = {"available_pure_nodes": [a, b], "their_unique_common_parent": common,
                   "outside_node": outsider, "outside_node_parents": sorted(actual_incoming[outsider]),
                   "shared_parents_with_the_two_pure_nodes": [p, q], "actual_covering_child": group,
                   "actual_covering_group": sorted(children[group])}
        layers.append({"j": j, "pure_births": len(pure_children), "pure_live": len(pure_children.keys() & nxt.live),
                       "implied_births": sorted(terminal), "parents": {u: sorted(p) for u, p in children.items()}})
        earlier_pure = pure
        pure, actual_incoming, current = {u: p for u, p in pure_children.items() if u in nxt.live}, children, nxt
        if not pure:
            break
    return {"source_supports": [sorted(w) for w in start.stars], "held_at_age_one": sorted(held),
            "marked_at_age_one": sorted(mark), "residual_pairs": sorted(sorted(p) for p in residual),
            "layers": layers, "missing_union_at_j4": gap, "outside_hits_at_j4": outsider_overlap}


def surplus_at_age_zero():
    start = wired_start([5, 4, 4, 4, 4], [(0, 1, 2, 3, 4)])
    _, births, _ = complete_round(start)
    chosen = {0, 1, 2, 3}
    unary = [u for u, p in births.items() if p <= chosen and len(p) == 1]
    assert len(unary) == 1 and births[unary[0]] == {0}
    return {"source_supports": [sorted(w) for w in start.stars], "mark": sorted(chosen),
            "pure_unary_child": unary[0], "parents": {u: sorted(p) for u, p in births.items()}}


def run():
    complete = passed_checks(False)
    crossing = passed_checks(True)
    whole = passed_checks(False, mark_all=True)
    assert [r["pure_births"] for r in complete["layers"]] == [4, 6, 4, 1, 0]
    assert [r["pure_births"] for r in crossing["layers"]] == [4, 5, 2, 0]
    assert [r["pure_live"] for r in whole["layers"]] == [4, 6, 4, 0]
    assert [r["pure_births"] for r in whole["layers"]] == [4, 6, 4, 1]
    return {"proper_complete": complete, "one_missing_residual_pair": crossing,
            "whole_component_terminal": whole, "age_zero_surplus_exception": surplus_at_age_zero()}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ARTIFACTS / "sources_shield_check.json")
    args = parser.parse_args()
    result = run()
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: [r["pure_births"] for r in v["layers"]] for k, v in result.items() if "layers" in v}))


if __name__ == "__main__":
    main()
