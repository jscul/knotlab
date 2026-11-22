"""Run the four fixed readers on the fresh paired feeder survival sample."""

import argparse
from collections import Counter
import csv
from dataclasses import asdict
from itertools import islice
import json
from pathlib import Path
from random import Random
from statistics import fmean, median, quantiles
from time import perf_counter

from feeder_game import episode, sample_world
from history_reader import PublicHistoryReader
from keeper import KnotKeeper
from survival_sources import archived_excluded_keys, candidate_starts, derive_seed


LAWS = ("parity", "nae")
READERS = ("naive", "current", "history", "keeper")
CONTRASTS = (("history", "current"), ("keeper", "current"), ("keeper", "history"))
STARTS, TAPES, BOOTSTRAP_SAMPLES = 48, 4, 2000
CSV_FIELDS = (
    "candidate_index", "source_key", "seed", "replicate", "tape", "law", "reader",
    "first_funded", "growth_stop", "rations", "turns", "meals", "energy", "wasted", "reason",
    "turn_bound", "unsuccessful_eats", "passes_on_fresh_feeder", "refusals", "public_history_sha256",
)


class CurrentReader:
    def __init__(self, *, skip_after_eat):
        self.skip_after_eat = skip_after_eat

    def decide(self, observation):
        return int(observation.feeder and (not self.skip_after_eat or observation.previous != "eat"))

    def advance(self, _transition):
        pass


class KeeperReader:
    """Attach the lawful apparatus and connect its sole action bit to the game."""

    def __init__(self, law):
        self.keeper = KnotKeeper(law)

    @property
    def memory_word(self):
        return self.keeper.memory_word

    @property
    def action_word(self):
        return self.keeper.action_word

    def decide(self, observation):
        return self.keeper.before_decision(observation.feeder, len(observation.slots))

    def advance(self, transition):
        observed = transition.observation
        return self.keeper.after_turn(observed.feeder, len(observed.slots), observed.energy,
                                      transition.bit, transition.energy_after)


def make_reader(name, law):
    if name == "keeper":
        return KeeperReader(law)
    if name == "history":
        return PublicHistoryReader()
    if name in ("current", "naive"):
        return CurrentReader(skip_after_eat=name == "current")
    raise ValueError(f"Unknown feeder reader {name!r}")


def _score_rows(records):
    turns = [row["turns"] for row in records]
    return {
        "episodes": len(records), "mean_turns": fmean(turns), "median_turns": median(turns),
        "min_turns": min(turns), "max_turns": max(turns),
        "mean_meals": fmean(row["meals"] for row in records),
        "total_unsuccessful_eats": sum(row["unsuccessful_eats"] for row in records),
        "mean_unsuccessful_eats": fmean(row["unsuccessful_eats"] for row in records),
        "passes_on_fresh_feeder": sum(row["passes_on_fresh_feeder"] for row in records),
        "refusals": sum(row["refusals"] for row in records),
        "terminal_reasons": dict(Counter(row["reason"] for row in records)),
    }


def _win_tie_loss(differences):
    return {"wins": sum(value > 0 for value in differences), "ties": differences.count(0),
            "losses": sum(value < 0 for value in differences)}


def _effect(clusters, seed):
    means = [fmean(cluster) for cluster in clusters]
    rng = Random(seed)
    draws = [fmean(rng.choices(means, k=len(means))) for _ in range(BOOTSTRAP_SAMPLES)]
    cuts = quantiles(draws, n=40, method="inclusive")
    differences = [value for cluster in clusters for value in cluster]
    return {
        "paired_starts": len(clusters), "paired_episodes": len(differences),
        "sum_turn_difference": sum(differences), "mean_turn_difference": fmean(differences),
        "start_bootstrap_95_percent_interval": [cuts[0], cuts[-1]],
        "bootstrap_seed": seed, **_win_tie_loss(differences),
    }


