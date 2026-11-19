"""Check the real zero result with literal closed candidate neighborhoods."""

import argparse
import hashlib
import json
import time
from pathlib import Path


def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def check(path):
    raw = path.read_bytes()
    header, *rows = raw.splitlines()
    n, block_count = map(int, header.split())
    if len(rows) != block_count:
        raise ValueError("wrong number of block rows")
    blocks = []
    affiliations = [[] for _ in range(n)]
    for i, row in enumerate(rows):
        mask = 0
        for v in map(int, row.split()):
            if not 0 <= v < n or (mask >> v) & 1:
                raise ValueError("invalid literal member")
            mask |= 1 << v
            affiliations[v].append(i)
        blocks.append(mask)

    high = 0
    low = []
    closed = []
    for v, affiliation in enumerate(affiliations):
        if len(affiliation) == 2:
            low.append(v)
        elif len(affiliation) > 2:
            high |= 1 << v
        else:
            raise ValueError("expected at least two memberships")
        neighborhood = 1 << v
        for b in affiliation:
            neighborhood |= blocks[b]
        closed.append(neighborhood)
    if high.bit_count() < 3 or any((closed[h] & high) != high for h in members(high)):
        raise ValueError("larger affiliations must form a clique")
    if any((block & high) == high for block in blocks):
        raise ValueError("some block holds the larger affiliations")
    literal_candidate_pairs, odd = divmod(sum(row.bit_count() - 1 for row in closed), 2)
    if odd:
        raise ArithmeticError("candidate adjacency is asymmetric")

    low_mask = 0
    for v in low:
        a, b = affiliations[v]
        singleton = 1 << v
        low_mask |= singleton
        if (blocks[a] & blocks[b]) != singleton:
            raise ValueError("every pair incident to a smaller affiliation must have a unique common block")

    low_low = mixed = residual = examined_witnesses = 0
    for other, current in enumerate(blocks):
        contained_low = list(members(current & low_mask))
        reachable_by_high = 0
        for witness in members(current & high):
            reachable_by_high |= closed[witness]
            examined_witnesses += 1
        before = [reachable_by_high]
        for witness in contained_low:
            before.append(before[-1] | closed[witness])
            examined_witnesses += 1
        after = 0
        for i in range(len(contained_low) - 1, -1, -1):
            v = contained_low[i]
            a, b = affiliations[v]
            shared = b if a == other else a
            # The two blocks intersect only at v. All other junctions
            # in this block can witness any pending candidate that
            # belongs to their literal closed neighborhood.
            eligible = high | ~((1 << (v + 1)) - 1)
            pending = blocks[shared] & eligible
            mixed += (pending & high).bit_count()
            low_low += (pending & ~high).bit_count()
            residual += (pending & ~(before[i] | after)).bit_count()
            after |= closed[v]
    high_high = high.bit_count() * (high.bit_count() - 1) // 2
    if low_low + mixed + high_high != literal_candidate_pairs:
        raise ArithmeticError("classification disagrees with literal candidate degrees")
    return {
        "input": path.name,
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "method": "literal closed-neighborhood intersections and unique holding blocks",
        "literal_candidate_pairs": literal_candidate_pairs,
        "high_high": high_high,
        "low_low": low_low,
        "mixed": mixed,
        "residual_pairs": residual,
        "witness_neighborhoods_intersected": examined_witnesses,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roster", type=Path)
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    start = time.monotonic()
    result = check(args.roster)
    original = json.loads(args.receipt.read_text())
    for key in ("input_sha256", "residual_pairs"):
        if original[key] != result[key]:
            raise AssertionError((key, original[key], result[key]))
    if original["candidate_pairs"] != result["literal_candidate_pairs"]:
        raise AssertionError("candidate pair count differs")
    for kind in ("high_high", "low_low"):
        if original["types"][kind]["candidate_pairs"] != result[kind]:
            raise AssertionError(f"candidate breakdown differs for {kind}")
    if original["types"]["mixed_single"]["candidate_pairs"] != result["mixed"]:
        raise AssertionError("candidate breakdown differs for mixed pairs")
    result["agrees_with_partition_receipt"] = True
    result["wall_seconds"] = time.monotonic() - start
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
