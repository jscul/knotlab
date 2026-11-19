"""Check a compact witness directly from its literal junctions and permutation."""

import argparse
from collections import defaultdict
from itertools import combinations
import json
from pathlib import Path


def connected(shore, neighbors):
    seen = shore & -shore
    frontier = seen
    while frontier:
        head = frontier & -frontier
        frontier ^= head
        new = neighbors[head.bit_length() - 1] & shore & ~seen
        seen |= new
        frontier |= new
    return seen == shore


def check(witness, order):
    rows = witness["support_history"][1]
    outside = len(rows)
    holders = defaultdict(list)
    for junction, row in enumerate(rows):
        for name in row:
            holders[name].append(junction)
    classes = defaultdict(list)
    for name, endpoints in holders.items():
        if len(endpoints) == 1:
            endpoints.append(outside)
        assert len(endpoints) == 2
        classes[tuple(endpoints)].append(name)
    class_names = list(classes.values())
    indices = {name: i for i, names in enumerate(class_names) for name in names}
    permutation = dict(witness["map"])
    images = []
    for names in class_names:
        target = {indices[permutation[name]] for name in names}
        assert len(target) == 1
        images.append(target.pop())
    neighbors = [0] * (outside + 1)
    incidences = [0] * (outside + 1)
    weights = []
    for index, ((u, v), names) in enumerate(classes.items()):
        neighbors[u] |= 1 << v
        neighbors[v] |= 1 << u
        incidences[u] |= 1 << index
        incidences[v] |= 1 << index
        weights.append(len(names))

    all_vertices = (1 << (outside + 1)) - 1
    cuts = [0] * (1 << outside)
    bonds = []
    for shore in range(1, 1 << outside):
        head = shore & -shore
        cut = cuts[shore ^ head] ^ incidences[head.bit_length() - 1]
        cuts[shore] = cut
        if connected(shore, neighbors) and connected(all_vertices ^ shore, neighbors):
            cost = sum(w for i, w in enumerate(weights) if cut & (1 << i))
            bonds.append((cost, cut))
    bonds.sort()
    byte_size = (len(bonds) + 7) // 8
    masks = [bytearray(byte_size) for _ in classes]
    for index, (_, cut) in enumerate(bonds):
        while cut:
            head = cut & -cut
            cut ^= head
            masks[head.bit_length() - 1][index // 8] |= 1 << (index % 8)
    through = [int.from_bytes(mask, "little") for mask in masks]
    every_bond = (1 << len(bonds)) - 1

    def minimum(mark):
        available = every_bond
        for i in mark:
            available &= through[i]
        if not available:
            return None
        return bonds[(available & -available).bit_length() - 1][0]

    counts = {}
    for size in range(1, order + 1):
        count = 0
        for mark in combinations(range(len(classes)), size):
            image = tuple(sorted(images[i] for i in mark))
            if mark < image:
                assert minimum(mark) == minimum(image), mark
            count += 1
        counts[size] = count
    exposed = witness["discrepancy"]
    old = exposed["old_mark"]
    assert len(set(old)) == order + 1
    readings = [minimum([indices[x] for x in old]),
                minimum([indices[permutation[x]] for x in old])]
    assert readings == [None, exposed["image_K"]]
    return {"order": order, "junctions": outside, "distinctions": len(holders),
            "bond_count": len(bonds), "holder_classes": len(classes),
            "all_class_sets_by_size": counts, "old_readings": readings}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("histories", type=Path)
    cli.add_argument("output", type=Path)
    args = cli.parse_args()
    histories = json.loads(args.histories.read_text())
    result = [check(row["least_junctions_in_formula"], row["preserved_order"])
              for row in histories if row["preserved_order"] <= 4]
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
