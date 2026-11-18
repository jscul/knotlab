"""Grade the actual next-input sets over every width-eighteen table isometry.

Every isometry maps distance-twin classes to distance-twin classes. The
quotient records their sizes and internal colors. Quotient isometries lift
by any bijection within those classes, so one lift and the in-class
transposition generators suffice for each quotient map.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from itertools import combinations, combinations_with_replacement, permutations, product
import json
from math import comb, factorial, prod


WIDTH = 18
INFINITY = WIDTH


def ranked(signatures):
    palette = {signature: i for i, signature in enumerate(sorted(set(signatures)))}
    return tuple(palette[signature] for signature in signatures)


def refine(matrix, initial):
    """A shared invariant that filters, but never decides, isomorphism."""
    colors = ranked(initial)
    rounds = [tuple(sorted(Counter(initial).items()))]
    while True:
        signatures = tuple((color, tuple(sorted((colors[j], value)
                                                 for j, value in enumerate(row) if i != j)))
                           for i, (color, row) in enumerate(zip(colors, matrix, strict=True)))
        rounds.append(tuple(sorted(Counter(signatures).items())))
        following = ranked(signatures)
        if len(set(colors)) == len(set(following)):
            return tuple(rounds), following
        colors = following


@dataclass(frozen=True)
class ColoredMatrix:
    matrix: tuple
    invariant: tuple
    colors: tuple

    @classmethod
    def make(cls, matrix, initial):
        invariant, colors = refine(matrix, initial)
        return cls(matrix, invariant, colors)


def isometries(left, right):
    if left.invariant != right.invariant:
        return
    choices = {i: tuple(j for j, color in enumerate(right.colors) if color == left.colors[i])
               for i in range(len(left.matrix))}
    mapping = [-1] * len(left.matrix)

    def visit(domains):
        if not domains:
            yield tuple(mapping)
            return
        a = min(domains, key=lambda i: (len(domains[i]), i))
        for b in domains[a]:
            following = {i: tuple(j for j in possible if j != b and left.matrix[a][i] == right.matrix[b][j])
                         for i, possible in domains.items() if i != a}
            if all(following.values()):
                mapping[a] = b
                yield from visit(following)

    yield from visit(choices)


@dataclass(frozen=True)
class Quotient:
    blocks: tuple
    colored: ColoredMatrix

    @classmethod
    def make(cls, matrix):
        blocks = []
        for i in range(len(matrix)):
            for block in blocks:
                j = block[0]
                if all(matrix[i][k] == matrix[j][k] for k in range(len(matrix)) if k not in (i, j)):
                    block.append(i)
                    break
            else:
                blocks.append([i])
        colors = tuple((len(block), matrix[block[0]][block[1]] if len(block) > 1 else 0)
                       for block in blocks)
        small = tuple(tuple(matrix[a[0]][b[0]] for b in blocks) for a in blocks)
        return cls(tuple(map(tuple, blocks)), ColoredMatrix.make(small, colors))

    def lift(self, target, mapping):
        result = [-1] * sum(map(len, self.blocks))
        for a, b in enumerate(mapping):
            for x, y in zip(self.blocks[a], target.blocks[b], strict=True):
                result[x] = y
        return tuple(result)

    def automorphisms(self):
        width = sum(map(len, self.blocks))
        identity = tuple(range(width))
        block_maps = tuple(isometries(self.colored, self.colored))
        generators = []
        for block in self.blocks:
            for x in block[1:]:
                swap = list(identity)
                swap[block[0]], swap[x] = swap[x], swap[block[0]]
                generators.append(tuple(swap))
        for mapping in block_maps:
            lifted = self.lift(self, mapping)
            if lifted != identity:
                generators.append(lifted)
        group_order = len(block_maps) * prod(factorial(len(block)) for block in self.blocks)
        return group_order, len(block_maps), tuple(generators)

    def all_automorphisms(self):
        width = sum(map(len, self.blocks))
        for mapping in isometries(self.colored, self.colored):
            for targets in product(*(permutations(self.blocks[j]) for j in mapping)):
                lifted = [-1] * width
                for block, image in zip(self.blocks, targets, strict=True):
                    for a, b in zip(block, image, strict=True):
                        lifted[a] = b
                yield tuple(lifted)


def disagreement(left, right, mapping):
    return next(((a, b) for a, b in combinations(range(len(left)), 2)
                 if left[a][b] != right[mapping[a]][mapping[b]]), None)


def transported(menu, mapping):
    return frozenset(frozenset(mapping[i] for i in action) for action in menu)


def inverse(mapping):
    result = [-1] * len(mapping)
    for i, j in enumerate(mapping):
        result[j] = i
    return tuple(result)


def dense(table, cutoff):
    pairs = tuple(combinations(range(WIDTH), 2))
    assert table.keys() == set(pairs)
    result = [[0] * WIDTH for _ in range(WIDTH)]
    for a, b in pairs:
        distance = table[a, b]
        assert distance is None or 2 <= distance < WIDTH
        value = INFINITY if distance is None else distance
        if cutoff is not None:
            value = min(value, cutoff + 1)
        result[a][b] = result[b][a] = value
    return tuple(map(tuple, result))


@dataclass(frozen=True)
class Member:
    index: int
    to_rep: tuple
    normalized_menu: frozenset
    bad_generator: tuple | None


@dataclass
class TableClass:
    matrix: tuple
    quotient: Quotient
    group_order: int
    quotient_order: int
    generators: tuple
    members: list = field(default_factory=list)

    @classmethod
    def make(cls, matrix, quotient):
        group_order, quotient_order, generators = quotient.automorphisms()
        assert all(disagreement(matrix, matrix, mapping) is None for mapping in generators)
        return cls(matrix, quotient, group_order, quotient_order, generators)

    def grade(self, index, menu, mapping):
        normalized = transported(menu, mapping)
        bad = None
        for generator in self.generators:
            if transported(normalized, generator) != normalized and bad is None:
                bad = generator
        member = Member(index, mapping, normalized, bad)
        self.members.append(member)
        return member


def build_classes(records, matrices):
    buckets = defaultdict(list)
    classes = []
    memberships = {}
    candidate_comparisons = 0
    for index, (record, matrix) in enumerate(zip(records, matrices, strict=True)):
        quotient = Quotient.make(matrix)
        bucket = buckets[quotient.colored.invariant]
        for entry in bucket:
            candidate_comparisons += 1
            iso = next(isometries(quotient.colored, entry.quotient.colored), None)
            if iso is not None:
                mapping = quotient.lift(entry.quotient, iso)
                assert disagreement(matrix, entry.matrix, mapping) is None
                break
        else:
            entry = TableClass.make(matrix, quotient)
            classes.append(entry)
            bucket.append(entry)
            mapping = tuple(range(WIDTH))
        memberships[index] = entry, entry.grade(index, record.menu, mapping)
    return classes, memberships, candidate_comparisons


def connected_fixture(fixture):
    width = len(fixture.loose_counts)
    meetings = {tuple(sorted(pair)) for pair in fixture.meetings}
    matrix = tuple(tuple(int(tuple(sorted((a, b))) in meetings) for b in range(width))
                   for a in range(width))
    return ColoredMatrix.make(matrix, tuple(fixture.loose_counts))


def target_indices(records, target):
    """Locate the producer's physical target even if its history was quotiented."""
    expected = connected_fixture(target)
    return {i for i, record in enumerate(records)
            if len(record.fixture.loose_counts) == len(target.loose_counts)
            and next(isometries(expected, connected_fixture(record.fixture)), None) is not None}


