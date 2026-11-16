"""Terminal-reward policy search for three atomic Boolean assignments.

World bit i is input register i (A0,A1,B0,B1,C0,C1). Programs execute three
ordinary gates, then emit one or two selected registers. The private oracle
enters only the terminal training scorer and the post-freeze evaluator.
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
import random
import time
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations_with_replacement
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ALL = (1 << 64) - 1
OPS = ("AND", "OR", "XOR", "NAND")
INPUT_NAMES = ("A0", "A1", "B0", "B1", "C0", "C1")
INPUT_MASKS = tuple(sum(((world >> register) & 1) << world for world in range(64))
                    for register in range(6))
TRAIN_WORLDS = tuple(world for world in range(64) if world.bit_count() % 2 == 0)
HELD_OUT_WORLDS = tuple(world for world in range(64) if world.bit_count() % 2)
TRAIN_MASK = sum(1 << world for world in TRAIN_WORLDS)
HELD_OUT_MASK = ALL ^ TRAIN_MASK
SEEDS = (17, 31, 53)
CONTEXTS = tuple(f"c{i}" for i in range(6))
GATE_TOKENS = tuple(tuple((op, left, right) for op in OPS
                         for left, right in combinations_with_replacement(range(6 + index), 2))
                    for index in range(3))
OUTPUT_TOKENS = {
    1: tuple((register,) for register in range(9)),
    2: tuple(combinations_with_replacement(range(9), 2)),
}
# This mapping is deliberately absent from the proposal policy's interface.
_ORACLES = {
    "c0": ((1, 2), (1, 2, 3)),
    "c1": ((0, 1), (3,)),
    "c2": ((0, 2), (1, 2, 3)),
    "c3": ((1, 2), (3,)),
    "c4": ((0, 1), (1, 2, 3)),
    "c5": ((0, 2), (3,)),
}


@dataclass(frozen=True)
class Settings:
    population: int = 96
    generations: int = 128
    elite_fraction: float = 0.125
    smoothing: float = 0.35
    uniform_mix: float = 0.10
    persistent_best: bool = True


FROZEN = Settings()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def proposal_seed(seed, context_id, width):
    # Opaque ID partitions independent fits; it does not encode the oracle pair.
    text = f"atomic-boolean-v1|{seed}|{context_id}|{width}"
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big")


@lru_cache(maxsize=32768)
def execute(program, width):
    registers = list(INPUT_MASKS)
    for index, token in enumerate(program[:3]):
        op, left, right = GATE_TOKENS[index][token]
        a, b = registers[left], registers[right]
        value = {"AND": lambda: a & b, "OR": lambda: a | b,
                 "XOR": lambda: a ^ b, "NAND": lambda: ALL ^ (a & b)}[op]()
        registers.append(value)
    return tuple(registers[tap] for tap in OUTPUT_TOKENS[width][program[3]])


def code_groups(program, width):
    emitted = execute(program, width)
    groups = []
    for code in range(1 << width):
        mask = ALL
        for bit, values in enumerate(emitted):
            mask &= values if (code >> bit) & 1 else ALL ^ values
        groups.append(mask)
    return groups


@lru_cache(maxsize=32768)
def live_gate_indices(program, width):
    live = set()

    def visit(register):
        if register < 6 or register - 6 in live:
            return
        index = register - 6
        live.add(index)
        _, left, right = GATE_TOKENS[index][program[index]]
        visit(left)
        visit(right)

    for register in OUTPUT_TOKENS[width][program[3]]:
        visit(register)
    return tuple(sorted(live))


def program_record(program, width):
    gates = [{"destination": 6 + index, "op": GATE_TOKENS[index][token][0],
              "left": GATE_TOKENS[index][token][1], "right": GATE_TOKENS[index][token][2]}
             for index, token in enumerate(program[:3])]
    outputs = OUTPUT_TOKENS[width][program[3]]
    text = "; ".join(f"r{g['destination']}={g['op']}(r{g['left']},r{g['right']})" for g in gates)
    text += "; emit(" + ",".join(f"r{register}" for register in outputs) + ")"
    live = live_gate_indices(program, width)
    return {"tokens": program, "gates": gates, "outputs": outputs,
            "text": text, "live_gate_indices": live, "live_gates": len(live),
            "width": width, "sha256": digest({"gates": gates, "outputs": outputs})}


def oracle_labels(context_id, worlds):
    pair, queries = _ORACLES[context_id]
    masks = {query: 0 for query in queries}
    for world in worlds:
        possible = [((world >> (2 * pair[0] + h)) & 1)
                    & ((world >> (2 * pair[1] + h)) & 1) for h in (0, 1)]
        for query in queries:
            answer = int(any(possible[h] for h in (0, 1) if query & (1 << h)))
            masks[query] |= answer << world
    return masks


class TrainingOracle:
    """The policy receives only terminal correctness, never these labels."""

    def __init__(self, context_id):
        self.labels = oracle_labels(context_id, TRAIN_WORLDS)
        self.total = len(TRAIN_WORLDS) * len(self.labels)
        self.cache = {}

    def score(self, program, width):
        key = (program, width)
        if key not in self.cache:
            correct = 0
            for group in code_groups(program, width):
                group &= TRAIN_MASK
                count = group.bit_count()
                for labels in self.labels.values():
                    ones = (group & labels).bit_count()
                    correct += max(ones, count - ones)
            self.cache[key] = correct
        return self.cache[key]

    def decoder(self, program, width):
        predictions, counts = {}, {}
        groups = [group & TRAIN_MASK for group in code_groups(program, width)]
        for query, labels in self.labels.items():
            rows = [{"ones": (group & labels).bit_count(),
                     "zeros": group.bit_count() - (group & labels).bit_count()}
                    for group in groups]
            predictions[str(query)] = [int(row["ones"] > row["zeros"]) for row in rows]
            counts[str(query)] = rows
        return predictions, counts


class CategoricalPolicy:
    """Generic grammar only. Oracle context, pair and query are not arguments."""

    def __init__(self, width):
        self.sizes = tuple(len(tokens) for tokens in GATE_TOKENS) + (len(OUTPUT_TOKENS[width]),)
        self.probabilities = [[1.0 / size] * size for size in self.sizes]
        self.updates = 0

    def sample(self, rng, count):
        cumulative = []
        for probabilities in self.probabilities:
            cdf, total = [], 0.0
            for probability in probabilities:
                total += probability
                cdf.append(total)
            cdf[-1] = 1.0
            cumulative.append(cdf)
        return [tuple(bisect.bisect_left(cdf, rng.random()) for cdf in cumulative)
                for _ in range(count)]

    def update(self, elites, settings):
        old = [values[:] for values in self.probabilities]
        for position, size in enumerate(self.sizes):
            counts = Counter(program[position] for program in elites)
            mixed = [(1 - settings.uniform_mix)
                     * ((1 - settings.smoothing) * old[position][token]
                        + settings.smoothing * counts[token] / len(elites))
                     + settings.uniform_mix / size for token in range(size)]
            normalizer = sum(mixed)
            self.probabilities[position] = [value / normalizer for value in mixed]
            if (min(self.probabilities[position]) < settings.uniform_mix / size * (1 - 1e-10)
                    or abs(sum(self.probabilities[position]) - 1) > 1e-10):
                raise ValueError("Categorical update lost its full-support probability law")
        self.updates += 1
        return sum(abs(a - b) for previous, following in zip(old, self.probabilities, strict=True)
                   for a, b in zip(previous, following, strict=True))

    def summary(self):
        return {
            "sha256": digest(self.probabilities),
            "l1_from_initial": sum(abs(value - 1 / size)
                                   for size, values in zip(self.sizes, self.probabilities, strict=True)
                                   for value in values),
            "entropy_bits": -sum(value * math.log2(value)
                                 for values in self.probabilities for value in values),
            "minimum_probability": min(min(values) for values in self.probabilities),
        }


def retention_rank(program, width, correct):
    return (-correct, len(live_gate_indices(program, width)), program)


def search(width, method, seed, score, total, settings):
    """One terminal-reward search; the sampler sees rewards only via elites."""
    policy = CategoricalPolicy(width)
    initial_policy = policy.summary()
    rng = random.Random(seed)
    best_program, best_correct, first_exact = None, -1, None
    trace, seen = [], set()
    evaluations = 0
    elite_count = max(1, math.ceil(settings.population * settings.elite_fraction))
    for generation in range(settings.generations):
        population = policy.sample(rng, settings.population)
        if generation == 0:
            initial_population_sha256 = digest(population)
        scored = []
        for program in population:
            correct = score(program, width)
            evaluations += 1
            seen.add(program)
            scored.append((program, correct))
            if (best_program is None or retention_rank(program, width, correct)
                    < retention_rank(best_program, width, best_correct)):
                best_program, best_correct = program, correct
            if correct == total and first_exact is None:
                first_exact = {"evaluation": evaluations, "generation": generation,
                               "program": program_record(program, width)}
        ranked = sorted(scored, key=lambda row: retention_rank(row[0], width, row[1]))
        elites = [program for program, _ in ranked[:elite_count]]
        if (settings.persistent_best and best_program not in elites
                and retention_rank(best_program, width, best_correct)
                < retention_rank(ranked[elite_count - 1][0], width, ranked[elite_count - 1][1])):
            elites[-1] = best_program
        delta = policy.update(elites, settings) if method == "cem" else 0.0
        distribution = policy.summary()
        trace.append({"generation": generation, "evaluations": evaluations,
                      "best_training_correct": best_correct, "training_total": total,
                      "generation_best_correct": ranked[0][1],
                      "sum_training_correct": sum(correct for _, correct in scored),
                      "exact_samples": sum(correct == total for _, correct in scored),
                      "best_live_gates": len(live_gate_indices(best_program, width)),
                      "distribution_step_l1": delta, **distribution})
    final_policy = policy.summary()
    if method == "cem" and (not policy.updates or final_policy["sha256"] == initial_policy["sha256"]):
        raise ValueError("Terminal-reward fitting did not change the initialized policy")
    if method == "blind" and (policy.updates or final_policy != initial_policy):
        raise ValueError("Blind sampling changed its grammar distribution")
    return best_program, {
        "evaluations": evaluations, "unique_programs": len(seen),
        "rewarded_world_query_pairs": evaluations * total,
        "first_exact_sample": first_exact,
        "proposal_seed": seed, "initial_population_sha256": initial_population_sha256,
        "initial_policy_sha256": initial_policy["sha256"],
        "final_policy_sha256": final_policy["sha256"],
        "policy_updates": policy.updates, "distribution_summary": final_policy,
        "best_training_correct": best_correct, "training_total": total, "trace": trace,
    }


def evaluate(program, width, decoder, context_id):
    groups = code_groups(program, width)
    labels = oracle_labels(context_id, range(64))
    queries = {}
    correct_masks = []
    for query, truth in labels.items():
        prediction = 0
        for code, answer in enumerate(decoder[str(query)]):
            if answer:
                prediction |= groups[code]
        correct_masks.append(ALL ^ (truth ^ prediction))
        queries[str(query)] = {"prediction_mask_hex": f"{prediction:016x}",
                               "truth_mask_hex": f"{truth:016x}"}
    result = {"codes_by_world": [sum(((values >> world) & 1) << bit
                                     for bit, values in enumerate(execute(program, width)))
                                  for world in range(64)], "queries": queries}
    for name, mask in (("train", TRAIN_MASK), ("held_out", HELD_OUT_MASK), ("all", ALL)):
        correct = sum((values & mask).bit_count() for values in correct_masks)
        total = mask.bit_count() * len(labels)
        result[name] = {"correct": correct, "total": total, "accuracy": correct / total}
    return result


def run_seed(seed, settings=FROZEN, context_ids=CONTEXTS):
    if seed not in SEEDS:
        raise ValueError(f"Frozen seeds are {SEEDS}")
    started = time.perf_counter()
    records = []
    for context_id in context_ids:
        oracle = TrainingOracle(context_id)
        methods = {method: {"widths": {}} for method in ("cem", "blind")}
        for width in (1, 2):
            draw_seed = proposal_seed(seed, context_id, width)
            for method in ("cem", "blind"):
                program, training = search(width, method, draw_seed, oracle.score, oracle.total, settings)
                decoder, counts = oracle.decoder(program, width)
                code = program_record(program, width)
                frozen = digest({"program": code, "decoder": decoder})
                methods[method]["widths"][str(width)] = {
                    "program": code, "decoder": decoder, "decoder_training_counts": counts,
                    "decoder_text": "; ".join(f"query {query}: code lookup {values}"
                                                 for query, values in decoder.items()),
                    "search": training, "frozen_program_decoder_sha256": frozen,
                }
            if (methods["cem"]["widths"][str(width)]["search"]["initial_population_sha256"]
                    != methods["blind"]["widths"][str(width)]["search"]["initial_population_sha256"]):
                raise ValueError("CEM and blind initial populations were not coupled")
        for method, record in methods.items():
            def rank(width):
                item = record["widths"][str(width)]
                return (-item["search"]["best_training_correct"], width,
                        item["program"]["live_gates"], item["program"]["tokens"])
            chosen = min((1, 2), key=rank)
            record["chosen_width"] = chosen
            record["chosen_program_sha256"] = record["widths"][str(chosen)]["program"]["sha256"]
            record["selection_rank"] = rank(chosen)
        records.append({"context_id": context_id, "query_ids": sorted(oracle.labels),
                        "methods": methods})
    fit_seconds = time.perf_counter() - started
    # All program/width choices above precede every held-out label read below.
    evaluation_started = time.perf_counter()
    for context in records:
        for record in context["methods"].values():
            for width, item in record["widths"].items():
                program = tuple(item["program"]["tokens"])
                item["evaluation"] = evaluate(program, int(width), item["decoder"], context["context_id"])
                following = digest({"program": item["program"], "decoder": item["decoder"]})
                if following != item["frozen_program_decoder_sha256"]:
                    raise ValueError("Evaluation altered the selected program or decoder")
                item["post_evaluation_program_decoder_sha256"] = following
                if item["evaluation"]["train"]["correct"] != item["search"]["best_training_correct"]:
                    raise ValueError("Frozen decoder did not reproduce terminal training reward")
    source_paths = (Path(__file__), HERE / "contract.json",
                    ROOT / "research/ATOMIC-FOLD-20261114-001/preregistration.md")
    return {
        "schema_version": 1, "seed": seed,
        "settings": settings.__dict__ | {
            "terminal_retention": "training errors, live gates, canonical token tuple",
            "width_selection": "training errors, emitted width, live gates, canonical token tuple",
            "elite_retention": "one best-so-far insertion if absent and better than the worst elite",
            "seed_derivation": "first 8 SHA256 bytes of atomic-boolean-v1|seed|opaque-context|width",
            "training_world_query_cost_includes_duplicate_candidates": True,
        },
        "grammar": {"input_registers": INPUT_NAMES, "operations": OPS,
                    "gate_token_counts": [len(tokens) for tokens in GATE_TOKENS],
                    "output_token_counts": {str(width): len(tokens) for width, tokens in OUTPUT_TOKENS.items()},
                    "operands_and_taps": "unordered with repetition; outputs use ascending register order",
                    "code_encoding": "code bit k is outputs[k]", "assignments": 3},
        "partitions": {"train_worlds": TRAIN_WORLDS, "held_out_worlds": HELD_OUT_WORLDS},
        "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in source_paths},
        "fit_seconds": fit_seconds, "evaluation_seconds": time.perf_counter() - evaluation_started,
        "elapsed_seconds": time.perf_counter() - started, "contexts": records,
        "execution_cache": execute.cache_info()._asdict(),
    }


def setup(params):
    if params:
        raise ValueError("The frozen primary panel accepts no runner parameters")


def cases():
    for seed in SEEDS:
        yield f"seed-{seed}", {"seed": seed}


def run(case_id, payload):
    return run_seed(int(payload["seed"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, choices=SEEDS, default=17)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    result = run_seed(args.seed, Settings(population=12, generations=3), ("c0",)) if args.smoke else run_seed(args.seed)
    if args.smoke:
        result = {"seed": result["seed"], "settings": result["settings"],
                  "elapsed_seconds": result["elapsed_seconds"], "source_sha256": result["source_sha256"],
                  "smoke": {method: {"chosen_width": item["chosen_width"],
                                     "widths": {width: {"evaluations": row["search"]["evaluations"],
                                                        "policy_updates": row["search"]["policy_updates"],
                                                        "distribution_l1": row["search"]["distribution_summary"]["l1_from_initial"],
                                                        "frozen_unchanged": row["frozen_program_decoder_sha256"] == row["post_evaluation_program_decoder_sha256"]}
                                                for width, row in item["widths"].items()}}
                            for method, item in result["contexts"][0]["methods"].items()}}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
