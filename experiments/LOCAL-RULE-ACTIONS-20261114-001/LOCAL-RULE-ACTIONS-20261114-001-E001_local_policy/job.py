"""Local phase edits and exact relation composition, with frozen-policy assessment.

The environment is supplied. Its radii count shared-rule steps in the current
chain; these counts are not a claim about native distance. Only the evaluator
sees the entire allowed boundary relation. The learner receives local phases,
local unsigned boundary information, the target phase, and legal actions.

Shared runner: setup(params), cases(), run(case_id, payload).
Direct smoke: python3 -B job.py --smoke
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import time
from collections import Counter
from dataclasses import dataclass, field, replace
from functools import lru_cache
from itertools import product
from pathlib import Path


BITS = (0, 1)
KEEP, FLIP = "keep", "flip"
PARITY_TABLES = ("01101001", "10010110")


@dataclass(frozen=True)
class Config:
    sight_radius: int = 1
    action_radius: int = 1
    preparation_budget: int = 1
    train_length: int = 3
    eval_lengths: tuple[int, ...] = (3, 4)
    train_episodes: int = 6000
    seeds: tuple[int, ...] = (17, 31, 53)
    alpha: float = 0.15
    gamma: float = 1.0
    epsilon_start: float = 0.4
    epsilon_end: float = 0.05

    def __post_init__(self):
        if min(self.sight_radius, self.action_radius, self.preparation_budget) < 0:
            raise ValueError("Radii and preparation budget must be nonnegative")
        if not self.eval_lengths or not self.seeds or self.train_episodes < 1:
            raise ValueError("An evaluation length, seed and training update are required")
        if any(not 1 <= n <= 6 for n in (self.train_length, *self.eval_lengths)):
            raise ValueError("This exact finite probe supports chain lengths 1 through 6")
        if not 0 < self.alpha <= 1 or not 0 <= self.gamma <= 1:
            raise ValueError("Invalid Q-learning parameters")
        if not 0 <= self.epsilon_end <= self.epsilon_start <= 1:
            raise ValueError("Invalid epsilon schedule")


@dataclass(frozen=True)
class Rule:
    """An allowed relation, with incoming first and outgoing last."""

    support: tuple[int, ...]
    phase: int
    rows: tuple[tuple[int, ...], ...] = field(repr=False)


@lru_cache(maxsize=None)
def original_rule(index, phase):
    support = tuple(range(3 * index, 3 * index + 4))
    # Read a three-input truth table; do not compute the whole-chain phase.
    rows = tuple(inputs + (int(PARITY_TABLES[phase][4 * inputs[0] + 2 * inputs[1]
                                                 + inputs[2]]),)
                 for inputs in product(BITS, repeat=3))
    return Rule(support, phase, rows)


def initial_rules(phases):
    return tuple(original_rule(i, phase) for i, phase in enumerate(phases))


def boundary_variables(length):
    return (0, *(j for i in range(length) for j in (3 * i + 1, 3 * i + 2)),
            3 * length)


def joined_assignments(rules):
    """Small relational joins, independent of any whole-chain XOR shortcut."""
    assignments = [dict()]
    for rule in rules:
        local = [dict(zip(rule.support, row, strict=True)) for row in rule.rows]
        joined = []
        for old in assignments:
            for new in local:
                if all(key not in old or old[key] == value for key, value in new.items()):
                    joined.append(old | new)
        assignments = joined
    return assignments


@lru_cache(maxsize=None)
def projected_relation(rules, boundary):
    """Existentially forget all variables outside the declared boundary."""
    return frozenset(tuple(row[v] for v in boundary) for row in joined_assignments(rules))


@lru_cache(maxsize=None)
def fuse(left, right):
    shared = set(left.support) & set(right.support)
    if shared != {left.support[-1]} or right.support[0] != left.support[-1]:
        raise ValueError("Fusion requires exactly the adjacent shared distinction")
    retained = left.support[:-1] + right.support[1:]
    rows = tuple(sorted(projected_relation((left, right), retained)))
    phases = {sum(row) % 2 for row in rows}
    if len(phases) != 1 or len(rows) != 2 ** (len(retained) - 1):
        raise ValueError("Exact fusion was not a complete signed parity relation")
    return Rule(retained, phases.pop(), rows)


@lru_cache(maxsize=None)
def flipped(rule):
    rows = tuple(sorted(row[:-1] + (1 - row[-1],) for row in rule.rows))
    return Rule(rule.support, 1 - rule.phase, rows)


@lru_cache(maxsize=None)
def candidate_relation(length, phase):
    # The supplied candidate is a full relation on the external input/output
    # boundary, rather than a label on one sampled input.
    return frozenset(inputs + ((sum(inputs) + phase) % 2,)
                     for inputs in product(BITS, repeat=2 * length + 1))


@lru_cache(maxsize=None)
def relation_digest(relation):
    encoded = "|".join("".join(map(str, row)) for row in sorted(relation))
    return hashlib.sha256(encoded.encode()).hexdigest()


class LocalRuleEnv:
    def __init__(self, config, phases, target):
        self.config = config
        self.length = len(phases)  # Evaluator only; never an observation field.
        if not phases or any(phase not in BITS for phase in (*phases, target)):
            raise ValueError("Binary signs and target are required")
        self.rules = initial_rules(tuple(phases))
        self.target = target
        self.preparations_left = config.preparation_budget
        self.done = False

    def observe(self):
        count = self.config.sight_radius + 1
        return {
            "target_phase": self.target,
            "preparations_left": self.preparations_left,
            "visible_phases": tuple(rule.phase for rule in self.rules[:count]),
            "visible_path_ends": len(self.rules) <= count,
        }

    def legal_actions(self):
        actions = [KEEP, FLIP]
        if self.preparations_left:
            # Pair i,i+1 is allowed exactly when both rules are within a hops
            # of the first current rule. Legality exposes no sign.
            actions += [f"fuse:{i}"
                        for i in range(min(self.config.action_radius, len(self.rules) - 1))]
        return tuple(actions)

    def step(self, action):
        if self.done or action not in self.legal_actions():
            raise ValueError(f"Illegal action {action!r}")
        if action.startswith("fuse:"):
            index = int(action.split(":")[1])
            combined = fuse(self.rules[index], self.rules[index + 1])
            self.rules = self.rules[:index] + (combined,) + self.rules[index + 2:]
            self.preparations_left -= 1
            return self.observe(), 0.0, False, {}
        if action == FLIP:
            self.rules = (flipped(self.rules[0]),) + self.rules[1:]
        actual = projected_relation(self.rules, boundary_variables(self.length))
        expected = candidate_relation(self.length, self.target)
        self.done = True
        correct = actual == expected
        return self.observe(), float(correct), True, {
            "correct": correct,
            "allowed_boundary_states": len(actual),
            "relation_sha256": relation_digest(actual),
        }


def observation_key(observation, legal):
    return (observation["target_phase"], observation["preparations_left"],
            observation["visible_phases"], observation["visible_path_ends"], legal)


class QLearner:
    def __init__(self):
        self.q = {}
        self.updates = 0

    def act(self, observation, legal, rng, epsilon=0.0):
        if epsilon > 0 and rng.random() < epsilon:
            return rng.choice(legal)
        values = self.q.get(observation_key(observation, legal), {})
        maximum = max(values.get(action, 0.0) for action in legal)
        tied = [action for action in legal if abs(values.get(action, 0.0) - maximum) <= 1e-12]
        return rng.choice(tied)

    def update(self, observation, legal, action, reward, next_observation, next_legal,
               done, config):
        key = observation_key(observation, legal)
        values = self.q.setdefault(key, {})
        future = self.q.get(observation_key(next_observation, next_legal), {})
        continuation = 0.0 if done else max(future.get(a, 0.0) for a in next_legal)
        previous = values.get(action, 0.0)
        values[action] = previous + config.alpha * (reward + config.gamma * continuation - previous)
        if not math.isfinite(values[action]):
            raise ValueError("Nonfinite Q value")
        self.updates += 1

    def digest(self):
        rows = [[key, sorted(values.items())] for key, values in sorted(self.q.items())]
        return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


def train(config, seed):
    learner = QLearner()
    sample_rng = random.Random(seed)
    action_rng = random.Random(seed + 100_000)
    rewards = []
    action_counts = Counter()
    initial_digest = learner.digest()
    for episode in range(config.train_episodes):
        phases = tuple(sample_rng.randrange(2) for _ in range(config.train_length))
        target = sample_rng.randrange(2)
        env = LocalRuleEnv(config, phases, target)
        epsilon = config.epsilon_start + (config.epsilon_end - config.epsilon_start) * (
            episode / max(1, config.train_episodes - 1))
        while True:
            observation, legal = env.observe(), env.legal_actions()
            action = learner.act(observation, legal, action_rng, epsilon)
            following, reward, done, _ = env.step(action)
            learner.update(observation, legal, action, reward, following, env.legal_actions(),
                           done, config)
            action_counts[action] += 1
            if done:
                rewards.append(reward)
                break
    if learner.digest() == initial_digest or not learner.updates:
        raise ValueError("Training did not change the initialized Q table")
    return learner, {
        "episodes": len(rewards), "q_updates": learner.updates,
        "observations_fitted": len(learner.q),
        "q_entries": sum(len(values) for values in learner.q.values()),
        "initial_q_sha256": initial_digest, "trained_q_sha256": learner.digest(),
        "mean_reward_last_100": sum(rewards[-100:]) / len(rewards[-100:]),
        "action_counts": dict(sorted(action_counts.items())),
    }


def local_policy(observation, legal, rng):
    """Task-aware control using only the public observation and action labels."""
    if not observation["visible_path_ends"]:
        fusions = [action for action in legal if action.startswith("fuse:")]
        if fusions:
            # At a fixed end, the first adjacent pair exposes one additional
            # original sign to the visible portion after contraction.
            return fusions[0]
    # If a sign remains hidden this is a deterministic guess (unknown XOR=0).
    # Exhausting all hidden sign assignments makes that guess correct in half.
    observed_phase = sum(observation["visible_phases"]) % 2
    return KEEP if observed_phase == observation["target_phase"] else FLIP


def random_policy(observation, legal, rng):
    return rng.choice(legal)


def evaluate(config, length, policy, seed):
    rows = []
    action_counts = Counter()
    for phases, target in (
            (phases, target) for phases in product(BITS, repeat=length) for target in BITS):
        # Independent episode resets; policy fitting is absent from this path.
        # Couple the random stream across all starts: indistinguishable local
        # histories receive identical random choices. No hidden task index is
        # passed even indirectly through an episode-specific random seed.
        rng = random.Random(seed)
        env = LocalRuleEnv(config, phases, target)
        trace = []
        while True:
            observation, legal = env.observe(), env.legal_actions()
            action = policy(observation, legal, rng)
            trace.append({"observation": observation, "legal": legal, "action": action})
            action_counts[action] += 1
            _, _, done, info = env.step(action)
            if done:
                rows.append({"phases": phases, "target_phase": target,
                             "trace": trace, **info})
                break
    correct = sum(row["correct"] for row in rows)
    return {"length": length, "starts": len(rows), "correct": correct,
            "success_rate": correct / len(rows),
            "action_counts": dict(sorted(action_counts.items())), "episodes": rows}


def hidden_sign_control(config, length):
    if config.sight_radius >= length - 1:
        return {"length": length, "initial_hidden_sign": False}
    first = (0,) * length
    second = first[:-1] + (1,)
    environments = [LocalRuleEnv(config, phases, 0) for phases in (first, second)]
    traces = [[], []]
    for env, trace in zip(environments, traces, strict=True):
        while True:
            trace.append(env.observe())
            fusions = [action for action in env.legal_actions() if action.startswith("fuse:")]
            if not fusions:
                break
            env.step(fusions[0])
    relations = [projected_relation(env.rules, boundary_variables(length))
                 for env in environments]
    opposite = [relations[i] == candidate_relation(length, 0) for i in range(2)]
    if relations[0] & relations[1] or opposite != [True, False]:
        raise ValueError("Hidden-sign control failed to reverse the correct action")
    return {"length": length, "initial_hidden_sign": True,
            "initial_observation_identical": traces[0][0] == traces[1][0],
            "after_available_fusions_observation_identical": traces[0][-1] == traces[1][-1],
            "correct_terminal_actions": [KEEP, FLIP],
            "boundary_relations_disjoint": True, "observation_traces": traces}


@lru_cache(maxsize=None)
def semantic_checks(lengths=(3, 4)):
    phase_cases = fusion_cases = 0
    for length in lengths:
        boundary = boundary_variables(length)
        for phases in product(BITS, repeat=length):
            rules = initial_rules(phases)
            actual = projected_relation(rules, boundary)
            expected = candidate_relation(length, sum(phases) % 2)
            changed = projected_relation((flipped(rules[0]),) + rules[1:], boundary)
            if actual != expected or changed != candidate_relation(length, 1 - sum(phases) % 2):
                raise ValueError("Independent joined relation disagreed with the candidate")
            if actual & changed or len(actual | changed) != 2 ** len(boundary):
                raise ValueError("One phase edit did not complement the entire relation")
            for index in range(length - 1):
                combined = rules[:index] + (fuse(rules[index], rules[index + 1]),) + rules[index + 2:]
                if projected_relation(combined, boundary) != actual:
                    raise ValueError("Exact adjacent fusion changed the boundary relation")
                fusion_cases += 1
            phase_cases += 1
    length = next((n for n in lengths if n >= 2), None)
    wrong_boundary = None
    if length is not None:
        rules = initial_rules((0,) * length)
        boundary = boundary_variables(length)
        wrong = projected_relation(rules, boundary[:-1] + (3,))
        expected = candidate_relation(length, 0)
        if wrong == expected:
            raise ValueError("Wrong observer boundary did not change the relation check")
        wrong_boundary = {"length": length, "correct_output": 3 * length,
                          "wrong_output": 3, "different_boundary_states": len(wrong ^ expected)}
        # Retain the phase label but corrupt one local table entry. This also
        # checks that relation scoring and its cache depend on actual rows,
        # rather than trusting the displayed phase as a sufficient certificate.
        first = rules[0]
        bad_rows = (first.rows[0][:-1] + (1 - first.rows[0][-1],),) + first.rows[1:]
        corrupted = Rule(first.support, first.phase, bad_rows)
        damaged = projected_relation((corrupted,) + rules[1:], boundary)
        if damaged == expected:
            raise ValueError("A wrong local table entry escaped independent scoring")
        wrong_boundary["wrong_local_table_entry_different_states"] = len(damaged ^ expected)
    return {"phase_cases_checked": phase_cases, "fusion_cases_checked": fusion_cases,
            "whole_relation_phase_flip_complements": True,
            "adjacent_fusion_preserves_relation": True,
            "wrong_observer_boundary": wrong_boundary,
            "local_input_output_tables": list(PARITY_TABLES),
            "scoring_method": "join allowed local rows, then existentially project the boundary"}


def run_cell(config):
    started = time.perf_counter()
    checks = semantic_checks(tuple(sorted(set((config.train_length, *config.eval_lengths)))))
    trials = []
    for seed in config.seeds:
        learner, training = train(config, seed)
        frozen_digest, frozen_updates = learner.digest(), learner.updates
        assessments = {}
        for length in config.eval_lengths:
            # Matching seeds deliberately make untrained all-zero Q tie-breaking
            # and the random legal-action control behaviorally identical.
            control_seed = seed + 1_000_000
            untrained = QLearner()
            panels = {
                "trained_q": evaluate(config, length, learner.act, control_seed),
                "local_rule": evaluate(config, length, local_policy, control_seed),
                "random_legal": evaluate(config, length, random_policy, control_seed),
                "untrained_q": evaluate(config, length, untrained.act, control_seed),
            }
            if learner.digest() != frozen_digest or learner.updates != frozen_updates:
                raise ValueError("Evaluation changed the fitted policy")
            if untrained.q or untrained.updates:
                raise ValueError("Untrained evaluation created fitted state")
            assessments[str(length)] = panels
        trials.append({"seed": seed, "training": training,
                       "evaluation_policy_unchanged": True, "assessments": assessments})
    aggregate = {}
    for length in config.eval_lengths:
        aggregate[str(length)] = {}
        for name in ("trained_q", "local_rule", "random_legal", "untrained_q"):
            panels = [trial["assessments"][str(length)][name] for trial in trials]
            correct = sum(panel["correct"] for panel in panels)
            starts = sum(panel["starts"] for panel in panels)
            aggregate[str(length)][name] = {
                "correct": correct, "starts": starts, "success_rate": correct / starts,
                "per_seed_success_rate": [panel["success_rate"] for panel in panels]}
    return {
        "config": config.__dict__, "semantic_checks": checks,
        "hidden_sign_controls": [hidden_sign_control(config, n) for n in config.eval_lengths],
        "training_evaluation_overlap": "length-three panel is the same finite family; no held-out tuple claim",
        "unseen_length": [n for n in config.eval_lengths if n != config.train_length],
        "random_policy_exact_expected_success": 0.5,
        "untrained_control": "all-zero Q, no updates; uniform random tie-breaking",
        "aggregate": aggregate, "trials": trials,
        "runtime_seconds": time.perf_counter() - started,
        "job_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


_CONFIG = Config()


def _integers(value):
    return tuple(int(part) for part in str(value).split(","))


def setup(params):
    global _CONFIG
    integer_fields = {name: int(params[name]) for name in (
        "preparation_budget", "train_length", "train_episodes") if name in params}
    sequence_fields = {name: _integers(params[name]) for name in (
        "eval_lengths", "seeds") if name in params}
    _CONFIG = Config(**integer_fields, **sequence_fields)


def cases():
    for sight, action in product(range(3), repeat=2):
        yield f"sight-{sight}-action-{action}", {"sight_radius": sight, "action_radius": action}


def run(case_id, payload):
    return run_cell(replace(_CONFIG, **payload))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--sight", type=int, default=1)
    parser.add_argument("--action", type=int, default=1)
    parser.add_argument("--preparations", type=int, default=1)
    parser.add_argument("--train-length", type=int, default=3)
    parser.add_argument("--eval-lengths", default="3,4")
    parser.add_argument("--train-episodes", type=int, default=6000)
    parser.add_argument("--seeds", default="17,31,53")
    args = parser.parse_args()
    config = Config(sight_radius=args.sight, action_radius=args.action,
                    preparation_budget=args.preparations, train_length=args.train_length,
                    eval_lengths=_integers(args.eval_lengths),
                    train_episodes=300 if args.smoke else args.train_episodes,
                    seeds=(17,) if args.smoke else _integers(args.seeds))
    result = run_cell(config)
    if args.smoke:
        result = {key: result[key] for key in (
            "config", "semantic_checks", "aggregate", "runtime_seconds", "job_sha256")}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
