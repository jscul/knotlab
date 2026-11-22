"""Verify the structural holdout and replay every saved evaluation game to death."""
from collections import Counter, defaultdict
import csv
from hashlib import sha256
import json
from pathlib import Path
from statistics import mean

from game import episode
from policies import get_policy, load_model
from verify_game import audit
from world import sample_world, source_key


HERE = Path(__file__).resolve().parent


def verify(directory):
    scores = json.loads((directory / "results.json").read_text())
    with (directory / "per_episode.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    model_file = directory / "model.json"
    assert scores["model_sha256"] == sha256(model_file.read_bytes()).hexdigest()
    model = load_model(model_file)
    starts = defaultdict(set)
    counts = Counter()
    choices = Counter()
    lifetimes = defaultdict(list)
    histories = defaultdict(dict)
    turns_verified = 0
    for row in rows:
        phase, law, bot = row["phase"], row["law"], row["policy"]
        seed, tape = int(row["seed"]), int(row["tape"])
        key = source_key(seed)
        assert key == row["source_key"]
        starts[phase].add(key)
        counts[phase] += 1
        assert int(row["energy"]) == 0 and row["reason"] == "death"
        assert int(row["turns"]) == 6 + 4 * int(row["meals"]) - int(row["wasted"])
        if phase == "train":
            continue
        world = sample_world(seed, law, rounds=2)
        policy = get_policy(bot, model if bot == "learner" else None)
        trial = episode(world, policy, tape=tape, sensor=bot in ("learner", "sensing"), trace=True)
        turns_verified += audit(trial)
        for field in ("turns", "meals", "energy", "wasted"):
            assert trial[field] == int(row[field])
        payload = json.dumps(trial["events"], sort_keys=True, separators=(",", ":")).encode("ascii")
        digest = sha256(payload).hexdigest()
        assert digest == row["history_sha256"]
        matched = histories[key, tape, bot]
        assert law not in matched
        matched[law] = digest
        lifetimes[law, bot].append(trial["turns"])
        if bot == "learner" and law == "parity":
            choices.update(("food" if event["food_before"] else "empty") + "_" + event["action"]
                           for event in trial["events"])
    assert counts == {"train": 3072, "evaluation": 2048}
    assert len(starts["train"]) == 128 and len(starts["evaluation"]) == 64
    excluded = {source_key(seed) for seed in range(100)} | {source_key(208304)}
    assert starts["train"].isdisjoint(starts["evaluation"])
    assert excluded.isdisjoint(starts["train"] | starts["evaluation"])
    assert len(histories) == 1024
    for pair in histories.values():
        assert pair["parity"] == pair["nae"]
    for (law, bot), values in lifetimes.items():
        assert len(values) == 256
        assert mean(values) == scores["evaluation"]["by_law"][law]["policies"][bot]["mean_turns"]
    return {"training_ledgers": counts["train"], "verified_evaluation_episodes": counts["evaluation"],
            "verified_evaluation_turns": turns_verified, "identical_between_law_pairs": len(histories),
            "structures": {phase: len(keys) for phase, keys in starts.items()},
            "learner_choices_across_256_parity_episodes": dict(choices)}


if __name__ == "__main__":
    print(json.dumps(verify(HERE), indent=2, sort_keys=True))
