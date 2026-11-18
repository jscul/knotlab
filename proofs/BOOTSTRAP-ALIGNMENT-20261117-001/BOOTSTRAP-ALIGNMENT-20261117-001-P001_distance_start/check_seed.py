"""Replay the literal cut seed and compare the first two parity commitments.

Old indices encode the predecessor's proof coordinates for replay and grading.
The bond-table oracle sees only the unordered allowed rows and their width.
"""

import json
import sys
from collections import Counter
from itertools import combinations, permutations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from knotlab import Relation, check_knot


OLD = tuple(range(8))
AXES = (4, 2, 1)
FIRST = (8, 9)
SECOND = (10, 11)
SOURCE = (
    "proofs/CUBIC-FROM-A-KNOT-20261117-001/"
    "CUBIC-FROM-A-KNOT-20261117-001-P001_local_growth/cube_interface.md"
)


def require(condition, detail):
    if not condition:
        raise AssertionError(detail)


def bit(row, position):
    return (row >> position) & 1


def named(position):
    return f"{position:03b}" if position < 8 else "pquv"[position - 8]


def cut_words(placement):
    words = [sum(int(bool(point & axis)) << i for i, point in enumerate(placement))
             for axis in AXES]
    return frozenset((0, 255, *words, *(word ^ 255 for word in words)))


def between_rows(knots, shown):
    mask = sum(1 << i for i in shown)
    return frozenset(row for row in range(256) if row & mask == row and
                     all(bit(row, a) != bit(row, c) or bit(row, b) == bit(row, a)
                         for a, b, c in knots))


def seed_rows():
    # The source replay chooses the first seed corner c=100 and opposite 010.
    steps = [
        (4, 0, 2),
        (6, ((4, 6, 2), (0, 4, 6), (0, 2, 6))),
        (5, ((2, 4, 5),)),
        *((x | 1, ((5, x | 1, x), (4, 5, x | 1), (4, x, x | 1)))
          for x in (0, 2, 6)),
    ]
    # Directly test every assignment of the final eight distinctions. Prefix
    # counts use the clauses introduced through that step without later filters.
    shown = set(steps[0])
    knots = [steps[0]]
    counts = {}
    for stop in range(len(steps)):
        if stop:
            fresh, new_knots = steps[stop]
            shown.add(fresh)
            knots.extend(new_knots)
        rows = between_rows(knots, shown)
        counts[len(shown)] = len(rows)
    require(rows == cut_words(OLD), "Literal betweenness missed the cut rows")
    require(counts == {3: 6, 4: 6, 5: 8, 6: 8, 7: 8, 8: 8}, counts)
    for positions in knots:
        relation = allowed_projection(rows, positions)
        require(len(relation.rows) == 6 and canonical_knot(relation), positions)
    a, b, c = knots[-1]
    wrong = between_rows([*knots[:-1], (b, a, c)], shown)
    require(wrong != rows, "Changing a literal middle role passed")
    control = {"changed_triple": list(map(named, (b, a, c))), "allowed_states": len(wrong)}
    return rows, knots, counts, control


def allowed_projection(rows, positions):
    return Relation(tuple(map(named, positions)), frozenset(
        tuple(bool(bit(row, i)) for i in positions) for row in rows))


def canonical_knot(relation):
    return check_knot(relation, relation.variables[:-1], relation.variables[-1]).is_knot


def parity_extension(rows, width, inputs, fresh_count=2):
    require(fresh_count >= 1, "A conservative parity attachment needs a fresh output")
    mask = sum(1 << i for i in inputs)
    free_patterns = 1 << (fresh_count - 1)
    extended = set()
    for row in rows:
        old_parity = (row & mask).bit_count() % 2
        for low in range(free_patterns):
            last_bit = old_parity ^ (low.bit_count() % 2)
            extended.add(row | (low << width) | (last_bit << (width + fresh_count - 1)))
    require(len(extended) == free_patterns * len(rows) and
            {row & ((1 << width) - 1) for row in extended} == rows, inputs)
    return frozenset(extended)


