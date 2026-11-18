"""Check every actual ternary input family against exact width-19 isometries."""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
import json
import sys


WIDTH = 19
NAMES = tuple(range(WIDTH))
PAIRS = tuple(combinations(NAMES, 2))
INFINITY = WIDTH
PREDECESSOR = (
    "proofs/VARIABLE-OUTPUT-READER-20261118-001A/"
    "VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen/check_classes.py"
)
PREDECESSOR_SHA256 = "8dd0ddaa58aa6e6f8ba1ec20fbe87b0b1c31cb090e93849fb271c8243dcb2472"


def load_predecessor():
    path = Path(__file__).resolve().parents[3] / PREDECESSOR
    assert sha256(path.read_bytes()).hexdigest() == PREDECESSOR_SHA256
    spec = spec_from_file_location("width_eighteen_class_algorithms", path)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def packed_table(table):
    assert table.keys() == set(PAIRS)
    assert all(value is None or 2 <= value < WIDTH for value in table.values())
    return bytes(INFINITY if table[pair] is None else table[pair] for pair in PAIRS)


def dense(packed):
    matrix = [[0] * WIDTH for _ in NAMES]
    for (a, b), value in zip(PAIRS, packed, strict=True):
        matrix[a][b] = matrix[b][a] = value
    return tuple(map(tuple, matrix))


def triple_family(menu):
    triples = frozenset(action for action in menu if len(action) == 3)
    assert all(action <= set(NAMES) for action in triples)
    return triples


def grade(api, family, generators):
    bad = mover = None
    for mapping in generators:
        image = api.transported(family, mapping)
        if image != family:
            if bad is None:
                bad = mapping
        elif mover is None:
            for action in sorted(tuple(sorted(bits)) for bits in family):
                target = tuple(sorted(mapping[bit] for bit in action))
                if action != target:
                    mover = mapping, action, target
                    break
    return bad, mover


@dataclass(frozen=True)
class Member:
    index: int
    depth: int
    to_rep: tuple
    triples: frozenset
    bad: tuple | None


@dataclass
class Observation:
    packed: bytes
    automorphisms: int
    quotient_order: int
    members: list = field(default_factory=list)


def fixture_info(fixture, index):
    return {"roster_index": index, "junction_count": len(fixture.loose_counts),
            "history": fixture.history, "loose_counts": fixture.loose_counts,
            "checks_in_birth_order": list(fixture.checks().values())}


def forbidden_loose_triple(fixture, legal):
    owners = defaultdict(list)
    for parent, support in fixture.checks().items():
        for bit in support:
            owners[bit].append(parent)
    loose = sorted(bit for bit, parents in owners.items() if len(parents) == 1)
    return next((bits for bits in combinations(loose, 3)
                 if len({owners[bit][0] for bit in bits}) == 3 and frozenset(bits) not in legal), None)


def plant_control(api, fixture, index, family, mover, matrix):
    bad_input = forbidden_loose_triple(fixture, family)
    if bad_input is None:
        return None
    mapping, source, image = mover
    assert api.disagreement(matrix, matrix, mapping) is None
    assert triple_family(api.independent_menu(fixture.checks())) == family
    planted = (family - {frozenset(image)}) | {frozenset(bad_input)}
    assert len(planted) == len(family) and frozenset(source) in planted
    assert grade(api, planted, (mapping,))[0] == mapping
    assert frozenset(mapping[bit] for bit in source) not in planted
    return {"fixture": fixture_info(fixture, index), "bit_permutation": mapping,
            "number_of_triples_before_and_after": len(family),
            "source_legal_in_both": source, "legal_image_removed": image,
            "added_forbidden_triple_on_three_distinct_loose_parents": bad_input}