def pairs_by_depth(depths):
    return Counter({(a, b): comb(depths[a], 2) if a == b else depths[a] * depths[b]
                    for a, b in combinations_with_replacement(sorted(depths), 2)})


def manifest_counts(depths):
    return {",".join(map(str, pair)): count for pair, count in sorted(depths.items()) if count}


def pair_is_bad(left, right):
    return bool(left.bad_generator or right.bad_generator or left.normalized_menu != right.normalized_menu)


def witness_iso(left, right):
    # If the normalized menus agree but are noninvariant, precompose with
    # the witnessed change. Otherwise the stored representative maps suffice.
    right_inverse = inverse(right.to_rep)
    if left.normalized_menu == right.normalized_menu and left.bad_generator is not None:
        return tuple(right_inverse[left.bad_generator[i]] for i in left.to_rep)
    return tuple(right_inverse[i] for i in left.to_rep)


def fixture_record(records, index, target_set):
    fixture = records[index].fixture
    return {"roster_index": index, "junctions": len(fixture.loose_counts), "history": fixture.history,
            "ordinary_meetings": fixture.meetings, "loose_counts": fixture.loose_counts,
            "is_target_presentation": index in target_set}


def witness(records, source, target_set, full, viewed, left, right, mapping):
    assert disagreement(viewed[left.index], viewed[right.index], mapping) is None
    differing = disagreement(full[left.index], full[right.index], mapping)
    graded = transported(records[left.index].menu, mapping)
    menu = records[right.index].menu
    extra = sorted(tuple(sorted(action)) for action in graded - menu)
    missing = sorted(tuple(sorted(action)) for action in menu - graded)
    result = {"left": fixture_record(records, left.index, target_set),
              "right": fixture_record(records, right.index, target_set),
              "observation_class_contains_target": any(member.index in target_set for member in source.members),
              "left_bit_maps_to_right_bit": mapping,
              "preserves_full_table": differing is None,
              "menu_sizes": [len(graded), len(menu)],
              "image_action_not_allowed_on_right": extra[0] if extra else None,
              "right_action_missing_in_image": missing[0] if missing else None}
    if differing is not None:
        a, b = differing
        left_d = full[left.index][a][b]
        right_d = full[right.index][mapping[a]][mapping[b]]
        result["first_changed_full_distance"] = {
            "left_bits": [a, b], "right_bits": [mapping[a], mapping[b]],
            "distances": [None if value == INFINITY else value for value in (left_d, right_d)],
        }
    return result


