"""Lazy, selector-independent candidate streams from the pinned reuse search.

Only caller-supplied training inputs and binary labels enter reward. Proposal
prefixes are reproducible, and costs describe the prefix actually executed.
Discovery indexes do not imply that a selector stopped there. No hidden-label
or target-oracle function is called. Smoke tests use synthetic labels only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import sys
import time
from dataclasses import replace
from functools import lru_cache
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent.parent / "BRAID-REUSE-20261114-001" / "BRAID-REUSE-20261114-001-E001_transfer" / "job.py"
SOURCE_SHA256 = "8ff46e077ee07694f27756f3b326ba094f2a5f1c827d22f14300c87f856fb336"
MAXIMUM_PREFIX = 49_184
COUNT_NAMES = ("guarded_toggles", "NOT", "AND", "XOR")


@lru_cache(maxsize=1)
def _base():
    actual = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if actual != SOURCE_SHA256:
        raise ValueError(f"The immutable predecessor producer changed: {actual}")
    name = "braid_reuse_pinned_for_candidate_stream"
    spec = importlib.util.spec_from_file_location(name, SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def make_grammar():
    """Return the predecessor's pinned public primitive/call language."""
    return _base().Grammar()


def default_config():
    return replace(_base().FROZEN, generations=128)


def _counts(values):
    result = dict(zip(COUNT_NAMES, map(int, values), strict=True))
    result["Boolean_gates"] = sum(values[1:])
    return result


def program_counts(genome, grammar=None):
    grammar = grammar or make_grammar()
    genome = tuple(genome)
    expanded = grammar.expand(genome)
    return {"expanded_length": len(expanded), "macro_calls": sum(token >= 72 for token in genome),
            "program_packed_counts": _counts(grammar.counts(expanded)),
            "readout_packed_counts": {"OR": 1, "NOT": 1, "Boolean_gates": 2}}


def execute(genome, inputs, grammar=None):
    """Execute raw inputs and return outputs/predictions, with no label access."""
    grammar = grammar or make_grammar()
    inputs = tuple(tuple(map(int, row)) for row in inputs)
    if not inputs or any(len(row) != 3 or any(value not in (0, 1, 2) for value in row) for row in inputs):
        raise ValueError("A nonempty list of three-trit inputs is required")
    expanded = grammar.expand(tuple(genome))
    mask = (1 << len(inputs)) - 1
    output_bits = grammar.execute_packed(expanded, _base().pack_states(inputs), mask)
    zero = mask ^ (output_bits[4] | output_bits[5])
    outputs = [tuple(2 * ((output_bits[2 * register] >> lane) & 1)
                     + ((output_bits[2 * register + 1] >> lane) & 1) for register in range(3))
               for lane in range(len(inputs))]
    return {"outputs": outputs, "predictions": [int((zero >> lane) & 1) for lane in range(len(inputs))],
            **program_counts(genome, grammar)}


class _CountedRandom:
    """Count requested RNG API values without changing predecessor randomness."""

    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.calls = {"randrange": 0, "randint": 0, "random": 0}

    def randrange(self, *args):
        self.calls["randrange"] += 1
        return self.rng.randrange(*args)

    def randint(self, *args):
        self.calls["randint"] += 1
        return self.rng.randint(*args)

    def random(self):
        self.calls["random"] += 1
        return self.rng.random()


