"""Fit one learner on the frozen founder split, then run every held-out game to death."""

import argparse
from collections import Counter
from copy import copy
import csv
from dataclasses import asdict, dataclass
from hashlib import blake2s, sha256
from itertools import count
import json
from pathlib import Path
from random import Random
from statistics import fmean, median, quantiles
from time import perf_counter

import game
import policies
from world import sample_world, source_key


LAWS = ("parity", "nae")
ROUNDS = 2
ROOT_SEED = 20261121
SPECTATOR_START = 208304
DEVELOPMENT_SEEDS = range(100)
TRAIN_STARTS = 128
EVAL_STARTS = 64
SOURCE_LIMIT = 8192
TRAIN_PASSES = 12
EVAL_TAPES = 4
BOOTSTRAP_SAMPLES = 2000
CONTRASTS = (("learner", "sensing"), ("sensing", "blind"))
CSV_FIELDS = (
    "phase", "pass", "replicate", "candidate_index", "source_key", "seed", "law", "tape",
    "policy", "epsilon", "turns", "meals", "energy", "wasted", "reason", "turn_bound",
    "food_seen_turns", "sensing_action_agreement", "sensing_kind_agreement", "compared_actions",
    "history_sha256",
)


@dataclass(frozen=True, slots=True)
class Start:
    candidate_index: int
    source_key: str
    seed: int


def derive_seed(domain, *parts):
    payload = json.dumps([ROOT_SEED, domain, *parts], separators=(",", ":"),
                         sort_keys=True, ensure_ascii=True).encode("ascii")
    return int.from_bytes(blake2s(payload, digest_size=8, person=b"KRAT2026").digest(), "big")


def spectator_seed():
    """Find the first designated seed with a funded first attempt under both laws."""
    for seed in count(SPECTATOR_START):
        if all(sample_world(seed, law, rounds=1).births for law in LAWS):
            return seed


def select_starts(spectator_through):
    excluded = {source_key(seed) for seed in DEVELOPMENT_SEEDS}
    excluded.update(source_key(seed) for seed in range(SPECTATOR_START, spectator_through + 1))
    starts = {"train": [], "evaluation": []}
    targets = {"train": TRAIN_STARTS, "evaluation": EVAL_STARTS}
    counts = Counter(scanned=0, excluded=0, duplicates=0, after_fold_filled=0)
    seen = set()
    for index in range(SOURCE_LIMIT):
        counts["scanned"] += 1
        seed = derive_seed("source", index)
        key = source_key(seed)
        if key in excluded:
            counts["excluded"] += 1
            continue
        if key in seen:
            counts["duplicates"] += 1
            continue
        seen.add(key)
        fold = "evaluation" if derive_seed("partition", key) % 4 == 0 else "train"
        if len(starts[fold]) < targets[fold]:
            starts[fold].append(Start(index, key, seed))
        else:
            counts["after_fold_filled"] += 1
        if all(len(starts[fold]) == target for fold, target in targets.items()):
            break
    actual = {fold: len(bank) for fold, bank in starts.items()}
    return starts, {
        **counts, "targets": targets, "actual": actual, "excluded_keys": len(excluded),
        "development_seed_range": [DEVELOPMENT_SEEDS.start, DEVELOPMENT_SEEDS.stop - 1],
        "spectator_seed_range": [SPECTATOR_START, spectator_through],
        "candidate_limit": SOURCE_LIMIT, "targets_reached": actual == targets,
    }


def _world_pair(start):
    worlds = {law: sample_world(start.seed, law, rounds=ROUNDS) for law in LAWS}
    if any(world.source_key != start.source_key for world in worlds.values()):
        raise RuntimeError(f"Founder key changed for source seed {start.seed}.")
    if worlds["parity"].stages[0] != worlds["nae"].stages[0]:
        raise RuntimeError(f"Founders differ between laws for source seed {start.seed}.")
    return worlds


def _turn_bound(world):
    return game.INITIAL_ENERGY + game.RATION_GAIN * len(world.births)