def _summary(rows, starts):
    index = {(row["law"], row["reader"], row["source_key"], row["replicate"]): row for row in rows}
    if (len(index) != len(rows) or len(rows) != len(starts) * len(LAWS) * TAPES * len(READERS)
            or any(row["reason"] != "death" or row["energy"] != 0 for row in rows)):
        raise RuntimeError("The result ledger contains missing, duplicate or incomplete episodes.")
    by_law = {}
    for law in LAWS:
        contrasts = {}
        for left, right in CONTRASTS:
            clusters = [[index[law, left, start.source_key, rep]["turns"]
                         - index[law, right, start.source_key, rep]["turns"] for rep in range(TAPES)]
                        for start in starts]
            contrasts[f"{left}_minus_{right}"] = _effect(clusters, derive_seed("bootstrap", law, left, right))
        by_law[law] = {
            "readers": {name: _score_rows([r for r in rows if r["law"] == law and r["reader"] == name])
                        for name in READERS},
            "contrasts": contrasts,
        }
    between_laws = {}
    for name in READERS:
        pairs = [(index["parity", name, start.source_key, rep], index["nae", name, start.source_key, rep])
                 for start in starts for rep in range(TAPES)]
        differences = [right["turns"] - left["turns"] for left, right in pairs]
        between_laws[name] = {
            "same_public_histories": sum(left["public_history_sha256"] == right["public_history_sha256"]
                                         for left, right in pairs),
            "mean_nae_minus_parity_turns": fmean(differences), **_win_tie_loss(differences),
        }
    return by_law, between_laws


def run(output_dir):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    raw_path, score_path = output / "survival_episodes.csv", output / "survival_results.json"
    if raw_path.exists() or score_path.exists():
        raise FileExistsError(f"The specified destination already contains survival records: {output}")

    begin = perf_counter()
    starts = list(islice(candidate_starts("survival"), STARTS))
    if not starts:
        raise RuntimeError("The frozen survival fold contains no eligible starts.")
    print(f"Selected {len(starts)}/{STARTS} fresh founder structures.", flush=True)
    rows = []
    growth = {law: Counter(first_funded=0, stalls=0, closures=0, rations=0) for law in LAWS}
    identical_growth = 0
    for count, start in enumerate(starts, 1):
        worlds = {law: sample_world(start.seed, law, rounds=2) for law in LAWS}
        parity, nae = worlds["parity"], worlds["nae"]
        if parity.stages[0] != nae.stages[0] or any(w.source_key != start.source_key for w in worlds.values()):
            raise RuntimeError(f"Frozen founder pair differs at seed {start.seed}.")
        identical_growth += (parity.stages, parity.attempts, parity.births, parity.stop) == (
            nae.stages, nae.attempts, nae.births, nae.stop)
        for law, world in worlds.items():
            first_funded = bool(world.attempts[0].births)
            growth[law].update(first_funded=first_funded, stalls=world.stop == "stall",
                               closures=world.stop == "closed", rations=len(world.births))
            for replicate in range(TAPES):
                tape = derive_seed("tape", start.source_key, replicate)
                for name in READERS:
                    played = episode(world, make_reader(name, law), tape=tape)
                    rows.append({
                        **asdict(start), "law": law, "replicate": replicate, "tape": tape, "reader": name,
                        "first_funded": int(first_funded), "growth_stop": world.stop, "rations": len(world.births),
                        **{field: played[field] for field in CSV_FIELDS if field in played},
                    })
        if count % 8 == 0 or count == len(starts):
            print(f"Played all matched games for {count}/{len(starts)} founder structures.", flush=True)

    by_law, between_laws = _summary(rows, starts)
    with raw_path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    results = {
        "schema_version": 1, "split": "survival", "target_start_count": STARTS,
        "selected_start_count": len(starts), "excluded_archived_keys": len(archived_excluded_keys()),
        "starts": [asdict(start) for start in starts], "tapes_per_start": TAPES,
        "bootstrap_samples_per_contrast": BOOTSTRAP_SAMPLES, "episodes": len(rows),
        "censored_episodes": 0, "identical_growth_by_start_pair": identical_growth,
        "growth_by_law": {law: dict(growth[law]) for law in LAWS}, "by_law": by_law,
        "between_laws": between_laws, "elapsed_seconds": perf_counter() - begin,
    }
    with score_path.open("x", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"Saved {len(rows)} complete episodes in {output}.", flush=True)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    run(parser.parse_args().output_dir)


if __name__ == "__main__":
    main()
