"""Train and export physical feeder-cue selections on the frozen training bank."""

import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from random import Random
from time import perf_counter

from bank import HERE, LAWS, TAPES, Start, derive_seed, load_bank, movement_tape, sample_pair
import device
from feeder_game import CAPACITY, FeederGame, Observation


SCHEMA = "second-feeder-cue-weights-v1"
CATALOGUE = ("strict_return", "approach_feeder", "approach_menu", "approach_slot")
SCORE_RULE = {
    "eligibility": "actual current-only ON with at least one pre-action physical EMPTY vote",
    "voted_empty_charged_unpaid": 1, "voted_empty_charged_paid": -4,
    "abstention_or_unprobed": 0, "clamp": [-7, 7], "initial_scores": [0, 0, 0, 0],
    "initial_selector": 0, "selector": "highest strictly positive score in fixed detector order, else none",
}


@dataclass(frozen=True, slots=True)
class Probe:
    observation: Observation
    bit: int
    outgoing_slot: int | None
    energy_after: int
    votes: tuple[int, ...]

    @property
    def eligible(self):
        return bool(self.bit and any(self.votes))

    @property
    def paid(self):
        return bool(self.bit and self.energy_after > self.observation.energy - 1)


@dataclass(frozen=True, slots=True)
class TrainingEpisode:
    start: Start
    tape: int
    probes: tuple[Probe, ...]
    meals: int


def _check_credit(receipt, probe, paid):
    if tuple(receipt["votes"]) != probe.votes:
        raise RuntimeError("The post-action score report changed a pre-action physical vote.")
    credit = -4 if paid else 1
    expected = [max(-7, min(7, value + credit * vote * probe.bit))
                for value, vote in zip(receipt["before"]["scores"], probe.votes, strict=True)]
    highest = max(expected)
    selector = expected.index(highest) + 1 if highest > 0 else 0
    if receipt["after"]["scores"] != expected or receipt["after"]["selector"] != selector:
        raise RuntimeError("Physical score update disagrees with the frozen public credit rule.")
    if probe.eligible and bool(receipt["credit_paid"]) != paid:
        raise RuntimeError("Physical credit disagrees with the supplied energy comparison.")


def _play_training(world, start, tape, bot):
    game = FeederGame(world, tape=tape)
    bot.begin_episode(training=True)
    probes = []
    while not game.done:
        observation = game.observe()
        bit = bot.decide(observation)
        current = int(observation.feeder and observation.previous != "eat")
        votes = tuple(bot.candidate_votes())
        if bit != current or (not bit and any(votes)):
            raise RuntimeError("The physical probe did not follow the fixed current-only budget.")
        transition = game.step(bit)
        probe = Probe(observation, bit, transition.outgoing_slot, transition.energy_after, votes)
        receipt = bot.after_turn(observation, bit, probe.outgoing_slot, probe.energy_after, training=True)
        _check_credit(receipt, probe, probe.paid)
        probes.append(probe)
    return TrainingEpisode(start, tape, tuple(probes), game.snapshot()["meals"])


def _permuted_credit(law, replicate, episodes, bot):
    actual = [probe.paid for ep in episodes for probe in ep.probes if probe.eligible]
    permutation_seed = derive_seed("feedback-permutation", law, replicate)
    shuffled = actual.copy()
    Random(permutation_seed).shuffle(shuffled)
    labels = iter(shuffled)
    evidence = []
    for ep in episodes:
        bot.begin_episode(training=True)
        for turn, probe in enumerate(ep.probes, 1):
            observation = probe.observation
            if bot.decide(observation) != probe.bit or tuple(bot.candidate_votes()) != probe.votes:
                raise RuntimeError("Permuted credit changed an action or candidate opportunity.")
            label = next(labels) if probe.eligible else probe.paid
            energy = min(CAPACITY, observation.energy + 3) if label else observation.energy - 1
            receipt = bot.after_turn(observation, probe.bit, probe.outgoing_slot, probe.energy_after,
                                     training=True, credit_energy_after=energy if probe.eligible else None)
            _check_credit(receipt, probe, label)
            if probe.eligible:
                evidence.append({
                    "seed": ep.start.seed, "tape": ep.tape, "turn": turn, "feeder": observation.feeder,
                    "previous": observation.previous, "slot_count": len(observation.slots), "action": probe.bit,
                    "energy_before": observation.energy, "energy_after": probe.energy_after,
                    "paid": probe.paid, "votes": list(probe.votes),
                    "permuted_paid": label, "permuted_credit_energy_after": energy,
                })
    if next(labels, None) is not None:
        raise RuntimeError("A shuffled credit receipt was left unassigned.")
    return {
        "permutation_seed": permutation_seed, "opportunities": len(actual), "paid": sum(actual),
        "permuted_paid": sum(shuffled), "displaced": sum(a != b for a, b in zip(actual, shuffled, strict=True)),
        "ordered_evidence": evidence,
    }


