"""Independent scoring, selection, certificate and search-prefix audit.

No producer, selector or grader module is imported.  The accepted preceding
independent primitive interpreter supplies only raw instruction semantics and
expansion counts.  All task tables, observation-only fits, rankings, paid
checks and ledgers below are reconstructed independently.
"""

from __future__ import annotations

import argparse
import base64
from collections import Counter, defaultdict
from functools import lru_cache
import hashlib
import importlib.util
from itertools import permutations, product
import json
from pathlib import Path
import random
import sys
import time
import zlib


ROOT = Path(__file__).resolve().parents[2]
PREVIOUS = ROOT / "research/BRAID-REUSE-20261114-001/independent.py"
BUNDLE = ROOT / "artifacts/BRAID-ACTIONS-20261114-001/BRAID-ACTIONS-20261114-001-E002_rewarded_actions/sequence_checkpoint.json"
POINTS = tuple(product(range(3), repeat=3))
HELD = tuple(point for point in POINTS if point[2] == (point[0] + point[1] + 2) % 3)
TRAIN = tuple(point for point in POINTS if point not in HELD)
PERMUTATIONS = tuple(permutations(range(3)))
SEEDS = (101, 211, 307)
CHECKPOINTS = (1568, 3104, 6176, 12320, 24608, 49184)
CAP = CHECKPOINTS[-1]
COUNT_NAMES = ("guarded_toggles", "NOT", "AND", "XOR")


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def fingerprint(data):
    return hashlib.sha256(canonical(data)).hexdigest()


@lru_cache(maxsize=1)
def primitive_runtime():
    spec = importlib.util.spec_from_file_location("accepted_primitive_audit_for_rename", PREVIOUS)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    forward = tuple(json.loads(BUNDLE.read_bytes())["forward"])
    if hashlib.sha256(bytes(forward)).hexdigest() != "a740b9a93061a75b78ce24a135b5adc94ca55a0206872c7b69e97117837f4246":
        raise ValueError("frozen forward program changed")
    return module, forward, module._effect_tables(forward)


@lru_cache(maxsize=None)
def program_counts(genome):
    runtime, forward, _ = primitive_runtime()
    values = runtime._packed_counts(genome, forward)
    return dict(zip(COUNT_NAMES, values)) | {"Boolean_gates": sum(values[1:])}


@lru_cache(maxsize=None)
def predictions(genome):
    runtime, _, tables = primitive_runtime()
    effect = runtime._genome_image(genome, tables)
    if len(set(effect)) != 27:
        raise ValueError("candidate ceased to be reversible")
    return tuple(int(value % 3 == 0) for value in effect)


def point_index(point):
    return 9 * point[0] + 3 * point[1] + point[2]


def private_tables():
    """Evaluation-only definitions, never passed into the fit or ranker."""
    functions = {
        "6d18": lambda x, y, z: x == y,
        "4caf": lambda x, y, z: x == z,
        "a942": lambda x, y, z: y == z,
        "c10e": lambda x, y, z: z == (y if x == 0 else x),
        "1ab7": lambda x, y, z: z == (0 if x == y else 3 - x - y),
        "e35a": lambda x, y, z: z == (y if x == y else (y + 1) % 3),
        "79c2": lambda x, y, z: z == (x if y == (x + 1) % 3 else y),
        "528f": lambda x, y, z: z == (y if x == 0 else (y + 1) % 3),
        "b037": lambda x, y, z: z == int(x == 0) + int(y == 1),
        "f46b": lambda x, y, z: (x == y and (x, y, z) != (1, 1, 1)) or (x, y, z) == (1, 0, 0),
    }
    tables = {key: tuple(int(function(*point)) for point in POINTS) for key, function in functions.items()}
    if any(sum(table) != 9 for table in tables.values()) or len(set(tables.values())) != 10:
        raise ValueError("independent task panel is not ten distinct balanced tables")
    return tables