def _fit(starts):
    cases = [(start, world) for start in starts for world in _world_pair(start).values()]
    total = TRAIN_PASSES * len(cases)
    learner = policies.QLearner()
    history = []
    for pass_number in range(TRAIN_PASSES):
        order = cases.copy()
        Random(derive_seed("train-order", pass_number)).shuffle(order)
        for start, world in order:
            fraction = len(history) / max(1, total - 1)
            epsilon = (1 - fraction) * policies.EPSILON_START + fraction * policies.EPSILON_END
            tape = derive_seed("train-tape", start.source_key, pass_number, world.law)
            current = game.Game(world, tape=tape)
            observation = current.observe()
            budget = _turn_bound(world)
            while not current.done:
                decision_rng, move_rng = game.action_rngs(tape, current.turns + 1)
                action = learner.choose(observation, decision_rng, move_rng, epsilon)
                event = current.step(action, detail=False)
                if current.turns > budget:
                    raise RuntimeError("Training exceeded the total available energy.")
                next_observation = None if event["terminal"] else current.observe()
                learner.update(observation, action, next_observation)
                observation = next_observation
            if current.turns != game.INITIAL_ENERGY + game.RATION_GAIN * current.meals - current.wasted:
                raise RuntimeError("Training lifetime disagrees with the energy ledger.")
            history.append({
                **asdict(start), "phase": "train", "pass": pass_number, "law": world.law,
                "tape": tape, "policy": "learner", "epsilon": epsilon, "turns": current.turns,
                "meals": current.meals, "energy": current.energy, "wasted": current.wasted,
                "reason": "death", "turn_bound": budget,
            })
        print(f"Training pass {pass_number + 1}/{TRAIN_PASSES} completed {len(history)}/{total} games.",
              flush=True)
    updates = sum(sum(visits) for visits in learner.visits.values())
    values_changed = any(values != policies.ZERO_VALUES for values in learner.values.values())
    if updates != sum(row["turns"] for row in history) or not values_changed:
        raise RuntimeError("The learner did not record one genuine update per completed turn.")
    return learner, history


def _history_digest(events):
    payload = json.dumps(events, separators=(",", ":"), sort_keys=True).encode("ascii")
    return sha256(payload).hexdigest()


def _evaluate(starts, model):
    controllers = {name: policies.get_policy(name, model) for name in policies.POLICY_NAMES}
    history = []
    world_agreement = Counter(founders=0, holdings_links=0, payments_grants=0, attempts=0, entire=0)
    growth_counts = {law: Counter(starts=0, first_funded=0, stalls=0, closures=0, rations=0) for law in LAWS}
    for index, start in enumerate(starts, 1):
        worlds = _world_pair(start)
        parity, nae = worlds["parity"], worlds["nae"]
        same_stages = parity.stages == nae.stages
        same_births = parity.births == nae.births
        same_attempts = parity.attempts == nae.attempts and parity.stop == nae.stop
        same_world = same_stages and same_births and same_attempts
        world_agreement.update(founders=1, holdings_links=same_stages, payments_grants=same_births,
                               attempts=same_attempts, entire=same_world)
        for law, world in worlds.items():
            growth_counts[law].update(starts=1, first_funded=bool(world.attempts[0].births),
                                      stalls=world.stop == "stall", closures=world.stop == "closed",
                                      rations=len(world.births))
        for replicate in range(EVAL_TAPES):
            tape = derive_seed("eval-tape", start.source_key, replicate)
            transcript_digests = {}
            for law, world in worlds.items():
                for name, controller in controllers.items():
                    agreement = Counter(sensing_action_agreement=0, sensing_kind_agreement=0, compared_actions=0)

                    def compare_sensing(observation, decision_rng, move_rng):
                        sensing_move_rng = copy(move_rng)
                        action = controller(observation, decision_rng, move_rng)
                        reference = controllers["sensing"](observation, decision_rng, sensing_move_rng)
                        same_kind = (action == policies.EAT) == (reference == policies.EAT)
                        agreement.update(sensing_action_agreement=action == reference,
                                         sensing_kind_agreement=same_kind, compared_actions=1)
                        return action

                    policy = compare_sensing if name == "learner" else controller
                    result = game.episode(world, policy, tape=tape, sensor=name in policies.SENSOR_POLICIES,
                                          trace=True)
                    digest = _history_digest(result["events"])
                    if same_world and name in transcript_digests and digest != transcript_digests[name]:
                        raise RuntimeError("Identical growth and action tapes produced different histories.")
                    transcript_digests[name] = digest
                    row = {
                        **asdict(start), "phase": "evaluation", "replicate": replicate, "law": law,
                        "tape": tape, "policy": name, "turn_bound": _turn_bound(world),
                        "food_seen_turns": sum(event["food_before"] for event in result["events"]),
                        "history_sha256": digest,
                        **{key: result[key] for key in ("turns", "meals", "energy", "wasted", "reason")},
                    }
                    if name == "learner":
                        row.update(agreement)
                    history.append(row)
        if index % 8 == 0 or index == len(starts):
            print(f"Evaluation completed all matched games for {index}/{len(starts)} starts.", flush=True)
    return history, dict(world_agreement), {law: dict(counts) for law, counts in growth_counts.items()}


