"""Compare conditional queries with explicit enumeration on finite controls."""

import json
from itertools import combinations, product
from pathlib import Path
from resource import RUSAGE_SELF, getrusage
import sys
from time import perf_counter

from omitted_semantics import StageChecks, _qualifying_upper_image


RESEARCH = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RESEARCH / "NAE-LAYER-20261127-001/referee-R1"))
from growth_rule import advance, supports_of


LOWER = tuple((a, 2 + b, 4 + c) for a, b, c in product(range(2), repeat=3) if (a + b + c) % 2 == 0)


def mask(labels):
    return sum(2 ** label for label in labels)


def pattern_of(carriers):
    flat = [(mask(carrier), 1) for carrier in carriers]
    return tuple(tuple(flat[offset:offset + 2]) for offset in range(0, 6, 2))


def at(word, positions):
    return tuple(word[index] for index in positions)


def upper(word, both_pair):
    values = [sum(word[offset:offset + 2]) for offset in (0, 2, 4)]
    return tuple(int(value >= (2 if index == both_pair else 1))
                 for index, value in enumerate(values))


def encode(word):
    return int("".join(map(str, word)), 2)


def lower_images(six_words):
    return [sorted({encode(at(word, positions)) for word in six_words}) for positions in LOWER]


def upper_control(six_words, both_pair):
    pairs_free = all(len({at(upper(word, both_pair), pair) for word in six_words}) == 4
                     for pair in combinations(range(3), 2))
    determined_at = []
    for positions in LOWER:
        cells = {}
        for word in six_words:
            cells.setdefault(at(word, positions), set()).add(upper(word, both_pair))
        determined_at.append([index for index in range(3)
                              if all(len({value[index] for value in cell}) == 1 for cell in cells.values())])
    return pairs_free, determined_at


def brute_force(supports, n_start, pattern):
    names = sorted({name for support in supports for name in support})
    compact = {name: index for index, name in enumerate(names)}
    laws = [mask(compact[name] for name in support) for support in supports]
    readings = [(mask(compact[name] for name in names if carrier & (2 ** name)), value)
                for pair in pattern for carrier, value in pair]

    allowed = []
    upper_counts = [[0] * 8 for _ in range(3)]
    deletion_counts = [[0] * len(supports) for _ in range(3)]
    for assignment in range(2 ** len(names)):
        broken = [index for index, law in enumerate(laws) if assignment & law in (0, law)]
        if len(broken) > 1:
            continue
        word = tuple(int((assignment & carrier in (0, carrier)) == value) for carrier, value in readings)
        if not broken:
            allowed.append((assignment, word))
        for both_pair in range(3):
            code = encode(upper(word, both_pair))
            if not broken:
                upper_counts[both_pair][code] += 1
            elif code == 7:
                deletion_counts[both_pair][broken[0]] += 1

    source_knots_determining = [[] for _ in readings]
    for index, law in enumerate(laws):
        cells = {}
        for assignment, word in allowed:
            cells.setdefault(assignment & law, set()).add(word)
        for reading_index in range(len(readings)):
            if all(len({word[reading_index] for word in cell}) == 1 for cell in cells.values()):
                source_knots_determining[reading_index].append(index)

    six_words = {word for _, word in allowed}
    images = lower_images(six_words)
    valid_lower = [image == list(range(7)) and all(not source_knots_determining[i] for i in positions)
                   for positions, image in zip(LOWER, images, strict=True)]
    result = []
    for both_pair in range(3):
        counts = upper_counts[both_pair]
        free, determined = upper_control(six_words, both_pair)
        if all(valid_lower) and counts[7] == 0 and free and not any(determined):
            deletions = deletion_counts[both_pair]
            result.append({
                "both_pair": both_pair,
                "upper_words": [code for code, count in enumerate(counts) if count],
                "initial_law_deletions": [index for index in range(n_start) if deletions[index]],
                "birth_law_deletions": [index for index in range(n_start, len(laws)) if deletions[index]],
            })
    return {
        "allowed_states": len(allowed),
        "six_reading_words": sorted(map(encode, six_words)),
        "lower_images": images,
        "source_knots_determining": source_knots_determining,
        "upper_word_counts": upper_counts,
        "restorations_by_deleted_law": deletion_counts,
        "valid_lower": valid_lower,
        "qualifying_readings": result,
    }


def check_fixture(supports, n_start, pattern):
    brute = brute_force(supports, n_start, pattern)
    flat = [reading for pair in pattern for reading in pair]
    with StageChecks(supports, n_start) as checker:
        lower = [checker.is_lower_bond(at(flat, positions)) for positions in LOWER]
        assert lower == brute["valid_lower"], (lower, brute["valid_lower"])
        exact = checker.check(pattern, stop_first=False)
        assert exact == brute["qualifying_readings"], (exact, brute["qualifying_readings"])
        assert checker.check(pattern) == exact[:1]
    return brute


