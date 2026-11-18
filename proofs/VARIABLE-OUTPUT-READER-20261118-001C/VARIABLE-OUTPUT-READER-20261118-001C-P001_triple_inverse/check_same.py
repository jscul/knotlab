"""Check every one-bit gluing of the two archived width-19 marked hosts."""

from collections import Counter
from hashlib import sha256
from itertools import combinations, permutations, product
from pathlib import Path
import json

import check_gluing as gluing


SIDE = 19
WIDTH = 2 * SIDE - 1


def named_copy(checks, names):
    return tuple(tuple(names[bit] for bit in support) for support in checks)


def joined_table(left, right, a, b, names):
    result = dict(left)
    for (x, y), value in right.items():
        result[tuple(sorted((names[x], names[y])))] = value
    for x, y in product(range(SIDE), repeat=2):
        if x != a and y != b:
            first, second = gluing.delta(left, a, x), gluing.delta(right, b, y)
            result[x, names[y]] = None if first is None or second is None else first + second - 1
    assert len(result) == WIDTH * (WIDTH - 1) // 2
    return result


def dense(table, width):
    matrix = [[0] * width for _ in range(width)]
    for (a, b), value in table.items():
        assert value is not None
        matrix[a][b] = matrix[b][a] = value
    return matrix


def legal_triples(checks):
    holders, adjacent = gluing.incidence(checks)
    loose = sorted(bit for bit, sites in holders.items() if len(sites) == 1)
    return {triple for triple in combinations(loose, 3)
            if gluing.legal_parents([holders[bit][0] for bit in triple], adjacent)}


def triangle(matrix, marked):
    a, b, c = marked
    return matrix[a][b], matrix[a][c], matrix[b][c]


def exterior(matrix, marked):
    a, b, c = marked
    return tuple(sorted((matrix[a][i], matrix[b][i], matrix[c][i])
                        for i in range(len(matrix)) if i not in marked))


def observation(matrix, marked, internal):
    return (internal, min(exterior(matrix, order) for order in permutations(marked)
                          if triangle(matrix, order) == internal))


def check_all_triples(matrix, actual):
    signatures = {}
    for marked in sorted(actual):
        internal = tuple(sorted(triangle(matrix, marked)))
        signatures[observation(matrix, marked, internal)] = marked
    triangles = {internal for internal, _ in signatures}
    comparisons = 0
    for marked in combinations(range(len(matrix)), 3):
        internal = tuple(sorted(triangle(matrix, marked)))
        if marked in actual or internal not in triangles:
            continue
        comparisons += 1
        key = observation(matrix, marked, internal)
        assert key not in signatures, ("opposite triple verdicts in one arrangement", signatures.get(key), marked)
    return comparisons


def archived_overlap(matrix, left, right):
    target = Counter(exterior(matrix, left))
    internal = triangle(matrix, left)
    options = [sum((target & Counter(exterior(matrix, order))).values())
               for order in permutations(right) if triangle(matrix, order) == internal]
    return len(options), max(options, default=0)