def summarize(records, target_set, full, viewed, census, depth):
    classes, memberships, comparisons = census
    by_depth = {d: Counter(fixtures=depth.count(d)) for d in sorted(set(depth))}
    duplicate_pairs = Counter()
    conflict_pairs = Counter()
    duplicate_choice = conflict_choice = self_choice = None
    witnessed_permutations = maps_within_fixtures = maps_between_fixtures = 0
    for entry in classes:
        members = sorted(entry.members, key=lambda m: (depth[m.index], m.index))
        distribution = Counter(depth[m.index] for m in members)
        duplicates = pairs_by_depth(distribution)
        good = defaultdict(Counter)
        for member in members:
            bucket = by_depth[depth[member.index]]
            bucket["duplicate_table_fixtures"] += int(len(members) > 1)
            bucket["menu_changing_automorphism_fixtures"] += int(member.bad_generator is not None)
            witnessed_permutations += len(entry.generators)
            if member.bad_generator is None:
                good[member.normalized_menu][depth[member.index]] += 1
            else:
                key = (depth[member.index], member.index)
                if self_choice is None or key < self_choice[0]:
                    self_choice = key, entry, member
        safe = Counter()
        for counts in good.values():
            safe.update(pairs_by_depth(counts))
        conflicts = duplicates - safe
        duplicate_pairs.update(duplicates)
        conflict_pairs.update(conflicts)
        maps_within_fixtures += entry.group_order * len(members)
        maps_between_fixtures += entry.group_order * comb(len(members), 2)
        for d in distribution:
            by_depth[d]["table_classes_represented"] += 1
        if len(members) > 1:
            left, right = members[:2]
            key = (depth[left.index], depth[right.index], left.index, right.index)
            if duplicate_choice is None or key < duplicate_choice[0]:
                duplicate_choice = key, entry, left, right
        if conflicts:
            left = members[0]
            right = next(member for member in members[1:] if pair_is_bad(left, member))
            key = (depth[left.index], depth[right.index], left.index, right.index)
            if conflict_choice is None or key < conflict_choice[0]:
                conflict_choice = key, entry, left, right

    target_classes = [entry for entry in classes if any(m.index in target_set for m in entry.members)]
    result = {
        "table_classes": len(classes),
        "exact_quotient_comparisons_after_invariants": comparisons,
        "fixtures_by_junction_count": dict(by_depth),
        "duplicate_table_classes": sum(len(entry.members) > 1 for entry in classes),
        "duplicate_pairs_by_junction_counts": manifest_counts(duplicate_pairs),
        "menu_conflict_pairs_by_junction_counts": manifest_counts(conflict_pairs),
        "automorphisms_counted_by_group_orders": maps_within_fixtures,
        "isometries_between_distinct_fixtures_counted_one_direction": maps_between_fixtures,
        "generator_checks_on_actual_menus": witnessed_permutations,
        "largest_quotient_automorphism_group": max(entry.quotient_order for entry in classes),
        "target_classes": [{"members_by_junction_count": dict(Counter(depth[m.index] for m in entry.members)),
                            "menu_conflict_with_target": any(pair_is_bad(memberships[i][1], m)
                                                             for i in target_set
                                                             if memberships[i][0] is entry
                                                             for m in entry.members),
                            "table_automorphisms": entry.group_order}
                           for entry in target_classes],
        "first_duplicate_table_pair": None,
        "first_conflict_between_fixtures": None,
        "first_menu_changing_automorphism": None,
    }
    if duplicate_choice is not None:
        _, entry, left, right = duplicate_choice
        mapping = tuple(inverse(right.to_rep)[i] for i in left.to_rep)
        result["first_duplicate_table_pair"] = witness(records, entry, target_set, full, viewed,
                                                       left, right, mapping)
    if conflict_choice is not None:
        _, entry, left, right = conflict_choice
        result["first_conflict_between_fixtures"] = witness(records, entry, target_set, full, viewed,
                                                          left, right, witness_iso(left, right))
    if self_choice is not None:
        _, entry, member = self_choice
        result["first_menu_changing_automorphism"] = witness(records, entry, target_set, full, viewed,
                                                           member, member, witness_iso(member, member))
    return result, (duplicate_pairs, conflict_pairs)


