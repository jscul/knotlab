#!/usr/bin/env python3
"""Independent exact check of raw-event memory. No producer imports.

Each transition is enumerated from the local triples. Integer matrix powers
count every proposal word. Rational linear equations independently determine
closed-class absorption and fixed-input limits. Observation horizons are fixed;
the neutral limit means a limit of fixed horizons, never a stopping rule.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time


ROOT = Path(__file__).resolve().parents[2]
FAMILY = "SIX-BIT-EVENT-20261111-001-E001_raw_event"
CONTRACT = ROOT / "experiments/SIX-BIT-EVENT-20261111-001" / FAMILY / "contract.json"
DEFAULT_PRODUCER = ROOT / "artifacts/SIX-BIT-EVENT-20261111-001" / FAMILY / "result.json"
CORE = ((0, 1, 2), (0, 4, 5), (3, 1, 5), (3, 4, 2))
HORIZONS = (0, 1, 2, 4, 8, 16, 32, 64, 128)
RAW = tuple(format(i, "03b") for i in range(8))
MIXED = tuple(w for w in RAW if w not in ("000", "111"))
CHANNELS = ((0, 0), (1, 0), (2, 0))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def bit(word, index):
    return (word >> (5 - index)) & 1


def text(word):
    return format(word, "06b")


def hard_legal(word):
    return all(len({bit(word, i) for i in triple}) == 2 for triple in CORE)


STATES = tuple(w for w in range(64) if hard_legal(w))
INDEX = {w: i for i, w in enumerate(STATES)}
CLEAR = tuple(w for w in STATES if bit(w, 0) != bit(w, 3) and bit(w, 4) == 0)
LOADED = tuple(w for w in STATES if bit(w, 0) != bit(w, 3) and bit(w, 4) == 1)
VARIANTS = {"original": CHANNELS,
            **{f"remove_{'uvw'[i]}": tuple(c for c in CHANNELS if c[0] != i) for i in range(3)},
            **{f"flip_{'uvw'[i]}": tuple((j, int(i == j)) for j, _ in CHANNELS) for i in range(3)},
            "uncoupled_raw": ()}


def kernel(raw, one_way, channels):
    """Reject a new local violation; no raw-word equality test is used."""
    raw_values = tuple(map(int, raw))

    def satisfied(word, channel):
        index, sign = channel
        return len({raw_values[index] ^ sign, bit(word, 0), bit(word, 3)}) == 2

    rows = []
    for word in STATES:
        counts = [0] * len(STATES)
        for port in range(6):
            candidate = word ^ (1 << (5 - port))
            permitted = candidate in INDEX and not (one_way and port == 4 and bit(word, 4))
            if permitted:
                permitted = all(not satisfied(word, c) or satisfied(candidate, c) for c in channels)
            counts[INDEX[candidate if permitted else word]] += 1
        require(sum(counts) == 6, "a proposal was lost")
        rows.append(tuple(counts))
    return tuple(rows)


def scc(matrix):
    graph = {i: [j for j, count in enumerate(row) if count and j != i]
             for i, row in enumerate(matrix)}
    number, stack, on_stack, order, low, groups = 0, [], set(), {}, {}, []

    def visit(v):
        nonlocal number
        order[v] = low[v] = number
        number += 1
        stack.append(v)
        on_stack.add(v)
        for w in graph[v]:
            if w not in order:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in on_stack:
                low[v] = min(low[v], order[w])
        if low[v] == order[v]:
            group = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                group.append(w)
                if w == v:
                    break
            groups.append(frozenset(group))

    for v in graph:
        if v not in order:
            visit(v)
    return sorted((g for g in groups if all(j in g for i in g for j in graph[i])),
                  key=lambda g: tuple(sorted(g)))


def solve(a, b):
    """Gauss-Jordan with exact fractions and any number of right-hand sides."""
    n = len(a)
    if not n:
        return []
    width = len(b[0])
    rows = [[Fraction(x) for x in left + right] for left, right in zip(a, b)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if rows[i][col]), None)
        require(pivot is not None, "singular rational system")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        divisor = rows[col][col]
        rows[col] = [value / divisor for value in rows[col]]
        for i in range(n):
            if i != col and rows[i][col]:
                factor = rows[i][col]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[col])]
    return [row[n:n + width] for row in rows]


CLASS_CACHE = {}
POWER_CACHE = {}
METRIC_CACHE = {}


def closed_analysis(matrix):
    if matrix in CLASS_CACHE:
        return CLASS_CACHE[matrix]
    groups = scc(matrix)
    owner = {i: c for c, group in enumerate(groups) for i in group}
    transient = [i for i in range(len(STATES)) if i not in owner]
    a = [[6 * int(i == j) - matrix[i][j] for j in transient] for i in transient]
    b = [[sum(matrix[i][j] for j in group) for group in groups] for i in transient]
    solution = solve(a, b)
    absorption = [[Fraction(int(owner.get(i) == c)) for c in range(len(groups))]
                  for i in range(len(STATES))]
    for i, row in zip(transient, solution):
        absorption[i] = row
    require(all(sum(row) == 1 and all(0 <= v <= 1 for v in row) for row in absorption),
            "invalid closed-class absorption")
    stationary_y = []
    for group in groups:
        ids = sorted(group)
        # A rejected hard-core proposal supplies a self-loop, so no periodic
        # terminal class invalidates the fixed-time limit.
        require(all(matrix[i][i] > 0 for i in ids), "periodic terminal class possible")
        a = [[matrix[j][i] - 6 * int(i == j) for j in ids] for i in ids[:-1]]
        a.append([1] * len(ids))
        b = [[0] for _ in ids[:-1]] + [[1]]
        pi = [row[0] for row in solve(a, b)]
        require(sum(pi) == 1 and all(p >= 0 for p in pi), "invalid stationary law")
        stationary_y.append(sum(p for i, p in zip(ids, pi) if bit(STATES[i], 4)))
    result = {"classes": groups, "absorption": absorption, "stationary_y": stationary_y}
    CLASS_CACHE[matrix] = result
    return result


def metrics(matrix):
    if matrix in METRIC_CACHE:
        return METRIC_CACHE[matrix]
    analysis = closed_analysis(matrix)
    captured = tuple(tuple(6 * int(i == j) for j in range(len(STATES)))
                     if bit(STATES[i], 4) else row for i, row in enumerate(matrix))
    hit = closed_analysis(captured)
    hit_classes = [all(bit(STATES[i], 4) for i in group) for group in hit["classes"]]
    permanent_classes = [all(bit(STATES[i], 4) for i in group) for group in analysis["classes"]]
    result = {
        **analysis,
        "ever": [sum(p for p, yes in zip(row, hit_classes) if yes) for row in hit["absorption"]],
        "limit": [sum(p * weight for p, weight in zip(row, analysis["stationary_y"]))
                  for row in analysis["absorption"]],
        "permanent": [sum(p for p, yes in zip(row, permanent_classes) if yes)
                      for row in analysis["absorption"]],
    }
    METRIC_CACHE[matrix] = result
    return result


def multiply(a, b):
    result = []
    for row in a:
        out = [0] * len(row)
        for k, value in enumerate(row):
            if value:
                for j, other in enumerate(b[k]):
                    if other:
                        out[j] += value * other
        result.append(tuple(out))
    return tuple(result)


def distribution(matrix, initial, horizon):
    if not horizon:
        return tuple(int(i == INDEX[initial]) for i in range(len(STATES)))
    powers = POWER_CACHE.setdefault(matrix, {1: matrix})
    n = 1
    while n * 2 <= horizon:
        if n * 2 not in powers:
            powers[n * 2] = multiply(powers[n], powers[n])
        n *= 2
    row = [int(i == INDEX[initial]) for i in range(len(STATES))]
    remaining, power = horizon, 1
    while remaining:
        if remaining & 1:
            row = [sum(row[i] * powers[power][i][j] for i in range(len(STATES)))
                   for j in range(len(STATES))]
        remaining >>= 1
        power *= 2
    require(sum(row) == 6 ** horizon, "integer path counts omit rejected proposals")
    return tuple(row)


def finite_curves(matrix, neutral, initial, horizons):
    neutral_analysis = metrics(neutral)
    immediate, settled = [], []
    last_classes = None
    for horizon in horizons:
        counts = distribution(matrix, initial, horizon)
        denominator = 6 ** horizon
        immediate.append(Fraction(sum(c for w, c in zip(STATES, counts) if bit(w, 4)), denominator))
        settled.append(sum(Fraction(c, denominator) * p
                           for c, p in zip(counts, neutral_analysis["limit"])))
        last_classes = [sum(Fraction(c, denominator) * row[j]
                            for c, row in zip(counts, neutral_analysis["absorption"]))
                        for j in range(len(neutral_analysis["classes"]))]
    support = sorted(STATES[i] for group, p in zip(neutral_analysis["classes"], last_classes)
                     if p for i in group)
    return {"immediate": immediate, "settled": settled, "last_classes": last_classes,
            "last_support": list(map(text, support))}


def closure(matrix_list, start):
    found, pending = {INDEX[start]}, [INDEX[start]]
    while pending:
        i = pending.pop()
        for matrix in matrix_list:
            for j, count in enumerate(matrix[i]):
                if count and j not in found:
                    found.add(j)
                    pending.append(j)
    return frozenset(found)


def path_count_control(matrix, initial, horizon=4):
    # Direct enumeration of all 6^4 choice words is a distinct computation
    # from matrix powers and includes every ineffective attempt.
    expected = [0] * len(STATES)
    expanded = []
    for row in matrix:
        expanded.append(tuple(j for j, count in enumerate(row) for _ in range(count)))
    for choices in itertools.product(range(6), repeat=horizon):
        current = INDEX[initial]
        for choice in choices:
            current = expanded[current][choice]
        expected[current] += 1
    require(tuple(expected) == distribution(matrix, initial, horizon), "direct proposal path count mismatch")


def summary(horizons):
    require(len(STATES) == 18 and len(CLEAR) == len(LOADED) == 2, "core or prepared start census")
    primary, controls = {}, {}
    for variant, channels in VARIANTS.items():
        laws = {}
        for label, one_way in (("symmetric", False), ("one_way_y", True)):
            kernels = {raw: kernel(raw, one_way, channels) for raw in RAW}
            neutral = kernels["001"]
            rows = {}
            for raw in RAW:
                values = metrics(kernels[raw])
                starts = {}
                for start in CLEAR + LOADED:
                    curves = finite_curves(kernels[raw], neutral, start, horizons)
                    starts[text(start)] = {
                        "ever_y1": str(values["ever"][INDEX[start]]),
                        "limit_y1": str(values["limit"][INDEX[start]]),
                        "eventually_permanent_y1": str(values["permanent"][INDEX[start]]),
                        "y1_immediate": list(map(str, curves["immediate"])),
                        "y1_after_neutral_limit": list(map(str, curves["settled"])),
                    }
                rows[raw] = {"closed_classes": [list(map(lambda i: text(STATES[i]), sorted(group)))
                                                for group in values["classes"]], "starts": starts}
            laws[label] = rows
            if variant == "original":
                require(all(kernels[raw] == neutral for raw in MIXED), "mixed input kernels differ")
                require(all(closure([kernels[w] for w in MIXED], start) == {INDEX[start]}
                            for start in CLEAR + LOADED), "mixed-only background is not frozen")
                if one_way:
                    require(all(not count or not bit(STATES[i], 4) or bit(STATES[j], 4)
                                for raw in RAW for i, row in enumerate(kernels[raw])
                                for j, count in enumerate(row)), "one-way read can be erased")
                    require(all(metrics(kernels[raw])["permanent"][INDEX[start]] == 1
                                for raw in ("000", "111") for start in CLEAR),
                            "sustained equal input does not capture almost surely")
                for start in CLEAR:
                    require(not hard_legal(start ^ (1 << (5 - 4))), "finite miss witness lost")
                    for raw in RAW:
                        require(kernels[raw][INDEX[start]][INDEX[start]] >= 1,
                                "blocked y attempt was not counted")
                path_count_control(kernels["000"], CLEAR[0])
        if variant == "original":
            primary = laws
        controls[variant] = {law: {raw: [rows[raw]["starts"][text(s)]["y1_after_neutral_limit"][-1]
                                            for s in CLEAR] for raw in RAW}
                             for law, rows in laws.items()}
    upper = {str(y): "".join(str(int(len({y, p, q}) == 2))
                            for p, q in itertools.product((0, 1), repeat=2)) for y in (0, 1)}
    disconnected = {str(y): "".join(str(int(any(len({h, p, q}) == 2 for h in (0, 1))))
                                   for p, q in itertools.product((0, 1), repeat=2)) for y in (0, 1)}
    require(upper == {"0": "0111", "1": "1110"} and set(disconnected.values()) == {"1111"},
            "upper causal control")
    return {"core_states": list(map(text, STATES)), "clear": list(map(text, CLEAR)),
            "loaded": list(map(text, LOADED)), "horizons": list(horizons), "primary": primary,
            "control_retained_at_last_horizon": controls,
            "upper": {"matched": upper, "uncoupled": disconnected},
            "mixed_only_false_write_probability": "0",
            "finite_miss_lower_bound": "6^(-T), from T rejected y proposals and a frozen mixed reset",
            "unique_local_kernels": len(METRIC_CACHE),
            "observation": "fixed proposal horizons; neutral limit is a limit of fixed horizons, not acknowledgment"}


def record_path(path):
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def unique_rows(rows, key, label):
    mapped = {row[key]: row for row in rows}
    require(len(mapped) == len(rows), f"{label}: duplicate {key}")
    return mapped


def parse_word(word):
    require(isinstance(word, str) and len(word) == 6 and set(word) <= {"0", "1"},
            "malformed core word")
    value = int(word, 2)
    require(value in INDEX, "reported state violates the hard core")
    return value


def compare_classes(actual, analysis, label):
    expected = {frozenset(text(STATES[i]) for i in group): n
                for n, group in enumerate(analysis["classes"])}
    identities, seen = {}, set()
    for row in actual:
        words = frozenset(row["states"])
        require(len(words) == len(row["states"]) and words in expected,
                f"{label}: wrong closed class")
        index = expected[words]
        require(index not in seen and row["class_id"] not in identities, f"{label}: repeated class")
        seen.add(index)
        identities[row["class_id"]] = index
        require(row["read_values"] == sorted({bit(parse_word(w), 4) for w in words}),
                f"{label}: class read values")
        require(Fraction(row["stationary_y1"]) == analysis["stationary_y"][index],
                f"{label}: stationary class response")
    require(len(seen) == len(expected), f"{label}: missing closed class")
    return identities


def compare_class_probabilities(actual, identities, expected, label):
    reported = {}
    for row in actual:
        require(row["class_id"] in identities, f"{label}: foreign class id")
        index = identities[row["class_id"]]
        require(index not in reported, f"{label}: repeated class probability")
        probability = Fraction(row["probability"])
        require(0 <= probability <= 1, f"{label}: invalid probability")
        reported[index] = probability
    require({i: p for i, p in reported.items() if p} ==
            {i: p for i, p in enumerate(expected) if p}, f"{label}: absorption probabilities")


def compare_upper(actual):
    allowed = [format(i, "03b") for i in range(8) if len(set(format(i, "03b"))) == 2]
    require(actual["allowed_words_ypq"] == allowed, "upper allowed relation")
    rows = unique_rows(actual["by_memory"], "y", "upper")
    require(set(rows) == {0, 1}, "upper memory values")
    for y, row in rows.items():
        wanted = [format(i, "02b") for i in range(4) if len({y, i >> 1, i & 1}) == 2]
        require(row["allowed_queries_pq"] == wanted, "upper conditional queries")
        require(row["initial_pq"] == "01" and row["proposed_q"] == 0, "upper matched query")
        require(row["proposal_accepted"] == bool(y), "upper query response")
        require(row["resulting_pq"] == ("00" if y else "01"), "upper query destination")
    severed = actual["severed"]
    require(severed["allowed_queries_after_forgetting_h"] == ["00", "01", "10", "11"],
            "upper uncoupled relation")
    require(severed["matched_q_proposal_by_h"] == {"0": False, "1": True} and
            severed["memory_y_has_no_incidence"] is True, "upper independent replacement")


def compare_paths(actual):
    cases = set()

    def validate(path, matrix):
        current = parse_word(path["initial"])
        for step in path["steps"]:
            require(step["flip"] in "abcxyz" and len(step["flip"]) == 1, "path flip label")
            port = "abcxyz".index(step["flip"])
            after = parse_word(step["after"])
            require(after == current ^ (1 << (5 - port)), "path does not match stated flip")
            require(matrix[INDEX[current]][INDEX[after]] > 0, "path contains forbidden transition")
            current = after
        require(text(current) == path["last"], "path endpoint")
        return current

    for row in actual:
        raw = row["raw"]
        require(raw in ("000", "111"), "representative event word")
        initial = parse_word(row["capture"]["initial"])
        require(initial in CLEAR and (raw, initial) not in cases, "representative start coverage")
        cases.add((raw, initial))
        captured = validate(row["capture"], kernel(raw, True, CHANNELS))
        require(bit(captured, 4) == 1, "representative path has not captured")
        require(row["common_neutral_settle"]["initial"] == text(captured), "path hidden jump at raw arrival")
        settled = validate(row["common_neutral_settle"], kernel("001", True, CHANNELS))
        require(settled in LOADED, "representative mixed reset is not loaded")
    require(cases == set(itertools.product(("000", "111"), CLEAR)), "missing representative path")


def compare_producer(actual):
    require(actual["contract_sha256"] == hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
            "producer binds a different contract")
    require(actual["core_order"] == "abcxyz" and actual["raw_order"] == "uvw", "port orders")
    require(actual["core_states"] == list(map(text, STATES)), "hard-core enumeration")
    require(actual["horizons"] == list(HORIZONS), "finite observation horizons")
    require(actual["starts"] == {"clear": list(map(text, CLEAR)), "loaded": list(map(text, LOADED))},
            "prepared starts")
    variants = unique_rows(actual["variants"], "name", "variants")
    require(set(variants) == set(VARIANTS), "variant coverage")
    pulse_rows, sustained_rows, probability_entries = 0, 0, 0
    for variant, channels in VARIANTS.items():
        data = variants[variant]
        described = []
        for item in data["couplings"]:
            require(item["core_ports"] == "ax" and item["raw_port"] in "uvw", "coupling incidence")
            require(type(item["negated"]) is bool, "coupling sign type")
            described.append(("uvw".index(item["raw_port"]), int(item["negated"])))
        require(sorted(described) == sorted(channels), f"{variant}: coupling source")
        dynamics = unique_rows(data["dynamics"], "name", variant)
        require(set(dynamics) == {"symmetric", "one_way_y"}, f"{variant}: dynamics coverage")
        for label, one_way in (("symmetric", False), ("one_way_y", True)):
            row = dynamics[label]
            require(row["neutral_word"] == "001", "common background differs")
            require(row["blocked_transition"] == ("y:1->0" if one_way else None), "one-way source label")
            kernels = {raw: kernel(raw, one_way, channels) for raw in RAW}
            neutral = kernels["001"]
            neutral_analysis = metrics(neutral)
            neutral_ids = compare_classes(row["neutral_classes"], neutral_analysis, f"{variant}/{label}/neutral")
            mixed = unique_rows(row["mixed_only"], "initial", f"{variant}/{label}/mixed")
            require(set(mixed) == set(map(text, CLEAR)), "mixed-only start coverage")
            for start in CLEAR:
                reachable = closure([kernels[raw] for raw in MIXED], start)
                wanted = sorted(text(STATES[i]) for i in reachable)
                item = mixed[text(start)]
                require(item["reachable_states"] == wanted, "mixed-only closure")
                require(item["y1_reachable"] == any(bit(STATES[i], 4) for i in reachable),
                        "mixed-only false-write flag")
            loaded_reachable = frozenset().union(*(closure(list(kernels.values()), s) for s in LOADED))
            retention = row["loaded_retention_under_arbitrary_raw_sequences"]
            require(retention["reachable_states"] == sorted(text(STATES[i]) for i in loaded_reachable),
                    "arbitrary-input loaded closure")
            require(retention["y0_reachable"] == any(not bit(STATES[i], 4) for i in loaded_reachable),
                    "arbitrary-input retention flag")
            sustained = unique_rows(row["sustained"], "raw", "sustained")
            require(set(sustained) == set(RAW), "sustained raw-word coverage")
            for raw in RAW:
                calculated = metrics(kernels[raw])
                ids = compare_classes(sustained[raw]["closed_classes"], calculated,
                                      f"{variant}/{label}/{raw}")
                starts = unique_rows(sustained[raw]["starts"], "initial", "sustained starts")
                require(set(starts) == set(map(text, CLEAR + LOADED)), "sustained start coverage")
                for start in CLEAR + LOADED:
                    item = starts[text(start)]
                    require(item["initial_kind"] == ("clear" if start in CLEAR else "loaded"), "start kind")
                    for field, name in (("ever_y1_probability", "ever"), ("limit_y1_probability", "limit"),
                                        ("eventually_permanently_y1_probability", "permanent")):
                        require(Fraction(item[field]) == calculated[name][INDEX[start]],
                                f"{variant}/{label}/{raw}/{text(start)}: {field}")
                        probability_entries += 1
                    compare_class_probabilities(item["terminal_class_probabilities"], ids,
                                                calculated["absorption"][INDEX[start]], "sustained classes")
                    sustained_rows += 1
            pulses = {(item["raw"], item["initial"]): item for item in row["pulses"]}
            require(len(pulses) == len(row["pulses"]) and set(pulses) ==
                    set(itertools.product(RAW, map(text, CLEAR + LOADED))), "pulse-case coverage")
            for raw in RAW:
                for start in CLEAR + LOADED:
                    item = pulses[(raw, text(start))]
                    require(item["initial_kind"] == ("clear" if start in CLEAR else "loaded"), "pulse start kind")
                    wanted = finite_curves(kernels[raw], neutral, start, HORIZONS)
                    require(list(map(Fraction, item["y1_immediate"])) == wanted["immediate"],
                            f"{variant}/{label}/{raw}/{text(start)}: finite pulse response")
                    require(list(map(Fraction, item["y1_after_neutral_limit"])) == wanted["settled"],
                            f"{variant}/{label}/{raw}/{text(start)}: neutral limit response")
                    compare_class_probabilities(item["settled_classes_at_last_horizon"], neutral_ids,
                                                wanted["last_classes"], "finite-pulse settled classes")
                    require(item["settled_state_support_at_last_horizon"] == wanted["last_support"],
                            "finite-pulse settled support")
                    last_counts = distribution(kernels[raw], start, HORIZONS[-1])
                    require(item["pulse_state_support_at_last_horizon"] ==
                            [text(w) for w, count in zip(STATES, last_counts) if count], "finite-pulse support")
                    pulse_rows += 1
                    probability_entries += 2 * len(HORIZONS)
    require(actual["coverage"] == {"variants": 8, "dynamics_per_variant": 2, "raw_words": 8,
                                   "initial_states": 4, "horizons_per_pulse": 9, "pulse_rows": 512},
            "coverage accounting")
    compare_upper(actual["upper_probe"])
    compare_paths(actual["representative_paths"])
    return {"pulse_rows": pulse_rows, "sustained_start_rows": sustained_rows,
            "scalar_probabilities_compared": probability_entries,
            "all_variants_laws_words_starts_and_horizons": True,
            "representative_paths_checked": len(actual["representative_paths"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--producer", type=Path, default=DEFAULT_PRODUCER)
    parser.add_argument("--baseline", action="store_true", help="Independent calculation without producer validation.")
    parser.add_argument("--smoke", action="store_true", help="Only finite horizons through four; not a complete check.")
    args = parser.parse_args()
    require(not args.smoke or args.baseline, "partial smoke requires explicit --baseline")
    if not args.baseline:
        require(args.producer.is_file(), f"producer result required: {args.producer}")
    begun = time.monotonic()
    report = summary(HORIZONS[:4] if args.smoke else HORIZONS)
    report.update({"status": "INDEPENDENT_BASELINE", "verification_scope": "independent_calculation_only",
                   "contract_sha256": hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
                   "producer_comparison": {"status": "not_run", "reason": "explicit baseline mode"},
                   "independence": "separate same-task local enumeration, integer matrix powers, rational absorption"})
    if not args.baseline:
        producer = json.loads(args.producer.read_text())
        checked = compare_producer(producer)
        altered = copy.deepcopy(producer)
        altered["variants"][0]["dynamics"][0]["pulses"][0]["y1_immediate"][1] = "1/6"
        try:
            compare_producer(altered)
        except AssertionError:
            wrong_rejected = True
        else:
            raise AssertionError("wrong finite probability was accepted")
        report.update({"status": "PASS", "verification_scope": "full_frozen_primary_contract",
                       "producer_comparison": {"status": "PASS", "path": record_path(args.producer),
                                               "sha256": hashlib.sha256(args.producer.read_bytes()).hexdigest(),
                                               **checked},
                       "negative_controls": {"altered_finite_probability_rejected": wrong_rejected,
                                             "finite_duration_all_rejected_y_witness": True}})
    if args.smoke:
        report["status"] = "PARTIAL_SMOKE"
        report["verification_scope"] = "partial_finite_horizons"
    report["elapsed_seconds"] = time.monotonic() - begun
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, KeyError, TypeError, ValueError, OSError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, sort_keys=True))
        raise SystemExit(1)
