"""Replay the start-03 sector extension and its certified irreplaceable members."""

import argparse
import hashlib
import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = "HUB-GUIDED-SAMPLE-20261119-001"
OLD_SCRIPTS = ROOT / "experiments" / PREVIOUS / f"{PREVIOUS}-E001_sampler"
OLD_ARTIFACTS = ROOT / "artifacts" / PREVIOUS / OLD_SCRIPTS.name
sys.path.insert(0, str(OLD_SCRIPTS))

from group_profile import pack
from structure_cnf import binary_closure_cnf
from structure_rank import load_bundled
from structure_sectors import common, masks_and_neighbors
from structure_union import bits, context, project

STAGE_HASH = "049ad2aa85d55619a9e9c97dfd7ed33f6bb0d929d665af56f071b13f8fbd1102"
# Old literal site IDs that start each clique, followed by its completion order.
SEEDS = [
    ((10294, 10427, 17868), "increasing"),
    ((8497, 12040), "increasing"),
    ((4674, 27760), "decreasing"),
    ((9944, 27909), "decreasing"),
    ((0, 8850), "increasing"),
    ((10217, 12040), "decreasing"),
    ((0, 8583, 23544), "increasing"),
]


def stage(path):
    if path:
        raw = path.read_bytes()
    else:
        from stages import archive_replay

        frames = []
        archive_replay("start-03", [8], lambda _, frame: frames.append(frame))
        frame, = frames
        lines = [f"{frame.size} {len(frame.blocks)}"]
        lines.extend(" ".join(map(str, block)) for block in frame.blocks)
        raw = ("\n".join(lines) + "\n").encode("ascii")
    assert hashlib.sha256(raw).hexdigest() == STAGE_HASH
    first, *lines = raw.splitlines()
    n, block_count = map(int, first.split())
    blocks = [list(map(int, line.split())) for line in lines]
    assert len(blocks) == block_count
    return n, blocks


def extend(seed, order, n, world, neighbors):
    group = pack(seed, n)
    choices = common(group, world, neighbors)
    assert group & ~choices == 0
    choices ^= group
    while choices:
        point = choices & -choices if order == "increasing" else 1 << (choices.bit_length() - 1)
        group |= point
        choices = (choices & neighbors[point.bit_length() - 1]) ^ point
    assert common(group, world, neighbors) == group
    return group


def cover_check(groups, n, core):
    target = (1 << len(groups)) - 1
    signatures = {}
    core_signatures = {}
    for site in range(n):
        flag = 1 << site
        signature = sum(1 << i for i, group in enumerate(groups) if group & flag)
        if signature:
            signatures.setdefault(signature, site)
            if flag & core:
                core_signatures.setdefault(signature, site)
    pair_unions = {a | b for a in signatures for b in signatures}
    assert target not in pair_unions
    # A three-name witness for the finite family plus every sector roster.
    three = next([core_signatures[a], signatures[b], signatures[c]]
                 for a in core_signatures for b, c in combinations(signatures, 2)
                 if a | b | c == target)
    assert len(set(three)) == 3
    return dict(physical_names=n, membership_signatures=len(signatures),
                distinct_pair_unions=len(pair_unions), two_names_cover=False,
                three_names_cover_finite_family_and_sector=three)


def conditioned_count(data, ones, zeros):
    """Count circuit assignments, treating a missing physical flag as zero."""
    assert not ones & zeros
    counts = [0, 1]
    scopes = [0, 0]
    dummy = len(data["coordinates"]) - 1
    assert data["coordinates"][dummy] == -1
    for _, kind, *children in data["nodes"][2:]:
        if kind == -1:
            value, scope = 1, 0
            for child in children:
                assert not scope & scopes[child]
                scope |= scopes[child]
                value *= counts[child]
        else:
            left, right = children
            descendants = scopes[left] | scopes[right]
            # Among the physical flags below a decision, every required one
            # must occur on the chosen branch. A missing flag defaults to zero.
            low = 0 if ones & descendants & ~scopes[left] else counts[left]
            high = 0 if ones & descendants & ~scopes[right] else counts[right]
            if kind == dummy:
                value, scope = low + high, descendants
            else:
                flag = 1 << kind
                assert kind >= 0 and not flag & descendants
                value = (0 if ones & flag else low) + (0 if zeros & flag else high)
                scope = descendants | flag
        counts.append(value)
        scopes.append(scope)
    assert ones & ~scopes[data["root"]] == 0
    return counts[data["root"]]


