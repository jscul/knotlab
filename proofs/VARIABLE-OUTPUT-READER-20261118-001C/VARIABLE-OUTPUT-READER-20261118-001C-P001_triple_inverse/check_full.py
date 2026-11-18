"""Compare actual three-input choices under the full width-20 scalar table."""

from collections import Counter, defaultdict
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
import json
import sys


WIDTH = 20
NAMES = tuple(range(WIDTH))
PAIRS = tuple(combinations(NAMES, 2))
PREDECESSOR = (
    "proofs/VARIABLE-OUTPUT-READER-20261118-001B/"
    "VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen/check_classes.py"
)
PREDECESSOR_SHA256 = "481166c5ad27c88717727e2dbb522cab1fa90d7fdf3449e58d5d03b8d53f01f1"


def configured_comparison():
    """Give the existing dimension-independent routines a private width-20 configuration."""
    source = Path(__file__).resolve().parents[3] / PREDECESSOR
    assert sha256(source.read_bytes()).hexdigest() == PREDECESSOR_SHA256
    spec = spec_from_file_location("width_nineteen_algorithms_at_twenty", source)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    assert module.WIDTH == 19
    module.WIDTH, module.NAMES, module.PAIRS, module.INFINITY = WIDTH, NAMES, PAIRS, WIDTH
    return module


def early_conflict(comparison, api, fixtures, observation, left, right):
    """Report the first exact mismatch while the stream is still running."""
    mapping = comparison.witness_mapping(api, left, right)
    first = comparison.triple_family(api.independent_menu(fixtures[left.index].checks()))
    second = comparison.triple_family(api.independent_menu(fixtures[right.index].checks()))
    invalid = first - api.transported(second, api.inverse(mapping))
    if not invalid:
        left, right = right, left
        first, second = second, first
        mapping = api.inverse(mapping)
        invalid = first - api.transported(second, api.inverse(mapping))
    witness = min(tuple(sorted(triple)) for triple in invalid)
    matrix = comparison.dense(observation.packed)
    left_matrix, right_matrix = (tuple(tuple(matrix[m.to_rep[a]][m.to_rep[b]] for b in NAMES) for a in NAMES)
                                 for m in (left, right))
    assert api.disagreement(left_matrix, right_matrix, mapping) is None
    return {"left": comparison.fixture_info(fixtures[left.index], left.index),
            "right": comparison.fixture_info(fixtures[right.index], right.index),
            "bit_permutation": mapping, "legal_triple_on_left": witness,
            "forbidden_image_on_right": sorted(mapping[i] for i in witness),
            "full_scalar_pairs_verified": len(PAIRS)}


def singleton_mismatch(record, generators):
    loose = frozenset(next(iter(action)) for action in record.menu if len(action) == 1)
    ordered = sorted(loose)
    for mapping in generators:
        for bit in ordered:
            if mapping[bit] not in loose:
                return mapping, bit
    return None