def bond_table(rows, width):
    """Return complete scalar bond distances and the minimal nonfree supports."""
    require(bool(rows), "K3 requires a nonempty relation")
    table = [[None] * width for _ in range(width)]
    for i in range(width):
        table[i][i] = 0
    free = {0}
    supports = []
    # A full (k-1)-coordinate projection requires at least 2**(k-1) rows.
    for size in range(1, min(width, len(rows).bit_length()) + 1):
        for support in combinations(range(width), size):
            mask = sum(1 << i for i in support)
            if any(mask ^ (1 << i) not in free for i in support):
                continue
            if len({row & mask for row in rows}) == 1 << size:
                free.add(mask)
                continue
            supports.append(support)
            # Binary ties still prevent larger supports from passing K2.
            if size >= 3:
                for i, j in combinations(support, 2):
                    if table[i][j] is None:
                        table[i][j] = table[j][i] = size - 1
    return tuple(tuple(line) for line in table), supports


def check_oracle(rows, width, supports):
    expected = {support for support in supports if len(support) >= 3}
    direct = {
        support
        for size in range(3, min(width, len(rows).bit_length()) + 1)
        for support in combinations(range(width), size)
        if canonical_knot(allowed_projection(rows, support))
    }
    require(direct == expected, {"missing": direct - expected, "extra": expected - direct})
    return len(direct)


def record(rows, table, supports):
    width = len(table)
    return {
        "allowed_states": len(rows),
        "variable_order": [named(i) for i in range(width)],
        "matrix": table,
        "bond_counts_by_support_size": dict(Counter(len(s) for s in supports if len(s) >= 3)),
        "pair_counts_by_bond_distance": dict(Counter(
            str(table[i][j]) if table[i][j] is not None else "infinite"
            for i, j in combinations(range(width), 2)
        )),
    }


def matrix_in_order(table, order):
    return tuple(tuple(table[i][j] for j in order) for i in order)


