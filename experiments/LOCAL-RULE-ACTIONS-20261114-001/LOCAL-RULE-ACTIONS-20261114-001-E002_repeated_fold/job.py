"""Replay E001, then compare two views of its frozen Q table on longer chains.

The count view exposes preparations_left unchanged. The availability view maps
that field to 0 or 1; the environment still enforces the full remaining count.
No fitting occurs after the original 6,000 episodes. E001 remains unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import resource
import sys
import time
from collections import Counter
from dataclasses import replace
from functools import lru_cache
from itertools import product
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "LOCAL-RULE-ACTIONS-20261114-001-E001_local_policy" / "job.py"
SOURCE_SHA256 = "0368dbd271e2ca10e6fc979f5a5ffc84ecb93be45ae4dda06c54f2465c8f36a8"
SEEDS = (17, 31, 53)
# Frozen observed E001 outcomes, not values selected using the new evaluations.
EXPECTED_TRAINING = {
    17: ("a0b9ecaf09d8540a30881764f6c474b36a59e622b5843926ad4004da04c102b0", 10787),
    31: ("4e85898c841fa06148310e4c7c1a6accafc3f0ee20088b6d2ceb2978d31e1087", 10667),
    53: ("56e61be9c12e8f328eb88d6b9df2dcaac289e681b1967a123a8fd87c0868b42b", 10677),
}


@lru_cache(maxsize=1)
def source():
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise ValueError(f"E001 source changed: {digest}")
    name = "local_rule_actions_e001_frozen"
    spec = importlib.util.spec_from_file_location(name, SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def policy_observation(observation, view):
    if view == "count":
        return observation
    if view == "available":
        return observation | {"preparations_left": int(observation["preparations_left"] > 0)}
    raise ValueError(f"Unknown preparation view {view!r}")


def evaluate(config, length, policy, seed, view="count", fitted_keys=None):
    """Compact E001-equivalent evaluation with table-key coverage added."""
    base = source()
    episodes = []
    actions, fold_counts, key_visits = Counter(), Counter(), Counter()
    for phases, target in product(product(base.BITS, repeat=length), base.BITS):
        env = base.LocalRuleEnv(config, phases, target)
        # Exactly E001's coupled reset; no start index or hidden bit enters it.
        rng = random.Random(seed + 1_000_000)
        trace, folds = [], 0
        while True:
            actual_observation, legal = env.observe(), env.legal_actions()
            observation = policy_observation(actual_observation, view)
            key = base.observation_key(observation, legal)
            if fitted_keys is not None:
                key_visits[key] += 1
            action = policy(observation, legal, rng)
            step = {
                "visible_phases": observation["visible_phases"],
                "visible_path_ends": observation["visible_path_ends"],
                "environment_preparations_left": actual_observation["preparations_left"],
                "policy_preparations_left": observation["preparations_left"],
                "action": action,
            }
            if fitted_keys is not None:
                step["key_seen_during_fit"] = key in fitted_keys
            trace.append(step)
            actions[action] += 1
            folds += action.startswith("fuse:")
            _, _, done, info = env.step(action)
            if done:
                fold_counts[folds] += 1
                episodes.append({"phases": phases, "target_phase": target,
                                 "folds": folds, "trace": trace, **info})
                break
    correct = sum(episode["correct"] for episode in episodes)
    result = {
        "starts": len(episodes), "correct": correct,
        "success_rate": correct / len(episodes),
        "action_counts": dict(sorted(actions.items())),
        "fold_count_histogram": {str(k): v for k, v in sorted(fold_counts.items())},
        "episodes": episodes,
    }
    if fitted_keys is not None:
        absent = {key: visits for key, visits in key_visits.items() if key not in fitted_keys}
        result["key_coverage"] = {
            "key_visits": sum(key_visits.values()),
            "distinct_keys": len(key_visits),
            "absent_key_visits": sum(absent.values()),
            "distinct_absent_keys": len(absent),
            "absent_keys": [{"key": key, "visits": visits}
                            for key, visits in sorted(absent.items())],
        }
    return result


def cache_sizes():
    base = source()
    return {name: getattr(base, name).cache_info()._asdict()
            for name in ("projected_relation", "fuse", "flipped", "candidate_relation",
                         "relation_digest")}


def image_peak_resident_kib():
    """Linux image high-water; ru_maxrss may include the pre-exec process."""
    if sys.platform.startswith("linux"):
        for line in Path("/proc/self/status").read_text().splitlines():
            if line.startswith("VmHWM:"):
                return int(line.split()[1])
    return None


def run_seed(seed):
    if seed not in SEEDS:
        raise ValueError(f"Frozen seeds are {SEEDS}")
    started = time.perf_counter()
    base = source()
    config = base.Config(sight_radius=1, action_radius=1, preparation_budget=1,
                         train_length=3, train_episodes=6000)
    fit_started = time.perf_counter()
    learner, training = base.train(config, seed)
    fit_seconds = time.perf_counter() - fit_started
    digest, updates = learner.digest(), learner.updates
    if (digest, updates) != EXPECTED_TRAINING[seed]:
        raise ValueError(f"E001 fitted policy did not reproduce for seed {seed}")
    if training["observations_fitted"] != 16 or training["q_entries"] != 40:
        raise ValueError("E001 fitted table dimensions changed")
    fitted_keys = frozenset(learner.q)
    # Both readings must address exactly the same keys on every fitted state.
    if any(key[1] not in (0, 1) or key[:1] + (int(key[1] > 0),) + key[2:] != key
           for key in fitted_keys):
        raise ValueError("The availability view changed a training key")

    untrained = base.QLearner()
    untrained_digest = untrained.digest()
    cells = []
    evaluation_started = time.perf_counter()
    for length in (3, 4, 5):
        for budget in sorted({1, length - 2}):
            cell_config = replace(config, preparation_budget=budget)
            panels = {}
            models = (
                ("count_q", learner.act, "count", fitted_keys),
                ("available_q", learner.act, "available", fitted_keys),
                ("local_rule", base.local_policy, "count", None),
                ("random_legal", base.random_policy, "count", None),
                ("untrained_q", untrained.act, "count", frozenset()),
            )
            for name, policy, view, keys in models:
                panels[name] = evaluate(cell_config, length, policy, seed, view, keys)
                if learner.digest() != digest or learner.updates != updates:
                    raise ValueError("Assessment altered the fitted Q policy")
                if untrained.digest() != untrained_digest or untrained.updates:
                    raise ValueError("Assessment fitted the untrained control")
            if budget == 1 and panels["count_q"] != panels["available_q"]:
                raise ValueError("Views disagreed despite a zero-or-one count")
            # E001's untrained and random policies are the same random action
            # distribution. Common resets must produce the same exact trace.
            if [episode["trace"] for episode in panels["random_legal"]["episodes"]] != [
                    [{key: value for key, value in step.items() if key != "key_seen_during_fit"}
                     for step in episode["trace"]]
                    for episode in panels["untrained_q"]["episodes"]]:
                raise ValueError("Random/untrained controls lost E001's coupled reset")
            cells.append({"length": length, "preparation_budget": budget,
                          "policies": panels})
    evaluation_seconds = time.perf_counter() - evaluation_started
    checks_started = time.perf_counter()
    checks = base.semantic_checks((3, 4, 5))
    checks_seconds = time.perf_counter() - checks_started
    summary = [{"length": cell["length"], "preparation_budget": cell["preparation_budget"],
                "policies": {name: {key: panel[key] for key in ("correct", "starts", "success_rate")}
                             for name, panel in cell["policies"].items()}}
               for cell in cells]
    return {
        "seed": seed, "training": training,
        "e001_training_digest_and_updates_reproduced": True,
        "all_fitted_keys_equal_under_both_views": True,
        "one_preparation_views_agree": True,
        "frozen_q_sha256_after_assessment": learner.digest(),
        "frozen_q_updates_after_assessment": learner.updates,
        "fit_seconds": fit_seconds, "evaluation_seconds": evaluation_seconds,
        "semantic_checks_seconds": checks_seconds,
        "elapsed_seconds": time.perf_counter() - started,
        "process_image_peak_resident_kib_linux": image_peak_resident_kib(),
        "resource_high_water_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "source_sha256": SOURCE_SHA256,
        "job_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "cache_sizes": cache_sizes(), "semantic_checks": checks,
        "random_policy_exact_expected_success": 0.5,
        "summary": summary, "cells": cells,
    }


def setup(params):
    if params:
        raise ValueError("This frozen follow-up has no runner parameters")
    source()


def cases():
    for seed in SEEDS:
        yield f"seed-{seed}", {"seed": seed}


def run(case_id, payload):
    return run_seed(int(payload["seed"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, choices=SEEDS, default=17)
    parser.add_argument("--smoke", action="store_true",
                        help="run the exact replay but print only its compact verification")
    args = parser.parse_args()
    result = run_seed(args.seed)
    if args.smoke:
        result = {key: value for key, value in result.items() if key != "cells"}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
