"""Train the repaired device with the pinned original fitting driver."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

if __package__:
    from . import bank, device
else:
    import bank
    import device


HERE, LAWS = bank.HERE, bank.LAWS
CORE_FILES = ("bank.py", "device.py", "learning_train.py", "learning_design.md")
_core = bank.load_original("learning_train.py", {"bank": bank, "device": device})
SCHEMA, CATALOGUE, SCORE_RULE = _core.SCHEMA, _core.CATALOGUE, _core.SCORE_RULE


def _source_hashes():
    for filename in bank.ORIGINAL_SHA256:
        bank._locked_bytes(filename)
    return {name: sha256((HERE / name).read_bytes()).hexdigest() for name in CORE_FILES}


def _winning_selector(scores):
    highest = max(scores)
    return scores.index(highest) + 1 if highest > 0 else 0


def count_controls(weights, ledger, digest):
    """Count strict-vote positions without using subsequent receipt labels."""
    by_law = {}
    for law in LAWS:
        positions, packets = [], []
        for packet in ledger["packets_by_law"][law]:
            positions.extend([row["seed"], row["tape"], row["turn"]]
                             for row in packet["ordered_evidence"] if row["votes"][0])
            trained = packet["trained"]
            scores = [min(7, len(positions)), *trained["scores"][1:]]
            selector = _winning_selector(scores)
            packets.append({
                "replicate": packet["replicate"], "opportunities": len(positions),
                "count_credit": scores[0], "genuine_strict_credit": trained["scores"][0],
                "reconstructed_scores": scores, "reconstructed_selector": selector,
                "genuine_selector": trained["selector"], "credit_matches": scores[0] == trained["scores"][0],
                "selector_matches": selector == trained["selector"],
            })
        final = weights["policies"][law]["trained"]
        if final["scores"][0] != packets[-1]["genuine_strict_credit"] or final["selector"] != packets[-1]["genuine_selector"]:
            raise RuntimeError("The final training packet does not match the locked physical state.")
        selector = packets[-1]["reconstructed_selector"]
        replacement = "learned" if selector == final["selector"] else {0: "zero", 1: "strict"}.get(selector)
        encoded = json.dumps(positions, separators=(",", ":"), ensure_ascii=True).encode("ascii")
        by_law[law] = {
            "opportunities": len(positions), "ordered_position_sha256": sha256(encoded).hexdigest(),
            "count_credit": min(7, len(positions)), "genuine_strict_credit": final["scores"][0],
            "genuine_selector": final["selector"], "ordered_positions": positions, "packets": packets,
            "credit_matches_all_packets": all(row["credit_matches"] for row in packets),
            "selector_matches_all_packets": all(row["selector_matches"] for row in packets),
            "aliases": {"replace_strict_credit": replacement,
                        "first_opportunity": "strict" if positions else "zero",
                        "seven_opportunities": "strict" if len(positions) >= 7 else "zero"},
        }
    return {"schema": "return-cue-count-controls-v1", "weights_sha256": digest,
            "position_fields": ["seed", "tape", "turn"], "by_law": by_law}


def load_frozen_weights(path, digest):
    path = Path(path)
    record = _core.load_frozen_weights(path, digest)
    lock = json.loads(path.with_name("learning_source_lock.json").read_bytes())
    _, bank_digest = bank.load_bank(HERE / "bank.json")
    if lock != {"weights_sha256": digest, "bank_sha256": bank_digest,
                "original_sha256": bank.ORIGINAL_SHA256, "repair_sha256": _source_hashes()}:
        raise ValueError("The repaired study's bank or driver source fails its training lock.")
    if record["bank_sha256"] != bank_digest:
        raise ValueError("Weights belong to a different founder bank.")
    return record


def run(bank_path, output_dir, expected_device_sha256):
    output = Path(output_dir)
    sources = _source_hashes()
    if sources["device.py"] != expected_device_sha256:
        raise ValueError("The repaired device fails the prospectively pinned SHA-256.")
    if any((output / name).exists() for name in ("learning_count_only.json", "learning_source_lock.json")):
        raise FileExistsError(f"Repair training records already exist in {output}.")
    digest = _core.run(bank_path, output)
    if sources != _source_hashes():
        raise RuntimeError("A locked repair input changed during fitting.")
    path = output / "learning_weights.json"
    weights = _core.load_frozen_weights(path, digest)
    ledger = json.loads((output / "learning_training.json").read_bytes())
    _core._save(output / "learning_count_only.json", count_controls(weights, ledger, digest))
    _core._save(output / "learning_source_lock.json", {
        "weights_sha256": digest, "bank_sha256": weights["bank_sha256"],
        "original_sha256": bank.ORIGINAL_SHA256, "repair_sha256": sources,
    })
    load_frozen_weights(path, digest)
    return digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", type=Path, default=HERE / "bank.json")
    parser.add_argument("--device-sha256", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    run(args.bank, args.output_dir, args.device_sha256)


if __name__ == "__main__":
    main()
