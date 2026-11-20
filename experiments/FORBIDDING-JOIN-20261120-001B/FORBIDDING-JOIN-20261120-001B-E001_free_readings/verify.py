"""Independently check saved free-setting scores and exact counts on named controls."""

from collections import Counter
from fractions import Fraction
from functools import lru_cache
import gzip
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from knotlab import Relation, check_knot  # noqa: E402

PRIOR = (ROOT / "experiments/ENTANGLEMENT-READ-20261120-001B/"
         "ENTANGLEMENT-READ-20261120-001B-E001_separated_readings/verify.py")
spec = spec_from_file_location("earlier_independent", PRIOR)
independent = module_from_spec(spec)
spec.loader.exec_module(independent)
DATA = ROOT / "artifacts" / HERE.parent.name / HERE.name / "exact_readings.json.gz"
FAMILIES = (("external_pairs", 2), ("six_marks", 3))
BRUTE_SOURCES = {"single_ternary", "two_disjoint", "two_sharing_one", "closure_bare", "closure_spare", "two_relays"}


@lru_cache(maxsize=None)
def canonical_verdict(arity, projected):
    """The prior forgetting checker runs on each distinct actually projected relation."""
    symbols = tuple(f"d{i}" for i in range(arity))
    allowed = set(projected)
    relation = Relation.from_predicate(
        symbols, lambda values: sum(1 << i for i, name in enumerate(symbols) if values[name]) in allowed)
    verdict = check_knot(relation, symbols[:-1], symbols[-1])
    return verdict.binding, verdict.loss_on_erasure, verdict.coexistence


def check_certificates(stage, law):
    assert stage["every_displayed_support_lawful"] == all(row["eligible"] for row in stage["support_certificates"])
    for support, cell in zip(stage["supports"], stage["support_certificates"], strict=True):
        n = len(support)
        if n < 3:
            assert not cell["eligible"]
            continue
        if law == "nae":
            patterns = tuple(cell["projected_patterns"])
            ordinary = tuple(range(1, (1 << n) - 1))
        else:
            equations = [sum(1 << support.index(bit) for bit in row) for row in cell["projected_equations"]]
            patterns = tuple(word for word in range(1 << n)
                             if all((word & row).bit_count() % 2 == 0 for row in equations))
            ordinary = tuple(word for word in range(1 << n) if word.bit_count() % 2 == 0)
        assert len(patterns) == cell["projected_count"] and len(ordinary) == cell["expected_count"]
        assert (patterns == ordinary) == cell["full_law"]
        assert canonical_verdict(n, patterns) == tuple(cell[key] for key in ("k1", "k2", "k3"))


def rows(stage):
    for family, width in FAMILIES:
        for slot in stage.get(family, {}).get("slots", []):
            if slot["placement"]:
                yield slot["placement"], slot["result"], width, slot["band"]
        for entry in stage.get("matched_predecessor_marks", {}).get(family, []):
            if "result" in entry:
                prior = entry["prior"]
                yield prior["placement"], entry["result"], width, prior["band"]


def verify_weights(stage, graph, counts):
    for placement, measured, width, band in rows(stage):
        marks = measured["mark_order"]
        assert marks == placement["alice"] + placement["bob"] and len(set(marks)) == 2 * width
        expected = independent.steps_between(graph, placement["alice"], placement["bob"])
        assert expected == placement["cross_steps"]
        assert band == ("no_chain" if expected is None else "2" if expected == 2 else "finite_3_or_more")
        assert expected is None or expected >= 2
        assert all(stage["support_certificates"][index]["eligible"] for index in placement["supports"])
        weights = measured["weightings"]
        raw = weights["U"]["counts"]
        assert sum(raw) == stage["complete_states"]
        half = len(raw) // 2
        assert weights["T"]["counts"] == raw[:half] + [2 * value for value in raw[half:]]
        assert ("undefined" in weights["L"]) == (stage["lost_previous_states"] > 0)
        transported = weights["L_survival"] if stage["lost_previous_states"] else weights["L"]
        assert sum(transported["counts"]) == transported["integer_units_per_unscaled_mass"] * stage["surviving_previous_states"]
        for weighting in weights.values():
            if "undefined" in weighting:
                continue
            counts["weighted_tables"] += 1
            mass = weighting["counts"]
            tables = weighting["readings"]
            assert sum(mass) == weighting["total"] > 0
            for context, computed in zip(tables["contexts"], independent.independent_contexts(mass, False, width), strict=True):
                independent.check_context(mass, context, computed, "external", band)
            zero = [[[0, 1]] * 2] * 2
            assert tables["pair_marginal_remote_tv"] == zero
            for read in ("I", "II"):
                row = tables[read]
                assert row["outcome_marginal_remote_tv"] == zero
                correlators = [Fraction(*context[read]["correlation"]) for context in tables["contexts"]]
                expected_sums = {sign: sum(value * s for value, s in zip(correlators, sign, strict=True))
                                 for sign in product((1, -1), repeat=4) if sign.count(-1) % 2}
                scores = {tuple(cell["signs"]): Fraction(*cell["value"]) for cell in row["chsh_sign_scores"]}
                assert scores == expected_sums
                assert Fraction(*row["signed_s"]) == scores[(1, 1, 1, -1)]
                assert Fraction(*row["maximum"]) == max(scores.values()) <= 2
        counts["placement_records"] += 1