def fit_votes(mode, observations):
    """Only observed input/answer pairs enter this function."""
    model = {"accepted": [], "evidence": [], "margins": {}}
    costs, vote_totals = Counter(), Counter()
    if mode == "shortest":
        return model, {}, costs
    if mode not in ("fitted", "always"):
        raise ValueError("unknown blind mode")
    for permutation in PERMUTATIONS[1:]:
        moved = {point: tuple(permutation[value] for value in point) for point in observations}
        pairs = {tuple(sorted((point, other))) for point, other in moved.items()
                 if point != other and other in observations}
        if mode == "fitted":
            classes = {observations[point] for pair in pairs for point in pair}
            mismatches = sum(observations[left] != observations[right] for left, right in pairs)
            costs["fit_label_reads"] += 2 * len(pairs)
            costs["fit_comparisons"] += len(pairs)
            model["evidence"].append([list(permutation), len(pairs), len(classes), mismatches])
            if len(pairs) < 2 or len(classes) != 2 or mismatches:
                continue
        model["accepted"].append(list(permutation))
        for source, destination in moved.items():
            if destination not in observations:
                vote_totals[destination] += 2 * observations[source] - 1
                costs["fit_label_reads"] += 1
                costs["vote_additions"] += 1
    votes = {point: vote_totals[point] for point in sorted(vote_totals) if vote_totals[point]}
    model["margins"] = {"".join(map(str, point)): count for point, count in votes.items()}
    return model, votes, costs


def event_record(event):
    if event is None:
        return None
    return {"proposal": event["first_proposal"], "genome": bytes(event["genome"]).hex(),
            "expanded_length": event["expanded_length"], "macro_calls": event["macro_calls"]}


def read_bank(blind):
    rows = json.loads(zlib.decompress(base64.b64decode(blind["bank_zlib_base64"], validate=True)))
    if len(rows) != blind["bank_count"] or fingerprint(rows) != blind["bank_sha256"]:
        raise ValueError("blind bank digest/count disagrees")
    events, seen, previous = [], set(), 0
    runtime, _, _ = primitive_runtime()
    for proposal, hexadecimal in rows:
        genome = tuple(bytes.fromhex(hexadecimal))
        runtime.normalize_genome(genome)
        if genome in seen or type(proposal) is not int or not previous < proposal <= CAP:
            raise ValueError("bank is not an ordered unique training-perfect prefix")
        counts = program_counts(genome)
        if counts["guarded_toggles"] > 36:
            raise ValueError("bank candidate exceeds expanded horizon")
        events.append({"first_proposal": proposal, "genome": genome,
                       "expanded_length": counts["guarded_toggles"], "macro_calls": sum(token >= 72 for token in genome)})
        previous = proposal
        seen.add(genome)
    return events


def rank_key(event, votes):
    bits = predictions(event["genome"])
    penalty = sum(abs(weight) for point, weight in votes.items()
                  if bits[point_index(point)] != int(weight > 0))
    return penalty, event["expanded_length"], event["first_proposal"]


