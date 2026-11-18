"""Verify the fresh-triple laws by applying the frozen literal-extension rule."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import importlib.util
from itertools import combinations, product
import json
from math import comb
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PRIOR = "ERASE-SEPARATELY-20261117-001"
OLD_FAMILY = PRIOR + "-E001_erasure"
CUT_FILE = ROOT / "artifacts" / PRIOR / OLD_FAMILY / "results.json"
RULE_FILE = ROOT / "experiments" / PRIOR / OLD_FAMILY / "enumerate_erasure.py"
CUT_DIGEST = "65b8a87894afafc8464731432c42242d1b55b803370ddece9c7232c6e79e6d95"
RULE_DIGEST = "c800b09d648406ab25f6b585ffb48d7056c78b5c3d76d1563129d73d4d2202ea"
STARTS = ("fan6", "nonfan6")


def frozen_rule():
    assert hashlib.sha256(RULE_FILE.read_bytes()).hexdigest() == RULE_DIGEST
    spec = importlib.util.spec_from_file_location("frozen_erasure_rule", RULE_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def projected_size(columns, number_rows):
    # This is an existential projection. Only patterns that occur matter.
    return len({tuple((column >> i) & 1 for column in columns) for i in range(number_rows)})


def check_ternary_types():
    proper, free = 0, 0
    for table in range(256):
        rows = {word for word in range(8) if (table >> word) & 1}
        if rows != {word ^ 7 for word in rows}:
            continue
        if any(len({(r >> a & 1, r >> b & 1) for r in rows}) != 4
               for a, b in combinations(range(3), 2)):
            continue
        if len(rows) == 8:
            free += 1
        else:
            missing = set(range(8)) - rows
            assert len(missing) == 2 and missing == {word ^ 7 for word in missing}
            proper += 1
    assert (proper, free) == (4, 1)
    return {"labelled_six_row_types": proper, "labelled_eight_row_types": free}


def unused_column_control(rows):
    positions = {row: i for i, row in enumerate(rows)}
    pairs = [(i, positions[row ^ 255]) for i, row in enumerate(rows) if row < (row ^ 255)]
    assert len(pairs) == 6
    full = (1 << len(rows)) - 1
    all_columns = set()
    for choices in product((0, 1), repeat=6):
        mask = sum(1 << pair[choice] for pair, choice in zip(pairs, choices))
        all_columns.add(min(mask, mask ^ full))
    old_columns = set()
    for bit in range(8):
        mask = sum(((row >> bit) & 1) << i for i, row in enumerate(rows))
        old_columns.add(min(mask, mask ^ full))
    unused = all_columns - old_columns
    assert len(all_columns) == 32 and len(unused) == 24
    counts = Counter(projected_size(triple, len(rows)) for triple in combinations(unused, 3))
    assert set(counts) <= {6, 8} and sum(counts.values()) == comb(24, 3)
    return Fraction(counts[6], comb(24, 3))


def literal_conditional(rows, rule):
    """Ignore the producer's six-row cover algorithm and count actual extensions.

    Each extension that preserves the twelve rows supplies a Boolean column on
    the original rows. The signed rule supplies that column and its complement
    with the same weight. We enumerate them both and then pair them.
    """
    positions = {row: i for i, row in enumerate(rows)}
    full = (1 << len(rows)) - 1

    def choices(added):
        width = 8 + len(added)
        parent = tuple(sorted(
            row | sum(((col >> i) & 1) << (8 + j) for j, col in enumerate(added))
            for i, row in enumerate(rows)
        ))
        literal = set()
        children = rule.cheapest(parent, width, signed=True)
        assert children
        for child, _ in children:
            assert len(child) == len(rows) and {r & 255 for r in child} == positions.keys()
            mask = sum(1 << positions[r & 255] for r in child if r & (1 << width))
            literal.add(mask)
        assert len(literal) == len(children)
        assert literal == {mask ^ full for mask in literal}
        return tuple(mask for mask in literal if mask < (mask ^ full))

    one = choices(())
    pair_mass = defaultdict(Fraction)
    for a in one:
        two = choices((a,))
        for b in two:
            assert projected_size((a, b), len(rows)) == 4
            pair_mass[tuple(sorted((a, b)))] += Fraction(1, len(one) * len(two))
    assert sum(pair_mass.values()) == 1
    six = Fraction()
    for (a, b), mass in pair_mass.items():
        sizes = Counter(projected_size((a, b, c), len(rows)) for c in choices((a, b)))
        assert set(sizes) <= {6, 8}
        six += mass * Fraction(sizes[6], sum(sizes.values()))
    return six


def verify(raw):
    types = check_ternary_types()
    cut_bytes = CUT_FILE.read_bytes()
    assert hashlib.sha256(cut_bytes).hexdigest() == CUT_DIGEST
    inputs = json.loads(cut_bytes)["cut_baselines"]["8_independent"]["class_records"]
    assert len(inputs) == len(raw["per_cut_class"]) == 13
    rule = frozen_rule()
    alternative = {start: Fraction() for start in STARTS}
    primary = alternative.copy()
    classes = []
    for index, (record, measured) in enumerate(zip(inputs, raw["per_cut_class"])):
        assert index == measured["cut_class"] and record["rows"] == measured["cut_rows"]
        # Exercise a different coordinate order and nontrivial independent
        # value swaps for every input. Only the evaluator knows the fresh set.
        perm = tuple((index - j) % 8 for j in range(8))
        rows = rule.recode(tuple(record["rows"]), perm, (0x5b + 29 * index) % 256)
        six = literal_conditional(rows, rule)
        assert six == Fraction(measured["projection_probabilities"]["6"])
        assert (1 - six) == Fraction(measured["projection_probabilities"]["8"])
        passive = unused_column_control(rows)
        classes.append({"cut_class": index, "signed_knot_six": str(six), "uniform_unused_six": str(passive)})
        for start in STARTS:
            weight = Fraction(record[start + "_probability"])
            primary[start] += weight * six
            alternative[start] += weight * passive
    for start in STARTS:
        assert primary[start] == Fraction(raw["by_start"][start]["projection_probabilities"]["6"])
    primary_score = (1 + abs(primary[STARTS[0]] - primary[STARTS[1]])) / 2
    passive_score = (1 + abs(alternative[STARTS[0]] - alternative[STARTS[1]])) / 2
    assert primary_score == Fraction(raw["equal_prior_recognition"])
    assert max(primary_score, passive_score) <= Fraction(26, 35)
    return {
        "ternary_classes": types, "cut_conditionals": classes,
        "signed_knot_six": {s: str(p) for s, p in primary.items()},
        "uniform_unused_six": {s: str(p) for s, p in alternative.items()},
        "equal_prior_recognition": {"signed_knots": str(primary_score), "uniform_unused": str(passive_score)},
        "uniform_unused_unordered_triples_per_cut": comb(24, 3),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(json.loads(args.results.read_text())), indent=2))
