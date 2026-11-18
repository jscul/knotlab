"""Exact reachable controls for two three-fresh additions and the rank gap."""

import importlib.util
import json
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from random import Random


PROOFS = Path(__file__).resolve().parents[2]
F_PATH = (PROOFS / "VARIABLE-OUTPUT-READER-20261118-001F"
          / "VARIABLE-OUTPUT-READER-20261118-001F-P001_finite_interval" / "audit.py")
C_PATH = (PROOFS / "VARIABLE-OUTPUT-READER-20261118-001C"
          / "VARIABLE-OUTPUT-READER-20261118-001C-P001_triple_inverse" / "check_witness.py")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


linear = load("two_three_fresh_primal", F_PATH)
cuts = load("two_three_fresh_cuts", C_PATH)


CORE = (
    (0, 1, 2),
    (0, 3, 4),
    (1, 5, 6),
    (2, 7, 8),
    (3, 5, 9, 10),
    (4, 7, 11, 12),
    (6, 8, 13, 14),
    (10, 15, 16),
)
TAIL = ((15, 17, 18, 19), (16, 20, 21, 22), (17, 23, 24), (23, 25, 26))
CAP = (9, 11, 13, 19, 22)
MARK = (9, 11, 13)


def measured(checks, width):
    scalar, bond_count = linear.scalar_minima(checks, width)
    cut_table, bonds, span = cuts.scalar_table(checks, width)
    assert scalar == tuple(bytes(width if value is None else value for value in row) for row in cut_table)
    assert len(bonds) == bond_count
    assert span == set(linear.dependent_supports(linear.primal_columns(checks, width)))
    return scalar, bond_count, span, linear.permissions(checks)