def audit_blind(blind, table):
    observations = {tuple(point): int(label) for point, label in blind["training_observations"]}
    expected_observations = {point: table[point_index(point)] for point in TRAIN}
    if observations != expected_observations or tuple(observations) != TRAIN:
        raise ValueError("training observations differ from the independent panel/split")
    events = read_bank(blind)
    for event in events:
        if any(predictions(event["genome"])[point_index(point)] != label for point, label in observations.items()):
            raise ValueError("a bank program is not training-perfect")
    models, choices, orders = {}, {}, {}
    for mode in ("shortest", "fitted", "always"):
        model, votes, _ = fit_votes(mode, observations)
        ordered = sorted(range(len(events)), key=lambda index: rank_key(events[index], votes))
        models[mode], orders[mode] = model, ordered
        choices[mode] = event_record(events[ordered[0]]) if ordered else None
    checks = {"models": models == blind["models"], "choices": choices == blind["choices"],
              "blind_commitment": fingerprint([blind["bank_sha256"], models, choices]) == blind["blind_commitment"]}
    truth = sum(table[point_index(point)] << index for index, point in enumerate(HELD))
    effects = [sum(predictions(event["genome"])[point_index(point)] << index for index, point in enumerate(HELD)) for event in events]
    valid = sum(effect == truth for effect in effects)
    scores = {}
    for mode, ordered in orders.items():
        bad_left, wins = len(events) - valid, 0
        for index in ordered:
            if effects[index] == truth:
                wins += bad_left
            else:
                bad_left -= 1
        chosen = effects[ordered[0]] if ordered else None
        scores[mode] = {"held_correct": None if chosen is None else 9 - (chosen ^ truth).bit_count(),
                        "exact": chosen == truth, "held_prediction_mask": chosen,
                        "correct_pair_choices": wins, "eligible_pairs": valid * (len(events) - valid)}
    full_symmetries = [permutation for permutation in PERMUTATIONS
                       if all(table[point_index(point)] == table[point_index(tuple(permutation[value] for value in point))]
                              for point in POINTS)]
    accepted = [tuple(permutation) for permutation in models["fitted"]["accepted"]]
    guessed = set(accepted) | {PERMUTATIONS[0]}  # Identity is implicit, never a learned decision.
    model, votes, _ = fit_votes("fitted", observations)
    inference = {"true_group_order": len(full_symmetries), "guessed_with_identity": len(guessed),
                 "false_accepted": sorted(guessed - set(full_symmetries)),
                 "missed_true": sorted(set(full_symmetries) - guessed),
                 "voted_held_cells": len(votes),
                 "correct_vote_signs": sum(int(weight > 0) == table[point_index(point)] for point, weight in votes.items())}
    offline = {"evaluation_input_executions": 9 * len(events),
               "evaluation_program_gates": 9 * sum(program_counts(event["genome"])["Boolean_gates"] for event in events),
               "evaluation_readout_gates": 18 * len(events),
               "evaluation_packed_program_plus_readout": sum(program_counts(event["genome"])["Boolean_gates"] + 2 for event in events),
               "evaluation_cached_predictions": 0}
    return {"pass": all(checks.values()), "checks": checks, "events": events, "observations": observations,
            "assessment": {"held_truth_mask": truth, "n_exact_in_pool": valid,
                           "distinct_held_predictions": len(set(effects)), "scores": scores,
                           "offline_evaluation_cost": offline}, "inference": inference}


class RandomLedger:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.calls = {"randrange": 0, "randint": 0, "random": 0}

    def randrange(self, bound):
        self.calls["randrange"] += 1
        return self.rng.randrange(bound)

    def randint(self, low, high):
        self.calls["randint"] += 1
        return self.rng.randint(low, high)

    def random(self):
        self.calls["random"] += 1
        return self.rng.random()


def _counts(values):
    return dict(zip(COUNT_NAMES, values)) | {"Boolean_gates": sum(values[1:])}