@lru_cache(maxsize=12)
def brute_states(supports, law):
    all_bits = sorted({d for support in supports for d in support})
    positions = {bit: i for i, bit in enumerate(all_bits)}
    states = np.arange(1 << len(all_bits), dtype=np.uint32)
    for support in supports:
        word = encode(states, positions, support)
        if law == "parity":
            even = np.asarray([value.bit_count() % 2 == 0 for value in range(1 << len(support))])
            states = states[even[word]]
        else:
            states = states[(word != 0) & (word != (1 << len(support)) - 1)]
    return states, positions


def encode(states, positions, marks):
    indices = np.zeros(states.shape, dtype=np.int32)
    for bit in marks:
        indices = 2 * indices + ((states >> positions[bit]) & 1).astype(np.int32)
    return indices


def check_small(source, stage, old, law, counts):
    supports = tuple(tuple(support) for support in stage["supports"])
    assert len(stage["distinct_names"]) <= 24
    states, positions = brute_states(supports, law)
    old_code = encode(states, positions, old["distinct_names"])
    fibers = np.bincount(old_code)
    initial_code = encode(states, positions, list(range(max(map(max, source["initial_supports"])) + 1)))
    assert len(states) == stage["complete_states"]
    assert np.count_nonzero(fibers) == stage["surviving_previous_states"]
    assert len(np.unique(initial_code)) == stage["surviving_initial_states"]
    for support, certificate in zip(supports, stage["support_certificates"], strict=True):
        patterns = sorted(map(int, np.unique(encode(states, positions, support))))
        assert len(patterns) == certificate["projected_count"]
        width = len(support)
        assert certificate["k1"] == (len(patterns) < 1 << width)
        assert certificate["k2"] == all(len({w & ~(1 << i) for w in patterns}) == 1 << (width - 1) for i in range(width))
        assert certificate["k3"] == bool(patterns)
    counts["brute_stages"] += 1
    for _, measured, width, _ in rows(stage):
        code = encode(states, positions, measured["mark_order"])
        size = 1 << (2 * width)
        weights = measured["weightings"]
        assert np.bincount(code, minlength=size).tolist() == weights["U"]["counts"]
        lifted = [Fraction()] * size
        multiplicity = fibers[old_code]
        for degree in np.unique(multiplicity):
            bins = np.bincount(code[multiplicity == degree], minlength=size)
            lifted = [value + Fraction(int(amount), int(degree)) for value, amount in zip(lifted, bins, strict=True)]
        key = "L_survival" if stage["lost_previous_states"] else "L"
        cell = weights[key]
        assert lifted == [Fraction(weight, cell["integer_units_per_unscaled_mass"]) for weight in cell["counts"]]
        counts["brute_placements"] += 1


def parity_count(stage, marks=(), values=()):
    """Reduce with least available pivots after substituting the pins."""
    keep = set(marks)
    ones = {d for d, bit in zip(marks, values, strict=True) if bit}
    basis = {}
    for row in stage["supports"]:
        mask = sum(1 << d for d in row if d not in keep)
        rhs = len(ones.intersection(row)) % 2
        while mask:
            pivot = mask & -mask
            if pivot not in basis:
                basis[pivot] = mask, rhs
                break
            other, known = basis[pivot]
            mask ^= other
            rhs ^= known
        if not mask and rhs:
            return 0
    return 1 << (len(stage["distinct_names"]) - len(marks) - len(basis))