def relabel_control(api, matrix, family):
    order = tuple((7 * i + 3) % WIDTH for i in NAMES)
    renamed = tuple(tuple(matrix[a][b] for b in order) for a in order)
    old, new = api.Quotient.make(matrix), api.Quotient.make(renamed)
    mapping = old.lift(new, next(api.isometries(old.colored, new.colored)))
    assert api.disagreement(matrix, renamed, mapping) is None
    assert api.transported(family, mapping) == api.transported(family, api.inverse(order))
    return {"supplied_new_to_old_names": order, "recovered_old_to_new_isometry": mapping}


def census(api, fixtures, measured):
    classes = []
    buckets = defaultdict(list)
    depths = defaultdict(Counter)
    positives = {}
    planted = None
    tests = Counter()
    for index, (fixture, record) in enumerate(zip(fixtures, measured, strict=True)):
        assert fixture == record.fixture
        depth = len(fixture.loose_counts)
        report = depths[depth]
        report["fixtures"] += 1
        family = triple_family(record.menu)
        report["fixtures_with_legal_triples"] += bool(family)
        report["legal_triples_on_actual_identities"] += len(family)
        packed = packed_table(record.table)
        matrix = dense(packed)
        quotient = api.Quotient.make(matrix)
        group_order, quotient_order, generators = quotient.automorphisms()
        assert all(api.disagreement(matrix, matrix, p) is None for p in generators)
        bad, mover = grade(api, family, generators)
        report["isometries_within_fixtures"] += group_order
        report["triple_menu_conflicting_fixtures"] += bad is not None
        report["stable_fixtures_with_a_triple_moving_isometry"] += mover is not None and bad is None
        tests["generators_graded"] += len(generators)
        tests["largest_quotient_group"] = max(tests["largest_quotient_group"], quotient_order)

        if bad is None and mover is not None:
            if depth not in positives:
                mapping, source, target = mover
                assert triple_family(api.independent_menu(fixture.checks())) == family
                positives[depth] = {"fixture": fixture_info(fixture, index), "bit_permutation": mapping,
                                    "legal_source": source, "different_legal_image": target,
                                    "legal_triples": len(family), "automorphisms": group_order,
                                    "separate_relabeling": relabel_control(api, matrix, family)}
            if planted is None:
                planted = plant_control(api, fixture, index, family, mover, matrix)

        # An invariant digest only picks candidates. A digest collision can
        # cause extra exact comparisons and cannot merge different tables.
        key = sha256(repr(quotient.colored.invariant).encode()).digest()
        bucket = buckets[key]
        for observation in bucket:
            tests["exact_cross_fixture_quotient_comparisons"] += 1
            reference = dense(observation.packed)
            target = api.Quotient.make(reference)
            quotient_map = next(api.isometries(quotient.colored, target.colored), None)
            if quotient_map is not None:
                mapping = quotient.lift(target, quotient_map)
                assert api.disagreement(matrix, reference, mapping) is None
                assert (group_order, quotient_order) == (observation.automorphisms, observation.quotient_order)
                break
        else:
            observation = Observation(packed, group_order, quotient_order)
            bucket.append(observation)
            classes.append(observation)
            mapping = NAMES
        observation.members.append(Member(index, depth, mapping, api.transported(family, mapping), bad))

    assert set(depths) == {7, 8, 9} and positives and planted is not None
    tests.setdefault("exact_cross_fixture_quotient_comparisons", 0)
    return classes, depths, tests, positives, planted


def different(left, right):
    return left.bad is not None or right.bad is not None or left.triples != right.triples


