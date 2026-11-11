#!/usr/bin/env python3
"""Independent SCC and whole-state checks for the six-bit memory protocol.

No producer imports. First-hit command states are absorbing. Uniform proposals
finish almost surely exactly when every reachable bottom SCC is a target.
Writes only its deterministic report to stdout; progress goes to stderr.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys
import time


NAMES = "abcxyz"
TRIPLES = tuple(itertools.combinations(range(6), 3))
TRIPLE_ID = {t: i for i, t in enumerate(TRIPLES)}
ORIGINAL_TEXT = ("abc", "ayz", "xbz", "xyc")
EQUIVALENT_TEXT = ("xyz", "xbc", "ayc", "abz")
ROLES = (0, 3, 1, 4)  # reference a, gate x, sample b, read y
ROOT = Path(__file__).resolve().parents[2]
CONTRACT = (ROOT / "experiments/SIX-BIT-MEMORY-20261111-001/"
            "SIX-BIT-MEMORY-20261111-001-E001_writable_memory/contract.json")
DEFAULT_PRODUCER = (ROOT / "artifacts/SIX-BIT-MEMORY-20261111-001/"
                    "SIX-BIT-MEMORY-20261111-001-E001_writable_memory/result.json")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def bit(word, index):
    return (word >> (5 - index)) & 1


def word_text(word):
    return format(word, "06b")


def rule_ids(strings):
    return tuple(sorted(TRIPLE_ID[tuple(sorted(NAMES.index(c) for c in s))] for s in strings))


ORIGINAL = rule_ids(ORIGINAL_TEXT)
EQUIVALENT = rule_ids(EQUIVALENT_TEXT)


def rule_text(pattern):
    return ["".join(NAMES[i] for i in TRIPLES[t]) for t in pattern]


def strongly_connected(adjacency):
    """Tarjan decomposition, independent of producer reachability."""
    serial, stack, on_stack, index, low, groups = 0, [], set(), {}, {}, []

    def visit(v):
        nonlocal serial
        index[v] = low[v] = serial
        serial += 1
        stack.append(v)
        on_stack.add(v)
        for w in adjacency[v]:
            if w not in index:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in on_stack:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            group = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                group.append(w)
                if w == v:
                    break
            groups.append(frozenset(group))

    for v in adjacency:
        if v not in index:
            visit(v)
    return groups


class Base:
    def __init__(self, pattern):
        self.pattern = tuple(pattern)
        self.states = frozenset(w for w in range(64) if all(
            len({bit(w, i) for i in TRIPLES[t]}) == 2 for t in pattern))
        self.moves = {w: tuple((i, w ^ (1 << (5 - i))) for i in range(6)
                               if w ^ (1 << (5 - i)) in self.states)
                      for w in self.states}
        self.command_cache = {}
        self.hold_cache = {}
        self.write_cache = {}

    def first_hits(self, commands):
        key = tuple(sorted(commands.items()))
        if key in self.command_cache:
            return self.command_cache[key]
        targets = {w for w in self.states if all(bit(w, i) == v for i, v in key)}
        graph = {w: (() if w in targets else tuple(v for i, v in self.moves[w]
                    if i not in commands or bit(w, i) != commands[i])) for w in self.states}
        groups = strongly_connected(graph)
        owner = {w: k for k, group in enumerate(groups) for w in group}
        children = [{owner[v] for w in group for v in graph[w] if owner[v] != k}
                    for k, group in enumerate(groups)]
        memo = {}

        def outcome(k):
            if k in memo:
                return memo[k]
            if groups[k] <= targets:
                answer = (True, groups[k])
            elif not children[k]:
                answer = (False, frozenset())
            else:
                downstream = [outcome(j) for j in children[k]]
                answer = (all(ok for ok, _ in downstream),
                          frozenset().union(*(ends for _, ends in downstream)))
            memo[k] = answer
            return answer

        result = {w: outcome(owner[w]) for w in self.states}
        self.command_cache[key] = result
        return result

    def holds(self, cue):
        key = tuple(sorted(cue.items()))
        if key not in self.hold_cache:
            states = {w for w in self.states if all(bit(w, i) == v for i, v in key)}
            graph = {w: tuple(v for _, v in self.moves[w] if v in states) for w in states}
            groups = strongly_connected(graph)
            self.hold_cache[key] = (groups, {w: g for g in groups for w in g})
        return self.hold_cache[key]

    def write(self, reference, gate, sample, starts=None):
        key = (reference, gate, sample)
        if starts is None and key in self.write_cache:
            return self.write_cache[key]
        neutral = {w for w in self.states if bit(w, reference) == 0 and bit(w, gate) == 1}
        answer = []
        for value in (0, 1):
            current = set(neutral if starts is None else starts)
            good, phases = bool(current), []
            for commands in ({reference: 0, gate: 0},
                             {reference: 0, gate: 0, sample: value},
                             {reference: 0, gate: 1, sample: value}):
                first = self.first_hits(commands)
                bad = sorted(w for w in current if not first[w][0])
                ends = set().union(*(first[w][1] for w in current)) if current else set()
                phases.append({"commands": {NAMES[i]: v for i, v in commands.items()},
                               "almost_sure": not bad and bool(current),
                               "closed_failure_starts": list(map(word_text, bad)),
                               "first_hit_states": list(map(word_text, sorted(ends)))})
                good = good and not bad and bool(ends)
                current = ends
                if not good:
                    break
            owner = self.holds({reference: 0, gate: 1})[1]
            held = frozenset().union(*(owner[w] for w in current)) if good else frozenset()
            answer.append({"sample": value, "almost_sure": good, "endpoints": frozenset(current),
                           "held": held, "phases": phases})
        if starts is None:
            self.write_cache[key] = answer
        return answer

    def successful_roles(self, prefixes=None):
        answer = []
        for reference, gate, sample in (prefixes or itertools.permutations(range(6), 3)):
            runs = self.write(reference, gate, sample)
            if not all(run["almost_sure"] for run in runs):
                continue
            for read in set(range(6)) - {reference, gate, sample}:
                values = [{bit(w, read) for w in run["held"]} for run in runs]
                for inverted in (False, True):
                    if values == [{int(inverted)}, {1 - int(inverted)}]:
                        answer.append({"ports": "".join(NAMES[i] for i in
                                                          (reference, gate, sample, read)),
                                       "inverted": inverted})
        return sorted(answer, key=lambda r: (r["ports"], r["inverted"]))


def role_set(rows):
    return {(row["ports"], bool(row["inverted"])) for row in rows}


def base_report(base):
    return {"rules": rule_text(base.pattern), "legal_states": list(map(word_text, sorted(base.states))),
            "successful_roles": base.successful_roles()}


def primary_report(base):
    ref, gate, sample, read = ROLES
    groups, _ = base.holds({ref: 0, gate: 1})
    runs = base.write(ref, gate, sample)
    require(all(r["almost_sure"] for r in runs), "primary write phases do not complete")
    require([{bit(w, read) for w in r["held"]} for r in runs] == [{0}, {1}],
            "primary read does not hold both sample values")
    by_start = {}
    for start in sorted(set().union(*groups)):
        values = base.write(ref, gate, sample, {start})
        by_start[word_text(start)] = [{"sample": r["sample"], "almost_sure": r["almost_sure"],
                                      "endpoints": list(map(word_text, sorted(r["endpoints"]))),
                                      "phases": r["phases"]} for r in values]
    attached, uncoupled = {}, {}
    for run in runs:
        allowed = {(p, q) for w in run["held"] for p, q in itertools.product((0, 1), repeat=2)
                   if len({bit(w, read), p, q}) == 2}
        detached = {(p, q) for p, q in itertools.product((0, 1), repeat=2)
                    if any(len({h, p, q}) == 2 for h in (0, 1))}
        attached[str(run["sample"])] = "".join(str(int(pq in allowed))
                                             for pq in itertools.product((0, 1), repeat=2))
        uncoupled[str(run["sample"])] = "".join(str(int(pq in detached))
                                              for pq in itertools.product((0, 1), repeat=2))
    require(attached == {"0": "0111", "1": "1110"}, "attached truth table")
    require(uncoupled == {"0": "1111", "1": "1111"}, "uncoupled truth table")
    pulse = {}
    for start in sorted(set().union(*groups)):
        opened = base.first_hits({ref: 0, gate: 0})[start]
        closed = base.first_hits({ref: 0, gate: 1})
        ends = set().union(*(closed[w][1] for w in opened[1]))
        pulse[word_text(start)] = sorted({bit(w, read) for w in ends})
    require(all(values == [0, 1] for values in pulse.values()), "free-sample pulse unexpectedly writes")
    return {"fixed_roles": "axby", "neutral_components": [list(map(word_text, sorted(g))) for g in groups],
            "by_neutral_start": by_start, "attached_query_00_01_10_11": attached,
            "uncoupled_query_00_01_10_11": uncoupled, "sample_free_pulse_readouts": pulse,
            "released_component_sizes": sorted(map(len, base.holds({})[0])),
            "reference_only_component_sizes": sorted(map(len, base.holds({ref: 0})[0])),
            "gate_only_component_sizes": sorted(map(len, base.holds({gate: 1})[0]))}


def content_report():
    original, deleted = Base(ORIGINAL), Base(tuple(i for i in ORIGINAL if i != rule_ids(("abc",))[0]))
    cue = lambda w: tuple(bit(w, i) for i in (3, 4, 5))
    preparations = [sorted(w for w in b.states if cue(w) == (0, 0, 1)) for b in (original, deleted)]
    probabilities = []
    for states in preparations:
        hits = 0
        for w in states:
            for i in range(6):
                v = w ^ (1 << (5 - i))
                if v not in deleted.states:
                    v = w
                hits += len(set(cue(v))) == 1
        probabilities.append(Fraction(hits, 6 * len(states)))
    require(probabilities == [Fraction(0), Fraction(1, 24)], "experienced response mismatch")
    free_responses = []
    for w in range(64):
        if cue(w) != (0, 0, 1):
            continue
        frequencies = {}
        for i in range(6):
            label = "".join(map(str, cue(w ^ (1 << (5 - i)))))
            frequencies[label] = frequencies.get(label, 0) + 1
        free_responses.append(frequencies)
    require(all(r == free_responses[0] for r in free_responses), "hidden-dependent free response")
    overlap = len(set(preparations[0]) & set(preparations[1]))
    require(overlap == 3, "preparations do not overlap")
    union = set().union(*preparations)
    laws = [{w: Fraction(int(w in p), len(p)) for w in union} for p in preparations]
    variation = sum(abs(laws[0][w] - laws[1][w]) for w in union) / 2
    accuracy = sum(max(laws[0][w], laws[1][w]) for w in union) / 2
    return {"cue": "xyz=001", "common_evaluation": "abc deleted",
            "preparations": [list(map(word_text, p)) for p in preparations],
            "next_all_equal_probabilities": list(map(str, probabilities)),
            "complete_preparation_overlap": overlap, "conditional_total_variation": str(variation),
            "best_equal_prior_classification_accuracy": str(accuracy),
            "free_next_visible_proposal_counts_out_of_six": free_responses[0],
            "free_hidden_preparations_checked": len(free_responses)}


def census(limit):
    patterns = tuple(itertools.combinations(range(20), 4))
    fixed = {}
    seeds = {w: {"final_patterns": math.comb(20 - math.comb(w.bit_count(), 3)
                                           - math.comb(6 - w.bit_count(), 3), 4),
                 "same_reading": 0, "inverted_reading": 0, "total_seen": 0}
             for w in range(64) if bit(w, 0) == 0 and bit(w, 3) == 1}
    fixed_signs = {}
    start = time.monotonic()
    for k, pattern in enumerate(patterns[:limit], 1):
        base = Base(pattern)
        matching = [r for r in base.successful_roles([ROLES[:3]]) if r["ports"] == "axby"]
        require(len(matching) <= 1, "both reading conventions cannot hold for one pattern")
        fixed[pattern] = bool(matching)
        fixed_signs[pattern] = matching[0]["inverted"] if matching else None
        for w in base.states & seeds.keys():
            seeds[w]["total_seen"] += 1
            if matching:
                label = "inverted_reading" if matching[0]["inverted"] else "same_reading"
                seeds[w][label] += 1
        if k % 1000 == 0:
            print(f"independent fixed-role census {k}/{limit}", file=sys.stderr, flush=True)
    result = {"labeled_pattern_count": limit, "fixed_roles": "axby",
              "passing_fixed_roles": sum(fixed.values()),
              "fixed_role_rows_sha256": hashlib.sha256(bytes(fixed[p] for p in patterns[:limit])).hexdigest(),
              "fixed_role_seconds": time.monotonic() - start}
    if limit != len(patterns):
        result["partial_smoke_only"] = True
        return result, None
    for w, data in seeds.items():
        require(data["total_seen"] == data["final_patterns"], "assembly seed weighting misses patterns")
        mixed_count = 20 - math.comb(w.bit_count(), 3) - math.comb(6 - w.bit_count(), 3)
        require(Fraction(math.factorial(4), math.perm(mixed_count, 4)) ==
                Fraction(1, data["final_patterns"]), "sequential and subset sampling differ")
    same_probability = sum(Fraction(d["same_reading"], 16 * d["final_patterns"]) for d in seeds.values())
    inverse_probability = sum(Fraction(d["inverted_reading"], 16 * d["final_patterns"]) for d in seeds.values())
    assembly = {"fixed_neutral": {"a": 0, "x": 1}, "roles": "axby",
                "labeled_same_reading": sum(v is False for v in fixed_signs.values()),
                "labeled_inverted_reading": sum(v is True for v in fixed_signs.values()),
                "probability_same_reading": str(same_probability),
                "probability_inverted_reading": str(inverse_probability),
                "probability_either_reading": str(same_probability + inverse_probability),
                "seeds": {word_text(w): {k: v for k, v in d.items() if k != "total_seen"}
                          for w, d in seeds.items()}}
    result["post_census_assembly_calculation"] = assembly
    permutations = tuple(itertools.permutations(range(6)))
    actions = [tuple(TRIPLE_ID[tuple(sorted(p[i] for i in t))] for t in TRIPLES)
               for p in permutations]
    unseen, rows, lookup, internal = set(patterns), [], {}, []
    while unseen:
        representative = min(unseen)
        orbit = {tuple(sorted(action[i] for i in representative)) for action in actions}
        unseen.difference_update(orbit)
        roles = Base(representative).successful_roles()
        numerator = len(orbit) * len(roles)
        require(numerator % 360 == 0, "nonintegral fixed-role orbit weight")
        direct = sum(fixed[p] for p in orbit)
        require(direct == numerator // 360, "direct fixed census disagrees with orbit weighting")
        row = {"rules": rule_text(representative), "orbit_size": len(orbit),
               "successful_role_count": len(roles), "passing_fixed_roles": direct}
        index = len(rows)
        rows.append(row)
        internal.append((representative, orbit, roles))
        lookup.update({p: index for p in orbit})
        if len(rows) % 10 == 0:
            print(f"independent role-complete orbits {len(rows)}, {len(unseen)} patterns left",
                  file=sys.stderr, flush=True)
    result.update({"orbit_count": len(rows),
                   "passing_any_roles": sum(r["orbit_size"] for r in rows if r["successful_role_count"]),
                   "orbits": rows, "total_seconds": time.monotonic() - start})
    return result, (lookup, internal, permutations, actions)


def compare_base(actual, expected, label):
    require(rule_ids(actual["rules"]) == rule_ids(expected["rules"]), f"{label}: wrong rules")
    require(set(actual["legal_states"]) == set(expected["legal_states"]), f"{label}: whole states")
    require(role_set(actual["successful_roles"]) == role_set(expected["successful_roles"]),
            f"{label}: successful write/hold roles")


def compare_producer(actual, expected, context):
    for name in ("original", "complementary", "free"):
        compare_base(actual[name], expected[name], name)
    require(len(actual["deletions"]) == 4, "deletion count")
    remaining = {rule_ids(row["rules"]): row for row in expected["deletions"]}
    for row in actual["deletions"]:
        pattern = rule_ids(row["rules"])
        require(pattern in remaining, "unexpected or duplicate deletion")
        compare_base(row, remaining.pop(pattern), "deletion")
    census_actual, census_expected = actual["census"], expected["census"]
    for field in ("labeled_pattern_count", "orbit_count", "passing_any_roles",
                  "passing_fixed_roles", "fixed_roles"):
        require(census_actual[field] == census_expected[field], f"census.{field}")
    lookup, internal, permutations, actions = context
    seen = set()
    for row in census_actual["orbits"]:
        pattern = rule_ids(row["rules"])
        index = lookup[pattern]
        require(index not in seen, "duplicate producer orbit")
        seen.add(index)
        wanted = census_expected["orbits"][index]
        for field in ("orbit_size", "successful_role_count", "passing_fixed_roles"):
            require(row[field] == wanted[field], f"orbit {pattern}: {field}")
        representative, _, roles = internal[index]
        permutation = next(p for p, action in zip(permutations, actions)
                           if tuple(sorted(action[i] for i in representative)) == pattern)
        transported = {("".join(NAMES[permutation[NAMES.index(c)]] for c in r["ports"]), r["inverted"])
                       for r in roles}
        require(role_set(row["successful_roles"]) == transported, f"orbit {pattern}: transported roles")
    require(len(seen) == census_expected["orbit_count"], "missing producer orbit")


def record_path(path):
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def probability_map(actual):
    require(isinstance(actual, dict), "probability table must be a mapping")
    converted = {key: Fraction(value) for key, value in actual.items()}
    require(all(len(key) == 3 and set(key) <= {"0", "1"} for key in converted),
            "invalid visible word in probability table")
    require(all(value >= 0 for value in converted.values()) and sum(converted.values()) == 1,
            "invalid probability normalization")
    return {key: value for key, value in converted.items() if value}


def visible_distribution(states, evaluation=None):
    counts = {}
    for w in states:
        for i in range(6):
            neighbor = w ^ (1 << (5 - i))
            if evaluation is not None and neighbor not in evaluation.states:
                neighbor = w
            label = word_text(neighbor)[3:]
            counts[label] = counts.get(label, 0) + 1
    return {key: Fraction(value, 6 * len(states)) for key, value in counts.items()}


def compare_experience(actual, content):
    original = Base(ORIGINAL)
    removed = Base(tuple(i for i in ORIGINAL if i != rule_ids(("abc",))[0]))
    models = {"four_knots": original, "without_abc": removed}
    require(actual["ports"] == NAMES, "experience ports")
    require(actual["preparation_sizes"] == [len(original.states), len(removed.states)],
            "experience preparation sizes")
    require(actual["shared_full_states"] == len(original.states & removed.states),
            "experience shared full states")
    cues = sorted({word_text(w)[3:] for w in original.states})
    require(set(actual["matched_visible_cues"]) == set(cues), "experience cue coverage")
    for cue in cues:
        require(set(actual["matched_visible_cues"][cue]) == set(models), "experience model coverage")
        for model, base in models.items():
            states = sorted(w for w in base.states if word_text(w)[3:] == cue)
            row = actual["matched_visible_cues"][cue][model]
            require(row["equiprobable_abc"] == [word_text(w)[:3] for w in states],
                    f"experience {cue}/{model}: hidden preparations")
            require(probability_map(row["next_xyz_with_abc_removed"]) ==
                    visible_distribution(states, removed),
                    f"experience {cue}/{model}: common constrained response")
            require(probability_map(row["next_xyz_free"]) == visible_distribution(states),
                    f"experience {cue}/{model}: free response")
    all_cues = [format(i, "03b") for i in range(8)]
    require(set(actual["free_visible_kernel_for_every_hidden_state"]) == set(all_cues),
            "experience free kernel cue coverage")
    for cue in all_cues:
        rows = [visible_distribution([w]) for w in range(64) if word_text(w)[3:] == cue]
        require(all(row == rows[0] for row in rows), "free kernel depends on hidden state")
        require(probability_map(actual["free_visible_kernel_for_every_hidden_state"][cue]) == rows[0],
                f"experience {cue}: free kernel")
    probabilities = []
    for model in models:
        row = probability_map(actual["matched_visible_cues"]["001"][model]["next_xyz_with_abc_removed"])
        probabilities.append(str(row.get("000", Fraction(0)) + row.get("111", Fraction(0))))
    require(probabilities == content["next_all_equal_probabilities"], "experience 001 content response")

    histories = actual["complete_histories"]
    common = histories["common_start_and_end"]
    require(isinstance(common, str) and len(common) == 6 and set(common) <= {"0", "1"},
            "experience common state must be a six-bit word")
    lengths, visible_orders, coverage = [], [], {}
    for model, base in models.items():
        words = histories[model]
        require(isinstance(words, list) and bool(words), f"experience {model}: missing history")
        require(all(isinstance(w, str) and len(w) == 6 and set(w) <= {"0", "1"} for w in words),
                f"experience {model}: malformed history word")
        require(words[0] == words[-1] == common, f"experience {model}: not closed at common full state")
        states = [int(w, 2) for w in words]
        require(all(w in base.states for w in states), f"experience {model}: illegal history state")
        require(all((left ^ right).bit_count() == 1 for left, right in zip(states, states[1:])),
                f"experience {model}: history step is not one legal flip")
        require(set(states) == base.states, f"experience {model}: history does not visit every state")
        lengths.append(len(states) - 1)
        visible_orders.append(list(dict.fromkeys(word[3:] for word in words)))
        coverage[model] = len(set(states))
    require(lengths[0] == lengths[1] == histories["moves_each"], "experience history lengths differ")
    require(histories["visible_words_in_order_of_first_visit"] == visible_orders,
            "experience visible first visits")
    return {"status": "PASS", "stationary_cues_checked": len(cues),
            "free_hidden_preparations_checked": 64,
            "closed_history_moves_each": lengths[0], "common_full_start_and_end": common,
            "history_state_coverage": coverage, "same_present_six_bits_after_complete_experience": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--producer", type=Path, default=DEFAULT_PRODUCER)
    parser.add_argument("--census-limit", type=int, default=4845,
                        help="Smaller values are timing smoke checks only.")
    args = parser.parse_args()
    require(1 <= args.census_limit <= 4845, "census limit outside frozen range")
    if args.census_limit == 4845:
        require(args.producer.is_file(), f"full comparison requires producer result: {args.producer}")
    started = time.monotonic()
    original = Base(ORIGINAL)
    report = {"status": "PASS", "independence": "separate same-task SCC/whole-state implementation",
              "contract_sha256": hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
              "original": base_report(original), "complementary": base_report(Base(EQUIVALENT)),
              "deletions": [base_report(Base(tuple(t for t in ORIGINAL if t != removed)))
                            for removed in ORIGINAL], "free": base_report(Base(()))}
    require(not report["free"]["successful_roles"], "negative free-base control unexpectedly stores")
    report["primary"] = primary_report(original)
    report["content"] = content_report()
    report["census"], context = census(args.census_limit)
    report["negative_controls"] = {"free_base_has_no_writable_roles": True,
                                   "sample_free_pulse_cannot_choose_readout": True,
                                   "uncoupled_probe_cannot_read_memory": True}
    if args.producer.exists() and context is not None:
        producer = json.loads(args.producer.read_text())
        compare_producer(producer, report, context)
        wrong = copy.deepcopy(producer)
        wrong["census"]["passing_fixed_roles"] += 1
        try:
            compare_producer(wrong, report, context)
        except AssertionError:
            report["negative_controls"]["altered_producer_result_rejected"] = True
        else:
            raise AssertionError("altered producer result was accepted")
        report["producer_comparison"] = {"status": "PASS", "path": record_path(args.producer),
                                         "sha256": hashlib.sha256(args.producer.read_bytes()).hexdigest()}
        missing = []
        assembly_path = args.producer.with_name("assembly.json")
        if assembly_path.is_file():
            assembly_actual = json.loads(assembly_path.read_text())
            assembly_expected = report["census"]["post_census_assembly_calculation"]
            for field, wanted in assembly_expected.items():
                require(assembly_actual[field] == wanted, f"assembly.{field}")
            report["assembly_comparison"] = {
                "status": "PASS", "stage": "post-census added calculation",
                "path": record_path(assembly_path),
                "sha256": hashlib.sha256(assembly_path.read_bytes()).hexdigest(),
                "sequential_and_subset_sampling_agree": True,
            }
        else:
            missing.append("assembly.json")
            report["assembly_comparison"] = {"status": "not_run", "reason": "selected producer sibling absent",
                                              "path": record_path(assembly_path)}
        experience_path = args.producer.with_name("experience.json")
        if experience_path.is_file():
            experience = json.loads(experience_path.read_text())
            report["experience_comparison"] = compare_experience(experience, report["content"])
            report["experience_comparison"].update({
                "path": record_path(experience_path),
                "sha256": hashlib.sha256(experience_path.read_bytes()).hexdigest(),
            })
            for mutation in ("illegal_history", "wrong_stationary_response"):
                altered = copy.deepcopy(experience)
                if mutation == "illegal_history":
                    altered["complete_histories"]["four_knots"][1] = "000000"
                else:
                    changed = altered["matched_visible_cues"]["001"]["four_knots"]["next_xyz_with_abc_removed"]
                    changed["000"] = "1/24"
                    changed["001"] = str(Fraction(changed["001"]) - Fraction(1, 24))
                try:
                    compare_experience(altered, report["content"])
                except AssertionError:
                    report["negative_controls"][f"altered_experience_{mutation}_rejected"] = True
                else:
                    raise AssertionError(f"altered experience {mutation} was accepted")
        else:
            missing.append("experience.json")
            report["experience_comparison"] = {"status": "not_run", "reason": "selected producer sibling absent",
                                                "path": record_path(experience_path)}
        report["verification_scope"] = "baseline_only" if missing else "comprehensive"
        report["untested_siblings"] = missing
        report["status"] = "BASELINE_PASS" if missing else "PASS"
    else:
        report["status"] = "PARTIAL_SMOKE_PASS"
        report["verification_scope"] = "partial_timing_smoke"
        report["producer_comparison"] = {"status": "not_run", "reason": "clearly marked partial timing smoke"}
    report["elapsed_seconds"] = time.monotonic() - started
    report["limits"] = ["External cues, their order and first-hit completion sensing are supplied.",
                         "Probability-one completion does not exclude indefinitely stalling proposal schedules.",
                         "The census ranges over supplied patterns; flips never assemble or change incidences.",
                         "Storage and a weak occupancy effect are distinct from learning the hidden rule."]
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, KeyError, TypeError, ValueError, OSError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, sort_keys=True))
        raise SystemExit(1)