class CandidateStream:
    def __init__(self, seed, condition, training_inputs, training_labels, config=None, grammar=None):
        self._created_ns = time.perf_counter_ns()
        if condition not in ("raw", "reuse"):
            raise ValueError("condition must be 'raw' or 'reuse'")
        self.seed, self.condition = int(seed), condition
        self.config = config or default_config()
        if self.config.evaluations > MAXIMUM_PREFIX:
            raise ValueError("This stream is bounded to at most 49,184 proposals")
        self.grammar = grammar or make_grammar()
        self.inputs = tuple(tuple(map(int, row)) for row in training_inputs)
        self.labels = tuple(map(int, training_labels))
        if (not self.inputs or len(self.inputs) != len(self.labels)
                or any(label not in (0, 1) for label in self.labels)
                or any(len(row) != 3 or any(value not in (0, 1, 2) for value in row) for row in self.inputs)):
            raise ValueError("Training inputs and binary labels must be aligned and valid")
        self._bits = _base().pack_states(self.inputs)
        self._mask = (1 << len(self.inputs)) - 1
        self._positive = sum(label << index for index, label in enumerate(self.labels))
        self._negative = self._mask ^ self._positive
        self.maximum_score = 2 * sum(self.labels) + len(self.labels) - sum(self.labels)
        self.maximum_proposals = self.config.evaluations
        self._variation = _CountedRandom(self.seed)
        self._selection = _CountedRandom(self.seed + 1)
        self.proposal = 0
        self._packed = [0, 0, 0, 0]
        self._best = None
        self._perfect_events, self._perfect_keys = [], set()
        self._perfect_proposals = 0
        self.initial_population_sha256 = None
        self._syntax = {"constructed_genomes": 0, "proposal_output_tokens": 0,
                        "expanded_tokens_materialized": 0, "initial_programs": 0,
                        "independent_programs": 0, "mutation_calls": 0,
                        "parent_length_tokens_scanned": 0, "candidate_pool_slots_appended": 0,
                        "parent_choices": 0, "parent_score_reads": 0,
                        "initial_population_hashes": 0, "perfect_registry_key_bytes": 0}
        self._query_count = self._query_event_records = 0
        self._query_ns = 0
        self._iterator = self._proposals()
        self._active_ns = time.perf_counter_ns() - self._created_ns

    def __iter__(self):
        return self

    def __next__(self):
        started = time.perf_counter_ns()
        try:
            return next(self._iterator)
        finally:
            self._active_ns += time.perf_counter_ns() - started

    @property
    def best(self):
        return self._copy_candidate(self._best)

    @staticmethod
    def _copy_candidate(candidate):
        if candidate is None:
            return None
        return candidate | {"genome": list(candidate["genome"]),
                            "program_packed_counts": candidate["program_packed_counts"].copy()}

    def _evaluate(self, genome, generation, island, kind):
        expanded = self.grammar.expand(genome)
        if (len(expanded) > self.config.maximum_expanded_length
                or (self.condition == "raw" and any(token >= 72 for token in genome))):
            raise ValueError("A candidate violated the frozen action/cap rules")
        counts = self.grammar.counts(expanded)
        bits = self.grammar.execute_packed(expanded, self._bits, self._mask)
        predicted = self._mask ^ (bits[4] | bits[5])
        score = 2 * (predicted & self._positive).bit_count() + ((self._mask ^ predicted) & self._negative).bit_count()
        self.proposal += 1
        for index, value in enumerate(counts):
            self._packed[index] += value
        self._syntax["constructed_genomes"] += 1
        self._syntax["proposal_output_tokens"] += len(genome)
        self._syntax["expanded_tokens_materialized"] += len(expanded)
        calls = (len(expanded) - len(genome)) // 11
        candidate = {"first_proposal": self.proposal, "genome": genome, "score": score,
                     "expanded_length": len(expanded), "macro_calls": calls,
                     "program_packed_counts": _counts(counts)}
        if self._best is None or (score, -len(expanded)) > (self._best["score"], -self._best["expanded_length"]):
            self._best = candidate
        new_perfect = False
        if score == self.maximum_score:
            self._perfect_proposals += 1
            key = bytes(genome)
            self._syntax["perfect_registry_key_bytes"] += len(key)
            if key not in self._perfect_keys:
                self._perfect_keys.add(key)
                self._perfect_events.append(candidate)
                new_perfect = True
        event = {"proposal": self.proposal, "generation": generation, "island": island, "kind": kind,
                 "genome": genome, "score": score, "maximum_score": self.maximum_score,
                 "perfect": score == self.maximum_score, "new_unique_perfect": new_perfect,
                 "expanded_length": len(expanded), "macro_calls": calls}
        return (genome, score, len(expanded)), event

    def _proposals(self):
        allow_calls = self.condition == "reuse"
        parents, initial = [], []
        for island in range(self.config.islands):
            # Initial genomes are generated lazily; their complete sequence is
            # exactly the predecessor's, but an actual early stop builds no tail.
            genome = self.grammar.random_program(self._variation, allow_calls, self.config, initial=True)
            initial.append(genome)
            self._syntax["initial_programs"] += 1
            parent, event = self._evaluate(genome, 0, island, "initial")
            parents.append(parent)
            self._syntax["candidate_pool_slots_appended"] += 1
            if len(initial) == self.config.islands:
                self.initial_population_sha256 = _base().canonical_sha256(initial)
                self._syntax["initial_population_hashes"] += 1
            yield event
        for generation in range(1, self.config.generations + 1):
            for island, parent in enumerate(parents):
                candidates = [parent]
                self._syntax["candidate_pool_slots_appended"] += 1
                for child in range(self.config.brood):
                    if child == self.config.brood - 1:
                        genome = self.grammar.random_program(self._variation, allow_calls, self.config)
                        kind = "independent"
                        self._syntax["independent_programs"] += 1
                    else:
                        self._syntax["mutation_calls"] += 1
                        self._syntax["parent_length_tokens_scanned"] += len(parent[0])
                        genome = self.grammar.mutate(parent[0], self._variation, allow_calls, self.config)
                        kind = "mutation"
                    candidate, event = self._evaluate(genome, generation, island, kind)
                    candidates.append(candidate)
                    self._syntax["candidate_pool_slots_appended"] += 1
                    yield event
                # A caller stopping after the last available proposal does not
                # execute an otherwise unused parent update.
                if self.proposal == self.maximum_proposals:
                    return
                if generation % self.config.restart_period == 0:
                    parents[island] = candidates[-1]
                else:
                    self._syntax["parent_score_reads"] += 2 * len(candidates)
                    maximum = max(candidate[1] for candidate in candidates)
                    tied = [candidate for candidate in candidates if candidate[1] == maximum]
                    parents[island] = tied[int(self._selection.random() * len(tied))]
                self._syntax["parent_choices"] += 1

    def _advance(self, proposal, stop_on_new):
        if not isinstance(proposal, int) or not self.proposal <= proposal <= self.maximum_proposals:
            raise ValueError("Advance to a future/current proposal within the declared prefix")
        started, before = time.perf_counter_ns(), self._active_ns
        try:
            while self.proposal < proposal:
                event = next(self)
                if stop_on_new and event["new_unique_perfect"]:
                    break
        finally:
            # Include the internal driver loop without double-counting __next__.
            self._active_ns += max(0, time.perf_counter_ns() - started - (self._active_ns - before))
        return self.proposal

    def advance_to(self, proposal):
        return self._advance(proposal, False)

    def advance_to_next_perfect_or(self, proposal):
        return self._advance(proposal, True)

    def prefix_cost(self):
        p, n = self.proposal, len(self.inputs)
        packed = _counts(self._packed)
        logical = {key: value * n for key, value in packed.items()}
        readout = {"OR": p, "NOT": p, "Boolean_gates": 2 * p}
        return {
            "executed_proposals": p, "training_lanes": n,
            "program_packed_counts": packed, "program_logical_counts": logical,
            "readout_packed_counts": readout,
            "readout_logical_counts": {key: value * n for key, value in readout.items()},
            "program_plus_readout_packed_gates": packed["Boolean_gates"] + 2 * p,
            "program_plus_readout_logical_gates": n * (packed["Boolean_gates"] + 2 * p),
            "fitness_costs": {"bitset_AND": 2 * p, "bitset_XOR": p, "bit_count_calls": 2 * p,
                              "weighted_integer_multiplies": p, "weighted_integer_additions": p,
                              "logical_label_events": p * n, "initial_training_label_reads": n},
            "proposal_syntax": self._syntax.copy(),
            "rng_API_calls": {"variation": self._variation.calls.copy(), "selection": self._selection.calls.copy()},
            "syntax_measure": "named representation-work proxies, not CPU instructions or Boolean gates",
        }

    def snapshot(self, event_cursor=0):
        started = time.perf_counter_ns()
        if not isinstance(event_cursor, int) or not 0 <= event_cursor <= len(self._perfect_events):
            raise ValueError("event_cursor must refer to an already exposed event prefix")
        new_events = [self._copy_candidate(event) for event in self._perfect_events[event_cursor:]]
        self._query_count += 1
        self._query_event_records += len(new_events)
        result = {"seed": self.seed, "condition": self.condition, "proposal": self.proposal,
                  "maximum_proposals": self.maximum_proposals, "maximum_score": self.maximum_score,
                  "best": self.best, "new_perfect_events": new_events, "event_cursor": len(self._perfect_events),
                  "unique_perfect_count": len(self._perfect_events), "perfect_proposals": self._perfect_proposals,
                  "prefix_cost": self.prefix_cost(), "elapsed_seconds": self._active_ns / 1e9,
                  "initial_population_sha256": self.initial_population_sha256,
                  "initial_population_complete": self.initial_population_sha256 is not None,
                  "accounting": "current actually executed prefix; no retroactive stopping at discovery indexes"}
        self._query_ns += time.perf_counter_ns() - started
        result["snapshot_query_cost"] = {"queries": self._query_count,
                                          "event_records_returned": self._query_event_records,
                                          "elapsed_seconds": self._query_ns / 1e9}
        result["wall_span_seconds"] = (time.perf_counter_ns() - self._created_ns) / 1e9
        return result


