"""Read terminal probability tables independently of the growth code."""
import argparse
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations, product
import json
from pathlib import Path


def row_disagreements(rows, n):
    """Bin unordered pairs of states by the number of distinctions they differ on."""
    bins = [0] * (n + 1)
    for left, right in combinations(rows, 2):
        bins[(left ^ right).bit_count()] += 1
    return tuple(bins)


@lru_cache(maxsize=None)
def row_permutations(k):
    """Lookup tables for permuting bit positions in a k-bit column."""
    return [
        [sum(((word >> i) & 1) << j for i, j in enumerate(order)) for word in range(1 << k)]
        for order in permutations(range(k))
    ]


def column_words(rows, n):
    complement = (1 << n) - 1
    assert set(rows) == {row ^ complement for row in rows}
    representatives = [row for row in rows if row < row ^ complement]
    return tuple(sum(((row >> j) & 1) << i for i, row in enumerate(representatives)) for j in range(n))


def equivalent_tables(left, right, n, signed):
    """Bijections must preserve complementary row pairs. Try all such bijections."""
    left_words, right_words = column_words(left, n), column_words(right, n)
    k = len(left) // 2
    full = (1 << k) - 1
    normalize = [min(word, full ^ word) if signed else word for word in range(full + 1)]
    target = sorted(normalize[word] for word in right_words)
    for mapping in row_permutations(k):
        permuted = [mapping[word] for word in left_words]
        # Choosing the other row of a pair flips that bit in *all* words.
        # The first word must match some target. Under signed observation the
        # two possible masks differ by a global complement, which normalizes away.
        for first in target:
            mask = first ^ permuted[0]
            if sorted(normalize[word ^ mask] for word in permuted) == target:
                return True
    return False


def verify_equivalence_control():
    source = (0, 1, 2, 5, 6, 7)
    switched = tuple(4 ^ row for row in source)
    assert equivalent_tables(source, switched, 3, True)
    assert not equivalent_tables(source, switched, 3, False)
    assert row_disagreements(source, 3) == row_disagreements(switched, 3)


def score_layer(records, n, signed):
    """Each input triple consists of (allowed rows, fan mass, other mass)."""
    mass = [Fraction(0), Fraction(0)]
    bins = defaultdict(lambda: [Fraction(0), Fraction(0)])
    representatives = defaultdict(list)
    success_mass = Fraction(0)
    checked_pairs = 0
    for rows, fan, other in records:
        assert len(set(rows)) == len(rows) and all(0 <= row < 1 << n for row in rows)
        assert fan >= 0 and other >= 0 and fan + other > 0
        mass[0] += fan
        mass[1] += other
        success_mass += max(fan, other)
        feature = row_disagreements(rows, n)
        bins[feature][0] += fan
        bins[feature][1] += other

        # These summaries only narrow the search. The definitive comparison
        # reads the whole table and omits the age of every distinction.
        row_profiles = tuple(sorted(tuple(sorted((row ^ other_row).bit_count()
                                                  for other_row in rows)) for row in rows))
        column_masks = [sum(((row >> j) & 1) << i for i, row in enumerate(rows)) for j in range(n)]
        column_profiles = []
        for left_mask in column_masks:
            counts = [(left_mask ^ right_mask).bit_count() for right_mask in column_masks]
            if signed:
                counts = [min(count, len(rows) - count) for count in counts]
            column_profiles.append(tuple(sorted(counts)))
        weight_key = () if signed else tuple(sorted(row.bit_count() for row in rows))
        bucket = representatives[row_profiles, tuple(sorted(column_profiles)), weight_key]
        bucket.append(rows)
    assert mass == [1, 1]
    for bucket in representatives.values():
        if len(bucket) < 2:
            continue
        for a, b in combinations(bucket, 2):
            checked_pairs += 1
            assert not equivalent_tables(a, b, n, signed), "the class list contains two equivalent relations"
    full_score = success_mass / 2
    feature_score = sum(max(values) for values in bins.values()) / 2
    assert Fraction(1, 2) <= feature_score <= full_score <= 1
    return {
        "state_classes": sum(map(len, representatives.values())),
        "full_accuracy": str(full_score),
        "histogram_classes": len(bins),
        "histogram_accuracy": str(feature_score),
        "isomorphism_checks_within_profile_buckets": checked_pairs,
    }


