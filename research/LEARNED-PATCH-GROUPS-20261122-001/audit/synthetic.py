"""Adversarial pre-run checks on artificial binary stencils and count vectors."""

import argparse
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path

from group_oracle import committee, group_roster, mask_from_partition, selected_groups
from panel_census import require
from pixel_counts import FIXED_CODING, counts
from subsets import subset_projections


def source_module(path):
    spec = spec_from_file_location(path.stem, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def synthetic_selection(learner, ordinary):
    base = [0] * 16
    base[4] = 77

    def hist(first, second):
        result = base[:]
        result[first] += 2
        result[second] += 2
        return tuple(result)

    rows = (hist(0, 1), hist(14, 15))
    labels = (0, 1)
    test = (hist(0, 14), tuple(value + int(index in (0, 1, 14, 15)) for index, value in enumerate(base)), *rows)
    rosters = []
    for order in (tuple(range(16)), FIXED_CODING):
        renamed = lambda row: tuple(row[column] for column in order)
        training = tuple(map(renamed, rows))
        selected = selected_groups(list(group_roster(training, labels)))
        wanted = sorted(mask_from_partition(group.members) for group in selected)
        require(len(wanted) == 4 and len(set(wanted)) == 4, "All four singleton winners must be retained")
        first, second = ([row] for row in training)
        masks, numerator, denominator = learner._fit_masks((first, second))
        require((masks, numerator, denominator) == (wanted, 1, 0), "Physical synthetic selector differs")
        numeric = ordinary.fit_histograms(training, labels)
        require(numeric["masks"] == wanted and numeric["score"] == [1, 0], "Numeric synthetic selector differs")
        for row, want in zip(test, (0, 0, 0, 1), strict=True):
            projected = renamed(row)
            decision, votes = committee(projected, selected)
            actual = ordinary.explain_histogram(projected, numeric)
            require(decision == actual["action"] == want, "Synthetic committee action differs")
            require(actual["votes"] == [votes[0], votes[1]] and actual["abstentions"] == votes[None], "Synthetic votes differ")
        rosters.append({tuple(sorted(order[index] for index in group.members)) for group in selected})
    require(rosters[0] == rosters[1], "Feature renaming did not transport tied winners")
    require(learner._fit_masks(([rows[0]], [rows[0]])) == ([], 0, 1), "No-contrast physical selector is active")
    require(ordinary.fit_histograms((rows[0], rows[0]), labels)["masks"] == [], "No-contrast numerical selector is active")

    # Splitting a constant sum of four across two active bins gives 1/7 exactly.
    finite = ((1, 3), (3, 1), (2, 2), (2, 2), (2, 2), (4, 0))
    target = (0, 0, 1, 1, 1, 1)
    oracle = selected_groups(list(group_roster(finite, target)))
    require(len(oracle) == 1 and Fraction(*oracle[0].score) == Fraction(1, 7), "Invalid computed synthetic finite rank")
    return {"tied_winners": 4, "anonymous_recodings": 2, "decisions_per_coding": 4, "finite_rank": "1/7"}


def synthetic_memory(learner, ordinary):
    triple_space = set(product((0, 1), repeat=3))
    pair_space = set(product((0, 1), repeat=2))
    bad = {"parity": {(0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 1)}, "nae": {(0, 0, 0), (1, 1, 1)}}
    stencils = ("0" * 64, "1" * 64, "1" + "0" * 63, "0" * 63 + "1", "0" * 27 + "1" + "0" * 36)
    for raw in stencils:
        pixels = tuple(map(int, raw))
        expected = counts(raw)
        require(learner.pattern_counts(pixels) == expected == tuple(ordinary.histogram(pixels)), "Synthetic sensor mismatch")

    reports = {}
    first, second = (tuple(map(int, raw)) for raw in stencils[:2])
    for law, forbidden in bad.items():
        allowed = triple_space - forbidden
        require(allowed == set(learner.OPEN_RELATIONS[law]), "Physical regime has different support")
        require(0 < len(allowed) < 8, "K1 or K3 failed")
        require(all({triple[:index] + triple[index + 1:] for triple in allowed} == pair_space for index in range(3)), "K2 failed")

        executable = set()
        device = learner.KnotLearner(law)
        for word in triple_space:
            try:
                device.prepare_holding(0, word)
            except ValueError:
                continue
            require(int(device.export_memory()["words"][:2], 16) == sum(bit << (2 - i) for i, bit in enumerate(word)),
                    "Admitted open word differs from durable holdings")
            executable.add(word)
        require(executable == allowed, "Executable open law rejected or added a holding")

        device = learner.KnotLearner(law)
        neutral = device.export_memory()
        for index, pixels in enumerate((first, second)):
            guess = device.predict(pixels)
            device.learn(pixels, guess, guess == index)
        result = device.finalize()
        fitted = device.export_memory()
        require(result["class_counts"] == [1, 1], "Fit did not retain one observation per action")
        require((device.predict(first), device.predict(second)) == (0, 1), "Synthetic fitted readout mismatch")
        twin = learner.KnotLearner.from_memory(fitted)
        twin.swap_actions()
        require((twin.predict(first), twin.predict(second)) == (1, 0), "Synthetic action exchange failed")
        device.erase_selection()
        erased = device.export_memory()
        flags_suffix = learner.PARTITION_COUNT * 2
        require(erased["words"][:-flags_suffix] == fitted["words"][:-flags_suffix], "Flag erase changed calibration")
        require(device.selection()["masks"] == [] and device.predict(second) == 0, "Flag erase preserved active readout")
        device.restore_memory(fitted)
        require(device.predict(second) == 1, "Physical-only restoration failed")
        require(device.clear_memory() == fitted and device.export_memory() == neutral, "Clear did not restore neutral state")

        bad_inputs = {
            "hidden conventional copy": {**fitted, "centroids": []},
            "wrong logical code": {**fitted, "words": "00" + fitted["words"][2:]},
            "truncated packed holdings": {**fitted, "words": fitted["words"][:-2]},
            "invalid training budget": {**fitted, "training_limit": 63},
            "unexpected acquisition receipt": {**fitted, "words": fitted["words"][:2] + fitted["words"][:2] + fitted["words"][4:]},
        }
        for name, mutated in bad_inputs.items():
            try:
                device.restore_memory(mutated)
            except ValueError:
                continue
            raise ValueError(f"{law}: accepted {name}")
        require(device.export_memory() == neutral, "Rejected restore changed state")
        reports[law] = {"executable_support": sorted(executable), "rejected_memory_mutations": list(bad_inputs),
                        "fit_restore_and_intervention_checked": True}

    return {"padded_sensor_stencils": len(stencils), "laws": reports}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("producer", type=Path)
    args = parser.parse_args()
    physical = source_module(args.producer / "learner.py")
    control = source_module(args.producer / "ordinary.py")
    count = sum(1 for _ in subset_projections(((1,) * 16,)))
    require(count == 65536, "Independent subset enumerator omitted some masks")
    print(json.dumps({"synthetic_subset_projections": count, "selection": synthetic_selection(physical, control),
                      "laws_and_sensor": synthetic_memory(physical, control)}, indent=2, sort_keys=True))