def smoke():
    base = _base()
    grammar = make_grammar()
    config = replace(default_config(), seeds=(0,), islands=2, generations=3, brood=3, restart_period=2)
    inputs, labels = ((0, 0, 0), (1, 2, 1), (2, 0, 2)), (0, 1, 0)
    mask = (1 << len(inputs)) - 1
    positive = sum(label << i for i, label in enumerate(labels))
    negative = mask ^ positive
    score = lambda prediction: 2 * (prediction & positive).bit_count() + ((mask ^ prediction) & negative).bit_count()
    maximum = 2 * sum(labels) + len(labels) - sum(labels)
    summaries = []
    original_oracle = base.target_answer

    def forbidden_oracle(*args, **kwargs):
        raise AssertionError("A candidate stream accessed the predecessor target oracle")

    base.target_answer = forbidden_oracle
    try:
        for condition in ("raw", "reuse"):
            reference = base.search_arm(grammar, config, inputs, score, maximum, 0, condition)
            stream = CandidateStream(0, condition, inputs, labels, config, grammar)
            stream.advance_to(config.evaluations)
            state = stream.snapshot()
            if (state["initial_population_sha256"] != reference["initial_population_sha256"]
                    or state["best"]["genome"] != reference["training_selected"]["genome"]
                    or state["best"]["score"] != reference["training_selected"]["training_score"]
                    or state["prefix_cost"]["program_packed_counts"] != reference["charges"]["packed_program"]):
                raise AssertionError("The lazy stream changed the immutable search candidate sequence")
            saved = [(row["evaluation"], row["genome_hex"]) for row in base.iter_perfect_events(reference["train_perfect_events"])]
            actual = [(row["first_proposal"], bytes(row["genome"]).hex()) for row in state["new_perfect_events"]]
            if saved != actual:
                raise AssertionError("The lazy stream lost first-occurrence training-perfect events")
            paused = CandidateStream(0, condition, inputs, labels, config, grammar)
            cursor = 0
            while paused.proposal < config.evaluations:
                paused.advance_to_next_perfect_or(config.evaluations)
                checkpoint = paused.snapshot(cursor)
                if checkpoint["new_perfect_events"] and checkpoint["new_perfect_events"][-1]["first_proposal"] != paused.proposal:
                    raise AssertionError("The operational new-perfect stop advanced past its event")
                cursor = checkpoint["event_cursor"]
            if paused.snapshot()["prefix_cost"] != state["prefix_cost"] or paused.best != state["best"]:
                raise AssertionError("Observing or pausing changed the shared proposal stream")
            summaries.append({"condition": condition, "proposals": state["proposal"],
                              "unique_perfect": state["unique_perfect_count"],
                              "program_plus_readout_packed_gates": state["prefix_cost"]["program_plus_readout_packed_gates"]})
    finally:
        base.target_answer = original_oracle
    return {"synthetic_only": True, "oracle_guard_passed": True, "streams": summaries,
            "default_maximum_proposals": default_config().evaluations,
            "source_sha256": SOURCE_SHA256,
            "stream_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.parse_args()
    print(json.dumps(smoke(), sort_keys=True))


if __name__ == "__main__":
    main()
