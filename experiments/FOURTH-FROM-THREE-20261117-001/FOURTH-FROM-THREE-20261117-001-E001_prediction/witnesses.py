"""Replay two same-cut counterexamples using the original literal move generator."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
from itertools import combinations
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ERASURE = "ERASE-SEPARATELY-20261117-001"
RULE = ROOT / "experiments" / ERASURE / (ERASURE + "-E001_erasure") / "enumerate_erasure.py"


def direct_rule():
    assert hashlib.sha256(RULE.read_bytes()).hexdigest() == "c800b09d648406ab25f6b585ffb48d7056c78b5c3d76d1563129d73d4d2202ea"
    spec = importlib.util.spec_from_file_location("original_erasure_rule", RULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def project(rows, indices):
    return frozenset(sum(((row >> col) & 1) << j for j, col in enumerate(indices))
                     for row in rows)


def add_named_column(rule, rows, width, word, local=None):
    # The letters specify the proposed witness. Search the blind rule's move
    # list to establish its reachability; the rule never receives the word.
    mask = sum(1 << (ord(letter) - ord("a")) for letter in word)
    expected = tuple(sorted(row | (((row & mask).bit_count() % 2) << width) for row in rows))
    extensions = rule.cheapest(rows, width, signed=local is None, local=local)
    paths = [added for target, added in extensions if target == expected]
    if not paths:
        raise AssertionError(f"unavailable witness {word} at width {width}")
    return expected, paths[0], Fraction(len(paths), len(extensions))


def statistics(rows, rule):
    triple = project(rows, (8, 9, 10))
    assert len(triple) in (6, 8)
    counts = Counter()
    for child, _ in rule.cheapest(rows, 11, signed=True):
        assert len(child) == 12 and {r & ((1 << 11) - 1) for r in child} == set(rows)
        four = project(child, (8, 9, 10, 11))
        assert {r & 7 for r in four} == triple
        k = sum(len(project(child, (i, j, 11))) == 6 for i, j in combinations((8, 9, 10), 2))
        counts["literal_choices"] += 1
        counts["determined"] += len(four) == len(triple)
        counts["four_parity"] += len(four) == 8 and len({r.bit_count() % 2 for r in four}) == 1
        counts["fourth_knots_with_a_pair"] += k > 0
    assert counts["literal_choices"] > 0
    return {"triple_rows": sorted(triple), **counts}


def verify_examples():
    rule = direct_rule()
    original_knots = rule.STARTS["fan6"]
    start = rule.seed_rows(6, original_knots)
    seven, added, first_p = add_named_column(rule, start, 6, "abc", original_knots)
    cut, _, second_p = add_named_column(rule, seven, 7, "acd", original_knots + added)
    paths = [("abe", "abf", "cef"), ("abe", "abf", "abd"),
             ("abf", "aef", "bce"), ("abf", "aef", "bcf")]
    results = []
    for words in paths:
        rows = cut
        probability = Fraction(1)
        for width, word in enumerate(words, 8):
            rows, _, choice_p = add_named_column(rule, rows, width, word)
            probability *= choice_p
        results.append({"added": words, "one_path_conditional_probability": str(probability),
                        **statistics(rows, rule)})
    knot_a, knot_b, free_a, free_b = results
    assert len(knot_a["triple_rows"]) == len(knot_b["triple_rows"]) == 6
    assert len(free_a["triple_rows"]) == len(free_b["triple_rows"]) == 8
    assert knot_a["determined"] == 0 < knot_b["determined"]
    assert free_a["four_parity"] == 0 < free_b["four_parity"]
    return {"two_fixed_pre_cut_moves": ["abc", "acd"], "positive_cut_path": str(first_p * second_p),
            "reached_from_fan6": results}


def verify_cross_cut(raw):
    rule = direct_rule()
    cut_rows = {r["cut_class"]: r["cut_rows"] for r in raw["cut_classes"]}
    labels = {"determined_by_three": "determined", "four_place_parity": "four_parity"}
    checked = {}
    for triple_type, group in raw["by_triple_support_size"].items():
        witness = group["witness"]
        contexts = witness["contexts"]
        assert contexts[0]["cut_class"] != contexts[1]["cut_class"]
        assert contexts[0]["fresh_words"] == contexts[1]["fresh_words"]
        reports = []
        for context, expected in zip(contexts, witness["conditional_probabilities"]):
            cut = tuple(cut_rows[context["cut_class"]])
            indices = {r: i for i, r in enumerate(cut[:6])}
            rows = cut
            path = context["reachable_path"]
            probability = Fraction(1)
            for step, word in enumerate(path["successive_new_words"], 8):
                mask = int(word, 2)
                def value(row):
                    old = row & 255
                    if old in indices:
                        return (mask >> indices[old]) & 1
                    return 1 ^ ((mask >> indices[old ^ 255]) & 1)
                wanted = tuple(sorted(r | (value(r) << step) for r in rows))
                options = rule.cheapest(rows, step, signed=True)
                assert len(options) == path["literal_branch_counts"][step - 8]
                assert sum(child == wanted for child, _ in options) == 1
                probability /= len(options)
                rows = wanted
            assert probability == Fraction(path["literal_path_probability_given_cut_class"])
            counts = statistics(rows, rule)
            assert len(counts["triple_rows"]) == int(triple_type)
            assert counts["literal_choices"] == context["literal_option_count"]
            event = labels[witness["event"]]
            actual = Fraction(counts[event], counts["literal_choices"])
            assert actual == Fraction(expected)
            reports.append({"cut_class": context["cut_class"], "event": event, "event_probability": str(actual),
                            "literal_choices": counts["literal_choices"], "event_choices": counts[event]})
        checked[triple_type] = reports
    return checked


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path)
    args = parser.parse_args()
    report = verify_examples()
    if args.results:
        report["matched_triples_on_distinct_cuts"] = verify_cross_cut(json.loads(args.results.read_text()))
    print(json.dumps(report, indent=2))
