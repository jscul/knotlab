"""Exact marginal distributions on a holder and its directly owned births."""

from collections import defaultdict
from fractions import Fraction
from itertools import product
import json
from math import lcm

from counts import StageCounts
from edits import holders
from exact_counts import boolean_words


def fraction(value):
    return [value.numerator, value.denominator]


def local_shape(preparation, edited, receipt, side, setting):
    observer = preparation.readers[side]
    before = holders(edited)
    own_before = tuple(sorted(preparation.base[observer]))
    own_after = tuple(sorted(edited[observer]))
    visible = sorted((row for row in receipt["births"] if observer in row["parents"]),
                     key=lambda row: (row["parents"], row["old_inputs"]))
    # Child identities within the local record follow their parent/old-input role,
    # so an unobserved extra birth cannot change a visible record by shifting IDs.
    children = [{key: row[key] for key in ("parents", "old_inputs", "fresh_count")} for row in visible]
    old_ids = tuple(sorted(set(own_after) | {bit for row in visible for _, bit in row["old_inputs"]}))
    fresh_ids = tuple(bit for row in visible for bit in row["fresh"])
    ownership = [(bit, tuple(before[bit]), tuple(i for i, row in enumerate(visible) if bit in dict(row["old_inputs"]).values()))
                 for bit in old_ids]
    shape = {"preparation": preparation.name, "own_setting": setting, "holder": observer,
             "before_values_order": own_before, "own_edited_support": own_after,
             "after_old_values_order": old_ids, "owned_births": children, "old_ownership": ownership,
             "visible_missing_birth_while_live": not visible and any(len(before[bit]) == 1 for bit in own_after),
             "visible_zero_fresh_child": any(not row["fresh"] for row in visible)}
    return shape, own_before, old_ids, fresh_ids, visible


def pack_distribution(weight):
    assert sum(weight.values()) == 1 and all(value > 0 for value in weight.values())
    denominator = lcm(*(value.denominator for value in weight.values()))
    return {"denominator": denominator, "positive_cells": {key: int(value * denominator) for key, value in weight.items()}}


def local_record(preparation, edited, receipt, settings, side, law, base_counter, final_counter):
    shape, own_before, old_ids, fresh_ids, visible = local_shape(preparation, edited, receipt, side, settings[side])
    universe = set(holders(preparation.base))
    observed_baseline = tuple(sorted(set(own_before) | (set(old_ids) & universe)))
    observed_optional = tuple(bit for bit in old_ids if bit not in universe)
    counts = base_counter.histogram(observed_baseline, "U")[0]
    optional = list(product((0, 1) if law == "nae" else (0,), repeat=len(observed_optional)))
    lifted = defaultdict(Fraction)
    for word, count in zip(boolean_words(len(observed_baseline)), counts, strict=True):
        if not count:
            continue
        old = dict(zip(observed_baseline, map(int, word), strict=True))
        before = "".join(str(old[bit]) for bit in own_before)
        for values in optional:
            current = {**old, **dict(zip(observed_optional, values, strict=True))}
            old_view = "".join(str(current[bit]) for bit in old_ids)
            choices = [completions(row, current, law) for row in visible]
            completions_count = 1
            for choice in choices:
                assert choice
                completions_count *= len(choice)
            mass = Fraction(count, base_counter.total() * len(optional) * completions_count)
            for complete in product(*choices):
                lifted[before + "|" + old_view + "|" + "".join(complete)] += mass

    marks = old_ids + fresh_ids
    whole_mass = final_counter.histogram(marks, "U")[0]
    uniform = {word: Fraction(count, final_counter.total())
               for word, count in zip(boolean_words(len(marks)), whole_mass, strict=True) if count}
    primary_after = defaultdict(Fraction)
    for key, weight in lifted.items():
        _, after, fresh = key.split("|")
        primary_after[after + fresh] += weight
    return {"structure": shape, "physical_fresh_ids_in_record_order": fresh_ids,
            "carried_old_state_full": pack_distribution(lifted),
            "carried_old_state_after_only": pack_distribution(primary_after),
            "uniform_final_after_only": pack_distribution(uniform),
            "uniform_final_vs_carried_after_only_tv": fraction(tv(primary_after, uniform))}


def completions(row, values, law):
    old = tuple(values[bit] for _, bit in row["old_inputs"])
    words = []
    for fresh in product((0, 1), repeat=row["fresh_count"]):
        scope = old + fresh
        lawful = sum(scope) % 2 == 0 if law == "parity" else len(set(scope)) == 2
        if lawful:
            words.append("".join(map(str, fresh)))
    return words


def tv(left, right):
    return sum((abs(left.get(word, 0) - right.get(word, 0)) for word in left.keys() | right.keys()), Fraction()) / 2


def record_tv(left, right, weighting):
    if left["structure"] != right["structure"]:
        return Fraction(1)
    a, b = left[weighting], right[weighting]
    den_a, den_b = a["denominator"], b["denominator"]
    return tv({key: Fraction(n, den_a) for key, n in a["positive_cells"].items()},
              {key: Fraction(n, den_b) for key, n in b["positive_cells"].items()})


def weighted_old_support(preparation, edited, result_supports, law, final_counter):
    edited_model = StageCounts(law, edited, edited)
    original_requirements = tuple(base for base, row in zip(preparation.base, edited, strict=True) if base != row)
    both = edited + original_requirements
    same_support = StageCounts(law, both, both + result_supports[len(edited):])
    return {"uniform_edited_total": edited_model.total(), "uniform_final_total": final_counter.total(),
            "uniform_edited_mass_on_prepared_old_relation": fraction(Fraction(same_support.retained(), edited_model.total())),
            "uniform_final_mass_on_prepared_old_relation": fraction(Fraction(same_support.total(), final_counter.total()))}
