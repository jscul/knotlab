"""Count residual candidate pairs when the larger affiliations form an unheld clique."""

import argparse
import hashlib
import itertools
import json
import random
import time
from pathlib import Path


def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def affiliation_masks(path):
    raw = path.read_bytes()
    header, *rows = raw.splitlines()
    n, b = map(int, header.split())
    if n < 1 or b < 0 or len(rows) != b:
        raise ValueError("invalid roster dimensions")
    by_junction = [0] * n
    for j, row in enumerate(rows):
        block = list(map(int, row.split()))
        if len(block) < 2 or len(set(block)) != len(block) or any(v < 0 or v >= n for v in block):
            raise ValueError(f"invalid block {j}")
        for v in block:
            by_junction[v] |= 1 << j
    return by_junction, b, hashlib.sha256(raw).hexdigest()


def choose_two(n):
    return n * (n - 1) // 2


def count_pair_residuals(affiliations, blocks, collect_pairs=False):
    """Return candidate and residual counts by pair type, and optional literal residuals."""
    low = {}
    high = []
    high_affiliations = []
    high_by_block = [0] * blocks
    for v, affiliation in enumerate(affiliations):
        size = affiliation.bit_count()
        if size < 2:
            raise ValueError("every junction must belong to at least two blocks")
        if size == 2:
            key = tuple(members(affiliation))
            if key in low:
                raise ValueError(f"duplicate two-block affiliation {key}")
            low[key] = v
        else:
            flag = 1 << len(high)
            high.append(v)
            high_affiliations.append(affiliation)
            for block in members(affiliation):
                high_by_block[block] |= flag

    all_high = (1 << len(high)) - 1
    high_common_block_count = sum(h == all_high for h in high_by_block) if high else 0
    for affiliation in high_affiliations:
        adjacent_high = 0
        for block in members(affiliation):
            adjacent_high |= high_by_block[block]
            if adjacent_high == all_high:
                break
        if adjacent_high != all_high:
            raise ValueError("junctions with more than two memberships are not a clique")
    if len(high) >= 2 and high_common_block_count:
        raise ValueError("the clique of larger affiliations must be unheld")

    low_adjacency = [0] * blocks
    for b, c in low:
        low_adjacency[b] |= 1 << c
        low_adjacency[c] |= 1 << b

    # union_except[b][c] includes highs holding some partner of b other
    # than c. Prefix and suffix ORs give all of these unions in linear
    # time in the number of low affiliations, counting bitset operations.
    union_except = []
    for neighbors in low_adjacency:
        partners = list(members(neighbors))
        prefix = [0]
        for partner in partners:
            prefix.append(prefix[-1] | high_by_block[partner])
        following = 0
        excluding = {}
        for i in range(len(partners) - 1, -1, -1):
            partner = partners[i]
            excluding[partner] = prefix[i] | following
            following |= high_by_block[partner]
        union_except.append(excluding)

    pairs = set() if collect_pairs else None
    low_low_candidates = 0
    low_low_residual = 0
    low_low_by_block = {}
    for b, neighbors in enumerate(low_adjacency):
        low_low_candidates += choose_two(neighbors.bit_count())
        ordered_count = 0
        for c in members(neighbors):
            # A low witness must hold c,d. A high witness must hold c,d
            # while omitting b. Cross off all leaves d with either type.
            still_residual = neighbors & ~low_adjacency[c] & ~(1 << c)
            possible_high = high_by_block[c] & ~high_by_block[b]
            while still_residual and possible_high:
                witness = possible_high & -possible_high
                possible_high ^= witness
                still_residual &= ~high_affiliations[witness.bit_length() - 1]
            ordered_count += still_residual.bit_count()
            if pairs is not None:
                one = low[tuple(sorted((b, c)))]
                for d in members(still_residual):
                    other = low[tuple(sorted((b, d)))]
                    pairs.add(tuple(sorted((one, other))))
        count, odd = divmod(ordered_count, 2)
        if odd:
            raise ArithmeticError(f"low-pair count lost symmetry in block {b}")
        low_low_residual += count
        if count:
            low_low_by_block[b] = count

    mixed_single_candidates = mixed_double_candidates = 0
    mixed_single_residual = mixed_double_residual = 0
    low_affiliations_with_mixed_residual = 0
    for (b, c), v in low.items():
        h_b, h_c = high_by_block[b], high_by_block[c]
        only_b, only_c = h_b & ~h_c, h_c & ~h_b
        both = h_b & h_c
        mixed_single_candidates += only_b.bit_count() + only_c.bit_count()
        mixed_double_candidates += both.bit_count()
        opp_b, opp_c = union_except[b][c], union_except[c][b]

        # A high sharing only b needs a witness through c and outside b.
        # Every high in only_c supplies it. A low witness (c,d) requires
        # this high to also hold d. Swap the roles for the other half.
        single = (0 if only_c else only_b & ~opp_c) | (0 if only_b else only_c & ~opp_b)
        mixed_single_residual += single.bit_count()

        # A high sharing both b,c needs compatible witnesses, one
        # holding b but not c and the other holding c but not b.
        double_covered = ((only_b and only_c) or (only_b & opp_c) or (only_c & opp_b)
                          or (low_adjacency[b] & low_adjacency[c]))
        double = 0 if double_covered else both
        mixed_double_residual += double.bit_count()
        low_affiliations_with_mixed_residual += bool(single or double)
        if pairs is not None:
            for w in members(single | double):
                pairs.add(tuple(sorted((v, high[w]))))

    counts = {
        "high_high": (choose_two(len(high)), 0),
        "low_low": (low_low_candidates, low_low_residual),
        "mixed_single": (mixed_single_candidates, mixed_single_residual),
        "mixed_double": (mixed_double_candidates, mixed_double_residual),
    }
    candidate_pairs = sum(candidate for candidate, _ in counts.values())
    residual_pairs = sum(residual for _, residual in counts.values())
    if pairs is not None and len(pairs) != residual_pairs:
        raise ArithmeticError("materialized residual pairs disagree with bulk count")
    return {
        "junctions": len(affiliations),
        "blocks": blocks,
        "larger_affiliations": len(high),
        "two_block_affiliations": len(low),
        "larger_affiliations_clique_verified": True,
        "larger_affiliations_common_blocks": high_common_block_count,
        "candidate_pairs": candidate_pairs,
        "covered_candidate_pairs": candidate_pairs - residual_pairs,
        "residual_pairs": residual_pairs,
        "types": {kind: {"candidate_pairs": candidate, "residual_pairs": residual}
                  for kind, (candidate, residual) in counts.items()},
        "low_low_residual_by_block": low_low_by_block,
        "low_affiliations_with_mixed_residual": low_affiliations_with_mixed_residual,
    }, pairs


