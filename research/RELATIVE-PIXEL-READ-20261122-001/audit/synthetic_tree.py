#!/usr/bin/env python3
"""Pre-run source checks on invented stencils and feature vectors only."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path

from tree_oracle import (
    PREPARED, TREE_BASE, TREE_HOLDINGS, fit_tree, hash_memory, require, sensor_view, tree_archive, tree_prefix,
)


def module_at(path):
    spec = spec_from_file_location(path.stem, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def image(cells, top=0, left=0):
    offsets = {8 * (top + row) + left + col for row, col in cells}
    return "".join("1" if i in offsets else "0" for i in range(64))


def ranks(reader, numeric):
    # Duplicate feature IDs and equal-gain integer thresholds exercise exact tie order.
    tie = [(tuple(value for _ in range(2)), bit) for value, bit in ((0, 0), (2, 1), (4, 0))]
    no_gain = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]
    for case, track in ((tie, "one preferred split"), (no_gain, "zero gain")):
        oracle = fit_tree(*zip(*case, strict=True))
        require(oracle == reader._fit_tree(case) == numeric._grow(case, 2), f"Independent rank fixture differs: {track}")
    chosen = reader._fit_tree(tie)
    require((chosen["feature"], chosen["threshold"]) == (0, 0), "Did not prefer lower feature and lower cutoff")
    require(reader._fit_tree(no_gain) == {"vote": 0}, "Zero-signal tied leaf did not default to zero")
    return {"synthetic_rank_fixtures": 2, "lowest_feature_and_threshold_wins": True, "positive_gain_only": True}


def strict_state_tests(reader, numeric):
    images = (image(()), image(((0, 0),)), image(((0, 0), (0, 1))), image(((0, 0), (1, 0))),
              image(((0, 0), (1, 0)), top=5, left=6), image(((0, 2), (1, 0), (1, 2))))
    require(sensor_view("position", images[3]) == sensor_view("position", images[4]), "Translation did not preserve support")
    require(sensor_view("position", images[2]) != sensor_view("position", images[3]), "The independent alignment folded a turn")
    for model, sensor in (("position", "position"), ("window_tree", "window")):
        sense = getattr(numeric, sensor + "_features")
        for raw in images:
            expected = sensor_view(model, raw)
            require(reader.features(tuple(map(int, raw)), sensor) == expected == tuple(sense(raw)), "Synthetic sensory mismatch")

    order = (images[2], images[3], images[4], images[5]) * 16
    targets = (0, 1, 1, 0) * 16
    relations = {"parity": {(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)},
                 "nae": set(product((0, 1), repeat=3)) - {(0, 0, 0), (1, 1, 1)}}
    suite = {}
    for law, (model, sensor) in product(PREPARED, (("position", "position"), ("window_tree", "window"))):
        device = reader.KnotTree(law, sensor)
        expected_relation = relations[law]
        require(0 < len(expected_relation) < 8 and all(
            {word[:i] + word[i+1:] for word in expected_relation} == {(0, 0), (0, 1), (1, 0), (1, 1)} for i in range(3)),
            "Expected open relation failed a projection gate")
        for address in (0, 1, 3, TREE_BASE, TREE_BASE + 14, TREE_HOLDINGS - 1):
            actual = set()
            for word in product((0, 1), repeat=3):
                try:
                    device.prepare_holding(address, word)
                except ValueError:
                    continue
                actual.add(word)
            require(actual == expected_relation, f"{law} at {address}: wrong executable open support")

        device.clear_memory()
        twin = numeric.IntegerTree(sensor)
        for pixels, target, prefix in zip(order, targets, tree_prefix(order, targets, sensor), strict=True):
            guess, correct, before, after = prefix
            bits = tuple(map(int, pixels))
            require(device.predict(bits) == twin.predict(bits) == guess and correct == (guess == target), "Acquisition guess differs")
            require(hash_memory(device.export_memory()) == before[law], "Incorrect before-state holding digest")
            device.learn(bits, guess, correct)
            twin.learn(bits, guess, correct)
            require(hash_memory(device.export_memory()) == after[law], "Incorrect after-state holding digest")
        model_tree = fit_tree([sensor_view(model, raw) for raw in order], targets)
        exact = tree_archive(model_tree, law, sensor)
        require(device.finalize() == twin.finalize() == model_tree and device.export_memory() == exact,
                f"{law}/{sensor}: wrong synthetic fitted words or structure")
        independently_loaded = reader.KnotTree.from_memory(exact)
        expected_actions = [device.predict(tuple(map(int, test))) for test in images]
        require([independently_loaded.predict(tuple(map(int, test))) for test in images] == expected_actions,
                "Physical-only reload changed actions")
        mutations = {
            "unprepared first word": {**exact, "words": "00" + exact["words"][2:]},
            "lost physical word": {**exact, "words": exact["words"][:-2]},
            "deployed acquisition retained": {**exact, "words": exact["words"][:2] * 2 + exact["words"][4:]},
            "adaptive numeric field": {**exact, "tree": model_tree},
            "unexpected phase budget": {**exact, "training_limit": 65},
        }
        for mutation, invalid in mutations.items():
            try:
                device.restore_memory(invalid)
            except ValueError:
                continue
            raise ValueError(f"{law}/{sensor} accepted {mutation}")
        require(device.export_memory() == exact, "Failed restorations changed fitted words")
        suite[f"{law}/{sensor}"] = {"K1_K2_K3_allowed": len(expected_relation), "real_holding_addresses": 6,
                                    "prefixes_verified": 64, "rejected_mutations": list(mutations)}
    return {"synthetic_stencils": len(images), "open_law_and_fit": suite, "fresh_or_public_pair_rows_read": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("producer", type=Path)
    source = parser.parse_args().producer
    physical, conventional = (module_at(source / name) for name in ("reader.py", "ordinary.py"))
    print(json.dumps({"rank": ranks(physical, conventional), "state": strict_state_tests(physical, conventional)},
                     indent=2, sort_keys=True))