def threshold_only(records, target_set, full, clipped, depth, full_census, clipped_census):
    _, exact, _ = full_census
    clipped_classes, _, _ = clipped_census
    duplicate_choice = conflict_choice = self_choice = None
    for entry in clipped_classes:
        members = sorted(entry.members, key=lambda m: (depth[m.index], m.index))
        for member in members:
            before = exact[member.index][1]
            if member.bad_generator and before.bad_generator is None:
                key = (depth[member.index], member.index)
                if self_choice is None or key < self_choice[0]:
                    self_choice = key, entry, member
        for left, right in combinations(members, 2):
            before_left, before_right = exact[left.index], exact[right.index]
            key = (depth[left.index], depth[right.index], left.index, right.index)
            together = before_left[0] is before_right[0]
            if not together and (duplicate_choice is None or key < duplicate_choice[0]):
                duplicate_choice = key, entry, left, right
            before_bad = together and pair_is_bad(before_left[1], before_right[1])
            if pair_is_bad(left, right) and not before_bad and (conflict_choice is None or key < conflict_choice[0]):
                conflict_choice = key, entry, left, right

    def describe(choice, change_menu):
        if choice is None:
            return None
        _, entry, left, right = choice
        if change_menu:
            mapping = witness_iso(left, right)
        else:
            right_inverse = inverse(right.to_rep)
            mapping = tuple(right_inverse[i] for i in left.to_rep)
        checked = witness(records, entry, target_set, full, clipped, left, right, mapping)
        assert not checked["preserves_full_table"]
        return checked

    same = (*self_choice, self_choice[-1]) if self_choice is not None else None
    return {"first_new_duplicate_table_pair": describe(duplicate_choice, False),
            "first_new_conflict_between_fixtures": describe(conflict_choice, True),
            "first_new_menu_changing_automorphism": describe(same, True)}


def remap_word(word, mapping):
    return sum(1 << image for i, image in enumerate(mapping) if word & (1 << i))


def independent_menu(checks):
    owners = defaultdict(list)
    neighbors = {parent: set() for parent in checks}
    for parent, star in checks.items():
        for bit in star:
            owners[bit].append(parent)
    for holders in owners.values():
        assert len(holders) in (1, 2)
        if len(holders) == 2:
            a, b = holders
            neighbors[a].add(b)
            neighbors[b].add(a)
    loose = sorted(bit for bit, holders in owners.items() if len(holders) == 1)
    menu = set()
    for size in (1, 2, 3):
        for bits in combinations(loose, size):
            parents = {owners[bit][0] for bit in bits}
            if len(parents) == size and all(neighbors[a] & neighbors[b] for a, b in combinations(parents, 2)):
                if size < 3 or not set.intersection(*(neighbors[parent] for parent in parents)):
                    menu.add(frozenset(bits))
    return frozenset(menu)