def reference(affiliations):
    """Enumerate literal candidate pairs and maximal cliques independently."""
    import networkx as nx

    graph = nx.Graph()
    graph.add_nodes_from(range(len(affiliations)))
    for a, b in itertools.combinations(range(len(affiliations)), 2):
        if affiliations[a] & affiliations[b]:
            graph.add_edge(a, b)
    candidates = {tuple(sorted(pair)) for pair in graph.edges}
    residual = set(candidates)
    for clique in nx.find_cliques(graph):
        if len(clique) < 3:
            continue
        shared = affiliations[clique[0]]
        for v in clique[1:]:
            shared &= affiliations[v]
        if not shared:
            residual.difference_update(itertools.combinations(sorted(clique), 2))
    return candidates, residual


def small_controls(control_rosters=None):
    fixed_high = [0b001011, 0b010101, 0b100110]
    choices = [1 << a | 1 << b for a, b in itertools.combinations(range(5), 2)]
    exercised = {name: {"covered": 0, "residual": 0}
                 for name in ("high_high", "low_low", "mixed_single", "mixed_double")}
    rng = random.Random(202611190133)

    def compare(affiliations, blocks, report_pairs=None):
        if report_pairs is None:
            report_pairs = count_pair_residuals(affiliations, blocks, collect_pairs=True)
        report, pairs = report_pairs
        candidates, expected = reference(affiliations)
        if report["candidate_pairs"] != len(candidates) or pairs != expected:
            raise AssertionError((affiliations, report, pairs, expected))
        for name, outcome in report["types"].items():
            exercise = exercised[name]
            exercise["residual"] += outcome["residual_pairs"]
            exercise["covered"] += outcome["candidate_pairs"] - outcome["residual_pairs"]

    for mask in range(1 << len(choices)):
        compare(fixed_high + [choices[v] for v in members(mask)], 6)
    cases = [1 << a | 1 << b for a, b in itertools.combinations(range(8), 2)]
    for i in range(192):
        additional_high = [
            sum(1 << a for a in rng.sample(range(3), 2))
            | sum(1 << b for b in rng.sample(range(3, 8), rng.randrange(1, 5)))
            for _ in range(rng.randrange(6))
        ]
        highs = fixed_high + additional_high if i % 7 else []
        low = rng.sample(cases, rng.randrange(1, len(cases) + 1))
        affiliations = highs + low
        rng.shuffle(affiliations)
        compare(affiliations, 8)

    roster_outcomes = []
    if control_rosters is not None:
        for path in sorted(control_rosters.glob("*.txt")):
            try:
                affiliations, blocks, _ = affiliation_masks(path)
                if len(affiliations) > 70:
                    continue
                report_pairs = count_pair_residuals(affiliations, blocks, collect_pairs=True)
            except ValueError:
                continue
            compare(affiliations, blocks, report_pairs)
            roster_outcomes.append({"file": path.name,
                                    "candidate_pairs": report_pairs[0]["candidate_pairs"],
                                    "residual_pairs": report_pairs[0]["residual_pairs"]})
    for name, outcomes in exercised.items():
        if not outcomes["covered"] or (name != "high_high" and not outcomes["residual"]):
            raise AssertionError(f"control set missed {name}: {outcomes}")
    return {
        "exhaustive_fixed_high_cases": 1 << len(choices),
        "randomized_cases": 192,
        "compatible_existing_rosters": roster_outcomes,
        "pair_outcomes_cross_checked": exercised,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roster", type=Path)
    parser.add_argument("--expected-candidates", type=int)
    parser.add_argument("--controls", action="store_true")
    parser.add_argument("--control-rosters", type=Path)
    args = parser.parse_args()
    start = time.monotonic()
    affiliations, blocks, digest = affiliation_masks(args.roster)
    result, _ = count_pair_residuals(affiliations, blocks)
    if args.expected_candidates is not None and result["candidate_pairs"] != args.expected_candidates:
        raise AssertionError((args.expected_candidates, result["candidate_pairs"]))
    result["input"] = args.roster.name
    result["input_sha256"] = digest
    result["stage_wall_seconds"] = time.monotonic() - start
    if args.controls:
        result["controls"] = small_controls(args.control_rosters)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