def populate(comparison, api, fixtures, records):
    classes = []
    buckets = defaultdict(list)
    profiles = defaultdict(Counter)
    tests = Counter(exact_cross_fixture_quotient_comparisons=0)
    positives = {}
    announced = set()
    histogram_reps = {}
    histogram_counts = Counter()
    planted = singleton = histogram_example = None
    for index, (fixture, record) in enumerate(zip(fixtures, records, strict=True)):
        assert fixture == record.fixture
        depth = len(fixture.loose_counts)
        assert depth == len(fixture.history) + 1 and 3 + sum(fresh for _, fresh in fixture.history) == WIDTH
        profile = profiles[depth]
        family = comparison.triple_family(record.menu)
        packed = comparison.packed_table(record.table)
        matrix = comparison.dense(packed)
        quotient = api.Quotient.make(matrix)
        group_order, quotient_order, generators = quotient.automorphisms()
        assert all(api.disagreement(matrix, matrix, mapping) is None for mapping in generators)
        bad, mover = comparison.grade(api, family, generators)
        single_change = singleton_mismatch(record, generators)
        profile["fixtures"] += 1
        profile["fixtures_with_legal_triples"] += bool(family)
        profile["legal_triples_on_actual_identities"] += len(family)
        profile["generators_graded"] += len(generators)
        profile["isometries_within_fixtures"] += group_order
        profile["triple_menu_conflicting_fixtures"] += bad is not None
        profile["stable_fixtures_with_a_triple_moving_isometry"] += mover is not None and bad is None
        profile["singleton_menu_conflicting_fixtures"] += single_change is not None
        tests["largest_quotient_group"] = max(tests["largest_quotient_group"], quotient_order)

        if single_change is not None and singleton is None:
            mapping, bit = single_change
            literal = api.independent_menu(fixture.checks())
            assert literal == record.menu
            assert frozenset((bit,)) in literal and frozenset((mapping[bit],)) not in literal
            singleton = {"fixture": comparison.fixture_info(fixture, index), "bit_permutation": mapping,
                         "allowed_input": [bit], "forbidden_image": [mapping[bit]],
                         "same_triple_family": api.transported(family, mapping) == family}

        if mover is not None and bad is None:
            if depth not in positives:
                mapping, source, target = mover
                assert comparison.triple_family(api.independent_menu(fixture.checks())) == family
                positives[depth] = {"fixture": comparison.fixture_info(fixture, index), "bit_permutation": mapping,
                                    "legal_source": source, "different_legal_image": target,
                                    "separate_relabeling": comparison.relabel_control(api, matrix, family)}
            if planted is None:
                planted = comparison.plant_control(api, fixture, index, family, mover, matrix)

        # Refinement is an invariant to reject candidates. Any prospective
        # match, including a fingerprint collision, gets an exact comparison.
        key = sha256(repr(quotient.colored.invariant).encode()).digest()
        bucket = buckets[key]
        for observation in bucket:
            tests["exact_cross_fixture_quotient_comparisons"] += 1
            reference = comparison.dense(observation.packed)
            candidate = api.Quotient.make(reference)
            reduced_map = next(api.isometries(quotient.colored, candidate.colored), None)
            if reduced_map is not None:
                mapping = quotient.lift(candidate, reduced_map)
                assert api.disagreement(matrix, reference, mapping) is None
                assert (group_order, quotient_order) == (observation.automorphisms, observation.quotient_order)
                break
        else:
            observation = comparison.Observation(packed, group_order, quotient_order)
            classes.append(observation)
            bucket.append(observation)
            mapping = NAMES
            histogram = tuple(sorted(packed))
            histogram_counts[histogram] += 1
            old_index, old_size = histogram_reps.setdefault(histogram, (index, len(family)))
            counts_differ = old_size != len(family)
            if old_index != index and (histogram_example is None or
                                      (counts_differ and not histogram_example["triple_counts_differ"])):
                histogram_example = {
                    "first": comparison.fixture_info(fixtures[old_index], old_index),
                    "second": comparison.fixture_info(fixture, index),
                    "same_distance_histogram": {"infinity" if value == WIDTH else str(value): count
                                                for value, count in Counter(histogram).items()},
                    "triple_family_sizes": [old_size, len(family)], "triple_counts_differ": counts_differ,
                }

        member = comparison.Member(index, depth, mapping, api.transported(family, mapping), bad)
        if bad is not None and "self" not in announced:
            payload = early_conflict(comparison, api, fixtures, observation, member, member)
            print("WIDTH20_SELF_CONFLICT " + json.dumps(payload, sort_keys=True), file=sys.stderr, flush=True)
            announced.add("self")
        if observation.members and "cross" not in announced and comparison.different(observation.members[0], member):
            payload = early_conflict(comparison, api, fixtures, observation, observation.members[0], member)
            print("WIDTH20_CROSS_CONFLICT " + json.dumps(payload, sort_keys=True), file=sys.stderr, flush=True)
            announced.add("cross")
        observation.members.append(member)

    assert set(profiles) == {7, 8, 9} and positives
    assert planted is not None
    tests["generators_graded"] = sum(profile["generators_graded"] for profile in profiles.values())
    controls = {"symmetry_visible_positives": positives, "equal_count_planted_triple_negative": planted,
                "first_singleton_mismatch": singleton,
                "distinct_full_table_classes_sharing_a_histogram":
                    sum(count for count in histogram_counts.values() if count > 1),
                "histogram_match_between_distinct_full_tables": histogram_example}
    return classes, profiles, dict(tests), controls


def full_witness(comparison, api, fixtures, selection, self_case=False):
    if selection is None:
        return None
    if self_case:
        selection = (*selection, selection[-1])
    evidence = comparison.explain_conflict(api, fixtures, *selection)
    checked = evidence["full_table_comparison"]
    assert checked["pairs_checked"] == len(PAIRS)
    checked["pair_order"] = "lexicographic (a,b), 0 <= a < b < 20"
    return evidence


def main():
    import check_parity

    comparison = configured_comparison()
    api = comparison.load_predecessor()
    api.verify_quotient()
    prior = comparison.width_eighteen_control(api)
    fixtures = check_parity.width_fixtures()
    classes, profiles, tests, controls = populate(comparison, api, fixtures, check_parity.width_records())
    result, self_cases, cross_cases = comparison.observed_summary(api, classes, profiles)
    self_first = min(self_cases, key=lambda entry: (entry[1].depth, entry[1].index), default=None)
    cross_first = min(cross_cases, key=lambda entry: (entry[1].depth, entry[2].depth, entry[1].index, entry[2].index),
                      default=None)
    result.update(width=WIDTH, checked_scalar_pairs_per_fixture=len(PAIRS), checked_full_distances=True,
                  producer_fixture_count=len(fixtures), generator_checks=tests,
                  automorphisms_counted_by_group_orders=sum(row["isometries_within_fixtures"]
                                                            for row in profiles.values()),
                  width_eighteen_singleton_and_pair_control=prior, controls=controls,
                  predecessor=PREDECESSOR, predecessor_sha256=PREDECESSOR_SHA256,
                  first_self_conflict=full_witness(comparison, api, fixtures, self_first, self_case=True),
                  first_distinct_fixture_conflict=full_witness(comparison, api, fixtures, cross_first))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
