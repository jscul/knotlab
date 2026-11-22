"""Evaluate pinned physical feeder-cue weights on the held-out survival bank."""

import argparse
from collections import Counter
import csv
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
from random import Random
from statistics import fmean, median, quantiles
from time import perf_counter

from bank import HERE, LAWS, TAPES, derive_seed, load_bank, movement_tape, sample_pair
import device
from feeder_game import FeederGame, episode
from learning_train import load_frozen_weights


READERS = ("current", "old", "learned", "zero", "strict", "feedback_permuted", "erased", "selector_permuted")
CONTROLS = tuple(name for name in READERS if name != "learned")
PRIMARY = ("old", "current")
BOOTSTRAP_SAMPLES = 2000
STOCK_COUNTS = ("on_full", "on_empty", "off_full", "off_empty")
IDENTITY = ("seed", "candidate_index", "source_key", "law", "replicate", "tape")
EPISODE_FIELDS = (*IDENTITY, "reader", "growth_stop", "first_funded", "rations", "turn_bound",
                  "turns", "meals", "energy", "wasted", "reason", "refusals", "unsuccessful_eats",
                  "passes_on_fresh_feeder", "public_history_sha256", *STOCK_COUNTS)
COMMON_FIELDS = (*IDENTITY, "turn", "energy", "previous", "slot_count", "stock", *READERS)


class _Current:
    def decide(self, observation):
        return int(observation.feeder and observation.previous != "eat")

    def advance(self, _transition):
        return None

    def verify_weights(self):
        return None


class _Old:
    def __init__(self, law):
        self.board = device.old.KnotKeeper(law)

    def decide(self, observation):
        return self.board.before_decision(observation.feeder, len(observation.slots))

    def advance(self, transition):
        obs = transition.observation
        return self.board.after_turn(obs.feeder, len(obs.slots), obs.energy, transition.bit,
                                     transition.energy_after)

    def verify_weights(self):
        return None


class _FrozenReader:
    def __init__(self, law, export, mode):
        self.board = device.LearnedKnotBot.from_frozen(law, export, mode=mode).begin_episode(training=False)
        self.fixed = self.board.export()

    @property
    def memory_word(self):
        return self.board.memory_word

    @property
    def action_word(self):
        return self.board.action_word

    def decide(self, observation):
        return self.board.decide(observation)

    def advance(self, transition):
        return self.board.after_turn(transition.observation, transition.bit, transition.outgoing_slot,
                                     transition.energy_after, training=False)

    def verify_weights(self):
        if self.fixed != self.board.export():
            raise RuntimeError("A held-out episode changed a frozen credit or selector mark.")


def make_reader(name, law, weights):
    if name == "current":
        return _Current()
    if name == "old":
        return _Old(law)
    record, mode = {
        "learned": ("trained", "learned"), "zero": ("zero", "zero"), "strict": ("trained", "strict_return"),
        "feedback_permuted": ("feedback_permuted", "learned"), "erased": ("trained", "erased"),
        "selector_permuted": ("trained", "permuted"),
    }[name]
    return _FrozenReader(law, weights["policies"][law][record], mode)


def _stock_cell(bit, stock):
    return ("on" if bit else "off") + ("_full" if stock else "_empty")


def _natural(world, tape, name, weights):
    reader = make_reader(name, world.law, weights)
    played = episode(world, reader, tape=tape, trace=True)
    reader.verify_weights()
    stock = Counter({key: 0 for key in STOCK_COUNTS})
    for recorded, private, apparatus in zip(played["public_history"], played["events"], played["apparatus"], strict=True):
        bit = recorded["bit"]
        if apparatus is not None and bit != int(apparatus["action_word"][-1]):
            raise RuntimeError("A played action differs from the physical readout.")
        if recorded["observation"]["feeder"]:
            stock[_stock_cell(bit, private["food_before"])] += 1
    if stock["on_full"] != played["meals"] or stock["off_full"] != played["passes_on_fresh_feeder"]:
        raise RuntimeError("Feeder visit counts disagree with the game's ledger.")
    return played, dict(stock)


def replay_survival(start, law, replicate, name, weights):
    """Reproduce one recorded natural episode with full public and spectator records."""
    world = sample_pair(start, "survival")[law]
    tape = movement_tape("survival", start.source_key, replicate)
    return _natural(world, tape, name, weights)[0]