def check_layer(layer, signed):
    assert layer["stalled_probability"] == ["0", "0"]
    records = [
        (record["rows"], Fraction(record["fan6_probability"]), Fraction(record["nonfan6_probability"]))
        for record in layer["class_records"]
    ]
    result = score_layer(records, layer["width"], signed)
    assert result["state_classes"] == layer["union_classes"]
    assert result["full_accuracy"] == layer["recognition"]
    assert result["histogram_accuracy"] == layer["hamming_histogram_recognition"]
    assert 2 * Fraction(result["full_accuracy"]) - 1 == Fraction(layer["total_variation"])
    result["row_counts"] = sorted({len(rows) for rows, _, _ in records})
    return result


def signed_fill_histograms(rows, n):
    """Try every column on the six complementary row pairs; certify each by a cover."""
    full = (1 << len(rows)) - 1
    positions = {row: i for i, row in enumerate(rows)}
    pairs = [(i, positions[row ^ ((1 << n) - 1)]) for i, row in enumerate(rows)
             if row < (row ^ ((1 << n) - 1))]
    assert len(pairs) == 6 and len(rows) == 12
    columns = {sum(((row >> j) & 1) << i for i, row in enumerate(rows)) for j in range(n)}
    excluded = columns | {full ^ column for column in columns}
    atoms = []
    for a, b in combinations(range(n), 2):
        for x, y in product((0, 1), repeat=2):
            # Forbid (x,y,0) and (1-x,1-y,1).
            force_one = sum(1 << i for i, r in enumerate(rows) if ((r >> a) & 1, (r >> b) & 1) == (x, y))
            force_zero = sum(1 << i for i, r in enumerate(rows) if ((r >> a) & 1, (r >> b) & 1) == (1-x, 1-y))
            atoms.append((force_one, force_zero))

    outcomes = []
    for choices in product((0, 1), repeat=len(pairs)):
        column = sum(1 << pair[choice] for pair, choice in zip(pairs, choices))
        if column in excluded:
            continue
        covers = {one | zero for one, zero in atoms if not (one & ~column or zero & column)}
        upto_two = {a | b for a in covers for b in covers}
        if any((ab | c) == full for ab in upto_two for c in covers):
            target = [row | (((column >> i) & 1) << n) for i, row in enumerate(rows)]
            outcomes.append(row_disagreements(target, n + 1))
    # A fill keeps all 12 original rows. Its existence certifies minimum size.
    assert outcomes and len(outcomes) % 2 == 0
    return outcomes


def check_signed_transitions(layers):
    """Recompute the simpler reader's two endpoint laws from all possible columns."""
    counts = {}
    for old, new in zip(layers, layers[1:]):
        n = old["width"]
        derived = defaultdict(lambda: [Fraction(), Fraction()])
        observed = defaultdict(lambda: [Fraction(), Fraction()])
        extensions = 0
        for record in old["class_records"]:
            options = signed_fill_histograms(record["rows"], n)
            extensions += len(options)
            for name, side in (("fan6_probability", 0), ("nonfan6_probability", 1)):
                step_mass = Fraction(record[name]) / len(options)
                for histogram in options:
                    derived[histogram][side] += step_mass
        for record in new["class_records"]:
            key = row_disagreements(record["rows"], n + 1)
            observed[key][0] += Fraction(record["fan6_probability"])
            observed[key][1] += Fraction(record["nonfan6_probability"])
        assert derived == observed, "independent column test disagrees with saved histogram laws"
        counts[n] = {"input_classes": len(old["class_records"]), "distinct_literal_fills": extensions}
    return counts


def verify(raw):
    verify_equivalence_control()
    cut_scores = {}
    for name, layer in raw["cut_baselines"].items():
        cut_scores[name] = check_layer(layer, name.endswith("_independent"))["full_accuracy"]
    assert cut_scores == {
        "7_common": "7/8", "7_independent": "1/2",
        "8_common": "249/280", "8_independent": "26/35",
    }
    assert all(Fraction(row["fan6_probability"]) == Fraction(row["nonfan6_probability"])
               for row in raw["cut_baselines"]["7_independent"]["class_records"])
    assert raw["seven_independent"]["derived_recognition"] == dict.fromkeys(("8", "9", "10"), "1/2")
    checked = {}
    for arm in ("seven_common", "eight_independent"):
        layers = raw[arm]["layers"]
        signed = arm == "eight_independent"
        assert [layer["width"] for layer in layers] == list(range(8 if signed else 7, 11))
        scores = {layer["width"]: check_layer(layer, signed) for layer in layers}
        accuracies = [Fraction(score["full_accuracy"]) for score in scores.values()]
        assert accuracies == sorted(accuracies, reverse=True)
        checked[arm] = scores
    return {"cut_recognition": cut_scores, "checked_layers": checked,
            "signed_transitions_by_column_covers": check_signed_transitions(raw["eight_independent"]["layers"])}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(json.loads(args.results.read_text())), indent=2))