def literal_reference(checks):
    """Build states first, then obtain bonds from their dual, independently of the scout."""
    equations = [sum(1 << bit for bit in star) for star in checks.values()]
    rows = frozenset(word for word in range(1 << WIDTH)
                     if all(not ((word & equation).bit_count() & 1) for equation in equations))
    pivots = {}
    for word in rows:
        while word:
            pivot = word.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = word
                break
            word ^= pivots[pivot]
    assert len(rows) == 1 << len(pivots)
    dual = frozenset(word for word in range(1 << WIDTH)
                     if all(not ((word & row).bit_count() & 1) for row in pivots.values()))
    bonds = []
    table = dict.fromkeys(combinations(range(WIDTH), 2), None)
    for support in sorted(dual - {0}, key=lambda word: (word.bit_count(), word)):
        if any(support & other == other for other in bonds):
            continue
        bonds.append(support)
        bits = [i for i in range(WIDTH) if support & (1 << i)]
        assert len(bits) >= 3 and len({word & support for word in rows}) == 1 << (len(bits) - 1)
        assert all(len({word & (support ^ (1 << i)) for word in rows}) == 1 << (len(bits) - 1) for i in bits)
        for pair in combinations(bits, 2):
            if table[pair] is None:
                table[pair] = len(bits) - 1
    return rows, dual, table, len(bonds)


def self_conflict_witnesses(records, target_set, full, census):
    _, memberships, _ = census
    results = []
    for i, (entry, member) in sorted(memberships.items()):
        if member.bad_generator is None:
            continue
        record = records[i]
        checks = record.fixture.checks()
        rows, dual, table, bond_count = literal_reference(checks)
        menu = independent_menu(checks)
        assert menu == record.menu and table == record.table and dual == record.span
        quotient = Quotient.make(full[i])
        group = tuple(quotient.all_automorphisms())
        assert len(group) == len(set(group)) == entry.group_order
        star_masks = tuple(sum(1 << bit for bit in star) for star in checks.values())
        parent_order = sorted(checks)
        prefix = {parent: checks[parent] for parent in parent_order[:-1]}
        last = frozenset(checks[parent_order[-1]])
        affected = Counter()
        examples = {}
        state_example = None
        tally = Counter(automorphisms=len(group), menu_changing=0, stars_preserved=0,
                        rows_preserved=0, menu_changing_with_stars_preserved=0,
                        menu_changing_with_rows_preserved=0)
        preferred = witness_iso(member, member)
        assert preferred in group
        for mapping in (preferred, *(p for p in group if p != preferred)):
            assert disagreement(full[i], full[i], mapping) is None
            same_stars = transported(record.stars, mapping) == record.stars
            same_rows = all(remap_word(word, mapping) in dual for word in star_masks)
            tally["stars_preserved"] += same_stars
            tally["rows_preserved"] += same_rows
            illegal = {action for action in menu if frozenset(mapping[bit] for bit in action) not in menu}
            if not illegal:
                continue
            tally["menu_changing"] += 1
            tally["menu_changing_with_stars_preserved"] += same_stars
            tally["menu_changing_with_rows_preserved"] += same_rows
            if same_rows:
                fixes_prefix = all(frozenset(mapping[bit] for bit in star) == frozenset(star)
                                   for star in prefix.values())
                cost = (not fixes_prefix, sum(a != b for a, b in enumerate(mapping)), mapping)
                if state_example is None or cost < state_example:
                    state_example = cost
            for size in {len(action) for action in illegal}:
                affected[size] += 1
                if size not in examples:
                    action = min(tuple(sorted(action)) for action in illegal if len(action) == size)
                    examples[size] = {"bit_permutation": mapping, "allowed_input": action,
                                      "illegal_image": sorted(mapping[bit] for bit in action)}
        assert tally["menu_changing"]
        escaped = min(((word, remap_word(word, preferred)) for word in rows
                       if remap_word(word, preferred) not in rows), default=None)
        result = {
            "fixture": fixture_record(records, i, target_set),
            "stars": list(checks.values()),
            "allowed_states": len(rows),
            "literal_reference_bonds": bond_count,
            "allowed_input_counts_by_arity": dict(Counter(map(len, menu))),
            "automorphism_counts": dict(tally),
            "menu_changing_automorphisms_by_input_arity": dict(affected),
            "example_per_affected_input_arity": examples,
            "preferred_map_state_and_image_if_changed": escaped,
        }
        if state_example is not None:
            moves_prefix, _, mapping = state_example
            assert {remap_word(word, mapping) for word in rows} == rows
            image_menu = transported(menu, mapping)
            assert image_menu != menu and transported(record.stars, mapping) != record.stars
            result["same_states_different_menu"] = {
                "bit_permutation": mapping,
                "allowed_inputs": sorted(tuple(sorted(action)) for action in menu),
                "image_inputs": sorted(tuple(sorted(action)) for action in image_menu),
                "all_earlier_stars_fixed_individually": not moves_prefix,
            }
            if not moves_prefix:
                earlier_bits = {bit for star in prefix.values() for bit in star}
                alternate = frozenset(mapping[bit] for bit in last)
                original_input, alternate_input = last & earlier_bits, alternate & earlier_bits
                earlier_menu = independent_menu(prefix)
                assert original_input in earlier_menu and alternate_input in earlier_menu
                assert len(last - earlier_bits) == len(alternate - earlier_bits) in (2, 3)
                result["same_states_different_menu"].update(
                    last_legal_original_inputs=sorted(original_input),
                    last_legal_alternate_inputs=sorted(alternate_input),
                    original_last_star=sorted(last), alternate_last_star=sorted(alternate),
                )
        results.append(result)
    return results