def _common_path(world, tape, weights):
    game = FeederGame(world, tape=tape)
    readers = {name: make_reader(name, world.law, weights) for name in READERS}
    visits = []
    while not game.done:
        obs = game.observe()
        bits = {name: reader.decide(obs) for name, reader in readers.items()}
        transition = game.step(bits["current"])
        private = game.last_event
        if obs.feeder:
            visits.append({"turn": private["turn"], "energy": obs.energy, "previous": obs.previous,
                           "slot_count": len(obs.slots), "stock": int(private["food_before"]), **bits})
        for reader in readers.values():
            reader.advance(transition)
    for reader in readers.values():
        reader.verify_weights()
    return visits


def _paired(clusters, seed):
    means = [fmean(cluster) for cluster in clusters]
    rng = Random(seed)
    boot = [fmean(rng.choices(means, k=len(means))) for _ in range(BOOTSTRAP_SAMPLES)]
    cuts = quantiles(boot, n=40, method="inclusive")
    differences = [difference for cluster in clusters for difference in cluster]
    return {
        "paired_founders": len(clusters), "paired_tapes": len(differences),
        "mean_turn_difference": fmean(differences), "sum_turn_difference": sum(differences),
        "founder_bootstrap_95_percent_interval": [cuts[0], cuts[-1]], "bootstrap_seed": seed,
        "wins": sum(d > 0 for d in differences), "ties": differences.count(0),
        "losses": sum(d < 0 for d in differences),
    }


def _natural_scores(rows):
    turns = [row["turns"] for row in rows]
    return {
        "episodes": len(rows), "mean_turns": fmean(turns), "median_turns": median(turns),
        "mean_meals": fmean(row["meals"] for row in rows), "refusals": sum(row["refusals"] for row in rows),
        "mean_unsuccessful_eats": fmean(row["unsuccessful_eats"] for row in rows),
        "mean_passes_on_fresh_feeder": fmean(row["passes_on_fresh_feeder"] for row in rows),
        "natural_feeder_outcomes": {key: sum(row[key] for row in rows) for key in STOCK_COUNTS},
    }


def _common_scores(visits):
    decisions = {name: Counter({key: 0 for key in STOCK_COUNTS}) for name in READERS}
    changes = {name: Counter(agree=0, correct_enable=0, incorrect_enable=0,
                             correct_suppression=0, incorrect_suppression=0) for name in CONTROLS}
    for row in visits:
        stock = row["stock"]
        learned = row["learned"]
        for name, counts in decisions.items():
            counts[_stock_cell(row[name], stock)] += 1
        for name, counts in changes.items():
            if learned == row[name]:
                counts["agree"] += 1
            else:
                correctness = "correct" if learned == stock else "incorrect"
                change = "enable" if learned else "suppression"
                counts[f"{correctness}_{change}"] += 1
    return {"feeder_visits": len(visits), "decisions": {n: dict(c) for n, c in decisions.items()},
            "learned_change_from": {n: dict(c) for n, c in changes.items()}}


def _summarize(episodes, common, starts):
    records = {(r["law"], r["source_key"], r["replicate"], r["reader"]): r for r in episodes}
    if (len(records) != len(LAWS) * len(READERS) * len(starts) * TAPES
            or len(records) != len(episodes)
            or any(r["reason"] != "death" or r["energy"] != 0 for r in episodes)):
        raise RuntimeError("Survival ledger contains missing, duplicate or incomplete games.")

    def contrasts_for(law, other):
        return [[records[law, start.source_key, rep, "learned"]["turns"]
                 - records[law, start.source_key, rep, other]["turns"] for rep in range(TAPES)]
                for start in starts]

    by_law = {}
    for law in LAWS:
        by_law[law] = {
            "natural": {name: _natural_scores([r for r in episodes if r["law"] == law and r["reader"] == name])
                        for name in READERS},
            "learned_minus": {other: _paired(contrasts_for(law, other), derive_seed("survival-bootstrap", law, other))
                              for other in CONTROLS},
            "common_current_path": _common_scores([row for row in common if row["law"] == law]),
        }
    paired_laws = {}
    for other in CONTROLS:
        parity, nae = (contrasts_for(law, other) for law in LAWS)
        clusters = [[(a + b) / 2 for a, b in zip(p, n, strict=True)] for p, n in zip(parity, nae, strict=True)]
        paired_laws[other] = _paired(clusters, derive_seed("survival-bootstrap", "paired-laws", other))
    between_laws = {name: sum(records["parity", s.source_key, rep, name]["public_history_sha256"]
                              == records["nae", s.source_key, rep, name]["public_history_sha256"]
                              for s in starts for rep in range(TAPES)) for name in READERS}
    return by_law, paired_laws, between_laws


