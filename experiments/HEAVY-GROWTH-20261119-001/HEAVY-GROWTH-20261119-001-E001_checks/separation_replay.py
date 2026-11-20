"""Replay archive supports and metric witnesses through literal incidences."""

import argparse
import hashlib
import itertools
import json
import operator
from functools import reduce
from pathlib import Path


def load(path, digest):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest:
        raise AssertionError(f"literal input mismatch for {path.name}")
    header, *lines = raw.splitlines()
    n, block_count = map(int, header.split())
    if len(lines) != block_count:
        raise AssertionError("invalid block family")
    blocks = [list(map(int, line.split())) for line in lines]
    incidence = [[] for _ in range(n)]
    masks = [0] * n
    for k, block in enumerate(blocks):
        flag = 1 << k
        for v in block:
            incidence[v].append(k)
            masks[v] |= flag
    return blocks, incidence, masks


def closure(blocks, incidence, source, depth=None, target=None):
    reached = set(source)
    pending = reached.copy()
    visited_blocks = set()
    distance = 0
    while pending:
        if target is not None and target & pending:
            return distance
        if depth is not None and distance == depth:
            return reached
        after = set()
        for v in pending:
            for block in incidence[v]:
                if block not in visited_blocks:
                    visited_blocks.add(block)
                    after.update(blocks[block])
        pending = after - reached
        reached.update(pending)
        distance += 1
    return reached if target is None else None


def check_support(masks, members):
    signatures = [masks[v] for v in members]
    if len(members) < 3 or reduce(operator.and_, signatures):
        raise AssertionError("literal support is small or held")
    if any(not (x & y) for x, y in itertools.combinations(signatures, 2)):
        raise AssertionError("literal support is not jointly candidate")
    member_set = set(members)
    if any(v not in member_set and all(signature & other for other in signatures)
           for v, signature in enumerate(masks)):
        raise AssertionError("literal support has an outside common candidate")


def verify(archive, row):
    blocks, incidence, masks = load(archive / f"{row['stage']}.txt", row["sha256"])
    report = row["exact_distances"]
    a, b = report["antipodes"]
    if closure(blocks, incidence, [a], target={b}) != report["diameter"]:
        raise AssertionError(f"incorrect diametral witness in {row['stage']}")
    for pack in report["ancestral_packings"]:
        anchors = set(pack["anchors"])
        restriction = pack["minimum_pair_distance"] - 1
        if restriction == 1:
            if any(masks[a] & masks[b] for a, b in itertools.combinations(anchors, 2)):
                raise AssertionError(f"packing has a candidate pair at {row['stage']}")
            continue
        if any(closure(blocks, incidence, [a], depth=restriction) & (anchors - {a}) for a in anchors):
            raise AssertionError(f"packing has a short walk at {row['stage']}")
    direct = row.get("verified_support_pair")
    witness = False
    if direct and direct["found"]:
        first, second = direct["parent_sets"]
        check_support(masks, first)
        check_support(masks, second)
        distance = closure(blocks, incidence, first, target=set(second))
        if distance != direct["parent_support_distance"] or distance + 1 != direct["exact_child_distance"]:
            raise AssertionError("literal support distance differs from claimed distance")
        witness = True
    return {"stage": row["stage"], "antipodes_checked": True,
            "packings_checked": len(report["ancestral_packings"]), "support_pair_checked": witness}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    rows = json.loads(args.report.read_text())
    receipts = [verify(args.archive, row) for row in rows]
    print(json.dumps({"checks": receipts,
                      "support_pairs_checked": sum(row["support_pair_checked"] for row in receipts)}, indent=2))


if __name__ == "__main__":
    main()