def verify_quotient():
    matrix = ((0, 2, 4, 4), (2, 0, 4, 4), (4, 4, 0, 2), (4, 4, 2, 0))
    quotient = Quotient.make(matrix)
    order, quotient_order, generators = quotient.automorphisms()
    exact = [p for p in permutations(range(4)) if disagreement(matrix, matrix, p) is None]
    assert order == len(exact) == 8 and quotient_order == 2
    menu = frozenset((frozenset((0, 2)),))
    assert any(transported(menu, g) != menu for g in generators)
    all_pairs = frozenset(map(frozenset, combinations(range(4), 2)))
    assert all(transported(all_pairs, g) == all_pairs for g in exact)
    names = (2, 0, 3, 1)
    renamed = tuple(tuple(matrix[i][j] for j in names) for i in names)
    other = Quotient.make(renamed)
    mapping = quotient.lift(other, next(isometries(quotient.colored, other.colored)))
    assert disagreement(matrix, renamed, mapping) is None


def main():
    import check_width

    verify_quotient()
    fixtures = check_width.width_fixtures()
    records = tuple(check_width.width_records())
    assert all(record.fixture == fixture for record, fixture in zip(records, fixtures, strict=True))
    assert all(all(1 <= len(action) <= 3 and action <= set(range(WIDTH)) for action in record.menu)
               for record in records)
    depth = tuple(len(record.fixture.loose_counts) for record in records)
    target_set = target_indices(records, check_width.target_fixture())
    assert target_set and set(depth) == {6, 7, 8}
    full = tuple(dense(record.table, None) for record in records)
    clipped = tuple(dense(record.table, 5) for record in records)
    exact_census = build_classes(records, full)
    clipped_census = build_classes(records, clipped)
    exact, (exact_duplicates, exact_conflicts) = summarize(records, target_set, full, full, exact_census, depth)
    capped, (cap_duplicates, cap_conflicts) = summarize(records, target_set, full, clipped, clipped_census, depth)
    additional = threshold_only(records, target_set, full, clipped, depth, exact_census, clipped_census)
    failures = self_conflict_witnesses(records, target_set, full, exact_census)
    same_groups = all(exact_census[1][i][0].group_order == clipped_census[1][i][0].group_order
                      for i in range(len(records)))
    result = {
        "width": WIDTH,
        "producer_fixtures": len(records),
        "fresh_output_counts_for_each_allowed_input": check_width.FRESH_COUNTS,
        "target_roster_indices": sorted(target_set),
        "full_distances": exact,
        "distances_through_five": capped,
        "automorphism_groups_unchanged_by_clipping": same_groups,
        "full_table_self_conflicts": failures,
        "fixtures_with_true_three_input_menu_change": sum(
            3 in failure["menu_changing_automorphisms_by_input_arity"] for failure in failures
        ),
        "new_after_clipping": {
            "duplicate_pairs_by_junction_counts": manifest_counts(cap_duplicates - exact_duplicates),
            "menu_conflict_pairs_by_junction_counts": manifest_counts(cap_conflicts - exact_conflicts),
            **additional,
        },
        "four_vertex_brute_force_quotient_control": True,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