def literal_replay(checks, width, scalar, span):
    linear.replay_history(checks, tuple(range(len(checks))))
    rows = {0}
    held = set()
    trace = []
    for check in checks:
        old = tuple(i for i in check if i in held)
        fresh = tuple(i for i in check if i not in held)
        state_mask = linear.mask(check)
        outside = [linear.mask(fresh[i] for i in linear.active_bits(word)) for word in range(1 << len(fresh))]
        extended = {row | word for row in rows for word in outside if not ((row | word) & state_mask).bit_count() % 2}
        old_mask = linear.mask(held)
        assert {row & old_mask for row in extended} == rows
        held.update(fresh)
        trace.append({"operands": old, "fresh": fresh})
        rows = extended
    assert len(held) == width and len(rows) * len(span) == 1 << width
    row_basis = cuts.independent_rows(rows)
    assert len(rows) == 1 << len(row_basis)
    assert all(not (row & check).bit_count() % 2 for row in row_basis for check in span)
    table_hash = sha256(b"".join(scalar)).hexdigest()
    row_hash = sha256(b"".join(row.to_bytes((width + 7) // 8, "little") for row in sorted(rows))).hexdigest()
    return rows, trace, table_hash, row_hash


def by_renaming(checks, width, scalar, span, legal, seed):
    image = list(range(width))
    Random(seed).shuffle(image)

    def mapped(group):
        return tuple(sorted(image[i] for i in group))

    renamed = tuple(mapped(check) for check in checks)
    linear.replay_history(renamed, tuple(range(len(renamed))))
    other, _, other_span, other_legal = measured(renamed, width)
    assert all(scalar[i][j] == other[image[i]][image[j]] for i, j in combinations(range(width), 2))
    assert {linear.mask(mapped(tuple(linear.active_bits(word)))) for word in span} == other_span
    assert {mapped(triple) for triple in legal} == other_legal
    return image


def examine(checks, width, expected_three_fresh):
    scalar, count, span, legal = measured(checks, width)
    rows, trace, table_hash, row_hash = literal_replay(checks, width, scalar, span)
    assert sum(len(event["fresh"]) == 3 for event in trace[1:]) == expected_three_fresh
    result = {
        "checks": checks,
        "history": trace,
        "width": width,
        "junction_arity_counts": dict(sorted(Counter(map(len, checks)).items())),
        "three_fresh_additions_after_seed": expected_three_fresh,
        "rank": len(span).bit_length() - 1,
        "allowed_rows": len(rows),
        "allowed_rows_sha256": row_hash,
        "full_table_sha256": table_hash,
        "bonds": count,
        "all_pair_entries_checked": width * (width - 1) // 2,
        "pair_histogram": dict(sorted(Counter(scalar[i][j] for i,j in combinations(range(width), 2)).items())),
        "actual_legal_triples": sorted(legal),
        "independent_named_relabeling": by_renaming(checks, width, scalar, span, legal, 813 + len(checks)),
    }
    return result, scalar, span, rows, legal


def matched_rank_example():
    first, left, left_span, left_rows, left_menu = examine((*CORE, *TAIL), 27, 2)
    second, right, right_span, right_rows, right_menu = examine((*CORE, CAP, *TAIL), 27, 0)
    assert max(first["junction_arity_counts"]) <= 4
    assert first["rank"] == 12 and second["rank"] == 13 == 1 + (27 - 3) // 2
    assert right_rows < left_rows and left_span < right_span
    assert {word for word in left_span if word.bit_count() <= 4} == {
        word for word in right_span if word.bit_count() <= 4}
    assert all(min(left[i][j], 4) == min(right[i][j], 4) for i,j in combinations(range(27), 2))
    assert MARK in left_menu and MARK not in right_menu
    assert first["pair_histogram"] != second["pair_histogram"]
    assert left[9][11] == 5 and right[9][11] == 4
    cap_output_minima = (left[19][22] + 1, right[19][22] + 1)
    assert cap_output_minima[0] >= 6 and cap_output_minima[1] == 5
    rejected_row = min(left_rows - right_rows)
    assert (rejected_row & linear.mask(CAP)).bit_count() % 2
    return {
        "original": first,
        "all_two_fresh_rival": second,
        "extra_rival_equation": CAP,
        "opposing_mark": MARK,
        "threshold_K_through_four_entries_equal": 27 * 26 // 2,
        "named_pair_disagreement": {"pair": (9, 11), "bond_distances": (left[9][11], right[9][11])},
        "cap_fresh_output_pair": {"pair": (19, 22), "minimum_bond_sizes": cap_output_minima},
        "full_histograms_differ": True,
        "ones_of_an_original_row_rejected_by_rival": tuple(linear.active_bits(rejected_row)),
    }


def layered_example():
    checks = [(0, 1, 2)]
    available = [[0, 1, 2]]
    width = 3

    def add(parents, count):
        nonlocal width
        joint = len(checks)
        taken = [available[i].pop(0) for i in parents]
        fresh = list(range(width, width + count))
        width += count
        checks.append(tuple(taken + fresh))
        available.append(fresh)
        return joint

    current = tuple(add((0,), fresh) for fresh in (3, 3, 2))
    for _ in range(3):
        current = tuple(add(parents, 2) for parents in combinations(current, 2))
    assert width == 29
    result, _, _, _, menu = examine(tuple(checks), width, 2)
    assert max(result["junction_arity_counts"]) <= 4
    chosen = tuple(available[i][0] for i in current)
    assert chosen in menu and len(menu) == 8
    return {"presentation": result, "one_legal_triple": chosen}


def separated_groups(items, linked):
    unseen = set(items)
    components = set()
    while unseen:
        first = unseen.pop()
        reached = {first}
        todo = [first]
        while todo:
            site = todo.pop()
            following = {other for other in unseen if linked(site, other)}
            reached.update(following)
            unseen.difference_update(following)
            todo.extend(following)
        components.add(frozenset(reached))
    return components


def bounded_partition(table, anchor, cutoff):
    def linked(a, b):
        ab, at, bt = table[a][b], table[a][anchor], table[anchor][b]
        return ab <= cutoff and (at > cutoff or bt > cutoff or ab != at + bt - 2)

    return separated_groups(set(range(len(table))) - {anchor}, linked)


def large_frontier_bridge_control():
    # The accepted fourteen-junction history has the four-bit frontier below.
    births = ((0,), (1,), (0, 2), (1, 3), (2, 4), (3, 5), (0, 6),
              (5, 7), (2, 8), (1, 7, 9), (4, 8, 10), (3, 9, 11), (6, 10, 12))
    checks = [(0, 1, 2)]
    loose = [[0, 1, 2]]
    size = 3
    for i, parents in enumerate(births, start=1):
        used = [loose[site].pop(0) for site in parents]
        fresh = list(range(size, size + (3 if i <= 3 else 2)))
        size += len(fresh)
        checks.append(tuple(used + fresh))
        loose.append(fresh)
    assert size == 32 and tuple(name for group in loose for name in group) == (27, 29, 30, 31)
    frontier = (27, 29, 30, 31)
    cases = {}
    bounded_cases = {}
    for width, junctions in ((32, tuple(checks)), (34, (*checks, (27, 32, 33)))):
        linear.replay_history(junctions, tuple(range(len(junctions))))
        distances, _, span, _ = measured(junctions, width)
        assert linear.mask(frontier) in span
        assert all(distances[i][j] < width for i, j in combinations(range(width), 2))
        owners = [tuple(site for site, check in enumerate(junctions) if bit in check) for bit in range(width)]
        bounded_tables = {
            cutoff: tuple(tuple(0 if a == b else min(distance + 1, cutoff + 1)
                                for b, distance in enumerate(row))
                          for a, row in enumerate(distances))
            for cutoff in (3, 4, 5)
        }
        bounded = {cutoff: {"partitions_checked": width, "mismatched_deletions": [],
                            "first_difference": None, "separating_distinctions": {}}
                   for cutoff in bounded_tables}
        found = {}
        for anchor in range(width):
            remaining = set(range(width)) - {anchor}
            measured_parts = separated_groups(
                remaining, lambda a, b: distances[a][b] != distances[a][anchor] + distances[anchor][b] - 1
            )
            ordinary_edges = {tuple(owners[i]) for i in remaining if len(owners[i]) == 2}
            physical_sites = separated_groups(range(len(junctions)),
                                               lambda a, b: tuple(sorted((a, b))) in ordinary_edges)
            physical_parts = {frozenset(name for name in remaining if owners[name][0] in group)
                              for group in physical_sites}
            assert measured_parts == physical_parts
            if len(measured_parts) > 1:
                found[anchor] = sorted(map(len, measured_parts))
            for cutoff, table in bounded_tables.items():
                report = bounded[cutoff]
                short_parts = bounded_partition(table, anchor, cutoff)
                if len(short_parts) > 1:
                    report["separating_distinctions"][anchor] = sorted(map(len, short_parts))
                if short_parts != physical_parts:
                    report["mismatched_deletions"].append(anchor)
                    if report["first_difference"] is None:
                        report["first_difference"] = {"deleted": anchor,
                                                      "cutoff_part_sizes": sorted(map(len, short_parts)),
                                                      "physical_part_sizes": sorted(map(len, physical_parts))}
        cases[width] = {"physical_and_scalar_partitions_agreed": width, "separating_distinctions": found}
        assert bounded[5]["separating_distinctions"] == found
        assert not bounded[5]["mismatched_deletions"]
        assert all(bounded[cutoff]["mismatched_deletions"] == list(range(width)) for cutoff in (3, 4))
        bounded_cases[width] = bounded
    assert not cases[32]["separating_distinctions"]
    assert cases[34]["separating_distinctions"] == {27: [2, 31]}
    return {"base_checks": checks, "four_bit_frontier": frontier,
            "attached_unary_check": (27, 32, 33), "verified": cases, "bounded_K_replay": bounded_cases}


def run():
    return {
        "source_hashes": {"primal_rank_checker": sha256(F_PATH.read_bytes()).hexdigest(),
                          "cut_checker": sha256(C_PATH.read_bytes()).hexdigest()},
        "width_27_rank_gap_at_equal_short_observation": matched_rank_example(),
        "width_29_three_live_holders_in_layered_history": layered_example(),
        "mixed_large_frontier_bridge_control": large_frontier_bridge_control(),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