def _stability(packets, condition):
    recent = [packet[condition] for packet in packets[-4:]]
    return {
        "packets": len(recent), "selector_constant": all(row["selector"] == recent[0]["selector"] for row in recent),
        "score_words_constant": all(row["score_words"] == recent[0]["score_words"] for row in recent),
    }


def load_frozen_weights(path, expected_sha256):
    raw = Path(path).read_bytes()
    if sha256(raw).hexdigest() != expected_sha256:
        raise ValueError("Weights fail the pinned SHA-256.")
    record = json.loads(raw)
    if (record["schema"] != SCHEMA or tuple(record["detector_order"]) != CATALOGUE
            or record["score_rule"] != SCORE_RULE
            or record["device_sha256"] != sha256(Path(device.__file__).read_bytes()).hexdigest()):
        raise ValueError("Weights differ from the frozen device or receipt rule.")
    return record


def _save(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")


def run(bank_path, output):
    begin = perf_counter()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    checkpoint = output / "learning_weights.json"
    ledger = output / "learning_training.json"
    if checkpoint.exists() or ledger.exists():
        raise FileExistsError(f"Training records already exist in {output}.")
    if tuple(device.CATALOGUE) != CATALOGUE:
        raise RuntimeError("Device catalogue differs from the frozen training priority.")
    banks, bank_digest = load_bank(bank_path)
    starts = banks["train"]
    if not starts:
        raise RuntimeError("The frozen training fold has no eligible founders.")

    actual = {law: device.LearnedKnotBot(law) for law in LAWS}
    permuted = {law: device.LearnedKnotBot(law) for law in LAWS}
    initial = {law: actual[law].export() for law in LAWS}
    packets = {law: [] for law in LAWS}
    worlds = {start.source_key: sample_pair(start, "train") for start in starts}
    for replicate in range(TAPES):
        order_seed = derive_seed("train-order", replicate)
        order = list(starts)
        Random(order_seed).shuffle(order)
        episodes = {law: [] for law in LAWS}
        for start in order:
            tape = movement_tape("train", start.source_key, replicate)
            for law in LAWS:
                ep = _play_training(worlds[start.source_key][law], start, tape, actual[law])
                episodes[law].append(ep)
        for law in LAWS:
            control = _permuted_credit(law, replicate, episodes[law], permuted[law])
            packets[law].append({
                "replicate": replicate, "order_seed": order_seed,
                "episodes": [{"seed": ep.start.seed, "tape": ep.tape, "turns": len(ep.probes), "meals": ep.meals}
                             for ep in episodes[law]],
                "trained": actual[law].export(), "feedback_permuted": permuted[law].export(), **control,
            })
        print(f"Training packet {replicate + 1}/{TAPES} complete under both laws.", flush=True)

    policies = {law: {"trained": actual[law].export(), "feedback_permuted": permuted[law].export(),
                      "zero": initial[law]} for law in LAWS}
    for law in LAWS:
        for state in policies[law].values():
            reconstructed = device.LearnedKnotBot.from_frozen(law, state).begin_episode()
            if reconstructed.export() != state:
                raise RuntimeError("The physical score words did not survive an episode reset.")
    weights = {
        "schema": SCHEMA, "bank_sha256": bank_digest,
        "device_sha256": sha256(Path(device.__file__).read_bytes()).hexdigest(),
        "detector_order": list(CATALOGUE), "score_rule": SCORE_RULE,
        "train_founders": [start.source_key for start in starts], "packets": TAPES,
        "games_per_law": len(starts) * TAPES, "policies": policies,
    }
    _save(checkpoint, weights)
    digest = sha256(checkpoint.read_bytes()).hexdigest()
    load_frozen_weights(checkpoint, digest)
    _save(ledger, {
        "schema": "second-feeder-cue-training-v1", "weights_sha256": digest, "bank_sha256": bank_digest,
        "games_per_law": len(starts) * TAPES, "packets_by_law": packets,
        "stability_last_four": {law: {name: _stability(packets[law], name)
                                       for name in ("trained", "feedback_permuted")} for law in LAWS},
        "elapsed_seconds": perf_counter() - begin,
    })
    print(f"Frozen train-only weights SHA-256 {digest}", flush=True)
    return digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", type=Path, default=HERE / "bank.json")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    run(args.bank, args.output_dir)


if __name__ == "__main__":
    main()
