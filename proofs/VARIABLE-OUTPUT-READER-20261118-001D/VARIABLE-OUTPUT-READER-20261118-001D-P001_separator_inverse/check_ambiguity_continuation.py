"""Continue the reachable width-20 loose/shared scalar transposition."""

from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import json

import check_continuation as continuation


SOURCE = continuation.WIDTH20 + "full.json"
SOURCE_SHA256 = "fe8942c22071b913e6362e95012a2ac7e6dd63a12c8bdb2b257cfca04953adcc"


def operands(gluing, checks):
    holders, adjacent = gluing.incidence(checks)
    loose = sorted(bit for bit, users in holders.items() if len(users) == 1)
    for size in (1, 2, 3):
        for inputs in combinations(loose, size):
            if gluing.legal_parents([holders[bit][0] for bit in inputs], adjacent):
                yield inputs


def triples(gluing, checks):
    return frozenset(frozenset(action) for action in operands(gluing, checks) if len(action) == 3)


def measure(gluing, checks):
    width = len(gluing.incidence(checks)[0])
    table = gluing.scalar_table(continuation.cut_supports(gluing, checks), width)
    return continuation.dense(table, width)


def in_span(word, checks):
    basis = {}
    for scope in checks:
        row = sum(1 << bit for bit in scope)
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    while word:
        pivot = word.bit_length() - 1
        if pivot not in basis:
            return False
        word ^= basis[pivot]
    return True


def compare_complete(api, observed):
    """Full isometries factor into quotient maps and internal twin permutations."""
    classes = defaultdict(list)
    counts = Counter(full_table_classes=0, isometric_pairs_of_indexed_observations=0, triple_menu_conflicts=0)
    first = None
    for label, matrix, family in observed:
        quotient = api.Quotient.make(matrix)
        order, _, generators = quotient.automorphisms()
        counts["automorphisms_across_fixtures"] += order
        for perm in generators:
            assert api.disagreement(matrix, matrix, perm) is None
            counts["generators_checked"] += 1
            if api.transported(family, perm) != family:
                counts["triple_menu_conflicts"] += 1
                if first is None:
                    first = {"left": label, "right": label, "permutation": perm}
        bucket = classes[quotient.colored.invariant]
        for prior in bucket:
            old_label, old_matrix, old_family, old_quotient, count = prior
            match = next(api.isometries(quotient.colored, old_quotient.colored), None)
            if match is None:
                continue
            perm = quotient.lift(old_quotient, match)
            assert api.disagreement(matrix, old_matrix, perm) is None
            counts["isometric_pairs_of_indexed_observations"] += count
            prior[-1] += 1
            if api.transported(family, perm) != old_family:
                counts["triple_menu_conflicts"] += 1
                if first is None:
                    first = {"left": label, "right": old_label, "permutation": perm}
            break
        else:
            bucket.append([label, matrix, family, quotient, 1])
            counts["full_table_classes"] += 1
    return {**dict(counts), "first_conflict": first}


def first_two(gluing, api, checks, swap):
    layer = [(checks, ())]
    result = []
    for depth in (1, 2):
        next_layer = []
        tables = []
        counts = Counter(with_legal_triples=0, legal_triples=0, original_swap_still_scalar=0,
                         original_swap_still_scalar_after_using_14=0)
        widths = Counter()
        for before, history in layer:
            width = len(gluing.incidence(before)[0])
            for action, fresh_count in product(operands(gluing, before), (2, 3)):
                n = width + fresh_count
                fresh = tuple(range(width, n))
                grown = (*before, (*action, *fresh))
                moves = (*history, (action, fresh))
                assert gluing.replay(grown)[-1]["consumed"] == list(action)
                family = triples(gluing, grown)
                matrix = measure(gluing, grown)
                p = (*swap, *range(20, n))
                scalar = api.disagreement(matrix, matrix, p) is None
                assert api.transported(family, p) == family
                counts["with_legal_triples"] += bool(family)
                counts["legal_triples"] += len(family)
                counts["original_swap_still_scalar"] += scalar
                counts["original_swap_still_scalar_after_using_14"] += scalar and any(14 in use for use, _ in moves)
                widths[n] += 1
                next_layer.append((grown, moves))
                tables.append((moves, matrix, family))
        result.append({"appended_joins": depth, "literal_histories": len(next_layer), "width_counts": dict(widths),
                       **dict(counts), **compare_complete(api, tables)})
        layer = next_layer
    return result


def offshoot(anchor):
    return ((anchor, 20, 21, 22), (20, 23, 24), (21, 25, 26), (22, 27, 28),
            (23, 25, 29, 30), (24, 27, 31, 32), (26, 28, 33, 34))


