"""Independent fitted-tree and frozen grouped-reader reconstruction."""

from itertools import product
from pathlib import Path
import sys

from tree_oracle import (
    TREE_HOLDINGS, equivalent, fit_tree, hash_memory, loads, require, route,
    sensor_view, tree_archive, tree_memory, tree_prefix,
)


PRIOR_AUDIT = Path(__file__).resolve().parents[2] / "VARIED-LETTER-DRAWINGS-20261122-001/audit"
sys.path.insert(0, str(PRIOR_AUDIT))
from reference import (
    HOLDING_COUNT, acquisition_prefixes, fit_reference, fitted_physical_archive, physical_archive, read_groups, vote_detail,
)
sys.path.pop(0)


READERS = ("position", "window_tree", "window_group")
LAWS = ("parity", "nae")
CONVENTIONS = ("ordinary", "opposite")
TREE_SENSORS = {"position": "position", "window_tree": "window"}


def load(path):
    return loads(path.read_bytes())


def models_from_training(raw_images, targets):
    references = {}
    received = {}
    for reader, convention in product(READERS, CONVENTIONS):
        features = [sensor_view(reader, raw) for raw in raw_images]
        teachings = [target ^ (convention == "opposite") for target in targets]
        if reader == "window_group":
            state = fit_reference(features, teachings)
            neutral = {law: hash_memory(physical_archive(law, bytearray(HOLDING_COUNT))) for law in LAWS}
            ledger = []
            for guess, correct, physical in acquisition_prefixes(features, teachings):
                ledger.append((guess, correct, neutral, physical))
                neutral = physical
        else:
            state = fit_tree(features, teachings)
            ledger = list(tree_prefix(raw_images, teachings, TREE_SENSORS[reader]))
        references[reader, convention] = state
        received[reader, convention] = ledger
    return references, received


def fitted_words(reader, law, auxiliary):
    if reader == "window_group":
        return fitted_physical_archive(law, auxiliary)
    return tree_archive(auxiliary, law, TREE_SENSORS[reader])


def blank_words(reader, law):
    if reader == "window_group":
        return physical_archive(law, bytearray(HOLDING_COUNT))
    return tree_memory(law, TREE_SENSORS[reader], bytearray(TREE_HOLDINGS))


def numeric_group(fitted):
    return {"class_totals": fitted["class_counts"], "class_bin_totals": fitted["class_totals"],
            "masks": fitted["masks"], "score": fitted["score"] if fitted["masks"] else None,
            "smaller_side_size": fitted["size"]}


def evaluate(reader, fitted, features):
    if reader == "window_group":
        return vote_detail(features, read_groups(fitted))
    guess, _, path = route(fitted, features)
    return {"guess": guess, "features": list(features),
            "path": [{"feature": f, "threshold": t, "value": value, "branch": side} for _, f, t, value, side in path]}


def evaluate_all(raw, deployed):
    results = {}
    for reader in READERS:
        features = sensor_view(reader, raw)
        results[reader] = {mode: evaluate(reader, deployed[reader, mode], features) for mode in CONVENTIONS}
    return results