def _save_csv(path, fields, rows):
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run(bank_path, weights_path, expected_sha256, output):
    begin = perf_counter()
    weights = load_frozen_weights(weights_path, expected_sha256)
    banks, bank_digest = load_bank(bank_path)
    if weights["bank_sha256"] != bank_digest or weights["train_founders"] != [s.source_key for s in banks["train"]]:
        raise ValueError("The fitted selector belongs to another source split.")
    starts = banks["survival"]
    if not starts:
        raise RuntimeError("The frozen survival fold has no founders.")

    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    scores = output / "survival_results.json"
    raw = output / "survival_episodes.csv"
    common_raw = output / "survival_common_path.csv"
    if any(path.exists() for path in (scores, raw, common_raw)):
        raise FileExistsError(f"Survival artifacts already exist in {output}.")

    natural, common = [], []
    growth = {law: Counter(first_funded=0, stalls=0, closures=0, rations=0) for law in LAWS}
    identical_growth = 0
    for index, start in enumerate(starts, 1):
        worlds = sample_pair(start, "survival")
        p, n = (worlds[law] for law in LAWS)
        identical_growth += (p.stages, p.attempts, p.births, p.stop) == (n.stages, n.attempts, n.births, n.stop)
        for law, world in worlds.items():
            first_funded = bool(world.attempts[0].births)
            growth[law].update(first_funded=first_funded, stalls=world.stop == "stall",
                               closures=world.stop == "closed", rations=len(world.births))
            for replicate in range(TAPES):
                tape = movement_tape("survival", start.source_key, replicate)
                identity = {**asdict(start), "law": law, "replicate": replicate, "tape": tape}
                for name in READERS:
                    played, stock = _natural(world, tape, name, weights)
                    natural.append({**identity, "reader": name, "growth_stop": world.stop,
                                    "first_funded": int(first_funded), "rations": len(world.births),
                                    **{key: played[key] for key in EPISODE_FIELDS if key in played}, **stock})
                common.extend({**identity, **visit} for visit in _common_path(world, tape, weights))
        if index % 8 == 0 or index == len(starts):
            print(f"Completed all natural and common-path games for {index}/{len(starts)} founders.", flush=True)

    by_law, paired_laws, between_laws = _summarize(natural, common, starts)
    if sha256(Path(weights_path).read_bytes()).hexdigest() != expected_sha256:
        raise RuntimeError("The weights file changed during evaluation.")
    _save_csv(raw, EPISODE_FIELDS, natural)
    _save_csv(common_raw, COMMON_FIELDS, common)
    results = {
        "schema": "second-feeder-cue-survival-v1", "weights_sha256": expected_sha256, "bank_sha256": bank_digest,
        "frozen_words_unchanged": True, "founders": len(starts), "tapes_per_founder": TAPES,
        "bootstrap_draws": BOOTSTRAP_SAMPLES, "episodes": len(natural), "common_path_games": len(starts) * TAPES * len(LAWS),
        "common_feeder_visits": len(common), "identical_growth_in_law_pairs": identical_growth,
        "between_laws_identical_public_histories": between_laws, "censored": 0,
        "growth": {law: dict(tally) for law, tally in growth.items()}, "by_law": by_law,
        "descriptive_paired_law_average": paired_laws,
        "primary_improvement": all(by_law[law]["learned_minus"][control]["founder_bootstrap_95_percent_interval"][0] > 0
                                   for law in LAWS for control in PRIMARY),
        "elapsed_seconds": perf_counter() - begin,
    }
    with scores.open("x", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    print(f"Saved {len(natural)} complete survival games and {len(common)} common feeder decisions.", flush=True)
    return results


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
