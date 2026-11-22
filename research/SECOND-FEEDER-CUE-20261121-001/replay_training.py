"""Rescore the sealed training receipts and replay one training episode per law."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from random import Random

from replay_game import CAPACITY, RATION_GAIN, require, take_turn
from replay_state import DETECTORS, PublicMemory, current_choice, empty_votes, one_hot, selected_from_score

from bank import derive_seed, load_bank, movement_tape, sample_pair
from device import LearnedKnotBot
import device
from feeder_game import FeederGame


HERE = Path(__file__).resolve().parent
LAWS = ("parity", "nae")
CUES = ("none", *DETECTORS)


def decoded_score(scores):
    selector = CUES.index(selected_from_score(dict(zip(DETECTORS, scores, strict=True))))
    return {"scores": scores, "score_words": [one_hot(score + 7, 15) for score in scores],
            "selector": selector, "selector_word": one_hot(selector, len(CUES))}


def check_score(scores, export, description):
    require(all(export[name] == expected for name, expected in decoded_score(scores).items()),
            f"Physical credit words disagree with {description}")


def apply_credit(scores, votes, paid):
    delta = -4 if paid else 1
    return [max(-7, min(7, score + vote * delta)) for score, vote in zip(scores, votes, strict=True)]


def legal_payment(row):
    before, after = row["energy_before"], row["energy_after"]
    require(type(before) is int and 1 <= before <= CAPACITY, "Invalid public energy before training receipt")
    require(after in (before - 1, min(CAPACITY, before - 1 + RATION_GAIN)), "Impossible charged ON energy")
    paid = after > before - 1
    require(row["paid"] is paid, "Stock label did not follow the actual public energy receipt")
    return paid


def packet_order(packet, starts, replicate):
    expected_seed = derive_seed("train-order", replicate)
    require(packet["replicate"] == replicate and packet["order_seed"] == expected_seed,
            "Training packet order key differs from the frozen recipe")
    ordered = list(starts)
    Random(expected_seed).shuffle(ordered)
    tapes = [movement_tape("train", start.source_key, replicate) for start in ordered]
    require([(ep["seed"], ep["tape"]) for ep in packet["episodes"]] == list(zip((s.seed for s in ordered), tapes)),
            "A training episode is missing, reordered, or outside the training bank")
    return {(ep["seed"], ep["tape"]): (index, ep["turns"])
            for index, ep in enumerate(packet["episodes"])}


def check_feedback(packet, law, replicate, timeline):
    ordered = packet["ordered_evidence"]
    positions = []
    for row in ordered:
        index, length = timeline[(row["seed"], row["tape"])]
        require(1 <= row["turn"] <= length and row["action"] == 1 and row["feeder"] and
                row["previous"] != "eat" and row["slot_count"] > 0,
                "Score input was outside a charged current-only ON opportunity")
        votes = row["votes"]
        require(len(votes) == len(DETECTORS) and set(votes) <= {0, 1} and any(votes),
                "Training receipt does not contain the four pre-action candidate marks")
        positions.append((index, row["turn"]))
    require(positions == sorted(set(positions)), "Training credit rows are duplicated or out of action order")
    paid = [legal_payment(row) for row in ordered]
    shuffled = paid.copy()
    seed = derive_seed("feedback-permutation", law, replicate)
    Random(seed).shuffle(shuffled)
    require(seed == packet["permutation_seed"] and shuffled == [row["permuted_paid"] for row in ordered],
            "Feedback re-pairing differs from the frozen law and packet tape")
    require((len(paid), sum(paid), sum(shuffled), sum(x != y for x, y in zip(paid, shuffled))) ==
            tuple(packet[k] for k in ("opportunities", "paid", "permuted_paid", "displaced")),
            "Training packet summary differs from its ordered receipts")
    for row, label in zip(ordered, shuffled, strict=True):
        before = row["energy_before"]
        credit = min(CAPACITY, before - 1 + RATION_GAIN * label)
        require(row["permuted_credit_energy_after"] == credit, "Permuted credit energy is wrong")
    return zip(ordered, paid, shuffled, strict=True)


def sampled_training_episode(law, start, tape, expected_rows):
    """Match one initial eligible training episode to live public game receipts."""
    world = sample_pair(start, "train")[law]
    game = FeederGame(world, tape=tape)
    boards = [LearnedKnotBot(law).begin_episode(training=True) for _ in range(2)]
    scores = [[0] * len(DETECTORS) for _ in boards]
    reference = PublicMemory()
    selected = {row["turn"]: row for row in expected_rows}
    seen = 0
    while not game.done:
        observation = game.observe()
        bit = current_choice(observation)
        votes = tuple(map(int, empty_votes(observation, reference.words()).values()))
        for bot in boards:
            require(bot.decide(observation) == bit and bot.candidate_votes() == votes,
                    f"Training action or offered detectors differ on a sampled {law} receipt")
        row = take_turn(game, world, bit)
        receipt = row.receipt
        turn = row.event["turn"]
        evidence = selected.get(turn)
        require(bool(bit and any(votes)) == bool(evidence), f"Wrong eligibility on sampled {law} turn {turn}")
        actual_paid = receipt.energy_after > observation.energy - 1
        if evidence:
            details = ((observation.energy, receipt.energy_after, list(votes), actual_paid),
                       tuple(evidence[key] for key in ("energy_before", "energy_after", "votes", "paid")))
            require(details[0] == details[1], f"Sampled {law} credits did not come from the actual charged action")
            seen += 1
        for index, board in enumerate(boards):
            kwargs = {} if not (index and evidence) else {"credit_energy_after": evidence["permuted_credit_energy_after"]}
            report = board.after_turn(observation, bit, receipt.outgoing_slot, receipt.energy_after,
                                      training=True, **kwargs)
            paid = evidence["permuted_paid"] if index and evidence else actual_paid
            if bit:
                scores[index] = apply_credit(scores[index], votes, paid)
            check_score(scores[index], report["after"], f"sampled {law} training turn {turn}")
        reference = reference.advance(receipt)
    require(seen == len(expected_rows), f"Missing eligible {law} rows in the replayed training episode")
    return seen


def audit_training(weights, ledger, train_starts):
    require(tuple(weights["detector_order"]) == DETECTORS, "The learned detector catalogue changed after freeze")
    require(weights["device_sha256"] == sha256(Path(device.__file__).read_bytes()).hexdigest(),
            "The sealed policy names a different device implementation")
    require(weights["train_founders"] == [start.source_key for start in train_starts],
            "Weights were not fitted on the declared training keys")
    results = {}
    for law in LAWS:
        scores = [0] * len(DETECTORS)
        shuffled_scores = scores.copy()
        packets = ledger["packets_by_law"][law]
        n_games = len(train_starts) * len(packets)
        require(len(packets) == weights["packets"] and n_games == weights["games_per_law"] == ledger["games_per_law"],
                f"Training game count changed under {law}")
        sample = None
        changed = opportunities = 0
        for replicate, packet in enumerate(packets):
            timeline = packet_order(packet, train_starts, replicate)
            for row, paid, shuffled in check_feedback(packet, law, replicate, timeline):
                if sample is None:
                    source = next(start for start in train_starts if start.seed == row["seed"])
                    evidence = [r for r in packet["ordered_evidence"] if r["seed"] == row["seed"] and r["tape"] == row["tape"]]
                    sample = sampled_training_episode(law, source, row["tape"], evidence)
                next_scores = apply_credit(scores, row["votes"], paid)
                changed += next_scores != scores
                scores = next_scores
                shuffled_scores = apply_credit(shuffled_scores, row["votes"], shuffled)
                opportunities += 1
            check_score(scores, packet["trained"], f"actual {law} packet {replicate + 1}")
            check_score(shuffled_scores, packet["feedback_permuted"], f"permuted {law} packet {replicate + 1}")

        model = weights["policies"][law]
        check_score([0] * len(DETECTORS), model["zero"], f"initial {law} words")
        check_score(scores, model["trained"], f"last {law} training packet")
        check_score(shuffled_scores, model["feedback_permuted"], f"last {law} permuted packet")
        results[law] = {"games": n_games, "opportunities": opportunities, "score_changes": changed,
                        "physical_sample_opportunities": sample or 0, "trained_scores": scores,
                        "trained_selector": CUES[model["trained"]["selector"]],
                        "permuted_scores": shuffled_scores,
                        "permuted_selector": CUES[model["feedback_permuted"]["selector"]]}
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training", type=Path, default=HERE / "learning_training.json")
    parser.add_argument("--weights", type=Path, default=HERE / "learning_weights.json")
    parser.add_argument("--bank", type=Path, default=HERE / "bank.json")
    args = parser.parse_args()
    try:
        raw = args.weights.read_bytes()
        weights, ledger = json.loads(raw), json.loads(args.training.read_bytes())
        folds, bank_digest = load_bank(args.bank)
        require(ledger["weights_sha256"] == sha256(raw).hexdigest(), "Receipt ledger names different fitted weights")
        require(ledger["bank_sha256"] == weights["bank_sha256"] == bank_digest, "Training bank hash differs")
        result = audit_training(weights, ledger, folds["train"])
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
