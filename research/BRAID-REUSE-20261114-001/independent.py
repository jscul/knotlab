"""Independent primitive replay and acquisition-cost audit for braid reuse.

This module imports no producer.  The old guided forward search is
reconstructed from its two random streams and checked against saved raw
trajectories.  Primitive costs are distinguished from the byte-table and
reward-cache implementation used by that historical search.
"""

from __future__ import annotations

import argparse
import base64
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import product
import json
import math
from pathlib import Path
import random
import sys
import time
import zlib
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
OLD_SOURCE = ROOT / "research/BRAID-ACTIONS-20261114-001/unguided.py"
OLD_RAW = ROOT / "artifacts/BRAID-ACTIONS-20261114-001/BRAID-ACTIONS-20261114-001-E002_rewarded_actions/results.jsonl"
OLD_BUNDLE = ROOT / "artifacts/BRAID-ACTIONS-20261114-001/BRAID-ACTIONS-20261114-001-E002_rewarded_actions/sequence_checkpoint.json"
POINTS = tuple(product(range(3), repeat=2))
TRIPLES = tuple(product(range(3), repeat=3))
TRAIN = tuple(triple for triple in TRIPLES if triple[2] != (triple[0] + triple[1] + 1) % 3)
HELD = tuple(triple for triple in TRIPLES if triple not in TRAIN)
WORDS = tuple((left << 2) | right for left, right in POINTS)
MASKS = (8, 4, 2, 1)
ACTIONS = tuple((target, guard) for target in MASKS for guard in WORDS
                if not guard & target and (guard | target) in WORDS)
ACTION_NOTS = tuple(sum(not guard & mask for mask in MASKS if mask != target) for target, guard in ACTIONS)
ORDERED_PAIRS = tuple((left, right) for left in range(3) for right in range(3) if left != right)


def _action(action: Any) -> int:
    if type(action) is not int or not 0 <= action < len(ACTIONS):
        raise ValueError("primitive action must be an integer in 0..11")
    return action


def primitive_counts(program: Sequence[int]) -> dict:
    program = tuple(_action(action) for action in program)
    counts = {"NOT": sum(ACTION_NOTS[action] for action in program),
              "AND": 2 * len(program), "XOR": len(program)}
    return {"guarded_steps": len(program), **counts, "total_gates": sum(counts.values())}


def primitive_step(action: int, point: tuple[int, int]) -> tuple[int, int]:
    """Literal NOT, AND, AND, XOR execution, without an effect table."""
    action = _action(action)
    if len(point) != 2 or any(type(value) is not int or value not in (0, 1, 2) for value in point):
        raise ValueError("a primitive acts on two legal ternary registers")
    left, right = point
    bits = [left >> 1, left & 1, right >> 1, right & 1]
    target, guard = ACTIONS[action]
    literals = [bit if guard & mask else 1 ^ bit
                for mask, bit in zip(MASKS, bits) if mask != target]
    enabled = (literals[0] & literals[1]) & literals[2]
    bits[MASKS.index(target)] ^= enabled
    return 2 * bits[0] + bits[1], 2 * bits[2] + bits[3]


def replay_pair(program: Sequence[int], point: tuple[int, int]) -> tuple[int, int]:
    for action in program:
        point = primitive_step(action, point)
    return point


def expand_program(program: Sequence[Sequence], frozen_forward: Sequence[int]) -> tuple[tuple[int, int, int], ...]:
    """Canonical independent schema: ['raw',i,j,action] or ['call',i,j]."""
    frozen_forward = tuple(_action(action) for action in frozen_forward)
    expanded = []
    for instruction in program:
        if not isinstance(instruction, (tuple, list)) or len(instruction) not in (3, 4):
            raise ValueError("malformed downstream instruction")
        operation, left, right = instruction[:3]
        if any(type(index) is not int or index not in (0, 1, 2) for index in (left, right)) or left == right:
            raise ValueError("an instruction needs two different physical registers")
        if operation == "raw" and len(instruction) == 4:
            actions = (_action(instruction[3]),)
        elif operation == "call" and len(instruction) == 3:
            actions = frozen_forward
        else:
            raise ValueError("only primitive actions and the frozen forward call are admitted")
        expanded.extend((left, right, action) for action in actions)
    return tuple(expanded)


def replay(program: Sequence[Sequence], state: tuple[int, int, int],
           frozen_forward: Sequence[int]) -> tuple[int, int, int]:
    if len(state) != 3 or any(type(value) is not int or value not in (0, 1, 2) for value in state):
        raise ValueError("three physical ternary registers are required")
    values = list(state)
    for left, right, action in expand_program(program, frozen_forward):
        values[left], values[right] = primitive_step(action, (values[left], values[right]))
    return tuple(values)


def expanded_counts(program: Sequence[Sequence], frozen_forward: Sequence[int], inputs: int = 1) -> dict:
    if type(inputs) is not int or inputs < 0:
        raise ValueError("input count must be a nonnegative integer")
    expanded = expand_program(program, frozen_forward)
    per_input = primitive_counts(tuple(action for _, _, action in expanded))
    return {"syntax_instructions": len(program), "frozen_calls": sum(step[0] == "call" for step in program),
            "per_input": per_input, "inputs": inputs,
            "logical_work": {key: value * inputs for key, value in per_input.items()}}


def target(state: tuple[int, int, int]) -> bool:
    """The supplied task, independently stated without a learned transformation."""
    return len(set(state)) in (1, 3)


def assess_program(program: Sequence[Sequence], frozen_forward: Sequence[int]) -> dict:
    rows = []
    for state in TRIPLES:
        output = replay(program, state, frozen_forward)
        expected, actual = target(state), output[2] == 0
        rows.append({"input": state, "output": output, "expected": int(expected), "actual": int(actual),
                     "correct": actual == expected, "split": "train" if state in TRAIN else "heldout"})
    summary = {}
    for name, selected in (("train", [row for row in rows if row["split"] == "train"]),
                           ("heldout", [row for row in rows if row["split"] == "heldout"]), ("all", rows)):
        correct = sum(row["correct"] for row in selected)
        summary[name] = {"correct": correct, "total": len(selected), "exact": correct == len(selected),
                         "weighted_reward": sum((2 if row["expected"] else 1) * row["correct"] for row in selected),
                         "maximum_reward": sum(2 if row["expected"] else 1 for row in selected)}
    return {**summary, "rows": rows,
            "distinct_outputs": len({tuple(row["output"]) for row in rows}),
            "positive_outputs": sum(row["actual"] for row in rows),
            "heldout_positive_outputs": sum(row["actual"] for row in rows if row["split"] == "heldout"),
            "execution": expanded_counts(program, frozen_forward, len(TRAIN))}