def rebuild_stream(seed, condition, observations, requested_prefixes):
    """Reconstruct all49,184 proposals and the *actual* paused prefix work."""
    runtime, forward, tables = primitive_runtime()
    variation, selection = RandomLedger(seed), RandomLedger(seed + 1)
    allow_calls = condition == "reuse"
    lengths = (1,) * 72 + (12,) * 6
    prices = tuple(runtime._packed_counts((token,), forward) for token in range(78))
    labeled = tuple((point_index(point), label, 2 if label else 1) for point, label in observations.items())
    maximum = sum(weight for _, _, weight in labeled)
    cumulative = [0, 0, 0, 0]
    syntax = dict.fromkeys(("constructed_genomes", "proposal_output_tokens", "expanded_tokens_materialized", "initial_programs",
                           "independent_programs", "mutation_calls", "parent_length_tokens_scanned", "candidate_pool_slots_appended",
                           "parent_choices", "parent_score_reads", "initial_population_hashes", "perfect_registry_key_bytes"), 0)
    evaluations = perfect_proposals = 0
    events, seen, snapshots, initial = [], set(), {}, []
    best = None
    requested_prefixes = set(requested_prefixes) | {CAP}

    def draw():
        pair, action = variation.randrange(6), variation.randrange(12)
        return 12 * pair + action, 72 + pair, variation.randrange(13) == 0

    def independent(initial=False):
        size = variation.randint(2, 12)
        draws = [draw() for _ in range(size)]
        genome, expanded = [item[0] for item in draws], size
        for index, (_, call, requested) in enumerate(draws):
            if allow_calls and not initial and requested and expanded + 11 <= 36:
                genome[index] = call
                expanded += 11
        return tuple(genome)

    def mutate(parent):
        kind, left, right = variation.randrange(100), variation.random(), variation.random()
        raw, call, requested = draw()
        token = call if allow_calls and requested else raw
        size, expanded = len(parent), sum(lengths[item] for item in parent)
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

    def prefix_cost():
        packed = _counts(cumulative)
        logical = {key: value * 18 for key, value in packed.items()}
        readout = {"OR": evaluations, "NOT": evaluations, "Boolean_gates": 2 * evaluations}
        return {"executed_proposals": evaluations, "training_lanes": 18,
                "program_packed_counts": packed, "program_logical_counts": logical,
                "readout_packed_counts": readout,
                "readout_logical_counts": {key: value * 18 for key, value in readout.items()},
                "program_plus_readout_packed_gates": packed["Boolean_gates"] + 2 * evaluations,
                "program_plus_readout_logical_gates": 18 * (packed["Boolean_gates"] + 2 * evaluations),
                "fitness_costs": {"bitset_AND": 2 * evaluations, "bitset_XOR": evaluations,
                                  "bit_count_calls": 2 * evaluations, "weighted_integer_multiplies": evaluations,
                                  "weighted_integer_additions": evaluations, "logical_label_events": 18 * evaluations,
                                  "initial_training_label_reads": 18},
                "proposal_syntax": syntax.copy(),
                "rng_API_calls": {"variation": variation.calls.copy(), "selection": selection.calls.copy()},
                "syntax_measure": "named representation-work proxies, not CPU instructions or Boolean gates"}

    def evaluate(genome):
        nonlocal evaluations, best, perfect_proposals
        expanded = sum(lengths[token] for token in genome)
        if expanded > 36 or (not allow_calls and any(token >= 72 for token in genome)):
            raise ValueError("reconstructed proposal violates action language")
        effect = runtime._genome_image(genome, tables)
        score = sum(weight * ((effect[index] % 3 == 0) == bool(label)) for index, label, weight in labeled)
        evaluations += 1
        cumulative[0] += expanded
        cumulative[1] += sum(prices[token][1] for token in genome)
        cumulative[2] += 2 * expanded
        cumulative[3] += expanded
        syntax["constructed_genomes"] += 1
        syntax["proposal_output_tokens"] += len(genome)
        syntax["expanded_tokens_materialized"] += expanded
        candidate = {"first_proposal": evaluations, "genome": genome, "score": score,
                     "expanded_length": expanded, "macro_calls": sum(token >= 72 for token in genome)}
        if best is None or (score, -expanded) > (best["score"], -best["expanded_length"]):
            best = candidate
        if score == maximum:
            perfect_proposals += 1
            syntax["perfect_registry_key_bytes"] += len(genome)
            if genome not in seen:
                seen.add(genome)
                events.append(candidate)
        return genome, score, expanded

    def capture():
        if evaluations in requested_prefixes:
            snapshots[evaluations] = prefix_cost()

    parents = []
    for _ in range(32):
        genome = independent(True)
        initial.append(genome)
        syntax["initial_programs"] += 1
        parent = evaluate(genome)
        parents.append(parent)
        syntax["candidate_pool_slots_appended"] += 1
        if len(initial) == 32:
            syntax["initial_population_hashes"] += 1
        capture()
    for generation in range(1, 129):
        for island, parent in enumerate(parents):
            candidates = [parent]
            syntax["candidate_pool_slots_appended"] += 1
            for child in range(12):
                if child == 11:
                    genome = independent()
                    syntax["independent_programs"] += 1
                else:
                    syntax["mutation_calls"] += 1
                    syntax["parent_length_tokens_scanned"] += len(parent[0])
                    genome = mutate(parent[0])
                candidates.append(evaluate(genome))
                syntax["candidate_pool_slots_appended"] += 1
                capture()
            if evaluations == CAP:
                return {"events": events, "prefixes": snapshots, "best": best,
                        "initial_population_sha256": fingerprint(initial), "perfect_proposals": perfect_proposals}
            if generation % 32 == 0:
                parents[island] = candidates[-1]
            else:
                syntax["parent_score_reads"] += 2 * len(candidates)
                highest = max(candidate[1] for candidate in candidates)
                tied = [candidate for candidate in candidates if candidate[1] == highest]
                parents[island] = tied[int(selection.random() * len(tied))]
            syntax["parent_choices"] += 1
    raise AssertionError("the complete prefix failed to reach its cap")


