"""Test intersection of the parents of two actual next-round children."""
import argparse
from collections import defaultdict
import gzip
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
from random import Random
from struct import pack
import subprocess
import sys
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = "HUB-GUIDED-SAMPLE-20261119-001"
FAMILY = PRIOR + "-E001_sampler"
SOURCE = ROOT / "artifacts" / PRIOR / FAMILY
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
sys.path.insert(0, str(ROOT / "experiments" / PRIOR / FAMILY))
from near_block import NearBlock, mask_of  # noqa: E402


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def common_neighborhood(rows, group):
    relevant = (1 << len(rows)) - 1
    for u in bits(group):
        relevant &= rows[u]
    return relevant


def no_cross_compatibility(rows, group, other):
    return all(not rows[u] & other for u in bits(group))


def set_distance(rows, left, right):
    steps = 0
    reached = left
    while not reached & right:
        expanded = touching(reached, rows)
        assert expanded != reached, "the tested archive end is connected"
        reached = expanded
        steps += 1
    return steps


def invert(count, codes):
    """Read a fixed sequence of sets into bitmaps indexing occurrences."""
    width = (len(codes) + 7) // 8
    columns = [bytearray(width) for _ in range(count)]
    for i, group in enumerate(codes):
        byte, mark = i // 8, 1 << (i % 8)
        for u in bits(group):
            columns[u][byte] |= mark
    return [int.from_bytes(column, "little") for column in columns]


def touching(group, inverted):
    result = 0
    for u in bits(group):
        result |= inverted[u]
    return result


class Roster:
    def __init__(self, path, expected):
        self.path = path
        assigned = []
        digest = sha256()
        with path.open("rb") as handle:
            header = handle.readline()
            digest.update(header)
            self.n, size = map(int, header.split())
            for line in handle:
                digest.update(line)
                assigned.append(tuple(map(int, line.split())))
        assert digest.hexdigest() == expected
        assert size == len(assigned)
        self.digest = expected
        self.full = (1 << self.n) - 1
        self.blocks = tuple(mask_of(block, self.n) for block in assigned)
        affiliation = [0] * self.n
        for b, block in enumerate(assigned):
            for u in block:
                affiliation[u] |= 1 << b
        self.affiliation = affiliation
        cache = {}
        self.rows = []
        for u, code in enumerate(affiliation):
            if not code:
                self.rows.append(1 << u)
                continue
            if code not in cache:
                hood = 0
                for b in bits(code):
                    hood |= self.blocks[b]
                cache[code] = hood
            self.rows.append(cache[code])

    def is_unheld_maximum(self, group):
        return (group.bit_count() >= 3 and common_neighborhood(self.rows, group) == group
                and all(group & ~block for block in self.blocks))


class Quotient:
    def __init__(self, rows, physical):
        class_of, keep, members = {}, [], []
        self.raw_class = []
        for u, row in enumerate(rows):
            if row not in class_of:
                class_of[row] = len(keep)
                keep.append(u)
                members.append(0)
            j = class_of[row]
            members[j] |= physical[u]
            self.raw_class.append(j)
        self.n = len(keep)
        self.full = (1 << self.n) - 1
        self.members = members
        self.rows = [sum(1 << j for j, u in enumerate(keep) if rows[v] >> u & 1) for v in keep]
        self.pick = [(m & -m).bit_length() - 1 for m in members]

    def to_physical(self, group):
        lifted = 0
        for u in bits(group):
            lifted |= self.members[u]
        return lifted

    def restrict_whole_block(self, block):
        compressed = sum(1 << u for u, member in enumerate(self.members) if member & block == member)
        if self.to_physical(compressed) == block:
            return compressed
        return None