def normalize_genome(genome: Sequence[int]) -> tuple[tuple, ...]:
    """Decode the frozen producer token format without importing its grammar."""
    normalized = []
    for token in genome:
        if type(token) is not int or not 0 <= token < 78:
            raise ValueError("a genome token must be in 0..77")
        if token < 72:
            left, right = ORDERED_PAIRS[token // 12]
            normalized.append(("raw", left, right, token % 12))
        else:
            left, right = ORDERED_PAIRS[token - 72]
            normalized.append(("call", left, right))
    return tuple(normalized)


def _expanded_tokens(genome: Sequence[int], forward: Sequence[int]) -> tuple[int, ...]:
    return tuple(12 * ORDERED_PAIRS.index((left, right)) + action
                 for left, right, action in expand_program(normalize_genome(genome), forward))


def _packed_counts(genome: Sequence[int], forward: Sequence[int]) -> tuple[int, int, int, int]:
    actions = _expanded_tokens(genome, forward)
    return len(actions), sum(ACTION_NOTS[token % 12] for token in actions), 2 * len(actions), len(actions)


def _charge_record(packed: Sequence[int], evaluations: int, lanes: int = 18) -> dict:
    keys = ("guarded_toggles", "NOT", "AND", "XOR")
    program = dict(zip(keys, packed))
    program["Boolean_gates"] = sum(packed[1:])
    return {"packed_program": program,
            "logical_program": {key: value * lanes for key, value in program.items()},
            "packed_terminal_readout": {"OR": evaluations, "NOT": evaluations, "Boolean_gates": 2 * evaluations},
            "logical_terminal_readout": {"OR": evaluations * lanes, "NOT": evaluations * lanes,
                                         "Boolean_gates": 2 * evaluations * lanes},
            "fitness_evaluations": evaluations, "lanes": lanes}


def _canonical_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def perfect_events(wrapper: Mapping) -> list[dict]:
    """Decode and validate the ordinary base64/zlib/JSONL data format."""
    if wrapper["encoding"] != "zlib-json-lines-base64":
        raise ValueError("unknown perfect-candidate log encoding")
    compressed = base64.b64decode(wrapper["data"], validate=True)
    if hashlib.sha256(compressed).hexdigest() != wrapper["compressed_sha256"]:
        raise ValueError("perfect-candidate log digest differs")
    events = [json.loads(line) for line in zlib.decompress(compressed).splitlines()]
    if len(events) != wrapper["unique_genomes"]:
        raise ValueError("perfect-candidate log count differs")
    previous_evaluation, previous_cost, seen = 0, (0, 0, 0, 0), set()
    for event in events:
        genome = tuple(bytes.fromhex(event["genome_hex"]))
        normalize_genome(genome)
        current_cost = tuple(event["cumulative_packed"])
        if (event["evaluation"] <= previous_evaluation or genome in seen or len(current_cost) != 4
                or any(type(value) is not int or value < before for value, before in zip(current_cost, previous_cost))):
            raise ValueError("perfect-candidate log is not a unique increasing execution history")
        seen.add(genome)
        previous_evaluation, previous_cost = event["evaluation"], current_cost
    return events


def _effect_tables(forward: Sequence[int]) -> tuple[bytes, ...]:
    """Checker-only acceleration, independently built from literal raw flips.

    All downstream cost counters still charge full expansions.  These tables
    do not describe the fitter, whose eager packed-gate execution is audited
    separately, and never supply programs or labels to it.
    """
    tables = []
    for token in range(78):
        image = []
        for state in TRIPLES:
            output = replay(normalize_genome((token,)), state, forward)
            image.append(9 * output[0] + 3 * output[1] + output[2])
        if len(set(image)) != 27:
            raise ValueError("an admitted primitive or frozen call is not reversible")
        tables.append(bytes(image).ljust(256, b"\0"))
    return tuple(tables)


def _genome_image(genome: Sequence[int], tables: tuple[bytes, ...]) -> bytes:
    effect = bytes(range(27))
    for token in genome:
        effect = effect.translate(tables[token])
    return effect


def _image_scores(effect: bytes) -> dict:
    if len(effect) != 27 or len(set(effect)) != 27 or any(value >= 27 for value in effect):
        raise ValueError("candidate effect is not a legal reversible three-register map")
    train_correct = held_correct = train_score = positive_count = held_positive_count = 0
    for state, output in zip(TRIPLES, effect):
        predicted = output % 3 == 0
        wanted = target(state)
        positive_count += predicted
        if state in TRAIN:
            train_correct += predicted == wanted
            train_score += (2 if wanted else 1) * (predicted == wanted)
        else:
            held_correct += predicted == wanted
            held_positive_count += predicted
    return {"training_score": train_score, "train_correct": train_correct, "held_correct": held_correct,
            "all_correct": train_correct + held_correct, "validated_exact": train_correct == 18 and held_correct == 9,
            "positive_outputs": positive_count, "held_positive_outputs": held_positive_count}


def audit_keeper(record: Mapping | None, forward: Sequence[int], *, tables: tuple[bytes, ...] | None = None) -> dict | None:
    if record is None:
        return None
    genome = tuple(record["genome"])
    program = normalize_genome(genome)
    expanded = expand_program(program, forward)
    if len(expanded) > 36:
        raise ValueError("keeper exceeds the expanded bound")
    packed = _packed_counts(genome, forward)
    expected_expansion = [{"pair": [left, right], "action": action} for left, right, action in expanded]
    if ([dict(pair=list(step["pair"]), action=step["action"]) for step in record["expanded_program"]] != expected_expansion
            or record["expanded_guarded_length"] != packed[0]
            or record["macro_calls"] != sum(token >= 72 for token in genome)
            or record["exposed_length"] != len(genome)
            or record["genome_hex"] != bytes(genome).hex()
            or record["genome_sha256"] != hashlib.sha256(bytes(genome)).hexdigest()
            or record["inference_counts_per_input"] != dict(zip(("guarded_toggles", "NOT", "AND", "XOR"), packed))):
        raise ValueError("keeper representation or expansion counts differ")
    if record["charges_to_event"] != _charge_record(record["cumulative_packed"], record["evaluation"]):
        raise ValueError("keeper cumulative cost units differ")
    # Every selected keeper receives literal scalar replay, independent of
    # the checker-only effect tables used for the complete event log.
    scalar = assess_program(program, forward)
    if record["training_score"] != scalar["train"]["weighted_reward"]:
        raise ValueError("keeper's recorded training score differs from raw replay")
    if tables is not None:
        score = _image_scores(_genome_image(genome, tables))
        if score["all_correct"] != scalar["all"]["correct"]:
            raise ValueError("checker table and literal keeper replay disagree")
    return {"evaluation": record["evaluation"], "genome": genome,
            "expanded_guarded_length": packed[0], "macro_calls": record["macro_calls"],
            "training_score": scalar["train"]["weighted_reward"],
            "train_correct": scalar["train"]["correct"], "held_correct": scalar["heldout"]["correct"],
            "validated_exact": scalar["all"]["exact"],
            "inference_counts_per_input": dict(zip(("guarded_toggles", "NOT", "AND", "XOR"), packed)),
            "charges_to_event": _charge_record(record["cumulative_packed"], record["evaluation"]),
            "raw_rows": scalar["rows"]}


def audit_arm(arm: Mapping, forward: Sequence[int], tables: tuple[bytes, ...] | None = None) -> dict:
    tables = _effect_tables(forward) if tables is None else tables
    if arm["condition"] not in ("raw", "reuse") or arm["evaluations"] != 196640:
        raise ValueError("unexpected downstream condition or evaluation budget")
    charges = arm["charges"]
    final_packed = tuple(charges["packed_program"][key] for key in ("guarded_toggles", "NOT", "AND", "XOR"))
    if charges != _charge_record(final_packed, arm["evaluations"]):
        raise ValueError("full-budget charge arithmetic differs")
    if arm["fitness_cache_hits"] != 0:
        raise ValueError("a fitness cache bypassed declared eager execution")
    events = perfect_events(arm["train_perfect_events"])
    held_counts = {str(value): 0 for value in (3, 5, 7, 9)}
    first_valid = None
    for event in events:
        genome = tuple(bytes.fromhex(event["genome_hex"]))
        packed = _packed_counts(genome, forward)
        if (packed[0] != event["expanded_guarded_length"] or packed[0] > 36
                or event["macro_calls"] != sum(token >= 72 for token in genome)
                or (arm["condition"] == "raw" and any(token >= 72 for token in genome))):
            raise ValueError("training-perfect event violates its instruction language")
        score = _image_scores(_genome_image(genome, tables))
        if score["train_correct"] != 18 or score["held_positive_outputs"] != 3:
            raise ValueError("logged training-perfect event fails independent training/cardinality replay")
        held_counts[str(score["held_correct"])] += 1
        if score["validated_exact"] and first_valid is None:
            first_valid = {"evaluation": event["evaluation"], "genome_hex": event["genome_hex"],
                           "elapsed_seconds": event["elapsed_ns"] / 1e9,
                           "macro_calls": event["macro_calls"], "expanded_guarded_length": packed[0],
                           "charges_to_event": _charge_record(event["cumulative_packed"], event["evaluation"])}
    selected = audit_keeper(arm["training_selected"], forward, tables=tables)
    first_train = audit_keeper(arm["first_train_perfect"], forward, tables=tables)
    if bool(first_train) != bool(events) or (first_train and first_train["evaluation"] != events[0]["evaluation"]):
        raise ValueError("first training-perfect keeper and event log differ")
    capped_charges = arm["charges"] if first_valid is None else first_valid["charges_to_event"]
    return {"seed": arm["seed"], "condition": arm["condition"], "evaluations": arm["evaluations"],
            "unique_training_perfect": len(events), "held_score_counts": held_counts,
            "training_selected": selected, "first_train_perfect": first_train,
            "retrospective_first_validated": first_valid, "right_censored": first_valid is None,
            "capped_evaluation": arm["evaluations"] if first_valid is None else first_valid["evaluation"],
            "capped_elapsed_seconds": arm["elapsed_seconds"] if first_valid is None else first_valid["elapsed_seconds"],
            "completed_budget_elapsed_seconds": arm["elapsed_seconds"],
            "capped_charges": capped_charges, "full_budget_charges": arm["charges"],
            "cost_recount": "candidate expansions and all saved perfect events independently replayed; complete proposal recount requires reconstruct_arm"}


def reconstruct_arm(arm: Mapping, config: Mapping, forward: Sequence[int], tables: tuple[bytes, ...] | None = None) -> dict:
    """Reproduce all proposals from frozen random streams and training reward.

    This is an offline audit of a saved arm, never a source of candidates for
    fitting.  Only training labels affect reconstruction.  Checker effect
    tables accelerate semantics; counts still include every literal expansion.
    """
    tables = _effect_tables(forward) if tables is None else tables
    if any(config[key] != value for key, value in {
        "islands": 32, "generations": 512, "brood": 12, "maximum_expanded_length": 36,
        "initial_minimum": 2, "initial_maximum": 12, "restart_period": 32, "call_denominator": 13}.items()):
        raise ValueError("unexpected downstream reconstruction protocol")
    seed, allow_calls = arm["seed"], arm["condition"] == "reuse"
    variation, selection = random.Random(seed), random.Random(seed + 1)
    lengths = (1,) * 72 + (12,) * 6
    token_counts = tuple(_packed_counts((token,), forward) for token in range(78))
    recorded_events = perfect_events(arm["train_perfect_events"])
    event_position = 0
    seen = set()
    total_perfect = evaluations = 0
    cumulative = [0, 0, 0, 0]
    best = first = None
    trajectories = []
    training_contract = tuple((TRIPLES.index(state), target(state), 2 if target(state) else 1) for state in TRAIN)

    def draw():
        pair, action = variation.randrange(6), variation.randrange(12)
        return 12 * pair + action, 72 + pair, variation.randrange(13) == 0

    def random_program(initial=False):
        count = variation.randint(2, 12)
        draws = [draw() for _ in range(count)]
        genome, expanded = [item[0] for item in draws], count
        for index, (_, call, requested) in enumerate(draws):
            if allow_calls and not initial and requested and expanded + 11 <= 36:
                genome[index] = call
                expanded += 11
        return tuple(genome)

    def expanded_length(genome):
        return sum(lengths[token] for token in genome)

    def mutate(parent):
        kind, left, right = variation.randrange(100), variation.random(), variation.random()
        raw, call, requested = draw()
        token = call if allow_calls and requested else raw
        size, expanded = len(parent), expanded_length(parent)
        if not size:
            return (token,)
        if kind < 30 and expanded < 36:
            if expanded + lengths[token] > 36:
                token = raw
            position = int(left * (size + 1))
            return parent[:position] + (token,) + parent[position:]
        position = int(left * size)
        if 30 <= kind < 55:
            return parent[:position] + parent[position + 1:]
        if kind < 85:
            if expanded - lengths[parent[position]] + lengths[token] > 36:
                token = raw
            return parent[:position] + (token,) + parent[position + 1:]
        reduced = parent[:position] + parent[position + 1:]
        destination = int(right * size)
        return reduced[:destination] + (parent[position],) + reduced[destination:]

    def evaluate(genome):
        nonlocal evaluations, best, first, total_perfect, event_position
        expanded = expanded_length(genome)
        if expanded > 36 or (not allow_calls and any(token >= 72 for token in genome)):
            raise ValueError("reconstructed proposal left the frozen language")
        effect = _genome_image(genome, tables)
        # No held labels are consulted here.
        score = sum(weight * ((effect[index] % 3 == 0) == wanted)
                    for index, wanted, weight in training_contract)
        evaluations += 1
        cumulative[0] += expanded
        cumulative[1] += sum(token_counts[token][1] for token in genome)
        cumulative[2] += 2 * expanded
        cumulative[3] += expanded
        current = {"genome": genome, "score": score, "evaluation": evaluations,
                   "expanded": expanded, "cumulative": tuple(cumulative)}
        if best is None or (score, -expanded) > (best["score"], -best["expanded"]):
            best = current
        if score == 24:
            total_perfect += 1
            if first is None:
                first = current
            if genome not in seen:
                seen.add(genome)
                if event_position >= len(recorded_events):
                    raise ValueError("saved log omitted a first-seen perfect candidate")
                event = recorded_events[event_position]
                if (event["evaluation"] != evaluations or event["genome_hex"] != bytes(genome).hex()
                        or event["cumulative_packed"] != cumulative
                        or event["expanded_guarded_length"] != expanded
                        or event["macro_calls"] != sum(token >= 72 for token in genome)):
                    raise ValueError("reconstructed perfect event differs")
                event_position += 1
        return genome, score, expanded

    started = time.perf_counter()
    initial = [random_program(True) for _ in range(32)]
    initial_hash = _canonical_sha(initial)
    parents = [evaluate(genome) for genome in initial]

    def record(generation):
        trajectories.append({"generation": generation, "evaluations": evaluations,
                             "best_training_score": best["score"], "best_expanded_length": best["expanded"],
                             "sum_parent_scores": sum(parent[1] for parent in parents),
                             "cumulative_packed": list(cumulative)})

    record(0)
    for generation in range(1, 513):
        for island, parent in enumerate(parents):
            children = [parent]
            children.extend(evaluate(mutate(parent[0])) for _ in range(11))
            children.append(evaluate(random_program()))
            if generation % 32 == 0:
                parents[island] = children[-1]
            else:
                highest = max(child[1] for child in children)
                tied = [child for child in children if child[1] == highest]
                parents[island] = tied[int(selection.random() * len(tied))]
        record(generation)

    def keeper_matches(reconstructed, saved):
        if reconstructed is None or saved is None:
            return reconstructed is None and saved is None
        return (list(reconstructed["genome"]) == saved["genome"]
                and reconstructed["evaluation"] == saved["evaluation"]
                and reconstructed["score"] == saved["training_score"]
                and list(reconstructed["cumulative"]) == saved["cumulative_packed"])

    checks = {"evaluations": evaluations == arm["evaluations"],
              "complete_cost_ledger": _charge_record(cumulative, evaluations) == arm["charges"],
              "every_trajectory_row": trajectories == arm["trajectory"],
              "every_first_seen_perfect_event": event_position == len(recorded_events),
              "perfect_repeats": total_perfect == arm["train_perfect_events"]["training_perfect_proposals_including_repeats"],
              "initial_population": initial_hash == arm["initial_population_sha256"],
              "final_variation_rng": _canonical_sha(variation.getstate()) == arm["variation_rng_final_sha256"],
              "final_selection_rng": _canonical_sha(selection.getstate()) == arm["selection_rng_final_sha256"],
              "training_selected": keeper_matches(best, arm["training_selected"]),
              "first_train_perfect": keeper_matches(first, arm["first_train_perfect"])}
    return {"pass": all(checks.values()), "checks": checks, "evaluations": evaluations,
            "reconstructed_charges": _charge_record(cumulative, evaluations),
            "checker_seconds": time.perf_counter() - started,
            "checker_acceleration": "27-state effects independently compiled from raw Boolean flips; costs charge every expansion"}


def _audit_post(arm: Mapping, independent: Mapping, post: Mapping, forward: Sequence[int]) -> dict:
    checks = {
        "right_censor": independent["right_censored"] == post["right_censored"],
        "capped_evaluation": independent["capped_evaluation"] == post["capped_evaluation"],
        "capped_charges": independent["capped_charges"] == post["capped_charges"],
        "held_distribution": independent["held_score_counts"] == post["unique_train_perfect_held_score_counts"],
    }
    own_first, saved_first = independent["retrospective_first_validated"], post["retrospective_first_validated"]
    checks["first_validated_event"] = ((own_first is None and saved_first is None)
                                       or (own_first is not None and saved_first is not None
                                           and own_first["evaluation"] == saved_first["evaluation"]
                                           and own_first["genome_hex"] == saved_first["genome_hex"]))
    for name in ("first_train_perfect", "training_selected"):
        ours, theirs = independent[name], post[name]
        checks[name + "_held_score"] = ((ours is None and theirs is None)
                                       or (ours is not None and theirs is not None
                                           and ours["held_correct"] == theirs["held_correct"]
                                           and ours["validated_exact"] == theirs["validated_exact"]))
    # Independently charge the post-fit held checks, including the retained
    # nonperfect program if it was not in the perfect-event log.
    events = perfect_events(arm["train_perfect_events"])
    held_genomes = {event["genome_hex"] for event in events}
    held_genomes.update(record["genome_hex"] for record in (arm["first_train_perfect"], arm["training_selected"])
                        if record is not None)
    held_counts = [0, 0, 0, 0]
    for genome_hex in held_genomes:
        for index, value in enumerate(_packed_counts(tuple(bytes.fromhex(genome_hex)), forward)):
            held_counts[index] += value
    checks["offline_held_executions"] = len(held_genomes) == post["offline_held_executions"]
    checks["offline_held_charges"] = _charge_record(held_counts, len(held_genomes), 9) == post["offline_held_charges"]
    replay_genomes = set()
    for name in ("first_train_perfect", "training_selected", "retrospective_first_validated"):
        record, replayed = post[name], post["raw_replays"][name]
        if record is None:
            checks[name + "_raw_replay"] = replayed is None
            continue
        checked = audit_keeper(record, forward)
        expected_rows = [{"input": row["input"], "output": row["output"],
                          "prediction": row["actual"], "target": row["expected"]}
                         for row in checked["raw_rows"]]
        checks[name + "_raw_replay"] = (_canonical_sha(expected_rows) == _canonical_sha(replayed["rows"])
                                         and checked["train_correct"] + checked["held_correct"] == replayed["correct"])
        replay_genomes.add(record["genome_hex"])
    replay_counts = [0, 0, 0, 0]
    for genome_hex in replay_genomes:
        for index, value in enumerate(_packed_counts(tuple(bytes.fromhex(genome_hex)), forward)):
            replay_counts[index] += 27 * value
    checks["offline_scalar_charges"] = dict(zip(("guarded_toggles", "NOT", "AND", "XOR"), replay_counts)) == post["offline_scalar_replay_charges"]
    checks["offline_scalar_point_executions"] = 27 * len(replay_genomes) == post["offline_scalar_point_executions"]
    return {"pass": all(checks.values()), "checks": checks}


def _paired_payback(acquisition: int, raw_total: int, reuse_total: int, repetitions: int) -> dict:
    """Express integer summed costs as a per-repeat mean without unit relabeling."""
    saving = Fraction(raw_total - reuse_total, repetitions)
    result = {"mean_saving_per_repeat": float(saving),
              "mean_saving_exact": (saving.numerator, saving.denominator),
              "sum_saving_over_repeats": raw_total - reuse_total, "repeats": repetitions}
    if saving <= 0:
        return {**result, "hypothetical_break_even_uses": None, "reason": "No positive mean saving in this unit."}
    ratio = Fraction(acquisition, 1) / saving
    return {**result, "acquisition_over_mean_saving": (ratio.numerator, ratio.denominator),
            "hypothetical_break_even_uses": (ratio.numerator + ratio.denominator - 1) // ratio.denominator}


def verify_result(data: Mapping, *, reconstruct_search: bool = True, progress=None) -> dict:
    """Audit all ten frozen arms, all perfect events and complete cost ledgers."""
    if "result" in data:
        data = data["result"]
    config, acquisition, arms = data["config"], data["acquisition"], data["arms"]
    payload = {"config": config, "acquisition": acquisition, "arms": arms}
    checks = {"frozen_training_sha256": _canonical_sha(payload) == data["frozen_training_sha256"],
              "training_split": _canonical_sha(data["train_states"]) == _canonical_sha(TRAIN),
              "heldout_split": _canonical_sha(data["held_states"]) == _canonical_sha(HELD),
              "five_fixed_seeds": config["seeds"] == [17, 29, 43, 59, 71],
              "six_ordered_pairs": _canonical_sha(config["ordered_pairs"]) == _canonical_sha(ORDERED_PAIRS)}
    bundle_bytes = OLD_BUNDLE.read_bytes()
    bundle = json.loads(bundle_bytes)
    forward = tuple(bundle["forward"])
    checks["source_bundle_digest"] = hashlib.sha256(bundle_bytes).hexdigest() == acquisition["bundle_sha256"]
    checks["source_action_digest"] = hashlib.sha256(bytes(forward)).hexdigest() == acquisition["forward_action_bytes_sha256"]
    checks["source_not_retrained"] = acquisition["retrained"] is False and list(forward) == acquisition["forward_action_ids"]
    tables = _effect_tables(forward)
    post = {(row["seed"], row["condition"]): row for row in data["post_freeze"]}
    indexed = {(row["seed"], row["condition"]): row for row in arms}
    expected_keys = {(seed, condition) for seed in config["seeds"] for condition in ("raw", "reuse")}
    checks["ten_distinct_arms"] = len(indexed) == len(arms) == 10 and set(indexed) == set(post) == expected_keys
    audited = []
    for arm in arms:
        key = (arm["seed"], arm["condition"])
        own = audit_arm(arm, forward, tables)
        own["post_freeze_reproduction"] = _audit_post(arm, own, post[key], forward)
        own["search_reconstruction"] = (reconstruct_arm(arm, config, forward, tables) if reconstruct_search
                                         else {"pass": None, "not_run": "Full proposal costs were not independently recounted."})
        for name in ("first_train_perfect", "training_selected"):
            if own[name] is not None:
                own[name].pop("raw_rows", None)
        audited.append(own)
        if progress is not None:
            progress(f"audited seed {key[0]} {key[1]}: {own['unique_training_perfect']} unique training-perfect programs")
    for seed in config["seeds"]:
        left, right = indexed[seed, "raw"], indexed[seed, "reuse"]
        for field in ("initial_population_sha256", "variation_rng_final_sha256", "selection_rng_final_sha256"):
            checks[f"paired_{seed}_{field}"] = left[field] == right[field]
    source_cost = audit_acquisition()
    checks["historical_acquisition_reproduced"] = source_cost["pass"]
    arm_audits = {(row["seed"], row["condition"]): row for row in audited}
    paired = []
    for seed in config["seeds"]:
        raw, reuse = arm_audits[seed, "raw"], arm_audits[seed, "reuse"]
        row = {"seed": seed}
        for condition, report in (("raw", raw), ("reuse", reuse)):
            row[condition] = {
                "train_selected_held_correct": report["training_selected"]["held_correct"],
                "train_selected_validated": report["training_selected"]["validated_exact"],
                "right_censored": report["right_censored"], "capped_evaluation": report["capped_evaluation"],
                "capped_elapsed_seconds": report["capped_elapsed_seconds"],
                "completed_budget_elapsed_seconds": report["completed_budget_elapsed_seconds"],
                "capped_logical_program_gates": report["capped_charges"]["logical_program"]["Boolean_gates"],
                "capped_logical_guarded_steps": report["capped_charges"]["logical_program"]["guarded_toggles"],
                "first_validated_macro_calls": None if report["right_censored"] else report["retrospective_first_validated"]["macro_calls"],
                "full_budget_logical_program_gates": report["full_budget_charges"]["logical_program"]["Boolean_gates"],
            }
        row["both_retrospectively_validated"] = not raw["right_censored"] and not reuse["right_censored"]
        row["capped_proposal_saving_reuse"] = raw["capped_evaluation"] - reuse["capped_evaluation"]
        row["capped_logical_program_gate_saving_reuse"] = row["raw"]["capped_logical_program_gates"] - row["reuse"]["capped_logical_program_gates"]
        row["completed_budget_logical_program_gate_saving_reuse"] = row["raw"]["full_budget_logical_program_gates"] - row["reuse"]["full_budget_logical_program_gates"]
        paired.append(row)
    all_validated = all(row["both_retrospectively_validated"] for row in paired)
    if all_validated:
        raw_proposals = sum(row["raw"]["capped_evaluation"] for row in paired)
        reuse_proposals = sum(row["reuse"]["capped_evaluation"] for row in paired)
        raw_gates = sum(row["raw"]["capped_logical_program_gates"] for row in paired)
        reuse_gates = sum(row["reuse"]["capped_logical_program_gates"] for row in paired)
        payback = {"same_target_all_pairs_validated": True,
                   "retrospective_only": True,
                   "proposal_units": _paired_payback(source_cost["proposals"], raw_proposals, reuse_proposals, len(paired)),
                   "logical_actor_gate_units": _paired_payback(source_cost["semantic_nine_state_work"]["total_gates"], raw_gates, reuse_gates, len(paired)),
                   "warning": "Retrospective first-valid arithmetic uses an oracle unavailable to training selection. It is not an operational early-stopping or learning-speed result, and repeats one target rather than a task distribution. Actor gate units exclude scoring/readout overhead."}
    else:
        payback = {"same_target_all_pairs_validated": False, "not_estimated": "Censoring or unequal validated success prevents a like-for-like per-task savings estimate."}
    raw_full = sum(row["raw"]["full_budget_logical_program_gates"] for row in paired)
    reuse_full = sum(row["reuse"]["full_budget_logical_program_gates"] for row in paired)
    payback["completed_fixed_budget"] = {
        "proposal_units": break_even(source_cost["proposals"], 196640, 196640),
        "logical_actor_gate_units": _paired_payback(source_cost["semantic_nine_state_work"]["total_gates"], raw_full, reuse_full, len(paired)),
        "raw_total_logical_actor_gates_five_runs": raw_full,
        "reuse_total_logical_actor_gates_five_runs": reuse_full,
        "scope": "Actual completed fixed-budget fits, separately from retrospective first valid discovery."}
    payback["training_selected_validated_counts"] = {
        condition: sum(row[condition]["train_selected_validated"] for row in paired) for condition in ("raw", "reuse")}
    payback["operational_payback_established"] = (
        all(count == len(paired) for count in payback["training_selected_validated_counts"].values())
        and payback["completed_fixed_budget"]["logical_actor_gate_units"]["mean_saving_per_repeat"] > 0)
    payback["wall_time_payback_estimated"] = source_cost["timing"]["original_guided_forward_seconds"] is not None
    payback["wall_time_reason"] = "Historical source acquisition was not separately timed; its recorded time includes four stages and assessment."
    finite_checks = all(checks.values()) and all(row["post_freeze_reproduction"]["pass"] for row in audited)
    if reconstruct_search:
        finite_checks = finite_checks and all(row["search_reconstruction"]["pass"] for row in audited)
    return {"pass": finite_checks, "checks": checks, "frozen_training_sha256": data["frozen_training_sha256"],
            "full_search_reconstruction_run": reconstruct_search, "arms": audited, "paired": paired,
            "acquisition_cost": source_cost, "payback": payback,
            "completion_control": reversible_completion_control(),
            "constructive_controls": {name: {key: value for key, value in assess_program(program, forward).items() if key != "rows"}
                                      for name, program in constructive_controls().items()},
            "scope": "One frozen new task, five paired seeds. No held labels entered proposal selection; retrospective discovery and training-selected inference are separate."}


def reversible_completion_control() -> dict:
    """Finite counting control, not a null distribution for the program search."""
    held_positive = sum(target(state) for state in HELD)
    possibilities = math.comb(len(HELD), held_positive)
    return {"global_positive_states": 9, "train_positive_states": 6,
            "heldout_positive_states_for_any_train_perfect_permutation": held_positive,
            "heldout_label_completions": possibilities,
            "possible_heldout_correct_counts": [3, 5, 7, 9],
            "globally_correct_reversible_completions": math.factorial(9) * math.factorial(18),
            "uniform_completion_fraction": (1, possibilities),
            "warning": "Combinatorial only. The fitted program distribution is not uniform over completions."}


def constructive_controls() -> dict[str, tuple]:
    """Supplied audit controls, never candidates or demonstrations for the search."""
    add_first_into_second = (10, 7, 8, 11)
    add_second_into_first = (4, 1, 2, 5)
    first = tuple(("raw", 0, 2, action) for action in add_first_into_second)
    first += tuple(("raw", 1, 2, action) for action in add_first_into_second)
    second = tuple(("raw", 0, 1, action) for action in add_second_into_first)
    second += tuple(("raw", 0, 2, action) for action in add_first_into_second)
    return {"z_add_x_then_y": first, "x_add_y_then_z_add_x": second}


def _image(program: Sequence[int], tables: tuple[bytes, ...]) -> bytes:
    result = bytes(range(9))
    for action in program:
        result = result.translate(tables[action])
    return result


def _forward_score(image: bytes) -> int:
    """Independent direct tuple scoring, not the producer's byte-packed scorer."""
    def step(state, place):
        state = list(state)
        pair = image[3 * state[place] + state[place + 1]]
        state[place:place + 2] = pair // 3, pair % 3
        return tuple(state)

    agree = 0
    for state in TRAIN:
        left = right = state
        for place in (0, 1, 0):
            left = step(left, place)
        for place in (1, 0, 1):
            right = step(right, place)
        agree += left == right
    first, second = tuple(value // 3 for value in image), tuple(value % 3 for value in image)
    rows = [len(set(first[3 * value:3 * value + 3])) for value in range(3)]
    columns = [len(set(second[value::3])) for value in range(3)]
    first_mixed = max(rows) > 1 and any(len(set(first[value::3])) > 1 for value in range(3))
    second_mixed = max(columns) > 1 and any(len(set(second[3 * value:3 * value + 3])) > 1 for value in range(3))
    diagonal = sum(image[4 * value] == 4 * value for value in range(3))
    noninvolution = any(image[image[value]] != value for value in range(9))
    return agree + sum(rows) + sum(columns) + 2 * diagonal + 4 * (first_mixed or second_mixed) + 2 * noninvolution


def _random_program(rng: random.Random) -> tuple[int, ...]:
    return tuple(rng.randrange(12) for _ in range(rng.randint(6, 24)))


def _mutate(parent: tuple[int, ...], rng: random.Random) -> tuple[int, ...]:
    kind = rng.randrange(100)
    first, second = rng.random(), rng.random()
    action = rng.randrange(12)
    length = len(parent)
    if length == 0:
        return (action,)
    if kind < 30 and length < 32:
        position = int(first * (length + 1))
        return parent[:position] + (action,) + parent[position:]
    position = int(first * length)
    if 30 <= kind < 55:
        return parent[:position] + parent[position + 1:]
    if kind < 85:
        return parent[:position] + (action,) + parent[position + 1:]
    reduced = parent[:position] + parent[position + 1:]
    destination = int(second * length)
    return reduced[:destination] + (parent[position],) + reduced[destination:]


def audit_acquisition(raw_path: Path = OLD_RAW, source_path: Path = OLD_SOURCE,
                      bundle_path: Path = OLD_BUNDLE) -> dict:
    """Replay the historical guided forward stage only, with exact work totals."""
    raw_bytes = Path(raw_path).read_bytes()
    raw_record = json.loads(raw_bytes)
    fit = raw_record["result"]["fit"]
    saved = fit["stages"]["guided_forward"]
    if fit["seed"] != 27183 or fit["sizes"] != {"islands": 32, "generations": 256, "brood": 12}:
        raise ValueError("unexpected historical acquisition protocol")
    if fit["initial_length"] != [6, 24] or fit["maximum_length"] != 32 or fit["restart_period"] != 32:
        raise ValueError("unexpected historical proposal grammar")
    tables = tuple(bytes(3 * output[0] + output[1] for output in
                         (primitive_step(action, pair) for pair in POINTS)).ljust(256, b"\0")
                   for action in range(12))
    variation, selection = random.Random(27183), random.Random(27184)
    cache, length_histogram, action_histogram = {}, Counter(), Counter()
    proposals = 0
    best = None
    first_maximum = None
    first_maximum_work = None
    trajectory = []
    frontier = []

    def current_work():
        steps = sum(action_histogram.values())
        negations = sum(count * ACTION_NOTS[action] for action, count in action_histogram.items())
        return {"guarded_steps_per_input": steps, "NOT_per_input": negations,
                "AND_per_input": 2 * steps, "XOR_per_input": steps,
                "gates_per_input": negations + 3 * steps}

    def evaluate(program):
        nonlocal proposals, best, first_maximum, first_maximum_work
        image = _image(program, tables)
        if image not in cache:
            cache[image] = _forward_score(image)
        score = cache[image]
        proposals += 1
        length_histogram[len(program)] += 1
        action_histogram.update(program)
        if score == 48 and first_maximum is None:
            first_maximum = proposals
            first_maximum_work = current_work()
        if best is None or (score, -len(program)) > (best[1], -len(best[0])):
            best = program, score
            frontier.append({"proposal": proposals, "score": score, "length": len(program)})
        return program, score

    started = time.perf_counter()
    parents = [evaluate(_random_program(variation)) for _ in range(32)]

    def record(generation):
        trajectory.append([generation, proposals, best[1], len(best[0]), sum(score for _, score in parents)])

    record(0)
    for generation in range(1, 257):
        for island, (parent, parent_score) in enumerate(parents):
            candidates = [(parent, parent_score)]
            candidates.extend(evaluate(_mutate(parent, variation)) for _ in range(11))
            candidates.append(evaluate(_random_program(variation)))
            if generation % 32 == 0:
                parents[island] = candidates[-1]
            else:
                maximum = max(score for _, score in candidates)
                eligible = [candidate for candidate in candidates if candidate[1] == maximum]
                parents[island] = eligible[int(selection.random() * len(eligible))]
        record(generation)
    elapsed = time.perf_counter() - started
    final, score = best
    digest = hashlib.sha256(bytes(final)).hexdigest()
    comparisons = {
        "proposal_count": proposals == saved["proposals_scored_including_initializations"],
        "distinct_images": len(cache) == saved["distinct_images_scored"],
        "first_maximum": first_maximum == saved["first_maximum_evaluation"],
        "final_actions": list(final) == saved["actions"],
        "final_digest": digest == saved["sha256_action_bytes"],
        "final_score": score == saved["score"],
        "saved_primitive_counts": {key: primitive_counts(final)[key] for key in ("NOT", "AND", "XOR")}
                                  == saved["primitive_counts"],
        "every_saved_trajectory_row": trajectory == saved["trajectory"],
    }
    bundle_bytes = Path(bundle_path).read_bytes()
    bundle = json.loads(bundle_bytes)
    comparisons["bundle_same_forward"] = bundle["forward"] == list(final)
    names = ("x_high", "x_low", "y_high", "y_low")
    repertoire = [{"id": action, "toggle": names[MASKS.index(target)],
                   "guard": {name: int(bool(guard & mask)) for name, mask in zip(names, MASKS) if mask != target}}
                  for action, (target, guard) in enumerate(ACTIONS)]
    comparisons["saved_primitive_repertoire"] = repertoire == fit["operator_repertoire"]
    work = current_work()
    steps, gates = work["guarded_steps_per_input"], work["gates_per_input"]
    misses = len(cache)
    mean_steps, mean_gates = Fraction(steps, proposals), Fraction(gates, proposals)
    return {
        "pass": all(comparisons.values()), "reproduction": comparisons,
        "source_sha256": hashlib.sha256(Path(source_path).read_bytes()).hexdigest(),
        "raw_results_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "bundle_sha256": hashlib.sha256(bundle_bytes).hexdigest(), "forward_action_sha256": digest,
        "guided_forward_only": True, "proposals": proposals, "reward_cache_misses": misses,
        "reward_cache_hits": proposals - misses, "first_maximum_proposal": first_maximum,
        "first_maximum_cumulative_work_per_input": first_maximum_work,
        "final_program": {"actions": final, **primitive_counts(final)},
        "all_proposals_work_per_input": work,
        "mean_candidate_cost_per_input": {
            "guarded_steps_fraction": (mean_steps.numerator, mean_steps.denominator),
            "primitive_gates_fraction": (mean_gates.numerator, mean_gates.denominator),
            "guarded_steps": float(mean_steps), "primitive_gates": float(mean_gates)},
        "semantic_nine_state_work": {"guarded_applications": 9 * steps,
                                     "enabled_bit_toggles": 2 * steps,
                                     "NOT": 9 * work["NOT_per_input"],
                                     "AND": 9 * work["AND_per_input"],
                                     "XOR": 9 * work["XOR_per_input"], "total_gates": 9 * gates},
        "length_histogram": dict(sorted(length_histogram.items())),
        "action_histogram": dict(sorted(action_histogram.items())), "best_frontier": frontier,
        "implementation": {
            "program_image_translate_calls": steps,
            "program_image_translated_bytes": 9 * steps,
            "reward_translate_calls_on_cache_misses": 6 * misses,
            "reward_translated_bytes_on_cache_misses": 126 * misses,
            "reward_padded_table_bytes_created": 512 * misses,
            "terminal_training_braid_comparisons": len(TRAIN) * misses,
            "cached_image_key_payload_bytes": 9 * misses,
            "shared_primitive_translation_table_bytes": 12 * 256,
            "parent_choices_including_restarts": 32 * 256,
            "forced_periodic_restarts": 32 * 8,
            "source_program_execution_bypassed_by_reward_cache": False,
            "primitive_interpreter_used_for_original_search": False,
        },
        "timing": {"audit_reproduction_seconds": elapsed,
                   "original_combined_four_stage_runner_seconds": raw_record["seconds"],
                   "original_guided_forward_seconds": None},
        "cost_scope": "The full fixed guided-forward stage selected the reusable final program; undo and neutral searches are excluded.",
        "unit_warning": "Nine-state literal primitive counts are semantic work, not measured instructions of the byte-packed implementation. Do not mix them with cached scoring or wall seconds.",
    }


def break_even(acquisition: int, primitive_cost: int, reuse_cost: int) -> dict:
    """All three inputs must use the same declared cost unit and success gate."""
    if any(type(value) is not int or value < 0 for value in (acquisition, primitive_cost, reuse_cost)):
        raise ValueError("costs must be nonnegative integer counts in one common unit")
    saving = primitive_cost - reuse_cost
    if saving <= 0:
        return {"per_task_saving": saving, "first_break_even_task_count": None,
                "reason": "No positive per-task saving in this unit."}
    ratio = Fraction(acquisition, saving)
    return {"per_task_saving": saving, "acquisition_over_saving": (ratio.numerator, ratio.denominator),
            "first_break_even_task_count": (acquisition + saving - 1) // saving,
            "interpretation": "Pretraining is paid once; every counted task must meet the same declared validation gate."}


def self_test() -> dict:
    assert len(ACTIONS) == 12
    for action in range(12):
        assert all(primitive_step(action, primitive_step(action, pair)) == pair for pair in POINTS)
    bundle = json.loads(OLD_BUNDLE.read_text())
    forward = bundle["forward"]
    assert primitive_counts(forward) == {"guarded_steps": 12, "NOT": 24, "AND": 24, "XOR": 12, "total_gates": 60}
    controls = {}
    for name, program in constructive_controls().items():
        result = assess_program(program, forward)
        assert result["all"]["exact"]
        assert result["execution"]["per_input"]["guarded_steps"] == 8
        assert result["execution"]["per_input"]["total_gates"] == 40
        assert result["train"]["maximum_reward"] == 24 and result["heldout"]["maximum_reward"] == 12
        controls[name] = {"all_exact": True, "execution": result["execution"]}
    calls = (("call", 0, 2),)
    for state in TRIPLES:
        actual = replay(calls, state, forward)
        pair = replay_pair(forward, (state[0], state[2]))
        assert actual == (pair[0], state[1], pair[1])
    return {"pass": True, "controls_are_not_search_inputs": True, "constructive_controls": controls,
            "completion_control": reversible_completion_control()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acquisition", type=Path, nargs="?", const=OLD_RAW)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--result", type=Path, help="official result JSON or one-row JSONL")
    parser.add_argument("--skip-search-reconstruction", action="store_true")
    parser.add_argument("--write", action="store_true", help="save audit.json beside --result")
    args = parser.parse_args()
    if not args.acquisition and not args.self_test and not args.result:
        parser.error("provide --acquisition, --self-test, or --result")
    if args.write and not args.result:
        parser.error("--write requires --result")
    result = {}
    if args.self_test:
        result["self_test"] = self_test()
    if args.acquisition:
        result["acquisition"] = audit_acquisition(args.acquisition)
    if args.result:
        raw = args.result.read_bytes()
        result["result_file_sha256"] = hashlib.sha256(raw).hexdigest()
        result["checker_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        result["verification"] = verify_result(json.loads(raw),
                                                reconstruct_search=not args.skip_search_reconstruction,
                                                progress=lambda value: print(value, file=sys.stderr, flush=True))
    if args.write:
        output = args.result.parent / "audit.json"
        output.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({"audit": str(output.resolve()), "pass": result["verification"]["pass"],
                          "paired": result["verification"]["paired"],
                          "payback": result["verification"]["payback"]}, indent=2))
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