def _scores(records):
    lifetimes = [row["turns"] for row in records]
    return {
        "episodes": len(records), "mean_turns": fmean(lifetimes), "median_turns": median(lifetimes),
        "min_turns": min(lifetimes), "max_turns": max(lifetimes),
        "mean_meals": fmean(row["meals"] for row in records),
        "death_turns_at_initial_energy": lifetimes.count(game.INITIAL_ENERGY),
        "death_turns_at_total_energy_bound": sum(row["turns"] == row["turn_bound"] for row in records),
        "episodes_with_food_at_cursor": sum(row["food_seen_turns"] > 0 for row in records),
        "episodes_without_a_meal": sum(row["meals"] == 0 for row in records),
        "terminal_reasons": dict(Counter(row["reason"] for row in records)),
    }


def _win_tie_loss(differences):
    return {"wins": sum(value > 0 for value in differences), "ties": differences.count(0),
            "losses": sum(value < 0 for value in differences)}


def _paired_effect(per_start, seed):
    start_means = [fmean(differences) for differences in per_start]
    rng = Random(seed)
    boot = [fmean(rng.choices(start_means, k=len(start_means))) for _ in range(BOOTSTRAP_SAMPLES)]
    cuts = quantiles(boot, n=40, method="inclusive")
    differences = [difference for cluster in per_start for difference in cluster]
    return {
        "paired_starts": len(per_start), "paired_episodes": len(differences),
        "mean_turn_difference": fmean(start_means),
        "start_bootstrap_95_percent_interval": [cuts[0], cuts[-1]],
        "bootstrap_seed": seed, **_win_tie_loss(differences),
    }


def _summarize(records, starts):
    paired = {(row["law"], row["policy"], row["source_key"], row["replicate"]): row for row in records}
    if len(paired) != len(records) or any(row["reason"] != "death" or row["energy"] != 0 for row in records):
        raise RuntimeError("Evaluation contains a duplicate or incomplete episode.")
    summaries = {}
    for law in LAWS:
        by_policy = {name: [row for row in records if row["law"] == law and row["policy"] == name]
                     for name in policies.POLICY_NAMES}
        contrasts = {}
        for left, right in CONTRASTS:
            name = f"{left}_minus_{right}"
            differences = [
                [paired[law, left, start.source_key, rep]["turns"] - paired[law, right, start.source_key, rep]["turns"]
                 for rep in range(EVAL_TAPES)] for start in starts
            ]
            contrasts[name] = _paired_effect(differences, derive_seed("bootstrap", law, name))
        learner = by_policy["learner"]
        compared = sum(row["compared_actions"] for row in learner)
        exact = sum(row["sensing_action_agreement"] for row in learner)
        kind = sum(row["sensing_kind_agreement"] for row in learner)
        summaries[law] = {
            "policies": {name: _scores(episodes) for name, episodes in by_policy.items()},
            "contrasts": contrasts,
            "learner_sensing_agreement": {
                "compared_actions": compared, "same_actions": exact, "same_action_kinds": kind,
                "action_agreement_fraction": exact / compared, "kind_agreement_fraction": kind / compared,
            },
        }
    between_laws = {}
    for name in policies.POLICY_NAMES:
        pairs = [(paired["parity", name, start.source_key, rep], paired["nae", name, start.source_key, rep])
                 for start in starts for rep in range(EVAL_TAPES)]
        differences = [right["turns"] - left["turns"] for left, right in pairs]
        between_laws[name] = {
            "mean_nae_minus_parity_turns": fmean(differences),
            "identical_event_histories": sum(a["history_sha256"] == b["history_sha256"] for a, b in pairs),
            **_win_tie_loss(differences),
        }
    return summaries, between_laws