def main():
    root = Path(__file__).resolve().parents[3]
    raw = (root / gluing.SOURCE).read_bytes()
    assert sha256(raw).hexdigest() == gluing.DIGEST
    archive = json.loads(raw)
    left, right = (tuple(map(tuple, archive[side]["junction_supports"]))
                   for side in ("legal_side", "forbidden_side"))
    marks_left, marks_right = (tuple(archive[side]["marked"])
                               for side in ("legal_side", "forbidden_side"))
    for checks, side in ((left, "legal_side"), (right, "forbidden_side")):
        replay = gluing.replay(checks)
        assert [[step["parents"], len(step["fresh"])] for step in replay] == archive[side]["history"]

    plans = [gluing.unmarked_anchor_replays(checks, ()) for checks in (left, right)]
    loose_left, loose_right = (plan["unmarked_loose_bits_tested"] for plan in plans)
    attach_left, attach_right = (plan["successful_orders_by_anchor"] for plan in plans)
    table_left, table_right = (gluing.scalar_table(gluing.minimal_dual(checks), SIDE)
                               for checks in (left, right))
    assert marks_left in legal_triples(left) and marks_right not in legal_triples(right)
    assert archived_overlap_across_hosts(table_left, table_right, marks_left, marks_right) == SIDE - 3

    cases = []
    history_count = 0
    direct_control = None
    best_archived = 0
    for a, b in product(loose_left, loose_right):
        if a not in attach_left and b not in attach_right:
            continue
        fresh = iter(range(SIDE, WIDTH))
        names = tuple(a if bit == b else next(fresh) for bit in range(SIDE))
        renamed = named_copy(right, names)
        # The single shared incidence is the only contact between the two
        # pieces. In any order its first far-side vertex must use it as a
        # unary input. Interleaving cannot supply another shared neighbor.
        hosts = []
        if b in attach_right:
            order = (*left, *(renamed[i] for i in attach_right[b]))
            assert gluing.replay(order)[len(left)]["consumed"] == [a]
            hosts.append("legal_side")
        if a in attach_left:
            order = (*renamed, *(left[i] for i in attach_left[a]))
            assert gluing.replay(order)[len(right)]["consumed"] == [a]
            hosts.append("forbidden_side")
        history_count += len(hosts)

        checks = (*left, *renamed)
        table = joined_table(table_left, table_right, a, b, names)
        matrix = dense(table, WIDTH)
        actual = legal_triples(checks)
        archived_right = tuple(names[bit] for bit in marks_right)
        opposite = (marks_left in actual) != (tuple(sorted(archived_right)) in actual)
        assert opposite == (a not in marks_left)
        matches, overlap = archived_overlap(matrix, marks_left, archived_right) if opposite else (0, 0)
        if opposite:
            assert overlap < WIDTH - 3
            best_archived = max(best_archived, overlap)
        comparisons = check_all_triples(matrix, actual)

        if opposite and direct_control is None:
            supports = gluing.minimal_dual(checks)
            assert table == gluing.scalar_table(supports, WIDTH)
            direct_control = {"anchor_pair": [a, b], "full_pair_entries": len(table),
                              "junctions": len(checks), "dual_words": 1 << len(checks),
                              "minimal_bonds": len(supports)}
        cases.append({"anchor_pair": [a, b], "admissible_seed_sides": hosts,
                      "old_marked_legality_opposed": opposite,
                      "old_mark_orders_with_same_internal_distances": matches,
                      "best_shared_old_mark_exterior_columns": overlap if opposite else None,
                      "legal_triples": len(actual), "forbidden_triples_with_matching_internal_shape": comparisons})

    assert cases and direct_control is not None
    print(json.dumps({
        "source": gluing.SOURCE, "source_sha256": gluing.DIGEST, "width": WIDTH,
        "all_loose_anchors": [loose_left, loose_right],
        "successful_graft_orders_by_anchor": [attach_left, attach_right],
        "loose_anchor_pairs": len(loose_left) * len(loose_right),
        "reachable_anchor_pairs": len(cases), "reachable_labeled_seed_orientations": history_count,
        "reachable_pairs_with_opposite_archived_verdicts": sum(c["old_marked_legality_opposed"] for c in cases),
        "archived_choices_permutations_checked_per_opposed_pair": 6,
        "exterior_columns_per_marking": WIDTH - 3, "best_archived_exterior_overlap": best_archived,
        "candidate_triples_checked": len(cases) * (WIDTH * (WIDTH - 1) * (WIDTH - 2) // 6),
        "legal_triples_over_reachable_pairs": sum(c["legal_triples"] for c in cases),
        "forbidden_triples_needing_full_marked_signature":
            sum(c["forbidden_triples_with_matching_internal_shape"] for c in cases),
        "opposite_verdicts_with_identical_marked_rows": 0,
        "direct_dual_control": direct_control,
        "cases": cases,
    }, indent=2, sort_keys=True))


def archived_overlap_across_hosts(left, right, marks_left, marks_right):
    l, r = dense(left, SIDE), dense(right, SIDE)
    target = Counter(exterior(l, marks_left))
    internal = triangle(l, marks_left)
    return max((sum((target & Counter(exterior(r, order))).values())
                for order in permutations(marks_right) if triangle(r, order) == internal), default=0)


if __name__ == "__main__":
    main()