def graft_controls(api, gluing, checks, base, swap, state_image):
    whole = []
    retained = []
    reports = []
    for anchor in (14, 15, 17):
        tail = offshoot(anchor)
        grown = (*checks, *tail)
        gluing.replay(grown)
        assert not in_span(state_image, grown)
        matrix = measure(gluing, grown)
        family = triples(gluing, grown)
        assert len(family) == 8 and all(min(mark) >= 29 for mark in family)
        boundary_and_new = (anchor, *range(20, 35))
        local_index = {bit: i for i, bit in enumerate(boundary_and_new)}
        local = tuple(tuple(local_index[bit] for bit in scope) for scope in tail)
        graft = measure(gluing, local)
        assert continuation.dense(gluing.scalar_table(gluing.minimal_dual(local), 16), 16) == graft
        cross_count = 0
        for a, b in combinations(range(35), 2):
            if b < 20:
                expected = base[a][b]
            elif a in local_index:
                expected = graft[local_index[a]][local_index[b]]
            else:
                expected = base[a][anchor] + graft[0][local_index[b]] - 1
                cross_count += 1
            assert matrix[a][b] == expected
        p = (*swap, *range(20, 35))
        difference = api.disagreement(matrix, matrix, p)
        assert (difference is None) == (anchor != 14)
        distances = None
        if difference is not None:
            a, b = difference
            distances = [matrix[a][b], matrix[p[a]][p[b]]]
        assert api.transported(family, p) == family
        separators, misses = continuation.separator_components(matrix, grown)
        assert not misses
        crop = sum(1 << bit for bit in boundary_and_new)
        assert all(continuation.retain(len(matrix), separators, mark) == crop for mark in family)
        whole.append((anchor, matrix, family))
        retained.append((anchor, graft, api.transported(family, local_index)))
        reports.append({"anchor": anchor, "width": len(matrix), "adjoined_stars": tail,
                        "legal_triples": sorted(tuple(sorted(action)) for action in family),
                        "original_swap_still_scalar": difference is None,
                        "first_pair_moved_to_another_distance": difference,
                        "distances_before_and_after_swap": distances,
                        "previous_nongenerator_still_absent_from_dual": True,
                        "distances_checked_across_anchor": cross_count,
                        "retained_distinctions": sorted(boundary_and_new)})
    return {"one_bit_grafts": reports, "full_table_isometries": compare_complete(api, whole),
            "retained_table_isometries": compare_complete(api, retained)}


def main():
    root = Path(__file__).resolve().parents[3]
    raw = (root / SOURCE).read_bytes()
    assert sha256(raw).hexdigest() == SOURCE_SHA256
    witness = json.loads(raw)["controls"]["first_singleton_mismatch"]
    assert witness["fixture"]["roster_index"] == 12350
    _, api, gluing = (continuation.load(root, path, digest) for path, digest in continuation.SOURCES)
    checks = tuple(map(tuple, witness["fixture"]["checks_in_birth_order"]))
    swap = tuple(witness["bit_permutation"])
    assert [(i, j) for i, j in enumerate(swap) if i != j] == [(13, 14), (14, 13)]
    gluing.replay(checks)
    original = measure(gluing, checks)
    direct = gluing.scalar_table(gluing.minimal_dual(checks), 20)
    assert continuation.dense(direct, 20) == original
    assert api.disagreement(original, original, swap) is None and not triples(gluing, checks)
    image = sum(1 << swap[bit] for bit in checks[8])
    assert not in_span(image, checks)

    holders, adjacent = gluing.incidence(checks)
    assert holders[13] == [6, 8] and holders[14] == [6]
    loose_parents = {sites[0] for sites in holders.values() if len(sites) == 1}
    assert loose_parents == {6, 7, 8} and adjacent[6] == {2, 3, 8}
    permanently_exhausted = (adjacent[2] | adjacent[3] | {2, 3}) - {6}
    assert not loose_parents & permanently_exhausted
    assert 7 not in adjacent[8]
    stages = first_two(gluing, api, checks, swap)
    assert [row["literal_histories"] for row in stages] == [24, 600]
    assert all(row["legal_triples"] == 0 and row["triple_menu_conflicts"] == 0 for row in stages)
    result = {"source": SOURCE, "source_sha256": SOURCE_SHA256, "roster_index": 12350,
              "full_scalar_transposition": swap, "actual_support_at_8": checks[8],
              "support_image_outside_the_dual": sorted(swap[bit] for bit in checks[8]),
              "shared_bit_and_users": [13, holders[13]], "loose_bit_and_holder": [14, holders[14]],
              "neighbors_of_holder_6": sorted(adjacent[6]),
              "permanently_exhausted_sites_around_2_3": sorted(permanently_exhausted),
              "first_two_literal_continuation_layers": stages,
              **graft_controls(api, gluing, checks, original, swap, image)}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
