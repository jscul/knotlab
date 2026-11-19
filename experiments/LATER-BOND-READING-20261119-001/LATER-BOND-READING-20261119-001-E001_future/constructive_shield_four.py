"""Exact bonds for selected hub-spoke queries by permutation orbits of shores."""

import argparse
import itertools
import json
from pathlib import Path


def weighted_core(anchors, shields, test_weight, shield_weight, outside_weight):
    weak = [f"w{i}" for i in range(anchors - 1)]
    groups = [
        ["a", "b"],
        ["c", "d"],
        [f"r{i}" for i in range(shields)],
        [f"b{i}" for i in range(shields)],
    ]
    nodes = ["O", "R", "B", "v", *weak, *itertools.chain.from_iterable(groups)]
    index = {name: i for i, name in enumerate(nodes)}
    adjacency = [0] * len(nodes)
    links = []

    def add(u, v, weight):
        i, j = index[u], index[v]
        adjacency[i] |= 1 << j
        adjacency[j] |= 1 << i
        links.append((i, j, weight))

    for kind, members in enumerate(groups):
        special = kind < 2
        hub = "R" if kind % 2 == 0 else "B"
        for middle in members:
            add(middle, hub, test_weight if special else shield_weight)
            add(middle, "v", test_weight if special else 1)
            for w in weak:
                add(middle, w, 1)
            if not special:
                add(middle, "O", outside_weight)
    return nodes, index, weak, groups, adjacency, links


def connected(side, adjacency):
    if not side:
        return False
    seen = pending = side & -side
    while pending:
        reached = pending & -pending
        pending ^= reached
        new = side & adjacency[reached.bit_length() - 1] & ~seen
        seen |= new
        pending |= new
    return seen == side


def minimum(core, marked):
    nodes, index, weak, groups, adjacency, links = core
    all_nodes = (1 << len(nodes)) - 1
    marks = {}
    for middle, endpoint in marked:
        marks.setdefault(middle, []).append(endpoint)
    marked_weak = [w for w in weak if any(w in endpoints for endpoints in marks.values())]
    unmarked_weak = [w for w in weak if w not in marked_weak]
    results = {}
    for hub_r, hub_b in itertools.product(range(2), repeat=2):
        best = None
        outer_assignments = itertools.product(
            range(2), itertools.product(range(2), repeat=len(marked_weak)),
            range(len(unmarked_weak) + 1),
        )
        for v, fixed_weak, nweak in outer_assignments:
            outer = [w for w, positive in zip(marked_weak, fixed_weak) if positive]
            outer += unmarked_weak[:nweak]
            for name, positive in [("R", hub_r), ("B", hub_b), ("v", v)]:
                if positive:
                    outer.append(name)
            forced = {m: {end in outer for end in ends} for m, ends in marks.items()}
            if any(len(values) != 1 for values in forced.values()):
                continue
            options = []
            for group in groups:
                positive = [m for m in group if forced.get(m) == {False}]
                other = [m for m in group if m not in forced]
                options.append([positive + other[:k] for k in range(len(other) + 1)])
            for positives in itertools.product(*options):
                members = outer + list(itertools.chain.from_iterable(positives))
                side = sum(1 << index[name] for name in members)
                cost = sum(weight for i, j, weight in links if ((side >> i) ^ (side >> j)) & 1)
                if best and cost >= best["minimum"]:
                    continue
                if connected(side, adjacency) and connected(all_nodes ^ side, adjacency):
                    best = {"minimum": cost, "shore": sorted(members)}
        results[f"red{hub_r}_blue{hub_b}"] = best
    allowed = [val["minimum"] for val in results.values() if val]
    return {"minimum": min(allowed) if allowed else None, "by_hub_sides": results}


def build(anchors, shields, test_weight, shield_weight):
    record = {
        "parameters": {
            "anchors_including_v": anchors, "shields_per_color": shields,
            "test_weight": test_weight, "shield_weight": shield_weight,
        },
        "scope": "All shores up to permutations of unmarked middles of each type and unmarked weak anchors. O is outside the listed shore.",
        "mark_convention": "Each pair marks one direct distinction between its middle and its named outer endpoint. The map interchanges a and c and their respective spoke types.",
    }
    r_spokes = [[f"r{i}", "R"] for i in range(3)]
    examples = [
        ("current_four", shield_weight, [["a", "R"], *r_spokes], [["c", "B"], *r_spokes]),
        ("later_pair", 1, [["a", "R"], ["b", "R"]], [["c", "B"], ["b", "R"]]),
    ]
    if anchors == 2:
        common = [["r0", "R"], ["r0", "v"]]
        examples.append((
            "current_four_existence", shield_weight,
            [*common, ["c", "v"], ["c", "w0"]], [*common, ["a", "v"], ["a", "w0"]],
        ))
    if anchors == 1:
        common = [["r0", "R"], ["r0", "v"]]
        examples.append((
            "current_three_existence", shield_weight,
            [*common, ["c", "v"]], [*common, ["a", "v"]],
        ))
    for name, price, source, image in examples:
        core = weighted_core(anchors, shields, test_weight, shield_weight, price)
        record[name] = {
            "source_marks": source, "image_marks": image,
            "source": minimum(core, source), "image": minimum(core, image),
        }
    if anchors in (1, 2):
        name = "current_three_existence" if anchors == 1 else "current_four_existence"
        expected = 2 * test_weight + shields * shield_weight + anchors * shields + 2 * anchors - 1
        assert record[name]["source"]["minimum"] == expected
        assert record[name]["image"]["minimum"] is None
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anchors", type=int, default=5)
    parser.add_argument("--shields", type=int, default=7)
    parser.add_argument("--test-weight", type=int, default=22)
    parser.add_argument("--shield-weight", type=int, default=28)
    parser.add_argument("--check", type=Path)
    parsed = parser.parse_args()
    if parsed.anchors < 1 or parsed.shields < 3 or min(parsed.test_weight, parsed.shield_weight) < 1:
        parser.error("the selected queries require an anchor, three shields and positive integer weights")
    result = build(parsed.anchors, parsed.shields, parsed.test_weight, parsed.shield_weight)
    if parsed.check:
        if json.loads(parsed.check.read_text()) != result:
            raise SystemExit("saved record differs")
        print("Selected bond minima agree with the saved record.")
    else:
        print(json.dumps(result, indent=2))
