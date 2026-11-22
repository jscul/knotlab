"""Run repaired survival with the frozen original evaluation driver."""

import argparse
from collections import defaultdict
import csv
from hashlib import sha256
import json
from pathlib import Path
from statistics import fmean

if __package__:
    from . import bank, device, learning_train
else:
    import bank
    import device
    import learning_train


HERE = bank.HERE
_core = bank.load_original("survival_eval.py", {"bank": bank, "device": device, "learning_train": learning_train})
READERS, make_reader, replay_survival = _core.READERS, _core.make_reader, _core.replay_survival
FOUNDER_CONTROLS = ("current", "old", "erased", "strict", "feedback_permuted")


def _founder_effects(natural, digest):
    grouped = defaultdict(list)
    for (law, key, _), block in natural.items():
        grouped[law, key].append(block)
    by_law = {law: [] for law in bank.LAWS}
    for (law, key), games in grouped.items():
        first = games[0]["learned"]
        if len(games) != bank.TAPES:
            raise RuntimeError("Incomplete paired tapes for a founder.")
        contrasts = {}
        for alias in FOUNDER_CONTROLS:
            deltas = [int(game["learned"]["turns"]) - int(game[alias]["turns"]) for game in games]
            contrasts[alias] = {"mean_turn_difference": fmean(deltas), "wins": sum(d > 0 for d in deltas),
                                "ties": deltas.count(0), "losses": sum(d < 0 for d in deltas)}
        by_law[law].append({"source_key": key, "seed": int(first["seed"]),
                           "first_funded": bool(int(first["first_funded"])),
                           "growth_stop": first["growth_stop"], "contrasts": contrasts})

    strata = {}
    for law, founders in by_law.items():
        strata[law] = {}
        for name, members in (("all", founders),
                              ("first_funded", [r for r in founders if r["first_funded"]]),
                              ("no_first_birth", [r for r in founders if not r["first_funded"]])):
            summaries = {}
            for control in FOUNDER_CONTROLS:
                effects = [r["contrasts"][control]["mean_turn_difference"] for r in members]
                summaries[control] = {
                    "mean_turn_difference": fmean(effects) if effects else None,
                    "founders_positive": sum(value > 0 for value in effects),
                    "founders_equal": effects.count(0), "founders_negative": sum(value < 0 for value in effects),
                }
            strata[law][name] = {"founders": len(members), "contrasts": summaries}
    return {"schema": "return-cue-founder-effects-v1", "weights_sha256": digest, "by_law": by_law,
            "funding_strata": strata}


def _audit_aliases(output, controls, scores, digest):
    natural = defaultdict(dict)
    with (output / "survival_episodes.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            key = row["law"], row["source_key"], row["replicate"]
            if row["reader"] in natural[key]:
                raise RuntimeError("Duplicate paired episode in the return-cue ledger.")
            natural[key][row["reader"]] = row
    common = defaultdict(list)
    with (output / "survival_common_path.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            common[row["law"]].append(row)

    by_law = {}
    for law in bank.LAWS:
        expected = controls["by_law"][law]
        aliases = dict(expected["aliases"])
        # When available, compare an independently mounted fixed readout even
        # if the reconstructed selector equals the trained selector.
        selector = expected["packets"][-1]["reconstructed_selector"]
        aliases["replace_strict_credit"] = {0: "zero", 1: "strict"}.get(selector, aliases["replace_strict_credit"])
        blocks = [readers for (key_law, _, _), readers in natural.items() if key_law == law]
        result = {}
        for control, alias in aliases.items():
            if alias is None:
                result[control] = {"reader_alias": None, "status": "no evaluated fixed readout for this selector"}
                continue
            pairs = [(readers["learned"], readers[alias]) for readers in blocks]
            differences = [int(learned["turns"]) - int(fixed["turns"]) for learned, fixed in pairs]
            hashes = sum(a["public_history_sha256"] == b["public_history_sha256"] for a, b in pairs)
            bits = sum(row["learned"] == row[alias] for row in common[law])
            interval = ([0.0, 0.0] if alias == "learned" else
                        scores["by_law"][law]["learned_minus"][alias]["founder_bootstrap_95_percent_interval"])
            result[control] = {
                "reader_alias": alias, "paired_episodes": len(pairs), "matching_full_public_histories": hashes,
                "mean_turn_difference_learned_minus_alias": fmean(differences), "founder_interval": interval,
                "wins": sum(d > 0 for d in differences), "ties": differences.count(0),
                "losses": sum(d < 0 for d in differences), "common_feeder_decisions": len(common[law]),
                "matching_common_decisions": bits,
            }
        by_law[law] = result
    alias = {"schema": "return-cue-count-survival-v1", "weights_sha256": digest,
             "evaluation_adapter_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
             "added_games": 0, "by_law": by_law}
    return alias, _founder_effects(natural, digest)


def run(bank_path, weights_path, digest, output_dir):
    weights_path, output = Path(weights_path), Path(output_dir)
    weights = learning_train.load_frozen_weights(weights_path, digest)
    book = json.loads(weights_path.with_name("learning_training.json").read_bytes())
    count_control = json.loads(weights_path.with_name("learning_count_only.json").read_bytes())
    if count_control != learning_train.count_controls(weights, book, digest):
        raise ValueError("The outcome-free training-opportunity record does not reproduce.")
    alias_path = output / "survival_count_only.json"
    founder_path = output / "survival_by_founder.json"
    if alias_path.exists() or founder_path.exists():
        raise FileExistsError(f"Existing count-only comparison in {output}.")
    scores = _core.run(bank_path, weights_path, digest, output)
    alias, founders = _audit_aliases(output, count_control, scores, digest)
    for path, report in ((alias_path, alias), (founder_path, founders)):
        with path.open("x", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
    return scores


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", type=Path, default=HERE / "bank.json")
    parser.add_argument("--weights", type=Path, default=HERE / "learning_weights.json")
    parser.add_argument("--weights-sha256", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    run(args.bank, args.weights, args.weights_sha256, args.output_dir)


if __name__ == "__main__":
    main()