def abstract_controls():
    base = [word for word in product(range(2), repeat=6)
            if all(at(word, positions) != (1, 1, 1) for positions in LOWER)]
    records = {}
    cases = [
        ("six_free_words", [word for word in base if upper(word, 0) != (0, 0, 0)],
         True, False, [1, 2, 3, 4, 5, 6]),
        ("a_constrained_upper_pair", [word for word in base if upper(word, 0) != (1, 0, 1)],
         False, False, None),
        ("determined_at_one_lower_bond", [word for word in base if word[0] <= word[1]],
         True, True, None),
    ]
    for name, six_words, expected_free, expected_determined, expected_image in cases:
        assert lower_images(six_words) == [list(range(7))] * 4
        free, determined = upper_control(six_words, 0)
        assert free == expected_free
        assert any(determined) == expected_determined
        image = _qualifying_upper_image(six_words, 0)
        assert image == expected_image
        records[name] = {
            "upper_image": sorted({encode(upper(word, 0)) for word in six_words}),
            "free_in_pairs": free,
            "upper_readings_determined_at_each_lower_bond": determined,
            "qualifies": image is not None,
        }
    return records


def main():
    beginning = perf_counter()
    closed_path = RESEARCH / "UPPER-GROWN-20261127-001/referee-R1/upper_four_closed.json"
    closed_fixture = next(row["witness"] for row in json.loads(closed_path.read_text()) if "witness" in row)
    closed_supports = closed_fixture["knots"]
    closed_pattern = pattern_of(closed_fixture["carriers"])
    closed = check_fixture(closed_supports, len(closed_supports), closed_pattern)
    assert len(closed["qualifying_readings"]) == 3
    assert closed["upper_word_counts"][0] == closed_fixture["upper_word_counts"]
    assert closed["restorations_by_deleted_law"][0] == closed_fixture["restorations_by_dropped_source_law"]

    archive = json.loads((RESEARCH / "FORBID-EDITS-20261126-001/starts.json").read_text())
    start = supports_of(archive[5260])
    first = advance(start)
    second = advance(first.supports)
    assert first.status == second.status == "funded"
    grown_carriers = [(2, 8, 10), (7, 13), (0, 1, 5), (9, 12, 14), (3, 4, 11), (6, 15, 16)]
    grown_pattern = pattern_of(grown_carriers)
    grown = check_fixture(second.supports, len(start), grown_pattern)
    assert len(grown["qualifying_readings"]) == 3
    for row in grown["qualifying_readings"]:
        assert row["initial_law_deletions"] == [1, 2, 3, 4]
        assert row["birth_law_deletions"] == [5, 6, 7, 8]

    opposite_parity = (closed_pattern[0][::-1], *closed_pattern[1:])
    reversed_order = check_fixture(closed_supports, len(closed_supports), opposite_parity)
    assert not all(reversed_order["valid_lower"])
    assert not reversed_order["qualifying_readings"]

    signed_pair = ((closed_pattern[0][0][0], 0), closed_pattern[0][1])
    changed_sign = check_fixture(closed_supports, len(closed_supports), (signed_pair, *closed_pattern[1:]))
    assert changed_sign["valid_lower"] == [False, False, True, True]
    assert all(7 in image for image in changed_sign["lower_images"][:2])
    assert not changed_sign["qualifying_readings"]

    dropped = check_fixture(closed_supports[1:], len(closed_supports) - 1, closed_pattern)
    assert not dropped["qualifying_readings"]
    assert any(7 in image for image in dropped["lower_images"])

    # The two-place laws make 16 equal to 4. The wider law is redundant
    # because it contains the first original law. Its values determine the
    # reading of 4 and 8 even though it does not contain 4.
    alias_supports = [*closed_supports, (4, 15), (15, 16), (*closed_supports[0], 8, 16)]
    alias = check_fixture(alias_supports, len(alias_supports), closed_pattern)
    assert alias["six_reading_words"] == closed["six_reading_words"]
    assert alias["allowed_states"] == closed["allowed_states"]
    assert all(not {4, 8}.issubset(law) for law in alias_supports)
    assert len(alias_supports) - 1 in alias["source_knots_determining"][1]
    assert not alias["qualifying_readings"]

    print(json.dumps({
        "closed_ten_knot_witness": closed,
        "five_knot_census_start_5260_at_round_two": grown,
        "closed_witness_with_one_pair_reversed": reversed_order,
        "closed_witness_with_one_sign_changed": changed_sign,
        "closed_witness_without_first_law": dropped,
        "closed_witness_with_a_reading_determined_via_an_alias": alias,
        "abstract_six_reading_controls": abstract_controls(),
    }, indent=2))
    elapsed = perf_counter() - beginning
    print(f"{elapsed:.3f} s, {getrusage(RUSAGE_SELF).ru_maxrss} KiB max RSS", file=sys.stderr)


if __name__ == "__main__":
    main()
