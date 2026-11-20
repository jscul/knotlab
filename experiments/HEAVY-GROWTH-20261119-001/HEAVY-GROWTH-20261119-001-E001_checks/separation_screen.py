"""Exact candidate diameters and search for separate pure birth supports."""

import argparse
import gzip
import hashlib
import json
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path


UNDECIDED = (1, 2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15)


def bits(mask, limit=None):
    outputs = 0
    while mask and (limit is None or outputs < limit):
        flag = mask & -mask
        yield flag.bit_length() - 1
        mask ^= flag
        outputs += 1


def bitmask(indices):
    most = max(indices, default=-1)
    storage = bytearray((most + 8) // 8)
    for v in indices:
        storage[v // 8] |= 1 << (v % 8)
    return int.from_bytes(storage, "little")


class Roster:
    def __init__(self, file):
        raw = file.read_bytes()
        first, *rows = raw.splitlines()
        self.n, self.block_count = map(int, first.split())
        if len(rows) != self.block_count:
            raise ValueError(f"wrong block count in {file.name}")
        self.sha256 = hashlib.sha256(raw).hexdigest()
        self.full = (1 << self.n) - 1
        self.blocks = []
        self.affiliation = [0] * self.n
        for i, row in enumerate(rows):
            vertices = list(map(int, row.split()))
            if len(vertices) < 2 or len(set(vertices)) != len(vertices) or any(v < 0 or v >= self.n for v in vertices):
                raise ValueError(f"invalid block in {file.name}")
            self.blocks.append(bitmask(vertices))
            color = 1 << i
            for v in vertices:
                self.affiliation[v] |= color
        self.row = lru_cache(maxsize=2048)(self.closed_row)
        self.degrees = None

    def closed_row(self, junction):
        reachable = 1 << junction
        for block in bits(self.affiliation[junction]):
            reachable |= self.blocks[block]
        return reachable

    def clique_neighbors(self, clique):
        reached = clique
        for block in self.blocks:
            if block & clique:
                reached |= block
        return reached


def diameter(roster):
    """Use the distances between holding blocks to test literal radius bounds."""
    if roster.n <= 1:
        return {"diameter": 0, "antipodes": None}
    if 0 in roster.affiliation:
        return {"diameter": None, "antipodes": [roster.affiliation.index(0), None],
                "reason": "isolated junction"}
    neighbors = [1 << b for b in range(roster.block_count)]
    for b, block in enumerate(roster.blocks):
        for c in range(b):
            if block & roster.blocks[c]:
                neighbors[b] |= 1 << c
                neighbors[c] |= 1 << b
    representatives = {}
    for v, signature in enumerate(roster.affiliation):
        representatives.setdefault(signature, v)
    balls = roster.blocks[:]
    witness = [0, 1]
    packings = []
    radius = 1
    while True:
        complete_blocks = bitmask([b for b, covered in enumerate(balls) if covered == roster.full])
        for signature, vertex in representatives.items():
            if signature & complete_blocks:
                continue
            covered = 0
            for block in bits(signature):
                covered |= balls[block]
                if covered == roster.full:
                    break
            if covered != roster.full:
                partner = next(bits(roster.full & ~covered))
                witness = [vertex, partner]
                break
        else:
            return {"diameter": radius, "antipodes": witness,
                    "distinct_affiliations": len(representatives), "ancestral_packings": packings}
        packing = max((greedy_packing(roster, balls, first) for first in witness), key=len)
        packings.append({"minimum_pair_distance": radius + 1, "anchors": packing,
                         "all_descendants_distinct_through": radius,
                         "all_descendants_noncandidate_through": radius - 1})
        extended = []
        for b, known in enumerate(balls):
            for c in bits(neighbors[b]):
                known |= balls[c]
                if known == roster.full:
                    break
            extended.append(known)
        if extended == balls:
            return {"diameter": None, "antipodes": witness, "reason": "separate components"}
        balls = extended
        radius += 1


def greedy_packing(roster, balls, first):
    """Exhibit anchors outside all previously selected literal metric balls."""
    available = roster.full
    chosen = []
    vertex = first
    while available:
        chosen.append(vertex)
        for block in bits(roster.affiliation[vertex]):
            available &= ~balls[block]
            if not available:
                break
        if available:
            vertex = next(bits(available))
    return chosen


def exact_degree_data(file, metadata, n):
    path = file.with_suffix(".degrees.json.gz")
    if not path.is_file():
        return None
    if hashlib.sha256(path.read_bytes()).hexdigest() != metadata["files"]["degrees"]["sha256"]:
        raise ValueError(f"candidate degree digest does not match {file.name}")
    with gzip.open(path, "rt") as readable:
        out = json.load(readable)
    if len(out) != n:
        raise ValueError("misaligned candidate degrees")
    return out


def complete_in_block(roster, eligible):
    representative = next(bits(eligible))
    for block in bits(roster.affiliation[representative]):
        if not eligible & ~roster.blocks[block]:
            return True
    return False


def extend(roster, anchor, domain, avoid=0, *, limit=600):
    """Deterministic bounded search for a globally maximal unheld clique."""
    if not (domain >> anchor) & 1:
        raise ValueError("seed outside its declared allowed region")
    held = roster.affiliation[anchor]
    chosen = 1 << anchor
    common = roster.row(anchor)
    picked = 1
    while True:
        eligible = common & domain & ~chosen
        if not eligible:
            break
        if complete_in_block(roster, eligible):
            chosen |= eligible
            for block in bits(held):
                if eligible & ~roster.blocks[block]:
                    held &= ~(1 << block)
            outsiders = common & ~domain
            for v in bits(outsiders):
                if eligible & ~roster.row(v):
                    common &= ~(1 << v)
            common &= chosen | ~domain
            break
        if picked >= limit:
            return None, "extension cap"
        sample = set(bits(eligible, 12))
        for block in bits(held, 6):
            sample.update(bits(eligible & ~roster.blocks[block], 4))
        score = lambda v: (
            (held & roster.affiliation[v]).bit_count(),
            (avoid & roster.row(v)).bit_count() if avoid else 0,
            roster.degrees[v] if roster.degrees is not None else roster.affiliation[v].bit_count(),
            v,
        )
        v = min(sample, key=score)
        common &= roster.row(v)
        held &= roster.affiliation[v]
        chosen |= 1 << v
        picked += 1
    if common & ~chosen:
        return None, "cannot extend inside region"
    if held or chosen.bit_count() < 3:
        return None, "held or too small"
    return chosen, "unheld maximal group"


def verify_support(roster, group):
    common = roster.full
    for v in bits(group):
        row = roster.row(v)
        if group & ~row:
            raise AssertionError("submitted group is not mutually joinable")
        common &= row
    if common != group:
        raise AssertionError("submitted group is not globally maximal")
    if group.bit_count() < 3 or any((block & group) == group for block in roster.blocks):
        raise AssertionError("submitted group is held")


def support_pair(roster, antipodes):
    if roster.n < 3:
        return {"found": False, "attempts": 0}
    if roster.degrees is not None:
        universal = [v for v, degree in enumerate(roster.degrees) if degree == roster.n - 1]
        if universal:
            if roster.row(universal[0]) != roster.full:
                raise AssertionError("universal candidate certificate failed literal replay")
            sizes = [block.bit_count() for block in roster.blocks]
            possible_sizes = set(sizes)
            exposed = [
                v for v, degree in enumerate(roster.degrees)
                if degree < roster.n - 1 and degree + 1 in possible_sizes
                and any(sizes[b] == degree + 1 for b in bits(roster.affiliation[v]))
            ]
            return {"found": False, "attempts": 0,
                    "exact_obstruction": "every legal large group contains every universal junction",
                    "universal_candidates": len(universal), "verified_example": universal[0],
                    "held_neighborhood_sites": exposed,
                    "guaranteed_residual_rectangle": len(universal) * len(exposed)}
    if roster.degrees is None:
        ordered = sorted(range(roster.n), key=lambda v: (roster.affiliation[v].bit_count(), v))
    else:
        ordered = sorted(range(roster.n), key=lambda v: (roster.degrees[v], v))
    initial = [v for v in (antipodes or []) if v is not None]
    probes = [ordered[(len(ordered) - 1) * i // 4] for i in range(1, 5)]
    choices = list(dict.fromkeys(initial + ordered[:6] + probes))[:12]
    counts = Counter()
    best = None
    for a in choices:
        first, status = extend(roster, a, roster.full)
        counts[status] += 1
        if first is None:
            continue
        # Try the most distant complement of a literal ball first.
        reached = first
        domains = []
        radius = 0
        while reached != roster.full:
            domains.append((roster.full & ~reached, radius))
            enlarged = roster.clique_neighbors(reached)
            if enlarged == reached:
                break
            reached = enlarged
            radius += 1
        for domain, radius in reversed(domains):
            if best is not None and radius == 0:
                continue
            seeds = [v for v in initial if (domain >> v) & 1]
            for v in ordered:
                if (domain >> v) & 1 and v not in seeds:
                    seeds.append(v)
                if len(seeds) >= 4:
                    break
            for b in seeds:
                second, status = extend(roster, b, domain, avoid=first if not radius else 0)
                counts[status] += 1
                if second is None:
                    continue
                if first & second or (radius and roster.clique_neighbors(first) & second):
                    raise AssertionError("separation witness failed its defining test")
                if radius:
                    return finish_pair(roster, a, b, first, second, counts)
                best = (a, b, first, second)
                break
    if best is None:
        return {"found": False, "attempts": sum(counts.values()), "search_outcomes": dict(counts)}
    return finish_pair(roster, *best, counts)


def finish_pair(roster, a, b, first, second, counts):
    verify_support(roster, first)
    verify_support(roster, second)
    reached = first
    distance = 0
    while not reached & second:
        enlarged = roster.clique_neighbors(reached)
        if enlarged == reached:
            raise ValueError("separation pair comes from disconnected supports")
        reached = enlarged
        distance += 1
    return {"found": True, "seed_junctions": [a, b], "disjoint": True,
            "all_cross_pairs_noncandidate": distance >= 2, "parent_support_distance": distance,
            "exact_child_distance": 1 + distance,
            "parent_counts": [first.bit_count(), second.bit_count()],
            "parent_sets": [list(bits(first)), list(bits(second))],
            "attempts": sum(counts.values()), "search_outcomes": dict(counts)}


def stage_run(folder, stage, search):
    start = time.monotonic()
    path = folder / f"{stage}.txt"
    metadata = json.loads(path.with_suffix(".meta.json").read_text())
    roster = Roster(path)
    if roster.sha256 != metadata["files"]["blocks"]["sha256"]:
        raise ValueError(f"literal roster hash does not match {stage}")
    diam = diameter(roster)
    result = {"stage": stage, "live": roster.n, "blocks": roster.block_count, "sha256": roster.sha256,
              "exact_distances": diam}
    bound = 0 if diam["diameter"] is None else max(0, diam["diameter"] - 1)
    if search:
        roster.degrees = exact_degree_data(path, metadata, roster.n)
        proof = support_pair(roster, diam["antipodes"])
        result["verified_support_pair"] = proof
        bound = max(bound, proof.get("exact_child_distance", 0))
    result["guaranteed_nonclosing_transitions"] = bound
    result["seconds"] = time.monotonic() - start
    return result


def archived_stages(folder):
    index = {}
    for file in folder.glob("start-*-age*.meta.json"):
        metadata = json.loads(file.read_text())
        tag, age = metadata["case"], metadata["age"]
        if not tag.startswith("start-") or int(tag.removeprefix("start-")) not in UNDECIDED:
            continue
        if metadata["role"] not in {"first_unread", "last_built_precursor"}:
            continue
        index.setdefault(tag, []).append((age, file.name.removesuffix(".meta.json"), metadata["role"]))
    for tag in sorted(index):
        for age, stage, role in sorted(index[tag]):
            yield stage, role == "first_unread"
    if len(index) != len(UNDECIDED):
        raise ValueError("missing one or more archived undecided starts")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--only", action="append")
    parser.add_argument("--distances-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    output = []
    for stage, search in archived_stages(args.archive):
        if args.only is None or stage in args.only:
            row = stage_run(args.archive, stage, search and not args.distances_only)
            if args.json:
                output.append(row)
            else:
                print(json.dumps(row), flush=True)
    if args.json:
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
