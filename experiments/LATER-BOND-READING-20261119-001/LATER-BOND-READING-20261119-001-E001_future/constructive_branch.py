"""Replay the compact M-to-one branch with the committed complete-round rule."""

import argparse
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "constructive_branch.json"
ENGINE = ROOT / "experiments/EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend/extend.py"


def attach_branches(price, stars, roots):
    stars = [set(star) for star in stars]
    labels = []
    next_bit = max(max(star) for star in stars) + 1

    def add_bit(*owners):
        nonlocal next_bit
        for u in owners:
            stars[u].add(next_bit)
        next_bit += 1

    def add_site():
        stars.append(set())
        return len(stars) - 1

    for root in roots:
        a, c = add_site(), add_site()
        middle = [add_site() for _ in range(price - 1)]
        labels.append((root, a, c, middle))
        add_bit(root, a)
        for b in middle:
            add_bit(root, b)
            add_bit(c, b)
            add_bit(b)
            add_bit(b)
        for u, v in zip(middle, middle[1:]):
            add_bit(u, v)
        for _ in middle:
            add_bit(a)
        add_bit(c)
    return [frozenset(star) for star in stars], labels


def screened_core(anchors, shields, test_weight, shield_weight):
    # Fixed order is R, B, the anchors (v first), then the special and shield middles.
    first_middle = 2 + anchors
    stars = [set() for _ in range(first_middle + 4 + 2 * shields)]
    next_bit = 0

    def bundle(u, v, count):
        nonlocal next_bit
        for name in range(next_bit, next_bit + count):
            stars[u].add(name)
            stars[v].add(name)
        next_bit += count

    for j in range(4 + 2 * shields):
        u = first_middle + j
        special = j < 4
        blue = j >= 2 if special else j >= 4 + shields
        bundle(u, int(blue), test_weight if special else shield_weight)
        bundle(u, 2, test_weight if special else 1)
        for weak in range(3, first_middle):
            bundle(u, weak, 1)
    roots = range(first_middle + 4, len(stars))
    return stars, roots


def holders(stars):
    owners = defaultdict(list)
    for u, star in enumerate(stars):
        for name in star:
            owners[name].append(u)
    return owners


def actual_additions(old, new):
    old_owners = holders(old)
    assert new[:len(old)] == old
    result = {}
    for u in range(len(old), len(new)):
        taken = new[u] & old_owners.keys()
        assert all(len(old_owners[name]) == 1 for name in taken)
        parents = frozenset(old_owners[name][0] for name in taken)
        assert len(taken) == len(parents)
        assert len(new[u] - taken) == 1
        assert parents not in result
        result[parents] = u
    return result


def wired(stars, selected):
    graph = nx.Graph()
    for ends in holders(stars).values():
        if any(u not in selected for u in ends):
            continue
        u, v = ends if len(ends) == 2 else (ends[0], "outside")
        if not graph.has_edge(u, v):
            graph.add_edge(u, v, capacity=0)
        graph[u][v]["capacity"] += 1
    return graph


def literal_matching(stars, anchors, test_weight, shield_weight):
    block = 2 * test_weight + anchors - 1

    def rename(x):
        if x < block:
            return x + 2 * block
        if 2 * block <= x < 3 * block:
            return x - 2 * block
        return x

    owners = holders(stars)
    live = {ends[0] for ends in owners.values() if len(ends) == 1}
    assert all(rename(x) == x for u in live for x in stars[u])
    basis = {}

    def reduce_word(row):
        while row and row.bit_length() in basis:
            row ^= basis[row.bit_length()]
        return row

    for star in stars:
        row = reduce_word(sum(1 << x for x in star))
        if row:
            basis[row.bit_length()] = row
    assert reduce_word(sum(1 << rename(x) for x in stars[0]))
    assert len(basis) == len(stars)
    special = 2 + anchors
    first_blue = special + 2
    first_shield = special + 4
    pair = [0, block]
    four = [4 * block, 4 * block + shield_weight, 2 * block + test_weight, 2 * block + 2 * test_weight]
    assert [set(owners[x]) for x in pair] == [{0, special}, {0, special + 1}]
    assert [set(owners[x]) for x in four] == [
        {0, first_shield}, {2, first_shield}, {2, first_blue}, {3, first_blue},
    ]
    return {
        "permutation": f"Swap names 0 through {block - 1} with {2 * block} through {3 * block - 1}, in order. Fix all other names.",
        "actual_pointwise_fixed_live_sites": len(live),
        "current_equation_rank": len(basis),
        "red_hub_equation_image_in_current_span": False,
        "later_old_pair_and_image": [pair, list(map(rename, pair))],
        "current_four_and_image": [four, list(map(rename, four))],
    }


def replay(grow, price, core, named=False):
    start, labels = attach_branches(price, *core)
    current = grow(start)
    after = grow(current)
    first = actual_additions(start, current)
    second = actual_additions(current, after)
    assert len(first) == len(labels) * price and len(second) == len(labels)
    measured = []
    for root, a, c, middle in labels:
        parents = [frozenset((a, b)) for b in middle]
        parents.append(frozenset([c, *middle]))
        live = frozenset(first[p] for p in parents)
        final = second[live]
        branch = {root, a, c, *middle, *live}
        current_price = nx.minimum_cut_value(wired(current, branch), root, "outside")
        next_price = nx.minimum_cut_value(wired(after, branch | {final}), root, "outside")
        assert (current_price, next_price) == (price, 1)
        measured.append([current_price, next_price])

    for stars in (start, current, after):
        ordinary = set(range(len(stars)))
        graph = wired(stars, ordinary)
        assert all(len(star) >= 3 for star in stars)
        assert all(u == "outside" for u in nx.articulation_points(graph))
        assert all(graph[u][v]["capacity"] > 1 for u, v in nx.bridges(graph))
    record = {
        "M": price,
        "ordinary_sites_start_current_next": [len(stars) for stars in (start, current, after)],
        "distinctions_start_current_next": [len(holders(stars)) for stars in (start, current, after)],
        "literal_current_parent_sizes_per_branch": sorted([2] * (price - 1) + [price]),
        "literal_next_parent_size_per_branch": price,
        "fresh_per_new_site_in_each_round": 1,
        "measured_branches": len(measured),
        "two_terminal_price_pair_on_every_branch": measured[0],
    }
    if named:
        record["literal_matching"] = literal_matching(current, 2, 17, 9)
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("constructive_archived_round", ENGINE)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    data = {
        "engine": str(ENGINE.relative_to(ROOT)),
        "scope": "The controls use two separate branches with their roots joined by one ordinary distinction. The full-screen replay uses all 22 branches of the two-anchor example. In each case all loose ends share one outside.",
        "two_branch_cases": [replay(engine.grow1, price, ([{0}, {0}], [0, 1])) for price in (3, 4, 9)],
        "full_two_anchor_case": replay(engine.grow1, 9, screened_core(2, 11, 17, 9), named=True),
    }
    encoded = json.dumps(data, indent=2) + "\n"
    if args.check:
        if OUT.read_text() != encoded:
            raise SystemExit("saved branch replay differs")
    else:
        OUT.write_text(encoded)
    print("The complete-round replay gives the expected parents, one fresh per site, and terminal costs 3/4/9 to one.")
