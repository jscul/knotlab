"""Matched whole-program mutation, using E001's pinned language and evaluator.

Guided groups retain a parent by terminal training correctness, with uniform
ties. Neutral groups retain one uniformly. Both report their best scored
program using E001's unchanged training-only retention and width rules.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import sys
import time
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE.parent / "ATOMIC-FOLD-20261114-001-E001_atomic_actions" / "job.py"
SOURCE_SHA256 = "15dcc2e96614d9dd3dd641f7f0e852296f465b15b8bace3fe7ae7177723f8ab1"
RAW = ROOT / "artifacts/ATOMIC-FOLD-20261114-001/ATOMIC-FOLD-20261114-001-E001_atomic_actions/results.jsonl"
RAW_SHA256 = "6180766f76666d85c2e737c84623e60774f4fc07210c1d1ee758f213e6123a8b"
METHODS = ("guided", "neutral")


@dataclass(frozen=True)
class Settings:
    groups: int = 12
    offspring_per_group: int = 8
    generations: int = 128
    restart_probability: float = 0.125
    two_position_probability: float = 0.25
    field_edit_probability: float = 0.5

    @property
    def population(self):
        return self.groups * self.offspring_per_group


FROZEN = Settings()


@lru_cache(maxsize=1)
def source():
    actual = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if actual != SOURCE_SHA256:
        raise ValueError(f"E001 producer changed: {actual}")
    name = "atomic_actions_e001_pinned_for_mutation"
    spec = importlib.util.spec_from_file_location(name, SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=1)
def expected_initial_hashes():
    raw = RAW.read_bytes()
    if hashlib.sha256(raw).hexdigest() != RAW_SHA256:
        raise ValueError("The closed E001 raw evidence changed")
    result = {}
    for line in raw.splitlines():
        row = json.loads(line)
        if row["status"] != "ok":
            raise ValueError("E001 has an unsuccessful saved seed")
        seed = row["result"]["seed"]
        for context in row["result"]["contexts"]:
            for width in (1, 2):
                search = context["methods"]["blind"]["widths"][str(width)]["search"]
                key = (seed, context["context_id"], width)
                if key in result:
                    raise ValueError("Duplicate E001 initial population")
                result[key] = search["initial_population_sha256"]
    if len(result) != 36:
        raise ValueError("All 36 E001 initial population hashes are required")
    return result


def initial_population(seed, context_id, width):
    base = source()
    draw_seed = base.proposal_seed(seed, context_id, width)
    rng = random.Random(draw_seed)
    population = base.CategoricalPolicy(width).sample(rng, 96)
    actual = base.digest(population)
    expected = expected_initial_hashes()[seed, context_id, width]
    if actual != expected:
        raise ValueError("The full initial population differs from saved E001 blind search")
    return population, rng, actual, draw_seed


def check_all_initial_populations():
    base = source()
    checked = []
    for seed in base.SEEDS:
        for context_id in base.CONTEXTS:
            for width in (1, 2):
                _, _, actual, _ = initial_population(seed, context_id, width)
                checked.append({"seed": seed, "context_id": context_id,
                                "width": width, "sha256": actual})
    return checked


def different_integer(rng, size, old):
    value = rng.randrange(size - 1)
    return value + (value >= old)


class MutationKernel:
    """Grammar, parent and randomness only; no context or reward argument."""

    def __init__(self, width, settings):
        base = source()
        self.width, self.settings = width, settings
        self.gates, self.outputs = base.GATE_TOKENS, base.OUTPUT_TOKENS[width]
        self.sizes = tuple(len(tokens) for tokens in self.gates) + (len(self.outputs),)
        self.gate_indices = tuple({token: index for index, token in enumerate(tokens)}
                                  for tokens in self.gates)
        self.output_indices = {token: index for index, token in enumerate(self.outputs)}
        self.operations = base.OPS
        self.events = Counter()

    def field_edit(self, position, token, rng):
        if position < 3:
            op, left, right = self.gates[position][token]
            field = rng.randrange(3)
            if field == 0:
                op = self.operations[different_integer(rng, len(self.operations), self.operations.index(op))]
            elif field == 1:
                left = different_integer(rng, 6 + position, left)
            else:
                right = different_integer(rng, 6 + position, right)
            left, right = sorted((left, right))
            return self.gate_indices[position][op, left, right]
        taps = list(self.outputs[token])
        slot = rng.randrange(self.width)
        taps[slot] = different_integer(rng, 9, taps[slot])
        return self.output_indices[tuple(sorted(taps))]

    def propose(self, parent, rng):
        if rng.random() < self.settings.restart_probability:
            self.events["uniform_restart"] += 1
            return tuple(rng.randrange(size) for size in self.sizes)
        count = 2 if rng.random() < self.settings.two_position_probability else 1
        self.events[f"mutate_{count}_positions"] += 1
        program = list(parent)
        for position in sorted(rng.sample(range(4), count)):
            if rng.random() < self.settings.field_edit_probability:
                self.events["changed_field"] += 1
                program[position] = self.field_edit(position, program[position], rng)
            else:
                self.events["fresh_token"] += 1
                program[position] = rng.randrange(self.sizes[position])
        return tuple(program)


def choose_parent(pool, method, rng):
    # One random float per group in either method keeps the mutation streams
    # coupled despite differences in the number of maximum-reward ties.
    if method == "guided":
        maximum = max(correct for _, correct in pool)
        eligible = [row for row in pool if row[1] == maximum]
    elif method == "neutral":
        eligible = pool
    else:
        raise ValueError(f"Unknown method {method!r}")
    return eligible[int(rng.random() * len(eligible))]


def search(seed, context_id, width, method, score, total, settings):
    base = source()
    if settings.population != 96:
        raise ValueError("The controlled initial population has exactly 96 programs")
    population, rng, initial_hash, draw_seed = initial_population(seed, context_id, width)
    kernel = MutationKernel(width, settings)
    parents, trace, seen = [], [], set()
    best_program, best_correct, first_exact = None, -1, None
    evaluations = 0
    for generation in range(settings.generations):
        if generation:
            population = [kernel.propose(parents[group][0], rng)
                          for group in range(settings.groups)
                          for _ in range(settings.offspring_per_group)]
        scored = []
        for program in population:
            correct = score(program, width)
            evaluations += 1
            seen.add(program)
            scored.append((program, correct))
            if (best_program is None or base.retention_rank(program, width, correct)
                    < base.retention_rank(best_program, width, best_correct)):
                best_program, best_correct = program, correct
            if correct == total and first_exact is None:
                first_exact = {"evaluation": evaluations, "generation": generation,
                               "program": base.program_record(program, width)}
        following = []
        for group in range(settings.groups):
            offset = group * settings.offspring_per_group
            pool = scored[offset:offset + settings.offspring_per_group]
            if generation:
                pool = [parents[group]] + pool
            following.append(choose_parent(pool, method, rng))
        if method == "guided" and generation and any(
                new[1] < old[1] for old, new in zip(parents, following, strict=True)):
            raise ValueError("A guided group lost its highest terminal training reward")
        changed = sum(old[0] != new[0] for old, new in zip(parents, following))
        parents = following
        trace.append({
            "generation": generation, "evaluations": evaluations,
            "best_training_correct": best_correct, "training_total": total,
            "generation_best_correct": max(correct for _, correct in scored),
            "sum_training_correct": sum(correct for _, correct in scored),
            "exact_samples": sum(correct == total for _, correct in scored),
            "best_live_gates": len(base.live_gate_indices(best_program, width)),
            "parent_tokens": [program for program, _ in parents],
            "parent_training_correct": [correct for _, correct in parents],
            "changed_parents": changed,
        })
    return best_program, {
        "evaluations": evaluations, "unique_programs": len(seen),
        "rewarded_world_query_pairs": evaluations * total,
        "first_exact_sample": first_exact, "proposal_seed": draw_seed,
        "initial_population_sha256": initial_hash,
        "e001_initial_population_matches": True,
        "best_training_correct": best_correct, "training_total": total,
        "parent_selections": settings.groups * settings.generations,
        "reward_guided_parent_selections": settings.groups * settings.generations if method == "guided" else 0,
        "mutation_event_counts": dict(sorted(kernel.events.items())),
        "final_rng_sha256": base.digest(rng.getstate()), "trace": trace,
    }


def run_seed(seed, settings=FROZEN, context_ids=None):
    started = time.perf_counter()
    base = source()
    if seed not in base.SEEDS:
        raise ValueError(f"Frozen seeds are {base.SEEDS}")
    records = []
    for context_id in base.CONTEXTS if context_ids is None else context_ids:
        oracle = base.TrainingOracle(context_id)
        methods = {method: {"widths": {}} for method in METHODS}
        for width in (1, 2):
            for method in METHODS:
                program, training = search(seed, context_id, width, method,
                                           oracle.score, oracle.total, settings)
                decoder, counts = oracle.decoder(program, width)
                code = base.program_record(program, width)
                frozen = base.digest({"program": code, "decoder": decoder})
                methods[method]["widths"][str(width)] = {
                    "program": code, "decoder": decoder, "decoder_training_counts": counts,
                    "decoder_text": "; ".join(f"query {query}: code lookup {values}"
                                                 for query, values in decoder.items()),
                    "search": training, "frozen_program_decoder_sha256": frozen,
                }
            pair = [methods[method]["widths"][str(width)]["search"] for method in METHODS]
            for field in ("initial_population_sha256", "evaluations", "mutation_event_counts", "final_rng_sha256"):
                if pair[0][field] != pair[1][field]:
                    raise ValueError(f"Guided and neutral search lost matched {field}")
        for record in methods.values():
            def rank(width):
                row = record["widths"][str(width)]
                return (-row["search"]["best_training_correct"], width,
                        row["program"]["live_gates"], row["program"]["tokens"])
            chosen = min((1, 2), key=rank)
            record["chosen_width"] = chosen
            record["chosen_program_sha256"] = record["widths"][str(chosen)]["program"]["sha256"]
            record["selection_rank"] = rank(chosen)
        records.append({"context_id": context_id, "query_ids": sorted(oracle.labels),
                        "methods": methods})
    fit_seconds = time.perf_counter() - started
    evaluation_started = time.perf_counter()
    # Every context, width and retained candidate is frozen before test labels.
    for context in records:
        for record in context["methods"].values():
            for width, item in record["widths"].items():
                item["evaluation"] = base.evaluate(tuple(item["program"]["tokens"]), int(width),
                                                    item["decoder"], context["context_id"])
                following = base.digest({"program": item["program"], "decoder": item["decoder"]})
                if following != item["frozen_program_decoder_sha256"]:
                    raise ValueError("Evaluation changed a retained program or decoder")
                item["post_evaluation_program_decoder_sha256"] = following
                if item["evaluation"]["train"]["correct"] != item["search"]["best_training_correct"]:
                    raise ValueError("Frozen decoder no longer matches terminal training reward")
    paths = (Path(__file__), HERE / "contract.json", SOURCE,
             ROOT / "research/ATOMIC-FOLD-20261114-001/mutation_design.md")
    return {
        "schema_version": 1, "seed": seed,
        "settings": settings.__dict__ | {
            "population": settings.population,
            "parent_selection": "terminal reward with uniform ties; matched neutral uniform selection",
            "changed_field": "uniform operation/left/right or emitted slot, different legal value, canonical reorder",
            "fresh_token": "uniform complete legal alphabet, including the current token",
            "parent_pool": "eight initial candidates; thereafter old parent plus eight scored offspring",
            "reporting_rank": "training errors, live gates, canonical token tuple",
            "width_selection": "training errors, emitted width, live gates, canonical token tuple",
            "initial_population": "exactly the corresponding saved E001 blind population",
            "duplicate_candidates_charged": True,
        },
        "grammar": {"input_registers": base.INPUT_NAMES, "operations": base.OPS,
                    "gate_token_counts": [len(tokens) for tokens in base.GATE_TOKENS],
                    "output_token_counts": {str(width): len(tokens) for width, tokens in base.OUTPUT_TOKENS.items()},
                    "operands_and_taps": "unordered with repetition; outputs use ascending register order",
                    "code_encoding": "code bit k is outputs[k]", "assignments": 3},
        "partitions": {"train_worlds": base.TRAIN_WORLDS, "held_out_worlds": base.HELD_OUT_WORLDS},
        "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in paths} | {str(RAW.relative_to(ROOT)): RAW_SHA256},
        "fit_seconds": fit_seconds, "evaluation_seconds": time.perf_counter() - evaluation_started,
        "elapsed_seconds": time.perf_counter() - started, "contexts": records,
        "execution_cache": base.execute.cache_info()._asdict(),
    }


def setup(params):
    if params:
        raise ValueError("The frozen mutation comparison has no runner parameters")
    source()
    expected_initial_hashes()


def cases():
    for seed in source().SEEDS:
        yield f"seed-{seed}", {"seed": seed}


def run(case_id, payload):
    return run_seed(int(payload["seed"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, choices=(17, 31, 53), default=17)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        initialization = check_all_initial_populations()
        result = run_seed(args.seed, Settings(generations=2), ("c0",))
        result = {"seed": result["seed"], "initial_populations_checked": len(initialization),
                  "source_sha256": result["source_sha256"], "elapsed_seconds": result["elapsed_seconds"],
                  "smoke": {method: {width: {"evaluations": row["search"]["evaluations"],
                                               "initial_matches_e001": row["search"]["e001_initial_population_matches"],
                                               "mutation_event_counts": row["search"]["mutation_event_counts"],
                                               "frozen_unchanged": row["frozen_program_decoder_sha256"] == row["post_evaluation_program_decoder_sha256"]}
                                      for width, row in record["widths"].items()}
                            for method, record in result["contexts"][0]["methods"].items()}}
    else:
        result = run_seed(args.seed)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