def near_quotient(path, receipt):
    stage = NearBlock(path)
    assert stage.digest == receipt["input_sha256"]
    conflicts, multiplicities, n_inside = stage.quotient()
    assert list(conflicts) == [int(r, 16) for r in receipt["literal_conflict_rows_on_quotient"]]
    profiles = [row.to_bytes((stage.n + 7) // 8, "little") for row in stage.exterior_types]
    by_profile = defaultdict(list)
    for u in bits(stage.big):
        byte, mark = divmod(u, 8)
        signature = sum(((row[byte] >> mark) & 1) << j for j, row in enumerate(profiles))
        by_profile[signature].append(u)
    physical = [mask_of(ids, stage.n) for ids in by_profile.values()] + [1 << u for u in stage.others]
    assert list(by_profile) == list(stage.interior_types)
    assert [group.bit_count() for group in physical] == list(multiplicities)
    full = (1 << len(conflicts)) - 1
    q = Quotient([full ^ row for row in conflicts], physical)
    inside = sum(1 << q.raw_class[i] for i in range(n_inside))
    assert inside.bit_count() == n_inside and q.to_physical(inside) == stage.big
    return stage, q, inside


def trace(binary, work, q, cap):
    width = ((q.n + 63) // 64) * 8
    input_graph = pack("<I", q.n) + b"".join((q.full ^ row).to_bytes(width, "little") for row in q.rows)
    out = work / "trace.bin"
    with out.open("wb") as output:
        result = subprocess.run([binary, str(cap)], input=input_graph, stdout=output, stderr=subprocess.PIPE, check=True)
    nodes, count, complete = map(int, result.stderr.split())
    assert out.stat().st_size == count * width and (complete or nodes == cap)
    payload = sha256()
    maxima = []
    with out.open("rb") as handle:
        while chunk := handle.read(width * 8192):
            payload.update(chunk)
            maxima.extend(int.from_bytes(chunk[i:i+width], "little") for i in range(0, len(chunk), width))
    return maxima, {"nodes": nodes, "raw_maxima": count, "trace_sha256": payload.hexdigest(),
                    "complete": bool(complete), "quotient_atoms": q.n}


def held_on_quotient(q, blocks):
    held = set()
    for block in blocks:
        which = q.restrict_whole_block(block)
        if which is not None and common_neighborhood(q.rows, which) == which:
            held.add(which)
    return held


def disjoint_groups(groups, width):
    inverted = invert(width, groups)
    full = (1 << len(groups)) - 1
    for selected in groups:
        absent = full ^ touching(selected, inverted)
        if absent:
            return selected, groups[(absent & -absent).bit_length() - 1]
    return None


def bucket_disjoint(groups, n, inside, budget):
    """Ignore pairs of families of children with a common interior parent."""
    buckets = defaultdict(list)
    for group in groups:
        buckets[group & inside].append(group & ~inside)
    inside_masks = list(buckets)
    inverted = invert(n, inside_masks)
    full = (1 << len(inside_masks)) - 1
    scanned = 0
    for i, core in enumerate(inside_masks):
        absent = (full ^ touching(core, inverted)) >> i << i
        for j in bits(absent):
            other_core = inside_masks[j]
            left, right = buckets[core], buckets[other_core]
            if len(left) > len(right):
                left, right = right, left
                first_core, second_core = other_core, core
            else:
                first_core, second_core = core, other_core
            right_inverted = invert(n, right)
            all_right = (1 << len(right)) - 1
            for exterior in left:
                if scanned == budget:
                    return None, False, len(buckets), scanned
                scanned += 1
                available = all_right ^ touching(exterior, right_inverted)
                if available:
                    other_exterior = right[(available & -available).bit_length() - 1]
                    return (first_core | exterior, second_core | other_exterior), True, len(buckets), scanned
    return None, True, len(buckets), scanned


def greedy_clique(rows, start, rng, avoid=0):
    full = (1 << len(rows)) - 1
    selected = start
    common = common_neighborhood(rows, start)
    assert common & start == start
    remaining = common & ~selected & ~avoid
    bad = common & avoid

    def sample(pool):
        trial = rng.randrange(len(rows))
        above = pool >> trial
        if above:
            return trial + (above & -above).bit_length() - 1
        return (pool & -pool).bit_length() - 1

    while remaining:
        u = sample(remaining)
        if bad:
            probe = [u] + [sample(remaining) for _ in range(5)]
            u = min(probe, key=lambda v: ((rows[v] & bad).bit_count(), -(rows[v] & remaining).bit_count()))
        add = 1 << u
        selected |= add
        remaining &= rows[u] ^ add
        bad &= rows[u]
    if bad:
        return None
    assert selected & (full ^ common_neighborhood(rows, selected)) == 0
    assert common_neighborhood(rows, selected) == selected
    return selected


def greatest_witness(roster, residual, limit):
    for left, right in combinations(residual, 2):
        if not left & right:
            return left, right
    rng = Random(202611190381)
    for i in range(limit):
        left = residual[i] if i < len(residual) else greedy_clique(roster.rows, 1 << rng.randrange(roster.n), rng)
        if left not in residual and not roster.is_unheld_maximum(left):
            continue
        right = greedy_clique(roster.rows, 0, rng, avoid=left)
        if right is not None and roster.is_unheld_maximum(right):
            assert not left & right
            return left, right
    return None


def separated_witness(roster, residual, pair):
    rng = Random(202611190773)
    smallest = sorted(range(roster.n), key=lambda u: (roster.rows[u].bit_count(), u))[:128]
    seeds = list(dict.fromkeys([*residual, *pair]))
    checks = 0
    searched = set()
    for choice in smallest:
        group = greedy_clique(roster.rows, 1 << choice, rng)
        if roster.is_unheld_maximum(group):
            seeds.append(group)
    for group in seeds:
        forbidden = touching(group, roster.rows)
        if forbidden in searched:
            continue
        searched.add(forbidden)
        if (roster.full ^ forbidden).bit_count() < 2:
            continue
        checks += 1
        for other in residual:
            if not other & forbidden:
                return (group,other),checks
        for _ in range(12):
            other = greedy_clique(roster.rows, 0, rng, avoid=forbidden)
            if other is not None and roster.is_unheld_maximum(other):
                return (group,other),checks
    return None,checks


def summarize_child(group, residual):
    return {"parent_count": group.bit_count(), "parents_hex": hex(group),
            "kind": "residual_pair" if group in residual else "unheld_maximal_group"}


def load(name):
    return json.loads((SOURCE / f"{name}.json").read_text())


def verify_named_parent(path, label, expected_hash):
    digest = sha256()
    compatible = set()
    name = str(label).encode()
    with path.open("rb") as source:
        header = source.readline()
        digest.update(header)
        n, b = map(int, header.split())
        membership = []
        for i, line in enumerate(source):
            digest.update(line)
            names = line.split()
            if name in names:
                membership.append(i)
                compatible.update(map(int, names))
    assert i + 1 == b
    assert digest.hexdigest() == expected_hash
    assert len(compatible) == n and min(compatible) == 0 and max(compatible) == n-1
    return {"stage": path.stem, "parent": label, "closed_candidate_neighborhood": len(compatible),
            "incident_blocks": membership, "source_sha256": expected_hash}


def near_case(binary, work, path):
    receipt = load("near_block_02")
    case, q, inside = near_quotient(path, receipt)
    maxima, stats = trace(binary, work, q, 12_000_000)
    assert stats["complete"] and stats["raw_maxima"] == receipt["exact_count"]["raw_maximal_cliques"]
    held = held_on_quotient(q, case.blocks)
    assert held == {inside}
    assert receipt["correction"]["offshoots"] == receipt["correction"]["residual_pairs"] == 0
    groups = [g for g in maxima if g not in held]
    common = q.full
    for group in groups:
        common &= group
    pair, decided, buckets, checks = bucket_disjoint(groups, q.n, inside, 20_000_000)
    physical = None
    if pair:
        physical = tuple(map(q.to_physical, pair))
        for group in physical:
            assert all(group & row == group for u, row in zip(case.others, case.rows) if group >> u & 1)
            assert not case.can_extend(group) and all(group & ~b for b in case.blocks)
        assert not physical[0] & physical[1]
    universal = case.big
    for row in case.rows:
        universal &= row
    # Inside the dominant clique, a junction is universally compatible exactly
    # when every exterior junction has it in its closed candidate row.
    assert universal and all(row != case.full for row in case.rows)
    assert q.to_physical(common) == universal and not pair and decided
    count = len(groups)
    born = int(case.path.stem[-2:]) + 1
    renamings = load("near_block_verified")["renamings"]
    root = next(bits(universal))
    named_receipts = [verify_named_parent(path, root, case.digest)]
    for image in renamings:
        stem = image["image"] + "-age09"
        map_bytes = (path.parent / (stem + ".map-from-02.json.gz")).read_bytes()
        assert sha256(map_bytes).hexdigest() == image["named_map_sha256"]
        names = json.loads(gzip.decompress(map_bytes))
        named_receipts.append(verify_named_parent(path.parent / (stem + ".txt"), names[root], image["blocks_sha256"]))
    return {"stage": case.path.stem, "sha256": case.digest, "images": renamings,
            "actual_children": count, "trace": stats, "interior_buckets": buckets,
            "exterior_tests": checks, "common_parent_count": universal.bit_count(),
            "least_common_parent": root,
            "universally_compatible_physical_parents": named_receipts,
            "verified_universal_parents_hex": hex(universal),
            "child_pairwise_intersecting": (pair is None) if decided else None,
            "disjoint_children": [summarize_child(group, ()) for group in physical] if pair else None,
            "single_block_tail": {"age_of_single_block": born,
                                  "next_round_births": comb(count, 2),
                                  "last_nonempty_round": born + count - 1,
                                  "first_empty_round": born + count}}


def other_case(binary, work, case, path, expected_hash):
    roster = Roster(path, expected_hash)
    residual = []
    if case == "01":
        receipt = load("pair_star_residual_start01")
        assert receipt["input_sha256"] == expected_hash and receipt["residual_pairs"] == 0
    else:
        receipt = load("cover_pairs" + case)
        assert receipt["live"] == roster.n
        residual = [(1 << u) | (1 << v) for u, v in receipt["pairs"]]
        assert len(residual) == receipt["residual_pairs"]
        assert all(common_neighborhood(roster.rows, group) & group == group for group in residual)

    stats = None
    pair = greatest_witness(roster, residual, 192)
    decided = pair is not None
    common = None
    if not pair and case == "11":
        q = Quotient(roster.rows, [1 << u for u in range(roster.n)])
        maxima, stats = trace(binary, work, q, 5_000_000)
        held = held_on_quotient(q, roster.blocks)
        truth = next(r for r in load("quotient_check")["targets"] if r["case"] == "start-11")
        assert stats["complete"] and len(maxima) == truth["counted_candidate_maxima"]
        assert len(held) == truth["held_maxima"] and not residual and not truth["offshoots"]
        groups = [g for g in maxima if g not in held]
        compact = disjoint_groups(groups, q.n)
        pair = tuple(map(q.to_physical, compact)) if compact else None
        co = q.full
        for group in groups:
            co &= group
        common = q.to_physical(co).bit_count()
        decided = True
    if pair:
        assert not pair[0] & pair[1]
        assert all(group in residual or roster.is_unheld_maximum(group) for group in pair)
    separation = None
    probes = None
    if pair and case in ("09", "10"):
        extra,probes = separated_witness(roster, residual, pair)
        if extra:
            gap = set_distance(roster.rows, *extra)
            assert gap >= 2
            separation = {"source_candidate_set_distance": gap,
                          "groups": [summarize_child(g, residual) for g in extra]}
    return {"stage": path.stem, "sha256": expected_hash, "trace": stats,
            "child_pairwise_intersecting": (pair is None) if decided else None,
            "common_parent_count": common,
            "disjoint_children": [summarize_child(group, residual) for group in pair] if pair else None,
            "separated_pair": separation, "separation_search_probes": probes,
            "no_cross_compatibility": no_cross_compatibility(roster.rows, *pair) if pair else None}


def control(binary, work):
    for n in range(1, 5):
        pairs = list(combinations(range(n), 2))
        full = (1 << n) - 1
        for chosen in range(1 << len(pairs)):
            rows = [1 << u for u in range(n)]
            for j in bits(chosen):
                u, v = pairs[j]
                rows[u] |= 1 << v
                rows[v] |= 1 << u
            q = Quotient(rows, [1 << u for u in range(n)])
            observed, report = trace(binary, work, q, 5000)
            exact = {g for g in range(1, full+1) if common_neighborhood(rows, g) == g}
            assert report["complete"] and len(observed) == len(exact)
            assert {q.to_physical(g) for g in observed} == exact
            disjoint = any(not a & b for a,b in combinations(observed, 2))
            witness, definite, _, _ = bucket_disjoint(observed, q.n, q.full >> 1, 5000)
            assert definite and bool(witness) == disjoint
            assert bool(disjoint_groups(observed, q.n)) == disjoint


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--case", action="append", choices=("01", "02", "09", "10", "11"))
    args = parser.parse_args()
    cases = args.case or ("02", "01", "09", "10", "11")
    archive = load("stages")
    frontier = {row["case"][6:]: row for row in archive["stages"] if row["role"] == "first_unread"}
    with TemporaryDirectory(prefix="heavy-quotient-") as tmp:
        work = Path(tmp)
        binary = work / "trace"
        subprocess.run(["c++", "-O3", "-march=native", "-std=c++20", "-Wall", "-Wextra",
                        HERE / "quotient_trace.cpp", "-o", binary], check=True)
        control(binary, work)
        for case in cases:
            row = frontier[case]["files"]["blocks"]
            path = args.input_dir / row["name"]
            evidence = near_case(binary, work, path) if case == "02" else other_case(binary, work, case, path, row["sha256"])
            evidence["controls"] = "All 75 labelled simple graphs on one through four vertices."
            (OUTPUT / f"quotient_{case}.json").write_text(json.dumps(evidence, indent=2) + "\n")
            print(evidence["stage"], evidence["child_pairwise_intersecting"],
                  evidence.get("common_parent_count"), flush=True)


if __name__ == "__main__":
    main()