def _save_json(path, data):
    temp = path.with_suffix(".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    temp.replace(path)


def run(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    checkpoint = output / "model.json"
    scores = output / "results.json"
    episode_csv = output / "per_episode.csv"
    if any(path.exists() for path in (checkpoint, scores, episode_csv)):
        raise FileExistsError(f"Previous study artifacts are present in {output}.")

    begin = perf_counter()
    through = spectator_seed()
    split, counts = select_starts(through)
    print(f"Founder split selected {counts['actual']['train']} training and {counts['actual']['evaluation']} "
          f"evaluation starts in {counts['scanned']} candidates.", flush=True)
    if not all(split.values()):
        raise RuntimeError(f"Both structural folds require starts. Actual and target counts: {counts!r}")

    learner, training = _fit(split["train"])
    training_config = {
        "root_seed": ROOT_SEED, "passes": TRAIN_PASSES, "growth_rounds": ROUNDS,
        "laws": list(LAWS), "episodes": len(training), "updates": sum(row["turns"] for row in training),
        "alpha_initial": policies.ALPHA_INITIAL, "alpha_visit_scale": policies.ALPHA_VISIT_SCALE,
        "alpha_power": policies.ALPHA_POWER, "discount": policies.DISCOUNT,
        "epsilon_start": policies.EPSILON_START, "epsilon_end": policies.EPSILON_END,
        "reward_per_completed_turn": 1, "terminal_bootstrap": False, "greedy_ties": "move_if_legal",
    }
    _save_json(checkpoint, {**learner.record(), "training": training_config,
                            "training_starts": [asdict(start) for start in split["train"]]})
    digest = sha256(checkpoint.read_bytes()).hexdigest()
    model = policies.load_model(checkpoint)
    if model != learner.values:
        raise RuntimeError("The saved Q values differ from the fitted values.")
    fit_done = perf_counter()

    evaluation, world_agreement, growth_counts = _evaluate(split["evaluation"], model)
    if digest != sha256(checkpoint.read_bytes()).hexdigest():
        raise RuntimeError("The checkpoint changed during evaluation.")
    by_law, between_laws = _summarize(evaluation, split["evaluation"])
    with episode_csv.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(training)
        writer.writerows(evaluation)

    results = {
        "schema_version": 1, "selection": counts, "training": training_config,
        "evaluation": {
            "episodes": len(evaluation), "tapes_per_start": EVAL_TAPES,
            "bootstrap_samples_per_contrast": BOOTSTRAP_SAMPLES, "censored_episodes": 0,
            "starts": [asdict(start) for start in split["evaluation"]], "by_law": by_law,
            "paired_world_agreement": world_agreement, "growth_by_law": growth_counts,
            "between_laws": between_laws,
        },
        "model_sha256": digest, "checkpoint_verified_unchanged": True,
        "seconds_to_frozen_checkpoint": fit_done - begin,
        "seconds_through_evaluation": perf_counter() - begin,
    }
    _save_json(scores, results)
    print(f"Saved the frozen model and {len(training) + len(evaluation)} complete games in {output}.",
          flush=True)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    run(args.output_dir)


if __name__ == "__main__":
    main()
