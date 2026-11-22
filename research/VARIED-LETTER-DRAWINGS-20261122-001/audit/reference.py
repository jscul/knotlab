"""Independent replay primitives for the unchanged, previously audited reader."""

from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path
import sys


PRIOR_AUDIT = Path(__file__).resolve().parents[2] / "LEARNED-PATCH-GROUPS-20261122-001/audit"
sys.path.insert(0, str(PRIOR_AUDIT))
from group_oracle import committee, group_roster, mask_from_partition, priority, selected_groups
from panel_census import digest, equivalent, loads, read_jsonl, require
from pixel_counts import TURN_BIN, counts
from replay import (
    FLAG_START, HOLDING_COUNT, LAWS, PARTITIONS, RECEIPT_SIZE, STATS_START,
    calibrate, check_physical, hash_memory, physical_archive, vote_detail, write_value,
)
sys.path.pop(0)


ARMS = ("narrow", "varied")


def load(path):
    return loads(path.read_bytes())


def fit_reference(features, truth):
    candidates = list(group_roster(features, truth))
    require(len(features) == len(truth) == 64 and Counter(truth) == {0: 32, 1: 32}, "Wrong fitted bank size")
    selected = selected_groups(candidates)
    selected_masks = sorted(mask_from_partition(group.members) for group in selected)
    totals = [[sum(row[i] for row, label in zip(features, truth, strict=True) if label == action) for i in range(16)]
              for action in range(2)]
    size = len(selected[0].members) if selected else None
    score = reduced_score(selected[0].score) if selected else [0, 1]
    maximum = priority(selected[0])[:2] if selected else None
    tied = [group for group in candidates if priority(group)[:2] == maximum]
    closed = [group for group in tied if quarter_turn_closed(group.members)]
    return {
        "masks": selected_masks, "class_counts": [32, 32], "class_totals": totals, "score": score, "size": size,
        "informative_partitions": len(candidates), "partitions_searched": PARTITIONS,
        "maximal_masks_before_size_preference": sorted(mask_from_partition(group.members) for group in tied),
        "maximal_masks_by_size": dict(sorted(Counter(len(group.members) for group in tied).items())),
        "number_of_distinct_nonzero_rank_tiers": len({priority(group)[:2] for group in candidates}),
        "quarter_turn_closed_maximal_masks": sorted(mask_from_partition(group.members) for group in closed),
        "quarter_turn_closed_selected_masks": sorted(mask_from_partition(group.members) for group in selected
                                                     if quarter_turn_closed(group.members)),
    }


def reduced_score(score):
    if score[1] == 0:
        return [1, 0]
    fraction = Fraction(*score)
    return [fraction.numerator, fraction.denominator]


def quarter_turn_closed(members):
    return mask_from_partition(members) == mask_from_partition(tuple(TURN_BIN[bin_] for bin_ in members))


def read_groups(recipient, masks=None):
    if masks is None:
        masks = recipient["masks"]
    rosters = (tuple(i for i in range(15) if mask >> i & 1) for mask in masks)
    return list(calibrate(rosters, recipient["class_counts"], recipient["class_totals"]))


def acquisition_prefixes(features, target_bits):
    """Recover every issued majority action and prepared prefix independently."""
    holdings = bytearray(HOLDING_COUNT)
    earned_counts = [0, 0]
    for index, (histogram, target) in enumerate(zip(features, target_bits, strict=True)):
        guess = int(earned_counts[1] > earned_counts[0])
        correct = guess == target
        earned = guess if correct else 1 - guess
        earned_counts[earned] += 1
        cursor = 1 + RECEIPT_SIZE * index
        write_value(holdings, cursor, 2, 1 + 2 * earned)
        for bin_, value in enumerate(histogram):
            write_value(holdings, cursor + 2 + 7 * bin_, 7, value)
        yield guess, correct, {law: hash_memory(physical_archive(law, holdings)) for law in LAWS}


def fitted_physical_archive(law, refit):
    binary = bytearray(HOLDING_COUNT)
    write_value(binary, 0, 1, 1)
    for action in (0, 1):
        write_value(binary, STATS_START + 7 * action, 7, refit["class_counts"][action])
        for i, value in enumerate(refit["class_totals"][action]):
            write_value(binary, STATS_START + 14 + (16 * action + i) * 13, 13, value)
    for mask in refit["masks"]:
        binary[FLAG_START + mask - 1] = 1
    return physical_archive(law, binary)


def check_fitted_checkpoint(path, law, fitted):
    actual = load(path)
    check_physical(actual, law, fitted["masks"], fitted["class_counts"], fitted["class_totals"])
    require(equivalent(fitted_physical_archive(law, fitted), actual), f"Physical reconstruction differs: {path.name}")


def check_numeric_checkpoint(path, fitted):
    expected = {"class_totals": fitted["class_counts"], "class_bin_totals": fitted["class_totals"],
                "masks": fitted["masks"], "score": fitted["score"] if fitted["masks"] else None,
                "smaller_side_size": fitted["size"]}
    require(equivalent(load(path), expected), f"Numeric reconstruction differs: {path.name}")


def calibrate_conditions(fitted):
    output = {}
    for arm in ARMS:
        donor = ARMS[1 - ARMS.index(arm)]
        normal = fitted[arm]["ordinary"]
        ordinary = read_groups(normal)
        opposite = read_groups(fitted[arm]["opposite"])
        other = read_groups(fitted[donor]["ordinary"])
        crossing = read_groups(normal, fitted[donor]["ordinary"]["masks"])
        output[arm] = {
            "ordinary": ordinary, "opposite": opposite, "swapped-ordinary": opposite, "swapped-opposite": ordinary,
            "sham-ordinary": ordinary, "clear-ordinary": [], "restored-ordinary": ordinary, "erase-ordinary": [],
            "cross-ordinary": other, "other-groups-ordinary": crossing,
        }
    return output


def expected_checkpoint_digests(fitted):
    """Expected read-time adaptive state for every physical intervention."""
    memory = {}
    for arm, law in product(ARMS, LAWS):
        donor = ARMS[1 - ARMS.index(arm)]
        ordinary = fitted[arm]["ordinary"]
        opposite = fitted[arm]["opposite"]
        alternative = fitted[donor]["ordinary"]
        setups = {
            "ordinary": ordinary, "opposite": opposite, "swapped-ordinary": opposite,
            "swapped-opposite": ordinary, "sham-ordinary": ordinary, "restored-ordinary": ordinary,
            "erase-ordinary": {**ordinary, "masks": []}, "cross-ordinary": alternative,
            "other-groups-ordinary": {**ordinary, "masks": alternative["masks"]},
        }
        for condition, state in setups.items():
            memory[f"{arm}-{law}-{condition}"] = hash_memory(fitted_physical_archive(law, state))
        memory[f"{arm}-{law}-clear-ordinary"] = hash_memory(physical_archive(law, bytearray(HOLDING_COUNT)))
    return memory