def fiber(blocks, neighbors, cnf_path):
    data = load_bundled(OLD_ARTIFACTS / "structure_rankers.json", "structure_sector13_4")
    coords = data["coordinates"][:-1]
    n = data["n"]
    signs = {p: (side, mask) for p, side, mask in data["sites"]}
    u = 1 << coords.index(193)
    v = 1 << coords.index(192)
    side_a, a = signs[16799]
    side_b, b = signs[16800]
    assert side_a == side_b == 0 and a & (u | v) == u and b & (u | v) == u | v
    required = (a | b) & ~(u | v)
    assert required
    right = pack([x for x, (side, mask) in signs.items() if side == 1 and mask & u], n)
    left = pack([x for x, (side, mask) in signs.items() if side == 0 and mask & v], n)
    assert all(not neighbors[x] & left for x in bits(right))
    empty_signature = pack([x for x, (side, mask) in signs.items() if side or mask == 0], n)
    assert empty_signature == pack(blocks[4], n)
    assert conditioned_count(data, 0, 0) == data["count"] == 183833974142788
    ways = conditioned_count(data, required, u | v)
    assert ways == 20527630615620

    left_sites, _, exclusions = context(blocks, 13, 4)
    physical, _, generators = project(exclusions, left_sites)
    assert physical == coords
    variables, clauses = binary_closure_cnf(generators, len(coords), True)
    units = [i + 1 for i in bits(required)] + [-i - 1 for i in bits(u | v)]
    clauses.extend([x] for x in units)
    lines = [f"p cnf {variables} {len(clauses)}"]
    lines.extend(" ".join(map(str, clause)) + " 0" for clause in clauses)
    raw = ("\n".join(lines) + "\n").encode("ascii")
    if cnf_path:
        cnf_path.write_bytes(raw)
    return dict(left_generators=[16799, 16800], right_flags=[193, 192],
                required_other_flags=len(units) - 2, required_literal_units=units,
                right_possible_difference=right.bit_count(), left_possible_difference=left.bit_count(),
                joinable_cross_pairs=0, irreplaceable_middle_rosters=ways,
                cnf_variables=variables, cnf_clauses=len(clauses),
                conditioned_cnf_sha256=hashlib.sha256(raw).hexdigest())


def run(args):
    n, blocks = stage(args.stage)
    masks, neighbors = masks_and_neighbors(n, blocks)
    world = (1 << n) - 1
    core = masks[4] & masks[13]
    domain = masks[4] | masks[13]
    assert common(core, world, neighbors) == domain
    # Every domain site occurs in an unheld maximal clique. A member of
    # the unique held clique needs a domain neighbor outside that clique.
    assert all(neighbors[v] & domain & ~masks[4] for v in bits(masks[4]))
    compulsory = common(domain, world, neighbors) & domain
    groups = []
    witnesses = []
    for seed, order in SEEDS:
        group = extend(seed, order, n, world, neighbors)
        assert group.bit_count() >= 3 and group not in masks
        assert group & ~domain and group & core
        label = " ".join(map(str, bits(group))).encode("ascii")
        witnesses.append(dict(seed=list(seed), order=order, size=group.bit_count(),
                              shared_core_sites=(group & core).bit_count(),
                              sha256_sorted_decimal_sites=hashlib.sha256(label).hexdigest()))
        groups.append(group)
    overlaps = [(g & h).bit_count() for g, h in combinations(groups, 2)]
    assert len(set(groups)) == 7 and min(overlaps) == 3
    return dict(stage_sha256=STAGE_HASH, physical_sites=n, held_blocks=len(blocks),
                shared_core=core.bit_count(), sector_union=domain.bit_count(),
                union_of_unheld_rosters=domain.bit_count(), intersection_of_unheld_rosters=compulsory.bit_count(),
                sector_children=183833974142787, outside_witnesses=witnesses,
                pairwise_intersections=overlaps, cover=cover_check(groups, n, core),
                minimum_age_nine_parents_in_complete_extension=183833974142794,
                protected=fiber(blocks, neighbors, args.cnf))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, help="optional exact text export, checked by SHA-256")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--cnf", type=Path, help="write independently countable conditioned DIMACS")
    options = parser.parse_args()
    result = json.dumps(run(options), indent=2) + "\n"
    if options.out:
        options.out.write_text(result)
    else:
        print(result, end="")
