"""Repeat the physical comparison on the independently trained return cue."""

import argparse
from collections import Counter
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "causal.py"
CORE_SHA256 = "f57f2124498747c99c9950276f930b5c5025e75675a7be1f0909b96ca1519ee8"
B306 = HERE.parents[1] / "FEEDER-MEMORY-20261121-001"
sys.path.append(str(B306))


def core():
    if sha256(CORE.read_bytes()).hexdigest() != CORE_SHA256:
        raise ValueError("The original intervention protocol differs from its accepted source.")
    import bank
    import device
    import learning_train
    spec = importlib.util.spec_from_file_location("first_equal_exit_intervention", CORE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.HERE = HERE
    module.select_starts, module.sample_pair = bank.select_starts, bank.sample_pair
    module.LearnedKnotBot = device.LearnedKnotBot
    module.SECOND_FIELDS, module.SELECTED_FIELD = device.SECOND_FIELDS, device.SELECTED_FIELD
    module.load_frozen_weights = learning_train.load_frozen_weights
    return module


def collect_menu_splits(module, weights, ledger, out):
    with gzip.open(ledger, "rt") as file:
        pairs = json.load(file)
    with gzip.open(out / "causal_rows.json.gz", "rt") as file:
        rows = json.load(file)
    tallies, examples = {}, {}
    comparison = module.Comparison(weights)
    for index, (row, pair) in enumerate(zip(rows, pairs, strict=True)):
        assert row[:3] == [index, pair["law"], pair["panel"]]
        start = pair["empty"]["first_memory"]
        assert start == pair["full"]["first_memory"]
        current = 1 if pair["degree"] == 1 else 2 if pair["degree"] else 0
        group = "old_menu_matches" if start == current and start != 0 else "old_menu_different"
        bits = {arm: tuple(row[3+i]) for i,arm in enumerate(module.ARMS)}
        flags, rank = module.stats(pair, bits, row[8], row[10])
        scope = tallies.setdefault(pair["law"], {}).setdefault(pair["panel"], {})
        scope.setdefault(group, Counter()).update(flags)
        if group == "old_menu_different" and flags["useful_flips"] and flags["erasure_removes_useful_contrast"]:
            key = (module.CATEGORIES.index(pair["panel"]), *rank)
            law = pair["law"]
            if law not in examples or key < examples[law][0]:
                examples[law] = key, pair
    module.save(out / "menu_comparison.json", {
        "description": "The old menu condition on the strict cue, computed from equal frozen first memories and exact current degree.",
        "by_law": tallies, "rows": len(rows)})
    module.save(out / "menu_mismatch_replay.json", {
        "selection": "Correct reciprocal change with sham stable and erasure collapsing under the removed gate; primary then cross then secondary and the registered ranking.",
        "weights_sha256": module.sha(weights),
        "by_law": {law:comparison.compare(pair,detail=True) for law, (_,pair) in examples.items()}})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--weights", type=Path, default=HERE / "learning_weights.json")
    p.add_argument("--ledger", type=Path, default=HERE / "panel_pairs.json.gz")
    p.add_argument("--output-dir", type=Path, default=HERE)
    args = p.parse_args()
    study = core()
    study.run(args.weights,args.ledger,args.output_dir)
    collect_menu_splits(study, args.weights, args.ledger, args.output_dir)


if __name__ == "__main__":
    main()