class PredictionLedger:
    def __init__(self):
        self.cache, self.cost = {}, Counter()

    def get(self, genome, cells, stage):
        if not cells:
            return ()
        known = self.cache.setdefault(genome, {})
        missing = tuple(point for point in cells if point not in known)
        if missing:
            bits, gates = predictions(genome), program_counts(genome)["Boolean_gates"]
            for point in missing:
                known[point] = bits[point_index(point)]
            self.cost[stage + "_input_executions"] += len(missing)
            self.cost[stage + "_program_gates"] += len(missing) * gates
            self.cost[stage + "_readout_gates"] += 2 * len(missing)
            self.cost[stage + "_packed_program_plus_readout"] += gates + 2
        self.cost[stage + "_cached_predictions"] += len(cells) - len(missing)
        return tuple(known[point] for point in cells)


def audit_deployment(mode, observations, table, events, rebuilt):
    cache = PredictionLedger()
    model, votes, fit_cost = ({}, {}, Counter()) if mode == "direct" else fit_votes(mode, observations)
    penalties, known_truth, certificate_cost = {}, {}, Counter()
    requests, offered_history, attempted = [], [], set()
    returned = None

    def key(event):
        genome = event["genome"]
        if genome not in penalties:
            bits = cache.get(genome, tuple(votes), "ranking")
            penalties[genome] = sum(abs(votes[point]) for point, bit in zip(votes, bits) if bit != int(votes[point] > 0))
            fit_cost["candidate_vote_comparisons"] += len(votes)
        fit_cost["rank_key_requests"] += 1
        return penalties[genome], event["expanded_length"], event["first_proposal"]

    def certify(event):
        for point in HELD:
            value, = cache.get(event["genome"], (point,), "verification")
            if point not in known_truth:
                known_truth[point] = table[point_index(point)]
                certificate_cost["fresh_truth_labels"] += 1
            certificate_cost["truth_reads"] += 1
            certificate_cost["answer_comparisons"] += 1
            if value != known_truth[point]:
                return False
        return True

    if mode == "direct":
        count = CAP
        for event in events:
            count = event["first_proposal"]
            passed = certify(event)
            requests.append([count, event["first_proposal"], passed])
            if passed:
                returned = event
                break
        if returned is None:
            count = CAP
    else:
        for count in CHECKPOINTS:
            eligible = [event for event in events if event["first_proposal"] <= count and event["first_proposal"] not in attempted]
            # key() visits every eligible candidate before sorting, just as a
            # bounded n-smallest selection must evaluate all candidate keys.
            offered = sorted(eligible, key=key)[:4]
            offered_history.append({"prefix": count, "offered_ids": [event["first_proposal"] for event in offered]})
            for event in offered:
                attempted.add(event["first_proposal"])
                passed = certify(event)
                requests.append([count, event["first_proposal"], passed])
                if passed:
                    returned = event
                    break
            if returned is not None:
                break
    prefix = rebuilt["prefixes"][count]
    pc, vc = cache.cost, certificate_cost
    components = {
        "training_label_reads": 18,
        "search_program_and_readout": prefix["program_plus_readout_logical_gates"],
        "fitness_bit_operations": 3 * count * 18,
        "fit_label_reads_and_comparisons": fit_cost["fit_label_reads"] + fit_cost["fit_comparisons"],
        "rank_prediction_and_comparison": pc["ranking_program_gates"] + pc["ranking_readout_gates"] + fit_cost["candidate_vote_comparisons"],
        "certificate": pc["verification_program_gates"] + pc["verification_readout_gates"] + vc["truth_reads"] + vc["answer_comparisons"] + vc["fresh_truth_labels"],
    }
    ledger = {"work_units": sum(components.values()), "components": components, "search": prefix,
              "fit_and_ranking": dict(fit_cost), "prediction": dict(pc), "checking": dict(vc)}
    return {"returned": event_record(returned), "correct_return": returned is not None,
            "cap_exhausted_without_return": returned is None, "proposals": count,
            "unique_training_perfect_seen": sum(event["first_proposal"] <= count for event in events),
            "requests": requests, "cost": ledger, "offered_history": offered_history,
            "failed_certificates": sum(not row[2] for row in requests), "fitted_model": model}


