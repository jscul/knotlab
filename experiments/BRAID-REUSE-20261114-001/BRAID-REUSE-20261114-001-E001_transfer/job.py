"""Paired primitive program search, with optional calls to one frozen crossing.

Every fitness proposal executes literal guarded NOT/AND/AND/XOR operations on
packed raw bit lanes; no image or reward cache bypasses execution. The ten
training runs finish and are hashed before any held-out target is scored.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import random
import time
import zlib
from dataclasses import asdict, dataclass
from itertools import permutations, product
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ACQUISITION = ROOT / "artifacts/BRAID-ACTIONS-20261114-001/BRAID-ACTIONS-20261114-001-E002_rewarded_actions/sequence_checkpoint.json"
ACQUISITION_SHA256 = "0314efd099e3a54c3791b60968587f1e1edb4e0112ea238eab84fb6ca1a8c8a9"
FORWARD_SHA256 = "a740b9a93061a75b78ce24a135b5adc94ca55a0206872c7b69e97117837f4246"
MASKS = (8, 4, 2, 1)
WORDS = tuple((x << 2) | y for x, y in product(range(3), repeat=2))
LOCAL_ACTIONS = tuple((target, guard) for target in MASKS for guard in WORDS
                      if not guard & target and (guard | target) in WORDS)
ORDERED_PAIRS = tuple(permutations(range(3), 2))
STATES = tuple(product(range(3), repeat=3))
TRAIN_STATES = tuple(state for state in STATES if state[2] != (state[0] + state[1] + 1) % 3)
HELD_STATES = tuple(state for state in STATES if state not in TRAIN_STATES)
COUNTER_ORDER = ("guarded_toggles", "NOT", "AND", "XOR")


def canonical_sha256(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class Config:
    seeds: tuple[int, ...] = (17, 29, 43, 59, 71)
    islands: int = 32
    generations: int = 512
    brood: int = 12
    maximum_expanded_length: int = 36
    initial_minimum: int = 2
    initial_maximum: int = 12
    restart_period: int = 32
    call_denominator: int = 13

    @property
    def evaluations(self):
        return self.islands * (1 + self.generations * self.brood)


FROZEN = Config()


class Grammar:
    """The proposal/execution language has no target or label input."""

    def __init__(self):
        data = ACQUISITION.read_bytes()
        if hashlib.sha256(data).hexdigest() != ACQUISITION_SHA256:
            raise ValueError("The frozen acquisition bundle changed")
        self.forward = tuple(json.loads(data)["forward"])
        if len(LOCAL_ACTIONS) != 12 or len(self.forward) != 12:
            raise ValueError("The declared local alphabet or frozen crossing is not twelve actions")
        if hashlib.sha256(bytes(self.forward)).hexdigest() != FORWARD_SHA256:
            raise ValueError("The frozen forward instruction sequence changed")
        descriptors, raw_counts = [], []
        for first, second in ORDERED_PAIRS:
            indices = (2 * first, 2 * first + 1, 2 * second, 2 * second + 1)
            for target, guard in LOCAL_ACTIONS:
                target_index = indices[MASKS.index(target)]
                literals = [(indices[i], int(not (guard & mask)))
                            for i, mask in enumerate(MASKS) if mask != target]
                descriptors.append((target_index, *literals[0], *literals[1], *literals[2]))
                raw_counts.append((1, sum(negate for _, negate in literals), 2, 1))
        self.descriptors = tuple(descriptors)
        self.raw_counts = tuple(raw_counts)
        self.expansions = tuple((token,) for token in range(72)) + tuple(
            tuple(12 * pair + action for action in self.forward) for pair in range(6))
        self.token_lengths = tuple(map(len, self.expansions))
        if sum(self.counts(self.expansions[72])[1:]) != 60:
            raise ValueError("The frozen call no longer costs sixty primitive gates")

    def expand(self, genome):
        return tuple(raw for token in genome for raw in self.expansions[token])

    def counts(self, expanded):
        return (len(expanded), sum(self.raw_counts[token][1] for token in expanded),
                2 * len(expanded), len(expanded))

    def length(self, genome):
        return sum(self.token_lengths[token] for token in genome)

    def execute_packed(self, expanded, initial_bits, lane_mask):
        bits = list(initial_bits)
        for token in expanded:
            target, a, not_a, b, not_b, c, not_c = self.descriptors[token]
            left, middle, right = bits[a], bits[b], bits[c]
            if not_a:
                left ^= lane_mask
            if not_b:
                middle ^= lane_mask
            if not_c:
                right ^= lane_mask
            enabled = left & middle
            enabled &= right
            bits[target] ^= enabled
        return tuple(bits)

    def execute_scalar(self, expanded, state):
        bits = [bit for label in state for bit in (label >> 1, label & 1)]
        for token in expanded:
            target, a, not_a, b, not_b, c, not_c = self.descriptors[token]
            left, middle, right = bits[a], bits[b], bits[c]
            if not_a:
                left ^= 1
            if not_b:
                middle ^= 1
            if not_c:
                right ^= 1
            enabled = left & middle
            enabled &= right
            bits[target] ^= enabled
        output = tuple(2 * bits[2 * i] + bits[2 * i + 1] for i in range(3))
        if any(value > 2 for value in output):
            raise ValueError("A guarded action left the legal ternary encoding")
        return output

    def draw_token(self, rng):
        pair, action, call = rng.randrange(6), rng.randrange(12), rng.randrange(13) == 0
        return 12 * pair + action, 72 + pair, call

    def random_program(self, rng, allow_calls, config, initial=False):
        length = rng.randint(config.initial_minimum, config.initial_maximum)
        draws = [self.draw_token(rng) for _ in range(length)]
        genome = [raw for raw, _, _ in draws]
        expanded = length
        for index, (_, call, requested) in enumerate(draws):
            if allow_calls and not initial and requested and expanded + 11 <= config.maximum_expanded_length:
                genome[index] = call
                expanded += 11
        return tuple(genome)

    def mutate(self, parent, rng, allow_calls, config):
        # Fixed draws even for delete/relocate/empty and irrespective of arm.
        kind, a, b = rng.randrange(100), rng.random(), rng.random()
        raw, call, requested = self.draw_token(rng)
        token = call if allow_calls and requested else raw
        n, expanded = len(parent), self.length(parent)
        if not n:
            return (token,)
        if kind < 30 and expanded < config.maximum_expanded_length:
            if expanded + self.token_lengths[token] > config.maximum_expanded_length:
                token = raw
            index = int(a * (n + 1))
            return parent[:index] + (token,) + parent[index:]
        index = int(a * n)
        if 30 <= kind < 55:
            return parent[:index] + parent[index + 1:]
        if kind < 85:  # Over-cap raw insertion is a substitution, as declared.
            if expanded - self.token_lengths[parent[index]] + self.token_lengths[token] > config.maximum_expanded_length:
                token = raw
            return parent[:index] + (token,) + parent[index + 1:]
        without = parent[:index] + parent[index + 1:]
        destination = int(b * n)
        return without[:destination] + (parent[index],) + without[destination:]


def pack_states(states):
    return tuple(sum(((state[register] >> shift) & 1) << lane for lane, state in enumerate(states))
                 for register in range(3) for shift in (1, 0))


def target_answer(state):
    # Private terminal oracle only; never called by grammar/proposal routines.
    return int(len(set(state)) in (1, 3))


def make_oracle(states):
    mask = (1 << len(states)) - 1
    positives = sum(target_answer(state) << lane for lane, state in enumerate(states))
    negatives = mask ^ positives

    def score(predicted_positives):
        return 2 * (predicted_positives & positives).bit_count() + ((mask ^ predicted_positives) & negatives).bit_count()

    return score, 2 * positives.bit_count() + negatives.bit_count()


def charge_record(packed, evaluations, lanes):
    vector = dict(zip(COUNTER_ORDER, packed, strict=True))
    vector["Boolean_gates"] = sum(packed[1:])
    logical = {key: value * lanes for key, value in vector.items()}
    return {"packed_program": vector, "logical_program": logical,
            "packed_terminal_readout": {"OR": evaluations, "NOT": evaluations, "Boolean_gates": 2 * evaluations},
            "logical_terminal_readout": {"OR": evaluations * lanes, "NOT": evaluations * lanes,
                                         "Boolean_gates": 2 * evaluations * lanes},
            "fitness_evaluations": evaluations, "lanes": lanes}


def genome_record(grammar, genome):
    expanded = grammar.expand(genome)
    return {"genome": list(genome), "genome_hex": bytes(genome).hex(),
            "genome_sha256": hashlib.sha256(bytes(genome)).hexdigest(),
            "exposed_length": len(genome), "macro_calls": sum(token >= 72 for token in genome),
            "expanded_guarded_length": len(expanded),
            "inference_counts_per_input": dict(zip(COUNTER_ORDER, grammar.counts(expanded), strict=True)),
            "expanded_program": [{"pair": ORDERED_PAIRS[token // 12], "action": token % 12} for token in expanded]}


class PerfectLog:
    """Lossless first occurrence of every training-perfect exact genome."""

    def __init__(self):
        self.seen, self.chunks = set(), []
        self.compressor = zlib.compressobj(level=6)
        self.total_hits = 0

    def append(self, genome, evaluation, cumulative, elapsed_ns, expanded):
        self.total_hits += 1
        raw = bytes(genome)
        if raw in self.seen:
            return
        self.seen.add(raw)
        row = {"evaluation": evaluation, "genome_hex": raw.hex(),
               "expanded_guarded_length": expanded,
               "macro_calls": sum(token >= 72 for token in genome),
               "cumulative_packed": list(cumulative), "elapsed_ns": elapsed_ns}
        chunk = self.compressor.compress((json.dumps(row, separators=(",", ":")) + "\n").encode())
        if chunk:
            self.chunks.append(chunk)

    def finish(self):
        self.chunks.append(self.compressor.flush())
        compressed = b"".join(self.chunks)
        return {"encoding": "zlib-json-lines-base64", "unique_genomes": len(self.seen),
                "training_perfect_proposals_including_repeats": self.total_hits,
                "coverage": "first occurrence per exact genome; repeat executions remain fully charged",
                "compressed_sha256": hashlib.sha256(compressed).hexdigest(),
                "data": base64.b64encode(compressed).decode()}


def iter_perfect_events(wrapper):
    if wrapper["encoding"] != "zlib-json-lines-base64":
        raise ValueError("Unknown training-hit log encoding")
    raw = base64.b64decode(wrapper["data"], validate=True)
    if hashlib.sha256(raw).hexdigest() != wrapper["compressed_sha256"]:
        raise ValueError("The training-hit log changed")
    for line in zlib.decompress(raw).splitlines():
        yield json.loads(line)


def keeper_record(grammar, keeper, lanes):
    if keeper is None:
        return None
    return genome_record(grammar, keeper["genome"]) | {
        "training_score": keeper["score"], "evaluation": keeper["evaluation"],
        "elapsed_seconds": keeper["elapsed_ns"] / 1e9,
        "cumulative_packed": list(keeper["cumulative"]),
        "charges_to_event": charge_record(keeper["cumulative"], keeper["evaluation"], lanes)}


def search_arm(grammar, config, states, score_function, maximum, seed, condition):
    started = time.perf_counter_ns()
    if condition not in ("raw", "reuse"):
        raise ValueError("The two paired conditions are raw and reuse")
    allow_calls = condition == "reuse"
    variation, selection = random.Random(seed), random.Random(seed + 1)
    initial_bits, lane_mask = pack_states(states), (1 << len(states)) - 1
    evaluations, cumulative, best, first = 0, [0, 0, 0, 0], None, None
    perfect = PerfectLog()
    trajectory = []

    def evaluate(genome):
        nonlocal evaluations, best, first
        expanded = grammar.expand(genome)
        if len(expanded) > config.maximum_expanded_length or (not allow_calls and any(token >= 72 for token in genome)):
            raise ValueError("A proposal violated its frozen action language or expanded cap")
        counts = grammar.counts(expanded)
        output_bits = grammar.execute_packed(expanded, initial_bits, lane_mask)
        # Supplied terminal readout is separate from actor primitive charges.
        predicted = lane_mask ^ (output_bits[4] | output_bits[5])
        score = int(score_function(predicted))
        evaluations += 1
        for index in range(4):
            cumulative[index] += counts[index]
        better = best is None or (score, -len(expanded)) > (best["score"], -best["expanded"])
        if better or score == maximum:
            elapsed = time.perf_counter_ns() - started
            current = {"genome": genome, "score": score, "expanded": len(expanded),
                       "evaluation": evaluations, "cumulative": tuple(cumulative), "elapsed_ns": elapsed}
            if better:
                best = current
            if score == maximum:
                if first is None:
                    first = current
                perfect.append(genome, evaluations, cumulative, elapsed, len(expanded))
        return genome, score, len(expanded)

    initial_programs = [grammar.random_program(variation, allow_calls, config, initial=True)
                        for _ in range(config.islands)]
    initial_hash = canonical_sha256(initial_programs)
    parents = [evaluate(program) for program in initial_programs]

    def record(generation):
        trajectory.append({"generation": generation, "evaluations": evaluations,
                           "best_training_score": best["score"], "best_expanded_length": best["expanded"],
                           "sum_parent_scores": sum(parent[1] for parent in parents),
                           "cumulative_packed": list(cumulative)})

    record(0)
    for generation in range(1, config.generations + 1):
        for island, parent in enumerate(parents):
            candidates = [parent]
            candidates.extend(evaluate(grammar.mutate(parent[0], variation, allow_calls, config))
                              for _ in range(config.brood - 1))
            candidates.append(evaluate(grammar.random_program(variation, allow_calls, config)))
            if generation % config.restart_period == 0:
                parents[island] = candidates[-1]
            else:
                highest = max(candidate[1] for candidate in candidates)
                tied = [candidate for candidate in candidates if candidate[1] == highest]
                parents[island] = tied[int(selection.random() * len(tied))]
        record(generation)
    if evaluations != config.evaluations:
        raise ValueError("The declared full proposal budget was not exhausted")
    log = perfect.finish()
    first_record = keeper_record(grammar, first, len(states))
    selected_record = keeper_record(grammar, best, len(states))
    elapsed = (time.perf_counter_ns() - started) / 1e9
    return {"seed": seed, "condition": condition, "evaluations": evaluations,
            "maximum_training_score": maximum, "elapsed_seconds": elapsed,
            "initial_population_sha256": initial_hash,
            "variation_rng_final_sha256": canonical_sha256(variation.getstate()),
            "selection_rng_final_sha256": canonical_sha256(selection.getstate()),
            "first_train_perfect": first_record, "training_selected": selected_record,
            "train_perfect_events": log, "trajectory": trajectory,
            "charges": charge_record(cumulative, evaluations, len(states)),
            "fitness_cache_hits": 0,
            "parent_choices_including_restarts": config.generations * config.islands}


def _event_record(grammar, event, lanes):
    genome = tuple(bytes.fromhex(event["genome_hex"]))
    if grammar.length(genome) != event["expanded_guarded_length"] or sum(token >= 72 for token in genome) != event["macro_calls"]:
        raise ValueError("A stored training-hit event disagreed with its genome")
    return genome_record(grammar, genome) | {
        "evaluation": event["evaluation"], "elapsed_seconds": event["elapsed_ns"] / 1e9,
        "cumulative_packed": event["cumulative_packed"],
        "charges_to_event": charge_record(event["cumulative_packed"], event["evaluation"], lanes)}


def assess_after_freeze(grammar, arms):
    """Held labels are constructed here only, after all ten training arms seal."""
    held_bits, held_mask = pack_states(HELD_STATES), (1 << len(HELD_STATES)) - 1
    held_target = sum(target_answer(state) << lane for lane, state in enumerate(HELD_STATES))
    results = []
    for arm in arms:
        cache, held_cumulative = {}, [0, 0, 0, 0]
        held_executions = 0

        def held_score(genome_hex):
            nonlocal held_executions
            if genome_hex not in cache:
                genome = tuple(bytes.fromhex(genome_hex))
                expanded = grammar.expand(genome)
                bits = grammar.execute_packed(expanded, held_bits, held_mask)
                predicted = held_mask ^ (bits[4] | bits[5])
                correct = len(HELD_STATES) - (predicted ^ held_target).bit_count()
                cache[genome_hex] = correct
                held_executions += 1
                for index, value in enumerate(grammar.counts(expanded)):
                    held_cumulative[index] += value
            return cache[genome_hex]

        first_validated = None
        distribution = {str(score): 0 for score in (3, 5, 7, 9)}
        event_count = 0
        for event in iter_perfect_events(arm["train_perfect_events"]):
            correct = held_score(event["genome_hex"])
            if correct not in (3, 5, 7, 9):
                raise ValueError("A reversible training-perfect classifier violated held-positive cardinality")
            distribution[str(correct)] += 1
            event_count += 1
            if correct == len(HELD_STATES) and first_validated is None:
                first_validated = _event_record(grammar, event, len(TRAIN_STATES)) | {
                    "training_score": arm["maximum_training_score"], "validated_exact": True,
                    "held_correct": correct, "held_total": len(HELD_STATES),
                    "selection_role": "retrospective event only; never deployed by held score"}
        if event_count != arm["train_perfect_events"]["unique_genomes"]:
            raise ValueError("Training-perfect log count changed")

        def scored_keeper(record):
            if record is None:
                return None
            correct = held_score(record["genome_hex"])
            return record | {"held_correct": correct, "held_total": len(HELD_STATES),
                             "validated_exact": record["training_score"] == arm["maximum_training_score"]
                             and correct == len(HELD_STATES)}

        first_train = scored_keeper(arm["first_train_perfect"])
        selected = scored_keeper(arm["training_selected"])
        replay_cache = {}

        def raw_replay(record):
            if record is None:
                return None
            key = record["genome_hex"]
            if key not in replay_cache:
                expanded = grammar.expand(tuple(bytes.fromhex(key)))
                replay_cache[key] = [{"input": state, "output": output,
                                      "prediction": int(output[2] == 0), "target": target_answer(state)}
                                     for state in STATES for output in (grammar.execute_scalar(expanded, state),)]
            rows = replay_cache[key]
            return {"rows": rows, "correct": sum(row["prediction"] == row["target"] for row in rows), "total": 27}

        replays = {"first_train_perfect": raw_replay(first_train), "training_selected": raw_replay(selected),
                   "retrospective_first_validated": raw_replay(first_validated)}
        replay_counts = [0, 0, 0, 0]
        for genome_hex in replay_cache:
            expanded = grammar.expand(tuple(bytes.fromhex(genome_hex)))
            for index, value in enumerate(grammar.counts(expanded)):
                replay_counts[index] += len(STATES) * value
        if first_validated is not None and replays["retrospective_first_validated"]["correct"] != 27:
            raise ValueError("Packed held validation disagreed with literal scalar replay")
        if first_train is not None and replays["first_train_perfect"]["correct"] != 18 + first_train["held_correct"]:
            raise ValueError("A first training-perfect keeper did not replay exactly on training")
        censor = first_validated is None
        results.append({"seed": arm["seed"], "condition": arm["condition"],
                        "first_train_perfect": first_train, "training_selected": selected,
                        "retrospective_first_validated": first_validated,
                        "right_censored": censor,
                        "capped_evaluation": arm["evaluations"] if censor else first_validated["evaluation"],
                        "capped_elapsed_seconds": arm["elapsed_seconds"] if censor else first_validated["elapsed_seconds"],
                        "capped_charges": arm["charges"] if censor else first_validated["charges_to_event"],
                        "unique_train_perfect_held_score_counts": distribution,
                        "offline_held_executions": held_executions,
                        "offline_held_charges": charge_record(held_cumulative, held_executions, len(HELD_STATES)),
                        "offline_scalar_replay_charges": dict(zip(COUNTER_ORDER, replay_counts, strict=True)),
                        "offline_scalar_point_executions": len(replay_cache) * len(STATES),
                        "offline_scalar_readout_equality_comparisons": len(replay_cache) * len(STATES),
                        "raw_replays": replays})
    return results


def run_all():
    started = time.perf_counter()
    grammar = Grammar()
    score, maximum = make_oracle(TRAIN_STATES)
    if len(TRAIN_STATES) != 18 or len(HELD_STATES) != 9 or maximum != 24:
        raise ValueError("The frozen task split or terminal reward changed")
    arms = []
    for index, seed in enumerate(FROZEN.seeds):
        order = ("raw", "reuse") if index % 2 == 0 else ("reuse", "raw")
        pair = []
        for condition in order:
            record = search_arm(grammar, FROZEN, TRAIN_STATES, score, maximum, seed, condition)
            record["serial_run_index"] = len(arms)
            arms.append(record)
            pair.append(record)
        for key in ("initial_population_sha256", "variation_rng_final_sha256", "selection_rng_final_sha256"):
            if pair[0][key] != pair[1][key]:
                raise ValueError(f"The paired search lost common {key}")
    acquisition = {"bundle_sha256": ACQUISITION_SHA256, "forward_action_bytes_sha256": FORWARD_SHA256,
                   "forward_action_ids": grammar.forward,
                   "frozen_call_counts_per_input": dict(zip(COUNTER_ORDER, grammar.counts(grammar.expansions[72]), strict=True)),
                   "retrained": False, "acquisition_cost": "reconstructed independently; not part of target search"}
    config = asdict(FROZEN) | {"evaluations_per_arm": FROZEN.evaluations,
                              "conditions": ["raw", "reuse"], "ordered_pairs": ORDERED_PAIRS,
                              "raw_token": "12*pair_index+local_action_id", "call_token": "72+pair_index",
                              "initialization": "identical all-raw genomes; all later sites draw a one-in-thirteen call flag",
                              "mutation_percentages": {"insert": 30, "delete": 25, "substitute": 30, "relocate": 15},
                              "over_cap": "same raw token fallback; over-cap raw insertion substitutes",
                              "parent_selection": "maximum training reward, uniform ties; periodic independent child",
                              "keeper_selection": "training reward, shorter expanded guarded length, first encounter",
                              "cost_order": COUNTER_ORDER,
                              "source_state_encoding": "registers x,y,z each high/low bits encoding 00,01,10"}
    # This binding is made before constructing/scoring any held-out target.
    training_payload = {"config": config, "acquisition": acquisition, "arms": arms}
    frozen = canonical_sha256(training_payload)
    fit_seconds = time.perf_counter() - started
    post_started = time.perf_counter()
    post = assess_after_freeze(grammar, arms)
    if canonical_sha256(training_payload) != frozen:
        raise ValueError("Held-out replay changed frozen training records")
    files = (Path(__file__), HERE / "contract.json", ROOT / "research/BRAID-REUSE-20261114-001/preregistration.md")
    return training_payload | {"schema_version": 1, "frozen_training_sha256": frozen,
                               "post_freeze": post, "train_states": TRAIN_STATES, "held_states": HELD_STATES,
                               "runtime_seconds": {"ten_serial_fits": fit_seconds,
                                                   "post_freeze": time.perf_counter() - post_started,
                                                   "total": time.perf_counter() - started},
                               "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                                 for path in files}}


def setup(params):
    if params:
        raise ValueError("The frozen paired panel accepts no runner parameters")


def cases():
    yield "five-paired-seeds-serial", {}


def run(case_id, payload):
    if payload:
        raise ValueError("The one sequential run has an empty payload")
    return run_all()


def smoke():
    grammar = Grammar()
    lanes, mask = pack_states(STATES), (1 << len(STATES)) - 1
    comparisons = 0
    physical_images = set()
    for token in range(78):
        expanded = grammar.expand((token,))
        packed = grammar.execute_packed(expanded, lanes, mask)
        scalar = [grammar.execute_scalar(expanded, state) for state in STATES]
        decoded = [tuple(2 * ((packed[2 * r] >> i) & 1) + ((packed[2 * r + 1] >> i) & 1)
                         for r in range(3)) for i in range(27)]
        if decoded != scalar:
            raise ValueError("Packed raw Boolean execution disagreed with literal scalar execution")
        if token < 72:
            physical_images.add(tuple(scalar))
        comparisons += 27
    if len(physical_images) != 36:
        raise ValueError("The seventy-two directed primitive names no longer have thirty-six effects")
    # Synthetic reward and synthetic input panel only; no target oracle call.
    toy = Config(seeds=(0,), islands=2, generations=2, brood=3)
    states = ((0, 0, 0), (1, 2, 1))
    records = [search_arm(grammar, toy, states, lambda prediction: int(bool(prediction & 1)), 1, 0, condition)
               for condition in ("raw", "reuse")]
    for key in ("initial_population_sha256", "variation_rng_final_sha256", "selection_rng_final_sha256"):
        if records[0][key] != records[1][key]:
            raise ValueError("Synthetic paired common randomness diverged")
    for record in records:
        if len(list(iter_perfect_events(record["train_perfect_events"]))) != record["train_perfect_events"]["unique_genomes"]:
            raise ValueError("Synthetic hit-log compression was not lossless")
    return {"smoke_only_no_target_fit": True, "primitive_and_call_scalar_comparisons": comparisons,
            "raw_names": 72, "physical_raw_behaviors": len(physical_images),
            "toy_evaluations_per_arm": toy.evaluations,
            "toy_first_train_perfect": [None if record["first_train_perfect"] is None else {
                key: record["first_train_perfect"][key] for key in
                ("evaluation", "genome", "macro_calls", "expanded_guarded_length", "cumulative_packed")}
                                       for record in records],
            "actions_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    print(json.dumps(smoke() if args.smoke else run_all(), sort_keys=True))


if __name__ == "__main__":
    main()