def commitment_census(rows, seed_table):
    require(all(seed_table[i][j] == 2 for i, j in combinations(OLD, 2)), seed_table)
    rooted_samples = {}
    second_samples = {}
    second_normal_forms = {}
    second_grades = {role: Counter() for role in ("r", "p", "q")}
    fixed_layer_direction_matches = Counter()
    rooted_normal_form = None
    for root in OLD:
        rooted = parity_extension(rows, 8, (root,))
        table, supports = bond_table(rooted, 10)
        require(canonical_knot(allowed_projection(rooted, (root, *FIRST))), root)
        ordered = matrix_in_order(table, (root, *(i for i in OLD if i != root), *FIRST))
        if rooted_normal_form is None:
            rooted_normal_form = ordered
        require(ordered == rooted_normal_form, ("rooted normalized matrix", root))
        require(all(table[i][j] == 2 for i, j in combinations(OLD, 2)) and
                all(table[i][j] == (2 if i == root else 3) for i in OLD for j in FIRST)
                and table[8][9] == 2, ("rooted scalar formula", root))
        if root == 0:
            rooted_samples = record(rooted, table, supports)
            rooted_samples["root"] = named(root)
            rooted_samples["canonical_tool_confirmed_bonds"] = check_oracle(rooted, 10, supports)
        for other in OLD:
            if other == root:
                continue
            distance = (root ^ other).bit_count()
            for role, incoming in zip(("r", "p", "q"), (root, *FIRST)):
                second = parity_extension(rooted, 10, (incoming, other))
                table, supports = bond_table(second, 12)
                require(canonical_knot(allowed_projection(second, (incoming, other, *SECOND))),
                        (root, incoming, other))
                unrelated = tuple(i for i in OLD if i not in (root, other))
                normal = matrix_in_order(table, (root, other, *unrelated, *FIRST, *SECOND))
                require(normal == second_normal_forms.setdefault(role, normal),
                        ("second normalized matrix", root, role, other))
                # Every permutation of the six other old indices is generated
                # by their adjacent transpositions. The table admits them all.
                order = list(range(12))
                for i in range(2, 7):
                    order[i], order[i + 1] = order[i + 1], order[i]
                    require(matrix_in_order(normal, order) == normal, (root, role, other, i))
                    order[i], order[i + 1] = order[i + 1], order[i]
                second_grades[role][distance] += 1
                difference = root ^ other
                layer_direction = AXES[-1]
                if difference in ((layer_direction,) if role == "r" else AXES[:-1]):
                    fixed_layer_direction_matches[role] += 1
                if root == 0 and other in (1, 7):
                    sample = record(second, table, supports)
                    sample.update(root=named(root), old_output=named(other), incoming=role,
                                  original_coordinate_step_distance=distance)
                    second_samples[f"{role}-{distance}"] = sample
    # The good and bad examples even have identical labeled numeric matrices
    # after the named old output is transported to the new position.
    require(all(grades == {1: 24, 2: 24, 3: 8} for grades in second_grades.values()),
            second_grades)
    require(fixed_layer_direction_matches == {"r": 8, "p": 16, "q": 16},
            fixed_layer_direction_matches)
    return rooted_samples, {
        "roots_checked": 8,
        "commitments_checked": sum(sum(grades.values()) for grades in second_grades.values()),
        "per_incoming_role_counts_by_original_coordinate_step_distance": second_grades,
        "matches_with_fixed_layer_direction_and_interchangeable_other_axes":
            dict(fixed_layer_direction_matches),
        "normalized_variable_order": ["root", "old output", *(f"other {i + 1}" for i in range(6)),
                                      "p", "q", "u", "v"],
        "normalized_scalar_matrices": second_normal_forms,
        "examples": second_samples,
    }


def placements(rows):
    # A placement maps each fixed old name to a proof coordinate. Permuting
    # names changes none of the observed normalized scalar matrices above.
    pair_counts = Counter()
    pinned_roots = Counter()
    literal_roots = Counter()
    signed_roots = Counter()
    aliases = {frozenset(row ^ flip for row in rows) for flip in rows}
    count = 0
    for placement in permutations(OLD):
        count += 1
        root = placement.index(0)
        pinned_roots[root] += 1
        implied_rows = cut_words(placement)
        if implied_rows == rows:
            literal_roots[root] += 1
        if implied_rows in aliases:
            signed_roots[root] += 1
        for other in OLD:
            if root != other:
                pair_counts[root, other, placement[other].bit_count()] += 1
    for root, other in permutations(OLD, 2):
        require([pair_counts[root, other, d] for d in (1, 2, 3)] == [2160, 2160, 720],
                (root, other))
    require(count == 40320 and set(pinned_roots.values()) == {5040}, pinned_roots)
    require(set(literal_roots.values()) == {6} and set(signed_roots.values()) == {24},
            (literal_roots, signed_roots))
    return {
        "all_old_permutations": count,
        "scalar_compatible_permutations_per_pin_to_origin": dict(pinned_roots),
        "fixed_root_and_old_output_counts_by_placed_step_distance": {1: 2160, 2: 2160, 3: 720},
        "permutations_matching_literal_cut_rows": sum(literal_roots.values()),
        "permutations_matching_up_to_independent_value_flips": sum(signed_roots.values()),
        "different_common_value_cut_relations_in_signed_class": len(aliases),
    }