def nae_count(old, stage, marks=(), values=(), *, lifted=False, units=1):
    # Inclusion–exclusion handles the old supports. Descendant births then have disjoint inputs and fresh names.
    encode_bits = lambda bits: sum(1 << d for d in bits)
    fresh = [(encode_bits(row["inputs"]), encode_bits(row["fresh"])) for row in stage["transition"]["births"]]
    names = encode_bits(stage["distinct_names"])
    leftover = names ^ sum(inputs | born for inputs, born in fresh)
    pins = [encode_bits(d for d, bit in zip(marks, values, strict=True) if bit == color) for color in (0, 1)]
    requested = pins[0] | pins[1]
    count = 0
    for old_zero, old_one, sign in independent.inclusion_exclusion_terms(old["supports"]):
        if old_zero & pins[1] or old_one & pins[0]:
            continue
        zeros, ones = old_zero | pins[0], old_one | pins[1]
        fixed = zeros | ones
        term = sign * (1 << (leftover & ~fixed).bit_count())
        for inputs, born in fresh:
            if not lifted or not born:
                scope = inputs | born
                term *= (1 << (scope & ~fixed).bit_count()) - int(not scope & zeros) - int(not scope & ones)
                continue
            input_choices = 1 << (inputs & ~fixed).bit_count()
            if not born & requested:
                term *= input_choices
                continue
            f = 1 << born.bit_count()
            remaining = 1 << (born & ~fixed).bit_count()
            all_zero, all_one = int(not inputs & ones), int(not inputs & zeros)
            term *= ((input_choices - all_zero - all_one) * remaining * (f - 1)
                     + f * (all_zero * (remaining - int(not born & ones)) + all_one * (remaining - int(not born & zeros))))
        count += term
    expected_units = 1
    if lifted:
        for _, born in fresh:
            if born & requested:
                f = 1 << born.bit_count()
                expected_units *= f * (f - 1)
    assert expected_units == units
    return count


def check_archive(stage, old, law, checks):
    if law == "parity":
        total = parity_count(stage)
        fibers = 1 << sum(max(0, row["f"] - 1) for row in stage["transition"]["births"])
        assert stage["surviving_previous_states"] * fibers == total
    else:
        total = nae_count(old, stage)
        assert nae_count(old, stage, lifted=True) == stage["surviving_previous_states"]
    assert total == stage["complete_states"]
    preferred = max(rows(stage), key=lambda row: (row[2], max(row[1]["mark_order"])), default=None)
    assert preferred is not None
    _, measured, width, _ = preferred
    marks = measured["mark_order"]
    words = list(product((0, 1), repeat=2 * width))
    weights = measured["weightings"]
    if law == "parity":
        reconstructed = [parity_count(stage, marks, word) for word in words]
    else:
        reconstructed = [nae_count(old, stage, marks, word) for word in words]
        cell = weights["L_survival"] if stage["lost_previous_states"] else weights["L"]
        lifted = [nae_count(old, stage, marks, word, lifted=True, units=cell["integer_units_per_unscaled_mass"])
                  for word in words]
        assert lifted == cell["counts"]
    assert reconstructed == weights["U"]["counts"]
    checks["archive_stages"] += 1


def main():
    data = json.loads(gzip.decompress(DATA.read_bytes()))
    counts = Counter()
    for source in data["sources"]:
        for law, variants in source["laws"].items():
            for stages in variants.values():
                previous = stages[0]
                for stage in stages:
                    if stage["status"] != "reached":
                        continue
                    assert stage["complete_states"] > 0
                    assert stage["previous_stage_states"] == previous["complete_states"]
                    assert stage["lost_previous_states"] == stage["previous_stage_states"] - stage["surviving_previous_states"]
                    if stage["age"]:
                        assert stage["supports"][:len(previous["supports"])] == previous["supports"]
                    check_certificates(stage, law)
                    graph = independent.adjacency_of(stage["supports"])
                    verify_weights(stage, graph, counts)
                    if source["name"] in BRUTE_SOURCES:
                        check_small(source, stage, previous, law, counts)
                    if source["group"] == "archive" and stage["age"]:
                        check_archive(stage, previous, law, counts)
                    previous = stage
    counts["canonical_projected_relations"] = canonical_verdict.cache_info().currsize
    print(json.dumps(dict(sorted(counts.items()))))


if __name__ == "__main__":
    main()