def observed_summary(api, classes, depths):
    coincidences, discrepancies = Counter(), Counter()
    self_examples = []
    cross_examples = []
    class_conflicts = duplicate_classes = between_maps = 0
    for observation in classes:
        members = observation.members
        by_depth = Counter(member.depth for member in members)
        stable = defaultdict(Counter)
        unstable = []
        for member in members:
            if member.bad is None:
                stable[member.triples][member.depth] += 1
            else:
                unstable.append(member)
        for d in by_depth:
            depths[d]["distinct_tables_represented"] += 1
        if unstable:
            self_examples.append((observation, unstable[0]))

        duplicate = api.pairs_by_depth(by_depth)
        agreeing = Counter()
        for family_depths in stable.values():
            agreeing.update(api.pairs_by_depth(family_depths))
        conflicts = duplicate - agreeing
        if len(members) > 1:
            duplicate_classes += 1
            coincidences.update(duplicate)
            between_maps += observation.automorphisms * sum(duplicate.values())
        if conflicts:
            discrepancies.update(conflicts)
            # Any incompatible partition or unstable member gives the
            # earliest member at least one incompatible partner.
            left = members[0]
            right = next(other for other in members[1:] if different(left, other))
            cross_examples.append((observation, left, right))
        implicated = {member.depth for member in unstable} | {d for pair in conflicts for d in pair}
        class_conflicts += bool(implicated)
        for d in implicated:
            depths[d]["full_table_classes_with_triple_discrepancy"] += 1
    for profile in depths.values():
        profile.setdefault("full_table_classes_with_triple_discrepancy", 0)
    return ({"full_table_classes": len(classes), "classes_with_distinct_fixture_coincidences": duplicate_classes,
             "classes_with_triple_discrepancy": class_conflicts,
             "distinct_fixture_coincidences_by_depth_pair": api.manifest_counts(coincidences),
             "distinct_fixture_discrepancies_by_depth_pair": api.manifest_counts(discrepancies),
             "isometries_between_distinct_fixtures_counted_one_direction": between_maps,
             "by_junction_count": dict(depths)}, self_examples, cross_examples)


def witness_mapping(api, left, right):
    to_left = api.inverse(left.to_rep)
    to_right = api.inverse(right.to_rep)
    if left.triples != right.triples:
        return tuple(to_right[i] for i in left.to_rep)
    if left.bad is not None:
        return tuple(to_right[left.to_rep[i]] for i in left.bad)
    reverse = tuple(to_left[right.to_rep[i]] for i in right.bad)
    return api.inverse(reverse)


def literal_table(fixture):
    """Derive a warning case from explicit states, independently of the scout."""
    equations = tuple(sum(1 << bit for bit in support) for support in fixture.checks().values())
    rows = tuple(word for word in range(1 << WIDTH)
                 if all((word & equation).bit_count() % 2 == 0 for equation in equations))
    basis = {}
    for row in rows:
        word = row
        while word:
            pivot = word.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = word
                break
            word ^= basis[pivot]
    assert len(rows) == 1 << len(basis)
    checks = [word for word in range(1, 1 << WIDTH)
              if all((word & row).bit_count() % 2 == 0 for row in basis.values())]
    minimal = []
    table = dict.fromkeys(PAIRS, None)
    for word in sorted(checks, key=lambda mask: (mask.bit_count(), mask)):
        if any(word & mask == mask for mask in minimal):
            continue
        minimal.append(word)
        support = tuple(i for i in NAMES if word & (1 << i))
        assert len(support) >= 3
        assert len({row & word for row in rows}) < 1 << len(support)
        assert all(len({row & (word ^ (1 << i)) for row in rows}) == 1 << (len(support) - 1) for i in support)
        for pair in combinations(support, 2):
            if table[pair] is None:
                table[pair] = len(support) - 1
    return len(rows), len(minimal), dense(packed_table(table))