def signed_witness(rows):
    # Changing the common reference row to y trades the y-neighbor of 000 for
    # its opposite. The grading bases are (x,y,z) and (y,x+y,y+z) over F2.
    root, other = 0, 2
    flip = sum(int(bool(point & 2)) << point for point in OLD)
    signed = frozenset(row ^ flip for row in rows)
    placed = tuple(4 * bit(point, 1) + 2 * (bit(point, 2) ^ bit(point, 1)) +
                   (bit(point, 1) ^ bit(point, 0)) for point in OLD)
    require(signed != rows and signed == cut_words(placed), placed)
    old_steps = (root ^ other).bit_count()
    signed_steps = (placed[root] ^ placed[other]).bit_count()
    require((old_steps, signed_steps) == (1, 3), placed)

    # Rebuild both row sets from the same literal parity equations. The flip
    # at the last fresh output is the parity of the flips at the inputs.
    table_stages = []
    for label, base, alternate, mask, width, inputs, fresh in (
        ("rooted attachment", rows, signed, flip, 8, (root,), 2),
        ("pair parity query", rows, signed, flip, 8, (root, other), 1),
        ("two-fresh parity query", rows, signed, flip, 8, (root, other), 2),
        ("three-fresh parity query", rows, signed, flip, 8, (root, other), 3),
        ("triple parity query", rows, signed, flip, 8, (0, 1, 2), 1),
    ):
        stage, base, alternate, mask = signed_stage(label, base, alternate, mask, width, inputs, fresh)
        table_stages.append(stage)
        if label == "rooted attachment":
            for incoming in (root, *FIRST):
                second, *_ = signed_stage("second commitment via " + named(incoming),
                                          base, alternate, mask, 10, (incoming, other), 2)
                table_stages.append(second)
    seed_matches = bond_table(rows, 8)[0] == bond_table(signed, 8)[0]
    require(seed_matches, "Signed seed matrices differ")
    return {
        "pair": [named(root), named(other)],
        "old_and_alternate_coordinate_step_distances": [old_steps, signed_steps],
        "old_flip_mask": flip,
        "alternate_allowed_rows_lsb_first": sorted(signed),
        "alternate_placement_in_old_name_order": [named(point) for point in placed],
        "seed_scalar_tables_equal": seed_matches,
        "extension_stages": table_stages,
    }


def signed_stage(label, base, alternate, flip, width, inputs, fresh):
    left = parity_extension(base, width, inputs, fresh)
    right = parity_extension(alternate, width, inputs, fresh)
    transported = flip | ((sum(bit(flip, i) for i in inputs) % 2) << (width + fresh - 1))
    require(right == {row ^ transported for row in left}, ("complete flip mismatch", label))
    table, supports = bond_table(left, width + fresh)
    require(table == bond_table(right, width + fresh)[0], ("scalar mismatch", label))
    result = record(left, table, supports)
    result.update(stage=label, inputs=list(map(named, inputs)), extended_flip_mask=transported)
    return result, left, right, transported


def main():
    # Count and identify extensions independently, including ordinary three-fresh moves.
    for old in (0, 1):
        for fresh_count in range(1, 5):
            expected = frozenset(word for word in range(1 << (1 + fresh_count))
                                 if word & 1 == old and word.bit_count() % 2 == 0)
            require(parity_extension({old}, 1, (0,), fresh_count) == expected, (old, fresh_count))
    rows, knots, row_counts, wrong_middle = seed_rows()
    table, supports = bond_table(rows, 8)
    seed = record(rows, table, supports)
    seed.update(allowed_rows_lsb_first=sorted(rows),
                literal_betweenness_triples=[list(map(named, knot)) for knot in knots],
                row_counts_by_prefix_width=row_counts,
                wrong_middle_control=wrong_middle,
                canonical_tool_confirmed_bonds=check_oracle(rows, 8, supports))
    first, second = commitment_census(rows, table)
    print(json.dumps({
        "source": SOURCE,
        "infinite_entry": None,
        "cut_seed": seed,
        "first_commitment": first,
        "second_commitments": second,
        "blind_placements": placements(rows),
        "signed_witness": signed_witness(rows),
    }, indent=2))


if __name__ == "__main__":
    main()
