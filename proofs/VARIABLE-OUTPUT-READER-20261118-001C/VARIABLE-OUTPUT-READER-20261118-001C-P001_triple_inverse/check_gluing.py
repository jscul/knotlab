"""Refute the width-19 reduced triple observation by a one-bit attachment."""

from collections import Counter, defaultdict
from functools import cache
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import json


SOURCE = (
    "proofs/VARIABLE-OUTPUT-READER-20261118-001B/"
    "VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen/near_witness.json"
)
DIGEST = "960ec63a1a23da44e6c70a489fd8bd27f6ab6152efe8a7599c47a72b2adb42da"
HOST_WIDTH = 19
GADGET_WIDTH = 9
WIDTH = HOST_WIDTH + GADGET_WIDTH - 1
HOST_ANCHOR = 16
GADGETS = (
    (3, ((0, 1, 3), (0, 2, 4), (1, 5, 6), (2, 7, 8))),
    (4, ((0, 1, 4), (0, 2, 5), (1, 3, 6), (2, 3, 7, 8))),
)


def bit_indices(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def incidence(checks):
    holders = defaultdict(list)
    adjacent = [set() for _ in checks]
    for site, scope in enumerate(checks):
        assert scope and len(scope) == len(set(scope))
        for bit in scope:
            holders[bit].append(site)
    for users in holders.values():
        assert len(users) in (1, 2)
        if len(users) == 2:
            a, b = users
            assert b not in adjacent[a]
            adjacent[a].add(b)
            adjacent[b].add(a)
    return holders, adjacent


def legal_parents(parents, adjacent):
    return (1 <= len(parents) <= 3 and len(set(parents)) == len(parents)
            and all(adjacent[a] & adjacent[b] for a, b in combinations(parents, 2))
            and (len(parents) < 3 or not set.intersection(*(adjacent[a] for a in parents))))


def replay(checks):
    """Validate the actual old operands and the number of genuinely fresh bits."""
    records = []
    for site, scope in enumerate(checks):
        holders, adjacent = incidence(checks[:site])
        consumed = sorted(bit for bit in scope if bit in holders)
        fresh = sorted(set(scope) - holders.keys())
        if site == 0:
            assert not consumed and len(fresh) == 3
            parents = []
        else:
            assert 2 <= len(fresh) <= 3 and all(len(holders[bit]) == 1 for bit in consumed)
            parents = sorted(holders[bit][0] for bit in consumed)
            assert legal_parents(parents, adjacent), (site, parents, adjacent)
        records.append({"parents": parents, "consumed": consumed, "fresh": fresh})
    return records


def unmarked_anchor_replays(checks, marks):
    """For each eligible anchor, decide if any order can grow the whole piece."""
    holders, adjacent = incidence(checks)
    all_sites = frozenset(range(len(checks)))

    @cache
    def finish(seen):
        if seen == all_sites:
            return ()
        available = [neighbors & seen for neighbors in adjacent]
        for site in sorted(all_sites - seen):
            parents = sorted(available[site])
            if len(checks[site]) - len(parents) in (2, 3) and legal_parents(parents, available):
                tail = finish(seen | {site})
                if tail is not None:
                    return (site, *tail)
        return None

    tested = sorted(bit for bit, used in holders.items() if len(used) == 1 and bit not in marks)
    result = {}
    for bit in tested:
        root, = holders[bit]
        if len(checks[root]) in (3, 4):
            rest = finish(frozenset((root,)))
            if rest is not None:
                result[bit] = (root, *rest)
    return {"unmarked_loose_bits_tested": tested, "successful_orders_by_anchor": result}


def minimal_dual(checks):
    """Enumerate the complete dual and retain inclusion-minimal supports."""
    span = [0]
    for scope in checks:
        word = sum(1 << bit for bit in scope)
        span += [row ^ word for row in span]
    assert len(span) == len(set(span)) == 1 << len(checks)
    minimal = []
    for word in sorted(span[1:], key=lambda row: (row.bit_count(), row)):
        if not any(word & other == other for other in minimal):
            assert word.bit_count() >= 3
            minimal.append(word)
    return frozenset(minimal)


def scalar_table(supports, width):
    table = dict.fromkeys(combinations(range(width), 2), None)
    for word in sorted(supports, key=lambda row: (row.bit_count(), row)):
        for pair in combinations(bit_indices(word), 2):
            if table[pair] is None:
                table[pair] = word.bit_count() - 1
    return table


def delta(table, a, b):
    return table[tuple(sorted((a, b)))]


def packed_image(word, names):
    return sum(1 << names[bit] for bit in bit_indices(word))


def anchor_histogram(table, width, anchor):
    return Counter(delta(table, anchor, bit) for bit in range(width) if bit != anchor)


def display_histogram(histogram):
    return {"infinity" if value is None else str(value): count for value, count in histogram.items()}


def marked_permission(checks, marked):
    holders, adjacent = incidence(checks)
    assert all(len(holders[bit]) == 1 for bit in marked)
    parents = [holders[bit][0] for bit in marked]
    return {"actual_marked_inputs": marked, "parents": parents,
            "common_neighbors_by_parent_pair": [sorted(adjacent[a] & adjacent[b])
                                                for a, b in combinations(parents, 2)],
            "neighbors_common_to_all": sorted(set.intersection(*(adjacent[a] for a in parents))),
            "legal_triple": legal_parents(parents, adjacent)}


def attach(host_data, gadget_anchor, gadget):
    checks = tuple(map(tuple, host_data["junction_supports"]))
    marks = tuple(host_data["marked"])
    assert HOST_ANCHOR not in marks
    assert len(incidence(checks)[0][HOST_ANCHOR]) == len(incidence(gadget)[0][gadget_anchor]) == 1
    assert all(bit in range(HOST_WIDTH) for scope in checks for bit in scope)
    new = iter(range(HOST_WIDTH, WIDTH))
    names = tuple(HOST_ANCHOR if bit == gadget_anchor else next(new) for bit in range(GADGET_WIDTH))
    glued = (*checks, *(tuple(names[bit] for bit in scope) for scope in gadget))
    history = replay(glued)
    prefix = len(checks)
    assert [[step["parents"], len(step["fresh"])] for step in history[:prefix]] == host_data["history"]
    assert history[prefix]["consumed"] == [HOST_ANCHOR]
    assert len(history) == 12 and len(incidence(glued)[0]) == WIDTH
    old_result = marked_permission(checks, marks)
    actual_result = marked_permission(glued, marks)
    assert old_result == actual_result and old_result["legal_triple"] == host_data["legal_marked_input"]

    host_bonds = minimal_dual(checks)
    gadget_bonds = minimal_dual(gadget)
    lifted = frozenset(packed_image(word, names) for word in gadget_bonds)
    anchor = 1 << HOST_ANCHOR
    # A mixed dual support can be minimal only when both summands use the
    # shared bit. It then cancels, and each summand must be minimal on its side.
    cross_bonds = {left ^ right for left, right in product(host_bonds, lifted)
                   if left & anchor and right & anchor}
    observed = minimal_dual(glued)
    assert observed == host_bonds | lifted | cross_bonds
    assert len(observed) == len(host_bonds) + len(lifted) + len(cross_bonds)

    old_table = scalar_table(host_bonds, HOST_WIDTH)
    gadget_table = scalar_table(gadget_bonds, GADGET_WIDTH)
    table = scalar_table(observed, WIDTH)
    assert all(table[pair] == distance for pair, distance in old_table.items())
    assert all(delta(table, names[a], names[b]) == d for (a, b), d in gadget_table.items())
    host_four, gadget_four = (sum(value == 4 for value in component.values())
                             for component in (old_table, gadget_table))
    host_hist = anchor_histogram(old_table, HOST_WIDTH, HOST_ANCHOR)
    gadget_hist = anchor_histogram(gadget_table, GADGET_WIDTH, gadget_anchor)
    cross_four = cross_pairs = 0
    for a, b in product(range(HOST_WIDTH), range(GADGET_WIDTH)):
        if a == HOST_ANCHOR or b == gadget_anchor:
            continue
        left, right = delta(old_table, a, HOST_ANCHOR), delta(gadget_table, gadget_anchor, b)
        expected = None if left is None or right is None else left + right - 1
        assert delta(table, a, names[b]) == expected
        cross_four += expected == 4
        cross_pairs += 1
    assert cross_four == host_hist[2] * gadget_hist[3] + host_hist[3] * gadget_hist[2]
    total_four = sum(distance == 4 for distance in table.values())
    assert total_four == host_four + gadget_four + cross_four
    return table, gadget_table, names, {
        "junctions_in_birth_order": glued,
        "literal_history_with_actual_operands": history,
        "marked_triple_permission": actual_result,
        "gadget_junctions_on_local_bits": gadget,
        "gadget_local_to_glued_bits": names,
        "gadget_local_anchor": gadget_anchor,
        "host_anchor_row_histogram": display_histogram(host_hist),
        "gadget_anchor_row_histogram": display_histogram(gadget_hist),
        "host_reroot_control": unmarked_anchor_replays(checks, marks),
        "host_gadget_and_cross_distance_four": [host_four, gadget_four, cross_four],
        "full_distance_four_count": total_four,
        "full_distance_four_parity": total_four % 2,
        "all_cross_distances_checked_by_formula": cross_pairs,
        "host_gadget_and_cross_bond_counts": [len(host_bonds), len(gadget_bonds), len(cross_bonds)],
        "direct_dual_words": 1 << len(glued),
        "allowed_state_count_by_rank": 1 << (WIDTH - len(glued)),
        "full_upper_triangle": [table[pair] for pair in combinations(range(WIDTH), 2)],
    }


def row_transport(left, right, t_left, t_right):
    classes = []
    for table, anchor in ((left, t_left), (right, t_right)):
        groups = defaultdict(list)
        for bit in range(GADGET_WIDTH):
            if bit != anchor:
                groups[delta(table, bit, anchor)].append(bit)
        classes.append(groups)
    left_groups, right_groups = classes
    assert left_groups.keys() == right_groups.keys()
    mapping = {t_left: t_right}
    for distance, bits in left_groups.items():
        mapping.update(zip(bits, right_groups[distance], strict=True))
    return mapping


def main():
    root = Path(__file__).resolve().parents[3]
    artifact = (root / SOURCE).read_bytes()
    assert sha256(artifact).hexdigest() == DIGEST
    origin = json.loads(artifact)
    left_anchor, left_gadget = GADGETS[0]
    right_anchor, right_gadget = GADGETS[1]
    left, left_part, left_names, good = attach(origin["legal_side"], left_anchor, left_gadget)
    right, right_part, right_names, bad = attach(origin["forbidden_side"], right_anchor, right_gadget)
    assert good["marked_triple_permission"]["legal_triple"] and not bad["marked_triple_permission"]["legal_triple"]
    assert good["host_anchor_row_histogram"] == bad["host_anchor_row_histogram"]
    assert good["gadget_anchor_row_histogram"] == bad["gadget_anchor_row_histogram"]
    host_map = origin["map_legal_to_forbidden"]
    assert host_map[HOST_ANCHOR] == HOST_ANCHOR
    gadget_map = row_transport(left_part, right_part, left_anchor, right_anchor)
    mapping = list(host_map) + [None] * (WIDTH - HOST_WIDTH)
    for old, new in gadget_map.items():
        mapping[left_names[old]] = right_names[new]
    assert set(mapping) == set(range(WIDTH))
    marks = good["marked_triple_permission"]["actual_marked_inputs"]
    assert tuple(mapping[bit] for bit in marks) == bad["marked_triple_permission"]["actual_marked_inputs"]
    assert good["full_distance_four_parity"] == bad["full_distance_four_parity"]
    assert good["full_distance_four_count"] != bad["full_distance_four_count"]

    differences = []
    marked_entries = 0
    for (a, b), distance in left.items():
        image = delta(right, mapping[a], mapping[b])
        if a in marks or b in marks:
            assert image == distance
            marked_entries += 1
        if image != distance:
            differences.append({"left_bits": [a, b], "right_bits": [mapping[a], mapping[b]],
                                "distances": [distance, image]})
    assert marked_entries == 3 * (WIDTH - 3) + 3 and differences

    # Supplying the legal side's gadget to both hosts preserves the marked
    # rows while leaving the original parity mismatch visible.
    same_gadget, _, _, match = attach(origin["forbidden_side"], left_anchor, left_gadget)
    same_map = (*host_map, *range(HOST_WIDTH, WIDTH))
    assert all(distance == delta(same_gadget, same_map[a], same_map[b])
               for (a, b), distance in left.items() if a in marks or b in marks)
    assert good["full_distance_four_parity"] != match["full_distance_four_parity"]
    print(json.dumps({
        "source": SOURCE, "source_sha256": DIGEST, "width": WIDTH, "host_anchor_bit": HOST_ANCHOR,
        "legal_side": good, "forbidden_side": bad, "map_legal_to_forbidden": mapping,
        "matching_pairs_with_at_least_one_marked_endpoint": marked_entries,
        "full_table_entries_compared": len(left), "entries_differing_under_marked_map": len(differences),
        "first_full_table_difference": differences[0],
        "full_tables_nonisomorphic_witness": [good["full_distance_four_count"], bad["full_distance_four_count"]],
        "same_gadget_control": {"matching_marked_entries": marked_entries,
                                "full_distance_four_counts": [good["full_distance_four_count"],
                                                              match["full_distance_four_count"]]},
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