def explain_conflict(api, fixtures, observation, left, right):
    mapping = witness_mapping(api, left, right)
    family_left = api.transported(left.triples, api.inverse(left.to_rep))
    family_right = api.transported(right.triples, api.inverse(right.to_rep))
    illegal = family_left - api.transported(family_right, api.inverse(mapping))
    if not illegal:
        left, right = right, left
        family_left, family_right = family_right, family_left
        mapping = api.inverse(mapping)
        illegal = family_left - api.transported(family_right, api.inverse(mapping))
    assert illegal
    chosen = min(tuple(sorted(action)) for action in illegal)
    image = tuple(sorted(mapping[i] for i in chosen))
    reference = dense(observation.packed)
    witnesses = []
    for member, family in ((left, family_left), (right, family_right)):
        fixture = fixtures[member.index]
        assert family == triple_family(api.independent_menu(fixture.checks()))
        if witnesses and left.index == right.index:
            witnesses.append(witnesses[0])
            continue
        rows, bonds, matrix = literal_table(fixture)
        assert api.disagreement(matrix, reference, member.to_rep) is None
        witnesses.append((rows, bonds, matrix))
    (left_rows, left_bonds, left_table), (right_rows, right_bonds, right_table) = witnesses
    assert api.disagreement(left_table, right_table, mapping) is None

    def decoded(value):
        return None if value == INFINITY else value

    return {"left": fixture_info(fixtures[left.index], left.index),
            "right": fixture_info(fixtures[right.index], right.index),
            "bit_permutation": mapping, "allowed_triple_on_left": chosen, "forbidden_image_on_right": image,
            "legal_triple_counts": [len(family_left), len(family_right)],
            "explicit_state_counts": [left_rows, right_rows], "literal_minimal_bonds": [left_bonds, right_bonds],
            "full_table_comparison": {"pair_order": "lexicographic (a,b), 0 <= a < b < 19",
                                      "pairs_checked": len(PAIRS),
                                      "left_distances": [decoded(left_table[a][b]) for a, b in PAIRS],
                                      "right_distances_after_permutation":
                                          [decoded(right_table[mapping[a]][mapping[b]]) for a, b in PAIRS]}}


def width_eighteen_control(api):
    path = Path(api.__file__).with_name("classes.json")
    known = json.loads(path.read_text())["full_table_self_conflicts"][0]
    checks = {i: tuple(support) for i, support in enumerate(known["stars"])}
    menu = api.independent_menu(checks)
    rows, _, table, _ = api.literal_reference(checks)
    matrix = api.dense(table, None)
    _, _, generators = api.Quotient.make(matrix).automorphisms()
    retained = tuple(known["example_per_affected_input_arity"]["2"]["bit_permutation"])
    assert api.disagreement(matrix, matrix, retained) is None and retained in generators
    affected = {len(action) for action in (menu ^ api.transported(menu, retained))}
    assert affected == {1, 2} and grade(api, triple_family(menu), generators)[0] is None
    return {"roster_index": known["fixture"]["roster_index"], "literal_rows": len(rows),
            "bit_permutation": retained, "affected_input_arities": sorted(affected)}


def main():
    import check_population

    api = load_predecessor()
    api.verify_quotient()
    prior_control = width_eighteen_control(api)
    fixtures = check_population.width_fixtures()
    classes, depths, tests, positives, planted = census(api, fixtures, check_population.width_records())
    result, self_examples, cross_examples = observed_summary(api, classes, depths)
    self_first = min(self_examples, key=lambda pair: (pair[1].depth, pair[1].index), default=None)
    cross_first = min(cross_examples, key=lambda item: (item[1].depth, item[2].depth, item[1].index, item[2].index),
                      default=None)
    result.update(
        width=WIDTH, producer_fixture_count=len(fixtures), checked_scalar_pairs_per_fixture=len(PAIRS),
        checked_full_distances=True, generator_controls=dict(tests), symmetry_visible_positives=positives,
        automorphisms_counted_by_group_orders=sum(profile["isometries_within_fixtures"]
                                                  for profile in depths.values()),
        width_eighteen_singleton_and_pair_control=prior_control,
        equal_count_planted_triple_negative=planted, predecessor=PREDECESSOR, predecessor_sha256=PREDECESSOR_SHA256,
        first_self_conflict=explain_conflict(api, fixtures, self_first[0], self_first[1], self_first[1])
        if self_first else None,
        first_distinct_fixture_conflict=explain_conflict(api, fixtures, *cross_first) if cross_first else None,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