def _equal(expected, actual):
    return canonical(expected) == canonical(actual)


def audit_results(rows, progress=None):
    tables = private_tables()
    expected = {(task, seed) for task in tables for seed in SEEDS}
    cases = {(row["result"]["task"], row["result"]["seed"]): row for row in rows}
    if set(cases) != expected or not len(rows) == len(cases) == 30:
        raise ValueError("expected exactly30 unique declared task/seed cases")
    if any(row["status"] != "ok" for row in rows):
        # Runner versions use either 'ok' or 'completed'.  Neither a failed
        # row nor a missing result can be silently counted as successful.
        if any(row["status"] not in ("ok", "completed", "success") for row in rows):
            raise ValueError("raw file includes an unsuccessful runner case")
    prepared, needed = {}, defaultdict(set)
    for (task, seed), wrapped in cases.items():
        result = wrapped["result"]
        for condition in ("raw", "reuse"):
            arm = result["arms"][condition]
            blind = audit_blind(arm["blind"], tables[task])
            key = (seed, condition, tuple(blind["observations"].values()))
            needed[key].update(CHECKPOINTS)
            needed[key].update(deployment["proposals"] for deployment in arm["deployed"].values())
            prepared[task, seed, condition] = (arm, blind, key)
    reconstructions = {}
    for index, (key, prefixes) in enumerate(needed.items()):
        seed, condition, labels = key
        reconstructions[key] = rebuild_stream(seed, condition, dict(zip(TRAIN, labels)), prefixes)
        if progress:
            progress(f"rebuilt stream {index + 1}/{len(needed)}: seed {seed} {condition}")
    episodes, errors, mode_scores = [], [], Counter()
    deployed_summaries = defaultdict(lambda: {"successes": 0, "work_units": 0, "wall_seconds": 0.0,
                                             "failed_certificates": 0, "fresh_truth_labels": 0, "episodes": 0})
    for (task, seed, condition), (arm, blind, stream_key) in prepared.items():
        rebuilt = reconstructions[stream_key]
        checks = {"blind": blind["pass"],
                  "bank_reconstructed": _equal([[event["first_proposal"], bytes(event["genome"]).hex()] for event in rebuilt["events"]],
                                               [[event["first_proposal"], bytes(event["genome"]).hex()] for event in blind["events"]]),
                  "initial_population": rebuilt["initial_population_sha256"] == arm["blind"]["initial_population_sha256"],
                  "whole_search_ledger": _equal(rebuilt["prefixes"][CAP], arm["blind"]["whole_search_cost"]),
                  "training_best": _equal(event_record(rebuilt["best"]), arm["blind"]["training_best"]),
                  "assessment": _equal(blind["assessment"], arm["assessment"])}
        deployed = {}
        for mode in ("shortest", "fitted", "direct"):
            own = audit_deployment(mode, blind["observations"], tables[task], blind["events"], rebuilt)
            saved = arm["deployed"][mode]
            fields = ("returned", "correct_return", "cap_exhausted_without_return", "proposals",
                      "unique_training_perfect_seen", "requests", "cost")
            local_checks = {field: _equal(own[field], saved[field]) for field in fields}
            checks["deployed_" + mode] = all(local_checks.values())
            if not all(local_checks.values()):
                errors.append({"task": task, "seed": seed, "condition": condition, "mode": mode,
                               "different_fields": [field for field, passed in local_checks.items() if not passed]})
            if own["returned"] is not None:
                genome = tuple(bytes.fromhex(own["returned"]["genome"]))
                if predictions(genome) != tables[task]:
                    raise ValueError("a paid certificate returned an incorrect full program")
            summary = deployed_summaries[condition, mode]
            summary["successes"] += own["correct_return"]
            summary["episodes"] += 1
            summary["work_units"] += own["cost"]["work_units"]
            summary["wall_seconds"] += saved["wall_seconds"]
            summary["failed_certificates"] += own["failed_certificates"]
            summary["fresh_truth_labels"] += own["cost"]["checking"].get("fresh_truth_labels", 0)
            deployed[mode] = {"pass": all(local_checks.values()), "checks": local_checks,
                              "correct_return": own["correct_return"], "proposals": own["proposals"],
                              "returned": own["returned"], "failed_certificates": own["failed_certificates"],
                              "requests": own["requests"], "offered_history": own["offered_history"],
                              "work_units": own["cost"]["work_units"], "cost_components": own["cost"]["components"],
                              "separate_vote_additions": own["cost"]["fit_and_ranking"].get("vote_additions", 0)}
        for mode in ("shortest", "fitted", "always"):
            mode_scores[mode] += blind["assessment"]["scores"][mode]["exact"]
        if not all(checks.values()):
            errors.append({"task": task, "seed": seed, "condition": condition,
                           "different_checks": [key for key, passed in checks.items() if not passed]})
        episodes.append({"task": task, "seed": seed, "condition": condition, "pass": all(checks.values()),
                         "checks": checks, "bank_count": len(blind["events"]), "n_exact_in_pool": blind["assessment"]["n_exact_in_pool"],
                         "blind_scores": blind["assessment"]["scores"], "inferred_symmetry": blind["inference"], "deployed": deployed})
    twins = []
    for seed in SEEDS:
        for condition in ("raw", "reuse"):
            left = prepared["6d18", seed, condition][0]["blind"]
            right = prepared["f46b", seed, condition][0]["blind"]
            twins.append({"seed": seed, "condition": condition,
                          "identical_observations": left["training_observations"] == right["training_observations"],
                          "identical_bank": left["bank_sha256"] == right["bank_sha256"],
                          "identical_inference": left["models"] == right["models"],
                          "identical_blind_choices": left["choices"] == right["choices"],
                          "identical_blind_commitment": left["blind_commitment"] == right["blind_commitment"]})
    if not all(all(value for key, value in twin.items() if key not in ("seed", "condition")) for twin in twins):
        errors.append({"error": "matched tasks differed before any paid verification"})
    summaries = []
    acquisition = primitive_runtime()[0].audit_acquisition()
    if not acquisition["pass"]:
        errors.append({"error": "source acquisition reconstruction failed"})
    acquisition_actor_units = acquisition["semantic_nine_state_work"]["total_gates"]
    for (condition, mode), values in sorted(deployed_summaries.items()):
        successes = values["successes"]
        charged = values["work_units"] + (acquisition_actor_units if condition == "reuse" else 0)
        summaries.append({"condition": condition, "mode": mode, **values,
                          "cost_per_exact_return_including_failures": None if not successes else values["work_units"] / successes,
                          "work_with_source_actor_acquisition_once": charged,
                          "cost_per_return_with_source_actor_acquisition_once": None if not successes else charged / successes,
                          "acquisition_scope": "actor-gate contribution only; historical byte/scoring overhead remains separately unpriced"})
    indexed_episodes = {(row["task"], row["seed"], row["condition"]): row for row in episodes}
    comparisons = []
    for condition in ("raw", "reuse"):
        for left_mode, right_mode in (("fitted", "shortest"), ("fitted", "direct")):
            paired = [(indexed_episodes[task, seed, condition]["deployed"][left_mode],
                       indexed_episodes[task, seed, condition]["deployed"][right_mode])
                      for task, seed in sorted(expected)]
            common = [(left, right) for left, right in paired if left["correct_return"] and right["correct_return"]]
            comparisons.append({"condition": condition, "left": left_mode, "right": right_mode,
                                "same_success_episodes": len(common),
                                "left_work_same_success": sum(left["work_units"] for left, _ in common),
                                "right_work_same_success": sum(right["work_units"] for _, right in common)})
    for mode in ("shortest", "fitted", "direct"):
        common, failures = [], {"raw": [], "reuse": []}
        for task, seed in sorted(expected):
            left = indexed_episodes[task, seed, "raw"]["deployed"][mode]
            right = indexed_episodes[task, seed, "reuse"]["deployed"][mode]
            if left["correct_return"] and right["correct_return"]:
                common.append((left, right))
            for condition, record in (("raw", left), ("reuse", right)):
                if not record["correct_return"]:
                    failures[condition].append({"task": task, "seed": seed})
        comparisons.append({"mode": mode, "left": "raw", "right": "reuse",
                            "same_success_episodes": len(common),
                            "left_work_same_success": sum(left["work_units"] for left, _ in common),
                            "right_work_same_success": sum(right["work_units"] for _, right in common),
                            "failures": failures})
    twin_differences = [point for point in POINTS if tables["6d18"][point_index(point)] != tables["f46b"][point_index(point)]]
    same_twin_observations = all(tables["6d18"][point_index(point)] == tables["f46b"][point_index(point)] for point in TRAIN)
    if not same_twin_observations or set(twin_differences) != {(1, 1, 1), (1, 0, 0)} or not set(twin_differences) <= set(HELD):
        errors.append({"error": "the independent matched-task information counterexample failed"})
    return {"pass": not errors, "errors": errors, "raw_cases": len(rows), "arm_episodes": len(episodes),
            "unique_streams_rebuilt": len(reconstructions), "proposals_rebuilt": CAP * len(reconstructions),
            "all_stream_prefixes_and_ledgers_reconstructed": True,
            "blind_exact_choices_out_of_60": dict(mode_scores), "deployed": summaries,
            "same_success_comparisons": comparisons, "acquisition_cost": acquisition,
            "twin_checks": twins, "episodes": episodes,
            "counterexample": {"tasks": ["6d18", "f46b"], "same_observations": same_twin_observations,
                               "different_only_at": twin_differences,
                               "identification_without_a_new_observation": "impossible on both matched tasks from the same observations"},
            "cost_unit": "Declared Boolean/label/answer-comparison unit; vote additions and host/syntax/RNG work remain separate, with measured all-in deployment time.",
            "primitive_audit_dependency_sha256": hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    raw = args.results.read_bytes()
    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    report = audit_results(rows, progress=lambda value: print(value, file=sys.stderr, flush=True))
    report["raw_sha256"] = hashlib.sha256(raw).hexdigest()
    report["checker_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if args.write:
        path = args.results.parent / "audit.json"
        path.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({"audit": str(path.resolve()), "pass": report["pass"], "errors": report["errors"],
                          "blind_exact_choices_out_of_60": report["blind_exact_choices_out_of_60"],
                          "deployed": report["deployed"]}, indent=2))
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
